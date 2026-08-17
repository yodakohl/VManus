#!/usr/bin/env python3
"""Score frozen PAGE_HOSTs against real diplomatic versus expanded Nuremberg LMs."""
from __future__ import annotations

import csv
import hashlib
import json
import math
import unicodedata
from collections import defaultdict
from pathlib import Path

import numpy as np

from gdt001_core import TARGET_ALPHABET, universal_uint_bits
from run_gdt001_mtf_dynamic_rank import compile_library, search_static
from run_gdt189_compiler_stripped_language import arrays, guarded, kt_bits, mapping_key, parser, sequences

ROOT = Path(__file__).resolve().parent
BLIND = ROOT / "gdt155_blinded_diplomatic.tsv"
EXPANDED = ROOT / "gdt155_unblinded_lines.tsv"
SOURCE = ROOT / "gdt016_group_state_inventory.tsv"
PARENT157 = ROOT / "gdt157_result.json"
PARENT189 = ROOT / "gdt189_result.json"
METHOD = ROOT / "GDT207_DIPLOMATIC_ABBREVIATION_LANGUAGE_SCREEN_METHOD.md"
REPORT = ROOT / "GDT207_DIPLOMATIC_ABBREVIATION_LANGUAGE_SCREEN_REPORT.md"
PACKS = ROOT / "gdt207_abbreviation_pack_summary.tsv"
RUNS = ROOT / "gdt207_mapping_runs.tsv"
COMPARISON = ROOT / "gdt207_abbreviation_comparison.tsv"
COUNTER = ROOT / "gdt207_counterexamples.tsv"
SENSITIVITY = ROOT / "gdt207_search_sensitivity.tsv"
RESULT = ROOT / "gdt207_result.json"

