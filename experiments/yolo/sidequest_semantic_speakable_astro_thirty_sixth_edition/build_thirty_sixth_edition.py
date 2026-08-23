#!/usr/bin/env python3
"""Build a speakable three-instrument edition without imposing orientation."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
UNITS = ROOT / "experiments/yolo/sidequest_semantic_stem_aligned_twentieth_edition/TWENTIETH_258_UNIT_TRANSLATIONS.tsv"
LOCI = ROOT / "experiments/yolo/sidequest_theory_candidates_v75/V75_SELECTED_142_LOCUS_CELESTIAL_EDITION.tsv"
NAMESPACES = ROOT / "experiments/yolo/sidequest_theory_candidates_v75/V75_SELECTED_NAMESPACE_REGISTRY.tsv"


PAGE_PROCEDURES = {
    "f67r2": {
        "name": "zwei getrennte Vergleichsräder",
        "entry": "Wähle zuerst sichtbar linkes oder rechtes Rad; danach genau Sektor, Sternplatz, Phase oder Ringband desselben Rades.",
        "read": "Sprich Klasse, Quelle, Ziel, Stufe und Wert nur soweit die Karten sie nennen; ergänze den lokalen Himmelswert aus dem Meisterexemplar.",
        "output": "Notiere eine einzelne Bedingungs- oder Vergleichsangabe für den Arbeitsfall.",
        "guard": "Kein Sprung zwischen den beiden Rädern; keine angenommene Nullposition oder Drehrichtung.",
    },
    "f68r1": {
        "name": "mehrpaneeliger Sternstationsatlas",
        "entry": "Wähle zuerst das sichtbare Teilbild oder seinen Kopf; danach genau den gezeichneten Sternplatz oder den lokalen Zentralschlüssel.",
        "read": "Sprich Eingang, Klasse, Quelle, Ziel, Stufe, Markierung und sichtbares Ergebnis als lokale Stationskarte.",
        "output": "Notiere Stationsklasse und Bedingungswert, ohne die 28 Sterne zu einer Folge zu zwingen.",
        "guard": "Mehrere Zentren bleiben getrennt; kein seitenweites Zentrum und kein Schlüssel zu f69v.",
    },
    "f69v": {
        "name": "drei selbständige Radtafeln",
        "entry": "Wähle links einen sichtbaren 28er-Platz oder lies stattdessen den eigenen Ringtext des mittleren beziehungsweise rechten Rades.",
        "read": "Links sprich Platz, Quelle, Ziel, Grad und Markierung; mittig eine örtliche Qualitätsablesung; rechts eine örtliche Licht- oder Zustandsablesung.",
        "output": "Notiere bis zu drei getrennte Werte, wenn der Meister sie für denselben Auftrag zusammenstellt.",
        "guard": "Die drei Werte werden nicht durch eine gezeichnete Kante verbunden; links ist keine Laufrichtung vorgegeben.",
    },
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def clean_literal(text: str) -> str:
    pieces = []
    for piece in text.split("; "):
        if piece == "NONE":
            pieces.append("lokalen Exemplarwert")
        else:
            pieces.append(piece)
    return "; ".join(pieces)


def locus_verb(namespace: str) -> str:
    if "QUARANTINE" in namespace:
        return "Kopiere diesen Hinweis separat und lasse seine Zuordnung offen"
    if "HEADER" in namespace:
        return "Setze den lokalen Modus dieses Teilbildes"
    if "STAR_SLOT" in namespace:
        return "Wähle diesen gezeichneten Sternplatz"
    if "LEFT_WHEEL" in namespace and "F69" in namespace:
        return "Wähle diesen sichtbaren Platz des linken 28er-Inventars"
    if "WHEEL" in namespace:
        return "Lies diesen sichtbaren Posten nur im gewählten Rad"
    return "Lies diese sichtbare lokale Adresse"


def main() -> None:
    unit_rows = [row for row in read_tsv(UNITS) if row["register"] == "ASTRO"]
    locus_rows = read_tsv(LOCI)
    namespaces = read_tsv(NAMESPACES)
    units_by_key = {(row["page"], row["unit_id"]): row for row in unit_rows}
    namespace_by_locus = {}
    for namespace in namespaces:
        for locus in namespace["source_loci"].split("|"):
            if locus in namespace_by_locus:
                raise RuntimeError(f"duplicate namespace locus: {locus}")
            namespace_by_locus[locus] = namespace

    spoken = []
    for locus in locus_rows:
        key = (locus["page"], locus["locus"])
        unit = units_by_key.get(key)
        if unit is None:
            raise RuntimeError(f"missing unit: {key}")
        namespace = namespace_by_locus.get(locus["locus"])
        if namespace is None:
            raise RuntimeError(f"missing namespace: {locus['locus']}")
        literal = clean_literal(unit["literal_card_reading_de"])
        verb = locus_verb(namespace["namespace_id"])
        instruction = f"{verb}: {literal}. Notiere das Ergebnis als lokalen Wert dieser Adresse."
        spoken.append({
            "page": locus["page"],
            "locus": locus["locus"],
            "namespace_id": namespace["namespace_id"],
            "visible_kind": namespace["visible_kind"],
            "visible_owner": unit["visible_owner"],
            "group_count": unit["group_count"],
            "surface_sequence": unit["surface_sequence"],
            "atom_sequence": unit["atom_sequence"],
            "portable_card_reading_de": literal,
            "spoken_instruction_de": instruction,
            "answer_slot_de": "LOKALER_BEDINGUNGS_ODER_NACHSCHLAGEWERT",
            "orientation_rule": "DIREKTE_SICHTADRESSE__KEINE_ERFUNDENE_REIHENFOLGE",
            "crosspage_rule": "KEIN_F68_F69_SCHLUESSEL__MEISTER_KANN_WERTE_IM_AUFTRAG_ZUSAMMENSTELLEN",
        })
    write_tsv(OUT / "THIRTY_SIXTH_142_SPOKEN_LOCI.tsv", spoken, list(spoken[0]))

    module_rows = []
    for namespace in namespaces:
        page = namespace["page"]
        members = [row for row in spoken if row["namespace_id"] == namespace["namespace_id"]]
        module_rows.append({
            "namespace_id": namespace["namespace_id"],
            "page": page,
            "visible_kind": namespace["visible_kind"],
            "locus_count": len(members),
            "group_count": sum(int(row["group_count"]) for row in members),
            "master_entry_de": PAGE_PROCEDURES[page]["entry"],
            "apprentice_read_de": PAGE_PROCEDURES[page]["read"],
            "output_de": PAGE_PROCEDURES[page]["output"],
            "local_rule_de": namespace["entry_rule"],
            "do_not_assume_de": PAGE_PROCEDURES[page]["guard"],
        })
    write_tsv(OUT / "THIRTY_SIXTH_13_INSTRUMENT_MODULES.tsv", module_rows, list(module_rows[0]))

    page_lines = ["# Drei sprechbare Himmelsinstrumente", ""]
    for page in ("f67r2", "f68r1", "f69v"):
        proc = PAGE_PROCEDURES[page]
        page_members = [row for row in spoken if row["page"] == page]
        page_lines.extend([
            f"## {page}: {proc['name']}",
            "",
            f"1. **Einstieg:** {proc['entry']}",
            f"2. **Lesen:** {proc['read']}",
            f"3. **Ausgabe:** {proc['output']}",
            f"4. **Werkstattgrenze:** {proc['guard']}",
            "",
            "### Vollständige lokale Lesung",
            "",
        ])
        for row in page_members:
            page_lines.append(f"- `{row['locus']}` / {row['visible_owner']}: {row['spoken_instruction_de']}")
        page_lines.append("")
    (OUT / "THIRTY_SIXTH_THREE_SPOKEN_INSTRUMENTS.md").write_text("\n".join(page_lines).rstrip() + "\n", encoding="utf-8")

    manual = [
        "# Taschenanweisung für die drei Kreisblätter",
        "",
        "Der Schreiber bestimmt zuerst die sichtbare Teiltafel. Er liest danach nur die",
        "Karten an der gewählten Adresse und schreibt einen lokalen Arbeitswert in den",
        "mündlich zusammengestellten Auftrag. Die Kreisblätter bilden keine fortlaufende",
        "Prosa und müssen nicht dieselbe Ordnung besitzen.",
        "",
    ]
    for page in ("f67r2", "f68r1", "f69v"):
        proc = PAGE_PROCEDURES[page]
        counts = Counter(row["page"] for row in spoken)
        groups = sum(int(row["group_count"]) for row in spoken if row["page"] == page)
        manual.extend([
            f"## {page}",
            "",
            f"{proc['entry']} {proc['read']} {proc['output']}",
            "",
            f"Umfang: {counts[page]} sichtbare Adressen / {groups} Gruppen. {proc['guard']}",
            "",
        ])
    (OUT / "THIRTY_SIXTH_ASTRO_APPRENTICE_MANUAL.md").write_text("\n".join(manual).rstrip() + "\n", encoding="utf-8")

    page_counts = {page: {"loci": sum(row["page"] == page for row in spoken), "groups": sum(int(row["group_count"]) for row in spoken if row["page"] == page)} for page in PAGE_PROCEDURES}
    summary = {
        "status": "PASS",
        "counts": {
            "pages": 3,
            "namespaces": len(module_rows),
            "loci": len(spoken),
            "visible_groups": sum(int(row["group_count"]) for row in spoken),
            "page_counts": page_counts,
        },
        "sources": {str(path.relative_to(ROOT)): sha256(path) for path in (UNITS, LOCI, NAMESPACES)},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
