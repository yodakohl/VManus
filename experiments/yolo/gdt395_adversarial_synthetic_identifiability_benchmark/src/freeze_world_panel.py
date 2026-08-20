#!/usr/bin/env python3
"""Hash and audit all isolated GDT395 world designs before corpus decoding."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

from world_api import validate_rows
from normalize_bundle import normalize_bundle, validate_canonical

ROOT = Path(__file__).resolve().parents[4]
EXP = ROOT / "experiments/yolo/gdt395_adversarial_synthetic_identifiability_benchmark"
INTERFACE = EXP / "artifacts/gdt395_interface_freeze.json"
OUT = EXP / "artifacts/gdt395_world_panel_freeze.json"
PAIR_AUDIT = EXP / "artifacts/gdt395_pair_matching_audit.tsv"
PAIR_MATCHES = EXP / "artifacts/gdt395_pair_matched_records.tsv"
DESIGNER_PROVENANCE = EXP / "artifacts/gdt395_designer_provenance.tsv"
PAIR_AMENDMENT = EXP / "artifacts/gdt395_pair_protocol_amendment.json"
PAIR_AMENDMENT_VALIDATION = EXP / "artifacts/gdt395_pair_protocol_amendment_validation.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path, name: str):
    if str(EXP) not in sys.path:
        sys.path.insert(0, str(EXP))
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> None:
    interface = json.loads(INTERFACE.read_text())
    rows = []
    for assignment in interface["world_assignments"]:
        wid = assignment["world_id"]
        paths = sorted((EXP / "worlds").glob(f"{wid.lower()}_*/generator.py"))
        if len(paths) != 1:
            raise RuntimeError(f"{wid}: one generator required")
        gen = paths[0]; design = gen.with_name("DESIGN.md")
        if not design.is_file():
            raise RuntimeError(f"{wid}: DESIGN.md absent")
        mod = load(gen, f"freeze_{wid}")
        bundle = mod.generate(39500 + int(wid[1:]), 300)
        validate_rows(mod.WORLD_META, bundle, 300)
        bundle = normalize_bundle(bundle)
        validate_rows(mod.WORLD_META, bundle, 300); validate_canonical(bundle)
        meta = mod.WORLD_META
        checks = {
            "assignment": meta["broad_family"] == assignment["broad_family"],
            "carrier": meta["carrier_profile"] == assignment["carrier_profile"],
            "pair": meta["adversarial_pair_id"] == assignment["adversarial_pair_id"],
            "organic": (not assignment["organic_required"]) or bool(meta["organic_evolution"]),
            "registers": len(meta["registers"]) >= 3,
            "hands": len(meta["hands"]) >= 2,
            "genealogy": len(bundle["genealogy"]) >= (6 if assignment["organic_required"] else 1),
        }
        if not all(checks.values()):
            raise RuntimeError(f"{wid}: {checks}")
        rows.append({
            "world_id": wid, "directory": str(gen.parent.relative_to(ROOT)),
            "generator_sha256": sha(gen), "design_sha256": sha(design),
            "smoke_events": len(bundle["observations"]), "codebook_rows": len(bundle["codebook"]),
            "genealogy_rows": len(bundle["genealogy"]), "meta": meta, "checks": checks,
            "final_observation_meta": meta,
            "designer_model": "gpt-5.6-sol", "designer_isolated": True,
        })
    data = {
        "schema": "GDT395_WORLD_PANEL_FREEZE_V1", "status": "FROZEN_BEFORE_CORPUS_GENERATION_AND_DECODING",
        "interface_sha256": sha(INTERFACE), "worlds": rows,
        "pair_matching_audit_sha256": sha(PAIR_AUDIT),
        "pair_matched_records_sha256": sha(PAIR_MATCHES),
        "pair_protocol_amendment_sha256": sha(PAIR_AMENDMENT),
        "pair_protocol_amendment_validation_sha256": sha(PAIR_AMENDMENT_VALIDATION),
        "designer_provenance_sha256": sha(DESIGNER_PROVENANCE),
        "document_hashes": {
            str(path.relative_to(ROOT)): sha(path)
            for path in [EXP / "METHOD.md", EXP / "PAIR_PROTOCOL_AMENDMENT.md"]
        },
        "implementation_hashes": {
            str(path.relative_to(ROOT)): sha(path)
            for path in [
                Path(__file__), EXP / "src/world_api.py", EXP / "src/normalize_bundle.py",
                EXP / "src/generate_corpora.py", EXP / "src/build_pair_matched_subpanels.py",
                EXP / "src/build_pair_blind_views.py", EXP / "src/freeze_pair_protocol_amendment.py",
                EXP / "src/validate_pair_protocol_amendment.py",
                EXP / "src/validate_pair_blind_views.py",
                EXP / "src/freeze_world_panel_stage.py",
                EXP / "src/validate_world_panel.py",
            ]
        },
        "voynich_rows": 0, "f84": {"opened": False, "parsed": False, "retained": False, "scored": False},
    }
    raw = json.dumps(data, sort_keys=True, separators=(",", ":")).encode()
    data["content_sha256"] = hashlib.sha256(raw).hexdigest()
    OUT.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"worlds": len(rows), "status": data["status"]}))


if __name__ == "__main__":
    main()
