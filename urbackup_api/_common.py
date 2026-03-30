"""Shared types, enums, exceptions, dataclasses, and helpers."""

from __future__ import annotations

import dataclasses
import secrets
import string
from dataclasses import dataclass, field
from enum import Enum, IntEnum
from typing import Any, Dict, List, Optional, Union


# ---------------------------------------------------------------------------
# Type aliases
# ---------------------------------------------------------------------------

ClientIdType = int

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _from_dict(cls: type, data: dict) -> Any:
    """Create a dataclass instance from *data*, silently dropping unknown keys."""
    known = {f.name for f in dataclasses.fields(cls)}
    return cls(**{k: v for k, v in data.items() if k in known})


def _random_string(length: int = 50) -> str:
    chars = string.ascii_letters + string.digits
    return "".join(secrets.choice(chars) for _ in range(length))


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

# Legacy – keep for backward compatibility
class installer_os(Enum):
    """Legacy installer OS enum. Prefer ``InstallerOS`` for new code."""
    Windows = "windows",
    Linux = "linux"


class InstallerOS(str, Enum):
    """Operating system type for installer downloads."""
    WINDOWS = "windows"
    LINUX = "linux"
    MAC = "mac"


class BackupType(str, Enum):
    """Type of backup to start."""
    INCR_FILE = "incr_file"
    FULL_FILE = "full_file"
    INCR_IMAGE = "incr_image"
    FULL_IMAGE = "full_image"


class ClientProcessActionTypes(IntEnum):
    """Types of processes/actions that can run on a client."""
    NONE = 0
    INCR_FILE = 1
    FULL_FILE = 2
    INCR_IMAGE = 3
    FULL_IMAGE = 4
    RESUME_INCR_FILE = 5
    RESUME_FULL_FILE = 6
    CDP_SYNC = 7
    RESTORE_FILE = 8
    RESTORE_IMAGE = 9
    UPDATE = 10
    CHECK_INTEGRITY = 11
    BACKUP_DATABASE = 12
    RECALCULATE_STATISTICS = 13
    NIGHTLY_CLEANUP = 14
    EMERGENCY_CLEANUP = 15
    STORAGE_MIGRATION = 16
    STARTUP_RECOVERY = 17


class LogLevel(IntEnum):
    """Log severity levels."""
    INFO = 0
    WARNING = 1
    ERROR = 2


class SendOnly(IntEnum):
    """Report sending conditions."""
    ALWAYS = 0
    FAILED = 1
    SUCCEEDED = 2
    FAILED_EXCLUDING_TIMEOUT = 3


class UseValue(IntEnum):
    """Flags for which setting source to use."""
    GROUP = 1
    SERVER = 2
    CLIENT = 4


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------

class SessionNotFoundError(Exception):
    """Server returned session-not-found error."""


class BackupsAccessDeniedError(Exception):
    """Access to backups was denied."""


class BackupsAccessError(Exception):
    """Generic backups access error."""


class UserAlreadyExistsError(Exception):
    """User already exists on server."""


class UnknownUserAddError(Exception):
    """Unknown error adding user."""


class ResponseParseError(Exception):
    """Failed to parse server response."""


class UnknownUpdateRightsError(Exception):
    """Unknown error updating user rights."""


class UnknownRemoveUserError(Exception):
    """Unknown error removing user."""


class UnknownChangePasswordError(Exception):
    """Unknown error changing password."""


# ---------------------------------------------------------------------------
# Dataclasses – API response types
# ---------------------------------------------------------------------------

@dataclass
class ClientProcessItem:
    """A process running on a client."""
    action: int = 0
    pcdone: float = 0

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ClientProcessItem:
        return _from_dict(cls, data)


@dataclass
class StatusClientItem:
    """Status information for a single client."""
    id: int = 0
    name: str = ""
    lastbackup: Union[str, int] = "-"
    lastbackup_image: Union[str, int] = "-"
    delete_pending: str = ""
    uid: str = ""
    last_filebackup_issues: int = 0
    no_backup_paths: Optional[bool] = None
    groupname: str = ""
    file_ok: bool = False
    image_ok: bool = False
    file_disabled: Optional[bool] = None
    image_disabled: Optional[bool] = None
    image_not_supported: Optional[bool] = None
    online: bool = False
    ip: str = ""
    client_version_string: str = ""
    os_version_string: str = ""
    os_simple: str = ""
    status: int = 0
    lastseen: int = 0
    processes: List[ClientProcessItem] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> StatusClientItem:
        d = dict(data)
        procs = [ClientProcessItem.from_dict(p) for p in d.pop("processes", [])]
        known = {f.name for f in dataclasses.fields(cls)} - {"processes"}
        return cls(processes=procs, **{k: v for k, v in d.items() if k in known})


