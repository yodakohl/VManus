#!/usr/bin/env python3
import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent
EXP = OUT.parents[1]
R137 = EXP / "yolo" / "sidequest_semantic_part_of_speech_composition_hundred_thirty_seventh"
R138 = EXP / "yolo" / "sidequest_semantic_bracket_formula_revision_hundred_thirty_eighth"
R141 = EXP / "yolo" / "sidequest_semantic_ten_mould_phrasebook_hundred_forty_first"

OWNERS = {
    "H1": ("f10r", "Bildpflanze; örtlicher Wurzel-/Materialansatz"),
    "H2": ("f10r", "Bildpflanze; örtlicher Blatt-/Sprossansatz"),
    "H3": ("f11r", "Bildpflanze; örtlicher Blüten-/Blattauszug"),
    "H4": ("f55v", "Bildpflanze; örtlicher Blattauszug und gebundener Rest"),
    "H5": ("f56r", "Bildpflanze; frisches Material und zwei örtliche Zubereitungen"),
    "B1": ("f81v", "gemeinsames zweireihiges Figurenbecken"),
    "B2": ("f82r", "jeweils nächster sichtbarer Becken-/Gerätebesitzer"),
    "B3": ("f83r", "jeweils nächste sichtbare Transfer-/Zustandsstation"),
    "B4": ("f83r", "Hauptpaar mit Tuchanwendung und getrennten Dienstläufen"),
    "B5": ("f83r", "linke figurenlose Dienststation"),
    "B6": ("f83r", "rechte figurenlose Dienststation"),
}

MOULD_REVISIONS = {
    "M01_MATERIAL_PREPARATION": ("OWNER>MATERIAL>PROCESS", "Bildmaterial und örtliche Zubereitung bearbeiten", "Do not force a product unless a product card appears"),
    "M02_SOURCE_SHARE_MEASURE": ("SOURCE>SHARE>[MEASURE]", "davon einen Anteil nehmen; nur mit AIIN/OKAIIN ausdrücklich bemessen", "Measure is optional, not automatic"),
    "M03_TARGET_TRANSFER": ("ITEM>TARGET>TRANSFER>[CLOSE]", "Posten an die vom Besitzer gelieferte Stelle führen", "Body, basin or vessel target comes from owner"),
    "M04_ORDER_CONTINUATION": ("ORDER>LINK>ITEM>ACTION", "Folge oder Fortsetzung im kopierten Ablauf", "Keep exact endpoint position"),
    "M05_STATE_CLOSE": ("ITEM>PROCESS_OR_STATE>[CLOSE]", "örtlichen Prozesszustand ausführen", "Do not default every state to heat"),
    "M06_FILTER_CLEAR_PRODUCT": ("ITEM>FILTER_OR_WASH>[PRODUCT]>[CLOSE]", "waschen, auswringen oder seihen; Klarauszug nur mit product card", "Cloth and water require card or owner"),
    "M07_PAIRED_MEASURE_FRAME": ("ITEM>MEASURE>ITEM", "zwei Posten unter demselben Sollmaß", "Keep both item boundaries"),
    "M08_CARRIED_PREPARATION_FRAME": ("LINK>PREPARATION>LINK", "Fortsetzung mit demselben Ansatz", "Payload may sit inside boundaries"),
    "M09_APPLICATION_FASTEN": ("LOCAL_APPLICATION_OR_STORAGE_WHOLE_CARD", "örtlich anwenden, verwahren oder festbinden", "Three learned variants; not freely interchangeable"),
    "M10_LOCAL_EXACT_CELL": ("LOCAL_WHOLE_CARD_SEQUENCE", "örtliche Ganzzelle aus Vorlage kopieren", "Change owner only"),
}


