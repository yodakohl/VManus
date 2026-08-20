#!/usr/bin/env python3
"""Post-freeze, standard-library-only oracle scorer for GDT395.

This module is intentionally executable only as a script. It never imports a
world, generator, decoder, claim, or oracle module from the experiment.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import sqlite3
import statistics
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path


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
    "binary": {"balanced_accuracy": 0.65, "mcc": 0.20, "fdr_max": 0.40},
    "relation": {"coverage": 0.25, "mrr": 0.15, "mrr_above_chance": 0.05},
    "scope": {"coverage": 0.25, "interval_iou": 0.35},
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
PAIR_ALLOWED = {
    "LEXICAL_IDENTITY": set(REPRESENTATIONS) - {"INFERRED_COMPONENTS"},
    "SEMANTIC_ENTITY_IDENTITY": set(REPRESENTATIONS) - {"INFERRED_COMPONENTS"},
    "SCOPE": set(REPRESENTATIONS) - {"INFERRED_COMPONENTS"},
    "ENTITY_REUSE": set(REPRESENTATIONS) - {"INFERRED_COMPONENTS"},
    "RECORD_SCHEMA": {"RECORD_TOPOLOGY"},
}
STRESS_TESTS = (
    "EXACT_COMPOSITE_AS_WORD", "UNIVERSAL_COEFFICIENTS",
    "RESIDUALIZE_FREQUENCY_POSITION_RECURRENCE", "SCALAR_ROLE_BOTTLENECK",
    "FIXED_SHORT_HORIZON", "MULTI_CONSTRAINT_INTERSECTION",
)
MISSING = {"", "NONE", "NULL", "UNRESOLVED", "NA", "N/A", "[]", "{}"}
class Refusal(RuntimeError):
    """A hard precondition failure that must produce no scientific output."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_json(path: Path) -> dict:
    try:
        with path.open("r", encoding="utf-8") as handle:
            value = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise Refusal(f"cannot read required JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise Refusal(f"required JSON is not an object: {path}")
    return value


def artifact_bindings(value: object) -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []
    if isinstance(value, dict):
        path = value.get("path")
        digest = value.get("sha256")
        if isinstance(path, str) and isinstance(digest, str):
            found.append((path, digest.lower()))
        hashes = value.get("hashes")
        if isinstance(hashes, dict):
            for key, val in hashes.items():
                if isinstance(key, str) and isinstance(val, str):
                    found.append((key, val.lower()))
        for child in value.values():
            found.extend(artifact_bindings(child))
    elif isinstance(value, list):
        for child in value:
            found.extend(artifact_bindings(child))
    return found


def path_aliases(path: Path) -> set[str]:
    resolved = path.resolve()
    aliases = {str(path), str(resolved), path.name}
    try:
        aliases.add(str(resolved.relative_to(Path.cwd().resolve())))
    except ValueError:
        pass
    return aliases


def portable_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(Path.cwd().resolve()))
    except ValueError:
        return path.name


def require_binding(artifact: dict, path: Path, digest: str, label: str) -> None:
    aliases = path_aliases(path)
    matches = [(p, h) for p, h in artifact_bindings(artifact)
               if p in aliases or Path(p).resolve() == path.resolve()]
    if not matches:
        raise Refusal(f"{label} is not path-bound in artifact: {path}")
    if not any(h == digest for _, h in matches):
        raise Refusal(f"{label} SHA-256 mismatch: {path}")


def validate_blind_gate(freeze_path: Path, validation_path: Path,
                        claim_paths: list[Path]) -> dict[str, str]:
    freeze = load_json(freeze_path)
    validation = load_json(validation_path)
    expected = {"status": "PASS", "phase": "FROZEN_BEFORE_ORACLE_ACCESS",
                "oracle_blind": True}
    for key, wanted in expected.items():
        if freeze.get(key) != wanted:
            raise Refusal(f"claims freeze requires {key}={wanted!r}")
    if validation.get("status") != "PASS":
        raise Refusal("blind-claims validation status is not PASS")
    freeze_digest = sha256_file(freeze_path)
    require_binding(validation, freeze_path, freeze_digest, "claims freeze")
    hashes = {"claims_freeze": freeze_digest,
              "claims_validation": sha256_file(validation_path)}
    for index, path in enumerate(claim_paths):
        digest = sha256_file(path)
        require_binding(freeze, path, digest, "blind claim input")
        hashes[f"blind_claim_{index:03d}:{portable_path(path)}"] = digest
    return hashes


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
    raise Refusal(f"non-binary value in a binary field: {value!r}")


