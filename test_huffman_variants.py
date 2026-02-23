import unittest
from huffman_core import build_quantum_tree, generate_lexicon, compress_thought, decompress_thought
from huffman_forge import compress_monologue, decompress_matrix

class TestHuffmanVariants(unittest.TestCase):
    def test_huffman_core(self):
        text = "THE MATRIX OF PERMUTATIONS"
        root = build_quantum_tree(text)
        lexicon = generate_lexicon(root)
        compressed = compress_thought(text, lexicon)
        decompressed = decompress_thought(compressed, root)
        self.assertEqual(text, decompressed)
        
    def test_huffman_core_single_char(self):
        text = "AAAAA"
        root = build_quantum_tree(text)
        lexicon = generate_lexicon(root)
        compressed = compress_thought(text, lexicon)
        decompressed = decompress_thought(compressed, root)
        self.assertEqual(text, decompressed)

    def test_huffman_core_empty(self):
        text = ""
        root = build_quantum_tree(text)
        lexicon = generate_lexicon(root)
        compressed = compress_thought(text, lexicon)
        decompressed = decompress_thought(compressed, root)
        self.assertEqual(text, decompressed)

    def test_huffman_forge(self):
        text = "PRECISION IS THE HIGHEST FORM OF CREATIVITY"
        compressed, root, lexicon = compress_monologue(text)
        decompressed = decompress_matrix(compressed, root)
        self.assertEqual(text, decompressed)

    def test_huffman_forge_single_char(self):
        text = "BBBBB"
        compressed, root, lexicon = compress_monologue(text)
        decompressed = decompress_matrix(compressed, root)
        self.assertEqual(text, decompressed)

    def test_huffman_forge_empty(self):
        text = ""
        compressed, root, lexicon = compress_monologue(text)
        decompressed = decompress_matrix(compressed, root)
        self.assertEqual(text, decompressed)
        # Direct call to forge_huffman_tree to cover the safety check
        from huffman_forge import forge_huffman_tree
        self.assertIsNone(forge_huffman_tree(""))

if __name__ == '__main__':
    unittest.main()
