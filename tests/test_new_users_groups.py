"""Tests for new typed users and groups methods."""

import pytest

from urbackup_api import (
    UserAlreadyExistsError,
    UserListItem,
    UserRight,
)


class TestUserList:

    def test_get_user_list_returns_typed(self, server):
        users = server.get_user_list()
        assert isinstance(users, list)
        for u in users:
            assert isinstance(u, UserListItem)
            assert isinstance(u.id, str)
            assert isinstance(u.name, str)
            assert isinstance(u.rights, list)

    def test_admin_in_user_list(self, server):
        users = server.get_user_list()
        names = [u.name for u in users]
        assert "admin" in names

    def test_admin_user_has_rights(self, server):
        users = server.get_user_list()
        admin = [u for u in users if u.name == "admin"][0]
        for r in admin.rights:
            assert isinstance(r, UserRight)


class TestCreateUser:

    def test_create_user(self, server):
        server.create_user("testuser1", "password123")

        users = server.get_user_list()
        names = [u.name for u in users]
        assert "testuser1" in names

    def test_create_duplicate_user_raises(self, server):
        server.create_user("testuser_dup", "password123")
        with pytest.raises(UserAlreadyExistsError):
            server.create_user("testuser_dup", "other_password")


class TestChangeUserRights:

    def test_change_user_rights(self, server):
        server.create_user("testuser_rights", "password123")
        users = server.get_user_list()
        user = [u for u in users if u.name == "testuser_rights"][0]

        # Should not raise
        server.change_user_rights(user.id, "all=all")


class TestRemoveUser:

    def test_remove_user(self, server):
        server.create_user("testuser_remove", "password123")
        users = server.get_user_list()
        user = [u for u in users if u.name == "testuser_remove"][0]

        server.remove_user(user.id)

        users_after = server.get_user_list()
        names_after = [u.name for u in users_after]
        assert "testuser_remove" not in names_after

    def test_remove_nonexistent_user_no_error(self, server):
        # Server silently accepts removal of nonexistent user IDs
        server.remove_user("99999")


class TestChangeUserPassword:

    def test_change_user_password(self, server):
        server.create_user("testuser_pwchange", "oldpassword")
        users = server.get_user_list()
        user = [u for u in users if u.name == "testuser_pwchange"][0]

        # Should not raise
        server.change_user_password(user.id, "newpassword")


class TestGroupsTyped:

    def test_groups_from_general_settings(self, server):
        result = server.get_general_settings_result()
        assert result is not None
        assert "navitems" in result
        groups = result["navitems"]["groups"]
        assert isinstance(groups, list)
        ids = [g["id"] for g in groups]
        assert 0 in ids

    def test_clients_with_group_from_general_settings(self, server):
        result = server.get_general_settings_result()
        assert result is not None
        clients = result["navitems"]["clients"]
        assert isinstance(clients, list)
