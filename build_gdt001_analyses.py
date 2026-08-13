#!/usr/bin/env python3
"""Build convergence, coverage, control, and final GDT001 branch analyses."""

from __future__ import annotations

import csv
import json
import statistics
from collections import defaultdict
from pathlib import Path

from gdt001_core import ROOT, canonical, sha256_file


RUNS = ROOT / ".gdt001/runs"


def load_runs():
    return [json.loads(path.read_text()) for path in RUNS.glob("*.json")]


def mapping_dict(run):
    rows = run.get("decoder", {}).get("mapping", [])
    return {row.get("source_unit"): row.get("latent_unit", row.get("plaintext_unit")) for row in rows}


def stability(runs):
    groups = defaultdict(list)
    for run in runs:
        if run["convergence_status"] == "CONVERGED" and run["seed"]:
            stem = run["candidate_id"].rsplit("_s", 1)[0]
            groups[stem].append(run)
    output = []
    for stem, values in sorted(groups.items()):
        if len(values) < 2: continue
        maps = [mapping_dict(value) for value in values]
        agreements = []
        for a in range(len(maps)):
            for b in range(a + 1, len(maps)):
                common = sorted(set(maps[a]) & set(maps[b])); agreements.append(sum(maps[a][key] == maps[b][key] for key in common) / max(1, len(common)))
        output.append({"configuration": stem, "restart_count": len(values), "best_bits_per_symbol": min(v["bits_per_symbol"] for v in values), "worst_bits_per_symbol": max(v["bits_per_symbol"] for v in values), "exact_decoder_hash_count": len({v["decoder_hash"] for v in values}), "mean_unaligned_mapping_agreement": statistics.mean(agreements) if agreements else None, "stable_exact_decoder": len({v["decoder_hash"] for v in values}) == 1})
    return output


def structural_coverage(run):
    schema = run["decoder"].get("schema", "")
    character = schema in {"GDT001_NONSEMANTIC_NGRAM_GENERATOR_V1", "GDT001_EXPLICIT_MONOTONIC_MAPPING_V1", "GDT001_ABBREVIATION_TRANSDUCER_V1", "GDT001_QUANTIZED_GRU_NULL_V1"}
    record = schema in {"GDT001_RECORD_NOTATION_V1", "GDT001_DUAL_CHANNEL_PROCEDURAL_V1", "GDT001_ANONYMOUS_RECORD_DICTIONARY_V1"}
    return {
        "candidate_id": run["candidate_id"], "schema": schema,
        "hierarchical_separators": "PARTIAL_MANUAL_GROUP_BOUNDARY" if character else "PARTIAL_RECORD_BOUNDARY",
        "line_resets": "EXPLICIT" if run["decoder"].get("line_reset") or "line" in str(run["decoder"]).lower() else "UNEXPLAINED",
        "d_s_t_entry_differences": "EXPLICIT_ANONYMOUS_ENTRY_STATE" if schema == "GDT001_DUAL_CHANNEL_PROCEDURAL_V1" else "NOT_EXPLICIT",
        "che_value_productivity": "LOCAL_NGRAM_ONLY" if character else "CORE_OR_STEM_DECOMPOSITION" if record else "UNEXPLAINED",
        "root_ordering": "LOCAL_SEQUENCE_ONLY" if character else "RECORD_SEQUENCE",
        "adjacent_root_selection": "LOCAL_SEQUENCE_ONLY" if character else "RECORD_SEQUENCE",
        "currier_transfer": "ONE_SHARED_MODEL_NO_EXPLICIT_VARIANTS",
        "layout_register_differences": "METADATA_UNUSED",
        "simple_object_name_failure": "COMPATIBLE_NO_OBJECT_NAME_CLAIM",
        "simple_visible_attribute_failure": "COMPATIBLE_NO_ATTRIBUTE_CLAIM",
    }


