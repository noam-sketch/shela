from typing import List
from collections import deque, defaultdict

def orchestrate_assembly(V: int, edges: List[List[int]]) -> List[int]:
    """
    Industrial Topological Sort (Kahn's Algorithm).
    Time Complexity: O(V + E) - Linear processing of all parts and welds.
    """
    # structural_locks tracks how many prerequisites a component is waiting on
    structural_locks = [0] * V
    # blueprints maps a component to everything that depends on it
    blueprints = defaultdict(list)
    
    # Analyze the schematics
    for prereq, dependent in edges:
        blueprints[prereq].append(dependent)
        structural_locks[dependent] += 1
        
    # The Conveyor Belt (Queue) - Load components with zero prerequisites
    conveyor = deque([part for part in range(V) if structural_locks[part] == 0])
    
    # The final completed product sequence
    finished_sequence = []
    
    while conveyor:
        # A component rolls off the belt and is added to the structure
        current_part = conveyor.popleft()
        finished_sequence.append(current_part)
        
        # As this part is installed, we unlock its dependents
        for dependent in blueprints[current_part]:
            structural_locks[dependent] -= 1
            # If all structural locks on a dependent are removed, onto the belt it goes
            if structural_locks[dependent] == 0:
                conveyor.append(dependent)
                
    # Quality Control Check: Did we assemble all parts?
    if len(finished_sequence) == V:
        return finished_sequence
    else:
        # Circular dependency detected. Parts are stuck waiting for each other.
        return []

# --- THE FACTORY FLOOR OUTLET ---
if __name__ == "__main__":
    total_components = 6
    # 0->1, 0->2, 1->3, 2->3, 3->4, 5->4
    welds = [[0, 1], [0, 2], [1, 3], [2, 3], [3, 4], [5, 4]]
    
    print("=== HEAVY MACHINERY: TOPOLOGICAL FORGE ===")
    print(f"Total Components: {total_components}")
    print(f"Required Welds (Dependencies): {welds}")
    
    production_timeline = orchestrate_assembly(total_components, welds)
    
    if production_timeline:
        print(f"Assembly Successful. Entrance Order: {production_timeline}")
    else:
        print("CRITICAL ERROR: Deadlock detected. Scrapping build.")
    print("==========================================")
