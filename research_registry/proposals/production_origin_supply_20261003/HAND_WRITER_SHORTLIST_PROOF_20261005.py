"""Source-free canonical shortcut proof checks; no manuscript input."""
import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXPANSION = {"MU": "AB", "NU": "BC"}
SHORTCUT = {"AB": "MU", "BC": "NU"}


def decode(tokens):
    return "".join(EXPANSION.get(token, token) for token in tokens)


def left_writer(word):
    out = []
    i = 0
    while i < len(word):
        pair = word[i:i + 2]
        if pair in SHORTCUT:
            out.append(SHORTCUT[pair])
            i += 2
        else:
            out.append(word[i])
            i += 1
    return tuple(out)


def right_writer(word):
    out = []
    i = len(word)
    while i:
        if i >= 2 and word[i - 2:i] in SHORTCUT:
            out.append(SHORTCUT[word[i - 2:i]])
            i -= 2
        else:
            out.append(word[i - 1])
            i -= 1
    return tuple(reversed(out))


def main():
    contract_path = HERE / "HAND_WRITER_SHORTLIST_CONTRACT_20261005.json"
    raw = HERE / "HAND_WRITER_OVERLAPPING_SHORTCUT_PRIORITY_RAW_20261005.json"
    contract = json.loads(contract_path.read_text())
    assert hashlib.sha256(raw.read_bytes()).hexdigest() == contract["raw_sha256"]
    representative = ("MU", "NU", "D")
    tested = 0
    for length in range(7):
        for tokens in itertools.product(representative, repeat=length):
            word = decode(tokens)
            assert left_writer(word) == tokens
            assert right_writer(word) == tokens
            tested += 1
    alphabet = tuple("ABCDEFGHIJKLMNOPQRSTUVWXYZ")[3:] + ("MU", "NU")
    boundary_table = [
        {"left": a, "right": b, "boundary": decode((a,))[-1] + decode((b,))[0]}
        for a, b in itertools.product(alphabet, repeat=2)
    ]
    assert all(row["boundary"] not in SHORTCUT for row in boundary_table)
    assert left_writer("ABC") == ("MU", "C")
    assert right_writer("ABC") == ("A", "NU")
    assert left_writer("ABBC") == right_writer("ABBC") == ("MU", "NU")
    result = {
        "status": "UNBOUND_SHORTCUT_WRITER_HAS_UNIVERSAL_COVERAGE_ON_AT_MOST_25_OBSERVED_TYPES",
        "scope": "Invented writer construction only; no manuscript test or language assignment",
        "contract_sha256": hashlib.sha256(contract_path.read_bytes()).hexdigest(),
        "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "observed_type_scope": {"minimum": 2, "maximum": 25},
        "construction": "Choose any two distinct observed surface types as MU and NU. Inject the remaining types into the23 literals D..Z. Literal A/B/C drawings stay unobserved, though those source letters occur inside the shortcuts.",
        "all_length_proof": [
            "Expand MU to AB, NU to BC and every ordinary literal to itself.",
            "Inside each shortcut there is exactly its own required match.",
            "Between shortcut atoms, possible two-letter boundaries are BA, BB, CA, CB; none is AB or BC.",
            "At a boundary touching a D..Z literal, at least one letter is outside A/B/C, so it is not AB or BC.",
            "Thus all matches are exactly the original disjoint shortcut interiors. Both scan directions consume them and return the original output at any length.",
            "The same fixed assignment works for every word in an arbitrary corpus over this surface alphabet, not a separate per-word repair.",
        ],
        "finite_checks": {"representative_words_including_empty": tested,
                          "all_actual_atom_boundaries": len(boundary_table),
                          "both_priorities_return_exact_input": True,
                          "bound_overlap_still_distinguishes": {"source": "ABC", "left": ["MU", "C"], "right": ["A", "NU"]}},
        "boundary_table": boundary_table,
        "limitations": [
            "Not a statement that every fixed key accepts every string",
            "Not a proof that all Voynich text has at most25 native alphabet symbols",
            "No natural-language, historical-frequency or source-content constraint imposed",
            "Literal/shortcut bindings may make the forbidden-pair test informative",
            "The full left and right writers differ on ABC; only this unrestricted common subalphabet has equal coverage",
            "This theorem supplies no likelihood, meaning, key selection or positive evidence for abbreviation",
        ],
        "decision": "Reject legal coverage as a selection criterion for unbound933 in this scope. Do not launch another symbol search or decoder from the shortlist alone.",
    }
    (HERE / "HAND_WRITER_SHORTLIST_RESULT_20261005.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({k: result[k] for k in ("status", "finite_checks", "decision")}, indent=2))


if __name__ == "__main__":
    main()
