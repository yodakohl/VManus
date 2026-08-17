#!/usr/bin/env python3
"""Independent source, score, null, and claim validation for GDT217."""

from __future__ import annotations

import csv
import hashlib
import itertools
import json
import math
import statistics
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PANEL = ROOT / "gdt187_page_inventory.tsv"
LABELS = ROOT / "gdt059_hpr2_external_inventory.tsv"
PROSE = ROOT / "gdt016_group_state_inventory.tsv"
LABEL_FAMILY = ROOT / "gdt012_annotated_core_inventory.tsv"
ROLES = ROOT / "experiments/semantic_assumptions/results/existing_human_locus_roles.tsv"
RESULT = ROOT / "gdt217_result.json"
REPS = (
    "FINAL_GROUP_EXACT_TO_INITIAL_GROUP_EXACT",
    "FINAL_FAMILY_1_TO_INITIAL_FAMILY_1",
    "FINAL_FAMILY_2_TO_INITIAL_FAMILY_2",
)
CHECKS: list[str] = []


def check(value: bool, name: str) -> None:
    if not value:
        raise AssertionError(name)
    CHECKS.append(name)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def wj(left: Counter[str], right: Counter[str]) -> float:
    keys = set(left) | set(right)
    denominator = sum(max(left[key], right[key]) for key in keys)
    return sum(min(left[key], right[key]) for key in keys) / denominator if denominator else 0.0


def rep_key(surface: str, rep: str, side: str) -> str:
    if rep == REPS[0]:
        return surface
    width = 1 if rep == REPS[1] else 2
    return surface[-width:] if side == "LABEL_FINAL" else surface[:width]


def close(left: float, right: float) -> bool:
    return abs(left - right) <= 5e-12


