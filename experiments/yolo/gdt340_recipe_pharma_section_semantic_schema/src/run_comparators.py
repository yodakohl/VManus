#!/usr/bin/env python3
"""Freeze GDT340's complete-record ontology instrument without Voynich input."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import random
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np


def find_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("repository root not found")


ROOT = find_root(Path(__file__).resolve())
sys.path.insert(0, str(ROOT))
from tools.vmanus_experiment import canonical_json_bytes, sha256_file  # noqa: E402

EXP = ROOT / "experiments/yolo/gdt340_recipe_pharma_section_semantic_schema"
ART = EXP / "artifacts"
DESIGN = ART / "gdt340_comparator_design.json"
ONTOLOGY = ART / "gdt340_event_ontology.tsv"
EXAMPLES = ART / "gdt340_comparator_examples.tsv"
VISUAL = ART / "gdt340_external_visual_observations.tsv"
PROVENANCE = ART / "gdt340_source_provenance.json"
METHOD = EXP / "METHOD.md"
AUDIT = EXP / "SOURCE_AUDIT.md"
INVENTORY = ROOT / "gdt176_corema_recipe_inventory.tsv"
SOURCE_FREEZE = ROOT / "gdt176_source_freeze.json"
MANIFEST = ROOT / "gdt176_corema_collection_manifest.tsv"
CACHE = ROOT / ".gdt176/corema"
RECORDS = ART / "gdt340_comparator_record_schemas.tsv"
FOLDS = ART / "gdt340_comparator_folds.tsv"
MODELS = ART / "gdt340_comparator_models.tsv"
NULL = ART / "gdt340_comparator_null.tsv"
FREEZE = ART / "gdt340_schema_instrument_freeze.json"
RESULT = ART / "gdt340_comparator_result.json"
REPORT = EXP / "COMPARATOR_REPORT.md"

NS = {"t": "http://www.tei-c.org/ns/1.0"}
XML_ID = "{http://www.w3.org/XML/1998/namespace}id"
SELECTED_TAGS = {"opener", "instruction", "ingredient", "tool", "closer"}
AXES = ("MATERIAL", "OPERATION", "INTERMEDIATE_STATE", "APPLICATION", "RESULT_CONDITION")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"empty table: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def lname(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def words(node: ET.Element) -> list[str]:
    return re.findall(r"[^\W_]+", " ".join(node.itertext()).lower(), flags=re.UNICODE)


def direct_words(node: ET.Element) -> list[str]:
    chunks = [node.text or ""] + [child.tail or "" for child in node]
    return re.findall(r"[^\W_]+", " ".join(chunks).lower(), flags=re.UNICODE)


def opaque(value: str) -> str:
    return hashlib.sha256(("GDT340_OPAQUE_UNIT_V1\0" + value).encode()).hexdigest()[:20]


def count_bin(value: int) -> str:
    if value <= 8:
        return "01_08"
    if value <= 16:
        return "09_16"
    if value <= 32:
        return "17_32"
    return "33_PLUS"


def content_hash(document: dict[str, object]) -> str:
    copy = dict(document)
    copy.pop("content_sha256", None)
    return hashlib.sha256(canonical_json_bytes(copy)).hexdigest()


def parse_records(inventory: dict[tuple[str, str], dict[str, str]], collections: list[str]) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for collection in collections:
        root = ET.parse(CACHE / f"{collection}.recipes.xml").getroot()
        for ordinal, recipe in enumerate(root.findall('.//*[@type="recipe"]', NS), 1):
            recipe_id = recipe.get(XML_ID, f"{collection}.ordinal{ordinal}")
            summary = inventory[(collection, recipe_id)]
            instructions = recipe.findall(".//t:instruction", NS)
            inst_index = {id(node): i for i, node in enumerate(instructions, 1)}
            parent = {id(child): node for node in recipe.iter() for child in node}
            units: list[dict[str, object]] = []
            external_ordinal = 0
            for element_ordinal, node in enumerate(recipe.iter(), 1):
                tag = lname(node.tag)
                if tag not in SELECTED_TAGS:
                    continue
                external_ordinal += 1
                ws = words(node)
                if tag in {"ingredient", "tool"}:
                    raw_identity = node.get("commodity") or " ".join(ws) or "EMPTY"
                else:
                    dw = direct_words(node) or ws
                    raw_identity = dw[0] if dw else "EMPTY"
                ancestor = node if tag == "instruction" else parent.get(id(node))
                while ancestor is not None and lname(ancestor.tag) != "instruction":
                    ancestor = parent.get(id(ancestor))
                instruction_ordinal = inst_index.get(id(ancestor), 0) if ancestor is not None else 0
                field = f"I{instruction_ordinal}" if instruction_ordinal else f"E{element_ordinal}"
                units.append({"identity": opaque(raw_identity), "field": field})
            if not units:
                continue
            targets = {
                "MATERIAL": int(int(summary["ingredient_count"]) + int(summary["dish_count"]) > 0),
                "OPERATION": int(int(summary["instruction_count"]) > 0),
                "INTERMEDIATE_STATE": int(int(summary["time_count"]) > 0),
                "APPLICATION": int(int(summary["servingTip_count"]) + int(summary["householdTip_count"]) > 0),
                "RESULT_CONDITION": int(int(summary["closer_count"]) + int(summary["dietetics_count"]) > 0),
                "TOOL_MEDIATION": int(int(summary["tool_count"]) > 0),
            }
            records.append({
                "collection": collection,
                "record": recipe_id,
                "units": units,
                "targets": targets,
            })
    return records


def reference_stats(records: list[dict[str, object]]) -> dict[str, object]:
    docs: dict[str, set[str]] = defaultdict(set)
    partners: dict[str, set[str]] = defaultdict(set)
    for record in records:
        identities = [str(unit["identity"]) for unit in record["units"]]
        unique = set(identities)
        for identity in unique:
            docs[identity].add(str(record["record"]))
            partners[identity].update(unique - {identity})
    return {"docs": docs, "partners": partners, "n_records": len(records)}


def record_vector(record: dict[str, object], stats: dict[str, object], subtract_self: bool) -> list[float]:
    units = record["units"]
    identities = [str(unit["identity"]) for unit in units]
    fields: dict[str, int] = Counter(str(unit["field"]) for unit in units)
    sizes = np.asarray(list(fields.values()), dtype=float)
    docs = stats["docs"]
    partners = stats["partners"]
    record_id = str(record["record"])
    dfs = []
    degrees = []
    for identity in identities:
        df = len(docs.get(identity, ())) - int(subtract_self and record_id in docs.get(identity, ()))
        dfs.append(max(0, df))
        degrees.append(len(partners.get(identity, ())))
    n = len(units)
    unique = len(set(identities))
    return [
        math.log2(1 + n),
        math.log2(1 + len(fields)),
        float(sizes.mean()),
        float(sizes.std()),
        float(sizes.max() / n),
        float(np.mean(sizes == 1)),
        unique / n,
        float(np.mean(np.asarray(dfs) > 0)),
        float(np.mean(dfs) / max(1, int(stats["n_records"]))),
        float(max(dfs, default=0) / max(1, int(stats["n_records"]))),
        float(np.mean(degrees) / max(1, int(stats["n_records"]))),
    ]


def fit_logistic(X: np.ndarray, y: np.ndarray, indices: tuple[int, ...], cfg: dict[str, object]) -> dict[str, object]:
    V = X[:, indices]
    mean = V.mean(axis=0)
    scale = V.std(axis=0)
    scale[scale < 1e-9] = 1.0
    Z = np.column_stack([np.ones(len(V)), np.clip((V - mean) / scale, -6, 6)])
    beta = np.zeros(Z.shape[1])
    prevalence = (float(y.sum()) + 0.5) / (len(y) + 1)
    beta[0] = math.log(prevalence / (1 - prevalence))
    m = np.zeros_like(beta)
    v = np.zeros_like(beta)
    for step in range(1, int(cfg["steps"]) + 1):
        logits = np.clip(Z @ beta, -30, 30)
        p = 1 / (1 + np.exp(-logits))
        grad = Z.T @ (p - y) / len(y)
        grad[1:] += float(cfg["ridge"]) * beta[1:]
        m = 0.9 * m + 0.1 * grad
        v = 0.999 * v + 0.001 * grad * grad
        beta -= float(cfg["learning_rate"]) * (m / (1 - 0.9**step)) / (np.sqrt(v / (1 - 0.999**step)) + 1e-8)
    return {"indices": indices, "mean": mean, "scale": scale, "beta": beta, "prevalence": prevalence}


def predict(X: np.ndarray, model: dict[str, object]) -> np.ndarray:
    V = X[:, model["indices"]]
    Z = np.column_stack([np.ones(len(V)), np.clip((V - model["mean"]) / model["scale"], -6, 6)])
    return 1 / (1 + np.exp(-np.clip(Z @ model["beta"], -30, 30)))


def bits(y: np.ndarray, p: np.ndarray) -> float:
    p = np.clip(p, 1e-12, 1 - 1e-12)
    return float(np.sum(-y * np.log2(p) - (1 - y) * np.log2(1 - p)))


def auc(y: np.ndarray, p: np.ndarray) -> float:
    positives = np.flatnonzero(y == 1)
    negatives = np.flatnonzero(y == 0)
    if not len(positives) or not len(negatives):
        return 0.5
    wins = sum(float(p[i] > p[j]) + 0.5 * float(p[i] == p[j]) for i in positives for j in negatives)
    return wins / (len(positives) * len(negatives))


def main() -> int:
    design = json.loads(DESIGN.read_text(encoding="utf-8"))
    inventory_rows = read_tsv(INVENTORY)
    inventory = {(row["collection_id"], row["recipe_id"]): row for row in inventory_rows}
    records = parse_records(inventory, design["collections"])
    if len(records) != 1136:
        raise AssertionError(len(records))
    record_export = []
    for record in records:
        field_count = len({str(unit["field"]) for unit in record["units"]})
        row = {
            "collection": record["collection"], "record": record["record"],
            "unit_count": len(record["units"]), "field_count": field_count,
            "source_forms_exported": "NO", "unit_order_exported": "NO",
        }
        row.update({axis.lower(): record["targets"][axis] for axis in (*AXES, "TOOL_MEDIATION")})
        record_export.append(row)
    write_tsv(RECORDS, record_export)

    fold_rows: list[dict[str, object]] = []
    all_predictions: dict[tuple[str, str], dict[str, list[object]]] = {}
    model_indices = {name: tuple(int(value) for value in values) for name, values in design["models"].items()}
    for held in design["collections"]:
        train = [record for record in records if record["collection"] != held]
        test = [record for record in records if record["collection"] == held]
        stats = reference_stats(train)
        X_train = np.asarray([record_vector(record, stats, False) for record in train])
        X_test = np.asarray([record_vector(record, stats, False) for record in test])
        for axis in AXES:
            y_train = np.asarray([int(record["targets"][axis]) for record in train], dtype=float)
            y_test = np.asarray([int(record["targets"][axis]) for record in test], dtype=float)
            prior = (float(y_train.sum()) + 0.5) / (len(y_train) + 1)
            p_prior = np.full(len(test), prior)
            prior_bits = bits(y_test, p_prior)
            all_predictions[(held, axis)] = {"y": list(y_test), "prior": list(p_prior), "count_bins": [count_bin(len(r["units"])) for r in test]}
            for model_name, indices in model_indices.items():
                model = fit_logistic(X_train, y_train, indices, design["optimizer"])
                p = predict(X_test, model)
                all_predictions[(held, axis)][model_name] = list(p)
                fold_rows.append({
                    "held_collection": held, "axis": axis, "model": model_name,
                    "records": len(test), "positives": int(y_test.sum()),
                    "bits": f"{bits(y_test, p):.9f}",
                    "prior_bits": f"{prior_bits:.9f}",
                    "gain_vs_prior_bits": f"{prior_bits - bits(y_test, p):.9f}",
                    "auc": f"{auc(y_test, p):.9f}",
                    "accuracy": f"{np.mean((p >= 0.5) == y_test):.9f}",
                })
    write_tsv(FOLDS, fold_rows)

    aggregate_rows: list[dict[str, object]] = []
    observed: dict[tuple[str, str], float] = {}
    for axis in AXES:
        for model_name in model_indices:
            selected = [row for row in fold_rows if row["axis"] == axis and row["model"] == model_name]
            gain = sum(float(row["gain_vs_prior_bits"]) for row in selected)
            observed[(axis, model_name)] = gain
            aggregate_rows.append({
                "axis": axis, "model": model_name,
                "records": len(records),
                "positives": sum(int(record["targets"][axis]) for record in records),
                "negative_records": sum(1 - int(record["targets"][axis]) for record in records),
                "positive_collections": sum(any(int(r["targets"][axis]) for r in records if r["collection"] == collection) for collection in design["collections"]),
                "positive_folds": sum(float(row["gain_vs_prior_bits"]) > 0 for row in selected),
                "gain_vs_prior_bits": f"{gain:.9f}",
                "bits_per_record_gain": f"{gain / len(records):.9f}",
                "mean_fold_auc": f"{np.mean([float(row['auc']) for row in selected]):.9f}",
                "local_p": "PENDING", "max_t_p": "PENDING", "recoverable": "PENDING",
            })

    rng = random.Random(int(design["null"]["seed"]))
    null_rows: list[dict[str, object]] = []
    exceed_local = Counter()
    exceed_max = Counter()
    keys = [(axis, model) for axis in AXES for model in model_indices]
    for world in range(int(design["null"]["worlds"])):
        world_gains = {key: 0.0 for key in keys}
        for held in design["collections"]:
            for axis in AXES:
                bundle = all_predictions[(held, axis)]
                y = list(bundle["y"])
                strata: dict[str, list[int]] = defaultdict(list)
                for i, bucket in enumerate(bundle["count_bins"]):
                    strata[bucket].append(i)
                perm = y[:]
                for indices in strata.values():
                    values = [y[i] for i in indices]
                    rng.shuffle(values)
                    for i, value in zip(indices, values):
                        perm[i] = value
                yp = np.asarray(perm)
                prior_bits = bits(yp, np.asarray(bundle["prior"]))
                for model in model_indices:
                    world_gains[(axis, model)] += prior_bits - bits(yp, np.asarray(bundle[model]))
        maximum = max(world_gains.values())
        null_rows.append({"world": world, "max_t_gain_bits": f"{maximum:.9f}"})
        for key in keys:
            exceed_local[key] += int(world_gains[key] >= observed[key] - 1e-12)
            exceed_max[key] += int(maximum >= observed[key] - 1e-12)
    write_tsv(NULL, null_rows)

    gates = design["axis_gate"]
    recoverable_axes = []
    for row in aggregate_rows:
        key = (str(row["axis"]), str(row["model"]))
        local_p = (exceed_local[key] + 1) / (int(design["null"]["worlds"]) + 1)
        max_p = (exceed_max[key] + 1) / (int(design["null"]["worlds"]) + 1)
        row["local_p"] = f"{local_p:.9f}"
        row["max_t_p"] = f"{max_p:.9f}"
        ok = (
            row["model"] == "STRUCTURE_PLUS_RECURRENCE"
            and int(row["positives"]) >= int(gates["minimum_positive_records"])
            and int(row["negative_records"]) >= int(gates["minimum_negative_records"])
            and int(row["positive_collections"]) >= int(gates["minimum_positive_collections"])
            and int(row["positive_folds"]) >= int(gates["minimum_positive_folds"])
            and float(row["gain_vs_prior_bits"]) > float(gates["gain_bits_min"])
            and max_p <= float(gates["max_t_p_max"])
        )
        row["recoverable"] = "YES" if ok else "NO"
        if ok:
            recoverable_axes.append(str(row["axis"]))
    write_tsv(MODELS, aggregate_rows)

    # Fit immutable full-corpus coefficients for Stage B.
    stats = reference_stats(records)
    X = np.asarray([record_vector(record, stats, False) for record in records])
    fitted = {}
    full_indices = model_indices["STRUCTURE_PLUS_RECURRENCE"]
    for axis in AXES:
        y = np.asarray([int(record["targets"][axis]) for record in records], dtype=float)
        model = fit_logistic(X, y, full_indices, design["optimizer"])
        fitted[axis] = {
            "feature_indices": list(full_indices), "mean": list(map(float, model["mean"])),
            "scale": list(map(float, model["scale"])), "beta": list(map(float, model["beta"])),
            "threshold_prevalence": float(model["prevalence"]),
        }
    optional_supported = any(axis in recoverable_axes for axis in ("INTERMEDIATE_STATE", "APPLICATION", "RESULT_CONDITION"))
    status = "COMPARATOR_RECORD_SCHEMA_RECOVERABLE" if optional_supported else "NO_OPTIONAL_RECORD_SCHEMA_RECOVERABLE"
    base_inputs = [METHOD, AUDIT, DESIGN, ONTOLOGY, EXAMPLES, VISUAL, PROVENANCE, INVENTORY, SOURCE_FREEZE, MANIFEST]
    for collection in design["collections"]:
        base_inputs.append(CACHE / f"{collection}.recipes.xml")
    freeze = {
        "schema": "GDT340_SCHEMA_INSTRUMENT_FREEZE_V1", "status": status,
        "chronology": "FROZEN_BEFORE_GDT327_TUPLE_VALUE_RETENTION_OR_SCORING",
        "target_schema_metadata_previously_inspected": True,
        "recoverable_axes": recoverable_axes, "primary_axes": list(AXES),
        "feature_names": design["feature_names"], "model": "STRUCTURE_PLUS_RECURRENCE",
        "fitted_axes": fitted,
        "inputs": {str(path.relative_to(ROOT)): sha256_file(path) for path in base_inputs},
        "outputs": {str(path.relative_to(ROOT)): sha256_file(path) for path in (RECORDS, FOLDS, MODELS, NULL)},
        "implementation": {str(Path(__file__).relative_to(ROOT)): sha256_file(Path(__file__))},
        "voynich_tuple_values_retained_or_scored": False,
        "f84": {"opened": False, "parsed": False, "retained": False, "joined": False, "scored": False},
        "claim_ceiling": "Readable-comparator complete-record schema instrument only; no Voynich role or meaning.",
    }
    freeze["content_sha256"] = content_hash(freeze)
    FREEZE.write_bytes(canonical_json_bytes(freeze))
    result = {
        "schema": "GDT340_COMPARATOR_RESULT_V1", "status": status,
        "records": len(records), "collections": len(design["collections"]),
        "recoverable_axes": recoverable_axes,
        "optional_axis_supported": optional_supported,
        "freeze_sha256": sha256_file(FREEZE),
        "inputs": freeze["inputs"], "outputs": {**freeze["outputs"], str(FREEZE.relative_to(ROOT)): sha256_file(FREEZE)},
        "implementation": freeze["implementation"],
        "voynich_tuple_values_retained_or_scored": False,
        "f84": freeze["f84"],
    }
    result["content_sha256"] = content_hash(result)
    RESULT.write_bytes(canonical_json_bytes(result))

    by_axis = {row["axis"]: row for row in aggregate_rows if row["model"] == "STRUCTURE_PLUS_RECURRENCE"}
    lines = [
        "# GDT340 comparator report — complete-record event schemas", "",
        f"Status: **{status}**.", "",
        "The ontology and instrument were derived from 1,136 complete records in six readable medieval recipe collections before any Voynich tuple value was retained or scored. Forms, language, order, and local token context were hidden from the model.", "",
        "## Held-collection recovery", "",
        "| event axis | positive / negative records | gain vs prevalence (bits) | positive folds | mean AUC | max-ten p | recoverable |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for axis in AXES:
        row = by_axis[axis]
        lines.append(f"| {axis} | {row['positives']} / {row['negative_records']} | {float(row['gain_vs_prior_bits']):+.3f} | {row['positive_folds']}/6 | {float(row['mean_fold_auc']):.3f} | {float(row['max_t_p']):.4f} | {row['recoverable']} |")
    lines += [
        "", "## Interpretation", "",
        "The three-witness fake-morel preparation and the two stuffed-apple records show qualitatively that MATERIAL→OPERATION→intermediate/result/application event structure survives wording, abbreviation, and layout variation even when individual optional events differ.", "",
        "Quantitative recoverability is stricter: only axes marked YES may enter the blind Voynich diagnostic. MATERIAL and OPERATION cannot support the decision by themselves because they are nearly universal. Failure of an optional axis means the present anonymous topology does not recover it across collections; it does not erase the readable ontology.", "",
        "No Voynich field or tuple has been assigned an event class. f84 was not accessed.", "",
    ]
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(f"{status} records={len(records)} recoverable={','.join(recoverable_axes) or 'NONE'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
