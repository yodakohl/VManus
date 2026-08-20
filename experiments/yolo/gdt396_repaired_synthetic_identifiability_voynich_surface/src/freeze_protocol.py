#!/usr/bin/env python3
"""Freeze the GDT396 surface/interface/scoring protocol before corpus use."""

from __future__ import annotations

import hashlib
import json
import platform
from pathlib import Path

from surface_channel import OFFICIAL_STA_FAMILY_NAMES, salt_commitment, sha256


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt396_repaired_synthetic_identifiability_voynich_surface"
G395 = ROOT / "experiments/yolo/gdt395_adversarial_synthetic_identifiability_benchmark"
OUT = EXP / "artifacts/gdt396_protocol_freeze.json"
SALT = EXP / ".work/sealed/surface_salt.hex"

REQUIRED_G395 = {
    "experiments/yolo/gdt395_adversarial_synthetic_identifiability_benchmark/WORLD_DESIGN_CONTRACT.md": "bc06c0bd8fc1c15b133090a720cd64ebd6db312e16e8b8ac283feb1df8f368c0",
    "experiments/yolo/gdt395_adversarial_synthetic_identifiability_benchmark/artifacts/gdt395_interface_freeze.json": "9a36477af1d77ddfa5c07608e593281ec001598db4a1d6f4f1537afe25e628cf",
    "experiments/yolo/gdt395_adversarial_synthetic_identifiability_benchmark/artifacts/gdt395_world_panel_freeze.json": "a6902f982eff9058b24748e38535f53c857d9e76928ebafff938b0de988b5b98",
    "experiments/yolo/gdt395_adversarial_synthetic_identifiability_benchmark/artifacts/gdt395_world_panel_validation.json": "8fd2c6f94e5691465943251dcf62437f886e4c48b634f7fd1f26dd2c3df6814d",
    "experiments/yolo/gdt395_adversarial_synthetic_identifiability_benchmark/artifacts/gdt395_corpus_manifest.tsv": "2564e294576610b2a399c37241a35f2a7bfb14779fde873b20641c01ffc4def2",
    "experiments/yolo/gdt395_adversarial_synthetic_identifiability_benchmark/artifacts/gdt395_corpus_generation_audit.json": "15c10b0363e66131dadf7bd1ce6e3d7a10a741ea4800f3ffc38446d94be003db",
    "experiments/yolo/gdt395_adversarial_synthetic_identifiability_benchmark/src/world_api.py": "add4b987cce7a36c2bb7e109995596b8d655c93f7c3cd96f534a5cf70ea606ef",
    "experiments/yolo/gdt395_adversarial_synthetic_identifiability_benchmark/src/normalize_bundle.py": "69afd4425f5e8f1f0f2d28c18394a1b9b45f23d1f6e3a608635dcabada03fd8a",
    "experiments/semantic_assumptions/LRG001_OFFICIAL_ALPHABET_RECOVERY_SPEC.md": "744e4500b0c4c9627254a80e0bce3878ff16a8d669cb947ace1005f940987c5d",
}
PROTOCOL_FILES = (
    "README.md", "METHOD.md", "CLAIM_INTERFACE.md", "DECODER_QUALIFICATION_SPEC.md",
    "SCORING_DESIGN.md", "VALIDATION_DESIGN.md", "src/surface_channel.py",
    "src/generate_paired_corpora.py", "src/decoder_api_v2.py", "src/freeze_protocol.py",
    "src/validate_protocol.py",
)
SEED_BLOCKS = {
    "legacy": list(range(0, 20)),
    "development": list(range(3960000, 3960005)),
    "qualification": list(range(3961000, 3961005)),
    "confirmation": list(range(3962000, 3962005)),
}


def content_hash(value: dict) -> str:
    clean = dict(value); clean.pop("content_sha256", None)
    return hashlib.sha256(json.dumps(clean, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main() -> int:
    if OUT.exists():
        raise RuntimeError(f"refusing to overwrite frozen protocol {OUT}")
    for relpath, expected in REQUIRED_G395.items():
        observed = sha256(ROOT / relpath)
        if observed != expected:
            raise RuntimeError(f"frozen input mismatch {relpath}: {observed}")
    panel = json.loads((G395 / "artifacts/gdt395_world_panel_freeze.json").read_text(encoding="utf-8"))
    if panel["status"] != "FROZEN_BEFORE_CORPUS_GENERATION_AND_DECODING" or len(panel["worlds"]) != 10:
        raise RuntimeError("bad GDT395 world panel")
    generators = {}
    designs = {}
    metas = {}
    for world in panel["worlds"]:
        wid = world["world_id"]
        generator = ROOT / world["directory"] / "generator.py"
        design = ROOT / world["directory"] / "DESIGN.md"
        if sha256(generator) != world["generator_sha256"] or sha256(design) != world["design_sha256"]:
            raise RuntimeError(f"{wid}: GDT395 world source mismatch")
        generators[str(generator.relative_to(ROOT))] = world["generator_sha256"]
        designs[str(design.relative_to(ROOT))] = world["design_sha256"]
        metas[wid] = world["final_observation_meta"]
    salt = bytes.fromhex(SALT.read_text(encoding="ascii").strip())
    result = {
        "schema": "GDT396_PROTOCOL_FREEZE_V1",
        "status": "FROZEN_BEFORE_DEVELOPMENT_CORPUS_GENERATION",
        "experiment": "GDT396",
        "python": platform.python_version(),
        "gdt395_required_hashes": REQUIRED_G395,
        "generator_hashes": generators,
        "design_hashes": designs,
        "world_meta_sha256": hashlib.sha256(json.dumps(metas, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
        "world_ids": sorted(metas),
        "target_events_per_seed": 8448,
        "seed_blocks": SEED_BLOCKS,
        "surface_channels": ["FREE_SURFACE", "VOYNICH_SURFACE"],
        "constrained_surface_schema": "GDT396_STA24_FIXED_WIDTH2_BINARY_V1",
        "official_sta_family_inventory_names": OFFICIAL_STA_FAMILY_NAMES,
        "official_sta_family_positions": len(OFFICIAL_STA_FAMILY_NAMES),
        "visible_transport": "RAW_ATOM_BYTES_0_TO_23_WITH_LENGTH_PREFIX_GZIP",
        "mapping_width": 2,
        "mapping_salt_commitment": salt_commitment(salt),
        "mapping_salt_revealed_to_decoders": False,
        "voynich_corpus_files_opened": 0,
        "voynich_rows": 0,
        "f84": {"allowed": False, "opened": False, "rows": 0},
        "f84r": {"allowed": False, "opened": False, "rows": 0},
        "protocol_hashes": {rel: sha256(EXP / rel) for rel in PROTOCOL_FILES},
        "confirmation_generated": False,
        "claim_ceiling": "Synthetic instrument calibration only; no synthetic role, code, ontology, or score transfers to Voynich.",
    }
    result["content_sha256"] = content_hash(result)
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
