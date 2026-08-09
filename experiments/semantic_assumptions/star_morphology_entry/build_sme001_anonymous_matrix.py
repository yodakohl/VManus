#!/usr/bin/env python3
"""Build SME001 paragraph features without reading morphology values."""

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
FEATURES_JSON = HERE / "anonymous_feature_inventory.json"
MATRIX = HERE / "anonymous_paragraph_matrix.tsv"
RESULT = HERE / "anonymous_matrix_capacity.json"
REPORT = ROOT / "experiments/semantic_assumptions/results/sme001_anonymous_matrix_capacity.md"

EDITIONS = ("ZL3b", "IT2a", "RF1b")
SOURCE_KEYS = ("page", "physical_folio", "star_ordinal", "locus")
ROOT_MIN_OCCURRENCES = 20
ROOT_MIN_PARAGRAPHS = 12
ROOT_MIN_PAGES = 6
ROOT_MIN_FOLIOS = 5

OPEN_FEATURES = (
    "OPEN_WORD_COUNT", "OPEN_CARRIER_ANY", "OPEN_CARRIER_T", "OPEN_CARRIER_D",
    "OPEN_CARRIER_S", "OPEN_ROLE_RATE_BOUND_D", "OPEN_ROLE_RATE_BOUND_E",
    "OPEN_ROLE_RATE_Q", "OPEN_ROLE_RATE_REL_I", "OPEN_ROLE_RATE_FREE_L",
    "OPEN_ROLE_RATE_FREE_R", "OPEN_FIRST_HAS_BOUND_D", "OPEN_FIRST_HAS_BOUND_E",
    "OPEN_FIRST_HAS_Q", "OPEN_FIRST_HAS_REL_I", "OPEN_FIRST_HAS_FREE_L",
    "OPEN_FIRST_HAS_FREE_R", "OPEN_EDGE_RATE_D_TO_Q", "OPEN_EDGE_RATE_E_TO_Q",
)
PARA_FEATURES = (
    "PARA_LINE_COUNT", "PARA_WORD_COUNT", "PARA_MEAN_WORDS_PER_LINE",
    "PARA_CARRIER_ANY_RATE", "PARA_CARRIER_T_RATE", "PARA_CARRIER_D_RATE",
    "PARA_CARRIER_S_RATE", "PARA_ROLE_RATE_BOUND_D", "PARA_ROLE_RATE_BOUND_E",
    "PARA_ROLE_RATE_Q", "PARA_ROLE_RATE_REL_I", "PARA_ROLE_RATE_FREE_L",
    "PARA_ROLE_RATE_FREE_R", "PARA_EDGE_RATE_D_TO_Q", "PARA_EDGE_RATE_E_TO_Q",
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def line_number(locus: str) -> int:
    match = re.fullmatch(r"f\d+[rv]\.(\d+)", locus)
    assert match
    return int(match.group(1))


def role_atoms(sequence: str) -> list[str]:
    return [atom for word in sequence.split() for atom in word.split("+") if atom]


def root_atoms(sequence: str) -> list[str]:
    return [atom for word in sequence.split() for atom in word.split("+") if atom]


def role_count(sequence: str, name: str) -> int:
    atoms = role_atoms(sequence)
    return sum(atom.startswith("Q_") for atom in atoms) if name == "Q" else atoms.count(name)


def first_has(sequence: str, name: str) -> float:
    word = sequence.split()[0] if sequence.split() else ""
    atoms = [atom for atom in word.split("+") if atom]
    return float(any(atom.startswith("Q_") for atom in atoms)) if name == "Q" else float(name in atoms)


def edge_count(value: str, left: str) -> int:
    total = 0
    for edge in filter(None, value.split(";")):
        roles = edge.split(":", 1)[-1]
        if ">" not in roles:
            continue
        before, after = roles.split(">", 1)
        total += before == left and after.startswith("Q_")
    return total


def source_units() -> list[dict[str, str]]:
    raw = rows(SOURCE)
    units = [{key: row[key] for key in SOURCE_KEYS} for row in raw]
    assert len(units) == 171
    assert len({row["locus"] for row in units}) == 171
    assert all(int(row["star_ordinal"]) >= 1 for row in units)
    return units


def load_prose(units: list[dict[str, str]]) -> dict[str, dict[str, dict[str, str]]]:
    pages = {row["page"] for row in units}
    out: dict[str, dict[str, dict[str, str]]] = {edition: {} for edition in EDITIONS}
    for row in rows(INTER):
        if row["page"] not in pages or row["grammar_scope"] != "CONFIRMED_PROSE":
            continue
        edition = row["edition"]
        assert edition in out
        assert row["locus"] not in out[edition]
        assert len(row["root_sequence"].split()) == int(row["word_count"])
        assert len(row["role_sequence"].split()) == int(row["word_count"])
        out[edition][row["locus"]] = row
    return out


def paragraph_loci(units: list[dict[str, str]], prose: dict[str, dict[str, dict[str, str]]]):
    page_units: dict[str, list[dict[str, str]]] = defaultdict(list)
    for unit in units:
        page_units[unit["page"]].append(unit)
    for page in page_units:
        page_units[page].sort(key=lambda row: int(row["star_ordinal"]))

    admitted: list[dict[str, object]] = []
    excluded: list[dict[str, object]] = []
    for page in sorted(page_units):
        page_rows = page_units[page]
        starts = [line_number(row["locus"]) for row in page_rows]
        assert starts == sorted(starts) and len(starts) == len(set(starts))
        for index, unit in enumerate(page_rows):
            lo = starts[index]
            hi = starts[index + 1] if index + 1 < len(starts) else 10**9
            loci = {}
            for edition in EDITIONS:
                loci[edition] = tuple(sorted(
                    (locus for locus, row in prose[edition].items()
                     if row["page"] == page and lo <= line_number(locus) < hi),
                    key=line_number,
                ))
                assert loci[edition] and loci[edition][0] == unit["locus"]
                if edition == "ZL3b":
                    assert prose[edition][loci[edition][0]]["paragraph_state"] == "OPEN"
                    assert all(
                        prose[edition][locus]["paragraph_state"] == "CONT"
                        for locus in loci[edition][1:]
                    )
            if len(set(loci.values())) != 1:
                excluded.append({
                    **unit,
                    "reason": "ALTERNATE_READING_PHYSICAL_LINE_SET_MISMATCH",
                    "line_counts": {edition: len(loci[edition]) for edition in EDITIONS},
                    "line_sets": {edition: list(loci[edition]) for edition in EDITIONS},
                })
                continue
            unit_id = hashlib.sha256(
                f"SME001|{unit['page']}|{unit['star_ordinal']}|{unit['locus']}".encode()
            ).hexdigest()[:20]
            admitted.append({**unit, "unit_id": unit_id, "line_loci": loci["ZL3b"]})

    assert len(admitted) == 170
    assert len(excluded) == 1
    assert excluded[0]["locus"] == "f106r.27"
    assert excluded[0]["line_counts"] == {"ZL3b": 5, "IT2a": 4, "RF1b": 5}
    return admitted, excluded


def root_inventory(admitted, prose):
    inventory: dict[str, dict[str, dict[str, object]]] = {"atom": {}, "word": {}}
    edition_sets: dict[str, dict[str, set[str]]] = {"atom": {}, "word": {}}
    for kind in ("atom", "word"):
        for edition in EDITIONS:
            occurrences: Counter[str] = Counter()
            paragraphs: dict[str, set[str]] = defaultdict(set)
            pages: dict[str, set[str]] = defaultdict(set)
            folios: dict[str, set[str]] = defaultdict(set)
            for unit in admitted:
                values: list[str] = []
                for locus in unit["line_loci"]:
                    sequence = prose[edition][locus]["root_sequence"]
                    values.extend(root_atoms(sequence) if kind == "atom" else sequence.split())
                for value, count in Counter(values).items():
                    occurrences[value] += count
                    paragraphs[value].add(unit["unit_id"])
                    pages[value].add(unit["page"])
                    folios[value].add(unit["physical_folio"])
            supported = set()
            for value in sorted(occurrences):
                detail = {
                    "occurrences": occurrences[value],
                    "paragraphs": len(paragraphs[value]),
                    "pages": len(pages[value]),
                    "folios": len(folios[value]),
                }
                inventory[kind].setdefault(value, {})[edition] = detail
                if (detail["occurrences"] >= ROOT_MIN_OCCURRENCES
                        and detail["paragraphs"] >= ROOT_MIN_PARAGRAPHS
                        and detail["pages"] >= ROOT_MIN_PAGES
                        and detail["folios"] >= ROOT_MIN_FOLIOS):
                    supported.add(value)
            edition_sets[kind][edition] = supported
    atoms = sorted(set.intersection(*(edition_sets["atom"][edition] for edition in EDITIONS)))
    compound_words = sorted(
        value for value in set.intersection(*(edition_sets["word"][edition] for edition in EDITIONS))
        if "+" in value
    )
    assert len(atoms) == 32
    assert len(compound_words) == 18
    selected_inventory = {
        "atom": {value: inventory["atom"][value] for value in atoms},
        "word": {value: inventory["word"][value] for value in compound_words},
    }
    return atoms, compound_words, selected_inventory


def base_features(lines: list[dict[str, str]]) -> dict[str, float]:
    opening = lines[0]
    n_open = int(opening["word_count"])
    total_words = sum(int(line["word_count"]) for line in lines)
    n_lines = len(lines)
    values = {
        "OPEN_WORD_COUNT": float(n_open),
        "OPEN_CARRIER_ANY": float(bool(opening["line_carrier"])),
        "OPEN_CARRIER_T": float(opening["line_carrier"] == "t"),
        "OPEN_CARRIER_D": float(opening["line_carrier"] == "d"),
        "OPEN_CARRIER_S": float(opening["line_carrier"] == "s"),
        "OPEN_ROLE_RATE_BOUND_D": role_count(opening["role_sequence"], "BOUND_D") / n_open,
        "OPEN_ROLE_RATE_BOUND_E": role_count(opening["role_sequence"], "BOUND_E") / n_open,
        "OPEN_ROLE_RATE_Q": role_count(opening["role_sequence"], "Q") / n_open,
        "OPEN_ROLE_RATE_REL_I": role_count(opening["role_sequence"], "REL_I") / n_open,
        "OPEN_ROLE_RATE_FREE_L": role_count(opening["role_sequence"], "FREE_L") / n_open,
        "OPEN_ROLE_RATE_FREE_R": role_count(opening["role_sequence"], "FREE_R") / n_open,
        "OPEN_FIRST_HAS_BOUND_D": first_has(opening["role_sequence"], "BOUND_D"),
        "OPEN_FIRST_HAS_BOUND_E": first_has(opening["role_sequence"], "BOUND_E"),
        "OPEN_FIRST_HAS_Q": first_has(opening["role_sequence"], "Q"),
        "OPEN_FIRST_HAS_REL_I": first_has(opening["role_sequence"], "REL_I"),
        "OPEN_FIRST_HAS_FREE_L": first_has(opening["role_sequence"], "FREE_L"),
        "OPEN_FIRST_HAS_FREE_R": first_has(opening["role_sequence"], "FREE_R"),
        "OPEN_EDGE_RATE_D_TO_Q": edge_count(opening["confirmed_edges"], "BOUND_D") / n_open,
        "OPEN_EDGE_RATE_E_TO_Q": edge_count(opening["confirmed_edges"], "BOUND_E") / n_open,
        "PARA_LINE_COUNT": float(n_lines),
        "PARA_WORD_COUNT": float(total_words),
        "PARA_MEAN_WORDS_PER_LINE": total_words / n_lines,
        "PARA_CARRIER_ANY_RATE": sum(bool(line["line_carrier"]) for line in lines) / n_lines,
        "PARA_CARRIER_T_RATE": sum(line["line_carrier"] == "t" for line in lines) / n_lines,
        "PARA_CARRIER_D_RATE": sum(line["line_carrier"] == "d" for line in lines) / n_lines,
        "PARA_CARRIER_S_RATE": sum(line["line_carrier"] == "s" for line in lines) / n_lines,
        "PARA_ROLE_RATE_BOUND_D": sum(role_count(line["role_sequence"], "BOUND_D") for line in lines) / total_words,
        "PARA_ROLE_RATE_BOUND_E": sum(role_count(line["role_sequence"], "BOUND_E") for line in lines) / total_words,
        "PARA_ROLE_RATE_Q": sum(role_count(line["role_sequence"], "Q") for line in lines) / total_words,
        "PARA_ROLE_RATE_REL_I": sum(role_count(line["role_sequence"], "REL_I") for line in lines) / total_words,
        "PARA_ROLE_RATE_FREE_L": sum(role_count(line["role_sequence"], "FREE_L") for line in lines) / total_words,
        "PARA_ROLE_RATE_FREE_R": sum(role_count(line["role_sequence"], "FREE_R") for line in lines) / total_words,
        "PARA_EDGE_RATE_D_TO_Q": sum(edge_count(line["confirmed_edges"], "BOUND_D") for line in lines) / total_words,
        "PARA_EDGE_RATE_E_TO_Q": sum(edge_count(line["confirmed_edges"], "BOUND_E") for line in lines) / total_words,
    }
    assert tuple(values) == OPEN_FEATURES + PARA_FEATURES
    return values


def build_matrix(admitted, prose, atom_features, word_features):
    feature_names = list(OPEN_FEATURES + PARA_FEATURES)
    feature_names += [f"ROOT_ATOM_RATE__{value}" for value in atom_features]
    feature_names += [f"ROOT_WORD_RATE__{value}" for value in word_features]
    assert len(feature_names) == 84 and len(set(feature_names)) == 84
    matrix = []
    for unit in admitted:
        for edition in EDITIONS:
            lines = [prose[edition][locus] for locus in unit["line_loci"]]
            values = base_features(lines)
            total_words = sum(int(line["word_count"]) for line in lines)
            atoms = Counter(atom for line in lines for atom in root_atoms(line["root_sequence"]))
            words = Counter(word for line in lines for word in line["root_sequence"].split())
            values.update({f"ROOT_ATOM_RATE__{value}": atoms[value] / total_words for value in atom_features})
            values.update({f"ROOT_WORD_RATE__{value}": words[value] / total_words for value in word_features})
            assert list(values) == feature_names
            assert all(math.isfinite(value) for value in values.values())
            matrix.append({
                "unit_id": unit["unit_id"], "page": unit["page"],
                "physical_folio": unit["physical_folio"], "star_ordinal": unit["star_ordinal"],
                "locus": unit["locus"], "edition": edition, **values,
            })
    assert len(matrix) == 510
    return feature_names, matrix


def main() -> None:
    units = source_units()
    prose = load_prose(units)
    admitted, excluded = paragraph_loci(units, prose)
    atoms, words_, inventory = root_inventory(admitted, prose)
    features, matrix = build_matrix(admitted, prose, atoms, words_)

    binding_fields = ("unit_id",) + SOURCE_KEYS + ("line_loci",)
    with BINDING.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=binding_fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for unit in admitted:
            writer.writerow({**{key: unit[key] for key in binding_fields if key != "line_loci"}, "line_loci": "|".join(unit["line_loci"])})

    matrix_fields = ("unit_id", "page", "physical_folio", "star_ordinal", "locus", "edition", *features)
    with MATRIX.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=matrix_fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in matrix:
            writer.writerow({key: (f"{row[key]:.12g}" if key in features else row[key]) for key in matrix_fields})

    feature_payload = {
        "formal_features": list(OPEN_FEATURES + PARA_FEATURES),
        "root_atom_features": atoms,
        "root_compound_word_features": words_,
        "all_features": features,
        "root_support_thresholds": {
            "occurrences": ROOT_MIN_OCCURRENCES, "paragraphs": ROOT_MIN_PARAGRAPHS,
            "pages": ROOT_MIN_PAGES, "folios": ROOT_MIN_FOLIOS,
        },
        "root_support_inventory": inventory,
    }
    FEATURES_JSON.write_text(json.dumps(feature_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    within_page = {}
    for feature in features:
        detail = {}
        for edition in EDITIONS:
            variable_pages = []
            variable_folios = set()
            for page in sorted({str(row["page"]) for row in matrix}):
                values = {float(row[feature]) for row in matrix if row["page"] == page and row["edition"] == edition}
                if len(values) >= 2:
                    variable_pages.append(page)
                    variable_folios.add(page[:-1])
            detail[edition] = {"pages": len(variable_pages), "folios": len(variable_folios)}
        within_page[feature] = detail

    payload = {
        "experiment": "SME001",
        "status": "PASS_TARGET_BLIND_PARAGRAPH_MATRIX_TARGET_LABELS_UNJOINED",
        "input_hashes": {str(SOURCE.relative_to(ROOT)): sha(SOURCE), str(INTER.relative_to(ROOT)): sha(INTER)},
        "source_units": 171,
        "admitted_units": 170,
        "excluded_units": excluded,
        "paragraph_line_count_distribution": dict(sorted(Counter(len(unit["line_loci"]) for unit in admitted).items())),
        "matrix_rows": 510,
        "editions": list(EDITIONS),
        "formal_features": len(OPEN_FEATURES + PARA_FEATURES),
        "root_atom_features": len(atoms),
        "root_compound_word_features": len(words_),
        "features": len(features),
        "within_page_variation": within_page,
        "binding_sha256": sha(BINDING),
        "feature_inventory_sha256": sha(FEATURES_JSON),
        "matrix_sha256": sha(MATRIX),
        "morphology_fields_in_binding_or_matrix": False,
        "target_assignment_joined": False,
        "target_result_absent": not (HERE / "TARGET_RESULT.json").exists(),
        "claim_ceiling": "target-blind paragraph structural and root-feature coverage only",
    }
    assert payload["target_result_absent"]
    RESULT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    REPORT.write_text("\n".join([
        "# SME001 anonymous paragraph-matrix capacity", "", "## Decision", "",
        "**PASS — target-blind matrix built; morphology assignments remain unjoined.**", "",
        "The exact-count source panel supplies 171 manual ZL paragraph-opening markers. Every reconstructed ZL span starts with OPEN and contains only CONT lines until the next marker or page end; RF does not carry this marker metadata and IT omits it at four starts, so those alternate metadata columns are not treated as independent layout evidence. One unit, f106r.27, is excluded without consulting morphology because IT2a omits physical line f106r.29 while ZL3b and RF1b retain it. The remaining 170 units have identical physical line sets in all three readings and span 2–7 lines. Their 510 reading-specific rows form the frozen anonymous matrix.", "",
        "The matrix has 84 prespecified or support-selected features: 19 opening-line formal measures, 15 whole-paragraph layout/formal measures, 32 root-atom rates, and 18 composite root-form rates. Root candidates were selected only by global support in every reading (at least 20 occurrences, 12 paragraphs, six pages, and five physical folios); target ray/tail values were never joined. Composite root forms retain within-space word structure, while atom features test reusable stems.", "",
        "No morphology column occurs in the binding or feature matrix. This artifact does not report any feature association. It supplies no ray/tail function, recipe class, root meaning, word meaning, lexeme, plaintext, language, or translation.", "",
        "## Reproduction", "", "```bash", "./vpy experiments/semantic_assumptions/star_morphology_entry/build_sme001_anonymous_matrix.py", "```",
    ]) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
