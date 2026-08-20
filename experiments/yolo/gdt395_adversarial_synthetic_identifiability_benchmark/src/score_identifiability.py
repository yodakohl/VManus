#!/usr/bin/env python3
"""Post-freeze, standard-library-only oracle scorer for GDT395.

This module is intentionally executable only as a script. It never imports a
world, generator, decoder, claim, or oracle module from the experiment.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import json
import math
import re
import sqlite3
import statistics
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
EXP = ROOT / "experiments/yolo/gdt395_adversarial_synthetic_identifiability_benchmark"
CORPUS_ROOT = EXP / ".work/corpora"

WORLDS = tuple(f"W{i:02d}" for i in range(1, 11))
HELD_SEEDS = tuple(range(15, 20))
REPRESENTATIONS = (
    "FULL_GROUP", "HOST_LIKE", "COMPOSITE_STATE", "INFERRED_COMPONENTS",
    "CONSTRUCTION_SPAN", "RECORD_TOPOLOGY",
)
PROPERTIES = (
    "LEXICAL_IDENTITY", "SEMANTIC_ENTITY_IDENTITY",
    "HISTORICAL_STEM_ANCESTRY", "PRODUCTIVE_MORPHOLOGY",
    "FOSSILIZED_MORPHOLOGY", "FUNCTION_CLASS", "COORDINATOR_RELATION",
    "ALTERNATIVE_RELATION", "REFERENCE_ANAPHORA", "TEMPORAL_STATE_GATE",
    "SCOPE", "ENTITY_REUSE", "OPERATOR_CLASS", "RECORD_SCHEMA",
    "REGISTER_LOCAL_VARIANT", "SEMANTIC_CATEGORY", "ACTUAL_LEXICAL_MEANING",
)
HOLD_PROPERTIES = {
    "COORDINATOR_RELATION", "ALTERNATIVE_RELATION", "REFERENCE_ANAPHORA",
    "TEMPORAL_STATE_GATE", "OPERATOR_CLASS", "ACTUAL_LEXICAL_MEANING",
    "PRODUCTIVE_MORPHOLOGY", "FOSSILIZED_MORPHOLOGY", "RECORD_SCHEMA", "SCOPE",
}
ENDPOINT_QUALIFICATION = {
    "LEXICAL_IDENTITY": "ANONYMOUS_LEXICAL_ID_EQUALITY_ONLY",
    "SEMANTIC_ENTITY_IDENTITY": "ANONYMOUS_SEMANTIC_ENTITY_COIDENTITY_ONLY",
    "HISTORICAL_STEM_ANCESTRY": "SHARED_HISTORICAL_STEM_ID_PARTITION_ONLY_NOT_GENEALOGY",
    "PRODUCTIVE_MORPHOLOGY": "INTERFACE_HOLD_OPAQUE_COMPONENT_ID_NOT_BOOLEAN",
    "FOSSILIZED_MORPHOLOGY": "INTERFACE_HOLD_OPAQUE_COMPONENT_ID_NOT_BOOLEAN",
    "FUNCTION_CLASS": "ANONYMOUS_FUNCTION_CLASS_PARTITION_ONLY",
    "COORDINATOR_RELATION": "INTERFACE_HOLD_NO_FROZEN_TYPED_RANKED_TARGET",
    "ALTERNATIVE_RELATION": "INTERFACE_HOLD_NO_FROZEN_TYPED_RANKED_TARGET",
    "REFERENCE_ANAPHORA": "INTERFACE_HOLD_NO_DIRECT_ORACLE_REFERENCE_TARGET",
    "TEMPORAL_STATE_GATE": "INTERFACE_HOLD_NO_MATCHING_CLAIM_TRUTH",
    "SCOPE": "INTERFACE_HOLD_NO_VALIDATED_EVENT_ORDER",
    "ENTITY_REUSE": "RECURRING_ANONYMOUS_ENTITY_ID_PAIR_PARTITION_ONLY",
    "OPERATOR_CLASS": "INTERFACE_HOLD_NO_ORACLE_OPERATOR_CLASS",
    "RECORD_SCHEMA": "INTERFACE_HOLD_NO_RECORD_ID_IN_ACCEPTED_INPUTS",
    "REGISTER_LOCAL_VARIANT": "AUTHENTIC_REGISTER_REALIZATION_IDENTITY_ONLY",
    "SEMANTIC_CATEGORY": "ANONYMOUS_SEMANTIC_CATEGORY_PARTITION_ONLY_NOT_MEANING",
    "ACTUAL_LEXICAL_MEANING": "INTERFACE_HOLD_NO_GLOSS_OR_MEANING_CHANNEL",
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
WORLD_CLAIM_FIELDS = (
    "decoder_id", "architecture_cluster", "language_like", "notation_like",
    "codebook_like", "semantics_light_like", "confidence",
)
ORACLE_FIELDS = (
    "world_id", "corpus_seed", "event_id", "domain_id", "activity_id",
    "lexical_id", "semantic_entity_id", "semantic_category", "function_class",
    "relation_type", "relation_target_event_id", "state_before", "state_after",
    "historical_stem_id", "current_morpheme_ids", "fossilized_component_ids",
    "construction_id", "scope_start_event_id", "scope_end_event_id",
    "record_schema_id", "register_realization_id", "productive_morphology",
    "current_component_semantics", "genealogy_stage",
)
THRESHOLDS = {
    "cluster": {"nmi": 0.35, "ari": 0.20, "pair_f1": 0.35},
}
WORLD_FAMILIES = {
    "W01": "TECHNICAL_SCRIBAL_SHORTHAND",
    "W02": "ORGANIC_CODEBOOK",
    "W03": "ENGINEERED_CATALOGUE_CODE",
    "W04": "PROCEDURAL_RECIPE_NOTATION",
    "W05": "MNEMONIC_RITUAL_LEGACY",
    "W06": "ORGANIC_CATALOGUE_INDEX",
    "W07": "HYBRID_WORD_CODE_QUANTITY",
    "W08": "DIVERGED_MULTI_SCHOOL_NOTATION",
    "W09": "MEANINGFUL_RELATIONAL_SYSTEM",
    "W10": "SEMANTICS_LIGHT_GENERATOR",
}
ARCH_FLAG_TRUTH = {
    "language_like": {"W01", "W07"},
    "notation_like": {"W04", "W05", "W08", "W09"},
    "codebook_like": {"W02", "W03", "W06"},
    "semantics_light_like": {"W10"},
}
PAIR_WORLDS = {"W02", "W03", "W09", "W10"}
PAIR_ALLOWED: dict[str, set[str]] = {}
STRESS_TESTS = (
    "EXACT_COMPOSITE_AS_WORD", "UNIVERSAL_COEFFICIENTS",
    "RESIDUALIZE_FREQUENCY_POSITION_RECURRENCE", "SCALAR_ROLE_BOTTLENECK",
    "FIXED_SHORT_HORIZON", "MULTI_CONSTRAINT_INTERSECTION",
)
MISSING = {"", "NONE", "NULL", "UNRESOLVED", "NA", "N/A", "[]", "{}"}
FREEZE_SCHEMA = "GDT395_BLIND_CLAIMS_FREEZE_V2"
VALIDATION_SCHEMA = "GDT395_BLIND_CLAIMS_VALIDATION_V2"
ROLE_NAMES = ("authentic_event_claims", "pair_event_claims", "world_claims")
class Refusal(RuntimeError):
    """A hard precondition failure that must produce no scientific output."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            for block in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(block)
    except OSError as exc:
        raise Refusal("cannot hash required input") from None
    return digest.hexdigest()


