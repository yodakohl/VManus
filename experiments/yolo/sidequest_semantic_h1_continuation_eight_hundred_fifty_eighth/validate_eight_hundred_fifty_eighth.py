#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent
PREFIX = "EIGHT_HUNDRED_FIFTY_EIGHTH"


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subprocess.run(["python", str(HERE / "build_eight_hundred_fifty_eighth.py")], check=True)
    rows = read(f"{PREFIX}_4_CARD_SOURCE_MAP.tsv")
    registers = read(f"{PREFIX}_4_INHERITED_REGISTERS.tsv")
    combined = read(f"{PREFIX}_COMPLETE_H1_SOURCE_EDITION.tsv")
    summary = json.loads((HERE / f"{PREFIX}_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "inventory": len(rows) == 4 and len(registers) == 4 and len(combined) == 1,
        "events": [row["event_id"] for row in rows] == ["E011", "E012", "E013", "E014"],
        "meanings": all(row["same_card_meaning"] == "YES" for row in rows),
        "inheritance": all(row["picture_owner_inherited"] == row["active_preparation_inherited"] == "YES" for row in rows),
        "atoms": summary["S002_semantic_atoms"] == 8 and summary["H1_semantic_atoms"] == 31,
        "registers": summary["inherited_registers"] == 3 and summary["restated_owner_or_preparation"] == 0,
        "open_record": combined[0]["explicit_close_in_H1"] == "NO" and summary["explicit_close_cards"] == 0,
        "no_unmapped": summary["unmapped_cards"] == 0,
        "sealed_pages": summary["sealed_pages"] == ["f84", "f84r"],
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / f"{PREFIX}_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
