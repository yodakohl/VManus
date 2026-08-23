#!/usr/bin/env python3
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


OUT = Path(__file__).resolve().parent
EXP = OUT.parents[1]
R137 = EXP / "yolo" / "sidequest_semantic_part_of_speech_composition_hundred_thirty_seventh"
R138 = EXP / "yolo" / "sidequest_semantic_bracket_formula_revision_hundred_thirty_eighth"

MOULDS = [
    ("M01_MATERIAL_PREPARATION", "OWNER>MATERIAL>PROCESS>PRODUCT", "Bildmaterial nehmen, bearbeiten und als Ansatz/Produkt weitergeben", "replace picture owner or one material card"),
    ("M02_SOURCE_SHARE_MEASURE", "SOURCE>SHARE>MEASURE", "davon einen Anteil nehmen und bemessen", "replace only local source or share card"),
    ("M03_TARGET_TRANSFER", "ITEM>TARGET>TRANSFER>CLOSE", "Posten dorthin überführen oder abführen und schließen", "preserve target before terminal transfer"),
    ("M04_ORDER_CONTINUATION", "ORDER>LINK>ITEM>ACTION", "Folgeposten oder Fortsetzung in den nächsten Arbeitsgang tragen", "preserve next/continue relation and local endpoint"),
    ("M05_STATE_CLOSE", "ITEM>PROCESS>STATE>CLOSE", "Posten bearbeiten, halten, wärmen oder absetzen und schließen", "replace state card only inside same duration/close slot"),
    ("M06_FILTER_CLEAR_PRODUCT", "ITEM>FILTER>PRODUCT>CLOSE", "auswringen, seihen oder waschen und den Klarauszug gewinnen", "replace filter path but retain product/close order"),
    ("M07_PAIRED_MEASURE_FRAME", "ITEM>MEASURE>ITEM", "zwei Posten unter demselben Sollmaß", "payload may sit inside but both item boundaries remain"),
    ("M08_CARRIED_PREPARATION_FRAME", "LINK>PREPARATION>LINK", "Fortsetzung mit demselben Ansatz", "local payload may sit inside continuation boundaries"),
    ("M09_APPLICATION_FASTEN", "SHARE>TARGET>APPLICATION>CLOSE", "Anteil an Zielstelle einsetzen, auflegen oder festbinden", "use one or more cells; never fuse a missing endpoint"),
    ("M10_LOCAL_EXACT_CELL", "LOCAL_WHOLE_CARD_SEQUENCE", "eine vollständig gelernte lokale Arbeitszelle", "copy exact order; change only owner label"),
]

F1 = {"H2-S001", "B3-S003", "B3-S021"}
F2 = {"H2-S002", "B1-S002"}

REPRESENTATIVES = {
    "M01_MATERIAL_PREPARATION": "H1-S001",
    "M02_SOURCE_SHARE_MEASURE": "B2-S011",
    "M03_TARGET_TRANSFER": "B3-S006",
    "M04_ORDER_CONTINUATION": "B4-S003",
    "M05_STATE_CLOSE": "B4-S008",
    "M06_FILTER_CLEAR_PRODUCT": "H3-S001",
    "M07_PAIRED_MEASURE_FRAME": "B3-S003",
    "M08_CARRIED_PREPARATION_FRAME": "H2-S002",
    "M09_APPLICATION_FASTEN": "H5-S005",
    "M10_LOCAL_EXACT_CELL": "B1-S011",
}


