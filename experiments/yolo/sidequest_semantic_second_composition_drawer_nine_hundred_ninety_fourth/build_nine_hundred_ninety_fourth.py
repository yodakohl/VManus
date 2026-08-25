#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
YOLO = HERE.parent
P993 = YOLO / "sidequest_semantic_canonical_scribe_workshop_fifth_edition_nine_hundred_ninety_third"
P982 = YOLO / "sidequest_semantic_forward_composition_handbook_nine_hundred_eighty_second"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=fields,
            delimiter="\t",
            lineterminator="\n",
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(rows)


NATURAL = {
    "S+AIN": "eine Einheit auswählen",
    "CH+OR": "vom Arbeitsansatz nehmen",
    "SH+EE+DY": "länger halten; Schluss",
    "OL+CHD+DY": "fortsetzen und umsetzen; Schluss",
    "OK+CHD+DY": "setzen und umsetzen; Schluss",
    "SH+OL": "halten und fortsetzen",
    "LSH+E+DY": "kurz spülen; Schluss",
    "CHK+E+Y": "den Posten kurz behandeln",
    "Y+T+Y": "den Posten einstellen und weiterführen",
    "SOLK+EE+Y": "den Posten länger auffangen",
    "SOLK+EE+DY": "länger auffangen; Schluss",
    "SH+E+OL": "kurz halten und fortsetzen",
    "S+OR": "einen Arbeitsansatz auswählen",
    "OK+SH+E+DY": "setzen, kurz halten; Schluss",
    "O+IIN": "auf der bezeichneten Stufe ausführen",
    "L+DY": "weiterleiten; Schluss",
    "K+EE+DY": "länger zugeben; Schluss",
    "D_ADDR+OR": "einen Teilansatz bilden",
    "D_ADDR+OL": "mit dem Teil fortsetzen",
    "CHK+EE+Y": "den Posten länger behandeln",
    "CHEO+R": "den Auszug markieren",
}


