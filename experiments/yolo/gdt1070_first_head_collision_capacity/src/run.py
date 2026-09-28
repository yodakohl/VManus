#!/usr/bin/env python3
"""Aggregate the frozen GDT1059 Herbal-A first-head projection."""
import csv
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / "experiments/yolo/gdt1059_kooiin_header_quality_base_rate/artifacts/HEAD_CONTACTS.tsv"
OUT = Path(__file__).resolve().parents[1] / "artifacts"


def summary(rows):
    by_form = defaultdict(list)
    for row in rows:
        by_form[row["head_surface"]].append(row["page"])
    forms = {word: sorted(pages) for word, pages in by_form.items()}
    return {
        "pages": len(rows), "types": len(forms),
        "singleton_types": sum(len(pages) == 1 for pages in forms.values()),
        "singleton_pages": sum(len(pages) == 1 for pages in forms.values()),
        "repeat_pairs": sum(len(pages) * (len(pages) - 1) // 2 for pages in forms.values()),
        "repeated": {word: pages for word, pages in forms.items() if len(pages) > 1},
    }, forms


def main():
    with SOURCE.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh, delimiter="\t"))
    assert len(rows) == 89 and len({row["page"] for row in rows}) == 89
    assert next(row["head_surface"] for row in rows if row["page"] == "f9v") == "fochor"
    full, forms = summary(rows)
    leave, _ = summary([row for row in rows if row["page"] not in {"f2v", "f29v"}])
    result = {
        "experiment": "GDT1070", "source": str(SOURCE.relative_to(ROOT)),
        "full": full, "without_selected_kooiin_pair": leave,
        "fochor_head_pages": forms["fochor"],
        "fochor_multiplicity": len(forms["fochor"]), "meaning": "unbound",
    }
    OUT.mkdir(exist_ok=True)
    with (OUT / "HEAD_MULTIPLICITIES.tsv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh, delimiter="\t", lineterminator="\n")
        writer.writerow(["head_surface", "multiplicity", "pages"])
        for form in sorted(forms):
            writer.writerow([form, len(forms[form]), ",".join(forms[form])])
    (OUT / "RESULT.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
