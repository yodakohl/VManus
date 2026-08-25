#!/usr/bin/env python3
"""Validate Pass 916."""

import csv
import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

OUT = Path(__file__).resolve().parent


def rows(name):
    with (OUT / name).open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def main():
    summary = json.loads((OUT / "PASS916_BUILD_SUMMARY.json").read_text())
    e = rows("PASS916_2010_EVENT_PHRASES.tsv")
    c = rows("PASS916_354_COMPACT_CLAUSES.tsv")
    m = rows("PASS916_PHRASEBOOK.tsv")
    checks = []
    def add(name, ok, detail): checks.append({"name": name, "pass": bool(ok), "detail": detail})
    add("events_2010", len(e) == 2010, len(e))
    add("event_ids_unique", len({r['event_id'] for r in e}) == 2010, len({r['event_id'] for r in e}))
    add("clauses_354", len(c) == 354, len(c))
    add("macros_44", len(m) == 44, len(m))
    add("macro_ids_unique", len({r['macro_id'] for r in m}) == 44, len({r['macro_id'] for r in m}))
    add("all_phrase_units", all(r['phrase_units'] for r in e), sum(bool(r['phrase_units']) for r in e))
    add("all_short_readings", all(r['workshop_phrase_de'] for r in e), sum(bool(r['workshop_phrase_de']) for r in e))
    add("macro_event_count", summary['events_using_macro'] == 816, summary['events_using_macro'])
    add("macro_atom_count", summary['component_atoms_in_macros'] == 1930, summary['component_atoms_in_macros'])
    add("atom_total", summary['component_atoms_total'] == 5027, summary['component_atoms_total'])
    add("all_clauses_compact", all(r['compact_workshop_reading_de'] for r in c), len(c))
    add("macro_use_sum", sum(int(r['uses_in_2010_prose_events']) for r in m) == summary['macro_uses'], summary['macro_uses'])
    published = [
        "PASS916_PHRASEBOOK.tsv", "PASS916_2010_EVENT_PHRASES.tsv",
        "PASS916_354_COMPACT_CLAUSES.tsv", "PASS916_COMPACT_CLAUSE_EDITION.md",
        "PASS916_REPORT.md",
    ]
    text = "\n".join((OUT / name).read_text(encoding="utf-8", errors="ignore") for name in published)
    add("sealed_absent", "f84" not in text.lower(), "sealed")
    before = summary['sha256']
    subprocess.run([sys.executable, str(OUT / "build_nine_hundred_sixteenth.py")], check=True)
    after = json.loads((OUT / "PASS916_BUILD_SUMMARY.json").read_text())['sha256']
    add("deterministic_rebuild", before == after, len(after))
    result = {"status": "PASS" if all(x['pass'] for x in checks) else "FAIL",
              "checks_passed": sum(x['pass'] for x in checks), "checks_total": len(checks), "checks": checks}
    (OUT / "PASS916_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result))
    raise SystemExit(0 if result['status'] == 'PASS' else 1)


if __name__ == '__main__':
    main()
