#!/usr/bin/env python3
"""Audit every cached occurrence of the eleven direct ychor followers."""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE_REL = Path("experiments/yolo/gdt758_ychor_follower_global_content_census")
EXP = ROOT / BASE_REL
SRC = EXP / "src"
DEFAULT_ARTIFACTS = EXP / "artifacts"

G756_RUN_REL = Path(
    "experiments/yolo/gdt756_ychor_line_frame_content_slots/src/run.py"
)
G745_RUN_REL = Path(
    "experiments/yolo/gdt745_exact_open_content_role_expansion/src/run.py"
)
G756_BODY_REL = Path(
    "experiments/yolo/gdt756_ychor_line_frame_content_slots/"
    "artifacts/YCHOR_71_BODY_TOKEN_CANDIDATES.tsv"
)
G756_LINES_REL = Path(
    "experiments/yolo/gdt756_ychor_line_frame_content_slots/"
    "artifacts/YCHOR_13_LINE_ATLAS.tsv"
)
G754_INVENTORY_REL = Path(
    "experiments/yolo/gdt754_active_productive_compound_provenance_sieve/"
    "artifacts/ACTIVE_172_PRODUCTIVE_COMPOUND_INVENTORY.tsv"
)
G757_FORMULAE_REL = Path(
    "experiments/yolo/gdt757_initial_formula_role_atlas/"
    "artifacts/INITIAL_FORMULA_11_WHOLE_ROLE_ATLAS.tsv"
)
G755_BANK_REL = Path(
    "experiments/yolo/gdt755_top24_historical_register_crosswalk/"
    "src/HISTORICAL_EXPRESSION_BANK.tsv"
)
G755_SOURCES_REL = Path(
    "experiments/yolo/gdt755_top24_historical_register_crosswalk/"
    "src/HISTORICAL_SOURCE_REGISTRY.tsv"
)
G625_TERM_REL = Path(
    "experiments/yolo/gdt625_ordered_quality_state_transitions/"
    "artifacts/CANDIDATE_TERM_ROLE_SUMMARY.tsv"
)
G629_CLAUSE_REL = Path(
    "experiments/yolo/gdt629_part_quality_degree_clause/"
    "artifacts/CONCRETE_CLAUSES_V1.tsv"
)

TARGET_FORMS = (
    "chor", "chshoty", "cthy", "oky", "qokchol", "s",
    "ar", "odol", "ols", "sheol", "chol",
)
ORDERED_VALUE_FORMS = ("an", "ain", "aiin", "aiiin")
OUTPUT_NAMES = (
    "FOLLOWER_11_1141_OCCURRENCE_ATLAS.tsv",
    "FOLLOWER_11_GLOBAL_CENSUS.tsv",
    "FOLLOWER_11_CLEAN_WHOLE_ANALOGY.tsv",
    "FOLLOWER_11_EXACT_ADJACENCY_ATLAS.tsv",
    "ORDERED_VALUE_FOLLOWER_COMPARATOR.tsv",
    "HISTORICAL_FOLLOWER_COMPARATORS.tsv",
    "YCHOR_71_REVISED_BODY_TOKENS.tsv",
    "YCHOR_13_REVISED_READER.tsv",
    "GDT758_WORKING_DICTIONARY.md",
    "RESULT.json",
)
STATUS = (
    "PARTIAL__11_YCHOR_FOLLOWER_WHOLES__1141_EXACT_OCCURRENCES__"
    "13_DIRECT_YCHOR_POSITIONS__S_EQUAL_AMOUNT_LEAD_25_OF99_ORDERED_VALUE_"
    "FOLLOWERS__23_S_TO_AIIN_BIGRAMS__8_EXACT_SPAN_RENDER_RULES__"
    "ZERO_CONFIRMED_LEXEMES__NO_NEW_PAGE"
)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load dependency: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


g756 = load_module("gdt756_builder_for_gdt758", ROOT / G756_RUN_REL)
g745 = load_module("gdt745_builder_for_gdt758", ROOT / G745_RUN_REL)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(
    path: Path, rows: Iterable[dict[str, object]], fields: Iterable[str]
) -> None:
    names = list(fields)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=names, delimiter="\t", lineterminator="\n",
            extrasaction="raise",
        )
        writer.writeheader()
        for row in rows:
            writer.writerow({name: row.get(name, "") for name in names})


def values(text: str) -> set[str]:
    return {item for item in text.split("|") if item and item != "NONE"}


def joined(items: Iterable[str]) -> str:
    selected = set(items)
    order = g756.g755.AXIS_ORDER
    arranged = [axis for axis in order if axis in selected]
    arranged.extend(sorted(selected - set(arranged)))
    return "|".join(arranged) or "NONE"


def count_text(items: Iterable[str]) -> str:
    counts = Counter(items)
    return "|".join(f"{key}:{counts[key]}" for key in sorted(counts)) or "NONE"


def fixed(number: float) -> str:
    return f"{number:.6f}"


def pair_universe(context: object) -> dict[str, object]:
    pairs: Counter[tuple[str, str]] = Counter()
    left_opportunities: Counter[str] = Counter()
    right_opportunities: Counter[str] = Counter()
    occurrences: Counter[str] = Counter()
    total_pairs = 0
    for locus, line in context.by_line.items():
        for index, token in enumerate(line):
            if not context.exact[(locus, int(token["token_index"]))]:
                continue
            surface = str(token["eva"])
            occurrences[surface] += 1
            if index + 1 >= len(line):
                continue
            follower = line[index + 1]
            if not context.exact[(locus, int(follower["token_index"]))]:
                continue
            following_surface = str(follower["eva"])
            pairs[(surface, following_surface)] += 1
            left_opportunities[surface] += 1
            right_opportunities[following_surface] += 1
            total_pairs += 1
    return {
        "pairs": pairs,
        "left_opportunities": left_opportunities,
        "right_opportunities": right_opportunities,
        "occurrences": occurrences,
        "total_pairs": total_pairs,
    }


