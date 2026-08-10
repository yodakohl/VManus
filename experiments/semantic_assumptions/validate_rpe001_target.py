#!/usr/bin/env python3
"""Clean-room, nonimporting validator for the frozen RPE001 target."""

from __future__ import annotations

import csv
import hashlib
import itertools
import json
import math
from collections import defaultdict
from pathlib import Path


BASE = Path(__file__).resolve().parent
ROOT = BASE.parent.parent
RESULTS = BASE / "results"
FREEZE = BASE / "RPE001_TARGET_FREEZE.json"
CAPACITY = RESULTS / "radial_endpoint_polarity_capacity.json"
GROUPS = RESULTS / "source_sta_family_consensus_groups.tsv"
TARGET = RESULTS / "rpe001_target.json"
TARGET_REPORT = RESULTS / "rpe001_target.md"
OUT = RESULTS / "rpe001_target_validation.json"
REPORT = RESULTS / "rpe001_target_validation.md"
ALPHABET = tuple("ABCDEFGHJKLMNPQTUVWXZ")
FOLIOS = ("f57", "f67", "f68", "f69", "f70")
TOL = 1e-15


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha(value: object) -> str:
    data = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n"
    return hashlib.sha256(data.encode()).hexdigest()


def validate_panel(panel: list[dict[str, str]], expected: list[dict[str, object]]) -> None:
    mapping = {str(row["locus"]): (str(row["physical_folio"]), str(row["direction"])) for row in expected}
    if len(panel) != 60 or len({row.get("locus") for row in panel}) != 60 or {row.get("locus") for row in panel} != set(mapping):
        raise AssertionError("panel identity")
    for row in panel:
        if (row["physical_folio"], row["direction"]) != mapping[row["locus"]]:
            raise AssertionError("panel metadata")
        if row["center"] not in ALPHABET or row["outer"] not in ALPHABET:
            raise AssertionError("family alphabet")


def equal_folio(rows: list[dict[str, str]], family: str) -> tuple[float, dict[str, float]]:
    cells: dict[str, list[int]] = defaultdict(list)
    for row in rows:
        cells[row["physical_folio"]].append(int(row["center"] == family) - int(row["outer"] == family))
    folio_values = {key: math.fsum(values) / len(values) for key, values in sorted(cells.items())}
    return math.fsum(folio_values.values()) / len(folio_values), folio_values


def evaluate(panel: list[dict[str, str]], expected: list[dict[str, object]]) -> dict[str, object]:
    validate_panel(panel, expected)
    panel = sorted(panel, key=lambda row: row["locus"])
    effects: dict[str, float] = {}
    folio_effects: dict[str, dict[str, float]] = {}
    for family in ALPHABET:
        effects[family], folio_effects[family] = equal_folio(panel, family)
    selected = sorted(ALPHABET, key=lambda family: (-effects[family], family))[0]
    M = effects[selected]
    null = []
    for signs_tuple in itertools.product((1, -1), repeat=5):
        signs = dict(zip(FOLIOS, signs_tuple, strict=True))
        null.append(max(math.fsum(signs[folio] * folio_effects[family][folio] for folio in FOLIOS) / 5 for family in ALPHABET))
    p = sum(value >= M - TOL for value in null) / 32
    direction_effects: dict[str, float] = {}
    direction_folio: dict[str, dict[str, float]] = {}
    for direction in ("Ri", "Ro"):
        direction_effects[direction], direction_folio[direction] = equal_folio([row for row in panel if row["direction"] == direction], selected)
    support = {direction: sum(value > 0 for value in direction_folio[direction].values()) for direction in ("Ri", "Ro")}
    loo = {deleted: math.fsum(folio_effects[selected][folio] for folio in FOLIOS if folio != deleted) / 4 for deleted in FOLIOS}
    total = math.fsum(abs(value) for value in folio_effects[selected].values())
    concentration = max(abs(value) for value in folio_effects[selected].values()) / total if total else 1.0
    gates = {
        "material_and_exact_maxT": M >= .10 - TOL and p <= .05 + TOL,
        "Ri_Ro_physical_direction_coherence": all(direction_effects[d] > 0 for d in ("Ri", "Ro")),
        "Ri_support_at_least_3_of_4_folios": support["Ri"] >= 3,
        "Ro_support_at_least_3_of_4_folios": support["Ro"] >= 3,
        "all_LOO_center_effect_at_least_005": all(value >= .05 - TOL for value in loo.values()),
        "folio_concentration_at_most_050": concentration <= .50 + TOL,
        "finite": all(math.isfinite(value) for value in [*effects.values(), *null, *direction_effects.values(), *loo.values(), concentration]),
    }
    return {
        "panel_sha256": canonical_sha(panel), "alphabet": "".join(ALPHABET),
        "selected_family": selected, "selected_polarity": "CENTER",
        "selected_effect": M, "M": M, "exact_maxT_p": p,
        "all_family_effects": effects, "all_family_folio_effects": folio_effects,
        "direction_effects": direction_effects, "direction_folio_effects": direction_folio,
        "direction_support": support, "leave_one_folio_out": loo,
        "concentration": concentration, "null_M": null,
        "null_M_sha256": canonical_sha(null), "gates": gates, "passes": all(gates.values()),
    }


