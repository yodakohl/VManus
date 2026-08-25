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
    labels = read("PASS945_16_F88R_LOCAL_LABELS.tsv")
    records = read("PASS945_3_F88R_PREPARATION_RECORDS.tsv")
    checks = [
        ("labels_16", len(labels) == 16, len(labels)),
        ("records_3", len(records) == 3, len(records)),
        ("prose_134", sum(int(row["prose_cards"]) for row in records) == 134, sum(int(row["prose_cards"]) for row in records)),
        ("total_150", len(labels) + sum(int(row["prose_cards"]) for row in records) == 150, "complete"),
        ("label_unique", len({row["event_id"] for row in labels}) == 16, len({row["event_id"] for row in labels})),
        ("all_named", all(row["local_nomenclator_default_de"].strip() for row in labels), "named"),
        ("three_heads", sum(row["visual_role"] == "PREPARATION_HEADING" for row in labels) == 3, sum(row["visual_role"] == "PREPARATION_HEADING" for row in labels)),
        ("sealed_absent", all("f84" not in "\t".join(row.values()).lower() for row in labels + records), "sealed"),
    ]
    targets = [OUT / "PASS945_16_F88R_LOCAL_LABELS.tsv", OUT / "PASS945_3_F88R_PREPARATION_RECORDS.tsv", OUT / "PASS945_F88R_COMPLETE_LOCAL_EDITION.md"]
    before = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in targets}
    subprocess.run([sys.executable, str(OUT / "build_nine_hundred_forty_fifth.py")], check=True)
    after = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in targets}
    checks.append(("deterministic", before == after, len(targets)))
    result = {"status": "PASS" if all(ok for _, ok, _ in checks) else "FAIL", "checks": [{"name": name, "pass": ok, "detail": detail} for name, ok, detail in checks]}
    (OUT / "PASS945_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
