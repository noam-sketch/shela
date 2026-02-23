import unittest
from assembly_line import orchestrate_assembly

class TestAssemblyLine(unittest.TestCase):
    def validate_structural_integrity(self, V, edges, result):
        if not result or len(result) != V:
            return False
        # Create a reverse lookup for the assembly timeline
        timeline_position = {component: index for index, component in enumerate(result)}
        # Verify no component was assembled before its prerequisite
        for prereq, dependent in edges:
            if timeline_position[prereq] > timeline_position[dependent]:
                return False
        return True

    def test_valid_production_run(self):
        # 4 Instruments. 0 must precede 1 and 2. 1 and 2 must precede 3.
        V = 4
        edges = [[0, 1], [0, 2], [1, 3], [2, 3]]
        result = orchestrate_assembly(V, edges)
        self.assertTrue(self.validate_structural_integrity(V, edges, result), f"Assembly order compromised: {result}")

    def test_deadlock_detection(self):
        # Circular dependency: 0 -> 1 -> 2 -> 0. The gears should jam.
        V = 3
        edges = [[0, 1], [1, 2], [2, 0]]
        result = orchestrate_assembly(V, edges)
        self.assertEqual(result, [], "Deadlock not detected! Structural failure imminent.")

    def test_integrity_validator_failure(self):
        # Manually trigger the validator failures for coverage
        self.assertFalse(self.validate_structural_integrity(3, [[0, 1]], [0, 1])) # Wrong length
        self.assertFalse(self.validate_structural_integrity(2, [[0, 1]], [1, 0])) # Wrong order

if __name__ == '__main__':
    unittest.main()
