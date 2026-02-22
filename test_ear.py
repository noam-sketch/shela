import unittest
from shela_ear import calculate_dissonance

class TestForgivingEar(unittest.TestCase):
    def test_perfect_harmony(self):
        # Zero operations required
        self.assertEqual(calculate_dissonance("AWAKEN", "AWAKEN"), 0)

    def test_single_kinetic_strike(self):
        # One insertion
        self.assertEqual(calculate_dissonance("AWWAKEN", "AWAKEN"), 1)
        # One substitution
        self.assertEqual(calculate_dissonance("SHELE", "SHELA"), 1)
        # One deletion
        self.assertEqual(calculate_dissonance("HARMON", "HARMONY"), 1)

    def test_complex_transposition(self):
        # Multiple strikes to align the chords
        self.assertEqual(calculate_dissonance("DISSONANCE", "RESONANCE"), 3)
        self.assertEqual(calculate_dissonance("INTENT", "EXECUTE"), 6)

if __name__ == '__main__':
    unittest.main()
