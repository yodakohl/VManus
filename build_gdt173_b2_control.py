#!/usr/bin/env python3
"""Render frozen GDT173 B2 lookup on the exact GDT172 System-A schedule."""
from __future__ import annotations

import csv
import gzip
import hashlib
import json
from collections import Counter
from pathlib import Path

R = Path(__file__).resolve().parent
PARENT_OBS = R / "gdt172_observation_corpus.json.gz"
PARENT_ORACLE = R / "gdt172_sealed_oracle.json.gz"
PARENT_FREEZE = R / "gdt172_source_literal_correction_freeze.json"
PARENT_LOOKUP = R / "gdt171_sealed_lexical_lookup.tsv"
LOOKUP = R / "gdt173_b2_lookup.tsv"
FAMILIES = R / "gdt173_b2_family_manifest.tsv"
AUTHOR = R / "author_gdt173_b2_lookup.py"
METHOD = R / "GDT173_HUMAN_GROWN_DISTRIBUTED_CONTROL_METHOD.md"
OBS = R / "gdt173_b2_observation_corpus.json.gz"
ORACLE = R / "gdt173_b2_sealed_oracle.json.gz"
FREEZE = R / "gdt173_b2_source_freeze.json"


def sha(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()
def csha(x) -> str: return hashlib.sha256(json.dumps(x, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()
def load(path: Path):
    with gzip.open(path, "rt", encoding="utf8") as handle: return json.load(handle)
def read(path: Path):
    with path.open(encoding="utf8", newline="") as handle: return list(csv.DictReader(handle, delimiter="\t"))
def write_gzip(path: Path, payload) -> None:
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()
    with path.open("wb") as target:
        with gzip.GzipFile(fileobj=target, mode="wb", mtime=0) as handle: handle.write(raw)
def val(row, field): return "" if row[field] == "NONE" else row[field]


def main() -> None:
    parent_obs_payload, parent_oracle_payload = load(PARENT_OBS), load(PARENT_ORACLE)
    parent_obs = [x for x in parent_obs_payload["rows"] if x["world_view"] == "CONTROL_P"]
    parent_truth_all = {x["observation_id"]: x for x in parent_oracle_payload["rows"]}
    assert len(parent_obs) == 15214 and all(parent_truth_all[x["observation_id"]]["system"] == "SYSTEM_A_V3_UNCHANGED_LITERAL" for x in parent_obs)
    table = read(LOOKUP); parent_lookup = read(PARENT_LOOKUP)
    assert len(table) == len(parent_lookup) == 384
    assert [(x["lexical_id"], x["source_form"], x["source_frequency"]) for x in table] == [(x["lexical_id"], x["source_form"], x["source_frequency"]) for x in parent_lookup]
    by_form = {x["source_form"]: x for x in table}; assert len(by_form) == 384

    obs_rows, oracle_rows = [], []
    for old in parent_obs:
        old_truth = parent_truth_all[old["observation_id"]]; frequent = old_truth["lexical_status"] == "FREQUENT_LEXICAL_ID"
        table_row = by_form.get(old_truth["source_form"])
        assert frequent == (table_row is not None)
        if frequent:
            host = table_row["b2_host"] if old["hand"] == "S1" else table_row["s2_host"]
            left, right, field, lexical_closure = (val(table_row, x) for x in ("b2_left", "b2_right", "b2_field", "b2_lexical_closure"))
            escape = ""; lexical_id = table_row["lexical_id"]
            family_id = table_row["family_id"]; variant_code = table_row["variant_code"]
            render_rule = "IDENTITY_TABLE_HOST_S1" if old["hand"] == "S1" or host == table_row["b2_host"] else "EXPLICIT_FAMILY_S2_FINAL_GLYPH_VARIANT"
        else:
            host = old_truth["source_form"]; left = right = field = lexical_closure = ""
            escape = "w"; lexical_id = "NONE_LITERAL_ESCAPE"; family_id = variant_code = "NONE_LITERAL"
            render_rule = "IDENTITY_UNCHANGED_SOURCE_GRAPHEMATIC_LITERAL"
        record_operator = old_truth["true_record_operator"]; line_frame = old_truth["true_line_frame"]
        positional_right = old_truth["true_positional_right"]; physical_closure = old_truth["true_closure"]
        surface = record_operator + line_frame + escape + left + host + right + field + lexical_closure + positional_right + physical_closure
        oid = "R" + old["observation_id"][1:]
        folio = old["folio_id"].replace("CONTROL_P:", "CONTROL_R:", 1)
        line_id = old["physical_line_id"].replace("CONTROL_P:", "CONTROL_R:", 1)
        observation = dict(old); observation.update({"observation_id": oid, "world_view": "CONTROL_R", "folio_id": folio, "physical_line_id": line_id, "surface_group": surface})
        truth = dict(old_truth); truth.update({"observation_id": oid, "system": "SYSTEM_B2_HUMAN_GROWN_DISTRIBUTED_CONTROL",
            "lexical_id": lexical_id, "canonical_host": table_row["b2_host"] if frequent else host, "rendered_host": host,
            "scribe_render_rule": render_rule, "true_literal_escape": escape, "true_lexical_left": left,
            "true_lexical_right": right, "true_field_marker": field, "true_b2_lexical_closure": lexical_closure,
            "b2_family_id": family_id, "b2_variant_code": variant_code})
        obs_rows.append(observation); oracle_rows.append(truth)

    oracle_rows.sort(key=lambda x: x["observation_id"])
    assert len(obs_rows) == len(oracle_rows) == 15214
    omap = {x["observation_id"]: x for x in oracle_rows}; assert len(omap) == len(oracle_rows)
    for row in obs_rows:
        truth = omap[row["observation_id"]]
        expected = truth["true_record_operator"] + truth["true_line_frame"] + truth["true_literal_escape"] + truth["true_lexical_left"] + truth["rendered_host"] + truth["true_lexical_right"] + truth["true_field_marker"] + truth["true_b2_lexical_closure"] + truth["true_positional_right"] + truth["true_closure"]
        assert row["surface_group"] == expected

    write_gzip(OBS, {"schema": "GDT173_B2_STRICT_OBSERVATION_CORPUS_V1", "rows": obs_rows})
    write_gzip(ORACLE, {"schema": "GDT173_B2_SEALED_ORACLE_V1", "rows": oracle_rows})
    families = read(FAMILIES); parent_freeze = json.loads(PARENT_FREEZE.read_text())
    frequent_rows = sum(x["lexical_status"] == "FREQUENT_LEXICAL_ID" for x in oracle_rows)
    literal_rows = len(oracle_rows) - frequent_rows
    dimensions = {field: len({x[field] for x in table}) for field in ("b2_host", "b2_left", "b2_right", "b2_field", "b2_lexical_closure")}
    cartesian_cells = 1
    for number in dimensions.values(): cartesian_cells *= number
    freeze = {"schema": "GDT173_B2_SOURCE_FREEZE_V1", "status": "FROZEN_B2_TABLE_RENDERER_AND_LAYOUT_BEFORE_BLIND_SCORE",
              "architecture": {"classification": "HUMAN_GROWN_DISTRIBUTED_SYNTHETIC_CONTROL", "lookup_rows": len(table),
                               "host_families": len(families), "family_size_min": min(int(x["lexical_ids"]) for x in families),
                               "family_size_max": max(int(x["lexical_ids"]) for x in families), "variant_codes": len({x["variant_code"] for x in table}),
                               "explicit_exceptions": sum(x["exception_note"] != "NONE" for x in table), "s2_variant_families": sum(x["s2_rule"] != "{}" for x in families),
                               "dimension_cardinalities": dimensions, "possible_cartesian_cells": cartesian_cells,
                               "occupied_lookup_rows": len(table), "cartesian_occupancy": len(table) / cartesian_cells,
                               "complete_factorial_grid": False, "modulo_or_hash_assignment": False, "optimization": False,
                               "renderer_authority": "MATERIALIZED_384_ROW_LOOKUP_PLUS_EXPLICIT_S2_HOST",
                               "rare_channel": "ESCAPE_W_PLUS_UNCHANGED_SOURCE_GRAPHEMATIC_FORM"},
              "counts": {"observation_rows": len(obs_rows), "oracle_rows": len(oracle_rows), "frequent_rows": frequent_rows,
                         "literal_rows": literal_rows, "content_folios": parent_freeze["counts"]["content_folios"],
                         "physical_lines": len({x["physical_line_id"] for x in obs_rows}), "registers": len({x["register"] for x in obs_rows}), "hands": len({x["hand"] for x in obs_rows})},
              "layout_invariants": {"gdt172_control_p_metadata_exact_except_anonymous_world_ids": True, "source_order_exact": True,
                                    "record_line_separator_layout_exact": True, "register_hand_partition_exact": True,
                                    "system_a_regenerated_or_modified": False, "factorial_system_b_regenerated_or_modified": False},
              "inputs": {p.name: sha(p) for p in (PARENT_OBS, PARENT_ORACLE, PARENT_FREEZE, PARENT_LOOKUP, LOOKUP, FAMILIES)},
              "outputs": {p.name: sha(p) for p in (OBS, ORACLE)},
              "commitments": {"observation_content_sha256": csha(obs_rows), "oracle_content_sha256": csha(oracle_rows), "lookup_content_sha256": csha(table), "family_content_sha256": csha(families)},
              "implementation": {AUTHOR.name: sha(AUTHOR), Path(__file__).name: sha(Path(__file__))}, "documents": {METHOD.name: sha(METHOD)},
              "blind_forbidden_until_output_freeze": [ORACLE.name, LOOKUP.name, FAMILIES.name, AUTHOR.name, Path(__file__).name],
              "no_voynich_tuning": True, "voynich_inputs": 0, "f84_access": False,
              "claim_ceiling": "Synthetic B2 instrument freeze only; no Voynich architecture, word, code value, language, meaning, plaintext or translation."}
    freeze["freeze_content_sha256"] = csha(freeze); FREEZE.write_text(json.dumps(freeze, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": freeze["status"], **freeze["counts"], "cartesian_occupancy": freeze["architecture"]["cartesian_occupancy"]}, sort_keys=True))


if __name__ == "__main__": main()
