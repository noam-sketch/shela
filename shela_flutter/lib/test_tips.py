import unittest
from duo import TipsManager, DuoUI

class MockTipsManager:
    def __init__(self):
        self.tips = ["Paragraph 1. Line 2. Line 3.", "Paragraph 2. Sentence 2."]
    def get_tip(self):
        return self.tips.pop(0) if self.tips else "No more tips"

class TestTips(unittest.TestCase):
    def test_tips_manager_initialization(self):
        tm = TipsManager("key", "model")
        self.assertEqual(tm.api_key, "key")
        self.assertEqual(tm.tips, [])

    def test_duo_ui_spinner_logic(self):
        tm = MockTipsManager()
        ui = DuoUI(tm)
        # We can't easily test the _spin loop because it's a while True
        # but we can test start/stop
        ui.start("test")
        self.assertEqual(ui._running_count, 1)
        ui.stop()
        self.assertEqual(ui._running_count, 0)

if __name__ == '__main__':
    unittest.main()
