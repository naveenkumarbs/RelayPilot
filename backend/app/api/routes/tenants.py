from fastapi import APIRouter

from app.api.tenant_dependencies import AuthorizedTenant
from app.schemas.tenant import TenantMembershipResponse

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