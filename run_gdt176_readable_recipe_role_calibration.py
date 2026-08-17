#!/usr/bin/env python3
"""Calibrate opaque record-role features on CoReMA, then project them to Q20."""
from __future__ import annotations

import csv
import hashlib
import json
import math
import re
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

NS = {"t": "http://www.tei-c.org/ns/1.0"}
XML_ID = "{http://www.w3.org/XML/1998/namespace}id"
COLLECTIONS = ("b4", "b6", "br1", "bs1", "gr1", "w1")
CLASSES = ("OPENER", "OPERATION", "INGREDIENT", "TOOL", "CLOSER")
ABSTRACT_ROLE = {
    "OPENER": "UNRESOLVED_EDGE_CLASS",
    "OPERATION": "INSTRUCTION_CLAUSE_LIKE",
    "INGREDIENT": "SHORT_ARGUMENT_LIKE",
    "TOOL": "SHORT_ARGUMENT_LIKE",
    "CLOSER": "RECORD_CLOSER_LIKE",
}
MODELS = {
    "POSITION_LENGTH": 4,
    "POSITION_LENGTH_PLUS_OPAQUE_RECURRENCE": 8,
}


def lname(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def words(node: ET.Element) -> list[str]:
    return re.findall(r"[^\W_]+", " ".join(node.itertext()).lower(), flags=re.UNICODE)


def direct_words(node: ET.Element) -> list[str]:
    chunks = [node.text or ""] + [child.tail or "" for child in node]
    return re.findall(r"[^\W_]+", " ".join(chunks).lower(), flags=re.UNICODE)


def opaque(value: str) -> str:
    return hashlib.sha256(("GDT176_OPAQUE_ID_V1\0" + value).encode()).hexdigest()[:20]


def extract_units(collection: str, root: ET.Element) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    for recipe_ordinal, recipe in enumerate(root.findall('.//*[@type="recipe"]', NS), 1):
        recipe_id = recipe.get(XML_ID, f"{collection}.ordinal{recipe_ordinal}")
        units: list[dict[str, object]] = []

        def add(role: str, node: ET.Element) -> None:
            ws = words(node)
            if role in ("INGREDIENT", "TOOL"):
                raw_id = node.get("commodity") or " ".join(ws) or "EMPTY"
            else:
                dw = direct_words(node) or ws
                raw_id = dw[0] if dw else "EMPTY"
            units.append({
                "role": role,
                "identity_hash": opaque(raw_id),
                "span_token_count": max(1, len(ws)),
            })

        def visit(node: ET.Element) -> None:
            tag = lname(node.tag)
            if tag == "title":
                return
            role = {
                "opener": "OPENER",
                "instruction": "OPERATION",
                "ingredient": "INGREDIENT",
                "tool": "TOOL",
                "closer": "CLOSER",
            }.get(tag)
            if role:
                add(role, node)
            if tag in ("ingredient", "tool"):
                return
            for child in node:
                visit(child)

        visit(recipe)
        if not units:
            continue
        for i, unit in enumerate(units, 1):
            unit.update({
                "collection_id": collection,
                "recipe_id": recipe_id,
                "recipe_ordinal": recipe_ordinal,
                "unit_ordinal": i,
                "record_unit_count": len(units),
                "relative_position": i / len(units),
            })
            out.append(unit)
    return out


def recurrence_features(rows: list[dict[str, object]], reference: list[dict[str, object]]) -> np.ndarray:
    counts = Counter(str(r["identity_hash"]) for r in reference)
    docs: dict[str, set[str]] = defaultdict(set)
    neighbors: dict[str, set[str]] = defaultdict(set)
    by_recipe: dict[str, list[dict[str, object]]] = defaultdict(list)
    for r in reference:
        docs[str(r["identity_hash"])].add(str(r["recipe_id"]))
        by_recipe[str(r["recipe_id"])].append(r)
    for rr in by_recipe.values():
        rr.sort(key=lambda x: int(x["unit_ordinal"]))
        for a, b in zip(rr, rr[1:]):
            neighbors[str(a["identity_hash"])].add(str(b["identity_hash"]))
            neighbors[str(b["identity_hash"])].add(str(a["identity_hash"]))
    n_ref = max(1, len(reference))
    n_docs = max(1, len({str(r["recipe_id"]) for r in reference}))
    prior: Counter[tuple[str, str]] = Counter()
    vectors = []
    for r in rows:
        ident = str(r["identity_hash"])
        recipe = str(r["recipe_id"])
        c = counts.get(ident, 0)
        vectors.append([
            float(r["relative_position"]),
            float(r["relative_position"]) ** 2,
            math.log2(1 + int(r["span_token_count"])),
            math.log2(1 + int(r["record_unit_count"])),
            math.log2(1 + c) / math.log2(2 + n_ref),
            len(docs.get(ident, ())) / n_docs,
            len(neighbors.get(ident, ())) / max(1, c),
            math.log2(1 + prior[(recipe, ident)]) / math.log2(2 + int(r["record_unit_count"])),
        ])
        prior[(recipe, ident)] += 1
    return np.asarray(vectors, dtype=float)


def fit_softmax_classifier(X: np.ndarray, y: np.ndarray, width: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    X = X[:, :width]
    mean = X.mean(axis=0)
    scale = X.std(axis=0)
    scale[scale < 1e-9] = 1
    Z = np.column_stack([np.ones(len(X)), (X - mean) / scale])
    Y = np.eye(len(CLASSES))[y]
    beta = np.zeros((Z.shape[1], len(CLASSES)))
    beta[0] = np.log(np.bincount(y, minlength=len(CLASSES)) / len(y) + 1e-12)
    m = np.zeros_like(beta); v = np.zeros_like(beta)
    for step in range(1, 801):
        logits = Z @ beta
        logits -= logits.max(axis=1, keepdims=True)
        p = np.exp(logits); p /= p.sum(axis=1, keepdims=True)
        grad = Z.T @ (p - Y) / len(y)
        grad[1:] += 0.001 * beta[1:]
        m = 0.9 * m + 0.1 * grad
        v = 0.999 * v + 0.001 * grad * grad
        mh = m / (1 - 0.9 ** step); vh = v / (1 - 0.999 ** step)
        beta -= 0.03 * mh / (np.sqrt(vh) + 1e-8)
    return beta, mean, scale


def probabilities(X: np.ndarray, model: tuple[np.ndarray, np.ndarray, np.ndarray], width: int) -> np.ndarray:
    beta, mean, scale = model
    Z = np.column_stack([np.ones(len(X)), np.clip((X[:, :width] - mean) / scale, -4, 4)])
    logits = Z @ beta
    logits -= logits.max(axis=1, keepdims=True)
    p = np.exp(logits)
    return p / p.sum(axis=1, keepdims=True)


def metrics(y: np.ndarray, p: np.ndarray) -> dict[str, float]:
    pred = p.argmax(axis=1)
    f1s = []
    for k in range(len(CLASSES)):
        tp = int(np.sum((pred == k) & (y == k)))
        fp = int(np.sum((pred == k) & (y != k)))
        fn = int(np.sum((pred != k) & (y == k)))
        f1s.append(2 * tp / max(1, 2 * tp + fp + fn))
    return {
        "n": len(y),
        "accuracy": float(np.mean(pred == y)),
        "macro_f1": float(np.mean(f1s)),
        "bits_per_unit": float(-np.log2(np.maximum(p[np.arange(len(y)), y], 1e-12)).mean()),
    }


def write_tsv(path: str, rows: list[dict[str, object]]) -> None:
    with Path(path).open("w", encoding="utf-8", newline="") as h:
        fields = list(rows[0])
        w = csv.DictWriter(h, fields, delimiter="\t", lineterminator="\n")
        w.writeheader(); w.writerows(rows)


def read_tsv(path: str) -> list[dict[str, str]]:
    with Path(path).open(encoding="utf-8", newline="") as h:
        return list(csv.DictReader(h, delimiter="\t"))


def q20_units(edition: str, fields: list[dict[str, str]]) -> list[dict[str, object]]:
    selected = [r for r in fields if r["edition"] == edition]
    assert all(not r["page"].startswith("f84") and not r["locus"].startswith("f84") for r in selected)
    by_record: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for r in selected:
        by_record[(r["page"], r["star_ordinal"])].append(r)
    out: list[dict[str, object]] = []
    for (page, star), rr in sorted(by_record.items()):
        rr.sort(key=lambda r: (int(r["line_depth"]), int(r["field_index"])))
        record_id = f"{edition}|{page}|{star}"
        for ordinal, r in enumerate(rr, 1):
            hosts = [x for x in r["page_hosts"].split("|") if x]
            identity = hosts[0] if hosts else "EMPTY"
            out.append({
                "collection_id": edition,
                "recipe_id": record_id,
                "recipe_ordinal": int(star),
                "unit_ordinal": ordinal,
                "record_unit_count": len(rr),
                "relative_position": ordinal / len(rr),
                "role": "UNKNOWN",
                "identity_hash": opaque(identity),
                "span_token_count": int(r["field_group_count"]),
                "field_id": r["field_id"],
                "page": page,
                "physical_folio": r["physical_folio"],
                "record_scope": r["record_scope"],
                "line_depth": r["line_depth"],
                "field_index": r["field_index"],
            })
    return out


def sha(path: str) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main() -> None:
    all_units: list[dict[str, object]] = []
    for collection in COLLECTIONS:
        root = ET.parse(Path(".gdt176/corema") / f"{collection}.recipes.xml").getroot()
        all_units.extend(extract_units(collection, root))
    assert {str(r["role"]) for r in all_units} == set(CLASSES)
    y_all = np.array([CLASSES.index(str(r["role"])) for r in all_units])

    fold_rows: list[dict[str, object]] = []
    prediction_rows: list[dict[str, object]] = []
    for held in COLLECTIONS:
        train = [r for r in all_units if r["collection_id"] != held]
        test = [r for r in all_units if r["collection_id"] == held]
        X_train = recurrence_features(train, train)
        X_test = recurrence_features(test, train)
        y_train = np.array([CLASSES.index(str(r["role"])) for r in train])
        y_test = np.array([CLASSES.index(str(r["role"])) for r in test])
        prior = np.bincount(y_train, minlength=len(CLASSES)) / len(y_train)
        p_prior = np.tile(prior, (len(test), 1))
        for model_name, width in (("TRAIN_ROLE_PRIOR", 0), *MODELS.items()):
            if width == 0:
                p = p_prior
            else:
                p = probabilities(X_test, fit_softmax_classifier(X_train, y_train, width), width)
            m = metrics(y_test, p)
            fold_rows.append({
                "held_collection": held, "model": model_name, **m,
                "gain_vs_prior_bits": (metrics(y_test, p_prior)["bits_per_unit"] - m["bits_per_unit"]) * len(test),
            })
            if width:
                for unit, truth, pred, probs in zip(test, y_test, p.argmax(axis=1), p):
                    prediction_rows.append({
                        "held_collection": held,
                        "recipe_id": unit["recipe_id"],
                        "unit_ordinal": unit["unit_ordinal"],
                        "model": model_name,
                        "oracle_role": CLASSES[truth],
                        "predicted_role": CLASSES[pred],
                        **{f"p_{role.lower()}": f"{probs[i]:.9f}" for i, role in enumerate(CLASSES)},
                    })

    # Select strictly by held-collection external log loss before inspecting
    # any Q20 aggregate.  The choice is therefore source-calibrated, not tuned
    # to Voynich.
    projection_model_name = min(
        MODELS,
        key=lambda name: sum(float(r["bits_per_unit"]) * int(r["n"]) for r in fold_rows if r["model"] == name),
    )
    projection_width = MODELS[projection_model_name]
    confusion = Counter(
        (r["oracle_role"], r["predicted_role"])
        for r in prediction_rows if r["model"] == projection_model_name
    )
    # Train the externally selected structural model on all external units.
    X_all = recurrence_features(all_units, all_units)
    full_model = fit_softmax_classifier(X_all, y_all, projection_width)
    field_rows = read_tsv("gdt127_q20_field_inventory.tsv")
    projections: list[dict[str, object]] = []
    summary_counts = Counter()
    for edition in ("ZL3b", "IT2a", "RF1b"):
        units = q20_units(edition, field_rows)
        X = recurrence_features(units, units)
        p = probabilities(X, full_model, projection_width)
        for unit, probs in zip(units, p):
            predicted = CLASSES[int(np.argmax(probs))]
            summary_counts[(edition, str(unit["record_scope"]), predicted)] += 1
            projections.append({
                "edition": edition,
                "page": unit["page"],
                "physical_folio": unit["physical_folio"],
                "field_id": unit["field_id"],
                "record_scope": unit["record_scope"],
                "line_depth": unit["line_depth"],
                "field_index": unit["field_index"],
                "predicted_role_like": predicted,
                "supported_abstract_role_like": ABSTRACT_ROLE[predicted],
                **{f"p_{role.lower()}": f"{probs[i]:.9f}" for i, role in enumerate(CLASSES)},
                "claim_state": "EXPLORATORY_CROSS_CORPUS_ROLE_LIKE_PROJECTION",
            })
    summary = [
        {"edition": e, "record_scope": s, "predicted_role_like": r, "field_count": n}
        for (e, s, r), n in sorted(summary_counts.items())
    ]
    abstract_summary_counts = Counter(
        (str(r["edition"]), str(r["record_scope"]), str(r["supported_abstract_role_like"]))
        for r in projections
    )
    abstract_summary = [
        {"edition": e, "record_scope": s, "supported_abstract_role_like": role, "field_count": n}
        for (e, s, role), n in sorted(abstract_summary_counts.items())
    ]
    # Opaque-host atlas: this describes where exact PAGE_HOST IDs occur under
    # the externally calibrated projection.  It does not alter the projection.
    zl_fields = {r["field_id"]: r for r in field_rows if r["edition"] == "ZL3b"}
    host_events: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for r in projections:
        if r["edition"] != "ZL3b":
            continue
        field = zl_fields[str(r["field_id"])]
        hosts = [x for x in field["page_hosts"].split("|") if x]
        if hosts:
            host_events[hosts[0]].append((str(r["predicted_role_like"]), str(r["physical_folio"])))
    host_atlas = []
    for host, events in sorted(host_events.items()):
        counts = Counter(role for role, _ in events)
        abstract_counts = Counter(ABSTRACT_ROLE[role] for role, _ in events)
        dominant, dominant_n = counts.most_common(1)[0]
        dominant_abstract, dominant_abstract_n = abstract_counts.most_common(1)[0]
        n = len(events)
        entropy = -sum((v / n) * math.log2(v / n) for v in counts.values())
        host_atlas.append({
            "page_host": host,
            "event_count": n,
            "physical_folio_count": len({folio for _, folio in events}),
            **{f"{role.lower()}_like_count": counts[role] for role in CLASSES},
            "dominant_role_like": dominant,
            "dominant_purity": f"{dominant_n / n:.9f}",
            "role_entropy_bits": f"{entropy:.9f}",
            "instruction_clause_like_count": abstract_counts["INSTRUCTION_CLAUSE_LIKE"],
            "short_argument_like_count": abstract_counts["SHORT_ARGUMENT_LIKE"],
            "record_closer_like_count": abstract_counts["RECORD_CLOSER_LIKE"],
            "unresolved_edge_class_count": abstract_counts["UNRESOLVED_EDGE_CLASS"],
            "dominant_abstract_role_like": dominant_abstract,
            "dominant_abstract_purity": f"{dominant_abstract_n / n:.9f}",
            "atlas_state": "CROSS_FOLIO_REPEATED" if len({folio for _, folio in events}) >= 3 and n >= 5 else "DESCRIPTIVE_LOW_CAPACITY",
        })

    unit_export = [{
        "collection_id": r["collection_id"], "recipe_id": r["recipe_id"],
        "unit_ordinal": r["unit_ordinal"], "record_unit_count": r["record_unit_count"],
        "relative_position": f"{float(r['relative_position']):.9f}",
        "span_token_count": r["span_token_count"], "identity_hash": r["identity_hash"],
        "oracle_role": r["role"],
    } for r in all_units]
    confusion_rows = [
        {"oracle_role": a, "predicted_role": b, "count": confusion[(a, b)]}
        for a in CLASSES for b in CLASSES
    ]
    for path, data in (
        ("gdt176_external_role_units.tsv", unit_export),
        ("gdt176_external_role_folds.tsv", fold_rows),
        ("gdt176_external_role_predictions.tsv", prediction_rows),
        ("gdt176_external_role_confusion.tsv", confusion_rows),
        ("gdt176_q20_role_like_projection.tsv", projections),
        ("gdt176_q20_role_like_summary.tsv", summary),
        ("gdt176_q20_abstract_role_summary.tsv", abstract_summary),
        ("gdt176_q20_opaque_host_role_atlas.tsv", host_atlas),
    ):
        write_tsv(path, data)

    agg: dict[str, dict[str, float]] = {}
    for model_name in ("TRAIN_ROLE_PRIOR", *MODELS):
        rr = [r for r in fold_rows if r["model"] == model_name]
        n = sum(int(r["n"]) for r in rr)
        agg[model_name] = {
            "n": n,
            "accuracy": sum(float(r["accuracy"]) * int(r["n"]) for r in rr) / n,
            "macro_f1_fold_mean": sum(float(r["macro_f1"]) for r in rr) / len(rr),
            "bits_per_unit": sum(float(r["bits_per_unit"]) * int(r["n"]) for r in rr) / n,
            "gain_vs_prior_bits": sum(float(r["gain_vs_prior_bits"]) for r in rr),
            "positive_folds_vs_prior": sum(float(r["gain_vs_prior_bits"]) > 0 for r in rr),
        }
    selected_class_metrics = {}
    for role in CLASSES:
        rr = [r for r in prediction_rows if r["model"] == projection_model_name]
        tp = sum(r["oracle_role"] == role and r["predicted_role"] == role for r in rr)
        truth = sum(r["oracle_role"] == role for r in rr)
        predicted = sum(r["predicted_role"] == role for r in rr)
        selected_class_metrics[role] = {
            "support": truth,
            "recall": tp / truth if truth else 0,
            "precision": tp / predicted if predicted else 0,
        }
    projected_by_key: dict[str, dict[str, str]] = defaultdict(dict)
    for r in projections:
        field_key = str(r["field_id"]).split("|", 1)[-1]
        projected_by_key[field_key][str(r["edition"])] = str(r["predicted_role_like"])
    all_three = [v for v in projected_by_key.values() if len(v) == 3]
    stable_three = sum(len(set(v.values())) == 1 for v in all_three)
    zl_projection = {str(r["field_id"]): str(r["predicted_role_like"]) for r in projections if r["edition"] == "ZL3b"}
    zl_records: dict[tuple[str, str], list[tuple[int, int, str]]] = defaultdict(list)
    for field_id, field in zl_fields.items():
        zl_records[(field["page"], field["star_ordinal"])].append(
            (int(field["line_depth"]), int(field["field_index"]), zl_projection[field_id])
        )
    for rr in zl_records.values():
        rr.sort()
    first_role_counts = Counter(rr[0][2] for rr in zl_records.values())
    last_role_counts = Counter(rr[-1][2] for rr in zl_records.values())
    result = {
        "experiment": "GDT176_READABLE_RECIPE_ROLE_CALIBRATION",
        "status": "PARTIAL_EXTERNAL_ROLE_INSTRUMENT_SUPPORTED_Q20_SCHEMA_EXPLORATORY",
        "external_units": len(all_units),
        "external_recipes": len({(r["collection_id"], r["recipe_id"]) for r in all_units}),
        "held_collection_results": agg,
        "projection_model_selected_on_external_folds_only": projection_model_name,
        "selected_model_class_metrics": selected_class_metrics,
        "q20_projected_fields": len(projections),
        "q20_editions": ["ZL3b", "IT2a", "RF1b"],
        "q20_editions_are_alternate_readings": True,
        "q20_all_three_comparable_field_keys": len(all_three),
        "q20_all_three_top_role_stable_keys": stable_three,
        "q20_zl_record_count": len(zl_records),
        "q20_zl_first_field_role_like_counts": dict(sorted(first_role_counts.items())),
        "q20_zl_final_field_role_like_counts": dict(sorted(last_role_counts.items())),
        "projection_is_role_like_not_semantic_confirmation": True,
        "f84r_accessed": False,
        "inputs": {p: sha(p) for p in ("gdt176_source_freeze.json", "gdt127_q20_field_inventory.tsv")},
        "documents": {p: sha(p) for p in (
            "GDT176_READABLE_RECIPE_ROLE_CALIBRATION_METHOD.md",
            "GDT176_READABLE_RECIPE_SOURCE_AUDIT.md",
        )},
        "implementation": {"run_gdt176_readable_recipe_role_calibration.py": sha("run_gdt176_readable_recipe_role_calibration.py")},
        "outputs": {p: sha(p) for p in (
            "gdt176_external_role_units.tsv", "gdt176_external_role_folds.tsv",
            "gdt176_external_role_predictions.tsv",
            "gdt176_external_role_confusion.tsv", "gdt176_q20_role_like_projection.tsv",
            "gdt176_q20_role_like_summary.tsv", "gdt176_q20_abstract_role_summary.tsv",
            "gdt176_q20_opaque_host_role_atlas.tsv",
        )},
        "claim_ceiling": "transferable cross-corpus record-role likeness only; no Voynich word meaning, language, plaintext, or translation",
    }
    payload = json.dumps(result, sort_keys=True, separators=(",", ":")).encode()
    result["content_hash"] = hashlib.sha256(payload).hexdigest()
    Path("gdt176_result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(agg, indent=2, sort_keys=True))
    print("q20 projections", len(projections))


if __name__ == "__main__":
    main()