def build_occurrences(
    context: object,
    line_meta: dict[str, dict[str, str]],
    rules: list[dict[str, str]],
    suspect_surfaces: set[str],
    formula_forms: set[str],
    priors: dict[str, dict[str, str]],
) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    target_set = set(TARGET_FORMS)
    number = 0
    for locus, line in context.by_line.items():
        written = " ".join(str(token["eva"]) for token in line)
        for ordinal, token in enumerate(line, start=1):
            surface = str(token["eva"])
            if surface not in target_set:
                continue
            if not context.exact[(locus, int(token["token_index"]))]:
                continue
            number += 1
            left, left_boundary = g756.g755.scan_side(
                context, locus, ordinal, -1, suspect_surfaces
            )
            right, right_boundary = g756.g755.scan_side(
                context, locus, ordinal, 1, suspect_surfaces
            )
            span = left + right
            anchors = [item for item in span if item["axes"]]
            tags = {axis for item in anchors for axis in item["axes"]}
            channel = g756.g755.g753.g752.g744.channel_for(tags, rules)
            complete = int(
                not left_boundary.startswith("RADIUS5")
                and not right_boundary.startswith("RADIUS5")
            )
            previous = line[ordinal - 2] if ordinal > 1 else None
            following = line[ordinal] if ordinal < len(line) else None
            previous_exact = int(
                previous is not None
                and context.exact[(locus, int(previous["token_index"]))]
            )
            following_exact = int(
                following is not None
                and context.exact[(locus, int(following["token_index"]))]
            )
            previous_surface = str(previous["eva"]) if previous else "LINE_EDGE"
            following_surface = str(following["eva"]) if following else "LINE_EDGE"
            formula_predecessor = (
                previous_surface
                if previous_exact and previous_surface in formula_forms else "NONE"
            )
            cell = context.cells[(locus, ordinal)]
            evidence = " || ".join(
                f"{item['side']}{item['distance']} {item['surface']}="
                f"{item['semantic']} [{joined(item['axes'])};{item['confidence']}]"
                for item in sorted(anchors, key=lambda item: int(item["ordinal"]))
            ) or "NONE"
            meta = line_meta[locus]
            prior = priors[surface]
            output.append({
                "gdt758_occurrence_id": f"G758-O{number:04d}",
                "surface": surface,
                "page": token["page"],
                "physical_folio": g756.g755.g753.g752.g751.g750.g749.g746.g745.physical_folio(token["page"]),
                "locus": locus,
                "token_ordinal": ordinal,
                "line_token_count": len(line),
                "normalized_position": fixed((ordinal - 1) / max(1, len(line) - 1)),
                "line_position": g756.g755.line_position(ordinal, len(line)),
                "paragraph_first_token": int(meta["paragraph_start"] == "1" and ordinal == 1),
                "paragraph_last_token": int(meta["paragraph_end"] == "1" and ordinal == len(line)),
                "section": token["section"],
                "language": token["language"],
                "hand": token["hand"],
                "written_line_eva": written,
                "immediate_left_surface": previous_surface,
                "immediate_left_reader_exact": previous_exact,
                "immediate_right_surface": following_surface,
                "immediate_right_reader_exact": following_exact,
                "formula_predecessor": formula_predecessor,
                "directly_after_ychor": int(formula_predecessor == "ychor"),
                "left_extent": len(left),
                "right_extent": len(right),
                "left_boundary_reason": left_boundary,
                "right_boundary_reason": right_boundary,
                "boundary_complete": complete,
                "independent_anchor_count": len(anchors),
                "independent_anchor_surfaces": "|".join(str(item["surface"]) for item in anchors) or "NONE",
                "independent_anchor_tags": joined(tags),
                "independent_anchor_evidence": evidence,
                "field_channel": channel,
                "slot_class": g756.g755.g753.g752.g744.content_slot_class(channel, tags),
                "suspect_neighbor_cells_with_axes_excluded": sum(
                    int(item["suspect_compound_axes_excluded"]) for item in span
                ),
                "target_cache_value_background_not_used_as_anchor": cell["v99r7_semantic_value_de"],
                "gdt758_primary_candidate_de": prior["primary_candidate_de"],
                "gdt758_renderer_value_de": prior["renderer_value_de"],
                "gdt758_working_confidence": prior["working_confidence"],
                "all_172_productive_compound_axes_excluded_from_field": 1,
                "reader_exact_target": 1,
                "exact_whole_only": 1,
                "literal_identity": "OPEN",
                "confirmed_lexeme": 0,
                "component_export_credit": 0,
            })
    return output


