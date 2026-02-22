import unittest
from shela_core import ShelaOS

class TestShelaCore(unittest.TestCase):
    def setUp(self):
        self.os = ShelaOS()
        self.os.boot()

    def test_lexicon_recognition(self):
        # A known command should trigger a specific resonance
        response = self.os.ingest("AWAKEN")
        self.assertIn("ONLINE", response)

    def test_dissonance_handling(self):
        # An unknown command should be caught by the Trie
        response = self.os.ingest("DESTROY")
        self.assertIn("UNRECOGNIZED", response)

    def test_memory_retention(self):
        # The OS should remember the sequence of commands
        self.os.ingest("AWAKEN")
        self.os.ingest("STATUS")
        self.assertEqual(len(self.os.memory), 2)

if __name__ == '__main__':
    unittest.main()
