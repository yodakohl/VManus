#!/usr/bin/env python3
"""Run the unchanged GDT171 blind instrument on corrected GDT172 surfaces."""
from __future__ import annotations

import csv
import gzip
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

from run_gdt170_blind_instrument import (
    annotation_scores, compatibility, discover, greedy_alignment, held_gain,
    host_signature, parse_token, record_metrics, short_and_substitution,
)

R = Path(__file__).resolve().parent
SOURCE = R / "gdt172_observation_corpus.json.gz"
SOURCE_FREEZE = R / "gdt172_source_literal_correction_freeze.json"
DESIGN = R / "gdt172_blind_design.json"
METHOD = R / "GDT172_LITERAL_ESCAPE_CORRECTION_METHOD.md"
PARENT_RUNNER = R / "run_gdt170_blind_instrument.py"
PARSES = R / "gdt172_blind_parses.json.gz"
OPERATIONS = R / "gdt172_blind_operations.tsv"
DIAGNOSTICS = R / "gdt172_blind_diagnostics.tsv"
RESULT = R / "gdt172_blind_result.json"
MODES = ("SURFACE_ONLY", "VMANUS_ANNOTATION_ASSISTED")


def sha(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()
def csha(x) -> str: return hashlib.sha256(json.dumps(x, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()


def write_tsv(path: Path, rows: list[dict]) -> None:
    fields = []
    for row in rows:
        for field in row:
            if field not in fields: fields.append(field)
    with path.open("w", encoding="utf8", newline="") as handle:
        writer = csv.DictWriter(handle, fields, delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows([{field: row.get(field, "NA") for field in fields} for row in rows])


def write_gzip(path: Path, payload) -> None:
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()
    with path.open("wb") as target:
        with gzip.GzipFile(fileobj=target, mode="wb", mtime=0) as handle: handle.write(raw)


def main() -> None:
    design = json.loads(DESIGN.read_text()); freeze = json.loads(SOURCE_FREEZE.read_text())
    assert design["status"] == "FROZEN_UNCHANGED_GDT171_INSTRUMENT_BEFORE_LITERAL_SENSITIVITY_PARSE"
    assert design["parent_runner_sha256"] == sha(R / "run_gdt171_blind_instrument.py")
    with gzip.open(SOURCE, "rt", encoding="utf8") as handle: payload = json.load(handle)
    assert payload["schema"] == "GDT172_STRICT_OBSERVATION_CORPUS_V1"; rows = payload["rows"]
    assert len(rows) == 30428 and all(set(x) == set(freeze["observation_allowed_fields"]) for x in rows)
    by_world = defaultdict(list)
    for row in rows: by_world[row["world_view"]].append(row)
    assert Counter({k: len(v) for k, v in by_world.items()}) == Counter({"CONTROL_P": 15214, "CONTROL_Q": 15214})

    parse_rows, operation_rows, diagnostic_rows = [], [], []
    parsed_by = {}
    for world, values in sorted(by_world.items()):
        left, right, stats, envelope, counts = discover(values); ann = annotation_scores(values, left, right)
        selected = {("LEFT", x) for x in left} | {("RIGHT", x) for x in right}
        for item in stats:
            if (item["side"], item["operation"]) not in selected: continue
            operation_rows.append({"world_view": world, "scope": "ALL_PARTITIONED_REGISTERS", "side": item["side"], "operation": item["operation"],
                                   "selected_rank": (left.index(item["operation"]) + 1) if item["side"] == "LEFT" else (right.index(item["operation"]) + 1),
                                   "distinct_hosts": item["distinct_hosts"], "exact_pair_types": item["exact_pair_types"],
                                   "synthetic_folios": item["synthetic_folios"], "transformed_occurrences": item["transformed_occurrences"],
                                   "annotation_rank_adjustment": ann.get((item["side"], item["operation"]), 0.0)})
        for mode in MODES:
            cache = {token: parse_token(token, counts, left, right, envelope, mode, ann) for token in counts}
            parsed = []
            for row in values:
                item = {"observation_id": row["observation_id"], "world_view": world, "witness_renderer": row["witness_renderer"],
                        "register": row["register"], "hand": row["hand"], "folio_id": row["folio_id"],
                        "layout_folio_ordinal": row["layout_folio_ordinal"], "physical_line_id": row["physical_line_id"],
                        "line_ordinal_on_folio": row["line_ordinal_on_folio"], "group_index": row["group_index"],
                        "group_count": row["group_count"], "paragraph_start": row["paragraph_start"],
                        "paragraph_end": row["paragraph_end"], "right_separator": row["right_separator"],
                        "surface_group": row["surface_group"], "parser_level": mode, **cache[row["surface_group"]]}
                parsed.append(item); parse_rows.append(item)
            parsed_by[world, mode] = parsed
            rec = record_metrics(parsed); comp = compatibility(set(counts), left, right, world + mode)
            short, same, external = short_and_substitution(parsed)
            base = {"world_view": world, "scope": "ALL_PARTITIONED_REGISTERS", "parser_level": mode}
            diagnostic_rows.extend([
                {**base, "diagnostic": "RECORD_ARCHITECTURE", **rec},
                {**base, "diagnostic": "OPERATION_COMPATIBILITY", **comp},
                {**base, "diagnostic": "SHORT_HOST_STRUCTURE", **short},
                {**base, "diagnostic": "SAME_GROUP_SUBSTITUTION", **same},
                {**base, "diagnostic": "EXTERNAL_CONTEXT_SUBSTITUTION", **external},
                {**base, "diagnostic": "HELD_CONTEXT", **held_gain(parsed, "NEXT_HOST")},
                {**base, "diagnostic": "HELD_CONTEXT", **held_gain(parsed, "WHOLE_LINE")},
            ])

    for world in sorted(by_world):
        for mode in MODES:
            values = parsed_by[world, mode]; by_register = defaultdict(list)
            for row in values: by_register[row["register"]].append(row)
            regs = sorted(by_register)
            for i, left_reg in enumerate(regs):
                for right_reg in regs[i + 1:]:
                    a_rows, b_rows = by_register[left_reg], by_register[right_reg]
                    a_panel = [x for x, _ in Counter(x["inferred_host"] for x in a_rows).most_common(100)]
                    b_panel = [x for x, _ in Counter(x["inferred_host"] for x in b_rows).most_common(100)]
                    a, b = host_signature(a_rows, a_panel), host_signature(b_rows, b_panel)
                    diagnostic_rows.append({"world_view": world, "scope": "REGISTER_PAIR", "parser_level": mode,
                                            "diagnostic": "REGISTER_GEOMETRY_ALIGNMENT", "left_register": left_reg,
                                            "right_register": right_reg, "panel_hosts": min(len(a), len(b)),
                                            "greedy_matched_mean_cosine": greedy_alignment(a, b)})

    parse_rows.sort(key=lambda x: (x["parser_level"], x["world_view"], int(x["layout_folio_ordinal"]), int(x["line_ordinal_on_folio"]), int(x["group_index"])))
    write_gzip(PARSES, {"schema": "GDT172_BLIND_PARSES_V1", "rows": parse_rows})
    write_tsv(OPERATIONS, operation_rows); write_tsv(DIAGNOSTICS, diagnostic_rows)
    summary = {}
    for world in sorted(by_world):
        for mode in MODES:
            values = parsed_by[world, mode]
            summary[world + "|" + mode] = {"inferred_host_types": len({x["inferred_host"] for x in values}),
                                             "mean_operation_count": sum(int(x["operation_count"]) for x in values) / len(values),
                                             "surface_exact_host_rate": sum(x["inferred_host"] == x["surface_group"] for x in values) / len(values)}
    result = {"schema": "GDT172_BLIND_INSTRUMENT_RESULT_V1", "status": "GDT172_BLIND_OUTPUTS_FROZEN_BEFORE_ORACLE_EVALUATION",
              "counts": {"observation_rows": len(rows), "parse_rows": len(parse_rows), "operation_rows": len(operation_rows),
                         "diagnostic_rows": len(diagnostic_rows), "anonymous_worlds": len(by_world), "content_folios": freeze["counts"]["content_folios"]},
              "summary": summary,
              "inputs": {p.name: sha(p) for p in (SOURCE, SOURCE_FREEZE, DESIGN, PARENT_RUNNER)},
              "outputs": {PARSES.name: sha(PARSES), OPERATIONS.name: sha(OPERATIONS), DIAGNOSTICS.name: sha(DIAGNOSTICS)},
              "commitments": {"parse_content_sha256": csha(parse_rows), "diagnostic_content_sha256": csha(diagnostic_rows)},
              "implementation": {Path(__file__).name: sha(Path(__file__))}, "documents": {METHOD.name: sha(METHOD)},
              "blind_firewall": {"read_files": [SOURCE.name, SOURCE_FREEZE.name, DESIGN.name, PARENT_RUNNER.name, METHOD.name],
                                   "forbidden_inputs_opened": False, "oracle_fields_used": False, "voynich_inputs": 0, "f84_access": False},
              "claim_ceiling": "Blind synthetic literal-channel sensitivity outputs only; no Voynich word, code value, language, meaning, plaintext, or translation."}
    result["result_content_sha256"] = csha(result); RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": result["status"], **result["counts"]}, sort_keys=True))


if __name__ == "__main__": main()
