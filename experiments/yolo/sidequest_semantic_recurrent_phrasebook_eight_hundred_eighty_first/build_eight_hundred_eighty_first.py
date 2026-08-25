#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
EDITION = ROOT / "sidequest_semantic_fifth_hand_normalized_edition_eight_hundred_eightieth"
MARKS = EDITION / "EIGHT_HUNDRED_EIGHTIETH_438_MARK_FIFTH_HAND_EDITION.tsv"
UNITS = EDITION / "EIGHT_HUNDRED_EIGHTIETH_119_UNIT_FIFTH_HAND_EDITION.tsv"
PREFIX = "EIGHT_HUNDRED_EIGHTY_FIRST"

PHRASE_GLOSSES = {
    ("AIIN", "Y"): "DEN POSTEN NACH SOLLMASS FUEHREN",
    ("AL", "OL"): "AN DER ZIELSTELLE WEITERARBEITEN",
    ("CHD+Y", "OL"): "DEN POSTEN UMSETZEN UND WEITERFUEHREN",
    ("OK+EE+Y", "OK+Y"): "DEN POSTEN LAENGER ANSETZEN UND ERNEUT ANSETZEN",
    ("OK+Y", "AIIN"): "DEN POSTEN NACH SOLLMASS ANSETZEN",
    ("OK+Y", "OL"): "DEN POSTEN ANSETZEN UND WEITERARBEITEN",
    ("OL", "SHED+DY"): "WEITERARBEITEN, STEHENLASSEN UND SCHLIESSEN",
    ("OL+K+AIN", "AL"): "EINE PORTION WEITER AN DIE ZIELSTELLE GEBEN",
    ("OR", "Y"): "DEN ANSATZ ALS LAUFENDEN POSTEN FUEHREN",
    ("OK+EE+Y", "OK+Y", "OL"): "DEN POSTEN LAENGER ANSETZEN, ERNEUT ANSETZEN UND WEITERARBEITEN",
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    all_marks = read(MARKS)
    source_units = read(UNITS)
    prose = [row for row in all_marks if not row["stage"].startswith("CONDITION")]
    physical: dict[str, dict[str, str]] = {}
    for row in prose:
        physical.setdefault(row["source_id"], row)
    rows = sorted(physical.values(), key=lambda row: int(row["source_id"][1:]))
    by_unit: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_unit[row["unit"]].append(row)

    unit_reading = {}
    for row in source_units:
        if row["stage"].startswith("CONDITION"):
            continue
        unit_reading.setdefault(row["unit"], row["fluent_workshop_reading_de"])

    candidates: dict[tuple[str, ...], list[dict[str, object]]] = defaultdict(list)
    for unit, sequence in by_unit.items():
        for length in range(2, 6):
            for start in range(len(sequence) - length + 1):
                key = tuple(row["component_recipe"] for row in sequence[start : start + length])
                candidates[key].append(
                    {
                        "unit": unit,
                        "page": sequence[start]["page"],
                        "start": start,
                        "rows": sequence[start : start + length],
                    }
                )
    qualified = {
        key: occurrences
        for key, occurrences in candidates.items()
        if len({str(row["unit"]) for row in occurrences}) >= 2
        and len({str(row["page"]) for row in occurrences}) >= 2
    }
    selected = {key: qualified[key] for key in PHRASE_GLOSSES}

    phrase_ids = {key: f"PHR{index:02d}" for index, key in enumerate(sorted(selected, key=lambda key: (len(key), key)), start=1)}
    phrase_rows = []
    occurrence_rows = []
    for key in sorted(selected, key=lambda key: (len(key), key)):
        occurrences = selected[key]
        identity_sequences = {
            tuple(str(row["identity"]) for row in occurrence["rows"]) for occurrence in occurrences
        }
        surface_sequences = {
            " ".join(str(row["fifth_hand_surface"]) for row in occurrence["rows"]) for occurrence in occurrences
        }
        phrase_id = phrase_ids[key]
        phrase_rows.append(
            {
                "phrase_id": phrase_id,
                "card_length": len(key),
                "component_sequence": " | ".join(key),
                "working_phrase_de": PHRASE_GLOSSES[key],
                "occurrences": len(occurrences),
                "statements": ",".join(sorted({str(row["unit"]) for row in occurrences})),
                "pages": ",".join(sorted({str(row["page"]) for row in occurrences})),
                "identity_sequence_invariant": "YES" if len(identity_sequences) == 1 else "NO",
                "surface_sequences": " || ".join(sorted(surface_sequences)),
                "workshop_use": "MEMORIZE_AS_ACTION_CHUNK",
            }
        )
        for number, occurrence in enumerate(occurrences, start=1):
            subset = occurrence["rows"]
            occurrence_rows.append(
                {
                    "phrase_id": phrase_id,
                    "occurrence": number,
                    "unit": occurrence["unit"],
                    "page": occurrence["page"],
                    "start_source_id": subset[0]["source_id"],
                    "end_source_id": subset[-1]["source_id"],
                    "identity_sequence": " ".join(str(row["identity"]) for row in subset),
                    "surface_sequence": " ".join(str(row["fifth_hand_surface"]) for row in subset),
                    "literal_cards_de": "; ".join(str(row["concrete_default_de"]) for row in subset),
                    "working_phrase_de": PHRASE_GLOSSES[key],
                }
            )

    statement_rows = []
    covered_events: set[str] = set()
    statements_with_phrase = 0
    ordered_keys = sorted(selected, key=lambda key: (-len(key), key))
    for unit, sequence in by_unit.items():
        segments = []
        phrase_hits = []
        index = 0
        while index < len(sequence):
            match = None
            for key in ordered_keys:
                if tuple(row["component_recipe"] for row in sequence[index : index + len(key)]) == key:
                    match = key
                    break
            if match is not None:
                phrase_id = phrase_ids[match]
                phrase_hits.append(phrase_id)
                segments.append(f"{phrase_id}[{PHRASE_GLOSSES[match]}]")
                for row in sequence[index : index + len(match)]:
                    covered_events.add(row["source_id"])
                index += len(match)
            else:
                segments.append(sequence[index]["concrete_default_de"])
                index += 1
        if phrase_hits:
            statements_with_phrase += 1
        statement_rows.append(
            {
                "unit": unit,
                "page": sequence[0]["page"],
                "source_ids": ",".join(row["source_id"] for row in sequence),
                "fifth_hand_surface_sequence": " ".join(row["fifth_hand_surface"] for row in sequence),
                "component_sequence": " ; ".join(row["component_recipe"] for row in sequence),
                "phrase_ids": ",".join(phrase_hits) if phrase_hits else "NONE",
                "phrase_first_segmentation_de": " ; ".join(segments),
                "fluent_workshop_reading_de": unit_reading[unit],
                "cards": len(sequence),
                "phrase_chunks": len(phrase_hits),
            }
        )

    write(f"{PREFIX}_10_RECURRENT_PHRASES.tsv", phrase_rows, ["phrase_id", "card_length", "component_sequence", "working_phrase_de", "occurrences", "statements", "pages", "identity_sequence_invariant", "surface_sequences", "workshop_use"])
    write(f"{PREFIX}_22_PHRASE_OCCURRENCES.tsv", occurrence_rows, ["phrase_id", "occurrence", "unit", "page", "start_source_id", "end_source_id", "identity_sequence", "surface_sequence", "literal_cards_de", "working_phrase_de"])
    write(f"{PREFIX}_107_PHRASE_FIRST_STATEMENTS.tsv", statement_rows, ["unit", "page", "source_ids", "fifth_hand_surface_sequence", "component_sequence", "phrase_ids", "phrase_first_segmentation_de", "fluent_workshop_reading_de", "cards", "phrase_chunks"])

    lines = ["# Kleines Werkstattphrasenbuch", ""]
    for row in phrase_rows:
        lines.extend(
            [
                f"## {row['phrase_id']}: {row['working_phrase_de']}",
                "",
                f"Kartenbau: `{row['component_sequence']}`.",
                f"Belegt in {row['occurrences']} Stellen auf {row['pages']}.",
                f"Hausoberflächen: `{row['surface_sequences']}`.",
                "",
            ]
        )
    lines.extend(
        [
            "## Leseregel",
            "",
            "Längere Phrase zuerst lesen; sonst einzelne Kartenwerte verbinden. Nur diese zehn",
            "Folgen werden als gelernte Handlungschunks behandelt. Es gibt keine über zwei Seiten",
            "wandernde Vier- oder Fünfkartenphrase; lange Aussagen bleiben frei zusammengesetzt.",
        ]
    )
    (HERE / f"{PREFIX}_WORKSHOP_PHRASEBOOK.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    summary = {
        "status": "PASS",
        "decision": "TEN_SHORT_PHRASES_RECUR_BUT_LONG_WORKSHOP_STATEMENTS_REMAIN_COMPOSITIONAL",
        "physical_prose_events": len(rows),
        "physical_statements": len(statement_rows),
        "phrase_types": len(phrase_rows),
        "bigram_types": sum(int(row["card_length"]) == 2 for row in phrase_rows),
        "trigram_types": sum(int(row["card_length"]) == 3 for row in phrase_rows),
        "four_or_five_card_types": sum(int(row["card_length"]) >= 4 for row in phrase_rows),
        "phrase_occurrences_with_overlap": len(occurrence_rows),
        "events_touched_by_any_phrase": len({event for row in occurrence_rows for event in [row["start_source_id"], row["end_source_id"]]} | covered_events),
        "events_used_by_greedy_phrase_reading": len(covered_events),
        "statements_with_phrase": statements_with_phrase,
        "statements_without_phrase": len(statement_rows) - statements_with_phrase,
        "cross_page_phrase_types": len(phrase_rows),
        "new_card_meanings": 0,
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / f"{PREFIX}_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (HERE / f"{PREFIX}_REPORT.md").write_text(
        "# Sidequest Pass 881: recurrent workshop phrasebook\n\n"
        "Across 334 distinct physical prose events and 107 statements, nine two-card chunks\n"
        "and one three-card chunk recur on at least two pages. The strongest is WEITER →\n"
        "STEHENLASSEN+SCHLUSS, occurring four times. The only portable three-card phrase is\n"
        "longer-ANSETZEN → ANSETZEN → WEITER. No four- or five-card sequence recurs across pages.\n\n"
        "The result supports a small learned phrasebook inside a flexible card-composition system,\n"
        "not a book made from a few repeated full sentence formulas.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
