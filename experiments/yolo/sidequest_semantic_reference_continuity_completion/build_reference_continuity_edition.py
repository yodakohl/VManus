#!/usr/bin/env python3
"""Build the creative reference/continuity layer over the parameter edition."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import OrderedDict, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
BASE = HERE.parent / "sidequest_semantic_parameter_setting_completion"

DICT_IN = BASE / "SELECTED_173_PARAMETER_SETTING_DICTIONARY.tsv"
EVENT_IN = BASE / "SELECTED_381_PARAMETER_SETTING_INTERLINEAR.tsv"
SENTENCE_IN = BASE / "SELECTED_116_PARAMETER_SETTING_SENTENCES.tsv"

DICT_OUT = HERE / "SELECTED_173_REFERENCE_CONTINUITY_DICTIONARY.tsv"
EVENT_OUT = HERE / "SELECTED_381_REFERENCE_CONTINUITY_INTERLINEAR.tsv"
SENTENCE_OUT = HERE / "SELECTED_116_REFERENCE_CONTINUITY_SENTENCES.tsv"
RECORD_OUT = HERE / "SELECTED_11_REFERENCE_CONTINUITY_RECORDS.md"
PARADIGM_OUT = HERE / "REFERENCE_CONTINUITY_PARADIGM.tsv"
REGISTER_OUT = HERE / "REFERENCE_CONTINUITY_REGISTER.tsv"
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
    "b921a237be883a820352": rev(
        "Y_CURRENT_ITEM_CARD",
        "Y=dieser aktuell gemeinte Posten",
        "dieser Posten",
        "Nimm diesen Posten",
        "CURRENT_ITEM",
        "HOC",
        "Shorten the recurrent referent without changing its function.",
    ),
    "d665560c8ff80799a82c": rev(
        "DCHOL_SCHOL_PREVIOUS_ITEM_WHOLE",
        "DCHOL~SCHOL=Vorposten",
        "Vorposten",
        "Nimm den Vorposten",
        "PREVIOUS_ITEM",
        "ITEM PRAECEDENS",
        "Both Herbal occurrences retrieve material established in the preceding local clause.",
    ),
    "5d5e0b288cf36864ed9d": rev(
        "OT_FOLLOW+GRADE_2+Y_ITEM",
        "OT=Folge; EE=länger; Y=Posten",
        "langer Folgeposten",
        "Nimm den langen Folgeposten",
        "NEXT_ITEM",
        "ITEM SEQUENS LONGUM",
        "Use a compact graded item name rather than a comparative sentence fragment.",
    ),
    "b6b654722e55729cc947": rev(
        "OT_NEXT+AR_FROM",
        "OT=danach; AR=aus/von",
        "danach von dort",
        "Führe danach von dort weiter",
        "NEXT_SOURCE",
        "DEINDE EX EO",
        "Keep AR as a source relation instead of turning it into a new outlet noun.",
    ),
    "7811a7daff25d476e28d": rev(
        "OLS_BELOW+AL_TO+Y_ITEM",
        "OLS=unten; AL=an/zu; Y=dies",
        "untere Zielstelle",
        "Führe zur unteren Zielstelle",
        "LOWER_TARGET",
        "LOCUS INFERIOR",
        "The compound names the target, not merely the adverb 'below'.",
    ),
    "97ddca78c9ebcc956d04": rev(
        "LD_END+AL_TO",
        "LD=Ende; AL=an/zu",
        "Endziel",
        "Führe zum Endziel",
        "FINAL_TARGET",
        "LOCUS FINALIS",
        "Shorten final site to the role it plays in the route.",
    ),
}


SENTENCE_REWRITES = {
    "H3-S003": "Bereite aus dem Vorposten einen Trank nach Sollmaß",
    "H5-S002": "Wasche die bezeichnete Stelle, setze den Vorposten an und trage ihn auf",
    "B1-S014": "Setze zur Arbeitsstelle um, führe am Auslass ab und führe danach von dort weiter",
    "B2-S006": "Nimm den langen Folgeposten, setze ihn dort am Überlauf an und führe ihn weiter",
    "B2-S016": "Führe ihn dorthin und von dort ab, teile gleich, stelle das Sollmaß ein, nimm den langen Folgeposten, setze kurz an, führe ein und schließe",
    "B3-S034": "Bringe auf Sollstufe, halte bereit, bearbeite gleichmäßig, stelle das Folgemaß ein, führe zur unteren Zielstelle, lass absetzen und schließe",
    "B6-S001": "Sammle den rohen Posten länger, öffne den Seitenarm, führe nach Sollmaß weiter, lege das Tuch ein und führe den Posten zum Endziel",
}


REGISTER = [
    ("CURRENT_ITEM", "Y~CHY", "DIESER POSTEN", "HOC", "retrieve the currently active item"),
    ("CURRENT_PORTION", "Y+AIN", "POSTENPORTION", "PARS EIUS", "portion of the current item"),
    ("CURRENT_MEASURE", "Y+AIIN", "POSTENMASS", "MENSURA EIUS", "measure of the current item"),
    ("CURRENT_TARGET", "HO+AL+Y", "DIESE ZUTAT DORTHIN", "SPECIES HAEC AD", "ingredient plus target plus current referent"),
    ("SOURCE", "AR", "DARAUS / VON DORT", "EX EO", "retrieve from the active source"),
    ("EXTRACT_FROM", "CHEO+AR", "AUSZUG DARAUS", "EXTRACTUM EX EO", "extract from the active source"),
    ("SET_FROM", "OK+AR", "DARAUS ANSETZEN", "PONE EX EO", "start from the active source"),
    ("NEXT_SOURCE", "OT+AR", "DANACH VON DORT", "DEINDE EX EO", "continue from the next source point"),
    ("TARGET", "AL", "DORTHIN / ZUM ZIEL", "AD EUM", "send to the active target"),
    ("SET_TO", "OK+AL", "DORT ANSETZEN", "PONE AD", "place at target"),
    ("NEXT_TARGET", "OT+AL", "DANACH DORTHIN", "DEINDE AD", "advance to next target"),
    ("LOWER_TARGET", "OLS+AL+Y", "UNTERE ZIELSTELLE", "LOCUS INFERIOR", "lower target of current item"),
    ("FINAL_TARGET", "LD+AL", "ENDZIEL", "LOCUS FINALIS", "final route target"),
    ("SAME_OPERATION", "OL", "FORTSETZEN", "PROSEQUERE", "continue the same operation"),
    ("CONTINUED_BATCH", "OL+OR", "FORTSETZUNGSANSATZ", "COMPOSITUM CONTINUATUM", "continue the same batch"),
    ("FURTHER_PORTION", "OL+AIN", "WEITERE PORTION", "PARS ULTERIOR", "continue with another portion"),
    ("CONTINUE_CLOSE", "OL+DY / OL+CHED+close", "FORTSETZEN; SCHLUSS", "PROSEQUERE ET CLAUDE", "continue and close local cell"),
    ("NEXT_OPERATION", "OT", "FOLGE", "SEQUENS", "advance to next operation"),
    ("NEXT_ITEM", "OT+Y", "FOLGEPOSTEN", "ITEM SEQUENS", "next active item"),
    ("LONG_NEXT_ITEM", "OT+EE+Y", "LANGER FOLGEPOSTEN", "ITEM SEQUENS LONGUM", "long-grade next item"),
    ("NEXT_BATCH", "OT+OR", "FOLGEANSATZ", "COMPOSITUM SEQUENS", "next batch"),
    ("NEXT_MEASURE", "OT+AIIN", "FOLGEMASS", "MENSURA SEQUENS", "measure for next operation"),
    ("NEXT_TRANSFER", "OT+CHED", "FOLGEUMSETZUNG", "TRANSFERTIO SEQUENS", "next transfer"),
    ("PREVIOUS_ITEM", "DCHOL~SCHOL", "VORPOSTEN", "ITEM PRAECEDENS", "learned anaphoric item sign"),
    ("REMAINDER", "LO", "REST", "RELIQUUM", "remaining material"),
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
            reference_previous_segmentation=original["semantic_segmentation"],
            reference_previous_nucleus_de=original["stable_concrete_nucleus_de"],
            reference_previous_gloss_de=original["concrete_word_reading_de"],
            reference_revision="UNCHANGED",
            reference_family="CARRIED_FORWARD",
            reference_mnemonic="",
            reference_reason="Parameter/setting edition retained.",
        )
        chosen = REVISIONS.get(row["joint_tuple_id"])
        if chosen:
            row["semantic_segmentation"] = chosen["seg"]
            row["stable_concrete_nucleus_de"] = chosen["nucleus"]
            row["concrete_word_reading_de"] = chosen["gloss"]
            row["reading_type"] = "REFERENCE_CONTINUITY__" + chosen["family"]
            row["local_expansion_examples_de"] = "Referenzfassung: " + chosen["context"]
            row["reference_revision"] = "REVISED"
            row["reference_family"] = chosen["family"]
            row["reference_mnemonic"] = chosen["mnemonic"]
            row["reference_reason"] = chosen["reason"]
        out_dictionary.append(row)
    dmap = {row["joint_tuple_id"]: row for row in out_dictionary}

    out_events: list[dict[str, str]] = []
    for original in events:
        row = dict(original)
        row.update(
            reference_previous_segmentation=original["semantic_segmentation"],
            reference_previous_nucleus_de=original["stable_concrete_nucleus_de"],
            reference_previous_gloss_de=original["concrete_word_reading_de"],
            reference_previous_context_de=original["contextual_event_reading_de"],
            reference_revision="UNCHANGED",
            reference_family="CARRIED_FORWARD",
            reference_reason="Parameter/setting edition retained.",
        )
        chosen = REVISIONS.get(row["joint_tuple_id"])
        if chosen:
            drow = dmap[row["joint_tuple_id"]]
            row["semantic_segmentation"] = drow["semantic_segmentation"]
            row["stable_concrete_nucleus_de"] = drow["stable_concrete_nucleus_de"]
            row["concrete_word_reading_de"] = drow["concrete_word_reading_de"]
            row["contextual_event_reading_de"] = chosen["context"]
            row["reference_revision"] = "REVISED"
            row["reference_family"] = chosen["family"]
            row["reference_reason"] = chosen["reason"]
        out_events.append(row)

    grouped: OrderedDict[str, list[dict[str, str]]] = OrderedDict()
    for event in out_events:
        grouped.setdefault(event["statement_id"], []).append(event)

    out_sentences: list[dict[str, str]] = []
    for statement_id, group in grouped.items():
        base = sentence_base[statement_id]
        row = dict(base)
        changed = [event for event in group if event["reference_revision"] == "REVISED"]
        row["card_sequence_de"] = " · ".join(event["concrete_word_reading_de"] for event in group)
        row["event_slot_trace"] = " | ".join(f'{event["event_id"]}[{event["workshop_slots"]}]' for event in group)
        row["workshop_sentence_de"] = SENTENCE_REWRITES.get(statement_id, base["workshop_sentence_de"])
        row["reference_revised_event_count"] = str(len(changed))
        row["reference_families"] = "|".join(OrderedDict.fromkeys(event["reference_family"] for event in changed)) or "CARRIED_FORWARD"
        row["reference_previous_card_sequence_de"] = base["card_sequence_de"]
        row["reference_previous_workshop_sentence_de"] = base["workshop_sentence_de"]
        out_sentences.append(row)

    records: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in out_sentences:
        records[row["record_unit_id"]].append(row)
    lines = [
        "# Referenz- und Fortsetzungsfassung — elf Records",
        "",
        "Y=jetzt, AR=von dort, AL=dorthin, OL=denselben Gang fortsetzen, OT=zum nächsten Gang wechseln.",
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
            "reference_family": chosen["family"],
            "workshop_mnemonic": chosen["mnemonic"],
            "event_ids": "|".join(row["event_id"] for row in selected_events),
            "statement_ids": "|".join(OrderedDict.fromkeys(row["statement_id"] for row in selected_events)),
            "workshop_reason": chosen["reason"],
        })
    register_rows = [
        {"reference_role": a, "card_or_component": b, "selected_value_de": c, "ca_1420_teaching_parallel": d, "workshop_use": e}
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
        "revisions_exact": {row["joint_tuple_id"] for row in out_dictionary if row["reference_revision"] == "REVISED"} == set(REVISIONS),
        "sentence_rewrites_exact": len(SENTENCE_REWRITES) == 7,
        "y_short": dmap["b921a237be883a820352"]["concrete_word_reading_de"] == "dieser Posten",
        "previous_item": dmap["d665560c8ff80799a82c"]["concrete_word_reading_de"] == "Vorposten",
        "source_target_preserved": dmap["4d4559019a961b834aa1"]["concrete_word_reading_de"] == "daraus" and dmap["dd0ecaf5e27d81befffc"]["concrete_word_reading_de"] == "dorthin",
        "ol_ot_preserved": dmap["dcda95c81a5460feb191"]["concrete_word_reading_de"] == "fortsetzen" and dmap["a48efd6c4491a046ba78"]["concrete_word_reading_de"] == "Folgeposten",
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
            "revised_events": sum(row["reference_revision"] == "REVISED" for row in out_events),
            "rewritten_sentences": len(SENTENCE_REWRITES),
            "register_rows": len(register_rows),
        },
        "working_model": "Y=CURRENT; AR=FROM; AL=TO; OL=SAME/CONTINUE; OT=NEXT + LEARNED PREVIOUS/FINAL ITEM SIGNS",
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
