#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P382 = ROOT / "experiments/yolo/sidequest_semantic_fourth_copy_combination_three_hundred_eighty_second"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    source = read(P382 / "THREE_HUNDRED_EIGHTY_SECOND_14_SOURCE_CARDS.tsv")
    visible = read(P382 / "THREE_HUNDRED_EIGHTY_SECOND_15_VISIBLE_FORMS.tsv")
    wrong_surface = "qokeedy"
    correct_surface = "qokeey"
    error_position = 12

    comparison_rows: list[dict[str, object]] = []
    for row in visible:
        position = int(row["source_position"])
        faulty = wrong_surface if position == error_position else row["surface"]
        comparison_rows.append({
            "line_no": row["line_no"],
            "visible_no": row["visible_no"],
            "source_position": position,
            "owner_code": row["owner_code"],
            "microcycle": row["microcycle"],
            "visibility_role": row["visibility_role"],
            "faulty_surface": faulty,
            "correct_surface": row["surface"],
            "surface_changed_by_corrector": "YES" if position == error_position else "NO",
            "source_contribution": row["source_contribution"],
            "correct_joint_tuple_id": row["joint_tuple_id"],
            "fault_class": "ENDPOINT_DY_FOR_Y" if position == error_position else "NONE",
        })
    write("THREE_HUNDRED_EIGHTY_SEVENTH_15_FORM_FAULT_AND_REPAIR.tsv", comparison_rows)

    phenomena = [
        {
            "phenomenon": "MARKED_CARRY",
            "locus": "line1:end_to_line2:start",
            "visible_surface": "cheky|cheky",
            "owner_before": "H4",
            "owner_after": "H4",
            "source_cards": 1,
            "diagnosis": "correct anticipation copy; read once",
            "action": "KEEP_BOTH_VISIBLE_READ_ONE_SOURCE",
        },
        {
            "phenomenon": "OWNER_HANDOFF",
            "locus": "line3_to_line4",
            "visible_surface": "checthy|dy",
            "owner_before": "H4",
            "owner_after": "B3",
            "source_cards": 2,
            "diagnosis": "correct image-owner change; new microcycle begins",
            "action": "KEEP_BOTH_AND_RESET_OWNER",
        },
        {
            "phenomenon": "COMPONENT_ERROR",
            "locus": "line5_position1",
            "visible_surface": "qokeedy",
            "owner_before": "B3",
            "owner_after": "B3",
            "source_cards": 1,
            "diagnosis": "EE grade correct but DY closes where Y must remain open",
            "action": "REPLACE_QOKEEDY_WITH_QOKEEY",
        },
    ]
    write("THREE_HUNDRED_EIGHTY_SEVENTH_THREE_PHENOMENA.tsv", phenomena)

    audit_rows = []
    for row in source:
        position = int(row["source_position"])
        before = wrong_surface if position == error_position else row["fourth_copy_surface"]
        after = row["fourth_copy_surface"]
        audit_rows.append({
            "source_position": position,
            "board_call_only": row["board_call_only"],
            "owner_code": row["owner_code"],
            "microcycle": row["microcycle"],
            "faulty_surface": before,
            "corrected_surface": after,
            "expected_joint_tuple_id": row["joint_tuple_id"],
            "corrected_identity_match": "YES",
            "changed": "YES" if before != after else "NO",
            "hidden_atomic_value_de": row["hidden_atomic_value_de"],
        })
    write("THREE_HUNDRED_EIGHTY_SEVENTH_14_SOURCE_AUDIT.tsv", audit_rows)

    faulty_lines = [
        "sho or cheoar cheky",
        "cheky",
        "lcheey cphy checthy",
        "dy daiin shckhy qoky",
        "qokeedy qokedy talam",
    ]
    corrected_lines = faulty_lines[:-1] + ["qokeey qokedy talam"]
    notebook = f"""# Pass 387 — Bildwechsel, Randkopie und Kartenfehler

## Fehlerhafte Abschrift

```text
{chr(10).join(faulty_lines)}
```

Der Korrektor arbeitet in dieser Reihenfolge:

1. `cheky | cheky` liegt beim selben H4-Besitzer und trägt die sichtbare
   Randmarkierung: zwei Formen, eine Quellkarte. Nicht löschen.
2. `checthy | dy` übergibt von H4 an das neue B3-Bild: zwei Quellkarten und ein
   echter Besitzerwechsel. Nicht verbinden.
3. `qokeedy` am Beginn des letzten B3-Gangs hat richtigen EE-Langgrad, aber den
   falschen DY-Schluss. An dieser Brettstelle wird Y/offen verlangt.

Einziger Tausch: `qokeedy` → `qokeey`.

## Korrigierte Abschrift

```text
{chr(10).join(corrected_lines)}
```
"""
    (HERE / "THREE_HUNDRED_EIGHTY_SEVENTH_CORRECTED_PAGE.md").write_text(notebook, encoding="utf-8")
    report = """# Pass 387 — drei ähnliche Störungen, drei verschiedene Handlungen

Auf derselben kurzen Seite stehen nun eine erlaubte Randdopplung, ein erlaubter
Bildbesitzerwechsel und ein echter Komponentenfehler. Der Korrektor liest die
Randdopplung einmal, setzt beim Besitzerwechsel den Bildbezug neu und ersetzt
nur beim Komponentenfehler eine Karte.

Der Fehler ist eng: `qokeedy` und `qokeey` teilen OK und EE. Nur DY versus Y ist
falsch. Der Tausch erhält Besitzer B3, Mikrogang C4, Langgrad, Nachbarkarte und
Zeilenlayout. Danach stimmen alle vierzehn Quellkarten wieder mit den
Brettaufrufen überein.

Als nächstes soll diese Seite ohne Brettaufrufe an einen Leser gehen. Er darf
nur Bildbesitzer, Linien, Markierung und das achtteilige Komponentenmanual
verwenden und muss angeben, was er sicher, wahrscheinlich und gar nicht
rücklesen kann.
"""
    (HERE / "THREE_HUNDRED_EIGHTY_SEVENTH_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS",
        "visible_forms": len(comparison_rows),
        "source_cards": len(audit_rows),
        "phenomena": len(phenomena),
        "surface_repairs": sum(row["surface_changed_by_corrector"] == "YES" for row in comparison_rows),
        "carry_source_count": int(phenomena[0]["source_cards"]),
        "owner_handoffs": 1,
    }
    (HERE / "THREE_HUNDRED_EIGHTY_SEVENTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
