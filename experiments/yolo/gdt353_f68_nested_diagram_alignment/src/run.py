#!/usr/bin/env python3
"""Run GDT353's exact eight-cycle alignment test."""
from __future__ import annotations

import csv
import hashlib
import itertools
import json
import sys
from collections import defaultdict
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from tools.vmanus_experiment import GuardedTSV  # noqa: E402

EXP = ROOT / "experiments/yolo/gdt353_f68_nested_diagram_alignment"
ART = EXP / "artifacts"
ALIGN = ROOT / "experiments/semantic_assumptions/results/source_sta_group_alignment.tsv"
SPECIAL = ROOT / "experiments/semantic_assumptions/results/special_circle_text_blind_array_inventory.tsv"
A = [f"f68v1.{i}" for i in range(3, 11)]
B = ["f68v2.18", "f68v2.7", "f68v2.9", "f68v2.10", "f68v2.12", "f68v2.13", "f68v2.15", "f68v2.16"]


def stable(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def trigrams(value: str) -> set[str]:
    marked = "^" + value + "$"
    return {marked[i:i + 3] for i in range(len(marked) - 2)}


def similarity(left: str, right: str, metric: str) -> float:
    if metric == "EDIT":
        return SequenceMatcher(None, left, right).ratio()
    a, b = trigrams(left), trigrams(right)
    return len(a & b) / len(a | b) if a | b else 1.0


def dihedral(order: tuple[int, ...]):
    for reflected in (0, 1):
        seq = list(reversed(order)) if reflected else list(order)
        for rotation in range(8):
            yield reflected, rotation, tuple(seq[rotation:] + seq[:rotation])


def exact_score(left: list[str], right: list[str], metric: str):
    matrix = [[similarity(a, b, metric) for b in right] for a in left]
    def score(order): return sum(matrix[i][order[i]] for i in range(8)) / 8
    direct = score(tuple(range(8)))
    best = max((score(order), reflected, rotation, order) for reflected, rotation, order in dihedral(tuple(range(8))))
    null = []
    for perm in itertools.permutations(range(8)):
        null.append(max(score(order) for _, _, order in dihedral(perm)))
    p = sum(value >= best[0] - 1e-15 for value in null) / len(null)
    return direct, best, p


def pearson(left: list[int], right: list[int]) -> float:
    ml, mr = sum(left) / 8, sum(right) / 8
    num = sum((a - ml) * (b - mr) for a, b in zip(left, right))
    den = (sum((a - ml) ** 2 for a in left) * sum((b - mr) ** 2 for b in right)) ** 0.5
    return num / den if den else 0.0


def length_score(left: list[int], right: list[int]):
    direct = pearson(left, right)
    best = max((pearson(left, [right[j] for j in order]), reflected, rotation, order) for reflected, rotation, order in dihedral(tuple(range(8))))
    null = []
    for perm in itertools.permutations(range(8)):
        null.append(max(pearson(left, [right[j] for j in order]) for _, _, order in dihedral(perm)))
    return direct, best, sum(value >= best[0] - 1e-15 for value in null) / len(null)


def main() -> None:
    ART.mkdir(parents=True, exist_ok=True)
    special_guard = GuardedTSV(SPECIAL, selector_column="page", allowed_values={"f68v2"})
    special = list(special_guard)
    observed_b = [r["locus"] for r in special if r["unit"] == "E1"]
    assert observed_b == B
    allowed = set(A + B)
    align_guard = GuardedTSV(ALIGN, selector_column="locus", allowed_values=allowed)
    rows = list(align_guard)
    assert {r["locus"] for r in rows} == allowed

    arrays = []
    for name, loci in (("F68V1_E1", A), ("F68V2_E1", B)):
        for ordinal, locus in enumerate(loci, 1):
            arrays.append({"array": name, "ordinal": ordinal, "locus": locus, "direction": "CLOCKWISE", "start_basis": "DOUBLE_RADIAL_STROKE_10H" if name == "F68V1_E1" else "FIRST_STAR_POINT_11H30"})
    arrays_path = ART / "gdt353_arrays.tsv"
    write_tsv(arrays_path, arrays)

    scores = []
    cached_zl_surface = None
    for edition in ("ZL3b", "IT2a", "RF1b"):
        by_locus = defaultdict(list)
        for row in rows:
            if row["edition"] == edition:
                by_locus[row["locus"]].append(row)
        for field, representation in (("nearest_basic_eva_primary", "DIPLOMATIC_SURFACE"), ("primary_sta_families", "PRIMARY_STA_FAMILY")):
            left = ["|".join(r[field].replace(" ", "") for r in by_locus[locus]) for locus in A]
            right = ["|".join(r[field].replace(" ", "") for r in by_locus[locus]) for locus in B]
            if edition == "ZL3b" and representation == "DIPLOMATIC_SURFACE": cached_zl_surface = (left, right)
            for metric in ("EDIT", "TRIGRAM_JACCARD"):
                direct, best, p = exact_score(left, right, metric)
                scores.append({"edition": edition, "representation": representation, "metric": metric, "analysis_role": "PREDECLARED", "direct_score": f"{direct:.12f}", "best_score": f"{best[0]:.12f}", "best_reflected": best[1], "best_rotation": best[2], "null_worlds": 40320, "inclusive_p": f"{p:.12f}", "passes_0_05": int(p <= .05)})

    assert cached_zl_surface is not None
    left_len = [sum(len(part) for part in value.split("|")) for value in cached_zl_surface[0]]
    right_len = [sum(len(part) for part in value.split("|")) for value in cached_zl_surface[1]]
    direct, best, p = length_score(left_len, right_len)
    scores.append({"edition": "ZL3b", "representation": "DIPLOMATIC_TITLE_LENGTH", "metric": "PEARSON", "analysis_role": "POSTHOC_SENSITIVITY", "direct_score": f"{direct:.12f}", "best_score": f"{best[0]:.12f}", "best_reflected": best[1], "best_rotation": best[2], "null_worlds": 40320, "inclusive_p": f"{p:.12f}", "passes_0_05": int(p <= .05)})
    scores_path = ART / "gdt353_scores.tsv"
    write_tsv(scores_path, scores)

    predeclared = [r for r in scores if r["analysis_role"] == "PREDECLARED"]
    pass_reps = []
    for representation in {r["representation"] + ":" + r["metric"] for r in predeclared}:
        subset = [r for r in predeclared if r["representation"] + ":" + r["metric"] == representation]
        if all(int(r["passes_0_05"]) for r in subset) and len({(r["best_reflected"], r["best_rotation"]) for r in subset}) == 1:
            pass_reps.append(representation)
    result = {
        "experiment": "GDT353",
        "schema": "GDT353_F68_NESTED_ALIGNMENT_V1",
        "status": "ORDERED_FORMAL_NESTING_SUPPORTED" if pass_reps else "NO_ORDERED_FORMAL_SUPPORT_FOR_F68V1_V2_NESTING",
        "exposure": "POST_EXPOSURE_EXPLORATORY",
        "counts": {"arrays": 2, "titles_per_array": 8, "alternate_readings": 3, "predeclared_scores": 12, "posthoc_scores": 1, "null_worlds_per_score": 40320, "passing_representations": len(pass_reps)},
        "decision": "No representation passes in all readings with a shared dihedral mapping.",
        "source_access": {"images_opened": False, "f84_rows_parsed_retained_displayed_joined_or_scored": False, "guard_stats": {"special": special_guard.stats.__dict__, "alignment": align_guard.stats.__dict__}},
        "claim_ceiling": "Ordered formal alignment of two eight-title arrays only; no diagram identity, sector value, language, meaning, plaintext, or translation.",
        "selected_source_content_sha256": hashlib.sha256(stable(rows)).hexdigest(),
        "outputs": {str(path.relative_to(ROOT)): sha(path) for path in (arrays_path, scores_path)},
        "documents": {str(path.relative_to(ROOT)): sha(path) for path in (EXP / "METHOD.md", EXP / "REPORT.md")},
        "implementation": {str(Path(__file__).relative_to(ROOT)): sha(Path(__file__))},
    }
    content = dict(result); result["result_content_sha256"] = hashlib.sha256(stable(content)).hexdigest()
    (ART / "gdt353_result.json").write_bytes(stable(result))


if __name__ == "__main__":
    main()
