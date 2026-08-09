#!/usr/bin/env python3
"""Audit literal-surface coverage of the frozen pre-grounding formal layer.

This does not reparse the manuscript.  It compares the complete manual-
transcription surface already stored in the frozen interlinear with the node
surfaces stored in ``formal_interlinear``.  Omitted space-delimited groups are
retained as literal, role-unknown residuals; no lexical gloss is introduced.
"""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
INTERLINEAR = RESULTS / "pre_grounding_interlinear.tsv"
MANIFEST = RESULTS / "pre_grounding_package_manifest.json"
OUTPUT_ATLAS = RESULTS / "pre_grounding_surface_residual_atlas.tsv"
OUTPUT_JSON = RESULTS / "pre_grounding_surface_coverage_audit.json"
EXPECTED_INPUT_SHA256 = "8052a51fa37ad467e754be39648336ec4014442dab5e223daab2e77efaba4a43"
EXPECTED_MANIFEST_SHA256 = "3ca036eecf45f7440c792d907ea630290116f82130c71af56494b654bdf0e542"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def formal_surfaces(row: dict[str, str]) -> list[str]:
    if not row["formal_interlinear"]:
        return []
    return [item.split("=", 1)[0] for item in row["formal_interlinear"].split(" | ")]


def unique_subsequence_mask(tokens: tuple[str, ...], target: str) -> tuple[bool, ...]:
    """Return the unique whole-token subset whose concatenation is target."""

    @lru_cache(maxsize=None)
    def solve(index: int, offset: int) -> tuple[int, tuple[bool, ...]]:
        if index == len(tokens):
            return (1, ()) if offset == len(target) else (0, ())
        count = 0
        chosen: tuple[bool, ...] = ()

        omit_count, omit_mask = solve(index + 1, offset)
        if omit_count:
            count = omit_count
            chosen = (False,) + omit_mask

        token = tokens[index]
        if target.startswith(token, offset):
            keep_count, keep_mask = solve(index + 1, offset + len(token))
            if keep_count:
                if count == 0:
                    chosen = (True,) + keep_mask
                count = min(2, count + keep_count)
        return count, chosen

    count, mask = solve(0, 0)
    if count != 1:
        raise RuntimeError(f"surface/formal alignment has {count} solutions: {tokens!r} -> {target!r}")
    return mask


def nested_counter(counter: Counter[tuple[str, str]]) -> dict[str, dict[str, int]]:
    output: dict[str, dict[str, int]] = defaultdict(dict)
    for (edition, category), count in sorted(counter.items()):
        output[edition][category] = count
    return dict(output)


