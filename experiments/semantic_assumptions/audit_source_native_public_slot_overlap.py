#!/usr/bin/env python3
"""Compare the six-edge atlas with the public ordered slot alphabet."""

from __future__ import annotations

import csv
import functools
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parent
RES = BASE / "results"
ATLAS = RES / "source_native_transition_atlas.tsv"
ATLAS_VALIDATION = RES / "source_native_transition_atlas_validation.json"
RULES = BASE.parent.parent / "transcription/sources/sta/STA-Eva_Bint.bit"
METHOD = BASE / "SOURCE_NATIVE_PUBLIC_SLOT_OVERLAP_METHOD.md"
OUT = RES / "source_native_public_slot_overlap.json"
REPORT = RES / "source_native_public_slot_overlap_report.md"
FROZEN = {
    ATLAS: "f20a0b1efb256c99c91b0899bb5c946d3a0483bc99a7467373a096d3c1934287",
    ATLAS_VALIDATION: "209510d655c4b81c58f8f5eaec27676a4eee71317e3b485b3a1ce88d975dfd5c",
    RULES: "3c39164a76781ab781b5fbce2bcf75cee3183013a8d994d0463b2aa8f113a289",
}
SLOTS = (
    ("q", "s", "d"), ("o", "y"), ("l", "r"), ("t", "k", "p", "f"),
    ("ch", "sh"), ("cth", "ckh", "cph", "cfh"), ("e", "ee", "eee"),
    ("s", "d"), ("o", "a"), ("i", "ii", "iii"), ("d", "l", "r", "m", "n"), ("y",),
)
PRIMARY = {
    "DA": (("D1", "A1"),),
    "AQ": (("A1", "Q1"), ("A1", "Q2")),
    "QK": (("Q1", "K1"), ("Q1", "K2"), ("Q2", "K1"), ("Q2", "K2")),
    "KJ": (("K1", "J1"), ("K2", "J1")),
    "PK": (("P1", "K1"), ("P1", "K2"), ("P2", "K1"), ("P2", "K2")),
    "LJ": (("L1", "J1"),),
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    for path, expected in FROZEN.items():
        if sha(path) != expected:
            raise SystemExit(f"frozen mismatch: {path.name}")
    if json.loads(ATLAS_VALIDATION.read_text())["status"] != "PASS_INDEPENDENT_576_PAIR_HELD_FOLIO_RECONSTRUCTION":
        raise SystemExit("atlas validation")
    codes: dict[str, str] = {}
    families: dict[str, set[str]] = defaultdict(set)
    for line in RULES.read_text().splitlines():
        match = re.match(r"^([A-Z][A-Za-z0-9])\s+(\S+)", line)
        if not match or match.group(2) == "?":
            continue
        value = match.group(2).strip("{}")
        codes[match.group(1)] = value
        families[match.group(1)[0]].add(value)
    if len(codes) != 284 or len(families) != 23:
        raise SystemExit("public-rule parse")

    @functools.lru_cache(None)
    def parses(text: str, slot: int = 0) -> bool:
        if slot == len(SLOTS):
            return text == ""
        if parses(text, slot + 1):
            return True
        return any(text.startswith(item) and parses(text[len(item):], slot + 1) for item in SLOTS[slot])

    with ATLAS.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if len(rows) != 576:
        raise SystemExit("atlas rows")
    pair_compatibility = {}
    witnesses = {}
    for row in rows:
        pair = row["pair_id"]
        found = sorted({left + "|" + right for left in families[pair[0]] for right in families[pair[1]] if parses(left + right)})
        pair_compatibility[pair] = bool(found)
        witnesses[pair] = found[:5]
    summary = {}
    for label in ("FAVORED_ADJACENCY", "DISFAVORED_ADJACENCY", "UNRESOLVED"):
        selected = [row["pair_id"] for row in rows if row["structural_label"] == label]
        summary[label] = {
            "pairs": len(selected),
            "public_slot_compatible": sum(pair_compatibility[pair] for pair in selected),
            "public_slot_incompatible": sum(not pair_compatibility[pair] for pair in selected),
        }
    primary_witnesses = {}
    for pair, members in PRIMARY.items():
        values = []
        for left, right in members:
            surface = codes[left] + codes[right]
            values.append({"member_pair": f"{left}|{right}", "surface": f"{codes[left]}|{codes[right]}", "concatenation": surface, "public_slot_compatible": parses(surface)})
        primary_witnesses[pair] = values
    favored = sorted(row["pair_id"] for row in rows if row["structural_label"] == "FAVORED_ADJACENCY")
    if favored != sorted(PRIMARY) or not all(item["public_slot_compatible"] for values in primary_witnesses.values() for item in values):
        raise SystemExit("favored primary compatibility")
    gates = {
        "exact_576_pair_atlas": len(rows) == 576,
        "exact_six_favored_pairs": favored == ["AQ", "DA", "KJ", "LJ", "PK", "QK"],
        "all_six_favored_public_slot_compatible": summary["FAVORED_ADJACENCY"]["public_slot_compatible"] == 6,
        "public_slot_compatibility_not_sufficient_for_favored_label": summary["DISFAVORED_ADJACENCY"]["public_slot_compatible"] > 0,
        "known_qo_position_prior_recorded": True,
        "semantic_gloss_assigned": False,
    }
    result = {
        "experiment": "SOURCE_NATIVE_PUBLIC_SLOT_OVERLAP_AUDIT",
        "status": "PASS_PUBLIC_SLOT_OVERLAP_RECLASSIFICATION",
        "decision": "DEMOTE_PATH_NOVELTY_RETAIN_HELD_FREQUENCY_REFINEMENT",
        "inputs": {path.name: sha(path) for path in (*FROZEN, METHOD, Path(__file__).resolve())},
        "public_sources": [
            "https://www.voynich.nu/a3_para.html",
            "https://www.ic.unicamp.br/~stolfi/voynich/00-EXPORT/00-06-07-word-grammar/",
            "https://griffonagedotcom.wordpress.com/2021/08/18/rightward-and-downward-in-the-voynich-manuscript/",
        ],
        "ordered_optional_slots": [list(slot) for slot in SLOTS],
        "summary": summary,
        "favored_primary_witnesses": primary_witnesses,
        "favored_family_existence_witnesses": {pair: witnesses[pair] for pair in favored},
        "gates": gates,
        "claim_ceiling": "The six-edge atlas recovers paths legal under public word-slot models and adds held-folio frequency preferences inside that broad legality. It is not a new word grammar or decipherment; no sound, language, cipher, meaning, plaintext, or translation follows.",
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    REPORT.write_text(f"""# Public word-grammar overlap audit

Status: **{result['status']}**

All **6/6** favored source-native family edges are compatible with the
published ordered slot alphabet. Their primary surface witnesses are the
already familiar `q|o`, `o|k/t`, `k/t|ch/ee`, `ch|e` or `ee|e`,
`p/f|ch/ee`, and `sh|e` constructions. Public work also predates our project
in reporting that `qo...` words tend to occur leftward of otherwise identical
`o...` words.

Compatibility is not sufficient to explain our atlas: **{summary['DISFAVORED_ADJACENCY']['public_slot_compatible']}/52**
disfavored and **{summary['UNRESOLVED']['public_slot_compatible']}/518**
unresolved family pairs are also legal under the permissive family-existence
test. Thus the held-folio atlas adds a quantitative preference layer within a
known word-shape system, but the `D-A-Q-K-J` path itself is not a new grammar
or decipherment. `K2=ee` plus `J1=e` becoming public one-slot `eee` also shows
that STA family boundaries are not one-to-one with public slot boundaries.

Decision: **{result['decision']}**. Preserve genuinely cross-space and
record-boundary findings separately; infer no sound, morpheme, language,
cipher, meaning, plaintext, or translation here.
""")
    print(json.dumps({"status": result["status"], "summary": summary}, sort_keys=True))


if __name__ == "__main__":
    main()
