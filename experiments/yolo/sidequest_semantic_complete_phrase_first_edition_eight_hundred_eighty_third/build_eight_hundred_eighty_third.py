#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
HERBAL = ROOT / "sidequest_semantic_four_herbal_process_atlas_eight_hundred_sixty_fourth" / "EIGHT_HUNDRED_SIXTY_FOURTH_100_CARD_HERBAL_ATLAS.tsv"
BIO = ROOT / "sidequest_semantic_three_biological_process_atlas_eight_hundred_sixty_fifth" / "EIGHT_HUNDRED_SIXTY_FIFTH_281_CARD_BIOLOGICAL_ATLAS.tsv"
STATEMENTS = ROOT / "sidequest_semantic_tenth_workshop_edition_eight_hundred_forty_sixth" / "EIGHT_HUNDRED_FORTY_SIXTH_116_STATEMENT_EDITION.tsv"
HOUSE = ROOT / "sidequest_semantic_multihand_renderer_drill_eight_hundred_seventy_eighth" / "EIGHT_HUNDRED_SEVENTY_EIGHTH_56_CORE_RENDERER_FAMILIES.tsv"
OLD_STATEMENTS = ROOT / "sidequest_semantic_recurrent_phrasebook_eight_hundred_eighty_first" / "EIGHT_HUNDRED_EIGHTY_FIRST_107_PHRASE_FIRST_STATEMENTS.tsv"
BOUNDARIES = ROOT / "sidequest_semantic_phrase_boundary_lexicon_eight_hundred_eighty_second" / "EIGHT_HUNDRED_EIGHTY_SECOND_12_LOCAL_BOUNDARY_REFINEMENTS.tsv"
PREFIX = "EIGHT_HUNDRED_EIGHTY_THIRD"

ATOM_CALIBRATION = {
    "SOLLMASS": "EIN KLEINER SCHOEPFBECHER",
    "PORTION": "EIN ABGEGRENZTER TEIL",
    "STUFE": "EINE EINGESTELLTE ARBEITSSTUFE",
    "KURZ": "EIN KURZER ARBEITSGANG",
    "LANG": "DREI KURZE ARBEITSGAENGE",
    "VOLL": "BIS DER GANZE POSTEN ERFASST IST",
}

