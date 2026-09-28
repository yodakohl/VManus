#!/usr/bin/env python3
"""Independent row and count replay of GDT1070 saved results."""
import csv
import json
from collections import Counter
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
DIR = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "experiments/yolo/gdt1059_kooiin_header_quality_base_rate/artifacts/HEAD_CONTACTS.tsv"


def main():
    with SOURCE.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh, delimiter="\t"))
    with (DIR / "artifacts/HEAD_MULTIPLICITIES.tsv").open(newline="", encoding="utf-8") as fh:
        saved = list(csv.DictReader(fh, delimiter="\t"))
    result = json.loads((DIR / "artifacts/RESULT.json").read_text(encoding="utf-8"))
    checks = 0
    assert len(rows) == result["full"]["pages"] == 89
    checks += 1
    assert len({r["page"] for r in rows}) == 89
    checks += 1
    assert len(saved) == result["full"]["types"]
    checks += 1
    for row in saved:
        observed = sorted(r["page"] for r in rows if r["head_surface"] == row["head_surface"])
        assert len(observed) == int(row["multiplicity"])
        assert observed == row["pages"].split(",")
        checks += 2
    for key, subset in [("full", rows), ("without_selected_kooiin_pair", [r for r in rows if r["page"] not in {"f2v", "f29v"}])]:
        counts = Counter(r["head_surface"] for r in subset)
        expected = result[key]
        assert expected["pages"] == len(subset)
        assert expected["types"] == len(counts)
        assert expected["singleton_types"] == sum(v == 1 for v in counts.values())
        assert expected["singleton_pages"] == sum(v for v in counts.values() if v == 1)
        assert expected["repeat_pairs"] == sum(1 for a, b in combinations(subset, 2) if a["head_surface"] == b["head_surface"])
        assert expected["repeated"] == {word: sorted(r["page"] for r in subset if r["head_surface"] == word) for word, n in counts.items() if n > 1}
        checks += 6
    assert result["fochor_head_pages"] == ["f9v"] and result["fochor_multiplicity"] == 1
    checks += 1
    report = {"experiment": "GDT1070", "status": "PASS", "checks": checks}
    (DIR / "artifacts/VALIDATION.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
