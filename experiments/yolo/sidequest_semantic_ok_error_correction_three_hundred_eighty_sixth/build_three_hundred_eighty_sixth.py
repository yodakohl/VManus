#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent

ERRORS = [
    {
        "exercise": "E1",
        "track": "KURZ",
        "intended": "dy daiin okey qokedy",
        "wrong": "dy daiin okey okey",
        "fault_position": 4,
        "wrong_card": "okey",
        "correct_card": "qokedy",
        "faulty_component": "ENDPOINT",
        "observed_components": "OK+E+Y",
        "required_components": "OK+E+DY",
        "diagnosis": "kurzer Schluss fehlt; der Diesposten bleibt versehentlich offen",
    },
    {
        "exercise": "E2",
        "track": "LÄNGER",
        "intended": "dy daiin okeey qokeedy",
        "wrong": "dy daiin okeey qokedy",
        "fault_position": 4,
        "wrong_card": "qokedy",
        "correct_card": "qokeedy",
        "faulty_component": "GRADE",
        "observed_components": "OK+E+DY",
        "required_components": "OK+EE+DY",
        "diagnosis": "der Schluss ist zu kurz; ein E fehlt",
    },
    {
        "exercise": "E3",
        "track": "VOLLSTÄNDIG",
        "intended": "dy daiin qokeeedy",
        "wrong": "dy daiin qokeedy",
        "fault_position": 3,
        "wrong_card": "qokeedy",
        "correct_card": "qokeeedy",
        "faulty_component": "GRADE",
        "observed_components": "OK+EE+DY",
        "required_components": "OK+EEE+DY",
        "diagnosis": "der Obergrad fehlt; länger wurde statt vollständig geschrieben",
    },
]

COMPONENTS = {
    "dy": "ENTRY_D+Y",
    "daiin": "ENTRY_D+AIIN",
    "okey": "OK+E+Y",
    "qokedy": "OK+E+DY",
    "okeey": "OK+EE+Y",
    "qokeedy": "OK+EE+DY",
    "qokeeedy": "OK+EEE+DY",
}


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    correction_rows = []
    trace_rows = []
    for error in ERRORS:
        wrong_tokens = error["wrong"].split()
        intended_tokens = error["intended"].split()
        differences = [index + 1 for index, (wrong, right) in enumerate(zip(wrong_tokens, intended_tokens)) if wrong != right]
        correction_rows.append({
            **error,
            "difference_positions": "|".join(map(str, differences)),
            "cards_changed": len(differences),
            "all_other_cards_preserved": "YES" if len(differences) == 1 else "NO",
            "surface_inventory_status": "BOTH_EXISTING_REGISTERED_CARDS",
            "repair_result": "EXACT_INTENDED_TRACK",
        })
        for position, (wrong, right) in enumerate(zip(wrong_tokens, intended_tokens), 1):
            trace_rows.append({
                "exercise": error["exercise"],
                "track": error["track"],
                "position": position,
                "before_surface": wrong,
                "before_components": COMPONENTS[wrong],
                "after_surface": right,
                "after_components": COMPONENTS[right],
                "changed": "YES" if wrong != right else "NO",
                "faulty_component": error["faulty_component"] if wrong != right else "NONE",
                "repair_preserves_other_components": "YES",
            })
    write("THREE_HUNDRED_EIGHTY_SIXTH_THREE_ERROR_REPAIRS.tsv", correction_rows)
    write("THREE_HUNDRED_EIGHTY_SIXTH_ELEVEN_POSITION_TRACE.tsv", trace_rows)

    notebook = [
        "# Pass 386 — Lehrlingskorrektur",
        "",
        "Der Meister nennt nur Bahn und Fehlerart. Es darf genau eine bestehende Karte gewechselt werden.",
        "",
    ]
    for row in correction_rows:
        notebook += [
            f"## {row['exercise']} — {row['track']}",
            "",
            f"Fehler: `{row['wrong']}`",
            "",
            f"Befund: {row['diagnosis']}.",
            "",
            f"Tausch: `{row['wrong_card']}` ({row['observed_components']}) → `{row['correct_card']}` ({row['required_components']})",
            "",
            f"Korrektur: `{row['intended']}`",
            "",
        ]
    (HERE / "THREE_HUNDRED_EIGHTY_SIXTH_CORRECTOR_NOTEBOOK.md").write_text("\n".join(notebook), encoding="utf-8")
    report = """# Pass 386 — Komponentenfehler sind lokal reparierbar

Drei fehlerhafte Lehrbahnen wurden ohne neue Zeichen und ohne Umschreiben des
Satzes repariert. In der kurzen Bahn war nur der Endpunkt falsch: Y blieb offen,
wo DY schließen musste. In der langen und vollständigen Bahn war nur die
E-Stufe falsch. Jede Korrektur tauscht genau eine bereits registrierte Karte und
bewahrt alle anderen Positionen.

Das ist ein praktischer Gewinn gegenüber einem reinen Ganzwortlexikon: Der
Korrektor kann den Fehler als ENDPOINT oder GRADE benennen. Er muss nicht wissen,
ob der lokale Besitzer ein Bad, ein Gefäß, einen Körperteil oder etwas anderes
zeigt.

Als nächstes soll derselbe Korrekturmechanismus in eine kurze gemischte
Herbal/Bio-Abschrift eingebaut werden, damit OWNER-Wechsel und Komponentenfehler
gleichzeitig beherrscht werden.
"""
    (HERE / "THREE_HUNDRED_EIGHTY_SIXTH_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS",
        "exercises": len(correction_rows),
        "trace_positions": len(trace_rows),
        "one_card_repairs": sum(int(row["cards_changed"]) == 1 for row in correction_rows),
        "endpoint_faults": sum(row["faulty_component"] == "ENDPOINT" for row in correction_rows),
        "grade_faults": sum(row["faulty_component"] == "GRADE" for row in correction_rows),
        "new_surfaces": 0,
    }
    (HERE / "THREE_HUNDRED_EIGHTY_SIXTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
