#!/usr/bin/env python3
from __future__ import annotations

import os

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

WORK = Path(os.environ.get("GDT612_WORK", Path(__file__).resolve().parent)).resolve()
PREP = WORK / "prepared"
EVAL = WORK / "evaluation"
REPO = Path(os.environ.get("VMANUS_REPO_ROOT", Path.cwd())).resolve()
EXPECTED_ROLES = {
    "literal_carrier": 18,
    "syllabic_carrier": 4,
    "prefix_operator": 3,
    "suffix_operator": 3,
    "connector": 2,
    "context_abbreviation_mark": 2,
    "wholeform_logogram": 1,
    "null_layout": 1,
}
ROLE_CATEGORY = {
    "literal_carrier": "literal", "syllabic_carrier": "syllabic",
    "prefix_operator": "prefix", "suffix_operator": "suffix",
    "connector": "connector", "context_abbreviation_mark": "context",
    "wholeform_logogram": "whole", "null_layout": "null",
}


def read_tsv(path):
    with Path(path).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def load_key(directory):
    mapping = {
        int(row["primitive_id"]): (row["role"], "" if row["output"] == "<EMPTY>" else row["output"])
        for row in read_tsv(Path(directory) / "primitive_mapping.tsv")
    }
    overrides = {
        int(row["unit_id"]): (row["type"], row["output"])
        for row in read_tsv(Path(directory) / "merge_overrides.tsv")
    }
    return mapping, overrides


def decode(sequence, mapping, overrides, units, with_spans=False):
    memo = {}

    def pieces(uid):
        if uid in memo:
            return memo[uid]
        unit = units[uid]
        if uid in overrides:
            kind, output = overrides[uid]
            value = [("wholeform_logogram" if kind == "wholeform" else "syllabic_carrier", output)]
        elif unit["is_primitive"] == "1":
            value = [mapping[int(unit["primitive_id"])]]
        else:
            value = pieces(int(unit["left_unit_id"])) + pieces(int(unit["right_unit_id"]))
        memo[uid] = value
        return value

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


