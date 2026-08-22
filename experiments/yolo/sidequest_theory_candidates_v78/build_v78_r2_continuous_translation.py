#!/usr/bin/env python3
"""Build the independent V78 R2 continuous prose edition.

This builder deliberately imports only the central V72/V73/V74 selected prose
layers and the frozen V77 selected dictionary.  It never assigns a lexical
value from the contextual prose: contextual words remain bracketed EXEMPLAR
expansions throughout.
"""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]

V72_STATEMENTS = ROOT / "experiments/yolo/sidequest_theory_candidates_v72/V72_SELECTED_116_STATEMENTS.tsv"
V73_EVENTS = ROOT / "experiments/yolo/sidequest_theory_candidates_v73/V73_SELECTED_100_EVENT_INTERLINEAR.tsv"
V73_ARTICLES = ROOT / "experiments/yolo/sidequest_theory_candidates_v73/V73_SELECTED_FIVE_ARTICLES.tsv"
V74_EVENTS = ROOT / "experiments/yolo/sidequest_theory_candidates_v74/V74_SELECTED_281_EVENT_INTERLINEAR.tsv"
V74_RECORDS = ROOT / "experiments/yolo/sidequest_theory_candidates_v74/V74_SELECTED_SIX_RECORD_EDITION.tsv"
V77_DICTIONARY = ROOT / "experiments/yolo/sidequest_theory_candidates_v77/V77_SELECTED_CARD_DICTIONARY.tsv"

OUT_EVENTS = HERE / "V78_R2_381_EVENT_INTERLINEAR.tsv"
OUT_RECORDS = HERE / "V78_R2_11_CONTINUOUS_RECORDS.tsv"
OUT_ORDER = HERE / "V78_R2_SOURCE_ORDER_CONTRADICTIONS.tsv"
OUT_RESULT = HERE / "V78_R2_RESULT.json"

ET_CARD = "dcda95c81a5460feb191"
PER_CARD = "b5fcea1eaed06b2f2291"
PARAMETER_CARD = "2f1c5e56e8f0ff459065"
RELATION_CARD = "308e8ea2d5d190c498e8"

RECORD_ORDER = ["H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"]


# Frozen before inspecting any V78 sibling output.  The only hard break is the
# consecutive PER?-PER? sequence with one following complement (E180/E181).
ET_SYNTAX = {
    13: ("PLAUSIBLE_MEDIAL_COORDINATION", "verbindet die Erwärmung mit dem folgenden Bereitschafts-/Gebrauchsglied"),
    27: ("STRONG_REPEATED_COORDINATION_CHAIN", "erstes Bindeglied der sichtbaren A–ET?–B–ET?–C-Folge"),
    29: ("STRONG_REPEATED_COORDINATION_CHAIN", "zweites Bindeglied der sichtbaren A–ET?–B–ET?–C-Folge"),
    106: ("PLAUSIBLE_MEDIAL_COORDINATION", "medial zwischen lokalen Stations-/Mengenquellengliedern"),
    110: ("PLAUSIBLE_MEDIAL_COORDINATION", "medial vor einem Zustands-/Zusatzglied"),
    114: ("PLAUSIBLE_MEDIAL_COORDINATION", "medial vor Mengen- und Parameterquellengliedern"),
    121: ("PLAUSIBLE_ADDITIVE_STATEMENT_CONTINUATION", "eröffnet eine neue formale Aussage, setzt aber denselben sichtbaren Besitzer ohne Stationsbruch fort"),
    124: ("PLAUSIBLE_MEDIAL_COORDINATION", "verbindet Rühren mit einem nachfolgenden Zustandsende"),
    133: ("STRONG_REPEATED_COORDINATION_CHAIN", "erstes Bindeglied einer lokalen ET?–Glied–ET?-Folge"),
    135: ("STRONG_REPEATED_COORDINATION_CHAIN", "zweites Bindeglied derselben lokalen Folge"),
    148: ("PLAUSIBLE_MEDIAL_COORDINATION", "medial zwischen lokalem Becken-/Stellen- und Ablaufglied"),
    154: ("PLAUSIBLE_MEDIAL_COORDINATION", "medial zwischen lokaler Temperierung und Zustandsende"),
    295: ("PLAUSIBLE_ADDITIVE_STATEMENT_CONTINUATION", "Aussageanfang, aber unmittelbare additive Fortsetzung am selben Besitzer"),
    324: ("PLAUSIBLE_MEDIAL_COORDINATION", "medial zwischen örtlichem Gebrauch und Zustandsende"),
    343: ("PLAUSIBLE_MEDIAL_COORDINATION", "medial zwischen Mischung und zweiter Waschhandlung"),
    366: ("STRONG_REPEATED_COORDINATION_CHAIN", "erstes Bindeglied einer lokalen ET?–Gliedfolge"),
    370: ("STRONG_REPEATED_COORDINATION_CHAIN", "zweites Bindeglied derselben lokalen Folge"),
    376: ("STRONG_REPEATED_COORDINATION_CHAIN", "erstes Bindeglied der sichtbaren ET?–Parameter–ET?-Folge"),
    378: ("STRONG_REPEATED_COORDINATION_CHAIN", "zweites Bindeglied derselben Folge"),
}

