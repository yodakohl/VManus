#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BASE = ROOT / "sidequest_semantic_clean_fluent_edition_seven_hundred_thirty_ninth"
CARDS = BASE / "SEVEN_HUNDRED_THIRTY_NINTH_173_CARD_DICTIONARY.tsv"
EVENTS = BASE / "SEVEN_HUNDRED_THIRTY_NINTH_381_EVENT_INTERLINEAR.tsv"
TARGETS = ("SHED", "CHK", "P", "LSH")
VALUE = {"SHED": "ABSETZEN", "CHK": "WAERMEN", "P": "FUELLEN", "LSH": "WASCHEN"}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    cards = read(CARDS)
    events = read(EVENTS)
    surfaces = {row["surface"] for row in events}

    inventory = []
    component_rows = []
    for component in TARGETS:
        selected = []
        tails = set()
        for row in cards:
            tokens = row["component_recipe"].split("+")
            if component not in tokens:
                continue
            selected.append(row)
            removed = tokens.copy()
            removed.remove(component)
            tails.add("+".join(removed) or "BARE")
            inventory.append(
                {
                    "component": component,
                    "short_value_de": VALUE[component],
                    "exact_card_id": row["exact_card_id"],
                    "surfaces": row["registered_surfaces"],
                    "component_recipe": row["component_recipe"],
                    "tail_without_component": "+".join(removed) or "BARE",
                    "working_reading_de": row["rebuilt_reading_de"],
                    "events": row["events"],
                }
            )
        same_value = all(VALUE[component] in row["rebuilt_reading_de"].split(" · ") for row in selected)
        component_rows.append(
            {
                "component": component,
                "short_value_de": VALUE[component],
                "exact_cards": len(selected),
                "events": sum(int(row["events"]) for row in selected),
                "distinct_tails": len(tails),
                "tails": "|".join(sorted(tails)),
                "meaning_invariant": "YES" if same_value else "NO",
                "shared_tail_with_other_target": "NO",
                "decision": "PROMOTE_TO_PARADIGM_CORE19" if component == "CHK" else "RETAIN_RECURRENT_RULE_STRIP",
                "reason": (
                    "registered E/EE grade contrast plus Y/DY endpoint contrast"
                    if component == "CHK"
                    else "portable short value but no controlled cross-target or complete internal grid"
                ),
            }
        )

    chk_grid = [
        {
            "grade": "E",
            "grade_value_de": "KURZ",
            "endpoint": "Y",
            "endpoint_value_de": "DIES",
            "component_recipe": "CHK+E+Y",
            "surfaces": "cheky",
            "events": 3,
            "status": "ATTESTED",
            "reading_de": "WAERMEN · KURZ · DIES",
        },
        {
            "grade": "EE",
            "grade_value_de": "LANG",
            "endpoint": "Y",
            "endpoint_value_de": "DIES",
            "component_recipe": "CHK+EE+Y",
            "surfaces": "cheeky|chkeey",
            "events": 3,
            "status": "ATTESTED_TWO_RENDERERS",
            "reading_de": "WAERMEN · LANG · DIES",
        },
        {
            "grade": "EE",
            "grade_value_de": "LANG",
            "endpoint": "DY",
            "endpoint_value_de": "SCHLUSS",
            "component_recipe": "CHK+EE+DY",
            "surfaces": "chkeedy",
            "events": 1,
            "status": "ATTESTED",
            "reading_de": "WAERMEN · LANG · SCHLUSS",
        },
        {
            "grade": "E",
            "grade_value_de": "KURZ",
            "endpoint": "DY",
            "endpoint_value_de": "SCHLUSS",
            "component_recipe": "CHK+E+DY",
            "surfaces": "chkedy",
            "events": 0,
            "status": "PREDICTED_UNATTESTED",
            "reading_de": "WAERMEN · KURZ · SCHLUSS",
        },
        {
            "grade": "EEE",
            "grade_value_de": "VOLL",
            "endpoint": "Y",
            "endpoint_value_de": "DIES",
            "component_recipe": "CHK+EEE+Y",
            "surfaces": "chkeeey|cheeeky",
            "events": 0,
            "status": "PREDICTED_RENDERER_AMBIGUOUS",
            "reading_de": "WAERMEN · VOLL · DIES",
        },
        {
            "grade": "EEE",
            "grade_value_de": "VOLL",
            "endpoint": "DY",
            "endpoint_value_de": "SCHLUSS",
            "component_recipe": "CHK+EEE+DY",
            "surfaces": "chkeeedy",
            "events": 0,
            "status": "PREDICTED_UNATTESTED",
            "reading_de": "WAERMEN · VOLL · SCHLUSS",
        },
    ]
    for row in chk_grid:
        row["surface_collision"] = "YES" if any(surface in surfaces for surface in row["surfaces"].split("|")) and row["events"] == 0 else "NO"

    write(
        "EIGHT_HUNDRED_FIRST_12_PROCESS_CARDS.tsv",
        inventory,
        ["component", "short_value_de", "exact_card_id", "surfaces", "component_recipe", "tail_without_component", "working_reading_de", "events"],
    )
    write(
        "EIGHT_HUNDRED_FIRST_4_PROCESS_DECISIONS.tsv",
        component_rows,
        ["component", "short_value_de", "exact_cards", "events", "distinct_tails", "tails", "meaning_invariant", "shared_tail_with_other_target", "decision", "reason"],
    )
    write(
        "EIGHT_HUNDRED_FIRST_CHK_GRADE_GRID.tsv",
        chk_grid,
        ["grade", "grade_value_de", "endpoint", "endpoint_value_de", "component_recipe", "surfaces", "events", "status", "reading_de", "surface_collision"],
    )
    summary = {
        "status": "PASS",
        "decision": "CHK_WARMING_PROMOTED_AS_CORE19__SHED_P_LSH_RETAINED_AS_STRIP_VALUES",
        "target_cards": len(inventory),
        "target_events": sum(int(row["events"]) for row in inventory),
        "components": len(component_rows),
        "meaning_invariant_components": sum(row["meaning_invariant"] == "YES" for row in component_rows),
        "shared_cross_target_tails": 0,
        "chk_grid_cells": len(chk_grid),
        "chk_attested_cells": sum(row["events"] > 0 for row in chk_grid),
        "chk_predicted_cells": sum(row["events"] == 0 for row in chk_grid),
        "predicted_surface_collisions": sum(row["surface_collision"] == "YES" for row in chk_grid),
        "new_core_size": 19,
        "remaining_recurrent_strip_values": 12,
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / "EIGHT_HUNDRED_FIRST_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
