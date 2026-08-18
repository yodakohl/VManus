#!/usr/bin/env python3
"""Independent validation of the GDT280 pre-score freeze."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

R = Path(__file__).resolve().parent


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def csha(value: dict) -> str:
    q = dict(value)
    q.pop("content_sha256", None)
    return hashlib.sha256(json.dumps(q, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()


def main() -> None:
    checks = []

    def check(name, condition):
        checks.append({"check": name, "pass": bool(condition)})
        assert condition, name

    design = json.loads((R / "gdt280_design.json").read_text())
    check("status", design["status"] == "FROZEN_BEFORE_GDT280_EDGE_SCORING")
    check("content_hash", design["content_sha256"] == csha(design))
    check("method_hash", design["method_sha256"] == sha(R / "GDT280_EDGE_COMPILER_FINE_DECOMPOSITION_METHOD.md"))
    check("freezer_hash", design["implementation_sha256"] == sha(R / "freeze_gdt280_edge_compiler_fine_decomposition.py"))
    with (R / "gdt280_gdt279_freeze_manifest.tsv").open(encoding="utf8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    check("manifest_hash", design["freeze_manifest_sha256"] == sha(R / "gdt280_gdt279_freeze_manifest.tsv"))
    check("manifest_count", len(rows) == 16)
    for row in rows:
        check("frozen:" + row["artifact"], sha(R / row["artifact"]) == row["frozen_sha256"])
    check("blocks", list(design["edge_blocks"]) == ["DISPLAY_RENDERER", "LOCAL_FRAME", "OUTER_WRAPPER", "RIGHT_FAMILY"] or set(design["edge_blocks"]) == {"OUTER_WRAPPER", "LOCAL_FRAME", "RIGHT_FAMILY", "DISPLAY_RENDERER"})
    check("subsets", design["subset_count"] == 16)
    check("null", design["null_worlds"] == 64 and design["context_bucket_count"] == 256)
    check("no_new_controls", design["new_control_corpora"] == 0)
    check("no_semantics", design["semantic_assignments"] == design["hpr1_semantics_used"] == design["voynich_substrings_mined"] == 0)
    check("f84", all(v in (0, False) for v in design["f84"].values()))
    result = {"schema": "GDT280_DESIGN_VALIDATION_V1", "status": "PASS", "checks": len(checks), "design_sha256": sha(R / "gdt280_design.json"), "validator_sha256": sha(Path(__file__))}
    result["content_sha256"] = csha(result)
    (R / "gdt280_design_validation.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": "PASS", "checks": len(checks)}, sort_keys=True))


if __name__ == "__main__":
    main()