def read_tsv(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name, rows):
    with (OUT / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def owner_policy(card):
    syn = card["syntactic_type"]
    drawer = card["drawer"]
    if "SOURCE_ANAPHOR" in syn:
        return "INHERITED_SOURCE_OR_PREVIOUS_BATCH"
    if "TARGET" in syn:
        return "VISIBLE_OR_REGISTERED_TARGET"
    if "ITEM_ANAPHOR" in syn:
        return "ACTIVE_WORK_ITEM"
    if "ORDER" in syn or "LINK" in syn:
        return "ACTIVE_SEQUENCE"
    if drawer == "D1_MATERIAL_PRODUCT_VESSEL":
        return "PICTURE_MATERIAL_OR_LOCAL_PREPARATION"
    if drawer == "D2_FILTER_WASH_FLOW":
        return "LOCAL_MEDIUM_PATH_OR_PRODUCT"
    if drawer == "D3_HEAT_SETTLE_STATE":
        return "ACTIVE_BATCH_OR_STATION_STATE"
    if drawer == "D4_TRANSFER_SOURCE_TARGET":
        return "LOCAL_SOURCE_PATH_TARGET"
    if drawer == "D5_QUANTITY_PART_STAGE":
        return "ACTIVE_ITEM_AND_LOCAL_UNIT"
    if drawer == "D6_ORDER_CONTINUATION":
        return "ACTIVE_SEQUENCE"
    if drawer == "D7_APPLICATION_FASTEN_STORE":
        return "VISIBLE_APPLICATION_OR_STORAGE_OWNER"
    if drawer == "D8_LOCAL_OPERATION":
        return "LOCAL_EXEMPLAR_OWNER"
    return "ACTIVE_WORK_ITEM_OR_BATCH"


def forbidden_fill(card):
    drawer = card["drawer"]
    table = {
        "D1_MATERIAL_PRODUCT_VESSEL": "specific species|unwritten ingredient",
        "D2_FILTER_WASH_FLOW": "cloth|water|device unless named",
        "D3_HEAT_SETTLE_STATE": "exact temperature|exact duration",
        "D4_TRANSFER_SOURCE_TARGET": "flow direction|body part|vessel type",
        "D5_QUANTITY_PART_STAGE": "number|unit",
        "D6_ORDER_CONTINUATION": "AND OR TIME semantic label",
        "D7_APPLICATION_FASTEN_STORE": "patient|disease|body part",
        "D8_LOCAL_OPERATION": "domain-specific purpose",
        "ACTIVE_CORE": "specific owner noun not supplied by card",
    }
    return table.get(drawer, table["ACTIVE_CORE"])


def main():
    typed = read_tsv(R137 / "HUNDRED_THIRTY_SEVENTH_173_TYPED_DICTIONARY.tsv")
    cards = read_tsv(R138 / "HUNDRED_THIRTY_EIGHTH_173_FORMULA_REVISED_DICTIONARY.tsv")
    events = read_tsv(R138 / "HUNDRED_THIRTY_EIGHTH_381_FORMULA_REVISED_EVENTS.tsv")
    statements = read_tsv(R138 / "HUNDRED_THIRTY_EIGHTH_116_FORMULA_STATEMENTS.tsv")
    assignments = read_tsv(R141 / "HUNDRED_FORTY_FIRST_116_MOULD_ASSIGNMENTS.tsv")
    moulds = read_tsv(R141 / "HUNDRED_FORTY_FIRST_TEN_PHRASE_MOULDS.tsv")
    type_by_id = {r["master_card_id"]: r["syntactic_type"] for r in typed}
    card_by_id = {r["master_card_id"]: r for r in cards}
    mould_by_statement = {r["statement_id"]: r["mould_id"] for r in assignments}

    layered_cards = []
    for row in cards:
        merged = {**row, "syntactic_type": type_by_id[row["master_card_id"]]}
        layered_cards.append({
            "master_card_id": row["master_card_id"], "master_form": row["master_form"],
            "registered_surfaces": row["registered_surfaces"],
            "portable_card_value_de": row["current_spoken_default_de"],
            "syntactic_type": merged["syntactic_type"],
            "portable_scope": "ACTIVE_CROSS_RECORD" if row["teaching_layer"] != "SPECIALIST_DRAWER_WHOLE_CARD" else "LOCAL_LEARNED_WHOLE_CARD",
            "owner_argument_policy": owner_policy(merged),
            "fluent_do_not_auto_add": forbidden_fill(merged),
            "drawer": row["drawer"], "event_count": row["event_count"], "records": row["records"],
        })

    layered_events = []
    for row in events:
        card = next(c for c in layered_cards if c["master_card_id"] == row["master_card_id"])
        layered_events.append({
            "event_serial": row["event_serial"], "statement_id": row["statement_id"],
            "record_unit_id": row["record_unit_id"], "page": row["page"],
            "visible_surface": row["visible_surface"], "master_card_id": row["master_card_id"],
            "portable_card_value_de": card["portable_card_value_de"],
            "owner_argument_policy": card["owner_argument_policy"],
            "portable_scope": card["portable_scope"],
        })

    revised_moulds = []
    for row in moulds:
        slots, spoken, guard = MOULD_REVISIONS[row["mould_id"]]
        revised_moulds.append({
            "mould_id": row["mould_id"], "revised_slot_mould": slots,
            "revised_spoken_template_de": spoken, "owner_guard": guard,
            "statement_count": row["statement_count"], "event_count": row["event_count"],
            "representative_statement_id": row["representative_statement_id"],
        })

    statement_by_id = {r["statement_id"]: r for r in statements}
    layered_statements = []
    for assignment in assignments:
        sid = assignment["statement_id"]
        source = statement_by_id[sid]
        owner = OWNERS[assignment["record_unit_id"]][1]
        layered_statements.append({
            "statement_id": sid, "record_unit_id": assignment["record_unit_id"], "page": assignment["page"],
            "mould_id": mould_by_statement[sid], "owner_argument_de": owner,
            "portable_literal_chain_de": source["revised_literal_chain_de"],
            "formula_expansion_de": source["formula_expansion_de"],
            "controlled_fluent_de": f"Besitzer: {owner}. Karten: {source['spoken_clause_de']}",
            "owner_terms_are_portable": "NO",
            "automatic_fill_prohibited": "water|patient|disease|body part|species unless card or owner explicitly supplies it",
        })

    owner_rows = [{"record_unit_id": rid, "page": page, "owner_argument_de": owner,
                   "scope": "RECORD_DEFAULT__LOCAL_VISIBLE_RESETS_OVERRIDE"} for rid, (page, owner) in OWNERS.items()]
    write_tsv("HUNDRED_FORTY_FOURTH_173_LAYERED_DICTIONARY.tsv", layered_cards)
    write_tsv("HUNDRED_FORTY_FOURTH_381_LAYERED_EVENTS.tsv", layered_events)
    write_tsv("HUNDRED_FORTY_FOURTH_116_LAYERED_STATEMENTS.tsv", layered_statements)
    write_tsv("HUNDRED_FORTY_FOURTH_TEN_REVISED_MOULDS.tsv", revised_moulds)
    write_tsv("HUNDRED_FORTY_FOURTH_ELEVEN_OWNER_REGISTERS.tsv", owner_rows)

    manual = ["# Aktuelles Schichtwörterbuch und Satzheft", "", "## Drei getrennte Ebenen", "",
              "1. PORTABLE CARD VALUE: the short learned card word or prompt.",
              "2. OWNER ARGUMENT: plant, basin, batch, station, source or target supplied by picture/register.",
              "3. FLUENT EXPANSION: German syntax combining the first two; never fed back into the dictionary.", "",
              "## Zehn revidierte Moulds", ""]
    for row in revised_moulds:
        manual += [f"- {row['mould_id']}: `{row['revised_slot_mould']}` — {row['revised_spoken_template_de']} — {row['owner_guard']}"]
    manual += ["", "## Aktive Karten", ""]
    for row in layered_cards:
        if row["portable_scope"] == "ACTIVE_CROSS_RECORD":
            manual.append(f"- `{row['master_form']}` = {row['portable_card_value_de']} [{row['syntactic_type']}]; owner: {row['owner_argument_policy']}")
    (OUT / "HUNDRED_FORTY_FOURTH_LAYERED_POCKET_MANUAL.md").write_text("\n".join(manual).rstrip() + "\n", encoding="utf-8")

    report = [
        "# Hundertvierundvierzigste Runde: eine sauber geschichtete aktuelle Ausgabe", "",
        "The current prose basis now separates portable card value, owner argument and controlled fluent expansion",
        "for all 173 cards, 381 events and 116 statements. The ten moulds are revised so optional measure, product,",
        "close and owner nouns cannot silently become mandatory card content.", "",
        "M09 is explicitly a local application/storage/fastening family rather than one free syntax. M02 requires",
        "AIIN/OKAIIN before saying measure. Filter cloth, water, patient, disease, body part, exact temperature and",
        "exact units are blocked unless a card or visible owner supplies them. The literal dictionary remains fully",
        "concrete; only its scope is now honest.", "",
        "Next rebuild the complete ten-page 776-group edition on this layered prose basis while leaving the 395",
        "Astro groups as owner-local menu labels and the four WHEN modules optional.",
    ]
    (OUT / "HUNDRED_FORTY_FOURTH_LAYERED_CURRENT_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps({"cards": len(layered_cards), "active_cards": sum(r["portable_scope"] == "ACTIVE_CROSS_RECORD" for r in layered_cards), "events": len(layered_events), "statements": len(layered_statements), "moulds": len(revised_moulds), "owner_registers": len(owner_rows)}, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
