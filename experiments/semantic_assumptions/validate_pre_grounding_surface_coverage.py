#!/usr/bin/env python3
"""Nonimporting reconstruction of the pre-grounding surface coverage audit."""

from __future__ import annotations

import csv
import hashlib
import io
import json
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
INTERLINEAR = RESULTS / "pre_grounding_interlinear.tsv"
MANIFEST = RESULTS / "pre_grounding_package_manifest.json"
ATLAS = RESULTS / "pre_grounding_surface_residual_atlas.tsv"
AUDIT = RESULTS / "pre_grounding_surface_coverage_audit.json"
OUTPUT = RESULTS / "pre_grounding_surface_coverage_validation.json"
EXPECTED_INTERLINEAR_SHA256 = "8052a51fa37ad467e754be39648336ec4014442dab5e223daab2e77efaba4a43"
EXPECTED_MANIFEST_SHA256 = "3ca036eecf45f7440c792d907ea630290116f82130c71af56494b654bdf0e542"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def node_surfaces(row: dict[str, str]) -> list[str]:
    text = row["formal_interlinear"]
    return [] if not text else [part.partition("=")[0] for part in text.split(" | ")]


def reconstruct_mask(tokens: list[str], target: str) -> list[bool]:
    """Independent forward path-count DP; require one exact token subset."""
    states: dict[int, tuple[int, list[bool]]] = {0: (1, [])}
    for token in tokens:
        next_states: dict[int, tuple[int, list[bool]]] = {}
        for offset, (count, path) in states.items():
            old_count, old_path = next_states.get(offset, (0, []))
            next_states[offset] = (min(2, old_count + count), old_path or (path + [False]))
            if target.startswith(token, offset):
                new_offset = offset + len(token)
                old_count, old_path = next_states.get(new_offset, (0, []))
                next_states[new_offset] = (
                    min(2, old_count + count), old_path or (path + [True])
                )
        states = next_states
    count, path = states.get(len(target), (0, []))
    if count != 1:
        raise AssertionError((tokens, target, count))
    return path


