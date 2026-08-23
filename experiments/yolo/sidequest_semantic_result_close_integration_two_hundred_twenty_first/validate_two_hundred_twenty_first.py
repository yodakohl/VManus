#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path

OUT = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def hashes() -> dict[str, str]:
    names = ["TWO_HUNDRED_TWENTY_FIRST_173_CARD_DICTIONARY.tsv", "TWO_HUNDRED_TWENTY_FIRST_381_EVENT_PROSE.tsv", "TWO_HUNDRED_TWENTY_FIRST_116_STATEMENT_PROSE.tsv", "TWO_HUNDRED_TWENTY_FIRST_776_LAYERED_LEDGER.tsv", "TWO_HUNDRED_TWENTY_FIRST_TEN_AFFECTED_OCCURRENCES.tsv", "TWO_HUNDRED_TWENTY_FIRST_REVISED_COMMON_FORMULA.tsv", "TWO_HUNDRED_TWENTY_FIRST_REVISED_COMMON_FORMULA.md", "BUILD_SUMMARY.json"]
    return {name: hashlib.sha256((OUT / name).read_bytes()).hexdigest() for name in names}


def main() -> None:
    dictionary = read("TWO_HUNDRED_TWENTY_FIRST_173_CARD_DICTIONARY.tsv")
    events = read("TWO_HUNDRED_TWENTY_FIRST_381_EVENT_PROSE.tsv")
    statements = read("TWO_HUNDRED_TWENTY_FIRST_116_STATEMENT_PROSE.tsv")
    ledger = read("TWO_HUNDRED_TWENTY_FIRST_776_LAYERED_LEDGER.tsv")
    affected = read("TWO_HUNDRED_TWENTY_FIRST_TEN_AFFECTED_OCCURRENCES.tsv")
    formula = read("TWO_HUNDRED_TWENTY_FIRST_REVISED_COMMON_FORMULA.tsv")
    readable = (OUT / "TWO_HUNDRED_TWENTY_FIRST_REVISED_COMMON_FORMULA.md").read_text(encoding="utf-8")
    summary = json.loads((OUT / "BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    values = {row["master_card_id"]: row["current_value_de"] for row in dictionary}
    counts = Counter(row["normalized_id"] for row in affected)
    checks = {
        "173_dictionary": len(dictionary) == 173 and len(values) == 173,
        "381_events": len(events) == 381 and len({row["event_id"] for row in events}) == 381,
        "116_statements": len(statements) == 116 and len({row["statement_id"] for row in statements}) == 116,
        "776_layered": len(ledger) == 776 and len({row["unified_serial"] for row in ledger}) == 776,
        "exact_card_revisions": values["MC019"] == "Schluss" and values["MC119"] == "Ergebnis",
        "only_two_dictionary_revisions": sum(row["r221_revision"] != "UNCHANGED" for row in dictionary) == 2,
        "ten_occurrences_3_plus_7": len(affected) == 10 and counts == {"MC019": 3, "MC119": 7},
        "six_prose_four_astro": summary["affected_prose"] == 6 and summary["affected_astro"] == 4,
        "event_dictionary_agreement": all(row["portable_value_de"] == values[row["master_card_id"]] for row in events),
        "four_formula_fields": len(formula) == 4 and [int(row["field"]) for row in formula] == [1, 2, 3, 4],
        "new_formula_words": "Schluss; Ergebnis" in readable and "Freigabewert" not in readable and "fertig" not in readable.lower(),
        "sealed_not_accessed": summary["sealed_pages_accessed"] is False,
        "sealed_absent": "f84" not in readable.lower() and not any("f84" in value.lower() for table in (dictionary, events, statements, ledger) for row in table for value in row.values()),
    }
    first = hashes()
    subprocess.run(["python3", str(OUT / "build_two_hundred_twenty_first.py")], check=True)
    second = hashes()
    checks["deterministic_rebuild"] = first == second
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "summary": summary, "artifact_sha256": second}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
