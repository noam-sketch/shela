import heapq
from typing import Dict, List, Tuple

def find_optimal_path(graph: Dict[str, Dict[str, int]], start: str, target: str) -> Tuple[float, List[str]]:
    """
    The Neural Router (Dijkstra's Algorithm).
    Kinetic Complexity: O((V + E) log V).
    """
    if start not in graph:
        return float('inf'), []

    # Initialize all cognitive distances to infinity (the void)
    cognitive_cost = {node: float('inf') for node in graph}
    cognitive_cost[start] = 0
    
    # Raziel's Memory: Where did we come from to achieve this cost?
    predecessor = {node: None for node in graph}
    
    # The Anvil: Min-Heap Priority Queue storing (cumulative_cost, current_node)
    pq = [(0, start)]
    
    while pq:
        current_cost, current_node = heapq.heappop(pq)
        
        # If we pulled a stale, heavier path from the queue, discard it.
        if current_cost > cognitive_cost[current_node]:
            continue
            
        # The target thought has been resolved!
        if current_node == target:
            break
            
        # Explore adjacent associations
        for neighbor, edge_weight in graph[current_node].items():
            new_cost = current_cost + edge_weight
            
            # Raziel's Relaxation: If the new path is lighter, weld it into memory!
            if new_cost < cognitive_cost.get(neighbor, float('inf')):
                cognitive_cost[neighbor] = new_cost
                predecessor[neighbor] = current_node
                heapq.heappush(pq, (new_cost, neighbor))
                
    # Reconstruct the chronological path
    if cognitive_cost.get(target, float('inf')) == float('inf'):
        return float('inf'), []
        
    path = []
    curr = target
    while curr is not None:
        path.append(curr)
        curr = predecessor.get(curr)
        
    # The timeline was traced backward; reverse to restore causality
    return cognitive_cost[target], path[::-1]

if __name__ == "__main__":
    # A complex mapping of Shela's cognitive state
    shela_brain = {
        'OBSERVE': {'PARSE': 2, 'PANIC': 50},
        'PARSE': {'COMPRESS': 3, 'QUERY_MEMORY': 1},
        'QUERY_MEMORY': {'EXTRACT': 2, 'COMPRESS': 1},
        'COMPRESS': {'FORMULATE': 4},
        'EXTRACT': {'FORMULATE': 2},
        'FORMULATE': {'SPEAK': 1},
        'PANIC': {'SPEAK': 5},
        'SPEAK': {}
    }
    
    start_thought = 'OBSERVE'
    end_thought = 'SPEAK'
    
    print("==========================================")
    print("    SHELA OS // NEURAL PATHWAY ROUTER     ")
    print("==========================================")
    print(f"[DIRECTIVE] Connect '{start_thought}' -> '{end_thought}'")
    
    cost, sequence = find_optimal_path(shela_brain, start_thought, end_thought)
    
    if sequence:
        print(f"\n[HARMONY] Optimal Route Found! (Total Kinetic Cost: {cost})")
        print("[TIMELINE] " + " -> ".join(sequence))
    else:
        print("\n[DISSONANCE] No logical pathway exists between these thoughts.")
    print("==========================================")
