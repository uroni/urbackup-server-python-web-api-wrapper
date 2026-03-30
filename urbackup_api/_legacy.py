"""Legacy (non-typed) server API – methods return raw dicts and lists."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

from ._base import _UrbackupServerBase
from ._common import InstallerOS, installer_os


class urbackup_server_legacy(_UrbackupServerBase):
    """Non-typed UrBackup server methods (backward-compatible dict returns)."""

    # Legacy action constants (backward compatible) ----------------------
    action_incr_file: int = 1
    action_full_file: int = 2
    action_incr_image: int = 3
    action_full_image: int = 4
    action_resumed_incr_file: int = 5
    action_resumed_full_file: int = 6
    action_file_restore: int = 8
    action_image_restore: int = 9
    action_client_update: int = 10
    action_check_db_integrity: int = 11
    action_backup_db: int = 12
    action_recalc_stats: int = 13

    # -------------------------------------------------------------------
    # Status (legacy – returns dicts/lists)
    # -------------------------------------------------------------------

    def get_client_status(self, clientname: str) -> Optional[Dict[str, Any]]:

        if not self.login():
            return None

        status = self._get_json("status")

        if not status:
            return None

        if "status" not in status:
            return None

        for client in status["status"]:

            if client["name"] == clientname:
                return client

        return None

    def get_status(self) -> Optional[List[Dict[str, Any]]]:
        if not self.login():
            return None

        status = self._get_json("status")

        if not status:
            return None

        if "status" not in status:
            return None

        return status["status"]

    def get_server_identity(self) -> Optional[str]:

        if not self.login():
            return None

        status = self._get_json("status")

        if not status:
            return None

        if "server_identity" not in status:
            return None

        return status["server_identity"]

    # -------------------------------------------------------------------
    # Installer (legacy)
    # -------------------------------------------------------------------

    def download_installer(
        self,
        installer_fn: str,
        new_clientname: str,
        e_installer_os: Union[installer_os, InstallerOS],
    ) -> bool:

        if not self.login():
            return False

        new_client = self._get_json("add_client", {"clientname": new_clientname})
        if new_client is None:
            return False
        if "already_exists" in new_client:

            status = self.get_client_status(new_clientname)

            if status is None:
                return False

            return self._download_file("download_client", installer_fn, {
                "clientid": status["id"],
                "os": e_installer_os.value,
            })

        if "new_authkey" not in new_client:
            return False

        return self._download_file("download_client", installer_fn, {
            "clientid": new_client["new_clientid"],
            "authkey": new_client["new_authkey"],
            "os": e_installer_os.value,
        })

    # -------------------------------------------------------------------
    # Clients (legacy)
    # -------------------------------------------------------------------

    def add_client(
        self,
        clientname: str,
        groupname: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        if not self.login():
            return None

        data: Dict[str, Any] = {"clientname": clientname}
        if groupname is not None:
            data['group_name'] = groupname

        ret = self._get_json("add_client", data)
        if ret is None or "already_exists" in ret:
            return None

        return ret

    # -------------------------------------------------------------------
    # Settings (legacy)
    # -------------------------------------------------------------------

    def get_global_settings(self) -> Optional[Dict[str, Any]]:
        if not self.login():
            return None

        settings = self._get_json("settings", {"sa": "general"})

        if not settings or "settings" not in settings:
            return None

        return settings["settings"]

    def set_global_setting(self, key: str, new_value: str) -> bool:
        if not self.login():
            return False

        settings = self._get_json("settings", {"sa": "general"})

        if not settings or "settings" not in settings:
            return False

        settings["settings"][key] = new_value
        settings["settings"]["sa"] = "general_save"

        params: Dict[str, Any] = {}
        for k, v in settings["settings"].items():
            params[k] = v["value"] if isinstance(v, dict) and "value" in v else v

        ret = self._get_json("settings", params)

        return ret is not None and "saved_ok" in ret

    def get_client_settings(self, clientname: str) -> Optional[Dict[str, Any]]:

        if not self.login():
            return None

        client = self.get_client_status(clientname)

        if client is None:
            return None

        clientid = client["id"]

        settings = self._get_json("settings", {
            "sa": "clientsettings",
            "t_clientid": clientid,
        })

        if not settings or "settings" not in settings:
            return None

        return settings["settings"]

    def change_client_setting(
        self,
        clientname: str,
        key: str,
        new_value: str,
    ) -> bool:
        if not self.login():
            return False

        client = self.get_client_status(clientname)

        if client is None:
            return False

        clientid = client["id"]

        settings = self._get_json("settings", {
            "sa": "clientsettings",
            "t_clientid": clientid,
        })

        if not settings or "settings" not in settings:
            return False

        settings["settings"][key] = new_value
        settings["settings"]["overwrite"] = "true"
        settings["settings"]["sa"] = "clientsettings_save"
        settings["settings"]["t_clientid"] = clientid

        params: Dict[str, Any] = {}
        for k, v in settings["settings"].items():
            if isinstance(v, dict):
                if "use" in v:
                    params[k + ".use"] = v["use"]
                if "value" in v:
                    params[k] = v["value"]
            elif not isinstance(v, list):
                params[k] = v

        ret = self._get_json("settings", params)

        return ret is not None and "saved_ok" in ret

    def get_client_authkey(self, clientname: str) -> Optional[Any]:

        if not self.login():
            return None

        settings = self.get_client_settings(clientname)

        if settings:
            return settings["internet_authkey"]

        return None

    # -------------------------------------------------------------------
    # Users / groups (legacy)
    # -------------------------------------------------------------------

    def get_users(self) -> Optional[List[Dict[str, Any]]]:
        if not self.login():
            return None

        users = self._get_json("settings", {"sa": "listusers"})

        if not users or "users" not in users:
            return None

        return users["users"]

    def get_groups(self) -> Optional[List[Dict[str, Any]]]:
        if not self.login():
            return None

        settings = self._get_json("settings")
        if settings is None:
            return None

        return settings["navitems"]["groups"]

    def get_clients_with_group(self) -> Optional[List[Dict[str, Any]]]:
        if not self.login():
            return None

        settings = self._get_json("settings")
        if settings is None:
            return None

        return settings["navitems"]["clients"]

    # -------------------------------------------------------------------
    # Live log (legacy)
    # -------------------------------------------------------------------

    def get_livelog(self, clientid: int = 0) -> Optional[List[Dict[str, Any]]]:
        if not self.login():
            return None

        log = self._get_json("livelog", {
            "clientid": clientid,
            "lastid": self._lastlogid,
        })

        if not log:
            return None

        if "logdata" not in log:
            return None

        self._lastlogid = log["logdata"][-1]['id']

        return log["logdata"]

    # -------------------------------------------------------------------
    # Usage (legacy)
    # -------------------------------------------------------------------

    def get_usage(self) -> Optional[List[Dict[str, Any]]]:
        if not self.login():
            return None

        usage = self._get_json("usage")

        if not usage:
            return None

        if "usage" not in usage:
            return None

        return usage["usage"]

    # -------------------------------------------------------------------
    # Extra clients (legacy)
    # -------------------------------------------------------------------

    def get_extra_clients(self) -> Optional[List[Dict[str, Any]]]:
        if not self.login():
            return None

        status = self._get_json("status")

        if not status:
            return None

        if "extra_clients" not in status:
            return None

        return status["extra_clients"]

    def add_extra_client(self, addr: str) -> bool:
        if not self.login():
            return False

        ret = self._get_json("status", {"hostname": addr})

        if not ret:
            return False

        return True

    def remove_extra_client(self, ecid: Union[int, str]) -> bool:
        if not self.login():
            return False

        ret = self._get_json("status", {
            "hostname": ecid,
            "remove": "true",
        })

        if not ret:
            return False

        return True

    # -------------------------------------------------------------------
    # Backups (legacy)
    # -------------------------------------------------------------------

    def _start_backup(self, clientname: str, backup_type: str) -> bool:

        client_info = self.get_client_status(clientname)

        if not client_info:
            return False

        ret = self._get_json("start_backup", {
            "start_client": client_info["id"],
            "start_type": backup_type,
        })

        if (ret is None
                or "result" not in ret
                or len(ret["result"]) != 1
                or "start_ok" not in ret["result"][0]
                or not ret["result"][0]["start_ok"]):
            return False

        return True

    def start_incr_file_backup(self, clientname: str) -> bool:
        return self._start_backup(clientname, 'incr_file')

    def start_full_file_backup(self, clientname: str) -> bool:
        return self._start_backup(clientname, 'full_file')

    def start_incr_image_backup(self, clientname: str) -> bool:
        return self._start_backup(clientname, 'incr_image')

    def start_full_image_backup(self, clientname: str) -> bool:
        return self._start_backup(clientname, 'full_image')

    def get_clientimagebackups(
        self,
        clientid: int = 0,
    ) -> Optional[List[Dict[str, Any]]]:
        if not self.login():
            return None

        backups = self._get_json("backups", {
            "sa": "backups",
            "clientid": clientid,
        })
        if backups is None:
            return None

        return backups["backup_images"]

    def get_clientbackups(
        self,
        clientid: int = 0,
    ) -> Optional[List[Dict[str, Any]]]:
        if not self.login():
            return None

        backups = self._get_json("backups", {
            "sa": "backups",
            "clientid": clientid,
        })
        if backups is None:
            return None

        return backups["backups"]

    def get_backup_content(
        self,
        clientid: int,
        backupid: int,
        path: str = "/",
    ) -> Optional[List[Dict[str, Any]]]:
        if not self.login():
            return None

        content = self._get_json("backups", {
            "sa": "files",
            "clientid": clientid,
            "backupid": backupid,
            "path": path,
        })
        if content is None:
            return None

        return content["files"]

    def download_backup_file(
        self,
        clientid: int,
        backupid: int,
        path: str = "/",
    ) -> Optional[bytes]:
        if not self.login():
            return None

        response = self._get_response("backups", {
            "sa": "filesdl",
            "clientid": clientid,
            "backupid": backupid,
            "path": path,
        }, "GET")

        if response.status != 200:
            return None
        return response.read()

    # -------------------------------------------------------------------
    # Actions / progress (legacy)
    # -------------------------------------------------------------------

    def get_actions(self) -> Optional[List[Dict[str, Any]]]:
        if not self.login():
            return None

        ret = self._get_json("progress")

        if not ret or "progress" not in ret:
            return None

        return ret["progress"]

    def stop_action(self, action: Dict[str, Any]) -> bool:
        if ("clientid" not in action
                or "id" not in action):
            return False

        if not self.login():
            return False

        ret = self._get_json("progress", {
            "stop_clientid": action["clientid"],
            "stop_id": action["id"],
        })

        if not ret or "progress" not in ret:
            return False

        return True
