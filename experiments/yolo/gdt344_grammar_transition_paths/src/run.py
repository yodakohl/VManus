#!/usr/bin/env python3
"""GDT344: held-folio grammar paths and gated recipe-event calibration."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import random
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np


def find_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("repository root not found")


ROOT = find_root(Path(__file__).resolve())
import sys
sys.path.insert(0, str(ROOT))
from tools.vmanus_experiment import GuardedTSV  # noqa: E402

EXP = ROOT / "experiments/yolo/gdt344_grammar_transition_paths"
ART = EXP / "artifacts"
DESIGN = ART / "gdt344_design.json"
METHOD = EXP / "METHOD.md"
SOURCE_AUDIT = EXP / "SOURCE_AUDIT.md"
NATIVE = ROOT / "gdt278_native_event_inventory.tsv"
INTER = ROOT / "gdt327_joint_tuple_interlinear.tsv"
GDT336_FOLDS = ROOT / "gdt336_folds.tsv"
TARGET_RECORDS = ROOT / "experiments/yolo/gdt340_recipe_pharma_section_semantic_schema/artifacts/gdt340_voynich_record_inventory.tsv"
ORACLE = ROOT / "gdt176_corema_role_oracle.tsv"
COREMA_MANIFEST = ROOT / "gdt176_corema_collection_manifest.tsv"
COREMA_FREEZE = ROOT / "gdt176_source_freeze.json"

TRANSITIONS = ART / "gdt344_transition_inventory.tsv"
PATH_ATLAS = ART / "gdt344_path_atlas.tsv"
FORMAL_FOLDS = ART / "gdt344_formal_folds.tsv"
FORMAL_MODELS = ART / "gdt344_formal_models.tsv"
FORMAL_NULL = ART / "gdt344_formal_null.tsv"
COMPARATOR_FOLDS = ART / "gdt344_comparator_folds.tsv"
COMPARATOR_MODELS = ART / "gdt344_comparator_models.tsv"
COMPARATOR_NULL = ART / "gdt344_comparator_null.tsv"
TARGET_FOLDS = ART / "gdt344_target_folds.tsv"
COUNTEREXAMPLES = ART / "gdt344_counterexamples.tsv"
RESULT = ART / "gdt344_result.json"
REPORT = EXP / "REPORT.md"
COMPARATOR_REPORT = EXP / "COMPARATOR_REPORT.md"

COORD_COLUMNS = ("local_frame", "inner_d", "right_family", "dy_closure", "b3")
FORMAL_MODELS_LIST = ("PLACEMENT", "EXACT_PREDECESSOR", "PATH_SHAPE", "PATH_VALUE")
ALPHAS = (8, 32, 128, 512)
CLASSES = ("BASIC_MO", "MO_STATE_ONLY", "MO_APPLICATION_ONLY", "MO_RESULT_ONLY", "MO_MULTI_OPTIONAL")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str] | None = None) -> None:
    if fields is None:
        if not rows:
            raise ValueError(f"fields required for empty TSV {path}")
        fields = list(rows[0])
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()


def content_hash(document: dict[str, object]) -> str:
    copy = dict(document)
    copy.pop("content_sha256", None)
    return hashlib.sha256(canonical(copy)).hexdigest()


def hid(domain: str, value: object, length: int = 20) -> str:
    return hashlib.sha256((domain + "\0" + json.dumps(value, sort_keys=True, separators=(",", ":"))).encode()).hexdigest()[:length]


def bucket(value: int) -> str:
    if value <= 2:
        return str(value)
    if value <= 4:
        return "3-4"
    if value <= 8:
        return "5-8"
    if value <= 16:
        return "9-16"
    return "17+"


def panel_pages() -> tuple[dict[str, str], set[str]]:
    rows = read_tsv(TARGET_RECORDS)
    mapping: dict[str, str] = {}
    for row in rows:
        if row["page"] == "page":
            continue
        prior = mapping.setdefault(row["page"], row["panel"])
        if prior != row["panel"]:
            raise AssertionError("page occurs in two panels")
    return mapping, set(mapping)


def guarded_rows(path: Path, pages: set[str]) -> tuple[list[dict[str, str]], object]:
    reader = GuardedTSV(path, selector_column="page", allowed_values=pages, forbidden_prefixes=("f84",), forbidden_action="error")
    rows = list(reader)
    if any(row["page"].startswith("f84") for row in rows):
        raise AssertionError("f84 retained")
    return rows, reader.stats


def renderer_state(row: dict[str, str]) -> str:
    if row["wrapper"] == "s" and row["line_first"] == "1":
        return "SUPPORTED_RENDERER_NUISANCE"
    if row["wrapper"] == "q" and row["prev_dy"] == "1":
        return "SUPPORTED_RENDERER_NUISANCE"
    return row["wrapper"]


def nominal_change(left: str, right: str, none: str = "NONE") -> str:
    left_none = left in {none, "0", ""}
    right_none = right in {none, "0", ""}
    if left_none and right_none:
        return "STAY_NONE"
    if left == right:
        return "STAY_VALUE"
    if left_none:
        return "ADD"
    if right_none:
        return "DROP"
    return "SWITCH"


def boundary(a: dict[str, str], b: dict[str, str]) -> tuple[str, str, int, int, int]:
    record_reset = int(a["record_ordinal"] != b["record_ordinal"])
    line_reset = int(a["locus"] != b["locus"])
    field_reset = int((a["record_ordinal"], a["field_ordinal"]) != (b["record_ordinal"], b["field_ordinal"]))
    if record_reset:
        scope = "RECORD_RESET"
        order = "RECORD_RESET"
    elif line_reset:
        scope = "LINE_RESET"
        delta = int(b["field_ordinal"]) - int(a["field_ordinal"])
        order = "SAME_FIELD" if not field_reset else ("NEXT_FIELD" if delta == 1 else ("FIELD_RESET" if delta < 1 else "FIELD_SKIP"))
    elif field_reset:
        scope = "FIELD_BOUNDARY"
        delta = int(b["field_ordinal"]) - int(a["field_ordinal"])
        order = "NEXT_FIELD" if delta == 1 else ("FIELD_RESET" if delta < 1 else "FIELD_SKIP")
    else:
        scope = "SAME_FIELD"
        order = "SAME_FIELD"
    return scope, order, field_reset, record_reset, line_reset


def placement(row: dict[str, str]) -> tuple[str, ...]:
    quartile = str(min(3, 4 * (int(row["group_index"]) - 1) // max(1, int(row["group_count"]))))
    return (row["line_first"], row["within_field_position"], quartile)


def make_edges() -> tuple[list[dict[str, object]], dict[str, object]]:
    page_panel, pages = panel_pages()
    native, native_stats = guarded_rows(NATIVE, pages)
    inter, inter_stats = guarded_rows(INTER, pages)
    native_key = {(row["page"], row["locus"], row["group_index"]): row for row in native}
    inter_keys = {(row["page"], row["locus"], row["group_index"]) for row in inter}
    if len(native_key) != len(native) or set(native_key) != inter_keys:
        raise AssertionError("native/interlinear join mismatch")
    by_page: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in inter:
        key = (row["page"], row["locus"], row["group_index"])
        by_page[row["page"]].append({**native_key[key], **row})
    edges: list[dict[str, object]] = []
    for page, values in by_page.items():
        for ordinal, (a, b) in enumerate(zip(values, values[1:]), 1):
            scope, field_order, field_boundary, record_boundary, line_reset = boundary(a, b)
            value_parts = tuple(f"{a[name]}>{b[name]}" for name in COORD_COLUMNS)
            shape_parts = tuple(nominal_change(a[name], b[name]) for name in COORD_COLUMNS)
            wrap_value = f"{renderer_state(a)}>{renderer_state(b)}"
            wrap_shape = nominal_change(renderer_state(a), renderer_state(b), "NONE")
            structural = (field_order, str(field_boundary), str(record_boundary), str(line_reset), scope)
            value_signature = (*value_parts, wrap_value, *structural)
            shape_signature = (*shape_parts, wrap_shape, *structural)
            target_place = placement(b)
            base_context = (page_panel[page], *target_place, scope, renderer_state(b), b["known_label_renderer"])
            source_shape = (
                "FRAME_PRESENT" if a["local_frame"] != "NONE" else "FRAME_NONE",
                a["inner_d"],
                "RIGHT_PRESENT" if a["right_family"] != "NONE" else "RIGHT_NONE",
                a["dy_closure"], a["b3"], renderer_state(a), field_order,
            )
            value_context = (a["coordinate_id"], renderer_state(a), field_order)
            exact_context = (a["joint_tuple_id"], field_order)
            edges.append({
                "edge_id": hid("GDT344_EDGE_V1", (page, ordinal, a["locus"], a["group_index"], b["locus"], b["group_index"])),
                "panel": page_panel[page], "page": page, "physical_folio": a["physical_folio"],
                "source_record": a["record_ordinal"], "target_record": b["record_ordinal"],
                "source_locus": a["locus"], "target_locus": b["locus"],
                "source_tuple": a["joint_tuple_id"], "target_tuple": b["joint_tuple_id"],
                "source_coordinate": a["coordinate_id"], "target_coordinate": b["coordinate_id"],
                "base_context": base_context, "exact_context": exact_context,
                "shape_context": source_shape, "value_context": value_context,
                "target_placement": target_place, "scope": scope, "field_order": field_order,
                "field_boundary": field_boundary, "record_boundary": record_boundary, "line_reset": line_reset,
                "source_renderer": renderer_state(a), "target_renderer": renderer_state(b),
                "value_signature": value_signature, "shape_signature": shape_signature,
                "value_path_id": hid("GDT344_VALUE_PATH_V1", value_signature),
                "shape_path_id": hid("GDT344_SHAPE_PATH_V1", shape_signature),
            })
    stats = {
        "native": native_stats.__dict__, "interlinear": inter_stats.__dict__, "groups": len(inter),
        "folios": len({row["physical_folio"] for row in inter}),
        "records": len({(row["page"], row["record_ordinal"]) for row in inter}),
        "fields": len({(row["page"], row["record_ordinal"], row["field_ordinal"]) for row in inter}),
        "lines": len({row["locus"] for row in inter}), "edges": len(edges),
    }
    return edges, stats


def atlas(edges: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for resolution, key in (("SHAPE", "shape_path_id"), ("VALUE", "value_path_id")):
        groups: dict[str, list[dict[str, object]]] = defaultdict(list)
        for edge in edges:
            groups[str(edge[key])].append(edge)
        for path_id, values in groups.items():
            signature = values[0]["shape_signature" if resolution == "SHAPE" else "value_signature"]
            pairs = {(x["source_tuple"], x["target_tuple"]) for x in values}
            folios = {x["physical_folio"] for x in values}
            rows.append({
                "resolution": resolution, "path_id": path_id,
                "signature_json": json.dumps(signature, separators=(",", ":")),
                "events": len(values), "folios": len(folios),
                "records": len({(x["page"], x["source_record"]) for x in values}),
                "exact_tuple_pairs": len(pairs), "panels": "|".join(sorted({str(x["panel"]) for x in values})),
                "cross_folio": int(len(folios) >= 2), "cross_pair": int(len(pairs) >= 2),
                "eligible_abstract_path": int(len(folios) >= 2 and len(pairs) >= 2),
                "semantic_state": "UNASSIGNED",
            })
    return sorted(rows, key=lambda row: (str(row["resolution"]), -int(row["events"]), str(row["path_id"])))


def count_tables(train: list[dict[str, object]], model: str):
    global_counts: Counter[str] = Counter(str(edge["target_coordinate"]) for edge in train)
    base: dict[tuple, Counter[str]] = defaultdict(Counter)
    context: dict[tuple, Counter[str]] = defaultdict(Counter)
    for edge in train:
        y = str(edge["target_coordinate"])
        b = tuple(edge["base_context"])
        base[b][y] += 1
        if model == "EXACT_PREDECESSOR":
            c = (b, tuple(edge["exact_context"]))
        elif model == "PATH_SHAPE":
            c = (b, tuple(edge["shape_context"]))
        elif model == "PATH_VALUE":
            c = (b, tuple(edge["value_context"]))
        else:
            c = (b,)
        context[c][y] += 1
    return global_counts, base, context


def coord_distribution(edge: dict[str, object], tables, model: str, alpha: float, candidates: tuple[str, ...]) -> dict[str, float]:
    global_counts, base, context = tables
    k = len(candidates)
    gn = sum(global_counts.values())
    bkey = tuple(edge["base_context"])
    bc = base.get(bkey, Counter())
    bn = sum(bc.values())
    base_prob = {y: (bc[y] + 32.0 * (global_counts[y] + 0.5) / (gn + 0.5 * k)) / (bn + 32.0) for y in candidates}
    if model == "PLACEMENT":
        return base_prob
    if model == "EXACT_PREDECESSOR":
        ckey = (bkey, tuple(edge["exact_context"]))
    elif model == "PATH_SHAPE":
        ckey = (bkey, tuple(edge["shape_context"]))
    elif model == "PATH_VALUE":
        ckey = (bkey, tuple(edge["value_context"]))
    else:
        raise ValueError(model)
    cc = context.get(ckey, Counter())
    cn = sum(cc.values())
    return {y: (cc[y] + alpha * base_prob[y]) / (cn + alpha) for y in candidates}


def select_alpha(edges: list[dict[str, object]], outer_hold: str, panel: str, model: str) -> int:
    if model == "PLACEMENT":
        return 0
    folios = sorted({str(edge["physical_folio"]) for edge in edges if edge["panel"] == panel and edge["physical_folio"] != outer_hold})
    totals = {alpha: 0.0 for alpha in ALPHAS}
    for inner in folios:
        train = [edge for edge in edges if edge["panel"] == panel and edge["physical_folio"] not in {outer_hold, inner}]
        test = [edge for edge in edges if edge["panel"] == panel and edge["physical_folio"] == inner]
        candidates = tuple(sorted({str(edge["target_coordinate"]) for edge in train}))
        if not candidates:
            continue
        tables = count_tables(train, model)
        for edge in test:
            y = str(edge["target_coordinate"])
            if y not in candidates:
                continue
            for alpha in ALPHAS:
                totals[alpha] -= math.log2(max(1e-300, coord_distribution(edge, tables, model, alpha, candidates)[y]))
    return min(ALPHAS, key=lambda alpha: (totals[alpha], alpha))


def tuple_probability(edge: dict[str, object], train: list[dict[str, object]], alpha: float) -> float | None:
    coordinate = str(edge["target_coordinate"])
    target = str(edge["target_tuple"])
    candidates = sorted({str(row["target_tuple"]) for row in train if row["target_coordinate"] == coordinate})
    if target not in candidates:
        return None
    base = Counter(str(row["target_tuple"]) for row in train if row["target_coordinate"] == coordinate)
    placed = Counter(str(row["target_tuple"]) for row in train if row["target_coordinate"] == coordinate and row["target_placement"] == edge["target_placement"])
    bn, pn, k = sum(base.values()), sum(placed.values()), len(candidates)
    pbase = (base[target] + 0.5) / (bn + 0.5 * k)
    return (placed[target] + alpha * pbase) / (pn + alpha)


def run_formal(edges: list[dict[str, object]], design: dict[str, object]):
    gdt336 = {(row["register"], row["held_folio"]): float(row["selected_alpha"]) for row in read_tsv(GDT336_FOLDS)}
    fold_rows: list[dict[str, object]] = []
    event_predictions: list[dict[str, object]] = []
    for panel in design["panels"]:
        panel_edges = [edge for edge in edges if edge["panel"] == panel]
        for hold in sorted({str(edge["physical_folio"]) for edge in panel_edges}):
            train = [edge for edge in panel_edges if edge["physical_folio"] != hold]
            test = [edge for edge in panel_edges if edge["physical_folio"] == hold]
            candidates = tuple(sorted({str(edge["target_coordinate"]) for edge in train}))
            alphas = {model: select_alpha(edges, hold, panel, model) for model in FORMAL_MODELS_LIST}
            tables = {model: count_tables(train, model) for model in FORMAL_MODELS_LIST}
            register = str(test[0]["panel"] == "RECIPE_STARS_S" and "STARS_RECIPE_B" or "OTHER_A")
            tuple_alpha = gdt336[(register, hold)]
            train_pairs = {(str(edge["source_tuple"]), str(edge["target_tuple"])) for edge in train}
            per_model = {model: {"bits": 0.0, "coord": 0.0, "tuple": 0.0, "n": 0, "unseen_bits": 0.0, "unseen_n": 0,
                                 "within_bits": 0.0, "within_n": 0, "field_bits": 0.0, "field_n": 0, "reset_bits": 0.0, "reset_n": 0}
                         for model in FORMAL_MODELS_LIST}
            for edge in test:
                y = str(edge["target_coordinate"])
                if y not in candidates:
                    continue
                pt = tuple_probability(edge, train, tuple_alpha)
                if pt is None:
                    continue
                tuple_bits = -math.log2(max(1e-300, pt))
                predictions: dict[str, dict[str, float]] = {}
                for model in FORMAL_MODELS_LIST:
                    predictions[model] = coord_distribution(edge, tables[model], model, alphas[model], candidates)
                    coord_bits = -math.log2(max(1e-300, predictions[model][y]))
                    total_bits = coord_bits + tuple_bits
                    z = per_model[model]
                    z["bits"] += total_bits; z["coord"] += coord_bits; z["tuple"] += tuple_bits; z["n"] += 1
                    unseen = (str(edge["source_tuple"]), str(edge["target_tuple"])) not in train_pairs
                    if unseen: z["unseen_bits"] += total_bits; z["unseen_n"] += 1
                    if not int(edge["record_boundary"]): z["within_bits"] += total_bits; z["within_n"] += 1
                    if int(edge["field_boundary"]): z["field_bits"] += total_bits; z["field_n"] += 1
                    if int(edge["record_boundary"]): z["reset_bits"] += total_bits; z["reset_n"] += 1
                event_predictions.append({
                    "edge": edge, "panel": panel, "hold": hold, "y": y, "candidates": candidates,
                    "probs": predictions, "tuple_bits": tuple_bits,
                })
            for model in FORMAL_MODELS_LIST:
                z = per_model[model]
                fold_rows.append({
                    "panel": panel, "held_folio": hold, "model": model, "selected_alpha": alphas[model],
                    "scored_edges": z["n"], "total_bits": f"{z['bits']:.9f}", "coordinate_bits": f"{z['coord']:.9f}",
                    "gdt336_tuple_bits": f"{z['tuple']:.9f}", "within_record_edges": z["within_n"], "within_record_bits": f"{z['within_bits']:.9f}",
                    "field_boundary_edges": z["field_n"], "field_boundary_bits": f"{z['field_bits']:.9f}",
                    "record_reset_edges": z["reset_n"], "record_reset_bits": f"{z['reset_bits']:.9f}",
                    "unseen_exact_pair_edges": z["unseen_n"], "unseen_exact_pair_bits": f"{z['unseen_bits']:.9f}",
                })
    model_rows: list[dict[str, object]] = []
    aggregates: dict[str, dict[str, float]] = {}
    for model in FORMAL_MODELS_LIST:
        rows = [row for row in fold_rows if row["model"] == model]
        agg = {
            "edges": sum(int(row["scored_edges"]) for row in rows),
            "bits": sum(float(row["total_bits"]) for row in rows),
            "coord": sum(float(row["coordinate_bits"]) for row in rows),
            "tuple": sum(float(row["gdt336_tuple_bits"]) for row in rows),
            "unseen_n": sum(int(row["unseen_exact_pair_edges"]) for row in rows),
            "unseen_bits": sum(float(row["unseen_exact_pair_bits"]) for row in rows),
        }
        aggregates[model] = agg
        exact_rows = { (row["panel"], row["held_folio"]): row for row in fold_rows if row["model"] == "EXACT_PREDECESSOR" }
        placement_rows = { (row["panel"], row["held_folio"]): row for row in fold_rows if row["model"] == "PLACEMENT" }
        positive_exact = sum(float(exact_rows[(row["panel"], row["held_folio"])]["total_bits"]) > float(row["total_bits"]) for row in rows) if model.startswith("PATH") else 0
        positive_by_panel = {}
        for panel in design["panels"]:
            selected = [row for row in rows if row["panel"] == panel]
            positive_by_panel[panel] = sum(float(exact_rows[(row["panel"], row["held_folio"])]["total_bits"]) > float(row["total_bits"]) for row in selected) if model.startswith("PATH") else 0
        model_rows.append({
            "model": model, "scored_edges": agg["edges"], "total_bits": f"{agg['bits']:.9f}", "coordinate_bits": f"{agg['coord']:.9f}",
            "gdt336_tuple_bits": f"{agg['tuple']:.9f}",
            "gain_over_placement": f"{aggregates.get('PLACEMENT', agg)['bits'] - agg['bits']:.9f}" if model != "PLACEMENT" else "0.000000000",
            "gain_over_exact_predecessor": f"{aggregates.get('EXACT_PREDECESSOR', agg)['bits'] - agg['bits']:.9f}" if model.startswith("PATH") else "NA",
            "positive_folios_vs_exact": positive_exact if model.startswith("PATH") else "NA",
            "positive_recipe_folios_vs_exact": positive_by_panel.get("RECIPE_STARS_S", 0) if model.startswith("PATH") else "NA",
            "positive_pharma_folios_vs_exact": positive_by_panel.get("PHARMA_P", 0) if model.startswith("PATH") else "NA",
            "unseen_exact_pair_edges": agg["unseen_n"], "unseen_exact_pair_bits": f"{agg['unseen_bits']:.9f}",
            "unseen_gain_over_placement": f"{aggregates.get('PLACEMENT', agg)['unseen_bits'] - agg['unseen_bits']:.9f}" if model != "PLACEMENT" else "0.000000000",
            "inclusive_p": "NA",
        })

    # Fixed-prediction alignment null. Candidate probabilities are already
    # outer-held predictions; only target labels move within opportunity strata.
    observed = {}
    for model in ("PATH_SHAPE", "PATH_VALUE"):
        observed[model] = sum(math.log2(max(1e-300, event["probs"][model][event["y"]])) - math.log2(max(1e-300, event["probs"]["EXACT_PREDECESSOR"][event["y"]])) for event in event_predictions)
    groups: dict[tuple, list[int]] = defaultdict(list)
    for index, event in enumerate(event_predictions):
        edge = event["edge"]
        groups[(event["panel"], event["hold"], edge["scope"], tuple(edge["target_placement"]), edge["target_renderer"])].append(index)
    null_rows = []
    exceed = {model: 0 for model in observed}
    exceed_max = 0
    observed_max = max(observed.values())
    for world in range(int(design["formal_null"]["worlds"])):
        rng = random.Random(int(design["formal_null"]["seed"]) + world)
        permuted = [event["y"] for event in event_predictions]
        for indices in groups.values():
            labels = [permuted[index] for index in indices]
            rng.shuffle(labels)
            for index, label in zip(indices, labels):
                permuted[index] = label
        gains = {}
        for model in observed:
            gain = 0.0
            for index, event in enumerate(event_predictions):
                y = permuted[index]
                gain += math.log2(max(1e-300, event["probs"][model].get(y, 1e-300))) - math.log2(max(1e-300, event["probs"]["EXACT_PREDECESSOR"].get(y, 1e-300)))
            gains[model] = gain
            exceed[model] += int(gain >= observed[model] - 1e-12)
        maximum = max(gains.values())
        exceed_max += int(maximum >= observed_max - 1e-12)
        null_rows.append({"world": world, "path_shape_gain_over_exact": f"{gains['PATH_SHAPE']:.9f}", "path_value_gain_over_exact": f"{gains['PATH_VALUE']:.9f}", "max_two_gain": f"{maximum:.9f}"})
    pmax = (1 + exceed_max) / (1 + len(null_rows))
    for row in model_rows:
        if row["model"] in observed:
            row["inclusive_p"] = f"{(1 + exceed[row['model']]) / (1 + len(null_rows)):.9f}"
            row["max_two_p"] = f"{pmax:.9f}"
        else:
            row["max_two_p"] = "NA"
    exact = aggregates["EXACT_PREDECESSOR"]
    placement_agg = aggregates["PLACEMENT"]
    supported_models = []
    fold_lookup = {(row["panel"], row["held_folio"], row["model"]): row for row in fold_rows}
    panel_folios = {panel: sorted({str(edge["physical_folio"]) for edge in edges if edge["panel"] == panel}) for panel in design["panels"]}
    for model in ("PATH_SHAPE", "PATH_VALUE"):
        agg = aggregates[model]
        panel_ok = all(
            sum(float(fold_lookup[(panel, folio, "EXACT_PREDECESSOR")]["total_bits"]) > float(fold_lookup[(panel, folio, model)]["total_bits"]) for folio in folios)
            >= math.ceil(float(design["formal_gate"]["positive_folio_fraction_each_panel"]) * len(folios))
            for panel, folios in panel_folios.items()
        )
        if agg["bits"] < placement_agg["bits"] and agg["bits"] < exact["bits"] and panel_ok and agg["unseen_bits"] < placement_agg["unseen_bits"] and pmax <= float(design["formal_gate"]["inclusive_p_max"]):
            supported_models.append(model)
    status = "ABSTRACT_GRAMMAR_TRANSITION_PATHS_SUPPORTED" if supported_models else "NO_TRANSFERABLE_GRAMMAR_TRANSITION_PATH"
    return fold_rows, model_rows, null_rows, status, supported_models, event_predictions


def build_fields(rows: list[dict[str, str]], identity_key: str, namespace: str) -> list[list[str]]:
    instruction = 0
    field_rows: dict[str, list[tuple[int, str]]] = defaultdict(list)
    field_first: dict[str, int] = {}
    for row in sorted(rows, key=lambda item: int(item["element_ordinal"])):
        if row["role"] == "TITLE":
            continue
        ordinal = int(row["element_ordinal"])
        parent = int(row["parent_instruction_ordinal"])
        if row["role"] == "INSTRUCTION":
            instruction += 1; field = f"I{instruction}"
        elif parent:
            field = f"I{parent}"
        else:
            field = f"E{ordinal}"
        value = row[identity_key]
        identity = hid("GDT344_GLOBAL_CONCEPT_V1", value) if value != "NONE" else hid("GDT344_LOCAL_SINGLETON_V1", (namespace, ordinal))
        field_rows[field].append((ordinal, identity))
        field_first[field] = min(field_first.get(field, ordinal), ordinal)
    return [[identity for _, identity in sorted(field_rows[field])] for field in sorted(field_rows, key=lambda field: (field_first[field], field))]


def record_features(fields: list[list[str]]) -> tuple[list[float], list[float]]:
    sizes = np.array([len(field) for field in fields], dtype=float)
    units = int(sizes.sum())
    nfields = len(fields)
    if not nfields:
        return [0.0] * 10, [0.0] * 10
    diffs = np.diff(sizes) if nfields > 1 else np.array([], dtype=float)
    shape = [
        math.log1p(units), math.log1p(nfields), float(sizes.mean()), float(sizes.std()), float(sizes.max()),
        float(np.mean(sizes == 1)), float(sizes[0]), float(sizes[-1]),
        float(np.mean(diffs > 0)) if len(diffs) else 0.0, float(np.mean(diffs < 0)) if len(diffs) else 0.0,
    ]
    counts = Counter(identity for field in fields for identity in field)
    positions: dict[str, list[int]] = defaultdict(list)
    for index, field in enumerate(fields):
        for identity in set(field): positions[identity].append(index)
    distinct = max(1, len(counts))
    repeated = sum(value >= 2 for value in counts.values()) / distinct
    cross = sum(len(value) >= 2 for value in positions.values()) / distinct
    overlaps = []
    retention = 0
    merges = 0
    for index in range(1, nfields):
        left, right = set(fields[index - 1]), set(fields[index])
        overlaps.append(len(left & right) / max(1, len(left | right)))
        retention += len(left & right)
        seen = set().union(*(set(field) for field in fields[:index]))
        merges += int(len(right & seen) >= 2)
    returning = sum(any(b - a > 1 for a, b in zip(pos, pos[1:])) for pos in positions.values()) / distinct
    future_reuse = sum(len(pos) >= 3 for pos in positions.values()) / distinct
    last_seen = len(set(fields[-1]) & set().union(*(set(field) for field in fields[:-1]))) / max(1, len(set(fields[-1]))) if nfields > 1 else 0.0
    change = float(np.mean([1.0 - value for value in overlaps])) if overlaps else 0.0
    flow = [
        len(counts) / max(1, units), repeated, cross, float(np.mean(overlaps)) if overlaps else 0.0,
        retention / max(1, units), returning, merges / max(1, nfields - 1), future_reuse, last_seen, change,
    ]
    return shape, flow


def event_class(rows: list[dict[str, str]]) -> str | None:
    roles = {row["role"] for row in rows}
    if not roles & {"INGREDIENT", "DISH"} or "INSTRUCTION" not in roles:
        return None
    state = bool(roles & {"TIME"})
    application = bool(roles & {"SERVINGTIP", "HOUSEHOLDTIP"})
    result = bool(roles & {"CLOSER", "DIETETICS"})
    total = state + application + result
    if total == 0: return "BASIC_MO"
    if total >= 2: return "MO_MULTI_OPTIONAL"
    if state: return "MO_STATE_ONLY"
    if application: return "MO_APPLICATION_ONLY"
    return "MO_RESULT_ONLY"


def fit_multinomial(x: np.ndarray, y: np.ndarray, classes: int, ridge: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    mean = x.mean(axis=0)
    scale = x.std(axis=0)
    scale[scale < 1e-8] = 1.0
    z = np.column_stack([np.ones(len(x)), (x - mean) / scale])
    weights = np.zeros((z.shape[1], classes), dtype=float)
    onehot = np.eye(classes)[y]
    for step in range(1800):
        logits = z @ weights
        logits -= logits.max(axis=1, keepdims=True)
        probs = np.exp(logits); probs /= probs.sum(axis=1, keepdims=True)
        gradient = z.T @ (probs - onehot) / len(z)
        gradient[1:] += (ridge / len(z)) * weights[1:]
        learning = 0.35 / math.sqrt(1.0 + step / 200.0)
        weights -= learning * gradient
    return weights, mean, scale


def predict_multinomial(x: np.ndarray, fit) -> np.ndarray:
    weights, mean, scale = fit
    z = np.column_stack([np.ones(len(x)), (x - mean) / scale])
    logits = z @ weights; logits -= logits.max(axis=1, keepdims=True)
    probs = np.exp(logits); probs /= probs.sum(axis=1, keepdims=True)
    return probs


def run_comparator(design: dict[str, object]):
    rows = read_tsv(ORACLE)
    by_record: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows: by_record[(row["collection_id"], row["recipe_id"])].append(row)
    records = []
    for key in sorted(by_record):
        klass = event_class(by_record[key])
        if klass is None: continue
        fields = build_fields(by_record[key], "concept_id", f"{key[0]}:{key[1]}")
        shape, flow = record_features(fields)
        records.append({"collection": key[0], "record": key[1], "class": klass, "shape": shape, "flow": flow,
                        "unit_count": sum(map(len, fields)), "field_count": len(fields)})
    class_index = {name: index for index, name in enumerate(CLASSES)}
    fold_rows = []
    predictions = []
    for held in design["comparator_collections"]:
        train = [record for record in records if record["collection"] != held]
        test = [record for record in records if record["collection"] == held]
        ytrain = np.array([class_index[record["class"]] for record in train], dtype=int)
        ytest = np.array([class_index[record["class"]] for record in test], dtype=int)
        for model in ("SHAPE_ONLY", "IDENTITY_FLOW_TOPOLOGY"):
            xtrain = np.array([record["shape"] + (record["flow"] if model == "IDENTITY_FLOW_TOPOLOGY" else []) for record in train], dtype=float)
            xtest = np.array([record["shape"] + (record["flow"] if model == "IDENTITY_FLOW_TOPOLOGY" else []) for record in test], dtype=float)
            fit = fit_multinomial(xtrain, ytrain, len(CLASSES), float(design["comparator_ridge"]))
            probs = predict_multinomial(xtest, fit)
            bits = float(sum(-math.log2(max(1e-300, probs[i, ytest[i]])) for i in range(len(test))))
            top1 = int(sum(np.argmax(probs, axis=1) == ytest))
            fold_rows.append({"held_collection": held, "model": model, "records": len(test), "bits": f"{bits:.9f}", "top1": top1})
            for record, y, prob in zip(test, ytest, probs):
                predictions.append({"record": record, "held": held, "model": model, "y": int(y), "prob": prob})
    aggregates = {}
    for model in ("SHAPE_ONLY", "IDENTITY_FLOW_TOPOLOGY"):
        selected = [row for row in fold_rows if row["model"] == model]
        aggregates[model] = {"records": sum(int(row["records"]) for row in selected), "bits": sum(float(row["bits"]) for row in selected), "top1": sum(int(row["top1"]) for row in selected)}
    shape = aggregates["SHAPE_ONLY"]; flow = aggregates["IDENTITY_FLOW_TOPOLOGY"]
    positive = sum(
        next(float(row["bits"]) for row in fold_rows if row["held_collection"] == held and row["model"] == "SHAPE_ONLY")
        > next(float(row["bits"]) for row in fold_rows if row["held_collection"] == held and row["model"] == "IDENTITY_FLOW_TOPOLOGY")
        for held in design["comparator_collections"]
    )
    # Fixed held-prediction null; shuffle complete class labels within matched
    # collection/size strata and score both predictions at the moved label.
    paired = {}
    for item in predictions:
        paired.setdefault((item["held"], item["record"]["record"]), {"record": item["record"], "y": item["y"]})[item["model"]] = item["prob"]
    items = list(paired.values())
    observed_gain = shape["bits"] - flow["bits"]
    groups: dict[tuple, list[int]] = defaultdict(list)
    for index, item in enumerate(items):
        record = item["record"]
        groups[(record["collection"], bucket(record["unit_count"]), bucket(record["field_count"]))].append(index)
    null_rows = []; exceed = 0
    for world in range(int(design["comparator_null"]["worlds"])):
        rng = random.Random(int(design["comparator_null"]["seed"]) + world)
        labels = [item["y"] for item in items]
        for indices in groups.values():
            local = [labels[index] for index in indices]; rng.shuffle(local)
            for index, value in zip(indices, local): labels[index] = value
        bshape = bflow = 0.0
        for item, y in zip(items, labels):
            bshape -= math.log2(max(1e-300, item["SHAPE_ONLY"][y])); bflow -= math.log2(max(1e-300, item["IDENTITY_FLOW_TOPOLOGY"][y]))
        gain = bshape - bflow; exceed += int(gain >= observed_gain - 1e-12)
        null_rows.append({"world": world, "topology_gain_over_shape": f"{gain:.9f}"})
    p = (1 + exceed) / (1 + len(null_rows))
    model_rows = [
        {"model": "SHAPE_ONLY", "records": shape["records"], "bits": f"{shape['bits']:.9f}", "top1": shape["top1"], "gain_over_shape": "0.000000000", "positive_collections": "NA", "inclusive_p": "NA"},
        {"model": "IDENTITY_FLOW_TOPOLOGY", "records": flow["records"], "bits": f"{flow['bits']:.9f}", "top1": flow["top1"], "gain_over_shape": f"{observed_gain:.9f}", "positive_collections": positive, "inclusive_p": f"{p:.9f}"},
    ]
    supported = observed_gain > 0 and positive >= int(design["comparator_gate"]["positive_collections_min"]) and p <= float(design["comparator_gate"]["inclusive_p_max"])
    status = "COMPARATOR_EVENT_PATH_CALIBRATED" if supported else "COMPARATOR_EVENT_PATH_NOT_CALIBRATED"
    return records, fold_rows, model_rows, null_rows, status, supported


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    design = json.loads(DESIGN.read_text())
    edges, source_stats = make_edges()
    atlas_rows = atlas(edges)
    transition_rows = []
    for edge in edges:
        transition_rows.append({
            "edge_id": edge["edge_id"], "panel": edge["panel"], "page": edge["page"], "physical_folio": edge["physical_folio"],
            "source_record": edge["source_record"], "target_record": edge["target_record"], "source_locus": edge["source_locus"], "target_locus": edge["target_locus"],
            "source_tuple_id": edge["source_tuple"], "target_tuple_id": edge["target_tuple"], "source_coordinate_id": edge["source_coordinate"], "target_coordinate_id": edge["target_coordinate"],
            "scope": edge["scope"], "field_order": edge["field_order"], "field_boundary": edge["field_boundary"], "record_boundary": edge["record_boundary"], "line_reset": edge["line_reset"],
            "shape_path_id": edge["shape_path_id"], "value_path_id": edge["value_path_id"], "source_renderer_state": edge["source_renderer"], "target_renderer_state": edge["target_renderer"],
            "semantic_state": "UNASSIGNED", "translation_state": "UNASSIGNED",
        })
    write_tsv(TRANSITIONS, transition_rows)
    write_tsv(PATH_ATLAS, atlas_rows)

    formal_folds, formal_models, formal_null, formal_status, formal_supported, _ = run_formal(edges, design)
    write_tsv(FORMAL_FOLDS, formal_folds); write_tsv(FORMAL_MODELS, formal_models); write_tsv(FORMAL_NULL, formal_null)

    comparator_records, comparator_folds, comparator_models, comparator_null, comparator_status, comparator_supported = run_comparator(design)
    write_tsv(COMPARATOR_FOLDS, comparator_folds); write_tsv(COMPARATOR_MODELS, comparator_models); write_tsv(COMPARATOR_NULL, comparator_null)

    # Stage C is deliberately gated. Its schema is emitted even on stop so the
    # absence of target semantic scoring is machine-checkable.
    stage_c_authorized = bool(formal_supported and comparator_supported)
    target_rows: list[dict[str, object]] = []
    write_tsv(TARGET_FOLDS, target_rows, ["panel", "held_folio", "model", "records", "bits", "top1", "gain_over_baseline", "semantic_state"])
    target_status = "NO_SECTION_SPECIFIC_EVENT_PATH_ALIGNMENT" if not stage_c_authorized else "INSUFFICIENT_CAPACITY"

    counterexamples = [
        {"code": "EXACT_PAIR_SPARSITY", "detail": f"{len({(e['source_tuple'],e['target_tuple']) for e in edges})} exact tuple-pair types among {len(edges)} transitions", "effect": "ABSTRACT_PATH_MUST_BEAT_EXACT_PREDECESSOR"},
        {"code": "RECORD_RESET", "detail": f"{sum(int(e['record_boundary']) for e in edges)} record-boundary edges retained as reset diagnostics", "effect": "NOT_PROCESS_CONTINUATION"},
        {"code": "RENDERER_NUISANCE", "detail": "supported s@LINE_START and q@POST_DY canonicalized before path construction", "effect": "NO_RENDERER_SEMANTICS"},
        {"code": "COMPARATOR_GATE", "detail": comparator_status, "effect": "STAGE_C_AUTHORIZED" if stage_c_authorized else "STAGE_C_STOPPED"},
        {"code": "TARGET_ACCESS", "detail": "GDT327 formal Recipe/Pharma rows used only in Stage A; no event-path likeness assigned unless both gates pass", "effect": target_status},
        {"code": "F84", "detail": "all f84 selectors forbidden before row parse", "effect": "NO_ACCESS"},
    ]
    write_tsv(COUNTEREXAMPLES, counterexamples)

    best_formal = min(formal_models, key=lambda row: float(row["total_bits"]))
    comparator_candidate = next(row for row in comparator_models if row["model"] == "IDENTITY_FLOW_TOPOLOGY")
    status = formal_status if formal_status != "ABSTRACT_GRAMMAR_TRANSITION_PATHS_SUPPORTED" else comparator_status
    report = f"""# GDT344 — grammar transition paths above atomic tuples

