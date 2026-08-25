#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BASE = ROOT / "sidequest_semantic_sixth_workshop_grammar_eight_hundred_nineteenth"
EVENTS = BASE / "EIGHT_HUNDRED_NINETEENTH_381_EVENT_REPARSE.tsv"
STATEMENTS = BASE / "EIGHT_HUNDRED_NINETEENTH_116_STATEMENT_REPARSE.tsv"
T_REVISIONS = ROOT / "sidequest_semantic_t_work_eight_hundred_twenty_first" / "EIGHT_HUNDRED_TWENTY_FIRST_7_REVISED_STATEMENTS.tsv"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    events = read(EVENTS)
    statements = {row["statement_id"]: row for row in read(STATEMENTS)}
    for row in read(T_REVISIONS):
        statements[row["statement_id"]]["working_reading_de"] = row["revised_reading_de"]

    candidates = [
        {"candidate": "EINFUELLEN", "f11r_fit": "MEDIUM", "f82r_fit": "HIGH", "f83r_fit": "HIGH", "role_collision": "NONE", "decision": "REJECT_OLD_TOO_VESSEL_SPECIFIC"},
        {"candidate": "EINBRINGEN", "f11r_fit": "HIGH", "f82r_fit": "HIGH", "f83r_fit": "HIGH", "role_collision": "NONE", "decision": "SELECT_CORE_VALUE"},
        {"candidate": "ZUGEBEN", "f11r_fit": "HIGH", "f82r_fit": "MEDIUM", "f83r_fit": "MEDIUM", "role_collision": "K", "decision": "REJECT_DUPLICATES_K"},
        {"candidate": "LEITEN", "f11r_fit": "LOW", "f82r_fit": "MEDIUM", "f83r_fit": "MEDIUM", "role_collision": "L", "decision": "REJECT_DUPLICATES_L"},
        {"candidate": "AUFLEGEN", "f11r_fit": "HIGH", "f82r_fit": "LOW", "f83r_fit": "LOW", "role_collision": "NONE", "decision": "REJECT_HERBAL_ONLY"},
        {"candidate": "EINSETZEN", "f11r_fit": "HIGH", "f82r_fit": "HIGH", "f83r_fit": "HIGH", "role_collision": "OK_ACTIVATION", "decision": "REJECT_LESS_DIRECTIONAL"},
    ]

    values = {"K": "ZUGEBEN", "P": "EINBRINGEN", "L": "LEITEN"}
    roles = {"K": "join active mixture", "P": "move inward to receiver or work site", "L": "move along path"}
    audit_rows = []
    for row in events:
        tokens = row["component_recipe"].split("+")
        for component in ("K", "P", "L"):
            if component in tokens:
                audit_rows.append(
                    {
                        "component": component,
                        "selected_value_de": values[component],
                        "event_id": row["event_id"],
                        "page": row["page"],
                        "statement_id": row["statement_id"],
                        "owner_de": row["owner_de"],
                        "surface": row["surface"],
                        "component_recipe": row["component_recipe"],
                        "role_test": roles[component],
                        "full_statement_de": statements[row["statement_id"]]["working_reading_de"],
                    }
                )

    p_events = [row for row in events if "P" in row["component_recipe"].split("+")]
    p_rows = []
    revised_rows = []
    replacements = {
        "H3-S001": ("in den lokalen Empfaenger einfuellen", "in den lokalen Empfaenger einbringen"),
        "B2-S016": ("einfuellen, umsetzen", "einbringen, umsetzen"),
        "B3-S010": ("An der Zielstelle einfuellen und umsetzen", "An der Zielstelle einbringen und umsetzen"),
    }
    for row in p_events:
        old_literal = row["sixth_grammar_reading_de"]
        revised_literal = old_literal.replace("EINFUELLEN", "EINBRINGEN")
        p_rows.append(
            {
                "event_id": row["event_id"],
                "page": row["page"],
                "statement_id": row["statement_id"],
                "owner_de": row["owner_de"],
                "surface": row["surface"],
                "component_recipe": row["component_recipe"],
                "old_literal_de": old_literal,
                "revised_literal_de": revised_literal,
                "receiver_status": "VISIBLE_RECEIVER" if row["page"] in {"f82r", "f83r"} else "LOCAL_WORK_SITE_ONLY",
            }
        )
        statement = statements[row["statement_id"]]
        old_phrase, new_phrase = replacements[row["statement_id"]]
        revised_rows.append(
            {
                "statement_id": row["statement_id"],
                "page": row["page"],
                "owner_noun_de": statement["owner_noun_de"],
                "surface_sequence": statement["surface_sequence"],
                "old_reading_de": statement["working_reading_de"],
                "revised_reading_de": statement["working_reading_de"].replace(old_phrase, new_phrase),
                "p_event": row["event_id"],
            }
        )

    counts = Counter(row["component"] for row in audit_rows)
    distinction_rows = [
        {"component": "K", "short_value_de": "ZUGEBEN", "events": counts["K"], "direction": "toward active mixture", "object_requirement": "added material", "decision": "KEEP"},
        {"component": "P", "short_value_de": "EINBRINGEN", "events": counts["P"], "direction": "inward to receiver or work site", "object_requirement": "receiver explicit or local", "decision": "REVISE"},
        {"component": "L", "short_value_de": "LEITEN", "events": counts["L"], "direction": "along a path", "object_requirement": "path or continuation", "decision": "KEEP"},
    ]

    write("EIGHT_HUNDRED_TWENTY_SECOND_6_P_CANDIDATES.tsv", candidates, ["candidate", "f11r_fit", "f82r_fit", "f83r_fit", "role_collision", "decision"])
    write("EIGHT_HUNDRED_TWENTY_SECOND_3_P_EVENTS.tsv", p_rows, ["event_id", "page", "statement_id", "owner_de", "surface", "component_recipe", "old_literal_de", "revised_literal_de", "receiver_status"])
    write("EIGHT_HUNDRED_TWENTY_SECOND_3_REVISED_STATEMENTS.tsv", revised_rows, ["statement_id", "page", "owner_noun_de", "surface_sequence", "old_reading_de", "revised_reading_de", "p_event"])
    write("EIGHT_HUNDRED_TWENTY_SECOND_51_TRANSFER_MEMBERSHIPS.tsv", audit_rows, ["component", "selected_value_de", "event_id", "page", "statement_id", "owner_de", "surface", "component_recipe", "role_test", "full_statement_de"])
    write("EIGHT_HUNDRED_TWENTY_SECOND_3_TRANSFER_DISTINCTIONS.tsv", distinction_rows, ["component", "short_value_de", "events", "direction", "object_requirement", "decision"])
    summary = {
        "status": "PASS",
        "decision": "P_REVISED_FROM_EINFUELLEN_TO_EINBRINGEN__K_AND_L_RETAINED",
        "p_cards": len({row["exact_card_id"] for row in p_events}),
        "p_events": len(p_events),
        "revised_statements": len(revised_rows),
        "transfer_memberships": len(audit_rows),
        "unique_transfer_events": len({row["event_id"] for row in audit_rows}),
        "k_events": counts["K"],
        "l_events": counts["L"],
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / "EIGHT_HUNDRED_TWENTY_SECOND_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
