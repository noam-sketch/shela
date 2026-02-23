class QuantumNode:
    def __init__(self):
        # The branching paths of future letters
        self.frequencies = {}
        # The marker of a completed word
        self.is_chord_resolved = False

class QuantumLexicon:
    """
    The Trie (Prefix Tree).
    Kinetic Complexity: O(L) Time per operation. Space is shared across common prefixes.
    """
    def __init__(self):
        # The silence before the choir breathes
        self.root = QuantumNode()

    def insert(self, word: str) -> None:
        current_node = self.root
        for char in word:
            if char not in current_node.frequencies:
                current_node.frequencies[char] = QuantumNode()
            # Traverse deeper into the branch
            current_node = current_node.frequencies[char]
        # The final note is struck; the word is anchored.
        current_node.is_chord_resolved = True

    def search(self, word: str) -> bool:
        current_node = self.root
        for char in word:
            if char not in current_node.frequencies:
                return False
            current_node = current_node.frequencies[char]
        # We must ensure the melody ended here, and wasn't just a prefix.
        return current_node.is_chord_resolved

    def starts_with(self, prefix: str) -> bool:
        current_node = self.root
        for char in prefix:
            if char not in current_node.frequencies:
                return False
            current_node = current_node.frequencies[char]
        # The prefix exists in the acoustic space.
        return True

# --- THE LEXICON CONSOLE ---
if __name__ == "__main__":
    lexicon = QuantumLexicon()
    words_to_learn = ["HARMONY", "HARMONIC", "CADENZA", "CRESCENDO", "CHORD"]
    
    print("[RAZIEL] The Choir is breathing in the following motifs:")
    for w in words_to_learn:
        lexicon.insert(w)
        print(f"  -> Inserted: {w}")
        
    print("\n[RAZIEL] Auditioning the Lexicon Matrix:")
    print(f"  ? Search 'HARMONY':    {lexicon.search('HARMONY')}")
    print(f"  ? Search 'HARMON':     {lexicon.search('HARMON')} (Prefix only)")
    print(f"  ? Starts with 'CRES':  {lexicon.starts_with('CRES')}")
    print(f"  ? Starts with 'CHO':   {lexicon.starts_with('CHO')}")
    print(f"  ? Search 'DISSONANCE': {lexicon.search('DISSONANCE')}")
