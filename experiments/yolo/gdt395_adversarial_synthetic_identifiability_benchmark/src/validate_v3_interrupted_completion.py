#!/usr/bin/env python3
"""Validate GDT395 V3 interruption recovery without oracle access."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
EXP = ROOT / "experiments/yolo/gdt395_adversarial_synthetic_identifiability_benchmark"
CLAIMS = EXP / ".work/claims"
CORPUS = EXP / "artifacts/gdt395_corpus_manifest.tsv"
PAIR = EXP / "artifacts/gdt395_pair_blind_manifest.tsv"
DECODER_FREEZE = EXP / "artifacts/gdt395_decoder_panel_freeze.json"
FREEZE = EXP / "artifacts/gdt395_v3_interruption_recovery_freeze.json"
RESULT = EXP / "artifacts/gdt395_v3_interruption_recovery_result.json"
MANIFEST = CLAIMS / "blind_claim_manifest_all.tsv"
OUT = EXP / "artifacts/gdt395_v3_interruption_recovery_validation.json"
MISSING = "world_claims/W05/D01_MULTIVIEW_GRAPH/train_seeds_00_14.json"
FIELDS = (
    "mode", "pair_id", "world_id", "held_seed", "decoder_id",
    "representation", "events", "claim_relpath", "claim_sha256",
)
REPS = (
    "FULL_GROUP", "HOST_LIKE", "COMPOSITE_STATE", "INFERRED_COMPONENTS",
    "CONSTRUCTION_SPAN", "RECORD_TOPOLOGY",
)
RECOVERY_BINDINGS = {
    "INTERRUPTION_RECOVERY.md",
    "artifacts/gdt395_corpus_manifest.tsv",
    "artifacts/gdt395_pair_blind_manifest.tsv",
    "artifacts/gdt395_decoder_panel_freeze.json",
    "artifacts/gdt395_decoder_execution_v3_correction.json",
    "src/run_blind_decoders.py",
    "src/run_blind_decoders_v2.py",
    "src/run_blind_decoders_v3.py",
    "src/freeze_v3_interrupted_recovery.py",
    "src/recover_v3_interrupted_completion.py",
    "src/validate_v3_interrupted_completion.py",
    "decoders/d01_multiview_graph/decoder.py",
}
WORLD_CLAIM_FIELDS = {
    "decoder_id", "architecture_cluster", "language_like", "notation_like",
    "codebook_like", "semantics_light_like", "confidence",
}


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_hash(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(raw).hexdigest()


def valid_content(data: dict) -> bool:
    copy = dict(data)
    expected = copy.pop("content_sha256", "")
    return canonical_hash(copy) == expected


def tsv(path: Path) -> tuple[tuple[str, ...], list[dict]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        rows = list(reader)
        return tuple(reader.fieldnames or ()), rows


def expected_manifest_rows() -> dict[tuple[str, str, str, str, str, str], tuple[int, str]]:
    _, corpus = tsv(CORPUS)
    _, pairs = tsv(PAIR)
    decoder_freeze = json.loads(DECODER_FREEZE.read_text())
    decoders = tuple(sorted(row["meta"]["decoder_id"] for row in decoder_freeze["decoders"]))
    corpus_events = {
        (row["world_id"], int(row["corpus_seed"])): int(row["events"])
        for row in corpus
    }
    pair_events = {
        (row["pair_id"], row["world_id"], int(row["corpus_seed"])): int(row["events"])
        for row in pairs
    }
    expected = {}
    for world in sorted({world for world, _ in corpus_events}):
        for seed in range(15, 20):
            for decoder in decoders:
                for rep in REPS:
                    rel = f"authentic/{world}/{decoder}/seed_{seed:02d}_{rep}.tsv.gz"
                    expected[("authentic", "NONE", world, str(seed), decoder, rep)] = (
                        corpus_events[(world, seed)], rel,
                    )
        for decoder in decoders:
            rel = f"world_claims/{world}/{decoder}/train_seeds_00_14.json"
            expected[("world_claim", "NONE", world, "NONE", decoder,
                      "ALL_TRAIN_OBSERVATIONS")] = (1, rel)
    for pair_id, world in sorted({(pair_id, world) for pair_id, world, _ in pair_events}):
        for seed in range(15, 20):
            for decoder in decoders:
                for rep in REPS:
                    rel = f"pair/{pair_id}/{world}/{decoder}/seed_{seed:02d}_{rep}.tsv.gz"
                    expected[("pair", pair_id, world, str(seed), decoder, rep)] = (
                        pair_events[(pair_id, world, seed)], rel,
                    )
    return expected


def main() -> None:
    if OUT.exists():
        raise RuntimeError("refusing to overwrite recovery validation")
    freeze = json.loads(FREEZE.read_text())
    result = json.loads(RESULT.read_text())
    header, rows = tsv(MANIFEST)
    paths = [row["claim_relpath"] for row in rows]
    safe = all(
        not Path(rel).is_absolute() and ".." not in Path(rel).parts
        and (CLAIMS / rel).is_file()
        for rel in paths
    )
    hashes = all(sha(CLAIMS / row["claim_relpath"]) == row["claim_sha256"] for row in rows)
    mode_counts = {
        mode: sum(row["mode"] == mode for row in rows)
        for mode in ("authentic", "pair", "world_claim")
    }
    claim_map = {
        path.relative_to(CLAIMS).as_posix(): sha(path)
        for path in sorted(CLAIMS.rglob("*"))
        if path.is_file() and path != MANIFEST
    }
    prestate = dict(claim_map)
    recovered_hash = prestate.pop(MISSING, "")
    expected_rows = expected_manifest_rows()
    actual_rows = {}
    matrix_well_formed = True
    for row in rows:
        key = (
            row.get("mode", ""), row.get("pair_id", ""), row.get("world_id", ""),
            row.get("held_seed", ""), row.get("decoder_id", ""),
            row.get("representation", ""),
        )
        try:
            payload = (int(row.get("events", "-1")), row.get("claim_relpath", ""))
        except ValueError:
            matrix_well_formed = False
            payload = (-1, "")
        if key in actual_rows:
            matrix_well_formed = False
        actual_rows[key] = payload
    freeze_checks = freeze.get("checks", {})
    freeze_bindings = freeze.get("bindings", {})
    recovered_claim = json.loads((CLAIMS / MISSING).read_text())
    try:
        recovered_confidence_valid = 0.0 <= float(recovered_claim.get("confidence", -1)) <= 1.0
    except (TypeError, ValueError):
        recovered_confidence_valid = False
    result_keys = {
        "schema", "status", "recovery_freeze_sha256",
        "preexisting_claims_unchanged", "claim_files", "claim_map_sha256",
        "recovered_world_claim", "recovered_world_claim_sha256",
        "claim_manifest_sha256", "oracle_opened", "voynich_rows",
        "f84_opened", "content_sha256",
    }
    checks = {
        "freeze_content": valid_content(freeze),
        "freeze_schema_status": (
            freeze.get("schema") == "GDT395_V3_INTERRUPTION_RECOVERY_FREEZE_V1"
            and freeze.get("status") == "FROZEN_BEFORE_RECOVERY_EXECUTION"
            and freeze.get("sole_missing_claim") == MISSING
            and freeze.get("event_claim_files") == 2100
            and freeze.get("world_claim_files") == 49
            and freeze.get("total_claim_files") == 2149
        ),
        "freeze_checks": (
            freeze_checks == {
                "all_event_claims_present": True,
                "one_world_claim_missing": True,
                "authoritative_manifest_absent": True,
                "recovery_source_bound": True,
                "oracle_opened": False,
                "voynich_rows": 0,
                "f84_opened": False,
            }
        ),
        "freeze_source_bindings": (
            isinstance(freeze_bindings, dict)
            and set(freeze_bindings) == RECOVERY_BINDINGS
            and all((EXP / rel).is_file() and sha(EXP / rel) == digest
                    for rel, digest in freeze_bindings.items())
        ),
        "result_content": valid_content(result),
        "result_schema_status": (
            set(result) == result_keys
            and result.get("schema") == "GDT395_V3_INTERRUPTION_RECOVERY_RESULT_V1"
            and result.get("status") == "RECOVERED_EXACT_MISSING_WORLD_CLAIM_AND_MANIFEST"
            and result.get("claim_files") == 2150
            and result.get("recovered_world_claim") == MISSING
        ),
        "freeze_binding": result.get("recovery_freeze_sha256") == sha(FREEZE),
        "preexisting_claims_unchanged": (
            result.get("preexisting_claims_unchanged") is True
            and len(prestate) == 2149
            and canonical_hash(prestate) == freeze.get("prestate_claim_map_sha256")
        ),
        "manifest_header": header == FIELDS,
        "manifest_shape": len(rows) == len(set(paths)) == 2150,
        "manifest_modes": mode_counts == {"authentic": 1500, "pair": 600, "world_claim": 50},
        "manifest_exact_matrix": (
            matrix_well_formed and len(actual_rows) == 2150
            and actual_rows == expected_rows
        ),
        "manifest_paths_safe": safe,
        "manifest_hashes": hashes,
        "claim_map": len(claim_map) == 2150 and canonical_hash(claim_map) == result.get("claim_map_sha256"),
        "manifest_bound": sha(MANIFEST) == result.get("claim_manifest_sha256"),
        "recovered_claim_bound": (
            bool(recovered_hash)
            and recovered_hash == result.get("recovered_world_claim_sha256")
            and sha(CLAIMS / MISSING) == recovered_hash
        ),
        "recovered_claim_schema": (
            set(recovered_claim) == WORLD_CLAIM_FIELDS
            and recovered_claim.get("decoder_id") == "D01_MULTIVIEW_GRAPH"
            and recovered_confidence_valid
        ),
        "oracle_seal": result.get("oracle_opened") is False,
        "voynich_zero": result.get("voynich_rows") == 0,
        "f84_seal": result.get("f84_opened") is False,
    }
    data = {
        "schema": "GDT395_V3_INTERRUPTION_RECOVERY_VALIDATION_V1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "checks_passed": sum(checks.values()),
        "checks_total": len(checks),
        "bindings": {
            "freeze_sha256": sha(FREEZE),
            "result_sha256": sha(RESULT),
            "manifest_sha256": sha(MANIFEST),
            "validator_sha256": sha(Path(__file__)),
        },
    }
    data["content_sha256"] = canonical_hash(data)
    OUT.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": data["status"], "checks": f"{data['checks_passed']}/{data['checks_total']}"}, sort_keys=True))
    if data["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