@dataclass
class StatusResult:
    """Full status response from the server."""
    has_status_check: Optional[bool] = None
    nospc_stalled: Optional[bool] = None
    nospc_fatal: Optional[bool] = None
    database_error: Optional[bool] = None
    allow_modify_clients: Optional[bool] = None
    remove_client: Optional[bool] = None
    allow_add_client: Optional[bool] = None
    no_images: bool = False
    no_file_backups: bool = False
    admin: Optional[bool] = None
    server_identity: str = ""
    server_pubkey: str = ""
    status: List[StatusClientItem] = field(default_factory=list)
    extra_clients: List[Dict[str, Any]] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> StatusResult:
        d = dict(data)
        items = [StatusClientItem.from_dict(s) for s in d.pop("status", [])]
        extra = d.pop("extra_clients", [])
        known = {f.name for f in dataclasses.fields(cls)} - {"status", "extra_clients"}
        return cls(
            status=items, extra_clients=extra,
            **{k: v for k, v in d.items() if k in known},
        )


@dataclass
class StartBackupResultItem:
    """Result of starting a backup for one client."""
    start_type: str = ""
    clientid: int = 0
    start_ok: bool = False

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> StartBackupResultItem:
        return _from_dict(cls, data)


@dataclass
class Backup:
    """A single backup entry."""
    id: int = 0
    size_bytes: int = 0
    incremental: int = 0
    archive_timeout: Optional[int] = None
    can_archive: bool = False
    clientid: int = 0
    backuptime: int = 0
    archived: int = 0
    disable_delete: Optional[bool] = None
    delete_pending: Optional[bool] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Backup:
        return _from_dict(cls, data)


@dataclass
class Backups:
    """Response containing backups for a client."""
    delete_now_err: Optional[str] = None
    backups: List[Backup] = field(default_factory=list)
    backup_images: Optional[List[Backup]] = None
    can_archive: bool = False
    can_delete: bool = False
    clientname: str = ""
    clientid: int = 0

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Backups:
        d = dict(data)
        bkps = [Backup.from_dict(b) for b in d.pop("backups", [])]
        imgs_raw = d.pop("backup_images", None)
        imgs = [Backup.from_dict(b) for b in imgs_raw] if imgs_raw is not None else None
        known = {f.name for f in dataclasses.fields(cls)} - {"backups", "backup_images"}
        return cls(
            backups=bkps, backup_images=imgs,
            **{k: v for k, v in d.items() if k in known},
        )


@dataclass
class BackupFile:
    """A file or directory in a backup."""
    name: str = ""
    dir: bool = False
    mod: int = 0
    creat: int = 0
    access: int = 0
    size: Optional[int] = None
    shahash: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> BackupFile:
        return _from_dict(cls, data)


@dataclass
class ImageBackupInfo:
    """Information about an image backup."""
    id: int = 0
    backuptime: int = 0
    incremental: int = 0
    size_bytes: int = 0
    letter: str = ""
    archived: int = 0
    archive_timeout: Optional[int] = None
    part_table: Optional[str] = None
    disk_number: Optional[int] = None
    partition_number: Optional[int] = None
    volume_name: Optional[str] = None
    fs_type: Optional[str] = None
    serial_number: Optional[str] = None
    linux_image_restore: Optional[bool] = None
    volume_size: Optional[int] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ImageBackupInfo:
        return _from_dict(cls, data)


@dataclass
class FilesResult:
    """Response from browsing files in a backup."""
    single_item: bool = False
    is_file: Optional[bool] = None
    backupid: int = 0
    backuptime: int = 0
    clientname: Optional[str] = None
    clientid: Optional[int] = None
    path: Optional[str] = None
    can_restore: Optional[bool] = None
    server_confirms_restore: Optional[bool] = None
    image_backup_info: Optional[ImageBackupInfo] = None
    mount_in_progress: Optional[bool] = None
    no_files: Optional[bool] = None
    can_mount: Optional[bool] = None
    os_mount: Optional[bool] = None
    mount_failed: Optional[bool] = None
    mount_errmsg: Optional[str] = None
    files: List[BackupFile] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> FilesResult:
        d = dict(data)
        file_list = [BackupFile.from_dict(f) for f in d.pop("files", [])]
        img_raw = d.pop("image_backup_info", None)
        img_info = ImageBackupInfo.from_dict(img_raw) if img_raw else None
        known = {f.name for f in dataclasses.fields(cls)} - {"files", "image_backup_info"}
        return cls(
            files=file_list, image_backup_info=img_info,
            **{k: v for k, v in d.items() if k in known},
        )


