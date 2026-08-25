#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
PREFIX = "EIGHT_HUNDRED_SEVENTY_FIRST"


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subprocess.run(["python", str(HERE / "build_eight_hundred_seventy_first.py")], check=True)
    classes = read(f"{PREFIX}_6_MATERIAL_RESULT_CLASSES.tsv")
    audit = read(f"{PREFIX}_59_RESULT_EVENT_AUDIT.tsv")
    statements = read(f"{PREFIX}_43_RESULT_STATEMENTS.tsv")
    sample = read(f"{PREFIX}_12_SAMPLE_RESULT_EVENTS.tsv")
    master = read(f"{PREFIX}_5_MASTER_VALUE_STATUS.tsv")
    summary = json.loads((HERE / f"{PREFIX}_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "six_classes": len(classes) == 6 and {row["material_result_class_de"] for row in classes} == {"BEREIT", "ABGESETZT", "GESAMMELT", "DURCHGELAUFEN", "ERWAERMT", "VOLLSTAENDIG_ANGELEGT"},
        "event_inventory": len(audit) == 59 and len({row["event_id"] for row in audit}) == 59 and len({row["exact_card_id"] for row in audit}) == 30,
        "statement_inventory": len(statements) == 43 and len({row["statement_id"] for row in statements}) == 43,
        "sample": len(sample) == 12 and all(row["page"] == "f56r" or row["record"] == "B2" for row in sample),
        "sample_classes": Counter(value for row in sample for value in row["material_result_classes_de"].split(" + ")) == {"DURCHGELAUFEN": 5, "BEREIT": 2, "ABGESETZT": 2, "GESAMMELT": 1, "ERWAERMT": 1, "VOLLSTAENDIG_ANGELEGT": 1},
        "close_separate": any(row["step_closed"] == "YES" for row in audit) and any(row["step_closed"] == "NO" for row in audit),
        "master_status": len(master) == 5 and Counter(row["status_after"] for row in master) == {"CALIBRATION_ONLY": 3, "FULL_MASTER": 2},
        "no_material_identity": all(row["material_identity_known"] == "NO" for row in audit),
        "no_new_words": summary["new_word_meanings"] == 0,
        "sealed_pages": summary["sealed_pages"] == ["f84", "f84r"] and not any("f84" in " ".join(row.values()).lower() for row in classes + audit + statements + sample + master),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / f"{PREFIX}_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
