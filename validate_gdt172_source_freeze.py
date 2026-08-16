#!/usr/bin/env python3
"""Independent invariant validator for the GDT172 literal correction."""
from __future__ import annotations

import csv
import gzip
import hashlib
import json
from pathlib import Path

R = Path(__file__).resolve().parent
OLD_OBS = R / "gdt171_observation_corpus.json.gz"
OLD_ORACLE = R / "gdt171_sealed_oracle.json.gz"
LOOKUP = R / "gdt171_sealed_lexical_lookup.tsv"
OBS = R / "gdt172_observation_corpus.json.gz"
ORACLE = R / "gdt172_sealed_oracle.json.gz"
AUDIT = R / "gdt172_literal_change_audit.tsv"
FREEZE = R / "gdt172_source_literal_correction_freeze.json"
PRODUCER = R / "build_gdt172_literal_correction.py"
OUT = R / "gdt172_source_freeze_validation.json"


def sha(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()
def csha(x) -> str: return hashlib.sha256(json.dumps(x, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()
def load(path: Path):
    with gzip.open(path, "rt", encoding="utf8") as h: return json.load(h)
def read(path: Path):
    with path.open(encoding="utf8", newline="") as h: return list(csv.DictReader(h, delimiter="\t"))
def check(v, label, checks):
    if not v: raise AssertionError(label)
    checks.append(label)


def main() -> None:
    checks = []
    old_obs_p, old_oracle_p, obs_p, oracle_p = load(OLD_OBS), load(OLD_ORACLE), load(OBS), load(ORACLE)
    old_obs, old_oracle, obs, oracle = old_obs_p["rows"], old_oracle_p["rows"], obs_p["rows"], oracle_p["rows"]
    freeze, audit, lookup = json.loads(FREEZE.read_text()), read(AUDIT), read(LOOKUP)
    check(freeze["status"] == "FROZEN_LITERAL_ONLY_CORRECTION_BEFORE_BLIND_RERUN", "freeze_status", checks)
    check(obs_p["schema"] == "GDT172_STRICT_OBSERVATION_CORPUS_V1" and oracle_p["schema"] == "GDT172_SEALED_ORACLE_V1", "schemas", checks)
    check(len(obs) == len(oracle) == len(old_obs) == len(old_oracle) == 30428, "row_counts", checks)
    old_o, new_o = {x["observation_id"]: x for x in old_oracle}, {x["observation_id"]: x for x in oracle}
    check(len(old_o) == len(new_o) == 30428 and [x["observation_id"] for x in obs] == [x["observation_id"] for x in old_obs], "ids_and_order", checks)
    check(len(lookup) == 384 and sha(LOOKUP) == freeze["inputs"][LOOKUP.name], "lookup_frozen", checks)
    frequent = literal = changed_literal = 0
    for old_row, row in zip(old_obs, obs):
        check({k: v for k, v in row.items() if k != "surface_group"} == {k: v for k, v in old_row.items() if k != "surface_group"}, "layout_exact", checks)
        ot, nt = old_o[row["observation_id"]], new_o[row["observation_id"]]
        expected_system = "SYSTEM_A_V3_UNCHANGED_LITERAL" if ot["system"] == "SYSTEM_A_V2" else "SYSTEM_B_FACTORIAL_DISTRIBUTED_CONTROL_V3"
        check(nt["system"] == expected_system, "system_label_only", checks)
        fixed = set(ot) - {"system", "canonical_host", "rendered_host", "scribe_render_rule"}
        check(all(nt[k] == ot[k] for k in fixed), "oracle_fields_frozen", checks)
        if ot["lexical_status"] == "FREQUENT_LEXICAL_ID":
            frequent += 1
            check(row["surface_group"] == old_row["surface_group"], "frequent_surface_exact", checks)
            check((nt["canonical_host"], nt["rendered_host"], nt["scribe_render_rule"]) == (ot["canonical_host"], ot["rendered_host"], ot["scribe_render_rule"]), "frequent_oracle_exact", checks)
        else:
            literal += 1
            check(nt["true_literal_escape"] == "w" and nt["canonical_host"] == nt["source_form"] == nt["rendered_host"], "literal_unchanged_form", checks)
            check(nt["scribe_render_rule"] == "IDENTITY_UNCHANGED_SOURCE_GRAPHEMATIC_LITERAL", "literal_render_rule", checks)
            changed_literal += row["surface_group"] != old_row["surface_group"]
        prefix = nt["true_record_operator"] + nt["true_line_frame"] + nt["true_literal_escape"] + nt["true_lexical_left"]
        suffix = nt["true_lexical_right"] + nt["true_field_marker"] + nt["true_positional_right"] + nt["true_closure"]
        check(row["surface_group"] == prefix + nt["rendered_host"] + suffix, "surface_reconstructs", checks)
    checks = list(dict.fromkeys(checks))
    check((frequent, literal, changed_literal) == (freeze["counts"]["frequent_rows"], freeze["counts"]["literal_rows"], freeze["counts"]["literal_surface_changes"]), "partition_counts", checks)
    check(len(audit) == 2 and all(int(x["frequent_surface_changes"]) == 0 and int(x["literal_surface_changes"]) == int(x["literal_rows"]) for x in audit), "audit_exact", checks)
    check(csha(obs) == freeze["commitments"]["observation_content_sha256"] and csha(oracle) == freeze["commitments"]["oracle_content_sha256"], "content_hashes", checks)
    check(all(sha(R / k) == v for k, v in freeze["inputs"].items()), "input_hashes", checks)
    check(all(sha(R / k) == v for k, v in freeze["outputs"].items()), "output_hashes", checks)
    check(sha(PRODUCER) == freeze["implementation"][PRODUCER.name], "producer_hash", checks)
    stored = freeze.pop("freeze_content_sha256"); check(csha(freeze) == stored, "freeze_content_hash", checks)
    check(freeze["voynich_inputs"] == 0 and freeze["f84_access"] is False and freeze["no_voynich_tuning"], "no_voynich_or_f84", checks)
    result = {"schema": "GDT172_SOURCE_FREEZE_VALIDATION_V1", "status": "PASS_INDEPENDENT_LITERAL_ONLY_CORRECTION",
              "checks_passed": len(checks), "checks_failed": 0, "checks": checks,
              "observation_rows": len(obs), "frequent_rows": frequent, "literal_rows": literal,
              "result_sha256": sha(FREEZE), "validator_sha256": sha(Path(__file__)), "voynich_inputs": 0, "f84_access": False}
    result["validation_content_sha256"] = csha(result)
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(f"PASS {len(checks)}/{len(checks)}")


if __name__ == "__main__": main()