def build_adjacency(
    pair_data: dict[str, object], formula_forms: set[str]
) -> list[dict[str, object]]:
    pairs: Counter[tuple[str, str]] = pair_data["pairs"]  # type: ignore[assignment]
    lefts: Counter[str] = pair_data["left_opportunities"]  # type: ignore[assignment]
    rights: Counter[str] = pair_data["right_opportunities"]  # type: ignore[assignment]
    occurrences: Counter[str] = pair_data["occurrences"]  # type: ignore[assignment]
    total = int(pair_data["total_pairs"])
    target_order = {surface: index for index, surface in enumerate(TARGET_FORMS)}
    output: list[dict[str, object]] = []
    for target in TARGET_FORMS:
        right_rows = [
            (neighbor, count) for (left, neighbor), count in pairs.items()
            if left == target
        ]
        left_rows = [
            (neighbor, count) for (neighbor, right), count in pairs.items()
            if right == target
        ]
        for direction, rows in (("RIGHT", right_rows), ("LEFT", left_rows)):
            rows.sort(key=lambda item: (-item[1], item[0]))
            denominator = int(lefts[target] if direction == "RIGHT" else rights[target])
            for rank, (neighbor, pair_count) in enumerate(rows, start=1):
                background_count = int(
                    rights[neighbor] if direction == "RIGHT" else lefts[neighbor]
                )
                conditional = pair_count / denominator if denominator else 0.0
                baseline = background_count / total if total else 0.0
                expression = (
                    f"{target} {neighbor}" if direction == "RIGHT"
                    else f"{neighbor} {target}"
                )
                output.append({
                    "surface": target,
                    "neighbor_side": direction,
                    "side_frequency_rank": rank,
                    "exact_pair_expression": expression,
                    "neighbor_surface": neighbor,
                    "exact_pair_count": pair_count,
                    "target_exact_neighbor_contexts": denominator,
                    "conditional_rate": fixed(conditional),
                    "neighbor_background_pairs_same_side": background_count,
                    "all_exact_adjacent_pairs": total,
                    "baseline_rate": fixed(baseline),
                    "descriptive_lift": fixed(conditional / baseline if baseline else 0.0),
                    "neighbor_exact_occurrences": occurrences[neighbor],
                    "neighbor_is_ordered_value_form": int(neighbor in ORDERED_VALUE_FORMS),
                    "neighbor_is_formula_whole": int(neighbor in formula_forms),
                    "relation_is_exact_whole_adjacency_only": 1,
                    "semantic_equivalence_inferred": 0,
                    "component_export_credit": 0,
                })
    output.sort(key=lambda row: (
        target_order[str(row["surface"])],
        0 if row["neighbor_side"] == "LEFT" else 1,
        int(row["side_frequency_rank"]),
    ))
    return output


def build_value_comparator(
    pair_data: dict[str, object], target_forms: set[str]
) -> list[dict[str, object]]:
    pairs: Counter[tuple[str, str]] = pair_data["pairs"]  # type: ignore[assignment]
    lefts: Counter[str] = pair_data["left_opportunities"]  # type: ignore[assignment]
    rights: Counter[str] = pair_data["right_opportunities"]  # type: ignore[assignment]
    occurrences: Counter[str] = pair_data["occurrences"]  # type: ignore[assignment]
    total = int(pair_data["total_pairs"])
    ordered_background = sum(rights[surface] for surface in ORDERED_VALUE_FORMS)
    ordered_baseline = ordered_background / total
    aiin_baseline = rights["aiin"] / total
    raw: list[dict[str, object]] = []
    for surface, occurrence_count in occurrences.items():
        denominator = int(lefts[surface])
        counts = Counter({
            follower: pairs[(surface, follower)]
            for follower in ORDERED_VALUE_FORMS
            if pairs[(surface, follower)]
        })
        hits = sum(counts.values())
        if occurrence_count < 5 or denominator < 4 or not hits:
            continue
        aiin_hits = pairs[(surface, "aiin")]
        raw.append({
            "surface": surface,
            "reader_exact_occurrences": occurrence_count,
            "exact_right_contexts": denominator,
            "ordered_value_follower_hits": hits,
            "ordered_value_follower_counts": "|".join(
                f"{value}:{counts[value]}" for value in ORDERED_VALUE_FORMS
                if counts[value]
            ),
            "ordered_value_conditional_rate": fixed(hits / denominator),
            "ordered_value_baseline_rate": fixed(ordered_baseline),
            "ordered_value_descriptive_lift": fixed((hits / denominator) / ordered_baseline),
            "aiin_follower_hits": aiin_hits,
            "aiin_conditional_rate": fixed(aiin_hits / denominator),
            "aiin_baseline_rate": fixed(aiin_baseline),
            "aiin_descriptive_lift": fixed((aiin_hits / denominator) / aiin_baseline),
            "gdt758_target": int(surface in target_forms),
            "ordered_value_family_is_working_structural_label": 1,
            "numeric_value_or_unit_confirmed": 0,
            "component_export_credit": 0,
        })
    by_hits = sorted(raw, key=lambda row: (
        -int(row["ordered_value_follower_hits"]),
        -float(row["ordered_value_conditional_rate"]), str(row["surface"]),
    ))
    for rank, row in enumerate(by_hits, start=1):
        row["ordered_value_hit_count_rank"] = rank
    share_pool = sorted(
        (row for row in raw if int(row["exact_right_contexts"]) >= 20),
        key=lambda row: (
            -float(row["ordered_value_conditional_rate"]),
            -int(row["ordered_value_follower_hits"]), str(row["surface"]),
        ),
    )
    share_rank = {str(row["surface"]): rank for rank, row in enumerate(share_pool, start=1)}
    aiin_pool = sorted(raw, key=lambda row: (
        -int(row["aiin_follower_hits"]),
        -float(row["aiin_conditional_rate"]), str(row["surface"]),
    ))
    aiin_rank = {str(row["surface"]): rank for rank, row in enumerate(aiin_pool, start=1)}
    fields = [
        "ordered_value_hit_count_rank", "ordered_value_share_rank_min20_right_contexts",
        "aiin_hit_count_rank", *list(raw[0]),
    ]
    output: list[dict[str, object]] = []
    for row in by_hits:
        surface = str(row["surface"])
        augmented = {
            "ordered_value_hit_count_rank": row["ordered_value_hit_count_rank"],
            "ordered_value_share_rank_min20_right_contexts": share_rank.get(surface, "NA"),
            "aiin_hit_count_rank": aiin_rank[surface],
            **{key: value for key, value in row.items() if key != "ordered_value_hit_count_rank"},
        }
        output.append({field: augmented[field] for field in fields})
    return output


