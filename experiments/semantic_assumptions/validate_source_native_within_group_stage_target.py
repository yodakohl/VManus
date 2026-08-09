#!/usr/bin/env python3
"""Production-free validation of the complete within-group stage target."""

from __future__ import annotations

import os

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

import csv
import hashlib
import json
import math
import re
from collections import Counter
from copy import deepcopy
from pathlib import Path

import validate_source_native_within_group_stage_preflight_v2 as clean


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
PANEL_PATH = RESULTS / "source_native_within_group_stage_masked.tsv"
CAPACITY_VALIDATION = RESULTS / "source_native_within_group_stage_capacity_validation.json"
PREFLIGHT_VALIDATION = RESULTS / "source_native_within_group_stage_preflight_v2_validation.json"
CLEAN_VALIDATOR = BASE / "validate_source_native_within_group_stage_preflight_v2.py"
TARGET_SOURCE = RESULTS / "source_sta_family_consensus_groups.tsv"
TARGET_SOURCE_VALIDATION = RESULTS / "source_sta_family_consensus_validation.json"
SPEC = BASE / "SOURCE_NATIVE_WITHIN_GROUP_STAGE_TARGET_SPEC.md"
RUNNER = BASE / "run_source_native_within_group_stage_target.py"
TARGET_RESULT = RESULTS / "source_native_within_group_stage_target.json"
TARGET_REPORT = RESULTS / "source_native_within_group_stage_target_report.md"
OUT = RESULTS / "source_native_within_group_stage_target_validation.json"
REPORT = RESULTS / "source_native_within_group_stage_target_validation_report.md"
FROZEN = {
    PANEL_PATH: "16d7395ae0410c8fc72b5e5462d6d425cd3a2685e7ea70eee0677bd936106ae5",
    CAPACITY_VALIDATION: "2a95ce3183b72540f39a8ef0f68129d1f7ccf2e688683a9f2989360f84c20007",
    PREFLIGHT_VALIDATION: "6d6dcd56ae68e06f42977d1ca7e754bbddd2235e9fe1d19962f1bde731db4533",
    CLEAN_VALIDATOR: "9d33a815fc10b75aa02a57568207691cdb33daf1165c5060c463cb811f8ed30a",
    TARGET_SOURCE: "a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225",
    TARGET_SOURCE_VALIDATION: "fcb6a53461b4f9df36f34161ed1d42087f4395988bea0d71f74a7dd635b68b76",
    SPEC: "3d97cfebbaad12d48d45b3a8081b506989e9dda1c3edb7423ee04023d42740b1",
    RUNNER: "7a40e055cccd0c72ec80f12f642d47ff5c424d11e66eb279d6728867769348fe",
    TARGET_RESULT: "79c1f7b63b5004283f635c999757368c9dfc81c8fa065aff287b44bf7c877cb6",
    TARGET_REPORT: "8a5c3f2f0d06797276eac01a7a3816862c4a320c59f0fc4037772347aa9fb531",
}
SOURCE_FIELDS = (
    "consensus_group_id", "locus", "page", "section", "currier", "hand", "code", "kind", "grammar_scope",
    "strict_zero_alternative", "consensus_group_index", "consensus_group_count", "start_symbol_1based",
    "end_symbol_1based", "symbol_count", "family_surface", "zl_sta_codes", "it_sta_codes", "rf_sta_codes",
    "left_boundary_profile", "right_boundary_profile",
)
ALPHABET = tuple("ABCDEFGHJKLMNPQRSTUVWXYZ")
INDEX = {value: index for index, value in enumerate(ALPHABET)}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def split_for(folio: str) -> str:
    value = int.from_bytes(hashlib.sha256(f"SNWG001|{folio}".encode()).digest()[:8], "little") % 5
    return "TEST" if value == 0 else ("CAL" if value == 1 else "TRAIN")


def numeric_max(left, right) -> float:
    if isinstance(left, dict):
        if set(left) != set(right):
            return math.inf
        return max((numeric_max(left[key], right[key]) for key in left), default=0.0)
    if isinstance(left, list):
        if len(left) != len(right):
            return math.inf
        return max((numeric_max(a, b) for a, b in zip(left, right)), default=0.0)
    if isinstance(left, (int, float)) and not isinstance(left, bool):
        return abs(float(left) - float(right))
    return 0.0 if left == right else math.inf


def aggregate(result: dict) -> dict:
    return {
        "selected_model": result["selected_model"], "best_fixed_model": result["best_fixed_model"],
        "candidate_diagnostics": result["candidate_diagnostics"], "test_groups": result["test_groups"],
        "test_symbols": result["test_symbols"], "gain_equal_symbol": result["gain_equal_symbol"],
        "gain_vs_fixed_equal_symbol": result["gain_vs_fixed_equal_symbol"], "gain": result["gain"],
        "gain_vs_fixed": result["gain_vs_fixed"], "unseen": result["unseen"], "currier": result["currier"],
        "POSITIONAL_PASS": clean.positional_pass(result), "LATENT_STAGE_PASS": clean.latent_pass(result),
    }


