#!/usr/bin/env python3
"""Independent reconstruction validator for GDT016 retained results."""
from __future__ import annotations

import csv
import hashlib
import json
import math
import random
from collections import Counter, defaultdict
from pathlib import Path

from run_gdt013_latent_role_propagation import all_strict_groups

ROOT = Path(__file__).resolve().parent
RESULT = ROOT / "gdt016_result.json"
VALIDATION = ROOT / "gdt016_validation.json"
ALPHA = 0.5
SHUFFLES = 20
TRANSITION_PERMS = 2000


def read_tsv(name):
    with (ROOT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()
    ).hexdigest()


def classify(row):
    host = row["residual_host"]
    if int(row["dy_closure"]):
        return "DY_RESOLUTION"
    for prefix, label in (
        ("otar", "OT_AR_LOCAL"), ("oar", "O_AR_LOCAL"),
        ("otal", "OT_AL_LOCAL"), ("oal", "O_AL_LOCAL"),
        ("otol", "OT_OL_LOCAL"), ("ool", "O_OL_LOCAL"),
    ):
        if host.startswith(prefix):
            return label
    if "ar" in host:
        return "AR_REFERENCE"
    if "al" in host:
        return "AL_STATE"
    if "ol" in host:
        return "OL_STATE"
    if "ed" in host:
        return "ED_MEDIUM"
    if "kal" in host:
        return "KAL_INDEX"
    prefix = row["stripped_prefix"]
    if prefix in ("d", "s", "t"):
        return "ENTRY_STATE"
    if prefix == "q":
        return "Q_OUTER_STATE"
    if prefix in ("ch", "sh", "che"):
        return "CARRIER_STATE"
    return "OTHER"


def collapse(sequence):
    out = []
    for value in sequence:
        if not out or out[-1] != value:
            out.append(value)
    return out


def train(sequences):
    unigram = Counter()
    transitions = defaultdict(Counter)
    for sequence in sequences:
        previous = "BOS"
        for value in sequence:
            unigram[value] += 1
            transitions[previous][value] += 1
            previous = value
    return unigram, transitions


def code_bits(sequence, unigram, transitions, alphabet_size):
    unigram_bits = markov_bits = 0.0
    previous = "BOS"
    unigram_total = sum(unigram.values())
    for value in sequence:
        unigram_bits -= math.log2(
            (unigram[value] + ALPHA) / (unigram_total + ALPHA * alphabet_size)
        )
        denominator = sum(transitions[previous].values()) + ALPHA * alphabet_size
        markov_bits -= math.log2((transitions[previous][value] + ALPHA) / denominator)
        previous = value
    return unigram_bits, markov_bits


def close(a, b, tolerance=6e-10):
    return abs(float(a) - float(b)) <= tolerance


