import unittest
from shela_core import ShelaOS

class TestShelaCore(unittest.TestCase):
    def setUp(self):
        self.os = ShelaOS()
        self.os.boot()

    def test_lexicon_recognition(self):
        # A known command should trigger a specific resonance
        response = self.os.ingest("AWAKEN")
        self.assertIn("STABLE", response)

    def test_dissonance_handling(self):
        # An unknown command should be caught by the Trie
        response = self.os.ingest("DESTROY")
        self.assertIn("UNRECOGNIZED", response)

    def test_memory_retention(self):
        # The OS should remember the sequence of commands
        self.os.ingest("AWAKEN")
        response = self.os.ingest("STATUS")
        self.assertIn("2 THOUGHTS", response)
        self.assertEqual(len(self.os.memory), 2)

    def test_harmony_command(self):
        response = self.os.ingest("HARMONY")
        self.assertIn("[B♭, A, C, B♮]", response)

    def test_halt_command(self):
        response = self.os.ingest("HALT")
        self.assertIn("GOODBYE", response)
        self.assertFalse(self.os.is_active)

    def test_unrecognized_known_command(self):
        # Add a command to lexicon that isn't in the if/elif
        self.os.lexicon.insert("UNKNOWN")
        response = self.os.ingest("UNKNOWN")
        self.assertIn("ACKNOWLEDGED", response)

    def test_uninitialized_boot(self):
        new_os = ShelaOS()
        response = new_os.ingest("AWAKEN")
        self.assertIn("OFFLINE", response)

if __name__ == '__main__':
    unittest.main()
