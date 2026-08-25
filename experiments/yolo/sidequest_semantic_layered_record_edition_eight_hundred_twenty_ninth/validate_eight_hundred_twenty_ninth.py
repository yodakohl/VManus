#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subprocess.run(["python", str(HERE / "build_eight_hundred_twenty_ninth.py")], check=True)
    contract = read("EIGHT_HUNDRED_TWENTY_NINTH_39_COMPONENT_LITERAL_CONTRACT.tsv")
    statements = read("EIGHT_HUNDRED_TWENTY_NINTH_116_LAYERED_STATEMENTS.tsv")
    records = read("EIGHT_HUNDRED_TWENTY_NINTH_11_LAYERED_RECORDS.tsv")
    summary = json.loads((HERE / "EIGHT_HUNDRED_TWENTY_NINTH_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    value = {row["component"]: row["short_value_de"] for row in contract}
    statement_counts = Counter(row["record"] for row in statements)
    markdown_headings = [line for line in (HERE / "EIGHT_HUNDRED_TWENTY_NINTH_ELEVEN_COMPLETE_RECORDS.md").read_text(encoding="utf-8").splitlines() if line.startswith("## ")]
    checks = {
        "complete_counts": len(contract) == 39 and len(statements) == 116 and len(records) == 11 and summary["events"] == 381,
        "record_split": summary["herbal_records"] == 5 and summary["biological_records"] == 6,
        "record_statement_counts": all(statement_counts[row["record"]] == int(row["statements"]) for row in records),
        "record_event_total": sum(int(row["events"]) for row in records) == 381,
        "atom_total": sum(int(row["component_atoms"]) for row in statements) == summary["component_atoms"] == sum(int(row["component_atoms"]) for row in records),
        "literal_atoms_exact": all(row["literal_component_layer_de"].split(" · ") == [value[token] for recipe in row["component_sequence"].split(" | ") for token in recipe.split("+")] for row in statements),
        "one_value_contract": len(set(value)) == 39 and all(row["short_value_de"] for row in contract) and all(row["owner_may_change_value"] == "NO" for row in contract),
        "owners_explicit": all(row["owner_address_de"] and row["owner_supplied_layer_de"].startswith("OWNER=") for row in statements),
        "fluent_complete": all(row["fluent_workshop_reading_de"] for row in statements),
        "markdown_complete": sum(line.startswith("## H") for line in markdown_headings) == 5 and sum(line.startswith("## B") for line in markdown_headings) == 6,
        "sealed_pages": summary["sealed_pages"] == ["f84", "f84r"],
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "EIGHT_HUNDRED_TWENTY_NINTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
