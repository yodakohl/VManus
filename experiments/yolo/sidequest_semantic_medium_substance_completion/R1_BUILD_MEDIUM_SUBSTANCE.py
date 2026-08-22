#!/usr/bin/env python3
"""Build R1's creative medium/substance workshop edition.

The builder changes only a small named card set in the active application
edition.  It does not read manuscript images or any folio outside that edition.
"""

from __future__ import annotations

import csv
import hashlib
import json
from collections import OrderedDict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = ROOT / "experiments/yolo/sidequest_semantic_application_completion"

DICT_IN = SOURCE / "SELECTED_173_APPLICATION_DICTIONARY.tsv"
EVENT_IN = SOURCE / "SELECTED_381_APPLICATION_INTERLINEAR.tsv"

DICT_OUT = HERE / "R1_173_MEDIUM_SUBSTANCE_DICTIONARY.tsv"
EVENT_OUT = HERE / "R1_381_MEDIUM_SUBSTANCE_INTERLINEAR.tsv"
STATEMENT_OUT = HERE / "R1_116_MEDIUM_SUBSTANCE_SENTENCES.tsv"
RECORD_OUT = HERE / "R1_11_MEDIUM_SUBSTANCE_RECORDS.md"
COMPONENT_OUT = HERE / "R1_MEDIUM_SUBSTANCE_COMPONENTS.tsv"
PARADIGM_OUT = HERE / "R1_MEDIUM_SUBSTANCE_PARADIGM.tsv"
SUMMARY_OUT = HERE / "R1_BUILD_SUMMARY.json"

ALLOWED_PAGES = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sentence_case(text: str) -> str:
    return text[:1].upper() + text[1:] if text else text


def uniq(values: list[str]) -> list[str]:
    return list(OrderedDict.fromkeys(value for value in values if value))


def ov(parse: str, nucleus: str, gloss: str, family: str, strength: str, slots: str, note: str) -> dict[str, str]:
    return {
        "semantic_segmentation": parse,
        "stable_concrete_nucleus_de": nucleus,
        "concrete_word_reading_de": gloss,
        "reading_type": "R1_MEDIUM_SUBSTANCE__" + family,
        "family": family,
        "strength": strength,
        "slots": slots,
        "note": note,
    }


