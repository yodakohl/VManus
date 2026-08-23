#!/usr/bin/env python3
"""Build the creative quantity/setting register over the state/product edition."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import OrderedDict, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
BASE = HERE.parent / "sidequest_semantic_state_product_completion"

DICT_IN = BASE / "SELECTED_173_STATE_PRODUCT_DICTIONARY.tsv"
EVENT_IN = BASE / "SELECTED_381_STATE_PRODUCT_INTERLINEAR.tsv"
SENTENCE_IN = BASE / "SELECTED_116_STATE_PRODUCT_SENTENCES.tsv"

DICT_OUT = HERE / "SELECTED_173_PARAMETER_SETTING_DICTIONARY.tsv"
EVENT_OUT = HERE / "SELECTED_381_PARAMETER_SETTING_INTERLINEAR.tsv"
SENTENCE_OUT = HERE / "SELECTED_116_PARAMETER_SETTING_SENTENCES.tsv"
RECORD_OUT = HERE / "SELECTED_11_PARAMETER_SETTING_RECORDS.md"
PARADIGM_OUT = HERE / "PARAMETER_SETTING_PARADIGM.tsv"
REGISTER_OUT = HERE / "PARAMETER_SETTING_REGISTER.tsv"
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


REVISIONS = {
    "f3c23f42baf625639e1e": rev(
        "CTH_READY+AIIN_MEASURE",
        "CTH=bereit; AIIN=Sollmaß",
        "Fertigmaß",
        "Bringe den Ansatz auf Fertigmaß",
        "AIIN_MEASURE",
        "MENSURA PARATA",
        "Use a natural compact threshold word for READY+MEASURE.",
    ),
    "a8af08e69edab8e54f15": rev(
        "SHFY_STAND+AIIN_MEASURE",
        "SHFY=stehen; AIIN=Sollmaß",
        "Standmaß",
        "Lass bis zum Standmaß stehen",
        "AIIN_MEASURE",
        "MENSURA STANDI",
        "Keep AIIN as measure; elapsed time is a local expansion of the standing measure.",
    ),
    "d72f71baff01cd0a0406": rev(
        "CHLD_SETTLE+AIIN_MEASURE",
        "CHLD=absetzen; AIIN=Sollmaß",
        "Absetzmaß",
        "Warte bis zum Absetzmaß",
        "AIIN_MEASURE",
        "MENSURA DEPOSITIONIS",
        "Keep AIIN invariant as measure rather than switching to an unrelated stand noun.",
    ),
    "2c82523794dcb7d2b343": rev(
        "IIN_TARGET_STAGE",
        "IIN=Sollstufe",
        "Sollstufe",
        "Bringe auf Sollstufe",
        "IIN_STAGE",
        "GRADUS DEBITUS",
        "Use one stage word that composes with opening and softness modifiers.",
    ),
    "409de02322e7b2ca0c62": rev(
        "K_SOFT+IIN_TARGET_STAGE",
        "K=weich; IIN=Sollstufe",
        "Weichstufe",
        "Bearbeite bis zur Weichstufe",
        "IIN_STAGE",
        "GRADUS MOLLIS",
        "Shorten the phrase while preserving K+IIN composition.",
    ),
    "4eab1841ed655c20a348": rev(
        "SHECKHAL_MIDDLE_MEASURE_WHOLE",
        "SHECKHAL=Mittelmaß",
        "Mittelmaß",
        "Bringe zunächst auf Mittelmaß",
        "LEARNED_MEASURE",
        "MENSURA MEDIA",
        "Replace a descriptive quantity phrase with one learned setting word.",
    ),
    "21ed2873b71e57269c08": rev(
        "CHCKHAL_HOLD_TIME_WHOLE",
        "CHCKHAL=Haltezeit",
        "Haltezeit",
        "Halte für die Haltezeit",
        "LEARNED_DURATION",
        "TEMPUS TENENDI",
        "Specify what the duration controls in its sole application context.",
    ),
    "9bb7122b386ebbc6138f": rev(
        "KEOL_DOSE_WHOLE",
        "KEOL=Gabe",
        "Gabe",
        "Gib die nächste Gabe",
        "LEARNED_DOSE",
        "DOSIS",
        "Remove the sentence-level preposition; sequence supplies 'per'.",
    ),
}


SENTENCE_REWRITES = {
    "H2-S001": "Bereite aus der abgebildeten Pflanze einen Auszugsansatz, bring ihn auf Fertigmaß, presse ihn aus und teile den gewonnenen Posten nach Sollmaß",
    "H2-S003": "Gib den Ansatz in den Topf, bearbeite ihn bis zur Weichstufe und entnimm das Zutatenmaß",
    "H3-S001": "Bereite aus dem Blütenkraut einen Weinsud, wringe ihn aus, lass ihn bis zum Standmaß stehen, seih nach, nimm die Klarflüssigkeit und kühle sie ab",
    "H5-S006": "Wähle für die nächste Gabe den Folgeposten und das Sollmaß",
    "B1-S002": "Stelle das Sollmaß ein, lass Beckenwasser zu, setze dort an, gib eine weitere Portion und Badzusatz hinzu, halte den Fortsetzungsansatz warm, führe ihn bis zum Mittelmaß weiter, stelle das Sollmaß ein, halte dort länger, prüfe erneut das Sollmaß, leite durch, setze um und schließe",
    "B1-S018": "Stelle die Auffangschale bereit, reibe die bezeichnete Stelle ein, bringe sie auf Sollstufe, sammle länger und schließe",
    "B3-S026": "Stelle das Sammelbecken bereit, warte bis zum Absetzmaß, setze um, gib eine Portion zu, halte bereit, warte, bis der Posten klar ist, sammle länger und schließe",
    "B3-S034": "Bringe auf Sollstufe, halte bereit, bearbeite gleichmäßig, stelle das Folgemaß ein, führe unten weiter, lass absetzen und schließe",
    "B4-S015": "Gib eine Portion zu, nimm die Klarflüssigkeit, halte eine Portion für die Haltezeit, sammle kurz, führe ab und schließe",
}


REGISTER = [
    ("PORTION_CORE", "AIN", "PORTION", "PARS", "physical share of the active material"),
    ("PORTION_ADD", "OK+AIN", "PORTION ZUGEBEN", "PONE PARTEM", "add one portion"),
    ("PORTION_MORE", "OL+AIN", "WEITERE PORTION", "PARS ULTERIOR", "continue with another portion"),
    ("BATCH_PORTION", "OR+AIN", "ANSATZPORTION", "PARS COMPOSITI", "portion of the batch"),
    ("ITEM_PORTION", "Y+AIN", "POSTENPORTION", "PARS EIUS", "portion of the current item"),
    ("TRANSFER_PORTION", "CHED+AIN", "PORTION UMSETZEN", "PARTEM TRANSFERE", "transfer a portion"),
    ("MEASURE_CORE", "AIIN", "SOLLMASS", "MENSURA DEBITA", "selected working measure"),
    ("MEASURE_SET", "OK+AIIN", "AUF SOLLMASS EINSTELLEN", "PONE AD MENSURAM", "set the measure"),
    ("MEASURE_NEXT", "OT+AIIN", "FOLGEMASS", "MENSURA SEQUENS", "measure for the following step"),
    ("MEASURE_ITEM", "Y+AIIN", "POSTENMASS", "MENSURA EIUS", "measure of the current item"),
    ("MEASURE_INGREDIENT", "HO+AIIN", "ZUTATENMASS", "MENSURA SPECIEI", "ingredient measure"),
    ("MEASURE_READY", "CTH+AIIN", "FERTIGMASS", "MENSURA PARATA", "ready threshold"),
    ("MEASURE_STAND", "SHFY+AIIN", "STANDMASS", "MENSURA STANDI", "standing threshold"),
    ("MEASURE_SETTLE", "CHLD+AIIN", "ABSETZMASS", "MENSURA DEPOSITIONIS", "settling threshold"),
    ("STAGE_CORE", "IIN", "SOLLSTUFE", "GRADUS DEBITUS", "target process stage"),
    ("STAGE_SOFT", "K+IIN", "WEICHSTUFE", "GRADUS MOLLIS", "softness stage"),
    ("STAGE_OPENING", "DA+IIN", "ÖFFNUNGSSTUFE", "GRADUS APERTURAE", "opening setting"),
    ("MIDDLE_MEASURE", "SHECKHAL", "MITTELMASS", "MENSURA MEDIA", "learned intermediate setting"),
    ("HOLD_TIME", "CHCKHAL", "HALTEZEIT", "TEMPUS TENENDI", "learned duration setting"),
    ("DOSE", "KEOL", "GABE", "DOSIS", "learned administration unit"),
    ("WET_SITE", "LCHEEY", "NASSSTELLE", "LOCUS MADIDUS", "learned application site"),
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
            parameter_previous_segmentation=original["semantic_segmentation"],
            parameter_previous_nucleus_de=original["stable_concrete_nucleus_de"],
            parameter_previous_gloss_de=original["concrete_word_reading_de"],
            parameter_revision="UNCHANGED",
            parameter_family="CARRIED_FORWARD",
            parameter_mnemonic="",
            parameter_reason="State/product edition retained.",
        )
        chosen = REVISIONS.get(row["joint_tuple_id"])
        if chosen:
            row["semantic_segmentation"] = chosen["seg"]
            row["stable_concrete_nucleus_de"] = chosen["nucleus"]
            row["concrete_word_reading_de"] = chosen["gloss"]
            row["reading_type"] = "PARAMETER_SETTING__" + chosen["family"]
            row["local_expansion_examples_de"] = "Einstellfassung: " + chosen["context"]
            row["parameter_revision"] = "REVISED"
            row["parameter_family"] = chosen["family"]
            row["parameter_mnemonic"] = chosen["mnemonic"]
            row["parameter_reason"] = chosen["reason"]
        out_dictionary.append(row)
    dmap = {row["joint_tuple_id"]: row for row in out_dictionary}

    out_events: list[dict[str, str]] = []
    for original in events:
        row = dict(original)
        row.update(
            parameter_previous_segmentation=original["semantic_segmentation"],
            parameter_previous_nucleus_de=original["stable_concrete_nucleus_de"],
            parameter_previous_gloss_de=original["concrete_word_reading_de"],
            parameter_previous_context_de=original["contextual_event_reading_de"],
            parameter_revision="UNCHANGED",
            parameter_family="CARRIED_FORWARD",
            parameter_reason="State/product edition retained.",
        )
        chosen = REVISIONS.get(row["joint_tuple_id"])
        if chosen:
            drow = dmap[row["joint_tuple_id"]]
            row["semantic_segmentation"] = drow["semantic_segmentation"]
            row["stable_concrete_nucleus_de"] = drow["stable_concrete_nucleus_de"]
            row["concrete_word_reading_de"] = drow["concrete_word_reading_de"]
            row["contextual_event_reading_de"] = chosen["context"]
            row["parameter_revision"] = "REVISED"
            row["parameter_family"] = chosen["family"]
            row["parameter_reason"] = chosen["reason"]
        out_events.append(row)

    grouped: OrderedDict[str, list[dict[str, str]]] = OrderedDict()
    for event in out_events:
        grouped.setdefault(event["statement_id"], []).append(event)

    out_sentences: list[dict[str, str]] = []
    for statement_id, group in grouped.items():
        base = sentence_base[statement_id]
        row = dict(base)
        changed = [event for event in group if event["parameter_revision"] == "REVISED"]
        row["card_sequence_de"] = " · ".join(event["concrete_word_reading_de"] for event in group)
        row["event_slot_trace"] = " | ".join(f'{event["event_id"]}[{event["workshop_slots"]}]' for event in group)
        row["workshop_sentence_de"] = SENTENCE_REWRITES.get(statement_id, base["workshop_sentence_de"])
        row["parameter_revised_event_count"] = str(len(changed))
        row["parameter_families"] = "|".join(OrderedDict.fromkeys(event["parameter_family"] for event in changed)) or "CARRIED_FORWARD"
        row["parameter_previous_card_sequence_de"] = base["card_sequence_de"]
        row["parameter_previous_workshop_sentence_de"] = base["workshop_sentence_de"]
        out_sentences.append(row)

    records: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in out_sentences:
        records[row["record_unit_id"]].append(row)
    lines = [
        "# Mengen-, Maß- und Einstellfassung — elf Records",
        "",
        "AIN=Portion, AIIN=Maß und IIN=Stufe bleiben in jeder produktiven Verbindung getrennt.",
        "",
    ]
    for record in RECORD_ORDER:
        rows = records[record]
        lines.extend([f"## {record} — {rows[0]['page']}", ""])
        lines.append(". ".join(row["workshop_sentence_de"].rstrip(". ") for row in rows) + ".")
        lines.extend(["", "### Einzelanweisungen", ""])
        for index, row in enumerate(rows, 1):
            lines.append(f"{index}. **{row['statement_id']}** — {row['workshop_sentence_de'].rstrip('.') }.")
        lines.append("")
    RECORD_OUT.write_text("\n".join(lines), encoding="utf-8")

    base_map = {row["joint_tuple_id"]: row for row in dictionary}
    paradigm_rows = []
    for ident, chosen in REVISIONS.items():
        before = base_map[ident]
        after = dmap[ident]
        selected_events = [row for row in out_events if row["joint_tuple_id"] == ident]
        paradigm_rows.append({
            "joint_tuple_id": ident,
            "surface_family": after["surface_family"],
            "occurrences": after["occurrences"],
            "records": after["records"],
            "previous_default_de": before["concrete_word_reading_de"],
            "selected_default_de": after["concrete_word_reading_de"],
            "selected_segmentation": after["semantic_segmentation"],
            "parameter_family": chosen["family"],
            "workshop_mnemonic": chosen["mnemonic"],
            "event_ids": "|".join(row["event_id"] for row in selected_events),
            "statement_ids": "|".join(OrderedDict.fromkeys(row["statement_id"] for row in selected_events)),
            "workshop_reason": chosen["reason"],
        })
    register_rows = [
        {"parameter_role": a, "card_or_component": b, "selected_value_de": c, "ca_1420_teaching_parallel": d, "workshop_use": e}
        for a, b, c, d, e in REGISTER
    ]

    write_tsv(DICT_OUT, out_dictionary)
    write_tsv(EVENT_OUT, out_events)
    write_tsv(SENTENCE_OUT, out_sentences)
    write_tsv(PARADIGM_OUT, paradigm_rows)
    write_tsv(REGISTER_OUT, register_rows)

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
        "revisions_exact": {row["joint_tuple_id"] for row in out_dictionary if row["parameter_revision"] == "REVISED"} == set(REVISIONS),
        "sentence_rewrites_exact": len(SENTENCE_REWRITES) == 9,
        "aiin_measure_invariant": all("AIIN" not in row["semantic_segmentation"] or "maß" in row["stable_concrete_nucleus_de"].lower() for row in out_dictionary if row["joint_tuple_id"] in {"2f1c5e56e8f0ff459065", "f3c23f42baf625639e1e", "a8af08e69edab8e54f15", "d72f71baff01cd0a0406"}),
        "iin_stage_invariant": dmap["2c82523794dcb7d2b343"]["concrete_word_reading_de"] == "Sollstufe" and dmap["409de02322e7b2ca0c62"]["concrete_word_reading_de"] == "Weichstufe" and dmap["fcc1deda9e24ec268eb0"]["concrete_word_reading_de"] == "Öffnungsstufe",
        "ain_portion_retained": dmap["9da1b6ac2c929daea697"]["concrete_word_reading_de"] == "eine Portion",
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
            "revised_events": sum(row["parameter_revision"] == "REVISED" for row in out_events),
            "rewritten_sentences": len(SENTENCE_REWRITES),
            "register_rows": len(register_rows),
        },
        "working_model": "AIN=PORTION; AIIN=MEASURE; IIN=STAGE + LEARNED DURATION/DOSE/SITE SETTINGS",
        "sealed": {"f84": True, "f84r": True},
    }
    CHECK_OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))

    outputs = [DICT_OUT, EVENT_OUT, SENTENCE_OUT, RECORD_OUT, PARADIGM_OUT, REGISTER_OUT, CHECK_OUT]
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
