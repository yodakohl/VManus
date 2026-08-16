#!/usr/bin/env python3
"""Build historically plausible GDT171 observation and sealed oracle layers."""
from __future__ import annotations

import csv
import gzip
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

R = Path(__file__).resolve().parent
SOURCE = R / "gdt159_diplomatic_corpora.json.gz"
PROVENANCE = R / "gdt159_diplomatic_source_provenance.json"
METHOD = R / "GDT171_HISTORICAL_PLAUSIBILITY_INSTRUMENT_METHOD.md"
OBS = R / "gdt171_observation_corpus.json.gz"
ORACLE = R / "gdt171_sealed_oracle.json.gz"
CODEBOOK = R / "gdt171_sealed_lexical_lookup.tsv"
MANIFEST = R / "gdt171_register_folio_manifest.tsv"
SCHEMA = R / "gdt171_observation_schema.tsv"
FREEZE = R / "gdt171_source_observation_oracle_freeze.json"

SOURCE_ID = "LATIN_MEDICAL_GRAPHEMATIC"
VOCABULARY_SIZE = 384
HOST_ALPHABET = "abcefghijlmnpstuvxz"  # 19 shared graphematic identities
ESCAPE = "w"
REGISTERS = ("R1", "R2", "R3", "R4")
HANDS = ("S1", "S2")
WORLD = {"SYSTEM_A_V2": "CONTROL_P", "SYSTEM_B_V2": "CONTROL_Q"}


