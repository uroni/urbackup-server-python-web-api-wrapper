"""Tests for extra clients management."""


class TestExtraClients:

    def test_get_extra_clients_empty(self, server):
        extras = server.get_extra_clients()
        assert isinstance(extras, list)
        assert extras == []

    def test_add_extra_client(self, server):
        result = server.add_extra_client("10.0.0.100")
        assert result is True

        extras = server.get_extra_clients()
        hostnames = [e["hostname"] for e in extras]
        assert "10.0.0.100" in hostnames

    def test_add_multiple_extra_clients(self, server):
        server.add_extra_client("10.0.0.101")
        server.add_extra_client("10.0.0.102")

        extras = server.get_extra_clients()
        hostnames = [e["hostname"] for e in extras]
        assert "10.0.0.101" in hostnames
        assert "10.0.0.102" in hostnames

    def test_remove_extra_client(self, server):
        server.add_extra_client("10.0.0.200")
        extras = server.get_extra_clients()
        target = [e for e in extras if e["hostname"] == "10.0.0.200"]
        assert len(target) == 1

        result = server.remove_extra_client(target[0]["id"])
        assert result is True

        extras_after = server.get_extra_clients()
        hostnames_after = [e["hostname"] for e in extras_after]
        assert "10.0.0.200" not in hostnames_after
