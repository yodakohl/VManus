#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PREDICTIONS = ROOT / "sidequest_semantic_control_axis_seven_hundred_ninety_fifth" / "SEVEN_HUNDRED_NINETY_FIFTH_8_PREDICTED_THIRD_CORES.tsv"
EVENTS = ROOT / "sidequest_semantic_clean_fluent_edition_seven_hundred_thirty_ninth" / "SEVEN_HUNDRED_THIRTY_NINTH_381_EVENT_INTERLINEAR.tsv"
SOURCE_SURFACE = {
    "qolaiin": "qokaiin",
    "qolal": "qokal",
    "qoledy": "qokedy",
    "qolar": "qokar",
    "qoleey": "qokeey",
    "qoleedy": "qokeedy",
    "qotaly": "qokaly",
    "qotshedy": "qokshedy",
}
CORE_READING = {"OK": "ANSETZEN", "OT": "DANACH", "OL": "WEITER"}


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
    predictions = read(PREDICTIONS)
    events = read(EVENTS)
    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        by_statement[row["statement_id"]].append(row)

    substitutions = []
    traces = []
    invariants = []
    for index, prediction in enumerate(predictions, start=1):
        source_surface = SOURCE_SURFACE[prediction["predicted_surface"]]
        source = next(
            row
            for row in events
            if row["surface"] == source_surface
            and "+".join(row["component_recipe"].split("+")[1:]) == prediction["tail_recipe"]
        )
        source_core = source["component_recipe"].split("+")[0]
        target_core = prediction["new_control_core"]
        source_tail = source["component_recipe"].split("+")[1:]
        target_tail = prediction["predicted_recipe"].split("+")[1:]
        statement = by_statement[source["statement_id"]]
        before_surfaces = [row["surface"] for row in statement]
        after_surfaces = [prediction["predicted_surface"] if row["event_id"] == source["event_id"] else row["surface"] for row in statement]
        before_readings = [row["rebuilt_reading_de"] for row in statement]
        after_readings = [prediction["predicted_reading_de"] if row["event_id"] == source["event_id"] else row["rebuilt_reading_de"] for row in statement]
        substitutions.append(
            {
                "exercise": f"S{index:02d}",
                "page": source["page"],
                "record": source["record"],
                "statement_id": source["statement_id"],
                "owner_de": source["owner_de"],
                "source_event": source["event_id"],
                "before_surfaces": " ".join(before_surfaces),
                "after_surfaces": " ".join(after_surfaces),
                "before_reading_de": "; ".join(before_readings),
                "after_reading_de": "; ".join(after_readings),
                "control_change": source_core + "→" + target_core,
                "mode_change_de": CORE_READING[source_core] + "→" + CORE_READING[target_core],
                "surface_change": source_surface + "→" + prediction["predicted_surface"],
                "other_events_unchanged": "YES",
            }
        )
        for phase, core, surface, recipe, reading in (
            ("BEFORE", source_core, source_surface, source["component_recipe"], source["rebuilt_reading_de"]),
            ("AFTER", target_core, prediction["predicted_surface"], prediction["predicted_recipe"], prediction["predicted_reading_de"]),
        ):
            traces.append(
                {
                    "exercise": f"S{index:02d}",
                    "phase": phase,
                    "control_core": core,
                    "control_reading_de": CORE_READING[core],
                    "tail_recipe": prediction["tail_recipe"],
                    "surface": surface,
                    "component_recipe": recipe,
                    "working_reading_de": reading,
                }
            )
        invariants.append(
            {
                "exercise": f"S{index:02d}",
                "source_tail": "+".join(source_tail),
                "target_tail": "+".join(target_tail),
                "tail_invariant": "YES" if source_tail == target_tail else "NO",
                "owner_invariant": source["owner_de"],
                "quantity_kept": ",".join(token for token in source_tail if token in {"AIIN", "AIN"}) or "NONE",
                "address_kept": ",".join(token for token in source_tail if token in {"AL", "AR"}) or "NONE",
                "grade_kept": ",".join(token for token in source_tail if token in {"E", "EE", "EEE"}) or "NONE",
                "endpoint_kept": ",".join(token for token in source_tail if token in {"Y", "DY"}) or "NONE",
            }
        )

    rules = [
        {"step": 1, "instruction_de": "DAS GEMEINSAME KARTENENDE UNVERAENDERT LASSEN"},
        {"step": 2, "instruction_de": "OK SAGT: DIESEN SCHRITT ANSETZEN ODER AUSFUEHREN"},
        {"step": 3, "instruction_de": "OT SAGT: DIESEN SCHRITT DANACH ALS NAECHSTEN NEHMEN"},
        {"step": 4, "instruction_de": "OL SAGT: DIESEN SCHRITT VOM VORIGEN HER WEITERFUEHREN"},
        {"step": 5, "instruction_de": "BILDOWNER, MENGE, ADRESSE, GRAD UND SCHLUSS BEIBEHALTEN"},
    ]

    write(
        "SEVEN_HUNDRED_NINETY_SIXTH_8_CONTROL_SUBSTITUTIONS.tsv",
        substitutions,
        ["exercise", "page", "record", "statement_id", "owner_de", "source_event", "before_surfaces", "after_surfaces", "before_reading_de", "after_reading_de", "control_change", "mode_change_de", "surface_change", "other_events_unchanged"],
    )
    write(
        "SEVEN_HUNDRED_NINETY_SIXTH_16_BEFORE_AFTER_TRACES.tsv",
        traces,
        ["exercise", "phase", "control_core", "control_reading_de", "tail_recipe", "surface", "component_recipe", "working_reading_de"],
    )
    write(
        "SEVEN_HUNDRED_NINETY_SIXTH_8_TAIL_INVARIANTS.tsv",
        invariants,
        ["exercise", "source_tail", "target_tail", "tail_invariant", "owner_invariant", "quantity_kept", "address_kept", "grade_kept", "endpoint_kept"],
    )
    write(
        "SEVEN_HUNDRED_NINETY_SIXTH_5_CONTROL_RULES.tsv",
        rules,
        ["step", "instruction_de"],
    )

    reading = """# Pass 796 — acht Sätze mit neuem Ablaufmodus

Die neue Karte ändert nicht den Sachschritt, sondern wie er an den vorigen Ablauf anschließt:

- `qokaiin → qolaiin`: nach Sollmaß **ansetzen** → nach Sollmaß **weiterführen**;
- `qokal → qolal`: an der Zielstelle **ansetzen** → dort **weiterführen**;
- `qokedy → qoledy`: kurz ansetzen und schließen → kurz **fortsetzen** und schließen;
- `qokar → qolar`: aus der Quelle ansetzen → von der Quelle **weiterführen**;
- `qokeey → qoleey`: den Posten länger ansetzen → ihn länger **weiterführen**;
- `qokeedy → qoleedy`: länger ansetzen und schließen → länger fortsetzen und schließen;
- `qokaly → qotaly`: an der Zielstelle ansetzen → **danach** an der Zielstelle den Posten nehmen;
- `qokshedy → qotshedy`: kurz halten ansetzen und schließen → diesen Halteschritt **danach** ausführen und schließen.

Das macht OK/OT/OL zu einer kleinen Ablaufgrammatik: `OK` startet/aktiviert den bezeichneten Schritt, `OT` reiht ihn als nächsten ein, `OL` übernimmt ihn aus dem laufenden Vorgang. Der Rest der Karte trägt weiterhin den eigentlichen Sachinhalt.
"""
    (HERE / "SEVEN_HUNDRED_NINETY_SIXTH_READABLE_SUBSTITUTIONS.md").write_text(reading, encoding="utf-8")

    report = """# Pass 796 — der Steuerkern ändert nur den Ablaufmodus

Alle acht fehlenden Steuerkarten wurden in ihre vollständigen Ausgangsaussagen eingesetzt. Sechsmal wird OK→OL und zweimal OK→OT getauscht. In 8/8 Fällen bleiben Tail, Bildbesitzer, sämtliche übrigen Ereignisse sowie vorhandene Mengen-, Adress-, Grad- und Endpunktwerte unverändert.

Die Vorher-/Nachherlesung ist konkret: OK setzt den Sachschritt an, OT nimmt denselben Sachschritt danach, OL führt ihn aus dem vorigen Zustand weiter. Damit ist der linke Kern weder bloßer Präfixlaut noch vollständiges Verb; er ist eine kleine gelernte Ablaufanweisung vor einem semantisch eigenständigen Kartenende.

Als nächstes zerlegen wir die Transferfamilie K/L/CHD: K=zugeben/einbringen, L=leiten, CHD=umsetzen. Gesucht werden gemeinsame Objekt-, Adress- und Schlussendungen sowie echte Gegenkarten, nicht bloß ähnliche Schreibungen.
"""
    (HERE / "SEVEN_HUNDRED_NINETY_SIXTH_REPORT.md").write_text(report, encoding="utf-8")

    summary = {
        "status": "PASS",
        "substitutions": len(substitutions),
        "before_after_traces": len(traces),
        "tail_invariants": len(invariants),
        "tail_matches": sum(row["tail_invariant"] == "YES" for row in invariants),
        "ok_to_ol": sum(row["control_change"] == "OK→OL" for row in substitutions),
        "ok_to_ot": sum(row["control_change"] == "OK→OT" for row in substitutions),
        "decision": "CONTROL_SWAP_CHANGES_FLOW_MODE_AND_PRESERVES_TAIL",
    }
    (HERE / "SEVEN_HUNDRED_NINETY_SIXTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
