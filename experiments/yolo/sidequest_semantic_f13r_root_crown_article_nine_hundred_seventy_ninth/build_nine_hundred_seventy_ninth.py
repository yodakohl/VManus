#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P975 = ROOT / "experiments/yolo/sidequest_semantic_specialist_whole_card_drawer_nine_hundred_seventy_fifth"
P977 = ROOT / "experiments/yolo/sidequest_semantic_complete_hybrid_clause_edition_nine_hundred_seventy_seventh"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


LOCAL_HEADWORDS = {
    "torshor": ("WURZELKRONE", "Artikelkopf: die große sichtbare Speicherwurzel/Krone aktivieren."),
    "dchg": ("BRUTKNÖLLCHEN", "Einen der kleinen sichtbaren Rundkörper am Wurzelhals abnehmen."),
    "tshy": ("BLÜTENANTEIL", "Den Anteil aus dem endständigen Blütenstand wählen."),
    "shochy": ("BLATTANTEIL", "Einen Anteil aus der breiten Blattkrone nehmen."),
    "cfholdy": ("AUSPRESSEN", "Den ersten Ansatz weiter auspressen und den Teilgang schließen."),
}


CLAUSE_READINGS = {
    "P915-C005": (
        "Die Wurzelkrone aktivieren. Einen ersten Teil und ein Brutknöllchen abnehmen, im Ansatz "
        "weiterhalten, die bezeichneten Teilmengen nach Sollmaß zugeben und den Blütenanteil "
        "mitführen; anschließend weiter auspressen und den ersten Teilgang schließen."
    ),
    "P915-C006": (
        "Vom restlichen Wurzelansatz eine Sollmenge nehmen, den nächsten Ansatz setzen, durch den "
        "Durchlass führen, an der Teilstelle fortsetzen und schließen."
    ),
    "P915-C007": (
        "Einen Blattanteil nach Sollmaß in den nächsten Ansatz geben, kurz bearbeiten, prüfen und "
        "den zweiten Teilgang schließen."
    ),
    "P915-C008": (
        "Den angesetzten Posten kurz halten, auf der nächsten Arbeitsstufe fortführen, zur "
        "bezeichneten Stelle geben und dort schließen."
    ),
    "P915-C009": (
        "Danach den nächsten Pflanzenteil auswählen, zugeben und mit dem vorhandenen Ansatz "
        "vereinigen; die Fortsetzung bleibt offen."
    ),
}


def main() -> None:
    source = [r for r in read(P975 / "PASS975_2511_EVENT_HYBRID_EDITION.tsv") if r["physical_page"] == "f13r"]
    clauses = [r for r in read(P977 / "PASS977_354_COMPLETE_HYBRID_CLAUSES.tsv") if r["physical_page"] == "f13r"]
    event_to_clause = {
        event_id: clause["clause_id"]
        for clause in clauses
        for event_id in clause["event_ids"].split("|")
    }
    rows = []
    for event in source:
        headword, expansion = LOCAL_HEADWORDS.get(event["surface"], ("NONE", event["hybrid_working_reading_de"]))
        rows.append({
            "event_id": event["event_id"],
            "clause_id": event_to_clause[event["event_id"]],
            "locus": event["locus"],
            "surface": event["surface"],
            "component_recipe": event["component_recipe"],
            "shared_card_reading_de": event["hybrid_working_reading_de"],
            "local_visual_headword_de": headword,
            "image_owned_expansion_de": expansion,
        })
    write(HERE / "PASS979_F13R_77_EVENT_ROOT_CROWN_EDITION.tsv", rows, list(rows[0]))

    clause_rows = []
    for clause in clauses:
        clause_events = [r for r in rows if r["clause_id"] == clause["clause_id"]]
        clause_rows.append({
            "clause_id": clause["clause_id"],
            "locus_span": clause["locus_span"],
            "event_count": clause["event_count"],
            "surface_sequence": clause["surface_sequence"],
            "local_headwords": " | ".join(
                f"{r['surface']}={r['local_visual_headword_de']}"
                for r in clause_events if r["local_visual_headword_de"] != "NONE"
            ),
            "complete_working_translation_de": CLAUSE_READINGS[clause["clause_id"]],
            "end_reason": clause["end_reason"],
        })
    write(HERE / "PASS979_FIVE_STAGE_ROOT_CROWN_ARTICLE.tsv", clause_rows, list(clause_rows[0]))

    lines = [
        "# Pass 979 — f13r als fünfteiliger Wurzelkronen-Artikel",
        "",
        "Das Bild liefert vier lokale Materialwörter: WURZELKRONE, BRUTKNÖLLCHEN,",
        "BLATTANTEIL und BLÜTENANTEIL. Der Text liefert die gemeinsame Grammatik",
        "für Teil, Maß, Ansatz, Zugabe, Durchlass, Auspressen und Schluss.",
        "",
    ]
    for row in clause_rows:
        lines += [
            f"## {row['clause_id']} — {row['locus_span']}",
            "",
            f"`{row['surface_sequence']}`",
            "",
            f"> {row['complete_working_translation_de']}",
            "",
        ]
    lines += [
        "## Arbeitstheorie",
        "",
        "Die ersten fünf Zeilen bilden die große Wurzelcharge; die folgenden Gänge",
        "verarbeiten Restwurzel, Blattanteil und einen weiteren offenen Pflanzenteil.",
        "Das ist als Werkstattartikel lernbar: Bildteile sind lokale Ganzwörter, der",
        "Ablauf wird mit dem gemeinsamen Kartenapparat geschrieben.",
        "",
    ]
    (HERE / "PASS979_F13R_ROOT_CROWN_REPORT.md").write_text("\n".join(lines), encoding="utf-8")
    summary = {
        "status": "PASS",
        "events": len(rows),
        "clauses": len(clause_rows),
        "local_headwords": len(LOCAL_HEADWORDS),
        "local_headword_events": sum(r["local_visual_headword_de"] != "NONE" for r in rows),
    }
    (HERE / "PASS979_BUILD_SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
