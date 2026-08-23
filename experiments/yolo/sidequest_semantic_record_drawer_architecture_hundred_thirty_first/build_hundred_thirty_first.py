#!/usr/bin/env python3
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R129 = ROOT / "experiments/yolo/sidequest_semantic_specialist_drawers_hundred_twenty_ninth"

RECORD_READING = {
    "H1": "material-led root or solid-part preparation with one run, one value and a carried finishing step",
    "H2": "material-led formulation of a new batch with repeated item, state and carry cards",
    "H3": "the clearest extraction article: material, wringing, holding, re-straining and clear run",
    "H4": "quantity-led division of a prepared product followed by storage or local application",
    "H5": "multi-product fresh-plant article with ingredients, extraction, binding and a second preparation",
    "B1": "general basin program alternating transfer, passage, state and wash cells",
    "B2": "multi-station program dominated by transfer, held state and filtered outflow",
    "B3": "long processing line dominated by repeated transfer and state changes",
    "B4": "cloth/application service program with ordering, filtration, fastening and cleanup",
    "B5": "small left service station for settling and source-to-target transfer",
    "B6": "small right service station for collection, cloth and final target delivery",
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


def short(drawer):
    return {"ACTIVE_CORE": "CORE", "D1_MATERIAL_PRODUCT_VESSEL": "MATERIAL", "D2_FILTER_WASH_FLOW": "FILTER",
            "D3_HEAT_SETTLE_STATE": "STATE", "D4_TRANSFER_SOURCE_TARGET": "TRANSFER", "D5_QUANTITY_PART_STAGE": "QUANTITY",
            "D6_ORDER_CONTINUATION": "ORDER", "D7_APPLICATION_FASTEN_STORE": "APPLICATION", "D8_LOCAL_OPERATION": "LOCAL"}[drawer]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    events = read_tsv(R129 / "HUNDRED_TWENTY_NINTH_COMPLETE_381_EVENT_DICTIONARY.tsv")
    by_record = defaultdict(list)
    for row in events:
        by_record[row["record_unit_id"]].append(row)

    trace_rows = []
    for record, members in by_record.items():
        previous = None
        phase = 0
        for row in members:
            if row["drawer"] != previous:
                phase += 1
                previous = row["drawer"]
            trace_rows.append({
                "event_serial": row["event_serial"],
                "record_unit_id": record,
                "page": row["page"],
                "statement_id": row["statement_id"],
                "visible_surface": row["visible_surface"],
                "spoken_value_de": row["current_spoken_default_de"],
                "drawer": row["drawer"],
                "record_phase": f"P{phase:02d}",
            })
    write_tsv("HUNDRED_THIRTY_FIRST_381_EVENT_DRAWER_TRACE.tsv", trace_rows)

    drawers = ["D1_MATERIAL_PRODUCT_VESSEL", "D2_FILTER_WASH_FLOW", "D3_HEAT_SETTLE_STATE",
               "D4_TRANSFER_SOURCE_TARGET", "D5_QUANTITY_PART_STAGE", "D6_ORDER_CONTINUATION",
               "D7_APPLICATION_FASTEN_STORE", "D8_LOCAL_OPERATION"]
    profile_rows = []
    for record in sorted(by_record, key=lambda value: (value[0], int(value[1:]))):
        members = by_record[record]
        counts = Counter(row["drawer"] for row in members)
        collapsed = []
        for row in members:
            label = short(row["drawer"])
            if not collapsed or collapsed[-1] != label:
                collapsed.append(label)
        specialist_counts = {drawer: counts[drawer] for drawer in drawers}
        leading = max(drawers, key=lambda drawer: (specialist_counts[drawer], drawer))
        profile_rows.append({
            "record_unit_id": record,
            "page": members[0]["page"],
            "section": "HERBAL" if record.startswith("H") else "BIOLOGICAL",
            "event_count": str(len(members)),
            "active_core_events": str(counts["ACTIVE_CORE"]),
            "material_events": str(counts[drawers[0]]),
            "filter_events": str(counts[drawers[1]]),
            "state_events": str(counts[drawers[2]]),
            "transfer_events": str(counts[drawers[3]]),
            "quantity_events": str(counts[drawers[4]]),
            "order_events": str(counts[drawers[5]]),
            "application_events": str(counts[drawers[6]]),
            "local_events": str(counts[drawers[7]]),
            "leading_specialist_drawer": short(leading),
            "collapsed_drawer_phases": ">".join(collapsed),
            "working_record_reading": RECORD_READING[record],
        })
    write_tsv("HUNDRED_THIRTY_FIRST_ELEVEN_RECORD_PROFILES.tsv", profile_rows)

    section_rows = []
    for section, prefix in (("HERBAL", "H"), ("BIOLOGICAL", "B")):
        members = [row for row in events if row["record_unit_id"].startswith(prefix)]
        counts = Counter(row["drawer"] for row in members)
        section_rows.append({
            "section": section,
            "records": str(len({row["record_unit_id"] for row in members})),
            "events": str(len(members)),
            "active_core": str(counts["ACTIVE_CORE"]),
            "material": str(counts[drawers[0]]),
            "filter": str(counts[drawers[1]]),
            "state": str(counts[drawers[2]]),
            "transfer": str(counts[drawers[3]]),
            "quantity": str(counts[drawers[4]]),
            "order": str(counts[drawers[5]]),
            "application": str(counts[drawers[6]]),
            "local": str(counts[drawers[7]]),
            "architecture_reading": "names material and product, then gives compact preparation clauses" if section == "HERBAL" else "inherits the work item, then routes it through transfer and state cells",
        })
    write_tsv("HUNDRED_THIRTY_FIRST_HERBAL_BIO_COMPARISON.tsv", section_rows)

    report = [
        "# Hunderteinunddreißigste Runde: WAS und WIE benutzen dasselbe Deck verschieden", "",
        "Herbal has 100 events: 55 active-core, 17 rare material/product, nine state, five quantity, five",
        "order, three filter, and only two transfer events. Biological has 281 events: 184 active-core,",
        "36 state, 35 transfer, twelve filter, but only three rare material/product events.", "",
        "That asymmetry gives the book a concrete architecture. The plant articles supply WHAT: pictured",
        "material, preparation, extracted product, portion and occasional application. The figure/basin pages",
        "supply HOW: inherit a work item, route it, hold or settle it, pass or strain it, and close the local",
        "cell. The shared 41-card core lets both sections speak to the same workshop without making their",
        "specialist vocabularies identical.", "",
        "H3 is the strongest extraction article; H4 the strongest quantity/application article. B2 and B3",
        "are the strongest transfer/state programs; B4 adds cloth application and cleanup. B5/B6 look like",
        "short service tails rather than independent medical chapters.", "",
        "Next step: connect each Herbal product profile to compatible Biological operation profiles using",
        "only these drawer functions, producing a small set of plausible workshop jobs without assuming a",
        "written cross-page pointer.",
    ]
    (OUT / "HUNDRED_THIRTY_FIRST_RECORD_ARCHITECTURE_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    summary = {"status": "COMPLETE", "records": len(profile_rows), "events": len(trace_rows), "sections": len(section_rows),
               "herbal_material": int(section_rows[0]["material"]), "herbal_transfer": int(section_rows[0]["transfer"]),
               "bio_material": int(section_rows[1]["material"]), "bio_transfer": int(section_rows[1]["transfer"])}
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
