#!/usr/bin/env python3
"""Blind internal segmentation and key recovery on the Naibbe control.

The primary configuration is the public capacity-saturated U=138 model. The
115 and 132 models are retained only as exploratory sensitivity outputs. All
segmentations and keys are serialized and hashed before this process opens the
published table or aligned plaintext.
"""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import io
import json
import math
import sys
import tempfile
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
HERE = Path(__file__).resolve().parent.parent
OUT = HERE / "artifacts"
CACHE = Path(tempfile.gettempdir()) / "gdt603_naibbe_end_to_end_control"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


G601 = load_module(
    "gdt601_for_gdt603",
    ROOT / "experiments/yolo/gdt601_naibbe_literal_key_attack/src/run.py",
)
G602 = load_module(
    "gdt602_for_gdt603",
    ROOT / "experiments/yolo/gdt602_naibbe_blind_key_recovery/src/run.py",
)

ACTIVE_LATIN = "abcdefghilmnopqrstuvxyz"
TABLES = 6
STATE_CAPACITY = len(ACTIVE_LATIN) * TABLES
PRIMARY_U_SIZE = STATE_CAPACITY
NAVIGATION_U_SIZES = (115, 132)
VARIANTS = (*NAVIGATION_U_SIZES, PRIMARY_U_SIZE)
KEY_ITERATIONS = 40_000
KEY_RESTARTS = 2
KEY_SEED = 20_260_828


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_bytes(value) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        + "\n"
    ).encode()


def pretty_bytes(value) -> bytes:
    return (
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    ).encode()


def fetch_url(name: str, url: str, expected_sha256: str) -> Path:
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / name
    data = path.read_bytes() if path.is_file() else b""
    if sha256_bytes(data) != expected_sha256:
        with urllib.request.urlopen(url, timeout=60) as response:
            data = response.read()
        if sha256_bytes(data) != expected_sha256:
            raise RuntimeError(f"source hash mismatch for {name}")
        temporary = path.with_suffix(path.suffix + ".tmp")
        temporary.write_bytes(data)
        temporary.replace(path)
    return path


def fetch_blind_sources() -> tuple[Path, Path]:
    """Fetch only ciphertext and independent LM material before the freeze."""
    cipher_spec = G601.SOURCES["nathist_output_ciphertext.txt"]
    caesar_spec = G601.SOURCES["caesar_la.txt"]
    cipher = fetch_url(
        "nathist_output_ciphertext.txt",
        cipher_spec["url"],
        cipher_spec["sha256"],
    )
    caesar = fetch_url("caesar_la.txt", caesar_spec["url"], caesar_spec["sha256"])
    return cipher, caesar


def fetch_oracle_sources() -> tuple[Path, Path]:
    """Called only after the blind artifact has been written and rehashed."""
    table_spec = G601.SOURCES["naibbe_tables.csv"]
    table = fetch_url("naibbe_tables.csv", table_spec["url"], table_spec["sha256"])
    plaintext = fetch_url(
        "nathist_pre_encryption_respaced_plaintext.txt",
        G602.PLAINTEXT_URL,
        G602.PLAINTEXT_SHA256,
    )
    return table, plaintext


def cuts(token: str):
    return range(1, len(token))


def greedy_side(
    side: str,
    other: set[str],
    bigram_types: set[str],
    frequencies: Counter,
) -> set[str]:
    incidence: dict[str, set[str]] = defaultdict(set)
    for token in sorted(bigram_types):
        for cut in cuts(token):
            prefix, suffix = token[:cut], token[cut:]
            if side == "P" and suffix in other:
                incidence[prefix].add(token)
            elif side == "S" and prefix in other:
                incidence[suffix].add(token)
    covered: set[str] = set()
    selected: set[str] = set()
    for _ in range(STATE_CAPACITY):
        choices = []
        for component, support in incidence.items():
            new = support - covered
            choices.append(
                (
                    len(new),
                    sum(min(frequencies[token], 5) for token in new),
                    -len(component),
                    component,
                )
            )
        if not choices:
            break
        best_key = max(choices)
        if best_key[0] == 0:
            break
        best = best_key[3]
        selected.add(best)
        covered.update(incidence.pop(best))
    return selected


