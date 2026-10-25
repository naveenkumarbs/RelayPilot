import logging

from sqlalchemy import select 

from app.core.config import get_settings
from app.core.logging_config import configure_logging
from app.db.session import SessionLocal, engine
from app.models import Tenant

logger = logging.getLogger("relaypilot.seed")

DEMO_TENANTS = (
    {"name": "Acme Services", "slug": "acme-services"},
    {"name": "BrightDesk Solutions", "slug": "brightdesk-solutions"},
)

def seed_demo_tenants() -> None: 
    settings = get_settings()

    if settings.environment != "development":
        raise RuntimeError("Demo tenant seeding is allowed only in development.")

    created_count = 0
    existing_count = 0

    with SessionLocal.begin() as session:
        for tenant_data in DEMO_TENANTS:
            existing_tenant = session.scalar(select(Tenant).where(Tenant.slug == tenant_data["slug"]))
            if existing_tenant is not None:
                existing_count += 1
                continue
            session.add(Tenant(**tenant_data))
            created_count += 1

    logger.info(
        "event=demo_tenants_seeded created_count=%s existing_count=%s",
        created_count, 
        existing_count,
    )

def main() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)

    try:
        seed_demo_tenants()
    except Exception:
        logger.exception("event=demo_tenant_seed_failed")
        raise 
    finally:
        engine.dispose()

if __name__ == "__main__":
    main() 
    
    