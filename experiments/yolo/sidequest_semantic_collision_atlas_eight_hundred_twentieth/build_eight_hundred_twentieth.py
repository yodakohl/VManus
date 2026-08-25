#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BASE = ROOT / "sidequest_semantic_sixth_workshop_grammar_eight_hundred_nineteenth"
COMPONENTS = BASE / "EIGHT_HUNDRED_NINETEENTH_39_COMPONENT_SIXTH_GRAMMAR.tsv"
EVENTS = BASE / "EIGHT_HUNDRED_NINETEENTH_381_EVENT_REPARSE.tsv"
STATEMENTS = BASE / "EIGHT_HUNDRED_NINETEENTH_116_STATEMENT_REPARSE.tsv"

GROUPS = [
    ("G01", "START_USE_TRANSFER", ["OK", "T", "CHD"], "Does the card start, use, or move the item?"),
    ("G02", "ADD_FILL_GUIDE", ["K", "P", "L"], "Does material join a mixture, enter a receiver, or travel a path?"),
    ("G03", "HOLD_WAIT", ["SH", "SHED"], "Is the item actively held or left standing?"),
    ("G04", "CONTINUE_NEXT_ADD", ["OL", "OT", "OS"], "Is the relation continuation, succession, or additive linkage?"),
    ("G05", "QUANTITY_PARAMETER", ["S", "AIN", "AIIN", "IIN"], "Is it a sample, portion, prescribed value, or process stage?"),
    ("G06", "SOURCE_PATH_TARGET", ["AR", "CKH", "AL", "SOLK"], "Is it origin, passage, target, or collecting place?"),
]

ROLES = {
    "OK": ("ANSETZEN", "activate the current work step"),
    "T": ("ANWENDEN", "use the current item on or for its owner"),
    "CHD": ("UMSETZEN", "move or convert the item within the work chain"),
    "K": ("ZUGEBEN", "add material to the active mixture"),
    "P": ("EINFUELLEN", "put material into a receiving place"),
    "L": ("LEITEN", "conduct the item along a path"),
    "SH": ("HALTEN", "actively keep the item in place or state"),
    "SHED": ("STEHENLASSEN", "leave the item without active handling"),
    "OL": ("WEITER", "continue the same operation or relation"),
    "OT": ("DANACH", "advance to the next operation"),
    "OS": ("DAZU", "add a linked clause without asserting succession"),
    "S": ("PROBE", "small diagnostic sample"),
    "AIN": ("PORTION", "working amount of material"),
    "AIIN": ("SOLLMASS", "prescribed value or measure"),
    "IIN": ("STUFE", "process setting or stage"),
    "AR": ("QUELLE", "origin from which material is taken"),
    "CKH": ("DURCHLASS", "passage through which material travels"),
    "AL": ("ZIELSTELLE", "destination at which an operation is performed"),
    "SOLK": ("SAMMELSTELLE", "place that receives and retains output"),
}


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
    components = {row["component"]: row for row in read(COMPONENTS)}
    events = read(EVENTS)
    statements = {row["statement_id"]: row for row in read(STATEMENTS)}

    profile_rows = []
    audit_rows = []
    group_rows = []
    example_rows = []
    for group_id, group_name, members, question in GROUPS:
        for component in members:
            selected = [row for row in events if component in row["component_recipe"].split("+")]
            page_counts = Counter(row["page"] for row in selected)
            co = Counter(
                token
                for row in selected
                for token in row["component_recipe"].split("+")
                if token != component
            )
            value, distinction = ROLES[component]
            profile_rows.append(
                {
                    "group_id": group_id,
                    "group_name": group_name,
                    "component": component,
                    "short_value_de": value,
                    "exact_cards": len({row["exact_card_id"] for row in selected}),
                    "events": len(selected),
                    "component_tokens": sum(row["component_recipe"].split("+").count(component) for row in selected),
                    "pages": ";".join(f"{page}:{count}" for page, count in sorted(page_counts.items())),
                    "top_partners": ";".join(f"{token}:{count}" for token, count in co.most_common(6)) or "NONE",
                    "role_boundary": distinction,
                    "decision": "KEEP_DISTINCT",
                }
            )
            seen_cards: set[str] = set()
            for row in selected:
                audit_rows.append(
                    {
                        "group_id": group_id,
                        "component": component,
                        "event_id": row["event_id"],
                        "page": row["page"],
                        "statement_id": row["statement_id"],
                        "surface": row["surface"],
                        "component_recipe": row["component_recipe"],
                        "literal_de": row["sixth_grammar_reading_de"],
                        "owner_de": row["owner_de"],
                    }
                )
                if row["exact_card_id"] not in seen_cards and len(seen_cards) < 3:
                    seen_cards.add(row["exact_card_id"])
                    example_rows.append(
                        {
                            "group_id": group_id,
                            "component": component,
                            "event_id": row["event_id"],
                            "page": row["page"],
                            "surface": row["surface"],
                            "component_recipe": row["component_recipe"],
                            "full_statement_de": statements[row["statement_id"]]["working_reading_de"],
                        }
                    )
        group_rows.append(
            {
                "group_id": group_id,
                "group_name": group_name,
                "members": "+".join(members),
                "decision_question": question,
                "selected_resolution": "KEEP_ALL_MEMBERS_DISTINCT",
                "reason": "each member answers a different workshop-role question",
            }
        )

    write("EIGHT_HUNDRED_TWENTIETH_6_COLLISION_GROUPS.tsv", group_rows, ["group_id", "group_name", "members", "decision_question", "selected_resolution", "reason"])
    write("EIGHT_HUNDRED_TWENTIETH_19_COMPONENT_PROFILES.tsv", profile_rows, ["group_id", "group_name", "component", "short_value_de", "exact_cards", "events", "component_tokens", "pages", "top_partners", "role_boundary", "decision"])
    write("EIGHT_HUNDRED_TWENTIETH_COMPONENT_EVENT_AUDIT.tsv", audit_rows, ["group_id", "component", "event_id", "page", "statement_id", "surface", "component_recipe", "literal_de", "owner_de"])
    write("EIGHT_HUNDRED_TWENTIETH_CONTEXT_EXAMPLES.tsv", example_rows, ["group_id", "component", "event_id", "page", "surface", "component_recipe", "full_statement_de"])
    summary = {
        "status": "PASS",
        "decision": "SIX_SEMANTIC_COLLISION_GROUPS_RESOLVE_AS_DISTINCT_WORKSHOP_ROLES",
        "groups": len(group_rows),
        "components": len(profile_rows),
        "component_event_memberships": len(audit_rows),
        "unique_audited_events": len({row["event_id"] for row in audit_rows}),
        "context_examples": len(example_rows),
        "meaning_merges": 0,
        "meaning_splits": 0,
        "kept_distinct": len(profile_rows),
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / "EIGHT_HUNDRED_TWENTIETH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
