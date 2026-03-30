"""Tests for extra clients via the new typed status API."""

from urbackup_api import StatusResult


class TestExtraClientsTyped:

    def test_get_extra_clients_from_status_result(self, server):
        result = server.get_status_result()
        assert isinstance(result, StatusResult)
        assert isinstance(result.extra_clients, list)
        assert result.extra_clients == []

    def test_extra_client_appears_in_status_result(self, server):
        server.add_extra_client("10.0.1.100")

        result = server.get_status_result()
        hostnames = [e["hostname"] for e in result.extra_clients]
        assert "10.0.1.100" in hostnames

    def test_multiple_extra_clients_in_status_result(self, server):
        server.add_extra_client("10.0.1.101")
        server.add_extra_client("10.0.1.102")

        result = server.get_status_result()
        hostnames = [e["hostname"] for e in result.extra_clients]
        assert "10.0.1.101" in hostnames
        assert "10.0.1.102" in hostnames

    def test_removed_extra_client_gone_from_status_result(self, server):
        server.add_extra_client("10.0.1.200")
        result = server.get_status_result()
        target = [e for e in result.extra_clients if e["hostname"] == "10.0.1.200"]
        assert len(target) == 1

        server.remove_extra_client(target[0]["id"])

        result_after = server.get_status_result()
        hostnames_after = [e["hostname"] for e in result_after.extra_clients]
        assert "10.0.1.200" not in hostnames_after
