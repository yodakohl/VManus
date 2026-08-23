#!/usr/bin/env python3
import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R146 = ROOT / "experiments/yolo/sidequest_semantic_specialist_owner_scrub_hundred_forty_sixth"

PROMOTIONS = {
    "oiiin": ("Arbeitsstufe", "STAGE_OBJECT"),
    "dain": ("Einlage", "INSERT_OBJECT"),
    "qcthey": ("kurz vorbereiten", "SHORT_PREPARATION_ACTION"),
    "olkain": ("weiterer Anteil", "CONTINUED_QUANTITY_OBJECT"),
    "shedal": ("am Ziel absetzen", "TARGET_STATE_ACTION"),
    "qoteedy": ("lange Folgestufe; Schluss", "TERMINAL_ORDERED_STATE"),
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
    cards = read_tsv(R146 / "HUNDRED_FORTY_SIXTH_173_SHORT_DICTIONARY.tsv")
    events = read_tsv(R146 / "HUNDRED_FORTY_SIXTH_381_SHORT_EVENTS.tsv")
    statements = read_tsv(R146 / "HUNDRED_FORTY_SIXTH_116_SHORT_STATEMENTS.tsv")

    recurrence = []
    revised_cards = []
    for row in cards:
        records = row["records"].split("|")
        count = int(row["event_count"])
        if row["portable_scope"] == "LOCAL_LEARNED_WHOLE_CARD":
            if len(records) > 1:
                portability = "CROSS_RECORD_SAME_SECTION"
            elif count > 1:
                portability = "REPEATED_ONE_RECORD"
            else:
                portability = "SINGLETON_NOMENCLATOR"
            decision = "PROMOTE_TO_BIO_SHARED_DECK" if row["master_form"] in PROMOTIONS else "KEEP_LOCAL_WHOLE_CARD"
            recurrence.append({
                "master_card_id": row["master_card_id"], "master_form": row["master_form"],
                "current_value_de": row["portable_card_value_de"], "event_count": row["event_count"],
                "records": row["records"], "portability_class": portability, "decision": decision,
                "promoted_value_de": PROMOTIONS.get(row["master_form"], (row["portable_card_value_de"], ""))[0],
                "promotion_boundary": "BIOLOGICAL_RECORDS_ONLY" if decision.startswith("PROMOTE") else "LOCAL",
            })
        new = dict(row)
        if row["master_form"] in PROMOTIONS:
            value, syntactic_type = PROMOTIONS[row["master_form"]]
            new["portable_card_value_de"] = value
            new["syntactic_type"] = syntactic_type
            new["portable_scope"] = "ACTIVE_BIO_CROSS_RECORD"
            new["owner_argument_policy"] = "ACTIVE_BIO_ITEM_OR_STATION"
            new["fluent_do_not_auto_add"] = "No plant, water, body, patient, vessel, exact target or unit"
        revised_cards.append(new)
    write_tsv("HUNDRED_FORTY_SEVENTH_132_RECURRENCE_AUDIT.tsv", recurrence)
    write_tsv("HUNDRED_FORTY_SEVENTH_173_PROMOTED_DICTIONARY.tsv", revised_cards)

    card_by_id = {row["master_card_id"]: row for row in revised_cards}
    revised_events = []
    for row in events:
        new = dict(row)
        card = card_by_id[row["master_card_id"]]
        new["portable_card_value_de"] = card["portable_card_value_de"]
        new["owner_argument_policy"] = card["owner_argument_policy"]
        new["portable_scope"] = card["portable_scope"]
        revised_events.append(new)
    write_tsv("HUNDRED_FORTY_SEVENTH_381_PROMOTED_EVENTS.tsv", revised_events)

    by_statement = defaultdict(list)
    for row in revised_events:
        by_statement[row["statement_id"]].append(row["portable_card_value_de"])
    revised_statements = []
    for row in statements:
        new = dict(row)
        chain = " | ".join(by_statement[row["statement_id"]])
        new["portable_literal_chain_de"] = chain
        new["controlled_fluent_de"] = f"Besitzer: {row['owner_argument_de']}. Karten: {chain.replace(' | ', '; ')}."
        revised_statements.append(new)
    write_tsv("HUNDRED_FORTY_SEVENTH_116_PROMOTED_STATEMENTS.tsv", revised_statements)

    report = [
        "# Hundertsiebenundvierzigste Runde: sechs Bio-Karten steigen in den gemeinsamen Lehrsatz auf", "",
        "The 132 specialist cards divide cleanly into 122 singletons, four cards repeated only inside one record,",
        "and six cards repeated across two Biological records. The last six cover twelve events and are promoted",
        "to a bounded Biological shared deck; none is yet claimed to bridge Herbal and Biological.", "",
        "The portable readings are OIIIN=ARBEITSSTUFE, DAIN=EINLAGE, QCTHEY=KURZ VORBEREITEN, OLKAIN=WEITERER",
        "ANTEIL, SHEDAL=AM ZIEL ABSETZEN and QOTEEDY=LANGE FOLGESTUFE; SCHLUSS. DAIN is deliberately broadened",
        "from TRÄGEREINLAGE because its second owner does not independently display cloth. The four within-record",
        "repetitions remain local; the 122 singletons remain memorized nomenclator cards.", "",
        "The active vocabulary is therefore 47 cards: the earlier 41 plus six Bio-shared cards. This is a better",
        "workshop economy without pretending recurrence on one page proves a universal stem. Next use the resulting",
        "47-card deck to reconstruct the six complete Biological records in terse apprentice speech.",
    ]
    (OUT / "HUNDRED_FORTY_SEVENTH_PROMOTION_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps({
        "cards": len(revised_cards), "active_cards": sum(r["portable_scope"].startswith("ACTIVE") for r in revised_cards),
        "promoted_cards": len(PROMOTIONS), "promoted_events": sum(int(r["event_count"]) for r in recurrence if r["decision"].startswith("PROMOTE")),
        "cross_record_specialists": sum(r["portability_class"] == "CROSS_RECORD_SAME_SECTION" for r in recurrence),
        "same_record_recurrent": sum(r["portability_class"] == "REPEATED_ONE_RECORD" for r in recurrence),
        "singleton_specialists": sum(r["portability_class"] == "SINGLETON_NOMENCLATOR" for r in recurrence),
        "events": len(revised_events), "statements": len(revised_statements),
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
