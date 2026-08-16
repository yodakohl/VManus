#!/usr/bin/env python3
"""Independent no-oracle validator for the frozen GDT170 blind instrument."""
from __future__ import annotations

import csv
import gzip
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

R = Path(__file__).resolve().parent
OBS = R / "gdt170_observation_corpus.json.gz"
PARSES = R / "gdt170_blind_parses.json.gz"
OPS = R / "gdt170_blind_operations.tsv"
DIAG = R / "gdt170_blind_diagnostics.tsv"
DESIGN = R / "gdt170_blind_design.json"
RESULT = R / "gdt170_blind_result.json"
RUNNER = R / "run_gdt170_blind_instrument.py"
OUT = R / "gdt170_blind_validation.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def csha(value) -> str:
    raw = json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def check(value: bool, label: str, checks: list[str]) -> None:
    if not value: raise AssertionError(label)
    checks.append(label)


def main() -> None:
    checks: list[str] = []
    design = json.loads(DESIGN.read_text()); result = json.loads(RESULT.read_text())
    with gzip.open(OBS, "rt", encoding="utf8") as handle: obs_payload = json.load(handle)
    with gzip.open(PARSES, "rt", encoding="utf8") as handle: parse_payload = json.load(handle)
    obs, parses = obs_payload["rows"], parse_payload["rows"]
    ops, diagnostics = read_tsv(OPS), read_tsv(DIAG)
    check(design["status"] == "FROZEN_BEFORE_BLIND_SURFACE_PARSE", "design_frozen", checks)
    check(result["status"] == "BLIND_OUTPUTS_FROZEN_BEFORE_ORACLE_EVALUATION", "result_status", checks)
    check(len(obs) == 240000 and len(parses) == 480000, "row_counts", checks)
    check(len(ops) == 40 and len(diagnostics) == 316, "artifact_counts", checks)
    obs_by_id = {x["observation_id"]: x for x in obs}
    check(len(obs_by_id) == len(obs), "observation_ids_unique", checks)
    levels = Counter((x["observation_id"], x["parser_level"]) for x in parses)
    check(set(x["parser_level"] for x in parses) == set(design["blind_levels"]), "parser_levels_exact", checks)
    check(len(levels) == 480000 and all(v == 1 for v in levels.values()), "one_parse_per_id_level", checks)
    selected = defaultdict(lambda: {"LEFT": set(), "RIGHT": set()})
    for row in ops: selected[row["world_view"], row["witness_renderer"]][row["side"]].add(row["operation"])
    check(len(selected) == 20, "operation_views_twenty", checks)
    check(all(len(v["LEFT"]) <= 12 and len(v["RIGHT"]) <= 12 for v in selected.values()), "operation_caps", checks)

    for item in parses:
        src = obs_by_id[item["observation_id"]]
        check(item["surface_group"] == src["surface_group"], "surface_join_exact", checks)
        check(item["world_view"] == src["world_view"] and item["witness_renderer"] == src["witness_renderer"], "view_join_exact", checks)
        check(item["folio_id"] == src["folio_id"] and item["physical_line_id"] == src["physical_line_id"], "physical_join_exact", checks)
        check(str(item["group_index"]) == str(src["group_index"]) and str(item["group_count"]) == str(src["group_count"]), "group_position_join_exact", checks)
        ls = [x for x in (item["outer_left"], item["local_left"]) if x != "NONE"]
        rs = [x for x in (item["right_outer"], item["right_inner"]) if x != "NONE"]
        reconstructed = "".join(ls) + item["inferred_host"] + "".join(reversed(rs))
        check(reconstructed == item["surface_group"], "surface_reconstructs_from_blind_parse", checks)
        key = item["world_view"], item["witness_renderer"]
        check(all(x in selected[key]["LEFT"] for x in ls), "left_ops_selected", checks)
        check(all(x in selected[key]["RIGHT"] for x in rs), "right_ops_selected", checks)
        check(int(item["operation_count"]) == len(ls) + len(rs) <= 3 and len(ls) <= 2 and len(rs) <= 2, "layer_caps_exact", checks)
    checks = list(dict.fromkeys(checks))

    # Reconstruct selected operation eligibility from the visible vocabulary.
    visible_by = defaultdict(list)
    for row in obs: visible_by[row["world_view"], row["witness_renderer"]].append(row)
    for key, values in visible_by.items():
        vocab = {x["surface_group"] for x in values}; folios = defaultdict(set)
        for row in values: folios[row["surface_group"]].add(row["folio_id"])
        for side in ("LEFT", "RIGHT"):
            for op in selected[key][side]:
                hosts, fs = set(), set()
                for word in vocab:
                    if side == "LEFT" and word.startswith(op) and len(word) > len(op) and word[len(op):] in vocab:
                        host = word[len(op):]; hosts.add(host); fs.update(folios[word] | folios[host])
                    if side == "RIGHT" and word.endswith(op) and len(word) > len(op) and word[:-len(op)] in vocab:
                        host = word[:-len(op)]; hosts.add(host); fs.update(folios[word] | folios[host])
                check(1 <= len(op) <= 3 and len(hosts) >= 8 and len(fs) >= 5, "selected_operation_eligible", checks)
    checks = list(dict.fromkeys(checks))

    expected_diag = Counter()
    for world, renderer in visible_by:
        for level in design["blind_levels"]:
            expected_diag[world, renderer, level] += 7
            if renderer != "R1_S1": expected_diag[world, renderer, level] += 1
    actual_diag = Counter((x["world_view"], x["witness_renderer"], x["parser_level"]) for x in diagnostics)
    check(actual_diag == expected_diag, "diagnostic_family_counts", checks)
    check({x["diagnostic"] for x in diagnostics} == {"RECORD_ARCHITECTURE", "OPERATION_COMPATIBILITY", "SHORT_HOST_STRUCTURE",
          "SAME_GROUP_SUBSTITUTION", "EXTERNAL_CONTEXT_SUBSTITUTION", "HELD_CONTEXT", "RENDERER_GEOMETRY_ALIGNMENT"},
          "diagnostic_names_exact", checks)
    for row in diagnostics:
        if row["diagnostic"] == "OPERATION_COMPATIBILITY":
            l, r = int(row["left_operations"]), int(row["right_operations"])
            check(abs(float(row["compatible_pair_density"]) - int(row["compatible_pairs"]) / max(1, l * r)) < 1e-12,
                  "compatibility_density_arithmetic", checks)
            check(0 < float(row["inclusive_p"]) <= 1, "compatibility_p_range", checks)
        if row["diagnostic"] == "HELD_CONTEXT":
            check(int(row["content_folios"]) == 123, "held_context_folio_count", checks)
    checks = list(dict.fromkeys(checks))

    for key, summary in result["primary_renderer_summary"].items():
        world, level = key.split("|"); subset = [x for x in parses if x["world_view"] == world and x["witness_renderer"] == "R1_S1" and x["parser_level"] == level]
        check(len({x["inferred_host"] for x in subset}) == int(summary["inferred_host_types"]), "summary_host_types", checks)
        check(abs(sum(int(x["operation_count"]) for x in subset) / len(subset) - float(summary["mean_operation_count"])) < 1e-12,
              "summary_mean_operation_count", checks)
        check(abs(sum(x["inferred_host"] == x["surface_group"] for x in subset) / len(subset) - float(summary["surface_exact_host_rate"])) < 1e-12,
              "summary_surface_host_rate", checks)
    checks = list(dict.fromkeys(checks))

    check(csha(parses) == result["commitments"]["parse_content_sha256"], "parse_content_hash", checks)
    # Heterogeneous TSV cells are serialized strings; arithmetic above independently
    # checks the scientific fields, while the exact byte hash binds the full table.
    check(all(sha(R / name) == digest for name, digest in result["outputs"].items()), "output_hashes", checks)
    check(all(sha(R / name) == digest for name, digest in result["inputs"].items()), "input_hashes", checks)
    check(sha(RUNNER) == result["implementation"][RUNNER.name], "runner_hash", checks)
    stored = result.pop("result_content_sha256")
    check(csha(result) == stored, "result_content_hash", checks)
    source_text = RUNNER.read_text()
    check(not any(name in source_text for name in design["forbidden_inputs"]), "runner_forbidden_filename_firewall", checks)
    check(not any(('"' + field + '"') in source_text or ("'" + field + "'") in source_text for field in design["forbidden_fields"]),
          "runner_forbidden_field_firewall", checks)
    check(result["blind_firewall"] == {"read_files": [OBS.name, "gdt170_observation_oracle_freeze.json", DESIGN.name, "GDT170_FULL_OBSERVATION_INSTRUMENT_METHOD.md"],
          "forbidden_inputs_opened": False, "truth_fields_used": False, "voynich_inputs": 0, "f84r_access": False}, "reported_firewall_exact", checks)

    validation = {"schema": "GDT170_BLIND_INSTRUMENT_VALIDATION_V1", "status": "PASS_INDEPENDENT_NO_ORACLE_BLIND_RECONSTRUCTION",
                  "checks_passed": len(checks), "checks_failed": 0, "checks": checks,
                  "observation_rows": len(obs), "parse_rows": len(parses), "operation_rows": len(ops), "diagnostic_rows": len(diagnostics),
                  "result_sha256": sha(RESULT), "validator_sha256": sha(Path(__file__)), "oracle_files_opened": 0,
                  "voynich_inputs": 0, "f84r_access": False}
    validation["validation_content_sha256"] = csha(validation)
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n")
    print(f"PASS {len(checks)}/{len(checks)}")


if __name__ == "__main__": main()
