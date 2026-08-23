#!/usr/bin/env python3
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R115 = ROOT / "experiments/yolo/sidequest_semantic_bridge_card_revision_hundred_fifteenth_edition"
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_atomic_defaults_hundred_first_edition/HUNDRED_FIRST_381_EVENT_ATOMIC_INTERLINEAR.tsv"


def load(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name, rows):
    with (OUT / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def cross_sections(records):
    values = records.split("|")
    return any(x.startswith("H") for x in values), any(x.startswith("B") for x in values)


def main():
    dictionary = load(R115 / "HUNDRED_FIFTEENTH_173_REVISED_TEACHING_DICTIONARY.tsv")
    events = load(EVENTS)
    by_card = defaultdict(list)
    for row in events:
        by_card[row["master_card_id"]].append(row)

    core_cards = [r for r in dictionary if r["revised_teaching_tier"] == "PORTABLE_CORE_CARD"]
    core_rows = []
    for row in core_cards:
        herbal, bio = cross_sections(row["records"])
        if herbal and bio:
            status = "PORTABLE_EXACT_CORE_CARD"
        elif herbal:
            status = "HERBAL_CORE_ATOM_CARD"
        else:
            status = "BIO_CORE_ATOM_CARD"
        ev = by_card[row["master_card_id"]]
        core_rows.append({
            "master_card_id": row["master_card_id"],
            "master_form": row["master_form"],
            "registered_surfaces": row["all_registered_surfaces"],
            "semantic_atoms": row["semantic_atoms"],
            "short_default_de": row["short_default_de"],
            "records": row["records"],
            "event_count": row["event_count"],
            "core_card_status": status,
            "herbal_surfaces": "|".join(sorted({x["visible_surface"] for x in ev if x["record_unit_id"].startswith("H")})) or "NONE",
            "biological_surfaces": "|".join(sorted({x["visible_surface"] for x in ev if x["record_unit_id"].startswith("B")})) or "NONE",
            "teaching_instruction": "teach exact card in both sections" if status == "PORTABLE_EXACT_CORE_CARD" else "teach core atoms globally but practice this exact card only in its section",
        })
    write_tsv("HUNDRED_SIXTEENTH_70_CORE_CARD_AUDIT.tsv", core_rows)

    exact_core = [r for r in core_rows if r["core_card_status"] == "PORTABLE_EXACT_CORE_CARD"]
    exact_bridge_ids = {r["master_card_id"] for r in load(R115 / "HUNDRED_FIFTEENTH_57_BRIDGE_CARD_AUDIT.tsv") if r["bridge_status"] == "PORTABLE_EXACT_BRIDGE_CARD"}
    portable_rows = []
    for row in dictionary:
        if row["master_card_id"] not in {r["master_card_id"] for r in exact_core} | exact_bridge_ids:
            continue
        ev = by_card[row["master_card_id"]]
        record_count = len(set(row["records"].split("|")))
        if record_count == 11:
            breadth = "UNIVERSAL_ALL_PROSE_RECORDS"
        elif record_count >= 4:
            breadth = "BROAD_CROSS_SECTION"
        else:
            breadth = "NARROW_CROSS_SECTION_EXEMPLAR"
        portable_rows.append({
            "deck_order": str(len(portable_rows) + 1),
            "master_card_id": row["master_card_id"],
            "master_form": row["master_form"],
            "registered_surfaces": row["all_registered_surfaces"],
            "semantic_atoms": row["semantic_atoms"],
            "short_default_de": row["short_default_de"],
            "records": row["records"],
            "event_count": row["event_count"],
            "portability_breadth": breadth,
            "herbal_event_count": str(sum(x["record_unit_id"].startswith("H") for x in ev)),
            "biological_event_count": str(sum(x["record_unit_id"].startswith("B") for x in ev)),
        })
    write_tsv("HUNDRED_SIXTEENTH_SEVENTEEN_EXACT_PORTABLE_CARDS.tsv", portable_rows)

    revised = []
    exact_core_ids = {r["master_card_id"] for r in exact_core}
    for row in dictionary:
        old = row["revised_teaching_tier"]
        if old == "PORTABLE_CORE_CARD":
            new = "PORTABLE_EXACT_CORE_CARD" if row["master_card_id"] in exact_core_ids else "SECTIONAL_CARD_WITH_PORTABLE_CORE_ATOMS"
        else:
            new = old
        revised.append({**row, "final_teaching_tier": new})
    write_tsv("HUNDRED_SIXTEENTH_173_FINAL_TEACHING_DICTIONARY.tsv", revised)

    deck_md = ["# Die siebzehn wirklich portablen Ganzkarten", ""]
    for row in portable_rows:
        deck_md.append(f"{row['deck_order']}. `{row['master_form']}` = {row['short_default_de']} — {row['records']} ({row['portability_breadth']})")
    deck_md += ["", "Nur `aiin` erscheint in allen elf Prosa-Records. Die anderen Karten bleiben portable Werkstattkarten mit unterschiedlicher Reichweite."]
    (OUT / "HUNDRED_SIXTEENTH_PORTABLE_DECK.md").write_text("\n".join(deck_md) + "\n", encoding="utf-8")

    report = [
        "# Hundertsechzehnte Runde: das echte gemeinsame Ganzkartendeck", "",
        "Auch bei den siebzig bisherigen Kernkarten war Atom-Portabilität mit Ganzkarten-Portabilität",
        "vermischt. Nur dreizehn exakte Kernkarten erscheinen sowohl in Herbal als auch Biological;",
        "35 sind Bio-only und 22 Herbal-only.", "",
        "Zusammen mit den vier exakten Brückenkarten ergibt das ein sehr kleines echtes gemeinsames Deck",
        "von siebzehn Karten: oldy, choky, aiin, okal, char, chor, okaiin, chey, cheol, al, cholor,",
        "checthy, otchey, cheeky, chdy, chety und cheey. Nur aiin steht in allen elf Prosa-Records.", "",
        "Das 1420-Werkstattmodell wird dadurch einfacher: siebzehn portable Ganzkarten und ihre Allographen,",
        "weitere portable Atombeiträge, danach sektionsgebundene Karten und fünf Spezialtafeln.", "",
        "f84 und f84r blieben versiegelt.",
    ]
    (OUT / "HUNDRED_SIXTEENTH_EXACT_PORTABLE_DECK_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    tiers = Counter(r["final_teaching_tier"] for r in revised)
    summary = {"status": "COMPLETE", "core_cards_audited": len(core_rows), "portable_exact_core": len(exact_core), "portable_exact_total": len(portable_rows), "final_tiers": dict(tiers)}
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
