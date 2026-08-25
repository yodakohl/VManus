#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path


OUT = Path(__file__).resolve().parent


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    clauses = rows("PASS940_354_SCRIBE_STYLE_CLAUSES.tsv")
    pages = rows("PASS940_14_SCRIBE_STYLE_PAGE_READINGS.tsv")
    checks = [
        ("clauses_354", len(clauses) == 354, len(clauses)),
        ("events_2010", sum(int(row["events"]) for row in clauses) == 2010, sum(int(row["events"]) for row in clauses)),
        ("pages_14", len(pages) == 14, len(pages)),
        ("clause_unique", len({row["clause_id"] for row in clauses}) == 354, len({row["clause_id"] for row in clauses})),
        ("all_translated", all(row["scribe_style_translation_de"].strip() for row in clauses), "nonempty"),
        ("all_phase_bound", all(int(row["phase_blocks"]) >= 1 for row in clauses), "bound"),
        ("no_unknown", all("UNKNOWN" not in row["scribe_style_translation_de"] for row in clauses), "spoken"),
        ("sealed_absent", all("f84" not in "\t".join(row.values()).lower() for row in clauses + pages), "sealed"),
    ]
    targets = [OUT / "PASS940_354_SCRIBE_STYLE_CLAUSES.tsv", OUT / "PASS940_14_SCRIBE_STYLE_PAGE_READINGS.tsv", OUT / "PASS940_SCRIBE_STYLE_FOURTEEN_PAGE_EDITION.md"]
    before = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in targets}
    subprocess.run([sys.executable, str(OUT / "build_nine_hundred_fortieth.py")], check=True)
    after = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in targets}
    checks.append(("deterministic", before == after, len(targets)))
    result = {"status": "PASS" if all(ok for _, ok, _ in checks) else "FAIL", "checks": [{"name": name, "pass": ok, "detail": detail} for name, ok, detail in checks]}
    (OUT / "PASS940_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
