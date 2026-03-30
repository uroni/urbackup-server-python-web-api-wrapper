"""Tests for client management (add, status, settings, authkey)."""

import pytest


class TestAddClient:

    def test_add_client(self, server):
        ret = server.add_client("pytest-client-1")
        assert ret is not None
        assert ret["added_new_client"] is True
        assert "new_authkey" in ret
        assert ret["new_clientname"] == "pytest-client-1"

    def test_add_client_duplicate_returns_none(self, server):
        server.add_client("pytest-dup")
        ret = server.add_client("pytest-dup")
        assert ret is None

    def test_add_client_with_group(self, server):
        ret = server.add_client("pytest-grouped", groupname="testgroup")
        assert ret is not None
        assert ret["added_new_client"] is True


class TestGetClientStatus:

    @pytest.fixture(autouse=True)
    def _create_client(self, server):
        server.add_client("pytest-status-client")

    def test_get_client_status(self, server):
        status = server.get_client_status("pytest-status-client")
        assert status is not None
        assert status["name"] == "pytest-status-client"
        assert "id" in status

    def test_get_client_status_nonexistent(self, server):
        status = server.get_client_status("nonexistent-client-xyz")
        assert status is None

    def test_client_appears_in_status_list(self, server):
        all_status = server.get_status()
        names = [c["name"] for c in all_status]
        assert "pytest-status-client" in names


class TestClientSettings:

    @pytest.fixture(autouse=True)
    def _create_client(self, server):
        server.add_client("pytest-settings-client")

    def test_get_client_settings(self, server):
        settings = server.get_client_settings("pytest-settings-client")
        assert settings is not None
        assert isinstance(settings, dict)
        assert "internet_authkey" in settings

    def test_get_client_settings_nonexistent(self, server):
        settings = server.get_client_settings("nonexistent-client-xyz")
        assert settings is None

    def test_change_client_setting(self, server):
        result = server.change_client_setting(
            "pytest-settings-client", "internet_authkey", "my-custom-key"
        )
        assert result is True

        authkey = server.get_client_authkey("pytest-settings-client")
        assert authkey is not None
        assert authkey["value"] == "my-custom-key"


class TestClientAuthkey:

    @pytest.fixture(autouse=True)
    def _create_client(self, server):
        server.add_client("pytest-authkey-client")

    def test_get_client_authkey(self, server):
        authkey = server.get_client_authkey("pytest-authkey-client")
        assert authkey is not None

    def test_get_client_authkey_nonexistent(self, server):
        authkey = server.get_client_authkey("nonexistent-client-xyz")
        assert authkey is None
