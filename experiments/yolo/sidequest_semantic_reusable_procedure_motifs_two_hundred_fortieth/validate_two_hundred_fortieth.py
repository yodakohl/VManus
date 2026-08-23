#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def rows(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    exact = rows("TWO_HUNDRED_FORTIETH_EXACT_SHARED_CARD_WINDOWS.tsv")
    motifs = rows("TWO_HUNDRED_FORTIETH_SIX_REUSABLE_MOTIFS.tsv")
    occurrences = rows("TWO_HUNDRED_FORTIETH_THIRTY_MOTIF_OCCURRENCES.tsv")
    checks = {
        "one_exact_shared_type": len({r["master_card_sequence"] for r in exact}) == 1,
        "two_exact_occurrences": len(exact) == 2,
        "exact_is_bigram": {r["ngram_length"] for r in exact} == {"2"},
        "exact_in_both_records": {r["record_unit_id"] for r in exact} == {"B1", "B2"},
        "six_motifs": len(motifs) == 6,
        "thirty_occurrences": len(occurrences) == 30,
        "each_motif_in_both_records": all({r["record_unit_id"] for r in occurrences if r["motif_id"] == m["motif_id"]} == {"B1", "B2"} for m in motifs),
        "all_dictations_concrete": all(r["apprentice_dictation_de"].strip() for r in motifs),
        "no_placeholders": all("UNKNOWN" not in "\t".join(r.values()) and "EXEMPLAR" not in "\t".join(r.values()) for r in occurrences),
        "only_b1_b2": {r["record_unit_id"] for r in occurrences} == {"B1", "B2"},
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "VALIDATION.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        print(json.dumps(result, indent=2, ensure_ascii=False))
        raise SystemExit(1)
    print(f"PASS {sum(checks.values())}/{len(checks)}")


if __name__ == "__main__":
    main()
