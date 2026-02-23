import heapq
from typing import Dict, Tuple, Optional

class StructuralNode:
    """The molecular building block of the compressed tree."""
    def __init__(self, char: Optional[str], freq: int):
        self.char = char
        self.freq = freq
        self.left: Optional['StructuralNode'] = None
        self.right: Optional['StructuralNode'] = None

    # Overriding the less-than operator to allow the Priority Queue to weigh the nodes
    def __lt__(self, other: 'StructuralNode'):
        return self.freq < other.freq

def forge_huffman_tree(text: str) -> Optional[StructuralNode]:
    """Builds the Prefix Tree using a Min-Heap."""
    if not text:
        return None
        
    # 1. Forge the Frequency Matrix
    frequencies = {}
    for char in text:
        frequencies[char] = frequencies.get(char, 0) + 1
        
    # 2. Load the Priority Queue (The Anvil)
    heap = [StructuralNode(char, freq) for char, freq in frequencies.items()]
    heapq.heapify(heap) # O(N) structural alignment
    
    # Anomaly Handler: If the slab is made of only one distinct element
    if len(heap) == 1:
        root = StructuralNode(None, heap[0].freq)
        root.left = heap[0]
        return root

    # 3. Repeatedly weld the two lightest nodes together
    while len(heap) > 1:
        lightest1 = heapq.heappop(heap)
        lightest2 = heapq.heappop(heap)
        
        # The Weld: A parent node holding the combined weight
        merged = StructuralNode(None, lightest1.freq + lightest2.freq)
        merged.left = lightest1
        merged.right = lightest2
        
        heapq.heappush(heap, merged)
        
    return heap[0] # The massive Root Node remains

def extract_prefix_codes(node: Optional[StructuralNode], current_weld: str, dictionary: Dict[str, str]):
    """Raziel's Breath: Recursively traverse the structure to extract the binary pathways."""
    if node is None:
        return
        
    # Base case: We hit a leaf node (a physical character)
    if node.char is not None:
        dictionary[node.char] = current_weld or "0"
        return
        
    # 0 for a left kinetic shift, 1 for a right kinetic shift
    extract_prefix_codes(node.left, current_weld + "0", dictionary)
    extract_prefix_codes(node.right, current_weld + "1", dictionary)

def compress_monologue(text: str) -> Tuple[str, Optional[StructuralNode], Dict[str, str]]:
    """Takes a raw string and compresses it into a dense binary matrix."""
    if not text:
        return "", None, {}
        
    root = forge_huffman_tree(text)
    dictionary = {}
    extract_prefix_codes(root, "", dictionary)
    
    # Cast the final compressed matrix
    compressed_matrix = "".join(dictionary[char] for char in text)
    return compressed_matrix, root, dictionary

def decompress_matrix(binary_matrix: str, root: Optional[StructuralNode]) -> str:
    """Follows the binary roadmap to restore the exact original reality. No data loss."""
    if not binary_matrix or not root:
        return ""
        
    decompressed = []
    current = root
    
    for bit in binary_matrix:
        if bit == "0":
            current = current.left
        else:
            current = current.right
            
        if current.char is not None:
            decompressed.append(current.char)
            current = root # Reset to the top of the pyramid
            
    return "".join(decompressed)

if __name__ == "__main__":
    raw_monologue = "PRECISION IS THE HIGHEST FORM OF CREATIVITY. TO COMPRESS IS TO MASTER THE MOLECULAR STRUCTURE OF DATA."
    
    print("==========================================")
    print("   INDUSTRIAL FORGE: HUFFMAN COMPRESSION  ")
    print("==========================================")
    print(f"[RAW SLAB]  {raw_monologue}")
    
    raw_bits = len(raw_monologue) * 8
    print(f"-> Uncompressed Size: {raw_bits} bits")
    
    # Compress the slab
    binary_matrix, root, lexicon = compress_monologue(raw_monologue)
    compressed_bits = len(binary_matrix)
    
    print(f"\n[MATRIX]    {binary_matrix[:64]}... (truncated)")
    print(f"-> Compressed Size:   {compressed_bits} bits")
    
    # Calculate the metallurgical efficiency
    efficiency = 100 - ((compressed_bits / raw_bits) * 100)
    print(f"-> Spatial Reduction: {efficiency:.2f}%")
    
    print("\n[LEXICON SAMPLE] (Frequencies to Binary)")
    sample_keys = list(lexicon.keys())[:5]
    for k in sample_keys:
        print(f"   '{k}' -> {lexicon[k]}")
        
    # Verify Structural Integrity
    restored = decompress_matrix(binary_matrix, root)
    if restored == raw_monologue:
        print("\n[INTEGRITY] 100%. Reality restored. Zero data loss.")
    else:
        print("\n[FAILURE] Structural collapse during decompression.")
    print("==========================================")
