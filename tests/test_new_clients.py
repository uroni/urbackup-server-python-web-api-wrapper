"""Tests for new typed client management (status, settings, remove)."""

import pytest

from urbackup_api import (
    ClientInfo,
    StatusClientItem,
    StatusResult,
)


class TestGetStatusResult:

    @pytest.fixture(autouse=True)
    def _create_client(self, server):
        server.add_client("pytest-new-status-client")

    def test_client_in_status_result(self, server):
        result = server.get_status_result()
        assert isinstance(result, StatusResult)
        names = [c.name for c in result.status]
        assert "pytest-new-status-client" in names

    def test_status_items_are_typed(self, server):
        result = server.get_status_result()
        for client in result.status:
            assert isinstance(client, StatusClientItem)
            assert isinstance(client.id, int)
            assert isinstance(client.name, str)

    def test_find_client_by_name(self, server):
        result = server.get_status_result()
        matches = [c for c in result.status if c.name == "pytest-new-status-client"]
        assert len(matches) == 1
        client = matches[0]
        assert client.id > 0
        assert isinstance(client.online, bool)


class TestGetClients:

    @pytest.fixture(autouse=True)
    def _create_client(self, server):
        server.add_client("pytest-new-clients-list")

    def test_get_clients_returns_typed_list(self, server):
        clients = server.get_clients()
        assert isinstance(clients, list)
        for c in clients:
            assert isinstance(c, ClientInfo)
            assert isinstance(c.id, int)
            assert isinstance(c.name, str)

    def test_client_appears_in_list(self, server):
        clients = server.get_clients()
        names = [c.name for c in clients]
        assert "pytest-new-clients-list" in names


class TestClientSettingsById:

    @pytest.fixture(autouse=True)
    def _create_client(self, server):
        server.add_client("pytest-new-settings-client")
        status = server.get_client_status("pytest-new-settings-client")
        self._clientid = status["id"]

    def test_get_client_settings_by_id(self, server):
        result = server.get_client_settings_by_id(self._clientid)
        assert result is not None
        assert isinstance(result, dict)
        assert "settings" in result

    def test_get_client_settings_by_id_has_authkey(self, server):
        result = server.get_client_settings_by_id(self._clientid)
        settings = result["settings"]
        assert "internet_authkey" in settings

    def test_save_client_settings_by_id(self, server):
        result = server.save_client_settings_by_id(
            self._clientid,
            {"internet_authkey": "new-typed-key", "overwrite": "true"},
        )
        assert result is True

        updated = server.get_client_settings_by_id(self._clientid)
        assert updated["settings"]["internet_authkey"]["value"] == "new-typed-key"


class TestRemoveClient:

    def test_remove_client(self, server):
        server.add_client("pytest-new-remove-client")
        result = server.get_status_result()
        target = [c for c in result.status if c.name == "pytest-new-remove-client"]
        assert len(target) == 1

        remove_result = server.remove_client(target[0].id)
        assert isinstance(remove_result, StatusResult)

        # Client should now have delete_pending set
        updated = server.get_status_result()
        target_after = [c for c in updated.status if c.name == "pytest-new-remove-client"]
        if target_after:
            assert target_after[0].delete_pending != ""

    def test_stop_remove_client(self, server):
        server.add_client("pytest-new-stoprm-client")
        result = server.get_status_result()
        target = [c for c in result.status if c.name == "pytest-new-stoprm-client"]
        assert len(target) == 1
        client_id = target[0].id

        server.remove_client(client_id)
        stop_result = server.stop_remove_client(client_id)
        assert isinstance(stop_result, StatusResult)
