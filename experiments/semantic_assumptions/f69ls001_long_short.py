#!/usr/bin/env python3
"""Exact paired f69v LONG/SHORT source-native feature test."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
METHOD = ROOT / "F69LS001_LONG_SHORT_LOG_METHOD.md"
ANNOTATIONS = ROOT / "experiments/semantic_assumptions/results/existing_human_exact_locus_annotations.tsv"
SURFACE = ROOT / "experiments/semantic_assumptions/results/source_separator_transcription.tsv"
STA = ROOT / "experiments/semantic_assumptions/results/source_sta_family_consensus_loci.tsv"
OUT_JSON = ROOT / "experiments/semantic_assumptions/results/f69ls001_long_short_result.json"
OUT_MD = ROOT / "experiments/semantic_assumptions/results/f69ls001_long_short_report.md"

EDITIONS = ("ZL3b", "IT2a", "RF1b")
EXPECTED_HASHES = {
    str(ANNOTATIONS.relative_to(ROOT)): "79c7f06e91f90054aff4cdf27f098a5977d820acdf91f239a14c6ddf553a7f61",
    str(SURFACE.relative_to(ROOT)): "4b649c8290d5afc7a5fbcc8e98db2bc123a1ceb5f3858d3befa781ce96b680f0",
    str(STA.relative_to(ROOT)): "84354a9e5d291ab00f45c9bfe161f62d8cbd8c39db7511ff263cd9fcfe9d9e77",
}
TOL = 1e-12


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def canonical_sha(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
    return hashlib.sha256(raw).hexdigest()


def array_sha(a: np.ndarray) -> str:
    x = np.ascontiguousarray(a.astype("<f8", copy=False))
    return hashlib.sha256(x.tobytes(order="C")).hexdigest()


def validate_panel_contract(panel: list[dict[str, object]]) -> None:
    ordinals = [int(item["ordinal"]) for item in panel]
    if len(ordinals) != 28 or len(set(ordinals)) != 28 or sorted(ordinals) != list(range(1, 29)):
        raise RuntimeError("panel is not one-to-one X1.1..28")
    if len({str(item["locus"]) for item in panel}) != 28:
        raise RuntimeError("panel has duplicate physical loci")
    ordered = sorted(panel, key=lambda item: int(item["ordinal"]))
    expected_states = ["LONG" if i % 2 else "SHORT" for i in range(1, 29)]
    if [item["state"] for item in ordered] != expected_states:
        raise RuntimeError("panel does not alternate LONG/SHORT")


def read_panel() -> tuple[list[dict[str, object]], dict[str, dict[str, str]], dict[str, str]]:
    found_hashes = {name: sha256(ROOT / name) for name in EXPECTED_HASHES}
    if found_hashes != EXPECTED_HASHES:
        raise RuntimeError(f"input hash mismatch: {found_hashes}")

    panel: list[dict[str, object]] = []
    with ANNOTATIONS.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["page"] != "f69v" or row["unit"] != "X1":
                continue
            match = re.fullmatch(r"f69v\.X1\.(\d+)", row["old_locus"])
            if not match:
                raise RuntimeError(f"bad old locus: {row['old_locus']}")
            ordinal = int(match.group(1))
            state_match = re.search(r"\b(long|short)\b", row["local_comment"].lower())
            if not state_match:
                raise RuntimeError(f"missing state: {row['locus']}")
            panel.append({"ordinal": ordinal, "locus": row["locus"], "state": state_match.group(1).upper()})
    panel.sort(key=lambda item: int(item["ordinal"]))
    validate_panel_contract(panel)
    loci = {str(item["locus"]) for item in panel}

    source_rows: dict[tuple[str, str], list[tuple[int, int, str]]] = defaultdict(list)
    with SURFACE.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["locus"] not in loci or row["edition"] not in EDITIONS:
                continue
            compact_fragment = "".join(row["clean_ascii_fragments"].split())
            if not compact_fragment or not re.fullmatch(r"[a-z]+", compact_fragment):
                raise RuntimeError(f"non-ASCII or empty source fragment: {row['source_group_id']}")
            source_rows[(row["locus"], row["edition"])].append(
                (int(row["source_group_index"]), int(row["source_group_count"]), compact_fragment)
            )
    surfaces: dict[str, dict[str, str]] = {edition: {} for edition in EDITIONS}
    group_counts: dict[str, dict[str, int]] = {edition: {} for edition in EDITIONS}
    for locus in sorted(loci):
        for edition in EDITIONS:
            rows = sorted(source_rows[(locus, edition)])
            if not rows:
                raise RuntimeError(f"missing surface rows: {edition} {locus}")
            declared = {row[1] for row in rows}
            if declared != {len(rows)} or [row[0] for row in rows] != list(range(1, len(rows) + 1)):
                raise RuntimeError(f"bad source group coverage: {edition} {locus}")
            surfaces[edition][locus] = "".join(row[2] for row in rows)
            group_counts[edition][locus] = len(rows)

    sta_sequences: dict[str, str] = {}
    with STA.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["locus"] not in loci:
                continue
            if row["locus"] in sta_sequences:
                raise RuntimeError(f"duplicate STA locus: {row['locus']}")
            if not re.fullmatch(r"[A-Z]+", row["family_sequence"]):
                raise RuntimeError(f"bad STA sequence: {row['locus']}")
            sta_sequences[row["locus"]] = row["family_sequence"]
    if set(sta_sequences) != loci:
        raise RuntimeError("STA locus set mismatch")

    for edition in EDITIONS:
        surfaces[edition]["__GROUP_COUNTS__"] = json.dumps(group_counts[edition], sort_keys=True)
    return panel, surfaces, sta_sequences


def add_binary(features: dict[str, np.ndarray], name: str, values: np.ndarray) -> None:
    features[name] = values.astype(np.float64)


def pairs(mode: str) -> tuple[np.ndarray, np.ndarray]:
    long_idx = np.arange(0, 28, 2, dtype=np.int64)
    if mode == "FORWARD":
        short_idx = np.arange(1, 28, 2, dtype=np.int64)
    elif mode == "BACKWARD":
        short_idx = (long_idx - 1) % 28
    else:
        raise ValueError(mode)
    if sorted(np.concatenate([long_idx, short_idx]).tolist()) != list(range(28)):
        raise RuntimeError(f"invalid {mode} partition")
    return long_idx, short_idx


def has_paired_null_variance(matrix: np.ndarray) -> bool:
    for mode in ("FORWARD", "BACKWARD"):
        long_idx, short_idx = pairs(mode)
        diffs = matrix[:, long_idx] - matrix[:, short_idx]
        if not (np.abs(diffs).sum(axis=1) > 0).all():
            return False
    return True


def build_features(
    panel: list[dict[str, object]], surfaces: dict[str, dict[str, str]], sta_sequences: dict[str, str]
) -> tuple[list[str], np.ndarray, dict[str, list[str]], dict[str, str], int, int]:
    loci = [str(item["locus"]) for item in panel]
    surface_matrix = [[surfaces[e][locus] for locus in loci] for e in EDITIONS]
    group_counts = [json.loads(surfaces[e]["__GROUP_COUNTS__"]) for e in EDITIONS]
    features: dict[str, np.ndarray] = {}

    features["SURF_SCALAR:COMPACT_LENGTH"] = np.array(
        [[len(value) for value in row] for row in surface_matrix], dtype=np.float64
    )
    features["SURF_SCALAR:SOURCE_GROUP_COUNT"] = np.array(
        [[group_counts[eidx][locus] for locus in loci] for eidx in range(len(EDITIONS))], dtype=np.float64
    )
    chars = sorted({char for row in surface_matrix for value in row for char in value})
    bigrams = sorted({value[i : i + 2] for row in surface_matrix for value in row for i in range(len(value) - 1)})
    trigrams = sorted({value[i : i + 3] for row in surface_matrix for value in row for i in range(len(value) - 2)})
    for char in chars:
        counts = np.array([[value.count(char) for value in row] for row in surface_matrix], dtype=np.float64)
        add_binary(features, f"SURF_HAS_CHAR:{char}", counts > 0)
        features[f"SURF_COUNT_CHAR:{char}"] = counts
    for gram in bigrams:
        counts = np.array([[sum(value[i : i + 2] == gram for i in range(len(value) - 1)) for value in row] for row in surface_matrix])
        add_binary(features, f"SURF_HAS_BIGRAM:{gram}", counts > 0)
        features[f"SURF_COUNT_BIGRAM:{gram}"] = counts.astype(np.float64)
    for gram in trigrams:
        add_binary(
            features,
            f"SURF_HAS_TRIGRAM:{gram}",
            np.array([[gram in value for value in row] for row in surface_matrix]),
        )
    for width in range(1, 5):
        prefixes = sorted({value[:width] for row in surface_matrix for value in row if len(value) >= width})
        suffixes = sorted({value[-width:] for row in surface_matrix for value in row if len(value) >= width})
        for value0 in prefixes:
            add_binary(
                features,
                f"SURF_PREFIX{width}:{value0}",
                np.array([[value.startswith(value0) for value in row] for row in surface_matrix]),
            )
        for value0 in suffixes:
            add_binary(
                features,
                f"SURF_SUFFIX{width}:{value0}",
                np.array([[value.endswith(value0) for value in row] for row in surface_matrix]),
            )

    sta_row = [sta_sequences[locus] for locus in loci]
    sta_matrix = [sta_row, sta_row, sta_row]
    families = sorted({char for value in sta_row for char in value})
    sta_bigrams = sorted({value[i : i + 2] for value in sta_row for i in range(len(value) - 1)})
    sta_trigrams = sorted({value[i : i + 3] for value in sta_row for i in range(len(value) - 2)})
    for family in families:
        counts = np.array([[value.count(family) for value in row] for row in sta_matrix], dtype=np.float64)
        add_binary(features, f"STA_HAS_FAMILY:{family}", counts > 0)
        features[f"STA_COUNT_FAMILY:{family}"] = counts
    for gram in sta_bigrams:
        counts = np.array([[sum(value[i : i + 2] == gram for i in range(len(value) - 1)) for value in row] for row in sta_matrix])
        add_binary(features, f"STA_HAS_BIGRAM:{gram}", counts > 0)
        features[f"STA_COUNT_BIGRAM:{gram}"] = counts.astype(np.float64)
    for gram in sta_trigrams:
        add_binary(features, f"STA_HAS_TRIGRAM:{gram}", np.array([[gram in value for value in row] for row in sta_matrix]))
    for width in range(1, 4):
        prefixes = sorted({value[:width] for value in sta_row if len(value) >= width})
        suffixes = sorted({value[-width:] for value in sta_row if len(value) >= width})
        for value0 in prefixes:
            add_binary(
                features,
                f"STA_PREFIX{width}:{value0}",
                np.array([[value.startswith(value0) for value in row] for row in sta_matrix]),
            )
        for value0 in suffixes:
            add_binary(
                features,
                f"STA_SUFFIX{width}:{value0}",
                np.array([[value.endswith(value0) for value in row] for row in sta_matrix]),
            )

    collapsed: dict[bytes, list[str]] = defaultdict(list)
    for name, matrix in features.items():
        if matrix.shape != (3, 28) or not np.isfinite(matrix).all():
            raise RuntimeError(f"invalid feature matrix: {name}")
        collapsed[np.ascontiguousarray(matrix.astype("<f8")).tobytes()].append(name)

    names: list[str] = []
    matrices: list[np.ndarray] = []
    aliases: dict[str, list[str]] = {}
    kinds: dict[str, str] = {}
    for raw, alias_names in collapsed.items():
        alias_names.sort()
        name = alias_names[0]
        matrix = np.frombuffer(raw, dtype="<f8").reshape(3, 28).copy()
        is_binary = bool(np.isin(matrix, [0.0, 1.0]).all())
        if is_binary:
            supports = matrix.sum(axis=1)
            eligible = bool(((supports >= 6) & (supports <= 22)).all())
        else:
            eligible = bool((matrix.std(axis=1, ddof=0) > 0).all())
        eligible = eligible and has_paired_null_variance(matrix)
        if not eligible:
            continue
        names.append(name)
        matrices.append(matrix)
        aliases[name] = alias_names
        kinds[name] = "BINARY" if is_binary else "COUNT_OR_SCALAR"
    order = np.argsort(np.array(names, dtype=object))
    ordered_names = [names[i] for i in order]
    ordered_matrix = np.stack([matrices[i] for i in order], axis=0)
    ordered_aliases = {name: aliases[name] for name in ordered_names}
    ordered_kinds = {name: kinds[name] for name in ordered_names}
    return ordered_names, ordered_matrix, ordered_aliases, ordered_kinds, len(features), len(collapsed)


def signs() -> np.ndarray:
    worlds = np.arange(1 << 14, dtype=np.uint16)[:, None]
    bits = (worlds >> np.arange(14, dtype=np.uint16)[None, :]) & 1
    return (1.0 - 2.0 * bits.astype(np.float64)).astype(np.float64)


def score_orbit(matrix: np.ndarray, mode: str) -> dict[str, object]:
    long_idx, short_idx = pairs(mode)
    diffs = matrix[:, :, long_idx] - matrix[:, :, short_idx]
    orbit_effects = np.einsum("wp,fep->wfe", signs(), diffs, optimize=False) / 14.0
    null_sd = orbit_effects.std(axis=0, ddof=0)
    if not np.isfinite(orbit_effects).all() or not np.isfinite(null_sd).all() or not (null_sd > 0).all():
        raise RuntimeError(f"nonfinite/zero null SD in {mode}")
    z = orbit_effects / null_sd[None, :, :]
    coherent = ((z > 0).all(axis=2)) | ((z < 0).all(axis=2))
    feature_scores = np.where(coherent, np.min(np.abs(z), axis=2), 0.0)
    maxima = feature_scores.max(axis=1)
    observed_scores = feature_scores[0]
    observed_max = float(maxima[0])
    top_indices = np.flatnonzero(np.abs(observed_scores - observed_max) <= TOL)
    p_value = float(np.count_nonzero(maxima >= observed_max - TOL) / len(maxima))
    return {
        "mode": mode,
        "long_indices_0based": long_idx.tolist(),
        "short_indices_0based": short_idx.tolist(),
        "diffs": diffs,
        "observed_effects": orbit_effects[0],
        "observed_z": z[0],
        "observed_scores": observed_scores,
        "observed_max": observed_max,
        "top_indices": top_indices.tolist(),
        "p_value": p_value,
        "inclusive_extreme_count": int(np.count_nonzero(maxima >= observed_max - TOL)),
        "null_sd": null_sd,
        "null_maxima": maxima,
    }


def robustness(matrix: np.ndarray, index: int, mode: str) -> dict[str, object]:
    long_idx, short_idx = pairs(mode)
    feature_matrix = matrix[index]
    diffs = feature_matrix[:, long_idx] - feature_matrix[:, short_idx]
    effect = diffs.mean(axis=1)
    direction = np.sign(effect)
    loo = np.stack([(np.delete(diffs, j, axis=1)).mean(axis=1) for j in range(14)], axis=0)
    loo_direction_ok = bool(((loo * direction[None, :]) > 0).all())
    denom = np.abs(diffs).sum(axis=1)
    concentration = np.divide(np.abs(diffs).max(axis=1), denom, out=np.full(3, np.inf), where=denom > 0)
    return {
        "loo_effects_sha256": array_sha(loo),
        "loo_direction_ok": loo_direction_ok,
        "max_pair_contribution_fraction": [float(x) for x in concentration],
        "concentration_ok": bool((concentration <= 0.35 + TOL).all()),
    }


def synthetic_controls() -> dict[str, object]:
    base = np.zeros((1, 3, 28), dtype=np.float64)
    base[:, :, 0::2] = 1.0
    planted = {mode: score_orbit(base, mode) for mode in ("FORWARD", "BACKWARD")}
    planted_robust = {mode: robustness(base, 0, mode) for mode in ("FORWARD", "BACKWARD")}

    concentrated = np.zeros((1, 3, 28), dtype=np.float64)
    concentrated[:, :, 0] = 1.0
    concentration_flags = {mode: robustness(concentrated, 0, mode)["concentration_ok"] for mode in ("FORWARD", "BACKWARD")}

    one_reading = base.copy()
    one_reading[:, 1, :] = np.roll(one_reading[:, 1, :], 1, axis=1)
    one_reading[:, 2, :] = np.roll(one_reading[:, 2, :], 2, axis=1)
    one_reading_scores = {mode: score_orbit(one_reading, mode)["observed_max"] for mode in ("FORWARD", "BACKWARD")}

    tie_rejected = False
    try:
        score_orbit(np.zeros((2, 3, 28), dtype=np.float64), "FORWARD")
    except RuntimeError:
        tie_rejected = True

    malformed = [
        {"ordinal": i, "locus": f"synthetic.{i}", "state": "LONG" if i % 2 else "SHORT"}
        for i in range(1, 29)
    ]
    malformed[-1] = dict(malformed[-2])
    malformed_duplicate_rejected = False
    try:
        validate_panel_contract(malformed)
    except RuntimeError:
        malformed_duplicate_rejected = True

    return {
        "planted_p_values": {mode: planted[mode]["p_value"] for mode in planted},
        "planted_scores": {mode: planted[mode]["observed_max"] for mode in planted},
        "planted_robustness": planted_robust,
        "one_reading_only_scores": one_reading_scores,
        "concentration_control_passes_concentration_gate": concentration_flags,
        "tie_zero_variance_control_rejected": tie_rejected,
        "malformed_duplicate_ordinal_control_rejected": malformed_duplicate_rejected,
        "passes": bool(
            all(planted[mode]["p_value"] <= 0.01 for mode in planted)
            and all(planted[mode]["observed_max"] >= 2.5 for mode in planted)
            and all(planted_robust[mode]["loo_direction_ok"] and planted_robust[mode]["concentration_ok"] for mode in planted)
            and all(one_reading_scores[mode] == 0.0 for mode in one_reading_scores)
            and not any(concentration_flags.values())
            and tie_rejected
            and malformed_duplicate_rejected
        ),
    }


def main() -> int:
    if OUT_JSON.exists() or OUT_MD.exists():
        raise RuntimeError("result artifact already exists")
    panel, surfaces, sta_sequences = read_panel()
    names, matrix, aliases, kinds, raw_feature_count, collapsed_feature_count = build_features(panel, surfaces, sta_sequences)
    if not names or matrix.shape[1:] != (3, 28):
        raise RuntimeError("empty/invalid eligible matrix")
    scored = {mode: score_orbit(matrix, mode) for mode in ("FORWARD", "BACKWARD")}
    top_names_by_pairing = {
        mode: [names[i] for i in scored[mode]["top_indices"]]
        for mode in ("FORWARD", "BACKWARD")
    }
    common_top_names = sorted(set(top_names_by_pairing["FORWARD"]) & set(top_names_by_pairing["BACKWARD"]))
    primary_name = common_top_names[0] if common_top_names else top_names_by_pairing["FORWARD"][0]
    primary_index = names.index(primary_name)
    observed_effects = np.asarray(scored["FORWARD"]["observed_effects"])[primary_index]
    observed_z_by_pairing = {
        mode: np.asarray(scored[mode]["observed_z"])[primary_index]
        for mode in ("FORWARD", "BACKWARD")
    }
    direction = "LONG_POSITIVE" if (observed_effects > 0).all() else "SHORT_POSITIVE" if (observed_effects < 0).all() else "INCOHERENT"
    if kinds[primary_name] == "BINARY":
        material_values = np.abs(observed_effects)
        material_ok = bool((material_values >= 0.35 - TOL).all())
        material_metric = "ABSOLUTE_PROPORTION_DIFFERENCE"
    else:
        scale = matrix[primary_index].std(axis=1, ddof=0)
        material_values = np.divide(np.abs(observed_effects), scale)
        material_ok = bool((material_values >= 0.75 - TOL).all())
        material_metric = "ALL_28_POPULATION_SD_STANDARDIZED_DIFFERENCE"
    robust = {mode: robustness(matrix, primary_index, mode) for mode in ("FORWARD", "BACKWARD")}
    controls = synthetic_controls()

    gates = {
        "input_and_panel_contract": True,
        "finite_nonzero_nulls": True,
        "unique_common_top_feature": (
            len(common_top_names) == 1
            and top_names_by_pairing["FORWARD"] == common_top_names
            and top_names_by_pairing["BACKWARD"] == common_top_names
            and direction != "INCOHERENT"
        ),
        "maxT_p_le_0_01_both_pairings": all(scored[mode]["p_value"] <= 0.01 + TOL for mode in scored),
        "common_z_ge_2_5_both_pairings": all(
            np.min(np.abs(observed_z_by_pairing[mode])) >= 2.5 - TOL
            for mode in observed_z_by_pairing
        ),
        "material_raw_effect": material_ok,
        "all_loo_directions": all(robust[mode]["loo_direction_ok"] for mode in robust),
        "pair_concentration_le_0_35": all(robust[mode]["concentration_ok"] for mode in robust),
        "synthetic_controls": bool(controls["passes"]),
        "independent_validation": False,
    }
    scientific_pass = all(value for key, value in gates.items() if key != "independent_validation")
    decision = (
        "PROVISIONAL_F69V_LONG_SHORT_FEATURE_LEAD_REQUIRES_VALIDATION_AND_REPLICATION"
        if scientific_pass
        else "PROVISIONAL_EXPLORATORY_NONCONFIRMATION_PENDING_VALIDATION"
    )
    result = {
        "experiment": "F69LS001",
        "status": decision,
        "inputs": {**EXPECTED_HASHES, str(METHOD.relative_to(ROOT)): sha256(METHOD), str(Path(__file__).relative_to(ROOT)): sha256(Path(__file__))},
        "panel": panel,
        "editions": list(EDITIONS),
        "raw_feature_count_before_collapse": raw_feature_count,
        "collapsed_feature_count_before_eligibility": collapsed_feature_count,
        "eligible_collapsed_feature_count": len(names),
        "eligible_feature_names_sha256": canonical_sha(names),
        "eligible_matrix_sha256": array_sha(matrix),
        "primary_feature": primary_name,
        "primary_aliases": aliases[primary_name],
        "primary_kind": kinds[primary_name],
        "top_names_by_pairing": top_names_by_pairing,
        "common_top_names": common_top_names,
        "direction": direction,
        "observed_effects": {edition: float(value) for edition, value in zip(EDITIONS, observed_effects)},
        "observed_z_by_pairing": {
            mode: {edition: float(value) for edition, value in zip(EDITIONS, observed_z_by_pairing[mode])}
            for mode in observed_z_by_pairing
        },
        "material_metric": material_metric,
        "material_values": {edition: float(value) for edition, value in zip(EDITIONS, material_values)},
        "pairings": {
            mode: {
                "long_indices_0based": scored[mode]["long_indices_0based"],
                "short_indices_0based": scored[mode]["short_indices_0based"],
                "observed_max": scored[mode]["observed_max"],
                "inclusive_extreme_count": scored[mode]["inclusive_extreme_count"],
                "p_value": scored[mode]["p_value"],
                "null_maxima_sha256": array_sha(np.asarray(scored[mode]["null_maxima"])),
                "null_sd_sha256": array_sha(np.asarray(scored[mode]["null_sd"])),
                "robustness": robust[mode],
            }
            for mode in scored
        },
        "controls": controls,
        "gates": gates,
        "scientific_pass_before_validation": scientific_pass,
        "decision": decision,
        "claim_ceiling": "At most a provisional source-native feature association with f69v LONG/SHORT graphical state; no lunar mansion, day, number, length word, language, plaintext, or translation.",
    }
    report = (
        "# F69LS001 f69v LONG/SHORT result\n\n"
        f"Decision: `{decision}`.\n\n"
        f"The exact panel contains 14 LONG and 14 SHORT logs in 14 adjacent pairs. "
        f"After duplicate collapse, {len(names)} complete source-native surface/STA features were eligible. "
        f"The top feature is `{primary_name}` ({direction}); aliases: {', '.join(aliases[primary_name])}.\n\n"
        f"ZL3b/IT2a/RF1b effects are " + ", ".join(f"{x:+.6f}" for x in observed_effects) +
        "; FORWARD standardized values are "
        + ", ".join(f"{x:+.6f}" for x in observed_z_by_pairing["FORWARD"])
        + "; BACKWARD standardized values are "
        + ", ".join(f"{x:+.6f}" for x in observed_z_by_pairing["BACKWARD"])
        + ". "
        f"FORWARD maxT p={scored['FORWARD']['p_value']:.6f} "
        f"({scored['FORWARD']['inclusive_extreme_count']}/16384); "
        f"BACKWARD maxT p={scored['BACKWARD']['p_value']:.6f} "
        f"({scored['BACKWARD']['inclusive_extreme_count']}/16384).\n\n"
        "Gates: " + ", ".join(f"{key}={value}" for key, value in gates.items()) + ".\n\n"
        "This complete exploratory feature test cannot identify lunar mansions, days, numbers, a length word, language, plaintext, or translation. "
        "A positive result would still require an independently selected graphical replication.\n"
    )
    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(report, encoding="utf-8")
    print(json.dumps({"decision": decision, "feature": primary_name, "p_forward": scored["FORWARD"]["p_value"], "p_backward": scored["BACKWARD"]["p_value"], "gates": gates}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
