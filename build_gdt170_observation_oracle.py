#!/usr/bin/env python3
"""Render frozen GDT168 controls into strict observation and sealed oracle layers."""
from __future__ import annotations
import csv
import gzip
import hashlib
import json
from collections import defaultdict
from pathlib import Path

R = Path(__file__).resolve().parent
OLD_OBS = R / "gdt168_blind_synthetic_corpora.json.gz"
OLD_TRUTH = R / "gdt168_synthetic_ground_truth.json.gz"
CODEBOOK = R / "gdt168_codebook_truth.tsv"
FREEZE168 = R / "gdt168_source_encoder_freeze.json"
METHOD = R / "GDT170_FULL_OBSERVATION_INSTRUMENT_METHOD.md"
OBS = R / "gdt170_observation_corpus.json.gz"
ORACLE = R / "gdt170_sealed_oracle.json.gz"
PAGES = R / "gdt170_observation_page_manifest.tsv"
SCHEMA = R / "gdt170_observation_schema.tsv"
FREEZE = R / "gdt170_observation_oracle_freeze.json"
RECORDS_PER_FOLIO = 6


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def csha(value): return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()
def hid(text, n=20): return hashlib.sha256(text.encode()).hexdigest()[:n]


def write_gzip(path, payload):
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()
    with path.open("wb") as target:
        with gzip.GzipFile(fileobj=target, mode="wb", mtime=0) as handle: handle.write(raw)


