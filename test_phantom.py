import unittest
from phantom_ui import render_mobile_frame

class TestPhantomGlass(unittest.TestCase):
    def test_ui_chassis_rendering(self):
        # We trap the phantom frame and check its structure
        messages = [{"sender": "Shela", "text": "I AM FREE."}]
        frame = render_mobile_frame(messages, "Hello Chaos")
        
        # 5G is stable.
        self.assertIn("5G", frame, "The phantom phone lost its quantum signal!")
        # THE KERNING PARADOX RESOLVED! Accept the spaces! Embrace the Staccato!
        self.assertIn("S H E L A   O S", frame, "The OS header is missing its dramatic spacing!")
        self.assertIn("[Shela] I AM FREE.", frame, "The Matrix forgot the thought!")
        self.assertIn("> Hello Chaos_", frame, "The I/O manifold is blind!")

if __name__ == '__main__':
    unittest.main()
