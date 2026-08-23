#!/usr/bin/env python3
"""Validate four-hand surface rendering against the registered prose inventory."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
LEDGER = ROOT / "experiments/yolo/sidequest_semantic_final_productive_cards_nineteenth_edition/NINETEENTH_776_SPEAKABLE_LEDGER.tsv"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    profiles = rows(OUT / "FIFTY_NINTH_4_SCRIBE_PROFILES.tsv")
    copies = rows(OUT / "FIFTY_NINTH_464_HAND_COPIES.tsv")
    choices = rows(OUT / "FIFTY_NINTH_1524_GROUP_CHOICES.tsv")
    safety = rows(OUT / "FIFTY_NINTH_8_SAFE_UNSAFE_RULES.tsv")
    prose = [row for row in rows(LEDGER) if row["register"] == "PROSE"]
    registered = defaultdict(set)
    for row in prose:
        registered[row["atom_sequence"]].add(row["visible_surface"])
    profile_counts = Counter(row["scribe_profile"] for row in copies)
    checks = {
        "four_profiles": len(profiles) == 4,
        "four_hundred_sixty_four_copies": len(copies) == 464 and profile_counts == Counter({row["scribe_profile"]: 116 for row in profiles}),
        "one_thousand_five_hundred_twenty_four_choices": len(choices) == 1524,
        "all_selected_surfaces_registered_for_atom": all(row["selected_surface"] in registered[row["atom_sequence"]] for row in choices),
        "all_atom_identities_preserved": all(row["atom_identity_preserved"] == "YES" for row in choices),
        "all_readbacks_unchanged": all(row["semantic_readback_changed"] == "NO" for row in copies),
        "copy_group_sums": sum(int(row["group_count"]) for row in copies) == 1524,
        "eight_rules_balanced": len(safety) == 8 and Counter(row["classification"] for row in safety) == Counter({"SAFE": 4, "UNSAFE": 4}),
        "fixed_pages_sealed": all("f84" not in "\t".join(row.values()).lower() for row in copies + choices),
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    result = {"status": status, "checks": checks, "copy_counts": dict(profile_counts)}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if status != "PASS":
        raise SystemExit(1)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
