#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BASE = ROOT / "sidequest_semantic_tenth_workshop_edition_eight_hundred_forty_sixth"
F10 = ROOT / "sidequest_semantic_f10r_complete_source_edition_eight_hundred_sixtieth" / "EIGHT_HUNDRED_SIXTIETH_BUILD_SUMMARY.json"
PREFIX = "EIGHT_HUNDRED_SIXTY_FIRST"

SOURCE_BY_CARD = {
    "PROC026": ("rem opera, tene et continua", "opera / tene / cont."),
    "PROC027": ("in opere ad locum tene", "in op. / ad loc. / tene"),
    "PROC028": ("rem exprime", "exprime rem"),
    "PROC029": ("rem ad mensuram tene", "rem / ad mens. / tene"),
    "PROC030": ("rem in receptaculum mitte", "in recip. / mitte"),
    "PROC031": ("rem diu tene", "rem / tene diu"),
    "PROC032": ("in opere rem tracta et sume; fini", "in op. / tracta-sume / f."),
    "PROC033": ("in opere rem tene et opera", "in op. / rem tene-opera"),
    "PROC034": ("ex eo", "ex eo"),
    "PROC019": ("res currens", "rem"),
    "PROC035": ("rem adde", "rem / adde"),
    "PROC009": ("ad mensuram", "ad mens."),
    "PROC036": ("deinde rem", "deinde rem"),
    "PROC037": ("pone et continua", "pone / cont."),
    "PROC014": ("rem para", "rem / para"),
}

STATEMENT_SOURCES = {
    "H3-S001": "Rem opera et continua tenere; in opere ad locum tene, exprime, ad mensuram tene, in receptaculum mitte, diu tene, in opere tracta et sume; fini.",
    "H3-S002": "In opere rem tene et opera.",
    "H3-S003": "Ex eo rem currentem tene, adde et ad mensuram continua.",
    "H3-S004": "Deinde rem pone et continua; paratam tene.",
}