def main() -> None:
    if sha256(INTERLINEAR) != EXPECTED_INPUT_SHA256:
        raise RuntimeError("pre-grounding interlinear hash drift")
    if sha256(MANIFEST) != EXPECTED_MANIFEST_SHA256:
        raise RuntimeError("pre-grounding manifest hash drift")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest["outputs"][INTERLINEAR.name]["sha256"] != EXPECTED_INPUT_SHA256:
        raise RuntimeError("manifest/interlinear binding drift")

    rows = load_tsv(INTERLINEAR)
    edition_stats: dict[str, Counter[str]] = defaultdict(Counter)
    scope_affected: Counter[tuple[str, str]] = Counter()
    kind_affected: Counter[tuple[str, str]] = Counter()
    omitted_types: Counter[str] = Counter()
    affected_pages: dict[str, set[str]] = defaultdict(set)
    atlas_rows: list[dict[str, object]] = []
    examples: dict[str, dict[str, object]] = {}

    for row in rows:
        edition = row["edition"]
        surface_tokens = tuple(row["surface"].split())
        node_surfaces = formal_surfaces(row)
        parsed_target = "".join(node_surfaces)
        mask = unique_subsequence_mask(surface_tokens, parsed_target)
        retained = [token for token, keep in zip(surface_tokens, mask) if keep]
        omitted = [token for token, keep in zip(surface_tokens, mask) if not keep]
        omitted_positions = [index for index, keep in enumerate(mask, 1) if not keep]

        root_count = len(row["root_sequence"].split()) if row["root_sequence"] else 0
        role_count = len(row["role_sequence"].split()) if row["role_sequence"] else 0
        declared_nodes = int(row["word_count"])
        if not (len(node_surfaces) == root_count == role_count == declared_nodes):
            raise RuntimeError(f"formal column count drift at {edition}/{row['locus']}")
        if retained != node_surfaces:
            raise RuntimeError(f"node surface order drift at {edition}/{row['locus']}")

        stats = edition_stats[edition]
        stats.update({
            "rows": 1,
            "surface_tokens": len(surface_tokens),
            "parsed_nodes": declared_nodes,
            "surface_characters": sum(map(len, surface_tokens)),
            "parsed_characters": len(parsed_target),
        })
        if omitted:
            stats.update({
                "affected_rows": 1,
                "omitted_tokens": len(omitted),
                "omitted_characters": sum(map(len, omitted)),
            })
            scope_affected[(edition, row["grammar_scope"])] += 1
            kind_affected[(edition, row["kind"])] += 1
            affected_pages[edition].add(row["page"])
            omitted_types.update(omitted)
            atlas_rows.append({
                "edition": edition,
                "locus": row["locus"],
                "page": row["page"],
                "grammar_scope": row["grammar_scope"],
                "kind": row["kind"],
                "surface_token_count": len(surface_tokens),
                "parsed_node_count": declared_nodes,
                "omitted_token_count": len(omitted),
                "omitted_positions_1based": ";".join(map(str, omitted_positions)),
                "omitted_tokens": " ".join(omitted),
                "position_token_pairs": ";".join(
                    f"{position}:{token}" for position, token in zip(omitted_positions, omitted)
                ),
            })

        key = f"{edition}/{row['locus']}"
        if row["locus"] in {"f11v.6", "f18v.8"}:
            examples[key] = {
                "surface": row["surface"],
                "parsed_node_surfaces": node_surfaces,
                "omitted_positions_1based": omitted_positions,
                "omitted_tokens": omitted,
            }

    atlas_rows.sort(key=lambda item: (str(item["edition"]), str(item["page"]), str(item["locus"])))
    fields = [
        "edition", "locus", "page", "grammar_scope", "kind",
        "surface_token_count", "parsed_node_count", "omitted_token_count",
        "omitted_positions_1based", "omitted_tokens", "position_token_pairs",
    ]
    with OUTPUT_ATLAS.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(atlas_rows)

    totals = Counter()
    for stats in edition_stats.values():
        totals.update(stats)
    payload = {
        "status": "PASS_COMPLETE_SURFACE_PARTIAL_FORMAL_COVERAGE",
        "decision": "CORRECT_PRE_GROUNDING_COMPLETENESS_CLAIM",
        "claim_ceiling": (
            "The frozen package is complete for loci and literal surface, but its formal/root/role "
            "layer covers only the retained parser nodes. Omitted groups remain literal "
            "UNPARSED_SURFACE with no assigned structural role or lexical meaning."
        ),
        "inputs": {
            str(INTERLINEAR.relative_to(HERE.parents[1])): sha256(INTERLINEAR),
            str(MANIFEST.relative_to(HERE.parents[1])): sha256(MANIFEST),
        },
        "totals": dict(sorted(totals.items())),
        "by_edition": {key: dict(sorted(value.items())) for key, value in sorted(edition_stats.items())},
        "affected_rows_by_scope": nested_counter(scope_affected),
        "affected_rows_by_kind": nested_counter(kind_affected),
        "affected_pages_by_edition": {key: len(value) for key, value in sorted(affected_pages.items())},
        "omitted_token_type_counts": dict(sorted(omitted_types.items())),
        "most_common_omitted_tokens": [
            {"token": token, "count": count} for token, count in omitted_types.most_common(20)
        ],
        "examples": dict(sorted(examples.items())),
        "target_relevance": {
            "f2r_15_has_surface_residual": any(
                item["locus"] == "f2r.15" for item in atlas_rows
            ),
            "omitted_token_occurrences_containing_i_or_o": sum(
                count for token, count in omitted_types.items() if "i" in token or "o" in token
            ),
            "col001_frozen_formal_counts_changed_by_residual_inventory": False,
        },
        "residual_atlas": {
            "path": str(OUTPUT_ATLAS.relative_to(HERE.parents[1])),
            "rows": len(atlas_rows),
            "sha256": sha256(OUTPUT_ATLAS),
        },
        "alignment": {
            "method": "unique whole-surface-token subsequence preserving order",
            "all_rows_unique": True,
            "rows_checked": len(rows),
            "insertions_or_replacements": 0,
        },
        "english_lexical_glosses": 0,
    }
    OUTPUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