PER_SYNTAX = {
    56: ("PLAUSIBLE_IF_GOVERNS_NEXT_COMPLEMENT", "PER? kann das unmittelbar folgende örtliche Maß E057 regieren"),
    102: ("PLAUSIBLE_IF_GOVERNS_NEXT_COMPLEMENT", "PER? kann den unmittelbar folgenden Rückstrom E103 regieren"),
    180: ("HARD_SYNTAX_BREAK__CONSECUTIVE_PER_PER_SINGLE_COMPLEMENT", "PER? PER? vor nur einer sichtbaren Ergänzung; keine zweite Bedeutung wird erfunden"),
    181: ("HARD_SYNTAX_BREAK__CONSECUTIVE_PER_PER_SINGLE_COMPLEMENT", "zweites PER? derselben unaufgelösten Doppelung; keine zweite Bedeutung wird erfunden"),
    219: ("PLAUSIBLE_IF_GOVERNS_NEXT_COMPLEMENT", "PER? kann warmes Wasser E220 als instrumentale Ergänzung regieren"),
    236: ("STRAINED_BUT_SINGLE_PREPOSITIONAL_READING", "nur als Durchgang durch den in E237 ergänzten unteren Ablauf; die alte Richtungsphrase wird nicht lexikalisiert"),
    243: ("PLAUSIBLE_IF_GOVERNS_NOMINALIZED_ACTION", "PER? kann das in E244 ergänzte Rühren als instrumentales Glied regieren"),
    256: ("PLAUSIBLE_IF_GOVERNS_NEXT_COMPLEMENT", "PER? kann den abgemessenen Anteil E257 regieren"),
    270: ("PLAUSIBLE_RULE_READING_IF_GOVERNS_NEXT_COMPLEMENT", "PER? kann den örtlichen Prüfzustand E271 als Regel-/Bezugsangabe regieren"),
}


