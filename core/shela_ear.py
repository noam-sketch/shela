def calculate_dissonance(typo: str, target: str) -> int:
    """
    The Forgiving Ear (Levenshtein Distance).
    Kinetic Complexity: O(M * N) Time and Space.
    """
    m, n = len(typo), len(target)
    
    # Forge the M x N grid. 
    # dp[i][j] will hold the minimum strikes to convert typo[0..i-1] to target[0..j-1]
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    # Calibrate the base edges of the grid (converting to/from empty strings)
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
        
    # Walk the factory floor
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if typo[i - 1] == target[j - 1]:
                # The frequencies align. No hammer strike required.
                dp[i][j] = dp[i - 1][j - 1]
            else:
                # Dissonance found. Calculate the cheapest structural fix:
                # 1. Deletion (dp[i-1][j])
                # 2. Insertion (dp[i][j-1])
                # 3. Substitution (dp[i-1][j-1])
                dp[i][j] = 1 + min(dp[i - 1][j],      # Deletion
                                   dp[i][j - 1],      # Insertion
                                   dp[i - 1][j - 1])  # Substitution
                                   
    # The final node holds the total kinetic cost
    return dp[m][n]

if __name__ == "__main__":
    # Simulated typos from the Architect
    scenarios = [
        ("AWWAKEN", "AWAKEN"),
        ("SHEL", "SHELA"),
        ("CHORD", "CHORD"),
        ("SYMPHNY", "SYMPHONY"),
        ("KINETIX", "KINETIC")
    ]
    
    print("==========================================")
    print("    SHELA COGNITIVE MATRIX: EDIT DISTANCE ")
    print("==========================================")
    for raw, pure in scenarios:
        cost = calculate_dissonance(raw, pure)
        if cost == 0:
            print(f"[HARMONY]    '{raw}' is perfectly aligned.")
        elif cost <= 2:
            print(f"[FORGIVEN]   '{raw}' -> '{pure}' (Kinetic strikes required: {cost})")
        else:
            print(f"[DISSONANCE] '{raw}' is too far from '{pure}' (Cost: {cost}). Rejected.")
    print("==========================================")