def initial_suffixes(unigrams: set[str], types: set[str]) -> set[str]:
    bigrams = types - unigrams
    prefix_support = Counter()
    suffix_support = Counter()
    for token in sorted(bigrams):
        for cut in cuts(token):
            prefix_support[token[:cut]] += 1
            suffix_support[token[cut:]] += 1
    assignment = {}
    for token in sorted(bigrams):
        candidates = []
        for cut in cuts(token):
            left = prefix_support[token[:cut]]
            right = suffix_support[token[cut:]]
            harmonic = 2.0 / (1.0 / left + 1.0 / right)
            candidates.append((harmonic, -cut, cut))
        if candidates:
            assignment[token] = max(candidates)[2]
    counts = Counter(token[cut:] for token, cut in assignment.items())
    ordered = sorted(counts, key=lambda value: (-counts[value], len(value), value))
    return set(ordered[:STATE_CAPACITY])


def induce_dictionaries(
    unigrams: set[str],
    suffixes: set[str],
    types: set[str],
    frequencies: Counter,
) -> tuple[set[str], set[str]]:
    bigrams = types - unigrams
    for _ in range(3):
        prefixes = greedy_side("P", suffixes, bigrams, frequencies)
        suffixes = greedy_side("S", prefixes, bigrams, frequencies)
    return greedy_side("P", suffixes, bigrams, frequencies), suffixes


def fit_cuts(
    unigrams: set[str],
    prefixes: set[str],
    suffixes: set[str],
    types: set[str],
    frequencies: Counter,
):
    bigrams = types - unigrams
    assignment = {}
    for token in sorted(bigrams):
        viable = [
            cut
            for cut in cuts(token)
            if token[:cut] in prefixes and token[cut:] in suffixes
        ]
        if viable:
            assignment[token] = viable[0]
    prefix_count = Counter()
    suffix_count = Counter()
    for _ in range(6):
        prefix_count = Counter()
        suffix_count = Counter()
        for token, cut in assignment.items():
            prefix_count[token[:cut]] += frequencies[token]
            suffix_count[token[cut:]] += frequencies[token]
        for token in sorted(bigrams):
            viable = [
                cut
                for cut in cuts(token)
                if token[:cut] in prefixes and token[cut:] in suffixes
            ]
            if viable:
                assignment[token] = max(
                    viable,
                    key=lambda cut: (
                        (prefix_count[token[:cut]] + 0.5)
                        * (suffix_count[token[cut:]] + 0.5),
                        -cut,
                    ),
                )
    return assignment, prefix_count, suffix_count


