import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import pytest
from unittest.mock import MagicMock, patch
from app import app

app.secret_key = "test-secret-key"


@pytest.fixture
def client():
    app.testing = True
    with app.test_client() as client:
        yield client


def make_mock_cursor(user_row):
    cursor = MagicMock()
    cursor.fetchone.return_value = user_row
    return cursor


# ================= BEST CASE =================
@patch("app.get_db_connection")
@patch("app.bcrypt.check_password_hash")
def test_login_best_case_success(mock_check_password, mock_get_db_conn, client):
    user_row = {"id": 1, "email": "test@example.com", "password": "hashed_pass"}

    mock_conn = MagicMock()
    mock_cursor = make_mock_cursor(user_row)
    mock_conn.cursor.return_value = mock_cursor
    mock_get_db_conn.return_value = mock_conn

    mock_check_password.return_value = True

    response = client.post(
        "/login",
        data={"email": "test@example.com", "password": "password123"},
        follow_redirects=False
    )

    assert response.status_code == 302
    assert "home" in response.headers["Location"] or "index" in response.headers["Location"]

    with client.session_transaction() as sess:
        assert sess.get("user_id") == 1


# =============== AVERAGE CASE =================
@patch("app.get_db_connection")
@patch("app.bcrypt.check_password_hash")
def test_login_average_case_wrong_password(mock_check_password, mock_get_db_conn, client):
    user_row = {"id": 1, "email": "test@example.com", "password": "hashed_pass"}

    mock_conn = MagicMock()
    mock_cursor = make_mock_cursor(user_row)
    mock_conn.cursor.return_value = mock_cursor
    mock_get_db_conn.return_value = mock_conn

    mock_check_password.return_value = False

    response = client.post(
        "/login",
        data={"email": "test@example.com", "password": "wrongpass"},
        follow_redirects=True
    )

    assert response.status_code == 200
    assert "Invalid email or password" in response.data.decode()

    with client.session_transaction() as sess:
        assert sess.get("user_id") is None


# ================= WORST CASE =================
@patch("app.get_db_connection")
def test_login_worst_case_user_not_found(mock_get_db_conn, client):
    mock_conn = MagicMock()
    mock_cursor = make_mock_cursor(None)
    mock_conn.cursor.return_value = mock_cursor
    mock_get_db_conn.return_value = mock_conn

    response = client.post(
        "/login",
        data={"email": "notfound@example.com", "password": "anypass"},
        follow_redirects=True
    )

    assert response.status_code == 200
    assert "Invalid email or password" in response.data.decode()

    with client.session_transaction() as sess:
        assert sess.get("user_id") is None
