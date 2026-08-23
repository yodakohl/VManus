#!/usr/bin/env python3
import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R147 = ROOT / "experiments/yolo/sidequest_semantic_recurrent_specialist_promotion_hundred_forty_seventh"
R150 = ROOT / "experiments/yolo/sidequest_semantic_eleven_record_source_book_hundred_fiftieth"
R151 = ROOT / "experiments/yolo/sidequest_semantic_open_carry_registers_hundred_fifty_first"
HERBAL_RECORDS = ["H1", "H2", "H3", "H4", "H5"]

ATOMIC = {
    "chokcheo": "Auszug einsetzen", "chodaly": "Zielzugabe", "chair": "Zuguss",
    "qokokchy": "erneut einsetzen", "oltchy": "Folgebereitung", "oykchor": "Arbeitsansatz",
    "tchody": "Endzugabe; Schluss", "okchol": "Weiterverarbeitung", "ykain": "erste Portion",
    "kaiiin": "Arbeitsstufe", "schoal": "Sudansatz", "otol": "Fortgang",
    "shoyty": "Zugabeteil", "sotodan": "Folgeanwendung", "otytchol": "Folgeteil",
    "dchey": "Grundteil", "orain": "Bereitungsanteil", "ycheor": "Auszugsansatz",
    "kchal": "Zielbearbeitung", "cheoar": "Quellauszug", "chodaiin": "Zugabemaß",
    "kchol": "Weiterverarbeitung", "tshol": "Kochgut", "cheeckhody": "Langpassage; Schluss",
    "ody": "Abkühlen", "keol": "Kurzfortsetzung", "qotchy": "Folgeposten",
    "etyd": "Kurzteil", "shfydaiin": "Stehzeit", "sh": "Halten",
    "qoctholy": "Folgeposten", "kchy": "Bearbeiten", "kchey": "Kurzbearbeitung",
    "chochor": "Zugabeansatz", "cfhy": "Auswringen", "choy": "Zugabeposten",
    "kchoar": "Quellauszug", "ykan": "zweite Portion", "cphy": "Nachseihen",
    "cthoor": "Vorbereitung", "os": "Aufnahmegefäß", "talam": "Verwahrort",
    "qotchol": "Weitergang", "cthaiin": "Sollvorbereitung", "ykaiin": "Sollportion",
}
TYPE_REVISIONS = {
    "chokcheo": "LEARNED_LOCAL_ACTION",
    "etyd": "LEARNED_QUANTITY_OR_STAGE",
    "shfydaiin": "LEARNED_QUANTITY_OR_STAGE",
    "talam": "LEARNED_TRANSFER_OR_ADDRESS",
}


