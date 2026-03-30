"""Tests for users and groups."""


class TestUsers:

    def test_get_users(self, server):
        users = server.get_users()
        assert isinstance(users, list)
        # After setting admin password, admin user should exist
        usernames = [u["name"] for u in users]
        assert "admin" in usernames


class TestGroups:

    def test_get_groups(self, server):
        groups = server.get_groups()
        assert isinstance(groups, list)
        # There is always a default group with id 0
        ids = [g["id"] for g in groups]
        assert 0 in ids

    def test_get_clients_with_group(self, server):
        clients = server.get_clients_with_group()
        assert isinstance(clients, list)
