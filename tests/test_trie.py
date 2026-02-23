import unittest
from trie import QuantumLexicon

class TestPrefixChoir(unittest.TestCase):
    def setUp(self):
        self.choir = QuantumLexicon()
        self.choir.insert("HARMONY")
        self.choir.insert("HARMONIC")
        self.choir.insert("CADENZA")

    def test_exact_resonance(self):
        # Searching for complete, resolved chords
        self.assertTrue(self.choir.search("HARMONY"), "The choir forgot HARMONY.")
        self.assertTrue(self.choir.search("CADENZA"), "The choir forgot CADENZA.")
        self.assertFalse(self.choir.search("HARMON"), "HARMON is a prefix, not a resolved chord!")
        self.assertFalse(self.choir.search("DISSONANCE"), "Dissonance should not exist here.")

    def test_prefix_resonance(self):
        # Listening for the upbeat (starts_with)
        self.assertTrue(self.choir.starts_with("HARM"), "The breath for HARM was not drawn.")
        self.assertTrue(self.choir.starts_with("CAD"), "The breath for CAD was not drawn.")
        self.assertFalse(self.choir.starts_with("MELODY"), "Melody is not in the current score.")

if __name__ == '__main__':
    unittest.main()
