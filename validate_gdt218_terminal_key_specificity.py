#!/usr/bin/env python3
"""Independent validation for GDT218."""

from __future__ import annotations

import csv
import hashlib
import itertools
import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CHECKS: list[str] = []
ORIENTATIONS = {
    "LT_PI": ("TERMINAL", "INITIAL"), "LI_PI": ("INITIAL", "INITIAL"),
    "LT_PT": ("TERMINAL", "TERMINAL"), "LI_PT": ("INITIAL", "TERMINAL"),
}


def check(value: bool, name: str) -> None:
    if not value: raise AssertionError(name)
    CHECKS.append(name)


def sha(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()


def read(name: str) -> list[dict[str, str]]:
    with (ROOT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def edge(value: str, side: str) -> str: return value[-2:] if side == "TERMINAL" else value[:2]


def wj(left: list[str], right: list[str]) -> float:
    a, b = Counter(left), Counter(right); keys = set(a) | set(b)
    denominator = sum(max(a[k], b[k]) for k in keys)
    return sum(min(a[k], b[k]) for k in keys) / denominator if denominator else 0.0


def close(a: float, b: float) -> bool: return abs(a - b) <= 5e-12


def main() -> None:
    result_path = ROOT / "gdt218_result.json"
    result = json.loads(result_path.read_text(encoding="utf-8"))
    panel = read("gdt187_page_inventory.tsv"); inventory = read("gdt217_terminal_key_inventory.tsv")
    scores = read("gdt218_orientation_scores.tsv"); nulls = read("gdt218_orientation_nulls.tsv"); capacity = read("gdt218_untouched_capacity.tsv")
    check(result["experiment"] == "GDT218_TERMINAL_KEY_SPECIFICITY", "experiment")
    check(result["status"] == "PRIMARY_ORIENTATION_UNIQUELY_POSITIVE_MAX4_NOT_SUPPORTED_NO_UNTOUCHED_CAPACITY", "status")
    pages = {row["page"] for row in panel}; meta = {row["page"]: (row["section"], row["currier"], row["hand"], row["physical_folio"]) for row in panel}
    check(len(pages) == 23 and len({x[3] for x in meta.values()}) == 11, "panel_23_11")
    labels, paragraphs = defaultdict(list), defaultdict(list)
    for row in inventory: (labels if row["side"] == "LABEL_FINAL" else paragraphs)[row["page"]].append(row["family_surface"])
    folio_pages = defaultdict(list)
    for page in pages:
        s, c, h, f = meta[page]; folio_pages[(s, c, h, f)].append(page)
    blocks = defaultdict(list)
    for (s, c, h, f), ps in folio_pages.items(): blocks[(s, c, h, len(ps))].append((f, sorted(ps)))
    block_maps = []
    for _, values in sorted((key, value) for key, value in blocks.items() if len(value) >= 2):
        folios = [f for f, _ in values]; by_folio = dict(values); mappings = []
        for perm in itertools.permutations(folios):
            mapping = {}
            for target, source in zip(folios, perm): mapping.update(dict(zip(by_folio[target], by_folio[source])))
            mappings.append(mapping)
        block_maps.append(mappings)
    worlds = []
    for parts in itertools.product(*block_maps):
        mapping = {}
        for part in parts: mapping.update(part)
        worlds.append(mapping)
    check(len(worlds) == 432, "null_432")
    ordered = sorted(pages); identity = {p: p for p in pages}
    def score(mapping, orientation):
        le, pe = ORIENTATIONS[orientation]
        return sum(wj([edge(x, le) for x in labels[mapping[p]]], [edge(x, pe) for x in paragraphs[p]]) for p in ordered) / len(ordered)
    observed = {o: score(identity, o) for o in ORIENTATIONS}; values = {o: [score(world, o) for world in worlds] for o in ORIENTATIONS}
    means = {o: statistics.mean(values[o]) for o in ORIENTATIONS}; sds = {o: statistics.pstdev(values[o]) for o in ORIENTATIONS}
    zs = {o: (observed[o] - means[o]) / sds[o] if sds[o] else 0.0 for o in ORIENTATIONS}
    maxima = [max((values[o][i] - means[o]) / sds[o] if sds[o] else 0.0 for o in ORIENTATIONS) for i in range(432)]
    by_score = {r["orientation"]: r for r in scores}; by_null = {r["orientation"]: r for r in nulls}
    check(set(by_score) == set(ORIENTATIONS) == set(by_null), "four_orientations")
    for o in ORIENTATIONS:
        local = sum(v >= observed[o] - 1e-15 for v in values[o]) / 432; max4 = sum(v >= zs[o] - 1e-15 for v in maxima) / 432
        check(close(float(by_score[o]["effect"]), observed[o] - means[o]), f"effect:{o}")
        check(close(float(by_score[o]["local_exact_p"]), local), f"local:{o}")
        check(close(float(by_score[o]["max_four_p"]), max4), f"max4:{o}")
        check(close(float(by_null[o]["null_min"]), min(values[o])), f"null_min:{o}")
        check(close(float(by_null[o]["null_max"]), max(values[o])), f"null_max:{o}")
    primary = by_score["LT_PI"]
    check(all(float(by_score[o]["effect"]) <= 0 for o in ORIENTATIONS if o != "LT_PI"), "primary_only_positive")
    check(float(primary["max_four_p"]) > .05, "max4_not_supported")
    check(all(str(result["primary"][key]) == value for key, value in primary.items()), "primary_exact")
    check(result["orientation_specific"] is True and result["primary_max_four_supported"] is False, "result_flags")
    check(len(capacity) == 1 and capacity[0]["page"] == "f76r", "one_untouched_page")
    check(capacity[0]["label_loci"] == "9" and capacity[0]["paragraph_start_loci"] == "2", "f76_counts")
    check(capacity[0]["minimum_label_family_length"] == capacity[0]["maximum_label_family_length"] == "1", "f76_single_family")
    check(capacity[0]["two_family_eligible_label_loci"] == "0" and capacity[0]["capacity_status"] == "NO_TWO_FAMILY_LABEL_CAPACITY", "f76_ineligible")
    check(capacity[0]["paragraph_family_payload_opened"] == "0", "paragraph_payload_sealed")
    check(result["counts"] == {"pages": 23, "physical_folios": 11, "orientations": 4, "null_worlds": 432, "positive_control_orientations": 0, "untouched_candidate_pages": 1, "untouched_eligible_pages": 0}, "counts")
    check(result["next_route"] == "NEW_SOURCE_BOUND_TWO_FAMILY_LABEL_AND_PARAGRAPH_DATA_REQUIRED", "next_route")
    check(result["f84r"] == {"accessed": False, "input": False, "output": False}, "f84r")
    for group in ("inputs_sha256", "selected_source_inputs_sha256", "outputs_sha256", "documents_sha256"):
        for name, digest in result[group].items():
            path = ROOT / name
            if not path.exists(): path = ROOT / "experiments/semantic_assumptions/results" / name
            check(sha(path) == digest, f"hash:{group}:{name}")
    check(sha(ROOT / "run_gdt218_terminal_key_specificity.py") == result["implementation_sha256"], "implementation_hash")
    check(sha(Path(__file__)) == result["validator_sha256"], "validator_hash")
    payload = dict(result); observed_hash = payload.pop("content_sha256")
    check(hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest() == observed_hash, "content_hash")
    validation = {"experiment": result["experiment"], "status": "PASS", "checks_passed": len(CHECKS), "checks": CHECKS, "result_sha256": sha(result_path), "validator_sha256": sha(Path(__file__))}
    (ROOT / "gdt218_validation.json").write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"PASS {len(CHECKS)}/{len(CHECKS)}")


if __name__ == "__main__": main()
