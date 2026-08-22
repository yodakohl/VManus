#!/usr/bin/env python3
"""Build the R4 chancery-corrector thermal/temporal candidate edition."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import OrderedDict, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = ROOT / "experiments/yolo/sidequest_semantic_medium_substance_completion"
DICT_IN = SOURCE / "SELECTED_173_MEDIUM_SUBSTANCE_DICTIONARY.tsv"
EVENT_IN = SOURCE / "SELECTED_381_MEDIUM_SUBSTANCE_INTERLINEAR.tsv"
SENTENCE_IN = SOURCE / "SELECTED_116_MEDIUM_SUBSTANCE_SENTENCES.tsv"

DICT_OUT = HERE / "R4_173_DICTIONARY.tsv"
EVENT_OUT = HERE / "R4_381_INTERLINEAR.tsv"
SENTENCE_OUT = HERE / "R4_116_SENTENCES.tsv"
RECORD_OUT = HERE / "R4_11_RECORDS.md"
PARADIGM_OUT = HERE / "R4_PARADIGM.tsv"
VALIDATION_OUT = HERE / "R4_VALIDATION.json"
SUMMARY_OUT = HERE / "R4_BUILD_SUMMARY.json"

ALLOWED_PAGES = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"}
RECORD_ORDER = ["H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def uniq(values: list[str]) -> list[str]:
    return list(OrderedDict.fromkeys(value for value in values if value))


def choice(parse: str, nucleus: str, gloss: str, family: str, reason: str) -> tuple[str, str, str, str, str]:
    return parse, nucleus, gloss, family, reason


# A small productive grammar plus short learned cards.  The visible string is
# split only in already licensed families; singleton thermal words remain whole.
R = {
    # Named stage.
    "2c82523794dcb7d2b343": choice("IIN_STAGE", "IIN=Stufe", "Stufe", "IIN_STAGE", "The recurrent base should name the stage, not a whole desired-state sentence."),
    "409de02322e7b2ca0c62": choice("K_SOFT+IIN_STAGE", "IIN=Stufe; K=weich", "weiche Stufe", "IIN_STAGE", "K supplies the learned soft qualifier."),
    "fcc1deda9e24ec268eb0": choice("DA_SECOND+IIN_STAGE", "IIN=Stufe; DA=zweite", "zweite Stufe", "IIN_STAGE", "The local opening is inherited; the card need only distinguish the second stage."),

    # E/EE/EEE duration-completion grades in the licensed grids.
    "08bd5ca0c2ad137a056d": choice("OK+GRADE_1+Y_REFERENT", "OK=ansetzen; E=kurz; Y=Posten", "kurz einwirken", "E_GRADE", "Remove application-specific laying-on from the portable grid."),
    "0275fbf14e07935b0a45": choice("OK+GRADE_2+Y_REFERENT", "OK=ansetzen; EE=lang; Y=Posten", "lang einwirken", "E_GRADE", "The sustained open cell keeps the item active."),
    "7db18b2f0fb7ed0fcfd3": choice("OK+GRADE_1+DY_CLOSE", "OK=ansetzen; E=kurz; Endkarte=Schluss", "kurz einwirken; Schluss", "E_GRADE", "Wet/contact is local; the portable value is brief action."),
    "7d25241b0e56c836372a": choice("OK+GRADE_2+DY_CLOSE", "OK=ansetzen; EE=lang; Endkarte=Schluss", "lang einwirken; Schluss", "E_GRADE", "The terminal pair closes sustained action."),
    "d25110e0d8488927278f": choice("OK+GRADE_3+DY_CLOSE", "OK=ansetzen; EEE=ganz; Endkarte=Schluss", "ganz einwirken; Schluss", "E_GRADE", "Saturation is local; EEE supplies completion."),
    "93f69c38fdedee1598e9": choice("OK+GRADE_2+AL_SITE", "OK=ansetzen; EE=lang; AL=Stelle", "lang an der Stelle einwirken", "E_GRADE", "The target replaces the current-item output."),
    "daf32e6db9e04413ce7f": choice("OK+GRADE_2+OL_CONTINUE", "OK=ansetzen; EE=lang; OL=weiter", "lang weiter einwirken", "E_GRADE", "OL continues rather than naming a previous substance."),

    # CHK warmth grid.
    "d904bf7b044dd3922781": choice("CHK_WARM+GRADE_1+Y_REFERENT", "CHK=wärmen; E=kurz; Y=Posten", "kurz wärmen", "CHK_WARM", "The short open warmth cell."),
    "2c1a5fd92b9e3c762242": choice("CHK_WARM+GRADE_2+Y_REFERENT", "CHK=wärmen; EE=lang; Y=Posten", "lang warmhalten", "CHK_WARM", "The long open warmth cell."),
    "f0db6d30cd34f4cb2a4d": choice("CHK_WARM+GRADE_2+Y_REFERENT", "CHK=wärmen; EE=lang; Y=Posten", "lang warmhalten", "CHK_WARM", "Second learned rendering of the same long open warmth cell."),
    "a84fbe3ad380df345b97": choice("CHK_WARM+GRADE_2+DY_CLOSE", "CHK=wärmen; EE=lang; Endkarte=Schluss", "lang warmhalten; Schluss", "CHK_WARM", "Closed counterpart to CHKEEY."),

    # Rest and readiness.
    "bc4f1f5c006c74a4d26d": choice("SHED_REST+GRADE_1+DY_CLOSE", "SHED=ruhen; E=Grundgrad; Endkarte=Schluss", "ruhen; Schluss", "SHED_REST", "Settling remains a local liquid expansion of rest."),
    "03626ca94cb17800d767": choice("SHED_REST+GRADE_2+DY_CLOSE", "SHED=ruhen; EE=lang; Endkarte=Schluss", "lang ruhen; Schluss", "SHED_REST", "The extra E supplies duration."),
    "abb23e5e6936b4147f76": choice("SHED_REST+AL_SITE", "SHED=ruhen; AL=Stelle", "Ruheplatz", "SHED_REST", "The local owner may specialize it as a settling station."),
    "daa1347f456415fe8737": choice("OL_CONTINUE+SHED_REST+DY_CLOSE", "OL=weiter; SHED=ruhen; Endkarte=Schluss", "weiter ruhen; Schluss", "SHED_REST", "Continuation is shorter than 'with the previous'."),
    "db167f8e9b53eefb58f8": choice("OK+SHED_REST+DY_CLOSE", "OK=ansetzen; SHED=ruhen; Endkarte=Schluss", "zur Ruhe setzen; Schluss", "SHED_REST", "OK initiates the rest state."),
    "e0b630cb1b5df5e7105b": choice("CTHY_READY_WHOLE_CARD", "CTHY=fertig", "fertig", "CTHY_READY", "One short state replaces the longer ready-for-use phrase."),
    "6b89d6dd70635bc60fe0": choice("CTH_READY+GRADE_1+Y_REFERENT", "CTH=fertig; E=kurz; Y=Posten", "kurz bereithalten", "CTHY_READY", "The grade supplies brief holding of the ready item."),

    # OT advances; OL continues; doubled OK repeats.
    "10488b911aae52b3b334": choice("OT_FOLLOW+OR_BATCH", "OT=Folge; OR=Ansatz", "Folgeansatz", "ORDER_OT", "One OT contribution works in batch, measure, site and item compounds."),
    "54d0e228ca346110af05": choice("OT_FOLLOW+AIIN_MEASURE", "OT=Folge; AIIN=Maß", "Folgemaß", "ORDER_OT", "The next measure is a compact compound."),
    "faf321940aed922846a9": choice("OT_FOLLOW+Y_REFERENT", "OT=Folge; Y=Posten", "Folgeposten", "ORDER_OT", "Remove the full choose-next instruction from the card."),
    "90bcf0a9ec0ef56399e6": choice("OT_FOLLOW+AL_SITE", "OT=Folge; AL=Stelle", "Folgestelle", "ORDER_OT", "The next local site is a compact compound."),
    "497cbd9c7401810ff56b": choice("OT_FOLLOW+OL_CONTINUE", "OT=Folge; OL=weiter", "danach weiter", "ORDER_OT", "The two order axes compose directly."),
    "4de12cf322dfb76ded1e": choice("OT_FOLLOW+CHED_TRANSFER+DY_CLOSE", "OT=danach; CHED=umsetzen; Endkarte=Schluss", "danach umsetzen; Schluss", "ORDER_OT", "Remove the unsupported alternative 'or repeat'."),
    "601b77449028deed39de": choice("OT_FOLLOW+CHD_TRANSFER+DY_CLOSE", "OT=danach; CHD=umsetzen; Endkarte=Schluss", "danach umsetzen; Schluss", "ORDER_OT", "Short allomorph of the same sequential close."),
    "b6b654722e55729cc947": choice("OT_FOLLOW+AR_SOURCE", "OT=danach; AR=aus", "danach auslassen", "ORDER_OT", "Source direction remains separate."),
    "5d5e0b288cf36864ed9d": choice("OT_FOLLOW+GRADE_2+Y_REFERENT", "OT=Folge; EE=lang; Y=Posten", "Folgeposten lang einwirken", "ORDER_OT", "The output is the next open item."),
    "c45ebac60774620561e2": choice("OT_FOLLOW+GRADE_1+DY_CLOSE", "OT=danach; E=kurz; Endkarte=Schluss", "danach kurz einwirken; Schluss", "ORDER_OT", "Brief sequential closed cell."),
    "ff178343c18e287ce3b7": choice("OT_FOLLOW+GRADE_2+DY_CLOSE", "OT=danach; EE=lang; Endkarte=Schluss", "danach lang einwirken; Schluss", "ORDER_OT", "Sustained sequential closed cell."),
    "dcda95c81a5460feb191": choice("OL_CONTINUE", "OL=weiter", "weiter", "ORDER_OL", "The recurrent exact card is a continuation prompt, not a content word."),
    "1b1ffdd869fb1429ad03": choice("OL_CONTINUE+DY_CLOSE", "OL=weiter; Endkarte=Schluss", "weiter; Schluss", "ORDER_OL", "The same exact card must not mean gentle heating in only one of its two occurrences."),
    "dec401773c1f0347793d": choice("OL_CONTINUE+OR_BATCH", "OL=weiter; OR=Ansatz", "Ansatz weiterführen", "ORDER_OL", "Previous batch is inherited; OL itself contributes continuation."),
    "94df4847b7b16c98394a": choice("OL_CONTINUE+AIN_PORTION", "OL=weiter; AIN=Portion", "weitere Portion", "ORDER_OL", "The compound predicts an additional portion."),
    "232195d6ff2f326322f7": choice("OK+OL_CONTINUE", "OK=in Arbeit setzen; OL=weiter", "weiterarbeiten", "ORDER_OL", "The same process continues."),
    "28ffbc88b97772a75f1e": choice("OL_CONTINUE+CHED_TRANSFER+DY_CLOSE", "OL=weiter; CHED=führen; Endkarte=Schluss", "weiterführen; Schluss", "ORDER_OL", "Continuation plus transfer and close."),
    "d665560c8ff80799a82c": choice("CH_RENDERER+OL_CONTINUE", "OL=weiter", "weiternehmen", "ORDER_OL", "The two-page exact card should not name two local plants or diseases."),
    "1322bc176443fc2a8a86": choice("OK+OK_REPEAT+Y_REFERENT", "OK+OK=nochmals; Y=Posten", "Posten nochmals einsetzen", "REPEAT_DOUBLE_OK", "Doubling repeats the operation; OT remains next and OL remains continue."),

    # Short learned thermal/time/result cards.
    "e8a6105b5c3a6220b440": choice("QOTCHOL_WARM_WHOLE_CARD", "QOTCHOL=anwärmen", "anwärmen", "THERMAL_WHOLE_CARD", "A one-word action replaces the gentle-heating sentence."),
    "204b04837409088c48f9": choice("OLTCHY_WARM_WHOLE_CARD", "OLTCHY=anwärmen", "anwärmen", "THERMAL_WHOLE_CARD", "A second learned warming card; no free TCHY root is asserted."),
    "1496a731803a9f48d2e1": choice("ROL_HOT_WHOLE_CARD", "ROL=heiß", "heiß", "THERMAL_WHOLE_CARD", "State, not the phrase 'before cooling'."),
    "8c97dfde96fbc78e3355": choice("LOL_WARM_WHOLE_CARD", "LOL=warm", "warm", "THERMAL_WHOLE_CARD", "State, not the phrase 'until warm'."),
    "43eb9aa12959b4d5cdc9": choice("QEKY_RAW_WHOLE_CARD", "QEKY=roh", "roh", "THERMAL_WHOLE_CARD", "Short state replaces the negative phrase unboiled."),
    "cb57b696b815fdef9cb7": choice("SHECTHY_TEMPERED_WHOLE_CARD", "SHECTHY=temperiert", "temperiert", "THERMAL_WHOLE_CARD", "Retain the selected intermediate state."),
    "2e2027b1951d79911e24": choice("TCHODY_COOL+DY_CLOSE", "TCHODY=kühlen; Endkarte=Schluss", "kühlen; Schluss", "COOL_WHOLE_CARD", "The Herbal product cools after clarification."),
    "0bdc8b6db811b4e67a63": choice("CHARY_COOL_WHOLE_CARD", "CHARY=kühlen", "kühlen", "COOL_WHOLE_CARD", "One-card cooling action."),
    "4da0f0f7b5fc7ac20067": choice("RAL_COOL_WHOLE_CARD", "RAL=kühlen", "kühlen", "COOL_WHOLE_CARD", "One-card cooling action in the bath cycle."),
    "97cc9ac109148723c472": choice("ODY_COOL_STATE+DY_CLOSE", "ODY=kühl; Endkarte=Schluss", "kühl; Schluss", "COOL_WHOLE_CARD", "Storage is contextual; the card supplies cool state and close."),
    "21ed2873b71e57269c08": choice("CHCKHAL_DURATION_WHOLE_CARD", "CHCKHAL=Dauer", "Dauer", "TIME_WHOLE_CARD", "Already atomic and reusable as a time slot."),
    "a8af08e69edab8e54f15": choice("SHFY_REST+AIIN_MEASURE", "SHFY=Ruhe; AIIN=Maß", "Ruhezeit", "TIME_WHOLE_CARD", "Replace the sentence 'stand for the prescribed time' with its slot noun."),
    "d72f71baff01cd0a0406": choice("CHLD_SETTLE+AIIN_MEASURE", "CHLD=absetzen; AIIN=Maß", "Absetzmaß", "TIME_WHOLE_CARD", "The surrounding basin supplies the object; the card names the settling threshold."),
    "d788d8d72d41b25a3c71": choice("CHEALROR_CLEAR_WHOLE_CARD", "CHEALROR=klar", "klar", "RESULT_WHOLE_CARD", "State, not the clause 'until clear'."),
}


def build() -> dict[str, object]:
    dictionary = read_tsv(DICT_IN)
    events = read_tsv(EVENT_IN)
    source_sentences = {row["statement_id"]: row for row in read_tsv(SENTENCE_IN)}
    if len(dictionary) != 173 or len(events) != 381:
        raise AssertionError("unexpected active edition dimensions")

    out_dictionary = []
    for source in dictionary:
        row = dict(source)
        row.update(
            r4_previous_segmentation=source["semantic_segmentation"],
            r4_previous_nucleus_de=source["stable_concrete_nucleus_de"],
            r4_previous_gloss_de=source["concrete_word_reading_de"],
            r4_revision_family="UNCHANGED",
            r4_revision_reason="NOT_APPLICABLE",
        )
        if row["joint_tuple_id"] in R:
            parse, nucleus, gloss, family, reason = R[row["joint_tuple_id"]]
            row["semantic_segmentation"] = parse
            row["stable_concrete_nucleus_de"] = nucleus
            row["concrete_word_reading_de"] = gloss
            row["reading_type"] = "R4_THERMAL_TEMPORAL__" + family
            row["local_expansion_examples_de"] = "R4-Prozessfassung: " + gloss
            row["r4_revision_family"] = family
            row["r4_revision_reason"] = reason
        out_dictionary.append(row)
    dmap = {row["joint_tuple_id"]: row for row in out_dictionary}

    out_events = []
    for source in events:
        row = dict(source)
        row.update(
            r4_previous_segmentation=source["semantic_segmentation"],
            r4_previous_nucleus_de=source["stable_concrete_nucleus_de"],
            r4_previous_gloss_de=source["concrete_word_reading_de"],
            r4_previous_context_de=source["contextual_event_reading_de"],
            r4_revision_family="UNCHANGED",
            r4_revision_reason="NOT_APPLICABLE",
        )
        if row["joint_tuple_id"] in R:
            drow = dmap[row["joint_tuple_id"]]
            row["semantic_segmentation"] = drow["semantic_segmentation"]
            row["stable_concrete_nucleus_de"] = drow["stable_concrete_nucleus_de"]
            row["concrete_word_reading_de"] = drow["concrete_word_reading_de"]
            row["contextual_event_reading_de"] = drow["concrete_word_reading_de"][:1].upper() + drow["concrete_word_reading_de"][1:]
            row["r4_revision_family"] = drow["r4_revision_family"]
            row["r4_revision_reason"] = drow["r4_revision_reason"]
        out_events.append(row)

    grouped: OrderedDict[str, list[dict[str, str]]] = OrderedDict()
    for event in out_events:
        grouped.setdefault(event["statement_id"], []).append(event)
    sentences = []
    for statement_id, group in grouped.items():
        row = dict(source_sentences[statement_id])
        changed = [event for event in group if event["joint_tuple_id"] in R]
        row["card_sequence_de"] = " · ".join(event["concrete_word_reading_de"] for event in group)
        row["event_slot_trace"] = " | ".join(f'{event["event_id"]}[{event["workshop_slots"]}]' for event in group)
        row["workshop_sentence_de"] = "; ".join(event["contextual_event_reading_de"] for event in group)
        row["r4_revised_event_count"] = str(len(changed))
        row["r4_revision_families"] = "|".join(uniq([event["r4_revision_family"] for event in changed])) or "UNCHANGED"
        sentences.append(row)

    records: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in sentences:
        records[row["record_unit_id"]].append(row)
    lines = ["# R4 — elf vollständige Records", "", "Kurze Prozesswerte; Zeile ist kein Satzschluss.", ""]
    for record in RECORD_ORDER:
        rows = records[record]
        lines.extend([f"## {record} — {rows[0]['page']}", ""])
        for index, row in enumerate(rows, 1):
            lines.append(f"{index}. **{row['statement_id']}** — {row['workshop_sentence_de'].rstrip('.')}.")
        lines.append("")
    RECORD_OUT.write_text("\n".join(lines), encoding="utf-8")

    event_by_card: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in out_events:
        event_by_card[row["joint_tuple_id"]].append(row)
    paradigm = []
    for ident, (_, nucleus, gloss, family, reason) in R.items():
        drow = dmap[ident]
        erows = event_by_card[ident]
        paradigm.append({
            "family": family,
            "joint_tuple_id": ident,
            "surface_family": drow["surface_family"],
            "selected_nucleus_de": nucleus,
            "selected_default_de": gloss,
            "occurrences": str(len(erows)),
            "event_ids": "|".join(row["event_id"] for row in erows),
            "statements": "|".join(uniq([row["statement_id"] for row in erows])),
            "pages": "|".join(uniq([row["page"] for row in erows])),
            "selection_reason": reason,
        })

    write_tsv(DICT_OUT, out_dictionary)
    write_tsv(EVENT_OUT, out_events)
    write_tsv(SENTENCE_OUT, sentences)
    write_tsv(PARADIGM_OUT, paradigm)

    checks = {
        "dictionary_173": len(out_dictionary) == 173,
        "events_381": len(out_events) == 381,
        "sentences_116": len(sentences) == 116,
        "records_11": set(records) == set(RECORD_ORDER),
        "ids_unique": len(dmap) == 173 and len({row["event_id"] for row in out_events}) == 381,
        "pages_allowlisted": {row["page"] for row in out_events} <= ALLOWED_PAGES,
        "defaults_complete": all(row["concrete_word_reading_de"] for row in out_dictionary + out_events),
        "event_card_match": all(row["concrete_word_reading_de"] == dmap[row["joint_tuple_id"]]["concrete_word_reading_de"] for row in out_events),
        "statement_partition": sum(int(row["event_count"]) for row in sentences) == 381,
        "paradigm_inventory": {row["joint_tuple_id"] for row in paradigm} == set(R),
        "short_revised_defaults": all(len(row["selected_default_de"].replace(";", "").split()) <= 5 for row in paradigm),
        "no_sealed_page": all(not row["page"].startswith("f84") for row in out_events),
    }
    validation = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "counts": {
            "cards": len(out_dictionary),
            "events": len(out_events),
            "statements": len(sentences),
            "records": len(records),
            "revised_cards": len(R),
            "revised_events": sum(row["joint_tuple_id"] in R for row in out_events),
            "revised_statements": sum(int(row["r4_revised_event_count"]) > 0 for row in sentences),
        },
        "sealed": {"f84": True, "f84r": True},
    }
    VALIDATION_OUT.write_text(json.dumps(validation, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    outputs = [DICT_OUT, EVENT_OUT, SENTENCE_OUT, RECORD_OUT, PARADIGM_OUT, VALIDATION_OUT]
    summary = {
        "status": validation["status"],
        "input_hashes": {path.name: sha256(path) for path in (DICT_IN, EVENT_IN, SENTENCE_IN)},
        "output_hashes": {path.name: sha256(path) for path in outputs},
        "counts": validation["counts"],
    }
    SUMMARY_OUT.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if validation["status"] != "PASS":
        raise SystemExit(json.dumps(validation, ensure_ascii=False))
    return summary


if __name__ == "__main__":
    print(json.dumps(build(), ensure_ascii=False, indent=2, sort_keys=True))