def parse_oracle_pipe(value: object, label: str) -> tuple[str, ...]:
    raw = clean(value)
    if raw in {"", "NULL", "UNRESOLVED"}:
        raise Refusal(f"invalid missing oracle value in {label}")
    atoms = raw.split("|")
    if any(not atom or atom != atom.strip() for atom in atoms):
        raise Refusal(f"noncanonical pipe value in {label}: {raw!r}")
    if len(atoms) != len(set(atoms)) or atoms != sorted(atoms):
        raise Refusal(f"unsorted or duplicate pipe atoms in {label}: {raw!r}")
    if "NONE" in atoms:
        if atoms != ["NONE"]:
            raise Refusal(f"NONE mixed with a value in {label}: {raw!r}")
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
        raise Refusal(f"invalid integer {label}: {value!r}") from exc


def open_tsv(path: Path) -> tuple[object, csv.DictReader]:
    try:
        handle = path.open("r", encoding="utf-8", newline="")
    except OSError as exc:
        raise Refusal(f"cannot open TSV {path}: {exc}") from exc
    reader = csv.DictReader(handle, delimiter="\t")
    if reader.fieldnames is None:
        handle.close()
        raise Refusal(f"TSV has no header: {path}")
    return handle, reader


def require_header(reader: csv.DictReader, fields: tuple[str, ...], path: Path) -> None:
    if tuple(reader.fieldnames or ()) != fields:
        raise Refusal(f"wrong TSV header for {path}")


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
                    raise Refusal(f"out-of-panel claim at {path}:{row_number}")
                if view == "pair" and world not in PAIR_WORLDS:
                    raise Refusal(f"non-pair world in pair claims at {path}:{row_number}")
                try:
                    confidence = float(row["confidence"])
                except ValueError as exc:
                    raise Refusal(f"bad confidence at {path}:{row_number}") from exc
                if not 0.0 <= confidence <= 1.0:
                    raise Refusal(f"confidence outside [0,1] at {path}:{row_number}")
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


def ingest_world_claims(paths: list[Path]) -> list[dict[str, str]]:
    required = ("world_id", "representation", *WORLD_CLAIM_FIELDS)
    rows: list[dict[str, str]] = []
    seen: set[tuple[str, str, str]] = set()
    for path in paths:
        handle, reader = open_tsv(path)
        try:
            require_header(reader, required, path)
            for row_number, row in enumerate(reader, 2):
                item = {name: clean(row[name]) for name in required}
                key = (item["world_id"], item["representation"], item["decoder_id"])
                if item["world_id"] not in WORLDS or item["representation"] not in REPRESENTATIONS:
                    raise Refusal(f"bad world-claim envelope at {path}:{row_number}")
                if key in seen:
                    raise Refusal(f"duplicate world claim key at {path}:{row_number}")
                seen.add(key)
                try:
                    confidence = float(item["confidence"])
                except ValueError as exc:
                    raise Refusal(f"bad world confidence at {path}:{row_number}") from exc
                if not 0.0 <= confidence <= 1.0:
                    raise Refusal(f"world confidence outside [0,1] at {path}:{row_number}")
                rows.append(item)
        finally:
            handle.close()
    return rows


def validate_claim_dimensions(db: sqlite3.Connection, world_claims: list[dict[str, str]]) -> tuple[str, ...]:
    decoders = tuple(row[0] for row in db.execute(
        "SELECT DISTINCT decoder_id FROM claims WHERE view='main' ORDER BY decoder_id"
    ))
    if len(decoders) != 5:
        raise Refusal(f"expected exactly five main decoders, found {len(decoders)}")
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
    expected_world = {(w, r, d) for w in WORLDS for r in REPRESENTATIONS for d in decoders}
    got_world = {(r["world_id"], r["representation"], r["decoder_id"]) for r in world_claims}
    if got_world != expected_world:
        raise Refusal("world-claim panel is not exactly 10 worlds x 6 representations x 5 decoders")
    return decoders


