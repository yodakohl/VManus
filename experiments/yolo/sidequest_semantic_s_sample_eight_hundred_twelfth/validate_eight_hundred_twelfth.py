#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subprocess.run(["python", str(HERE / "build_eight_hundred_twelfth.py")], check=True)
    candidates = read("EIGHT_HUNDRED_TWELFTH_5_S_CANDIDATES.tsv")
    events = read("EIGHT_HUNDRED_TWELFTH_S_EVENT.tsv")
    statements = read("EIGHT_HUNDRED_TWELFTH_REVISED_STATEMENT.tsv")
    contrasts = read("EIGHT_HUNDRED_TWELFTH_S_AIN_AIIN_CONTRAST.tsv")
    predictions = read("EIGHT_HUNDRED_TWELFTH_4_RECIPE_PREDICTIONS.tsv")
    summary = json.loads((HERE / "EIGHT_HUNDRED_TWELFTH_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "one_event_statement": len(events) == 1 and events[0]["event_id"] == "E216" and len(statements) == 1,
        "five_candidates_probe_selected": len(candidates) == 5 and next(row for row in candidates if row["decision"] == "SELECT")["candidate"] == "PROBE",
        "statement_revised_to_sample": "Probe entnehmen" in statements[0]["revised_reading_de"] and statements[0]["old_reading_de"] != statements[0]["revised_reading_de"],
        "three_quantity_roles_distinct": len(contrasts) == 3 and all(row["kept_distinct"] == "YES" for row in contrasts),
        "four_predictions_surfaces_withheld": len(predictions) == 4 and all(row["surface"] == "WITHHELD" for row in predictions),
        "core33_two_singletons": summary["new_core_size"] == 33 and summary["remaining_local_singletons"] == 2,
        "sealed_pages": summary["sealed_pages"] == ["f84", "f84r"],
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "EIGHT_HUNDRED_TWELFTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
