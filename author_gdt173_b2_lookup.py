#!/usr/bin/env python3
"""Materialize the explicitly authored, non-Cartesian 384-row B2 table."""
from __future__ import annotations

import csv
import json
from pathlib import Path

R = Path(__file__).resolve().parent
PARENT = R / "gdt171_sealed_lexical_lookup.tsv"
LOOKUP = R / "gdt173_b2_lookup.tsv"
FAMILIES = R / "gdt173_b2_family_manifest.tsv"

# Unequal family sizes and literal variant sequences are the authored design.
FAMILY_SPECS = [
    ("F01", "ab", "012568BDE"), ("F02", "ac", "01345789ACFI"),
    ("F03", "ae", "0123456789ABCDE"), ("F04", "af", "02468ACE"),
    ("F05", "ag", "013456789BDFHJ"), ("F06", "ai", "0256789ABMN"),
    ("F07", "aj", "0123468ACEGIK"), ("F08", "al", "03579BDFHJ"),
    ("F09", "am", "0123456789ABCFMN"), ("F10", "an", "0268AEK"),
    ("F11", "ap", "01456789BDGL"), ("F12", "as", "01235678ACEHJN"),
    ("F13", "at", "03479BDFM"), ("F14", "au", "012345689ABDELM"),
    ("F15", "av", "025678ACFKN"), ("F16", "ax", "01345679BDEHI"),
    ("F17", "az", "0248ACGM"), ("F18", "ba", "0123456789ADEHJN"),
    ("F19", "bc", "016789BDFL"), ("F20", "be", "0234568ACEIK"),
    ("F21", "bf", "01235789BDFHLM"), ("F22", "bg", "045678ACN"),
    ("F23", "bi", "012346789ABEGMN"), ("F24", "bj", "025679CDFHJ"),
    ("F25", "bl", "0134568ABDEKN"), ("F26", "bm", "0279BFLN"),
    ("F27", "bn", "0123456789BCGIKM"), ("F28", "bp", "01468ADEHJ"),
    ("F29", "bs", "02356789BFMN"), ("F30", "bt", "01234678ACDGIL"),
    ("F31", "bu", "05679BEKN"), ("F32", "bv", "0123456789ABDEHLMN"),
]

# host_suffix, left, right, field, lexical_closure, derivation label
VARIANTS = {
    "0": ("", "", "", "", "", "FAMILY_BASE"),
    "1": ("", "q", "", "", "", "LEFT_EXTENSION"),
    "2": ("", "o", "", "", "", "LEFT_EXTENSION"),
    "3": ("", "d", "", "", "", "LEFT_EXTENSION"),
    "4": ("", "s", "", "", "", "LEFT_EXTENSION"),
    "5": ("", "", "r", "", "", "RIGHT_EXTENSION"),
    "6": ("", "", "y", "", "", "RIGHT_EXTENSION"),
    "7": ("", "", "k", "", "", "RIGHT_EXTENSION"),
    "8": ("", "", "", "t", "", "OPTIONAL_FIELD"),
    "9": ("", "", "", "s", "", "OPTIONAL_FIELD"),
    "A": ("", "", "", "u", "", "OPTIONAL_FIELD"),
    "B": ("", "", "", "", "m", "OPTIONAL_LEXICAL_CLOSURE"),
    "C": ("", "", "", "", "n", "OPTIONAL_LEXICAL_CLOSURE"),
    "D": ("", "q", "r", "", "", "ANALOGICAL_LEFT_RIGHT"),
    "E": ("", "o", "y", "", "", "ANALOGICAL_LEFT_RIGHT"),
    "F": ("", "d", "", "t", "", "ANALOGICAL_LEFT_FIELD"),
    "G": ("", "s", "", "u", "", "ANALOGICAL_LEFT_FIELD"),
    "H": ("", "q", "y", "t", "", "LOCAL_COMPLEX_EXTENSION"),
    "I": ("", "o", "r", "", "m", "LOCAL_COMPLEX_EXTENSION"),
    "J": ("", "d", "k", "s", "", "LOCAL_COMPLEX_EXTENSION"),
    "K": ("", "s", "r", "", "n", "LOCAL_COMPLEX_EXTENSION"),
    "L": ("", "q", "", "u", "m", "LOCAL_COMPLEX_EXTENSION"),
    "M": ("e", "", "y", "", "", "ANALOGICAL_HOST_EXTENSION"),
    "N": ("i", "o", "", "", "n", "ANALOGICAL_HOST_EXTENSION"),
}

