#!/usr/bin/env python3
"""Build V78 R1: 381 event-bound segments and eleven continuous records."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = Path(__file__).resolve().parents[3]
V77_DICT = ROOT / "experiments/yolo/sidequest_theory_candidates_v77/V77_SELECTED_CARD_DICTIONARY.tsv"
V73_EVENTS = ROOT / "experiments/yolo/sidequest_theory_candidates_v73/V73_SELECTED_100_EVENT_INTERLINEAR.tsv"
V73_RECORDS = ROOT / "experiments/yolo/sidequest_theory_candidates_v73/V73_SELECTED_FIVE_ARTICLES.tsv"
V74_EVENTS = ROOT / "experiments/yolo/sidequest_theory_candidates_v74/V74_SELECTED_281_EVENT_INTERLINEAR.tsv"
V74_RECORDS = ROOT / "experiments/yolo/sidequest_theory_candidates_v74/V74_SELECTED_SIX_RECORD_EDITION.tsv"
V72_STATEMENTS = ROOT / "experiments/yolo/sidequest_theory_candidates_v72/V72_SELECTED_116_STATEMENTS.tsv"

INPUT_HASHES = {
    V77_DICT: "4aaae864f45ea152da0f44524c515a4f0ba8f61dad5eca09501fbba644c01faf",
    V73_EVENTS: "de9dbc9b7bf834090ee50707f59e3e7f6490844461a7670ad80d720479b645dc",
    V73_RECORDS: "fe38340b28bc32d62a3556569c83edc4ce1b6f87be18e52559bc4b7e9a5f9ee9",
    V74_EVENTS: "201b1126f3922758bf76eb8bd15180ec6a8c38c4b66a5a9e68b4583c5a42cfe3",
    V74_RECORDS: "72776e55d262d81618180f2c6f21fe82376d059986b86dbb782dd91205691ea6",
    V72_STATEMENTS: "3ecd5b902d83bd92cb0a51d7719d5d5c0ebbfcbe28f1a03d65a08ec536aae17f",
}

RECORD_ORDER = ["H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"]
ALLOWED_PAGES = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"}
ET_CARD = "dcda95c81a5460feb191"
PER_CARD = "b5fcea1eaed06b2f2291"
FORMAL_CARDS = {"2f1c5e56e8f0ff459065", "308e8ea2d5d190c498e8"}

# Each role-card event gets exactly one of the two frozen values.  Completion
# material is visibly marked as exemplar ellipsis and is never a card gloss.
SPECIAL = {
    13: ("ET", "UND", "", 1, "joins heating to the following readiness/use clause", "could be a record-state mark rather than a conjunction"),
    27: ("ET", "UND", "", 2, "first member of an A-ET-B-ET-C additive chain", "requires a silent repeated imperative"),
    29: ("ET", "UND", "", 2, "second member of the same additive chain", "the following nonword formal mark makes the right conjunct opaque"),
    56: ("PER", "GEMÄSS", "der örtlichen Vorlage", 3, "field-entry instruction can be introduced by according-to", "no overt complement identifies the governing Vorlage"),
    102: ("PER", "DURCH", "den unmittelbar folgenden Rücklauf", 1, "field-entry through-reading takes the visible next segment as complement", "could instead be a generic entry mark"),
    106: ("ET", "AUCH", "", 1, "adds a measured portion to the same-source phrase", "deictic source is exemplar-supplied"),
    110: ("ET", "UND", "", 2, "adds the next timing clause to the local-station phrase", "left member is nominal/elliptical"),
    114: ("ET", "AUCH", "", 2, "adds the following moderate quantity to the prior-post instruction", "requires an omitted take/use predicate"),
    121: ("ET", "UND", "", 1, "joins rinse completion to keeping the post warm across a field/line carry", "the physical break could instead be a restart"),
    124: ("ET", "UND", "", 1, "joins mixing to standing until ready", "terminal construction could be mere sequencing"),
    133: ("ET", "AUCH", "", 1, "first link in portion-ET-warmth-ET-readiness chain", "portion phrase is elliptical"),
    135: ("ET", "UND", "", 1, "second link in the same three-member chain", "right member could open a fresh instruction"),
    148: ("ET", "UND", "", 2, "adds lower outlet use to lower-basin mention", "two nominal station fragments need a supplied predicate"),
    154: ("ET", "UND", "", 1, "joins tempering to standing until ready", "could be a generic continuation mark"),
    180: ("PER", "DURCH", "den ersten örtlichen Leitungsweg", 3, "field-final through-reading can close the preceding path description", "first of adjacent PER cards; complement boundary is underdetermined"),
    181: ("PER", "GEMÄSS", "derselben örtlichen Einstellung", 3, "field-entry according-to reading can govern the following setting", "second adjacent PER card makes repetition conspicuous"),
    219: ("PER", "DURCH", "das unmittelbar folgende warme Wasser", 2, "internal through-reading takes warm water as local instrument/medium", "not at field entry and complement direction is inferred"),
    236: ("PER", "GEMÄSS", "der örtlichen Ablaufvorgabe", 2, "field-entry according-to reading introduces the lower-outlet instruction", "the preceding drain may instead govern the field"),
    243: ("PER", "GEMÄSS", "der örtlichen Mischvorgabe", 1, "field-entry according-to reading introduces mixing", "could be a construction-entry mark without lexical value"),
    256: ("PER", "GEMÄSS", "der örtlichen Mengenvorgabe", 1, "field-entry according-to reading introduces a measured share", "quantity remains entirely exemplar-supplied"),
    270: ("PER", "GEMÄSS", "der örtlichen Prüfvorgabe", 1, "field-entry according-to reading introduces a local state check", "could be a construction-entry mark without lexical value"),
    295: ("ET", "UND", "", 1, "joins first rinse to the repeated rinse clause", "right repetition requires its predicate from the following event"),
    324: ("ET", "UND", "", 1, "joins application to standing until ready", "could be a generic sequence separator"),
    343: ("ET", "UND", "", 1, "joins mixing to washing twice across a field/line carry", "physical break could instead restart"),
    366: ("ET", "UND", "", 2, "joins station assignment to the until-warm condition", "left phrase lacks an overt imperative after V77 withdrawal"),
    370: ("ET", "UND", "", 2, "joins the nonword formal mark to the second-opening phrase", "left conjunct has no lexical content"),
    376: ("ET", "UND", "", 2, "first link in opening-ET-formal-ET-filter chain", "middle member is deliberately nonlexical"),
    378: ("ET", "UND", "", 2, "second link in the same three-member chain", "middle member is deliberately nonlexical"),
}

IMPERATIVE_OR_FINITE_START = re.compile(
    r"\b(Nimm|Säubere|Führe|Zerschneide|Gib|Gieße|Fange|Gebrauche|Bewahre|Erwärme|"
    r"Sammle|Zerstoße|Presse|Vereinige|Rühre|Wring|Lass|Lasse|Seihe|Warte|Setze|"
    r"Miss|Wasche|Verwende|Beende|Lege|Mische|Streiche|Trockne|Zerreibe|Verwahre|"
    r"Wende|Halte|Beginne|Fahre|Ziehe|Schließe|Öffne|Benutze|Fülle|Richte|Tauche|"
    r"Koche|Wiederhole|Entferne|Trenne|Bedecke|Kühle|Drücke|Nimmst|Behalte|Spüle|"
    r"Verschließe|Bereite|Verarbeite|Stelle|Entnimm)\b",
    re.IGNORECASE,
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def clean_phrase(text: str) -> str:
    return text.strip().rstrip(". ")


def is_explicit_clause(text: str) -> bool:
    clean = clean_phrase(text)
    if IMPERATIVE_OR_FINITE_START.search(clean):
        return True
    return any(marker in clean for marker in (" bestätigt ", " entsteht", " erreicht ist", " wird", " ist "))


def main() -> None:
    for path, expected in INPUT_HASHES.items():
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected, f"input changed: {path}"

    dictionary_rows = read_tsv(V77_DICT)
    dictionary = {r["joint_tuple_id"]: r for r in dictionary_rows}
    assert len(dictionary) == 24
    assert dictionary[ET_CARD]["minimal_editorial_gloss"] == "ET?__UND_ODER_AUCH?"
    assert dictionary[PER_CARD]["minimal_editorial_gloss"] == "PER?__DURCH_ODER_GEMAESS?"
    assert {card for card, r in dictionary.items() if r["decision"] == "FORMAL_LABEL_NOT_WORD"} == FORMAL_CARDS

    herbal_events = read_tsv(V73_EVENTS)
    bio_events = read_tsv(V74_EVENTS)
    events = herbal_events + bio_events
    assert len(events) == 381
    assert [int(r["event_serial"]) for r in events] == list(range(1, 382))
    assert {r["page"] for r in events} <= ALLOWED_PAGES

    statements = read_tsv(V72_STATEMENTS)
    assert len(statements) == 116
    statement_map = {r["statement_id"]: r for r in statements}
    statement_last = {r["statement_id"]: int(r["event_serials"].split("|")[-1]) for r in statements}

    herbal_records = read_tsv(V73_RECORDS)
    bio_records = read_tsv(V74_RECORDS)
    record_sources = {r["record_unit_id"]: r for r in herbal_records + bio_records}
    assert list(record_sources) == RECORD_ORDER

    first_in_field: dict[str, int] = {}
    last_in_field: dict[str, int] = {}
    for event in events:
        serial = int(event["event_serial"])
        first_in_field.setdefault(event["field_id"], serial)
        last_in_field[event["field_id"]] = serial

    event_rows: list[dict[str, object]] = []
    special_rows: list[dict[str, object]] = []
    per_record_segments: dict[str, list[str]] = defaultdict(list)
    per_record_literal: dict[str, list[str]] = defaultdict(list)
    per_record_source_alignment: dict[str, list[str]] = defaultdict(list)

    for event in events:
        serial = int(event["event_serial"])
        card = event["joint_tuple_id"]
        record = event["record_unit_id"]
        phrase = clean_phrase(event["concrete_german_meaning_in_context"])
        if card == ET_CARD:
            assert serial in SPECIAL and SPECIAL[serial][0] == "ET"
            role, reading, completion, cost, rationale, rival = SPECIAL[serial]
            literal_value = "ET?"
            source_segment = f"[ET?:{reading}?]"
            segment_type = "CODEBOOK_ATTESTED_CATEGORY_ET"
            ellipsis = "NO_NEW_COMPLEMENT"
        elif card == PER_CARD:
            assert serial in SPECIAL and SPECIAL[serial][0] == "PER"
            role, reading, completion, cost, rationale, rival = SPECIAL[serial]
            literal_value = "PER?"
            source_segment = f"[PER?:{reading}?] [EXEMPLAR:{completion} [ELLIPSE:lokales Komplement]]"
            segment_type = "CODEBOOK_ATTESTED_CATEGORY_PER_WITH_EXEMPLAR_COMPLEMENT"
            ellipsis = "EXPLICIT_EXEMPLAR_COMPLEMENT"
        elif card in FORMAL_CARDS:
            role, reading, completion, cost, rationale, rival = "FORMAL", "NONE", "", 0, "nonlexical formal event retained without paraphrase", "any word reading is forbidden"
            literal_value = "[FORMAL; KEIN WORT]"
            source_segment = "[FORMAL; KEIN WORT]"
            segment_type = "FORMAL_NONWORD"
            ellipsis = "NOT_APPLICABLE"
        else:
            role, reading, completion, cost, rationale, rival = "EXEMPLAR", "NONE", "", 0, "concrete phrase is supplied only by the selected local source exemplar", event.get("strongest_alternative", event.get("strongest_bathhouse_technical_or_formal_rival", ""))
            literal_value = "[EXEMPLARWERT UNBEKANNT]"
            if is_explicit_clause(phrase):
                source_segment = f"[EXEMPLAR:{phrase}]"
                ellipsis = "NO"
            else:
                source_segment = f"[EXEMPLAR:{phrase} [ELLIPSE:Prädikat oder Bezug aus dem lokalen Masterexemplar ergänzen]]"
                ellipsis = "YES_EXPLICIT"
            segment_type = "LOCAL_SOURCE_EXEMPLAR"

        owner = event.get("whole_plant_owner", event.get("local_owner_label", ""))
        owner_break = event.get("owner_break_before", "")
        editorial_prefix = ""
        if owner_break == "RECORD_START__RESET_ALL_LOCAL_STATE":
            editorial_prefix = f"[EDITORIAL:RECORDANFANG; LOKALER BESITZER={owner}]"
        elif owner_break == "BREAK_VISIBLE_GAP__RESET_SUBSTANCE_TARGET_DIRECTION":
            editorial_prefix = f"[EDITORIAL:STATIONSWECHSEL ZU {owner}; STOFF, ZIEL UND RICHTUNG NICHT VERERBEN]"
        elif record.startswith("H") and not per_record_segments[record]:
            editorial_prefix = f"[EDITORIAL:RECORDANFANG; GANZPFLANZENBESITZER={owner}]"
        if editorial_prefix:
            per_record_segments[record].append(editorial_prefix)
        per_record_segments[record].append(source_segment)
        if serial == statement_last[event["statement_id"]]:
            per_record_segments[record].append(".")

        literal_token = f"E{serial:03d}:CARD[{card}]={literal_value}"
        per_record_literal[record].append(literal_token)
        per_record_source_alignment[record].append(f"E{serial:03d}=>{source_segment}")
        v77_row = dictionary.get(card)
        v77_decision = v77_row["decision"] if v77_row else "OUTSIDE_BOUNDED_V77_DICTIONARY__EXEMPLAR_VALUE_UNKNOWN"
        statement = statement_map[event["statement_id"]]
        event_rows.append({
            "event_serial": serial,
            "record_unit_id": record,
            "page": event["page"],
            "locus": event["locus"],
            "field_id": event["field_id"],
            "statement_id": event["statement_id"],
            "joint_tuple_id": card,
            "literal_card_order_token": literal_token,
            "v77_dictionary_decision": v77_decision,
            "source_expansion_segment": source_segment,
            "segment_type": segment_type,
            "ellipsis_status": ellipsis,
            "local_owner": owner,
            "owner_break_before": owner_break or "NONE",
            "statement_line_crossing": statement["line_crossing"],
            "statement_ends_after_event": "YES" if serial == statement_last[event["statement_id"]] else "NO",
            "et_per_reading": reading,
            "et_per_fit_cost_0_4": cost,
            "et_per_fit_reason": rationale,
            "strongest_local_rival": rival,
            "source_status": "EXPLORATORY_CONTINUOUS_WORKING_EDITION",
            "semantic_ceiling": "ET_PER_ARE_PROVISIONAL_CATEGORIES;ALL_OTHER_CONCRETE_CONTENT_IS_EXEMPLAR_ONLY;NOT_TRANSLATION",
        })

        if role in {"ET", "PER"}:
            special_rows.append({
                "event_serial": serial,
                "record_unit_id": record,
                "page": event["page"],
                "locus": event["locus"],
                "field_id": event["field_id"],
                "statement_id": event["statement_id"],
                "role_card": role + "?",
                "allowed_reading_used": reading + "?",
                "field_entry": "YES" if first_in_field[event["field_id"]] == serial else "NO",
                "field_exit": "YES" if last_in_field[event["field_id"]] == serial else "NO",
                "explicit_exemplar_completion": completion or "NONE",
                "fit_cost_0_4": cost,
                "fit_grade": {0: "CLEAN", 1: "WORKABLE", 2: "STRAINED", 3: "HIGH_REPAIR", 4: "FAIL"}[cost],
                "fit_reason": rationale,
                "strongest_rival": rival,
                "extra_sense_introduced": "NO",
                "decision": "RETAIN_FOR_THIS_WORKING_EDITION" if cost < 4 else "CONTRADICTED",
            })

    assert len(event_rows) == 381
    assert len(special_rows) == 28
    assert sum(r["role_card"] == "ET?" for r in special_rows) == 19
    assert sum(r["role_card"] == "PER?" for r in special_rows) == 9
    write_tsv(HERE / "V78_R1_381_EVENT_CONTINUOUS_INTERLINEAR.tsv", event_rows, list(event_rows[0]))
    write_tsv(HERE / "V78_R1_ET_PER_28_FIT.tsv", special_rows, list(special_rows[0]))

    statement_by_record: dict[str, list[dict[str, str]]] = defaultdict(list)
    for statement in statements:
        statement_by_record[statement["record_unit_id"]].append(statement)
    event_by_record: dict[str, list[dict[str, object]]] = defaultdict(list)
    for event in event_rows:
        event_by_record[str(event["record_unit_id"])].append(event)
    special_by_record: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in special_rows:
        special_by_record[str(row["record_unit_id"])].append(row)

    record_rows: list[dict[str, object]] = []
    contradiction_rows: list[dict[str, object]] = []
    for record in RECORD_ORDER:
        erows = event_by_record[record]
        srows = statement_by_record[record]
        frows = special_by_record[record]
        source = record_sources[record]
        fluent = " ".join(per_record_segments[record]).replace(" .", ".")
        literal = " | ".join(per_record_literal[record])
        v72_max = max(int(r["repair_cost_0_4"]) for r in srows)
        role_max = max((int(r["fit_cost_0_4"]) for r in frows), default=0)
        total_cost = max(v72_max, role_max)
        crossing = [r["statement_id"] + ":" + r["line_crossing"] for r in srows if r["line_crossing"].startswith("YES")]
        contradiction = source["strongest_contradiction"]
        fit_summary = (
            f"ET={sum(r['role_card']=='ET?' for r in frows)};"
            f"PER={sum(r['role_card']=='PER?' for r in frows)};"
            f"MAX_COST={role_max};"
            + ("EVENTS=" + "|".join(str(r["event_serial"]) for r in frows) if frows else "EVENTS=NONE")
        )
        record_rows.append({
            "record_unit_id": record,
            "page": erows[0]["page"],
            "event_count": len(erows),
            "event_serials": "|".join(str(r["event_serial"]) for r in erows),
            "field_count": len({r["field_id"] for r in erows}),
            "statement_count": len(srows),
            "literal_card_order": literal,
            "source_event_alignment": " | ".join(per_record_source_alignment[record]),
            "continuous_source_expansion": fluent,
            "line_and_field_crossing": "|".join(crossing) if crossing else "NONE",
            "et_per_fit": fit_summary,
            "repair_cost_0_4": total_cost,
            "repair_reason": f"max(V72 statement repair={v72_max}, ET/PER local fit={role_max}); station breaks remain explicit",
            "strongest_conflict": contradiction,
            "strongest_record_rival": source.get("strongest_alternative_article", source.get("strongest_global_rival", "")),
            "reading_status": "COMPLETE_EXPLORATORY_WORKING_EDITION",
            "semantic_ceiling": "CONTINUOUS_SOURCE_EXPANSION_NOT_DECIPHERMENT_OR_CONFIRMED_TRANSLATION",
        })
        contradiction_rows.append({
            "contradiction_id": "REC_" + record,
            "scope": "RECORD",
            "record_unit_id": record,
            "event_serial": "ALL",
            "issue": contradiction,
            "required_repair": "keep owners and station gaps explicit; treat all concrete content as exemplar expansion",
            "repair_cost_0_4": total_cost,
            "disposition": "RETAIN_WITH_VISIBLE_EXEMPLAR_CEILING",
        })

    for row in special_rows:
        contradiction_rows.append({
            "contradiction_id": f"ROLE_E{int(row['event_serial']):03d}",
            "scope": "ET_PER_OCCURRENCE",
            "record_unit_id": row["record_unit_id"],
            "event_serial": row["event_serial"],
            "issue": row["strongest_rival"],
            "required_repair": row["fit_reason"],
            "repair_cost_0_4": row["fit_cost_0_4"],
            "disposition": row["decision"],
        })

    assert len(record_rows) == 11 and sum(int(r["event_count"]) for r in record_rows) == 381
    assert len(contradiction_rows) == 39
    write_tsv(HERE / "V78_R1_11_RECORD_CONTINUOUS.tsv", record_rows, list(record_rows[0]))
    write_tsv(HERE / "V78_R1_CONTRADICTIONS.tsv", contradiction_rows, list(contradiction_rows[0]))

    md = [
        "# V78 R1 — elf kontinuierliche Prosa-Records",
        "",
        "Alle Wörter innerhalb `[EXEMPLAR:…]` stammen aus der kreativen Quellenausweitung; fehlende Prädikate oder Bezüge stehen darin nochmals als `[ELLIPSE:…]`. Nur `ET?` und `PER?` sind die zwei V77-Arbeitshypothesen; `[FORMAL; KEIN WORT]` ist ausdrücklich nicht lexikalisch.",
        "",
    ]
    for row in record_rows:
        md += [
            f"## {row['record_unit_id']} — {row['page']}",
            "",
            f"Ereignisse: {row['event_count']}; Felder: {row['field_count']}; Statements: {row['statement_count']}; Reparaturkosten: {row['repair_cost_0_4']}/4.",
            "",
            "### Literalspur",
            "",
            str(row["literal_card_order"]),
            "",
            "### Flüssige Quellenausweitung",
            "",
            str(row["continuous_source_expansion"]),
            "",
            "### Übergänge, ET/PER und Konflikt",
            "",
            f"- Linien-/Feldübergriff: {row['line_and_field_crossing']}",
            f"- ET/PER-Fit: {row['et_per_fit']}",
            f"- stärkster Konflikt: {row['strongest_conflict']}",
            f"- stärkster Rivale: {row['strongest_record_rival']}",
            "",
        ]
    (HERE / "V78_R1_ELEVEN_RECORDS_CONTINUOUS.md").write_text("\n".join(md).rstrip() + "\n", encoding="utf-8")

    summary = {
        "status": "BUILT",
        "events": len(event_rows),
        "records": len(record_rows),
        "statements": len(statements),
        "et_occurrences": sum(r["role_card"] == "ET?" for r in special_rows),
        "per_occurrences": sum(r["role_card"] == "PER?" for r in special_rows),
        "formal_nonword_occurrences": sum(r["segment_type"] == "FORMAL_NONWORD" for r in event_rows),
        "exemplar_occurrences": sum(r["segment_type"] == "LOCAL_SOURCE_EXEMPLAR" for r in event_rows),
        "explicit_ellipsis_occurrences": sum(str(r["ellipsis_status"]).startswith("YES") or r["ellipsis_status"] == "EXPLICIT_EXEMPLAR_COMPLEMENT" for r in event_rows),
        "contradiction_rows": len(contradiction_rows),
        "pages": sorted({str(r["page"]) for r in event_rows}),
        "sealed_pages_accessed": [],
        "input_hashes": {str(path.relative_to(ROOT)): digest for path, digest in INPUT_HASHES.items()},
    }
    (HERE / "V78_R1_BUILD_SUMMARY.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