def fit_segmentation(u_size: int, frequencies: Counter) -> dict:
    types = set(frequencies)
    unigrams = {token for token, _count in frequencies.most_common(u_size)}
    suffixes = initial_suffixes(unigrams, types)
    for _ in range(6):
        prefixes, suffixes = induce_dictionaries(
            unigrams, suffixes, types, frequencies
        )
        assignment, prefix_count, suffix_count = fit_cuts(
            unigrams, prefixes, suffixes, types, frequencies
        )
        bigram_events = sum(frequencies[token] for token in assignment)
        evidence = []
        for token, observed in frequencies.items():
            viable = [
                cut
                for cut in cuts(token)
                if token[:cut] in prefixes and token[cut:] in suffixes
            ]
            if not viable:
                deviance = math.inf
            else:
                expected = max(
                    (prefix_count[token[:cut]] + 0.5)
                    * (suffix_count[token[cut:]] + 0.5)
                    / (bigram_events + 0.5 * max(1, len(prefixes)))
                    for cut in viable
                )
                deviance = (
                    observed * math.log(observed / expected) - observed + expected
                    if observed > expected
                    else 0.0
                )
            evidence.append((deviance, token))
        updated = {token for _score, token in sorted(evidence, reverse=True)[:u_size]}
        if updated == unigrams:
            break
        unigrams = updated

    prefixes, suffixes = induce_dictionaries(unigrams, suffixes, types, frequencies)
    assignment, prefix_count, suffix_count = fit_cuts(
        unigrams, prefixes, suffixes, types, frequencies
    )
    missing = sorted((types - unigrams) - set(assignment))
    if missing:
        raise RuntimeError(f"unfactorable non-U types: {missing[:10]}")
    used_prefixes = set(prefix_count)
    used_suffixes = set(suffix_count)
    if max(len(unigrams), len(used_prefixes), len(used_suffixes)) > STATE_CAPACITY:
        raise RuntimeError("public state capacity exceeded")
    mapping = {
        token: (
            {"state": "U"}
            if token in unigrams
            else {"state": "B", "cut": assignment[token]}
        )
        for token in sorted(types)
    }
    return {
        "u_size": u_size,
        "inventories": {
            "U": len(unigrams),
            "P": len(used_prefixes),
            "S": len(used_suffixes),
        },
        "token_map": mapping,
    }


def segmented_lines(cipher_lines: list[str], segmentation: dict) -> list[list[str]]:
    token_map = segmentation["token_map"]
    output = []
    for physical in cipher_lines:
        units = []
        for token in physical.split():
            record = token_map[token]
            if record["state"] == "U":
                units.append("U|" + token)
            else:
                cut = int(record["cut"])
                units.extend(("P|" + token[:cut], "S|" + token[cut:]))
        if units:
            output.append(units)
    return output


def recover_key(
    cipher_lines: list[str], segmentation: dict, caesar_path: Path, u_size: int
) -> dict:
    units = segmented_lines(cipher_lines, segmentation)
    model = G602.fit_latin({"caesar_la.txt": caesar_path}, 4)
    problem = G602.build_blind_problem(units, model)
    score, key = G602.solve(
        problem,
        KEY_ITERATIONS,
        KEY_RESTARTS,
        KEY_SEED + u_size,
        capacity=True,
    )
    key_map = {
        code: G602.ALPHABET[int(key[index])]
        for index, code in enumerate(problem.vocab)
    }
    return {
        "u_size": u_size,
        "iterations": KEY_ITERATIONS,
        "restarts": KEY_RESTARTS,
        "seed": KEY_SEED + u_size,
        "code_types": len(problem.vocab),
        "lm_events": len(problem.obs),
        "score_bits_per_event": score / len(problem.obs),
        "key": key_map,
        "code_counts": problem.counts,
    }


def truth_records(cipher_path: Path, table_path: Path, plaintext_path: Path):
    reverse = G601.reverse_tables(table_path)
    records = []
    true_key = {}
    cipher_lines = cipher_path.read_text().splitlines()
    plaintext_lines = plaintext_path.read_text().splitlines()
    if len(cipher_lines) != len(plaintext_lines):
        raise RuntimeError("control line-count mismatch")
    for line_number, (plain_line, cipher_line) in enumerate(
        zip(plaintext_lines, cipher_lines), start=1
    ):
        plain_tokens = plain_line.split()
        cipher_tokens = cipher_line.split()
        if len(plain_tokens) != len(cipher_tokens):
            raise RuntimeError(f"token alignment mismatch on line {line_number}")
        for plain, cipher in zip(plain_tokens, cipher_tokens):
            if len(plain) == 1:
                if plain not in reverse["unigram"].get(cipher, ()):
                    raise RuntimeError("unigram truth mismatch")
                truth = {"state": "U", "cut": None, "units": [("U|" + cipher, plain)]}
            elif len(plain) == 2:
                viable = [
                    cut
                    for cut in cuts(cipher)
                    if plain[0] in reverse["prefix"].get(cipher[:cut], ())
                    and plain[1] in reverse["suffix"].get(cipher[cut:], ())
                ]
                if len(viable) != 1:
                    raise RuntimeError("bigram truth mismatch")
                cut = viable[0]
                truth = {
                    "state": "B",
                    "cut": cut,
                    "units": [
                        ("P|" + cipher[:cut], plain[0]),
                        ("S|" + cipher[cut:], plain[1]),
                    ],
                }
            else:
                raise RuntimeError("control chunks must contain one or two letters")
            for code, letter in truth["units"]:
                old = true_key.setdefault(code, letter)
                if old != letter:
                    raise RuntimeError("true state-specific code is nondeterministic")
            records.append((cipher, plain, truth))
    return records, true_key