def ingest_oracle(db: sqlite3.Connection, paths: list[Path]) -> dict[str, str]:
    placeholders = ",".join("?" for _ in range(len(ORACLE_FIELDS) + 1))
    sql = f"INSERT INTO oracle({quoted(ORACLE_FIELDS)},oracle_order) VALUES ({placeholders})"
    hashes: dict[str, str] = {}
    order_by_corpus: Counter[tuple[str, int]] = Counter()
    for path_index, path in enumerate(paths):
        hashes[f"sealed_oracle_{path_index:03d}:{portable_path(path)}"] = sha256_file(path)
        handle, reader = open_tsv(path)
        try:
            require_header(reader, ORACLE_FIELDS, path)
            batch = []
            for row_number, row in enumerate(reader, 2):
                world = clean(row["world_id"])
                seed = safe_int(row["corpus_seed"], "oracle corpus_seed")
                if world not in WORLDS:
                    raise Refusal(f"bad oracle world at {path}:{row_number}")
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
        return {"n": 0, "nmi": None, "ari": None, "pair_f1": None}
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
    return {"n": n, "nmi": nmi, "ari": ari, "pair_f1": pair_f1}


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


def interval_iou(a: int, b: int, c: int, d: int) -> float:
    left1, right1 = sorted((a, b))
    left2, right2 = sorted((c, d))
    intersection = max(0, min(right1, right2) - max(left1, left2) + 1)
    union = max(right1, right2) - min(left1, left2) + 1
    return intersection / union


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
        "metric_note": "",
    }


