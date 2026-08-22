#!/usr/bin/env python3
"""Build Rolle-2 medium/substance edition from the selected application edition."""

from __future__ import annotations

import csv
import json
from collections import OrderedDict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "experiments/yolo/sidequest_semantic_application_completion"
OUT = Path(__file__).resolve().parent

DICT_IN = SRC / "SELECTED_173_APPLICATION_DICTIONARY.tsv"
EVENT_IN = SRC / "SELECTED_381_APPLICATION_INTERLINEAR.tsv"
SENT_IN = SRC / "SELECTED_116_APPLICATION_SENTENCES.tsv"


def read_tsv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        return list(reader.fieldnames or []), list(reader)


def write_tsv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


# Exact-card revisions only. No visible substring is globally assigned a meaning.
R = {
    # AIR: a work liquor while it is in a flow path, not WATER.
    "12efe866f335461823a6": (
        "CH_LEARNED+AIR_WORK_LIQUOR_FLOW",
        "AIR=laufende Arbeitsflüssigkeit",
        "Arbeitsflüssigkeit zulassen",
        "R2_MEDIUM__AIR_FLOW",
        "SELECTED_THIN_COMPOSITION",
        "H1 provides vessel/collection context; the card names inlet liquor, not water.",
    ),
    "22fb87a5a83e5c3fb510": (
        "K_LEARNED+AIR_WORK_LIQUOR_FLOW",
        "AIR=laufende Arbeitsflüssigkeit",
        "laufende Arbeitsflüssigkeit",
        "R2_MEDIUM__AIR_FLOW",
        "SELECTED_THIN_COMPOSITION",
        "The B1 pool owner supplies the path; no return arrow and no substance identity is encoded.",
    ),
    "7d2404c835b10a2c06af": (
        "OK+AIR_WORK_LIQUOR_FLOW",
        "OK=in Gang setzen; AIR=laufende Arbeitsflüssigkeit",
        "Arbeitsflüssigkeit in den Lauf bringen",
        "R2_MEDIUM__AIR_FLOW",
        "SELECTED_COMPOSITIONAL",
        "OK contributes initiation and AIR the flowing work liquor.",
    ),
    "b154ff779abe5f196c80": (
        "S_RENDERER+CHED+AIR_WORK_LIQUOR_FLOW",
        "CHED=führen; AIR=laufende Arbeitsflüssigkeit",
        "Arbeitsflüssigkeit durch den Lauf führen",
        "R2_MEDIUM__AIR_FLOW",
        "SELECTED_COMPOSITIONAL",
        "Clear, water, and drain are not separately encoded in the exact card.",
    ),
    "8aedd154964a78e555d6": (
        "D_RENDERER+AIR_WORK_LIQUOR_FLOW+Y_REFERENT+DY_TERMINAL",
        "AIR=Arbeitsflüssigkeitslauf; Y=laufender Posten; DY=Schluss",
        "Lauf der Arbeitsflüssigkeit abschließen",
        "R2_MEDIUM__AIR_FLOW",
        "SELECTED_SINGLETON_EXTENSION",
        "The terminal frame closes the running-liquor step, not a named water channel.",
    ),
    # CHEO: solvent/extraction-medium slot; water, wine, vinegar, lye, oil remain local fillers.
    "087a47b5423438cd6b6a": (
        "CH_RENDERER+OK+CHEO_EXTRACTION_MEDIUM",
        "OK=zugeben; CHEO=Auszugsmedium",
        "Auszugsmedium zugeben",
        "R2_MEDIUM__CHEO_MEDIUM",
        "SELECTED_PROVISIONAL_CORE",
        "Immediately precedes straining; no particular solvent is named.",
    ),
    "807591efc3d3f7ddbfab": (
        "CHEO_EXTRACTION_MEDIUM+AR_SOURCE",
        "CHEO=Auszugsmedium; AR=aus",
        "Auszugsmedium daraus entnehmen",
        "R2_MEDIUM__CHEO_MEDIUM",
        "SELECTED_PROVISIONAL_CORE",
        "The second CHEO card preserves the same medium slot plus source relation.",
    ),
    # OR: prepared batch, not a specific decoction.
    "7a4bb8136330ee4e6e56": (
        "OR_BATCH",
        "OR=Ansatz",
        "Ansatz",
        "R2_MEDIUM__OR_BATCH",
        "SELECTED_RECURRENT_CORE",
        "Seven events support a neutral prepared batch; no wet/dry or medicinal content is forced.",
    ),
    "dec401773c1f0347793d": (
        "OL_CONTINUE+OR_BATCH",
        "OL=mit dem Vorigen; OR=Ansatz",
        "mit dem vorigen Ansatz",
        "R2_MEDIUM__OR_BATCH",
        "SELECTED_COMPOSITIONAL",
        "Two events preserve previous-batch reference.",
    ),
    "10488b911aae52b3b334": (
        "OT_NEXT+OR_BATCH",
        "OT=nächster; OR=Ansatz",
        "der nächste Ansatz",
        "R2_MEDIUM__OR_BATCH",
        "SELECTED_COMPOSITIONAL",
        "Two Herbal events preserve next-batch reference.",
    ),
    "b9d7b6d68209a9019e7a": (
        "CHO_PLANT+OR_BATCH",
        "CHO=Pflanzenstoff; OR=Ansatz",
        "Pflanzenansatz",
        "R2_MEDIUM__OR_BATCH",
        "SELECTED_COMPOSITIONAL",
        "The illustrated plant supplies the material; OR supplies only batch identity.",
    ),
    "6afeb5c9ab9f6cbdea0d": (
        "OR_BATCH+AIN_PORTION",
        "OR=Ansatz; AIN=Portion",
        "eine Portion des Ansatzes",
        "R2_MEDIUM__OR_BATCH",
        "SELECTED_COMPOSITIONAL",
        "The card composes prepared batch with bounded portion.",
    ),
    # Learned wet-work cards. These do not license free visible stems.
    "428a5e3662aa57b4b256": (
        "SCHOAL_BOIL_IN_EXTRACTION_MEDIUM_WHOLE_CARD",
        "SCHOAL=im Auszugsmedium auskochen",
        "im Auszugsmedium auskochen",
        "R2_MEDIUM__LEARNED_WET_WORK_CARD",
        "SELECTED_SINGLETON_WHOLE_CARD",
        "Wine is removed: the press-rest-strain sequence identifies a functional extraction slot only.",
    ),
    "0f18de177ed7c878bf95": (
        "DL_BATH_ADDITIVE_WHOLE_CARD",
        "DL=Badzusatz",
        "Badzusatz",
        "R2_MEDIUM__LEARNED_WET_WORK_CARD",
        "SELECTED_RECURRENT_WHOLE_CARD",
        "Bad means a work bath as well as a body wash; the card does not choose between them.",
    ),
    "c71c72da4e09e0833392": (
        "KCHOAR_WORKING_EXTRACT_WHOLE_CARD",
        "KCHOAR=Gebrauchsauszug",
        "Gebrauchsauszug",
        "R2_MEDIUM__LEARNED_WET_WORK_CARD",
        "SELECTED_SINGLETON_WHOLE_CARD",
        "The old chest-drink gloss is sentence-sized and unsupported; the position supports a usable extract.",
    ),
    "cb57b696b815fdef9cb7": (
        "SHECTHY_WARM_WORK_LIQUOR_WHOLE_CARD",
        "SHECTHY=warme Arbeitsflüssigkeit",
        "warme Arbeitsflüssigkeit",
        "R2_MEDIUM__LEARNED_WET_WORK_CARD",
        "SELECTED_SINGLETON_WHOLE_CARD",
        "Water is removed; warmth remains a tentative learned whole-card contrast beside the ready-state card.",
    ),
    "98bdc4244c84cbef3321": (
        "RSHEAL_WARM_RINSE_LIQUOR_WHOLE_CARD",
        "RSHEAL=warme Spülflüssigkeit",
        "warme Spülflüssigkeit",
        "R2_MEDIUM__LEARNED_WET_WORK_CARD",
        "SELECTED_SINGLETON_WHOLE_CARD",
        "The following second opening licenses rinse liquor, not specifically water.",
    ),
    "cbb42a4fe68068325d6b": (
        "DSHE_FRESH_RINSE_LIQUOR+DY_TERMINAL",
        "DSHE=frische Spülflüssigkeit zugeben; DY=Schluss",
        "frische Spülflüssigkeit zugeben; Schluss",
        "R2_MEDIUM__LEARNED_WET_WORK_CARD",
        "SELECTED_SINGLETON_CLOSE",
        "Clean-water specificity is removed; freshness is only a practical default for an isolated rinse close.",
    ),
    "d4a31dbcf1ed6d9e5aa9": (
        "TSHEY_RINSE_LIQUOR_WHOLE_CARD",
        "TSHEY=Spülflüssigkeit",
        "Spülflüssigkeit",
        "R2_MEDIUM__LEARNED_WET_WORK_CARD",
        "SELECTED_SINGLETON_WHOLE_CARD",
        "The following sustained contact supports rinse liquor; no chemical substance is named.",
    ),
    "883a6708116c342cb10b": (
        "SK_WARM_WORK_LIQUOR+AR_SOURCE",
        "SK=warme Arbeitsflüssigkeit; AR=aus",
        "warme Arbeitsflüssigkeit ausgießen",
        "R2_MEDIUM__LEARNED_WET_WORK_CARD",
        "SELECTED_SINGLETON_COMPOSITION",
        "AR preserves outward/source contribution; the precise liquid remains local.",
    ),
    "b5df9126607030b95175": (
        "SHEY_CLARIFIED_EXTRACT_WHOLE_CARD",
        "CHEEY|SHEY=Klarauszug",
        "Klarauszug",
        "R2_MEDIUM__CLARIFIED_EXTRACT",
        "SELECTED_RECURRENT_WHOLE_CARD",
        "Four events retain the filter-product card; this still does not license EY=WATER.",
    ),
}


