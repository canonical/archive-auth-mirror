from pathlib import Path

from charmtest import CharmTest

from archive_auth_mirror.scripts.manage_user import (
    add_user,
    remove_user,
    list_users,
)


class ManageUserTest(CharmTest):

    def setUp(self):
        super().setUp()
        self.auth_file = Path(self.fakes.fs.root.path) / 'auth-file'
        self.auth_file.touch()

    def test_add_user(self):
        """add_user adds the user with the specified password."""
        add_user(self.auth_file, 'user1', 'pass1')
        add_user(self.auth_file, 'user2', 'pass2')
        self.assertIn('user1:', self.auth_file.read_text())
        self.assertIn('user2:', self.auth_file.read_text())

    def test_list_users(self):
        """list_users lists existing users."""
        add_user(self.auth_file, 'user1', 'pass1')
        add_user(self.auth_file, 'user2', 'pass2')
        users = list_users(self.auth_file)
        self.assertEqual(['user1', 'user2'], users)

    def test_list_users_no_file(self):
        """list_users returns an empty list if the file is not present."""
        self.assertEqual([], list_users(self.auth_file))

    def test_remove_user(self):
        """remove_user removes a user."""
        add_user(self.auth_file, 'user1', 'pass1')
        add_user(self.auth_file, 'user2', 'pass2')
        remove_user(self.auth_file, 'user1')
        self.assertNotIn('user1', self.auth_file.read_text())
        self.assertIn('user2', self.auth_file.read_text())
