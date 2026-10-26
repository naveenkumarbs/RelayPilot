from typing import Literal

from pydantic import BaseModel

class TenantMembershipResponse(BaseModel):
    tenant_id: int
    tenant_slug: str 
    user_id: int 
    role: Literal["admin", "support", "customer"]

class TenantMemberResponse(BaseModel):
    user_id: int 
    display_name: str 
    role: Literal["admin", "support", "customer"]
    membership_active: bool 
    user_active: bool 
