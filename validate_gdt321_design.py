#!/usr/bin/env python3
"""Validate GDT321 frozen two-rule architecture."""
import csv
import hashlib
import json
from pathlib import Path

R = Path(__file__).resolve().parent
DESIGN = R / "gdt321_design.json"
OUT = R / "gdt321_design_validation.json"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()


def main():
    checks = []
    def check(name, condition):
        if not condition:
            raise AssertionError(name)
        checks.append(name)
    design = json.loads(DESIGN.read_text())
    stored = design.pop("content_sha256")
    check("content", stored == canonical_hash(design))
    with (R / "gdt318_frozen_panel.tsv").open(encoding="utf8", newline="") as handle:
        panel = list(csv.DictReader(handle, delimiter="\t"))
    check("panel", len(panel) == 5607 and len({row["cell_id"] for row in panel}) == 126 and len({row["physical_folio"] for row in panel}) == 91)
    check("rules", design["models"]["ROBUST_TWO_RULE"]["parameters"] == ["s_X_line_first", "q_X_prev_dy"])
    check("charges", design["parameter_counts"] == {"ROBUST_TWO_RULE": 2, "FULL_GDT318_ANCHOR": 16})
    check("f84", not any(row["page"].startswith("f84") or row["locus"].startswith("f84") for row in panel) and not any(design["f84"].values()))
    check("hashes", all(design["inputs"][name] == sha(R / name) for name in design["inputs"]))
    validation = {"schema": "GDT321_DESIGN_VALIDATION_V1", "status": "PASS", "checks_passed": len(checks), "checks": checks, "design_sha256": sha(DESIGN), "f84_rows": 0}
    validation["content_sha256"] = canonical_hash(validation)
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": "PASS", "checks": len(checks)}, sort_keys=True))


if __name__ == "__main__":
    main()