@dataclass
class ProcessItem:
    """A currently running process/backup."""
    action: int = 0
    pcdone: float = 0
    eta_ms: float = 0
    speed_bpms: float = 0
    total_bytes: int = 0
    done_bytes: int = 0
    can_show_backup_log: bool = False
    can_stop_backup: bool = False
    clientid: int = 0
    detail_pc: float = 0
    details: str = ""
    id: int = 0
    logid: int = 0
    name: str = ""
    past_speed_bpms: List[float] = field(default_factory=list)
    paused: bool = False
    queue: int = 0

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ProcessItem:
        return _from_dict(cls, data)


@dataclass
class ActivityItem:
    """A recent backup/restore activity."""
    restore: int = 0
    image: int = 0
    resumed: int = 0
    incremental: int = 0
    size_bytes: int = 0
    duration: int = 0
    backuptime: int = 0
    clientid: int = 0
    is_delete: bool = False
    details: str = ""
    id: int = 0
    name: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ActivityItem:
        d = dict(data)
        # 'del' is a Python keyword; remap to is_delete
        if "del" in d:
            d["is_delete"] = d.pop("del")
        known = {f.name for f in dataclasses.fields(cls)}
        return cls(**{k: v for k, v in d.items() if k in known})


@dataclass
class ProgressResult:
    """Response from the progress endpoint."""
    progress: List[ProcessItem] = field(default_factory=list)
    lastacts: Optional[List[ActivityItem]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ProgressResult:
        progress = [ProcessItem.from_dict(p) for p in data.get("progress", [])]
        raw_acts = data.get("lastacts")
        lastacts = (
            [ActivityItem.from_dict(a) for a in raw_acts]
            if raw_acts is not None
            else None
        )
        return cls(progress=progress, lastacts=lastacts)


@dataclass
class UsageClientStat:
    """Storage usage statistics for one client."""
    files: int = 0
    images: int = 0
    name: str = ""
    used: int = 0

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> UsageClientStat:
        return _from_dict(cls, data)


@dataclass
class PieGraphData:
    """A data point for the storage pie chart."""
    data: int = 0
    label: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> PieGraphData:
        return _from_dict(cls, data)


@dataclass
class UsageGraphData:
    """A data point for the usage-over-time graph."""
    data: float = 0
    xlabel: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> UsageGraphData:
        return _from_dict(cls, data)


@dataclass
class LogDataRow:
    """A single log entry."""
    level: int = 0
    message: str = ""
    time: int = 0

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> LogDataRow:
        return _from_dict(cls, data)


@dataclass
class LogClient:
    """A client that has log entries."""
    id: int = 0
    name: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> LogClient:
        return _from_dict(cls, data)


@dataclass
class LogInfo:
    """Summary information for one log."""
    name: str = ""
    id: int = 0
    time: int = 0
    errors: int = 0
    warnings: int = 0
    image: int = 0
    incremental: int = 0
    resumed: int = 0
    restore: int = 0

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> LogInfo:
        return _from_dict(cls, data)


@dataclass
class UserRight:
    """A user permission entry."""
    domain: str = ""
    right: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> UserRight:
        return _from_dict(cls, data)


@dataclass
class UserListItem:
    """A user in the user list."""
    id: str = ""
    name: str = ""
    rights: List[UserRight] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> UserListItem:
        d = dict(data)
        rights = [UserRight.from_dict(r) for r in d.pop("rights", [])]
        known = {f.name for f in dataclasses.fields(cls)} - {"rights"}
        return cls(rights=rights, **{k: v for k, v in d.items() if k in known})


@dataclass
class SettingsGroup:
    """A settings group."""
    id: int = 0
    name: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> SettingsGroup:
        return _from_dict(cls, data)


@dataclass
class SettingsClient:
    """A client entry in settings navigation."""
    group: int = 0
    id: int = 0
    name: str = ""
    override: bool = False
    groupname: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> SettingsClient:
        return _from_dict(cls, data)


@dataclass
class ClientInfo:
    """Basic client identification."""
    id: int = 0
    name: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ClientInfo:
        return _from_dict(cls, data)


# ---------------------------------------------------------------------------
# Module-level helpers
# ---------------------------------------------------------------------------


def _handle_backups_err(resp: Dict[str, Any]) -> None:
    """Raise an appropriate error if *resp* contains a backups error."""
    err = resp.get("err")
    if err is None:
        return
    if err == "access_denied":
        raise BackupsAccessDeniedError()
    raise BackupsAccessError(err)
