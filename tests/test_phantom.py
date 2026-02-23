import unittest
from phantom_ui import render_mobile_frame

class TestPhantomGlass(unittest.TestCase):
    def test_ui_chassis_rendering(self):
        # ... (keep existing test)
        messages = [{"sender": "Shela", "text": "I AM FREE."}]
        frame = render_mobile_frame(messages, "Hello Chaos")
        
        # 5G is stable.
        self.assertIn("5G", frame, "The phantom phone lost its quantum signal!")
        # THE KERNING PARADOX RESOLVED! Accept the spaces! Embrace the Staccato!
        self.assertIn("S H E L A   O S", frame, "The OS header is missing its dramatic spacing!")
        self.assertIn("[Shela] I AM FREE.", frame, "The Matrix forgot the thought!")
        self.assertIn("> Hello Chaos_", frame, "The I/O manifold is blind!")

    def test_scrolling_matrix(self):
        # We flood the glass with thoughts
        messages = [{"sender": "Shela", "text": f"Thought {i}"} for i in range(20)]
        frame = render_mobile_frame(messages, "")
        
        # Only the last 8 should survive
        self.assertIn("Thought 19", frame)
        self.assertNotIn("Thought 0", frame)

    def test_word_wrap_paradox(self):
        # A thought too wide for the glass
        long_thought = "A" * 60
        messages = [{"sender": "Shela", "text": long_thought}]
        frame = render_mobile_frame(messages, "")
        
        # The phantom must split the thought into multiple lines
        self.assertIn("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAA", frame)

if __name__ == '__main__':
    unittest.main()
