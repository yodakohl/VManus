#!/usr/bin/env python3
"""Mechanical completeness checks for the creative vessel/tool edition."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read_tsv(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


dictionary = read_tsv("SELECTED_173_VESSEL_TOOL_DICTIONARY.tsv")
events = read_tsv("SELECTED_381_VESSEL_TOOL_INTERLINEAR.tsv")
sentences = read_tsv("SELECTED_116_VESSEL_TOOL_SENTENCES.tsv")
paradigm = read_tsv("VESSEL_TOOL_PARADIGM.tsv")
components = read_tsv("VESSEL_TOOL_COMPONENTS.tsv")
dmap = {row["joint_tuple_id"]: row for row in dictionary}

checks = {
    "cards_173": len(dictionary) == 173,
    "events_381": len(events) == 381,
    "sentences_116": len(sentences) == 116,
    "records_11": len({row["record_unit_id"] for row in events}) == 11,
    "cards_unique": len(dmap) == 173,
    "events_unique": len({row["event_id"] for row in events}) == 381,
    "all_cards_concrete": all(row["concrete_word_reading_de"].strip() for row in dictionary),
    "all_events_readable": all(row["contextual_event_reading_de"].strip() for row in events),
    "dictionary_event_identity": all(row["concrete_word_reading_de"] == dmap[row["joint_tuple_id"]]["concrete_word_reading_de"] for row in events),
    "sentence_partition_381": sum(int(row["event_count"]) for row in sentences) == 381,
    "revised_cards_54": sum(row["vessel_tool_revision"] == "REVISED" for row in dictionary) == 54,
    "revised_events_103": sum(row["vessel_tool_revision"] == "REVISED" for row in events) == 103,
    "paradigm_54": len(paradigm) == 54,
    "components_21": len(components) == 21,
    "no_old_opening_ordinals": all("erste Öffnung" not in row["concrete_word_reading_de"] and "zweite Öffnung" not in row["concrete_word_reading_de"] for row in dictionary),
    "al_short": dmap["dd0ecaf5e27d81befffc"]["concrete_word_reading_de"] == "dorthin",
    "ar_short": dmap["4d4559019a961b834aa1"]["concrete_word_reading_de"] == "daraus",
    "ckh_through": dmap["2cc8bb3c2af19607888f"]["concrete_word_reading_de"] == "durchleiten",
    "ched_short": dmap["6f7ff8287eddf4da9fdb"]["concrete_word_reading_de"] == "umsetzen",
    "solk_grade_series": [dmap[ident]["concrete_word_reading_de"] for ident in ("42cdc187d5b9ffc60063", "1bfd786e6b8b63734a59", "3b70942557b3a40e8030")] == ["kurz sammeln", "länger sammeln", "länger sammeln; Schluss"],
    "six_vessels": [dmap[ident]["concrete_word_reading_de"] for ident in ("df1098831679a8ad1b39", "27d97af8c96eb056c2e6", "b38d70daefd663d74625", "1779decef17481ec2853", "e2eb77ca9d9e1a8ba29a", "342c3f0777337648f4b3")] == ["Gefäß", "Topf", "Auffangschale", "Wanne", "Becken", "Sammelbecken"],
    "four_fittings": [dmap[ident]["concrete_word_reading_de"] for ident in ("a06244ef1f2b37ca44c1", "5eff216ba51fbfb21f22", "92e43836d82f98bf02d3", "3e9c7f217843b588489d")] == ["Hahn", "Düse", "Ablauf", "Seitenarm"],
    "fixed_pages_only": {row["page"] for row in events} == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
    "sealed_absent": all(not row["page"].startswith("f84") for row in events),
}

result = {
    "status": "PASS" if all(checks.values()) else "FAIL",
    "checks": checks,
    "counts": {
        "cards": len(dictionary),
        "events": len(events),
        "sentences": len(sentences),
        "paradigm_rows": len(paradigm),
        "component_rows": len(components),
    },
}
(HERE / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
if result["status"] != "PASS":
    raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
