#!/usr/bin/env python3
import csv
import json
import re
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R144 = ROOT / "experiments/yolo/sidequest_semantic_layered_current_edition_hundred_forty_fourth"

REPLACEMENTS = [
    ("Wurzel · Posten", "Grundteil"),
    ("Flüssigkeitslauf", "Lauf"),
    ("Zielstelle", "Ziel"),
    ("Ausgang", "Quelle"),
    ("Durchgang", "Passage"),
    ("Zutat", "Zugabe"),
    ("Gefäß", "Aufnahme"),
    ("Tuch", "Trägereinlage"),
    ("Ansatz", "Bereitung"),
]
OVERRIDES = {
    "sshkchdy": "Haltetransfer; Schluss",
    "cheeckhody": "Langpassage; Schluss",
    "qockhey": "Kurzpassage",
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


def shorten(row):
    old = row["portable_card_value_de"]
    new = old
    hits = []
    for source, target in REPLACEMENTS:
        if source in new:
            hits.append(source)
            new = new.replace(source, target)
    if row["master_form"] in OVERRIDES:
        new = OVERRIDES[row["master_form"]]
    overlong = len(re.findall(r"[A-Za-zÄÖÜäöüß]+", old)) > 3
    reason = "KEEP_SHORT_SPECIALIST_VALUE"
    if hits and overlong:
        reason = "REMOVE_OWNER_NOUN_AND_COMPRESS"
    elif hits:
        reason = "REMOVE_OWNER_NOUN"
    elif overlong:
        reason = "COMPRESS_SENTENCE_SIZED_VALUE"
    return new, "|".join(hits) or "NONE", "YES" if overlong else "NO", reason


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    cards = read_tsv(R144 / "HUNDRED_FORTY_FOURTH_173_LAYERED_DICTIONARY.tsv")
    events = read_tsv(R144 / "HUNDRED_FORTY_FOURTH_381_LAYERED_EVENTS.tsv")
    statements = read_tsv(R144 / "HUNDRED_FORTY_FOURTH_116_LAYERED_STATEMENTS.tsv")
    audit = []
    revised = []
    for row in cards:
        new = dict(row)
        if row["portable_scope"] == "LOCAL_LEARNED_WHOLE_CARD":
            short, hits, overlong, reason = shorten(row)
            new["portable_card_value_de"] = short
            audit.append({
                "master_card_id": row["master_card_id"], "master_form": row["master_form"],
                "event_count": row["event_count"], "records": row["records"],
                "old_value_de": row["portable_card_value_de"], "short_value_de": short,
                "owner_noun_hits": hits, "old_value_over_three_words": overlong,
                "decision": reason, "owner_argument_policy": row["owner_argument_policy"],
            })
        revised.append(new)
    write_tsv("HUNDRED_FORTY_SIXTH_132_SPECIALIST_AUDIT.tsv", audit)
    write_tsv("HUNDRED_FORTY_SIXTH_173_SHORT_DICTIONARY.tsv", revised)

    card_by_id = {row["master_card_id"]: row for row in revised}
    revised_events = []
    for row in events:
        new = dict(row)
        new["portable_card_value_de"] = card_by_id[row["master_card_id"]]["portable_card_value_de"]
        revised_events.append(new)
    write_tsv("HUNDRED_FORTY_SIXTH_381_SHORT_EVENTS.tsv", revised_events)

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
    write_tsv("HUNDRED_FORTY_SIXTH_116_SHORT_STATEMENTS.tsv", revised_statements)

    changed = [row for row in audit if row["old_value_de"] != row["short_value_de"]]
    report = [
        "# Hundertsechsundvierzigste Runde: die Fachschubladen verlieren ihre Bildnomen", "",
        f"All 132 learned specialist cards were reread. {len(changed)} card defaults covering "
        f"{sum(int(r['event_count']) for r in changed)} events were shortened. The remaining "
        f"{132-len(changed)} were already compact enough.", "",
        "The main corrections are deliberately plain: Wurzel/Posten becomes GRUNDTEIL, Zutat becomes ZUGABE,",
        "Gefäß becomes AUFNAHME, Tuch becomes TRÄGEREINLAGE, Flüssigkeitslauf becomes LAUF, Zielstelle becomes",
        "ZIEL, Ausgang becomes QUELLE, Durchgang becomes PASSAGE and Ansatz becomes BEREITUNG. These are learned",
        "workshop entries; the exact pictured plant, vessel, basin, cloth, source or target remains an owner argument.", "",
        "Three sentence-sized entries are compressed further: SSHKCHDY is HALTETRANSFER; SCHLUSS, CHEECKHODY is",
        "LANGPASSAGE; SCHLUSS, and QOCKHEY is KURZPASSAGE. No card is left without a concrete default. The complete",
        "381-event and 116-statement readings are regenerated so the shorter words can be judged in place.", "",
        "Next rank these specialist values by recurrence and cross-record portability. Promote only genuinely shared",
        "short words; keep one-off values as learned nomenclator entries rather than pretending every visible part is a stem.",
    ]
    (OUT / "HUNDRED_FORTY_SIXTH_SPECIALIST_SCRUB_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps({
        "cards": len(revised), "specialist_cards": len(audit), "changed_specialist_cards": len(changed),
        "changed_events": sum(int(row["event_count"]) for row in changed), "events": len(revised_events),
        "statements": len(revised_statements),
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