def read_tsv(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name, rows):
    rows = list(rows)
    with (OUT / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    cards = read_tsv(R147 / "HUNDRED_FORTY_SEVENTH_173_PROMOTED_DICTIONARY.tsv")
    events = read_tsv(R147 / "HUNDRED_FORTY_SEVENTH_381_PROMOTED_EVENTS.tsv")
    carry_clauses = read_tsv(R151 / "HUNDRED_FIFTY_FIRST_116_CARRY_AWARE_CLAUSES.tsv")
    audit = []
    revised_cards = []
    for row in cards:
        new = dict(row)
        if row["master_form"] in ATOMIC:
            new["portable_card_value_de"] = ATOMIC[row["master_form"]]
            if row["master_form"] in TYPE_REVISIONS:
                new["syntactic_type"] = TYPE_REVISIONS[row["master_form"]]
            audit.append({
                "master_card_id": row["master_card_id"], "master_form": row["master_form"],
                "records": row["records"], "event_count": row["event_count"],
                "old_composite_default_de": row["portable_card_value_de"],
                "atomic_whole_card_default_de": new["portable_card_value_de"],
                "old_syntactic_type": row["syntactic_type"], "new_syntactic_type": new["syntactic_type"],
                "teaching_rule": "MEMORIZE_AS_ONE_HERBAL_CARD__DO_NOT_DECOMPOSE",
            })
        revised_cards.append(new)
    write_tsv("HUNDRED_FIFTY_FOURTH_45_HERBAL_ATOMIC_CARDS.tsv", audit)
    write_tsv("HUNDRED_FIFTY_FOURTH_173_REVISED_DICTIONARY.tsv", revised_cards)

    card_by_id = {row["master_card_id"]: row for row in revised_cards}
    revised_events = []
    for row in events:
        new = dict(row)
        card = card_by_id[row["master_card_id"]]
        new["portable_card_value_de"] = card["portable_card_value_de"]
        new["owner_argument_policy"] = card["owner_argument_policy"]
        new["portable_scope"] = card["portable_scope"]
        revised_events.append(new)
    write_tsv("HUNDRED_FIFTY_FOURTH_381_REVISED_EVENTS.tsv", revised_events)

    by_statement = defaultdict(list)
    for row in revised_events:
        by_statement[row["statement_id"]].append(row["portable_card_value_de"])
    herbal_clause_rows = []
    carry_by_id = {row["statement_id"]: row for row in carry_clauses}
    for sid, values in by_statement.items():
        rid = sid.split("-")[0]
        if rid not in HERBAL_RECORDS:
            continue
        source = carry_by_id[sid]
        spoken = " — ".join(value.replace(" · ", " ") for value in values)
        if source["terminal_status"] == "TERMINAL" and "Schluss" not in spoken:
            spoken += "; Schluss"
        herbal_clause_rows.append({
            "statement_id": sid, "record_unit_id": rid, "page": source["page"],
            "connective_de": source["connective_de"], "owner_trace": source["owner_trace"],
            "atomic_card_chain_de": " | ".join(values),
            "atomic_apprentice_clause_de": f"{source['connective_de']} {spoken}.",
            "dictionary_layer": "SHARED_DECK_PLUS_ATOMIC_HERBAL_NOMENCLATOR",
        })
    write_tsv("HUNDRED_FIFTY_FOURTH_19_ATOMIC_HERBAL_CLAUSES.tsv", herbal_clause_rows)

    by_record = defaultdict(list)
    for row in herbal_clause_rows:
        by_record[row["record_unit_id"]].append(row)
    book = ["# Fünf Herbal-Records mit atomarem Ganzkarten-Nomenklator", "",
            "The forty-five local Herbal cards are spoken as indivisible learned words. Their older component",
            "glosses remain in the audit but are no longer recited as productive composition.", ""]
    record_rows = []
    for rid in HERBAL_RECORDS:
        rows = by_record[rid]
        text = " ".join(row["atomic_apprentice_clause_de"] for row in rows)
        record_rows.append({
            "record_unit_id": rid, "page": rows[0]["page"], "statement_count": str(len(rows)),
            "continuous_atomic_recitation_de": text,
        })
        book += [f"## {rid} · {rows[0]['page']}", "", text, ""]
    write_tsv("HUNDRED_FIFTY_FOURTH_FIVE_ATOMIC_HERBAL_RECORDS.tsv", record_rows)
    (OUT / "HUNDRED_FIFTY_FOURTH_ATOMIC_HERBAL_BOOK.md").write_text("\n".join(book).rstrip() + "\n", encoding="utf-8")

    report = [
        "# Hundertvierundfünfzigste Runde: der Herbal-Nomenklator wird atomar", "",
        "All 45 local Herbal card types are now taught as short indivisible whole words rather than miniature",
        "sentences assembled from uncertain parts. Examples are VORBEREITUNG, AUFNAHMEGEFÄSS, ZUGUSS, FOLGETEIL,",
        "AUSZUGSANSATZ, SOLLVORBEREITUNG, KOCHGUT, SUDANSATZ, STEHZEIT, NACHSEIHEN, QUELLAUSZUG and VERWAHRORT.", "",
        "This greatly improves the five complete Herbal recitations while remaining faithful to the mixed system",
        "we were seeking: a small productive deck plus learned technical whole words. It also avoids pretending",
        "that visible substrings inside a singleton card independently mean ingredient, target, source or measure.", "",
        "Next perform the same atomic whole-card pass over the 81 Biological local cards, using station function",
        "and complete clause position to choose one short operation, state, path or address value for each.",
    ]
    (OUT / "HUNDRED_FIFTY_FOURTH_HERBAL_ATOMIC_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps({
        "cards": len(revised_cards), "atomic_herbal_cards": len(audit),
        "revised_events": sum(int(row["event_count"]) for row in audit),
        "events": len(revised_events), "herbal_statements": len(herbal_clause_rows), "herbal_records": len(record_rows),
        "old_composite_values": sum(" · " in row["old_composite_default_de"] for row in audit),
        "new_composite_values": sum(" · " in row["atomic_whole_card_default_de"] for row in audit),
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
