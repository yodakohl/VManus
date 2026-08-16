#!/usr/bin/env python3
"""Independent reconstruction validator for the GDT170 unblind calibration."""
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
PARSES = R / "gdt170_blind_parses.json.gz"
LEVELS = R / "gdt170_recovery_levels.tsv"
COMPONENTS = R / "gdt170_component_recovery.tsv"
CALIBRATION = R / "gdt170_diagnostic_calibration.tsv"
COUNTER = R / "gdt170_counterexamples.tsv"
RESULT = R / "gdt170_result.json"
REPORT = R / "GDT170_FULL_OBSERVATION_INSTRUMENT_REPORT.md"
PRODUCER = R / "unblind_gdt170_full_instrument.py"
OUT = R / "gdt170_validation.json"


def sha(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()
def csha(value) -> str: return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()


def load(path: Path):
    with gzip.open(path, "rt", encoding="utf8") as handle: return json.load(handle)["rows"]


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf8", newline="") as handle: return list(csv.DictReader(handle, delimiter="\t"))


def entropy(c: Counter) -> float:
    n = sum(c.values()); return -sum(v / n * math.log2(v / n) for v in c.values() if v) if n else 0.0


def information(rows: list[dict], key) -> float:
    h = entropy(Counter(int(x["concept_index"]) for x in rows)); groups = defaultdict(Counter)
    for x in rows: groups[key(x)][int(x["concept_index"])] += 1
    cond = sum(sum(c.values()) / len(rows) * entropy(c) for c in groups.values())
    return (h - cond) / h


def held(rows: list[dict], key) -> tuple[int, int, float, float]:
    covered = correct = total = 0
    for fold in sorted({x["source_unit_full"] for x in rows}):
        maps = defaultdict(Counter)
        for x in rows:
            if x["source_unit_full"] != fold: maps[key(x)][int(x["concept_index"])] += 1
        for x in rows:
            if x["source_unit_full"] != fold: continue
            total += 1; k = key(x)
            if k in maps:
                covered += 1; pred = sorted(maps[k].items(), key=lambda z: (-z[1], z[0]))[0][0]; correct += pred == int(x["concept_index"])
    return covered, correct, covered / total, correct / covered if covered else 0.0


def check(value: bool, label: str, checks: list[str]) -> None:
    if not value: raise AssertionError(label)
    checks.append(label)


def main() -> None:
    checks: list[str] = []; result = json.loads(RESULT.read_text())
    obs, oracle, parses = load(OBS), load(ORACLE), load(PARSES)
    levels, components, calibration, counters = read(LEVELS), read(COMPONENTS), read(CALIBRATION), read(COUNTER)
    check(result["status"] == "PARTIAL_IDENTITY_AND_RECORD_SIGNAL_WITHOUT_COMPONENT_ARCHITECTURE_RECOVERY", "result_status", checks)
    check(len(obs) == len(oracle) == 240000 and len(parses) == 480000, "source_counts", checks)
    check(len(levels) == 6 and len(components) == 42 and len(calibration) == 28 and len(counters) == 5, "output_counts", checks)
    omap = {x["observation_id"]: x for x in oracle}; pmap = {(x["observation_id"], x["parser_level"]): x for x in parses}
    check(len(omap) == 240000 and len(pmap) == 480000, "joins_unique", checks)
    mapping = defaultdict(set)
    for x in obs: mapping[x["world_view"]].add(omap[x["observation_id"]]["system"])
    check(mapping == {"CONTROL_X": {"SYSTEM_A"}, "CONTROL_Y": {"SYSTEM_B"}}, "world_mapping_exact", checks)

    level_map = {(x["system"], x["instrument_level"]): x for x in levels}
    exact = defaultdict(Counter); totals = Counter()
    for x in obs:
        if x["witness_renderer"] != "R1_S1": continue
        truth = omap[x["observation_id"]]; system = truth["system"]
        prefix = truth["true_wrapper"] + truth["true_local_frame"]
        check(x["surface_group"].startswith(prefix + truth["rendered_host"]), "oracle_surface_prefix_exact", checks)
        suffix = x["surface_group"][len(prefix + truth["rendered_host"]):]
        for mode in ("SURFACE_ONLY", "VMANUS_ANNOTATION_ASSISTED"):
            p = pmap[x["observation_id"], mode]; left = ("" if p["outer_left"] == "NONE" else p["outer_left"]) + ("" if p["local_left"] == "NONE" else p["local_left"])
            right = ("" if p["right_inner"] == "NONE" else p["right_inner"]) + ("" if p["right_outer"] == "NONE" else p["right_outer"])
            totals[system, mode] += 1; exact[system, mode]["host"] += p["inferred_host"] == truth["rendered_host"]
            exact[system, mode]["left"] += left == prefix; exact[system, mode]["right"] += right == suffix
            exact[system, mode]["full"] += p["inferred_host"] == truth["rendered_host"] and left == prefix and right == suffix
    checks = list(dict.fromkeys(checks))
    comp_map = {(x["system"], x["instrument_level"], x["witness_renderer"]): x for x in components}
    for key, n in totals.items():
        row = comp_map[key[0], key[1], "R1_S1"]
        check(abs(float(row["exact_true_host_rate"]) - exact[key]["host"] / n) < 1e-12, "component_host_rate", checks)
        check(abs(float(row["exact_left_edge_rate"]) - exact[key]["left"] / n) < 1e-12, "component_left_rate", checks)
        check(abs(float(row["exact_right_edge_rate"]) - exact[key]["right"] / n) < 1e-12, "component_right_rate", checks)
        check(abs(float(row["exact_full_decomposition_rate"]) - exact[key]["full"] / n) < 1e-12, "component_full_rate", checks)
    checks = list(dict.fromkeys(checks))
    check(all(float(comp_map[s, m, "R1_S1"][f]) == 0 for s in ("SYSTEM_A", "SYSTEM_B") for m in ("SURFACE_ONLY", "VMANUS_ANNOTATION_ASSISTED")
              for f in ("exact_true_host_rate", "exact_left_edge_rate", "exact_right_edge_rate", "exact_full_decomposition_rate")),
          "primary_blind_component_recovery_zero", checks)
    check(all(float(x[f]) == 1 for x in components if x["instrument_level"] == "ORACLE_CEILING" for f in ("exact_true_host_rate", "exact_left_edge_rate", "exact_right_edge_rate", "exact_full_decomposition_rate")),
          "oracle_component_ceiling_one", checks)

    for system in ("SYSTEM_A", "SYSTEM_B"):
        base = []
        for x in obs:
            if x["witness_renderer"] != "R1_S1" or omap[x["observation_id"]]["system"] != system: continue
            base.append({**x, **omap[x["observation_id"]]})
        for mode in ("SURFACE_ONLY", "VMANUS_ANNOTATION_ASSISTED"):
            rows = [{**x, **pmap[x["observation_id"], mode]} for x in base]
            host_key = lambda z: z["inferred_host"]
            full_key = lambda z: (z["outer_left"], z["local_left"], z["inferred_host"], z["right_inner"], z["right_outer"], int(z["group_index"]), int(z["line_ordinal_on_folio"]) % 3, int(z["paragraph_start"]), int(z["paragraph_end"]))
            row = level_map[system, mode]; hc, hh, hcov, hacc = held(rows, host_key); fc, fh, fcov, facc = held(rows, full_key)
            check(abs(information(rows, host_key) - float(row["host_information_fraction"])) < 1e-12, "blind_host_information", checks)
            check((hc, hh) == (int(row["host_decoder_predictions"]), round(int(row["host_decoder_predictions"]) * float(row["host_decoder_accuracy"]))), "blind_host_decoder_counts", checks)
            check(abs(hcov - float(row["host_decoder_coverage"])) < 1e-12 and abs(hacc - float(row["host_decoder_accuracy"])) < 1e-12, "blind_host_decoder_metrics", checks)
            check(abs(fcov - float(row["full_decoder_coverage"])) < 1e-12 and abs(facc - float(row["full_decoder_accuracy"])) < 1e-12, "blind_full_decoder_metrics", checks)
        orow = level_map[system, "ORACLE_CEILING"]
        host_key = lambda z: z["rendered_host"]
        full_key = lambda z: (z["true_wrapper"], z["true_local_frame"], z["rendered_host"], z["true_right_family"], z["true_closure_value"], int(z["true_dy_closure"]), int(z["true_b3"]), int(z["true_record_slot"]))
        check(abs(information(base, host_key) - float(orow["host_information_fraction"])) < 1e-12, "oracle_host_information", checks)
        check(abs(information(base, full_key) - float(orow["full_tuple_information_fraction"])) < 1e-12, "oracle_full_information", checks)
    checks = list(dict.fromkeys(checks))

    check(all(sha(R / name) == digest for name, digest in result["inputs"].items()), "input_hashes", checks)
    check(all(sha(R / name) == digest for name, digest in result["outputs"].items()), "output_hashes", checks)
    check(sha(PRODUCER) == result["implementation"][PRODUCER.name], "producer_hash", checks)
    check(sha(REPORT) == result["documents"][REPORT.name], "report_hash", checks)
    stored = result.pop("result_content_sha256"); check(csha(result) == stored, "result_content_hash", checks)
    check(result["chronology"] == {"observation_oracle_freeze_commit": "b4c1cba", "blind_design_commit": "4ecde6f", "blind_outputs_commit": "ef379be", "oracle_opened_only_after_blind_outputs_published": True}, "chronology_exact", checks)
    check(result["voynich_inputs"] == 0 and result["f84r_access"] is False, "no_voynich_f84", checks)
    validation = {"schema": "GDT170_FULL_OBSERVATION_INSTRUMENT_VALIDATION_V1", "status": "PASS_INDEPENDENT_THREE_LEVEL_INSTRUMENT_RECONSTRUCTION",
                  "checks_passed": len(checks), "checks_failed": 0, "checks": checks, "observation_rows": len(obs),
                  "oracle_rows": len(oracle), "blind_parse_rows": len(parses), "result_sha256": sha(RESULT),
                  "validator_sha256": sha(Path(__file__)), "voynich_inputs": 0, "f84r_access": False}
    validation["validation_content_sha256"] = csha(validation); OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n")
    print(f"PASS {len(checks)}/{len(checks)}")


if __name__ == "__main__": main()
