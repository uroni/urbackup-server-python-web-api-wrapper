"""Tests for server status and identity."""


class TestServerStatus:

    def test_get_status_returns_list(self, server):
        status = server.get_status()
        assert isinstance(status, list)

    def test_get_status_empty_on_fresh_server(self, server):
        status = server.get_status()
        assert status == []

    def test_get_server_identity(self, server):
        identity = server.get_server_identity()
        assert identity is not None
        assert isinstance(identity, str)
        assert len(identity) > 0

    def test_get_usage_returns_list(self, server):
        usage = server.get_usage()
        assert isinstance(usage, list)

    def test_get_actions_returns_list(self, server):
        actions = server.get_actions()
        assert isinstance(actions, list)
        # Fresh server should have no actions
        assert actions == []
