#!/usr/bin/env python3
"""Development-only adversarial fixtures for the GDT396 claim contract."""

from __future__ import annotations

import copy
import hashlib
import json
import tempfile
from pathlib import Path
from types import SimpleNamespace

from decoder_api_v2 import TABLE_FIELDS, unresolved_outputs, validate_shape
from run_blind_decoders import (
    CANDIDATE_POLICY,
    boolean_roundtrip_selftest,
    complete_explicit_unsupported,
    validate_claims,
)
from phase_authority import content_hash, require_instrument
from qualify_decoders import semantic_w10_false_rates


def expect_failure(fn, label: str) -> None:
    try:
        fn()
    except (TypeError, ValueError, RuntimeError):
        return
    raise AssertionError(f"fixture did not fail: {label}")


def held_rows() -> list[dict]:
    common = {
        "phase": "DEVELOPMENT", "run_id": "FIXTURE", "world_id": "W00",
        "corpus_seed": 1, "surface_id": "FREE_SURFACE", "page_id": "P0",
        "paragraph_id": "Q0", "line_id": "L0", "record_id": "R0",
        "visible_surface": ("a",), "layout_role": "X",
    }
    return [
        common | {"event_id": "E0", "global_event_rank": 0, "record_event_ordinal": 0},
        common | {"event_id": "E1", "global_event_rank": 1, "record_event_ordinal": 1},
    ]


def main() -> int:
    boolean_roundtrip_selftest()

    # Python booleans are mandatory before TSV serialization. Strings that
    # look true/false must never silently become truthy claims.
    bad = unresolved_outputs()
    common = {
        "schema_version": 2, "phase": "DEVELOPMENT", "run_id": "FIXTURE",
        "world_id": "W00", "corpus_seed": 1, "surface_id": "FREE_SURFACE",
        "representation_id": "COMPOSITE_STATE", "decoder_id": "fixture",
        "method_variant": "PRIMARY", "property_id": "TEMPORAL_STATE_GATE",
        "unit_type": "EVENT", "unit_id": "E0", "claim_status": "RESOLVED",
        "predicted_bool": "TRUE", "confidence": 0.5,
    }
    bad["binary_claims"].append(common)
    expect_failure(lambda: validate_shape(bad), "string boolean")

    # Exercise runner completion, candidate universes, source/target locality,
    # scope endpoint rules, and complete nine-table shape together.
    module = SimpleNamespace(DECODER_META={"decoder_id": "fixture", "max_rank_by_claim_kind": {
        "GENERIC_RELATION": 5, "COORDINATOR_RELATION": 5, "ALTERNATIVE_RELATION": 5,
        "REFERENCE_ANAPHORA": 5, "ENTITY_REUSE_ANTECEDENT": 5,
        "MORPHOLOGY_ANALYSIS": 3,
    }})
    held = held_rows(); outputs = unresolved_outputs()
    complete_explicit_unsupported(outputs, module, held, "RECORD_TOPOLOGY")
    validate_claims(outputs, module, held, "RECORD_TOPOLOGY", "DEVELOPMENT", "FIXTURE")
    assert set(outputs) == set(TABLE_FIELDS)

    malformed = copy.deepcopy(outputs)
    malformed["target_queries"][0]["candidate_set_id"] = "HASHED_PRIVATE_UNIVERSE"
    expect_failure(
        lambda: validate_claims(malformed, module, held, "RECORD_TOPOLOGY", "DEVELOPMENT", "FIXTURE"),
        "private candidate universe",
    )

    malformed = copy.deepcopy(outputs)
    duplicate = copy.deepcopy(malformed["target_queries"][0]); duplicate["confidence"] = 0.75
    malformed["target_queries"].append(duplicate)
    expect_failure(
        lambda: validate_claims(malformed, module, held, "RECORD_TOPOLOGY", "DEVELOPMENT", "FIXTURE"),
        "conflicting logical duplicate",
    )

    scope_outputs = unresolved_outputs()
    complete_explicit_unsupported(scope_outputs, module, held, "CONSTRUCTION_SPAN")
    malformed = copy.deepcopy(scope_outputs)
    malformed["scope_claims"][0]["predicted_start_event_id"] = "E0"
    expect_failure(
        lambda: validate_claims(malformed, module, held, "CONSTRUCTION_SPAN", "DEVELOPMENT", "FIXTURE"),
        "negative scope endpoint",
    )

    assert CANDIDATE_POLICY == {
        "GENERIC_RELATION": "RECORD_EXCL_SELF",
        "COORDINATOR_RELATION": "RECORD_EXCL_SELF",
        "ALTERNATIVE_RELATION": "RECORD_EXCL_SELF",
        "REFERENCE_ANAPHORA": "PRIOR_SEED_EVENTS",
        "ENTITY_REUSE_ANTECEDENT": "PRIOR_SEED_EVENTS",
    }

    # A stored PASS cannot authorize execution after any bound byte changes.
    with tempfile.TemporaryDirectory(prefix="gdt396-authority-") as name:
        root=Path(name);(root/"artifacts").mkdir();(root/"bound.txt").write_text("A",encoding="utf-8")
        digest=hashlib.sha256((root/"bound.txt").read_bytes()).hexdigest()
        frozen={"schema":"FIXTURE","status":"FROZEN_BEFORE_QUALIFICATION_GENERATION","bindings":{"bound.txt":digest},"decoders":[]}
        frozen["content_sha256"]=content_hash(frozen)
        freeze_path=root/"artifacts/gdt396_decoder_panel_freeze.json";freeze_path.write_text(json.dumps(frozen),encoding="utf-8")
        freeze_digest=hashlib.sha256(freeze_path.read_bytes()).hexdigest()
        (root/"artifacts/gdt396_decoder_panel_validation.json").write_text(json.dumps({"status":"PASS","freeze_sha256":freeze_digest}),encoding="utf-8")
        require_instrument(root,"QUALIFICATION")
        (root/"bound.txt").write_text("B",encoding="utf-8")
        expect_failure(lambda:require_instrument(root,"QUALIFICATION"),"stale PASS after binding drift")

    # The semantics-light guard is mandatory. An absent W10 route must not be
    # interpreted as a zero false-positive rate.
    expect_failure(
        lambda: semantic_w10_false_rates(
            [], "fixture", "FUNCTION_OPERATOR_CLASS", "MULTI_RESOLUTION", "VOYNICH_SURFACE",
        ),
        "absent W10 semantics-light panel",
    )

    print("PASS 9/9")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
