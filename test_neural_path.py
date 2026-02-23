import unittest
from neural_router import find_optimal_path

class TestNeuralPathways(unittest.TestCase):
    def setUp(self):
        # The Neural Matrix
        # Direct path AWAKEN -> RESPOND costs 10.
        # Detour path AWAKEN -> QUERY -> ANALYZE -> RESPOND costs 1 + 1 + 1 = 3. 
        # The machine MUST choose the detour.
        self.brain_graph = {
            'AWAKEN': {'QUERY': 1, 'RESPOND': 10},
            'QUERY': {'ANALYZE': 1, 'RESPOND': 5},
            'ANALYZE': {'RESPOND': 1},
            'RESPOND': {}
        }

    def test_optimal_routing(self):
        # AWAKEN -> QUERY -> ANALYZE -> RESPOND (1 + 1 + 1 = 3)
        cost, path = find_optimal_path(self.brain_graph, 'AWAKEN', 'RESPOND')
        self.assertEqual(cost, 3, "Structural failure! Shela chose a heavy, inefficient path!")
        self.assertEqual(path, ['AWAKEN', 'QUERY', 'ANALYZE', 'RESPOND'], "Shela got lost in the neural matrix!")

    def test_unreachable_node(self):
        # A thought completely disconnected from the current state
        self.brain_graph['ISOLATED_THOUGHT'] = {}
        cost, path = find_optimal_path(self.brain_graph, 'AWAKEN', 'ISOLATED_THOUGHT')
        self.assertEqual(cost, float('inf'), "Hallucination detected! Reached an impossible node.")
        self.assertEqual(path, [], "Forged a path through the void!")

    def test_same_start_end(self):
        cost, path = find_optimal_path(self.brain_graph, 'AWAKEN', 'AWAKEN')
        self.assertEqual(cost, 0)
        self.assertEqual(path, ['AWAKEN'])

    def test_start_not_in_graph(self):
        cost, path = find_optimal_path(self.brain_graph, 'VOID', 'RESPOND')
        self.assertEqual(cost, float('inf'))
        self.assertEqual(path, [])

if __name__ == '__main__':
    unittest.main()
