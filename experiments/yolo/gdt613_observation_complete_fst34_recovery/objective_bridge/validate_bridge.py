#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path


TOL = 1e-12


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    root = args.bundle.resolve()
    artifact = root / "results"
    checks: dict[str, bool] = {}

    manifest = rows(artifact / "OUTPUT_MANIFEST.tsv")
    checks["manifest_entries_exist"] = all(
        ((root if row["kind"] != "artifact" else artifact) / row["path"]).is_file()
        for row in manifest
    )
    checks["manifest_hashes_exact"] = all(
        sha256((root if row["kind"] != "artifact" else artifact) / row["path"])
        == row["sha256"]
        for row in manifest
    )

    inputs = rows(artifact / "input_manifest.tsv")
    checks["twenty_allowlisted_inputs"] = len(inputs) == 20
    checks["input_paths_scope_safe"] = all(
        "f84" not in row["relative_path"].lower()
        and "target" not in row["relative_path"].lower()
        and row["relative_path"].startswith(
            ("artifacts/synthetic_", "artifacts/units", "artifacts/primitives", "artifacts/reference_packs/", "artifacts/keys/synthetic/")
        )
        for row in inputs
    )

    result = json.loads((artifact / "RESULTS.json").read_text(encoding="utf-8"))
    validation = json.loads((artifact / "VALIDATION.json").read_text(encoding="utf-8"))
    checks["producer_validation_ok"] = validation["status"] == "VALIDATION_OK"
    checks["declared_mutation_count_1888"] = result["mutation_universe"]["count"] == 1888

    catalog = rows(artifact / "mutation_catalog.tsv")
    checks["catalog_1888_unique"] = len(catalog) == 1888 and len(
        {row["mutation_id"] for row in catalog}
    ) == 1888
    checks["catalog_same_length"] = all(
        len("" if row["old_output"] == "<EMPTY>" else row["old_output"])
        == len("" if row["new_output"] == "<EMPTY>" else row["new_output"])
        == int(row["fixed_output_length"])
        for row in catalog
    )

    local = rows(artifact / "local_mutation_scores.tsv")
    checks["all_mutation_panels_present"] = len(local) == 1888 * 8 * 2
    checks["local_structure_exactly_invariant"] = all(
        abs(float(row[field])) <= 1e-9
        for row in local
        for field in (
            "delta_weighted_letters_vs_truth",
            "delta_weighted_boundaries_vs_truth",
            "delta_weighted_words_vs_truth",
        )
    )
    panels: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in local:
        panels[(row["model"], row["weight_scheme"])].append(row)
    summaries = {
        (row["model"], row["weight_scheme"]): row
        for row in rows(artifact / "local_truth_rank_summary.tsv")
    }
    checks["sixteen_local_panels"] = set(panels) == set(summaries) and len(panels) == 16
    rank_replay_ok = True
    for panel, values in panels.items():
        summary = summaries[panel]
        deltas = [float(row["delta_bits_per_scored_symbol_vs_truth"]) for row in values]
        beating = sum(delta < -TOL for delta in deltas)
        tying = sum(abs(delta) <= TOL for delta in deltas)
        rank_replay_ok &= beating == int(summary["decoys_beating_truth"])
        rank_replay_ok &= tying == int(summary["decoys_tying_truth"])
        rank_replay_ok &= 1 + beating == int(
            summary["truth_rank_of_truth_plus_local_decoys"]
        )
    checks["local_rank_replay"] = rank_replay_ok

    zero = rows(artifact / "zero_exposure_tie_audit.tsv")
    checks["four_zero_exposure_primitives"] = {
        row["primitive"] for row in zero
    } == {"F", "K", "f", "i"}
    checks["zero_exposure_explains_232_ties"] = sum(
        int(row["expected_exact_score_ties_per_panel"]) for row in zero
    ) == 232

    primary = {
        model: {
            row["mutation_id"]
            for row in values
            if float(row["delta_bits_per_scored_symbol_vs_truth"]) < -TOL
        }
        for (model, scheme), values in panels.items()
        if scheme == "event_count_PRIMARY"
    }
    universal = sorted(set.intersection(*(set(value) for value in primary.values())))
    checks["universal_beater_replayed"] = universal == result[
        "primary_local_decoys_beating_truth_in_every_model"
    ] == ["P28_que_TO_qua"]

    key_scores = rows(artifact / "key_scores.tsv")
    checks["seven_keys_eight_models_two_weights"] = len(key_scores) == 7 * 8 * 2
    key_ranks = rows(artifact / "key_rank_summary.tsv")
    checks["truth_wins_all_seven_key_panels"] = len(key_ranks) == 16 and all(
        row["truth_rank_of_7"] == "1"
        and row["wrong_keys_beating_truth"] == "0"
        and row["wrong_keys_tying_truth"] == "0"
        for row in key_ranks
    )
    checks["truth_wins_all_seven_key_letter_denominator_panels"] = all(
        row["truth_rank_of_7_letter_denominator"] == "1"
        and row["wrong_keys_beating_truth_letter_denominator"] == "0"
        and row["wrong_keys_tying_truth_letter_denominator"] == "0"
        for row in key_ranks
    )

    splits = rows(artifact / "reference_split_audit.tsv")
    checks["reference_split_models_sane"] = len(splits) == 8 and all(
        row["beats_uniform"] == "1" for row in splits
    )
    checks["fit_score_contracts_explicit_and_separate"] = {
        row["fit_score_mode"] for row in splits
    } == {"LEGACY_CONTINUOUS_CHUNK", "RESET_MATCHED_WORD"} and all(
        row["model"].startswith(row["fit_score_mode"] + "__") for row in splits
    )
    split_by_partition = defaultdict(list)
    for row in splits:
        split_by_partition[row["fit_partition"]].append(row)
    checks["prospective_fit_confirm_partitions_exact"] = (
        len(split_by_partition["LM_FIT_40"]) == 2
        and len(split_by_partition["LM_CONFIRM_20"]) == 2
        and all(
            row["fit_words"] == "8209"
            and row["fit_sequence_sha256"]
            == "2255b67ffb1b41bf1c327b97fb5b7c87acec70947aeeb3b75143d55a2af1c412"
            for row in split_by_partition["LM_FIT_40"]
        )
        and all(
            row["fit_words"] == "4104"
            and row["fit_sequence_sha256"]
            == "73d40ca54cc2fec3e7f1a5df4994a5cd394f4cbee2dacf966aa81c59518246a1"
            for row in split_by_partition["LM_CONFIRM_20"]
        )
    )
    falsifiers = rows(artifact / "hard_falsifiers.tsv")
    triggered = sorted(row["falsifier_id"] for row in falsifiers if row["triggered"] == "1")
    checks["triggered_falsifiers_replay"] = triggered == sorted(
        result["triggered_falsifiers"]
    )
    checks["decision_replayed"] = (
        result["decision"] == "PURE_LATIN_CE_FAILS_AT_LEAST_ONE_DECLARED_BRIDGE_GATE"
        and not result["truth_unique_rank1_all_primary_local_panels"]
        and result["truth_unique_rank1_all_primary_seven_key_panels"]
    )

    payload = {
        "status": "INDEPENDENT_VALIDATION_OK" if all(checks.values()) else "INDEPENDENT_VALIDATION_FAILED",
        "check_count": len(checks),
        "checks": checks,
    }
    args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, sort_keys=True))
    if payload["status"] != "INDEPENDENT_VALIDATION_OK":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
