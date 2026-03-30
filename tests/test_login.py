"""Tests for login and authentication."""

import urbackup_api

from conftest import ADMIN_PASSWORD, ADMIN_USER, SERVER_URL


class TestLogin:

    def test_login_correct_password(self):
        server = urbackup_api.urbackup_server(SERVER_URL, ADMIN_USER, ADMIN_PASSWORD)
        assert server.login() is True

    def test_login_wrong_password(self):
        server = urbackup_api.urbackup_server(SERVER_URL, ADMIN_USER, "wrongpassword")
        assert server.login() is False

    def test_login_wrong_username(self):
        server = urbackup_api.urbackup_server(SERVER_URL, "nonexistent", "whatever")
        assert server.login() is False

    def test_login_idempotent(self):
        server = urbackup_api.urbackup_server(SERVER_URL, ADMIN_USER, ADMIN_PASSWORD)
        assert server.login() is True
        # Calling login again should still succeed (cached)
        assert server.login() is True

    def test_anonymous_login_fails_with_password_set(self):
        server = urbackup_api.urbackup_server(SERVER_URL, ADMIN_USER, "")
        assert server.login() is False
