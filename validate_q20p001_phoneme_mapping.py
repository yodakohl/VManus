#!/usr/bin/env python3
"""Independent retained-score validator for Q20P001 (does not import producer)."""

from __future__ import annotations

import csv
import hashlib
import itertools
import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parent
ALIGNMENT = ROOT / "experiments/semantic_assumptions/results/source_sta_group_alignment.tsv"
CORPUS = ROOT / "q20p001_asjp_v21_core40.tsv"
MANIFEST = ROOT / "q20p001_language_manifest.tsv"
RESULT = ROOT / "q20p001_result.json"
FOLDS = ROOT / "q20p001_fold_scores.tsv"
MAPS = ROOT / "q20p001_mappings.tsv"
STABILITY = ROOT / "q20p001_mapping_stability.tsv"
MODULES_FILE = ROOT / "q20p001_module_realizations.tsv"
BASELINES = ROOT / "q20p001_baselines.tsv"
COUNTER = ROOT / "q20p001_counterexamples.tsv"
REPORT = ROOT / "Q20P001_PHONEME_MAPPING_REPORT.md"
RUNNER = ROOT / "run_q20p001_phoneme_mapping.py"
OUT = ROOT / "q20p001_validation.json"

EDITIONS = ("ZL3b", "IT2a", "RF1b")
FOLIOS = tuple(f"f{x}" for x in (*range(103, 109), *range(111, 117)))
TARGETS = ("GEORGIAN", "MINGRELIAN", "LAZ", "SVAN")
CONTROLS = ("ARMENIAN", "CHECHEN", "AVAR", "BASQUE", "TURKISH", "GREEK", "ARABIC_QURANIC", "FINNISH")
LANGUAGES = TARGETS + CONTROLS
MODULES = {"q-": ("D1",), "d-": ("B1",), "s-": ("C2",), "-dy": ("B1", "A2"), "-dal": ("B1", "A3", "B2"), "-dar": ("B1", "A3", "C1")}
ALPHA = 0.5
RANDOM_MAPS = 128


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def canonical_sha(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def seed_for(*parts: object) -> int:
    return int(hashlib.sha256("|".join(map(str, parts)).encode()).hexdigest()[:16], 16)


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def close(left: float, right: float, tolerance: float = 6e-8) -> bool:
    return abs(left - right) <= tolerance


def load_external() -> tuple[dict[str, list[tuple[str, ...]]], dict[str, tuple[str, ...]]]:
    seqs: dict[str, list[tuple[str, ...]]] = defaultdict(list)
    for row in rows(CORPUS):
        if row["language_id"] in LANGUAGES:
            seqs[row["language_id"]].append(tuple(row["phoneme_segments"].split()))
    inv = {row["language_id"]: tuple(row["phoneme_inventory"].split()) for row in rows(MANIFEST) if row["language_id"] in LANGUAGES}
    return seqs, inv


def load_groups() -> list[dict[str, object]]:
    grouped: dict[tuple[str, int], dict[str, dict[str, str]]] = defaultdict(dict)
    with ALIGNMENT.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        for row in reader:
            match = re.match(r"(f\d+)", row["locus"])
            if not match or match.group(1) not in FOLIOS:
                continue
            assert not row["locus"].startswith("f84r")
            grouped[(row["locus"], int(row["source_group_index"]))][row["edition"]] = row
    result = []
    for (locus, group_index), alternatives in sorted(grouped.items()):
        if set(alternatives) != set(EDITIONS):
            continue
        if len({(x["primary_sta_codes"], x["source_group_count"]) for x in alternatives.values()}) != 1:
            continue
        sequence = tuple(alternatives["ZL3b"]["primary_sta_codes"].split())
        result.append({"locus": locus, "folio": re.match(r"(f\d+)", locus).group(1), "group_index": group_index, "codes": sequence})  # type: ignore[union-attr]
    return result


def external_logp(seqs: list[tuple[str, ...]], inv: tuple[str, ...]) -> np.ndarray:
    index = {token: i for i, token in enumerate(inv)}
    m = len(inv)
    counts = np.zeros((m + 1, m + 1, m + 1))
    for sequence in seqs:
        a = b = m
        for token in sequence:
            c = index[token]
            counts[a, b, c] += 1
            a, b = b, c
        counts[a, b, m] += 1
    return -np.log2((counts + ALPHA) / (counts.sum(2, keepdims=True) + ALPHA * (m + 1)))


def mapped_bits(groups: list[dict[str, object]], mapping: dict[str, int], logp: np.ndarray) -> float:
    m = logp.shape[0] - 1
    total = 0.0
    for row in groups:
        a = b = m
        sequence = row["codes"]
        assert isinstance(sequence, tuple)
        for code in sequence:
            c = mapping[code]
            total += float(logp[a, b, c])
            a, b = b, c
        total += float(logp[a, b, m])
    return total


def source_model(groups: list[dict[str, object]], codes: tuple[str, ...]) -> np.ndarray:
    index = {code: i for i, code in enumerate(codes)}
    g = len(codes)
    counts = np.zeros((g + 1, g + 1, g + 1))
    for row in groups:
        a = b = g
        sequence = row["codes"]
        assert isinstance(sequence, tuple)
        for code in sequence:
            c = index[code]
            counts[a, b, c] += 1
            a, b = b, c
        counts[a, b, g] += 1
    return -np.log2((counts + ALPHA) / (counts.sum(2, keepdims=True) + ALPHA * (g + 1)))


def source_bits(groups: list[dict[str, object]], model: np.ndarray, codes: tuple[str, ...]) -> float:
    index = {code: i for i, code in enumerate(codes)}
    g = len(codes)
    total = 0.0
    for row in groups:
        a = b = g
        sequence = row["codes"]
        assert isinstance(sequence, tuple)
        for code in sequence:
            c = index[code]
            total += float(model[a, b, c])
            a, b = b, c
        total += float(model[a, b, g])
    return total


def dictionary_bits(train: list[dict[str, object]], held: list[dict[str, object]], model: np.ndarray, codes: tuple[str, ...]) -> float:
    counts = Counter(row["codes"] for row in train)
    denominator = len(train) + ALPHA * (len(counts) + 1)
    total = 0.0
    for row in held:
        sequence = row["codes"]
        if sequence in counts:
            total += -math.log2((counts[sequence] + ALPHA) / denominator)
        else:
            total += -math.log2(ALPHA / denominator) + source_bits([row], model, codes)
    return total


def pairwise(maps: list[np.ndarray], indices: np.ndarray) -> float:
    return float(np.mean([np.mean(a[indices] == b[indices]) for a, b in itertools.combinations(maps, 2)]))


def main() -> None:
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, detail: str = "") -> None:
        checks.append({"check": name, "passed": bool(passed), "detail": detail})

    check("schema", result["schema"] == "Q20P001_PHONEME_MAPPING_RESULT_V1")
    check("status_vocabulary", result["status"] in {"KARTVELIAN_PHONOTACTIC_ADVANTAGE_SUPPORTED", "KARTVELIAN_PHONOTACTIC_FIT_WEAK_OR_UNSTABLE", "KARTVELIAN_PHONOTACTIC_FIT_NOT_ABOVE_CONTROLS", "INSUFFICIENT_PHONOTACTIC_CAPACITY"})
    input_paths = {ALIGNMENT.name: ALIGNMENT}
    check(
        "input_hashes",
        all((input_paths.get(name, ROOT / name)).exists() and sha(input_paths.get(name, ROOT / name)) == digest for name, digest in result["inputs"].items()),
    )
    check("implementation_hash", result["implementation"] == {RUNNER.name: sha(RUNNER)})
    check("output_hashes", all((ROOT / name).exists() and sha(ROOT / name) == digest for name, digest in result["outputs"].items()))

    groups = load_groups()
    codes = tuple(sorted({code for row in groups for code in row["codes"]}))  # type: ignore[union-attr]
    total_members = sum(len(row["codes"]) for row in groups)  # type: ignore[arg-type]
    counts = Counter(code for row in groups for code in row["codes"])  # type: ignore[union-attr]
    frequent = np.array([i for i, code in enumerate(codes) if counts[code] >= 20])
    check("q20_census", len(groups) == 4671 and len(codes) == 36 and total_members == 19794)
    check("physical_folios", tuple(sorted({row["folio"] for row in groups}, key=lambda x: int(str(x)[1:]))) == FOLIOS)
    check("f84_sealed", all(not str(row["locus"]).startswith("f84r") for row in groups) and result["capacity"]["f84r_rows_retained_joined_or_scored"] == 0)

    seqs, inv = load_external()
    check("language_panel", set(seqs) == set(LANGUAGES) and set(inv) == set(LANGUAGES))
    check("external_capacity", all(len(seqs[x]) >= 39 and 18 <= len(inv[x]) <= 35 for x in LANGUAGES))
    logps = {language: external_logp(seqs[language], inv[language]) for language in LANGUAGES}

    fold_rows = rows(FOLDS)
    map_rows = rows(MAPS)
    baseline_rows = rows(BASELINES)
    stability_rows = rows(STABILITY)
    module_rows = rows(MODULES_FILE)
    check("artifact_row_counts", len(fold_rows) == 144 and len(map_rows) == 5184 and len(stability_rows) == 12 and len(module_rows) == 864 and len(baseline_rows) == 26)

    by_fold_language = {(row["held_folio"], row["language_id"]): row for row in fold_rows}
    maps_by = defaultdict(list)
    for row in map_rows:
        maps_by[(row["held_folio"], row["language_id"])].append(row)
    held_total = Counter()
    symbols_total = Counter()
    random_total = Counter()
    adjusted_total = Counter()
    reconstructed_maps: dict[str, list[np.ndarray]] = defaultdict(list)
    score_errors = []
    random_errors = []
    hash_errors = []
    for folio in FOLIOS:
        train = [row for row in groups if row["folio"] != folio]
        held = [row for row in groups if row["folio"] == folio]
        symbols = sum(len(row["codes"]) for row in held)  # type: ignore[arg-type]
        for language in LANGUAGES:
            record = by_fold_language[(folio, language)]
            entries = sorted(maps_by[(folio, language)], key=lambda row: row["source_sta_code"])
            if [row["source_sta_code"] for row in entries] != list(codes):
                hash_errors.append(f"{folio}:{language}:codes")
                continue
            token_index = {token: i for i, token in enumerate(inv[language])}
            mapping = np.array([token_index[row["mapped_phoneme"]] for row in entries], dtype=np.int16)
            mapping_dict = {code: int(mapping[i]) for i, code in enumerate(codes)}
            expected_hash = canonical_sha({"language": language, "mapping": [[code, inv[language][int(mapping[i])]] for i, code in enumerate(codes)]})
            if expected_hash != record["retained_mapping_hash"] or any(row["mapping_hash"] != expected_hash for row in entries):
                hash_errors.append(f"{folio}:{language}:hash")
            train_bits = mapped_bits(train, mapping_dict, logps[language])
            held_bits = mapped_bits(held, mapping_dict, logps[language])
            if not close(train_bits, float(record["training_phonotactic_bits"])) or not close(held_bits, float(record["held_phonotactic_bits"])):
                score_errors.append(f"{folio}:{language}")
            key = len(codes) * math.log2(len(inv[language]))
            if not close(key, float(record["mapping_key_bits"])):
                score_errors.append(f"{folio}:{language}:key")
            random_scores = []
            for random_index in range(RANDOM_MAPS):
                rng = random.Random(seed_for("Q20P001_RANDOM", language, folio, random_index))
                rm = {code: rng.randrange(len(inv[language])) for code in codes}
                random_scores.append(mapped_bits(held, rm, logps[language]) / symbols)
            random_median = float(np.median(sorted(random_scores)))
            if not close(random_median, float(record["random_map_median_bps"])):
                random_errors.append(f"{folio}:{language}")
            held_total[language] += held_bits
            symbols_total[language] += symbols
            random_total[language] += random_median * symbols
            adjusted_total[language] += held_bits + key
            reconstructed_maps[language].append(mapping)
    check("mapping_hashes", not hash_errors, ";".join(hash_errors[:5]))
    check("retained_train_and_held_scores", not score_errors, ";".join(score_errors[:5]))
    check("random_mapping_medians", not random_errors, ";".join(random_errors[:5]))

    baseline_by = {(row["held_folio"], row["baseline"]): row for row in baseline_rows}
    source_total = dictionary_total = 0.0
    baseline_errors = []
    for folio in FOLIOS:
        train = [row for row in groups if row["folio"] != folio]
        held = [row for row in groups if row["folio"] == folio]
        model = source_model(train, codes)
        sb = source_bits(held, model, codes)
        db = dictionary_bits(train, held, model, codes)
        source_total += sb
        dictionary_total += db
        if not close(sb, float(baseline_by[(folio, "SOURCE_STA_ORDER2_KT")]["held_bits"])) or not close(db, float(baseline_by[(folio, "WHOLE_GROUP_KT_ESCAPE_SOURCE_ORDER2")]["held_bits"])):
            baseline_errors.append(folio)
    check("source_and_group_baselines", not baseline_errors, ";".join(baseline_errors))

    aggregate = {language: held_total[language] / symbols_total[language] for language in LANGUAGES}
    check("aggregate_language_scores", all(close(aggregate[x], result["aggregate"]["language_bits_per_member"][x], 1e-10) for x in LANGUAGES))
    check("aggregate_adjusted_scores", all(close(adjusted_total[x] / symbols_total[x], result["aggregate"]["language_bits_per_member_plus_full_key_each_fold"][x], 1e-10) for x in LANGUAGES))
    check("aggregate_random_scores", all(close(random_total[x] / symbols_total[x], result["aggregate"]["language_random_map_median_bits_per_member"][x], 1e-9) for x in LANGUAGES))
    check("source_baseline_aggregate", close(source_total / total_members, result["aggregate"]["source_sta_order2_kt_bits_per_member"], 1e-10))
    check("dictionary_baseline_aggregate", close(dictionary_total / total_members, result["aggregate"]["whole_group_kt_escape_bits_per_member"], 1e-10))

    target_mean = float(np.mean([aggregate[x] for x in TARGETS]))
    control_mean = float(np.mean([aggregate[x] for x in CONTROLS]))
    effect = target_mean - control_mean
    effects = []
    for subset in itertools.combinations(LANGUAGES, 4):
        rest = tuple(x for x in LANGUAGES if x not in subset)
        effects.append(float(np.mean([aggregate[x] for x in subset]) - np.mean([aggregate[x] for x in rest])))
    p = sum(x <= effect + 1e-12 for x in effects) / len(effects)
    check("family_effect_and_subset_p", close(effect, result["aggregate"]["kartvelian_minus_control_bits_per_member"], 1e-10) and close(p, result["aggregate"]["exact_4_of_12_subset_diagnostic_p"], 1e-12))

    stability_by = {row["language_id"]: row for row in stability_rows}
    stability_errors = []
    for language in LANGUAGES:
        all_agreement = pairwise(reconstructed_maps[language], np.arange(len(codes)))
        frequent_agreement = pairwise(reconstructed_maps[language], frequent)
        if not close(all_agreement, float(stability_by[language]["cross_fold_all_code_exact_agreement"])) or not close(frequent_agreement, float(stability_by[language]["cross_fold_frequent_code_exact_agreement"])):
            stability_errors.append(language)
    check("cross_fold_mapping_stability", not stability_errors, ";".join(stability_errors))

    module_by = {(row["language_id"], row["module"], row["held_folio"]): row for row in module_rows}
    module_errors = []
    for language in LANGUAGES:
        for module, sequence in MODULES.items():
            realizations = []
            for folio, mapping in zip(FOLIOS, reconstructed_maps[language], strict=True):
                realization = " ".join(inv[language][int(mapping[codes.index(code)])] for code in sequence)
                realizations.append(realization)
                if module_by[(language, module, folio)]["mapped_phoneme_sequence"] != realization:
                    module_errors.append(f"{language}:{module}:{folio}")
            mode_count = Counter(realizations).most_common(1)[0][1]
            if any(int(module_by[(language, module, folio)]["modal_fold_count"]) != mode_count for folio in FOLIOS):
                module_errors.append(f"{language}:{module}:mode")
    check("registered_module_realizations", not module_errors, ";".join(module_errors[:5]))

    best_target = min(TARGETS, key=aggregate.get)
    best_control = min(CONTROLS, key=aggregate.get)
    expected_status = "KARTVELIAN_PHONOTACTIC_FIT_NOT_ABOVE_CONTROLS" if target_mean >= control_mean or aggregate[best_control] < min(aggregate[x] for x in TARGETS) else result["status"]
    check("negative_decision", result["status"] == expected_status == "KARTVELIAN_PHONOTACTIC_FIT_NOT_ABOVE_CONTROLS")
    check(
        "counterexamples",
        len(rows(COUNTER)) == 4
        and {row["effect"] for row in rows(COUNTER)}
        >= {"CONTROL_BETTER_THAN_TARGET", "SOURCE_REFERENCE_CODE_LENGTH_LOWER_NOT_DIRECT_LIKELIHOOD_RATIO", "UNSTABLE"},
    )
    report = REPORT.read_text(encoding="utf-8")
    check("report_status_and_ceiling", result["status"] in report and "No output was optimized for recognizable words" in report and "translation" in report)
    check("no_decoded_output_fields", not any(key in row for row in fold_rows for key in ("decoded_word", "translation", "meaning", "gloss")))

    passed = all(item["passed"] for item in checks)
    validation = {
        "schema": "Q20P001_PHONEME_MAPPING_VALIDATION_V1",
        "status": "PASS_INDEPENDENT_RETAINED_SCORE_RECONSTRUCTION" if passed else "FAIL",
        "checks_passed": sum(bool(item["passed"]) for item in checks),
        "checks_total": len(checks),
        "checks": checks,
        "scope": "Independently reconstructs retained mappings, train/held scores, random-map medians, source/group baselines, cross-fold stability, registered module realizations, aggregates, and decision. It does not rerun or certify global optimality of coordinate search.",
        "result_sha256": sha(RESULT),
        "validator_sha256": sha(Path(__file__)),
        "verified_best_target": best_target,
        "verified_best_control": best_control,
        "verified_kartvelian_minus_control_bits_per_member": effect,
        "verified_subset_p": p,
    }
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": validation["status"], "checks": f"{validation['checks_passed']}/{validation['checks_total']}"}, indent=2))
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
