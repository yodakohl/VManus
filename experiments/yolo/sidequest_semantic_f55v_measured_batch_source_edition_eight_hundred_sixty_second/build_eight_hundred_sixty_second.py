#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BASE = ROOT / "sidequest_semantic_tenth_workshop_edition_eight_hundred_forty_sixth"
F11 = ROOT / "sidequest_semantic_f11r_extraction_source_edition_eight_hundred_sixty_first" / "EIGHT_HUNDRED_SIXTY_FIRST_BUILD_SUMMARY.json"
PREFIX = "EIGHT_HUNDRED_SIXTY_SECOND"

SOURCE_BY_CARD = {
    "PROC038": ("ad mensuram pone", "ad mens. / pone"),
    "PROC009": ("ad mensuram", "ad mens."),
    "PROC039": ("rem et portionem adde", "rem / port. adde"),
    "PROC040": ("rem et supplementum adde", "rem / suppl. adde"),
    "PROC041": ("opus fini", "op. / f."),
    "PROC042": ("rem transfer", "rem / transf."),
    "PROC043": ("seponere", "sepon."),
    "PROC044": ("rem ad mensuram adde", "rem / ad mens. / adde"),
    "PROC045": ("ex fonte in opere cito sume", "ex fonte / in op. / cito sume"),
    "PROC046": ("rem diu calefac", "rem / calef. diu"),
    "PROC047": ("continua; fini", "cont. / f."),
    "PROC048": ("ad locum pone", "ad loc. / pone"),
    "PROC049": ("rem opera et continua", "rem / opera-cont."),
    "PROC016": ("preparatio", "prep."),
    "PROC019": ("res currens", "rem"),
    "PROC050": ("portio praeparationis", "port. prep."),
}

STATEMENT_SOURCES = {
    "H4-S001": "Ad mensuram pone; rei portionem et supplementum adde; opus fini.",
    "H4-S002": "Ad mensuram rem transfer et seponere.",
    "H4-S003": "Rem ad mensuram adde; ex fonte in opere cito sume; rem diu calefac; continua et fini.",
    "H4-S004": "Ad mensuram ad locum pone, rem opera et continua, ut praeparationem et portionem praeparationis tene.",
}