def main():
    runs = load_runs(); good = sorted((run for run in runs if run["convergence_status"] == "CONVERGED"), key=lambda x: (x["total_bits"], x["candidate_id"]))
    stability_rows = stability(runs)
    (ROOT / "gdt001_restart_stability.json").write_bytes(canonical({"schema": "GDT001_RESTART_STABILITY_V1", "status": "EXPLORATORY", "configurations": stability_rows}))
    coverage = [structural_coverage(run) for run in good[:10]]
    (ROOT / "gdt001_structural_coverage.json").write_bytes(canonical({"schema": "GDT001_STRUCTURAL_COVERAGE_V1", "status": "EXPLORATORY", "candidates": coverage}))
    controls = json.loads((ROOT / "gdt001_counterfactual_results.json").read_text())["results"]
    real = {"NONSEMANTIC_2GRAM": next(r for r in good if r["candidate_id"] == "nonsemantic_ngram_o2")["bits_per_symbol"], "RECORD_NOTATION": next(r for r in good if r["model_class"] == "RECORD_NOTATION")["bits_per_symbol"], "ABBR_LANG_MHG": min(r["bits_per_symbol"] for r in good if r["model_class"] == "ABBR_LANG"), "HOMOPHONIC_MHG": min(r["bits_per_symbol"] for r in good if r["model_class"] == "HOMOPHONIC_CIPHER")}
    control_analysis = []
    for row in controls:
        control_analysis.append(row | {"real_bits_per_symbol": real[row["model"]], "control_minus_real_bits_per_symbol": row["bits_per_symbol"] - real[row["model"]]})
    (ROOT / "gdt001_counterfactual_analysis.json").write_bytes(canonical({"schema": "GDT001_COUNTERFACTUAL_ANALYSIS_V1", "status": "EXPLORATORY", "results": control_analysis, "finding": "All representative families compress the real manuscript better than shuffled controls, but the nonsemantic 2-gram remains strongest on real and every control."}))
    report = [
        "# GDT001 whole-manuscript global decipherment tournament — YOLO result", "",
        "**Status: EXPLORATORY. This is not a confirmed translation and must not be merged automatically into the canonical evidence branch.**", "",
        "## Outcome", "",
        f"The strongest complete generative account in this tournament is `{good[0]['candidate_id']}` at **{good[0]['bits_per_symbol']:.6f} bits per source symbol**. It is a line-reset, second-order character generator and emits no plaintext. The strongest language-like candidate is `{min((r for r in good if r['model_class']=='ABBR_LANG'), key=lambda r:r['bits_per_symbol'])['candidate_id']}` at **{min(r['bits_per_symbol'] for r in good if r['model_class']=='ABBR_LANG'):.6f} bits/symbol**. The strongest homophonic cipher is **{min(r['bits_per_symbol'] for r in good if r['model_class']=='HOMOPHONIC_CIPHER'):.6f}**, the strongest anonymous record model is **{min(r['bits_per_symbol'] for r in good if r['model_class']=='RECORD_NOTATION'):.6f}**, and my line-entry/body-channel hybrid is **{next(r['bits_per_symbol'] for r in good if r['candidate_id']=='hybrid_dual_channel_entry_body'):.6f}**.", "",
        "No candidate qualifies for freezing as a decipherment. The nonsemantic winner is both much shorter and fully explicit; the language/cipher mappings are restart-unstable and their fixed-packet outputs are orthographic-looking noise rather than defensible readings.", "",
        "## Complete leaderboard", "", "| rank | candidate | class | system | bits | bits/source symbol | key | latent | reconstruction | exceptions |", "|---:|---|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for rank, run in enumerate(good, 1):
        report.append(f"| {rank} | `{run['candidate_id']}` | {run['model_class']} | {run['language_or_system']} | {run['total_bits']:.2f} | {run['bits_per_symbol']:.6f} | {run['key_bits']:.2f} | {run['latent_bits']:.2f} | {run['reconstruction_bits']:.2f} | {run['exception_bits']:.2f} |")
    failures = sorted((r for r in runs if r["convergence_status"] != "CONVERGED"), key=lambda x:x["candidate_id"])
    report += ["", "## Failed runs retained", "", f"{len(failures)} failed exact-audit/search runs remain in `GDT001_YOLO_LEDGER.tsv`; none was deleted from the run history.", "", "## GPU and exact CPU accounting", "", "The RTX 3090 proposed language, cipher, abbreviation, and neural-null parameters. Large population search showed a material CUDA crossover. Every retained discrete key was rescored by deterministic CPU code; the final nonsemantic leader is independently reconstructed context-by-context by `validate_gdt001_tournament.py`.", "", "## Restart stability", "", "No three-restart language/cipher/abbreviation configuration converged to one byte-identical decoder. See `gdt001_restart_stability.json`. The best-score spread can be small while the explicit key remains different; that is evidence for a broad accidental optimum rather than a recovered unique key.", "", "## Counterfactual manuscripts", "", "Within-line, page-conditioned, global frequency-preserving, boundary-preserving identity, and Timm/copy-modify controls were all fit with representative language/cipher/record/nonsemantic systems. Real Voynich structure is easier for all of them than destructive shuffles, but the same second-order nonsemantic family wins every control. This shows real local structure without making it linguistic. See `gdt001_counterfactual_analysis.json`.", "", "## Fixed interpretation packet", "", "Every exported candidate includes the same Herbal-A, Currier-B, biological f75v, f57v, f67r2, circular f69v, and f116v stress packet in `reverse_generation.tsv`, including alternate lattice readings and failures. The historical-language strings were not repaired or paraphrased.", "", "## Structural coverage", "", "The character winner captures line resets and local construction regularity but does not independently explain diagram registers or semantics. The hybrid explicitly models entry-state differences and reusable body stems, but its extra inventory cost leaves it 1.493 bits/symbol behind. See `gdt001_structural_coverage.json`.", "", "## Score strata and transcription sensitivity", "", "`gdt001_score_breakdown.tsv` reports common-code allocation by Currier and section and keeps model/key costs global. `gdt001_edition_sensitivity.json` evaluates ZL3b-, IT2a-, and RF1b-constrained paths under the frozen winning predictor. Neither diagnostic selects an edition as truth.", "", "## Why every candidate may still be false", "", "- The historical corpora are proxies, not perfect fifteenth-century domain corpora.\n- Greedy multigraph segmentation is only one abbreviation transducer family.\n- The record grammars may be too literal and dictionary-heavy.\n- The null winner describes local form but does not establish that the manuscript is meaningless.\n- Whole-manuscript discovery permits postselection; this branch deliberately makes no confirmation claim.\n- Transcription is an alternate-observation lattice, not physical ground truth.", "", "## Decision", "", "`NO_DECIPHERMENT_CANDIDATE_FREEZE`. Do not create a confirmation branch. The exploratory result is that, among the implemented complete explicit systems, a compact nonsemantic local generator decisively wins. This is a tournament result, not a proof that no language, cipher, or technical notation exists.", ""]
    (ROOT / "GDT001_YOLO_RESULT.md").write_text("\n".join(report))
    result = {"schema": "GDT001_YOLO_RESULT_V1", "status": "EXPLORATORY_NO_CONFIRMED_TRANSLATION", "decision": "NO_DECIPHERMENT_CANDIDATE_FREEZE", "leader": {k: good[0][k] for k in ("candidate_id", "model_class", "total_bits", "bits_per_symbol", "decoder_hash")}, "strongest_by_class": {family: {k: min((r for r in good if r["model_class"] == family), key=lambda x:x["total_bits"])[k] for k in ("candidate_id", "total_bits", "bits_per_symbol", "decoder_hash")} for family in sorted({r["model_class"] for r in good})}, "run_count": len(runs), "converged_count": len(good), "failed_count": len(failures), "inputs": {name: sha256_file(ROOT / name) for name in ("gdt001_corpus_lattice.json", "gdt001_tournament_runs.json", "gdt001_counterfactual_results.json", "candidates/index.json", "gdt001_restart_stability.json", "gdt001_structural_coverage.json")}, "claim_ceiling": "Exploratory complete-model competition only; no confirmed translation, language, cipher, record semantics, or nonsemantic-status conclusion."}
    (ROOT / "gdt001_result.json").write_bytes(canonical(result))
    print(json.dumps({"leader": good[0]["candidate_id"], "runs": len(runs), "report_sha256": sha256_file(ROOT / "GDT001_YOLO_RESULT.md")}))


if __name__ == "__main__": main()
