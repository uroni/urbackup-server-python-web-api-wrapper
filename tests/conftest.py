import subprocess
import time

import pytest

import urbackup_api


SERVER_URL = "http://127.0.0.1:55414/x"
ADMIN_USER = "admin"
ADMIN_PASSWORD = "test1234"


def _run(cmd):
    """Run a command, capturing output and raising with details on failure."""
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"Command {cmd!r} failed (rc={result.returncode})\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
    return result


def _restart_clean_server():
    """Stop urbackupsrv, wipe /var/urbackup/, start fresh."""
    _run(["sudo", "systemctl", "stop", "urbackupsrv"])
    _run(["sudo", "rm", "-rf", "/var/urbackup/"])
    _run(["sudo", "mkdir", "-p", "/var/urbackup/"])
    _run(["sudo", "chown", "urbackup:urbackup", "/var/urbackup/"])
    _run(["sudo", "systemctl", "start", "urbackupsrv"])
    # Wait for the server to be ready
    for _ in range(30):
        try:
            s = urbackup_api.urbackup_server(SERVER_URL, ADMIN_USER, "")
            if s.login():
                break
        except Exception:
            pass
        time.sleep(1)
    else:
        raise RuntimeError("urbackupsrv did not become ready after restart")
    # Set admin password
    subprocess.run(
        ["sudo", "urbackupsrv", "reset-admin-pw", "-p", ADMIN_PASSWORD],
        check=True,
    )


@pytest.fixture(scope="module", autouse=True)
def clean_server():
    """Restart urbackupsrv with clean data before each test module."""
    _restart_clean_server()
    yield
    # No teardown needed; next module will restart anyway


@pytest.fixture()
def server():
    """Return a logged-in urbackup_server instance."""
    s = urbackup_api.urbackup_server(SERVER_URL, ADMIN_USER, ADMIN_PASSWORD)
    assert s.login(), "Failed to login to urbackup server"
    return s
