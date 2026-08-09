#!/usr/bin/env python3
"""Execute the single frozen complete within-group stage target."""

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
import tempfile
from collections import Counter
from pathlib import Path

from source_native_within_group_stage_core import INDEX, evaluate, latent_pass, load_panel, positional_pass


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
PANEL_PATH = RESULTS / "source_native_within_group_stage_masked.tsv"
CAPACITY_VALIDATION = RESULTS / "source_native_within_group_stage_capacity_validation.json"
CORE = BASE / "source_native_within_group_stage_core.py"
TEST_SPEC = BASE / "SOURCE_NATIVE_WITHIN_GROUP_STAGE_TEST_SPEC.md"
AMENDMENT = BASE / "SOURCE_NATIVE_WITHIN_GROUP_STAGE_PREFLIGHT_V2_AMENDMENT.md"
PREFLIGHT = RESULTS / "source_native_within_group_stage_preflight_v2.json"
PREFLIGHT_VALIDATION = RESULTS / "source_native_within_group_stage_preflight_v2_validation.json"
TARGET_SOURCE = RESULTS / "source_sta_family_consensus_groups.tsv"
TARGET_SOURCE_VALIDATION = RESULTS / "source_sta_family_consensus_validation.json"
SPEC = BASE / "SOURCE_NATIVE_WITHIN_GROUP_STAGE_TARGET_SPEC.md"
RUNNER = Path(__file__).resolve()
OUT = RESULTS / "source_native_within_group_stage_target.json"
REPORT = RESULTS / "source_native_within_group_stage_target_report.md"
SAFE_FROZEN = {
    PANEL_PATH: "16d7395ae0410c8fc72b5e5462d6d425cd3a2685e7ea70eee0677bd936106ae5",
    CAPACITY_VALIDATION: "2a95ce3183b72540f39a8ef0f68129d1f7ccf2e688683a9f2989360f84c20007",
    CORE: "ce1cd0854426b34e8b3e9ba0e6057352f9a5b99737e9e148e791e02979bc65dc",
    TEST_SPEC: "e3758d2a4c8d5d306b38602e8a1663ebc42a78db2abecd5905fe191a5d983d47",
    AMENDMENT: "b0b42cc092c2b97ac919d5ecc471d890a09a7c5e0b21fe10548efb543c02bc80",
    PREFLIGHT: "a619c087692b27dd3dac062412238388d717fcfe7c5f213fbfa28b0fe0c586c2",
    PREFLIGHT_VALIDATION: "6d6dcd56ae68e06f42977d1ca7e754bbddd2235e9fe1d19962f1bde731db4533",
    TARGET_SOURCE_VALIDATION: "fcb6a53461b4f9df36f34161ed1d42087f4395988bea0d71f74a7dd635b68b76",
    SPEC: "3d97cfebbaad12d48d45b3a8081b506989e9dda1c3edb7423ee04023d42740b1",
}
TARGET_HASH = "a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225"
SOURCE_FIELDS = (
    "consensus_group_id", "locus", "page", "section", "currier", "hand", "code", "kind", "grammar_scope",
    "strict_zero_alternative", "consensus_group_index", "consensus_group_count", "start_symbol_1based",
    "end_symbol_1based", "symbol_count", "family_surface", "zl_sta_codes", "it_sta_codes", "rf_sta_codes",
    "left_boundary_profile", "right_boundary_profile",
)


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


def principal_gain(result: dict) -> dict:
    return {
        "test_groups": result["test_groups"],
        "test_symbols": result["test_symbols"],
        "gain_equal_symbol": result["gain_equal_symbol"],
        "gain": result["gain"],
        "unseen": result["unseen"],
        "currier": {currier: {"gain": result["currier"][currier]["gain"]} for currier in ("A", "B")},
    }


def aggregate(result: dict) -> dict:
    return {
        "selected_model": result["selected_model"],
        "best_fixed_model": result["best_fixed_model"],
        "candidate_diagnostics": result["candidate_diagnostics"],
        "test_groups": result["test_groups"],
        "test_symbols": result["test_symbols"],
        "gain_equal_symbol": result["gain_equal_symbol"],
        "gain_vs_fixed_equal_symbol": result["gain_vs_fixed_equal_symbol"],
        "gain": result["gain"],
        "gain_vs_fixed": result["gain_vs_fixed"],
        "unseen": result["unseen"],
        "currier": result["currier"],
        "POSITIONAL_PASS": positional_pass(result),
        "LATENT_STAGE_PASS": latent_pass(result),
    }


