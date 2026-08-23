#!/usr/bin/env python3
from pathlib import Path
from collections import Counter, defaultdict
import csv
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
FUSIONS = ROOT / "experiments/yolo/sidequest_semantic_clause_attachment/FUSION_UNITS.tsv"
CURRENT = ROOT / "experiments/yolo/sidequest_semantic_stem_aligned_twentieth_edition/TWENTIETH_116_PROSE_STATEMENTS.tsv"
OWNERS = ROOT / "experiments/yolo/sidequest_semantic_owner_filled_twenty_first_edition/TWENTY_FIRST_116_OWNER_FILLED_PROSE.tsv"


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path, fields, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


HEADS = {
    "OK": ("SET", "pone", "ansetzen"),
    "OL": ("CONTINUE", "continua", "fortsetzen"),
    "L": ("LEAD_OUT", "educ", "herausführen"),
    "CHD": ("TRANSFER", "transfer", "umsetzen"),
    "SHED": ("SETTLE", "dimitte stare", "absetzen lassen"),
    "CTH": ("READY", "ad statum para", "bereitstellen"),
    "CKH": ("PASSAGE", "per conductum duc", "durchführen"),
    "CHK": ("WARM", "calefac", "wärmen"),
    "SOLK": ("COLLECT", "collige", "auffangen"),
    "SH": ("HOLD", "tene", "halten"),
    "KCH": ("PROCESS", "opera", "bearbeiten"),
    "WASH": ("WASH", "lava", "waschen"),
    "OWNER_SUPPLIED_ACTION": ("OWNER_ACTION", "fac de imagine", "mit dem Bildbesitzer arbeiten"),
    "PARTITION": ("DIVIDE", "divide", "abteilen"),
    "CKHE": ("STRAIN", "cola", "seihen"),
    "P": ("LEAD_IN", "mitte in", "einführen"),
    "SK": ("POUR", "effunde", "ausgießen"),
    "ODY": ("WITHDRAW", "remove", "zurücknehmen"),
    "DAN": ("APPLY", "applica", "anwenden"),
    "CPH": ("STRAIN_AGAIN", "itera cola", "nachseihen"),
    "CFH": ("SQUEEZE", "exprime", "auswringen"),
    "AM": ("STORE", "serva ad locum", "am Ziel verwahren"),
}


def atoms(sequence):
    return {
        atom.strip()
        for group in sequence.split("|")
        for atom in group.split("+")
        if atom.strip() and atom.strip() not in {"NONE", "LOCAL_WHOLE"}
    }


def latin_clause(head, sequence, owner):
    present = atoms(sequence)
    words = [HEADS[head][1]]
    if "PREV" in present:
        words.append("de priore")
    if "HO" in present:
        words.append("materiam")
    if "CHEO" in present:
        words.append("extractum")
    if "TY" in present:
        words.append("partem")
    if "AIN" in present:
        words.append("portionem")
    if "AIIN" in present:
        words.append("ad mensuram")
    if "IIN" in present:
        words.append("ad gradum")
    if "AR" in present:
        words.append("ab fonte")
    if "AIR" in present:
        words.append("per cursum")
    if "AL" in present:
        words.append("ad locum")
    if "OR" in present:
        words.append("in praeparato")
    if "E" in present:
        words.append("breviter")
    if "EE" in present:
        words.append("diutius")
    if "EEE" in present:
        words.append("plene")
    if "Y" in present:
        words.append("hoc")
    if "CLOSE" in present:
        words.append("et comple")
    if head == "OWNER_SUPPLIED_ACTION":
        words.append(owner)
    return " ".join(words) + "."


fusions = read(FUSIONS)
current = {row["unit_id"]: row for row in read(CURRENT)}
owners = {row["statement_id"]: row for row in read(OWNERS)}

