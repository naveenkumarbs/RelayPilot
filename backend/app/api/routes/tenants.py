from fastapi import APIRouter, Query 
from typing import Annotated
from sqlalchemy import select 

from app.api.dependencies import DatabaseSession
from app.api.permissions import AdminTenant
from app.models import TenantMembership, User 
from app.api.tenant_dependencies import AuthorizedTenant
from app.schemas.tenant import TenantMembershipResponse, TenantMemberResponse

router = APIRouter(
    prefix="/tenants",
    tags=["Tenants"],
)

@router.get("/{tenant_slug}/me", response_model=TenantMembershipResponse)
def read_tenant_membership(context: AuthorizedTenant) -> TenantMembershipResponse:
    return TenantMembershipResponse(
        tenant_id = context.tenant_id,
        tenant_slug=context.tenant_slug,
        user_id=context.user_id,
        role=context.role, 
    )

@router.get("/{tenant_slug}/members", response_model=list[TenantMemberResponse])
def list_tenant_members(
    context: AdminTenant, 
    db: DatabaseSession, 
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[TenantMemberResponse]:
    statement = (
        select(
            User.id.label("user_id"),
            User.display_name,
            TenantMembership.role,
            TenantMembership.is_active.label("membership_active"),
            User.is_active.label("user_active"),
        )
        .join(
            TenantMembership,
            TenantMembership.user_id == User.id,
        )
        .where(
            TenantMembership.tenant_id == context.tenant_id
        )
        .order_by(User.id)
        .limit(limit)
        .offset(offset)
    )

    rows = db.execute(statement).mappings().all()

    return[
        TenantMemberResponse(**row)
        for row in rows
    ]