def main():
    require(WORK != REPO, "full reproduction workspace must remain outside the repository root")
    prepared = json.loads((PREP / "MANIFEST.json").read_text())
    require(prepared["counts"] == {
        "held_chunks": 9838, "held_folios": 23, "held_paragraphs": 255,
        "merges": 64, "primitives": 34, "train_chunk_types": 5582,
        "train_chunks": 20336, "units": 98,
    }, "prepared counts drift")
    for relative, expected in prepared["input_hashes"].items():
        require(sha(REPO / relative) == expected, f"input hash drift: {relative}")
    for relative, expected in prepared["reference_hashes"].items():
        require(sha(WORK / "references" / relative) == expected, f"reference hash drift: {relative}")

    held = read_tsv(PREP / "held_chunks.tsv")
    require(len(held) == 9838, "held chunk count")
    require(len({row["physical_folio"] for row in held}) == 23, "held folio count")
    for row in held:
        for column in ("page", "physical_folio", "locus"):
            require(not row[column].lower().startswith(("f84", "f84r")), f"forbidden selector in {column}")
    guarded = read_tsv(REPO / "experiments/yolo/gdt606_mixed_nomenclator_decoder/artifacts/guarded_rows.tsv")
    for row in guarded:
        require(not row["page"].lower().startswith(("f84", "f84r")), "forbidden page in guarded source")
        require(not row["physical_folio"].lower().startswith(("f84", "f84r")), "forbidden folio in guarded source")

    decoder_source = (WORK / "decoder.cpp").read_text(encoding="utf-8")
    require("held_chunks" not in decoder_source and "held_lines" not in decoder_source, "fitter source mentions held material")
    require('units[uid].name == "qok"' in decoder_source, "qok wholeform guard absent")
    unit_rows = read_tsv(PREP / "units.tsv")
    units = {int(row["unit_id"]): row for row in unit_rows}
    merge_ids = {int(row["unit_id"]) for row in unit_rows if row["is_primitive"] == "0"}
    qok_id = next(int(row["unit_id"]) for row in unit_rows if row["unit"] == "qok")

    jobs = []
    for language, base in (("latin", 1100), ("old_italian", 2100), ("middle_high_german", 3100)):
        for kind, offsets in (("real", range(1, 7)), ("destroyed", range(91, 94))):
            candidate_rows = read_tsv(PREP / f"packs/{language}_{kind}_candidates.tsv")
            candidates = defaultdict(set)
            for row in candidate_rows:
                candidates[row["category"]].add(row["value"])
            for offset in offsets:
                seed = base + offset
                directory = WORK / f"target_runs/{language}/{kind}/seed_{seed}"
                mapping = read_tsv(directory / "primitive_mapping.tsv")
                require(len(mapping) == 34, f"mapping capacity {language} {kind} {seed}")
                require(Counter(row["role"] for row in mapping) == EXPECTED_ROLES, f"role capacity {language} {kind} {seed}")
                by_role = defaultdict(list)
                for row in mapping:
                    role, output = row["role"], row["output"]
                    by_role[role].append(output)
                    if role == "null_layout":
                        require(output == "<EMPTY>", "nonempty null")
                        require(float(row["leaf_train_fraction"]) <= .03 + 1e-12, "null mass violation")
                    else:
                        require(output in candidates[ROLE_CATEGORY[role]], f"output outside candidate pack: {output}")
                for role, outputs in by_role.items():
                    require(len(outputs) == len(set(outputs)), f"duplicate role output {language} {kind} {seed} {role}")
                overrides = read_tsv(directory / "merge_overrides.tsv")
                require(len(overrides) <= 8, "override capacity")
                require(sum(row["type"] == "wholeform" for row in overrides) <= 4, "whole override capacity")
                require(all(int(row["unit_id"]) in merge_ids for row in overrides), "primitive override")
                require(not any(int(row["unit_id"]) == qok_id and row["type"] == "wholeform" for row in overrides), "qok standalone whole override")
                require(len(read_tsv(EVAL / f"decodes/{language}_{kind}_{seed}.tsv")) == 9838, "decode coverage")
                jobs.append((language, kind, seed))
    require(len(jobs) == 27, "job count")

    synth_truth = read_tsv(WORK / "synthetic/truth_primitives.tsv")
    require(Counter(row["role"] for row in synth_truth) == EXPECTED_ROLES, "synthetic truth capacity")
    synth_overrides = read_tsv(WORK / "synthetic/truth_overrides.tsv")
    require(len(synth_overrides) == 8 and sum(r["type"] == "wholeform" for r in synth_overrides) == 4, "synthetic override capacity")
    require(not any(r["unit"] == "qok" and r["type"] == "wholeform" for r in synth_overrides), "synthetic qok violation")
    truth_mapping = {
        int(row["primitive_id"]): (row["role"], "" if row["output"] == "<EMPTY>" else row["output"])
        for row in synth_truth
    }
    truth_overrides = {int(row["unit_id"]): (row["type"], row["output"]) for row in synth_overrides}
    synthetic_held = read_tsv(WORK / "synthetic/held.tsv")
    require(all(
        " ".join(decode([int(x) for x in row["units"].split(",")], truth_mapping, truth_overrides, units)) == row["plaintext"]
        for row in synthetic_held
    ), "independent synthetic truth decode")
    synth_eval = read_tsv(EVAL / "synthetic_recovery.tsv")
    require(len(synth_eval) == 6, "synthetic run count")

    metrics = read_tsv(EVAL / "held_run_metrics.tsv")
    require(len(metrics) == 27, "metric rows")
    require({(r["language"], r["kind"], int(r["seed"])) for r in metrics} == set(jobs), "metric job mismatch")
    stability = read_tsv(EVAL / "carrier_stability.tsv")
    require(len(stability) == 3, "stability language rows")
    stability_by_language = {row["language"]: row for row in stability}
    for language, base in (("latin", 1100), ("old_italian", 2100), ("middle_high_german", 3100)):
        loaded = [load_key(WORK / f"target_runs/{language}/real/seed_{base + offset}") for offset in range(1, 7)]
        mappings = [item[0] for item in loaded]
        overrides = [item[1] for item in loaded]
        unanimous_primitives = sum(len({mapping[pid] for mapping in mappings}) == 1 for pid in range(34))
        require(unanimous_primitives == int(stability_by_language[language]["unanimous_primitive_role_output_of_34"]), "independent primitive stability")
        unanimous_units = 0
        for uid in range(98):
            values = [" ".join(decode([uid], mappings[index], overrides[index], units)) for index in range(6)]
            unanimous_units += len(set(values)) == 1
        require(unanimous_units == int(stability_by_language[language]["unanimous_unit_output_of_98"]), "independent unit stability")
        span_maps = []
        for index in range(6):
            current = {}
            for row in held:
                record_id = int(row["record_id"])
                sequence = [int(x) for x in row["units"].split(",")]
                _words, spans = decode(sequence, mappings[index], overrides[index], units, with_spans=True)
                for start, end, ordinal, output in spans:
                    current[(record_id, start, end, ordinal)] = output
            span_maps.append(current)
        common = set.intersection(*(set(mapping) for mapping in span_maps))
        stable_spans = sum(len({mapping[key] for mapping in span_maps}) == 1 for key in common)
        require(stable_spans == int(stability_by_language[language]["unanimous_held_word_spans"]), "independent held span stability")
    result = json.loads((EVAL / "RESULTS.json").read_text())
    require(result["synthetic"]["truth_decode_rate"] == 1.0, "synthetic generator truth decode")
    require(result["target"]["held_folios"] == 23, "result held folios")
    require(result["target"]["real_jobs"] == 18 and result["target"]["destroyed_jobs"] == 9, "result job partition")
    for name, expected in result["source_hashes"].items():
        path = PREP / "MANIFEST.json" if name == "prepared_manifest" else WORK / name
        require(sha(path) == expected, f"evaluation source hash: {name}")
    best = json.loads((EVAL / "best_held_paragraph.json").read_text())
    paragraphs = read_tsv(EVAL / "held_paragraphs.tsv")
    require(any(all(row[key] == str(best[key]) for key in ("language", "seed", "paragraph_id", "decoded_paragraph")) for row in paragraphs), "best paragraph not in full table")
    independently_best = max(
        (row for row in paragraphs if int(row["letters"]) >= 50),
        key=lambda row: (float(row["order_signal_bits_per_letter"]), float(row["lexicon_char_coverage"]), int(row["letters"])),
    )
    require(independently_best["language"] == best["language"] and int(independently_best["seed"]) == int(best["seed"]) and independently_best["paragraph_id"] == best["paragraph_id"], "independent best paragraph selection")
    conclusion = json.loads((EVAL / "CONCLUSION.json").read_text())
    require(conclusion["target_ready"] is False, "unsupported target-ready conclusion")
    require(conclusion["restart_stable_concrete_meanings"] == 0, "stable meaning count")
    require((EVAL / "CONCLUSION.json").exists(), "conclusion absent")

    validation = {
        "status": "VALIDATION_OK",
        "prepared_counts": prepared["counts"],
        "fit_jobs": 27,
        "synthetic_jobs": 6,
        "role_capacity": EXPECTED_ROLES,
        "held_folios": 23,
        "held_chunks_per_job": 9838,
        "forbidden_selectors": "ABSENT",
        "fitter_held_access_static_gate": "PASS",
        "qok_wholeform_gate": "PASS",
        "source_sha256": sha(Path(__file__)),
    }
    (WORK / "VALIDATION.json").write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n")
    print(json.dumps(validation, sort_keys=True))


if __name__ == "__main__":
    main()
