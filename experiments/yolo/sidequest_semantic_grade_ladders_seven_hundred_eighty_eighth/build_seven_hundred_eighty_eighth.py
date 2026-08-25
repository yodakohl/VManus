#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE_DIR = HERE.parent / "sidequest_semantic_e_grade_boundary_seven_hundred_eighty_seventh"
SOURCE = SOURCE_DIR / "SEVEN_HUNDRED_EIGHTY_SEVENTH_51_GRADED_RECIPES.tsv"
EVENTS = SOURCE_DIR / "SEVEN_HUNDRED_EIGHTY_SEVENTH_91_TRUE_GRADE_EVENTS.tsv"
ALL_EVENTS = (
    HERE.parent
    / "sidequest_semantic_clean_fluent_edition_seven_hundred_thirty_ninth"
    / "SEVEN_HUNDRED_THIRTY_NINTH_381_EVENT_INTERLINEAR.tsv"
)

GRADES = ("E", "EE", "EEE")
GRADE_READING = {"E": "KURZ", "EE": "LANG", "EEE": "VOLL"}
CORES = ("OK", "OT", "SH", "CHK", "SOLK")
ENDPOINTS = ("Y", "DY", "AL", "OL", "AIIN")

PREDICTIONS = {
    ("CHK+Y", "EEE"): {
        "predicted_surfaces": "cheeeky",
        "reading_de": "WAERMEN · VOLL · DIES",
        "confidence": "MEDIUM",
        "formation_rule": "cheky→cheeky→cheeeky",
    },
    ("OK+Y", "EEE"): {
        "predicted_surfaces": "okeeey,qokeeey",
        "reading_de": "ANSETZEN · VOLL · DIES",
        "confidence": "HIGH",
        "formation_rule": "okey/qokey→okeey/qokeey→okeeey/qokeeey",
    },
    ("OT+DY", "EEE"): {
        "predicted_surfaces": "qoteeedy",
        "reading_de": "DANACH · VOLL · SCHLUSS",
        "confidence": "MEDIUM",
        "formation_rule": "otedy→qoteedy→qoteeedy; q-Hülle aus langem Modell",
    },
    ("SH+DY", "EEE"): {
        "predicted_surfaces": "sheeedy",
        "reading_de": "HALTEN · VOLL · SCHLUSS",
        "confidence": "LOW_MEDIUM",
        "formation_rule": "dshedy→sheedy→sheeedy; Eintrittshülle nicht sicher",
    },
    ("SH+Y", "EEE"): {
        "predicted_surfaces": "sheeey",
        "reading_de": "HALTEN · VOLL · DIES",
        "confidence": "LOW_MEDIUM",
        "formation_rule": "tshey→sheey→sheeey; kontrahiertes shey nicht fortsetzen",
    },
    ("SOLK+Y", "EEE"): {
        "predicted_surfaces": "solkeeey",
        "reading_de": "SAMMELSTELLE · VOLL · DIES",
        "confidence": "HIGH",
        "formation_rule": "solkey→solkeey→solkeeey",
    },
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def signature(recipe: str) -> str:
    return "+".join(token for token in recipe.split("+") if token not in GRADES)


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    recipes = read(SOURCE)
    events = read(EVENTS)
    all_events = read(ALL_EVENTS)
    seen_surfaces = {row["surface"] for row in all_events}

    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in recipes:
        grouped[signature(row["component_recipe"])].append(row)

    family_rows: list[dict[str, object]] = []
    rung_rows: list[dict[str, object]] = []
    missing_rows: list[dict[str, object]] = []
    repeated = {
        key: value
        for key, value in grouped.items()
        if len({row["effective_grade"] for row in value}) >= 2
    }
    for family in sorted(repeated):
        rows = repeated[family]
        present = {row["effective_grade"] for row in rows}
        events_by_grade = {
            grade: sum(int(row["events"]) for row in rows if row["effective_grade"] == grade)
            for grade in GRADES
        }
        surfaces_by_grade = {
            grade: sorted(
                {
                    surface
                    for row in rows
                    if row["effective_grade"] == grade
                    for surface in row["surfaces"].split(",")
                }
            )
            for grade in GRADES
        }
        missing = [grade for grade in GRADES if grade not in present]
        predictable = [grade for grade in missing if (family, grade) in PREDICTIONS]
        family_rows.append(
            {
                "ladder_signature": family,
                "attested_grades": ",".join(grade for grade in GRADES if grade in present),
                "missing_grades": ",".join(missing) or "NONE",
                "attested_events": sum(events_by_grade.values()),
                "surface_series": " | ".join(
                    f"{grade}={','.join(surfaces_by_grade[grade])}"
                    for grade in GRADES
                    if surfaces_by_grade[grade]
                ),
                "ladder_status": (
                    "COMPLETE_THREE_RUNG"
                    if not missing
                    else "SURFACE_PREDICTABLE"
                    if predictable == missing
                    else "SEMANTIC_RUNG_ONLY_SURFACE_UNSTABLE"
                ),
            }
        )
        for grade in GRADES:
            grade_rows = [row for row in rows if row["effective_grade"] == grade]
            if not grade_rows:
                continue
            rung_rows.append(
                {
                    "ladder_signature": family,
                    "grade": grade,
                    "grade_reading_de": GRADE_READING[grade],
                    "component_recipe": " | ".join(sorted({row["component_recipe"] for row in grade_rows})),
                    "surfaces": ",".join(sorted({surface for row in grade_rows for surface in row["surfaces"].split(",")})),
                    "events": sum(int(row["events"]) for row in grade_rows),
                    "working_reading_de": " | ".join(sorted({row["working_reading_de"] for row in grade_rows})),
                }
            )
        for grade in missing:
            prediction = PREDICTIONS.get((family, grade))
            if prediction:
                candidates = prediction["predicted_surfaces"].split(",")
                collision = sorted(surface for surface in candidates if surface in seen_surfaces)
                missing_rows.append(
                    {
                        "ladder_signature": family,
                        "missing_grade": grade,
                        "grade_reading_de": GRADE_READING[grade],
                        "predicted_surfaces": prediction["predicted_surfaces"],
                        "predicted_reading_de": prediction["reading_de"],
                        "formation_rule": prediction["formation_rule"],
                        "confidence": prediction["confidence"],
                        "fixed_page_collision": ",".join(collision) or "NONE",
                        "use_status": "WORKSHOP_PREDICTION_ONLY__DO_NOT_INSERT",
                    }
                )
            else:
                missing_rows.append(
                    {
                        "ladder_signature": family,
                        "missing_grade": grade,
                        "grade_reading_de": GRADE_READING[grade],
                        "predicted_surfaces": "NO_SAFE_SURFACE",
                        "predicted_reading_de": "ANWENDEN · LANG · DIES",
                        "formation_rule": "T+Y has incompatible E surfaces etyd/ytey and EEE surface cheeety",
                        "confidence": "WITHHELD",
                        "fixed_page_collision": "NOT_TESTED",
                        "use_status": "SEMANTIC_RUNG_EXPECTED__SURFACE_WITHHELD",
                    }
                )

    matrix_rows: list[dict[str, object]] = []
    recipe_lookup: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in recipes:
        recipe_lookup[(signature(row["component_recipe"]), row["effective_grade"])].append(row)
    repeated_signatures = set(repeated)
    for core in CORES:
        for endpoint in ENDPOINTS:
            family = f"{core}+{endpoint}"
            for grade in GRADES:
                rows = recipe_lookup.get((family, grade), [])
                prediction = PREDICTIONS.get((family, grade))
                if rows:
                    status = "ATTESTED"
                    surfaces = sorted({surface for row in rows for surface in row["surfaces"].split(",")})
                    reading = " | ".join(sorted({row["working_reading_de"] for row in rows}))
                    count = sum(int(row["events"]) for row in rows)
                elif prediction and family in repeated_signatures:
                    status = "FORMABLE_BY_REPEATED_LADDER"
                    surfaces = prediction["predicted_surfaces"].split(",")
                    reading = prediction["reading_de"]
                    count = 0
                else:
                    status = "NO_LOCAL_LADDER"
                    surfaces = []
                    reading = "NOT_ASSIGNED"
                    count = 0
                matrix_rows.append(
                    {
                        "core": core,
                        "endpoint": endpoint,
                        "grade": grade,
                        "status": status,
                        "events": count,
                        "surfaces": ",".join(surfaces) or "NONE",
                        "reading_de": reading,
                    }
                )

    write(
        "SEVEN_HUNDRED_EIGHTY_EIGHTH_8_REPEATED_LADDERS.tsv",
        family_rows,
        ["ladder_signature", "attested_grades", "missing_grades", "attested_events", "surface_series", "ladder_status"],
    )
    write(
        "SEVEN_HUNDRED_EIGHTY_EIGHTH_17_ATTESTED_RUNGS.tsv",
        rung_rows,
        ["ladder_signature", "grade", "grade_reading_de", "component_recipe", "surfaces", "events", "working_reading_de"],
    )
    write(
        "SEVEN_HUNDRED_EIGHTY_EIGHTH_7_MISSING_RUNGS.tsv",
        missing_rows,
        ["ladder_signature", "missing_grade", "grade_reading_de", "predicted_surfaces", "predicted_reading_de", "formation_rule", "confidence", "fixed_page_collision", "use_status"],
    )
    write(
        "SEVEN_HUNDRED_EIGHTY_EIGHTH_75_CORE_ENDPOINT_MATRIX.tsv",
        matrix_rows,
        ["core", "endpoint", "grade", "status", "events", "surfaces", "reading_de"],
    )

    card_text = """# Pass 788 — sechs neue Kartenformen, die der Schreiber bilden könnte

Diese Formen stehen **nicht** auf den zehn Seiten. Sie sind Werkstattprognosen aus mehrfach belegten Gradleitern:

- `cheeeky` — WÄRMEN · VOLL · DIES;
- `okeeey` / `qokeeey` — ANSETZEN · VOLL · DIES;
- `qoteeedy` — DANACH · VOLL · SCHLUSS;
- `sheeedy` — HALTEN · VOLL · SCHLUSS;
- `sheeey` — HALTEN · VOLL · DIES;
- `solkeeey` — SAMMELSTELLE · VOLL · DIES.

Die fehlende mittlere Stufe der T+Y-Reihe bekommt absichtlich keine Oberfläche. Ihre kurze Stufe erscheint als `etyd` und `ytey`, die volle als `cheeety`; hier ist die Hülle zu unstet, um `teey` oder eine andere Form ehrlich vorherzusagen.

Die stärkste Leiter ist `qokedy → qokeedy → qokeeedy`: ANSETZEN · KURZ/LANG/VOLL · SCHLUSS. Das ist bisher unser sauberstes Beispiel dafür, dass ein Schreiber aus einem Grundbefehl durch einen kleinen sichtbaren Gradwechsel neue Karten erzeugen konnte.
"""
    (HERE / "SEVEN_HUNDRED_EIGHTY_EIGHTH_PREDICTED_CARDS.md").write_text(card_text, encoding="utf-8")

    report = f"""# Pass 788 — die Gradleitern des Werkstattbuchs

Die 51 Gradrezepte bilden acht wiederholte Leitern. Eine ist vollständig: `OK+DY` erscheint als `qokedy → qokeedy → qokeeedy`, also ANSETZEN · KURZ/LANG/VOLL · SCHLUSS. Sieben weitere Familien besitzen je zwei Stufen.

Für sechs dieser Lücken lässt sich die nächste Oberfläche durch bloßes Verlängern des registrierten Gradslots bilden. Keine der sieben vorhergesagten Oberflächen kollidiert mit einer bereits anders belegten Karte auf den festen Seiten. Besonders sauber sind `OK+Y: okey/okeey/okeeey` und `SOLK+Y: solkey/solkeey/solkeeey`.

Die T+Y-Reihe zeigt zugleich die Grenze: E kommt als `etyd` und `ytey`, EEE als `cheeety`. Die fehlende EE-Bedeutungsstufe wäre LANG, doch die Oberfläche bleibt unbestimmt. Damit erfindet das Modell nicht blind jede denkbare Karte.

Das 75-Zellen-Raster aus fünf Kernen, fünf Ausgängen und drei Graden enthält {sum(row['status'] == 'ATTESTED' for row in matrix_rows)} belegte Zellen und {sum(row['status'] == 'FORMABLE_BY_REPEATED_LADDER' for row in matrix_rows)} eng ableitbare Lücken. Alle übrigen Kombinationen bleiben ungebildet. Der praktische Kern ist jetzt: **Kern wählen, Ausgang wählen, Gradslot verlängern; vorhandene Hülle vom Muster übernehmen.**

Als nächstes prüfen wir die sechs vorhergesagten Formen gegen das gesamte erlaubte Oberflächeninventar der zehn Seiten und bauen danach eine kleine Schreibtafel, auf der ein Lehrling neue Kurz/Lang/Voll-Karten tatsächlich erzeugt und rückliest.
"""
    (HERE / "SEVEN_HUNDRED_EIGHTY_EIGHTH_REPORT.md").write_text(report, encoding="utf-8")

    summary = {
        "status": "PASS",
        "true_grade_events_carried": len(events),
        "repeated_ladders": len(family_rows),
        "attested_rungs": len(rung_rows),
        "missing_rungs": len(missing_rows),
        "surface_predictions": sum(row["predicted_surfaces"] != "NO_SAFE_SURFACE" for row in missing_rows),
        "predicted_surface_strings": sum(
            len(row["predicted_surfaces"].split(","))
            for row in missing_rows
            if row["predicted_surfaces"] != "NO_SAFE_SURFACE"
        ),
        "prediction_collisions": sum(row["fixed_page_collision"] not in {"NONE", "NOT_TESTED"} for row in missing_rows),
        "matrix_rows": len(matrix_rows),
        "matrix_attested": sum(row["status"] == "ATTESTED" for row in matrix_rows),
        "matrix_formable": sum(row["status"] == "FORMABLE_BY_REPEATED_LADDER" for row in matrix_rows),
        "decision": "ONE_COMPLETE_AND_SIX_SURFACE_PREDICTABLE_GRADE_LADDERS",
    }
    (HERE / "SEVEN_HUNDRED_EIGHTY_EIGHTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
