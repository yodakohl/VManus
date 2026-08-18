#!/usr/bin/env python3
"""Freeze the broad outcome-diverse GDT318 wrapper panel before scoring."""
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

R = Path(__file__).resolve().parent
SOURCE = R / "gdt278_native_event_inventory.tsv"
METHOD = R / "GDT318_GLOBAL_WRAPPER_ENTRY_STATE_METHOD.md"
PANEL = R / "gdt318_frozen_panel.tsv"
CAPACITY = R / "gdt318_capacity.tsv"
DESIGN = R / "gdt318_design.json"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()


def read(path):
    with Path(path).open(encoding="utf8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path, rows):
    with Path(path).open("w", encoding="utf8", newline="") as handle:
        writer = csv.DictWriter(handle, rows[0].keys(), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main():
    rows = [row for row in read(SOURCE) if row["control_id"] == "VOYNICH_REFERENCE"]
    assert not any(row["page"].startswith("f84") or row["locus"].startswith("f84") for row in rows)
    positions = {(row["locus"], int(row["group_index"])): row for row in rows}
    cells = defaultdict(list)
    for row in rows:
        key = (row["page_host"], row["local_frame"], row["inner_d"], row["right_family"], row["dy_closure"], row["b3"])
        cells[key].append(row)
    eligible = {
        key: members for key, members in cells.items()
        if len(members) >= 10
        and len({row["physical_folio"] for row in members}) >= 3
        and len({row["wrapper"] for row in members}) >= 2
    }
    output = []
    wrapper_counts = Counter()
    for key, members in eligible.items():
        cell_id = hashlib.sha256(("CELL|" + "|".join(key)).encode()).hexdigest()[:20]
        for row in members:
            previous = positions.get((row["locus"], int(row["group_index"]) - 1))
            wrapper_counts[row["wrapper"]] += 1
            output.append({
                "event_id_sha256": hashlib.sha256(row["observation_id"].encode()).hexdigest()[:20],
                "cell_id": cell_id,
                "physical_folio": row["physical_folio"], "page": row["page"],
                "locus": row["locus"], "section": row["section"],
                "register": row["register"],
                "line_first": int(row["group_index"] == "1"),
                "prev_dy": int(previous is not None and previous["dy_closure"] == "1"),
                "wrapper_choice_withheld": "WITHHELD_UNTIL_SCORING",
            })
    output.sort(key=lambda row: (row["cell_id"], row["physical_folio"], row["locus"], row["event_id_sha256"]))
    write(PANEL, output)
    capacity = [{
        "cells": len(eligible), "events": len(output),
        "folios": len({row["physical_folio"] for row in output}),
        "wrapper_counts_json": json.dumps(dict(sorted(wrapper_counts.items())), sort_keys=True, separators=(",", ":")),
        "sections": "|".join(sorted({row["section"] for row in output})),
    }]
    write(CAPACITY, capacity)
    design = {
        "schema": "GDT318_GLOBAL_WRAPPER_ENTRY_STATE_DESIGN_V1",
        "status": "FROZEN_BEFORE_GLOBAL_WRAPPER_SCORING",
        "classes": ["NONE", "ch", "che", "d", "q", "s", "sh", "t"],
        "eligibility": {"min_events": 10, "min_folios": 3, "min_wrapper_classes": 2},
        "models": {
            "CELL": [], "CELL_LINE_START": ["line_first"],
            "CELL_PREV_DY": ["prev_dy"], "CELL_BOTH": ["line_first", "prev_dy"],
        },
        "alpha": 0.5, "ridge": 10.0,
        "fold": "LEAVE_ONE_PHYSICAL_FOLIO_OUT",
        "selector_cost_bits": 2.0,
        "null": {"worlds": 8192, "seed": 31820260818, "strata": "CELL_X_REGISTER", "scope": "FIXED_CROSSFIT_MAX_THREE_ALIGNMENT_DIAGNOSTIC"},
        "decision": {"selector_paid_gain_positive": True, "positive_powered_sections_min": 2, "s_line_positive_coefficients_min": 75, "q_prev_dy_positive_coefficients_min": 75, "max_three_p_le": 0.05},
        "claim_ceiling": "Shared opaque-cell wrapper entry-state compression only; no unseen license prefix morpheme POS meaning sound language plaintext or translation.",
        "f84": {"authorized": False, "opened": False, "parsed": False, "retained": False, "joined": False, "scored": False},
        "inputs": {path.name: sha(path) for path in (SOURCE, METHOD)},
        "outputs": {path.name: sha(path) for path in (PANEL, CAPACITY)},
        "implementation": {Path(__file__).name: sha(Path(__file__))},
    }
    design["content_sha256"] = canonical_hash(design)
    DESIGN.write_text(json.dumps(design, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": design["status"], "capacity": capacity[0]}, sort_keys=True))


if __name__ == "__main__":
    main()