def build_historical_comparators(
    priors: dict[str, dict[str, str]],
    bank_rows: list[dict[str, str]],
    source_rows: list[dict[str, str]],
) -> list[dict[str, object]]:
    bank = {row["candidate_id"]: row for row in bank_rows}
    sources = {row["source_id"]: row for row in source_rows}
    targets_by_expression: defaultdict[str, list[str]] = defaultdict(list)
    for surface, prior in priors.items():
        for expression_id in values(prior["historical_expression_ids"]):
            if expression_id not in bank:
                raise AssertionError(f"unknown historical expression {expression_id}")
            targets_by_expression[expression_id].append(surface)
    output: list[dict[str, object]] = []
    for expression_id in sorted(targets_by_expression):
        row = bank[expression_id]
        source_ids = sorted(values(row["source_ids"]))
        missing = set(source_ids) - set(sources)
        if missing:
            raise AssertionError(f"missing historical sources {sorted(missing)}")
        output.append({
            "candidate_id": expression_id,
            "target_surfaces": "|".join(sorted(targets_by_expression[expression_id])),
            "normalized_expression": row["normalized_expression"],
            "working_gloss_de": row["working_gloss_de"],
            "candidate_kind": row["candidate_kind"],
            "historical_register_family": row["historical_register_family"],
            "required_all_axes": row["required_all_axes"],
            "preferred_axes": row["preferred_axes"],
            "source_ids": row["source_ids"],
            "source_works": " || ".join(sources[source_id]["work"] for source_id in source_ids),
            "date_bands": " || ".join(sources[source_id]["date_band"] for source_id in source_ids),
            "primary_urls": " || ".join(sources[source_id]["primary_url"] for source_id in source_ids),
            "attested_form": row["attested_form"],
            "locator": row["locator"],
            "attestation_scope": row["attestation_scope"],
            "evidence_note": row["evidence_note"],
            "voynich_spelling_match_scored": 0,
            "historical_expression_identified_with_target": 0,
        })
    return output


def axis_count_text(rows: Iterable[dict[str, object]]) -> str:
    counts: Counter[str] = Counter()
    for row in rows:
        counts.update(values(str(row["independent_anchor_tags"])))
    return "|".join(
        f"{axis}:{counts[axis]}" for axis in g756.g755.AXIS_ORDER if counts[axis]
    ) or "NONE"


def top_neighbors(
    rows: list[dict[str, object]], side: str, limit: int = 8
) -> str:
    chosen = [row for row in rows if row["neighbor_side"] == side][:limit]
    return "|".join(
        f"{row['neighbor_surface']}:{row['exact_pair_count']}"
        for row in chosen
    ) or "NONE"