CONTEXT = {
    "12efe866f335461823a6": "Arbeitsflüssigkeit zulassen",
    "22fb87a5a83e5c3fb510": "Laufende Arbeitsflüssigkeit",
    "7d2404c835b10a2c06af": "Arbeitsflüssigkeit in den Lauf bringen",
    "b154ff779abe5f196c80": "Arbeitsflüssigkeit durch den Lauf führen",
    "8aedd154964a78e555d6": "Den Lauf der Arbeitsflüssigkeit abschließen",
    "087a47b5423438cd6b6a": "Auszugsmedium zugeben",
    "807591efc3d3f7ddbfab": "Auszugsmedium daraus entnehmen",
    "7a4bb8136330ee4e6e56": "Ansatz",
    "dec401773c1f0347793d": "Mit dem vorigen Ansatz",
    "10488b911aae52b3b334": "Der nächste Ansatz",
    "b9d7b6d68209a9019e7a": "Pflanzenansatz",
    "6afeb5c9ab9f6cbdea0d": "Eine Portion des Ansatzes",
    "428a5e3662aa57b4b256": "Im Auszugsmedium auskochen",
    "0f18de177ed7c878bf95": "Der vorbereitete Badzusatz",
    "c71c72da4e09e0833392": "Gebrauchsauszug",
    "cb57b696b815fdef9cb7": "Warme Arbeitsflüssigkeit",
    "98bdc4244c84cbef3321": "Warme Spülflüssigkeit zugeben",
    "cbb42a4fe68068325d6b": "Frische Spülflüssigkeit zugeben; Schluss",
    "d4a31dbcf1ed6d9e5aa9": "Spülflüssigkeit",
    "883a6708116c342cb10b": "Warme Arbeitsflüssigkeit ausgießen",
    "b5df9126607030b95175": "Klarauszug",
}