def load_json(path: Path) -> dict:
    try:
        with path.open("r", encoding="utf-8") as handle:
            value = json.load(handle)
    except (OSError, json.JSONDecodeError):
        raise Refusal(f"cannot read required JSON {portable_path(path)}") from None
    if not isinstance(value, dict):
        raise Refusal(f"required JSON is not an object: {portable_path(path)}")
    return value


def portable_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(ROOT.resolve()))
    except ValueError:
        return path.name


def validate_content_hash(document: dict, label: str) -> None:
    declared = document.get("content_sha256")
    if not isinstance(declared, str) or not re.fullmatch(r"[0-9a-f]{64}", declared):
        raise Refusal(f"{label} lacks a valid content_sha256")
    payload = dict(document)
    del payload["content_sha256"]
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"),
                         ensure_ascii=True).encode("ascii")
    if hashlib.sha256(encoded).hexdigest() != declared:
        raise Refusal(f"{label} content_sha256 mismatch")


def validate_checks(document: dict, label: str) -> None:
    checks = document.get("checks")
    if not isinstance(checks, dict) or not checks:
        raise Refusal(f"{label} requires a nonempty checks object")
    if any(type(value) is not bool for value in checks.values()):
        raise Refusal(f"{label} checks must be Boolean")
    if not all(checks.values()):
        raise Refusal(f"{label} contains a failed check")


def binding_entries(document: dict, role: str) -> list[dict[str, str]]:
    bindings = document.get("bindings")
    if not isinstance(bindings, dict) or role not in bindings:
        raise Refusal(f"freeze lacks required binding role {role}")
    entries = bindings[role]
    if not isinstance(entries, list) or not entries:
        raise Refusal(f"binding role {role} must be a nonempty list")
    output = []
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != {"path", "sha256"}:
            raise Refusal(f"binding role {role} has a malformed entry")
        path, digest = entry["path"], entry["sha256"]
        if not isinstance(path, str) or not path or not isinstance(digest, str):
            raise Refusal(f"binding role {role} has invalid types")
        if not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise Refusal(f"binding role {role} has invalid SHA-256")
        output.append({"path": path, "sha256": digest})
    return output


def exact_role_bindings(freeze: dict, role_paths: dict[str, list[Path]]) -> dict[str, str]:
    bound_by_role: dict[str, dict[Path, str]] = {}
    for role in ROLE_NAMES:
        bound: dict[Path, str] = {}
        for entry in binding_entries(freeze, role):
            resolved = Path(entry["path"]).resolve()
            if resolved in bound:
                raise Refusal(f"duplicate path in binding role {role}")
            bound[resolved] = entry["sha256"]
        bound_by_role[role] = bound
    for first, second in itertools.combinations(ROLE_NAMES, 2):
        if set(bound_by_role[first]) & set(bound_by_role[second]):
            raise Refusal(f"cross-role binding substitution between {first} and {second}")
    hashes: dict[str, str] = {}
    for role in ROLE_NAMES:
        supplied = {path.resolve() for path in role_paths[role]}
        if supplied != set(bound_by_role[role]):
            raise Refusal(f"supplied files do not exactly equal binding role {role}")
        for index, path in enumerate(role_paths[role]):
            digest = sha256_file(path)
            if digest != bound_by_role[role][path.resolve()]:
                raise Refusal(f"SHA-256 mismatch in binding role {role}")
            hashes[f"{role}_{index:03d}:{portable_path(path)}"] = digest
    return hashes


def validate_implementation_map(freeze: dict) -> dict[str, str]:
    mapping = freeze.get("implementation_map")
    if not isinstance(mapping, dict) or len(mapping) != 5:
        raise Refusal("freeze implementation_map must bind exactly five decoders")
    tiers: dict[str, str] = {}
    for decoder_id, entry in mapping.items():
        if not isinstance(decoder_id, str) or not decoder_id or not isinstance(entry, dict):
            raise Refusal("malformed decoder implementation_map entry")
        if entry.get("decoder_id") != decoder_id or entry.get("oracle_blind") is not True:
            raise Refusal("implementation_map decoder provenance failure")
        tier = entry.get("model_family")
        if tier not in {"SOL", "LUNA"}:
            raise Refusal("implementation_map model_family must be SOL or LUNA")
        tiers[decoder_id] = tier
    if list(tiers.values()).count("SOL") != 2 or list(tiers.values()).count("LUNA") != 3:
        raise Refusal("implementation_map must bind exactly two SOL and three LUNA decoders")
    return tiers


def validate_blind_gate(freeze_path: Path, validation_path: Path,
                        role_paths: dict[str, list[Path]]) -> tuple[dict[str, str], dict[str, str], dict]:
    freeze = load_json(freeze_path)
    validation = load_json(validation_path)
    if freeze.get("schema") != FREEZE_SCHEMA or validation.get("schema") != VALIDATION_SCHEMA:
        raise Refusal("freeze or validation schema mismatch")
    validate_content_hash(freeze, "claims freeze")
    validate_content_hash(validation, "claims validation")
    validate_checks(freeze, "claims freeze")
    validate_checks(validation, "claims validation")
    expected = {"status": "PASS", "phase": "FROZEN_BEFORE_ORACLE_ACCESS",
                "oracle_blind": True, "oracle_opened": False,
                "oracle_rows_read": 0, "voynich_rows": 0}
    for key, wanted in expected.items():
        if freeze.get(key) != wanted:
            raise Refusal(f"claims freeze requires {key}={wanted!r}")
    f84 = freeze.get("f84")
    if not isinstance(f84, dict) or not f84 or any(value is not False for value in f84.values()):
        raise Refusal("claims freeze does not preserve the f84 seal")
    if validation.get("status") != "PASS":
        raise Refusal("blind-claims validation status is not PASS")
    freeze_digest = sha256_file(freeze_path)
    validation_binding = binding_entries(validation, "claims_freeze")
    if len(validation_binding) != 1:
        raise Refusal("validation must bind exactly one claims freeze")
    bound = validation_binding[0]
    if Path(bound["path"]).resolve() != freeze_path.resolve() or bound["sha256"] != freeze_digest:
        raise Refusal("validation claims-freeze binding mismatch")
    hashes = {"claims_freeze": freeze_digest,
              "claims_validation": sha256_file(validation_path)}
    hashes.update(exact_role_bindings(freeze, role_paths))
    return hashes, validate_implementation_map(freeze), freeze


def validate_oracle_manifest(freeze: dict, manifest_path: Path,
                             oracle_paths: list[Path]) -> dict[Path, str]:
    implementation = freeze.get("bindings", {}).get("implementation", {}).get("hashes", {})
    manifest_rel = "artifacts/gdt395_corpus_manifest.tsv"
    if not isinstance(implementation, dict) or implementation.get(manifest_rel) != sha256_file(manifest_path):
        raise Refusal("corpus manifest is not implementation-bound by the claims freeze")
    handle, reader = open_tsv(manifest_path)
    try:
        require_header(reader, (
            "world_id", "corpus_seed", "events", "record_rewriter",
            "observation_relpath", "observation_sha256", "oracle_relpath",
            "oracle_sha256",
        ), manifest_path)
        expected: dict[Path, str] = {}
        for row in reader:
            world = clean(row["world_id"])
            seed = safe_int(row["corpus_seed"], "manifest corpus_seed")
            if world not in WORLDS or seed not in range(20):
                raise Refusal("corpus manifest has an out-of-panel identity")
            if seed not in HELD_SEEDS:
                continue
            rel = Path(clean(row["oracle_relpath"]))
            canonical = Path("sealed") / world / f"seed_{seed:02d}_oracle.tsv.gz"
            digest = clean(row["oracle_sha256"])
            if rel != canonical or rel.is_absolute() or ".." in rel.parts:
                raise Refusal("corpus manifest has an unsafe oracle path")
            if not re.fullmatch(r"[0-9a-f]{64}", digest):
                raise Refusal("corpus manifest has an invalid oracle SHA-256")
            expected[(CORPUS_ROOT / rel).resolve()] = digest
    finally:
        handle.close()
    supplied = {path.resolve() for path in oracle_paths}
    if len(expected) != 50 or supplied != set(expected):
        raise Refusal("oracle inputs do not exactly equal the 50 frozen held corpora")
    return expected


