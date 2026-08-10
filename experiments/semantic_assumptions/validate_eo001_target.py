#!/usr/bin/env python3
"""Production-free EO001 target reconstruction using the validated clean scorer."""

from __future__ import annotations

import os
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

import numpy as np

import validate_eo001_synthetic_preflight_v2 as independent


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
FREEZE = BASE / "EO001_TARGET_FREEZE.json"
PANEL = RESULTS / "eo001_exact_form_onset_capacity.tsv"
SOURCE = RESULTS / "source_native_structural_interlinear_v1.tsv"
TARGET = RESULTS / "eo001_target.json"
TARGET_REPORT = RESULTS / "eo001_target_report.md"
VALIDATOR = Path(__file__).resolve()
OUT = RESULTS / "eo001_target_validation.json"
REPORT = RESULTS / "eo001_target_validation_report.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def matrix_hash(matrix: np.ndarray) -> str:
    return hashlib.sha256(np.asarray(matrix, dtype="<f8", order="C").tobytes(order="C")).hexdigest()


def report_text(result: dict) -> str:
    summary = result["evaluation"]["summary"]
    lines = ["# EO001 exact-form continuation-transfer target", "", f"Status: **{result['status']}**.", "",
             f"The frozen same-folio statistic used **{summary['informative_folios']}** informative physical folios. Its combined standardized value is **{summary['combined_observed']:+.6f}** with fixed permutation p **{summary['combined_p']:.6f}**; **{summary['positive_folios']}/38** folios and **{summary['positive_forms']}/9** forms contribute positively.", "",
             "| block | raw effect | z | p |", "|---|---:|---:|---:|"]
    for name in independent.DIMS:
        block = result["evaluation"]["blocks"][name]
        lines.append(f"| `{name}` | {block['raw_effect']:+.6f} | {block['z']:+.6f} | {block['p']:.6f} |")
    lines += ["", f"Decision: **{result['decision']}**. " + ("The narrow source-native continuation fingerprint transfers between factual FIRST and CORE positions. " if result["evaluation"]["passes"] else "The frozen three-block continuation fingerprint does not pass all transfer gates. ") + "This does not establish a clause, word, part of speech, sound, meaning, plaintext, language, cipher, or translation."]
    return "\n".join(lines) + "\n"


def main() -> None:
    if not TARGET.is_file() or not TARGET_REPORT.is_file():
        raise SystemExit("EO001 target is absent")
    if OUT.exists() or REPORT.exists():
        raise SystemExit("EO001 target validation already exists")
    freeze = json.loads(FREEZE.read_text())
    for name, digest in freeze["frozen_files"].items():
        if sha(BASE / name) != digest:
            raise SystemExit(f"EO001 frozen file drift: {name}")
    if sha(VALIDATOR) != freeze["frozen_files"][VALIDATOR.name]:
        raise SystemExit("EO001 target validator binding drift")
    independent.DATA = independent.read_panel()
    with SOURCE.open(encoding="utf-8", newline="") as handle:
        source = list(csv.DictReader(handle, delimiter="\t"))
    by_locus = {(row["locus"], int(row["group_index"])): row for row in source}
    panel_ids = {row["anonymous_event_id"]: index for index, row in enumerate(independent.DATA.rows)}
    sequences = [None] * 1295; target_ids = set()
    for row in source:
        event = "EO001-" + hashlib.sha256(("EO001|" + row["consensus_group_id"]).encode()).hexdigest()[:20]
        if event not in panel_ids: continue
        index = panel_ids[event]; masked = independent.DATA.rows[index]
        folio = row["page"].split("r", 1)[0].split("v", 1)[0]
        state = "FIRST" if int(row["group_index"]) == 1 else "CORE"
        expected = (row["family_surface"], state, folio, row["section"], row["currier"], row["hand"], row["code"], row["kind"], row["group_index"], row["group_count"], str(int(row["group_count"]) - int(row["group_index"])))
        observed = tuple(masked[key] for key in ("trigger_family_surface", "trigger_state", "physical_folio", "section", "currier", "hand", "code", "kind", "trigger_group_index", "locus_group_count", "remaining_groups_after_trigger"))
        if expected != observed: raise AssertionError("metadata join")
        successor = by_locus[(row["locus"], int(row["group_index"]) + 1)]
        if successor["factual_position"] != "CORE" or successor["grammar_scope"] != "CONFIRMED_PROSE": raise AssertionError("successor scope")
        sequences[index] = successor["family_surface"]; target_ids.add(successor["consensus_group_id"])
    if any(value is None for value in sequences) or len(target_ids) != 1295: raise AssertionError("join count")
    blocks = independent.fp_matrix([str(value) for value in sequences])
    evaluation = independent.evaluate(blocks)
    stored = json.loads(TARGET.read_text())
    checks, delta = independent.compare(stored["evaluation"], evaluation, "evaluation")
    counts = Counter(map(str, sequences)); lengths = Counter(map(len, sequences))
    diagnostics = {"distinct_surfaces": len(counts), "length_counts": {str(key): value for key, value in sorted(lengths.items())}, "block_sha256": {name: matrix_hash(matrix) for name, matrix in blocks.items()}}
    if stored["successor_diagnostics"] != diagnostics: raise AssertionError("diagnostics")
    gates = {"exact_1295_target_join": True, "all_successors_core": True, "exact_38_informative_folios": evaluation["summary"]["informative_folios"] == 38, "all_preflight_gates": True, "independent_preflight_exact": True, **{f"target_{key}": value for key, value in evaluation["gates"].items()}}
    if stored["gates"] != gates: raise AssertionError("gates")
    passed = evaluation["passes"] and all(gates.values())
    status = "CONFIRM_EXACT_FORM_CONTINUATION_TRANSFER" if passed else "NONCONFIRM_EXACT_FORM_CONTINUATION_TRANSFER"
    decision = "RETAIN_EMBEDDED_ONSET_STRUCTURAL_CANDIDATE" if passed else "RETAIN_POSITION_ATLAS_WITHOUT_CONTINUATION_TRANSFER"
    if stored["status"] != status or stored["decision"] != decision or stored["event_level_successors_stored"] != 0 or stored["english_glosses"] != 0: raise AssertionError("decision/ceiling")
    if TARGET_REPORT.read_text() != report_text(stored): raise AssertionError("report bytes")
    checks += 8 + len(source)
    # A changed successor must change at least one fingerprint block.
    mutated = list(map(str, sequences)); mutated[0] = "A" if mutated[0] != "A" else "B"
    changed = independent.fp_matrix(mutated)
    if all(np.array_equal(blocks[name], changed[name]) for name in independent.DIMS): raise AssertionError("target mutation not detected")
    checks += 1
    result = {"experiment": "EO001_TARGET_VALIDATION", "status": "PASS_PRODUCTION_FREE_TARGET_RECONSTRUCTION", "checks": checks, "max_numeric_delta": delta, "target_sha256": sha(TARGET), "validator_sha256": sha(VALIDATOR), "decision": decision, "failures": [], "successor_rows_accessed": 1295, "event_level_successors_stored": 0, "english_glosses": 0, "claim_ceiling": stored["claim_ceiling"]}
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text("# EO001 target validation\n\n" + f"Status: **{result['status']}**.\n\nProduction-free code reconstructed all 1,295 joins, three fingerprint matrices, 32,768-assignment statistics, gates, decision, and exact report in **{checks:,}** checks; maximum numeric delta was **{delta:.3g}**.\n\nThis validates only the frozen structural result and supplies no word, meaning, plaintext, or translation.\n", encoding="utf-8")


if __name__ == "__main__":
    main()
