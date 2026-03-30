"""Tests for live log retrieval."""


class TestLiveLog:

    def test_get_livelog(self, server):
        log = server.get_livelog()
        # Fresh server should have some log entries (startup messages)
        # or None if no entries exist yet
        if log is not None:
            assert isinstance(log, list)
            for entry in log:
                assert "id" in entry

    def test_get_livelog_updates_lastlogid(self, server):
        log = server.get_livelog()
        if log is not None:
            assert server._lastlogid > 0
