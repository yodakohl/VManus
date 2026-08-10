#!/usr/bin/env python3
"""Execute the single hash-frozen EO001 manuscript target."""

from __future__ import annotations

import os
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

import csv
import hashlib
import json
import tempfile
from collections import Counter
from pathlib import Path

import numpy as np

import eo001_core as core


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
FREEZE = BASE / "EO001_TARGET_FREEZE.json"
PANEL_FILE = RESULTS / "eo001_exact_form_onset_capacity.tsv"
SOURCE = RESULTS / "source_native_structural_interlinear_v1.tsv"
PREFLIGHT = RESULTS / "eo001_synthetic_preflight_v2.json"
PREFLIGHT_VALIDATION = RESULTS / "eo001_synthetic_preflight_v2_validation.json"
OUT = RESULTS / "eo001_target.json"
REPORT = RESULTS / "eo001_target_report.md"
RUNNER = Path(__file__).resolve()
REQUIRED_FILES = {
    "EO001_EXACT_FORM_ONSET_TRANSFER_CAPACITY_SPEC.md",
    "EO001_EXACT_FORM_ONSET_TRANSFER_PREREGISTRATION.md",
    "build_eo001_exact_form_onset_capacity.py",
    "validate_eo001_exact_form_onset_capacity.py",
    "eo001_core.py", "run_eo001_synthetic_preflight.py",
    "validate_eo001_synthetic_preflight_v2.py", "run_eo001_target.py",
    "validate_eo001_target.py", "build_eo001_target_freeze.py",
    "results/eo001_exact_form_onset_capacity.tsv",
    "results/eo001_exact_form_onset_capacity.json",
    "results/eo001_exact_form_onset_capacity_validation.json",
    "results/eo001_synthetic_preflight_v2.json",
    "results/eo001_synthetic_preflight_v2_validation.json",
    "results/source_native_structural_interlinear_v1.tsv",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_matrix_hash(matrix: np.ndarray) -> str:
    return hashlib.sha256(np.asarray(matrix, dtype="<f8", order="C").tobytes(order="C")).hexdigest()


def install_pair(result: bytes, report: bytes) -> None:
    if OUT.exists() or REPORT.exists():
        raise FileExistsError("EO001 target already exists")
    with tempfile.TemporaryDirectory(prefix="eo001_target_", dir=RESULTS) as directory:
        first, second = Path(directory) / "result", Path(directory) / "report"
        first.write_bytes(result); second.write_bytes(report)
        if OUT.exists() or REPORT.exists():
            raise FileExistsError("EO001 target appeared during run")
        os.link(first, OUT)
        try:
            os.link(second, REPORT)
        except Exception:
            OUT.unlink(missing_ok=True)
            raise


def report_text(result: dict) -> str:
    summary = result["evaluation"]["summary"]
    lines = [
        "# EO001 exact-form continuation-transfer target", "",
        f"Status: **{result['status']}**.", "",
        f"The frozen same-folio statistic used **{summary['informative_folios']}** informative physical folios. "
        f"Its combined standardized value is **{summary['combined_observed']:+.6f}** with fixed permutation "
        f"p **{summary['combined_p']:.6f}**; **{summary['positive_folios']}/38** folios and "
        f"**{summary['positive_forms']}/9** forms contribute positively.", "",
        "| block | raw effect | z | p |", "|---|---:|---:|---:|",
    ]
    for name in core.BLOCK_DIMS:
        block = result["evaluation"]["blocks"][name]
        lines.append(f"| `{name}` | {block['raw_effect']:+.6f} | {block['z']:+.6f} | {block['p']:.6f} |")
    lines += [
        "", f"Decision: **{result['decision']}**. "
        + ("The narrow source-native continuation fingerprint transfers between factual FIRST and CORE positions. " if result["evaluation"]["passes"] else "The frozen three-block continuation fingerprint does not pass all transfer gates. ")
        + "This does not establish a clause, word, part of speech, sound, meaning, plaintext, language, cipher, or translation.",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing a second EO001 target run")
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    if freeze["status"] != "SEALED_SINGLE_TARGET_AUTHORIZED" or set(freeze["frozen_files"]) != REQUIRED_FILES:
        raise SystemExit("EO001 freeze schema/status drift")
    for name, digest in freeze["frozen_files"].items():
        if name == "results/source_native_structural_interlinear_v1.tsv":
            continue
        if sha(BASE / name) != digest:
            raise SystemExit(f"EO001 safe frozen file drift: {name}")
    if sha(RUNNER) != freeze["frozen_files"][RUNNER.name]:
        raise SystemExit("EO001 runner binding drift")
    preflight = json.loads(PREFLIGHT.read_text())
    validation = json.loads(PREFLIGHT_VALIDATION.read_text())
    if preflight["status"] != "PASS_TARGET_FREE_CALIBRATION" or not all(preflight["gates"].values()):
        raise SystemExit("EO001 preflight not PASS")
    if validation["status"] != "PASS_INDEPENDENT_264_WORLD_RECONSTRUCTION" or validation["max_numeric_delta"] != 0:
        raise SystemExit("EO001 independent preflight not exact PASS")
    if any((BASE / name).exists() for name in freeze["target_artifacts_absent"]):
        raise SystemExit("EO001 target artifact appeared before source access")

    # Target access begins only here.
    if sha(SOURCE) != freeze["target_source_sha256"]:
        raise SystemExit("EO001 target source hash drift")
    panel = core.load_panel(PANEL_FILE)
    with SOURCE.open(encoding="utf-8", newline="") as handle:
        source = list(csv.DictReader(handle, delimiter="\t"))
    by_id = {row["consensus_group_id"]: row for row in source}
    by_locus_index = {(row["locus"], int(row["group_index"])): row for row in source}
    panel_index = {row["anonymous_event_id"]: index for index, row in enumerate(panel.rows)}
    sequences: list[str | None] = [None] * len(panel.rows)
    target_ids = set()
    for source_id, row in by_id.items():
        event = "EO001-" + hashlib.sha256(("EO001|" + source_id).encode()).hexdigest()[:20]
        if event not in panel_index:
            continue
        index = panel_index[event]; masked = panel.rows[index]
        folio = row["page"].split("r", 1)[0].split("v", 1)[0]
        state = "FIRST" if int(row["group_index"]) == 1 else "CORE"
        expected = (row["family_surface"], state, folio, row["section"], row["currier"], row["hand"], row["code"], row["kind"], row["group_index"], row["group_count"], str(int(row["group_count"]) - int(row["group_index"])))
        observed = tuple(masked[key] for key in ("trigger_family_surface", "trigger_state", "physical_folio", "section", "currier", "hand", "code", "kind", "trigger_group_index", "locus_group_count", "remaining_groups_after_trigger"))
        if expected != observed:
            raise SystemExit(f"EO001 target metadata join drift: {event}")
        successor = by_locus_index.get((row["locus"], int(row["group_index"]) + 1))
        if successor is None or successor["factual_position"] != "CORE" or successor["grammar_scope"] != "CONFIRMED_PROSE":
            raise SystemExit("EO001 successor scope/position drift")
        sequences[index] = successor["family_surface"]
        target_ids.add(successor["consensus_group_id"])
    if any(value is None for value in sequences) or len(target_ids) != 1295:
        raise SystemExit("EO001 target join cardinality drift")
    target_sequences = [str(value) for value in sequences]
    blocks = core.fingerprint_matrix(target_sequences)
    evaluation = core.evaluate(panel, blocks)
    sequence_counts = Counter(target_sequences)
    lengths = Counter(map(len, target_sequences))
    gates = {
        "exact_1295_target_join": len(target_sequences) == 1295 and len(target_ids) == 1295,
        "all_successors_core": True,
        "exact_38_informative_folios": evaluation["summary"]["informative_folios"] == 38,
        "all_preflight_gates": all(preflight["gates"].values()),
        "independent_preflight_exact": validation["max_numeric_delta"] == 0,
        **{f"target_{key}": value for key, value in evaluation["gates"].items()},
    }
    passed = evaluation["passes"] and all(gates.values())
    status = "CONFIRM_EXACT_FORM_CONTINUATION_TRANSFER" if passed else "NONCONFIRM_EXACT_FORM_CONTINUATION_TRANSFER"
    decision = "RETAIN_EMBEDDED_ONSET_STRUCTURAL_CANDIDATE" if passed else "RETAIN_POSITION_ATLAS_WITHOUT_CONTINUATION_TRANSFER"
    result = {
        "experiment": "EO001_EXACT_FORM_ONSET_TRANSFER_TARGET", "status": status, "decision": decision,
        "freeze_sha256": sha(FREEZE), "inputs": {"panel_sha256": sha(PANEL_FILE), "source_sha256": sha(SOURCE), "core_sha256": sha(BASE / "eo001_core.py"), "runner_sha256": sha(RUNNER)},
        "target_access": {"source_rows_read": len(source), "successor_rows_joined": len(target_sequences), "successor_surfaces_accessed": len(target_sequences), "member_codes_accessed": 0, "parser_fields_accessed": 0, "semantic_fields_accessed": 0},
        "successor_diagnostics": {"distinct_surfaces": len(sequence_counts), "length_counts": {str(key): value for key, value in sorted(lengths.items())}, "block_sha256": {name: canonical_matrix_hash(matrix) for name, matrix in blocks.items()}},
        "evaluation": evaluation, "gates": gates, "english_glosses": 0,
        "event_level_successors_stored": 0,
        "claim_ceiling": "Exact-form same-folio continuation-construction transfer only; no clause, word, POS, sound, meaning, plaintext, language, cipher, or translation.",
    }
    report = report_text(result)
    result_bytes = (json.dumps(result, indent=2, sort_keys=True) + "\n").encode()
    if any((BASE / name).exists() for name in freeze["target_artifacts_absent"]):
        raise SystemExit("EO001 target artifact appeared before install")
    install_pair(result_bytes, report.encode())


if __name__ == "__main__":
    main()
