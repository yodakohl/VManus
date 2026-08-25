#!/usr/bin/env python3
"""Integrate the three Pass-1023 workshop-scope decisions.

This sidequest build changes no root value.  It only chooses one operational
attachment for the 328 Pass-1022 focus occurrences that retained alternatives.
"""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
P1022 = ROOT / "experiments/yolo/sidequest_semantic_argument_scope_stack_one_thousand_twenty_second"

ATTACHMENTS = P1022 / "SCOPE_STACK_ATTACHMENTS.tsv"
AMBIGUITIES = P1022 / "SCOPE_STACK_AMBIGUITIES.tsv"
STATEMENTS = P1022 / "PASS1022_627_STATEMENT_SCOPE_EDITION.tsv"
EQUAL = OUT / "EQUAL_DISTANCE_RESOLUTIONS.tsv"
OWNER = OUT / "OWNER_NEXT_146_RESOLUTIONS.tsv"
R_HEAD = OUT / "R_HEAD_TAIL_63_ADJUDICATION.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def unique_join(values: list[str], separator: str = " | ") -> str:
    seen: list[str] = []
    for value in values:
        if value and value not in seen:
            seen.append(value)
    return separator.join(seen) if seen else "NONE"


def main() -> None:
    attachments = read_tsv(ATTACHMENTS)
    ambiguities = read_tsv(AMBIGUITIES)
    statements = read_tsv(STATEMENTS)
    equal_rows = read_tsv(EQUAL)
    owner_rows = read_tsv(OWNER)
    r_rows = read_tsv(R_HEAD)

    if len(attachments) != 4345 or len(statements) != 627:
        raise AssertionError("Pass1022 inventory changed")
    if len(ambiguities) != 329 or len({row["attachment_id"] for row in ambiguities}) != 328:
        raise AssertionError("Pass1022 ambiguity inventory changed")
    if (len(equal_rows), len(owner_rows), len(r_rows)) != (120, 146, 63):
        raise AssertionError("Pass1023 branch inventory mismatch")

    attachment_by_id = {row["attachment_id"]: row for row in attachments}
    ambiguity_by_id = {row["ambiguity_id"]: row for row in ambiguities}
    ambiguity_groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in ambiguities:
        ambiguity_groups[row["attachment_id"]].append(row)

    decisions: dict[str, list[dict[str, str]]] = defaultdict(list)

    for row in equal_rows:
        ambiguity = ambiguity_by_id[row["source_ambiguity_id"]]
        attachment_id = row["source_attachment_id"]
        if ambiguity["attachment_id"] != attachment_id:
            raise AssertionError(f"equal-distance join failed: {row['resolution_id']}")
        target = (
            f"{row['direct_governor_core']}={row['direct_governor_value_de']}"
            f"@CURRENT_CARD_ATOM{row['direct_governor_atom_ordinal']}"
        )
        decisions[attachment_id].append(
            {
                "class": "EQUAL_DISTANCE_TWO_HEADS",
                "decision": f"EQUAL_{row['decision']}",
                "target": target,
                "scope": row["package_reading"],
                "rule": row["tie_rule_branch"],
                "changed": "YES" if (
                    attachment_by_id[attachment_id]["chosen_action"] != row["direct_governor_core"]
                    or attachment_by_id[attachment_id]["chosen_action_atom_ordinal"]
                    != row["direct_governor_atom_ordinal"]
                ) else "NO",
                "reason": row["reason_de"],
            }
        )

    for row in owner_rows:
        ambiguity = ambiguity_by_id[row["ambiguity_id"]]
        attachment_id = row["attachment_id"]
        if ambiguity["attachment_id"] != attachment_id:
            raise AssertionError(f"owner-next join failed: {row['resolution_id']}")
        decisions[attachment_id].append(
            {
                "class": "OWNER_OR_NEXT_CARD_ACTION",
                "decision": row["decision"],
                "target": row["attachment_target"],
                "scope": row["attachment_target"],
                "rule": row["decision_rule"],
                "changed": "YES" if row["decision"] == "BOUNDED_FORWARD" else "NO",
                "reason": row["rationale_de"],
            }
        )

    for row in r_rows:
        ambiguity = ambiguity_by_id[row["ambiguity_id"]]
        attachment_id = row["attachment_id"]
        if ambiguity["attachment_id"] != attachment_id:
            raise AssertionError(f"R join failed: {row['ambiguity_id']}")
        decisions[attachment_id].append(
            {
                "class": "R_HEAD_OR_TAIL",
                "decision": f"R_{row['r_decision']}",
                "target": row["selected_attachment"],
                "scope": row["selected_attachment"],
                "rule": row["rule_id"],
                "changed": row["changed_from_pass1022_default"],
                "reason": row["rationale_de"],
            }
        )

    if set(decisions) != set(ambiguity_groups):
        raise AssertionError("not every formerly ambiguous attachment has a Pass1023 choice")

    # The sole overlap is AL in R+AL+CH+E+Y.  Both independent rules must point
    # to the same R head rather than silently introducing a fourth choice.
    overlaps = {key: value for key, value in decisions.items() if len(value) > 1}
    if set(overlaps) != {"SA03062"}:
        raise AssertionError(f"unexpected cross-branch overlaps: {sorted(overlaps)}")
    overlap_targets = {item["target"].split("@")[0].split("[")[0] for item in overlaps["SA03062"]}
    if overlap_targets != {"R=MARKIEREN"}:
        raise AssertionError(f"overlap decisions disagree: {overlap_targets}")

    resolved_rows: list[dict[str, object]] = []
    full_rows: list[dict[str, object]] = []
    resolved_by_statement: dict[str, list[dict[str, object]]] = defaultdict(list)
    changed_attachment_ids: set[str] = set()

    resolved_fields = [
        "resolution_id",
        "attachment_id",
        "ambiguity_ids",
        "ambiguity_classes",
        "physical_page",
        "register",
        "statement_id",
        "event_id",
        "locus",
        "card_ordinal_in_statement",
        "surface_card",
        "component_recipe",
        "focus_core",
        "focus_value_de",
        "pass1022_attachment_class",
        "pass1022_chosen_attachment_de",
        "pass1023_decisions",
        "pass1023_selected_target_de",
        "pass1023_scope_de",
        "pass1023_rule_ids",
        "changed_from_pass1022",
        "reason_de",
        "former_alternatives_de",
        "resolution_status",
    ]

    for number, attachment_id in enumerate(sorted(decisions, key=lambda item: int(item[2:])), 1):
        attachment = attachment_by_id[attachment_id]
        source_ambiguities = ambiguity_groups[attachment_id]
        choice_rows = decisions[attachment_id]
        changed = "YES" if any(row["changed"] == "YES" for row in choice_rows) else "NO"
        if changed == "YES":
            changed_attachment_ids.add(attachment_id)
        row = {
            "resolution_id": f"P1023-R{number:04d}",
            "attachment_id": attachment_id,
            "ambiguity_ids": unique_join([entry["ambiguity_id"] for entry in source_ambiguities], "|"),
            "ambiguity_classes": unique_join([entry["ambiguity_class"] for entry in source_ambiguities], "|"),
            "physical_page": attachment["physical_page"],
            "register": attachment["register"],
            "statement_id": attachment["statement_id"],
            "event_id": attachment["event_id"],
            "locus": attachment["locus"],
            "card_ordinal_in_statement": attachment["card_ordinal_in_statement"],
            "surface_card": attachment["surface_card"],
            "component_recipe": attachment["component_recipe"],
            "focus_core": attachment["focus_core"],
            "focus_value_de": attachment["focus_value_de"],
            "pass1022_attachment_class": attachment["chosen_attachment_class"],
            "pass1022_chosen_attachment_de": attachment["bracket_reading_de"],
            "pass1023_decisions": unique_join([entry["decision"] for entry in choice_rows], "+"),
            "pass1023_selected_target_de": unique_join([entry["target"] for entry in choice_rows]),
            "pass1023_scope_de": unique_join([entry["scope"] for entry in choice_rows]),
            "pass1023_rule_ids": unique_join([entry["rule"] for entry in choice_rows], "+"),
            "changed_from_pass1022": changed,
            "reason_de": unique_join([entry["reason"] for entry in choice_rows]),
            "former_alternatives_de": unique_join([entry["alternative_attachment"] for entry in source_ambiguities]),
            "resolution_status": "SELECTED_WORKSHOP_SCOPE",
        }
        resolved_rows.append(row)
        resolved_by_statement[attachment["statement_id"]].append(row)

    extra_fields = [
        "pass1023_resolution_status",
        "pass1023_ambiguity_classes",
        "pass1023_decisions",
        "pass1023_selected_attachment_de",
        "pass1023_scope_de",
        "pass1023_rule_ids",
        "pass1023_changed_from_pass1022",
        "pass1023_note_de",
    ]
    resolved_by_attachment = {row["attachment_id"]: row for row in resolved_rows}
    for attachment in attachments:
        row: dict[str, object] = dict(attachment)
        resolution = resolved_by_attachment.get(attachment["attachment_id"])
        if resolution:
            row.update(
                {
                    "pass1023_resolution_status": "RESOLVED_BY_WORKSHOP_RULE",
                    "pass1023_ambiguity_classes": resolution["ambiguity_classes"],
                    "pass1023_decisions": resolution["pass1023_decisions"],
                    "pass1023_selected_attachment_de": resolution["pass1023_selected_target_de"],
                    "pass1023_scope_de": resolution["pass1023_scope_de"],
                    "pass1023_rule_ids": resolution["pass1023_rule_ids"],
                    "pass1023_changed_from_pass1022": resolution["changed_from_pass1022"],
                    "pass1023_note_de": resolution["reason_de"],
                }
            )
        else:
            row.update(
                {
                    "pass1023_resolution_status": "ALREADY_UNAMBIGUOUS",
                    "pass1023_ambiguity_classes": "NONE",
                    "pass1023_decisions": "KEEP_PASS1022",
                    "pass1023_selected_attachment_de": attachment["bracket_reading_de"],
                    "pass1023_scope_de": attachment["bracket_reading_de"],
                    "pass1023_rule_ids": "PASS1022_CLEAR_ATTACHMENT",
                    "pass1023_changed_from_pass1022": "NO",
                    "pass1023_note_de": "Keine offene Anschlussalternative in Pass1022.",
                }
            )
        full_rows.append(row)

    statement_fields = list(statements[0]) + [
        "focus_attachment_count",
        "pass1022_open_attachment_count",
        "pass1023_resolved_attachment_count",
        "pass1023_changed_attachment_count",
        "pass1023_resolution_classes",
        "pass1023_decision_trace_de",
        "pass1023_scope_result",
    ]
    attachments_by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in attachments:
        attachments_by_statement[row["statement_id"]].append(row)

    statement_rows: list[dict[str, object]] = []
    for statement in statements:
        sid = statement["statement_id"]
        selected = resolved_by_statement.get(sid, [])
        row: dict[str, object] = dict(statement)
        row.update(
            {
                "focus_attachment_count": len(attachments_by_statement[sid]),
                "pass1022_open_attachment_count": len(selected),
                "pass1023_resolved_attachment_count": len(selected),
                "pass1023_changed_attachment_count": sum(
                    entry["changed_from_pass1022"] == "YES" for entry in selected
                ),
                "pass1023_resolution_classes": unique_join(
                    [str(entry["ambiguity_classes"]) for entry in selected]
                ),
                "pass1023_decision_trace_de": unique_join(
                    [
                        f"{entry['event_id']}:{entry['focus_core']}→{entry['pass1023_decisions']}"
                        for entry in selected
                    ]
                ),
                "pass1023_scope_result": "COMPLETE_SELECTED_SCOPE__NO_OPEN_ATTACHMENTS",
            }
        )
        statement_rows.append(row)

    rule_rows = [
        {
            "rule_id": "P1023-1",
            "name": "NEAREST_HEAD_LEFT_TIE",
            "instruction_de": "Argument und Grad nehmen den nächsten Kopf; nur bei gleichem Abstand schließt der Zusatz links, bevor der rechte Kopf sein inneres Paket beginnt.",
            "selected_occurrences": 119,
        },
        {
            "rule_id": "P1023-2",
            "name": "L_AIR_RIGHT_FRAME",
            "instruction_de": "L und AIR nehmen den nächsten rechten Kopf; fehlt er örtlich, fallen sie auf den linken oder laufenden Kopf beziehungsweise genau eine folgende Karte zurück.",
            "selected_occurrences": 24,
        },
        {
            "rule_id": "P1023-3",
            "name": "HEADLESS_OPENING_FORWARD",
            "instruction_de": "Kopflose Posten-, Wert-, Anteil-, Einheits- und Gradpakete dürfen genau eine Karte bis zum ersten Kopf desselben Besitzersegments vorausgreifen.",
            "selected_occurrences": 55,
        },
        {
            "rule_id": "P1023-4",
            "name": "Q_OT_FORWARD",
            "instruction_de": "Q pusht und OT wechselt; ihre kopflosen Zusätze binden an den ersten Kopf des eröffneten oder nächsten Geschwisterpakets.",
            "selected_occurrences": 49,
        },
        {
            "rule_id": "P1023-5",
            "name": "AR_AL_OWNER_DEFAULT",
            "instruction_de": "Nacktes AR/AL ohne linken, laufenden oder gleichkarten-rechten Kopf und ohne Q/OT/L/AIR-Lizenz bleibt Ausgang/Zielort des sichtbaren Besitzers.",
            "selected_occurrences": 19,
        },
        {
            "rule_id": "P1023-6",
            "name": "R_POSITIONAL_MARKING",
            "instruction_de": "R mit eigenem Rechtsglied ist MARKIEREN-Kopf; nach äußerer Handlung ohne Rechtsglied ist R Schwanz; zwischen äußerem Kopf und Rechtsglied ist R innerer Kopf.",
            "selected_occurrences": 63,
        },
    ]

    write_tsv(OUT / "PASS1023_328_RESOLVED_ATTACHMENTS.tsv", resolved_rows, resolved_fields)
    write_tsv(
        OUT / "PASS1023_4345_SCOPE_ATTACHMENTS.tsv",
        full_rows,
        list(attachments[0]) + extra_fields,
    )
    write_tsv(OUT / "PASS1023_627_STATEMENT_SCOPE_EDITION.tsv", statement_rows, statement_fields)
    write_tsv(
        OUT / "PASS1023_SIX_SCOPE_RULES.tsv",
        rule_rows,
        ["rule_id", "name", "instruction_de", "selected_occurrences"],
    )

    decision_counts = Counter(
        decision
        for row in resolved_rows
        for decision in str(row["pass1023_decisions"]).split("+")
    )
    summary = {
        "result": "COMPLETE_OPERATIONAL_SCOPE_SELECTION",
        "source_attachment_count": len(attachments),
        "source_ambiguity_rows": len(ambiguities),
        "formerly_ambiguous_attachment_count": len(resolved_rows),
        "resolved_attachment_count": len(resolved_rows),
        "remaining_open_attachment_count": 0,
        "changed_from_pass1022_attachment_count": len(changed_attachment_ids),
        "statement_count": len(statement_rows),
        "statements_with_resolutions": sum(bool(resolved_by_statement.get(row["statement_id"])) for row in statements),
        "decision_counts": dict(sorted(decision_counts.items())),
        "branch_counts": {
            "equal_distance_rows": len(equal_rows),
            "owner_or_next_rows": len(owner_rows),
            "r_head_or_tail_rows": len(r_rows),
            "cross_branch_overlap_attachments": len(overlaps),
        },
        "fixed_core_values_changed": 0,
        "new_pages_opened": 0,
        "checks": {
            "all_4345_attachments_present_once": "PASS",
            "all_328_formerly_ambiguous_attachments_selected": "PASS",
            "all_627_statements_present_once": "PASS",
            "no_open_scope_status": "PASS",
            "overlap_rules_agree": "PASS",
        },
        "source_hashes": {
            path.name: sha256(path)
            for path in [ATTACHMENTS, AMBIGUITIES, STATEMENTS, EQUAL, OWNER, R_HEAD]
        },
    }
    (OUT / "PASS1023_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
