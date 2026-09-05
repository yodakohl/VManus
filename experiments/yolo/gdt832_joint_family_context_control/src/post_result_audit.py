#!/usr/bin/env python3
"""Post-result aggregate audit of frozen GDT832 keys and reference spelling.

No fitting, key modification, language-model rescoring or normalization change
is performed. Original plaintext is used only for aggregate error accounting.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import string


EXPERIMENT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def letter_summary(words):
    counts = Counter(c for word in words for c in word)
    containing = Counter(c for word in words for c in set(word))
    return {"word_tokens": len(words), "letter_occurrences_total": sum(counts.values()),
        "letter_occurrences": {c: counts[c] for c in string.ascii_lowercase},
        "word_tokens_containing_letter": {c: containing[c] for c in string.ascii_lowercase}}


def run(root):
    inputs = {}

    def bound(relative):
        path = root / relative
        inputs[relative] = sha(path)
        return path

    lock_path = bound("artifacts/FIT_LOCK.json")
    lock = load(lock_path)
    for relative, expected in lock["sha256"].items():
        if sha(root / relative) != expected:
            raise AssertionError("A locked fit changed")
    evaluation = load(bound("artifacts/EVALUATION.json"))
    validation = load(bound("artifacts/VALIDATION.json"))
    if evaluation["fit_lock_sha256"] != sha(lock_path):
        raise AssertionError("Evaluation does not bind this fit lock")
    if evaluation["status"] != "CONTROL_RECOVERY_FAIL" or validation["scientific_status"] != evaluation["status"]:
        raise AssertionError("Expected completed failure evaluation and independent validation")
    evaluation_rows = {(r["world_id"], r["condition"], r["arm"]): r for r in evaluation["results"]}

    reference_rows = [json.loads(line) for line in bound("prepared/reference.jsonl").read_text().splitlines()]
    reference_words = [word for sentence in reference_rows for word in sentence]
    families = load(bound("prepared/families.json"))
    reference_summary = letter_summary(reference_words)
    reference_summary["sentences"] = len(reference_rows)
    reference_summary["family_form_types"] = len(families)
    reference_summary["family_form_types_containing_letter"] = {c: sum(c in word for word in families) for c in string.ascii_lowercase}
    reference_summary["denominator_note"] = "Letter counts use every character of every normalized reference word token, including characters inside forms that may become W/S cards in the control. Family-form counts instead count distinct dictionary form keys."
    source_truth = load(bound("sealed/source_truth.json"))
    source_by_id = {row["paragraph_id"]: row for row in source_truth["paragraphs"]}
    source_summary = {split: letter_summary([word for row in source_truth["paragraphs"] if row["split"] == split for word in row["words"]]) for split in ("discovery", "held")}

    worlds = []
    for world_id in (83201, 83202, 83203):
        truth = load(bound(f"sealed/world_{world_id}_truth.json"))
        actual_key = truth["decode_map"]
        selected = load(bound(f"artifacts/fits/world_{world_id}_real_FULL_selected.json"))
        selected_key = selected["key"]
        off = load(bound(f"artifacts/fits/world_{world_id}_real_OFF_selected.json"))
        full_evaluation = evaluation_rows[(world_id, "real", "FULL")]
        exposures = {}
        wrong_groups = Counter()
        membership = Counter()
        held_words = correct_words = wrong_words = 0
        full_off_word_disagreements = 0
        for split in ("discovery", "held"):
            cipher = load(bound(f"prepared/world_{world_id}_{split}.json"))
            exposure = Counter()
            for paragraph in cipher["paragraphs"]:
                source = source_by_id[paragraph["paragraph_id"]]
                if source["split"] != split or len(source["words"]) != len(paragraph["words"]):
                    raise AssertionError("Source and ciphertext positions differ")
                for atoms, expected_word in zip(paragraph["words"], source["words"]):
                    exposure.update(atoms)
                    if "".join(actual_key[a] for a in atoms) != expected_word:
                        raise AssertionError("Fixed truth does not roundtrip")
                    if split != "held":
                        continue
                    held_words += 1
                    predicted = "".join(selected_key[a] for a in atoms)
                    off_prediction = "".join(off["key"][a] for a in atoms)
                    full_off_word_disagreements += predicted != off_prediction
                    if predicted == expected_word:
                        correct_words += 1
                        continue
                    wrong_words += 1
                    bad_atoms = {a for a in atoms if selected_key[a] != actual_key[a]}
                    wrong_letters = tuple(sorted({actual_key[a] for a in bad_atoms if a.startswith("L")}))
                    wrong_other = tuple(sorted(a for a in bad_atoms if not a.startswith("L")))
                    wrong_groups[(wrong_letters, wrong_other)] += 1
                    membership["actual_form_in_reference_families"] += expected_word in families
                    membership["fitted_form_in_reference_families"] += predicted in families
                    membership["both_forms_in_reference_families"] += expected_word in families and predicted in families
            exposures[split] = exposure
        active = set(exposures["discovery"]) | set(exposures["held"])
        inactive = set(actual_key) - active
        key_classes = {}
        for kind in ("L", "S", "W"):
            ids = sorted(a for a in active if a.startswith(kind))
            key_classes[kind] = {"active": len(ids), "correct": sum(selected_key[a] == actual_key[a] for a in ids)}
        active_errors = [{"primitive_id": a, "actual_output": actual_key[a], "fitted_output": selected_key[a],
            "discovery_occurrences": exposures["discovery"][a], "held_occurrences": exposures["held"][a],
            "reference_actual_letter_occurrences": reference_summary["letter_occurrences"].get(actual_key[a]) if a.startswith("L") else None}
            for a in sorted(active) if selected_key[a] != actual_key[a]]
        inactive_differences = [{"primitive_id": a, "actual_output": actual_key[a], "fitted_output": selected_key[a], "discovery_occurrences": 0, "held_occurrences": 0}
            for a in sorted(inactive) if selected_key[a] != actual_key[a]]
        literal_exposures = {split: {c: sum(n for a, n in exposures[split].items() if a.startswith("L") and actual_key[a] == c) for c in string.ascii_lowercase} for split in exposures}
        group_rows = [{"incorrect_actual_letter_set": list(letters), "incorrect_nonletter_primitive_ids": list(other),
            "wrong_held_word_tokens": count, "fraction_of_all_held_word_tokens": count / held_words,
            "fraction_of_wrong_held_word_tokens": count / wrong_words}
            for (letters, other), count in sorted(wrong_groups.items())]
        if sum(row["wrong_held_word_tokens"] for row in group_rows) != wrong_words:
            raise AssertionError("Error groups do not partition wrong held word tokens")
        oracle = full_evaluation["oracle_objective"]
        fitted = full_evaluation["selected_discovery_objective_replayed"]
        objective = {"oracle": oracle, "selected": fitted,
            "selected_minus_oracle": full_evaluation["selected_minus_oracle"],
            "family_difference_nats": fitted["family_nats"] - oracle["family_nats"],
            "language_difference_nats": fitted["language_nats"] - oracle["language_nats"],
            "family_identical": fitted["family_nats"] == oracle["family_nats"],
            "source": "Copied from completed EVALUATION.json; no key rescoring performed by this audit."}
        worlds.append({"world_id": world_id, "active_key_recovery": key_classes, "active_key_errors": active_errors,
            "inactive_unscored_key_differences": inactive_differences,
            "literal_rule_occurrences_by_actual_letter": literal_exposures,
            "literal_exposure_denominator": "Counts only occurrences of L primitive IDs, not characters emitted by S/W cards.",
            "held_word_tokens": held_words, "correct_held_word_tokens": correct_words, "wrong_held_word_tokens": wrong_words,
            "exact_held_word_accuracy": correct_words / held_words,
            "wrong_word_group_denominator": "Each of the fixed held word tokens is counted once. Error rows are mutually exclusive sets of actually encoded letters whose fixed selected L mapping is wrong; their sum equals all wrong held word tokens. A word with repeated erroneous letters still contributes one token.",
            "wrong_held_words_partition": group_rows,
            "reference_family_membership_among_wrong_held_word_tokens": dict(membership),
            "FULL_OFF_held_word_prediction_disagreements": full_off_word_disagreements,
            "stored_oracle_comparison": objective})
    result = {"schema": "GDT832_POST_RESULT_ORTHOGRAPHY_AUDIT_V1", "status": "POSTHOC_DIAGNOSTIC_ONLY",
        "preregistered_result_unchanged": evaluation["status"], "inputs_sha256": inputs,
        "audit_source_sha256": sha(Path(__file__)), "all_locked_fit_files_verified": len(lock["sha256"]),
        "reference": reference_summary, "control_plaintext_letter_counts": source_summary, "real_FULL_worlds": worlds,
        "empirical_findings": {"direct_v_reference_occurrences": reference_summary["letter_occurrences"]["v"],
            "direct_v_discovery_plaintext_occurrences": source_summary["discovery"]["letter_occurrences"]["v"],
            "direct_v_held_plaintext_occurrences": source_summary["held"]["letter_occurrences"]["v"],
            "all_FULL_oracle_and_selected_family_terms_identical": all(w["stored_oracle_comparison"]["family_identical"] for w in worlds),
            "all_FULL_OFF_held_predictions_identical": all(w["FULL_OFF_held_word_prediction_disagreements"] == 0 for w in worlds)},
        "interpretation": "The reference/control letter-frequency mismatch and concentration of errors on these letter mappings are compatible with a reference-orthography/domain bias. The stored objective favors a wrong key entirely through its language term while the family term is unchanged. This is a post-result explanation candidate, not an independently isolated causal test of orthography or a repaired recovery result.",
        "limits": ["The three keys encode the same historical source, not three independent text samples.",
            "No normalization change, v/u collapsing, replacement key, fit, optimizer extension or additional model score was computed.",
            "No word or paragraph plaintext is exported in this aggregate artifact.",
            "Unused primitive differences are reported separately and remain excluded from active-key recovery.",
            "The original CONTROL_RECOVERY_FAIL and zero joint-gain finding remain unchanged."]}
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=EXPERIMENT)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = run(args.root)
    output = args.output or args.root / "artifacts/POST_RESULT_AUDIT.json"
    output.write_text(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "empirical_findings": result["empirical_findings"],
        "reference_letters": {c: result["reference"]["letter_occurrences"][c] for c in "vukz"},
        "worlds": [{"world_id": row["world_id"], "active_key_errors": row["active_key_errors"],
            "held_words": row["held_word_tokens"], "wrong_held_words": row["wrong_held_word_tokens"],
            "wrong_held_words_partition": row["wrong_held_words_partition"]} for row in result["real_FULL_worlds"]]}, sort_keys=True))


if __name__ == "__main__":
    main()