def edit_distance(left: str, right: str) -> int:
    previous = list(range(len(right) + 1))
    for i, left_char in enumerate(left, start=1):
        current = [i]
        for j, right_char in enumerate(right, start=1):
            current.append(
                min(
                    current[-1] + 1,
                    previous[j] + 1,
                    previous[j - 1] + (left_char != right_char),
                )
            )
        previous = current
    return previous[-1]


def evaluate(segmentation: dict, key_record: dict, records, true_key: dict) -> dict:
    token_map = segmentation["token_map"]
    key = key_record["key"]
    state_ok = exact_segmentation = true_bigram = predicted_bigram = boundary_tp = 0
    exact_decoded = exact_condition_chars = exact_condition_ok = 0
    true_chars = predicted_chars = edit_errors = 0
    truth_by_type: dict[str, Counter] = defaultdict(Counter)
    errors = Counter()
    for cipher, plain, truth in records:
        predicted = token_map[cipher]
        predicted_state = predicted["state"]
        truth_state = truth["state"]
        state_match = predicted_state == truth_state
        segmentation_match = state_match and (
            truth_state == "U" or int(predicted["cut"]) == truth["cut"]
        )
        state_ok += state_match
        exact_segmentation += segmentation_match
        true_bigram += truth_state == "B"
        predicted_bigram += predicted_state == "B"
        boundary_tp += segmentation_match and truth_state == "B"
        truth_by_type[cipher][(truth_state, truth["cut"])] += 1

        if predicted_state == "U":
            predicted_units = ["U|" + cipher]
        else:
            cut = int(predicted["cut"])
            predicted_units = ["P|" + cipher[:cut], "S|" + cipher[cut:]]
        decoded = "".join(key[code] for code in predicted_units)
        exact_decoded += decoded == plain
        true_chars += len(plain)
        predicted_chars += len(decoded)
        edit_errors += edit_distance(decoded, plain)
        if segmentation_match:
            exact_condition_chars += len(plain)
            exact_condition_ok += sum(a == b for a, b in zip(decoded, plain))
        if not segmentation_match:
            errors[(truth_state, predicted_state, truth["cut"], predicted.get("cut"))] += 1

    type_state_ok = type_exact_ok = 0
    for token, alternatives in truth_by_type.items():
        truth_state, truth_cut = max(
            alternatives.items(), key=lambda item: (item[1], item[0])
        )[0]
        predicted = token_map[token]
        type_state_ok += predicted["state"] == truth_state
        type_exact_ok += predicted["state"] == truth_state and (
            truth_state == "U" or int(predicted["cut"]) == truth_cut
        )

    intersection = set(key) & set(true_key)
    key_type_ok = sum(key[code] == true_key[code] for code in intersection)
    key_occurrences = key_occurrence_ok = 0
    for _cipher, _plain, truth in records:
        for code, letter in truth["units"]:
            if code in key:
                key_occurrences += 1
                key_occurrence_ok += key[code] == letter
    precision = boundary_tp / predicted_bigram
    recall = boundary_tp / true_bigram
    return {
        "u_size": segmentation["u_size"],
        "inventories": segmentation["inventories"],
        "token_occurrences": len(records),
        "token_types": len(truth_by_type),
        "state_accuracy_occurrence": state_ok / len(records),
        "state_majority_accuracy_type": type_state_ok / len(truth_by_type),
        "exact_segmentation_accuracy_occurrence": exact_segmentation / len(records),
        "exact_segmentation_majority_accuracy_type": type_exact_ok / len(truth_by_type),
        "true_bigram_tokens": true_bigram,
        "predicted_bigram_tokens": predicted_bigram,
        "boundary_precision": precision,
        "boundary_recall": recall,
        "boundary_f1": 2 * precision * recall / (precision + recall),
        "key_type_intersection": len(intersection),
        "key_type_accuracy_on_intersection": key_type_ok / len(intersection),
        "key_occurrence_coverage": key_occurrences / true_chars,
        "key_accuracy_on_covered_true_units": key_occurrence_ok / key_occurrences,
        "key_accuracy_given_exact_segmentation": exact_condition_ok / exact_condition_chars,
        "exact_decoded_token_rate": exact_decoded / len(records),
        "predicted_characters": predicted_chars,
        "true_characters": true_chars,
        "end_to_end_edit_accuracy": 1.0 - edit_errors / true_chars,
        "top_segmentation_error_classes": [
            {
                "truth_state": fields[0],
                "predicted_state": fields[1],
                "truth_cut": fields[2],
                "predicted_cut": fields[3],
                "count": count,
            }
            for fields, count in errors.most_common(12)
        ],
    }