def main() -> None:
    checks = 0
    assert digest(INTERLINEAR) == EXPECTED_INTERLINEAR_SHA256
    checks += 1
    source_rows = rows(INTERLINEAR)
    stored = json.loads(AUDIT.read_text(encoding="utf-8"))

    edition_stats: dict[str, Counter[str]] = defaultdict(Counter)
    scope_counts: Counter[tuple[str, str]] = Counter()
    kind_counts: Counter[tuple[str, str]] = Counter()
    page_sets: dict[str, set[str]] = defaultdict(set)
    token_types: Counter[str] = Counter()
    rebuilt: list[dict[str, object]] = []
    unique = 0
    examples: dict[str, dict[str, object]] = {}

    for row in source_rows:
        tokens = row["surface"].split()
        nodes = node_surfaces(row)
        target = "".join(nodes)
        mask = reconstruct_mask(tokens, target)
        unique += 1
        kept = [token for token, flag in zip(tokens, mask) if flag]
        omitted = [token for token, flag in zip(tokens, mask) if not flag]
        positions = [index for index, flag in enumerate(mask, 1) if not flag]
        assert kept == nodes
        assert len(nodes) == int(row["word_count"])
        assert len(nodes) == (len(row["root_sequence"].split()) if row["root_sequence"] else 0)
        assert len(nodes) == (len(row["role_sequence"].split()) if row["role_sequence"] else 0)

        stats = edition_stats[row["edition"]]
        stats.update({
            "rows": 1,
            "surface_tokens": len(tokens),
            "parsed_nodes": len(nodes),
            "surface_characters": sum(len(value) for value in tokens),
            "parsed_characters": len(target),
        })
        if omitted:
            stats.update({
                "affected_rows": 1,
                "omitted_tokens": len(omitted),
                "omitted_characters": sum(len(value) for value in omitted),
            })
            scope_counts[(row["edition"], row["grammar_scope"])] += 1
            kind_counts[(row["edition"], row["kind"])] += 1
            page_sets[row["edition"]].add(row["page"])
            token_types.update(omitted)
            rebuilt.append({
                "edition": row["edition"],
                "locus": row["locus"],
                "page": row["page"],
                "grammar_scope": row["grammar_scope"],
                "kind": row["kind"],
                "surface_token_count": len(tokens),
                "parsed_node_count": len(nodes),
                "omitted_token_count": len(omitted),
                "omitted_positions_1based": ";".join(str(value) for value in positions),
                "omitted_tokens": " ".join(omitted),
                "position_token_pairs": ";".join(
                    f"{position}:{token}" for position, token in zip(positions, omitted)
                ),
            })
        key = f"{row['edition']}/{row['locus']}"
        if row["locus"] in {"f11v.6", "f18v.8"}:
            examples[key] = {
                "surface": row["surface"],
                "parsed_node_surfaces": nodes,
                "omitted_positions_1based": positions,
                "omitted_tokens": omitted,
            }

    rebuilt.sort(key=lambda item: (str(item["edition"]), str(item["page"]), str(item["locus"])))
    fieldnames = [
        "edition", "locus", "page", "grammar_scope", "kind", "surface_token_count",
        "parsed_node_count", "omitted_token_count", "omitted_positions_1based",
        "omitted_tokens", "position_token_pairs",
    ]
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fieldnames, delimiter="\t", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rebuilt)
    assert stream.getvalue().encode("utf-8") == ATLAS.read_bytes()
    checks += 1

    total = Counter()
    for stats in edition_stats.values():
        total.update(stats)
    assert stored["totals"] == dict(sorted(total.items()))
    checks += 1
    assert stored["by_edition"] == {
        key: dict(sorted(value.items())) for key, value in sorted(edition_stats.items())
    }
    checks += 1

    def nested(values: Counter[tuple[str, str]]) -> dict[str, dict[str, int]]:
        output: dict[str, dict[str, int]] = defaultdict(dict)
        for (edition, category), count in sorted(values.items()):
            output[edition][category] = count
        return dict(output)

    assert stored["affected_rows_by_scope"] == nested(scope_counts)
    checks += 1
    assert stored["affected_rows_by_kind"] == nested(kind_counts)
    checks += 1
    assert stored["affected_pages_by_edition"] == {
        key: len(value) for key, value in sorted(page_sets.items())
    }
    checks += 1
    assert stored["omitted_token_type_counts"] == dict(sorted(token_types.items()))
    checks += 1
    target_relevance = {
        "f2r_15_has_surface_residual": any(item["locus"] == "f2r.15" for item in rebuilt),
        "omitted_token_occurrences_containing_i_or_o": sum(
            count for token, count in token_types.items() if "i" in token or "o" in token
        ),
        "col001_frozen_formal_counts_changed_by_residual_inventory": False,
    }
    assert stored["target_relevance"] == target_relevance == {
        "f2r_15_has_surface_residual": False,
        "omitted_token_occurrences_containing_i_or_o": 0,
        "col001_frozen_formal_counts_changed_by_residual_inventory": False,
    }
    checks += 1
    assert digest(MANIFEST) == EXPECTED_MANIFEST_SHA256
    assert stored["inputs"] == {
        "experiments/semantic_assumptions/results/pre_grounding_interlinear.tsv": EXPECTED_INTERLINEAR_SHA256,
        "experiments/semantic_assumptions/results/pre_grounding_package_manifest.json": EXPECTED_MANIFEST_SHA256,
    }
    checks += 2
    assert stored["claim_ceiling"] == (
        "The frozen package is complete for loci and literal surface, but its formal/root/role "
        "layer covers only the retained parser nodes. Omitted groups remain literal "
        "UNPARSED_SURFACE with no assigned structural role or lexical meaning."
    )
    checks += 1
    assert stored["examples"] == dict(sorted(examples.items()))
    checks += 1
    assert stored["most_common_omitted_tokens"] == [
        {"token": token, "count": count} for token, count in token_types.most_common(20)
    ]
    checks += 1
    assert stored["residual_atlas"] == {
        "path": "experiments/semantic_assumptions/results/pre_grounding_surface_residual_atlas.tsv",
        "rows": len(rebuilt),
        "sha256": digest(ATLAS),
    }
    checks += 1
    assert stored["alignment"] == {
        "method": "unique whole-surface-token subsequence preserving order",
        "all_rows_unique": True,
        "rows_checked": unique,
        "insertions_or_replacements": 0,
    }
    checks += 1
    assert stored["status"] == "PASS_COMPLETE_SURFACE_PARTIAL_FORMAL_COVERAGE"
    assert stored["decision"] == "CORRECT_PRE_GROUNDING_COMPLETENESS_CLAIM"
    assert stored["english_lexical_glosses"] == 0
    checks += 3
    assert stored["totals"] == {
        "affected_rows": 2833,
        "omitted_characters": 5237,
        "omitted_tokens": 3838,
        "parsed_characters": 568072,
        "parsed_nodes": 114173,
        "rows": 15960,
        "surface_characters": 573309,
        "surface_tokens": 118011,
    }
    checks += 1
    assert stored["by_edition"]["ZL3b"]["omitted_tokens"] == 817
    assert stored["by_edition"]["IT2a"]["omitted_tokens"] == 599
    assert stored["by_edition"]["RF1b"]["omitted_tokens"] == 2422
    checks += 3
    assert stored["omitted_token_type_counts"]["y"] == 2463
    assert stored["omitted_token_type_counts"]["dy"] == 774
    assert stored["omitted_token_type_counts"]["ddy"] == 6
    checks += 3
    for key in ("ZL3b/f11v.6", "IT2a/f11v.6", "RF1b/f11v.6"):
        assert "ddy" in stored["examples"][key]["omitted_tokens"]
        checks += 1
    for key in ("ZL3b/f18v.8", "IT2a/f18v.8", "RF1b/f18v.8"):
        assert stored["examples"][key]["omitted_tokens"] == ["ddy"]
        checks += 1

    output = {
        "status": "PASS_INDEPENDENT_PRE_GROUNDING_SURFACE_COVERAGE_RECONSTRUCTION",
        "checks": checks,
        "source_rows": len(source_rows),
        "unique_alignments": unique,
        "affected_rows": len(rebuilt),
        "omitted_tokens": total["omitted_tokens"],
        "omitted_characters": total["omitted_characters"],
        "input_sha256": digest(INTERLINEAR),
        "audit_sha256": digest(AUDIT),
        "residual_atlas_sha256": digest(ATLAS),
        "english_lexical_glosses": 0,
    }
    OUTPUT.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
