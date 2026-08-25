#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
PREFIX = "EIGHT_HUNDRED_SIXTY_NINTH"


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subprocess.run(["python", str(HERE / "build_eight_hundred_sixty_ninth.py")], check=True)
    unified = read(f"{PREFIX}_776_TEN_PAGE_PRODUCTION_LEDGER.tsv")
    pages = read(f"{PREFIX}_10_PAGE_LAYER_SUMMARY.tsv")
    manual = read(f"{PREFIX}_12_STEP_SCRIBAL_MANUAL.tsv")
    sample = read(f"{PREFIX}_90_MARK_COMPLETE_SAMPLE.tsv")
    master = read(f"{PREFIX}_5_SAMPLE_MASTER_VALUES.tsv")
    roundtrip = read(f"{PREFIX}_10_CHECKPOINT_ROUNDTRIP.tsv")
    summary = json.loads((HERE / f"{PREFIX}_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    layers = Counter(row["layer"] for row in unified)
    sample_layers = Counter(row["stage"] for row in sample)
    checks = {
        "unified_776": len(unified) == 776 and layers == {"WHAT_PREPARATION": 100, "HOW_APPLICATION": 281, "WHEN_CONDITION": 395},
        "ten_pages": len(pages) == 10 and {row["page"] for row in pages} == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v"},
        "page_total": sum(int(row["visible_groups"]) for row in pages) == 776,
        "manual": len(manual) == 12 and {int(row["step"]) for row in manual} == set(range(1, 13)),
        "sample_90": len(sample) == 90 and sample_layers == {"WHAT_PREPARATION": 27, "HOW_APPLICATION": 62, "WHEN_CONDITION": 1},
        "sample_condition": sample[-1]["page"] == "f69v" and sample[-1]["source_id"] == "A3:G118" and sample[-1]["surface"] == "otody",
        "five_master_values": len(master) == 5 and {row["slot"] for row in master} == {"PRODUCT", "MEASURE", "DURATION", "RESULT", "CONDITION"},
        "roundtrip": len(roundtrip) == 10 and sum(row["backward_without_master"] == "RECOVERED" for row in roundtrip) == 5 and sum(row["backward_with_master"] == "RECOVERED" for row in roundtrip) == 10,
        "no_new_words": summary["new_word_meanings"] == 0,
        "sealed_pages": summary["sealed_pages"] == ["f84", "f84r"] and not any("f84" in " ".join(row.values()).lower() for row in unified + pages + manual + sample + master + roundtrip),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / f"{PREFIX}_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
