import logging 
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status 
from sqlalchemy import text 
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session 

from app.db.session import get_db 

logger = logging.getLogger("relaypilot.health")

router = APIRouter(tags=["Health"])

DatabaseSession = Annotated[Session, Depends(get_db)]

@router.get("/health")
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "relaypilot-api"
    }

@router.get("/health/ready")
def readiness_check(db: DatabaseSession) -> dict[str, str]:
    try:
        db.execute(text("SELECT 1")).scalar_one()
    except SQLAlchemyError:
        logger.error("event=database_readiness_failed")

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database unavailable",
        ) from None 

    return {
        "status": "ready",
        "database": "ok",
    }