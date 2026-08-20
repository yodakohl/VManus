#!/usr/bin/env python3
"""Independently validate GDT396 legacy/development paired corpora."""

from __future__ import annotations

import csv
import gzip
import hashlib
import hmac
import itertools
import json
import struct
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt396_repaired_synthetic_identifiability_voynich_surface"
G395 = ROOT / "experiments/yolo/gdt395_adversarial_synthetic_identifiability_benchmark"
CORPORA = EXP / ".work/corpora"
FREEZE = EXP / "artifacts/gdt396_protocol_freeze.json"
OUT = EXP / "artifacts/gdt396_development_corpus_validation.json"
OBS_FIELDS = (
    "world_id", "corpus_seed", "event_id", "page_id", "paragraph_id",
    "record_id", "line_id", "event_index", "group_index", "visible_group",
    "separator_before", "separator_after", "register_id", "hand_id",
    "layout_role", "line_position_bin", "record_position_bin", "ambiguous_boundary",
)
META_FIELDS = tuple(field for field in OBS_FIELDS if field != "visible_group") + ("surface_channel", "surface_payload_index")
ORACLE_FIELDS = (
    "world_id", "corpus_seed", "event_id", "domain_id", "activity_id",
    "lexical_id", "semantic_entity_id", "semantic_category", "function_class",
    "relation_type", "relation_target_event_id", "state_before", "state_after",
    "historical_stem_id", "current_morpheme_ids", "fossilized_component_ids",
    "construction_id", "scope_start_event_id", "scope_end_event_id",
    "record_schema_id", "register_realization_id", "productive_morphology",
    "current_component_semantics", "genealogy_stage",
)
MAGIC = b"GDT396VS1\0"
ATOM_COUNT = 24


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def rows(path: Path) -> list[dict]:
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def atom_rows(path: Path) -> list[bytes]:
    with gzip.open(path, "rb") as fh:
        if fh.read(len(MAGIC)) != MAGIC:
            raise ValueError("bad atom magic")
        raw = fh.read(4)
        if len(raw) != 4:
            raise ValueError("truncated atom count")
        count = struct.unpack(">I", raw)[0]
        result = []
        for _ in range(count):
            raw = fh.read(2)
            if len(raw) != 2:
                raise ValueError("truncated atom length")
            size = struct.unpack(">H", raw)[0]
            value = fh.read(size)
            if len(value) != size or not value or any(atom >= ATOM_COUNT for atom in value):
                raise ValueError("bad atom payload")
            result.append(value)
        if fh.read(1):
            raise ValueError("trailing atom bytes")
    return result


def rank(salt: bytes, world: str, label: bytes) -> bytes:
    return hmac.new(salt, b"GDT396-VS1\0" + world.encode() + b"\0" + label, hashlib.sha256).digest()


def mapping(salt: bytes, world: str, alphabet: list[str]) -> dict[str, bytes]:
    pool = list(itertools.product(range(24), repeat=2))
    pool.sort(key=lambda code: (rank(salt, world, bytes(code)), code))
    native = sorted(alphabet, key=lambda value: (rank(salt, world, value.encode()), value))
    return {value: bytes(pool[index]) for index, value in enumerate(native)}


