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
    stems = read("PASS941_56_PRODUCTIVE_ABBREVIATIONS.tsv")
    whole = read("PASS941_64_LEARNED_WHOLE_CARDS.tsv")
    dictionary = read("PASS941_1078_HYBRID_DICTIONARY.tsv")
    events = read("PASS941_2511_HYBRID_EVENT_READINGS.tsv")
    checks = [
        ("stems_56", len(stems) == 56, len(stems)),
        ("whole_64", len(whole) == 64, len(whole)),
        ("surfaces_1078", len(dictionary) == 1078, len(dictionary)),
        ("events_2511", len(events) == 2511, len(events)),
        ("unique_surfaces", len({row["surface"] for row in dictionary}) == 1078, len({row["surface"] for row in dictionary})),
        ("unique_events", len({row["event_id"] for row in events}) == 2511, len({row["event_id"] for row in events})),
        ("whole_in_dictionary", sum(row["reading_route"] == "LEARNED_WHOLE_CARD" for row in dictionary) == 64, sum(row["reading_route"] == "LEARNED_WHOLE_CARD" for row in dictionary)),
        ("all_concrete", all(row["hybrid_codebook_reading_de"].strip() for row in events), "nonempty"),
        ("all_pages", len({row["physical_page"] for row in events}) == 14, len({row["physical_page"] for row in events})),
        ("sealed_absent", all("f84" not in "\t".join(row.values()).lower() for row in events), "sealed"),
    ]
    targets = [OUT / "PASS941_56_PRODUCTIVE_ABBREVIATIONS.tsv", OUT / "PASS941_64_LEARNED_WHOLE_CARDS.tsv", OUT / "PASS941_1078_HYBRID_DICTIONARY.tsv", OUT / "PASS941_2511_HYBRID_EVENT_READINGS.tsv"]
    before = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in targets}
    subprocess.run([sys.executable, str(OUT / "build_nine_hundred_forty_first.py")], check=True)
    after = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in targets}
    checks.append(("deterministic", before == after, len(targets)))
    result = {"status": "PASS" if all(ok for _, ok, _ in checks) else "FAIL", "checks": [{"name": name, "pass": ok, "detail": detail} for name, ok, detail in checks]}
    (OUT / "PASS941_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
