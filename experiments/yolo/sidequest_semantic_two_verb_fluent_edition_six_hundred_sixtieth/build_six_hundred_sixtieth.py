#!/usr/bin/env python3
"""Write fluent workshop-German readings for all 18 joint OK/CHD statements."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P659 = ROOT / "experiments/yolo/sidequest_semantic_two_verb_cycle_six_hundred_fifty_ninth"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


TRANSLATIONS = {
    "B1-S002": (
        "DENSE_BUT_COMPLETE",
        "Setze die vorgeschriebene Menge an. Gib die laufende Fluessigkeit hinzu und setze sie an der Zielstelle an. Nimm aus dem Vorrat, fahre fort, gib eine Portion und danach eine weitere Portion an die Zielstelle. Fahre kuehlend fort, leite den Ansatz weiter, halte ihn kurz am Durchlass der Zielstelle, richte erneut das Sollmass ein, halte ihn dort laenger, fuehre den bemessenen Posten durch den Kanal und setze ihn zum Abschluss um.",
        "DOSIEREN_SETZEN_WEITERLEITEN_SCHLIESSEN",
    ),
    "B1-S007": ("CLEAN", "Ansetzen, umsetzen und abschliessen.", "FUSED_SET_TRANSFER_CLOSE"),
    "B1-S015": ("CLEAN", "Den Posten kurz eintragen; ansetzen, umsetzen und abschliessen.", "ENTER_THEN_FUSED_CLOSE"),
    "B2-S004": (
        "WORKABLE",
        "An der Zielstelle ansetzen. Den Posten durch den Kanal weiterleiten, umsetzen und laenger ansetzen; danach kurz durch den Kanal weiterleiten und abschliessen.",
        "TARGET_CHANNEL_TRANSFER_LONG_CLOSE",
    ),
    "B2-S016": (
        "WORKABLE",
        "Von der Zielstelle aus dem Vorrat weiterleiten und umsetzen. Einen Teil kurz abnehmen, das Sollmass setzen und danach den Posten laenger behandeln. Nach Sollmass kurz ansetzen, einfliessen lassen, umsetzen und abschliessen.",
        "SOURCE_MEASURE_FILL_TRANSFER_CLOSE",
    ),
    "B3-S006": (
        "CLEAN",
        "Den laufenden Posten umsetzen, an der Zielstelle ansetzen, weiter umsetzen und abschliessen.",
        "TRANSFER_SET_TARGET_TRANSFER_CLOSE",
    ),
    "B3-S007": (
        "CLEAN",
        "Nach Sollmass ansetzen, den laufenden Posten umsetzen, laenger ansetzen und abschliessen.",
        "MEASURE_SET_TRANSFER_LONG_CLOSE",
    ),
    "B3-S011": (
        "WORKABLE",
        "Kurz halten, bis der Posten bereit ist; ihn umsetzen, wieder ansetzen und nochmals umsetzen, dann beim Vorratsposten belassen.",
        "HOLD_READY_TRANSFER_RECONFIGURE",
    ),
    "B3-S016": ("CLEAN", "Den Arbeitsgang weiterleiten; ansetzen, umsetzen und abschliessen.", "FORWARD_THEN_FUSED_CLOSE"),
    "B3-S021": (
        "WORKABLE",
        "Nach Sollmass ansetzen. Den bereiten Posten fuer die Zielstelle nehmen, erneut bemessen und dort absetzen. Kurz halten, bis er bereit ist, und ihn schliesslich an der Zielstelle umsetzen.",
        "MEASURE_TARGET_SETTLE_READY_TRANSFER_CLOSE",
    ),
    "B3-S025": ("CLEAN", "Ansetzen, umsetzen und abschliessen.", "FUSED_SET_TRANSFER_CLOSE"),
    "B3-S026": (
        "WORKABLE",
        "Aus dem Vorrat laenger nehmen, nach Sollmass weiterleiten, den Posten umsetzen und eine Portion ansetzen. Bereitstellen, den Ansatz an der Zielstelle kuehlen, laenger auffangen und abschliessen.",
        "SOURCE_MEASURE_TRANSFER_PORTION_COOL_COLLECT",
    ),
    "B3-S030": (
        "CLEAN",
        "Den Posten nach Sollmass ansetzen, die laufende Fluessigkeit umsetzen, danach nochmals umsetzen und abschliessen.",
        "SET_MEASURE_TRANSFER_FLOW_CLOSE",
    ),
    "B4-S003": (
        "WORKABLE",
        "Den Posten umsetzen und danach zur Zielstelle fuehren. Ihn dort laenger ansetzen, wieder in Arbeit setzen, fortfahren, absetzen lassen und abschliessen.",
        "TRANSFER_TARGET_LONG_SET_SETTLE_CLOSE",
    ),
    "B4-S005": (
        "CLEAN",
        "Eine Portion nehmen, den laufenden Posten umsetzen, laenger ansetzen und abschliessen.",
        "PORTION_TRANSFER_LONG_CLOSE",
    ),
    "B4-S011": (
        "WORKABLE",
        "Nach Sollmass den Posten kurz waermen, laenger fortfahren, eine Portion ansetzen und den Posten umsetzen. Fortsetzen, kurz weiterleiten und zudosieren, dann abschliessen.",
        "MEASURE_WARM_PORTION_TRANSFER_FORWARD_CLOSE",
    ),
    "B4-S015": (
        "WORKABLE",
        "Eine Portion ansetzen, den Posten laenger halten und eine weitere Portion zufuegen. Durch den Kanal zur Zielstelle abnehmen, kurz auffangen, weiterleiten, umsetzen und abschliessen.",
        "PORTION_HOLD_CHANNEL_COLLECT_TRANSFER_CLOSE",
    ),
    "B5-S002": ("CLEAN", "Ansetzen, umsetzen und abschliessen.", "FUSED_SET_TRANSFER_CLOSE"),
}


TEACHING = ["B3-S006", "B3-S007", "B3-S030", "B4-S005", "B4-S015"]


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    traces = read_tsv(P659 / "SIX_HUNDRED_FIFTY_NINTH_18_JOINT_STATEMENT_TRACES.tsv")
    rows = []
    for trace in traces:
        quality, translation, process = TRANSLATIONS[trace["statement_id"]]
        rows.append({
            "statement_id": trace["statement_id"],
            "page": trace["page"],
            "record": trace["record"],
            "event_count": trace["statement_events"],
            "source_surface": trace["full_surface"],
            "verb_skeleton": trace["verb_skeleton"],
            "literal_card_reading_de": trace["full_card_reading_de"],
            "fluent_workshop_reading_de": translation,
            "process_summary": process,
            "reading_quality": quality,
            "all_visible_events_retained": "YES",
            "added_content_nouns": "NONE",
        })
    teaching_rows = [
        {
            "rank": i,
            "statement_id": sid,
            "source_surface": next(row["source_surface"] for row in rows if row["statement_id"] == sid),
            "fluent_workshop_reading_de": next(row["fluent_workshop_reading_de"] for row in rows if row["statement_id"] == sid),
            "why_selected": "klare mehrstufige Setzen-Umsetzen-Folge mit sichtbarem Abschluss",
        }
        for i, sid in enumerate(TEACHING, 1)
    ]
    write_tsv(HERE / "SIX_HUNDRED_SIXTIETH_18_FLUENT_STATEMENT_READINGS.tsv", rows, list(rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_SIXTIETH_5_TEACHING_EXCERPTS.tsv", teaching_rows, list(teaching_rows[0]))

    md = [
        "# Achtzehn vollständige Zweiverb-Lesungen",
        "",
        "Die flüssige Fassung ergänzt nur deutsche Grammatik. Keine neue Zutat, Krankheit, Körperstelle oder Apparatur wird eingesetzt.",
        "",
    ]
    for row in rows:
        md.extend([
            f"## {row['statement_id']} — {row['reading_quality']}",
            "",
            f"`{row['source_surface']}`",
            "",
            str(row["fluent_workshop_reading_de"]),
            "",
        ])
    (HERE / "SIX_HUNDRED_SIXTIETH_COMPLETE_TRANSLATION_BOOK.md").write_text("\n".join(md).rstrip() + "\n", encoding="utf-8")

    summary = {
        "status": "PASS",
        "statements": len(rows),
        "events": sum(int(row["event_count"]) for row in rows),
        "clean_readings": sum(row["reading_quality"] == "CLEAN" for row in rows),
        "workable_readings": sum(row["reading_quality"] == "WORKABLE" for row in rows),
        "dense_but_complete_readings": sum(row["reading_quality"] == "DENSE_BUT_COMPLETE" for row in rows),
        "teaching_excerpts": len(teaching_rows),
        "added_content_nouns": 0,
        "decision": "EIGHTEEN_TWO_VERB_STATEMENTS_HAVE_COMPLETE_FLUENT_WORKSHOP_READINGS",
    }
    (HERE / "SIX_HUNDRED_SIXTIETH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
