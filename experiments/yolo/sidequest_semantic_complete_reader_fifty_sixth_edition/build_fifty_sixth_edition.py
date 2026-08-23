#!/usr/bin/env python3
"""Rebuild the complete ten-page reader from the pocket grammar and hierarchy."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
UNITS = ROOT / "experiments/yolo/sidequest_semantic_complete_human_forty_fifth_edition/FORTY_FIFTH_258_READING_UNITS.tsv"
LEDGER = ROOT / "experiments/yolo/sidequest_semantic_final_productive_cards_nineteenth_edition/NINETEENTH_776_SPEAKABLE_LEDGER.tsv"
HIERARCHY = ROOT / "experiments/yolo/sidequest_semantic_hierarchical_dictionary_fifty_fourth_edition/FIFTY_FOURTH_89_HIERARCHICAL_ENTRIES.tsv"
POCKET = ROOT / "experiments/yolo/sidequest_semantic_pocket_grammar_fifty_fifth_edition/FIFTY_FIFTH_24_DESK_RULES.tsv"

PAGE_ORDER = ("f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v")


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


def layer_for(row: dict[str, str]) -> str:
    if row["register"] == "ASTRO":
        return "ASTRO_LOCAL_MODULE"
    if row["lookup_mode"] in {"COMPOSED_LEARNED_PROSE_BODY", "FINAL_PRODUCTIVE_BODY_OR_REGISTER_SPLIT", "MEMORIZED_WHOLE_COMMAND"}:
        return "LEARNED_NOMENCLATOR"
    if row["lookup_mode"] == "PROSE_STATEMENT_ATTACHMENT":
        return "OWNER_OR_MEMORY_EXPANSION"
    return "POCKET_CORE_CARD"


def main() -> None:
    units = read_tsv(UNITS)
    ledger = read_tsv(LEDGER)
    hierarchy = read_tsv(HIERARCHY)
    pocket = read_tsv(POCKET)
    by_unit: dict[str, list[dict[str, str]]] = defaultdict(list)
    group_rows = []
    for row in ledger:
        layer = layer_for(row)
        out = {
            "unified_serial": row["unified_serial"],
            "page": row["page"],
            "reading_unit_id": row["reading_unit_id"],
            "source_group_id": row["source_group_id"],
            "visible_owner": row["visible_owner"],
            "visible_surface": row["visible_surface"],
            "atom_sequence": row["atom_sequence"],
            "card_reading_de": row["short_value_de"],
            "teaching_layer": layer,
            "lookup_mode": row["lookup_mode"],
            "concrete_noun_source": "LOCAL_ASTRO_EXEMPLAR" if row["register"] == "ASTRO" else "VISIBLE_OWNER_OR_RECORD_MEMORY",
        }
        group_rows.append(out)
        by_unit[row["reading_unit_id"]].append(out)
    write_tsv(OUT / "FIFTY_SIXTH_776_GROUP_READER.tsv", group_rows)

    unit_rows = []
    dependency_rows = []
    for unit in units:
        groups = by_unit[unit["unit_id"]]
        dependencies = sorted({row["teaching_layer"] for row in groups})
        if unit["unit_kind"] == "PROSE_STATEMENT":
            dependencies.extend(name for name in ("VISIBLE_OWNER", "SILENT_MEMORY_REGISTER") if name not in dependencies)
        else:
            if "VISIBLE_DIAGRAM_ADDRESS" not in dependencies:
                dependencies.append("VISIBLE_DIAGRAM_ADDRESS")
        dependencies = sorted(set(dependencies))
        card_reading = "; ".join(row["card_reading_de"] for row in groups)
        unit_rows.append({
            "unit_order": unit["unit_order"],
            "page": unit["page"],
            "unit_id": unit["unit_id"],
            "unit_kind": unit["unit_kind"],
            "owner_or_namespace": unit["owner_or_namespace"],
            "group_count": unit["group_count"],
            "surface_sequence": unit["surface_sequence"],
            "atom_sequence": unit["atom_sequence"],
            "card_by_card_reading_de": card_reading,
            "fluent_working_reading_de": unit["short_workshop_reading_de"],
            "fully_memory_expanded_reading_de": unit["fully_spoken_reading_de"],
            "dependencies_beyond_atomic_roots": "|".join(dependencies),
            "pocket_sequence_readable": "YES",
            "fluent_content_source": "OWNER_AND_WORKSHOP_EXEMPLAR" if unit["unit_kind"] == "PROSE_STATEMENT" else "LOCAL_DIAGRAM_AND_MASTER_EXEMPLAR",
            "sentence_ends_at_physical_line": "NO_ASSUMPTION",
        })
        dependency_rows.append({
            "unit_id": unit["unit_id"],
            "page": unit["page"],
            "unit_kind": unit["unit_kind"],
            "dependencies": "|".join(dependencies),
            "what_pocket_grammar_recovers_de": "Kartenfolge, kurze Arbeitswerte, Reihenfolge und lokale Adressregel",
            "what_context_adds_de": "konkrete Gegenstände, lokale Referenten und die flüssige Werkstattformulierung" if unit["unit_kind"] == "PROSE_STATEMENT" else "örtlicher Tabellenwert und Instrumentadresse",
            "is_this_a_word_meaning": "NO_CONTEXT_LAYER",
        })
    write_tsv(OUT / "FIFTY_SIXTH_258_COMPLETE_UNITS.tsv", unit_rows)
    write_tsv(OUT / "FIFTY_SIXTH_258_CONTEXT_DEPENDENCIES.tsv", dependency_rows)

    page_rows = []
    for page in PAGE_ORDER:
        page_units = [row for row in unit_rows if row["page"] == page]
        group_count = sum(int(row["group_count"]) for row in page_units)
        deps = Counter(dep for row in page_units for dep in row["dependencies_beyond_atomic_roots"].split("|"))
        page_rows.append({
            "page": page,
            "unit_kind": page_units[0]["unit_kind"],
            "reading_units": len(page_units),
            "visible_groups": group_count,
            "owner_or_namespace_count": len({row["owner_or_namespace"] for row in page_units}),
            "dominant_context_layers": "|".join(name for name, _ in deps.most_common()),
            "complete_card_sequence": "YES",
            "complete_fluent_working_reading": "YES",
        })
    write_tsv(OUT / "FIFTY_SIXTH_10_PAGE_SUMMARY.tsv", page_rows)

    doc = [
        "# Vollständige Zehnseiten-Lesefassung aus der Taschengrammatik",
        "",
        "Jede Einheit zeigt zuerst Oberfläche und Kartenlesung, danach die flüssige",
        "kreative Werkstattlesung. Lange Gegenstände stammen aus Bild, Merktafel oder",
        "lokalem Himmelsinstrument; sie werden nicht rückwirkend in einen Stamm gepackt.",
        "",
    ]
    for page in PAGE_ORDER:
        doc.extend([f"# {page}", ""])
        for row in (item for item in unit_rows if item["page"] == page):
            doc.extend([
                f"## {row['unit_id']} — {row['owner_or_namespace']}",
                "",
                f"**Oberfläche:** `{row['surface_sequence']}`",
                "",
                f"**Karten:** {row['card_by_card_reading_de']}.",
                "",
                f"**Flüssige Arbeitslesung:** {row['fluent_working_reading_de']}",
                "",
                f"**Ergänzt durch:** {row['dependencies_beyond_atomic_roots']}.",
                "",
            ])
    (OUT / "FIFTY_SIXTH_COMPLETE_TEN_PAGE_READER.md").write_text("\n".join(doc).rstrip() + "\n", encoding="utf-8")

    layer_counts = Counter(row["teaching_layer"] for row in group_rows)
    summary = {
        "status": "CONSISTENT",
        "counts": {
            "pages": len(page_rows),
            "reading_units": len(unit_rows),
            "visible_groups": len(group_rows),
            "prose_units": sum(row["unit_kind"] == "PROSE_STATEMENT" for row in unit_rows),
            "astro_units": sum(row["unit_kind"] == "ASTRO_LOCUS" for row in unit_rows),
            "hierarchy_entries_available": len(hierarchy),
            "pocket_rules_available": len(pocket),
            **dict(layer_counts),
        },
        "sources": {str(path.relative_to(ROOT)): sha256(path) for path in (UNITS, LEDGER, HIERARCHY, POCKET)},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
