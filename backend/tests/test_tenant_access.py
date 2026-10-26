import pytest 
from sqlalchemy import select 

@pytest.mark.parametrize(
    "caller,target,expected_status",
    [
        ("acme-services", "acme-services", 200),
        ("acme-services", "brightdesk-solutions", 403),    
        ("brightdesk-solutions", "brightdesk-solutions", 200),
        ("brightdesk-solutions", "acme-services", 403),
        ("acme-services", "unknown-tenant", 403),
    ],
)
def test_tenant_access(client, login_headers, caller, target, expected_status):
    response = client.get(
        f"/tenants/{target}/me",
        headers=login_headers(caller),
    )

    assert response.status_code == expected_status 

    if expected_status == 200:
        body = response.json()
        assert body["tenant_slug"] == target
        assert body["role"] == "admin"
    else:
        assert response.json() == {"detail": "Tenant access denied"}

def test_missing_token_is_rejected(client):
    response = client.get("/tenants/acme-services/me")
    assert response.status_code == 401 

@pytest.mark.parametrize(
    "disabled_entity,expected_status",
    [
        ("user", 401),
        ("tenant", 403),
        ("membership", 403),
    ],
)
def test_disabled_access_is_rejected(client, login_headers, session_factory, disabled_entity, expected_status):
    from app.models import Tenant, TenantMembership, User 

    # Issue a valid token before disabling access. 
    headers = login_headers("acme-services")

    with session_factory.begin() as session:
        user = session.scalar(
            select(User).where(User.email == "admin@acme-services.example")
        )
        tenant = session.scalar(
            select(Tenant).where(Tenant.slug == "acme-services")
        )
        membership = session.scalar(
            select(TenantMembership).where(TenantMembership.user_id == user.id, TenantMembership.tenant_id == tenant.id,)
        )

        entities = {
            "user": user, 
            "tenant": tenant, 
            "membership": membership,
        }

        entities[disabled_entity].is_active = False

    response = client.get(
        "/tenants/acme-services/me",
        headers=headers,
    )

    assert response.status_code == expected_status 
    