# Every productive component below has one short invariant default.  Singleton
# nomenclator cards remain whole cards; no substance is reverse-engineered from
# a convenient one-glyph substring.
OVERRIDES = {
    # AIR: one medium atom under five learned operational hulls.
    "12efe866f335461823a6": ov("CH_LEARNED+AIR_RUNNING_LIQUID", "AIR=Laufflüssigkeit", "Laufflüssigkeitszulauf", "AIR_RUNNING_LIQUID", "R1_RECURRENT_COMPONENT", "MEDIUM+FLOW_TRANSFER", "AIR contributes only Laufflüssigkeit; CH supplies inlet behavior."),
    "22fb87a5a83e5c3fb510": ov("K_LEARNED+AIR_RUNNING_LIQUID", "AIR=Laufflüssigkeit", "Laufflüssigkeit", "AIR_RUNNING_LIQUID", "R1_RECURRENT_COMPONENT", "MEDIUM", "Basin context realizes the portable running liquid."),
    "7d2404c835b10a2c06af": ov("OK_START+AIR_RUNNING_LIQUID", "OK=starten; AIR=Laufflüssigkeit", "Laufflüssigkeit starten", "AIR_RUNNING_LIQUID", "R1_RECURRENT_COMPOSITION", "MEDIUM+OPERATION+FLOW_TRANSFER", "OK changes the state; AIR remains Laufflüssigkeit."),
    "b154ff779abe5f196c80": ov("S_RENDERER+CHED_LEAD+AIR_RUNNING_LIQUID", "CHED=führen; AIR=Laufflüssigkeit", "Laufflüssigkeit führen", "AIR_RUNNING_LIQUID", "R1_RECURRENT_COMPOSITION", "MEDIUM+FLOW_TRANSFER", "The transfer hull supplies führen; AIR remains Laufflüssigkeit."),
    "8aedd154964a78e555d6": ov("D_RENDERER+AIR_RUNNING_LIQUID+Y_REFERENT+DY_CLOSE", "AIR=Laufflüssigkeit; Y=Posten; DY=Schluss", "Laufflüssigkeit abschließen", "AIR_RUNNING_LIQUID", "R1_RECURRENT_COMPOSITION", "MEDIUM+FLOW_TRANSFER+CLOSE", "The terminal hull closes the run; AIR does not mean closing."),

    # CHEO: the prior 'carrier/extraction liquid' wording is shortened to the
    # reusable material noun AUSZUG.
    "087a47b5423438cd6b6a": ov("CH_RENDERER+OK_ADD+CHEO_EXTRACT", "OK=zugeben; CHEO=Auszug", "Auszug zugeben", "CHEO_EXTRACT", "R1_RECURRENT_COMPONENT", "MEDIUM+OPERATION", "CHEO supplies Auszug in both cards; OK supplies addition."),
    "807591efc3d3f7ddbfab": ov("CHEO_EXTRACT+AR_SOURCE", "CHEO=Auszug; AR=aus", "Auszug entnehmen", "CHEO_EXTRACT", "R1_RECURRENT_COMPONENT", "MEDIUM+SOURCE+OPERATION", "CHEO remains Auszug while AR supplies source direction."),

    # Three learned water cards.  They deliberately do not create a fictive
    # common visible WATER root.
    "cbb42a4fe68068325d6b": ov("DSHE_FRESH_WATER+DY_CLOSE", "DSHE=Frischwasser; DY=Schluss", "Frischwasser; Schluss", "WATER_NOMENCLATOR", "R1_SINGLETON_WHOLE_CARD", "MEDIUM+OPERATION+CLOSE", "The exact card licenses fresh water plus closure; DSHE is not exported globally."),
    "98bdc4244c84cbef3321": ov("RSHEAL_WARM_WATER_WHOLE_CARD", "RSHEAL=Warmwasser", "Warmwasser", "WATER_NOMENCLATOR", "R1_SINGLETON_WHOLE_CARD", "MEDIUM", "Learned whole card at the second opening; no anatomy is encoded."),
    "cb57b696b815fdef9cb7": ov("SHECTHY_BATH_WATER_WHOLE_CARD", "SHECTHY=Badwasser", "Badwasser", "WATER_NOMENCLATOR", "R1_SINGLETON_WHOLE_CARD", "MEDIUM", "The station/measure/rest neighborhood favors bath water over a second generic warm-water card."),

    # Specialist medium/material nomenclator.
    "428a5e3662aa57b4b256": ov("SCHOAL_WINE_DECOCTION_WHOLE_CARD", "SCHOAL=Weinsud", "Weinsud", "SPECIALIST_MEDIUM_DECK", "R1_SINGLETON_WHOLE_CARD", "MEDIUM+PREPARATION", "One compact learned preparation name replaces the sentence-sized 'in wine boil'."),
    "0f18de177ed7c878bf95": ov("DL_BATH_ADDITIVE_WHOLE_CARD", "DL=Badzusatz", "Badzusatz", "SPECIALIST_MEDIUM_DECK", "R1_RECURRENT_WHOLE_CARD", "MEDIUM", "Two occurrences in one bath record retain the same additive noun."),
    "b2812c8283c3a62438bd": ov("KCHY_DRAUGHT_WHOLE_CARD", "KCHY=Trank", "Trank", "SPECIALIST_MEDIUM_DECK", "R1_SINGLETON_WHOLE_CARD", "MEDIUM", "The administration verb is contextual; the card default is the material noun."),
    "883a6708116c342cb10b": ov("SKAR_WARM_POUR_WHOLE_CARD", "SKAR=Warmausguss", "Warmausguss", "SPECIALIST_MEDIUM_DECK", "R1_SINGLETON_WHOLE_CARD", "MEDIUM+FLOW_TRANSFER", "A short learned noun replaces 'erwärmtes Medium ausgießen'; no free SK or AR substance atom is claimed."),

    # Exact cho|sho identity forbids the old context-only honey reading.
    "2cc054357a929df85f64": ov("HO_PLANT_MATERIAL", "HO=Pflanzenstoff", "Pflanzenstoff", "PLANT_MATERIAL", "R1_RECURRENT_EXACT_CARD", "OWNER_ITEM", "All four exact occurrences retain plant material; the former honey expansion is removed."),
}


