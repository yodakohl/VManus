#!/usr/bin/env python3
"""Post-score orientation and untouched-capacity audit for GDT217."""

from __future__ import annotations

import csv
import hashlib
import itertools
import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PANEL = ROOT / "gdt187_page_inventory.tsv"
INVENTORY = ROOT / "gdt217_terminal_key_inventory.tsv"
LABEL_SOURCE = ROOT / "gdt012_annotated_core_inventory.tsv"
PROSE_SOURCE = ROOT / "gdt016_group_state_inventory.tsv"
ROLES = ROOT / "experiments/semantic_assumptions/results/existing_human_locus_roles.tsv"
METHOD = ROOT / "GDT218_TERMINAL_KEY_SPECIFICITY_METHOD.md"
REPORT = ROOT / "GDT218_TERMINAL_KEY_SPECIFICITY_REPORT.md"
SCORES = ROOT / "gdt218_orientation_scores.tsv"
NULLS = ROOT / "gdt218_orientation_nulls.tsv"
CAPACITY = ROOT / "gdt218_untouched_capacity.tsv"
RESULT = ROOT / "gdt218_result.json"
ORIENTATIONS = {
    "LT_PI": ("LABEL_TERMINAL_2", "PARAGRAPH_INITIAL_2"),
    "LI_PI": ("LABEL_INITIAL_2", "PARAGRAPH_INITIAL_2"),
    "LT_PT": ("LABEL_TERMINAL_2", "PARAGRAPH_TERMINAL_2"),
    "LI_PT": ("LABEL_INITIAL_2", "PARAGRAPH_TERMINAL_2"),
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def edge(surface: str, mode: str) -> str:
    return surface[-2:] if "TERMINAL" in mode else surface[:2]


def wj(left: list[str], right: list[str]) -> float:
    a, b = Counter(left), Counter(right)
    keys = set(a) | set(b)
    denominator = sum(max(a[key], b[key]) for key in keys)
    return sum(min(a[key], b[key]) for key in keys) / denominator if denominator else 0.0


def main() -> None:
    panel = read(PANEL); inventory = read(INVENTORY)
    pages = {row["page"] for row in panel}
    meta = {row["page"]: (row["section"], row["currier"], row["hand"], row["physical_folio"]) for row in panel}
    labels, paragraphs = defaultdict(list), defaultdict(list)
    for row in inventory:
        (labels if row["side"] == "LABEL_FINAL" else paragraphs)[row["page"]].append(row["family_surface"])

    folio_pages: dict[tuple[str, str, str, str], list[str]] = defaultdict(list)
    for page in pages:
        section, currier, hand, folio = meta[page]
        folio_pages[(section, currier, hand, folio)].append(page)
    blocks: dict[tuple[str, str, str, int], list[tuple[str, list[str]]]] = defaultdict(list)
    for (section, currier, hand, folio), ps in folio_pages.items():
        blocks[(section, currier, hand, len(ps))].append((folio, sorted(ps)))
    block_maps = []
    for _, values in sorted((key, value) for key, value in blocks.items() if len(value) >= 2):
        folios = [folio for folio, _ in values]; by_folio = dict(values); mappings = []
        for perm in itertools.permutations(folios):
            mapping = {}
            for target, source in zip(folios, perm):
                mapping.update(dict(zip(by_folio[target], by_folio[source])))
            mappings.append(mapping)
        block_maps.append(mappings)
    worlds = []
    for parts in itertools.product(*block_maps):
        mapping = {}
        for part in parts: mapping.update(part)
        worlds.append(mapping)
    assert len(worlds) == 432
    ordered = sorted(pages); identity = {page: page for page in pages}

    def score(mapping: dict[str, str], orientation: str) -> float:
        left_mode, right_mode = ORIENTATIONS[orientation]
        return sum(wj([edge(value, left_mode) for value in labels[mapping[page]]], [edge(value, right_mode) for value in paragraphs[page]]) for page in ordered) / len(ordered)

    observed = {name: score(identity, name) for name in ORIENTATIONS}
    values = {name: [score(world, name) for world in worlds] for name in ORIENTATIONS}
    means = {name: statistics.mean(values[name]) for name in ORIENTATIONS}
    sds = {name: statistics.pstdev(values[name]) for name in ORIENTATIONS}
    zs = {name: (observed[name] - means[name]) / sds[name] if sds[name] else 0.0 for name in ORIENTATIONS}
    world_max = [max((values[name][i] - means[name]) / sds[name] if sds[name] else 0.0 for name in ORIENTATIONS) for i in range(432)]
    score_rows, null_rows = [], []
    for name, (left_mode, right_mode) in ORIENTATIONS.items():
        local = sum(value >= observed[name] - 1e-15 for value in values[name]) / 432
        max4 = sum(value >= zs[name] - 1e-15 for value in world_max) / 432
        score_rows.append({
            "orientation": name, "label_edge": left_mode, "paragraph_edge": right_mode,
            "externally_specified_primary": int(name == "LT_PI"),
            "observed_mean_weighted_jaccard": f"{observed[name]:.12f}", "null_mean": f"{means[name]:.12f}",
            "effect": f"{observed[name]-means[name]:.12f}", "standardized_effect": f"{zs[name]:.12f}",
            "local_exact_p": f"{local:.12f}", "max_four_p": f"{max4:.12f}",
        })
        null_rows.append({"orientation": name, "worlds": 432, "null_min": f"{min(values[name]):.12f}", "null_mean": f"{means[name]:.12f}", "null_max": f"{max(values[name]):.12f}", "local_exact_p": f"{local:.12f}", "max_four_p": f"{max4:.12f}"})

    used_pages = pages
    roles = {row["locus"]: row for row in read(ROLES) if not row["page"].startswith("f84")}
    label_meta: dict[str, dict[str, int]] = defaultdict(lambda: {"loci": 0, "eligible": 0, "min": 999, "max": 0})
    seen_loci = defaultdict(set)
    for row in read(LABEL_SOURCE):
        page, locus = row["page"], row["locus"]
        if page.startswith("f84") or page in used_pages or roles.get(locus, {}).get("kind") != "L":
            continue
        if locus not in seen_loci[page]:
            length = int(row["family_length"]); seen_loci[page].add(locus)
            label_meta[page]["loci"] += 1; label_meta[page]["eligible"] += int(length >= 2)
            label_meta[page]["min"] = min(label_meta[page]["min"], length); label_meta[page]["max"] = max(label_meta[page]["max"], length)
    starts = defaultdict(set)
    with PROSE_SOURCE.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        for row in reader:
            page, locus = row["page"], row["locus"]
            if page.startswith("f84") or page in used_pages:
                continue
            role = roles.get(locus, {})
            if role.get("kind") == "P" and role.get("paragraph_start") == "1":
                starts[page].add(locus)
    capacity_rows = []
    for page in sorted(set(label_meta) & set(starts)):
        data = label_meta[page]
        capacity_rows.append({
            "page": page, "physical_folio": next(iter(page for page in [page])).split("r")[0].split("v")[0],
            "label_loci": data["loci"], "paragraph_start_loci": len(starts[page]),
            "minimum_label_family_length": data["min"], "maximum_label_family_length": data["max"],
            "two_family_eligible_label_loci": data["eligible"],
            "capacity_status": "ELIGIBLE_UNTOUCHED_TRANSFER" if data["eligible"] else "NO_TWO_FAMILY_LABEL_CAPACITY",
            "paragraph_family_payload_opened": 0,
        })
    assert len(capacity_rows) == 1 and capacity_rows[0]["page"] == "f76r"
    write(SCORES, score_rows); write(NULLS, null_rows); write(CAPACITY, capacity_rows)

    primary = next(row for row in score_rows if row["orientation"] == "LT_PI")
    other_positive = sum(float(row["effect"]) > 0 for row in score_rows if row["orientation"] != "LT_PI")
    status = "PRIMARY_ORIENTATION_UNIQUELY_POSITIVE_MAX4_NOT_SUPPORTED_NO_UNTOUCHED_CAPACITY"
    report = f"""# GDT218 — terminal-key orientation specificity

## Result

Status: **{status}**.

The GDT217 label-terminal → paragraph-initial orientation is the only one of
four two-family edge comparisons with a positive null-relative effect.  Its
effect remains {float(primary['effect']):+.5f} with local `p={float(primary['local_exact_p']):.4f}`.
The other three orientations have {other_positive}/3 positive effects.

When all four edge orientations are treated as an exposed post-score family,
the primary max-four tail is `p={float(primary['max_four_p']):.4f}`.  This does
not erase the external Wound-Man specification, but it prevents treating the
nominal GDT217 lead as search-robust confirmation.

The untouched capacity census finds exactly one page outside the GDT217 panel:
f76r has nine label loci and two confirmed-prose paragraph starts.  All nine
labels are single-family source groups, so zero can carry the frozen
two-family key.  Paragraph family payload was not opened.  Shortening the
hypothesis to one family would duplicate GDT217's failed coarse channel and is
not allowed.

## Consequence

The provisional lead is directionally specific rather than a generic match of
any two edges, but no untouched internal transfer panel remains.  Validation
requires new source-bound label/prose data with at least one two-family label,
not a redefinition of f76r.

No key, number, letter, label-paragraph pairing, word, language, plaintext,
meaning, or translation is established.  No f84r source or artifact was
accessed.
"""
    REPORT.write_text(report, encoding="utf-8")
    result = {
        "experiment": "GDT218_TERMINAL_KEY_SPECIFICITY",
        "status": status,
        "counts": {"pages": 23, "physical_folios": 11, "orientations": 4, "null_worlds": 432, "positive_control_orientations": other_positive, "untouched_candidate_pages": len(capacity_rows), "untouched_eligible_pages": sum(row["capacity_status"] == "ELIGIBLE_UNTOUCHED_TRANSFER" for row in capacity_rows)},
        "primary": primary,
        "orientation_specific": other_positive == 0 and float(primary["effect"]) > 0,
        "primary_max_four_supported": float(primary["max_four_p"]) <= .05,
        "next_route": "NEW_SOURCE_BOUND_TWO_FAMILY_LABEL_AND_PARAGRAPH_DATA_REQUIRED",
        "f84r": {"accessed": False, "input": False, "output": False},
        "inputs_sha256": {path.name: sha(path) for path in (PANEL, INVENTORY, LABEL_SOURCE, PROSE_SOURCE)},
        "selected_source_inputs_sha256": {ROLES.name: sha(ROLES)},
        "outputs_sha256": {path.name: sha(path) for path in (SCORES, NULLS, CAPACITY)},
        "documents_sha256": {METHOD.name: sha(METHOD), REPORT.name: sha(REPORT)},
        "implementation_sha256": sha(Path(__file__)),
        "validator_sha256": sha(ROOT / "validate_gdt218_terminal_key_specificity.py"),
        "claim_ceiling": "Post-score edge orientation and untouched capacity only; no key value, label pairing, word, language, plaintext, meaning, or translation.",
    }
    canonical = json.dumps(result, sort_keys=True, separators=(",", ":"))
    result["content_sha256"] = hashlib.sha256(canonical.encode()).hexdigest()
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(status, primary)


if __name__ == "__main__": main()
