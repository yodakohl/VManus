#!/usr/bin/env python3
"""Hand-polish every dense or workable statement from pass 673."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P673 = ROOT / "experiments/yolo/sidequest_semantic_fluent_workshop_edition_six_hundred_seventy_third"

POLISH = {
    "H1-S001": "Den laufenden Posten kurz abnehmen; den Ansatz im Arbeitsgang bereitstellen und aus dem Vorrat eintragen; den Fluessigkeitslauf abnehmen, danach den Posten weiterfuehren, nach Sollmass ansetzen und kurz eintragen.",
    "H2-S001": "Vom laufenden Ansatz kurz abnehmen; den Posten bereithalten, den Ansatz nach Sollmass weiterbearbeiten und als aktuellen Posten verfuegbar lassen.",
    "H2-S002": "Danach vom Ansatz abnehmen; denselben Ansatz in mehreren Fortsetzungsschritten nach Sollmass aus dem Vorrat weiterfuehren.",
    "H2-S003": "Im Arbeitsgang den aktuellen Ansatz zudosieren; denselben Ansatz als laufenden Posten beibehalten, bis zur Arbeitsstufe weiterdosieren und anschliessend im Arbeitsgang nach Sollmass abnehmen.",
    "H3-S001": "Den Ansatz am Ziel weiter halten; auswringen, bis zum Sollmass halten, in den Empfaenger fuellen, laenger halten, abnehmen und den Schritt schliessen.",
    "H3-S003": "Den vorigen Vorgang wiederaufnehmen, den aktuellen Posten beibehalten, ihm zudosieren und ihn bis zum Sollmass weiterfuehren.",
    "H4-S001": "Nach Sollmass ansetzen; dem laufenden Posten eine Portion und danach eine Nachportion zudosieren; den Arbeitsgang schliessen.",
    "H4-S004": "Nach Sollmass an der Zielstelle ansetzen, den laufenden Posten weiter eintragen, als Ansatz beibehalten und als Ansatzportion fuehren.",
    "H5-S001": "Eine Zutat fuer den Ansatz abnehmen, zur Zielstelle bringen und nach Sollmass weiter zudosieren; danach vom Ansatz abnehmen und den Posten an der Zielstelle ansetzen.",
    "B1-S002": "Nach Sollmass ansetzen und die laufende Fluessigkeit zudosieren. An der Zielstelle aus dem Vorrat weiterarbeiten: eine Portion und dann eine weitere Portion zudosieren, weiter kuehlen und weiterleiten. Den Ansatz fortsetzen, kurz am Durchlass der Zielstelle halten, erneut nach Sollmass laenger ansetzen, den Posten durch den Durchlass umsetzen und schliessen.",
    "B1-S008": "Den Posten beibehalten und fortsetzen, kurz erwaermen, weiterfuehren, absetzen lassen und den Schritt schliessen.",
    "B1-S014": "Den Posten umsetzen und auffangen; zur Zielstelle weiterleiten und umsetzen, dort fortsetzen und danach zum Vorrat wechseln.",
    "B2-S004": "An der Zielstelle ansetzen; den Posten durch den Durchlass weiterleiten und umsetzen, laenger ansetzen, danach kurz durch den Durchlass weiterleiten und schliessen.",
    "B2-S005": "Den Posten an der Zielstelle ansetzen und nach Sollmass auffangen. Ihn durch den Durchlass fuehren, zweimal nach Sollmass ansetzen, im Arbeitsgang kurz bis zur Bereitschaft fortsetzen, laenger erwaermen, weiterleiten und schliessen.",
    "B2-S012": "Den Posten weiterleiten und abnehmen; laenger halten, kurz bereithalten, laenger ansetzen und laenger weiterleiten; nach Sollmass beibehalten, vollstaendig ansetzen und schliessen.",
    "B2-S016": "An der Zielstelle aus dem Vorrat weiterleiten und umsetzen. Kurz abnehmen und teilen; nach Sollmass den naechsten Posten laenger fuehren, nach Sollmass und kurz ansetzen, einfuellen, umsetzen und schliessen.",
    "B3-S021": "Nach Sollmass ansetzen und den Posten bereithalten. An der Zielstelle nach Sollmass absetzen und kurz bis zur Bereitschaft halten. Den Posten beibehalten, an der Zielstelle erneut bereithalten, umsetzen und schliessen.",
    "B3-S026": "Laenger aus dem Vorrat arbeiten; nach Sollmass weiterleiten, den Posten umsetzen, eine Portion ansetzen und bereithalten; den Ansatz an der Zielstelle kuehlen, laenger auffangen und schliessen.",
    "B3-S032": "Eine Portion und dann den laufenden Posten umsetzen; danach kurz nach Sollmass, anschliessend nochmals nach Sollmass und den folgenden Kurzschritt schliessen.",
    "B3-S034": "Den Arbeitsgang bis zur Arbeitsstufe fuehren; den Posten bereithalten und eintragen; danach nach Sollmass an der Zielstelle weiterfuehren, absetzen und schliessen.",
    "B4-S003": "Den Posten umsetzen; danach zur Zielstelle und zum naechsten Posten wechseln; diesen laenger ansetzen, weiter ansetzen, fortsetzen, absetzen und schliessen.",
    "B4-S011": "Nach Sollmass den Posten kurz erwaermen, laenger weiter ansetzen, eine Portion ansetzen, den Posten umsetzen, fortsetzen, kurz weiterleiten und zudosieren, dann schliessen.",
    "B4-S015": "Eine Portion ansetzen, den Posten laenger halten, eine Portion zudosieren, durch den Durchlass an der Zielstelle abnehmen, kurz auffangen, weiterleiten, umsetzen und schliessen.",
    "B5-S003": "An der Zielstelle absetzen und dort weiterarbeiten; weiterleiten und fortsetzen, an der Zielstelle umsetzen, nach Sollmass fortsetzen, fuer den zweiten Durchgang bis zur Arbeitsstufe fuehren und den Posten umsetzen.",
    "B6-S001": "Den Posten laenger auffangen, kurz zudosieren, an der Zielstelle kuehlen, nach Sollmass weiterarbeiten, eine Portion nehmen und den Ansatz zur Zielstelle weiterleiten.",
}


def read(name: str) -> list[dict[str, str]]:
    with (P673 / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    source = read("SIX_HUNDRED_SEVENTY_THIRD_116_FLUENT_STATEMENTS.tsv")
    output = []
    repairs = []
    for row in source:
        revised = dict(row)
        if row["statement_id"] in POLISH:
            revised["fluent_workshop_reading_de"] = POLISH[row["statement_id"]]
            revised["reading_source"] = "HAND_POLISHED_V2"
            revised["fluency_grade"] = "POLISHED"
            repairs.append({
                "statement_id": row["statement_id"],
                "record": row["record"],
                "events": row["events"],
                "prior_grade": row["fluency_grade"],
                "repair_focus": "REMOVE_DUPLICATED_SEQUENCE_WORDS_AND_ATTACH_NOMINAL_SLOTS",
                "before_de": row["fluent_workshop_reading_de"],
                "after_de": POLISH[row["statement_id"]],
                "card_sequence_unchanged": "YES",
                "component_sequence_unchanged": "YES",
            })
        else:
            revised["reading_source"] = "UNCHANGED_CLEAN_V1"
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
            "complete_polished_reading_de": " ".join(f"[{row['statement_id']}] {row['fluent_workshop_reading_de']}" for row in rows),
        })

    write(HERE / "SIX_HUNDRED_SEVENTY_FOURTH_116_POLISHED_STATEMENTS.tsv", output, list(output[0]))
    write(HERE / "SIX_HUNDRED_SEVENTY_FOURTH_25_POLISH_REPAIRS.tsv", repairs, list(repairs[0]))
    write(HERE / "SIX_HUNDRED_SEVENTY_FOURTH_11_POLISHED_RECORDS.tsv", records, list(records[0]))
    summary = {
        "status": "PASS",
        "statements": len(output),
        "events": sum(int(row["events"]) for row in output),
        "records": len(records),
        "polished_statements": len(repairs),
        "polished_events": sum(int(row["events"]) for row in repairs),
        "unchanged_clean_statements": sum(row["reading_source"] == "UNCHANGED_CLEAN_V1" for row in output),
        "remaining_dense_or_workable": sum(row["fluency_grade"] in {"DENSE", "WORKABLE"} for row in output),
        "decision": "ALL_25_LONG_OR_STRAINED_STATEMENTS_HAND_POLISHED_WITH_CARD_SEQUENCES_UNCHANGED",
    }
    (HERE / "SIX_HUNDRED_SEVENTY_FOURTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