def clean(value: object) -> str:
    return "" if value is None else str(value).strip()


def present(value: object) -> bool:
    return clean(value).upper() not in MISSING


def parse_bool(value: object) -> bool | None:
    token = clean(value).upper()
    if token == "TRUE":
        return True
    if token == "FALSE":
        return False
    if token == "UNRESOLVED":
        return None
    raise Refusal("non-Boolean value in a Boolean field")


def parse_oracle_pipe(value: object, label: str) -> tuple[str, ...]:
    raw = clean(value)
    if raw in {"", "NULL", "UNRESOLVED"}:
        raise Refusal(f"invalid missing oracle value in {label}")
    atoms = raw.split("|")
    if any(not atom or atom != atom.strip() for atom in atoms):
        raise Refusal(f"noncanonical pipe value in {label}")
    if len(atoms) != len(set(atoms)) or atoms != sorted(atoms):
        raise Refusal(f"unsorted or duplicate pipe atoms in {label}")
    if "NONE" in atoms:
        if atoms != ["NONE"]:
            raise Refusal(f"NONE mixed with a value in {label}")
        return ()
    return tuple(atoms)


def parse_oracle_scalar(value: object, label: str) -> str | None:
    atoms = parse_oracle_pipe(value, label)
    if not atoms:
        return None
    if len(atoms) != 1:
        raise Refusal(f"multi-label truth cannot define a partition in {label}")
    return atoms[0]


def safe_int(value: object, label: str) -> int:
    try:
        return int(clean(value))
    except ValueError as exc:
        raise Refusal(f"invalid integer {label}") from exc


def open_tsv(path: Path) -> tuple[object, csv.DictReader]:
    try:
        handle = path.open("r", encoding="utf-8", newline="")
    except OSError as exc:
        raise Refusal(f"cannot open TSV {portable_path(path)}") from None
    reader = csv.DictReader(handle, delimiter="\t")
    if reader.fieldnames is None:
        handle.close()
        raise Refusal(f"TSV has no header: {portable_path(path)}")
    return handle, reader


def require_header(reader: csv.DictReader, fields: tuple[str, ...], path: Path) -> None:
    if tuple(reader.fieldnames or ()) != fields:
        raise Refusal(f"wrong TSV header for {portable_path(path)}")


def quoted(names: tuple[str, ...] | list[str]) -> str:
    return ",".join(f'"{name}"' for name in names)


def create_database(path: str) -> sqlite3.Connection:
    db = sqlite3.connect(path)
    db.execute("PRAGMA journal_mode=OFF")
    db.execute("PRAGMA synchronous=OFF")
    db.execute("PRAGMA temp_store=FILE")
    claim_cols = ",".join(f'"{name}" TEXT NOT NULL' for name in CLAIM_FIELDS)
    oracle_cols = ",".join(f'"{name}" TEXT NOT NULL' for name in ORACLE_FIELDS)
    db.execute(
        f"CREATE TABLE claims (view TEXT NOT NULL,{claim_cols},"
        "PRIMARY KEY(view,world_id,corpus_seed,event_id,representation,decoder_id))"
    )
    db.execute(
        f"CREATE TABLE oracle ({oracle_cols},oracle_order INTEGER NOT NULL,"
        "PRIMARY KEY(world_id,corpus_seed,event_id))"
    )
    return db


def ingest_claims(db: sqlite3.Connection, paths: list[Path], view: str) -> None:
    placeholders = ",".join("?" for _ in range(len(CLAIM_FIELDS) + 1))
    sql = f"INSERT INTO claims(view,{quoted(CLAIM_FIELDS)}) VALUES ({placeholders})"
    for path in paths:
        handle, reader = open_tsv(path)
        try:
            require_header(reader, CLAIM_FIELDS, path)
            batch = []
            for row_number, row in enumerate(reader, 2):
                world = clean(row["world_id"])
                seed = safe_int(row["corpus_seed"], "corpus_seed")
                rep = clean(row["representation"])
                if world not in WORLDS or seed not in HELD_SEEDS or rep not in REPRESENTATIONS:
                    raise Refusal(f"out-of-panel claim at {portable_path(path)}:{row_number}")
                if view == "pair" and world not in PAIR_WORLDS:
                    raise Refusal(f"non-pair world in pair claims at {portable_path(path)}:{row_number}")
                if not clean(row["event_id"]) or not clean(row["decoder_id"]):
                    raise Refusal(f"missing claim identity at {portable_path(path)}:{row_number}")
                try:
                    confidence = float(row["confidence"])
                except ValueError as exc:
                    raise Refusal(f"bad confidence at {portable_path(path)}:{row_number}") from None
                if not math.isfinite(confidence) or not 0.0 <= confidence <= 1.0:
                    raise Refusal(f"confidence outside [0,1] at {portable_path(path)}:{row_number}")
                cluster_fields = (
                    "entity_cluster", "lexical_cluster", "stem_cluster", "function_cluster",
                    "operator_cluster", "construction_cluster", "register_variant_cluster",
                    "semantic_category_cluster", "record_schema_cluster",
                    "productive_component_prediction", "fossilized_component_prediction",
                )
                for field in cluster_fields:
                    token = clean(row[field])
                    if not token or token.upper() in {"NONE", "NULL", "NA", "N/A"}:
                        raise Refusal(f"invalid opaque/abstention claim at {portable_path(path)}:{row_number}")
                endpoint_fields = (
                    "predicted_relation_target_event_id", "predicted_reference_target_event_id",
                    "predicted_scope_start_event_id", "predicted_scope_end_event_id",
                )
                for field in endpoint_fields:
                    token = clean(row[field])
                    if (not token or token.upper() in {"NONE", "NULL", "NA", "N/A"}
                            or (token != "UNRESOLVED" and "|" in token)):
                        raise Refusal(f"invalid endpoint claim at {portable_path(path)}:{row_number}")
                values = [clean(row[name]) for name in CLAIM_FIELDS]
                values[CLAIM_FIELDS.index("corpus_seed")] = str(seed)
                batch.append((view, *values))
                if len(batch) >= 10000:
                    try:
                        db.executemany(sql, batch)
                    except sqlite3.IntegrityError as exc:
                        raise Refusal(f"duplicate claim key in {view} claims") from exc
                    batch.clear()
            if batch:
                try:
                    db.executemany(sql, batch)
                except sqlite3.IntegrityError as exc:
                    raise Refusal(f"duplicate claim key in {view} claims") from exc
        finally:
            handle.close()
    db.commit()


