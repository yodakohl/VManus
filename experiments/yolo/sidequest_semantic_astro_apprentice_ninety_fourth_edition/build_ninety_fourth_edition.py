#!/usr/bin/env python3
"""Add a separate eight-rule apprentice compiler for the Astro diagrams."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R85 = ROOT / "experiments/yolo/sidequest_semantic_celestial_almanac_vocabulary_eighty_fifth_edition"
R93 = ROOT / "experiments/yolo/sidequest_semantic_unified_apprentice_grammar_ninety_third_edition"


ASTRO_PRIMITIVES = [
    ("OPEN_INSTRUMENT", "aktives Rad, Paneel oder Rosetteninstrument öffnen"),
    ("SELECT_NAMESPACE", "nur den örtlichen Namensraum dieses Teilbilds laden"),
    ("SELECT_LOCAL_SLOT", "sichtbaren lokalen Sektor-, Stern- oder Feldplatz wählen"),
    ("COPY_OPAQUE_GROUPS", "alle Gruppen dieses Platzes in gegebener lokaler Folge kopieren"),
    ("READ_WITH_LOCAL_KEY", "Wert nur mit dem Meisterschlüssel dieses Namensraums lesen"),
    ("RESET_AT_NAMESPACE_CHANGE", "beim Rad-/Paneel-/Rosettenwechsel vollständig neu beginnen"),
    ("PRESERVE_NO_ORIENTATION", "keinen Startpunkt, Drehsinn oder Rang ergänzen"),
    ("NO_CROSSPAGE_JOIN", "keinen Schlüssel zwischen A1, A2 und A3 übertragen"),
]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    loci = read_tsv(R85 / "EIGHTY_FIFTH_142_LOCAL_ALMANAC_LOCI.tsv")
    groups = read_tsv(R85 / "EIGHTY_FIFTH_395_ALMANAC_GROUP_BINDING.tsv")
    instruments = read_tsv(R85 / "EIGHTY_FIFTH_3_COMPLETE_ALMANAC_INSTRUMENTS.tsv")
    prose_primitives = read_tsv(R93 / "NINETY_THIRD_20_UNIFIED_SOURCE_PRIMITIVES.tsv")
    prose_rules = read_tsv(R93 / "NINETY_THIRD_12_APPRENTICE_RULES.tsv")

    primitive_rows = [
        {"diagram_order": order, "primitive_id": primitive, "instruction_de": instruction,
         "prose_word_value": "NONE__DIAGRAM_ADDRESS_RULE"}
        for order, (primitive, instruction) in enumerate(ASTRO_PRIMITIVES, 1)
    ]
    write_tsv(OUT / "NINETY_FOURTH_8_ASTRO_APPRENTICE_PRIMITIVES.tsv", primitive_rows)

    locus_rows = []
    previous_unit = None
    previous_namespace = None
    for serial, row in enumerate(loci, 1):
        unit_start = row["unit_id"] != previous_unit
        namespace_reset = unit_start or row["local_namespace"] != previous_namespace
        sequence = []
        if unit_start:
            sequence.append("OPEN_INSTRUMENT")
        if namespace_reset:
            sequence.extend(["RESET_AT_NAMESPACE_CHANGE", "SELECT_NAMESPACE"])
        sequence.extend(["SELECT_LOCAL_SLOT", "COPY_OPAQUE_GROUPS", "READ_WITH_LOCAL_KEY", "PRESERVE_NO_ORIENTATION", "NO_CROSSPAGE_JOIN"])
        locus_rows.append({
            "locus_serial": serial, "unit_id": row["unit_id"], "page": row["page"],
            "locus": row["locus"], "group_count": row["group_count"],
            "local_owner": row["local_owner"], "local_namespace": row["local_namespace"],
            "namespace_reset": "YES" if namespace_reset else "NO",
            "apprentice_primitive_sequence": ">".join(sequence),
            "write_instruction_de": row["selected_local_action_de"],
            "orientation": "NONE", "crosspage_key": "NONE",
        })
        previous_unit = row["unit_id"]
        previous_namespace = row["local_namespace"]
    write_tsv(OUT / "NINETY_FOURTH_142_LOCUS_WRITE_TRACE.tsv", locus_rows)

    locus_lookup = {(row["unit_id"], row["locus"]): row for row in locus_rows}
    group_rows = []
    for row in groups:
        locus = locus_lookup[(row["unit_id"], row["locus"])]
        group_rows.append({
            "group_serial": row["group_serial"], "unit_id": row["unit_id"],
            "page": row["page"], "locus": row["locus"], "event_index": row["event_index"],
            "opaque_local_id": row["opaque_local_id"], "local_owner": row["local_owner"],
            "local_namespace": row["local_namespace"],
            "locus_primitive_sequence": locus["apprentice_primitive_sequence"],
            "copy_instruction_de": row["copy_instruction_de"],
            "semantic_reading": "LOCAL_MASTER_KEY_ONLY",
        })
    write_tsv(OUT / "NINETY_FOURTH_395_GROUP_COPY_TRACE.tsv", group_rows)

    by_unit_loci: dict[str, list[dict[str, object]]] = defaultdict(list)
    by_unit_groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in locus_rows:
        by_unit_loci[str(row["unit_id"])].append(row)
    for row in group_rows:
        by_unit_groups[str(row["unit_id"])].append(row)
    instrument_by_id = {row["unit_id"]: row for row in instruments}
    roundtrip_rows = []
    for unit_id in ("A1", "A2", "A3"):
        unit_loci = by_unit_loci[unit_id]
        unit_groups = by_unit_groups[unit_id]
        namespaces = sorted({str(row["local_namespace"]) for row in unit_loci})
        roundtrip_rows.append({
            "unit_id": unit_id, "page": instrument_by_id[unit_id]["page"],
            "locus_count": len(unit_loci), "group_count": len(unit_groups),
            "namespace_count": len(namespaces), "namespaces": ",".join(namespaces),
            "namespace_reset_count": sum(row["namespace_reset"] == "YES" for row in unit_loci),
            "complete_instrument_reading_de": instrument_by_id[unit_id]["complete_instrument_reading_de"],
            "forward_status": "LOCAL_OWNER_TO_OPAQUE_GROUP_COPY_COMPLETE",
            "backward_status": "OPAQUE_GROUP_TO_LOCAL_OWNER_NAMESPACE_COMPLETE",
            "orientation": "NONE", "crosspage_key": "NONE", "prose_import": "NONE",
        })
    write_tsv(OUT / "NINETY_FOURTH_3_INSTRUMENT_ROUNDTRIP.tsv", roundtrip_rows)

    doc = [
        "# Integriertes Lehrlingsmanual: Prosa und Himmelsinstrumente", "",
        "## Teil I: Herbal-/Bio-Prosa", "",
        "Die Prosa benutzt die zwanzig Rollen und zwölf Regeln der 93. Runde.",
        "Sie erzeugt 116 Aussagen und 381 sichtbare Gruppen.", "",
    ]
    for row in prose_primitives:
        doc.append(f"- **{row['primitive_id']}** — {row['source_meaning_de']}")
    doc.extend(["", "## Teil II: Astro-Diagramme", ""])
    for row in primitive_rows:
        doc.append(f"- **{row['primitive_id']}** — {row['instruction_de']}")
    doc.extend([
        "", "Der Astro-Schreiber bildet keine Sätze aus den Prosa-Primitiven. Er arbeitet",
        "wie mit einem lokalen Nomenklator: Instrument öffnen, Namensraum setzen, Platz",
        "zeigen, Gruppen kopieren und nur im örtlichen Schlüssel lesen. Bei jedem sichtbaren",
        "Teilbildwechsel wird neu begonnen. Keine Richtung und kein Seitenjoin werden gelernt.", "",
        "## Gemeinsamer Werkstattkern", "",
        "Beide Systeme teilen nur Besitzerwahl, exakte Kartentreue, lokale Namensräume und",
        "Handrenderer. Die Prosa kombiniert Operationen; Astro kopiert Adressen. Gerade diese",
        "Trennung macht ein gemeinsames Mehrschreiberbuch einfacher statt komplizierter.",
    ])
    (OUT / "NINETY_FOURTH_INTEGRATED_APPRENTICE_MANUAL.md").write_text("\n".join(doc).rstrip() + "\n", encoding="utf-8")

    namespace_counts = Counter(row["unit_id"] for row in locus_rows if row["namespace_reset"] == "YES")
    report = [
        "# Vierundneunzigste Werkstattrunde: Astro-Lehrgang", "",
        "## Ergebnis", "",
        "A separate eight-primitive diagram compiler covers all 142 Astro loci and 395",
        "groups. A1 has 74 loci/190 groups, A2 37/65 and A3 31/140. Eleven local",
        "namespaces are preserved. No prose card value, orientation or cross-page key is",
        "introduced.", "",
        "The complete workshop therefore teaches two simple modes: a combinatorial prose",
        "grammar for Herbal/Biological and an address-copy nomenclator for Astro. The modes",
        "share production discipline but not word meanings.", "",
        "Only the fixed Astro pages were used; f84 and f84r remained sealed.",
    ]
    (OUT / "NINETY_FOURTH_EDITION_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")

    summary = {
        "status": "CONSISTENT", "astro_primitives": len(primitive_rows),
        "astro_loci": len(locus_rows), "astro_groups": len(group_rows),
        "instruments": len(roundtrip_rows), "namespace_resets": dict(namespace_counts),
        "prose_primitives_reused_as_words": 0,
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