def principal(result: dict) -> dict:
    return {
        "test_groups": result["test_groups"], "test_symbols": result["test_symbols"],
        "gain_equal_symbol": result["gain_equal_symbol"], "gain": result["gain"], "unseen": result["unseen"],
        "currier": {currier: {"gain": result["currier"][currier]["gain"]} for currier in ("A", "B")},
    }


def eligible_source_ids(rows: list[dict]) -> set[str]:
    output = set()
    for row in rows:
        if row["strict_zero_alternative"] == "1" and row["grammar_scope"] == "CONFIRMED_PROSE" and re.match(r"f\d+", row["page"]):
            output.add(row["consensus_group_id"])
    return output


def join(panel: clean.Panel, source_rows: list[dict]) -> tuple[list[tuple[int, ...]], Counter]:
    if len(source_rows) != 26184:
        raise ValueError("source rows")
    source_by_id = {row["consensus_group_id"]: row for row in source_rows}
    if len(source_by_id) != len(source_rows):
        raise ValueError("duplicate source ID")
    panel_ids = {row["unit_id"] for row in panel.rows}
    if eligible_source_ids(source_rows) != panel_ids or len(panel_ids) != 21899:
        raise ValueError("eligible ID set")
    sequences, counts = [], Counter()
    for masked in panel.rows:
        source = source_by_id.get(masked["unit_id"])
        if source is None or source["consensus_group_id"] != masked["unit_id"]:
            raise ValueError("join ID")
        match = re.match(r"f\d+", source["page"])
        if match is None or source["strict_zero_alternative"] != "1" or source["grammar_scope"] != "CONFIRMED_PROSE":
            raise ValueError("join scope")
        surface = source["family_surface"]
        if len(surface) != int(masked["symbol_count"]) or int(source["symbol_count"]) != len(surface):
            raise ValueError("length")
        if not surface or any(symbol not in INDEX for symbol in surface):
            raise ValueError("symbol")
        exact = {
            "locus": source["locus"], "page": source["page"], "physical_folio": match.group(),
            "section": source["section"], "currier": source["currier"], "hand": source["hand"],
            "kind": source["kind"], "symbol_count": str(len(surface)), "split": split_for(match.group()),
        }
        if any(masked[key] != value for key, value in exact.items()):
            raise ValueError("metadata")
        sequences.append(tuple(INDEX[symbol] for symbol in surface))
        counts.update(surface)
    return sequences, counts


def expected_report(result: dict) -> str:
    forward, reversed_result = result["forward"], result["reversed"]
    positional = result["gates"]["POSITIONAL_TARGET_PASS"]
    latent = result["gates"]["LATENT_STAGE_TARGET_PASS"]
    return f"""# Complete source-native within-group stage target

Status: **{result['status']}**

The one authorized join read **{result['source_rows_accessed']:,}** source rows and matched
all **{result['joined_target_sequences']:,}** frozen complete prose groups. The forward model
selects **{forward['selected_model']}** against **{forward['best_fixed_model']}**;
the reversed robustness view selects **{reversed_result['selected_model']}**
against **{reversed_result['best_fixed_model']}**.

Forward/reversed equal-folio selected-minus-K1 gains are
**{forward['gain']['effect_equal_folio']:+.6f}** and
**{reversed_result['gain']['effect_equal_folio']:+.6f}** nat/symbol. Their
selected-minus-best-FIXED gains are
**{forward['gain_vs_fixed']['effect_equal_folio']:+.6f}** and
**{reversed_result['gain_vs_fixed']['effect_equal_folio']:+.6f}**.
`POSITIONAL_TARGET_PASS` is **{str(positional).lower()}** and
`LATENT_STAGE_TARGET_PASS` is **{str(latent).lower()}**.

Decision: **{result['decision']}**. No event-level sequence or path is stored. Even a
pass establishes only neutral structural stages, never a prefix, root, suffix,
sound, word, part of speech, language, cipher operation, meaning, plaintext,
or translation.
"""


