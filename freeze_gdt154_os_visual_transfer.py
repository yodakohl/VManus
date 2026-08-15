#!/usr/bin/env python3
"""Freeze the exact-os visual transfer before target image access."""
import csv
import hashlib
import json
from pathlib import Path

R = Path(__file__).resolve().parent
HOSTS = R / "gdt062_right_family_inventory.tsv"
SEEDS = R / "gdt089_os_cases.tsv"
PARENT = R / "gdt089_result.json"
METHOD = R / "GDT154_OS_VISUAL_TRANSFER_METHOD.md"
TSV = R / "gdt154_os_visual_predictions.tsv"
OUT = R / "gdt154_prediction.json"


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def csha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()).hexdigest()


def main():
    with SEEDS.open(encoding="utf8", newline="") as handle:
        seeds = list(csv.DictReader(handle, delimiter="\t"))
    seed_pages = {row["locus"].split(".")[0] for row in seeds}
    assert seed_pages == {"f88v", "f100v"}
    selected = []
    with HOSTS.open(encoding="utf8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["page"].startswith("f84"): continue
            if row["section"] != "H" or row["page"] in seed_pages: continue
            if (row["page_host"], row["token"], row["wrapper"], row["right_family"], row["dy_closure"], row["b3"]) != ("os", "chos", "ch", "NONE", "0", "0"): continue
            selected.append(row)
    def folio_number(row): return int("".join(ch for ch in row["physical_folio"] if ch.isdigit()))
    selected.sort(key=lambda row: (folio_number(row), row["page"], row["locus"]))
    assert [(row["locus"], row["page"]) for row in selected] == [("f15r.9", "f15r"), ("f27r.4", "f27r"), ("f29r.4", "f29r"), ("f33r.7", "f33r"), ("f90v2.5", "f90v2")]
    candidate_count = len(selected); selected = selected[:2]
    rows = []
    for index, row in enumerate(selected, 1):
        rows.append({
            "target_id": f"OSVT{index:02d}", "page": row["page"], "physical_folio": row["physical_folio"],
            "locus": row["locus"], "token": row["token"], "page_host": row["page_host"],
            "wrapper": row["wrapper"], "right_family": row["right_family"],
            "dy_closure": row["dy_closure"], "b3": row["b3"],
            "occurrence_scope": "RUNNING_TEXT_PAGE_LEVEL_NO_SINGULAR_OWNERSHIP",
            "predicted_dark_leaf": "POSITIVE", "predicted_light_root": "POSITIVE",
            "predicted_joint_state": "DARK_LEAF_AND_LIGHT_ROOT",
            "image_access_at_freeze": "NOT_OPENED_FOR_GDT154",
            "semantic_status": "FROZEN_EXACT_GLOSS_HYPOTHESIS_ONLY",
        })
    with TSV.open("w", encoding="utf8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)
    result = {
        "schema": "GDT154_OS_VISUAL_TRANSFER_PREDICTION_V1",
        "status": "FROZEN_BEFORE_TARGET_IMAGE_ACCESS",
        "seed_loci": [row["locus"] for row in seeds],
        "target_loci": [row["locus"] for row in rows], "target_pages": [row["page"] for row in rows],
        "eligible_candidates": candidate_count,
        "selection_rule": "HERBAL exact PAGE_HOST=os and token=chos and wrapper=ch with no right/DY/B3, excluding GDT089 seed pages and all f84 pages; retain first two by numeric physical folio",
        "prediction": "Each target page plant set contains a conspicuously dark leaf surface and depicted root interiors visibly lighter than that leaf.",
        "decision_rule": {"two_of_two": "PROVISIONAL_SEMANTIC_LEAD", "one_of_two": "UNSTABLE_LOCAL_ONLY", "zero_of_two_or_component_contradiction": "REJECT_EXACT_GLOSS"},
        "ownership_caveat": "Targets are running-text occurrences with page-level plant association only; no singular label ownership is asserted.",
        "f84r": {key: False for key in ("targeted", "opened", "retained", "joined", "scored")},
        "inputs": {path.name: sha(path) for path in (HOSTS, SEEDS, PARENT)},
        "implementation": {Path(__file__).name: sha(Path(__file__))},
        "outputs": {TSV.name: sha(TSV)}, "documents": {METHOD.name: sha(METHOD)},
        "claim_ceiling": "Frozen page-level exact-gloss test only; no word, morpheme, POS, sound, language, plaintext, plant identity, meaning, or translation.",
    }
    result["content_sha256"] = csha(result)
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf8")
    print(json.dumps({"status": result["status"], "targets": result["target_loci"]}, sort_keys=True))


if __name__ == "__main__": main()
