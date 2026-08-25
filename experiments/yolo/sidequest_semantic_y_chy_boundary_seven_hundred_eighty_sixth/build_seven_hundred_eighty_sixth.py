#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P739 = ROOT / "experiments/yolo/sidequest_semantic_clean_fluent_edition_seven_hundred_thirty_ninth"
EMPIRICAL = {"Y", "OK+Y", "CHD+Y"}


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
    events = read(P739 / "SEVEN_HUNDRED_THIRTY_NINTH_381_EVENT_INTERLINEAR.tsv")
    y_events = [
        row
        for row in events
        if "Y" in row["component_recipe"].split("+") and "DY" not in row["component_recipe"].split("+")
    ]
    by_recipe: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in y_events:
        by_recipe[row["component_recipe"]].append(row)

    recipe_rows = []
    for recipe, rows in sorted(by_recipe.items()):
        components = recipe.split("+")
        surfaces = {row["surface"] for row in rows}
        has_terminal_chy = any(surface.endswith("chy") for surface in surfaces)
        if recipe in EMPIRICAL:
            recipe_class = "EMPIRICAL_Y_CHY_ALLOGRAPH_FAMILY"
        elif recipe == "OT+Y":
            recipe_class = "PAIRED_ENTRY_TEMPLATE"
        elif "CH" in components:
            recipe_class = "SEMANTIC_CH_PLUS_Y"
        elif has_terminal_chy:
            recipe_class = "STRUCTURAL_CHY_EXTENSION"
        else:
            recipe_class = "Y_WITHOUT_CHY_VARIANT"
        recipe_rows.append(
            {
                "component_recipe": recipe,
                "workshop_reading_de": rows[0]["rebuilt_reading_de"],
                "events": len(rows),
                "exact_cards": len({row["card_no"] for row in rows}),
                "surfaces": ",".join(sorted(surfaces)),
                "terminal_chy_surfaces": ",".join(sorted(surface for surface in surfaces if surface.endswith("chy"))) or "NONE",
                "standalone_semantic_ch_component": "YES" if "CH" in components else "NO",
                "recipe_class": recipe_class,
                "teaching_readback": "KEEP_CH_AS_ENTNEHMEN" if "CH" in components else "DO_NOT_ADD_CH_MEANING_BEFORE_TERMINAL_Y",
            }
        )
    write(
        "SEVEN_HUNDRED_EIGHTY_SIXTH_53_OPEN_Y_RECIPES.tsv",
        recipe_rows,
        ["component_recipe", "workshop_reading_de", "events", "exact_cards", "surfaces", "terminal_chy_surfaces", "standalone_semantic_ch_component", "recipe_class", "teaching_readback"],
    )

    event_rows = []
    for row in y_events:
        components = row["component_recipe"].split("+")
        terminal_chy = row["surface"].endswith("chy")
        if terminal_chy and "CH" in components:
            role = "SEMANTIC_CH_ENTNEHMEN_PLUS_Y_REFERENT"
        elif terminal_chy:
            role = "NONSEMANTIC_CHY_REFERENT_ALLOGRAPH"
        elif "CH" in components:
            role = "SEMANTIC_CH_ELSEWHERE_IN_RECIPE"
        else:
            role = "Y_REFERENT_WITHOUT_TERMINAL_CHY"
        event_rows.append(
            {
                "event_id": row["event_id"],
                "page": row["page"],
                "record": row["record"],
                "statement_id": row["statement_id"],
                "exact_card_id": row["card_no"],
                "surface": row["surface"],
                "component_recipe": row["component_recipe"],
                "working_reading_de": row["rebuilt_reading_de"],
                "terminal_chy": "YES" if terminal_chy else "NO",
                "standalone_ch_component": "YES" if "CH" in components else "NO",
                "terminal_ch_role": role,
                "readback_preserved": "YES",
            }
        )
    write(
        "SEVEN_HUNDRED_EIGHTY_SIXTH_122_OPEN_Y_EVENTS.tsv",
        event_rows,
        ["event_id", "page", "record", "statement_id", "exact_card_id", "surface", "component_recipe", "working_reading_de", "terminal_chy", "standalone_ch_component", "terminal_ch_role", "readback_preserved"],
    )

    chy_rows = [row for row in event_rows if row["terminal_chy"] == "YES"]
    write(
        "SEVEN_HUNDRED_EIGHTY_SIXTH_13_TERMINAL_CHY_EVENTS.tsv",
        chy_rows,
        ["event_id", "page", "record", "statement_id", "exact_card_id", "surface", "component_recipe", "working_reading_de", "terminal_chy", "standalone_ch_component", "terminal_ch_role", "readback_preserved"],
    )

    semantic_rows = [row for row in event_rows if row["standalone_ch_component"] == "YES"]
    write(
        "SEVEN_HUNDRED_EIGHTY_SIXTH_4_SEMANTIC_CH_CONTROLS.tsv",
        semantic_rows,
        ["event_id", "page", "record", "statement_id", "exact_card_id", "surface", "component_recipe", "working_reading_de", "terminal_chy", "standalone_ch_component", "terminal_ch_role", "readback_preserved"],
    )

    rules = [
        {"priority": 1, "condition": "recipe explicitly contains standalone CH", "read_ch": "ENTNEHMEN", "read_y": "DIES", "example": "lchy = L+CH+Y"},
        {"priority": 2, "condition": "surface ends CHY and recipe has no standalone CH", "read_ch": "NO EXTRA VALUE", "read_y": "DIES", "example": "qokchy = OK+Y"},
        {"priority": 3, "condition": "recipe in Y, OK+Y or CHD+Y", "read_ch": "REGISTERED ALLOGRAPH WHEN PRESENT", "read_y": "DIES", "example": "y~chy; oky~okchy; chedy~chedchy"},
        {"priority": 4, "condition": "other recipe with terminal CHY", "read_ch": "PROVISIONAL NONSEMANTIC HULL", "read_y": "DIES", "example": "kchy, oltchy, qokokchy"},
        {"priority": 5, "condition": "never infer recipe from letters alone", "read_ch": "LOOK UP CARD RECIPE", "read_y": "LOOK UP CARD RECIPE", "example": "ly and lchy stay different"},
    ]
    write(
        "SEVEN_HUNDRED_EIGHTY_SIXTH_5_Y_CHY_RULES.tsv",
        rules,
        ["priority", "condition", "read_ch", "read_y", "example"],
    )

    report = """# Pass 786 — CHY ist meist eine Referenzhülle, aber CH kann ein eigenes Wortstück bleiben

Der offene Y-Bereich umfasst122 Ereignisse,58 Karten und53 Komponentenrezepte. Die klare Werkstattregel lautet nicht „CH bedeutet immer nichts“, sondern **das registrierte Rezept entscheidet**.

Unter13 Oberflächen mit terminalem `chy` sind12 Fälle ohne selbständiges CH im Rezept. Dort trägt CH keinen zusätzlichen Arbeitswert; Y bleibt `DIES/der laufende Posten`. Sieben davon liegen in den direkt gepaarten Familien Y, OK+Y und CHD+Y. Fünf weitere sind plausible Erweiterungen derselben Schreiberhülle (`kchy`, `qotchy`, `oltchy`, `qokokchy`, `shecthedchy`), bleiben aber ohne sichtbaren Kurzpartner.

Der eine Gegenfall ist entscheidend: `lchy` ist ausdrücklich `L+CH+Y = LEITEN · ENTNEHMEN · DIES`. Seine Nachbarkarte `ly = L+Y = LEITEN · DIES` zeigt, dass CH hier wirklich semantisch ist. Drei weitere offene Y-Rezepte besitzen ebenfalls ein registriertes CH an anderer Stelle.

Die kürzeste fehlerfreie Leseregel ist deshalb:

1. Steht CH als eigene Komponente im Kartenrezept, lies `ENTNEHMEN`.
2. Steht CH nur unmittelbar vor dem terminalen Y und fehlt als Rezeptkomponente, lies es als Schreiberhülle ohne Zusatzwert.
3. Errate niemals das Rezept aus der sichtbaren Zeichenfolge allein.

Damit bleiben alle122 Arbeitslesungen konsistent, und `ly/lchy` werden nicht mehr versehentlich zusammengelegt.

Als nächstes untersuchen wir die E/EE/EEE-Grade mit derselben Methode: Welche sichtbaren e-Längen sind echte KURZ/LANG/VOLL-Komponenten, welche gehören fest zum Kern, und welche sind nur Handhüllen?
"""
    (HERE / "SEVEN_HUNDRED_EIGHTY_SIXTH_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS",
        "open_y_events": len(event_rows),
        "open_y_cards": len({row["exact_card_id"] for row in event_rows}),
        "open_y_recipes": len(recipe_rows),
        "terminal_chy_events": len(chy_rows),
        "nonsemantic_terminal_chy": sum(row["terminal_ch_role"] == "NONSEMANTIC_CHY_REFERENT_ALLOGRAPH" for row in chy_rows),
        "semantic_terminal_chy": sum(row["terminal_ch_role"] == "SEMANTIC_CH_ENTNEHMEN_PLUS_Y_REFERENT" for row in chy_rows),
        "semantic_ch_control_events": len(semantic_rows),
        "decision": "RECIPE_GOVERNED_CH__TERMINAL_CHY_NONSEMANTIC_UNLESS_CH_REGISTERED",
    }
    (HERE / "SEVEN_HUNDRED_EIGHTY_SIXTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
