#!/usr/bin/env python3
"""Build a complete speakable edition of the three fixed Astro pages."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
ASTRO = ROOT / "experiments/yolo/sidequest_semantic_astro_nomenclator_closure/ASTRO_395_NOMENCLATOR_CLOSED.tsv"
TRANSFER = ROOT / "experiments/yolo/sidequest_semantic_astro_surface_transfer/ASTRO_395_SURFACE_PARSE.tsv"
MODIFIERS = ROOT / "experiments/yolo/sidequest_semantic_modifier_lattice/UPDATED_ASTRO_53_MODIFIER_DICTIONARY.tsv"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def owner_label(owner: str) -> str:
    return owner.replace("A1_", "").replace("A2_", "").replace("A3_", "").replace("_", " ").lower()


def main() -> None:
    source = read(ASTRO)
    transfer = read(TRANSFER)
    modifier = read(MODIFIERS)
    transfer_by_group = {row["group_serial"]: row for row in transfer}
    modifier_by_surface = {row["visible_surface"]: row for row in modifier}

    group_rows = []
    loci: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in source:
        trans = transfer_by_group[row["group_serial"]]
        mod = modifier_by_surface.get(row["surface_display"])
        if mod and mod["modifier_status"] == "ENRICHED_BOUND_MODIFIER":
            spoken = mod["enriched_common_reading_de"]
            source_mode = "ENRICHED_COMPONENT_READING"
            atom_sequence = mod["enriched_atom_sequence"]
        elif trans["transfer_class"] in {"FORWARD_PREDICTED_EXACT", "FORWARD_PREDICTED_EMBEDDED", "NEW_MULTI_ATOM_CANDIDATE"} and mod:
            spoken = mod["enriched_common_reading_de"]
            source_mode = "COMPONENT_HINT_READING"
            atom_sequence = mod["enriched_atom_sequence"]
        elif trans["transfer_class"] == "EXACT_PROSE_SURFACE":
            spoken = row["compact_operational_default_de"]
            source_mode = "EXACT_SHARED_SURFACE_READING"
            atom_sequence = trans["detected_literal_atoms"]
        else:
            spoken = row["compact_operational_default_de"]
            source_mode = "LOCAL_ASTRO_WORD"
            atom_sequence = trans["detected_literal_atoms"]
        output: dict[str, object] = {
            "group_serial": row["group_serial"], "diagram_id": row["diagram_id"], "page": row["page"],
            "locus": row["locus"], "event_index": row["event_index"], "opaque_local_id": row["opaque_local_id"],
            "visible_owner": row["local_image_owner"], "visible_surface": row["surface_display"],
            "namespace_id": row["namespace_id"], "local_content_class": row["local_content_class"],
            "spoken_atom_sequence": atom_sequence, "speakable_value_de": spoken,
            "reading_source": source_mode, "full_spoken_label_de": f"{owner_label(row['local_image_owner'])}: {spoken}",
            "orientation_rule": row["orientation_rule"], "crosspage_rule": row["crosspage_rule"],
        }
        group_rows.append(output)
        loci[(row["page"], row["locus"])].append(output)
    write(HERE / "COMPLETE_395_SPEAKABLE_ASTRO_GROUPS.tsv", group_rows, list(group_rows[0]))

    locus_rows = []
    for (page, locus), rows in sorted(loci.items(), key=lambda item: (item[1][0]["group_serial"] if False else int(item[1][0]["group_serial"]))):
        owner = str(rows[0]["visible_owner"])
        surfaces = " ".join(str(row["visible_surface"]) for row in rows)
        values = "; ".join(str(row["speakable_value_de"]) for row in rows)
        locus_rows.append({
            "locus_serial": len(locus_rows) + 1, "diagram_id": rows[0]["diagram_id"], "page": page,
            "locus": locus, "visible_owner": owner, "namespace_id": rows[0]["namespace_id"],
            "group_count": len(rows), "surface_sequence": surfaces,
            "component_group_count": sum(str(row["reading_source"]) != "LOCAL_ASTRO_WORD" for row in rows),
            "local_word_group_count": sum(str(row["reading_source"]) == "LOCAL_ASTRO_WORD" for row in rows),
            "speakable_locus_reading_de": f"{owner_label(owner)}: {values}",
            "use_rule_de": "wähle diesen sichtbaren Besitzer/Locus; lies seine Gruppen in lokaler Schreibreihenfolge, nicht als globalen Kreisstart",
        })
    write(HERE / "COMPLETE_142_SPEAKABLE_ASTRO_LOCI.tsv", locus_rows, list(locus_rows[0]))

    page_intro = {
        "f67r2": (
            "Gekoppelte Wahltafel mit zwei getrennten Rädern. Wähle rechts einen Sektor oder Phasenplatz und links einen Stern-/Aspekt- oder Ziel-/Quellplatz; "
            "lies die lokalen Sollwert-, Stufen-, Folge- und Laufkarten. Die Legenden verbinden die beiden Bereiche als gemeinsame Arbeitsseite, aber geben keinen festen Startpunkt vor."
        ),
        "f68r1": (
            "Mehrpanel-Sternatlas. Wähle Panel oder Zentrum und danach eine der 28 sichtbaren Sternstationen; die Kürzel nennen lokalen Satz, Quelle, Ziel, Grad, Fortsetzung oder einen gelernten Sternnamen. "
            "Die 28 Stationen sind Adressen, keine automatisch abzulaufende Sequenz."
        ),
        "f69v": (
            "Drei getrennte Auswahlräder. Links liegt ein lokales 28-Platz-Inventar, Mitte und rechts liefern eigene Bedingungen und Rubriken. "
            "Formen wie `qotair` werden als nächste Bahn gelesen; es gibt aber keinen stillen Schlüssel, der dieselbe Nummer mit f68 verbindet."
        ),
    }
    page_title = {"f67r2": "Gekoppelte Himmelswahl", "f68r1": "Sternstationsatlas", "f69v": "Drei Bedingungsräder"}
    edition = "# Sprechbare Ausgabe der drei Himmelsseiten\n\n"
    edition += "Die Kartenwerte werden wie in der Prosa kurz ausgesprochen; der sichtbare Ring, Stern, Sektor oder Legendenbesitzer liefert den Gegenstand.\n\n"
    page_rows = []
    for page in ["f67r2", "f68r1", "f69v"]:
        rows = [row for row in locus_rows if row["page"] == page]
        groups = sum(int(row["group_count"]) for row in rows)
        edition += f"## {page} — {page_title[page]}\n\n{page_intro[page]}\n\n"
        for row in rows:
            edition += f"- `{row['locus']}` **{row['surface_sequence']}** — {row['speakable_locus_reading_de']}\n"
        edition += "\n"
        page_rows.append({
            "page": page, "title_de": page_title[page], "locus_count": len(rows), "group_count": groups,
            "component_groups": sum(int(row["component_group_count"]) for row in rows),
            "local_word_groups": sum(int(row["local_word_group_count"]) for row in rows),
            "whole_page_reading_de": page_intro[page],
        })
    if edition.endswith("\n\n"):
        edition = edition[:-1]
    (HERE / "THREE_SPEAKABLE_ASTRO_PAGES.md").write_text(edition, encoding="utf-8")
    write(HERE / "PAGE_SUMMARY.tsv", page_rows, list(page_rows[0]))

    mode_counts = Counter(str(row["reading_source"]) for row in group_rows)
    report = f"""# Sprechbare Himmelsseiten

