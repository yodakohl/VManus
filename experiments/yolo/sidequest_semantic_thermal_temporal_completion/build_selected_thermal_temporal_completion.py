#!/usr/bin/env python3
"""Build the selected thermal, temporal, and order workshop edition.

R3 supplies the broad technical inventory and close audit.  The central pass
then applies only short lexical repairs selected from the four role drafts.
"""

from __future__ import annotations

import csv
import hashlib
import json
from collections import OrderedDict, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]

DICT_IN = HERE / "R3_173_DICTIONARY.tsv"
EVENT_IN = HERE / "R3_381_INTERLINEAR.tsv"
SENTENCE_IN = HERE / "R3_116_SENTENCES.tsv"
PARADIGM_IN = HERE / "R3_PARADIGM.tsv"

DICT_OUT = HERE / "SELECTED_173_THERMAL_TEMPORAL_DICTIONARY.tsv"
EVENT_OUT = HERE / "SELECTED_381_THERMAL_TEMPORAL_INTERLINEAR.tsv"
SENTENCE_OUT = HERE / "SELECTED_116_THERMAL_TEMPORAL_SENTENCES.tsv"
RECORD_OUT = HERE / "SELECTED_11_THERMAL_TEMPORAL_RECORDS.md"
PARADIGM_OUT = HERE / "SELECTED_THERMAL_TEMPORAL_PARADIGM.tsv"
COMPONENTS_OUT = HERE / "THERMAL_TEMPORAL_COMPONENTS.tsv"
MODELS_OUT = HERE / "THERMAL_TEMPORAL_MODEL_COMPARISON.tsv"
VALIDATION_OUT = HERE / "validation.json"
SUMMARY_OUT = HERE / "SELECTED_BUILD_SUMMARY.json"

ROLE_DICTIONARIES = {
    "R1": HERE / "R1_173_DICTIONARY.tsv",
    "R2": HERE / "R2_173_DICTIONARY.tsv",
    "R3": HERE / "R3_173_DICTIONARY.tsv",
    "R4": HERE / "R4_173_DICTIONARY.tsv",
}

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


def repair(
    segmentation: str,
    nucleus: str,
    gloss: str,
    context: str,
    family: str,
    reason: str,
) -> dict[str, str]:
    return {
        "semantic_segmentation": segmentation,
        "stable_concrete_nucleus_de": nucleus,
        "concrete_word_reading_de": gloss,
        "contextual_event_reading_de": context,
        "family": family,
        "reason": reason,
    }