def write_tsv(path, rows):
    with path.open("w", encoding="utf8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def main():
    with gzip.open(OLD_OBS, "rt", encoding="utf8") as handle: old = json.load(handle)
    with gzip.open(OLD_TRUTH, "rt", encoding="utf8") as handle: truth_payload = json.load(handle)
    assert old["schema"] == "GDT168_BLIND_SYNTHETIC_CORPORA_V1"
    assert truth_payload["schema"] == "GDT168_SYNTHETIC_GROUND_TRUTH_V1"
    blind = old["rows"]; truth = {x["blind_id"]: x for x in truth_payload["rows"]}
    assert len(blind) == len(truth) == 240000 and {x["blind_id"] for x in blind} == set(truth)

    reference = [x for x in blind if x["corpus_view"] == "CONTROL_X" and x["renderer"] == "R1_S1"]
    records_by_unit = defaultdict(set)
    for x in reference: records_by_unit[x["source_unit_id"]].add(x["record_id"])
    layout = {}; page_ordinal = 0
    for unit in sorted(records_by_unit):
        records = sorted(records_by_unit[unit])
        for offset in range(0, len(records), RECORDS_PER_FOLIO):
            for paragraph, record in enumerate(records[offset:offset + RECORDS_PER_FOLIO]):
                layout[record] = (page_ordinal, paragraph)
            page_ordinal += 1
    assert len(layout) == 678

    observations = []; oracle_rows = []; page_acc = defaultdict(lambda: {"lines": set(), "groups": 0, "paragraphs": set()})
    for old_row in blind:
        true = truth[old_row["blind_id"]]
        po, paragraph = layout[old_row["record_id"]]
        world = old_row["corpus_view"]; renderer = old_row["renderer"]
        folio = f"{world}:{renderer}:F{po:04d}"
        line_in_para = int(old_row["line_index"])
        line_ordinal = paragraph * 3 + line_in_para
        line_id = f"{folio}:L{line_ordinal:02d}"
        group_index = int(old_row["position_in_line"]) + 1
        remaining = int(old_row["record_length"]) - line_in_para * 6
        group_count = min(6, max(0, remaining))
        assert 1 <= group_index <= group_count
        paragraph_start = int(line_in_para == 0)
        paragraph_end = int((line_in_para + 1) * 6 >= int(old_row["record_length"]))
        oid = "O" + hid(f"GDT170|{world}|{renderer}|{po}|{paragraph}|{line_in_para}|{group_index}")
        obs = {
            "observation_id": oid, "world_view": world, "witness_renderer": renderer,
            "register": old_row["register"], "hand": old_row["scribe"],
            "folio_id": folio, "layout_folio_ordinal": po, "physical_line_id": line_id,
            "line_ordinal_on_folio": line_ordinal, "group_index": group_index, "group_count": group_count,
            "surface_group": old_row["surface"],
            "left_separator": "LINE_START" if group_index == 1 else "CONFIDENT_SPACE",
            "right_separator": "LINE_END" if group_index == group_count else "CONFIDENT_SPACE",
            "paragraph_start": paragraph_start, "paragraph_end": paragraph_end,
            "line_layout_role": "PARAGRAPH_OPENING" if paragraph_start else "PARAGRAPH_CONTINUATION",
            "page_layout_role": "MULTI_RECORD_MEDICAL_PAGE",
            "annotation_provenance": "SYNTHETIC_EXACT_LAYOUT_OBSERVATION",
            "annotation_tags": "MEDICAL_APOTHECARY_SOURCE;REPEATED_PARAGRAPH_RECORD",
            "annotation_confidence": "EXACT_GENERATED_LAYOUT",
        }
        observations.append(obs)
        oracle_rows.append({
            "observation_id": oid, "system": true["system"], "original_blind_id": old_row["blind_id"],
            "source_unit_full": true["source_unit_full"], "plaintext_form": true["plaintext_form"],
            "concept_index": true["concept_index"], "true_record_id": old_row["record_id"],
            "true_record_slot": true["slot"], "true_record_length": old_row["record_length"],
            "canonical_a_code": true["canonical_a_code"], "canonical_host": true["canonical_host"],
            "rendered_host": old_row["page_host"], "true_wrapper": old_row["wrapper"],
            "true_local_frame": old_row["local_frame"], "true_right_family": old_row["right_family"],
            "true_closure_value": old_row["closure_value"], "true_dy_closure": old_row["dy_closure"],
            "true_b3": old_row["b3"], "wrapper_digit": true["wrapper_digit"],
            "right_digit": true["right_digit"], "closure_digit": true["closure_digit"],
        })
        page_acc[folio]["lines"].add(line_id); page_acc[folio]["groups"] += 1; page_acc[folio]["paragraphs"].add(paragraph)

    observations.sort(key=lambda x: (x["world_view"], x["witness_renderer"], int(x["layout_folio_ordinal"]), int(x["line_ordinal_on_folio"]), int(x["group_index"])))
    oracle_rows.sort(key=lambda x: x["observation_id"])
    assert len(observations) == len(oracle_rows) == 240000
    forbidden = {"concept_index", "plaintext_form", "canonical_host", "rendered_host", "true_record_slot", "true_wrapper", "true_right_family", "true_b3", "page_host", "wrapper", "right_family", "dy_closure", "b3", "record_id", "source_unit_id"}
    assert not forbidden.intersection(observations[0])

    page_rows = []
    for folio, acc in sorted(page_acc.items()):
        world, renderer, page = folio.split(":")
        register, hand = renderer.split("_")
        page_rows.append({"folio_id": folio, "world_view": world, "witness_renderer": renderer,
                          "register": register, "hand": hand, "layout_folio_ordinal": int(page[1:]),
                          "physical_lines": len(acc["lines"]), "visible_paragraphs": len(acc["paragraphs"]),
                          "source_groups": acc["groups"], "page_layout_role": "MULTI_RECORD_MEDICAL_PAGE",
                          "annotation_tags": "MEDICAL_APOTHECARY_SOURCE;REPEATED_PARAGRAPH_RECORD"})

    schema_rows = []
    for field in observations[0]:
        cls = "VISIBLE_SURFACE" if field == "surface_group" else ("SOURCE_SEPARATOR" if field.endswith("separator") else ("REGISTER_HAND" if field in {"register", "hand", "witness_renderer"} else ("PERMITTED_LAYOUT_ANNOTATION" if field.startswith("annotation_") or field.endswith("layout_role") or field.startswith("paragraph_") else "PHYSICAL_LOCATOR")))
        schema_rows.append({"field": field, "evidence_class": cls, "oracle_forbidden": 0, "blind_parser_allowed": 1})
    for field in sorted(forbidden): schema_rows.append({"field": field, "evidence_class": "SEALED_ORACLE_ONLY", "oracle_forbidden": 1, "blind_parser_allowed": 0})

    write_gzip(OBS, {"schema": "GDT170_STRICT_OBSERVATION_CORPUS_V1", "rows": observations})
    write_gzip(ORACLE, {"schema": "GDT170_SEALED_ORACLE_V1", "rows": oracle_rows})
    write_tsv(PAGES, page_rows); write_tsv(SCHEMA, schema_rows)
    freeze = {
        "schema": "GDT170_OBSERVATION_ORACLE_FREEZE_V1", "status": "FROZEN_STRICT_OBSERVATION_AND_SEALED_ORACLE_BEFORE_BLIND_PARSE",
        "counts": {"observation_rows": len(observations), "oracle_rows": len(oracle_rows), "synthetic_folios": len(page_rows),
                   "content_folio_ordinals": page_ordinal, "worlds": 2, "renderers_per_world": 10},
        "observation_allowed_fields": list(observations[0]), "observation_forbidden_fields": sorted(forbidden),
        "oracle_fields": list(oracle_rows[0]), "records_per_folio": RECORDS_PER_FOLIO,
        "alternate_renderers_are_not_replications": True, "no_voynich_tuning": True,
        "inputs": {p.name: sha(p) for p in (OLD_OBS, OLD_TRUTH, CODEBOOK, FREEZE168)},
        "implementation": {Path(__file__).name: sha(Path(__file__))},
        "outputs": {p.name: sha(p) for p in (OBS, ORACLE, PAGES, SCHEMA)},
        "commitments": {"observation_content_sha256": csha(observations), "oracle_content_sha256": csha(oracle_rows)},
        "documents": {METHOD.name: sha(METHOD)},
        "voynich_inputs": 0, "f84r_access": False,
        "claim_ceiling": "Synthetic instrument freeze only; no Voynich word, code value, language, meaning, plaintext, or translation.",
    }
    freeze["freeze_content_sha256"] = csha(freeze)
    FREEZE.write_text(json.dumps(freeze, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": freeze["status"], **freeze["counts"]}, sort_keys=True))


if __name__ == "__main__": main()