FAMILY = {
    "12efe866f335461823a6": "AIR",
    "22fb87a5a83e5c3fb510": "AIR",
    "7d2404c835b10a2c06af": "AIR",
    "b154ff779abe5f196c80": "AIR",
    "8aedd154964a78e555d6": "AIR",
    "087a47b5423438cd6b6a": "CHEO",
    "807591efc3d3f7ddbfab": "CHEO",
    "7a4bb8136330ee4e6e56": "OR",
    "dec401773c1f0347793d": "OR",
    "10488b911aae52b3b334": "OR",
    "b9d7b6d68209a9019e7a": "OR",
    "6afeb5c9ab9f6cbdea0d": "OR",
    "428a5e3662aa57b4b256": "SCHOAL",
    "0f18de177ed7c878bf95": "DL",
    "c71c72da4e09e0833392": "KCHOAR",
    "cb57b696b815fdef9cb7": "SHECTHY",
    "98bdc4244c84cbef3321": "RSHEAL",
    "cbb42a4fe68068325d6b": "DSHEDY",
    "d4a31dbcf1ed6d9e5aa9": "TSHEY",
    "883a6708116c342cb10b": "SKAR",
    "b5df9126607030b95175": "SHEY",
}


RIVAL = {
    "AIR": "formal flow/path card with no material noun",
    "CHEO": "generic operation or already-produced extract rather than extraction medium",
    "OR": "generic preparation label rather than a wet batch",
    "SCHOAL": "wine, water, lye, oil, or a wholly different learned operation",
    "DL": "tool or station rather than bath additive",
    "KCHOAR": "drink or administration card rather than usable extract",
    "SHECTHY": "ready-state variant; warmth and liquid both absent",
    "RSHEAL": "second-opening operation rather than rinse liquor",
    "DSHEDY": "generic terminal operation rather than fresh rinse addition",
    "TSHEY": "rinse operation rather than rinse liquor",
    "SKAR": "generic outward transfer rather than warm liquor",
    "SHEY": "formal filtered product rather than a liquid extract",
}


