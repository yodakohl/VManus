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
    subprocess.run(["python", str(HERE / "build_eight_hundred_fourteenth.py")], check=True)
    candidates = read("EIGHT_HUNDRED_FOURTEENTH_5_LD_CANDIDATES.tsv")
    events = read("EIGHT_HUNDRED_FOURTEENTH_LD_EVENT.tsv")
    extensions = read("EIGHT_HUNDRED_FOURTEENTH_5_EXTENSION_TESTS.tsv")
    summary = json.loads((HERE / "EIGHT_HUNDRED_FOURTEENTH_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "one_event": len(events) == 1 and events[0]["event_id"] == "E326" and events[0]["classification"] == "BOUND_FASTENING_BEFORE_DY",
        "five_candidates_fastening_selected": len(candidates) == 5 and next(row for row in candidates if row["decision"] == "SELECT_BOUND")["candidate"] == "BEFESTIGEN",
        "five_extension_tests": len(extensions) == 5,
        "ldy_collision_with_l_plus_dy": summary["surface_collisions"] == 1 and next(row for row in extensions if row["naive_surface"] == "ldy")["observed_recipe"] == "L+DY",
        "no_free_predictions": all(row["decision"] in {"DO_NOT_GENERALIZE", "WITHHOLD_BOUND_COMPONENT"} for row in extensions),
        "core33_bound3_local0": summary["core_size"] == 33 and summary["bound_components"] == 3 and summary["remaining_local_singletons"] == 0,
        "sealed_pages": summary["sealed_pages"] == ["f84", "f84r"],
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "EIGHT_HUNDRED_FOURTEENTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
