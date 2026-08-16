#!/usr/bin/env python3
"""Unblind frozen GDT171 outputs and measure historical-v2 instrument recovery."""
from __future__ import annotations

import csv
import gzip
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

R = Path(__file__).resolve().parent
OBS = R / "gdt171_observation_corpus.json.gz"
ORACLE = R / "gdt171_sealed_oracle.json.gz"
SOURCE_FREEZE = R / "gdt171_source_observation_oracle_freeze.json"
DESIGN = R / "gdt171_blind_design.json"
PARSES = R / "gdt171_blind_parses.json.gz"
BLIND_RESULT = R / "gdt171_blind_result.json"
BLIND_VALIDATION = R / "gdt171_blind_validation.json"
BLIND_DIAG = R / "gdt171_blind_diagnostics.tsv"
METHOD = R / "GDT171_HISTORICAL_PLAUSIBILITY_INSTRUMENT_METHOD.md"
LEVELS = R / "gdt171_recovery_levels.tsv"
COMPONENTS = R / "gdt171_component_recovery.tsv"
CALIBRATION = R / "gdt171_diagnostic_calibration.tsv"
COUNTER = R / "gdt171_counterexamples.tsv"
REPORT = R / "GDT171_HISTORICAL_PLAUSIBILITY_INSTRUMENT_REPORT.md"
RESULT = R / "gdt171_result.json"


