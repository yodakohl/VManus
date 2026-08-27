#!/usr/bin/env python3
"""Close aiicthy through the old aiin/saiin/saii renderer square."""

from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt536_aii_renderer_square_aiicthy_closure"
OUT = BASE / "artifacts"
OLD = (
    ROOT
    / "experiments/yolo/gdt407_unified_twenty_six_page_workshop_edition/artifacts"
    / "gdt407_4576_running_event_edition.tsv"
)
CURRENT_EVENTS = (
    ROOT
    / "experiments/yolo/gdt516_thirty_page_new_surface_family_consolidation/artifacts"
    / "gdt516_597_contextualized_event_edition.tsv"
)
CANDIDATES = (
    ROOT
    / "experiments/yolo/gdt529_nearest_terminal_m_square/artifacts"
    / "gdt529_candidate_score_atlas.tsv"
)
CURRENT_WORKING = (
    ROOT
    / "experiments/yolo/gdt535_same_statement_q_null_qef_closure/artifacts"
    / "gdt535_159_working_revision.tsv"
)
CURRENT_RESULT = (
    ROOT
    / "experiments/yolo/gdt535_same_statement_q_null_qef_closure/artifacts"
    / "gdt535_result.json"
)

TARGET_SURFACE = "aiicthy"
TARGET_EVENT = "G515-E0253"
TARGET_PAGE = "f31r"
SELECTED_RECIPE = "AIIN+CH+T+Y"
WORKING_LITERAL_DE = "WERT · NEHMEN · EINSTELLEN · POSTEN"
WORKING_PHRASE_DE = "Den Wert nehmen, einstellen und posten."


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=fields, delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows({field: row.get(field, "") for field in fields} for row in rows)


