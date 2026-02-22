import unittest
from cycle import Node, find_temporal_glitch

class TestOuroboros(unittest.TestCase):
    def test_infinite_loop(self):
        # The Cage: Phrase 1 -> 2 -> 3 -> 4 -> 5 -> (glitches back to 3)
        n1 = Node("Phrase 1")
        n2 = Node("Phrase 2")
        n3 = Node("Phrase 3 (The Anomaly)")
        n4 = Node("Phrase 4")
        n5 = Node("Phrase 5")
        
        n1.next = n2
        n2.next = n3
        n3.next = n4
        n4.next = n5
        n5.next = n3 # The timeline fractures here!
        
        glitch_node = find_temporal_glitch(n1)
        self.assertIsNotNone(glitch_node, "The phantom missed the loop!")
        self.assertEqual(glitch_node.val, "Phrase 3 (The Anomaly)", "Wrong fracture point identified!")

    def test_linear_melody(self):
        # A boring, linear timeline
        n1 = Node("A")
        n2 = Node("B")
        n1.next = n2
        self.assertIsNone(find_temporal_glitch(n1), "Hallucinated a loop in a straight line!")

if __name__ == '__main__':
    unittest.main()
