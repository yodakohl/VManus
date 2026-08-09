#!/usr/bin/env python3
"""Reclassify retained hard edges against the public y.q/qo prior."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parent
RES = BASE / "results"
INTERLINEAR = RES / "pre_grounding_interlinear.tsv"
IMPACT = RES / "source_separator_formal_impact.json"
METHOD = BASE / "SOURCE_HARD_EDGE_PUBLIC_BOUNDARY_OVERLAP_METHOD.md"
OUT = RES / "source_hard_edge_public_boundary_overlap.json"
REPORT = RES / "source_hard_edge_public_boundary_overlap_report.md"
FROZEN = {
    INTERLINEAR: "8052a51fa37ad467e754be39648336ec4014442dab5e223daab2e77efaba4a43",
    IMPACT: "3db3e606b8e86756adea25a90aaeb4e7e6bce1bb22e66ecd8462ada433a8e797",
}
EDGE_TYPES = (
    "BOUND_D>Q_BARE", "BOUND_D>Q_BOUND_D", "BOUND_D>Q_BOUND_E",
    "BOUND_D>Q_REL_I", "BOUND_E>Q_BARE", "BOUND_E>Q_BOUND_E",
)
READINGS = ("ZL3b", "IT2a", "RF1b")
PUBLIC = "https://agnosticvoynich.files.wordpress.com/2019/06/glyph-combinations-across-word-breaks-in-the-voynich-manuscript-preprint.pdf"
CLAIM = (
    "The source-separated retained hard-edge inventory is real, but its aggregate surface "
    "direction is predominantly the already published y.q/qo word-boundary pattern. The six "
    "role classes are a conditional partition made by the frozen incomplete parser, not an "
    "independently established new syntax. No wordhood, sound, language, cipher, meaning, "
    "plaintext, or translation follows."
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def add(counter: Counter[str], left: str, right: str) -> None:
    counter["edges"] += 1
    counter["left_ends_y"] += left.endswith("y")
    counter["right_starts_q"] += right.startswith("q")
    counter["right_starts_qo"] += right.startswith("qo")
    counter["literal_y_q"] += left.endswith("y") and right.startswith("q")
    counter["literal_y_qo"] += left.endswith("y") and right.startswith("qo")
    counter["literal_dy_or_ey_qo"] += (left.endswith("dy") or left.endswith("ey")) and right.startswith("qo")


def serialize(counter: Counter[str]) -> dict[str, int | float]:
    total = counter["edges"]
    keys = (
        "edges", "left_ends_y", "right_starts_q", "right_starts_qo",
        "literal_y_q", "literal_y_qo", "literal_dy_or_ey_qo",
    )
    result: dict[str, int | float] = {key: counter[key] for key in keys}
    for key in keys[1:]:
        result[f"{key}_fraction"] = counter[key] / total if total else 0.0
    return result


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    for path, expected in FROZEN.items():
        if sha(path) != expected:
            raise SystemExit(f"frozen input mismatch: {path.name}")
    impact = json.loads(IMPACT.read_text(encoding="utf-8"))
    formal = impact["formal_adjacency_correction"]
    if impact["status"] != "PASS_SOURCE_SEPARATOR_FORMAL_IMPACT_CORRECTION":
        raise SystemExit("source-impact status")
    skipped = {
        (item["edition"], item["locus"], item["registered_edge"])
        for item in formal["skipped_registered_edge_examples"]
    }
    if len(skipped) != 6:
        raise SystemExit("skipped-edge inventory")

    all_counts: Counter[str] = Counter()
    direct_counts: Counter[str] = Counter()
    by_type_all: dict[str, Counter[str]] = defaultdict(Counter)
    by_type_direct: dict[str, Counter[str]] = defaultdict(Counter)
    by_reading_all: dict[str, Counter[str]] = defaultdict(Counter)
    by_reading_direct: dict[str, Counter[str]] = defaultdict(Counter)
    last_chars: Counter[str] = Counter()
    first_chunks: Counter[str] = Counter()
    pair_chunks: Counter[str] = Counter()
    seen: set[tuple[str, str, str]] = set()

    with INTERLINEAR.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if len(rows) != 15_960:
        raise SystemExit("interlinear row count")
    for row in rows:
        nodes = [item.split("=", 1)[0] for item in row["formal_interlinear"].split(" | ")] if row["formal_interlinear"] else []
        for edge in filter(None, row["confirmed_edges"].split(";")):
            coordinates, edge_type = edge.split(":", 1)
            left_text, right_text = coordinates.split(">", 1)
            left_index = int(left_text[1:]) - 1
            right_index = int(right_text[1:]) - 1
            if edge_type not in EDGE_TYPES or right_index != left_index + 1 or not (0 <= left_index < right_index < len(nodes)):
                raise SystemExit("edge coordinate/type drift")
            key = (row["edition"], row["locus"], edge)
            if key in seen:
                raise SystemExit("duplicate registered edge")
            seen.add(key)
            left, right = nodes[left_index], nodes[right_index]
            if not left or not right:
                raise SystemExit("empty edge surface")
            add(all_counts, left, right)
            add(by_type_all[edge_type], left, right)
            add(by_reading_all[row["edition"]], left, right)
            last_chars[left[-1]] += 1
            first_chunks[right[:2]] += 1
            pair_chunks[f"{left[-2:]}|{right[:2]}"] += 1
            if key not in skipped:
                add(direct_counts, left, right)
                add(by_type_direct[edge_type], left, right)
                add(by_reading_direct[row["edition"]], left, right)

    expected_original = formal["registered_hard_edge_original_counts"]
    observed_original = {edge: by_type_all[edge]["edges"] for edge in EDGE_TYPES}
    expected_direct = formal["registered_hard_edge_direct_source_counts"]
    observed_direct = {edge: by_type_direct[edge]["edges"] for edge in EDGE_TYPES}
    gates = {
        "exact_15960_interlinear_rows": len(rows) == 15_960,
        "exact_4737_registered_edges": all_counts["edges"] == 4_737,
        "exact_six_skipped_and_4731_direct_edges": len(skipped) == 6 and direct_counts["edges"] == 4_731,
        "edge_type_counts_match_source_impact": observed_original == expected_original,
        "direct_type_counts_match_source_impact": observed_direct == expected_direct,
        "direct_literal_y_q_at_least_85_percent": direct_counts["literal_y_q"] / direct_counts["edges"] >= 0.85,
        "direct_right_qo_at_least_90_percent": direct_counts["right_starts_qo"] / direct_counts["edges"] >= 0.90,
        "all_six_edge_types_majority_literal_y_q": all(by_type_direct[edge]["literal_y_q"] * 2 > by_type_direct[edge]["edges"] for edge in EDGE_TYPES),
        "english_lexical_gloss_assigned": False,
    }
    if not all(value for key, value in gates.items() if key != "english_lexical_gloss_assigned") or gates["english_lexical_gloss_assigned"]:
        raise SystemExit("reclassification gate failure")

    result = {
        "experiment": "SOURCE_HARD_EDGE_PUBLIC_BOUNDARY_OVERLAP_AUDIT",
        "status": "PASS_PUBLIC_Y_Q_DOMINANCE_RECLASSIFICATION",
        "decision": "DEMOTE_HARD_EDGE_NOVELTY_RETAIN_SOURCE_SAFE_CONDITIONAL_ROLE_PARTITION",
        "inputs": {path.name: sha(path) for path in (*FROZEN, METHOD, Path(__file__).resolve())},
        "public_prior": {
            "source": PUBLIC,
            "recorded_findings": [
                "cross-word-break glyph combinations deviate from independence",
                "y.q is a particularly strong published boundary combination",
                "q is regularly connected with following o and can be construed as qo",
            ],
        },
        "all_registered_edges": serialize(all_counts),
        "direct_adjacent_source_group_edges": serialize(direct_counts),
        "by_edge_type_all": {edge: serialize(by_type_all[edge]) for edge in EDGE_TYPES},
        "by_edge_type_direct": {edge: serialize(by_type_direct[edge]) for edge in EDGE_TYPES},
        "by_reading_all": {reading: serialize(by_reading_all[reading]) for reading in READINGS},
        "by_reading_direct": {reading: serialize(by_reading_direct[reading]) for reading in READINGS},
        "surface_inventory": {
            "left_final_character_counts": dict(sorted(last_chars.items())),
            "right_initial_two_character_counts": dict(sorted(first_chunks.items())),
            "left_final_two_to_right_initial_two_counts": dict(sorted(pair_chunks.items())),
        },
        "gates": gates,
        "claim_ceiling": CLAIM,
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    direct = result["direct_adjacent_source_group_edges"]
    REPORT.write_text(f"""# Public word-boundary overlap of retained hard edges

