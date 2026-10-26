def test_current_user_response(client, login_headers):
    response = client.get(
        "/auth/me",
        headers=login_headers("acme-services")
    )

    assert response.status_code == 200

    body = response.json()

    assert body["email"] == "admin@acme-services.example"
    assert set(body) == {"id", "email", "display_name"}

def test_invalid_credentials_have_same_response(client):
    wrong_pasword = client.post(
        "/auth/login",
        json ={
            "email": "admin@acme-services.example",
            "password": "incorrect-password",
        },
    )

    unknown_user = client.post(
        "/auth/login",
        json = {
            "email": "unknown@example.com",
            "password": "incorrect-password",
        },
    )

    assert wrong_pasword.status_code == 401, wrong_pasword.json() 
    assert unknown_user.status_code == 401, unknown_user.json()
    assert wrong_pasword.json() == unknown_user.json()

def test_invalid_bearer_token_is_rejected(client):
    response = client.get(
        "/auth/me",
        headers={"Authorization": "Bearer invalid-token"},
    )

    assert response.status_code == 401