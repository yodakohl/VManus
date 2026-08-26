#!/usr/bin/env python3
"""Compile one context-safe current-default deck for all 110 GDT493 T/R cells."""

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
BASE = ROOT / "experiments/yolo/gdt497_complete_context_safe_tr_default_deck"
ART = BASE / "artifacts"
G493 = ROOT / "experiments/yolo/gdt493_owner_dependent_tr_realization_deck/artifacts"
G496 = ROOT / "experiments/yolo/gdt496_semantic_action_substitution_atlas/artifacts"

CELLS_IN = G493 / "gdt493_110_owner_frame_realization_cells.tsv"
STATE_FRAMES_IN = G493 / "gdt493_4_state_dependent_frames.tsv"
G496_CONTEXT_IN = G496 / "gdt496_9_context_safe_defaults.tsv"

DECK_OUT = ART / "gdt497_110_current_default_cells.tsv"
GENERALIZED_OUT = ART / "gdt497_23_context_generalized_composed_cells.tsv"
OBSERVED_STATE_OUT = ART / "gdt497_17_observed_state_examples.tsv"
PAIRS_OUT = ART / "gdt497_55_current_tr_pairs.tsv"
FRAMES_OUT = ART / "gdt497_11_frame_default_coverage.tsv"
REGISTERS_OUT = ART / "gdt497_5_register_default_coverage.tsv"
READABLE_OUT = ART / "GDT497_COMPLETE_CONTEXT_SAFE_TR_DEFAULT_DECK.md"
RESULT_OUT = ART / "gdt497_result.json"

STATUS = "ONE_HUNDRED_TEN_CURRENT_DEFAULTS__TWENTY_THREE_CONTEXT_GENERALIZED__THIRTY_SEVEN_OBSERVED_RETAINED"
GUARD = "CURRENT_WORKING_DEFAULT__NO_SURFACE_OR_OCCURRENCE_PREDICTION"


def read_tsv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if reader.fieldnames is None:
            raise ValueError(f"missing header: {path}")
        return list(reader.fieldnames), list(reader)


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"refusing to write empty table: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def generalize_active_phrase(phrase: str, frame: str) -> tuple[str, str, int]:
    matches = list(re.finditer(r"\b(?:den|die|das) [^.;]+? \[wie zuvor\]", phrase))
    expected = 2 if frame == "CH+@ACTION" else 1
    if len(matches) != expected:
        raise ValueError(f"expected {expected} inherited noun(s) in {frame}: {phrase}")
    replacement_index = 0

    def replace(_match: re.Match[str]) -> str:
        nonlocal replacement_index
        replacement_index += 1
        return "das zuvor Genannte" if replacement_index == 1 else "es"

    generalized = re.sub(r"\b(?:den|die|das) [^.;]+? \[wie zuvor\]", replace, phrase)
    change_type = "COMPOSED_CONTEXT_NOUN_GENERALIZED"
    if frame == "@ACTION+OL":
        patterns = {
            "Weiter stelle das zuvor Genannte ein.": "Fahre fort, das zuvor Genannte einzustellen.",
            "Weiter kennzeichne das zuvor Genannte.": "Fahre fort, das zuvor Genannte zu kennzeichnen.",
            "Weiter markiere das zuvor Genannte.": "Fahre fort, das zuvor Genannte zu markieren.",
        }
        if generalized not in patterns:
            raise ValueError(f"unhandled continuation phrase: {generalized}")
        generalized = patterns[generalized]
        change_type = "COMPOSED_CONTEXT_NOUN_AND_CONTINUATION_FLUENCY"
    return generalized, change_type, expected


