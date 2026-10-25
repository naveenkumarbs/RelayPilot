from datetime import datetime 

from sqlalchemy import (
    Boolean, 
    CheckConstraint,
    DateTime,
    ForeignKey,
    String, 
    UniqueConstraint,
    func, 
    true, 
)

from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base 

class TenantMembership(Base):
    __tablename__ = "tenant_memberships"

    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "user_id",
            name="uq_tenant_memberships_tenant_user",
        ),
        CheckConstraint(
            "role IN ('admin', 'support', 'customer')",
            name="valid_role",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), nullable=False, index=True,)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=true())
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.current_timestamp())
    