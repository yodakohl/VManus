#!/usr/bin/env python3
"""IL001: locate predictive information in manually transcribed Voynich text.

This runner is deliberately count based.  It reads only the three locked manual
transcriptions and the confirmed structural parser.  Validation selects fixed
Dirichlet strengths; a separate final phase verifies the frozen runner hash
before touching held likelihoods.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import sys
import time
from collections import Counter, defaultdict
from dataclasses import dataclass, replace
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable, Sequence

import numpy as np


HERE = Path(__file__).resolve().parent
BASE = HERE.parents[1]
LEGACY = BASE / "archive_pre_reset_2026-08-06" / "semantic_assumptions"
sys.path.insert(0, str(LEGACY))

from common import (  # noqa: E402
    _boundary_canonicalizations,
    _clear_form_slots,
    parse_rows,
)
import voynich_fast_state_graph as core  # noqa: E402
import voynich_paradigm_decoder as paradigm  # noqa: E402


SOURCES = {
    "ZL3b": BASE / "transcription" / "sources" / "ZL3b-n.txt",
    "IT2a": BASE / "transcription" / "sources" / "IT2a-n.txt",
    "RF1b": BASE / "transcription" / "sources" / "RF1b-e.txt",
}
PREREG = HERE / "hypotheses" / "IL001_INFORMATION_LOCATION_PREREGISTRATION.md"
RESULTS = HERE / "results"
FROZEN = RESULTS / "il001_information_location_validation_frozen.json"
OUTPUT_JSON = RESULTS / "il001_information_location_results.json"
OUTPUT_REPORT = RESULTS / "il001_information_location_report.md"
SALT = "IL001-2026-08-06|"
GRID = (1.0, 2.0, 4.0, 8.0, 16.0, 32.0, 64.0, 128.0)
ALPHA = 0.5
UNKNOWN = ("<UNK>",)
MODEL_NAMES = (
    "GLOBAL", "FORM", "TEMPLATE", "WITHIN", "PREVIOUS",
    "REMOTE_PAGE", "FULL_CONTEXT",
)
GAIN_MODELS = {
    "TEMPLATE": "FORM",
    "WITHIN": "TEMPLATE",
    "PREVIOUS": "TEMPLATE",
    "REMOTE_PAGE": "TEMPLATE",
    "FULL_CONTEXT": "TEMPLATE",
}
CACHE_MODELS = ("WITHIN", "PREVIOUS", "REMOTE_PAGE", "FULL_CONTEXT")
SIGN_REPEATS = 200_000
BOOTSTRAP_REPEATS = 20_000
SEED = 1_100_001


Root = tuple[str, ...]
UnitShell = tuple[int, str, str, str, str]
FormShell = tuple[UnitShell, ...]


@dataclass(frozen=True)
class Token:
    root: Root
    shell: FormShell
    position_bin: int
    length_bin: str


@dataclass(frozen=True)
class Line:
    page: str
    locus: str
    language: str
    section: str
    hand: str
    paragraph_start: bool
    tokens: tuple[Token, ...]

    @property
    def stratum(self) -> tuple[str, str, str]:
        return self.language, self.section, self.hand


@dataclass
class Score:
    bits: dict[str, float]
    page_bits: dict[str, dict[str, float]]
    page_targets: dict[str, int]
    targets: int
    events: list[dict[str, Any]]

    def bpt(self, model: str) -> float:
        return self.bits[model] / self.targets


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stable_int(text: str) -> int:
    return int.from_bytes(hashlib.sha256(text.encode("utf-8")).digest()[:8], "big")


def split_bucket(page: str) -> int:
    digest = hashlib.sha256((SALT + page.lower()).encode("utf-8")).hexdigest()
    return int(digest[:2], 16) % 5


def split_name(page: str) -> str:
    bucket = split_bucket(page)
    return "test" if bucket == 0 else "validation" if bucket == 1 else "train"


@lru_cache(maxsize=None)
def deep_canonical(word: str) -> str:
    """Exact conservative canonicalizer used by the confirmed grammar."""
    value = _boundary_canonicalizations(word)["CANON_BOUNDARY"]
    atoms = core.atomize(value)
    if len(atoms) > 1 and atoms[0] in {"d", "y", "t", "s", "k"}:
        value = "".join(atoms[1:])
    cleared = _clear_form_slots(value, initials={"P", "F"}, finals={"Y", "M", "G"})
    return value if cleared is None else cleared


def normalized_root(root: str) -> str:
    return "H" + root[2:] if root.startswith(("ch", "sh")) else root


def length_bin(length: int) -> str:
    if length <= 4:
        return "2-4"
    if length <= 8:
        return "5-8"
    if length <= 12:
        return "9-12"
    return "13+"


def parse_token(word: str, index: int, line_length: int) -> Token | None:
    value = deep_canonical(word)
    units = core.segment(value) if value else []
    if not units:
        return None
    roots: list[str] = []
    shells: list[UnitShell] = []
    for unit in units:
        root, q, initial, stage1, stage2, final = paradigm.strict_parse(unit)
        roots.append(normalized_root(root))
        shells.append((int(q), initial, stage1, stage2, final))
    coordinate = index / max(line_length - 1, 1)
    position = min(4, int(5 * coordinate))
    return Token(tuple(roots), tuple(shells), position, length_bin(line_length))


def load_lines(path: Path) -> list[Line]:
    output: list[Line] = []
    for row in parse_rows(path):
        if row.kind != "P" or row.language not in {"A", "B"} or not row.words:
            continue
        preliminary = []
        for word in row.words:
            value = deep_canonical(word)
            if value and core.segment(value):
                preliminary.append(word)
        if len(preliminary) < 2:
            continue
        tokens = tuple(
            token for index, word in enumerate(preliminary)
            if (token := parse_token(word, index, len(preliminary))) is not None
        )
        if len(tokens) < 2:
            continue
        output.append(Line(
            page=row.page,
            locus=row.locus,
            language=row.language,
            section=row.section,
            hand=row.hand,
            paragraph_start=row.paragraph_start,
            tokens=tokens,
        ))
    return output


def page_groups(lines: Sequence[Line]) -> list[tuple[str, list[Line]]]:
    grouped: dict[str, list[Line]] = {}
    for line in lines:
        grouped.setdefault(line.page, []).append(line)
    return list(grouped.items())


def select_split(lines: Sequence[Line], name: str) -> list[Line]:
    return [line for line in lines if split_name(line.page) == name]


def corpus_inventory(lines: Sequence[Line]) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for name in ("train", "validation", "test"):
        selected = select_split(lines, name)
        output[name] = {
            "pages": len({line.page for line in selected}),
            "lines": len(selected),
            "targets": sum(len(line.tokens) for line in selected),
            "strata": len({line.stratum for line in selected}),
        }
    return output


class StructuralModel:
    def __init__(self, train: Sequence[Line]):
        roots = sorted({token.root for line in train for token in line.tokens})
        self.roots: tuple[Root, ...] = tuple(roots) + (UNKNOWN,)
        self.index = {root: idx for idx, root in enumerate(self.roots)}
        self.unk = self.index[UNKNOWN]
        self.vocab_size = len(self.roots)
        self.global_counts: Counter[int] = Counter()
        self.meta_counts: dict[tuple[Any, ...], Counter[int]] = defaultdict(Counter)
        self.form_counts: dict[tuple[Any, ...], Counter[int]] = defaultdict(Counter)
        self.template_counts: dict[tuple[Any, ...], Counter[int]] = defaultdict(Counter)
        for line in train:
            meta = line.stratum
            for token in line.tokens:
                idx = self.index[token.root]
                self.global_counts[idx] += 1
                self.meta_counts[meta][idx] += 1
                self.form_counts[(meta, token.shell)][idx] += 1
                self.template_counts[(
                    meta, token.shell, token.position_bin,
                    int(line.paragraph_start), token.length_bin,
                )][idx] += 1
        self.total = sum(self.global_counts.values())

    def target_index(self, root: Root) -> int:
        return self.index.get(root, self.unk)

    @staticmethod
    def _backoff(counter: Counter[int], idx: int, prior: float, tau: float) -> float:
        total = sum(counter.values())
        return (counter.get(idx, 0) + tau * prior) / (total + tau)

    def global_probability(self, idx: int) -> float:
        return (
            self.global_counts.get(idx, 0) + ALPHA
        ) / (self.total + ALPHA * self.vocab_size)

    def form_probability(self, idx: int, line: Line, token: Token, tau: float) -> float:
        probability = self.global_probability(idx)
        meta = line.stratum
        probability = self._backoff(self.meta_counts.get(meta, Counter()), idx, probability, tau)
        probability = self._backoff(
            self.form_counts.get((meta, token.shell), Counter()),
            idx, probability, tau,
        )
        return probability

    def template_probability(
        self,
        idx: int,
        line: Line,
        token: Token,
        tau_form: float,
        tau_template: float,
        tail_override: tuple[int, int, str] | None = None,
    ) -> float:
        probability = self.form_probability(idx, line, token, tau_form)
        tail = tail_override or (
            token.position_bin, int(line.paragraph_start), token.length_bin,
        )
        key = (line.stratum, token.shell, *tail)
        return self._backoff(
            self.template_counts.get(key, Counter()), idx,
            probability, tau_template,
        )

    def known_indices(self, roots: Iterable[Root]) -> tuple[int, ...]:
        return tuple(self.index[root] for root in roots if root in self.index and root != UNKNOWN)


def cache_probability(base: float, idx: int, sequence: Sequence[int], tau: float) -> float:
    if not sequence:
        return base
    counts = Counter(sequence)
    return (counts.get(idx, 0) + tau * base) / (len(sequence) + tau)


def cache_probability_counts(
    base: float, idx: int, counts: Counter[int], total: int, tau: float
) -> float:
    if not total:
        return base
    return (counts.get(idx, 0) + tau * base) / (total + tau)


def score_lines(
    lines: Sequence[Line],
    model: StructuralModel,
    parameters: dict[str, float],
    collect_events: bool = False,
) -> Score:
    bits = {name: 0.0 for name in MODEL_NAMES}
    page_bits: dict[str, dict[str, float]] = defaultdict(
        lambda: {name: 0.0 for name in MODEL_NAMES}
    )
    page_targets: Counter[str] = Counter()
    events: list[dict[str, Any]] = []
    targets = 0
    for page, page_lines in page_groups(lines):
        previous: tuple[int, ...] = ()
        previous_counts: Counter[int] = Counter()
        remote: list[int] = []
        remote_counts: Counter[int] = Counter()
        for line in page_lines:
            current_known = model.known_indices(token.root for token in line.tokens)
            within: list[int] = []
            within_counts: Counter[int] = Counter()
            for token_index, token in enumerate(line.tokens):
                idx = model.target_index(token.root)
                p_global = model.global_probability(idx)
                p_form = model.form_probability(idx, line, token, parameters["form"])
                p_template = model.template_probability(
                    idx, line, token, parameters["form"], parameters["template"]
                )
                probabilities = {
                    "GLOBAL": p_global,
                    "FORM": p_form,
                    "TEMPLATE": p_template,
                }
                probabilities["WITHIN"] = cache_probability_counts(
                    p_template, idx, within_counts, len(within), parameters["within"]
                )
                probabilities["PREVIOUS"] = cache_probability_counts(
                    p_template, idx, previous_counts, len(previous), parameters["previous"]
                )
                probabilities["REMOTE_PAGE"] = cache_probability_counts(
                    p_template, idx, remote_counts, len(remote), parameters["remote_page"]
                )
                full_total = len(within) + len(previous) + len(remote)
                full_count = (
                    within_counts.get(idx, 0)
                    + previous_counts.get(idx, 0)
                    + remote_counts.get(idx, 0)
                )
                probabilities["FULL_CONTEXT"] = (
                    (full_count + parameters["full_context"] * p_template)
                    / (full_total + parameters["full_context"])
                    if full_total else p_template
                )
                for name, probability in probabilities.items():
                    if not math.isfinite(probability) or probability <= 0 or probability > 1 + 1e-12:
                        raise RuntimeError(
                            f"invalid probability {probability} for {name} at {line.locus}:{token_index}"
                        )
                    value = -math.log2(min(probability, 1.0))
                    bits[name] += value
                    page_bits[page][name] += value
                page_targets[page] += 1
                targets += 1
                if collect_events:
                    caches = {
                        "WITHIN": tuple(within),
                        "PREVIOUS": previous,
                        "REMOTE_PAGE": tuple(remote),
                        "FULL_CONTEXT": tuple(within) + previous + tuple(remote),
                    }
                    events.append({
                        "page": page,
                        "locus": line.locus,
                        "token_index": token_index,
                        "line": line,
                        "token": token,
                        "idx": idx,
                        "p_form": p_form,
                        "p_template": p_template,
                        "caches": caches,
                    })
                if idx != model.unk:
                    within.append(idx)
                    within_counts[idx] += 1
            remote.extend(previous)
            remote_counts.update(previous_counts)
            previous = current_known
            previous_counts = Counter(current_known)
    if not targets:
        raise RuntimeError("no eligible targets")
    return Score(bits, dict(page_bits), dict(page_targets), targets, events)


def tune_parameters(train: Sequence[Line], validation: Sequence[Line]) -> tuple[StructuralModel, dict[str, float], dict[str, Any]]:
    model = StructuralModel(train)
    defaults = {
        "form": 16.0,
        "template": 16.0,
        "within": 16.0,
        "previous": 16.0,
        "remote_page": 16.0,
        "full_context": 16.0,
    }
    traces: dict[str, list[dict[str, float]]] = {}

    form_trace = []
    for tau in GRID:
        trial = {**defaults, "form": tau}
        score = score_lines(validation, model, trial)
        form_trace.append({"tau": tau, "bpt": score.bpt("FORM")})
    defaults["form"] = min(form_trace, key=lambda row: (row["bpt"], row["tau"]))["tau"]
    traces["form"] = form_trace

    template_trace = []
    for tau in GRID:
        trial = {**defaults, "template": tau}
        score = score_lines(validation, model, trial)
        template_trace.append({"tau": tau, "bpt": score.bpt("TEMPLATE")})
    defaults["template"] = min(
        template_trace, key=lambda row: (row["bpt"], row["tau"])
    )["tau"]
    traces["template"] = template_trace

    for model_name, parameter_name in (
        ("WITHIN", "within"),
        ("PREVIOUS", "previous"),
        ("REMOTE_PAGE", "remote_page"),
        ("FULL_CONTEXT", "full_context"),
    ):
        trace = []
        for tau in GRID:
            trial = {**defaults, parameter_name: tau}
            score = score_lines(validation, model, trial)
            trace.append({"tau": tau, "bpt": score.bpt(model_name)})
        defaults[parameter_name] = min(
            trace, key=lambda row: (row["bpt"], row["tau"])
        )["tau"]
        traces[parameter_name] = trace

    selected_score = score_lines(validation, model, defaults)
    summary = {
        "traces": traces,
        "selected_bpt": {name: selected_score.bpt(name) for name in MODEL_NAMES},
        "vocabulary": model.vocab_size,
        "unknown_targets": sum(
            model.target_index(token.root) == model.unk
            for line in validation for token in line.tokens
        ),
    }
    return model, defaults, summary


def replace_roots_with_copy_signal(
    lines: Sequence[Line], source: str, known: set[Root]
) -> tuple[list[Line], int]:
    output: list[Line] = []
    replacements = 0
    for page, original_lines in page_groups(lines):
        previous: tuple[Root, ...] = ()
        remote: list[Root] = []
        for line in original_lines:
            original_roots = tuple(token.root for token in line.tokens if token.root in known)
            new_tokens: list[Token] = []
            within: list[Root] = []
            for index, token in enumerate(line.tokens):
                if source == "WITHIN":
                    candidates = tuple(within)
                elif source == "PREVIOUS":
                    candidates = previous
                elif source == "REMOTE_PAGE":
                    candidates = tuple(remote)
                else:
                    raise ValueError(source)
                marker = stable_int(f"IL001-PLANT|{source}|{page}|{line.locus}|{index}")
                if candidates and marker % 10 == 0:
                    copied = candidates[(marker // 10) % len(candidates)]
                    new_tokens.append(replace(token, root=copied))
                    replacements += 1
                else:
                    new_tokens.append(token)
                if token.root in known:
                    within.append(token.root)
            output.append(replace(line, tokens=tuple(new_tokens)))
            remote.extend(previous)
            previous = original_roots
    return output, replacements


def shuffle_lines_within_pages(lines: Sequence[Line]) -> list[Line]:
    output: list[Line] = []
    for page, selected in page_groups(lines):
        shuffled = list(selected)
        random.Random(stable_int(f"IL001-SHUFFLE|{page}")).shuffle(shuffled)
        output.extend(shuffled)
    return output


def normalization_gate(
    lines: Sequence[Line], model: StructuralModel, parameters: dict[str, float]
) -> dict[str, Any]:
    checked = 0
    maximum_error = 0.0
    empty_error = 0.0
    identical_error = 0.0
    for line in lines:
        for token in line.tokens:
            if checked >= 12:
                break
            form_sum = 0.0
            template_sum = 0.0
            for idx in range(model.vocab_size):
                form_sum += model.form_probability(idx, line, token, parameters["form"])
                template_sum += model.template_probability(
                    idx, line, token, parameters["form"], parameters["template"]
                )
            maximum_error = max(
                maximum_error, abs(form_sum - 1.0), abs(template_sum - 1.0)
            )
            idx = model.target_index(token.root)
            base = model.template_probability(
                idx, line, token, parameters["form"], parameters["template"]
            )
            empty_error = max(
                empty_error,
                abs(cache_probability(base, idx, (), parameters["within"]) - base),
            )
            cache = (idx,) if idx != model.unk else ()
            first = cache_probability(base, idx, cache, parameters["within"])
            second = cache_probability(base, idx, tuple(cache), parameters["within"])
            identical_error = max(identical_error, abs(first - second))
            checked += 1
        if checked >= 12:
            break
    passed = maximum_error < 1e-9 and empty_error < 1e-15 and identical_error < 1e-15
    return {
        "passed": passed,
        "contexts_checked": checked,
        "maximum_normalization_error": maximum_error,
        "empty_cache_error": empty_error,
        "identical_cache_error": identical_error,
    }


def validation_power_gates(
    validation: Sequence[Line], model: StructuralModel, parameters: dict[str, float]
) -> dict[str, Any]:
    known = set(model.index) - {UNKNOWN}
    disjoint = {
        "WITHIN": "PREVIOUS",
        "PREVIOUS": "REMOTE_PAGE",
        "REMOTE_PAGE": "PREVIOUS",
    }
    tests: dict[str, Any] = {}
    all_pass = True
    for source in ("WITHIN", "PREVIOUS", "REMOTE_PAGE"):
        planted, replacements = replace_roots_with_copy_signal(validation, source, known)
        score = score_lines(planted, model, parameters)
        intended_gain = score.bpt("TEMPLATE") - score.bpt(source)
        disjoint_gain = score.bpt("TEMPLATE") - score.bpt(disjoint[source])
        passed = (
            replacements > 0
            and intended_gain >= 0.02
            and intended_gain - disjoint_gain >= 0.02
        )
        tests[source] = {
            "replacements": replacements,
            "replacement_fraction": replacements / score.targets,
            "intended_gain_bpt": intended_gain,
            "disjoint_model": disjoint[source],
            "disjoint_gain_bpt": disjoint_gain,
            "passed": passed,
        }
        all_pass &= passed

    planted_previous, _ = replace_roots_with_copy_signal(validation, "PREVIOUS", known)
    ordered_score = score_lines(planted_previous, model, parameters)
    shuffled_score = score_lines(
        shuffle_lines_within_pages(planted_previous), model, parameters
    )
    ordered_gain = ordered_score.bpt("TEMPLATE") - ordered_score.bpt("PREVIOUS")
    shuffled_gain = shuffled_score.bpt("TEMPLATE") - shuffled_score.bpt("PREVIOUS")
    shuffle_passed = ordered_gain - shuffled_gain >= 0.02
    all_pass &= shuffle_passed
    return {
        "passed": all_pass,
        "copy_tests": tests,
        "shuffled_previous": {
            "ordered_gain_bpt": ordered_gain,
            "shuffled_gain_bpt": shuffled_gain,
            "passed": shuffle_passed,
        },
    }


def sign_flip_p(values: Sequence[float], seed: int) -> float:
    vector = np.asarray([value for value in values if math.isfinite(value)], dtype=np.float64)
    if not len(vector):
        return 1.0
    observed = float(vector.mean())
    if len(vector) <= 16:
        masks = np.arange(1 << len(vector), dtype=np.uint64)[:, None]
        bits = (masks >> np.arange(len(vector), dtype=np.uint64)) & 1
        signs = bits.astype(np.float64) * 2.0 - 1.0
        null = (signs * vector[None, :]).mean(axis=1)
        return float((np.count_nonzero(null >= observed - 1e-15) + 1) / (len(null) + 1))
    rng = np.random.default_rng(seed)
    exceed = 0
    done = 0
    batch = 4096
    while done < SIGN_REPEATS:
        size = min(batch, SIGN_REPEATS - done)
        signs = rng.integers(0, 2, size=(size, len(vector)), dtype=np.int8) * 2 - 1
        null = (signs * vector[None, :]).mean(axis=1)
        exceed += int(np.count_nonzero(null >= observed - 1e-15))
        done += size
    return (exceed + 1) / (SIGN_REPEATS + 1)


def bootstrap_ci(values: Sequence[float], seed: int) -> tuple[float, float]:
    vector = np.asarray([value for value in values if math.isfinite(value)], dtype=np.float64)
    if not len(vector):
        return float("nan"), float("nan")
    rng = np.random.default_rng(seed)
    means = np.empty(BOOTSTRAP_REPEATS, dtype=np.float64)
    batch = 1000
    for start in range(0, BOOTSTRAP_REPEATS, batch):
        size = min(batch, BOOTSTRAP_REPEATS - start)
        selected = rng.integers(0, len(vector), size=(size, len(vector)))
        means[start:start + size] = vector[selected].mean(axis=1)
    low, high = np.quantile(means, (0.025, 0.975))
    return float(low), float(high)


def holm_adjust(raw: dict[str, float]) -> dict[str, float]:
    ordered = sorted(raw, key=lambda name: raw[name])
    adjusted: dict[str, float] = {}
    running = 0.0
    count = len(ordered)
    for rank, name in enumerate(ordered):
        value = min(1.0, raw[name] * (count - rank))
        running = max(running, value)
        adjusted[name] = running
    return adjusted


def donor_index(
    event_index: int,
    events: Sequence[dict[str, Any]],
    candidates: dict[tuple[str, str, str], list[int]],
    require_cache: str | None,
) -> int | None:
    event = events[event_index]
    pool = candidates.get(event["line"].stratum, [])
    if not pool:
        return None
    start = stable_int(
        f"IL001-DONOR|{require_cache or 'TEMPLATE'}|{event['page']}|"
        f"{event['locus']}|{event['token_index']}"
    ) % len(pool)
    for offset in range(len(pool)):
        candidate = pool[(start + offset) % len(pool)]
        donor = events[candidate]
        if donor["page"] == event["page"]:
            continue
        if require_cache is not None and not donor["caches"][require_cache]:
            continue
        return candidate
    return None


def resize_sequence(sequence: Sequence[int], size: int, seed: int) -> tuple[int, ...]:
    if size <= 0 or not sequence:
        return ()
    start = seed % len(sequence)
    return tuple(sequence[(start + index) % len(sequence)] for index in range(size))


def decoy_specificity(
    score: Score,
    model: StructuralModel,
    parameters: dict[str, float],
) -> dict[str, Any]:
    events = score.events
    all_candidates: dict[tuple[str, str, str], list[int]] = defaultdict(list)
    cache_candidates: dict[str, dict[tuple[str, str, str], list[int]]] = {
        name: defaultdict(list) for name in CACHE_MODELS
    }
    for index, event in enumerate(events):
        stratum = event["line"].stratum
        all_candidates[stratum].append(index)
        for name in CACHE_MODELS:
            if event["caches"][name]:
                cache_candidates[name][stratum].append(index)

    decoy_bits: dict[str, Counter[str]] = {
        name: Counter() for name in GAIN_MODELS
    }
    actual_bits: dict[str, Counter[str]] = {
        name: Counter() for name in GAIN_MODELS
    }
    available: dict[str, Counter[str]] = {
        name: Counter() for name in GAIN_MODELS
    }
    for event_index, event in enumerate(events):
        line: Line = event["line"]
        token: Token = event["token"]
        idx = event["idx"]

        donor = donor_index(event_index, events, all_candidates, None)
        if donor is not None:
            donor_event = events[donor]
            donor_line: Line = donor_event["line"]
            donor_token: Token = donor_event["token"]
            tail = (
                donor_token.position_bin,
                int(donor_line.paragraph_start),
                donor_token.length_bin,
            )
            probability = model.template_probability(
                idx, line, token, parameters["form"], parameters["template"], tail
            )
            decoy_bits["TEMPLATE"][event["page"]] += -math.log2(probability)
            actual_bits["TEMPLATE"][event["page"]] += -math.log2(event["p_template"])
            available["TEMPLATE"][event["page"]] += 1

        for name in CACHE_MODELS:
            actual = event["caches"][name]
            if not actual:
                # Empty actual caches are exact baseline equalities and carry no
                # context-specificity information.
                continue
            donor = donor_index(event_index, events, cache_candidates[name], name)
            if donor is None:
                continue
            donor_sequence = events[donor]["caches"][name]
            resized = resize_sequence(
                donor_sequence,
                len(actual),
                stable_int(f"IL001-RESIZE|{name}|{event['page']}|{event['locus']}|{event['token_index']}"),
            )
            probability = cache_probability(
                event["p_template"], idx, resized, parameters[name.lower()]
            )
            decoy_bits[name][event["page"]] += -math.log2(probability)
            actual_probability = cache_probability(
                event["p_template"], idx, actual, parameters[name.lower()]
            )
            actual_bits[name][event["page"]] += -math.log2(actual_probability)
            available[name][event["page"]] += 1

    output: dict[str, Any] = {}
    for name in GAIN_MODELS:
        page_differences = []
        total_available = 0
        actual_available_bits = 0.0
        decoy_available_bits = 0.0
        for page, count in available[name].items():
            if not count:
                continue
            actual = actual_bits[name][page]
            decoy = decoy_bits[name][page]
            page_differences.append((decoy - actual) / count)
            total_available += count
            actual_available_bits += actual
            decoy_available_bits += decoy
        output[name] = {
            "available_targets": total_available,
            "availability_fraction": total_available / score.targets,
            "actual_minus_decoy_gain_bpt": (
                (decoy_available_bits - actual_available_bits) / total_available
                if total_available else float("nan")
            ),
            "page_mean_actual_minus_decoy_gain_bpt": (
                float(np.mean(page_differences)) if page_differences else float("nan")
            ),
            "raw_p": sign_flip_p(page_differences, SEED + 100 + len(output)),
            "pages": len(page_differences),
        }
    adjusted = holm_adjust({name: row["raw_p"] for name, row in output.items()})
    for name in output:
        output[name]["holm_p"] = adjusted[name]
    return output


def registered_gains(score: Score) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for index, (name, baseline) in enumerate(GAIN_MODELS.items()):
        gain = score.bpt(baseline) - score.bpt(name)
        page_values = [
            (score.page_bits[page][baseline] - score.page_bits[page][name])
            / score.page_targets[page]
            for page in sorted(score.page_targets)
        ]
        low, high = bootstrap_ci(page_values, SEED + 200 + index)
        output[name] = {
            "baseline": baseline,
            "gain_bpt": gain,
            "relative_improvement": gain / score.bpt(baseline),
            "page_mean_gain_bpt": float(np.mean(page_values)),
            "page_bootstrap_95_ci": [low, high],
            "pages": len(page_values),
        }
    return output


def edition_final(
    edition: str, parameters: dict[str, float], collect_events: bool = False
) -> tuple[StructuralModel, Score, dict[str, Any]]:
    lines = load_lines(SOURCES[edition])
    train = select_split(lines, "train")
    test = select_split(lines, "test")
    model = StructuralModel(train)
    score = score_lines(test, model, parameters, collect_events=collect_events)
    return model, score, {
        "inventory": corpus_inventory(lines),
        "vocabulary": model.vocab_size,
        "unknown_targets": sum(
            model.target_index(token.root) == model.unk
            for line in test for token in line.tokens
        ),
        "bpt": {name: score.bpt(name) for name in MODEL_NAMES},
        "gains": registered_gains(score),
    }


def interpret(
    gains: dict[str, Any], specificity: dict[str, Any], sensitivity: dict[str, Any]
) -> tuple[str, dict[str, bool]]:
    material: dict[str, bool] = {}
    for name, row in gains.items():
        same_direction = all(
            sensitivity[edition]["gains"][name]["gain_bpt"] > 0
            for edition in ("IT2a", "RF1b")
        )
        material[name] = bool(
            row["gain_bpt"] >= 0.02
            and row["relative_improvement"] >= 0.01
            and specificity[name]["holm_p"] <= 0.05
            and same_direction
        )

    active = [name for name, value in material.items() if value]
    if not active:
        interpretation = (
            "No registered information channel met the frozen materiality rule; "
            "the representation is non-discriminating for system class."
        )
    elif len(active) > 1:
        interpretation = (
            "Mixed information location: " + ", ".join(active) +
            " meet the frozen rule, so all compatible system classes remain open."
        )
    elif active == ["PREVIOUS"] and (
        gains["PREVIOUS"]["gain_bpt"] > gains["REMOTE_PAGE"]["gain_bpt"]
    ):
        interpretation = (
            "Immediate sequential context is specifically supported; this is "
            "discourse-like organization but does not establish natural language."
        )
    elif active == ["REMOTE_PAGE"]:
        interpretation = (
            "Nonadjacent page context is supported without an immediate-line result; "
            "catalogue, topic, or mnemonic organization gains support."
        )
    elif active == ["TEMPLATE"]:
        interpretation = (
            "Fixed within-line slots are supported without cross-line information; "
            "record/formulary or local generative accounts gain support."
        )
    else:
        interpretation = (
            f"Only {active[0]} met the frozen rule; this locates predictive "
            "information but does not uniquely select a manuscript-system class."
        )
    return interpretation, material


def report_markdown(result: dict[str, Any]) -> str:
    primary = result["editions"]["ZL3b"]
    rows = []
    for name in GAIN_MODELS:
        gain = primary["gains"][name]
        spec = result["specificity"][name]
        rows.append(
            f"| {name} | {gain['baseline']} | {gain['gain_bpt']:.4f} | "
            f"{100 * gain['relative_improvement']:.2f}% | {spec['holm_p']:.6g} | "
            f"{'yes' if result['material'][name] else 'no'} |"
        )
    sensitivity_rows = []
    for edition in ("IT2a", "RF1b"):
        values = result["editions"][edition]["gains"]
        sensitivity_rows.append(
            f"| {edition} | " + " | ".join(f"{values[name]['gain_bpt']:.4f}" for name in GAIN_MODELS) + " |"
        )
    return "\n".join([
        "# IL001 — text-only information-location result",
        "",
        f"Status: **{result['status']}**",
        "",
        "## Outcome",
        "",
        result["interpretation"],
        "",
        "This result assigns no word meaning, part of speech, language, cipher, or plaintext.",
        "",
        "## Frozen held ZL3b result",
        "",
        "| Model | Baseline | gain (bit/target) | relative | Holm p | material |",
        "|---|---|---:|---:|---:|---|",
        *rows,
        "",
        f"Held targets: {primary['targets']}; held pages: {primary['pages']}; "
        f"unknown targets: {primary['unknown_targets']}.",
        "",
        "## Alternate-reading directional sensitivity",
        "",
        "The readings are sensitivity analyses of the same manuscript, not replications.",
        "",
        "| Reading | TEMPLATE | WITHIN | PREVIOUS | REMOTE_PAGE | FULL_CONTEXT |",
        "|---|---:|---:|---:|---:|---:|",
        *sensitivity_rows,
        "",
        "## Safeguards",
        "",
        "- Manual ZL3b/IT2a/RF1b transcription only.",
        "- No OCR, image, embedding, visual model, dictionary, or proposed gloss was loaded.",
        "- Page split, target representation, model family, thresholds, and nulls were preregistered.",
        "- Hyperparameters were selected on validation; the final runner hash was verified before scoring.",
        "- Complete numeric output and validation gates are in the accompanying JSON.",
        "",
    ])


def selftest() -> None:
    shell: FormShell = ((0, "NONE", "NONE", "NONE", "NONE"),)
    def token(root: str, position: int) -> Token:
        return Token((root,), shell, position, "2-4")
    train = [
        Line("f1r", f"f1r.{line + 1}", "A", "H", "1", line == 0,
             tuple(token(root, index) for index, root in enumerate(roots)))
        for line, roots in enumerate((("a", "b", "a"), ("b", "a", "b"), ("a", "a", "b")))
    ]
    validation = [
        replace(line, page=page, locus=line.locus.replace("f1r", page))
        for page in ("f2r", "f3r") for line in train
    ]
    model = StructuralModel(train)
    parameters = {name: 8.0 for name in ("form", "template", "within", "previous", "remote_page", "full_context")}
    score = score_lines(validation, model, parameters, collect_events=True)
    assert score.targets == 18
    assert all(math.isfinite(score.bpt(name)) for name in MODEL_NAMES)
    gate = normalization_gate(validation, model, parameters)
    assert gate["passed"], gate
    specificity = decoy_specificity(score, model, parameters)
    assert set(specificity) == set(GAIN_MODELS)
    assert all(math.isfinite(row["holm_p"]) for row in specificity.values())
    assert split_bucket("f1r") == split_bucket("F1R")
    print(json.dumps({
        "status": "PASS", "targets": score.targets,
        "normalization": gate,
        "decoy_models": sorted(specificity),
    }, indent=2))


def validation_phase() -> None:
    started = time.perf_counter()
    lines = load_lines(SOURCES["ZL3b"])
    inventory = corpus_inventory(lines)
    split_gate = all(inventory[name]["pages"] and inventory[name]["targets"] for name in inventory)
    train = select_split(lines, "train")
    validation = select_split(lines, "validation")
    model, parameters, tuning = tune_parameters(train, validation)
    normalization = normalization_gate(validation, model, parameters)
    power = validation_power_gates(validation, model, parameters)
    gates = {
        "split_nonempty": split_gate,
        "normalization_and_cache_controls": normalization["passed"],
        "planted_power": power["passed"],
    }
    passed = all(gates.values())
    result = {
        "experiment": "IL001",
        "phase": "VALIDATION_FROZEN" if passed else "VALIDATION_FAILED",
        "created": "2026-08-06",
        "runner_sha256": sha256_path(Path(__file__)),
        "preregistration_sha256": sha256_path(PREREG),
        "source_sha256": {name: sha256_path(path) for name, path in SOURCES.items()},
        "parameters": parameters,
        "grid": GRID,
        "inventory": inventory,
        "gates": gates,
        "normalization": normalization,
        "power": power,
        "tuning": tuning,
        "elapsed_seconds": time.perf_counter() - started,
    }
    RESULTS.mkdir(parents=True, exist_ok=True)
    FROZEN.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    if not passed:
        raise SystemExit(2)


def final_phase() -> None:
    started = time.perf_counter()
    frozen = json.loads(FROZEN.read_text(encoding="utf-8"))
    current_hash = sha256_path(Path(__file__))
    current_prereg = sha256_path(PREREG)
    if frozen.get("phase") != "VALIDATION_FROZEN":
        raise RuntimeError("validation did not freeze a passing configuration")
    if current_hash != frozen["runner_sha256"]:
        raise RuntimeError("runner changed after validation freeze")
    if current_prereg != frozen["preregistration_sha256"]:
        raise RuntimeError("preregistration changed after validation freeze")
    for edition, path in SOURCES.items():
        if sha256_path(path) != frozen["source_sha256"][edition]:
            raise RuntimeError(f"manual source changed after validation: {edition}")

    parameters = {key: float(value) for key, value in frozen["parameters"].items()}
    zl_model, zl_score, zl_summary = edition_final("ZL3b", parameters, collect_events=True)
    editions = {
        "ZL3b": {
            **zl_summary,
            "targets": zl_score.targets,
            "pages": len(zl_score.page_targets),
        }
    }
    for edition in ("IT2a", "RF1b"):
        _model, score, summary = edition_final(edition, parameters)
        editions[edition] = {
            **summary,
            "targets": score.targets,
            "pages": len(score.page_targets),
        }

    specificity = decoy_specificity(zl_score, zl_model, parameters)
    interpretation, material = interpret(
        editions["ZL3b"]["gains"], specificity, editions
    )
    result = {
        "experiment": "IL001",
        "status": "FINAL_HELD_EVALUATED",
        "created": "2026-08-06",
        "runner_sha256": current_hash,
        "preregistration_sha256": current_prereg,
        "parameters": parameters,
        "validation_gates": frozen["gates"],
        "editions": editions,
        "specificity": specificity,
        "material": material,
        "interpretation": interpretation,
        "elapsed_seconds": time.perf_counter() - started,
    }
    OUTPUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUTPUT_REPORT.write_text(report_markdown(result), encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--phase", choices=("selftest", "inventory", "validate", "final"), required=True
    )
    args = parser.parse_args()
    if args.phase == "selftest":
        selftest()
    elif args.phase == "inventory":
        print(json.dumps({name: corpus_inventory(load_lines(path)) for name, path in SOURCES.items()}, indent=2, sort_keys=True))
    elif args.phase == "validate":
        validation_phase()
    else:
        final_phase()


if __name__ == "__main__":
    main()
