#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent
PREFIX = "EIGHT_HUNDRED_FIFTY_SECOND"


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subprocess.run(["python", str(HERE / "build_eight_hundred_fifty_second.py")], check=True)
    switches = read(f"{PREFIX}_3_SECONDARY_SWITCHES.tsv")
    extras = read(f"{PREFIX}_10_GENERATED_EXTRAS.tsv")
    summary = json.loads((HERE / f"{PREFIX}_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "inventory": len(switches) == 3 and len(extras) == 10,
        "switch_partition": sorted(int(row["generated_count"]) for row in switches) == [3, 3, 4],
        "all_generated_once": len({(row["exact_card_id"], row["generated_extra_surface"]) for row in extras}) == 10,
        "same_meaning": all(row["same_card_and_meaning"] == "YES" for row in extras),
        "complete_coverage": summary["previously_selected_card_surface_pairs"] + summary["generated_extra_card_surface_pairs"] == summary["total_registered_card_surface_pairs"] == 230,
        "no_surface_exceptions": summary["remaining_memorized_surface_exceptions"] == 0,
        "no_hand_attribution": summary["actual_hand_attributions"] == 0,
        "sealed_pages": summary["sealed_pages"] == ["f84", "f84r"],
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / f"{PREFIX}_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
