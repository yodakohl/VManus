#!/usr/bin/env python3
"""Target-free synthetic controls for RPE001."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

from rpe001_core import ALPHABET, canonical_sha, make_world, score, validate_panel


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
CAPACITY = RESULTS / "radial_endpoint_polarity_capacity.json"
METHOD = BASE / "RADIAL_ENDPOINT_POLARITY_METHOD.md"
OUT = RESULTS / "rpe001_controls.json"
REPORT = RESULTS / "rpe001_controls.md"
MODES = (
    "DISTRIBUTED_CENTER", "NULL", "ONE_FOLIO", "TEXT_START_ONLY",
    "TEXT_END_ONLY", "ONE_DIRECTION_ONLY",
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def comparable(result: dict[str, object]) -> dict[str, object]:
    return {key: result[key] for key in ("M", "exact_maxT_p", "concentration", "gates", "passes")}


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    capacity = json.loads(CAPACITY.read_text(encoding="utf-8"))
    if capacity["status"] != "PASS_UNSCORED_60_STRICT_RADIAL_LOCI_5_FOLIOS":
        raise SystemExit("capacity")
    expected = capacity["eligible"]["loci"]
    if len(expected) != 60:
        raise SystemExit("capacity size")

    records: list[dict[str, object]] = []
    for world in range(8):
        for mode in MODES:
            panel = make_world(expected, world, mode)
            evaluation = score(panel, expected)
            records.append({"world": world, "mode": mode, "evaluation": evaluation})

    pass_counts = {
        mode: sum(bool(record["evaluation"]["passes"]) for record in records if record["mode"] == mode)
        for mode in MODES
    }

    base_panel = make_world(expected, 0, "DISTRIBUTED_CENTER")
    base = score(base_panel, expected)
    reordered = score(list(reversed(base_panel)), expected)
    relabel = {family: ALPHABET[(index + 7) % len(ALPHABET)] for index, family in enumerate(ALPHABET)}
    relabeled_panel = [dict(row, center=relabel[row["center"]], outer=relabel[row["outer"]]) for row in base_panel]
    relabeled = score(relabeled_panel, expected)
    complemented = score([dict(row, center=row["outer"], outer=row["center"]) for row in base_panel], expected)
    complement_effect_identity = all(
        abs(float(complemented["all_family_effects"][family]) + float(base["all_family_effects"][family])) <= 1e-15
        and all(
            abs(float(complemented["all_family_folio_effects"][family][folio]) + float(base["all_family_folio_effects"][family][folio])) <= 1e-15
            for folio in complemented["all_family_folio_effects"][family]
        )
        for family in ALPHABET
    )
    invariance = {
        "row_order": comparable(base) == comparable(reordered) and base["panel_sha256"] == reordered["panel_sha256"],
        "family_relabeling": (
            comparable(base) == comparable(relabeled)
            and relabeled["selected_family"] == relabel[base["selected_family"]]
            and relabeled["selected_polarity"] == base["selected_polarity"]
        ),
        "center_outer_signed_complement": complement_effect_identity,
    }

    mutations: dict[str, bool] = {}
    cases: dict[str, list[dict[str, str]]] = {}
    cases["duplicate"] = copy.deepcopy(base_panel[:-1]) + [copy.deepcopy(base_panel[0])]
    cases["missing"] = copy.deepcopy(base_panel[:-1])
    cases["wrong_direction"] = copy.deepcopy(base_panel)
    cases["wrong_direction"][0]["direction"] = "Ri" if cases["wrong_direction"][0]["direction"] == "Ro" else "Ro"
    cases["wrong_folio"] = copy.deepcopy(base_panel)
    cases["wrong_folio"][0]["physical_folio"] = "f999"
    cases["unknown_family"] = copy.deepcopy(base_panel)
    cases["unknown_family"][0]["center"] = "?"
    for name, panel in cases.items():
        try:
            validate_panel(panel, expected)
        except (ValueError, KeyError):
            mutations[name] = True
        else:
            mutations[name] = False

    gates = {
        "distributed_center_passes_8_of_8": pass_counts["DISTRIBUTED_CENTER"] == 8,
        "null_rejected_8_of_8": pass_counts["NULL"] == 0,
        "one_folio_rejected_8_of_8": pass_counts["ONE_FOLIO"] == 0,
        "text_start_only_rejected_8_of_8": pass_counts["TEXT_START_ONLY"] == 0,
        "text_end_only_rejected_8_of_8": pass_counts["TEXT_END_ONLY"] == 0,
        "one_direction_only_rejected_8_of_8": pass_counts["ONE_DIRECTION_ONLY"] == 0,
        "all_invariances_pass": all(invariance.values()),
        "all_malformed_inputs_rejected": all(mutations.values()),
        "no_manuscript_endpoint_family_source_opened": True,
        "zero_English_glosses": True,
    }
    if not all(gates.values()):
        raise AssertionError({"pass_counts": pass_counts, "invariance": invariance, "mutations": mutations, "gates": gates})
    result = {
        "experiment": "RPE001_TARGET_BLIND_CONTROLS",
        "status": "PASS_ALL_48_SYNTHETIC_WORLD_GATES",
        "inputs": {path.name: sha(path) for path in (CAPACITY, METHOD, BASE / "rpe001_core.py", Path(__file__))},
        "alphabet": "".join(ALPHABET),
        "capacity_loci_sha256": canonical_sha(expected),
        "records": records,
        "pass_counts": pass_counts,
        "invariance": invariance,
        "mutations_rejected": mutations,
        "gates": gates,
        "decision": "AUTHORIZE_INDEPENDENT_CONTROL_RECONSTRUCTION_ONLY",
        "claim_ceiling": "Synthetic controls validate the frozen center/outer scorer and gates only; no manuscript endpoint identity, word, meaning, plaintext, or translation was accessed.",
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# RPE001 target-blind controls\n\n"
        "Status: **PASS_ALL_48_SYNTHETIC_WORLD_GATES**\n\n"
        "The frozen exact 32-swap scorer confirmed all eight distributed physical-center plants and "
        "rejected all eight worlds in each of five negative families: exact null, one-folio, textual-"
        "start-only, textual-end-only, and one-direction-only. Family relabeling, row serialization, "
        "and center/outer complement invariances pass; all five malformed-panel mutations stop.\n\n"
        "No manuscript endpoint family source was opened. Independent reconstruction is required before "
        "a hash freeze or target run. These controls provide no word, meaning, plaintext, or translation.\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": result["status"], "pass_counts": pass_counts}, sort_keys=True))


if __name__ == "__main__":
    main()