# Lexical repairs only.  The R3 process/grade/open-close inventory remains the
# structural base.  Whole-card values are shortened when a role draft imported
# a preposition, object, or full instruction into the card itself.
REPAIRS = {
    "e0b630cb1b5df5e7105b": repair(
        "CTH_READY+Y_CURRENT", "CTH=bereit; Y=Posten", "bereit", "Bereit",
        "READY_ATOM", "R1/R2 use the smaller state BEREIT; 'gebrauchsfertig' adds an unsupported use context.",
    ),
    "6b89d6dd70635bc60fe0": repair(
        "CTH_READY+GRADE_1+Y_CURRENT", "CTH=bereit; E=Stufe I; Y=Posten", "kurz bereithalten", "Kurz bereithalten",
        "READY_GRADE", "The current item is supplied by Y and need not be repeated inside the default.",
    ),
    "e8a6105b5c3a6220b440": repair(
        "QOTCHOL_WARM_WHOLE_CARD", "QOTCHOL=anwärmen", "anwärmen", "Anwärmen",
        "THERMAL_WHOLE", "Three roles prefer the shorter action; 'sanft' is not independently encoded.",
    ),
    "204b04837409088c48f9": repair(
        "OLTCHY_WARM_WHOLE_CARD", "OLTCHY=anwärmen", "anwärmen", "Anwärmen",
        "THERMAL_WHOLE", "Keep this as a learned whole card and remove the unsupported degree adverb.",
    ),
    "1496a731803a9f48d2e1": repair(
        "ROL_STILL_WARM_WHOLE_CARD", "ROL=noch warm", "noch warm", "Noch warm",
        "THERMAL_STATE", "A state is smaller than R3's prepositional phrase 'vor Abkühlung'.",
    ),
    "8c97dfde96fbc78e3355": repair(
        "LOL_WARM_WHOLE_CARD", "LOL=warm", "warm", "Warm",
        "THERMAL_STATE", "WARM is the common core of warm-enough, hand-warm, and warm-point rivals.",
    ),
    "43eb9aa12959b4d5cdc9": repair(
        "QEKY_RAW_WHOLE_CARD", "QEKY=roh", "roh", "Roh",
        "THERMAL_STATE", "ROH is the shorter positive state; 'ungekocht' presupposes a specific process.",
    ),
    "97cc9ac109148723c472": repair(
        "ODY_COOL+TERMINAL_CLOSE", "ODY=kühl; Endkarte=Schluss", "kühl; Schluss", "Kühl; Schluss",
        "THERMAL_CLOSE", "The storage location is contextual; the card retains cool state plus its licensed close.",
    ),
    "d788d8d72d41b25a3c71": repair(
        "CHEALROR_CLEAR_ENDPOINT_WHOLE_CARD", "CHEALROR=Klarpunkt", "Klarpunkt", "Klarpunkt",
        "RESULT_ENDPOINT", "A compact endpoint replaces the clause 'bis klar'.",
    ),
    "dcda95c81a5460feb191": repair(
        "OL_CONTINUE", "OL=fortsetzen", "fortsetzen", "Fortsetzen",
        "ORDER_OL", "The inherited item supplies 'mit dem Vorigen'; the card contributes only continuation.",
    ),
    "dec401773c1f0347793d": repair(
        "OL_CONTINUE+OR_BATCH", "OL=Fortsetzung; OR=Ansatz", "Fortsetzungsansatz", "Fortsetzungsansatz",
        "ORDER_OL", "The compound makes the OL and OR contributions explicit without a whole phrase.",
    ),
    "d665560c8ff80799a82c": repair(
        "CH_WRAPPER+OL_CONTINUE", "OL=Fortsetzung", "Fortsetzungsposten", "Fortsetzungsposten",
        "ORDER_OL", "The local verb 'nehmen' belongs to sentence expansion, not the recurrent card.",
    ),
    "232195d6ff2f326322f7": repair(
        "OK_SET+OL_CONTINUE", "OK=einsetzen; OL=Fortsetzung", "Fortsetzung einsetzen", "Fortsetzung einsetzen",
        "ORDER_OL", "One invariant OK+OL composition replaces a reference-heavy phrase.",
    ),
    "322281bd391aa621f568": repair(
        "OK_SET+CH_WRAPPER+OL_CONTINUE", "OK=einsetzen; OL=Fortsetzung", "Fortsetzung einsetzen", "Fortsetzung einsetzen",
        "ORDER_OL", "Wrapped realization of the same OK+OL composition.",
    ),
    "28ffbc88b97772a75f1e": repair(
        "OL_CONTINUE+CHED_TRANSFER+TERMINAL_CLOSE", "OL=fortsetzen; CHED=führen; Endkarte=Schluss", "fortsetzen; Schluss", "Fortsetzen; Schluss",
        "ORDER_OL", "The visible owner supplies the transferred item; the portable value is continuation plus close.",
    ),
    "10488b911aae52b3b334": repair(
        "OT_FOLLOW+OR_BATCH", "OT=Folge; OR=Ansatz", "Folgeansatz", "Folgeansatz",
        "ORDER_OT", "Nominal OT compound selected by R1/R2/R4.",
    ),
    "54d0e228ca346110af05": repair(
        "OT_FOLLOW+AIIN_MEASURE", "OT=Folge; AIIN=Sollmaß", "Folgemaß", "Folgemaß",
        "ORDER_OT", "Nominal OT compound selected by R1/R2/R4.",
    ),
    "90bcf0a9ec0ef56399e6": repair(
        "OT_FOLLOW+AL_SITE", "OT=Folge; AL=Stelle", "Folgestelle", "Folgestelle",
        "ORDER_OT", "Nominal OT compound is more compositional than the phrase 'danach zur Stelle'.",
    ),
    "b6b654722e55729cc947": repair(
        "OT_FOLLOW+AR_OUTLET", "OT=Folge; AR=Auslass", "Folgeauslass", "Folgeauslass",
        "ORDER_OT", "Keep the order relation nominal; a later clause supplies the action.",
    ),
    "4de12cf322dfb76ded1e": repair(
        "OT_FOLLOW+CHED_TRANSFER+TERMINAL_CLOSE", "OT=Folge; CHED=umsetzen; Endkarte=Schluss", "Folgeumsetzung; Schluss", "Folgeumsetzung; Schluss",
        "ORDER_OT", "The compact compound avoids making one card an entire temporal clause.",
    ),
    "601b77449028deed39de": repair(
        "OT_FOLLOW+CHD_TRANSFER+TERMINAL_CLOSE", "OT=Folge; CHD=umsetzen; Endkarte=Schluss", "Folgeumsetzung; Schluss", "Folgeumsetzung; Schluss",
        "ORDER_OT", "Short allomorph of the same selected compound.",
    ),
    "1322bc176443fc2a8a86": repair(
        "OK_SET+OK_REPEAT+Y_CURRENT", "OK+OK=erneut; Y=Posten", "erneut ansetzen", "Erneut ansetzen",
        "REPEAT_DOUBLE_OK", "The doubled operation supplies repetition; the item is inherited from Y.",
    ),
    "f0db6d30cd34f4cb2a4d": repair(
        "CHK_WARM+GRADE_2+Y_CURRENT", "CHK=wärmen; EE=Stufe II; Y=Posten", "länger wärmen", "Länger wärmen",
        "CHK_GRADE", "The Y carrier need not be repeated in the short dictionary value.",
    ),
}


