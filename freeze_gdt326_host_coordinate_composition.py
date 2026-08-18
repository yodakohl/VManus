#!/usr/bin/env python3
"""Freeze novel held-folio host-coordinate edges without their outcomes."""
import csv
import hashlib
import json
from pathlib import Path

R = Path(__file__).resolve().parent
SOURCE = R / "gdt278_native_event_inventory.tsv"
METHOD = R / "GDT326_HOST_COORDINATE_COMPOSITION_METHOD.md"
G325 = R / "gdt325_result.json"
PANEL = R / "gdt326_frozen_panel.tsv"
CAPACITY = R / "gdt326_capacity.tsv"
DESIGN = R / "gdt326_design.json"
COORD = ("local_frame", "inner_d", "right_family", "dy_closure", "b3")


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def canonical_hash(value): return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()
def read(path):
    with Path(path).open(encoding="utf8", newline="") as handle: return list(csv.DictReader(handle, delimiter="\t"))
def write(path, rows):
    with Path(path).open("w", encoding="utf8", newline="") as handle:
        writer = csv.DictWriter(handle, rows[0].keys(), delimiter="\t", lineterminator="\n"); writer.writeheader(); writer.writerows(rows)


def main():
    rows = [row for row in read(SOURCE) if row["control_id"] == "VOYNICH_REFERENCE"]
    assert not any(row["page"].startswith("f84") or row["locus"].startswith("f84") for row in rows)
    folios = sorted({row["physical_folio"] for row in rows}); panel = []
    for folio in folios:
        training = [row for row in rows if row["physical_folio"] != folio]; target = [row for row in rows if row["physical_folio"] == folio]
        hosts = {row["page_host"] for row in training}; coordinates = {tuple(row[key] for key in COORD) for row in training}; edges = {(row["page_host"],) + tuple(row[key] for key in COORD) for row in training}
        for row in target:
            coordinate = tuple(row[key] for key in COORD); edge = (row["page_host"],) + coordinate
            if row["page_host"] not in hosts or coordinate not in coordinates or edge in edges: continue
            panel.append({"event_id_sha256": hashlib.sha256(row["observation_id"].encode()).hexdigest()[:20], "physical_folio": folio, "page": row["page"], "locus": row["locus"], "section": row["section"], "register": row["register"], "currier": row["currier"], "hand": row["hand"], "host_id": hashlib.sha256(("HOST|" + row["page_host"]).encode()).hexdigest()[:20], "target_coordinate": "WITHHELD_UNTIL_SCORING"})
    panel.sort(key=lambda row: (row["physical_folio"], row["locus"], row["event_id_sha256"])); write(PANEL, panel)
    capacity = [{"events": len(panel), "folios": len({row["physical_folio"] for row in panel}), "hosts": len({row["host_id"] for row in panel}), "all_reference_events": len(rows), "all_reference_hosts": len({row["page_host"] for row in rows}), "all_reference_coordinates": len({tuple(row[key] for key in COORD) for row in rows}), "all_reference_edges": len({(row["page_host"],) + tuple(row[key] for key in COORD) for row in rows})}]; write(CAPACITY, capacity)
    design = {"schema": "GDT326_HOST_COORDINATE_COMPOSITION_DESIGN_V1", "status": "FROZEN_BEFORE_HOST_COORDINATE_SCORING", "coordinate_fields": list(COORD), "fold": "LEAVE_ONE_PHYSICAL_FOLIO_OUT", "eligibility": ["HOST_SEEN_IN_TRAINING", "COORDINATE_SEEN_IN_TRAINING", "HOST_X_COORDINATE_EDGE_UNSEEN_IN_TRAINING"], "models": ["REGISTER_TABLE", "HOST_TABLE", "HOST_FACTORIAL", "HOST_FACTORIAL_REGISTER"], "alpha": 0.5, "primary_weighting": "EQUAL_HELD_FOLIOS", "sensitivity_weighting": "HELD_EVENTS", "selector_bits": 2.0, "null": {"worlds": 8192, "seed": 32620260818, "strata": "HELD_PHYSICAL_FOLIO", "unit": "COMPLETE_COORDINATE", "scope": "FIXED_PREDICTION_MAX_FOUR_DIAGNOSTIC"}, "decision": {"selector_paid_gain_positive": True, "beats_register_and_host_table": True, "positive_folios_min": 50, "max_four_p_le": 0.05}, "claim_ceiling": "Held-folio opaque-host renderer-coordinate factorization only; no word morpheme category meaning sound language plaintext or translation.", "f84": {"authorized": False, "opened": False, "parsed": False, "retained": False, "joined": False, "scored": False}, "inputs": {path.name: sha(path) for path in (SOURCE, METHOD, G325)}, "outputs": {path.name: sha(path) for path in (PANEL, CAPACITY)}, "implementation": {Path(__file__).name: sha(Path(__file__))}}
    design["content_sha256"] = canonical_hash(design); DESIGN.write_text(json.dumps(design, indent=2, sort_keys=True) + "\n"); print(json.dumps({"status": design["status"], "capacity": capacity[0]}, sort_keys=True))


if __name__ == "__main__": main()
