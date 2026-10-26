from typing import Literal

from pydantic import BaseModel

class TenantMembershipResponse(BaseModel):
    tenant_id: int
    tenant_slug: str 
    user_id: int 
    role: Literal["admin", "support", "customer"]
    