COMPONENTS = [
    ("AIIN", "SOLLMASS", "2f1c5e…; b5fcea…; 54d0e2…", "productive", "Not IIN and not inherently time."),
    ("IIN", "ZIELSTUFE", "2c8252…; 409de0…; fcc1de…", "productive", "Distinct exact-card family from AIIN."),
    ("OK", "ANSETZEN / IN ARBEIT SETZEN", "OKY; OKEY; OKEEY; OKEDY", "productive", "Local wet-contact wording comes from context."),
    ("E", "STUFE I", "OKEY; CHEKY; SOLKEY", "productive grade", "Usually short or mild, not a free time word."),
    ("EE", "STUFE II", "OKEEY; CHEEKY; SOLKEEY", "productive grade", "Usually longer or sustained."),
    ("EEE", "STUFE III", "OKEEEDY", "thin productive grade", "Usually complete; only one current card."),
    ("CHK", "WÄRMEN", "CHEKY; CHEEKY; CHKEEY; CHKEEDY", "productive", "Bounded family; CHCKHY is a counterexample."),
    ("SHED", "ABSETZEN", "SHEDY; SHEEDY; SHEDAL; QOKSHEDY", "productive", "Technical choice over the broader rival RUHEN."),
    ("CTH", "BEREIT", "CTHY; CTH+E+Y", "bounded productive", "CTHOOR and CTHAIIN remain whole-card counterexamples."),
    ("SOLK", "AUFFANGEN", "SOLKEY; SOLKEEY; SOLKEEDY", "productive", "Local station/collection family."),
    ("OT", "FOLGE", "OT+OR; OT+AIIN; OT+AL; OT+Y", "productive order", "Nouns read Folge-, actions read danach."),
    ("OL", "FORTSETZUNG", "OL; OL+OR; OL+AIN; OL+CHED", "productive order", "Inherited owner supplies the previous item."),
    ("OK+OK", "ERNEUT", "QOKOKCHY", "thin productive repetition", "One visible doubled-operation witness."),
    ("Y", "AKTUELLER POSTEN", "OKY; OKEY; CHKEEY", "productive carrier", "It does not itself mean open."),
    ("terminal construction", "SCHLUSS", "OKEDY; OKEEDY; SHEDY", "licensed whole construction", "Bare dy is not a global close sign."),
    ("AIN", "PORTION", "OLKAIN and prior quantity grid", "carried forward", "Separate from AIIN and IIN."),
    ("AL", "STELLE", "OTAL; SHEDAL; OKEEDAL", "carried forward", "Target/site rather than a body gloss."),
    ("AR", "QUELLE / AUSLASS", "OTAR and prior direction grid", "carried forward", "Direction is locally expanded."),
    ("OR", "ANSATZ", "OTCHOR; CHOLOR", "carried forward", "Prepared working batch."),
]


