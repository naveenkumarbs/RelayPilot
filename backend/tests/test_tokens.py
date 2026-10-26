from datetime import datetime, timedelta, timezone

import jwt
import pytest


@pytest.fixture
def valid_payload(login_headers):
    from app.core.config import get_settings

    settings = get_settings()

    headers = login_headers("acme-services")
    token = headers["Authorization"].removeprefix("Bearer ")

    return jwt.decode(
        token,
        settings.jwt_secret_key.get_secret_value(),
        algorithms=["HS256"],
        issuer=settings.jwt_issuer,
        audience=settings.jwt_audience,
    )


def sign_test_token(payload, *, key=None, algorithm="HS256"):
    from app.core.config import get_settings

    settings = get_settings()

    signing_key = (
        key
        if key is not None
        else settings.jwt_secret_key.get_secret_value()
    )

    return jwt.encode(
        payload,
        signing_key,
        algorithm=algorithm,
    )


def assert_token_rejected(client, token):
    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Invalid or expired credentials"
    }
    assert response.headers["WWW-Authenticate"] == "Bearer"


@pytest.mark.parametrize(
    "claim,value",
    [
        ("iss", "another-issuer"),
        ("aud", "another-audience"),
        ("token_type", "refresh"),
        ("sub", "not-a-user-id"),
        ("sub", "0"),
    ],
)
def test_invalid_claim_is_rejected(
    client,
    valid_payload,
    claim,
    value,
):
    payload = valid_payload.copy()
    payload[claim] = value

    assert_token_rejected(client, sign_test_token(payload))


def test_expired_token_is_rejected(client, valid_payload):
    payload = valid_payload.copy()
    now = datetime.now(timezone.utc)

    payload["iat"] = now - timedelta(minutes=20)
    payload["exp"] = now - timedelta(minutes=5)

    assert_token_rejected(client, sign_test_token(payload))


def test_future_issued_at_is_rejected(client, valid_payload):
    payload = valid_payload.copy()
    now = datetime.now(timezone.utc)

    payload["iat"] = now + timedelta(minutes=5)
    payload["exp"] = now + timedelta(minutes=20)

    assert_token_rejected(client, sign_test_token(payload))


@pytest.mark.parametrize(
    "claim",
    ["sub", "iat", "exp", "iss", "aud", "token_type"],
)
def test_missing_required_claim_is_rejected(
    client,
    valid_payload,
    claim,
):
    payload = valid_payload.copy()
    del payload[claim]

    assert_token_rejected(client, sign_test_token(payload))


def test_wrong_signing_key_is_rejected(client, valid_payload):
    token = sign_test_token(
        valid_payload,
        key="different-test-only-secret-with-at-least-32-characters",
    )

    assert_token_rejected(client, token)


def test_unapproved_algorithm_is_rejected(client, valid_payload):
    token = sign_test_token(
        valid_payload,
        algorithm="HS384",
    )

    assert_token_rejected(client, token)