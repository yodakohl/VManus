#!/usr/bin/env python3
"""Resolve qef through its unanimous same-statement noncarrier-q family."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt535_same_statement_q_null_qef_closure"
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
Q_SIGNATURES = (
    ROOT
    / "experiments/yolo/gdt522_local_edit_analogy_license_reranker/artifacts"
    / "gdt522_local_edit_analogy_atlas.tsv"
)
Q_CONTEXT = (
    ROOT
    / "experiments/yolo/gdt523_path_local_null_renderer_license/artifacts"
    / "gdt523_left_null_atom_context_atlas.tsv"
)
Q_TRADEOFF = (
    ROOT
    / "experiments/yolo/gdt523_path_local_null_renderer_license/artifacts"
    / "gdt523_q_path_tradeoff_atlas.tsv"
)
CANDIDATES = (
    ROOT
    / "experiments/yolo/gdt529_nearest_terminal_m_square/artifacts"
    / "gdt529_candidate_score_atlas.tsv"
)
CURRENT_WORKING = (
    ROOT
    / "experiments/yolo/gdt534_third_rung_cheeeky_grade_ladder/artifacts"
    / "gdt534_159_working_revision.tsv"
)
CURRENT_RESULT = (
    ROOT
    / "experiments/yolo/gdt534_third_rung_cheeeky_grade_ladder/artifacts"
    / "gdt534_result.json"
)

TARGET_SURFACE = "qef"
TARGET_EVENT = "G515-E0165"
TARGET_STATEMENT = "G515-S010"
SELECTED_RECIPE = "E+LOCAL_CHAR_F"
RIVAL_RECIPE = "CARRIER_Q+E+LOCAL_CHAR_F"
WORKING_LITERAL_DE = "[E:STEUERUNG=GRAD I] · [LOCAL_CHAR_F:STEUERUNG=HIER]"
WORKING_PHRASE_DE = "Hier auf Grad I."


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


def q_role(recipe: str) -> str:
    atoms = recipe.split("+") if recipe else []
    return "CARRIER_Q" if atoms and atoms[0] == "CARRIER_Q" else "NONCARRIER_Q"


def statement_q_atlas(
    rows: list[dict[str, str]],
    corpus: str,
    statement_field: str,
    event_field: str,
    recipe_field: str,
) -> tuple[list[dict], list[dict], dict[str, list[dict]]]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        if not row["surface"].startswith("q"):
            continue
        grouped[row[statement_field]].append(
            {
                "event_id": row[event_field],
                "surface": row["surface"],
                "recipe": row[recipe_field],
                "q_role": q_role(row[recipe_field]),
                "physical_page": row["physical_page"],
                "locus": row["locus"],
            }
        )

    profiles = []
    neighbour_votes = []
    for statement_id, events in sorted(grouped.items()):
        roles = Counter(row["q_role"] for row in events)
        profiles.append(
            {
                "corpus": corpus,
                "statement_id": statement_id,
                "physical_pages": "|".join(sorted({row["physical_page"] for row in events})),
                "q_event_count": len(events),
                "carrier_q_count": roles["CARRIER_Q"],
                "noncarrier_q_count": roles["NONCARRIER_Q"],
                "unanimous_role": next(iter(roles)) if len(roles) == 1 else "MIXED",
                "event_ids": "|".join(row["event_id"] for row in events),
                "surfaces": "|".join(row["surface"] for row in events),
                "recipes": "|".join(row["recipe"] for row in events),
            }
        )
        if len(events) < 2:
            continue
        for index, event in enumerate(events):
            others = [row for other_index, row in enumerate(events) if other_index != index]
            other_roles = {row["q_role"] for row in others}
            if len(other_roles) != 1:
                continue
            predicted = next(iter(other_roles))
            neighbour_votes.append(
                {
                    "corpus": corpus,
                    "statement_id": statement_id,
                    "target_event_id": event["event_id"],
                    "target_surface": event["surface"],
                    "target_recipe": event["recipe"],
                    "actual_q_role": event["q_role"],
                    "other_q_event_count": len(others),
                    "predicted_q_role": predicted,
                    "prediction_correct": "YES" if event["q_role"] == predicted else "NO",
                    "other_event_ids": "|".join(row["event_id"] for row in others),
                    "other_surfaces": "|".join(row["surface"] for row in others),
                    "other_recipes": "|".join(row["recipe"] for row in others),
                    "relation": (
                        "TARGET_QEF_NEIGHBOUR_VOTE"
                        if event["event_id"] == TARGET_EVENT
                        else "STATEMENT_Q_ROLE_NEIGHBOUR_VOTE"
                    ),
                }
            )
    return profiles, neighbour_votes, grouped


def vote_metrics(
    profiles: list[dict], votes: list[dict], grouped: dict[str, list[dict]]
) -> dict:
    multi = [row for row in profiles if int(row["q_event_count"]) >= 2]
    return {
        "q_event_count": sum(len(rows) for rows in grouped.values()),
        "q_statement_count": len(grouped),
        "multi_q_statement_count": len(multi),
        "fully_unanimous_multi_q_statement_count": sum(
            row["unanimous_role"] != "MIXED" for row in multi
        ),
        "neighbour_vote_scored_event_count": len(votes),
        "neighbour_vote_correct_event_count": sum(
            row["prediction_correct"] == "YES" for row in votes
        ),
        "neighbour_vote_accuracy": (
            sum(row["prediction_correct"] == "YES" for row in votes) / len(votes)
            if votes
            else 0.0
        ),
        "role_counts": dict(
            sorted(
                Counter(
                    event["q_role"]
                    for events in grouped.values()
                    for event in events
                ).items()
            )
        ),
    }


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    old = read_tsv(OLD)
    current_events = read_tsv(CURRENT_EVENTS)
    signatures = read_tsv(Q_SIGNATURES)
    context_rows = read_tsv(Q_CONTEXT)
    tradeoff_rows = [row for row in read_tsv(Q_TRADEOFF) if row["surface"] == TARGET_SURFACE]
    candidate_rows = [
        row for row in read_tsv(CANDIDATES) if row["surface"] == TARGET_SURFACE
    ]
    current = read_tsv(CURRENT_WORKING)
    inherited_result = json.loads(CURRENT_RESULT.read_text(encoding="utf-8"))

    old_profiles, old_votes, old_grouped = statement_q_atlas(
        old,
        "OLD26",
        "source_statement_id",
        "global_running_event_id",
        "component_recipe",
    )
    current_profiles, current_votes, current_grouped = statement_q_atlas(
        current_events,
        "CURRENT4",
        "statement_id",
        "event_id",
        "gdt516_context_recipe",
    )
    old_metrics = vote_metrics(old_profiles, old_votes, old_grouped)
    current_metrics = vote_metrics(current_profiles, current_votes, current_grouped)

    target_event = next(row for row in current_events if row["event_id"] == TARGET_EVENT)
    target_statement_rows = [
        row for row in current_events if row["statement_id"] == TARGET_STATEMENT
    ]
    target_q_events = current_grouped[TARGET_STATEMENT]
    other_target_q_events = [row for row in target_q_events if row["event_id"] != TARGET_EVENT]
    other_roles = {row["q_role"] for row in other_target_q_events}
    target_vote = next(row for row in current_votes if row["target_event_id"] == TARGET_EVENT)

    target_statement_atlas = []
    for row in target_statement_rows:
        target_statement_atlas.append(
            {
                "event_id": row["event_id"],
                "physical_page": row["physical_page"],
                "locus": row["locus"],
                "card_ordinal_in_statement": row["card_ordinal_in_statement"],
                "surface": row["surface"],
                "recipe": row["gdt516_context_recipe"],
                "literal_reading_de": row["gdt516_literal_reading_de"],
                "starts_q": "YES" if row["surface"].startswith("q") else "NO",
                "q_role": q_role(row["gdt516_context_recipe"])
                if row["surface"].startswith("q")
                else "NOT_Q_INITIAL",
                "relation": "TARGET" if row["event_id"] == TARGET_EVENT else "SAME_STATEMENT",
            }
        )

    target_q_atlas = []
    for row in target_q_events:
        target_q_atlas.append(
            {
                **row,
                "relation": "TARGET" if row["event_id"] == TARGET_EVENT else "Q_ROLE_VOTER",
            }
        )

    q_signature = next(
        row
        for row in signatures
        if row["visible_insert"] == "q"
        and row["visible_position"] == "LEFT"
        and row["atom_insert"] == "NULL"
        and row["atom_position"] == "NULL"
    )
    e_context = next(
        row
        for row in context_rows
        if row["visible_insert"] == "q"
        and row["visible_position"] == "LEFT"
        and row["base_edge_atom"] == "E"
    )
    combined_rank1 = next(
        row for row in tradeoff_rows if row["model_stage"] == "COMBINED_W085"
    )

    comparison_rows = []
    matching_candidates = []
    for row in candidate_rows:
        role = q_role(row["candidate_recipe"])
        matches = role == "NONCARRIER_Q"
        if matches:
            matching_candidates.append(row)
        comparison_rows.append(
            {
                "surface": TARGET_SURFACE,
                "candidate_recipe": row["candidate_recipe"],
                "gdt529_rank": row["gdt529_rank"],
                "gdt529_score": row["gdt529_score"],
                "candidate_q_role": role,
                "same_statement_other_q_vote": "NONCARRIER_Q",
                "matches_same_statement_vote": "YES" if matches else "NO",
                "context_rank": "1" if row["candidate_recipe"] == SELECTED_RECIPE else "REJECTED",
                "decision": (
                    "SELECT_UNIQUE_NONCARRIER_CANDIDATE"
                    if row["candidate_recipe"] == SELECTED_RECIPE
                    else "REJECT_CARRIER_CONFLICT"
                ),
            }
        )
    selected_candidate = min(matching_candidates, key=lambda row: int(row["gdt529_rank"]))

    certificate_rows = [
        {
            "evidence_layer": "OLD_GLOBAL_VISIBLE_q_NULL",
            "support": q_signature["support_pair_count"],
            "total": q_signature["visible_condition_total"],
            "value": q_signature["conditional_probability"],
            "detail": q_signature["examples"],
        },
        {
            "evidence_layer": "OLD_FIRST_ATOM_E_CONTEXT",
            "support": e_context["null_support"],
            "total": e_context["conditional_total"],
            "value": e_context["context_null_log_odds"],
            "detail": "q before an E-edge base is noncarrier in the sole old context pair",
        },
        {
            "evidence_layer": "CURRENT_SAME_STATEMENT_NEIGHBOURS",
            "support": len(other_target_q_events),
            "total": len(other_target_q_events),
            "value": "NONCARRIER_Q",
            "detail": "|".join(row["surface"] for row in other_target_q_events),
        },
        {
            "evidence_layer": "GDT523_PATH_EXPLANATION",
            "support": "qe=>e~E",
            "total": "COMBINED_W085",
            "value": combined_rank1["truth_null_feature"],
            "detail": (
                f"truth rank {combined_rank1['truth_rank']}; broad weighting not adopted, "
                "local statement vote decides here"
            ),
        },
    ]

    edition = []
    for row in current:
        if row["surface"] == TARGET_SURFACE:
            recipe = SELECTED_RECIPE
            candidate_rank = row["gdt534_candidate_rank"]
            context_rank = 1
            literal = WORKING_LITERAL_DE
            phrase = WORKING_PHRASE_DE
            evidence = (
                "six other q-initial cards in G515-S010 are unanimously noncarrier; "
                "old q-null 75/84; old E-edge context 1/1; qef path qe=>e~E"
            )
            policy = "GDT535_SAME_STATEMENT_Q_ROLE_NEIGHBOUR_VOTE"
            resolution = "RESOLVED_BY_SAME_STATEMENT_Q_NULL_CONTEXT"
        else:
            recipe = row["gdt534_working_recipe"]
            candidate_rank = row["gdt534_candidate_rank"]
            context_rank = "INHERITED"
            literal = row["gdt534_literal_reading_de"]
            phrase = row["gdt534_short_phrase_de"]
            evidence = "NO_SELECTED_SAME_STATEMENT_Q_REVISION"
            policy = "INHERIT_GDT534_WORKING_RECIPE"
            resolution = row["gdt534_resolution_status"]
        edition.append(
            {
                **row,
                "gdt535_working_recipe": recipe,
                "gdt535_gdt529_candidate_rank": candidate_rank,
                "gdt535_context_rank": context_rank,
                "gdt535_literal_reading_de": literal,
                "gdt535_short_phrase_de": phrase,
                "gdt535_evidence": evidence,
                "gdt535_policy": policy,
                "gdt535_resolution_status": resolution,
            }
        )

    unresolved = [
        row
        for row in edition
        if row["gdt535_resolution_status"] == "UNRESOLVED_NON_TOP1"
    ]
    inherited_metrics = inherited_result["inherited_gdt533_candidate_metrics"]
    status = (
        "PASS_SAME_STATEMENT_Q_NULL_qef_CLOSURE"
        if len(old) == 4576
        and len(current_events) == 597
        and len(current) == 159
        and old_metrics["q_event_count"] == 768
        and old_metrics["q_statement_count"] == 430
        and old_metrics["multi_q_statement_count"] == 166
        and old_metrics["fully_unanimous_multi_q_statement_count"] == 125
        and old_metrics["neighbour_vote_scored_event_count"] == 383
        and old_metrics["neighbour_vote_correct_event_count"] == 339
        and current_metrics["q_event_count"] == 78
        and current_metrics["q_statement_count"] == 42
        and current_metrics["multi_q_statement_count"] == 17
        and current_metrics["fully_unanimous_multi_q_statement_count"] == 13
        and current_metrics["neighbour_vote_scored_event_count"] == 47
        and current_metrics["neighbour_vote_correct_event_count"] == 41
        and len(target_statement_rows) == 27
        and len(target_q_events) == 7
        and len(other_target_q_events) == 6
        and other_roles == {"NONCARRIER_Q"}
        and target_vote["predicted_q_role"] == "NONCARRIER_Q"
        and q_signature["support_pair_count"] == "75"
        and q_signature["visible_condition_total"] == "84"
        and e_context["null_support"] == "1"
        and e_context["competing_support"] == "0"
        and selected_candidate["candidate_recipe"] == SELECTED_RECIPE
        and selected_candidate["gdt529_rank"] == "2"
        and len(matching_candidates) == 1
        and combined_rank1["truth_rank"] == "1"
        and len(unresolved) == 1
        and unresolved[0]["surface"] == "aiicthy"
        else "FAIL_SAME_STATEMENT_Q_NULL_GATE"
    )

    result = {
        "experiment_id": "GDT535",
        "status": status,
        "claim_ceiling": (
            "EXPLORATORY_SAME_STATEMENT_Q_ROLE_CLOSURE__"
            "NO_GLOBAL_Q_NULL_OR_CONFIRMED_PLAINTEXT"
        ),
        "old_statement_q_metrics": old_metrics,
        "current_statement_q_metrics": current_metrics,
        "selected_resolution_count": 1,
        "selected_resolution": {
            "surface": TARGET_SURFACE,
            "event_id": TARGET_EVENT,
            "statement_id": TARGET_STATEMENT,
            "recipe": SELECTED_RECIPE,
            "global_candidate_rank": 2,
            "same_statement_context_rank": 1,
            "rival_recipe": RIVAL_RECIPE,
            "other_q_event_count": len(other_target_q_events),
            "other_q_role_vote": "NONCARRIER_Q",
            "other_q_surfaces": [row["surface"] for row in other_target_q_events],
            "old_global_q_null_signature": "75/84",
            "old_E_edge_q_null_context": "1/1",
            "path_trace": "qe=>e~E",
            "working_literal_de": WORKING_LITERAL_DE,
            "working_phrase_de": WORKING_PHRASE_DE,
        },
        "inherited_candidate_metrics_unchanged": inherited_metrics,
        "working_resolved_surface_count": len(edition) - len(unresolved),
        "remaining_unresolved_surface_count": len(unresolved),
        "remaining_unresolved_surfaces": [row["surface"] for row in unresolved],
        "guard": (
            "USE_UNANIMOUS_OTHER_Q_ROLES_IN_THE_EXACT_STATEMENT_ONLY__"
            "KEEP_GLOBAL_q_AMBIGUITY__NO_RECIPE_CHANGE_OUTSIDE_qef__NO_NEW_PAGES"
        ),
    }

    write_tsv(OUT / "gdt535_159_working_revision.tsv", edition, list(edition[0]))
    write_tsv(
        OUT / "gdt535_statement_q_role_profiles.tsv",
        old_profiles + current_profiles,
        list(old_profiles[0]),
    )
    write_tsv(
        OUT / "gdt535_statement_q_neighbour_votes.tsv",
        old_votes + current_votes,
        list(old_votes[0]),
    )
    write_tsv(
        OUT / "gdt535_qef_target_statement_atlas.tsv",
        target_statement_atlas,
        list(target_statement_atlas[0]),
    )
    write_tsv(
        OUT / "gdt535_qef_same_statement_q_votes.tsv",
        target_q_atlas,
        list(target_q_atlas[0]),
    )
    write_tsv(
        OUT / "gdt535_qef_candidate_comparison.tsv",
        comparison_rows,
        list(comparison_rows[0]),
    )
    write_tsv(
        OUT / "gdt535_qef_resolution_certificate.tsv",
        certificate_rows,
        list(certificate_rows[0]),
    )
    write_tsv(
        OUT / "gdt535_remaining_unresolved_atlas.tsv",
        unresolved,
        list(edition[0]),
    )
    write_json(OUT / "gdt535_result.json", result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if status.startswith("PASS_") else 1


if __name__ == "__main__":
    raise SystemExit(main())