BREAK = {
    "AIR": "A non-liquid object in the same five exact cards, or a base AIR use incompatible with flow.",
    "CHEO": "Either card used where no carrier/extract medium can be supplied or removed.",
    "OR": "An OR-family card that cannot denote a prepared batch under OL/OT/CHO/AIN composition.",
    "SCHOAL": "Independent evidence that the whole card names a specific substance or a non-heating operation.",
    "DL": "A DL occurrence in a slot that cannot host an additive or prepared bath charge.",
    "KCHOAR": "A repeated KCHOAR use that is not a usable prepared extract.",
    "SHECTHY": "A repeated use without heat/liquid, especially exact interchange with SHCTHY ready-state.",
    "RSHEAL": "A repeated use without rinse/working liquid near a transfer opening.",
    "DSHEDY": "A repeated use that closes a dry operation.",
    "TSHEY": "A repeated use whose following operation cannot act on a rinse liquor.",
    "SKAR": "A repeated use without outward warm-liquid handling.",
    "SHEY": "A use before separation or as an unprocessed input rather than after withdrawal/filtration.",
}


# Already-corrected false substance segmentations included in the audit inventory.
NEGATIVE_IDS = {
    "08bd5ca0c2ad137a056d": ("NOT_WATER", "OK+E+Y=kurz anlegen"),
    "0275fbf14e07935b0a45": ("NOT_WARM_MEDIUM", "OK+EE+Y=länger halten"),
    "7db18b2f0fb7ed0fcfd3": ("NOT_RINSE_NOUN", "OK+E+DY=kurz benetzen; Schluss"),
    "7d25241b0e56c836372a": ("NOT_BATH_NOUN", "OK+EE+DY=länger einwirken; Schluss"),
    "322281bd391aa621f568": ("NOT_OIL", "OK+OL=mit Vorigem weiterarbeiten"),
    "d929a14ec45749b2e805": ("NOT_WHITE_WINE", "Y+AIN=diese Portion"),
    "0f15effeca7ab10bb026": ("NOT_COOL_WATER", "L+CHED+AR=aus der Quelle hinausführen"),
    "5e8441397e7c0faf042b": ("NOT_WARM_WATER", "CHED+Y=laufenden Posten umsetzen"),
    "0ab57b7166de99db3a55": ("CONTEXT_ONLY_FLUID", "LCH+Y=laufenden Posten abziehen"),
    "eb2e4bc143f623ee03ac": ("NOT_WARM_CLOTH", "OK+Y+LDDY=Posten befestigen; Schluss"),
    "de7321bface5628e35d6": ("NOT_NECESSARILY_LIQUID", "L+CHED+DY=hinausführen; Schluss"),
}


