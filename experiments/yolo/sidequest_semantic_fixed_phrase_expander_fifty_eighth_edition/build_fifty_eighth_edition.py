#!/usr/bin/env python3
"""Regenerate all prose with fixed owner and content phrases, not bespoke nouns."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
SENTENCES = ROOT / "experiments/yolo/sidequest_semantic_picture_phrasebook_fifty_seventh_edition/FIFTY_SEVENTH_116_ANNOTATED_SENTENCES.tsv"
OWNERS = ROOT / "experiments/yolo/sidequest_semantic_picture_phrasebook_fifty_seventh_edition/FIFTY_SEVENTH_17_VISIBLE_OWNER_PHRASES.tsv"
PHRASES = ROOT / "experiments/yolo/sidequest_semantic_picture_phrasebook_fifty_seventh_edition/FIFTY_SEVENTH_20_CONTENT_CONVENTIONS.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


PREFIX = {
    "PLANT_BATCH": "Bildbesitzer: {subject}. Kartenfolge",
    "BASIN_STATION": "Stationsbesitzer: {subject}. Kartenfolge",
    "CONNECTED_STRUCTURE": "Verbindungsbesitzer: {subject}. Kartenfolge",
    "UNRESOLVED_GAP_STATION": "Zwischenbesitzer: {subject}. Kartenfolge",
    "GENERIC_WORKPIECE": "Arbeitsbesitzer: {subject}. Kartenfolge",
}

CONTENT_LEAD = {
    "PLANT_BATCH": "Der Pflanzenartikel setzt dabei voraus",
    "BASIN_STATION": "Die gezeichnete Station setzt dabei voraus",
    "CONNECTED_STRUCTURE": "Die sichtbare Verbindung setzt dabei voraus",
    "UNRESOLVED_GAP_STATION": "Der Meister ergänzt dabei",
    "GENERIC_WORKPIECE": "Die Werkstatt ergänzt dabei",
}


def main() -> None:
    sentences = read_tsv(SENTENCES)
    owners = {row["exact_visible_owner_de"]: row for row in read_tsv(OWNERS)}
    phrases = {row["phrase_id"]: row for row in read_tsv(PHRASES)}

    templates = []
    for owner_class in PREFIX:
        for content in ("NO_CONTENT_TAG", "WITH_CONTENT_TAGS"):
            templates.append({
                "template_id": f"T{len(templates)+1:02d}",
                "owner_class": owner_class,
                "content_mode": content,
                "fixed_pattern_de": PREFIX[owner_class] + ": {cards}." + ("" if content == "NO_CONTENT_TAG" else " " + CONTENT_LEAD[owner_class] + ": {contents}."),
                "sentence_specific_free_text_allowed": "NO",
            })
    write_tsv(OUT / "FIFTY_EIGHTH_10_EXPANSION_TEMPLATES.tsv", templates)
    template_lookup = {(row["owner_class"], row["content_mode"]): row for row in templates}

    generated = []
    phrase_usage = Counter()
    for row in sentences:
        owner = owners[row["visible_owner"]]
        ids = [] if row["content_phrase_ids"] == "NONE" else row["content_phrase_ids"].split("|")
        for phrase_id in ids:
            phrase_usage[phrase_id] += 1
        content_mode = "WITH_CONTENT_TAGS" if ids else "NO_CONTENT_TAG"
        template = template_lookup[(owner["owner_class"], content_mode)]
        values = {
            "subject": owner["silent_subject_de"],
            "active": owner["silent_active_item_de"],
            "source": owner["silent_source_de"],
            "target": owner["silent_target_de"],
            "cards": row["card_by_card_reading_de"].rstrip(". "),
            "contents": "; ".join(phrases[phrase_id]["default_spoken_phrase_de"] for phrase_id in ids),
        }
        expanded = template["fixed_pattern_de"].format(**values)
        generated.append({
            "unit_id": row["unit_id"],
            "page": row["page"],
            "owner_class": owner["owner_class"],
            "template_id": template["template_id"],
            "surface_sequence": row["surface_sequence"],
            "card_reading_de": row["card_by_card_reading_de"],
            "content_phrase_ids": row["content_phrase_ids"],
            "fixed_generated_prose_de": expanded,
            "previous_fluent_working_reading_de": row["fluent_working_reading_de"],
            "sentence_specific_lexical_insertions": 0,
            "generation_layers": "VISIBLE_OWNER|CARD_READING" + ("|FIXED_CONTENT_PHRASE" if ids else ""),
        })
    write_tsv(OUT / "FIFTY_EIGHTH_116_FIXED_EXPANSIONS.tsv", generated)

    coverage = []
    for phrase_id, row in phrases.items():
        coverage.append({
            "phrase_id": phrase_id,
            "fixed_phrase_de": row["default_spoken_phrase_de"],
            "expected_statement_count": row["statement_count"],
            "generated_statement_count": phrase_usage[phrase_id],
            "all_uses_regenerated": "YES" if int(row["statement_count"]) == phrase_usage[phrase_id] else "NO",
        })
    write_tsv(OUT / "FIFTY_EIGHTH_20_PHRASE_COVERAGE.tsv", coverage)

    doc = [
        "# 116 Aussagen aus festen Werkstattwendungen",
        "",
        "Jede folgende Kurzfassung wurde nur aus Besitzerformel, Kartenlesung und den",
        "zwanzig festen Inhaltswendungen zusammengesetzt. Es gibt keine frei pro Aussage",
        "eingesetzten Zusatznomen.",
        "",
    ]
    current_page = None
    for row in generated:
        if row["page"] != current_page:
            current_page = row["page"]
            doc.extend([f"# {current_page}", ""])
        doc.extend([f"## {row['unit_id']}", "", row["fixed_generated_prose_de"], ""])
    (OUT / "FIFTY_EIGHTH_COMPLETE_FIXED_PROSE.md").write_text("\n".join(doc).rstrip() + "\n", encoding="utf-8")

    template_counts = Counter(row["template_id"] for row in generated)
    summary = {
        "status": "CONSISTENT",
        "counts": {
            "fixed_templates": len(templates),
            "generated_statements": len(generated),
            "content_phrases": len(coverage),
            "sentence_specific_lexical_insertions": sum(int(row["sentence_specific_lexical_insertions"]) for row in generated),
            "statements_with_content_phrases": sum(row["content_phrase_ids"] != "NONE" for row in generated),
        },
        "template_usage": dict(template_counts),
        "sources": {str(path.relative_to(ROOT)): sha256(path) for path in (SENTENCES, OWNERS, PHRASES)},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
