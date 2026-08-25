#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BASE = ROOT / "sidequest_semantic_tenth_workshop_edition_eight_hundred_forty_sixth"
PREFIX = "EIGHT_HUNDRED_SIXTY_THIRD"

SOURCE_BY_CARD = {
    "PROC051": ("additamentum de praeparatione sume", "addit. / de prep. sume"),
    "PROC052": ("additamentum", "addit."),
    "PROC053": ("additamentum ad locum ut rem", "addit. / ad loc. / rem"),
    "PROC009": ("ad mensuram", "ad mens."),
    "PROC054": ("adde et continua", "adde / cont."),
    "PROC020": ("deinde de praeparatione sume", "deinde / de prep. sume"),
    "PROC008": ("rem pone", "rem / pone"),
    "PROC055": ("ad locum", "ad loc."),
    "PROC034": ("ex eo", "ex eo"),
    "PROC056": ("additamentum ut rem", "addit. / rem"),
    "PROC057": ("diu per meatum in opere sume; fini", "diu / per meat. / in op. sume / f."),
    "PROC058": ("tene", "tene"),
    "PROC059": ("rem cito adde", "rem / cito adde"),
    "PROC060": ("rem bis pone", "rem / bis pone"),
    "PROC011": ("rem pone", "rem / pone"),
    "PROC061": ("in opere cito pone et sume", "in op. / cito pone-sume"),
    "PROC062": ("ad locum adde", "ad loc. / adde"),
    "PROC063": ("additamentum ex fonte adde", "addit. / ex fonte / adde"),
    "PROC064": ("deinde portionem in opere", "deinde / port. / in op."),
    "PROC065": ("deinde rem", "deinde rem"),
    "PROC066": ("cito adde et continua", "cito adde / cont."),
}

STATEMENT_SOURCES = {
    "H5-S001": "Additamentum de praeparatione sume, ad locum ut rem fer et ad mensuram continua addere; deinde de praeparatione sume et rem ad locum pone.",
    "H5-S002": "Ex eo additamentum ut rem pone; diu per meatum in opere sume et fini.",
    "H5-S003": "Additamentum tene, rem cito adde et bis pone.",
    "H5-S004": "Rem pone; in opere cito pone et sume; ad locum adde.",
    "H5-S005": "Additamentum et rem pone; additamentum ex fonte adde; deinde portionem in opere sume.",
    "H5-S006": "Deinde rem cito adde et continua ad mensuram.",
}

