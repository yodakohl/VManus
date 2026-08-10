#!/usr/bin/env python3
"""One-shot hash-frozen manuscript target runner for RPE001."""

from __future__ import annotations

import csv
import hashlib
import json
import os
import tempfile
from collections import defaultdict
from pathlib import Path

from rpe001_core import ALPHABET, score, validate_panel


BASE = Path(__file__).resolve().parent
ROOT = BASE.parent.parent
RESULTS = BASE / "results"
FREEZE = BASE / "RPE001_TARGET_FREEZE.json"
CAPACITY = RESULTS / "radial_endpoint_polarity_capacity.json"
CONTROLS = RESULTS / "rpe001_controls.json"
CONTROL_VALIDATION = RESULTS / "rpe001_controls_validation.json"
GROUPS = RESULTS / "source_sta_family_consensus_groups.tsv"
OUT = RESULTS / "rpe001_target.json"
REPORT = RESULTS / "rpe001_target.md"
VALIDATION_OUT = RESULTS / "rpe001_target_validation.json"
VALIDATION_REPORT = RESULTS / "rpe001_target_validation.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_new(path: Path, payload: str) -> None:
    if path.exists():
        raise SystemExit(f"refusing overwrite: {path.name}")
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        if path.exists():
            raise SystemExit(f"concurrent output appeared: {path.name}")
        os.link(temp_name, path)
    finally:
        try: os.unlink(temp_name)
        except FileNotFoundError: pass


