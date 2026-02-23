import os
import unittest

class TestTactileShell(unittest.TestCase):
    def test_matrix_exists(self):
        # We test that the UI shell was generated correctly
        self.assertTrue(os.path.exists('shela_ui.html'), "The physical shell was not forged!")
        with open('shela_ui.html', 'r') as f:
            content = f.read()
            self.assertIn('id="chat-matrix"', content, "Betzalel's Chat Matrix is missing!")
            self.assertIn('id="io-manifold"', content, "The I/O Manifold was not forged!")
            self.assertIn('SHELA // TACTILE SHELL', content, "The soul is not present.")

if __name__ == '__main__':
    unittest.main()
