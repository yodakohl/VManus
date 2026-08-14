#!/usr/bin/env python3
"""Build the compact GDT004 postselected physical-module atlas."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SEL = ROOT / "gdt004_module_shape_selection.tsv"
OBS = ROOT / "gdt004_module_shape_observations.tsv"
SRC = ROOT / "experiments/semantic_assumptions/results/source_separator_transcription.tsv"
STA = ROOT / "experiments/semantic_assumptions/results/source_sta_group_alignment.tsv"
PRED = ROOT / "gdt003_holdout_predictions.tsv"
ATLAS = ROOT / "gdt004_module_shape_atlas.tsv"
HYP = ROOT / "gdt004_module_shape_hypotheses.tsv"
RESULT = ROOT / "gdt004_module_shape_result.json"


def rows(path: Path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def guarded_locus_rows(path: Path, wanted_loci: set[str]):
    """Retain only whitelisted loci; do not parse other formal payload rows."""
    with path.open(encoding="utf-8") as f:
        header = f.readline().rstrip("\n").split("\t")
        locus_i = header.index("locus")
        out = []
        for line in f:
            probe = line.split("\t", locus_i + 1)
            if len(probe) <= locus_i or probe[locus_i] not in wanted_loci:
                continue
            values = line.rstrip("\n").split("\t")
            out.append(dict(zip(header, values)))
    return out


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_tsv(path: Path, data: list[dict], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, delimiter="\t", lineterminator="\n", fieldnames=fields)
        w.writeheader()
        w.writerows(data)


def main() -> None:
    selection = rows(SEL)
    observations = {r["target_id"]: r for r in rows(OBS)}
    assert len(selection) == len(observations) == 9
    assert len({r["target_id"] for r in selection}) == 9
    assert len({r["physical_folio"] for r in selection}) == 9
    assert all("f84" not in json.dumps(r) for r in selection)

    wanted = {(r["locus"], r["group_index"]) for r in selection}
    wanted_loci = {r["locus"] for r in selection}
    source = [r for r in guarded_locus_rows(SRC, wanted_loci) if (r["locus"], r["source_group_index"]) in wanted]
    sta = [r for r in guarded_locus_rows(STA, wanted_loci) if (r["locus"], r["source_group_index"]) in wanted]
    assert all(r["page"] != "f84r" for r in source)
    predictions = [
        r for r in rows(PRED)
        if r["evaluation"] == "FOLIO_HELD_NOVEL_FORM"
        and any(r["target_locus_examples"] == s["locus"] for s in selection)
    ]

    output = []
    for s in selection:
        o = observations[s["target_id"]]
        ss = [r for r in source if r["locus"] == s["locus"] and r["source_group_index"] == s["group_index"]]
        st = [r for r in sta if r["locus"] == s["locus"] and r["source_group_index"] == s["group_index"]]
        assert {r["edition"] for r in ss} == {"ZL3b", "IT2a", "RF1b"}
        assert {r["edition"] for r in st} == {"ZL3b", "IT2a", "RF1b"}
        assert {r["nearest_basic_eva_primary"] for r in st} == {s["target_surface"]}
        assert {r["source_group_count"] for r in ss} == {s["group_count"]}
        p = [r for r in predictions if r["target_locus_examples"] == s["locus"] and r["predicted_fourth"] == s["target_surface"]]
        assert len(p) == 1
        p = p[0]
        z = next(r for r in ss if r["edition"] == "ZL3b")
        editions_raw = ";".join(f"{r['edition']}={r['ivtff_group_raw']}" for r in sorted(ss, key=lambda x: x["edition"]))
        row = dict(s)
        row.update({
            "section": z["section"],
            "currier": z["currier"],
            "hand": z["hand"],
            "grammar_scope": z["grammar_scope"],
            "alternate_readings": editions_raw,
            "alternate_basic_surface_agreement": "3_OF_3",
            "folio_holdout_paradigm_rank": p["paradigm_rank_in_fold"],
            "folio_holdout_ngram_rank": p["ngram_rank_in_fold"],
            "folio_holdout_exact_correct": p["exact_prediction_correct"],
        })
        row.update(o)
        output.append(row)

    fields = list(selection[0]) + [
        "section", "currier", "hand", "grammar_scope", "alternate_readings",
        "alternate_basic_surface_agreement", "folio_holdout_paradigm_rank",
        "folio_holdout_ngram_rank", "folio_holdout_exact_correct",
    ] + [k for k in next(iter(observations.values())) if k != "target_id"]
    write_tsv(ATLAS, output, fields)

    q = sum(r["operation_A"] == "PREPEND_Q" for r in output)
    dy = sum(r["target_surface"].endswith("dy") for r in output)
    left_sep = sum(r["left_cut_state"] == "DISTINCT_PHYSICAL_SEPARATOR" for r in output)
    right_sep = sum(r["right_cut_state"] == "DISTINCT_PHYSICAL_SEPARATOR" for r in output)
    hypotheses = [
        {"rank":"1", "candidate_id":"G4_EDGE_Q", "formal_candidate":"REUSABLE_LEADING_Q_EDGE_SEQUENCE", "support":"8/9 targets; 8/8 applicable PREPEND_Q targets", "physical_separator_support":f"{left_sep}/8", "rating":"PROVISIONAL", "reason":"Cross-folio physical recurrence is real, but the analytic q|host cut is fused and the sample is postselected."},
        {"rank":"2", "candidate_id":"G4_EDGE_DY", "formal_candidate":"REUSABLE_RIGHT_EDGE_DY_SEQUENCE", "support":f"{dy}/9 targets", "physical_separator_support":f"{right_sep}/{dy}", "rating":"PROVISIONAL", "reason":"The final sequence recurs on eight folios, but no target contains a delimiter-like mark before it and GDT003 did not beat string baselines."},
        {"rank":"3", "candidate_id":"G4_EDGE_DAR", "formal_candidate":"REUSABLE_RIGHT_EDGE_DAR_SEQUENCE", "support":"1/9 targets", "physical_separator_support":"0/1", "rating":"WEAK", "reason":"One inspected completion is insufficient; qoldar was also a low-ranked folio-held paradigm prediction."},
        {"rank":"4", "candidate_id":"G4_PHYSICAL_SLOTS", "formal_candidate":"AUTHOR_MARKED_INTERNAL_SLOT_BOUNDARIES", "support":"0/9 targets", "physical_separator_support":f"{left_sep + right_sep}/17 applicable cuts", "rating":"FAILED", "reason":"No inspected analytic cut has a distinct physical separator. This does not falsify fused orthographic modules."},
        {"rank":"5", "candidate_id":"G4_UNIQUE_PARSE", "formal_candidate":"UNIQUE_COMPOSITIONAL_FACTORISATION", "support":"0 independently established", "physical_separator_support":"NOT_APPLICABLE", "rating":"WEAK", "reason":"qoldy has multiple GDT003 derivations and the images do not select one formal parse."},
    ]
    write_tsv(HYP, hypotheses, list(hypotheses[0]))

    result = {
        "experiment": "GDT004_EXPLORATORY_MODULE_SHAPE_ATLAS",
        "status": "PASS_POSTSELECTED_PHYSICAL_ATLAS_NO_INDEPENDENT_SLOT_BOUNDARY",
        "exploratory": True,
        "sample": {
            "targets": len(output),
            "physical_folios": len({r["physical_folio"] for r in output}),
            "sections": dict(sorted(Counter(r["section"] for r in output).items())),
            "prepend_q_targets": q,
            "dy_final_targets": dy,
            "distinct_physical_separators_at_applicable_cuts": left_sep + right_sep,
            "applicable_analytic_cuts": 17,
            "alternate_basic_surface_agreement": "9/9 loci; editions are alternate readings, not samples",
        },
        "headline": "The postselected GDT003 completions are real fused physical groups with recurring edge sequences; no inspected analytic cut is independently author-marked.",
        "gdt003_constraint": "NOT DISTINGUISHABLE FROM STRING STATISTICS remains unchanged",
        "holdout": {"f84r_formal_payload_opened": False, "f84r_rows_retained_joined_or_scored": 0},
        "claim_ceiling": "Formal edge-sequence recurrence in a postselected physical sample only; no morpheme, slot, language, meaning, semantic role, plaintext, or translation.",
        "inputs": {str(p.relative_to(ROOT)): sha(p) for p in [SEL, OBS, SRC, STA, PRED, ROOT / "GDT004_EXPLORATORY_MODULE_SHAPE_METHOD.md", ROOT / "build_gdt004_module_shape_atlas.py"]},
        "outputs": {str(p.relative_to(ROOT)): sha(p) for p in [ATLAS, HYP]},
        "external_source": {"manifest_url":"https://collections.library.yale.edu/manifests/2002046", "manifest_sha256":"317d58fd9ea90392a83d9858a91eada3d0b41416a3c835857dc0154bd123a309", "full_image_hashes_recorded_in": SEL.name},
    }
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
