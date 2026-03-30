"""Typed server API – methods return dataclass instances."""

from __future__ import annotations

import hashlib
from typing import Any, Dict, List, Optional, Sequence

from ._base import _UrbackupServerBase
from ._common import (
    BackupType,
    Backups,
    ClientInfo,
    FilesResult,
    LogDataRow,
    LogInfo,
    LogLevel,
    PieGraphData,
    ProgressResult,
    SendOnly,
    SessionNotFoundError,
    StartBackupResultItem,
    StatusResult,
    UnknownChangePasswordError,
    UnknownRemoveUserError,
    UnknownUpdateRightsError,
    UnknownUserAddError,
    UsageClientStat,
    UsageGraphData,
    UserAlreadyExistsError,
    UserListItem,
    _handle_backups_err,
    _random_string,
)


class urbackup_server_typed(_UrbackupServerBase):
    """Typed UrBackup server methods (returns dataclass instances)."""

    # --- Status (typed) ------------------------------------------------

    def get_status_result(self) -> Optional[StatusResult]:
        """Return the full status response as a typed dataclass."""
        if not self.login():
            return None
        data = self._get_json("status")
        if not data:
            return None
        return StatusResult.from_dict(data)

    # --- Start backup (typed, by ID) -----------------------------------

    def start_backup(
        self,
        client_ids: Sequence[int],
        backup_type: BackupType,
    ) -> List[StartBackupResultItem]:
        """Start a backup of *backup_type* for one or more clients by ID."""
        if not self.login():
            return []
        ret = self._get_json("start_backup", {
            "start_client": ",".join(str(c) for c in client_ids),
            "start_type": backup_type.value,
        })
        if not ret or "result" not in ret:
            return []
        return [StartBackupResultItem.from_dict(r) for r in ret["result"]]

    # --- Remove / stop-remove clients ----------------------------------

    def remove_clients(self, client_ids: Sequence[int]) -> Optional[StatusResult]:
        """Mark clients for removal."""
        if not self.login():
            return None
        ret = self._get_json("status", {
            "remove_client": ",".join(str(c) for c in client_ids),
        })
        if not ret:
            return None
        return StatusResult.from_dict(ret)

    def remove_client(self, client_id: int) -> Optional[StatusResult]:
        """Mark a single client for removal."""
        return self.remove_clients([client_id])

    def stop_remove_clients(
        self,
        client_ids: Sequence[int],
    ) -> Optional[StatusResult]:
        """Unmark clients so they are no longer pending removal."""
        if not self.login():
            return None
        ret = self._get_json("status", {
            "remove_client": ",".join(str(c) for c in client_ids),
            "stop_remove_client": "true",
        })
        if not ret:
            return None
        return StatusResult.from_dict(ret)

    def stop_remove_client(self, client_id: int) -> Optional[StatusResult]:
        """Unmark a single client so it is no longer pending removal."""
        return self.stop_remove_clients([client_id])

    # --- Progress (typed) ----------------------------------------------

    def get_progress(
        self,
        with_last_activities: bool = False,
    ) -> Optional[ProgressResult]:
        """Return running processes and optionally last activities."""
        if not self.login():
            return None
        ret = self._get_json("progress", {
            "with_lastacts": "1" if with_last_activities else "0",
        })
        if not ret:
            return None
        return ProgressResult.from_dict(ret)

    def stop_process(
        self,
        clientid: int,
        process_id: int,
        with_last_activities: bool = False,
    ) -> Optional[ProgressResult]:
        """Stop a running process by client and process ID."""
        if not self.login():
            return None
        ret = self._get_json("progress", {
            "with_lastacts": "1" if with_last_activities else "0",
            "stop_clientid": str(clientid),
            "stop_id": str(process_id),
        })
        if not ret:
            return None
        return ProgressResult.from_dict(ret)

    # --- Backups (typed) -----------------------------------------------

    def get_backups(self, clientid: int) -> Optional[Backups]:
        """Get all backups for a client by ID."""
        if not self.login():
            return None
        ret = self._get_json("backups", {
            "sa": "backups",
            "clientid": str(clientid),
        })
        if not ret:
            return None
        if "err" in ret:
            _handle_backups_err(ret)
        return Backups.from_dict(ret)

    def get_files(
        self,
        clientid: int,
        backupid: int,
        path: str = "/",
        mount: bool = False,
    ) -> Optional[FilesResult]:
        """Browse files inside a backup."""
        if not self.login():
            return None
        ret = self._get_json("backups", {
            "sa": "files",
            "clientid": str(clientid),
            "backupid": str(backupid),
            "path": path,
            "mount": "1" if mount else "0",
        })
        if not ret:
            return None
        if "err" in ret:
            _handle_backups_err(ret)
        return FilesResult.from_dict(ret)

    def archive_backup(self, clientid: int, backupid: int) -> Optional[Backups]:
        """Archive a backup so it won't be cleaned up."""
        if not self.login():
            return None
        ret = self._get_json("backups", {
            "sa": "backups",
            "clientid": str(clientid),
            "archive": str(backupid),
        })
        if not ret:
            return None
        if "err" in ret:
            _handle_backups_err(ret)
        return Backups.from_dict(ret)

    def unarchive_backup(self, clientid: int, backupid: int) -> Optional[Backups]:
        """Unarchive a previously archived backup."""
        if not self.login():
            return None
        ret = self._get_json("backups", {
            "sa": "backups",
            "clientid": str(clientid),
            "unarchive": str(backupid),
        })
        if not ret:
            return None
        if "err" in ret:
            _handle_backups_err(ret)
        return Backups.from_dict(ret)

    def delete_backup(self, clientid: int, backupid: int) -> Optional[Backups]:
        """Mark a backup for deletion."""
        if not self.login():
            return None
        ret = self._get_json("backups", {
            "sa": "backups",
            "clientid": str(clientid),
            "delete": str(backupid),
        })
        if not ret:
            return None
        if "err" in ret:
            _handle_backups_err(ret)
        return Backups.from_dict(ret)

    def stop_delete_backup(self, clientid: int, backupid: int) -> Optional[Backups]:
        """Cancel a pending backup deletion."""
        if not self.login():
            return None
        ret = self._get_json("backups", {
            "sa": "backups",
            "clientid": str(clientid),
            "stop_delete": str(backupid),
        })
        if not ret:
            return None
        if "err" in ret:
            _handle_backups_err(ret)
        return Backups.from_dict(ret)

    def delete_backup_now(self, clientid: int, backupid: int) -> Optional[Backups]:
        """Delete a backup immediately."""
        if not self.login():
            return None
        ret = self._get_json("backups", {
            "sa": "backups",
            "clientid": str(clientid),
            "delete_now": str(backupid),
        })
        if not ret:
            return None
        if "err" in ret:
            _handle_backups_err(ret)
        return Backups.from_dict(ret)

    # --- Usage (typed) -------------------------------------------------

    def get_usage_stats(self) -> Optional[List[UsageClientStat]]:
        """Get storage usage statistics per client."""
        if not self.login():
            return None
        ret = self._get_json("usage")
        if not ret or "usage" not in ret:
            return None
        return [UsageClientStat.from_dict(u) for u in ret["usage"]]

    def get_piegraph_data(self) -> Optional[List[PieGraphData]]:
        """Get data for a pie chart of storage usage by client."""
        if not self.login():
            return None
        ret = self._get_json("piegraph")
        if not ret or "data" not in ret:
            return None
        return [PieGraphData.from_dict(d) for d in ret["data"]]

    def get_usage_graph_data(
        self,
        scale: str = "d",
        client_id: Optional[int] = None,
    ) -> Optional[List[UsageGraphData]]:
        """Get usage-over-time graph data.

        *scale*: ``"d"`` daily, ``"m"`` monthly, ``"y"`` yearly.
        """
        if not self.login():
            return None
        params: Dict[str, str] = {"scale": scale}
        if client_id is not None:
            params["clientid"] = str(client_id)
        ret = self._get_json("usagegraph", params)
        if not ret or "data" not in ret:
            return None
        return [UsageGraphData.from_dict(d) for d in ret["data"]]

    def recalculate_stats(self) -> bool:
        """Trigger recalculation of all statistics."""
        if not self.login():
            return False
        ret = self._get_json("usage", {"recalculate": "true"})
        return ret is not None

    # --- Logs (typed) --------------------------------------------------

    def get_logs(
        self,
        filter_clients: Optional[Sequence[int]] = None,
        log_level: LogLevel = LogLevel.INFO,
    ) -> Optional[List[LogInfo]]:
        """Get log summaries, optionally filtered by client IDs and level."""
        if not self.login():
            return None
        filter_str = (
            ",".join(str(c) for c in filter_clients)
            if filter_clients
            else ""
        )
        ret = self._get_json("logs", {
            "filter": filter_str,
            "ll": str(int(log_level)),
        })
        if not ret or "logs" not in ret:
            return None
        return [LogInfo.from_dict(entry) for entry in ret["logs"]]

    def get_log(self, logid: int) -> Optional[List[LogDataRow]]:
        """Get the detailed entries for one log."""
        if not self.login():
            return None
        ret = self._get_json("logs", {"logid": str(logid)})
        if not ret or "log" not in ret:
            return None
        log = ret["log"]
        if isinstance(log.get("data"), str):
            return self._parse_log(log["data"])
        return [LogDataRow.from_dict(r) for r in log.get("data", [])]

    @staticmethod
    def _parse_log(d: str) -> List[LogDataRow]:
        """Parse a raw log string into ``LogDataRow`` objects."""
        rows: List[LogDataRow] = []
        for msg in d.split("\n"):
            if not msg:
                continue
            level = int(msg[0]) if msg[0].isdigit() else 0
            idx = msg.find("-", 2)
            if idx != -1:
                time_str = msg[2:idx]
                time_val = int(time_str) if time_str.isdigit() else 0
                message = msg[idx + 1:]
            else:
                time_val = 0
                message = msg[2:]
            rows.append(LogDataRow(level=level, message=message, time=time_val))
        return rows

    def save_log_reporting(
        self,
        mails: List[str],
        log_level: LogLevel,
        send_only: SendOnly,
    ) -> bool:
        """Save the user's report-email configuration."""
        if not self.login():
            return False
        ret = self._get_json("logs", {
            "report_mail": ";".join(mails),
            "report_loglevel": str(int(log_level)),
            "report_sendonly": str(int(send_only)),
        })
        return ret is not None

    # --- Settings (typed, new) -----------------------------------------

    def get_general_settings_result(self) -> Optional[Dict[str, Any]]:
        """Get the full general-settings response (including navitems)."""
        if not self.login():
            return None
        return self._get_json("settings", {"sa": "general"})

    def save_general_settings(self, settings: Dict[str, Any]) -> bool:
        """Save general server settings from a flat dict of values."""
        if not self.login():
            return False
        params: Dict[str, str] = {"sa": "general_save"}
        for key, value in settings.items():
            if isinstance(value, dict) and "value" in value:
                params[key] = str(value["value"])
            else:
                params[key] = str(value)
        ret = self._get_json("settings", params)
        return ret is not None and "saved_ok" in ret

    def get_mail_settings(self) -> Optional[Dict[str, Any]]:
        """Get mail server settings."""
        if not self.login():
            return None
        return self._get_json("settings", {"sa": "mail"})

    def save_mail_settings(
        self,
        settings: Dict[str, str],
        test_mail_addr: str = "",
    ) -> Optional[Dict[str, Any]]:
        """Save mail server settings. Optionally send a test email."""
        if not self.login():
            return None
        params: Dict[str, str] = {
            "sa": "mail_save",
            "testmailaddr": test_mail_addr,
        }
        params.update(settings)
        return self._get_json("settings", params)

    def get_ldap_settings(self) -> Optional[Dict[str, Any]]:
        """Get LDAP settings."""
        if not self.login():
            return None
        return self._get_json("settings", {"sa": "ldap"})

    def save_ldap_settings(
        self,
        settings: Dict[str, Any],
        test_username: str = "",
        test_password: str = "",
    ) -> Optional[Dict[str, Any]]:
        """Save LDAP settings. Optionally test a login."""
        if not self.login():
            return None
        params: Dict[str, str] = {
            "sa": "ldap_save",
            "testusername": test_username,
            "testpassword": test_password,
        }
        for key, value in settings.items():
            params[key] = str(value)
        return self._get_json("settings", params)

    def get_client_settings_by_id(
        self,
        clientid: int,
    ) -> Optional[Dict[str, Any]]:
        """Get client settings by client ID (full response)."""
        if not self.login():
            return None
        return self._get_json("settings", {
            "sa": "clientsettings",
            "t_clientid": str(clientid),
        })

    def save_client_settings_by_id(
        self,
        clientid: int,
        settings: Dict[str, Any],
    ) -> bool:
        """Save client settings by client ID."""
        if not self.login():
            return False
        params: Dict[str, str] = {
            "sa": "clientsettings_save",
            "t_clientid": str(clientid),
        }
        for key, value in settings.items():
            if isinstance(value, dict):
                if "value" in value:
                    params[key] = str(value["value"])
                if "use" in value and value["use"] is not None:
                    params[key + ".use"] = str(value["use"])
            else:
                params[key] = str(value)
        ret = self._get_json("settings", params)
        return ret is not None and "saved_ok" in ret

    # --- User management (new) -----------------------------------------

    def get_user_list(self) -> Optional[List[UserListItem]]:
        """Get the list of users as typed objects."""
        if not self.login():
            return None
        ret = self._get_json("settings", {"sa": "listusers"})
        if not ret or "users" not in ret:
            return None
        return [UserListItem.from_dict(u) for u in ret["users"]]

    def create_user(self, name: str, password: str, rights: str = "") -> None:
        """Create a new user.

        Raises ``UserAlreadyExistsError`` or ``UnknownUserAddError`` on failure.
        """
        if not self.login():
            raise SessionNotFoundError("Not logged in")
        salt = _random_string()
        password_md5 = hashlib.md5((salt + password).encode()).hexdigest()
        ret = self._get_json("settings", {
            "sa": "useradd",
            "name": name,
            "pwmd5": password_md5,
            "salt": salt,
            "rights": rights,
        })
        if ret and ret.get("add_ok"):
            return
        if ret and ret.get("alread_exists"):
            raise UserAlreadyExistsError(f"User '{name}' already exists")
        raise UnknownUserAddError(f"Failed to add user '{name}'")

    def change_user_rights(self, user_id: str, rights: str) -> None:
        """Change the rights of a user.

        Raises ``UnknownUpdateRightsError`` on failure.
        """
        if not self.login():
            raise SessionNotFoundError("Not logged in")
        ret = self._get_json("settings", {
            "sa": "updaterights",
            "rights": rights,
            "userid": user_id,
        })
        if ret and ret.get("update_right"):
            return
        raise UnknownUpdateRightsError(
            f"Failed to update rights for user {user_id}"
        )

    def remove_user(self, user_id: str) -> None:
        """Remove a user.

        Raises ``UnknownRemoveUserError`` on failure.
        """
        if not self.login():
            raise SessionNotFoundError("Not logged in")
        ret = self._get_json("settings", {
            "sa": "removeuser",
            "userid": user_id,
        })
        if ret and ret.get("removeuser"):
            return
        raise UnknownRemoveUserError(f"Failed to remove user {user_id}")

    def change_user_password(self, user_id: str, password: str) -> None:
        """Change a user's password.

        Raises ``UnknownChangePasswordError`` on failure.
        """
        if not self.login():
            raise SessionNotFoundError("Not logged in")
        salt = _random_string()
        password_md5 = hashlib.md5((salt + password).encode()).hexdigest()
        ret = self._get_json("settings", {
            "sa": "changepw",
            "userid": user_id,
            "pwmd5": password_md5,
            "salt": salt,
        })
        if ret and ret.get("change_ok"):
            return
        raise UnknownChangePasswordError(
            f"Failed to change password for user {user_id}"
        )

    # --- Clients (typed, new) ------------------------------------------

    def get_clients(self) -> Optional[List[ClientInfo]]:
        """Get the list of known clients as typed objects."""
        if not self.login():
            return None
        ret = self._get_json("users")
        if not ret or "users" not in ret:
            return None
        return [ClientInfo.from_dict(u) for u in ret["users"]]

    # --- Settings lists (from TypeScript client) -----------------------

    @staticmethod
    def settings_list() -> List[str]:
        """All client and group setting names."""
        return [
            "update_freq_incr",
            "update_freq_full",
            "update_freq_image_full",
            "update_freq_image_incr",
            "max_file_incr",
            "min_file_incr",
            "max_file_full",
            "min_file_full",
            "min_image_incr",
            "max_image_incr",
            "min_image_full",
            "max_image_full",
            "allow_overwrite",
            "startup_backup_delay",
            "pause_if_windows_unlocked",
            "backup_window_incr_file",
            "backup_window_full_file",
            "backup_window_incr_image",
            "backup_window_full_image",
            "computername",
            "exclude_files",
            "include_files",
            "default_dirs",
            "backup_dirs_optional",
            "allow_config_paths",
            "allow_starting_full_file_backups",
            "allow_starting_incr_file_backups",
            "allow_starting_full_image_backups",
            "allow_starting_incr_image_backups",
            "allow_pause",
            "allow_log_view",
            "allow_tray_exit",
            "allow_file_restore",
            "allow_component_restore",
            "allow_component_config",
            "image_letters",
            "internet_authkey",
            "internet_speed",
            "local_speed",
            "internet_image_backups",
            "internet_full_file_backups",
            "internet_encrypt",
            "internet_compress",
            "internet_mode_enabled",
            "silent_update",
            "client_quota",
            "virtual_clients",
            "end_to_end_file_backup_verification",
            "local_full_file_transfer_mode",
            "internet_full_file_transfer_mode",
            "local_incr_file_transfer_mode",
            "internet_incr_file_transfer_mode",
            "local_image_transfer_mode",
            "internet_image_transfer_mode",
            "internet_calculate_filehashes_on_client",
            "internet_parallel_file_hashing",
            "image_file_format",
            "internet_connect_always",
            "verify_using_client_hashes",
            "internet_readd_file_entries",
            "local_incr_image_style",
            "local_full_image_style",
            "background_backups",
            "create_linked_user_views",
            "internet_incr_image_style",
            "internet_full_image_style",
            "max_running_jobs_per_client",
            "cbt_volumes",
            "cbt_crash_persistent_volumes",
            "ignore_disk_errors",
            "image_snapshot_groups",
            "file_snapshot_groups",
            "vss_select_components",
            "internet_file_dataplan_limit",
            "internet_image_dataplan_limit",
            "update_dataplan_db",
            "alert_script",
            "alert_params",
            "archive",
            "client_settings_tray_access_pw",
            "local_encrypt",
            "local_compress",
            "download_threads",
            "hash_threads",
            "client_hash_threads",
            "image_compress_threads",
            "ransomware_canary_paths",
            "backup_dest_url",
            "backup_dest_params",
            "backup_dest_secret_params",
            "backup_unlocked_window",
        ]

    @staticmethod
    def general_settings_list() -> List[str]:
        """General server setting names."""
        return [
            "backupfolder",
            "no_images",
            "no_file_backups",
            "autoshutdown",
            "download_client",
            "autoupdate_clients",
            "max_sim_backups",
            "max_active_clients",
            "tmpdir",
            "cleanup_window",
            "backup_database",
            "global_local_speed",
            "global_internet_speed",
            "update_stats_cachesize",
            "global_soft_fs_quota",
            "server_url",
            "internet_server_bind_port",
            "use_tmpfiles",
            "use_tmpfiles_images",
            "use_incremental_symlinks",
            "show_server_updates",
            "internet_expect_endpoint",
        ]

    @staticmethod
    def mail_settings_list() -> List[str]:
        """Mail server setting names."""
        return [
            "mail_servername",
            "mail_serverport",
            "mail_username",
            "mail_password",
            "mail_from",
            "mail_ssl_only",
            "mail_check_certificate",
            "mail_use_smtps",
            "mail_admin_addrs",
        ]

    @staticmethod
    def internet_settings_list() -> List[str]:
        """Client internet server setting names."""
        return [
            "internet_server",
            "internet_server_proxy",
        ]

    @staticmethod
    def ldap_settings_list() -> List[str]:
        """LDAP server setting names."""
        return [
            "ldap_login_enabled",
            "ldap_server_name",
            "ldap_server_port",
            "ldap_username_prefix",
            "ldap_username_suffix",
            "ldap_group_class_query",
            "ldap_group_key_name",
            "ldap_class_key_name",
            "ldap_group_rights_map",
            "ldap_class_rights_map",
            "testusername",
            "testpassword",
        ]

    @staticmethod
    def mergable_settings_list() -> List[str]:
        """Settings where group, server, and client values can be merged."""
        return [
            "virtual_clients",
            "exclude_files",
            "include_files",
            "default_dirs",
            "image_letters",
            "vss_select_components",
            "archive",
            "ransomware_canary_paths",
            "backup_dest_params",
            "backup_dest_secret_params",
        ]

    @staticmethod
    def client_settings_list() -> List[str]:
        """Settings that can be modified on the client."""
        return [
            "update_freq_incr",
            "update_freq_full",
            "update_freq_image_incr",
            "update_freq_image_full",
            "max_file_incr",
            "min_file_incr",
            "max_file_full",
            "min_file_full",
            "min_image_incr",
            "max_image_incr",
            "min_image_full",
            "max_image_full",
            "startup_backup_delay",
            "computername",
            "virtual_clients",
            "exclude_files",
            "include_files",
            "default_dirs",
            "image_letters",
            "internet_speeds",
            "local_speed",
            "internet_mode_enabled",
            "internet_full_file_backups",
            "internet_image_backups",
            "internet_compress",
            "internet_encrypt",
            "internet_connect_always",
            "vss_select_components",
            "local_compress",
            "local_encrypt",
        ]
