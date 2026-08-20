#!/usr/bin/env python3
"""Independent hash/schema validation of the frozen GDT396 protocol."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt396_repaired_synthetic_identifiability_voynich_surface"
FREEZE = EXP / "artifacts/gdt396_protocol_freeze.json"
OUT = EXP / "artifacts/gdt396_protocol_validation.json"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def content_hash(value: dict) -> str:
    clean = dict(value); clean.pop("content_sha256", None)
    return hashlib.sha256(json.dumps(clean, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main() -> int:
    frozen = json.loads(FREEZE.read_text(encoding="utf-8"))
    checks: dict[str, bool] = {}
    checks["schema_status"] = frozen.get("schema") == "GDT396_PROTOCOL_FREEZE_V1" and frozen.get("status") == "FROZEN_BEFORE_DEVELOPMENT_CORPUS_GENERATION"
    checks["content_hash"] = frozen.get("content_sha256") == content_hash(frozen)
    checks["ten_worlds"] = frozen.get("world_ids") == [f"W{i:02d}" for i in range(1, 11)] and len(frozen.get("generator_hashes", {})) == 10 and len(frozen.get("design_hashes", {})) == 10
    checks["seed_blocks"] = frozen.get("seed_blocks") == {
        "legacy": list(range(20)),
        "development": list(range(3960000, 3960005)),
        "qualification": list(range(3961000, 3961005)),
        "confirmation": list(range(3962000, 3962005)),
    }
    checks["seed_disjoint"] = len({v for values in frozen["seed_blocks"].values() for v in values}) == 35
    checks["surface_contract"] = frozen.get("official_sta_family_inventory_names") == "ABCDEFGHJKLMNPQRSTUVWXYZ" and frozen.get("official_sta_family_positions") == 24 and frozen.get("mapping_width") == 2 and frozen.get("surface_channels") == ["FREE_SURFACE", "VOYNICH_SURFACE"]
    checks["binary_transport"] = frozen.get("visible_transport") == "RAW_ATOM_BYTES_0_TO_23_WITH_LENGTH_PREFIX_GZIP" and frozen.get("constrained_surface_schema") == "GDT396_STA24_FIXED_WIDTH2_BINARY_V1"
    checks["salt_commitment"] = isinstance(frozen.get("mapping_salt_commitment"), str) and len(frozen["mapping_salt_commitment"]) == 64 and frozen.get("mapping_salt_revealed_to_decoders") is False
    checks["f84_seals"] = frozen.get("f84") == {"allowed": False, "opened": False, "rows": 0} and frozen.get("f84r") == {"allowed": False, "opened": False, "rows": 0}
    checks["no_voynich"] = frozen.get("voynich_corpus_files_opened") == 0 and frozen.get("voynich_rows") == 0
    checks["confirmation_closed"] = frozen.get("confirmation_generated") is False
    checks["gdt395_hashes"] = all(sha256(ROOT / path) == expected for path, expected in frozen.get("gdt395_required_hashes", {}).items())
    checks["generator_hashes"] = all(sha256(ROOT / path) == expected for path, expected in frozen.get("generator_hashes", {}).items())
    checks["design_hashes"] = all(sha256(ROOT / path) == expected for path, expected in frozen.get("design_hashes", {}).items())
    checks["protocol_hashes"] = all(sha256(EXP / path) == expected for path, expected in frozen.get("protocol_hashes", {}).items())
    result = {
        "schema": "GDT396_PROTOCOL_VALIDATION_V1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "checks_passed": sum(checks.values()),
        "checks_total": len(checks),
        "freeze_sha256": sha256(FREEZE),
        "validator_sha256": sha256(Path(__file__)),
        "voynich_corpus_files_opened": 0,
        "voynich_rows": 0,
        "f84": {"allowed": False, "opened": False, "rows": 0},
        "f84r": {"allowed": False, "opened": False, "rows": 0},
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