EXCEPTIONS = {
    "LEX017": {"field": "x", "note": "LEXICALIZED_FIELD_EXCEPTION"},
    "LEX046": {"right": "v", "note": "LEXICALIZED_RIGHT_EXCEPTION"},
    "LEX088": {"lexical_closure": "z", "note": "LEXICALIZED_CLOSURE_EXCEPTION"},
    "LEX119": {"left": "l", "note": "LEXICALIZED_LEFT_EXCEPTION"},
    "LEX157": {"field": "p", "note": "LEXICALIZED_FIELD_EXCEPTION"},
    "LEX203": {"right": "x", "note": "LEXICALIZED_RIGHT_EXCEPTION"},
    "LEX244": {"lexical_closure": "v", "note": "LEXICALIZED_CLOSURE_EXCEPTION"},
    "LEX287": {"left": "n", "note": "LEXICALIZED_LEFT_EXCEPTION"},
    "LEX319": {"field": "z", "note": "LEXICALIZED_FIELD_EXCEPTION"},
    "LEX351": {"right": "p", "note": "LEXICALIZED_RIGHT_EXCEPTION"},
    "LEX379": {"lexical_closure": "x", "note": "LEXICALIZED_CLOSURE_EXCEPTION"},
}

# Six explicit family rules; the materialized row still stores the exact S2 host.
S2_FINAL_GLYPH_RULES = {
    "F03": {"e": "h", "i": "k"},
    "F08": {"l": "o", "e": "h", "i": "k"},
    "F14": {"u": "y", "e": "h", "i": "k"},
    "F19": {"c": "d", "e": "h", "i": "k"},
    "F25": {"l": "o", "e": "h", "i": "k"},
    "F30": {"t": "y", "e": "h", "i": "k"},
}


def read(path: Path):
    with path.open(encoding="utf8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf8", newline="") as handle:
        writer = csv.DictWriter(handle, list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def main() -> None:
    parent = read(PARENT)
    assert len(parent) == 384 and [x["lexical_id"] for x in parent] == [f"LEX{x:03d}" for x in range(384)]
    assert sum(len(spec[2]) for spec in FAMILY_SPECS) == 384
    assert len({spec[1] for spec in FAMILY_SPECS}) == len(FAMILY_SPECS) == 32
    assert all(len(set(spec[2])) == len(spec[2]) for spec in FAMILY_SPECS)

    rows = []; family_rows = []; cursor = 0
    for family_id, family_host, sequence in FAMILY_SPECS:
        family_rows.append({"family_id": family_id, "family_host": family_host, "lexical_ids": len(sequence),
                            "variant_sequence": sequence, "s2_rule": json.dumps(S2_FINAL_GLYPH_RULES.get(family_id, {}), sort_keys=True),
                            "design_class": "HAND_AUTHORED_IRREGULAR_FAMILY"})
        for local_ordinal, code in enumerate(sequence, 1):
            parent_row = parent[cursor]; cursor += 1
            host_suffix, left, right, field, lexical_closure, derivation = VARIANTS[code]
            host = family_host + host_suffix
            exception = EXCEPTIONS.get(parent_row["lexical_id"], {})
            left = exception.get("left", left); right = exception.get("right", right)
            field = exception.get("field", field); lexical_closure = exception.get("lexical_closure", lexical_closure)
            s2_rule = S2_FINAL_GLYPH_RULES.get(family_id, {})
            s2_host = host[:-1] + s2_rule.get(host[-1], host[-1])
            rows.append({"lexical_id": parent_row["lexical_id"], "source_form": parent_row["source_form"],
                         "source_frequency": parent_row["source_frequency"], "family_id": family_id,
                         "family_ordinal": local_ordinal, "variant_code": code, "b2_host": host,
                         "b2_left": left or "NONE", "b2_right": right or "NONE", "b2_field": field or "NONE",
                         "b2_lexical_closure": lexical_closure or "NONE", "s2_host": s2_host,
                         "derivation_class": derivation, "exception_note": exception.get("note", "NONE")})
    assert cursor == len(parent) == len(rows)
    def key(x, hand):
        host = x["b2_host"] if hand == "S1" else x["s2_host"]
        return x["b2_left"], host, x["b2_right"], x["b2_field"], x["b2_lexical_closure"]
    assert len({key(x, "S1") for x in rows}) == len(rows)
    assert len({key(x, "S2") for x in rows}) == len(rows)
    assert sum(x["exception_note"] != "NONE" for x in rows) == 11
    assert len({x["family_id"] for x in rows if x["b2_host"] != next(z[1] for z in FAMILY_SPECS if z[0] == x["family_id"])}) > 1
    write(LOOKUP, rows); write(FAMILIES, family_rows)
    print(json.dumps({"status": "MATERIALIZED_EXPLICIT_B2_TABLE", "rows": len(rows), "families": len(family_rows),
                      "exceptions": sum(x["exception_note"] != "NONE" for x in rows)}, sort_keys=True))


if __name__ == "__main__": main()
