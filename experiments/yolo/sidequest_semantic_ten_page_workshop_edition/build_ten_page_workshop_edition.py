#!/usr/bin/env python3
"""Assemble the current prose and Astro readings into one workshop edition."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
PROSE_SURFACES = ROOT / "experiments/yolo/sidequest_semantic_surface_compiler/COMPLETE_230_SURFACE_PARSE.tsv"
PROSE_EVENTS = ROOT / "experiments/yolo/sidequest_semantic_clause_attachment/COMPLETE_381_ATTACHED_EVENTS.tsv"
PROSE_STATEMENTS = ROOT / "experiments/yolo/sidequest_semantic_speakable_edition/COMPLETE_116_SPEAKABLE_STATEMENTS.tsv"
PROSE_EDITION = ROOT / "experiments/yolo/sidequest_semantic_speakable_edition/SPEAKABLE_ELEVEN_RECORD_EDITION.md"
ASTRO_GROUPS = ROOT / "experiments/yolo/sidequest_semantic_speakable_astro_edition/COMPLETE_395_SPEAKABLE_ASTRO_GROUPS.tsv"
ASTRO_LOCI = ROOT / "experiments/yolo/sidequest_semantic_speakable_astro_edition/COMPLETE_142_SPEAKABLE_ASTRO_LOCI.tsv"
ASTRO_EDITION = ROOT / "experiments/yolo/sidequest_semantic_speakable_astro_edition/THREE_SPEAKABLE_ASTRO_PAGES.md"
STEMS = ROOT / "experiments/yolo/sidequest_semantic_cross_register_paradigms/REVISED_COMMON_STEM_DICTIONARY.tsv"
FAMILIES = ROOT / "experiments/yolo/sidequest_semantic_cross_register_paradigms/PRODUCTIVE_CROSS_REGISTER_FAMILIES.tsv"
MODIFIERS = ROOT / "experiments/yolo/sidequest_semantic_modifier_lattice/MODIFIER_DECISIONS.tsv"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def main() -> None:
    prose_surfaces = read(PROSE_SURFACES)
    prose_events = read(PROSE_EVENTS)
    prose_statements = read(PROSE_STATEMENTS)
    astro_groups = read(ASTRO_GROUPS)
    astro_loci = read(ASTRO_LOCI)
    stems = read(STEMS)
    families = read(FAMILIES)
    modifiers = read(MODIFIERS)
    stem_values = {row["atom"]: row["short_common_value_de"] for row in stems}

    prose_by_surface = {row["visible_surface"]: row for row in prose_surfaces}
    astro_by_surface: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in astro_groups:
        astro_by_surface[row["visible_surface"]].append(row)
    all_surfaces = sorted(set(prose_by_surface) | set(astro_by_surface))

    surface_rows = []
    surface_id = {}
    for serial, surface in enumerate(all_surfaces, 1):
        sid = f"SF{serial:04d}"
        surface_id[surface] = sid
        prose = prose_by_surface.get(surface)
        astro = astro_by_surface.get(surface, [])
        if prose and astro:
            register_status = "PROSE_AND_ASTRO"
        elif prose:
            register_status = "PROSE_ONLY"
        else:
            register_status = "ASTRO_ONLY"
        if prose:
            sequences = [prose["corrected_semantic_atoms"]]
        else:
            sequences = sorted({row["spoken_atom_sequence"] for row in astro})
        common_parts = []
        for sequence in sequences:
            if sequence == "NONE":
                continue
            values = [stem_values.get(atom, atom) for atom in sequence.split("+")]
            common_parts.append(" + ".join(values))
        common_nucleus = " || ".join(dict.fromkeys(common_parts)) if common_parts else "GELERNTES LOKALES GANZWORT"
        astro_values = sorted({row["speakable_value_de"] for row in astro})
        owners = sorted({row["visible_owner"] for row in astro})
        surface_rows.append({
            "surface_id": sid, "visible_surface": surface, "register_status": register_status,
            "common_atom_sequences": "|".join(sequences), "common_nucleus_de": common_nucleus,
            "prose_master_card_id": prose["master_card_id"] if prose else "NONE",
            "prose_short_value_de": prose["short_default_de"] if prose else "NONE",
            "prose_occurrences": prose["observed_events"] if prose else 0,
            "astro_short_values_de": " || ".join(astro_values) if astro_values else "NONE",
            "astro_occurrences": len(astro), "astro_owner_count": len(owners),
            "astro_owners": "|".join(owners) if owners else "NONE",
            "reading_rule_de": "lies gemeinsamen Kern; Besitzer/Register liefert lokale Expansion" if register_status == "PROSE_AND_ASTRO" else "lies den registrierten Werkstattwert dieses Registers",
        })
    write(HERE / "TEN_PAGE_487_SURFACE_DICTIONARY.tsv", surface_rows, list(surface_rows[0]))

    statement_by_id = {row["statement_id"]: row for row in prose_statements}
    locus_by_key = {(row["page"], row["locus"]): row for row in astro_loci}
    ledger_rows = []
    for event in prose_events:
        statement = statement_by_id[event["statement_id"]]
        ledger_rows.append({
            "unified_serial": len(ledger_rows) + 1, "register": "PROSE", "page": event["page"],
            "source_group_id": event["event_id"], "reading_unit_id": event["statement_id"],
            "visible_owner": event["record_unit_id"], "visible_surface": event["surface_display"],
            "surface_id": surface_id[event["surface_display"]], "atom_sequence": event["corrected_semantic_atoms"],
            "short_value_de": event["short_default_de"], "unit_reading_de": statement["speakable_reading_de"],
            "lookup_mode": "PROSE_STATEMENT_ATTACHMENT",
        })
    for group in astro_groups:
        locus = locus_by_key[(group["page"], group["locus"])]
        ledger_rows.append({
            "unified_serial": len(ledger_rows) + 1, "register": "ASTRO", "page": group["page"],
            "source_group_id": group["opaque_local_id"], "reading_unit_id": group["locus"],
            "visible_owner": group["visible_owner"], "visible_surface": group["visible_surface"],
            "surface_id": surface_id[group["visible_surface"]], "atom_sequence": group["spoken_atom_sequence"],
            "short_value_de": group["speakable_value_de"], "unit_reading_de": locus["speakable_locus_reading_de"],
            "lookup_mode": group["reading_source"],
        })
    write(HERE / "TEN_PAGE_776_SPEAKABLE_LEDGER.tsv", ledger_rows, list(ledger_rows[0]))

    unit_rows = []
    for statement in prose_statements:
        unit_rows.append({
            "unit_serial": len(unit_rows) + 1, "unit_type": "PROSE_STATEMENT", "register": "PROSE",
            "page": statement["page"], "unit_id": statement["statement_id"],
            "visible_owner": statement["record_unit_id"], "group_count": len(statement["surface_sequence"].split()),
            "surface_sequence": statement["surface_sequence"], "speakable_reading_de": statement["speakable_reading_de"],
            "ordering_rule": "registered statement order; physical line is not sentence end",
        })
    for locus in astro_loci:
        unit_rows.append({
            "unit_serial": len(unit_rows) + 1, "unit_type": "ASTRO_OWNER_LOCUS", "register": "ASTRO",
            "page": locus["page"], "unit_id": locus["locus"], "visible_owner": locus["visible_owner"],
            "group_count": locus["group_count"], "surface_sequence": locus["surface_sequence"],
            "speakable_reading_de": locus["speakable_locus_reading_de"],
            "ordering_rule": "local owner order only; no global wheel start/direction",
        })
    write(HERE / "TEN_PAGE_258_READING_UNITS.tsv", unit_rows, list(unit_rows[0]))

    pocket = "# Taschen-Codebuch der Zehnseiten-Werkstatt\n\n"
    pocket += "## 25 gemeinsame Kerne\n\n"
    for row in stems:
        pocket += f"- `{row['atom']}` — **{row['short_common_value_de']}**; nass: {row['wet_owner_expansion_de']}; Himmel: {row['celestial_owner_expansion_de']}.\n"
    pocket += "\n## Produktive Reihen\n\n"
    for row in families:
        if row["status"] not in {"PROMOTED_PRODUCTIVE_FAMILY", "FORWARD_PREDICTED_SINGLE_CELL"}:
            continue
        pocket += f"- `{row['atom_sequence']}` — **{row['common_nucleus_de']}**; Formen `{row['surface_forms']}`.\n"
    pocket += "\n## Gebundene Modifier\n\n"
    for row in modifiers:
        pocket += f"- `{row['modifier']}` — **{row['short_value_de']}**; {row['licensing_boundary']}.\n"
    pocket += """

