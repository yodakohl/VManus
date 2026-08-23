#!/usr/bin/env python3
from pathlib import Path
from collections import defaultdict
import csv
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_final_productive_cards_nineteenth_edition/NINETEENTH_776_SPEAKABLE_LEDGER.tsv"
CLAUSES = ROOT / "experiments/yolo/sidequest_semantic_clause_chain_twenty_fifth_edition/TWENTY_FIFTH_254_SOURCE_CLAUSES.tsv"


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path, fields, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


EVENT_IDIOMS = {
    ("Y", "AIIN"): "diesen Posten nach Sollmaß nehmen",
    ("AIIN", "Y"): "Sollmaß dieses Postens",
    ("OR", "Y"): "dieser laufende Ansatz",
    ("OL", "SHED+E+CLOSE"): "weiterführen, kurz absetzen und schließen",
    ("CHD+Y", "OL"): "den Posten umsetzen und weiterführen",
    ("Y", "AIIN", "Y"): "denselben Posten um das Sollmaß führen",
    ("AIIN", "OL"): "mit demselben Sollmaß fortfahren",
    ("AL", "OL"): "am Ziel weiterarbeiten",
    ("CHD+Y", "OK+EE+CLOSE"): "umsetzen, länger ansetzen und schließen",
    ("OK+EE+Y", "OK+E+CLOSE"): "länger halten, kurz nachsetzen und schließen",
    ("OK+EE+Y", "OK+Y"): "den länger gehaltenen Posten weiter ansetzen",
    ("OK+Y", "AIIN"): "den aktuellen Posten auf Sollmaß setzen",
    ("OL", "AIIN"): "fortsetzen und auf Sollmaß stellen",
    ("OL+AIN", "AL"): "die nächste Portion zum Ziel bringen",
    ("OL+OR", "OL"): "den Fortsetzungsansatz weiterführen",
    ("OT+OL", "OL"): "danach im selben Gang weiter",
    ("Y", "AL"): "den aktuellen Posten zum Ziel bringen",
}

CLAUSE_IDIOMS = {
    ("SET", "SET"): "zwei Einstellungen nacheinander ausführen",
    ("SET", "CONTINUE"): "ansetzen und weiterführen",
    ("CONTINUE", "CONTINUE"): "im selben Gang weiterarbeiten",
    ("SET", "PASSAGE"): "ansetzen und durchleiten",
    ("SET", "READY"): "ansetzen und bereit halten",
    ("TRANSFER", "CONTINUE"): "umsetzen und weiterführen",
    ("CONTINUE", "LEAD_OUT"): "weiterführen und abführen",
    ("CONTINUE", "SET"): "weiterführen und neu ansetzen",
    ("SET", "SETTLE"): "ansetzen und absetzen lassen",
    ("TRANSFER", "SET"): "umsetzen und neu ansetzen",
    ("CONTINUE", "SETTLE"): "weiterführen und absetzen lassen",
    ("PASSAGE", "SET"): "durchleiten und ansetzen",
    ("SET", "TRANSFER"): "ansetzen und umsetzen",
    ("LEAD_OUT", "SET"): "abführen und neu ansetzen",
    ("READY", "READY"): "den Bereitschaftszustand bestätigen",
    ("READY", "SET"): "bereitstellen und ansetzen",
    ("WARM", "CONTINUE"): "wärmen und weiterführen",
}


def occurrences(units, key_field, surface_field, patterns, prefix):
    pattern_rows = []
    occurrence_rows = []
    for number, (pattern, phrase) in enumerate(patterns.items(), 1):
        pattern_id = f"{prefix}{number:02d}"
        hits = []
        records = set()
        for unit_id, members in units.items():
            sequence = [row[key_field] for row in members]
            for start in range(len(sequence) - len(pattern) + 1):
                if tuple(sequence[start:start + len(pattern)]) != pattern:
                    continue
                selected = members[start:start + len(pattern)]
                record_id = selected[0].get("record_id") or unit_id.split("-")[0]
                records.add(record_id)
                occurrence_id = f"{pattern_id}-{len(hits)+1:03d}"
                hits.append(occurrence_id)
                occurrence_rows.append(
                    {
                        "occurrence_id": occurrence_id,
                        "pattern_id": pattern_id,
                        "unit_id": unit_id,
                        "record_id": record_id,
                        "page": selected[0]["page"],
                        "start_position": start + 1,
                        "member_ids": "|".join(row.get("source_group_id") or row.get("clause_id") for row in selected),
                        "observed_sequence": " > ".join(sequence[start:start + len(pattern)]),
                        "surface_or_clause_sequence": " | ".join(row[surface_field] for row in selected),
                        "spoken_idiom_de": phrase,
                    }
                )
        pattern_rows.append(
            {
                "pattern_id": pattern_id,
                "level": "EVENT" if prefix == "E" else "CLAUSE",
                "member_count": len(pattern),
                "pattern": " > ".join(pattern),
                "spoken_idiom_de": phrase,
                "occurrence_count": len(hits),
                "record_count": len(records),
                "records": "|".join(sorted(records)),
            }
        )
    return pattern_rows, occurrence_rows


event_units = defaultdict(list)
for row in read(EVENTS):
    if row["register"] == "PROSE":
        event_units[row["reading_unit_id"]].append(row)

