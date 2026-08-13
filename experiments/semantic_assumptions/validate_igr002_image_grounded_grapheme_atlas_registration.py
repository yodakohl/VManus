#!/usr/bin/env python3
"""Validate the public, target-unopened IGR002 commitment envelope."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "experiments/semantic_assumptions"
RES = BASE / "results"
METHOD = BASE / "IGR002_IMAGE_GROUNDED_GRAPHEME_ATLAS_METHOD.md"
REGISTRATION = RES / "igr002_image_grounded_grapheme_atlas_registration.json"
OUT = RES / "igr002_image_grounded_grapheme_atlas_registration_validation.json"

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main() -> None:
    if OUT.exists():
        raise SystemExit("refusing overwrite")
    r = json.loads(REGISTRATION.read_text())
    checks = {
        "canonical_registration": REGISTRATION.read_bytes() == (json.dumps(r, sort_keys=True, separators=(",", ":")) + "\n").encode(),
        "method_hash_bound": r["commitments"]["method_sha256"] == sha(METHOD),
        "seven_sha256_commitments": len(r["commitments"]) == 7 and all(re.fullmatch(r"[0-9a-f]{64}", value) for value in r["commitments"].values()),
        "exact_counts": r["counts"] == {"types": 8, "targets": 32, "primary_targets": 28, "diagnostic_targets": 4, "new_physical_folios": 25, "excluded_igr001_folios": 19},
        "exact_gates": r["gates"] == {"localized_primary_targets": 24, "exact_signature_matches": 20, "types_with_at_least_three_of_four_matches": 6},
        "all_target_access_closed": r["access"] == {"private_builder_published": False, "private_nonce_published": False, "private_selection_published": False, "private_validator_published": False, "shape_reviewer_target_crops_opened": False, "target_image_bodies_opened": False},
        "frozen_status_decision": r["status"] == "FROZEN_PRIVATE_SELECTION_HASH_COMMITMENT_BEFORE_TARGET_IMAGE_ACCESS" and r["decision"] == "AUTHORIZE_SOURCE_LOCALIZATION_THEN_FRESH_CROP_ONLY_SHAPE_REVIEW",
        "release_after_seal_only": r["release_rule"] == "Publish the committed private builder selection worklist validator and join only after all crop-only shape judgments are sealed.",
        "no_nonce_or_type_join_in_public_envelope": "nonce" not in json.dumps(r).lower().replace("private_nonce_published", "") and "prototype" not in json.dumps(r).lower() and "targets" not in r,
        "claim_ceiling": "translation" in r["claim_ceiling"] and "select a reading" in r["claim_ceiling"],
    }
    if not all(checks.values()):
        raise SystemExit({key: value for key, value in checks.items() if not value})
    out = {"status": f"PASS_{len(checks)}_CHECK_IGR002_REGISTRATION_VALIDATION", "check_count": len(checks), "checks": list(checks), "registration_sha256": sha(REGISTRATION), "method_sha256": sha(METHOD)}
    OUT.write_text(json.dumps(out, sort_keys=True, separators=(",", ":")) + "\n")

if __name__ == "__main__": main()
