#!/usr/bin/env python3
"""Leave each physical page out of the GDT449 target robustness shortcut."""

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
BASE = ROOT / "experiments/yolo/gdt450_target_robustness_page_holdout"
OUT = BASE / "artifacts"
GDT448 = ROOT / "experiments/yolo/gdt448_context_conditioned_neighbor_replay/artifacts"
CURRENT = ROOT / "experiments/yolo/gdt441_factor_gated_unseen_recipe_reader/artifacts/gdt441_4576_factor_reader_replay.tsv"
TARGETS = ROOT / "experiments/yolo/gdt449_context_robust_neighbor_deck/artifacts/gdt449_target_context_robustness.tsv"
SHARD_SIZE = 5000


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str] | None = None) -> None:
    if not rows and fields is None:
        raise ValueError(f"Refusing to write schema-less empty table {path}")
    columns = fields or list(rows[0])
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def broad_class(rows: list[dict[str, str]]) -> str:
    readable = sum(row["context_execution_decision"] in {"READ", "READ_AMBER"} for row in rows)
    stopped = sum(row["context_execution_decision"] == "STOP" for row in rows)
    if stopped == 0:
        return "READABLE"
    if readable == 0:
        return "STOP"
    return "MIXED"


def outcome(train_class: str, held_rows: list[dict[str, str]]) -> str:
    if train_class == "NO_TRAINING":
        return "NO_OTHER_PAGE_TRAINING"
    if train_class == "MIXED":
        return "ABSTAIN_TRAIN_MIXED"
    held_readable = any(row["context_execution_decision"] in {"READ", "READ_AMBER"} for row in held_rows)
    held_stop = any(row["context_execution_decision"] == "STOP" for row in held_rows)
    if train_class == "READABLE":
        return "FALSE_SAFE" if held_stop else "CORRECT_READABLE"
    return "FALSE_STOP" if held_readable else "CORRECT_STOP"


