#!/usr/bin/env python3
"""Build the selected creative application/administration workshop edition."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import OrderedDict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = ROOT / "experiments/yolo/sidequest_semantic_filtration_separation_completion"

DICT_IN = SOURCE / "SELECTED_173_FILTRATION_DICTIONARY.tsv"
EVENT_IN = SOURCE / "SELECTED_381_FILTRATION_INTERLINEAR.tsv"
COMPONENT_IN = SOURCE / "SELECTED_FILTRATION_COMPONENTS.tsv"
UNRESOLVED_IN = SOURCE / "REMAINING_UNRESOLVED_AFTER_FILTRATION.tsv"

DICT_OUT = HERE / "SELECTED_173_APPLICATION_DICTIONARY.tsv"
EVENT_OUT = HERE / "SELECTED_381_APPLICATION_INTERLINEAR.tsv"
STATEMENT_OUT = HERE / "SELECTED_116_APPLICATION_SENTENCES.tsv"
RECORD_OUT = HERE / "SELECTED_11_APPLICATION_RECORDS.md"
COMPONENT_OUT = HERE / "SELECTED_APPLICATION_COMPONENTS.tsv"
PARADIGM_OUT = HERE / "SELECTED_APPLICATION_PARADIGM.tsv"
BRANCH_OUT = HERE / "SELECTED_APPLICATION_BRANCHES.tsv"
COUNTER_OUT = HERE / "APPLICATION_COUNTEREXAMPLES.tsv"
UNRESOLVED_OUT = HERE / "REMAINING_UNRESOLVED_AFTER_APPLICATION.tsv"
SUMMARY_OUT = HERE / "SELECTED_BUILD_SUMMARY.json"


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


def ov(
    parse: str,
    nucleus: str,
    gloss: str,
    family: str,
    strength: str,
    slots: str,
    note: str,
) -> dict[str, str]:
    return {
        "semantic_segmentation": parse,
        "stable_concrete_nucleus_de": nucleus,
        "concrete_word_reading_de": gloss,
        "reading_type": "SELECTED_APPLICATION__" + family,
        "family": family,
        "strength": strength,
        "slots": slots,
        "note": note,
    }


# AL is shortened to one portable atom, STELLE.  Body site, basin, opening,
# cloth, or apparatus station is supplied by the local owner.  The longer
# action cards remain a small learned nomenclator.
OVERRIDES = {
    "dd0ecaf5e27d81befffc": ov("AL_SITE", "AL=Stelle", "Stelle", "AL_SITE", "SELECTED_RECURRENT_CORE", "TARGET", "Ten base events across five pages; the owner supplies the kind of site."),
    "308e8ea2d5d190c498e8": ov("Q_RENDERER+OK+AL_SITE", "OK=einsetzen; AL=Stelle", "an die Stelle setzen", "AL_SITE", "SELECTED_RECURRENT_COMPOSITION", "TARGET+OPERATION", "Six events preserve the same neutral target operation."),
    "4a7a6326ac95a8809302": ov("Q_RENDERER+OK+AL_SITE+Y_REFERENT", "OK=einsetzen; AL=Stelle; Y=laufender Posten", "Posten zur Stelle setzen", "AL_SITE", "SELECTED_SINGLETON_COMPOSITION", "OWNER_ITEM+TARGET+OPERATION", "The following cloth/passage chain is technical, showing that AL is not inherently anatomical."),
    "90bcf0a9ec0ef56399e6": ov("OT_NEXT+AL_SITE", "OT=danach; AL=Stelle", "danach zur Stelle", "AL_SITE", "SELECTED_RECURRENT_COMPOSITION", "TARGET", "Three f83r station changes; no flow direction is encoded."),
    "93f69c38fdedee1598e9": ov("OK+GRADE_2+AL_SITE", "OK=einsetzen; EE=anhaltend; AL=Stelle", "länger an der Stelle halten", "AL_SITE", "SELECTED_SINGLETON_GRID_CELL", "TARGET+STATE_GRADE", "Completes the long-grade Y/AL/DY row without naming skin or a vessel."),
    "00d8ebe3c68294eeac39": ov("CHD+AL_SITE", "CHD=umsetzen; AL=Stelle", "an der Stelle umsetzen", "AL_SITE", "SELECTED_SINGLETON_COMPOSITION", "TARGET+OPERATION", "The short site atom replaces the longer target-site gloss."),
    "433713294b25b0a12f66": ov("L+CHED+AL_SITE", "L+CHED=hinausführen; AL=Stelle", "Auslassstelle", "AL_SITE_EXTENSION", "SELECTED_SINGLETON_COMPOSITION", "TARGET", "The transfer hull supplies outlet; AL supplies only site."),
    "7811a7daff25d476e28d": ov("OLS_LEARNED+AL_SITE+Y_SURFACE", "AL=Stelle; lokale OLS-Hülle=unten", "untere Stelle", "AL_SITE_EXTENSION", "SELECTED_SINGLETON_COMPOSITION", "TARGET", "Lower is local to the learned hull, not part of AL."),
    "97ddca78c9ebcc956d04": ov("LD_OR_LEARNED+AL_SITE", "AL=Stelle; lokale Hülle=bezeichnet", "bezeichnete Stelle", "AL_SITE_EXTENSION", "SELECTED_SINGLETON_COMPOSITION", "TARGET", "The hull supplies the designation; AL supplies only site."),
    "abb23e5e6936b4147f76": ov("SHED_REST+AL_SITE", "SHED=ruhen oder absetzen; AL=Stelle", "Ruhe-/Absetzstelle", "AL_SITE_EXTENSION", "SELECTED_RECURRENT_COMPOSITION", "TARGET+STATE_GRADE", "Two records retain the same rest-site reading."),
    "ba540da978ea132f6da5": ov("P+CHED+AL_SITE", "P+CHED=hineinführen; AL=Stelle", "Einfüllstelle", "AL_SITE_EXTENSION", "SELECTED_SINGLETON_COMPOSITION", "TARGET", "The inward transfer hull supplies inlet; AL supplies only site."),

    # Short open/sustained contact values.  The ten OKEEDY events are broadened
    # from soaking to sustained action; soaking remains their liquid-context
    # expansion.
    "08bd5ca0c2ad137a056d": ov("OK+GRADE_1+Y_REFERENT", "OK=ansetzen; E=kurz; Y=laufender Posten", "kurz anlegen", "CONTACT_GRID", "SELECTED_RECURRENT_GRID", "OWNER_ITEM+OPERATION+STATE_GRADE", "Two owners support brief contact; Y supplies the current item."),
    "0275fbf14e07935b0a45": ov("OK+GRADE_2+Y_REFERENT", "OK=ansetzen; EE=länger; Y=laufender Posten", "länger halten", "CONTACT_GRID", "SELECTED_RECURRENT_GRID", "OWNER_ITEM+OPERATION+STATE_GRADE", "Seven events across four records support sustained contact without fixing body versus apparatus."),
    "7d25241b0e56c836372a": ov("OK+GRADE_2+DY_CLOSE", "OK=ansetzen; EE=länger; Endkarte=Schluss", "länger einwirken; Schluss", "CONTACT_GRID", "SELECTED_RECURRENT_GRID", "OPERATION+STATE_GRADE+CLOSE", "Ten cells range from liquid soaking to cloth or station contact; the portable default is sustained action."),

    # Learned site and action cards.  Their values are short; no fictitious
    # common visible root is asserted.
    "5fca8fc3dee57e1d8c1f": ov("LCHEEY_WET_SITE_WHOLE_CARD", "LCHEEY=benetzte Stelle", "benetzte Stelle", "APPLICATION_SITE_DECK", "SELECTED_SINGLETON_WHOLE_CARD", "TARGET", "The lower f82r figure/pool owner supports contact but not an anatomical name."),
    "c205570c49d4d93c23d3": ov("QOLKY_TREATMENT_SITE_WHOLE_CARD", "QOLKY=Behandlungsstelle", "Behandlungsstelle", "APPLICATION_SITE_DECK", "SELECTED_SINGLETON_WHOLE_CARD", "TARGET", "The following outlet makes a treated station at least as plausible as a body part."),
    "c10aec6d4dd877ec8bd8": ov("CHOY_WASH_WHOLE_CARD", "CHOY=waschen", "waschen", "APPLICATION_ACTION_DECK", "SELECTED_SINGLETON_WHOLE_CARD", "OPERATION", "Water is the H5 local realization, not a required part of the card meaning."),
    "74c76d589d44120f647b": ov("DSHEOL_RUB_WHOLE_CARD", "DSHEOL=einreiben", "einreiben", "APPLICATION_ACTION_DECK", "SELECTED_SINGLETON_WHOLE_CARD", "OPERATION", "A concrete rubbing action; coating a technical surface remains the strongest rival."),
    "348e81ba084c5acdb32b": ov("SHECTHEDCHY_SPREAD_WHOLE_CARD", "SHECTHEDCHY=aufstreichen", "aufstreichen", "APPLICATION_ACTION_DECK", "SELECTED_SINGLETON_WHOLE_CARD", "OPERATION", "A second learned spreading action; it is not forced to share a visible root with DSHEOL."),
    "7f68f60279efe6b28cd7": ov("RSHE_WASH_WHOLE_CARD+DY_CLOSE", "RSHE=Waschung; Endkarte=Schluss", "Waschung; Schluss", "APPLICATION_ACTION_DECK", "SELECTED_SINGLETON_WHOLE_CARD", "OPERATION+CLOSE", "The former unsupported part value is removed; the one complete cell retains a wash close."),
    "95987d6f198d6d247511": ov("CHEECKHO_APPLY_WHOLE_CARD+DY_CLOSE", "CHEECKHO=auftragen; Endkarte=Schluss", "auftragen; Schluss", "APPLICATION_ACTION_DECK", "SELECTED_SINGLETON_WHOLE_CARD", "OPERATION+CLOSE", "The preceding H5 wash licenses application; external/body specificity stays local."),
    "eb2e4bc143f623ee03ac": ov("Q_RENDERER+OK+Y_REFERENT+LDDY_FASTEN_CLOSE", "OK+Y=Posten ansetzen; LDDY=befestigen und schließen", "Posten befestigen; Schluss", "LDDY_FASTEN_CLOSE", "SELECTED_SINGLETON_LEARNED_CORE", "OWNER_ITEM+OPERATION+CLOSE", "Application and apparatus readings converge on fastening; poultice, cloth, or insert is local."),
}


CONTEXT_BY_EVENT = {
    "E084": "Wasche die bezeichnete Stelle",
    "E086": "Trage den laufenden Posten auf; Schluss",
    "E146": "Behandlungsstelle",
    "E160": "Reibe die bezeichnete Stelle ein",
    "E206": "Benetzte Stelle",
    "E225": "Führe die Waschung aus; Schluss",
    "E250": "Streiche den Posten auf",
    "E326": "Befestige den laufenden Posten; Schluss",
}


# The selected paradigm deliberately includes inherited preparation, quantity,
# current-item and contact cards, even where their dictionary values do not
# change in this round.
PARADIGM = [
    ("01_PREPARATION", "b9d7b6d68209a9019e7a", "CHO+OR", "PLANT_PREPARATION"),
    ("01_PREPARATION", "dec401773c1f0347793d", "OL+OR", "PREVIOUS_PREPARATION"),
    ("01_PREPARATION", "7a4bb8136330ee4e6e56", "OR", "PREPARATION"),
    ("01_PREPARATION", "6afeb5c9ab9f6cbdea0d", "OR+AIN", "PREPARATION_PORTION"),
    ("01_PREPARATION", "10488b911aae52b3b334", "OT+OR", "NEXT_PREPARATION"),
    ("02_QUANTITY", "2f1c5e56e8f0ff459065", "AIIN", "MEASURE"),
    ("02_QUANTITY", "9da1b6ac2c929daea697", "AIN", "PORTION"),
    ("02_QUANTITY", "b5fcea1eaed06b2f2291", "OK+AIIN", "SET_MEASURE"),
    ("02_QUANTITY", "1645e612504fcef59ced", "OK+AIN", "ADD_PORTION"),
    ("02_QUANTITY", "54d0e228ca346110af05", "OT+AIIN", "NEXT_MEASURE"),
    ("02_QUANTITY", "f7dc90b2c31fd341f0a4", "Y+AIIN", "CURRENT_MEASURE"),
    ("02_QUANTITY", "403c1592f918c8f23b88", "Y+AIN", "CURRENT_PORTION"),
    ("02_QUANTITY", "d929a14ec45749b2e805", "Y+AIN", "THIS_PORTION"),
    ("03_TARGET", "dd0ecaf5e27d81befffc", "AL", "SITE"),
    ("03_TARGET", "5fca8fc3dee57e1d8c1f", "LCHEEY", "WET_SITE"),
    ("03_TARGET", "c205570c49d4d93c23d3", "QOLKY", "TREATMENT_SITE"),
    ("03_TARGET", "308e8ea2d5d190c498e8", "OK+AL", "SET_AT_SITE"),
    ("03_TARGET", "90bcf0a9ec0ef56399e6", "OT+AL", "NEXT_SITE"),
    ("03_TARGET", "4a7a6326ac95a8809302", "OK+AL+Y", "CURRENT_TO_SITE"),
    ("03_TARGET", "93f69c38fdedee1598e9", "OK+EE+AL", "HOLD_AT_SITE"),
    ("04_CURRENT_ITEM", "b921a237be883a820352", "Y", "CURRENT_ITEM"),
    ("04_CURRENT_ITEM", "9ad66e67803a12e745de", "OK+CHY", "SET_CURRENT_ITEM"),
    ("04_CURRENT_ITEM", "276a7c2d74d1143446f4", "OK+Y", "SET_CURRENT_ITEM"),
    ("05_ACTION", "c10aec6d4dd877ec8bd8", "CHOY", "WASH"),
    ("05_ACTION", "74c76d589d44120f647b", "DSHEOL", "RUB"),
    ("05_ACTION", "893c570f3fa3fce99711", "KCHOL", "LAY_ON"),
    ("05_ACTION", "348e81ba084c5acdb32b", "SHECTHEDCHY", "SPREAD"),
    ("06_CONTACT", "08bd5ca0c2ad137a056d", "OK+E+Y", "BRIEF_OPEN_CONTACT"),
    ("06_CONTACT", "0275fbf14e07935b0a45", "OK+EE+Y", "SUSTAINED_OPEN_CONTACT"),
    ("06_CONTACT", "7db18b2f0fb7ed0fcfd3", "OK+E+DY", "BRIEF_CLOSED_CONTACT"),
    ("06_CONTACT", "7d25241b0e56c836372a", "OK+EE+DY", "SUSTAINED_CLOSED_CONTACT"),
    ("06_CONTACT", "d25110e0d8488927278f", "OK+EEE+DY", "COMPLETE_CLOSED_CONTACT"),
    ("07_CLOSE", "95987d6f198d6d247511", "CHEECKHO+DY", "APPLY_CLOSE"),
    ("07_CLOSE", "eb2e4bc143f623ee03ac", "OK+Y+LDDY", "FASTEN_CLOSE"),
    ("07_CLOSE", "7f68f60279efe6b28cd7", "RSHE+DY", "WASH_CLOSE"),
]


BRANCHES = OrderedDict(
    [
        ("H3-S001", ("PREPARE_CLEAR_EXTRACT", "auswringen → stehen lassen → nachseihen → Klarauszug", "preparation stage shared by both content models")),
        ("H4-S004", ("MEASURE_TARGET_PREPARATION", "Maß → Stelle → Wärme → Zubereitung → Portion", "application reading possible; plant work station remains rival")),
        ("H5-S001", ("HERBAL_LAY_ON", "Pflanzenzubereitung → Maß → auflegen → Stelle", "strongest Herbal application branch")),
        ("H5-S002", ("HERBAL_WASH_APPLY", "voriger Posten → waschen → auftragen → Schluss", "strongest complete Herbal apply-close branch")),
        ("B1-S012", ("BRIEF_WASH_CONTACT", "Waschgang → kurz anlegen → waschen → Schluss", "body wash and apparatus rinse are isomorphic")),
        ("B1-S016", ("TARGET_HOLD_REST", "Stelle → länger halten → ruhen → Schluss", "targeted sustained contact")),
        ("B1-S018", ("RUB_OR_COAT", "Gefäß → einreiben → Sollstufe → auffangen", "technical coating remains stronger local rival")),
        ("B2-S005", ("TECHNICAL_INSERT", "Stelle → Seihtuch → Durchlauf → Maß → warm halten → abziehen", "strongest apparatus branch")),
        ("B2-S012", ("CLEAR_EXTRACT_APPLICATION", "Klarauszug → länger halten → benetzte Stelle → Maß → durchtränken", "strongest body-contact branch")),
        ("B2-S016", ("TARGET_BRIEF_INSERT", "Stelle → Quelle → Maß → kurz anlegen → hineinführen", "station handling stronger than body treatment")),
        ("B3-S011", ("SPREAD_AND_WORK", "aufstreichen → Posten einsetzen → durcharbeiten → abkühlen", "application and surface coating remain live")),
        ("B4-S004", ("FASTEN_CLOSE", "Posten befestigen → Schluss", "local poultice versus apparatus insert")),
        ("B4-S005", ("CLOTH_SUSTAINED_CONTACT", "Tuch → durcharbeiten → länger einwirken", "bridges poultice and filter-insert readings")),
    ]
)


COUNTEREXAMPLES = [
    ("AL_NOT_BODY", "dd0ecaf5e27d81befffc", "al|chal|cheal|dal|sal|tal", "Stelle", "The same card appears at plant, pool, vessel, gap and apparatus owners."),
    ("QOKALY_FILTER_CONTEXT", "4a7a6326ac95a8809302", "qokaly", "Posten zur Stelle setzen", "Its only event is immediately followed by cloth, passage, measure, warmth and withdrawal."),
    ("LCHEEY_NOT_ANATOMY", "5fca8fc3dee57e1d8c1f", "lcheey", "benetzte Stelle", "Figures touch the lower pool, but no named body part is drawn."),
    ("LDDY_ONE_CARD_ONLY", "eb2e4bc143f623ee03ac", "qokylddy", "Posten befestigen; Schluss", "Befestigen is a learned one-card core, not a productive L/DD/DY morphology."),
    ("OKEEDY_NOT_ALWAYS_SOAK", "7d25241b0e56c836372a", "qokeedy", "länger einwirken; Schluss", "Ten cells include liquid, cloth, mixture and owner-ambiguous contexts."),
    ("KCHOL_WHOLE_CARD", "893c570f3fa3fce99711", "kchol", "auflegen", "The value does not license K or CHOL as a global application morpheme."),
    ("ACTION_DECK_NO_SHARED_ROOT", "c10aec6d4dd877ec8bd8|74c76d589d44120f647b|348e81ba084c5acdb32b|95987d6f198d6d247511", "choy|dsheol|shecthedchy|cheeckhody", "waschen|einreiben|aufstreichen|auftragen", "These are learned specialist cards, not a fabricated substring paradigm."),
    ("DY_EXACT_CARD_ONLY", "7db18b2f0fb7ed0fcfd3|7d25241b0e56c836372a|d25110e0d8488927278f", "qokedy|qokeedy|qokeeedy", "licensed contact closes", "Visible dy alone remains insufficient; exact identity licenses closure."),
    ("CHOY_NO_GLOBAL_O_WATER", "c10aec6d4dd877ec8bd8", "choy", "waschen", "Water is supplied by the H5 reading and does not turn O or Y into water."),
    ("BODY_APPARATUS_ISOMORPHY", "08bd5ca0c2ad137a056d|0275fbf14e07935b0a45", "okey|okeey", "kurz anlegen|länger halten", "The same contact grammar describes a body application, bath, cloth or apparatus insert."),
]


def build_components() -> list[dict[str, str]]:
    rows = read_tsv(COMPONENT_IN)
    for row in rows:
        if row["component_id"] == "AL":
            row.update(
                working_meaning_de="Stelle; neutraler Ziel- oder Arbeitsort",
                licensed_environment="base card and OK/OT/CHED/P/L compounds",
                evidence_summary="ten base events plus recurrent target compounds across Herbal and Biological records",
                important_limit="body, basin, vessel, opening, cloth or apparatus comes from the local owner",
            )
        elif row["component_id"] == "E_GRADE_1":
            row["working_meaning_de"] = "kurzer oder direkter Kontakt"
        elif row["component_id"] == "E_GRADE_2":
            row["working_meaning_de"] = "anhaltender oder längerer Kontakt"
        elif row["component_id"] == "E_GRADE_3":
            row["working_meaning_de"] = "vollständiger Kontakt oder Durchtränkung"
        elif row["component_id"] == "LDDY_APPLICATION_CLOSE":
            row.update(
                working_meaning_de="befestigen und den Schritt schließen",
                status="SELECTED_SINGLE_CARD_LEARNED_CORE",
                licensed_environment="qokylddy only",
                evidence_summary="one terminal card between target/hold and cloth/contact steps",
                important_limit="poultice, bandage, cloth or apparatus insert is a local expansion",
            )
    rows.extend(
        [
            {"component_id": "APPLICATION_SITE_DECK", "visible_realizations": "qolky; lcheey", "working_meaning_de": "Behandlungsstelle; benetzte Stelle", "status": "SELECTED_NOMENCLATOR_PAIR", "licensed_environment": "two exact singleton site cards", "evidence_summary": "both occupy target roles next to outlet/contact operations", "important_limit": "neither card is an anatomical noun"},
            {"component_id": "APPLICATION_ACTION_DECK", "visible_realizations": "choy; dsheol; shecthedchy; kchol; rshedy; cheeckhody", "working_meaning_de": "waschen; einreiben; aufstreichen; auflegen; Waschung; auftragen", "status": "SELECTED_NOMENCLATOR_DECK", "licensed_environment": "six exact specialist action cards", "evidence_summary": "Herbal and Biological statements separate preparation, target, action, grade and close", "important_limit": "no shared visible root and body versus apparatus remains owner-local"},
        ]
    )
    if len({row["component_id"] for row in rows}) != len(rows):
        raise AssertionError("duplicate component IDs")
    return rows


def build_unresolved() -> list[dict[str, str]]:
    rows = read_tsv(UNRESOLVED_IN)
    for row in rows:
        if row["candidate_component"] == "LDDY_PORTABILITY":
            row.update(
                current_best_constraint="selected learned core BEFESTIGEN; SCHLUSS inside qokylddy",
                why_not_closed="one exact card cannot establish a portable free component",
                working_default_until_better_model="Posten befestigen; Schluss",
                prediction_that_could_improve_it="a second LDDY carrier should retain fastening under another owner",
            )
        elif row["candidate_component"] == "MEMORIZED_WHOLE_CARDS":
            row.update(
                current_best_constraint="six application actions and two site cards now have short stable defaults",
                why_not_closed="the remaining local nomenclator still lacks substitutions",
                working_default_until_better_model="retain short exact-card values",
                prediction_that_could_improve_it="another record should reuse one application card in the same action slot",
            )
    rows.extend(
        [
            {"candidate_component": "BODY_VS_APPARATUS_TARGET", "current_best_constraint": "AL is a neutral site and the same contact grid fits both branches", "why_not_closed": "most Biological owners combine figures with vessels or conduits", "working_default_until_better_model": "medical reading first where direct figure-fluid contact exists; technical rival elsewhere", "prediction_that_could_improve_it": "a site card should recur at a visually unambiguous body-only or apparatus-only owner"},
            {"candidate_component": "DSHEOL_VS_SHECTHEDCHY", "current_best_constraint": "einreiben versus aufstreichen as two learned action defaults", "why_not_closed": "one event each and no shared owner contrast", "working_default_until_better_model": "keep the two concrete hand actions distinct", "prediction_that_could_improve_it": "reuse should preserve the rub/spread distinction"},
            {"candidate_component": "CHOY_WATER_CONTENT", "current_best_constraint": "CHOY=waschen; water is the H5 local medium", "why_not_closed": "one event", "working_default_until_better_model": "waschen", "prediction_that_could_improve_it": "reuse without water should retain the wash action"},
            {"candidate_component": "OKEEDY_HOLD_VS_SOAK", "current_best_constraint": "portable default is longer action/contact; liquid contexts expand to soaking", "why_not_closed": "ten events span several owner types but their objects are inherited", "working_default_until_better_model": "länger einwirken; Schluss", "prediction_that_could_improve_it": "a new non-liquid owner should still support sustained contact"},
        ]
    )
    return rows


def build() -> dict[str, object]:
    dictionary = read_tsv(DICT_IN)
    events = read_tsv(EVENT_IN)
    source_by_id = {row["joint_tuple_id"]: row for row in dictionary}
    missing = sorted(set(OVERRIDES) - set(source_by_id))
    if missing:
        raise AssertionError(f"missing override IDs: {missing}")

    dict_fields = list(dictionary[0]) + [
        "application_previous_segmentation",
        "application_previous_nucleus_de",
        "application_previous_gloss_de",
        "application_revision_family",
        "application_revision_strength",
        "application_revision_note",
    ]
    revised_dictionary: list[dict[str, str]] = []
    for source in dictionary:
        row = dict(source)
        selected = OVERRIDES.get(row["joint_tuple_id"])
        if selected:
            row["application_previous_segmentation"] = row["semantic_segmentation"]
            row["application_previous_nucleus_de"] = row["stable_concrete_nucleus_de"]
            row["application_previous_gloss_de"] = row["concrete_word_reading_de"]
            for key in ("semantic_segmentation", "stable_concrete_nucleus_de", "concrete_word_reading_de", "reading_type"):
                row[key] = selected[key]
            row["local_expansion_examples_de"] = "Anwendungsfassung: " + selected["concrete_word_reading_de"]
            row["variation_note"] += "; application: " + selected["note"]
            row["application_revision_family"] = selected["family"]
            row["application_revision_strength"] = selected["strength"]
            row["application_revision_note"] = selected["note"]
        else:
            row.update(
                application_previous_segmentation="",
                application_previous_nucleus_de="",
                application_previous_gloss_de="",
                application_revision_family="UNCHANGED",
                application_revision_strength="UNCHANGED",
                application_revision_note="NOT_APPLICABLE",
            )
        revised_dictionary.append(row)
    by_id = {row["joint_tuple_id"]: row for row in revised_dictionary}

    event_fields = list(events[0]) + [
        "application_previous_segmentation",
        "application_previous_nucleus_de",
        "application_previous_gloss_de",
        "application_previous_context_de",
        "application_revision_family",
        "application_revision_strength",
    ]
    revised_events: list[dict[str, str]] = []
    for source in events:
        row = dict(source)
        selected = OVERRIDES.get(row["joint_tuple_id"])
        if selected:
            row["application_previous_segmentation"] = row["semantic_segmentation"]
            row["application_previous_nucleus_de"] = row["stable_concrete_nucleus_de"]
            row["application_previous_gloss_de"] = row["concrete_word_reading_de"]
            row["application_previous_context_de"] = row["contextual_event_reading_de"]
            card = by_id[row["joint_tuple_id"]]
            row["semantic_segmentation"] = card["semantic_segmentation"]
            row["stable_concrete_nucleus_de"] = card["stable_concrete_nucleus_de"]
            row["concrete_word_reading_de"] = card["concrete_word_reading_de"]
            row["contextual_event_reading_de"] = CONTEXT_BY_EVENT.get(row["event_id"], sentence_case(card["concrete_word_reading_de"]))
            row["workshop_slots"] = selected["slots"]
            row["application_revision_family"] = selected["family"]
            row["application_revision_strength"] = selected["strength"]
        else:
            row.update(
                application_previous_segmentation="",
                application_previous_nucleus_de="",
                application_previous_gloss_de="",
                application_previous_context_de="",
                application_revision_family="UNCHANGED",
                application_revision_strength="UNCHANGED",
            )
        revised_events.append(row)

    grouped: dict[str, list[dict[str, str]]] = OrderedDict()
    for row in revised_events:
        grouped.setdefault(row["statement_id"], []).append(row)
    statement_fields = [
        "statement_id", "record_unit_id", "page", "loci", "field_ids", "event_ids", "event_count",
        "application_revised_event_count", "surface_sequence", "card_sequence_de", "event_slot_trace",
        "canonical_slots_present", "workshop_sentence_de", "physical_line_note",
    ]
    slot_order = ["OWNER_ITEM", "SOURCE", "QUANTITY", "PREPARATION", "TARGET", "OPERATION", "FLOW_TRANSFER", "STATE_GRADE", "CLOSE"]
    statements: list[dict[str, str]] = []
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
                "application_revised_event_count": str(sum(row["application_revision_family"] != "UNCHANGED" for row in rows)),
                "surface_sequence": " · ".join(row["surface_display"] for row in rows),
                "card_sequence_de": " · ".join(row["concrete_word_reading_de"] for row in rows),
                "event_slot_trace": " | ".join(f"{row['event_id']}[{row['workshop_slots']}]" for row in rows),
                "canonical_slots_present": ">".join(slot for slot in slot_order if slot in present),
                "workshop_sentence_de": sentence_case("; ".join(row["contextual_event_reading_de"] for row in rows)),
                "physical_line_note": rows[-1]["statement_continuation"],
            }
        )
    statements_by_id = {row["statement_id"]: row for row in statements}

    records: dict[str, list[dict[str, str]]] = OrderedDict()
    for row in statements:
        records.setdefault(row["record_unit_id"], []).append(row)
    markdown = [
        "# Elf vollständige Records nach der Anwendungsrunde", "",
        "Kreative Werkstattlesung: STELLE und Kontaktgrad sind portable Defaults;",
        "Körper, Bad, Tuch oder Apparat werden lokal ergänzt. Zeile ist kein Satzschluss.", "",
    ]
    for record_id, rows in records.items():
        markdown.extend([f"## {record_id} — {rows[0]['page']}", ""])
        for index, row in enumerate(rows, 1):
            markdown.append(f"{index}. **{row['statement_id']}** `{row['canonical_slots_present']}` — {row['workshop_sentence_de']}.")
        markdown.append("")
    RECORD_OUT.write_text("\n".join(markdown).rstrip() + "\n", encoding="utf-8")

    components = build_components()
    unresolved = build_unresolved()
    event_counts = {ident: sum(row["joint_tuple_id"] == ident for row in revised_events) for ident in source_by_id}
    paradigm_rows = [
        {
            "application_stage": stage,
            "joint_tuple_id": ident,
            "surface_family": by_id[ident]["surface_family"],
            "formula": formula,
            "selected_reading_de": by_id[ident]["concrete_word_reading_de"],
            "events": str(event_counts[ident]),
            "application_role": role,
            "revision_status": OVERRIDES[ident]["strength"] if ident in OVERRIDES else "INHERITED_SELECTED_VALUE",
            "important_limit": OVERRIDES[ident]["note"] if ident in OVERRIDES else "Inherited exact-card value; included to make the full application checklist explicit.",
        }
        for stage, ident, formula, role in PARADIGM
    ]
    branch_rows = []
    for statement_id, (name, stages, rival) in BRANCHES.items():
        statement = statements_by_id[statement_id]
        branch_rows.append(
            {
                "branch_name": name,
                "statement_id": statement_id,
                "record_unit_id": statement["record_unit_id"],
                "page": statement["page"],
                "loci": statement["loci"],
                "surface_sequence": statement["surface_sequence"],
                "selected_card_sequence_de": statement["card_sequence_de"],
                "application_stages_de": stages,
                "complete_workshop_reading_de": statement["workshop_sentence_de"],
                "body_or_medical_expansion_de": "Anwendung an der bezeichneten Körper-, Bade- oder Auflagestelle",
                "apparatus_rival_de": rival,
            }
        )
    counter_rows = [
        {"counterexample": kind, "joint_tuple_ids": ident, "surface_forms": surface, "retained_reading_de": gloss, "reason": reason}
        for kind, ident, surface, gloss, reason in COUNTEREXAMPLES
    ]

    write_tsv(DICT_OUT, revised_dictionary, dict_fields)
    write_tsv(EVENT_OUT, revised_events, event_fields)
    write_tsv(STATEMENT_OUT, statements, statement_fields)
    write_tsv(COMPONENT_OUT, components, list(components[0]))
    write_tsv(PARADIGM_OUT, paradigm_rows, list(paradigm_rows[0]))
    write_tsv(BRANCH_OUT, branch_rows, list(branch_rows[0]))
    write_tsv(COUNTER_OUT, counter_rows, list(counter_rows[0]))
    write_tsv(UNRESOLVED_OUT, unresolved, list(unresolved[0]))

    outputs = (DICT_OUT, EVENT_OUT, STATEMENT_OUT, RECORD_OUT, COMPONENT_OUT, PARADIGM_OUT, BRANCH_OUT, COUNTER_OUT, UNRESOLVED_OUT)
    changed_cards = [row for row in revised_dictionary if row["application_revision_family"] != "UNCHANGED"]
    changed_events = [row for row in revised_events if row["application_revision_family"] != "UNCHANGED"]
    changed_statements = [row for row in statements if int(row["application_revised_event_count"]) > 0]
    summary: dict[str, object] = {
        "schema": "SIDEQUEST_SELECTED_APPLICATION_COMPLETION_SUMMARY_V1",
        "status": "PASS",
        "cards": len(revised_dictionary),
        "events": len(revised_events),
        "statements": len(statements),
        "records": len(records),
        "changed_cards": len(changed_cards),
        "changed_events": len(changed_events),
        "changed_statements": len(changed_statements),
        "components": len(components),
        "paradigm_rows": len(paradigm_rows),
        "application_branches": len(branch_rows),
        "counterexamples": len(counter_rows),
        "remaining_unresolved_rows": len(unresolved),
        "inputs": {str(path.relative_to(ROOT)): sha256(path) for path in (DICT_IN, EVENT_IN, COMPONENT_IN, UNRESOLVED_IN)},
        "outputs": {str(path.relative_to(ROOT)): sha256(path) for path in outputs},
    }
    SUMMARY_OUT.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary


if __name__ == "__main__":
    print(json.dumps(build(), ensure_ascii=False, indent=2, sort_keys=True))
