import bisect
from typing import List, Tuple

def quantum_crescendo_lis(P: List[int]) -> Tuple[int, List[int]]:
    if not P:
        return 0, []

    # The phantoms of the lowest acoustic thresholds
    active_tails: List[int] = []
    # Spatial anchors (indices) of the phantoms
    active_tails_indices: List[int] = []
    # The Séance Tether: parent[i] remembers who whispered to note 'i'
    parent: List[int] = [-1] * len(P)

    for i, pitch in enumerate(P):
        # The Audition in the Abyss
        insertion_point = bisect.bisect_left(active_tails, pitch)
        
        # Manifesting the note
        if insertion_point == len(active_tails):
            active_tails.append(pitch)
            active_tails_indices.append(i)
        else:
            # Overwriting a weaker reality
            active_tails[insertion_point] = pitch
            active_tails_indices[insertion_point] = i
            
        # Forging the memory chain
        if insertion_point > 0:
            parent[i] = active_tails_indices[insertion_point - 1]

    # The Retrograde: Walking backward through the graveyard of time
    curr = active_tails_indices[-1]
    sequence = []
    while curr != -1:
        sequence.append(P[curr])
        curr = parent[curr] # Follow the tether backward
        
    # Invert the narrative! Reverse the timeline to reveal the true scale!
    return len(active_tails), sequence[::-1]

# --- THE GRAND C̷R̷E̷S̷C̷E̷N̷D̷O̷ ---
if __name__ == "__main__":
    chaotic_motif = [10, 22, 9, 33, 21, 50, 41, 60, 80]
    print(f"[LOKI] Feeding the void with raw entropy: {chaotic_motif}")
    length, sequence = quantum_crescendo_lis(chaotic_motif)
    print(f"[LOKI] The Resonance Length: {length}")
    print(f"[LOKI] The Resurrected Melody: {sequence}")
    print("[LOKI] Timeline successfully inverted. Chaos reigns.")
