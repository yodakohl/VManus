#!/usr/bin/env python3
"""Validate the frozen GDT325 target inventory."""
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

R = Path(__file__).resolve().parent
OUT = R / "gdt325_design_validation.json"


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def canonical_hash(value): return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()
def read(name):
    with (R / name).open(encoding="utf8", newline="") as handle: return list(csv.DictReader(handle, delimiter="\t"))


def main():
    checks = []
    def check(name, condition):
        if not condition: raise AssertionError(name)
        checks.append(name)
    design = json.loads((R / "gdt325_design.json").read_text()); stored = design.pop("content_sha256")
    check("content", stored == canonical_hash(design))
    source = [row for row in read("gdt278_native_event_inventory.tsv") if row["control_id"] == "VOYNICH_REFERENCE"]
    check("source_f84", not any(row["page"].startswith("f84") or row["locus"].startswith("f84") for row in source))
    keys = tuple(design["cell_fields"]); cells = defaultdict(list)
    for row in source: cells[tuple(row[key] for key in keys)].append(row)
    powered = {key: value for key, value in cells.items() if len(value) >= 10 and len({row["physical_folio"] for row in value}) >= 3}
    targets = {key: value for key, value in cells.items() if key not in powered and 5 <= len(value) <= 9 and len({row["physical_folio"] for row in value}) >= 2 and key[1:] in {item[1:] for item in powered}}
    panel = read("gdt325_frozen_panel.tsv")
    check("capacity", len(powered) == 136 and len(targets) == 94 and len(panel) == 609 and len({row["physical_folio"] for row in panel}) == 85 and len({key[0] for key in targets}) == 84 and len({key[1:] for key in targets}) == 12)
    expected_ids = {hashlib.sha256(("CELL|" + "|".join(key)).encode()).hexdigest()[:20] for key in targets}
    check("cells", {row["cell_id"] for row in panel} == expected_ids)
    check("withheld", all(row["wrapper_outcome"] == "WITHHELD_UNTIL_SCORING" for row in panel))
    check("models", design["models"] == ["GLOBAL", "GLOBAL_TWO_RULE", "COORDINATE", "COORDINATE_TWO_RULE"])
    check("coefficients", abs(design["fixed_coefficients"]["s_X_line_first"] - 1.0021314958853849) < 1e-15 and abs(design["fixed_coefficients"]["q_X_prev_dy"] - .8920380870887143) < 1e-15)
    check("hashes", all(design["inputs"][name] == sha(R / name) for name in design["inputs"]) and all(design["outputs"][name] == sha(R / name) for name in design["outputs"]))
    validation = {"schema": "GDT325_DESIGN_VALIDATION_V1", "status": "PASS", "checks_passed": len(checks), "checks": checks, "design_sha256": sha(R / "gdt325_design.json"), "f84_rows": 0}; validation["content_sha256"] = canonical_hash(validation)
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": "PASS", "checks": len(checks)}, sort_keys=True))


if __name__ == "__main__": main()