def canonical_trace(obs: list[dict], oracle: list[dict]) -> str:
    trace = [{field: row[field] for field in OBS_FIELDS if field != "visible_group"} for row in obs]
    value = json.dumps({"trace": trace, "oracle": oracle}, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n"
    return hashlib.sha256(value.encode()).hexdigest()


def main() -> int:
    frozen = json.loads(FREEZE.read_text())
    salt = bytes.fromhex((EXP / ".work/sealed/surface_salt.hex").read_text().strip())
    commitment = hashlib.sha256(b"GDT396-SURFACE-SALT-V1\0" + salt).hexdigest()
    checks: dict[str, bool] = {}
    checks["protocol_valid"] = json.loads((EXP / "artifacts/gdt396_protocol_validation.json").read_text())["status"] == "PASS"
    checks["salt_commitment"] = commitment == frozen["mapping_salt_commitment"]
    old = {(r["world_id"], r["corpus_seed"]): r for r in rows(G395 / "artifacts/gdt395_corpus_manifest.tsv")}
    manifests = {}
    all_manifest_rows = []
    for block, expected_count in (("legacy", 200), ("development", 50)):
        path = CORPORA / f"gdt396_{block}_paired_manifest_v2.tsv"
        data = rows(path); manifests[block] = (path, data)
        checks[f"{block}_manifest_rows"] = len(data) == expected_count
        all_manifest_rows.extend(data)
    checks["qualification_absent"] = not (CORPORA / "qualification").exists()
    checks["confirmation_absent"] = not (CORPORA / "confirmation").exists()

    legacy_hash_match = oracle_hash_match = event_match = True
    non_surface_equal = atom_exact = trace_exact = endpoints_valid = true_alphabet = source_manifest_bound = True
    events_total = 0
    worlds = set(); seeds_by_block = {"legacy": set(), "development": set()}
    for manifest in all_manifest_rows:
        world = manifest["world_id"]; seed = manifest["corpus_seed"]; block = manifest["seed_block"]
        source_manifest = CORPORA / f"gdt396_{block}_paired_manifest.tsv"
        source_manifest_bound &= manifest["source_manifest_sha256"] == sha256(source_manifest)
        source_manifest_bound &= manifest["trace_hash_definition"] == "STORED_TSV_TEXT_SCALARS_VISIBLE_GROUP_OMITTED_PLUS_ORACLE_V1"
        worlds.add(world); seeds_by_block[block].add(int(seed))
        free_path = CORPORA / manifest["free_observation_relpath"]
        meta_path = CORPORA / manifest["voynich_metadata_relpath"]
        surface_path = CORPORA / manifest["voynich_surface_relpath"]
        oracle_path = CORPORA / manifest["oracle_relpath"]
        for path, key in ((free_path, "free_observation_sha256"), (meta_path, "voynich_metadata_sha256"), (surface_path, "voynich_surface_sha256"), (oracle_path, "oracle_sha256")):
            if sha256(path) != manifest[key]:
                raise RuntimeError(f"manifest hash mismatch {path}")
        free = rows(free_path); meta = rows(meta_path); atoms = atom_rows(surface_path); oracle = rows(oracle_path)
        events_total += len(free)
        event_match &= len(free) == len(meta) == len(atoms) == len(oracle) == int(manifest["events"])
        if free and (tuple(free[0]) != OBS_FIELDS or tuple(meta[0]) != META_FIELDS or tuple(oracle[0]) != ORACLE_FIELDS):
            raise RuntimeError("field-order/schema mismatch")
        m = json.loads((CORPORA / "sealed" / world / "world_meta.json").read_text())
        mp = mapping(salt, world, m["alphabet"])
        ids = {row["event_id"] for row in free}
        for index, (fr, mr, payload, truth) in enumerate(zip(free, meta, atoms, oracle, strict=True)):
            non_surface_equal &= all(fr[field] == mr[field] for field in OBS_FIELDS if field != "visible_group")
            non_surface_equal &= mr["surface_channel"] == "VOYNICH_SURFACE" and int(mr["surface_payload_index"]) == index
            expected = b"".join(mp[char] for char in fr["visible_group"])
            atom_exact &= payload == expected and len(payload) == 2 * len(fr["visible_group"])
            true_alphabet &= all(atom < 24 for atom in payload)
            endpoints_valid &= truth["event_id"] == fr["event_id"]
            for field in ("relation_target_event_id", "scope_start_event_id", "scope_end_event_id"):
                values = [] if truth[field] == "NONE" else truth[field].split("|")
                endpoints_valid &= all(value in ids for value in values)
        trace_exact &= canonical_trace(free, oracle) == manifest["hidden_trace_sha256"]
        if block == "legacy":
            prior = old[(world, seed)]
            legacy_hash_match &= prior["observation_sha256"] == manifest["free_observation_sha256"]
            oracle_hash_match &= prior["oracle_sha256"] == manifest["oracle_sha256"]
            event_match &= prior["events"] == manifest["events"]

    checks.update({
        "ten_worlds": worlds == {f"W{i:02d}" for i in range(1, 11)},
        "legacy_seed_set": seeds_by_block["legacy"] == set(range(20)),
        "development_seed_set": seeds_by_block["development"] == set(range(3960000, 3960005)),
        "legacy_free_exact_gdt395": legacy_hash_match,
        "legacy_oracle_exact_gdt395": oracle_hash_match,
        "event_counts_exact": event_match,
        "paired_non_surface_equal": non_surface_equal,
        "atom_stream_exact": atom_exact,
        "atom_inventory_0_23_only": true_alphabet,
        "hidden_trace_exact": trace_exact,
        "source_manifest_bound": source_manifest_bound,
        "relation_scope_endpoints_valid": endpoints_valid,
    })
    result = {
        "schema": "GDT396_DEVELOPMENT_CORPUS_VALIDATION_V1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "checks_passed": sum(checks.values()),
        "checks_total": len(checks),
        "paired_corpora": len(all_manifest_rows),
        "paired_events": events_total,
        "legacy_manifest_sha256": sha256(manifests["legacy"][0]),
        "development_manifest_sha256": sha256(manifests["development"][0]),
        "protocol_freeze_sha256": sha256(FREEZE),
        "validator_sha256": sha256(Path(__file__)),
        "voynich_corpus_files_opened": 0,
        "voynich_rows": 0,
        "f84": {"allowed": False, "opened": False, "rows": 0},
        "f84r": {"allowed": False, "opened": False, "rows": 0},
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
