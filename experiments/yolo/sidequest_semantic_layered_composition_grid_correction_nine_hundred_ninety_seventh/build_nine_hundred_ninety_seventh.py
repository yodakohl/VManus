#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
P996 = HERE.parent / "sidequest_semantic_canonical_scribe_workshop_sixth_edition_nine_hundred_ninety_sixth"


def read_tsv(name: str) -> list[dict[str, str]]:
    with (P996 / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


NATURAL_EMPTY = {
    "OK+CTH": "gebrauchsfertig setzen",
    "OT+CTH": "danach den bereiten Posten nehmen",
    "S+Y": "diesen Posten auswählen",
    "S+CTH": "den bereiten Posten auswählen",
    "CH+Y": "diesen Posten nehmen",
    "CH+AIN": "eine Portion nehmen",
    "CH+AR": "aus der Quelle nehmen",
    "CH+CTH": "den bereiten Posten nehmen",
    "OL+AIN": "mit einer Portion fortsetzen",
    "OL+AL": "zum Ziel fortsetzen",
    "OL+AIR": "im Lauf fortsetzen",
    "OL+CTH": "mit dem bereiten Posten fortsetzen",
    "O+AL": "am Ziel ausführen",
    "O+AIR": "den Lauf ausführen",
    "O+OR": "den Ansatz ausführen",
    "O+CTH": "den bereiten Gang ausführen",
    "L+AIN": "eine Portion leiten",
    "L+AIR": "durch den Lauf leiten",
    "L+CTH": "den bereiten Posten leiten",
    "P+AIN": "eine Portion einsetzen",
    "P+AIIN": "nach Maß einsetzen",
    "P+AL": "am Ziel einsetzen",
    "P+AIR": "in den Lauf einsetzen",
    "P+OR": "in den Ansatz einsetzen",
    "P+CTH": "den bereiten Posten einsetzen",
}


def main() -> None:
    events = read_tsv("PASS996_2511_EVENT_INTERLINEAR.tsv")
    roots = {
        row["root_id"].removeprefix("R-"): row["atomic_meaning_de"]
        for row in read_tsv("PASS996_53_PORTABLE_ROOTS.tsv")
    }
    by_recipe: dict[str, list[dict[str, str]]] = defaultdict(list)
    by_surface: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        by_recipe[event["component_recipe"]].append(event)
        by_surface[event["surface"]].append(event)

    left = ["OK", "OT", "S", "CH", "OL", "O", "L", "P"]
    right = ["Y", "AIN", "AIIN", "AL", "AR", "AIR", "OR", "CTH"]
    local_layers = {"LOCAL_ADDRESS_OR_KENNING", "DRUG_LABEL_NOMENCLATOR", "IMAGE_OWNED_SPECIALIST_CARD"}
    grid: list[dict[str, object]] = []
    empty: list[dict[str, object]] = []
    collisions: list[dict[str, object]] = []

    for left_root in left:
        for right_root in right:
            recipe = f"{left_root}+{right_root}"
            members = by_recipe.get(recipe, [])
            layers = Counter(row["primary_layer"] for row in members)
            productive = layers["PRODUCTIVE_ROOT_COMPOSITION"]
            formula = layers["COMMON_FORMULA_CARD"]
            specialist = layers["MEMORIZED_SPECIALIST_WHOLE_WORD"]
            local = sum(layers[layer] for layer in local_layers)
            if productive:
                status = "BELEGT_PRODUKTIV"
            elif formula:
                status = "BELEGT_ALS_GELERNTE_FORMEL"
            elif specialist:
                status = "NUR_GELERNTE_FACHKARTE"
            elif local:
                status = "NUR_LOKALE_ADRESSE"
            else:
                status = "NICHT_BELEGT"

            candidate_surface = f"{left_root}{right_root}".lower()
            candidate_members = by_surface.get(candidate_surface, [])
            competing = [row for row in candidate_members if row["component_recipe"] != recipe]
            collision = bool(competing)
            collision_values = sorted({f"{row['component_recipe']}@{row['primary_layer']}" for row in competing})
            content_members = [
                row for row in members
                if row["primary_layer"] in {"PRODUCTIVE_ROOT_COMPOSITION", "COMMON_FORMULA_CARD", "MEMORIZED_SPECIALIST_WHOLE_WORD"}
            ]
            grid_row = {
                "left_root": left_root,
                "right_root": right_root,
                "component_recipe": recipe,
                "literal_prediction_de": f"{roots[left_root]} · {roots[right_root]}",
                "status": status,
                "productive_events": productive,
                "formula_card_events": formula,
                "specialist_events": specialist,
                "local_address_events": local,
                "content_events": len(content_members),
                "content_surfaces": "|".join(sorted({row["surface"] for row in content_members})) or "KEINE",
                "content_pages": "|".join(sorted({row["physical_page"] for row in content_members})) or "KEINE",
                "simple_candidate_surface": candidate_surface,
                "candidate_surface_collision": "JA" if collision else "NEIN",
                "collision_with": "|".join(collision_values) or "KEINE",
            }
            grid.append(grid_row)
            if status == "NICHT_BELEGT":
                empty_row = dict(grid_row)
                empty_row["natural_available_reading_de"] = NATURAL_EMPTY[recipe]
                empty_row["workshop_instruction_de"] = (
                    "nicht mit dieser Kurzform schreiben; sie ist bereits anders vergeben"
                    if collision
                    else "verfügbar, aber auf den vierzehn Seiten nicht gebraucht"
                )
                empty.append(empty_row)
            if collision:
                collisions.append(
                    {
                        "component_recipe": recipe,
                        "intended_reading_de": NATURAL_EMPTY.get(recipe, f"{roots[left_root]} {roots[right_root]}"),
                        "blocked_candidate_surface": candidate_surface,
                        "already_read_as": "|".join(collision_values),
                        "observed_collision_events": len(competing),
                        "scribe_solution_de": "Ganzkarte beibehalten oder eine andere Schreibform wählen",
                    }
                )

    write_tsv(
        "PASS997_CORRECTED_LAYERED_EIGHT_BY_EIGHT_GRID.tsv",
        grid,
        list(grid[0]),
    )
    write_tsv(
        "PASS997_TWENTY_FIVE_TRUE_EMPTY_CELLS.tsv",
        empty,
        list(empty[0]),
    )
    write_tsv(
        "PASS997_THREE_SURFACE_COLLISIONS.tsv",
        collisions,
        list(collisions[0]),
    )

    counts = Counter(row["status"] for row in grid)
    summary = {
        "status": "PASS",
        "grid_cells": len(grid),
        "status_counts": dict(counts),
        "content_attested_cells": sum(row["status"] in {"BELEGT_PRODUKTIV", "BELEGT_ALS_GELERNTE_FORMEL"} for row in grid),
        "specialist_only_cells": counts["NUR_GELERNTE_FACHKARTE"],
        "local_only_cells": counts["NUR_LOKALE_ADRESSE"],
        "true_empty_cells": counts["NICHT_BELEGT"],
        "surface_collisions": len(collisions),
    }
    (HERE / "PASS997_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    report = """# Pass 997 — korrigiertes Wortbauraster

## Der gefundene Fehler

Pass 994 zählte im 8×8-Raster nur frei produktive Ereignisse. Dadurch wurden
zwölf bereits gelernte Formelkarten – etwa `OK+Y`, `OK+AIN` und `OT+AR` –
fälschlich als unbelegt ausgegeben. Die 70 Familien der zweiten Schublade
bleiben richtig; nur das Raster war zu eng gefiltert.

## Korrigierte Bilanz

- 24 Zellen sind frei produktiv belegt;
- 12 weitere sind als gelernte Formelkarten belegt;
- 1 Zelle (`L+AR`) existiert nur als Fachkarte;
- 2 Zellen (`OT+AIR`, `O+AR`) stehen nur in lokalen Adressen;
- 25 Zellen sind im festen Korpus wirklich unbenutzt.

Damit sind **36 statt 24** Zellen im laufenden Inhalt belegt. Die Formelkarten
sind keine Widerlegung der Wurzeln: Sie sind die häufigen Kombinationen, deren
komplette Schreibform der Lehrling als Einheit lernt.

## Drei echte Oberflächenkollisionen

- `S+Y` würde schlicht `sy` ergeben, aber `sy` ist bereits eine Y-/POSTEN-Form;
- `CH+Y` würde `chy` ergeben, aber `chy` ist ebenfalls eine Y-/POSTEN-Form;
- `CH+AR` würde `char` ergeben, aber `char` ist bereits die QUELLE-Karte.

Der Schreiber kann diese Bedeutungen trotzdem ausdrücken, darf dafür aber
nicht die naive Kurzform verwenden. Genau dafür braucht ein gemischtes
Codebuch Ganzkarten und alternative Rendererformen.

## Was die 25 leeren Zellen bedeuten

Sie sind keine fehlenden Übersetzungen. Jede besitzt bereits eine lesbare
Werkstattbedeutung, zum Beispiel `P+AIIN` = **nach Maß einsetzen** oder
`OL+AIR` = **im Lauf fortsetzen**. Zweiundzwanzig einfache Kurzformen sind noch
frei; drei sind durch bestehende Karten blockiert. Das liefert eine konkrete
Schreibregel für weitere Seiten, ohne das Wörterbuch zu vergrößern.
"""
    (HERE / "PASS997_REPORT.md").write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
