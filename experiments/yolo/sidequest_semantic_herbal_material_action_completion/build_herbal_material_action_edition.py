#!/usr/bin/env python3
"""Build the creative Herbal material/action edition from the vessel edition."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import OrderedDict, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
BASE = HERE.parent / "sidequest_semantic_vessel_tool_station_completion"

DICT_IN = BASE / "SELECTED_173_VESSEL_TOOL_DICTIONARY.tsv"
EVENT_IN = BASE / "SELECTED_381_VESSEL_TOOL_INTERLINEAR.tsv"
SENTENCE_IN = BASE / "SELECTED_116_VESSEL_TOOL_SENTENCES.tsv"

DICT_OUT = HERE / "SELECTED_173_HERBAL_MATERIAL_DICTIONARY.tsv"
EVENT_OUT = HERE / "SELECTED_381_HERBAL_MATERIAL_INTERLINEAR.tsv"
SENTENCE_OUT = HERE / "SELECTED_116_HERBAL_MATERIAL_SENTENCES.tsv"
RECORD_OUT = HERE / "SELECTED_11_HERBAL_MATERIAL_RECORDS.md"
PARADIGM_OUT = HERE / "HERBAL_MATERIAL_PARADIGM.tsv"
COMPONENT_OUT = HERE / "HERBAL_MATERIAL_COMPONENTS.tsv"
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
    return {"seg": seg, "nucleus": nucleus, "gloss": gloss, "context": context, "family": family, "latin": latin, "reason": reason}


REVISIONS = {
    "65f320e75510b2f38182": rev("DCHEY_ROOT_WHOLE", "DCHEY=Wurzel", "Wurzel", "Wurzel nehmen", "PLANT_PART", "RADIX", "Use one plant-part noun rather than the phrase 'part of the root'."),
    "dedc383b600397a301ee": rev("CTH_READY+OR_BATCH", "CTH=bereit; OR=Ansatz", "Ansatz bereit", "Ansatz bereitstellen", "CTH_OR", "PARATUM", "Visible CTH+OR now follows the shared ready/batch values instead of the unrelated verb 'clean'."),
    "a6939862e33ece5a0483": rev("ETYD_ROOT_REMAINDER_WHOLE", "ETYD=Wurzelrest", "Wurzelrest", "Wurzelrest verwahren", "PLANT_PART", "RELIQUUM RADICIS", "Remove the former stomach-pain and storage sentence from the card value."),
    "7249edc4df3419c26999": rev("Y_ITEM+CHEO_EXTRACT+OR_BATCH", "Y=dies; CHEO=Auszug; OR=Ansatz", "Auszugsansatz", "Auszugsansatz der abgebildeten Pflanze", "EXTRACT_BATCH", "EXTRACTUM", "The established Y/CHEO/OR values give a cleaner composition than 'plant tips'."),
    "f3c23f42baf625639e1e": rev("CTH_READY+AIIN_MEASURE", "CTH=bereit; AIIN=Sollmaß", "Bereitmaß", "Auf Bereitmaß bringen", "CTH_AIIN", "MENSURA PARATA", "Visible CTH+AIIN now composes instead of importing the object 'herb'."),
    "af816c04e65874a0f2fa": rev("QOCTHOLY_PRESS_WHOLE", "QOCTHOLY=pressen", "pressen", "Pressen", "PREPARATION_ACTION", "EXPRIME", "Shorten the action to its workshop core."),
    "834825c61d048a6b5628": rev("HO_INGREDIENT+AIIN_MEASURE", "HO=Zutat; AIIN=Sollmaß", "Zutatenmaß", "Zutatenmaß entnehmen", "HO_AIIN", "MENSURA SPECIEI", "The former ulcer meaning conflicts with the already selected HO and AIIN components."),
    "953ad19b79517fc8a211": rev("TSHOL_FLOWERING_HERB_WHOLE", "TSHOL=Blütenkraut", "Blütenkraut", "Blütenkraut nehmen", "PLANT_PART", "HERBA FLORIDA", "Keep the material class but remove the invented first-spring date from the card."),
    "577c03a928d674d420d7": rev("SHOYTY_FLOWER_RESERVE_WHOLE", "SHOYTY=Blütenreserve", "Blütenreserve", "Blütenreserve zurücklegen", "PLANT_PART", "FLORES RESERVATI", "One compact stored-material noun replaces a full future-use instruction."),
    "a48efd6c4491a046ba78": rev("OT_FOLLOW+CHY_ITEM", "OT=Folge; CHY=dies", "Folgeposten", "Die Blütenreserve als Folgeposten nehmen", "OT_Y", "ITEM SEQUENS", "Use the productive order/current-item grammar; flower identity is inherited from the preceding reserve."),
    "403c1592f918c8f23b88": rev("Y_ITEM+AIN_PORTION", "Y=dies; AIN=Portion", "Postenportion", "Eine Postenportion", "Y_AIN", "PARS EIUS", "Compact Y+AIN quantity compound."),
    "d929a14ec45749b2e805": rev("Y_ITEM+AIN_PORTION", "Y=dies; AIN=Portion", "dieser Anteil", "Diesen Anteil", "Y_AIN", "HAEC PARS", "Second learned realization of the same current-item portion."),
    "f7dc90b2c31fd341f0a4": rev("Y_ITEM+AIIN_MEASURE", "Y=dies; AIIN=Sollmaß", "Postenmaß", "Nach Postenmaß", "Y_AIIN", "MENSURA EIUS", "Compact Y+AIIN measure compound."),
    "0ec6a45e2950e8e7061d": rev("HO_INGREDIENT+AL_TO+Y_ITEM", "HO=Zutat; AL=an/zu; Y=dies", "Zutat dorthin", "Diese Zutat dorthin geben", "HO_AL_Y", "SPECIES AD", "Replace the unsupported flowering-time gloss with the selected ingredient/target/current-item composition."),
    "893c570f3fa3fce99711": rev("KCHOL_LAY_WHOLE", "KCHOL=auflegen", "auflegen", "Auflegen", "APPLICATION_ACTION", "APPONE", "Keep only the action; poultice is a local expansion."),
    "ad3581d3144f69a5912d": rev("SH_STALK_WHOLE", "SH=Stängel", "Stängel", "Stängel nehmen", "PLANT_PART", "CAULIS", "The pictured Herbal context supports a concrete short part name better than generic plant part."),
    "b74e9e65637b7c8538dd": rev("KCHEY_GRIND_WHOLE", "KCHEY=zerreiben", "zerreiben", "Zerreiben", "PREPARATION_ACTION", "TERE", "Remove the unsupported adverb 'coarsely'."),
    "c71c72da4e09e0833392": rev("K_HULL+CHEO_EXTRACT+AR_FROM", "CHEO=Auszug; AR=aus/von", "Auszug daraus", "Den Auszug daraus nehmen", "EXTRACT_FROM", "EXTRACTUM EX", "Use the established extract and source relation instead of a purpose-loaded 'use extract'."),
    "61a075bc54793c1c781f": rev("SOTODAN_APPLY_WHOLE", "SOTODAN=anwenden", "anwenden", "Anwenden", "APPLICATION_ACTION", "UTERE", "Remove the invented dry-cough indication from the card."),
}


HERBAL_SENTENCES = {
    "H1-S001": "Nimm die Wurzel der abgebildeten Pflanze aus dem bereitgestellten Ansatz, zerkleinere sie, gib sie in das Gefäß, lass Wasser zulaufen und sammle den Auszug; setze ihn nach Sollmaß an und verwahre den Wurzelrest",
    "H1-S002": "Setze den Posten an, wärme ihn an, führe ihn weiter und halte ihn bereit",
    "H2-S001": "Bereite aus der abgebildeten Pflanze einen Auszugsansatz, bring ihn auf Bereitmaß, presse ihn aus und teile den gewonnenen Posten nach Sollmaß",
    "H2-S002": "Führe den Folgeansatz und seinen Fortsetzungsposten weiter und nimm daraus das Sollmaß",
    "H2-S003": "Gib den Ansatz in den Topf, bearbeite ihn bis zur weichen Zielstufe und entnimm das Zutatenmaß",
    "H3-S001": "Bereite aus dem Blütenkraut einen Weinsud, wringe ihn aus, lass ihn für das Standmaß stehen, seih nach, nimm den Klarauszug und kühle ihn ab",
    "H3-S002": "Lege eine Blütenreserve zurück",
    "H3-S003": "Bereite aus dem Fortsetzungsposten einen Trank nach Sollmaß",
    "H3-S004": "Nimm die Blütenreserve als Folgeposten, setze die Fortsetzung an und halte sie bereit",
    "H4-S001": "Stelle das Sollmaß ein, nimm eine Postenportion und kühle diesen Anteil ab",
    "H4-S002": "Setze den Posten nach Sollmaß um und verwahre ihn",
    "H4-S003": "Nimm den Auszug daraus nach Postenmaß, wärme ihn länger und schließe die Fortsetzung",
    "H4-S004": "Gib nach Sollmaß eine Ansatzportion dorthin, wärme sie an und halte den Posten im Ansatz",
    "H5-S001": "Bereite einen Zutatenansatz, gib die Zutat dorthin nach Sollmaß, lege die nächste Zutat auf, beginne den Folgeansatz und setze den Posten dort an",
    "H5-S002": "Wasche die bezeichnete Stelle, setze den Fortsetzungsposten an und trage ihn auf",
    "H5-S003": "Nimm die Stängel als Zutat, zerreibe sie und setze sie erneut an",
    "H5-S004": "Setze den Posten an, gib den Auszug zu und seih ab",
    "H5-S005": "Setze die Zutat an, nimm den Auszug daraus und wende ihn an",
    "H5-S006": "Wähle den Folgeposten und gib je Gabe das Sollmaß",
}


COMPONENTS = [
    ("CTH+OR", "ANSATZ BEREIT", "PARATUM", "CTHOOR", "productive state + batch"),
    ("CTH+AIIN", "BEREITMASS", "MENSURA PARATA", "CTHAIIN", "productive state + measure"),
    ("Y+CHEO+OR", "AUSZUGSANSATZ", "EXTRACTUM", "YCHEOR", "productive item + extract + batch"),
    ("HO+OR", "ZUTATENANSATZ", "COMPOSITUM SPECIERUM", "CHOCHOR", "productive ingredient + batch"),
    ("HO+AIIN", "ZUTATENMASS", "MENSURA SPECIEI", "CHODAIIN", "productive ingredient + measure"),
    ("HO+AL+Y", "ZUTAT DORTHIN", "SPECIES AD", "CHODALY", "productive ingredient + target + item"),
    ("Y+AIN", "POSTENPORTION", "PARS EIUS", "YKAIN / YKAN", "productive item + portion"),
    ("Y+AIIN", "POSTENMASS", "MENSURA EIUS", "YKAIIN", "productive item + measure"),
    ("OT+Y", "FOLGEPOSTEN", "ITEM SEQUENS", "QOTCHY / OTCHEY", "productive order + item"),
    ("DCHEY", "WURZEL", "RADIX", "DCHEY", "learned plant-part sign"),
    ("ETYD", "WURZELREST", "RELIQUUM RADICIS", "ETYD", "learned plant-part sign"),
    ("TSHOL", "BLÜTENKRAUT", "HERBA FLORIDA", "TSHOL", "learned plant-part sign"),
    ("SHOYTY", "BLÜTENRESERVE", "FLORES RESERVATI", "SHOYTY", "learned stored-material sign"),
    ("SH", "STÄNGEL", "CAULIS", "SH", "learned plant-part sign"),
    ("SCHOAL", "WEINSUD", "DECOCTUM IN VINO", "SCHOAL", "learned preparation sign"),
    ("KCHY", "TRANK", "POTUS", "KCHY", "learned product sign"),
    ("QOCTHOLY", "PRESSEN", "EXPRIME", "QOCTHOLY", "learned action sign"),
    ("CFHY", "AUSWRINGEN", "EXTORQUE", "CFHY", "learned action sign"),
    ("CPHY", "NACHSEIHEN", "COLA ITERUM", "CPHY", "learned action sign"),
    ("KCHEY", "ZERREIBEN", "TERE", "KCHEY", "learned action sign"),
    ("KCHOL", "AUFLEGEN", "APPONE", "KCHOL", "learned action sign"),
    ("SOTODAN", "ANWENDEN", "UTERE", "SOTODAN", "learned action sign"),
    ("TALAM", "VERWAHREN", "SERVA", "TALAM", "learned action sign"),
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
            herbal_previous_segmentation=original["semantic_segmentation"],
            herbal_previous_nucleus_de=original["stable_concrete_nucleus_de"],
            herbal_previous_gloss_de=original["concrete_word_reading_de"],
            herbal_revision="UNCHANGED",
            herbal_family="CARRIED_FORWARD",
            herbal_latin_mnemonic="",
            herbal_reason="Vessel/tool edition retained.",
        )
        chosen = REVISIONS.get(row["joint_tuple_id"])
        if chosen:
            row["semantic_segmentation"] = chosen["seg"]
            row["stable_concrete_nucleus_de"] = chosen["nucleus"]
            row["concrete_word_reading_de"] = chosen["gloss"]
            row["reading_type"] = "HERBAL_MATERIAL__" + chosen["family"]
            row["local_expansion_examples_de"] = "Herbal-Werkstattfassung: " + chosen["context"]
            row["herbal_revision"] = "REVISED"
            row["herbal_family"] = chosen["family"]
            row["herbal_latin_mnemonic"] = chosen["latin"]
            row["herbal_reason"] = chosen["reason"]
        out_dictionary.append(row)
    dmap = {row["joint_tuple_id"]: row for row in out_dictionary}

    out_events: list[dict[str, str]] = []
    for original in events:
        row = dict(original)
        row.update(
            herbal_previous_segmentation=original["semantic_segmentation"],
            herbal_previous_nucleus_de=original["stable_concrete_nucleus_de"],
            herbal_previous_gloss_de=original["concrete_word_reading_de"],
            herbal_previous_context_de=original["contextual_event_reading_de"],
            herbal_revision="UNCHANGED",
            herbal_family="CARRIED_FORWARD",
            herbal_reason="Vessel/tool edition retained.",
        )
        chosen = REVISIONS.get(row["joint_tuple_id"])
        if chosen:
            drow = dmap[row["joint_tuple_id"]]
            row["semantic_segmentation"] = drow["semantic_segmentation"]
            row["stable_concrete_nucleus_de"] = drow["stable_concrete_nucleus_de"]
            row["concrete_word_reading_de"] = drow["concrete_word_reading_de"]
            row["contextual_event_reading_de"] = chosen["context"]
            row["herbal_revision"] = "REVISED"
            row["herbal_family"] = chosen["family"]
            row["herbal_reason"] = chosen["reason"]
        out_events.append(row)

    grouped: OrderedDict[str, list[dict[str, str]]] = OrderedDict()
    for event in out_events:
        grouped.setdefault(event["statement_id"], []).append(event)

    out_sentences: list[dict[str, str]] = []
    for statement_id, group in grouped.items():
        base = sentence_base[statement_id]
        row = dict(base)
        changed = [event for event in group if event["herbal_revision"] == "REVISED"]
        row["card_sequence_de"] = " · ".join(event["concrete_word_reading_de"] for event in group)
        row["event_slot_trace"] = " | ".join(f'{event["event_id"]}[{event["workshop_slots"]}]' for event in group)
        row["workshop_sentence_de"] = HERBAL_SENTENCES.get(statement_id, "; ".join(event["contextual_event_reading_de"] for event in group))
        row["herbal_revised_event_count"] = str(len(changed))
        row["herbal_families"] = "|".join(OrderedDict.fromkeys(event["herbal_family"] for event in changed)) or "CARRIED_FORWARD"
        row["herbal_previous_card_sequence_de"] = base["card_sequence_de"]
        row["herbal_previous_workshop_sentence_de"] = base["workshop_sentence_de"]
        out_sentences.append(row)

    records: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in out_sentences:
        records[row["record_unit_id"]].append(row)
    lines = [
        "# Herbal-Material- und Handlungsfassung — elf Records",
        "",
        "Kreative Werkstattlesung: Die fünf Herbal-Artikel sind flüssig gesetzt; die sechs Biological-Records tragen die zuvor gewählte Gerätegrammatik weiter.",
        "",
    ]
    for record in RECORD_ORDER:
        rows = records[record]
        lines.extend([f"## {record} — {rows[0]['page']}", ""])
        for index, row in enumerate(rows, 1):
            lines.append(f"{index}. **{row['statement_id']}** — {row['workshop_sentence_de'].rstrip('.')}.")
        lines.append("")
    RECORD_OUT.write_text("\n".join(lines), encoding="utf-8")

    base_map = {row["joint_tuple_id"]: row for row in dictionary}
    paradigm_rows = []
    for ident, chosen in REVISIONS.items():
        before = base_map[ident]
        after = dmap[ident]
        event_ids = [row["event_id"] for row in out_events if row["joint_tuple_id"] == ident]
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
            "composition_or_nomenclator": "COMPOSITION" if "+" in chosen["seg"] and "WHOLE" not in chosen["seg"] else "LEARNED_WHOLE_SIGN",
            "workshop_reason": chosen["reason"],
        })
    component_rows = [
        {"component_or_whole_sign": a, "selected_value_de": b, "latin_workshop_parallel": c, "current_examples": d, "role_in_mixed_system": e}
        for a, b, c, d, e in COMPONENTS
    ]

    write_tsv(DICT_OUT, out_dictionary)
    write_tsv(EVENT_OUT, out_events)
    write_tsv(SENTENCE_OUT, out_sentences)
    write_tsv(PARADIGM_OUT, paradigm_rows)
    write_tsv(COMPONENT_OUT, component_rows)

    checks = {
        "cards_173": len(out_dictionary) == 173,
        "events_381": len(out_events) == 381,
        "sentences_116": len(out_sentences) == 116,
        "records_11": set(records) == set(RECORD_ORDER),
        "dictionary_ids_unique": len(dmap) == 173,
        "event_ids_unique": len({row["event_id"] for row in out_events}) == 381,
        "all_cards_concrete": all(row["concrete_word_reading_de"] for row in out_dictionary),
        "all_events_readable": all(row["contextual_event_reading_de"] for row in out_events),
        "event_dictionary_match": all(row["concrete_word_reading_de"] == dmap[row["joint_tuple_id"]]["concrete_word_reading_de"] for row in out_events),
        "all_events_in_sentences": sum(int(row["event_count"]) for row in out_sentences) == 381,
        "all_herbal_sentences_rewritten": set(HERBAL_SENTENCES) == {row["statement_id"] for row in out_sentences if row["record_unit_id"].startswith("H")},
        "revisions_exact": {row["joint_tuple_id"] for row in out_dictionary if row["herbal_revision"] == "REVISED"} == set(REVISIONS),
        "old_disease_gloss_removed": all("Geschwür" not in row["concrete_word_reading_de"] and "Husten" not in row["concrete_word_reading_de"] for row in out_dictionary),
        "old_flowering_time_removed": all("Blütebeginn" not in row["concrete_word_reading_de"] for row in out_dictionary),
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
            "revised_events": sum(row["herbal_revision"] == "REVISED" for row in out_events),
            "herbal_sentences_rewritten": len(HERBAL_SENTENCES),
            "components_and_whole_signs": len(component_rows),
        },
        "working_model": "MATERIA-MEDICA ABBREVIATION GRAMMAR + LEARNED PLANT-PART/PRODUCT/ACTION NOMENCLATOR",
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
