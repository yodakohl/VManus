#!/usr/bin/env python3
"""Independent nonimporting reconstruction of member-resolution preflight."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import re
import struct
from collections import Counter, defaultdict
from pathlib import Path


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
PRODUCER = BASE / "run_source_member_resolution_preflight.py"
PRODUCTION = RESULTS / "source_member_resolution_preflight.json"
PRODUCTION_REPORT = RESULTS / "source_member_resolution_preflight_report.md"
VALIDATOR = Path(__file__).resolve()
OUT = RESULTS / "source_member_resolution_preflight_validation.json"
REPORT = RESULTS / "source_member_resolution_preflight_validation_report.md"

HASHES = {
    GROUPS: "a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225",
    SCAFFOLD_VALIDATION: "fcb6a53461b4f9df36f34161ed1d42087f4395988bea0d71f74a7dd635b68b76",
    EDGE: "2a4a246bf1d8de1f2bed76e4e790d44832e9c5ba85cc8d3ad6f2e832b035ea88",
    EDGE_VALIDATION: "0a87ffb2c23fdc6882887e5a854112d678cb6c1de1946407068462ce91fca712",
    CAPACITY: "5a4058ff814366509d9726e39c481739e7f1bc9c33dee5ec87ac3b96c3525769",
    CAPACITY_VALIDATION: "3143a7a69dff1fe4443361b292c581a51f1b6259d7d1e1d6192831232265132b",
    RULES: "7f37853510144fb3e2dc3ee9458d634f41e6d95bc1fbf1c4b8f479a53a021f81",
    SPEC: "f59e21dfaa2fdc326462da638d537d8d62cc6a80048da5511c106af3056521db",
    PRODUCER: "2cc6e4f9dbd39d8a426519918d1c5b09df37c189a469f859f7e482ca72017c44",
    PRODUCTION: "1619e18536db412f980ec4002e5b76da9f4454963d49441ae85326510b76a355",
    PRODUCTION_REPORT: "ce515feabc94692805a2b5f0f3e82acb9920b138872b3957f995a58fcb55cf64",
}
FAMILY_VOCAB = {"P1": 21, "P2": 462, "S1": 21, "S2": 462, "LEN": 8}
FAMILY_SCORE_HASH = "c27eaee78ec21c8f392157603c585cb44edaee8ad87d72363b9296cf05894b9f"
TARGET_ID_HASH = "f569e1a9cc4dd13f7339b6d3216fff3d0920ed69f0fbaaace8de1b578b19d225"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def folio(page: str) -> str:
    match = re.match(r"^(f[0-9]+)[rv]", page)
    if match is None:
        raise ValueError(page)
    return match.group(1)


def family_vector(surface: str) -> list[tuple[str, str]]:
    return [
        ("P1", surface[0]),
        ("P2", surface[:2]),
        ("S1", surface[-1]),
        ("S2", surface[-2:]),
        ("LEN", str(len(surface)) if len(surface) <= 7 else "8+"),
    ]


def fine_vector(codes: tuple[str, ...]) -> list[tuple[str, tuple[str, ...]]]:
    return [("P1", codes[:1]), ("P2", codes[:2]), ("S1", codes[-1:]), ("S2", codes[-2:])]


def log_sigmoid(value: float) -> float:
    return -math.log1p(math.exp(-value)) if value >= 0 else value - math.log1p(math.exp(value))


def sign_tail(positive: int, negative: int) -> float:
    return sum(math.comb(positive + negative, k) for k in range(positive, positive + negative + 1)) / 2 ** (positive + negative)


def avg(values: list[float]) -> float:
    return sum(values) / len(values)


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing to overwrite validation artifacts")
    checks = 0

    def require(condition: bool, message: str) -> None:
        nonlocal checks
        checks += 1
        if not condition:
            raise AssertionError(message)

    def equivalent(left, right) -> bool:
        if isinstance(left, bool) or isinstance(right, bool):
            return left is right
        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            return math.isclose(float(left), float(right), rel_tol=0.0, abs_tol=1e-12)
        if isinstance(left, dict) and isinstance(right, dict):
            return left.keys() == right.keys() and all(equivalent(left[key], right[key]) for key in left)
        if isinstance(left, list) and isinstance(right, list):
            return len(left) == len(right) and all(equivalent(a, b) for a, b in zip(left, right))
        return left == right

    for path, expected in HASHES.items():
        require(sha(path) == expected, f"hash mismatch {path.name}")
    require(json.loads(CAPACITY.read_text())["decision"] == "GO_PREREGISTER_INCREMENTAL_MEMBER_TEST", "bad capacity")
    require(json.loads(CAPACITY_VALIDATION.read_text())["status"] == "PASS_INDEPENDENT_SCORE_BLIND_CAPACITY_RECONSTRUCTION", "bad capacity validation")

    inventory: dict[str, list[str]] = defaultdict(list)
    for raw in RULES.read_text(encoding="utf-8").splitlines():
        if not raw or raw.startswith(("#", "<")):
            continue
        code = raw.split(maxsplit=1)[0]
        require(re.fullmatch(r"[A-Z][A-Za-z0-9]", code) is not None, "bad official code")
        inventory[code[0]].append(code)
    require(len(inventory) == 24, "official family count")
    require(sum(len(values) for values in inventory.values()) == 242, "official code count")

    with GROUPS.open(encoding="utf-8", newline="") as handle:
        raw_rows = list(csv.DictReader(handle, delimiter="\t"))
    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in raw_rows:
        if row["strict_zero_alternative"] == "1":
            groups[row["locus"]].append(row)
    panel = []
    for locus in sorted(groups):
        sequence = sorted(groups[locus], key=lambda row: int(row["consensus_group_index"]))
        require(len(sequence) == int(sequence[0]["consensus_group_count"]), "group count")
        require([int(row["consensus_group_index"]) for row in sequence] == list(range(1, len(sequence) + 1)), "group order")
        if len(sequence) < 2:
            continue
        endpoints = []
        for role, row in (("FIRST", sequence[0]), ("LAST", sequence[-1])):
            codes = tuple(row["zl_sta_codes"].split())
            require("".join(code[0] for code in codes) == row["family_surface"], "family/code mismatch")
            endpoints.append({
                "role": role,
                "family": row["family_surface"],
                "codes": codes,
                "exact": len({row["zl_sta_codes"], row["it_sta_codes"], row["rf_sta_codes"]}) == 1,
            })
        panel.append({
            "locus": locus,
            "folio": folio(sequence[0]["page"]),
            "grammar_scope": sequence[0]["grammar_scope"],
            "currier": sequence[0]["currier"],
            "endpoints": endpoints,
        })
    require(len(panel) == 2873, "panel count")

    family_count = Counter()
    family_fold = Counter()
    family_total = Counter()
    family_fold_total = Counter()
    fine_count = Counter()
    fine_fold = Counter()
    shell_count = Counter()
    shell_fold = Counter()
    family_surface_occ = Counter()
    family_surface_fold = Counter()
    member_surface_occ = Counter()
    member_surface_fold = Counter()
    for locus in panel:
        held = locus["folio"]
        for endpoint in locus["endpoints"]:
            role = endpoint["role"]
            surface = endpoint["family"]
            family_surface_occ[surface] += 1
            family_surface_fold[(held, surface)] += 1
            for namespace, value in family_vector(surface):
                family_count[(role, namespace, value)] += 1
                family_fold[(held, role, namespace, value)] += 1
                family_total[(role, namespace)] += 1
                family_fold_total[(held, role, namespace)] += 1
            if not endpoint["exact"]:
                continue
            member_string = " ".join(endpoint["codes"])
            member_surface_occ[(surface, member_string)] += 1
            member_surface_fold[(held, surface, member_string)] += 1
            for namespace, value in fine_vector(endpoint["codes"]):
                shell = "".join(code[0] for code in value)
                fine_count[(role, namespace, value)] += 1
                fine_fold[(held, role, namespace, value)] += 1
                shell_count[(role, namespace, shell)] += 1
                shell_fold[(held, role, namespace, shell)] += 1

    folds = sorted({row["folio"] for row in panel})
    surfaces = sorted(family_surface_occ)
    family_scores = {}
    family_payload = bytearray()
    for held in folds:
        for surface in surfaces:
            components = {}
            for namespace, value in family_vector(surface):
                logs = {}
                for role in ("FIRST", "LAST"):
                    n = family_count[(role, namespace, value)] - family_fold[(held, role, namespace, value)]
                    d = family_total[(role, namespace)] - family_fold_total[(held, role, namespace)]
                    logs[role] = math.log((n + 0.5) / (d + 0.5 * FAMILY_VOCAB[namespace]))
                components[namespace] = logs["FIRST"] - logs["LAST"]
            score = sum(components.values())
            family_scores[(held, surface)] = score
            family_payload += held.encode() + b"\0" + surface.encode() + b"\0" + struct.pack("<dd", score, components["LEN"])
    reconstructed_family_hash = hashlib.sha256(family_payload).hexdigest()
    require(reconstructed_family_hash == FAMILY_SCORE_HASH, "family table hash")

    all_values: dict[str, set[tuple[str, ...]]] = defaultdict(set)
    for role, namespace, value in fine_count:
        all_values[namespace].add(value)
    member_scores = {}
    member_payload = bytearray()
    swap_max = 0.0
    mutation_discrepancies = 0
    for held in folds:
        for namespace in ("P1", "P2", "S1", "S2"):
            for value in sorted(all_values[namespace]):
                shell = "".join(code[0] for code in value)
                k = math.prod(len(inventory[family]) for family in shell)
                logs = {}
                for role in ("FIRST", "LAST"):
                    n = fine_count[(role, namespace, value)] - fine_fold[(held, role, namespace, value)]
                    d = shell_count[(role, namespace, shell)] - shell_fold[(held, role, namespace, shell)]
                    logs[role] = math.log((n + 0.5) / (d + 0.5 * k))
                    opposite = "LAST" if role == "FIRST" else "FIRST"
                    mutated = fine_count[(role, namespace, value)] - fine_fold[(held, role, namespace, value)] + fine_fold[(held, opposite, namespace, value)] - fine_fold[(held, opposite, namespace, value)]
                    mutation_discrepancies += mutated != n
                coefficient = logs["FIRST"] - logs["LAST"]
                swapped = logs["LAST"] - logs["FIRST"]
                swap_max = max(swap_max, abs(coefficient + swapped))
                member_scores[(held, namespace, value)] = coefficient
                member_payload += held.encode() + b"\0" + namespace.encode() + b"\0" + shell.encode() + b"\0" + " ".join(value).encode() + b"\0" + struct.pack("<d", coefficient)
    member_hash = hashlib.sha256(member_payload).hexdigest()
    require(mutation_discrepancies == 0, "held mutation")
    require(swap_max == 0.0, "role swap")

    calibration = []
    target = []
    for locus in panel:
        held = locus["folio"]
        endpoints = locus["endpoints"]
        if not all(endpoint["exact"] for endpoint in endpoints):
            continue
        if not all(family_surface_occ[endpoint["family"]] > family_surface_fold[(held, endpoint["family"])] for endpoint in endpoints):
            continue
        support = True
        for endpoint in endpoints:
            for namespace, value in fine_vector(endpoint["codes"]):
                for role in ("FIRST", "LAST"):
                    if fine_count[(role, namespace, value)] <= fine_fold[(held, role, namespace, value)]:
                        support = False
        if not support:
            continue
        seen = [
            member_surface_occ[(endpoint["family"], " ".join(endpoint["codes"]))]
            > member_surface_fold[(held, endpoint["family"], " ".join(endpoint["codes"]))]
            for endpoint in endpoints
        ]
        (calibration if all(seen) else target).append(locus)
    require(len(calibration) == 783, "calibration loci")
    require(len({row["folio"] for row in calibration}) == 97, "calibration folios")
    require(len(target) == 285, "target loci")
    require(len({row["folio"] for row in target}) == 81, "target folios")
    target_hash = hashlib.sha256("\n".join(row["locus"] for row in target).encode()).hexdigest()
    require(target_hash == TARGET_ID_HASH, "target digest")

    def summarize(items: list[dict]) -> dict:
        detail = []
        vector = bytearray()
        for locus in items:
            held = locus["folio"]
            pair = []
            for endpoint in locus["endpoints"]:
                member = sum(member_scores[(held, namespace, value)] for namespace, value in fine_vector(endpoint["codes"]))
                pair.append((family_scores[(held, endpoint["family"])], member))
            baseline = pair[0][0] - pair[1][0]
            residual = pair[0][1] - pair[1][1]
            combined = baseline + residual
            gain = log_sigmoid(combined) - log_sigmoid(baseline)
            require(all(math.isfinite(x) for x in (baseline, residual, combined, gain)), "finite score")
            detail.append((locus["locus"], held, baseline, residual, combined, gain))
            vector += locus["locus"].encode() + b"\0" + held.encode() + b"\0" + struct.pack("<dddd", baseline, residual, combined, gain)
        by_fold: dict[str, list[tuple]] = defaultdict(list)
        for row in detail:
            by_fold[row[1]].append(row)
        fold_details = []
        for held in sorted(by_fold):
            rows = by_fold[held]
            fold_details.append({"folio": held, "loci": len(rows), "member_residual": avg([row[3] for row in rows]), "log_gain": avg([row[5] for row in rows])})
        residuals = [row[3] for row in detail]
        fold_residuals = [row["member_residual"] for row in fold_details]
        fold_gains = [row["log_gain"] for row in fold_details]
        pos = sum(x > 0 for x in fold_residuals)
        neg = sum(x < 0 for x in fold_residuals)
        loo_r = [avg(fold_residuals[:i] + fold_residuals[i + 1:]) for i in range(len(fold_residuals))]
        loo_g = [avg(fold_gains[:i] + fold_gains[i + 1:]) for i in range(len(fold_gains))]
        return {
            "loci": len(detail), "folios": len(fold_details),
            "equal_folio_member_residual": avg(fold_residuals), "equal_folio_log_gain": avg(fold_gains),
            "positive_folios": pos, "negative_folios": neg, "tied_folios": len(fold_residuals) - pos - neg,
            "one_sided_folio_sign_p": sign_tail(pos, neg),
            "positive_loci": sum(x > 0 for x in residuals), "negative_loci": sum(x < 0 for x in residuals), "tied_loci": sum(x == 0 for x in residuals),
            "nonzero_locus_positive_fraction": sum(x > 0 for x in residuals) / sum(x != 0 for x in residuals),
            "baseline_locus_accuracy": sum(row[2] > 0 for row in detail) / len(detail),
            "combined_locus_accuracy": sum(row[4] > 0 for row in detail) / len(detail),
            "minimum_leave_one_folio_out_member_residual": min(loo_r), "minimum_leave_one_folio_out_log_gain": min(loo_g),
            "max_absolute_residual_contribution_fraction": max(map(abs, fold_residuals)) / sum(map(abs, fold_residuals)),
            "max_absolute_gain_contribution_fraction": max(map(abs, fold_gains)) / sum(map(abs, fold_gains)),
            "locus_vector_sha256": hashlib.sha256(vector).hexdigest(), "folio_details": fold_details,
        }

    main_summary = summarize(calibration)
    subgroups = {
        "confirmed_prose": summarize([row for row in calibration if row["grammar_scope"] == "CONFIRMED_PROSE"]),
        "currier_A": summarize([row for row in calibration if row["currier"] == "A"]),
        "currier_B": summarize([row for row in calibration if row["currier"] == "B"]),
    }
    actual = json.loads(PRODUCTION.read_text(encoding="utf-8"))
    require(actual["inputs"] == {
        path.name: sha(path)
        for path in (
            GROUPS, SCAFFOLD_VALIDATION, EDGE, EDGE_VALIDATION, CAPACITY,
            CAPACITY_VALIDATION, RULES, SPEC, PRODUCER,
        )
    }, "production input bindings")
    require(actual["status"] == "STOP_MEMBER_RESOLUTION_PREFLIGHT_TARGET_UNSCORED", "status")
    require(actual["decision"] == "STOP_BEFORE_MEMBER_TARGET", "decision")
    require(equivalent(actual["calibration"], main_summary), "calibration summary")
    require(equivalent(actual["calibration_subgroups"], subgroups), "subgroup summaries")
    require(actual["calibration"]["locus_vector_sha256"] == main_summary["locus_vector_sha256"], "calibration vector hash")
    for subgroup in subgroups:
        require(actual["calibration_subgroups"][subgroup]["locus_vector_sha256"] == subgroups[subgroup]["locus_vector_sha256"], f"{subgroup} vector hash")
    require(actual["model"]["member_score_table_sha256"] == member_hash, "member table hash")
    require(actual["model"]["member_score_cells"] == len(member_scores), "member cell count")
    require(actual["model"]["official_member_counts"] == {key: len(values) for key, values in sorted(inventory.items())}, "official counts")
    require(actual["target_member_residual_rows_scored"] == 0, "target residual opened")
    require(actual["target_log_gain_rows_scored"] == 0, "target gain opened")
    require(actual["english_glosses"] == 0, "English gloss")
    false_gates = sorted(key for key, value in actual["gates"].items() if not value)
    require(false_gates == ["currier_A_positive_at_least_45_folios"], "wrong failed gate")
    require(main_summary["equal_folio_member_residual"] > 0, "calibration residual direction")
    require(main_summary["equal_folio_log_gain"] > 0, "calibration gain direction")
    require(subgroups["currier_A"]["equal_folio_log_gain"] < 0, "Currier A failure direction")
    require("zero scored rows" in PRODUCTION_REPORT.read_text(encoding="utf-8"), "report target isolation")

    validation = {
        "experiment": "SOURCE_MEMBER_RESOLUTION_PREFLIGHT_VALIDATION",
        "status": "PASS_INDEPENDENT_PREFLIGHT_STOP_RECONSTRUCTION",
        "checks": checks,
        "validator_sha256": sha(VALIDATOR),
        "producer_sha256": sha(PRODUCER),
        "production_sha256": sha(PRODUCTION),
        "production_report_sha256": sha(PRODUCTION_REPORT),
        "family_score_table_sha256": reconstructed_family_hash,
        "member_score_table_sha256": member_hash,
        "calibration_locus_vector_sha256": main_summary["locus_vector_sha256"],
        "failed_gates": false_gates,
        "target_rows_scored": 0,
        "production_module_imported": False,
        "decision": actual["decision"],
        "claim_ceiling": actual["claim_ceiling"],
    }
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report = f"""# Conditional STA member-resolution preflight validation

Status: **{validation['status']}**

The nonimporting reconstruction passed **{checks:,}** checks and exactly
reproduced the family and member score-table hashes, 783-locus calibration,
three subgroup summaries, target-ID digest, controls, and single failed gate.

The calibration is strong in aggregate, but Currier A incremental log gain is
**{subgroups['currier_A']['equal_folio_log_gain']:.6f}**, so the frozen gate
fails. Decision: **{actual['decision']}**. The 285-locus target has zero scored
rows. No retuning or target run is authorized, and no glyph, sound, alphabet,
meaning, plaintext, language, cipher, or translation follows.
"""
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps({"status": validation["status"], "checks": checks, "failed_gates": false_gates, "decision": actual["decision"]}, sort_keys=True))


if __name__ == "__main__":
    main()