def write_json(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def old_surface_index(rows: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    index: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        index[row["surface"]].append(row)
    return index


def recipe_counts(rows: list[dict[str, str]]) -> Counter:
    return Counter(row["component_recipe"] for row in rows)


def joined_counter(counter: Counter) -> str:
    return "|".join(f"{key}:{counter[key]}" for key in sorted(counter))


def profile(surface: str, rows: list[dict[str, str]]) -> dict:
    recipes = recipe_counts(rows)
    return {
        "surface": surface,
        "event_count": len(rows),
        "physical_page_count": len({row["physical_page"] for row in rows}),
        "physical_pages": "|".join(sorted({row["physical_page"] for row in rows})),
        "registers": "|".join(sorted({row["register"] for row in rows})),
        "recipes": joined_counter(recipes),
        "invariant_recipe": next(iter(recipes)) if len(recipes) == 1 else "AMBIGUOUS",
    }


def aii_right_context(surface: str) -> str:
    match = re.search(r"aii(?!n)", surface)
    if not match:
        return "NONE"
    remainder = surface[match.end() :]
    return remainder if remainder else "RIGHT_EDGE"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    old = read_tsv(OLD)
    current_events = read_tsv(CURRENT_EVENTS)
    candidates = [
        row for row in read_tsv(CANDIDATES) if row["surface"] == TARGET_SURFACE
    ]
    current = read_tsv(CURRENT_WORKING)
    inherited_result = json.loads(CURRENT_RESULT.read_text(encoding="utf-8"))
    old_by_surface = old_surface_index(old)

    # Three observed corners and the inferred fourth corner of one renderer square.
    square_specs = [
        ("BASE_PLUS_N", "aiin", "NO", "PLUS_N", "AIIN", "OBSERVED_OLD_EXACT"),
        ("S_PREFIX_PLUS_N", "saiin", "YES", "PLUS_N", "S+AIIN", "OBSERVED_OLD_EXACT"),
        ("S_PREFIX_MINUS_N", "saii", "YES", "MINUS_N", "S+AIIN", "OBSERVED_OLD_EXACT"),
        ("BASE_MINUS_N", "aii", "NO", "MINUS_N", "AIIN", "INFERRED_MISSING_CORNER"),
    ]
    square_rows = []
    for cell, surface, s_prefix, n_state, recipe, state in square_specs:
        rows = old_by_surface.get(surface, [])
        recipes = recipe_counts(rows)
        square_rows.append(
            {
                "cell": cell,
                "surface": surface,
                "s_prefix": s_prefix,
                "terminal_n_state": n_state,
                "event_count": len(rows),
                "physical_page_count": len({row["physical_page"] for row in rows}),
                "physical_pages": "|".join(sorted({row["physical_page"] for row in rows})),
                "registers": "|".join(sorted({row["register"] for row in rows})),
                "observed_recipes": joined_counter(recipes),
                "working_recipe": recipe,
                "cell_state": state,
                "relation": (
                    "REMOVE_s_AND_S_FROM_saii"
                    if cell == "BASE_MINUS_N"
                    else "EXACT_SQUARE_CORNER"
                ),
            }
        )

    # Keep the deletion narrow: every exact terminal-n neighbour stays visible.
    terminal_n_rows = []
    for long_surface in sorted(old_by_surface):
        if not long_surface.endswith("n"):
            continue
        short_surface = long_surface[:-1]
        if short_surface not in old_by_surface:
            continue
        long_recipes = recipe_counts(old_by_surface[long_surface])
        short_recipes = recipe_counts(old_by_surface[short_surface])
        common = sorted(set(long_recipes) & set(short_recipes))
        terminal_n_rows.append(
            {
                "long_surface": long_surface,
                "short_surface": short_surface,
                "long_event_count": len(old_by_surface[long_surface]),
                "short_event_count": len(old_by_surface[short_surface]),
                "long_recipes": joined_counter(long_recipes),
                "short_recipes": joined_counter(short_recipes),
                "common_recipes": "|".join(common) if common else "NONE",
                "same_recipe": "YES" if common else "NO",
                "relation": (
                    "SELECTED_S_AIIN_RENDERER_SHORTENING"
                    if (long_surface, short_surface) == ("saiin", "saii")
                    else "CONTRARY_TERMINAL_N_CONTROL"
                ),
            }
        )

    # The left edge is separately real, but explicitly not universal.
    s_prefix_rows = []
    for base_surface in sorted(old_by_surface):
        prefixed_surface = "s" + base_surface
        if prefixed_surface not in old_by_surface:
            continue
        base_recipes = recipe_counts(old_by_surface[base_surface])
        prefixed_recipes = recipe_counts(old_by_surface[prefixed_surface])
        expected = {"S+" + recipe for recipe in base_recipes}
        common = sorted(expected & set(prefixed_recipes))
        s_prefix_rows.append(
            {
                "base_surface": base_surface,
                "prefixed_surface": prefixed_surface,
                "base_event_count": len(old_by_surface[base_surface]),
                "prefixed_event_count": len(old_by_surface[prefixed_surface]),
                "base_recipes": joined_counter(base_recipes),
                "prefixed_recipes": joined_counter(prefixed_recipes),
                "expected_prefixed_recipes": "|".join(sorted(expected)),
                "matching_recipes": "|".join(common) if common else "NONE",
                "literal_s_prefix_match": "YES" if common else "NO",
                "relation": (
                    "SELECTED_AIIN_S_PREFIX_EDGE"
                    if base_surface == "aiin"
                    else "OLD_S_PREFIX_CONTROL"
                ),
            }
        )

    cthy_rows = []
    for row in old_by_surface.get("cthy", []):
        if row["component_recipe"] != "CH+T+Y":
            continue
        cthy_rows.append(
            {
                "event_id": row["global_running_event_id"],
                "physical_page": row["physical_page"],
                "register": row["register"],
                "locus": row["locus"],
                "statement_id": row["source_statement_id"],
                "surface": row["surface"],
                "recipe": row["component_recipe"],
                "relation": "EXACT_RIGHT_CTHY_CARD",
            }
        )

    # Show every old/current short aii context so this cannot become a blanket rule.
    aii_context_rows = []
    for surface in sorted(old_by_surface):
        if not re.search(r"aii(?!n)", surface):
            continue
        p = profile(surface, old_by_surface[surface])
        aii_context_rows.append(
            {
                "corpus": "OLD26",
                **p,
                "right_context_after_aii": aii_right_context(surface),
                "relation": (
                    "SQUARE_SHORT_CORNER" if surface == "saii" else "CONTEXT_CONTROL"
                ),
            }
        )
    for row in current:
        if not re.search(r"aii(?!n)", row["surface"]):
            continue
        aii_context_rows.append(
            {
                "corpus": "CURRENT_NEW159",
                "surface": row["surface"],
                "event_count": row["occurrence_count"],
                "physical_page_count": len(row["physical_pages"].split("|")),
                "physical_pages": row["physical_pages"],
                "registers": "CURRENT30",
                "recipes": row["gdt535_working_recipe"] + ":" + row["occurrence_count"],
                "invariant_recipe": row["gdt535_working_recipe"],
                "right_context_after_aii": aii_right_context(row["surface"]),
                "relation": "TARGET_BEFORE_GDT536" if row["surface"] == TARGET_SURFACE else "CONTEXT_CONTROL",
            }
        )

    # The target page itself contains several independently carried value cards.
    current_working_by_surface = {row["surface"]: row for row in current}
    target_page_rows = []
    for row in current_events:
        if row["physical_page"] != TARGET_PAGE or "aii" not in row["surface"]:
            continue
        if row["event_id"] == TARGET_EVENT:
            live_recipe = SELECTED_RECIPE
            relation = "TARGET_SELECTED"
        elif row["surface"] in current_working_by_surface:
            live_recipe = current_working_by_surface[row["surface"]]["gdt535_working_recipe"]
            relation = "CURRENT_WORKING_AII_CONTEXT"
        else:
            live_recipe = row["gdt516_context_recipe"]
            relation = "LOCKED_OR_CONTEXTUAL_AII_CARRIER"
        target_page_rows.append(
            {
                "event_id": row["event_id"],
                "locus": row["locus"],
                "statement_id": row["statement_id"],
                "card_ordinal_in_statement": row["card_ordinal_in_statement"],
                "surface": row["surface"],
                "gdt516_recipe": row["gdt516_context_recipe"],
                "live_working_recipe": live_recipe,
                "relation": relation,
            }
        )

    comparison_rows = []
    matching_candidates = []
    for row in candidates:
        atoms = row["candidate_recipe"].split("+")
        aii_match = atoms[:1] == ["AIIN"]
        cthy_match = atoms[-3:] == ["CH", "T", "Y"]
        both = aii_match and cthy_match
        if both:
            matching_candidates.append(row)
        if both:
            decision = "SELECT_UNIQUE_SQUARE_PLUS_EXACT_TAIL"
        elif aii_match:
            decision = "KEEP_ALTERNATE__RIGHT_TAIL_NOT_EXACT_CTHY"
        elif cthy_match:
            decision = "KEEP_ALTERNATE__LEFT_BLOCK_NOT_SQUARE_AIIN"
        else:
            decision = "KEEP_ALTERNATE__NEITHER_EXACT_BLOCK_MATCHES"
        comparison_rows.append(
            {
                "surface": TARGET_SURFACE,
                "candidate_recipe": row["candidate_recipe"],
                "gdt529_rank": row["gdt529_rank"],
                "gdt529_score": row["gdt529_score"],
                "aii_square_recipe": "AIIN",
                "matches_aii_square": "YES" if aii_match else "NO",
                "cthy_exact_recipe": "CH+T+Y",
                "matches_exact_cthy_tail": "YES" if cthy_match else "NO",
                "matches_both_blocks": "YES" if both else "NO",
                "gdt536_context_rank": "1" if both else "ALTERNATE",
                "decision": decision,
            }
        )

    certificate_rows = [
        {"step": 1, "surface": "aiin", "recipe": "AIIN", "support": "55 events / 15 pages / 4 registers", "operation": "exact unprefixed plus-n corner"},
        {"step": 2, "surface": "saiin", "recipe": "S+AIIN", "support": "20 events / 10 pages / 3 registers", "operation": "add visible s and recipe S"},
        {"step": 3, "surface": "saii", "recipe": "S+AIIN", "support": "1 event on f83r", "operation": "remove terminal n with recipe unchanged in this exact family"},
        {"step": 4, "surface": "aii", "recipe": "AIIN", "support": "missing fourth square corner", "operation": "remove the matched leading s/S block from saii"},
        {"step": 5, "surface": "cthy", "recipe": "CH+T+Y", "support": "13 events / 6 pages", "operation": "append exact old right card"},
        {"step": 6, "surface": TARGET_SURFACE, "recipe": SELECTED_RECIPE, "support": "unique matching GDT529 candidate; global rank 1", "operation": "compose aii | cthy"},
    ]

    edition = []
    for row in current:
        if row["surface"] == TARGET_SURFACE:
            recipe = SELECTED_RECIPE
            candidate_rank = "1"
            context_rank = "1"
            literal = WORKING_LITERAL_DE
            phrase = WORKING_PHRASE_DE
            evidence = (
                "aiin=AIIN 55x; saiin=S+AIIN 20x; saii=S+AIIN 1x; "
                "inferred aii=AIIN; exact cthy=CH+T+Y 13x"
            )
            policy = "GDT536_AII_RENDERER_SQUARE_PLUS_EXACT_CTHY"
            resolution = "RESOLVED_BY_AII_RENDERER_SQUARE_AND_EXACT_CTHY"
        else:
            recipe = row["gdt535_working_recipe"]
            candidate_rank = row["gdt535_gdt529_candidate_rank"]
            context_rank = "INHERITED"
            literal = row["gdt535_literal_reading_de"]
            phrase = row["gdt535_short_phrase_de"]
            evidence = "NO_SELECTED_AII_SQUARE_REVISION"
            policy = "INHERIT_GDT535_WORKING_RECIPE"
            resolution = row["gdt535_resolution_status"]
        edition.append(
            {
                **row,
                "gdt536_working_recipe": recipe,
                "gdt536_gdt529_candidate_rank": candidate_rank,
                "gdt536_renderer_square_rank": context_rank,
                "gdt536_literal_reading_de": literal,
                "gdt536_short_phrase_de": phrase,
                "gdt536_evidence": evidence,
                "gdt536_policy": policy,
                "gdt536_resolution_status": resolution,
            }
        )

    unresolved = [row for row in edition if row["gdt536_resolution_status"] == "UNRESOLVED_NON_TOP1"]
    recipe_changes = [row for row in edition if row["gdt535_working_recipe"] != row["gdt536_working_recipe"]]
    rank_distribution = Counter(row["gdt536_gdt529_candidate_rank"] for row in edition)
    s_prefix_matches = sum(row["literal_s_prefix_match"] == "YES" for row in s_prefix_rows)
    terminal_same = sum(row["same_recipe"] == "YES" for row in terminal_n_rows)
    selected_candidate = matching_candidates[0] if len(matching_candidates) == 1 else None
    exact_target_page_aiin = sum(row["surface"] == "aiin" and row["live_working_recipe"] == "AIIN" for row in target_page_rows)
    exact_target_page_daiin = sum(row["surface"] == "daiin" and row["live_working_recipe"] == "AIIN" for row in target_page_rows)

    status = (
        "PASS_AII_RENDERER_SQUARE_aiicthy_CLOSURE"
        if len(old) == 4576
        and len({row["surface"] for row in old}) == 1558
        and len(current_events) == 597
        and len(current) == 159
        and recipe_counts(old_by_surface["aiin"]) == Counter({"AIIN": 55})
        and recipe_counts(old_by_surface["saiin"]) == Counter({"S+AIIN": 20})
        and recipe_counts(old_by_surface["saii"]) == Counter({"S+AIIN": 1})
        and "aii" not in old_by_surface
        and recipe_counts(old_by_surface["cthy"]) == Counter({"CH+T+Y": 13})
        and len(terminal_n_rows) == 3
        and terminal_same == 1
        and any(row["long_surface"] == "saiin" and row["short_surface"] == "saii" and row["same_recipe"] == "YES" for row in terminal_n_rows)
        and len(s_prefix_rows) == 47
        and s_prefix_matches == 25
        and any(row["base_surface"] == "aiin" and row["prefixed_surface"] == "saiin" and row["literal_s_prefix_match"] == "YES" for row in s_prefix_rows)
        and len(cthy_rows) == 13
        and len(candidates) == 12
        and selected_candidate is not None
        and selected_candidate["candidate_recipe"] == SELECTED_RECIPE
        and selected_candidate["gdt529_rank"] == "1"
        and exact_target_page_aiin == 4
        and exact_target_page_daiin == 4
        and len(recipe_changes) == 1
        and recipe_changes[0]["surface"] == TARGET_SURFACE
        and len(unresolved) == 0
        else "FAIL_AII_RENDERER_SQUARE_GATE"
    )

    result = {
        "experiment_id": "GDT536",
        "status": status,
        "claim_ceiling": "EXPLORATORY_FAMILY_SPECIFIC_AII_VALUE_RENDERER_AND_COMPOSITIONAL_CLOSURE__NO_GLOBAL_AII_OR_N_NULL_RULE_OR_CONFIRMED_PLAINTEXT",
        "old_source_metrics": {
            "event_count": len(old),
            "surface_type_count": len(old_by_surface),
            "aiin_event_count": len(old_by_surface["aiin"]),
            "saiin_event_count": len(old_by_surface["saiin"]),
            "saii_event_count": len(old_by_surface["saii"]),
            "aii_event_count": len(old_by_surface.get("aii", [])),
            "cthy_event_count": len(cthy_rows),
            "terminal_n_neighbour_pair_count": len(terminal_n_rows),
            "same_recipe_terminal_n_pair_count": terminal_same,
            "s_prefix_pair_count": len(s_prefix_rows),
            "literal_s_prefix_match_count": s_prefix_matches,
        },
        "renderer_square": {
            "observed_corner_count": 3,
            "inferred_corner_count": 1,
            "inferred_surface": "aii",
            "inferred_recipe": "AIIN",
            "specific_family": "aiin/saiin/saii",
        },
        "selected_resolution_count": 1,
        "selected_resolution": {
            "surface": TARGET_SURFACE,
            "event_id": TARGET_EVENT,
            "physical_page": TARGET_PAGE,
            "recipe": SELECTED_RECIPE,
            "global_candidate_rank": 1,
            "renderer_square_rank": 1,
            "left_card": "aii=AIIN",
            "right_card": "cthy=CH+T+Y",
            "target_page_exact_aiin_count": exact_target_page_aiin,
            "target_page_daiin_as_AIIN_count": exact_target_page_daiin,
            "working_literal_de": WORKING_LITERAL_DE,
            "working_phrase_de": WORKING_PHRASE_DE,
        },
        "candidate_comparison": {
            "candidate_count": len(candidates),
            "square_and_tail_match_count": len(matching_candidates),
            "selected_recipe": SELECTED_RECIPE,
        },
        "inherited_candidate_metrics_unchanged": inherited_result["inherited_candidate_metrics_unchanged"],
        "working_candidate_rank_distribution": dict(sorted(rank_distribution.items())),
        "working_resolved_surface_count": len(edition) - len(unresolved),
        "remaining_unresolved_surface_count": len(unresolved),
        "remaining_unresolved_surfaces": [row["surface"] for row in unresolved],
        "guard": "USE_THE_EXACT_aiin_saiin_saii_SQUARE_FOR_aii_ONLY_WHEN_COMPOSED_WITH_THE_EXACT_cthy_CARD__KEEP_OTHER_aii_CONTEXTS_DISTINCT__NO_NEW_PAGES",
    }

    write_tsv(OUT / "gdt536_159_working_revision.tsv", edition, list(edition[0]))
    write_tsv(OUT / "gdt536_aii_renderer_square.tsv", square_rows, list(square_rows[0]))
    write_tsv(OUT / "gdt536_terminal_n_pair_control.tsv", terminal_n_rows, list(terminal_n_rows[0]))
    write_tsv(OUT / "gdt536_s_prefix_pair_control.tsv", s_prefix_rows, list(s_prefix_rows[0]))
    write_tsv(OUT / "gdt536_cthy_exact_carriers.tsv", cthy_rows, list(cthy_rows[0]))
    write_tsv(OUT / "gdt536_aii_context_control.tsv", aii_context_rows, list(aii_context_rows[0]))
    write_tsv(OUT / "gdt536_f31r_aii_family_atlas.tsv", target_page_rows, list(target_page_rows[0]))
    write_tsv(OUT / "gdt536_aiicthy_candidate_comparison.tsv", comparison_rows, list(comparison_rows[0]))
    write_tsv(OUT / "gdt536_aiicthy_resolution_certificate.tsv", certificate_rows, list(certificate_rows[0]))
    write_tsv(OUT / "gdt536_remaining_unresolved_atlas.tsv", unresolved, list(edition[0]))
    write_json(OUT / "gdt536_result.json", result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if status.startswith("PASS_") else 1


if __name__ == "__main__":
    raise SystemExit(main())