def main() -> None:
    outputs = (OUT, REPORT, VALIDATION_OUT, VALIDATION_REPORT)
    if any(path.exists() for path in outputs):
        raise SystemExit("target or validation artifact already exists")
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    if freeze["experiment"] != "RPE001_TARGET_FREEZE" or freeze["status"] != "FROZEN_TARGET_AND_VALIDATION_ABSENT":
        raise SystemExit("freeze status")
    for relative, expected_sha in freeze["frozen_files"].items():
        path = ROOT / relative
        if not path.is_file() or sha(path) != expected_sha:
            raise SystemExit(f"frozen mismatch: {relative}")
    if freeze["target_outputs"] != [str(path.relative_to(ROOT)) for path in outputs]:
        raise SystemExit("output contract")

    capacity = json.loads(CAPACITY.read_text(encoding="utf-8"))
    controls = json.loads(CONTROLS.read_text(encoding="utf-8"))
    control_validation = json.loads(CONTROL_VALIDATION.read_text(encoding="utf-8"))
    if capacity["status"] != "PASS_UNSCORED_60_STRICT_RADIAL_LOCI_5_FOLIOS":
        raise SystemExit("capacity not pass")
    if controls["status"] != "PASS_ALL_48_SYNTHETIC_WORLD_GATES" or not all(controls["gates"].values()):
        raise SystemExit("controls not pass")
    if control_validation["status"] != "PASS_INDEPENDENT_CAPACITY_AND_48_WORLD_RECONSTRUCTION":
        raise SystemExit("control validation not pass")
    expected = capacity["eligible"]["loci"]
    expected_map = {row["locus"]: row for row in expected}

    all_families: set[str] = set()
    target_rows: dict[str, list[dict[str, str]]] = defaultdict(list)
    with GROUPS.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            surface = row["family_surface"]
            all_families.update(surface)
            if row["locus"] in expected_map:
                target_rows[row["locus"]].append(row)
    if tuple(sorted(all_families)) != ALPHABET:
        raise SystemExit("global family alphabet drift")
    if set(target_rows) != set(expected_map):
        raise SystemExit("target locus coverage")

    panel: list[dict[str, str]] = []
    for locus, meta in sorted(expected_map.items()):
        rows = sorted(target_rows[locus], key=lambda row: int(row["consensus_group_index"]))
        n = int(meta["group_count"])
        if (
            len(rows) != n
            or [int(row["consensus_group_index"]) for row in rows] != list(range(1, n + 1))
            or any(int(row["consensus_group_count"]) != n for row in rows)
            or any(row["strict_zero_alternative"] != "1" for row in rows)
            or any(not row["family_surface"] for row in rows)
        ):
            raise SystemExit(f"target group drift: {locus}")
        first_family = rows[0]["family_surface"][0]
        last_family = rows[-1]["family_surface"][-1]
        if meta["direction"] == "Ri":
            center, outer = last_family, first_family
        elif meta["direction"] == "Ro":
            center, outer = first_family, last_family
        else:
            raise SystemExit("direction")
        panel.append({
            "locus": locus,
            "physical_folio": meta["physical_folio"],
            "direction": meta["direction"],
            "center": center,
            "outer": outer,
        })
    validate_panel(panel, expected)
    evaluation = score(panel, expected)
    scientific_pass = bool(evaluation["passes"])
    external_gates = {
        "capacity_pass": True,
        "controls_pass": True,
        "independent_controls_pass": True,
        "frozen_hashes_pass": True,
        "exact_60_loci": len(panel) == 60,
        "global_21_family_alphabet": "".join(ALPHABET) == evaluation["alphabet"],
        "target_and_validation_absent_before_run": True,
        "zero_English_glosses": True,
    }
    decision = "CONFIRM_ANONYMOUS_PHYSICAL_CENTER_ENDPOINT_CONSTRUCTION" if scientific_pass and all(external_gates.values()) else "NONCONFIRM_FIXED_RADIAL_ENDPOINT_REPRESENTATION"
    result = {
        "experiment": "RPE001_RADIAL_ENDPOINT_POLARITY_TARGET",
        "status": "PROVISIONAL_AWAITING_INDEPENDENT_VALIDATION",
        "freeze_sha256": sha(FREEZE),
        "inputs": {path.name: sha(path) for path in (FREEZE, CAPACITY, CONTROLS, CONTROL_VALIDATION, GROUPS, BASE / "rpe001_core.py", Path(__file__))},
        "target_panel": panel,
        "evaluation": evaluation,
        "external_gates": external_gates,
        "decision": decision,
        "claim_ceiling": (
            "A pass identifies only an anonymous STA family enriched at the physical center endpoint of "
            "strict multi-group radial loci across inward and outward text. It does not identify a word, "
            "direction term, meaning, sound, language, cipher, plaintext, or translation."
        ),
    }
    report = (
        "# RPE001 radial endpoint-polarity target\n\n"
        f"Status: **{result['status']}**\n\n"
        f"Decision: **{decision}**\n\n"
        f"The frozen 60-locus test selected anonymous family **{evaluation['selected_family']}** as the "
        f"largest center-enriched family: equal-folio effect **{evaluation['M']:.6f}**, exact 32-swap "
        f"max-family p **{evaluation['exact_maxT_p']:.6f}**. Direction-specific effects are Ri "
        f"**{evaluation['direction_effects']['Ri']:.6f}** and Ro **{evaluation['direction_effects']['Ro']:.6f}**; "
        f"support is {evaluation['direction_support']['Ri']}/4 Ri folios and "
        f"{evaluation['direction_support']['Ro']}/4 Ro folios. Concentration is "
        f"**{evaluation['concentration']:.6f}**.\n\n"
        "Independent reconstruction is mandatory before this is final. Even confirmation would establish "
        "only an anonymous physical-endpoint construction, not a word, direction term, meaning, plaintext, "
        "or translation.\n"
    )
    # Recheck absence immediately before installing both artifacts.
    if any(path.exists() for path in outputs):
        raise SystemExit("output appeared before installation")
    atomic_new(REPORT, report)
    try:
        atomic_new(OUT, json.dumps(result, indent=2, sort_keys=True) + "\n")
    except BaseException:
        try: REPORT.unlink()
        except FileNotFoundError: pass
        raise
    print(json.dumps({"decision": decision, "family": evaluation["selected_family"], "M": evaluation["M"], "p": evaluation["exact_maxT_p"]}, sort_keys=True))


if __name__ == "__main__":
    main()
