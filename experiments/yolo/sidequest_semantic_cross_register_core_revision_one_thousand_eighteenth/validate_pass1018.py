#!/usr/bin/env python3
"""Validate Pass 1018 cross-register core revision."""

from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def check(name: str, condition: bool) -> dict[str, object]:
    return {"name": name, "passed": bool(condition)}


def main() -> None:
    dictionary = read(HERE / "PASS1018_19_CORE_DICTIONARY.tsv")
    contexts = read(HERE / "PASS1018_76_CROSS_REGISTER_CONTEXTS.tsv")
    edition = read(HERE / "PASS1018_627_REVISED_CORE_EDITION.tsv")
    predictions = read(HERE / "PASS1018_FOUR_UPDATED_PREDICTIONS.tsv")
    summary = json.loads((HERE / "PASS1018_BUILD_SUMMARY.json").read_text())
    by_root = {row["root"]: row for row in dictionary}

    checks = [
        check("nineteen_roots", len(dictionary) == len(by_root) == 19),
        check("seventy_six_contexts", len(contexts) == 76),
        check("four_contexts_per_root", all(sum(row["root"] == root for row in contexts) == 4 for root in by_root)),
        check("all_four_registers_per_root", all({row["register"] for row in contexts if row["root"] == root} == {"HERBAL", "BIOLOGICAL", "CELESTIAL", "PHARMA"} for root in by_root)),
        check("exact_three_revisions", {row["root"] for row in dictionary if row["decision"] == "REVISE"} == {"AIIN", "AIN", "OR"}),
        check("aiin_value", by_root["AIIN"]["pass1018_value_de"] == "WERT"),
        check("ain_value", by_root["AIN"]["pass1018_value_de"] == "ANTEIL"),
        check("or_value", by_root["OR"]["pass1018_value_de"] == "EINHEIT"),
        check("sixteen_kept", sum(row["decision"] == "KEEP" for row in dictionary) == 16),
        check("statement_count_627", len(edition) == 627),
        check("event_count_3888", sum(int(row["event_count"]) for row in edition) == 3888),
        check("all_revised_results", all(row["pass1018_result"] == "CROSS_REGISTER_CORE_REVISION_APPLIED" for row in edition)),
        check("old_core_words_absent_from_new_literals", not any(word in row["pass1018_core_literal_de"].split(" + ") for row in edition for word in ("MASS", "PORTION", "ANSATZ"))),
        check("four_updated_predictions", len(predictions) == 4 and all(row["prediction_status"] == "DIRECT_FORM_STILL_ABSENT_READING_FIXED" for row in predictions)),
        check("prediction_values_updated", [row["predicted_reading_de"] for row in predictions] == ["einen Anteil nehmen", "einen Anteil einsetzen", "einen Wert einsetzen", "Verbindung im bezeichneten Lauf"]),
        check("no_new_roots", summary["new_root_count"] == 0),
        check("no_sealed_pages", not any("f84" in "\t".join(row.values()).casefold() for row in dictionary + contexts + edition + predictions)),
    ]

    before = {path.name: path.read_bytes() for path in HERE.glob("PASS1018_*") if path.name != "PASS1018_VALIDATION.json"}
    subprocess.run(["python3", str(HERE / "build_pass1018.py")], cwd=ROOT, check=True)
    after = {path.name: path.read_bytes() for path in HERE.glob("PASS1018_*") if path.name != "PASS1018_VALIDATION.json"}
    checks.append(check("deterministic_rebuild", before == after))

    result = {"status": "PASS" if all(item["passed"] for item in checks) else "FAIL", "check_count": len(checks), "checks": checks}
    (HERE / "PASS1018_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        for item in checks:
            if not item["passed"]:
                print("FAIL", item["name"])
        raise SystemExit(1)
    print(f"PASS {len(checks)}/{len(checks)}")


if __name__ == "__main__":
    main()