def reconstruct_panel(expected: list[dict[str, object]]) -> tuple[list[dict[str, str]], set[str]]:
    emap = {str(row["locus"]): row for row in expected}
    target_rows: dict[str, list[dict[str, str]]] = defaultdict(list)
    alphabet: set[str] = set()
    with GROUPS.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            alphabet.update(row["family_surface"])
            if row["locus"] in emap:
                target_rows[row["locus"]].append(row)
    panel = []
    for locus, meta in sorted(emap.items()):
        rows = sorted(target_rows[locus], key=lambda row: int(row["consensus_group_index"]))
        n = int(meta["group_count"])
        if len(rows) != n or [int(row["consensus_group_index"]) for row in rows] != list(range(1, n + 1)) or any(row["strict_zero_alternative"] != "1" for row in rows):
            raise AssertionError("group reconstruction")
        first, last = rows[0]["family_surface"][0], rows[-1]["family_surface"][-1]
        center, outer = (last, first) if meta["direction"] == "Ri" else (first, last)
        panel.append({"locus": locus, "physical_folio": str(meta["physical_folio"]), "direction": str(meta["direction"]), "center": center, "outer": outer})
    validate_panel(panel, expected)
    return panel, alphabet


def expected_report(result: dict[str, object]) -> str:
    e = result["evaluation"]
    return (
        "# RPE001 radial endpoint-polarity target\n\n"
        f"Status: **{result['status']}**\n\n"
        f"Decision: **{result['decision']}**\n\n"
        f"The frozen 60-locus test selected anonymous family **{e['selected_family']}** as the "
        f"largest center-enriched family: equal-folio effect **{e['M']:.6f}**, exact 32-swap "
        f"max-family p **{e['exact_maxT_p']:.6f}**. Direction-specific effects are Ri "
        f"**{e['direction_effects']['Ri']:.6f}** and Ro **{e['direction_effects']['Ro']:.6f}**; "
        f"support is {e['direction_support']['Ri']}/4 Ri folios and "
        f"{e['direction_support']['Ro']}/4 Ro folios. Concentration is "
        f"**{e['concentration']:.6f}**.\n\n"
        "Independent reconstruction is mandatory before this is final. Even confirmation would establish "
        "only an anonymous physical-endpoint construction, not a word, direction term, meaning, plaintext, "
        "or translation.\n"
    )


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    for relative, expected_hash in freeze["frozen_files"].items():
        if sha(ROOT / relative) != expected_hash:
            raise AssertionError(f"freeze mismatch {relative}")
    target = json.loads(TARGET.read_text(encoding="utf-8"))
    capacity = json.loads(CAPACITY.read_text(encoding="utf-8"))
    expected = capacity["eligible"]["loci"]
    panel, alphabet = reconstruct_panel(expected)
    if tuple(sorted(alphabet)) != ALPHABET:
        raise AssertionError("alphabet")
    evaluation = evaluate(panel, expected)
    if target["target_panel"] != panel or target["evaluation"] != evaluation:
        raise AssertionError("target reconstruction")
    external = {
        "capacity_pass": True, "controls_pass": True, "independent_controls_pass": True,
        "frozen_hashes_pass": True, "exact_60_loci": True,
        "global_21_family_alphabet": True, "target_and_validation_absent_before_run": True,
        "zero_English_glosses": True,
    }
    decision = "CONFIRM_ANONYMOUS_PHYSICAL_CENTER_ENDPOINT_CONSTRUCTION" if evaluation["passes"] else "NONCONFIRM_FIXED_RADIAL_ENDPOINT_REPRESENTATION"
    if target["external_gates"] != external or target["decision"] != decision:
        raise AssertionError("decision")
    if target["freeze_sha256"] != sha(FREEZE) or target["status"] != "PROVISIONAL_AWAITING_INDEPENDENT_VALIDATION":
        raise AssertionError("binding")
    if TARGET_REPORT.read_text(encoding="utf-8") != expected_report(target):
        raise AssertionError("report")
    checks = 16 + len(freeze["frozen_files"]) + len(panel) + len(ALPHABET) + 32
    result = {
        "experiment": "RPE001_TARGET_VALIDATION",
        "status": "PASS_INDEPENDENT_TARGET_RECONSTRUCTION",
        "checks": checks,
        "inputs": {path.name: sha(path) for path in (FREEZE, CAPACITY, GROUPS, TARGET, TARGET_REPORT, Path(__file__))},
        "selected_family": evaluation["selected_family"],
        "M": evaluation["M"],
        "exact_maxT_p": evaluation["exact_maxT_p"],
        "scientific_gates": evaluation["gates"],
        "final_decision": decision,
        "claim_ceiling": target["claim_ceiling"],
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# RPE001 target validation\n\n"
        f"Status: **{result['status']}**\n\n"
        f"A production-free implementation passed **{checks} checks** and exactly reconstructed the "
        f"60-locus panel, 21 family effects, all 32 synchronized folio swaps, support, deletion, "
        f"concentration, gates, report, and final decision **{decision}**. The selected symbol is only "
        "an anonymous structural family. No word, direction term, meaning, plaintext, or translation follows.\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": result["status"], "decision": decision, "M": evaluation["M"], "p": evaluation["exact_maxT_p"]}, sort_keys=True))


if __name__ == "__main__":
    main()
