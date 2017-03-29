from pathlib import Path

from fixtures import TestWithFixtures, TempDir

from importlib.machinery import SourceFileLoader


# manually import the script since it's not in a module
manage_user = SourceFileLoader(
    'manage_user', "resources/manage-user").load_module()


class ManageUserTest(TestWithFixtures):

    def setUp(self):
        super().setUp()
        tempdir = self.useFixture(TempDir())
        self.auth_file = Path(tempdir.path) / 'auth-file'
        self.auth_file.touch()

    def test_add_user(self):
        """add_user adds the user with the specified password."""
        manage_user.add_user(self.auth_file, 'user1', 'pass1')
        manage_user.add_user(self.auth_file, 'user2', 'pass2')
        self.assertIn('user1:', self.auth_file.read_text())
        self.assertIn('user2:', self.auth_file.read_text())

    def test_list_users(self):
        """list_users lists existing users."""
        manage_user.add_user(self.auth_file, 'user1', 'pass1')
        manage_user.add_user(self.auth_file, 'user2', 'pass2')
        users = manage_user.list_users(self.auth_file)
        self.assertEqual(['user1', 'user2'], users)

    def test_list_users_no_file(self):
        """list_users returns an empty list if the file is not present."""
        self.assertEqual([], manage_user.list_users(self.auth_file))

    def test_remove_user(self):
        """remove_user removes a user."""
        manage_user.add_user(self.auth_file, 'user1', 'pass1')
        manage_user.add_user(self.auth_file, 'user2', 'pass2')
        manage_user.remove_user(self.auth_file, 'user1')
        self.assertNotIn('user1', self.auth_file.read_text())
        self.assertIn('user2', self.auth_file.read_text())