## Leseregel in acht Schritten

1. Bestimme Prosa-Statement oder sichtbaren Diagrammbesitzer.
2. Erkenne die registrierte Oberfläche; q/s/ch/d/t können Renderer sein.
3. Nimm den längsten bekannten Körper, etwa AIR, CHD~CHED oder CKHE.
4. Lies OK/OL/OT als aktivieren/fortsetzen/Folge.
5. Lies AIIN/AIN/IIN als Sollwert/Portion/Stufe.
6. Lies AL/AR/AIR als Ziel/Quelle/Lauf oder Bahn.
7. Lies E/EE/EEE und Y/DY nur in einer belegten Familie.
8. Fülle den konkreten Stoff, Stern, Ring, Behälter oder Stationswert aus Bildbesitzer bzw. gelerntem Ganzwort.
"""
    (HERE / "TEN_PAGE_POCKET_CODEBOOK.md").write_text(pocket, encoding="utf-8")

    prose_text = PROSE_EDITION.read_text(encoding="utf-8")
    astro_text = ASTRO_EDITION.read_text(encoding="utf-8")
    complete = "# Vollständige Zehnseiten-Werkstattausgabe\n\n"
    complete += "Die Ausgabe verbindet elf Prosa-Records und drei Himmelsseiten mit einem gemeinsamen Taschen-Codebuch.\n\n"
    complete += prose_text.replace("# Sprechbare Elf-Record-Ausgabe", "## Teil I — Elf Prosa-Records", 1)
    complete += "\n\n---\n\n"
    complete += astro_text.replace("# Sprechbare Ausgabe der drei Himmelsseiten", "## Teil II — Drei Himmelsseiten", 1)
    (HERE / "COMPLETE_TEN_PAGE_WORKSHOP_EDITION.md").write_text(complete, encoding="utf-8")

    register_counts = Counter(row["register_status"] for row in surface_rows)
    report = f"""# Eine gemeinsame Zehnseiten-Werkstattausgabe