CONTEXT_BY_EVENT = {
    "E006": "Laufflüssigkeit zulaufen lassen",
    "E040": "Weinsud bereiten",
    "E049": "Als Trank geben",
    "E065": "Auszug daraus entnehmen",
    "E075": "Pflanzenstoff",
    "E078": "Pflanzenstoff",
    "E088": "Pflanzenstoff",
    "E092": "Auszug zugeben",
    "E094": "Pflanzenstoff zugeben",
    "E103": "Laufflüssigkeit",
    "E112": "Badzusatz",
    "E129": "Badzusatz",
    "E189": "Frischwasser zugeben; Schluss",
    "E222": "Warmwasser eingießen",
    "E260": "Laufflüssigkeit starten",
    "E276": "Badwasser",
    "E300": "Laufflüssigkeit führen",
    "E351": "Laufflüssigkeit abschließen",
    "E360": "Warmausguss",
}


PARADIGM = [
    ("01_AIR_RUNNING_LIQUID", "12efe866f335461823a6", "CH+AIR", "RUNNING_LIQUID_INLET"),
    ("01_AIR_RUNNING_LIQUID", "22fb87a5a83e5c3fb510", "K+AIR", "RUNNING_LIQUID"),
    ("01_AIR_RUNNING_LIQUID", "7d2404c835b10a2c06af", "OK+AIR", "START_RUNNING_LIQUID"),
    ("01_AIR_RUNNING_LIQUID", "b154ff779abe5f196c80", "S+CHED+AIR", "LEAD_RUNNING_LIQUID"),
    ("01_AIR_RUNNING_LIQUID", "8aedd154964a78e555d6", "D+AIR+Y+DY", "CLOSE_RUNNING_LIQUID"),
    ("02_CHEO_EXTRACT", "087a47b5423438cd6b6a", "OK+CHEO", "ADD_EXTRACT"),
    ("02_CHEO_EXTRACT", "807591efc3d3f7ddbfab", "CHEO+AR", "TAKE_EXTRACT_FROM_SOURCE"),
    ("03_OR_PREPARATION", "b9d7b6d68209a9019e7a", "CHO+OR", "PLANT_PREPARATION"),
    ("03_OR_PREPARATION", "dec401773c1f0347793d", "OL+OR", "PREVIOUS_PREPARATION"),
    ("03_OR_PREPARATION", "7a4bb8136330ee4e6e56", "OR", "PREPARATION"),
    ("03_OR_PREPARATION", "6afeb5c9ab9f6cbdea0d", "OR+AIN", "PREPARATION_PORTION"),
    ("03_OR_PREPARATION", "10488b911aae52b3b334", "OT+OR", "NEXT_PREPARATION"),
    ("04_WATER_DECK", "cbb42a4fe68068325d6b", "DSHE+DY", "FRESH_WATER_CLOSE"),
    ("04_WATER_DECK", "98bdc4244c84cbef3321", "RSHEAL", "WARM_WATER"),
    ("04_WATER_DECK", "cb57b696b815fdef9cb7", "SHECTHY", "BATH_WATER"),
    ("05_SPECIALIST_MEDIUM", "428a5e3662aa57b4b256", "SCHOAL", "WINE_DECOCTION"),
    ("05_SPECIALIST_MEDIUM", "0f18de177ed7c878bf95", "DL", "BATH_ADDITIVE"),
    ("05_SPECIALIST_MEDIUM", "b5df9126607030b95175", "SHEY", "CLEAR_EXTRACT"),
    ("05_SPECIALIST_MEDIUM", "d4a31dbcf1ed6d9e5aa9", "TSHEY", "RINSE_LIQUID"),
    ("05_SPECIALIST_MEDIUM", "b2812c8283c3a62438bd", "KCHY", "DRAUGHT"),
    ("05_SPECIALIST_MEDIUM", "c71c72da4e09e0833392", "KCHOAR", "CHEST_DRAUGHT"),
    ("05_SPECIALIST_MEDIUM", "883a6708116c342cb10b", "SKAR", "WARM_POUR"),
    ("06_PLANT_MATERIAL", "2cc054357a929df85f64", "HO", "PLANT_MATERIAL"),
]