def validate_preoracle_claims(db: sqlite3.Connection, decoders: tuple[str, ...]) -> None:
    expected_repeats = len(REPRESENTATIONS) * len(decoders)
    for view, worlds in (("main", WORLDS), ("pair", tuple(sorted(PAIR_WORLDS)))):
        for world in worlds:
            for seed in HELD_SEEDS:
                bad = db.execute(
                    "SELECT COUNT(*) FROM (SELECT event_id,COUNT(*) n FROM claims "
                    "WHERE view=? AND world_id=? AND corpus_seed=? GROUP BY event_id HAVING n != ?)",
                    (view, world, str(seed), expected_repeats),
                ).fetchone()[0]
                if bad:
                    raise Refusal(f"claim event identities vary across {view} panels")
    for field in (
        "predicted_relation_target_event_id", "predicted_reference_target_event_id",
        "predicted_scope_start_event_id", "predicted_scope_end_event_id",
    ):
        invalid = db.execute(
            f'SELECT COUNT(*) FROM claims c WHERE c."{field}" != \'UNRESOLVED\' '
            f'AND NOT EXISTS (SELECT 1 FROM claims e WHERE e.view=c.view '
            f'AND e.world_id=c.world_id AND e.corpus_seed=c.corpus_seed '
            f'AND e.event_id=c."{field}")'
        ).fetchone()[0]
        if invalid:
            raise Refusal("endpoint claim refers outside its permitted held view")


def path_world_id(path: Path) -> str | None:
    matches = set(re.findall(r"(?<![A-Za-z0-9])W(?:0[1-9]|10)(?![A-Za-z0-9])", str(path)))
    if len(matches) > 1:
        raise Refusal("world-claim path contains multiple world IDs")
    return next(iter(matches)) if matches else None


