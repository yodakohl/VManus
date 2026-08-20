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
MANIFEST = CLAIMS / "blind_claim_manifest_all.tsv"
FREEZE = EXP / "artifacts/gdt395_blind_claims_freeze.json"
OUT = EXP / "artifacts/gdt395_blind_claims_validation.json"
CORPUS = EXP / "artifacts/gdt395_corpus_manifest.tsv"
PAIR = EXP / "artifacts/gdt395_pair_blind_manifest.tsv"
REPS = {
    "FULL_GROUP", "HOST_LIKE", "COMPOSITE_STATE", "INFERRED_COMPONENTS",
    "CONSTRUCTION_SPAN", "RECORD_TOPOLOGY",
}
CLAIM_FIELDS = {
    "world_id", "corpus_seed", "event_id", "representation", "decoder_id",
    "entity_cluster", "lexical_cluster", "stem_cluster", "function_cluster",
    "operator_cluster", "construction_cluster", "register_variant_cluster",
    "semantic_category_cluster", "predicted_relation_target_event_id",
    "predicted_reference_target_event_id", "predicted_scope_start_event_id",
    "predicted_scope_end_event_id", "productive_component_prediction",
    "fossilized_component_prediction", "record_schema_cluster", "confidence",
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


def claim_shape(path: Path) -> tuple[int, set[str]]:
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        fields = set(reader.fieldnames or ())
        count = sum(1 for _ in reader)
    return count, fields


def main() -> None:
    freeze = json.loads(FREEZE.read_text())
    rows = tsv(MANIFEST)
    corpus_events = {(r["world_id"], int(r["corpus_seed"])): int(r["events"]) for r in tsv(CORPUS)}
    pair_events = {(r["pair_id"], r["world_id"], int(r["corpus_seed"])): int(r["events"]) for r in tsv(PAIR)}
    checks = {}
    checks["status"] = freeze["status"] == "BLIND_CLAIMS_FROZEN_BEFORE_ORACLE_ACCESS"
    checks["bindings"] = all(sha(EXP / rel) == digest for rel, digest in freeze["bindings"].items())
    checks["manifest_hash"] = sha(MANIFEST) == freeze["claim_manifest_sha256"]
    checks["counts"] = len(rows) == freeze["claim_file_count"] == 2150
    checks["mode_counts"] = (
        sum(r["mode"] == "world_claim" for r in rows) == freeze["world_claim_file_count"] == 50
        and sum(r["mode"] != "world_claim" for r in rows) == freeze["event_claim_file_count"] == 2100
    )
    exact_keys = set()
    hashes = shapes = path_safe = identity = confidence = True
    for row in rows:
        rel = Path(row["claim_relpath"])
        path_safe &= not rel.is_absolute() and ".." not in rel.parts
        path = CLAIMS / rel
        hashes &= path.is_file() and sha(path) == row["claim_sha256"]
        held_key = -1 if row["held_seed"] == "NONE" else int(row["held_seed"])
        key = (row["mode"], row["pair_id"], row["world_id"], held_key, row["decoder_id"], row["representation"])
        exact_keys.add(key)
        if row["mode"] == "world_claim":
            payload = json.loads(path.read_text())
            shapes &= set(payload) == {"decoder_id", "architecture_cluster", "language_like", "notation_like", "codebook_like", "semantics_light_like", "confidence"}
            identity &= payload.get("decoder_id") == row["decoder_id"]
            confidence &= 0.0 <= float(payload.get("confidence", -1)) <= 1.0
            continue
        n, fields = claim_shape(path)
        shapes &= fields == CLAIM_FIELDS
        if row["mode"] == "authentic":
            expected = corpus_events[(row["world_id"], int(row["held_seed"]))]
        else:
            expected = pair_events[(row["pair_id"], row["world_id"], int(row["held_seed"]))]
        shapes &= n == int(row["events"]) == expected
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
    checks["file_hashes"] = hashes
    checks["claim_shapes"] = shapes
    checks["safe_paths"] = path_safe
    checks["world_claim_identity"] = identity
    checks["confidence"] = confidence
    checks["no_oracle_interface"] = "oracle" not in MANIFEST.read_text().lower()
    checks["seal"] = not freeze["oracle_opened"] and freeze["oracle_rows_read"] == freeze["voynich_rows"] == 0 and not any(freeze["f84"].values())
    tmp = dict(freeze); expected_hash = tmp.pop("content_sha256")
    checks["content_hash"] = hashlib.sha256(json.dumps(tmp, sort_keys=True, separators=(",", ":")).encode()).hexdigest() == expected_hash
    result = {
        "schema": "GDT395_BLIND_CLAIMS_VALIDATION_V1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "checks_passed": sum(checks.values()), "checks_total": len(checks),
        "freeze_sha256": sha(FREEZE),
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": result["status"], "checks": f"{result['checks_passed']}/{result['checks_total']}"}, sort_keys=True))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