def sha(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()
def csha(value) -> str: return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()
def hnum(text: str) -> int: return int(hashlib.sha256(text.encode()).hexdigest()[:16], 16)
def hid(text: str, n: int = 18) -> str: return hashlib.sha256(text.encode()).hexdigest()[:n]


def base_code(number: int, width: int) -> str:
    out = []
    for _ in range(width): out.append(HOST_ALPHABET[number % len(HOST_ALPHABET)]); number //= len(HOST_ALPHABET)
    assert number == 0
    return "".join(reversed(out))


def literal_code(form: str) -> str:
    # One fixed two-glyph base-19 pair per UTF-8 byte; ESCAPE is a separate field.
    return "".join(base_code(byte, 2) for byte in form.encode("utf8"))


def write_gzip(path: Path, payload) -> None:
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()
    with path.open("wb") as target:
        with gzip.GzipFile(fileobj=target, mode="wb", mtime=0) as handle: handle.write(raw)


def write_tsv(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf8", newline="") as handle:
        writer = csv.DictWriter(handle, list(rows[0]), delimiter="\t", lineterminator="\n"); writer.writeheader(); writer.writerows(rows)


def primary_register(unit: str) -> str:
    if "CLM13027" in unit: return "R1"
    if "H318" in unit: return "R2"
    if "Egerton821" in unit or "Phi_10a135" in unit: return "R3"
    return "R4"


def assigned_registers(unit: str) -> list[str]:
    primary = primary_register(unit); out = [primary]
    if hnum("GDT171_OVERLAP|" + unit) % 5 == 0:
        out.append(REGISTERS[(REGISTERS.index(primary) + 1) % len(REGISTERS)])
    return out


def chunks(total: int, seed_key: str, lo: int, hi: int) -> list[int]:
    out = []; used = 0; index = 0
    while used < total:
        remain = total - used
        if remain <= hi:
            size = remain
        else:
            size = lo + hnum(f"{seed_key}|{index}") % (hi - lo + 1)
            if remain - size < lo: size = remain - lo
        assert lo <= size <= hi
        out.append(size); used += size; index += 1
    assert sum(out) == total and all(lo <= x <= hi for x in out)
    return out


def scribe_variant(host: str, lexical_index: int | None, hand: str) -> tuple[str, str]:
    if hand == "S2" and lexical_index is not None and lexical_index % 17 == 0 and host:
        pos = len(host) - 1; current = HOST_ALPHABET.index(host[pos]); replacement = HOST_ALPHABET[(current + 1) % len(HOST_ALPHABET)]
        return host[:pos] + replacement, "S2_FINAL_GLYPH_SHARED_ALPHABET_VARIANT"
    return host, "IDENTITY_SHARED_ALPHABET"


def main() -> None:
    payload = json.load(gzip.open(SOURCE, "rt", encoding="utf8"))
    rows = [x for x in payload["records"] if x["corpus_id"] == SOURCE_ID]
    assert len(rows) == 12000 and len(HOST_ALPHABET) == 19
    freq = Counter(x["form"] for x in rows)
    ranked = sorted(freq, key=lambda x: (-freq[x], hid(x, 64)))
    frequent = ranked[:VOCABULARY_SIZE]; lexical_index = {form: i for i, form in enumerate(frequent)}
    assert freq[frequent[-1]] == 4 and sum(freq[x] for x in frequent) == 4678

    lookup_rows = []
    for i, form in enumerate(frequent):
        a_host = base_code(i, 2) if i < len(HOST_ALPHABET) ** 2 else base_code(i, 3)
        # Explicit 384-row table.  These values are materialized and audited as rows;
        # the scorer has no arithmetic decoder.
        b_host_bucket = i // 64
        b_left_class = (i // 16) - 4 * b_host_bucket
        b_right_class = (i // 4) - 4 * (i // 16)
        b_field_class = i - 4 * (i // 4)
        lookup_rows.append({"lexical_id": f"LEX{i:03d}", "source_form": form, "source_frequency": freq[form],
                            "system_a_host": a_host, "system_b_host": base_code(b_host_bucket, 2),
                            "system_b_lexical_left": ("", "q", "o", "d")[b_left_class],
                            "system_b_lexical_right": ("", "r", "y", "k")[b_right_class],
                            "system_b_field_marker": ("", "t", "s", "u")[b_field_class]})
    lookup = {row["source_form"]: row for row in lookup_rows}
    assert len({(x["system_b_host"], x["system_b_lexical_left"], x["system_b_lexical_right"], x["system_b_field_marker"]) for x in lookup_rows}) == 384

    by_unit = defaultdict(list)
    for row in rows: by_unit[row["unit_id"]].append(row)
    for values in by_unit.values(): values.sort(key=lambda x: (int(x["occurrence_index"]), x["fold_id"], x["form"]))

    instances = []; folio_manifest = []; folio_serial = 0
    for unit in sorted(by_unit):
        values = by_unit[unit]
        for register in assigned_registers(unit):
            hand = HANDS[hnum(f"GDT171_HAND|{unit}|{register}") % 2]
            record_sizes = chunks(len(values), f"GDT171_RECORD|{unit}|{register}", 9, 27)
            records = []; cursor = 0
            for record_index, record_size in enumerate(record_sizes):
                line_sizes = chunks(record_size, f"GDT171_LINE|{unit}|{register}|{record_index}", 4, 9)
                records.append((record_index, cursor, record_size, line_sizes)); cursor += record_size
            assert cursor == len(values)
            record_cursor = 0
            folio_sizes = chunks(len(records), f"GDT171_FOLIO|{unit}|{register}", 3, 7)
            for per_folio in folio_sizes:
                page_records = records[record_cursor:record_cursor + per_folio]
                page_id = f"F{folio_serial:04d}"; line_on_page = 0
                page_group_count = 0
                for paragraph_ordinal, (record_index, start, record_size, line_sizes) in enumerate(page_records):
                    offset = 0
                    for line_in_record, line_size in enumerate(line_sizes):
                        for position in range(line_size):
                            source_row = values[start + offset + position]
                            instances.append({**source_row, "register": register, "hand": hand, "layout_page": page_id,
                                              "layout_folio_ordinal": folio_serial, "paragraph_ordinal": paragraph_ordinal,
                                              "record_index": record_index, "record_length": record_size,
                                              "record_slot": offset + position, "line_in_record": line_in_record,
                                              "line_count": len(line_sizes), "line_ordinal_on_folio": line_on_page,
                                              "group_index": position + 1, "group_count": line_size})
                            page_group_count += 1
                        offset += line_size; line_on_page += 1
                    assert offset == record_size
                folio_manifest.append({"content_folio_id": page_id, "layout_folio_ordinal": folio_serial, "register": register,
                                       "hand": hand, "source_unit_hash": "U" + hid(unit, 14), "source_unit_overlap_registers": len(assigned_registers(unit)),
                                       "records": len(page_records), "physical_lines": line_on_page, "source_groups": page_group_count})
                folio_serial += 1; record_cursor += len(page_records)
            assert record_cursor == len(records)

    observation_rows = []; oracle_rows = []
    page_counts = Counter()
    for system, world in WORLD.items():
        for occurrence, item in enumerate(instances):
            form = item["form"]; frequent_row = lookup.get(form); is_frequent = frequent_row is not None
            lexical_id = frequent_row["lexical_id"] if is_frequent else "NONE_LITERAL_ESCAPE"
            lexical_i = lexical_index.get(form)
            if system == "SYSTEM_A_V2":
                canonical_host = frequent_row["system_a_host"] if is_frequent else literal_code(form)
                lexical_left = lexical_right = field_marker = ""
            else:
                canonical_host = frequent_row["system_b_host"] if is_frequent else literal_code(form)
                lexical_left = frequent_row["system_b_lexical_left"] if is_frequent else ""
                lexical_right = frequent_row["system_b_lexical_right"] if is_frequent else ""
                field_marker = frequent_row["system_b_field_marker"] if is_frequent else ""
            rendered_host, hand_rule = scribe_variant(canonical_host, lexical_i, item["hand"])
            record_start = item["record_slot"] == 0; line_start = item["group_index"] == 1
            line_end = item["group_index"] == item["group_count"]; record_end = item["record_slot"] == item["record_length"] - 1
            record_operator = "q" if record_start else ("d" if line_start else ("s" if item["record_slot"] % 5 == 0 else ""))
            line_frame = "o" if line_start and not record_start and item["line_in_record"] % 2 == 1 else ""
            literal_escape = ESCAPE if not is_frequent else ""
            positional_right = "r" if item["group_index"] == 1 and not line_end else ""
            closure = "k" if record_end else ("y" if line_end else "")
            surface = record_operator + line_frame + literal_escape + lexical_left + rendered_host + lexical_right + field_marker + positional_right + closure
            folio = f"{world}:{item['register']}:{item['hand']}:{item['layout_page']}"
            line_id = f"{folio}:L{int(item['line_ordinal_on_folio']):02d}"
            oid = "H" + hid(f"GDT171|{system}|{item['register']}|{item['hand']}|{item['layout_page']}|{item['paragraph_ordinal']}|{item['record_slot']}|{occurrence}", 22)
            observation_rows.append({"observation_id": oid, "world_view": world, "witness_renderer": f"{item['register']}_{item['hand']}",
                                     "register": item["register"], "hand": item["hand"], "folio_id": folio,
                                     "layout_folio_ordinal": item["layout_folio_ordinal"], "physical_line_id": line_id,
                                     "line_ordinal_on_folio": item["line_ordinal_on_folio"], "group_index": item["group_index"],
                                     "group_count": item["group_count"], "surface_group": surface,
                                     "left_separator": "LINE_START" if item["group_index"] == 1 else "CONFIDENT_SPACE",
                                     "right_separator": "LINE_END" if line_end else "CONFIDENT_SPACE",
                                     "paragraph_start": int(item["line_in_record"] == 0), "paragraph_end": int(item["line_in_record"] == item["line_count"] - 1),
                                     "line_layout_role": "PARAGRAPH_OPENING" if item["line_in_record"] == 0 else "PARAGRAPH_CONTINUATION",
                                     "page_layout_role": "VARIABLE_TECHNICAL_RECORD_PAGE",
                                     "annotation_provenance": "SYNTHETIC_EXACT_LAYOUT_OBSERVATION",
                                     "annotation_tags": "MEDIEVAL_MEDICAL_SOURCE;VARIABLE_RECORD_LAYOUT",
                                     "annotation_confidence": "EXACT_GENERATED_LAYOUT"})
            oracle_rows.append({"observation_id": oid, "system": system, "source_unit_full": item["unit_id"],
                                "source_form": form, "source_type_hash": "T" + hid(form, 18), "lexical_status": "FREQUENT_LEXICAL_ID" if is_frequent else "LITERAL_ESCAPE",
                                "lexical_id": lexical_id, "true_record_id": f"{item['unit_id']}|{item['register']}|R{item['record_index']:04d}",
                                "true_source_occurrence_index": int(item["occurrence_index"]),
                                "true_record_slot": item["record_slot"], "true_record_length": item["record_length"],
                                "canonical_host": canonical_host, "rendered_host": rendered_host, "scribe_render_rule": hand_rule,
                                "true_record_operator": record_operator, "true_line_frame": line_frame, "true_literal_escape": literal_escape,
                                "true_lexical_left": lexical_left, "true_lexical_right": lexical_right, "true_field_marker": field_marker,
                                "true_positional_right": positional_right, "true_closure": closure})
            page_counts[folio] += 1

    observation_rows.sort(key=lambda x: (x["world_view"], int(x["layout_folio_ordinal"]), int(x["line_ordinal_on_folio"]), int(x["group_index"])))
    oracle_rows.sort(key=lambda x: x["observation_id"])
    forbidden = {"source_form", "source_type_hash", "lexical_status", "lexical_id", "true_record_id", "true_source_occurrence_index", "true_record_slot", "true_record_length",
                 "canonical_host", "rendered_host", "scribe_render_rule", "true_record_operator", "true_line_frame", "true_literal_escape",
                 "true_lexical_left", "true_lexical_right", "true_field_marker", "true_positional_right", "true_closure"}
    assert not forbidden.intersection(observation_rows[0]) and len({x["observation_id"] for x in observation_rows}) == len(observation_rows)
    assert {x["observation_id"] for x in observation_rows} == {x["observation_id"] for x in oracle_rows}

    schema_rows = []
    for field in observation_rows[0]:
        cls = "VISIBLE_SURFACE" if field == "surface_group" else ("SOURCE_SEPARATOR" if field.endswith("separator") else ("REGISTER_HAND" if field in {"register", "hand", "witness_renderer"} else ("PERMITTED_LAYOUT_ANNOTATION" if field.startswith("annotation_") or field.endswith("layout_role") or field.startswith("paragraph_") else "PHYSICAL_LOCATOR")))
        schema_rows.append({"field": field, "evidence_class": cls, "oracle_forbidden": 0, "blind_parser_allowed": 1})
    for field in sorted(forbidden): schema_rows.append({"field": field, "evidence_class": "SEALED_ORACLE_ONLY", "oracle_forbidden": 1, "blind_parser_allowed": 0})
    lookup_file_rows = [{k: ("NONE" if v == "" else v) for k, v in row.items()} for row in lookup_rows]
    write_gzip(OBS, {"schema": "GDT171_STRICT_OBSERVATION_CORPUS_V1", "rows": observation_rows})
    write_gzip(ORACLE, {"schema": "GDT171_SEALED_ORACLE_V1", "rows": oracle_rows})
    write_tsv(CODEBOOK, lookup_file_rows); write_tsv(MANIFEST, folio_manifest); write_tsv(SCHEMA, schema_rows)
    register_counts = Counter((x["register"], x["hand"]) for x in instances)
    freeze = {"schema": "GDT171_SOURCE_OBSERVATION_ORACLE_FREEZE_V1", "status": "FROZEN_HISTORICAL_V2_BEFORE_BLIND_PARSE",
              "source": {"corpus_id": SOURCE_ID, "source_rows": len(rows), "source_types": len(freq), "source_units": len(by_unit),
                         "frequent_lexical_ids": VOCABULARY_SIZE, "frequent_token_rows": sum(freq[x] for x in frequent),
                         "literal_escape_rows_in_unreplicated_source": len(rows) - sum(freq[x] for x in frequent)},
              "architecture": {"record_length_range": [9, 27], "line_length_range": [4, 9], "folio_record_range": [3, 7],
                               "registers": list(REGISTERS), "hands": list(HANDS), "alphabet_permutations": 0,
                               "scribe_variant": "S2_FINAL_GLYPH_SHARED_ALPHABET_VARIANT_FOR_1_OF_17_FREQUENT_IDS",
                               "system_a": "384_ID_INJECTIVE_HOST_PLUS_LITERAL_ESCAPE",
                               "system_b": "384_ROW_EXPLICIT_HOST_LEFT_RIGHT_FIELD_TABLE_PLUS_LITERAL_ESCAPE"},
              "counts": {"layout_instances_per_world": len(instances), "observation_rows": len(observation_rows), "oracle_rows": len(oracle_rows),
                         "content_folios": len(folio_manifest), "world_folios": len(page_counts), "register_hand_rows": {f"{k[0]}_{k[1]}": v for k, v in sorted(register_counts.items())}},
              "observation_allowed_fields": list(observation_rows[0]), "observation_forbidden_fields": sorted(forbidden),
              "oracle_fields": list(oracle_rows[0]), "alternate_registers_are_partial_content_witnesses": True,
              "inputs": {SOURCE.name: sha(SOURCE), PROVENANCE.name: sha(PROVENANCE)},
              "outputs": {p.name: sha(p) for p in (OBS, ORACLE, CODEBOOK, MANIFEST, SCHEMA)},
              "commitments": {"observation_content_sha256": csha(observation_rows), "oracle_content_sha256": csha(oracle_rows), "lookup_content_sha256": csha(lookup_file_rows)},
              "implementation": {Path(__file__).name: sha(Path(__file__))}, "documents": {METHOD.name: sha(METHOD)},
              "no_voynich_tuning": True, "voynich_inputs": 0, "f84r_access": False,
              "claim_ceiling": "Synthetic historical-plausibility instrument freeze only; no Voynich word, code value, language, meaning, plaintext, or translation."}
    freeze["freeze_content_sha256"] = csha(freeze); FREEZE.write_text(json.dumps(freeze, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": freeze["status"], **freeze["counts"], "lexical_ids": VOCABULARY_SIZE}, sort_keys=True))


if __name__ == "__main__": main()
