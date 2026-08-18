#!/usr/bin/env python3
"""Freeze fresh d/non-d cells after excluding every GDT318 surface."""
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

R = Path(__file__).resolve().parent
SOURCE = R / "gdt278_native_event_inventory.tsv"
G318 = R / "gdt318_frozen_panel.tsv"
METHOD = R / "GDT320_FRESH_D_DUAL_ENTRY_METHOD.md"
PANEL = R / "gdt320_frozen_panel.tsv"
CAPACITY = R / "gdt320_capacity.tsv"
DESIGN = R / "gdt320_design.json"


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
    source = [row for row in read(SOURCE) if row["control_id"] == "VOYNICH_REFERENCE"]
    assert not any(row["page"].startswith("f84") or row["locus"].startswith("f84") for row in source)
    by_id = {hashlib.sha256(row["observation_id"].encode()).hexdigest()[:20]: row for row in source}
    used = {by_id[row["event_id_sha256"]]["source_surface_sha256"] for row in read(G318)}
    positions = {(row["locus"], int(row["group_index"])): row for row in source}
    cells = defaultdict(list)
    for row in source:
        if row["source_surface_sha256"] in used:
            continue
        key = (row["page_host"], row["local_frame"], row["inner_d"], row["right_family"], row["dy_closure"], row["b3"])
        cells[key].append(row)
    eligible = {
        key: members for key, members in cells.items()
        if sum(row["wrapper"] == "d" for row in members) >= 2
        and sum(row["wrapper"] != "d" for row in members) >= 2
        and len({row["physical_folio"] for row in members if row["wrapper"] == "d"}) >= 2
        and len({row["physical_folio"] for row in members if row["wrapper"] != "d"}) >= 2
    }
    output = []
    truth = {}
    for key, members in eligible.items():
        cell_id = hashlib.sha256(("CELL|" + "|".join(key)).encode()).hexdigest()[:20]
        for row in members:
            event_id = hashlib.sha256(row["observation_id"].encode()).hexdigest()[:20]
            previous = positions.get((row["locus"], int(row["group_index"]) - 1))
            truth[event_id] = int(row["wrapper"] == "d")
            output.append({
                "event_id_sha256": event_id, "cell_id": cell_id,
                "physical_folio": row["physical_folio"], "page": row["page"],
                "locus": row["locus"], "section": row["section"], "register": row["register"],
                "line_first": int(row["group_index"] == "1"),
                "prev_dy": int(previous is not None and previous["dy_closure"] == "1"),
                "d_choice_withheld": "WITHHELD_UNTIL_SCORING",
            })
    output.sort(key=lambda row: (row["cell_id"], row["physical_folio"], row["locus"], row["event_id_sha256"]))
    write(PANEL, output)
    capacity = [{"cells": len(eligible), "events": len(output), "d_events": sum(truth.values()), "folios": len({row["physical_folio"] for row in output}), "excluded_surface_hashes": len(used), "powered_sections": "B|H|S"}]
    write(CAPACITY, capacity)
    design = {
        "schema": "GDT320_FRESH_D_DUAL_ENTRY_DESIGN_V1", "status": "FROZEN_BEFORE_FRESH_D_SCORING",
        "models": {"CELL": [], "CELL_LINE_START": ["line_first"], "CELL_PREV_DY": ["prev_dy"], "CELL_BOTH": ["line_first", "prev_dy"]},
        "ridge": 10.0, "fold": "LEAVE_ONE_PHYSICAL_FOLIO_OUT", "selector_cost_bits": 2.0,
        "null": {"worlds": 8192, "seed": 32020260818, "strata": "CELL_X_REGISTER", "scope": "FIXED_CROSSFIT_MAX_THREE_ALIGNMENT_DIAGNOSTIC"},
        "decision": {"joint_selector_paid_gain_positive": True, "both_matched_deltas_positive": True, "positive_coefficients_min_each": 23, "positive_powered_sections_min": 2, "max_three_p_le": 0.05},
        "forbidden": ["ALL_GDT318_SURFACES", "same_group_renderer_as_predictor", "host_glyphs", "host_substrings"],
        "claim_ceiling": "Fresh-surface d dual-entry tendency only; no prefix morpheme POS meaning sound language plaintext or translation.",
        "f84": {"authorized": False, "opened": False, "parsed": False, "retained": False, "joined": False, "scored": False},
        "inputs": {path.name: sha(path) for path in (SOURCE, G318, METHOD)},
        "outputs": {path.name: sha(path) for path in (PANEL, CAPACITY)},
        "implementation": {Path(__file__).name: sha(Path(__file__))},
    }
    design["content_sha256"] = canonical_hash(design)
    DESIGN.write_text(json.dumps(design, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": design["status"], "capacity": capacity[0]}, sort_keys=True))


if __name__ == "__main__":
    main()