def sha(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()
def csha(x) -> str: return hashlib.sha256(json.dumps(x, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()


def load(path: Path):
    with gzip.open(path, "rt", encoding="utf8") as handle: return json.load(handle)["rows"]


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf8", newline="") as handle: return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict]) -> None:
    fields = []
    for row in rows:
        for field in row:
            if field not in fields: fields.append(field)
    with path.open("w", encoding="utf8", newline="") as handle:
        writer = csv.DictWriter(handle, fields, delimiter="\t", lineterminator="\n"); writer.writeheader()
        writer.writerows([{field: row.get(field, "NA") for field in fields} for row in rows])


def entropy(c: Counter) -> float:
    n = sum(c.values()); return -sum(v / n * math.log2(v / n) for v in c.values() if v) if n else 0.0


def information(rows: list[dict], target, key) -> tuple[float, float]:
    h = entropy(Counter(target(x) for x in rows)); groups = defaultdict(Counter)
    for row in rows: groups[key(row)][target(row)] += 1
    cond = sum(sum(c.values()) / len(rows) * entropy(c) for c in groups.values())
    return h - cond, (h - cond) / h if h else 0.0


def held_decoder(rows: list[dict], target, key) -> dict:
    covered = correct = total = positive = 0; units = sorted({x["source_unit_full"] for x in rows})
    for held in units:
        maps = defaultdict(Counter)
        for row in rows:
            if row["source_unit_full"] != held: maps[key(row)][target(row)] += 1
        fold_correct = 0
        for row in rows:
            if row["source_unit_full"] != held: continue
            total += 1; k = key(row)
            if k in maps:
                covered += 1; pred = sorted(maps[k].items(), key=lambda z: (-z[1], str(z[0])))[0][0]
                hit = pred == target(row); correct += hit; fold_correct += hit
        positive += fold_correct > 0
    return {"predictions": covered, "correct": correct, "total_rows": total, "coverage": covered / total,
            "accuracy": correct / covered if covered else 0.0, "positive_source_units": positive, "source_units": len(units)}


def blind_full(x: dict):
    return (x["outer_left"], x["local_left"], x["inferred_host"], x["right_inner"], x["right_outer"],
            int(x["group_index"]), int(x["line_ordinal_on_folio"]), int(x["paragraph_start"]), int(x["paragraph_end"]))


def oracle_full(x: dict):
    return (x["true_record_operator"], x["true_line_frame"], x["true_literal_escape"], x["true_lexical_left"],
            x["rendered_host"], x["true_lexical_right"], x["true_field_marker"], x["true_positional_right"], x["true_closure"], int(x["true_record_slot"]))


def main() -> None:
    blind = json.loads(BLIND_RESULT.read_text()); validation = json.loads(BLIND_VALIDATION.read_text())
    assert blind["status"] == "GDT171_BLIND_OUTPUTS_FROZEN_BEFORE_ORACLE_EVALUATION"
    assert validation["status"] == "PASS_INDEPENDENT_NO_ORACLE_V2_BLIND_RECONSTRUCTION"
    obs, oracle, parses = load(OBS), load(ORACLE), load(PARSES)
    assert len(obs) == len(oracle) == 30428 and len(parses) == 60856
    omap = {x["observation_id"]: x for x in oracle}; pmap = {(x["observation_id"], x["parser_level"]): x for x in parses}
    mapping = defaultdict(set)
    for x in obs: mapping[x["world_view"]].add(omap[x["observation_id"]]["system"])
    assert mapping == {"CONTROL_P": {"SYSTEM_A_V2"}, "CONTROL_Q": {"SYSTEM_B_V2"}}

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
            true_parts = [x for x in (truth["true_record_operator"], truth["true_line_frame"], truth["true_literal_escape"],
                                      truth["true_lexical_left"], truth["rendered_host"], truth["true_lexical_right"],
                                      truth["true_field_marker"], truth["true_positional_right"], truth["true_closure"]) if x]
            pred_parts = [x for x in ("" if p["outer_left"] == "NONE" else p["outer_left"],
                                      "" if p["local_left"] == "NONE" else p["local_left"], p["inferred_host"],
                                      "" if p["right_inner"] == "NONE" else p["right_inner"],
                                      "" if p["right_outer"] == "NONE" else p["right_outer"]) if x]
            true_bounds, pred_bounds = set(), set(); cursor = 0
            for part in true_parts[:-1]: cursor += len(part); true_bounds.add(cursor)
            cursor = 0
            for part in pred_parts[:-1]: cursor += len(part); pred_bounds.add(cursor)
            strata = ["ALL_ROWS", truth["lexical_status"]]
            if truth["lexical_status"] == "FREQUENT_LEXICAL_ID" and (prefix or suffix): strata.append("FREQUENT_COMPILER_MARKED")
            for stratum in strata:
                key = system, level, stratum; component_n[key] += 1
                component[key]["host"] += p["inferred_host"] == truth["rendered_host"]
                component[key]["left"] += left == prefix; component[key]["right"] += right == suffix
                component[key]["span"] += p["inferred_host"] == truth["rendered_host"] and left == prefix and right == suffix
                component[key]["boundary_exact"] += pred_bounds == true_bounds
                component[key]["boundary_tp"] += len(pred_bounds & true_bounds)
                component[key]["boundary_pred"] += len(pred_bounds)
                component[key]["boundary_true"] += len(true_bounds)

    level_rows = []; idx = {}
    target = lambda x: x["lexical_id"] if x["lexical_status"] == "FREQUENT_LEXICAL_ID" else x["source_type_hash"]
    for system in ("SYSTEM_A_V2", "SYSTEM_B_V2"):
        oracle_rows = [{**x, **omap[x["observation_id"]]} for x in obs if omap[x["observation_id"]]["system"] == system]
        for level in ("SURFACE_ONLY", "VMANUS_ANNOTATION_ASSISTED", "ORACLE_CEILING"):
            base = oracle_rows if level == "ORACLE_CEILING" else joined[system, level]
            for stratum in ("ALL_ROWS", "FREQUENT_LEXICAL_ID", "LITERAL_ESCAPE"):
                rows = base if stratum == "ALL_ROWS" else [x for x in base if x["lexical_status"] == stratum]
                host_key = (lambda x: x["rendered_host"]) if level == "ORACLE_CEILING" else (lambda x: x["inferred_host"])
                full_key = oracle_full if level == "ORACLE_CEILING" else blind_full
                host_mi, host_fraction = information(rows, target, host_key); full_mi, full_fraction = information(rows, target, full_key)
                raw_mi, raw_fraction = information(rows, target, lambda x: x["surface_group"])
                hd, fd, rd = held_decoder(rows, target, host_key), held_decoder(rows, target, full_key), held_decoder(rows, target, lambda x: x["surface_group"])
                item = {"system": system, "instrument_level": level, "stratum": stratum, "rows": len(rows), "target_types": len({target(x) for x in rows}),
                        "host_mutual_information_bits": host_mi, "host_information_fraction": host_fraction,
                        "full_tuple_mutual_information_bits": full_mi, "full_tuple_information_fraction": full_fraction,
                        "raw_surface_information_fraction": raw_fraction,
                        "host_decoder_predictions": hd["predictions"], "host_decoder_coverage": hd["coverage"], "host_decoder_accuracy": hd["accuracy"],
                        "full_decoder_predictions": fd["predictions"], "full_decoder_coverage": fd["coverage"], "full_decoder_accuracy": fd["accuracy"],
                        "raw_decoder_coverage": rd["coverage"], "raw_decoder_accuracy": rd["accuracy"]}
                level_rows.append(item); idx[system, level, stratum] = item

    component_rows = []
    for key in sorted(component_n):
        n = component_n[key]; c = component[key]
        precision = c["boundary_tp"] / c["boundary_pred"] if c["boundary_pred"] else 0.0
        recall = c["boundary_tp"] / c["boundary_true"] if c["boundary_true"] else 0.0
        component_rows.append({"system": key[0], "instrument_level": key[1], "stratum": key[2], "rows": n,
                               "exact_true_host_rate": c["host"] / n, "exact_left_edge_rate": c["left"] / n,
                               "exact_right_edge_rate": c["right"] / n, "exact_edge_span_decomposition_rate": c["span"] / n,
                               "exact_component_boundary_set_rate": c["boundary_exact"] / n,
                               "component_boundary_precision": precision, "component_boundary_recall": recall,
                               "component_boundary_f1": 2 * precision * recall / (precision + recall) if precision + recall else 0.0})
    for system in ("SYSTEM_A_V2", "SYSTEM_B_V2"):
        for stratum in ("ALL_ROWS", "FREQUENT_LEXICAL_ID", "LITERAL_ESCAPE", "FREQUENT_COMPILER_MARKED"):
            n = len([x for x in oracle if x["system"] == system and (stratum == "ALL_ROWS" or x["lexical_status"] == stratum or
                    (stratum == "FREQUENT_COMPILER_MARKED" and x["lexical_status"] == "FREQUENT_LEXICAL_ID" and
                     any(x[k] for k in ("true_record_operator", "true_line_frame", "true_literal_escape", "true_lexical_left", "true_lexical_right", "true_field_marker", "true_positional_right", "true_closure"))))])
            component_rows.append({"system": system, "instrument_level": "ORACLE_CEILING", "stratum": stratum, "rows": n,
                                   "exact_true_host_rate": 1.0, "exact_left_edge_rate": 1.0, "exact_right_edge_rate": 1.0,
                                   "exact_edge_span_decomposition_rate": 1.0, "exact_component_boundary_set_rate": 1.0,
                                   "component_boundary_precision": 1.0, "component_boundary_recall": 1.0, "component_boundary_f1": 1.0})

    blind_diag = read(BLIND_DIAG); calibration_rows = []
    for system, world in (("SYSTEM_A_V2", "CONTROL_P"), ("SYSTEM_B_V2", "CONTROL_Q")):
        for level in ("SURFACE_ONLY", "VMANUS_ANNOTATION_ASSISTED"):
            rows = [x for x in blind_diag if x["world_view"] == world and x["parser_level"] == level and x["scope"] == "ALL_PARTITIONED_REGISTERS"]
            by = defaultdict(list)
            for x in rows: by[x["diagnostic"]].append(x)
            rec, comp, short = by["RECORD_ARCHITECTURE"][0], by["OPERATION_COMPATIBILITY"][0], by["SHORT_HOST_STRUCTURE"][0]
            same, external = by["SAME_GROUP_SUBSTITUTION"][0], by["EXTERNAL_CONTEXT_SUBSTITUTION"][0]
            nxt = next(x for x in by["HELD_CONTEXT"] if x["endpoint"] == "NEXT_HOST"); line = next(x for x in by["HELD_CONTEXT"] if x["endpoint"] == "WHOLE_LINE")
            calibration_rows.extend([
                {"system": system, "instrument_level": level, "diagnostic": "GDT113_RECORD_CLOSURE", "known_property": "OPTIONAL_POSITIONAL_CLOSURE_PRESENT", "observed_value": rec["right_marked_record_end_precision"], "secondary_value": rec["record_end_right_mark_recall"]},
                {"system": system, "instrument_level": level, "diagnostic": "GDT160_OPERATION_COMPATIBILITY", "known_property": "SEPARATE_FIELDS_PRESENT", "observed_value": comp["compatible_pair_density"], "secondary_value": comp["inclusive_p"]},
                {"system": system, "instrument_level": level, "diagnostic": "GDT162_SHORT_HOST", "known_property": "FREQUENT_HOST_LENGTH_2_OR_3_LITERAL_HOSTS_LONG", "observed_value": short["short_host_mass"], "secondary_value": short["host_types"]},
                {"system": system, "instrument_level": level, "diagnostic": "GDT163_SAME_GROUP_SUBSTITUTION", "known_property": "DISTRIBUTED_TABLE" if system == "SYSTEM_B_V2" else "LEXICAL_CODEBOOK", "observed_value": same["mean_delta_cosine"], "secondary_value": same["repeated_substitution_classes"]},
                {"system": system, "instrument_level": level, "diagnostic": "GDT164_EXTERNAL_SUBSTITUTION", "known_property": "NO_PRODUCTIVE_EXTERNAL_SUBSTITUTION_OPERATOR", "observed_value": external["mean_delta_cosine"], "secondary_value": external["repeated_substitution_classes"]},
                {"system": system, "instrument_level": level, "diagnostic": "GDT165_NEXT_HOST", "known_property": "REAL_MEDICAL_SOURCE_ORDER", "observed_value": nxt["gain_bits"], "secondary_value": nxt["positive_content_folios"]},
                {"system": system, "instrument_level": level, "diagnostic": "GDT166_LINE_CONTEXT", "known_property": "REAL_MEDICAL_SOURCE_LINE_CONTEXT", "observed_value": line["gain_bits"], "secondary_value": line["positive_content_folios"]},
            ])

    counters = [
        {"counterexample": "GDT168_V1_RESULT_GENERALIZES_UNCHANGED", "evidence": "The v2 lexical world has strong positive held context, unlike v1, because content is not copied ten times and the vocabulary is bounded.", "impact": "Instrument calibration is highly generator-sensitive."},
        {"counterexample": "HIGH_COMPATIBILITY_IS_LEXICAL_CODEBOOK_EVIDENCE", "evidence": "The explicit distributed table has much higher compatible-pair density than the lexical codebook.", "impact": "Compatibility remains a distributed-notation signal, not lexical proof."},
        {"counterexample": "ANNOTATION_ASSISTANCE_ALWAYS_IMPROVES_HOST_RECOVERY", "evidence": "Layout weighting favors precise closures but can retain fewer true lexical host boundaries.", "impact": "Boundary annotations and lexical segmentation must be evaluated separately."},
        {"counterexample": "EVERY_SOURCE_FORM_REQUIRES_A_LEXICAL_ID", "evidence": "Only 384 recurrent forms receive lexical IDs; all others are losslessly transmitted through one literal mechanism.", "impact": "Rare-type capacity no longer masquerades as a huge semantic vocabulary."},
        {"counterexample": "ORACLE_CEILING_IS_BLIND_RECOVERY", "evidence": "The oracle contains the exact lookup and fields by construction.", "impact": "Only the surface and annotation levels measure end-to-end recoverability."},
    ]
    write(LEVELS, level_rows); write(COMPONENTS, component_rows); write(CALIBRATION, calibration_rows); write(COUNTER, counters)

    a_s = idx["SYSTEM_A_V2", "SURFACE_ONLY", "FREQUENT_LEXICAL_ID"]; a_v = idx["SYSTEM_A_V2", "VMANUS_ANNOTATION_ASSISTED", "FREQUENT_LEXICAL_ID"]; a_o = idx["SYSTEM_A_V2", "ORACLE_CEILING", "FREQUENT_LEXICAL_ID"]
    b_s = idx["SYSTEM_B_V2", "SURFACE_ONLY", "FREQUENT_LEXICAL_ID"]; b_v = idx["SYSTEM_B_V2", "VMANUS_ANNOTATION_ASSISTED", "FREQUENT_LEXICAL_ID"]; b_o = idx["SYSTEM_B_V2", "ORACLE_CEILING", "FREQUENT_LEXICAL_ID"]
    ca_s = next(x for x in component_rows if x["system"] == "SYSTEM_A_V2" and x["instrument_level"] == "SURFACE_ONLY" and x["stratum"] == "FREQUENT_LEXICAL_ID")
    ca_v = next(x for x in component_rows if x["system"] == "SYSTEM_A_V2" and x["instrument_level"] == "VMANUS_ANNOTATION_ASSISTED" and x["stratum"] == "FREQUENT_LEXICAL_ID")
    cb_s = next(x for x in component_rows if x["system"] == "SYSTEM_B_V2" and x["instrument_level"] == "SURFACE_ONLY" and x["stratum"] == "FREQUENT_LEXICAL_ID")
    cb_v = next(x for x in component_rows if x["system"] == "SYSTEM_B_V2" and x["instrument_level"] == "VMANUS_ANNOTATION_ASSISTED" and x["stratum"] == "FREQUENT_LEXICAL_ID")
    ca_sm = next(x for x in component_rows if x["system"] == "SYSTEM_A_V2" and x["instrument_level"] == "SURFACE_ONLY" and x["stratum"] == "FREQUENT_COMPILER_MARKED")
    ca_vm = next(x for x in component_rows if x["system"] == "SYSTEM_A_V2" and x["instrument_level"] == "VMANUS_ANNOTATION_ASSISTED" and x["stratum"] == "FREQUENT_COMPILER_MARKED")
    cb_sm = next(x for x in component_rows if x["system"] == "SYSTEM_B_V2" and x["instrument_level"] == "SURFACE_ONLY" and x["stratum"] == "FREQUENT_COMPILER_MARKED")
    cb_vm = next(x for x in component_rows if x["system"] == "SYSTEM_B_V2" and x["instrument_level"] == "VMANUS_ANNOTATION_ASSISTED" and x["stratum"] == "FREQUENT_COMPILER_MARKED")
    report = f"""# GDT171 — historical-plausibility instrument calibration report

Status: **HISTORICAL_V2_PARTIALLY_RECOVERED_BUT_COMPONENT_SENSITIVITY_LIMITED**.

GDT168 v1 remains unchanged. GDT171 replaces its 6,175 pseudo-concepts,
fixed 18/6 layout, alphabet permutations and ten complete content copies with
384 recurring lexical IDs, literal escape, real source order, variable physical
records/lines, partitioned registers, partial overlap and shared-alphabet hands.
World B is an explicit 384-row table, not a modulo cipher.

## Frequent lexical-ID recovery

| world | level | host information | held host accuracy / coverage | held full accuracy / coverage | exact host boundary (all frequent) | exact component-boundary set (compiler-marked) |
|---|---|---:|---:|---:|---:|---:|
| A lexical codebook | surface | {a_s['host_information_fraction']:.3f} | {a_s['host_decoder_accuracy']:.3f} / {a_s['host_decoder_coverage']:.3f} | {a_s['full_decoder_accuracy']:.3f} / {a_s['full_decoder_coverage']:.3f} | {ca_s['exact_true_host_rate']:.3f} | {ca_sm['exact_component_boundary_set_rate']:.3f} |
| A lexical codebook | annotation | {a_v['host_information_fraction']:.3f} | {a_v['host_decoder_accuracy']:.3f} / {a_v['host_decoder_coverage']:.3f} | {a_v['full_decoder_accuracy']:.3f} / {a_v['full_decoder_coverage']:.3f} | {ca_v['exact_true_host_rate']:.3f} | {ca_vm['exact_component_boundary_set_rate']:.3f} |
| A lexical codebook | oracle | {a_o['host_information_fraction']:.3f} | {a_o['host_decoder_accuracy']:.3f} / {a_o['host_decoder_coverage']:.3f} | {a_o['full_decoder_accuracy']:.3f} / {a_o['full_decoder_coverage']:.3f} | 1.000 | 1.000 |
| B distributed table | surface | {b_s['host_information_fraction']:.3f} | {b_s['host_decoder_accuracy']:.3f} / {b_s['host_decoder_coverage']:.3f} | {b_s['full_decoder_accuracy']:.3f} / {b_s['full_decoder_coverage']:.3f} | {cb_s['exact_true_host_rate']:.3f} | {cb_sm['exact_component_boundary_set_rate']:.3f} |
| B distributed table | annotation | {b_v['host_information_fraction']:.3f} | {b_v['host_decoder_accuracy']:.3f} / {b_v['host_decoder_coverage']:.3f} | {b_v['full_decoder_accuracy']:.3f} / {b_v['full_decoder_coverage']:.3f} | {cb_v['exact_true_host_rate']:.3f} | {cb_vm['exact_component_boundary_set_rate']:.3f} |
| B distributed table | oracle | {b_o['host_information_fraction']:.3f} | {b_o['host_decoder_accuracy']:.3f} / {b_o['host_decoder_coverage']:.3f} | {b_o['full_decoder_accuracy']:.3f} / {b_o['full_decoder_coverage']:.3f} | 1.000 | 1.000 |

## Diagnostic calibration

The historically plausible controls produce signals missing from v1.  The
lexical world has positive held next-host and whole-line context.  The
distributed world has a much denser compatible-operation graph, but its
whole-line context is negative.  Layout assistance makes lexical-world right
marks almost perfectly specific to record endings, while the distributed
world's lexical right/field layers confound that endpoint.

This means the normal pipeline has real partial sensitivity when the lexical
inventory is recurrent and register content is not copied wholesale.  It still
does not simply recover the encoder: exact host and full-component rates stay
well below the oracle, annotation assistance can trade host recovery for
closure precision, and literal escapes dominate the all-row corpus.  The
separate literal rows in the artifacts prevent that mechanism from being
misreported as a 6,175-entry vocabulary.

The component-boundary column is restricted to compiler-marked frequent rows;
bare-host rows are excluded so a trivially boundary-free group cannot count as
a successful decomposition.  Full precision/recall/F1 and the corresponding
literal/all-row sensitivities are retained in `gdt171_component_recovery.tsv`.

## Consequence

GDT170's zero component recovery was partly a v1 generator pathology, not a
universal parser verdict.  GDT171 is the more relevant calibration for a
bounded medieval technical lexicon with literal exceptions.  Positive held
context is compatible with a genuine lexical-ID layer; high left-right
compatibility is compatible with distributed notation.  Neither pattern alone
identifies Voynich architecture, and oracle ceilings remain non-blind.

No Voynich source or image was used. f84r was not accessed.
"""
    REPORT.write_text(report, encoding="utf8")
    result = {"schema": "GDT171_HISTORICAL_PLAUSIBILITY_INSTRUMENT_RESULT_V1",
              "status": "HISTORICAL_V2_PARTIALLY_RECOVERED_BUT_COMPONENT_SENSITIVITY_LIMITED",
              "decision": "USE_GDT171_AS_PRIMARY_SYNTHETIC_INSTRUMENT_CALIBRATION_KEEP_GDT168_V1_AS_TOY_CONTROL",
              "headline": {"system_a_surface_frequent": a_s, "system_a_annotation_frequent": a_v,
                           "system_b_surface_frequent": b_s, "system_b_annotation_frequent": b_v,
                           "system_a_surface_component": ca_s, "system_b_surface_component": cb_s,
                           "system_a_surface_marked_component": ca_sm, "system_b_surface_marked_component": cb_sm},
              "inputs": {p.name: sha(p) for p in (OBS, ORACLE, SOURCE_FREEZE, DESIGN, PARSES, BLIND_RESULT, BLIND_VALIDATION, BLIND_DIAG)},
              "outputs": {p.name: sha(p) for p in (LEVELS, COMPONENTS, CALIBRATION, COUNTER)},
              "documents": {METHOD.name: sha(METHOD), REPORT.name: sha(REPORT)}, "implementation": {Path(__file__).name: sha(Path(__file__))},
              "commitments": {"level_content_sha256": csha(level_rows), "component_content_sha256": csha(component_rows), "calibration_content_sha256": csha(calibration_rows)},
              "chronology": {"source_freeze_commit": "0ac0569", "blind_design_commit": "a639c9d", "blind_outputs_commit": "3e48f28", "oracle_opened_only_after_blind_outputs_published": True},
              "no_voynich_tuning": True, "voynich_inputs": 0, "f84r_access": False,
              "claim_ceiling": "Synthetic historical-plausibility instrument calibration only; no Voynich word, code value, language, role, meaning, plaintext, or translation."}
    result["result_content_sha256"] = csha(result); RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": result["status"], "a_surface_host_exact": ca_s["exact_true_host_rate"],
                      "b_surface_host_exact": cb_s["exact_true_host_rate"], "a_host_accuracy": a_s["host_decoder_accuracy"],
                      "b_full_accuracy": b_s["full_decoder_accuracy"]}, sort_keys=True))


if __name__ == "__main__": main()
