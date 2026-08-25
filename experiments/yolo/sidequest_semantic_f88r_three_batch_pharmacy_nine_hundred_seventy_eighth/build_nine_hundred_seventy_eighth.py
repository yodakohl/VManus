#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P972 = ROOT / "experiments/yolo/sidequest_semantic_visual_material_owner_revision_nine_hundred_seventy_second"
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


BATCHES = {
    "UPPER_SIX": {
        "label_loci": {f"f88r.{n}" for n in range(1, 7)},
        "prose_loci": {f"f88r.{n}" for n in range(7, 12)},
        "clauses": ["P915-C350"],
        "visible_station_de": "oberes Gefäß mit sechs Wurzel-/Blattposten",
        "working_recipe_de": (
            "Die sechs oberen Drogenposten auswählen. Vom bezeichneten Vorrat einen Teil nach Sollmaß "
            "in das obere Gefäß geben, kurz vorbereiten, weitere Anteile zugeben, den Ansatz im Gefäß "
            "führen und den Auszug in die nächste Aufnahme leiten."
        ),
    },
    "MIDDLE_SIX": {
        "label_loci": {f"f88r.{n}" for n in range(12, 18)},
        "prose_loci": {f"f88r.{n}" for n in range(18, 23)},
        "clauses": ["P915-C351", "P915-C352"],
        "visible_station_de": "mittleres Gefäß mit sechs neuen Drogenposten",
        "working_recipe_de": (
            "Mit den sechs mittleren Drogenposten einen zweiten Ansatz beginnen. Die Sollmenge zugeben, "
            "mehrfach weiterführen und durch den Auszugsweg leiten; länger halten, einen weiteren Teil "
            "nachsetzen und den Teilgang schließen."
        ),
    },
    "LOWER_FOUR": {
        "label_loci": {"f88r.23", "f88r.24", "f88r.25"},
        "prose_loci": {f"f88r.{n}" for n in range(26, 32)},
        "clauses": ["P915-C353", "P915-C354"],
        "visible_station_de": "unteres Gefäß mit vier Drogenposten",
        "working_recipe_de": (
            "Die vier unteren Drogenposten auswählen, vom Vorrat nehmen und länger ansetzen. Den Ansatz "
            "nach Sollmaß fortführen, den Auszug leiten, einen weiteren Teil zugeben und die letzte "
            "Gefäßcharge schließen."
        ),
    },
}


def batch_for_locus(locus: str) -> tuple[str, str]:
    for batch_id, data in BATCHES.items():
        if locus in data["label_loci"]:
            return batch_id, "LEARNED_DRUG_LABEL"
        if locus in data["prose_loci"]:
            return batch_id, "PRODUCTIVE_RECIPE_PROSE"
    raise KeyError(locus)


def main() -> None:
    hybrid = [r for r in read(P975 / "PASS975_2511_EVENT_HYBRID_EDITION.tsv") if r["physical_page"] == "f88r"]
    labels = {r["event_id"]: r for r in read(P972 / "PASS972_F88R_SIXTEEN_LABEL_OWNER_MAP.tsv")}
    clauses = {r["clause_id"]: r for r in read(P977 / "PASS977_354_COMPLETE_HYBRID_CLAUSES.tsv") if r["physical_page"] == "f88r"}
    event_to_clause = {}
    for clause in clauses.values():
        for event_id in clause["event_ids"].split("|"):
            event_to_clause[event_id] = clause["clause_id"]

    rows = []
    for event in hybrid:
        batch_id, role = batch_for_locus(event["locus"])
        label = labels.get(event["event_id"])
        rows.append({
            "event_id": event["event_id"],
            "batch_id": batch_id,
            "role": role,
            "locus": event["locus"],
            "surface": event["surface"],
            "component_recipe": event["component_recipe"],
            "visual_object_id": label["visual_object_id"] if label else "NONE",
            "visible_object_de": label["visible_object_de"] if label else BATCHES[batch_id]["visible_station_de"],
            "clause_id": event_to_clause.get(event["event_id"], "NONE__LABEL"),
            "short_working_reading_de": label["local_reading_de"] if label else event["hybrid_working_reading_de"],
        })
    write(HERE / "PASS978_F88R_150_EVENT_THREE_BATCH_EDITION.tsv", rows, list(rows[0]))

    batch_rows = []
    for batch_id, data in BATCHES.items():
        batch_events = [r for r in rows if r["batch_id"] == batch_id]
        label_events = [r for r in batch_events if r["role"] == "LEARNED_DRUG_LABEL"]
        prose_events = [r for r in batch_events if r["role"] == "PRODUCTIVE_RECIPE_PROSE"]
        batch_rows.append({
            "batch_id": batch_id,
            "visible_station_de": data["visible_station_de"],
            "label_events": str(len(label_events)),
            "prose_events": str(len(prose_events)),
            "label_surfaces": " ".join(r["surface"] for r in label_events),
            "clause_ids": "|".join(data["clauses"]),
            "working_recipe_de": data["working_recipe_de"],
        })
    write(HERE / "PASS978_THREE_BATCH_RECIPES.tsv", batch_rows, list(batch_rows[0]))

    lines = [
        "# Pass 978 — f88r als dreifacher Drogen- und Gefäßkasten",
        "",
        "Die Seite ist jetzt am einfachsten als drei wiederholte Arbeitsfächer lesbar:",
        "sichtbare Drogenetiketten, dann der zugehörige Gefäßtext. Die sechzehn",
        "Etiketten bleiben gelernte Namen/Klassencodes; der Lauftext benutzt die",
        "gemeinsame Werkstattgrammatik.",
        "",
    ]
    for row in batch_rows:
        lines += [
            f"## {row['batch_id']} — {row['visible_station_de']}",
            "",
            f"Etiketten: `{row['label_surfaces']}`",
            "",
            f"> {row['working_recipe_de']}",
            "",
        ]
        for clause_id in row["clause_ids"].split("|"):
            clause = clauses[clause_id]
            lines.append(f"- **{clause_id}** (`{clause['surface_sequence']}`): {clause['continuous_working_translation_de']}")
        lines.append("")
    lines += [
        "## Wichtigster Gewinn",
        "",
        "f88r zeigt das Mischsystem direkt: Ein neues Drogenetikett muss nicht aus",
        "Wurzeln übersetzt werden. Es wählt den sichtbaren Stoff. Die folgenden",
        "Karten können trotzdem produktiv Menge, Ansatz, Halten, Leiten und Schluss",
        "notieren. Das erklärt, wie ein kleiner gemeinsamer Code und viele gelernte",
        "Fachwörter im selben Werk funktionieren.",
        "",
    ]
    (HERE / "PASS978_F88R_THREE_BATCH_REPORT.md").write_text("\n".join(lines), encoding="utf-8")
    summary = {
        "status": "PASS",
        "events": len(rows),
        "labels": sum(r["role"] == "LEARNED_DRUG_LABEL" for r in rows),
        "prose": sum(r["role"] == "PRODUCTIVE_RECIPE_PROSE" for r in rows),
        "batches": len(batch_rows),
        "clauses": len(clauses),
    }
    (HERE / "PASS978_BUILD_SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
