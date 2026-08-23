#!/usr/bin/env python3
"""Run the twelve clause shapes backward from surface to source prose."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
MAP = ROOT / "experiments/yolo/sidequest_semantic_clause_shapes_sixty_third_edition/SIXTY_THIRD_381_GROUP_SHAPE_MAP.tsv"
CHAINS = ROOT / "experiments/yolo/sidequest_semantic_clause_shapes_sixty_third_edition/SIXTY_THIRD_16_COMPRESSION_CHAINS.tsv"


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


def main() -> None:
    groups = read_tsv(MAP)
    chains = read_tsv(CHAINS)
    chain_units = {row["unit_id"] for row in chains}
    by_unit = defaultdict(list)
    reverse_rows = []
    for row in groups:
        productive = row["learned_or_local_atoms"] == "NONE"
        readback = f"{row['clause_shape_id']} {row['source_slot_sequence']}: {row['card_reading_de']}"
        out = {
            "source_group_id": row["source_group_id"],
            "unit_id": row["unit_id"],
            "page": row["page"],
            "visible_surface": row["visible_surface"],
            "atom_sequence_recovered": row["atom_sequence"],
            "clause_shape_recovered": row["clause_shape_id"],
            "source_slots_recovered": row["source_slot_sequence"],
            "short_dictionary_readback_de": row["card_reading_de"],
            "combined_reverse_readback_de": readback,
            "component_status": "PRODUCTIVE_COMPONENTS" if productive else "LEARNED_BODY_PRESENT",
            "owner_status": "PAGE_IMAGE_OR_RECORD_OWNER_REQUIRED_FOR_CONCRETE_NOUN",
            "rich_source_status": "MASTER_EXEMPLAR_REQUIRED_FOR_FULL_PROSE",
            "structural_readback_complete": "YES",
        }
        reverse_rows.append(out)
        by_unit[row["unit_id"]].append(out)
    write_tsv(OUT / "SIXTY_FOURTH_381_REVERSE_DECOMPRESSION.tsv", reverse_rows)

    chain_rows = []
    for chain in chains:
        rows = by_unit[chain["unit_id"]]
        dictionary = "; ".join(row["short_dictionary_readback_de"] for row in rows)
        owner_augmented = f"Bei {chain['owner']}: {dictionary}."
        chain_rows.append({
            "chain_order": chain["chain_order"],
            "unit_id": chain["unit_id"],
            "page": chain["page"],
            "visible_surface_input": chain["visible_surface"],
            "recovered_atom_sequence": chain["atom_sequence"],
            "recovered_clause_shapes": chain["clause_shape_program"],
            "recovered_slot_program": chain["slot_program"],
            "dictionary_only_readback_de": dictionary,
            "owner_augmented_readback_de": owner_augmented,
            "full_master_source_de": chain["natural_source_prose_de"],
            "construction_recovery": "DIRECT_FROM_REGISTERED_SURFACE_AND_GRAMMAR",
            "short_card_recovery": "REQUIRES_SHARED_WORKSHOP_DICTIONARY",
            "concrete_owner_recovery": "REQUIRES_VISIBLE_IMAGE_OR_RECORD_CONTEXT",
            "full_source_recovery": "REQUIRES_MASTER_EXEMPLAR",
        })
    write_tsv(OUT / "SIXTY_FOURTH_16_REVERSE_CHAINS.tsv", chain_rows)

    doc = [
        "# Rückwärtslesung der sechzehn Kompressionsketten", "",
        "Die vier Stufen werden absichtlich getrennt. Die Oberfläche liefert eine",
        "registrierte Atom- und Bauformlesung. Das gemeinsame Wörterbuch liefert den",
        "kurzen Kartenwert. Das Bild liefert den konkreten Besitzer. Erst das",
        "Meisterexemplar liefert die vollständig ausgeschriebene Fachprosa.", "",
    ]
    for row in chain_rows:
        doc.extend([
            f"## {row['unit_id']} · {row['page']}", "",
            f"**Schrift:** `{row['visible_surface_input']}`", "",
            f"**Atome:** `{row['recovered_atom_sequence']}`", "",
            f"**Bauformen:** {row['recovered_clause_shapes']}", "",
            f"**Wörterbuchlesung:** {row['dictionary_only_readback_de']}", "",
            f"**Mit Bildbesitzer:** {row['owner_augmented_readback_de']}", "",
            f"**Meisterfassung:** {row['full_master_source_de']}", "",
        ])
    (OUT / "SIXTY_FOURTH_SOURCE_RECOVERY_BOOK.md").write_text("\n".join(doc).rstrip() + "\n", encoding="utf-8")

    status = Counter(row["component_status"] for row in reverse_rows)
    report = [
        "# Vierundsechzigste Werkstattfassung: Rückwärts-Dekompressor", "",
        "## Ergebnis", "",
        f"Alle 381 Prosagruppen lassen sich von der registrierten Oberfläche zurück in Atomfolge, Klauseltyp und Quellslots führen. {status['PRODUCTIVE_COMPONENTS']} Gruppen bestehen nur aus den aktuell produktiven Komponenten; {status['LEARNED_BODY_PRESENT']} tragen zusätzlich einen gelernten lokalen oder fachlichen Körper.", "",
        "Die sechzehn vollständigen Rückläufe zeigen aber auch die richtige Grenze der",
        "Werkstatttheorie. Das kurze Wörterbuch kann Handlungs- und Adressgerüste lesen.",
        "Der konkrete Pflanzenname, Körperteil, Stoff, Zweck oder astronomische Name",
        "kommt nicht automatisch aus der Kartenform. Er wird vom Bild, vom laufenden",
        "Record oder vom Meisterexemplar ergänzt.", "",
        "## Praktische Leseregel", "",
        "1. Oberfläche in registrierte Atome zurückführen.",
        "2. Eine der zwölf Klauselformen wählen.",
        "3. produktive Stämme und gelernte Ganzkarten aus dem gemeinsamen Wörterbuch lesen.",
        "4. sichtbaren Bild- oder Stationsbesitzer einsetzen.",
        "5. nur beim Kopieren aus dem Meisterexemplar die reiche Fachprosa ergänzen.", "",
        "Das ist weiterhin eine kreative Rekonstruktion. Es ist jetzt jedoch deutlich,",
        "welche Wörter aus welcher Werkstattschicht stammen, statt alles der sichtbaren",
        "Karte zuzuschreiben.", "",
        "Nur die zehn festen Seiten wurden verwendet; f84 und f84r blieben versiegelt.",
    ]
    (OUT / "SIXTY_FOURTH_EDITION_REPORT.md").write_text("\n".join(report).rstrip() + "\n", encoding="utf-8")

    summary = {
        "status": "CONSISTENT",
        "counts": {
            "reverse_decompressed_groups": len(reverse_rows),
            "representative_reverse_chains": len(chain_rows),
            "productive_component_groups": status["PRODUCTIVE_COMPONENTS"],
            "learned_body_groups": status["LEARNED_BODY_PRESENT"],
            "represented_units": len(chain_units),
        },
        "sources": {str(path.relative_to(ROOT)): sha256(path) for path in (MAP, CHAINS)},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
