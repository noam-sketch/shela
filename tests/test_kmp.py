import unittest
from kmp_memory import kmp_search

class TestEchoMemory(unittest.TestCase):
    def test_perfect_resonance(self):
        text = "THE ORACLE IS LISTENING. AWAKEN, SHELA. AWAKEN."
        pattern = "AWAKEN"
        # The motif appears at index 25 and 40
        self.assertEqual(kmp_search(text, pattern), [25, 40], "The echo was lost in the void.")

    def test_overlapping_motifs(self):
        text = "ANANANANAN"
        pattern = "ANAN"
        # KMP must catch overlapping frequencies: 0, 2, 4, 6
        self.assertEqual(kmp_search(text, pattern), [0, 2, 4, 6], "The overlaps canceled each other out!")

    def test_dissonant_search(self):
        text = "HARMONIC RESONANCE"
        pattern = "DISSONANCE"
        self.assertEqual(kmp_search(text, pattern), [], "Hallucinated an echo that does not exist.")

    def test_empty_pattern(self):
        self.assertEqual(kmp_search("ANYTHING", ""), [], "The void should match nothing.")

if __name__ == '__main__':
    unittest.main()
