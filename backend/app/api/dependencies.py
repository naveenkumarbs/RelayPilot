from typing import Annotated

import jwt 
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session 

from app.core.tokens import decode_access_token
from app.db.session import get_db
from app.models import User 

DatabaseSession = Annotated[Session, Depends(get_db)]
bearer_scheme = HTTPBearer(auto_error=False)

BearerCredentials = Annotated[
    HTTPAuthorizationCredentials | None,
    Depends(bearer_scheme),
]

def authentication_error() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

def get_current_user(credentials: BearerCredentials, db: DatabaseSession) -> User:
    if credentials is None:
        raise authentication_error()

    try:
        user_id = decode_access_token(credentials.credentials)
    except jwt.InvalidTokenError:
        raise authentication_error() from None 

    user = db.get(User, user_id)

    if user is None or not user.is_active:
        raise authentication_error()
    print (user.display_name)
    return user

CurrentUser = Annotated[User, Depends(get_current_user)]
