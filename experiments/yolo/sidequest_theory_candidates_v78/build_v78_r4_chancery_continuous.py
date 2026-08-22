#!/usr/bin/env python3
"""Build V78 R4 continuous prose records under the selected V77 mini-dictionary."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
V73 = ROOT / "experiments/yolo/sidequest_theory_candidates_v73"
V74 = ROOT / "experiments/yolo/sidequest_theory_candidates_v74"
V77 = ROOT / "experiments/yolo/sidequest_theory_candidates_v77"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def write(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        out = csv.DictWriter(fh, fieldnames=fields, delimiter="\t", lineterminator="\n")
        out.writeheader()
        out.writerows(rows)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def clean_phrase(value: str) -> str:
    value = value.strip()
    while value.endswith((".", ";", ":")):
        value = value[:-1].rstrip()
    return value


def main() -> None:
    dictionary = read(V77 / "V77_SELECTED_CARD_DICTIONARY.tsv")
    d_by_id = {r["joint_tuple_id"]: r for r in dictionary}
    herbal = read(V73 / "V73_SELECTED_100_EVENT_INTERLINEAR.tsv")
    bio = read(V74 / "V74_SELECTED_281_EVENT_INTERLINEAR.tsv")
    assert len(herbal) == 100 and len(bio) == 281

    raw_events: list[dict[str, str]] = []
    for r in herbal:
        raw_events.append({
            "event_serial": r["event_serial"], "record_unit_id": r["record_unit_id"],
            "page": r["page"], "locus": r["locus"], "field_id": r["field_id"],
            "statement_id": r["statement_id"], "joint_tuple_id": r["joint_tuple_id"],
            "owner": r["whole_plant_owner"], "owner_status": r["owner_status"],
            "source_phrase": r["concrete_german_meaning_in_context"],
            "terminal_status": r["terminal_status"],
            "strongest_rival": r["strongest_alternative"],
            "contradiction": r["strongest_contradiction"],
            "section": "HERBAL",
        })
    for r in bio:
        raw_events.append({
            "event_serial": r["event_serial"], "record_unit_id": r["record_unit_id"],
            "page": r["page"], "locus": r["locus"], "field_id": r["field_id"],
            "statement_id": r["statement_id"], "joint_tuple_id": r["joint_tuple_id"],
            "owner": r["local_image_owner"], "owner_status": r["owner_status"],
            "source_phrase": r["concrete_german_meaning_in_context"],
            "terminal_status": r["terminal_status"],
            "strongest_rival": r["strongest_bathhouse_technical_or_formal_rival"],
            "contradiction": r["strongest_contradiction"],
            "section": "BIOLOGICAL",
        })
    raw_events.sort(key=lambda r: int(r["event_serial"]))
    assert [int(r["event_serial"]) for r in raw_events] == list(range(1, 382))

    by_field: dict[str, list[dict[str, str]]] = defaultdict(list)
    by_statement_raw: dict[str, list[dict[str, str]]] = defaultdict(list)
    for r in raw_events:
        by_field[r["field_id"]].append(r)
        by_statement_raw[r["statement_id"]].append(r)

    event_rows: list[dict[str, object]] = []
    fit_rows: list[dict[str, object]] = []
    for r in raw_events:
        tid = r["joint_tuple_id"]
        d = d_by_id.get(tid)
        field_events = by_field[r["field_id"]]
        position = next(i for i, x in enumerate(field_events, 1) if x["event_serial"] == r["event_serial"])
        phrase = clean_phrase(r["source_phrase"])
        if d and d["usable_as_v78_working_word"] == "YES_WITH_QUESTION_MARK":
            word = d["minimal_editorial_gloss"]
            if word.startswith("ET?"):
                literal = "[WORTKANDIDAT:ET?]"
                event_phrase = f"und/auch? [EXEMPLAR:{phrase}]"
                formal_rival = "[FORMAL:ADDITIVER_LINK_ODER_FORTSETZUNG;KEIN_WORT]"
                if len(field_events) == 1:
                    fit = "STRAINED_SINGLETON_CONTINUATION"
                    fit_grade = "STRAINED"
                elif 1 < position < len(field_events):
                    fit = "MEDIAL_ADDITIVE_LINK"
                    fit_grade = "GOOD"
                elif position == 1:
                    fit = "FIELD_INITIAL_ALSO_OR_RESUME"
                    fit_grade = "ACCEPTABLE"
                else:
                    fit = "FIELD_FINAL_OPEN_ADDITION_OR_CARRY"
                    fit_grade = "ACCEPTABLE"
            else:
                literal = "[WORTKANDIDAT:PER?]"
                event_phrase = f"durch/gemäß? [EXEMPLAR:{phrase}]"
                formal_rival = "[FORMAL:ENTRY_ODER_STANDARDSLOT;KEIN_WORT]"
                statement_events = by_statement_raw[r["statement_id"]]
                idx = next(i for i, x in enumerate(statement_events) if x["event_serial"] == r["event_serial"])
                next_same = idx + 1 < len(statement_events) and statement_events[idx + 1]["joint_tuple_id"] == tid
                if position == 1:
                    fit = "FIELD_INITIAL_RELATION_OR_INSTRUCTION_HEAD"
                    fit_grade = "GOOD"
                elif position == len(field_events) and next_same:
                    fit = "LINE_EDGE_CATCHWORD_THEN_RESTART"
                    fit_grade = "GOOD"
                else:
                    fit = "MEDIAL_PRETERMINAL_RELATION"
                    fit_grade = "STRAINED"
            fit_rows.append({
                "event_serial": r["event_serial"], "record_unit_id": r["record_unit_id"],
                "page": r["page"], "locus": r["locus"], "field_id": r["field_id"],
                "statement_id": r["statement_id"], "joint_tuple_id": tid,
                "working_word": word, "position_in_field": position,
                "field_length": len(field_events), "fit_class": fit,
                "fit_grade": fit_grade, "formal_nonword_rival": formal_rival,
                "source_expansion_tested": phrase,
            })
            selected_status = d["selection_status"]
        elif d and d["selection_status"] == "FORMAL_LABEL_NOT_WORD":
            literal = f"[FORMAL:{d['minimal_editorial_gloss']};KEIN_WORT]"
            event_phrase = f"{literal} [EXEMPLAR:{phrase}]"
            word = "NONE"
            selected_status = "FORMAL_LABEL_NOT_WORD"
        else:
            literal = f"[OPAQUE_KARTE:{tid}]"
            event_phrase = f"[EXEMPLAR:{phrase}]"
            word = "NONE"
            selected_status = "EXEMPLAR_VALUE_UNKNOWN"
        event_rows.append({
            "event_serial": r["event_serial"], "section": r["section"],
            "record_unit_id": r["record_unit_id"], "page": r["page"],
            "locus": r["locus"], "field_id": r["field_id"],
            "statement_id": r["statement_id"], "joint_tuple_id": tid,
            "owner": r["owner"], "owner_status": r["owner_status"],
            "position_in_field": position, "field_length": len(field_events),
            "literal_card_order_token": literal, "selected_dictionary_status": selected_status,
            "selected_working_word": word,
            "bracketed_source_expansion": f"[EXEMPLAR:{phrase}]",
            "continuous_event_phrase": event_phrase,
            "terminal_status": r["terminal_status"],
            "strongest_local_rival": r["strongest_rival"],
            "contradiction": r["contradiction"],
            "semantic_ceiling": "WORKING_TRANSLATION_SHAPED_EXEMPLAR_EXPANSION_NOT_DECIPHERMENT",
        })

    event_out = HERE / "V78_R4_381_EVENT_CONTINUOUS_INTERLINEAR.tsv"
    write(event_out, list(event_rows[0]), event_rows)

    by_statement: dict[str, list[dict[str, object]]] = defaultdict(list)
    for r in event_rows:
        by_statement[str(r["statement_id"])].append(r)
    statement_rows: list[dict[str, object]] = []
    for sid, rows in by_statement.items():
        loci = list(dict.fromkeys(str(r["locus"]) for r in rows))
        fields = list(dict.fromkeys(str(r["field_id"]) for r in rows))
        statement_rows.append({
            "statement_id": sid, "record_unit_id": rows[0]["record_unit_id"],
            "page": rows[0]["page"], "field_ids": "|".join(fields),
            "loci": "|".join(loci), "line_crossing": "YES" if len(loci) > 1 else "NO",
            "event_count": len(rows),
            "event_serials": "|".join(str(r["event_serial"]) for r in rows),
            "literal_card_order": " > ".join(str(r["literal_card_order_token"]) for r in rows),
            "continuous_working_translation": " ".join(str(r["continuous_event_phrase"]) for r in rows) + ".",
            "et_occurrences": sum(str(r["selected_working_word"]).startswith("ET?") for r in rows),
            "per_occurrences": sum(str(r["selected_working_word"]).startswith("PER?") for r in rows),
            "exemplar_expansion_count": len(rows),
            "semantic_ceiling": "STATEMENT_CONTINUITY_NOT_PLAINTEXT_CLAUSE",
        })
    statement_rows.sort(key=lambda r: int(str(r["event_serials"]).split("|")[0]))
    assert len(statement_rows) == 116
    statement_out = HERE / "V78_R4_116_STATEMENT_CONTINUITY.tsv"
    write(statement_out, list(statement_rows[0]), statement_rows)

    herbal_records = {r["record_unit_id"]: r for r in read(V73 / "V73_SELECTED_FIVE_ARTICLES.tsv")}
    bio_records = {r["record_unit_id"]: r for r in read(V74 / "V74_SELECTED_SIX_RECORD_EDITION.tsv")}
    by_record: dict[str, list[dict[str, object]]] = defaultdict(list)
    for r in statement_rows:
        by_record[str(r["record_unit_id"])].append(r)
    record_rows: list[dict[str, object]] = []
    for rid in ["H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"]:
        rows = by_record[rid]
        event_ids = [int(x) for row in rows for x in str(row["event_serials"]).split("|")]
        if rid.startswith("H"):
            meta = herbal_records[rid]
            fluent = meta["fluent_article"]
            rival = meta["strongest_alternative_article"]
            contradiction = meta["strongest_contradiction"]
        else:
            meta = bio_records[rid]
            fluent = meta["fluent_record_synopsis"]
            rival = meta["strongest_global_rival"]
            contradiction = meta["strongest_contradiction"]
        record_rows.append({
            "record_unit_id": rid, "page": rows[0]["page"],
            "statement_count": len(rows), "event_count": len(event_ids),
            "event_serials": "|".join(map(str, event_ids)),
            "literal_card_order": " || ".join(str(r["literal_card_order"]) for r in rows),
            "event_bound_continuous_working_translation": " ".join(str(r["continuous_working_translation"]) for r in rows),
            "fluent_content_expansion": f"[GESAMT_EXEMPLAR:{clean_phrase(fluent)}]",
            "et_occurrences": sum(int(r["et_occurrences"]) for r in rows),
            "per_occurrences": sum(int(r["per_occurrences"]) for r in rows),
            "strongest_complete_rival": rival,
            "strongest_contradiction": contradiction,
            "record_reading_status": "COMPLETE_CREATIVE_WORKING_TRANSLATION_NOT_DECIPHERMENT",
        })
    record_out = HERE / "V78_R4_11_CONTINUOUS_RECORDS.tsv"
    write(record_out, list(record_rows[0]), record_rows)
    readable_out = HERE / "V78_R4_COMPLETE_RECORD_READINGS.md"
    readable_parts = [
        "# V78 R4 — complete continuous record readings",
        "",
        "Every concrete phrase below is a master-exemplar expansion. Only `ET?` and `PER?` are portable working-word candidates; brackets are not decoded plaintext.",
        "",
    ]
    for row in record_rows:
        readable_parts.extend([
            f"## {row['record_unit_id']} — {row['page']}",
            "",
            f"Events: {row['event_count']}; statements: {row['statement_count']}; ET?: {row['et_occurrences']}; PER?: {row['per_occurrences']}.",
            "",
            "### Literal/event-bound layer",
            "",
            str(row["event_bound_continuous_working_translation"]),
            "",
            "### Fluent whole-record exemplar expansion",
            "",
            str(row["fluent_content_expansion"]),
            "",
            "### Strongest rival",
            "",
            str(row["strongest_complete_rival"]),
            "",
            "### Strongest contradiction",
            "",
            str(row["strongest_contradiction"]),
            "",
        ])
    readable_out.write_text("\n".join(readable_parts).rstrip() + "\n", encoding="utf-8")
    fit_out = HERE / "V78_R4_ET_PER_FIT_AUDIT.tsv"
    write(fit_out, list(fit_rows[0]), fit_rows)

    checks = {
        "events_381": len(event_rows) == 381,
        "event_serials_exact_1_381": [int(r["event_serial"]) for r in event_rows] == list(range(1, 382)),
        "statements_116": len(statement_rows) == 116,
        "records_11": len(record_rows) == 11,
        "event_membership_once": sum(int(r["event_count"]) for r in record_rows) == 381,
        "et_19": sum(r["working_word"].startswith("ET?") for r in fit_rows) == 19,
        "per_9": sum(r["working_word"].startswith("PER?") for r in fit_rows) == 9,
        "fit_rows_28": len(fit_rows) == 28,
        "every_concrete_source_phrase_bracketed": all(str(r["bracketed_source_expansion"]).startswith("[EXEMPLAR:") for r in event_rows),
        "no_empty_event_phrase": all(str(r["continuous_event_phrase"]).strip() for r in event_rows),
        "no_f84": all(not str(r["page"]).startswith("f84") for r in event_rows),
        "no_new_dictionary_word": set(r["selected_working_word"] for r in event_rows) <= {"NONE", "ET?__UND_ODER_AUCH?", "PER?__DURCH_ODER_GEMAESS?"},
    }
    bindings = {}
    for p in [
        V73 / "V73_SELECTED_100_EVENT_INTERLINEAR.tsv",
        V73 / "V73_SELECTED_FIVE_ARTICLES.tsv",
        V74 / "V74_SELECTED_281_EVENT_INTERLINEAR.tsv",
        V74 / "V74_SELECTED_SIX_RECORD_EDITION.tsv",
        V77 / "V77_SELECTED_CARD_DICTIONARY.tsv",
        event_out, statement_out, record_out, readable_out, fit_out,
    ]:
        bindings[p.name] = digest(p)
    validation = {
        "schema": "SIDEQUEST_V78_R4_VALIDATION_V1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "counts": {"events": len(event_rows), "statements": len(statement_rows), "records": len(record_rows), "et_per_fit_rows": len(fit_rows)},
        "bindings": bindings,
    }
    (HERE / "V78_R4_VALIDATION.json").write_text(json.dumps(validation, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if validation["status"] != "PASS":
        raise SystemExit(json.dumps(validation, indent=2))
    print(json.dumps(validation, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
