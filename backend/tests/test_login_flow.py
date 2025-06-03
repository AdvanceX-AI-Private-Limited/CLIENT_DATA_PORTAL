# Login Flow Test
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

# Update the below import to your own app
from main import app
from api.v1.routers import auth

client = TestClient(app)

@pytest.fixture(autouse=True)
def clean_session_store():
    # Ensure session_store is always cleaned between tests
    auth.session_store.clear()
    yield
    auth.session_store.clear()


# Common mocking of DB dependency (returns a MagicMock session)
@pytest.fixture
def mock_db(monkeypatch):
    mock_db = MagicMock()
    monkeypatch.setattr("api.v1.routers.auth.get_db", lambda: mock_db)
    return mock_db


@pytest.fixture
def mock_send_mail(monkeypatch):
    monkeypatch.setattr("api.v1.routers.helpers.send_mail", lambda *a, **kw: None)


@pytest.fixture
def user_obj():
    """Returns a mock ORM user instance with minimal required attributes."""
    mock_user = MagicMock()
    mock_user.email = "user@example.com"
    mock_user.hashed_password = "hashed"
    mock_user.id = 42
    mock_user.google_linked = False
    return mock_user


@pytest.fixture
def session_token():
    return "test-session-token"


# ============ /login ===============
# 1. Login With invalid payload
def test_login_invalid_payload():
    """Payload missing required fields."""
    resp = client.post("/api/v1/auth/login", json={})
    assert resp.status_code == 422  # validation error

# 2. Login with invalid email
def test_login_invalid_email(mock_db):
    """Email not found."""
    mock_db.query.return_value.filter.return_value.first.return_value = None
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": "nouser@example.com", "password": "password"},
    )
    assert resp.status_code == 401

# 3. Login with invalid password
def test_login_invalid_password(mock_db, user_obj):
    """Email correct, password wrong."""
    mock_db.query.return_value.filter.return_value.first.return_value = user_obj
    # Patch verify_password to return False
    with patch("api.v1.routers.auth.verify_password", return_value=False):
        resp = client.post(
            "/api/v1/auth/login",
            json={"email": "user@example.com", "password": "badpass"},
        )
        assert resp.status_code == 401

# ============ /verify-otp ===============
# 4. OTP verify with invalid payload
def test_verify_otp_invalid_payload():
    """Payload missing required fields."""
    resp = client.post("/api/v1/auth/verify-otp", json={})
    assert resp.status_code == 422  # Pydantic validation error

# 5. OTP verify with invalid otp
def test_verify_otp_invalid_otp(mock_send_mail, user_obj):
    """Token valid, but OTP wrong."""
    token = "token-1"
    sess = auth.SessionData(email=user_obj.email, client_id=99)
    sess.otp = "888888"
    auth.session_store[token] = sess
    with patch("api.v1.routers.auth.create_session_token_in_db", return_value="sess-tok"):
        resp = client.post(
            "/api/v1/auth/verify-otp", json={"token": token, "otp": "123456"}
        )
        assert resp.status_code == 400
        assert resp.json()["detail"] == "Invalid OTP"


# 6. OTP verify with expired token
def test_verify_otp_expired_token():
    """Token present, but OTP expired."""
    token = "token-2"
    sess = auth.SessionData(email="e@x.com", client_id=55)
    sess.otp_timestamp = sess.otp_timestamp - 1000  # Make it expired (otp_expiry=300)
    auth.session_store[token] = sess
    resp = client.post("/api/v1/auth/verify-otp", json={"token": token, "otp": "123456"})
    assert resp.status_code == 401
    assert "OTP has expired" in resp.json()["detail"]

# ============ /resend-otp ===============
# 7. Resend OTP with invalid payload
def test_resend_otp_invalid_payload():
    """Payload missing `token`"""
    resp = client.post("/api/v1/auth/resend-otp", json={})
    assert resp.status_code == 422

# 8. Resend OTP with expired token
def test_resend_otp_expired_token():
    """Token not found in session_store."""
    resp = client.post("/api/v1/auth/resend-otp", json={"token": "doesnotexist"})
    assert resp.status_code == 401
    assert "Invalid or expired temporary token" in resp.json()["detail"]

# ============ /logout ===============
# 9. Logout with invalid session
def test_logout_invalid_session(mock_db):
    """No session token header/cookie."""
    mock_db.query.return_value.filter.return_value.first.return_value = None
    resp = client.post("/api/v1/auth/logout")
    assert resp.status_code == 401
    assert "No session token" in resp.json()["detail"]

# 10. Logout with already logged out session
def test_logout_already_logged_out_session(mock_db, session_token):
    """Session token exists but already inactive."""
    # Simulate a session that is inactive
    mock_session = MagicMock()
    mock_session.is_active = False
    mock_db.query.return_value.filter.return_value.first.return_value = mock_session
    # Set token in header
    resp = client.post(
        "/api/v1/auth/logout", headers={"Authorization": f"Bearer {session_token}"}
    )
    assert resp.status_code == 401
    assert "Invalid or expired session token" in resp.json()["detail"]

# ============ /session/validate ===============
# 11. Validate with invalid session 
def test_session_validate_invalid_session(mock_db):
    """No token / bad token."""
    mock_db.query.return_value.filter.return_value.first.return_value = None
    resp = client.get("/api/v1/auth/session/validate")
    assert resp.status_code == 401
    assert "No session token" in resp.json()["detail"]

    # Try with an invalid header as well
    resp = client.get(
        "/api/v1/auth/session/validate", headers={"Authorization": "Bearer badtoken"}
    )
    assert resp.status_code == 401
    assert "Invalid or expired session token" in resp.json()["detail"]

# ======== Extra: Valid OTP flow/happy path (for reference) ========
def test_verify_otp_success(mock_send_mail, user_obj):
    token = "token-happy"
    sess = auth.SessionData(email=user_obj.email, client_id=99)
    sess.otp = "246810"
    auth.session_store[token] = sess
    with patch("api.v1.routers.auth.create_session_token_in_db", return_value="sess-token"):
        resp = client.post(
            "/api/v1/auth/verify-otp", json={"token": token, "otp": "246810"}
        )
        assert resp.status_code == 200
        assert "session_token" in resp.json()


def test_resend_otp_success(mock_send_mail):
    token = "token-resend"
    sess = auth.SessionData(email="abc@abc.com", client_id=5)
    auth.session_store[token] = sess
    resp = client.post("/api/v1/auth/resend-otp", json={"token": token})
    assert resp.status_code == 200
    assert resp.json()["message"].startswith("New OTP sent")

# 12. Login Successfull with mock OTP send + mock OTP verification
