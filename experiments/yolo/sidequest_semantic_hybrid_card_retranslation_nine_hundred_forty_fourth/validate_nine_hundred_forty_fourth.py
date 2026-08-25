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
    clauses = read("PASS944_354_HYBRID_CARD_CLAUSES.tsv")
    events = read("PASS944_2010_PROSE_CARD_INTERLINEAR.tsv")
    checks = [
        ("clauses_354", len(clauses) == 354, len(clauses)),
        ("events_2010", len(events) == 2010, len(events)),
        ("clause_event_sum", sum(int(row["events"]) for row in clauses) == 2010, sum(int(row["events"]) for row in clauses)),
        ("route_sum", sum(int(row["learned_card_events"]) + int(row["composed_events"]) for row in clauses) == 2010, "complete"),
        ("event_unique", len({row["event_id"] for row in events}) == 2010, len({row["event_id"] for row in events})),
        ("clause_unique", len({row["clause_id"] for row in clauses}) == 354, len({row["clause_id"] for row in clauses})),
        ("all_translated", all(row["hybrid_card_translation_de"].strip() for row in clauses), "nonempty"),
        ("all_pages", len({row["physical_page"] for row in events}) == 12, len({row["physical_page"] for row in events})),
        ("sealed_absent", all("f84" not in "\t".join(row.values()).lower() for row in clauses + events), "sealed"),
    ]
    targets = [OUT / "PASS944_354_HYBRID_CARD_CLAUSES.tsv", OUT / "PASS944_2010_PROSE_CARD_INTERLINEAR.tsv", OUT / "PASS944_COMPLETE_HYBRID_RETRANSLATION.md"]
    before = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in targets}
    subprocess.run([sys.executable, str(OUT / "build_nine_hundred_forty_fourth.py")], check=True)
    after = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in targets}
    checks.append(("deterministic", before == after, len(targets)))
    result = {"status": "PASS" if all(ok for _, ok, _ in checks) else "FAIL", "checks": [{"name": name, "pass": ok, "detail": detail} for name, ok, detail in checks]}
    (OUT / "PASS944_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
