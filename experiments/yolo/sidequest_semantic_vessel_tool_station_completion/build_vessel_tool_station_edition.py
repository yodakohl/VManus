#!/usr/bin/env python3
"""Build the creative vessel/tool/station edition from the thermal edition."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import OrderedDict, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
BASE = HERE.parent / "sidequest_semantic_thermal_temporal_completion"

DICT_IN = BASE / "SELECTED_173_THERMAL_TEMPORAL_DICTIONARY.tsv"
EVENT_IN = BASE / "SELECTED_381_THERMAL_TEMPORAL_INTERLINEAR.tsv"
SENTENCE_IN = BASE / "SELECTED_116_THERMAL_TEMPORAL_SENTENCES.tsv"

DICT_OUT = HERE / "SELECTED_173_VESSEL_TOOL_DICTIONARY.tsv"
EVENT_OUT = HERE / "SELECTED_381_VESSEL_TOOL_INTERLINEAR.tsv"
SENTENCE_OUT = HERE / "SELECTED_116_VESSEL_TOOL_SENTENCES.tsv"
RECORD_OUT = HERE / "SELECTED_11_VESSEL_TOOL_RECORDS.md"
PARADIGM_OUT = HERE / "VESSEL_TOOL_PARADIGM.tsv"
COMPONENT_OUT = HERE / "VESSEL_TOOL_COMPONENTS.tsv"
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


def rev(seg: str, nucleus: str, gloss: str, context: str, family: str, latin: str, reason: str) -> dict[str, str]:
    return {
        "seg": seg,
        "nucleus": nucleus,
        "gloss": gloss,
        "context": context,
        "family": family,
        "latin": latin,
        "reason": reason,
    }


# This is a creative workshop lexicon, not a plaintext claim.  The Latin labels
# are mnemonic parallels for a ca. 1420 mixed abbreviation/nomenclator system;
# no phonetic identity with the surface is asserted.
REVISIONS = {
    # Productive address and transfer grammar.
    "4d4559019a961b834aa1": rev("AR_FROM", "AR=aus/von", "daraus", "Daraus", "AR_SOURCE", "DE / EX", "Reduce the old phrase 'aus demselben Vorrat' to one reusable source relation."),
    "dd0ecaf5e27d81befffc": rev("AL_TO", "AL=an/zu", "dorthin", "Dorthin", "AL_TARGET", "AD", "AL behaves more cleanly as a target relation than as a complete noun 'Stelle'."),
    "308e8ea2d5d190c498e8": rev("OK_SET+AL_TO", "OK=ansetzen; AL=an/zu", "dort ansetzen", "Dort ansetzen", "OK_AL", "PONE AD", "Transparent operation plus target relation."),
    "4a7a6326ac95a8809302": rev("OK_SET+AL_TO+Y_ITEM", "OK=ansetzen; AL=an/zu; Y=dies", "dies dort ansetzen", "Diesen Posten dort ansetzen", "OK_AL_Y", "PONE HOC AD", "The current item is supplied by Y."),
    "93f69c38fdedee1598e9": rev("OK_SET+EE_HOLD+AL_TO", "OK=ansetzen; EE=länger; AL=an/zu", "dort länger halten", "Dort länger halten", "OK_EE_AL", "TENE AD", "A target plus sustained contact, not a sentence-sized treatment word."),
    "90bcf0a9ec0ef56399e6": rev("OT_NEXT+AL_TO", "OT=danach; AL=an/zu", "danach dorthin", "Danach dorthin", "OT_AL", "DEINDE AD", "Productive order plus target relation."),
    "abb23e5e6936b4147f76": rev("SHED_SETTLE+AL_TO", "SHED=absetzen; AL=an/zu", "dort absetzen", "Dort absetzen", "SHED_AL", "DEPONE AD", "The site is supplied by AL; no separate station noun is needed."),
    "00d8ebe3c68294eeac39": rev("CHD_TRANSFER+AL_TO", "CHD=umsetzen; AL=an/zu", "dort umsetzen", "Dort umsetzen", "CHD_AL", "TRANSFER AD", "Short target-directed transfer."),
    "7811a7daff25d476e28d": rev("OLS_BELOW+AL_TO+Y_ITEM", "OLS=unterhalb; AL=an/zu; Y=dies", "unterhalb", "Unterhalb weiterführen", "LOWER_SITE", "INFRA", "Compress the former noun phrase 'untere Stelle'."),
    "97ddca78c9ebcc956d04": rev("LD_END+AL_TO", "LD=Ende; AL=an/zu", "Endstelle", "Zur Endstelle", "END_SITE", "AD FINEM", "A learned local hull plus the productive target relation."),
    "433713294b25b0a12f66": rev("L_OUT+CHED_TRANSFER+AL_TO", "L=ab; CHED=führen; AL=an/zu", "Auslass", "Am Auslass abführen", "OUTLET", "EXITUS", "The old long gloss collapses to the named output station."),
    "ba540da978ea132f6da5": rev("P_IN+CHED_TRANSFER+AL_TO", "P=ein; CHED=führen; AL=an/zu", "Einlass", "Am Einlass zuführen", "INLET", "INTroitus", "Mirror image of L+CHED+AL."),
    "0f15effeca7ab10bb026": rev("L_OUT+CHED_TRANSFER+AR_FROM", "L=ab; CHED=führen; AR=aus/von", "von dort abführen", "Von dort abführen", "OUT_FROM", "EDUCE DE", "Source and outward transfer remain separately visible."),
    "65df3cd9e59060042d47": rev("P_IN+CHED_TRANSFER+TERMINAL", "P=ein; CHED=führen; Endkarte=Schluss", "einführen; Schluss", "Einführen; Schluss", "IN_TRANSFER", "INDUCE", "Short inward transfer plus the learned close."),
    "ba8142680851f24c9ff2": rev("L_OUT+CHED_TRANSFER", "L=ab; CHED=führen", "abführen", "Abführen", "OUT_TRANSFER", "EDUCE", "Use one portable outward-transfer verb."),
    "de7321bface5628e35d6": rev("L_OUT+CHED_TRANSFER+TERMINAL", "L=ab; CHED=führen; Endkarte=Schluss", "abführen; Schluss", "Abführen; Schluss", "OUT_TRANSFER_CLOSE", "EDUCE", "Same transfer with the learned terminal construction."),
    "f2af6326898fb5b490a4": rev("LO_REMAINDER+CHED_TRANSFER+TERMINAL", "LO=Rest; CHED=abführen; Endkarte=Schluss", "Rest abführen; Schluss", "Den Rest abführen; Schluss", "REMAINDER_OUT", "EDUCE RELIQUUM", "Keep the local remainder hull but shorten the action."),
    "6f7ff8287eddf4da9fdb": rev("CHD~CHED_TRANSFER+Y_ITEM", "CHD~CHED=umsetzen; Y=dies", "umsetzen", "Umsetzen", "TRANSFER_CORE", "TRANSFER", "Collapse the old sentence-sized 'current item transfer or work through' hedge to one operation."),
    "5e8441397e7c0faf042b": rev("CHED_TRANSFER+CHY_ITEM", "CHED=umsetzen; CHY=dies", "umsetzen", "Umsetzen", "TRANSFER_CORE", "TRANSFER", "Wrapped current-item realization of the same short operation."),
    "259b2b3b0bf859882e2c": rev("CHED_TRANSFER+TERMINAL", "CHED=umsetzen; Endkarte=Schluss", "umsetzen; Schluss", "Umsetzen; Schluss", "TRANSFER_CLOSE", "TRANSFER; FINIS", "Replace 'finish the work movement' with the operation plus its learned close."),

    # Through-path and filter grammar.
    "2cc8bb3c2af19607888f": rev("CKH_THROUGH+Y_ITEM", "CKH=durch; Y=dies", "durchleiten", "Durchleiten", "PASSAGE", "PER", "CKH is most useful as a through-path, not as a named pipe."),
    "f329f2051370174e9a38": rev("L_OUT+CKH_THROUGH+Y_ITEM", "L=ab; CKH=Durchgang; Y=dies", "Ausgangsdurchlass", "Durch den Ausgangsdurchlass leiten", "OUT_PASSAGE", "PER EXITUM", "This becomes the compositional outward passage rather than an unexplained ordinal opening."),
    "c1db6b0a28d5cbb5d3d2": rev("L_OUT+CKHE_STRAIN+TERMINAL", "L=ab; CKHE=seihen; Endkarte=Schluss", "abseihen; Schluss", "Abseihen; Schluss", "STRAIN_OUT", "COLA", "Remove the unsupported adjective 'klar'."),
    "d68bc8de3bcee09db23c": rev("CKHE_STRAIN+TERMINAL", "CKHE=seihen; Endkarte=Schluss", "seihen; Schluss", "Seihen; Schluss", "STRAIN", "COLA", "Learned filtered version of the through-path."),
    "c1913ec4ff84148da6d3": rev("SHE_OVERFLOW_WHOLE", "SHECKHY=Überlauf", "Überlauf", "Am Überlauf", "OVERFLOW", "SUPERFLUUM", "Replace the prepositional sentence fragment with one apparatus noun."),
    "ecce30bc8dcc400bf2c8": rev("QO_OVERFLOW_WHOLE", "QOCKHEY=Überlauf", "Überlauf", "Am Überlauf", "OVERFLOW", "SUPERFLUUM", "Second learned realization of the same workshop object."),

    # Collection and cloth.
    "42cdc187d5b9ffc60063": rev("SOLK_COLLECT+E_SHORT+Y_ITEM", "SOLK=sammeln; E=kurz; Y=dies", "kurz sammeln", "Kurz sammeln", "COLLECT_GRADE", "COLLIGE", "Use a verb that combines cleanly with the E grade."),
    "1bfd786e6b8b63734a59": rev("SOLK_COLLECT+EE_LONG+Y_ITEM", "SOLK=sammeln; EE=länger; Y=dies", "länger sammeln", "Länger sammeln", "COLLECT_GRADE", "COLLIGE", "Same collection family with the longer grade."),
    "3b70942557b3a40e8030": rev("SOLK_COLLECT+EE_LONG+TERMINAL", "SOLK=sammeln; EE=länger; Endkarte=Schluss", "länger sammeln; Schluss", "Länger sammeln; Schluss", "COLLECT_GRADE", "COLLIGE", "Closed member of the same collection family."),
    "2d2e37ccb2dacc53ee5a": rev("SOLKAIIN_CLOTH_WHOLE", "SOLKAIIN=Seihtuch", "Seihtuch", "Seihtuch einsetzen", "CLOTH_NOMENCLATOR", "COLATORIUM", "Memorized specialist cloth, not forced into SOLK+AIIN."),
    "53cd0637c6820ba5e91f": rev("DAIN_CLOTH_WHOLE", "DAIN=Tuch", "Tuch", "Tuch einlegen", "CLOTH_NOMENCLATOR", "PANNUS", "Plain cloth remains a shorter learned whole sign."),

    # Learned vessel nomenclator.
    "df1098831679a8ad1b39": rev("OS_VESSEL_WHOLE", "OS=Gefäß", "Gefäß", "In das Gefäß geben", "VESSEL_NOMENCLATOR", "VAS", "Generic vessel sign."),
    "27d97af8c96eb056c2e6": rev("OYKCHOR_POT_WHOLE", "OYKCHOR=Topf", "Topf", "In den Topf geben", "VESSEL_NOMENCLATOR", "OLLA", "The former adjective 'glasiert' was too specific for the card."),
    "b38d70daefd663d74625": rev("LY_RECEIVER_WHOLE", "LY=Auffangschale", "Auffangschale", "Auffangschale bereitstellen", "VESSEL_NOMENCLATOR", "SCUTELLA", "Short learned receiving-vessel name."),
    "1779decef17481ec2853": rev("QOTEDAIIN_VAT_WHOLE", "QOTEDAIIN=Wanne", "Wanne", "Die Wanne verwenden", "VESSEL_NOMENCLATOR", "TINA", "Replace the descriptive phrase 'breites Gefäß' with one vessel class."),
    "e2eb77ca9d9e1a8ba29a": rev("QOLCHEY_BASIN_WHOLE", "QOLCHEY=Becken", "Becken", "Das Becken vorbereiten", "VESSEL_NOMENCLATOR", "LABRUM", "Short learned basin name."),
    "342c3f0777337648f4b3": rev("CHEEDAR_COLLECTING_BASIN_WHOLE", "CHEEDAR=Sammelbecken", "Sammelbecken", "Das Sammelbecken bereitstellen", "VESSEL_NOMENCLATOR", "RECEPTACULUM", "One compact vessel name replaces 'Beckenstation'."),

    # Learned port nomenclator; ordinals are removed unless composition supplies them.
    "a06244ef1f2b37ca44c1": rev("TEOL_TAP_WHOLE", "TEOL=Hahn", "Hahn", "Den Hahn öffnen", "PORT_NOMENCLATOR", "CANNA", "The former 'first opening' was an overread; retain the concrete fitting."),
    "5eff216ba51fbfb21f22": rev("LS_NOZZLE_WHOLE", "LS=Düse", "Düse", "Durch die Düse führen", "PORT_NOMENCLATOR", "FISTULA", "Local hand-device reading becomes a learned nozzle sign."),
    "92e43836d82f98bf02d3": rev("SHEEY_DRAIN_WHOLE", "SHEEY=Ablauf", "Ablauf", "Den Ablauf öffnen", "PORT_NOMENCLATOR", "EMISSARIUM", "Separate exact card from the CHEEY/SHEY clear-extract card."),
    "3e9c7f217843b588489d": rev("RALY_SIDE_ARM_WHOLE", "RALY=Seitenarm", "Seitenarm", "Den Seitenarm öffnen", "PORT_NOMENCLATOR", "RAMUS", "Fits the visible multiport owner without inventing an ordinal."),
    "78b3b3140714da19090d": rev("DALDY_SIDE_PORT+TERMINAL", "DALDY=Nebenöffnung; Endkarte=Schluss", "Nebenöffnung; Schluss", "Die Nebenöffnung schließen", "PORT_NOMENCLATOR", "OSTIUM LATERALE", "Remove the unsupported second/again reading."),
    "fcc1deda9e24ec268eb0": rev("DA+IIN_PORT_GRADE", "DA=Öffnung; IIN=Zielstufe", "Öffnungsstufe", "Öffnung auf Zielstufe stellen", "PORT_GRADE", "GRADUS OSTII", "The IIN grade survives; the ordinal does not."),
    "29e0eb222ef2fb99523a": rev("LAR_BOTTOM_DRAIN_WHOLE", "LAR=Bodenablauf", "Bodenablauf", "Den Bodenablauf schließen", "PORT_NOMENCLATOR", "EMISSARIUM INFERIUS", "Short exact station name."),
    "2b7fa918d1b2f5c656e3": rev("LO_BOTTOM_DRAIN_WHOLE", "LO=Bodenablauf", "Bodenablauf", "Den Bodenablauf schließen", "PORT_NOMENCLATOR", "EMISSARIUM INFERIUS", "Second learned code for the same local fitting."),
    "b6b654722e55729cc947": rev("OT_NEXT+AR_OUT", "OT=danach; AR=Abgang", "Folgeabgang", "Zum Folgeabgang", "ORDERED_PORT", "EXITUS SEQUENS", "Keep order and source-side relation visible."),
    "3ae9a121ba0045b913e8": rev("OK_SET+AR_FROM", "OK=ansetzen; AR=aus/von", "daraus ansetzen", "Daraus ansetzen", "OK_AR", "PONE EX", "Productive source-directed counterpart to OK+AL."),

    # Water and local workplace terms carried into the same apparatus grammar.
    "12efe866f335461823a6": rev("CH_INLET+AIR_WATER", "AIR=Wasser", "Wasserzulauf", "Wasser zulaufen lassen", "WATER_PATH", "AQUA", "AIR remains the water stem inside a learned inlet hull."),
    "22fb87a5a83e5c3fb510": rev("K_BASIN+AIR_WATER", "AIR=Wasser", "Beckenwasser", "Beckenwasser", "WATER_PATH", "AQUA IN PELVI", "Learned basin hull plus AIR."),
    "7d2404c835b10a2c06af": rev("OK_SET+AIR_WATER", "OK=ansetzen; AIR=Wasser", "Wasser einlassen", "Wasser einlassen", "WATER_PATH", "MITTE AQUAM", "The apparatus expansion is shorter than 'water in motion'."),
    "b154ff779abe5f196c80": rev("SCHED_LEAD+AIR_WATER", "SCHED=weiterführen; AIR=Wasser", "Wasser weiterleiten", "Wasser weiterleiten", "WATER_PATH", "DUCE AQUAM", "Portable water-transfer compound."),
    "8aedd154964a78e555d6": rev("D_HULL+AIR_WATER+Y_ITEM+TERMINAL", "AIR=Wasser; Y=dies; Endkarte=Schluss", "Wasserlauf schließen; Schluss", "Wasserlauf schließen; Schluss", "WATER_PATH", "CLAUDE AQUAM", "Retain the learned close around the water item."),
    "5fca8fc3dee57e1d8c1f": rev("LCHEEY_WET_PLACE_WHOLE", "LCHEEY=Nassstelle", "Nassstelle", "Nassstelle", "WORKPLACE_NOMENCLATOR", "LOCUS MADIDUS", "Shorten 'benetzte Stelle' to a compact station name."),
    "c205570c49d4d93c23d3": rev("QOLKY_WORKPLACE_WHOLE", "QOLKY=Arbeitsstelle", "Arbeitsstelle", "Arbeitsstelle", "WORKPLACE_NOMENCLATOR", "LOCUS OPERIS", "Neutral workplace is more portable than treatment site."),
}


COMPONENTS = [
    ("AL", "AN / ZU", "AD", "OKAL, OTAL, SHEDAL, PCHEDAL", "productive target relation"),
    ("AR", "AUS / VON", "DE / EX", "CHAR, QOKAR, LCHEDAR, CHEOAR", "productive source relation"),
    ("CHED", "UMSETZEN", "TRANSFER", "CHEDY, CHEDCHY, DCHEDY", "productive transfer core"),
    ("L+CHED", "ABFÜHREN", "EDUCE", "LCHED, LCHEDY, LCHEDAR, LCHEDAL", "productive outward transfer"),
    ("P+CHED", "EINFÜHREN", "INDUCE", "PCHEDY, PCHEDAL", "productive inward transfer"),
    ("CKH", "DURCH / DURCHGANG", "PER", "CHCKHY, LCHECKHY", "productive passage"),
    ("CKHE", "SEIHEN", "COLA", "SHCKHEDY, LCHECKHEDY", "filtered passage"),
    ("SOLK", "SAMMELN", "COLLIGE", "SOLKEY, SOLKEEY, SOLKEEDY", "productive collection plus grade"),
    ("AIR", "WASSER", "AQUA", "CHAIR, KAIR, OKAIR, SCHEDAIR", "productive medium stem"),
    ("OS", "GEFÄSS", "VAS", "OS", "learned whole sign"),
    ("OYKCHOR", "TOPF", "OLLA", "OYKCHOR", "learned whole sign"),
    ("LY", "AUFFANGSCHALE", "SCUTELLA", "LY", "learned whole sign"),
    ("QOTEDAIIN", "WANNE", "TINA", "QOTEDAIIN", "learned whole sign"),
    ("QOLCHEY", "BECKEN", "LABRUM", "QOLCHEY", "learned whole sign"),
    ("CHEEDAR", "SAMMELBECKEN", "RECEPTACULUM", "CHEEDAR", "learned whole sign"),
    ("DAIN", "TUCH", "PANNUS", "DAIN", "learned whole sign"),
    ("SOLKAIIN", "SEIHTUCH", "COLATORIUM", "SOLKAIIN", "learned whole sign"),
    ("TEOL", "HAHN", "CANNA", "TEOL", "learned fitting"),
    ("LS", "DÜSE", "FISTULA", "LS", "learned fitting"),
    ("SHEEY", "ABLAUF", "EMISSARIUM", "SHEEY", "learned fitting"),
    ("RALY", "SEITENARM", "RAMUS", "RALY", "learned fitting"),
]


def build() -> dict[str, object]:
    dictionary = read_tsv(DICT_IN)
    events = read_tsv(EVENT_IN)
    sentence_base = {row["statement_id"]: row for row in read_tsv(SENTENCE_IN)}
    if (len(dictionary), len(events), len(sentence_base)) != (173, 381, 116):
        raise AssertionError("unexpected input dimensions")

    selected_dictionary: list[dict[str, str]] = []
    for original in dictionary:
        row = dict(original)
        row.update(
            vessel_tool_previous_segmentation=original["semantic_segmentation"],
            vessel_tool_previous_nucleus_de=original["stable_concrete_nucleus_de"],
            vessel_tool_previous_gloss_de=original["concrete_word_reading_de"],
            vessel_tool_revision="UNCHANGED",
            vessel_tool_family="CARRIED_FORWARD",
            vessel_tool_latin_mnemonic="",
            vessel_tool_reason="Thermal/temporal edition retained.",
        )
        chosen = REVISIONS.get(row["joint_tuple_id"])
        if chosen:
            row["semantic_segmentation"] = chosen["seg"]
            row["stable_concrete_nucleus_de"] = chosen["nucleus"]
            row["concrete_word_reading_de"] = chosen["gloss"]
            row["reading_type"] = "VESSEL_TOOL__" + chosen["family"]
            row["local_expansion_examples_de"] = "Werkstattfassung: " + chosen["context"]
            row["vessel_tool_revision"] = "REVISED"
            row["vessel_tool_family"] = chosen["family"]
            row["vessel_tool_latin_mnemonic"] = chosen["latin"]
            row["vessel_tool_reason"] = chosen["reason"]
        selected_dictionary.append(row)
    dmap = {row["joint_tuple_id"]: row for row in selected_dictionary}

    selected_events: list[dict[str, str]] = []
    for original in events:
        row = dict(original)
        row.update(
            vessel_tool_previous_segmentation=original["semantic_segmentation"],
            vessel_tool_previous_nucleus_de=original["stable_concrete_nucleus_de"],
            vessel_tool_previous_gloss_de=original["concrete_word_reading_de"],
            vessel_tool_previous_context_de=original["contextual_event_reading_de"],
            vessel_tool_revision="UNCHANGED",
            vessel_tool_family="CARRIED_FORWARD",
            vessel_tool_reason="Thermal/temporal edition retained.",
        )
        chosen = REVISIONS.get(row["joint_tuple_id"])
        if chosen:
            drow = dmap[row["joint_tuple_id"]]
            row["semantic_segmentation"] = drow["semantic_segmentation"]
            row["stable_concrete_nucleus_de"] = drow["stable_concrete_nucleus_de"]
            row["concrete_word_reading_de"] = drow["concrete_word_reading_de"]
            row["contextual_event_reading_de"] = chosen["context"]
            row["vessel_tool_revision"] = "REVISED"
            row["vessel_tool_family"] = chosen["family"]
            row["vessel_tool_reason"] = chosen["reason"]
        selected_events.append(row)

    grouped: OrderedDict[str, list[dict[str, str]]] = OrderedDict()
    for event in selected_events:
        grouped.setdefault(event["statement_id"], []).append(event)

    selected_sentences: list[dict[str, str]] = []
    for statement_id, group in grouped.items():
        base = sentence_base[statement_id]
        row = dict(base)
        changed = [event for event in group if event["vessel_tool_revision"] == "REVISED"]
        row["card_sequence_de"] = " · ".join(event["concrete_word_reading_de"] for event in group)
        row["event_slot_trace"] = " | ".join(f'{event["event_id"]}[{event["workshop_slots"]}]' for event in group)
        row["workshop_sentence_de"] = "; ".join(event["contextual_event_reading_de"] for event in group)
        row["vessel_tool_revised_event_count"] = str(len(changed))
        row["vessel_tool_families"] = "|".join(OrderedDict.fromkeys(event["vessel_tool_family"] for event in changed)) or "CARRIED_FORWARD"
        row["vessel_tool_previous_card_sequence_de"] = base["card_sequence_de"]
        row["vessel_tool_previous_workshop_sentence_de"] = base["workshop_sentence_de"]
        selected_sentences.append(row)

    records: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in selected_sentences:
        records[row["record_unit_id"]].append(row)
    lines = [
        "# Gefäß-, Werkzeug- und Stationsfassung — elf fortlaufende Records",
        "",
        "Kreative Werkstattlesung: Fachkürzel und gelernte Gerätewörter werden gemeinsam rückgelesen; eine sichtbare Zeile beendet keinen Satz.",
        "",
    ]
    for record in RECORD_ORDER:
        rows = records[record]
        lines.extend([f"## {record} — {rows[0]['page']}", ""])
        for index, row in enumerate(rows, 1):
            lines.append(f"{index}. **{row['statement_id']}** — {row['workshop_sentence_de'].rstrip('.')}.")
        lines.append("")
    RECORD_OUT.write_text("\n".join(lines), encoding="utf-8")

    paradigm_rows = []
    base_map = {row["joint_tuple_id"]: row for row in dictionary}
    for ident, chosen in REVISIONS.items():
        before = base_map[ident]
        after = dmap[ident]
        event_ids = [row["event_id"] for row in selected_events if row["joint_tuple_id"] == ident]
        paradigm_rows.append({
            "joint_tuple_id": ident,
            "surface_family": after["surface_family"],
            "occurrences": after["occurrences"],
            "records": after["records"],
            "previous_default_de": before["concrete_word_reading_de"],
            "selected_default_de": after["concrete_word_reading_de"],
            "selected_segmentation": after["semantic_segmentation"],
            "family": chosen["family"],
            "latin_workshop_mnemonic": chosen["latin"],
            "event_ids": "|".join(event_ids),
            "composition_or_nomenclator": "COMPOSITION" if any(token in chosen["seg"] for token in ("+", "AR_", "AL_", "CKH_", "SOLK_")) and "WHOLE" not in chosen["seg"] else "LEARNED_WHOLE_SIGN",
            "workshop_reason": chosen["reason"],
        })

    component_rows = [
        {
            "component_or_whole_sign": component,
            "selected_value_de": value,
            "latin_workshop_parallel": latin,
            "current_examples": examples,
            "role_in_mixed_system": role,
        }
        for component, value, latin, examples, role in COMPONENTS
    ]

    write_tsv(DICT_OUT, selected_dictionary)
    write_tsv(EVENT_OUT, selected_events)
    write_tsv(SENTENCE_OUT, selected_sentences)
    write_tsv(PARADIGM_OUT, paradigm_rows)
    write_tsv(COMPONENT_OUT, component_rows)

    checks = {
        "cards_173": len(selected_dictionary) == 173,
        "events_381": len(selected_events) == 381,
        "sentences_116": len(selected_sentences) == 116,
        "records_11": set(records) == set(RECORD_ORDER),
        "only_fixed_pages": {row["page"] for row in selected_events} == ALLOWED_PAGES,
        "sealed_pages_absent": all(not row["page"].startswith("f84") for row in selected_events),
        "dictionary_ids_unique": len(dmap) == 173,
        "event_ids_unique": len({row["event_id"] for row in selected_events}) == 381,
        "all_cards_have_short_defaults": all(row["concrete_word_reading_de"] for row in selected_dictionary),
        "all_events_have_context": all(row["contextual_event_reading_de"] for row in selected_events),
        "event_dictionary_match": all(row["concrete_word_reading_de"] == dmap[row["joint_tuple_id"]]["concrete_word_reading_de"] for row in selected_events),
        "all_events_in_sentences": sum(int(row["event_count"]) for row in selected_sentences) == 381,
        "revisions_exact": {row["joint_tuple_id"] for row in selected_dictionary if row["vessel_tool_revision"] == "REVISED"} == set(REVISIONS),
        "al_is_target_relation": dmap["dd0ecaf5e27d81befffc"]["concrete_word_reading_de"] == "dorthin",
        "ar_is_source_relation": dmap["4d4559019a961b834aa1"]["concrete_word_reading_de"] == "daraus",
        "port_ordinals_removed": all("erste Öffnung" not in dmap[ident]["concrete_word_reading_de"] and "zweite Öffnung" not in dmap[ident]["concrete_word_reading_de"] for ident in ("a06244ef1f2b37ca44c1", "5eff216ba51fbfb21f22", "92e43836d82f98bf02d3", "3e9c7f217843b588489d", "78b3b3140714da19090d", "fcc1deda9e24ec268eb0")),
        "vessel_nomenclator_six": all(dmap[ident]["vessel_tool_family"] == "VESSEL_NOMENCLATOR" for ident in ("df1098831679a8ad1b39", "27d97af8c96eb056c2e6", "b38d70daefd663d74625", "1779decef17481ec2853", "e2eb77ca9d9e1a8ba29a", "342c3f0777337648f4b3")),
    }
    result = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "counts": {
            "cards": len(selected_dictionary),
            "events": len(selected_events),
            "sentences": len(selected_sentences),
            "records": len(records),
            "revised_cards": len(REVISIONS),
            "revised_events": sum(row["vessel_tool_revision"] == "REVISED" for row in selected_events),
            "components_and_whole_signs": len(component_rows),
        },
        "working_model": "PRODUCTIVE AD/DE/PER/IN/OUT/COLLECT GRAMMAR + LEARNED VESSEL/TOOL/PORT NOMENCLATOR",
        "sealed": {"f84": True, "f84r": True},
    }
    CHECK_OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))

    outputs = [DICT_OUT, EVENT_OUT, SENTENCE_OUT, RECORD_OUT, PARADIGM_OUT, COMPONENT_OUT, CHECK_OUT]
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