Formal status: **{formal_status}**. Comparator status: **{comparator_status}**. Target alignment: **{target_status}**.

The section-restricted inventory contains {source_stats['groups']:,} atomic groups and {source_stats['edges']:,} adjacent transitions on {source_stats['folios']} folios. The best held-folio formal model is `{best_formal['model']}` at {float(best_formal['total_bits']):.3f} total bits; its gain over exact predecessor is {best_formal['gain_over_exact_predecessor']} bits and max-two diagnostic p is {best_formal.get('max_two_p','NA')}.

The readable event-path comparator covers {len(comparator_records):,} eligible complete records. Anonymous identity-flow topology changes held log-loss over shape by {float(comparator_candidate['gain_over_shape']):+.3f} bits, is positive in {comparator_candidate['positive_collections']}/6 held collections, and has inclusive p={comparator_candidate['inclusive_p']}.

Stage C requires both the formal and readable-comparator gates. Authorized: `{str(stage_c_authorized).lower()}`. No tuple or field receives a recipe role or gloss.

Exact GDT327 tuple identities remain atomic. PAGE_HOST was not factored, no other Voynich section was retained, and no f84 selector was parsed, joined, or scored.
"""
    REPORT.write_text(report)
    comparator_report = f"""# GDT344 comparator — complete-record event paths

