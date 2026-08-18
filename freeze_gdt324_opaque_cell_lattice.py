#!/usr/bin/env python3
"""Freeze the score-blind GDT324 cell-lattice capacity and target panel."""
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

R = Path(__file__).resolve().parent
SOURCE = R / "gdt278_native_event_inventory.tsv"
METHOD = R / "GDT324_OPAQUE_CELL_LATTICE_COMPRESSION_METHOD.md"
G310 = R / "gdt310_result.json"
G323 = R / "gdt323_result.json"
PANEL = R / "gdt324_frozen_cells.tsv"
CAPACITY = R / "gdt324_capacity.tsv"
DESIGN = R / "gdt324_design.json"
KEYS = ("page_host", "local_frame", "inner_d", "right_family", "dy_closure", "b3")


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
    cells = defaultdict(list)
    for row in rows:
        cells[tuple(row[key] for key in KEYS)].append(row)
    eligible = {key: value for key, value in cells.items() if len(value) >= 10 and len({row["physical_folio"] for row in value}) >= 3}
    by_host = defaultdict(list)
    for key in eligible:
        by_host[key[0]].append(key)
    targets = {key: value for key, value in eligible.items() if len(by_host[key[0]]) >= 2}
    panel = []
    for key, members in targets.items():
        coordinate = key[1:]
        panel.append({
            "cell_id": hashlib.sha256(("CELL|" + "|".join(key)).encode()).hexdigest()[:20],
            "host_id": hashlib.sha256(("HOST|" + key[0]).encode()).hexdigest()[:20],
            "coordinate_id": hashlib.sha256(("COORD|" + "|".join(coordinate)).encode()).hexdigest()[:20],
            "event_count": len(members),
            "folio_count": len({row["physical_folio"] for row in members}),
            "sibling_cells": len(by_host[key[0]]) - 1,
            "wrapper_outcome": "WITHHELD_UNTIL_SCORING",
        })
    panel.sort(key=lambda row: row["cell_id"])
    write(PANEL, panel)
    capacity = [{"training_cells": len(eligible), "target_cells": len(panel), "target_events": sum(int(row["event_count"]) for row in panel), "target_hosts": len({row["host_id"] for row in panel}), "minimum_events": 10, "minimum_folios": 3, "minimum_sibling_cells": 1}]
    write(CAPACITY, capacity)
    design = {
        "schema": "GDT324_OPAQUE_CELL_LATTICE_DESIGN_V1",
        "status": "FROZEN_BEFORE_CELL_LATTICE_SCORING",
        "cell_fields": list(KEYS),
        "coordinate_fields": list(KEYS[1:]),
        "classes": ["NONE", "ch", "che", "d", "q", "s", "sh", "t"],
        "eligibility": {"minimum_events": 10, "minimum_physical_folios": 3, "minimum_other_retained_host_cells": 1, "wrapper_outcome_used": False},
        "models": ["GLOBAL", "COORDINATE", "HOST_SIBLING", "HOST_COORD_ADDITIVE"],
        "alpha": 0.5,
        "fold": "LEAVE_ONE_COMPLETE_CELL_OUT",
        "primary_weighting": "EQUAL_TARGET_CELLS",
        "sensitivity_weighting": "HELD_EVENTS",
        "selector_bits": 2.0,
        "null": {"worlds": 8192, "seed": 32420260818, "strata": "EVENT_COUNT_BIN_X_FOLIO_COUNT_BIN", "event_count_bins": ["10_19", "20_49", "50_PLUS"], "folio_count_bins": ["3_4", "5_9", "10_PLUS"], "unit": "COMPLETE_CELL_WRAPPER_COUNT_VECTOR", "scope": "FIXED_PREDICTION_MAX_THREE_DIAGNOSTIC"},
        "decision": {"additive_selector_paid_gain_positive": True, "additive_beats_both_single_axes": True, "max_three_p_le": 0.05},
        "claim_ceiling": "Known recurrent-host opaque compatibility-cell compression only; no new host license morpheme lexical category meaning sound language plaintext or translation.",
        "f84": {"authorized": False, "opened": False, "parsed": False, "retained": False, "joined": False, "scored": False},
        "inputs": {path.name: sha(path) for path in (SOURCE, METHOD, G310, G323)},
        "outputs": {path.name: sha(path) for path in (PANEL, CAPACITY)},
        "implementation": {Path(__file__).name: sha(Path(__file__))},
    }
    design["content_sha256"] = canonical_hash(design)
    DESIGN.write_text(json.dumps(design, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": design["status"], "capacity": capacity[0]}, sort_keys=True))


if __name__ == "__main__":
    main()
