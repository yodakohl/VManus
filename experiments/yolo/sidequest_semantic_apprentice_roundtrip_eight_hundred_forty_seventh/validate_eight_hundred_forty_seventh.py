#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
PREFIX = "EIGHT_HUNDRED_FORTY_SEVENTH"


def read(suffix: str) -> list[dict[str, str]]:
    with (HERE / f"{PREFIX}_{suffix}").open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subprocess.run(["python", str(HERE / "build_eight_hundred_forty_seventh.py")], check=True)
    forward = read("20_FORWARD_ROUNDTRIPS.tsv")
    reverse = read("20_REVERSE_FLASHCARDS.tsv")
    traps = read("5_APPRENTICE_TRAPS.tsv")
    summary = json.loads((HERE / f"{PREFIX}_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "command_inventory": len(forward) == 20 and len(reverse) == 20 and [int(row["command_no"]) for row in forward] == list(range(1, 21)),
        "roundtrip_pass": all(row["roundtrip"] == "PASS" for row in forward),
        "owner_free": all(row["page_owner_used"] == "NO" for row in forward + reverse),
        "surface_split": Counter(row["surface_status"] for row in forward) == Counter({"ATTESTED_CARD": 17, "PREDICTED_CARD": 3}),
        "predicted_surfaces": {row["encoded_surface"] for row in forward if row["surface_status"] == "PREDICTED_CARD"} == {"lair", "qokaiiin", "cheeeky"},
        "learning_modes": Counter(row["learning_mode"] for row in forward) == Counter({"COMPOSE_COMPONENTS": 14, "MEMORIZE_BOUND_FRAME": 3, "MEMORIZE_WHOLE_CARD": 3}),
        "reverse_alignment": all(f["encoded_surface"] == r["shown_surface"] and f["decoded_command_de"] == r["say_de"] for f, r in zip(forward, reverse)),
        "trap_inventory": len(traps) == 5 and {row["trap"] for row in traps} == {"VISIBLE_DY", "AIR_VS_AR", "TWO_E_SLOTS", "BOUND_VALUES", "WHOLE_WORDS"},
        "summary": summary["roundtrip_passes"] == 20 and summary["owner_uses"] == 0,
        "sealed_pages": summary["sealed_pages"] == ["f84", "f84r"],
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / f"{PREFIX}_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
