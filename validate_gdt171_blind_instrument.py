#!/usr/bin/env python3
"""Independent no-oracle validator for the GDT171 blind instrument run."""
from __future__ import annotations

import csv
import gzip
import hashlib
import json
from collections import defaultdict
from pathlib import Path

R = Path(__file__).resolve().parent
OBS = R / "gdt171_observation_corpus.json.gz"
PARSES = R / "gdt171_blind_parses.json.gz"
OPS = R / "gdt171_blind_operations.tsv"
DIAG = R / "gdt171_blind_diagnostics.tsv"
DESIGN = R / "gdt171_blind_design.json"
RESULT = R / "gdt171_blind_result.json"
RUNNER = R / "run_gdt171_blind_instrument.py"
PARENT = R / "run_gdt170_blind_instrument.py"
OUT = R / "gdt171_blind_validation.json"


def sha(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()
def csha(x) -> str: return hashlib.sha256(json.dumps(x, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()


def load(path: Path):
    with gzip.open(path, "rt", encoding="utf8") as handle: return json.load(handle)["rows"]


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf8", newline="") as handle: return list(csv.DictReader(handle, delimiter="\t"))


def check(value: bool, label: str, checks: list[str]) -> None:
    if not value: raise AssertionError(label)
    checks.append(label)


def main() -> None:
    checks: list[str] = []; design = json.loads(DESIGN.read_text()); result = json.loads(RESULT.read_text())
    obs, parses, ops, diagnostics = load(OBS), load(PARSES), read(OPS), read(DIAG)
    check(design["status"] == "FROZEN_UNCHANGED_GDT170_INSTRUMENT_BEFORE_V2_BLIND_PARSE", "design_status", checks)
    check(result["status"] == "GDT171_BLIND_OUTPUTS_FROZEN_BEFORE_ORACLE_EVALUATION", "result_status", checks)
    check(len(obs) == 30428 and len(parses) == 60856 and len(ops) == 35 and len(diagnostics) == 52, "artifact_counts", checks)
    omap = {x["observation_id"]: x for x in obs}; check(len(omap) == len(obs), "observation_ids_unique", checks)
    check(len({(x["observation_id"], x["parser_level"]) for x in parses}) == len(parses), "parse_ids_levels_unique", checks)
    check({x["parser_level"] for x in parses} == set(design["blind_levels"]), "parser_levels", checks)
    selected = defaultdict(lambda: {"LEFT": set(), "RIGHT": set()})
    for x in ops: selected[x["world_view"]][x["side"]].add(x["operation"])
    check(set(selected) == {"CONTROL_P", "CONTROL_Q"} and all(len(v["LEFT"]) <= 12 and len(v["RIGHT"]) <= 12 for v in selected.values()), "selected_operation_caps", checks)
    for p in parses:
        src = omap[p["observation_id"]]; check(p["surface_group"] == src["surface_group"], "surface_join", checks)
        check(p["world_view"] == src["world_view"] and p["register"] == src["register"] and p["hand"] == src["hand"], "metadata_join", checks)
        left = [x for x in (p["outer_left"], p["local_left"]) if x != "NONE"]
        right = [x for x in (p["right_outer"], p["right_inner"]) if x != "NONE"]
        check("".join(left) + p["inferred_host"] + "".join(reversed(right)) == p["surface_group"], "parse_reconstructs_surface", checks)
        check(all(x in selected[p["world_view"]]["LEFT"] for x in left) and all(x in selected[p["world_view"]]["RIGHT"] for x in right), "parse_ops_selected", checks)
        check(int(p["operation_count"]) == len(left) + len(right) <= 3 and len(left) <= 2 and len(right) <= 2, "layer_caps", checks)
    checks = list(dict.fromkeys(checks))

    by_world = defaultdict(list)
    for x in obs: by_world[x["world_view"]].append(x)
    for world, values in by_world.items():
        vocab = {x["surface_group"] for x in values}; folios = defaultdict(set)
        for x in values: folios[x["surface_group"]].add(x["folio_id"])
        for side in ("LEFT", "RIGHT"):
            for op in selected[world][side]:
                hosts, fs = set(), set()
                for word in vocab:
                    if side == "LEFT" and word.startswith(op) and len(word) > len(op) and word[len(op):] in vocab:
                        host = word[len(op):]; hosts.add(host); fs.update(folios[word] | folios[host])
                    if side == "RIGHT" and word.endswith(op) and len(word) > len(op) and word[:-len(op)] in vocab:
                        host = word[:-len(op)]; hosts.add(host); fs.update(folios[word] | folios[host])
                check(1 <= len(op) <= 3 and len(hosts) >= 8 and len(fs) >= 5, "operation_eligibility", checks)
    checks = list(dict.fromkeys(checks))
    check(sum(x["diagnostic"] == "REGISTER_GEOMETRY_ALIGNMENT" for x in diagnostics) == 24, "register_alignment_count", checks)
    check(sum(x["diagnostic"] == "HELD_CONTEXT" for x in diagnostics) == 8, "held_context_count", checks)
    check(all(int(x["content_folios"]) == 176 for x in diagnostics if x["diagnostic"] == "HELD_CONTEXT"), "held_folio_count", checks)
    check({x["diagnostic"] for x in diagnostics} == {"RECORD_ARCHITECTURE", "OPERATION_COMPATIBILITY", "SHORT_HOST_STRUCTURE", "SAME_GROUP_SUBSTITUTION", "EXTERNAL_CONTEXT_SUBSTITUTION", "HELD_CONTEXT", "REGISTER_GEOMETRY_ALIGNMENT"}, "diagnostic_names", checks)
    for key, summary in result["summary"].items():
        world, mode = key.split("|"); sub = [x for x in parses if x["world_view"] == world and x["parser_level"] == mode]
        check(len({x["inferred_host"] for x in sub}) == int(summary["inferred_host_types"]), "summary_host_types", checks)
        check(abs(sum(int(x["operation_count"]) for x in sub) / len(sub) - float(summary["mean_operation_count"])) < 1e-12, "summary_operation_mean", checks)
        check(abs(sum(x["inferred_host"] == x["surface_group"] for x in sub) / len(sub) - float(summary["surface_exact_host_rate"])) < 1e-12, "summary_surface_rate", checks)
    checks = list(dict.fromkeys(checks))
    check(csha(parses) == result["commitments"]["parse_content_sha256"], "parse_content_hash", checks)
    check(all(sha(R / name) == digest for name, digest in result["inputs"].items()), "input_hashes", checks)
    check(all(sha(R / name) == digest for name, digest in result["outputs"].items()), "output_hashes", checks)
    check(sha(RUNNER) == result["implementation"][RUNNER.name] and sha(PARENT) == design["parent_runner_sha256"], "implementation_hashes", checks)
    stored = result.pop("result_content_sha256"); check(csha(result) == stored, "result_content_hash", checks)
    source_text = RUNNER.read_text(); check(not any(x in source_text for x in design["forbidden_inputs"]), "runner_forbidden_input_firewall", checks)
    check(result["blind_firewall"]["forbidden_inputs_opened"] is False and result["blind_firewall"]["oracle_fields_used"] is False and result["blind_firewall"]["voynich_inputs"] == 0 and result["blind_firewall"]["f84r_access"] is False, "firewall_report", checks)
    validation = {"schema": "GDT171_BLIND_INSTRUMENT_VALIDATION_V1", "status": "PASS_INDEPENDENT_NO_ORACLE_V2_BLIND_RECONSTRUCTION",
                  "checks_passed": len(checks), "checks_failed": 0, "checks": checks, "observation_rows": len(obs), "parse_rows": len(parses),
                  "operation_rows": len(ops), "diagnostic_rows": len(diagnostics), "result_sha256": sha(RESULT), "validator_sha256": sha(Path(__file__)),
                  "oracle_files_opened": 0, "voynich_inputs": 0, "f84r_access": False}
    validation["validation_content_sha256"] = csha(validation); OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n")
    print(f"PASS {len(checks)}/{len(checks)}")


if __name__ == "__main__": main()
