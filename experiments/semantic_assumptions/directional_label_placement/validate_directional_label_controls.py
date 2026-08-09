#!/usr/bin/env python3
"""Independent nonimporting prescore validator for DIRECTIONPLACEMENT001."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "experiments/semantic_assumptions/directional_label_placement"
CONTROL = BASE / "CONTROL_RESULT.json"
OUTPUT = BASE / "CONTROL_VALIDATION.json"
TARGET = BASE / "TARGET_RESULT.json"
DESIGN = BASE / "SOURCE_AND_METHOD_FREEZE.md"
PANEL = BASE / "MASKED_PAIR_PANEL.tsv"
PAIR_AUDIT = BASE / "PAIRING_AUDIT.json"
INTERLINEAR = ROOT / "experiments/semantic_assumptions/results/pre_grounding_interlinear.tsv"
RUNNER = BASE / "run_directional_label_placement.py"
EDITIONS = ("ZL3b", "IT2a", "RF1b")
VIEWS = ("LENGTH_ADJUSTED", "RAW")
HEADER = [
    "pair_id", "side", "physical_folio", "page", "stratum_id",
    "source_locus", "normalized_code", "object_tags", "readings",
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path: Path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def panel_valid(panel: list[dict[str, str]]) -> bool:
    if not panel or list(panel[0]) != HEADER or len(panel) != 32:
        return False
    if len({row["source_locus"] for row in panel}) != 32:
        return False
    groups = defaultdict(list)
    for row in panel:
        if row.get("class") is not None or row["readings"] != "IT2a;RF1b;ZL3b":
            return False
        groups[row["pair_id"]].append(row)
    if len(groups) != 16 or len({row["physical_folio"] for row in panel}) != 6:
        return False
    for pair_id, members in groups.items():
        if Counter(row["side"] for row in members) != {"A": 1, "B": 1}:
            return False
        for field in ("physical_folio", "page", "stratum_id", "normalized_code", "object_tags"):
            if len({row[field] for row in members}) != 1:
                return False
        if not pair_id.startswith(members[0]["stratum_id"] + "|P"):
            return False
    return True


def token_marks(domain: str, token: str) -> set[str]:
    if domain == "LIT":
        marks = {f"LIT_TOKEN:{token}"}
        for width in (2, 3, 4):
            if len(token) > width:
                marks.add(f"LIT_PREFIX{width}:{token[:width]}")
                marks.add(f"LIT_SUFFIX{width}:{token[-width:]}")
                for offset in range(1, len(token) - width):
                    marks.add(f"LIT_INFIX{width}:{token[offset:offset + width]}")
        return marks
    atoms = token.split("+")
    marks = {
        f"{domain}_TOKEN:{token}",
        f"{domain}_PREFIX:{atoms[0]}",
        f"{domain}_SUFFIX:{atoms[-1]}",
    }
    marks |= {f"{domain}_ATOM:{atom}" for atom in atoms}
    marks |= {
        f"{domain}_BIGRAM:{atoms[index]}+{atoms[index + 1]}"
        for index in range(len(atoms) - 1)
    }
    return marks


def domain_tokens(row: dict[str, str], domain: str):
    column = {"LIT": "surface", "ROOT": "root_sequence", "ROLE": "role_sequence"}[domain]
    output = []
    for token in row[column].split():
        size = len(token) if domain == "LIT" else len(token.split("+"))
        output.append((token, size, token_marks(domain, token)))
    return output


def rebuild(panel: list[dict[str, str]]):
    loci = [row["source_locus"] for row in panel]
    meta = {row["source_locus"]: row for row in panel}
    selected = [row for row in rows(INTERLINEAR) if row["locus"] in set(loci)]
    keyed = defaultdict(list)
    for row in selected:
        keyed[(row["edition"], row["locus"])].append(row)
    expected = {(edition, locus) for edition in EDITIONS for locus in loci}
    row_contract = (
        set(keyed) == expected
        and len(selected) == 96
        and all(len(value) == 1 for value in keyed.values())
        and all(
            row["page"] == meta[row["locus"]]["page"]
            and row["code"] == meta[row["locus"]]["normalized_code"]
            and row["grammar_scope"] == "DIAGNOSTIC_NONPROSE"
            and row["kind"] == "L"
            and len(row["surface"].split()) == len(row["root_sequence"].split()) == len(row["role_sequence"].split()) > 0
            for row in selected
        )
    )
    if not row_contract:
        raise ValueError("independent interlinear row contract failed")

    inventory = {edition: defaultdict(lambda: [0, set(), set()]) for edition in EDITIONS}
    token_cache = {}
    for edition in EDITIONS:
        for locus in loci:
            row = keyed[(edition, locus)][0]
            folio = meta[locus]["physical_folio"]
            for domain in ("LIT", "ROOT", "ROLE"):
                tokens = domain_tokens(row, domain)
                token_cache[(edition, locus, domain)] = tokens
                for token, _, marks in tokens:
                    for mark in marks:
                        inventory[edition][mark][0] += 1
                        inventory[edition][mark][1].add(folio)
                        inventory[edition][mark][2].add(token)
    common = set.intersection(*(set(inventory[edition]) for edition in EDITIONS))
    supported = []
    for mark in sorted(common):
        if any(inventory[edition][mark][0] < 4 or len(inventory[edition][mark][1]) < 4 for edition in EDITIONS):
            continue
        if mark.startswith(("LIT_PREFIX", "LIT_SUFFIX", "LIT_INFIX")) and any(
            len(inventory[edition][mark][2]) < 3 for edition in EDITIONS
        ):
            continue
        supported.append(mark)

    raw = {}
    adjusted = {}
    for edition in EDITIONS:
        raw_matrix = np.zeros((32, len(supported)))
        adjusted_matrix = np.zeros_like(raw_matrix)
        length_total = defaultdict(Counter)
        length_mark = defaultdict(Counter)
        for locus in loci:
            for domain in ("LIT", "ROOT", "ROLE"):
                for _, size, marks in token_cache[(edition, locus, domain)]:
                    length_total[domain][size] += 1
                    for mark in marks & set(supported):
                        length_mark[mark][size] += 1
        for row_index, locus in enumerate(loci):
            for column, mark in enumerate(supported):
                domain = mark.split("_", 1)[0]
                tokens = token_cache[(edition, locus, domain)]
                observed = sum(mark in marks for _, _, marks in tokens)
                local_lengths = Counter(size for _, size, _ in tokens)
                expected_count = sum(
                    count * length_mark[mark][size] / length_total[domain][size]
                    for size, count in local_lengths.items()
                )
                raw_matrix[row_index, column] = observed / len(tokens)
                adjusted_matrix[row_index, column] = (observed - expected_count) / len(tokens)
        raw[edition] = raw_matrix
        adjusted[edition] = adjusted_matrix

    pair_ids = list(dict.fromkeys(row["pair_id"] for row in panel))
    pair_indices = []
    pair_folios = []
    for pair_id in pair_ids:
        side_index = {row["side"]: index for index, row in enumerate(panel) if row["pair_id"] == pair_id}
        pair_indices.append((side_index["A"], side_index["B"]))
        pair_folios.append(panel[side_index["A"]]["physical_folio"])
    variable = []
    for column in range(len(supported)):
        okay = True
        for edition in EDITIONS:
            for matrix in (raw[edition], adjusted[edition]):
                if not any(abs(matrix[a, column] - matrix[b, column]) > 1e-14 for a, b in pair_indices):
                    okay = False
        if okay:
            variable.append(column)
    features = [supported[index] for index in variable]
    matrices = {
        "LENGTH_ADJUSTED": {edition: adjusted[edition][:, variable] for edition in EDITIONS},
        "RAW": {edition: raw[edition][:, variable] for edition in EDITIONS},
    }
    return selected, features, matrices, pair_indices, pair_folios


def matrix_hash(features, matrices):
    content = [features]
    for view in VIEWS:
        for edition in EDITIONS:
            content += [view, edition, [[f"{x:.12f}" for x in row] for row in matrices[view][edition]]]
    return hashlib.sha256(json.dumps(content, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def signs_65536():
    output = np.empty((65536, 16), dtype=float)
    for number in range(65536):
        for bit in range(16):
            output[number, bit] = 1.0 if number & (1 << bit) else -1.0
    return output


def score_orbits(matrices, pair_indices, pair_folios, signs):
    counts = Counter(pair_folios)
    coefficients = np.array([1 / (6 * counts[folio]) for folio in pair_folios])
    family = {}
    for view in VIEWS:
        standardized = {}
        for edition in EDITIONS:
            matrix = matrices[view][edition]
            differences = np.array([matrix[a] - matrix[b] for a, b in pair_indices])
            effect = signs @ (differences * coefficients[:, None])
            scale = np.sqrt(np.mean(effect * effect, axis=0))
            z = np.zeros_like(effect)
            active = scale > 1e-14
            z[:, active] = effect[:, active] / scale[active]
            standardized[edition] = z
        stack = np.stack([standardized[edition] for edition in EDITIONS])
        robust = np.maximum(np.min(stack, axis=0), np.min(-stack, axis=0)).clip(min=0)
        family[view] = robust.max(axis=1)
    return coefficients, family


def main() -> None:
    stored = json.loads(CONTROL.read_text())
    panel = rows(PANEL)
    selected, features, matrices, pair_indices, pair_folios = rebuild(panel)
    signs = signs_65536()
    coefficients, family = score_orbits(matrices, pair_indices, pair_folios, signs)
    quantiles = {
        view: {
            name: f"{np.quantile(family[view], value):.12f}"
            for name, value in (("p90", .90), ("p95", .95), ("p99", .99))
        }
        for view in VIEWS
    }
    planted_index = 23117
    planted_diff = signs[planted_index][:, None]
    effect = signs @ (planted_diff * coefficients[:, None])
    scale = np.sqrt(np.mean(effect * effect, axis=0))
    planted = np.abs(effect[:, 0] / scale[0])
    top = planted[planted_index]
    planted_tops = np.flatnonzero(np.abs(planted - top) <= 1e-12).tolist()
    planted_z = effect / scale
    disagreement_stack = np.stack((planted_z, planted_z, -planted_z))
    disagreement = np.maximum(
        np.min(disagreement_stack, axis=0),
        np.min(-disagreement_stack, axis=0),
    ).clip(min=0)

    missing = panel[:-1]
    duplicate = panel + [dict(panel[0])]
    side = [dict(row) for row in panel]
    side[0]["side"] = side[1]["side"]
    page = [dict(row) for row in panel]
    page[0]["page"] = "f999r"
    fixture_lengths = [1, 1, 2, 2]
    fixture_hits = [0, 0, 1, 1]
    totals = Counter(fixture_lengths)
    positives = Counter(length for length, hit in zip(fixture_lengths, fixture_hits) if hit)
    residuals = [hit - positives[length] / totals[length] for length, hit in zip(fixture_lengths, fixture_hits)]

    expected_bindings = {
        "design": sha(DESIGN), "masked_pair_panel": sha(PANEL),
        "pairing_audit": sha(PAIR_AUDIT), "interlinear": sha(INTERLINEAR),
        "runner": sha(RUNNER),
    }
    checks = {
        "bindings": stored["bindings"] == expected_bindings,
        "masked_panel_contract": panel_valid(panel),
        "interlinear_96_rows": len(selected) == 96,
        "feature_list": stored["features"] == features,
        "feature_count_13": stored["feature_count"] == len(features) == 13,
        "feature_domains_4_6_3": stored["feature_domain_counts"] == {"LIT": 4, "ROLE": 6, "ROOT": 3},
        "matrix_hash": stored["matrix_sha256"] == matrix_hash(features, matrices),
        "orbit_65536_unique": stored["assignment_count"] == len(signs) == len({tuple(row) for row in signs}) == 65536,
        "family_quantiles": stored["family_max_quantiles"] == quantiles,
        "planted_complement_tie": stored["planted_top_indices"] == planted_tops == [23117, 42418],
        "inclusive_tail_two": int(np.sum(planted >= top - 1e-12)) == 2,
        "reading_disagreement_zero": np.max(disagreement) == 0,
        "length_fixture_zero": max(abs(value) for value in residuals) == 0,
        "folio_equal_weight": abs(sum(value for value, folio in zip(coefficients, pair_folios) if folio == "f99") - 1/6) < 1e-12,
        "mutated_missing_rejected": not panel_valid(missing),
        "mutated_duplicate_rejected": not panel_valid(duplicate),
        "mutated_side_rejected": not panel_valid(side),
        "mutated_page_rejected": not panel_valid(page),
        "all_registered_assertions_pass": stored["status"] == "PASS" and len(stored["assertions"]) == 15 and all(stored["assertions"].values()),
        "target_unextracted_absent": stored["target_assignment_extracted"] is False and stored["target_result_exists_after"] is False and not TARGET.exists(),
    }
    checks = {name: bool(value) for name, value in checks.items()}
    payload = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks_passed": sum(checks.values()),
        "checks_total": len(checks),
        "checks": checks,
        "control_result_sha256": sha(CONTROL),
        "matrix_sha256": matrix_hash(features, matrices),
        "target_authorized": all(checks.values()) and not TARGET.exists(),
    }
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
