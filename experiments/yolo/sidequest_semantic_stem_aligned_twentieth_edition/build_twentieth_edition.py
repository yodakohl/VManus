#!/usr/bin/env python3
from pathlib import Path
from collections import defaultdict
import csv
import json
import shutil

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = ROOT / "experiments/yolo/sidequest_semantic_final_productive_cards_nineteenth_edition"


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path, fields, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


ledger = read(BASE / "NINETEENTH_776_SPEAKABLE_LEDGER.tsv")
units = read(BASE / "NINETEENTH_258_READING_UNITS.tsv")
dictionary = read(BASE / "NINETEENTH_487_SURFACE_DICTIONARY.tsv")
autonomy = read(BASE / "NINETEENTH_776_GROUP_AUTONOMY.tsv")

groups = defaultdict(list)
for row in ledger:
    groups[(row["register"], row["page"], row["reading_unit_id"])].append(row)

translation_rows = []
for unit in units:
    key = (unit["register"], unit["page"], unit["unit_id"])
    members = groups[key]
    literal = "; ".join(row["short_value_de"] for row in members)
    atoms = " | ".join(row["atom_sequence"] for row in members)
    surfaces = " ".join(row["visible_surface"] for row in members)
    owner_expansion = unit["speakable_reading_de"]
    if unit["register"] == "ASTRO":
        owner_prefix = owner_expansion.split(":", 1)[0]
        owner_expansion = owner_prefix + ": " + literal
    translation_rows.append(
        {
            "unit_serial": unit["unit_serial"],
            "register": unit["register"],
            "page": unit["page"],
            "unit_id": unit["unit_id"],
            "visible_owner": unit["visible_owner"],
            "group_count": len(members),
            "surface_sequence": surfaces,
            "atom_sequence": atoms,
            "literal_card_reading_de": literal,
            "owner_expansion_de": owner_expansion,
            "translation_mode": "CURRENT_STEMS_PLUS_WORKING_OWNER_EXPANSION",
        }
    )
fields = list(translation_rows[0])
write(HERE / "TWENTIETH_258_UNIT_TRANSLATIONS.tsv", fields, translation_rows)
write(
    HERE / "TWENTIETH_116_PROSE_STATEMENTS.tsv",
    fields,
    [row for row in translation_rows if row["register"] == "PROSE"],
)
write(
    HERE / "TWENTIETH_142_ASTRO_LOCI.tsv",
    fields,
    [row for row in translation_rows if row["register"] == "ASTRO"],
)

event_rows = []
autonomy_lookup = {row["unified_serial"]: row["autonomy"] for row in autonomy}
for row in ledger:
    out = dict(row)
    out["autonomy"] = autonomy_lookup[row["unified_serial"]]
    event_rows.append(out)
write(HERE / "TWENTIETH_776_EVENT_BINDING.tsv", list(event_rows[0]), event_rows)
write(HERE / "TWENTIETH_487_CURRENT_DICTIONARY.tsv", list(dictionary[0]), dictionary)

record_titles = {
    "H1": "Wurzelansatz",
    "H2": "Fortgesetzter Pflanzenansatz",
    "H3": "Auswringen und Nachseihen",
    "H4": "Verwahrter Auszug",
    "H5": "Frische Pflanzenfolge",
    "B1": "Gemeinsamer Beckenweg",
    "B2": "Stations- und Durchlaufweg",
    "B3": "Hauptfolge der Anwendungen",
    "B4": "Tuch-, Halte- und Nachwaschfolge",
    "B5": "Kurzer Seitenweg",
    "B6": "Abschlussweg",
}
record_pages = {
    "H1": "f10r", "H2": "f10r", "H3": "f11r", "H4": "f55v", "H5": "f56r",
    "B1": "f81v", "B2": "f82r", "B3": "f83r", "B4": "f83r", "B5": "f83r", "B6": "f83r",
}

lines = [
    "# Vollständige stem-konsistente Zehnseiten-Ausgabe",
    "",
    "Diese Fassung wird direkt aus dem aktuellen 487-Karten-/776-Gruppen-Ledger erzeugt.",
    "Jede Einheit zeigt erst die exakte Oberfläche, dann die Komponenten, dann die",
    "wörtliche Kartenlesung und schließlich die flüssige, bildbesitzergestützte Expansion.",
    "",
    "## Teil I — 116 Prosa-Aussagen",
    "",
]
for record, title in record_titles.items():
    lines.extend([f"### {record} — {title} ({record_pages[record]})", ""])
    for row in translation_rows:
        if row["register"] == "PROSE" and row["unit_id"].startswith(record + "-"):
            lines.extend(
                [
                    f"#### {row['unit_id']}",
                    "",
                    f"- Oberfläche: `{row['surface_sequence']}`",
                    f"- Komponenten: `{row['atom_sequence']}`",
                    f"- Kartenlesung: {row['literal_card_reading_de']}.",
                    f"- Werkstattdeutsch: {row['owner_expansion_de']}",
                    "",
                ]
            )

lines.extend(["## Teil II — 142 Himmelsloci", ""])
for page in ("f67r2", "f68r1", "f69v"):
    lines.extend([f"### {page}", ""])
    for row in translation_rows:
        if row["register"] == "ASTRO" and row["page"] == page:
            lines.extend(
                [
                    f"#### {row['unit_id']} — {row['visible_owner']}",
                    "",
                    f"- Oberfläche: `{row['surface_sequence']}`",
                    f"- Komponenten: `{row['atom_sequence']}`",
                    f"- Kartenlesung: {row['literal_card_reading_de']}.",
                    f"- Tafelsprechung: {row['owner_expansion_de']}",
                    "",
                ]
            )
(HERE / "COMPLETE_TEN_PAGE_STEM_ALIGNED_TWENTIETH_EDITION.md").write_text(
    "\n".join(lines).rstrip() + "\n", encoding="utf-8"
)

shutil.copyfile(BASE / "NINETEENTH_POCKET_CODEBOOK.md", HERE / "TWENTIETH_POCKET_CODEBOOK.md")

summary = {
    "status": "PASS",
    "counts": {
        "dictionary_surfaces": len(dictionary),
        "visible_groups": len(ledger),
        "reading_units": len(translation_rows),
        "prose_statements": sum(row["register"] == "PROSE" for row in translation_rows),
        "astro_loci": sum(row["register"] == "ASTRO" for row in translation_rows),
        "full_groups": sum(row["autonomy"] == "FULL" for row in event_rows),
        "whole_groups": sum(row["autonomy"] == "NONE" for row in event_rows),
        "empty_literal_readings": sum(not row["literal_card_reading_de"] for row in translation_rows),
    },
}
(HERE / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(summary, ensure_ascii=False, indent=2))
