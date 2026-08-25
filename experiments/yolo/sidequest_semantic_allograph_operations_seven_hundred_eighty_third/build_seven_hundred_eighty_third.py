#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P782 = ROOT / "experiments/yolo/sidequest_semantic_recipe_identity_seven_hundred_eighty_second"


PRIMARY = {
    "CHD+DY": "OP1_CHED_CHD_CONTRACTION",
    "OK+CHD+DY": "OP1_CHED_CHD_CONTRACTION",
    "OT+CHD+DY": "OP1_CHED_CHD_CONTRACTION",
    "OK+Y": "OP2_Y_CHY_EXPANSION",
    "CHD+Y": "OP2_Y_CHY_EXPANSION",
    "OK+OL": "OP3_ENTRY_SIDE_TEMPLATE",
    "OT+Y": "OP3_ENTRY_SIDE_TEMPLATE",
    "OL": "MODEL_ONLY_WHOLE_VARIANT",
    "CHK+EE+Y": "MODEL_ONLY_GRADE_ORDER",
    "SH+EE+Y": "MODEL_ONLY_GRADE_WRAPPER",
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        out = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        out.writeheader()
        out.writerows(rows)


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    pairs = read(P782 / "SEVEN_HUNDRED_EIGHTY_SECOND_10_TWO_CARD_RECIPE_FAMILIES.tsv")
    paired_events = read(P782 / "SEVEN_HUNDRED_EIGHTY_SECOND_71_PAIRED_RECIPE_EVENTS.tsv")

    factored_rows = []
    for row in pairs:
        mechanism = PRIMARY[row["component_recipe"]]
        if mechanism.startswith("OP1") or mechanism.startswith("OP2"):
            tier = "PRODUCTIVE_SURFACE_EDIT"
        elif mechanism.startswith("OP3"):
            tier = "TWO_FORM_WORKSHOP_TEMPLATE"
        else:
            tier = "COPY_WHOLE_VARIANT_FROM_MODEL"
        factored_rows.append(
            {
                **row,
                "primary_mechanism": mechanism,
                "teaching_tier": tier,
                "semantic_value_changed": "NO",
                "variant_choice_source": "PAGE_MODEL_CUE",
            }
        )
    write(
        "SEVEN_HUNDRED_EIGHTY_THIRD_10_FACTORED_RECIPE_PAIRS.tsv",
        factored_rows,
        [*pairs[0].keys(), "primary_mechanism", "teaching_tier", "semantic_value_changed", "variant_choice_source"],
    )

    operation_rows = [
        {
            "operation_id": "OP1_CHED_CHD_CONTRACTION",
            "spoken_instruction": "schreibe den Umsetzungskern lang CHED oder kurz CHD",
            "mechanical_edit": "replace first CHED by CHD; reverse by inserting E",
            "recipe_families": "CHD+DY,OK+CHD+DY,OT+CHD+DY",
            "families": 3,
            "events": 13,
            "teaching_status": "PRODUCTIVE",
        },
        {
            "operation_id": "OP2_Y_CHY_EXPANSION",
            "spoken_instruction": "schreibe den laufenden Posten kurz Y oder erweitert CHY",
            "mechanical_edit": "replace final Y by CHY; reverse by removing inserted CH",
            "recipe_families": "CHD+Y,OK+Y",
            "families": 2,
            "events": 25,
            "teaching_status": "PRODUCTIVE",
        },
        {
            "operation_id": "OP3_ENTRY_SIDE_TEMPLATE",
            "spoken_instruction": "waehle die gelernte Eintrittsseite Q-vorn oder CH/CH(E)-innen",
            "mechanical_edit": "paired template, not a free character rewrite",
            "recipe_families": "OK+OL,OT+Y",
            "families": 2,
            "events": 5,
            "teaching_status": "TWO_FORM_TEMPLATE",
        },
    ]
    write(
        "SEVEN_HUNDRED_EIGHTY_THIRD_3_REPEATED_ALLOGRAPH_OPERATIONS.tsv",
        operation_rows,
        ["operation_id", "spoken_instruction", "mechanical_edit", "recipe_families", "families", "events", "teaching_status"],
    )

    edit_examples = [
        {"operation_id": "OP1_CHED_CHD_CONTRACTION", "recipe": "CHD+DY", "long_form": "dchedy", "short_form": "dchdy", "forward_result": "dchedy".replace("ched", "chd", 1)},
        {"operation_id": "OP1_CHED_CHD_CONTRACTION", "recipe": "OK+CHD+DY", "long_form": "qokchedy", "short_form": "qokchdy", "forward_result": "qokchedy".replace("ched", "chd", 1)},
        {"operation_id": "OP1_CHED_CHD_CONTRACTION", "recipe": "OT+CHD+DY", "long_form": "otchedy", "short_form": "otchdy", "forward_result": "otchedy".replace("ched", "chd", 1)},
        {"operation_id": "OP2_Y_CHY_EXPANSION", "recipe": "OK+Y", "long_form": "okchy", "short_form": "oky", "forward_result": "oky"[:-1] + "chy"},
        {"operation_id": "OP2_Y_CHY_EXPANSION", "recipe": "OK+Y", "long_form": "chokchy", "short_form": "choky", "forward_result": "choky"[:-1] + "chy"},
        {"operation_id": "OP2_Y_CHY_EXPANSION", "recipe": "OK+Y", "long_form": "qokchy", "short_form": "qoky", "forward_result": "qoky"[:-1] + "chy"},
        {"operation_id": "OP2_Y_CHY_EXPANSION", "recipe": "CHD+Y", "long_form": "chedchy", "short_form": "chedy", "forward_result": "chedy"[:-1] + "chy"},
        {"operation_id": "OP3_ENTRY_SIDE_TEMPLATE", "recipe": "OK+OL", "long_form": "okchol", "short_form": "qokol", "forward_result": "qokol"},
        {"operation_id": "OP3_ENTRY_SIDE_TEMPLATE", "recipe": "OT+Y", "long_form": "otchey", "short_form": "qotchy", "forward_result": "qotchy"},
    ]
    write(
        "SEVEN_HUNDRED_EIGHTY_THIRD_9_VARIANT_DRILLS.tsv",
        edit_examples,
        ["operation_id", "recipe", "long_form", "short_form", "forward_result"],
    )

    mechanism_by_recipe = {row["component_recipe"]: row["primary_mechanism"] for row in factored_rows}
    event_rows = []
    for row in paired_events:
        mechanism = mechanism_by_recipe[row["component_recipe"]]
        event_rows.append(
            {
                **row,
                "variant_mechanism": mechanism,
                "surface_memory": "DERIVE_WITH_MODEL_CUE" if mechanism.startswith(("OP1", "OP2", "OP3")) else "COPY_WHOLE_VARIANT",
                "spoken_reading_preserved": "YES",
            }
        )
    write(
        "SEVEN_HUNDRED_EIGHTY_THIRD_71_VARIANT_EVENT_TRACE.tsv",
        event_rows,
        [*paired_events[0].keys(), "variant_mechanism", "surface_memory", "spoken_reading_preserved"],
    )

    model_only = [row for row in event_rows if row["surface_memory"] == "COPY_WHOLE_VARIANT"]
    write(
        "SEVEN_HUNDRED_EIGHTY_THIRD_28_MODEL_ONLY_VARIANT_EVENTS.tsv",
        model_only,
        [*paired_events[0].keys(), "variant_mechanism", "surface_memory", "spoken_reading_preserved"],
    )

    report = """# Pass 783 — Drei Variantenregeln statt zehn unverbundener Paare

Sieben der zehn zweikartigen Rezeptfamilien lassen sich mit drei wiederkehrenden Werkstattoperationen lehren:

1. **CHED ↔ CHD:** der Umsetzungskern darf lang oder kontrahiert stehen. Die Operation erzeugt exakt `dchedy→dchdy`, `qokchedy→qokchdy` und `otchedy→otchdy`; drei Familien/13 Ereignisse.
2. **Y ↔ CHY:** der laufende Posten darf kurz oder mit eingeschobenem CH stehen. Sie erzeugt `oky→okchy`, `choky→chokchy`, `qoky→qokchy` und `chedy→chedchy`; zwei Familien/25 Ereignisse.
3. **Eintrittsseiten-Vorlage:** zwei gelernte Paare setzen Q vorn gegen CH/CH(E) innen (`qokol↔okchol`, `qotchy↔otchey`); zwei Familien/5 Ereignisse. Das ist eine Zweiformvorlage, kein freies Buchstabenrezept.

Damit sind43/71 Ereignisse der gepaarten Rezeptfamilien durch wiederkehrende Variantenlehre gedeckt. Drei Familien/28 Ereignisse bleiben ehrliche Ganzvarianten: `OL↔ls`, die CHK/EE-Reihenfolge und die SH/EE-Hülle.

Wichtig: Der Seitenexemplar-Cue wählt weiterhin, welche Variante an einer Stelle steht. Die Operation lehrt nur, wie die zweite Form gebaut und gleich rückgelesen wird. So sparen wir Formenlernen, ohne freie Ersetzung zu erfinden.

Als nächstes tragen wir diese zwei produktiven Edits in die gesamten163 Rezeptwerte ein und suchen vorausberechenbare, bislang nur einmal belegte Partnerformen. Wir erzeugen nur Kandidaten innerhalb bereits gelernter Komponentenrezepte und prüfen sie gegen die zehn festen Seiten.
"""
    (HERE / "SEVEN_HUNDRED_EIGHTY_THIRD_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS",
        "pair_families": len(factored_rows),
        "repeated_operations": len(operation_rows),
        "operation_covered_families": sum(row["teaching_tier"] != "COPY_WHOLE_VARIANT_FROM_MODEL" for row in factored_rows),
        "operation_covered_events": sum(int(row["pair_events"]) for row in factored_rows if row["teaching_tier"] != "COPY_WHOLE_VARIANT_FROM_MODEL"),
        "model_only_families": sum(row["teaching_tier"] == "COPY_WHOLE_VARIANT_FROM_MODEL" for row in factored_rows),
        "model_only_events": len(model_only),
        "decision": "CHED_CHD_AND_Y_CHY_PRODUCTIVE__ENTRY_SIDE_PAIRED__THREE_MODEL_VARIANTS_REMAIN",
    }
    (HERE / "SEVEN_HUNDRED_EIGHTY_THIRD_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
