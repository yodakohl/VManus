#!/usr/bin/env python3
import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R147 = ROOT / "experiments/yolo/sidequest_semantic_recurrent_specialist_promotion_hundred_forty_seventh"
V73 = ROOT / "experiments/yolo/sidequest_theory_candidates_v73"
HERBAL_PAGES = {"f10r", "f11r", "f55v", "f56r"}
RECORD_ORDER = ["H1", "H2", "H3", "H4", "H5"]


def read_tsv(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name, rows):
    rows = list(rows)
    with (OUT / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def speak(values):
    text = " — ".join(values).replace(" · ", " ")
    return text.replace("; schließen", "; Schritt schließen").replace("; Schluss", "; Schluss") + "."


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    all_events = read_tsv(R147 / "HUNDRED_FORTY_SEVENTH_381_PROMOTED_EVENTS.tsv")
    herbal_events = [row for row in all_events if row["page"] in HERBAL_PAGES]
    owners = read_tsv(V73 / "V73_SELECTED_100_EVENT_INTERLINEAR.tsv")
    owner_by_serial = {row["event_serial"]: row for row in owners}

    event_rows = []
    for row in herbal_events:
        serial = str(int(row["event_serial"]))
        owner = owner_by_serial[serial]
        shared = row["portable_scope"].startswith("ACTIVE")
        event_rows.append({
            "event_serial": serial, "statement_id": row["statement_id"], "record_unit_id": row["record_unit_id"],
            "page": row["page"], "visible_surface": row["visible_surface"], "master_card_id": row["master_card_id"],
            "whole_plant_owner": owner["whole_plant_owner"], "owner_status": owner["owner_status"],
            "apprentice_layer": "LEHRWORT" if shared else "LOKALKARTE",
            "portable_or_local_value_de": row["portable_card_value_de"],
            "spoken_token_de": row["portable_card_value_de"].replace(" · ", " "),
            "scope_guard": "CROSS_RECORD" if shared else "COPY_LOCAL_WHOLE",
            "picture_supplies": "WHOLE_PLANT_OWNER_ONLY__NOT_SPECIES_PART_MEDIUM_DISEASE_OR_USE",
        })
    write_tsv("HUNDRED_FORTY_NINTH_100_EVENT_RECITATION.tsv", event_rows)

    by_statement = defaultdict(list)
    for row in event_rows:
        by_statement[row["statement_id"]].append(row)
    statement_rows = []
    for sid, rows in by_statement.items():
        values = [row["portable_or_local_value_de"] for row in rows]
        layer_trace = ["G" if row["apprentice_layer"] == "LEHRWORT" else "L" for row in rows]
        owner = rows[0]["whole_plant_owner"]
        statement_rows.append({
            "statement_id": sid, "record_unit_id": rows[0]["record_unit_id"], "page": rows[0]["page"],
            "whole_plant_owner": owner, "card_layer_trace": " ".join(layer_trace),
            "shared_card_count": str(layer_trace.count("G")), "local_card_count": str(layer_trace.count("L")),
            "terse_apprentice_recitation_de": f"Bei der Bildpflanze »{owner}«: {speak(values)}",
            "forbidden_automatic_expansion": "species|root|leaf|flower|water|wine|oil|disease|body part|dose unit",
        })
    statement_rows.sort(key=lambda row: int(row["statement_id"].split("-S")[1]))
    statement_rows.sort(key=lambda row: RECORD_ORDER.index(row["record_unit_id"]))
    write_tsv("HUNDRED_FORTY_NINTH_19_STATEMENT_RECITATION.tsv", statement_rows)

    by_record = defaultdict(list)
    for row in statement_rows:
        by_record[row["record_unit_id"]].append(row)
    readable = ["# Fünf Herbal-Records im Lehrmeister-Telegramm", "",
                "The drawn whole plant is the silent article owner. `G` is a shared teaching card and `L` a",
                "locally memorized whole card. Plant species, part, liquid, disease and use are not added unless",
                "the learned card itself says so.", ""]
    record_rows = []
    for rid in RECORD_ORDER:
        rows = by_record[rid]
        record_events = [row for row in event_rows if row["record_unit_id"] == rid]
        owner = record_events[0]["whole_plant_owner"]
        record_rows.append({
            "record_unit_id": rid, "page": rows[0]["page"], "whole_plant_owner": owner,
            "statement_count": str(len(rows)), "event_count": str(len(record_events)),
            "shared_events": str(sum(row["apprentice_layer"] == "LEHRWORT" for row in record_events)),
            "local_events": str(sum(row["apprentice_layer"] == "LOKALKARTE" for row in record_events)),
            "teaching_instruction": "Point to whole plant; speak G; copy L whole; never invent species part medium disease or use",
        })
        readable += [f"## {rid} · {rows[0]['page']} · `{owner}`", ""]
        for row in rows:
            readable += [f"- **{row['statement_id']}** `{row['card_layer_trace']}` — {row['terse_apprentice_recitation_de']}"]
        readable.append("")
    write_tsv("HUNDRED_FORTY_NINTH_FIVE_RECORD_SUMMARY.tsv", record_rows)
    (OUT / "HUNDRED_FORTY_NINTH_FIVE_CONTINUOUS_RECITATIONS.md").write_text("\n".join(readable).rstrip() + "\n", encoding="utf-8")

    report = [
        "# Hundertneunundvierzigste Runde: fünf Herbal-Records sind vollständig sprechbar", "",
        "All 100 Herbal events and 19 statements now use the same owner-first teaching method as Biological.",
        "Twenty-one shared card types speak 55 events; 45 local whole-card types speak the remaining 45 events.",
        "The whole drawn plant is pointed to once as article owner. Species, plant part, water, wine, oil, illness,",
        "body part and exact dose are not supplied automatically.", "",
        "This yields an important architectural contrast. Herbal is nearly half nomenclator because each pictured",
        "article carries many one-off material/preparation words. Biological is much more repetitive and operational.",
        "The same workshop can therefore teach Herbal by picture plus local card list and Bio by a larger shared",
        "action deck, without assuming that either page writes ordinary continuous prose.", "",
        "Next join the five Herbal and six Biological recitations into one eleven-record source book and inspect",
        "which apparent sentence boundaries disappear when statements are read as sequential workshop clauses.",
    ]
    (OUT / "HUNDRED_FORTY_NINTH_HERBAL_RECITATION_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps({
        "herbal_events": len(event_rows), "herbal_statements": len(statement_rows), "herbal_records": len(record_rows),
        "shared_events": sum(row["apprentice_layer"] == "LEHRWORT" for row in event_rows),
        "local_events": sum(row["apprentice_layer"] == "LOKALKARTE" for row in event_rows),
        "shared_card_types_used": len({row["master_card_id"] for row in event_rows if row["apprentice_layer"] == "LEHRWORT"}),
        "local_card_types_used": len({row["master_card_id"] for row in event_rows if row["apprentice_layer"] == "LOKALKARTE"}),
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
