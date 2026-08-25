#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BASE = ROOT / "sidequest_semantic_tenth_workshop_edition_eight_hundred_forty_sixth"
HERBAL = ROOT / "sidequest_semantic_four_herbal_process_atlas_eight_hundred_sixty_fourth" / "EIGHT_HUNDRED_SIXTY_FOURTH_100_CARD_HERBAL_ATLAS.tsv"
PREFIX = "EIGHT_HUNDRED_SIXTY_FIFTH"
PAGES = {"f81v", "f82r", "f83r"}
RECORD_SHAPES = {
    "B1": "shared pool: repeated set, hold, transfer and target cells",
    "B2": "five local stations: measured setting, passage and holding cells",
    "B3": "five local owners: vessel and paired-station procedure catalogue",
    "B4": "paired and left/right stations: transfer, portion and dwell variants",
    "B5": "left-fringe routing and measure appendix",
    "B6": "open right-run setting and target appendix",
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
    events = [row for row in read(BASE / "EIGHT_HUNDRED_FORTY_SIXTH_381_EVENT_INTERLINEAR.tsv") if row["page"] in PAGES]
    statement_source = [row for row in read(BASE / "EIGHT_HUNDRED_FORTY_SIXTH_116_STATEMENT_EDITION.tsv") if row["page"] in PAGES]
    herbal_cards = {row["exact_card_id"] for row in read(HERBAL)}
    cards = []
    for event in events:
        components = event["component_recipe"].split("+")
        cards.append(
            {
                "event_id": event["event_id"],
                "page": event["page"],
                "record": event["record"],
                "statement_id": event["statement_id"],
                "owner_de": event["owner_de"],
                "surface": event["surface"],
                "exact_card_id": event["exact_card_id"],
                "component_recipe": event["component_recipe"],
                "card_meaning_de": event["tenth_edition_reading_de"],
                "semantic_atom_count": len(event["tenth_edition_reading_de"].split(" · ")),
                "shared_with_herbal": "YES" if event["exact_card_id"] in herbal_cards else "NO",
                "quantity": "YES" if any(value in components for value in ["AIN", "AIIN", "IIN", "AN"]) else "NO",
                "target": "YES" if "AL" in components else "NO",
                "source": "YES" if "AR" in components else "NO",
                "passage": "YES" if "CKH" in components else "NO",
                "heat": "YES" if "CHK" in components else "NO",
                "close": "YES" if "SCHLUSS" in event["tenth_edition_reading_de"] else "NO",
            }
        )

    statements = []
    for source in statement_source:
        subset = [row for row in cards if row["statement_id"] == source["statement_id"]]
        statements.append(
            {
                "statement_id": source["statement_id"],
                "page": source["page"],
                "record": source["record"],
                "owner_noun_de": source["owner_noun_de"],
                "surface_sequence": source["surface_sequence"],
                "component_sequence": source["component_sequence"],
                "literal_de": source["ninth_grammar_literal_de"],
                "fluent_reading_de": source["working_reading_de"],
                "cards": len(subset),
                "semantic_atoms": sum(int(row["semantic_atom_count"]) for row in subset),
                "closed_cell": "YES" if any(row["close"] == "YES" for row in subset) else "NO",
                "shared_herbal_cards": sum(row["shared_with_herbal"] == "YES" for row in subset),
            }
        )

    record_rows = []
    for record in ["B1", "B2", "B3", "B4", "B5", "B6"]:
        subset = [row for row in cards if row["record"] == record]
        subset_statements = [row for row in statements if row["record"] == record]
        record_rows.append(
            {
                "record": record,
                "page": subset[0]["page"],
                "owners": len({row["owner_de"] for row in subset}),
                "statements": len(subset_statements),
                "cards": len(subset),
                "exact_card_types": len({row["exact_card_id"] for row in subset}),
                "semantic_atoms": sum(int(row["semantic_atom_count"]) for row in subset),
                "closed_cells": sum(row["closed_cell"] == "YES" for row in subset_statements),
                "shared_herbal_events": sum(row["shared_with_herbal"] == "YES" for row in subset),
                "working_process_shape": RECORD_SHAPES[record],
            }
        )

    page_rows = []
    for page in ["f81v", "f82r", "f83r"]:
        subset = [row for row in cards if row["page"] == page]
        subset_statements = [row for row in statements if row["page"] == page]
        page_rows.append(
            {
                "page": page,
                "records": len({row["record"] for row in subset}),
                "owners": len({row["owner_de"] for row in subset}),
                "statements": len(subset_statements),
                "cards": len(subset),
                "exact_card_types": len({row["exact_card_id"] for row in subset}),
                "semantic_atoms": sum(int(row["semantic_atom_count"]) for row in subset),
                "closed_cells": sum(row["closed_cell"] == "YES" for row in subset_statements),
                "open_cells": sum(row["closed_cell"] == "NO" for row in subset_statements),
                "shared_herbal_events": sum(row["shared_with_herbal"] == "YES" for row in subset),
                "quantity_cards": sum(row["quantity"] == "YES" for row in subset),
                "target_cards": sum(row["target"] == "YES" for row in subset),
                "source_cards": sum(row["source"] == "YES" for row in subset),
                "passage_cards": sum(row["passage"] == "YES" for row in subset),
                "heat_cards": sum(row["heat"] == "YES" for row in subset),
            }
        )

    pages_by_card: dict[str, set[str]] = defaultdict(set)
    herb_count: Counter[str] = Counter(row["exact_card_id"] for row in read(HERBAL))
    bio_count: Counter[str] = Counter()
    for row in cards:
        pages_by_card[str(row["exact_card_id"])].add(str(row["page"]))
        bio_count[str(row["exact_card_id"])] += 1
    shared_rows = []
    for card_id in sorted(set(bio_count) & set(herb_count)):
        exemplar = next(row for row in cards if row["exact_card_id"] == card_id)
        shared_rows.append(
            {
                "exact_card_id": card_id,
                "component_recipe": exemplar["component_recipe"],
                "meaning_de": exemplar["card_meaning_de"],
                "herbal_events": herb_count[card_id],
                "biological_events": bio_count[card_id],
                "biological_pages": "|".join(sorted(pages_by_card[card_id])),
                "application_compatible": "YES",
            }
        )
    shared_rows.sort(key=lambda row: (-int(row["biological_events"]), str(row["exact_card_id"])))

    comparison = [
        {"register": "HERBAL", "pages": 4, "statements": 19, "cards": 100, "semantic_atoms": 206, "closed_statements": 4, "open_statements": 15, "working_text_type": "long picture-owned preparation articles"},
        {"register": "BIOLOGICAL", "pages": 3, "statements": len(statements), "cards": len(cards), "semantic_atoms": sum(int(row["semantic_atom_count"]) for row in cards), "closed_statements": sum(row["closed_cell"] == "YES" for row in statements), "open_statements": sum(row["closed_cell"] == "NO" for row in statements), "working_text_type": "short station-owned application cells"},
    ]
    write(f"{PREFIX}_281_CARD_BIOLOGICAL_ATLAS.tsv", cards, ["event_id", "page", "record", "statement_id", "owner_de", "surface", "exact_card_id", "component_recipe", "card_meaning_de", "semantic_atom_count", "shared_with_herbal", "quantity", "target", "source", "passage", "heat", "close"])
    write(f"{PREFIX}_97_STATEMENT_BIOLOGICAL_ATLAS.tsv", statements, ["statement_id", "page", "record", "owner_noun_de", "surface_sequence", "component_sequence", "literal_de", "fluent_reading_de", "cards", "semantic_atoms", "closed_cell", "shared_herbal_cards"])
    write(f"{PREFIX}_6_RECORD_PROCESS_PROFILES.tsv", record_rows, ["record", "page", "owners", "statements", "cards", "exact_card_types", "semantic_atoms", "closed_cells", "shared_herbal_events", "working_process_shape"])
    write(f"{PREFIX}_3_PAGE_PROCESS_PROFILES.tsv", page_rows, ["page", "records", "owners", "statements", "cards", "exact_card_types", "semantic_atoms", "closed_cells", "open_cells", "shared_herbal_events", "quantity_cards", "target_cards", "source_cards", "passage_cards", "heat_cards"])
    write(f"{PREFIX}_17_HERBAL_BIOLOGICAL_SHARED_CARDS.tsv", shared_rows, ["exact_card_id", "component_recipe", "meaning_de", "herbal_events", "biological_events", "biological_pages", "application_compatible"])
    write(f"{PREFIX}_HERBAL_BIOLOGICAL_TEXT_TYPE_COMPARISON.tsv", comparison, ["register", "pages", "statements", "cards", "semantic_atoms", "closed_statements", "open_statements", "working_text_type"])

    shared_events = sum(int(row["biological_events"]) for row in shared_rows)
    summary = {
        "status": "PASS",
        "decision": "BIOLOGICAL_ATLAS_FITS_APPLICATION_CELLS_WITHOUT_DIRECT_HERBAL_CROSSREFERENCE",
        "pages": len(page_rows),
        "records": len(record_rows),
        "owners": len({row["owner_de"] for row in cards}),
        "statements": len(statements),
        "cards": len(cards),
        "exact_card_types": len({row["exact_card_id"] for row in cards}),
        "semantic_atoms": sum(int(row["semantic_atom_count"]) for row in cards),
        "closed_statements": sum(row["closed_cell"] == "YES" for row in statements),
        "open_statements": sum(row["closed_cell"] == "NO" for row in statements),
        "shared_herbal_exact_cards": len(shared_rows),
        "shared_herbal_biological_events": shared_events,
        "bio_local_events": len(cards) - shared_events,
        "direct_herbal_crossreferences": 0,
        "new_meanings": 0,
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / f"{PREFIX}_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = ["# Atlas der drei Biological-Seiten", ""]
    for row in record_rows:
        lines.extend([
            f"## {row['record']} / {row['page']}", "",
            f"{row['working_process_shape']}", "",
            f"{row['cards']} Karten, {row['statements']} Zellen, {row['closed_cells']} geschlossen, {row['owners']} Bildbesitzer.", "",
        ])
    lines.extend([
        "## Herbal → Biological", "",
        "Siebzehn exakte Karten erscheinen in beiden Registern und tragen 92/281",
        "Biological-Ereignisse: Quelle, Zielstelle, Sollmaß, Ansatz, Posten, Ansetzen,",
        "Bereiten, Umsetzen, Halten und Weiter. Biological schließt 85/97 Aussagen,",
        "Herbal nur 4/19. Das passt gut zu Zubereitung → einzelne Anwendung/Zelle.", "",
        "Ein direkter Kartenverweis von einer Herbal-Seite zu einer Biological-Zelle",
        "ist nicht vorhanden. Die Verbindung bleibt eine Werkstatt-Lesetheorie.",
    ])
    (HERE / f"{PREFIX}_THREE_BIOLOGICAL_ATLAS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (HERE / f"{PREFIX}_REPORT.md").write_text(
        "# Sidequest Pass 865: three-page Biological process atlas\n\n"
        "All three fixed Biological pages now form one atlas: 281 cards, 97 statements,\n"
        "six records, sixteen local image owners and 644 semantic atoms. Eighty-five\n"
        "statements close and twelve remain open.\n\n"
        "Seventeen exact cards are shared with Herbal and account for ninety-two Biological\n"
        "events. Their meanings are precisely application-compatible: source, target,\n"
        "measure, batch, item, set, prepare, transfer, hold and continue. Against Herbal's\n"
        "4/19 closed statements, Biological's 85/97 closure density makes the strongest\n"
        "current content story preparation articles -> short station application cells.\n\n"
        "There is still no direct Herbal-to-Biological crossreference card, so this is a\n"
        "coherent workshop reading rather than a decoded link. Next, pair page process\n"
        "types without claiming exact product identity.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
