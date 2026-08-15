#!/usr/bin/env python3
"""Validate the GDT135 pre-target freeze."""
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PREDICTION = ROOT / "gdt135_prediction.json"
INVENTORY = ROOT / "gdt134_general_continuation_inventory.tsv"
OUT = ROOT / "gdt135_prediction_validation.json"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def csha(value):
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode()).hexdigest()


prediction = json.loads(PREDICTION.read_text())
checks = []


def check(name, value):
    checks.append({"check": name, "pass": bool(value)})
    assert value, name


check("status", prediction["status"] == "FROZEN_POSTSELECTED_BEFORE_TARGET_ARCHITECTURE_EXTRACTION")
with INVENTORY.open(encoding="utf-8", newline="") as handle:
    rows = [
        row
        for row in csv.DictReader(handle, delimiter="\t")
        if row["primary_continuation_pair"] == "1" and row["section"] == "B"
    ]
check("pairs", len(rows) == prediction["panel"]["pairs"] == 69)
check("pages", len({row["page"] for row in rows}) == prediction["panel"]["pages"] == 17)
check("folios", len({row["physical_folio"] for row in rows}) == prediction["panel"]["physical_folios"] == 9)
check("f84", not any(row["page"].startswith("f84") or row["locus"].startswith("f84") for row in rows))
check("models", prediction["models"] == ["COMPILER12", "HOST_CHAR3", "RAW_CHAR3"])
check("inputs", all(sha(ROOT / path) == digest for path, digest in prediction["inputs"].items()))
check("implementation", all(sha(ROOT / path) == digest for path, digest in prediction["implementation"].items()))
content = dict(prediction)
digest = content.pop("prediction_content_sha256")
check("content", csha(content) == digest)
validation = {
    "schema": "GDT135_SECTION_B_FIELD_ARCHITECTURE_PREDICTION_VALIDATION_V1",
    "status": "PASS_PRETARGET_FREEZE",
    "checks": len(checks),
    "passed": sum(row["pass"] for row in checks),
    "prediction_sha256": sha(PREDICTION),
    "validator_sha256": sha(Path(__file__)),
    "check_rows": checks,
}
OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n")
print(json.dumps({"status": validation["status"], "checks": validation["checks"]}, sort_keys=True))
