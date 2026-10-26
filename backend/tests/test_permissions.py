import pytest
from sqlalchemy import select


@pytest.mark.parametrize(
    "role,expected_status",
    [
        ("admin", 200),
        ("support", 403),
        ("customer", 403),
    ],
)
def test_member_directory_requires_admin(
    client,
    login_headers,
    session_factory,
    role,
    expected_status,
):
    from app.models import Tenant, TenantMembership, User

    # Obtain a token before changing the membership role.
    headers = login_headers("acme-services")

    with session_factory.begin() as session:
        membership = session.scalar(
            select(TenantMembership)
            .join(User, User.id == TenantMembership.user_id)
            .join(Tenant, Tenant.id == TenantMembership.tenant_id)
            .where(
                User.email == "admin@acme-services.example",
                Tenant.slug == "acme-services",
            )
        )

        assert membership is not None
        membership.role = role

    response = client.get(
        "/tenants/acme-services/members",
        headers=headers,
    )

    assert response.status_code == expected_status

    if expected_status == 200:
        body = response.json()

        assert len(body) == 1
        assert body[0]["role"] == "admin"
        assert set(body[0]) == {
            "user_id",
            "display_name",
            "role",
            "membership_active",
            "user_active",
        }
    else:
        assert response.json() == {
            "detail": "Insufficient permissions"
        }


@pytest.mark.parametrize(
    "caller,target",
    [
        ("acme-services", "brightdesk-solutions"),
        ("brightdesk-solutions", "acme-services"),
    ],
)
def test_admin_cannot_list_another_tenants_members(
    client,
    login_headers,
    caller,
    target,
):
    response = client.get(
        f"/tenants/{target}/members",
        headers=login_headers(caller),
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "Tenant access denied"}


def test_member_directory_requires_authentication(client):
    response = client.get("/tenants/acme-services/members")

    assert response.status_code == 401


def test_member_directory_rejects_excessive_page_size(
    client,
    login_headers,
):
    response = client.get(
        "/tenants/acme-services/members",
        params={"limit": 101},
        headers=login_headers("acme-services"),
    )

    assert response.status_code == 422