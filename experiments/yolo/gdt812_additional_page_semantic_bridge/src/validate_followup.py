#!/usr/bin/env python3
"""Independently verify guarded-cache substitution conservation, not meanings."""
import argparse
import csv
import hashlib
import io
import itertools
import json
import subprocess
from pathlib import Path

EXP = Path(__file__).resolve().parent.parent
REPO = EXP.parents[2]
ARTIFACTS = EXP / "artifacts"
SOURCE = "experiments/yolo/gdt812_additional_page_semantic_bridge/artifacts/ADMITTED_PAGE_LINES.tsv"
FIELDS = ("page", "locus", "line_number", "kind", "paragraph_start", "paragraph_end",
          "eva_clean", "it2a_clean", "rf1b_clean")
VERSIONS = (("ZL3b", "eva_clean"), ("IT2a", "it2a_clean"), ("RF1b", "rf1b_clean"))
OUTPUT_FIELDS = list(FIELDS[:6]) + ["reader_id", "source_text", "token_count", "daiin_count",
                                   "unknown_count", "daiin_positions_1based", "model_III", "model_sehr"]
CHECKS = []


def verify(condition, label):
    if not condition:
        raise ValueError(label)
    CHECKS.append(label)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def dump(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--check", action="store_true", help="Verify validation replay without writing.")
    options = cli.parse_args()
    contract_bytes = (EXP / "src/FOLLOWUP_RENDER_SPEC.json").read_bytes()
    contract = json.loads(contract_bytes)
    verify(contract["status"] == "POST_RESULT_EXPLORATORY_DISPLAY_ONLY", "exploratory_status")
    verify(contract["source"] == SOURCE and contract["selector"] == "page"
           and contract["allowed"] == ["f32v"] and contract["sealed_data"] == ["f84", "f84r"], "fixed_scope_and_seals")
    verify(contract["source_columns"] == list(FIELDS) and contract["readers"] == dict(VERSIONS)
           and contract["reader_order"] == [v[0] for v in VERSIONS]
           and contract["required_locus_count"] == 11, "fixed_complete_projection")
    verify(contract["target_whole"] == "daiin" and contract["unknown_template"] == "[token]"
           and contract["models"] == {"model_III": "III?", "model_sehr": "sehr?"}, "fixed_substitution_contract")
    verify(all(contract[k] == 0 for k in ("confirmed_words", "confirmed_plaintext_clauses", "new_admissions"))
           and contract["dictionary_changed"] is False, "contract_claim_ceiling")

    argv = ["./vmanus-exp", "query-tsv", SOURCE, "--selector", "page", "--allow", "f32v",
            "--columns", ",".join(FIELDS), "--forbid-prefix", "f84", "--forbid-prefix", "f84r"]
    fresh = subprocess.run(argv, cwd=REPO, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    guard_lines = [s[len("GUARD_STATS "):] for s in fresh.stderr.splitlines() if s.startswith("GUARD_STATS ")]
    verify(len(guard_lines) == 1, "fresh_selector_first_guard_audit")
    guard_stats = json.loads(guard_lines[0])
    verify(guard_stats["selected"] == 11, "guard_selected_eleven_loci")
    projected = csv.DictReader(io.StringIO(fresh.stdout), delimiter="\t")
    verify(projected.fieldnames == list(FIELDS), "guard_projection_columns")
    original = list(projected)
    verify(len(original) == 11 and [r["locus"] for r in original] == ["f32v." + str(n) for n in range(1, 12)],
           "all_source_loci_once_in_order")
    verify(all(r["page"] == "f32v" and r["line_number"] == str(i + 1) for i, r in enumerate(original)),
           "physical_page_and_line_coordinates")
    verify(all(r[c].strip() for r in original for _, c in VERSIONS), "all_three_readings_nonempty")

    trial_bytes = (ARTIFACTS / "FOLLOWUP_WHOLE_PAGE_TRIAL.tsv").read_bytes()
    parsed = csv.DictReader(io.StringIO(trial_bytes.decode()), delimiter="\t")
    verify(parsed.fieldnames == OUTPUT_FIELDS, "trial_schema")
    actual = list(parsed)
    verify(len(actual) == 33, "thirty_three_reader_locus_rows")
    expected_rows = []
    for src in original:
        for reader_id, column in VERSIONS:
            words = src[column].split()
            hit_indices = [index + 1 for index in range(len(words)) if words[index] == "daiin"]
            displays = []
            for substitution in ("III?", "sehr?"):
                display = []
                for word in words:
                    if word != "daiin":
                        display.append("[{}]".format(word))
                    else:
                        display.append(substitution)
                displays.append(" ".join(display))
            expected_rows.append([src[k] for k in FIELDS[:6]] + [reader_id, src[column], str(len(words)),
                str(len(hit_indices)), str(len(words) - len(hit_indices)),
                json.dumps(hit_indices, separators=(",", ":"))] + displays)
    actual_rows = [[r[k] for k in OUTPUT_FIELDS] for r in actual]
    verify(actual_rows == expected_rows, "complete_independent_row_reconstruction")
    reconstructed = io.StringIO(newline="")
    csv_output = csv.writer(reconstructed, delimiter="\t", lineterminator="\n")
    csv_output.writerow(OUTPUT_FIELDS)
    csv_output.writerows(expected_rows)
    verify(trial_bytes == reconstructed.getvalue().encode(), "exact_trial_bytes")

    tested_positions = adjacent_repeats = protected_compounds = 0
    for row in actual:
        source_words = row["source_text"].split()
        numerical = row["model_III"].split()
        degree = row["model_sehr"].split()
        verify(len(source_words) == len(numerical) == len(degree), "position_count_" + row["reader_id"] + "_" + row["locus"])
        for position, token in enumerate(source_words):
            if token == "daiin":
                if numerical[position] != "III?" or degree[position] != "sehr?":
                    raise ValueError("Target replacement lost or relocated")
            elif numerical[position] != "[" + token + "]" or degree[position] != "[" + token + "]":
                raise ValueError("Unknown whole was split, translated, or changed")
            tested_positions += 1
            if token == "cthodaiin":
                protected_compounds += 1
            if position and token == source_words[position - 1]:
                if numerical[position] != numerical[position - 1] or degree[position] != degree[position - 1]:
                    raise ValueError("Adjacent repetition lost")
                adjacent_repeats += 1
    verify(protected_compounds > 0, "cthodaiin_present_and_unsplit")
    verify(adjacent_repeats > 0, "adjacent_repetitions_preserved")
    per_reader = {}
    for name, column in VERSIONS:
        whole_rows = [r[column].split() for r in original]
        count = sum(len(words) for words in whole_rows)
        hits = sum(words.count("daiin") for words in whole_rows)
        per_reader[name] = {"loci": len(whole_rows), "tokens": count,
                            "daiin_wholes": hits, "unknown_wholes": count - hits}
    differences = {a[0] + "_vs_" + b[0]: [r["locus"] for r in original if r[a[1]] != r[b[1]]]
                   for a, b in itertools.combinations(VERSIONS, 2)}
    verify(all(differences.values()), "reading_differences_retained")
    expected_result = {
        "status": "POST_RESULT_EXPLORATORY_DISPLAY_ONLY", "page": "f32v", "source_loci": 11, "reader_rows": 33,
        "readers_are_alternate_readings_not_independent_witnesses": True,
        "models": {"model_III": "III?", "model_sehr": "sehr?"},
        "per_reader": per_reader, "source_difference_loci": differences,
        "confirmed_words": 0, "confirmed_plaintext_clauses": 0, "new_admissions": 0,
        "dictionary_changed": False, "semantic_score": None, "meanings_validated": False,
        "claim_ceiling": "Model-display contrast and exact-whole substitution reproducibility only.",
        "guard": {"command": argv, "stats": guard_stats, "projection_sha256": sha(fresh.stdout.encode())},
        "spec_sha256": sha(contract_bytes), "runner_sha256": sha((EXP / "src/run_followup.py").read_bytes()),
        "trial_tsv_sha256": sha(trial_bytes),
    }
    result_bytes = (ARTIFACTS / "FOLLOWUP_TRIAL_RESULT.json").read_bytes()
    verify(json.loads(result_bytes) == expected_result, "independent_totals_differences_bindings_and_claim_ceiling")
    verify(result_bytes == dump(expected_result), "exact_result_bytes")
    report = {
        "status": "PASS_SUBSTITUTION_REPRODUCIBILITY_ONLY", "checks": CHECKS,
        "checks_passed": len(CHECKS), "source_loci": 11, "reader_rows": 33,
        "tested_positions": tested_positions, "adjacent_repeats_preserved": adjacent_repeats,
        "cthodaiin_unknown_positions": protected_compounds, "per_reader": per_reader,
        "meanings_validated": False, "confirmed_words": 0, "confirmed_plaintext_clauses": 0,
        "new_admissions": 0, "semantic_score": None,
        "spec_sha256": sha(contract_bytes), "projection_sha256": sha(fresh.stdout.encode()),
        "trial_tsv_sha256": sha(trial_bytes), "result_sha256": sha(result_bytes),
        "validator_sha256": sha(Path(__file__).read_bytes()),
    }
    target = ARTIFACTS / "FOLLOWUP_TRIAL_VALIDATION.json"
    payload = dump(report)
    if options.check:
        if not target.is_file() or target.read_bytes() != payload:
            raise ValueError("Validation replay bytes differ")
    else:
        target.write_bytes(payload)
    print(json.dumps({"status": report["status"], "checks_passed": len(CHECKS),
                      "tested_positions": tested_positions, "meanings_validated": False}, sort_keys=True))


if __name__ == "__main__":
    main()
