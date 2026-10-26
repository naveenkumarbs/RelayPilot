from datetime import datetime, timedelta, timezone 

import jwt

from app.core.config import get_settings

ALGORITHM = "HS256"

def create_acces_token(user_id: int) -> str:
    settings = get_settings()
    now = datetime.now(timezone.utc)

    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + timedelta(minutes=settings.access_token_expire_minutes),
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience,
        "token_type": "access",
    }

    return jwt.encode(payload, settings.jwt_secret_key.get_secret_value(), algorithm=ALGORITHM)

def decode_access_token(token: str) -> str: 
    settings = get_settings()

    payload = jwt.decode(
        token,
        settings.jwt_secret_key.get_secret_value(),
        algorithms=[ALGORITHM],
        issuer=settings.jwt_issuer,
        audience=settings.jwt_audience,
        options={
            "require": ["sub", "iat", "exp", "iss", "aud", "token_type"]
        },
    )

    if payload["token_type"] != "access":
        raise jwt.InvalidTokenError("Unexpected token type.")

    subject = payload["sub"]

    if not isinstance(subject, str) or not subject.isascii() or not subject.isdigit():
        raise jwt.InvalidTokenError("Invalid subject.")

    user_id = int(subject)
    if user_id <= 0:
        raise jwt.InvalidTokenError("Invalid subject.")

    return user_id
