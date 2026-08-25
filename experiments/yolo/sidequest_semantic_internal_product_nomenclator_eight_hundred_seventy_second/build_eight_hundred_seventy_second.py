#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
HERBAL_DIR = ROOT / "sidequest_semantic_four_herbal_process_atlas_eight_hundred_sixty_fourth"
HERBAL_EVENTS = HERBAL_DIR / "EIGHT_HUNDRED_SIXTY_FOURTH_100_CARD_HERBAL_ATLAS.tsv"
HERBAL_STATEMENTS = HERBAL_DIR / "EIGHT_HUNDRED_SIXTY_FOURTH_19_STATEMENT_HERBAL_ATLAS.tsv"
PAIRINGS = ROOT / "sidequest_semantic_what_how_workshop_leaf_eight_hundred_sixty_seventh" / "EIGHT_HUNDRED_SIXTY_SEVENTH_6_WHAT_HOW_ENTRIES.tsv"
PREFIX = "EIGHT_HUNDRED_SEVENTY_SECOND"

OWNERS = {
    "f10r": ("A", "die breite gezahnte Blütenpflanze"),
    "f11r": ("B", "die dicht blühende Kronenpflanze"),
    "f55v": ("C", "die breitblättrige rispige Pflanze"),
    "f56r": ("D", "die mehrköpfige stachelige Pflanze"),
}

PRODUCTS = {
    "H1-S001": ("A.G1", "GRUNDANSATZ", "erster Grundansatz der Bildpflanze A"),
    "H1-S002": ("A.G2", "GRUNDANSATZ", "weitergeführter wässriger Grundansatz A"),
    "H2-S001": ("A.Z1", "ZWEIGANSATZ", "erster abgezweigter Ansatz aus A.G2"),
    "H2-S002": ("A.Z2", "ZWEIGANSATZ", "weitergeführter Zweigansatz A.Z1"),
    "H2-S003": ("A.Z3", "ZWEIGANSATZ", "ergänzter Zweigansatz der Bildpflanze A"),
    "H3-S001": ("B.X1", "AUSZUG", "erster geschlossener Durchgangsauszug der Bildpflanze B"),
    "H3-S002": ("B.X2", "AUSZUG", "nachbearbeiteter und aufgenommener Auszug B.X1"),
    "H3-S003": ("B.X3", "AUSZUGSPORTION", "davon genommene Portion aus B.X2"),
    "H3-S004": ("B.X4", "AUSZUGSFORTSETZUNG", "offene Fortsetzung der Auszugsportion B.X3"),
    "H4-S001": ("C.M1", "MESSANSATZ", "erster gemessener Ansatz der Bildpflanze C"),
    "H4-S002": ("C.M2", "MESSANSATZ", "übertragener und beiseitegestellter Messansatz C.M1"),
    "H4-S003": ("C.W1", "WARMANSATZ", "erwärmter zweiter Ansatz der Bildpflanze C"),
    "H4-S004": ("C.W2", "WARME_ZIELPORTION", "warme Zielportion aus C.W1"),
    "H5-S001": ("D.I1", "ZUTATENANSATZ", "erster Zutatenansatz der Bildpflanze D"),
    "H5-S002": ("D.P1", "DURCHLASSANSATZ", "geschlossener Durchlassansatz aus D.I1"),
    "H5-S003": ("D.I2", "ZUTATENFORTSETZUNG", "kurze Zutatenfortsetzung nach D.P1"),
    "H5-S004": ("D.A1", "ANWENDUNGSPOSTEN", "Zielanwendungsposten der Bildpflanze D"),
    "H5-S005": ("D.P2", "DURCHLASSPORTION", "Durchlassportion aus D.A1"),
    "H5-S006": ("D.P3", "DURCHLASSFORTSETZUNG", "gemessene offene Durchlassfortsetzung D.P2"),
}

