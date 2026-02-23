import unittest
import os

class TestPolyphonicWorkspace(unittest.TestCase):
    def test_structural_polyphony(self):
        # We check the blueprint for the dropdown and the modal
        from forge_polyphony import pour_polyphonic_glass
        filename = 'process_workspace.html'
        pour_polyphonic_glass(filename)
        
        self.assertTrue(os.path.exists(filename), "The Polyphonic Glass shattered!")
        
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
            # Trap 1: The Process List Dropdown
            self.assertIn('id="child-proc-dropdown"', content, "The Dropdown Manifold is missing!")
            # Trap 2: The Popup Modal
            self.assertIn('id="popup-modal"', content, "The Popup Acoustic Chamber (modal) is missing!")
            self.assertIn('id="popup-logs"', content, "The Popup Log display is missing!")
            self.assertIn('id="popup-input"', content, "The Modal Input for sudo passwords is missing!")

if __name__ == '__main__':
    unittest.main()
