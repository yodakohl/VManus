#!/usr/bin/env python3
"""Run target-free production controls for SME001."""

from __future__ import annotations

import hashlib
import json
import math
from collections import Counter
from pathlib import Path

import numpy as np

import sme001_core as core

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
OUT = HERE / "sme001_anonymous_control_result.json"
REPORT = ROOT / "experiments/semantic_assumptions/results/sme001_anonymous_control_report.md"

EDITIONS = core.EDITIONS
PAGES = [
    "s01r", "s01v", "s02r", "s02v", "s03r", "s04r",
    "s05r", "s05v", "s06r", "s06v", "s07r", "s07v",
]
RAY_SHIFTS = [0, 3, 7, 1, 9, 5, 2, 10, 6, 4, 11, 8]
BASE_RAY = ["7", "8", "8", "7", "7", "8", "7", "8", "8", "7", "8", "7"]
TAIL_PAGES = ["s01r", "s01v", "s02r", "s03r", "s04r", "s05r", "s06r", "s06v"]
TAIL_HIGH = [
    {1, 4, 7, 10}, {1, 6, 8, 11}, {2, 5, 7, 12}, {3, 4, 9, 10},
    {1, 2, 8, 9}, {3, 6, 7, 12}, {2, 3, 10, 11}, {4, 5, 8, 9},
]
BASE_FEATURES = [
    "PARA_WORD_COUNT",
    "FORMAL_PLANTED_RAY",
    "ROOT_ATOM_RATE__PLANTED_TAIL",
    "NULL_A", "NULL_B", "NULL_C",
    "PARITY_ONLY_RAY", "EARLY_ONLY_RAY",
    "PAGE_CONSTANT", "BIFOLIO_CONSTANT", "ONE_FOLIO_RAY",
    "READING_DISAGREEMENT_RAY",
    "ROOT_ATOM_RATE__LENGTH_ONLY", "CONSTANT",
    "ROOT_ATOM_RATE__NONLINEAR_LENGTH_ONLY",
    "ROOT_ATOM_RATE__NEAR_ZERO_LENGTH_RESIDUAL",
]
FEATURES = BASE_FEATURES + [f"NULL_{index:03d}" for index in range(68)]
TARGET_SPECS = {"RAY_8_MINUS_7": ("7", "8"), "TAIL_2_MINUS_1": ("1", "2")}
EXPECTED_HASHES = {
    "target_source_binding.tsv": "315ea24a10995caaa86a77a5a93ecfc0e666351c1ce6a44b078b08686c1d6f3b",
    "target_source_capacity.json": "e2322d841d4af6ca08737697e5eb32a104dd61178ff9f281e879dc0c5c364d44",
    "target_source_validation.json": "38cc174f38607731005e9a2567eed113d02a47114e8640e2e97fc472ede0a74b",
    "anonymous_paragraph_matrix.tsv": "b246456b181b07e847c6d5a49b959b0346eff6a4c6febb8a543de104c505a26a",
    "anonymous_feature_inventory.json": "088232b431b4b9746bb94a08328cb969fb7c21c6a28cd112286da40d6429fea5",
    "anonymous_matrix_capacity.json": "7043fd8d2f8b6b829a2ecd1724b701d3ab811ad4545434720222e1ad03138828",
    "anonymous_matrix_validation.json": "c5a5bb236dd61ecdf8a76ff05e697b8b3a636aa03145fe019a6348fac74aa3d9",
}
TARGET_ARTIFACTS = [
    HERE / "TARGET_RESULT.json",
    HERE / "SME001_TARGET_RESULT.json",
    HERE / "sme001_target_result.tsv",
    ROOT / "experiments/semantic_assumptions/results/sme001_star_morphology_paragraph_result.md",
    ROOT / "experiments/semantic_assumptions/results/sme001_star_morphology_paragraph_validation.md",
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def noise(feature: str, edition: str, unit: str) -> float:
    payload = f"SME001_CONTROL_NOISE_V1|{feature}|{edition}|{unit}".encode()
    value = int.from_bytes(hashlib.sha256(payload).digest()[:8], "big")
    return 2.0 * value / ((1 << 64) - 1) - 1.0


def build_fixture():
    assert len(FEATURES) == 84 and len(set(FEATURES)) == 84
    unit_ids, pages, folios, ordinals = [], [], [], []
    rays, tails = [], []
    tail_positions = dict(zip(TAIL_PAGES, TAIL_HIGH))
    for page_index, page in enumerate(PAGES):
        shift = RAY_SHIFTS[page_index]
        ray_sequence = BASE_RAY[shift:] + BASE_RAY[:shift]
        for ordinal in range(1, 13):
            unit = f"{page}.S{ordinal:02d}"
            unit_ids.append(unit)
            pages.append(page)
            folios.append(page[:-1])
            ordinals.append(ordinal)
            ray = ray_sequence[ordinal - 1]
            if page == "s01r" and ordinal == 5:
                ray = "6"
            if page == "s02v" and ordinal == 11:
                ray = "9"
            rays.append(ray)
            tail = "2" if ordinal in tail_positions.get(page, set()) else "1"
            if page == "s07r" and ordinal == 12:
                tail = "-"
            tails.append(tail)

    values = np.zeros((len(unit_ids), len(EDITIONS), len(FEATURES)), dtype=np.float64)
    feature_index = {feature: index for index, feature in enumerate(FEATURES)}
    page_index = {page: index + 1 for index, page in enumerate(PAGES)}
    folio_names = sorted(set(folios))
    folio_index = {folio: index + 1 for index, folio in enumerate(folio_names)}
    for row, unit in enumerate(unit_ids):
        ordinal = ordinals[row]
        ray_score = {"7": -1.0, "8": 1.0}.get(rays[row], 0.0)
        tail_score = {"1": -1.0, "2": 1.0}.get(tails[row], 0.0)
        for edition_index, edition in enumerate(EDITIONS):
            word_count = 40.0 + 8.0 * ray_score + ordinal % 3 + edition_index
            values[row, edition_index, feature_index["PARA_WORD_COUNT"]] = word_count
            values[row, edition_index, feature_index["FORMAL_PLANTED_RAY"]] = (
                ray_score + 0.03 * noise("FORMAL_PLANTED_RAY", edition, unit)
            )
            values[row, edition_index, feature_index["ROOT_ATOM_RATE__PLANTED_TAIL"]] = (
                0.15 + 0.08 * tail_score
                + 0.003 * noise("ROOT_ATOM_RATE__PLANTED_TAIL", edition, unit)
            )
            for feature in ("NULL_A", "NULL_B", "NULL_C"):
                values[row, edition_index, feature_index[feature]] = (
                    0.5 + 0.1 * noise(feature, edition, unit)
                )
            values[row, edition_index, feature_index["PARITY_ONLY_RAY"]] = (
                ray_score if ordinal % 2 == 1 else 0.0
            )
            values[row, edition_index, feature_index["EARLY_ONLY_RAY"]] = (
                ray_score if ordinal <= 6 else 0.0
            )
            values[row, edition_index, feature_index["PAGE_CONSTANT"]] = page_index[pages[row]]
            values[row, edition_index, feature_index["BIFOLIO_CONSTANT"]] = folio_index[folios[row]]
            values[row, edition_index, feature_index["ONE_FOLIO_RAY"]] = (
                ray_score if folios[row] == "s01"
                else noise("ONE_FOLIO_RAY", edition, unit)
            )
            values[row, edition_index, feature_index["READING_DISAGREEMENT_RAY"]] = (
                ray_score * (1.0, -1.0, 1.0)[edition_index]
            )
            log_length = math.log1p(word_count)
            values[row, edition_index, feature_index["ROOT_ATOM_RATE__LENGTH_ONLY"]] = log_length / 10.0
            values[row, edition_index, feature_index["CONSTANT"]] = 1.0
            values[row, edition_index, feature_index["ROOT_ATOM_RATE__NONLINEAR_LENGTH_ONLY"]] = log_length ** 2 / 100.0
            values[row, edition_index, feature_index["ROOT_ATOM_RATE__NEAR_ZERO_LENGTH_RESIDUAL"]] = (
                log_length / 10.0 + 1e-6 * ray_score
            )
            for feature in FEATURES[len(BASE_FEATURES):]:
                values[row, edition_index, feature_index[feature]] = (
                    0.5 + 0.1 * noise(feature, edition, unit)
                )

    one_index = feature_index["ONE_FOLIO_RAY"]
    for page in PAGES:
        if page[:-1] == "s01":
            continue
        page_rows = [index for index, value in enumerate(pages) if value == page]
        for edition_index in range(len(EDITIONS)):
            for label in ("7", "8"):
                group = [index for index in page_rows if rays[index] == label]
                mean = float(np.mean(values[group, edition_index, one_index]))
                values[group, edition_index, one_index] -= mean

    expected_rows = list(zip(unit_ids, pages, folios, ordinals))
    return {
        "unit_ids": unit_ids, "pages_by_unit": pages, "folios_by_unit": folios,
        "ordinals": ordinals, "values": values, "features": FEATURES,
        "label_sets": {"RAY_8_MINUS_7": rays, "TAIL_2_MINUS_1": tails},
        "expected_rows": expected_rows,
    }


def find_row(result, target, feature):
    matches = [
        row for row in result["results"]
        if row["target"] == target and row["feature"] == feature
    ]
    assert len(matches) == 1
    return matches[0]


def compact(row):
    return {
        key: row[key] for key in (
            "target", "feature", "eligible", "effects", "z", "direction",
            "null_means", "null_sds", "robust_z", "raw_p", "family_p", "material_effect",
            "common_folio_support_count", "ordinal_residual_material_effect",
            "length_linear_residual_material_effect",
            "length_cubic_residual_material_effect", "statistical_gates",
            "statistical_passes",
        )
    }


def cyclic_pairs(sequence):
    return Counter(zip(sequence, sequence[1:] + sequence[:1]))


def linear_runs(sequence):
    runs = []
    for value in sequence:
        if not runs or runs[-1][0] != value:
            runs.append([value, 1])
        else:
            runs[-1][1] += 1
    return tuple((value, count) for value, count in runs)


def evaluate_ordinal_controls(fixture, page_rotations, folio_rotations):
    templates = {
        "RAY_HUMP": ["8" if 4 <= ordinal <= 9 else "7" for ordinal in range(1, 13)],
        "RAY_QUARTER": ["8" if ordinal in {4, 5, 6, 10, 11, 12} else "7" for ordinal in range(1, 13)],
        "RAY_CUT": ["8" if ordinal in {1, 2, 3, 10, 11, 12} else "7" for ordinal in range(1, 13)],
    }
    features = ["FORMAL_HUMP", "FORMAL_QUARTER", "FORMAL_CUT"]
    labels = {
        target: template * len(PAGES) for target, template in templates.items()
    }
    values = np.zeros((len(fixture["unit_ids"]), len(EDITIONS), len(features)))
    for index, feature in enumerate(features):
        target = ("RAY_HUMP", "RAY_QUARTER", "RAY_CUT")[index]
        signal = np.asarray([1.0 if value == "8" else -1.0 for value in labels[target]])
        values[:, :, index] = signal[:, None]
    kwargs = {
        "unit_ids": fixture["unit_ids"], "pages_by_unit": fixture["pages_by_unit"],
        "folios_by_unit": fixture["folios_by_unit"], "ordinals": fixture["ordinals"],
        "values": values, "features": features, "label_sets": labels,
        "target_specs": {target: ("7", "8") for target in labels},
    }
    page = core.evaluate(**kwargs, rotations=page_rotations, chunk_size=2048)
    folio = core.evaluate(**kwargs, rotations=folio_rotations, chunk_size=2048)
    pairs = [("RAY_HUMP", "FORMAL_HUMP"), ("RAY_QUARTER", "FORMAL_QUARTER"), ("RAY_CUT", "FORMAL_CUT")]
    return page, folio, pairs


def evaluate_shared_folio_control(fixture, page_rotations, folio_rotations):
    phase = {"s01": 0, "s02": 2, "s03": 4, "s04": 6, "s05": 8, "s06": 10, "s07": 1}
    labels = []
    nuisance = np.zeros((len(fixture["unit_ids"]), len(EDITIONS)))
    for index, (page, ordinal) in enumerate(zip(fixture["pages_by_unit"], fixture["ordinals"])):
        shift = phase[page[:-1]]
        sequence = BASE_RAY[shift:] + BASE_RAY[:shift]
        labels.append(sequence[ordinal - 1])
        for edition_index, edition in enumerate(EDITIONS):
            nuisance[index, edition_index] = noise(
                "SHARED_FOLIO", edition, f"{page[:-1]}.S{ordinal:02d}"
            )
    score = np.asarray([1.0 if value == "8" else -1.0 for value in labels])
    rows = []
    for amplitude_index in range(21):
        amplitude = amplitude_index * 0.025
        values = nuisance + amplitude * score[:, None]
        kwargs = {
            "unit_ids": fixture["unit_ids"], "pages_by_unit": fixture["pages_by_unit"],
            "folios_by_unit": fixture["folios_by_unit"], "ordinals": fixture["ordinals"],
            "values": values[:, :, None], "features": ["FORMAL_SHARED_FOLIO"],
            "label_sets": {"RAY_SHARED_FOLIO": labels},
            "target_specs": {"RAY_SHARED_FOLIO": ("7", "8")},
        }
        page = find_row(core.evaluate(**kwargs, rotations=page_rotations, chunk_size=2048), "RAY_SHARED_FOLIO", "FORMAL_SHARED_FOLIO")
        folio = find_row(core.evaluate(**kwargs, rotations=folio_rotations, chunk_size=2048), "RAY_SHARED_FOLIO", "FORMAL_SHARED_FOLIO")
        rows.append({"amplitude": amplitude, "page": compact(page), "folio": compact(folio)})
    return rows


def main() -> None:
    checks = {}

    def check(name, condition):
        checks[name] = bool(condition)

    fixture = build_fixture()
    lengths = {page: 12 for page in PAGES}
    page_folio = {page: page[:-1] for page in PAGES}
    rotations_page = core.make_rotations(PAGES, lengths, 65536)
    rotations_folio = core.make_folio_phase_rotations(PAGES, lengths, page_folio, 65536)
    check("rotation_page_deterministic", np.array_equal(rotations_page, core.make_rotations(PAGES, lengths, 65536)))
    check("rotation_folio_deterministic", np.array_equal(rotations_folio, core.make_folio_phase_rotations(PAGES, lengths, page_folio, 65536)))
    paired_columns = [(PAGES.index(page), PAGES.index(page[:-1] + "v")) for page in PAGES if page.endswith("r") and page[:-1] + "v" in PAGES]
    check("coupled_equal_length_page_phases", all(np.array_equal(rotations_folio[:, left], rotations_folio[:, right]) for left, right in paired_columns))

    kwargs = {key: fixture[key] for key in (
        "unit_ids", "pages_by_unit", "folios_by_unit", "ordinals", "values",
        "features", "label_sets",
    )}
    result_page = core.evaluate(**kwargs, target_specs=TARGET_SPECS, rotations=rotations_page)
    result_folio = core.evaluate(**kwargs, target_specs=TARGET_SPECS, rotations=rotations_folio)

    named_pairs = [
        ("RAY_8_MINUS_7", "FORMAL_PLANTED_RAY"),
        ("TAIL_2_MINUS_1", "ROOT_ATOM_RATE__PLANTED_TAIL"),
        ("RAY_8_MINUS_7", "PARITY_ONLY_RAY"),
        ("RAY_8_MINUS_7", "EARLY_ONLY_RAY"),
        ("RAY_8_MINUS_7", "ONE_FOLIO_RAY"),
        ("RAY_8_MINUS_7", "READING_DISAGREEMENT_RAY"),
        ("RAY_8_MINUS_7", "ROOT_ATOM_RATE__LENGTH_ONLY"),
        ("RAY_8_MINUS_7", "ROOT_ATOM_RATE__NONLINEAR_LENGTH_ONLY"),
        ("RAY_8_MINUS_7", "ROOT_ATOM_RATE__NEAR_ZERO_LENGTH_RESIDUAL"),
    ]
    selected = {}
    for target, feature in named_pairs:
        selected[f"{target}|{feature}"] = {
            "page": compact(find_row(result_page, target, feature)),
            "folio": compact(find_row(result_folio, target, feature)),
        }

    for target, feature in named_pairs[:2]:
        check(
            f"planted_joint_pass_{feature}",
            selected[f"{target}|{feature}"]["page"]["statistical_passes"]
            and selected[f"{target}|{feature}"]["folio"]["statistical_passes"],
        )
    null_features = [feature for feature in FEATURES if feature.startswith("NULL")]
    joint_null = []
    for target in TARGET_SPECS:
        for feature in null_features:
            if (
                find_row(result_page, target, feature)["statistical_passes"]
                and find_row(result_folio, target, feature)["statistical_passes"]
            ):
                joint_null.append([target, feature])
    check("null_family_zero_joint_pass", not joint_null)
    check("parity_gate_rejects", not selected["RAY_8_MINUS_7|PARITY_ONLY_RAY"]["page"]["statistical_gates"]["parity_and_early_late"])
    check("early_late_gate_rejects", not selected["RAY_8_MINUS_7|EARLY_ONLY_RAY"]["page"]["statistical_gates"]["parity_and_early_late"])
    for feature in ("PAGE_CONSTANT", "BIFOLIO_CONSTANT", "CONSTANT"):
        check(
            f"ineligible_{feature}",
            all(not find_row(result, target, feature)["eligible"] for result in (result_page, result_folio) for target in TARGET_SPECS),
        )
    one = selected["RAY_8_MINUS_7|ONE_FOLIO_RAY"]["page"]["statistical_gates"]
    check("one_folio_deletion_rejects", not one["folio_deletions"])
    check("one_folio_support_rejects", not one["folio_support"])
    check("reading_disagreement_rejects", not selected["RAY_8_MINUS_7|READING_DISAGREEMENT_RAY"]["page"]["statistical_gates"]["same_reading_direction"])
    for feature in (
        "ROOT_ATOM_RATE__LENGTH_ONLY", "ROOT_ATOM_RATE__NONLINEAR_LENGTH_ONLY",
        "ROOT_ATOM_RATE__NEAR_ZERO_LENGTH_RESIDUAL",
    ):
        check(
            f"length_gate_rejects_{feature}",
            all(not selected[f"RAY_8_MINUS_7|{feature}"][mode]["statistical_gates"]["root_length_residual"] for mode in ("page", "folio")),
        )
    check("crafted_raw_z_contradiction_rejects", not core.z_matches_raw_direction([-3.0, -4.0, -5.0], core.raw_direction([0.1, 0.2, 0.3])))

    small_page = rotations_page[:16384]
    small_folio = rotations_folio[:16384]
    ray_feature_index = FEATURES.index("FORMAL_PLANTED_RAY")
    one_values = fixture["values"][:, :, ray_feature_index:ray_feature_index + 1]
    invariant = {}
    for mode, rotations in (("page", small_page), ("folio", small_folio)):
        base_kwargs = {
            "unit_ids": fixture["unit_ids"], "pages_by_unit": fixture["pages_by_unit"],
            "folios_by_unit": fixture["folios_by_unit"], "ordinals": fixture["ordinals"],
            "features": ["FORMAL_PLANTED_RAY"],
            "label_sets": {"RAY_8_MINUS_7": fixture["label_sets"]["RAY_8_MINUS_7"]},
        }
        base = find_row(core.evaluate(**base_kwargs, values=one_values, target_specs={"RAY_8_MINUS_7": ("7", "8")}, rotations=rotations), "RAY_8_MINUS_7", "FORMAL_PLANTED_RAY")
        comp = find_row(core.evaluate(**base_kwargs, values=-one_values, target_specs={"RAY_8_MINUS_7": ("7", "8")}, rotations=rotations), "RAY_8_MINUS_7", "FORMAL_PLANTED_RAY")
        rev = find_row(core.evaluate(**base_kwargs, values=one_values, target_specs={"RAY_8_MINUS_7": ("8", "7")}, rotations=rotations), "RAY_8_MINUS_7", "FORMAL_PLANTED_RAY")
        invariant[mode] = {"base": compact(base), "complement": compact(comp), "reversed": compact(rev)}
        for variant, candidate in (("complement", comp), ("reversed", rev)):
            check(f"{mode}_{variant}_effect_reversal", all(abs(candidate["effects"][edition] + base["effects"][edition]) <= 1e-12 for edition in EDITIONS))
            check(f"{mode}_{variant}_robust_invariance", abs(candidate["robust_z"] - base["robust_z"]) <= 1e-12)
            check(f"{mode}_{variant}_tail_invariance", candidate["raw_p"] == base["raw_p"] and candidate["family_p"] == base["family_p"])

    ordinal_page, ordinal_folio, ordinal_pairs = evaluate_ordinal_controls(fixture, small_page, small_folio)
    ordinal_rows = {}
    for target, feature in ordinal_pairs:
        ordinal_rows[f"{target}|{feature}"] = {}
        for mode, result in (("page", ordinal_page), ("folio", ordinal_folio)):
            row = find_row(result, target, feature)
            ordinal_rows[f"{target}|{feature}"][mode] = compact(row)
            check(f"ordinal_{target}_{mode}_raw_material", row["statistical_gates"]["material"])
            check(f"ordinal_{target}_{mode}_rejected", not row["statistical_gates"]["ordinal_residual_material"] and not row["statistical_passes"])

    shared_folio = evaluate_shared_folio_control(fixture, small_page, small_folio)
    check("shared_folio_coupled_p_not_smaller", all(row["folio"]["family_p"] + 1e-12 >= row["page"]["family_p"] for row in shared_folio))
    check("shared_folio_coupled_sd_larger", any(
        row["amplitude"] > 0 and all(
            row["folio"]["null_sds"][edition] > row["page"]["null_sds"][edition]
            for edition in EDITIONS
        ) for row in shared_folio
    ))

    for target, sequence in fixture["label_sets"].items():
        for page in PAGES:
            indices = [index for index, value in enumerate(fixture["pages_by_unit"]) if value == page]
            original = [sequence[index] for index in indices]
            original_counter = Counter(original)
            original_pairs = cyclic_pairs(original)
            for shift in range(12):
                rotated = original[shift:] + original[:shift]
                check(f"{target}_{page}_shift_{shift}_counts", Counter(rotated) == original_counter)
                check(f"{target}_{page}_shift_{shift}_cyclic_pairs", cyclic_pairs(rotated) == original_pairs)
    check("rare_ray_states_present", Counter(fixture["label_sets"]["RAY_8_MINUS_7"])["6"] == 1 and Counter(fixture["label_sets"]["RAY_8_MINUS_7"])["9"] == 1)
    check("rare_tail_state_present", Counter(fixture["label_sets"]["TAIL_2_MINUS_1"])["-"] == 1)
    for page in PAGES:
        indices = [index for index, value in enumerate(fixture["pages_by_unit"]) if value == page]
        original = [
            (fixture["label_sets"]["RAY_8_MINUS_7"][index], fixture["label_sets"]["TAIL_2_MINUS_1"][index])
            for index in indices
        ]
        for shift in range(12):
            rotated = original[shift:] + original[:shift]
            check(f"paired_target_{page}_shift_{shift}_counts", Counter(rotated) == Counter(original))
            check(f"paired_target_{page}_shift_{shift}_cyclic_pairs", cyclic_pairs(rotated) == cyclic_pairs(original))
    check("linear_cut_relocates", linear_runs(BASE_RAY) != linear_runs(BASE_RAY[1:] + BASE_RAY[:1]))
    check("inclusive_tie", (1 + sum(value >= 2.0 - core.TIE_TOL for value in [2.0, 2.0, 1.0, 0.0])) / 5 == 0.6)
    check("strict_tie_differs", (1 + sum(value > 2.0 + core.TIE_TOL for value in [2.0, 2.0, 1.0, 0.0])) / 5 == 0.2)

    expected = fixture["expected_rows"]
    contract_args = [fixture["unit_ids"], fixture["pages_by_unit"], fixture["folios_by_unit"], fixture["ordinals"], fixture["values"], fixture["features"]]
    check("exact_row_contract_accepts", core.exact_matrix_contract(*contract_args, expected))
    for name, position, replacement in (
        ("locus", 0, "changed-locus"),
        ("page", 1, "s99r"),
        ("folio", 2, "s99"),
        ("ordinal", 3, 2),
    ):
        mutated = [list(value) if index < 4 else value.copy() for index, value in enumerate(contract_args)]
        mutated[position][0] = replacement
        check(f"reject_{name}_drift", not core.exact_matrix_contract(*mutated, expected))
    duplicate = [list(value) if index < 4 else value.copy() for index, value in enumerate(contract_args)]
    duplicate[0][1] = duplicate[0][0]
    check("reject_duplicate", not core.exact_matrix_contract(*duplicate, expected))
    missing = [
        list(contract_args[index][:-1]) for index in range(4)
    ] + [fixture["values"][:-1].copy(), list(FEATURES)]
    check("reject_missing", not core.exact_matrix_contract(*missing, expected))
    extra = [list(contract_args[index]) for index in range(4)] + [
        np.concatenate([fixture["values"], fixture["values"][-1:]], axis=0),
        list(FEATURES),
    ]
    extra[0].append("s07v.S13"); extra[1].append("s07v"); extra[2].append("s07"); extra[3].append(13)
    check("reject_extra", not core.exact_matrix_contract(*extra, expected))
    reordered = [list(value) if index < 4 else value.copy() for index, value in enumerate(contract_args)]
    for value in reordered[:4]: value[0], value[1] = value[1], value[0]
    reordered[4][[0, 1]] = reordered[4][[1, 0]]
    check("reject_reordered", not core.exact_matrix_contract(*reordered, expected))
    nonfinite = fixture["values"].copy(); nonfinite[0, 0, 0] = np.nan
    check("reject_nonfinite", not core.matrix_contract(fixture["unit_ids"], fixture["pages_by_unit"], fixture["folios_by_unit"], fixture["ordinals"], nonfinite, FEATURES))
    negative = fixture["values"].copy(); negative[0, 0, FEATURES.index("PARA_WORD_COUNT")] = -1
    try:
        core.evaluate(**{**kwargs, "values": negative}, target_specs=TARGET_SPECS, rotations=rotations_page[:2])
        negative_rejected = False
    except ValueError:
        negative_rejected = True
    check("reject_negative_word_count", negative_rejected)

    actual_hashes = {name: sha(HERE / name) for name in EXPECTED_HASHES}
    check("frozen_hashes", actual_hashes == EXPECTED_HASHES)
    target_absence = {str(path.relative_to(ROOT)): not path.exists() for path in TARGET_ARTIFACTS}
    check("target_artifacts_absent", all(target_absence.values()))

    failures = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "experiment": "SME001",
        "status": "PASS_TARGET_FREE_PRODUCTION_CONTROLS" if not failures else "FAIL_TARGET_FREE_PRODUCTION_CONTROLS",
        "target_join_performed": False,
        "target_files_parsed": False,
        "feature_family_size": len(FEATURES),
        "primary_rotations": 65536,
        "page_rotation_digest": core.rotation_digest(rotations_page),
        "folio_rotation_digest": core.rotation_digest(rotations_folio),
        "checks": checks,
        "check_count": len(checks),
        "failures": failures,
        "selected_rows": selected,
        "joint_null_passing": joint_null,
        "invariance": invariant,
        "ordinal_controls": ordinal_rows,
        "shared_folio_grid": shared_folio,
        "input_hashes": actual_hashes,
        "target_artifact_absence": target_absence,
        "claim_ceiling": "synthetic implementation behavior only; no manuscript association or meaning",
    }
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text("\n".join([
        "# SME001 target-free production controls", "", "## Decision", "",
        ("**PASS — all synthetic production controls passed; the real target remains unjoined.**"
         if not failures else f"**FAIL — {len(failures)} synthetic controls failed; target access remains forbidden.**"),
        "", f"The runner evaluated exactly 84 synthetic features against two targets under 65,536 independent-page and coupled-folio assignments. It performed {len(checks)} deterministic checks. Real source files were read only as opaque bytes for frozen SHA-256 identities; no morphology row was parsed or joined to a feature value.",
        "", ("Failures: none." if not failures else "Failures: " + ", ".join(failures) + "."),
        "", "This is an implementation control, not evidence about the manuscript. It supplies no marker association, function, meaning, lexeme, plaintext, language, or translation.",
        "", "## Reproduction", "", "```bash",
        "./vpy experiments/semantic_assumptions/star_morphology_entry/run_sme001_anonymous_controls.py",
        "```",
    ]) + "\n", encoding="utf-8")
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
