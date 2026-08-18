#!/usr/bin/env python3
"""Validate the GDT279 pre-score freeze without importing its freezer."""
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
    return hashlib.sha256(
        json.dumps(q, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()
    ).hexdigest()


def main() -> None:
    checks: list[tuple[str, bool]] = []
    design = json.loads((R / "gdt279_design.json").read_text())
    checks.append(("status", design["status"] == "FROZEN_BEFORE_GDT279_BLOCK_SCORING"))
    checks.append(("content_hash", design["content_sha256"] == csha(design)))
    checks.append(("method_hash", design["method_sha256"] == sha(R / "GDT279_NATIVE_ORDER_COMPILER_DECOMPOSITION_METHOD.md")))
    checks.append(("freezer_hash", design["implementation_sha256"] == sha(R / "freeze_gdt279_native_order_compiler_decomposition.py")))
    with (R / "gdt279_gdt278_freeze_manifest.tsv").open(encoding="utf8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    checks.append(("manifest_hash", design["freeze_manifest_sha256"] == sha(R / "gdt279_gdt278_freeze_manifest.tsv")))
    checks.append(("manifest_count", len(rows) == 20))
    checks.extend((f"frozen:{row['artifact']}", sha(R / row["artifact"]) == row["frozen_sha256"]) for row in rows)
    checks.append(("blocks", list(design["blocks"]) == ["CLOSURE_BOUNDARY", "EDGE_COMPILER", "OPPORTUNITY"] or set(design["blocks"]) == {"OPPORTUNITY", "EDGE_COMPILER", "CLOSURE_BOUNDARY"}))
    checks.append(("all_subsets", design["subset_count"] == 8))
    checks.append(("null", design["null_worlds"] == 64 and design["context_bucket_count"] == 256))
    checks.append(("no_semantics", design["semantic_assignments"] == design["hpr1_semantics_used"] == design["voynich_substrings_mined"] == 0))
    checks.append(("no_new_controls", design["new_control_corpora"] == 0))
    checks.append(("f84", all(v in (0, False) for v in design["f84"].values())))
    failed = [name for name, ok in checks if not ok]
    assert not failed, failed
    result = {
        "schema": "GDT279_DESIGN_VALIDATION_V1",
        "status": "PASS",
        "checks": len(checks),
        "design_sha256": sha(R / "gdt279_design.json"),
        "validator_sha256": sha(Path(__file__)),
    }
    result["content_sha256"] = csha(result)
    (R / "gdt279_design_validation.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": "PASS", "checks": len(checks)}, sort_keys=True))


if __name__ == "__main__":
    main()
