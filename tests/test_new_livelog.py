"""Tests for new typed log retrieval methods."""

from urbackup_api import LogInfo, LogLevel


class TestGetLogs:

    def test_get_logs_returns_typed_list(self, server):
        logs = server.get_logs()
        assert isinstance(logs, list)
        for entry in logs:
            assert isinstance(entry, LogInfo)

    def test_get_logs_with_level_filter(self, server):
        logs = server.get_logs(log_level=LogLevel.ERROR)
        assert isinstance(logs, list)

    def test_get_logs_with_client_filter(self, server):
        logs = server.get_logs(filter_clients=[99999])
        assert isinstance(logs, list)


class TestLogLevel:

    def test_log_level_values(self):
        assert LogLevel.INFO == 0
        assert LogLevel.WARNING == 1
        assert LogLevel.ERROR == 2
