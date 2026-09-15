EVA_LIGATURES = [
    'sh', 'ch', 'cth', 'ckh', 'cph', 'cfh',
    'iin', 'iiin', 'aiin', 'aiiin',
    'ol', 'or', 'al', 'ar',
    'qo', 'qok', 'qot',
    'dy', 'ey',
]

EVA_LIGATURES_SORTED = sorted(EVA_LIGATURES, key=len, reverse=True)

def tokenize_eva_chars(token: str) -> List[str]:
    """
    Parse a single EVA token into its constituent EVA characters/ligatures.
    Uses longest-match-first to handle multi-character sequences like
    'sh', 'ch', 'cth', 'ckh', 'aiin', etc.

    Example: 'shody' -> ['sh', 'o', 'd', 'y']
             'cthres' -> ['cth', 'r', 'e', 's']
    """
    chars = []
    i = 0
    while i < len(token):
        matched = False
        # Try longest ligatures first
        for lig in EVA_LIGATURES_SORTED:
            if token[i:i+len(lig)] == lig:
                chars.append(lig)
                i += len(lig)
                matched = True
                break
        if not matched:
            chars.append(token[i])
            i += 1
    return chars
