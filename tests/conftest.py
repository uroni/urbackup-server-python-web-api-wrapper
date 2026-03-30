import subprocess
import time

import pytest

import urbackup_api


SERVER_URL = "http://127.0.0.1:55414/x"
ADMIN_USER = "admin"
ADMIN_PASSWORD = "test1234"


def _restart_clean_server():
    """Stop urbackupsrv, wipe /var/urbackup/, start fresh."""
    subprocess.run(["sudo", "systemctl", "stop", "urbackupsrv"], check=True)
    subprocess.run(["sudo", "rm", "-rf", "/var/urbackup/"], check=True)
    subprocess.run(["sudo", "mkdir", "-p", "/var/urbackup/"], check=True)
    subprocess.run(["sudo", "chown", "urbackup:urbackup", "/var/urbackup/"], check=True)
    subprocess.run(["sudo", "systemctl", "start", "urbackupsrv"], check=True)
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
