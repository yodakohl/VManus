#!/usr/bin/env python3
"""Independent source/layout/oracle validator for the GDT171 v2 freeze."""
from __future__ import annotations

import csv
import gzip
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

R = Path(__file__).resolve().parent
SOURCE = R / "gdt159_diplomatic_corpora.json.gz"
OBS = R / "gdt171_observation_corpus.json.gz"
ORACLE = R / "gdt171_sealed_oracle.json.gz"
LOOKUP = R / "gdt171_sealed_lexical_lookup.tsv"
MANIFEST = R / "gdt171_register_folio_manifest.tsv"
SCHEMA = R / "gdt171_observation_schema.tsv"
FREEZE = R / "gdt171_source_observation_oracle_freeze.json"
PRODUCER = R / "build_gdt171_historical_controls.py"
OUT = R / "gdt171_source_freeze_validation.json"
HOST_ALPHABET = "abcefghijlmnpstuvxz"


def sha(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()
def csha(value) -> str: return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()
def hnum(text: str) -> int: return int(hashlib.sha256(text.encode()).hexdigest()[:16], 16)
def hid(text: str, n: int = 18) -> str: return hashlib.sha256(text.encode()).hexdigest()[:n]


def base_code(number: int, width: int) -> str:
    out = []
    for _ in range(width): out.append(HOST_ALPHABET[number % len(HOST_ALPHABET)]); number //= len(HOST_ALPHABET)
    assert number == 0
    return "".join(reversed(out))


def literal_code(form: str) -> str: return "".join(base_code(x, 2) for x in form.encode("utf8"))


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf8", newline="") as handle: return list(csv.DictReader(handle, delimiter="\t"))


def load(path: Path):
    with gzip.open(path, "rt", encoding="utf8") as handle: return json.load(handle)


def check(value: bool, label: str, checks: list[str]) -> None:
    if not value: raise AssertionError(label)
    checks.append(label)


def main() -> None:
    checks: list[str] = []; freeze = json.loads(FREEZE.read_text())
    source = [x for x in load(SOURCE)["records"] if x["corpus_id"] == "LATIN_MEDICAL_GRAPHEMATIC"]
    obs_payload, oracle_payload = load(OBS), load(ORACLE); obs, oracle = obs_payload["rows"], oracle_payload["rows"]
    lookup_file, manifest, schema = read(LOOKUP), read(MANIFEST), read(SCHEMA)
    lookup = [{k: ("" if v == "NONE" else v) for k, v in row.items()} for row in lookup_file]
    check(freeze["status"] == "FROZEN_HISTORICAL_V2_BEFORE_BLIND_PARSE", "freeze_status", checks)
    check(len(source) == 12000 and len({x["form"] for x in source}) == 6175 and len({x["unit_id"] for x in source}) == 21, "source_census", checks)
    freq = Counter(x["form"] for x in source); ranked = sorted(freq, key=lambda x: (-freq[x], hid(x, 64))); frequent = ranked[:384]
    check(sum(freq[x] for x in frequent) == 4678 and freq[frequent[-1]] == 4, "bounded_vocabulary_census", checks)
    check(len(lookup) == 384 and [x["source_form"] for x in lookup] == frequent, "lookup_frequency_order", checks)
    check([x["lexical_id"] for x in lookup] == [f"LEX{i:03d}" for i in range(384)], "lexical_ids_exact", checks)
    check(len({x["system_a_host"] for x in lookup}) == 384, "system_a_hosts_injective", checks)
    check(len({(x["system_b_host"], x["system_b_lexical_left"], x["system_b_lexical_right"], x["system_b_field_marker"]) for x in lookup}) == 384,
          "system_b_explicit_rows_unique", checks)
    check(obs_payload["schema"] == "GDT171_STRICT_OBSERVATION_CORPUS_V1" and oracle_payload["schema"] == "GDT171_SEALED_ORACLE_V1", "payload_schemas", checks)
    check(len(obs) == len(oracle) == 30428, "row_counts", checks)
    omap = {x["observation_id"]: x for x in oracle}; check(len(omap) == len(oracle) and set(omap) == {x["observation_id"] for x in obs}, "oracle_join_exact", checks)
    allowed, forbidden = set(freeze["observation_allowed_fields"]), set(freeze["observation_forbidden_fields"])
    check(all(set(x) == allowed and not forbidden.intersection(x) for x in obs), "strict_observation_fields", checks)
    check({x["world_view"] for x in obs} == {"CONTROL_P", "CONTROL_Q"} and Counter(x["world_view"] for x in obs) == {"CONTROL_P": 15214, "CONTROL_Q": 15214}, "world_counts", checks)
    check({x["system"] for x in oracle} == {"SYSTEM_A_V2", "SYSTEM_B_V2"}, "oracle_systems", checks)

    lookup_by_form = {x["source_form"]: x for x in lookup}; lexical_index = {form: i for i, form in enumerate(frequent)}
    variant_rows = 0; literal_rows = frequent_rows = 0
    sequence = defaultdict(list); hands = defaultdict(set); registers = defaultdict(set)
    for row in obs:
        truth = omap[row["observation_id"]]; system = truth["system"]
        check((row["world_view"] == "CONTROL_P") == (system == "SYSTEM_A_V2"), "world_system_mapping", checks)
        frequent_row = lookup_by_form.get(truth["source_form"])
        if frequent_row:
            frequent_rows += 1; check(truth["lexical_status"] == "FREQUENT_LEXICAL_ID" and truth["lexical_id"] == frequent_row["lexical_id"], "frequent_lexical_truth", checks)
            expected = frequent_row["system_a_host"] if system == "SYSTEM_A_V2" else frequent_row["system_b_host"]
        else:
            literal_rows += 1; check(truth["lexical_status"] == "LITERAL_ESCAPE" and truth["lexical_id"] == "NONE_LITERAL_ESCAPE", "literal_truth", checks)
            expected = literal_code(truth["source_form"]); check(truth["true_literal_escape"] == "w", "literal_escape_marker", checks)
        check(truth["canonical_host"] == expected, "canonical_host_exact", checks)
        rendered = expected
        index = lexical_index.get(truth["source_form"])
        if row["hand"] == "S2" and index is not None and index % 17 == 0:
            rendered = expected[:-1] + HOST_ALPHABET[(HOST_ALPHABET.index(expected[-1]) + 1) % len(HOST_ALPHABET)]; variant_rows += 1
            check(truth["scribe_render_rule"] == "S2_FINAL_GLYPH_SHARED_ALPHABET_VARIANT", "scribe_variant_tag", checks)
        else: check(truth["scribe_render_rule"] == "IDENTITY_SHARED_ALPHABET", "scribe_identity_tag", checks)
        check(truth["rendered_host"] == rendered, "rendered_host_exact", checks)
        prefix = truth["true_record_operator"] + truth["true_line_frame"] + truth["true_literal_escape"] + truth["true_lexical_left"]
        suffix = truth["true_lexical_right"] + truth["true_field_marker"] + truth["true_positional_right"] + truth["true_closure"]
        check(row["surface_group"] == prefix + rendered + suffix, "surface_reconstructs", checks)
        check(9 <= int(truth["true_record_length"]) <= 27 and 4 <= int(row["group_count"]) <= 9, "variable_layout_ranges", checks)
        if row["world_view"] == "CONTROL_P":
            sequence[truth["source_unit_full"], row["register"]].append((int(row["layout_folio_ordinal"]), int(row["line_ordinal_on_folio"]), int(row["group_index"]), int(truth["true_source_occurrence_index"]), truth["source_form"]))
            hands[truth["source_unit_full"], row["register"]].add(row["hand"]); registers[truth["source_unit_full"]].add(row["register"])
    checks = list(dict.fromkeys(checks))
    check(frequent_rows + literal_rows == len(obs) and frequent_rows > 0 and literal_rows > 0, "lexical_literal_partition_nonempty", checks)
    # Duplicated register witnesses change the exact frequent count, so verify against oracle directly.
    check(Counter(x["lexical_status"] for x in oracle) == {"FREQUENT_LEXICAL_ID": frequent_rows, "LITERAL_ESCAPE": literal_rows}, "lexical_status_counts", checks)
    check(variant_rows > 0 and variant_rows < frequent_rows // 10, "small_scribe_variant_rate", checks)
    check(all(len(v) == 1 for v in hands.values()), "one_hand_per_register_unit", checks)
    check(Counter(len(v) for v in registers.values()) == {1: 15, 2: 6}, "controlled_partial_overlap_units", checks)

    source_by_unit = defaultdict(list)
    for x in source: source_by_unit[x["unit_id"]].append(x)
    for values in source_by_unit.values(): values.sort(key=lambda x: (int(x["occurrence_index"]), x["fold_id"], x["form"]))
    for (unit, register), values in sequence.items():
        values.sort(); observed = [(x[3], x[4]) for x in values]; expected = [(int(x["occurrence_index"]), x["form"]) for x in source_by_unit[unit]]
        check(observed == expected, "real_source_order_preserved", checks)
    checks = list(dict.fromkeys(checks))
    check(len(manifest) == 176 and all(3 <= int(x["records"]) <= 7 for x in manifest), "folio_record_ranges", checks)
    check(sum(int(x["source_groups"]) for x in manifest) == 15214, "manifest_group_total", checks)
    check({x["register"] for x in manifest} == {"R1", "R2", "R3", "R4"} and {x["hand"] for x in manifest} == {"S1", "S2"}, "manifest_register_hands", checks)
    schema_allowed = {x["field"] for x in schema if x["blind_parser_allowed"] == "1"}; schema_forbidden = {x["field"] for x in schema if x["oracle_forbidden"] == "1"}
    check(schema_allowed == allowed and schema_forbidden == forbidden, "schema_policy_exact", checks)
    typed_lookup_file = [{**x, "source_frequency": int(x["source_frequency"])} for x in lookup_file]
    check(csha(obs) == freeze["commitments"]["observation_content_sha256"] and csha(oracle) == freeze["commitments"]["oracle_content_sha256"] and csha(typed_lookup_file) == freeze["commitments"]["lookup_content_sha256"], "content_hashes", checks)
    check(all(sha(R / name) == digest for name, digest in freeze["inputs"].items()), "input_hashes", checks)
    check(all(sha(R / name) == digest for name, digest in freeze["outputs"].items()), "output_hashes", checks)
    check(sha(PRODUCER) == freeze["implementation"][PRODUCER.name], "producer_hash", checks)
    stored = freeze.pop("freeze_content_sha256"); check(csha(freeze) == stored, "freeze_content_hash", checks)
    check(freeze["no_voynich_tuning"] and freeze["voynich_inputs"] == 0 and freeze["f84r_access"] is False, "no_voynich_f84", checks)
    result = {"schema": "GDT171_SOURCE_FREEZE_VALIDATION_V1", "status": "PASS_INDEPENDENT_HISTORICAL_V2_SOURCE_ORACLE_RECONSTRUCTION",
              "checks_passed": len(checks), "checks_failed": 0, "checks": checks, "observation_rows": len(obs), "oracle_rows": len(oracle),
              "content_folios": len(manifest), "lexical_ids": len(lookup), "result_sha256": sha(FREEZE), "validator_sha256": sha(Path(__file__)),
              "voynich_inputs": 0, "f84r_access": False}
    result["validation_content_sha256"] = csha(result); OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(f"PASS {len(checks)}/{len(checks)}")


if __name__ == "__main__": main()
