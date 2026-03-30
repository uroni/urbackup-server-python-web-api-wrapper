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

    def test_set_global_setting_does_not_corrupt_other_settings(self, server):
        """Changing one setting must not corrupt the values of other settings.

        The legacy set_global_setting sends the full settings dict back to the
        server.  If nested setting objects (e.g. ``{"value": 10}``) are not
        flattened to plain values before URL-encoding, every *unchanged* setting
        is sent as a Python repr string like ``"{'value': 10}"`` which the
        server cannot parse, corrupting or rejecting the save.
        """
        original = server.get_global_settings()
        assert original is not None

        # Pick two independent settings
        key_to_change = "max_file_incr"
        other_key = "max_file_full"
        assert other_key in original, f"{other_key} not found in global settings"

        original_other_value = original[other_key]["value"]

        # Change only one setting
        result = server.set_global_setting(key_to_change, "17")
        assert result is True, "set_global_setting must return True on success"

        # Re-read and verify the untouched setting is still intact
        updated = server.get_global_settings()
        assert updated is not None
        assert isinstance(updated[other_key], dict), (
            f"Setting '{other_key}' should still be a dict with a 'value' key, "
            f"got {type(updated[other_key])!r}: {updated[other_key]!r}"
        )
        assert updated[other_key]["value"] == original_other_value, (
            f"Setting '{other_key}' was corrupted after changing '{key_to_change}': "
            f"expected {original_other_value!r}, got {updated[other_key]['value']!r}"
        )


class TestClientSettings:

    def test_change_client_setting_does_not_corrupt_other_settings(self, server):
        """Changing one client setting must not corrupt other client settings.

        Same issue as the global variant: nested setting dicts must be
        flattened before being sent to the server.
        """
        # We need at least one client.  Add one if needed.
        client_name = "_test_settings_client"
        server.add_client(client_name)

        settings = server.get_client_settings(client_name)
        assert settings is not None, (
            f"Could not retrieve client settings for '{client_name}'"
        )

        # Pick two independent settings that exist for clients.
        # Client settings use {"use": N, "value_group": X} structure.
        key_to_change = "max_file_incr"
        other_key = "max_file_full"
        assert key_to_change in settings, f"{key_to_change} not in client settings"
        assert other_key in settings, f"{other_key} not in client settings"

        other_setting = settings[other_key]
        # Grab the current effective value from whichever field is present
        if "value" in other_setting:
            original_other_value = other_setting["value"]
        else:
            original_other_value = other_setting.get("value_group")

        # Change only one setting
        result = server.change_client_setting(client_name, key_to_change, "18")
        assert result is True, "change_client_setting must return True on success"

        # Re-read and verify the untouched setting is still intact
        updated = server.get_client_settings(client_name)
        assert updated is not None
        assert isinstance(updated[other_key], dict), (
            f"Client setting '{other_key}' should still be a dict, "
            f"got {type(updated[other_key])!r}: {updated[other_key]!r}"
        )
        updated_setting = updated[other_key]
        if "value" in updated_setting:
            updated_value = updated_setting["value"]
        else:
            updated_value = updated_setting.get("value_group")
        assert updated_value == original_other_value, (
            f"Client setting '{other_key}' was corrupted after changing "
            f"'{key_to_change}': expected {original_other_value!r}, "
            f"got {updated_value!r}"
        )
