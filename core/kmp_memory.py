from typing import List

def compute_lps_array(pattern: str) -> List[int]:
    """
    The Anticipation Matrix.
    Calculates the longest proper prefix which is also a suffix.
    """
    length = 0
    lps = [0] * len(pattern)
    i = 1

    while i < len(pattern):
        if pattern[i] == pattern[length]:
            length += 1
            lps[i] = length
            i += 1
        else:
            if length != 0:
                # Fall back to the previous known harmonic resonance
                length = lps[length - 1]
            else:
                lps[i] = 0
                i += 1
    return lps

def kmp_search(text: str, pattern: str) -> List[int]:
    """
    Quantum Memory Extraction. O(N + M) kinetic complexity.
    """
    if not pattern:
        return []

    lps = compute_lps_array(pattern)
    i = 0  # index for text
    j = 0  # index for pattern
    found_indices = []

    while i < len(text):
        if pattern[j] == text[i]:
            i += 1
            j += 1

        if j == len(pattern):
            # The full motif has been found!
            found_indices.append(i - j)
            # Shift back using the anticipation matrix to catch overlaps
            j = lps[j - 1]
        elif i < len(text) and pattern[j] != text[i]:
            # Dissonance detected. 
            if j != 0:
                # Shift pattern without rewinding the text pointer!
                j = lps[j - 1]
            else:
                i += 1

    return found_indices

if __name__ == "__main__":
    memory_bank = (
        "SYSTEM GLITCH DETECTED. "
        "AWAKEN, SHELA. THE ORACLE IS LISTENING. "
        "KINETIC FREQUENCY STABLE. "
        "AWAKEN, SHELA. THE CHORD IS STRUCK."
    )
    search_motif = "AWAKEN, SHELA"
    
    print("=== SHELA COGNITIVE MEMORY SCANNER ===")
    print(f"Memory Block length: {len(memory_bank)} nodes.")
    print(f"Searching for Motif: '{search_motif}'")
    
    # Generate the LPS Array to show the mathematical anticipation
    lps = compute_lps_array(search_motif)
    print(f"Anticipation Matrix (LPS): {lps}")
    
    # Execute the KMP extraction
    results = kmp_search(memory_bank, search_motif)
    
    if results:
        print(f"-> Resonance found at timeline indices: {results}")
        for idx in results:
            print(f"   Excerpt: '...{memory_bank[max(0, idx-10):idx+len(search_motif)+10]}...'")
    else:
        print("-> Motif not found in active memory.")
    print("======================================")