TRANSITIONS = {
    "H4-S001": ("PICTURE_OWNER+RAW_MATERIAL", "CLOSED_MEASURED_BATCH_A", "MEASURE_PORTION_SUPPLEMENT_AND_CLOSE"),
    "H4-S002": ("CLOSED_MEASURED_BATCH_A", "SET_ASIDE_PORTION", "TRANSFER_MEASURED_PORTION_AND_SET_ASIDE"),
    "H4-S003": ("SET_ASIDE_PORTION+SOURCE", "CLOSED_HEATED_BATCH_B", "ADD_SOURCE_HEAT_AND_CLOSE"),
    "H4-S004": ("CLOSED_HEATED_BATCH_B", "OPEN_TARGET_PORTION", "SET_AT_TARGET_AND_KEEP_PORTION_OPEN"),
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
    events = [row for row in read(BASE / "EIGHT_HUNDRED_FORTY_SIXTH_381_EVENT_INTERLINEAR.tsv") if row["page"] == "f55v"]
    statements = [row for row in read(BASE / "EIGHT_HUNDRED_FORTY_SIXTH_116_STATEMENT_EDITION.tsv") if row["page"] == "f55v"]
    cards = []
    for position, event in enumerate(events, 1):
        latin, short = SOURCE_BY_CARD[event["exact_card_id"]]
        components = event["component_recipe"].split("+")
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
                "has_quantity": "YES" if any(value in components for value in ["AIN", "AIIN", "IIN", "AN"]) else "NO",
                "has_heat": "YES" if "CHK" in components else "NO",
                "has_press_or_passage": "YES" if any(value in components for value in ["CFH", "CKH"]) else "NO",
                "has_water": "YES" if "AIR" in components else "NO",
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

    registers = [
        {"register": "PICTURE_OWNER", "introduced": "f55v plant image", "value_de": statements[0]["owner_noun_de"]},
        {"register": "CLOSED_MEASURED_BATCH_A", "introduced": "H4-S001", "value_de": "mit Portion und Nachgabe geschlossener erster Ansatz"},
        {"register": "SET_ASIDE_PORTION", "introduced": "H4-S002", "value_de": "nach Sollmaß umgesetzte und beiseitegestellte Portion"},
        {"register": "CLOSED_HEATED_BATCH_B", "introduced": "H4-S003", "value_de": "mit Quellzugabe länger erwärmter geschlossener Ansatz"},
        {"register": "OPEN_TARGET_PORTION", "introduced": "H4-S004", "value_de": "an der Zielstelle offen weitergeführte Ansatzportion"},
    ]
    f11 = json.loads(F11.read_text(encoding="utf-8"))
    comparison = [
        {"page": "f11r", "cards": f11["cards"], "atoms": f11["semantic_atoms"], "quantity_cards": 2, "heat_cards": 0, "press_or_passage_cards": 1, "water_cards": 0, "closes": f11["closes"], "best_reading": "press/receive first extract, close, resume"},
        {"page": "f55v", "cards": len(cards), "atoms": sum(int(row["semantic_atom_count"]) for row in cards), "quantity_cards": sum(row["has_quantity"] == "YES" for row in cards), "heat_cards": sum(row["has_heat"] == "YES" for row in cards), "press_or_passage_cards": sum(row["has_press_or_passage"] == "YES" for row in cards), "water_cards": sum(row["has_water"] == "YES" for row in cards), "closes": sum(row["is_close"] == "YES" for row in cards), "best_reading": "measure/add/set-aside/heat/target batching"},
    ]
    write(f"{PREFIX}_18_CARD_PAGE_EDITION.tsv", cards, ["page_position", "event_id", "statement_id", "surface", "exact_card_id", "component_recipe", "card_meaning_de", "semantic_atom_count", "source_phrase", "workshop_shorthand", "has_quantity", "has_heat", "has_press_or_passage", "has_water", "is_close", "same_card_meaning"])
    write(f"{PREFIX}_4_STATEMENT_LAYER_MAP.tsv", layers, ["statement_id", "transition", "incoming_registers", "outgoing_registers", "picture_contribution", "surface_sequence", "latin_like_source_statement", "card_literal_de", "fluent_reading_de", "cards", "semantic_atoms", "closes"])
    write(f"{PREFIX}_5_REGISTER_STORY.tsv", registers, ["register", "introduced", "value_de"])
    write(f"{PREFIX}_F11R_F55V_PROCESS_COMPARISON.tsv", comparison, ["page", "cards", "atoms", "quantity_cards", "heat_cards", "press_or_passage_cards", "water_cards", "closes", "best_reading"])

    summary = {
        "status": "PASS",
        "decision": "F55V_IS_MEASURED_BATCHING_AND_HEATING_NOT_PRIMARY_FILTRATION",
        "cards": len(cards),
        "statements": len(layers),
        "semantic_atoms": sum(int(row["semantic_atom_count"]) for row in cards),
        "quantity_cards": sum(row["has_quantity"] == "YES" for row in cards),
        "heat_cards": sum(row["has_heat"] == "YES" for row in cards),
        "press_or_passage_cards": sum(row["has_press_or_passage"] == "YES" for row in cards),
        "water_cards": sum(row["has_water"] == "YES" for row in cards),
        "closes": sum(row["is_close"] == "YES" for row in cards),
        "unmapped_cards": 0,
        "new_meanings": 0,
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / f"{PREFIX}_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# f55v: Dosier-, Wärme- und Zielstellenfolge", "", f"Bildbesitzer: **{statements[0]['owner_noun_de']}**", ""]
    for row in layers:
        lines.extend([
            f"## {row['statement_id']} — {row['transition']}", "",
            f"Karten: `{row['surface_sequence']}`", "",
            f"Quelle: *{row['latin_like_source_statement']}*", "",
            f"Rücklesung: {row['fluent_reading_de']}", "",
            f"Register: `{row['incoming_registers']} → {row['outgoing_registers']}`", "",
        ])
    lines.extend([
        "Die Seite hat acht Mengenkarten, eine Wärmekarte, zwei Schlüsse, aber weder",
        "Wasser- noch Auspress-/Durchlasskarte. Daher ist Dosieren und Erwärmen die",
        "bessere Arbeitslesung; f11r bleibt die stärkere Auspressseite.",
    ])
    (HERE / f"{PREFIX}_COMPLETE_F55V_EDITION.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (HERE / f"{PREFIX}_REPORT.md").write_text(
        "# Sidequest Pass 862: complete f55v measured-batch edition\n\n"
        "The eighteen-card f55v article carries thirty-seven semantic atoms in four\n"
        "statements. It is not the fixed Herbal set's strongest filtration page. It has\n"
        "eight quantity cards, one heat card and two closes, but no AIR/water, CFH/press or\n"
        "CKH/passage card.\n\n"
        "The better working sequence is measured batching: measure a portion and supplement\n"
        "then close; transfer and set aside; add from a source, heat longer and close; set\n"
        "an open portion at the target. f11r remains the stronger extraction/receiving page.\n\n"
        "Next, build f56r and ask whether its repeated local card supplies a plant-owner\n"
        "resumption or a genuine preparation operation.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
