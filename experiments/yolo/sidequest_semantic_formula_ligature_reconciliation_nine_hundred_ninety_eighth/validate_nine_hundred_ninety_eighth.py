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
    codebook = rows("PASS998_159_RECONCILED_CODEBOOK.tsv")
    formulas = rows("PASS998_30_FORMULA_LIGATURES.tsv")
    checks = {
        "codebook_159": len(codebook) == 159,
        "formulas_30": len(formulas) == 30,
        "events_595": sum(int(row["observed_events"]) for row in formulas) == 595,
        "all_exact": all(row["semantic_relation"] == "EXAKT_WURZELKOMPOSITION" for row in formulas),
        "changed_4": sum(row["old_spoken_value_de"] != row["revised_spoken_value_de"] for row in formulas) == 4,
        "old_words_absent": not any(
            old in row["spoken_value_de"]
            for row in codebook
            if row["layer"] == "C_LEARNED_FORMULA_CARD"
            for old in ("SOLLWERT", "EINHEIT", "ARBEITSSATZ", "EINSTELLEN", "MARKIEREN", "START")
        ),
        "sealed_absent": not any("f84" in str(row).lower() for row in codebook + formulas),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "PASS998_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
