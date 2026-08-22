#!/usr/bin/env python3
"""Build the creative quantity/preparation and workshop-sentence edition."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import OrderedDict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = ROOT / "experiments/yolo/sidequest_semantic_directional_completion"

DICT_IN = SOURCE / "SELECTED_173_DIRECTIONAL_DICTIONARY.tsv"
EVENT_IN = SOURCE / "SELECTED_381_DIRECTIONAL_INTERLINEAR.tsv"
COMPONENT_IN = SOURCE / "SELECTED_DIRECTIONAL_COMPONENT_LEXICON.tsv"
UNRESOLVED_IN = SOURCE / "REMAINING_UNRESOLVED_AFTER_DIRECTION.tsv"

DICT_OUT = HERE / "SELECTED_173_QUANTITY_PREPARATION_DICTIONARY.tsv"
EVENT_OUT = HERE / "SELECTED_381_QUANTITY_PREPARATION_INTERLINEAR.tsv"
STATEMENT_OUT = HERE / "SELECTED_116_WORKSHOP_SENTENCES.tsv"
RICH_SLOT_OUT = HERE / "WORKSHOP_SENTENCE_SLOTS.tsv"
RECORD_OUT = HERE / "SELECTED_11_WORKSHOP_RECORDS.md"
COMPONENT_OUT = HERE / "SELECTED_QUANTITY_PREPARATION_COMPONENTS.tsv"
COMPOSITION_OUT = HERE / "SELECTED_COMPOSITION_TABLE.tsv"
UNRESOLVED_OUT = HERE / "REMAINING_UNRESOLVED_AFTER_QUANTITY.tsv"
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


def ov(parse: str, nucleus: str, gloss: str, source: str, strength: str, note: str) -> dict[str, str]:
    return {
        "semantic_segmentation": parse,
        "stable_concrete_nucleus_de": nucleus,
        "concrete_word_reading_de": gloss,
        "reading_type": "SELECTED_QUANTITY_PREPARATION__" + source,
        "source": source,
        "strength": strength,
        "note": note,
    }


# Exact joint-tuple identities, never a blind substring rewrite.  The short
# atoms are deliberately kept distinct: AIN is the aliquot, AIIN its measure,
# and IIN the setting/degree.
OVERRIDES = {
    "9da1b6ac2c929daea697": ov("AIN_PORTION", "AIN=Teil oder Portion", "eine Portion", "QUANTITY_CORE", "SELECTED_RECURRENT", "The three occurrences name the bounded amount, not the measuring rule."),
    "1645e612504fcef59ced": ov("OK+AIN_PORTION", "OK=in Arbeit setzen; AIN=Portion", "eine Portion zugeben", "QUANTITY_COMPOSITION", "SELECTED_PRODUCTIVE", "Seven events preserve the OK plus portion contribution."),
    "94df4847b7b16c98394a": ov("OL+AIN_PORTION", "OL=weiter oder noch eine; AIN=Portion", "eine weitere Portion zugeben", "QUANTITY_COMPOSITION", "SELECTED_RECURRENT", "Both occurrences continue with an additional portion."),
    "d784b2abcaf1a3703de2": ov("CHED+AIN_PORTION", "CHED=umsetzen; AIN=Portion", "eine Portion umsetzen", "QUANTITY_COMPOSITION", "SELECTED_SINGLETON_PREDICTION", "A single card, but both components retain their selected values."),
    "403c1592f918c8f23b88": ov("Y_REFERENT+K_HULL+AIN_PORTION", "Y=laufender Posten; AIN=Portion", "eine Portion des laufenden Postens", "QUANTITY_EXTENSION", "SELECTED_SINGLETON_PREDICTION", "The near-minimal YKAIN/YKAN/YKAIIN series is shorter than three unrelated sentence glosses."),
    "d929a14ec45749b2e805": ov("Y_REFERENT+K_HULL+AIN_PORTION", "Y=dies; AIN=Portion", "diese Portion", "QUANTITY_EXTENSION", "SELECTED_SINGLETON_PREDICTION", "This replaces the unsupported white-wine noun with the already licensed Y and AIN values."),

    "2f1c5e56e8f0ff459065": ov("AIIN_MEASURE", "AIIN=vorgeschriebenes Maß", "vorgeschriebenes Maß", "MEASURE_CORE", "SELECTED_STRONG", "Twenty events in all eleven prose records make this the portable measure card."),
    "b5fcea1eaed06b2f2291": ov("OK+AIIN_MEASURE", "OK=einstellen; AIIN=Maß", "auf das vorgeschriebene Maß einstellen", "MEASURE_COMPOSITION", "SELECTED_PRODUCTIVE", "Nine visible events use the measured setup card; E180/E181 remain one read-once source token."),
    "54d0e228ca346110af05": ov("OT+AIIN_MEASURE", "OT=danach oder nächster; AIIN=Maß", "das nächste Maß", "MEASURE_COMPOSITION", "SELECTED_RECURRENT", "The old previous-measure repetition was not contributed by OT."),
    "f7dc90b2c31fd341f0a4": ov("Y_REFERENT+K_HULL+AIIN_MEASURE", "Y=laufender Posten; AIIN=Maß", "Maß des laufenden Postens", "MEASURE_EXTENSION", "SELECTED_SINGLETON_PREDICTION", "The earlier wound-washing gloss is replaced by the portable measure axis."),
    "a8af08e69edab8e54f15": ov("SHFY_LEARNED+AIIN_MEASURE", "SHFY=stehen lassen; AIIN=vorgeschriebenes Maß", "für die vorgeschriebene Zeit stehen lassen", "MEASURE_EXTENSION", "SELECTED_CONTEXTUAL_COMPOSITION", "Measure is realized as duration in this learned rest hull."),
    "d72f71baff01cd0a0406": ov("CHLD_LEARNED+AIIN_MEASURE", "CHLD=absetzen lassen; AIIN=vorgeschriebener Stand", "bis zum vorgeschriebenen Stand absetzen lassen", "MEASURE_EXTENSION", "SELECTED_CONTEXTUAL_COMPOSITION", "The measure axis specifies the endpoint of the learned settling operation."),
    "2c82523794dcb7d2b343": ov("IIN_GRADE", "IIN=Grad oder Stufe", "vorgeschriebener Grad", "GRADE_CORE", "SELECTED_RECURRENT", "IIN is the setting itself, distinct from an aliquot and its measure."),
    "409de02322e7b2ca0c62": ov("K_SOFT_HULL+IIN_GRADE", "IIN=Konsistenzgrad; K=weich", "weiche Konsistenz", "GRADE_EXTENSION", "SELECTED_SINGLETON_PREDICTION", "This retains the earlier soft result while exposing the IIN grade contribution."),
    "fcc1deda9e24ec268eb0": ov("DA_OPENING_HULL+IIN_GRADE", "IIN=Grad oder Stufe; DA=zweite Öffnung", "zweite Öffnungsstufe", "GRADE_EXTENSION", "SELECTED_SINGLETON_PREDICTION", "The old second-opening reading is retained as one local grade rather than generalized away."),

    "7a4bb8136330ee4e6e56": ov("OR_PREPARATION", "OR=Zubereitung", "Zubereitung", "PREPARATION_CORE", "SELECTED_RECURRENT", "Seven events retain the concrete preparation noun."),
    "dec401773c1f0347793d": ov("OL+OR_PREPARATION", "OL=mit dem Vorigen; OR=Zubereitung", "mit der vorigen Zubereitung", "PREPARATION_COMPOSITION", "SELECTED_RECURRENT", "Two records preserve the preceding-preparation relation."),
    "10488b911aae52b3b334": ov("OT+OR_PREPARATION", "OT=nächste; OR=Zubereitung", "die nächste Zubereitung", "PREPARATION_COMPOSITION", "SELECTED_RECURRENT", "Two Herbal records preserve the next-preparation relation."),
    "b9d7b6d68209a9019e7a": ov("CHO_PLANT+OR_PREPARATION", "CHO=Pflanzenstoff; OR=Zubereitung", "Pflanzenzubereitung", "PREPARATION_EXTENSION", "SELECTED_SINGLETON_PREDICTION", "The H5 opening immediately repeats the pictured plant and keeps OR as preparation."),
    "6afeb5c9ab9f6cbdea0d": ov("OR_PREPARATION+AIN_PORTION", "OR=Zubereitung; AIN=Portion", "eine Portion der Zubereitung", "PREPARATION_COMPOSITION", "SELECTED_SINGLETON_PREDICTION", "Both selected atoms replace the unsupported warm-application whole gloss."),
    "497cbd9c7401810ff56b": ov("OT+OL", "OT=danach; OL=weiter", "danach weiter", "ORDER_COMPOSITION", "SELECTED_SINGLETON_PREDICTION", "This was already predicted by the historical compositional model and removes an unmotivated handful noun."),

    # Two learned DY cards already carried an end in their parse but not in
    # their German default.  The sentence grammar makes that close explicit.
    "cbb42a4fe68068325d6b": ov("DSHE_CLEAN_WATER+DY_TERMINAL", "DSHE=sauberes Wasser zugeben; DY=Schluss", "sauberes Wasser zugeben; Schluss", "SENTENCE_CLOSE_REPAIR", "SELECTED_EXISTING_COMPONENT", "The prior segmentation already contained dy=Ende."),
    "7f68f60279efe6b28cd7": ov("RSHE_WASH_PART+DY_TERMINAL", "RSHE=Teil als Waschung; DY=Schluss", "Teil als Waschung; Schluss", "SENTENCE_CLOSE_REPAIR", "SELECTED_EXISTING_COMPONENT", "The prior segmentation already contained dy=Ende."),
}


COMPOSITIONS = [
    ("AIN", "AIN", "eine Portion", "9da1b6ac2c929daea697"),
    ("OK+AIN", "OK(AIN)", "eine Portion zugeben", "1645e612504fcef59ced"),
    ("OL+AIN", "OL(AIN)", "eine weitere Portion zugeben", "94df4847b7b16c98394a"),
    ("CHED+AIN", "CHED(AIN)", "eine Portion umsetzen", "d784b2abcaf1a3703de2"),
    ("AIIN", "AIIN", "vorgeschriebenes Maß", "2f1c5e56e8f0ff459065"),
    ("OK+AIIN", "OK(AIIN)", "auf das vorgeschriebene Maß einstellen", "b5fcea1eaed06b2f2291"),
    ("OT+AIIN", "OT(AIIN)", "das nächste Maß", "54d0e228ca346110af05"),
    ("IIN", "IIN", "vorgeschriebener Grad", "2c82523794dcb7d2b343"),
    ("OR", "OR", "Zubereitung", "7a4bb8136330ee4e6e56"),
    ("OL+OR", "OL(OR)", "mit der vorigen Zubereitung", "dec401773c1f0347793d"),
    ("OT+OR", "OT(OR)", "die nächste Zubereitung", "10488b911aae52b3b334"),
    ("CHO+OR", "CHO(OR)", "Pflanzenzubereitung", "b9d7b6d68209a9019e7a"),
    ("OR+AIN", "OR(AIN)", "eine Portion der Zubereitung", "6afeb5c9ab9f6cbdea0d"),
    ("OT+OL", "OT(OL)", "danach weiter", "497cbd9c7401810ff56b"),
]


SLOT_ORDER = ["OWNER_ITEM", "SOURCE", "QUANTITY", "PREPARATION", "OPERATION", "FLOW_TRANSFER", "TARGET", "STATE_GRADE", "CLOSE"]

OWNER_BY_PAGE = {
    "f10r": "abgebildete Pflanze auf f10r",
    "f11r": "abgebildete Pflanze auf f11r",
    "f55v": "abgebildete Pflanze auf f55v",
    "f56r": "abgebildete Pflanze auf f56r",
    "f81v": "gemeinsames Becken- und Figurenfeld auf f81v",
    "f82r": "aktuelle lokale Becken- oder Gerätestation auf f82r",
    "f83r": "aktuelle lokale Gefäß- oder Leitungsstation auf f83r",
}


def slots_for(row: dict[str, str]) -> list[str]:
    parse = row["semantic_segmentation"].upper()
    gloss = row["concrete_word_reading_de"].lower()
    slots: list[str] = []
    if "Y_REFERENT" in parse or any(word in gloss for word in ("pflanze", "wurzel", "blatt", "blüte", "posten", "anteil")):
        slots.append("OWNER_ITEM")
    if "AR_SOURCE" in parse or any(word in gloss for word in ("vorrat", "quelle", "daraus", "vom vorigen posten")):
        slots.append("SOURCE")
    if any(word in parse for word in ("AIN_PORTION", "AIIN_MEASURE", "IIN_GRADE")) or any(word in gloss for word in ("portion", "maß", "menge", "grad", "stufe", "handvoll", "zeit")):
        slots.append("QUANTITY")
    if "OR_PREPARATION" in parse or any(word in gloss for word in ("zubereitung", "ansatz", "auszug", "badezusatz", "salbe")):
        slots.append("PREPARATION")
    if any(word in parse for word in ("OK+", "CHED", "CHD", "APPLICATION")) or any(word in gloss for word in ("nehmen", "zugeben", "umsetzen", "zerkleinern", "anwenden", "bestreichen", "kochen", "wringen", "befestigen", "abmessen", "einstellen")):
        slots.append("OPERATION")
    if any(word in parse for word in ("AIR_FLOW", "L+CHED", "P+CHED")) or any(word in gloss for word in ("flüssigkeit", "hinausführen", "hineinführen", "abführen", "spülen", "waschen", "durchtränken")):
        slots.append("FLOW_TRANSFER")
    if "AL_TARGET" in parse or any(word in gloss for word in ("zielstelle", "einfüllstelle", "auslassstelle", "sammelstelle", "körperstelle", "an der stelle")):
        slots.append("TARGET")
    state_word = re.search(r"\b(bereit|warm|kühl|ruhen|klar|ungekocht)\b", gloss) is not None
    if any(word in parse for word in ("IIN_GRADE", "E_GRADE", "CTH_READY", "REST", "HOLD", "WARM")) or state_word or "stehen lassen" in gloss or "absetzen" in gloss:
        slots.append("STATE_GRADE")
    if "TERMINAL" in parse or "DY=ENDE" in parse or any(word in gloss for word in ("; schluss", "; ende", "abschließen", "beenden")):
        slots.append("CLOSE")
    return uniq(slots) or ["OPERATION"]


def is_link_select(row: dict[str, str]) -> bool:
    parse = row["semantic_segmentation"].upper()
    gloss = row["concrete_word_reading_de"].lower()
    component = parse.startswith(("OT+", "OL+")) or "+OT+" in parse or "+OL+" in parse or "RENDERER+OT+" in parse or "RENDERER+OL+" in parse
    lexical = any(term in gloss for term in ("vorigen", "nächste", "danach", "weiter", "erneut"))
    return component or lexical


def slot_entries(rows: list[dict[str, str]], slot: str) -> str:
    selected = [row for row in rows if slot in row["workshop_slots"].split("+")]
    return " | ".join(f"{row['surface_display']}={row['concrete_word_reading_de']}" for row in selected)


def build_rich_slots(grouped: dict[str, list[dict[str, str]]]) -> list[dict[str, str]]:
    fields = [
        "statement_id", "record_unit_id", "page", "loci", "field_ids", "event_ids",
        "event_count", "surface_sequence", "owner_slot", "owner_mode", "link_select_slot",
        "source_item_slot", "quantity_slot", "operation_slot", "medium_flow_slot",
        "target_slot", "state_grade_slot", "close_slot", "event_slot_sequence",
        "cell_count", "work_cell_packets", "inheritance_and_omission_note",
        "line_continuity", "concrete_german_reading",
    ]
    result: list[dict[str, str]] = []
    for statement_id, rows in grouped.items():
        page = rows[0]["page"]
        owner = OWNER_BY_PAGE[page]
        link_rows = [row for row in rows if is_link_select(row)]
        source = slot_entries(rows, "SOURCE")
        owner_item = slot_entries(rows, "OWNER_ITEM")
        preparation = slot_entries(rows, "PREPARATION")
        source_items = " | ".join(value for value in (source, owner_item, preparation) if value)
        quantity = slot_entries(rows, "QUANTITY")
        operation = slot_entries(rows, "OPERATION")
        medium = slot_entries(rows, "FLOW_TRANSFER")
        target = slot_entries(rows, "TARGET")
        state = slot_entries(rows, "STATE_GRADE")
        close = slot_entries(rows, "CLOSE")
        field_groups: dict[str, list[dict[str, str]]] = OrderedDict()
        for row in rows:
            field_groups.setdefault(row["field_id"], []).append(row)
        packets = []
        for index, field_rows in enumerate(field_groups.values(), 1):
            packet = " > ".join(f"{row['event_id']}:{row['surface_display']}{{{row['workshop_slots']}}}" for row in field_rows)
            packets.append(f"Z{index}[{packet}]")
        omissions = []
        if not quantity:
            omissions.append("QUANTITY=GEERBT: kein neues Maß")
        if not medium:
            omissions.append("MEDIUM_FLOW=AUSGELASSEN: kein eigener Lauf")
        if not target:
            omissions.append("TARGET=GEERBT: lokale Arbeitsstelle")
        if not state:
            omissions.append("STATE_GRADE=AUSGELASSEN: örtlicher Zustand")
        if not close:
            omissions.append("CLOSE=OFFEN: nächste Arbeitszelle darf fortführen")
        result.append(
            {
                "statement_id": statement_id,
                "record_unit_id": rows[0]["record_unit_id"],
                "page": page,
                "loci": "|".join(uniq([row["locus"] for row in rows])),
                "field_ids": "|".join(field_groups),
                "event_ids": "|".join(row["event_id"] for row in rows),
                "event_count": str(len(rows)),
                "surface_sequence": " · ".join(row["surface_display"] for row in rows),
                "owner_slot": owner,
                "owner_mode": "PAGE_OWNER_INHERITED" if page in {"f10r", "f11r", "f55v", "f56r"} else "LOCAL_STATION_OWNER_INHERITED",
                "link_select_slot": " | ".join(f"{row['surface_display']}={row['concrete_word_reading_de']}" for row in link_rows) or "NEUE ZELLE: kein ausdrücklicher Rückverweis",
                "source_item_slot": source_items or "GEERBT: laufender Posten des Bildbesitzers",
                "quantity_slot": quantity or "GEERBT: kein neues Maß",
                "operation_slot": operation or "ELLIPTISCH: auswählen, zuordnen oder fortsetzen",
                "medium_flow_slot": medium or "AUSGELASSEN: kein eigener Lauf",
                "target_slot": target or "GEERBT: lokale Arbeitsstelle",
                "state_grade_slot": state or "AUSGELASSEN: örtlicher Zustand",
                "close_slot": close or "OFFEN: nächste Arbeitszelle darf fortführen",
                "event_slot_sequence": " > ".join(f"{row['event_id']}{{{row['workshop_slots']}}}" for row in rows),
                "cell_count": str(len(field_groups)),
                "work_cell_packets": " || ".join(packets),
                "inheritance_and_omission_note": "; ".join(omissions) or "ALLE BENÖTIGTEN SLOTS LOKAL GESETZT",
                "line_continuity": "CROSSES_PHYSICAL_LINE" if len(uniq([row["locus"] for row in rows])) > 1 else "ONE_LOCUS: kein erzwungener Satzschluss aus der Zeile",
                "concrete_german_reading": f"Beim Besitzer „{owner}“: " + sentence_case("; ".join(row["concrete_word_reading_de"] for row in rows)) + ".",
            }
        )
    if result and list(result[0]) != fields:
        raise AssertionError("rich slot schema drift")
    return result


def build_components() -> list[dict[str, str]]:
    rows = read_tsv(COMPONENT_IN)
    for row in rows:
        if row["component_id"] == "AIN":
            row.update(visible_realizations="ain; kain in licensed exact cards", working_meaning_de="Teil; abgeteilte Portion", status="FIXED_IN_WORKING_MODEL", licensed_environment="AIN, OK+AIN, OL+AIN, CHED+AIN and OR+AIN", evidence_summary="3 base, 7 OK, 2 OL, 1 CHED and 1 OR events", important_limit="the amount itself, never the rule by which it is measured")
        elif row["component_id"] == "AIIN":
            row.update(working_meaning_de="Maß; vorgeschriebene Menge", status="FIXED_IN_WORKING_MODEL", licensed_environment="base AIIN, OK+AIIN, OT+AIIN and selected contextual compounds", evidence_summary="20 base and 12 recurrent OK/OT events plus bounded predictions", important_limit="the measuring prescription, not the physical aliquot")
        elif row["component_id"] == "IIN_GRADE":
            row.update(visible_realizations="oiiin|soiiin and bounded IIN compounds", working_meaning_de="Grad; Arbeitsstufe oder Einstellung", status="FIXED_CONTEXT_BOUND", licensed_environment="exact IIN grade card plus selected K/D hulls", evidence_summary="two recurrent base events and two single-card extensions", important_limit="the local dimension may be heat concentration duration opening or another setting")
        elif row["component_id"] == "OR_PREPARATION":
            row.update(working_meaning_de="Zubereitung; bereiteter Ansatz", status="FIXED_IN_WORKING_MODEL", licensed_environment="OR, OL+OR, OT+OR, CHO+OR and OR+AIN", evidence_summary="7 base, 2 previous, 2 next, 1 plant and 1 portion event", important_limit="only licensed exact identities; not every visible internal or")
        elif row["component_id"] == "OL":
            row.update(licensed_environment="base continuation plus OK+OL, OL+CHED, OL+AIN and OL+OR", evidence_summary="base card plus transfer, quantity and preparation compounds", important_limit="continuation/previous relation, not oil")
        elif row["component_id"] == "OT":
            row.update(licensed_environment="before AIIN, OR, OL, AL, CHED and E grades", evidence_summary="next/after contribution across quantity preparation order target and operation", important_limit="does not itself mean repeat or equality")
    return rows


def build_unresolved() -> list[dict[str, str]]:
    result = [row for row in read_tsv(UNRESOLVED_IN) if row["candidate_component"] != "IIN_GRADE_PORTABILITY"]
    result.extend(
        [
            {"candidate_component": "IIN_LOCAL_DIMENSION", "current_best_constraint": "portable grade or setting", "why_not_closed": "the two recurrent and two extended cards do not identify heat concentration duration or aperture", "working_default_until_better_model": "grade or work stage", "prediction_that_could_improve_it": "another IIN card should contrast two settings of the same operation"},
            {"candidate_component": "LONG_AIIN_HULLS", "current_best_constraint": "several long exact cards admit an AIIN contribution", "why_not_closed": "CHO D SOLK and SHFY hulls are not independently complete paradigms", "working_default_until_better_model": "use the selected concrete whole construction", "prediction_that_could_improve_it": "a second occurrence should preserve the measure slot under a new owner"},
            {"candidate_component": "OR_INTERNAL_STRINGS", "current_best_constraint": "OR composes in OR OLOR OTCHOR and ORAIN", "why_not_closed": "Y CHE OYK and CHO hulls may merely contain the same surface letters", "working_default_until_better_model": "do not split ycheor oykchor or chochor", "prediction_that_could_improve_it": "a minimal pair must preserve preparation while changing only the hull"},
        ]
    )
    return result


def build() -> dict[str, object]:
    dictionary = read_tsv(DICT_IN)
    events = read_tsv(EVENT_IN)
    source_by_id = {row["joint_tuple_id"]: row for row in dictionary}
    missing = sorted(set(OVERRIDES) - set(source_by_id))
    if missing:
        raise ValueError(f"Missing override IDs: {missing}")

    dict_fields = list(dictionary[0]) + [
        "quantity_previous_segmentation", "quantity_previous_nucleus_de",
        "quantity_previous_gloss_de", "quantity_revision_source",
        "quantity_revision_strength", "quantity_revision_note",
    ]
    revised_dictionary: list[dict[str, str]] = []
    for source_row in dictionary:
        row = dict(source_row)
        selected = OVERRIDES.get(row["joint_tuple_id"])
        if selected:
            row["quantity_previous_segmentation"] = row["semantic_segmentation"]
            row["quantity_previous_nucleus_de"] = row["stable_concrete_nucleus_de"]
            row["quantity_previous_gloss_de"] = row["concrete_word_reading_de"]
            for key in ("semantic_segmentation", "stable_concrete_nucleus_de", "concrete_word_reading_de", "reading_type"):
                row[key] = selected[key]
            row["local_expansion_examples_de"] = "Mengen-/Zubereitungsfassung: " + selected["concrete_word_reading_de"]
            row["variation_note"] += "; quantity/preparation: " + selected["note"]
            row["quantity_revision_source"] = selected["source"]
            row["quantity_revision_strength"] = selected["strength"]
            row["quantity_revision_note"] = selected["note"]
        else:
            row.update(quantity_previous_segmentation="", quantity_previous_nucleus_de="", quantity_previous_gloss_de="", quantity_revision_source="UNCHANGED", quantity_revision_strength="UNCHANGED", quantity_revision_note="NOT_APPLICABLE")
        revised_dictionary.append(row)

    revised_by_id = {row["joint_tuple_id"]: row for row in revised_dictionary}
    event_fields = list(events[0]) + [
        "quantity_previous_segmentation", "quantity_previous_nucleus_de",
        "quantity_previous_gloss_de", "quantity_previous_context_de",
        "quantity_revision_source", "quantity_revision_strength", "workshop_slots",
    ]
    revised_events: list[dict[str, str]] = []
    for source_row in events:
        row = dict(source_row)
        selected = OVERRIDES.get(row["joint_tuple_id"])
        card = revised_by_id[row["joint_tuple_id"]]
        if selected:
            row["quantity_previous_segmentation"] = row["semantic_segmentation"]
            row["quantity_previous_nucleus_de"] = row["stable_concrete_nucleus_de"]
            row["quantity_previous_gloss_de"] = row["concrete_word_reading_de"]
            row["quantity_previous_context_de"] = row["contextual_event_reading_de"]
            row["semantic_segmentation"] = card["semantic_segmentation"]
            row["stable_concrete_nucleus_de"] = card["stable_concrete_nucleus_de"]
            row["concrete_word_reading_de"] = card["concrete_word_reading_de"]
            row["contextual_event_reading_de"] = sentence_case(card["concrete_word_reading_de"])
            row["quantity_revision_source"] = selected["source"]
            row["quantity_revision_strength"] = selected["strength"]
        else:
            row.update(quantity_previous_segmentation="", quantity_previous_nucleus_de="", quantity_previous_gloss_de="", quantity_previous_context_de="", quantity_revision_source="UNCHANGED", quantity_revision_strength="UNCHANGED")
        row["workshop_slots"] = "+".join(slots_for(row))
        revised_events.append(row)

    grouped: dict[str, list[dict[str, str]]] = OrderedDict()
    for row in revised_events:
        grouped.setdefault(row["statement_id"], []).append(row)
    statement_fields = [
        "statement_id", "record_unit_id", "page", "loci", "field_ids", "event_ids",
        "event_count", "revised_event_count", "surface_sequence", "card_sequence_de",
        "event_slot_trace", "canonical_slots_present", "workshop_sentence_de",
        "physical_line_note",
    ]
    statements: list[dict[str, str]] = []
    for statement_id, rows in grouped.items():
        glosses = [row["concrete_word_reading_de"] for row in rows]
        slots = uniq(slot for row in rows for slot in row["workshop_slots"].split("+"))
        canonical = [slot for slot in SLOT_ORDER if slot in slots]
        statements.append(
            {
                "statement_id": statement_id,
                "record_unit_id": rows[0]["record_unit_id"],
                "page": rows[0]["page"],
                "loci": "|".join(uniq([row["locus"] for row in rows])),
                "field_ids": "|".join(uniq([row["field_id"] for row in rows])),
                "event_ids": "|".join(row["event_id"] for row in rows),
                "event_count": str(len(rows)),
                "revised_event_count": str(sum(row["quantity_revision_source"] != "UNCHANGED" for row in rows)),
                "surface_sequence": " · ".join(row["surface_display"] for row in rows),
                "card_sequence_de": " · ".join(glosses),
                "event_slot_trace": " | ".join(f"{row['event_id']}[{row['workshop_slots']}]" for row in rows),
                "canonical_slots_present": ">".join(canonical),
                "workshop_sentence_de": sentence_case("; ".join(glosses)),
                "physical_line_note": rows[-1]["statement_continuation"],
            }
        )

    records: dict[str, list[dict[str, str]]] = OrderedDict()
    for row in statements:
        records.setdefault(row["record_unit_id"], []).append(row)
    markdown = [
        "# Elf vollständige Werkstatt-Records nach Mengen-/Zubereitungsabschluss",
        "",
        "Jede Aussage behält die sichtbare Kartenreihenfolge. Das Slotmuster ist eine",
        "optionale Werkstatt-Checkliste, keine Behauptung über eine moderne Satzsyntax:",
        "",
        "`GEGENSTAND → QUELLE → MENGE → ZUBEREITUNG → ARBEITSGANG → LAUF → ZIEL → GRAD → SCHLUSS`",
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
    rich_slots = build_rich_slots(grouped)
    event_counts = {ident: sum(row["joint_tuple_id"] == ident for row in revised_events) for ident in source_by_id}
    composition_rows = [
        {"family": family, "formula": formula, "selected_reading_de": gloss, "joint_tuple_id": ident, "surface_family": revised_by_id[ident]["surface_family"], "events": str(event_counts[ident]), "status": OVERRIDES[ident]["strength"]}
        for family, formula, gloss, ident in COMPOSITIONS
    ]

    write_tsv(DICT_OUT, revised_dictionary, dict_fields)
    write_tsv(EVENT_OUT, revised_events, event_fields)
    write_tsv(STATEMENT_OUT, statements, statement_fields)
    write_tsv(RICH_SLOT_OUT, rich_slots, list(rich_slots[0]))
    write_tsv(COMPONENT_OUT, components, list(components[0]))
    write_tsv(COMPOSITION_OUT, composition_rows, list(composition_rows[0]))
    write_tsv(UNRESOLVED_OUT, unresolved, list(unresolved[0]))

    changed_cards = [row for row in revised_dictionary if row["quantity_revision_source"] != "UNCHANGED"]
    changed_events = [row for row in revised_events if row["quantity_revision_source"] != "UNCHANGED"]
    outputs = (DICT_OUT, EVENT_OUT, STATEMENT_OUT, RICH_SLOT_OUT, RECORD_OUT, COMPONENT_OUT, COMPOSITION_OUT, UNRESOLVED_OUT)
    summary: dict[str, object] = {
        "schema": "SIDEQUEST_SELECTED_QUANTITY_PREPARATION_SUMMARY_V1",
        "status": "PASS",
        "cards": len(revised_dictionary),
        "events": len(revised_events),
        "statements": len(statements),
        "rich_slot_statements": len(rich_slots),
        "records": len(records),
        "changed_cards": len(changed_cards),
        "changed_events": len(changed_events),
        "changed_statements": sum(int(row["revised_event_count"]) > 0 for row in statements),
        "components": len(components),
        "composition_rows": len(composition_rows),
        "remaining_unresolved_rows": len(unresolved),
        "inputs": {str(path.relative_to(ROOT)): sha256(path) for path in (DICT_IN, EVENT_IN, COMPONENT_IN, UNRESOLVED_IN)},
        "outputs": {str(path.relative_to(ROOT)): sha256(path) for path in outputs},
    }
    SUMMARY_OUT.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary


if __name__ == "__main__":
    print(json.dumps(build(), ensure_ascii=False, indent=2, sort_keys=True))
