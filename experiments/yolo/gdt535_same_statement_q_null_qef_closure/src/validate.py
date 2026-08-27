#!/usr/bin/env python3
"""Independently validate GDT535's same-statement qef closure."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
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
VALIDATION = OUT / "gdt535_validation.json"
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
ALIGN = BASE / "src/align_surface.py"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def role(recipe: str) -> str:
    atoms = recipe.split("+") if recipe else []
    return "CARRIER_Q" if atoms and atoms[0] == "CARRIER_Q" else "NONCARRIER_Q"


def independent_q_counts(
    rows: list[dict[str, str]], statement: str, recipe: str
) -> tuple[dict, list[tuple]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        if row["surface"].startswith("q"):
            grouped[row[statement]].append(row)
    multi = {key: values for key, values in grouped.items() if len(values) >= 2}
    votes = []
    for key, values in multi.items():
        for index, target in enumerate(values):
            others = [row for other_index, row in enumerate(values) if other_index != index]
            other_roles = {role(row[recipe]) for row in others}
            if len(other_roles) == 1:
                predicted = next(iter(other_roles))
                votes.append(
                    (
                        key,
                        target["surface"],
                        role(target[recipe]),
                        predicted,
                        role(target[recipe]) == predicted,
                        len(others),
                    )
                )
    metrics = {
        "q_event_count": sum(len(values) for values in grouped.values()),
        "q_statement_count": len(grouped),
        "multi_q_statement_count": len(multi),
        "fully_unanimous_multi_q_statement_count": sum(
            len({role(row[recipe]) for row in values}) == 1 for values in multi.values()
        ),
        "neighbour_vote_scored_event_count": len(votes),
        "neighbour_vote_correct_event_count": sum(row[4] for row in votes),
    }
    return metrics, votes


def main() -> int:
    result = json.loads((OUT / "gdt535_result.json").read_text(encoding="utf-8"))
    edition = read_tsv(OUT / "gdt535_159_working_revision.tsv")
    profiles = read_tsv(OUT / "gdt535_statement_q_role_profiles.tsv")
    votes = read_tsv(OUT / "gdt535_statement_q_neighbour_votes.tsv")
    statement = read_tsv(OUT / "gdt535_qef_target_statement_atlas.tsv")
    target_q = read_tsv(OUT / "gdt535_qef_same_statement_q_votes.tsv")
    comparison = read_tsv(OUT / "gdt535_qef_candidate_comparison.tsv")
    certificate = read_tsv(OUT / "gdt535_qef_resolution_certificate.tsv")
    unresolved = read_tsv(OUT / "gdt535_remaining_unresolved_atlas.tsv")
    old = read_tsv(OLD)
    current_events = read_tsv(CURRENT_EVENTS)
    signatures = read_tsv(Q_SIGNATURES)
    context_rows = read_tsv(Q_CONTEXT)
    tradeoff = read_tsv(Q_TRADEOFF)
    candidate_source = read_tsv(CANDIDATES)
    old_metrics, old_votes = independent_q_counts(
        old, "source_statement_id", "component_recipe"
    )
    current_metrics, current_votes = independent_q_counts(
        current_events, "statement_id", "gdt516_context_recipe"
    )
    checks = []

    def check(name: str, condition: bool, detail) -> None:
        checks.append({"check": name, "pass": bool(condition), "detail": detail})

    check(
        "result_status",
        result["status"] == "PASS_SAME_STATEMENT_Q_NULL_qef_CLOSURE",
        result["status"],
    )
    check(
        "claim_ceiling",
        result["claim_ceiling"]
        == "EXPLORATORY_SAME_STATEMENT_Q_ROLE_CLOSURE__NO_GLOBAL_Q_NULL_OR_CONFIRMED_PLAINTEXT",
        result["claim_ceiling"],
    )
    check("source_counts", len(old) == 4576 and len(current_events) == 597, [len(old), len(current_events)])
    check("edition_count", len(edition) == 159, len(edition))
    check(
        "edition_unique", len({row["surface"] for row in edition}) == 159, len(edition)
    )
    recipe_changes = [
        row for row in edition if row["gdt534_working_recipe"] != row["gdt535_working_recipe"]
    ]
    resolution_changes = [
        row
        for row in edition
        if row["gdt534_resolution_status"] != row["gdt535_resolution_status"]
    ]
    check("zero_recipe_changes", recipe_changes == [], [row["surface"] for row in recipe_changes])
    check(
        "one_resolution_change",
        len(resolution_changes) == 1 and resolution_changes[0]["surface"] == "qef",
        [row["surface"] for row in resolution_changes],
    )
    selected = resolution_changes[0]
    check(
        "selected_recipe_and_ranks",
        selected["gdt535_working_recipe"] == "E+LOCAL_CHAR_F"
        and selected["gdt535_gdt529_candidate_rank"] == "2"
        and selected["gdt535_context_rank"] == "1",
        selected,
    )
    check(
        "selected_reading",
        selected["gdt535_literal_reading_de"]
        == "[E:STEUERUNG=GRAD I] · [LOCAL_CHAR_F:STEUERUNG=HIER]"
        and selected["gdt535_short_phrase_de"] == "Hier auf Grad I.",
        selected["gdt535_short_phrase_de"],
    )
    check(
        "selected_resolution",
        selected["gdt535_resolution_status"]
        == "RESOLVED_BY_SAME_STATEMENT_Q_NULL_CONTEXT",
        selected["gdt535_resolution_status"],
    )

    expected_old = {
        "q_event_count": 768,
        "q_statement_count": 430,
        "multi_q_statement_count": 166,
        "fully_unanimous_multi_q_statement_count": 125,
        "neighbour_vote_scored_event_count": 383,
        "neighbour_vote_correct_event_count": 339,
    }
    expected_current = {
        "q_event_count": 78,
        "q_statement_count": 42,
        "multi_q_statement_count": 17,
        "fully_unanimous_multi_q_statement_count": 13,
        "neighbour_vote_scored_event_count": 47,
        "neighbour_vote_correct_event_count": 41,
    }
    check("independent_old_q_metrics", old_metrics == expected_old, old_metrics)
    check("independent_current_q_metrics", current_metrics == expected_current, current_metrics)
    check(
        "result_old_metrics",
        all(result["old_statement_q_metrics"][key] == value for key, value in expected_old.items()),
        result["old_statement_q_metrics"],
    )
    check(
        "result_current_metrics",
        all(result["current_statement_q_metrics"][key] == value for key, value in expected_current.items()),
        result["current_statement_q_metrics"],
    )
    check(
        "profile_atlas_count",
        len(profiles) == expected_old["q_statement_count"] + expected_current["q_statement_count"],
        len(profiles),
    )
    check(
        "vote_atlas_count",
        len(votes) == expected_old["neighbour_vote_scored_event_count"] + expected_current["neighbour_vote_scored_event_count"],
        len(votes),
    )
    check(
        "vote_atlas_correct_count",
        Counter(row["prediction_correct"] for row in votes) == Counter({"YES": 380, "NO": 50}),
        Counter(row["prediction_correct"] for row in votes),
    )

    target_statement_source = [
        row for row in current_events if row["statement_id"] == "G515-S010"
    ]
    target_q_source = [row for row in target_statement_source if row["surface"].startswith("q")]
    other_q = [row for row in target_q_source if row["event_id"] != "G515-E0165"]
    check("target_statement_count", len(statement) == len(target_statement_source) == 27, len(statement))
    check("target_q_count", len(target_q) == len(target_q_source) == 7, len(target_q))
    check(
        "target_other_q_unanimous",
        len(other_q) == 6
        and {role(row["gdt516_context_recipe"]) for row in other_q} == {"NONCARRIER_Q"},
        [(row["surface"], row["gdt516_context_recipe"]) for row in other_q],
    )
    check(
        "target_other_q_surfaces",
        [row["surface"] for row in other_q]
        == ["qokees", "qokeey", "qokeey", "qotar", "qokey", "qokeor"],
        [row["surface"] for row in other_q],
    )
    target_vote_rows = [row for row in votes if row["target_event_id"] == "G515-E0165"]
    check(
        "target_vote_exact",
        len(target_vote_rows) == 1
        and target_vote_rows[0]["predicted_q_role"] == "NONCARRIER_Q"
        and target_vote_rows[0]["other_q_event_count"] == "6"
        and target_vote_rows[0]["prediction_correct"] == "YES",
        target_vote_rows,
    )

    signature = next(
        row
        for row in signatures
        if row["visible_insert"] == "q"
        and row["visible_position"] == "LEFT"
        and row["atom_insert"] == "NULL"
        and row["atom_position"] == "NULL"
    )
    check(
        "old_global_q_null",
        signature["support_pair_count"] == "75"
        and signature["visible_condition_total"] == "84"
        and signature["reliability"] == "0.974025974",
        signature,
    )
    e_context = next(
        row
        for row in context_rows
        if row["visible_insert"] == "q"
        and row["visible_position"] == "LEFT"
        and row["base_edge_atom"] == "E"
    )
    check(
        "old_E_edge_q_null",
        e_context["null_support"] == "1"
        and e_context["competing_support"] == "0"
        and e_context["context_dominant_null"] == "YES",
        e_context,
    )
    combined = next(
        row
        for row in tradeoff
        if row["surface"] == "qef" and row["model_stage"] == "COMBINED_W085"
    )
    check(
        "path_tradeoff_can_select_qef",
        combined["truth_recipe"] == "E+LOCAL_CHAR_F"
        and combined["truth_rank"] == "1"
        and combined["top1_recipe"] == "E+LOCAL_CHAR_F"
        and combined["truth_null_feature"] == "2.993026809",
        combined,
    )

    source_candidates = {
        (row["candidate_recipe"], row["gdt529_rank"])
        for row in candidate_source
        if row["surface"] == "qef"
    }
    check(
        "source_candidate_count",
        len(source_candidates) == 4,
        sorted(source_candidates, key=lambda item: int(item[1])),
    )
    check(
        "comparison_exact_source",
        len(comparison) == 4
        and {(row["candidate_recipe"], row["gdt529_rank"]) for row in comparison}
        == source_candidates,
        comparison,
    )
    matching = [row for row in comparison if row["matches_same_statement_vote"] == "YES"]
    check(
        "unique_noncarrier_candidate",
        len(matching) == 1
        and matching[0]["candidate_recipe"] == "E+LOCAL_CHAR_F"
        and matching[0]["gdt529_rank"] == "2"
        and matching[0]["context_rank"] == "1",
        matching,
    )
    check("certificate_layer_count", len(certificate) == 4, len(certificate))
    check(
        "certificate_layers",
        [row["evidence_layer"] for row in certificate]
        == [
            "OLD_GLOBAL_VISIBLE_q_NULL",
            "OLD_FIRST_ATOM_E_CONTEXT",
            "CURRENT_SAME_STATEMENT_NEIGHBOURS",
            "GDT523_PATH_EXPLANATION",
        ],
        [row["evidence_layer"] for row in certificate],
    )

    inherited = result["inherited_candidate_metrics_unchanged"]
    check(
        "candidate_metrics_unchanged",
        inherited["target_count"] == 159
        and inherited["top1_exact_count"] == 155
        and inherited["top2_exact_count"] == 157
        and inherited["rank_sum"] == 174,
        inherited,
    )
    check(
        "unresolved_queue",
        len(unresolved) == 1
        and unresolved[0]["surface"] == "aiicthy"
        and result["working_resolved_surface_count"] == 158
        and result["remaining_unresolved_surfaces"] == ["aiicthy"],
        [row["surface"] for row in unresolved],
    )

    def align(surface: str, event: str, page: str) -> dict:
        completed = subprocess.run(
            [
                sys.executable,
                str(ALIGN),
                "--surface",
                surface,
                "--event-id",
                event,
                "--page",
                page,
                "--top",
                "12",
            ],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        return json.loads(completed.stdout)

    aligned = align("qef", "G515-E0165", "f31r")
    check(
        "executable_qef_resolution",
        aligned["default_selection"] == "E+LOCAL_CHAR_F"
        and aligned["working_revision"] == "E+LOCAL_CHAR_F"
        and aligned["same_statement_q_certificate"]["other_q_event_count"] == 6
        and aligned["same_statement_q_certificate"]["same_statement_context_rank"] == 1
        and aligned["working_phrase_de"] == "Hier auf Grad I.",
        aligned,
    )
    dalcheeeky = align("dalcheeeky", "G515-E0423", "f66r")
    check(
        "gdt534_dalcheeeky_revision_preserved",
        dalcheeeky["default_selection"] == "AL+CH+K+EEE+Y"
        and dalcheeeky["working_revision"] == "AL+CH+K+EEE+Y"
        and dalcheeeky["same_statement_q_certificate"] == "NONE",
        dalcheeeky["default_selection"],
    )
    dairykodas = align("dairykodas", "G515-E0364", "f66r")
    check(
        "gdt533_dairykodas_revision_preserved",
        dairykodas["default_selection"] == "D_ADDR+AIR+Y+K+O+DA+S",
        dairykodas["default_selection"],
    )
    dshold = align("dsholdaiir", "G515-E0366", "f66r")
    check(
        "gdt532_dsholdaiir_revision_preserved",
        dshold["default_selection"] == "D_ADDR+SH+OL+DA+IIN+R",
        dshold["default_selection"],
    )
    saiis = align("saiis", "G515-E0243", "f31r")
    check(
        "gdt531_saiis_revision_preserved",
        saiis["default_selection"] == "S+A_ADDR+IIN+S",
        saiis["default_selection"],
    )
    check(
        "no_new_page_guard",
        result["guard"].endswith("NO_NEW_PAGES"),
        result["guard"],
    )

    status = "PASS" if all(row["pass"] for row in checks) else "FAIL"
    validation = {
        "experiment_id": "GDT535",
        "status": status,
        "check_count": len(checks),
        "passed_count": sum(row["pass"] for row in checks),
        "failed_count": sum(not row["pass"] for row in checks),
        "checks": checks,
    }
    VALIDATION.write_text(
        json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
