import logging 
from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import select 

from app.api.dependencies import CurrentUser, DatabaseSession
from app.models import TenantMembership, Tenant 

logger = logging.getLogger("relaypilot.authorization")

@dataclass(frozen=True)
class TenantContext:
    tenant_id: int
    tenant_slug: str 
    user_id: int 
    role: str 

def get_tenant_context(tenant_slug: str, user: CurrentUser, db: DatabaseSession, request: Request) -> TenantContext:
    statement = (
        select(TenantMembership, Tenant).join(Tenant, Tenant.id == TenantMembership.tenant_id)
        .where(
            Tenant.slug == tenant_slug,
            Tenant.is_active.is_(True),
            TenantMembership.user_id == user.id,
            TenantMembership.is_active.is_(True),
        )
    )

    result = db.execute(statement).one_or_none()

    if result is None:
        logger.warning(
            "event=tenant_acces_denied request_id=%s user_id=%s",
            getattr(request.state, "request_id", "-"),
            user.id,
        )

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tenant access denied",
        )

    membership, tenant = result 
    return TenantContext(
        tenant_id=tenant.id,
        tenant_slug=tenant.slug,
        user_id=user.id,
        role=membership.role,
    )

AuthorizedTenant = Annotated[
    TenantContext,
    Depends(get_tenant_context),
]
