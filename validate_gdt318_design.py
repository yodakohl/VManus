#!/usr/bin/env python3
"""Validate the score-blind GDT318 panel and bindings."""
import csv
import hashlib
import json
from pathlib import Path

R = Path(__file__).resolve().parent
PANEL = R / "gdt318_frozen_panel.tsv"
CAPACITY = R / "gdt318_capacity.tsv"
DESIGN = R / "gdt318_design.json"
OUT = R / "gdt318_design_validation.json"


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
    check("capacity", (int(capacity["cells"]), int(capacity["events"]), int(capacity["folios"])) == (126, 5607, 91))
    check("unique", len(panel) == len({row["event_id_sha256"] for row in panel}))
    check("withheld", {row["wrapper_choice_withheld"] for row in panel} == {"WITHHELD_UNTIL_SCORING"})
    check("features", {row["line_first"] for row in panel} <= {"0", "1"} and {row["prev_dy"] for row in panel} <= {"0", "1"})
    check("f84", not any(row["page"].startswith("f84") or row["locus"].startswith("f84") for row in panel) and not any(design["f84"].values()))
    check("hashes", all(design["inputs"][name] == sha(R / name) for name in design["inputs"]) and all(design["outputs"][name] == sha(R / name) for name in design["outputs"]))
    validation = {"schema": "GDT318_DESIGN_VALIDATION_V1", "status": "PASS", "checks_passed": len(checks), "checks": checks, "design_sha256": sha(DESIGN), "f84_rows": 0}
    validation["content_sha256"] = canonical_hash(validation)
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": "PASS", "checks": len(checks)}, sort_keys=True))


if __name__ == "__main__":
    main()
