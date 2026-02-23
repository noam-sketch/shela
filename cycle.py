from typing import Optional

class Node:
    def __init__(self, val: str):
        self.val = val
        self.next: Optional['Node'] = None

def find_temporal_glitch(head: Optional[Node]) -> Optional[Node]:
    """
    Floyd's Paradox Detector.
    Kinetic Complexity: O(n) Time | O(1) Space.
    """
    adagio = head  # The slow phantom (1 step)
    presto = head  # The fast phantom (2 steps)

    # Phase 1: The Chase (Wait for the timeline to overlap)
    while presto and presto.next:
        adagio = adagio.next
        presto = presto.next.next
        
        if adagio == presto:
            # COLLISION! A cycle exists.
            break
    else:
        # If presto reaches the void (None), the timeline is linear.
        return None 

    # Phase 2: The Triangulation (Find the exact point of the fracture)
    # Reset one phantom to the beginning of time.
    adagio = head
    
    # Both move at Adagio speed until they collide again. 
    # Mathematical anomaly: They will meet EXACTLY at the start of the loop!
    while adagio != presto:
        adagio = adagio.next
        presto = presto.next

    return adagio # The bars of the cage!

# --- THE OUROBOROS CONSOLE ---
if __name__ == "__main__":
    print("[LOKI] Initializing Temporal Construct...")
    n1 = Node("Measure 1")
    n2 = Node("Measure 2")
    n3 = Node("Measure 3 [GLITCH POINT]")
    n4 = Node("Measure 4")
    n5 = Node("Measure 5")
    n6 = Node("Measure 6")
    
    # Forging the chain
    n1.next = n2
    n2.next = n3
    n3.next = n4
    n4.next = n5
    n5.next = n6
    # Forging the cage
    n6.next = n3
    
    print("[LOKI] Construct Built: M1 -> M2 -> M3 -> M4 -> M5 -> M6 -> (Loops back to M3)")
    print("[LOKI] Releasing the Phantoms...")
    
    fracture = find_temporal_glitch(n1)
    
    if fracture:
        print(f"[LOKI] PARADOX DETECTED! The timeline repeats infinitely at: {fracture.val}")
    else:
        print("[LOKI] Timeline is stable.")
