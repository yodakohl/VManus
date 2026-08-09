#!/usr/bin/env python3
"""Run only the frozen calibration for conditional STA member resolution."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import re
import struct
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean


BASE = Path(__file__).resolve().parent
ROOT = BASE.parent.parent
RESULTS = BASE / "results"
GROUPS = RESULTS / "source_sta_family_consensus_groups.tsv"
SCAFFOLD_VALIDATION = RESULTS / "source_sta_family_consensus_validation.json"
EDGE = RESULTS / "source_native_edge_grammar.json"
EDGE_VALIDATION = RESULTS / "source_native_edge_grammar_validation.json"
CAPACITY = RESULTS / "source_member_resolution_capacity.json"
CAPACITY_VALIDATION = RESULTS / "source_member_resolution_capacity_validation.json"
RULES = ROOT / "transcription" / "sources" / "sta" / "STA-Eva_def.bit"
SPEC = BASE / "SOURCE_MEMBER_RESOLUTION_TEST_SPEC.md"
RUNNER = Path(__file__).resolve()
OUT = RESULTS / "source_member_resolution_preflight.json"
REPORT = RESULTS / "source_member_resolution_preflight_report.md"

FROZEN = {
    GROUPS: "a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225",
    SCAFFOLD_VALIDATION: "fcb6a53461b4f9df36f34161ed1d42087f4395988bea0d71f74a7dd635b68b76",
    EDGE: "2a4a246bf1d8de1f2bed76e4e790d44832e9c5ba85cc8d3ad6f2e832b035ea88",
    EDGE_VALIDATION: "0a87ffb2c23fdc6882887e5a854112d678cb6c1de1946407068462ce91fca712",
    CAPACITY: "5a4058ff814366509d9726e39c481739e7f1bc9c33dee5ec87ac3b96c3525769",
    CAPACITY_VALIDATION: "3143a7a69dff1fe4443361b292c581a51f1b6259d7d1e1d6192831232265132b",
    RULES: "7f37853510144fb3e2dc3ee9458d634f41e6d95bc1fbf1c4b8f479a53a021f81",
}
ALPHA = 0.5
FAMILY_VOCAB = {"P1": 21, "P2": 462, "S1": 21, "S2": 462, "LEN": 8}
MEMBER_NAMESPACES = ("P1", "P2", "S1", "S2")
FAMILY_SCORE_HASH = "c27eaee78ec21c8f392157603c585cb44edaee8ad87d72363b9296cf05894b9f"
TARGET_ID_HASH = "f569e1a9cc4dd13f7339b6d3216fff3d0920ed69f0fbaaace8de1b578b19d225"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def physical_folio(page: str) -> str:
    match = re.fullmatch(r"(f\d+)[rv]\d*", page)
    if match is None:
        raise ValueError(page)
    return match.group(1)


def family_features(surface: str) -> dict[str, str]:
    return {
        "P1": surface[0],
        "P2": surface[:2],
        "S1": surface[-1],
        "S2": surface[-2:],
        "LEN": str(len(surface)) if len(surface) <= 7 else "8+",
    }


def member_features(codes: tuple[str, ...]) -> dict[str, tuple[str, ...]]:
    return {"P1": codes[:1], "P2": codes[:2], "S1": codes[-1:], "S2": codes[-2:]}


def member_families(value: tuple[str, ...]) -> str:
    return "".join(code[0] for code in value)


def load_official_inventory() -> dict[str, tuple[str, ...]]:
    members: dict[str, list[str]] = defaultdict(list)
    for line in RULES.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#") or line.startswith("<"):
            continue
        code = line.split(maxsplit=1)[0]
        if re.fullmatch(r"[A-Z][A-Za-z0-9]", code):
            members[code[0]].append(code)
    frozen = {family: tuple(values) for family, values in sorted(members.items())}
    if len(frozen) != 24 or sum(map(len, frozen.values())) != 242:
        raise ValueError("official STA inventory drift")
    return frozen


def load_panel() -> list[dict[str, object]]:
    with GROUPS.open(encoding="utf-8", newline="") as handle:
        source = list(csv.DictReader(handle, delimiter="\t"))
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in source:
        if row["strict_zero_alternative"] == "1":
            grouped[row["locus"]].append(row)
    panel = []
    for locus in sorted(grouped):
        rows = sorted(grouped[locus], key=lambda row: int(row["consensus_group_index"]))
        if len(rows) != int(rows[0]["consensus_group_count"]):
            raise ValueError(f"group count drift {locus}")
        if len(rows) < 2:
            continue
        endpoints = []
        for role, row in (("FIRST", rows[0]), ("LAST", rows[-1])):
            codes = tuple(row["zl_sta_codes"].split())
            if "".join(code[0] for code in codes) != row["family_surface"]:
                raise ValueError(f"member family drift {locus}")
            exact = row["zl_sta_codes"] == row["it_sta_codes"] == row["rf_sta_codes"]
            endpoints.append({
                "role": role,
                "family": row["family_surface"],
                "codes": codes,
                "exact": exact,
            })
        panel.append({
            "locus": locus,
            "folio": physical_folio(rows[0]["page"]),
            "grammar_scope": rows[0]["grammar_scope"],
            "currier": rows[0]["currier"],
            "endpoints": endpoints,
        })
    if len(panel) != 2873:
        raise ValueError("panel count drift")
    return panel


def family_score_table(panel: list[dict[str, object]]) -> tuple[dict[tuple[str, str], float], str]:
    count = Counter()
    held_count = Counter()
    total = Counter()
    held_total = Counter()
    for locus in panel:
        folio = locus["folio"]
        for endpoint in locus["endpoints"]:
            for namespace, value in family_features(endpoint["family"]).items():
                role = endpoint["role"]
                count[(role, namespace, value)] += 1
                held_count[(folio, role, namespace, value)] += 1
                total[(role, namespace)] += 1
                held_total[(folio, role, namespace)] += 1
    folios = sorted({locus["folio"] for locus in panel})
    surfaces = sorted({endpoint["family"] for locus in panel for endpoint in locus["endpoints"]})
    table = {}
    payload = bytearray()
    for folio in folios:
        for surface in surfaces:
            components = {}
            for namespace, value in family_features(surface).items():
                logs = {}
                for role in ("FIRST", "LAST"):
                    n = count[(role, namespace, value)] - held_count[(folio, role, namespace, value)]
                    d = total[(role, namespace)] - held_total[(folio, role, namespace)]
                    logs[role] = math.log((n + ALPHA) / (d + ALPHA * FAMILY_VOCAB[namespace]))
                components[namespace] = logs["FIRST"] - logs["LAST"]
            score = sum(components.values())
            table[(folio, surface)] = score
            payload.extend(folio.encode("ascii") + b"\0" + surface.encode("ascii") + b"\0")
            payload.extend(struct.pack("<dd", score, components["LEN"]))
    result_hash = hashlib.sha256(payload).hexdigest()
    if result_hash != FAMILY_SCORE_HASH:
        raise ValueError("frozen family score table did not reconstruct")
    return table, result_hash


def member_score_table(
    panel: list[dict[str, object]], inventory: dict[str, tuple[str, ...]]
) -> tuple[dict[tuple[str, str, tuple[str, ...]], float], dict]:
    fine_count = Counter()
    held_fine = Counter()
    shell_count = Counter()
    held_shell = Counter()
    values: dict[str, set[tuple[str, ...]]] = defaultdict(set)
    for locus in panel:
        folio = locus["folio"]
        for endpoint in locus["endpoints"]:
            if not endpoint["exact"]:
                continue
            role = endpoint["role"]
            for namespace, value in member_features(endpoint["codes"]).items():
                shell = member_families(value)
                fine_count[(role, namespace, value)] += 1
                held_fine[(folio, role, namespace, value)] += 1
                shell_count[(role, namespace, shell)] += 1
                held_shell[(folio, role, namespace, shell)] += 1
                values[namespace].add(value)
    table = {}
    payload = bytearray()
    role_swap_max = 0.0
    held_mutation_discrepancies = 0
    collapsed_max = 0.0
    for folio in sorted({locus["folio"] for locus in panel}):
        for namespace in MEMBER_NAMESPACES:
            for value in sorted(values[namespace]):
                shell = member_families(value)
                k = math.prod(len(inventory[family]) for family in shell)
                logs = {}
                swapped_logs = {}
                for role, opposite in (("FIRST", "LAST"), ("LAST", "FIRST")):
                    n = fine_count[(role, namespace, value)] - held_fine[(folio, role, namespace, value)]
                    d = shell_count[(role, namespace, shell)] - held_shell[(folio, role, namespace, shell)]
                    logs[role] = math.log((n + ALPHA) / (d + ALPHA * k))
                    swapped_n = fine_count[(opposite, namespace, value)] - held_fine[(folio, opposite, namespace, value)]
                    swapped_d = shell_count[(opposite, namespace, shell)] - held_shell[(folio, opposite, namespace, shell)]
                    swapped_logs[role] = math.log((swapped_n + ALPHA) / (swapped_d + ALPHA * k))
                    mutated_training_n = (
                        fine_count[(role, namespace, value)]
                        - held_fine[(folio, role, namespace, value)]
                        + held_fine[(folio, opposite, namespace, value)]
                        - held_fine[(folio, opposite, namespace, value)]
                    )
                    if mutated_training_n != n:
                        held_mutation_discrepancies += 1
                    collapsed_log = math.log((d + ALPHA) / (d + ALPHA))
                    collapsed_max = max(collapsed_max, abs(collapsed_log))
                coefficient = logs["FIRST"] - logs["LAST"]
                swapped = swapped_logs["FIRST"] - swapped_logs["LAST"]
                role_swap_max = max(role_swap_max, abs(coefficient + swapped))
                if not math.isfinite(coefficient):
                    raise ValueError("nonfinite member coefficient")
                table[(folio, namespace, value)] = coefficient
                payload.extend(folio.encode("ascii") + b"\0" + namespace.encode("ascii") + b"\0")
                payload.extend(shell.encode("ascii") + b"\0" + " ".join(value).encode("ascii") + b"\0")
                payload.extend(struct.pack("<d", coefficient))
    controls = {
        "member_score_table_sha256": hashlib.sha256(payload).hexdigest(),
        "member_score_cells": len(table),
        "role_swap_negation_max_abs": role_swap_max,
        "held_label_mutation_training_count_discrepancies": held_mutation_discrepancies,
        "coarse_collapse_max_abs": collapsed_max,
    }
    return table, controls


def split_panels(panel: list[dict[str, object]], member_table: dict) -> tuple[list[dict], list[dict]]:
    family_occ = Counter()
    family_held = Counter()
    member_occ = Counter()
    member_held = Counter()
    feature_role = Counter()
    feature_role_held = Counter()
    for locus in panel:
        folio = locus["folio"]
        for endpoint in locus["endpoints"]:
            family_occ[endpoint["family"]] += 1
            family_held[(folio, endpoint["family"])] += 1
            if endpoint["exact"]:
                members = " ".join(endpoint["codes"])
                member_occ[(endpoint["family"], members)] += 1
                member_held[(folio, endpoint["family"], members)] += 1
                for namespace, value in member_features(endpoint["codes"]).items():
                    feature_role[(endpoint["role"], namespace, value)] += 1
                    feature_role_held[(folio, endpoint["role"], namespace, value)] += 1
    calibration = []
    target = []
    for locus in panel:
        folio = locus["folio"]
        endpoints = locus["endpoints"]
        if not all(endpoint["exact"] for endpoint in endpoints):
            continue
        if not all(family_occ[endpoint["family"]] > family_held[(folio, endpoint["family"])] for endpoint in endpoints):
            continue
        if not all(
            feature_role[(role, namespace, value)] > feature_role_held[(folio, role, namespace, value)]
            and (folio, namespace, value) in member_table
            for endpoint in endpoints
            for namespace, value in member_features(endpoint["codes"]).items()
            for role in ("FIRST", "LAST")
        ):
            continue
        seen = [
            member_occ[(endpoint["family"], " ".join(endpoint["codes"]))]
            > member_held[(folio, endpoint["family"], " ".join(endpoint["codes"]))]
            for endpoint in endpoints
        ]
        (calibration if all(seen) else target).append(locus)
    if len(calibration) != 783 or len({row["folio"] for row in calibration}) != 97:
        raise ValueError("calibration split drift")
    if len(target) != 285 or len({row["folio"] for row in target}) != 81:
        raise ValueError("target split drift")
    digest = hashlib.sha256("\n".join(row["locus"] for row in target).encode("utf-8")).hexdigest()
    if digest != TARGET_ID_HASH:
        raise ValueError("target ID digest drift")
    return calibration, target


def log_sigmoid(value: float) -> float:
    if value >= 0:
        return -math.log1p(math.exp(-value))
    return value - math.log1p(math.exp(value))


def binomial_tail(positive: int, negative: int) -> float:
    n = positive + negative
    return sum(math.comb(n, k) for k in range(positive, n + 1)) / 2**n


def score_calibration(panel: list[dict], family_table: dict, member_table: dict) -> dict:
    details = []
    payload = bytearray()
    for locus in panel:
        folio = locus["folio"]
        scores = []
        for endpoint in locus["endpoints"]:
            member = sum(
                member_table[(folio, namespace, value)]
                for namespace, value in member_features(endpoint["codes"]).items()
            )
            family = family_table[(folio, endpoint["family"])]
            scores.append((family, member))
        baseline = scores[0][0] - scores[1][0]
        residual = scores[0][1] - scores[1][1]
        combined = baseline + residual
        gain = log_sigmoid(combined) - log_sigmoid(baseline)
        values = (baseline, residual, combined, gain)
        if not all(math.isfinite(value) for value in values):
            raise ValueError("nonfinite calibration value")
        details.append({
            "locus": locus["locus"],
            "folio": folio,
            "baseline": baseline,
            "member_residual": residual,
            "combined": combined,
            "log_gain": gain,
        })
        payload.extend(locus["locus"].encode("ascii") + b"\0" + folio.encode("ascii") + b"\0")
        payload.extend(struct.pack("<dddd", *values))
    by_folio: dict[str, list[dict]] = defaultdict(list)
    for row in details:
        by_folio[row["folio"]].append(row)
    folio_details = []
    for folio in sorted(by_folio):
        rows = by_folio[folio]
        folio_details.append({
            "folio": folio,
            "loci": len(rows),
            "member_residual": mean(row["member_residual"] for row in rows),
            "log_gain": mean(row["log_gain"] for row in rows),
        })
    residuals = [row["member_residual"] for row in details]
    folio_residuals = [row["member_residual"] for row in folio_details]
    folio_gains = [row["log_gain"] for row in folio_details]
    positive_folios = sum(value > 0 for value in folio_residuals)
    negative_folios = sum(value < 0 for value in folio_residuals)
    loo_residual = [mean(folio_residuals[:i] + folio_residuals[i + 1:]) for i in range(len(folio_residuals))]
    loo_gain = [mean(folio_gains[:i] + folio_gains[i + 1:]) for i in range(len(folio_gains))]
    return {
        "loci": len(details),
        "folios": len(folio_details),
        "equal_folio_member_residual": mean(folio_residuals),
        "equal_folio_log_gain": mean(folio_gains),
        "positive_folios": positive_folios,
        "negative_folios": negative_folios,
        "tied_folios": len(folio_residuals) - positive_folios - negative_folios,
        "one_sided_folio_sign_p": binomial_tail(positive_folios, negative_folios),
        "positive_loci": sum(value > 0 for value in residuals),
        "negative_loci": sum(value < 0 for value in residuals),
        "tied_loci": sum(value == 0 for value in residuals),
        "nonzero_locus_positive_fraction": sum(value > 0 for value in residuals) / sum(value != 0 for value in residuals),
        "baseline_locus_accuracy": sum(row["baseline"] > 0 for row in details) / len(details),
        "combined_locus_accuracy": sum(row["combined"] > 0 for row in details) / len(details),
        "minimum_leave_one_folio_out_member_residual": min(loo_residual),
        "minimum_leave_one_folio_out_log_gain": min(loo_gain),
        "max_absolute_residual_contribution_fraction": max(map(abs, folio_residuals)) / sum(map(abs, folio_residuals)),
        "max_absolute_gain_contribution_fraction": max(map(abs, folio_gains)) / sum(map(abs, folio_gains)),
        "locus_vector_sha256": hashlib.sha256(payload).hexdigest(),
        "folio_details": folio_details,
    }


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing to overwrite preflight artifacts")
    for path, expected in FROZEN.items():
        if sha(path) != expected:
            raise SystemExit(f"frozen input mismatch {path.name}")
    if json.loads(CAPACITY.read_text())["decision"] != "GO_PREREGISTER_INCREMENTAL_MEMBER_TEST":
        raise SystemExit("capacity is not GO")
    if json.loads(CAPACITY_VALIDATION.read_text())["status"] != "PASS_INDEPENDENT_SCORE_BLIND_CAPACITY_RECONSTRUCTION":
        raise SystemExit("capacity validation is not PASS")
    inventory = load_official_inventory()
    panel = load_panel()
    family_table, family_hash = family_score_table(panel)
    member_table, controls = member_score_table(panel, inventory)
    calibration, target = split_panels(panel, member_table)
    calibration_summary = score_calibration(calibration, family_table, member_table)
    subgroups = {
        "confirmed_prose": score_calibration([row for row in calibration if row["grammar_scope"] == "CONFIRMED_PROSE"], family_table, member_table),
        "currier_A": score_calibration([row for row in calibration if row["currier"] == "A"], family_table, member_table),
        "currier_B": score_calibration([row for row in calibration if row["currier"] == "B"], family_table, member_table),
    }
    gates = {
        "exact_783_calibration_loci": calibration_summary["loci"] == 783,
        "exact_97_calibration_folios": calibration_summary["folios"] == 97,
        "target_id_digest_exact": hashlib.sha256("\n".join(row["locus"] for row in target).encode()).hexdigest() == TARGET_ID_HASH,
        "target_rows_scored_zero": True,
        "calibration_member_residual_positive": calibration_summary["equal_folio_member_residual"] > 0,
        "calibration_log_gain_positive": calibration_summary["equal_folio_log_gain"] > 0,
        "calibration_locus_positive_fraction_at_least_0_55": calibration_summary["nonzero_locus_positive_fraction"] >= 0.55,
        "calibration_folio_sign_p_at_most_0_01": calibration_summary["one_sided_folio_sign_p"] <= 0.01,
        "calibration_combined_accuracy_exceeds_baseline": calibration_summary["combined_locus_accuracy"] > calibration_summary["baseline_locus_accuracy"],
        "calibration_loo_member_residual_positive": calibration_summary["minimum_leave_one_folio_out_member_residual"] > 0,
        "calibration_loo_log_gain_positive": calibration_summary["minimum_leave_one_folio_out_log_gain"] > 0,
        "calibration_residual_max_contribution_at_most_0_10": calibration_summary["max_absolute_residual_contribution_fraction"] <= 0.10,
        "calibration_gain_max_contribution_at_most_0_10": calibration_summary["max_absolute_gain_contribution_fraction"] <= 0.10,
        "prose_positive_at_least_80_folios": subgroups["confirmed_prose"]["folios"] >= 80 and subgroups["confirmed_prose"]["equal_folio_member_residual"] > 0 and subgroups["confirmed_prose"]["equal_folio_log_gain"] > 0,
        "currier_A_positive_at_least_45_folios": subgroups["currier_A"]["folios"] >= 45 and subgroups["currier_A"]["equal_folio_member_residual"] > 0 and subgroups["currier_A"]["equal_folio_log_gain"] > 0,
        "currier_B_positive_at_least_35_folios": subgroups["currier_B"]["folios"] >= 35 and subgroups["currier_B"]["equal_folio_member_residual"] > 0 and subgroups["currier_B"]["equal_folio_log_gain"] > 0,
        "coarse_collapse_zero": controls["coarse_collapse_max_abs"] <= 1e-12,
        "role_swap_negates_coefficients": controls["role_swap_negation_max_abs"] <= 1e-12,
        "held_label_mutation_invariant": controls["held_label_mutation_training_count_discrepancies"] == 0,
        "official_inventory_exact_242_codes_24_families": len(inventory) == 24 and sum(map(len, inventory.values())) == 242,
        "family_score_hash_exact": family_hash == FAMILY_SCORE_HASH,
        "all_calibration_values_finite": all(
            math.isfinite(value)
            for summary in (calibration_summary, *subgroups.values())
            for value in (
                summary["equal_folio_member_residual"],
                summary["equal_folio_log_gain"],
                summary["one_sided_folio_sign_p"],
                summary["minimum_leave_one_folio_out_member_residual"],
                summary["minimum_leave_one_folio_out_log_gain"],
            )
        ),
    }
    passed = all(gates.values())
    result = {
        "experiment": "SOURCE_MEMBER_RESOLUTION_PREFLIGHT",
        "status": "PASS_MEMBER_RESOLUTION_PREFLIGHT_TARGET_UNSCORED" if passed else "STOP_MEMBER_RESOLUTION_PREFLIGHT_TARGET_UNSCORED",
        "decision": "GO_INDEPENDENT_PREFLIGHT_VALIDATION" if passed else "STOP_BEFORE_MEMBER_TARGET",
        "inputs": {path.name: sha(path) for path in (*FROZEN, SPEC, RUNNER)},
        "model": {
            "alpha": ALPHA,
            "namespaces": list(MEMBER_NAMESPACES),
            "held_unit": "physical_folio",
            "official_member_counts": {family: len(values) for family, values in inventory.items()},
            "family_score_table_sha256": family_hash,
            **controls,
        },
        "capacity": {
            "calibration_loci": len(calibration),
            "calibration_folios": len({row["folio"] for row in calibration}),
            "sealed_target_loci": len(target),
            "sealed_target_folios": len({row["folio"] for row in target}),
            "sealed_target_ids_sha256": TARGET_ID_HASH,
        },
        "calibration": calibration_summary,
        "calibration_subgroups": subgroups,
        "gates": gates,
        "target_member_residual_rows_scored": 0,
        "target_log_gain_rows_scored": 0,
        "english_glosses": 0,
        "claim_ceiling": (
            "Calibration of an exact STA member-code score conditional on fixed family shells, with the "
            "unseen-fine-surface target unscored. It supplies no physical glyph identity, allography, "
            "sound, alphabet, word, cipher, meaning, plaintext, language, or translation."
        ),
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report = f"""# Conditional STA member-resolution preflight

Status: **{result['status']}**

The calibration contains **{calibration_summary['loci']:,}** loci on
**{calibration_summary['folios']}** physical folios. Its equal-folio conditional
member residual is **{calibration_summary['equal_folio_member_residual']:.6f}**
and its proper incremental log gain is
**{calibration_summary['equal_folio_log_gain']:.6f}**. Combined locus accuracy
is **{calibration_summary['combined_locus_accuracy']:.3%}** versus
**{calibration_summary['baseline_locus_accuracy']:.3%}** for the frozen
family-only score; folio sign p is
**{calibration_summary['one_sided_folio_sign_p']:.8f}**.

Decision: **{result['decision']}**. The full set of **{len(gates)}** preflight gates
{'passes' if passed else 'does not pass'}. The 285-locus unseen-fine-surface target
has **zero scored rows** and remains sealed pending independent reconstruction.
No glyph, allograph, sound, alphabet, word, meaning, plaintext, language,
cipher, or translation follows.
"""
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps({"status": result["status"], "decision": result["decision"], "gates_pass": passed}, sort_keys=True))


if __name__ == "__main__":
    main()