Status: **{comparator_status}**.

Five complete-record classes were defined from readable CoReMA roles only for evaluation. Model features contain no words, concept names, or role names. The frozen topology model changes held log-loss over record shape by {float(comparator_candidate['gain_over_shape']):+.3f} bits, is positive in {comparator_candidate['positive_collections']}/6 collections, and has inclusive p={comparator_candidate['inclusive_p']}.

This is an instrument calibration, not a claim that any Voynich record contains MATERIAL, OPERATION, STATE, APPLICATION, or RESULT.
"""
    COMPARATOR_REPORT.write_text(comparator_report)

    inputs = {str(path.relative_to(ROOT)): sha(path) for path in (METHOD, SOURCE_AUDIT, DESIGN, NATIVE, INTER, GDT336_FOLDS, TARGET_RECORDS, ORACLE, COREMA_MANIFEST, COREMA_FREEZE)}
    outputs = {str(path.relative_to(ROOT)): sha(path) for path in (TRANSITIONS, PATH_ATLAS, FORMAL_FOLDS, FORMAL_MODELS, FORMAL_NULL, COMPARATOR_FOLDS, COMPARATOR_MODELS, COMPARATOR_NULL, TARGET_FOLDS, COUNTEREXAMPLES, REPORT, COMPARATOR_REPORT)}
    result = {
        "schema": "GDT344_RESULT_V1", "date": "2026-08-19", "status": status,
        "formal_status": formal_status, "formal_supported_models": formal_supported,
        "comparator_status": comparator_status, "stage_c_authorized": stage_c_authorized, "target_status": target_status,
        "source": source_stats, "path_atlas": {"rows": len(atlas_rows), "eligible": sum(int(row["eligible_abstract_path"]) for row in atlas_rows)},
        "formal_models": {row["model"]: row for row in formal_models}, "comparator_models": {row["model"]: row for row in comparator_models},
        "voynich_semantic_assignments": 0, "tuple_merges": 0, "page_host_factorizations": 0,
        "other_section_rows_retained": 0, "f84": {"opened": False, "parsed": False, "retained": False, "joined": False, "scored": False},
        "claim_ceiling": "Formal transition recurrence and gated record-event-path likeness only; no tuple merge role meaning language plaintext or translation.",
        "inputs": inputs, "outputs": outputs,
        "implementation": {str(Path(__file__).resolve().relative_to(ROOT)): sha(Path(__file__).resolve())},
    }
    result["content_sha256"] = content_hash(result)
    RESULT.write_bytes(canonical(result))
    print(f"{status} formal={formal_status} comparator={comparator_status} stage_c={stage_c_authorized}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
