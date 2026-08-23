#!/usr/bin/env python3
from pathlib import Path
import csv
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
IDIOMS = ROOT / "experiments/yolo/sidequest_semantic_scribe_idiom_copybook_twenty_ninth_edition/TWENTY_NINTH_17_IDIOM_COPYBOOK.tsv"
COPIES = ROOT / "experiments/yolo/sidequest_semantic_scribe_idiom_copybook_twenty_ninth_edition/TWENTY_NINTH_68_SCRIBE_IDIOM_COPIES.tsv"
STATEMENTS = ROOT / "experiments/yolo/sidequest_semantic_four_scribe_copyshop/FOUR_HAND_116_STATEMENT_RENDERINGS.tsv"


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path, fields, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


EXERCISES = [
    ("X17", "PICTURED_PLANT_BATCH", ["E03", "E12", "E16"], "Diesen Pflanzenansatz auf Sollmaß setzen und danach im selben Gang weiterführen."),
    ("X18", "VISIBLE_BASIN_TARGET", ["E17", "E09"], "Die aktuelle Charge zum Ziel bringen, umsetzen, länger ansetzen und schließen."),
    ("X19", "CLOTH_OR_INSERT_TARGET", ["E14", "E10"], "Die nächste Portion zum Ziel bringen, länger halten, kurz nachsetzen und schließen."),
    ("X20", "CURRENT_PREPARATION", ["E03", "E07", "E04"], "Diesen Ansatz mit demselben Sollmaß fortführen, kurz absetzen und schließen."),
    ("X21", "LOCAL_STATION", ["E08", "E04"], "Am Ziel weiterarbeiten, dann kurz absetzen und schließen."),
    ("X22", "CONTINUATION_BATCH", ["E15", "E07"], "Den Fortsetzungsansatz weiterführen und beim selben Sollmaß bleiben."),
    ("X23", "MEASURED_WORK_ITEM", ["E06", "E17"], "Denselben Posten um das Sollmaß führen und zum Ziel bringen."),
    ("X24", "HELD_WORK_ITEM", ["E11", "E09"], "Den länger gehaltenen Posten weiter ansetzen, umsetzen und geschlossen fertigstellen."),
    ("X25", "TARGET_MEASURE", ["E02", "E08"], "Das Sollmaß dieses Postens nehmen und am Ziel weiterarbeiten."),
    ("X26", "TRANSFER_RUN", ["E05", "E04"], "Den Posten umsetzen, weiterführen, kurz absetzen und schließen."),
    ("X27", "MEASURED_TARGET_PORTION", ["E12", "E14"], "Den aktuellen Posten auf Sollmaß setzen und die nächste Portion zum Ziel bringen."),
    ("X28", "FOLLOWING_CLOSED_TRANSFER", ["E16", "E09"], "Danach im selben Gang weiter, umsetzen, länger ansetzen und schließen."),
]

profiles = ["S1_BARE_MASTER", "S2_Q_CELL_SCRIBE", "S3_S_LINE_SCRIBE", "S4_MIXED_COMPACT"]
idioms = {row["pattern_id"]: row for row in read(IDIOMS)}
copies = {(row["pattern_id"], row["scribe_id"]): row for row in read(COPIES)}
existing_tuple_sequences = [
    row["tuple_sequence"]
    for row in read(STATEMENTS)
    if row["scribe_id"] == "S1_BARE_MASTER"
]

exercise_rows = []
copy_rows = []
for exercise_id, owner, pattern_ids, dictation in EXERCISES:
    tuple_sequence = " ".join(idioms[pattern_id]["tuple_sequence"] for pattern_id in pattern_ids)
    atom_pattern = " | ".join(idioms[pattern_id]["pattern"] for pattern_id in pattern_ids)
    spoken_chain = " ; ".join(idioms[pattern_id]["spoken_idiom_de"] for pattern_id in pattern_ids)
    found_contiguous = any(
        f" {tuple_sequence} " in f" {existing} "
        for existing in existing_tuple_sequences
    )
    variants = []
    for profile in profiles:
        surfaces = " ".join(copies[(pattern_id, profile)]["scribe_surface_sequence"] for pattern_id in pattern_ids)
        variants.append(surfaces)
        copy_rows.append(
            {
                "exercise_id": exercise_id,
                "silent_owner": owner,
                "master_dictation_de": dictation,
                "idiom_ids": "|".join(pattern_ids),
                "scribe_id": profile,
                "tuple_sequence": tuple_sequence,
                "atom_pattern_chain": atom_pattern,
                "scribe_surface_sequence": surfaces,
                "semantic_readback_de": spoken_chain,
                "uses_only_registered_idiom_cards": "YES",
                "tuple_sequence_changed": "NO",
                "meaning_changed": "NO",
                "new_manuscript_claim": "NO_APPRENTICE_EXERCISE",
            }
        )
    exercise_rows.append(
        {
            "exercise_id": exercise_id,
            "silent_owner": owner,
            "master_dictation_de": dictation,
            "idiom_ids": "|".join(pattern_ids),
            "idiom_count": len(pattern_ids),
            "tuple_count": len(tuple_sequence.split()),
            "tuple_sequence": tuple_sequence,
            "atom_pattern_chain": atom_pattern,
            "spoken_idiom_chain_de": spoken_chain,
            "four_surface_copies": " | ".join(f"{profile}:{variant}" for profile, variant in zip(profiles, variants)),
            "distinct_surface_variants": len(set(variants)),
            "occurs_contiguously_in_current_statement": "YES" if found_contiguous else "NO",
        }
    )
write(HERE / "THIRTIETH_12_NEW_DICTATIONS.tsv", list(exercise_rows[0]), exercise_rows)
write(HERE / "THIRTIETH_48_SCRIBE_COPIES.tsv", list(copy_rows[0]), copy_rows)

doc = [
    "# Zwölf neue Diktate aus dem vorhandenen Phrasekasten",
    "",
    "Diese Folgen stehen nicht im festen Zehnseiten-Text. Sie sind Übungen, die ein",
    "Meister mit den bereits vorhandenen Karten und Wendungen diktieren könnte.",
    "Der stille Besitzer wird gezeigt; geschrieben werden nur die bekannten",
    "Kartenfolgen. Vier Hände dürfen unterschiedliche registrierte Oberflächen wählen.",
    "",
]
for row in exercise_rows:
    doc.extend(
        [
            f"## {row['exercise_id']} — {row['silent_owner']}",
            "",
            row["master_dictation_de"],
            "",
            f"Wendungen: `{row['idiom_ids']}` — {row['spoken_idiom_chain_de']}",
            "",
            f"Kerne: `{row['atom_pattern_chain']}`",
            "",
            f"Vier Kopien: `{row['four_surface_copies']}`",
            "",
            f"Als ganze Tuplefolge bereits im Text: **{row['occurs_contiguously_in_current_statement']}**.",
            "",
        ]
    )
(HERE / "THIRTIETH_APPRENTICE_DICTATION_BOOK.md").write_text("\n".join(doc).rstrip() + "\n", encoding="utf-8")

summary = {
    "status": "PASS",
    "counts": {
        "new_dictations": len(exercise_rows),
        "scribe_copies": len(copy_rows),
        "scribe_profiles": len(profiles),
        "dictations_absent_as_contiguous_tuple_sequence": sum(row["occurs_contiguously_in_current_statement"] == "NO" for row in exercise_rows),
        "dictations_with_surface_variation": sum(int(row["distinct_surface_variants"]) > 1 for row in exercise_rows),
    },
}
(HERE / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(summary, ensure_ascii=False, indent=2))
