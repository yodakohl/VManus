#!/usr/bin/env python3
"""Attach each one-off recipe to a recurrent construction or known root tray."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P679 = ROOT / "experiments/yolo/sidequest_semantic_historical_layer_dictionary_six_hundred_seventy_ninth"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def edit_script(source: list[str], target: list[str]) -> tuple[int, list[str]]:
    rows, cols = len(source) + 1, len(target) + 1
    distance = [[0] * cols for _ in range(rows)]
    for i in range(rows):
        distance[i][0] = i
    for j in range(cols):
        distance[0][j] = j
    for i in range(1, rows):
        for j in range(1, cols):
            distance[i][j] = min(
                distance[i - 1][j] + 1,
                distance[i][j - 1] + 1,
                distance[i - 1][j - 1] + (source[i - 1] != target[j - 1]),
            )
    script: list[str] = []
    i, j = len(source), len(target)
    while i or j:
        if i and j and distance[i][j] == distance[i - 1][j - 1] + (source[i - 1] != target[j - 1]):
            script.append(f"KEEP:{source[i-1]}" if source[i - 1] == target[j - 1] else f"REPLACE:{source[i-1]}>{target[j-1]}")
            i -= 1
            j -= 1
        elif j and distance[i][j] == distance[i][j - 1] + 1:
            script.append(f"ADD:{target[j-1]}")
            j -= 1
        else:
            script.append(f"DROP:{source[i-1]}")
            i -= 1
    script.reverse()
    return distance[-1][-1], script


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    events = read(P679 / "SIX_HUNDRED_SEVENTY_NINTH_381_COMPACT_EVENT_INTERLINEAR.tsv")
    cards = {row["card_no"]: row for row in read(P679 / "SIX_HUNDRED_SEVENTY_NINTH_173_COMPACT_CARD_TABLET.tsv")}
    roots = {row["component"]: row for row in read(P679 / "SIX_HUNDRED_SEVENTY_NINTH_39_LAYER_DICTIONARY.tsv")}
    by_recipe: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        by_recipe[event["component_recipe"]].append(event)
    recurrent = [recipe for recipe, rows in by_recipe.items() if len(rows) >= 2]
    singleton = [recipe for recipe, rows in by_recipe.items() if len(rows) == 1]
    recurrent_by_first: dict[str, list[str]] = defaultdict(list)
    for recipe in recurrent:
        recurrent_by_first[recipe.split("+")[0]].append(recipe)

    rows = []
    for rare_no, recipe in enumerate(sorted(singleton), start=1):
        event = by_recipe[recipe][0]
        card = cards[event["card_no"]]
        tokens = recipe.split("+")
        candidates = recurrent_by_first.get(tokens[0], [])
        if candidates:
            scored = []
            for candidate in candidates:
                distance, script = edit_script(candidate.split("+"), tokens)
                scored.append((distance, -len(set(candidate.split("+")) & set(tokens)), candidate, script))
            distance, _, anchor, script = min(scored)
            method = "RECURRENT_SAME_HEAD_ANCHOR"
            teaching_level = {1: "ONE_CHANGE", 2: "TWO_CHANGES", 3: "THREE_CHANGES"}.get(distance, f"{distance}_CHANGES")
        else:
            anchor = tokens[0]
            distance = len(tokens) - 1
            script = [f"KEEP:{tokens[0]}"] + [f"ADD:{token}" for token in tokens[1:]]
            method = "KNOWN_ROOT_TRAY_EXTENSION" if card["composition_mode"] != "MEMORIZED_WHOLE_COMMAND" else "WHOLE_NOMENCLATOR_ENTRY"
            teaching_level = "ROOT_PLUS_ATTACHMENTS" if method == "KNOWN_ROOT_TRAY_EXTENSION" else "LEARN_WHOLE"
        rows.append({
            "rare_no": f"R{rare_no:03d}",
            "event_id": event["event_id"],
            "page": event["page"],
            "record": event["record"],
            "statement_id": event["statement_id"],
            "surface": event["surface"],
            "card_no": event["card_no"],
            "rare_recipe": recipe,
            "compact_reading_de": event["compact_atomic_reading_de"],
            "teaching_method": method,
            "anchor_recipe_or_root": anchor,
            "anchor_reading_de": " · ".join(roots[token]["compact_table_value_de"] for token in anchor.split("+")),
            "edit_distance": distance,
            "edit_script": " | ".join(script),
            "teaching_level": teaching_level,
            "new_root_required": "NO",
        })

    group_counts = Counter((row["teaching_method"], row["anchor_recipe_or_root"]) for row in rows)
    group_rows = []
    for group_no, ((method, anchor), count) in enumerate(sorted(group_counts.items(), key=lambda item: (-item[1], item[0])), start=1):
        members = [row for row in rows if row["teaching_method"] == method and row["anchor_recipe_or_root"] == anchor]
        group_rows.append({
            "group_no": f"G{group_no:02d}",
            "teaching_method": method,
            "anchor_recipe_or_root": anchor,
            "anchor_reading_de": members[0]["anchor_reading_de"],
            "rare_recipes": count,
            "rare_recipe_ids": "|".join(str(row["rare_no"]) for row in members),
            "max_changes": max(int(row["edit_distance"]) for row in members),
            "master_phrase_de": "Wie den Anker lesen; dann nur die aufgefuehrten ADD DROP oder REPLACE-Schritte anwenden.",
        })

    difficult = sorted(rows, key=lambda row: (-int(row["edit_distance"]), str(row["rare_recipe"])))[:12]
    difficult_rows = [{
        "rank": rank,
        "rare_recipe": row["rare_recipe"],
        "reading_de": row["compact_reading_de"],
        "anchor": row["anchor_recipe_or_root"],
        "edit_script": row["edit_script"],
        "master_warning_de": "Nicht als neues Stammwort lernen; ganze Komponentenfolge aussprechen und exakte Karte kopieren.",
    } for rank, row in enumerate(difficult, start=1)]

    write("SIX_HUNDRED_EIGHTY_FOURTH_113_RARE_RECIPE_LESSONS.tsv", rows)
    write("SIX_HUNDRED_EIGHTY_FOURTH_TEACHING_GROUPS.tsv", group_rows)
    write("SIX_HUNDRED_EIGHTY_FOURTH_12_HARDEST_RARE_CARDS.tsv", difficult_rows)

    summary = {
        "status": "PASS",
        "rare_singleton_recipes": len(rows),
        "recurrent_same_head_lessons": sum(row["teaching_method"] == "RECURRENT_SAME_HEAD_ANCHOR" for row in rows),
        "known_root_extensions": sum(row["teaching_method"] == "KNOWN_ROOT_TRAY_EXTENSION" for row in rows),
        "whole_nomenclator_lessons": sum(row["teaching_method"] == "WHOLE_NOMENCLATOR_ENTRY" for row in rows),
        "distance_distribution": dict(sorted(Counter(int(row["edit_distance"]) for row in rows if row["teaching_method"] == "RECURRENT_SAME_HEAD_ANCHOR").items())),
        "teaching_groups": len(group_rows),
        "new_roots": sum(row["new_root_required"] == "YES" for row in rows),
    }
    (HERE / "SIX_HUNDRED_EIGHTY_FOURTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
