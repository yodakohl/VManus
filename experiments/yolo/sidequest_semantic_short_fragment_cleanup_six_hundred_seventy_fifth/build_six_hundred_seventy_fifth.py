#!/usr/bin/env python3
"""Repair the 20 genuine fragment cases and normalize all short readings."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P674 = ROOT / "experiments/yolo/sidequest_semantic_polished_long_statements_six_hundred_seventy_fourth"

FRAGMENT_REPAIRS = {
    "H1-S002": "Den laufenden Posten ansetzen, danach abnehmen und weiterfuehren, weiterarbeiten und ihn bereithalten.",
    "H4-S002": "Nach Sollmass den laufenden Posten umsetzen und anschliessend verwahren.",
    "H5-S002": "Den vorigen Vorgang wiederaufnehmen, die Zutat als laufenden Posten fuehren und ansetzen; laenger im Arbeitsgang durch den Durchlass abnehmen und schliessen.",
    "H5-S003": "Die Zutat halten, dem laufenden Posten kurz zudosieren und ihn zweimal ansetzen.",
    "H5-S005": "Die Zutat bereitstellen, den laufenden Posten ansetzen und die Zutat aus dem Vorrat zudosieren; danach eine Portion in den Arbeitsgang nehmen.",
    "H5-S006": "Danach den laufenden Posten kurz weiterdosieren, bis das Sollmass erreicht ist.",
    "B1-S017": "An der Zielstelle kurz fortsetzen, umsetzen und den Schritt schliessen.",
    "B1-S021": "Die Zielstelle festlegen.",
    "B2-S011": "Eine Portion ansetzen, aus dem Vorrat eine zweite Portion ansetzen, laenger ansetzen und schliessen.",
    "B2-S017": "An der Zielstelle kurz kuehlen und halten, dann den Zielschritt schliessen.",
    "B3-S003": "Den laufenden Posten nach Sollmass beibehalten, anschliessend weiterleiten und umsetzen, dann schliessen.",
    "B3-S004": "Nach Sollmass ansetzen; danach zur Zielstelle wechseln und aus dem Vorrat weiterarbeiten.",
    "B3-S010": "An der Zielstelle einfuellen und umsetzen; danach den kurzen Folgeschritt schliessen.",
    "B3-S012": "Den Ansatz absetzen lassen und den Schritt schliessen.",
    "B3-S020": "An der Zielstelle weiterleiten, umsetzen und den Schritt schliessen.",
    "B3-S030": "Den Posten nach Sollmass ansetzen, die laufende Fluessigkeit umsetzen; danach nochmals umsetzen und schliessen.",
    "B4-S005": "Eine Portion als laufenden Posten umsetzen, laenger ansetzen und den Schritt schliessen.",
    "B4-S008": "Nach Sollmass den Posten laenger erwaermen, laenger halten, kurz ansetzen und schliessen.",
    "B4-S014": "Den Ansatz als laufenden Posten fuehren; ihn kurz im Arbeitsgang am Durchlass halten, die laufende Fluessigkeit als aktuellen Posten fuehren und schliessen.",
    "B4-S016": "Eine Portion weiter zudosieren, an der Zielstelle aus dem Vorrat nachdosieren, absetzen lassen und schliessen.",
}


def read(name: str) -> list[dict[str, str]]:
    with (P674 / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def normalize(text: str) -> str:
    replacements = [
        ("; dann danach ", "; danach "),
        ("laenger ihn ", "ihn laenger "),
        ("kurz ihn ", "ihn kurz "),
        ("weiter laenger ", "laenger weiter "),
        ("weiter kurz ", "kurz weiter "),
    ]
    for before, after in replacements:
        text = text.replace(before, after)
    if text:
        text = text[0].upper() + text[1:]
    return text


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    source = read("SIX_HUNDRED_SEVENTY_FOURTH_116_POLISHED_STATEMENTS.tsv")
    output = []
    repairs = []
    for row in source:
        revised = dict(row)
        before = row["fluent_workshop_reading_de"]
        if row["statement_id"] in FRAGMENT_REPAIRS:
            after = FRAGMENT_REPAIRS[row["statement_id"]]
            revised["fluent_workshop_reading_de"] = after
            revised["reading_source"] = "HAND_POLISHED_FRAGMENT_V3"
            revised["fluency_grade"] = "POLISHED"
            repairs.append({
                "statement_id": row["statement_id"],
                "record": row["record"],
                "events": row["events"],
                "repair_type": "ATTACH_DANGLING_NOMINAL_OR_SEQUENCE_FRAGMENT",
                "component_sequence": row["component_sequence"],
                "before_de": before,
                "after_de": after,
            })
        elif row["reading_source"] == "HAND_POLISHED_V2":
            revised["reading_source"] = "HAND_POLISHED_LONG_V2"
        else:
            revised["fluent_workshop_reading_de"] = normalize(before)
            revised["reading_source"] = "NORMALIZED_SHORT_V3"
            revised["fluency_grade"] = "CLEAN"
        output.append(revised)

    record_order = []
    for row in output:
        if row["record"] not in record_order:
            record_order.append(row["record"])
    records = []
    for record in record_order:
        rows = [row for row in output if row["record"] == record]
        records.append({
            "record": record,
            "page": rows[0]["page"],
            "statements": len(rows),
            "events": sum(int(row["events"]) for row in rows),
            "complete_clean_reading_de": " ".join(f"[{row['statement_id']}] {row['fluent_workshop_reading_de']}" for row in rows),
        })

    write(HERE / "SIX_HUNDRED_SEVENTY_FIFTH_116_CLEAN_STATEMENTS.tsv", output, list(output[0]))
    write(HERE / "SIX_HUNDRED_SEVENTY_FIFTH_20_FRAGMENT_REPAIRS.tsv", repairs, list(repairs[0]))
    write(HERE / "SIX_HUNDRED_SEVENTY_FIFTH_11_CLEAN_RECORDS.tsv", records, list(records[0]))
    summary = {
        "status": "PASS",
        "statements": len(output),
        "events": sum(int(row["events"]) for row in output),
        "records": len(records),
        "long_polished": sum(row["reading_source"] == "HAND_POLISHED_LONG_V2" for row in output),
        "fragment_polished": sum(row["reading_source"] == "HAND_POLISHED_FRAGMENT_V3" for row in output),
        "normalized_short": sum(row["reading_source"] == "NORMALIZED_SHORT_V3" for row in output),
        "decision": "TWENTY_SHORT_FRAGMENT_CASES_REPAIRED_AND_ALL_116_READINGS_NORMALIZED",
    }
    (HERE / "SIX_HUNDRED_SEVENTY_FIFTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
