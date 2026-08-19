#!/usr/bin/env python3
"""Build the source-only GDT351 capacity audit."""
from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from tools.vmanus_experiment import GuardedTSV  # noqa: E402
EXP = ROOT / "experiments/yolo/gdt351_remaining_referent_label_capacity"
ART = EXP / "artifacts"
CAND = ROOT / "gdt169_external_referent_candidates.tsv"
REL = ROOT / "gdt151_relation_inventory.tsv"
EXACT = ROOT / "experiments/semantic_assumptions/results/existing_human_exact_locus_annotations.tsv"
PAGE = ROOT / "experiments/semantic_assumptions/results/existing_human_page_annotations.tsv"
GDT152_METHOD = ROOT / "GDT152_OWNED_LABEL_HPR2_PAGE_ADDRESS_METHOD.md"


def read(path: Path):
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stable(obj) -> bytes:
    return (json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()


def main() -> None:
    ART.mkdir(parents=True, exist_ok=True)
    candidates = [
        r for r in read(CAND)
        if r["evidence_panel"] == "HERBAL_TO_PHARMA"
        and r["assertion_strength"] == "ASSERTED_SAME"
        and r["local_query_locus"] == "NONE"
    ]
    assert [r["candidate_id"] for r in candidates] == [
        "GDT151_HP006", "GDT151_HP011", "GDT151_HP019", "GDT151_HP020"
    ]
    rel = {r["relation_id"]: r for r in read(REL)}
    target_pages = {r["target_page"] for r in candidates}
    exact_guard = GuardedTSV(EXACT, selector_column="page", allowed_values=target_pages, forbidden_prefixes=("f84",), forbidden_action="skip")
    page_guard = GuardedTSV(PAGE, selector_column="page", allowed_values=target_pages, forbidden_prefixes=("f84",), forbidden_action="skip")
    exact = list(exact_guard)
    page = {r["page"]: r for r in page_guard}

    specs = {
        "GDT151_HP006": ("204", "NO_SEPARATE_TARGET_LABEL", "f102r1 has four plant fragments but only one plant-fragment label; the published query f102r1.2 is attached to fragment 203, leaving fragment 204 without a mapped label."),
        "GDT151_HP011": ("206", "NO_SEPARATE_TARGET_LABEL", "f102r2 has nine plant fragments but only two plant-fragment labels; the published queries f102r2.21/.22 are the bottom-row fragments 212/213, leaving fragment 206 without a mapped label."),
        "GDT151_HP019": ("205", "NO_SEPARATE_TARGET_LABEL", "f102r2 has nine plant fragments but only two plant-fragment labels; the published queries f102r2.21/.22 are the bottom-row fragments 212/213, leaving fragment 205 without a mapped label."),
        "GDT151_HP020": ("61", "AMBIGUOUS_PROXIMITY_ONLY", "The only plausible row-end inscription, f89v2.28, is human-described between plants [3,3] and [3,4]; it does not singularly own fragment 61 ([3,4])."),
    }
    # Assertions tie the hard-coded source interpretation to current public bytes.
    assert "fragment 204" in rel["GDT151_HP006"]["raw_human_illustration_description"].lower()
    assert "fragment 206" in rel["GDT151_HP011"]["raw_human_illustration_description"].lower()
    assert "fragment 205" in rel["GDT151_HP019"]["raw_human_illustration_description"].lower()
    assert "fragment 61" in rel["GDT151_HP020"]["raw_human_illustration_description"].lower()
    assert "four relatively large herb fragments" in page["f102r1"]["illustrations"]
    assert "1 label of a plant fragment" in page["f102r1"]["text_description"]
    assert "(9 in total)" in page["f102r2"]["illustrations"]
    assert "2 labels of plant fragments" in page["f102r2"]["text_description"]
    method152 = GDT152_METHOD.read_text(encoding="utf-8")
    assert "f102r1.2 → f37v" in method152
    assert "f102r2.21 → f18v" in method152 and "f102r2.22 → f23r" in method152
    row28 = next(r for r in exact if r["locus"] == "f89v2.28")
    assert "Between plants <f89v2>[3,3] and <f89v2>[3,4]" in row28["local_comment"]

    rows = []
    for c in candidates:
        frag, status, reason = specs[c["candidate_id"]]
        rows.append({
            "candidate_id": c["candidate_id"],
            "source_page": c["source_page"],
            "target_page": c["target_page"],
            "catalogue_fragment": frag,
            "assertion_strength": c["assertion_strength"],
            "prior_local_query": c["local_query_locus"],
            "capacity_status": status,
            "singular_owned_locus": "NONE",
            "reason": reason,
            "image_opened": "0",
            "formal_identity_opened_or_scored": "0",
        })
    out = ART / "gdt351_capacity.tsv"
    with out.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        w.writeheader(); w.writerows(rows)

    result = {
        "experiment": "GDT351",
        "schema": "GDT351_REMAINING_REFERENT_LABEL_CAPACITY_V1",
        "status": "STOP_ZERO_NEW_SINGULAR_OWNED_REFERENT_LABELS",
        "counts": {
            "frozen_relations": 4,
            "no_separate_target_label": 3,
            "ambiguous_proximity_only": 1,
            "eligible_new_local_queries": 0,
        },
        "source_access": {
            "manuscript_images_opened": False,
            "voynich_formal_identity_opened_joined_or_scored": False,
            "final_guarded_run_f84_rows_parsed_retained_joined_or_scored": False,
            "prepublication_first_local_build_parsed_global_human_rows_including_f84": True,
            "prepublication_f84_rows_displayed_or_used_for_selection_or_scoring": False,
            "correction_status": "PREPUBLICATION_SOURCE_ACCESS_CORRECTED",
            "guard_stats": {
                "exact": exact_guard.stats.__dict__,
                "page": page_guard.stats.__dict__,
            },
        },
        "decision": "The remaining four asserted-same GDT169 relations supply no new singularly owned target inscription under the cached human sources.",
        "next_route": "Acquire a genuinely new source-bound repeated referent with singular inscription ownership; do not repair these rows by visual proximity.",
        "claim_ceiling": "Source-capacity result only; no plant identity, label meaning, word, language, plaintext, or translation.",
        "inputs": {str(p.relative_to(ROOT)): sha(p) for p in [CAND, REL, EXACT, PAGE, GDT152_METHOD]},
        "outputs": {str(out.relative_to(ROOT)): sha(out)},
        "documents": {str(p.relative_to(ROOT)): sha(p) for p in [EXP / "METHOD.md", EXP / "REPORT.md"] if p.exists()},
        "implementation": {str(Path(__file__).relative_to(ROOT)): sha(Path(__file__))},
        "superseded_prepublication_local_bytes": {
            "capacity_sha256": "8444b76edd5dcbc6dc44e10846068349b43684bf0d0b32a2dd410063a326bfeb",
            "result_sha256": "043a9d0623d66ee0efbec4bc47dfa8450e916cdbb11d408efbaea39ba93e01c7",
            "validation_sha256": "af96bc5eae97e41e75dfd5fde41b558a4550d62d6453d07b2e79e582c0d9b1f4",
        },
    }
    content = dict(result)
    result["result_content_sha256"] = hashlib.sha256(stable(content)).hexdigest()
    (ART / "gdt351_result.json").write_bytes(stable(result))


if __name__ == "__main__":
    main()
