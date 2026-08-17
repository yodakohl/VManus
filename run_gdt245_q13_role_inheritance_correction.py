#!/usr/bin/env python3
"""Publish the machine-readable inheritance correction implied by GDT242/244."""
import csv
import hashlib
import json
from pathlib import Path

R = Path(__file__).resolve().parent
INPUTS = [
    "gdt224_result.json", "gdt227_result.json", "gdt228_result.json",
    "gdt229_result.json", "gdt230_result.json", "gdt239_result.json",
    "gdt242_result.json", "gdt243_result.json", "gdt244_result.json",
    "GDT242_F82R_PARAGRAPH_COORDINATE_CORRECTION_REPORT.md",
    "GDT244_F80R_PARAGRAPH_COORDINATE_CORRECTION_REPORT.md",
]
OUT = "gdt245_q13_role_artifact_status.tsv"
DOCS = [
    "GDT245_Q13_ROLE_INHERITANCE_CORRECTION_METHOD.md",
    "GDT245_Q13_ROLE_INHERITANCE_CORRECTION_REPORT.md",
]


def sha(name):
    return hashlib.sha256((R / name).read_bytes()).hexdigest()


ROWS = [
    {
        "source_experiment": "GDT224", "artifact_or_claim": "gdt224_field_role_projection.tsv",
        "layer": "RECORD_RELATIVE_ROLE", "current_state": "SUSPENDED_UNAUDITED_COORDINATE",
        "reason": "f80r and f82r paragraph starts were omitted from the record coordinate",
        "surviving_content": "underlying source groups and HPR2 formal fields",
        "permitted_use": "formal reconstruction only; no q13 role inference",
    },
    {
        "source_experiment": "GDT227", "artifact_or_claim": "gdt227_q13_abstract_interlinear.tsv formal columns",
        "layer": "FORMAL_PARSE", "current_state": "RETAINED_FORMAL_ONLY",
        "reason": "PAGE_HOST/compiler/DY parsing does not require the erroneous role coordinate",
        "surviving_content": "source groups PAGE_HOST compiler cells DY and line ends",
        "permitted_use": "formal grammar and coverage analyses",
    },
    {
        "source_experiment": "GDT227", "artifact_or_claim": "gdt227_q13_abstract_interlinear.tsv role columns",
        "layer": "RECORD_RELATIVE_ROLE", "current_state": "SUSPENDED_UNAUDITED_COORDINATE",
        "reason": "role positions inherit GDT224 record coordinates",
        "surviving_content": "none at semantic-role layer",
        "permitted_use": "historical hypothesis generation only",
    },
    {
        "source_experiment": "GDT227", "artifact_or_claim": "gdt227_identity_role_atlas.tsv role purity",
        "layer": "HOST_ROLE_ASSOCIATION", "current_state": "SUSPENDED_UNAUDITED_COORDINATE",
        "reason": "role labels used to calculate purity inherit collapsed paragraphs",
        "surviving_content": "exact PAGE_HOST recurrence counts",
        "permitted_use": "identity recurrence only; not role purity",
    },
    {
        "source_experiment": "GDT228", "artifact_or_claim": "multi-region short-argument lead",
        "layer": "PAGE_VISUAL_TO_ROLE", "current_state": "SUSPENDED_UNAUDITED_COORDINATE",
        "reason": "page role fractions are computed from GDT227 inherited roles",
        "surviving_content": "source-bound human visual feature manifest",
        "permitted_use": "visual inventory only; rescore after pagewise reconstruction",
    },
    {
        "source_experiment": "GDT229", "artifact_or_claim": "gdt229_q13_semantic_role_lattice.tsv",
        "layer": "SEMANTIC_INTERLINEAR", "current_state": "ARCHIVED_HYPOTHESIS_NOT_ACTIVE_INTERLINEAR",
        "reason": "all q13 role bundles inherit an unaudited record coordinate and both audited discovery pages fail",
        "surviving_content": "candidate document-world vocabulary as abductive alternatives",
        "permitted_use": "historical hypothesis generation only; never as assigned roles",
    },
    {
        "source_experiment": "GDT229", "artifact_or_claim": "gdt229_q13_record_role_summaries.tsv",
        "layer": "RECORD_RELATIVE_ROLE", "current_state": "SUSPENDED_UNAUDITED_COORDINATE",
        "reason": "record keys merge five f80r paragraphs into two and three f82r paragraphs into one",
        "surviving_content": "none at record-role layer",
        "permitted_use": "audit provenance only",
    },
    {
        "source_experiment": "GDT230", "artifact_or_claim": "gdt230_content_host_atlas.tsv role rankings",
        "layer": "HOST_ROLE_ASSOCIATION", "current_state": "SUSPENDED_UNAUDITED_COORDINATE",
        "reason": "rankings use GDT229 assigned role bundles",
        "surviving_content": "PAGE_HOST surface inventory",
        "permitted_use": "host inventory only; no semantic placement ranking",
    },
    {
        "source_experiment": "GDT239", "artifact_or_claim": "f82r visual label dossier",
        "layer": "SOURCE_BOUND_VISUAL_LABEL", "current_state": "RETAINED",
        "reason": "label loci ownership grades and source families do not use prose record coordinates",
        "surviving_content": "13 labels one connected-component and twelve proximity-only observations",
        "permitted_use": "formal label renderer and provenance-bound visual inventory",
    },
    {
        "source_experiment": "GDT239", "artifact_or_claim": "f82r 16 short-like / 10 instruction-like prose counts",
        "layer": "RECORD_RELATIVE_ROLE", "current_state": "WITHDRAWN_F82R",
        "reason": "the eight scaffolded loci were placed in one merged record rather than three paragraphs",
        "surviving_content": "26 formal fields on eight loci",
        "permitted_use": "formal fields only; old role counts must not be quoted as current",
    },
    {
        "source_experiment": "GDT243", "artifact_or_claim": "f82r long-versus-compact missingness result",
        "layer": "FORMAL_EXTENT_ANALOGY", "current_state": "RETAINED_FORMAL_ANALOGY_ONLY",
        "reason": "classification is stable across every feasible within-paragraph completion but externally length-driven",
        "surviving_content": "20 clause-like and 31 short-like formal extent analogies",
        "permitted_use": "formal architecture only; no operation ingredient or semantic role",
    },
    {
        "source_experiment": "GDT231-GDT238", "artifact_or_claim": "graphical label prefix/relation renderer",
        "layer": "LABEL_RENDERER", "current_state": "RETAINED",
        "reason": "label-prefix transfer and relation-mode tests do not use q13 prose paragraph positions",
        "surviving_content": "partial section-specialized graphical-label prefix layer",
        "permitted_use": "formal rendering predictions; no object or relation meaning",
    },
    {
        "source_experiment": "GDT016/HPR2", "artifact_or_claim": "PAGE_HOST compiler DY and line-end parses",
        "layer": "FORMAL_PARSE", "current_state": "RETAINED",
        "reason": "the parser is source-group local and independent of q13 role coordinates",
        "surviving_content": "all formal parsing outputs",
        "permitted_use": "formal grammar segmentation coverage and new corrected coordinates",
    },
    {
        "source_experiment": "GDT236", "artifact_or_claim": "page-conditioned hybrid technical record compiler",
        "layer": "GENERATOR_ARCHITECTURE", "current_state": "RETAINED_WITH_ROLE_LAYER_REMOVED",
        "reason": "record/compiler and label-rendering evidence survives but the q13 recipe-like role scaffold does not",
        "surviving_content": "page/paragraph/field compiler plus unresolved content channel",
        "permitted_use": "leading formal generator; zero executable semantic assignments",
    },
]