def context_signature(row: dict[str, str]) -> str:
    return "|".join((
        row["incoming_action"],
        row["incoming_argument"],
        row["scope_incoming_action"],
        row["next_recipe"],
    ))


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    replay = [
        row
        for path in sorted(GDT448.glob("gdt448_context_neighbor_replay_part*.tsv"))
        for row in read_tsv(path)
    ]
    current = read_tsv(CURRENT)
    current_by_event = {row["event_id"]: row for row in current}
    target_metadata = {row["target_recipe"]: row for row in read_tsv(TARGETS)}

    raw_occurrences: list[dict[str, str]] = []
    for row in replay:
        event_ids = row["context_event_ids"].split("|")
        if len(event_ids) != int(row["context_occurrence_count"]):
            raise ValueError(f"Context weight mismatch {row['replay_id']}")
        for event_id in event_ids:
            event = current_by_event[event_id]
            raw_occurrences.append({
                **row,
                "event_id": event_id,
                "physical_page": event["physical_page"],
                "operational_context_signature": context_signature(row),
            })

    # Source multiplicity must not weight a target twice at the same actual
    # event. In the current atlas no conflicting decision is allowed.
    target_event: dict[tuple[str, str], dict[str, str]] = {}
    source_edges: dict[tuple[str, str], set[str]] = defaultdict(set)
    for row in raw_occurrences:
        key = (row["target_recipe"], row["event_id"])
        previous = target_event.get(key)
        if previous and previous["context_execution_decision"] != row["context_execution_decision"]:
            raise ValueError(f"Target/event disagreement {key}")
        target_event[key] = row
        source_edges[key].add(row["neighbor_id"])

    by_target: dict[str, list[dict[str, str]]] = defaultdict(list)
    for (target_recipe, _), row in target_event.items():
        by_target[target_recipe].append(row)

    fold_rows: list[dict[str, object]] = []
    critical_rows: list[dict[str, object]] = []
    for target_recipe, rows in sorted(by_target.items()):
        pages = sorted({row["physical_page"] for row in rows})
        metadata = target_metadata[target_recipe]
        for held_page in pages:
            held = [row for row in rows if row["physical_page"] == held_page]
            train = [row for row in rows if row["physical_page"] != held_page]
            train_class = broad_class(train) if train else "NO_TRAINING"
            held_class = broad_class(held)
            fold_outcome = outcome(train_class, held)
            train_signatures = {row["operational_context_signature"] for row in train}
            unseen_held = [row for row in held if row["operational_context_signature"] not in train_signatures]
            unseen_outcome = "NO_UNSEEN_HELD_CONTEXT" if not unseen_held else outcome(train_class, unseen_held)
            train_counts = Counter(row["context_execution_decision"] for row in train)
            held_counts = Counter(row["context_execution_decision"] for row in held)
            unseen_counts = Counter(row["context_execution_decision"] for row in unseen_held)
            fold_rows.append({
                "fold_id": f"G450-F{len(fold_rows) + 1:06d}",
                "held_page": held_page,
                "target_recipe": target_recipe,
                "target_is_exact_catalog_key": metadata["target_is_exact_catalog_key"],
                "target_identity_route": metadata["target_identity_route"],
                "global_gdt449_robustness": metadata["observed_context_robustness"],
                "training_page_count": len({row["physical_page"] for row in train}),
                "training_occurrence_probe_count": len(train),
                "held_occurrence_probe_count": len(held),
                "training_green_count": train_counts["READ"],
                "training_amber_count": train_counts["READ_AMBER"],
                "training_stop_count": train_counts["STOP"],
                "held_green_count": held_counts["READ"],
                "held_amber_count": held_counts["READ_AMBER"],
                "held_stop_count": held_counts["STOP"],
                "training_shortcut_class": train_class,
                "held_actual_class": held_class,
                "holdout_outcome": fold_outcome,
                "training_context_signature_count": len(train_signatures),
                "held_context_signature_count": len({row["operational_context_signature"] for row in held}),
                "unseen_held_context_occurrence_count": len(unseen_held),
                "unseen_held_green_count": unseen_counts["READ"],
                "unseen_held_amber_count": unseen_counts["READ_AMBER"],
                "unseen_held_stop_count": unseen_counts["STOP"],
                "unseen_context_outcome": unseen_outcome,
                "shortcut_never_overrides_live_certificate": "YES",
                "identity_not_inferred": "YES",
                "occurrence_not_predicted": "YES",
            })
            if fold_outcome == "FALSE_SAFE":
                for row in held:
                    if row["context_execution_decision"] != "STOP":
                        continue
                    key = (target_recipe, row["event_id"])
                    critical_rows.append({
                        "critical_id": f"G450-C{len(critical_rows) + 1:04d}",
                        "fold_id": fold_rows[-1]["fold_id"],
                        "held_page": held_page,
                        "target_recipe": target_recipe,
                        "event_id": row["event_id"],
                        "context_id": row["context_id"],
                        "source_recipe": row["source_recipe"],
                        "source_neighbor_edges": "|".join(sorted(source_edges[key])),
                        "incoming_action": row["incoming_action"],
                        "incoming_argument": row["incoming_argument"],
                        "scope_incoming_action": row["scope_incoming_action"],
                        "next_recipe": row["next_recipe"],
                        "blocked_factor_rules": row["context_blocked_factor_rules"],
                        "training_shortcut_class": train_class,
                        "live_certificate_decision": "STOP",
                        "required_action": "LIVE_CERTIFICATE_OVERRIDES_SHORTCUT__STOP",
                    })

    for stale in OUT.glob("gdt450_target_page_folds_part*.tsv"):
        stale.unlink()
    shard_paths: list[str] = []
    for start in range(0, len(fold_rows), SHARD_SIZE):
        path = OUT / f"gdt450_target_page_folds_part{start // SHARD_SIZE + 1:02d}.tsv"
        write_tsv(path, fold_rows[start:start + SHARD_SIZE])
        shard_paths.append(str(path.relative_to(ROOT)))
    write_tsv(
        OUT / "gdt450_false_safe_cases.tsv",
        critical_rows,
        [
            "critical_id", "fold_id", "held_page", "target_recipe", "event_id", "context_id",
            "source_recipe", "source_neighbor_edges", "incoming_action", "incoming_argument",
            "scope_incoming_action", "next_recipe", "blocked_factor_rules",
            "training_shortcut_class", "live_certificate_decision", "required_action",
        ],
    )

    page_rows: list[dict[str, object]] = []
    for page in sorted({row["held_page"] for row in fold_rows}):
        selected = [row for row in fold_rows if row["held_page"] == page]
        counts = Counter(str(row["holdout_outcome"]) for row in selected)
        unseen_counts = Counter(str(row["unseen_context_outcome"]) for row in selected)
        page_rows.append({
            "held_page": page,
            "target_fold_count": len(selected),
            "correct_readable_count": counts["CORRECT_READABLE"],
            "correct_stop_count": counts["CORRECT_STOP"],
            "false_safe_count": counts["FALSE_SAFE"],
            "false_stop_count": counts["FALSE_STOP"],
            "mixed_training_abstention_count": counts["ABSTAIN_TRAIN_MIXED"],
            "no_training_count": counts["NO_OTHER_PAGE_TRAINING"],
            "unseen_context_false_safe_count": unseen_counts["FALSE_SAFE"],
            "unseen_context_false_stop_count": unseen_counts["FALSE_STOP"],
            "unseen_context_probe_count": sum(int(row["unseen_held_context_occurrence_count"]) for row in selected),
        })
    write_tsv(OUT / "gdt450_page_holdout_summary.tsv", page_rows)

    outcomes = Counter(str(row["holdout_outcome"]) for row in fold_rows)
    unseen_outcomes = Counter(str(row["unseen_context_outcome"]) for row in fold_rows)
    result = {
        "status": "PAGE_HOLDOUT_REJECTS_ROBUSTNESS_SHORTCUT_AS_EXECUTION_OVERRIDE",
        "raw_weighted_occurrence_probe_count": len(raw_occurrences),
        "unique_target_event_probe_count": len(target_event),
        "unique_target_count": len(by_target),
        "target_page_fold_count": len(fold_rows),
        "physical_page_count": len(page_rows),
        "fold_shards": shard_paths,
        "holdout_outcome_counts": dict(sorted(outcomes.items())),
        "unseen_context_outcome_counts": dict(sorted(unseen_outcomes.items())),
        "false_safe_fold_count": outcomes["FALSE_SAFE"],
        "false_safe_stop_occurrence_count": len(critical_rows),
        "false_safe_target_count": len({row["target_recipe"] for row in critical_rows}),
        "false_safe_page_count": len({row["held_page"] for row in critical_rows}),
        "unseen_context_false_safe_fold_count": unseen_outcomes["FALSE_SAFE"],
        "shortcut_execution_overrides_allowed": 0,
        "identity_promotions": 0,
        "meaning_revisions": 0,
        "surface_predictions": 0,
        "occurrence_predictions": 0,
        "new_pages": 0,
    }
    (OUT / "gdt450_result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
