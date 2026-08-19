#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
EXP = ROOT / "experiments/yolo/gdt349_zodiac_facing_orientation_acquisition"
SEL = EXP / "artifacts/gdt349_selection.tsv"
OBS = EXP / "artifacts/gdt349_observations.tsv"
RES = EXP / "artifacts/gdt349_result.json"
OUT = EXP / "artifacts/gdt349_validation.json"

HUMAN = {
    "STOLFI_BEST_0396": "PROFILE_LEFT", "STOLFI_BEST_0399": "PROFILE_LEFT",
    "STOLFI_BEST_0402": "PROFILE_RIGHT", "STOLFI_BEST_0405": "PROFILE_LEFT",
    "STOLFI_BEST_0408": "PROFILE_LEFT", "STOLFI_BEST_0411": "PROFILE_LEFT",
    "STOLFI_BEST_0414": "PROFILE_LEFT", "STOLFI_BEST_0417": "PROFILE_LEFT",
    "STOLFI_BEST_0420": "PROFILE_LEFT", "STOLFI_BEST_0423": "PROFILE_LEFT",
    "STOLFI_BEST_0628": "PROFILE_LEFT",
}

CANVAS = {
    "f70v2": ("1006200", "062ff6a9f14d0c16eb12dc8f6dc480771b7c19746ebdb20302b998e66181ccea"),
    "f71r": ("1006202", "6405841a75a8fa24dd9e5c93ad090ee56bf26c77757f3b1634487e27b509e61b"),
    "f71v": ("1006203", "45f7caf4b58744fdcd4928887661b56a135538a5a40a24fea6ca6c5239898269"),
    "f72r1": ("1006203", "45f7caf4b58744fdcd4928887661b56a135538a5a40a24fea6ca6c5239898269"),
    "f72r2": ("1006203", "45f7caf4b58744fdcd4928887661b56a135538a5a40a24fea6ca6c5239898269"),
    "f72r3": ("1006203", "45f7caf4b58744fdcd4928887661b56a135538a5a40a24fea6ca6c5239898269"),
    "f72v1": ("1006205", "c0ac0dbc3e4b4a6eb2b8edf26dc762a7f9bf26ac9c385fa6bdc770725622b1e7"),
    "f72v2": ("1006204", "2552b2eafb7948d182e52ec49e96a5d92a774917924aea594fb1ac3af3bfcdc5"),
    "f72v3": ("1006204", "2552b2eafb7948d182e52ec49e96a5d92a774917924aea594fb1ac3af3bfcdc5"),
    "f73r": ("1006206", "5bc8e07dbd61cc1f218cfc4449cd527be118aa7884878ec4c8e568e9c2d89bad"),
    "f73v": ("1006207", "4227e5261bb5986e605ddb4f58fa1526640955d778c06916a1c34734bb431141"),
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def content_hash(obj: dict) -> str:
    bare = dict(obj); bare.pop("content_sha256", None)
    return hashlib.sha256(json.dumps(bare, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main() -> None:
    with SEL.open(encoding="utf-8", newline="") as f: sel = list(csv.DictReader(f, delimiter="\t"))
    with OBS.open(encoding="utf-8", newline="") as f: obs = list(csv.DictReader(f, delimiter="\t"))
    result = json.loads(RES.read_text(encoding="utf-8"))
    checks = []
    def ck(name: str, cond: bool) -> None:
        assert cond, name; checks.append(name)

    ck("selection_235", len(sel) == 235)
    ck("observations_235", len(obs) == 235)
    ck("selection_observation_keys_equal", [r["target_id"] for r in sel] == [r["target_id"] for r in obs])
    ck("unique_targets", len({r["target_id"] for r in obs}) == 235)
    ck("no_f84_rows", not any(r["page"].lower().startswith("f84") or r["current_locus"].lower().startswith("f84") for r in obs))
    ck("four_folios", {r["physical_folio"] for r in obs} == {"f70", "f71", "f72", "f73"})
    ck("eleven_pages", len({r["page"] for r in obs}) == 11)
    ck("twenty_one_rings", len({(r["page"], r["ring_scope"]) for r in obs}) == 21)
    ck("allowed_states", {r["review_state"] for r in obs} <= {"PROFILE_LEFT", "PROFILE_RIGHT", "FRONTAL_OR_NON_DIRECTIONAL", "UNCERTAIN"})
    ck("human_ids_exact", {r["source_record_id"] for r in obs if r["review_provenance"] == "EXISTING_HUMAN_ANNOTATION"} == set(HUMAN))
    ck("human_states_exact", all(r["review_state"] == HUMAN[r["source_record_id"]] for r in obs if r["source_record_id"] in HUMAN))
    ck("ai_rows_exact", sum(r["review_provenance"] == "AI_DIRECT_VISUAL_OBSERVATION" for r in obs) == 224)
    ck("ai_state_nondirectional", all(r["review_state"] == "FRONTAL_OR_NON_DIRECTIONAL" for r in obs if r["review_provenance"] == "AI_DIRECT_VISUAL_OBSERVATION"))
    ck("official_urls", all(r["official_image_url"] == f"https://collections.library.yale.edu/iiif/2/{r['official_canvas_id']}/full/full/0/default.jpg" for r in obs))
    ck("canvas_and_image_hash_exact", all((r["official_canvas_id"], r["official_image_sha256"]) == CANVAS[r["page"]] for r in obs))
    ck("review_scope_exact", all(r["review_scope"] == "OFFICIAL_FULL_CANVAS_PLUS_CLOCK_POSITION_CROP" for r in obs))

    counts = Counter(r["review_state"] for r in obs)
    ck("state_counts", counts == Counter({"FRONTAL_OR_NON_DIRECTIONAL": 224, "PROFILE_LEFT": 10, "PROFILE_RIGHT": 1}))
    by_state = defaultdict(set)
    strata = defaultdict(set)
    for r in obs:
        by_state[r["review_state"]].add(r["physical_folio"])
        strata[(r["page"], r["ring_scope"])].add(r["review_state"])
    mixed = sorted(f"{p}:{ring}" for (p, ring), states in strata.items() if {"PROFILE_LEFT", "PROFILE_RIGHT"}.issubset(states))
    ck("one_mixed_stratum", mixed == ["f70v2:INNER"])
    ck("left_two_folios", by_state["PROFILE_LEFT"] == {"f70", "f72"})
    ck("right_one_folio", by_state["PROFILE_RIGHT"] == {"f70"})
    ck("result_counts", result["state_counts"] == dict(sorted(counts.items())))
    ck("result_mixed", result["mixed_page_ring_strata"] == mixed)
    ck("result_status", result["status"] == "STOP_NO_TRANSFERABLE_DIRECTIONAL_PROFILE_CAPACITY")
    ck("gates_fail", not result["all_capacity_gates_pass"] and not result["capacity_gates"]["minimum_12_profile_left"] and not result["capacity_gates"]["minimum_12_profile_right"])
    ck("no_formal_open", result["formal_payload_opened_or_joined"] is False and result["formal_score_run"] is False)
    ck("access_disclosure", result["access_disclosure"]["unrelated_preexisting_f84_result_line_displayed_by_broad_repository_search"] is True and result["access_disclosure"]["f84_used_for_selection_observation_or_score"] is False)
    ck("observation_hash", result["outputs"][str(OBS.relative_to(ROOT))] == sha(OBS))
    for rel, expected in result["inputs"].items(): ck("input_hash_" + Path(rel).name, sha(ROOT / rel) == expected)
    ck("content_hash", result["content_sha256"] == content_hash(result))

    validation = {
        "experiment": "GDT349_ZODIAC_FACING_ORIENTATION_RESULT_VALIDATION",
        "status": "PASS_INTEGRITY_AND_ACCOUNTING_NOT_INDEPENDENT_VISUAL_REVIEW",
        "check_count": len(checks),
        "checks": checks,
        "result_sha256": sha(RES),
        "observation_sha256": sha(OBS),
        "scope": "Independently reconstructs panel joins, provenance partition, counts, gates, hashes, and stop decision; does not duplicate the native visual judgments.",
    }
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
