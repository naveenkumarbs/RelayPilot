import secrets 

from fastapi import APIRouter, Response 
from sqlalchemy import Select 

from app.api.dependencies import (
    CurrentUser,
    DatabaseSession,
    authentication_error
)
from app.core.security import hash_password, verify_password
from app.core.tokens import create_acces_token
from app.models import User 
from app.schemas.auth import LoginRequest, TokenResponse, UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])

DUMMY_HASH = hash_password(secrets.token_urlsafe(32))

@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: DatabaseSession, response: Response) -> TokenResponse:
    email = body.email.strip().lower()
    user = db.scalar(Select(User).where(User.email == email))
    stored_hash = user.password_hash if user is not None else DUMMY_HASH 
    password_valid = verify_password(body.password.get_secret_value(), stored_hash)

    if user is None or not password_valid or not user.is_active:
        raise authentication_error()

    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"

    return TokenResponse(access_token=create_acces_token(user.id))

@router.get("/me", response_model=UserResponse)
def read_current_user(user:CurrentUser) -> User:
    return user