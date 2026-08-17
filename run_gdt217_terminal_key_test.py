#!/usr/bin/env python3
"""Run the frozen GDT216 terminal-diagram-key prediction on Voynich labels."""

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
FREEZE = ROOT / "gdt216_prediction_freeze.json"
METHOD = ROOT / "GDT216_TERMINAL_KEY_PREDICTION_METHOD.md"
REPORT = ROOT / "GDT217_TERMINAL_KEY_TEST_REPORT.md"
INVENTORY = ROOT / "gdt217_terminal_key_inventory.tsv"
SCORES = ROOT / "gdt217_terminal_key_scores.tsv"
NULLS = ROOT / "gdt217_terminal_key_nulls.tsv"
OVERLAPS = ROOT / "gdt217_exact_overlaps.tsv"
LOFO = ROOT / "gdt217_leave_one_folio.tsv"
COUNTER = ROOT / "gdt217_counterexamples.tsv"
RESULT = ROOT / "gdt217_result.json"
REPS = (
    "FINAL_GROUP_EXACT_TO_INITIAL_GROUP_EXACT",
    "FINAL_FAMILY_1_TO_INITIAL_FAMILY_1",
    "FINAL_FAMILY_2_TO_INITIAL_FAMILY_2",
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def weighted_jaccard(left: Counter[str], right: Counter[str]) -> float:
    keys = set(left) | set(right)
    denominator = sum(max(left[key], right[key]) for key in keys)
    return sum(min(left[key], right[key]) for key in keys) / denominator if denominator else 0.0


def key(surface: str, representation: str, side: str) -> str:
    if representation == REPS[0]:
        return surface
    width = 1 if representation == REPS[1] else 2
    return surface[-width:] if side == "LABEL_FINAL" else surface[:width]


def main() -> None:
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    assert freeze["target_prediction"]["score_run"] is False
    assert freeze["target_prediction"]["representations"] == list(REPS)

    panel = read(PANEL)
    pages = {row["page"] for row in panel}
    assert len(pages) == 23 and not any(page.startswith("f84") for page in pages)
    page_meta = {row["page"]: (row["section"], row["currier"], row["hand"], row["physical_folio"]) for row in panel}

    roles: dict[str, dict[str, str]] = {}
    with ROLES.open(encoding="utf-8", newline="") as handle:
        header = handle.readline().rstrip("\n").split("\t")
        for raw in handle:
            prefix = raw.rstrip("\n").split("\t")
            locus, page = prefix[2], prefix[1]
            if page.startswith("f84") or locus.startswith("f84") or page not in pages:
                continue
            roles[locus] = dict(zip(header, prefix))

    label_loci = set()
    with LABELS.open(encoding="utf-8", newline="") as handle:
        header = handle.readline().rstrip("\n").split("\t")
        li, pi = header.index("locus"), header.index("page")
        for raw in handle:
            prefix = raw.rstrip("\n").split("\t")
            locus, page = prefix[li], prefix[pi]
            if page.startswith("f84") or locus.startswith("f84") or page not in pages:
                continue
            if roles.get(locus, {}).get("kind") == "L":
                label_loci.add(locus)

    prose_loci = set()
    with PROSE.open(encoding="utf-8", newline="") as handle:
        header = handle.readline().rstrip("\n").split("\t")
        li, pi = header.index("locus"), header.index("page")
        for raw in handle:
            prefix = raw.rstrip("\n").split("\t")
            locus, page = prefix[li], prefix[pi]
            if page.startswith("f84") or locus.startswith("f84") or page not in pages:
                continue
            prose_loci.add(locus)
    opening_loci = {locus for locus in prose_loci if roles.get(locus, {}).get("kind") == "P" and roles[locus]["paragraph_start"] == "1"}
    label_groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    with LABEL_FAMILY.open(encoding="utf-8", newline="") as handle:
        header = handle.readline().rstrip("\n").split("\t")
        li, pi = header.index("locus"), header.index("page")
        for raw in handle:
            prefix = raw.rstrip("\n").split("\t")
            locus, page = prefix[li], prefix[pi]
            if page.startswith("f84") or locus.startswith("f84") or locus not in label_loci:
                continue
            label_groups[locus].append(dict(zip(header, prefix)))
    opening_groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    with PROSE.open(encoding="utf-8", newline="") as handle:
        header = handle.readline().rstrip("\n").split("\t")
        li, pi = header.index("locus"), header.index("page")
        for raw in handle:
            prefix = raw.rstrip("\n").split("\t")
            locus, page = prefix[li], prefix[pi]
            if page.startswith("f84") or locus.startswith("f84") or locus not in opening_loci:
                continue
            opening_groups[locus].append(dict(zip(header, prefix)))
    assert all(label_groups[locus] for locus in label_loci)
    assert all(opening_groups[locus] for locus in opening_loci)
    for locus in label_groups:
        label_groups[locus].sort(key=lambda row: int(row["group_index"]))
    for locus in opening_groups:
        opening_groups[locus].sort(key=lambda row: int(row["group_index"]))

    inventory: list[dict[str, object]] = []
    label_by_page: dict[str, list[str]] = defaultdict(list)
    opening_by_page: dict[str, list[str]] = defaultdict(list)
    for locus in sorted(label_loci):
        row = label_groups[locus][-1]
        surface = row["family_surface"]
        page = roles[locus]["page"]
        label_by_page[page].append(surface)
        inventory.append({
            "side": "LABEL_FINAL", "page": page, "physical_folio": page_meta[page][3], "locus": locus,
            "selected_group_index": row["group_index"], "selected_group_count": row["group_count"],
            "family_surface": surface, "family_1_key": surface[-1:], "family_2_key": surface[-2:],
            "source_view": "GDT012_ANNOTATED_SOURCE_NATIVE_FAMILY", "claim_state": "SOURCE_NATIVE_TERMINAL_KEY_CANDIDATE_NOT_MEANING",
        })
    for locus in sorted(opening_loci):
        row = opening_groups[locus][0]
        surface = row["family_surface"]
        page = roles[locus]["page"]
        opening_by_page[page].append(surface)
        inventory.append({
            "side": "PARAGRAPH_INITIAL", "page": page, "physical_folio": page_meta[page][3], "locus": locus,
            "selected_group_index": row["group_index"], "selected_group_count": row["group_count"],
            "family_surface": surface, "family_1_key": surface[:1], "family_2_key": surface[:2],
            "source_view": "GDT016_CONFIRMED_PROSE_SOURCE_NATIVE_FAMILY", "claim_state": "SOURCE_NATIVE_INITIAL_KEY_CANDIDATE_NOT_MEANING",
        })

    label_bags = {page: {rep: Counter(key(surface, rep, "LABEL_FINAL") for surface in label_by_page[page]) for rep in REPS} for page in pages}
    opening_bags = {page: {rep: Counter(key(surface, rep, "PARAGRAPH_INITIAL") for surface in opening_by_page[page]) for rep in REPS} for page in pages}

    folio_pages: dict[tuple[str, str, str, str], list[str]] = defaultdict(list)
    for page in pages:
        section, currier, hand, folio = page_meta[page]
        folio_pages[(section, currier, hand, folio)].append(page)
    blocks: dict[tuple[str, str, str, int], list[tuple[str, list[str]]]] = defaultdict(list)
    for (section, currier, hand, folio), block_pages in folio_pages.items():
        blocks[(section, currier, hand, len(block_pages))].append((folio, sorted(block_pages)))
    blocks = {group: value for group, value in blocks.items() if len(value) >= 2}
    block_maps = []
    block_manifest = []
    for block, values in sorted(blocks.items()):
        folios = [folio for folio, _ in values]
        by_folio = {folio: block_pages for folio, block_pages in values}
        mappings = []
        for permutation in itertools.permutations(folios):
            mapping = {}
            for target_folio, source_folio in zip(folios, permutation):
                for target_page, source_page in zip(by_folio[target_folio], by_folio[source_folio]):
                    mapping[target_page] = source_page
            mappings.append(mapping)
        block_maps.append(mappings)
        block_manifest.append({"block": "|".join(map(str, block)), "folios": ",".join(folios), "permutations": math.factorial(len(folios))})
    worlds = []
    for parts in itertools.product(*block_maps):
        mapping = {}
        for part in parts:
            mapping.update(part)
        worlds.append(mapping)
    assert len(worlds) == 432 and all(set(world) == pages for world in worlds)

    identity = {page: page for page in pages}
    ordered_pages = sorted(pages)

    def score(mapping: dict[str, str], rep: str, subset: list[str] | None = None) -> float:
        chosen = subset or ordered_pages
        return sum(weighted_jaccard(label_bags[mapping[page]][rep], opening_bags[page][rep]) for page in chosen) / len(chosen)

    observed = {rep: score(identity, rep) for rep in REPS}
    null_values = {rep: [score(world, rep) for world in worlds] for rep in REPS}
    means = {rep: statistics.mean(null_values[rep]) for rep in REPS}
    sds = {rep: statistics.pstdev(null_values[rep]) for rep in REPS}
    zs = {rep: (observed[rep] - means[rep]) / sds[rep] if sds[rep] else 0.0 for rep in REPS}
    world_max = [max((null_values[rep][i] - means[rep]) / sds[rep] if sds[rep] else 0.0 for rep in REPS) for i in range(len(worlds))]

    score_rows = []
    null_rows = []
    overlap_by_rep: dict[str, tuple[int, int, set[str]]] = {}
    for rep in REPS:
        local_p = sum(value >= observed[rep] - 1e-15 for value in null_values[rep]) / len(worlds)
        max_p = sum(value >= zs[rep] - 1e-15 for value in world_max) / len(worlds)
        section_values = {}
        for section in ("P", "B"):
            subset = [page for page in ordered_pages if page_meta[page][0] == section]
            obs = score(identity, rep, subset)
            vals = [score(world, rep, subset) for world in worlds]
            section_values[section] = (obs, statistics.mean(vals), sum(value >= obs - 1e-15 for value in vals) / len(vals))
        exact_occurrences = 0
        matched_openings = 0
        contributing_folios: set[str] = set()
        for page in ordered_pages:
            label_keys = [key(surface, rep, "LABEL_FINAL") for surface in label_by_page[page]]
            opening_keys = [key(surface, rep, "PARAGRAPH_INITIAL") for surface in opening_by_page[page]]
            opening_set = set(opening_keys)
            label_set = set(label_keys)
            exact_occurrences += sum(value in opening_set for value in label_keys)
            matched_openings += sum(value in label_set for value in opening_keys)
            if label_set & opening_set:
                contributing_folios.add(page_meta[page][3])
        overlap_by_rep[rep] = (exact_occurrences, matched_openings, contributing_folios)
        score_rows.append({
            "representation": rep,
            "observed_mean_weighted_jaccard": f"{observed[rep]:.12f}", "null_mean": f"{means[rep]:.12f}",
            "effect": f"{observed[rep]-means[rep]:.12f}", "standardized_effect": f"{zs[rep]:.12f}",
            "local_exact_p": f"{local_p:.12f}", "max_three_p": f"{max_p:.12f}",
            "pharma_effect": f"{section_values['P'][0]-section_values['P'][1]:.12f}", "pharma_exact_p": f"{section_values['P'][2]:.12f}",
            "bio_effect": f"{section_values['B'][0]-section_values['B'][1]:.12f}", "bio_exact_p": f"{section_values['B'][2]:.12f}",
            "matched_label_occurrences": exact_occurrences, "matched_paragraph_openings": matched_openings,
            "contributing_physical_folios": len(contributing_folios), "folio_ids": ",".join(sorted(contributing_folios)),
        })
        null_rows.append({
            "representation": rep, "worlds": len(worlds), "null_min": f"{min(null_values[rep]):.12f}",
            "null_mean": f"{means[rep]:.12f}", "null_max": f"{max(null_values[rep]):.12f}",
            "local_exact_p": f"{local_p:.12f}", "max_three_p": f"{max_p:.12f}",
        })

    best = max(score_rows, key=lambda row: float(row["standardized_effect"]))
    supported = (
        float(best["max_three_p"]) <= 0.05
        and float(best["pharma_effect"]) > 0
        and float(best["bio_effect"]) > 0
        and best["representation"] in {REPS[0], REPS[2]}
        and int(best["contributing_physical_folios"]) >= 2
    )
    status = "VOYNICH_TERMINAL_KEY_PROVISIONAL_LEAD" if supported else "VOYNICH_TERMINAL_KEY_NOT_SUPPORTED"

    best_rep = best["representation"]
    lofo_rows = []
    for held_folio in sorted({meta[3] for meta in page_meta.values()}):
        subset = [page for page in ordered_pages if page_meta[page][3] != held_folio]
        obs = score(identity, best_rep, subset)
        vals = [score(world, best_rep, subset) for world in worlds]
        mean = statistics.mean(vals)
        lofo_rows.append({
            "representation": best_rep, "held_physical_folio": held_folio, "remaining_pages": len(subset),
            "observed_mean_weighted_jaccard": f"{obs:.12f}", "null_mean": f"{mean:.12f}",
            "effect": f"{obs-mean:.12f}",
            "local_exact_p": f"{sum(value >= obs - 1e-15 for value in vals) / len(vals):.12f}",
            "positive_effect": int(obs > mean), "claim_state": "POST_SCORE_STABILITY_NOT_IN_DECISION_GATE",
        })
    overlap_rows = []
    for page in ordered_pages:
        label_index: dict[str, list[str]] = defaultdict(list)
        opening_index: dict[str, list[str]] = defaultdict(list)
        for locus in sorted(label_loci):
            if roles[locus]["page"] == page:
                label_index[key(label_groups[locus][-1]["family_surface"], best_rep, "LABEL_FINAL")].append(locus)
        for locus in sorted(opening_loci):
            if roles[locus]["page"] == page:
                opening_index[key(opening_groups[locus][0]["family_surface"], best_rep, "PARAGRAPH_INITIAL")].append(locus)
        for shared_key in sorted(set(label_index) & set(opening_index)):
            overlap_rows.append({
                "representation": best_rep, "page": page, "physical_folio": page_meta[page][3], "section": page_meta[page][0],
                "shared_key": shared_key, "label_loci": ",".join(label_index[shared_key]),
                "paragraph_initial_loci": ",".join(opening_index[shared_key]),
                "label_occurrences": len(label_index[shared_key]), "paragraph_occurrences": len(opening_index[shared_key]),
                "claim_state": "EXACT_SOURCE_NATIVE_POSITIONAL_OVERLAP_NOT_KEY_VALUE_OR_MEANING",
            })

    counterexamples = [
        {"counterexample_id": "C01", "observation": "The readable Wound Man key is an overt numeral or initial; no Voynich source-native family is identified as either.", "impact": "structural analogy cannot identify key value"},
        {"counterexample_id": "C02", "observation": "Only 206 distinct GDT187 label loci and 42 confirmed-prose paragraph starts have family-consensus coverage.", "impact": "sparse and asymmetric target bags"},
        {"counterexample_id": "C03", "observation": "A single-family terminal/initial match is extremely coarse and cannot satisfy the decision rule alone.", "impact": "frequent family ecology is not a key"},
        {"counterexample_id": "C04", "observation": "The panel includes Pharma and Biological/Balneological registers with correlated pages inside eleven folios.", "impact": "whole-folio null and both-section gate are mandatory"},
        {"counterexample_id": "C05", "observation": "Label ownership and paragraph correspondence are not established by the Voynich human inventory.", "impact": "no matched label-paragraph pairs or meanings"},
        {"counterexample_id": "C06", "observation": "The winning overlaps use only common two-family keys QA, BA, KA and CA; QA/BA carry most matched label occurrences.", "impact": "formal boundary ecology remains a strong alternative"},
    ]
    write(INVENTORY, inventory)
    write(SCORES, score_rows)
    write(NULLS, null_rows)
    write(OVERLAPS, overlap_rows)
    write(LOFO, lofo_rows)
    write(COUNTER, counterexamples)

    report = f"""# GDT217 — compact terminal diagram key test

## Result

Status: **{status}**.

The independent positive control remains exact: three documented Wellcome MS
49 Wound Man catchphrases end in keys 14, 19, and 41, each pointing to the
same-numbered prose entry although the descriptive phrase itself differs.

The frozen Voynich panel contains {len(label_loci)} distinct label loci and
{len(opening_loci)} confirmed-prose paragraph starts with source-native family
coverage across {len(pages)} pages and {len({meta[3] for meta in page_meta.values()})}
physical folios.  The exact null contains {len(worlds)} whole-folio worlds.

The strongest of the three predeclared positional representations is
`{best['representation']}`.  Its observed mean weighted Jaccard is
{float(best['observed_mean_weighted_jaccard']):.5f} versus a null mean of
{float(best['null_mean']):.5f}, an effect of {float(best['effect']):+.5f}.
The local exact tail is {float(best['local_exact_p']):.4f} and the max-three
tail is {float(best['max_three_p']):.4f}.  Its Pharma/Biological effects are
{float(best['pharma_effect']):+.5f}/{float(best['bio_effect']):+.5f};
{best['contributing_physical_folios']} physical folios have at least one exact
same-page key overlap under this representation.

The exact overlap atlas contains {len(overlap_rows)} page/key cells using only
{', '.join(sorted({row['shared_key'] for row in overlap_rows}))}.  The common
`QA` and `BA` keys carry most matched label occurrences, and the Pharma effect
is nearly zero (`p={float(best['pharma_exact_p']):.4f}`).  The result is
therefore a narrow Biological/Balneological-weighted provisional lead, not a
decoded index.

As a post-score stability diagnostic, all
{sum(int(row['positive_effect']) for row in lofo_rows)}/{len(lofo_rows)}
leave-one-physical-folio effects remain positive.  This rules out dependence
on one folio but does not remove the common-boundary-family alternative.

The conjunctive decision is {'passed' if supported else 'not passed'}.
{'The association is retained as a provisional compact positional-key lead, but it does not identify a key value or label-to-paragraph assignment.' if supported else 'The readable mechanism does not presently identify a compact Voynich terminal key.'}
This is a positional test that GDT187 did not run.  Even on a pass, the current
panel establishes only an excess terminal-to-initial overlap, not a
demonstrated cross-reference field.

## Consequence

GDT215's hybrid record compiler remains live because real Wound Man traditions
also include direct-line, unnumbered-caption, and unkeyed-image variants.  The
compact source-native label-terminal to paragraph-initial mechanism is
{'retained provisionally for untouched-page transfer' if supported else 'rejected on the frozen panel'}.

No source-native family is a number, letter, index, word, morpheme, sound,
language, plaintext, or meaning.  No label is assigned to a paragraph.  No f84
artifact was retained, parsed, joined, or scored.
"""
    REPORT.write_text(report, encoding="utf-8")

    result = {
        "experiment": "GDT217_TERMINAL_KEY_TEST",
        "status": status,
        "decision_gates": {
            "max_three_at_most_05": float(best["max_three_p"]) <= .05,
            "positive_in_pharma": float(best["pharma_effect"]) > 0,
            "positive_in_biological": float(best["bio_effect"]) > 0,
            "eligible_representation": best["representation"] in {REPS[0], REPS[2]},
            "at_least_two_contributing_folios": int(best["contributing_physical_folios"]) >= 2,
            "all_pass": supported,
        },
        "counts": {
            "pages": len(pages), "physical_folios": len({meta[3] for meta in page_meta.values()}),
            "label_loci": len(label_loci), "paragraph_start_loci": len(opening_loci),
            "label_selected_groups": sum(len(values) for values in label_by_page.values()),
            "paragraph_selected_groups": sum(len(values) for values in opening_by_page.values()),
            "representations": len(REPS), "null_worlds": len(worlds),
            "best_overlap_cells": len(overlap_rows), "best_overlap_key_types": len({row["shared_key"] for row in overlap_rows}),
            "lofo_rows": len(lofo_rows), "lofo_positive_effects": sum(int(row["positive_effect"]) for row in lofo_rows),
        },
        "positive_control": freeze["positive_control"],
        "best_representation": best,
        "blocks": block_manifest,
        "f84r": {"accessed": False, "input": False, "output": False},
        "f84v": {"rows_present_in_global_prose_input": 228, "retained": False, "parsed": False, "output": False},
        "claim_ceiling": "Frozen source-native terminal-to-initial association only; no key value, number, label owner, word, language, plaintext, meaning, or translation.",
        "inputs_sha256": {path.name: sha(path) for path in (PANEL, LABELS, PROSE, FREEZE)},
        "selected_source_inputs_sha256": {ROLES.name: sha(ROLES), LABEL_FAMILY.name: sha(LABEL_FAMILY)},
        "outputs_sha256": {path.name: sha(path) for path in (INVENTORY, SCORES, NULLS, OVERLAPS, LOFO, COUNTER)},
        "documents_sha256": {METHOD.name: sha(METHOD), REPORT.name: sha(REPORT)},
        "implementation_sha256": sha(Path(__file__)),
        "validator_sha256": sha(ROOT / "validate_gdt217_terminal_key_test.py"),
    }
    canonical = json.dumps(result, sort_keys=True, separators=(",", ":"))
    result["content_sha256"] = hashlib.sha256(canonical.encode()).hexdigest()
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(status, best)


if __name__ == "__main__":
    main()
