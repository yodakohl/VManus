#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
PREFIX = "EIGHT_HUNDRED_SEVENTY_THIRD"


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subprocess.run(["python", str(HERE / "build_eight_hundred_seventy_third.py")], check=True)
    roots = read(f"{PREFIX}_12_RELATIVE_ASTRO_COMPONENTS.tsv")
    groups = read(f"{PREFIX}_395_RELATIVE_CONDITION_GROUPS.tsv")
    loci = read(f"{PREFIX}_142_INTERNAL_CONDITION_HANDLES.tsv")
    shelves = read(f"{PREFIX}_7_SHELF_RELATIVE_PROFILES.tsv")
    sample = read(f"{PREFIX}_OTODY_SAMPLE_DECODE.tsv")
    payload = read(f"{PREFIX}_5_PAYLOAD_STATUS.tsv")
    summary = json.loads((HERE / f"{PREFIX}_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    page_groups = Counter(row["page"] for row in groups)
    page_loci = Counter(row["page"] for row in loci)
    checks = {
        "twelve_roots": len(roots) == 12 and {row["relative_component"] for row in roots} == {"OT", "OL", "AR", "AL", "AIN", "AIIN", "IIN", "E", "EE", "EEE", "Y", "DY"},
        "all_groups": len(groups) == 395 and page_groups == {"f67r2": 190, "f68r1": 65, "f69v": 140},
        "relative_coverage": sum(row["portable_relative_components"] != "NONE" for row in groups) == 329,
        "all_loci": len(loci) == 142 and len({row["condition_handle"] for row in loci}) == 142 and page_loci == {"f67r2": 74, "f68r1": 37, "f69v": 31},
        "seven_shelves": len(shelves) == 7 and sum(int(row["groups"]) for row in shelves) == 395 and sum(int(row["loci"]) for row in shelves) == 142,
        "sample_otody": len(sample) == 5 and {row["layer"]: row["value"] for row in sample}["PARSE"] == "OT+O+DY" and {row["layer"]: row["value"] for row in sample}["HANDLE"] == "C4@f69v.12",
        "payloads": len(payload) == 5 and summary["fully_master_dependent_internal_payloads_after"] == 0,
        "no_external_names": all(row["external_celestial_or_calendar_name"] == "UNNAMED" for row in groups) and summary["external_celestial_names_identified"] == 0,
        "no_crosspage_keys": summary["crosspage_keys"] == 0,
        "sealed_pages": summary["sealed_pages"] == ["f84", "f84r"] and not any("f84" in " ".join(row.values()).lower() for row in roots + groups + loci + shelves + sample + payload),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / f"{PREFIX}_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