def ingest_world_claims(paths: list[Path]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for path in paths:
        document = load_json(path)
        envelope_world: str | None = None
        if set(document) == set(WORLD_CLAIM_FIELDS):
            payload = document
        elif set(document) == {"world_id", *WORLD_CLAIM_FIELDS}:
            envelope_world = clean(document["world_id"])
            payload = {name: document[name] for name in WORLD_CLAIM_FIELDS}
        elif set(document) in ({"world_id", "claim"}, {"world_id", "world_claim"}):
            envelope_world = clean(document["world_id"])
            payload = document.get("claim", document.get("world_claim"))
            if not isinstance(payload, dict) or set(payload) != set(WORLD_CLAIM_FIELDS):
                raise Refusal("malformed world-claim JSON envelope")
        else:
            raise Refusal("world-claim JSON has an unexpected schema")
        from_path = path_world_id(path)
        if envelope_world and from_path and envelope_world != from_path:
            raise Refusal("world-claim path/envelope world mismatch")
        world = envelope_world or from_path
        if world not in WORLDS:
            raise Refusal("world claim lacks one strict W01--W10 path/envelope ID")
        item = {name: clean(payload[name]) for name in WORLD_CLAIM_FIELDS}
        item["world_id"] = world
        key = (world, item["decoder_id"])
        if key in seen:
            raise Refusal("duplicate world claim key")
        seen.add(key)
        try:
            confidence = float(item["confidence"])
        except ValueError as exc:
            raise Refusal("bad world-claim confidence") from exc
        if not math.isfinite(confidence) or not 0.0 <= confidence <= 1.0:
            raise Refusal("world-claim confidence outside [0,1]")
        for flag in ("language_like", "notation_like", "codebook_like", "semantics_light_like"):
            parse_bool(item[flag])
        if not present(item["architecture_cluster"]):
            item["architecture_cluster"] = "UNRESOLVED"
        rows.append(item)
    if len(rows) != 50:
        raise Refusal("world claims must be exactly 50 individual JSON files")
    return rows


def validate_claim_dimensions(db: sqlite3.Connection, world_claims: list[dict[str, str]],
                              model_tiers: dict[str, str]) -> tuple[str, ...]:
    decoders = tuple(row[0] for row in db.execute(
        "SELECT DISTINCT decoder_id FROM claims WHERE view='main' ORDER BY decoder_id"
    ))
    if len(decoders) != 5:
        raise Refusal(f"expected exactly five main decoders, found {len(decoders)}")
    if set(decoders) != set(model_tiers):
        raise Refusal("event decoder IDs do not match the frozen implementation_map")
    pair_decoders = tuple(row[0] for row in db.execute(
        "SELECT DISTINCT decoder_id FROM claims WHERE view='pair' ORDER BY decoder_id"
    ))
    if pair_decoders != decoders:
        raise Refusal("pair decoder IDs do not exactly match main decoder IDs")
    expected_main = len(WORLDS) * len(HELD_SEEDS) * len(REPRESENTATIONS) * len(decoders)
    got_main = db.execute(
        "SELECT COUNT(*) FROM (SELECT world_id,corpus_seed,representation,decoder_id "
        "FROM claims WHERE view='main' GROUP BY 1,2,3,4)"
    ).fetchone()[0]
    expected_pair = len(PAIR_WORLDS) * len(HELD_SEEDS) * len(REPRESENTATIONS) * len(decoders)
    got_pair = db.execute(
        "SELECT COUNT(*) FROM (SELECT world_id,corpus_seed,representation,decoder_id "
        "FROM claims WHERE view='pair' GROUP BY 1,2,3,4)"
    ).fetchone()[0]
    if got_main != expected_main or got_pair != expected_pair:
        raise Refusal("incomplete claim panel dimensions")
    expected_world = {(w, d) for w in WORLDS for d in decoders}
    got_world = {(r["world_id"], r["decoder_id"]) for r in world_claims}
    if got_world != expected_world:
        raise Refusal("world-claim panel is not exactly 10 worlds x 5 decoders")
    return decoders


def ingest_oracle(db: sqlite3.Connection, paths: list[Path],
                  expected_hashes: dict[Path, str]) -> dict[str, str]:
    placeholders = ",".join("?" for _ in range(len(ORACLE_FIELDS) + 1))
    sql = f"INSERT INTO oracle({quoted(ORACLE_FIELDS)},oracle_order) VALUES ({placeholders})"
    hashes: dict[str, str] = {}
    order_by_corpus: Counter[tuple[str, int]] = Counter()
    for path_index, path in enumerate(paths):
        digest = sha256_file(path)
        if digest != expected_hashes[path.resolve()]:
            raise Refusal("sealed oracle SHA-256 differs from the frozen corpus manifest")
        hashes[f"sealed_oracle_{path_index:03d}:{portable_path(path)}"] = digest
        handle, reader = open_tsv(path)
        try:
            require_header(reader, ORACLE_FIELDS, path)
            batch = []
            for row_number, row in enumerate(reader, 2):
                world = clean(row["world_id"])
                seed = safe_int(row["corpus_seed"], "oracle corpus_seed")
                if world not in WORLDS:
                    raise Refusal(f"bad oracle world at {portable_path(path)}:{row_number}")
                if seed not in HELD_SEEDS:
                    continue
                key = (world, seed)
                ordinal = order_by_corpus[key]
                order_by_corpus[key] += 1
                values = [clean(row[name]) for name in ORACLE_FIELDS]
                values[ORACLE_FIELDS.index("corpus_seed")] = str(seed)
                batch.append((*values, ordinal))
                if len(batch) >= 10000:
                    try:
                        db.executemany(sql, batch)
                    except sqlite3.IntegrityError as exc:
                        raise Refusal("duplicate sealed-oracle event key") from exc
                    batch.clear()
            if batch:
                try:
                    db.executemany(sql, batch)
                except sqlite3.IntegrityError as exc:
                    raise Refusal("duplicate sealed-oracle event key") from exc
        finally:
            handle.close()
    db.commit()
    expected = {(w, s) for w in WORLDS for s in HELD_SEEDS}
    if set(order_by_corpus) != expected:
        raise Refusal("sealed oracle lacks one or more held world/seed corpora")
    for key, count in order_by_corpus.items():
        if count < 8448 or count > 8512:
            raise Refusal(f"oracle corpus size outside frozen bounds for {key}: {count}")
    return hashes


def validate_oracle_joins(db: sqlite3.Connection, decoders: tuple[str, ...]) -> None:
    db.execute("CREATE INDEX claims_panel_idx ON claims(view,world_id,corpus_seed,representation,decoder_id)")
    db.execute("CREATE INDEX claims_event_idx ON claims(view,world_id,corpus_seed,event_id)")
    for view, worlds in (("main", set(WORLDS)), ("pair", PAIR_WORLDS)):
        for world in sorted(worlds):
            for seed in HELD_SEEDS:
                oracle_n = db.execute(
                    "SELECT COUNT(*) FROM oracle WHERE world_id=? AND corpus_seed=?",
                    (world, str(seed)),
                ).fetchone()[0]
                if view == "main":
                    expected_n = oracle_n
                else:
                    expected_n = db.execute(
                        "SELECT COUNT(DISTINCT event_id) FROM claims WHERE view='pair' "
                        "AND world_id=? AND corpus_seed=?", (world, str(seed)),
                    ).fetchone()[0]
                    if expected_n == 0:
                        raise Refusal(f"empty pair view for {world}/{seed}")
                for rep in REPRESENTATIONS:
                    for decoder in decoders:
                        count, distinct_events, joined = db.execute(
                            "SELECT COUNT(*),COUNT(DISTINCT c.event_id),COUNT(o.event_id) "
                            "FROM claims c LEFT JOIN oracle o ON o.world_id=c.world_id "
                            "AND o.corpus_seed=c.corpus_seed AND o.event_id=c.event_id "
                            "WHERE c.view=? AND c.world_id=? AND c.corpus_seed=? "
                            "AND c.representation=? AND c.decoder_id=?",
                            (view, world, str(seed), rep, decoder),
                        ).fetchone()
                        if count != expected_n or distinct_events != expected_n or joined != expected_n:
                            raise Refusal(f"non-exact {view} event/oracle join: {world}/{seed}/{rep}/{decoder}")
                if view == "pair":
                    expected_repeats = len(REPRESENTATIONS) * len(decoders)
                    bad = db.execute(
                        "SELECT COUNT(*) FROM (SELECT event_id,COUNT(*) n FROM claims "
                        "WHERE view='pair' AND world_id=? AND corpus_seed=? GROUP BY event_id HAVING n != ?)",
                        (world, str(seed), expected_repeats),
                    ).fetchone()[0]
                    if bad:
                        raise Refusal(f"pair event universe varies across panels: {world}/{seed}")


def entropy(counts: Counter[str], n: int) -> float:
    if n <= 0:
        return 0.0
    result = 0.0
    for count in counts.values():
        if count:
            p = count / n
            result -= p * math.log(p)
    return result


def comb2(value: int) -> int:
    return value * (value - 1) // 2


def cluster_scores(pairs: Counter[tuple[str, str]]) -> dict[str, float | int | None]:
    n = sum(pairs.values())
    if n == 0:
        return {"n": 0, "nmi": None, "ari": None, "pair_f1": None,
                "co_cluster_fpr": None}
    truth = Counter()
    pred = Counter()
    for (t, p), count in pairs.items():
        truth[t] += count
        pred[p] += count
    ht, hp = entropy(truth, n), entropy(pred, n)
    mi = 0.0
    for (t, p), count in pairs.items():
        if count:
            mi += (count / n) * math.log((count * n) / (truth[t] * pred[p]))
    nmi = 1.0 if ht == 0.0 and hp == 0.0 else (0.0 if ht + hp == 0.0 else 2.0 * mi / (ht + hp))
    tp = sum(comb2(c) for c in pairs.values())
    truth_pairs = sum(comb2(c) for c in truth.values())
    pred_pairs = sum(comb2(c) for c in pred.values())
    total_pairs = comb2(n)
    if total_pairs == 0:
        ari = 1.0
    else:
        expected = truth_pairs * pred_pairs / total_pairs
        maximum = 0.5 * (truth_pairs + pred_pairs)
        ari = 1.0 if maximum == expected else (tp - expected) / (maximum - expected)
    precision = tp / pred_pairs if pred_pairs else (1.0 if truth_pairs == 0 else 0.0)
    recall = tp / truth_pairs if truth_pairs else (1.0 if pred_pairs == 0 else 0.0)
    pair_f1 = 0.0 if precision + recall == 0.0 else 2.0 * precision * recall / (precision + recall)
    different_truth_pairs = total_pairs - truth_pairs
    false_co_clusters = pred_pairs - tp
    co_cluster_fpr = (false_co_clusters / different_truth_pairs
                      if different_truth_pairs else None)
    return {"n": n, "nmi": nmi, "ari": ari, "pair_f1": pair_f1,
            "co_cluster_fpr": co_cluster_fpr}


def binary_scores(tp: int, tn: int, fp: int, fn: int) -> dict[str, float | int | None]:
    positive = tp + fn
    negative = tn + fp
    tpr = tp / positive if positive else None
    tnr = tn / negative if negative else None
    ba = None if tpr is None or tnr is None else 0.5 * (tpr + tnr)
    denominator = math.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
    mcc = (tp * tn - fp * fn) / denominator if denominator else None
    fdr = fp / (tp + fp) if tp + fp else None
    return {
        "n": tp + tn + fp + fn, "tp": tp, "tn": tn, "fp": fp, "fn": fn,
        "balanced_accuracy": ba, "mcc": mcc, "fdr": fdr,
    }


def empty_result(view: str, world: str, seed: int, rep: str, decoder: str,
                 prop: str, kind: str, status: str) -> dict[str, object]:
    return {
        "view": view, "world_id": world, "corpus_seed": seed,
        "representation": rep, "decoder_id": decoder, "property": prop,
        "kind": kind, "status": status, "eligible_n": 0, "prediction_n": 0,
        "coverage": None, "nmi": None, "ari": None, "pair_f1": None,
        "balanced_accuracy": None, "mcc": None, "fdr": None, "top1": None,
        "mrr": None, "mrr_above_chance": None, "endpoint_accuracy": None,
        "exact_scope_accuracy": None, "interval_iou": None,
        "target_distance_mae": None, "false_discoveries": 0,
        "primary_index": None, "threshold_pass": False,
        "absent_truth_n": 0, "unresolved_n": 0, "invalid_n": 0,
        "co_cluster_fpr": None, "false_positive_rate": None,
        "endpoint_qualification": ENDPOINT_QUALIFICATION[prop], "metric_note": "",
    }


CLUSTER_MAP = {
    "LEXICAL_IDENTITY": ("lexical_cluster", "lexical_id"),
    "SEMANTIC_ENTITY_IDENTITY": ("entity_cluster", "semantic_entity_id"),
    "HISTORICAL_STEM_ANCESTRY": ("stem_cluster", "historical_stem_id"),
    "FUNCTION_CLASS": ("function_cluster", "function_class"),
    "REGISTER_LOCAL_VARIANT": ("register_variant_cluster", "register_realization_id"),
    "SEMANTIC_CATEGORY": ("semantic_category_cluster", "semantic_category"),
}


def panel_rows(db: sqlite3.Connection, view: str, world: str, seed: int,
               rep: str, decoder: str) -> list[sqlite3.Row]:
    db.row_factory = sqlite3.Row
    claim_values = [name for name in CLAIM_FIELDS if name not in {
        "world_id", "corpus_seed", "event_id", "representation", "decoder_id"
    }]
    oracle_values = [name for name in ORACLE_FIELDS if name not in {
        "world_id", "corpus_seed", "event_id"
    }]
    select = ["c.event_id AS event_id"]
    select.extend(f'c."{name}" AS "c_{name}"' for name in claim_values)
    select.extend(f'o."{name}" AS "o_{name}"' for name in oracle_values)
    select.append("o.oracle_order AS oracle_order")
    return db.execute(
        f"SELECT {','.join(select)} FROM claims c JOIN oracle o ON "
        "o.world_id=c.world_id AND o.corpus_seed=c.corpus_seed AND o.event_id=c.event_id "
        "WHERE c.view=? AND c.world_id=? AND c.corpus_seed=? AND c.representation=? "
        "AND c.decoder_id=? ORDER BY o.oracle_order",
        (view, world, str(seed), rep, decoder),
    ).fetchall()


def score_panel(db: sqlite3.Connection, view: str, world: str, seed: int,
                rep: str, decoder: str) -> list[dict[str, object]]:
    joined = panel_rows(db, view, world, seed, rep, decoder)
    results: list[dict[str, object]] = []
    for prop in PROPERTIES:
        if prop in HOLD_PROPERTIES:
            result = empty_result(view, world, seed, rep, decoder, prop,
                                  "interface_hold", "UNSCORED_INTERFACE_HOLD")
            result["metric_note"] = "SCORING_REVIEW interface HOLD; no surrogate mapping"
            results.append(result)
            continue
        if view == "pair" and (prop not in PAIR_ALLOWED or rep not in PAIR_ALLOWED[prop]):
            results.append(empty_result(view, world, seed, rep, decoder, prop, "prohibited",
                                        "UNSCORED_PAIR_PROTOCOL_PROHIBITED"))
            continue
        if prop in CLUSTER_MAP or prop == "ENTITY_REUSE":
            result = score_cluster_panel(joined, view, world, seed, rep, decoder, prop)
        else:
            raise AssertionError(prop)
        finalize_result(result)
        results.append(result)
    return results


def score_cluster_panel(joined: list[sqlite3.Row], view: str, world: str, seed: int,
                        rep: str, decoder: str, prop: str) -> dict[str, object]:
    result = empty_result(view, world, seed, rep, decoder, prop, "cluster", "SCORED")
    pairs: Counter[tuple[str, str]] = Counter()
    predictions = eligible_predictions = false_discoveries = absent_n = unresolved_n = 0
    parsed_entities: list[str | None] = []
    recurring_entities: Counter[str] = Counter()
    if prop == "ENTITY_REUSE":
        for row in joined:
            truth_value = parse_oracle_scalar(row["o_semantic_entity_id"], "semantic_entity_id")
            parsed_entities.append(truth_value)
            if truth_value is not None:
                recurring_entities[truth_value] += 1
    for row_index, row in enumerate(joined):
        if prop == "ENTITY_REUSE":
            candidate = parsed_entities[row_index]
            if candidate is not None and recurring_entities[candidate] < 2:
                # A singleton entity is outside the reuse endpoint, not an
                # oracle-negative reuse event and not a decoder false positive.
                continue
            truth = candidate or ""
            pred = clean(row["c_entity_cluster"])
        else:
            pred_field, truth_field = CLUSTER_MAP[prop]
            truth = parse_oracle_scalar(row[f"o_{truth_field}"], truth_field) or ""
            pred = clean(row[f"c_{pred_field}"])
        resolved = present(pred)
        if resolved:
            predictions += 1
        if not present(truth):
            absent_n += 1
            if resolved:
                false_discoveries += 1
            continue
        if resolved:
            eligible_predictions += 1
        else:
            unresolved_n += 1
        abstention = f"__ABSTENTION_SINGLETON__{clean(row['event_id'])}"
        pairs[(truth, pred if resolved else abstention)] += 1
    scores = cluster_scores(pairs)
    result.update({"eligible_n": scores["n"], "prediction_n": predictions,
                   "coverage": eligible_predictions / scores["n"] if scores["n"] else 0.0,
                   "nmi": scores["nmi"], "ari": scores["ari"],
                   "pair_f1": scores["pair_f1"], "false_discoveries": false_discoveries,
                   "absent_truth_n": absent_n, "unresolved_n": unresolved_n,
                   "co_cluster_fpr": scores["co_cluster_fpr"]})
    absent_claim_rate = false_discoveries / absent_n if absent_n else None
    applicable_rates = [rate for rate in (absent_claim_rate, scores["co_cluster_fpr"])
                        if rate is not None]
    result["false_positive_rate"] = max(applicable_rates) if applicable_rates else None
    result["fdr"] = result["false_positive_rate"]
    truth_counts = Counter()
    for (truth, _), count in pairs.items():
        truth_counts[truth] += count
    same_pairs = sum(comb2(count) for count in truth_counts.values())
    all_pairs = comb2(sum(truth_counts.values()))
    if scores["n"] == 0 or len(truth_counts) < 2 or same_pairs == 0 or same_pairs == all_pairs:
        result["status"] = "ABSENT_OR_NO_CAPACITY"
    return result


def primary_index(result: dict[str, object]) -> float | None:
    kind = result["kind"]
    if result["status"] != "SCORED":
        return None
    if kind == "cluster":
        values = (result["nmi"], result["ari"], result["pair_f1"])
        scales = (0.35, 0.20, 0.35)
    else:
        return None
    if any(value is None for value in values):
        return None
    return statistics.fmean(float(value) / scale for value, scale in zip(values, scales))


def passes_threshold(result: dict[str, object]) -> bool:
    if result["status"] != "SCORED":
        return False
    kind = str(result["kind"])
    try:
        if kind == "cluster":
            return (float(result["nmi"]) >= 0.35 and float(result["ari"]) >= 0.20
                    and float(result["pair_f1"]) >= 0.35)
    except (TypeError, ValueError):
        return False
    return False


def finalize_result(result: dict[str, object]) -> None:
    result["primary_index"] = primary_index(result)
    result["threshold_pass"] = passes_threshold(result)


METRIC_FIELDS = (
    "view", "world_id", "corpus_seed", "representation", "decoder_id",
    "property", "kind", "status", "eligible_n", "prediction_n", "coverage",
    "nmi", "ari", "pair_f1", "balanced_accuracy", "mcc", "fdr", "top1",
    "mrr", "mrr_above_chance", "endpoint_accuracy", "exact_scope_accuracy",
    "interval_iou", "target_distance_mae", "false_discoveries",
    "absent_truth_n", "unresolved_n", "invalid_n", "co_cluster_fpr",
    "false_positive_rate", "primary_index", "threshold_pass",
    "endpoint_qualification", "metric_note",
)
AGG_METRICS = (
    "coverage", "nmi", "ari", "pair_f1", "balanced_accuracy", "mcc", "fdr",
    "top1", "mrr", "mrr_above_chance", "endpoint_accuracy",
    "exact_scope_accuracy", "interval_iou", "target_distance_mae", "primary_index",
    "false_positive_rate", "co_cluster_fpr",
)


def median_values(rows: list[dict[str, object]]) -> dict[str, float | None]:
    values: dict[str, float | None] = {}
    for name in AGG_METRICS:
        available = [float(row[name]) for row in rows if row.get(name) is not None]
        values[name] = statistics.median(available) if len(available) == len(rows) and available else None
    return values


def aggregate_world_representation(panel: list[dict[str, object]], decoders: tuple[str, ...],
                                   view: str, model_tiers: dict[str, str]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str, str, str], list[dict[str, object]]] = defaultdict(list)
    for row in panel:
        if row["view"] == view:
            grouped[(str(row["property"]), str(row["world_id"]),
                     str(row["representation"]), str(row["decoder_id"]))].append(row)
    decoder_agg: dict[tuple[str, str, str, str], dict[str, object]] = {}
    for key, rows in grouped.items():
        scored = len(rows) == 5 and all(row["status"] == "SCORED" for row in rows)
        med = median_values(rows) if scored else {name: None for name in AGG_METRICS}
        synthetic = {"kind": rows[0]["kind"], "status": "SCORED" if scored else "UNSCORED", **med}
        synthetic["seeds_clear"] = sum(bool(row["threshold_pass"]) for row in rows)
        synthetic["threshold_pass"] = scored and synthetic["seeds_clear"] >= 3
        decoder_agg[key] = synthetic
    worlds = WORLDS if view == "main" else tuple(sorted(PAIR_WORLDS))
    output = []
    for prop in PROPERTIES:
        for world in worlds:
            for rep in REPRESENTATIONS:
                rows = [decoder_agg.get((prop, world, rep, decoder)) for decoder in decoders]
                valid = [row for row in rows if row is not None and row["status"] == "SCORED"]
                med = median_values(valid) if len(valid) == len(decoders) else {name: None for name in AGG_METRICS}
                clear_n = sum(bool(row and row.get("threshold_pass")) for row in rows)
                luna_clear = sum(bool(row and row.get("threshold_pass"))
                                 for decoder, row in zip(decoders, rows)
                                 if model_tiers[decoder] == "LUNA")
                status = "SCORED" if len(valid) == len(decoders) else "UNSCORED"
                output.append({
                    "view": view, "property": prop, "world_id": world,
                    "representation": rep, "status": status,
                    "decoders_scored": len(valid), "decoders_clear": clear_n,
                    "luna_decoders_clear": luna_clear,
                    "median_decoder_clear": status == "SCORED" and clear_n >= 3 and luna_clear >= 2,
                    "endpoint_qualification": ENDPOINT_QUALIFICATION[prop],
                    **med,
                })
    return output


