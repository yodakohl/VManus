#!/usr/bin/env python3
"""Build an anonymous four-register ellipsis trace over V61 statements."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
V61 = ROOT / "experiments/yolo/sidequest_theory_candidates_v61"
STATEMENTS_IN = V61 / "V61_SELECTED_116_SOURCE_STATEMENTS.tsv"
BOUNDARIES_IN = V61 / "V61_SELECTED_46_LINE_BOUNDARIES.tsv"


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        out = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        out.writeheader()
        out.writerows(rows)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def contains(skeleton, value):
    return value in skeleton


def main():
    statements = read(STATEMENTS_IN)
    boundaries = read(BOUNDARIES_IN)
    by_record = defaultdict(list)
    for row in statements:
        by_record[row["record_unit_id"]].append(row)

    trace = []
    edges = []
    inventory = []
    operation_counts = Counter()

    for record, rows in by_record.items():
        owner = f"OWNER_{record}"
        active_serial = 0
        target_serial = 0
        active = "NONE"
        previous = "NONE"
        target = "NONE"
        record_active_ids = []
        record_target_ids = []
        prior_statement = None

        for ordinal, row in enumerate(rows, 1):
            entry = row["entry_boundary_class"]
            pre_active, pre_previous, pre_target = active, previous, target
            operations = ["CARRY_OWNER"]
            if ordinal == 1:
                active_serial += 1
                active = f"ITEM_{record}_{active_serial:02d}"
                record_active_ids.append(active)
                operations.append("INTRODUCE_ACTIVE_ITEM")
            elif entry in ("CONTINUE_SAME_CLAUSE", "RESUME_ACTIVE_ITEM", "NEXT_PARALLEL_CELL", "WITHIN_LOCUS_FIELD_BOUNDARY"):
                previous = active
                operations.append("STORE_PREVIOUS_STATE")
                if entry == "RESUME_ACTIVE_ITEM":
                    operations.append("RESUME_ACTIVE_ITEM")
                elif entry in ("NEXT_PARALLEL_CELL", "WITHIN_LOCUS_FIELD_BOUNDARY"):
                    operations.extend(["CARRY_ACTIVE_ITEM", "RESET_TARGET"])
                    target = "NONE"
                else:
                    operations.append("CARRY_ACTIVE_ITEM")
            else:
                previous = active
                active_serial += 1
                active = f"ITEM_{record}_{active_serial:02d}"
                record_active_ids.append(active)
                operations.extend(["STORE_PREVIOUS_ITEM", "INTRODUCE_ACTIVE_ITEM"])
                target = "NONE"
                operations.append("RESET_TARGET")

            skeleton = row["selected_short_card_skeleton"]
            if contains(skeleton, "ZIEL?"):
                target_serial += 1
                target = f"TARGET_{record}_{target_serial:02d}"
                record_target_ids.append(target)
                operations.append("INTRODUCE_TARGET_SLOT")
            elif target != "NONE" and entry in ("CONTINUE_SAME_CLAUSE", "RESUME_ACTIVE_ITEM"):
                operations.append("CARRY_TARGET")

            if contains(skeleton, "VORIGES?"):
                operations.append("SELECT_PREVIOUS_ITEM")
                resolved_previous = previous
            else:
                resolved_previous = "NOT_SELECTED"

            need_target = any(contains(skeleton, token) for token in ("ZIEL?", "ANWENDEN?", "SPÜLEN?", "ABLASSEN?"))
            missing = ["PICTURE_OWNER_REFERENT", "ACTIVE_ITEM_REFERENT"]
            if need_target:
                missing.append("TARGET_REFERENT")
            if contains(skeleton, "VORIGES?"):
                missing.append("PREVIOUS_ITEM_ANTECEDENT")
            evidence = ["RECORD_MEMBERSHIP_OWNER", f"ENTRY={entry}"]
            if skeleton != "NO_SELECTED_SHORT_CARD":
                evidence.append("EXACT_V60_SHORT_CARD")
            else:
                evidence.append("LOCAL_EXEMPLAR_ONLY")

            for operation in operations:
                operation_counts[operation] += 1
            trace.append({
                "statement_id": row["statement_id"],
                "record_unit_id": record,
                "page": row["page"],
                "statement_ordinal": ordinal,
                "entry_boundary_class": entry,
                "selected_short_card_skeleton": skeleton,
                "pre_owner": owner,
                "pre_active_item": pre_active,
                "pre_target": pre_target,
                "pre_previous_item": pre_previous,
                "register_operations": "|".join(operations),
                "resolved_previous_for_voriges": resolved_previous,
                "post_owner": owner,
                "post_active_item": active,
                "post_target": target,
                "post_previous_item": previous,
                "required_silent_slots": "|".join(missing),
                "evidence_channels": "|".join(evidence),
                "creative_source_clause": row["concrete_workshop_reading"],
                "status": "ANONYMOUS_REGISTER_TRACE_NOT_CARD_MEANING",
            })
            if prior_statement is not None:
                edges.append({
                    "record_unit_id": record,
                    "from_statement_id": prior_statement,
                    "to_statement_id": row["statement_id"],
                    "entry_boundary_class": entry,
                    "owner_edge": "CARRY",
                    "active_item_edge": "CARRY_OR_RESUME" if entry in ("CONTINUE_SAME_CLAUSE", "RESUME_ACTIVE_ITEM", "NEXT_PARALLEL_CELL", "WITHIN_LOCUS_FIELD_BOUNDARY") else "REPLACE_AND_STORE_PREVIOUS",
                    "target_edge": "CARRY" if "CARRY_TARGET" in operations else ("INTRODUCE" if "INTRODUCE_TARGET_SLOT" in operations else "NONE_OR_RESET"),
                    "previous_edge": "SELECT" if "SELECT_PREVIOUS_ITEM" in operations else "AVAILABLE_NOT_SELECTED",
                    "strongest_rival": "NO_SEMANTIC_REGISTER_PURE_EXEMPLAR_ORDER",
                })
            prior_statement = row["statement_id"]

        inventory.extend([
            {"record_unit_id": record, "register": "PICTURE_OWNER", "anonymous_values": owner, "value_count": 1, "initialization": "RECORD_START_FROM_IMAGE_OR_LAYOUT", "semantic_status": "REFERENT_UNGROUNDED"},
            {"record_unit_id": record, "register": "ACTIVE_ITEM_OR_PREPARATION", "anonymous_values": "|".join(record_active_ids), "value_count": len(record_active_ids), "initialization": "SOURCE_STATEMENT_TRANSITION", "semantic_status": "REFERENT_UNGROUNDED"},
            {"record_unit_id": record, "register": "TARGET_OR_STATION", "anonymous_values": "|".join(record_target_ids) if record_target_ids else "NONE", "value_count": len(record_target_ids), "initialization": "EXACT_ZIEL_SLOT_ONLY", "semantic_status": "TARGET_ID_UNGROUNDED"},
            {"record_unit_id": record, "register": "PREVIOUS_ITEM", "anonymous_values": "DERIVED_FROM_ACTIVE_HISTORY", "value_count": max(0, len(record_active_ids) - 1), "initialization": "ON_ACTIVE_ITEM_REPLACEMENT", "semantic_status": "ANTECEDENT_UNGROUNDED"},
        ])

    outputs = {
        "trace": HERE / "V62_R4_116_STATEMENT_REGISTER_TRACE.tsv",
        "edges": HERE / "V62_R4_105_INTERSTATEMENT_CARRY_EDGES.tsv",
        "inventory": HERE / "V62_R4_11_RECORD_REGISTER_INVENTORY.tsv",
    }
    write(outputs["trace"], trace)
    write(outputs["edges"], edges)
    write(outputs["inventory"], inventory)
    checks = {
        "statements_116": len(trace) == 116,
        "edges_105": len(edges) == 105,
        "records_11": len(by_record) == 11,
        "four_registers_each": len(inventory) == 44,
        "owner_always_stable": all(row["pre_owner"] == row["post_owner"] for row in trace),
        "previous_only_selected_by_voriges": all(("SELECT_PREVIOUS_ITEM" in row["register_operations"]) == ("VORIGES?" in row["selected_short_card_skeleton"]) for row in trace),
        "target_introduced_only_by_ziel": all(("INTRODUCE_TARGET_SLOT" in row["register_operations"]) == ("ZIEL?" in row["selected_short_card_skeleton"]) for row in trace),
        "no_f84": all(not row["page"].startswith("f84") for row in trace),
    }
    validation = {
        "schema": "SIDEQUEST_V62_R4_ANONYMOUS_REGISTER_TRACE_V1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "counts": {
            "operations": dict(sorted(operation_counts.items())),
            "statements_with_target_requirement": sum("TARGET_REFERENT" in row["required_silent_slots"] for row in trace),
            "statements_with_previous_selection": sum("SELECT_PREVIOUS_ITEM" in row["register_operations"] for row in trace),
            "statements_without_selected_short_card": sum(not any(token in row["selected_short_card_skeleton"] for token in ("MASS?", "ANWENDEN?", "BEREIT?", "ANSATZ?", "ZIEL?", "KLAR?", "VORIGES?", "ANTEIL?", "TEMPERIEREN?", "SPÜLEN?", "ABLASSEN?")) for row in trace),
        },
        "inputs": {str(path.relative_to(ROOT)): sha(path) for path in (STATEMENTS_IN, BOUNDARIES_IN)},
        "outputs": {str(path.relative_to(ROOT)): sha(path) for path in outputs.values()},
    }
    (HERE / "V62_R4_VALIDATION.json").write_text(json.dumps(validation, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if validation["status"] != "PASS":
        raise SystemExit("V62 R4 validation failed")


if __name__ == "__main__":
    main()