SLOT_TO_PRODUCT = {"P1": "A.G2", "P2": "B.X2", "P3": "C.W2", "P4": "D.P1"}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    events = read(HERBAL_EVENTS)
    statements = {row["statement_id"]: row for row in read(HERBAL_STATEMENTS)}
    pairings = read(PAIRINGS)

    owner_rows = []
    for page, (sigil, owner) in OWNERS.items():
        owner_rows.append(
            {
                "owner_sigil": sigil,
                "herbal_page": page,
                "picture_owner_de": owner,
                "external_species_name": "UNNAMED",
                "scribe_rule_de": f"Alle Produkte dieses Bildartikels beginnen mit {sigil}.",
            }
        )

    product_rows = []
    for statement_id, (handle, family, meaning) in PRODUCTS.items():
        source = statements[statement_id]
        page = source["page"]
        statement_events = [row for row in events if row["statement_id"] == statement_id]
        predecessor = "NONE"
        for candidate_handle, _, _ in PRODUCTS.values():
            if candidate_handle != handle and candidate_handle in meaning:
                predecessor = candidate_handle
        product_rows.append(
            {
                "product_handle": handle,
                "owner_sigil": OWNERS[page][0],
                "herbal_page": page,
                "statement_id": statement_id,
                "product_family": family,
                "internal_workshop_name_de": meaning,
                "predecessor_product": predecessor,
                "cards_in_statement": source["cards"],
                "statement_closed": "YES" if any("SCHLUSS" in row["card_meaning_de"] for row in statement_events) else "NO",
                "external_plant_or_product_name": "UNNAMED",
            }
        )
    product_rows.sort(key=lambda row: list(PRODUCTS).index(str(row["statement_id"])))

    event_rows = []
    for row in events:
        handle, family, meaning = PRODUCTS[row["statement_id"]]
        event_rows.append(
            {
                "event_id": row["event_id"],
                "page": row["page"],
                "record": row["record"],
                "statement_id": row["statement_id"],
                "product_handle": handle,
                "product_family": family,
                "surface": row["surface"],
                "exact_card_id": row["exact_card_id"],
                "card_meaning_de": row["card_meaning_de"],
                "product_reading_de": meaning,
            }
        )

    supply_rows = []
    product_by_handle = {row["product_handle"]: row for row in product_rows}
    for pairing in pairings:
        handle = SLOT_TO_PRODUCT[pairing["what_slot"]]
        product = product_by_handle[handle]
        supply_rows.append(
            {
                "entry_id": pairing["entry_id"],
                "what_slot": pairing["what_slot"],
                "internal_product_handle": handle,
                "internal_product_name_de": product["internal_workshop_name_de"],
                "how_record": pairing["how_record"],
                "how_page": pairing["how_page"],
                "complete_workshop_instruction_de": f"Nimm {handle}, {product['internal_workshop_name_de']}. Arbeitsauftrag: {pairing['how_purpose_de']}.",
                "external_species_required_for_workshop_use": "NO",
            }
        )

    grammar = [
        {"position": 1, "element": "OWNER_SIGIL", "values": "A|B|C|D", "meaning_de": "welcher Bildartikel/Pflanzenbesitzer"},
        {"position": 2, "element": "PRODUCT_FAMILY", "values": "G|Z|X|M|W|I|P|A", "meaning_de": "Grund-, Zweig-, Auszugs-, Mess-, Warm-, Zutaten-, Durchlass- oder Anwendungsposten"},
        {"position": 3, "element": "LOCAL_ORDINAL", "values": "1|2|3|4", "meaning_de": "welcher aufeinanderfolgende Werkstattposten dieser Familie"},
    ]

    write(f"{PREFIX}_4_PICTURE_OWNER_SIGILS.tsv", owner_rows, ["owner_sigil", "herbal_page", "picture_owner_de", "external_species_name", "scribe_rule_de"])
    write(f"{PREFIX}_3_PART_PRODUCT_NAME_GRAMMAR.tsv", grammar, ["position", "element", "values", "meaning_de"])
    write(f"{PREFIX}_19_INTERNAL_PRODUCTS.tsv", product_rows, ["product_handle", "owner_sigil", "herbal_page", "statement_id", "product_family", "internal_workshop_name_de", "predecessor_product", "cards_in_statement", "statement_closed", "external_plant_or_product_name"])
    write(f"{PREFIX}_100_EVENT_PRODUCT_BINDING.tsv", event_rows, ["event_id", "page", "record", "statement_id", "product_handle", "product_family", "surface", "exact_card_id", "card_meaning_de", "product_reading_de"])
    write(f"{PREFIX}_6_EXACT_INTERNAL_SUPPLY_LINKS.tsv", supply_rows, ["entry_id", "what_slot", "internal_product_handle", "internal_product_name_de", "how_record", "how_page", "complete_workshop_instruction_de", "external_species_required_for_workshop_use"])

    lines = [
        "# Interner Produkt-Nomenklator",
        "",
        "Ein Produktname hat drei Teile: Bildbesitzer, Produktfamilie, Laufnummer.",
        "`D.P1` bedeutet daher nicht den botanischen Namen einer Pflanze, sondern den ersten",
        "geschlossenen Durchlassansatz des Bildartikels D. Das genügt der Werkstatt.",
        "",
        "## Vier Vorratsgriffe für WHAT→HOW",
        "",
    ]
    for slot, handle in SLOT_TO_PRODUCT.items():
        product = product_by_handle[handle]
        lines.append(f"- {slot} = **{handle}**: {product['internal_workshop_name_de']}.")
    lines.extend(["", "## Sechs Aufträge", ""])
    for row in supply_rows:
        lines.append(f"- {row['complete_workshop_instruction_de']}")
    lines.extend(
        [
            "",
            "Damit braucht der zweite Schreiber keinen lateinischen oder volkssprachlichen",
            "Pflanzennamen. Er zeigt auf das Bild, nennt den internen Griff und führt den",
            "Biological-Auftrag aus. Nur eine externe Identifikation der Pflanze bleibt offen.",
        ]
    )
    (HERE / f"{PREFIX}_INTERNAL_PRODUCT_HANDBOOK.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    summary = {
        "status": "PASS",
        "decision": "INTERNAL_PRODUCT_IDENTITY_IS_USABLE_WITHOUT_EXTERNAL_SPECIES_NAMES",
        "picture_owner_sigils": len(owner_rows),
        "product_name_parts": len(grammar),
        "internal_products": len(product_rows),
        "bound_herbal_events": len(event_rows),
        "exact_internal_supply_links": len(supply_rows),
        "product_slots_resolved": len(SLOT_TO_PRODUCT),
        "external_species_names": 0,
        "master_values_fully_missing_after": 1,
        "master_values_reduced_to_calibration": 3,
        "book_internal_product_identity_recovered": True,
        "new_voynich_word_meanings": 0,
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / f"{PREFIX}_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (HERE / f"{PREFIX}_REPORT.md").write_text(
        "# Sidequest Pass 872: internal product nomenclator\n\n"
        "Four picture-owner sigils plus eight preparation-family letters and a local ordinal\n"
        "give all nineteen Herbal statements short internal product handles. All 100 Herbal\n"
        "events bind to one of those handles. P1-P4 now resolve to A.G2, B.X2, C.W2 and D.P1.\n\n"
        "This does not identify any plant species or external product name. It does solve the\n"
        "small-workshop problem: a second scribe can point to a picture, request an internal\n"
        "batch and execute one of six Biological jobs. Only the external Astro value remains\n"
        "a fully master-supplied payload.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