CLUSTER_MAP = {
    "LEXICAL_IDENTITY": ("lexical_cluster", "lexical_id"),
    "SEMANTIC_ENTITY_IDENTITY": ("entity_cluster", "semantic_entity_id"),
    "HISTORICAL_STEM_ANCESTRY": ("stem_cluster", "historical_stem_id"),
    "FUNCTION_CLASS": ("function_cluster", "function_class"),
    "RECORD_SCHEMA": ("record_schema_cluster", "record_schema_id"),
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
    universe = {clean(row["event_id"]): int(row["oracle_order"]) for row in joined}
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
        elif prop in {"PRODUCTIVE_MORPHOLOGY", "FOSSILIZED_MORPHOLOGY"}:
            result = score_binary_panel(joined, view, world, seed, rep, decoder, prop)
        elif prop == "SCOPE":
            result = score_scope_panel(joined, universe, view, world, seed, rep, decoder)
        else:
            raise AssertionError(prop)
        finalize_result(result)
        results.append(result)
    return results


def score_cluster_panel(joined: list[sqlite3.Row], view: str, world: str, seed: int,
                        rep: str, decoder: str, prop: str) -> dict[str, object]:
    result = empty_result(view, world, seed, rep, decoder, prop, "cluster", "SCORED")
    pairs: Counter[tuple[str, str]] = Counter()
    predictions = false_discoveries = absent_n = 0
    for row in joined:
        if prop == "ENTITY_REUSE":
            truth = parse_oracle_scalar(row["o_semantic_entity_id"], "semantic_entity_id") or ""
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
        abstention = f"__ABSTENTION_SINGLETON__{clean(row['event_id'])}"
        pairs[(truth, pred if resolved else abstention)] += 1
    scores = cluster_scores(pairs)
    result.update({"eligible_n": scores["n"], "prediction_n": predictions,
                   "coverage": predictions / len(joined) if joined else 0.0,
                   "nmi": scores["nmi"], "ari": scores["ari"],
                   "pair_f1": scores["pair_f1"], "false_discoveries": false_discoveries})
    if world == "W10" and prop == "SEMANTIC_CATEGORY":
        result["false_discoveries"] = predictions
        result["fdr"] = 1.0 if predictions else 0.0
    else:
        result["fdr"] = false_discoveries / predictions if predictions else 0.0
    truth_counts = Counter()
    for (truth, _), count in pairs.items():
        truth_counts[truth] += count
    same_pairs = sum(comb2(count) for count in truth_counts.values())
    all_pairs = comb2(sum(truth_counts.values()))
    if scores["n"] == 0 or len(truth_counts) < 2 or same_pairs == 0 or same_pairs == all_pairs:
        result["status"] = "ABSENT_OR_NO_CAPACITY"
    return result


def score_binary_panel(joined: list[sqlite3.Row], view: str, world: str, seed: int,
                       rep: str, decoder: str, prop: str) -> dict[str, object]:
    result = empty_result(view, world, seed, rep, decoder, prop, "binary", "SCORED")
    tp = tn = fp = fn = covered = 0
    for row in joined:
        if prop == "PRODUCTIVE_MORPHOLOGY":
            truth = parse_bool(row["o_productive_morphology"])
            pred = parse_bool(row["c_productive_component_prediction"])
        else:
            truth = bool(parse_oracle_pipe(row["o_fossilized_component_ids"],
                                           "fossilized_component_ids"))
            pred = parse_bool(row["c_fossilized_component_prediction"])
        if truth is None:
            continue
        if pred is not None:
            covered += 1
        if pred is None:
            if truth:
                fn += 1
            else:
                fp += 1
            continue
        positive_call = pred
        if truth and positive_call:
            tp += 1
        elif truth:
            fn += 1
        elif positive_call:
            fp += 1
        else:
            tn += 1
    scores = binary_scores(tp, tn, fp, fn)
    result.update(scores)
    result.update({"eligible_n": scores["n"], "prediction_n": tp + fp,
                   "coverage": covered / scores["n"] if scores["n"] else 0.0,
                   "false_discoveries": fp})
    if scores["n"] == 0 or scores["balanced_accuracy"] is None or scores["mcc"] is None:
        result["status"] = "UNSCORED_DEGENERATE_BINARY_TRUTH"
    return result


def score_scope_panel(joined: list[sqlite3.Row], universe: dict[str, int],
                      view: str, world: str, seed: int, rep: str,
                      decoder: str) -> dict[str, object]:
    result = empty_result(view, world, seed, rep, decoder, "SCOPE", "scope", "SCORED")
    eligible = covered = predictions = false_discoveries = 0
    endpoint_hits = exact_hits = 0
    iou_sum = 0.0
    for row in joined:
        ts = parse_oracle_scalar(row["o_scope_start_event_id"], "scope_start_event_id")
        te = parse_oracle_scalar(row["o_scope_end_event_id"], "scope_end_event_id")
        if (ts is None) != (te is None):
            raise Refusal("one-sided oracle scope interval")
        ps, pe = clean(row["c_predicted_scope_start_event_id"]), clean(row["c_predicted_scope_end_event_id"])
        truth_ok = ts is not None and te is not None and ts in universe and te in universe
        if ts is not None and te is not None and (ts not in universe or te not in universe):
            raise Refusal("oracle scope endpoint outside permitted held view")
        if truth_ok and universe[ts] > universe[te]:
            raise Refusal("reversed oracle scope interval")
        predicted = present(ps) or present(pe)
        if predicted:
            predictions += 1
        if not truth_ok:
            if predicted:
                false_discoveries += 1
            continue
        eligible += 1
        pred_ok = ps in universe and pe in universe
        if pred_ok and universe[ps] > universe[pe]:
            pred_ok = False
        if not pred_ok:
            continue
        covered += 1
        endpoint_hits += int(ps == ts) + int(pe == te)
        exact_hits += int(ps == ts and pe == te)
        iou_sum += interval_iou(universe[ps], universe[pe], universe[ts], universe[te])
    result.update({
        "eligible_n": eligible, "prediction_n": predictions,
        "coverage": covered / eligible if eligible else 0.0,
        "endpoint_accuracy": endpoint_hits / (2 * eligible) if eligible else None,
        "exact_scope_accuracy": exact_hits / eligible if eligible else None,
        "interval_iou": iou_sum / eligible if eligible else None,
        "false_discoveries": false_discoveries,
        "fdr": false_discoveries / predictions if predictions else 0.0,
    })
    if eligible == 0:
        result["status"] = "UNSCORED_NO_ELIGIBLE_TRUTH"
    return result


def primary_index(result: dict[str, object]) -> float | None:
    kind = result["kind"]
    if result["status"] != "SCORED":
        return None
    if kind == "cluster":
        values = (result["nmi"], result["ari"], result["pair_f1"])
        scales = (0.35, 0.20, 0.35)
    elif kind == "binary":
        values = (result["balanced_accuracy"], result["mcc"], 1.0 - float(result["fdr"]))
        scales = (0.65, 0.20, 0.60)
    elif kind == "relation":
        values = (result["coverage"], result["mrr"], result["mrr_above_chance"])
        scales = (0.25, 0.15, 0.05)
    elif kind == "scope":
        values = (result["coverage"], result["interval_iou"])
        scales = (0.25, 0.35)
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
        if kind == "binary":
            return (float(result["balanced_accuracy"]) >= 0.65 and float(result["mcc"]) >= 0.20
                    and float(result["fdr"]) <= 0.40)
        if kind == "relation":
            return (float(result["coverage"]) >= 0.25 and float(result["mrr"]) >= 0.15
                    and float(result["mrr_above_chance"]) >= 0.05)
        if kind == "scope":
            return float(result["coverage"]) >= 0.25 and float(result["interval_iou"]) >= 0.35
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
    "primary_index", "threshold_pass", "metric_note",
)
AGG_METRICS = (
    "coverage", "nmi", "ari", "pair_f1", "balanced_accuracy", "mcc", "fdr",
    "top1", "mrr", "mrr_above_chance", "endpoint_accuracy",
    "exact_scope_accuracy", "interval_iou", "target_distance_mae", "primary_index",
)


