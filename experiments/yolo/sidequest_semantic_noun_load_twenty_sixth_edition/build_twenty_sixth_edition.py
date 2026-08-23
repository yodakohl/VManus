#!/usr/bin/env python3
from pathlib import Path
from collections import Counter, defaultdict
import csv
import json
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OWNERS = ROOT / "experiments/yolo/sidequest_semantic_owner_filled_twenty_first_edition/TWENTY_FIRST_116_OWNER_FILLED_PROSE.tsv"
CLAUSES = ROOT / "experiments/yolo/sidequest_semantic_clause_chain_twenty_fifth_edition/TWENTY_FIFTH_116_MULTI_CLAUSE_STATEMENTS.tsv"


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path, fields, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


RISK_GROUPS = {
    "EXACT_MEDIUM": ["Quellwasser", "Weißwein", "Wein", "Olivenöl", "Öl", "Honig", "Milch", "Essig"],
    "EXACT_VESSEL_OR_TOOL": ["Glas", "glasiertes Gefäß", "Leinwand", "Wolltuch", "Wolle", "Kessel"],
    "DISEASE_OR_BODY_TARGET": ["Stechen im Leib", "Leib", "Geschwür", "Schwellung", "Gemüt", "Brust", "Lider", "Auge", "Wunde", "Warze", "Hühnerauge", "Husten", "Hautstelle"],
    "MEDICAL_PRODUCT_OR_USE": ["innerlich", "äußerlich", "Trank", "Salbe", "Arznei", "Umschlag", "Auflage", "Teilbad", "Badende"],
    "EXACT_TIME_OR_HABITAT": ["Frühjahr", "vor voller Blüte", "Beginn der Blüte", "feuchten Standort", "im Schatten", "über Nacht", "Tage"],
    "EXACT_PLANT_PART": ["junge Spitzen", "Blütenstände", "Blüten", "junge Blätter", "breite Blätter", "blühenden Stiele", "klebrigen Blätter"],
}


def owner_phrase(row):
    if row["owner_kind"] == "VISIBLE_WHOLE_PLANT":
        return "an der abgebildeten Pflanze"
    owner = row["image_owner"]
    if "|" in owner:
        return "über den sichtbaren Besitzerwechsel hinweg"
    if any(word in owner for word in ("POOL", "BASIN", "BECKEN")):
        return "am sichtbaren Becken"
    if "PAIR" in owner or "FIGURE" in owner:
        return "bei der sichtbaren Figurengruppe"
    if "GAP" in owner or "UNRESOLVED" in owner:
        return "im unklaren Zwischenbereich"
    if "DEVICE" in owner or "NODE" in owner:
        return "am sichtbaren Gerät oder Knoten"
    return "an der sichtbaren lokalen Station"


owners = {row["statement_id"]: row for row in read(OWNERS)}
clauses = read(CLAUSES)
rows = []
for source in clauses:
    owner = owners[source["statement_id"]]
    original = owner["selected_concrete_reading_de"]
    flags = []
    terms = []
    for group, candidates in RISK_GROUPS.items():
        hits = [term for term in candidates if re.search(rf"(?<!\w){re.escape(term)}(?!\w)", original, flags=re.IGNORECASE)]
        if hits:
            flags.append(group)
            terms.extend(f"{group}:{term}" for term in hits)
    phrase = owner_phrase(owner)
    lean = f"{phrase[0].upper() + phrase[1:]}: {source['german_clause_chain_de']}"
    rows.append(
        {
            "statement_id": source["statement_id"],
            "record_id": source["record_id"],
            "page": source["page"],
            "image_owner": owner["image_owner"],
            "owner_support": owner_phrase(owner),
            "group_count": source["group_count"],
            "clause_count": source["clause_count"],
            "surface_sequence": source["surface_sequence"],
            "literal_card_reading_de": owner["literal_card_reading_de"],
            "original_concrete_reading_de": original,
            "creative_detail_categories": "|".join(flags) if flags else "NONE",
            "creative_detail_terms": "|".join(terms) if terms else "NONE",
            "creative_detail_category_count": len(flags),
            "lean_owner_clause_reading_de": lean,
        }
    )
write(HERE / "TWENTY_SIXTH_116_NOUN_LOAD_AUDIT.tsv", list(rows[0]), rows)

by_record = defaultdict(list)
for row in rows:
    by_record[row["record_id"]].append(row)

record_rows = []
for record_id in ("H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"):
    members = by_record[record_id]
    flags = Counter(
        flag
        for row in members
        for flag in row["creative_detail_categories"].split("|")
        if flag != "NONE"
    )
    record_rows.append(
        {
            "record_id": record_id,
            "page": members[0]["page"],
            "statement_count": len(members),
            "group_count": sum(int(row["group_count"]) for row in members),
            "statements_with_creative_detail": sum(row["creative_detail_categories"] != "NONE" for row in members),
            "creative_category_hits": sum(flags.values()),
            "creative_category_counts": "|".join(f"{key}:{flags[key]}" for key in sorted(flags)) if flags else "NONE",
            "lean_record_reading_de": " ".join(row["lean_owner_clause_reading_de"] for row in members),
        }
    )
write(HERE / "TWENTY_SIXTH_ELEVEN_LEAN_RECORDS.tsv", list(record_rows[0]), record_rows)

doc = [
    "# Magere, aber vollständige Zehnseiten-Prosa",
    "",
    "Diese Ausgabe nimmt keiner Karte ihre Arbeitsbedeutung. Sie entfernt nur",
    "konkrete Nomen, die weder Karte noch sichtbarer Besitzer erzwingen. Pflanzen",
    "bleiben Pflanzen, Becken bleiben Becken und alle Handlungsklauseln bleiben",
    "erhalten; Wein, Öl, Honig, Krankheiten und genaue Körperstellen erscheinen nur",
    "in der reicheren kreativen Lesung daneben.",
    "",
]
for record in record_rows:
    doc.extend(
        [
            f"## {record['record_id']} ({record['page']})",
            "",
            record["lean_record_reading_de"],
            "",
            f"Kreative Detailkategorien in der reichen Fassung: `{record['creative_category_counts']}`.",
            "",
        ]
    )
(HERE / "TWENTY_SIXTH_LEAN_ELEVEN_RECORD_EDITION.md").write_text("\n".join(doc).rstrip() + "\n", encoding="utf-8")

category_counts = Counter(
    flag
    for row in rows
    for flag in row["creative_detail_categories"].split("|")
    if flag != "NONE"
)
summary = {
    "status": "PASS",
    "counts": {
        "statements": len(rows),
        "records": len(record_rows),
        "groups": sum(int(row["group_count"]) for row in rows),
        "statements_with_flagged_creative_detail": sum(row["creative_detail_categories"] != "NONE" for row in rows),
        "statements_without_flagged_creative_detail": sum(row["creative_detail_categories"] == "NONE" for row in rows),
        "creative_detail_categories": len(category_counts),
    },
    "creative_category_statement_hits": dict(sorted(category_counts.items())),
}
(HERE / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(summary, ensure_ascii=False, indent=2))
