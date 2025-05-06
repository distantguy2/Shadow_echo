import unittest
from src.systems.roles import assign_roles

class TestRoles(unittest.TestCase):
    def test_assign_roles_unique(self):
        players = ['p1', 'p2', 'p3']
        roles = assign_roles(players)
        self.assertEqual(len(roles), len(set(roles.values())))
        for player in players:
            self.assertIn(player, roles)

    def test_roles_from_pool(self):
        players = ['p1', 'p2', 'p3', 'p4']
        role_pool = ['♕', '♛', '☢', '♕']  # Allow duplicate roles
        roles = assign_roles(players, role_pool)
        for role in roles.values():
            self.assertIn(role, role_pool)

    def test_invalid_player_list(self):
        with self.assertRaises(ValueError):
            assign_roles([])

if __name__ == '__main__':
    unittest.main()