def rejects(panel: clean.Panel, rows: list[dict], mutation) -> bool:
    altered = deepcopy(rows)
    mutation(altered)
    try:
        join(panel, altered)
    except ValueError:
        return True
    return False


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing to overwrite stage target validation")
    failures, checks = [], 0

    def check(condition: bool, name: str) -> None:
        nonlocal checks
        checks += 1
        if not condition:
            failures.append(name)

    for path, expected in FROZEN.items():
        check(sha(path) == expected, f"hash:{path.name}")
    check(json.loads(CAPACITY_VALIDATION.read_text())["status"] == "PASS_INDEPENDENT_SCORE_BLIND_STAGE_CAPACITY_RECONSTRUCTION", "capacity status")
    check(json.loads(PREFLIGHT_VALIDATION.read_text())["status"] == "PASS_INDEPENDENT_WITHIN_GROUP_STAGE_PREFLIGHT_V2_RECONSTRUCTION", "preflight status")
    check(json.loads(TARGET_SOURCE_VALIDATION.read_text())["status"] == "PASS_INDEPENDENT_EXACT_FAMILY_GRAMMAR_SCAFFOLD_RECONSTRUCTION", "source status")

    with TARGET_SOURCE.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        check(tuple(reader.fieldnames or ()) == SOURCE_FIELDS, "source schema")
        source_rows = list(reader)
    panel = clean.load_panel()
    sequences, family_counts = join(panel, source_rows)
    check(len(sequences) == 21899, "joined groups")
    check(sum(map(len, sequences)) == sum(family_counts.values()), "symbol count")
    check(Counter(row["split"] for row in panel.rows) == {"TRAIN": 10753, "CAL": 5516, "TEST": 5630}, "split counts")
    check(len(set(panel.folios)) == 94, "folios")

    forward_full = clean.evaluate(panel, sequences)
    reversed_full = clean.evaluate(panel, [tuple(reversed(sequence)) for sequence in sequences])
    forward, reversed_result = aggregate(forward_full), aggregate(reversed_full)
    same_latent = forward["selected_model"] == reversed_result["selected_model"] and forward["selected_model"].startswith("LATENT_")
    principal_delta = numeric_max(principal(forward_full), principal(reversed_full)) if same_latent else None
    positional_target_pass = forward["POSITIONAL_PASS"] and reversed_result["POSITIONAL_PASS"]
    latent_target_pass = forward["LATENT_STAGE_PASS"] and reversed_result["LATENT_STAGE_PASS"] and same_latent and principal_delta is not None and principal_delta <= 1e-10
    if latent_target_pass:
        status, decision = "CONFIRM_COMPLETE_SOURCE_NATIVE_LATENT_STAGE_GRAMMAR", "AUTHORIZE_NEUTRAL_STAGE_ATLAS"
    elif positional_target_pass:
        status, decision = "CONFIRM_COMPLETE_SOURCE_NATIVE_POSITIONAL_STRUCTURE_ONLY", "RETAIN_POSITIONAL_STRUCTURE_WITHOUT_UNIQUE_STAGE_ATLAS"
    else:
        status, decision = "NONCONFIRM_COMPLETE_SOURCE_NATIVE_WITHIN_GROUP_STAGE_MODEL", "CLOSE_EXACT_WITHIN_GROUP_STAGE_MODEL_WITHOUT_RETUNING"
    gates = {
        "exact_26184_source_rows": len(source_rows) == 26184,
        "exact_21899_joined_groups": len(sequences) == 21899,
        "exact_split_counts": Counter(row["split"] for row in panel.rows) == {"TRAIN": 10753, "CAL": 5516, "TEST": 5630},
        "exact_94_folios": len(set(panel.folios)) == 94,
        "complete_eligible_id_set": eligible_source_ids(source_rows) == {row["unit_id"] for row in panel.rows},
        "forward_POSITIONAL_PASS": forward["POSITIONAL_PASS"],
        "reversed_POSITIONAL_PASS": reversed_result["POSITIONAL_PASS"],
        "forward_LATENT_STAGE_PASS": forward["LATENT_STAGE_PASS"],
        "reversed_LATENT_STAGE_PASS": reversed_result["LATENT_STAGE_PASS"],
        "same_selected_latent_model": same_latent,
        "latent_principal_reversal_delta_at_most_1e_10": principal_delta is not None and principal_delta <= 1e-10,
        "POSITIONAL_TARGET_PASS": positional_target_pass,
        "LATENT_STAGE_TARGET_PASS": latent_target_pass,
    }
    stored = json.loads(TARGET_RESULT.read_text())
    check(stored["status"] == status and stored["decision"] == decision, "decision")
    check(numeric_max(stored["forward"], forward) <= 1e-12, "forward reconstruction")
    check(numeric_max(stored["reversed"], reversed_result) <= 1e-12, "reversed reconstruction")
    check(stored["gates"] == gates, "gates")
    check(stored["latent_principal_reversal_max_abs"] == principal_delta, "principal delta")
    check(stored["family_counts"] == {family: family_counts[family] for family in ALPHABET}, "family counts")
    check(stored["source_rows_accessed"] == 26184 and stored["joined_target_sequences"] == 21899, "access counts")
    check(stored["target_source_opened"] is True and stored["target_sequences_accessed"] == 21899 and stored["target_evaluations_computed"] == 2, "target access")
    check(stored["event_level_sequences_stored"] == 0 and stored["event_level_stage_paths_stored"] == 0 and stored["english_glosses"] == 0, "output ceiling")
    check(TARGET_REPORT.read_text() == expected_report(stored), "report bytes")
    expected_inputs = {
        "source_native_within_group_stage_masked.tsv": sha(PANEL_PATH),
        "source_native_within_group_stage_capacity_validation.json": sha(CAPACITY_VALIDATION),
        "source_native_within_group_stage_core.py": "ce1cd0854426b34e8b3e9ba0e6057352f9a5b99737e9e148e791e02979bc65dc",
        "SOURCE_NATIVE_WITHIN_GROUP_STAGE_TEST_SPEC.md": "e3758d2a4c8d5d306b38602e8a1663ebc42a78db2abecd5905fe191a5d983d47",
        "SOURCE_NATIVE_WITHIN_GROUP_STAGE_PREFLIGHT_V2_AMENDMENT.md": "b0b42cc092c2b97ac919d5ecc471d890a09a7c5e0b21fe10548efb543c02bc80",
        "source_native_within_group_stage_preflight_v2.json": "a619c087692b27dd3dac062412238388d717fcfe7c5f213fbfa28b0fe0c586c2",
        "source_native_within_group_stage_preflight_v2_validation.json": sha(PREFLIGHT_VALIDATION),
        "source_sta_family_consensus_validation.json": sha(TARGET_SOURCE_VALIDATION),
        "SOURCE_NATIVE_WITHIN_GROUP_STAGE_TARGET_SPEC.md": sha(SPEC),
        "source_sta_family_consensus_groups.tsv": sha(TARGET_SOURCE),
        "run_source_native_within_group_stage_target.py": sha(RUNNER),
    }
    check(stored["inputs"] == expected_inputs, "stored input bindings")

    panel_id = panel.rows[0]["unit_id"]
    source_index = next(i for i, row in enumerate(source_rows) if row["consensus_group_id"] == panel_id)
    check(rejects(panel, source_rows, lambda rows: rows.pop(source_index)), "missing-row mutation")
    check(rejects(panel, source_rows, lambda rows: rows.append(dict(rows[source_index]))), "duplicate-row mutation")
    check(rejects(panel, source_rows, lambda rows: rows[source_index].__setitem__("page", "f999r")), "metadata mutation")
    check(rejects(panel, source_rows, lambda rows: rows[source_index].__setitem__("family_surface", "I" + rows[source_index]["family_surface"][1:])), "symbol mutation")
    if failures:
        raise SystemExit("validation failed: " + failures[0])
    result = {
        "experiment": "SOURCE_NATIVE_WITHIN_GROUP_STAGE_TARGET_VALIDATION",
        "status": "PASS_PRODUCTION_FREE_WITHIN_GROUP_POSITIONAL_CONFIRMATION_RECONSTRUCTION",
        "checks": checks,
        "failures": [],
        "reconstructed_status": status,
        "reconstructed_decision": decision,
        "selected_models": {"forward": forward["selected_model"], "reversed": reversed_result["selected_model"]},
        "forward_equal_folio_gain": forward["gain"]["effect_equal_folio"],
        "reversed_equal_folio_gain": reversed_result["gain"]["effect_equal_folio"],
        "forward_positive_folios": forward["gain"]["positive_folios"],
        "reversed_positive_folios": reversed_result["gain"]["positive_folios"],
        "target_rows_reconstructed": 21899,
        "event_level_sequences_stored": 0,
        "english_glosses": 0,
        "inputs": {path.name: sha(path) for path in FROZEN},
        "claim_ceiling": "Production-free confirmation of a complete source-native five-position structure only; no unique latent stages, morphology, sound, word, language, meaning, plaintext, or translation follows.",
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    REPORT.write_text(f"""# Complete within-group stage target validation

Status: **{result['status']}**

The prior production-free target-free implementation independently rejoined
all **21,899** target groups and reconstructed both target evaluations in
**{checks} checks**. Forward and reversed runs both select **FIXED_5**, with
equal-folio gains **{forward['gain']['effect_equal_folio']:+.6f}** and
**{reversed_result['gain']['effect_equal_folio']:+.6f}** and **24/24** positive
held folios in each direction. Every stored aggregate, gate, decision, binding,
and report byte matches; four join mutations reject.

This validates complete source-native five-position structure only. The latent
stage gate failed, and no morphology, sound, word, language, meaning, plaintext,
or translation follows.
""")
    print(json.dumps({"status": result["status"], "checks": checks, "selected": result["selected_models"]}, sort_keys=True))


if __name__ == "__main__":
    main()