def build_census(
    occurrences: list[dict[str, object]],
    adjacency: list[dict[str, object]],
    summaries: dict[str, dict[str, object]],
    priors: dict[str, dict[str, str]],
    value_comparator: list[dict[str, object]],
    cthy_legacy: dict[str, str],
    exact_part_clauses: int,
) -> list[dict[str, object]]:
    by_surface: defaultdict[str, list[dict[str, object]]] = defaultdict(list)
    adj_by_surface: defaultdict[str, list[dict[str, object]]] = defaultdict(list)
    value_by_surface = {str(row["surface"]): row for row in value_comparator}
    for row in occurrences:
        by_surface[str(row["surface"])].append(row)
    for row in adjacency:
        adj_by_surface[str(row["surface"])].append(row)
    output: list[dict[str, object]] = []
    for surface in TARGET_FORMS:
        rows = by_surface[surface]
        complete = [row for row in rows if int(row["boundary_complete"])]
        anchored = [row for row in complete if int(row["independent_anchor_count"])]
        adj = adj_by_surface[surface]
        prior = priors[surface]
        analogy = summaries[surface]
        value = value_by_surface.get(surface)
        section_counts = Counter(str(row["section"]) for row in rows)
        formula_counts = Counter(
            str(row["formula_predecessor"]) for row in rows
            if row["formula_predecessor"] != "NONE"
        )
        evidence_parts = [
            f"{len(rows)} reader-exakte Vorkommen auf {len({str(row['page']) for row in rows})} Seiten",
            f"Sektionen {count_text(str(row['section']) for row in rows)}",
            f"direkt nach ychor {sum(int(row['directly_after_ychor']) for row in rows)}",
            f"Ganzwortanalogie {analogy['analogy_consensus_axes']} ({analogy['analogy_confidence_level']})",
        ]
        if value is not None:
            evidence_parts.append(
                f"geordnete Wertfolger {value['ordered_value_follower_hits']}/"
                f"{value['exact_right_contexts']} Lift {value['ordered_value_descriptive_lift']}"
            )
        if surface == "cthy":
            evidence_parts.append(
                f"GDT625 Altpanel {cthy_legacy['herbal_occurrences']}/"
                f"{cthy_legacy['zl3b_occurrences']} Herbal"
            )
        if surface in {"chor", "chol"}:
            evidence_parts.append(f"GDT629 dreifach exakte Part-Trocken-Klauseln {exact_part_clauses}")
        output.append({
            "surface": surface,
            "reader_exact_occurrences": len(rows),
            "reader_exact_pages": len({str(row["page"]) for row in rows}),
            "reader_exact_loci": len({str(row["locus"]) for row in rows}),
            "line_first_occurrences": sum(row["line_position"] in {"FIRST", "SINGLE"} for row in rows),
            "line_middle_occurrences": sum(row["line_position"] == "MIDDLE" for row in rows),
            "line_last_occurrences": sum(row["line_position"] in {"LAST", "SINGLE"} for row in rows),
            "paragraph_first_occurrences": sum(int(row["paragraph_first_token"]) for row in rows),
            "paragraph_last_occurrences": sum(int(row["paragraph_last_token"]) for row in rows),
            "section_counts": count_text(str(row["section"]) for row in rows),
            "herbal_occurrences": section_counts["H"],
            "herbal_share": fixed(section_counts["H"] / len(rows)),
            "direct_ychor_predecessor_occurrences": sum(int(row["directly_after_ychor"]) for row in rows),
            "all_formula_predecessor_counts": "|".join(
                f"{key}:{formula_counts[key]}" for key in sorted(formula_counts)
            ) or "NONE",
            "complete_independent_fields": len(complete),
            "anchored_complete_fields": len(anchored),
            "complete_field_channel_counts": count_text(str(row["field_channel"]) for row in complete),
            "complete_independent_axis_counts": axis_count_text(complete),
            "top_exact_left_neighbors": top_neighbors(adj, "LEFT"),
            "top_exact_right_neighbors": top_neighbors(adj, "RIGHT"),
            "ordered_value_follower_hits": value["ordered_value_follower_hits"] if value else 0,
            "ordered_value_exact_right_contexts": value["exact_right_contexts"] if value else 0,
            "ordered_value_descriptive_lift": value["ordered_value_descriptive_lift"] if value else "0.000000",
            "aiin_follower_hits": value["aiin_follower_hits"] if value else 0,
            "aiin_descriptive_lift": value["aiin_descriptive_lift"] if value else "0.000000",
            "analogy_min_edit_distance": analogy["analogy_min_edit_distance"],
            "analogy_neighbor_wholes": analogy["analogy_neighbor_wholes"],
            "analogy_consensus_axes": analogy["analogy_consensus_axes"],
            "analogy_rival_axes": analogy["analogy_rival_axes"],
            "analogy_axis_support": analogy["analogy_axis_support"],
            "analogy_confidence_level": analogy["analogy_confidence_level"],
            "gdt756_candidate_de": prior["gdt756_candidate_de"],
            "gdt758_primary_candidate_de": prior["primary_candidate_de"],
            "gdt758_renderer_value_de": prior["renderer_value_de"],
            "semantic_role": prior["semantic_role"],
            "working_confidence": prior["working_confidence"],
            "alternate_1_de": prior["alternate_1_de"],
            "alternate_2_de": prior["alternate_2_de"],
            "historical_expression_ids": prior["historical_expression_ids"],
            "revision_reason": prior["revision_reason"],
            "positive_evidence": "; ".join(evidence_parts) + "; " + prior["prior_positive_evidence"],
            "counterevidence": prior["counterevidence"],
            "claim_scope": prior["claim_scope"],
            "eva_spelling_used": 0,
            "confirmed_lexeme": 0,
            "component_export_credit": 0,
        })
    return output


def build_revised_body_tokens(
    body_rows: list[dict[str, str]], priors: dict[str, dict[str, str]]
) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for row in body_rows:
        surface = row["surface"]
        prior = priors.get(surface)
        candidate = prior["renderer_value_de"] if prior else row["working_candidate_de"]
        if surface == "s" and row["line_position"] in {"LAST", "SINGLE"}:
            candidate = "zu gleichen Teilen"
        output.append({
            "gdt756_body_token_id": row["gdt756_body_token_id"],
            "page": row["page"],
            "locus": row["locus"],
            "token_ordinal": row["token_ordinal"],
            "body_offset_after_ychor": row["body_offset_after_ychor"],
            "line_position": row["line_position"],
            "surface": surface,
            "reader_exact": row["reader_exact"],
            "independent_axes_at_position": row["independent_axes_at_position"],
            "gdt756_candidate_de": row["working_candidate_de"],
            "gdt758_candidate_de": candidate,
            "candidate_changed": int(prior is not None and candidate != row["working_candidate_de"]),
            "candidate_origin": "GDT758_GLOBAL_FOLLOWER_AUDIT" if prior else row["candidate_source"],
            "working_confidence": prior["working_confidence"] if prior else row["working_confidence"],
            "alternate_1_de": prior["alternate_1_de"] if prior else row["alternate_1_de"],
            "alternate_2_de": prior["alternate_2_de"] if prior else row["alternate_2_de"],
            "exact_whole_default": 1,
            "candidate_not_plaintext": 1,
            "confirmed_lexeme": 0,
            "component_export_credit": 0,
        })
    return output


