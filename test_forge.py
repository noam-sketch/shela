import unittest
import os

class TestGlassForge(unittest.TestCase):
    def test_monolithic_structure(self):
        from forge_ui import pour_glass
        filename = 'shela_mobile.html'
        
        # Strike the mold
        pour_glass(filename)
        
        # Verify the glass didn't shatter
        self.assertTrue(os.path.exists(filename), "Structural failure: Glass not poured.")
        
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn('id="chat-matrix"', content, "Missing load-bearing matrix!")
            self.assertIn('id="io-manifold"', content, "Missing I/O manifold!")
            self.assertIn('function transmit()', content, "Missing kinetic JavaScript relay!")

if __name__ == '__main__':
    unittest.main()