def architecture_scores(rows: list[dict[str, str]], decoders: tuple[str, ...]) -> list[dict[str, object]]:
    indexed = {(r["world_id"], r["decoder_id"]): r for r in rows}
    output: list[dict[str, object]] = []
    for decoder in decoders:
        panel = [indexed[(world, decoder)] for world in WORLDS]
        pairs = Counter((WORLD_FAMILIES[row["world_id"]],
                         row["architecture_cluster"] if present(row["architecture_cluster"])
                         else f"__ABSTENTION_SINGLETON__{row['world_id']}") for row in panel)
        scores = cluster_scores(pairs)
        output.append({
            "decoder_id": decoder, "endpoint": "ARCHITECTURE_CLUSTER",
            "truth_basis": "FROZEN_BROAD_FAMILY", "n": scores["n"],
            "nmi": scores["nmi"], "ari": scores["ari"],
            "pair_f1": scores["pair_f1"], "balanced_accuracy": None,
            "mcc": None, "fdr": None,
        })
        for flag, positives in ARCH_FLAG_TRUTH.items():
            tp = tn = fp = fn = 0
            for row in panel:
                truth = row["world_id"] in positives
                prediction = parse_bool(row[flag])
                pred = bool(prediction) if prediction is not None else False
                if truth and pred:
                    tp += 1
                elif truth:
                    fn += 1
                elif pred:
                    fp += 1
                else:
                    tn += 1
            scores_b = binary_scores(tp, tn, fp, fn)
            output.append({
                "decoder_id": decoder, "endpoint": flag.upper(),
                "truth_basis": ("FROZEN_EXPLICIT" if flag == "semantics_light_like"
                                else "PREDECLARED_PUBLIC_ASSIGNMENT_PROXY"),
                "n": scores_b["n"], "nmi": None, "ari": None, "pair_f1": None,
                "balanced_accuracy": scores_b["balanced_accuracy"],
                "mcc": scores_b["mcc"], "fdr": scores_b["fdr"],
            })
    return output


