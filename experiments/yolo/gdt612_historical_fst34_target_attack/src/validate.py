#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import itertools
import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path

from oracle_objective_audit import compute_rows as compute_oracle_objective_rows

ROOT = Path(__file__).resolve().parents[4]
EXP = Path(__file__).resolve().parents[1]
ART = EXP / "artifacts"
G606 = ROOT / "experiments/yolo/gdt606_mixed_nomenclator_decoder/artifacts"

ROLE_COUNTS = {
    "literal_carrier": 18,
    "syllabic_carrier": 4,
    "prefix_operator": 3,
    "suffix_operator": 3,
    "connector": 2,
    "context_abbreviation_mark": 2,
    "wholeform_logogram": 1,
    "null_layout": 1,
}
LANGUAGE_SEEDS = {
    "latin": range(1101, 1107),
    "old_italian": range(2101, 2107),
    "middle_high_german": range(3101, 3107),
}


def read_tsv(path: Path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


checks = []


def check(name, condition, detail=""):
    checks.append({"name": name, "pass": bool(condition), "detail": str(detail)})


units = {int(row["unit_id"]): row for row in read_tsv(ART / "units.tsv")}
unit_id = {row["unit"]: uid for uid, row in units.items()}
primitives = {int(row["primitive_id"]): row for row in read_tsv(ART / "primitives.tsv")}
qok_id = unit_id["qok"]


def load_key(directory: Path):
    mapping = {
        int(row["primitive_id"]): (
            row["role"],
            "" if row["output"] == "<EMPTY>" else row["output"],
        )
        for row in read_tsv(directory / "primitive_mapping.tsv")
    }
    overrides = {
        int(row["unit_id"]): (row["type"], row["output"])
        for row in read_tsv(directory / "merge_overrides.tsv")
    }
    return mapping, overrides


def decode(sequence, mapping, overrides, with_spans=False):
    memo = {}

    def pieces(uid):
        if uid in memo:
            return memo[uid]
        unit = units[uid]
        if uid in overrides:
            kind, output = overrides[uid]
            result = [
                (
                    "wholeform_logogram" if kind == "wholeform" else "syllabic_carrier",
                    output,
                )
            ]
        elif unit["is_primitive"] == "1":
            result = [mapping[int(unit["primitive_id"])]]
        else:
            result = pieces(int(unit["left_unit_id"])) + pieces(int(unit["right_unit_id"]))
        memo[uid] = result
        return result

    words, spans = [], []
    current, start, end = "", None, None

    def flush():
        nonlocal current, start, end
        if current:
            words.append(current)
            spans.append((start, end, len(words) - 1, current))
        current, start, end = "", None, None

    for position, uid in enumerate(sequence):
        for role, output in pieces(uid):
            if role == "null_layout" or not output:
                continue
            if role in {"connector", "wholeform_logogram"}:
                flush()
                words.append(output)
                spans.append((position, position, len(words) - 1, output))
            else:
                if start is None:
                    start = position
                end = position
                current += output
    flush()
    return (words, spans) if with_spans else words


def levenshtein(left, right):
    previous = list(range(len(right) + 1))
    for i, char_left in enumerate(left, 1):
        current = [i]
        for j, char_right in enumerate(right, 1):
            current.append(
                min(
                    current[-1] + 1,
                    previous[j] + 1,
                    previous[j - 1] + (char_left != char_right),
                )
            )
        previous = current
    return previous[-1]


def validate_key(name, mapping, overrides):
    check(name + "_34_primitives", len(mapping) == 34, len(mapping))
    check(name + "_role_capacity", Counter(role for role, _ in mapping.values()) == ROLE_COUNTS)
    null_ids = [pid for pid, (role, _output) in mapping.items() if role == "null_layout"]
    check(name + "_one_null", len(null_ids) == 1, null_ids)
    if null_ids:
        check(
            name + "_null_mass",
            float(primitives[null_ids[0]]["leaf_train_fraction"]) <= 0.03 + 1e-12,
            primitives[null_ids[0]]["leaf_train_fraction"],
        )
    check(name + "_override_capacity", len(overrides) <= 8, len(overrides))
    check(
        name + "_wholeform_override_capacity",
        sum(kind == "wholeform" for kind, _ in overrides.values()) <= 4,
    )
    check(
        name + "_qok_not_wholeform",
        not (qok_id in overrides and overrides[qok_id][0] == "wholeform"),
    )


def main():
    prepared = json.loads((ART / "PREPARED_MANIFEST.json").read_text(encoding="utf-8"))
    results = json.loads((ART / "RESULTS.json").read_text(encoding="utf-8"))
    conclusion = json.loads((ART / "CONCLUSION.json").read_text(encoding="utf-8"))

    for relative, expected in prepared["input_hashes"].items():
        observed = sha256(ROOT / relative)
        check("input_hash_" + Path(relative).name, observed == expected, observed)
    check("prepared_counts", prepared["counts"] == {
        "held_chunks": 9838,
        "held_folios": 23,
        "held_paragraphs": 255,
        "merges": 64,
        "primitives": 34,
        "train_chunk_types": 5582,
        "train_chunks": 20336,
        "units": 98,
    })
    check("unit_inventory_98", len(units) == 98)
    check("primitive_inventory_34", len(primitives) == 34)
    check(
        "gdt609_model_hash",
        sha256(ART / "model_v1.json")
        == sha256(ROOT / "experiments/yolo/gdt609_historical_mixed_abbreviation_prior/artifacts/model_v1.json")
        == prepared["model_sha256"],
    )

    sequence_data = json.loads((G606 / "unit_sequences.json").read_text(encoding="utf-8"))
    held_records = sequence_data["sequences"]["held"]
    guarded = read_tsv(G606 / "guarded_rows.tsv")
    check("held_chunks_9838", len(held_records) == 9838, len(held_records))
    check(
        "held_folios_23",
        len({row["physical_folio"] for row in held_records}) == 23,
    )
    check(
        "source_forbidden_selectors_absent",
        all(
            not row[field].lower().startswith("f84")
            for row in guarded
            for field in ("page", "physical_folio")
        )
        and all(
            not row[field].lower().startswith("f84")
            for row in held_records
            for field in ("page", "physical_folio", "locus")
        ),
    )
    decoder_source = (EXP / "src/full/decoder.cpp").read_text(encoding="utf-8")
    check(
        "fitter_static_held_gate",
        "held_chunks" not in decoder_source and "held_lines" not in decoder_source,
    )
    check("fitter_qok_guard", 'units[uid].name == "qok"' in decoder_source)

    synthetic_truth_mapping = {
        int(row["primitive_id"]): (
            row["role"],
            "" if row["output"] == "<EMPTY>" else row["output"],
        )
        for row in read_tsv(ART / "synthetic_truth_primitives.tsv")
    }
    synthetic_truth_overrides = {
        int(row["unit_id"]): (row["type"], row["output"])
        for row in read_tsv(ART / "synthetic_truth_overrides.tsv")
    }
    synthetic_held = read_tsv(ART / "synthetic_held.tsv")
    check("synthetic_truth_roles", Counter(role for role, _ in synthetic_truth_mapping.values()) == ROLE_COUNTS)
    check("synthetic_truth_overrides_8", len(synthetic_truth_overrides) == 8)
    check(
        "synthetic_truth_wholeforms_4",
        sum(kind == "wholeform" for kind, _ in synthetic_truth_overrides.values()) == 4,
    )
    truth_exact = all(
        " ".join(
            decode(
                [int(value) for value in row["units"].split(",")],
                synthetic_truth_mapping,
                synthetic_truth_overrides,
            )
        )
        == row["plaintext"]
        for row in synthetic_held
    )
    check("synthetic_truth_decodes_all_3639", truth_exact and len(synthetic_held) == 3639)

    recorded_synthetic = {
        int(row["seed"]): row for row in read_tsv(ART / "synthetic_recovery.tsv")
    }
    recovered_mappings = []
    for seed in range(7001, 7007):
        directory = ART / f"keys/synthetic/seed_{seed}"
        mapping, overrides = load_key(directory)
        validate_key(f"synthetic_{seed}", mapping, overrides)
        recovered_mappings.append(mapping)
        role_exact = sum(
            mapping[pid][0] == synthetic_truth_mapping[pid][0] for pid in range(34)
        )
        pair_exact = sum(
            mapping[pid] == synthetic_truth_mapping[pid] for pid in range(34)
        )
        override_exact = sum(
            overrides.get(uid) == value for uid, value in synthetic_truth_overrides.items()
        )
        exact_words = edit_distance = total_chars = 0
        for row in synthetic_held:
            decoded = " ".join(
                decode(
                    [int(value) for value in row["units"].split(",")],
                    mapping,
                    overrides,
                )
            )
            truth = row["plaintext"]
            exact_words += decoded == truth
            edit_distance += levenshtein(decoded, truth)
            total_chars += max(len(decoded), len(truth))
        recorded = recorded_synthetic[seed]
        check(f"synthetic_{seed}_role_recovery", role_exact == int(recorded["primitive_role_exact"]))
        check(f"synthetic_{seed}_pair_recovery", pair_exact == int(recorded["primitive_role_output_exact"]))
        check(f"synthetic_{seed}_override_recovery", override_exact == int(recorded["truth_override_exact"]))
        check(f"synthetic_{seed}_held_words", exact_words == int(recorded["held_word_exact"]))
        similarity = 1 - edit_distance / max(1, total_chars)
        check(
            f"synthetic_{seed}_char_similarity",
            abs(similarity - float(recorded["held_normalized_char_similarity"])) < 5e-10,
            similarity,
        )
    synthetic_pair_agreement = statistics.mean(
        sum(left[pid] == right[pid] for pid in range(34)) / 34
        for left, right in itertools.combinations(recovered_mappings, 2)
    )
    check(
        "synthetic_restart_pair_agreement",
        abs(
            synthetic_pair_agreement
            - float(results["synthetic"]["restart_primitive_pair_agreement_mean"])
        )
        < 1e-12,
        synthetic_pair_agreement,
    )
    check(
        "synthetic_key_failure",
        max(int(row["primitive_role_output_exact"]) for row in recorded_synthetic.values()) == 4
        and max(int(row["held_word_exact"]) for row in recorded_synthetic.values()) == 3
        and all(int(row["truth_override_exact"]) == 0 for row in recorded_synthetic.values()),
    )

    oracle_rows = compute_oracle_objective_rows()
    recorded_oracle = {
        row["key"]: row for row in read_tsv(ART / "oracle_objective_audit.tsv")
    }
    check("oracle_objective_seven_keys", len(oracle_rows) == len(recorded_oracle) == 7)
    for row in oracle_rows:
        recorded = recorded_oracle[row["key"]]
        check(
            "oracle_objective_reproduced_" + row["key"],
            abs(
                row["objective_per_sqrt_weight"]
                - float(recorded["objective_per_sqrt_weight"])
            )
            < 5e-12,
            row["objective_per_sqrt_weight"],
        )
    truth_objective = oracle_rows[0]["objective_per_sqrt_weight"]
    fitted_objectives = [
        row["objective_per_sqrt_weight"] for row in oracle_rows[1:]
    ]
    check(
        "oracle_truth_objective_exact",
        abs(truth_objective - 1.9145349778686591) < 1e-12,
        truth_objective,
    )
    check(
        "oracle_truth_ranks_last_of_seven",
        oracle_rows[0]["objective_rank_of_7"] == 7
        and all(value > truth_objective for value in fitted_objectives),
    )
    check(
        "oracle_wrong_key_advantage_range",
        abs(min(fitted_objectives) - 3.1149522359252337) < 1e-12
        and abs(max(fitted_objectives) - 3.3866430961773073) < 1e-12,
        f"{min(fitted_objectives)}..{max(fitted_objectives)}",
    )

    method_audit = json.loads((ART / "METHOD_AUDIT.json").read_text(encoding="utf-8"))
    exposure = read_tsv(ART / "synthetic_truth_exposure.tsv")
    zero_train = {
        f"{row['truth_level']}:{row['unit']}"
        for row in exposure
        if int(row["train_direct_events"]) == 0
    }
    check(
        "synthetic_truth_items_missing_from_train",
        {
            "primitive:F",
            "primitive:K",
            "primitive:f",
            "primitive:i",
            "override:dy",
        }
        <= zero_train,
        sorted(zero_train),
    )
    orientation = read_tsv(ART / "orientation_audit.tsv")
    check(
        "destroyed_control_is_self_oriented_not_matched_null",
        len(orientation) == 6
        and all(float(row["fit_oriented_mean"]) > 0 for row in orientation),
    )
    injection = read_tsv(ART / "top_token_injection.tsv")
    check(
        "all_real_top_tokens_are_injected_connector_or_whole_words",
        len(injection) == 18
        and all(
            row["mapping_role_or_type"]
            in {"connector", "wholeform_logogram"}
            and row["in_real_reference_lexicon"] == "1"
            and row["in_candidate_categories"]
            for row in injection
        ),
    )
    decoder_implementation = method_audit["implementation"]
    check(
        "simplified_decoder_not_model_json_execution",
        method_audit["status"] == "METHOD_AUDIT_OK"
        and decoder_implementation["copied_model_id"]
        == "HISTORICAL_MIXED_ABBREVIATION_FST_34_V1"
        and decoder_implementation["decoder_parses_model_json"] is False
        and decoder_implementation["hard_role_counts_present"] is True
        and decoder_implementation["lexicon_bonus_present"] is True
        and decoder_implementation["exact_qok_only_guard_present"] is True
        and decoder_implementation["whole_and_connector_share_branch"] is True,
    )

    recorded_stability = {
        row["language"]: row for row in read_tsv(ART / "carrier_stability.tsv")
    }
    target_keys = {}
    held_sequences = [
        [unit_id[name] for name in row["units"]] for row in held_records
    ]
    for language, seeds in LANGUAGE_SEEDS.items():
        mappings, overrides = [], []
        for seed in seeds:
            directory = ART / f"keys/target/{language}/seed_{seed}"
            mapping, override = load_key(directory)
            validate_key(f"target_{language}_{seed}", mapping, override)
            mappings.append(mapping)
            overrides.append(override)
            target_keys[(language, seed)] = (mapping, override)

        role_pair = []
        exact_pair = []
        unit_pair = []
        unit_outputs = []
        for mapping, override in zip(mappings, overrides):
            unit_outputs.append(
                [" ".join(decode([uid], mapping, override)) for uid in range(98)]
            )
        for left, right in itertools.combinations(range(6), 2):
            role_pair.append(
                sum(mappings[left][pid][0] == mappings[right][pid][0] for pid in range(34))
                / 34
            )
            exact_pair.append(
                sum(mappings[left][pid] == mappings[right][pid] for pid in range(34))
                / 34
            )
            unit_pair.append(
                sum(unit_outputs[left][uid] == unit_outputs[right][uid] for uid in range(98))
                / 98
            )

        unanimous_primitives = sum(
            len({mapping[pid] for mapping in mappings}) == 1 for pid in range(34)
        )
        unanimous_units = sum(
            len({table[uid] for table in unit_outputs}) == 1 for uid in range(98)
        )
        span_maps = []
        for mapping, override in zip(mappings, overrides):
            current = {}
            for record_id, sequence in enumerate(held_sequences):
                _words, spans = decode(sequence, mapping, override, with_spans=True)
                for start, end, ordinal, output in spans:
                    current[(record_id, start, end, ordinal)] = output
            span_maps.append(current)
        common = set.intersection(*(set(mapping) for mapping in span_maps))
        stable_spans = sum(
            len({mapping[key] for mapping in span_maps}) == 1 for key in common
        )

        recorded = recorded_stability[language]
        check(
            language + "_role_pairwise",
            abs(statistics.mean(role_pair) - float(recorded["primitive_role_pairwise_agreement"])) < 5e-13,
        )
        check(
            language + "_exact_pairwise",
            abs(statistics.mean(exact_pair) - float(recorded["primitive_role_output_pairwise_agreement"])) < 5e-13,
        )
        check(
            language + "_unit_pairwise",
            abs(statistics.mean(unit_pair) - float(recorded["unit_output_pairwise_agreement"])) < 5e-13,
        )
        check(
            language + "_unanimous_primitives_zero",
            unanimous_primitives == int(recorded["unanimous_primitive_role_output_of_34"]) == 0,
        )
        check(
            language + "_unanimous_units_zero",
            unanimous_units == int(recorded["unanimous_unit_output_of_98"]) == 0,
        )
        check(
            language + "_unanimous_spans_zero",
            stable_spans == int(recorded["unanimous_held_word_spans"]) == 0,
        )

    y_pid = next(pid for pid, row in primitives.items() if row["primitive"] == "y")
    mhg_y = [target_keys[("middle_high_german", seed)][0][y_pid] for seed in LANGUAGE_SEEDS["middle_high_german"]]
    check(
        "mhg_y_suffix_role_6_of_6",
        all(role == "suffix_operator" for role, _ in mhg_y),
        mhg_y,
    )
    check("mhg_y_output_split_3_3", Counter(output for _role, output in mhg_y) == {"oy": 3, "ex": 3})

    page_active = {}
    page_counter = Counter()
    locus_paragraph = {}
    locus_line_index = {}
    paragraph_line_counter = Counter()
    for row in guarded:
        page = row["page"]
        starts = "<%>" in row["ivtff_raw"][:32]
        ends = "<$>" in row["ivtff_raw"]
        if starts or page not in page_active:
            page_counter[page] += 1
            page_active[page] = f"{page}:p{page_counter[page]}"
        paragraph_id = page_active[page]
        locus_paragraph[row["locus"]] = paragraph_id
        locus_line_index[row["locus"]] = paragraph_line_counter[paragraph_id]
        paragraph_line_counter[paragraph_id] += 1
        if ends:
            page_active.pop(page, None)

    best = json.loads((ART / "best_held_paragraph.json").read_text(encoding="utf-8"))
    mapping, overrides = target_keys[(best["language"], int(best["seed"]))]
    by_locus = defaultdict(list)
    for row, sequence in zip(held_records, held_sequences):
        if locus_paragraph[row["locus"]] == best["paragraph_id"]:
            text = " ".join(decode(sequence, mapping, overrides))
            by_locus[row["locus"]].append((int(row["chunk_index"]), text))
    lines = []
    for locus in sorted(by_locus, key=lambda item: locus_line_index[item]):
        lines.append(" / ".join(text for _index, text in sorted(by_locus[locus])))
    reproduced_paragraph = " || ".join(lines)
    check("best_paragraph_identity", best["language"] == "middle_high_german" and int(best["seed"]) == 3103 and best["paragraph_id"] == "f103r:p18")
    check("best_paragraph_complete_text", reproduced_paragraph == best["decoded_paragraph"], reproduced_paragraph)
    check("best_paragraph_three_lines", len(lines) == int(best["line_count"]) == 3)

    metrics = read_tsv(ART / "held_run_metrics.tsv")
    check("target_metrics_27_jobs", len(metrics) == 27, len(metrics))
    check("target_real_18", sum(row["kind"] == "real" for row in metrics) == 18)
    check("target_destroyed_9", sum(row["kind"] == "destroyed" for row in metrics) == 9)
    check(
        "real_order_positive",
        all(float(row["held_order_signal_bits_per_letter"]) > 0 for row in metrics if row["kind"] == "real"),
    )
    check(
        "destroyed_order_negative",
        all(float(row["held_order_signal_bits_per_letter"]) < 0 for row in metrics if row["kind"] == "destroyed"),
    )
    baselines = {row["language"]: row for row in read_tsv(ART / "reference_baselines.tsv")}
    check(
        "real_top10_overconcentration",
        all(
            float(row["top10_token_fraction"])
            > float(baselines[row["language"]]["top10_token_fraction"])
            for row in metrics
            if row["kind"] == "real"
        ),
    )
    check(
        "reported_zero_meanings",
        conclusion["target_ready"] is False
        and conclusion["restart_stable_concrete_meanings"] == 0
        and all(
            row["unanimous_primitive_role_output_of_34"] == 0
            and row["unanimous_unit_output_of_98"] == 0
            and row["unanimous_held_word_spans"] == 0
            for row in results["target"]["stability"]
        ),
    )
    check(
        "empty_stable_output_tables",
        len(read_tsv(ART / "stable_unit_reference_outputs.tsv")) == 0
        and len(read_tsv(ART / "stable_held_spans.tsv")) == 0,
    )
    full_manifest = read_tsv(ART / "FULL_RUN_MANIFEST.tsv")
    check("full_run_manifest_286_files", len(full_manifest) == 286, len(full_manifest))
    check(
        "full_run_manifest_relative",
        all(not Path(row["relative_path"]).is_absolute() and ".." not in Path(row["relative_path"]).parts for row in full_manifest),
    )
    reproduction = json.loads((ART / "REPRODUCTION_CHECK.json").read_text(encoding="utf-8"))
    canonical_synthetic = hashlib.sha256(
        json.dumps(results["synthetic"], sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    canonical_target = hashlib.sha256(
        json.dumps(results["target"], sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    check(
        "clean_reproduction_payloads",
        reproduction["clean_full_rerun"] is True
        and reproduction["clean_full_validator"] == "VALIDATION_OK"
        and reproduction["synthetic_payload_equal"] is True
        and reproduction["target_payload_equal"] is True
        and reproduction["synthetic_payload_sha256"] == canonical_synthetic
        and reproduction["target_payload_sha256"] == canonical_target,
    )

    compact_manifest = {
        row["relative_path"]: row
        for row in read_tsv(ART / "COMPACT_MANIFEST.tsv")
    }
    compact_excluded = {
        "experiment.json",
        "artifacts/COMPACT_MANIFEST.tsv",
        "artifacts/VALIDATION.json",
    }
    compact_files = {
        path.relative_to(EXP).as_posix(): path
        for path in EXP.rglob("*")
        if path.is_file()
        and path.relative_to(EXP).as_posix() not in compact_excluded
        and "__pycache__" not in path.parts
    }
    check(
        "compact_manifest_complete",
        set(compact_manifest) == set(compact_files),
        len(compact_manifest),
    )
    check(
        "compact_manifest_hashes",
        all(
            int(compact_manifest[name]["bytes"]) == path.stat().st_size
            and compact_manifest[name]["sha256"] == sha256(path)
            for name, path in compact_files.items()
            if name in compact_manifest
        ),
    )

    status = "PASS" if all(row["pass"] for row in checks) else "FAIL"
    validation = {
        "status": status,
        "checks_passed": sum(row["pass"] for row in checks),
        "checks_total": len(checks),
        "decision": "HEURISTIC_DECODER_INVALIDATED__ORACLE_TRUTH_RANKS_LAST__ZERO_STABLE_TARGET_OUTPUTS",
        "checks": checks,
    }
    (ART / "VALIDATION.json").write_text(
        json.dumps(validation, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(validation, indent=2, sort_keys=True))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
