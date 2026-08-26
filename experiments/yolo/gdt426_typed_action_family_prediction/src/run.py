#!/usr/bin/env python3
"""Turn the nine local action cards into typed, explicit amber predictions."""

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
BASE = ROOT / "experiments/yolo/gdt426_typed_action_family_prediction"
OUT = BASE / "artifacts"
CLAUSES = ROOT / "experiments/yolo/gdt416_owner_local_imperative_sentence_compiler/artifacts/gdt416_4576_imperative_clauses.tsv"
FOCUS = ROOT / "experiments/yolo/gdt425_complete_factorized_action_portability/artifacts/gdt425_5051_focus_edge_portability.tsv"
APPENDIX = ROOT / "experiments/yolo/gdt425_complete_factorized_action_portability/artifacts/gdt425_9_local_action_appendix.tsv"

ACTION_CLASSES = {
    "CH": "SELECT", "S": "SELECT",
    "K": "MOVE_SET", "OK": "MOVE_SET", "P": "MOVE_SET",
    "SH": "HOLD_PROCESS", "CHD": "HOLD_PROCESS",
    "T": "CONTROL", "R": "CONTROL",
}
FOCUS_FAMILIES = {
    "E": "GRADE", "EE": "GRADE", "EEE": "GRADE",
    "Y": "ITEM", "AIIN": "ITEM", "AIN": "ITEM", "OR": "ITEM",
    "AL": "RELATION", "AR": "RELATION", "L": "RELATION", "AIR": "RELATION",
}
ACTION_CLASS_NAMES = ("SELECT", "MOVE_SET", "HOLD_PROCESS", "CONTROL")
FOCUS_FAMILY_NAMES = ("GRADE", "ITEM", "RELATION")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    clauses = read_tsv(CLAUSES)
    focus_rows = read_tsv(FOCUS)
    appendix = read_tsv(APPENDIX)

    exact_pair_pages: dict[tuple[str, str], set[str]] = defaultdict(set)
    exact_pair_events: Counter[tuple[str, str]] = Counter()
    class_pair_pages: dict[tuple[str, str], set[str]] = defaultdict(set)
    class_pair_events: Counter[tuple[str, str]] = Counter()
    exact_pair_surfaces: dict[tuple[str, str], set[str]] = defaultdict(set)
    for row in clauses:
        actions = [atom for atom in row["component_recipe"].split("+") if atom in ACTION_CLASSES]
        for left, right in zip(actions, actions[1:]):
            exact_pair_pages[(left, right)].add(row["physical_page"])
            exact_pair_events[(left, right)] += 1
            exact_pair_surfaces[(left, right)].add(row["surface"])
            class_pair = (ACTION_CLASSES[left], ACTION_CLASSES[right])
            class_pair_pages[class_pair].add(row["physical_page"])
            class_pair_events[class_pair] += 1

    focus_edge_pages: dict[tuple[str, str], set[str]] = defaultdict(set)
    head_family_pages: dict[tuple[str, str], set[str]] = defaultdict(set)
    focus_value_other_head_pages: dict[str, set[str]] = defaultdict(set)
    class_exact_focus_pages: dict[tuple[str, str], set[str]] = defaultdict(set)
    class_family_pages: dict[tuple[str, str], set[str]] = defaultdict(set)
    class_family_events: Counter[tuple[str, str]] = Counter()
    class_family_edges: dict[tuple[str, str], set[str]] = defaultdict(set)
    for row in focus_rows:
        action = row["action_core"]
        focus = row["focus_core"]
        if action not in ACTION_CLASSES or focus not in FOCUS_FAMILIES:
            continue
        page = row["physical_page"]
        family = FOCUS_FAMILIES[focus]
        action_class = ACTION_CLASSES[action]
        focus_edge_pages[(action, focus)].add(page)
        head_family_pages[(action, family)].add(page)
        focus_value_other_head_pages[focus].add(page)
        class_exact_focus_pages[(action_class, focus)].add(page)
        class_family_pages[(action_class, family)].add(page)
        class_family_events[(action_class, family)] += 1
        class_family_edges[(action_class, family)].add(f"{action}<-{focus}")

    prediction_rows: list[dict[str, object]] = []
    for row in appendix:
        rule = row["rule_id"]
        page = row["pages"]
        if "|" in page:
            raise RuntimeError(f"appendix rule unexpectedly spans pages: {rule}")
        if rule.startswith("PAIR:"):
            left, right = rule.removeprefix("PAIR:").split(">")
            pair = (left, right)
            class_pair = (ACTION_CLASSES[left], ACTION_CLASSES[right])
            exact_other = sorted(exact_pair_pages[pair] - {page})
            class_other = sorted(class_pair_pages[class_pair] - {page})
            if exact_other:
                decision = "AMBER_EXACT_ORDERED_PAIR_WITH_INTERVENING_SLOTS"
            elif class_other:
                decision = "AMBER_ACTION_CLASS_TRANSITION"
            else:
                decision = "HARD_LOCAL_UNEXPLAINED"
            evidence_a = f"exact_pair_other_pages={len(exact_other)}:{'|'.join(exact_other) if exact_other else 'NONE'}"
            evidence_b = f"class_transition={class_pair[0]}>{class_pair[1]};other_pages={len(class_other)}:{'|'.join(class_other) if class_other else 'NONE'}"
            typed_rule = f"{class_pair[0]}>{class_pair[1]}"
        elif rule.startswith("FOCUS:"):
            action, focus = rule.removeprefix("FOCUS:").split("<-")
            family = FOCUS_FAMILIES[focus]
            action_class = ACTION_CLASSES[action]
            same_head_family_other = sorted(head_family_pages[(action, family)] - {page})
            same_focus_other = sorted(focus_value_other_head_pages[focus] - {page})
            same_class_focus_other = sorted(class_exact_focus_pages[(action_class, focus)] - {page})
            if same_head_family_other and same_focus_other:
                decision = "AMBER_HEAD_FOCUS_FAMILY_RECTANGLE"
            elif same_class_focus_other:
                decision = "AMBER_ACTION_CLASS_FOCUS_FAMILY"
            else:
                decision = "HARD_LOCAL_UNEXPLAINED"
            evidence_a = f"head={action};family={family};other_pages={len(same_head_family_other)}:{'|'.join(same_head_family_other) if same_head_family_other else 'NONE'}"
            evidence_b = f"focus={focus};other_head_pages={len(same_focus_other)}:{'|'.join(same_focus_other) if same_focus_other else 'NONE'};same_class_focus_pages={len(same_class_focus_other)}:{'|'.join(same_class_focus_other) if same_class_focus_other else 'NONE'}"
            typed_rule = f"{action_class}<-{family}"
        else:
            raise RuntimeError(f"unknown appendix rule: {rule}")
        prediction_rows.append({
            "rule_id": rule,
            "rule_type": row["rule_type"],
            "page": page,
            "surface": row["surfaces"],
            "component_recipe": row["component_recipes"],
            "typed_rule": typed_rule,
            "evidence_a": evidence_a,
            "evidence_b": evidence_b,
            "prediction_status": decision,
            "portable_status": "AMBER_TYPED_PREDICTION_NOT_PROMOTED" if decision.startswith("AMBER") else "HARD_LOCAL",
        })

    class_pair_rows: list[dict[str, object]] = []
    for left_class in ACTION_CLASS_NAMES:
        for right_class in ACTION_CLASS_NAMES:
            key = (left_class, right_class)
            exact_pairs = sorted(
                f"{left}>{right}"
                for left in ACTION_CLASSES
                for right in ACTION_CLASSES
                if ACTION_CLASSES[left] == left_class and ACTION_CLASSES[right] == right_class and exact_pair_events[(left, right)]
            )
            class_pair_rows.append({
                "left_action_class": left_class,
                "right_action_class": right_class,
                "typed_transition": f"{left_class}>{right_class}",
                "event_count": class_pair_events[key],
                "page_count": len(class_pair_pages[key]),
                "pages": "|".join(sorted(class_pair_pages[key])) if class_pair_pages[key] else "NONE",
                "attested_exact_pairs": "|".join(exact_pairs) if exact_pairs else "NONE",
                "transition_status": "ATTESTED" if class_pair_events[key] else "EMPTY",
            })

    class_focus_rows: list[dict[str, object]] = []
    for action_class in ACTION_CLASS_NAMES:
        for family in FOCUS_FAMILY_NAMES:
            key = (action_class, family)
            class_focus_rows.append({
                "action_class": action_class,
                "focus_family": family,
                "typed_focus_edge": f"{action_class}<-{family}",
                "event_count": class_family_events[key],
                "page_count": len(class_family_pages[key]),
                "pages": "|".join(sorted(class_family_pages[key])) if class_family_pages[key] else "NONE",
                "attested_exact_edges": "|".join(sorted(class_family_edges[key])) if class_family_edges[key] else "NONE",
                "edge_status": "ATTESTED" if class_family_events[key] else "EMPTY",
            })

    exact_pair_rows: list[dict[str, object]] = []
    for left in ACTION_CLASSES:
        for right in ACTION_CLASSES:
            pages = exact_pair_pages[(left, right)]
            class_pages = class_pair_pages[(ACTION_CLASSES[left], ACTION_CLASSES[right])]
            if len(pages) >= 2:
                status = "ATTESTED_MULTI_PAGE"
            elif len(pages) == 1:
                status = "ATTESTED_ONE_PAGE"
            elif class_pages:
                status = "UNATTESTED_EXACT_PAIR__CLASS_TRANSITION_OLD"
            else:
                status = "UNATTESTED_EXACT_PAIR__CLASS_TRANSITION_EMPTY"
            exact_pair_rows.append({
                "left_action": left,
                "right_action": right,
                "ordered_pair": f"{left}>{right}",
                "left_class": ACTION_CLASSES[left],
                "right_class": ACTION_CLASSES[right],
                "event_count": exact_pair_events[(left, right)],
                "page_count": len(pages),
                "pages": "|".join(sorted(pages)) if pages else "NONE",
                "surface_count": len(exact_pair_surfaces[(left, right)]),
                "pair_status": status,
            })

    write_tsv(OUT / "gdt426_9_typed_local_predictions.tsv", prediction_rows, list(prediction_rows[0]))
    write_tsv(OUT / "gdt426_16_action_class_transition_atlas.tsv", class_pair_rows, list(class_pair_rows[0]))
    write_tsv(OUT / "gdt426_12_action_class_focus_family_atlas.tsv", class_focus_rows, list(class_focus_rows[0]))
    write_tsv(OUT / "gdt426_81_exact_action_pair_status.tsv", exact_pair_rows, list(exact_pair_rows[0]))

    card = [
        "# Gelbe Vorhersagekarte für lokale Handlungsformen", "",
        "Vier Handlungsklassen: SELECT, MOVE_SET, HOLD_PROCESS, CONTROL.",
        "Drei Fokusfamilien: GRADE, ITEM, RELATION.", "",
    ]
    for row in prediction_rows:
        card.append(f"- `{row['rule_id']}` → `{row['typed_rule']}` → {row['prediction_status']}")
    card.extend([
        "", "Diese neun Formen sind damit typisiert vorhersagbar, bleiben aber gelb.",
        "Eine neue Seite darf ihre genaue Karte bestätigen; sie darf die Klassen nicht nachträglich verändern.",
    ])
    (OUT / "TYPED_LOCAL_PREDICTION_CARD.md").write_text("\n".join(card) + "\n", encoding="utf-8")

    decision_counts = Counter(row["prediction_status"] for row in prediction_rows)
    pair_status_counts = Counter(row["pair_status"] for row in exact_pair_rows)
    result = {
        "status": "NINE_LOCAL_ACTION_CARDS_TYPED_AS_AMBER_PREDICTIONS",
        "local_rule_count": len(prediction_rows),
        "prediction_status_counts": dict(sorted(decision_counts.items())),
        "hard_local_unexplained_count": decision_counts["HARD_LOCAL_UNEXPLAINED"],
        "action_class_count": len(ACTION_CLASS_NAMES),
        "action_class_transition_cell_count": len(class_pair_rows),
        "attested_action_class_transition_count": sum(row["transition_status"] == "ATTESTED" for row in class_pair_rows),
        "focus_family_count": len(FOCUS_FAMILY_NAMES),
        "action_class_focus_cell_count": len(class_focus_rows),
        "attested_action_class_focus_count": sum(row["edge_status"] == "ATTESTED" for row in class_focus_rows),
        "exact_action_pair_cell_count": len(exact_pair_rows),
        "exact_action_pair_status_counts": dict(sorted(pair_status_counts.items())),
        "new_roots": 0,
        "dictionary_revisions": 0,
        "new_pages": 0,
    }
    (OUT / "gdt426_result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
