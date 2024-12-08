import unittest
from models.character import Character

class TestCharacter(unittest.TestCase):
    def setUp(self):
        self.character = Character(name="Test Character", age=25)

    def test_initial_stats(self):
        """Test initial character stats are set correctly."""
        self.assertEqual(self.character.tier, 1)
        self.assertEqual(self.character.name, "Test Character")
        self.assertEqual(self.character.age, 25)
        self.assertEqual(self.character.xp, 0)

    def test_add_xp(self):
        """Test XP addition and leveling."""
        initial_tier = self.character.tier
        self.character.add_xp(100)
        self.assertEqual(self.character.xp, 100)

    def test_take_damage(self):
        """Test damage calculation and health reduction."""
        initial_health = self.character.current_health
        self.character.take_damage(10)
        self.assertEqual(self.character.current_health, initial_health - 10)

    def test_healing(self):
        """Test healing mechanics."""
        self.character.current_health = 10
        self.character.heal(5)
        self.assertEqual(self.character.current_health, 15)

if __name__ == '__main__':
    unittest.main()