def revise_dictionary() -> list[dict[str, str]]:
    fields, rows = read_tsv(DICT_IN)
    extra = [
        "medium_previous_segmentation",
        "medium_previous_nucleus_de",
        "medium_previous_gloss_de",
        "medium_revision_family",
        "medium_revision_strength",
        "medium_revision_note",
    ]
    for row in rows:
        ident = row["joint_tuple_id"]
        if ident in R:
            old = (row["semantic_segmentation"], row["stable_concrete_nucleus_de"], row["concrete_word_reading_de"])
            seg, nucleus, gloss, family, strength, note = R[ident]
            row.update(
                semantic_segmentation=seg,
                stable_concrete_nucleus_de=nucleus,
                concrete_word_reading_de=gloss,
                reading_type=family,
                local_expansion_examples_de=f"R2-Nasswerkstatt: {CONTEXT[ident]}",
                variation_note=(row["variation_note"] + "; medium/substance: " + note).strip("; "),
                medium_previous_segmentation=old[0],
                medium_previous_nucleus_de=old[1],
                medium_previous_gloss_de=old[2],
                medium_revision_family=family,
                medium_revision_strength=strength,
                medium_revision_note=note,
            )
        else:
            for key in extra:
                if key in {"medium_revision_family", "medium_revision_strength"}:
                    row[key] = "UNCHANGED"
                elif key == "medium_revision_note":
                    row[key] = "NOT_APPLICABLE"
                else:
                    row[key] = ""
            if ident in NEGATIVE_IDS:
                family, note = NEGATIVE_IDS[ident]
                row["medium_revision_family"] = "R2_MEDIUM_NEGATIVE_CONTROL__" + family
                row["medium_revision_strength"] = "RETAIN_CURRENT_NON_SUBSTANCE_READING"
                row["medium_revision_note"] = note
    write_tsv(OUT / "R2_173_MEDIUM_DICTIONARY.tsv", fields + extra, rows)
    return rows


def revise_events() -> list[dict[str, str]]:
    fields, rows = read_tsv(EVENT_IN)
    extra = [
        "medium_previous_segmentation",
        "medium_previous_nucleus_de",
        "medium_previous_gloss_de",
        "medium_previous_context_de",
        "medium_revision_family",
        "medium_revision_strength",
        "medium_revision_note",
    ]
    for row in rows:
        ident = row["joint_tuple_id"]
        if ident in R:
            old = (
                row["semantic_segmentation"],
                row["stable_concrete_nucleus_de"],
                row["concrete_word_reading_de"],
                row["contextual_event_reading_de"],
            )
            seg, nucleus, gloss, family, strength, note = R[ident]
            row.update(
                semantic_segmentation=seg,
                stable_concrete_nucleus_de=nucleus,
                concrete_word_reading_de=gloss,
                contextual_event_reading_de=CONTEXT[ident],
                medium_previous_segmentation=old[0],
                medium_previous_nucleus_de=old[1],
                medium_previous_gloss_de=old[2],
                medium_previous_context_de=old[3],
                medium_revision_family=family,
                medium_revision_strength=strength,
                medium_revision_note=note,
            )
        else:
            for key in extra:
                if key in {"medium_revision_family", "medium_revision_strength"}:
                    row[key] = "UNCHANGED"
                elif key == "medium_revision_note":
                    row[key] = "NOT_APPLICABLE"
                else:
                    row[key] = ""
            if ident in NEGATIVE_IDS:
                family, note = NEGATIVE_IDS[ident]
                row["medium_revision_family"] = "R2_MEDIUM_NEGATIVE_CONTROL__" + family
                row["medium_revision_strength"] = "RETAIN_CURRENT_NON_SUBSTANCE_READING"
                row["medium_revision_note"] = note
    write_tsv(OUT / "R2_381_MEDIUM_INTERLINEAR.tsv", fields + extra, rows)
    return rows


