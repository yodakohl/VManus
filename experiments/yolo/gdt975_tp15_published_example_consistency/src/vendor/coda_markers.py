@dataclass
class CodaTable:
    """Maps stroke types to coda consonants."""
    variant: str                          # 'primary' or 'alternate'
    stroke_to_coda: Dict[str, str]        # last_stroke -> coda consonant
    eva_modifiers: Dict[str, str]         # EVA char -> last_stroke
    modifier_confidence: Dict[str, str]   # EVA char -> MODIFIER/AMBIGUOUS
    n_modifier: int
    n_ambiguous_as_coda: int
    ambiguous_chars: List[str]            # AMBIGUOUS chars that can act as coda

@dataclass
class CvcDecodeResult:
    """Decode result for a single token."""
    token: str
    eva_chars: List[str]
    char_roles: List[str]        # SYLLABIC / CODA_MARKER per char
    decoded_cv: str              # old CV-only decode (strip modifiers)
    decoded_cvc: str             # new CVC decode

SIMPLE_GALLOWS = {'k', 't', 'p', 'f'}

def get_coda(eva_char: str, coda_table: CodaTable) -> Optional[str]:
    """Return the coda consonant for an EVA modifier character.

    Returns None if the character is not in the coda table.
    """
    last_stroke = coda_table.eva_modifiers.get(eva_char)
    if last_stroke is None:
        return None
    return coda_table.stroke_to_coda.get(last_stroke)

def classify_token_chars(
    eva_chars: List[str],
    coda_table: CodaTable,
) -> List[Tuple[str, str]]:
    """Classify each EVA character in a token as SYLLABIC or CODA_MARKER.

    Rules:
    1. The first character of a token is always SYLLABIC (words don't start
       with a coda).
    2. Simple gallows (k, t, p, f) are always SYLLABIC.
    3. Characters classified as MODIFIER by Phase 16 -> CODA_MARKER.
    4. AMBIGUOUS characters -> CODA_MARKER if they follow a SYLLABIC char;
       SYLLABIC otherwise (conservative default).
    5. All other characters -> SYLLABIC.

    Returns list of (role, eva_char) tuples.
    """
    classified: List[Tuple[str, str]] = []

    for idx, char in enumerate(eva_chars):
        # Rule 1: first char is always syllabic
        if idx == 0:
            classified.append(('SYLLABIC', char))
            continue

        # Rule 2: simple gallows are always syllabic
        if char in SIMPLE_GALLOWS:
            classified.append(('SYLLABIC', char))
            continue

        conf = coda_table.modifier_confidence.get(char)

        # Rule 3: MODIFIER -> CODA_MARKER
        if conf == 'MODIFIER':
            classified.append(('CODA_MARKER', char))
            continue

        # Rule 4: AMBIGUOUS -> CODA_MARKER only if the char has a valid
        # coda stroke AND follows a SYLLABIC char.  Otherwise SYLLABIC.
        if conf == 'AMBIGUOUS':
            last_stroke = coda_table.eva_modifiers.get(char)
            has_valid_coda = (last_stroke is not None
                              and last_stroke in coda_table.stroke_to_coda)
            if has_valid_coda and classified and classified[-1][0] == 'SYLLABIC':
                classified.append(('CODA_MARKER', char))
            else:
                classified.append(('SYLLABIC', char))
            continue

        # Rule 5: everything else -> SYLLABIC
        classified.append(('SYLLABIC', char))

    return classified