def install_pair(result_bytes: bytes, report_bytes: bytes) -> None:
    if OUT.exists() or REPORT.exists():
        raise FileExistsError("within-group stage target artifact already exists")
    with tempfile.TemporaryDirectory(prefix="source_native_within_group_stage_target_", dir=RESULTS) as directory:
        result_stage = Path(directory) / "result.json"
        report_stage = Path(directory) / "report.md"
        result_stage.write_bytes(result_bytes)
        report_stage.write_bytes(report_bytes)
        if OUT.exists() or REPORT.exists():
            raise FileExistsError("within-group stage target artifact appeared during execution")
        os.link(result_stage, OUT)
        try:
            os.link(report_stage, REPORT)
        except Exception:
            OUT.unlink(missing_ok=True)
            raise


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing a second within-group stage target run")
    for path, expected in SAFE_FROZEN.items():
        if sha(path) != expected:
            raise SystemExit(f"frozen stage target input mismatch: {path.name}")
    if json.loads(CAPACITY_VALIDATION.read_text())["status"] != "PASS_INDEPENDENT_SCORE_BLIND_STAGE_CAPACITY_RECONSTRUCTION":
        raise SystemExit("stage capacity validation is not PASS")
    preflight = json.loads(PREFLIGHT.read_text())
    if preflight["status"] != "PASS_TARGET_FREE_WITHIN_GROUP_STAGE_PREFLIGHT_V2" or not all(preflight["gates"].values()):
        raise SystemExit("stage v2 preflight does not authorize target")
    validation = json.loads(PREFLIGHT_VALIDATION.read_text())
    if validation["status"] != "PASS_INDEPENDENT_WITHIN_GROUP_STAGE_PREFLIGHT_V2_RECONSTRUCTION" or not validation["target_outputs_absent"]:
        raise SystemExit("stage v2 independent validation does not authorize target")
    if json.loads(TARGET_SOURCE_VALIDATION.read_text())["status"] != "PASS_INDEPENDENT_EXACT_FAMILY_GRAMMAR_SCAFFOLD_RECONSTRUCTION":
        raise SystemExit("target source validation is not PASS")

    # Target access begins only after every target-blind authorization check.
    if sha(TARGET_SOURCE) != TARGET_HASH:
        raise SystemExit("frozen target source hash mismatch")
    with TARGET_SOURCE.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if tuple(reader.fieldnames or ()) != SOURCE_FIELDS:
            raise ValueError("target source schema drift")
        source_rows = list(reader)
    if len(source_rows) != 26184:
        raise ValueError("target source row count drift")
    source_by_id = {row["consensus_group_id"]: row for row in source_rows}
    if len(source_by_id) != len(source_rows):
        raise ValueError("duplicate target consensus-group ID")

    panel = load_panel(PANEL_PATH)
    panel_ids = {row["unit_id"] for row in panel.rows}
    eligible_ids = set()
    for source in source_rows:
        match = re.match(r"f\d+", source["page"])
        if source["strict_zero_alternative"] == "1" and source["grammar_scope"] == "CONFIRMED_PROSE" and match is not None:
            eligible_ids.add(source["consensus_group_id"])
    if eligible_ids != panel_ids or len(eligible_ids) != 21899:
        raise ValueError("target eligible ID-set drift")

    sequences = []
    family_counts: Counter[str] = Counter()
    for masked in panel.rows:
        source = source_by_id.get(masked["unit_id"])
        if source is None or source["consensus_group_id"] != masked["unit_id"]:
            raise ValueError("target join identity mismatch")
        match = re.match(r"f\d+", source["page"])
        if match is None or source["strict_zero_alternative"] != "1" or source["grammar_scope"] != "CONFIRMED_PROSE":
            raise ValueError("target join scope mismatch")
        surface = source["family_surface"]
        if len(surface) != int(masked["symbol_count"]) or int(source["symbol_count"]) != len(surface):
            raise ValueError("target sequence length mismatch")
        if not surface or any(symbol not in INDEX for symbol in surface):
            raise ValueError("invalid target family surface")
        exact = {
            "locus": source["locus"],
            "page": source["page"],
            "physical_folio": match.group(),
            "section": source["section"],
            "currier": source["currier"],
            "hand": source["hand"],
            "kind": source["kind"],
            "symbol_count": str(len(surface)),
            "split": split_for(match.group()),
        }
        if any(masked[key] != value for key, value in exact.items()):
            raise ValueError("target metadata or split mismatch")
        encoded = tuple(INDEX[symbol] for symbol in surface)
        sequences.append(encoded)
        family_counts.update(surface)

    forward_full = evaluate(panel, sequences)
    reversed_full = evaluate(panel, [tuple(reversed(sequence)) for sequence in sequences])
    forward, reversed_result = aggregate(forward_full), aggregate(reversed_full)
    same_selected_latent = (
        forward["selected_model"] == reversed_result["selected_model"]
        and forward["selected_model"].startswith("LATENT_")
    )
    principal_delta = numeric_max(principal_gain(forward_full), principal_gain(reversed_full)) if same_selected_latent else None
    positional_target_pass = forward["POSITIONAL_PASS"] and reversed_result["POSITIONAL_PASS"]
    latent_stage_target_pass = (
        forward["LATENT_STAGE_PASS"]
        and reversed_result["LATENT_STAGE_PASS"]
        and same_selected_latent
        and principal_delta is not None
        and principal_delta <= 1e-10
    )
    gates = {
        "exact_26184_source_rows": len(source_rows) == 26184,
        "exact_21899_joined_groups": len(sequences) == 21899,
        "exact_split_counts": Counter(row["split"] for row in panel.rows) == {"TRAIN": 10753, "CAL": 5516, "TEST": 5630},
        "exact_94_folios": len(set(panel.folios)) == 94,
        "complete_eligible_id_set": eligible_ids == panel_ids,
        "forward_POSITIONAL_PASS": forward["POSITIONAL_PASS"],
        "reversed_POSITIONAL_PASS": reversed_result["POSITIONAL_PASS"],
        "forward_LATENT_STAGE_PASS": forward["LATENT_STAGE_PASS"],
        "reversed_LATENT_STAGE_PASS": reversed_result["LATENT_STAGE_PASS"],
        "same_selected_latent_model": same_selected_latent,
        "latent_principal_reversal_delta_at_most_1e_10": principal_delta is not None and principal_delta <= 1e-10,
        "POSITIONAL_TARGET_PASS": positional_target_pass,
        "LATENT_STAGE_TARGET_PASS": latent_stage_target_pass,
    }
    if latent_stage_target_pass:
        status = "CONFIRM_COMPLETE_SOURCE_NATIVE_LATENT_STAGE_GRAMMAR"
        decision = "AUTHORIZE_NEUTRAL_STAGE_ATLAS"
    elif positional_target_pass:
        status = "CONFIRM_COMPLETE_SOURCE_NATIVE_POSITIONAL_STRUCTURE_ONLY"
        decision = "RETAIN_POSITIONAL_STRUCTURE_WITHOUT_UNIQUE_STAGE_ATLAS"
    else:
        status = "NONCONFIRM_COMPLETE_SOURCE_NATIVE_WITHIN_GROUP_STAGE_MODEL"
        decision = "CLOSE_EXACT_WITHIN_GROUP_STAGE_MODEL_WITHOUT_RETUNING"

    result = {
        "experiment": "SOURCE_NATIVE_WITHIN_GROUP_STAGE_TARGET",
        "status": status,
        "decision": decision,
        "inputs": {path.name: sha(path) for path in (*SAFE_FROZEN, TARGET_SOURCE, RUNNER)},
        "source_rows_accessed": len(source_rows),
        "joined_target_sequences": len(sequences),
        "physical_folios": len(set(panel.folios)),
        "split_group_counts": dict(sorted(Counter(row["split"] for row in panel.rows).items())),
        "family_counts": {family: family_counts[family] for family in INDEX},
        "forward": forward,
        "reversed": reversed_result,
        "latent_principal_reversal_max_abs": principal_delta,
        "gates": gates,
        "target_source_opened": True,
        "target_sequences_accessed": len(sequences),
        "target_evaluations_computed": 2,
        "event_level_sequences_stored": 0,
        "event_level_stage_paths_stored": 0,
        "english_glosses": 0,
        "claim_ceiling": "A pass establishes only complete source-native positional structure and, under the stronger gate, a transferable neutral ordered-stage construction. It supplies no prefix, root, suffix, sound, word, part of speech, language, cipher operation, meaning, plaintext, or translation.",
    }
    report = f"""# Complete source-native within-group stage target

Status: **{status}**

The one authorized join read **{len(source_rows):,}** source rows and matched
all **{len(sequences):,}** frozen complete prose groups. The forward model
selects **{forward['selected_model']}** against **{forward['best_fixed_model']}**;
the reversed robustness view selects **{reversed_result['selected_model']}**
against **{reversed_result['best_fixed_model']}**.

Forward/reversed equal-folio selected-minus-K1 gains are
**{forward['gain']['effect_equal_folio']:+.6f}** and
**{reversed_result['gain']['effect_equal_folio']:+.6f}** nat/symbol. Their
selected-minus-best-FIXED gains are
**{forward['gain_vs_fixed']['effect_equal_folio']:+.6f}** and
**{reversed_result['gain_vs_fixed']['effect_equal_folio']:+.6f}**.
`POSITIONAL_TARGET_PASS` is **{str(positional_target_pass).lower()}** and
`LATENT_STAGE_TARGET_PASS` is **{str(latent_stage_target_pass).lower()}**.

Decision: **{decision}**. No event-level sequence or path is stored. Even a
pass establishes only neutral structural stages, never a prefix, root, suffix,
sound, word, part of speech, language, cipher operation, meaning, plaintext,
or translation.
"""
    install_pair((json.dumps(result, indent=2, sort_keys=True) + "\n").encode(), report.encode())
    print(json.dumps({"status": status, "selected_forward": forward["selected_model"], "selected_reversed": reversed_result["selected_model"], "gates": gates, "decision": decision}, sort_keys=True))


if __name__ == "__main__":
    main()