COMPONENTS = [
    ("AIR", "chair|kair|okair|schedair|dairydy", "Laufflüssigkeit", "RECURRENT_COMPONENT", "The operational hull changes; the medium value remains constant.", "Not necessarily water and not a liquid identity across records."),
    ("CHEO", "chokcheo|cheoar", "Auszug", "RECURRENT_COMPONENT", "OK+CHEO adds it; CHEO+AR takes it from a source.", "No claim that every Auszug is the same physical batch."),
    ("OR", "chor|or|shor|sor|chochor|cholor|olor|otchor|qotchor|orain", "Zubereitung", "INHERITED_RECURRENT_COMPONENT", "Base, previous, next, plant and portion cells remain compositional.", "OR is not oil and not a specific ingredient."),
    ("WATER_DECK", "dshedy|rsheal|shecthy", "Frischwasser | Warmwasser | Badwasser", "LEARNED_WHOLE_CARDS", "Three local water cards occupy distinct workshop slots.", "No productive visible WATER component is claimed."),
    ("SCHOAL", "schoal", "Weinsud", "LEARNED_WHOLE_CARD", "The H3 extraction chain supports a wine-based decoction.", "It does not license O, OL or AL as wine."),
    ("DL", "dl", "Badzusatz", "RECURRENT_WHOLE_CARD", "Twice in the same f81v bath cycle.", "One record does not prove a productive abbreviation."),
    ("SHEY", "cheey|shey", "Klarauszug", "INHERITED_RECURRENT_WHOLE_CARD", "Four filtration endpoints retain the same clear-extract value.", "Not every clear liquid is SHEY."),
    ("TSHEY", "tshey", "Spülflüssigkeit", "INHERITED_WHOLE_CARD", "One rinse position in f82r.", "Its relation to SHEY is not decomposed."),
    ("KCHY_KCHOAR", "kchy|kchoar", "Trank | Brusttrank", "LEARNED_MEDIUM_DECK", "Two administration nouns close Herbal preparation chains.", "A common productive CHY or AR drink atom is not asserted."),
    ("SKAR", "skar", "Warmausguss", "LEARNED_WHOLE_CARD", "One terminal warm-pour position in f83r.", "No free SK/AR decomposition."),
    ("HO", "cho|sho", "Pflanzenstoff", "RECURRENT_EXACT_CARD", "Four exact occurrences on f56r now share one material default.", "It cannot mean honey in only one of four identical events."),
    ("OIL", "NONE", "keine Karte", "NO_ASSIGNMENT", "OL is previous/continuation and OR is preparation.", "Oil remains a plausible recipe ingredient but is not lexically located."),
    ("HONEY", "NONE", "keine Karte", "NO_ASSIGNMENT", "The former sho=honey event violates exact-card invariance.", "Honey remains historically plausible but unlocated."),
]