def apply_span_rules(
    rows: list[dict[str, object]], span_rules: list[dict[str, str]]
) -> tuple[list[str], list[str]]:
    ordered_rules = sorted(
        span_rules, key=lambda row: (-len(row["surfaces"].split("|")), row["span_id"])
    )
    rendered: list[str] = []
    applied: list[str] = []
    index = 0
    while index < len(rows):
        matched = None
        for rule in ordered_rules:
            surfaces = rule["surfaces"].split("|")
            actual = [str(row["surface"]) for row in rows[index:index + len(surfaces)]]
            if actual == surfaces:
                matched = rule
                break
        if matched is None:
            rendered.append(str(rows[index]["gdt758_candidate_de"]))
            index += 1
            continue
        rendered.append(matched["combined_de"])
        applied.append(matched["span_id"])
        index += len(matched["surfaces"].split("|"))
    return rendered, applied


def build_revised_lines(
    line_rows: list[dict[str, str]],
    body_rows: list[dict[str, object]],
    span_rules: list[dict[str, str]],
) -> list[dict[str, object]]:
    by_locus: defaultdict[str, list[dict[str, object]]] = defaultdict(list)
    for row in body_rows:
        by_locus[str(row["locus"])].append(row)
    output: list[dict[str, object]] = []
    for line in line_rows:
        locus = line["locus"]
        rows = sorted(by_locus[locus], key=lambda row: int(row["token_ordinal"]))
        uncomposed = [str(row["gdt758_candidate_de"]) for row in rows]
        composed, span_ids = apply_span_rules(rows, span_rules)
        changed = [row for row in rows if int(row["candidate_changed"])]
        token_map = " | ".join(
            f"{row['surface']}→{row['gdt758_candidate_de']}" for row in rows
        )
        output.append({
            "page": line["page"],
            "locus": locus,
            "section": line["section"],
            "written_line_eva": line["written_line_eva"],
            "token_candidate_map_de": "ychor→ferner/ebenso | " + token_map,
            "uncomposed_candidate_render_de": "ferner/ebenso: " + "; ".join(uncomposed),
            "span_composed_candidate_render_de": "ferner/ebenso: " + "; ".join(composed),
            "recipe_command_rival_render_de": "nimm: " + "; ".join(composed),
            "applied_span_rule_ids": "|".join(span_ids) or "NONE",
            "changed_token_count": len(changed),
            "changed_surfaces": "|".join(str(row["surface"]) for row in changed) or "NONE",
            "body_token_count": len(rows),
            "all_body_tokens_have_candidate_default": int(all(row["gdt758_candidate_de"] for row in rows)),
            "candidate_line_not_plaintext": 1,
            "confirmed_lexeme": 0,
        })
    return output


def md_cell(value: object) -> str:
    return str(value).replace("|", " / ").replace("\n", " ")


