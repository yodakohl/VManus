#!/usr/bin/env python3
"""Mechanical consistency checks for the selected creative paradigm closure."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
DICT = HERE / "SELECTED_173_STEM_CONSISTENT_DICTIONARY.tsv"
EVENTS = HERE / "SELECTED_381_STEM_CONSISTENT_INTERLINEAR.tsv"
STATEMENTS = HERE / "SELECTED_116_STEM_CONSISTENT_STATEMENTS.tsv"
COMPONENTS = HERE / "SELECTED_COMPONENT_LEXICON.tsv"
UNRESOLVED = HERE / "UNRESOLVED_COMPONENTS.tsv"
SUMMARY = HERE / "SELECTED_BUILD_SUMMARY.json"


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
    require(
        len({row["joint_tuple_id"] for row in dictionary}) == 173,
        "dictionary_ids_unique",
        checks,
    )
    require(
        [row["event_id"] for row in events]
        == [f"E{index:03d}" for index in range(1, 382)],
        "event_order_complete",
        checks,
    )
    require(
        set(row["page"] for row in events)
        == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
        "fixed_prose_pages_only",
        checks,
    )
    require(
        all(
            row["semantic_segmentation"]
            and row["stable_concrete_nucleus_de"]
            and row["concrete_word_reading_de"]
            for row in dictionary
        ),
        "dictionary_no_blank_meanings",
        checks,
    )
    require(
        all(row["contextual_event_reading_de"] for row in events),
        "events_no_blank_readings",
        checks,
    )

    by_id = {row["joint_tuple_id"]: row for row in dictionary}
    require(
        all(
            row["semantic_segmentation"]
            == by_id[row["joint_tuple_id"]]["semantic_segmentation"]
            and row["stable_concrete_nucleus_de"]
            == by_id[row["joint_tuple_id"]]["stable_concrete_nucleus_de"]
            and row["concrete_word_reading_de"]
            == by_id[row["joint_tuple_id"]]["concrete_word_reading_de"]
            for row in events
        ),
        "event_dictionary_values_identical",
        checks,
    )
    changed_cards = [
        row for row in dictionary if row["paradigm_revision"] != "UNCHANGED"
    ]
    changed_events = [
        row for row in events if row["paradigm_revision"] != "UNCHANGED"
    ]
    require(len(changed_cards) == 49, "changed_cards_49", checks)
    require(len(changed_events) == 145, "changed_events_145", checks)
    require(
        sum(int(row["revised_event_count"]) > 0 for row in statements) == 93,
        "changed_statements_93",
        checks,
    )

    by_surface = {row["surface_family"]: row for row in dictionary}
    expected = {
        "okain|qokain": "eine Portion einsetzen oder zugeben",
        "okaiin|qokaiin": "nach Maß einsetzen; den Einsatz bemessen",
        "okchol": "mit dem vorigen Arbeitsgut weiterarbeiten",
        "qokol": "vorigen Arbeitsgang weiterführen",
        "qokedy": "kurz spülen oder benetzen und den Schritt abschließen",
        "qokeedy": "eintauchen oder einweichen und den Schritt abschließen",
        "qokeeedy": "vollständig durchtränken und den Schritt abschließen",
        "chdy|chedy": "Ansatz umsetzen oder durcharbeiten",
        "lchedy": "abführen; Schluss",
        "dchedy|schedy|tchedy": "Arbeitsbewegung abschließen",
        "oteey": "danach anhaltend einwirken lassen; Arbeitszustand offen",
    }
    require(
        all(by_surface[surface]["concrete_word_reading_de"] == gloss for surface, gloss in expected.items()),
        "named_paradigm_values_exact",
        checks,
    )
    forbidden_old = (
        "Olivenöl",
        "Einlauf",
        "abkühlen",
        "erhitzen",
        "gleichteilig",
        "kühles Wasser",
        "warmes Wasser",
    )
    require(
        not any(
            token.lower() in row["concrete_word_reading_de"].lower()
            for row in changed_cards
            for token in forbidden_old
        ),
        "contradictory_old_glosses_removed",
        checks,
    )

    component_ids = {row["component_id"] for row in components}
    require(
        {
            "OK",
            "AIN",
            "AIIN",
            "AL",
            "AR",
            "AIR",
            "OL",
            "OT",
            "CHD_CHED",
            "L_CHED",
            "E_GRADE_1",
            "E_GRADE_2",
            "E_GRADE_3",
            "Y_STATE",
            "DY_STATE",
        }.issubset(component_ids),
        "required_components_present",
        checks,
    )
    require(len(unresolved) == 15, "unresolved_inventory_15", checks)
    require(
        all(
            row["working_meaning_de"]
            not in {"Wasser", "warm", "ruhen"}
            for row in components
            if row["component_id"].startswith("E_GRADE")
        ),
        "e_grade_not_global_substance_or_temperature",
        checks,
    )
    require(
        "DY" not in by_surface["chdy|chedy"]["semantic_segmentation"],
        "bare_chedy_not_forced_close",
        checks,
    )
    require(
        summary["status"] == "PASS"
        and summary["cards"] == 173
        and summary["events"] == 381
        and summary["statements"] == 116,
        "summary_counts_and_status",
        checks,
    )
    require(
        all(
            summary["outputs"][str(path.relative_to(HERE.parents[2]))] == sha256(path)
            for path in (DICT, EVENTS, STATEMENTS)
        ),
        "summary_output_hashes_current",
        checks,
    )

    result = {
        "schema": "SIDEQUEST_SELECTED_PARADIGM_CLOSURE_VALIDATION_V1",
        "status": "PASS",
        "checks": checks,
        "counts": {
            "cards": len(dictionary),
            "events": len(events),
            "statements": len(statements),
            "changed_cards": len(changed_cards),
            "changed_events": len(changed_events),
            "components": len(components),
            "unresolved_rows": len(unresolved),
        },
    }
    output = HERE / "VALIDATION.json"
    output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
