#!/usr/bin/env python3
"""Independent three-level validator for the GDT171 historical-v2 calibration."""
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
PARSES = R / "gdt171_blind_parses.json.gz"
LEVELS = R / "gdt171_recovery_levels.tsv"
COMPONENTS = R / "gdt171_component_recovery.tsv"
CALIBRATION = R / "gdt171_diagnostic_calibration.tsv"
COUNTER = R / "gdt171_counterexamples.tsv"
REPORT = R / "GDT171_HISTORICAL_PLAUSIBILITY_INSTRUMENT_REPORT.md"
RESULT = R / "gdt171_result.json"
PRODUCER = R / "unblind_gdt171_historical_calibration.py"
OUT = R / "gdt171_validation.json"


def sha(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()
def csha(x) -> str: return hashlib.sha256(json.dumps(x, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()


def load(path: Path):
    with gzip.open(path, "rt", encoding="utf8") as handle: return json.load(handle)["rows"]


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf8", newline="") as handle: return list(csv.DictReader(handle, delimiter="\t"))


def entropy(c: Counter) -> float:
    n = sum(c.values()); return -sum(v / n * math.log2(v / n) for v in c.values() if v) if n else 0.0


def information(rows: list[dict], target, key) -> float:
    h = entropy(Counter(target(x) for x in rows)); groups = defaultdict(Counter)
    for x in rows: groups[key(x)][target(x)] += 1
    cond = sum(sum(c.values()) / len(rows) * entropy(c) for c in groups.values())
    return (h - cond) / h if h else 0.0


def held(rows: list[dict], target, key) -> tuple[int, int, float, float]:
    covered = correct = total = 0
    for fold in sorted({x["source_unit_full"] for x in rows}):
        maps = defaultdict(Counter)
        for x in rows:
            if x["source_unit_full"] != fold: maps[key(x)][target(x)] += 1
        for x in rows:
            if x["source_unit_full"] != fold: continue
            total += 1; k = key(x)
            if k in maps:
                covered += 1; pred = sorted(maps[k].items(), key=lambda z: (-z[1], str(z[0])))[0][0]; correct += pred == target(x)
    return covered, correct, covered / total, correct / covered if covered else 0.0


def check(value: bool, label: str, checks: list[str]) -> None:
    if not value: raise AssertionError(label)
    checks.append(label)


def main() -> None:
    checks: list[str] = []; result = json.loads(RESULT.read_text())
    obs, oracle, parses = load(OBS), load(ORACLE), load(PARSES)
    levels, components, calibration, counters = read(LEVELS), read(COMPONENTS), read(CALIBRATION), read(COUNTER)
    check(result["status"] == "HISTORICAL_V2_PARTIALLY_RECOVERED_BUT_COMPONENT_SENSITIVITY_LIMITED", "result_status", checks)
    check(result["decision"] == "USE_GDT171_AS_PRIMARY_SYNTHETIC_INSTRUMENT_CALIBRATION_KEEP_GDT168_V1_AS_TOY_CONTROL", "decision_exact", checks)
    check(len(obs) == len(oracle) == 30428 and len(parses) == 60856, "input_counts", checks)
    check(len(levels) == 18 and len(components) == 24 and len(calibration) == 28 and len(counters) == 5, "output_counts", checks)
    omap = {x["observation_id"]: x for x in oracle}; pmap = {(x["observation_id"], x["parser_level"]): x for x in parses}
    check(len(omap) == len(oracle) and len(pmap) == len(parses), "join_keys_unique", checks)
    mapping = defaultdict(set)
    for x in obs: mapping[x["world_view"]].add(omap[x["observation_id"]]["system"])
    check(mapping == {"CONTROL_P": {"SYSTEM_A_V2"}, "CONTROL_Q": {"SYSTEM_B_V2"}}, "world_mapping", checks)
    level_map = {(x["system"], x["instrument_level"], x["stratum"]): x for x in levels}
    component_map = {(x["system"], x["instrument_level"], x["stratum"]): x for x in components}
    target = lambda x: x["lexical_id"]

    joined = defaultdict(list); accum = defaultdict(Counter); totals = Counter()
    for x in obs:
        truth = omap[x["observation_id"]]; system = truth["system"]
        prefix = truth["true_record_operator"] + truth["true_line_frame"] + truth["true_literal_escape"] + truth["true_lexical_left"]
        suffix = truth["true_lexical_right"] + truth["true_field_marker"] + truth["true_positional_right"] + truth["true_closure"]
        check(x["surface_group"] == prefix + truth["rendered_host"] + suffix, "oracle_surface_reconstruction", checks)
        for mode in ("SURFACE_ONLY", "VMANUS_ANNOTATION_ASSISTED"):
            p = pmap[x["observation_id"], mode]; row = {**x, **truth, **p}; joined[system, mode].append(row)
            left = ("" if p["outer_left"] == "NONE" else p["outer_left"]) + ("" if p["local_left"] == "NONE" else p["local_left"])
            right = ("" if p["right_inner"] == "NONE" else p["right_inner"]) + ("" if p["right_outer"] == "NONE" else p["right_outer"])
            true_parts = [z for z in (truth["true_record_operator"], truth["true_line_frame"], truth["true_literal_escape"], truth["true_lexical_left"], truth["rendered_host"], truth["true_lexical_right"], truth["true_field_marker"], truth["true_positional_right"], truth["true_closure"]) if z]
            pred_parts = [z for z in ("" if p["outer_left"] == "NONE" else p["outer_left"], "" if p["local_left"] == "NONE" else p["local_left"], p["inferred_host"], "" if p["right_inner"] == "NONE" else p["right_inner"], "" if p["right_outer"] == "NONE" else p["right_outer"]) if z]
            tb, pb, cursor = set(), set(), 0
            for z in true_parts[:-1]: cursor += len(z); tb.add(cursor)
            cursor = 0
            for z in pred_parts[:-1]: cursor += len(z); pb.add(cursor)
            strata = ["ALL_ROWS", truth["lexical_status"]]
            if truth["lexical_status"] == "FREQUENT_LEXICAL_ID" and (prefix or suffix): strata.append("FREQUENT_COMPILER_MARKED")
            for stratum in strata:
                key = system, mode, stratum; totals[key] += 1
                accum[key]["host"] += p["inferred_host"] == truth["rendered_host"]; accum[key]["left"] += left == prefix; accum[key]["right"] += right == suffix
                accum[key]["span"] += p["inferred_host"] == truth["rendered_host"] and left == prefix and right == suffix
                accum[key]["be"] += pb == tb; accum[key]["tp"] += len(pb & tb); accum[key]["pred"] += len(pb); accum[key]["true"] += len(tb)
    checks = list(dict.fromkeys(checks))
    for key, n in totals.items():
        row, a = component_map[key], accum[key]; precision = a["tp"] / a["pred"] if a["pred"] else 0; recall = a["tp"] / a["true"] if a["true"] else 0
        check(abs(float(row["exact_true_host_rate"]) - a["host"] / n) < 1e-12, "component_host_rate", checks)
        check(abs(float(row["exact_component_boundary_set_rate"]) - a["be"] / n) < 1e-12, "component_boundary_set_rate", checks)
        check(abs(float(row["component_boundary_precision"]) - precision) < 1e-12 and abs(float(row["component_boundary_recall"]) - recall) < 1e-12, "component_boundary_pr", checks)
    checks = list(dict.fromkeys(checks))
    check(all(float(x[f]) == 1 for x in components if x["instrument_level"] == "ORACLE_CEILING" for f in ("exact_true_host_rate", "exact_component_boundary_set_rate", "component_boundary_precision", "component_boundary_recall")), "oracle_component_ceiling", checks)

    for system in ("SYSTEM_A_V2", "SYSTEM_B_V2"):
        for mode in ("SURFACE_ONLY", "VMANUS_ANNOTATION_ASSISTED"):
            rows = [x for x in joined[system, mode] if x["lexical_status"] == "FREQUENT_LEXICAL_ID"]
            host_key = lambda z: z["inferred_host"]
            full_key = lambda z: (z["outer_left"], z["local_left"], z["inferred_host"], z["right_inner"], z["right_outer"], int(z["group_index"]), int(z["line_ordinal_on_folio"]), int(z["paragraph_start"]), int(z["paragraph_end"]))
            row = level_map[system, mode, "FREQUENT_LEXICAL_ID"]
            hc, hh, hcov, hacc = held(rows, target, host_key); fc, fh, fcov, facc = held(rows, target, full_key)
            check(abs(information(rows, target, host_key) - float(row["host_information_fraction"])) < 1e-12, "frequent_host_information", checks)
            check((hc, hh) == (int(row["host_decoder_predictions"]), round(int(row["host_decoder_predictions"]) * float(row["host_decoder_accuracy"]))), "frequent_host_counts", checks)
            check(abs(hcov - float(row["host_decoder_coverage"])) < 1e-12 and abs(hacc - float(row["host_decoder_accuracy"])) < 1e-12, "frequent_host_decoder", checks)
            check(abs(fcov - float(row["full_decoder_coverage"])) < 1e-12 and abs(facc - float(row["full_decoder_accuracy"])) < 1e-12, "frequent_full_decoder", checks)
        oracle_rows = [{**x, **omap[x["observation_id"]]} for x in obs if omap[x["observation_id"]]["system"] == system and omap[x["observation_id"]]["lexical_status"] == "FREQUENT_LEXICAL_ID"]
        orow = level_map[system, "ORACLE_CEILING", "FREQUENT_LEXICAL_ID"]
        host_key = lambda z: z["rendered_host"]
        full_key = lambda z: (z["true_record_operator"], z["true_line_frame"], z["true_literal_escape"], z["true_lexical_left"], z["rendered_host"], z["true_lexical_right"], z["true_field_marker"], z["true_positional_right"], z["true_closure"], int(z["true_record_slot"]))
        check(abs(information(oracle_rows, target, host_key) - float(orow["host_information_fraction"])) < 1e-12, "oracle_host_information", checks)
        check(abs(information(oracle_rows, target, full_key) - float(orow["full_tuple_information_fraction"])) < 1e-12, "oracle_full_information", checks)
    checks = list(dict.fromkeys(checks))

    check(all(sha(R / name) == digest for name, digest in result["inputs"].items()), "input_hashes", checks)
    check(all(sha(R / name) == digest for name, digest in result["outputs"].items()), "output_hashes", checks)
    check(sha(REPORT) == result["documents"][REPORT.name] and sha(PRODUCER) == result["implementation"][PRODUCER.name], "document_implementation_hashes", checks)
    stored = result.pop("result_content_sha256"); check(csha(result) == stored, "result_content_hash", checks)
    check(result["chronology"] == {"source_freeze_commit": "0ac0569", "blind_design_commit": "a639c9d", "blind_outputs_commit": "3e48f28", "oracle_opened_only_after_blind_outputs_published": True}, "chronology_exact", checks)
    check(result["no_voynich_tuning"] and result["voynich_inputs"] == 0 and result["f84r_access"] is False, "no_voynich_f84", checks)
    validation = {"schema": "GDT171_HISTORICAL_PLAUSIBILITY_VALIDATION_V1", "status": "PASS_INDEPENDENT_HISTORICAL_V2_THREE_LEVEL_RECONSTRUCTION",
                  "checks_passed": len(checks), "checks_failed": 0, "checks": checks, "observation_rows": len(obs), "oracle_rows": len(oracle),
                  "blind_parse_rows": len(parses), "result_sha256": sha(RESULT), "validator_sha256": sha(Path(__file__)), "voynich_inputs": 0, "f84r_access": False}
    validation["validation_content_sha256"] = csha(validation); OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n")
    print(f"PASS {len(checks)}/{len(checks)}")


if __name__ == "__main__": main()
