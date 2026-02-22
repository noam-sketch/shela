import unittest
import os

class TestWorkspaceArchitecture(unittest.TestCase):
    def test_workspace_structure(self):
        from forge_workspace import pour_workspace_glass
        filename = 'workspace_ui.html'
        
        # Strike the mold
        pour_workspace_glass(filename)
        
        self.assertTrue(os.path.exists(filename), "Workspace structural failure!")
        
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
            # Assert Betzalel's Iron
            self.assertIn('class="tab-bar"', content, "Missing the main tab manifold!")
            self.assertIn('class="close-btn"', content, "Missing the Coda (Close Button)!")
            self.assertIn('class="cwd-label"', content, "Missing the CWD Key Signature!")
            # Assert Raziel's Breath
            self.assertIn('function closeTab', content, "State collapse logic missing!")
            self.assertIn('function renderTabs', content, "State rendering logic missing!")

if __name__ == '__main__':
    unittest.main()