def revise_sentences(events: list[dict[str, str]]) -> list[dict[str, str]]:
    fields, rows = read_tsv(SENT_IN)
    by_statement: dict[str, list[dict[str, str]]] = OrderedDict()
    for event in events:
        by_statement.setdefault(event["statement_id"], []).append(event)

    substitutions = [
        ("Pflanzenzubereitung", "Pflanzenansatz"),
        ("Die nächste Zubereitung", "Der nächste Ansatz"),
        ("Mit der vorigen Zubereitung", "Mit dem vorigen Ansatz"),
        ("Eine Portion der Zubereitung", "Eine Portion des Ansatzes"),
        ("Zubereitung", "Ansatz"),
        ("Koche sie in reinem Wein", "Koche sie im Auszugsmedium aus"),
        ("Auszugsflüssigkeit zugeben", "Auszugsmedium zugeben"),
        ("Auszug daraus entnehmen", "Auszugsmedium daraus entnehmen"),
        ("Flüssigkeitszulauf", "Arbeitsflüssigkeit zulassen"),
        ("Laufende Beckenflüssigkeit", "Laufende Arbeitsflüssigkeit"),
        ("Der vorbereitete Bade- oder Waschzusatz", "Der vorbereitete Badzusatz"),
        ("Sauberes Wasser zugeben", "Frische Spülflüssigkeit zugeben"),
        ("Gieße das erwärmte Wasser ein", "Gieße warme Spülflüssigkeit ein"),
        ("Warmes Wasser", "Warme Arbeitsflüssigkeit"),
        ("Flüssigkeit in den Lauf bringen", "Arbeitsflüssigkeit in den Lauf bringen"),
        ("Fließende Flüssigkeit durch den Lauf führen", "Arbeitsflüssigkeit durch den Lauf führen"),
        ("Den Flüssigkeitslauf abschließen", "Den Lauf der Arbeitsflüssigkeit abschließen"),
        ("Erwärmtes Medium ausgießen", "Warme Arbeitsflüssigkeit ausgießen"),
    ]

    for row in rows:
        statement_events = by_statement[row["statement_id"]]
        row["card_sequence_de"] = " · ".join(e["concrete_word_reading_de"] for e in statement_events)
        reading = row["workshop_sentence_de"]
        for old, new in substitutions:
            reading = reading.replace(old, new)
        if row["statement_id"] == "H5-S005":
            reading = "Pflanzenstoff; Den laufenden Posten einsetzen; Gebrauchsauszug; Gebrauchen"
        row["workshop_sentence_de"] = reading
        row["medium_revised_event_count"] = str(sum(e["joint_tuple_id"] in R for e in statement_events))
        row["medium_revision_note"] = (
            "R2 functional-medium substitution; no specific water/wine/oil identity asserted"
            if int(row["medium_revised_event_count"]) else "UNCHANGED"
        )
    out_fields = fields + ["medium_revised_event_count", "medium_revision_note"]
    write_tsv(OUT / "R2_116_MEDIUM_SENTENCES.tsv", out_fields, rows)
    return rows


def write_records(sentences: list[dict[str, str]]) -> None:
    groups: OrderedDict[str, list[dict[str, str]]] = OrderedDict()
    for row in sentences:
        groups.setdefault(row["record_unit_id"], []).append(row)
    lines = [
        "# Elf vollständige Records der R2-Nasswerkstatt",
        "",
        "Kreative Werkstattlesung: Stoffnamen werden nur als gelernte Ganzkarten",
        "angesetzt. AIR, CHEO und OR tragen Lauf, Auszugsmedium und Ansatz; Wasser,",
        "Wein, Öl, Essig oder Lauge bleiben lokale Füllungen. Zeile ist kein Satzschluss.",
        "",
    ]
    for record, rows in groups.items():
        lines.extend([f"## {record} — {rows[0]['page']}", ""])
        for index, row in enumerate(rows, 1):
            sentence = row["workshop_sentence_de"].rstrip(".") + "."
            lines.append(f"{index}. **{row['statement_id']}** `{row['canonical_slots_present']}` — {sentence}")
        lines.append("")
    (OUT / "R2_11_MEDIUM_RECORDS.md").write_text("\n".join(lines), encoding="utf-8")


