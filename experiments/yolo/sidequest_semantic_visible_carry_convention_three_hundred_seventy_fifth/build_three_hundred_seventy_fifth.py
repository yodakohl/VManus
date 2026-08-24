#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    candidates = [
        {
            "candidate": "EXTRA_MARGIN_GAP",
            "description_de": "Antizipationskarte nach doppeltem Normalabstand in letzter Randposition.",
            "new_glyphs": 0,
            "apprentice_rules": 2,
            "survives_hand_change": "YES",
            "collision_risk": "LOW",
            "selected": "YES",
        },
        {
            "candidate": "PREPOSED_PUNCTUS",
            "description_de": "Kleiner Punkt unmittelbar vor der Antizipationskarte.",
            "new_glyphs": 1,
            "apprentice_rules": 2,
            "survives_hand_change": "LIKELY",
            "collision_risk": "MEDIUM",
            "selected": "NO",
        },
        {
            "candidate": "RAISED_MARGIN_CARD",
            "description_de": "Antizipationskarte leicht erhöht in der Randzone.",
            "new_glyphs": 0,
            "apprentice_rules": 3,
            "survives_hand_change": "UNCERTAIN",
            "collision_risk": "MEDIUM",
            "selected": "NO",
        },
    ]
    cases = [
        {
            "case_id": "A_LEGAL_CHEKY",
            "left_predecessor": "chckhy",
            "left_margin_form": "cheky",
            "gap_units_before_margin_form": 2,
            "margin_position": "FINAL",
            "right_initial_form": "cheky",
            "same_owner": "YES",
            "corrector_decision": "LICENSED_READ_ONCE",
            "source_cards_for_pair": 1,
        },
        {
            "case_id": "B_LEGAL_QOKEEY",
            "left_predecessor": "chaiin",
            "left_margin_form": "qokeey",
            "gap_units_before_margin_form": 2,
            "margin_position": "FINAL",
            "right_initial_form": "qokeey",
            "same_owner": "YES",
            "corrector_decision": "LICENSED_READ_ONCE",
            "source_cards_for_pair": 1,
        },
        {
            "case_id": "C_UNMARKED_AIIIN_DUPLICATE",
            "left_predecessor": "oky",
            "left_margin_form": "aiin",
            "gap_units_before_margin_form": 1,
            "margin_position": "FINAL",
            "right_initial_form": "aiin",
            "same_owner": "YES",
            "corrector_decision": "UNLICENSED_DUPLICATE_FLAG_FOR_MASTER",
            "source_cards_for_pair": "UNDECIDED_UNTIL_MASTER_CORRECTION",
        },
    ]
    layouts = [
        {
            "layout_id": "A_WIDTH20_MARKED",
            "line_no": 1,
            "visible_line": "or kain chckhy  cheky",
            "double_gap_before": "cheky",
            "line_role": "LEGAL_CARRY_LEFT",
        },
        {
            "layout_id": "A_WIDTH20_MARKED",
            "line_no": 2,
            "visible_line": "cheky oky",
            "double_gap_before": "NONE",
            "line_role": "LEGAL_CARRY_RIGHT_AND_CYCLE_END",
        },
        {
            "layout_id": "A_WIDTH20_MARKED",
            "line_no": 3,
            "visible_line": "aiin okeey qokedy",
            "double_gap_before": "NONE",
            "line_role": "NEW_CYCLE",
        },
        {
            "layout_id": "B_WIDTH30_MARKED",
            "line_no": 1,
            "visible_line": "chor chkain shckhy cheky choky",
            "double_gap_before": "NONE",
            "line_role": "CYCLE_END",
        },
        {
            "layout_id": "B_WIDTH30_MARKED",
            "line_no": 2,
            "visible_line": "chaiin  qokeey",
            "double_gap_before": "qokeey",
            "line_role": "LEGAL_CARRY_LEFT",
        },
        {
            "layout_id": "B_WIDTH30_MARKED",
            "line_no": 3,
            "visible_line": "qokeey qokedy",
            "double_gap_before": "NONE",
            "line_role": "LEGAL_CARRY_RIGHT",
        },
    ]
    write("THREE_HUNDRED_SEVENTY_FIFTH_THREE_CONVENTIONS.tsv", candidates)
    write("THREE_HUNDRED_SEVENTY_FIFTH_THREE_DECISION_CASES.tsv", cases)
    write("THREE_HUNDRED_SEVENTY_FIFTH_SIX_MARKED_LINES.tsv", layouts)
    manual = """# Pass 375 — sichtbare Randzone der Übungswerkstatt

## Gewählte Regel

1. Eine Vorwegnahme steht als letzte Karte nach **doppeltem Normalabstand**.
2. Dieselbe Karte beginnt die nächste Zeile beim selben Besitzer.
3. Nur wenn beides gilt, wird sie einmal gelesen.
4. Gleiche Rand- und Anfangskarte ohne doppelten Abstand wird nicht automatisch
   gerettet; der Meister entscheidet, ob Fehler oder echte Wiederholung.

## Markierte Fassungen

```text
or kain chckhy  cheky
cheky oky
aiin okeey qokedy

chor chkain shckhy cheky choky
chaiin  qokeey
qokeey qokedy
```

Der Abstand ist eine neu erfundene Lehrmarke. Er wird nicht in die Lesung
aufgenommen und nicht als Eigenschaft der realen Voynich-Seiten ausgegeben.
"""
    (HERE / "THREE_HUNDRED_SEVENTY_FIFTH_CARRY_MANUAL.md").write_text(manual, encoding="utf-8")
    report = """# Pass 375 — positive Antizipationsmarke

Unter drei einfachen Werkstattkonventionen gewinnt die zusätzliche Randlücke:
kein neues Zeichen, zwei Regeln und stabil bei verschiedenen Schreibpaletten.
Sie lizenziert die beiden Übungskopien `cheky` und `qokeey`, während ein
unmarkiertes `aiin | aiin` offen als Fehler oder echte Wiederholung zum Meister
zurückgeht. Damit wird keine unsichtbare Unterscheidung behauptet.

Als nächstes soll dieselbe Markierung in eine komplette Musterseite mit Bildraum,
zwei Besitzern und vier Mikrogängen eingebaut werden, um die Regeln gemeinsam zu
sehen: Bild zuerst, Restbreite, Besitzerwechsel, Kartenwahl und Randkopie.
"""
    (HERE / "THREE_HUNDRED_SEVENTY_FIFTH_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS",
        "candidate_conventions": len(candidates),
        "selected_convention": "EXTRA_MARGIN_GAP",
        "new_glyphs": 0,
        "marked_layout_lines": len(layouts),
        "licensed_carries": sum(row["corrector_decision"] == "LICENSED_READ_ONCE" for row in cases),
        "unlicensed_duplicates": sum(row["corrector_decision"] == "UNLICENSED_DUPLICATE_FLAG_FOR_MASTER" for row in cases),
        "real_page_claim": "NONE",
    }
    (HERE / "THREE_HUNDRED_SEVENTY_FIFTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