MODELS = [
    ("R1_LEHRMEISTER", "Kern–Grad–Ausgang, RUHEN", "high", "Some defaults retain contextual phrases.", "OT/OL teaching rule; endpoint nouns; OLDY repair"),
    ("R2_HISTORICAL", "recipe-like grades, ABSETZEN", "high", "Medical process vocabulary can over-specialize.", "ABSETZEN; STANDZEIT; FOLGE compounds; source comparison"),
    ("R3_TECHNICAL", "base + grade + carrier/close", "selected structural base", "A few whole-card glosses are larger than their evidence.", "close audit; AIIN/IIN split; counterexample inventory"),
    ("R4_CORRECTOR", "maximally short process atoms", "high lexical influence", "Audits fewer inherited counterexample cards.", "ANWÄRMEN; ROH; WARM; KLARPUNKT repair pressure"),
    ("SELECTED", "R3 structure + R2/R4 lexical compression", "selected", "Still a creative working codebook, not a decipherment.", "small compositional grammar plus learned whole cards"),
]


def build() -> dict[str, object]:
    dictionary = read_tsv(DICT_IN)
    events = read_tsv(EVENT_IN)
    sentence_source = {row["statement_id"]: row for row in read_tsv(SENTENCE_IN)}
    role_maps = {
        role: {row["joint_tuple_id"]: row for row in read_tsv(path)}
        for role, path in ROLE_DICTIONARIES.items()
    }
    if (len(dictionary), len(events), len(sentence_source)) != (173, 381, 116):
        raise AssertionError("unexpected R3 dimensions")

    selected_dictionary = []
    for original in dictionary:
        row = dict(original)
        row.update(
            selected_thermal_previous_segmentation=original["semantic_segmentation"],
            selected_thermal_previous_nucleus_de=original["stable_concrete_nucleus_de"],
            selected_thermal_previous_gloss_de=original["concrete_word_reading_de"],
            selected_thermal_source="R3_STRUCTURAL_BASE",
            selected_thermal_family=original.get("r3_thermal_family", "UNCHANGED"),
            selected_thermal_reason="R3 retained after four-role comparison.",
        )
        chosen = REPAIRS.get(row["joint_tuple_id"])
        if chosen:
            row["semantic_segmentation"] = chosen["semantic_segmentation"]
            row["stable_concrete_nucleus_de"] = chosen["stable_concrete_nucleus_de"]
            row["concrete_word_reading_de"] = chosen["concrete_word_reading_de"]
            row["reading_type"] = "SELECTED_THERMAL_TEMPORAL__" + chosen["family"]
            row["local_expansion_examples_de"] = "Selected process edition: " + chosen["concrete_word_reading_de"]
            row["selected_thermal_source"] = "FOUR_ROLE_LEXICAL_REPAIR"
            row["selected_thermal_family"] = chosen["family"]
            row["selected_thermal_reason"] = chosen["reason"]
        selected_dictionary.append(row)
    dmap = {row["joint_tuple_id"]: row for row in selected_dictionary}

    selected_events = []
    for original in events:
        row = dict(original)
        row.update(
            selected_thermal_previous_segmentation=original["semantic_segmentation"],
            selected_thermal_previous_nucleus_de=original["stable_concrete_nucleus_de"],
            selected_thermal_previous_gloss_de=original["concrete_word_reading_de"],
            selected_thermal_previous_context_de=original["contextual_event_reading_de"],
            selected_thermal_source="R3_STRUCTURAL_BASE",
            selected_thermal_family=original.get("r3_thermal_family", "UNCHANGED"),
            selected_thermal_reason="R3 retained after four-role comparison.",
        )
        chosen = REPAIRS.get(row["joint_tuple_id"])
        if chosen:
            drow = dmap[row["joint_tuple_id"]]
            row["semantic_segmentation"] = drow["semantic_segmentation"]
            row["stable_concrete_nucleus_de"] = drow["stable_concrete_nucleus_de"]
            row["concrete_word_reading_de"] = drow["concrete_word_reading_de"]
            row["contextual_event_reading_de"] = chosen["contextual_event_reading_de"]
            row["selected_thermal_source"] = "FOUR_ROLE_LEXICAL_REPAIR"
            row["selected_thermal_family"] = chosen["family"]
            row["selected_thermal_reason"] = chosen["reason"]
        selected_events.append(row)

    grouped: OrderedDict[str, list[dict[str, str]]] = OrderedDict()
    for event in selected_events:
        grouped.setdefault(event["statement_id"], []).append(event)
    selected_sentences = []
    for statement_id, group in grouped.items():
        base = sentence_source[statement_id]
        row = dict(base)
        repairs = [event for event in group if event["selected_thermal_source"] == "FOUR_ROLE_LEXICAL_REPAIR"]
        row["card_sequence_de"] = " · ".join(event["concrete_word_reading_de"] for event in group)
        row["event_slot_trace"] = " | ".join(f'{event["event_id"]}[{event["workshop_slots"]}]' for event in group)
        row["workshop_sentence_de"] = "; ".join(event["contextual_event_reading_de"] for event in group)
        row["selected_thermal_repaired_event_count"] = str(len(repairs))
        row["selected_thermal_families"] = "|".join(uniq([event["selected_thermal_family"] for event in repairs])) or "R3_RETAINED"
        row["selected_thermal_previous_card_sequence_de"] = base["card_sequence_de"]
        row["selected_thermal_previous_workshop_sentence_de"] = base["workshop_sentence_de"]
        selected_sentences.append(row)

    records: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in selected_sentences:
        records[row["record_unit_id"]].append(row)
    record_lines = [
        "# Ausgewählte Wärme-/Zeit-/Reihenfolgefassung — elf Records",
        "",
        "Kreative Werkstattlesung. Kartenwerte bleiben kurz; sichtbare Zeilen sind keine Satzgrenzen.",
        "",
    ]
    for record in RECORD_ORDER:
        rows = records[record]
        record_lines.extend([f"## {record} — {rows[0]['page']}", ""])
        for index, row in enumerate(rows, 1):
            record_lines.append(f"{index}. **{row['statement_id']}** — {row['workshop_sentence_de'].rstrip('.') }.")
        record_lines.append("")
    RECORD_OUT.write_text("\n".join(record_lines), encoding="utf-8")

    selected_paradigm = []
    for original in read_tsv(PARADIGM_IN):
        row = dict(original)
        ident = row["joint_tuple_id"]
        drow = dmap[ident]
        row.update(
            r1_default_de=role_maps["R1"][ident]["concrete_word_reading_de"],
            r2_default_de=role_maps["R2"][ident]["concrete_word_reading_de"],
            r3_default_de=role_maps["R3"][ident]["concrete_word_reading_de"],
            r4_default_de=role_maps["R4"][ident]["concrete_word_reading_de"],
            central_selected_segmentation=drow["semantic_segmentation"],
            central_selected_nucleus_de=drow["stable_concrete_nucleus_de"],
            central_selected_default_de=drow["concrete_word_reading_de"],
            central_decision_source=("FOUR_ROLE_LEXICAL_REPAIR" if ident in REPAIRS else "R3_STRUCTURAL_BASE"),
            central_decision_reason=(REPAIRS[ident]["reason"] if ident in REPAIRS else "R3 retained after four-role comparison."),
        )
        selected_paradigm.append(row)

    component_rows = [
        {
            "component": component,
            "selected_meaning_de": meaning,
            "examples": examples,
            "status": status,
            "boundary_or_caveat": caveat,
        }
        for component, meaning, examples, status, caveat in COMPONENTS
    ]
    model_rows = [
        {
            "model": model,
            "core": core,
            "selection_weight": weight,
            "main_weakness": weakness,
            "selected_contribution": contribution,
        }
        for model, core, weight, weakness, contribution in MODELS
    ]

    write_tsv(DICT_OUT, selected_dictionary)
    write_tsv(EVENT_OUT, selected_events)
    write_tsv(SENTENCE_OUT, selected_sentences)
    write_tsv(PARADIGM_OUT, selected_paradigm)
    write_tsv(COMPONENTS_OUT, component_rows)
    write_tsv(MODELS_OUT, model_rows)

    checks = {
        "cards_173": len(selected_dictionary) == 173,
        "events_381": len(selected_events) == 381,
        "sentences_116": len(selected_sentences) == 116,
        "records_11": set(records) == set(RECORD_ORDER),
        "event_ids_unique": len({row["event_id"] for row in selected_events}) == 381,
        "dictionary_ids_unique": len(dmap) == 173,
        "events_bound_to_dictionary": all(
            event["concrete_word_reading_de"] == dmap[event["joint_tuple_id"]]["concrete_word_reading_de"]
            for event in selected_events
        ),
        "all_cards_have_defaults": all(row["concrete_word_reading_de"] for row in selected_dictionary),
        "all_events_have_context": all(row["contextual_event_reading_de"] for row in selected_events),
        "all_events_partitioned": sum(int(row["event_count"]) for row in selected_sentences) == 381,
        "only_fixed_pages": {row["page"] for row in selected_events} == ALLOWED_PAGES,
        "f84_and_f84r_absent": all(not row["page"].startswith("f84") for row in selected_events),
        "repairs_exact": {
            row["joint_tuple_id"] for row in selected_dictionary
            if row["selected_thermal_source"] == "FOUR_ROLE_LEXICAL_REPAIR"
        } == set(REPAIRS),
        "components_19": len(component_rows) == 19,
        "models_5": len(model_rows) == 5,
        "bare_dy_not_global_close": dmap["b921a237be883a820352"]["concrete_word_reading_de"] != "Schluss",
        "aiin_iin_distinct": dmap["2f1c5e56e8f0ff459065"]["concrete_word_reading_de"] != dmap["2c82523794dcb7d2b343"]["concrete_word_reading_de"],
        "oldy_repaired": dmap["1b1ffdd869fb1429ad03"]["concrete_word_reading_de"] == "fortsetzen; Schluss",
    }
    validation = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "counts": {
            "cards": len(selected_dictionary),
            "events": len(selected_events),
            "sentences": len(selected_sentences),
            "records": len(records),
            "r3_structural_revised_cards": sum(row.get("r3_thermal_status") == "REVISED_R3" for row in selected_dictionary),
            "central_lexical_repairs": len(REPAIRS),
            "central_repaired_events": sum(row["selected_thermal_source"] == "FOUR_ROLE_LEXICAL_REPAIR" for row in selected_events),
            "paradigm_rows": len(selected_paradigm),
        },
        "model": {
            "process_grade": "E / EE / EEE = STUFE I / II / III",
            "thermal_core": "CHK = WAERMEN",
            "settling_core": "SHED = ABSETZEN",
            "successor": "OT = FOLGE",
            "continuation": "OL = FORTSETZUNG",
            "repeat": "OK+OK = ERNEUT",
            "carrier": "Y = AKTUELLER POSTEN",
            "close": "LICENSED TERMINAL CONSTRUCTION; BARE DY IS NOT GLOBAL CLOSE",
        },
        "astro": "UNCHANGED",
        "sealed": {"f84": True, "f84r": True},
    }
    VALIDATION_OUT.write_text(json.dumps(validation, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    outputs = [
        DICT_OUT, EVENT_OUT, SENTENCE_OUT, RECORD_OUT, PARADIGM_OUT,
        COMPONENTS_OUT, MODELS_OUT, VALIDATION_OUT,
    ]
    summary = {
        "status": validation["status"],
        "input_hashes": {path.name: sha256(path) for path in [DICT_IN, EVENT_IN, SENTENCE_IN, PARADIGM_IN, *ROLE_DICTIONARIES.values()]},
        "output_hashes": {path.name: sha256(path) for path in outputs},
        "counts": validation["counts"],
        "sealed": {"f84": True, "f84r": True},
    }
    SUMMARY_OUT.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if validation["status"] != "PASS":
        raise SystemExit(json.dumps(validation, ensure_ascii=False, indent=2))
    return summary


if __name__ == "__main__":
    print(json.dumps(build(), ensure_ascii=False, indent=2, sort_keys=True))
