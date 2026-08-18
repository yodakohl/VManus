#!/usr/bin/env python3
"""Validate the frozen GDT311 split, panel, and feature exclusions."""
import csv
import hashlib
import json
from pathlib import Path

R = Path(__file__).resolve().parent
PANEL = R / "gdt311_frozen_event_panel.tsv"
CAPACITY = R / "gdt311_capacity.tsv"
DESIGN = R / "gdt311_design.json"
OUT = R / "gdt311_design_validation.json"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical_hash(value):
    raw = json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()


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
    check("content_hash", stored == canonical_hash(design))
    panel = read(PANEL)
    capacity = {row["operation"]: row for row in read(CAPACITY)}
    expected = {
        "wrapper:ch>s": (7, 232, 150, 48),
        "wrapper:d>s": (8, 380, 262, 51),
        "wrapper:NONE>q": (38, 1225, 694, 394),
    }
    check(
        "capacity",
        all(
            (int(capacity[operation]["exact_pairs"]), int(capacity[operation]["training_events"]), int(capacity[operation]["test_events"]), int(capacity[operation]["test_target_events"])) == values
            for operation, values in expected.items()
        ),
    )
    check("event_total", len(panel) == 2943)
    check("unique_operation_event", len(panel) == len({(row["operation"], row["anonymous_event_id"]) for row in panel}))
    check("outcomes_withheld", {row["outcome_withheld"] for row in panel} == {"WITHHELD_UNTIL_SCORING"})
    check("test_split", all((int(hashlib.sha256(f"GDT311_SPLIT_V1|{row['physical_folio']}".encode()).hexdigest()[:8], 16) % 3 == 0) == (row["split"] == "TEST") for row in panel))
    check("position_bounds", all(0 <= float(row["relative_position"]) <= 1 for row in panel))
    check("f84_absent", not any(row["page"].startswith("f84") or row["locus"].startswith("f84") for row in panel))
    used = {name for names in design["models"].values() for name in names}
    check("forbidden_absent", not used.intersection(design["forbidden_predictors"]))
    check("input_hashes", all(design["inputs"][name] == sha(R / name) for name in design["inputs"]))
    check("output_hashes", all(design["outputs"][name] == sha(R / name) for name in design["outputs"]))
    check("f84_flags", not any(design["f84"].values()))
    result = {"schema": "GDT311_DESIGN_VALIDATION_V1", "status": "PASS", "checks_passed": len(checks), "checks": checks, "design_sha256": sha(DESIGN), "f84_rows": 0}
    result["content_sha256"] = canonical_hash(result)
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": "PASS", "checks": len(checks), "events": len(panel)}, sort_keys=True))


if __name__ == "__main__":
    main()