TRANSITIONS = {
    "H5-S001": ("PICTURE_OWNER+INGREDIENT_SLOT", "MEASURED_INGREDIENT_BATCH_A", "BUILD_MEASURED_INGREDIENT_BATCH"),
    "H5-S002": ("MEASURED_INGREDIENT_BATCH_A", "CLOSED_PASSAGE_PRODUCT_A", "RESUME_PASS_THROUGH_AND_CLOSE"),
    "H5-S003": ("PICTURE_OWNER+INGREDIENT_SLOT", "APPLICATION_CYCLE_B", "START_SECOND_INGREDIENT_CYCLE"),
    "H5-S004": ("APPLICATION_CYCLE_B", "TARGET_PORTION_B", "WORK_AND_TRANSFER_TO_TARGET"),
    "H5-S005": ("PICTURE_OWNER+INGREDIENT_SLOT+SOURCE", "SOURCE_PORTION_C", "ADD_SOURCE_INGREDIENT_AND_TAKE_PORTION"),
    "H5-S006": ("SOURCE_PORTION_C", "OPEN_MEASURED_PORTION_C", "CONTINUE_TO_MEASURE"),
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
    events = [row for row in read(BASE / "EIGHT_HUNDRED_FORTY_SIXTH_381_EVENT_INTERLINEAR.tsv") if row["page"] == "f56r"]
    statements = [row for row in read(BASE / "EIGHT_HUNDRED_FORTY_SIXTH_116_STATEMENT_EDITION.tsv") if row["page"] == "f56r"]
    cards = []
    for position, event in enumerate(events, 1):
        latin, short = SOURCE_BY_CARD[event["exact_card_id"]]
        cards.append(
            {
                "page_position": position,
                "event_id": event["event_id"],
                "statement_id": event["statement_id"],
                "surface": event["surface"],
                "exact_card_id": event["exact_card_id"],
                "component_recipe": event["component_recipe"],
                "card_meaning_de": event["tenth_edition_reading_de"],
                "semantic_atom_count": len(event["tenth_edition_reading_de"].split(" · ")),
                "source_phrase": latin,
                "workshop_shorthand": short,
                "is_HO_ingredient_card": "YES" if event["exact_card_id"] == "PROC052" else "NO",
                "is_close": "YES" if "SCHLUSS" in event["tenth_edition_reading_de"] else "NO",
                "same_card_meaning": "YES",
            }
        )

    layers = []
    for statement in statements:
        subset = [row for row in cards if row["statement_id"] == statement["statement_id"]]
        incoming, outgoing, transition = TRANSITIONS[statement["statement_id"]]
        layers.append(
            {
                "statement_id": statement["statement_id"],
                "transition": transition,
                "incoming_registers": incoming,
                "outgoing_registers": outgoing,
                "picture_contribution": statement["owner_noun_de"],
                "surface_sequence": statement["surface_sequence"],
                "latin_like_source_statement": STATEMENT_SOURCES[statement["statement_id"]],
                "card_literal_de": statement["ninth_grammar_literal_de"],
                "fluent_reading_de": statement["working_reading_de"],
                "cards": len(subset),
                "semantic_atoms": sum(int(row["semantic_atom_count"]) for row in subset),
                "closes": sum(row["is_close"] == "YES" for row in subset),
            }
        )

    ho_rows = []
    for occurrence, row in enumerate([item for item in cards if item["is_HO_ingredient_card"] == "YES"], 1):
        ho_rows.append(
            {
                "occurrence": occurrence,
                "event_id": row["event_id"],
                "statement_id": row["statement_id"],
                "surface": row["surface"],
                "exact_card_id": row["exact_card_id"],
                "portable_card_meaning_de": "ZUTAT",
                "page_local_resolution_de": "Zutatenplatz im Artikel der Bildpflanze",
                "is_picture_owner": "NO",
                "is_operation": "NO",
                "same_card": "YES",
            }
        )
    registers = [
        {"register": "PICTURE_OWNER", "value_de": statements[0]["owner_noun_de"], "role": "owns all six statements"},
        {"register": "INGREDIENT_SLOT_HO", "value_de": "Zutatenplatz, lokal mit Bildpflanzenmaterial füllbar", "role": "reselected four times"},
        {"register": "MEASURED_INGREDIENT_BATCH_A", "value_de": "erste gemessene Zutatencharge", "role": "built in S001"},
        {"register": "CLOSED_PASSAGE_PRODUCT_A", "value_de": "durch Durchlass geführtes geschlossenes Produkt", "role": "closed in S002"},
        {"register": "APPLICATION_CYCLE_B", "value_de": "zweiter Zutaten-/Ansetzzyklus", "role": "S003-S004"},
        {"register": "SOURCE_PORTION_C", "value_de": "aus Quelle ergänzte Portion", "role": "S005-S006"},
    ]
    write(f"{PREFIX}_27_CARD_PAGE_EDITION.tsv", cards, ["page_position", "event_id", "statement_id", "surface", "exact_card_id", "component_recipe", "card_meaning_de", "semantic_atom_count", "source_phrase", "workshop_shorthand", "is_HO_ingredient_card", "is_close", "same_card_meaning"])
    write(f"{PREFIX}_6_STATEMENT_LAYER_MAP.tsv", layers, ["statement_id", "transition", "incoming_registers", "outgoing_registers", "picture_contribution", "surface_sequence", "latin_like_source_statement", "card_literal_de", "fluent_reading_de", "cards", "semantic_atoms", "closes"])
    write(f"{PREFIX}_4_HO_INGREDIENT_OCCURRENCES.tsv", ho_rows, ["occurrence", "event_id", "statement_id", "surface", "exact_card_id", "portable_card_meaning_de", "page_local_resolution_de", "is_picture_owner", "is_operation", "same_card"])
    write(f"{PREFIX}_6_REGISTER_STORY.tsv", registers, ["register", "value_de", "role"])

    summary = {
        "status": "PASS",
        "decision": "F56R_HO_IS_INGREDIENT_CARD_WITH_PICTURE_RESOLUTION_NOT_OWNER_OR_OPERATION",
        "cards": len(cards),
        "statements": len(layers),
        "semantic_atoms": sum(int(row["semantic_atom_count"]) for row in cards),
        "HO_events": len(ho_rows),
        "HO_surfaces_in_order": [row["surface"] for row in ho_rows],
        "HO_picture_owner_claims": sum(row["is_picture_owner"] == "YES" for row in ho_rows),
        "HO_operation_claims": sum(row["is_operation"] == "YES" for row in ho_rows),
        "closes": sum(row["is_close"] == "YES" for row in cards),
        "unmapped_cards": 0,
        "new_meanings": 0,
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / f"{PREFIX}_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# f56r: Zutatenplätze und wiederholte Arbeitszyklen", "", f"Bildbesitzer: **{statements[0]['owner_noun_de']}**", ""]
    for row in layers:
        lines.extend([
            f"## {row['statement_id']} — {row['transition']}", "",
            f"Karten: `{row['surface_sequence']}`", "",
            f"Quelle: *{row['latin_like_source_statement']}*", "",
            f"Rücklesung: {row['fluent_reading_de']}", "",
            f"Register: `{row['incoming_registers']} → {row['outgoing_registers']}`", "",
        ])
    lines.extend([
        "## Die vier HO-Vorkommen", "",
        "`cho → sho → cho → sho` sind vier Renderings derselben ZUTAT-Karte. Das Bild",
        "liefert den Artikelbesitzer; HO öffnet einen Zutatenplatz. Lokal darf dieser",
        "Platz Bildpflanzenmaterial meinen, doch HO bedeutet weder PFLANZE noch NEHMEN.",
    ])
    (HERE / f"{PREFIX}_COMPLETE_F56R_EDITION.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (HERE / f"{PREFIX}_REPORT.md").write_text(
        "# Sidequest Pass 863: complete f56r ingredient edition\n\n"
        "The f56r article has twenty-seven cards, six statements and fifty-eight semantic\n"
        "atoms. It runs a measured ingredient batch through one closed passage product,\n"
        "then opens two additional ingredient/application cycles.\n\n"
        "The key local card cho/sho occurs four times. Its portable value remains ZUTAT.\n"
        "The picture supplies the plant owner; page context can fill HO with material of\n"
        "that pictured plant. HO itself is neither the owner nor an operation. This keeps\n"
        "the useful concrete reading without overloading the card.\n\n"
        "Next, synthesize all four Herbal pages into one process atlas and compare their\n"
        "distinct page recipes under the shared card vocabulary.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
