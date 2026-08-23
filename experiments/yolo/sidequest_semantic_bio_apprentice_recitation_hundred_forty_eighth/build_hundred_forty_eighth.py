#!/usr/bin/env python3
import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R147 = ROOT / "experiments/yolo/sidequest_semantic_recurrent_specialist_promotion_hundred_forty_seventh"
V74 = ROOT / "experiments/yolo/sidequest_theory_candidates_v74"
BIO_PAGES = {"f81v", "f82r", "f83r"}
RECORD_ORDER = ["B1", "B2", "B3", "B4", "B5", "B6"]


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


def speak(values):
    text = " — ".join(values)
    text = text.replace(" · ", " ")
    text = text.replace("; schließen", "; Schritt schließen")
    text = text.replace("; Schluss", "; Schluss")
    return text + "."


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    cards = read_tsv(R147 / "HUNDRED_FORTY_SEVENTH_173_PROMOTED_DICTIONARY.tsv")
    all_events = read_tsv(R147 / "HUNDRED_FORTY_SEVENTH_381_PROMOTED_EVENTS.tsv")
    bio_events = [row for row in all_events if row["page"] in BIO_PAGES]
    owners = read_tsv(V74 / "V74_SELECTED_281_EVENT_INTERLINEAR.tsv")
    owner_by_serial = {row["event_serial"]: row for row in owners}
    card_by_id = {row["master_card_id"]: row for row in cards}

    event_rows = []
    for row in bio_events:
        serial = str(int(row["event_serial"]))
        owner = owner_by_serial[serial]
        shared = row["portable_scope"].startswith("ACTIVE")
        event_rows.append({
            "event_serial": serial, "statement_id": row["statement_id"], "record_unit_id": row["record_unit_id"],
            "page": row["page"], "visible_surface": row["visible_surface"], "master_card_id": row["master_card_id"],
            "local_image_owner": owner["local_image_owner"], "local_owner_label": owner["local_owner_label"],
            "owner_status": owner["owner_status"], "owner_break_before": owner["owner_break_before"],
            "apprentice_layer": "LEHRWORT" if shared else "LOKALKARTE",
            "portable_or_local_value_de": row["portable_card_value_de"],
            "spoken_token_de": row["portable_card_value_de"].replace(" · ", " "),
            "scope_guard": "BIO_SHARED" if row["portable_scope"] == "ACTIVE_BIO_CROSS_RECORD" else ("CROSS_RECORD" if shared else "COPY_LOCAL_WHOLE"),
        })
    write_tsv("HUNDRED_FORTY_EIGHTH_281_EVENT_RECITATION.tsv", event_rows)

    by_statement = defaultdict(list)
    for row in event_rows:
        by_statement[row["statement_id"]].append(row)
    statement_rows = []
    for sid, rows in by_statement.items():
        owner_trace = unique_order([row["local_owner_label"] for row in rows])
        values = [row["portable_or_local_value_de"] for row in rows]
        layer_trace = ["G" if row["apprentice_layer"] == "LEHRWORT" else "L" for row in rows]
        statement_rows.append({
            "statement_id": sid, "record_unit_id": rows[0]["record_unit_id"], "page": rows[0]["page"],
            "visible_owner_trace": " -> ".join(owner_trace),
            "owner_break_inside_statement": "YES" if len(owner_trace) > 1 else "NO",
            "card_layer_trace": " ".join(layer_trace),
            "shared_card_count": str(layer_trace.count("G")), "local_card_count": str(layer_trace.count("L")),
            "terse_apprentice_recitation_de": f"Beim Besitzer »{'«; dann Besitzer »'.join(owner_trace)}«: {speak(values)}",
        })
    statement_rows.sort(key=lambda row: int(row["statement_id"].split("-S")[1]))
    statement_rows.sort(key=lambda row: RECORD_ORDER.index(row["record_unit_id"]))
    write_tsv("HUNDRED_FORTY_EIGHTH_97_STATEMENT_RECITATION.tsv", statement_rows)

    by_record = defaultdict(list)
    for row in statement_rows:
        by_record[row["record_unit_id"]].append(row)
    record_rows = []
    readable = ["# Sechs Biological-Records im Lehrmeister-Telegramm", "",
                "`G` means shared teaching word; `L` means a locally memorized whole card. The owner is pointed",
                "to before the cards are spoken. A change after `dann` is a real visible owner reset.", ""]
    for rid in RECORD_ORDER:
        rows = by_record[rid]
        record_events = [row for row in event_rows if row["record_unit_id"] == rid]
        owners_used = unique_order([row["local_owner_label"] for row in record_events])
        record_rows.append({
            "record_unit_id": rid, "page": rows[0]["page"], "statement_count": str(len(rows)),
            "event_count": str(len(record_events)),
            "shared_events": str(sum(row["apprentice_layer"] == "LEHRWORT" for row in record_events)),
            "local_events": str(sum(row["apprentice_layer"] == "LOKALKARTE" for row in record_events)),
            "visible_owner_count": str(len(owners_used)), "visible_owner_sequence": " -> ".join(owners_used),
            "teaching_instruction": "Point to owner; speak G from deck; copy L as one learned word; close only when the card says so",
        })
        readable += [f"## {rid} · {rows[0]['page']}", ""]
        for row in rows:
            readable += [f"- **{row['statement_id']}** `{row['card_layer_trace']}` — {row['terse_apprentice_recitation_de']}"]
        readable.append("")
    write_tsv("HUNDRED_FORTY_EIGHTH_SIX_RECORD_SUMMARY.tsv", record_rows)
    (OUT / "HUNDRED_FORTY_EIGHTH_SIX_CONTINUOUS_RECITATIONS.md").write_text("\n".join(readable).rstrip() + "\n", encoding="utf-8")

    bio_active_cards = {row["master_card_id"] for row in event_rows if row["apprentice_layer"] == "LEHRWORT"}
    bio_local_cards = {row["master_card_id"] for row in event_rows if row["apprentice_layer"] == "LOKALKARTE"}
    report = [
        "# Hundertachtundvierzigste Runde: sechs Biological-Records sind vollständig sprechbar", "",
        "All 281 Biological events and 97 statements are now recited with their selected image-local owner.",
        "The apprentice uses 43 shared cards for 196 events and copies 81 local whole-card types for 85 events.",
        "Every token is marked G (teaching word) or L (local card), so fluency no longer hides the nomenclator.", "",
        "The six records retain the visible station changes from the image-first atlas. If a statement crosses",
        "a visible owner break, the recitation explicitly says `dann` and names the next owner. No global water",
        "direction or closed machine is inferred. The resulting style is terse but learnable: point, speak the",
        "shared word, copy the local word, and close only when the exact card carries closure.", "",
        "Next give the five Herbal records the same treatment. Their picture owner should supply the plant article",
        "while the card deck supplies only material, portion, source, preparation and operation words.",
    ]
    (OUT / "HUNDRED_FORTY_EIGHTH_BIO_RECITATION_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps({
        "bio_events": len(event_rows), "bio_statements": len(statement_rows), "bio_records": len(record_rows),
        "shared_events": sum(row["apprentice_layer"] == "LEHRWORT" for row in event_rows),
        "local_events": sum(row["apprentice_layer"] == "LOKALKARTE" for row in event_rows),
        "shared_card_types_used": len(bio_active_cards), "local_card_types_used": len(bio_local_cards),
        "owner_break_statements": sum(row["owner_break_inside_statement"] == "YES" for row in statement_rows),
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