clause_units = defaultdict(list)
for row in read(CLAUSES):
    clause_units[row["statement_id"]].append(row)

event_patterns, event_occurrences = occurrences(
    event_units, "atom_sequence", "visible_surface", EVENT_IDIOMS, "E"
)
clause_patterns, clause_occurrences = occurrences(
    clause_units, "source_clause_family", "surface_sequence", CLAUSE_IDIOMS, "C"
)
write(HERE / "TWENTY_EIGHTH_EVENT_IDIOMS.tsv", list(event_patterns[0]), event_patterns)
write(HERE / "TWENTY_EIGHTH_EVENT_IDIOM_OCCURRENCES.tsv", list(event_occurrences[0]), event_occurrences)
write(HERE / "TWENTY_EIGHTH_CLAUSE_IDIOMS.tsv", list(clause_patterns[0]), clause_patterns)
write(HERE / "TWENTY_EIGHTH_CLAUSE_IDIOM_OCCURRENCES.tsv", list(clause_occurrences[0]), clause_occurrences)

event_by_unit = defaultdict(list)
for row in event_occurrences:
    event_by_unit[row["unit_id"]].append(row)
clause_by_unit = defaultdict(list)
for row in clause_occurrences:
    clause_by_unit[row["unit_id"]].append(row)

statement_rows = []
for unit_id in event_units:
    members = event_units[unit_id]
    event_hits = event_by_unit[unit_id]
    clause_hits = clause_by_unit[unit_id]
    covered_events = {
        event_id
        for row in event_hits
        for event_id in row["member_ids"].split("|")
    }
    statement_rows.append(
        {
            "statement_id": unit_id,
            "record_id": unit_id.split("-")[0],
            "page": members[0]["page"],
            "group_count": len(members),
            "event_idiom_occurrences": len(event_hits),
            "clause_idiom_occurrences": len(clause_hits),
            "event_idiom_ids": "|".join(row["occurrence_id"] for row in event_hits) if event_hits else "NONE",
            "clause_idiom_ids": "|".join(row["occurrence_id"] for row in clause_hits) if clause_hits else "NONE",
            "spoken_event_idioms_de": " / ".join(row["spoken_idiom_de"] for row in event_hits) if event_hits else "NONE",
            "spoken_clause_idioms_de": " / ".join(row["spoken_idiom_de"] for row in clause_hits) if clause_hits else "NONE",
            "unique_events_covered_by_idiom": len(covered_events),
            "residual_events": len(members) - len(covered_events),
            "surface_sequence": " ".join(row["visible_surface"] for row in members),
        }
    )
write(HERE / "TWENTY_EIGHTH_116_STATEMENT_IDIOM_INDEX.tsv", list(statement_rows[0]), statement_rows)

doc = [
    "# Redewendungsbuch der Zehnseiten-Werkstatt",
    "",
    "Ein Lehrling muss nicht jede Folge Wort für Wort aufsagen. Wiederkehrende",
    "Kartenpaare und Handlungspaare werden als kurze Werkstattwendungen gelernt.",
    "Sie ersetzen keine Kartenbedeutung; sie sind die natürliche Aussprache einer",
    "bereits wiederkehrenden Komposition.",
    "",
    "## Siebzehn Kartenwendungen",
    "",
]
for row in event_patterns:
    doc.append(f"- `{row['pattern']}` — **{row['spoken_idiom_de']}** ({row['occurrence_count']}× in {row['record_count']} Records).")
doc.extend(["", "## Siebzehn Handlungswendungen", ""])
for row in clause_patterns:
    doc.append(f"- `{row['pattern']}` — **{row['spoken_idiom_de']}** ({row['occurrence_count']}× in {row['record_count']} Records).")
doc.extend(
    [
        "",
        "## Sprechregel",
        "",
        "Lies zuerst die längste passende Wendung, aber lösche keine Karte. Wenn zwei",
        "Wendungen überlappen, dient die längere nur als flüssige Aussprache; die exakte",
        "Kartenfolge bleibt im darunterliegenden Wörterbuch erhalten. Besitzer, Material",
        "und Ziel werden anschließend aus Bild und laufendem Record ergänzt.",
    ]
)
(HERE / "TWENTY_EIGHTH_WORKSHOP_PHRASEBOOK.md").write_text("\n".join(doc).rstrip() + "\n", encoding="utf-8")

covered_event_ids = {
    event_id
    for row in event_occurrences
    for event_id in row["member_ids"].split("|")
}
covered_clause_ids = {
    clause_id
    for row in clause_occurrences
    for clause_id in row["member_ids"].split("|")
}
summary = {
    "status": "PASS",
    "counts": {
        "event_idioms": len(event_patterns),
        "event_idiom_occurrences": len(event_occurrences),
        "unique_events_covered": len(covered_event_ids),
        "clause_idioms": len(clause_patterns),
        "clause_idiom_occurrences": len(clause_occurrences),
        "unique_clauses_covered": len(covered_clause_ids),
        "statements": len(statement_rows),
        "statements_with_any_idiom": sum(
            bool(row["event_idiom_occurrences"] or row["clause_idiom_occurrences"])
            for row in statement_rows
        ),
    },
}
(HERE / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(summary, ensure_ascii=False, indent=2))
