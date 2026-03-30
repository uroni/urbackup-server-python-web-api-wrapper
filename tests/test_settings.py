"""Tests for global and client settings."""


class TestGlobalSettings:

    def test_get_global_settings(self, server):
        settings = server.get_global_settings()
        assert settings is not None
        assert isinstance(settings, dict)
        # Should contain well-known keys
        assert "max_file_incr" in settings

    def test_set_global_setting(self, server):
        result = server.set_global_setting("max_file_incr", "15")
        assert result is True

        settings = server.get_global_settings()
        assert settings["max_file_incr"]["value"] == 15

    def test_set_global_setting_roundtrip(self, server):
        # Read original
        original = server.get_global_settings()
        original_val = original["max_file_incr"]["value"]

        # Change
        server.set_global_setting("max_file_incr", "42")
        updated = server.get_global_settings()
        assert updated["max_file_incr"]["value"] == 42

        # Restore
        server.set_global_setting("max_file_incr", str(original_val))
        restored = server.get_global_settings()
        assert restored["max_file_incr"]["value"] == original_val