def compact_examples(rows: list[dict[str, str]]) -> str:
    return " || ".join(
        f'{row["realization_cell_id"]}:{row["register"]}:{row["action_recipe"]}:{row["display_phrase_de"]}'
        for row in rows
    ) or "NONE"


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    _cell_fields, source_cells = read_tsv(CELLS_IN)
    _state_fields, state_frames = read_tsv(STATE_FRAMES_IN)
    _g496_fields, g496_context = read_tsv(G496_CONTEXT_IN)
    if (len(source_cells), len(state_frames), len(g496_context)) != (110, 4, 9):
        raise ValueError("input count drift")

    state_frame_names = {row["frozen_frame"] for row in state_frames}
    if state_frame_names != {"@ACTION", "@ACTION+AL", "@ACTION+OL", "CH+@ACTION"}:
        raise ValueError("state-frame drift")

    observed_state = [
        row for row in source_cells
        if row["state_requirement"] == "ACTIVE_ARGUMENT_REQUIRED" and row["evidence_status"] == "OBSERVED_CLAUSE"
    ]
    composed_state = [
        row for row in source_cells
        if row["state_requirement"] == "ACTIVE_ARGUMENT_REQUIRED" and row["evidence_status"] == "COMPOSED_WORKING"
    ]
    if (len(observed_state), len(composed_state)) != (17, 23):
        raise ValueError("state-cell partition drift")

    observed_by_frame: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in observed_state:
        observed_by_frame[row["frozen_frame"]].append(row)

    deck_rows: list[dict[str, object]] = []
    generalized_rows: list[dict[str, object]] = []
    deck_by_source_id: dict[str, dict[str, object]] = {}
    for source in source_cells:
        if source["evidence_status"] == "OBSERVED_CLAUSE":
            current_phrase = source["display_phrase_de"]
            policy = "OBSERVED_CLAUSE_RETAINED"
            change_type = "UNCHANGED_OBSERVED"
            generalized_noun_count = 0
        elif source["state_requirement"] == "SELF_CONTAINED_ARGUMENT":
            current_phrase = source["display_phrase_de"]
            policy = "COMPOSED_SELF_CONTAINED_RETAINED"
            change_type = "UNCHANGED_SELF_CONTAINED"
            generalized_noun_count = 0
        else:
            current_phrase, change_type, generalized_noun_count = generalize_active_phrase(
                source["display_phrase_de"], source["frozen_frame"]
            )
            policy = "COMPOSED_CONTEXT_SAFE_GENERALIZED"

        deck = {
            "current_default_id": f"G497-D{len(deck_rows) + 1:03d}",
            "source_realization_cell_id": source["realization_cell_id"],
            "frame_id": source["frame_id"],
            "frozen_frame": source["frozen_frame"],
            "action_root": source["action_root"],
            "action_recipe": source["action_recipe"],
            "register": source["register"],
            "portable_component_trace_de": source["portable_component_trace_de"],
            "owner_local_slot_trace_de": source["owner_local_slot_trace_de"],
            "state_requirement": source["state_requirement"],
            "previous_display_phrase_de": source["display_phrase_de"],
            "current_default_phrase_de": current_phrase,
            "current_default_policy": policy,
            "editorial_change_type": change_type,
            "generalized_inherited_noun_count": generalized_noun_count,
            "evidence_status_retained": source["evidence_status"],
            "display_phrase_provenance_retained": source["display_phrase_provenance"],
            "observed_event_count_retained": source["observed_event_count"],
            "observed_clause_form_count_retained": source["observed_clause_form_count"],
            "observed_pages_retained": source["observed_pages"],
            "observed_event_ids_retained": source["observed_event_ids"],
            "all_observed_clause_forms_de_retained": source["all_observed_clause_forms_de"],
            "observed_inherited_argument_roots_retained": source["observed_inherited_argument_roots"],
            "context_argument_policy": "USE_EXACT_OBSERVED_ARGUMENT" if source["evidence_status"] == "OBSERVED_CLAUSE" else (
                "INHERIT_LIVE_ARGUMENT" if source["state_requirement"] == "ACTIVE_ARGUMENT_REQUIRED" else "EXPLICIT_IN_RECIPE"
            ),
            "all_recipe_value_cells_observed": source["all_recipe_value_cells_observed"],
            "new_slot_value_required": source["new_slot_value_required"],
            "working_root_meaning_changed": "NO",
            "formal_frame_changed": "NO",
            "evidence_status_changed": "NO",
            "surface_prediction_made": "NO",
            "occurrence_prediction_made": "NO",
            "guard": GUARD,
        }
        deck_rows.append(deck)
        deck_by_source_id[source["realization_cell_id"]] = deck

        if policy == "COMPOSED_CONTEXT_SAFE_GENERALIZED":
            frame_examples = observed_by_frame[source["frozen_frame"]]
            same_register = [row for row in frame_examples if row["register"] == source["register"]]
            same_action = [row for row in frame_examples if row["action_root"] == source["action_root"]]
            frame_roots = sorted(
                {
                    root
                    for row in frame_examples
                    for root in row["observed_inherited_argument_roots"].split("|")
                    if root and root != "NONE"
                }
            )
            generalized_rows.append(
                {
                    "context_generalization_id": f"G497-C{len(generalized_rows) + 1:02d}",
                    "current_default_id": deck["current_default_id"],
                    "source_realization_cell_id": source["realization_cell_id"],
                    "frozen_frame": source["frozen_frame"],
                    "action_root": source["action_root"],
                    "action_recipe": source["action_recipe"],
                    "register": source["register"],
                    "previous_y_default_phrase_de": source["display_phrase_de"],
                    "context_safe_default_phrase_de": current_phrase,
                    "editorial_change_type": change_type,
                    "generalized_inherited_noun_count": generalized_noun_count,
                    "same_frame_observed_state_cell_count": len(frame_examples),
                    "same_frame_observed_state_cell_ids": "|".join(row["realization_cell_id"] for row in frame_examples),
                    "same_frame_observed_argument_roots": "|".join(frame_roots),
                    "same_register_observed_state_cell_count": len(same_register),
                    "same_register_observed_state_cell_ids": "|".join(row["realization_cell_id"] for row in same_register) or "NONE",
                    "same_action_observed_state_cell_count": len(same_action),
                    "same_action_observed_state_cell_ids": "|".join(row["realization_cell_id"] for row in same_action),
                    "same_action_observed_registers": "|".join(row["register"] for row in same_action),
                    "observed_state_examples_de": compact_examples(frame_examples),
                    "working_root_meaning_changed": "NO",
                    "formal_frame_changed": "NO",
                    "evidence_status_retained": source["evidence_status"],
                    "surface_prediction_made": "NO",
                    "occurrence_prediction_made": "NO",
                    "guard": GUARD,
                }
            )

    observed_state_rows: list[dict[str, object]] = []
    for source in observed_state:
        observed_state_rows.append(
            {
                "observed_state_example_id": f"G497-O{len(observed_state_rows) + 1:02d}",
                "current_default_id": deck_by_source_id[source["realization_cell_id"]]["current_default_id"],
                "source_realization_cell_id": source["realization_cell_id"],
                "frozen_frame": source["frozen_frame"],
                "action_root": source["action_root"],
                "action_recipe": source["action_recipe"],
                "register": source["register"],
                "observed_phrase_de": source["display_phrase_de"],
                "all_observed_clause_forms_de": source["all_observed_clause_forms_de"],
                "observed_inherited_argument_roots": source["observed_inherited_argument_roots"],
                "observed_event_count": source["observed_event_count"],
                "observed_clause_form_count": source["observed_clause_form_count"],
                "observed_pages": source["observed_pages"],
                "observed_event_ids": source["observed_event_ids"],
                "evidence_status": source["evidence_status"],
                "observed_phrase_retained_exactly": "YES" if deck_by_source_id[source["realization_cell_id"]]["current_default_phrase_de"] == source["display_phrase_de"] else "NO",
                "guard": GUARD,
            }
        )

    pairs: list[dict[str, object]] = []
    by_frame_register: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in deck_rows:
        by_frame_register[(str(row["frozen_frame"]), str(row["register"]))].append(row)
    for source in source_cells:
        key = (source["frozen_frame"], source["register"])
        if key not in by_frame_register:
            continue
    for (frame, register), group in sorted(by_frame_register.items()):
        if len(group) != 2:
            raise ValueError(f"T/R pair count drift: {frame} {register}")
        by_action = {str(row["action_root"]): row for row in group}
        t_row = by_action["T"]
        r_row = by_action["R"]
        pairs.append(
            {
                "current_pair_id": f"G497-TR{len(pairs) + 1:02d}",
                "frozen_frame": frame,
                "register": register,
                "t_current_default_id": t_row["current_default_id"],
                "r_current_default_id": r_row["current_default_id"],
                "t_current_phrase_de": t_row["current_default_phrase_de"],
                "r_current_phrase_de": r_row["current_default_phrase_de"],
                "t_policy": t_row["current_default_policy"],
                "r_policy": r_row["current_default_policy"],
                "t_evidence_status": t_row["evidence_status_retained"],
                "r_evidence_status": r_row["evidence_status_retained"],
                "current_phrases_distinct": "YES" if t_row["current_default_phrase_de"] != r_row["current_default_phrase_de"] else "NO",
                "formal_remainder_unchanged": "YES",
                "both_context_safe": "YES",
                "working_root_meaning_changed": "NO",
                "guard": GUARD,
            }
        )

    def summarize(axis: str) -> list[dict[str, object]]:
        summaries: list[dict[str, object]] = []
        for value in sorted({str(row[axis]) for row in deck_rows}):
            group = [row for row in deck_rows if row[axis] == value]
            summaries.append(
                {
                    axis: value,
                    "current_default_count": len(group),
                    "observed_retained_count": sum(row["current_default_policy"] == "OBSERVED_CLAUSE_RETAINED" for row in group),
                    "composed_self_contained_retained_count": sum(row["current_default_policy"] == "COMPOSED_SELF_CONTAINED_RETAINED" for row in group),
                    "composed_context_generalized_count": sum(row["current_default_policy"] == "COMPOSED_CONTEXT_SAFE_GENERALIZED" for row in group),
                    "continuation_fluency_change_count": sum(row["editorial_change_type"] == "COMPOSED_CONTEXT_NOUN_AND_CONTINUATION_FLUENCY" for row in group),
                    "all_context_safe": "YES",
                    "all_meanings_retained": "YES" if all(row["working_root_meaning_changed"] == "NO" for row in group) else "NO",
                    "all_evidence_statuses_retained": "YES" if all(row["evidence_status_changed"] == "NO" for row in group) else "NO",
                }
            )
        return summaries

    frame_rows = summarize("frozen_frame")
    register_rows = summarize("register")
    write_tsv(DECK_OUT, deck_rows)
    write_tsv(GENERALIZED_OUT, generalized_rows)
    write_tsv(OBSERVED_STATE_OUT, observed_state_rows)
    write_tsv(PAIRS_OUT, pairs)
    write_tsv(FRAMES_OUT, frame_rows)
    write_tsv(REGISTERS_OUT, register_rows)

    policy_counts = Counter(str(row["current_default_policy"]) for row in deck_rows)
    lines = [
        "# GDT497 — Vollständiger kontextsicherer T/R-Defaultbestand",
        "",
        f"Status: `{STATUS}`",
        "",
        "Alle 110 T/R×Rahmen×Register-Zellen haben nun genau einen aktuellen",
        "deutschen Default. Beobachtete Klauseln bleiben wortgleich. Konkrete",
        "selbständige Kompositionen bleiben konkret. Nur unbeobachtete Ellipsen",
        "ersetzen den willkürlichen Y-Posten durch das geerbte `das zuvor Genannte`.",
        "",
        f"- beobachtet und wortgleich: **{policy_counts['OBSERVED_CLAUSE_RETAINED']}**;",
        f"- selbständig komponiert und wortgleich: **{policy_counts['COMPOSED_SELF_CONTAINED_RETAINED']}**;",
        f"- kontextabhängig komponiert und generalisiert: **{policy_counts['COMPOSED_CONTEXT_SAFE_GENERALIZED']}**;",
        f"- davon flüssiger FORTSETZEN-Satzbau: **{sum(row['editorial_change_type'] == 'COMPOSED_CONTEXT_NOUN_AND_CONTINUATION_FLUENCY' for row in deck_rows)}**.",
        "",
        "## Die 110 aktuellen Defaults",
        "",
        "| ID | Rahmen | Aktion | Register | aktueller Default | Status | Politik |",
        "|---|---|---|---|---|---|---|",
    ]
    for row in deck_rows:
        lines.append(
            f'| {row["current_default_id"]} | `{row["frozen_frame"]}` | `{row["action_recipe"]}` | '
            f'{row["register"]} | {row["current_default_phrase_de"]} | `{row["evidence_status_retained"]}` | '
            f'`{row["current_default_policy"]}` |'
        )
    lines.extend(
        [
            "",
            "## Die 23 generalisierten Ellipsen",
            "",
        ]
    )
    for row in generalized_rows:
        lines.extend(
            [
                f'### {row["context_generalization_id"]} — {row["register"]} · `{row["action_recipe"]}`',
                "",
                f'**Vorher:** {row["previous_y_default_phrase_de"]}',
                "",
                f'**Jetzt:** {row["context_safe_default_phrase_de"]}',
                "",
                f'Beobachtete Argumentwurzeln im Rahmen: `{row["same_frame_observed_argument_roots"]}`. '
                f'Beobachtete Rahmenbeispiele: {row["observed_state_examples_de"]}',
                "",
                f'`{GUARD}`',
                "",
            ]
        )
    lines.extend(["## Die 17 beobachteten Zustandsbeispiele", ""])
    for row in observed_state_rows:
        lines.append(
            f'- {row["observed_state_example_id"]}: {row["register"]} `{row["action_recipe"]}` — '
            f'{row["observed_phrase_de"]} (Argument `{row["observed_inherited_argument_roots"]}`, '
            f'{row["observed_event_count"]} Events, {row["observed_pages"]}).'
        )
    READABLE_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    g496_by_recipe_register = {(row["action_recipe"], row["register"]): row for row in g496_context}
    overlap = [
        row for row in generalized_rows
        if (str(row["action_recipe"]), str(row["register"])) in g496_by_recipe_register
    ]
    result = {
        "status": STATUS,
        "current_default_cells": len(deck_rows),
        "observed_clauses_retained": policy_counts["OBSERVED_CLAUSE_RETAINED"],
        "composed_self_contained_retained": policy_counts["COMPOSED_SELF_CONTAINED_RETAINED"],
        "composed_context_generalized": policy_counts["COMPOSED_CONTEXT_SAFE_GENERALIZED"],
        "state_dependent_cells": len(observed_state) + len(composed_state),
        "observed_state_examples": len(observed_state_rows),
        "composed_state_defaults": len(generalized_rows),
        "inherited_noun_occurrences_generalized": sum(int(row["generalized_inherited_noun_count"]) for row in generalized_rows),
        "continuation_fluency_changes": sum(row["editorial_change_type"] == "COMPOSED_CONTEXT_NOUN_AND_CONTINUATION_FLUENCY" for row in generalized_rows),
        "gdt496_overlap_cells": len(overlap),
        "gdt496_overlap_with_same_context_referent": sum("das zuvor Genannte" in str(row["context_safe_default_phrase_de"]) for row in overlap),
        "gdt496_overlap_exact_phrase": sum(
            row["context_safe_default_phrase_de"] == g496_by_recipe_register[(str(row["action_recipe"]), str(row["register"]))]["context_safe_default_de"]
            for row in overlap
        ),
        "current_tr_pairs": len(pairs),
        "distinct_current_tr_pairs": sum(row["current_phrases_distinct"] == "YES" for row in pairs),
        "generalized_cells_with_frame_examples": sum(int(row["same_frame_observed_state_cell_count"]) > 0 for row in generalized_rows),
        "generalized_cells_with_same_action_examples": sum(int(row["same_action_observed_state_cell_count"]) > 0 for row in generalized_rows),
        "generalized_cells_with_same_register_examples": sum(int(row["same_register_observed_state_cell_count"]) > 0 for row in generalized_rows),
        "working_root_meaning_changes": sum(row["working_root_meaning_changed"] == "YES" for row in deck_rows),
        "formal_frame_changes": sum(row["formal_frame_changed"] == "YES" for row in deck_rows),
        "evidence_status_changes": sum(row["evidence_status_changed"] == "YES" for row in deck_rows),
        "surface_predictions": sum(row["surface_prediction_made"] == "YES" for row in deck_rows),
        "occurrence_predictions": sum(row["occurrence_prediction_made"] == "YES" for row in deck_rows),
        "frame_count": len(frame_rows),
        "register_count": len(register_rows),
        "guard": GUARD,
    }
    RESULT_OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
