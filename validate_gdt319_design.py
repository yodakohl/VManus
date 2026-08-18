#!/usr/bin/env python3
"""Validate GDT319 fresh-surface freeze."""
import csv
import hashlib
import json
from pathlib import Path

R = Path(__file__).resolve().parent
PANEL = R / "gdt319_frozen_panel.tsv"
CAPACITY = R / "gdt319_capacity.tsv"
DESIGN = R / "gdt319_design.json"
OUT = R / "gdt319_design_validation.json"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()


def read(path):
    with Path(path).open(encoding="utf8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    checks = []
    def check(name, condition):
        if not condition:
            raise AssertionError(name)
        checks.append(name)
    design = json.loads(DESIGN.read_text())
    stored = design.pop("content_sha256")
    check("content", stored == canonical_hash(design))
    panel = read(PANEL)
    capacity = read(CAPACITY)[0]
    check("capacity", (int(capacity["cells"]), int(capacity["events"]), int(capacity["t_events"]), int(capacity["folios"]), int(capacity["excluded_surface_hashes"])) == (7, 50, 20, 31, 505))
    check("unique", len(panel) == len({row["event_id_sha256"] for row in panel}))
    check("withheld", {row["t_choice_withheld"] for row in panel} == {"WITHHELD_UNTIL_SCORING"})
    check("f84", not any(row["page"].startswith("f84") or row["locus"].startswith("f84") for row in panel) and not any(design["f84"].values()))
    check("hashes", all(design["inputs"][name] == sha(R / name) for name in design["inputs"]) and all(design["outputs"][name] == sha(R / name) for name in design["outputs"]))
    validation = {"schema": "GDT319_DESIGN_VALIDATION_V1", "status": "PASS", "checks_passed": len(checks), "checks": checks, "design_sha256": sha(DESIGN), "f84_rows": 0}
    validation["content_sha256"] = canonical_hash(validation)
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": "PASS", "checks": len(checks)}, sort_keys=True))


if __name__ == "__main__":
    main()
