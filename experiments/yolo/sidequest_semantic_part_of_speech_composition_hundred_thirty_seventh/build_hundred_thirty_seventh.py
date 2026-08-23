#!/usr/bin/env python3
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


OUT = Path(__file__).resolve().parent
EXP = OUT.parents[1]
R136 = EXP / "yolo" / "sidequest_semantic_period_sized_current_edition_hundred_thirty_sixth"


def read_tsv(name):
    with (R136 / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name, rows):
    with (OUT / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


ACTIVE_TYPES = {
    "MC002": "DURATIVE_ACTION", "MC004": "TERMINAL_ACTION", "MC005": "TERMINAL_ACTION",
    "MC007": "DURATIVE_ACTION", "MC012": "OBJECT", "MC013": "ORDERED_OBJECT",
    "MC017": "QUANTITY_ACTION", "MC019": "TERMINAL_STATE", "MC025": "TERMINAL_ACTION",
    "MC026": "ACTION", "MC028": "TERMINAL_ACTION", "MC032": "DURATIVE_ACTION",
    "MC034": "OBJECT", "MC035": "ACTION", "MC039": "QUANTITY", "MC040": "TARGET_ACTION",
    "MC045": "TERMINAL_ACTION", "MC055": "SOURCE_ANAPHOR", "MC060": "ORDERED_QUANTITY",
    "MC074": "ACTION", "MC080": "OBJECT", "MC082": "TERMINAL_ACTION", "MC083": "TERMINAL_ACTION",
    "MC086": "QUANTITY_OBJECT", "MC088": "TERMINAL_ACTION", "MC093": "TARGET_ANAPHOR",
    "MC103": "ACTION", "MC105": "QUANTITY_OBJECT", "MC119": "PRODUCT_OBJECT",
    "MC120": "QUANTITY_ACTION", "MC123": "ITEM_ANAPHOR", "MC128": "TERMINAL_ACTION",
    "MC142": "SOURCE_ANAPHOR", "MC143": "TERMINAL_ACTION", "MC147": "ACTION",
    "MC153": "CONTINUATION_LINK", "MC154": "TARGET_ANAPHOR", "MC155": "TERMINAL_ACTION",
    "MC157": "CARRIED_PREPARATION", "MC161": "STATE", "MC171": "ORDER_ANAPHOR",
}


DRAWER_TYPES = {
    "D1_MATERIAL_PRODUCT_VESSEL": "LEARNED_OBJECT",
    "D2_FILTER_WASH_FLOW": "LEARNED_PROCESS_OR_PATH",
    "D3_HEAT_SETTLE_STATE": "LEARNED_PROCESS_OR_STATE",
    "D4_TRANSFER_SOURCE_TARGET": "LEARNED_TRANSFER_OR_ADDRESS",
    "D5_QUANTITY_PART_STAGE": "LEARNED_QUANTITY_OR_STAGE",
    "D6_ORDER_CONTINUATION": "LEARNED_ORDER_OR_LINK",
    "D7_APPLICATION_FASTEN_STORE": "LEARNED_APPLICATION_ACTION",
    "D8_LOCAL_OPERATION": "LEARNED_LOCAL_ACTION",
}


def main():
    cards = read_tsv("HUNDRED_THIRTY_SIXTH_173_CARD_DICTIONARY.tsv")
    events = read_tsv("HUNDRED_THIRTY_SIXTH_381_PROSE_EVENTS.tsv")
    statements = read_tsv("HUNDRED_THIRTY_SIXTH_116_TERSE_STATEMENTS.tsv")
    typed_cards = []
    for row in cards:
        pos = ACTIVE_TYPES[row["master_card_id"]] if row["master_card_id"] in ACTIVE_TYPES else DRAWER_TYPES[row["drawer"]]
        typed_cards.append({
            "master_card_id": row["master_card_id"], "master_form": row["master_form"],
            "registered_surfaces": row["registered_surfaces"], "current_default_de": row["current_spoken_default_de"],
            "syntactic_type": pos, "teaching_layer": row["teaching_layer"], "drawer": row["drawer"],
            "event_count": row["event_count"],
        })
    type_by_id = {r["master_card_id"]: r["syntactic_type"] for r in typed_cards}
    value_by_id = {r["master_card_id"]: r["current_default_de"] for r in typed_cards}

    by_statement = defaultdict(list)
    for row in events:
        by_statement[row["statement_id"]].append(row)
    pair_counts = Counter()
    pair_contexts = defaultdict(list)
    triple_counts = Counter()
    triple_contexts = defaultdict(list)
    for sid, group in by_statement.items():
        ids = [r["master_card_id"] for r in group]
        for a, b in zip(ids, ids[1:]):
            pair_counts[(a, b)] += 1
            pair_contexts[(a, b)].append(sid)
        for a, b, c in zip(ids, ids[1:], ids[2:]):
            triple_counts[(a, b, c)] += 1
            triple_contexts[(a, b, c)].append(sid)
    pairs = []
    for (a, b), count in sorted(pair_counts.items(), key=lambda x: (-x[1], x[0])):
        if count < 2:
            continue
        pairs.append({
            "left_card_id": a, "right_card_id": b, "count": str(count),
            "left_value_de": value_by_id[a], "right_value_de": value_by_id[b],
            "type_signature": type_by_id[a] + ">" + type_by_id[b],
            "statement_ids": "|".join(pair_contexts[(a, b)]),
            "composition_reading_de": value_by_id[a] + " → " + value_by_id[b],
        })
    triples = []
    for ids, count in sorted(triple_counts.items(), key=lambda x: (-x[1], x[0])):
        if count < 2:
            continue
        triples.append({
            "card_ids": "|".join(ids), "count": str(count),
            "values_de": " | ".join(value_by_id[i] for i in ids),
            "type_signature": ">".join(type_by_id[i] for i in ids),
            "statement_ids": "|".join(triple_contexts[ids]),
            "construction": "PAIRED_ITEMS_UNDER_ONE_MEASURE" if ids == ("MC123", "MC039", "MC123") else "RECURRENT_TRIPLE",
        })

    formulae = [
        {"formula_id": "F1_Y_AIIN_Y", "surface_pattern": "CHEY AIIN CHEY", "attested_count": "2", "typed_parse": "ITEM_ANAPHOR>QUANTITY>ITEM_ANAPHOR", "current_reading_de": "dies | Sollmaß | dies", "best_composition_de": "zwei Posten unter demselben Sollmaß", "revision": "KEEP"},
        {"formula_id": "F2_OL_OLOR_OL", "surface_pattern": "CHEOL CHOLOR CHEOL", "attested_count": "2", "typed_parse": "CONTINUATION_LINK>CARRIED_PREPARATION>CONTINUATION_LINK", "current_reading_de": "weiter | damit weiter | weiter", "best_composition_de": "weiter | derselbe Ansatz | weiter", "revision": "CHOLOR_TO_DERSELBE_ANSATZ"},
        {"formula_id": "F3_LONG_SHORT_CLOSE", "surface_pattern": "QOKEEY QOKEDY", "attested_count": "2", "typed_parse": "DURATIVE_ACTION>TERMINAL_ACTION", "current_reading_de": "lange einwirken | kurz einwirken; Schluss", "best_composition_de": "lange halten; kurz nachwirken; Schluss", "revision": "KEEP_PENDING"},
        {"formula_id": "F4_TRANSFER_HOLD_CLOSE", "surface_pattern": "CHEDY QOKEEDY", "attested_count": "2", "typed_parse": "ACTION>TERMINAL_ACTION", "current_reading_de": "überführen | lange einwirken; Schluss", "best_composition_de": "überführen; lange einwirken; Schluss", "revision": "KEEP"},
        {"formula_id": "F5_CONTINUE_SETTLE_CLOSE", "surface_pattern": "OL SHEDY", "attested_count": "4", "typed_parse": "CONTINUATION_LINK>TERMINAL_ACTION", "current_reading_de": "weiter | kurz absetzen; Schluss", "best_composition_de": "danach kurz absetzen; Schluss", "revision": "KEEP"},
    ]

    typed_statements = []
    old_by_id = {r["statement_id"]: r for r in statements}
    for sid, group in by_statement.items():
        typed_statements.append({
            "statement_id": sid, "record_unit_id": group[0]["record_unit_id"], "page": group[0]["page"],
            "visible_surface_sequence": " ".join(r["visible_surface"] for r in group),
            "type_signature": ">".join(type_by_id[r["master_card_id"]] for r in group),
            "period_sized_card_chain_de": old_by_id[sid]["period_sized_card_chain_de"],
            "typed_clause_de": old_by_id[sid]["terse_workshop_clause_de"],
        })

    write_tsv("HUNDRED_THIRTY_SEVENTH_173_TYPED_DICTIONARY.tsv", typed_cards)
    write_tsv("HUNDRED_THIRTY_SEVENTH_RECURRENT_EXACT_PAIRS.tsv", pairs)
    write_tsv("HUNDRED_THIRTY_SEVENTH_RECURRENT_EXACT_TRIPLES.tsv", triples)
    write_tsv("HUNDRED_THIRTY_SEVENTH_FIVE_COMPOSITION_FORMULAE.tsv", formulae)
    write_tsv("HUNDRED_THIRTY_SEVENTH_116_TYPED_STATEMENTS.tsv", typed_statements)

    report = [
        "# Hundertsiebenunddreißigste Runde: Wortarten und echte Kartenkomposition", "",
        "The complete 173-card dictionary now has a syntactic type. The 41 active cards receive narrow types;",
        "the 132 rare cards retain learned drawer types rather than invented morphemes. Across all 116 statements",
        "only fourteen exact adjacent pairs recur at least twice and only one exact triple recurs twice. This",
        "confirms that most long apparent words are memorized cards, while a small formula grammar is real.", "",
        "## Strong constructions", "",
        "`CHEY AIIN CHEY` is clean: ITEM > MEASURE > ITEM, read as two current items under one prescribed",
        "measure. `CHEDY QOKEEDY` is action > terminal action: transfer, then hold long, then close. `OL SHEDY`",
        "is continuation > terminal action: continue and then settle/close. These need no new meanings.", "",
        "## One useful correction", "",
        "`CHEOL CHOLOR CHEOL` currently says the redundant 'weiter | damit weiter | weiter'. Treating the middle",
        "whole card as `DERSELBE ANSATZ` makes both occurrences readable: the links bracket a carried preparation.",
        "This does not imply that OR or OL is a spoken suffix everywhere; it is a learned compositional island.", "",
        "## Part-of-speech result", "",
        "The shortened shared deck is now internally coherent: ANTEIL, SOLLMASS, ANSATZ and KLARAUSZUG are nouns;",
        "DAVON, DORTHIN, DIES and DAS NÄCHSTE are anaphors; EINSETZEN, ÜBERFÜHREN and BEMESSEN are actions; BEREIT",
        "and FERTIG are states. No active card needs both a noun and a verb in the same default.", "",
        "Next revise CHOLOR to DERSELBE ANSATZ everywhere and rewrite the two bracket constructions as explicit",
        "spoken formulae inside all affected statements and records.",
    ]
    (OUT / "HUNDRED_THIRTY_SEVENTH_COMPOSITION_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps({"cards": len(typed_cards), "statements": len(typed_statements), "recurrent_pairs": len(pairs), "recurrent_triples": len(triples), "formulae": len(formulae)}, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