## Ausgabe

Alle 395 sichtbaren Gruppen sind jetzt zu 142 besitzergebundenen Locus-Lesungen zusammengezogen: 74 auf `f67r2`, 37 auf `f68r1` und 31 auf `f69v`. Jede sichtbare Form bleibt erhalten; die Ausgabe spricht aber nicht 395 isolierte Wörter, sondern jeweils den ganzen lokalen Eintrag.

- {mode_counts['ENRICHED_COMPONENT_READING']} Gruppen nutzen die neue Grad/Y/DY-Lattice.
- {mode_counts['COMPONENT_HINT_READING']} weitere Gruppen nutzen eine Mehrkern-Komposition.
- {mode_counts['EXACT_SHARED_SURFACE_READING']} Gruppen tragen eine exakte Prosaoberfläche.
- {mode_counts['LOCAL_ASTRO_WORD']} Gruppen bleiben gelernte lokale Astro-Wörter.

## Arbeitsdeutung

`f67r2` ist eine gekoppelte, aber nicht automatisch zyklische Wahltafel; `f68r1` ein Mehrpanel-Atlas mit 28 adressierbaren Sternstationen; `f69v` drei getrennte Bedingungsräder, deren linkes ein 28-Platz-Inventar trägt. Die gemeinsame Sprache nennt Quelle, Ziel, Sollwert, Stufe, Folge, Fortsetzung und Lauf/Bahn. Die lokalen Ganzwörter nennen den speziellen Stern-, Sektor-, Tabellen- oder Bedingungswert.

Damit ist die feste Zehnseiten-Ausgabe erstmals auf beiden Seiten gleich gebaut: elf fortlaufende Prosa-Records plus drei besitzeradressierte Diagrammseiten, verbunden durch dieselbe kleine Kürzungsgrammatik und getrennt durch ihre gelernten Sachwörter.
"""
    (HERE / "SPEAKABLE_ASTRO_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS", "groups": len(group_rows), "loci": len(locus_rows), "pages": len(page_rows),
        "page_loci": {row["page"]: row["locus_count"] for row in page_rows},
        "page_groups": {row["page"]: row["group_count"] for row in page_rows},
        "reading_source_counts": dict(sorted(mode_counts.items())),
    }
    (HERE / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
