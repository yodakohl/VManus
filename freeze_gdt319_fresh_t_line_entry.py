#!/usr/bin/env python3
"""Freeze fresh t/non-t cells after excluding every GDT318 surface."""
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

R = Path(__file__).resolve().parent
SOURCE = R / "gdt278_native_event_inventory.tsv"
G318 = R / "gdt318_frozen_panel.tsv"
METHOD = R / "GDT319_FRESH_T_LINE_ENTRY_METHOD.md"
PANEL = R / "gdt319_frozen_panel.tsv"
CAPACITY = R / "gdt319_capacity.tsv"
DESIGN = R / "gdt319_design.json"


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
    used_surfaces = {by_id[row["event_id_sha256"]]["source_surface_sha256"] for row in read(G318)}
    cells = defaultdict(list)
    for row in source:
        if row["source_surface_sha256"] in used_surfaces:
            continue
        key = (row["page_host"], row["local_frame"], row["inner_d"], row["right_family"], row["dy_closure"], row["b3"])
        cells[key].append(row)
    eligible = {
        key: members for key, members in cells.items()
        if sum(row["wrapper"] == "t" for row in members) >= 2
        and sum(row["wrapper"] != "t" for row in members) >= 2
        and len({row["physical_folio"] for row in members if row["wrapper"] == "t"}) >= 2
        and len({row["physical_folio"] for row in members if row["wrapper"] != "t"}) >= 2
    }
    output = []
    for key, members in eligible.items():
        cell_id = hashlib.sha256(("CELL|" + "|".join(key)).encode()).hexdigest()[:20]
        for row in members:
            output.append({
                "event_id_sha256": hashlib.sha256(row["observation_id"].encode()).hexdigest()[:20],
                "cell_id": cell_id,
                "physical_folio": row["physical_folio"], "page": row["page"],
                "locus": row["locus"], "section": row["section"],
                "register": row["register"],
                "line_first": int(row["group_index"] == "1"),
                "t_choice_withheld": "WITHHELD_UNTIL_SCORING",
            })
    output.sort(key=lambda row: (row["cell_id"], row["physical_folio"], row["locus"], row["event_id_sha256"]))
    write(PANEL, output)
    truth = {hashlib.sha256(row["observation_id"].encode()).hexdigest()[:20]: int(row["wrapper"] == "t") for row in source}
    capacity = [{"cells": len(eligible), "events": len(output), "t_events": sum(truth[row["event_id_sha256"]] for row in output), "folios": len({row["physical_folio"] for row in output}), "excluded_surface_hashes": len(used_surfaces), "powered_sections": "B|H|S"}]
    write(CAPACITY, capacity)
    design = {
        "schema": "GDT319_FRESH_T_LINE_ENTRY_DESIGN_V1", "status": "FROZEN_BEFORE_FRESH_T_SCORING",
        "models": {"CELL": [], "CELL_LINE_START": ["line_first"]},
        "ridge": 10.0, "fold": "LEAVE_ONE_PHYSICAL_FOLIO_OUT",
        "null": {"worlds": 8192, "seed": 31920260818, "strata": "CELL_X_REGISTER", "scope": "FIXED_CROSSFIT_ALIGNMENT_DIAGNOSTIC"},
        "decision": {"gain_positive": True, "matched_delta_positive": True, "positive_coefficients_min": 24, "positive_powered_sections_min": 2, "alignment_p_le": 0.05},
        "forbidden": ["ALL_GDT318_SURFACES", "same_group_renderer_as_predictor", "host_glyphs", "host_substrings"],
        "claim_ceiling": "Fresh-surface t line-entry tendency only; no prefix morpheme POS meaning sound language plaintext or translation.",
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
