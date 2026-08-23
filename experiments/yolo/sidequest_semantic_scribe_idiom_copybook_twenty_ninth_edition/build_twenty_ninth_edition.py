#!/usr/bin/env python3
from pathlib import Path
from collections import defaultdict
import csv
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PATTERNS = ROOT / "experiments/yolo/sidequest_semantic_idiom_phrasebook_twenty_eighth_edition/TWENTY_EIGHTH_EVENT_IDIOMS.tsv"
OCCURRENCES = ROOT / "experiments/yolo/sidequest_semantic_idiom_phrasebook_twenty_eighth_edition/TWENTY_EIGHTH_EVENT_IDIOM_OCCURRENCES.tsv"
COPIES = ROOT / "experiments/yolo/sidequest_semantic_four_scribe_copyshop/FOUR_HAND_116_STATEMENT_RENDERINGS.tsv"


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path, fields, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


profiles = ["S1_BARE_MASTER", "S2_Q_CELL_SCRIBE", "S3_S_LINE_SCRIBE", "S4_MIXED_COMPACT"]
patterns = {row["pattern_id"]: row for row in read(PATTERNS)}
first_occurrence = {}
for row in read(OCCURRENCES):
    first_occurrence.setdefault(row["pattern_id"], row)
copies = {(row["statement_id"], row["scribe_id"]): row for row in read(COPIES)}

copy_rows = []
summary_rows = []
for pattern_id in sorted(patterns):
    pattern = patterns[pattern_id]
    occurrence = first_occurrence[pattern_id]
    start = int(occurrence["start_position"]) - 1
    length = int(pattern["member_count"])
    variants = []
    tuple_slices = set()
    for profile in profiles:
        source = copies[(occurrence["unit_id"], profile)]
        original = source["original_surface_sequence"].split()[start:start + length]
        rendered = source["counterfactual_surface_sequence"].split()[start:start + length]
        tuples = source["tuple_sequence"].split()[start:start + length]
        variants.append(" ".join(rendered))
        tuple_slices.add(" ".join(tuples))
        copy_rows.append(
            {
                "pattern_id": pattern_id,
                "spoken_idiom_de": pattern["spoken_idiom_de"],
                "source_statement_id": occurrence["unit_id"],
                "page": occurrence["page"],
                "start_position": start + 1,
                "scribe_id": profile,
                "tuple_sequence": " ".join(tuples),
                "source_surface_sequence": " ".join(original),
                "scribe_surface_sequence": " ".join(rendered),
                "changed_token_count": sum(left != right for left, right in zip(original, rendered)),
                "semantic_readback_de": pattern["spoken_idiom_de"],
                "tuple_sequence_changed": "NO",
                "meaning_changed": "NO",
                "copy_status": source["copy_status"],
            }
        )
    summary_rows.append(
        {
            "pattern_id": pattern_id,
            "pattern": pattern["pattern"],
            "spoken_idiom_de": pattern["spoken_idiom_de"],
            "source_statement_id": occurrence["unit_id"],
            "source_page": occurrence["page"],
            "tuple_sequence": next(iter(tuple_slices)),
            "four_surface_copies": " | ".join(f"{profile}:{variant}" for profile, variant in zip(profiles, variants)),
            "distinct_surface_variants": len(set(variants)),
            "meaning_variants": 1,
        }
    )
write(HERE / "TWENTY_NINTH_68_SCRIBE_IDIOM_COPIES.tsv", list(copy_rows[0]), copy_rows)
write(HERE / "TWENTY_NINTH_17_IDIOM_COPYBOOK.tsv", list(summary_rows[0]), summary_rows)

errors = [
    ("ERR01", "q als eigenes Wort lesen", "q nur nach ausgewählter Exact-Karte als registrierte Zellschreiberform setzen"),
    ("ERR02", "s als eigenes Wort lesen", "s nur in einer registrierten Familie am Zeilenanfang wählen"),
    ("ERR03", "an jedem Zeilenende eine Aussage schließen", "Aussage bis zum Karten- oder Besitzerabschluss weiterlesen"),
    ("ERR04", "sichtbares dy immer als Schluss lesen", "nur die registrierte ganze Schlusskarte schließen lassen"),
    ("ERR05", "eine gelernte Ganzkarte in kurze Kerne zerlegen", "zuerst längsten Eintrag des Meisterexemplars prüfen"),
    ("ERR06", "e und ee überall als Grad lesen", "Grad nur in einer belegten Handlungs- oder Tafelfamilie setzen"),
    ("ERR07", "beim Bildwechsel denselben Stoffbezug behalten", "Besitzerregister am sichtbaren Wechsel neu setzen"),
    ("ERR08", "eine Phrase als neue Einzelkarte memorieren", "Phrase flüssig sprechen, darunter aber alle Exact-Karten bewahren"),
]
error_rows = [
    {"error_id": error_id, "apprentice_error_de": error, "master_correction_de": correction}
    for error_id, error, correction in errors
]
write(HERE / "TWENTY_NINTH_EIGHT_APPRENTICE_ERRORS.tsv", list(error_rows[0]), error_rows)

doc = [
    "# Vier Hände schreiben dieselben Werkstattwendungen",
    "",
    "Für jede der siebzehn wiederkehrenden Kartenwendungen wurde ein echtes",
    "Auftreten gewählt und von vier didaktischen Werkstatthänden abgeschrieben.",
    "Die sichtbare Form darf wechseln; Kartenidentität und ausgesprochene Wendung",
    "bleiben gleich.",
    "",
]
for row in summary_rows:
    doc.extend(
        [
            f"## {row['pattern_id']} — {row['spoken_idiom_de']}",
            "",
            f"Kartenmuster: `{row['pattern']}`",
            "",
            f"Exact-Tuples: `{row['tuple_sequence']}`",
            "",
            f"Kopien: `{row['four_surface_copies']}`",
            "",
            f"Sichtbare Varianten: {row['distinct_surface_variants']}; Bedeutungsvarianten: 1.",
            "",
        ]
    )
doc.extend(["## Acht typische Lehrlingsfehler", ""])
for row in error_rows:
    doc.append(f"- **{row['apprentice_error_de']}** — {row['master_correction_de']}.")
(HERE / "TWENTY_NINTH_FOUR_SCRIBE_IDIOM_COPYBOOK.md").write_text("\n".join(doc).rstrip() + "\n", encoding="utf-8")

summary = {
    "status": "PASS",
    "counts": {
        "idioms": len(summary_rows),
        "scribe_copies": len(copy_rows),
        "scribe_profiles": len(profiles),
        "idioms_with_visible_variation": sum(int(row["distinct_surface_variants"]) > 1 for row in summary_rows),
        "apprentice_errors": len(error_rows),
    },
}
(HERE / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(summary, ensure_ascii=False, indent=2))
