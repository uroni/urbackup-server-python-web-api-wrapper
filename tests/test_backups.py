"""Tests for backup-related operations (backups listing, actions, start/stop)."""

import pytest


class TestBackupLists:

    def test_get_clientbackups_empty(self, server):
        server.add_client("pytest-backup-client")
        status = server.get_client_status("pytest-backup-client")
        backups = server.get_clientbackups(status["id"])
        assert isinstance(backups, list)
        assert backups == []

    def test_get_clientimagebackups_empty(self, server):
        server.add_client("pytest-imgbackup-client")
        status = server.get_client_status("pytest-imgbackup-client")
        backups = server.get_clientimagebackups(status["id"])
        assert isinstance(backups, list)
        assert backups == []


class TestStartBackup:

    @pytest.fixture(autouse=True)
    def _create_client(self, server):
        server.add_client("pytest-startbackup-client")

    def test_start_incr_file_backup_no_online_client(self, server):
        # Client exists but is not online, so backup start should fail
        result = server.start_incr_file_backup("pytest-startbackup-client")
        assert result is False

    def test_start_full_file_backup_no_online_client(self, server):
        result = server.start_full_file_backup("pytest-startbackup-client")
        assert result is False

    def test_start_incr_image_backup_no_online_client(self, server):
        result = server.start_incr_image_backup("pytest-startbackup-client")
        assert result is False

    def test_start_full_image_backup_no_online_client(self, server):
        result = server.start_full_image_backup("pytest-startbackup-client")
        assert result is False

    def test_start_backup_nonexistent_client(self, server):
        result = server.start_incr_file_backup("nonexistent-client-xyz")
        assert result is False


class TestActions:

    def test_get_actions_empty(self, server):
        actions = server.get_actions()
        assert isinstance(actions, list)

    def test_stop_action_missing_fields(self, server):
        # action dict missing required keys
        result = server.stop_action({})
        assert result is False

        result = server.stop_action({"clientid": 1})
        assert result is False

        result = server.stop_action({"id": 1})
        assert result is False


class TestActionConstants:

    def test_action_constants_exist(self):
        from urbackup_api import urbackup_server

        assert urbackup_server.action_incr_file == 1
        assert urbackup_server.action_full_file == 2
        assert urbackup_server.action_incr_image == 3
        assert urbackup_server.action_full_image == 4
        assert urbackup_server.action_resumed_incr_file == 5
        assert urbackup_server.action_resumed_full_file == 6
        assert urbackup_server.action_file_restore == 8
        assert urbackup_server.action_image_restore == 9
        assert urbackup_server.action_client_update == 10
        assert urbackup_server.action_check_db_integrity == 11
        assert urbackup_server.action_backup_db == 12
        assert urbackup_server.action_recalc_stats == 13
