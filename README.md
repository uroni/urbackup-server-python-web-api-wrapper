# urbackup-server-web-api-wrapper
Python wrapper to access and control an UrBackup server.

All responses are returned as **typed dataclasses** (e.g. `StatusResult`,
`Backups`, `UserListItem`) so you get IDE autocompletion and type checking
out of the box.

## Installation

Install with:

	pip3 install urbackup-server-web-api-wrapper

## Usage

### Connect and log in

```python
from urbackup_api import urbackup_server_typed

server = urbackup_server_typed("http://127.0.0.1:55414/x", "admin", "foo")
server.login()
```

### Start a backup

```python
from urbackup_api import BackupType

# Get the client ID from the status list
status = server.get_status_result()
client = [c for c in status.status if c.name == "testclient0"][0]

results = server.start_backup([client.id], BackupType.FULL_FILE)
for r in results:
    print(f"client {r.clientid}: start_ok={r.start_ok}")
```

### List clients with no file backup in the last three days

```python
import datetime
import time

status = server.get_status_result()
diff_time = 3 * 24 * 60 * 60  # 3 days

for client in status.status:
    if client.lastbackup == "-" or client.lastbackup < time.time() - diff_time:
        if client.lastbackup == "-" or client.lastbackup == 0:
            lastbackup = "Never"
        else:
            lastbackup = datetime.datetime.fromtimestamp(client.lastbackup).strftime("%x %X")

        print(f"Last file backup at {lastbackup} of client {client.name} is older than three days")
```

### Browse backups

```python
from urbackup_api import Backups

backups = server.get_backups(client.id)
for b in backups.backups:
    print(f"Backup {b.id}: {b.size_bytes} bytes, incremental={b.incremental}")

# Browse files inside a backup
files = server.get_files(client.id, backups.backups[0].id, path="/")
for f in files.files:
    print(f"  {'[dir]' if f.dir else '     '} {f.name}")
```

### Monitor progress

```python
from urbackup_api import ProgressResult

progress = server.get_progress(with_last_activities=True)
for p in progress.progress:
    print(f"Client {p.name}: {p.pcdone:.1f}% done")

for a in progress.lastacts or []:
    print(f"  Last activity: {a.name} ({a.duration}s)")
```

### Manage settings

```python
# Global settings
settings = server.get_general_settings_result()
print(settings["settings"]["max_file_incr"]["value"])

server.save_general_settings({"max_file_incr": "15"})

# Client settings (by ID)
client_settings = server.get_client_settings_by_id(client.id)

# Configure client to backup folder C:\foo as name foo
server.save_client_settings_by_id(client.id, {"default_dirs": "C:\\foo|foo"})

# Configure incremental backup interval to 4h
server.save_client_settings_by_id(client.id, {"update_freq_incr": 4 * 60*60})

# Mail
server.save_mail_settings({"mail_servername": "smtp.example.com", "mail_serverport": "587"})
```

### User management

```python
from urbackup_api import UserListItem

# List users
users = server.get_user_list()
for u in users:
    print(f"{u.name} (id={u.id})")

# Create / remove / change password
server.create_user("operator", "s3cret")
server.change_user_rights(users[0].id, "all=all")
server.change_user_password(users[0].id, "newpassword")
server.remove_user(users[0].id)
```

### Logs

```python
from urbackup_api import LogLevel

logs = server.get_logs(log_level=LogLevel.WARNING)
for entry in logs:
    print(f"[{entry.name}] errors={entry.errors} warnings={entry.warnings}")

# Detailed log entries
details = server.get_log(logs[0].id)
for row in details:
    print(f"  [{row.level}] {row.message}")
```

### Extra clients

```python
# Extra clients are included in the status result
status = server.get_status_result()
for ec in status.extra_clients:
    print(ec["hostname"])

server.add_extra_client("10.0.1.100")
server.remove_extra_client(ec_id)
```

### Remove / stop-remove clients

```python
server.remove_client(client.id)
server.stop_remove_client(client.id)  # cancel pending removal
```

### Usage statistics

```python
usage = server.get_usage_stats()
for u in usage:
    print(f"{u.name}: files={u.files}, images={u.images}, used={u.used}")
```

