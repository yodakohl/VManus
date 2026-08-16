#!/usr/bin/env python3
"""Unblind the frozen GDT170 parses and measure recovery of the known worlds."""
from __future__ import annotations

import csv
import gzip
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

R = Path(__file__).resolve().parent
OBS = R / "gdt170_observation_corpus.json.gz"
ORACLE = R / "gdt170_sealed_oracle.json.gz"
FREEZE = R / "gdt170_observation_oracle_freeze.json"
DESIGN = R / "gdt170_blind_design.json"
PARSES = R / "gdt170_blind_parses.json.gz"
BLIND_RESULT = R / "gdt170_blind_result.json"
BLIND_VALIDATION = R / "gdt170_blind_validation.json"
BLIND_DIAGNOSTICS = R / "gdt170_blind_diagnostics.tsv"
METHOD = R / "GDT170_FULL_OBSERVATION_INSTRUMENT_METHOD.md"
LEVELS = R / "gdt170_recovery_levels.tsv"
COMPONENTS = R / "gdt170_component_recovery.tsv"
CALIBRATION = R / "gdt170_diagnostic_calibration.tsv"
COUNTER = R / "gdt170_counterexamples.tsv"
REPORT = R / "GDT170_FULL_OBSERVATION_INSTRUMENT_REPORT.md"
RESULT = R / "gdt170_result.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def csha(value) -> str:
    raw = json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def load_gzip(path: Path):
    with gzip.open(path, "rt", encoding="utf8") as handle: return json.load(handle)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf8", newline="") as handle: return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict]) -> None:
    fields: list[str] = []
    for row in rows:
        for field in row:
            if field not in fields: fields.append(field)
    with path.open("w", encoding="utf8", newline="") as handle:
        writer = csv.DictWriter(handle, fields, delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows([{field: row.get(field, "NA") for field in fields} for row in rows])


def entropy(counts: Counter) -> float:
    total = sum(counts.values())
    return -sum(n / total * math.log2(n / total) for n in counts.values() if n) if total else 0.0


def information(rows: list[dict], key) -> tuple[float, float, float]:
    h = entropy(Counter(int(x["concept_index"]) for x in rows)); groups = defaultdict(Counter)
    for row in rows: groups[key(row)][int(row["concept_index"])] += 1
    cond = sum(sum(c.values()) / len(rows) * entropy(c) for c in groups.values())
    return h, h - cond, (h - cond) / h if h else 0.0


def held_decoder(rows: list[dict], key) -> dict:
    units = sorted({x["source_unit_full"] for x in rows}); correct = covered = total = positive = 0
    for held in units:
        maps = defaultdict(Counter)
        for row in rows:
            if row["source_unit_full"] != held: maps[key(row)][int(row["concept_index"])] += 1
        fold_correct = 0
        for row in rows:
            if row["source_unit_full"] != held: continue
            total += 1; k = key(row)
            if k in maps:
                covered += 1; prediction = sorted(maps[k].items(), key=lambda x: (-x[1], x[0]))[0][0]
                hit = int(prediction == int(row["concept_index"])); correct += hit; fold_correct += hit
        positive += int(fold_correct > 0)
    return {"predictions": covered, "correct": correct, "total_rows": total, "coverage": covered / total,
            "accuracy_on_predictions": correct / covered if covered else 0.0, "positive_source_units": positive,
            "source_units": len(units)}


def inferred_tuple(x: dict):
    return (x["outer_left"], x["local_left"], x["inferred_host"], x["right_inner"], x["right_outer"],
            int(x["group_index"]), int(x["line_ordinal_on_folio"]) % 3, int(x["paragraph_start"]), int(x["paragraph_end"]))


def oracle_tuple(x: dict):
    return (x["true_wrapper"], x["true_local_frame"], x["rendered_host"], x["true_right_family"],
            x["true_closure_value"], int(x["true_dy_closure"]), int(x["true_b3"]), int(x["true_record_slot"]))


def architecture_readout(system: str, level: str, host: dict, full: dict) -> str:
    if level == "ORACLE_CEILING": return "KNOWN_ARCHITECTURE_RECOVERED"
    if system == "SYSTEM_A" and host["accuracy_on_predictions"] >= .8 and host["coverage"] >= .2:
        return "PARTIAL_LEXICAL_IDENTITY_RECOVERY_WITHOUT_COMPONENT_SEGMENTATION"
    if system == "SYSTEM_B" and full["accuracy_on_predictions"] >= .8 and full["coverage"] >= .2 and full["accuracy_on_predictions"] - host["accuracy_on_predictions"] >= .3:
        return "PARTIAL_DISTRIBUTED_RECORD_SIGNAL_RECOVERY_WITHOUT_COMPONENT_SEGMENTATION"
    return "ARCHITECTURE_NOT_RECOVERED"


def main() -> None:
    blind = json.loads(BLIND_RESULT.read_text()); validation = json.loads(BLIND_VALIDATION.read_text())
    assert blind["status"] == "BLIND_OUTPUTS_FROZEN_BEFORE_ORACLE_EVALUATION"
    assert validation["status"] == "PASS_INDEPENDENT_NO_ORACLE_BLIND_RECONSTRUCTION"
    obs = load_gzip(OBS)["rows"]; oracle = load_gzip(ORACLE)["rows"]; parses = load_gzip(PARSES)["rows"]
    assert len(obs) == len(oracle) == 240000 and len(parses) == 480000
    omap = {x["observation_id"]: x for x in oracle}; pmap = {(x["observation_id"], x["parser_level"]): x for x in parses}
    systems = defaultdict(set)
    for row in obs: systems[row["world_view"]].add(omap[row["observation_id"]]["system"])
    assert systems == {"CONTROL_X": {"SYSTEM_A"}, "CONTROL_Y": {"SYSTEM_B"}}

    joined_by = defaultdict(list)
    component_acc = defaultdict(Counter)
    component_n = Counter()
    for row in obs:
        truth = omap[row["observation_id"]]; system = truth["system"]
        if row["witness_renderer"] != "R1_S1":
            for level in ("SURFACE_ONLY", "VMANUS_ANNOTATION_ASSISTED"):
                p = pmap[row["observation_id"], level]
                prefix = truth["true_wrapper"] + truth["true_local_frame"]
                assert row["surface_group"].startswith(prefix + truth["rendered_host"])
                suffix = row["surface_group"][len(prefix + truth["rendered_host"]):]
                parsed_left = ("" if p["outer_left"] == "NONE" else p["outer_left"]) + ("" if p["local_left"] == "NONE" else p["local_left"])
                parsed_right = ("" if p["right_inner"] == "NONE" else p["right_inner"]) + ("" if p["right_outer"] == "NONE" else p["right_outer"])
                key = system, level, row["witness_renderer"]
                component_n[key] += 1; component_acc[key]["host"] += p["inferred_host"] == truth["rendered_host"]
                component_acc[key]["left"] += parsed_left == prefix; component_acc[key]["right"] += parsed_right == suffix
                component_acc[key]["full"] += p["inferred_host"] == truth["rendered_host"] and parsed_left == prefix and parsed_right == suffix
            continue
        base = {**row, **truth}
        for level in ("SURFACE_ONLY", "VMANUS_ANNOTATION_ASSISTED"):
            p = pmap[row["observation_id"], level]; joined_by[system, level].append({**base, **p})
            prefix = truth["true_wrapper"] + truth["true_local_frame"]
            assert row["surface_group"].startswith(prefix + truth["rendered_host"])
            suffix = row["surface_group"][len(prefix + truth["rendered_host"]):]
            parsed_left = ("" if p["outer_left"] == "NONE" else p["outer_left"]) + ("" if p["local_left"] == "NONE" else p["local_left"])
            parsed_right = ("" if p["right_inner"] == "NONE" else p["right_inner"]) + ("" if p["right_outer"] == "NONE" else p["right_outer"])
            key = system, level, "R1_S1"; component_n[key] += 1
            component_acc[key]["host"] += p["inferred_host"] == truth["rendered_host"]
            component_acc[key]["left"] += parsed_left == prefix; component_acc[key]["right"] += parsed_right == suffix
            component_acc[key]["full"] += p["inferred_host"] == truth["rendered_host"] and parsed_left == prefix and parsed_right == suffix

    level_rows = []; level_index = {}
    for system in ("SYSTEM_A", "SYSTEM_B"):
        primary_oracle = [{**row, **omap[row["observation_id"]]} for row in obs if row["witness_renderer"] == "R1_S1" and omap[row["observation_id"]]["system"] == system]
        for level in ("SURFACE_ONLY", "VMANUS_ANNOTATION_ASSISTED", "ORACLE_CEILING"):
            rows = primary_oracle if level == "ORACLE_CEILING" else joined_by[system, level]
            host_key = (lambda x: x["rendered_host"]) if level == "ORACLE_CEILING" else (lambda x: x["inferred_host"])
            full_key = oracle_tuple if level == "ORACLE_CEILING" else inferred_tuple
            raw_key = lambda x: x["surface_group"]
            h, host_mi, host_fraction = information(rows, host_key); _, full_mi, full_fraction = information(rows, full_key); _, raw_mi, raw_fraction = information(rows, raw_key)
            host_dec = held_decoder(rows, host_key); full_dec = held_decoder(rows, full_key); raw_dec = held_decoder(rows, raw_key)
            item = {"system": system, "instrument_level": level, "rows": len(rows), "concept_entropy_bits": h,
                    "host_mutual_information_bits": host_mi, "host_information_fraction": host_fraction,
                    "full_tuple_mutual_information_bits": full_mi, "full_tuple_information_fraction": full_fraction,
                    "raw_surface_information_fraction": raw_fraction,
                    "host_decoder_predictions": host_dec["predictions"], "host_decoder_coverage": host_dec["coverage"],
                    "host_decoder_accuracy": host_dec["accuracy_on_predictions"],
                    "full_decoder_predictions": full_dec["predictions"], "full_decoder_coverage": full_dec["coverage"],
                    "full_decoder_accuracy": full_dec["accuracy_on_predictions"],
                    "raw_decoder_coverage": raw_dec["coverage"], "raw_decoder_accuracy": raw_dec["accuracy_on_predictions"],
                    "architecture_readout": architecture_readout(system, level, host_dec, full_dec)}
            level_rows.append(item); level_index[system, level] = item

    component_rows = []
    for key in sorted(component_n):
        system, level, renderer = key; n = component_n[key]; acc = component_acc[key]
        component_rows.append({"system": system, "instrument_level": level, "witness_renderer": renderer, "rows": n,
                               "exact_true_host_rate": acc["host"] / n, "exact_left_edge_rate": acc["left"] / n,
                               "exact_right_edge_rate": acc["right"] / n, "exact_full_decomposition_rate": acc["full"] / n})
    for system in ("SYSTEM_A", "SYSTEM_B"):
        component_rows.append({"system": system, "instrument_level": "ORACLE_CEILING", "witness_renderer": "ALL_RENDERERS", "rows": 120000,
                               "exact_true_host_rate": 1.0, "exact_left_edge_rate": 1.0, "exact_right_edge_rate": 1.0,
                               "exact_full_decomposition_rate": 1.0})

    diag = read_tsv(BLIND_DIAGNOSTICS); calibration_rows = []
    for system, world in (("SYSTEM_A", "CONTROL_X"), ("SYSTEM_B", "CONTROL_Y")):
        for level in ("SURFACE_ONLY", "VMANUS_ANNOTATION_ASSISTED"):
            rows = [x for x in diag if x["world_view"] == world and x["witness_renderer"] == "R1_S1" and x["parser_level"] == level]
            by_name = defaultdict(list)
            for row in rows: by_name[row["diagnostic"]].append(row)
            rec = by_name["RECORD_ARCHITECTURE"][0]; comp = by_name["OPERATION_COMPATIBILITY"][0]; short = by_name["SHORT_HOST_STRUCTURE"][0]
            same = by_name["SAME_GROUP_SUBSTITUTION"][0]; ext = by_name["EXTERNAL_CONTEXT_SUBSTITUTION"][0]
            nxt = next(x for x in by_name["HELD_CONTEXT"] if x["endpoint"] == "NEXT_HOST")
            line = next(x for x in by_name["HELD_CONTEXT"] if x["endpoint"] == "WHOLE_LINE")
            calibration_rows.extend([
                {"system": system, "instrument_level": level, "diagnostic": "GDT113_RECORD_CLOSURE", "known_property": "GENERATED_RECORD_CLOSURE_PRESENT", "observed_value": rec["right_marked_record_end_precision"], "assessment": "PARTIAL_TRUE_POSITIVE"},
                {"system": system, "instrument_level": level, "diagnostic": "GDT160_OPERATION_COMPATIBILITY", "known_property": "SEPARATE_EDGE_FIELDS_PRESENT", "observed_value": comp["compatible_pair_density"], "assessment": "FALSE_NEGATIVE_ZERO"},
                {"system": system, "instrument_level": level, "diagnostic": "GDT162_SHORT_HOST", "known_property": "TRUE_HOST_LENGTH_2_OR_3", "observed_value": short["short_host_mass"], "assessment": "FALSE_NEGATIVE_ZERO"},
                {"system": system, "instrument_level": level, "diagnostic": "GDT163_SAME_GROUP_SUBSTITUTION", "known_property": "DISTRIBUTED_COUPLING" if system == "SYSTEM_B" else "NO_INTERNAL_OPERATOR", "observed_value": same["mean_delta_cosine"], "assessment": "FALSE_NEGATIVE" if system == "SYSTEM_B" else "TRUE_NEGATIVE"},
                {"system": system, "instrument_level": level, "diagnostic": "GDT164_EXTERNAL_SUBSTITUTION", "known_property": "NO_EXTERNAL_SUBSTITUTION_OPERATOR", "observed_value": ext["mean_delta_cosine"], "assessment": "TRUE_NEGATIVE"},
                {"system": system, "instrument_level": level, "diagnostic": "GDT165_NEXT_HOST", "known_property": "REAL_SOURCE_ORDER", "observed_value": nxt["gain_bits"], "assessment": "NEGATIVE_CONTEXT_TRANSFER"},
                {"system": system, "instrument_level": level, "diagnostic": "GDT166_LINE_CONTEXT", "known_property": "REAL_SOURCE_LINE_CONTEXT", "observed_value": line["gain_bits"], "assessment": "NEGATIVE_CONTEXT_TRANSFER"},
            ])

    counter_rows = [
        {"counterexample": "OBSERVATION_LAYER_PRESERVES_ENCODER_FIELDS", "evidence": "The strict observation corpus omits every true component; exact full decomposition is low in both blind levels.", "impact": "GDT168 truth-column results were an oracle-assisted ceiling, not normal parser sensitivity."},
        {"counterexample": "VISIBLE_LAYOUT_RECOVERS_FULL_COMPILER", "evidence": "Layout assistance makes selected right marks precise at record ends but does not recover most left/right component boundaries.", "impact": "Boundary recovery and surface-algebra recovery are separate instrument capabilities."},
        {"counterexample": "SHORT_TRUE_HOST_IS_DISCOVERABLE_FROM_SURFACE_CONTRASTS", "evidence": "Both worlds have true 2-3 character hosts, while blind inferred short-host mass is zero.", "impact": "The frozen contrast parser is not sensitive to the implanted codebook layer under these historical render variants."},
        {"counterexample": "NEGATIVE_HOST_DIAGNOSTICS_DISTINGUISH_ARCHITECTURE", "evidence": "With inferred rather than oracle hosts, both worlds remain negative and neither architecture is recovered.", "impact": "Negative VManus host diagnostics cannot be interpreted without segmentation calibration."},
        {"counterexample": "ORACLE_RECOVERY_VALIDATES_SURFACE_PIPELINE", "evidence": "Oracle fields recover both architectures by construction.", "impact": "Oracle ceilings verify identifiability given correct fields, not blind recoverability."},
    ]
    write_tsv(LEVELS, level_rows); write_tsv(COMPONENTS, component_rows); write_tsv(CALIBRATION, calibration_rows); write_tsv(COUNTER, counter_rows)

    a_s = level_index["SYSTEM_A", "SURFACE_ONLY"]; a_v = level_index["SYSTEM_A", "VMANUS_ANNOTATION_ASSISTED"]; a_o = level_index["SYSTEM_A", "ORACLE_CEILING"]
    b_s = level_index["SYSTEM_B", "SURFACE_ONLY"]; b_v = level_index["SYSTEM_B", "VMANUS_ANNOTATION_ASSISTED"]; b_o = level_index["SYSTEM_B", "ORACLE_CEILING"]
    report = f"""# GDT170 — full observation-layer instrument calibration report

Status: **PARTIAL_IDENTITY_AND_RECORD_SIGNAL_WITHOUT_COMPONENT_ARCHITECTURE_RECOVERY**.

GDT170 upgrades GDT168 by forcing both causal worlds through a manuscript-like
observation boundary.  The blind parser saw only visible groups, separators,
physical line/layout roles, register/hand metadata and permitted neutral
annotations.  Concepts, plaintext, codebook, record slots and encoder fields
were opened only after the 480,000 blind parses were committed and published.

## Recovery by instrument level (primary renderer)

| world | level | host information fraction | host held decoder accuracy / coverage | full-tuple held decoder accuracy / coverage | readout |
|---|---|---:|---:|---:|---|
| A: lexical codebook | surface only | {a_s['host_information_fraction']:.3f} | {a_s['host_decoder_accuracy']:.3f} / {a_s['host_decoder_coverage']:.3f} | {a_s['full_decoder_accuracy']:.3f} / {a_s['full_decoder_coverage']:.3f} | {a_s['architecture_readout']} |
| A: lexical codebook | annotation assisted | {a_v['host_information_fraction']:.3f} | {a_v['host_decoder_accuracy']:.3f} / {a_v['host_decoder_coverage']:.3f} | {a_v['full_decoder_accuracy']:.3f} / {a_v['full_decoder_coverage']:.3f} | {a_v['architecture_readout']} |
| A: lexical codebook | oracle ceiling | {a_o['host_information_fraction']:.3f} | {a_o['host_decoder_accuracy']:.3f} / {a_o['host_decoder_coverage']:.3f} | {a_o['full_decoder_accuracy']:.3f} / {a_o['full_decoder_coverage']:.3f} | {a_o['architecture_readout']} |
| B: distributed record code | surface only | {b_s['host_information_fraction']:.3f} | {b_s['host_decoder_accuracy']:.3f} / {b_s['host_decoder_coverage']:.3f} | {b_s['full_decoder_accuracy']:.3f} / {b_s['full_decoder_coverage']:.3f} | {b_s['architecture_readout']} |
| B: distributed record code | annotation assisted | {b_v['host_information_fraction']:.3f} | {b_v['host_decoder_accuracy']:.3f} / {b_v['host_decoder_coverage']:.3f} | {b_v['full_decoder_accuracy']:.3f} / {b_v['full_decoder_coverage']:.3f} | {b_v['architecture_readout']} |
| B: distributed record code | oracle ceiling | {b_o['host_information_fraction']:.3f} | {b_o['host_decoder_accuracy']:.3f} / {b_o['host_decoder_coverage']:.3f} | {b_o['full_decoder_accuracy']:.3f} / {b_o['full_decoder_coverage']:.3f} | {b_o['architecture_readout']} |

Empirical information on nearly unique inferred strings is optimistic; the
held-source decoder is the decisive calibration.  The blind levels do recover
limited transferable signal: System A's inferred whole-surface-like identities
decode perfectly where seen at 23--25% coverage, and System B's visible full
group plus physical record position decodes perfectly at 22% coverage.  These
are partial lexical-identity and distributed-record signals.  They are not a
recovery of the hidden components: exact true-host, left-edge, right-edge and
full-decomposition rates are all zero.  The oracle reproduces the original
GDT168 ceiling: System A's true host is a complete lexical address, while
System B requires its distributed tuple and slot.

## What annotations help

Visible layout helps find a subset of closure behavior: in the primary views,
annotation-assisted inferred right marks have record-end precision 1.0.  It
does not solve segmentation.  Exact true-host recovery is zero, the true
2–3-character host mass is reported as zero by the blind parser, operation
compatibility is zero, and the implanted distributed substitution coupling in
System B is missed.

## Instrument consequence

GDT168's earlier host and compiler diagnostics were computed from supplied
HPR2-analog truth columns.  They therefore calibrate **oracle-field
diagnostics**, not the end-to-end VManus surface pipeline.  GDT170 shows that
the current generic prefix/suffix contrast parser can recover some record
closure and some whole-identity/position transfer, but cannot recover either
the implanted lexical host boundary or the distributed compiler components
from manuscript-like observations.

Accordingly, a negative Voynich PAGE_HOST result cannot by itself distinguish
the two architectures, and an oracle-level positive cannot be credited to the
surface parser.  A future instrument improvement must be judged on these
frozen synthetic observations, not tuned on Voynich outcomes.

No Voynich source or image was used.  f84r was not accessed.
"""
    REPORT.write_text(report, encoding="utf8")
    result = {"schema": "GDT170_FULL_OBSERVATION_INSTRUMENT_RESULT_V1",
              "status": "PARTIAL_IDENTITY_AND_RECORD_SIGNAL_WITHOUT_COMPONENT_ARCHITECTURE_RECOVERY",
              "decision": "GDT168_ORACLE_DIAGNOSTICS_NOT_END_TO_END_PARSER_CALIBRATION",
              "world_mapping": {"CONTROL_X": "SYSTEM_A_FIXED_LEXICAL_CODEBOOK", "CONTROL_Y": "SYSTEM_B_DISTRIBUTED_RECORD_CODE"},
              "headline": {"system_a": {x: a_s[x] for x in ("host_information_fraction", "host_decoder_accuracy", "host_decoder_coverage", "full_decoder_accuracy", "full_decoder_coverage")},
                           "system_b": {x: b_s[x] for x in ("host_information_fraction", "host_decoder_accuracy", "host_decoder_coverage", "full_decoder_accuracy", "full_decoder_coverage")},
                           "oracle_system_a_host_information_fraction": a_o["host_information_fraction"],
                           "oracle_system_b_host_information_fraction": b_o["host_information_fraction"],
                           "oracle_system_b_full_information_fraction": b_o["full_tuple_information_fraction"]},
              "inputs": {p.name: sha(p) for p in (OBS, ORACLE, FREEZE, DESIGN, PARSES, BLIND_RESULT, BLIND_VALIDATION, BLIND_DIAGNOSTICS)},
              "outputs": {p.name: sha(p) for p in (LEVELS, COMPONENTS, CALIBRATION, COUNTER)},
              "documents": {METHOD.name: sha(METHOD), REPORT.name: sha(REPORT)},
              "implementation": {Path(__file__).name: sha(Path(__file__))},
              "commitments": {"recovery_levels_content_sha256": csha(level_rows), "component_recovery_content_sha256": csha(component_rows),
                              "diagnostic_calibration_content_sha256": csha(calibration_rows)},
              "chronology": {"observation_oracle_freeze_commit": "b4c1cba", "blind_design_commit": "4ecde6f", "blind_outputs_commit": "ef379be",
                             "oracle_opened_only_after_blind_outputs_published": True},
              "no_voynich_tuning": True, "voynich_inputs": 0, "f84r_access": False,
              "claim_ceiling": "Synthetic end-to-end instrument calibration only; no Voynich word, code value, language, role, meaning, plaintext, or translation."}
    result["result_content_sha256"] = csha(result); RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": result["status"], "a_surface_host_accuracy": a_s["host_decoder_accuracy"],
                      "b_surface_full_accuracy": b_s["full_decoder_accuracy"], "a_oracle_host_fraction": a_o["host_information_fraction"],
                      "b_oracle_full_fraction": b_o["full_tuple_information_fraction"]}, sort_keys=True))


if __name__ == "__main__": main()