def build() -> dict[str, object]:
    dictionary = read_tsv(DICT_IN)
    events = read_tsv(EVENT_IN)
    if len(dictionary) != 173 or len(events) != 381:
        raise AssertionError("active application inputs have unexpected dimensions")
    if {row["page"] for row in events} - ALLOWED_PAGES:
        raise AssertionError("event input contains a page outside the fixed seven-page prose set")
    source_by_id = {row["joint_tuple_id"]: row for row in dictionary}
    missing = sorted(set(OVERRIDES) - set(source_by_id))
    if missing:
        raise AssertionError(f"missing override IDs: {missing}")

    dict_fields = list(dictionary[0]) + [
        "medium_previous_segmentation",
        "medium_previous_nucleus_de",
        "medium_previous_gloss_de",
        "medium_revision_family",
        "medium_revision_strength",
        "medium_revision_note",
    ]
    revised_dictionary: list[dict[str, str]] = []
    for source in dictionary:
        row = dict(source)
        selected = OVERRIDES.get(row["joint_tuple_id"])
        if selected:
            row["medium_previous_segmentation"] = row["semantic_segmentation"]
            row["medium_previous_nucleus_de"] = row["stable_concrete_nucleus_de"]
            row["medium_previous_gloss_de"] = row["concrete_word_reading_de"]
            for key in ("semantic_segmentation", "stable_concrete_nucleus_de", "concrete_word_reading_de", "reading_type"):
                row[key] = selected[key]
            row["local_expansion_examples_de"] = "Stofffassung: " + selected["concrete_word_reading_de"]
            row["variation_note"] = row.get("variation_note", "") + "; medium R1: " + selected["note"]
            row["medium_revision_family"] = selected["family"]
            row["medium_revision_strength"] = selected["strength"]
            row["medium_revision_note"] = selected["note"]
        else:
            row.update(
                medium_previous_segmentation="",
                medium_previous_nucleus_de="",
                medium_previous_gloss_de="",
                medium_revision_family="UNCHANGED",
                medium_revision_strength="UNCHANGED",
                medium_revision_note="NOT_APPLICABLE",
            )
        revised_dictionary.append(row)
    by_id = {row["joint_tuple_id"]: row for row in revised_dictionary}

    event_fields = list(events[0]) + [
        "medium_previous_segmentation",
        "medium_previous_nucleus_de",
        "medium_previous_gloss_de",
        "medium_previous_context_de",
        "medium_revision_family",
        "medium_revision_strength",
        "medium_revision_note",
    ]
    revised_events: list[dict[str, str]] = []
    for source in events:
        row = dict(source)
        selected = OVERRIDES.get(row["joint_tuple_id"])
        if selected:
            row["medium_previous_segmentation"] = row["semantic_segmentation"]
            row["medium_previous_nucleus_de"] = row["stable_concrete_nucleus_de"]
            row["medium_previous_gloss_de"] = row["concrete_word_reading_de"]
            row["medium_previous_context_de"] = row["contextual_event_reading_de"]
            card = by_id[row["joint_tuple_id"]]
            row["semantic_segmentation"] = card["semantic_segmentation"]
            row["stable_concrete_nucleus_de"] = card["stable_concrete_nucleus_de"]
            row["concrete_word_reading_de"] = card["concrete_word_reading_de"]
            row["contextual_event_reading_de"] = CONTEXT_BY_EVENT.get(row["event_id"], sentence_case(card["concrete_word_reading_de"]))
            row["workshop_slots"] = selected["slots"]
            row["medium_revision_family"] = selected["family"]
            row["medium_revision_strength"] = selected["strength"]
            row["medium_revision_note"] = selected["note"]
        else:
            row.update(
                medium_previous_segmentation="",
                medium_previous_nucleus_de="",
                medium_previous_gloss_de="",
                medium_previous_context_de="",
                medium_revision_family="UNCHANGED",
                medium_revision_strength="UNCHANGED",
                medium_revision_note="NOT_APPLICABLE",
            )
        revised_events.append(row)

    grouped: dict[str, list[dict[str, str]]] = OrderedDict()
    for row in revised_events:
        grouped.setdefault(row["statement_id"], []).append(row)
    statements: list[dict[str, str]] = []
    statement_fields = [
        "statement_id", "record_unit_id", "page", "loci", "field_ids", "event_ids", "event_count",
        "medium_revised_event_count", "surface_sequence", "card_sequence_de", "event_slot_trace",
        "canonical_slots_present", "workshop_sentence_de", "physical_line_note",
    ]
    slot_order = ["OWNER_ITEM", "SOURCE", "QUANTITY", "MEDIUM", "PREPARATION", "TARGET", "OPERATION", "FLOW_TRANSFER", "STATE_GRADE", "CLOSE"]
    for statement_id, rows in grouped.items():
        present = uniq(slot for row in rows for slot in row["workshop_slots"].split("+"))
        statements.append(
            {
                "statement_id": statement_id,
                "record_unit_id": rows[0]["record_unit_id"],
                "page": rows[0]["page"],
                "loci": "|".join(uniq([row["locus"] for row in rows])),
                "field_ids": "|".join(uniq([row["field_id"] for row in rows])),
                "event_ids": "|".join(row["event_id"] for row in rows),
                "event_count": str(len(rows)),
                "medium_revised_event_count": str(sum(row["medium_revision_family"] != "UNCHANGED" for row in rows)),
                "surface_sequence": " · ".join(row["surface_display"] for row in rows),
                "card_sequence_de": " · ".join(row["concrete_word_reading_de"] for row in rows),
                "event_slot_trace": " | ".join(f"{row['event_id']}[{row['workshop_slots']}]" for row in rows),
                "canonical_slots_present": ">".join(slot for slot in slot_order if slot in present),
                "workshop_sentence_de": sentence_case("; ".join(row["contextual_event_reading_de"] for row in rows)),
                "physical_line_note": rows[-1]["statement_continuation"],
            }
        )

    records: dict[str, list[dict[str, str]]] = OrderedDict()
    for row in statements:
        records.setdefault(row["record_unit_id"], []).append(row)
    markdown = [
        "# R1 — elf vollständige Records nach der Stoffrunde",
        "",
        "Kreative Werkstattlesung. Exakte Karten bleiben invariant; lokale Besitzer und Nachbarn dürfen die Handlung ergänzen.",
        "Die Zeile ist kein Satzschluss. Öl und Honig erhalten keine erzwungene Karte.",
        "",
    ]
    for record_id, rows in records.items():
        markdown.extend([f"## {record_id} — {rows[0]['page']}", ""])
        for index, row in enumerate(rows, 1):
            markdown.append(f"{index}. **{row['statement_id']}** `{row['canonical_slots_present']}` — {row['workshop_sentence_de']}.")
        markdown.append("")
    RECORD_OUT.write_text("\n".join(markdown).rstrip() + "\n", encoding="utf-8")

    event_counts = {ident: 0 for ident in by_id}
    event_ids: dict[str, list[str]] = {ident: [] for ident in by_id}
    statement_ids: dict[str, list[str]] = {ident: [] for ident in by_id}
    pages: dict[str, list[str]] = {ident: [] for ident in by_id}
    for row in revised_events:
        ident = row["joint_tuple_id"]
        event_counts[ident] += 1
        event_ids[ident].append(row["event_id"])
        statement_ids[ident].append(row["statement_id"])
        pages[ident].append(row["page"])

    component_rows = [
        {
            "component_id": ident,
            "visible_realizations": visible,
            "working_default_de": default,
            "status": status,
            "evidence_summary": evidence,
            "important_limit": limit,
        }
        for ident, visible, default, status, evidence, limit in COMPONENTS
    ]
    paradigm_rows = []
    for stage, ident, formula, role in PARADIGM:
        selected = OVERRIDES.get(ident)
        paradigm_rows.append(
            {
                "medium_stage": stage,
                "joint_tuple_id": ident,
                "surface_family": by_id[ident]["surface_family"],
                "formula": formula,
                "working_default_de": by_id[ident]["concrete_word_reading_de"],
                "events": str(event_counts[ident]),
                "event_ids": "|".join(event_ids[ident]),
                "statement_ids": "|".join(uniq(statement_ids[ident])),
                "pages": "|".join(uniq(pages[ident])),
                "medium_role": role,
                "revision_status": selected["strength"] if selected else "INHERITED_ACTIVE_VALUE",
                "important_limit": selected["note"] if selected else "Inherited active exact-card value; tested here without changing it.",
            }
        )

    write_tsv(DICT_OUT, revised_dictionary, dict_fields)
    write_tsv(EVENT_OUT, revised_events, event_fields)
    write_tsv(STATEMENT_OUT, statements, statement_fields)
    write_tsv(COMPONENT_OUT, component_rows, list(component_rows[0]))
    write_tsv(PARADIGM_OUT, paradigm_rows, list(paradigm_rows[0]))

    outputs = (DICT_OUT, EVENT_OUT, STATEMENT_OUT, RECORD_OUT, COMPONENT_OUT, PARADIGM_OUT)
    changed_cards = [row for row in revised_dictionary if row["medium_revision_family"] != "UNCHANGED"]
    changed_events = [row for row in revised_events if row["medium_revision_family"] != "UNCHANGED"]
    changed_statements = [row for row in statements if int(row["medium_revised_event_count"]) > 0]
    summary: dict[str, object] = {
        "schema": "SIDEQUEST_R1_MEDIUM_SUBSTANCE_SUMMARY_V1",
        "status": "PASS",
        "cards": len(revised_dictionary),
        "events": len(revised_events),
        "statements": len(statements),
        "records": len(records),
        "changed_cards": len(changed_cards),
        "changed_events": len(changed_events),
        "changed_statements": len(changed_statements),
        "components": len(component_rows),
        "paradigm_rows": len(paradigm_rows),
        "input_hashes": {str(path.relative_to(ROOT)): sha256(path) for path in (DICT_IN, EVENT_IN)},
        "output_hashes": {str(path.relative_to(ROOT)): sha256(path) for path in outputs},
    }
    SUMMARY_OUT.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary


if __name__ == "__main__":
    print(json.dumps(build(), ensure_ascii=False, indent=2, sort_keys=True))