def main():
    for name in INPUTS:
        assert (R / name).exists(), name
    c82 = json.loads((R / "gdt242_result.json").read_text())
    c80 = json.loads((R / "gdt244_result.json").read_text())
    assert c82["status"] == "GDT229_F82R_RECORD_COORDINATE_INVALID_THREE_PARAGRAPHS_COLLAPSED"
    assert c80["status"] == "GDT229_F80R_RECORD_COORDINATE_INVALID_FIVE_PARAGRAPHS_COLLAPSED_TO_TWO"
    with (R / OUT).open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(ROWS[0]), delimiter="\t", lineterminator="\n")
        w.writeheader(); w.writerows(ROWS)
    result = {
        "experiment": "GDT245_Q13_ROLE_INHERITANCE_CORRECTION",
        "status": "Q13_ROLE_LAYER_SUSPENDED_FORMAL_COMPILER_AND_LABEL_RENDERER_RETAINED",
        "artifact_status_rows": len(ROWS),
        "states": {s: sum(r["current_state"] == s for r in ROWS) for s in sorted({r["current_state"] for r in ROWS})},
        "audited_pages": {"f80r": {"physical_paragraphs": 5, "historical_records": 2}, "f82r": {"physical_paragraphs": 3, "historical_records": 1}},
        "live_generator": "page-conditioned paragraph/field compiler plus label renderer with unresolved content channel",
        "active_semantic_assignments": 0,
        "correction": "Withdraw executable q13 semantic roles inherited from GDT224 while retaining source-local formal parses and independently tested label rendering.",
        "claim_ceiling": "Inheritance correction only; no replacement role, word, language, plaintext, or translation.",
        "f84": {"input": False, "retained": False, "joined": False, "scored": False, "new_access": False},
        "inputs": {name: sha(name) for name in INPUTS},
        "outputs": {OUT: sha(OUT)},
        "documents": {}, "implementation": {},
    }
    for name in DOCS:
        if (R / name).exists(): result["documents"][name] = sha(name)
    result["implementation"][Path(__file__).name] = sha(Path(__file__).name)
    result["content_hash"] = hashlib.sha256(json.dumps(result, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    (R / "gdt245_result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": result["status"], "rows": len(ROWS), "states": result["states"]}, sort_keys=True))


if __name__ == "__main__": main()