Status: **{result['status']}**

Of all 4,737 frozen retained-parser hard edges, 4,731 directly join adjacent
source groups. In that direct subset, **{direct['literal_y_q']}/4,731
({100 * direct['literal_y_q_fraction']:.2f}%)** are literal `y|q`, **{direct['right_starts_qo']}/4,731
({100 * direct['right_starts_qo_fraction']:.2f}%)** enter `qo...`, and **{direct['literal_dy_or_ey_qo']}/4,731
({100 * direct['literal_dy_or_ey_qo_fraction']:.2f}%)** are specifically `dy|qo` or `ey|qo`.
Every one of the six formal edge classes has a majority literal `y|q` carrier.

This strongly overlaps the 2019 public report of non-independent glyph
combinations across word breaks, especially `y.q`, and its observation that
`q` is regularly joined conceptually with following `o`. The source-separator
correction remains valid, but the aggregate direction is not a newly
discovered syntax. The six D/E-to-q role labels are at most a frozen-parser
partition of this known orthotactic boundary effect; the unavailable partial
parser prevents treating that partition as exhaustive grammar.

Decision: **{result['decision']}**. Preserve the exact source-boundary evidence,
but do not cite the aggregate as novel syntax or semantic progress. No
authorial wordhood, morpheme, sound, language, cipher, meaning, plaintext, or
translation follows.
""", encoding="utf-8")
    print(json.dumps({"status": result["status"], "direct": direct}, sort_keys=True))


if __name__ == "__main__":
    main()