def tsv_bytes(fields: list[str], rows: list[dict]) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, delimiter="\t", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode()


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)

    # Blind phase. These two paths are the only source paths passed into it.
    cipher_path, caesar_path = fetch_blind_sources()
    cipher_bytes = cipher_path.read_bytes()
    cipher_lines = cipher_bytes.decode().splitlines()
    frequencies = Counter(token for line in cipher_lines for token in line.split())
    segmentations = {
        str(u_size): fit_segmentation(u_size, frequencies) for u_size in VARIANTS
    }
    keys = {
        str(u_size): recover_key(
            cipher_lines, segmentations[str(u_size)], caesar_path, u_size
        )
        for u_size in VARIANTS
    }
    blind_payload = {
        "schema": "gdt603-blind-freeze-v1",
        "cipher_sha256": sha256_bytes(cipher_bytes),
        "caesar_sha256": sha256_bytes(caesar_path.read_bytes()),
        "active_latin_letters": ACTIVE_LATIN,
        "public_tables": TABLES,
        "state_capacity": STATE_CAPACITY,
        "primary_u_size": PRIMARY_U_SIZE,
        "navigation_u_sizes": list(NAVIGATION_U_SIZES),
        "segmentations": segmentations,
        "keys": keys,
        "oracle_sources_opened": False,
    }
    freeze_bytes = canonical_bytes(blind_payload)
    freeze_path = OUT / "gdt603_blind_freeze.json"
    freeze_path.write_bytes(freeze_bytes)
    freeze_sha256 = sha256_bytes(freeze_path.read_bytes())
    if freeze_sha256 != sha256_bytes(freeze_bytes):
        raise RuntimeError("blind freeze roundtrip failed")

    # Oracle phase starts only after the complete blind payload is immutable.
    table_path, plaintext_path = fetch_oracle_sources()
    if sha256_bytes(freeze_path.read_bytes()) != freeze_sha256:
        raise RuntimeError("blind artifact changed before evaluation")
    records, true_key = truth_records(cipher_path, table_path, plaintext_path)
    evaluations = [
        evaluate(segmentations[str(u_size)], keys[str(u_size)], records, true_key)
        for u_size in VARIANTS
    ]
    primary = next(row for row in evaluations if row["u_size"] == PRIMARY_U_SIZE)
    status = (
        "END_TO_END_NAIBBE_CONTROL_RECOVERED_AT_PUBLIC_CAPACITY"
        if primary["exact_segmentation_accuracy_occurrence"] >= 0.95
        and primary["end_to_end_edit_accuracy"] >= 0.94
        and primary["key_accuracy_given_exact_segmentation"] >= 0.99
        else "END_TO_END_CONTROL_NOT_RECOVERED"
    )

    result = {
        "experiment_id": "GDT603",
        "status": status,
        "question": "Can the public-capacity Naibbe architecture be recovered end to end from ciphertext tokens without internal U/P/S boundaries, key, table, or aligned plaintext?",
        "configuration": {
            "primary_u_size": PRIMARY_U_SIZE,
            "primary_reason": "public capacity-saturated U inventory; no oracle-tuned size selector",
            "navigation_u_sizes": list(NAVIGATION_U_SIZES),
            "navigation_warning": "U=115 has deficient pre-oracle selector provenance and is never the primary claim",
            "state_capacity": STATE_CAPACITY,
            "key_iterations": KEY_ITERATIONS,
            "key_restarts": KEY_RESTARTS,
            "key_seed_base": KEY_SEED,
        },
        "data_separation": {
            "blind_phase_reads": [
                "pinned Naibbe ciphertext",
                "pinned independent Caesar Latin corpus",
                "public 23-letter by six-table capacity",
            ],
            "blind_phase_does_not_read": [
                "published Naibbe table",
                "aligned plaintext",
                "true segmentation",
                "true key",
            ],
            "blind_freeze_sha256": freeze_sha256,
            "oracle_phase_starts_after_freeze": True,
        },
        "sources": {
            "ciphertext": G601.SOURCES["nathist_output_ciphertext.txt"],
            "caesar": G601.SOURCES["caesar_la.txt"],
            "table_evaluation_only": G601.SOURCES["naibbe_tables.csv"],
            "plaintext_evaluation_only": {
                "url": G602.PLAINTEXT_URL,
                "sha256": G602.PLAINTEXT_SHA256,
            },
        },
        "evaluations": evaluations,
        "decision_rule": "primary U=138 exact segmentation >=95%, end-to-end edit accuracy >=94%, and key accuracy given exact segmentation >=99%",
        "claim_ceiling": "Establishes end-to-end recovery only for the modern Naibbe control with given whitespace token boundaries and public architecture. It does not establish that Voynich uses Naibbe, does not recover Voynich plaintext, and does not license the exploratory U=115 selector.",
    }
    (OUT / "gdt603_result.json").write_bytes(pretty_bytes(result))

    segmentation_rows = []
    key_rows = []
    for u_size in VARIANTS:
        segmentation = segmentations[str(u_size)]
        for token, record in segmentation["token_map"].items():
            cut = record.get("cut", -1)
            is_bigram = record["state"] == "B"
            segmentation_rows.append(
                {
                    "u_size": u_size,
                    "primary": int(u_size == PRIMARY_U_SIZE),
                    "token": token,
                    "events": frequencies[token],
                    "state": record["state"],
                    "cut": cut,
                    "prefix": token[:cut] if is_bigram else "NA",
                    "suffix": token[cut:] if is_bigram else "NA",
                }
            )
        key_record = keys[str(u_size)]
        for code, recovered in sorted(key_record["key"].items()):
            state, surface = code.split("|", 1)
            key_rows.append(
                {
                    "u_size": u_size,
                    "primary": int(u_size == PRIMARY_U_SIZE),
                    "state": state,
                    "surface": surface,
                    "events": key_record["code_counts"][code],
                    "recovered": recovered,
                }
            )
    (OUT / "gdt603_blind_segmentations.tsv").write_bytes(
        tsv_bytes(
            ["u_size", "primary", "token", "events", "state", "cut", "prefix", "suffix"],
            segmentation_rows,
        )
    )
    (OUT / "gdt603_recovered_keys.tsv").write_bytes(
        tsv_bytes(
            ["u_size", "primary", "state", "surface", "events", "recovered"],
            key_rows,
        )
    )
    print(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