PHRASE_GLOSSES = {
    ("AIIN", "Y"): "DEN POSTEN NACH SOLLMASS FUEHREN",
    ("AL", "OL"): "AN DER ZIELSTELLE WEITERARBEITEN",
    ("CHD+Y", "OL"): "DEN POSTEN UMSETZEN UND WEITERFUEHREN",
    ("OK+EE+Y", "OK+Y"): "DEN POSTEN LAENGER ANSETZEN UND ERNEUT ANSETZEN",
    ("OK+Y", "AIIN"): "DEN POSTEN NACH SOLLMASS ANSETZEN",
    ("OK+Y", "OL"): "DEN POSTEN ANSETZEN UND WEITERARBEITEN",
    ("OL", "AIIN"): "NACH SOLLMASS WEITERARBEITEN",
    ("OL", "SHED+DY"): "WEITERARBEITEN, STEHENLASSEN UND SCHLIESSEN",
    ("OL+K+AIN", "AL"): "EINE PORTION WEITER AN DIE ZIELSTELLE GEBEN",
    ("OL+OR", "OL"): "DEN ANSATZ WEITERFUEHREN UND WEITERARBEITEN",
    ("OR", "Y"): "DEN ANSATZ ALS LAUFENDEN POSTEN FUEHREN",
    ("Y", "AIIN"): "DEN POSTEN AUF SOLLMASS BRINGEN",
    ("OK+EE+Y", "OK+Y", "OL"): "DEN POSTEN LAENGER ANSETZEN, ERNEUT ANSETZEN UND WEITERARBEITEN",
    ("Y", "AIIN", "Y"): "DEN AKTUELLEN POSTEN NACH SOLLMASS WEITERFUEHREN",
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def calibrate(value: str) -> str:
    return " · ".join(ATOM_CALIBRATION.get(atom, atom) for atom in value.split(" · "))


def main() -> None:
    herbal = read(HERBAL)
    bio = read(BIO)
    statements = read(STATEMENTS)
    statement_by_id = {row["statement_id"]: row for row in statements}
    house = {row["identity"]: row["house_model_surface"] for row in read(HOUSE)}
    old_statement_ids = {row["unit"] for row in read(OLD_STATEMENTS)}
    compact = {row["source_id"]: row["compact_phrase_boundary_de"] for row in read(BOUNDARIES)}

    events = []
    for row in herbal:
        events.append(
            {
                "event_id": row["event_id"], "page": row["page"], "record": row["record"], "statement_id": row["statement_id"],
                "owner_de": statement_by_id[row["statement_id"]]["owner_noun_de"], "original_surface": row["surface"],
                "fifth_hand_surface": house.get(row["exact_card_id"], row["surface"]), "identity": row["exact_card_id"],
                "card_class": "PORTABLE_CORE" if row["exact_card_id"] in house else "LOCAL_MODEL", "component_recipe": row["component_recipe"],
                "concrete_default_de": calibrate(row["card_meaning_de"]), "source_section": "HERBAL",
            }
        )
    for row in bio:
        events.append(
            {
                "event_id": row["event_id"], "page": row["page"], "record": row["record"], "statement_id": row["statement_id"],
                "owner_de": row["owner_de"], "original_surface": row["surface"], "fifth_hand_surface": house.get(row["exact_card_id"], row["surface"]),
                "identity": row["exact_card_id"], "card_class": "PORTABLE_CORE" if row["exact_card_id"] in house else "LOCAL_MODEL",
                "component_recipe": row["component_recipe"], "concrete_default_de": calibrate(row["card_meaning_de"]), "source_section": "BIOLOGICAL",
            }
        )
    events.sort(key=lambda row: int(row["event_id"][1:]))
    for row in events:
        row["surface_action"] = "NORMALIZE_TO_HOUSE" if row["fifth_hand_surface"] != row["original_surface"] else "COPY_UNCHANGED"
        row["phrase_ready_card_de"] = compact.get(row["event_id"], row["concrete_default_de"])

    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        by_statement[row["statement_id"]].append(row)

    candidates: dict[tuple[str, ...], list[tuple[str, str, int]]] = defaultdict(list)
    for statement_id, sequence in by_statement.items():
        for length in range(2, 6):
            for start in range(len(sequence) - length + 1):
                key = tuple(row["component_recipe"] for row in sequence[start : start + length])
                candidates[key].append((statement_id, sequence[start]["page"], start))
    qualified = {
        key: occurrences for key, occurrences in candidates.items()
        if len({row[0] for row in occurrences}) >= 2 and len({row[1] for row in occurrences}) >= 2
    }
    if set(qualified) != set(PHRASE_GLOSSES):
        raise RuntimeError(f"phrase inventory drift: {sorted(set(qualified) ^ set(PHRASE_GLOSSES))}")
    phrase_ids = {key: f"CPH{index:02d}" for index, key in enumerate(sorted(qualified, key=lambda key: (len(key), key)), start=1)}

    phrase_rows = []
    phrase_occurrence_rows = []
    for key in sorted(qualified, key=lambda key: (len(key), key)):
        occurrences = qualified[key]
        phrase_id = phrase_ids[key]
        phrase_rows.append(
            {
                "phrase_id": phrase_id, "card_length": len(key), "component_sequence": " | ".join(key),
                "working_phrase_de": PHRASE_GLOSSES[key], "occurrences": len(occurrences),
                "statements": ",".join(sorted({row[0] for row in occurrences})), "pages": ",".join(sorted({row[1] for row in occurrences})),
                "status": "COMPLETE_381_EVENT_PHRASEBOOK",
            }
        )
        for number, (statement_id, page, start) in enumerate(occurrences, start=1):
            subset = by_statement[statement_id][start : start + len(key)]
            phrase_occurrence_rows.append(
                {
                    "phrase_id": phrase_id, "occurrence": number, "statement_id": statement_id, "page": page,
                    "start_event_id": subset[0]["event_id"], "end_event_id": subset[-1]["event_id"],
                    "surface_sequence": " ".join(row["fifth_hand_surface"] for row in subset),
                    "identity_sequence": " ".join(row["identity"] for row in subset), "working_phrase_de": PHRASE_GLOSSES[key],
                }
            )

    ordered_keys = sorted(qualified, key=lambda key: (-len(key), key))
    statement_rows = []
    greedy_events: set[str] = set()
    for source in statements:
        statement_id = source["statement_id"]
        sequence = by_statement[statement_id]
        segments = []
        used_phrases = []
        index = 0
        while index < len(sequence):
            match = None
            for key in ordered_keys:
                if tuple(row["component_recipe"] for row in sequence[index : index + len(key)]) == key:
                    match = key
                    break
            if match is not None:
                phrase_id = phrase_ids[match]
                used_phrases.append(phrase_id)
                segments.append(f"{phrase_id}[{PHRASE_GLOSSES[match]}]")
                greedy_events.update(row["event_id"] for row in sequence[index : index + len(match)])
                index += len(match)
            else:
                segments.append(sequence[index]["phrase_ready_card_de"])
                index += 1
        statement_rows.append(
            {
                "statement_id": statement_id, "page": source["page"], "record": source["record"], "owner_de": source["owner_noun_de"],
                "events": len(sequence), "fifth_hand_surface_sequence": " ".join(row["fifth_hand_surface"] for row in sequence),
                "component_sequence": " | ".join(row["component_recipe"] for row in sequence),
                "phrase_ids": ",".join(used_phrases) if used_phrases else "NONE", "phrase_first_reading_de": "; ".join(segments),
                "fluent_workshop_reading_de": source["working_reading_de"], "restored_after_107_statement_omission": "YES" if statement_id not in old_statement_ids else "NO",
            }
        )

    restored_rows = [row for row in statement_rows if row["restored_after_107_statement_omission"] == "YES"]
    record_rows = []
    for record in ["H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"]:
        subset = [row for row in statement_rows if row["record"] == record]
        record_rows.append(
            {
                "record": record, "page": subset[0]["page"], "statements": len(subset), "events": sum(int(row["events"]) for row in subset),
                "phrase_bearing_statements": sum(row["phrase_ids"] != "NONE" for row in subset),
                "continuous_workshop_reading_de": " ".join(row["fluent_workshop_reading_de"] for row in subset),
            }
        )

    write(f"{PREFIX}_381_EVENT_COMPLETE_FIFTH_HAND.tsv", events, ["event_id", "page", "record", "statement_id", "owner_de", "original_surface", "fifth_hand_surface", "identity", "card_class", "component_recipe", "concrete_default_de", "phrase_ready_card_de", "source_section", "surface_action"])
    write(f"{PREFIX}_116_COMPLETE_PHRASE_FIRST_STATEMENTS.tsv", statement_rows, ["statement_id", "page", "record", "owner_de", "events", "fifth_hand_surface_sequence", "component_sequence", "phrase_ids", "phrase_first_reading_de", "fluent_workshop_reading_de", "restored_after_107_statement_omission"])
    write(f"{PREFIX}_14_COMPLETE_RECURRENT_PHRASES.tsv", phrase_rows, ["phrase_id", "card_length", "component_sequence", "working_phrase_de", "occurrences", "statements", "pages", "status"])
    write(f"{PREFIX}_34_COMPLETE_PHRASE_OCCURRENCES.tsv", phrase_occurrence_rows, ["phrase_id", "occurrence", "statement_id", "page", "start_event_id", "end_event_id", "surface_sequence", "identity_sequence", "working_phrase_de"])
    write(f"{PREFIX}_9_RESTORED_STATEMENTS.tsv", restored_rows, list(statement_rows[0]))
    write(f"{PREFIX}_11_CONTINUOUS_RECORDS.tsv", record_rows, ["record", "page", "statements", "events", "phrase_bearing_statements", "continuous_workshop_reading_de"])

    lines = ["# Vollständige Phrasenausgabe der elf Prosa-Records", ""]
    for record in record_rows:
        lines.extend([f"## {record['record']} ({record['page']})", ""])
        for row in statement_rows:
            if row["record"] != record["record"]:
                continue
            lines.extend(
                [
                    f"### {row['statement_id']} — {row['owner_de']}",
                    "",
                    f"`{row['fifth_hand_surface_sequence']}`",
                    "",
                    f"Phrasenlesung: {row['phrase_first_reading_de']}",
                    "",
                    f"Flüssig: {row['fluent_workshop_reading_de']}",
                    "",
                ]
            )
    lines.extend(
        [
            "## Korrekturhinweis",
            "",
            "Die frühere 107-Aussagen-Phrasenfassung war nur die Prosa der sechs Aufträge.",
            "Hier sind H2 sowie die Nachsätze H3-S003–S004 und H5-S003–S006 wieder eingesetzt:",
            "neun Aussagen und 47 Karten. Damit umfasst die Ausgabe wieder alle 381 Karten.",
        ]
    )
    (HERE / f"{PREFIX}_COMPLETE_ELEVEN_RECORD_EDITION.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    summary = {
        "status": "PASS",
        "decision": "COMPLETE_ELEVEN_RECORD_EDITION_RESTORES_FORTY_SEVEN_OMITTED_HERBAL_CARDS_AND_EXPANDS_PHRASEBOOK",
        "events": len(events), "statements": len(statement_rows), "records": len(record_rows),
        "herbal_events": sum(row["source_section"] == "HERBAL" for row in events), "biological_events": sum(row["source_section"] == "BIOLOGICAL" for row in events),
        "restored_statements": len(restored_rows), "restored_events": sum(int(row["events"]) for row in restored_rows),
        "phrase_types": len(phrase_rows), "bigram_types": sum(int(row["card_length"]) == 2 for row in phrase_rows),
        "trigram_types": sum(int(row["card_length"]) == 3 for row in phrase_rows), "longer_phrase_types": sum(int(row["card_length"]) > 3 for row in phrase_rows),
        "phrase_occurrences": len(phrase_occurrence_rows), "greedy_phrase_events": len(greedy_events),
        "normalized_surfaces": sum(row["surface_action"] == "NORMALIZE_TO_HOUSE" for row in events),
        "identities": len({row["identity"] for row in events}), "new_card_meanings": 0,
        "fixed_pages": sorted({row["page"] for row in events}), "sealed_pages": ["f84", "f84r"],
    }
    (HERE / f"{PREFIX}_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (HERE / f"{PREFIX}_REPORT.md").write_text(
        "# Sidequest Pass 883: complete phrase-first eleven-record edition\n\n"
        "The prior 107-statement phrase pass reflected only the six-order preparation subset.\n"
        "This correction restores H2 and the unused H3/H5 continuations: nine statements and 47\n"
        "events. The complete edition again contains 381 events, 116 statements and 11 records.\n\n"
        "On the restored corpus the cross-page phrasebook grows from ten to fourteen chunks: 12\n"
        "bigrams and two trigrams. The returned Y-AIIN-Y frame is read minimally as DEN AKTUELLEN\n"
        "POSTEN NACH SOLLMASS WEITERFUEHREN, not as a grounded equality or semantic operator.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
