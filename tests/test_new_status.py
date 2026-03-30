"""Tests for new typed server status, usage, and progress methods."""

from urbackup_api import (
    ProgressResult,
    StatusResult,
    UsageClientStat,
)


class TestServerStatusResult:

    def test_get_status_result_returns_typed(self, server):
        result = server.get_status_result()
        assert isinstance(result, StatusResult)
        assert isinstance(result.status, list)

    def test_get_status_result_empty_on_fresh_server(self, server):
        result = server.get_status_result()
        assert result.status == []

    def test_get_status_result_has_server_identity(self, server):
        result = server.get_status_result()
        assert result.server_identity is not None
        assert isinstance(result.server_identity, str)
        assert len(result.server_identity) > 0

    def test_get_status_result_has_admin_flag(self, server):
        result = server.get_status_result()
        assert result.admin is True

    def test_get_status_result_has_extra_clients(self, server):
        result = server.get_status_result()
        assert isinstance(result.extra_clients, list)


class TestUsageStats:

    def test_get_usage_stats_returns_typed_list(self, server):
        usage = server.get_usage_stats()
        assert isinstance(usage, list)
        for item in usage:
            assert isinstance(item, UsageClientStat)


class TestProgress:

    def test_get_progress_returns_typed(self, server):
        result = server.get_progress()
        assert isinstance(result, ProgressResult)
        assert isinstance(result.progress, list)
        # Fresh server should have no progress
        assert result.progress == []

    def test_get_progress_without_last_activities(self, server):
        result = server.get_progress(with_last_activities=False)
        assert isinstance(result, ProgressResult)
        assert result.lastacts is None

    def test_get_progress_with_last_activities(self, server):
        result = server.get_progress(with_last_activities=True)
        assert isinstance(result, ProgressResult)
        assert isinstance(result.lastacts, list)
