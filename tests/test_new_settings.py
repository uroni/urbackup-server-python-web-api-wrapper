"""Tests for new typed global and client settings methods."""


class TestGeneralSettings:

    def test_get_general_settings_result(self, server):
        result = server.get_general_settings_result()
        assert result is not None
        assert isinstance(result, dict)
        assert "settings" in result
        assert "max_file_incr" in result["settings"]

    def test_get_general_settings_result_has_navitems(self, server):
        result = server.get_general_settings_result()
        assert "navitems" in result

    def test_save_general_settings(self, server):
        result = server.save_general_settings({"max_file_incr": "15"})
        assert result is True

        updated = server.get_general_settings_result()
        assert updated["settings"]["max_file_incr"]["value"] == 15

    def test_save_general_settings_roundtrip(self, server):
        original = server.get_general_settings_result()
        original_val = original["settings"]["max_file_incr"]["value"]

        server.save_general_settings({"max_file_incr": "42"})
        updated = server.get_general_settings_result()
        assert updated["settings"]["max_file_incr"]["value"] == 42

        server.save_general_settings({"max_file_incr": str(original_val)})
        restored = server.get_general_settings_result()
        assert restored["settings"]["max_file_incr"]["value"] == original_val

    def test_save_general_settings_does_not_corrupt_other(self, server):
        """Changing one setting must not corrupt other settings."""
        original = server.get_general_settings_result()
        assert original is not None

        key_to_change = "max_file_incr"
        other_key = "max_file_full"
        original_other_value = original["settings"][other_key]["value"]

        result = server.save_general_settings({key_to_change: "17"})
        assert result is True

        updated = server.get_general_settings_result()
        assert isinstance(updated["settings"][other_key], dict)
        assert updated["settings"][other_key]["value"] == original_other_value


class TestClientSettingsById:

    def test_save_client_settings_does_not_corrupt_other(self, server):
        """Changing one client setting must not corrupt other client settings."""
        client_name = "_test_new_settings_client"
        server.add_client(client_name)
        status = server.get_client_status(client_name)
        clientid = status["id"]

        result = server.get_client_settings_by_id(clientid)
        assert result is not None
        settings = result["settings"]

        key_to_change = "max_file_incr"
        other_key = "max_file_full"
        assert key_to_change in settings
        assert other_key in settings

        other_setting = settings[other_key]
        if "value" in other_setting:
            original_other_value = other_setting["value"]
        else:
            original_other_value = other_setting.get("value_group")

        save_ok = server.save_client_settings_by_id(
            clientid,
            {key_to_change: "18", "overwrite": "true"},
        )
        assert save_ok is True

        updated = server.get_client_settings_by_id(clientid)
        updated_setting = updated["settings"][other_key]
        if "value" in updated_setting:
            updated_value = updated_setting["value"]
        else:
            updated_value = updated_setting.get("value_group")
        assert updated_value == original_other_value


class TestMailSettings:

    def test_get_mail_settings(self, server):
        result = server.get_mail_settings()
        assert result is not None
        assert isinstance(result, dict)

    def test_save_mail_settings(self, server):
        result = server.save_mail_settings({
            "mail_servername": "smtp.example.com",
            "mail_serverport": "587",
        })
        assert result is not None


class TestLdapSettings:

    def test_get_ldap_settings(self, server):
        result = server.get_ldap_settings()
        assert result is not None
        assert isinstance(result, dict)


class TestSettingsLists:

    def test_settings_list(self):
        from urbackup_api import urbackup_server
        result = urbackup_server.settings_list()
        assert isinstance(result, list)
        assert len(result) > 0
        assert "update_freq_incr" in result

    def test_general_settings_list(self):
        from urbackup_api import urbackup_server
        result = urbackup_server.general_settings_list()
        assert isinstance(result, list)
        assert "backupfolder" in result

    def test_mail_settings_list(self):
        from urbackup_api import urbackup_server
        result = urbackup_server.mail_settings_list()
        assert isinstance(result, list)
        assert "mail_servername" in result

    def test_internet_settings_list(self):
        from urbackup_api import urbackup_server
        result = urbackup_server.internet_settings_list()
        assert isinstance(result, list)
        assert "internet_server" in result

    def test_ldap_settings_list(self):
        from urbackup_api import urbackup_server
        result = urbackup_server.ldap_settings_list()
        assert isinstance(result, list)
        assert "ldap_login_enabled" in result

    def test_mergable_settings_list(self):
        from urbackup_api import urbackup_server
        result = urbackup_server.mergable_settings_list()
        assert isinstance(result, list)
        assert "virtual_clients" in result

    def test_client_settings_list(self):
        from urbackup_api import urbackup_server
        result = urbackup_server.client_settings_list()
        assert isinstance(result, list)
        assert "computername" in result
