#!/usr/bin/env python3
"""Independent observation-only validation of the GDT395 blind-claim freeze."""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
EXP = ROOT / "experiments/yolo/gdt395_adversarial_synthetic_identifiability_benchmark"
CLAIMS = EXP / ".work/claims"
CORPUS_ROOT = EXP / ".work/corpora"
PAIR_ROOT = EXP / ".work/pair_blind"
MANIFEST = CLAIMS / "blind_claim_manifest_all.tsv"
FREEZE = EXP / "artifacts/gdt395_blind_claims_freeze.json"
OUT = EXP / "artifacts/gdt395_blind_claims_validation.json"
CORPUS = EXP / "artifacts/gdt395_corpus_manifest.tsv"
PAIR = EXP / "artifacts/gdt395_pair_blind_manifest.tsv"
DECODER_FREEZE = EXP / "artifacts/gdt395_decoder_panel_freeze.json"
RECOVERY_FREEZE = EXP / "artifacts/gdt395_v3_interruption_recovery_freeze.json"
RECOVERY_RESULT = EXP / "artifacts/gdt395_v3_interruption_recovery_result.json"
RECOVERY_VALIDATION = EXP / "artifacts/gdt395_v3_interruption_recovery_validation.json"
REPS = {
    "FULL_GROUP", "HOST_LIKE", "COMPOSITE_STATE", "INFERRED_COMPONENTS",
    "CONSTRUCTION_SPAN", "RECORD_TOPOLOGY",
}
CLAIM_FIELDS = (
    "world_id", "corpus_seed", "event_id", "representation", "decoder_id",
    "entity_cluster", "lexical_cluster", "stem_cluster", "function_cluster",
    "operator_cluster", "construction_cluster", "register_variant_cluster",
    "semantic_category_cluster", "predicted_relation_target_event_id",
    "predicted_reference_target_event_id", "predicted_scope_start_event_id",
    "predicted_scope_end_event_id", "productive_component_prediction",
    "fossilized_component_prediction", "record_schema_cluster", "confidence",
)
ENDPOINT_FIELDS = {
    "predicted_relation_target_event_id", "predicted_reference_target_event_id",
    "predicted_scope_start_event_id", "predicted_scope_end_event_id",
}
REQUIRED_IMPLEMENTATION = {
    "artifacts/gdt395_decoder_panel_freeze.json",
    "artifacts/gdt395_decoder_panel_validation.json",
    "artifacts/gdt395_decoder_execution_correction.json",
    "artifacts/gdt395_decoder_execution_correction_validation.json",
    "artifacts/gdt395_decoder_execution_v3_correction.json",
    "artifacts/gdt395_decoder_execution_v3_correction_validation.json",
    "artifacts/gdt395_runner_cache_equivalence_validation.json",
    "SCORING_DESIGN.md",
    "SCORING_REVIEW.md",
    "VALIDATION_DESIGN.md",
    "VALIDATION_REVIEW.md",
    "INTERRUPTION_RECOVERY.md",
    "artifacts/gdt395_v3_interruption_recovery_freeze.json",
    "artifacts/gdt395_v3_interruption_recovery_result.json",
    "artifacts/gdt395_v3_interruption_recovery_validation.json",
    "artifacts/gdt395_corpus_manifest.tsv",
    "artifacts/gdt395_pair_blind_manifest.tsv",
    "src/decoder_api.py",
    "src/run_blind_decoders.py",
    "src/run_blind_decoders_v2.py",
    "src/run_blind_decoders_v3.py",
    "src/freeze_blind_claims.py",
    "src/score_identifiability.py",
    "src/validate_blind_claims.py",
    "src/validate_identifiability.py",
    "src/freeze_v3_interrupted_recovery.py",
    "src/recover_v3_interrupted_completion.py",
    "src/validate_v3_interrupted_completion.py",
}


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def tsv(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def repo_path(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT.resolve()))