def w10_table(panel: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in panel:
        if row["view"] == "main" and row["world_id"] == "W10":
            grouped[(str(row["property"]), str(row["representation"]))].append(row)
    output = []
    for prop in PROPERTIES:
        for rep in REPRESENTATIONS:
            rows = grouped[(prop, rep)]
            seed_rates = []
            for seed in HELD_SEEDS:
                values = [float(row["false_positive_rate"]) for row in rows
                          if row["corpus_seed"] == seed and row["false_positive_rate"] is not None]
                if values:
                    seed_rates.append(statistics.median(values))
            point = statistics.fmean(seed_rates) if len(seed_rates) == 5 else None
            if len(seed_rates) == 5:
                bootstrap = sorted(statistics.fmean(seed_rates[index] for index in draw)
                                   for draw in itertools.product(range(5), repeat=5))
                upper = bootstrap[math.ceil(0.95 * len(bootstrap)) - 1]
            else:
                upper = None
            output.append({
                "property": prop, "representation": rep,
                "endpoint_qualification": ENDPOINT_QUALIFICATION[prop],
                "panels": len(rows),
                "seed_false_positive_rates": ("|".join(f"{value:.10g}" for value in seed_rates)
                                               if seed_rates else "NA"),
                "false_positive_rate": point, "false_positive_upper95": upper,
                "upper95_method": "EXACT_SEED_CLUSTER_BOOTSTRAP_3125_NO_RECORD_RESAMPLE",
                "point_guard_pass": upper is not None and upper <= 0.10,
                "confirmatory_guard_pass": False,
                "inference_status": "EXPLORATORY_UNCONFIRMED",
            })
    return output


def property_decisions(main_agg: list[dict[str, object]], pair_agg: list[dict[str, object]],
                       w10: list[dict[str, object]]) -> list[dict[str, object]]:
    main_index = {(r["property"], r["world_id"], r["representation"]): r for r in main_agg}
    pair_index = {(r["property"], r["world_id"], r["representation"]): r for r in pair_agg}
    guard = {(r["property"], r["representation"]): r for r in w10}
    output = []
    for prop in PROPERTIES:
        if prop in HOLD_PROPERTIES:
            output.append({
                "property": prop, "decision": "UNSCORED_INTERFACE_HOLD",
                "endpoint_qualification": ENDPOINT_QUALIFICATION[prop],
                "representation": "NONE", "worlds_clear": 0,
                "meaningful_worlds_clear": 0, "clear_world_ids": "NONE",
                "clear_world_families": "NONE", "w10_false_positive_rate": None,
                "w10_false_positive_upper95": None,
                "w10_guard_pass": False, "organic_confusion_flag": False,
                "organic_confusion_representations": "NONE",
                "raw_p_value": None, "holm_adjusted_p_value": None,
                "inference_status": "UNSCORED_INTERFACE_HOLD",
            })
            continue
        rep_counts: dict[str, int] = {}
        meaningful_counts: dict[str, int] = {}
        for rep in REPRESENTATIONS:
            rep_counts[rep] = sum(bool(main_index[(prop, world, rep)]["median_decoder_clear"])
                                  for world in WORLDS if world != "W10")
            meaningful_counts[rep] = sum(bool(main_index[(prop, world, rep)]["median_decoder_clear"])
                                          for world in WORLDS if world != "W10")
        best_rep = min(REPRESENTATIONS, key=lambda rep: (-rep_counts[rep], REPRESENTATIONS.index(rep)))
        general_reps = [rep for rep in REPRESENTATIONS
                        if meaningful_counts[rep] >= 7 and bool(guard[(prop, rep)]["point_guard_pass"])]
        family_reps = [rep for rep in REPRESENTATIONS
                       if 2 <= meaningful_counts[rep] <= 6 and bool(guard[(prop, rep)]["point_guard_pass"])]
        if general_reps:
            exploratory_pattern = "POINT_THRESHOLD_GENERAL_PATTERN"
            chosen = general_reps[0]
        elif family_reps:
            exploratory_pattern = "POINT_THRESHOLD_FAMILY_SPECIFIC_PATTERN"
            chosen = max(family_reps, key=lambda rep: (meaningful_counts[rep], -REPRESENTATIONS.index(rep)))
        else:
            exploratory_pattern = "NO_POINT_THRESHOLD_PATTERN"
            chosen = best_rep
        clear_worlds = [world for world in WORLDS
                        if main_index[(prop, world, chosen)]["median_decoder_clear"]]
        output.append({
            "property": prop, "decision": "EXPLORATORY_UNCONFIRMED",
            "endpoint_qualification": ENDPOINT_QUALIFICATION[prop],
            "exploratory_pattern": exploratory_pattern, "representation": chosen,
            "worlds_clear": len(clear_worlds), "meaningful_worlds_clear": len([w for w in clear_worlds if w != "W10"]),
            "clear_world_ids": "|".join(clear_worlds) if clear_worlds else "NONE",
            "clear_world_families": "|".join(WORLD_FAMILIES[w] for w in clear_worlds if w != "W10") or "NONE",
            "w10_false_positive_rate": guard[(prop, chosen)]["false_positive_rate"],
            "w10_false_positive_upper95": guard[(prop, chosen)]["false_positive_upper95"],
            "w10_guard_pass": False,
            "organic_confusion_flag": False,
            "organic_confusion_representations": "UNSCORED_EQUIVALENCE_GATE_REQUIRED",
            "raw_p_value": None, "holm_adjusted_p_value": None,
            "inference_status": "EXPLORATORY_UNCONFIRMED_NO_RECORD_BLOCKS_OR_HOLM_INPUTS",
        })
    return output


def format_value(value: object) -> object:
    if value is None:
        return "NA"
    if isinstance(value, bool):
        return "1" if value else "0"
    if isinstance(value, float):
        return f"{value:.10g}"
    return value


def write_tsv(path: Path, rows: list[dict[str, object]], fields: tuple[str, ...] | None = None) -> None:
    if not rows and fields is None:
        raise Refusal(f"cannot infer empty TSV schema: {portable_path(path)}")
    names = fields or tuple(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=names, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({name: format_value(row.get(name)) for name in names})


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--claims-freeze", type=Path, required=True)
    parser.add_argument("--claims-validation", type=Path, required=True)
    parser.add_argument("--corpus-manifest", type=Path, required=True)
    parser.add_argument("--claims-tsv", type=Path, action="append", required=True)
    parser.add_argument("--pair-claims-tsv", type=Path, action="append", required=True)
    parser.add_argument("--world-claim-json", type=Path, action="append", required=True)
    parser.add_argument("--oracle-tsv", type=Path, action="append", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    role_paths = {
        "authentic_event_claims": args.claims_tsv,
        "pair_event_claims": args.pair_claims_tsv,
        "world_claims": args.world_claim_json,
    }
    input_hashes, model_tiers, freeze = validate_blind_gate(
        args.claims_freeze, args.claims_validation, role_paths)
    expected_oracles = validate_oracle_manifest(freeze, args.corpus_manifest, args.oracle_tsv)
    input_hashes["corpus_manifest"] = sha256_file(args.corpus_manifest)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="gdt395_score_") as temp_dir:
        db = create_database(str(Path(temp_dir) / "score.sqlite3"))
        try:
            ingest_claims(db, args.claims_tsv, "main")
            ingest_claims(db, args.pair_claims_tsv, "pair")
            world_claims = ingest_world_claims(args.world_claim_json)
            decoders = validate_claim_dimensions(db, world_claims, model_tiers)
            validate_preoracle_claims(db, decoders)
            # This is the first access to any sealed-oracle path.
            oracle_hashes = ingest_oracle(db, args.oracle_tsv, expected_oracles)
            input_hashes.update(oracle_hashes)
            validate_oracle_joins(db, decoders)
            panel: list[dict[str, object]] = []
            for view, worlds in (("main", WORLDS), ("pair", tuple(sorted(PAIR_WORLDS)))):
                for world in worlds:
                    for seed in HELD_SEEDS:
                        for rep in REPRESENTATIONS:
                            for decoder in decoders:
                                panel.extend(score_panel(db, view, world, seed, rep, decoder))
        finally:
            db.close()
    main_panel = [row for row in panel if row["view"] == "main"]
    pair_panel = [row for row in panel if row["view"] == "pair"]
    main_agg = aggregate_world_representation(main_panel, decoders, "main", model_tiers)
    pair_agg = aggregate_world_representation(pair_panel, decoders, "pair", model_tiers)
    w10 = w10_table(main_panel)
    decisions = property_decisions(main_agg, pair_agg, w10)
    architecture = architecture_scores(world_claims, decoders)
    stress = [{"stress_test": name,
               "status": "UNSCORED_NO_EXPLICIT_DECODER_PREDICTIONS"} for name in STRESS_TESTS]
    write_tsv(args.output_dir / "panel_metrics.tsv", main_panel, METRIC_FIELDS)
    write_tsv(args.output_dir / "pair_panel_metrics.tsv", pair_panel, METRIC_FIELDS)
    write_tsv(args.output_dir / "world_representation_metrics.tsv", main_agg)
    write_tsv(args.output_dir / "property_decisions.tsv", decisions)
    write_tsv(args.output_dir / "w10_false_discoveries.tsv", w10)
    write_tsv(args.output_dir / "architecture_metrics.tsv", architecture)
    write_tsv(args.output_dir / "method_stress_tests.tsv", stress)
    summary = {
        "schema": "GDT395_IDENTIFIABILITY_SCORE_SUMMARY_V1",
        "status": "PASS",
        "panel": {"worlds": 10, "held_seeds": list(HELD_SEEDS),
                  "representations": list(REPRESENTATIONS), "decoders": list(decoders),
                  "decoder_model_family": model_tiers,
                  "world_claim_files": len(args.world_claim_json)},
        "input_sha256": input_hashes,
        "decisions": {row["property"]: row["decision"] for row in decisions},
        "endpoint_qualification": ENDPOINT_QUALIFICATION,
        "interface_hold_properties": sorted(HOLD_PROPERTIES),
        "confirmatory_promotions_enabled": False,
        "unscored_method_stress_tests": list(STRESS_TESTS),
        "ambiguities": [
            "Coordinator, alternative, and reference retrieval are UNSCORED_INTERFACE_HOLD.",
            "Temporal-state gate and operator class are UNSCORED_INTERFACE_HOLD.",
            "Productive and fossilized morphology are HOLD because resolved claims are opaque component IDs, not Booleans.",
            "Record schema is HOLD without record_id; scope is HOLD without validated event order.",
            "ACTUAL_LEXICAL_MEANING is UNSCORED_INTERFACE_HOLD and is not lexical identity.",
            "No relation-type substring, state-pair, function-class, or lexical-identity surrogate is used.",
            "Architecture boolean truths except semantics-light are public-assignment proxies.",
            "A common representation must meet cross-world decision counts.",
            "All point-threshold patterns are EXPLORATORY_UNCONFIRMED; no PROPERTY_IDENTIFIABLE promotion is emitted.",
        ],
        "contains_event_rows": False,
        "voynich_rows": 0,
    }
    with (args.output_dir / "summary.json").open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, sort_keys=True, indent=2, ensure_ascii=True, allow_nan=False)
        handle.write("\n")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Refusal as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        raise SystemExit(2)
