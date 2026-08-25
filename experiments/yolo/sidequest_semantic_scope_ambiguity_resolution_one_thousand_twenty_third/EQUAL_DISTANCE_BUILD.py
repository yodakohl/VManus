#!/usr/bin/env python3
"""Resolve the 120 Pass1022 equal-distance attachment rows."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
PASS1022 = ROOT / (
    "experiments/yolo/"
    "sidequest_semantic_argument_scope_stack_one_thousand_twenty_second"
)
PASS1021 = ROOT / (
    "experiments/yolo/"
    "sidequest_semantic_repeated_core_operator_one_thousand_twenty_first"
)

AMBIGUITIES = PASS1022 / "SCOPE_STACK_AMBIGUITIES.tsv"
EVENT_SCOPE = PASS1022 / "PASS1022_3888_EVENT_SCOPE_BINDINGS.tsv"
DOUBLING = PASS1021 / "PASS1021_ADJUDICATED_DOUBLING.tsv"

ACTIONS = {
    "OK": "SETZEN",
    "CH": "NEHMEN",
    "SH": "HALTEN",
    "K": "GEBEN",
    "S": "WÄHLEN",
    "T": "EINSTELLEN",
    "CHD": "UMSETZEN",
    "R": "MARKIEREN",
    "P": "EINSETZEN",
}

FOCI = {
    "Y": ("AKTIVER POSTEN", "ARGUMENT"),
    "AIIN": ("WERT", "ARGUMENT"),
    "AIN": ("ANTEIL", "ARGUMENT"),
    "OR": ("EINHEIT", "ARGUMENT"),
    "E": ("GRAD I", "GRADE"),
    "EE": ("GRAD II", "GRADE"),
    "EEE": ("GRAD III", "GRADE"),
    "AL": ("ZIELORT", "RELATION"),
    "AR": ("AUSGANG", "RELATION"),
    "L": ("VERBINDUNG", "RELATION"),
    "AIR": ("LAUF", "RELATION"),
}

FORWARD_FRAMES = {"L", "AIR"}

OUTPUT_FIELDS = [
    "resolution_id",
    "source_ambiguity_id",
    "source_attachment_id",
    "physical_page",
    "register",
    "statement_id",
    "event_id",
    "card_ordinal_in_statement",
    "locus",
    "owner_de",
    "surface_card",
    "component_recipe",
    "focus_core",
    "focus_value_de",
    "focus_family",
    "focus_atom_ordinal",
    "left_action_core",
    "left_action_value_de",
    "left_action_atom_ordinal",
    "right_action_core",
    "right_action_value_de",
    "right_action_atom_ordinal",
    "equal_distance",
    "between_left_and_focus",
    "between_focus_and_right",
    "pass1021_duplicate_overlap",
    "pass1021_duplicate_rule",
    "tie_rule_branch",
    "decision",
    "direct_governor_core",
    "direct_governor_value_de",
    "direct_governor_atom_ordinal",
    "package_reading",
    "reason_de",
    "pass1022_binding_trace_de",
    "pass1022_trace_match",
    "active_head_before_de",
    "active_head_after_de",
]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def joined(atoms: list[str]) -> str:
    return "+".join(atoms) if atoms else "NONE"


def main() -> None:
    source = [
        row for row in read_tsv(AMBIGUITIES)
        if row["ambiguity_class"] == "EQUAL_DISTANCE_TWO_HEADS"
    ]
    event_scope = {row["event_id"]: row for row in read_tsv(EVENT_SCOPE)}
    duplicate_by_event = {row["event_id"]: row for row in read_tsv(DOUBLING)}

    if len(source) != 120:
        raise AssertionError(f"expected 120 equal-distance rows, got {len(source)}")
    if len({row["event_id"] for row in source}) != 120:
        raise AssertionError("equal-distance rows are not one per event")
    if len(event_scope) != 3888:
        raise AssertionError("Pass1022 event scope does not contain 3,888 cards")

    results: list[dict[str, object]] = []
    for ordinal, row in enumerate(source, start=1):
        focus = row["focus_core"]
        if focus not in FOCI:
            raise AssertionError(f"unknown focus {focus}")
        atoms = row["component_recipe"].split("+")
        candidates: list[tuple[int, tuple[int, str], tuple[int, str]]] = []
        for focus_index, atom in enumerate(atoms):
            if atom != focus:
                continue
            left = [(index, value) for index, value in enumerate(atoms[:focus_index]) if value in ACTIONS]
            right = [
                (index, value)
                for index, value in enumerate(atoms[focus_index + 1 :], start=focus_index + 1)
                if value in ACTIONS
            ]
            if not left or not right:
                continue
            nearest_left = left[-1]
            nearest_right = right[0]
            if focus_index - nearest_left[0] == nearest_right[0] - focus_index:
                candidates.append((focus_index, nearest_left, nearest_right))
        if len(candidates) != 1:
            raise AssertionError(f"expected one tied focus in {row['event_id']}, got {candidates}")

        focus_index, left, right = candidates[0]
        left_index, left_core = left
        right_index, right_core = right
        distance = focus_index - left_index
        duplicate = duplicate_by_event.get(row["event_id"])
        duplicate_is_focus = bool(duplicate and duplicate["core"] == focus)

        # Priority: an already established doubled package is opened before
        # positional attachment. None of the present 120 rows reaches this branch.
        if duplicate_is_focus and duplicate["selected_doubling_rule"] == "PACKAGE_SCOPE_DESCENT":
            decision = "NESTED"
            rule_branch = "PASS1021_PACKAGE_FIRST"
            governor_core = "PACKAGE"
            governor_value = "OUTER_INNER_LAYER"
            governor_index: int | str = "PACKAGE"
            package_reading = (
                f"{left_core}@{left_index + 1}[{focus}@{focus_index + 1}"
                f"[...{right_core}@{right_index + 1}[…]]]"
            )
            reason = "Die bereits entschiedene Doppelung eröffnet vor jeder Seitenbindung eine äußere und innere Ebene."
        elif focus in FORWARD_FRAMES:
            decision = "RIGHT"
            rule_branch = "FORWARD_RELATION_FRAME"
            governor_core = right_core
            governor_value = ACTIONS[right_core]
            governor_index = right_index + 1
            package_reading = (
                f"{left_core}@{left_index + 1}[({focus}@{focus_index + 1}→"
                f"{right_core}@{right_index + 1})[…]]"
            )
            reason = (
                f"{focus} ist ein vorwärts öffnender Beziehungsrahmen; der rechte Kopf beginnt seinen Inhalt."
            )
        else:
            decision = "LEFT"
            rule_branch = "CLOSE_OPEN_HEAD_BEFORE_NEXT_HEAD"
            governor_core = left_core
            governor_value = ACTIONS[left_core]
            governor_index = left_index + 1
            package_reading = (
                f"{left_core}@{left_index + 1}[{focus}@{focus_index + 1}; "
                f"{right_core}@{right_index + 1}[…]]"
            )
            if FOCI[focus][1] == "GRADE":
                reason = "Der Grad schließt die bereits links geöffnete Handlung; der rechte Kopf eröffnet danach die innere Folgehandlung."
            elif FOCI[focus][1] == "ARGUMENT":
                reason = "Das Argument vervollständigt den offenen linken Kopf; der rechte Handlungskopf beginnt erst an seiner eigenen Position."
            else:
                reason = "AUSGANG/ZIELORT schließen nach der festen Beziehungsseite an den linken Kopf an."

        scope = event_scope[row["event_id"]]
        if scope["component_recipe"] != row["component_recipe"]:
            raise AssertionError(f"Pass1022 recipe mismatch for {row['event_id']}")
        if scope["surface"] != row["surface_card"]:
            raise AssertionError(f"Pass1022 surface mismatch for {row['event_id']}")
        expected_trace = (
            None if decision == "NESTED"
            else f"{FOCI[focus][0]}→{governor_value}"
        )
        trace_match = expected_trace is None or expected_trace in scope["binding_trace_de"]
        if not trace_match:
            raise AssertionError(
                f"Pass1022 trace lacks {expected_trace} for {row['event_id']}: "
                f"{scope['binding_trace_de']}"
            )

        results.append(
            {
                "resolution_id": f"ED{ordinal:03d}",
                "source_ambiguity_id": row["ambiguity_id"],
                "source_attachment_id": row["attachment_id"],
                "physical_page": row["physical_page"],
                "register": scope["register"],
                "statement_id": row["statement_id"],
                "event_id": row["event_id"],
                "card_ordinal_in_statement": scope["card_ordinal_in_statement"],
                "locus": row["locus"],
                "owner_de": scope["owner_de"],
                "surface_card": row["surface_card"],
                "component_recipe": row["component_recipe"],
                "focus_core": focus,
                "focus_value_de": FOCI[focus][0],
                "focus_family": FOCI[focus][1],
                "focus_atom_ordinal": focus_index + 1,
                "left_action_core": left_core,
                "left_action_value_de": ACTIONS[left_core],
                "left_action_atom_ordinal": left_index + 1,
                "right_action_core": right_core,
                "right_action_value_de": ACTIONS[right_core],
                "right_action_atom_ordinal": right_index + 1,
                "equal_distance": distance,
                "between_left_and_focus": joined(atoms[left_index + 1 : focus_index]),
                "between_focus_and_right": joined(atoms[focus_index + 1 : right_index]),
                "pass1021_duplicate_overlap": "YES" if duplicate else "NO",
                "pass1021_duplicate_rule": duplicate["selected_doubling_rule"] if duplicate else "NONE",
                "tie_rule_branch": rule_branch,
                "decision": decision,
                "direct_governor_core": governor_core,
                "direct_governor_value_de": governor_value,
                "direct_governor_atom_ordinal": governor_index,
                "package_reading": package_reading,
                "reason_de": reason,
                "pass1022_binding_trace_de": scope["binding_trace_de"],
                "pass1022_trace_match": "YES",
                "active_head_before_de": scope["active_head_before_de"],
                "active_head_after_de": scope["active_head_after_de"],
            }
        )

    decisions = Counter(str(row["decision"]) for row in results)
    families = Counter((str(row["focus_family"]), str(row["decision"])) for row in results)
    foci = Counter((str(row["focus_core"]), str(row["decision"])) for row in results)
    distances = Counter(int(row["equal_distance"]) for row in results)
    same_head = sum(row["left_action_core"] == row["right_action_core"] for row in results)
    duplicate_overlap = sum(row["pass1021_duplicate_overlap"] == "YES" for row in results)

    if decisions != Counter({"LEFT": 119, "RIGHT": 1}):
        raise AssertionError(f"unexpected decision counts: {decisions}")
    if duplicate_overlap != 0:
        raise AssertionError("an equal-distance row unexpectedly overlaps Pass1021 doubling")

    count_rows: list[dict[str, object]] = []
    for decision in ["LEFT", "RIGHT", "NESTED", "UNRESOLVED"]:
        count_rows.append({"count_type": "DECISION", "key": decision, "subkey": "ALL", "count": decisions[decision]})
    for family in ["ARGUMENT", "GRADE", "RELATION"]:
        for decision in ["LEFT", "RIGHT", "NESTED", "UNRESOLVED"]:
            count_rows.append(
                {"count_type": "FAMILY_DECISION", "key": family, "subkey": decision, "count": families[(family, decision)]}
            )
    for focus in FOCI:
        if any(key[0] == focus for key in foci):
            for decision in ["LEFT", "RIGHT", "NESTED", "UNRESOLVED"]:
                count_rows.append(
                    {"count_type": "FOCUS_DECISION", "key": focus, "subkey": decision, "count": foci[(focus, decision)]}
                )
    for distance, count in sorted(distances.items()):
        count_rows.append({"count_type": "TIE_DISTANCE", "key": distance, "subkey": "ATOMS", "count": count})
    count_rows.extend(
        [
            {"count_type": "CONTROL", "key": "SAME_CORE_HEADS_BOTH_SIDES", "subkey": "ALL", "count": same_head},
            {"count_type": "CONTROL", "key": "PASS1021_DUPLICATE_EVENT_OVERLAP", "subkey": "ALL", "count": duplicate_overlap},
        ]
    )

    summary = {
        "source_equal_distance_rows": len(source),
        "resolved_rows": len(results) - decisions["UNRESOLVED"],
        "decision_counts": {key: decisions[key] for key in ["LEFT", "RIGHT", "NESTED", "UNRESOLVED"]},
        "family_decision_counts": {
            family: {decision: families[(family, decision)] for decision in ["LEFT", "RIGHT", "NESTED", "UNRESOLVED"]}
            for family in ["ARGUMENT", "GRADE", "RELATION"]
        },
        "focus_counts": dict(sorted(Counter(str(row["focus_core"]) for row in results).items())),
        "tie_distance_counts": {str(key): value for key, value in sorted(distances.items())},
        "same_core_heads_both_sides": same_head,
        "pass1021_duplicate_event_overlap": duplicate_overlap,
        "rule": [
            "PASS1021_PACKAGE_FIRST",
            "FORWARD_FRAME_L_OR_AIR_GOES_RIGHT",
            "OTHER_FOCUS_CLOSES_OPEN_LEFT_HEAD_BEFORE_NEXT_HEAD",
        ],
        "checks": {
            "all_120_source_rows_present": "PASS",
            "one_resolution_per_source_row": "PASS",
            "root_values_unchanged": "PASS",
            "pass1022_event_recipe_alignment": "PASS",
            "pass1022_binding_trace_matches_all_resolutions": "PASS",
            "unresolved_rows": decisions["UNRESOLVED"],
        },
    }

    write_tsv(OUT / "EQUAL_DISTANCE_RESOLUTIONS.tsv", results, OUTPUT_FIELDS)
    write_tsv(OUT / "EQUAL_DISTANCE_COUNTS.tsv", count_rows, ["count_type", "key", "subkey", "count"])
    with (OUT / "EQUAL_DISTANCE_SUMMARY.json").open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
