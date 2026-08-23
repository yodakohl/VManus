#!/usr/bin/env python3
import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R148 = ROOT / "experiments/yolo/sidequest_semantic_bio_apprentice_recitation_hundred_forty_eighth"
R149 = ROOT / "experiments/yolo/sidequest_semantic_herbal_apprentice_recitation_hundred_forty_ninth"
V73 = ROOT / "experiments/yolo/sidequest_theory_candidates_v73"
V74 = ROOT / "experiments/yolo/sidequest_theory_candidates_v74"
RECORD_ORDER = ["H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"]


def read_tsv(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name, rows):
    rows = list(rows)
    with (OUT / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def unique_order(values):
    out = []
    for value in values:
        if not out or out[-1] != value:
            out.append(value)
    return out


def owner_label(row):
    return row.get("whole_plant_owner") or row.get("local_owner_label")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    herbal = read_tsv(R149 / "HUNDRED_FORTY_NINTH_100_EVENT_RECITATION.tsv")
    bio = read_tsv(R148 / "HUNDRED_FORTY_EIGHTH_281_EVENT_RECITATION.tsv")
    events = herbal + bio
    source_terminal = read_tsv(V73 / "V73_SELECTED_100_EVENT_INTERLINEAR.tsv") + read_tsv(V74 / "V74_SELECTED_281_EVENT_INTERLINEAR.tsv")
    terminal_by_serial = {row["event_serial"]: row["terminal_status"] for row in source_terminal}

    unified_events = []
    for row in events:
        unified_events.append({
            "event_serial": row["event_serial"], "record_unit_id": row["record_unit_id"],
            "statement_id": row["statement_id"], "page": row["page"],
            "visible_surface": row["visible_surface"], "master_card_id": row["master_card_id"],
            "visible_owner": owner_label(row), "apprentice_layer": row["apprentice_layer"],
            "card_value_de": row["portable_or_local_value_de"],
            "terminal_status": terminal_by_serial[row["event_serial"]],
        })
    write_tsv("HUNDRED_FIFTIETH_381_SOURCE_EVENTS.tsv", unified_events)

    by_statement = defaultdict(list)
    for row in unified_events:
        by_statement[row["statement_id"]].append(row)
    statement_order = []
    seen = set()
    for row in unified_events:
        if row["statement_id"] not in seen:
            statement_order.append(row["statement_id"])
            seen.add(row["statement_id"])

    statement_rows = []
    previous_by_record = {}
    for sid in statement_order:
        rows = by_statement[sid]
        rid = rows[0]["record_unit_id"]
        owners = unique_order([row["visible_owner"] for row in rows])
        previous = previous_by_record.get(rid)
        if previous is None:
            boundary = "RECORD_START"
            connective = f"Besitzer »{owners[0]}«:"
        elif previous[-1]["visible_owner"] != rows[0]["visible_owner"]:
            boundary = "OWNER_RESET"
            connective = f"Neuer Besitzer »{owners[0]}«:"
        elif previous[-1]["terminal_status"] == "TERMINAL":
            boundary = "FRESH_AFTER_CLOSE"
            connective = "Neuer Schritt:"
        else:
            boundary = "CONTINUE_SAME_OWNER_OPEN"
            connective = "weiter:"
        values = [row["card_value_de"].replace(" · ", " ") for row in rows]
        if len(owners) > 1:
            values.append(f"[innerer Besitzerwechsel zu {owners[-1]}]")
        phrase = " — ".join(values).replace("; schließen", "; Schritt schließen") + "."
        statement_rows.append({
            "statement_id": sid, "record_unit_id": rid, "page": rows[0]["page"],
            "boundary_from_previous": boundary, "connective_de": connective,
            "owner_trace": " -> ".join(owners),
            "terminal_status": rows[-1]["terminal_status"],
            "shared_events": str(sum(row["apprentice_layer"] == "LEHRWORT" for row in rows)),
            "local_events": str(sum(row["apprentice_layer"] == "LOKALKARTE" for row in rows)),
            "source_book_clause_de": f"{connective} {phrase}",
        })
        previous_by_record[rid] = rows
    write_tsv("HUNDRED_FIFTIETH_116_SOURCE_CLAUSES.tsv", statement_rows)

    by_record = defaultdict(list)
    for row in statement_rows:
        by_record[row["record_unit_id"]].append(row)
    record_rows = []
    book = ["# Das Elf-Record-Quellenbuch der Werkstatt", "",
            "`weiter:` joins an open clause to the next statement. `Neuer Schritt:` follows an exact learned",
            "close. `Neuer Besitzer:` follows a visible owner reset. Physical line endings play no role here.", ""]
    for rid in RECORD_ORDER:
        rows = by_record[rid]
        text = " ".join(row["source_book_clause_de"] for row in rows)
        ev = [row for row in unified_events if row["record_unit_id"] == rid]
        record_rows.append({
            "record_unit_id": rid, "page": rows[0]["page"], "statement_count": str(len(rows)),
            "event_count": str(len(ev)), "terminal_statements": str(sum(row["terminal_status"] == "TERMINAL" for row in rows)),
            "open_statements": str(sum(row["terminal_status"] == "NONCLOSE" for row in rows)),
            "open_continuations": str(sum(row["boundary_from_previous"] == "CONTINUE_SAME_OWNER_OPEN" for row in rows)),
            "owner_resets_between_statements": str(sum(row["boundary_from_previous"] == "OWNER_RESET" for row in rows)),
            "continuous_source_book_de": text,
        })
        book += [f"## {rid} · {rows[0]['page']}", "", text, ""]
    write_tsv("HUNDRED_FIFTIETH_ELEVEN_CONTINUOUS_RECORDS.tsv", record_rows)
    (OUT / "HUNDRED_FIFTIETH_COMPLETE_SOURCE_BOOK.md").write_text("\n".join(book).rstrip() + "\n", encoding="utf-8")

    boundary_counts = defaultdict(int)
    for row in statement_rows:
        boundary_counts[row["boundary_from_previous"]] += 1
    report = [
        "# Hundertfünfzigste Runde: ein einziges Elf-Record-Quellenbuch", "",
        "The Herbal and Biological recitations are now one 381-event, 116-clause source book. Exact selected",
        "terminal status decides how clauses sound. Ninety statements close and 26 remain open. Among the 105",
        "within-record boundaries, 86 begin a fresh step after closure, thirteen continue under the same owner",
        "without a sentence restart, and six reset to a new visible owner.", "",
        "This directly implements the user's earlier correction that a thought need not end at a physical line.",
        "The source book does not use line ending at all. It uses only learned closure and owner transition.",
        "The 47-card teaching deck supplies 251 events; the 126 remaining local card types supply 130 events.", "",
        "The next useful improvement is syntactic: give the thirteen open continuations explicit antecedent roles",
        "such as same item, same preparation, same target or unfinished transfer, so `weiter` says what is carried.",
    ]
    (OUT / "HUNDRED_FIFTIETH_SOURCE_BOOK_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps({
        "events": len(unified_events), "statements": len(statement_rows), "records": len(record_rows),
        "terminal_statements": sum(row["terminal_status"] == "TERMINAL" for row in statement_rows),
        "open_statements": sum(row["terminal_status"] == "NONCLOSE" for row in statement_rows),
        "record_starts": boundary_counts["RECORD_START"], "fresh_after_close": boundary_counts["FRESH_AFTER_CLOSE"],
        "open_continuations": boundary_counts["CONTINUE_SAME_OWNER_OPEN"], "owner_resets": boundary_counts["OWNER_RESET"],
        "shared_events": sum(row["apprentice_layer"] == "LEHRWORT" for row in unified_events),
        "local_events": sum(row["apprentice_layer"] == "LOKALKARTE" for row in unified_events),
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
