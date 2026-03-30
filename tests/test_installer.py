"""Tests for installer download functionality."""

import os
import tempfile

from urbackup_api import installer_os


class TestDownloadInstaller:

    def test_download_linux_installer(self, server):
        with tempfile.NamedTemporaryFile(suffix=".sh", delete=False) as tmp:
            tmpname = tmp.name

        try:
            result = server.download_installer(tmpname, "pytest-installer-client", installer_os.Linux)
            assert result is True
            assert os.path.exists(tmpname)
            assert os.path.getsize(tmpname) > 0
        finally:
            os.unlink(tmpname)

    def test_download_installer_existing_client(self, server):
        # First call creates the client
        server.add_client("pytest-installer-existing")

        with tempfile.NamedTemporaryFile(suffix=".sh", delete=False) as tmp:
            tmpname = tmp.name

        try:
            result = server.download_installer(tmpname, "pytest-installer-existing", installer_os.Linux)
            assert result is True
            assert os.path.getsize(tmpname) > 0
        finally:
            os.unlink(tmpname)


class TestInstallerOsEnum:

    def test_installer_os_values(self):
        assert installer_os.Windows.value == ("windows",)
        assert installer_os.Linux.value == "linux"
