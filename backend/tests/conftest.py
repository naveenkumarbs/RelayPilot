import pytest 
from fastapi.testclient import TestClient 
from sqlalchemy import create_engine, event 
from sqlalchemy.engine import URL 
from sqlalchemy.orm import sessionmaker 

TEST_PASSWORD = "Synthetic-test-password-only!"

@pytest.fixture(autouse=True)
def test_settings(monkeypatch, tmp_path):
    # Override local configuration before importing the application.
    monkeypatch.setenv("RELAYPILOT_ENVIRONMENT", "test")
    monkeypatch.setenv(
        "RELAYPILOT_JWT_SECRET_KEY",
        "test-only-signing-secret-not-for-real-deployments",
    )
    monkeypatch.setenv("REPAYPILOT_JWT_ISSUER", "relaypilot-test")
    monkeypatch.setenv("RELAYPILOT_JWT_AUDIENCE", "relaypilot-test-api")
    monkeypatch.setenv(
        "RELAYPILOT_DATABASE_PATH",
        str(tmp_path/"application-test.db"),
    )

    from app.core.config import get_settings

    get_settings.cache_clear()

    yield 

    get_settings.cache_clear()

@pytest.fixture 
def session_factory(test_settings, tmp_path):
    from app.core.security import hash_password
    from app.db.base import Base 
    from app.models import Tenant, TenantMembership, User 

    test_engine = create_engine(
        URL.create(
            "sqlite+pysqlite",
            database=str(tmp_path/"test.db"),
        ),
        connect_args={"check_same_thread": False},
    )

    @event.listens_for(test_engine, "connect")
    def enable_foreign_keys(connection, connection_record):
        cursor = connection.cursor()
        try:
            cursor.execute("PRAGMA foreign_keys=ON")
        finally:
            cursor.close()

    factory = sessionmaker(bind=test_engine, autoflush=False)

    # Test databases are rebuilt from models from each test.
    Base.metadata.create_all(test_engine)

    try:
        with factory.begin() as session:
            for slug in ("acme-services", "brightdesk-solutions"):
                tenant = Tenant(name=slug, slug=slug)
                user = User(
                    email=f"admin@{slug}.example",
                    display_name=f"{slug} admin",
                    password_hash=hash_password(TEST_PASSWORD),
                )

                session.add_all([tenant, user])
                session.flush()

                session.add(
                    TenantMembership(
                        tenant_id=tenant.id,
                        user_id=user.id, 
                        role="admin",
                    )
                )
        yield factory
    finally:
        test_engine.dispose()

@pytest.fixture 
def client(session_factory):
    from app.db.session import get_db
    from app.main import app 

    def override_get_db():
        with session_factory() as session:
            yield session 

    from sqlalchemy import select 

    from app.core.security import verify_password 
    from app.models import User 

    with session_factory() as session:
        seeded_user = session.scalar(
            select(User).where(User.email == "admin@acme-services.example")
        )
        
        assert seeded_user is not None, "Test account was not seeded"
        assert seeded_user.is_active, "Test account is inactive"
        assert verify_password(
            TEST_PASSWORD,
            seeded_user.password_hash,
        ), "Seeded password does not match TEST_PASSWORD"

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as test_client:
            yield test_client 
    finally:
        app.dependency_overrides.pop(get_db, None)

@pytest.fixture 
def login_headers(client):
    def login(tenant_slug):
        response = client.post(
            "/auth/login",
            json={
                "email": f"admin@{tenant_slug}.example",
                "password": TEST_PASSWORD,
            },
        )

        assert response.status_code == 200

        token = response.json()["access_token"]

        return {"Authorization": f"Bearer {token}"}

    return login 


