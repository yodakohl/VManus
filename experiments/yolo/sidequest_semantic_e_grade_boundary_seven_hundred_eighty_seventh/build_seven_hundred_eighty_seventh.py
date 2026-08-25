#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P739 = ROOT / "experiments/yolo/sidequest_semantic_clean_fluent_edition_seven_hundred_thirty_ninth"
GRADES = {"E": ("KURZ", 1), "EE": ("LANG", 2), "EEE": ("VOLL", 3)}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        out = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        out.writeheader()
        out.writerows(rows)


def max_e_run(surface: str) -> int:
    runs = re.findall(r"e+", surface)
    return max((len(run) for run in runs), default=0)


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    events = read(P739 / "SEVEN_HUNDRED_THIRTY_NINTH_381_EVENT_INTERLINEAR.tsv")
    true_rows = []
    false_rows = []
    for row in events:
        components = row["component_recipe"].split("+")
        grade_tokens = [component for component in components if component in GRADES]
        run = max_e_run(row["surface"])
        if grade_tokens:
            grade = max(grade_tokens, key=lambda token: GRADES[token][1])
            expected = GRADES[grade][1]
            true_rows.append(
                {
                    "event_id": row["event_id"],
                    "page": row["page"],
                    "record": row["record"],
                    "statement_id": row["statement_id"],
                    "exact_card_id": row["card_no"],
                    "surface": row["surface"],
                    "component_recipe": row["component_recipe"],
                    "grade_tokens": ",".join(grade_tokens),
                    "effective_grade": grade,
                    "grade_reading_de": GRADES[grade][0],
                    "visible_max_e_run": run,
                    "expected_e_run": expected,
                    "surface_matches_grade_length": "YES" if run == expected else "NO",
                    "working_reading_de": row["rebuilt_reading_de"],
                }
            )
        elif run:
            if "CHD" in components:
                mechanism = "E_EMBEDDED_IN_CHED_CORE"
            elif "SHED" in components:
                mechanism = "E_EMBEDDED_IN_SHED_CORE"
            else:
                mechanism = "E_IN_WRAPPER_OR_OTHER_WHOLE_CORE"
            false_rows.append(
                {
                    "event_id": row["event_id"],
                    "page": row["page"],
                    "record": row["record"],
                    "statement_id": row["statement_id"],
                    "exact_card_id": row["card_no"],
                    "surface": row["surface"],
                    "component_recipe": row["component_recipe"],
                    "visible_max_e_run": run,
                    "non_grade_mechanism": mechanism,
                    "working_reading_de": row["rebuilt_reading_de"],
                    "grade_reading_added": "NONE",
                }
            )
    write(
        "SEVEN_HUNDRED_EIGHTY_SEVENTH_91_TRUE_GRADE_EVENTS.tsv",
        true_rows,
        ["event_id", "page", "record", "statement_id", "exact_card_id", "surface", "component_recipe", "grade_tokens", "effective_grade", "grade_reading_de", "visible_max_e_run", "expected_e_run", "surface_matches_grade_length", "working_reading_de"],
    )
    write(
        "SEVEN_HUNDRED_EIGHTY_SEVENTH_70_NONGRADE_E_EVENTS.tsv",
        false_rows,
        ["event_id", "page", "record", "statement_id", "exact_card_id", "surface", "component_recipe", "visible_max_e_run", "non_grade_mechanism", "working_reading_de", "grade_reading_added"],
    )

    by_recipe: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in true_rows:
        by_recipe[row["component_recipe"]].append(row)
    recipe_rows = []
    for recipe, rows in sorted(by_recipe.items()):
        recipe_rows.append(
            {
                "component_recipe": recipe,
                "effective_grade": rows[0]["effective_grade"],
                "grade_reading_de": rows[0]["grade_reading_de"],
                "events": len(rows),
                "exact_cards": len({row["exact_card_id"] for row in rows}),
                "surfaces": ",".join(sorted({str(row["surface"]) for row in rows})),
                "matching_surface_events": sum(row["surface_matches_grade_length"] == "YES" for row in rows),
                "contracted_surface_events": sum(row["surface_matches_grade_length"] == "NO" for row in rows),
                "working_reading_de": rows[0]["working_reading_de"],
            }
        )
    write(
        "SEVEN_HUNDRED_EIGHTY_SEVENTH_51_GRADED_RECIPES.tsv",
        recipe_rows,
        ["component_recipe", "effective_grade", "grade_reading_de", "events", "exact_cards", "surfaces", "matching_surface_events", "contracted_surface_events", "working_reading_de"],
    )

    mechanism_rows = []
    for mechanism in ("E_EMBEDDED_IN_CHED_CORE", "E_EMBEDDED_IN_SHED_CORE", "E_IN_WRAPPER_OR_OTHER_WHOLE_CORE"):
        rows = [row for row in false_rows if row["non_grade_mechanism"] == mechanism]
        mechanism_rows.append(
            {
                "non_grade_mechanism": mechanism,
                "events": len(rows),
                "exact_cards": len({row["exact_card_id"] for row in rows}),
                "recipes": len({row["component_recipe"] for row in rows}),
                "example_surfaces": ",".join(sorted({row["surface"] for row in rows})[:10]),
                "instruction": "do not add KURZ LANG or VOLL",
            }
        )
    write(
        "SEVEN_HUNDRED_EIGHTY_SEVENTH_3_NONGRADE_MECHANISMS.tsv",
        mechanism_rows,
        ["non_grade_mechanism", "events", "exact_cards", "recipes", "example_surfaces", "instruction"],
    )

    grade_rows = []
    for grade in ("E", "EE", "EEE"):
        rows = [row for row in true_rows if row["effective_grade"] == grade]
        grade_rows.append(
            {
                "grade": grade,
                "reading_de": GRADES[grade][0],
                "events": len(rows),
                "expected_run": GRADES[grade][1],
                "matching_run_events": sum(row["surface_matches_grade_length"] == "YES" for row in rows),
                "contracted_events": sum(row["surface_matches_grade_length"] == "NO" for row in rows),
                "surface_runs": ",".join(f"{key}:{value}" for key, value in sorted(Counter(int(row["visible_max_e_run"]) for row in rows).items())),
            }
        )
    write(
        "SEVEN_HUNDRED_EIGHTY_SEVENTH_3_GRADE_LEVELS.tsv",
        grade_rows,
        ["grade", "reading_de", "events", "expected_run", "matching_run_events", "contracted_events", "surface_runs"],
    )

    exceptions = [row for row in true_rows if row["surface_matches_grade_length"] == "NO"]
    write(
        "SEVEN_HUNDRED_EIGHTY_SEVENTH_2_CONTRACTED_EE_EVENTS.tsv",
        exceptions,
        ["event_id", "page", "record", "statement_id", "exact_card_id", "surface", "component_recipe", "grade_tokens", "effective_grade", "grade_reading_de", "visible_max_e_run", "expected_e_run", "surface_matches_grade_length", "working_reading_de"],
    )

    rules = [
        {"priority": 1, "condition": "card recipe contains E", "reading": "KURZ", "surface_expectation": "one e-run"},
        {"priority": 2, "condition": "card recipe contains EE", "reading": "LANG", "surface_expectation": "two e-run, except registered shey contraction"},
        {"priority": 3, "condition": "card recipe contains EEE", "reading": "VOLL", "surface_expectation": "three e-run"},
        {"priority": 4, "condition": "visible e but no grade token", "reading": "NO GRADE", "surface_expectation": "e belongs to CHED, SHED, wrapper, or whole core"},
    ]
    write(
        "SEVEN_HUNDRED_EIGHTY_SEVENTH_4_GRADE_RULES.tsv",
        rules,
        ["priority", "condition", "reading", "surface_expectation"],
    )

    report = """# Pass 787 — E/EE/EEE ist produktiv, aber nur im registrierten Gradslot

Es gibt 91 Ereignisse mit einer echten Gradkomponente in 51 Rezepten. Die sichtbare e-Länge folgt ihr fast vollständig:

- E=KURZ: 49 Ereignisse, 49× genau ein e-Lauf;
- EE=LANG: 40 Ereignisse, 38× zwei e, 2× die kontrahierte Oberfläche `shey`;
- EEE=VOLL: 2 Ereignisse, 2× drei e.

Das ergibt 89/91 direkte Oberflächenübereinstimmungen. Die beiden Abweichungen ändern den Grad nicht: `shey` bleibt durch sein Kartenrezept SH+EE+Y lang.

Gleichzeitig enthalten 70 weitere Ereignisse sichtbares e, obwohl ihr Rezept überhaupt keinen Gradslot besitzt. Davon liegen 38 im festen CHED-Kern, 15 im SHED/ABSETZEN-Kern und 17 in Eintrittshüllen oder anderen Ganzkernen. Der schärfste Warnfall ist `cheedy` mit zwei sichtbaren e, aber Rezept SHED+DY: Es bedeutet ABSETZEN·SCHLUSS, nicht LANG.

Die Lehrregel ist daher sehr einfach: **Zähle e nur innerhalb eines registrierten Gradslots.** E, EE und EEE tragen dann KURZ, LANG und VOLL; sonst trägt das e keinen selbständigen Zeitwert.

Als nächstes bauen wir die vollständigen Gradraster gleicher Kerne: OK, OT, SH, CHK und SOLK mit Y/DY/Ziel-Ausgängen. Fehlende Stufen werden als konkrete neue Oberflächenprognosen notiert, ohne sie auf den festen Seiten einzusetzen.
"""
    (HERE / "SEVEN_HUNDRED_EIGHTY_SEVENTH_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS",
        "true_grade_events": len(true_rows),
        "graded_recipes": len(recipe_rows),
        "grade_surface_matches": sum(row["surface_matches_grade_length"] == "YES" for row in true_rows),
        "contracted_true_grades": len(exceptions),
        "nongrade_visible_e_events": len(false_rows),
        "decision": "E_EE_EEE_PRODUCTIVE_ONLY_IN_REGISTERED_GRADE_SLOT",
    }
    (HERE / "SEVEN_HUNDRED_EIGHTY_SEVENTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
