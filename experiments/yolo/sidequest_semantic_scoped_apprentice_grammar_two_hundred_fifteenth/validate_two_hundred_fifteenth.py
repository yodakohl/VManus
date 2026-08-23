#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from pathlib import Path

OUT = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def hashes() -> dict[str, str]:
    names = ["TWO_HUNDRED_FIFTEENTH_TEN_COMMON_CORE_AXES.tsv", "TWO_HUNDRED_FIFTEENTH_EIGHTEEN_PROSE_AXES.tsv", "TWO_HUNDRED_FIFTEENTH_22_SCOPED_WHOLE_CARDS.tsv", "TWO_HUNDRED_FIFTEENTH_173_CARD_SCOPED_DICTIONARY.tsv", "BUILD_SUMMARY.json"]
    return {name: hashlib.sha256((OUT / name).read_bytes()).hexdigest() for name in names}


def main() -> None:
    common = read("TWO_HUNDRED_FIFTEENTH_TEN_COMMON_CORE_AXES.tsv")
    prose = read("TWO_HUNDRED_FIFTEENTH_EIGHTEEN_PROSE_AXES.tsv")
    whole = read("TWO_HUNDRED_FIFTEENTH_22_SCOPED_WHOLE_CARDS.tsv")
    dictionary = read("TWO_HUNDRED_FIFTEENTH_173_CARD_SCOPED_DICTIONARY.tsv")
    summary = json.loads((OUT / "BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "ten_common_axes": len(common) == 10 and len({row["axis"] for row in common}) == 10,
        "eighteen_prose_axes": len(prose) == 18 and len({row["axis"] for row in prose}) == 18,
        "ched_chd_unified": "CHED~CHD" in {row["axis"] for row in common} and "CHED" not in {row["axis"] for row in common} and "CHD" not in {row["axis"] for row in common},
        "aiin_is_sollwert": next(row for row in common if row["axis"] == "AIIN")["portable_value_de"] == "SOLLWERT",
        "22_whole_cards": len(whole) == 22 and len({row["master_card_id"] for row in whole}) == 22,
        "one_common_whole_card": summary["common_whole_cards"] == 1 and next(row for row in whole if row["scope"] == "COMMON_THREE_REGISTER_RESULT_CARD")["portable_value_de"] == "Freigabewert",
        "173_cards": len(dictionary) == 173 and len({row["master_card_id"] for row in dictionary}) == 173,
        "every_card_scoped": all(row["semantic_scope"] for row in dictionary),
        "no_free_ey_axis": "EY" not in {row["axis"] for row in common + prose},
        "all_axes_have_examples": all(int(row["productive_card_types"]) > 0 for row in common + prose),
        "sealed_not_accessed": summary["sealed_pages_accessed"] is False,
        "sealed_absent": not any("f84" in value.lower() for rows in (common, prose, whole, dictionary) for row in rows for value in row.values()),
    }
    first = hashes()
    subprocess.run(["python3", str(OUT / "build_two_hundred_fifteenth.py")], check=True)
    second = hashes()
    checks["deterministic_rebuild"] = first == second
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "summary": summary, "artifact_sha256": second}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
