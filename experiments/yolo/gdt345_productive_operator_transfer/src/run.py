#!/usr/bin/env python3
"""GDT345: productive formal-delta prediction without target leakage."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import random
from collections import Counter, defaultdict
from pathlib import Path


def find_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("repository root not found")


ROOT = find_root(Path(__file__).resolve())
import sys
sys.path.insert(0, str(ROOT))
from tools.vmanus_experiment import GuardedTSV  # noqa: E402

EXP = ROOT / "experiments/yolo/gdt345_productive_operator_transfer"
ART = EXP / "artifacts"
METHOD = EXP / "METHOD.md"
SOURCE_AUDIT = EXP / "SOURCE_AUDIT.md"
DESIGN = ART / "gdt345_design.json"
NATIVE = ROOT / "gdt278_native_event_inventory.tsv"
INTER = ROOT / "gdt327_joint_tuple_interlinear.tsv"
OPERATORS = ART / "gdt345_operator_inventory.tsv"
TRANSITIONS = ART / "gdt345_transition_inventory.tsv"
LOFO = ART / "gdt345_lofo_folds.tsv"
TRANSFER = ART / "gdt345_transfer_folds.tsv"
SCORES = ART / "gdt345_model_scores.tsv"
NULL = ART / "gdt345_null.tsv"
COUNTER = ART / "gdt345_counterexamples.tsv"
RESULT = ART / "gdt345_result.json"
REPORT = EXP / "REPORT.md"

COMPONENTS = ("local_frame", "inner_d", "right_family", "dy_closure", "b3", "canonical_wrapper")
MODELS = ("PLACEMENT", "EXACT_PREDECESSOR", "SOURCE_STATE_TABLE", "FACTORIAL_OPERATOR")


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()


def content_hash(document: dict[str, object]) -> str:
    copy = dict(document); copy.pop("content_sha256", None)
    return hashlib.sha256(canonical(copy)).hexdigest()


def hid(domain: str, value: object, length: int = 20) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256((domain + "\0" + payload).encode()).hexdigest()[:length]


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str] | None = None) -> None:
    if fields is None:
        if not rows:
            raise ValueError(f"empty rows require fields: {path}")
        fields = list(rows[0])
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fields, delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def canonical_wrapper(row: dict[str, str]) -> str:
    if row["wrapper"] == "s" and row["line_first"] == "1":
        return "NONE"
    if row["wrapper"] == "q" and row["prev_dy"] == "1":
        return "NONE"
    return row["wrapper"]


def state(row: dict[str, str]) -> tuple[str, ...]:
    return (row["local_frame"], row["inner_d"], row["right_family"], row["dy_closure"], row["b3"], canonical_wrapper(row))


def delta(source: tuple[str, ...], target: tuple[str, ...]) -> tuple[str, ...]:
    return tuple("KEEP" if left == right else f"SET:{right}" for left, right in zip(source, target))


def apply_delta(source: tuple[str, ...], operation: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(left if change == "KEEP" else change[4:] for left, change in zip(source, operation))


def boundary(a: dict[str, str], b: dict[str, str]) -> tuple[str, str, int, int, int, str]:
    record_reset = int(a["record_ordinal"] != b["record_ordinal"])
    line_reset = int(a["locus"] != b["locus"])
    field_reset = int((a["record_ordinal"], a["field_ordinal"]) != (b["record_ordinal"], b["field_ordinal"]))
    if record_reset:
        scope, order, reset = "RECORD_RESET", "RECORD_RESET", "RECORD_START"
    elif line_reset:
        step = int(b["field_ordinal"]) - int(a["field_ordinal"])
        order = "SAME_FIELD" if not field_reset else ("NEXT_FIELD" if step == 1 else ("FIELD_RESET" if step < 1 else "FIELD_SKIP"))
        scope, reset = "LINE_RESET", "LINE_START"
    elif field_reset:
        step = int(b["field_ordinal"]) - int(a["field_ordinal"])
        order = "NEXT_FIELD" if step == 1 else ("FIELD_RESET" if step < 1 else "FIELD_SKIP")
        scope, reset = "FIELD_BOUNDARY", "CONTINUATION"
    else:
        scope, order, reset = "SAME_FIELD", "SAME_FIELD", "CONTINUATION"
    return scope, order, field_reset, line_reset, record_reset, reset


def line_quartile(row: dict[str, str]) -> str:
    return str(min(3, 4 * (int(row["group_index"]) - 1) // max(1, int(row["group_count"]))))


def make_edges() -> tuple[list[dict[str, object]], dict[str, object]]:
    inter_reader = GuardedTSV(INTER, selector_column="page", forbidden_prefixes=("f84",), forbidden_action="skip")
    inter = list(inter_reader)
    keys = {(row["page"], row["locus"], row["group_index"]) for row in inter}
    if len(keys) != len(inter):
        raise AssertionError("GDT327 key is not unique")
    pages = {row["page"] for row in inter}
    native_reader = GuardedTSV(NATIVE, selector_column="page", allowed_values=pages, forbidden_prefixes=("f84",), forbidden_action="skip")
    native = [row for row in native_reader if row["control_id"] == "VOYNICH_REFERENCE" and (row["page"], row["locus"], row["group_index"]) in keys]
    nk = {(row["page"], row["locus"], row["group_index"]): row for row in native}
    if len(nk) != len(native) or set(nk) != keys:
        raise AssertionError(f"GDT278/GDT327 join mismatch: {len(nk)} {len(keys)}")
    if any(row["page"].startswith("f84") or row["locus"].startswith("f84") for row in inter + native):
        raise AssertionError("f84 retained")
    by_page: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in inter:
        key = (row["page"], row["locus"], row["group_index"])
        by_page[row["page"]].append({**nk[key], **row})
    edges: list[dict[str, object]] = []
    for page, rows in by_page.items():
        for edge_ordinal, (a, b) in enumerate(zip(rows, rows[1:]), 1):
            source_state, target_state = state(a), state(b)
            text_delta = delta(source_state, target_state)
            scope, field_order, field_boundary, line_reset, record_reset, reset = boundary(a, b)
            layout = (scope, field_order, b["line_first"], b["within_field_position"], line_quartile(b))
            full_operator = (*text_delta, scope, field_order, reset)
            source_state_id = hid("GDT345_STATE_V1", source_state)
            target_state_id = hid("GDT345_STATE_V1", target_state)
            text_operator_id = hid("GDT345_TEXT_OPERATOR_V1", text_delta)
            operator_id = hid("GDT345_OPERATOR_V1", full_operator)
            edges.append({
                "edge_id": hid("GDT345_EDGE_V1", (page, edge_ordinal, a["locus"], a["group_index"], b["locus"], b["group_index"])),
                "page": page, "physical_folio": a["physical_folio"], "section": a["section"], "register": a["register"], "hand": a["hand"],
                "source_locus": a["locus"], "target_locus": b["locus"], "source_group_index": a["group_index"], "target_group_index": b["group_index"],
                "source_tuple": a["joint_tuple_id"], "target_tuple": b["joint_tuple_id"], "source_state": source_state, "target_state": target_state,
                "source_state_id": source_state_id, "target_state_id": target_state_id, "text_delta": text_delta,
                "text_operator_id": text_operator_id, "operator_id": operator_id, "full_operator": full_operator,
                "scope": scope, "field_order": field_order, "field_boundary": field_boundary, "line_reset": line_reset, "record_reset": record_reset,
                "reset_state": reset, "layout": layout,
            })
    stats = {
        "groups": len(inter), "pages": len(by_page), "folios": len({row["physical_folio"] for row in inter}), "edges": len(edges),
        "sections": dict(sorted(Counter(str(edge["section"]) for edge in edges).items())),
        "registers": dict(sorted(Counter(str(edge["register"]) for edge in edges).items())),
        "hands": dict(sorted(Counter(str(edge["hand"]) for edge in edges).items())),
        "inter_guard": inter_reader.stats.__dict__, "native_guard": native_reader.stats.__dict__,
    }
    return edges, stats


def model_context(edge: dict[str, object], model: str, component: int) -> tuple[object, ...] | None:
    layout = tuple(edge["layout"])
    if model == "PLACEMENT":
        return None
    if model == "EXACT_PREDECESSOR":
        return (*layout, "TUPLE", edge["source_tuple"])
    if model == "SOURCE_STATE_TABLE":
        return (*layout, "STATE", edge["source_state_id"])
    if model == "FACTORIAL_OPERATOR":
        return (*layout, f"C{component}", edge["source_state"][component])
    raise ValueError(model)


def build_tables(train: list[dict[str, object]], design: dict[str, object], model: str) -> dict[str, object]:
    globals_ = [Counter() for _ in COMPONENTS]
    layouts: list[dict[tuple, Counter[str]]] = [defaultdict(Counter) for _ in COMPONENTS]
    contexts: list[dict[tuple, Counter[str]]] = [defaultdict(Counter) for _ in COMPONENTS]
    for edge in train:
        layout = tuple(edge["layout"])
        for index, label in enumerate(edge["text_delta"]):
            globals_[index][label] += 1
            layouts[index][layout][label] += 1
            context = model_context(edge, model, index)
            if context is not None:
                contexts[index][context][label] += 1
    return {"global": globals_, "layout": layouts, "context": contexts, "design": design, "model": model}


def component_distribution(edge: dict[str, object], tables: dict[str, object], index: int) -> dict[str, float]:
    global_counts: Counter[str] = tables["global"][index]
    labels = tuple(sorted(global_counts))
    k, gn = len(labels), sum(global_counts.values())
    if not labels:
        return {}
    jf = float(tables["design"]["alphas"]["global_jeffreys"])
    global_prob = {label: (global_counts[label] + jf) / (gn + jf * k) for label in labels}
    layout = tuple(edge["layout"])
    layout_counts: Counter[str] = tables["layout"][index].get(layout, Counter())
    ln = sum(layout_counts.values()); a_layout = float(tables["design"]["alphas"]["layout_to_global"])
    layout_prob = {label: (layout_counts[label] + a_layout * global_prob[label]) / (ln + a_layout) for label in labels}
    if tables["model"] == "PLACEMENT":
        return layout_prob
    context = model_context(edge, str(tables["model"]), index)
    counts: Counter[str] = tables["context"][index].get(context, Counter())
    n = sum(counts.values()); alpha = float(tables["design"]["alphas"]["source_to_layout"])
    return {label: (counts[label] + alpha * layout_prob[label]) / (n + alpha) for label in labels}


def predict(edge: dict[str, object], tables: dict[str, object]) -> tuple[float, tuple[str, ...]] | None:
    bits = 0.0; chosen: list[str] = []
    for index, truth in enumerate(edge["text_delta"]):
        probs = component_distribution(edge, tables, index)
        if truth not in probs:
            return None
        bits -= math.log2(max(1e-300, probs[truth]))
        chosen.append(min(probs, key=lambda label: (-probs[label], label)))
    return bits, tuple(chosen)


def run_split(edges: list[dict[str, object]], split_name: str, key: str, design: dict[str, object]) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    fold_rows: list[dict[str, object]] = []
    events: list[dict[str, object]] = []
    for held in sorted({str(edge[key]) for edge in edges}):
        train = [edge for edge in edges if str(edge[key]) != held]
        test = [edge for edge in edges if str(edge[key]) == held]
        tables = {model: build_tables(train, design, model) for model in MODELS}
        train_states = {str(edge["source_state_id"]) for edge in train}
        train_ops = {str(edge["operator_id"]) for edge in train}
        train_combos = {(str(edge["source_state_id"]), str(edge["operator_id"])) for edge in train}
        aggregates = {model: {"bits": 0.0, "n": 0, "hits": 0, "unseen_bits": 0.0, "unseen_n": 0, "unseen_hits": 0} for model in MODELS}
        for edge in test:
            predictions = {model: predict(edge, tables[model]) for model in MODELS}
            if any(value is None for value in predictions.values()):
                continue
            combo = (str(edge["source_state_id"]), str(edge["operator_id"]))
            unseen_combo = str(edge["source_state_id"]) in train_states and str(edge["operator_id"]) in train_ops and combo not in train_combos
            event = {"edge": edge, "held": held, "split": split_name, "unseen_combo": unseen_combo, "predicted": {}}
            for model, value in predictions.items():
                bits, pred_delta = value
                pred_state = apply_delta(edge["source_state"], pred_delta)
                hit = int(pred_state == edge["target_state"])
                agg = aggregates[model]; agg["bits"] += bits; agg["n"] += 1; agg["hits"] += hit
                if unseen_combo:
                    agg["unseen_bits"] += bits; agg["unseen_n"] += 1; agg["unseen_hits"] += hit
                event["predicted"][model] = {"delta": pred_delta, "text_operator_id": hid("GDT345_TEXT_OPERATOR_V1", pred_delta), "bits": bits, "hit": hit}
            events.append(event)
        exact = aggregates["EXACT_PREDECESSOR"]
        placement = aggregates["PLACEMENT"]
        for model in MODELS:
            agg = aggregates[model]
            fold_rows.append({
                "split": split_name, "held_value": held, "model": model, "eligible_events": agg["n"], "total_bits": f"{agg['bits']:.9f}",
                "exact_next_state_hits": agg["hits"], "gain_over_placement": f"{placement['bits'] - agg['bits']:.9f}",
                "gain_over_exact_predecessor": f"{exact['bits'] - agg['bits']:.9f}", "unseen_combo_events": agg["unseen_n"],
                "unseen_combo_bits": f"{agg['unseen_bits']:.9f}", "unseen_combo_hits": agg["unseen_hits"],
                "unseen_gain_over_exact": f"{exact['unseen_bits'] - agg['unseen_bits']:.9f}",
            })
    return fold_rows, events


def aggregate_models(folds: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    agg: dict[str, dict[str, float]] = {}
    for model in MODELS:
        selected = [row for row in folds if row["model"] == model]
        agg[model] = {
            "n": sum(int(row["eligible_events"]) for row in selected), "bits": sum(float(row["total_bits"]) for row in selected),
            "hits": sum(int(row["exact_next_state_hits"]) for row in selected), "un": sum(int(row["unseen_combo_events"]) for row in selected),
            "ub": sum(float(row["unseen_combo_bits"]) for row in selected), "uh": sum(int(row["unseen_combo_hits"]) for row in selected),
        }
    for model in MODELS:
        x = agg[model]
        positives = sum(float(row["gain_over_exact_predecessor"]) > 0 for row in folds if row["model"] == model)
        rows.append({
            "model": model, "eligible_events": int(x["n"]), "total_bits": f"{x['bits']:.9f}", "exact_next_state_hits": int(x["hits"]),
            "gain_over_placement": f"{agg['PLACEMENT']['bits'] - x['bits']:.9f}", "gain_over_exact_predecessor": f"{agg['EXACT_PREDECESSOR']['bits'] - x['bits']:.9f}",
            "gain_over_source_state_table": f"{agg['SOURCE_STATE_TABLE']['bits'] - x['bits']:.9f}", "positive_folios_vs_exact": positives,
            "unseen_combo_events": int(x["un"]), "unseen_combo_bits": f"{x['ub']:.9f}", "unseen_combo_hits": int(x["uh"]),
            "unseen_gain_over_placement": f"{agg['PLACEMENT']['ub'] - x['ub']:.9f}", "unseen_gain_over_exact": f"{agg['EXACT_PREDECESSOR']['ub'] - x['ub']:.9f}",
            "unseen_gain_over_source_state": f"{agg['SOURCE_STATE_TABLE']['ub'] - x['ub']:.9f}", "inclusive_p": "NA", "max_two_p": "NA",
        })
    return rows


def run_null(events: list[dict[str, object]], design: dict[str, object]) -> tuple[list[dict[str, object]], dict[str, float], int]:
    candidates = ("SOURCE_STATE_TABLE", "FACTORIAL_OPERATOR")
    observed = {model: sum(int(event["predicted"][model]["hit"]) - int(event["predicted"]["EXACT_PREDECESSOR"]["hit"]) for event in events) for model in candidates}
    groups: dict[tuple, list[int]] = defaultdict(list)
    for index, event in enumerate(events):
        groups[(event["held"], *tuple(event["edge"]["layout"]))].append(index)
    mobile = sum(len(indices) for indices in groups.values() if len({events[index]["edge"]["text_operator_id"] for index in indices}) >= 2)
    null_rows: list[dict[str, object]] = []; exceed = Counter(); exceed_max = 0; obs_max = max(observed.values())
    for world in range(int(design["null"]["worlds"])):
        rng = random.Random(int(design["null"]["seed"]) + world)
        labels = [str(event["edge"]["text_operator_id"]) for event in events]
        for indices in groups.values():
            local = [labels[index] for index in indices]; rng.shuffle(local)
            for index, value in zip(indices, local): labels[index] = value
        gains = {}
        for model in candidates:
            model_hits = sum(str(event["predicted"][model]["text_operator_id"]) == labels[index] for index, event in enumerate(events))
            exact_hits = sum(str(event["predicted"]["EXACT_PREDECESSOR"]["text_operator_id"]) == labels[index] for index, event in enumerate(events))
            gains[model] = model_hits - exact_hits; exceed[model] += int(gains[model] >= observed[model])
        maximum = max(gains.values()); exceed_max += int(maximum >= obs_max)
        null_rows.append({"world": world, "source_state_hit_gain": gains["SOURCE_STATE_TABLE"], "factorial_hit_gain": gains["FACTORIAL_OPERATOR"], "max_two_hit_gain": maximum})
    p = {model: (1 + exceed[model]) / (1 + len(null_rows)) for model in candidates}
    p["MAX_TWO"] = (1 + exceed_max) / (1 + len(null_rows))
    return null_rows, p, mobile


def inventory_rows(edges: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for edge in edges: grouped[str(edge["operator_id"])].append(edge)
    rows = []
    for operator_id, values in grouped.items():
        first = values[0]
        rows.append({
            "operator_id": operator_id, "text_operator_id": first["text_operator_id"], "delta_json": json.dumps(first["text_delta"], separators=(",", ":")),
            "boundary_scope": first["scope"], "field_order": first["field_order"], "reset_state": first["reset_state"], "events": len(values),
            "folios": len({edge["physical_folio"] for edge in values}), "sections": "|".join(sorted({str(edge["section"]) for edge in values})),
            "source_states": len({edge["source_state_id"] for edge in values}), "source_tuples": len({edge["source_tuple"] for edge in values}), "semantic_state": "UNASSIGNED",
        })
    return sorted(rows, key=lambda row: (-int(row["events"]), str(row["operator_id"])))


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    design = json.loads(DESIGN.read_text())
    edges, source = make_edges()
    operators = inventory_rows(edges)
    write_tsv(OPERATORS, operators)
    transition_rows = []
    for edge in edges:
        transition_rows.append({
            "edge_id": edge["edge_id"], "page": edge["page"], "physical_folio": edge["physical_folio"], "section": edge["section"], "register": edge["register"], "hand": edge["hand"],
            "source_locus": edge["source_locus"], "target_locus": edge["target_locus"], "source_group_index": edge["source_group_index"], "target_group_index": edge["target_group_index"],
            "source_tuple_id": edge["source_tuple"], "target_tuple_id": edge["target_tuple"], "source_state_id": edge["source_state_id"], "target_state_id": edge["target_state_id"],
            "source_state_json": json.dumps(edge["source_state"], separators=(",", ":")), "target_state_json": json.dumps(edge["target_state"], separators=(",", ":")),
            "delta_json": json.dumps(edge["text_delta"], separators=(",", ":")), "text_operator_id": edge["text_operator_id"], "operator_id": edge["operator_id"],
            "boundary_scope": edge["scope"], "field_order": edge["field_order"], "field_boundary": edge["field_boundary"], "line_reset": edge["line_reset"], "record_reset": edge["record_reset"],
            "reset_state": edge["reset_state"], "layout_context_json": json.dumps(edge["layout"], separators=(",", ":")), "semantic_state": "UNASSIGNED", "translation_state": "UNASSIGNED",
        })
    write_tsv(TRANSITIONS, transition_rows)

    lofo_rows, lofo_events = run_split(edges, "PHYSICAL_FOLIO", "physical_folio", design)
    write_tsv(LOFO, lofo_rows)
    transfer_rows: list[dict[str, object]] = []
    for name, key in (("SECTION", "section"), ("REGISTER", "register"), ("HAND", "hand")):
        rows, _ = run_split(edges, name, key, design); transfer_rows.extend(rows)
    write_tsv(TRANSFER, transfer_rows)
    scores = aggregate_models(lofo_rows)
    null_rows, null_p, mobile = run_null(lofo_events, design)
    write_tsv(NULL, null_rows)
    for row in scores:
        if row["model"] in {"SOURCE_STATE_TABLE", "FACTORIAL_OPERATOR"}:
            row["inclusive_p"] = f"{null_p[str(row['model'])]:.9f}"; row["max_two_p"] = f"{null_p['MAX_TWO']:.9f}"
    write_tsv(SCORES, scores)

    score = {str(row["model"]): row for row in scores}
    fac = score["FACTORIAL_OPERATOR"]
    powered = int(design["gate"]["minimum_powered_events"])
    fraction = float(design["gate"]["positive_category_fraction"])
    transfer_summary = {}
    for split in ("SECTION", "REGISTER", "HAND"):
        rows = [row for row in transfer_rows if row["split"] == split and row["model"] == "FACTORIAL_OPERATOR" and int(row["eligible_events"]) >= powered]
        positive = sum(float(row["gain_over_exact_predecessor"]) > 0 for row in rows)
        gain = sum(float(row["gain_over_exact_predecessor"]) for row in rows)
        transfer_summary[split] = {"powered_categories": len(rows), "positive_categories": positive, "aggregate_gain_over_exact": gain, "passes": bool(rows and gain > 0 and positive >= math.ceil(fraction * len(rows)))}
    lofo_baselines = ("PLACEMENT", "EXACT_PREDECESSOR", "SOURCE_STATE_TABLE")
    bits_gate = all(float(fac["total_bits"]) < float(score[model]["total_bits"]) for model in lofo_baselines)
    hits_gate = all(int(fac["exact_next_state_hits"]) > int(score[model]["exact_next_state_hits"]) for model in lofo_baselines)
    unseen_gate = all(float(fac["unseen_combo_bits"]) < float(score[model]["unseen_combo_bits"]) and int(fac["unseen_combo_hits"]) >= int(score[model]["unseen_combo_hits"]) for model in ("PLACEMENT", "EXACT_PREDECESSOR"))
    positive_folios = int(fac["positive_folios_vs_exact"])
    folio_gate = positive_folios >= math.ceil(float(design["gate"]["positive_folio_fraction"]) * source["folios"])
    p_gate = float(fac["max_two_p"]) <= float(design["gate"]["inclusive_max_two_p"])
    gates = {"lofo_bits_over_all": bits_gate, "lofo_exact_recovery_over_all": hits_gate, "unseen_combo": unseen_gate, "positive_folios": folio_gate, "held_transfer_families": all(x["passes"] for x in transfer_summary.values()), "max_two_p": p_gate}
    if int(fac["unseen_combo_events"]) < powered or mobile < powered:
        status = "INSUFFICIENT_CAPACITY"
    elif all(gates.values()):
        status = "PRODUCTIVE_FORMAL_OPERATOR_TRANSFER_SUPPORTED"
    elif float(fac["gain_over_exact_predecessor"]) > 0 or float(fac["unseen_gain_over_exact"]) > 0:
        status = "LOCAL_OR_LEXICAL_OPERATOR_DEPENDENCE_ONLY"
    else:
        status = "NO_PRODUCTIVE_OPERATOR_TRANSFER"

    counterexamples = [
        {"code": "GDT344_PREDECESSOR_LEAD", "detail": "GDT344 exact predecessor beat target-conditioned path models overall", "effect": "PRODUCTIVE_MODEL_MUST_BEAT_EXACT_PREDECESSOR"},
        {"code": "UNSEEN_COMBINATION", "detail": f"{fac['unseen_combo_events']} LOFO events have source state and operator seen separately but pair unseen", "effect": f"factorial gain over exact={fac['unseen_gain_over_exact']} bits"},
        {"code": "NULL_CAPACITY", "detail": f"{mobile} LOFO events lie in exact-layout strata with at least two operator values", "effect": "FIXED_PREDICTION_ALIGNMENT_DIAGNOSTIC"},
        {"code": "TARGET_LEAKAGE", "detail": "target wrapper coordinate tuple and target-derived signatures excluded from all contexts", "effect": "TRUE_OPERATOR_PREDICTION"},
        {"code": "ATOMIC_TUPLES", "detail": "exact predecessor uses opaque joint_tuple_id only; PAGE_HOST never factored", "effect": "NO_SUBSTRING_OR_HOST_MINING"},
        {"code": "SEMANTIC_ALIGNMENT", "detail": "not run by design", "effect": "NO_ROLE_OR_MEANING"},
        {"code": "F84", "detail": "raw f84 selectors rejected before row parse", "effect": "NO_ACCESS"},
    ]
    write_tsv(COUNTER, counterexamples)
    report = f"""# GDT345 — productive formal-operator transfer

