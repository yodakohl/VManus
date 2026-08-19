#!/usr/bin/env python3
"""Validate the pre-oracle GDT381 freeze."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "experiments/yolo/gdt381_relational_topology_transfer"
ART = BASE / "artifacts"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def content(obj: dict) -> str:
    clone = dict(obj); clone.pop("content_hash", None)
    return hashlib.sha256(json.dumps(clone, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main() -> None:
    design = json.loads((ART / "gdt381_comparator_topology_freeze.json").read_text())
    result = json.loads((ART / "gdt381_comparator_freeze_result.json").read_text())
    checks = []
    def check(name: str, ok: bool) -> None:
        checks.append({"check": name, "pass": bool(ok)})
        if not ok: raise AssertionError(name)
    check("design_hash", design["content_hash"] == content(design))
    check("result_hash", result["content_hash"] == content(result))
    check("five_families", [x["id"] for x in design["anonymous_topologies"]] == [f"CMP_TOPOLOGY_0{i}" for i in range(1, 6)])
    check("domain_local_classes", design["latent_classes"]["scope"].startswith("LEARNED_INDEPENDENTLY"))
    check("no_class_alignment", design["latent_classes"]["cross_domain_class_alignment"] is False)
    check("oracle_unused", design["latent_classes"]["oracle_labels_used"] is False and result["hidden_oracle_evaluated"] is False)
    check("trivial_baseline", "TRIVIAL_MOTIF_BASELINE" in design["models"])
    check("joint_null", design["null"]["worlds"] == 2048 and design["null"]["maxT"].startswith("FIVE_TOPOLOGIES"))
    check("voynich_unread", design["voynich_rows_read"] == 0 and result["voynich_rows_read"] == 0)
    check("dedup", not design["route_deduplication"]["gdt378_to_380_local_or_identity_search_reopened"] and not design["route_deduplication"]["gdt345_to_347_coordinate_operator_manifold_reopened"])
    check("f84_false", all(v is False for v in design["f84"].values()) and all(v is False for v in result["f84"].values()))
    for path, digest in design["inputs"].items(): check("input_" + path.replace("/", "_"), sha(ROOT / path) == digest)
    for section in ["documents", "implementation", "outputs"]:
        for path, digest in result[section].items(): check(section + "_" + path.replace("/", "_"), sha(ROOT / path) == digest)
    out = {"schema": "GDT381_FREEZE_VALIDATION_V1", "status": "PASS", "checks_passed": len(checks), "checks_total": len(checks), "checks": checks, "result_hash": sha(ART / "gdt381_comparator_freeze_result.json"), "f84": {"opened": False, "parsed": False, "retained": False, "scored": False}}
    out["content_hash"] = content(out)
    (ART / "gdt381_comparator_freeze_validation.json").write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(f"PASS {len(checks)}/{len(checks)}")


if __name__ == "__main__": main()