def main() -> None:
    events = read_tsv(P993 / "PASS993_2511_EVENT_INTERLINEAR.tsv")
    roots_raw = read_tsv(P993 / "PASS993_53_PORTABLE_ROOTS.tsv")
    old_templates = read_tsv(P982 / "PASS982_THIRTY_FORWARD_COMPOSITION_TEMPLATES.tsv")
    roots = {row["root_id"].removeprefix("R-"): row["atomic_meaning_de"] for row in roots_raw}
    old_recipes = {row["component_recipe"] for row in old_templates}

    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        if event["primary_layer"] == "PRODUCTIVE_ROOT_COMPOSITION":
            grouped[event["component_recipe"]].append(event)

    selected: list[tuple[str, list[dict[str, str]]]] = []
    for recipe, members in grouped.items():
        components = recipe.split("+")
        if (
            recipe not in old_recipes
            and len(components) >= 2
            and set(components) <= set(roots)
            and len(members) >= 3
        ):
            selected.append((recipe, members))
    selected.sort(key=lambda item: (-len(item[1]), item[0]))

    drawer_rows: list[dict[str, object]] = []
    for index, (recipe, members) in enumerate(selected, 1):
        components = recipe.split("+")
        pages = sorted({row["physical_page"] for row in members})
        surfaces = sorted({row["surface"] for row in members})
        literal = " · ".join(roots[component] for component in components)
        if len(pages) >= 2 and len(surfaces) >= 2:
            support = "MEHRSEITIG_UND_MEHRFÖRMIG"
        elif len(pages) >= 2:
            support = "MEHRSEITIG"
        else:
            support = "LOKAL_WIEDERHOLT"
        readings = []
        for row in members:
            reading = row["complete_working_reading_de"]
            if reading not in readings:
                readings.append(reading)
        drawer_rows.append(
            {
                "drawer_id": f"D2-{index:03d}",
                "component_recipe": recipe,
                "atomic_workshop_reading_de": literal,
                "natural_apprentice_reading_de": NATURAL.get(recipe, literal.lower()),
                "events": len(members),
                "surfaces": "|".join(surfaces),
                "pages": "|".join(pages),
                "page_count": len(pages),
                "support_kind": support,
                "example_event_ids": "|".join(row["event_id"] for row in members[:6]),
                "attested_context_readings_de": " || ".join(readings[:4]),
            }
        )
    write_tsv(
        HERE / "PASS994_SECOND_COMPOSITION_DRAWER.tsv",
        drawer_rows,
        [
            "drawer_id",
            "component_recipe",
            "atomic_workshop_reading_de",
            "natural_apprentice_reading_de",
            "events",
            "surfaces",
            "pages",
            "page_count",
            "support_kind",
            "example_event_ids",
            "attested_context_readings_de",
        ],
    )

    left = ["OK", "OT", "S", "CH", "OL", "O", "L", "P"]
    right = ["Y", "AIN", "AIIN", "AL", "AR", "AIR", "OR", "CTH"]
    grid_rows: list[dict[str, object]] = []
    for left_root in left:
        for right_root in right:
            recipe = f"{left_root}+{right_root}"
            members = grouped.get(recipe, [])
            grid_rows.append(
                {
                    "left_root": left_root,
                    "right_root": right_root,
                    "component_recipe": recipe,
                    "literal_prediction_de": f"{roots[left_root]} · {roots[right_root]}",
                    "status": "BELEGT" if members else "VERFÜGBAR_ABER_NICHT_BELEGT",
                    "events": len(members),
                    "surfaces": "|".join(sorted({row["surface"] for row in members})) if members else "NICHT_BELEGT",
                    "pages": "|".join(sorted({row["physical_page"] for row in members})) if members else "NICHT_BELEGT",
                }
            )
    write_tsv(
        HERE / "PASS994_EIGHT_BY_EIGHT_COMPOSITION_GRID.tsv",
        grid_rows,
        ["left_root", "right_root", "component_recipe", "literal_prediction_de", "status", "events", "surfaces", "pages"],
    )

    phrase_rows = drawer_rows[:20]
    write_tsv(
        HERE / "PASS994_TWENTY_APPRENTICE_PHRASES.tsv",
        phrase_rows,
        [
            "drawer_id",
            "component_recipe",
            "natural_apprentice_reading_de",
            "events",
            "surfaces",
            "pages",
            "attested_context_readings_de",
        ],
    )

    cross_page = sum(int(row["page_count"]) >= 2 for row in drawer_rows)
    multi_surface = sum(len(str(row["surfaces"]).split("|")) >= 2 for row in drawer_rows)
    observed_grid = sum(row["status"] == "BELEGT" for row in grid_rows)
    summary = {
        "status": "PASS",
        "second_drawer_families": len(drawer_rows),
        "second_drawer_events": sum(int(row["events"]) for row in drawer_rows),
        "cross_page_families": cross_page,
        "multi_surface_families": multi_surface,
        "composition_grid_cells": len(grid_rows),
        "observed_grid_cells": observed_grid,
        "new_roots": 0,
    }
    (HERE / "PASS994_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    top_lines = []
    for row in drawer_rows[:20]:
        top_lines.append(
            f"- `{row['component_recipe']}` → **{str(row['natural_apprentice_reading_de']).upper()}** "
            f"({row['events']} Vorkommen; {row['pages']})."
        )
    report = f"""# Pass 994 — zweite Kompositionsschublade

## Ergebnis

Das 30-Karten-Handbuch war zu knapp, aber der Fehler lag nicht im
Wurzelinventar. Auf den vierzehn Seiten stehen weitere **{len(drawer_rows)}
wiederkehrende Kompositionen** aus bereits bekannten Wurzeln. Sie decken
**{summary['second_drawer_events']} Ereignisse**; {cross_page} Familien stehen
auf mindestens zwei Seiten und {multi_surface} besitzen mehrere sichtbare
Schreibformen. Dafür wird **keine neue Wurzel** gebraucht.

Diese zweite Schublade ist genau das erwartete Zwischenstück eines
Werkstattcodebuchs: zu häufig, um jedes Vorkommen als freie Neuerfindung zu
lesen, aber zu selten, um jede Karte im kleinen Grunddeck auswendig zu lernen.

## Die zwanzig ergiebigsten Lesungen

{chr(10).join(top_lines)}

## 8×8-Wortbaukasten

Das separate Raster kreuzt acht linke Arbeitswurzeln mit acht rechten
Posten-, Mengen-, Ziel-, Quellen- und Zustandswurzeln. Eine leere Zelle ist
kein Widerspruch: der Schreiber muss keinen vollständigen kartesischen
Wortschatz benutzen. Sie ist eine **verfügbare, noch nicht belegte Bildung**,
die auf einer weiteren Seite sofort ohne neue Bedeutung lesbar wäre.

## Werkstattregel

1. Gelernte lange Fachkarte zuerst prüfen.
2. Sonst die bekannte Wurzelfolge von links nach rechts lesen.
3. Eine wiederkehrende Folge nach drei Sichtungen in die zweite Schublade
   aufnehmen.
4. Den natürlichen Satz aus Bildbesitzer und Register ergänzen, ohne den
   atomaren Kartenwert zu verändern.
5. Eine fehlende Kombination nicht erzwingen und keine neue Wurzel erfinden.

## Konsequenz

Die aktuelle Stärke des Modells liegt nun weniger in einzelnen spektakulären
Wortwetten als in seinem praktischen Wortbau: Grunddeck, zweite Schublade,
Fachkarten und lokale Bildnamen genügen gemeinsam für die volle Ausgabe. Das
ist weiterhin eine kreative Werkstatttheorie und keine historische
Entzifferungsbehauptung.
"""
    (HERE / "PASS994_REPORT.md").write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
