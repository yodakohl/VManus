#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path


OUT = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    units = read("PASS947_14_UNIT_BOOK_MAP.tsv")
    stages = read("PASS947_4_STAGE_WORKFLOW.tsv")
    checks = [
        ("units_14", len(units) == 14, len(units)),
        ("events_2511", sum(int(row["events"]) for row in units) == 2511, sum(int(row["events"]) for row in units)),
        ("stages_4", len(stages) == 4, len(stages)),
        ("all_stages_used", {row["book_stage"] for row in units} == {row["book_stage"] for row in stages}, sorted({row["book_stage"] for row in units})),
        ("all_pages_unique", len({row["physical_page"] for row in units}) == 14, len({row["physical_page"] for row in units})),
        ("all_concrete", all(row["concrete_function_de"].strip() for row in units), "nonempty"),
        ("sealed_absent", all("f84" not in "\t".join(row.values()).lower() for row in units + stages), "sealed"),
    ]
    targets = [OUT / "PASS947_14_UNIT_BOOK_MAP.tsv", OUT / "PASS947_4_STAGE_WORKFLOW.tsv", OUT / "PASS947_COMPLETE_WORKING_THEORY.md"]
    before = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in targets}
    subprocess.run([sys.executable, str(OUT / "build_nine_hundred_forty_seventh.py")], check=True)
    after = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in targets}
    checks.append(("deterministic", before == after, len(targets)))
    result = {"status": "PASS" if all(ok for _, ok, _ in checks) else "FAIL", "checks": [{"name": name, "pass": ok, "detail": detail} for name, ok, detail in checks]}
    (OUT / "PASS947_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