clause_rows = []
for serial, source in enumerate(fusions, 1):
    statement_id = source["statement_id"]
    owner = owners[statement_id]["image_owner"]
    family, _, short = HEADS[source["action_head"]]
    member_ids = [source["host_event_id"]]
    for field in ("pre_attached_event_ids", "post_attached_event_ids"):
        member_ids.extend(item for item in source[field].split("|") if item and item != "NONE")
    clause_rows.append(
        {
            "clause_serial": serial,
            "clause_id": source["fusion_unit_id"],
            "statement_id": statement_id,
            "record_id": source["record_unit_id"],
            "page": source["page"],
            "image_owner": owner,
            "head_event_id": source["host_event_id"],
            "member_event_ids": "|".join(member_ids),
            "member_event_count": source["member_event_count"],
            "surface_sequence": source["surface_sequence"],
            "atom_sequence": source["atom_sequence"],
            "action_head": source["action_head"],
            "source_clause_family": family,
            "short_head_de": short,
            "latin_like_source_clause": latin_clause(source["action_head"], source["atom_sequence"], owner),
            "german_clause_reading_de": source["fused_clause_de"],
        }
    )
write(HERE / "TWENTY_FIFTH_254_SOURCE_CLAUSES.tsv", list(clause_rows[0]), clause_rows)

by_statement = defaultdict(list)
for row in clause_rows:
    by_statement[row["statement_id"]].append(row)

statement_rows = []
for statement_id in current:
    source = current[statement_id]
    owner_row = owners[statement_id]
    clauses = by_statement[statement_id]
    reconstructed_surface = " ".join(row["surface_sequence"] for row in clauses)
    statement_rows.append(
        {
            "statement_id": statement_id,
            "record_id": owner_row["record_id"],
            "page": source["page"],
            "image_owner": owner_row["image_owner"],
            "clause_count": len(clauses),
            "group_count": source["group_count"],
            "clause_ids": "|".join(row["clause_id"] for row in clauses),
            "source_clause_chain": " ; ".join(row["source_clause_family"] for row in clauses),
            "latin_like_source_chain": " ".join(row["latin_like_source_clause"] for row in clauses),
            "surface_sequence": reconstructed_surface,
            "current_surface_sequence": source["surface_sequence"],
            "german_clause_chain_de": " / ".join(row["german_clause_reading_de"] for row in clauses),
            "continuous_owner_reading_de": owner_row["selected_concrete_reading_de"],
            "surface_chain_matches_current": "YES" if reconstructed_surface == source["surface_sequence"] else "NO",
        }
    )
write(HERE / "TWENTY_FIFTH_116_MULTI_CLAUSE_STATEMENTS.tsv", list(statement_rows[0]), statement_rows)

by_record = defaultdict(list)
for row in statement_rows:
    by_record[row["record_id"]].append(row)

doc = [
    "# Elf Records als Ketten kurzer Meisterklauseln",
    "",
    "Jede Aussage wird an ihren sichtbaren Handlungsköpfen geteilt. Eine lange",
    "Kartenfolge ist deshalb keine einzige überladene Formel, sondern eine Folge",
    "kurzer Werkstattbefehle. Der Bildbesitzer bleibt während der Kette aktiv, bis",
    "ein sichtbarer Besitzerwechsel ihn ersetzt.",
    "",
]
for record_id in ("H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"):
    doc.extend([f"## {record_id}", ""])
    for row in by_record[record_id]:
        doc.extend(
            [
                f"### {row['statement_id']} — {row['clause_count']} Klauseln",
                "",
                f"Meisterfolge: *{row['latin_like_source_chain']}*",
                "",
                f"Karten: `{row['surface_sequence']}`",
                "",
                f"Werkstattdeutsch: {row['german_clause_chain_de']}",
                "",
                f"Mit Bildbesitzer: {row['continuous_owner_reading_de']}",
                "",
            ]
        )
(HERE / "TWENTY_FIFTH_ELEVEN_CLAUSE_RECORDS.md").write_text("\n".join(doc).rstrip() + "\n", encoding="utf-8")

head_counts = Counter(row["source_clause_family"] for row in clause_rows)
clause_count_dist = Counter(int(row["clause_count"]) for row in statement_rows)
summary = {
    "status": "PASS",
    "counts": {
        "clauses": len(clause_rows),
        "statements": len(statement_rows),
        "records": len(by_record),
        "groups": sum(int(row["group_count"]) for row in statement_rows),
        "head_families": len(head_counts),
        "multi_clause_statements": sum(int(row["clause_count"]) > 1 for row in statement_rows),
        "max_clauses_per_statement": max(int(row["clause_count"]) for row in statement_rows),
    },
    "head_family_counts": dict(sorted(head_counts.items())),
    "clause_count_distribution": {str(key): value for key, value in sorted(clause_count_dist.items())},
}
(HERE / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(summary, ensure_ascii=False, indent=2))
