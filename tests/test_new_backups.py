"""Tests for new typed backup-related operations."""

import pytest

from urbackup_api import (
    BackupType,
    Backups,
    ClientProcessActionTypes,
    ProgressResult,
    StartBackupResultItem,
)


class TestBackupList:

    def test_get_backups_returns_typed(self, server):
        server.add_client("pytest-new-backup-client")
        status = server.get_client_status("pytest-new-backup-client")
        result = server.get_backups(status["id"])
        assert isinstance(result, Backups)
        assert isinstance(result.backups, list)
        assert result.backups == []

    def test_get_backups_has_image_backups(self, server):
        server.add_client("pytest-new-imgbackup-client")
        status = server.get_client_status("pytest-new-imgbackup-client")
        result = server.get_backups(status["id"])
        assert isinstance(result, Backups)
        assert isinstance(result.backup_images, list)
        assert result.backup_images == []

    def test_get_backups_has_client_info(self, server):
        server.add_client("pytest-new-bkp-info")
        status = server.get_client_status("pytest-new-bkp-info")
        result = server.get_backups(status["id"])
        assert result.clientid == status["id"]
        assert result.clientname == "pytest-new-bkp-info"


class TestStartBackup:

    @pytest.fixture(autouse=True)
    def _create_client(self, server):
        server.add_client("pytest-new-startbackup")
        self._status = server.get_client_status("pytest-new-startbackup")

    def test_start_incr_file_backup_no_online_client(self, server):
        results = server.start_backup(
            [self._status["id"]], BackupType.INCR_FILE
        )
        assert isinstance(results, list)
        for r in results:
            assert isinstance(r, StartBackupResultItem)
            # Client not online, so start_ok should be False
            assert r.start_ok is False

    def test_start_full_file_backup_no_online_client(self, server):
        results = server.start_backup(
            [self._status["id"]], BackupType.FULL_FILE
        )
        assert isinstance(results, list)
        for r in results:
            assert isinstance(r, StartBackupResultItem)
            assert r.start_ok is False

    def test_start_incr_image_backup_no_online_client(self, server):
        results = server.start_backup(
            [self._status["id"]], BackupType.INCR_IMAGE
        )
        assert isinstance(results, list)
        for r in results:
            assert isinstance(r, StartBackupResultItem)
            assert r.start_ok is False

    def test_start_full_image_backup_no_online_client(self, server):
        results = server.start_backup(
            [self._status["id"]], BackupType.FULL_IMAGE
        )
        assert isinstance(results, list)
        for r in results:
            assert isinstance(r, StartBackupResultItem)
            assert r.start_ok is False

    def test_start_backup_returns_client_id(self, server):
        results = server.start_backup(
            [self._status["id"]], BackupType.INCR_FILE
        )
        assert len(results) == 1
        assert results[0].clientid == self._status["id"]

    def test_start_backup_returns_start_type(self, server):
        results = server.start_backup(
            [self._status["id"]], BackupType.FULL_FILE
        )
        assert len(results) == 1
        assert results[0].start_type == "full_file"


class TestProgressTyped:

    def test_get_progress_empty(self, server):
        result = server.get_progress()
        assert isinstance(result, ProgressResult)
        assert result.progress == []

    def test_stop_process_invalid(self, server):
        # Stopping a nonexistent process should still return a result
        result = server.stop_process(clientid=99999, process_id=99999)
        assert isinstance(result, ProgressResult)


class TestProcessActionTypes:

    def test_action_types_enum_values(self):
        assert ClientProcessActionTypes.NONE == 0
        assert ClientProcessActionTypes.INCR_FILE == 1
        assert ClientProcessActionTypes.FULL_FILE == 2
        assert ClientProcessActionTypes.INCR_IMAGE == 3
        assert ClientProcessActionTypes.FULL_IMAGE == 4
        assert ClientProcessActionTypes.RESUME_INCR_FILE == 5
        assert ClientProcessActionTypes.RESUME_FULL_FILE == 6
        assert ClientProcessActionTypes.RESTORE_FILE == 8
        assert ClientProcessActionTypes.RESTORE_IMAGE == 9
        assert ClientProcessActionTypes.UPDATE == 10
        assert ClientProcessActionTypes.CHECK_INTEGRITY == 11
        assert ClientProcessActionTypes.BACKUP_DATABASE == 12
        assert ClientProcessActionTypes.RECALCULATE_STATISTICS == 13

    def test_backup_type_enum_values(self):
        assert BackupType.INCR_FILE.value == "incr_file"
        assert BackupType.FULL_FILE.value == "full_file"
        assert BackupType.INCR_IMAGE.value == "incr_image"
        assert BackupType.FULL_IMAGE.value == "full_image"