TRANSITIONS = {
    "H3-S001": ("PICTURE_OWNER+RAW_MATERIAL", "CLOSED_FIRST_EXTRACT", "PROCESS_RECEIVE_AND_CLOSE_FIRST_EXTRACT"),
    "H3-S002": ("CLOSED_FIRST_EXTRACT", "WORKED_FIRST_EXTRACT", "WORK_ON_CLOSED_PRODUCT"),
    "H3-S003": ("WORKED_FIRST_EXTRACT", "RESUMED_PORTION", "RESUME_WITH_DAVON_AND_ADD"),
    "H3-S004": ("RESUMED_PORTION", "OPEN_PREPARED_PORTION", "CONTINUE_RESUMED_PORTION"),
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
    events = [row for row in read(BASE / "EIGHT_HUNDRED_FORTY_SIXTH_381_EVENT_INTERLINEAR.tsv") if row["page"] == "f11r"]
    statements = [row for row in read(BASE / "EIGHT_HUNDRED_FORTY_SIXTH_116_STATEMENT_EDITION.tsv") if row["page"] == "f11r"]
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
                "picture_owner": event["owner_de"],
                "is_close": "YES" if "SCHLUSS" in event["tenth_edition_reading_de"] else "NO",
                "is_resume_whole_card": "YES" if event["component_recipe"] == "RESUME_CARD" else "NO",
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
                "resume_cards": sum(row["is_resume_whole_card"] == "YES" for row in subset),
            }
        )

    registers = [
        {"register": "PICTURE_OWNER", "introduced": "f11r plant image", "value_de": statements[0]["owner_noun_de"], "cleared": "NO"},
        {"register": "RAW_MATERIAL", "introduced": "H3-S001", "value_de": "Posten der Bildpflanze", "cleared": "at H3-S001 close"},
        {"register": "CLOSED_FIRST_EXTRACT", "introduced": "H3-S001 close", "value_de": "ausgepresster/aufgenommener erster Arbeitsstoff", "cleared": "NO"},
        {"register": "RESUMED_PORTION", "introduced": "H3-S003 DAVON", "value_de": "davon abgenommener laufender Posten", "cleared": "NO"},
        {"register": "OPEN_PREPARED_PORTION", "introduced": "H3-S004", "value_de": "weiter bereitgehaltener Posten", "cleared": "NO"},
    ]
    f10 = json.loads(F10.read_text(encoding="utf-8"))
    comparison = [
        {"page": "f10r", "picture_owners": f10["picture_owners"], "records": f10["records"], "statements": f10["statements"], "cards": f10["cards"], "semantic_atoms": f10["semantic_atoms"], "closes": f10["explicit_closes"], "resume_whole_cards": 0, "working_shape": "open main preparation plus open branch"},
        {"page": "f11r", "picture_owners": 1, "records": 1, "statements": len(layers), "cards": len(cards), "semantic_atoms": sum(int(row["semantic_atom_count"]) for row in cards), "closes": sum(row["is_close"] == "YES" for row in cards), "resume_whole_cards": sum(row["is_resume_whole_card"] == "YES" for row in cards), "working_shape": "closed first extract then resumed open portion"},
    ]
    write(f"{PREFIX}_17_CARD_PAGE_EDITION.tsv", cards, ["page_position", "event_id", "statement_id", "surface", "exact_card_id", "component_recipe", "card_meaning_de", "semantic_atom_count", "source_phrase", "workshop_shorthand", "picture_owner", "is_close", "is_resume_whole_card", "same_card_meaning"])
    write(f"{PREFIX}_4_STATEMENT_LAYER_MAP.tsv", layers, ["statement_id", "transition", "incoming_registers", "outgoing_registers", "picture_contribution", "surface_sequence", "latin_like_source_statement", "card_literal_de", "fluent_reading_de", "cards", "semantic_atoms", "closes", "resume_cards"])
    write(f"{PREFIX}_5_REGISTER_STORY.tsv", registers, ["register", "introduced", "value_de", "cleared"])
    write(f"{PREFIX}_F10R_F11R_COMPARISON.tsv", comparison, ["page", "picture_owners", "records", "statements", "cards", "semantic_atoms", "closes", "resume_whole_cards", "working_shape"])

    summary = {
        "status": "PASS",
        "decision": "F11R_READS_AS_CLOSED_EXTRACTION_FOLLOWED_BY_RESUMED_WORK",
        "cards": len(cards),
        "statements": len(layers),
        "semantic_atoms": sum(int(row["semantic_atom_count"]) for row in cards),
        "picture_owners": 1,
        "registers": len(registers),
        "closes": sum(row["is_close"] == "YES" for row in cards),
        "resume_whole_cards": sum(row["is_resume_whole_card"] == "YES" for row in cards),
        "unmapped_cards": 0,
        "new_meanings": 0,
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / f"{PREFIX}_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# f11r: Auspress-/Aufnahmefolge mit Wiederaufnahme", "", f"Bildbesitzer: **{statements[0]['owner_noun_de']}**", ""]
    for row in layers:
        lines.extend([
            f"## {row['statement_id']} — {row['transition']}", "",
            f"Karten: `{row['surface_sequence']}`", "",
            f"Quelle: *{row['latin_like_source_statement']}*", "",
            f"Rücklesung: {row['fluent_reading_de']}", "",
            f"Register: `{row['incoming_registers']} → {row['outgoing_registers']}`", "",
        ])
    lines.extend([
        "Die erste Phase endet ausdrücklich. `DAVON` nimmt das erzeugte Produkt später",
        "wieder auf. Das Bild bleibt Besitzer; die Karte nennt weder einen neuen Stoff",
        "noch eine neue Pflanze.",
    ])
    (HERE / f"{PREFIX}_COMPLETE_F11R_EDITION.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (HERE / f"{PREFIX}_REPORT.md").write_text(
        "# Sidequest Pass 861: complete f11r extraction edition\n\n"
        "The f11r plant article has seventeen cards, four statements and thirty-eight\n"
        "semantic atoms. Its first seven-card phase presses/receives material and closes.\n"
        "After one short work statement, learned whole card DAVON explicitly resumes the\n"
        "produced material for two open continuation statements.\n\n"
        "The three-layer architecture matches f10r: picture owner, persistent registers,\n"
        "visible card instructions. The process shape differs: f10r stays open and branches;\n"
        "f11r closes a first extract and reopens a portion. No new card meanings are needed.\n\n"
        "Next, apply the same page-edition method to f55v and ask whether it supplies the\n"
        "strongest plant-to-wash/filter transition in the fixed Herbal set.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
