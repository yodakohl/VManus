#!/usr/bin/env python3
"""Clean-room reconstruction of the DIC001 target-blind reference instrument.

This validator does not import the production runner and never scores a drawing
boundary.  It reconstructs the reference events, leave-folio models, summaries,
and fixed 64-world label-permutation check from the two frozen public artifacts.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
SOURCE = RESULTS / "source_native_structural_interlinear_v1.tsv"
CAPACITY = RESULTS / "dic001_drawing_interruption_capacity.tsv"
SPEC = HERE / "DIC001_TARGET_BLIND_INSTRUMENT_SPEC.md"
RUNNER = HERE / "run_dic001_target_blind_instrument.py"
PRODUCTION = RESULTS / "dic001_target_blind_instrument.json"
PRODUCTION_REPORT = RESULTS / "dic001_target_blind_instrument_report.md"
OUTPUT = RESULTS / "dic001_target_blind_instrument_validation.json"
OUTPUT_REPORT = RESULTS / "dic001_target_blind_instrument_validation_report.md"

FROZEN_HASHES = {
    SOURCE: "95a15329c61a11c1c4dc671b4df2b3482af9d25a1108eadac2f69b066d3785af",
    CAPACITY: "e4e1a507211230f362ac4fd34bc0c382442300600132b7deb4e971cab69cfa2c",
    SPEC: "cf13b1ddd047ef39d10b504b58942cb1100daa55e9fdf11ad9a48e6cfe7b5236",
    RUNNER: "ccd5ab6f16b83bd0f43a92c14654adb1c158ffbe64451a566e4024177d2757d0",
    PRODUCTION: "8b4b2e3566d5f4c6392e5086445090759c96bb3ebc43612e03028d5d5aab7113",
    PRODUCTION_REPORT: "4a90371299f53c70b165d825a6e8cd304c3c82f70bab6a30b0ae71863a49d250",
}
SPACE_PROFILE = "ZL3b:DEFINITE_SPACE;IT2a:DEFINITE_SPACE;RF1b:DEFINITE_SPACE"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def physical_folio(page: str) -> str:
    match = re.match(r"f\d+", page)
    if not match:
        raise AssertionError(f"invalid page {page!r}")
    return match.group(0)


def line_number(locus: str) -> int:
    return int(locus.rsplit(".", 1)[1])


def shape_fields(left: dict[str, str], right: dict[str, str]) -> tuple[str, ...]:
    a, b = left["family_surface"], right["family_surface"]
    a2 = a[-2:] if len(a) > 1 else "#" + a
    b2 = b[:2] if len(b) > 1 else b + "#"
    return a[-1], b[0], a[-1] + "|" + b[0], a2, b2, a2 + "|" + b2


def length_fields(left: dict[str, str], right: dict[str, str]) -> tuple[str, ...]:
    a = str(min(len(left["family_surface"]), 8))
    b = str(min(len(right["family_surface"]), 8))
    return a, b, a + "|" + b


class Event:
    __slots__ = ("page", "folio", "label", "left", "right", "currier")

    def __init__(self, page, label, left, right, currier):
        self.page = page
        self.folio = physical_folio(page)
        self.label = label
        self.left = left
        self.right = right
        self.currier = currier


def train_model(events: list[Event], field_fn):
    by_class = [[Counter() for _ in field_fn(events[0].left, events[0].right)] for _ in range(2)]
    totals = [[0] * len(by_class[0]) for _ in range(2)]
    vocab = [set() for _ in by_class[0]]
    for event in events:
        values = field_fn(event.left, event.right)
        for j, value in enumerate(values):
            by_class[event.label][j][value] += 1
            totals[event.label][j] += 1
            vocab[j].add(value)

    def score(event: Event) -> float:
        answer = 0.0
        for j, value in enumerate(field_fn(event.left, event.right)):
            cardinality = len(vocab[j]) + 1
            answer += math.log((by_class[1][j][value] + 1) / (totals[1][j] + cardinality))
            answer -= math.log((by_class[0][j][value] + 1) / (totals[0][j] + cardinality))
        return answer

    return score


def auc(high: list[float], low: list[float]) -> float:
    return float(np.mean([(x > y) + 0.5 * (x == y) for x in high for y in low]))


def summarize(scored: list[tuple[Event, float]], replacement_labels=None):
    page_values = defaultdict(lambda: [[], []])
    for i, (event, score) in enumerate(scored):
        label = event.label if replacement_labels is None else replacement_labels[i]
        page_values[event.page][label].append(score)
    folio_values, currier_values = defaultdict(list), defaultdict(list)
    for page, pair in page_values.items():
        if not pair[0] or not pair[1]:
            continue
        page_auc = auc(pair[1], pair[0])
        first = next(event for event, _ in scored if event.page == page)
        folio_values[first.folio].append(page_auc)
        currier_values[first.currier].append(page_auc)
    folio_auc = {key: float(np.mean(values)) for key, values in folio_values.items()}
    currier_auc = {key: float(np.mean(values)) for key, values in currier_values.items()}
    return {
        "auc": float(np.mean(list(folio_auc.values()))),
        "folio_auc": folio_auc,
        "currier_auc": currier_auc,
        "positive_folios": sum(value > 0.5 for value in folio_auc.values()),
        "folios": len(folio_auc),
        "pages": len(page_values),
    }


def reconstruct():
    with CAPACITY.open(newline="") as handle:
        target_pages = {
            row["page"]
            for row in csv.DictReader(handle, delimiter="\t")
            if row["boundary_class"] == "DRAWING_INTERRUPTION"
        }
    with SOURCE.open(newline="") as handle:
        source_rows = list(csv.DictReader(handle, delimiter="\t"))

    lines = defaultdict(list)
    for row in source_rows:
        if row["page"] not in target_pages and row["grammar_scope"] == "CONFIRMED_PROSE":
            lines[row["locus"]].append(row)
    for groups in lines.values():
        groups.sort(key=lambda row: int(row["group_index"]))

    events: list[Event] = []
    for groups in lines.values():
        for left, right in zip(groups, groups[1:]):
            if left["right_boundary_profile"] == SPACE_PROFILE:
                events.append(Event(left["page"], 0, left, right, left["currier"]))

    pages = defaultdict(list)
    for groups in lines.values():
        pages[groups[0]["page"]].append(groups)
    for page, page_lines in pages.items():
        page_lines.sort(key=lambda groups: line_number(groups[0]["locus"]))
        for first, second in zip(page_lines, page_lines[1:]):
            if (line_number(second[0]["locus"]) == line_number(first[0]["locus"]) + 1
                    and second[0]["code"].startswith("+P")):
                events.append(Event(page, 1, first[-1], second[0], second[0]["currier"]))

    scored = {}
    for name, field_fn in (("SHAPE", shape_fields), ("LENGTH", length_fields)):
        values = []
        for held_folio in sorted({event.folio for event in events}):
            train = [event for event in events if event.folio != held_folio]
            test = [event for event in events if event.folio == held_folio]
            model = train_model(train, field_fn)
            values.extend((event, model(event)) for event in test)
        scored[name] = values

    summary = {name: summarize(values) for name, values in scored.items()}
    page_indices = defaultdict(list)
    for i, (event, _) in enumerate(scored["SHAPE"]):
        page_indices[event.page].append(i)
    base_labels = [event.label for event, _ in scored["SHAPE"]]
    rng = np.random.default_rng(4100101)
    null = []
    for _ in range(64):
        labels = base_labels.copy()
        for indices in page_indices.values():
            shuffled = [labels[i] for i in indices]
            rng.shuffle(shuffled)
            for i, value in zip(indices, shuffled):
                labels[i] = value
        null.append(summarize(scored["SHAPE"], labels)["auc"])

    labels = Counter(event.label for event in events)
    real = summary["SHAPE"]["auc"]
    p_value = (1 + sum(value >= real for value in null)) / 65
    gates = {
        "resets_at_least_1000": labels[1] >= 1000,
        "folios_at_least_60": summary["SHAPE"]["folios"] >= 60,
        "shape_auc_at_least_075": real >= 0.75,
        "shape_minus_length_at_least_015": real - summary["LENGTH"]["auc"] >= 0.15,
        "positive_folios_at_least_90pct": summary["SHAPE"]["positive_folios"] >= math.ceil(0.9 * summary["SHAPE"]["folios"]),
        "currier_A_B_auc_at_least_070": all(summary["SHAPE"]["currier_auc"].get(c, 0) >= 0.70 for c in "AB"),
        "permutation_p_at_most_1_over_65": p_value <= 1 / 65,
        "target_pages_excluded": not ({event.page for event in events} & target_pages),
    }
    all_pass = all(gates.values())
    result = {
        "experiment": "DIC001_TARGET_BLIND_INSTRUMENT",
        "status": "PASS_TARGET_BLIND_REFERENCE_INSTRUMENT" if all_pass else "STOP_INSTRUMENT_GATES",
        "inputs": {path.name: digest(path) for path in (SOURCE, CAPACITY, SPEC, RUNNER)},
        "counts": {"events": len(events), "spaces": labels[0], "resets": labels[1], "target_pages_excluded": len(target_pages)},
        "summary": summary,
        "permutation": {"worlds": 64, "p": p_value, "null_min": min(null), "null_max": max(null)},
        "gates": gates,
        "drawing_target_family_scores_computed": False,
        "decision": "AUTHORIZE_INDEPENDENT_RECONSTRUCTION_ONLY" if all_pass else "STOP",
        "claim_ceiling": "Reference reset-likeness instrument only; no drawing result, word, sound, POS, meaning, plaintext, language, cipher, or translation.",
    }
    report = (
        "# DIC001 target-blind continuity instrument\n\n"
        f"Status: **{result['status']}**.\n\n"
        f"All **{len(target_pages)}** drawing-target pages were excluded. Held-folio shape AUC is **{real:.6f}** across **{summary['SHAPE']['folios']}** folios versus length-only **{summary['LENGTH']['auc']:.6f}**; **{summary['SHAPE']['positive_folios']}/{summary['SHAPE']['folios']}** folios are positive and the 64-world within-page permutation p is **{p_value:.6f}**. The reference has **{labels[1]:,}** continuation resets and **{labels[0]:,}** ordinary spaces.\n\n"
        "This authorizes independent reconstruction only. No drawing-interruption family score or semantic value was computed.\n"
    )
    return result, report, null


def compare(expected, observed, path="root"):
    checks = 1
    discrepancies = []
    max_abs = 0.0
    if type(expected) is not type(observed):
        return checks, [f"{path}: type {type(expected).__name__} != {type(observed).__name__}"], max_abs
    if isinstance(expected, dict):
        if set(expected) != set(observed):
            discrepancies.append(f"{path}: keys differ")
        for key in sorted(set(expected) & set(observed)):
            c, d, m = compare(expected[key], observed[key], f"{path}.{key}")
            checks += c
            discrepancies.extend(d)
            max_abs = max(max_abs, m)
    elif isinstance(expected, list):
        if len(expected) != len(observed):
            discrepancies.append(f"{path}: length differs")
        for i, (a, b) in enumerate(zip(expected, observed)):
            c, d, m = compare(a, b, f"{path}[{i}]")
            checks += c
            discrepancies.extend(d)
            max_abs = max(max_abs, m)
    elif isinstance(expected, float):
        delta = abs(expected - observed)
        max_abs = delta
        if delta > 1e-15:
            discrepancies.append(f"{path}: {expected!r} != {observed!r} (delta {delta:.3g})")
    elif expected != observed:
        discrepancies.append(f"{path}: {expected!r} != {observed!r}")
    return checks, discrepancies, max_abs


def main():
    hash_failures = [f"{path.name}: {digest(path)}" for path, frozen in FROZEN_HASHES.items() if digest(path) != frozen]
    if hash_failures:
        raise SystemExit("frozen input drift: " + "; ".join(hash_failures))
    reconstructed, expected_report, null = reconstruct()
    stored = json.loads(PRODUCTION.read_text())
    checks, discrepancies, max_abs = compare(reconstructed, stored)
    checks += 1
    if PRODUCTION_REPORT.read_text() != expected_report:
        discrepancies.append("production report text differs from independent reconstruction")
    checks += len(FROZEN_HASHES)
    status = "PASS" if not discrepancies else "FAIL"
    validation = {
        "experiment": "DIC001_TARGET_BLIND_INSTRUMENT_VALIDATION",
        "status": status,
        "assertions": checks,
        "discrepancies": discrepancies,
        "max_numeric_abs_difference": max_abs,
        "reconstructed": {
            "events": reconstructed["counts"]["events"],
            "spaces": reconstructed["counts"]["spaces"],
            "resets": reconstructed["counts"]["resets"],
            "target_pages_excluded": reconstructed["counts"]["target_pages_excluded"],
            "shape_auc": reconstructed["summary"]["SHAPE"]["auc"],
            "length_auc": reconstructed["summary"]["LENGTH"]["auc"],
            "shape_folios": reconstructed["summary"]["SHAPE"]["folios"],
            "positive_shape_folios": reconstructed["summary"]["SHAPE"]["positive_folios"],
            "null_worlds": len(null),
            "permutation_p": reconstructed["permutation"]["p"],
            "all_gates": all(reconstructed["gates"].values()),
        },
        "bound_sha256": {path.name: frozen for path, frozen in FROZEN_HASHES.items()},
        "target_family_scores_computed": False,
        "decision": "VALIDATE_REFERENCE_ONLY" if status == "PASS" else "STOP",
        "claim_ceiling": reconstructed["claim_ceiling"],
    }
    OUTPUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n")
    OUTPUT_REPORT.write_text(
        "# DIC001 target-blind instrument validation\n\n"
        f"Status: **{status}** with **{checks:,}** checks and **{len(discrepancies)}** discrepancies.\n\n"
        f"Independent reconstruction recovered **{reconstructed['counts']['events']:,}** reference boundaries, held-folio shape AUC **{reconstructed['summary']['SHAPE']['auc']:.6f}**, length-only AUC **{reconstructed['summary']['LENGTH']['auc']:.6f}**, and all **{len(null)}** fixed permutation worlds. Maximum numeric difference was **{max_abs:.3g}**.\n\n"
        "No drawing-boundary family score was computed.\n"
    )
    print(json.dumps(validation, indent=2, sort_keys=True))
    if discrepancies:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
