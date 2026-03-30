"""Python wrapper for the UrBackup server web API.

Public API surface – everything previously importable from ``urbackup_api``
is still importable from here.

Three server classes are available:

* ``urbackup_server_legacy`` – only the legacy (non-typed) methods.
* ``urbackup_server_typed``  – only the new typed methods.
* ``urbackup_server``        – both combined (backward-compatible default).
"""

from __future__ import annotations

# Re-export shared types so ``from urbackup_api import BackupType`` etc. work.
from ._common import (  # noqa: F401  – re-exports
    ActivityItem,
    Backup,
    BackupFile,
    Backups,
    BackupsAccessDeniedError,
    BackupsAccessError,
    BackupType,
    ClientIdType,
    ClientInfo,
    ClientProcessActionTypes,
    ClientProcessItem,
    FilesResult,
    ImageBackupInfo,
    InstallerOS,
    LogClient,
    LogDataRow,
    LogInfo,
    LogLevel,
    PieGraphData,
    ProcessItem,
    ProgressResult,
    ResponseParseError,
    SendOnly,
    SessionNotFoundError,
    SettingsClient,
    SettingsGroup,
    StartBackupResultItem,
    StatusClientItem,
    StatusResult,
    UnknownChangePasswordError,
    UnknownRemoveUserError,
    UnknownUpdateRightsError,
    UnknownUserAddError,
    UsageClientStat,
    UsageGraphData,
    UserAlreadyExistsError,
    UserListItem,
    UserRight,
    UseValue,
    installer_os,
)

# Re-export the individual classes.
from ._legacy import urbackup_server_legacy  # noqa: F401
from ._typed import urbackup_server_typed  # noqa: F401


# ---------------------------------------------------------------------------
# Combined class (backward-compatible default)
# ---------------------------------------------------------------------------

class urbackup_server(urbackup_server_legacy, urbackup_server_typed):
    """Python wrapper to access and control an UrBackup server.

    Inherits **all** methods from both ``urbackup_server_legacy`` (non-typed,
    returns raw dicts/lists) and ``urbackup_server_typed`` (returns typed
    dataclass instances).
    """
