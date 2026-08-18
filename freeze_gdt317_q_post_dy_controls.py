#!/usr/bin/env python3
"""Freeze powered controls for the unchanged GDT316 q post-DY instrument."""
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

R = Path(__file__).resolve().parent
SOURCE = R / "gdt278_native_event_inventory.tsv"
VMS = R / "gdt316_frozen_panel.tsv"
METHOD = R / "GDT317_Q_POST_DY_CONTROL_CALIBRATION_METHOD.md"
PANEL = R / "gdt317_frozen_panel.tsv"
CAPACITY = R / "gdt317_capacity.tsv"
DESIGN = R / "gdt317_design.json"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical_hash(value):
    data = json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()
    return hashlib.sha256(data).hexdigest()


def read(path):
    with Path(path).open(encoding="utf8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path, rows):
    with Path(path).open("w", encoding="utf8", newline="") as handle:
        writer = csv.DictWriter(handle, rows[0].keys(), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main():
    events = read(SOURCE)
    assert not any(row["page"].startswith("f84") or row["locus"].startswith("f84") for row in events)
    by_panel = defaultdict(list)
    for row in events:
        if row["control_id"] != "VOYNICH_REFERENCE":
            by_panel[row["control_id"]].append(row)

    output = []
    capacity = []
    for panel, rows in sorted(by_panel.items()):
        positions = {(row["locus"], int(row["group_index"])): row for row in rows}
        cells = defaultdict(list)
        for row in rows:
            key = (
                row["page_host"], row["local_frame"], row["inner_d"],
                row["right_family"], row["dy_closure"], row["b3"],
            )
            cells[key].append(row)
        eligible = {
            key: members
            for key, members in cells.items()
            if sum(row["wrapper"] == "q" for row in members) >= 2
            and sum(row["wrapper"] != "q" for row in members) >= 2
            and len({row["physical_folio"] for row in members if row["wrapper"] == "q"}) >= 2
            and len({row["physical_folio"] for row in members if row["wrapper"] != "q"}) >= 2
        }
        event_count = sum(map(len, eligible.values()))
        q_count = sum(row["wrapper"] == "q" for members in eligible.values() for row in members)
        folio_count = len({row["physical_folio"] for members in eligible.values() for row in members})
        powered = len(eligible) >= 5 and event_count >= 100 and folio_count >= 5 and q_count >= 20
        capacity.append({
            "panel": panel, "cells": len(eligible), "events": event_count,
            "q_events": q_count, "folios": folio_count, "powered": int(powered),
        })
        if powered:
            for key, members in eligible.items():
                cell_id = hashlib.sha256((panel + "|CELL|" + "|".join(key)).encode()).hexdigest()[:20]
                for row in members:
                    previous = positions.get((row["locus"], int(row["group_index"]) - 1))
                    output.append({
                        "panel": panel,
                        "event_id_sha256": hashlib.sha256(row["observation_id"].encode()).hexdigest()[:20],
                        "cell_id": cell_id,
                        "physical_folio": row["physical_folio"],
                        "page": row["page"],
                        "locus": row["locus"],
                        "section": row["section"],
                        "register": row["register"],
                        "prev_dy": int(previous is not None and previous["dy_closure"] == "1"),
                        "q_choice_withheld": "WITHHELD_UNTIL_SCORING",
                    })

    for row in read(VMS):
        output.append({
            "panel": "VOYNICH_REFERENCE", "event_id_sha256": row["event_id_sha256"],
            "cell_id": row["cell_id"], "physical_folio": row["physical_folio"],
            "page": row["page"], "locus": row["locus"], "section": row["section"],
            "register": row["register"], "prev_dy": row["prev_dy"],
            "q_choice_withheld": "WITHHELD_UNTIL_SCORING",
        })
    capacity.append({
        "panel": "VOYNICH_REFERENCE", "cells": 36, "events": 450,
        "q_events": 137, "folios": 82, "powered": 1,
    })
    output.sort(key=lambda row: (row["panel"], row["cell_id"], row["physical_folio"], row["locus"], row["event_id_sha256"]))
    write(PANEL, output)
    write(CAPACITY, sorted(capacity, key=lambda row: row["panel"]))
    powered_panels = sorted(row["panel"] for row in capacity if int(row["powered"]))
    design = {
        "schema": "GDT317_Q_POST_DY_CONTROL_DESIGN_V1",
        "status": "FROZEN_BEFORE_CONTROL_SCORING",
        "powered_panels": powered_panels,
        "eligibility": {
            "min_cells": 5, "min_events": 100, "min_folios": 5, "min_q_events": 20,
            "cell_min_q": 2, "cell_min_non_q": 2,
            "cell_min_q_folios": 2, "cell_min_non_q_folios": 2,
        },
        "instrument": {
            "ridge": 10.0, "fold": "LEAVE_ONE_PHYSICAL_FOLIO_OUT",
            "models": ["CELL", "CELL_PREV_DY"], "null_worlds": 8192,
            "null_seed": 31720260818, "null_strata": "CELL_X_REGISTER",
            "null_scope": "FIXED_CROSSFIT_ALIGNMENT_DIAGNOSTIC",
        },
        "classification": {
            "enriched": "VOYNICH_RANK1_GAIN_AND_DELTA",
            "non_specific": "AT_LEAST_TWO_CONTROLS_GAIN_GE_VOYNICH",
            "otherwise": "MIXED",
        },
        "claim_ceiling": "Formal q post-DY calibration only; no shared prefix linguistic function meaning sound language plaintext or translation.",
        "f84": {"authorized": False, "opened": False, "parsed": False, "retained": False, "joined": False, "scored": False},
        "inputs": {path.name: sha(path) for path in (SOURCE, VMS, METHOD)},
        "outputs": {path.name: sha(path) for path in (PANEL, CAPACITY)},
        "implementation": {Path(__file__).name: sha(Path(__file__))},
    }
    design["content_sha256"] = canonical_hash(design)
    DESIGN.write_text(json.dumps(design, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": design["status"], "powered": powered_panels, "rows": len(output)}, sort_keys=True))


if __name__ == "__main__":
    main()
