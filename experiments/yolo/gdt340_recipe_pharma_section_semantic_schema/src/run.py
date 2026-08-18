#!/usr/bin/env python3
"""Apply the frozen GDT340 record-schema instrument section-specifically."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import random
import sys
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
from tools.vmanus_experiment import GuardedTSV, canonical_json_bytes, sha256_file  # noqa: E402

EXP = ROOT / "experiments/yolo/gdt340_recipe_pharma_section_semantic_schema"
ART = EXP / "artifacts"
METHOD = EXP / "METHOD.md"
DESIGN = ART / "gdt340_comparator_design.json"
FREEZE = ART / "gdt340_schema_instrument_freeze.json"
COMPARATOR = ART / "gdt340_comparator_result.json"
SOURCE = ROOT / "gdt327_joint_tuple_interlinear.tsv"
SOURCE_RESULT = ROOT / "gdt327_result.json"
INVENTORY = ART / "gdt340_voynich_record_inventory.tsv"
FOLDS = ART / "gdt340_voynich_schema_folds.tsv"
MODELS = ART / "gdt340_voynich_schema_models.tsv"
NULL = ART / "gdt340_voynich_schema_null.tsv"
COUNTER = ART / "gdt340_counterexamples.tsv"
RESULT = ART / "gdt340_result.json"
REPORT = EXP / "REPORT.md"
VALIDATOR = EXP / "src/validate.py"


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"empty table {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def content_hash(document: dict[str, object]) -> str:
    copy = dict(document)
    copy.pop("content_sha256", None)
    return hashlib.sha256(canonical_json_bytes(copy)).hexdigest()


def size_bin(value: int) -> str:
    if value <= 8:
        return "01_08"
    if value <= 16:
        return "09_16"
    if value <= 32:
        return "17_32"
    return "33_PLUS"


def field_bin(value: int) -> str:
    if value <= 2:
        return "01_02"
    if value <= 4:
        return "03_04"
    if value <= 8:
        return "05_08"
    return "09_PLUS"


def logit(value: float) -> float:
    value = min(max(value, 1e-9), 1 - 1e-9)
    return math.log(value / (1 - value))


def logistic(value: float) -> float:
    return 1 / (1 + math.exp(-max(-30.0, min(30.0, value))))


def binary_bits(y: int, p: float) -> float:
    p = min(max(p, 1e-12), 1 - 1e-12)
    return -math.log2(p if y else 1 - p)


def source_records(rows: list[dict[str, str]], panel_name: str, section: str, register: str) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        if row["section"] == section and row["register"] == register:
            grouped[(row["page"], row["physical_folio"], row["record_ordinal"])].append(row)
    records = []
    for (page, folio, ordinal), events in sorted(grouped.items()):
        events.sort(key=lambda row: (row["locus"], int(row["group_index"])))
        records.append({
            "panel": panel_name, "page": page, "folio": folio,
            "record": f"{page}|R{ordinal}",
            "units": [{"identity": row["joint_tuple_id"], "field": f"{row['locus']}|{row['field_ordinal']}"} for row in events],
        })
    return records


def reference_stats(records: list[dict[str, object]]) -> dict[str, object]:
    docs: dict[str, set[str]] = defaultdict(set)
    partners: dict[str, set[str]] = defaultdict(set)
    folios: dict[str, set[str]] = defaultdict(set)
    for record in records:
        identities = {str(unit["identity"]) for unit in record["units"]}
        for identity in identities:
            docs[identity].add(str(record["record"]))
            folios[identity].add(str(record["folio"]))
            partners[identity].update(identities - {identity})
    return {"docs": docs, "folios": folios, "partners": partners, "n_records": len(records)}


def vector(record: dict[str, object], stats: dict[str, object]) -> list[float]:
    identities = [str(unit["identity"]) for unit in record["units"]]
    fields: dict[str, int] = Counter(str(unit["field"]) for unit in record["units"])
    sizes = np.asarray(list(fields.values()), dtype=float)
    dfs = [len(stats["docs"].get(identity, ())) for identity in identities]
    degrees = [len(stats["partners"].get(identity, ())) for identity in identities]
    n = len(identities)
    return [
        math.log2(1 + n), math.log2(1 + len(fields)), float(sizes.mean()), float(sizes.std()),
        float(sizes.max() / n), float(np.mean(sizes == 1)), len(set(identities)) / n,
        float(np.mean(np.asarray(dfs) > 0)), float(np.mean(dfs) / max(1, int(stats["n_records"]))),
        float(max(dfs, default=0) / max(1, int(stats["n_records"]))),
        float(np.mean(degrees) / max(1, int(stats["n_records"]))),
    ]


def comparator_probability(values: list[float], model: dict[str, object]) -> float:
    indices = [int(value) for value in model["feature_indices"]]
    mean = np.asarray(model["mean"], dtype=float)
    scale = np.asarray(model["scale"], dtype=float)
    beta = np.asarray(model["beta"], dtype=float)
    selected = np.asarray(values, dtype=float)[indices]
    z = np.concatenate([[1.0], np.clip((selected - mean) / scale, -6, 6)])
    return logistic(float(z @ beta))


def baseline_probability(record: dict[str, object], training_labels: list[tuple[dict[str, object], int]], alpha: float) -> tuple[float, str, int]:
    n_units = len(record["units"])
    n_fields = len({str(unit["field"]) for unit in record["units"]})
    levels = [
        ("EXACT_SIZE_FIELD", lambda other: len(other["units"]) == n_units and len({str(u["field"]) for u in other["units"]}) == n_fields),
        ("BINNED_SIZE_FIELD", lambda other: size_bin(len(other["units"])) == size_bin(n_units) and field_bin(len({str(u["field"]) for u in other["units"]})) == field_bin(n_fields)),
        ("PANEL_PRIOR", lambda other: True),
    ]
    for name, predicate in levels:
        values = [label for other, label in training_labels if predicate(other)]
        if len(values) >= 4 or name == "PANEL_PRIOR":
            return (sum(values) + alpha) / (len(values) + 2 * alpha), name, len(values)
    raise AssertionError("unreachable")


def main() -> int:
    design = json.loads(DESIGN.read_text())
    freeze = json.loads(FREEZE.read_text())
    comparator = json.loads(COMPARATOR.read_text())
    guard = GuardedTSV(SOURCE, selector_column="page", forbidden_action="error")
    rows = list(guard)
    if guard.stats.skipped_forbidden or any(r["page"].startswith("f84") or r["locus"].startswith("f84") for r in rows):
        raise AssertionError("f84 entered GDT340")
    panels = {
        name: source_records(rows, name, spec["section"], spec["register"])
        for name, spec in design["target_panels"].items()
    }
    recoverable = list(freeze["recoverable_axes"])
    if not recoverable:
        raise AssertionError("Stage A exposed no recoverable axis")
    alpha = float(design["target_model"]["jeffreys_alpha"])
    shrink = float(design["target_model"]["tuple_shrinkage_trials"])
    fold_rows: list[dict[str, object]] = []
    inventory_rows: list[dict[str, object]] = []
    prediction_cache: dict[tuple[str, str, str], list[dict[str, object]]] = {}

    for panel, records in panels.items():
        for held in sorted({str(record["folio"]) for record in records}):
            train = [record for record in records if record["folio"] != held]
            test = [record for record in records if record["folio"] == held]
            stats = reference_stats(train)
            for axis in recoverable:
                frozen_model = freeze["fitted_axes"][axis]
                threshold = float(frozen_model["threshold_prevalence"])
                train_labels = [(record, int(comparator_probability(vector(record, stats), frozen_model) >= threshold)) for record in train]
                tuple_counts: dict[str, list[int]] = defaultdict(lambda: [0, 0])
                tuple_folios: dict[str, set[str]] = defaultdict(set)
                for record, label in train_labels:
                    for identity in {str(unit["identity"]) for unit in record["units"]}:
                        tuple_counts[identity][0] += label
                        tuple_counts[identity][1] += 1
                        tuple_folios[identity].add(str(record["folio"]))
                fold_predictions = []
                for record in test:
                    values = vector(record, stats)
                    schema_p = comparator_probability(values, frozen_model)
                    y = int(schema_p >= threshold)
                    base, level, reference_n = baseline_probability(record, train_labels, alpha)
                    supported = sorted({str(unit["identity"]) for unit in record["units"] if len(tuple_folios.get(str(unit["identity"]), ())) >= 2})
                    shifts = []
                    for identity in supported:
                        positive, total = tuple_counts[identity]
                        p_tuple = (positive + alpha + shrink * base) / (total + 2 * alpha + shrink)
                        shifts.append(logit(p_tuple) - logit(base))
                    candidate = logistic(logit(base) + (sum(shifts) / len(shifts) if shifts else 0.0))
                    item = {
                        "panel": panel, "axis": axis, "held_folio": held,
                        "page": record["page"], "record": record["record"],
                        "unit_count": len(record["units"]),
                        "field_count": len({str(unit["field"]) for unit in record["units"]}),
                        "schema_probability": schema_p, "schema_assignment": y,
                        "baseline_probability": base, "candidate_probability": candidate,
                        "baseline_level": level, "baseline_reference_records": reference_n,
                        "supported_tuple_count": len(supported),
                        "baseline_bits": binary_bits(y, base), "candidate_bits": binary_bits(y, candidate),
                    }
                    fold_predictions.append(item)
                    inventory_rows.append({
                        "panel": panel, "page": record["page"], "physical_folio": held,
                        "record": record["record"], "unit_count": item["unit_count"],
                        "field_count": item["field_count"], "axis": axis,
                        "comparator_axis_probability": f"{schema_p:.9f}",
                        "comparator_axis_assignment": y,
                        "supported_cross_folio_tuple_count": len(supported),
                        "tuple_ids_exported": "NO", "surface_forms_exported": "NO",
                    })
                prediction_cache[(panel, axis, held)] = fold_predictions
                base_bits = sum(float(item["baseline_bits"]) for item in fold_predictions)
                cand_bits = sum(float(item["candidate_bits"]) for item in fold_predictions)
                covered = [item for item in fold_predictions if int(item["supported_tuple_count"]) > 0]
                fold_rows.append({
                    "panel": panel, "axis": axis, "held_folio": held,
                    "records": len(fold_predictions), "positive_assignments": sum(int(item["schema_assignment"]) for item in fold_predictions),
                    "covered_records": len(covered), "baseline_bits": f"{base_bits:.9f}",
                    "candidate_bits": f"{cand_bits:.9f}", "gain_bits": f"{base_bits - cand_bits:.9f}",
                    "covered_gain_bits": f"{sum(float(item['baseline_bits']) - float(item['candidate_bits']) for item in covered):.9f}",
                })
    write_tsv(INVENTORY, inventory_rows)
    write_tsv(FOLDS, fold_rows)

    model_rows: list[dict[str, object]] = []
    observed: dict[tuple[str, str], float] = {}
    for panel, records in panels.items():
        for axis in recoverable:
            selected = [row for row in fold_rows if row["panel"] == panel and row["axis"] == axis]
            gain = sum(float(row["gain_bits"]) for row in selected)
            observed[(panel, axis)] = gain
            total_records = sum(int(row["records"]) for row in selected)
            covered = sum(int(row["covered_records"]) for row in selected)
            model_rows.append({
                "panel": panel, "axis": axis, "records": total_records,
                "folios": len(selected), "positive_assignments": sum(int(row["positive_assignments"]) for row in selected),
                "covered_records": covered, "coverage": f"{covered / max(1,total_records):.9f}",
                "gain_bits": f"{gain:.9f}", "gain_bits_per_record": f"{gain / max(1,total_records):.9f}",
                "positive_folios": sum(float(row["gain_bits"]) > 0 for row in selected),
                "mobile_exact_null_records": 0, "local_p": "PENDING", "max_family_p": "PENDING",
            })

    # Fixed-prediction exact opportunity null. Exact unit/field sizes are
    # intentionally preserved; one-sided/singleton strata remain immobile.
    rng = random.Random(int(design["target_model"]["seed"]))
    endpoints = sorted(observed)
    exceed_local = Counter()
    exceed_max = Counter()
    null_rows = []
    mobile_by_endpoint: dict[tuple[str, str], set[int]] = defaultdict(set)
    for world in range(int(design["target_model"]["worlds"])):
        gains = {}
        for panel, axis in endpoints:
            total = 0.0
            for held in sorted({key[2] for key in prediction_cache if key[:2] == (panel, axis)}):
                items = prediction_cache[(panel, axis, held)]
                strata: dict[tuple[int, int], list[int]] = defaultdict(list)
                for i, item in enumerate(items):
                    strata[(int(item["unit_count"]), int(item["field_count"]))].append(i)
                permuted = [int(item["schema_assignment"]) for item in items]
                for indices in strata.values():
                    values = [permuted[i] for i in indices]
                    if len(set(values)) > 1:
                        mobile_by_endpoint[(panel, axis)].update(indices)
                    rng.shuffle(values)
                    for i, value in zip(indices, values):
                        permuted[i] = value
                for item, y in zip(items, permuted):
                    total += binary_bits(y, float(item["baseline_probability"])) - binary_bits(y, float(item["candidate_probability"]))
            gains[(panel, axis)] = total
        maximum = max(gains.values())
        null_rows.append({"world": world, "max_family_gain_bits": f"{maximum:.9f}"})
        for endpoint in endpoints:
            exceed_local[endpoint] += int(gains[endpoint] >= observed[endpoint] - 1e-12)
            exceed_max[endpoint] += int(maximum >= observed[endpoint] - 1e-12)
    write_tsv(NULL, null_rows)

    worlds = int(design["target_model"]["worlds"])
    for row in model_rows:
        endpoint = (str(row["panel"]), str(row["axis"]))
        row["mobile_exact_null_records"] = len(mobile_by_endpoint[endpoint])
        row["local_p"] = f"{(exceed_local[endpoint] + 1)/(worlds+1):.9f}"
        row["max_family_p"] = f"{(exceed_max[endpoint] + 1)/(worlds+1):.9f}"
    write_tsv(MODELS, model_rows)

    powered = [row for row in model_rows if int(row["records"]) >= 20 and int(row["covered_records"]) >= 10 and int(row["mobile_exact_null_records"]) >= 10]
    selector_charge = math.log2(max(1, len(powered)))
    leads = [
        row for row in powered
        if float(row["gain_bits"]) - selector_charge > 0
        and int(row["positive_folios"]) / int(row["folios"]) >= 0.60
        and float(row["max_family_p"]) <= 0.05
    ]
    if not powered:
        status = "INSUFFICIENT_COMPARATOR_OR_TARGET_CAPACITY"
    elif leads:
        status = "SECTION_SPECIFIC_SCHEMA_RECOVERY_LEAD"
    else:
        status = "NO_BLIND_SECTION_SPECIFIC_SCHEMA_RECOVERY"
    counter_rows = [
        {"counterexample": "MATERIAL_OPERATION_NEAR_UNIVERSAL", "observation": "MATERIAL and OPERATION have only two and one negative readable records", "consequence": "cannot identify a semantic schema"},
        {"counterexample": "APPLICATION_RESULT_NOT_CORRECTED", "observation": "both axes gain raw held bits but fail max-ten correction", "consequence": "excluded from Voynich scoring"},
        {"counterexample": "PHARMA_SMALL_PANEL", "observation": f"PHARMA_P has {len(panels['PHARMA_P'])} complete mechanical records on {len({r['folio'] for r in panels['PHARMA_P']})} folios", "consequence": "separate capacity result; never pooled with Recipe/Stars"},
        {"counterexample": "EXACT_NULL_LOW_MOBILITY", "observation": "; ".join(f"{r['panel']}={r['mobile_exact_null_records']}" for r in model_rows), "consequence": "a positive descriptive gain cannot be called confirmed without exact opportunity mobility"},
        {"counterexample": "FROZEN_ASSIGNMENT_NOT_TRUTH", "observation": "target labels are thresholded comparator probabilities", "consequence": "recovery is schema-likeness consistency, not Voynich semantic accuracy"},
        {"counterexample": "PRIOR_FIELD_ROLE_FAILURE", "observation": "GDT177 rejected independent Q20 field-role support", "consequence": "no field role is revived"},
    ]
    write_tsv(COUNTER, counter_rows)

    output_paths = (INVENTORY, FOLDS, MODELS, NULL, COUNTER)
    result = {
        "schema": "GDT340_RESULT_V1", "status": status,
        "stage_a_status": comparator["status"], "recoverable_axes": recoverable,
        "panels": {name: {"records": len(records), "folios": len({r["folio"] for r in records})} for name, records in panels.items()},
        "model_rows": model_rows, "powered_endpoints": len(powered), "lead_endpoints": [{"panel": r["panel"], "axis": r["axis"]} for r in leads],
        "inputs": {str(path.relative_to(ROOT)): sha256_file(path) for path in (METHOD, DESIGN, FREEZE, COMPARATOR, SOURCE, SOURCE_RESULT)},
        "outputs": {str(path.relative_to(ROOT)): sha256_file(path) for path in output_paths},
        "implementation": {
            str(Path(__file__).relative_to(ROOT)): sha256_file(Path(__file__)),
            str(VALIDATOR.relative_to(ROOT)): sha256_file(VALIDATOR),
        },
        "access": {"voynich_tuple_scoring_after_public_comparator_freeze_commit": "b019e33", "f84_opened": False, "f84_parsed": False, "f84_retained": False, "f84_joined": False, "f84_scored": False},
        "claim_ceiling": "Held-folio recovery of comparator-defined complete-record likeness from exact opaque tuples within Recipe/Stars or Pharma only; no tuple or field role, meaning, language, plaintext, translation, or cross-section semantics.",
    }
    result["content_sha256"] = content_hash(result)
    RESULT.write_bytes(canonical_json_bytes(result))

    lines = [
        "# GDT340 report — section-specific complete-record schema recovery", "",
        f"Status: **{status}**.", "",
        "Stage A froze the five-event readable-recipe ontology before target tuple scoring. Only `INTERMEDIATE_STATE` survived held-collection correction, so it is the sole scored Voynich axis. It is a comparator-defined record likeness, not an assigned meaning.", "",
        "## Blind held-folio results", "",
        "| panel | records / folios | positive likeness assignments | tuple coverage | gain over exact size/field baseline | positive folios | exact-null mobile records | max-family p |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in model_rows:
        lines.append(f"| {row['panel']} | {row['records']} / {row['folios']} | {row['positive_assignments']} | {float(row['coverage']):.1%} | {float(row['gain_bits']):+.3f} bits | {row['positive_folios']}/{row['folios']} | {row['mobile_exact_null_records']} | {float(row['max_family_p']):.4f} |")
    lines += [
        "", "## What was learned", "",
        "The readable sources support a compact event ontology qualitatively: homologous recipes retain material, operation, intermediate/result, and application structure despite wording, abbreviation, and layout changes. Quantitatively, anonymous record topology robustly recovers only explicit intermediate-state/time gating across collections.", "",
        "On Voynich, exact tuple bags are asked only whether they recover that frozen whole-record likeness beyond record size and field count on unseen folios. One-sided arrays, uncertain structural assignments, and low-mobility null strata remain observations rather than kill gates; however they limit inferential force. Recipe/Stars and Pharma remain separate throughout.", "",
        "A positive raw gain without powered exact-null mobility is descriptive only. A negative result means this instrument cannot blindly localize the comparator schema; it does not show that Recipe/Pharma lacks procedures or states.", "",
        "No token, PAGE_HOST, field, wrapper, tuple, or position is glossed. No Herbal, Astro, Bio, or q13 semantic model is mixed in. f84 was not accessed.", "",
    ]
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(f"{status} " + " ".join(f"{r['panel']}={float(r['gain_bits']):+.3f}" for r in model_rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
