#!/usr/bin/env python3
from pathlib import Path
from collections import defaultdict, Counter
import csv
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = ROOT / "experiments/yolo/sidequest_semantic_stem_aligned_twentieth_edition"
HERBAL = ROOT / "experiments/yolo/sidequest_theory_candidates_v73/V73_SELECTED_20_FIELD_EDITION.tsv"
BIO = ROOT / "experiments/yolo/sidequest_theory_candidates_v74/V74_SELECTED_97_STATEMENT_EDITION.tsv"


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path, fields, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


prose = read(BASE / "TWENTIETH_116_PROSE_STATEMENTS.tsv")
astro = read(BASE / "TWENTIETH_142_ASTRO_LOCI.tsv")
herbal_fields = read(HERBAL)
bio_statements = read(BIO)

herbal_by_statement = defaultdict(list)
for row in herbal_fields:
    herbal_by_statement[row["statement_id"]].append(row)
bio_by_statement = {row["statement_id"]: row for row in bio_statements}

owner_rows = []
for row in prose:
    statement = row["unit_id"]
    if statement.startswith("H"):
        fields = herbal_by_statement[statement]
        owners = list(dict.fromkeys(field["whole_plant_owner"] for field in fields))
        concrete = " ".join(field["third_edition_field_text"] for field in fields)
        alternative = (
            "Pflanzenmaterial-/Probenregister: dieselbe sichtbare Pflanze und dieselben "
            "Arbeitsgänge, aber ohne vorausgesetzte Krankheit oder Arzneiwirkung."
        )
        owner_break = "NO"
        image_owner = " | ".join(owners)
        owner_kind = "VISIBLE_WHOLE_PLANT"
    else:
        selected = bio_by_statement[statement]
        image_owner = selected["local_owner_sequence"]
        owner_kind = "VISIBLE_BASIN_FIGURE_OR_LOCAL_STATION"
        owner_break = selected["contains_visible_owner_break"]
        concrete = selected["balneological_statement_text"]
        alternative = selected["strongest_rival"]
    owner_rows.append(
        {
            "unit_serial": row["unit_serial"],
            "record_id": statement.split("-", 1)[0],
            "page": row["page"],
            "statement_id": statement,
            "group_count": row["group_count"],
            "surface_sequence": row["surface_sequence"],
            "atom_sequence": row["atom_sequence"],
            "literal_card_reading_de": row["literal_card_reading_de"],
            "image_owner": image_owner,
            "owner_kind": owner_kind,
            "owner_break_inside_statement": owner_break,
            "selected_concrete_reading_de": concrete,
            "short_rival_de": alternative,
        }
    )

write(HERE / "TWENTY_FIRST_116_OWNER_FILLED_PROSE.tsv", list(owner_rows[0]), owner_rows)

record_titles = {
    "H1": "Wurzelansatz", "H2": "Fortgesetzter Pflanzenansatz",
    "H3": "Auswringen und Nachseihen", "H4": "Verwahrter Auszug",
    "H5": "Frische Pflanzenfolge", "B1": "Gemeinsamer Beckenweg",
    "B2": "Stations- und Durchlaufweg", "B3": "Hauptfolge der Anwendungen",
    "B4": "Tuch-, Halte- und Nachwaschfolge", "B5": "Kurzer Seitenweg",
    "B6": "Abschlussweg",
}

lines = [
    "# Elf bildbesitzergestützte Prosa-Records",
    "",
    "Die Kartenlesung bleibt stem-konsistent. Die konkrete Fassung setzt den sichtbaren",
    "Pflanzen-, Becken-, Figuren- oder Stationsbesitzer als stilles Subjekt/Objekt ein.",
    "",
]
for record, title in record_titles.items():
    page = next(row["page"] for row in owner_rows if row["record_id"] == record)
    lines.extend([f"## {record} — {title} ({page})", ""])
    record_rows = [row for row in owner_rows if row["record_id"] == record]
    lines.append(f"Bildbesitzer: **{record_rows[0]['image_owner']}**.")
    lines.append("")
    for row in record_rows:
        lines.extend(
            [
                f"### {row['statement_id']}",
                "",
                f"- Oberfläche: `{row['surface_sequence']}`",
                f"- Komponenten: `{row['atom_sequence']}`",
                f"- Kartenlesung: {row['literal_card_reading_de']}.",
                f"- Konkrete Bildfassung: {row['selected_concrete_reading_de']}",
                f"- Technischer Rivale: {row['short_rival_de']}",
                "",
            ]
        )
(HERE / "ELEVEN_OWNER_FILLED_PROSE_RECORDS.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

complete = [
    "# Vollständige bildbesitzergestützte Zehnseiten-Ausgabe",
    "",
    "## Teil I — Prosa mit sichtbarem Besitzer",
    "",
]
for row in owner_rows:
    complete.extend(
        [
            f"### {row['statement_id']} — {row['image_owner']}",
            "",
            f"- `{row['surface_sequence']}`",
            f"- Karten: {row['literal_card_reading_de']}.",
            f"- Bildfassung: {row['selected_concrete_reading_de']}",
            "",
        ]
    )
complete.extend(["## Teil II — Himmelsloci", ""])
for row in astro:
    complete.extend(
        [
            f"### {row['unit_id']} — {row['visible_owner']}",
            "",
            f"- `{row['surface_sequence']}`",
            f"- Komponenten: `{row['atom_sequence']}`",
            f"- Tafelsprechung: {row['owner_expansion_de']}",
            "",
        ]
    )
(HERE / "COMPLETE_TEN_PAGE_OWNER_FILLED_TWENTY_FIRST_EDITION.md").write_text(
    "\n".join(complete).rstrip() + "\n", encoding="utf-8"
)

owner_counts = Counter(row["image_owner"] for row in owner_rows)
write(
    HERE / "OWNER_USAGE_SUMMARY.tsv",
    ["image_owner", "statements"],
    [{"image_owner": owner, "statements": count} for owner, count in sorted(owner_counts.items())],
)

summary = {
    "status": "PASS",
    "counts": {
        "prose_statements": len(owner_rows),
        "herbal_statements": sum(row["record_id"].startswith("H") for row in owner_rows),
        "bio_statements": sum(row["record_id"].startswith("B") for row in owner_rows),
        "astro_loci": len(astro),
        "prose_group_sum": sum(int(row["group_count"]) for row in owner_rows),
        "distinct_owner_strings": len(owner_counts),
        "owner_break_statements": sum(row["owner_break_inside_statement"] == "YES" for row in owner_rows),
    },
}
(HERE / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(summary, ensure_ascii=False, indent=2))