def median_values(rows: list[dict[str, object]]) -> dict[str, float | None]:
    values: dict[str, float | None] = {}
    for name in AGG_METRICS:
        available = [float(row[name]) for row in rows if row.get(name) is not None]
        values[name] = statistics.median(available) if len(available) == len(rows) and available else None
    return values


def aggregate_world_representation(panel: list[dict[str, object]], decoders: tuple[str, ...],
                                   view: str) -> list[dict[str, object]]:
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
                status = "SCORED" if len(valid) == len(decoders) else "UNSCORED"
                output.append({
                    "view": view, "property": prop, "world_id": world,
                    "representation": rep, "status": status,
                    "decoders_scored": len(valid), "decoders_clear": clear_n,
                    "median_decoder_clear": status == "SCORED" and clear_n >= 3,
                    **med,
                })
    return output


def architecture_scores(rows: list[dict[str, str]], decoders: tuple[str, ...]) -> list[dict[str, object]]:
    indexed = {(r["world_id"], r["representation"], r["decoder_id"]): r for r in rows}
    output: list[dict[str, object]] = []
    for rep in REPRESENTATIONS:
        for decoder in decoders:
            panel = [indexed[(world, rep, decoder)] for world in WORLDS]
            pairs = Counter((WORLD_FAMILIES[row["world_id"]],
                             row["architecture_cluster"] if present(row["architecture_cluster"])
                             else "UNRESOLVED") for row in panel)
            scores = cluster_scores(pairs)
            output.append({
                "representation": rep, "decoder_id": decoder,
                "endpoint": "ARCHITECTURE_CLUSTER", "truth_basis": "FROZEN_BROAD_FAMILY",
                "n": scores["n"], "nmi": scores["nmi"], "ari": scores["ari"],
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
                    "representation": rep, "decoder_id": decoder,
                    "endpoint": flag.upper(),
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
            discoveries = sum(int(row["false_discoveries"]) for row in rows)
            predictions = sum(int(row["prediction_n"]) for row in rows)
            output.append({
                "property": prop, "representation": rep,
                "panels": len(rows), "predictions": predictions,
                "false_discoveries": discoveries,
                "false_discovery_rate": discoveries / predictions if predictions else 0.0,
                "guard_pass": (discoveries / predictions if predictions else 0.0) <= 0.10,
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
                "representation": "NONE", "worlds_clear": 0,
                "meaningful_worlds_clear": 0, "clear_world_ids": "NONE",
                "clear_world_families": "NONE", "w10_false_discovery_rate": None,
                "w10_guard_pass": False, "organic_confusion_flag": False,
                "organic_confusion_representations": "NONE",
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
                        if meaningful_counts[rep] >= 7 and bool(guard[(prop, rep)]["guard_pass"])]
        family_reps = [rep for rep in REPRESENTATIONS
                       if 2 <= meaningful_counts[rep] <= 6 and bool(guard[(prop, rep)]["guard_pass"])]
        confused_reps: list[str] = []
        if general_reps:
            decision = "PROPERTY_IDENTIFIABLE_FROM_INTERNAL_STRUCTURE"
            chosen = general_reps[0]
        elif family_reps:
            decision = "PROPERTY_ONLY_IDENTIFIABLE_UNDER_SPECIFIC_WORLD_FAMILIES"
            chosen = max(family_reps, key=lambda rep: (meaningful_counts[rep], -REPRESENTATIONS.index(rep)))
        elif prop in {"SEMANTIC_CATEGORY", "ACTUAL_LEXICAL_MEANING"}:
            decision = "PROPERTY_REQUIRES_EXTERNAL_GROUNDING"
            chosen = best_rep
        else:
            decision = "NOT_IDENTIFIABLE_BY_THIS_PANEL"
            chosen = best_rep
        clear_worlds = [world for world in WORLDS
                        if main_index[(prop, world, chosen)]["median_decoder_clear"]]
        output.append({
            "property": prop, "decision": decision, "representation": chosen,
            "worlds_clear": len(clear_worlds), "meaningful_worlds_clear": len([w for w in clear_worlds if w != "W10"]),
            "clear_world_ids": "|".join(clear_worlds) if clear_worlds else "NONE",
            "clear_world_families": "|".join(WORLD_FAMILIES[w] for w in clear_worlds if w != "W10") or "NONE",
            "w10_false_discovery_rate": guard[(prop, chosen)]["false_discovery_rate"],
            "w10_guard_pass": guard[(prop, chosen)]["guard_pass"],
            "organic_confusion_flag": False,
            "organic_confusion_representations": "UNSCORED_EQUIVALENCE_GATE_REQUIRED",
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
        raise Refusal(f"cannot infer empty TSV schema: {path}")
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
    parser.add_argument("--claims-tsv", type=Path, action="append", required=True)
    parser.add_argument("--pair-claims-tsv", type=Path, action="append", required=True)
    parser.add_argument("--world-claims-tsv", type=Path, action="append", required=True)
    parser.add_argument("--oracle-tsv", type=Path, action="append", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    claim_inputs = [*args.claims_tsv, *args.pair_claims_tsv, *args.world_claims_tsv]
    input_hashes = validate_blind_gate(args.claims_freeze, args.claims_validation, claim_inputs)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="gdt395_score_") as temp_dir:
        db = create_database(str(Path(temp_dir) / "score.sqlite3"))
        try:
            ingest_claims(db, args.claims_tsv, "main")
            ingest_claims(db, args.pair_claims_tsv, "pair")
            world_claims = ingest_world_claims(args.world_claims_tsv)
            decoders = validate_claim_dimensions(db, world_claims)
            # This is the first access to any sealed-oracle path.
            oracle_hashes = ingest_oracle(db, args.oracle_tsv)
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
    main_agg = aggregate_world_representation(main_panel, decoders, "main")
    pair_agg = aggregate_world_representation(pair_panel, decoders, "pair")
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
                  "representations": list(REPRESENTATIONS), "decoders": list(decoders)},
        "input_sha256": input_hashes,
        "decisions": {row["property"]: row["decision"] for row in decisions},
        "unscored_method_stress_tests": list(STRESS_TESTS),
        "ambiguities": [
            "Coordinator, alternative, and reference retrieval are UNSCORED_INTERFACE_HOLD.",
            "Temporal-state gate and operator class are UNSCORED_INTERFACE_HOLD.",
            "ACTUAL_LEXICAL_MEANING is UNSCORED_INTERFACE_HOLD and is not lexical identity.",
            "No relation-type substring, state-pair, function-class, or lexical-identity surrogate is used.",
            "Architecture boolean truths except semantics-light are public-assignment proxies.",
            "A common representation must meet cross-world decision counts.",
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
