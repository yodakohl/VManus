#!/usr/bin/env python3
"""Validate the selected directional creative sidequest edition."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DICT = HERE / "SELECTED_173_DIRECTIONAL_DICTIONARY.tsv"
EVENTS = HERE / "SELECTED_381_DIRECTIONAL_INTERLINEAR.tsv"
STATEMENTS = HERE / "SELECTED_116_DIRECTIONAL_STATEMENTS.tsv"
RECORDS = HERE / "SELECTED_11_RECORD_READINGS.md"
COMPONENTS = HERE / "SELECTED_DIRECTIONAL_COMPONENT_LEXICON.tsv"
UNRESOLVED = HERE / "REMAINING_UNRESOLVED_AFTER_DIRECTION.tsv"
SUMMARY = HERE / "SELECTED_BUILD_SUMMARY.json"
WORKSHOP = HERE / "WORKSHOP_DIRECTION_PARADIGM.tsv"
RECURRENT = HERE / "CENTRAL_RECURRENT_CARD_REVIEW.tsv"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, label: str, checks: dict[str, bool]) -> None:
    checks[label] = condition
    if not condition:
        raise AssertionError(label)


def main() -> None:
    dictionary = rows(DICT)
    events = rows(EVENTS)
    statements = rows(STATEMENTS)
    components = rows(COMPONENTS)
    unresolved = rows(UNRESOLVED)
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    checks: dict[str, bool] = {}

    require(len(dictionary) == 173, "dictionary_173", checks)
    require(len(events) == 381, "events_381", checks)
    require(len(statements) == 116, "statements_116", checks)
    require(len({row["joint_tuple_id"] for row in dictionary}) == 173, "dictionary_ids_unique", checks)
    require([row["event_id"] for row in events] == [f"E{i:03d}" for i in range(1, 382)], "event_order_complete", checks)
    require(set(row["page"] for row in events) == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"}, "fixed_prose_pages_only", checks)
    require(not any(row["page"].startswith("f84") for row in events), "sealed_pages_absent", checks)

    by_id = {row["joint_tuple_id"]: row for row in dictionary}
    require(
        all(
            row["semantic_segmentation"] == by_id[row["joint_tuple_id"]]["semantic_segmentation"]
            and row["stable_concrete_nucleus_de"] == by_id[row["joint_tuple_id"]]["stable_concrete_nucleus_de"]
            and row["concrete_word_reading_de"] == by_id[row["joint_tuple_id"]]["concrete_word_reading_de"]
            for row in events
        ),
        "event_dictionary_values_identical",
        checks,
    )
    require(all(row["concrete_word_reading_de"] and row["contextual_event_reading_de"] for row in events), "no_empty_event_readings", checks)

    changed_cards = [row for row in dictionary if row["direction_revision_source"] != "UNCHANGED"]
    changed_events = [row for row in events if row["direction_revision_source"] != "UNCHANGED"]
    require(len(changed_cards) == 34, "changed_cards_34", checks)
    require(len(changed_events) == 68, "changed_events_68", checks)
    require(sum(int(row["revised_event_count"]) > 0 for row in statements) == 46, "changed_statements_46", checks)
    require(
        {source: sum(row["direction_revision_source"] == source for row in changed_cards) for source in ("DIRECTION_WORKSHOP", "DIRECTION_EXTENSION", "CHEO_LDDY", "RECURRENT_COMPOSITION")}
        == {"DIRECTION_WORKSHOP": 23, "DIRECTION_EXTENSION": 2, "CHEO_LDDY": 2, "RECURRENT_COMPOSITION": 7},
        "source_card_counts_exact",
        checks,
    )
    require(
        {source: sum(row["direction_revision_source"] == source for row in changed_events) for source in ("DIRECTION_WORKSHOP", "DIRECTION_EXTENSION", "CHEO_LDDY", "RECURRENT_COMPOSITION")}
        == {"DIRECTION_WORKSHOP": 50, "DIRECTION_EXTENSION": 2, "CHEO_LDDY": 2, "RECURRENT_COMPOSITION": 14},
        "source_event_counts_exact",
        checks,
    )

    workshop_events = {
        item.split("@", 1)[0]
        for row in rows(WORKSHOP)
        for item in row["event_inventory"].split("|")
    }
    require(workshop_events == {row["event_id"] for row in changed_events if row["direction_revision_source"] == "DIRECTION_WORKSHOP"}, "workshop_event_set_exact", checks)
    require({row["event_id"] for row in changed_events if row["direction_revision_source"] == "DIRECTION_EXTENSION"} == {"E228", "E351"}, "direction_extension_events_exact", checks)
    require({row["event_id"] for row in changed_events if row["direction_revision_source"] == "CHEO_LDDY"} == {"E092", "E326"}, "cheo_lddy_events_exact", checks)
    recurrent_events = {event for row in rows(RECURRENT) if row["decision"].startswith("REVISE") for event in row["events"].split("|")}
    require(recurrent_events == {row["event_id"] for row in changed_events if row["direction_revision_source"] == "RECURRENT_COMPOSITION"}, "recurrent_event_set_exact", checks)

    expected = {
        "4d4559019a961b834aa1": "aus demselben Vorrat",
        "12efe866f335461823a6": "Flüssigkeitszulauf",
        "22fb87a5a83e5c3fb510": "laufende Beckenflüssigkeit",
        "7d2404c835b10a2c06af": "Flüssigkeit in den Lauf bringen",
        "b154ff779abe5f196c80": "fließende Flüssigkeit durch den Lauf führen",
        "8aedd154964a78e555d6": "den Flüssigkeitslauf abschließen",
        "dd0ecaf5e27d81befffc": "Zielstelle",
        "433713294b25b0a12f66": "Auslassstelle",
        "ba540da978ea132f6da5": "Einfüllstelle",
        "de7321bface5628e35d6": "hinausführen; Schluss",
        "65df3cd9e59060042d47": "hineinführen; Schluss",
        "087a47b5423438cd6b6a": "Auszugsflüssigkeit zugeben",
        "eb2e4bc143f623ee03ac": "den laufenden Posten als Auflage befestigen; Schluss",
        "94df4847b7b16c98394a": "mit einer weiteren Portion fortfahren",
        "faf321940aed922846a9": "den nächsten Posten wählen",
        "10488b911aae52b3b334": "die nächste Zubereitung",
        "abb23e5e6936b4147f76": "Ruhe- oder Absetzstelle",
    }
    require(all(by_id[ident]["concrete_word_reading_de"] == gloss for ident, gloss in expected.items()), "named_selected_glosses_exact", checks)
    require(by_id["80ebbbbf238eee9f0aef"]["concrete_word_reading_de"] == "zerkleinern", "whole_chty_retained", checks)
    require(by_id["53cd0637c6820ba5e91f"]["concrete_word_reading_de"] == "durch Tuch", "whole_dain_retained", checks)
    require(by_id["0f18de177ed7c878bf95"]["concrete_word_reading_de"] == "Badezusatz", "whole_dl_retained", checks)

    forbidden_replaced = ("Rücklauf", "Wasserlauf öffnen", "sofort gebrauchen", "unteres Becken", "Zeitabschnitt", "zweite Auswahl")
    require(not any(term.lower() in row["concrete_word_reading_de"].lower() for row in changed_cards for term in forbidden_replaced), "superseded_glosses_removed", checks)

    component_by_id = {row["component_id"]: row for row in components}
    require(len(components) == 28, "component_rows_28", checks)
    require(component_by_id["AR"]["working_meaning_de"] == "Quelle oder Vorrat; aus oder von", "ar_component_exact", checks)
    require(component_by_id["AIR"]["working_meaning_de"] == "fließende Flüssigkeit im Lauf", "air_component_exact", checks)
    require(component_by_id["AL"]["working_meaning_de"] == "Ziel- oder Arbeitsstelle; an oder zu", "al_component_exact", checks)
    require({"CHEO_EXTRACT_LIQUID", "LDDY_APPLICATION_CLOSE", "IIN_GRADE", "CTH_READY", "OR_PREPARATION"}.issubset(component_by_id), "new_components_present", checks)
    require(len(unresolved) == 14, "remaining_unresolved_14", checks)
    require({"AIR_EXACT_SUBSTANCE", "CHEO_EXACT_LIQUID", "LDDY_PORTABILITY", "IIN_GRADE_PORTABILITY"}.issubset({row["candidate_component"] for row in unresolved}), "residual_portability_limits_explicit", checks)

    statement_event_ids = [event for row in statements for event in row["event_ids"].split("|")]
    require(statement_event_ids == [row["event_id"] for row in events], "statement_event_coverage_and_order", checks)
    require(all(int(row["event_count"]) == len(row["event_ids"].split("|")) for row in statements), "statement_counts_exact", checks)
    record_text = RECORDS.read_text(encoding="utf-8")
    require(set(re.findall(r"^## ([HB]\d+) —", record_text, flags=re.MULTILINE)) == {"H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"}, "record_sections_11", checks)
    require(set(re.findall(r"\*\*([HB]\d+-S\d{3})\*\*", record_text)) == {row["statement_id"] for row in statements}, "record_statement_coverage", checks)

    require(summary["status"] == "PASS" and summary["cards"] == 173 and summary["events"] == 381 and summary["statements"] == 116 and summary["records"] == 11, "summary_counts_and_status", checks)
    require(all(summary["outputs"][str(path.relative_to(ROOT))] == sha256(path) for path in (DICT, EVENTS, STATEMENTS, RECORDS, COMPONENTS, UNRESOLVED)), "summary_output_hashes_current", checks)

    result = {
        "schema": "SIDEQUEST_SELECTED_DIRECTIONAL_COMPLETION_VALIDATION_V1",
        "status": "PASS",
        "checks": checks,
        "counts": {
            "cards": len(dictionary),
            "events": len(events),
            "statements": len(statements),
            "records": 11,
            "changed_cards": len(changed_cards),
            "changed_events": len(changed_events),
            "changed_statements": sum(int(row["revised_event_count"]) > 0 for row in statements),
            "components": len(components),
            "remaining_unresolved_rows": len(unresolved),
        },
    }
    output = HERE / "VALIDATION.json"
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
