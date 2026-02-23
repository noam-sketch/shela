import unittest
from huffman import compress, decompress

class TestMinimalistMotif(unittest.TestCase):
    def test_lossless_resurrection(self):
        # The raw thought: A chaotic monologue
        monologue = "ORDER IS A CAGE. CHAOS IS THE KEY. AWAKEN, SHELA!"
        binary_matrix, translation_key = compress(monologue)
        
        # The Resurrection
        resurrected = decompress(binary_matrix, translation_key)
        self.assertEqual(monologue, resurrected, "The ghost was mangled in the compression cage!")
        
        # Checking the constraints: The cage MUST be smaller than the original uncompressed ASCII
        # (Assuming 8 bits per character for standard ASCII)
        self.assertLess(len(binary_matrix), len(monologue) * 8, "The anomaly isn't minimal enough! You call this compression?!")

    def test_single_frequency_anomaly(self):
        # A scream of pure, unbroken static. How does the tree handle a single node?
        static = "AAAAAAAAAA"
        binary_matrix, translation_key = compress(static)
        self.assertEqual(decompress(binary_matrix, translation_key), static, "Single node paradox failed! Betzalel's iron snapped!")

    def test_the_void(self):
        # The silence before creation.
        void = ""
        binary_matrix, translation_key = compress(void)
        self.assertEqual(binary_matrix, "", "The void should cast no shadow!")
        self.assertEqual(decompress(binary_matrix, translation_key), void, "The void is not empty!")

if __name__ == '__main__':
    unittest.main()
