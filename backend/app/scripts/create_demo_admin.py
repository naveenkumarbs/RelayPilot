import logging
from getpass import getpass 

from sqlalchemy import select 

from app.core.config import get_settings
from app.core.logging_config import configure_logging
from app.core.security import hash_password
from app.db.session import SessionLocal, engine
from app.models import Tenant, TenantMembership, User 

logger = logging.getLogger("relaypilot.seed")

def create_demo_admin() -> None: 
    settings = get_settings()

    if settings.environment != "development":
        raise ValueError("Demo account creation is allowed only in development.")

    tenant_slug = input("Tenant slug: ").strip().lower()
    email = input("Admin email: ").strip().lower() 
    display_name = input("Display name: ").strip() 

    # Basic checks for this development script 
    # API input validation will be introduced separately
    if (not email or email.count("@") != 1 or any(character.isspace() for character in email) or len(email) > 254):
        raise ValueError("Enter a valid development email address.")

    if not display_name or len(display_name) > 150:
        raise ValueError("Display name must contain 1-150 characters.")

    # Validate the target before prompting for a password.
    with SessionLocal() as session:
        tenant = session.scalar(
            select(Tenant).where(Tenant.slug == tenant_slug)
        )

        if tenant is None or not tenant.is_active:
            raise ValueError("Tenant does not exist or is inactive.")

        existing_user = session.scalar(
            select(User).where(User.email == email)
        )

        if existing_user is not None:
            logger.info("event=demo_admin_creation_skipped reason=user_exists")
            print("This login already exists. No changes made. This script does not grant new memberships or reset passwords for existing users.")
            return 

        tenant_id = tenant.id 

    password = getpass("Password (15-128 characters): ")
    confirmation = getpass("Confirm password: ")

    if password != confirmation:
        raise ValueError("Passwords do not match.")
    
    if not 15 <= len(password) <=128:
        raise ValueError("Password must contain 15-128 characters.")

    stored_hash = hash_password(password)

    with SessionLocal.begin() as session:
        # Recheck the tenant inside the write transaction.
        tenant = session.get(Tenant, tenant_id)

        if tenant is None or not tenant.is_active:
            raise ValueError("Tenant is no longer available.")

        user = User(
            email=email,
            display_name=display_name,
            password_hash=stored_hash
        )

        session.add(user)
        session.flush()

        membership = TenantMembership(
            tenant_id=tenant.id,
            user_id=user.id,
            role="admin",
        )

        session.add(membership)

    logger.info("event=demo_admin_created")
    print("Development admin and tenant membership created.")

def main() -> None: 
    settings = get_settings()
    configure_logging(settings.log_level)

    try:
        create_demo_admin()
    except ValueError as exc:
        logger.warning("event=demo_admin_creation_rejected")
        print(f"Account creation rejected: {exc}")
        raise SystemExit(1) from None 
    except Exception:
        # Avoid logging exception details that might contain account data.
        logger.error("event=demo_admin_creation_failed")
        print("Account creation failed. Check database setup and migrations.")
        raise SystemExit(1) from None 
    finally:
        engine.dispose()

if __name__ == "__main__":
    main()
    