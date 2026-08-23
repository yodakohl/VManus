#!/usr/bin/env python3
"""Build the creative Biological operation-alphabet edition."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import OrderedDict, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
BASE = HERE.parent / "sidequest_semantic_herbal_material_action_completion"

DICT_IN = BASE / "SELECTED_173_HERBAL_MATERIAL_DICTIONARY.tsv"
EVENT_IN = BASE / "SELECTED_381_HERBAL_MATERIAL_INTERLINEAR.tsv"
SENTENCE_IN = BASE / "SELECTED_116_HERBAL_MATERIAL_SENTENCES.tsv"

DICT_OUT = HERE / "SELECTED_173_BIOLOGICAL_OPERATION_DICTIONARY.tsv"
EVENT_OUT = HERE / "SELECTED_381_BIOLOGICAL_OPERATION_INTERLINEAR.tsv"
SENTENCE_OUT = HERE / "SELECTED_116_BIOLOGICAL_OPERATION_SENTENCES.tsv"
RECORD_OUT = HERE / "SELECTED_11_BIOLOGICAL_OPERATION_RECORDS.md"
PARADIGM_OUT = HERE / "BIOLOGICAL_OPERATION_PARADIGM.tsv"
ALPHABET_OUT = HERE / "BIOLOGICAL_OPERATION_ALPHABET.tsv"
CHECK_OUT = HERE / "BUILD_CHECK.json"
SUMMARY_OUT = HERE / "BUILD_SUMMARY.json"

RECORD_ORDER = ["H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"]
ALLOWED_PAGES = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"}


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


def rev(seg: str, nucleus: str, gloss: str, context: str, family: str, mnemonic: str, reason: str) -> dict[str, str]:
    return {
        "seg": seg,
        "nucleus": nucleus,
        "gloss": gloss,
        "context": context,
        "family": family,
        "mnemonic": mnemonic,
        "reason": reason,
    }


# This pass removes sentence-sized card meanings.  SSHK, OCTHEOL, CHES, LKEDY
# and LDDY remain learned shop signs; the rest use already selected components.
REVISIONS = {
    "54e32e9c1414b20640e9": rev("SSHK_SWIVEL_WHOLE+CLOSE", "SSHK=schwenken; Schluss", "schwenken; Schluss", "Schwenke den Posten und schließe den Schritt", "MIX_ACTION", "AGITA", "Replace an empty 'special condition' with one short learned handling verb."),
    "0ab57b7166de99db3a55": rev("LCH_WITHDRAW+Y_ITEM", "LCH=abziehen; Y=dies", "abziehen", "Ziehe den Posten ab", "WITHDRAW", "DETRAHE", "Y supplies the current item; the dictionary needs only the action."),
    "daf32e6db9e04413ce7f": rev("OK_SET+GRADE_2+OL_CONTINUE", "OK=ansetzen; EE=länger; OL=fortführen", "länger fortführen", "Führe den Posten länger fort", "CONTINUE", "PROSEQUERE", "Remove the redundant phrase 'with the previous'."),
    "db167f8e9b53eefb58f8": rev("OK_SET+SHED_SETTLE+CLOSE", "SHED=absetzen; Schluss", "absetzen; Schluss", "Lass absetzen und schließe den Schritt", "SETTLE", "DEPONE", "The action itself already selects the working item."),
    "daa1347f456415fe8737": rev("OL_CONTINUE+SHED_SETTLE+CLOSE", "OL=weiter; SHED=absetzen; Schluss", "weiter absetzen; Schluss", "Lass weiter absetzen und schließe den Schritt", "SETTLE", "DEPONE ULTERIUS", "Compose continuation plus settling instead of a sentence fragment."),
    "87411f84689b4f93a303": rev("OK+CHD_TRANSFER+CLOSE", "CHD=umsetzen; Schluss", "umsetzen; Schluss", "Setze um und schließe den Schritt", "TRANSFER", "TRANSFERE", "Ansatz is supplied by the active item, not by the card."),
    "07913ef9b1fb773cd325": rev("OK+CHED_TRANSFER+CLOSE", "CHED=umsetzen; Schluss", "umsetzen; Schluss", "Setze um und schließe den Schritt", "TRANSFER", "TRANSFERE", "The E-rendered companion receives the same compact operation."),
    "c45ebac60774620561e2": rev("OT_FOLLOW+GRADE_1+CLOSE", "OT=Folge; E=kurz; Schluss", "kurze Folge; Schluss", "Nimm die kurze Folge und schließe", "ORDER", "SEQUENS BREVIS", "Turn the old sentence phrase into a compact graded order sign."),
    "ff178343c18e287ce3b7": rev("OT_FOLLOW+GRADE_2+CLOSE", "OT=Folge; EE=länger; Schluss", "lange Folge; Schluss", "Nimm die lange Folge und schließe", "ORDER", "SEQUENS LONGA", "Use the same graded order sign with the longer grade."),
    "d784b2abcaf1a3703de2": rev("CHED_TRANSFER+AIN_PORTION", "CHED=umsetzen; AIN=Portion", "Portion umsetzen", "Setze eine Portion um", "QUANTITY_TRANSFER", "PARTEM TRANSFERE", "Compact productive composition."),
    "2bc2ed2630dbdaaa6b59": rev("D+AL_TO+CHD_TRANSFER+CLOSE", "AL=an/zu; CHD=umsetzen; Schluss", "dorthin umsetzen; Schluss", "Setze dorthin um und schließe", "TARGET_TRANSFER", "TRANSFERE AD", "Replace vague local with the selected target relation."),
    "b958a512ca6a3559e86e": rev("LKEDY_REWASH_WHOLE+CLOSE", "LKEDY=nachwaschen; Schluss", "nachwaschen; Schluss", "Wasche nach und schließe", "WASH_ACTION", "LAVA ITERUM", "One short specialist verb replaces the numbered phrase 'second washing'."),
    "eb2e4bc143f623ee03ac": rev("OK+Y_ITEM+LDDY_FASTEN_CLOSE", "LDDY=befestigen; Schluss", "befestigen; Schluss", "Befestige den Posten und schließe", "FASTEN", "LIGA", "The current item is inherited; keep the learned fastening action short."),
    "a8f891de626fc00028e9": rev("OCTHEOL_EQUALIZE_WHOLE", "OCTHEOL=gleichstellen", "gleichstellen", "Stelle beide Seiten gleich", "ADJUST", "AEQUA", "A concrete shop verb is smaller than 'same local setting'."),
    "db729b598e89e11452e0": rev("CHES_DIVIDE_EQUAL_WHOLE", "CHES=gleichteilen", "gleichteilen", "Teile gleich", "DIVIDE", "DIVIDE AEQUALITER", "A compact action replaces the noun phrase 'equal shares'."),
    "d225b7a7b95da7aee437": rev("D+CHD_TRANSFER+CLOSE", "CHD=umsetzen; Schluss", "umsetzen; Schluss", "Setze um und schließe den Schritt", "TRANSFER", "TRANSFERE", "Remove the abstract nominal phrase 'complete the transfer'."),
}


BIO_SENTENCES = {
    "B1-S001": "Setze den ersten Posten kurz an und schließe",
    "B1-S002": "Stelle das Sollmaß ein, lass Beckenwasser zu, setze dort an, gib eine weitere Portion und Badzusatz hinzu, führe den warmen Fortsetzungsansatz weiter, halte die Sollmenge dort länger, leite sie durch, setze sie um und schließe",
    "B1-S003": "Führe weiter, schwenke den Posten und schließe",
    "B1-S004": "Setze um, führe weiter, lass absetzen und schließe",
    "B1-S005": "Führe den Posten weiter und schließe",
    "B1-S006": "Gib eine Portion und den Badzusatz zu, leite durch und lass abkühlen",
    "B1-S007": "Setze den Posten um und schließe",
    "B1-S008": "Führe den aktuellen Posten weiter, wärme kurz, lass absetzen und schließe",
    "B1-S009": "Setze kurz an und schließe",
    "B1-S010": "Setze den nächsten Posten kurz an und schließe",
    "B1-S011": "Leite durch und setze den Posten an",
    "B1-S012": "Beginne den Waschgang, setze kurz an, wasche und schließe",
    "B1-S013": "Wasche und schließe",
    "B1-S014": "Setze zur Arbeitsstelle um, führe am Auslass ab und leite zum Folgeabgang weiter",
    "B1-S015": "Fülle das Gefäß, setze den Inhalt um und schließe",
    "B1-S016": "Setze dort länger an, führe weiter, lass absetzen und schließe",
    "B1-S017": "Führe ihn dorthin, öffne den Hahn, setze um und schließe",
    "B1-S018": "Stelle die Auffangschale bereit, reibe die bezeichnete Stelle ein, bringe sie auf Zielstufe, sammle länger und schließe",
    "B1-S019": "Lass absetzen und schließe",
    "B1-S020": "Wärme kurz, seih und schließe",
    "B1-S021": "Führe den nächsten Posten dorthin",

    "B2-S001": "Setze um und schließe",
    "B2-S002": "Führe weiter und schließe",
    "B2-S003": "Gib eine Portion zu, setze den Posten länger an und schließe",
    "B2-S004": "Setze dort an, leite durch den Ausgang, führe ab, setze länger an, seih ab und schließe",
    "B2-S005": "Setze den Posten am Seihtuch an, leite ihn durch, stelle das Sollmaß ein, gleiche beide Seiten an, wärme länger, ziehe ab und schließe",
    "B2-S006": "Nimm den längeren Folgeposten, setze ihn dort am Überlauf an und führe ihn weiter",
    "B2-S007": "Gib Frischwasser zu und schließe",
    "B2-S008": "Stelle das Folgemaß ein, setze daraus an, lass absetzen und schließe",
    "B2-S009": "Lass den vorigen Posten weiter absetzen und schließe",
    "B2-S010": "Setze länger an, führe den Posten durch die Düse und nimm den Klarauszug",
    "B2-S011": "Gib eine Portion zu, nimm daraus eine weitere Portion, setze länger an und schließe",
    "B2-S012": "Ziehe den Posten ab, nimm den Klarauszug, halte ihn kurz bereit, setze ihn länger an der Nassstelle nach Sollmaß an, führe ihn vollständig aus und schließe",
    "B2-S013": "Führe ab und schließe",
    "B2-S014": "Schließe den Bodenablauf",
    "B2-S015": "Gib Spülwasser zu, setze länger an und schließe",
    "B2-S016": "Führe ihn dorthin und von dort ab, teile gleich, stelle das Sollmaß ein, nimm die lange Folge, setze kurz an, führe ein und schließe",
    "B2-S017": "Lass Warmwasser ein und schließe die Nebenöffnung",
    "B2-S018": "Setze länger an und schließe",
    "B2-S019": "Führe die Waschung aus und schließe",
    "B2-S020": "Nimm die lange Folge und schließe",
    "B2-S021": "Setze länger an und schließe",
    "B2-S022": "Führe den Rest ab und schließe",

    "B3-S001": "Sammle länger und schließe",
    "B3-S002": "Führe danach dorthin, wärme länger und schließe",
    "B3-S003": "Nimm den aktuellen Posten nach Sollmaß, führe ihn ab und schließe",
    "B3-S004": "Stelle das Sollmaß ein, führe danach dorthin und nimm daraus",
    "B3-S005": "Setze um und schließe",
    "B3-S006": "Setze dorthin um, führe weiter und schließe",
    "B3-S007": "Stelle das Sollmaß ein, setze um, setze länger an und schließe",
    "B3-S008": "Führe ab und schließe",
    "B3-S009": "Setze den Posten an",
    "B3-S010": "Führe am Einlass zu, nimm die kurze Folge und schließe",
    "B3-S011": "Streiche den Posten auf, setze ihn an, setze um und lass abkühlen",
    "B3-S012": "Lass den Ansatz absetzen und schließe",
    "B3-S013": "Stelle das Sollmaß ein, nimm eine Portion, halte kurz bereit, setze kurz an und schließe",
    "B3-S014": "Lass Wasser ein, lass länger absetzen und schließe",
    "B3-S015": "Führe ab und schließe",
    "B3-S016": "Schließe den Bodenablauf, setze den Posten um und schließe",
    "B3-S017": "Setze länger an und schließe",
    "B3-S018": "Lass absetzen und schließe",
    "B3-S019": "Lass absetzen und schließe",
    "B3-S020": "Führe dorthin, führe ab und schließe",
    "B3-S021": "Stelle das Sollmaß ein, halte bereit, führe dorthin, lass den Posten temperiert absetzen, führe ihn erneut dorthin, stelle bereit, setze dort um und schließe",
    "B3-S022": "Führe die Folgeumsetzung aus und schließe",
    "B3-S023": "Führe ab und schließe",
    "B3-S024": "Setze um und schließe",
    "B3-S025": "Setze um und schließe",
    "B3-S026": "Stelle das Sammelbecken bereit, warte bis zum Absetzstand, setze um, gib eine Portion zu, halte bereit, warte bis zum Klarpunkt, sammle länger und schließe",
    "B3-S027": "Nimm die lange Folge und schließe",
    "B3-S028": "Setze länger, dann kurz an und schließe",
    "B3-S029": "Führe nach der ersten Spülung weiter, setze kurz an und schließe",
    "B3-S030": "Setze den Posten nach Sollmaß an, leite Wasser weiter, führe die Folgeumsetzung aus und schließe",
    "B3-S031": "Setze länger an und schließe",
    "B3-S032": "Setze eine Portion um, führe sie in die Wanne, stelle das Folgemaß ein, nimm die kurze Folge und schließe",
    "B3-S033": "Ziehe ab und schließe",
    "B3-S034": "Bringe auf Zielstufe, halte bereit, bearbeite gleichmäßig, stelle das Folgemaß ein, führe unten weiter, lass absetzen und schließe",

    "B4-S001": "Setze länger an und schließe",
    "B4-S002": "Bereite das Becken vor, setze länger und dann kurz an und schließe",
    "B4-S003": "Setze um, führe danach dorthin, wähle den Folgeposten, setze länger an, führe weiter, lass absetzen und schließe",
    "B4-S004": "Befestige den Posten und schließe",
    "B4-S005": "Lege das Tuch ein, setze um, setze länger an und schließe",
    "B4-S006": "Seih und schließe",
    "B4-S007": "Seih nochmals und schließe",
    "B4-S008": "Stelle das Sollmaß ein, wärme länger, öffne den Ablauf, setze kurz an und schließe",
    "B4-S009": "Lass absetzen und schließe",
    "B4-S010": "Führe weiter und schließe",
    "B4-S011": "Stelle das Sollmaß ein, wärme kurz, führe länger fort, gib eine Portion zu, setze um, führe weiter, wasche nach und schließe",
    "B4-S012": "Führe ab und schließe",
    "B4-S013": "Setze die Fortsetzung ein, lass absetzen und schließe",
    "B4-S014": "Führe den Ansatz am Überlauf, schließe den Wasserlauf und beende den Schritt",
    "B4-S015": "Gib eine Portion zu, nimm den Klarauszug, halte eine Portion für die angegebene Dauer, sammle kurz, führe ab und schließe",
    "B4-S016": "Gib eine weitere Portion dorthin, gieße warm aus, lass absetzen und schließe",

    "B5-S001": "Führe die Folgeumsetzung aus und schließe",
    "B5-S002": "Setze um und schließe",
    "B5-S003": "Lass dort absetzen, führe dorthin weiter, halte warm, setze nach Sollmaß um, stelle die Öffnung auf Zielstufe und setze erneut um",
    "B6-S001": "Sammle den rohen Posten länger, öffne den Seitenarm, führe nach Sollmaß weiter, lege das Tuch ein und führe den Posten zur Endstelle",
}


ALPHABET = [
    ("OK", "ANSETZEN", "PONE", "start or place the active work item"),
    ("CHD~CHED", "UMSETZEN", "TRANSFERE", "move the active item into the next working state"),
    ("P+CHED", "EINFÜHREN", "INFUNDE", "move into a receiver"),
    ("L+CHED", "ABFÜHREN", "DEDUC", "move out toward a receiver"),
    ("LCH", "ABZIEHEN", "DETRAHE", "withdraw from the active item"),
    ("LSH", "WASCHEN", "LAVA", "wash or rinse"),
    ("LKEDY", "NACHWASCHEN", "LAVA ITERUM", "learned repeat-wash sign"),
    ("SHED", "ABSETZEN", "DEPONE", "leave material to settle"),
    ("CHK", "WÄRMEN", "CALEFAC", "warm the active item"),
    ("CKHE", "SEIHEN", "COLA", "strain through the selected passage"),
    ("SOLK", "SAMMELN", "COLLIGE", "collect at the active receiver"),
    ("LDDY", "BEFESTIGEN", "LIGA", "learned fastening close"),
    ("SSHK", "SCHWENKEN", "AGITA", "learned agitation sign"),
    ("OCTHEOL", "GLEICHSTELLEN", "AEQUA", "learned balancing sign"),
    ("CHES", "GLEICHTEILEN", "DIVIDE AEQUALITER", "learned equal-division sign"),
    ("OT", "FOLGE", "SEQUENS", "next operation or item"),
    ("OL", "FORTFÜHREN", "PROSEQUERE", "continue the current operation"),
    ("E / EE / EEE", "KURZ / LÄNGER / VOLL", "BREVIS / LONGA / PLENA", "graded duration or completion"),
    ("Y~CHY", "DIESER POSTEN", "HOC", "current working referent"),
    ("licensed close", "SCHLIESSEN", "CLAUDE", "finish the local work cell"),
]


def build() -> dict[str, object]:
    dictionary = read_tsv(DICT_IN)
    events = read_tsv(EVENT_IN)
    sentence_base = {row["statement_id"]: row for row in read_tsv(SENTENCE_IN)}
    if (len(dictionary), len(events), len(sentence_base)) != (173, 381, 116):
        raise AssertionError("unexpected input dimensions")

    out_dictionary: list[dict[str, str]] = []
    for original in dictionary:
        row = dict(original)
        row.update(
            biological_operation_previous_segmentation=original["semantic_segmentation"],
            biological_operation_previous_nucleus_de=original["stable_concrete_nucleus_de"],
            biological_operation_previous_gloss_de=original["concrete_word_reading_de"],
            biological_operation_revision="UNCHANGED",
            biological_operation_family="CARRIED_FORWARD",
            biological_operation_mnemonic="",
            biological_operation_reason="Herbal material/action edition retained.",
        )
        chosen = REVISIONS.get(row["joint_tuple_id"])
        if chosen:
            row["semantic_segmentation"] = chosen["seg"]
            row["stable_concrete_nucleus_de"] = chosen["nucleus"]
            row["concrete_word_reading_de"] = chosen["gloss"]
            row["reading_type"] = "BIOLOGICAL_OPERATION__" + chosen["family"]
            row["local_expansion_examples_de"] = "Biological-Werkstattfassung: " + chosen["context"]
            row["biological_operation_revision"] = "REVISED"
            row["biological_operation_family"] = chosen["family"]
            row["biological_operation_mnemonic"] = chosen["mnemonic"]
            row["biological_operation_reason"] = chosen["reason"]
        out_dictionary.append(row)
    dmap = {row["joint_tuple_id"]: row for row in out_dictionary}

    out_events: list[dict[str, str]] = []
    for original in events:
        row = dict(original)
        row.update(
            biological_operation_previous_segmentation=original["semantic_segmentation"],
            biological_operation_previous_nucleus_de=original["stable_concrete_nucleus_de"],
            biological_operation_previous_gloss_de=original["concrete_word_reading_de"],
            biological_operation_previous_context_de=original["contextual_event_reading_de"],
            biological_operation_revision="UNCHANGED",
            biological_operation_family="CARRIED_FORWARD",
            biological_operation_reason="Herbal material/action edition retained.",
        )
        chosen = REVISIONS.get(row["joint_tuple_id"])
        if chosen:
            drow = dmap[row["joint_tuple_id"]]
            row["semantic_segmentation"] = drow["semantic_segmentation"]
            row["stable_concrete_nucleus_de"] = drow["stable_concrete_nucleus_de"]
            row["concrete_word_reading_de"] = drow["concrete_word_reading_de"]
            row["contextual_event_reading_de"] = chosen["context"]
            row["biological_operation_revision"] = "REVISED"
            row["biological_operation_family"] = chosen["family"]
            row["biological_operation_reason"] = chosen["reason"]
        out_events.append(row)

    grouped: OrderedDict[str, list[dict[str, str]]] = OrderedDict()
    for event in out_events:
        grouped.setdefault(event["statement_id"], []).append(event)

    expected_bio = {statement_id for statement_id in sentence_base if statement_id.startswith("B")}
    if set(BIO_SENTENCES) != expected_bio:
        missing = sorted(expected_bio - set(BIO_SENTENCES))
        extra = sorted(set(BIO_SENTENCES) - expected_bio)
        raise AssertionError(f"Biological sentence coverage mismatch: missing={missing}, extra={extra}")

    out_sentences: list[dict[str, str]] = []
    for statement_id, group in grouped.items():
        base = sentence_base[statement_id]
        row = dict(base)
        changed = [event for event in group if event["biological_operation_revision"] == "REVISED"]
        row["card_sequence_de"] = " · ".join(event["concrete_word_reading_de"] for event in group)
        row["event_slot_trace"] = " | ".join(f'{event["event_id"]}[{event["workshop_slots"]}]' for event in group)
        row["workshop_sentence_de"] = BIO_SENTENCES.get(statement_id, base["workshop_sentence_de"])
        row["biological_operation_revised_event_count"] = str(len(changed))
        row["biological_operation_families"] = "|".join(OrderedDict.fromkeys(event["biological_operation_family"] for event in changed)) or "CARRIED_FORWARD"
        row["biological_operation_previous_card_sequence_de"] = base["card_sequence_de"]
        row["biological_operation_previous_workshop_sentence_de"] = base["workshop_sentence_de"]
        out_sentences.append(row)

    records: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in out_sentences:
        records[row["record_unit_id"]].append(row)
    lines = [
        "# Biological-Bedienungsfassung — elf Prosa-Records",
        "",
        "Die Herbal-Artikel bleiben unverändert. Die sechs Biological-Records werden hier als fortlaufende Bedienungsabschnitte gelesen; eine physische Zeile beendet keinen Satz.",
        "",
    ]
    for record in RECORD_ORDER:
        rows = records[record]
        title = "Herbal-Artikel" if record.startswith("H") else "Biological-Arbeitsgang"
        lines.extend([f"## {record} — {rows[0]['page']} — {title}", ""])
        continuous = ". ".join(row["workshop_sentence_de"].rstrip(". ") for row in rows) + "."
        lines.extend([continuous, "", "### Kartenfolge", ""])
        for index, row in enumerate(rows, 1):
            lines.append(f"{index}. **{row['statement_id']}** — {row['workshop_sentence_de'].rstrip('.') }.")
        lines.append("")
    RECORD_OUT.write_text("\n".join(lines), encoding="utf-8")

    base_map = {row["joint_tuple_id"]: row for row in dictionary}
    paradigm_rows = []
    for ident, chosen in REVISIONS.items():
        before = base_map[ident]
        after = dmap[ident]
        event_ids = [row["event_id"] for row in out_events if row["joint_tuple_id"] == ident]
        statement_ids = list(OrderedDict.fromkeys(row["statement_id"] for row in out_events if row["joint_tuple_id"] == ident))
        paradigm_rows.append({
            "joint_tuple_id": ident,
            "surface_family": after["surface_family"],
            "occurrences": after["occurrences"],
            "records": after["records"],
            "previous_default_de": before["concrete_word_reading_de"],
            "selected_default_de": after["concrete_word_reading_de"],
            "selected_segmentation": after["semantic_segmentation"],
            "operation_family": chosen["family"],
            "workshop_mnemonic": chosen["mnemonic"],
            "event_ids": "|".join(event_ids),
            "statement_ids": "|".join(statement_ids),
            "composition_or_learned_sign": "COMPOSITION" if "+" in chosen["seg"] and "WHOLE" not in chosen["seg"] else "LEARNED_SIGN",
            "workshop_reason": chosen["reason"],
        })
    alphabet_rows = [
        {"component_or_sign": a, "selected_value_de": b, "ca_1420_teaching_parallel": c, "workshop_use": d}
        for a, b, c, d in ALPHABET
    ]

    write_tsv(DICT_OUT, out_dictionary)
    write_tsv(EVENT_OUT, out_events)
    write_tsv(SENTENCE_OUT, out_sentences)
    write_tsv(PARADIGM_OUT, paradigm_rows)
    write_tsv(ALPHABET_OUT, alphabet_rows)

    checks = {
        "cards_173": len(out_dictionary) == 173,
        "events_381": len(out_events) == 381,
        "sentences_116": len(out_sentences) == 116,
        "records_11": set(records) == set(RECORD_ORDER),
        "biological_sentences_97": len(BIO_SENTENCES) == 97,
        "dictionary_ids_unique": len(dmap) == 173,
        "event_ids_unique": len({row["event_id"] for row in out_events}) == 381,
        "all_cards_concrete": all(row["concrete_word_reading_de"] for row in out_dictionary),
        "all_events_readable": all(row["contextual_event_reading_de"] for row in out_events),
        "event_dictionary_match": all(row["concrete_word_reading_de"] == dmap[row["joint_tuple_id"]]["concrete_word_reading_de"] for row in out_events),
        "all_events_in_sentences": sum(int(row["event_count"]) for row in out_sentences) == 381,
        "all_biological_sentences_rewritten": set(BIO_SENTENCES) == {row["statement_id"] for row in out_sentences if row["record_unit_id"].startswith("B")},
        "revisions_exact": {row["joint_tuple_id"] for row in out_dictionary if row["biological_operation_revision"] == "REVISED"} == set(REVISIONS),
        "sentence_glosses_removed": all(phrase not in row["concrete_word_reading_de"] for row in out_dictionary for phrase in ("unter besonderer Bedingung", "dieselbe örtliche Einstellung", "zweite Waschung", "mit Vorigem länger")),
        "only_fixed_pages": {row["page"] for row in out_events} == ALLOWED_PAGES,
        "sealed_absent": all(not row["page"].startswith("f84") for row in out_events),
    }
    result = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "counts": {
            "cards": len(out_dictionary),
            "events": len(out_events),
            "sentences": len(out_sentences),
            "records": len(records),
            "revised_cards": len(REVISIONS),
            "revised_events": sum(row["biological_operation_revision"] == "REVISED" for row in out_events),
            "biological_sentences_rewritten": len(BIO_SENTENCES),
            "operation_alphabet_rows": len(alphabet_rows),
        },
        "working_model": "SMALL PRODUCTIVE OPERATION ALPHABET + LEARNED SPECIALIST ACTION SIGNS",
        "sealed": {"f84": True, "f84r": True},
    }
    CHECK_OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))

    outputs = [DICT_OUT, EVENT_OUT, SENTENCE_OUT, RECORD_OUT, PARADIGM_OUT, ALPHABET_OUT, CHECK_OUT]
    summary = {
        "status": result["status"],
        "input_hashes": {path.name: sha256(path) for path in (DICT_IN, EVENT_IN, SENTENCE_IN)},
        "output_hashes": {path.name: sha256(path) for path in outputs},
        "counts": result["counts"],
        "sealed": {"f84": True, "f84r": True},
    }
    SUMMARY_OUT.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary


if __name__ == "__main__":
    print(json.dumps(build(), ensure_ascii=False, indent=2, sort_keys=True))
