#!/usr/bin/env python3
"""Nonimporting reconstruction of SME001's target-blind paragraph matrix."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
SOURCE = HERE / "source_unit_binding.tsv"
INTER = ROOT / "experiments/semantic_assumptions/results/pre_grounding_interlinear.tsv"
BINDING = HERE / "anonymous_unit_binding.tsv"
FEATURES = HERE / "anonymous_feature_inventory.json"
MATRIX = HERE / "anonymous_paragraph_matrix.tsv"
CAPACITY = HERE / "anonymous_matrix_capacity.json"
OUT = HERE / "anonymous_matrix_validation.json"
REPORT = ROOT / "experiments/semantic_assumptions/results/sme001_anonymous_matrix_validation.md"

EDITIONS = ("ZL3b", "IT2a", "RF1b")
META = ("unit_id", "page", "physical_folio", "star_ordinal", "locus", "edition")
FORBIDDEN = {"vpos", "core", "paint", "color", "rays", "tail", "observation"}
FORMAL = (
    "OPEN_WORD_COUNT", "OPEN_CARRIER_ANY", "OPEN_CARRIER_T", "OPEN_CARRIER_D", "OPEN_CARRIER_S",
    "OPEN_ROLE_RATE_BOUND_D", "OPEN_ROLE_RATE_BOUND_E", "OPEN_ROLE_RATE_Q", "OPEN_ROLE_RATE_REL_I",
    "OPEN_ROLE_RATE_FREE_L", "OPEN_ROLE_RATE_FREE_R", "OPEN_FIRST_HAS_BOUND_D", "OPEN_FIRST_HAS_BOUND_E",
    "OPEN_FIRST_HAS_Q", "OPEN_FIRST_HAS_REL_I", "OPEN_FIRST_HAS_FREE_L", "OPEN_FIRST_HAS_FREE_R",
    "OPEN_EDGE_RATE_D_TO_Q", "OPEN_EDGE_RATE_E_TO_Q", "PARA_LINE_COUNT", "PARA_WORD_COUNT",
    "PARA_MEAN_WORDS_PER_LINE", "PARA_CARRIER_ANY_RATE", "PARA_CARRIER_T_RATE", "PARA_CARRIER_D_RATE",
    "PARA_CARRIER_S_RATE", "PARA_ROLE_RATE_BOUND_D", "PARA_ROLE_RATE_BOUND_E", "PARA_ROLE_RATE_Q",
    "PARA_ROLE_RATE_REL_I", "PARA_ROLE_RATE_FREE_L", "PARA_ROLE_RATE_FREE_R", "PARA_EDGE_RATE_D_TO_Q",
    "PARA_EDGE_RATE_E_TO_Q",
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def seq(locus: str) -> int:
    match = re.fullmatch(r"f\d+[rv]\.(\d+)", locus)
    assert match
    return int(match.group(1))


def role_atoms(text: str) -> list[str]:
    return [part for word in text.split() for part in word.split("+") if part]


def roots(text: str) -> list[str]:
    return [part for word in text.split() for part in word.split("+") if part]


def count_role(text: str, role: str) -> int:
    values = role_atoms(text)
    if role == "Q":
        return sum(value.startswith("Q_") for value in values)
    return values.count(role)


def opening_has(text: str, role: str) -> float:
    values = (text.split()[0] if text.split() else "").split("+")
    if role == "Q":
        return float(any(value.startswith("Q_") for value in values))
    return float(role in values)


def dq_edges(text: str, left: str) -> int:
    answer = 0
    for item in text.split(";"):
        if not item or ">" not in item:
            continue
        pair = item.split(":", 1)[-1]
        before, after = pair.split(">", 1)
        answer += before == left and after.startswith("Q_")
    return answer


def reconstruct_units(source_rows, prose):
    by_page = defaultdict(list)
    for source in source_rows:
        by_page[source["page"]].append({key: source[key] for key in ("page", "physical_folio", "star_ordinal", "locus")})
    admitted, excluded = [], []
    for page in sorted(by_page):
        values = sorted(by_page[page], key=lambda row: int(row["star_ordinal"]))
        starts = [seq(row["locus"]) for row in values]
        for index, value in enumerate(values):
            lo = starts[index]
            hi = starts[index + 1] if index + 1 < len(starts) else 10**9
            locus_sets = {
                edition: tuple(sorted(
                    (locus for locus, row in prose[edition].items() if row["page"] == page and lo <= seq(locus) < hi),
                    key=seq,
                )) for edition in EDITIONS
            }
            assert all(locus_sets[edition] and locus_sets[edition][0] == value["locus"] for edition in EDITIONS)
            assert prose["ZL3b"][locus_sets["ZL3b"][0]]["paragraph_state"] == "OPEN"
            assert all(
                prose["ZL3b"][locus]["paragraph_state"] == "CONT"
                for locus in locus_sets["ZL3b"][1:]
            )
            if len(set(locus_sets.values())) != 1:
                excluded.append((value, locus_sets))
                continue
            unit_id = hashlib.sha256(f"SME001|{page}|{value['star_ordinal']}|{value['locus']}".encode()).hexdigest()[:20]
            admitted.append({**value, "unit_id": unit_id, "line_loci": locus_sets["ZL3b"]})
    return admitted, excluded


def select_roots(admitted, prose, kind):
    selected_by_edition = {}
    details_by_edition = {}
    for edition in EDITIONS:
        occ = Counter()
        parags, pages, folios = defaultdict(set), defaultdict(set), defaultdict(set)
        for unit in admitted:
            values = []
            for locus in unit["line_loci"]:
                text = prose[edition][locus]["root_sequence"]
                values.extend(roots(text) if kind == "atom" else text.split())
            for value, count in Counter(values).items():
                occ[value] += count
                parags[value].add(unit["unit_id"])
                pages[value].add(unit["page"])
                folios[value].add(unit["physical_folio"])
        detail = {
            value: {"occurrences": occ[value], "paragraphs": len(parags[value]), "pages": len(pages[value]), "folios": len(folios[value])}
            for value in occ
        }
        details_by_edition[edition] = detail
        selected_by_edition[edition] = {
            value for value, item in detail.items()
            if item["occurrences"] >= 20 and item["paragraphs"] >= 12 and item["pages"] >= 6 and item["folios"] >= 5
        }
    chosen = sorted(set.intersection(*(selected_by_edition[edition] for edition in EDITIONS)))
    if kind == "word":
        chosen = [value for value in chosen if "+" in value]
    support = {
        value: {edition: details_by_edition[edition][value] for edition in EDITIONS}
        for value in chosen
    }
    return chosen, support


def formal_values(lines):
    opening = lines[0]
    n_open = int(opening["word_count"])
    n_lines = len(lines)
    n_words = sum(int(line["word_count"]) for line in lines)
    carrier = opening["line_carrier"]
    values = [
        n_open, bool(carrier), carrier == "t", carrier == "d", carrier == "s",
        count_role(opening["role_sequence"], "BOUND_D") / n_open,
        count_role(opening["role_sequence"], "BOUND_E") / n_open,
        count_role(opening["role_sequence"], "Q") / n_open,
        count_role(opening["role_sequence"], "REL_I") / n_open,
        count_role(opening["role_sequence"], "FREE_L") / n_open,
        count_role(opening["role_sequence"], "FREE_R") / n_open,
        opening_has(opening["role_sequence"], "BOUND_D"), opening_has(opening["role_sequence"], "BOUND_E"),
        opening_has(opening["role_sequence"], "Q"), opening_has(opening["role_sequence"], "REL_I"),
        opening_has(opening["role_sequence"], "FREE_L"), opening_has(opening["role_sequence"], "FREE_R"),
        dq_edges(opening["confirmed_edges"], "BOUND_D") / n_open,
        dq_edges(opening["confirmed_edges"], "BOUND_E") / n_open,
        n_lines, n_words, n_words / n_lines,
        sum(bool(line["line_carrier"]) for line in lines) / n_lines,
        sum(line["line_carrier"] == "t" for line in lines) / n_lines,
        sum(line["line_carrier"] == "d" for line in lines) / n_lines,
        sum(line["line_carrier"] == "s" for line in lines) / n_lines,
        sum(count_role(line["role_sequence"], "BOUND_D") for line in lines) / n_words,
        sum(count_role(line["role_sequence"], "BOUND_E") for line in lines) / n_words,
        sum(count_role(line["role_sequence"], "Q") for line in lines) / n_words,
        sum(count_role(line["role_sequence"], "REL_I") for line in lines) / n_words,
        sum(count_role(line["role_sequence"], "FREE_L") for line in lines) / n_words,
        sum(count_role(line["role_sequence"], "FREE_R") for line in lines) / n_words,
        sum(dq_edges(line["confirmed_edges"], "BOUND_D") for line in lines) / n_words,
        sum(dq_edges(line["confirmed_edges"], "BOUND_E") for line in lines) / n_words,
    ]
    assert len(values) == len(FORMAL)
    return dict(zip(FORMAL, map(float, values))), n_words


def main() -> None:
    checks = []
    source_rows = read_tsv(SOURCE)
    assert len(source_rows) == 171
    checks.append("source_projection")

    pages = {row["page"] for row in source_rows}
    prose = {edition: {} for edition in EDITIONS}
    for row in read_tsv(INTER):
        if row["page"] in pages and row["grammar_scope"] == "CONFIRMED_PROSE":
            assert len(row["root_sequence"].split()) == int(row["word_count"])
            assert len(row["role_sequence"].split()) == int(row["word_count"])
            prose[row["edition"]][row["locus"]] = row
    admitted, excluded = reconstruct_units(source_rows, prose)
    assert len(admitted) == 170 and len(excluded) == 1
    assert excluded[0][0]["locus"] == "f106r.27"
    assert {edition: len(excluded[0][1][edition]) for edition in EDITIONS} == {"ZL3b": 5, "IT2a": 4, "RF1b": 5}
    checks.append("paragraph_segmentation_and_exclusion")

    stored_binding = read_tsv(BINDING)
    expected_binding = [{
        "unit_id": unit["unit_id"], "page": unit["page"], "physical_folio": unit["physical_folio"],
        "star_ordinal": unit["star_ordinal"], "locus": unit["locus"], "line_loci": "|".join(unit["line_loci"]),
    } for unit in admitted]
    assert stored_binding == expected_binding
    checks.append("anonymous_binding")

    atom_values, atom_support = select_roots(admitted, prose, "atom")
    word_values, word_support = select_roots(admitted, prose, "word")
    assert len(atom_values) == 32 and len(word_values) == 18
    feature_data = json.loads(FEATURES.read_text(encoding="utf-8"))
    assert feature_data["formal_features"] == list(FORMAL)
    assert feature_data["root_atom_features"] == atom_values
    assert feature_data["root_compound_word_features"] == word_values
    assert feature_data["root_support_inventory"] == {"atom": atom_support, "word": word_support}
    checks.append("root_candidate_inventory")

    feature_names = list(FORMAL) + [f"ROOT_ATOM_RATE__{value}" for value in atom_values] + [f"ROOT_WORD_RATE__{value}" for value in word_values]
    assert feature_data["all_features"] == feature_names and len(feature_names) == 84
    stored_matrix = read_tsv(MATRIX)
    assert len(stored_matrix) == 510
    assert not (FORBIDDEN & set(stored_matrix[0])) and not (FORBIDDEN & set(stored_binding[0]))
    checks.append("matrix_schema_and_target_blinding")

    expected_rows = []
    for unit in admitted:
        for edition in EDITIONS:
            lines = [prose[edition][locus] for locus in unit["line_loci"]]
            values, n_words = formal_values(lines)
            atom_counts = Counter(value for line in lines for value in roots(line["root_sequence"]))
            word_counts = Counter(value for line in lines for value in line["root_sequence"].split())
            values.update({f"ROOT_ATOM_RATE__{value}": atom_counts[value] / n_words for value in atom_values})
            values.update({f"ROOT_WORD_RATE__{value}": word_counts[value] / n_words for value in word_values})
            expected_rows.append((unit, edition, values))
    assert len(expected_rows) == len(stored_matrix)
    for stored, (unit, edition, values) in zip(stored_matrix, expected_rows):
        expected_meta = (unit["unit_id"], unit["page"], unit["physical_folio"], unit["star_ordinal"], unit["locus"], edition)
        assert tuple(stored[key] for key in META) == expected_meta
        for feature in feature_names:
            actual = float(stored[feature])
            expected = float(values[feature])
            assert math.isfinite(actual) and abs(actual - expected) <= 5e-12 * max(1.0, abs(expected)), (feature, actual, expected)
    checks.append("all_510_by_84_values")

    capacity = json.loads(CAPACITY.read_text(encoding="utf-8"))
    assert capacity["binding_sha256"] == digest(BINDING)
    assert capacity["feature_inventory_sha256"] == digest(FEATURES)
    assert capacity["matrix_sha256"] == digest(MATRIX)
    assert capacity["features"] == 84 and capacity["matrix_rows"] == 510
    checks.append("artifact_hashes_and_counts")

    for feature, detail in capacity["within_page_variation"].items():
        assert feature in feature_names
        for edition in EDITIONS:
            variable_pages = set()
            for page in sorted(pages):
                vals = {float(row[feature]) for row in stored_matrix if row["edition"] == edition and row["page"] == page}
                if len(vals) >= 2:
                    variable_pages.add(page)
            assert detail[edition] == {"pages": len(variable_pages), "folios": len({page[:-1] for page in variable_pages})}
    checks.append("within_page_variation")

    assert capacity["target_assignment_joined"] is False
    assert capacity["target_result_absent"] is True and not (HERE / "TARGET_RESULT.json").exists()
    checks.append("target_absence")
    assert capacity["claim_ceiling"] == "target-blind paragraph structural and root-feature coverage only"
    checks.append("claim_ceiling")
    assert len(checks) == 10

    payload = {"experiment": "SME001", "status": "PASS_10_CHECK_NONIMPORTING_ANONYMOUS_MATRIX_RECONSTRUCTION", "checks": checks, "matrix_rows": 510, "features": 84, "matrix_sha256": digest(MATRIX), "target_absent": True}
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text("\n".join([
        "# SME001 anonymous matrix validation", "", "**PASS — 10/10 nonimporting checks.**", "",
        "Independent code reconstructs every manual ZL OPEN-then-CONT paragraph span, the sole all-reading physical-line coverage exclusion, anonymous bindings, global-support root inventory, all 510 × 84 stored values, within-page variation, hashes, target absence, and claim ceiling. RF lacks the paragraph-marker metadata and IT omits it at four starts, so neither is counted as independent layout evidence. No morphology field entered the binding or matrix.", "",
        "This validates feature extraction only. It supplies no ray/tail association, root meaning, word meaning, lexeme, plaintext, language, or translation.",
    ]) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
