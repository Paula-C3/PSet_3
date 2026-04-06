from backend.infrastructure.auth import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)


def test_hash_password_is_not_plain_text():
    password = "123456"
    hashed = hash_password(password)

    assert hashed != password
    assert isinstance(hashed, str)


def test_verify_password_returns_true_for_correct_password():
    password = "123456"
    hashed = hash_password(password)

    assert verify_password(password, hashed) is True


def test_verify_password_returns_false_for_incorrect_password():
    password = "123456"
    hashed = hash_password(password)

    assert verify_password("wrong-password", hashed) is False


def test_create_and_decode_access_token():
    token = create_access_token(user_id="user-1", role="ADMIN")
    payload = decode_access_token(token)

    assert payload["user_id"] == "user-1"
    assert payload["role"] == "ADMIN"
    assert "exp" in payload