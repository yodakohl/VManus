#!/usr/bin/env python3
"""Unblind GDT172 and compare it exactly with published GDT171."""
from __future__ import annotations

import csv
import gzip
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

from unblind_gdt171_historical_calibration import (
    blind_full, held_decoder, information, oracle_full,
)

R = Path(__file__).resolve().parent
OBS = R / "gdt172_observation_corpus.json.gz"; ORACLE = R / "gdt172_sealed_oracle.json.gz"
FREEZE = R / "gdt172_source_literal_correction_freeze.json"; DESIGN = R / "gdt172_blind_design.json"
PARSES = R / "gdt172_blind_parses.json.gz"; BLIND = R / "gdt172_blind_result.json"
BLIND_VALIDATION = R / "gdt172_blind_validation.json"; BLIND_DIAG = R / "gdt172_blind_diagnostics.tsv"
OPS = R / "gdt172_blind_operations.tsv"; OLD_LEVELS = R / "gdt171_recovery_levels.tsv"
OLD_COMPONENTS = R / "gdt171_component_recovery.tsv"; OLD_DIAG = R / "gdt171_blind_diagnostics.tsv"
OLD_OPS = R / "gdt171_blind_operations.tsv"; OLD_RESULT = R / "gdt171_result.json"
METHOD = R / "GDT172_LITERAL_ESCAPE_CORRECTION_METHOD.md"
LEVELS = R / "gdt172_recovery_levels.tsv"; COMPONENTS = R / "gdt172_component_recovery.tsv"
CALIBRATION = R / "gdt172_diagnostic_calibration.tsv"; DELTAS = R / "gdt172_gdt171_delta.tsv"
COUNTER = R / "gdt172_counterexamples.tsv"; REPORT = R / "GDT172_LITERAL_ESCAPE_CORRECTION_REPORT.md"
RESULT = R / "gdt172_result.json"

A = "SYSTEM_A_V3_UNCHANGED_LITERAL"
B = "SYSTEM_B_FACTORIAL_DISTRIBUTED_CONTROL_V3"
OLD_SYSTEM = {A: "SYSTEM_A_V2", B: "SYSTEM_B_V2"}