def main() -> None:
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    inventory = read(ROOT / "gdt217_terminal_key_inventory.tsv")
    scores = read(ROOT / "gdt217_terminal_key_scores.tsv")
    nulls = read(ROOT / "gdt217_terminal_key_nulls.tsv")
    overlaps = read(ROOT / "gdt217_exact_overlaps.tsv")
    lofo = read(ROOT / "gdt217_leave_one_folio.tsv")
    counter = read(ROOT / "gdt217_counterexamples.tsv")
    panel = read(PANEL)

    check(result["experiment"] == "GDT217_TERMINAL_KEY_TEST", "experiment")
    check(result["status"] in {"VOYNICH_TERMINAL_KEY_PROVISIONAL_LEAD", "VOYNICH_TERMINAL_KEY_NOT_SUPPORTED"}, "status_vocab")
    check(len(panel) == 23 and len({r["physical_folio"] for r in panel}) == 11, "panel_23_11")
    check(not any(r["page"].startswith("f84") for r in panel), "panel_no_f84")
    pages = {row["page"] for row in panel}
    meta = {row["page"]: (row["section"], row["currier"], row["hand"], row["physical_folio"]) for row in panel}

    roles = {r["locus"]: r for r in read(ROLES) if r["page"] in pages and not r["page"].startswith("f84")}
    label_loci = {r["locus"] for r in read(LABELS) if r["page"] in pages and roles.get(r["locus"], {}).get("kind") == "L"}
    prose_rows = [r for r in read(PROSE) if r["page"] in pages and not r["page"].startswith("f84")]
    prose_loci = {r["locus"] for r in prose_rows}
    opening_loci = {locus for locus in prose_loci if roles.get(locus, {}).get("kind") == "P" and roles[locus]["paragraph_start"] == "1"}
    check(len(label_loci) == 206, "source_label_loci_206")
    check(len(opening_loci) == 42, "source_openings_42")

    label_rows: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in read(LABEL_FAMILY):
        if row["locus"] in label_loci:
            label_rows[row["locus"]].append(row)
    opening_rows: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in prose_rows:
        if row["locus"] in opening_loci:
            opening_rows[row["locus"]].append(row)
    check(all(label_rows[locus] for locus in label_loci), "all_labels_covered")
    check(all(opening_rows[locus] for locus in opening_loci), "all_openings_covered")
    for values in label_rows.values():
        values.sort(key=lambda row: int(row["group_index"]))
    for values in opening_rows.values():
        values.sort(key=lambda row: int(row["group_index"]))

    expected = []
    for locus in sorted(label_loci):
        row = label_rows[locus][-1]
        expected.append(("LABEL_FINAL", roles[locus]["page"], locus, row["group_index"], row["group_count"], row["family_surface"]))
    for locus in sorted(opening_loci):
        row = opening_rows[locus][0]
        expected.append(("PARAGRAPH_INITIAL", roles[locus]["page"], locus, row["group_index"], row["group_count"], row["family_surface"]))
    observed = [(r["side"], r["page"], r["locus"], r["selected_group_index"], r["selected_group_count"], r["family_surface"]) for r in inventory]
    check(observed == expected, "inventory_exact_source_rebuild")
    check(len(inventory) == 248, "inventory_248")
    check(all(r["family_1_key"] == (r["family_surface"][-1:] if r["side"] == "LABEL_FINAL" else r["family_surface"][:1]) for r in inventory), "family1_keys")
    check(all(r["family_2_key"] == (r["family_surface"][-2:] if r["side"] == "LABEL_FINAL" else r["family_surface"][:2]) for r in inventory), "family2_keys")

    labels_by_page: dict[str, list[str]] = defaultdict(list)
    openings_by_page: dict[str, list[str]] = defaultdict(list)
    for row in inventory:
        (labels_by_page if row["side"] == "LABEL_FINAL" else openings_by_page)[row["page"]].append(row["family_surface"])
    lb = {p: {rep: Counter(rep_key(v, rep, "LABEL_FINAL") for v in labels_by_page[p]) for rep in REPS} for p in pages}
    ob = {p: {rep: Counter(rep_key(v, rep, "PARAGRAPH_INITIAL") for v in openings_by_page[p]) for rep in REPS} for p in pages}

    folio_pages: dict[tuple[str, str, str, str], list[str]] = defaultdict(list)
    for page in pages:
        section, currier, hand, folio = meta[page]
        folio_pages[(section, currier, hand, folio)].append(page)
    blocks: dict[tuple[str, str, str, int], list[tuple[str, list[str]]]] = defaultdict(list)
    for (section, currier, hand, folio), ps in folio_pages.items():
        blocks[(section, currier, hand, len(ps))].append((folio, sorted(ps)))
    blocks = {key: value for key, value in blocks.items() if len(value) >= 2}
    block_maps = []
    for _, values in sorted(blocks.items()):
        folios = [folio for folio, _ in values]
        by_folio = dict(values)
        mappings = []
        for perm in itertools.permutations(folios):
            mapping = {}
            for target, source in zip(folios, perm):
                mapping.update(dict(zip(by_folio[target], by_folio[source])))
            mappings.append(mapping)
        block_maps.append(mappings)
    worlds = []
    for parts in itertools.product(*block_maps):
        mapping = {}
        for part in parts:
            mapping.update(part)
        worlds.append(mapping)
    check(len(worlds) == 432, "null_worlds_432")
    check(all(set(world) == pages for world in worlds), "null_world_page_complete")
    ordered = sorted(pages)
    identity = {page: page for page in pages}

    def score(mapping: dict[str, str], rep: str, subset: list[str] | None = None) -> float:
        chosen = subset or ordered
        return sum(wj(lb[mapping[p]][rep], ob[p][rep]) for p in chosen) / len(chosen)

    recomputed = {}
    world_stats = {}
    for rep in REPS:
        obs = score(identity, rep)
        values = [score(world, rep) for world in worlds]
        mean = statistics.mean(values)
        sd = statistics.pstdev(values)
        recomputed[rep] = (obs, mean, sd, (obs - mean) / sd if sd else 0.0)
        world_stats[rep] = values
    world_max = [max((world_stats[rep][i] - recomputed[rep][1]) / recomputed[rep][2] if recomputed[rep][2] else 0.0 for rep in REPS) for i in range(432)]
    by_score = {r["representation"]: r for r in scores}
    by_null = {r["representation"]: r for r in nulls}
    check(set(by_score) == set(REPS) and set(by_null) == set(REPS), "three_exact_representations")
    for rep in REPS:
        obs, mean, sd, z = recomputed[rep]
        local = sum(value >= obs - 1e-15 for value in world_stats[rep]) / 432
        maxt = sum(value >= z - 1e-15 for value in world_max) / 432
        check(close(float(by_score[rep]["observed_mean_weighted_jaccard"]), obs), f"score_obs:{rep}")
        check(close(float(by_score[rep]["null_mean"]), mean), f"score_mean:{rep}")
        check(close(float(by_score[rep]["standardized_effect"]), z), f"score_z:{rep}")
        check(close(float(by_score[rep]["local_exact_p"]), local), f"score_local_p:{rep}")
        check(close(float(by_score[rep]["max_three_p"]), maxt), f"score_maxt:{rep}")
        check(close(float(by_null[rep]["null_min"]), min(world_stats[rep])), f"null_min:{rep}")
        check(close(float(by_null[rep]["null_max"]), max(world_stats[rep])), f"null_max:{rep}")

    best = max(scores, key=lambda row: float(row["standardized_effect"]))
    check(all(str(result["best_representation"][key]) == value for key, value in best.items()), "best_row_exact")
    gates = result["decision_gates"]
    expected_pass = all(value for key, value in gates.items() if key != "all_pass")
    check(gates["all_pass"] == expected_pass, "gate_conjunction")
    expected_status = "VOYNICH_TERMINAL_KEY_PROVISIONAL_LEAD" if expected_pass else "VOYNICH_TERMINAL_KEY_NOT_SUPPORTED"
    check(result["status"] == expected_status, "status_from_gates")
    expected_overlap_rows = []
    best_rep = best["representation"]
    for page in ordered:
        li: dict[str, list[str]] = defaultdict(list)
        oi: dict[str, list[str]] = defaultdict(list)
        for row in inventory:
            if row["page"] != page:
                continue
            value = rep_key(row["family_surface"], best_rep, row["side"])
            (li if row["side"] == "LABEL_FINAL" else oi)[value].append(row["locus"])
        for shared in sorted(set(li) & set(oi)):
            expected_overlap_rows.append((page, shared, ",".join(li[shared]), ",".join(oi[shared])))
    observed_overlap_rows = [(r["page"], r["shared_key"], r["label_loci"], r["paragraph_initial_loci"]) for r in overlaps]
    check(observed_overlap_rows == expected_overlap_rows, "overlap_atlas_exact")
    check(len(lofo) == 11, "eleven_lofo_rows")
    for row in lofo:
        subset = [page for page in ordered if meta[page][3] != row["held_physical_folio"]]
        obs = score(identity, best_rep, subset)
        values = [score(world, best_rep, subset) for world in worlds]
        mean = statistics.mean(values)
        check(close(float(row["effect"]), obs - mean), f"lofo_effect:{row['held_physical_folio']}")
        check(int(row["positive_effect"]) == int(obs > mean), f"lofo_sign:{row['held_physical_folio']}")
    check(result["counts"] == {"pages": 23, "physical_folios": 11, "label_loci": 206, "paragraph_start_loci": 42, "label_selected_groups": 206, "paragraph_selected_groups": 42, "representations": 3, "null_worlds": 432, "best_overlap_cells": len(overlaps), "best_overlap_key_types": len({r["shared_key"] for r in overlaps}), "lofo_rows": 11, "lofo_positive_effects": sum(int(r["positive_effect"]) for r in lofo)}, "result_counts")
    check(result["positive_control"] == {"pairs": 3, "exact_terminal_to_initial_matches": 3, "full_phrase_exact_matches_expected": 0}, "positive_control")
    check(len(counter) == 6, "six_counterexamples")
    check(result["f84r"] == {"accessed": False, "input": False, "output": False}, "f84r_flags")
    check(result["f84v"] == {"rows_present_in_global_prose_input": 228, "retained": False, "parsed": False, "output": False}, "f84v_disclosure")
    check(not any(r["page"].startswith("f84") or r["locus"].startswith("f84") for r in inventory), "outputs_no_f84")

    for group in ("inputs_sha256", "selected_source_inputs_sha256", "outputs_sha256", "documents_sha256"):
        for name, digest in result[group].items():
            path = ROOT / name
            if not path.exists():
                path = ROOT / "experiments/semantic_assumptions/results" / name
            check(sha(path) == digest, f"hash:{group}:{name}")
    check(sha(ROOT / "run_gdt217_terminal_key_test.py") == result["implementation_sha256"], "implementation_hash")
    check(sha(Path(__file__)) == result["validator_sha256"], "validator_hash")
    payload = dict(result)
    observed_hash = payload.pop("content_sha256")
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    check(hashlib.sha256(canonical.encode()).hexdigest() == observed_hash, "content_hash")

    validation = {
        "experiment": result["experiment"], "status": "PASS", "checks_passed": len(CHECKS), "checks": CHECKS,
        "result_sha256": sha(RESULT), "validator_sha256": sha(Path(__file__)),
    }
    (ROOT / "gdt217_validation.json").write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"PASS {len(CHECKS)}/{len(CHECKS)}")


if __name__ == "__main__":
    main()
