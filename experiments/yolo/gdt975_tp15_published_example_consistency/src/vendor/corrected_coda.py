def classify_token_chars_v2(
    eva_chars: List[str],
    coda_table: CodaTable,
) -> List[Tuple[str, str]]:
    """Corrected character classification.

    Calls the original classify_token_chars, then reclassifies EVA 'i'
    as SYLLABIC in non-final positions.  Phase 59 Inv 3 found that 'i'
    produces 0 meaningful coda hits (5 total hits out of 2,807 tokens).
    """
    classified = classify_token_chars(eva_chars, coda_table)

    # Post-process: 'i' at non-final position -> SYLLABIC
    corrected = []
    for idx, (role, char) in enumerate(classified):
        if char == 'i' and role == 'CODA_MARKER' and idx < len(classified) - 1:
            corrected.append(('SYLLABIC', char))
        else:
            corrected.append((role, char))

    return corrected

def decode_token_cvc_v2(
    token: str,
    assignment: Dict[str, str],
    eva_to_triple: Dict[str, str],
    coda_table: CodaTable,
) -> CvcDecodeResult:
    """Decode an EVA token using corrected CVC rules.

    Same algorithm as decode_token_cvc but uses classify_token_chars_v2.
    """
    eva_chars = tokenize_eva_chars(token)
    if not eva_chars:
        return CvcDecodeResult(
            token=token, eva_chars=[], char_roles=[],
            decoded_cv='', decoded_cvc='',
        )

    classified = classify_token_chars_v2(eva_chars, coda_table)
    roles = [role for role, _ in classified]

    # Build CVC output
    output_parts: List[Tuple[str, str]] = []
    for role, char in classified:
        if role == 'SYLLABIC':
            triple = eva_to_triple.get(char)
            syl = assignment.get(triple, '?') if triple else '?'
            output_parts.append(('CV', syl))
        elif role == 'CODA_MARKER':
            coda = get_coda(char, coda_table)
            if coda and output_parts and output_parts[-1][0] in ('CV', 'CVC'):
                prev_type, prev_val = output_parts[-1]
                output_parts[-1] = ('CVC', prev_val + coda)
            elif coda:
                output_parts.append(('ORPHAN', coda))

    decoded_cvc = ''.join(val for _, val in output_parts)

    # CV-only decode (strip modifiers)
    cv_parts = []
    for role, char in classified:
        if role == 'SYLLABIC':
            triple = eva_to_triple.get(char)
            syl = assignment.get(triple, '?') if triple else '?'
            cv_parts.append(syl)
    decoded_cv = ''.join(cv_parts)

    return CvcDecodeResult(
        token=token,
        eva_chars=eva_chars,
        char_roles=roles,
        decoded_cv=decoded_cv,
        decoded_cvc=decoded_cvc,
    )
