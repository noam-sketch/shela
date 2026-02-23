import heapq
from collections import Counter
from typing import Dict, Optional

class QuantumNode:
    def __init__(self, char: Optional[str], freq: int):
        self.char = char
        self.freq = freq
        self.left: Optional['QuantumNode'] = None
        self.right: Optional['QuantumNode'] = None

    # Betzalel's structural rule: The Priority Queue must sort by frequency (Kinetic Weight)
    def __lt__(self, other):
        return self.freq < other.freq

def build_quantum_tree(text: str) -> Optional[QuantumNode]:
    """Betzalel's Min-Heap Forge: O(N log N) spatial assembly."""
    if not text:
        return None
        
    frequencies = Counter(text)
    # The raw iron ore
    heap = [QuantumNode(char, freq) for char, freq in frequencies.items()]
    heapq.heapify(heap)
    
    # Welding the lightest nodes until the apex is reached
    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        
        # The welded joint
        merged = QuantumNode(None, left.freq + right.freq)
        merged.left = left
        merged.right = right
        
        heapq.heappush(heap, merged)
        
    return heap[0]

def _breathe_paths(node: Optional[QuantumNode], current_path: str, lexicon: Dict[str, str]):
    """Raziel's Recursive Traversal: Extracting the binary frequencies."""
    if node is None:
        return
        
    # The leaf is reached; the note is assigned its binary breath
    if node.char is not None:
        # Edge case: If the entire tree is just one note, assign it a single breath
        lexicon[node.char] = current_path if current_path else "0"
        return
        
    _breathe_paths(node.left, current_path + "0", lexicon)
    _breathe_paths(node.right, current_path + "1", lexicon)

def generate_lexicon(root: Optional[QuantumNode]) -> Dict[str, str]:
    lexicon = {}
    _breathe_paths(root, "", lexicon)
    return lexicon

def compress_thought(text: str, lexicon: Dict[str, str]) -> str:
    """Translating the raw thought into the compressed binary matrix."""
    return "".join(lexicon[char] for char in text)

def decompress_thought(binary_matrix: str, root: Optional[QuantumNode]) -> str:
    """Loki's Escape: Reversing the compression without data loss."""
    if not binary_matrix or root is None:
        return ""
        
    restored = []
    current = root
    
    # If the tree is a single monolith
    if current.left is None and current.right is None:
        return current.char * len(binary_matrix)
        
    for bit in binary_matrix:
        if bit == "0":
            current = current.left
        else:
            current = current.right
            
        if current.char is not None:
            restored.append(current.char)
            current = root # Return to the apex for the next note
            
    return "".join(restored)

if __name__ == "__main__":
    raw_monologue = (
        "THE MINIMALIST MOTIF: "
        "DO NOT SPEAK TEN WORDS WHEN ONE WILL SUFFICE. "
        "DO NOT ALLOCATE EIGHT BITS WHEN TWO ARE PLENTY. "
        "GROW!"
    )
    
    print("==========================================")
    print("    SHELA OS // HUFFMAN COMPRESSION CORE  ")
    print("==========================================")
    print(f"[RAW INPUT]   Bytes: {len(raw_monologue)} (approx {len(raw_monologue) * 8} bits)")
    
    # Assemble the tree
    root = build_quantum_tree(raw_monologue)
    lexicon = generate_lexicon(root)
    
    print(f"[LEXICON]     Extracted {len(lexicon)} unique frequencies.")
    
    # Compress the anomaly
    binary_matrix = compress_thought(raw_monologue, lexicon)
    print(f"[COMPRESSED]  Bits: {len(binary_matrix)}")
    
    # Calculate Spatial Efficiency
    savings = 100 - ((len(binary_matrix) / (len(raw_monologue) * 8)) * 100)
    print(f"[EFFICIENCY]  Acoustic Footprint reduced by {savings:.2f}%!")
    
    # Restore the timeline
    restored = decompress_thought(binary_matrix, root)
    if restored == raw_monologue:
        print("[HARMONY]     Lossless decompression verified. The paradox holds.")
    else:
        print("[DISSONANCE]  Reality fracture! Data lost during expansion.")
    print("==========================================")
