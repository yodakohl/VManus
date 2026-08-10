#!/usr/bin/env python3
"""Independent, production-free validator for RPE001 capacity and controls."""

from __future__ import annotations

import copy
import csv
import hashlib
import itertools
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
CAPACITY = RESULTS / "radial_endpoint_polarity_capacity.json"
CONTROLS = RESULTS / "rpe001_controls.json"
GROUPS = RESULTS / "source_sta_family_consensus_groups.tsv"
SEPARATORS = RESULTS / "source_separator_transcription.tsv"
OUT = RESULTS / "rpe001_controls_validation.json"
REPORT = RESULTS / "rpe001_controls_validation.md"
ALPHABET = tuple("ABCDEFGHJKLMNPQTUVWXZ")
FOLIOS = ("f57", "f67", "f68", "f69", "f70")
MODES = ("DISTRIBUTED_CENTER", "NULL", "ONE_FOLIO", "TEXT_START_ONLY", "TEXT_END_ONLY", "ONE_DIRECTION_ONLY")
TOL = 1e-15


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def object_digest(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n"
    return hashlib.sha256(payload.encode()).hexdigest()


def folio(page: str) -> str:
    match = re.fullmatch(r"(f\d+)[rv]\d*", page)
    if not match:
        raise AssertionError(page)
    return match.group(1)


def reconstruct_capacity() -> tuple[list[dict[str, object]], dict[str, object]]:
    official: dict[str, set[str]] = defaultdict(set)
    with SEPARATORS.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["code"] in ("@Ri", "@Ro"):
                official[row["locus"]].add(row["code"][1:])
    if len(official) != 142 or Counter(next(iter(v)) for v in official.values()) != Counter({"Ri": 75, "Ro": 67}):
        raise AssertionError("official radial inventory")

    # Only metadata columns are retained. Family identities are never indexed.
    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    with GROUPS.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["code"] in ("@Ri", "@Ro"):
                groups[row["locus"]].append({key: row[key] for key in (
                    "locus", "page", "code", "strict_zero_alternative",
                    "consensus_group_index", "consensus_group_count",
                )})
    eligible: list[dict[str, object]] = []
    for locus, rows in sorted(groups.items()):
        rows.sort(key=lambda row: int(row["consensus_group_index"]))
        n = int(rows[0]["consensus_group_count"])
        if (
            n >= 2
            and len(rows) == n
            and [int(row["consensus_group_index"]) for row in rows] == list(range(1, n + 1))
            and all(row["strict_zero_alternative"] == "1" for row in rows)
            and len({(row["page"], row["code"]) for row in rows}) == 1
        ):
            eligible.append({
                "locus": locus,
                "page": rows[0]["page"],
                "physical_folio": folio(rows[0]["page"]),
                "direction": rows[0]["code"][1:],
                "group_count": n,
            })
    if len(eligible) != 60:
        raise AssertionError("eligible")
    summary = {
        "physical_loci": 60,
        "pages": len({row["page"] for row in eligible}),
        "physical_folios": len({row["physical_folio"] for row in eligible}),
        "direction_counts": dict(sorted(Counter(row["direction"] for row in eligible).items())),
        "folio_counts": dict(sorted(Counter(row["physical_folio"] for row in eligible).items())),
        "page_counts": dict(sorted(Counter(row["page"] for row in eligible).items())),
        "direction_folios": {
            d: sorted({row["physical_folio"] for row in eligible if row["direction"] == d})
            for d in ("Ri", "Ro")
        },
        "loci": eligible,
    }
    return eligible, summary


def check_panel(panel: list[dict[str, str]], expected: list[dict[str, object]]) -> None:
    emap = {str(row["locus"]): (str(row["physical_folio"]), str(row["direction"])) for row in expected}
    if len(panel) != 60 or len({row.get("locus") for row in panel}) != 60:
        raise ValueError("size")
    if {row.get("locus") for row in panel} != set(emap):
        raise ValueError("membership")
    for row in panel:
        if (row.get("physical_folio"), row.get("direction")) != emap[row["locus"]]:
            raise ValueError("metadata")
        if row.get("center") not in ALPHABET or row.get("outer") not in ALPHABET:
            raise ValueError("family")


def equal_folio(panel: list[dict[str, str]], family: str) -> tuple[float, dict[str, float]]:
    cells: dict[str, list[int]] = defaultdict(list)
    for row in panel:
        cells[row["physical_folio"]].append(int(row["center"] == family) - int(row["outer"] == family))
    values = {key: math.fsum(x) / len(x) for key, x in sorted(cells.items())}
    return math.fsum(values.values()) / len(values), values


def evaluate(panel: list[dict[str, str]], expected: list[dict[str, object]]) -> dict[str, object]:
    check_panel(panel, expected)
    panel = sorted(panel, key=lambda row: row["locus"])
    effects: dict[str, float] = {}
    folio_effects: dict[str, dict[str, float]] = {}
    for family in ALPHABET:
        effects[family], folio_effects[family] = equal_folio(panel, family)
    selected = sorted(ALPHABET, key=lambda family: (-effects[family], family))[0]
    M = effects[selected]
    orbit = []
    for signs_tuple in itertools.product((1, -1), repeat=5):
        signs = dict(zip(FOLIOS, signs_tuple, strict=True))
        orbit.append(max(math.fsum(signs[f] * folio_effects[a][f] for f in FOLIOS) / 5 for a in ALPHABET))
    p = sum(value >= M - TOL for value in orbit) / 32
    d_effect: dict[str, float] = {}
    d_folio: dict[str, dict[str, float]] = {}
    for direction in ("Ri", "Ro"):
        d_effect[direction], d_folio[direction] = equal_folio([row for row in panel if row["direction"] == direction], selected)
    support = {d: sum(value > 0 for value in d_folio[d].values()) for d in ("Ri", "Ro")}
    loo = {deleted: math.fsum(folio_effects[selected][f] for f in FOLIOS if f != deleted) / 4 for deleted in FOLIOS}
    denominator = math.fsum(abs(v) for v in folio_effects[selected].values())
    concentration = max(abs(v) for v in folio_effects[selected].values()) / denominator if denominator else 1.0
    gates = {
        "material_and_exact_maxT": M >= .10 - TOL and p <= .05 + TOL,
        "Ri_Ro_physical_direction_coherence": all(d_effect[d] > 0 for d in ("Ri", "Ro")),
        "Ri_support_at_least_3_of_4_folios": support["Ri"] >= 3,
        "Ro_support_at_least_3_of_4_folios": support["Ro"] >= 3,
        "all_LOO_center_effect_at_least_005": all(value >= .05 - TOL for value in loo.values()),
        "folio_concentration_at_most_050": concentration <= .50 + TOL,
        "finite": all(math.isfinite(value) for value in [*effects.values(), *orbit, *d_effect.values(), *loo.values(), concentration]),
    }
    return {
        "panel_sha256": object_digest(panel), "alphabet": "".join(ALPHABET),
        "selected_family": selected, "selected_polarity": "CENTER",
        "selected_effect": M, "M": M, "exact_maxT_p": p,
        "all_family_effects": effects, "all_family_folio_effects": folio_effects,
        "direction_effects": d_effect, "direction_folio_effects": d_folio,
        "direction_support": support, "leave_one_folio_out": loo,
        "concentration": concentration, "null_M": orbit,
        "null_M_sha256": object_digest(orbit), "gates": gates, "passes": all(gates.values()),
    }


def world(expected: list[dict[str, object]], number: int, mode: str) -> list[dict[str, str]]:
    candidate = ALPHABET[number]
    output = []
    for index, meta in enumerate(sorted(expected, key=lambda row: str(row["locus"]))):
        background = ALPHABET[(number + 1 + index) % 21]
        if background == candidate:
            background = ALPHABET[(ALPHABET.index(background) + 1) % 21]
        center = outer = background
        if mode == "DISTRIBUTED_CENTER": center = candidate
        elif mode == "ONE_FOLIO" and meta["physical_folio"] == "f68": center = candidate
        elif mode == "TEXT_START_ONLY":
            if meta["direction"] == "Ro": center = candidate
            else: outer = candidate
        elif mode == "TEXT_END_ONLY":
            if meta["direction"] == "Ri": center = candidate
            else: outer = candidate
        elif mode == "ONE_DIRECTION_ONLY" and meta["direction"] == "Ri": center = candidate
        elif mode != "NULL":
            if mode not in MODES: raise ValueError(mode)
        output.append({"locus": str(meta["locus"]), "physical_folio": str(meta["physical_folio"]), "direction": str(meta["direction"]), "center": center, "outer": outer})
    return output


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    capacity = json.loads(CAPACITY.read_text(encoding="utf-8"))
    controls = json.loads(CONTROLS.read_text(encoding="utf-8"))
    expected, summary = reconstruct_capacity()
    checks = 0
    if capacity["eligible"] != summary:
        raise AssertionError("capacity mismatch")
    checks += 1
    if controls["capacity_loci_sha256"] != object_digest(expected):
        raise AssertionError("capacity digest")
    checks += 1
    rebuilt_records = []
    for number in range(8):
        for mode in MODES:
            rebuilt_records.append({"world": number, "mode": mode, "evaluation": evaluate(world(expected, number, mode), expected)})
            checks += 1
    if controls["records"] != rebuilt_records:
        raise AssertionError("control records")
    pass_counts = {mode: sum(r["evaluation"]["passes"] for r in rebuilt_records if r["mode"] == mode) for mode in MODES}
    if controls["pass_counts"] != pass_counts or pass_counts != {"DISTRIBUTED_CENTER": 8, "NULL": 0, "ONE_FOLIO": 0, "TEXT_START_ONLY": 0, "TEXT_END_ONLY": 0, "ONE_DIRECTION_ONLY": 0}:
        raise AssertionError("pass counts")
    checks += 2

    base_panel = world(expected, 0, "DISTRIBUTED_CENTER")
    base = evaluate(base_panel, expected)
    reordered = evaluate(list(reversed(base_panel)), expected)
    mapping = {family: ALPHABET[(i + 7) % 21] for i, family in enumerate(ALPHABET)}
    relabeled = evaluate([dict(row, center=mapping[row["center"]], outer=mapping[row["outer"]]) for row in base_panel], expected)
    complement = evaluate([dict(row, center=row["outer"], outer=row["center"]) for row in base_panel], expected)
    comparable_keys = ("M", "exact_maxT_p", "concentration", "gates", "passes")
    comparable = lambda x: {key: x[key] for key in comparable_keys}
    invariance = {
        "row_order": comparable(base) == comparable(reordered) and base["panel_sha256"] == reordered["panel_sha256"],
        "family_relabeling": comparable(base) == comparable(relabeled) and relabeled["selected_family"] == mapping[base["selected_family"]] and relabeled["selected_polarity"] == base["selected_polarity"],
        "center_outer_signed_complement": all(
            abs(complement["all_family_effects"][a] + base["all_family_effects"][a]) <= TOL
            and all(abs(complement["all_family_folio_effects"][a][f] + base["all_family_folio_effects"][a][f]) <= TOL for f in complement["all_family_folio_effects"][a])
            for a in ALPHABET
        ),
    }
    if controls["invariance"] != invariance or not all(invariance.values()):
        raise AssertionError("invariance")
    checks += 3

    cases = {"duplicate": copy.deepcopy(base_panel[:-1]) + [copy.deepcopy(base_panel[0])], "missing": copy.deepcopy(base_panel[:-1])}
    cases["wrong_direction"] = copy.deepcopy(base_panel); cases["wrong_direction"][0]["direction"] = "Ri" if cases["wrong_direction"][0]["direction"] == "Ro" else "Ro"
    cases["wrong_folio"] = copy.deepcopy(base_panel); cases["wrong_folio"][0]["physical_folio"] = "f999"
    cases["unknown_family"] = copy.deepcopy(base_panel); cases["unknown_family"][0]["center"] = "?"
    rejected = {}
    for name, panel in cases.items():
        try: check_panel(panel, expected)
        except ValueError: rejected[name] = True
        else: rejected[name] = False
    if controls["mutations_rejected"] != rejected or not all(rejected.values()):
        raise AssertionError("mutations")
    checks += 5

    for name, value in controls["inputs"].items():
        path = RESULTS / name if name.endswith(".json") else BASE / name
        if digest(path) != value:
            raise AssertionError(f"input hash {name}")
        checks += 1
    if controls["status"] != "PASS_ALL_48_SYNTHETIC_WORLD_GATES" or not all(controls["gates"].values()):
        raise AssertionError("top level")
    checks += 2
    result = {
        "experiment": "RPE001_CONTROL_VALIDATION",
        "status": "PASS_INDEPENDENT_CAPACITY_AND_48_WORLD_RECONSTRUCTION",
        "checks": checks,
        "inputs": {path.name: digest(path) for path in (CAPACITY, CONTROLS, GROUPS, SEPARATORS, Path(__file__))},
        "records_reconstructed": 48,
        "pass_counts": pass_counts,
        "target_endpoint_families_accessed": False,
        "decision": "AUTHORIZE_HASH_FREEZE_AND_ONE_TARGET_RUN",
        "claim_ceiling": "Independent validation confirms only capacity, synthetic scorer behavior, invariances, and input guards; it supplies no manuscript endpoint result, word, meaning, plaintext, or translation.",
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# RPE001 control validation\n\n"
        f"Status: **{result['status']}**\n\n"
        f"A nonimporting implementation passed **{checks} checks**, independently rebuilt the public/manual "
        "142-locus radial inventory, the frozen 60-locus strict panel, all 48 synthetic worlds, the exact "
        "32-swap inference, three invariances, and five malformed-input stops. Manuscript endpoint family "
        "values were not accessed. One separately hash-frozen target run is authorized. No word, meaning, "
        "plaintext, or translation follows.\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": result["status"], "checks": checks}, sort_keys=True))


if __name__ == "__main__":
    main()