def main():
    checks = []
    result = json.loads(RESULT.read_text())
    copy = dict(result)
    digest = copy.pop("result_content_sha256")
    checks += [
        ("schema", result["schema"] == "GDT016_RECORD_STATE_ASSEMBLER_RESULT_V1"),
        ("result_content", digest == canonical_sha(copy)),
    ]
    for part in ("inputs", "implementation", "outputs"):
        for name, expected in result[part].items():
            checks.append((part + ":" + name, sha(ROOT / name) == expected))

    corpus = [
        row for row in all_strict_groups()
        if row["grammar_scope"] == "CONFIRMED_PROSE"
    ]
    grouped = defaultdict(list)
    for row in corpus:
        grouped[row["locus"]].append(row)
    lines = []
    expected_inventory = []
    for locus, rows in sorted(grouped.items()):
        rows.sort(key=lambda row: row["group_index"])
        sequence = []
        for row in rows:
            value = classify(row)
            sequence.append(value)
            expected_inventory.append({
                "locus": locus, "page": row["page"],
                "physical_folio": row["physical_folio"], "section": row["section"],
                "currier": row["currier"], "hand": row["hand"],
                "group_index": str(row["group_index"]), "group_count": str(row["group_count"]),
                "token": row["token"], "stripped_prefix": row["stripped_prefix"],
                "residual_host": row["residual_host"], "dy_closure": str(row["dy_closure"]),
                "family_surface": row["family_surface"], "record_state": value,
            })
        lines.append({
            "locus": locus, "physical_folio": rows[0]["physical_folio"],
            "section": rows[0]["section"], "states": sequence,
        })
    stored_inventory = read_tsv("gdt016_group_state_inventory.tsv")
    checks += [
        ("corpus_count", len(corpus) == result["strict_prose_groups"] == 15592),
        ("line_count", len(lines) == result["lines"] == 2471),
        ("folio_count", len({line["physical_folio"] for line in lines}) == result["folios"] == 94),
        ("inventory_exact", stored_inventory == expected_inventory),
        ("f84r_excluded", not any(row["locus"].startswith("f84r") for row in corpus)),
        ("f84r_flags", result["f84r"] == {"retained": False, "joined": False, "scored": False}),
    ]

    collapsed_counts = Counter(" > ".join(collapse(line["states"])) for line in lines)
    stored_templates = read_tsv("gdt016_recurrent_line_templates.tsv")
    checks += [
        ("template_count", len(stored_templates) == result["recurrent_templates"] == 73),
        ("template_counts", {row["collapsed_template"]: int(row["lines"]) for row in stored_templates}
         == {key: value for key, value in collapsed_counts.items() if value >= 3}),
    ]

    alphabet = sorted({value for line in lines for value in line["states"]})
    folios = sorted({line["physical_folio"] for line in lines})
    stored_folds = {row["held_folio"]: row for row in read_tsv("gdt016_heldout_state_model.tsv")}
    total_unigram = total_markov = total_shuffled = 0.0
    for fold_index, held in enumerate(folios):
        training = [line["states"] for line in lines if line["physical_folio"] != held]
        testing = [line["states"] for line in lines if line["physical_folio"] == held]
        unigram, transitions = train(training)
        ub = mb = shuffled = 0.0
        events = 0
        for line_index, sequence in enumerate(testing):
            a, b = code_bits(sequence, unigram, transitions, len(alphabet))
            ub += a
            mb += b
            events += len(sequence)
            rng = random.Random(160000 + fold_index * 1000 + line_index)
            for _ in range(SHUFFLES):
                alternate = list(sequence)
                rng.shuffle(alternate)
                shuffled += code_bits(alternate, unigram, transitions, len(alphabet))[1] / SHUFFLES
        stored = stored_folds[held]
        checks.append((
            "fold:" + held,
            int(stored["held_lines"]) == len(testing)
            and int(stored["held_states"]) == events
            and close(stored["unigram_bits"], ub)
            and close(stored["markov_bits"], mb)
            and close(stored["shuffled_markov_bits_mean"], shuffled),
        ))
        total_unigram += ub
        total_markov += mb
        total_shuffled += shuffled
    checks += [
        ("held_total_unigram", close(total_unigram, result["unigram_bits"])),
        ("held_total_markov", close(total_markov, result["markov_bits"])),
        ("held_total_shuffle", close(total_shuffled, result["shuffled_markov_bits"])),
        ("held_gain", close(total_unigram - total_markov, result["markov_gain_vs_unigram"])),
        ("order_gain", close(total_shuffled - total_markov, result["true_order_gain_vs_shuffle"])),
    ]

    observed = Counter()
    expected = Counter()
    for line in lines:
        sequence = line["states"]
        counts = Counter(sequence)
        n = len(sequence)
        observed.update(zip(sequence, sequence[1:]))
        if n > 1:
            for left in alphabet:
                for right in alphabet:
                    expected[(left, right)] += counts[left] * (counts[right] - (left == right)) / n
    eligible = [
        key for key in expected
        if expected[key] > 0 and (observed[key] >= 3 or expected[key] >= 3)
    ]
    deviation = {key: abs(observed[key] - expected[key]) for key in eligible}
    extreme = Counter()
    destinations = ("OT_AR_LOCAL", "OT_AL_LOCAL", "OT_OL_LOCAL")
    inherited_observed = sum(observed[("DY_RESOLUTION", value)] for value in destinations)
    inherited_expected = sum(expected[("DY_RESOLUTION", value)] for value in destinations)
    inherited_extreme = 0
    rng = random.Random(161616)
    for _ in range(TRANSITION_PERMS):
        permuted = Counter()
        for line in lines:
            alternate = list(line["states"])
            rng.shuffle(alternate)
            permuted.update(zip(alternate, alternate[1:]))
        for key in eligible:
            extreme[key] += abs(permuted[key] - expected[key]) >= deviation[key] - 1e-12
        inherited_extreme += sum(
            permuted[("DY_RESOLUTION", value)] for value in destinations
        ) >= inherited_observed
    stored_atlas = {
        (row["from_state"], row["to_state"]): row
        for row in read_tsv("gdt016_transition_atlas.tsv")
    }
    checks.append(("transition_count", len(stored_atlas) == result["transition_tests"] == len(eligible)))
    for key in eligible:
        row = stored_atlas[key]
        p = (extreme[key] + 1) / (TRANSITION_PERMS + 1)
        checks.append((
            "transition:" + "->".join(key),
            int(row["observed"]) == observed[key]
            and close(row["within_line_shuffle_expected"], expected[key])
            and close(row["local_p"], p)
            and close(row["adjusted_p"], min(1.0, p * len(eligible))),
        ))
    stored_inherited = read_tsv("gdt016_inherited_hypothesis_tests.tsv")[0]
    inherited_p = (inherited_extreme + 1) / (TRANSITION_PERMS + 1)
    checks += [
        ("inherited_observed", int(stored_inherited["observed"]) == inherited_observed == 69),
        ("inherited_expected", close(stored_inherited["within_line_shuffle_expected"], inherited_expected)),
        ("inherited_p", close(stored_inherited["one_sided_local_p"], inherited_p)
         and close(result["gdt015_inherited_transition"]["one_sided_local_p"], inherited_p)
         and int(result["gdt015_inherited_transition"]["observed"]) == inherited_observed
         and close(result["gdt015_inherited_transition"]["within_line_shuffle_expected"], inherited_expected)
         and result["gdt015_inherited_transition"]["test"] == stored_inherited["test"]),
    ]

    report = (ROOT / "GDT016_RECORD_STATE_ASSEMBLER_REPORT.md").read_text().lower()
    checks += [
        ("ledger", (ROOT / "GDT002_YOLO_LEDGER.tsv").read_text().count("GDT016_CKPT001") == 1),
        ("claim_ceiling", all(term in report for term in (
            "post-selected", "no morpheme", "no transition has", "f84r was not retained"
        ))),
    ]
    failures = [name for name, ok in checks if not ok]
    validation = {
        "schema": "GDT016_RECORD_STATE_ASSEMBLER_VALIDATION_V1",
        "status": "PASS" if not failures else "FAIL",
        "checks": len(checks),
        "failures": failures,
        "result_sha256": sha(RESULT),
        "validator_sha256": sha(Path(__file__)),
        "scope": "Independent reconstruction of every state assignment, recurrent-template count, 94 held-folio codes and shuffles, 133 transition permutation tests, the inherited GDT015 pooled transition, hashes, ledger, f84 exclusion, and claim ceiling. Reuses only the separately validated strict-group loader.",
    }
    VALIDATION.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n")
    print(json.dumps(validation, sort_keys=True))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
