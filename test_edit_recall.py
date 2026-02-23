import unittest
import os

class TestQueueRecall(unittest.TestCase):
    def test_structural_edit_icon(self):
        from forge_queue_edit import pour_editable_glass
        filename = 'editable_workspace.html'
        pour_editable_glass(filename)
        
        self.assertTrue(os.path.exists(filename), "The Glass was not poured!")
        
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
            # Trap 1: The Edit Icon Glyph (Checking for the CSS class and click handler)
            self.assertIn('.edit-btn', content, "The Errata Icon style is missing from the queue!")
            self.assertIn('recallCommand(index)', content, "The Recall trigger is not bound to the icon!")
            
            # Trap 2: The Recall Logic in JS
            self.assertIn('function recallCommand', content, "The Recall logic is missing from the state!")
            self.assertIn('editor.value = cmd', content, "The ghost cannot find its way back to the manifold!")

    def test_tab_structure_updates(self):
        # Ensuring Carbon's CWD requirement is met
        from forge_queue_edit import pour_editable_glass
        filename = 'editable_workspace.html'
        pour_editable_glass(filename)
        
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn('class="cwd-label"', content, "The Key Signature (CWD) is missing from the tab!")
            self.assertIn('class="close-btn"', content, "The Coda (Close Icon) is missing from the tab!")

if __name__ == '__main__':
    unittest.main()
