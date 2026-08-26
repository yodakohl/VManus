#!/usr/bin/env python3
"""Repair the over-broad GDT426 action-class prediction gate."""

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
BASE = ROOT / "experiments/yolo/gdt427_typed_prediction_specificity_repair"
OUT = BASE / "artifacts"
CLAUSES = ROOT / "experiments/yolo/gdt416_owner_local_imperative_sentence_compiler/artifacts/gdt416_4576_imperative_clauses.tsv"
FOCUS = ROOT / "experiments/yolo/gdt425_complete_factorized_action_portability/artifacts/gdt425_5051_focus_edge_portability.tsv"
LOCAL = ROOT / "experiments/yolo/gdt425_complete_factorized_action_portability/artifacts/gdt425_9_local_action_appendix.tsv"

ACTIONS = ("CH", "S", "K", "OK", "P", "SH", "CHD", "T", "R")
FOCUS_FAMILY = {
    "E": "GRADE", "EE": "GRADE", "EEE": "GRADE",
    "Y": "ITEM", "AIIN": "ITEM", "AIN": "ITEM", "OR": "ITEM",
    "AL": "RELATION", "AR": "RELATION", "L": "RELATION", "AIR": "RELATION",
}
MODELS = {
    "M4_GDT426": (("CH", "S"), ("K", "OK", "P"), ("SH", "CHD"), ("T", "R")),
    "M5_SPLIT_K": (("CH", "S"), ("K",), ("OK", "P"), ("SH", "CHD"), ("T", "R")),
    "M5_SPLIT_P": (("CH", "S"), ("K", "OK"), ("P",), ("SH", "CHD"), ("T", "R")),
    "M5_SPLIT_SELECT": (("CH",), ("S",), ("K", "OK", "P"), ("SH", "CHD"), ("T", "R")),
    "M5_SPLIT_HOLD_PROCESS": (("CH", "S"), ("K", "OK", "P"), ("SH",), ("CHD",), ("T", "R")),
    "M5_SPLIT_CONTROL_SELECTED": (("CH", "S"), ("K", "OK", "P"), ("SH", "CHD"), ("T",), ("R",)),
    "M5_SPLIT_OK": (("CH", "S"), ("K", "P"), ("OK",), ("SH", "CHD"), ("T", "R")),
}
SELECTED = "M5_SPLIT_CONTROL_SELECTED"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def class_map(groups: tuple[tuple[str, ...], ...]) -> dict[str, str]:
    return {action: f"C{index + 1}_{'_'.join(group)}" for index, group in enumerate(groups) for action in group}


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    clauses = read_tsv(CLAUSES)
    focus_rows = read_tsv(FOCUS)
    local_rows = read_tsv(LOCAL)

    pair_pages: dict[tuple[str, str], set[str]] = defaultdict(set)
    pair_events: Counter[tuple[str, str]] = Counter()
    for row in clauses:
        actions = [atom for atom in row["component_recipe"].split("+") if atom in ACTIONS]
        for left, right in zip(actions, actions[1:]):
            pair_pages[(left, right)].add(row["physical_page"])
            pair_events[(left, right)] += 1
    all_pairs = {(left, right) for left in ACTIONS for right in ACTIONS}
    absent_pairs = all_pairs - set(pair_pages)
    singleton_pairs = sorted((left, right, next(iter(pages))) for (left, right), pages in pair_pages.items() if len(pages) == 1)

    model_rows: list[dict[str, object]] = []
    model_maps: dict[str, dict[str, str]] = {}
    model_transition_pages: dict[str, dict[tuple[str, str], set[str]]] = {}
    for name, groups in MODELS.items():
        mapping = class_map(groups)
        model_maps[name] = mapping
        transition_pages: dict[tuple[str, str], set[str]] = defaultdict(set)
        for (left, right), pages in pair_pages.items():
            transition_pages[(mapping[left], mapping[right])].update(pages)
        model_transition_pages[name] = transition_pages
        true_positive = sum(bool(transition_pages[(mapping[left], mapping[right])] - {page}) for left, right, page in singleton_pairs)
        false_negative = len(singleton_pairs) - true_positive
        false_positive = sum(bool(transition_pages[(mapping[left], mapping[right])]) for left, right in absent_pairs)
        true_negative = len(absent_pairs) - false_positive
        sensitivity = true_positive / len(singleton_pairs)
        specificity = true_negative / len(absent_pairs)
        balanced = (sensitivity + specificity) / 2
        model_rows.append({
            "model_id": name,
            "class_count": len(groups),
            "class_definition": "|".join("/".join(group) for group in groups),
            "filled_transition_count": sum(bool(pages) for pages in transition_pages.values()),
            "possible_transition_count": len(groups) ** 2,
            "singleton_pair_true_positive": true_positive,
            "singleton_pair_false_negative": false_negative,
            "absent_pair_false_positive": false_positive,
            "absent_pair_true_negative": true_negative,
            "sensitivity": f"{sensitivity:.6f}",
            "specificity": f"{specificity:.6f}",
            "balanced_accuracy": f"{balanced:.6f}",
            "selection": "SELECTED" if name == SELECTED else "NOT_SELECTED",
        })

    selected_map = model_maps[SELECTED]
    selected_transitions = model_transition_pages[SELECTED]
    singleton_rows: list[dict[str, object]] = []
    for left, right, page in singleton_pairs:
        other_pages = sorted(selected_transitions[(selected_map[left], selected_map[right])] - {page})
        singleton_rows.append({
            "ordered_pair": f"{left}>{right}",
            "only_page": page,
            "event_count": pair_events[(left, right)],
            "typed_transition": f"{selected_map[left]}>{selected_map[right]}",
            "other_support_pages": "|".join(other_pages) if other_pages else "NONE",
            "prediction": "AMBER_PREDICTED" if other_pages else "RED_LOCAL",
        })

    absent_rows: list[dict[str, object]] = []
    for left, right in sorted(absent_pairs):
        support_pages = sorted(selected_transitions[(selected_map[left], selected_map[right])])
        absent_rows.append({
            "ordered_pair": f"{left}>{right}",
            "typed_transition": f"{selected_map[left]}>{selected_map[right]}",
            "transition_support_pages": "|".join(support_pages) if support_pages else "NONE",
            "negative_control_result": "FALSE_AMBER_ALLOWED" if support_pages else "TRUE_RED_BLOCKED",
        })

    focus_edge_pages: dict[tuple[str, str], set[str]] = defaultdict(set)
    head_family_pages: dict[tuple[str, str], set[str]] = defaultdict(set)
    focus_value_pages: dict[str, set[str]] = defaultdict(set)
    class_exact_focus_pages: dict[tuple[str, str], set[str]] = defaultdict(set)
    for row in focus_rows:
        action, focus = row["action_core"], row["focus_core"]
        if action not in selected_map or focus not in FOCUS_FAMILY:
            continue
        page = row["physical_page"]
        family = FOCUS_FAMILY[focus]
        focus_edge_pages[(action, focus)].add(page)
        head_family_pages[(action, family)].add(page)
        focus_value_pages[focus].add(page)
        class_exact_focus_pages[(selected_map[action], focus)].add(page)

    local_decisions: list[dict[str, object]] = []
    for row in local_rows:
        rule = row["rule_id"]
        page = row["pages"]
        if rule.startswith("PAIR:"):
            left, right = rule.removeprefix("PAIR:").split(">")
            exact_other = sorted(pair_pages[(left, right)] - {page})
            class_other = sorted(selected_transitions[(selected_map[left], selected_map[right])] - {page})
            if exact_other:
                status = "AMBER_EXACT_PAIR_OTHER_PAGE"
            elif class_other:
                status = "AMBER_SELECTED_CLASS_TRANSITION"
            else:
                status = "RED_LOCAL_AFTER_SPECIFICITY_REPAIR"
            typed = f"{selected_map[left]}>{selected_map[right]}"
            evidence = f"exact={len(exact_other)}:{'|'.join(exact_other) if exact_other else 'NONE'};class={len(class_other)}:{'|'.join(class_other) if class_other else 'NONE'}"
        else:
            action, focus = rule.removeprefix("FOCUS:").split("<-")
            family = FOCUS_FAMILY[focus]
            head_other = sorted(head_family_pages[(action, family)] - {page})
            value_other = sorted(focus_value_pages[focus] - {page})
            class_exact_other = sorted(class_exact_focus_pages[(selected_map[action], focus)] - {page})
            if head_other and value_other:
                status = "AMBER_HEAD_FOCUS_RECTANGLE"
            elif class_exact_other:
                status = "AMBER_SELECTED_CLASS_FOCUS"
            else:
                status = "RED_LOCAL_AFTER_SPECIFICITY_REPAIR"
            typed = f"{selected_map[action]}<-{family}"
            evidence = f"head_family={len(head_other)}:{'|'.join(head_other) if head_other else 'NONE'};focus_other={len(value_other)}:{'|'.join(value_other) if value_other else 'NONE'};class_exact={len(class_exact_other)}:{'|'.join(class_exact_other) if class_exact_other else 'NONE'}"
        local_decisions.append({
            "rule_id": rule,
            "page": page,
            "surface": row["surfaces"],
            "selected_typed_rule": typed,
            "support": evidence,
            "specificity_repaired_status": status,
        })

    transition_rows: list[dict[str, object]] = []
    selected_classes = tuple(dict.fromkeys(selected_map[action] for action in ACTIONS))
    for left_class in selected_classes:
        for right_class in selected_classes:
            pages = selected_transitions[(left_class, right_class)]
            transition_rows.append({
                "left_class": left_class,
                "right_class": right_class,
                "typed_transition": f"{left_class}>{right_class}",
                "page_count": len(pages),
                "pages": "|".join(sorted(pages)) if pages else "NONE",
                "transition_status": "ATTESTED" if pages else "EMPTY_RED",
            })

    write_tsv(OUT / "gdt427_7_model_specificity_comparison.tsv", model_rows, list(model_rows[0]))
    write_tsv(OUT / "gdt427_15_singleton_pair_leaveout.tsv", singleton_rows, list(singleton_rows[0]))
    write_tsv(OUT / "gdt427_17_absent_pair_negative_controls.tsv", absent_rows, list(absent_rows[0]))
    write_tsv(OUT / "gdt427_9_local_rule_reclassification.tsv", local_decisions, list(local_decisions[0]))
    write_tsv(OUT / "gdt427_25_selected_transition_atlas.tsv", transition_rows, list(transition_rows[0]))

    card = [
        "# Fünfklassen-Gate", "",
        "SELECT=CH/S; MOVE_SET=K/OK/P; HOLD_PROCESS=SH/CHD; SET_CONTROL=T; MARK_CONTROL=R.", "",
        "- 12/15 einseitige echte Paare werden aus anderen Seiten vorhergesagt.",
        "- 7/17 nie beobachtete Paare werden rot blockiert.",
        "- Sieben der neun lokalen Aktionskarten bleiben gelb.",
        "- `PAIR:R>T` und `FOCUS:R<-EE` bleiben rot-lokal.",
        "- Fokusfamilien bleiben eine schwache Lesebrücke, kein Negativfilter.",
    ]
    (OUT / "SELECTED_FIVE_CLASS_GATE.md").write_text("\n".join(card) + "\n", encoding="utf-8")

    selected_row = next(row for row in model_rows if row["model_id"] == SELECTED)
    result = {
        "status": "FIVE_CLASS_SPECIFICITY_GATE_SELECTED__SEVEN_AMBER_TWO_LOCAL",
        "model_count": len(model_rows),
        "selected_model": SELECTED,
        "selected_class_count": 5,
        "selected_filled_transition_count": int(selected_row["filled_transition_count"]),
        "selected_possible_transition_count": int(selected_row["possible_transition_count"]),
        "singleton_pair_true_positive": int(selected_row["singleton_pair_true_positive"]),
        "singleton_pair_false_negative": int(selected_row["singleton_pair_false_negative"]),
        "absent_pair_false_positive": int(selected_row["absent_pair_false_positive"]),
        "absent_pair_true_negative": int(selected_row["absent_pair_true_negative"]),
        "selected_balanced_accuracy": selected_row["balanced_accuracy"],
        "local_rule_amber_count": sum(row["specificity_repaired_status"].startswith("AMBER") for row in local_decisions),
        "local_rule_red_count": sum(row["specificity_repaired_status"].startswith("RED") for row in local_decisions),
        "new_roots": 0,
        "dictionary_revisions": 0,
        "new_pages": 0,
    }
    (OUT / "gdt427_result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