def write_paradigm(events: list[dict[str, str]], sentences: list[dict[str, str]]) -> int:
    sentence_text = {row["statement_id"]: row["workshop_sentence_de"] for row in sentences}
    fields = [
        "audit_family",
        "audit_kind",
        "event_id",
        "statement_id",
        "page",
        "locus",
        "joint_tuple_id",
        "surface",
        "selected_segmentation",
        "short_default_de",
        "contextual_reading_de",
        "complete_statement_de",
        "strongest_rival",
        "break_condition",
    ]
    rows: list[dict[str, str]] = []
    for event in events:
        ident = event["joint_tuple_id"]
        if ident in FAMILY:
            family = FAMILY[ident]
            kind = "SELECTED_MEDIUM_OR_BATCH_CARD"
            rival = RIVAL[family]
            break_condition = BREAK[family]
        elif ident in NEGATIVE_IDS:
            family = NEGATIVE_IDS[ident][0]
            kind = "NEGATIVE_SUBSTANCE_CONTROL"
            rival = "old water/wine/oil/warm-medium reading"
            break_condition = "Only reopen if the exact tuple, not a visible substring, repeatedly names that substance."
        else:
            continue
        rows.append(
            {
                "audit_family": family,
                "audit_kind": kind,
                "event_id": event["event_id"],
                "statement_id": event["statement_id"],
                "page": event["page"],
                "locus": event["locus"],
                "joint_tuple_id": ident,
                "surface": event["surface_display"],
                "selected_segmentation": event["semantic_segmentation"],
                "short_default_de": event["concrete_word_reading_de"],
                "contextual_reading_de": event["contextual_event_reading_de"],
                "complete_statement_de": sentence_text[event["statement_id"]],
                "strongest_rival": rival,
                "break_condition": break_condition,
            }
        )
    write_tsv(OUT / "R2_MEDIUM_SUBSTANCE_PARADIGM.tsv", fields, rows)
    return len(rows)


def validate(dictionary: list[dict[str, str]], events: list[dict[str, str]], sentences: list[dict[str, str]], paradigm_n: int) -> None:
    validations = {
        "dictionary_rows": len(dictionary),
        "event_rows": len(events),
        "sentence_rows": len(sentences),
        "record_count": len({row["record_unit_id"] for row in sentences}),
        "revised_exact_types": len(R),
        "revised_events": sum(row["joint_tuple_id"] in R for row in events),
        "audit_paradigm_events": paradigm_n,
        "dictionary_empty_defaults": sum(not row["concrete_word_reading_de"].strip() for row in dictionary),
        "event_empty_defaults": sum(not row["contextual_event_reading_de"].strip() for row in events),
        "sentence_empty_defaults": sum(not row["workshop_sentence_de"].strip() for row in sentences),
        "forbidden_pages": sorted({row["page"] for row in events if row["page"] in {"f84", "f84r"}}),
    }
    validations["ok"] = (
        validations["dictionary_rows"] == 173
        and validations["event_rows"] == 381
        and validations["sentence_rows"] == 116
        and validations["record_count"] == 11
        and validations["dictionary_empty_defaults"] == 0
        and validations["event_empty_defaults"] == 0
        and validations["sentence_empty_defaults"] == 0
        and not validations["forbidden_pages"]
    )
    (OUT / "R2_VALIDATION.json").write_text(json.dumps(validations, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if not validations["ok"]:
        raise SystemExit(json.dumps(validations, ensure_ascii=False))


def main() -> None:
    dictionary = revise_dictionary()
    events = revise_events()
    sentences = revise_sentences(events)
    write_records(sentences)
    paradigm_n = write_paradigm(events, sentences)
    validate(dictionary, events, sentences, paradigm_n)


if __name__ == "__main__":
    main()
