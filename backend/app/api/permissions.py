# reusable role checker 

import logging 
from typing import Annotated, Literal 

from fastapi import Depends, HTTPException, Request, status 

from app.api.tenant_dependencies import AuthorizedTenant, TenantContext

logger = logging.getLogger("relaypilot.authorization")

TenantRole = Literal["admin", "support", "customer"]

class RequireRoles:
    def __init__(self, *allowed_roles: TenantRole):
        valid_roles = {"admin", "support", "customer"}
        print(allowed_roles)
        print(set(allowed_roles))

        if not allowed_roles or not set(allowed_roles) <= valid_roles:
            raise ValueError("Specify at least one valid tenant role.")

        self.allowed_roles = frozenset(allowed_roles)

    def __call__(self, context: AuthorizedTenant, request: Request) -> TenantContext:
        if context.role not in self.allowed_roles:
            logger.warning(
                "event=role_access_denied request_id=%s "
                "tenant_id=%s user_id=%s",
                getattr(request.state, "request_id", "-"),
                context.tenant_id,
                context.user_id,
            )

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )

        return context 

AdminTenant = Annotated[TenantContext, Depends(RequireRoles("admin"))]
