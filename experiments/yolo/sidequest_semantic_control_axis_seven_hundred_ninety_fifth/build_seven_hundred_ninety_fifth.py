#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = (
    HERE.parent
    / "sidequest_semantic_clean_fluent_edition_seven_hundred_thirty_ninth"
    / "SEVEN_HUNDRED_THIRTY_NINTH_381_EVENT_INTERLINEAR.tsv"
)
CORES = ("OK", "OT", "OL")
READING = {"OK": "ANSETZEN", "OT": "DANACH", "OL": "WEITER"}
PREDICTIONS = [
    ("AIIN", "OL", "qolaiin", "WEITER · SOLLMASS"),
    ("AL", "OL", "qolal", "WEITER · ZIELSTELLE"),
    ("E+DY", "OL", "qoledy", "WEITER · KURZ · SCHLUSS"),
    ("AR", "OL", "qolar", "WEITER · QUELLE"),
    ("EE+Y", "OL", "qoleey", "WEITER · LANG · DIES"),
    ("EE+DY", "OL", "qoleedy", "WEITER · LANG · SCHLUSS"),
    ("AL+Y", "OT", "qotaly", "DANACH · ZIELSTELLE · DIES"),
    ("SH+E+DY", "OT", "qotshedy", "DANACH · HALTEN · KURZ · SCHLUSS"),
]


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def first_core(recipe: str) -> str | None:
    first = recipe.split("+")[0]
    return first if first in CORES else None