Status: **{status}**.

GDT345 formed {source['edges']:,} adjacent formal transitions from {source['groups']:,} source groups on {source['folios']} physical folios. The inventory contains {len(operators)} registered boundary-aware operators. Unlike GDT344, the target delta was never used as a predictor: each held operator was selected from source-side state and observable boundary/layout only, applied to the source, and scored against the next six-coordinate formal state.

The factorized operator model changes LOFO codelength by {float(fac['gain_over_exact_predecessor']):+.3f} bits relative to exact atomic predecessor and by {float(fac['gain_over_placement']):+.3f} bits relative to layout. It exactly reconstructs {fac['exact_next_state_hits']}/{fac['eligible_events']} next states, versus {score['EXACT_PREDECESSOR']['exact_next_state_hits']} for exact predecessor. On {fac['unseen_combo_events']} events whose source state and operator were individually known but whose combination was unseen in training, its gain over exact predecessor is {float(fac['unseen_gain_over_exact']):+.3f} bits with {fac['unseen_combo_hits']} exact recoveries versus {score['EXACT_PREDECESSOR']['unseen_combo_hits']}.

The factorized model beats exact predecessor on {fac['positive_folios_vs_exact']}/{source['folios']} physical folios. Held-category transfer is: {json.dumps(transfer_summary, sort_keys=True)}. The exact-layout fixed-prediction max-two p is {fac['max_two_p']} over {mobile} mobile events. Gate outcomes are {json.dumps(gates, sort_keys=True)}.

