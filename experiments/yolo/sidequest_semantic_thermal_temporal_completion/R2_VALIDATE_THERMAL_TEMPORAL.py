#!/usr/bin/env python3
"""Validate R2's complete thermal/temporal creative edition."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
DICT_PATH = HERE / "R2_173_DICTIONARY.tsv"
EVENT_PATH = HERE / "R2_381_INTERLINEAR.tsv"
SENTENCE_PATH = HERE / "R2_116_SENTENCES.tsv"
RECORD_PATH = HERE / "R2_11_RECORDS.md"
PARADIGM_PATH = HERE / "R2_PARADIGM.tsv"
SUMMARY_PATH = HERE / "R2_BUILD_SUMMARY.json"
VALIDATION_PATH = HERE / "R2_VALIDATION.json"

ALLOWED_PAGES = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"}

E_SHORT_IDS = {
    "08bd5ca0c2ad137a056d", "7db18b2f0fb7ed0fcfd3", "c45ebac60774620561e2",
    "42cdc187d5b9ffc60063", "bc4f1f5c006c74a4d26d", "d904bf7b044dd3922781",
    "6b89d6dd70635bc60fe0",
}
EE_HOLD_IDS = {
    "0275fbf14e07935b0a45", "7d25241b0e56c836372a", "5d5e0b288cf36864ed9d",
    "ff178343c18e287ce3b7", "93f69c38fdedee1598e9", "1bfd786e6b8b63734a59",
    "3b70942557b3a40e8030", "03626ca94cb17800d767", "a84fbe3ad380df345b97",
    "f0db6d30cd34f4cb2a4d", "2c1a5fd92b9e3c762242", "daf32e6db9e04413ce7f",
}
EEE_FULL_IDS = {"d25110e0d8488927278f"}
CHK_IDS = {"d904bf7b044dd3922781", "2c1a5fd92b9e3c762242", "f0db6d30cd34f4cb2a4d", "a84fbe3ad380df345b97"}
IIN_IDS = {"2c82523794dcb7d2b343", "409de02322e7b2ca0c62", "fcc1deda9e24ec268eb0"}
SHED_IDS = {"bc4f1f5c006c74a4d26d", "03626ca94cb17800d767", "abb23e5e6936b4147f76", "daa1347f456415fe8737", "db167f8e9b53eefb58f8"}
CTH_IDS = {"e0b630cb1b5df5e7105b", "6b89d6dd70635bc60fe0"}
OT_IDS = {
    "10488b911aae52b3b334", "497cbd9c7401810ff56b", "4de12cf322dfb76ded1e",
    "54d0e228ca346110af05", "601b77449028deed39de", "90bcf0a9ec0ef56399e6",
    "b6b654722e55729cc947", "faf321940aed922846a9", "c45ebac60774620561e2",
    "5d5e0b288cf36864ed9d", "ff178343c18e287ce3b7",
}
OL_IDS = {
    "1b1ffdd869fb1429ad03", "232195d6ff2f326322f7", "28ffbc88b97772a75f1e",
    "322281bd391aa621f568", "94df4847b7b16c98394a", "dcda95c81a5460feb191",
    "d665560c8ff80799a82c", "dec401773c1f0347793d", "daf32e6db9e04413ce7f",
    "daa1347f456415fe8737",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def require(condition: bool, message: str, checks: list[str]) -> None:
    if not condition:
        raise AssertionError(message)
    checks.append(message)


def main() -> dict[str, object]:
    checks: list[str] = []
    dictionary = read_tsv(DICT_PATH)
    events = read_tsv(EVENT_PATH)
    sentences = read_tsv(SENTENCE_PATH)
    paradigm = read_tsv(PARADIGM_PATH)
    summary = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))

    require(len(dictionary) == 173, "dictionary has exactly 173 cards", checks)
    require(len(events) == 381, "interlinear has exactly 381 events", checks)
    require(len(sentences) == 116, "sentence table has exactly 116 statements", checks)
    require(len({row["record_unit_id"] for row in events}) == 11, "event table has exactly 11 records", checks)
    require(len({row["joint_tuple_id"] for row in dictionary}) == 173, "dictionary card IDs are unique", checks)
    require(len({row["event_id"] for row in events}) == 381, "event IDs are unique", checks)
    require(len({row["statement_id"] for row in sentences}) == 116, "statement IDs are unique", checks)
    require({row["page"] for row in events} <= ALLOWED_PAGES, "only fixed prose pages occur", checks)
    require(all(not row["page"].lower().startswith("f84") for row in events), "f84 and f84r have no event", checks)

    for field in ("semantic_segmentation", "stable_concrete_nucleus_de", "concrete_word_reading_de", "reading_type"):
        require(all(row[field].strip() for row in dictionary), f"dictionary field {field} has no blank default", checks)
    for field in ("semantic_segmentation", "stable_concrete_nucleus_de", "concrete_word_reading_de", "contextual_event_reading_de"):
        require(all(row[field].strip() for row in events), f"event field {field} has no blank value", checks)

    by_id = {row["joint_tuple_id"]: row for row in dictionary}
    require(all(row["joint_tuple_id"] in by_id for row in events), "every event resolves to a dictionary card", checks)
    for row in events:
        card = by_id[row["joint_tuple_id"]]
        for field in ("semantic_segmentation", "stable_concrete_nucleus_de", "concrete_word_reading_de"):
            if row[field] != card[field]:
                raise AssertionError(f"event/card mismatch {row['event_id']} {field}")
    checks.append("every event repeats its exact current card default")

    changed_cards = [row for row in dictionary if row["r2_thermal_family"] != "UNCHANGED"]
    changed_events = [row for row in events if row["r2_thermal_family"] != "UNCHANGED"]
    changed_sentences = [row for row in sentences if int(row["r2_thermal_revised_event_count"]) > 0]
    require(len(changed_cards) == 56, "exactly 56 target cards are revised", checks)
    require(len(changed_events) == 138, "exactly 138 target events are revised", checks)
    require(len(changed_sentences) == 80, "exactly 80 statements contain a revision", checks)
    require(all(row["r2_thermal_previous_segmentation"].strip() for row in changed_cards), "every revised card retains prior segmentation provenance", checks)
    require(all(row["r2_thermal_previous_context_de"].strip() for row in changed_events), "every revised event retains prior context provenance", checks)

    require(all("E=Kurzgrad" in by_id[ident]["stable_concrete_nucleus_de"] for ident in E_SHORT_IDS), "E is invariantly Kurzgrad in all selected productive hosts", checks)
    require(all("EE=Haltegrad" in by_id[ident]["stable_concrete_nucleus_de"] for ident in EE_HOLD_IDS), "EE is invariantly Haltegrad in all selected productive hosts", checks)
    require(all("EEE=Vollgrad" in by_id[ident]["stable_concrete_nucleus_de"] for ident in EEE_FULL_IDS), "EEE is Vollgrad in its complete host", checks)
    require(all("CHK=wärmen" in by_id[ident]["stable_concrete_nucleus_de"] for ident in CHK_IDS), "CHK is invariantly wärmen across four cards", checks)
    require(all("IIN=Grad" in by_id[ident]["stable_concrete_nucleus_de"] for ident in IIN_IDS), "IIN is invariantly Grad across three cards", checks)
    require(all("SHED=absetzen" in by_id[ident]["stable_concrete_nucleus_de"] for ident in SHED_IDS), "SHED is invariantly absetzen across five cards", checks)
    require(all("CTH=bereit" in by_id[ident]["stable_concrete_nucleus_de"] for ident in CTH_IDS), "CTH is invariantly bereit in its productive cards", checks)
    require(all("OT=Folge" in by_id[ident]["stable_concrete_nucleus_de"] for ident in OT_IDS), "OT is invariantly Folge across eleven compositions", checks)
    require(all("OL=Fortsetzung" in by_id[ident]["stable_concrete_nucleus_de"] for ident in OL_IDS), "OL is invariantly Fortsetzung across ten compositions", checks)

    require(by_id["2f1c5e56e8f0ff459065"]["stable_concrete_nucleus_de"] == "AIIN=vorgeschriebenes Maß", "AIIN remains measure and is not collapsed into IIN grade", checks)
    require(by_id["cb57b696b815fdef9cb7"]["concrete_word_reading_de"] == "temperiert", "SHECTHY remains an indivisible tempered whole card", checks)
    require(by_id["428a5e3662aa57b4b256"]["concrete_word_reading_de"] == "Weinsud", "SCHOAL remains the product noun Weinsud", checks)
    require(by_id["62ff059766b21c7de083"]["concrete_word_reading_de"] == "auffangen", "OTYTCHOL remains an indivisible collect card", checks)
    require(by_id["b5df9126607030b95175"]["concrete_word_reading_de"] == "Klarauszug", "SHEY remains clear extract rather than an E-grade composition", checks)
    require(by_id["5fca8fc3dee57e1d8c1f"]["concrete_word_reading_de"] == "benetzte Stelle", "LCHEEY remains a whole wet-site card", checks)
    require(by_id["cbb42a4fe68068325d6b"]["concrete_word_reading_de"] == "Frischwasser; Schluss", "DSHEDY remains fresh water rather than SHED settling", checks)
    require(by_id["4eab1841ed655c20a348"]["concrete_word_reading_de"] == "mäßige Menge", "SHECKHAL remains quantity rather than CHCKHAL duration", checks)

    oldy_contexts = {row["contextual_event_reading_de"] for row in events if row["joint_tuple_id"] == "1b1ffdd869fb1429ad03"}
    require(oldy_contexts == {"Fortsetzen; Schluss"}, "both OLDY events obey the exact continuation card and no longer invent heat", checks)

    sentence_event_ids = [event_id for row in sentences for event_id in row["event_ids"].split("|")]
    require(Counter(sentence_event_ids) == Counter(row["event_id"] for row in events), "sentences cover every event exactly once", checks)
    require(sum(int(row["event_count"]) for row in sentences) == 381, "sentence event counts sum to 381", checks)
    require(RECORD_PATH.read_text(encoding="utf-8").count("\n## ") == 11, "record markdown contains 11 record headings", checks)
    require(len(paradigm) == 77, "paradigm inventories exactly 77 thermal/temporal and control cards", checks)
    require(len({row["joint_tuple_id"] for row in paradigm}) == 77, "paradigm card IDs are unique", checks)
    require(all(row["event_ids"].strip() for row in paradigm), "every paradigm card lists all event IDs", checks)
    require(summary["cards"] == 173 and summary["events"] == 381 and summary["statements"] == 116 and summary["records"] == 11, "summary dimensions agree", checks)

    result: dict[str, object] = {
        "schema": "SIDEQUEST_R2_THERMAL_TEMPORAL_VALIDATION_V1",
        "status": "PASS",
        "checks_passed": len(checks),
        "checks": checks,
        "counts": {
            "cards": len(dictionary),
            "events": len(events),
            "statements": len(sentences),
            "records": len({row["record_unit_id"] for row in events}),
            "changed_cards": len(changed_cards),
            "changed_events": len(changed_events),
            "changed_statements": len(changed_sentences),
            "inventory_rows": len(paradigm),
        },
        "sealed_pages": ["f84", "f84r"],
    }
    VALIDATION_PATH.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    print(json.dumps(main(), ensure_ascii=False, indent=2, sort_keys=True))
