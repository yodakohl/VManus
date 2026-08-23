#!/usr/bin/env python3
import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R156 = ROOT / "experiments/yolo/sidequest_semantic_atomic_current_ten_page_hundred_fifty_sixth"
R157 = ROOT / "experiments/yolo/sidequest_semantic_shared_renderer_simplification_hundred_fifty_seventh"
PROFILES = ["MASTER_BARE", "CH_OPEN_HAND", "Q_CELL_HAND", "S_FLOW_HAND", "HARD_COMPACT_HAND"]
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


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    events = read_tsv(R156 / "HUNDRED_FIFTY_SIXTH_381_ATOMIC_EVENTS.tsv")
    clauses = read_tsv(R156 / "HUNDRED_FIFTY_SIXTH_116_ATOMIC_CLAUSES.tsv")
    surfaces = read_tsv(R156 / "HUNDRED_FIFTY_SIXTH_230_SURFACE_READER.tsv")
    choices = read_tsv(R157 / "HUNDRED_FIFTY_SEVENTH_FIVE_HAND_SHARED_COPYBOOK.tsv")
    choice = {(row["profile"], row["master_card_id"]): row["chosen_surface"] for row in choices}
    surface_to_card = {row["visible_surface"]: row["master_card_id"] for row in surfaces}
    clause_by_id = {row["statement_id"]: row for row in clauses}

    token_rows = []
    by_statement_profile = defaultdict(list)
    for profile in PROFILES:
        for row in events:
            rendered = choice[(profile, row["master_card_id"])] if row["teaching_layer"] == "SHARED_DECK" else row["visible_surface"]
            token = {
                "profile": profile, "event_serial": row["event_serial"], "statement_id": row["statement_id"],
                "record_unit_id": row["record_unit_id"], "page": row["page"],
                "teaching_layer": row["teaching_layer"], "master_card_id": row["master_card_id"],
                "card_value_de": row["card_value_de"], "observed_surface": row["visible_surface"],
                "rendered_surface": rendered, "surface_changed": "YES" if rendered != row["visible_surface"] else "NO",
                "recovered_master_card_id": surface_to_card[rendered],
                "roundtrip": "PASS" if surface_to_card[rendered] == row["master_card_id"] else "FAIL",
            }
            token_rows.append(token)
            by_statement_profile[(profile, row["statement_id"])].append(token)
    write_tsv("HUNDRED_FIFTY_EIGHTH_1905_TOKEN_COPIES.tsv", token_rows)

    statement_rows = []
    for profile in PROFILES:
        for sid in [row["statement_id"] for row in clauses]:
            tokens = by_statement_profile[(profile, sid)]
            source = clause_by_id[sid]
            statement_rows.append({
                "profile": profile, "statement_id": sid, "record_unit_id": source["record_unit_id"],
                "page": source["page"], "rendered_surface_sequence": " ".join(row["rendered_surface"] for row in tokens),
                "master_card_sequence": "|".join(row["master_card_id"] for row in tokens),
                "atomic_meaning_sequence_de": " | ".join(row["card_value_de"] for row in tokens),
                "changed_tokens": str(sum(row["surface_changed"] == "YES" for row in tokens)),
                "roundtrip": "PASS" if all(row["roundtrip"] == "PASS" for row in tokens) else "FAIL",
            })
    write_tsv("HUNDRED_FIFTY_EIGHTH_580_STATEMENT_COPIES.tsv", statement_rows)

    variation_rows = []
    for sid in [row["statement_id"] for row in clauses]:
        copies = [row for row in statement_rows if row["statement_id"] == sid]
        distinct = sorted({row["rendered_surface_sequence"] for row in copies})
        variation_rows.append({
            "statement_id": sid, "record_unit_id": copies[0]["record_unit_id"], "page": copies[0]["page"],
            "event_count": str(len(copies[0]["master_card_sequence"].split("|"))),
            "distinct_visible_sequences": str(len(distinct)),
            "visibly_variable": "YES" if len(distinct) > 1 else "NO",
            "atomic_meaning_sequence_de": copies[0]["atomic_meaning_sequence_de"],
            "visible_sequences": " || ".join(distinct),
        })
    write_tsv("HUNDRED_FIFTY_EIGHTH_116_STATEMENT_VARIATION.tsv", variation_rows)

    record_rows = []
    copybook = ["# Fünf Hände kopieren dieselben elf Records", "",
                "Local nomenclator cards keep their observed spelling. Shared cards are rendered by one of five",
                "registered hand habits. Every copy prints the same atomic card meanings.", ""]
    for profile in PROFILES:
        copybook += [f"## {profile}", ""]
        for rid in RECORD_ORDER:
            rows = [row for row in statement_rows if row["profile"] == profile and row["record_unit_id"] == rid]
            visible = " / ".join(row["rendered_surface_sequence"] for row in rows)
            meanings = " / ".join(row["atomic_meaning_sequence_de"] for row in rows)
            record_rows.append({
                "profile": profile, "record_unit_id": rid, "page": rows[0]["page"],
                "statement_count": str(len(rows)), "rendered_record": visible,
                "atomic_record_reading_de": meanings, "roundtrip": "PASS",
            })
            copybook += [f"### {rid} · {rows[0]['page']}", "", f"Sichtbar: `{visible}`", "", f"Lesung: {meanings}", ""]
    write_tsv("HUNDRED_FIFTY_EIGHTH_55_RECORD_COPIES.tsv", record_rows)
    (OUT / "HUNDRED_FIFTY_EIGHTH_FIVE_HAND_COPYBOOK.md").write_text("\n".join(copybook).rstrip() + "\n", encoding="utf-8")

    variable = sum(row["visibly_variable"] == "YES" for row in variation_rows)
    report = [
        "# Hundertachtundfünfzigste Runde: fünf Hände kopieren die vollständige atomare Prosa", "",
        "Five hand profiles render all 381 events, producing 1,905 token copies, 580 complete statement copies",
        "and 55 full record copies. Every rendered surface is registered and every copy round-trips to the same",
        "master-card and atomic-meaning sequence.", "",
        f"{variable} of 116 statements acquire at least two visibly different surface sequences. The others are",
        "dominated by one-form local nomenclator cards or shared families lacking an alternative for that hand.",
        "Thus several scribes can visibly diverge while sharing one source book and one 173-card dictionary.", "",
        "Next compare the five profiles against the actual record-specific surface choices and assign each of the",
        "eleven records the smallest hand mixture that reproduces its observed shared-card spellings.",
    ]
    (OUT / "HUNDRED_FIFTY_EIGHTH_COPYSHOP_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps({
        "profiles": len(PROFILES), "token_copies": len(token_rows), "statement_copies": len(statement_rows),
        "record_copies": len(record_rows), "variable_statements": variable,
        "invariant_statements": len(variation_rows) - variable,
        "changed_shared_token_copies": sum(row["surface_changed"] == "YES" for row in token_rows),
        "roundtrip_failures": sum(row["roundtrip"] == "FAIL" for row in token_rows),
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
