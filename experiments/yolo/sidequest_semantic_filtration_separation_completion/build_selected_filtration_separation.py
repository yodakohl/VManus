#!/usr/bin/env python3
"""Build the selected creative filtration/separation workshop edition."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import OrderedDict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = ROOT / "experiments/yolo/sidequest_semantic_state_endpoint_completion"

DICT_IN = SOURCE / "SELECTED_173_STATE_ENDPOINT_DICTIONARY.tsv"
EVENT_IN = SOURCE / "SELECTED_381_STATE_ENDPOINT_INTERLINEAR.tsv"
COMPONENT_IN = SOURCE / "SELECTED_STATE_ENDPOINT_COMPONENTS.tsv"
UNRESOLVED_IN = SOURCE / "REMAINING_UNRESOLVED_AFTER_STATE_ENDPOINT.tsv"

DICT_OUT = HERE / "SELECTED_173_FILTRATION_DICTIONARY.tsv"
EVENT_OUT = HERE / "SELECTED_381_FILTRATION_INTERLINEAR.tsv"
STATEMENT_OUT = HERE / "SELECTED_116_FILTRATION_SENTENCES.tsv"
RECORD_OUT = HERE / "SELECTED_11_FILTRATION_RECORDS.md"
COMPONENT_OUT = HERE / "SELECTED_FILTRATION_COMPONENTS.tsv"
PARADIGM_OUT = HERE / "SELECTED_FILTRATION_PARADIGM.tsv"
CHAIN_OUT = HERE / "SELECTED_PROCESS_CHAINS.tsv"
COUNTER_OUT = HERE / "FILTRATION_COUNTEREXAMPLES.tsv"
UNRESOLVED_OUT = HERE / "REMAINING_UNRESOLVED_AFTER_FILTRATION.tsv"
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
        "reading_type": "SELECTED_FILTRATION__" + family,
        "family": family,
        "strength": strength,
        "slots": slots,
        "note": note,
    }


# The selected model is deliberately mixed.  A few bounded card families have
# reusable components; rarer concrete operations remain learned whole cards.
# Exact card identity always outranks a similar visible substring.
OVERRIDES = {
    # Bounded passage/straining family.
    "2cc8bb3c2af19607888f": ov(
        "CKH_PASSAGE+Y_CURRENT_ITEM",
        "CKH=Durchlauf; Y=aktueller Posten",
        "durch den Durchlauf führen",
        "CKH_PASSAGE",
        "SELECTED_RECURRENT",
        "FLOW_TRANSFER",
        "Four events retain the same passage value; no drawn arrow or filter cloth is claimed.",
    ),
    "d68bc8de3bcee09db23c": ov(
        "CKHE_STRAIN+DY_CLOSE",
        "CKHE=seihen; Endkarte=Schluss",
        "seihen; Schluss",
        "CKHE_STRAIN",
        "SELECTED_RECURRENT",
        "FLOW_TRANSFER+CLOSE",
        "Three complete cells use the learned straining close.",
    ),
    "c1db6b0a28d5cbb5d3d2": ov(
        "LCHE_LOCAL_HULL+CKHE_STRAIN+DY_CLOSE",
        "CKHE=seihen; lokale LCHE-Hülle; Endkarte=Schluss",
        "klar seihen; Schluss",
        "CKHE_STRAIN",
        "SELECTED_SINGLETON_EXTENSION",
        "FLOW_TRANSFER+CLOSE",
        "The local hull supplies the clear-outlet execution; CKHE retains straining.",
    ),

    # Wash/rinse family and a learned rinse-medium card.
    "be0974b366c981dc1eef": ov(
        "LSH_WASH",
        "LSH=waschen oder spülen",
        "Waschgang",
        "LSH_WASH",
        "SELECTED_OPEN_BASE",
        "OPERATION",
        "Open member of the bounded LSH wash pair.",
    ),
    "2e7e89e0bd12b999c280": ov(
        "LSH_WASH+DY_CLOSE",
        "LSH=waschen oder spülen; Endkarte=Schluss",
        "waschen; Schluss",
        "LSH_WASH",
        "SELECTED_RECURRENT_CLOSE",
        "FLOW_TRANSFER+CLOSE",
        "Two complete cells close the bounded LSH wash pair.",
    ),
    "d4a31dbcf1ed6d9e5aa9": ov(
        "TSHEY_RINSE_LIQUID_WHOLE_CARD",
        "TSHEY=Spülflüssigkeit",
        "Spülflüssigkeit",
        "RINSE_NOMENCLATOR",
        "SELECTED_SINGLETON_WHOLE_CARD",
        "PREPARATION",
        "It precedes a sustained soak; TSHOL remains an unrelated plant whole card.",
    ),

    # Result, collection and storage.
    "b5df9126607030b95175": ov(
        "SHEY_CLEAR_EXTRACT_WHOLE_CARD",
        "CHEEY|SHEY=Klarauszug",
        "Klarauszug",
        "CLEAR_EXTRACT",
        "SELECTED_RECURRENT_WHOLE_CARD",
        "PREPARATION",
        "The exact renderer family follows straining or liquid withdrawal; it is not EY=water.",
    ),
    "42cdc187d5b9ffc60063": ov(
        "SOLK_COLLECTION+GRADE_1+Y_CURRENT_ITEM",
        "SOLK=Auffangstelle; E=kurz; Y=aktueller Posten",
        "kurz auffangen",
        "SOLK_COLLECTION",
        "SELECTED_LOCAL_GRADED_FAMILY",
        "TARGET+STATE_GRADE",
        "Brief collection at the local owner-bound receiving station.",
    ),
    "1bfd786e6b8b63734a59": ov(
        "SOLK_COLLECTION+GRADE_2+Y_CURRENT_ITEM",
        "SOLK=Auffangstelle; EE=länger; Y=aktueller Posten",
        "länger auffangen",
        "SOLK_COLLECTION",
        "SELECTED_LOCAL_GRADED_FAMILY",
        "TARGET+STATE_GRADE",
        "Sustained collection at the local owner-bound receiving station.",
    ),
    "3b70942557b3a40e8030": ov(
        "OLK_SOLK_COLLECTION+GRADE_2+DY_CLOSE",
        "OLK~SOLK=Auffangstelle; EE=länger; Endkarte=Schluss",
        "länger auffangen; Schluss",
        "SOLK_COLLECTION",
        "SELECTED_LOCAL_GRADED_FAMILY",
        "TARGET+STATE_GRADE+CLOSE",
        "Three complete cells close sustained collection at the local station.",
    ),
    "62ff059766b21c7de083": ov(
        "OTYTCHOL_COLLECT_WHOLE_CARD",
        "OTYTCHOL=auffangen",
        "auffangen",
        "COLLECT_STORE_NOMENCLATOR",
        "SELECTED_SINGLETON_WHOLE_CARD",
        "FLOW_TRANSFER",
        "First extract is the local H1 expansion; the card default is the shorter operation.",
    ),
    "e026af581c99322fbd46": ov(
        "TALAM_STORE_WHOLE_CARD",
        "TALAM=verwahren",
        "verwahren",
        "COLLECT_STORE_NOMENCLATOR",
        "SELECTED_SINGLETON_WHOLE_CARD",
        "PREPARATION",
        "Clear extract is the local H4 object; the card default is the shorter operation.",
    ),

    # Learned cloth/tool/action nomenclator.  These are not forced into one
    # visible morpheme; their distinct statement positions motivate distinct
    # short values.
    "53cd0637c6820ba5e91f": ov(
        "DAIN_FILTER_CLOTH_WHOLE_CARD",
        "DAIN=Tuch",
        "Tuch",
        "CLOTH_NOMENCLATOR",
        "SELECTED_RECURRENT_WHOLE_CARD",
        "OPERATION",
        "Two tool-slot occurrences; DAIN is not decomposed as AIIN=measure.",
    ),
    "2d2e37ccb2dacc53ee5a": ov(
        "SOLKAIIN_STRAINING_CLOTH_WHOLE_CARD",
        "SOLKAIIN=Seihtuch",
        "Seihtuch",
        "CLOTH_NOMENCLATOR",
        "SELECTED_SINGLETON_WHOLE_CARD",
        "OPERATION",
        "A tool card immediately before the CKH passage; not SOLK+AIIN composition.",
    ),
    "af816c04e65874a0f2fa": ov(
        "QOCTHOLY_PRESS_WHOLE_CARD",
        "QOCTHOLY=abpressen",
        "abpressen",
        "SEPARATION_NOMENCLATOR",
        "SELECTED_SINGLETON_WHOLE_CARD",
        "OPERATION",
        "The operation follows the learned crushed-herb card in H2.",
    ),
    "75a523fcf039b006f97b": ov(
        "KCHAL_STRAIN_WHOLE_CARD",
        "KCHAL=abseihen",
        "abseihen",
        "SEPARATION_NOMENCLATOR",
        "SELECTED_SINGLETON_WHOLE_CARD",
        "OPERATION",
        "The operation follows addition of extract liquid in H5.",
    ),
    "bdad9f9ea8b80f141496": ov(
        "CFHY_WRING_WHOLE_CARD",
        "CFHY=auswringen",
        "auswringen",
        "SEPARATION_NOMENCLATOR",
        "SELECTED_SINGLETON_WHOLE_CARD",
        "OPERATION",
        "First coarse separation in the complete H3 process sequence.",
    ),
    "deb377381ceaf55ea310": ov(
        "CPHY_RESTRAIN_WHOLE_CARD",
        "CPHY=nachseihen",
        "nachseihen",
        "SEPARATION_NOMENCLATOR",
        "SELECTED_SINGLETON_WHOLE_CARD",
        "OPERATION",
        "Second fine separation after the prescribed standing time in H3.",
    ),
}


PARADIGM_ORDER = [
    ("01_WASH", "be0974b366c981dc1eef", "LSH", "OPEN_WASH"),
    ("01_WASH", "2e7e89e0bd12b999c280", "LSH+DY", "CLOSED_WASH"),
    ("01_WASH", "d4a31dbcf1ed6d9e5aa9", "TSHEY", "RINSE_LIQUID"),
    ("03_PASS", "2cc8bb3c2af19607888f", "CKH+Y", "PASSAGE"),
    ("03_PASS", "d68bc8de3bcee09db23c", "CKHE+DY", "CLOSED_STRAIN"),
    ("03_PASS", "c1db6b0a28d5cbb5d3d2", "LCHE+CKHE+DY", "LOCAL_CLOSED_STRAIN"),
    ("03_CLOTH", "53cd0637c6820ba5e91f", "DAIN", "CLOTH_TOOL"),
    ("03_CLOTH", "2d2e37ccb2dacc53ee5a", "SOLKAIIN", "STRAINING_CLOTH_TOOL"),
    ("03_SEPARATE", "af816c04e65874a0f2fa", "QOCTHOLY", "PRESS"),
    ("03_SEPARATE", "75a523fcf039b006f97b", "KCHAL", "STRAIN"),
    ("03_SEPARATE", "bdad9f9ea8b80f141496", "CFHY", "WRING"),
    ("03_SEPARATE", "deb377381ceaf55ea310", "CPHY", "RESTRAIN"),
    ("04_RESULT", "b5df9126607030b95175", "SHEY", "CLEAR_EXTRACT"),
    ("05_COLLECT", "42cdc187d5b9ffc60063", "SOLK+E+Y", "BRIEF_COLLECTION"),
    ("05_COLLECT", "1bfd786e6b8b63734a59", "SOLK+EE+Y", "SUSTAINED_COLLECTION"),
    ("05_COLLECT", "3b70942557b3a40e8030", "SOLK+EE+DY", "CLOSED_COLLECTION"),
    ("05_COLLECT", "62ff059766b21c7de083", "OTYTCHOL", "COLLECT"),
    ("05_STORE", "e026af581c99322fbd46", "TALAM", "STORE"),
]


CHAIN_STATEMENTS = OrderedDict(
    [
        ("H1-S001", ("HERBAL_INFLOW_COLLECTION", "Flüssigkeitszulauf → auffangen")),
        ("H2-S001", ("HERBAL_PRESSING", "zerkleinern → abpressen")),
        ("H3-S001", ("COMPLETE_HERBAL_SEPARATION", "auswringen → stehen lassen → nachseihen → Klarauszug → abkühlen")),
        ("H4-S002", ("HERBAL_STORAGE", "Maß → durcharbeiten → verwahren")),
        ("H5-S004", ("HERBAL_STRAINING", "Auszugsflüssigkeit → abseihen")),
        ("B1-S012", ("WASH_CYCLE", "Waschgang → kurz anlegen → waschen → Schluss")),
        ("B1-S020", ("WARM_STRAIN", "mild erwärmen → seihen → Schluss")),
        ("B2-S004", ("OUTLET_STRAIN", "Zielstelle → Auslass → hinausführen → seihen → Schluss")),
        ("B2-S005", ("CLOTH_PASSAGE", "Seihtuch → Durchlauf → Maß → warm halten → abziehen")),
        ("B2-S010", ("CLEAR_RESULT", "länger einwirken → einsetzen → Klarauszug")),
        ("B2-S012", ("CLEAR_APPLICATION", "flüssigen Anteil abziehen → Klarauszug → Anwendung")),
        ("B2-S015", ("RINSE_SOAK", "Spülflüssigkeit → länger einweichen → Schluss")),
        ("B3-S026", ("SETTLE_CLEAR_COLLECT", "absetzen → bis klar → länger auffangen")),
        ("B4-S005", ("CLOTH_SOAK", "Tuch → durcharbeiten → einweichen")),
        ("B4-S006", ("STRAIN_CLOSE", "seihen → Schluss")),
        ("B4-S007", ("STRAIN_CLOSE_REPEAT", "seihen → Schluss")),
        ("B4-S015", ("CLEAR_COLLECT_DRAIN", "Klarauszug → Dauer → kurz auffangen → hinausführen")),
        ("B6-S001", ("COLLECT_THEN_CLOTH", "länger auffangen → weiter → Tuch → Zielstelle")),
    ]
)


COUNTEREXAMPLES = [
    ("CKH_NOT_GLOBAL", "c1913ec4ff84148da6d3|ecce30bc8dcc400bf2c8|f329f2051370174e9a38|95987d6f198d6d9e5aa", "sheckhy|qockhey|lcheckhy|cheeckhody", "learned exact-card values", "Only CKHY and CKHEDY members receive the selected passage/strain contribution."),
    ("CHK_ORDER_CONTROL", "d904bf7b044dd3922781|2c1a5fd92b9e3c762242|f0db6d30cd34f4cb2a4d|a84fbe3ad380df345b97", "cheky|cheeky|chkeey|chkeedy", "wärmen", "CHK is the bounded warmth family; reversing K/H is not harmless."),
    ("SHEY_EXACT_CARD_ONLY", "b5df9126607030b95175", "cheey|shey", "Klarauszug", "The whole-card value does not license EY=water or SH=clear globally."),
    ("SHEEY_DIFFERENT_CARD", "92e43836d82f98bf02d3", "sheey", "erste Öffnung", "A similar surface belongs to a different exact card."),
    ("LSH_NOT_SHED", "2e7e89e0bd12b999c280|bc4f1f5c006c74a4d26d", "lshedy versus cheedy|shedy|tedy", "waschen versus ruhen", "The bounded LSH wash card and SHED rest card remain distinct."),
    ("TSH_NOT_GLOBAL", "d4a31dbcf1ed6d9e5aa9|953ad19b79517fc8a211", "tshey versus tshol", "Spülflüssigkeit versus Blütenkraut", "TSHEY is a learned whole card, not a productive TSH stem."),
    ("DAIN_NOT_AIIN", "53cd0637c6820ba5e91f|48fdfea71d4a6264a9b8", "dain versus aiin", "Tuch versus Maß", "The exact DAIN tool card overrides visible overlap with AIIN."),
    ("CLOTH_DECK_NO_SHARED_ROOT", "53cd0637c6820ba5e91f|2d2e37ccb2dacc53ee5a|af816c04e65874a0f2fa|75a523fcf039b006f97b", "dain|solkaiin|qoctholy|kchal", "Tuch|Seihtuch|abpressen|abseihen", "These learned specialist cards form a functional deck, not a fabricated visible morpheme."),
    ("CFHY_CPHY_NO_FREE_F_P", "bdad9f9ea8b80f141496|deb377381ceaf55ea310", "cfhy|cphy", "auswringen|nachseihen", "The ordered H3 operations do not license free F=press or P=repeat."),
]


def build_components() -> list[dict[str, str]]:
    rows = read_tsv(COMPONENT_IN)
    for row in rows:
        if row["component_id"] == "OLK_SOLK_COLLECTION_STATION":
            row.update(
                working_meaning_de="Auffangstelle; lokal kurz oder länger auffangen",
                status="SELECTED_LOCAL_PROCESS_FAMILY",
                licensed_environment="solkey; solkeey; olkeedy|solkeedy",
                evidence_summary="brief/sustained open and sustained closed collection cards",
                important_limit="owner-local; no drawn source, sink or flow direction",
            )
    rows.extend(
        [
            {"component_id": "CKH_PASSAGE", "visible_realizations": "chckhy|shckhy in one exact card", "working_meaning_de": "Durchlauf", "status": "SELECTED_BOUNDED_PROCESS_STEM", "licensed_environment": "2cc8bb3c2af19607888f only", "evidence_summary": "four events across B1/B2; one follows the Seihtuch card", "important_limit": "not every visible CKH substring and no drawn arrow"},
            {"component_id": "CKHE_STRAIN", "visible_realizations": "shckhedy; lcheckhedy", "working_meaning_de": "seihen", "status": "SELECTED_BOUNDED_PROCESS_STEM", "licensed_environment": "two exact terminal cards", "evidence_summary": "four statement-final events; H3 supplies the independent coarse/fine process analogy", "important_limit": "CKHE is learned in these cards, not automatically CKH plus free E"},
            {"component_id": "LSH_WASH", "visible_realizations": "lsho; lshedy", "working_meaning_de": "waschen oder spülen", "status": "SELECTED_BOUNDED_PROCESS_STEM", "licensed_environment": "two exact LSH cards", "evidence_summary": "one open wash card and two terminal wash cards in B1", "important_limit": "SHED rest and TSHOL plant remain unrelated exact cards"},
            {"component_id": "SHEY_CLEAR_EXTRACT", "visible_realizations": "cheey|shey exact renderer family", "working_meaning_de": "Klarauszug", "status": "SELECTED_RECURRENT_WHOLE_CARD", "licensed_environment": "b5df9126607030b95175 only", "evidence_summary": "four events; one immediately follows the second straining in H3", "important_limit": "does not mean that EY is water or SH is clear elsewhere"},
            {"component_id": "FILTER_CLOTH_DECK", "visible_realizations": "dain; solkaiin", "working_meaning_de": "Tuch; Seihtuch", "status": "SELECTED_NOMENCLATOR_PAIR", "licensed_environment": "two exact tool cards", "evidence_summary": "three tool-slot events before process/route cards", "important_limit": "no shared visible root is asserted"},
            {"component_id": "SEPARATION_ACTION_DECK", "visible_realizations": "qoctholy; kchal; cfhy; cphy", "working_meaning_de": "abpressen; abseihen; auswringen; nachseihen", "status": "SELECTED_NOMENCLATOR_DECK", "licensed_environment": "four exact action cards", "evidence_summary": "H2/H3/H5 statement order separates coarse, fine and repeated operations", "important_limit": "short whole-card values, not a new F/P/HY morphology"},
        ]
    )
    if len({row["component_id"] for row in rows}) != len(rows):
        raise AssertionError("duplicate component IDs")
    return rows


def build_unresolved() -> list[dict[str, str]]:
    rows = read_tsv(UNRESOLVED_IN)
    for row in rows:
        if row["candidate_component"] == "GLOBAL_SOLK":
            row.update(
                current_best_constraint="owner-local graded Auffangstellenfamilie",
                why_not_closed="the five events remain tied to Biological station owners",
                working_default_until_better_model="short/länger auffangen only in the three selected exact cards",
                prediction_that_could_improve_it="reuse at an independent Herbal owner",
            )
        elif row["candidate_component"] == "MEMORIZED_WHOLE_CARDS":
            row.update(
                current_best_constraint="the process round shortens eight learned operation/tool/result cards but leaves the large local deck intact",
                why_not_closed="most remaining singleton cards lack a stable process substitution",
                working_default_until_better_model="retain each short whole-card value",
                prediction_that_could_improve_it="another complete local process chain should reuse one of the remaining whole cards",
            )
    rows.extend(
        [
            {"candidate_component": "CKH_SURFACE_PORTABILITY", "current_best_constraint": "CKH=Durchlauf and CKHE=seihen only in three exact cards", "why_not_closed": "similar CKH surfaces also label learned position, opening and application cards", "working_default_until_better_model": "exact-card override before visible segmentation", "prediction_that_could_improve_it": "a new exact CKH argument should preserve passage under a different owner"},
            {"candidate_component": "SHEY_PRODUCT_VS_STATE", "current_best_constraint": "the exact card is read as Klarauszug", "why_not_closed": "three Biological contexts also permit a clarity check or clear outflow", "working_default_until_better_model": "Klarauszug as the short whole-card default", "prediction_that_could_improve_it": "a statement should contrast the liquid before and after the same exact card"},
            {"candidate_component": "TSHEY_MEDIUM_VS_START", "current_best_constraint": "Spülflüssigkeit before a sustained soak", "why_not_closed": "the one event also permits begin the rinse", "working_default_until_better_model": "Spülflüssigkeit", "prediction_that_could_improve_it": "a second TSHEY occurrence should remain a medium when not field-initial"},
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
        "filtration_previous_segmentation",
        "filtration_previous_nucleus_de",
        "filtration_previous_gloss_de",
        "filtration_revision_family",
        "filtration_revision_strength",
        "filtration_revision_note",
    ]
    revised_dictionary: list[dict[str, str]] = []
    for source in dictionary:
        row = dict(source)
        selected = OVERRIDES.get(row["joint_tuple_id"])
        if selected:
            row["filtration_previous_segmentation"] = row["semantic_segmentation"]
            row["filtration_previous_nucleus_de"] = row["stable_concrete_nucleus_de"]
            row["filtration_previous_gloss_de"] = row["concrete_word_reading_de"]
            for key in ("semantic_segmentation", "stable_concrete_nucleus_de", "concrete_word_reading_de", "reading_type"):
                row[key] = selected[key]
            row["local_expansion_examples_de"] = "Filtrationsfassung: " + selected["concrete_word_reading_de"]
            row["variation_note"] += "; filtration: " + selected["note"]
            row["filtration_revision_family"] = selected["family"]
            row["filtration_revision_strength"] = selected["strength"]
            row["filtration_revision_note"] = selected["note"]
        else:
            row.update(
                filtration_previous_segmentation="",
                filtration_previous_nucleus_de="",
                filtration_previous_gloss_de="",
                filtration_revision_family="UNCHANGED",
                filtration_revision_strength="UNCHANGED",
                filtration_revision_note="NOT_APPLICABLE",
            )
        revised_dictionary.append(row)
    by_id = {row["joint_tuple_id"]: row for row in revised_dictionary}

    event_fields = list(events[0]) + [
        "filtration_previous_segmentation",
        "filtration_previous_nucleus_de",
        "filtration_previous_gloss_de",
        "filtration_previous_context_de",
        "filtration_revision_family",
        "filtration_revision_strength",
    ]
    revised_events: list[dict[str, str]] = []
    for source in events:
        row = dict(source)
        selected = OVERRIDES.get(row["joint_tuple_id"])
        if selected:
            row["filtration_previous_segmentation"] = row["semantic_segmentation"]
            row["filtration_previous_nucleus_de"] = row["stable_concrete_nucleus_de"]
            row["filtration_previous_gloss_de"] = row["concrete_word_reading_de"]
            row["filtration_previous_context_de"] = row["contextual_event_reading_de"]
            card = by_id[row["joint_tuple_id"]]
            row["semantic_segmentation"] = card["semantic_segmentation"]
            row["stable_concrete_nucleus_de"] = card["stable_concrete_nucleus_de"]
            row["concrete_word_reading_de"] = card["concrete_word_reading_de"]
            row["contextual_event_reading_de"] = sentence_case(card["concrete_word_reading_de"])
            row["workshop_slots"] = selected["slots"]
            row["filtration_revision_family"] = selected["family"]
            row["filtration_revision_strength"] = selected["strength"]
        else:
            row.update(
                filtration_previous_segmentation="",
                filtration_previous_nucleus_de="",
                filtration_previous_gloss_de="",
                filtration_previous_context_de="",
                filtration_revision_family="UNCHANGED",
                filtration_revision_strength="UNCHANGED",
            )
        revised_events.append(row)

    grouped: dict[str, list[dict[str, str]]] = OrderedDict()
    for row in revised_events:
        grouped.setdefault(row["statement_id"], []).append(row)
    statement_fields = [
        "statement_id",
        "record_unit_id",
        "page",
        "loci",
        "field_ids",
        "event_ids",
        "event_count",
        "filtration_revised_event_count",
        "surface_sequence",
        "card_sequence_de",
        "event_slot_trace",
        "canonical_slots_present",
        "workshop_sentence_de",
        "physical_line_note",
    ]
    statements: list[dict[str, str]] = []
    slot_order = ["OWNER_ITEM", "SOURCE", "QUANTITY", "PREPARATION", "OPERATION", "FLOW_TRANSFER", "TARGET", "STATE_GRADE", "CLOSE"]
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
                "filtration_revised_event_count": str(sum(row["filtration_revision_family"] != "UNCHANGED" for row in rows)),
                "surface_sequence": " · ".join(row["surface_display"] for row in rows),
                "card_sequence_de": " · ".join(row["concrete_word_reading_de"] for row in rows),
                "event_slot_trace": " | ".join(f"{row['event_id']}[{row['workshop_slots']}]" for row in rows),
                "canonical_slots_present": ">".join(slot for slot in slot_order if slot in present),
                "workshop_sentence_de": sentence_case("; ".join(row["concrete_word_reading_de"] for row in rows)),
                "physical_line_note": rows[-1]["statement_continuation"],
            }
        )
    statements_by_id = {row["statement_id"]: row for row in statements}

    records: dict[str, list[dict[str, str]]] = OrderedDict()
    for row in statements:
        records.setdefault(row["record_unit_id"], []).append(row)
    markdown = [
        "# Elf vollständige Records nach der Filtrations-/Trennungsrunde",
        "",
        "Die Kartenlesungen sind eine kreative Werkstattrekonstruktion. Zeilen sind",
        "kein Satzschluss; die sichtbare Ereignisreihenfolge bleibt vollständig.",
        "",
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
            "chain_stage": stage,
            "joint_tuple_id": ident,
            "surface_family": by_id[ident]["surface_family"],
            "formula": formula,
            "selected_reading_de": by_id[ident]["concrete_word_reading_de"],
            "events": str(event_counts[ident]),
            "process_role": role,
            "selection_strength": OVERRIDES[ident]["strength"],
            "important_limit": OVERRIDES[ident]["note"],
        }
        for stage, ident, formula, role in PARADIGM_ORDER
    ]
    chain_rows = []
    for statement_id, (chain_name, stages) in CHAIN_STATEMENTS.items():
        statement = statements_by_id[statement_id]
        chain_rows.append(
            {
                "chain_name": chain_name,
                "statement_id": statement_id,
                "record_unit_id": statement["record_unit_id"],
                "page": statement["page"],
                "loci": statement["loci"],
                "surface_sequence": statement["surface_sequence"],
                "selected_card_sequence_de": statement["card_sequence_de"],
                "process_stages_de": stages,
                "complete_workshop_reading_de": statement["workshop_sentence_de"],
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
    write_tsv(CHAIN_OUT, chain_rows, list(chain_rows[0]))
    write_tsv(COUNTER_OUT, counter_rows, list(counter_rows[0]))
    write_tsv(UNRESOLVED_OUT, unresolved, list(unresolved[0]))

    outputs = (DICT_OUT, EVENT_OUT, STATEMENT_OUT, RECORD_OUT, COMPONENT_OUT, PARADIGM_OUT, CHAIN_OUT, COUNTER_OUT, UNRESOLVED_OUT)
    changed_cards = [row for row in revised_dictionary if row["filtration_revision_family"] != "UNCHANGED"]
    changed_events = [row for row in revised_events if row["filtration_revision_family"] != "UNCHANGED"]
    changed_statements = [row for row in statements if int(row["filtration_revised_event_count"]) > 0]
    summary: dict[str, object] = {
        "schema": "SIDEQUEST_SELECTED_FILTRATION_SEPARATION_SUMMARY_V1",
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
        "process_chains": len(chain_rows),
        "counterexamples": len(counter_rows),
        "remaining_unresolved_rows": len(unresolved),
        "inputs": {str(path.relative_to(ROOT)): sha256(path) for path in (DICT_IN, EVENT_IN, COMPONENT_IN, UNRESOLVED_IN)},
        "outputs": {str(path.relative_to(ROOT)): sha256(path) for path in outputs},
    }
    SUMMARY_OUT.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary


if __name__ == "__main__":
    print(json.dumps(build(), ensure_ascii=False, indent=2, sort_keys=True))