def read_tsv(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name, rows):
    with (OUT / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def broad_type(syntactic_type):
    if "SOURCE" in syntactic_type:
        return "SOURCE"
    if "TARGET" in syntactic_type:
        return "TARGET"
    if "QUANTITY" in syntactic_type or "MEASURE" in syntactic_type:
        return "MEASURE"
    if "ORDER" in syntactic_type:
        return "ORDER"
    if "CONTINUATION" in syntactic_type or "LINK" in syntactic_type:
        return "LINK"
    if "STATE" in syntactic_type:
        return "STATE"
    if "OBJECT" in syntactic_type or "PREPARATION" in syntactic_type or "ITEM" in syntactic_type:
        return "OBJECT"
    if "TRANSFER" in syntactic_type or "ADDRESS" in syntactic_type:
        return "TRANSFER"
    if "PROCESS" in syntactic_type or "ACTION" in syntactic_type:
        return "ACTION"
    return "LOCAL"


def collapse(seq):
    out = []
    for x in seq:
        if not out or out[-1] != x:
            out.append(x)
    return ">".join(out)


def choose_mould(sid, group):
    ids = {r["master_card_id"] for r in group}
    drawers = {r["drawer"] for r in group}
    if sid in F1:
        return "M07_PAIRED_MEASURE_FRAME"
    if sid in F2:
        return "M08_CARRIED_PREPARATION_FRAME"
    if "D7_APPLICATION_FASTEN_STORE" in drawers:
        return "M09_APPLICATION_FASTEN"
    if "D2_FILTER_WASH_FLOW" in drawers or "MC119" in ids:
        return "M06_FILTER_CLEAR_PRODUCT"
    if group[0]["record_unit_id"].startswith("H") and "D1_MATERIAL_PRODUCT_VESSEL" in drawers:
        return "M01_MATERIAL_PREPARATION"
    if ids & {"MC055", "MC142"} and ids & {"MC039", "MC086", "MC105", "MC017", "MC120"}:
        return "M02_SOURCE_SHARE_MEASURE"
    if "D6_ORDER_CONTINUATION" in drawers or ids & {"MC013", "MC060", "MC093", "MC153", "MC171"}:
        return "M04_ORDER_CONTINUATION"
    if "D4_TRANSFER_SOURCE_TARGET" in drawers or ids & {"MC040", "MC074", "MC154", "MC155"}:
        return "M03_TARGET_TRANSFER"
    if "D3_HEAT_SETTLE_STATE" in drawers or ids & {"MC002", "MC007", "MC019", "MC032", "MC045", "MC082", "MC083", "MC128", "MC147", "MC161"}:
        return "M05_STATE_CLOSE"
    return "M10_LOCAL_EXACT_CELL"


def main():
    typed_cards = read_tsv(R137 / "HUNDRED_THIRTY_SEVENTH_173_TYPED_DICTIONARY.tsv")
    events = read_tsv(R138 / "HUNDRED_THIRTY_EIGHTH_381_FORMULA_REVISED_EVENTS.tsv")
    statements = read_tsv(R138 / "HUNDRED_THIRTY_EIGHTH_116_FORMULA_STATEMENTS.tsv")
    type_by_id = {r["master_card_id"]: r["syntactic_type"] for r in typed_cards}
    statement_by_id = {r["statement_id"]: r for r in statements}
    by_statement = defaultdict(list)
    for row in events:
        by_statement[row["statement_id"]].append(row)

    assignments = []
    counts = Counter()
    for sid, group in by_statement.items():
        mould = choose_mould(sid, group)
        counts[mould] += 1
        broad = [broad_type(type_by_id[r["master_card_id"]]) for r in group]
        assignments.append({
            "statement_id": sid, "record_unit_id": group[0]["record_unit_id"], "page": group[0]["page"],
            "mould_id": mould, "event_count": str(len(group)),
            "visible_surface_sequence": " ".join(r["visible_surface"] for r in group),
            "broad_slot_signature": collapse(broad),
            "literal_clause_de": statement_by_id[sid]["spoken_clause_de"],
            "formula_expansion_de": statement_by_id[sid]["formula_expansion_de"],
        })

    templates = []
    for mould_id, slots, speech, substitution in MOULDS:
        group = [r for r in assignments if r["mould_id"] == mould_id]
        representative = next(r for r in group if r["statement_id"] == REPRESENTATIVES[mould_id])
        templates.append({
            "mould_id": mould_id, "source_slot_mould": slots, "spoken_template_de": speech,
            "substitution_rule": substitution, "statement_count": str(len(group)),
            "event_count": str(sum(int(r["event_count"]) for r in group)),
            "representative_statement_id": representative["statement_id"],
            "representative_visible_sequence": representative["visible_surface_sequence"],
            "representative_literal_de": representative["literal_clause_de"],
        })

    write_tsv("HUNDRED_FORTY_FIRST_TEN_PHRASE_MOULDS.tsv", templates)
    write_tsv("HUNDRED_FORTY_FIRST_116_MOULD_ASSIGNMENTS.tsv", assignments)

    phrasebook = ["# Zehn Satzformen für die Werkstatt", "", "Use the mould before choosing local cards. A mould",
                  "is a copied clause habit, not a claim about a natural-language sentence.", ""]
    for row in templates:
        phrasebook += [f"## {row['mould_id']} · {row['statement_count']} Aussagen / {row['event_count']} Karten", "",
                       f"Slots: `{row['source_slot_mould']}`", "", f"Gesprochen: {row['spoken_template_de']}", "",
                       f"Austauschregel: {row['substitution_rule']}", "",
                       f"Kurze echte Vorlage {row['representative_statement_id']}: `{row['representative_visible_sequence']}`", "",
                       row["representative_literal_de"], ""]
    phrasebook += ["## Lehrfolge", "", "OWNER bestimmen → Mould wählen → gemeinsame Karten setzen → lokale Ganzkarte",
                   "einsetzen → Schlusslage bewahren → Handform schreiben → zur Mould zurücklesen."]
    (OUT / "HUNDRED_FORTY_FIRST_TEN_MOULD_PHRASEBOOK.md").write_text("\n".join(phrasebook).rstrip() + "\n", encoding="utf-8")

    report = [
        "# Hunderteinundvierzigste Runde: 116 Aussagen werden zehn Satzformen", "",
        "Every prose statement is assigned to one of ten apprentice moulds. The largest are target/transfer,",
        "state/close and order/continuation; together they explain the repetitive Biological cells. Herbal",
        "material/preparation remains a smaller but distinct article mould. Five statements instantiate the two",
        "bracket frames. Thirteen statements remain exact local cells and must be copied as wholes.", "",
        "The phrasebook makes the system learnable without pretending that all 173 cards decompose. An apprentice",
        "chooses a mould, fills the visible owner and one local slot, preserves endpoint position, then selects a",
        "hand form. Next make a readable apprenticeship lesson for each of the ten moulds and test it by rewriting",
        "one existing statement into a different owner while retaining the exact mould.",
    ]
    (OUT / "HUNDRED_FORTY_FIRST_TEN_MOULD_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps({"moulds": len(templates), "statements": len(assignments), "counts": dict(sorted(counts.items())), "events": sum(int(r["event_count"]) for r in assignments)}, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
