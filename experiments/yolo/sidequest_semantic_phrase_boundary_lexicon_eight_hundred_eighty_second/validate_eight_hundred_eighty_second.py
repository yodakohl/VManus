#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent
PREFIX = "EIGHT_HUNDRED_EIGHTY_SECOND"


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subprocess.run(["python", str(HERE / "build_eight_hundred_eighty_second.py")], check=True)
    summary = json.loads((HERE / f"{PREFIX}_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    windows = read(f"{PREFIX}_22_ANCHORED_PHRASE_WINDOWS.tsv")
    boundaries = read(f"{PREFIX}_31_UNIQUE_BOUNDARY_EVENTS.tsv")
    local = read(f"{PREFIX}_12_LOCAL_BOUNDARY_REFINEMENTS.tsv")
    frames = read(f"{PREFIX}_10_PHRASE_SLOT_FRAMES.tsv")
    checks = {
        "summary_pass": summary["status"] == "PASS",
        "windows_22": len(windows) == 22,
        "boundaries_31_unique": len(boundaries) == 31 and len({row["source_id"] for row in boundaries}) == 31,
        "portable_19": sum(row["card_class"] == "PORTABLE_CORE" for row in boundaries) == 19,
        "local_12": len(local) == 12 and all(row["new_stem_meaning"] == "NO" for row in local),
        "local_identities_12": len({row["identity"] for row in local}) == 12,
        "frames_10": len(frames) == 10,
        "all_phrase_ids": {row["phrase_id"] for row in frames} == {f"PHR{i:02d}" for i in range(1, 11)},
        "all_slots_filled": all(row["left_slot"] and row["right_slot"] for row in windows),
        "all_boundary_readings": all(row["phrase_ready_reading_de"] and row["semantic_atoms_changed"] == "NO" for row in boundaries),
        "no_semantic_atom_changes": summary["semantic_atom_changes"] == 0,
        "fixed_pages": summary["fixed_pages"] == ["f10r", "f55v", "f81v", "f82r", "f83r"],
        "sealed": summary["sealed_pages"] == ["f84", "f84r"],
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / f"{PREFIX}_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