def write_dictionary(
    path: Path,
    census: list[dict[str, object]],
    value_rows: list[dict[str, object]],
    revised_lines: list[dict[str, object]],
    historical: list[dict[str, object]],
) -> None:
    s_value = next(row for row in value_rows if row["surface"] == "s")
    lines = [
        "# GDT758 working dictionary", "",
        "## Result", "",
        "The eleven direct `ychor` followers now have global, replaceable complete-form defaults. The largest correction is `s`: the forced `Samen` reading is removed. Its leading role is `je / zu gleichen Teilen`, historically comparable in function to recipe `ana`; a unit sign such as drachm or ounce remains a rival. This is a functional candidate, not a graphic identification.", "",
        f"Across the safe cache the eleven forms contribute {sum(int(row['reader_exact_occurrences']) for row in census)} reader-exact occurrences. Exactly {sum(int(row['direct_ychor_predecessor_occurrences']) for row in census)} are the direct follower positions that opened this pass.", "",
        "## Eleven-whole dictionary", "",
        "| whole | new working default | confidence | global evidence | strongest alternatives |",
        "|---|---|---|---|---|",
    ]
    for row in census:
        evidence = (
            f"n={row['reader_exact_occurrences']}; H={row['herbal_occurrences']}; "
            f"analogy={row['analogy_consensus_axes']}; after ychor={row['direct_ychor_predecessor_occurrences']}"
        )
        lines.append(
            f"| `{row['surface']}` | {md_cell(row['gdt758_primary_candidate_de'])} | "
            f"`{row['working_confidence']}` | {md_cell(evidence)} | "
            f"{md_cell(row['alternate_1_de'])}; {md_cell(row['alternate_2_de'])} |"
        )
    lines.extend([
        "", "## Why `s` changed", "",
        f"`s` has {s_value['ordered_value_follower_hits']}/{s_value['exact_right_contexts']} reader-exact right contexts immediately before the ordered `an/ain/aiin/aiiin` value family (descriptive lift {s_value['ordered_value_descriptive_lift']}). The exact pair `s aiin` alone occurs {s_value['aiin_follower_hits']} times (lift {s_value['aiin_descriptive_lift']}). By hit count, `s` ranks {s_value['ordered_value_hit_count_rank']} among all recurrent exact forms, behind `or` and `ar`; it is therefore a member of a small quantity-introducer ecology, not a unique decoder key.", "",
        "This makes the observed `ychor s om ...` read economically as `ferner/ebenso: je eine Handvoll ...`. Drachm and ounce signs are historically realistic alternatives because medieval measure signs also precede values, but nothing in the EVA shape selects either one.", "",
        "## Concrete corrections", "",
        "- `cthy`: `Wurzel` → `Blattgut`; this restores the independent GDT625 visual/context result.",
        "- `chol`, `qokchol`, `sheol`: invented carriers such as Kraut are removed; only dry, hot-dry and moist/soaked content is spoken.",
        "- `ar`: `erster Teil` → `Anteil`; the first-value claim had no separate support.",
        "- `odol`: the unsupported imperative becomes the nominal `abgemessene Zubereitung`.",
        "- `ols`: generic `Heilmittel` becomes the weak but testable `abgeseihtes Endprodukt`, with oil still a rival.",
        "", "## Revised thirteen-line reader", "",
        "Every written body token retains a default. Exact observed multiword spans may be smoothed once; they do not export component values.", "",
    ])
    for row in revised_lines:
        lines.extend([
            f"### {row['locus']}", "",
            f"EVA: `{row['written_line_eva']}`", "",
            f"Working rendering: {row['span_composed_candidate_render_de']}", "",
            f"Command rival: {row['recipe_command_rival_render_de']}", "",
        ])
    lines.extend([
        "## Historical register control", "",
        f"The compact comparator deck contains {len(historical)} attested expression classes. It licenses candidate categories—parts, measures, hot/dry states, soaking, straining and named preparations—but no Voynich spelling match.", "",
        "## Boundary", "",
        "These are deliberately concrete working defaults. None is a confirmed lexeme, sound, Latin abbreviation or plaintext clause. The purpose is to make upcoming pages capable of replacing a candidate rather than allowing an empty generic rendering to survive every contradiction.",
    ])
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def build(output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    priors_rows = read_tsv(SRC / "FOLLOWER_CANDIDATE_PRIORS.tsv")
    span_rules = read_tsv(SRC / "YCHOR_EXACT_SPAN_RENDER_RULES.tsv")
    inventory = read_tsv(ROOT / G754_INVENTORY_REL)
    formula_rows = read_tsv(ROOT / G757_FORMULAE_REL)
    body_rows = read_tsv(ROOT / G756_BODY_REL)
    line_rows = read_tsv(ROOT / G756_LINES_REL)
    bank_rows = read_tsv(ROOT / G755_BANK_REL)
    source_rows = read_tsv(ROOT / G755_SOURCES_REL)
    cthy_rows = read_tsv(ROOT / G625_TERM_REL)
    clause_rows = read_tsv(ROOT / G629_CLAUSE_REL)
    priors = {row["surface"]: row for row in priors_rows}
    formula_forms = {row["surface"] for row in formula_rows}
    suspect_surfaces = {row["surface"] for row in inventory} | set(TARGET_FORMS)

    if tuple(row["surface"] for row in priors_rows) != TARGET_FORMS:
        raise AssertionError("candidate prior order or target universe changed")
    if len(priors) != 11 or len(span_rules) != 8:
        raise AssertionError("eleven priors and eight span rules required")
    if len(inventory) != 172 or len(formula_forms) != 11:
        raise AssertionError("fixed suspect or formula universe changed")
    if len(body_rows) != 71 or len(line_rows) != 13:
        raise AssertionError("fixed ychor renderer universe changed")
    direct_followers = Counter(row["immediate_follower_surface"] for row in line_rows)
    if set(direct_followers) != set(TARGET_FORMS) or sum(direct_followers.values()) != 13:
        raise AssertionError("direct ychor follower universe changed")

    context, line_meta, guard = g756.g755.g753.g752.g751.load_context()
    rules = g756.g755.g753.g752.g744.load_channel_rules()
    pair_data = pair_universe(context)
    occurrences = build_occurrences(
        context, line_meta, rules, suspect_surfaces, formula_forms, priors
    )
    adjacency = build_adjacency(pair_data, formula_forms)
    value_comparator = build_value_comparator(pair_data, set(TARGET_FORMS))
    analogy_deck, analogy_summaries, analogy_diagnostics = g745.build_analogy_deck(
        set(TARGET_FORMS)
    )
    for number, row in enumerate(analogy_deck, start=1):
        row["analogy_id"] = f"G758-A{number:04d}"
    historical = build_historical_comparators(
        priors, bank_rows, source_rows
    )
    cthy_legacy = next(row for row in cthy_rows if row["surface"] == "cthy")
    exact_part_clauses = sum(
        row["evidence_class"] == "TRIPLE_EXACT_COMPLETE_CLAUSE"
        for row in clause_rows
    )
    census = build_census(
        occurrences, adjacency, analogy_summaries, priors,
        value_comparator, cthy_legacy, exact_part_clauses,
    )
    revised_body = build_revised_body_tokens(body_rows, priors)
    revised_lines = build_revised_lines(line_rows, revised_body, span_rules)

    s_value = next(row for row in value_comparator if row["surface"] == "s")
    observed_counts = Counter(str(row["surface"]) for row in occurrences)
    expected_counts = {
        "ar": 242, "chol": 303, "chor": 176, "chshoty": 1,
        "cthy": 85, "odol": 2, "oky": 80, "ols": 12,
        "qokchol": 15, "s": 154, "sheol": 71,
    }
    if observed_counts != Counter(expected_counts):
        raise AssertionError(f"target occurrence universe changed: {observed_counts}")
    if len(occurrences) != 1141:
        raise AssertionError("fixed 1141-occurrence census changed")
    if sum(int(row["directly_after_ychor"]) for row in occurrences) != 13:
        raise AssertionError("fixed thirteen direct ychor positions changed")
    if (
        s_value["ordered_value_follower_hits"] != 25
        or s_value["exact_right_contexts"] != 99
        or s_value["aiin_follower_hits"] != 23
        or s_value["ordered_value_hit_count_rank"] != 3
    ):
        raise AssertionError("s ordered-value geometry changed")
    if len(analogy_deck) != 80 or exact_part_clauses != 2:
        raise AssertionError("analogy or exact-clause evidence changed")
    if sum(int(row["candidate_changed"]) for row in revised_body) != 23:
        raise AssertionError("expected 23 revised ychor body token positions")
    if not all(int(row["all_body_tokens_have_candidate_default"]) for row in revised_lines):
        raise AssertionError("revised renderer contains a missing default")
    used_span_ids = {
        span_id for row in revised_lines
        for span_id in values(str(row["applied_span_rule_ids"]))
    }
    if used_span_ids != {row["span_id"] for row in span_rules}:
        raise AssertionError("every exact span rule must match the ychor reader")

    write_tsv(output_dir / OUTPUT_NAMES[0], occurrences, list(occurrences[0]))
    write_tsv(output_dir / OUTPUT_NAMES[1], census, list(census[0]))
    write_tsv(output_dir / OUTPUT_NAMES[2], analogy_deck, list(analogy_deck[0]))
    write_tsv(output_dir / OUTPUT_NAMES[3], adjacency, list(adjacency[0]))
    write_tsv(output_dir / OUTPUT_NAMES[4], value_comparator, list(value_comparator[0]))
    write_tsv(output_dir / OUTPUT_NAMES[5], historical, list(historical[0]))
    write_tsv(output_dir / OUTPUT_NAMES[6], revised_body, list(revised_body[0]))
    write_tsv(output_dir / OUTPUT_NAMES[7], revised_lines, list(revised_lines[0]))
    write_dictionary(
        output_dir / OUTPUT_NAMES[8], census, value_comparator,
        revised_lines, historical,
    )

    confidence_counts = Counter(row["working_confidence"] for row in census)
    result = {
        "schema": "GDT758_RESULT_V1",
        "status": STATUS,
        "scope": {
            "target_complete_forms": len(TARGET_FORMS),
            "reader_exact_occurrences": len(occurrences),
            "reader_exact_pages": len({str(row["page"]) for row in occurrences}),
            "reader_exact_loci": len({str(row["locus"]) for row in occurrences}),
            "direct_ychor_follower_positions": sum(int(row["directly_after_ychor"]) for row in occurrences),
            "clean_whole_analogy_relations": len(analogy_deck),
            "exact_adjacency_relations": len(adjacency),
            "ordered_value_comparator_forms": len(value_comparator),
            "historical_expression_classes": len(historical),
            "revised_ychor_body_tokens": len(revised_body),
            "changed_ychor_body_tokens": sum(int(row["candidate_changed"]) for row in revised_body),
            "revised_ychor_lines": len(revised_lines),
            "exact_span_render_rules": len(span_rules),
        },
        "primary_working_dictionary": {
            row["surface"]: row["gdt758_primary_candidate_de"] for row in census
        },
        "confidence_counts": dict(sorted(confidence_counts.items())),
        "strongest_correction": {
            "surface": "s",
            "retired_candidate": "Samen",
            "new_candidate": "je / zu gleichen Teilen",
            "historical_functional_comparator": "ana",
            "ordered_value_follower_hits": int(s_value["ordered_value_follower_hits"]),
            "exact_right_contexts": int(s_value["exact_right_contexts"]),
            "ordered_value_lift": float(s_value["ordered_value_descriptive_lift"]),
            "s_aiin_exact_pairs": int(s_value["aiin_follower_hits"]),
            "s_aiin_lift": float(s_value["aiin_descriptive_lift"]),
            "hit_count_rank": int(s_value["ordered_value_hit_count_rank"]),
            "not_unique_value_introducer": True,
        },
        "cross_pass_repairs": {
            "cthy": "Wurzel -> Blattgut",
            "chol": "trockenes Kraut -> trocken/getrocknet",
            "qokchol": "heiss getrocknetes Kraut -> erhitzt und getrocknet",
            "sheol": "eingeweichtes Kraut -> feucht/eingeweicht",
            "ar": "erster Teil -> Teil/Anteil",
            "odol": "miss den Arzneistoff ab -> abgemessene Zubereitung",
            "ols": "Heilmittel -> abgeseihtes Endprodukt",
        },
        "analogy_diagnostics": analogy_diagnostics,
        "legacy_evidence": {
            "gdt625_cthy_zl3b_occurrences": int(cthy_legacy["zl3b_occurrences"]),
            "gdt625_cthy_herbal_occurrences": int(cthy_legacy["herbal_occurrences"]),
            "gdt629_triple_exact_chor_chol_daiin_clauses": exact_part_clauses,
        },
        "guard": guard,
        "claim_boundary": {
            "confirmed_lexemes": 0,
            "confirmed_plaintext_clauses": 0,
            "historical_graphic_matches": 0,
            "component_values": 0,
            "new_pages": 0,
            "new_images": 0,
            "new_transcriptions": 0,
            "f84_accessed": False,
            "f84r_accessed": False,
        },
    }
    (output_dir / OUTPUT_NAMES[9]).write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_ARTIFACTS)
    result = build(parser.parse_args().output_dir)
    print(json.dumps({
        "status": result["status"],
        "scope": result["scope"],
        "strongest_correction": result["strongest_correction"],
    }, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
