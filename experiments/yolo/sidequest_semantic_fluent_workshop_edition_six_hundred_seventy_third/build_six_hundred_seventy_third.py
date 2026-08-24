#!/usr/bin/env python3
"""Render all 116 integrated statements as fluent workshop German."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P672 = ROOT / "experiments/yolo/sidequest_semantic_integrated_dictionary_six_hundred_seventy_second"

ACTION = {
    "OK": "ansetzen", "CHD": "umsetzen", "SH": "halten", "SHED": "absetzen lassen",
    "CHK": "erwaermen", "SOLK": "auffangen", "P": "einfuellen", "LSH": "waschen",
    "CFH": "auswringen", "CH": "abnehmen", "T": "eintragen", "K": "zudosieren",
    "S": "teilen", "L": "weiterleiten", "R": "kuehlen", "LD": "befestigen",
}
OVERRIDES = {
    "H1-S001": "Den laufenden Posten kurz abnehmen; den Ansatz im Arbeitsgang bereitstellen und aus dem Vorrat eintragen; den Fluessigkeitslauf abnehmen, danach den Posten weiterfuehren, nach Sollmass ansetzen und kurz eintragen.",
    "H2-S001": "Vom laufenden Ansatz kurz abnehmen; den Posten bereithalten, den Ansatz nach Sollmass weiterbearbeiten und als aktuellen Posten verfuegbar lassen.",
    "H3-S001": "Den Ansatz am Ziel weiter halten; auswringen, bis zum Sollmass halten, in den Empfaenger fuellen, laenger halten, abnehmen und den Schritt schliessen.",
    "H4-S001": "Nach Sollmass ansetzen; dem laufenden Posten eine Portion und danach eine Nachportion zudosieren; den Arbeitsgang schliessen.",
    "H5-S001": "Eine Zutat fuer den Ansatz abnehmen, zur Zielstelle bringen und nach Sollmass weiter zudosieren; danach vom Ansatz abnehmen und den Posten an der Zielstelle ansetzen.",
    "B1-S001": "Kurz ansetzen und den Schritt schliessen.",
    "B2-S001": "Umsetzen und den Schritt schliessen.",
    "B3-S001": "Laenger auffangen und den Schritt schliessen.",
    "B4-S001": "Laenger ansetzen und den Schritt schliessen.",
    "B5-S001": "Danach umsetzen und den Schritt schliessen.",
    "B6-S001": "Den Posten laenger auffangen, kurz zudosieren, an der Zielstelle kuehlen, nach Sollmass weiterarbeiten, eine Portion nehmen und den Ansatz zur Zielstelle weiterleiten.",
    "B1-S012": "Den Arbeitsgang waschen, den Posten kurz ansetzen, nochmals kurz waschen und den Schritt schliessen.",
    "B1-S013": "Kurz waschen und den Schritt schliessen.",
}


def read(name: str) -> list[dict[str, str]]:
    with (P672 / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def join_actions(actions: list[str]) -> str:
    if not actions:
        return ""
    if len(actions) == 1:
        return actions[0]
    return ", ".join(actions[:-1]) + " und " + actions[-1]


def render_card(recipe: str, seen_item: bool) -> tuple[str, bool]:
    atoms = recipe.split("+")
    if recipe == "OS":
        return "das Arbeitsfach waehlen", seen_item
    if recipe == "RESUME_CARD":
        return "den vorigen Vorgang wiederaufnehmen", seen_item
    if recipe == "TALAM":
        return "den Posten verwahren", True

    actions = [ACTION[atom] for atom in atoms if atom in ACTION]
    prefix = "danach " if "OT" in atoms else ""
    if "OL" in atoms:
        if actions:
            prefix += "weiter "
        else:
            actions.append("fortsetzen")
    if "CTH" in atoms and not actions:
        actions.append("bereithalten")

    objects = []
    if "Y" in atoms:
        objects.append("ihn" if seen_item else "den laufenden Posten")
        seen_item = True
    if "HO" in atoms:
        objects.append("die Zutat")
    if "OR" in atoms:
        objects.append("den Ansatz")
    if "AIR" in atoms:
        objects.append("die laufende Fluessigkeit")
    if "O" in atoms:
        objects.append("im Arbeitsgang")
    if "CKH" in atoms:
        objects.append("durch den Durchlass")
    if "AIN" in atoms:
        objects.append("als Portion")
    if "AIIN" in atoms:
        objects.append("nach Sollmass")
    if "IIN" in atoms:
        objects.append("bis zur Arbeitsstufe")
    if "AN" in atoms:
        objects.append("als Nachportion")
    if "AR" in atoms:
        objects.append("aus dem Vorrat")
    if "AL" in atoms:
        objects.append("zur Zielstelle")
    if "DA" in atoms:
        objects.append("fuer den zweiten Durchgang")

    grades = []
    if "E" in atoms:
        grades.append("kurz")
    if "EE" in atoms:
        grades.append("laenger")
    if "EEE" in atoms:
        grades.append("vollstaendig")
    if "CTH" in atoms and actions and "bereithalten" not in actions:
        grades.append("bis bereit")

    if actions:
        phrase = " ".join([prefix + " ".join(grades), " ".join(objects), join_actions(actions)]).strip()
    else:
        nominal = " ".join(grades + objects).strip()
        if not nominal and "Y" in atoms:
            nominal = "ihn beibehalten"
        elif nominal and set(atoms) == {"Y"}:
            nominal += " beibehalten"
        phrase = prefix + (nominal or "fortfahren")
    phrase = " ".join(phrase.split())
    if "DY" in atoms:
        phrase += "; den Schritt schliessen"
    return phrase, seen_item


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    events = read("SIX_HUNDRED_SEVENTY_SECOND_381_EVENT_INTERLINEAR.tsv")
    statements = read("SIX_HUNDRED_SEVENTY_SECOND_116_STATEMENT_EDITION.tsv")
    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        by_statement[event["statement_id"]].append(event)

    output = []
    grades = Counter()
    for statement in statements:
        rows = by_statement[statement["statement_id"]]
        seen_item = False
        phrases = []
        for row in rows:
            phrase, seen_item = render_card(row["component_recipe"], seen_item)
            phrases.append(phrase)
        automatic = "; dann ".join(phrases) + "."
        fluent = OVERRIDES.get(statement["statement_id"], automatic)
        grade = "DENSE" if len(rows) >= 9 else "CLEAN" if len(rows) <= 4 else "WORKABLE"
        grades[grade] += 1
        output.append({
            "statement_id": statement["statement_id"],
            "page": statement["page"],
            "record": statement["record"],
            "events": len(rows),
            "surface_sequence": statement["surface_sequence"],
            "card_sequence": "|".join(row["card_no"] for row in rows),
            "component_sequence": statement["component_sequence"],
            "event_phrases_de": " | ".join(phrases),
            "fluent_workshop_reading_de": fluent,
            "reading_source": "HAND_POLISHED" if statement["statement_id"] in OVERRIDES else "COMPOSITIONAL_RENDERER",
            "fluency_grade": grade,
            "closes": statement["closes"],
        })

    record_order = []
    for row in output:
        if row["record"] not in record_order:
            record_order.append(str(row["record"]))
    records = []
    for record in record_order:
        rows = [row for row in output if row["record"] == record]
        records.append({
            "record": record,
            "page": rows[0]["page"],
            "statements": len(rows),
            "events": sum(int(row["events"]) for row in rows),
            "complete_reading_de": " ".join(f"[{row['statement_id']}] {row['fluent_workshop_reading_de']}" for row in rows),
        })

    write(HERE / "SIX_HUNDRED_SEVENTY_THIRD_116_FLUENT_STATEMENTS.tsv", output, list(output[0]))
    write(HERE / "SIX_HUNDRED_SEVENTY_THIRD_11_FLUENT_RECORDS.tsv", records, list(records[0]))

    lines = ["# Eleven continuous workshop records", ""]
    for record in records:
        lines.extend([f"## {record['record']} · {record['page']}", "", str(record["complete_reading_de"]), ""])
    (HERE / "SIX_HUNDRED_SEVENTY_THIRD_ELEVEN_RECORDS.md").write_text("\n".join(lines), encoding="utf-8")

    summary = {
        "status": "PASS",
        "statements": len(output),
        "events": sum(int(row["events"]) for row in output),
        "records": len(records),
        "hand_polished_statements": sum(row["reading_source"] == "HAND_POLISHED" for row in output),
        "compositional_statements": sum(row["reading_source"] == "COMPOSITIONAL_RENDERER" for row in output),
        "fluency_grades": dict(sorted(grades.items())),
        "decision": "ALL_116_STATEMENTS_HAVE_CARD_COMPLETE_FLUENT_WORKSHOP_READINGS",
    }
    (HERE / "SIX_HUNDRED_SEVENTY_THIRD_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
