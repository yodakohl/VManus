#!/usr/bin/env python3
import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R150 = ROOT / "experiments/yolo/sidequest_semantic_eleven_record_source_book_hundred_fiftieth"
RECORD_ORDER = ["H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"]

CARRIES = {
    "H1-S002": ("ACTIVE_PREPARATION", "mit der aktiven Bereitung weiter:", "previous clause prepares, portions, inserts and measures one batch"),
    "H2-S002": ("ACTIVE_PREPARATION|PRESCRIBED_MEASURE", "mit demselben Ansatz und Sollmaß weiter:", "paired-measure frame leaves preparation and measure active"),
    "H2-S003": ("ACTIVE_PREPARATION", "aus demselben Ansatz weiter:", "preceding clause explicitly says derselbe Ansatz and davon"),
    "H3-S003": ("CURRENT_MATERIAL_SHARE", "mit diesem Materialanteil weiter:", "preceding one-card clause selects a part; next begins vom vorigen"),
    "H3-S004": ("CURRENT_ITEM|PRESCRIBED_MEASURE", "mit diesem Posten auf Sollmaß weiter:", "previous clause keeps item and prescribed measure open"),
    "H5-S002": ("TARGETED_PREPARATION", "vom zielgesetzten Ansatz weiter:", "previous clause sets preparation, target and destination without close"),
    "H5-S004": ("CURRENT_ITEM", "mit dem eingesetzten Posten weiter:", "previous clause ends with repeated insertion of the current item"),
    "H5-S005": ("ACTIVE_EXTRACT|TARGET", "mit dem Auszug am Ziel weiter:", "previous clause installs extract and names target"),
    "H5-S006": ("ACTIVE_SEQUENCE|CURRENT_ITEM", "zum nächsten Posten weiter:", "next clause explicitly selects das nächste"),
    "B1-S007": ("TARGET|UNFINISHED_TRANSFER", "am offenen Ziel in die Überführung weiter:", "previous clause ends at target; next closes inward transfer"),
    "B1-S012": ("CURRENT_ITEM|LOCAL_STATION", "mit dem eingesetzten Posten am selben Besitzer weiter:", "previous clause passes and inserts one item without close"),
    "B1-S015": ("SOURCE", "von der eben gesetzten Quelle weiter:", "previous clause ends by selecting the next source"),
    "B3-S012": ("CURRENT_ITEM|SOURCE", "mit dem aus der Quelle überführten Posten weiter:", "previous clause leaves transferred source item open"),
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
    events = read_tsv(R150 / "HUNDRED_FIFTIETH_381_SOURCE_EVENTS.tsv")
    clauses = read_tsv(R150 / "HUNDRED_FIFTIETH_116_SOURCE_CLAUSES.tsv")
    audit = []
    revised = []
    for row in clauses:
        new = dict(row)
        if row["statement_id"] in CARRIES:
            registers, connective, rationale = CARRIES[row["statement_id"]]
            old_prefix = row["connective_de"]
            body = row["source_book_clause_de"][len(old_prefix):].lstrip()
            new["connective_de"] = connective
            new["source_book_clause_de"] = f"{connective} {body}"
            audit.append({
                "previous_statement_id": "", "next_statement_id": row["statement_id"],
                "record_unit_id": row["record_unit_id"], "page": row["page"],
                "carried_registers": registers, "spoken_carry_de": connective,
                "next_owner": row["owner_trace"], "rationale": rationale,
            })
        revised.append(new)

    by_record_statement_ids = defaultdict(list)
    for row in revised:
        by_record_statement_ids[row["record_unit_id"]].append(row["statement_id"])
    for row in audit:
        ids = by_record_statement_ids[row["record_unit_id"]]
        row["previous_statement_id"] = ids[ids.index(row["next_statement_id"]) - 1]
    write_tsv("HUNDRED_FIFTY_FIRST_13_OPEN_CARRY_AUDIT.tsv", audit)
    write_tsv("HUNDRED_FIFTY_FIRST_116_CARRY_AWARE_CLAUSES.tsv", revised)

    by_record = defaultdict(list)
    for row in revised:
        by_record[row["record_unit_id"]].append(row)
    records = []
    book = ["# Elf Records mit ausgesprochenem Gedächtnisregister", "",
            "Only thirteen boundaries carry state without a close. Their connective now names exactly what the",
            "apprentice retains. All other boundaries remain record starts, fresh steps or visible owner resets.", ""]
    for rid in RECORD_ORDER:
        rows = by_record[rid]
        text = " ".join(row["source_book_clause_de"] for row in rows)
        carries = [row for row in audit if row["record_unit_id"] == rid]
        records.append({
            "record_unit_id": rid, "page": rows[0]["page"], "statement_count": str(len(rows)),
            "explicit_carry_count": str(len(carries)),
            "carried_register_sequence": " || ".join(row["carried_registers"] for row in carries) or "NONE",
            "continuous_carry_aware_text_de": text,
        })
        book += [f"## {rid} · {rows[0]['page']}", "", text, ""]
    write_tsv("HUNDRED_FIFTY_FIRST_ELEVEN_CARRY_AWARE_RECORDS.tsv", records)
    (OUT / "HUNDRED_FIFTY_FIRST_CARRY_AWARE_SOURCE_BOOK.md").write_text("\n".join(book).rstrip() + "\n", encoding="utf-8")

    manual = ["# Gedächtniskarte für offene Übergänge", "",
              "An exact close clears item, preparation, measure, source and target. Without a close and under the",
              "same owner, retain only the registers named by the transition card or immediate clause ending.", ""]
    for row in audit:
        manual.append(f"- {row['previous_statement_id']} -> {row['next_statement_id']}: **{row['spoken_carry_de']}** ({row['carried_registers']})")
    (OUT / "HUNDRED_FIFTY_FIRST_APPRENTICE_MEMORY_CARD.md").write_text("\n".join(manual).rstrip() + "\n", encoding="utf-8")

    register_counts = defaultdict(int)
    for row in audit:
        for register in row["carried_registers"].split("|"):
            register_counts[register] += 1
    report = [
        "# Hunderteinundfünfzigste Runde: die dreizehn offenen Übergänge tragen benannte Register", "",
        "Every open same-owner transition now says what survives. The main memories are active preparation, current",
        "item, prescribed measure, source, target, local station, active extract, sequence or unfinished transfer.",
        "No generic hidden sentence state is needed; the apprentice carries a small concrete work register.", "",
        "Examples are H2-S001->S002 `mit demselben Ansatz und Sollmaß weiter`, H3-S002->S003 `mit diesem",
        "Materialanteil weiter`, B1-S006->S007 `am offenen Ziel in die Überführung weiter`, and B3-S011->S012",
        "`mit dem aus der Quelle überführten Posten weiter`. Exact closure still clears the registers.", "",
        "Next compress the resulting clauses into source-order verbs and objects: identify which cards behave as",
        "imperatives, quantities, anaphors, state words and learned object names in actual spoken order.",
    ]
    (OUT / "HUNDRED_FIFTY_FIRST_OPEN_CARRY_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps({
        "events_unchanged": len(events), "statements": len(revised), "records": len(records),
        "open_carries": len(audit), "register_counts": dict(sorted(register_counts.items())),
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