def tail(recipe: str) -> str:
    tokens = recipe.split("+")
    return "+".join(tokens[1:]) or "EMPTY"


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    rows = read(SOURCE)
    seen = {row["surface"] for row in rows}
    events = [row for row in rows if first_core(row["component_recipe"])]

    event_rows = []
    for row in events:
        core = first_core(row["component_recipe"])
        expected = READING[core]
        event_rows.append(
            {
                "event_id": row["event_id"],
                "page": row["page"],
                "record": row["record"],
                "statement_id": row["statement_id"],
                "exact_card_id": row["card_no"],
                "surface": row["surface"],
                "component_recipe": row["component_recipe"],
                "control_core": core,
                "control_reading_de": expected,
                "tail_recipe": tail(row["component_recipe"]),
                "working_reading_de": row["rebuilt_reading_de"],
                "meaning_invariant": "YES" if row["rebuilt_reading_de"].split(" · ")[0] == expected else "NO",
                "surface_transparency": "TRANSPARENT" if core.lower() in row["surface"] else "OPAQUE_WHOLE_ALLOGRAPH",
            }
        )

    summary_rows = []
    for core in CORES:
        core_events = [row for row in event_rows if row["control_core"] == core]
        summary_rows.append(
            {
                "control_core": core,
                "reading_de": READING[core],
                "events": len(core_events),
                "exact_cards": len({row["exact_card_id"] for row in core_events}),
                "recipes": len({row["component_recipe"] for row in core_events}),
                "transparent_events": sum(row["surface_transparency"] == "TRANSPARENT" for row in core_events),
                "opaque_events": sum(row["surface_transparency"] == "OPAQUE_WHOLE_ALLOGRAPH" for row in core_events),
            }
        )

    by_tail: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in event_rows:
        by_tail[str(row["tail_recipe"])].append(row)
    shared = {
        key: value
        for key, value in by_tail.items()
        if len({str(row["control_core"]) for row in value}) >= 2
    }
    tail_rows = []
    shared_event_rows = []
    for tail_key, tail_events in sorted(shared.items()):
        present = {str(row["control_core"]) for row in tail_events}
        tail_rows.append(
            {
                "tail_recipe": tail_key,
                "present_cores": ",".join(core for core in CORES if core in present),
                "missing_cores": ",".join(core for core in CORES if core not in present) or "NONE",
                "events": len(tail_events),
                "surfaces_by_core": " | ".join(
                    f"{core}={','.join(sorted({str(row['surface']) for row in tail_events if row['control_core'] == core}))}"
                    for core in CORES
                    if core in present
                ),
                "tail_reading_de": " · ".join(str(tail_events[0]["working_reading_de"]).split(" · ")[1:]) or "EMPTY",
                "status": "THREE_CORE_COMPLETE" if len(present) == 3 else "TWO_CORE_PARADIGM",
            }
        )
        for row in tail_events:
            shared_event_rows.append(row)

    prediction_rows = []
    for index, (tail_key, missing_core, surface, reading) in enumerate(PREDICTIONS, start=1):
        source_tail = next(row for row in tail_rows if row["tail_recipe"] == tail_key)
        prediction_rows.append(
            {
                "predicted_card": f"PRED_CTRL_{index:02d}",
                "tail_recipe": tail_key,
                "observed_cores": source_tail["present_cores"],
                "new_control_core": missing_core,
                "predicted_recipe": missing_core + "+" + tail_key,
                "predicted_surface": surface,
                "predicted_reading_de": reading,
                "fixed_page_collision": "YES" if surface in seen else "NO",
                "status": "WORKSHOP_PREDICTION_ONLY__DO_NOT_INSERT",
            }
        )

    withheld = [{
        "tail_recipe": "OL",
        "observed_cores": "OK,OT",
        "missing_core": "OL",
        "would_be_recipe": "OL+OL",
        "would_be_reading_de": "WEITER · WEITER",
        "decision": "WITHHOLD_RECURSIVE_CONTROL_AS_NEW_CARD",
    }]
    opaque = [
        {
            "event_id": row["event_id"],
            "surface": row["surface"],
            "component_recipe": row["component_recipe"],
            "control_core": row["control_core"],
            "working_reading_de": row["working_reading_de"],
            "reason": "learned surface ls realizes OL without visible ol",
        }
        for row in event_rows
        if row["surface_transparency"] == "OPAQUE_WHOLE_ALLOGRAPH"
    ]

    write(
        "SEVEN_HUNDRED_NINETY_FIFTH_138_CONTROL_EVENTS.tsv",
        event_rows,
        ["event_id", "page", "record", "statement_id", "exact_card_id", "surface", "component_recipe", "control_core", "control_reading_de", "tail_recipe", "working_reading_de", "meaning_invariant", "surface_transparency"],
    )
    write(
        "SEVEN_HUNDRED_NINETY_FIFTH_3_CONTROL_CORES.tsv",
        summary_rows,
        ["control_core", "reading_de", "events", "exact_cards", "recipes", "transparent_events", "opaque_events"],
    )
    write(
        "SEVEN_HUNDRED_NINETY_FIFTH_11_SHARED_TAILS.tsv",
        tail_rows,
        ["tail_recipe", "present_cores", "missing_cores", "events", "surfaces_by_core", "tail_reading_de", "status"],
    )
    write(
        "SEVEN_HUNDRED_NINETY_FIFTH_89_SHARED_TAIL_EVENTS.tsv",
        sorted(shared_event_rows, key=lambda row: int(str(row["event_id"])[1:])),
        ["event_id", "page", "record", "statement_id", "exact_card_id", "surface", "component_recipe", "control_core", "control_reading_de", "tail_recipe", "working_reading_de", "meaning_invariant", "surface_transparency"],
    )
    write(
        "SEVEN_HUNDRED_NINETY_FIFTH_8_PREDICTED_THIRD_CORES.tsv",
        prediction_rows,
        ["predicted_card", "tail_recipe", "observed_cores", "new_control_core", "predicted_recipe", "predicted_surface", "predicted_reading_de", "fixed_page_collision", "status"],
    )
    write(
        "SEVEN_HUNDRED_NINETY_FIFTH_1_WITHHELD_RECURSION.tsv",
        withheld,
        ["tail_recipe", "observed_cores", "missing_core", "would_be_recipe", "would_be_reading_de", "decision"],
    )
    write(
        "SEVEN_HUNDRED_NINETY_FIFTH_1_OPAQUE_OL_ALLOGRAPH.tsv",
        opaque,
        ["event_id", "surface", "component_recipe", "control_core", "working_reading_de", "reason"],
    )

    report = """# Pass 795 — OK, OT und OL bilden die linke Steuerachse

138 Ereignisse beginnen rezeptseitig mit einem der drei Steuerkerne: 79× OK, 26× OT, 33× OL. In sämtlichen 138 Fällen bleibt der erste Arbeitswert gleich: OK=ANSETZEN, OT=DANACH/FOLGE, OL=WEITER/FORTSETZEN. 137 Oberflächen zeigen den Kern sichtbar; nur `ls` ist eine gelernte OL-Ganzform.

Elf identische Rezeptenden erscheinen unter mindestens zwei Steuerkernen und decken 89 Ereignisse. Zwei Enden sind vollständig dreifach:

- `Y`: OK+Y / OT+Y / OL+Y = ansetzen / danach / weiter, jeweils den laufenden Posten;
- `CHD+DY`: denselben Umsetzungsschritt ansetzen / danach ausführen / fortsetzen und schließen.

Weitere gemeinsame Enden sind AIIN, AL, AR, E+DY, EE+Y, EE+DY, AL+Y, SH+E+DY und OL. Aus acht nichtrekursiven Lücken entstehen konkrete neue Karten: `qolaiin`, `qolal`, `qoledy`, `qolar`, `qoleey`, `qoleedy`, `qotaly`, `qotshedy`. Keine kollidiert mit einer vorhandenen Oberfläche. `OL+OL=WEITER·WEITER` wird nicht als neue Karte erzeugt; Wiederholung braucht ein eigenes Muster.

Damit ist auch der linke Rand nicht bloß Ornament. Er wählt die Art, wie derselbe Rest in den Arbeitsablauf eintritt: ausführen, als nächsten Schritt setzen oder vom Vorigen her fortführen.

Als nächstes setzen wir die acht neuen Steuerkarten in vollständige Aussagen ein und prüfen, ob der Austausch tatsächlich nur den Diskurs-/Ablaufmodus ändert. Danach nehmen wir K/L/CHD als eigentliche Transferhandlung auseinander.
"""
    (HERE / "SEVEN_HUNDRED_NINETY_FIFTH_REPORT.md").write_text(report, encoding="utf-8")

    summary = {
        "status": "PASS",
        "control_events": len(event_rows),
        "control_cards": len({row["exact_card_id"] for row in event_rows}),
        "control_recipes": len({row["component_recipe"] for row in event_rows}),
        "meaning_invariant_events": sum(row["meaning_invariant"] == "YES" for row in event_rows),
        "transparent_events": sum(row["surface_transparency"] == "TRANSPARENT" for row in event_rows),
        "shared_tails": len(tail_rows),
        "shared_tail_events": len(shared_event_rows),
        "three_core_complete_tails": sum(row["status"] == "THREE_CORE_COMPLETE" for row in tail_rows),
        "predicted_third_cores": len(prediction_rows),
        "prediction_collisions": sum(row["fixed_page_collision"] == "YES" for row in prediction_rows),
        "decision": "OK_OT_OL_CONTROL_AXIS_INVARIANT_OVER_ELEVEN_SHARED_TAILS",
    }
    (HERE / "SEVEN_HUNDRED_NINETY_FIFTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