# Small grammatical repairs to the *bracketed source expansion* following PER?.
# They never become card meanings.  Without this frozen declensional repair the
# inherited imperative sentences would falsely test a preposition against a
# finite clause rather than against its plausible complement.
PER_COMPLEMENT_REPAIRS = {
    57: "das örtlich vorgeschriebene Maß",
    103: "den zurücklaufenden Strom",
    182: "dieselbe örtliche Einstellung",
    220: "warmes Wasser",
    237: "den unteren Ablauf",
    244: "Rühren bis zur Gleichmäßigkeit",
    257: "einen abgemessenen Anteil",
    271: "den örtlichen Prüfzustand",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def clean_sentence(text: str) -> str:
    text = " ".join((text or "").split()).strip()
    while text.endswith((".", ";", ":")):
        text = text[:-1].rstrip()
    return text


def exemplar(text: str) -> str:
    return f"[EXEMPLAR:{clean_sentence(text)}]"


def event_owner(row: dict[str, str]) -> tuple[str, str, str]:
    if row["record_unit_id"].startswith("H"):
        owner = row["whole_plant_owner"]
        return owner, owner.replace("_", " ").lower(), "RECORD_START" if int(row["event_serial"]) in {1, 15, 39, 56, 74} else "SAME_OWNER"
    owner = row["local_image_owner"]
    label = row.get("local_owner_label") or owner.replace("_", " ").lower()
    return owner, label, row.get("owner_break_before", "SAME_OWNER")


def literal_layer(card: str, owner: str) -> tuple[str, str, str, str]:
    prefix = f"[OWNER:{owner}; EXEMPLAR] > [OPAQUE_CARD:{card}] > "
    if card == ET_CARD:
        return (
            prefix + "[CODEBOOK-KATEGORIE:ET? (UND/AUCH?)]",
            "PROVISIONAL_CODEBOOK_WORD__QUESTION_MARK_MANDATORY",
            "ET? (UND/AUCH?)",
            "[EXEMPLAR:kein eigener Inhaltswert; nur additive oder koordinierende Verknüpfung der benachbarten Quellenglieder]",
        )
    if card == PER_CARD:
        return (
            prefix + "[CODEBOOK-KATEGORIE:PER? (DURCH/GEMÄSS?)]",
            "PROVISIONAL_CODEBOOK_WORD__QUESTION_MARK_MANDATORY",
            "PER? (DURCH/GEMÄSS?)",
            "[EXEMPLAR:kein eigener Inhaltswert; nur präpositionale Beziehung zum unmittelbar folgenden Quellenglied]",
        )
    if card == PARAMETER_CARD:
        return (
            prefix + "[FORMAL:VORGABEPARAMETER?; KEIN WORT]",
            "FORMAL_LABEL_NOT_WORD",
            "[FORMAL:VORGABEPARAMETER?; KEIN WORT]",
            "",
        )
    if card == RELATION_CARD:
        return (
            prefix + "[FORMAL:LOKALEN_RELATIONSSLOT_SETZEN; KEIN WORT]",
            "FORMAL_LABEL_NOT_WORD",
            "[FORMAL:LOKALEN_RELATIONSSLOT_SETZEN; KEIN WORT]",
            "",
        )
    return (
        prefix + "[EXEMPLARWERT UNBEKANNT]",
        "EXEMPLAR_VALUE_UNKNOWN",
        "[EXEMPLARWERT UNBEKANNT]",
        "",
    )


def separator(prev_card: str | None, card: str) -> str:
    if prev_card in {ET_CARD, PER_CARD} or card in {ET_CARD, PER_CARD}:
        return " "
    return "; "


def main() -> None:
    statements = read_tsv(V72_STATEMENTS)
    statement_map = {row["statement_id"]: row for row in statements}
    dictionary = {row["joint_tuple_id"]: row for row in read_tsv(V77_DICTIONARY)}

    herbal = read_tsv(V73_EVENTS)
    bio = read_tsv(V74_EVENTS)
    raw_events = herbal + bio
    raw_events.sort(key=lambda row: int(row["event_serial"]))

    assert [int(row["event_serial"]) for row in raw_events] == list(range(1, 382))
    assert len(statements) == 116

    event_rows: list[dict[str, object]] = []
    per_hard_breaks: list[int] = []
    for raw in raw_events:
        serial = int(raw["event_serial"])
        card = raw["joint_tuple_id"]
        owner, owner_label, owner_break = event_owner(raw)
        literal, portable_status, portable_token, portable_meta = literal_layer(card, owner)
        phrase = PER_COMPLEMENT_REPAIRS.get(serial, raw["concrete_german_meaning_in_context"])
        source_expansion = exemplar(phrase)

        if card == ET_CARD:
            syntax_status, syntax_reason = ET_SYNTAX[serial]
            fluent_token = portable_token
            source_expansion = portable_meta
        elif card == PER_CARD:
            syntax_status, syntax_reason = PER_SYNTAX[serial]
            fluent_token = portable_token
            source_expansion = portable_meta
            if syntax_status.startswith("HARD_SYNTAX_BREAK"):
                per_hard_breaks.append(serial)
        else:
            syntax_status = "NOT_ET_OR_PER"
            syntax_reason = "keine portable Wortsyntax; der konkrete Inhalt bleibt occurrence-gebundene Quellenausweitung"
            # The literal/nonword status remains explicit in the interlinear
            # layer.  The continuous reading carries only the bracketed source
            # expansion, so it stays readable without silently turning that
            # expansion into a dictionary gloss.
            fluent_token = source_expansion

        selected = statement_map[raw["statement_id"]]
        dict_row = dictionary.get(card)
        rival = raw.get("strongest_alternative") or raw.get("strongest_bathhouse_technical_or_formal_rival", "")
        support = raw.get("v69_support_class") or raw.get("v69_source_status", "")

        event_rows.append(
            {
                "event_serial": serial,
                "event_id": f"E{serial:03d}",
                "record_unit_id": raw["record_unit_id"],
                "page": raw["page"],
                "locus": raw["locus"],
                "field_id": raw["field_id"],
                "statement_id": raw["statement_id"],
                "joint_tuple_id": card,
                "image_owner_id": owner,
                "image_owner_exemplar": exemplar(f"Bildbesitzer {owner_label}"),
                "owner_break_before": owner_break,
                "literal_card_layer": literal,
                "v77_dictionary_decision": dict_row["decision"] if dict_row else "NOT_IN_FROZEN_24_TARGET_DICTIONARY__UNKNOWN",
                "portable_status": portable_status,
                "portable_token_or_formal_prompt": portable_token,
                "source_expansion_de": source_expansion,
                "continuous_event_token": fluent_token,
                "et_per_syntax_status": syntax_status,
                "et_per_syntax_reason": syntax_reason,
                "source_class": selected["source_class"],
                "line_crossing": selected["line_crossing"],
                "terminal_status": raw["terminal_status"],
                "v69_support_or_source_status": support,
                "source_expansion_confidence": raw["meaning_in_context_confidence"],
                "strongest_source_rival": rival,
                "strongest_contradiction": raw["strongest_contradiction"],
                "unsupported_nouns_from_prior_context_layer": raw["unsupported_nouns"],
                "semantic_ceiling": "BRACKETED_SOURCE_EXEMPLAR_NOT_CARD_STEM_SOUND_LANGUAGE_OR_DECIPHERMENT",
            }
        )

    event_fields = [
        "event_serial", "event_id", "record_unit_id", "page", "locus", "field_id", "statement_id",
        "joint_tuple_id", "image_owner_id", "image_owner_exemplar", "owner_break_before",
        "literal_card_layer", "v77_dictionary_decision", "portable_status",
        "portable_token_or_formal_prompt", "source_expansion_de", "continuous_event_token",
        "et_per_syntax_status", "et_per_syntax_reason", "source_class", "line_crossing",
        "terminal_status", "v69_support_or_source_status", "source_expansion_confidence",
        "strongest_source_rival", "strongest_contradiction", "unsupported_nouns_from_prior_context_layer",
        "semantic_ceiling",
    ]
    write_tsv(OUT_EVENTS, event_rows, event_fields)

    by_statement: dict[str, list[dict[str, object]]] = defaultdict(list)
    by_record: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in event_rows:
        by_statement[str(row["statement_id"])].append(row)
        by_record[str(row["record_unit_id"])].append(row)

    def owner_marker(row: dict[str, object], transition: bool) -> str:
        label = str(row["image_owner_exemplar"])[10:-1]
        if transition:
            return exemplar(f"Stationswechsel zu {label}; Stoff, Ziel und Richtung werden nicht vererbt")
        return exemplar(label)

    def statement_text(rows: list[dict[str, object]], with_ids: bool) -> str:
        parts: list[str] = []
        previous_card: str | None = None
        for idx, row in enumerate(rows):
            # A visible owner break can fall *inside* a V72 statement.  It must
            # still reset the local source argument; statements are linguistic
            # groupings, not permission to carry through a disconnected scene.
            marker_needed = str(row["owner_break_before"]).startswith("BREAK_") or (
                idx == 0 and str(row["owner_break_before"]).startswith("RECORD_START")
            )
            if marker_needed:
                if parts:
                    parts.append("; ")
                parts.append(owner_marker(row, str(row["owner_break_before"]).startswith("BREAK_")))
                parts.append("; ")
                previous_card = None
            token = str(row["continuous_event_token"])
            if with_ids:
                token = f"{row['event_id']}={row['literal_card_layer']} {row['source_expansion_de']}"
            if parts and parts[-1] != "; ":
                parts.append(separator(previous_card, str(row["joint_tuple_id"])))
            parts.append(token)
            previous_card = str(row["joint_tuple_id"])
        return "".join(parts).strip() + "."

    statement_rows: list[dict[str, object]] = []
    for selected in statements:
        sid = selected["statement_id"]
        rows = by_statement[sid]
        et_rows = [r for r in rows if r["joint_tuple_id"] == ET_CARD]
        per_rows = [r for r in rows if r["joint_tuple_id"] == PER_CARD]
        syntax_breaks = [r["event_id"] for r in rows if str(r["et_per_syntax_status"]).startswith("HARD_SYNTAX_BREAK")]
        order_model = "HERBAL_RECEPTARIUM_CLAUSE_ORDER" if sid.startswith("H") else "LOCAL_BALNEOLOGICAL_STATION_ARTICLE"
        statement_rows.append(
            {
                "statement_id": sid,
                "record_unit_id": selected["record_unit_id"],
                "page": selected["page"],
                "constituent_fields": selected["constituent_fields"],
                "event_count": len(rows),
                "event_serials": "|".join(str(r["event_serial"]) for r in rows),
                "owner_bindings": selected["owner_bindings"],
                "owner_transition": selected["owner_transition"],
                "source_class": selected["source_class"],
                "source_order_model": order_model,
                "line_crossing": selected["line_crossing"],
                "line_boundary_policy": "PHYSICAL_LINE_IS_NOT_A_SENTENCE_BOUNDARY",
                "et_count": len(et_rows),
                "per_count": len(per_rows),
                "et_per_syntax_statuses": "|".join(str(r["et_per_syntax_status"]) for r in et_rows + per_rows) or "NONE",
                "syntax_break_events": "|".join(syntax_breaks) or "NONE",
                "continuous_statement_reading": statement_text(rows, with_ids=False),
                "event_bound_literal_plus_source": statement_text(rows, with_ids=True),
                "strongest_source_rival": selected["strongest_rival"],
                "repair_cost_0_4": selected["repair_cost_0_4"],
                "repair_reason": selected["repair_reason"],
                "hardest_contradiction": selected["hardest_contradiction"],
                "semantic_ceiling": "HISTORICAL_SOURCE_EXEMPLAR_NOT_TRANSLATION_OR_CARD_VALUE",
            }
        )

    order_fields = [
        "statement_id", "record_unit_id", "page", "constituent_fields", "event_count", "event_serials",
        "owner_bindings", "owner_transition", "source_class", "source_order_model", "line_crossing",
        "line_boundary_policy", "et_count", "per_count", "et_per_syntax_statuses", "syntax_break_events",
        "continuous_statement_reading", "event_bound_literal_plus_source", "strongest_source_rival",
        "repair_cost_0_4", "repair_reason", "hardest_contradiction", "semantic_ceiling",
    ]
    write_tsv(OUT_ORDER, statement_rows, order_fields)

    herbal_articles = {row["record_unit_id"]: row for row in read_tsv(V73_ARTICLES)}
    bio_records = {row["record_unit_id"]: row for row in read_tsv(V74_RECORDS)}
    statements_by_record: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in statement_rows:
        statements_by_record[str(row["record_unit_id"])].append(row)

    record_rows: list[dict[str, object]] = []
    for rid in RECORD_ORDER:
        rows = by_record[rid]
        st_rows = statements_by_record[rid]
        source_meta = herbal_articles.get(rid) or bio_records[rid]
        if rid.startswith("H"):
            source_structure = source_meta["historical_source_structure"]
            strongest_rival = source_meta["strongest_alternative_article"]
            global_contradiction = source_meta["strongest_contradiction"]
        else:
            source_structure = source_meta["historical_station_article_structure"]
            strongest_rival = source_meta["strongest_global_rival"]
            global_contradiction = source_meta["strongest_contradiction"]

        fluent = " ".join(str(s["continuous_statement_reading"]) for s in st_rows)
        event_bound = " ".join(str(s["event_bound_literal_plus_source"]) for s in st_rows)
        breaks = [str(r["event_id"]) for r in rows if str(r["owner_break_before"]).startswith("BREAK_")]
        syntax_breaks = [str(r["event_id"]) for r in rows if str(r["et_per_syntax_status"]).startswith("HARD_SYNTAX_BREAK")]
        record_rows.append(
            {
                "record_unit_id": rid,
                "page": rows[0]["page"],
                "section": "HERBAL" if rid.startswith("H") else "BIOLOGICAL_STATION_ATLAS",
                "event_count": len(rows),
                "event_serials": "|".join(str(r["event_serial"]) for r in rows),
                "field_ids": "|".join(dict.fromkeys(str(r["field_id"]) for r in rows)),
                "statement_ids": "|".join(str(s["statement_id"]) for s in st_rows),
                "owner_sequence": "|".join(dict.fromkeys(str(r["image_owner_id"]) for r in rows)),
                "visible_owner_break_events": "|".join(breaks) or "NONE",
                "historical_source_structure": source_structure,
                "line_policy": "CONTINUOUS_ACROSS_PHYSICAL_LINES__STATEMENT_AND_OWNER_BREAKS_ONLY",
                "et_count": sum(r["joint_tuple_id"] == ET_CARD for r in rows),
                "per_count": sum(r["joint_tuple_id"] == PER_CARD for r in rows),
                "hard_syntax_break_events": "|".join(syntax_breaks) or "NONE",
                "continuous_german_working_reading": fluent,
                "event_bound_literal_plus_source_reading": event_bound,
                "strongest_global_rival": strongest_rival,
                "strongest_global_contradiction": global_contradiction,
                "semantic_ceiling": "COMPLETE_BRACKETED_WORKING_EDITION_NOT_DECIPHERMENT",
            }
        )

    record_fields = [
        "record_unit_id", "page", "section", "event_count", "event_serials", "field_ids", "statement_ids",
        "owner_sequence", "visible_owner_break_events", "historical_source_structure", "line_policy",
        "et_count", "per_count", "hard_syntax_break_events", "continuous_german_working_reading",
        "event_bound_literal_plus_source_reading", "strongest_global_rival", "strongest_global_contradiction",
        "semantic_ceiling",
    ]
    write_tsv(OUT_RECORDS, record_rows, record_fields)

    result = {
        "experiment": "V78_R2_CONTINUOUS_PROSE_EDITION",
        "status": "PASS",
        "independent_role": "R2_HISTORICAL_MEDICAL_HERBAL_SCRIBE",
        "event_rows": len(event_rows),
        "event_coverage": "381/381_EXACTLY_ONCE",
        "statement_rows": len(statement_rows),
        "record_rows": len(record_rows),
        "records": RECORD_ORDER,
        "et_occurrences": sum(r["joint_tuple_id"] == ET_CARD for r in event_rows),
        "et_hard_syntax_breaks": sum(str(r["et_per_syntax_status"]).startswith("HARD_SYNTAX_BREAK") for r in event_rows if r["joint_tuple_id"] == ET_CARD),
        "per_occurrences": sum(r["joint_tuple_id"] == PER_CARD for r in event_rows),
        "per_hard_syntax_break_events": per_hard_breaks,
        "portable_dictionary_words": ["ET? (UND/AUCH?)", "PER? (DURCH/GEMÄSS?)"],
        "formal_nonwords": [
            "[FORMAL:VORGABEPARAMETER?; KEIN WORT]",
            "[FORMAL:LOKALEN_RELATIONSSLOT_SETZEN; KEIN WORT]",
        ],
        "physical_line_policy": "LINES_ARE_NOT_SENTENCE_BOUNDARIES",
        "per_assessment": "PORTABLE_PER_READING_HAS_TWO_HARD_SYNTAX_BREAK_EVENTS__NO_POLYSEMY_RESCUE",
        "et_assessment": "PORTABLE_ET_READING_REMAINS_SYNTACTICALLY_VIABLE_BUT_UNCONFIRMED",
        "semantic_ceiling": "CREATIVE_BRACKETED_SOURCE_EDITION_NOT_CARD_STEM_SOUND_LANGUAGE_OR_DECIPHERMENT",
        "sealed_pages": ["f84", "f84r"],
        "inputs": [str(path.relative_to(ROOT)) for path in [V72_STATEMENTS, V73_EVENTS, V73_ARTICLES, V74_EVENTS, V74_RECORDS, V77_DICTIONARY]],
        "outputs": [path.name for path in [OUT_EVENTS, OUT_RECORDS, OUT_ORDER]],
    }
    OUT_RESULT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