No semantic comparator was run. Exact joint tuples stayed opaque and atomic; PAGE_HOST was not factored; no glyph string, role, meaning, or translation was used. All f84 selectors were rejected before row parsing.
"""
    REPORT.write_text(report)
    inputs = {str(path.relative_to(ROOT)): sha(path) for path in (METHOD, SOURCE_AUDIT, DESIGN, NATIVE, INTER)}
    outputs = {str(path.relative_to(ROOT)): sha(path) for path in (OPERATORS, TRANSITIONS, LOFO, TRANSFER, SCORES, NULL, COUNTER, REPORT)}
    result = {
        "schema": "GDT345_RESULT_V1", "date": "2026-08-19", "status": status, "source": source,
        "operator_inventory": {"registered_operators": len(operators), "text_operators": len({edge['text_operator_id'] for edge in edges}), "source_states": len({edge['source_state_id'] for edge in edges}), "target_states": len({edge['target_state_id'] for edge in edges}), "source_state_operator_combinations": len({(edge['source_state_id'], edge['operator_id']) for edge in edges})},
        "models": score, "transfer": transfer_summary, "null_mobile_events": mobile, "gates": gates,
        "semantic_alignments": 0, "tuple_merges": 0, "page_host_factorizations": 0,
        "f84": {"opened": False, "parsed": False, "retained": False, "joined": False, "scored": False},
        "claim_ceiling": "Held formal-delta reconstruction only; no morphology semantics word meaning language plaintext translation or f84 result.",
        "inputs": inputs, "outputs": outputs, "implementation": {str(Path(__file__).resolve().relative_to(ROOT)): sha(Path(__file__).resolve())},
    }
    result["content_sha256"] = content_hash(result); RESULT.write_bytes(canonical(result))
    print(f"{status} edges={source['edges']} unseen={fac['unseen_combo_events']} gain_exact={fac['gain_over_exact_predecessor']} max2={fac['max_two_p']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