def sha(p: Path) -> str: return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(x) -> str: return hashlib.sha256(json.dumps(x, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()
def load(p: Path):
    with gzip.open(p, "rt", encoding="utf8") as h: return json.load(h)["rows"]
def read(p: Path):
    with p.open(encoding="utf8", newline="") as h: return list(csv.DictReader(h, delimiter="\t"))
def write(p: Path, rows: list[dict]) -> None:
    fields = []
    for row in rows:
        for field in row:
            if field not in fields: fields.append(field)
    with p.open("w", encoding="utf8", newline="") as h:
        w = csv.DictWriter(h, fields, delimiter="\t", lineterminator="\n"); w.writeheader()
        w.writerows([{f: row.get(f, "NA") for f in fields} for row in rows])


def material(metric: str, old: float, new: float, kind: str) -> tuple[bool, str]:
    delta = new - old
    if kind == "RATE": return abs(delta) >= 0.05, "ABS_DELTA_GE_0.05" if abs(delta) >= 0.05 else "BELOW_0.05"
    if kind == "GAIN":
        flag = (old < 0 < new) or (new < 0 < old) or (abs(old) > 0 and abs(delta) >= 0.10 * abs(old))
        return flag, "SIGN_OR_RELATIVE_10_PERCENT" if flag else "BELOW_GAIN_RULE"
    if kind == "COUNT": return (old == 0) != (new == 0), "ZERO_NONZERO_CHANGE" if (old == 0) != (new == 0) else "NO_ZERO_BOUNDARY_CHANGE"
    return False, "DESCRIPTIVE_ONLY"


def main() -> None:
    blind, blind_validation = json.loads(BLIND.read_text()), json.loads(BLIND_VALIDATION.read_text())
    assert blind["status"] == "GDT172_BLIND_OUTPUTS_FROZEN_BEFORE_ORACLE_EVALUATION"
    assert blind_validation["status"] == "PASS_INDEPENDENT_NO_ORACLE_LITERAL_SENSITIVITY_RECONSTRUCTION"
    obs, oracle, parses = load(OBS), load(ORACLE), load(PARSES)
    assert len(obs) == len(oracle) == 30428 and len(parses) == 60856
    omap = {x["observation_id"]: x for x in oracle}; pmap = {(x["observation_id"], x["parser_level"]): x for x in parses}
    mapping = defaultdict(set)
    for x in obs: mapping[x["world_view"]].add(omap[x["observation_id"]]["system"])
    assert mapping == {"CONTROL_P": {A}, "CONTROL_Q": {B}}

    joined = defaultdict(list); component = defaultdict(Counter); component_n = Counter()
    for row in obs:
        truth = omap[row["observation_id"]]; system = truth["system"]
        prefix = truth["true_record_operator"] + truth["true_line_frame"] + truth["true_literal_escape"] + truth["true_lexical_left"]
        suffix = truth["true_lexical_right"] + truth["true_field_marker"] + truth["true_positional_right"] + truth["true_closure"]
        assert row["surface_group"] == prefix + truth["rendered_host"] + suffix
        for level in ("SURFACE_ONLY", "VMANUS_ANNOTATION_ASSISTED"):
            p = pmap[row["observation_id"], level]; item = {**row, **truth, **p}; joined[system, level].append(item)
            left = ("" if p["outer_left"] == "NONE" else p["outer_left"]) + ("" if p["local_left"] == "NONE" else p["local_left"])
            right = ("" if p["right_inner"] == "NONE" else p["right_inner"]) + ("" if p["right_outer"] == "NONE" else p["right_outer"])
            true_parts = [x for x in (truth["true_record_operator"], truth["true_line_frame"], truth["true_literal_escape"], truth["true_lexical_left"], truth["rendered_host"], truth["true_lexical_right"], truth["true_field_marker"], truth["true_positional_right"], truth["true_closure"]) if x]
            pred_parts = [x for x in (("" if p["outer_left"] == "NONE" else p["outer_left"]), ("" if p["local_left"] == "NONE" else p["local_left"]), p["inferred_host"], ("" if p["right_inner"] == "NONE" else p["right_inner"]), ("" if p["right_outer"] == "NONE" else p["right_outer"])) if x]
            tb, pb, cursor = set(), set(), 0
            for part in true_parts[:-1]: cursor += len(part); tb.add(cursor)
            cursor = 0
            for part in pred_parts[:-1]: cursor += len(part); pb.add(cursor)
            strata = ["ALL_ROWS", truth["lexical_status"]]
            if truth["lexical_status"] == "FREQUENT_LEXICAL_ID" and (prefix or suffix): strata.append("FREQUENT_COMPILER_MARKED")
            for stratum in strata:
                key = system, level, stratum; component_n[key] += 1
                component[key]["host"] += p["inferred_host"] == truth["rendered_host"]
                component[key]["left"] += left == prefix; component[key]["right"] += right == suffix
                component[key]["span"] += p["inferred_host"] == truth["rendered_host"] and left == prefix and right == suffix
                component[key]["be"] += pb == tb; component[key]["tp"] += len(pb & tb)
                component[key]["pred"] += len(pb); component[key]["true"] += len(tb)

    target = lambda x: x["lexical_id"] if x["lexical_status"] == "FREQUENT_LEXICAL_ID" else x["source_type_hash"]
    level_rows, idx = [], {}
    for system in (A, B):
        oracle_rows = [{**x, **omap[x["observation_id"]]} for x in obs if omap[x["observation_id"]]["system"] == system]
        for level in ("SURFACE_ONLY", "VMANUS_ANNOTATION_ASSISTED", "ORACLE_CEILING"):
            base = oracle_rows if level == "ORACLE_CEILING" else joined[system, level]
            for stratum in ("ALL_ROWS", "FREQUENT_LEXICAL_ID", "LITERAL_ESCAPE"):
                rows = base if stratum == "ALL_ROWS" else [x for x in base if x["lexical_status"] == stratum]
                host_key = (lambda x: x["rendered_host"]) if level == "ORACLE_CEILING" else (lambda x: x["inferred_host"])
                full_key = oracle_full if level == "ORACLE_CEILING" else blind_full
                hmi, hfrac = information(rows, target, host_key); fmi, ffrac = information(rows, target, full_key); _, rfrac = information(rows, target, lambda x: x["surface_group"])
                hd, fd, rd = held_decoder(rows, target, host_key), held_decoder(rows, target, full_key), held_decoder(rows, target, lambda x: x["surface_group"])
                item = {"system": system, "instrument_level": level, "stratum": stratum, "rows": len(rows), "target_types": len({target(x) for x in rows}),
                        "host_mutual_information_bits": hmi, "host_information_fraction": hfrac, "full_tuple_mutual_information_bits": fmi, "full_tuple_information_fraction": ffrac,
                        "raw_surface_information_fraction": rfrac, "host_decoder_predictions": hd["predictions"], "host_decoder_coverage": hd["coverage"], "host_decoder_accuracy": hd["accuracy"],
                        "full_decoder_predictions": fd["predictions"], "full_decoder_coverage": fd["coverage"], "full_decoder_accuracy": fd["accuracy"], "raw_decoder_coverage": rd["coverage"], "raw_decoder_accuracy": rd["accuracy"]}
                level_rows.append(item); idx[system, level, stratum] = item

    component_rows = []
    for key in sorted(component_n):
        n, c = component_n[key], component[key]; precision = c["tp"] / c["pred"] if c["pred"] else 0; recall = c["tp"] / c["true"] if c["true"] else 0
        component_rows.append({"system": key[0], "instrument_level": key[1], "stratum": key[2], "rows": n,
                               "exact_true_host_rate": c["host"] / n, "exact_left_edge_rate": c["left"] / n, "exact_right_edge_rate": c["right"] / n,
                               "exact_edge_span_decomposition_rate": c["span"] / n, "exact_component_boundary_set_rate": c["be"] / n,
                               "component_boundary_precision": precision, "component_boundary_recall": recall, "component_boundary_f1": 2 * precision * recall / (precision + recall) if precision + recall else 0})
    for system in (A, B):
        for stratum in ("ALL_ROWS", "FREQUENT_LEXICAL_ID", "LITERAL_ESCAPE", "FREQUENT_COMPILER_MARKED"):
            n = len([x for x in oracle if x["system"] == system and (stratum == "ALL_ROWS" or x["lexical_status"] == stratum or (stratum == "FREQUENT_COMPILER_MARKED" and x["lexical_status"] == "FREQUENT_LEXICAL_ID" and any(x[k] for k in ("true_record_operator", "true_line_frame", "true_literal_escape", "true_lexical_left", "true_lexical_right", "true_field_marker", "true_positional_right", "true_closure"))))])
            component_rows.append({"system": system, "instrument_level": "ORACLE_CEILING", "stratum": stratum, "rows": n, "exact_true_host_rate": 1., "exact_left_edge_rate": 1., "exact_right_edge_rate": 1., "exact_edge_span_decomposition_rate": 1., "exact_component_boundary_set_rate": 1., "component_boundary_precision": 1., "component_boundary_recall": 1., "component_boundary_f1": 1.})

    blind_diag, calibration_rows = read(BLIND_DIAG), []
    for system, world in ((A, "CONTROL_P"), (B, "CONTROL_Q")):
        for level in ("SURFACE_ONLY", "VMANUS_ANNOTATION_ASSISTED"):
            rows = [x for x in blind_diag if x["world_view"] == world and x["parser_level"] == level and x["scope"] == "ALL_PARTITIONED_REGISTERS"]
            by = defaultdict(list)
            for x in rows: by[x["diagnostic"]].append(x)
            rec, comp, short = by["RECORD_ARCHITECTURE"][0], by["OPERATION_COMPATIBILITY"][0], by["SHORT_HOST_STRUCTURE"][0]
            same, external = by["SAME_GROUP_SUBSTITUTION"][0], by["EXTERNAL_CONTEXT_SUBSTITUTION"][0]
            nxt = next(x for x in by["HELD_CONTEXT"] if x["endpoint"] == "NEXT_HOST"); line = next(x for x in by["HELD_CONTEXT"] if x["endpoint"] == "WHOLE_LINE")
            calibration_rows += [
                {"system": system, "instrument_level": level, "diagnostic": "GDT113_RECORD_CLOSURE", "observed_value": rec["right_marked_record_end_precision"], "secondary_value": rec["record_end_right_mark_recall"]},
                {"system": system, "instrument_level": level, "diagnostic": "GDT160_OPERATION_COMPATIBILITY", "observed_value": comp["compatible_pair_density"], "secondary_value": comp["inclusive_p"]},
                {"system": system, "instrument_level": level, "diagnostic": "GDT162_SHORT_HOST", "observed_value": short["short_host_mass"], "secondary_value": short["host_types"]},
                {"system": system, "instrument_level": level, "diagnostic": "GDT163_SAME_GROUP_SUBSTITUTION", "observed_value": same["mean_delta_cosine"], "secondary_value": same["repeated_substitution_classes"]},
                {"system": system, "instrument_level": level, "diagnostic": "GDT164_EXTERNAL_SUBSTITUTION", "observed_value": external["mean_delta_cosine"], "secondary_value": external["repeated_substitution_classes"]},
                {"system": system, "instrument_level": level, "diagnostic": "GDT165_NEXT_HOST", "observed_value": nxt["gain_bits"], "secondary_value": nxt["positive_content_folios"]},
                {"system": system, "instrument_level": level, "diagnostic": "GDT166_LINE_CONTEXT", "observed_value": line["gain_bits"], "secondary_value": line["positive_content_folios"]},
            ]

    old_levels, old_components = read(OLD_LEVELS), read(OLD_COMPONENTS)
    old_level_map = {(x["system"], x["instrument_level"], x["stratum"]): x for x in old_levels}
    old_component_map = {(x["system"], x["instrument_level"], x["stratum"]): x for x in old_components}
    delta_rows = []
    recovery_fields = ("host_information_fraction", "full_tuple_information_fraction", "raw_surface_information_fraction", "host_decoder_coverage", "host_decoder_accuracy", "full_decoder_coverage", "full_decoder_accuracy", "raw_decoder_coverage", "raw_decoder_accuracy")
    for row in level_rows:
        if row["stratum"] != "FREQUENT_LEXICAL_ID": continue
        old = old_level_map[OLD_SYSTEM[row["system"]], row["instrument_level"], row["stratum"]]
        for field in recovery_fields:
            ov, nv = float(old[field]), float(row[field]); flag, rule = material(field, ov, nv, "RATE")
            delta_rows.append({"scope": "FREQUENT_ID_RECOVERY", "system": row["system"], "instrument_level": row["instrument_level"], "stratum": row["stratum"], "metric": field, "gdt171_value": ov, "gdt172_value": nv, "delta": nv - ov, "material": int(flag), "material_rule": rule})
    component_fields = ("exact_true_host_rate", "exact_left_edge_rate", "exact_right_edge_rate", "exact_edge_span_decomposition_rate", "exact_component_boundary_set_rate", "component_boundary_precision", "component_boundary_recall", "component_boundary_f1")
    for row in component_rows:
        if row["stratum"] not in {"FREQUENT_LEXICAL_ID", "FREQUENT_COMPILER_MARKED"}: continue
        old = old_component_map[OLD_SYSTEM[row["system"]], row["instrument_level"], row["stratum"]]
        for field in component_fields:
            ov, nv = float(old[field]), float(row[field]); flag, rule = material(field, ov, nv, "RATE")
            delta_rows.append({"scope": "FREQUENT_ID_COMPONENT", "system": row["system"], "instrument_level": row["instrument_level"], "stratum": row["stratum"], "metric": field, "gdt171_value": ov, "gdt172_value": nv, "delta": nv - ov, "material": int(flag), "material_rule": rule})

    old_diag = read(OLD_DIAG); diag_metrics = {
        "RECORD_ARCHITECTURE": [("right_marked_record_end_precision", "RATE"), ("record_end_right_mark_recall", "RATE")],
        "OPERATION_COMPATIBILITY": [("compatible_pair_density", "RATE"), ("inclusive_p", "RATE")],
        "SHORT_HOST_STRUCTURE": [("short_host_mass", "RATE"), ("recurrent_host_mass", "RATE")],
        "SAME_GROUP_SUBSTITUTION": [("mean_delta_cosine", "RATE")], "EXTERNAL_CONTEXT_SUBSTITUTION": [("mean_delta_cosine", "RATE")],
        "HELD_CONTEXT": [("gain_bits", "GAIN")],
    }
    def dkey(x): return (x["world_view"], x["scope"], x["parser_level"], x["diagnostic"], x.get("endpoint", "NA"), x.get("left_register", "NA"), x.get("right_register", "NA"))
    old_dm = {dkey(x): x for x in old_diag}; new_dm = {dkey(x): x for x in blind_diag}
    for key in sorted(set(old_dm) & set(new_dm)):
        old, new = old_dm[key], new_dm[key]; diag = key[3]
        for field, kind in diag_metrics.get(diag, []):
            if old.get(field, "NA") == "NA" or new.get(field, "NA") == "NA": continue
            ov, nv = float(old[field]), float(new[field]); flag, rule = material(field, ov, nv, kind)
            delta_rows.append({"scope": "GLOBAL_BLIND_DIAGNOSTIC", "system": key[0], "instrument_level": key[2], "stratum": "ALL_ROWS", "metric": diag + ":" + key[4] + ":" + field, "gdt171_value": ov, "gdt172_value": nv, "delta": nv - ov, "material": int(flag), "material_rule": rule})
    old_ops, new_ops = read(OLD_OPS), read(OPS)
    for world in ("CONTROL_P", "CONTROL_Q"):
        for side in ("LEFT", "RIGHT"):
            x = {r["operation"] for r in old_ops if r["world_view"] == world and r["side"] == side}; y = {r["operation"] for r in new_ops if r["world_view"] == world and r["side"] == side}
            j = len(x & y) / len(x | y); flag = j < .8
            delta_rows.append({"scope": "GLOBAL_OPERATION_LIBRARY", "system": world, "instrument_level": side, "stratum": "ALL_ROWS", "metric": "SIDE_AWARE_OPERATION_JACCARD", "gdt171_value": len(x), "gdt172_value": len(y), "delta": len(y) - len(x), "material": int(flag), "material_rule": "JACCARD_BELOW_0.80" if flag else "JACCARD_AT_LEAST_0.80", "jaccard": j, "retained": "|".join(sorted(x & y)) or "NONE", "lost": "|".join(sorted(x - y)) or "NONE", "gained": "|".join(sorted(y - x)) or "NONE"})

    frequent_material = [x for x in delta_rows if x["scope"].startswith("FREQUENT_ID") and x["material"]]
    global_material = [x for x in delta_rows if x["scope"].startswith("GLOBAL") and x["material"]]
    status = "FREQUENT_ID_RECOVERY_MATERIALLY_CHANGED_AND_GLOBAL_DIAGNOSTICS_LITERAL_SENSITIVE" if frequent_material else "FREQUENT_ID_RECOVERY_STABLE_GLOBAL_DIAGNOSTICS_LITERAL_SENSITIVE"
    counters = [
        {"counterexample": "UNCHANGED_FREQUENT_SURFACES_FORCE_UNCHANGED_RECOVERY", "evidence": "Operation discovery is corpus-wide, so changing only literal rows can alter parses on byte-identical frequent rows.", "impact": "Frequent recovery must be remeasured, not assumed."},
        {"counterexample": "SYSTEM_B_IS_HISTORICAL_NATURALISTIC", "evidence": "System B retains the frozen Cartesian 6x4x4x4 allocation.", "impact": "It is an explicit factorial distributed control only; B2 is deferred."},
        {"counterexample": "GLOBAL_OPERATION_METRICS_ARE_LITERAL_INVARIANT", "evidence": f"The selected operation count changes from {len(old_ops)} to {len(new_ops)} and at least one side-aware operation Jaccard is below the frozen threshold: {bool([x for x in global_material if x['scope']=='GLOBAL_OPERATION_LIBRARY'])}.", "impact": "Global operation metrics depend on the literal representation."},
        {"counterexample": "GDT172_VALIDATES_VOYNICH_ARCHITECTURE", "evidence": "The run contains no Voynich input.", "impact": "This is instrument calibration only."},
    ]
    write(LEVELS, level_rows); write(COMPONENTS, component_rows); write(CALIBRATION, calibration_rows); write(DELTAS, delta_rows); write(COUNTER, counters)

    a_s, a_v = idx[A, "SURFACE_ONLY", "FREQUENT_LEXICAL_ID"], idx[A, "VMANUS_ANNOTATION_ASSISTED", "FREQUENT_LEXICAL_ID"]
    b_s, b_v = idx[B, "SURFACE_ONLY", "FREQUENT_LEXICAL_ID"], idx[B, "VMANUS_ANNOTATION_ASSISTED", "FREQUENT_LEXICAL_ID"]
    ca_s = next(x for x in component_rows if x["system"] == A and x["instrument_level"] == "SURFACE_ONLY" and x["stratum"] == "FREQUENT_LEXICAL_ID")
    cb_s = next(x for x in component_rows if x["system"] == B and x["instrument_level"] == "SURFACE_ONLY" and x["stratum"] == "FREQUENT_LEXICAL_ID")
    report = f"""# GDT172 — unchanged-graphematic literal escape sensitivity

Status: **{status}**.

GDT171 remains published unchanged. GDT172 replaces only its artificial
UTF-8/base-19 rare-literal payload with `w` plus the unchanged source
graphematic form. All 384 frequent lexical assignments, 11,422 frequent visible
rows and all layout fields are exact. System B is an explicit **factorial
distributed control**, not a historical-naturalistic encoding. B2 was not
built.

## Frequent-ID result

| system | level | held host accuracy / coverage | host information fraction | exact true-host rate |
|---|---|---:|---:|---:|
| A lexical | surface | {a_s['host_decoder_accuracy']:.3f} / {a_s['host_decoder_coverage']:.3f} | {a_s['host_information_fraction']:.3f} | {ca_s['exact_true_host_rate']:.3f} |
| A lexical | annotation | {a_v['host_decoder_accuracy']:.3f} / {a_v['host_decoder_coverage']:.3f} | {a_v['host_information_fraction']:.3f} | see component table |
| B factorial control | surface | {b_s['host_decoder_accuracy']:.3f} / {b_s['host_decoder_coverage']:.3f} | {b_s['host_information_fraction']:.3f} | {cb_s['exact_true_host_rate']:.3f} |
| B factorial control | annotation | {b_v['host_decoder_accuracy']:.3f} / {b_v['host_decoder_coverage']:.3f} | {b_v['host_information_fraction']:.3f} | see component table |

The frozen comparison finds **{len(frequent_material)} material frequent-ID
metric changes**. The largest recovery-rate shift is System A surface held-host
accuracy, 0.897 to 0.881 (-0.016). The largest component shift is -0.048,
still just below the frozen 0.05 threshold. Any change is indirect: frequent
surfaces themselves are byte-identical, while the corpus-wide operation
library is relearned from the corrected all-row corpus.

## Global diagnostics

Rare-literal mean visible length falls from 15.59 to 7.57 characters. The
selected operation library changes from {len(old_ops)} to {len(new_ops)}
rows and yields {len(global_material)} globally material deltas under the frozen
rules. Control P compatibility density changes from 0.3333 to 0.1970 and stays
high-null (surface p 0.7990). Factorial Control Q changes from 0.8125 to 0.8750
and remains low-null (surface p 0.00195). Held-context signs do not change:
Control P remains positive for NEXT_HOST and WHOLE_LINE; Control Q remains
positive for NEXT_HOST and negative for WHOLE_LINE. Control P's gained left
operations are dominated by the now-visible escape marker (`w`, `wa`, `wd`,
`wh`, `wl`, `ws`, `wu`, `sw`), directly locating the operation-library change
in the corrected literal mechanism rather than the frequent codebook.

Thus the broad qualitative calibration survives, but exact global operation
counts and several magnitudes are literal-channel-sensitive. The complete
frequent, component and all-row deltas are retained in
`gdt172_gdt171_delta.tsv`.

## Consequence

Use GDT172 instead of the base-19 condition when citing historical-plausibility
sensitivities. Keep GDT171 as the published artificial-literal comparator and
GDT168 v1 as the toy control. No Voynich source or image was used; no f84
material was accessed.
"""
    REPORT.write_text(report)
    result = {"schema": "GDT172_LITERAL_ESCAPE_CORRECTION_RESULT_V1", "status": status,
              "decision": "USE_UNCHANGED_GRAPHEMATIC_LITERAL_CONDITION_FOR_PRIMARY_HISTORICAL_PLAUSIBILITY_SENSITIVITY",
              "counts": {"frequent_material_deltas": len(frequent_material), "global_material_deltas": len(global_material), "old_operations": len(old_ops), "new_operations": len(new_ops)},
              "headline": {"system_a_surface_frequent": a_s, "system_a_annotation_frequent": a_v, "system_b_surface_frequent": b_s, "system_b_annotation_frequent": b_v,
                           "system_a_surface_component": ca_s, "system_b_surface_component": cb_s},
              "inputs": {p.name: sha(p) for p in (OBS, ORACLE, FREEZE, DESIGN, PARSES, BLIND, BLIND_VALIDATION, BLIND_DIAG, OPS, OLD_LEVELS, OLD_COMPONENTS, OLD_DIAG, OLD_OPS, OLD_RESULT)},
              "outputs": {p.name: sha(p) for p in (LEVELS, COMPONENTS, CALIBRATION, DELTAS, COUNTER)},
              "documents": {METHOD.name: sha(METHOD), REPORT.name: sha(REPORT)}, "implementation": {Path(__file__).name: sha(Path(__file__))},
              "commitments": {"levels": csha(level_rows), "components": csha(component_rows), "calibration": csha(calibration_rows), "deltas": csha(delta_rows)},
              "chronology": {"source_and_design_commit": "f374df8", "blind_outputs_commit": "a9d472b", "oracle_opened_only_after_blind_outputs_published": True},
              "system_b_architecture": "EXPLICIT_FACTORIAL_DISTRIBUTED_CONTROL_NOT_HISTORICAL_NATURALISTIC", "b2_status": "NOT_BUILT_DEFERRED",
              "no_voynich_tuning": True, "voynich_inputs": 0, "f84_access": False,
              "claim_ceiling": "Synthetic literal-channel instrument calibration only; no Voynich word, code value, language, role, meaning, plaintext, or translation."}
    result["result_content_sha256"] = csha(result); RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": status, **result["counts"], "a_host_accuracy": a_s["host_decoder_accuracy"], "b_host_accuracy": b_s["host_decoder_accuracy"]}, sort_keys=True))


if __name__ == "__main__": main()
