#!/usr/bin/env python3
"""Freeze the score-blind sparse-cell coordinate-backoff panel."""
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

R = Path(__file__).resolve().parent
SOURCE = R / "gdt278_native_event_inventory.tsv"
METHOD = R / "GDT325_SPARSE_CELL_COORDINATE_BACKOFF_METHOD.md"
G322 = R / "gdt322_renderer_model.json"
G324 = R / "gdt324_result.json"
PANEL = R / "gdt325_frozen_panel.tsv"
CAPACITY = R / "gdt325_capacity.tsv"
DESIGN = R / "gdt325_design.json"
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
    positions = {}
    for row in rows:
        cells[tuple(row[key] for key in KEYS)].append(row)
        positions[(row["locus"], int(row["group_index"]))] = row
    powered = {key: value for key, value in cells.items() if len(value) >= 10 and len({row["physical_folio"] for row in value}) >= 3}
    powered_coordinates = {key[1:] for key in powered}
    targets = {key: value for key, value in cells.items() if key not in powered and 5 <= len(value) <= 9 and len({row["physical_folio"] for row in value}) >= 2 and key[1:] in powered_coordinates}
    panel = []
    for key, members in targets.items():
        cell_id = hashlib.sha256(("CELL|" + "|".join(key)).encode()).hexdigest()[:20]
        coordinate_id = hashlib.sha256(("COORD|" + "|".join(key[1:])).encode()).hexdigest()[:20]
        for row in members:
            previous = positions.get((row["locus"], int(row["group_index"]) - 1))
            panel.append({"event_id_sha256": hashlib.sha256(row["observation_id"].encode()).hexdigest()[:20], "cell_id": cell_id, "coordinate_id": coordinate_id, "physical_folio": row["physical_folio"], "page": row["page"], "locus": row["locus"], "section": row["section"], "register": row["register"], "cell_event_count": len(members), "line_first": int(row["group_index"] == "1"), "prev_dy": int(previous is not None and previous["dy_closure"] == "1"), "wrapper_outcome": "WITHHELD_UNTIL_SCORING"})
    panel.sort(key=lambda row: (row["cell_id"], row["physical_folio"], row["locus"], row["event_id_sha256"]))
    write(PANEL, panel)
    capacity = [{"training_cells": len(powered), "target_cells": len(targets), "target_events": len(panel), "target_folios": len({row["physical_folio"] for row in panel}), "target_hosts": len({key[0] for key in targets}), "target_coordinates": len({key[1:] for key in targets}), "register_counts_json": json.dumps(dict(sorted(Counter(row["register"] for row in panel).items())), sort_keys=True, separators=(",", ":"))}]
    write(CAPACITY, capacity)
    renderer = json.loads(G322.read_text())
    design = {"schema": "GDT325_SPARSE_CELL_COORDINATE_BACKOFF_DESIGN_V1", "status": "FROZEN_BEFORE_SPARSE_CELL_SCORING", "cell_fields": list(KEYS), "coordinate_fields": list(KEYS[1:]), "classes": renderer["classes"], "training_eligibility": {"minimum_events": 10, "minimum_folios": 3}, "target_eligibility": {"minimum_events": 5, "maximum_events": 9, "minimum_folios": 2, "powered_coordinate_required": True, "wrapper_outcome_used": False}, "models": ["GLOBAL", "GLOBAL_TWO_RULE", "COORDINATE", "COORDINATE_TWO_RULE"], "alpha": 0.5, "fixed_coefficients": {"s_X_line_first": renderer["beta_s_line_first"], "q_X_prev_dy": renderer["beta_q_prev_dy"]}, "primary_weighting": "EQUAL_TARGET_CELLS", "sensitivity_weighting": "HELD_EVENTS", "selector_bits": 2.0, "null": {"worlds": 8192, "seed": 32520260818, "strata": "REGISTER_X_LINE_START_X_PREV_DY_X_CELL_EVENT_COUNT_BIN", "event_count_bins": ["5_6", "7_9"], "scope": "FIXED_PREDICTION_MAX_FOUR_DIAGNOSTIC"}, "decision": {"selector_paid_gain_positive": True, "coordinate_beats_global": True, "positive_powered_sections_min": 2, "max_four_p_le": 0.05}, "claim_ceiling": "Sparse-cell renderer-coordinate wrapper backoff only; no host identity morpheme lexical class meaning sound language plaintext or translation.", "f84": {"authorized": False, "opened": False, "parsed": False, "retained": False, "joined": False, "scored": False}, "inputs": {path.name: sha(path) for path in (SOURCE, METHOD, G322, G324)}, "outputs": {path.name: sha(path) for path in (PANEL, CAPACITY)}, "implementation": {Path(__file__).name: sha(Path(__file__))}}
    design["content_sha256"] = canonical_hash(design)
    DESIGN.write_text(json.dumps(design, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": design["status"], "capacity": capacity[0]}, sort_keys=True))


if __name__ == "__main__":
    main()