## Stand

Die getrennten Leser sind jetzt ein Buch: {len(surface_rows)} verschiedene sichtbare Formen, {len(ledger_rows)} sichtbare Gruppen und {len(unit_rows)} lesbare Einheiten. Das Oberflächenwörterbuch enthält {register_counts['PROSE_AND_ASTRO']} Formen in beiden Registern, {register_counts['PROSE_ONLY']} nur in Prosa und {register_counts['ASTRO_ONLY']} nur in den Himmeltafeln.

Die Architektur ist eine **Mischung aus Fachkürzeln und gelernten Ganzwörtern**:

- 25 kurze gemeinsame Kerne;
- acht produktive Mehrformenreihen und drei vorwärts gefüllte Einzelzellen;
- E/EE/EEE-Grade sowie gebundenes Y/DY;
- viele gelernte Sachkarten für konkrete Pflanzen-, Gefäß-, Stern-, Sektor- und Tabellenwerte.

## Praktische Lesung

Die Prosa liefert die laufenden Arbeitsschritte; die Diagramme liefern adressierbare Bedingungen und Werte. In beiden Registern heißen die tragenden Kerne Quelle, Ziel, Sollwert, Stufe, Folge, Fortsetzung, Aktivierung, Lauf/Bahn und Umsetzen. Das Bild bzw. der lokale Nomenklator sagt, ob damit Wurzel, Ansatz, Wasserlauf, Becken, Sternsektor oder Himmelsbahn gemeint ist.

`COMPLETE_TEN_PAGE_WORKSHOP_EDITION.md` ist die aktuelle vollständige Lesefassung. `TEN_PAGE_POCKET_CODEBOOK.md` ist die lehrbare Kurzfassung. Die TSVs binden jede Form und jedes Ereignis zurück an seine Quelle.
"""
    (HERE / "TEN_PAGE_WORKSHOP_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS", "surface_types": len(surface_rows), "groups": len(ledger_rows),
        "reading_units": len(unit_rows), "prose_groups": sum(row["register"] == "PROSE" for row in ledger_rows),
        "astro_groups": sum(row["register"] == "ASTRO" for row in ledger_rows),
        "prose_units": sum(row["register"] == "PROSE" for row in unit_rows),
        "astro_units": sum(row["register"] == "ASTRO" for row in unit_rows),
        "surface_register_counts": dict(sorted(register_counts.items())),
        "common_stems": len(stems),
    }
    (HERE / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
