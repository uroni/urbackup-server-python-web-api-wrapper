"""Tests for new InstallerOS enum."""

from urbackup_api import InstallerOS


class TestInstallerOSEnum:

    def test_installer_os_values(self):
        assert InstallerOS.WINDOWS.value == "windows"
        assert InstallerOS.LINUX.value == "linux"
        assert InstallerOS.MAC.value == "mac"

    def test_download_installer_with_new_enum(self, server):
        import os
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".sh", delete=False) as tmp:
            tmpname = tmp.name

        try:
            result = server.download_installer(
                tmpname, "pytest-new-installer-client", InstallerOS.LINUX
            )
            assert result is True
            assert os.path.exists(tmpname)
            assert os.path.getsize(tmpname) > 0
        finally:
            os.unlink(tmpname)
