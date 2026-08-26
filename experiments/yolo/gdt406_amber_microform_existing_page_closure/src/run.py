#!/usr/bin/env python3
"""Audit the 49 GDT405 amber recipes against the already admitted 26 pages.

No new transcription or image is opened. The experiment asks a narrow
question: are the internal adjacent packages of each singleton recipe already
used on other admitted pages? Package support can lower the risk of a locked
recipe, but a singleton never becomes GREEN without an exact future recurrence.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
HERE = Path(__file__).resolve().parent.parent
OUT = HERE / "artifacts"
OLD = ROOT / "experiments/yolo/sidequest_semantic_visible_allograph_resegmentation_one_thousand_twenty_sixth/PASS1026_3888_CORRECTED_EVENT_LEDGER.tsv"
NEW = ROOT / "experiments/yolo/gdt404_random_four_page_factorized_admission/artifacts/gdt404_688_event_first_pass.tsv"
AMBER = ROOT / "experiments/yolo/gdt405_second_random_batch_recipe_lock/artifacts/gdt405_49_amber_microform_lock.tsv"
ATOMS = ROOT / "experiments/yolo/gdt405_second_random_batch_recipe_lock/artifacts/gdt405_46_locked_atom_dictionary.tsv"

OLD_PAGES = {
    "f10r", "f11r", "f13r", "f17r", "f18r", "f55v", "f56r", "f67r2",
    "f68r1", "f71v", "f72r", "f75r", "f76r", "f77r", "f81v", "f82r",
    "f83r", "f88r", "f88v", "f89r",
}
NEW_PAGES = {"f1r", "f24v", "f81r", "f95v"}
LOCAL_ONLY_PAGES = {"f69v", "f70v"}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def split_recipe(recipe: str) -> tuple[str, ...]:
    return tuple(part for part in recipe.split("+") if part)


def ngrams(parts: tuple[str, ...], n: int) -> set[tuple[str, ...]]:
    return {parts[i:i+n] for i in range(len(parts) - n + 1)}


def parse_candidates(raw: str) -> list[tuple[str, int]]:
    out: list[tuple[str, int]] = []
    if not raw:
        return out
    for item in raw.split(" | "):
        recipe, weight = item.rsplit("::", 1)
        out.append((recipe, int(weight)))
    return out


def recipe_bits(parts: tuple[str, ...], unigram: Counter, bigram: Counter, vocabulary: int) -> float:
    """Descriptive Markov score; never used to change a locked recipe."""
    if not parts:
        return 999.0
    total = sum(unigram.values())
    bits = -math.log2((unigram[parts[0]] + 1) / (total + vocabulary))
    for left, right in zip(parts, parts[1:]):
        bits -= math.log2((bigram[(left, right)] + 1) / (unigram[left] + vocabulary))
    return bits


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    old_rows = read_tsv(OLD)
    new_rows = read_tsv(NEW)
    amber_rows = read_tsv(AMBER)
    atom_rows = read_tsv(ATOMS)
    known_atoms = {row["atom"] for row in atom_rows}

    assert len(old_rows) == 3888
    assert len(new_rows) == 688
    assert len(amber_rows) == 49
    assert len(known_atoms) == 46
    assert {r["physical_page"] for r in old_rows} == OLD_PAGES
    assert {r["physical_page"] for r in new_rows} == NEW_PAGES
    assert not (OLD_PAGES & NEW_PAGES)

    corpus: list[dict[str, object]] = []
    for row in old_rows:
        corpus.append({
            "deck": "OLD22", "page": row["physical_page"], "surface": row["surface"],
            "recipe": row["pass1026_recipe"], "event_id": row["pass1026_event_id"],
            "statement_id": row["statement_id"], "register": row["register"],
        })
    for row in new_rows:
        corpus.append({
            "deck": "RANDOM4", "page": row["physical_page"], "surface": row["surface"],
            "recipe": row["visible_recipe"], "event_id": row["event_id"],
            "statement_id": row["statement_id"], "register": row["register"],
        })

    amber_surfaces = {row["surface"] for row in amber_rows}
    occurrence = defaultdict(list)
    for row in corpus:
        occurrence[str(row["surface"])].append(row)
    assert all(len(occurrence[surface]) == 1 for surface in amber_surfaces)

    package_rows: list[dict[str, object]] = []
    audit_rows: list[dict[str, object]] = []
    candidate_rows: list[dict[str, object]] = []
    cluster_counter: Counter[str] = Counter()
    tier_counter: Counter[str] = Counter()

    for amber in amber_rows:
        surface = amber["surface"]
        primary = amber["primary_locked_recipe"]
        primary_atoms = split_recipe(primary)
        target = occurrence[surface][0]
        other = [row for row in corpus if row["surface"] != surface]

        support: dict[int, dict[tuple[str, ...], list[dict[str, object]]]] = {
            1: defaultdict(list), 2: defaultdict(list), 3: defaultdict(list), 4: defaultdict(list)
        }
        unigram: Counter = Counter()
        bigram: Counter = Counter()
        for row in other:
            parts = split_recipe(str(row["recipe"]))
            unigram.update(parts)
            bigram.update(zip(parts, parts[1:]))
            for size in support:
                for gram in ngrams(parts, size):
                    support[size][gram].append(row)

        pair_grams = list(zip(primary_atoms, primary_atoms[1:]))
        tri_grams = [primary_atoms[i:i+3] for i in range(max(0, len(primary_atoms)-2))]
        old_pair_supported = 0
        external_pair_supported = 0
        two_page_pair_supported = 0
        pair_min_pages = 999 if pair_grams else 0
        pair_min_surfaces = 999 if pair_grams else 0
        unsupported_pairs: list[str] = []
        for ordinal, pair in enumerate(pair_grams, start=1):
            hits = support[2].get(pair, [])
            pages = sorted({str(hit["page"]) for hit in hits})
            surfaces = sorted({str(hit["surface"]) for hit in hits})
            old_hits = [hit for hit in hits if hit["deck"] == "OLD22"]
            new_hits = [hit for hit in hits if hit["deck"] == "RANDOM4"]
            old_pages = sorted({str(hit["page"]) for hit in old_hits})
            if hits:
                external_pair_supported += 1
            else:
                unsupported_pairs.append("+".join(pair))
            if old_hits:
                old_pair_supported += 1
            if len(pages) >= 2:
                two_page_pair_supported += 1
            pair_min_pages = min(pair_min_pages, len(pages))
            pair_min_surfaces = min(pair_min_surfaces, len(surfaces))
            package_rows.append({
                "amber_id": amber["amber_id"], "surface": surface,
                "target_page": target["page"], "pair_ordinal": ordinal,
                "left_atom": pair[0], "right_atom": pair[1], "pair": "+".join(pair),
                "other_event_count": len(hits), "other_surface_count": len(surfaces),
                "other_page_count": len(pages), "old22_event_count": len(old_hits),
                "old22_page_count": len(old_pages), "random4_other_event_count": len(new_hits),
                "supporting_pages": "|".join(pages) or "NONE",
                "example_surfaces": "|".join(surfaces[:8]) or "NONE",
            })

        tri_supported = sum(bool(support[3].get(gram)) for gram in tri_grams)
        old_tri_supported = sum(
            any(hit["deck"] == "OLD22" for hit in support[3].get(gram, []))
            for gram in tri_grams
        )
        max_span = 1
        max_old_span = 1
        for size in range(2, min(4, len(primary_atoms)) + 1):
            for gram in ngrams(primary_atoms, size):
                if support[size].get(gram):
                    max_span = max(max_span, size)
                if any(hit["deck"] == "OLD22" for hit in support[size].get(gram, [])):
                    max_old_span = max(max_old_span, size)

        unknown_atoms = sorted(set(primary_atoms) - known_atoms)
        pair_total = len(pair_grams)
        all_external = external_pair_supported == pair_total
        all_old = old_pair_supported == pair_total
        has_long_old = len(primary_atoms) <= 2 or max_old_span >= 3
        if unknown_atoms:
            tier = "BLOCK_NEW_ATOM"
        elif all_old and has_long_old:
            tier = "AMBER__STRONG_OLD_PACKAGE_SUPPORT"
        elif all_external and max_span >= min(3, len(primary_atoms)):
            tier = "AMBER__CURRENT_CROSS_PAGE_PACKAGE_SUPPORT"
        elif external_pair_supported >= max(1, pair_total - 1):
            tier = "AMBER__PARTIAL_PACKAGE_SUPPORT"
        else:
            tier = "AMBER__ISOLATED_BOUNDARY"
        tier_counter[tier] += 1

        flags: list[str] = []
        if "DY" in primary_atoms:
            flags.append("CONTAINS_DY")
        if primary_atoms and primary_atoms[-1] == "DY":
            flags.append("CLOSE_CANDIDATE")
        if any(token.startswith("LOCAL_") or token.endswith("_ADDR") or token.endswith("_LABEL") or token == "M_LOCAL" for token in primary_atoms):
            flags.append("LOCAL_SIGN")
        if len(primary_atoms) >= 6:
            flags.append("LONG_CHAIN")
        if len(set(primary_atoms)) < len(primary_atoms):
            flags.append("REPEATED_ATOM")
        if "R" in primary_atoms:
            flags.append("R_INTERNAL")
        if not flags:
            flags.append("PLAIN_CORE_CHAIN")
        for flag in flags:
            cluster_counter[flag] += 1

        alternatives = parse_candidates(amber["one_edit_candidate_recipes"])
        candidate_set: list[tuple[str, int, str]] = [(primary, 0, "LOCKED_PRIMARY")]
        seen = {primary}
        for recipe, weight in alternatives:
            if recipe not in seen:
                candidate_set.append((recipe, weight, "ONE_EDIT_RIVAL"))
                seen.add(recipe)
        scored: list[tuple[float, str, int, str]] = []
        vocabulary = max(1, len(known_atoms))
        for recipe, weight, kind in candidate_set:
            parts = split_recipe(recipe)
            bits = recipe_bits(parts, unigram, bigram, vocabulary)
            pairs = list(zip(parts, parts[1:]))
            pair_cov = sum(bool(support[2].get(pair)) for pair in pairs)
            old_pair_cov = sum(
                any(hit["deck"] == "OLD22" for hit in support[2].get(pair, [])) for pair in pairs
            )
            candidate_rows.append({
                "amber_id": amber["amber_id"], "surface": surface, "candidate_kind": kind,
                "recipe": recipe, "one_edit_weight": weight, "atom_count": len(parts),
                "known_atom_count": sum(token in known_atoms for token in parts),
                "adjacent_pair_count": len(pairs), "external_pair_support_count": pair_cov,
                "old22_pair_support_count": old_pair_cov,
                "descriptive_bigram_bits": f"{bits:.6f}",
                "may_change_locked_recipe": "NO",
            })
            scored.append((bits, recipe, weight, kind))
        scored.sort(key=lambda item: (item[0], item[1]))
        primary_bits = next(item[0] for item in scored if item[1] == primary)
        primary_rank = 1 + next(i for i, item in enumerate(scored) if item[1] == primary)
        better_rivals = sum(1 for bits, recipe, _, _ in scored if recipe != primary and bits < primary_bits)

        audit_rows.append({
            "amber_id": amber["amber_id"], "surface": surface,
            "event_id": target["event_id"], "physical_page": target["page"],
            "statement_id": target["statement_id"], "register": target["register"],
            "primary_locked_recipe": primary, "atom_count": len(primary_atoms),
            "all_atoms_locked": "YES" if not unknown_atoms else "NO",
            "adjacent_pair_count": pair_total,
            "pairs_supported_outside_surface": external_pair_supported,
            "pairs_supported_in_old22": old_pair_supported,
            "pairs_supported_on_two_pages": two_page_pair_supported,
            "minimum_other_page_support": pair_min_pages,
            "minimum_other_surface_support": pair_min_surfaces,
            "trigram_count": len(tri_grams), "trigrams_supported_outside_surface": tri_supported,
            "trigrams_supported_in_old22": old_tri_supported,
            "longest_supported_span_max4": max_span,
            "longest_old22_supported_span_max4": max_old_span,
            "unsupported_adjacent_pairs": "|".join(unsupported_pairs) or "NONE",
            "risk_flags": "|".join(flags), "package_support_tier": tier,
            "locked_primary_bigram_rank_among_candidates": primary_rank,
            "candidate_recipe_count_including_primary": len(scored),
            "rivals_with_lower_descriptive_bigram_bits": better_rivals,
            "promotion_status": "REMAINS_AMBER__NO_EXACT_RECURRENCE",
            "lock_action": "KEEP_GDT405_PRIMARY_RECIPE",
        })

    cluster_rows = [
        {"cluster": key, "amber_surface_count": value}
        for key, value in sorted(cluster_counter.items())
    ]
    tier_rows = [
        {"package_support_tier": key, "amber_surface_count": value}
        for key, value in sorted(tier_counter.items())
    ]

    audit_path = OUT / "gdt406_49_amber_package_audit.tsv"
    pair_path = OUT / "gdt406_adjacent_package_evidence.tsv"
    cand_path = OUT / "gdt406_candidate_recipe_pressure.tsv"
    cluster_path = OUT / "gdt406_amber_risk_clusters.tsv"
    tier_path = OUT / "gdt406_package_support_tiers.tsv"
    write_tsv(audit_path, audit_rows, list(audit_rows[0]))
    write_tsv(pair_path, package_rows, list(package_rows[0]))
    write_tsv(cand_path, candidate_rows, list(candidate_rows[0]))
    write_tsv(cluster_path, cluster_rows, ["cluster", "amber_surface_count"])
    write_tsv(tier_path, tier_rows, ["package_support_tier", "amber_surface_count"])

    result = {
        "status": "AMBER_RISK_STRATIFIED__NO_PROMOTIONS_WITHOUT_RECURRENCE",
        "admitted_physical_pages": 26,
        "running_recipe_pages": len(OLD_PAGES | NEW_PAGES),
        "local_only_pages_excluded_from_recipe_support": sorted(LOCAL_ONLY_PAGES),
        "source_events": len(corpus),
        "amber_surfaces": len(audit_rows),
        "promoted_green": 0,
        "new_atoms": sum(row["all_atoms_locked"] == "NO" for row in audit_rows),
        "tier_counts": dict(sorted(tier_counter.items())),
        "risk_cluster_counts": dict(sorted(cluster_counter.items())),
        "all_adjacent_pairs_supported_outside_surface": sum(
            row["pairs_supported_outside_surface"] == row["adjacent_pair_count"] for row in audit_rows
        ),
        "all_adjacent_pairs_supported_in_old22": sum(
            row["pairs_supported_in_old22"] == row["adjacent_pair_count"] for row in audit_rows
        ),
        "primary_bigram_rank_one": sum(
            row["locked_primary_bigram_rank_among_candidates"] == 1 for row in audit_rows
        ),
        "input_sha256": {str(path.relative_to(ROOT)): sha256(path) for path in (OLD, NEW, AMBER, ATOMS)},
        "output_sha256": {str(path.relative_to(HERE)): sha256(path) for path in (audit_path, pair_path, cand_path, cluster_path, tier_path)},
    }
    (OUT / "gdt406_result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
