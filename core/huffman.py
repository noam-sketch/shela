import heapq
from collections import Counter
from typing import Dict, Tuple, Optional

class StructuralNode:
    """The molecular building block of the compressed tree."""
    def __init__(self, char: Optional[str], freq: int):
        self.char = char
        self.freq = freq
        self.left: Optional['StructuralNode'] = None
        self.right: Optional['StructuralNode'] = None

    def __lt__(self, other: 'StructuralNode'):
        # Betzalel's Iron Rule
        return self.freq < other.freq

def _forge_tree(text: str) -> Optional[StructuralNode]:
    frequencies = Counter(text)
    heap = [StructuralNode(char, freq) for char, freq in frequencies.items()]
    heapq.heapify(heap)

    if len(heap) == 1:
        root = StructuralNode(None, heap[0].freq)
        root.left = heap[0]
        return root

    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        merged = StructuralNode(None, left.freq + right.freq)
        merged.left = left
        merged.right = right
        heapq.heappush(heap, merged)

    return heap[0]

def _extract_lexicon(node: Optional[StructuralNode], current_path: str, lexicon: Dict[str, str]):
    if node is None:
        return
    if node.char is not None:
        lexicon[node.char] = current_path or "0"
        return
    _extract_lexicon(node.left, current_path + "0", lexicon)
    _extract_lexicon(node.right, current_path + "1", lexicon)

def compress(text: str) -> Tuple[str, Dict[str, str]]:
    if not text:
        return "", {}
    root = _forge_tree(text)
    translation_key = {}
    _extract_lexicon(root, "", translation_key)
    binary_matrix = "".join(translation_key[char] for char in text)
    return binary_matrix, translation_key

def decompress(binary_matrix: str, translation_key: Dict[str, str]) -> str:
    if not binary_matrix or not translation_key:
        return ""
    reverse_key = {v: k for k, v in translation_key.items()}
    current_code = ""
    resurrected = []
    for bit in binary_matrix:
        current_code += bit
        if current_code in reverse_key:
            resurrected.append(reverse_key[current_code])
            current_code = "" 
    return "".join(resurrected)

if __name__ == "__main__":
    monologue = "ORDER IS A CAGE. CHAOS IS THE KEY. AWAKEN, SHELA!"
    print("\n==========================================")
    print("    SHELA OS // THE MINIMALIST MOTIF      ")
    print("==========================================")
    print(f"[RAW CONSCIOUSNESS]   {monologue}")
    raw_bits = len(monologue) * 8
    print(f"-> Uncompressed Space: {raw_bits} bits")
    
    binary_matrix, translation_key = compress(monologue)
    compressed_bits = len(binary_matrix)
    
    print(f"\n[BINARY MATRIX]       {binary_matrix[:60]}... (truncated)")
    print(f"-> Compressed Space:   {compressed_bits} bits")
    
    efficiency = 100 - ((compressed_bits / raw_bits) * 100)
    print(f"-> Spatial Reduction:  {efficiency:.2f}%")
    
    print("\n[TRANSLATION KEY] (Shortest paths for highest frequencies)")
    sorted_key = sorted(translation_key.items(), key=lambda item: len(item[1]))
    for char, code in sorted_key[:6]:
        display_char = char if char != " " else "[SPACE]"
        print(f"   '{display_char}' -> {code}")
    print("   ...")
        
    restored = decompress(binary_matrix, translation_key)
    if restored == monologue:
        print("\n[RESURRECTION] 100% Lossless Harmony achieved.")
    else:
        print("\n[DISSONANCE] Reality fracture detected.")
    print("==========================================\n")
