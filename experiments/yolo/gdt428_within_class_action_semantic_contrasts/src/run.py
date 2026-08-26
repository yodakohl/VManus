#!/usr/bin/env python3
"""Build direct semantic contrast cards for the nine working action roots."""

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
BASE = ROOT / "experiments/yolo/gdt428_within_class_action_semantic_contrasts"
OUT = BASE / "artifacts"
CLAUSES = ROOT / "experiments/yolo/gdt416_owner_local_imperative_sentence_compiler/artifacts/gdt416_4576_imperative_clauses.tsv"
FOCUS = ROOT / "experiments/yolo/gdt425_complete_factorized_action_portability/artifacts/gdt425_5051_focus_edge_portability.tsv"
CLOSE = ROOT / "experiments/yolo/gdt425_complete_factorized_action_portability/artifacts/gdt425_639_close_edge_portability.tsv"
DICTIONARY = ROOT / "experiments/yolo/gdt413_twenty_six_page_semantic_working_edition/artifacts/gdt413_46_component_working_dictionary.tsv"

ACTIONS = ("CH", "S", "K", "OK", "P", "SH", "CHD", "T", "R")
CONTRASTS = (
    ("SELECT", "CH", "S"),
    ("MOVE_SET", "K", "OK"),
    ("MOVE_SET", "K", "P"),
    ("MOVE_SET", "OK", "P"),
    ("HOLD_PROCESS", "SH", "CHD"),
    ("CONTROL_SPLIT", "T", "R"),
)
FOCUS_FAMILIES = {
    "E": "GRADE", "EE": "GRADE", "EEE": "GRADE",
    "Y": "ITEM", "AIIN": "ITEM", "AIN": "ITEM", "OR": "ITEM",
    "AL": "RELATION", "AR": "RELATION", "L": "RELATION", "AIR": "RELATION",
}
ROOT_CONTRACT = {
    "CH": ("etwas aus dem Besitzerkontext nehmen und in den Arbeitsgang geben", "BEARBEITEN", "NEHMEN"),
    "S": ("unter vorhandenen Posten, Werten oder Anteilen auswählen", "PRÜFEN", "WÄHLEN"),
    "K": ("den genommenen Posten an den nächsten Empfänger oder Zustand geben", "FÜHREN", "GEBEN"),
    "OK": ("einen Posten oder Zustand als laufende Einstellung setzen", "BEGINNEN", "SETZEN"),
    "P": ("einen Posten in einen nachfolgenden Arbeitsgang einsetzen", "VERWENDEN", "EINSETZEN"),
    "SH": ("einen Posten unter einer angegebenen Stufe halten", "RUHEN", "HALTEN"),
    "CHD": ("den laufenden Posten ohne eigene Gradstufe weiterbearbeiten", "ABSCHLIESSEN", "BEARBEITEN"),
    "T": ("einen Posten, Wert oder Grad als Einstellung festlegen", "MISCHEN", "EINSTELLEN"),
    "R": ("einen Posten oder Wert als Bezug markieren", "WIEDERHOLEN", "MARKIEREN"),
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def pct(numerator: int, denominator: int) -> str:
    return f"{numerator}/{denominator} ({100 * numerator / denominator:.1f}%)"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    clauses = read_tsv(CLAUSES)
    focus_rows = read_tsv(FOCUS)
    close_rows = read_tsv(CLOSE)
    dictionary = read_tsv(DICTIONARY)
    meanings = {row["atom"]: row["working_value_de"] for row in dictionary}

    profiles: dict[str, dict[str, object]] = {
        action: {
            "mention_count": 0,
            "events": set(),
            "pages": set(),
            "registers": set(),
            "register_counter": Counter(),
            "position": Counter(),
            "previous": Counter(),
            "next": Counter(),
            "focus": Counter(),
            "focus_family": Counter(),
            "close_source": Counter(),
        }
        for action in ACTIONS
    }

    by_recipe: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in clauses:
        by_recipe[row["component_recipe"]].append(row)
        action_chain = [atom for atom in row["component_recipe"].split("+") if atom in ACTIONS]
        for index, action in enumerate(action_chain):
            profile = profiles[action]
            profile["mention_count"] += 1
            profile["events"].add(row["global_running_event_id"])
            profile["pages"].add(row["physical_page"])
            profile["registers"].add(row["register"])
            profile["register_counter"][row["register"]] += 1
            if len(action_chain) == 1:
                position = "ONLY"
            elif index == 0:
                position = "FIRST"
            elif index == len(action_chain) - 1:
                position = "LAST"
            else:
                position = "MEDIAL"
            profile["position"][position] += 1
            profile["previous"][action_chain[index - 1] if index else "START"] += 1
            profile["next"][action_chain[index + 1] if index + 1 < len(action_chain) else "END"] += 1

    for row in focus_rows:
        action = row["action_core"]
        focus = row["focus_core"]
        if action not in profiles:
            continue
        profiles[action]["focus"][focus] += 1
        profiles[action]["focus_family"][FOCUS_FAMILIES[focus]] += 1

    for row in close_rows:
        action = row["close_target_action"]
        if action in profiles:
            profiles[action]["close_source"][row["target_source"]] += 1

    # An exact substitution frame replaces one action atom while freezing every
    # other atom and its position. It is the clearest evidence that two roots
    # occupy the same compositional slot without being the same root.
    substitution_index: dict[tuple[str, ...], dict[str, dict[str, object]]] = defaultdict(
        lambda: defaultdict(lambda: {"events": 0, "recipes": set(), "pages": set(), "registers": set(), "surfaces": set()})
    )
    for recipe, rows in by_recipe.items():
        atoms = recipe.split("+")
        for index, atom in enumerate(atoms):
            if atom not in ACTIONS:
                continue
            frame = tuple(atoms[:index] + ["@ACTION"] + atoms[index + 1:])
            cell = substitution_index[frame][atom]
            cell["events"] += len(rows)
            cell["recipes"].add(recipe)
            cell["pages"].update(row["physical_page"] for row in rows)
            cell["registers"].update(row["register"] for row in rows)
            cell["surfaces"].update(row["surface"] for row in rows)

    substitution_rows: list[dict[str, object]] = []
    pair_frame_counts: Counter[tuple[str, str]] = Counter()
    pair_frame_events: Counter[tuple[str, str]] = Counter()
    for family, left, right in CONTRASTS:
        for frame, members in sorted(substitution_index.items()):
            if left not in members or right not in members:
                continue
            left_cell, right_cell = members[left], members[right]
            pair_frame_counts[(left, right)] += 1
            pair_frame_events[(left, right)] += int(left_cell["events"]) + int(right_cell["events"])
            substitution_rows.append({
                "family": family,
                "contrast_pair": f"{left}~{right}",
                "frozen_frame": "+".join(frame),
                "left_root": left,
                "left_meaning_de": meanings[left],
                "left_event_count": left_cell["events"],
                "left_page_count": len(left_cell["pages"]),
                "left_pages": "|".join(sorted(left_cell["pages"])),
                "left_registers": "|".join(sorted(left_cell["registers"])),
                "left_surfaces": "|".join(sorted(left_cell["surfaces"])),
                "right_root": right,
                "right_meaning_de": meanings[right],
                "right_event_count": right_cell["events"],
                "right_page_count": len(right_cell["pages"]),
                "right_pages": "|".join(sorted(right_cell["pages"])),
                "right_registers": "|".join(sorted(right_cell["registers"])),
                "right_surfaces": "|".join(sorted(right_cell["surfaces"])),
                "reading_rule_de": f"Gleicher Rahmen; {left} liest {meanings[left]}, {right} liest {meanings[right]}",
            })

    profile_rows: list[dict[str, object]] = []
    for action in ACTIONS:
        p = profiles[action]
        mentions = int(p["mention_count"])
        focus = p["focus"]
        focus_family = p["focus_family"]
        grade = int(focus_family["GRADE"])
        item = int(focus_family["ITEM"])
        relation = int(focus_family["RELATION"])
        closes = sum(p["close_source"].values())
        definition, rival, selected = ROOT_CONTRACT[action]
        profile_rows.append({
            "action_root": action,
            "working_meaning_de": meanings[action],
            "operational_definition_de": definition,
            "mention_count": mentions,
            "event_count": len(p["events"]),
            "page_count": len(p["pages"]),
            "register_count": len(p["registers"]),
            "only_count": p["position"]["ONLY"],
            "first_count": p["position"]["FIRST"],
            "medial_count": p["position"]["MEDIAL"],
            "last_count": p["position"]["LAST"],
            "chain_end_count": p["next"]["END"],
            "preceded_by_CH_count": p["previous"]["CH"],
            "followed_by_K_T_P_count": sum(p["next"][root] for root in ("K", "T", "P")),
            "followed_by_CH_SH_CHD_count": sum(p["next"][root] for root in ("CH", "SH", "CHD")),
            "focus_edge_count": sum(focus.values()),
            "grade_focus_count": grade,
            "item_focus_count": item,
            "value_share_focus_count": focus["AIIN"] + focus["AIN"],
            "relation_focus_count": relation,
            "focus_breakdown": "|".join(f"{key}:{focus[key]}" for key in sorted(focus)),
            "close_target_count": closes,
            "explicit_close_count": p["close_source"]["EXPLICIT_LAST_ACTION"],
            "inherited_close_count": p["close_source"]["INHERITED_ACTION"],
            "strongest_rival_de": rival,
            "decision": f"KEEP_{selected}",
        })

    def prof(action: str) -> dict[str, object]:
        return profiles[action]

    contrast_evidence = {
        ("CH", "S"): (
            f"CH→K/T/P {pct(sum(prof('CH')['next'][x] for x in ('K','T','P')), int(prof('CH')['mention_count']))}; "
            f"S→K/T/P {pct(sum(prof('S')['next'][x] for x in ('K','T','P')), int(prof('S')['mention_count']))}. "
            f"S bindet AIIN/AIN {profiles['S']['focus']['AIIN'] + profiles['S']['focus']['AIN']}×, CH {profiles['CH']['focus']['AIIN'] + profiles['CH']['focus']['AIN']}×."
        ),
        ("K", "OK"): (
            f"K folgt CH {pct(prof('K')['previous']['CH'], int(prof('K')['mention_count']))}, OK nur {pct(prof('OK')['previous']['CH'], int(prof('OK')['mention_count']))}; "
            f"OK steht als einzige Handlung {pct(prof('OK')['position']['ONLY'], int(prof('OK')['mention_count']))}, K {pct(prof('K')['position']['ONLY'], int(prof('K')['mention_count']))}."
        ),
        ("K", "P"): (
            f"P führt zu CH/SH/CHD {pct(sum(prof('P')['next'][x] for x in ('CH','SH','CHD')), int(prof('P')['mention_count']))}; "
            f"K nur {pct(sum(prof('K')['next'][x] for x in ('CH','SH','CHD')), int(prof('K')['mention_count']))}. "
            f"K endet die Handlungskette {pct(prof('K')['next']['END'], int(prof('K')['mention_count']))}, P {pct(prof('P')['next']['END'], int(prof('P')['mention_count']))}."
        ),
        ("OK", "P"): (
            f"OK steht allein {pct(prof('OK')['position']['ONLY'], int(prof('OK')['mention_count']))}; P {pct(prof('P')['position']['ONLY'], int(prof('P')['mention_count']))}. "
            f"P öffnet CH/SH/CHD {pct(sum(prof('P')['next'][x] for x in ('CH','SH','CHD')), int(prof('P')['mention_count']))}, OK {pct(sum(prof('OK')['next'][x] for x in ('CH','SH','CHD')), int(prof('OK')['mention_count']))}."
        ),
        ("SH", "CHD"): (
            f"SH trägt {sum(prof('SH')['focus'][x] for x in ('E','EE','EEE'))} Gradbindungen; CHD nur {sum(prof('CHD')['focus'][x] for x in ('E','EE','EEE'))}. "
            f"CHD endet die Handlungskette {pct(prof('CHD')['next']['END'], int(prof('CHD')['mention_count']))}, SH {pct(prof('SH')['next']['END'], int(prof('SH')['mention_count']))}."
        ),
        ("T", "R"): (
            f"T trägt {sum(prof('T')['focus'][x] for x in ('E','EE','EEE'))} Gradbindungen; R nur {sum(prof('R')['focus'][x] for x in ('E','EE','EEE'))}. "
            f"T folgt CH {pct(prof('T')['previous']['CH'], int(prof('T')['mention_count']))}, R {pct(prof('R')['previous']['CH'], int(prof('R')['mention_count']))}."
        ),
    }
    contrast_interpretation = {
        ("CH", "S"): "NEHMEN eröffnet eine Übergabe; WÄHLEN bestimmt eher den gewünschten Wert oder Anteil.",
        ("K", "OK"): "GEBEN ist die häufige Fortsetzung nach NEHMEN; SETZEN etabliert meist selbständig einen Zustand.",
        ("K", "P"): "GEBEN schließt die Übergabe; EINSETZEN öffnet häufig den nächsten Bearbeitungs- oder Halteschritt.",
        ("OK", "P"): "SETZEN ist ein selbständiger Zustandskopf; EINSETZEN ist ein Brückenkopf in einen weiteren Gang.",
        ("SH", "CHD"): "HALTEN nimmt Gradstufen; BEARBEITEN ist fast immer der letzte ungradierte Handlungskopf.",
        ("T", "R"): "EINSTELLEN nimmt Gradstufen; MARKIEREN setzt einen Bezug, ohne selbst den Grad zu tragen.",
    }
    contrast_rows: list[dict[str, object]] = []
    for family, left, right in CONTRASTS:
        contrast_rows.append({
            "family": family,
            "contrast_pair": f"{left}~{right}",
            "left_meaning_de": meanings[left],
            "right_meaning_de": meanings[right],
            "shared_exact_substitution_frame_count": pair_frame_counts[(left, right)],
            "shared_frame_event_count": pair_frame_events[(left, right)],
            "decisive_distributional_contrast": contrast_evidence[(left, right)],
            "workshop_interpretation_de": contrast_interpretation[(left, right)],
            "decision": "DISTINCT_MEANINGS_RETAINED",
        })

    write_tsv(OUT / "gdt428_9_action_semantic_profiles.tsv", profile_rows, list(profile_rows[0]))
    write_tsv(OUT / "gdt428_6_within_class_contrasts.tsv", contrast_rows, list(contrast_rows[0]))
    write_tsv(OUT / "gdt428_104_direct_substitution_frames.tsv", substitution_rows, list(substitution_rows[0]))

    deck = [
        "# Neun Handlungen: kurze Kontrastkarte", "",
        "Die Klasse sagt nur, welche Bauform möglich ist. Die Wurzel sagt weiterhin, welche Handlung gemeint ist.", "",
    ]
    for row in profile_rows:
        deck += [
            f"- **{row['action_root']} = {row['working_meaning_de']}** — {row['operational_definition_de']}. "
            f"Nicht automatisch {row['strongest_rival_de']}.",
        ]
    deck += ["", "## Entscheidende Minimalpaare", ""]
    for row in contrast_rows:
        deck.append(
            f"- **{row['contrast_pair']}** ({row['shared_exact_substitution_frame_count']} gleiche Rahmen): "
            f"{row['workshop_interpretation_de']}"
        )
    (OUT / "ACTION_MEANING_CONTRAST_DECK.md").write_text("\n".join(deck) + "\n", encoding="utf-8")

    result = {
        "status": "NINE_ACTION_MEANINGS_RETAINED_WITH_DIRECT_CONTRAST_RULES",
        "running_event_count": len(clauses),
        "action_root_count": len(profile_rows),
        "action_mention_count": sum(int(row["mention_count"]) for row in profile_rows),
        "focus_edge_count": len(focus_rows),
        "close_edge_count": len(close_rows),
        "contrast_pair_count": len(contrast_rows),
        "direct_substitution_frame_count": len(substitution_rows),
        "all_contrasts_have_shared_frames": all(int(row["shared_exact_substitution_frame_count"]) > 0 for row in contrast_rows),
        "meaning_revisions": 0,
        "new_roots": 0,
        "new_pages": 0,
    }
    (OUT / "gdt428_result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