SEEDS = (20701, 20702, 20703)
SENSITIVITY_SEEDS = (18901, 18902, 18903)
FOLD = str.maketrans({"ſ": "s", "ı": "i", "ȷ": "j", "ẜ": "s", "ß": "ss"})


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def content_sha(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()


def write(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def normalize_line(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).translate(FOLD).lower()
    out: list[str] = []
    last_space = True
    for char in value:
        if "a" <= char <= "z":
            out.append(char)
            last_space = False
        elif not last_space:
            out.append(" ")
            last_space = True
    return "".join(out).strip()


def load_parallel() -> tuple[dict[str, str], dict[str, str]]:
    diplomatic = {}
    with BLIND.open(encoding="utf8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["corpus"] == "NUREMBERG":
                diplomatic[row["line_id"]] = row["diplomatic_bare"]
    expanded = {}
    with EXPANDED.open(encoding="utf8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["corpus"] == "NUREMBERG":
                expanded[row["line_id"]] = row["expanded_diplomatic"]
    assert diplomatic.keys() == expanded.keys() and len(diplomatic) == 48337
    return diplomatic, expanded


def source_scope_census() -> tuple[int, int]:
    """Count forbidden rows from locus/page identifiers without parsing payload."""
    f84r = f84_other = 0
    with SOURCE.open(encoding="utf8") as handle:
        header = handle.readline().rstrip("\n").split("\t")
        locus_i, page_i = header.index("locus"), header.index("page")
        for raw in handle:
            parts = raw.rstrip("\n").split("\t")
            locus, page = parts[locus_i], parts[page_i]
            if locus.startswith("f84r") or page.startswith("f84r"):
                f84r += 1
            elif locus.startswith("f84") or page.startswith("f84"):
                f84_other += 1
    return f84r, f84_other


def train(lines: list[str], alpha: float = 0.5) -> tuple[np.ndarray, int, int]:
    size = len(TARGET_ALPHABET)
    counts = np.zeros((size + 1, size + 1, size), dtype=np.float64)
    letters = groups = 0
    for raw in lines:
        text = normalize_line(raw)
        if not text:
            continue
        groups += len(text.split())
        ids = [TARGET_ALPHABET.index(char) for char in text]
        history = [size, size]
        for value in ids:
            counts[history[0], history[1], value] += 1.0
            history = [history[1], value]
            letters += value != 26
    denominators = counts.sum(axis=-1, keepdims=True) + alpha * size
    costs = np.ascontiguousarray(-np.log2((counts + alpha) / denominators), dtype=np.float64)
    return costs, letters, groups


def main() -> None:
    diplomatic, expanded = load_parallel()
    f84r_rows, f84_other_rows = source_scope_census()
    pack_lines = {
        "REAL_DIPLOMATIC": [diplomatic[key] for key in sorted(diplomatic)],
        "EXPANDED_PARALLEL": [expanded[key] for key in sorted(expanded)],
    }
    source = guarded()
    parse = parser(source)
    seqs = sequences(source, "PAGE_HOST", parse)
    tokens, offsets = arrays(seqs)
    active = {value for seq in seqs for value in seq if value != 25}
    null_payload, outcomes = kt_bits(seqs, active)
    common = 3 + universal_uint_bits(2)
    selector = math.log2(len(pack_lines))
    key_bits = mapping_key(len(active))
    null_total = null_payload + common
    api = compile_library()
    pack_rows = []
    run_rows = []
    best_by_pack = {}
    costs_by_pack = {}
    for pack, lines in pack_lines.items():
        costs, letters, groups = train(lines)
        costs_by_pack[pack] = costs
        pack_rows.append({
            "pack": pack,
            "parallel_lines": len(lines),
            "normalized_letter_events": letters,
            "normalized_group_events": groups,
            "order": 2,
            "alpha": "0.5",
            "normalization": "NFKD_LONG_S_DOTLESS_I_SHARP_S_TO_ASCII_AZ_SPACE",
        })
        current = []
        for seed in SEEDS:
            payload, mapping, passes, local = search_static(api, tokens, offsets, costs, seed)
            total = payload + common + selector + key_bits
            mapping_text = "".join(chr(97 + int(value)) for value in mapping)
            active_mapping = "".join(
                f"{chr(97 + index)}>{chr(97 + int(mapping[index]))}"
                for index in sorted(active)
            )
            row = {
                "pack": pack,
                "seed": seed,
                "physical_lines": len(seqs),
                "events": len(tokens),
                "active_source_signs": len(active),
                "payload_bits": f"{payload:.12f}",
                "common_overhead_bits": f"{common:.12f}",
                "pack_selector_bits": f"{selector:.12f}",
                "key_bits": f"{key_bits:.12f}",
                "paid_total_bits": f"{total:.12f}",
                "matched_kt_total_bits": f"{null_total:.12f}",
                "gap_vs_matched_kt_bits": f"{total - null_total:.12f}",
                "gap_per_event": f"{(total - null_total) / len(tokens):.12f}",
                "passes": passes,
                "all_pair_swaps_locally_optimal": int(local),
                "full_mapping_order": mapping_text,
                "active_mapping": active_mapping,
                "mapping_hash": hashlib.sha256(active_mapping.encode()).hexdigest(),
            }
            run_rows.append(row)
            current.append(row)
        best_by_pack[pack] = min(current, key=lambda row: float(row["paid_total_bits"]))
    diplomatic_best = best_by_pack["REAL_DIPLOMATIC"]
    expanded_best = best_by_pack["EXPANDED_PARALLEL"]
    diplomatic_runs = [row for row in run_rows if row["pack"] == "REAL_DIPLOMATIC"]
    expanded_runs = [row for row in run_rows if row["pack"] == "EXPANDED_PARALLEL"]
    saving = float(expanded_best["paid_total_bits"]) - float(diplomatic_best["paid_total_bits"])
    comparison = [{
        "comparison": "REAL_DIPLOMATIC_MINUS_EXPANDED_PARALLEL",
        "diplomatic_best_paid_bits": diplomatic_best["paid_total_bits"],
        "expanded_best_paid_bits": expanded_best["paid_total_bits"],
        "diplomatic_saving_bits": f"{saving:.12f}",
        "diplomatic_saving_bits_per_event": f"{saving / len(tokens):.12f}",
        "diplomatic_gap_vs_kt_bits": diplomatic_best["gap_vs_matched_kt_bits"],
        "expanded_gap_vs_kt_bits": expanded_best["gap_vs_matched_kt_bits"],
        "failure_gap_fraction_removed": f"{saving / float(expanded_best['gap_vs_matched_kt_bits']):.12f}",
        "diplomatic_mapping_stable": int(len({row["mapping_hash"] for row in diplomatic_runs}) == 1),
        "expanded_mapping_stable": int(len({row["mapping_hash"] for row in expanded_runs}) == 1),
    }]
    sensitivity_rows = []
    sensitivity_by_seed = defaultdict(dict)
    for seed in SENSITIVITY_SEEDS:
        for pack in pack_lines:
            payload, mapping, passes, local = search_static(api, tokens, offsets, costs_by_pack[pack], seed)
            total = payload + common + selector + key_bits
            active_mapping = "".join(
                f"{chr(97 + index)}>{chr(97 + int(mapping[index]))}"
                for index in sorted(active)
            )
            row = {
                "analysis_scope": "POSTHOC_SEARCH_SENSITIVITY",
                "pack": pack,
                "seed": seed,
                "paid_total_bits": f"{total:.12f}",
                "gap_vs_matched_kt_bits": f"{total - null_total:.12f}",
                "passes": passes,
                "all_pair_swaps_locally_optimal": int(local),
                "active_mapping": active_mapping,
                "mapping_hash": hashlib.sha256(active_mapping.encode()).hexdigest(),
            }
            sensitivity_rows.append(row)
            sensitivity_by_seed[seed][pack] = total
    paired_savings = [
        sensitivity_by_seed[seed]["EXPANDED_PARALLEL"]
        - sensitivity_by_seed[seed]["REAL_DIPLOMATIC"]
        for seed in SENSITIVITY_SEEDS
    ]
    paired_savings += [
        float(next(row for row in expanded_runs if int(row["seed"]) == seed)["paid_total_bits"])
        - float(next(row for row in diplomatic_runs if int(row["seed"]) == seed)["paid_total_bits"])
        for seed in SEEDS
    ]
    write(PACKS, pack_rows)
    write(RUNS, run_rows)
    write(COMPARISON, comparison)
    write(SENSITIVITY, sensitivity_rows)
    counter = [
        {"counterexample_id": "C01", "observation": f"Real diplomatic still loses {float(diplomatic_best['gap_vs_matched_kt_bits']):.1f} bits to matched source KT.", "impact": "authentic abbreviation is not a competitive direct decoder"},
        {"counterexample_id": "C02", "observation": "The three retained diplomatic mappings are not identical.", "impact": "no stable sign assignment"},
        {"counterexample_id": "C03", "observation": "GDT189's best six-pack PAGE_HOST gap remains smaller than the diplomatic gap.", "impact": "diplomatic improvement over its expansion is not absolute closeness"},
        {"counterexample_id": "C04", "observation": "The Nuremberg corpus is German civic correspondence, not a medical-alchemical source text.", "impact": "bounded channel-practice comparator only"},
        {"counterexample_id": "C05", "observation": "An injective character map cannot represent the full learned GDT157 abbreviation transducer.", "impact": "failure does not close every contextual inverse channel"},
        {"counterexample_id": "C06", "observation": f"Across the three primary and three post-hoc shared starts, paired diplomatic savings range from {min(paired_savings):.1f} to {max(paired_savings):.1f} bits.", "impact": "the magnitude is heuristic-local-optimum sensitive"},
    ]
    write(COUNTER, counter)
    gates = {
        "real_diplomatic_beats_expanded_parallel": saving > 0,
        "real_diplomatic_beats_matched_kt": float(diplomatic_best["gap_vs_matched_kt_bits"]) < 0,
        "real_diplomatic_mapping_stable": len({row["mapping_hash"] for row in diplomatic_runs}) == 1,
    }
    gates["inverse_transducer_screen_authorized"] = all(gates.values())
    status = "DIPLOMATIC_ABBREVIATION_RELATIVE_GAIN_DIRECT_DECODER_REJECTED"
    REPORT.write_text(f"""# GDT207 — abbreviation helps relatively, but does not decode PAGE_HOST

Status: **{status}**.

The authentic Nuremberg diplomatic character model is slightly closer than
its line-aligned expanded parallel under the unchanged primary GDT189 mapping
budget.  It saves **{saving:,.1f} bits** ({saving / len(tokens):.3f} bits/event), removing
{100 * saving / float(expanded_best['gap_vs_matched_kt_bits']):.1f}% of the
expanded model's failure gap.  The direction is the same in all six shared
initializations inspected, but the paired saving ranges from
{min(paired_savings):,.1f} to {max(paired_savings):,.1f} bits.  The older three
starts are a post-hoc search sensitivity and do not alter the frozen gates.
Historical abbreviation remains a plausible directional contributor, while
its magnitude is not identified by this heuristic screen.

It is not a decoder.  The best diplomatic mapping costs
{float(diplomatic_best['paid_total_bits']):,.1f} paid bits and remains
**{float(diplomatic_best['gap_vs_matched_kt_bits']):,.1f} bits**
({float(diplomatic_best['gap_per_event']):.3f} bits/event) worse than the matched
anonymous source KT channel.  All retained keys are pair-swap local optima, but
the three starts give different mappings.  The diplomatic gap is also larger
than GDT189's best frozen six-language-pack gap.

The useful conclusion is architectural: authentic diplomatic abbreviation
moves the compiler-stripped stream in the right direction, but a stable
one-source-sign/one-letter reading remains decisively inadequate.  The frozen
gate therefore does not authorize a flexible inverse transducer from this
exposed panel.  A future inverse route needs an externally constrained
contextual unit or parallel key, not more mapping freedom alone.

No sign, sound, word, language, plaintext, meaning, or translation is
established.  The source has no f84r rows.  Its 228 f84v rows were rejected
from locus/page identifiers before formal-field retention; no f84 formal row
was joined, scored, or displayed.
""", encoding="utf8")
    result = {
        "schema": "GDT207_DIPLOMATIC_ABBREVIATION_LANGUAGE_SCREEN_RESULT_V1",
        "status": status,
        "counts": {"parallel_lines_per_pack": 48337, "physical_lines": len(seqs), "events": len(tokens), "active_source_signs": len(active), "runs": len(run_rows), "anonymous_outcomes": outcomes},
        "best": {"real_diplomatic": diplomatic_best, "expanded_parallel": expanded_best},
        "comparison": {**comparison[0], "all_six_shared_start_savings_positive": all(value > 0 for value in paired_savings), "paired_saving_min_bits": min(paired_savings), "paired_saving_max_bits": max(paired_savings)},
        "gates": gates,
        "interpretation": "Authentic diplomatic abbreviation improves its expanded parallel but does not provide a competitive or stable injective PAGE_HOST decoder.",
        "claim_ceiling": "Bounded historical-diplomatic character-model screen only; no sign, sound, word, language, plaintext, meaning, or translation.",
        "f84": {
            "f84r_rows_in_source": f84r_rows,
            "other_f84_rows_in_source": f84_other_rows,
            "formal_fields_retained": 0,
            "formal_rows_joined": 0,
            "formal_rows_scored": 0,
            "formal_payload_displayed": False,
        },
        "inputs": {BLIND.name: sha(BLIND), EXPANDED.name: sha(EXPANDED), SOURCE.name: sha(SOURCE), PARENT157.name: sha(PARENT157), PARENT189.name: sha(PARENT189)},
        "implementation": {Path(__file__).name: sha(Path(__file__)), "run_gdt189_compiler_stripped_language.py": sha(ROOT / "run_gdt189_compiler_stripped_language.py"), "run_gdt001_mtf_dynamic_rank.py": sha(ROOT / "run_gdt001_mtf_dynamic_rank.py"), "gdt001_mtf_score.cpp": sha(ROOT / "gdt001_mtf_score.cpp")},
        "outputs": {path.name: sha(path) for path in (PACKS, RUNS, COMPARISON, COUNTER, SENSITIVITY)},
        "documents": {METHOD.name: sha(METHOD), REPORT.name: sha(REPORT)},
    }
    result["result_content_sha256"] = content_sha(result)
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf8")
    print(json.dumps({"status": status, "diplomatic_saving_bits": saving, "diplomatic_gap_bits": float(diplomatic_best["gap_vs_matched_kt_bits"]), "gates": gates}, sort_keys=True))


if __name__ == "__main__":
    main()
