#!/usr/bin/env python3
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R156 = ROOT / "experiments/yolo/sidequest_semantic_atomic_current_ten_page_hundred_fifty_sixth"
OLD = "seihen; Schluss"
NEW = "durchlassen; Schluss"
TARGET_CARD = "MC143"

TABLES = {
    "HUNDRED_SIXTY_FOURTH_173_ATOMIC_DICTIONARY.tsv": "HUNDRED_FIFTY_SIXTH_173_ATOMIC_DICTIONARY.tsv",
    "HUNDRED_SIXTY_FOURTH_230_SURFACE_READER.tsv": "HUNDRED_FIFTY_SIXTH_230_SURFACE_READER.tsv",
    "HUNDRED_SIXTY_FOURTH_381_ATOMIC_EVENTS.tsv": "HUNDRED_FIFTY_SIXTH_381_ATOMIC_EVENTS.tsv",
    "HUNDRED_SIXTY_FOURTH_116_ATOMIC_CLAUSES.tsv": "HUNDRED_FIFTY_SIXTH_116_ATOMIC_CLAUSES.tsv",
    "HUNDRED_SIXTY_FOURTH_11_ATOMIC_RECORDS.tsv": "HUNDRED_FIFTY_SIXTH_ELEVEN_ATOMIC_RECORDS.tsv",
    "HUNDRED_SIXTY_FOURTH_395_ASTRO_OWNER_MENU.tsv": "HUNDRED_FIFTY_SIXTH_395_ASTRO_OWNER_MENU.tsv",
    "HUNDRED_SIXTY_FOURTH_776_ATOMIC_LEDGER.tsv": "HUNDRED_FIFTY_SIXTH_776_ATOMIC_LEDGER.tsv",
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


def revised(row):
    return {key: value.replace(OLD, NEW) for key, value in row.items()}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    built = {}
    for output, source in TABLES.items():
        rows = [revised(row) for row in read_tsv(R156 / source)]
        write_tsv(output, rows)
        built[output] = rows

    clauses = built["HUNDRED_SIXTY_FOURTH_116_ATOMIC_CLAUSES.tsv"]
    remaining = [row for row in clauses if row["record_unit_id"] not in {"H3", "B2"}]
    pressure_rows = []
    for row in remaining:
        if TARGET_CARD in {
            event["master_card_id"] for event in built["HUNDRED_SIXTY_FOURTH_381_ATOMIC_EVENTS.tsv"]
            if event["statement_id"] == row["statement_id"]
        }:
            status = "REVISED_OVERLITERAL_FILTER_TO_TECHNICAL_PASSAGE"
            consequence = "Lesung wird Durchlass/Passage; lokaler Filter bleibt möglich, aber nicht im Kartenwert."
        elif "ungelöst" in row["owner_trace"]:
            status = "KEEP_PROCESS_VALUE_OWNER_UNRESOLVED"
            consequence = "Operationskette bleibt, konkrete Station wird nicht erfunden."
        else:
            status = "KEEP_PROCESS_COMPATIBLE"
            consequence = "Kein klarer Widerspruch zum Auszug-Teilung-Halten-Transfer-Waschen-Ablauf-Modell."
        pressure_rows.append({
            "statement_id": row["statement_id"], "record_unit_id": row["record_unit_id"],
            "page": row["page"], "owner_trace": row["owner_trace"],
            "atomic_card_chain_de": row["atomic_card_chain_de"], "pressure_status": status,
            "workshop_consequence_de": consequence,
        })
    write_tsv("HUNDRED_SIXTY_FOURTH_90_CLAUSE_PROCESS_PRESSURE.tsv", pressure_rows)

    revision_events = [
        row for row in built["HUNDRED_SIXTY_FOURTH_381_ATOMIC_EVENTS.tsv"]
        if row["master_card_id"] == TARGET_CARD
    ]
    revision_rows = [{
        "master_card_id": TARGET_CARD, "master_form": "shckhedy", "old_value_de": OLD,
        "new_value_de": NEW, "event_count": str(len(revision_events)),
        "event_serials": "|".join(row["event_serial"] for row in revision_events),
        "records": "|".join(dict.fromkeys(row["record_unit_id"] for row in revision_events)),
        "reason_de": "Bio zeigt Durchlass- und Beckenstationen, aber kein Filtertuch; zwei direkt wiederholte Vorkommen sind besser zwei Passagen als zwei unabhängige Seihvorgänge.",
        "local_expansion_allowed": "FILTRATION_ONLY_IF_OWNER_OR_NEIGHBOURING_WHOLE_CARD_SUPPLIES_IT",
    }]
    write_tsv("HUNDRED_SIXTY_FOURTH_1_CARD_REVISION.tsv", revision_rows)

    for output, source in [
        ("HUNDRED_SIXTY_FOURTH_COMPLETE_TEN_PAGE_EDITION.md", "HUNDRED_FIFTY_SIXTH_COMPLETE_TEN_PAGE_EDITION.md"),
        ("HUNDRED_SIXTY_FOURTH_ATOMIC_POCKET_MANUAL.md", "HUNDRED_FIFTY_SIXTH_ATOMIC_POCKET_MANUAL.md"),
    ]:
        text = (R156 / source).read_text(encoding="utf-8").replace(OLD, NEW)
        (OUT / output).write_text(text, encoding="utf-8")

    report = [
        "# Hundertvierundsechzigste Runde: Prozessdruck auf die übrigen neun Records", "",
        "Ninety clauses outside H3 and B2 were read against the extract-to-station workflow. Seventy-six remain",
        "directly compatible. Eleven retain usable operations but sit under an unresolved B3 image owner. Three",
        "clauses expose one over-literal shared card: MC143 `shckhedy = seihen; Schluss`.", "",
        "All three MC143 occurrences are Biological. Two are consecutive under the same visible main pair, and no",
        "filter cloth is drawn. The revised atomic value is `durchlassen; Schluss`: a concrete passage operation",
        "that can still expand to filtration when a local owner or neighbouring whole card supplies a filter.", "",
        "The complete current base is rebuilt with exactly one card revision: 173 cards, 230 visible forms, 381",
        "events, 116 clauses, eleven records, 395 Astro groups and 776 total groups. Next rewrite the affected B1",
        "and B4 passages fluently and check whether the two consecutive B4 passages represent two stages, two",
        "channels or a copied repetition.",
    ]
    (OUT / "HUNDRED_SIXTY_FOURTH_PROCESS_PRESSURE_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps({
        "cards": len(built["HUNDRED_SIXTY_FOURTH_173_ATOMIC_DICTIONARY.tsv"]),
        "surfaces": len(built["HUNDRED_SIXTY_FOURTH_230_SURFACE_READER.tsv"]),
        "events": len(built["HUNDRED_SIXTY_FOURTH_381_ATOMIC_EVENTS.tsv"]),
        "clauses": len(clauses), "records": len(built["HUNDRED_SIXTY_FOURTH_11_ATOMIC_RECORDS.tsv"]),
        "astro_groups": len(built["HUNDRED_SIXTY_FOURTH_395_ASTRO_OWNER_MENU.tsv"]),
        "unified_groups": len(built["HUNDRED_SIXTY_FOURTH_776_ATOMIC_LEDGER.tsv"]),
        "pressure_clauses": len(pressure_rows),
        "compatible_clauses": sum(row["pressure_status"] == "KEEP_PROCESS_COMPATIBLE" for row in pressure_rows),
        "owner_unresolved_clauses": sum(row["pressure_status"] == "KEEP_PROCESS_VALUE_OWNER_UNRESOLVED" for row in pressure_rows),
        "revised_clauses": sum(row["pressure_status"] == "REVISED_OVERLITERAL_FILTER_TO_TECHNICAL_PASSAGE" for row in pressure_rows),
        "revised_cards": 1, "revised_events": len(revision_events),
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
