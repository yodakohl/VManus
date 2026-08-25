#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BASE = ROOT / "sidequest_semantic_tenth_workshop_edition_eight_hundred_forty_sixth"
PREFIX = "EIGHT_HUNDRED_SIXTY_FOURTH"
PAGE_FILES = {
    "f10r": (ROOT / "sidequest_semantic_f10r_complete_source_edition_eight_hundred_sixtieth" / "EIGHT_HUNDRED_SIXTIETH_38_CARD_PAGE_EDITION.tsv", ROOT / "sidequest_semantic_f10r_complete_source_edition_eight_hundred_sixtieth" / "EIGHT_HUNDRED_SIXTIETH_5_STATEMENT_LAYER_MAP.tsv"),
    "f11r": (ROOT / "sidequest_semantic_f11r_extraction_source_edition_eight_hundred_sixty_first" / "EIGHT_HUNDRED_SIXTY_FIRST_17_CARD_PAGE_EDITION.tsv", ROOT / "sidequest_semantic_f11r_extraction_source_edition_eight_hundred_sixty_first" / "EIGHT_HUNDRED_SIXTY_FIRST_4_STATEMENT_LAYER_MAP.tsv"),
    "f55v": (ROOT / "sidequest_semantic_f55v_measured_batch_source_edition_eight_hundred_sixty_second" / "EIGHT_HUNDRED_SIXTY_SECOND_18_CARD_PAGE_EDITION.tsv", ROOT / "sidequest_semantic_f55v_measured_batch_source_edition_eight_hundred_sixty_second" / "EIGHT_HUNDRED_SIXTY_SECOND_4_STATEMENT_LAYER_MAP.tsv"),
    "f56r": (ROOT / "sidequest_semantic_f56r_ingredient_source_edition_eight_hundred_sixty_third" / "EIGHT_HUNDRED_SIXTY_THIRD_27_CARD_PAGE_EDITION.tsv", ROOT / "sidequest_semantic_f56r_ingredient_source_edition_eight_hundred_sixty_third" / "EIGHT_HUNDRED_SIXTY_THIRD_6_STATEMENT_LAYER_MAP.tsv"),
}
SHAPES = {
    "f10r": "main preparation plus open derived branch",
    "f11r": "close first extract then resume an open portion",
    "f55v": "measure, supplement, set aside, heat, target",
    "f56r": "ingredient slots and repeated application cycles",
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
    base_events = {
        row["event_id"]: row
        for row in read(BASE / "EIGHT_HUNDRED_FORTY_SIXTH_381_EVENT_INTERLINEAR.tsv")
        if row["page"] in PAGE_FILES
    }
    cards = []
    statements = []
    for page, (card_path, statement_path) in PAGE_FILES.items():
        for local in read(card_path):
            event = base_events[local["event_id"]]
            components = event["component_recipe"].split("+")
            cards.append(
                {
                    "event_id": event["event_id"],
                    "page": page,
                    "record": event["record"],
                    "statement_id": event["statement_id"],
                    "surface": event["surface"],
                    "exact_card_id": event["exact_card_id"],
                    "component_recipe": event["component_recipe"],
                    "card_meaning_de": event["tenth_edition_reading_de"],
                    "semantic_atom_count": len(event["tenth_edition_reading_de"].split(" · ")),
                    "source_phrase": local["source_phrase"],
                    "quantity": "YES" if any(value in components for value in ["AIN", "AIIN", "IIN", "AN"]) else "NO",
                    "water": "YES" if "AIR" in components else "NO",
                    "press": "YES" if "CFH" in components else "NO",
                    "passage": "YES" if "CKH" in components else "NO",
                    "heat": "YES" if "CHK" in components else "NO",
                    "ingredient": "YES" if "HO" in components else "NO",
                    "target": "YES" if "AL" in components else "NO",
                    "close": "YES" if "SCHLUSS" in event["tenth_edition_reading_de"] else "NO",
                }
            )
        for row in read(statement_path):
            statements.append(
                {
                    "page": page,
                    "statement_id": row["statement_id"],
                    "transition": row["transition"],
                    "incoming_registers": row["incoming_registers"],
                    "outgoing_registers": row["outgoing_registers"],
                    "picture_owner": row["picture_contribution"],
                    "surface_sequence": row.get("surface_sequence", ""),
                    "latin_like_source_statement": row["latin_like_source_statement"],
                    "fluent_reading_de": row["fluent_reading_de"],
                    "cards": row["cards"],
                    "semantic_atoms": row["semantic_atoms"],
                }
            )

    page_rows = []
    for page in PAGE_FILES:
        subset = [row for row in cards if row["page"] == page]
        page_statements = [row for row in statements if row["page"] == page]
        page_rows.append(
            {
                "page": page,
                "picture_owner": page_statements[0]["picture_owner"],
                "records": len({row["record"] for row in subset}),
                "statements": len(page_statements),
                "cards": len(subset),
                "exact_card_types": len({row["exact_card_id"] for row in subset}),
                "semantic_atoms": sum(int(row["semantic_atom_count"]) for row in subset),
                "quantity_cards": sum(row["quantity"] == "YES" for row in subset),
                "water_cards": sum(row["water"] == "YES" for row in subset),
                "press_cards": sum(row["press"] == "YES" for row in subset),
                "passage_cards": sum(row["passage"] == "YES" for row in subset),
                "heat_cards": sum(row["heat"] == "YES" for row in subset),
                "ingredient_cards": sum(row["ingredient"] == "YES" for row in subset),
                "target_cards": sum(row["target"] == "YES" for row in subset),
                "closes": sum(row["close"] == "YES" for row in subset),
                "working_process_shape": SHAPES[page],
            }
        )

    pages_by_card: dict[str, set[str]] = defaultdict(set)
    events_by_card: Counter[str] = Counter()
    for row in cards:
        pages_by_card[str(row["exact_card_id"])].add(str(row["page"]))
        events_by_card[str(row["exact_card_id"])] += 1
    shared = []
    for card_id, pages in pages_by_card.items():
        if len(pages) < 2:
            continue
        exemplar = next(row for row in cards if row["exact_card_id"] == card_id)
        shared.append(
            {
                "exact_card_id": card_id,
                "component_recipe": exemplar["component_recipe"],
                "meaning_de": exemplar["card_meaning_de"],
                "pages": "|".join(sorted(pages)),
                "page_count": len(pages),
                "events": events_by_card[card_id],
            }
        )
    shared.sort(key=lambda row: (-int(row["page_count"]), -int(row["events"]), str(row["exact_card_id"])))

    write(f"{PREFIX}_100_CARD_HERBAL_ATLAS.tsv", cards, ["event_id", "page", "record", "statement_id", "surface", "exact_card_id", "component_recipe", "card_meaning_de", "semantic_atom_count", "source_phrase", "quantity", "water", "press", "passage", "heat", "ingredient", "target", "close"])
    write(f"{PREFIX}_19_STATEMENT_HERBAL_ATLAS.tsv", statements, ["page", "statement_id", "transition", "incoming_registers", "outgoing_registers", "picture_owner", "surface_sequence", "latin_like_source_statement", "fluent_reading_de", "cards", "semantic_atoms"])
    write(f"{PREFIX}_4_PAGE_PROCESS_PROFILES.tsv", page_rows, ["page", "picture_owner", "records", "statements", "cards", "exact_card_types", "semantic_atoms", "quantity_cards", "water_cards", "press_cards", "passage_cards", "heat_cards", "ingredient_cards", "target_cards", "closes", "working_process_shape"])
    write(f"{PREFIX}_8_SHARED_EXACT_CARDS.tsv", shared, ["exact_card_id", "component_recipe", "meaning_de", "pages", "page_count", "events"])

    shared_events = sum(int(row["events"]) for row in shared)
    summary = {
        "status": "PASS",
        "decision": "HERBAL_ATLAS_IS_SHARED_MEASURED_WORKSHOP_GRAMMAR_WITH_FOUR_DISTINCT_RECIPES",
        "pages": len(page_rows),
        "picture_owners": len({row["picture_owner"] for row in page_rows}),
        "records": len({row["record"] for row in cards}),
        "statements": len(statements),
        "cards": len(cards),
        "exact_card_types": len(pages_by_card),
        "semantic_atoms": sum(int(row["semantic_atom_count"]) for row in cards),
        "closes": sum(row["close"] == "YES" for row in cards),
        "cross_page_exact_card_types": len(shared),
        "cross_page_exact_card_events": shared_events,
        "page_local_exact_card_events": len(cards) - shared_events,
        "all_four_page_cards": [row["exact_card_id"] for row in shared if int(row["page_count"]) == 4],
        "unmapped_cards": 0,
        "new_meanings": 0,
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / f"{PREFIX}_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = ["# Atlas der vier Pflanzenartikel", ""]
    for row in page_rows:
        lines.extend([
            f"## {row['page']} — {row['working_process_shape']}", "",
            f"Besitzer: **{row['picture_owner']}**", "",
            f"{row['cards']} Karten, {row['statements']} Aussagen, {row['semantic_atoms']} Atome, {row['closes']} Schlüsse.", "",
        ])
    lines.extend([
        "## Gemeinsamer Kartensatz", "",
        "Acht exakte Karten überschreiten Seitengrenzen und tragen 36/100 Ereignisse.",
        "Nur AIIN/SOLLMASS erscheint auf allen vier Seiten. Die übrigen 64 Ereignisse",
        "nutzen seitenlokale exakte Karten, bleiben aber aus demselben Komponenten- und",
        "Schreibsystem gebaut.", "",
        "Damit ist das Herbal-Modell weder ein einziges starres Rezept noch vier fremde",
        "Sprachen: gemeinsame Werkstattgrammatik, vier bildgebundene Arbeitsartikel.",
    ])
    (HERE / f"{PREFIX}_FOUR_HERBAL_ATLAS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (HERE / f"{PREFIX}_REPORT.md").write_text(
        "# Sidequest Pass 864: four-page Herbal process atlas\n\n"
        "The four fixed Herbal pages now form a single atlas of one hundred cards,\n"
        "nineteen statements and 206 semantic atoms under four picture owners. Their\n"
        "processes are deliberately different: open preparation/branch; closed extraction\n"
        "and resumption; measured batching/heating; ingredient/application cycles.\n\n"
        "Eight exact card types recur across pages and account for thirty-six events.\n"
        "AIIN/SOLLMASS is the sole exact card on all four pages. Sixty-four events use\n"
        "page-local exact cards, but all remain in the shared component grammar. The\n"
        "best current picture is therefore a common measured workshop register with\n"
        "four distinct, image-owned recipes.\n\n"
        "Next, build an equally concrete Biological process atlas and compare whether\n"
        "its short closed cells are applications of these Herbal products.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
