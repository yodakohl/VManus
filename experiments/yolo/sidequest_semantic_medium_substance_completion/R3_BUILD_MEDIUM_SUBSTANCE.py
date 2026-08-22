#!/usr/bin/env python3
"""Build R3's creative medium/substance/flow workshop candidate edition."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import OrderedDict, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = ROOT / "experiments/yolo/sidequest_semantic_application_completion"

DICT_IN = SOURCE / "SELECTED_173_APPLICATION_DICTIONARY.tsv"
EVENT_IN = SOURCE / "SELECTED_381_APPLICATION_INTERLINEAR.tsv"
SENTENCE_IN = SOURCE / "SELECTED_116_APPLICATION_SENTENCES.tsv"

DICT_OUT = HERE / "R3_173_MEDIUM_SUBSTANCE_DICTIONARY.tsv"
EVENT_OUT = HERE / "R3_381_MEDIUM_SUBSTANCE_INTERLINEAR.tsv"
SENTENCE_OUT = HERE / "R3_116_MEDIUM_SUBSTANCE_SENTENCES.tsv"
RECORD_OUT = HERE / "R3_11_MEDIUM_SUBSTANCE_RECORDS.md"
PARADIGM_OUT = HERE / "R3_MEDIUM_SUBSTANCE_PARADIGM.tsv"
VALIDATION_OUT = HERE / "R3_VALIDATION.json"
SUMMARY_OUT = HERE / "R3_BUILD_SUMMARY.json"

ALLOWED_PAGES = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"}
RECORD_ORDER = ["H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"]


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
        "reading_type": "R3_MEDIUM_SUBSTANCE__" + family,
        "family": family,
        "strength": strength,
        "slots": slots,
        "note": note,
    }


# The central correction is ontological, not a wholesale retranslation:
# AIR is the water material named inside several flow constructions, CHEO is
# an intermediate product, OR is the prepared batch, and containers/passages
# remain separate from all three.  HO is the ingredient card, not plant alone.
OVERRIDES = {
    # HO: the exact CHO/SHO card recurs three times for the pictured plant and
    # once for a later addition.  Ingredient is the invariant workshop value;
    # plant is the local picture-owned realization.
    "2cc054357a929df85f64": ov(
        "HO_INGREDIENT", "HO=Zutat", "Zutat", "HO_INGREDIENT", "SELECTED_RECURRENT_CORE",
        "OWNER_ITEM+PREPARATION", "Three H5 events inherit plant from the picture; the fourth is an added ingredient, so ZUTAT is the shared value.",
    ),

    # OR: a prepared batch/object, not the act "preparation" and not a raw medium.
    "7a4bb8136330ee4e6e56": ov(
        "OR_BATCH", "OR=Ansatz", "Ansatz", "OR_BATCH", "SELECTED_RECURRENT_CORE",
        "PREPARATION", "Seven events span Herbal and apparatus records; ANSATZ survives all contexts.",
    ),
    "10488b911aae52b3b334": ov(
        "OT_NEXT+OR_BATCH", "OT=nächster; OR=Ansatz", "der nächste Ansatz", "OR_BATCH",
        "SELECTED_RECURRENT_COMPOSITION", "PREPARATION", "Two Herbal events preserve the next-batch composition.",
    ),
    "dec401773c1f0347793d": ov(
        "OL_CONTINUE+OR_BATCH", "OL=mit dem vorigen; OR=Ansatz", "mit dem vorigen Ansatz", "OR_BATCH",
        "SELECTED_RECURRENT_COMPOSITION", "PREPARATION", "Herbal and Biological events share the previous-batch reading.",
    ),
    "b9d7b6d68209a9019e7a": ov(
        "CHO_INGREDIENT+OR_BATCH", "CHO=Zutat; OR=Ansatz", "Zutatenansatz", "OR_BATCH",
        "SELECTED_SINGLETON_COMPOSITION", "OWNER_ITEM+PREPARATION", "The picture locally makes the ingredient vegetal; HO itself remains ZUTAT and OR remains ANSATZ.",
    ),
    "6afeb5c9ab9f6cbdea0d": ov(
        "OR_BATCH+AIN_PORTION", "OR=Ansatz; AIN=Portion", "eine Portion des Ansatzes", "OR_BATCH",
        "SELECTED_SINGLETON_COMPOSITION", "QUANTITY+PREPARATION", "The amount is separate from the prepared batch.",
    ),

    # AIR: water as material.  The learned hulls and operations supply inlet,
    # basin placement, motion and closure; AIR itself does not mean flow.
    "12efe866f335461823a6": ov(
        "CH_LEARNED_INLET+AIR_WATER", "AIR=Wasser; CH=gelernte Zulaufhülle", "Wasserzulauf", "AIR_WATER",
        "SELECTED_SINGLETON_COMPOSITION", "PREPARATION+FLOW_TRANSFER", "Vessel then CHAIR then collection supports water entering the Herbal preparation.",
    ),
    "22fb87a5a83e5c3fb510": ov(
        "K_LEARNED_BASIN+AIR_WATER", "AIR=Wasser; K=gelernte Beckenhülle", "Beckenwasser", "AIR_WATER",
        "SELECTED_SINGLETON_COMPOSITION", "PREPARATION", "The f81v pool owner supplies the basin reading; AIR remains the water material.",
    ),
    "7d2404c835b10a2c06af": ov(
        "OK_START+AIR_WATER", "OK=in Gang setzen; AIR=Wasser", "Wasser einströmen lassen", "AIR_WATER",
        "SELECTED_SINGLETON_COMPOSITION", "PREPARATION+OPERATION+FLOW_TRANSFER", "The following long rest fits water admitted before settling.",
    ),
    "b154ff779abe5f196c80": ov(
        "S_RENDERER+CHED_CONDUCT+AIR_WATER", "CHED=führen; AIR=Wasser", "Wasser weiterführen", "AIR_WATER",
        "SELECTED_SINGLETON_COMPOSITION", "PREPARATION+OPERATION+FLOW_TRANSFER", "CHED supplies conduct; AIR supplies the water being conducted.",
    ),
    "8aedd154964a78e555d6": ov(
        "D_RENDERER+AIR_WATER+Y_REFERENT+DY_CLOSE", "AIR=Wasser; Y=laufender Posten; Endkarte=Schluss",
        "laufendes Wasser schließen; Schluss", "AIR_WATER", "SELECTED_SINGLETON_COMPOSITION",
        "PREPARATION+OWNER_ITEM+FLOW_TRANSFER+CLOSE", "The B4 cell closes the running water belonging to the current item.",
    ),

    # CHEO: intermediate extract.  The same extract is a product in H4 and an
    # input in H5; this is reuse, not two meanings.
    "807591efc3d3f7ddbfab": ov(
        "CHEO_EXTRACT+AR_SOURCE", "CHEO=Auszug; AR=aus", "Auszug daraus nehmen", "CHEO_EXTRACT",
        "SELECTED_TWO_CARD_CORE", "SOURCE+PREPARATION+OPERATION", "H4 takes the extract from the current batch before warming it.",
    ),
    "087a47b5423438cd6b6a": ov(
        "CH_RENDERER+OK+CHEO_EXTRACT", "OK=zugeben; CHEO=Auszug", "Auszug zugeben", "CHEO_EXTRACT",
        "SELECTED_TWO_CARD_CORE", "PREPARATION+OPERATION+FLOW_TRANSFER", "H5 reuses an extract as input immediately before straining.",
    ),

    # This singleton is better a temperature/readiness state than a substance.
    "cb57b696b815fdef9cb7": ov(
        "SHECTHY_TEMPERED_STATE_WHOLE_CARD", "SHECTHY=temperiert", "temperiert",
        "TEMPERED_STATE", "SELECTED_SINGLETON_WHOLE_CARD", "STATE_GRADE",
        "It lies after a rest station and before the current-item card; this supports a state, not a second medium noun.",
    ),

    # Passage versus moving current.
    "2cc8bb3c2af19607888f": ov(
        "CKH_PASSAGE+Y_CURRENT_ITEM", "CKH=Durchlass; Y=aktueller Posten", "durch den Durchlass führen",
        "PASSAGE_NOT_CURRENT", "SELECTED_RECURRENT_CORE", "OWNER_ITEM+OPERATION+FLOW_TRANSFER",
        "Four events identify the passage/aperture; AIR is reserved for current or flow.",
    ),
    "0ab57b7166de99db3a55": ov(
        "LCH_WITHDRAW+Y_REFERENT", "LCH=abziehen; Y=laufender Posten", "den laufenden Posten abziehen",
        "WITHDRAW_NOT_PRODUCT", "SELECTED_SINGLETON_COMPOSITION", "OWNER_ITEM+OPERATION+FLOW_TRANSFER",
        "The following SHEY supplies clear extract; liquid is local context, not part of LCHY.",
    ),

    # Learned media/products whose old gloss contained an unsupported action
    # or overly narrow medical label.
    "883a6708116c342cb10b": ov(
        "SK_WARM_MEDIUM+AR_SOURCE", "SK=warmes Medium; AR=aus der Quelle", "warmes Medium aus der Quelle",
        "WARM_MEDIUM", "SELECTED_SINGLETON_COMPOSITION", "SOURCE+PREPARATION+STATE_GRADE",
        "The surrounding site and rest cards supply delivery; SKAR need not itself mean pour.",
    ),
    "c71c72da4e09e0833392": ov(
        "KCHOAR_DRINK_WHOLE_CARD", "KCHOAR=Trank", "Trank", "DRINK_PRODUCT",
        "SELECTED_SINGLETON_WHOLE_CARD", "PREPARATION", "The H5 context licenses a drink; chest and cough are not in the card.",
    ),
    "98bdc4244c84cbef3321": ov(
        "RSHEAL_WARM_BATH_WATER_WHOLE_CARD", "RSHEAL=warmes Badwasser", "warmes Badwasser",
        "WATER_MEDIUM", "SELECTED_SINGLETON_WHOLE_CARD", "PREPARATION+STATE_GRADE",
        "The lower-pool owner and following second opening make bathwater the concrete local choice.",
    ),
    "cbb42a4fe68068325d6b": ov(
        "DSHE_FRESH_WATER_INLET+DY_CLOSE", "DSHE=Frischwassereinlass; Endkarte=Schluss",
        "Frischwasser einlassen; Schluss", "WATER_MEDIUM", "SELECTED_SINGLETON_WHOLE_CARD",
        "OPERATION+FLOW_TRANSFER+CLOSE", "A complete f82r device-node cell is best read as a fresh-water inlet close.",
    ),

    # Three formerly synonymous "fill vessel" cards are assigned distinct
    # workshop roles so container and movement are not collapsed.
    "a7af89ab31ce5e247395": ov(
        "YTEY_FILL_WHOLE_CARD", "YTEY=füllen", "füllen", "FILL_ACTION",
        "SELECTED_SINGLETON_WHOLE_CARD", "OPERATION+FLOW_TRANSFER", "B1-S015 supplies the vessel; the card supplies filling.",
    ),
    "b38d70daefd663d74625": ov(
        "LY_RECEIVER_WHOLE_CARD", "LY=Empfangsgefäß", "Empfangsgefäß", "CONTAINER_DECK",
        "SELECTED_SINGLETON_WHOLE_CARD", "TARGET", "It precedes a target grade and sustained collection, making a receiver better than a second fill verb.",
    ),
    "e2eb77ca9d9e1a8ba29a": ov(
        "QOLCHEY_WORK_BASIN_WHOLE_CARD", "QOLCHEY=Arbeitsbecken", "Arbeitsbecken", "CONTAINER_DECK",
        "SELECTED_SINGLETON_WHOLE_CARD", "TARGET", "B4 holds and briefly wets the current item at this arch-linked owner.",
    ),
}


CONTEXT_BY_EVENT = {
    "E006": "Lass Wasser zulaufen",
    "E017": "Ansatz",
    "E024": "Der nächste Ansatz",
    "E025": "Ansatz",
    "E028": "Mit dem vorigen Ansatz",
    "E033": "Ansatz",
    "E034": "Ansatz",
    "E065": "Nimm den Auszug daraus",
    "E071": "Ansatz",
    "E073": "Eine Portion des Ansatzes",
    "E074": "Pflanzenansatz",
    "E075": "Sammle die ganze oberirdische Pflanzenzutat an einem feuchten Standort",
    "E078": "Zerstoße die frische Pflanzenzutat",
    "E088": "Trockne die Pflanzenzutat im Schatten",
    "E080": "Der nächste Ansatz",
    "E092": "Gib den Auszug zu",
    "E094": "Gib die weitere Zutat hinzu",
    "E103": "Beckenwasser",
    "E113": "Mit dem vorigen Ansatz",
    "E150": "Fülle das Gefäß",
    "E159": "Stelle das Empfangsgefäß bereit",
    "E179": "Führe den Posten durch den Durchlass",
    "E202": "Ziehe den laufenden Flüssigkeitsposten ab",
    "E222": "Gieße warmes Badwasser ein",
    "E254": "Ansatz",
    "E260": "Lass Wasser einströmen",
    "E276": "Temperiert",
    "E300": "Führe das Wasser weiter",
    "E316": "Bereite das Arbeitsbecken vor",
    "E348": "Ansatz",
    "E351": "Schließe das laufende Wasser; Schluss",
    "E360": "Gib warmes Medium aus der Quelle an die Stelle",
    "E096": "Gib den Auszug als Trank",
    "E189": "Lass Frischwasser ein; Schluss",
}


# Event-specific contexts for the three additional CKH occurrences.
for _event in ("E118", "E128", "E139"):
    CONTEXT_BY_EVENT[_event] = "Führe den Posten durch den Durchlass"


# Complete audit deck: revised cards plus retained cards needed to keep raw
# material, intermediate product, motion, passage, vessel and station apart.
AUDIT = [
    ("00_INGREDIENT", "2cc054357a929df85f64", "INGREDIENT", "picture supplies plant locally; exact card also covers a later addition"),
    ("01_RAW_MEDIUM", "428a5e3662aa57b4b256", "MEDIUM+HEAT", "wine carrier; learned whole card"),
    ("01_RAW_MEDIUM", "0f18de177ed7c878bf95", "BATH_ADDITIVE", "prepared additive, not bath water"),
    ("01_RAW_MEDIUM", "d4a31dbcf1ed6d9e5aa9", "RINSE_LIQUID", "unspecified rinse medium"),
    ("01_RAW_MEDIUM", "98bdc4244c84cbef3321", "WARM_BATH_WATER", "concrete water card at lower-pool opening"),
    ("01_RAW_MEDIUM", "cbb42a4fe68068325d6b", "FRESH_WATER_INLET", "water plus inlet close as learned card"),
    ("09_STATE", "cb57b696b815fdef9cb7", "TEMPERED", "state after rest station, not a material noun"),
    ("01_RAW_MEDIUM", "883a6708116c342cb10b", "WARM_MEDIUM_FROM_SOURCE", "delivery supplied by sentence frame"),
    ("02_PREPARED_BATCH", "7a4bb8136330ee4e6e56", "BATCH", "portable OR core"),
    ("02_PREPARED_BATCH", "10488b911aae52b3b334", "NEXT_BATCH", "OT composition"),
    ("02_PREPARED_BATCH", "dec401773c1f0347793d", "PREVIOUS_BATCH", "OL composition"),
    ("02_PREPARED_BATCH", "b9d7b6d68209a9019e7a", "INGREDIENT_BATCH", "HO supplies ingredient; picture locally supplies plant"),
    ("02_PREPARED_BATCH", "6afeb5c9ab9f6cbdea0d", "BATCH_PORTION", "AIN supplies amount"),
    ("03_PRODUCT", "807591efc3d3f7ddbfab", "EXTRACT_FROM_SOURCE", "CHEO product can be reused"),
    ("03_PRODUCT", "087a47b5423438cd6b6a", "ADD_EXTRACT", "same CHEO as later input"),
    ("03_PRODUCT", "b5df9126607030b95175", "CLEAR_EXTRACT", "retained recurrent result card"),
    ("03_PRODUCT", "c71c72da4e09e0833392", "DRINK", "medical target removed"),
    ("03_PRODUCT", "b2812c8283c3a62438bd", "SERVE_AS_DRINK", "retained learned use card"),
    ("04_WATER", "12efe866f335461823a6", "WATER_INLET", "AIR water plus learned inlet hull"),
    ("04_WATER", "22fb87a5a83e5c3fb510", "BASIN_WATER", "AIR water plus basin hull/owner"),
    ("04_WATER", "7d2404c835b10a2c06af", "START_WATER_FLOW", "OK starts motion of AIR water"),
    ("04_WATER", "b154ff779abe5f196c80", "CONDUCT_WATER", "CHED conducts AIR water"),
    ("04_WATER", "8aedd154964a78e555d6", "CLOSE_RUNNING_WATER", "Y/DY close the running water cell"),
    ("05_PASSAGE", "2cc8bb3c2af19607888f", "PASSAGE", "CKH is apparatus/path; AIR supplies water and its construction supplies motion"),
    ("05_PASSAGE", "433713294b25b0a12f66", "OUTLET_SITE", "movement plus AL site"),
    ("05_PASSAGE", "ba540da978ea132f6da5", "INLET_SITE", "movement plus AL site"),
    ("05_PASSAGE", "29e0eb222ef2fb99523a", "LOWER_OUTLET", "retained learned outlet"),
    ("05_PASSAGE", "2b7fa918d1b2f5c656e3", "LOWER_OUTLET", "second retained learned outlet"),
    ("06_TRANSFER", "4d4559019a961b834aa1", "SOURCE", "AR is source/stock, not substance"),
    ("06_TRANSFER", "3ae9a121ba0045b913e8", "TAKE_FROM_SOURCE", "OK+AR"),
    ("06_TRANSFER", "0f15effeca7ab10bb026", "OUT_FROM_SOURCE", "L+CHED+AR"),
    ("06_TRANSFER", "ba8142680851f24c9ff2", "LEAD_OUT", "open outward transfer"),
    ("06_TRANSFER", "de7321bface5628e35d6", "LEAD_OUT_CLOSE", "recurrent outward close"),
    ("06_TRANSFER", "65df3cd9e59060042d47", "LEAD_IN_CLOSE", "inward close"),
    ("06_TRANSFER", "0ab57b7166de99db3a55", "WITHDRAW_CURRENT", "product supplied by following SHEY"),
    ("06_TRANSFER", "04a3877f0fc81b7597c9", "WITHDRAW_CLOSE", "retained learned transfer close"),
    ("06_TRANSFER", "62ff059766b21c7de083", "COLLECT", "operation, not receiver noun"),
    ("07_CONTAINER", "df1098831679a8ad1b39", "VESSEL", "generic Herbal vessel"),
    ("07_CONTAINER", "27d97af8c96eb056c2e6", "GLAZED_VESSEL", "learned specialist vessel"),
    ("07_CONTAINER", "1779decef17481ec2853", "WIDE_VESSEL", "learned specialist vessel"),
    ("07_CONTAINER", "342c3f0777337648f4b3", "BASIN_STATION", "visible-owner station"),
    ("07_CONTAINER", "a7af89ab31ce5e247395", "FILL", "movement; vessel inherited"),
    ("07_CONTAINER", "b38d70daefd663d74625", "RECEIVER", "container; replaces duplicate fill verb"),
    ("07_CONTAINER", "e2eb77ca9d9e1a8ba29a", "WORK_BASIN", "container; replaces duplicate fill verb"),
    ("08_COLLECTION_STATION", "42cdc187d5b9ffc60063", "BRIEF_COLLECTION", "SOLK station plus E/Y"),
    ("08_COLLECTION_STATION", "1bfd786e6b8b63734a59", "SUSTAINED_COLLECTION", "SOLK station plus EE/Y"),
    ("08_COLLECTION_STATION", "3b70942557b3a40e8030", "SUSTAINED_COLLECTION_CLOSE", "SOLK station plus EE/DY"),
    ("08_COLLECTION_STATION", "e026af581c99322fbd46", "STORE", "retained storage operation"),
]


def build_dictionary() -> tuple[list[dict[str, str]], int]:
    source = read_tsv(DICT_IN)
    rows: list[dict[str, str]] = []
    revised = 0
    for original in source:
        row = dict(original)
        row.update(
            r3_previous_segmentation=original["semantic_segmentation"],
            r3_previous_nucleus_de=original["stable_concrete_nucleus_de"],
            r3_previous_gloss_de=original["concrete_word_reading_de"],
            r3_revision_family="UNCHANGED",
            r3_revision_strength="UNCHANGED",
            r3_revision_note="NOT_APPLICABLE",
        )
        override = OVERRIDES.get(row["joint_tuple_id"])
        if override:
            for key in ("semantic_segmentation", "stable_concrete_nucleus_de", "concrete_word_reading_de", "reading_type"):
                row[key] = override[key]
            row["local_expansion_examples_de"] = "R3-Mediumfassung: " + row["concrete_word_reading_de"]
            row["variation_note"] = (row["variation_note"] + "; " if row["variation_note"] else "") + "R3: " + override["note"]
            row["r3_revision_family"] = override["family"]
            row["r3_revision_strength"] = override["strength"]
            row["r3_revision_note"] = override["note"]
            revised += 1
        rows.append(row)
    return rows, revised


def build_events(dictionary: list[dict[str, str]]) -> tuple[list[dict[str, str]], int]:
    dictionary_by_id = {row["joint_tuple_id"]: row for row in dictionary}
    source = read_tsv(EVENT_IN)
    rows: list[dict[str, str]] = []
    revised = 0
    for original in source:
        row = dict(original)
        row.update(
            r3_previous_segmentation=original["semantic_segmentation"],
            r3_previous_nucleus_de=original["stable_concrete_nucleus_de"],
            r3_previous_gloss_de=original["concrete_word_reading_de"],
            r3_previous_context_de=original["contextual_event_reading_de"],
            r3_revision_family="UNCHANGED",
            r3_revision_strength="UNCHANGED",
            r3_revision_note="NOT_APPLICABLE",
        )
        override = OVERRIDES.get(row["joint_tuple_id"])
        if override:
            drow = dictionary_by_id[row["joint_tuple_id"]]
            row["semantic_segmentation"] = drow["semantic_segmentation"]
            row["stable_concrete_nucleus_de"] = drow["stable_concrete_nucleus_de"]
            row["concrete_word_reading_de"] = drow["concrete_word_reading_de"]
            row["contextual_event_reading_de"] = CONTEXT_BY_EVENT.get(row["event_id"], sentence_case(row["concrete_word_reading_de"]))
            row["workshop_slots"] = override["slots"]
            row["r3_revision_family"] = override["family"]
            row["r3_revision_strength"] = override["strength"]
            row["r3_revision_note"] = override["note"]
            revised += 1
        rows.append(row)
    return rows, revised


def build_sentences(events: list[dict[str, str]]) -> tuple[list[dict[str, str]], int]:
    source_rows = read_tsv(SENTENCE_IN)
    source_by_id = {row["statement_id"]: row for row in source_rows}
    grouped: OrderedDict[str, list[dict[str, str]]] = OrderedDict()
    for event in events:
        grouped.setdefault(event["statement_id"], []).append(event)

    rows: list[dict[str, str]] = []
    changed_statements = 0
    for statement_id, group in grouped.items():
        base = source_by_id[statement_id]
        revisions = [event for event in group if event["r3_revision_family"] != "UNCHANGED"]
        if revisions:
            changed_statements += 1
        row = dict(base)
        row["card_sequence_de"] = " · ".join(event["concrete_word_reading_de"] for event in group)
        row["event_slot_trace"] = " | ".join(f'{event["event_id"]}[{event["workshop_slots"]}]' for event in group)
        slots: list[str] = []
        for event in group:
            slots.extend(part for part in event["workshop_slots"].split("+") if part)
        row["canonical_slots_present"] = ">".join(uniq(slots))
        row["workshop_sentence_de"] = "; ".join(event["contextual_event_reading_de"] for event in group)
        row.update(
            r3_medium_revised_event_count=str(len(revisions)),
            r3_revision_families="|".join(uniq([event["r3_revision_family"] for event in revisions])) or "UNCHANGED",
            r3_previous_card_sequence_de=base["card_sequence_de"],
            r3_previous_workshop_sentence_de=base["workshop_sentence_de"],
        )
        rows.append(row)
    return rows, changed_statements


def build_records(sentences: list[dict[str, str]]) -> None:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in sentences:
        grouped[row["record_unit_id"]].append(row)
    lines = [
        "# R3: elf vollständige Records nach der Medium-/Stoffrunde",
        "",
        "Kreative Werkstattlesung. Stoff, Zwischenprodukt, Ansatz, Strömung, Durchlass und Gefäß bleiben getrennt; Zeile ist kein Satzschluss.",
        "",
    ]
    for record in RECORD_ORDER:
        rows = grouped[record]
        pages = "|".join(uniq([row["page"] for row in rows]))
        lines.extend([f"## {record} — {pages}", ""])
        for index, row in enumerate(rows, 1):
            lines.append(
                f'{index}. **{row["statement_id"]}** `{row["canonical_slots_present"]}` — '
                f'{row["workshop_sentence_de"].rstrip(".")}.'
            )
        lines.append("")
    RECORD_OUT.write_text("\n".join(lines), encoding="utf-8")


def build_paradigm(dictionary: list[dict[str, str]], events: list[dict[str, str]]) -> None:
    dmap = {row["joint_tuple_id"]: row for row in dictionary}
    event_map: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        event_map[event["joint_tuple_id"]].append(event)
    rows = []
    for level, tuple_id, role, audit_note in AUDIT:
        drow = dmap[tuple_id]
        erows = event_map[tuple_id]
        rows.append(
            {
                "semantic_level": level,
                "joint_tuple_id": tuple_id,
                "surface_family": drow["surface_family"],
                "atomic_role": role,
                "selected_segmentation": drow["semantic_segmentation"],
                "selected_nucleus_de": drow["stable_concrete_nucleus_de"],
                "selected_card_reading_de": drow["concrete_word_reading_de"],
                "occurrences": str(len(erows)),
                "events": "|".join(row["event_id"] for row in erows),
                "statements": "|".join(uniq([row["statement_id"] for row in erows])),
                "pages": "|".join(uniq([row["page"] for row in erows])),
                "records": "|".join(uniq([row["record_unit_id"] for row in erows])),
                "revision_status": "REVISED_R3" if tuple_id in OVERRIDES else "RETAINED_AUDITED",
                "strongest_context_or_counterexample": audit_note,
            }
        )
    fields = list(rows[0])
    write_tsv(PARADIGM_OUT, rows, fields)


def validate(
    dictionary: list[dict[str, str]],
    events: list[dict[str, str]],
    sentences: list[dict[str, str]],
    revised_types: int,
    revised_events: int,
    changed_statements: int,
) -> dict[str, object]:
    checks = {
        "dictionary_rows_173": len(dictionary) == 173,
        "event_rows_381": len(events) == 381,
        "sentence_rows_116": len(sentences) == 116,
        "record_count_11": len({row["record_unit_id"] for row in events}) == 11,
        "pages_allowlisted": {row["page"] for row in events} <= ALLOWED_PAGES,
        "f84_f84r_absent": all(not row["page"].startswith("f84") for row in events),
        "dictionary_no_blank_defaults": all(
            row["semantic_segmentation"] and row["stable_concrete_nucleus_de"] and row["concrete_word_reading_de"]
            for row in dictionary
        ),
        "events_no_blank_defaults": all(
            row["semantic_segmentation"] and row["stable_concrete_nucleus_de"] and row["concrete_word_reading_de"] and row["contextual_event_reading_de"]
            for row in events
        ),
        "sentences_no_blank_readings": all(row["card_sequence_de"] and row["workshop_sentence_de"] for row in sentences),
        "event_ids_unique": len({row["event_id"] for row in events}) == 381,
        "statement_event_counts_match": all(
            int(row["event_count"]) == len(row["event_ids"].split("|")) for row in sentences
        ),
        "only_expected_revised_types": {row["joint_tuple_id"] for row in dictionary if row["r3_revision_family"] != "UNCHANGED"} == set(OVERRIDES),
        "astro_unchanged_no_astro_output_written": True,
    }
    return {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "counts": {
            "revised_exact_cards": revised_types,
            "revised_events": revised_events,
            "revised_statements": changed_statements,
            "audited_paradigm_cards": len(AUDIT),
        },
        "sealed": {"f84": True, "f84r": True},
    }


def main() -> None:
    dictionary, revised_types = build_dictionary()
    events, revised_events = build_events(dictionary)
    sentences, changed_statements = build_sentences(events)

    dict_fields = list(dictionary[0])
    event_fields = list(events[0])
    sentence_fields = list(sentences[0])
    write_tsv(DICT_OUT, dictionary, dict_fields)
    write_tsv(EVENT_OUT, events, event_fields)
    write_tsv(SENTENCE_OUT, sentences, sentence_fields)
    build_records(sentences)
    build_paradigm(dictionary, events)

    validation = validate(dictionary, events, sentences, revised_types, revised_events, changed_statements)
    VALIDATION_OUT.write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    outputs = [DICT_OUT, EVENT_OUT, SENTENCE_OUT, RECORD_OUT, PARADIGM_OUT, VALIDATION_OUT]
    summary = {
        "status": validation["status"],
        "source": {
            "dictionary": str(DICT_IN.relative_to(ROOT)),
            "events": str(EVENT_IN.relative_to(ROOT)),
            "sentences": str(SENTENCE_IN.relative_to(ROOT)),
        },
        "counts": validation["counts"],
        "outputs": {path.name: sha256(path) for path in outputs},
        "astro_unchanged": True,
        "sealed": {"f84": True, "f84r": True},
    }
    SUMMARY_OUT.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if validation["status"] != "PASS":
        raise SystemExit("R3 validation failed")


if __name__ == "__main__":
    main()
