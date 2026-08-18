#!/usr/bin/env python3
"""Freeze GDT311 event panel, deterministic split, and external features."""
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

R = Path(__file__).resolve().parent
SOURCE = R / "gdt278_native_event_inventory.tsv"
PAIRS = R / "gdt303_pair_deltas.tsv"
METHOD = R / "GDT311_OPERATION_EVENT_CHOICE_METHOD.md"
PANEL = R / "gdt311_frozen_event_panel.tsv"
CAPACITY = R / "gdt311_capacity.tsv"
DESIGN = R / "gdt311_design.json"
OPERATIONS = ("wrapper:ch>s", "wrapper:d>s", "wrapper:NONE>q")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical_hash(value):
    raw = json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()


def read(path):
    with Path(path).open(encoding="utf8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path, rows):
    with Path(path).open("w", encoding="utf8", newline="") as handle:
        writer = csv.DictWriter(handle, rows[0].keys(), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def pair_id(operation, source_hash, target_hash):
    text = f"{operation}|{source_hash}|{target_hash}"
    return hashlib.sha256(text.encode()).hexdigest()[:20]


def is_test_folio(folio):
    value = hashlib.sha256(f"GDT311_SPLIT_V1|{folio}".encode()).hexdigest()
    return int(value[:8], 16) % 3 == 0


def main():
    events = [row for row in read(SOURCE) if row["control_id"] == "VOYNICH_REFERENCE"]
    assert not any(row["page"].startswith("f84") or row["locus"].startswith("f84") for row in events)
    by_position = {(row["locus"], int(row["group_index"])): row for row in events}
    selected_pairs = [row for row in read(PAIRS) if row["operation"] in OPERATIONS]
    surface_map = {}
    pair_meta = {}
    for row in selected_pairs:
        identifier = pair_id(row["operation"], row["source_surface_sha256"], row["target_surface_sha256"])
        pair_meta[identifier] = row
        for role, surface in ((0, row["source_surface_sha256"]), (1, row["target_surface_sha256"])):
            key = (row["operation"], surface)
            assert key not in surface_map
            surface_map[key] = (identifier, role)

    panel = []
    outcomes = {}
    for event in events:
        for operation in OPERATIONS:
            key = (operation, event["source_surface_sha256"])
            if key not in surface_map:
                continue
            identifier, role = surface_map[key]
            previous = by_position.get((event["locus"], int(event["group_index"]) - 1))
            split = "TEST" if is_test_folio(event["physical_folio"]) else "TRAIN"
            anonymous_event = hashlib.sha256(f"{operation}|{event['observation_id']}".encode()).hexdigest()[:20]
            outcomes[anonymous_event] = role
            panel.append(
                {
                    "anonymous_event_id": anonymous_event,
                    "operation": operation,
                    "pair_id": identifier,
                    "split": split,
                    "physical_folio": event["physical_folio"],
                    "page": event["page"],
                    "locus": event["locus"],
                    "group_index": event["group_index"],
                    "group_count": event["group_count"],
                    "line_first": int(event["group_index"] == "1"),
                    "line_last": int(event["group_index"] == event["group_count"]),
                    "relative_position": f"{(int(event['group_index']) - 1) / (int(event['group_count']) - 1):.12f}",
                    "field_first": int(event["within_field_position"] == "FIRST"),
                    "field_last": int(event["within_field_position"] == "LAST"),
                    "record1": int(event["record_ordinal"] == "1"),
                    "prev_dy": int(previous is not None and previous["dy_closure"] == "1"),
                    "section": event["section"],
                    "currier": event["currier"],
                    "hand": event["hand"],
                    "register": event["register"],
                    "outcome_withheld": "WITHHELD_UNTIL_SCORING",
                }
            )
    panel.sort(key=lambda row: (row["operation"], row["pair_id"], row["physical_folio"], row["locus"], int(row["group_index"])))

    train_roles = defaultdict(set)
    for row in panel:
        if row["split"] == "TRAIN":
            train_roles[(row["operation"], row["pair_id"])].add(outcomes[row["anonymous_event_id"]])
    eligible = {key for key, roles in train_roles.items() if roles == {0, 1}}
    assert len(eligible) == len(selected_pairs)

    capacity = []
    for operation in OPERATIONS:
        rows = [row for row in panel if row["operation"] == operation]
        test = [row for row in rows if row["split"] == "TEST"]
        training = [row for row in rows if row["split"] == "TRAIN"]
        capacity.append(
            {
                "operation": operation,
                "exact_pairs": len({row["pair_id"] for row in rows}),
                "training_events": len(training),
                "test_events": len(test),
                "training_folios": len({row["physical_folio"] for row in training}),
                "test_folios": len({row["physical_folio"] for row in test}),
                "test_target_events": sum(outcomes[row["anonymous_event_id"]] for row in test),
            }
        )
    write(PANEL, panel)
    write(CAPACITY, capacity)
    design = {
        "schema": "GDT311_OPERATION_EVENT_CHOICE_DESIGN_V1",
        "status": "FROZEN_BEFORE_HELD_EVENT_CHOICE_SCORING",
        "operations": list(OPERATIONS),
        "split": "SHA256_GDT311_SPLIT_V1_MOD3_EQ0_TEST",
        "ridge": 10.0,
        "probability_clip": [0.01, 0.99],
        "models": {
            "PAIR": [],
            "PAIR_POSITION": ["line_first", "line_last", "relative_position", "field_first", "field_last", "record1"],
            "PAIR_BOUNDARY": ["prev_dy", "line_first"],
            "PAIR_REGISTER": ["section", "currier", "hand", "register"],
            "PAIR_FULL": ["line_first", "line_last", "relative_position", "field_first", "field_last", "record1", "prev_dy", "section", "currier", "hand", "register"],
        },
        "categorical_features": ["section", "currier", "hand", "register"],
        "forbidden_predictors": ["same_group_wrapper", "same_group_frame", "same_group_inner_d", "same_group_right_family", "same_group_dy", "same_group_b3", "page_host_identity", "host_glyphs", "host_substrings", "target_surface_identity"],
        "null": {"worlds": 8192, "seed": 31120260818, "primary_strata": "PAIR_X_REGISTER", "sensitivity_strata": "PAIR"},
        "decision": {"held_full_bits_per_event_gain_positive": True, "null_centered_gain_positive": True, "auc_minimum": 0.60, "max12_p_le": 0.05},
        "claim_ceiling": "Stochastic formal operation choice on already licensed exact pairs only; no unseen license morphology category semantics sound language plaintext meaning or translation.",
        "f84": {"authorized": False, "opened": False, "parsed": False, "retained": False, "joined": False, "scored": False},
        "inputs": {path.name: sha(path) for path in (SOURCE, PAIRS, METHOD)},
        "outputs": {path.name: sha(path) for path in (PANEL, CAPACITY)},
        "implementation": {Path(__file__).name: sha(Path(__file__))},
    }
    design["content_sha256"] = canonical_hash(design)
    DESIGN.write_text(json.dumps(design, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": design["status"], "pairs": len(selected_pairs), "events": len(panel), "capacity": capacity}, sort_keys=True))


if __name__ == "__main__":
    main()
