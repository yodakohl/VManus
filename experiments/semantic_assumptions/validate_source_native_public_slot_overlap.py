#!/usr/bin/env python3
"""Independent reconstruction of the public slot-overlap reclassification."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parent
RES = BASE / "results"
ATLAS = RES / "source_native_transition_atlas.tsv"
RULES = BASE.parent.parent / "transcription/sources/sta/STA-Eva_Bint.bit"
RESULT = RES / "source_native_public_slot_overlap.json"
REPORT = RES / "source_native_public_slot_overlap_report.md"
OUT = RES / "source_native_public_slot_overlap_validation.json"
OUT_REPORT = RES / "source_native_public_slot_overlap_validation_report.md"
SLOTS = (("q","s","d"),("o","y"),("l","r"),("t","k","p","f"),("ch","sh"),("cth","ckh","cph","cfh"),("e","ee","eee"),("s","d"),("o","a"),("i","ii","iii"),("d","l","r","m","n"),("y",))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def legal(text: str) -> bool:
    states = {text}
    for slot in SLOTS:
        next_states = set(states)
        for remainder in states:
            for item in slot:
                if remainder.startswith(item):
                    next_states.add(remainder[len(item):])
        states = next_states
    return "" in states


def main() -> None:
    if OUT.exists() or OUT_REPORT.exists():
        raise SystemExit("refusing overwrite")
    result = json.loads(RESULT.read_text())
    checks = 0
    def check(value: bool, label: str) -> None:
        nonlocal checks
        checks += 1
        if not value:
            raise AssertionError(label)
    check(sha(ATLAS) == "f20a0b1efb256c99c91b0899bb5c946d3a0483bc99a7467373a096d3c1934287", "atlas hash")
    check(sha(RULES) == "3c39164a76781ab781b5fbce2bcf75cee3183013a8d994d0463b2aa8f113a289", "rules hash")
    members = defaultdict(set); codes = {}
    for line in RULES.read_text().splitlines():
        match = re.match(r"^([A-Z][A-Za-z0-9])\s+(\S+)", line)
        if match and match.group(2) != "?":
            value = match.group(2).strip("{}")
            codes[match.group(1)] = value
            members[match.group(1)[0]].add(value)
    check(len(codes) == 284 and len(members) == 23, "rule inventory")
    rows = list(csv.DictReader(ATLAS.open(), delimiter="\t"))
    check(len(rows) == 576 and len({row["pair_id"] for row in rows}) == 576, "atlas inventory")
    by_label = defaultdict(list)
    compatibility = {}
    for row in rows:
        pair = row["pair_id"]
        compatibility[pair] = any(legal(left + right) for left in members[pair[0]] for right in members[pair[1]])
        by_label[row["structural_label"]].append(pair)
    summary = {label: {"pairs": len(pairs), "public_slot_compatible": sum(compatibility[pair] for pair in pairs), "public_slot_incompatible": sum(not compatibility[pair] for pair in pairs)} for label, pairs in by_label.items()}
    check(summary == result["summary"], "summary")
    check(summary == {"FAVORED_ADJACENCY":{"pairs":6,"public_slot_compatible":6,"public_slot_incompatible":0},"DISFAVORED_ADJACENCY":{"pairs":52,"public_slot_compatible":46,"public_slot_incompatible":6},"UNRESOLVED":{"pairs":518,"public_slot_compatible":239,"public_slot_incompatible":279}}, "exact counts")
    primaries = {"DA":[("D1","A1")],"AQ":[("A1","Q1"),("A1","Q2")],"QK":[("Q1","K1"),("Q1","K2"),("Q2","K1"),("Q2","K2")],"KJ":[("K1","J1"),("K2","J1")],"PK":[("P1","K1"),("P1","K2"),("P2","K1"),("P2","K2")],"LJ":[("L1","J1")]}
    for pair, pairs in primaries.items():
        check(all(legal(codes[left] + codes[right]) for left, right in pairs), f"primary {pair}")
    check(codes["D1"] + codes["A1"] == "qo", "qo")
    check(codes["K2"] + codes["J1"] == "eee" and legal("eee"), "within-slot boundary")
    check(result["status"] == "PASS_PUBLIC_SLOT_OVERLAP_RECLASSIFICATION", "status")
    check(result["decision"] == "DEMOTE_PATH_NOVELTY_RETAIN_HELD_FREQUENCY_REFINEMENT", "decision")
    check(all(result["gates"].values()) is False, "semantic false retained")
    check("not a new grammar" in REPORT.read_text(), "report ceiling")
    # Mutations.
    check(not legal("oq"), "reverse mutation")
    altered = [list(slot) for slot in SLOTS]; altered[0].remove("q")
    check(altered != result["ordered_optional_slots"], "slot mutation")
    check({**summary, "FAVORED_ADJACENCY": {**summary["FAVORED_ADJACENCY"], "public_slot_compatible": 5}} != result["summary"], "count mutation")
    validation = {
        "experiment": "SOURCE_NATIVE_PUBLIC_SLOT_OVERLAP_VALIDATION",
        "status": "PASS_INDEPENDENT_PUBLIC_SLOT_OVERLAP_RECONSTRUCTION",
        "checks": checks,
        "inputs": {ATLAS.name: sha(ATLAS), RULES.name: sha(RULES), RESULT.name: sha(RESULT), REPORT.name: sha(REPORT), Path(__file__).name: sha(Path(__file__).resolve())},
        "summary": summary,
        "maximum_numeric_delta": 0.0,
        "claim_ceiling": "Validates novelty reclassification only; no sound, word, language, cipher, meaning, plaintext, or translation follows.",
    }
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n")
    OUT_REPORT.write_text(f"""# Public slot-overlap validation

Status: **{validation['status']}**

Independent iterative parsing reconstructs all 284 basic STA definitions, all
576 atlas pairs, the 6/6 favored, 46/52 disfavored, and 239/518 unresolved
compatibility counts, every primary witness, decisions, and mutations in
**{checks}** checks with zero discrepancy.

This validates a novelty correction only. No sound, word, language, cipher,
meaning, plaintext, or translation follows.
""")
    print(json.dumps({"status": validation["status"], "checks": checks}, sort_keys=True))


if __name__ == "__main__":
    main()
