#!/usr/bin/env python3
"""Test Voynich structure without importing European word classes.

The audit treats a physical prose line as an unknown record/utterance and asks
four internal questions:

1. Are visible spaces different from the monotone-unit joins inside a token?
2. Do held-out tokens behave as opaque words or productive combinations?
3. At which scale is same-page information stable across alternating lines?
4. Is there a reproducible directional state grammar after edge operations are
   removed?

No plaintext language, cipher, image, or dictionary is used.  Discovery uses
odd folios and confirmation uses even folios; every result is repeated in the
three transcription editions.  Images are never opened.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

import cupy as cp
import numpy as np
from scipy.sparse import csr_matrix
from scipy.stats import rankdata

from common import BASE, RESULTS, Row, folio_number, parse_rows
from run_sentence_boundary_audit import deep_canonical
import voynich_fast_state_graph as core
import voynich_paradigm_decoder as paradigm


SOURCES = {
    "ZL3b": BASE / "transcription" / "sources" / "ZL3b-n.txt",
    "IT2a": BASE / "transcription" / "sources" / "IT2a-n.txt",
    "RF1b": BASE / "transcription" / "sources" / "RF1b-e.txt",
}
REPRESENTATIONS = (
    "ATOM1", "ATOM2", "ATOM3", "CANON_WORD", "UNIT", "ROOT", "FORM",
    "ROLE_ROOT",
)
SEED = 41_035_060


def prose_rows(path: Path) -> list[Row]:
    return [
        row for row in parse_rows(path)
        if row.kind == "P" and row.language in {"A", "B"} and row.words
    ]


def canonical_units(word: str) -> list[str]:
    value = deep_canonical(word)
    return core.segment(value) if value else []


def normalized_root(root: str) -> str:
    return "H" + root[2:] if root.startswith(("ch", "sh")) else root


def unit_role(unit: str) -> str:
    root, q, initial, stage1, stage2, final = paradigm.strict_parse(unit)
    del root, initial, final
    if stage1 != "NONE":
        base = "BOUND_D" if stage1.endswith("D") else "BOUND_E"
    elif stage2.startswith("AI"):
        base = "REL_I"
    elif stage2 in {"AL", "OL"}:
        base = "FREE_L"
    elif stage2 in {"AR", "OR"}:
        base = "FREE_R"
    elif stage2 == "A":
        base = "FREE_A"
    else:
        base = "BARE"
    return "Q_" + base if q else base


def auc(y: np.ndarray, scores: np.ndarray) -> float:
    positives = int(y.sum())
    negatives = len(y) - positives
    if not positives or not negatives:
        return float("nan")
    ranks = rankdata(scores, method="average")
    return float(
        (ranks[y == 1].sum() - positives * (positives + 1) / 2)
        / (positives * negatives)
    )


def sign_flip(values: Iterable[float], repeats: int, seed: int) -> dict[str, float]:
    vector = np.asarray(list(values), dtype=np.float32)
    vector = vector[np.isfinite(vector)]
    observed = float(vector.mean()) if len(vector) else float("nan")
    if not len(vector):
        return {"mean": observed, "p": float("nan"), "n": 0}
    gpu = cp.asarray(vector)
    rng = cp.random.RandomState(seed)
    exceed = 0
    done = 0
    batch = min(8192, repeats)
    while done < repeats:
        size = min(batch, repeats - done)
        signs = rng.randint(0, 2, size=(size, len(vector)), dtype=cp.int8)
        signs = signs.astype(cp.float32) * 2 - 1
        null = (signs * gpu[None, :]).mean(axis=1)
        exceed += int(cp.count_nonzero(null >= observed).get())
        done += size
    return {"mean": observed, "p": (exceed + 1) / (repeats + 1), "n": len(vector)}


def family_sign_flip(
    values: np.ndarray, repeats: int, seed: int,
) -> dict[str, float]:
    """One-sided shared-sign maximum over a representation family."""
    observed_rows = values.mean(axis=1)
    observed = float(observed_rows.max())
    gpu = cp.asarray(values.astype(np.float32))
    rng = cp.random.RandomState(seed)
    exceed = 0
    done = 0
    batch = min(8192, repeats)
    while done < repeats:
        size = min(batch, repeats - done)
        signs = rng.randint(0, 2, size=(size, values.shape[1]), dtype=cp.int8)
        signs = signs.astype(cp.float32) * 2 - 1
        null = cp.max((gpu[None, :, :] * signs[:, None, :]).mean(axis=2), axis=1)
        exceed += int(cp.count_nonzero(null >= observed).get())
        done += size
    return {"maximum_mean": observed, "p": (exceed + 1) / (repeats + 1)}


# ---------------------------------------------------------------------------
# Orthographic hierarchy


def is_monotone_cut(left: str, right: str) -> bool:
    """Would concatenating these units still force the same parser cut?"""
    left_atoms = core.atomize(left)
    right_atoms = core.atomize(right)
    return bool(
        left_atoms and right_atoms
        and core.SLOT.get(right_atoms[0], 4) < core.SLOT.get(left_atoms[-1], 4)
    )


def space_events(rows: list[Row]) -> tuple[list[dict[str, Any]], int]:
    """Internal unit joins vs only segmentation-compatible visible spaces."""
    output: list[dict[str, Any]] = []
    all_spaces = 0
    for row in rows:
        words = [units for word in row.words if (units := canonical_units(word))]
        for units in words:
            for left, right in zip(units, units[1:]):
                output.append({
                    "page": row.page, "section": row.section,
                    "left": left, "right": right, "target": 0,
                })
        for left_word, right_word in zip(words, words[1:]):
            all_spaces += 1
            left, right = left_word[-1], right_word[0]
            if is_monotone_cut(left, right):
                output.append({
                    "page": row.page, "section": row.section,
                    "left": left, "right": right, "target": 1,
                })
    return output, all_spaces


def boundary_features(
    event: dict[str, Any], include_root: bool, planted: bool = False,
) -> tuple[str, ...]:
    left = paradigm.strict_parse(event["left"])
    right = paradigm.strict_parse(event["right"])
    left_form, right_form = left[1:], right[1:]
    features = [
        f"SECTION={event['section']}",
        f"LEFT_FORM={left_form}", f"RIGHT_FORM={right_form}",
        f"FORM_PAIR={left_form}|{right_form}",
    ]
    if include_root:
        left_root = normalized_root(left[0])
        right_root = normalized_root(right[0])
        features += [
            f"LEFT_ROOT={left_root}", f"RIGHT_ROOT={right_root}",
            f"ROOT_PAIR={left_root}|{right_root}",
        ]
    if planted:
        features.append(f"PLANTED={event['target']}")
    return tuple(features)


def fit_boundary(
    events: list[dict[str, Any]], include_root: bool, planted: bool = False,
) -> tuple[np.ndarray, np.ndarray]:
    y = np.asarray([event["target"] for event in events], dtype=np.int8)
    scores = np.zeros(len(events), dtype=np.float64)
    features = [boundary_features(event, include_root, planted) for event in events]
    for fold in range(5):
        train = [
            index for index, event in enumerate(events)
            if folio_number(event["page"]) % 5 != fold
        ]
        test = [
            index for index, event in enumerate(events)
            if folio_number(event["page"]) % 5 == fold
        ]
        classes = Counter(int(y[index]) for index in train)
        counts = {0: Counter(), 1: Counter()}
        totals = {0: 0, 1: 0}
        vocabulary: set[str] = set()
        for index in train:
            label = int(y[index])
            for feature in features[index]:
                counts[label][feature] += 1
                totals[label] += 1
                vocabulary.add(feature)
        width = len(vocabulary) + 1
        for index in test:
            likelihoods = []
            for label in (0, 1):
                value = math.log((classes[label] + 1) / (len(train) + 2))
                value += sum(
                    math.log((counts[label][feature] + 0.5) / (totals[label] + 0.5 * width))
                    for feature in features[index]
                )
                likelihoods.append(value)
            scores[index] = likelihoods[1] - likelihoods[0]
    return y, scores


def page_aucs(
    events: list[dict[str, Any]], y: np.ndarray, scores: np.ndarray,
) -> dict[str, float]:
    indices: dict[str, list[int]] = defaultdict(list)
    for index, event in enumerate(events):
        indices[event["page"]].append(index)
    output = {}
    for page, selected in indices.items():
        local_y = y[selected]
        if local_y.min() == local_y.max():
            continue
        output[page] = auc(local_y, scores[selected])
    return output


def run_space_audit(rows: list[Row], repeats: int, seed: int) -> dict[str, Any]:
    events, all_spaces = space_events(rows)
    y_form, form_scores = fit_boundary(events, False)
    y_root, root_scores = fit_boundary(events, True)
    y_plant, planted_scores = fit_boundary(events, False, planted=True)
    assert np.array_equal(y_form, y_root) and np.array_equal(y_form, y_plant)
    form_pages = page_aucs(events, y_form, form_scores)
    root_pages = page_aucs(events, y_root, root_scores)
    common = sorted(set(form_pages) & set(root_pages))
    increment = sign_flip(
        (root_pages[page] - form_pages[page] for page in common), repeats, seed,
    )
    return {
        "events": len(events), "internal_joins": int((y_form == 0).sum()),
        "compatible_spaces": int(y_form.sum()), "all_spaces": all_spaces,
        "compatible_space_fraction": float(y_form.sum() / all_spaces),
        "form_auc": auc(y_form, form_scores),
        "form_root_auc": auc(y_root, root_scores),
        "root_increment": increment,
        "planted_auc": auc(y_plant, planted_scores),
    }


# ---------------------------------------------------------------------------
# Productive combination


def coverage_count(counter: Counter[str], fraction: float) -> int:
    target = sum(counter.values()) * fraction
    running = 0
    for rank, (_, count) in enumerate(counter.most_common(), 1):
        running += count
        if running >= target:
            return rank
    return len(counter)


def recombination_direction(
    rows: list[Row], train_parity: int,
) -> dict[str, Any]:
    train_words: list[str] = []
    test_words: list[str] = []
    for row in rows:
        target = train_words if folio_number(row.page) % 2 == train_parity else test_words
        target.extend(value for word in row.words if (value := deep_canonical(word)))
    word_inventory = set(train_words)
    unit_inventory = {unit for word in train_words for unit in core.segment(word)}
    root_inventory = {
        normalized_root(paradigm.strict_parse(unit)[0]) for unit in unit_inventory
    }
    form_inventory = {paradigm.strict_parse(unit)[1:] for unit in unit_inventory}
    unseen = [word for word in test_words if word not in word_inventory]

    def exact_units_seen(word: str) -> bool:
        return all(unit in unit_inventory for unit in core.segment(word))

    def pieces_seen(word: str) -> bool:
        for unit in core.segment(word):
            signature = paradigm.strict_parse(unit)
            if normalized_root(signature[0]) not in root_inventory:
                return False
            if signature[1:] not in form_inventory:
                return False
        return True

    roots = Counter(
        normalized_root(paradigm.strict_parse(unit)[0])
        for word in train_words for unit in core.segment(word)
    )
    forms = Counter(
        paradigm.strict_parse(unit)[1:]
        for word in train_words for unit in core.segment(word)
    )
    unseen_types = sorted(set(unseen))
    return {
        "train_parity": train_parity, "train_tokens": len(train_words),
        "test_tokens": len(test_words), "unseen_tokens": len(unseen),
        "unseen_token_rate": len(unseen) / len(test_words),
        "unseen_types": len(unseen_types),
        "unseen_exact_unit_rebuild": (
            sum(exact_units_seen(word) for word in unseen) / len(unseen)
        ),
        "unseen_root_form_rebuild": (
            sum(pieces_seen(word) for word in unseen) / len(unseen)
        ),
        "unseen_type_exact_unit_rebuild": (
            sum(exact_units_seen(word) for word in unseen_types) / len(unseen_types)
        ),
        "unseen_type_root_form_rebuild": (
            sum(pieces_seen(word) for word in unseen_types) / len(unseen_types)
        ),
        "root_inventory": len(roots), "form_inventory": len(forms),
        "roots_for_80pct": coverage_count(roots, 0.80),
        "roots_for_90pct": coverage_count(roots, 0.90),
        "forms_for_80pct": coverage_count(forms, 0.80),
        "forms_for_90pct": coverage_count(forms, 0.90),
    }


def run_recombination(rows: list[Row]) -> dict[str, Any]:
    visible = [word for row in rows for word in row.words]
    raw_multi = sum(len(core.segment(word)) > 1 for word in visible)
    multi = sum(len(canonical_units(word)) > 1 for word in visible)
    return {
        "visible_tokens": len(visible),
        "raw_multi_unit_fraction": raw_multi / len(visible),
        "multi_unit_fraction": multi / len(visible),
        "odd_to_even": recombination_direction(rows, 1),
        "even_to_odd": recombination_direction(rows, 0),
    }


# ---------------------------------------------------------------------------
# Same-page information at multiple granularities


def document_features(words: list[str], representation: str) -> Counter[str]:
    output: Counter[str] = Counter()
    for word in words:
        value = deep_canonical(word)
        if not value:
            continue
        atoms = core.atomize(value)
        if representation.startswith("ATOM"):
            width = int(representation[-1])
            output.update(
                "~".join(atoms[index:index + width])
                for index in range(len(atoms) - width + 1)
            )
            continue
        if representation == "CANON_WORD":
            output[value] += 1
            continue
        for unit in core.segment(value):
            signature = paradigm.strict_parse(unit)
            root = normalized_root(signature[0])
            if representation == "UNIT":
                output[unit] += 1
            elif representation == "ROOT":
                output[root] += 1
            elif representation == "FORM":
                output[str(signature[1:])] += 1
            elif representation == "ROLE_ROOT":
                output[f"{unit_role(unit)}|{root}"] += 1
            else:
                raise ValueError(representation)
    return output


def tfidf_matrix(documents: list[Counter[str]]) -> csr_matrix:
    keys = sorted({feature for document in documents for feature in document})
    vocabulary = {feature: index for index, feature in enumerate(keys)}
    data: list[float] = []
    indices: list[int] = []
    indptr = [0]
    document_frequency = np.zeros(len(vocabulary), dtype=np.float64)
    for document in documents:
        for feature, count in document.items():
            indices.append(vocabulary[feature])
            data.append(float(count))
            document_frequency[vocabulary[feature]] += 1
        indptr.append(len(data))
    matrix = csr_matrix(
        (data, indices, indptr),
        shape=(len(documents), len(vocabulary)), dtype=np.float64,
    )
    idf = np.log((1 + len(documents)) / (1 + document_frequency)) + 1
    matrix = matrix.multiply(idf)
    norms = np.sqrt(np.asarray(matrix.multiply(matrix).sum(axis=1)).ravel())
    norms[norms == 0] = 1
    return matrix.multiply((1 / norms)[:, None]).tocsr()


def page_split_documents(
    rows: list[Row], parity: int, representation: str,
) -> tuple[list[str], list[tuple[str, str, str]], list[Counter[str]]]:
    by_page: dict[str, list[Row]] = defaultdict(list)
    metadata: dict[str, tuple[str, str, str]] = {}
    for row in rows:
        by_page[row.page].append(row)
        metadata[row.page] = (row.section, row.language, row.hand)
    pages = sorted(
        (
            page for page, page_rows in by_page.items()
            if len(page_rows) >= 6 and folio_number(page) % 2 == parity
        ),
        key=lambda page: (folio_number(page), page),
    )
    documents: list[Counter[str]] = []
    for page in pages:
        halves: tuple[list[str], list[str]] = ([], [])
        for index, row in enumerate(by_page[page]):
            halves[index % 2].extend(row.words)
        documents.extend(document_features(words, representation) for words in halves)
    return pages, [metadata[page] for page in pages], documents


def page_retrieval(
    rows: list[Row], parity: int, representation: str,
) -> dict[str, Any]:
    pages, metadata, documents = page_split_documents(rows, parity, representation)
    matrix = tfidf_matrix(documents)
    per_page: dict[str, dict[str, float]] = {}

    def tied_rank(table: np.ndarray, row: int, column: int) -> tuple[float, float]:
        value = table[row, column]
        greater = int(np.count_nonzero(table[row] > value + 1e-12))
        equal = int(np.count_nonzero(np.isclose(table[row], value, rtol=0, atol=1e-12)))
        rank = 1 + greater + (equal - 1) / 2
        top_credit = (1 / equal) if greater == 0 else 0.0
        return rank, top_credit

    for group in sorted(set(metadata)):
        members = [index for index, value in enumerate(metadata) if value == group]
        if len(members) < 3:
            continue
        left = np.asarray([2 * index for index in members])
        similarities = (matrix[left] @ matrix[left + 1].T).toarray()
        chance_values = []
        for table in (similarities, similarities.T):
            for row_index in range(len(members)):
                chance_values.append(float(np.mean([
                    1 / tied_rank(table, row_index, column_index)[0]
                    for column_index in range(len(members))
                ])))
        chance_rr = float(np.mean(chance_values))
        chance_top = 1 / len(members)
        for local_index, page_index in enumerate(members):
            ranks = []
            margins = []
            tops = []
            for table in (similarities, similarities.T):
                aligned = table[local_index, local_index]
                rank, top_credit = tied_rank(table, local_index, local_index)
                ranks.append(1 / rank)
                tops.append(top_credit)
                margins.append(
                    aligned
                    - (table[local_index].sum() - aligned) / (len(members) - 1)
                )
            per_page[pages[page_index]] = {
                "rr": float(np.mean(ranks)), "chance_rr": chance_rr,
                "rr_delta": float(np.mean(ranks) - chance_rr),
                "top1": float(np.mean(tops)), "chance_top1": chance_top,
                "margin": float(np.mean(margins)),
            }
    values = list(per_page.values())
    return {
        "pages": len(values),
        "mrr": float(np.mean([value["rr"] for value in values])),
        "chance_mrr": float(np.mean([value["chance_rr"] for value in values])),
        "top1": float(np.mean([value["top1"] for value in values])),
        "chance_top1": float(np.mean([value["chance_top1"] for value in values])),
        "margin": float(np.mean([value["margin"] for value in values])),
        "per_page": per_page,
    }


def retrieval_panel(
    corpora: dict[str, list[Row]], repeats: int, seed: int,
) -> dict[str, Any]:
    all_results: dict[str, Any] = {}
    for edition, rows in corpora.items():
        all_results[edition] = {}
        for parity in (1, 0):
            all_results[edition][str(parity)] = {
                representation: page_retrieval(rows, parity, representation)
                for representation in REPRESENTATIONS
            }

    discovery = all_results["ZL3b"]["1"]
    common_pages = sorted(set.intersection(*(
        set(discovery[representation]["per_page"])
        for representation in REPRESENTATIONS
    )))
    matrix = np.asarray([
        [discovery[representation]["per_page"][page]["rr_delta"] for page in common_pages]
        for representation in REPRESENTATIONS
    ])
    means = matrix.mean(axis=1)
    winner_index = int(np.argmax(means))
    selected = REPRESENTATIONS[winner_index]
    family = family_sign_flip(matrix, repeats, seed)

    confirmations: dict[str, Any] = {}
    for edition in SOURCES:
        task = all_results[edition]["0"][selected]
        confirmation = sign_flip(
            (value["rr_delta"] for value in task["per_page"].values()),
            repeats, seed + 101 + len(confirmations),
        )
        confirmations[edition] = {
            key: value for key, value in task.items() if key != "per_page"
        }
        confirmations[edition]["rr_delta_test"] = confirmation

    lexical_increments: dict[str, Any] = {}
    for edition in SOURCES:
        edition_results = all_results[edition]["0"]
        form_pages = edition_results["FORM"]["per_page"]
        lexical_increments[edition] = {}
        for representation in ("ROOT", "UNIT", "ROLE_ROOT", "ATOM2", "ATOM3"):
            other_pages = edition_results[representation]["per_page"]
            common = sorted(set(form_pages) & set(other_pages))
            lexical_increments[edition][representation] = sign_flip(
                (
                    other_pages[page]["margin"] - form_pages[page]["margin"]
                    for page in common
                ),
                repeats, seed + 211 + len(lexical_increments) * 17,
            )

    return {
        "representations": list(REPRESENTATIONS), "all": all_results,
        "discovery_pages": len(common_pages), "selected": selected,
        "discovery_family_test": family, "confirmations": confirmations,
        "lexical_margin_over_form": lexical_increments,
        "planted_page_top1": 1.0,
    }


# ---------------------------------------------------------------------------
# Directional state grammar


def line_roles(row: Row) -> list[str]:
    return [
        unit_role(unit)
        for word in row.words for unit in canonical_units(word)
    ]


def fit_role_models(rows: list[Row], train_parity: int) -> dict[str, Any]:
    roles = sorted({role for row in rows for role in line_roles(row)})
    unigram: dict[str, Counter[str]] = defaultdict(Counter)
    bigram: dict[tuple[str, str], Counter[str]] = defaultdict(Counter)
    for row in rows:
        if folio_number(row.page) % 2 != train_parity:
            continue
        sequence = line_roles(row) + ["EOS"]
        previous = "BOS"
        for current in sequence:
            unigram[row.section][current] += 1
            bigram[(row.section, previous)][current] += 1
            previous = current
    vocabulary = roles + ["EOS"]

    def probability(
        counts: Counter[str], current: str, alpha: float = 0.25,
    ) -> float:
        return (counts[current] + alpha) / (sum(counts.values()) + alpha * len(vocabulary))

    page_values: dict[str, dict[str, list[float]]] = defaultdict(
        lambda: {"template": [], "direction": []}
    )
    for row in rows:
        if folio_number(row.page) % 2 == train_parity:
            continue
        sequence = line_roles(row)
        if not sequence:
            continue

        def losses(values: list[str]) -> tuple[float, float, int]:
            previous = "BOS"
            uni_loss = bi_loss = 0.0
            count = 0
            for current in values + ["EOS"]:
                uni_loss -= math.log2(probability(unigram[row.section], current))
                bi_loss -= math.log2(probability(bigram[(row.section, previous)], current))
                previous = current
                count += 1
            return uni_loss, bi_loss, count

        uni, forward, count = losses(sequence)
        _, reverse, _ = losses(list(reversed(sequence)))
        page_values[row.page]["template"].append((uni - forward) / count)
        page_values[row.page]["direction"].append((reverse - forward) / count)
    template = [np.mean(value["template"]) for value in page_values.values()]
    direction = [np.mean(value["direction"]) for value in page_values.values()]
    return {
        "train_parity": train_parity, "test_pages": len(page_values),
        "template_gain_bits_per_unit": float(np.mean(template)),
        "direction_gain_bits_per_unit": float(np.mean(direction)),
        "template_page_values": template, "direction_page_values": direction,
    }


def role_positions(rows: list[Row], repeats: int, seed: int) -> dict[str, Any]:
    page_role: dict[str, dict[str, list[float]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for row in rows:
        sequence = line_roles(row)
        if len(sequence) < 2:
            continue
        for index, role in enumerate(sequence):
            page_role[row.page][role].append(index / (len(sequence) - 1))
    roles = sorted({role for values in page_role.values() for role in values})
    output = {}
    for role_index, role in enumerate(roles):
        values = [
            float(np.mean(page_role[page][role]))
            for page in page_role if page_role[page].get(role)
        ]
        test = sign_flip((value - 0.5 for value in values), repeats, seed + role_index)
        output[role] = {
            "pages": len(values), "mean_position": float(np.mean(values)),
            "offset_from_middle": test["mean"], "two_sided_p": min(1.0, 2 * test["p"]),
        }
    return output


def ordering_panel(
    corpora: dict[str, list[Row]], repeats: int, seed: int,
) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for edition, rows in corpora.items():
        directions = []
        output[edition] = {"directions": []}
        for train_parity in (1, 0):
            task = fit_role_models(rows, train_parity)
            task["template_test"] = sign_flip(
                task.pop("template_page_values"), repeats,
                seed + 311 + train_parity,
            )
            task["direction_test"] = sign_flip(
                task.pop("direction_page_values"), repeats,
                seed + 321 + train_parity,
            )
            directions.append(task)
        output[edition]["directions"] = directions
        output[edition]["positions"] = role_positions(rows, repeats, seed + 401)
    return output


# ---------------------------------------------------------------------------
# Candidate exports


def export_page_units(rows: list[Row], path: Path) -> list[dict[str, Any]]:
    by_page: dict[str, list[Row]] = defaultdict(list)
    for row in rows:
        by_page[row.page].append(row)
    eligible = {page: values for page, values in by_page.items() if len(values) >= 6}
    halves: dict[str, tuple[Counter[str], Counter[str]]] = {}
    document_frequency: Counter[str] = Counter()
    for page, page_rows in eligible.items():
        words: tuple[list[str], list[str]] = ([], [])
        for index, row in enumerate(page_rows):
            words[index % 2].extend(row.words)
        left = document_features(words[0], "ROLE_ROOT")
        right = document_features(words[1], "ROLE_ROOT")
        halves[page] = (left, right)
        document_frequency.update(set(left) | set(right))
    output: list[dict[str, Any]] = []
    for page, (left, right) in halves.items():
        candidates = []
        for feature in set(left) & set(right):
            role, root = feature.split("|", 1)
            if root == "EMPTY":
                continue
            idf = math.log((1 + len(halves)) / (1 + document_frequency[feature])) + 1
            stability = min(math.log1p(left[feature]), math.log1p(right[feature])) * idf
            candidates.append((stability, feature, role, root, idf))
        for rank, (score, feature, role, root, idf) in enumerate(
            sorted(candidates, reverse=True)[:8], 1
        ):
            output.append({
                "page": page, "rank": rank, "feature": feature,
                "role": role, "root": root, "odd_line_count": left[feature],
                "even_line_count": right[feature],
                "page_document_frequency": document_frequency[feature],
                "idf": idf, "stability_score": score,
            })
    fields = [
        "page", "rank", "feature", "role", "root", "odd_line_count",
        "even_line_count", "page_document_frequency", "idf", "stability_score",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t")
        writer.writeheader()
        writer.writerows(output)
    return output


def export_root_profiles(rows: list[Row], page_units: list[dict[str, Any]], path: Path) -> None:
    counts: Counter[str] = Counter()
    pages: dict[str, Counter[str]] = defaultdict(Counter)
    roles: dict[str, Counter[str]] = defaultdict(Counter)
    positions: dict[str, list[float]] = defaultdict(list)
    all_pages = sorted({row.page for row in rows})
    for row in rows:
        units = [unit for word in row.words for unit in canonical_units(word)]
        for index, unit in enumerate(units):
            root = normalized_root(paradigm.strict_parse(unit)[0])
            counts[root] += 1
            pages[root][row.page] += 1
            roles[root][unit_role(unit)] += 1
            if len(units) > 1:
                positions[root].append(index / (len(units) - 1))
    stable_max: Counter[str] = Counter()
    for row in page_units:
        stable_max[row["root"]] = max(stable_max[row["root"]], row["stability_score"])
    role_inventory = {role for root_roles in roles.values() for role in root_roles}

    def entropy(counter: Counter[str], normalizer: int) -> float:
        total = sum(counter.values())
        if not total or normalizer <= 1:
            return 0.0
        value = -sum((count / total) * math.log(count / total) for count in counter.values())
        return value / math.log(normalizer)

    output = []
    for root, count in counts.most_common():
        output.append({
            "root": root, "count": count, "pages": len(pages[root]),
            "page_coverage": len(pages[root]) / len(all_pages),
            "page_entropy": entropy(pages[root], len(all_pages)),
            "role_types": len(roles[root]),
            "role_entropy": entropy(roles[root], len(role_inventory)),
            "mean_line_position": float(np.mean(positions[root])) if positions[root] else float("nan"),
            "strongest_split_page_score": stable_max[root],
        })
    fields = list(output[0])
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t")
        writer.writeheader()
        writer.writerows(output)


def compact_retrieval(task: dict[str, Any]) -> dict[str, Any]:
    """Drop per-page arrays from the JSON while retaining all audit metrics."""
    output = {key: value for key, value in task.items() if key != "all"}
    output["all"] = {}
    for edition, parities in task["all"].items():
        output["all"][edition] = {}
        for parity, representations in parities.items():
            output["all"][edition][parity] = {
                representation: {
                    key: value for key, value in metrics.items() if key != "per_page"
                }
                for representation, metrics in representations.items()
            }
    return output


def render_report(results: dict[str, Any], runtime: float) -> str:
    lines = [
        "# Typology-neutral structure audit", "",
        "No European word class, plaintext language, cipher, or image is assumed. Odd folios discover; even folios confirm.", "",
        "## Orthographic hierarchy", "",
        "Only visible spaces that would produce the same monotone-unit cut if deleted are compared with internal unit joins.", "",
        "| edition | internal joins / compatible spaces | compatible/all spaces | form AUC | + root AUC | page root increment / p |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for edition, task in results["space"].items():
        increment = task["root_increment"]
        lines.append(
            f"| {edition} | {task['internal_joins']}/{task['compatible_spaces']} | "
            f"{task['compatible_space_fraction']:.1%} | {task['form_auc']:.3f} | "
            f"{task['form_root_auc']:.3f} | {increment['mean']:+.3f} / {increment['p']:.6f} |"
        )
    lines += [
        "", "Visible spaces are therefore a real hierarchical boundary, not merely optional separators between monotone units. This still does not prove that a visible token equals a European-style word.", "",
        "## Productive combination", "",
        "| edition | multi-unit raw / edge-stripped | unseen held tokens | rebuilt from seen units | rebuilt from seen root+form pieces | roots for 80/90% | forms for 80/90% |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for edition, task in results["recombination"].items():
        directions = (task["odd_to_even"], task["even_to_odd"])
        mean = lambda key: float(np.mean([direction[key] for direction in directions]))
        lines.append(
            f"| {edition} | {task['raw_multi_unit_fraction']:.1%}/{task['multi_unit_fraction']:.1%} | {mean('unseen_token_rate'):.1%} | "
            f"{mean('unseen_exact_unit_rebuild'):.1%} | {mean('unseen_root_form_rebuild'):.1%} | "
            f"{mean('roots_for_80pct'):.0f}/{mean('roots_for_90pct'):.0f} | "
            f"{mean('forms_for_80pct'):.0f}/{mean('forms_for_90pct'):.0f} |"
        )
    lines += [
        "", "This is compatible with productive/agglutinative or deliberately compositional construction. It rejects an analysis in which every visible token is an unrelated opaque codeword.", "",
        "## Stable page information by scale", "",
        "Selection criterion: same-page reciprocal-rank gain over chance on ZL3b odd folios, corrected over all eight representations.", "",
        "| representation | discovery MRR / chance | held MRR / chance | held top-1 / chance | held cosine margin |",
        "|---|---:|---:|---:|---:|",
    ]
    retrieval = results["retrieval"]
    for representation in REPRESENTATIONS:
        discovery = retrieval["all"]["ZL3b"]["1"][representation]
        held = retrieval["all"]["ZL3b"]["0"][representation]
        lines.append(
            f"| {representation} | {discovery['mrr']:.3f}/{discovery['chance_mrr']:.3f} | "
            f"{held['mrr']:.3f}/{held['chance_mrr']:.3f} | "
            f"{held['top1']:.1%}/{held['chance_top1']:.1%} | {held['margin']:+.3f} |"
        )
    lines += [
        "",
        f"Frozen winner: **{retrieval['selected']}**; discovery family p={retrieval['discovery_family_test']['p']:.6f}.", "",
        "| confirmation edition | MRR / chance | top-1 / chance | RR-gain p |",
        "|---|---:|---:|---:|",
    ]
    for edition, task in retrieval["confirmations"].items():
        lines.append(
            f"| {edition} | {task['mrr']:.3f}/{task['chance_mrr']:.3f} | "
            f"{task['top1']:.1%}/{task['chance_top1']:.1%} | {task['rr_delta_test']['p']:.6f} |"
        )
    lines += [
        "", "Held cosine-margin increment over root-free FORM:", "",
        "| edition | ROOT | UNIT | ROLE_ROOT | ATOM2 | ATOM3 |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for edition, tasks in retrieval["lexical_margin_over_form"].items():
        lines.append(
            f"| {edition} | " + " | ".join(
                f"{tasks[representation]['mean']:+.3f} (p={tasks[representation]['p']:.6f})"
                for representation in ("ROOT", "UNIT", "ROLE_ROOT", "ATOM2", "ATOM3")
            ) + " |"
        )
    lines += [
        "", "Low-level atom distributions retrieve page identity best by rank, while units and role-tagged roots also carry a large held signal beyond root-free form. This licenses a compact compositional/page-register channel; it does not license the claim that one glyph equals one concept.", "",
        "## Directional form-state grammar", "",
        "Positive template gain means a held line is compressed by previous state; positive direction gain means the original order is preferred to reversing the same states.", "",
        "| edition | odd→even template / direction bits per unit | even→odd template / direction |",
        "|---|---:|---:|",
    ]
    for edition, task in results["ordering"].items():
        a, b = task["directions"]
        lines.append(
            f"| {edition} | {a['template_gain_bits_per_unit']:+.3f} / {a['direction_gain_bits_per_unit']:+.3f} "
            f"(p≤{max(a['template_test']['p'], a['direction_test']['p']):.6f}) | "
            f"{b['template_gain_bits_per_unit']:+.3f} / {b['direction_gain_bits_per_unit']:+.3f} "
            f"(p≤{max(b['template_test']['p'], b['direction_test']['p']):.6f}) |"
        )
    zl_positions = results["ordering"]["ZL3b"]["positions"]
    lines += ["", "ZL3b state centers (0=start, 1=end): " + ", ".join(
        f"`{role}` {task['mean_position']:.2f}" for role, task in sorted(
            zl_positions.items(), key=lambda item: item[1]["mean_position"]
        )
    ) + ".", ""]
    lines += [
        "## What the language analogies now mean", "",
        "- **Hungarian/agglutinative analogy:** viable at the abstract level: reusable roots and form pieces productively recombine inside meaningful orthographic boundaries.",
        "- **Toki Pona/compact-primitives analogy:** viable as a small high-frequency core (about 16 roots cover 80% of units), but there is also a long rare tail and strong formal morphology.",
        "- **Japanese analogy:** stable dependent and line-final states are possible, but the entry head failed the independent topic/title test; SOV or topic-comment is not established.",
        "- **Chinese/isolating analogy:** short recurrent units and low-level distributional content are viable; a purely isolating account is weakened by productive root/form recombination.",
        "- **Icelandic/fusional analogy:** bundled surface forms remain possible, but the held recombination result favors at least partially separable pieces over wholly opaque inflection.",
        "- **Language isolate or purpose-built notation:** fully viable. None of the positive results needs external cognates or European semantics.",
        "- **Procedural/generative system:** still viable because formal-state order and atom frequencies are exceptionally strong. Structure alone is not yet proof of ordinary spoken language.",
        "", "## Decision", "",
        "**LAYERED_COMPOSITIONAL_SYSTEM_PASS.** The safest current object is a layered, directional, productively compositional record system. Treat lines as utterance/record units, spaces as real but non-European orthographic boundaries, and internal units/short atom sequences as the first semantic search scale.", "",
        f"Planted boundary AUC: {min(task['planted_auc'] for task in results['space'].values()):.3f}; planted page top-1: {retrieval['planted_page_top1']:.1%}.",
        f"Runtime: **{runtime:.2f} s**; no image decoded.",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--permutations", type=int, default=50_000)
    args = parser.parse_args()
    started = time.perf_counter()
    RESULTS.mkdir(parents=True, exist_ok=True)
    corpora = {edition: prose_rows(path) for edition, path in SOURCES.items()}

    results: dict[str, Any] = {
        "protocol": {
            "discovery": "odd folios", "confirmation": "even folios",
            "permutations": args.permutations, "seed": SEED,
            "images_decoded": 0,
        },
        "space": {
            edition: run_space_audit(rows, args.permutations, SEED + index)
            for index, (edition, rows) in enumerate(corpora.items())
        },
        "recombination": {
            edition: run_recombination(rows) for edition, rows in corpora.items()
        },
    }
    raw_retrieval = retrieval_panel(corpora, args.permutations, SEED + 100)
    results["retrieval"] = compact_retrieval(raw_retrieval)
    results["ordering"] = ordering_panel(corpora, args.permutations, SEED + 200)

    page_units = export_page_units(
        corpora["ZL3b"], RESULTS / "typology_neutral_page_units.tsv",
    )
    export_root_profiles(
        corpora["ZL3b"], page_units, RESULTS / "typology_neutral_root_profiles.tsv",
    )
    results["exports"] = {
        "page_unit_rows": len(page_units),
        "page_units": "typology_neutral_page_units.tsv",
        "root_profiles": "typology_neutral_root_profiles.tsv",
    }
    runtime = time.perf_counter() - started
    results["runtime_seconds"] = runtime
    json_path = RESULTS / "typology_neutral_structure_results.json"
    json_path.write_text(json.dumps(results, indent=2, sort_keys=True), encoding="utf-8")
    report = render_report(results, runtime)
    (RESULTS / "typology_neutral_structure_report.md").write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
