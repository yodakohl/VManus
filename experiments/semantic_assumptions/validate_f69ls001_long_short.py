#!/usr/bin/env python3
"""Production-free reconstruction of F69LS001."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
ANNOTATIONS = ROOT / "experiments/semantic_assumptions/results/existing_human_exact_locus_annotations.tsv"
SURFACE = ROOT / "experiments/semantic_assumptions/results/source_separator_transcription.tsv"
ALIGNMENT = ROOT / "experiments/semantic_assumptions/results/source_sta_group_alignment.tsv"
STA = ROOT / "experiments/semantic_assumptions/results/source_sta_family_consensus_loci.tsv"
METHOD = ROOT / "F69LS001_LONG_SHORT_LOG_METHOD.md"
RECOVERY = ROOT / "F69LS001_SOURCE_RECOVERY.md"
RUNNER = ROOT / "experiments/semantic_assumptions/f69ls001_long_short.py"
RESULT = ROOT / "experiments/semantic_assumptions/results/f69ls001_long_short_result.json"
REPORT = ROOT / "experiments/semantic_assumptions/results/f69ls001_long_short_report.md"
OUT_JSON = ROOT / "experiments/semantic_assumptions/results/f69ls001_long_short_validation.json"
OUT_MD = ROOT / "experiments/semantic_assumptions/results/f69ls001_long_short_validation.md"

EDITIONS = ("ZL3b", "IT2a", "RF1b")
TOL = 1e-12
EXPECTED_INPUTS = {
    "F69LS001_LONG_SHORT_LOG_METHOD.md": "737ebaf17e83a5a982ca0a1ffba4fc8708fdb71ed9733cfa5578446136289230",
    "F69LS001_SOURCE_RECOVERY.md": "9047f449a962690af3f8a414fc9927682cec5b850f11d36da09edf9415d2443a",
    "experiments/semantic_assumptions/f69ls001_long_short.py": "46528aacefaba7531df24bb51fab548ea0015b1753f1f80adadfee6b913dc6c4",
    "experiments/semantic_assumptions/results/existing_human_exact_locus_annotations.tsv": "79c7f06e91f90054aff4cdf27f098a5977d820acdf91f239a14c6ddf553a7f61",
    "experiments/semantic_assumptions/results/source_separator_transcription.tsv": "4b649c8290d5afc7a5fbcc8e98db2bc123a1ceb5f3858d3befa781ce96b680f0",
    "experiments/semantic_assumptions/results/source_sta_family_consensus_loci.tsv": "84354a9e5d291ab00f45c9bfe161f62d8cbd8c39db7511ff263cd9fcfe9d9e77",
    "experiments/semantic_assumptions/results/source_sta_group_alignment.tsv": "f23654f1d4c854db6d458b418a0d3530115731604854cf0a0495565e58341840",
}
EXPECTED_RESULT_SHA = "649535a69eb853548c801f25dcea33db5b0bf597a317f6f3df32fba7a9a75fbc"
EXPECTED_REPORT_SHA = "baf00b9fd38ae1441c96fe294a34b9a9ffc2deaca485ac7079e1be32f5f88736"

CHECKS = 0


def require(condition: bool, message: str) -> None:
    global CHECKS
    CHECKS += 1
    if not condition:
        raise RuntimeError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_sha(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
    return hashlib.sha256(payload).hexdigest()


def array_sha(value: np.ndarray) -> str:
    payload = np.ascontiguousarray(value.astype("<f8", copy=False)).tobytes(order="C")
    return hashlib.sha256(payload).hexdigest()


def validate_panel(panel: list[dict[str, object]]) -> list[dict[str, object]]:
    ordered = sorted(panel, key=lambda row: int(row["ordinal"]))
    ordinals = [int(row["ordinal"]) for row in ordered]
    require(len(ordered) == 28, "panel row count")
    require(ordinals == list(range(1, 29)), "panel ordinal contract")
    require(len({str(row["locus"]) for row in ordered}) == 28, "panel locus uniqueness")
    expected = ["LONG" if ordinal % 2 else "SHORT" for ordinal in ordinals]
    require([row["state"] for row in ordered] == expected, "panel alternation")
    return ordered


def reconstruct_inputs() -> tuple[list[dict[str, object]], dict[str, dict[str, str]], dict[str, dict[str, int]], dict[str, str]]:
    panel: list[dict[str, object]] = []
    with ANNOTATIONS.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["page"] != "f69v" or row["unit"] != "X1":
                continue
            match = re.fullmatch(r"f69v\.X1\.(\d+)", row["old_locus"])
            require(match is not None, f"bad old locus {row['old_locus']}")
            state = re.search(r"\b(long|short)\b", row["local_comment"].lower())
            require(state is not None, f"missing state {row['locus']}")
            panel.append({"ordinal": int(match.group(1)), "locus": row["locus"], "state": state.group(1).upper()})
    panel = validate_panel(panel)
    loci = {str(row["locus"]) for row in panel}

    source: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    with SURFACE.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["locus"] in loci and row["edition"] in EDITIONS:
                source[(row["locus"], row["edition"])].append(row)
    source_ids = {row["source_group_id"] for rows in source.values() for row in rows}
    require(len(source_ids) == 100, "source group count")

    alignment: dict[str, dict[str, str]] = {}
    with ALIGNMENT.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            identifier = row["source_group_id"]
            if identifier in source_ids:
                require(identifier not in alignment, f"duplicate alignment {identifier}")
                require(re.fullmatch(r"[a-z]+", row["nearest_basic_eva_primary"]) is not None, f"bad basic EVA {identifier}")
                alignment[identifier] = row
    require(set(alignment) == source_ids, "alignment ID coverage")

    surfaces: dict[str, dict[str, str]] = {edition: {} for edition in EDITIONS}
    counts: dict[str, dict[str, int]] = {edition: {} for edition in EDITIONS}
    for locus in sorted(loci):
        for edition in EDITIONS:
            rows = sorted(source[(locus, edition)], key=lambda row: int(row["source_group_index"]))
            require(bool(rows), f"missing source {edition} {locus}")
            require({int(row["source_group_count"]) for row in rows} == {len(rows)}, f"declared count {edition} {locus}")
            require([int(row["source_group_index"]) for row in rows] == list(range(1, len(rows) + 1)), f"group order {edition} {locus}")
            basics: list[str] = []
            for row in rows:
                other = alignment[row["source_group_id"]]
                for field in ("source_group_id", "edition", "locus", "source_group_index", "source_group_count", "left_separator", "right_separator"):
                    require(row[field] == other[field], f"alignment mismatch {field} {row['source_group_id']}")
                basics.append(other["nearest_basic_eva_primary"])
            surfaces[edition][locus] = "".join(basics)
            counts[edition][locus] = len(rows)

    sta: dict[str, str] = {}
    with STA.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["locus"] not in loci:
                continue
            require(row["locus"] not in sta, f"duplicate STA {row['locus']}")
            require(re.fullmatch(r"[A-Z]+", row["family_sequence"]) is not None, f"bad STA {row['locus']}")
            sta[row["locus"]] = row["family_sequence"]
    require(set(sta) == loci, "STA coverage")
    return panel, surfaces, counts, sta


def pair_indices(mode: str) -> tuple[np.ndarray, np.ndarray]:
    long_index = np.arange(0, 28, 2, dtype=np.int64)
    short_index = np.arange(1, 28, 2, dtype=np.int64) if mode == "FORWARD" else (long_index - 1) % 28
    require(sorted(np.concatenate([long_index, short_index]).tolist()) == list(range(28)), f"bad {mode} partition")
    return long_index, short_index


def add_binary(features: dict[str, np.ndarray], name: str, values: object) -> None:
    features[name] = np.asarray(values, dtype=np.float64)


def reconstruct_features(
    panel: list[dict[str, object]],
    surfaces: dict[str, dict[str, str]],
    group_counts: dict[str, dict[str, int]],
    sta: dict[str, str],
) -> tuple[list[str], np.ndarray, dict[str, list[str]], dict[str, str], int, int]:
    loci = [str(row["locus"]) for row in panel]
    text = [[surfaces[edition][locus] for locus in loci] for edition in EDITIONS]
    features: dict[str, np.ndarray] = {}
    features["SURF_SCALAR:COMPACT_LENGTH"] = np.asarray([[len(value) for value in reading] for reading in text], dtype=np.float64)
    features["SURF_SCALAR:SOURCE_GROUP_COUNT"] = np.asarray([[group_counts[edition][locus] for locus in loci] for edition in EDITIONS], dtype=np.float64)
    chars = sorted({symbol for reading in text for value in reading for symbol in value})
    bigrams = sorted({value[i:i + 2] for reading in text for value in reading for i in range(len(value) - 1)})
    trigrams = sorted({value[i:i + 3] for reading in text for value in reading for i in range(len(value) - 2)})
    for symbol in chars:
        values = np.asarray([[value.count(symbol) for value in reading] for reading in text], dtype=np.float64)
        add_binary(features, f"SURF_HAS_CHAR:{symbol}", values > 0)
        features[f"SURF_COUNT_CHAR:{symbol}"] = values
    for gram in bigrams:
        values = np.asarray([[sum(value[i:i + 2] == gram for i in range(len(value) - 1)) for value in reading] for reading in text], dtype=np.float64)
        add_binary(features, f"SURF_HAS_BIGRAM:{gram}", values > 0)
        features[f"SURF_COUNT_BIGRAM:{gram}"] = values
    for gram in trigrams:
        add_binary(features, f"SURF_HAS_TRIGRAM:{gram}", [[gram in value for value in reading] for reading in text])
    for width in range(1, 5):
        prefixes = sorted({value[:width] for reading in text for value in reading if len(value) >= width})
        suffixes = sorted({value[-width:] for reading in text for value in reading if len(value) >= width})
        for prefix in prefixes:
            add_binary(features, f"SURF_PREFIX{width}:{prefix}", [[value.startswith(prefix) for value in reading] for reading in text])
        for suffix in suffixes:
            add_binary(features, f"SURF_SUFFIX{width}:{suffix}", [[value.endswith(suffix) for value in reading] for reading in text])

    sta_row = [sta[locus] for locus in loci]
    sta_text = [sta_row, sta_row, sta_row]
    families = sorted({symbol for value in sta_row for symbol in value})
    bigrams = sorted({value[i:i + 2] for value in sta_row for i in range(len(value) - 1)})
    trigrams = sorted({value[i:i + 3] for value in sta_row for i in range(len(value) - 2)})
    for family in families:
        values = np.asarray([[value.count(family) for value in reading] for reading in sta_text], dtype=np.float64)
        add_binary(features, f"STA_HAS_FAMILY:{family}", values > 0)
        features[f"STA_COUNT_FAMILY:{family}"] = values
    for gram in bigrams:
        values = np.asarray([[sum(value[i:i + 2] == gram for i in range(len(value) - 1)) for value in reading] for reading in sta_text], dtype=np.float64)
        add_binary(features, f"STA_HAS_BIGRAM:{gram}", values > 0)
        features[f"STA_COUNT_BIGRAM:{gram}"] = values
    for gram in trigrams:
        add_binary(features, f"STA_HAS_TRIGRAM:{gram}", [[gram in value for value in reading] for reading in sta_text])
    for width in range(1, 4):
        prefixes = sorted({value[:width] for value in sta_row if len(value) >= width})
        suffixes = sorted({value[-width:] for value in sta_row if len(value) >= width})
        for prefix in prefixes:
            add_binary(features, f"STA_PREFIX{width}:{prefix}", [[value.startswith(prefix) for value in reading] for reading in sta_text])
        for suffix in suffixes:
            add_binary(features, f"STA_SUFFIX{width}:{suffix}", [[value.endswith(suffix) for value in reading] for reading in sta_text])

    collapsed: dict[bytes, list[str]] = defaultdict(list)
    for name, matrix in features.items():
        require(matrix.shape == (3, 28), f"shape {name}")
        require(np.isfinite(matrix).all(), f"finite {name}")
        collapsed[np.ascontiguousarray(matrix.astype("<f8")).tobytes()].append(name)

    retained: dict[str, tuple[np.ndarray, list[str], str]] = {}
    for raw, names0 in collapsed.items():
        aliases = sorted(names0)
        matrix = np.frombuffer(raw, dtype="<f8").reshape(3, 28).copy()
        binary = bool(np.isin(matrix, [0.0, 1.0]).all())
        if binary:
            support = matrix.sum(axis=1)
            eligible = bool(((support >= 6) & (support <= 22)).all())
        else:
            eligible = bool((matrix.std(axis=1, ddof=0) > 0).all())
        for mode in ("FORWARD", "BACKWARD"):
            long_index, short_index = pair_indices(mode)
            differences = matrix[:, long_index] - matrix[:, short_index]
            eligible = eligible and bool((np.abs(differences).sum(axis=1) > 0).all())
        if eligible:
            retained[aliases[0]] = (matrix, aliases, "BINARY" if binary else "COUNT_OR_SCALAR")
    names = sorted(retained)
    matrix = np.stack([retained[name][0] for name in names], axis=0)
    aliases = {name: retained[name][1] for name in names}
    kinds = {name: retained[name][2] for name in names}
    return names, matrix, aliases, kinds, len(features), len(collapsed)


def flip_signs() -> np.ndarray:
    return np.asarray([[1.0 if ((world >> pair) & 1) == 0 else -1.0 for pair in range(14)] for world in range(1 << 14)], dtype=np.float64)


def orbit(matrix: np.ndarray, mode: str) -> dict[str, object]:
    long_index, short_index = pair_indices(mode)
    differences = matrix[:, :, long_index] - matrix[:, :, short_index]
    effects = np.einsum("wp,fep->wfe", flip_signs(), differences, optimize=False) / 14.0
    null_sd = effects.std(axis=0, ddof=0)
    require(np.isfinite(effects).all(), f"finite effects {mode}")
    require((null_sd > 0).all(), f"positive null SD {mode}")
    z = effects / null_sd[None, :, :]
    coherent = ((z > 0).all(axis=2)) | ((z < 0).all(axis=2))
    scores = np.where(coherent, np.min(np.abs(z), axis=2), 0.0)
    maxima = scores.max(axis=1)
    observed_max = float(maxima[0])
    top = np.flatnonzero(np.abs(scores[0] - observed_max) <= TOL)
    extreme = int(np.count_nonzero(maxima >= observed_max - TOL))
    return {
        "long": long_index,
        "short": short_index,
        "differences": differences,
        "effects": effects[0],
        "z": z[0],
        "maxima": maxima,
        "null_sd": null_sd,
        "observed_max": observed_max,
        "top": top,
        "extreme": extreme,
        "p": float(extreme / len(maxima)),
    }


def robustness(matrix: np.ndarray, feature_index: int, mode: str) -> dict[str, object]:
    long_index, short_index = pair_indices(mode)
    feature = matrix[feature_index]
    differences = feature[:, long_index] - feature[:, short_index]
    effect = differences.mean(axis=1)
    loo = np.stack([np.delete(differences, pair, axis=1).mean(axis=1) for pair in range(14)], axis=0)
    denominator = np.abs(differences).sum(axis=1)
    concentration = np.divide(np.abs(differences).max(axis=1), denominator, out=np.full(3, np.inf), where=denominator > 0)
    return {
        "loo_effects_sha256": array_sha(loo),
        "loo_direction_ok": bool(((loo * np.sign(effect)[None, :]) > 0).all()),
        "max_pair_contribution_fraction": [float(value) for value in concentration],
        "concentration_ok": bool((concentration <= 0.35 + TOL).all()),
    }


def controls() -> dict[str, object]:
    planted_matrix = np.zeros((1, 3, 28), dtype=np.float64)
    planted_matrix[:, :, 0::2] = 1.0
    planted = {mode: orbit(planted_matrix, mode) for mode in ("FORWARD", "BACKWARD")}
    planted_robustness = {mode: robustness(planted_matrix, 0, mode) for mode in planted}
    concentrated = np.zeros((1, 3, 28), dtype=np.float64)
    concentrated[:, :, 0] = 1.0
    concentration_flags = {mode: robustness(concentrated, 0, mode)["concentration_ok"] for mode in planted}
    one_reading = planted_matrix.copy()
    one_reading[:, 1, :] = np.roll(one_reading[:, 1, :], 1, axis=1)
    one_reading[:, 2, :] = np.roll(one_reading[:, 2, :], 2, axis=1)
    one_reading_scores = {mode: orbit(one_reading, mode)["observed_max"] for mode in planted}
    tie_rejected = False
    try:
        orbit(np.zeros((2, 3, 28), dtype=np.float64), "FORWARD")
    except RuntimeError:
        tie_rejected = True
    malformed = [{"ordinal": i, "locus": f"synthetic.{i}", "state": "LONG" if i % 2 else "SHORT"} for i in range(1, 29)]
    malformed[-1] = dict(malformed[-2])
    malformed_rejected = False
    try:
        validate_panel(malformed)
    except RuntimeError:
        malformed_rejected = True
    return {
        "planted_p_values": {mode: planted[mode]["p"] for mode in planted},
        "planted_scores": {mode: planted[mode]["observed_max"] for mode in planted},
        "planted_robustness": planted_robustness,
        "one_reading_only_scores": one_reading_scores,
        "concentration_control_passes_concentration_gate": concentration_flags,
        "tie_zero_variance_control_rejected": tie_rejected,
        "malformed_duplicate_ordinal_control_rejected": malformed_rejected,
        "passes": bool(
            all(planted[mode]["p"] <= 0.01 for mode in planted)
            and all(planted[mode]["observed_max"] >= 2.5 for mode in planted)
            and all(planted_robustness[mode]["loo_direction_ok"] and planted_robustness[mode]["concentration_ok"] for mode in planted)
            and all(one_reading_scores[mode] == 0.0 for mode in planted)
            and not any(concentration_flags.values())
            and tie_rejected
            and malformed_rejected
        ),
    }


def main() -> int:
    require(not OUT_JSON.exists() and not OUT_MD.exists(), "validation outputs already exist")
    for relative, expected in EXPECTED_INPUTS.items():
        require(sha256(ROOT / relative) == expected, f"input hash {relative}")
    require(sha256(RESULT) == EXPECTED_RESULT_SHA, "result hash")
    require(sha256(REPORT) == EXPECTED_REPORT_SHA, "report hash")
    stored = json.loads(RESULT.read_text(encoding="utf-8"))
    require(stored["inputs"] == EXPECTED_INPUTS, "stored input binding")

    panel, surfaces, group_counts, sta = reconstruct_inputs()
    names, matrix, aliases, kinds, raw_count, collapsed_count = reconstruct_features(panel, surfaces, group_counts, sta)
    require(raw_count == 404, "raw feature count")
    require(collapsed_count == 143, "collapsed feature count")
    require(len(names) == 43, "eligible feature count")
    require(canonical_sha(names) == "7262b733f2033f90100d980f6fbe6167f7473dbdaaea811960e2efee8a7d21ac", "feature-name digest")
    require(array_sha(matrix) == "88e4ea8adf7e0a512187de9c05c6e2176e6b9762278549414b01bcf725876db6", "feature matrix digest")

    scored = {mode: orbit(matrix, mode) for mode in ("FORWARD", "BACKWARD")}
    top_by_pairing = {mode: [names[index] for index in scored[mode]["top"]] for mode in scored}
    common = sorted(set(top_by_pairing["FORWARD"]) & set(top_by_pairing["BACKWARD"]))
    primary = common[0] if common else top_by_pairing["FORWARD"][0]
    primary_index = names.index(primary)
    observed_effects = np.asarray(scored["FORWARD"]["effects"])[primary_index]
    observed_z = {mode: np.asarray(scored[mode]["z"])[primary_index] for mode in scored}
    direction = "LONG_POSITIVE" if (observed_effects > 0).all() else "SHORT_POSITIVE" if (observed_effects < 0).all() else "INCOHERENT"
    if kinds[primary] == "BINARY":
        material = np.abs(observed_effects)
        material_metric = "ABSOLUTE_PROPORTION_DIFFERENCE"
        material_ok = bool((material >= 0.35 - TOL).all())
    else:
        material = np.abs(observed_effects) / matrix[primary_index].std(axis=1, ddof=0)
        material_metric = "ALL_28_POPULATION_SD_STANDARDIZED_DIFFERENCE"
        material_ok = bool((material >= 0.75 - TOL).all())
    robust = {mode: robustness(matrix, primary_index, mode) for mode in scored}
    control_result = controls()
    gates = {
        "input_and_panel_contract": True,
        "finite_nonzero_nulls": True,
        "unique_common_top_feature": len(common) == 1 and top_by_pairing["FORWARD"] == common and top_by_pairing["BACKWARD"] == common and direction != "INCOHERENT",
        "maxT_p_le_0_01_both_pairings": all(scored[mode]["p"] <= 0.01 + TOL for mode in scored),
        "common_z_ge_2_5_both_pairings": all(np.min(np.abs(observed_z[mode])) >= 2.5 - TOL for mode in observed_z),
        "material_raw_effect": material_ok,
        "all_loo_directions": all(robust[mode]["loo_direction_ok"] for mode in robust),
        "pair_concentration_le_0_35": all(robust[mode]["concentration_ok"] for mode in robust),
        "synthetic_controls": bool(control_result["passes"]),
        "independent_validation": False,
    }
    scientific_pass = all(value for key, value in gates.items() if key != "independent_validation")
    decision = "PROVISIONAL_F69V_LONG_SHORT_FEATURE_LEAD_REQUIRES_VALIDATION_AND_REPLICATION" if scientific_pass else "PROVISIONAL_EXPLORATORY_NONCONFIRMATION_PENDING_VALIDATION"
    expected_result = {
        "experiment": "F69LS001",
        "status": decision,
        "inputs": EXPECTED_INPUTS,
        "recovery_qualified_after_unscored_source_representation_stop": True,
        "panel": panel,
        "editions": list(EDITIONS),
        "raw_feature_count_before_collapse": raw_count,
        "collapsed_feature_count_before_eligibility": collapsed_count,
        "eligible_collapsed_feature_count": len(names),
        "eligible_feature_names_sha256": canonical_sha(names),
        "eligible_matrix_sha256": array_sha(matrix),
        "primary_feature": primary,
        "primary_aliases": aliases[primary],
        "primary_kind": kinds[primary],
        "top_names_by_pairing": top_by_pairing,
        "common_top_names": common,
        "direction": direction,
        "observed_effects": {edition: float(value) for edition, value in zip(EDITIONS, observed_effects)},
        "observed_z_by_pairing": {mode: {edition: float(value) for edition, value in zip(EDITIONS, observed_z[mode])} for mode in observed_z},
        "material_metric": material_metric,
        "material_values": {edition: float(value) for edition, value in zip(EDITIONS, material)},
        "pairings": {
            mode: {
                "long_indices_0based": scored[mode]["long"].tolist(),
                "short_indices_0based": scored[mode]["short"].tolist(),
                "observed_max": scored[mode]["observed_max"],
                "inclusive_extreme_count": scored[mode]["extreme"],
                "p_value": scored[mode]["p"],
                "null_maxima_sha256": array_sha(scored[mode]["maxima"]),
                "null_sd_sha256": array_sha(scored[mode]["null_sd"]),
                "robustness": robust[mode],
            }
            for mode in scored
        },
        "controls": control_result,
        "gates": gates,
        "scientific_pass_before_validation": scientific_pass,
        "decision": decision,
        "claim_ceiling": "At most a provisional source-native feature association with f69v LONG/SHORT graphical state; no lunar mansion, day, number, length word, language, plaintext, or translation.",
    }
    require(expected_result == stored, "full result reconstruction")

    expected_report = (
        "# F69LS001 f69v LONG/SHORT result\n\n"
        f"Decision: `{decision}`.\n\n"
        f"The exact panel contains 14 LONG and 14 SHORT logs in 14 adjacent pairs. After duplicate collapse, {len(names)} complete source-native surface/STA features were eligible. "
        f"The top feature is `{primary}` ({direction}); aliases: {', '.join(aliases[primary])}.\n\n"
        "ZL3b/IT2a/RF1b effects are " + ", ".join(f"{value:+.6f}" for value in observed_effects)
        + "; FORWARD standardized values are " + ", ".join(f"{value:+.6f}" for value in observed_z["FORWARD"])
        + "; BACKWARD standardized values are " + ", ".join(f"{value:+.6f}" for value in observed_z["BACKWARD"])
        + ". "
        f"FORWARD maxT p={scored['FORWARD']['p']:.6f} ({scored['FORWARD']['extreme']}/16384); "
        f"BACKWARD maxT p={scored['BACKWARD']['p']:.6f} ({scored['BACKWARD']['extreme']}/16384).\n\n"
        "Gates: " + ", ".join(f"{key}={value}" for key, value in gates.items()) + ".\n\n"
        "The run is recovery-qualified after an unscored legacy-surface stop; all 100 source groups use the same validated basic-EVA realization. "
        "This complete exploratory feature test cannot identify lunar mansions, days, numbers, a length word, language, plaintext, or translation. "
        "A positive result would still require an independently selected graphical replication.\n"
    )
    require(REPORT.read_text(encoding="utf-8") == expected_report, "exact report reconstruction")
    require(not gates["maxT_p_le_0_01_both_pairings"], "maxT gate must fail")
    require(not gates["common_z_ge_2_5_both_pairings"], "z gate must fail")
    require(not scientific_pass, "scientific decision must fail")

    validation = {
        "experiment": "F69LS001",
        "status": "PASS_CLEAN_RECONSTRUCTION_FINAL_NONCONFIRMATION",
        "checks": CHECKS,
        "input_group_readings": 100,
        "raw_features": raw_count,
        "collapsed_features": collapsed_count,
        "eligible_features": len(names),
        "exact_null_assignments_per_pairing": 16384,
        "primary_feature": primary,
        "p_forward": scored["FORWARD"]["p"],
        "p_backward": scored["BACKWARD"]["p"],
        "result_sha256": sha256(RESULT),
        "report_sha256": sha256(REPORT),
        "validator_sha256": sha256(Path(__file__)),
        "decision": "FINAL_EXPLORATORY_NONCONFIRMATION_F69V_LONG_SHORT_COMPLETE_FEATURE_FAMILY",
        "claim_ceiling": stored["claim_ceiling"],
    }
    report = (
        "# F69LS001 independent validation\n\n"
        f"Status: `{validation['status']}` with {CHECKS} checks.\n\n"
        "Clean code imported no production module and reconstructed all 100 source-group joins, the 404-feature inventory, 143 exact matrix classes, 43 eligible classes, both 16,384-assignment nulls, robustness checks, controls, gates, full result JSON, and exact report.\n\n"
        f"The final decision is `{validation['decision']}`: FORWARD p={scored['FORWARD']['p']:.6f}, BACKWARD p={scored['BACKWARD']['p']:.6f}. "
        "This closes only the frozen f69v LONG/SHORT surface/STA feature family. It supplies no mansion, day, number, length word, language, plaintext, or translation.\n"
    )
    OUT_JSON.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(report, encoding="utf-8")
    print(json.dumps(validation, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