def valid_content(data: dict) -> bool:
    copy = dict(data)
    expected = copy.pop("content_sha256", "")
    raw = json.dumps(copy, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(raw).hexdigest() == expected


def observation_ids(path: Path, world: str, seed: int) -> set[str]:
    opener = gzip.open if path.suffix == ".gz" else open
    found = set()
    with opener(path, "rt", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        if not {"world_id", "corpus_seed", "event_id"}.issubset(reader.fieldnames or ()):
            raise RuntimeError(f"observation identity fields missing: {path}")
        for row in reader:
            if row["world_id"] != world or int(row["corpus_seed"]) != seed:
                raise RuntimeError(f"observation provenance mismatch: {path}")
            if row["event_id"] in found:
                raise RuntimeError(f"duplicate observation event: {path}")
            found.add(row["event_id"])
    return found


def validate_claim_file(path: Path, manifest_row: dict,
                        expected: set[str]) -> tuple[int, bool, bool]:
    opener = gzip.open if path.suffix == ".gz" else open
    count = 0
    shape = provenance = values = True
    seen = set()
    with opener(path, "rt", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        shape &= tuple(reader.fieldnames or ()) == CLAIM_FIELDS
        for claim in reader:
            count += 1
            event = claim.get("event_id", "")
            provenance &= (
                claim.get("world_id") == manifest_row["world_id"]
                and claim.get("corpus_seed") == manifest_row["held_seed"]
                and claim.get("representation") == manifest_row["representation"]
                and claim.get("decoder_id") == manifest_row["decoder_id"]
                and event in expected and event not in seen
            )
            seen.add(event)
            try:
                confidence = float(claim.get("confidence", "nan"))
                values &= 0.0 <= confidence <= 1.0
            except ValueError:
                values = False
            for field in ENDPOINT_FIELDS:
                value = claim.get(field, "")
                values &= value == "UNRESOLVED" or value in expected
    provenance &= seen == expected
    return count, shape and provenance, values


def main() -> None:
    freeze = json.loads(FREEZE.read_text())
    rows = tsv(MANIFEST)
    corpus_rows = tsv(CORPUS)
    pair_rows = tsv(PAIR)
    corpus_events = {(r["world_id"], int(r["corpus_seed"])): int(r["events"]) for r in corpus_rows}
    pair_events = {(r["pair_id"], r["world_id"], int(r["corpus_seed"])): int(r["events"]) for r in pair_rows}
    corpus_paths = {
        (r["world_id"], int(r["corpus_seed"])): CORPUS_ROOT / r["observation_relpath"]
        for r in corpus_rows
    }
    pair_paths = {
        (r["pair_id"], r["world_id"], int(r["corpus_seed"])): PAIR_ROOT / r["observation_relpath"]
        for r in pair_rows
    }
    checks = {}
    checks["status"] = (
        freeze.get("schema") == "GDT395_BLIND_CLAIMS_FREEZE_V2"
        and freeze.get("status") == "PASS"
        and freeze.get("phase") == "FROZEN_BEFORE_ORACLE_ACCESS"
        and freeze.get("oracle_blind") is True
    )
    implementation = freeze.get("bindings", {}).get("implementation", {}).get("hashes", {})
    checks["bindings"] = (
        set(implementation) == REQUIRED_IMPLEMENTATION
        and all(sha(EXP / rel) == digest for rel, digest in implementation.items())
    )
    manifest_binding = freeze.get("claim_manifest", {})
    checks["manifest_hash"] = (
        manifest_binding.get("path") == repo_path(MANIFEST)
        and sha(MANIFEST) == manifest_binding.get("sha256")
    )
    checks["counts"] = len(rows) == freeze["claim_file_count"] == 2150
    checks["mode_counts"] = (
        sum(r["mode"] == "world_claim" for r in rows) == freeze["world_claim_file_count"] == 50
        and sum(r["mode"] != "world_claim" for r in rows) == freeze["event_claim_file_count"] == 2100
    )
    exact_keys = set()
    hashes = shapes = path_safe = identity = confidence = claim_bindings = values = True
    expected_cache = {}
    frozen_by_role = {}
    frozen_claims = {}
    for kind in ("authentic_event_claims", "pair_event_claims", "world_claims"):
        items = freeze.get("bindings", {}).get(kind, [])
        frozen_by_role[kind] = {}
        for item in items:
            frozen_by_role[kind][item.get("path", "")] = item.get("sha256", "")
            frozen_claims[item.get("path", "")] = item.get("sha256", "")
    for row in rows:
        rel = Path(row["claim_relpath"])
        path_safe &= not rel.is_absolute() and ".." not in rel.parts
        path = CLAIMS / rel
        hashes &= path.is_file() and sha(path) == row["claim_sha256"]
        role = {
            "authentic": "authentic_event_claims",
            "pair": "pair_event_claims",
            "world_claim": "world_claims",
        }.get(row["mode"], "")
        bound_path = repo_path(path)
        claim_bindings &= (
            bool(role)
            and frozen_by_role.get(role, {}).get(bound_path) == row["claim_sha256"]
            and sum(bound_path in bindings for bindings in frozen_by_role.values()) == 1
        )
        held_key = -1 if row["held_seed"] == "NONE" else int(row["held_seed"])
        key = (row["mode"], row["pair_id"], row["world_id"], held_key, row["decoder_id"], row["representation"])
        exact_keys.add(key)
        if row["mode"] == "world_claim":
            payload = json.loads(path.read_text())
            shapes &= set(payload) == {"decoder_id", "architecture_cluster", "language_like", "notation_like", "codebook_like", "semantics_light_like", "confidence"}
            identity &= payload.get("decoder_id") == row["decoder_id"]
            confidence &= 0.0 <= float(payload.get("confidence", -1)) <= 1.0
            continue
        if row["mode"] == "authentic":
            obs_key = (row["world_id"], int(row["held_seed"]))
            expected_n = corpus_events[obs_key]
            cache_key = ("authentic", *obs_key)
            if cache_key not in expected_cache:
                expected_cache[cache_key] = observation_ids(
                    corpus_paths[obs_key], row["world_id"], int(row["held_seed"])
                )
        else:
            obs_key = (row["pair_id"], row["world_id"], int(row["held_seed"]))
            expected_n = pair_events[obs_key]
            cache_key = ("pair", *obs_key)
            if cache_key not in expected_cache:
                expected_cache[cache_key] = observation_ids(
                    pair_paths[obs_key], row["world_id"], int(row["held_seed"])
                )
        n, valid_shape, valid_values = validate_claim_file(
            path, row, expected_cache[cache_key]
        )
        shapes &= valid_shape and n == int(row["events"]) == expected_n
        values &= valid_values
    expected_keys = set()
    decoders = sorted({r["decoder_id"] for r in rows})
    for world in sorted({k[0] for k in corpus_events}):
        for decoder in decoders:
            expected_keys.add(("world_claim", "NONE", world, -1, decoder, "ALL_TRAIN_OBSERVATIONS"))
            for seed in range(15, 20):
                for rep in REPS:
                    expected_keys.add(("authentic", "NONE", world, seed, decoder, rep))
    for pair_id, world, _ in pair_events:
        for seed in range(15, 20):
            for decoder in decoders:
                for rep in REPS:
                    expected_keys.add(("pair", pair_id, world, seed, decoder, rep))
    checks["exact_matrix"] = exact_keys == expected_keys and len(decoders) == 5
    decoder_freeze = json.loads(DECODER_FREEZE.read_text())
    frozen_decoder_map = {r["meta"]["decoder_id"]: r for r in decoder_freeze["decoders"]}
    implementation_map = freeze.get("implementation_map", {})
    checks["implementation_map"] = (
        set(implementation_map) == set(decoders) == set(frozen_decoder_map)
        and all(
            implementation_map[decoder]["decoder_id"] == decoder
            and implementation_map[decoder]["oracle_blind"] is True
            and implementation_map[decoder]["source_sha256"] == frozen_decoder_map[decoder]["source_sha256"]
            and implementation_map[decoder]["model_family"] == (
                "LUNA" if "luna" in frozen_decoder_map[decoder]["meta"]["designer_model"].lower()
                else "SOL" if "sol" in frozen_decoder_map[decoder]["meta"]["designer_model"].lower()
                else "UNRESOLVED"
            )
            for decoder in decoders
        )
        and sum(implementation_map[d]["model_family"] == "SOL" for d in decoders) == 2
        and sum(implementation_map[d]["model_family"] == "LUNA" for d in decoders) == 3
    )
    checks["file_hashes"] = hashes
    checks["claim_bindings"] = claim_bindings and len(frozen_claims) == len(rows)
    checks["claim_shapes"] = shapes
    checks["claim_values"] = values
    checks["safe_paths"] = path_safe
    checks["world_claim_identity"] = identity
    checks["confidence"] = confidence
    checks["no_oracle_interface"] = "oracle" not in MANIFEST.read_text().lower()
    checks["seal"] = not freeze["oracle_opened"] and freeze["oracle_rows_read"] == freeze["voynich_rows"] == 0 and not any(freeze["f84"].values())
    recovery_freeze = json.loads(RECOVERY_FREEZE.read_text())
    recovery_result = json.loads(RECOVERY_RESULT.read_text())
    recovery_validation = json.loads(RECOVERY_VALIDATION.read_text())
    recovery_bindings = recovery_validation.get("bindings", {})
    checks["interruption_recovery"] = (
        valid_content(recovery_freeze)
        and valid_content(recovery_result)
        and valid_content(recovery_validation)
        and recovery_validation.get("schema") == "GDT395_V3_INTERRUPTION_RECOVERY_VALIDATION_V1"
        and recovery_validation.get("status") == "PASS"
        and recovery_validation.get("checks_total") == recovery_validation.get("checks_passed")
        and bool(recovery_validation.get("checks"))
        and all(type(value) is bool and value
                for value in recovery_validation.get("checks", {}).values())
        and recovery_bindings.get("freeze_sha256") == sha(RECOVERY_FREEZE)
        and recovery_bindings.get("result_sha256") == sha(RECOVERY_RESULT)
        and recovery_bindings.get("manifest_sha256") == sha(MANIFEST)
        and recovery_result.get("recovery_freeze_sha256") == sha(RECOVERY_FREEZE)
        and recovery_result.get("claim_manifest_sha256") == sha(MANIFEST)
    )
    freeze_checks = freeze.get("checks", {})
    checks["freeze_checks"] = (
        isinstance(freeze_checks, dict) and bool(freeze_checks)
        and all(type(value) is bool and value for value in freeze_checks.values())
    )
    tmp = dict(freeze); expected_hash = tmp.pop("content_sha256")
    checks["content_hash"] = hashlib.sha256(json.dumps(tmp, sort_keys=True, separators=(",", ":")).encode()).hexdigest() == expected_hash
    result = {
        "schema": "GDT395_BLIND_CLAIMS_VALIDATION_V2",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "checks_passed": sum(checks.values()), "checks_total": len(checks),
        "freeze_sha256": sha(FREEZE),
        "bindings": {
            "claims_freeze": [{"path": repo_path(FREEZE), "sha256": sha(FREEZE)}],
        },
    }
    raw = json.dumps(result, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")
    result["content_sha256"] = hashlib.sha256(raw).hexdigest()
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": result["status"], "checks": f"{result['checks_passed']}/{result['checks_total']}"}, sort_keys=True))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
