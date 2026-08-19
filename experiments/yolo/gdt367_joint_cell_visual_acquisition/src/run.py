#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from tools.vmanus_experiment import canonical_json_bytes, sha256_file  # noqa:E402

EXP = ROOT / "experiments/yolo/gdt367_joint_cell_visual_acquisition"
ART = EXP / "artifacts"
TARGETS = ART / "gdt367_target_manifest.tsv"
OBS = ART / "gdt367_visual_observations.tsv"
FREEZE = ART / "gdt367_freeze.json"
OUT_CAP = ART / "gdt367_capacity.tsv"
OUT_RESULT = ART / "gdt367_result.json"


def read(path):
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    targets = read(TARGETS); obs = read(OBS)
    t = {r["gdt367_target_id"]: r for r in targets}
    o = {r["gdt367_target_id"]: r for r in obs}
    assert len(t) == len(o) == 27 and set(t) == set(o)
    axes = ["contact_gap_state", "broad_closed_form", "fork_or_branch", "colored_fill"]
    rows = []
    for scope_name, key in (("GLOBAL", None), ("FOLIO", "physical_folio"), ("ARRAY", "array_id")):
        groups = {"ALL": list(t)} if key is None else defaultdict(list)
        if key is not None:
            for target_id, r in t.items(): groups[r[key]].append(target_id)
        for scope_id, ids in sorted(groups.items()):
            for axis in axes:
                values = [t[i][axis] if axis == "contact_gap_state" else o[i][axis] for i in ids]
                counts = Counter(values)
                binary_states = [s for s in counts if s not in {"UNCERTAIN", "UNCERTAIN_COMPONENT"}]
                rows.append({"scope": scope_name, "scope_id": scope_id, "axis": axis.upper(), "n": len(ids), "state_counts_json": json.dumps(dict(sorted(counts.items())), separators=(",", ":")), "secure_state_count": len(binary_states), "mobile": int(len(binary_states) >= 2)})
    fields = list(rows[0])
    with OUT_CAP.open("w", newline="") as handle:
        w = csv.DictWriter(handle, fields, delimiter="\t", lineterminator="\n"); w.writeheader(); w.writerows(rows)

    global_rows = {r["axis"]: r for r in rows if r["scope"] == "GLOBAL"}
    informative_new_axes = [a for a in ("BROAD_CLOSED_FORM", "FORK_OR_BRANCH", "COLORED_FILL") if global_rows[a]["mobile"]]
    mobile_new_by_multiple_folios = []
    for axis in informative_new_axes:
        n_mobile = sum(r["mobile"] for r in rows if r["scope"] == "FOLIO" and r["axis"] == axis)
        if n_mobile >= 2: mobile_new_by_multiple_folios.append(axis)
    status = "NEW_AXES_INSUFFICIENT_FOR_JOINT_FORMAL_SEARCH" if len(mobile_new_by_multiple_folios) < 2 else "JOINT_FORMAL_SEARCH_CAPACITY_PRESENT"
    payload = {
        "schema": "GDT367_RESULT_V1",
        "status": status,
        "target_count": 27,
        "physical_folios": 3,
        "visual_axis_count_including_contact_gap": 4,
        "global_axis_counts": {a: json.loads(global_rows[a]["state_counts_json"]) for a in global_rows},
        "globally_mobile_new_axes": informative_new_axes,
        "new_axes_mobile_within_at_least_two_folios": mobile_new_by_multiple_folios,
        "formal_rows_loaded_or_joined": False,
        "formal_search_run": False,
        "historical_contact_gap_gates_rewritten": False,
        "f84_accessed": False,
        "interpretation": "The frozen broad-form and colored-fill axes are one-sided. Fork/branch supplies only two absences; it is the sole new axis mobile within at least two physical folios. The panel still lacks a multi-axis within-folio contrast suitable for a joint formal search.",
        "inputs": {str(p.relative_to(ROOT)): sha256_file(p) for p in (TARGETS, OBS, FREEZE, EXP / "METHOD.md")},
        "outputs": {str(OUT_CAP.relative_to(ROOT)): sha256_file(OUT_CAP)},
        "implementation": {str(Path(__file__).relative_to(ROOT)): sha256_file(Path(__file__))},
        "claim_ceiling": "VISUAL_CAPACITY_AUDIT_ONLY_NO_FORMAL_OR_SEMANTIC_ASSOCIATION",
    }
    payload["content_hash"] = hashlib.sha256(canonical_json_bytes(payload)).hexdigest()
    OUT_RESULT.write_bytes(canonical_json_bytes(payload))


if __name__ == "__main__":
    main()
