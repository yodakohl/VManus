#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


OUT = Path(__file__).resolve().parent


def read_tsv(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    entries = read_tsv("PASS964_TIERED_122_ENTRY_CODEBOOK.tsv")
    phases = read_tsv("PASS964_FOUR_PHASE_TRAINING.tsv")
    tiers = Counter(row["entry_tier"] for row in entries)
    local = {row["recognition_form"] for row in entries if row["entry_tier"] == "D_LOCAL_DIAGRAM_SIGN"}
    checks = {
        "entries_122": len(entries) == 122,
        "common_roots_37": tiers["A_COMMON_PRODUCTIVE_ROOT"] == 37,
        "rare_roots_16": tiers["B_RARE_PRODUCTIVE_EXTENSION"] == 16,
        "formula_cards_66": tiers["C_LEARNED_FORMULA_CARD"] == 66,
        "local_signs_3": tiers["D_LOCAL_DIAGRAM_SIGN"] == 3,
        "local_sign_identity": local == {"LOCAL_CHAR_Z", "S_LABEL", "Z_ADDR"},
        "local_signs_zero_productive": all(row["productive_composition_uses"] == "0" for row in entries if row["entry_tier"] == "D_LOCAL_DIAGRAM_SIGN"),
        "all_other_roots_productive": all(int(row["productive_composition_uses"]) > 0 for row in entries if row["entry_type"] == "ROOT_OR_LOCAL_SIGN" and row["entry_tier"] != "D_LOCAL_DIAGRAM_SIGN"),
        "phases_4": len(phases) == 4 and sum(int(row["entries"]) for row in phases) == 122,
        "no_sealed_pages": not any("f84" in str(row).lower() for row in entries + phases),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "PASS964_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
