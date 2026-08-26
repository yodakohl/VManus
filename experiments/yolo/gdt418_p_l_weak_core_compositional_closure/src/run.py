#!/usr/bin/env python3
"""Close the two weakest exact-recipe portability cores, P and L."""

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
BASE = ROOT / "experiments/yolo/gdt418_p_l_weak_core_compositional_closure"
OUT = BASE / "artifacts"
CLAUSES = ROOT / "experiments/yolo/gdt416_owner_local_imperative_sentence_compiler/artifacts/gdt416_4576_imperative_clauses.tsv"
CROSS_RECIPES = ROOT / "experiments/yolo/gdt417_cross_register_semantic_parallel_phrasebook/artifacts/gdt417_298_cross_register_recipes.tsv"

ACTION = {"OK", "CH", "SH", "K", "S", "CHD", "T", "R", "P"}
ARGUMENT = {"Y", "AIIN", "AIN", "OR"}
RELATION = {"AL", "AR", "L", "AIR"}
ORDER = {"OL", "OT"}
GRADE = {"E", "EE", "EEE", "IIN", "DA"}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def position(index: int, length: int) -> str:
    if length == 1:
        return "ONLY"
    if index == 0:
        return "FIRST"
    if index == length - 1:
        return "LAST"
    return "MIDDLE"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    clauses = read_tsv(CLAUSES)
    cross = {r["component_recipe"]: r for r in read_tsv(CROSS_RECIPES)}
    selected = {"P": "EINSETZEN", "L": "VERBINDUNG"}

    occurrence_rows: list[dict[str, object]] = []
    by_root_recipe: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for clause in clauses:
        atoms = clause["component_recipe"].split("+")
        for index, atom in enumerate(atoms):
            if atom not in selected:
                continue
            other_actions = [a for a in atoms if a in ACTION and a != atom]
            arguments = [a for a in atoms if a in ARGUMENT]
            relations = [a for a in atoms if a in RELATION and a != atom]
            row = {
                "root": atom,
                "selected_value_de": selected[atom],
                "global_running_event_id": clause["global_running_event_id"],
                "global_statement_id": clause["global_statement_id"],
                "physical_page": clause["physical_page"],
                "register": clause["register"],
                "owner_de": clause["owner_de"],
                "surface": clause["surface"],
                "component_recipe": clause["component_recipe"],
                "atom_position": position(index, len(atoms)),
                "previous_atom": atoms[index - 1] if index else "BOUNDARY",
                "next_atom": atoms[index + 1] if index + 1 < len(atoms) else "BOUNDARY",
                "other_action_roots": "|".join(other_actions) or "NONE",
                "argument_roots": "|".join(arguments) or "NONE",
                "other_relation_roots": "|".join(relations) or "NONE",
                "has_order": "YES" if set(atoms) & ORDER else "NO",
                "has_grade": "YES" if set(atoms) & GRADE else "NO",
                "has_close": "YES" if "DY" in atoms else "NO",
                "template": clause["template"],
                "imperative_clause_de": clause["imperative_clause_de"],
                "cross_register_tier": cross.get(clause["component_recipe"], {}).get("portability_tier", "REGISTER_LOCAL_EXACT_RECIPE"),
                "cross_register_count": cross.get(clause["component_recipe"], {}).get("register_count", "1"),
                "semantic_decision": "KEEP_SELECTED_CORE",
            }
            occurrence_rows.append(row)
            by_root_recipe[(atom, clause["component_recipe"])].append(row)

    recipe_rows: list[dict[str, object]] = []
    for (root, recipe), rows in sorted(by_root_recipe.items()):
        positions = Counter(str(r["atom_position"]) for r in rows)
        recipe_rows.append({
            "root": root,
            "selected_value_de": selected[root],
            "component_recipe": recipe,
            "mention_count": len(rows),
            "event_count": len({r["global_running_event_id"] for r in rows}),
            "register_count": len({r["register"] for r in rows}),
            "registers": "|".join(sorted({str(r["register"]) for r in rows})),
            "page_count": len({r["physical_page"] for r in rows}),
            "positions": "|".join(f"{k}:{v}" for k, v in sorted(positions.items())),
            "with_other_action_count": sum(r["other_action_roots"] != "NONE" for r in rows),
            "with_argument_count": sum(r["argument_roots"] != "NONE" for r in rows),
            "with_relation_count": sum(r["other_relation_roots"] != "NONE" for r in rows),
            "with_close_count": sum(r["has_close"] == "YES" for r in rows),
            "cross_register_tier": rows[0]["cross_register_tier"],
            "example_clause_de": rows[0]["imperative_clause_de"],
        })

    profile_rows: list[dict[str, object]] = []
    for root in ("P", "L"):
        rows = [r for r in occurrence_rows if r["root"] == root]
        pos = Counter(str(r["atom_position"]) for r in rows)
        profile_rows.append({
            "root": root,
            "selected_value_de": selected[root],
            "mention_count": len(rows),
            "event_count": len({r["global_running_event_id"] for r in rows}),
            "recipe_type_count": len({r["component_recipe"] for r in rows}),
            "register_count": len({r["register"] for r in rows}),
            "first_count": pos["FIRST"],
            "middle_count": pos["MIDDLE"],
            "last_count": pos["LAST"],
            "only_count": pos["ONLY"],
            "with_other_action_count": sum(r["other_action_roots"] != "NONE" for r in rows),
            "with_argument_count": sum(r["argument_roots"] != "NONE" for r in rows),
            "with_relation_count": sum(r["other_relation_roots"] != "NONE" for r in rows),
            "with_grade_count": sum(r["has_grade"] == "YES" for r in rows),
            "with_close_count": sum(r["has_close"] == "YES" for r in rows),
            "cross_register_recipe_type_count": len({r["component_recipe"] for r in rows if r["cross_register_count"] != "1"}),
            "fully_self_contained_cross_recipe_type_count": len({
                r["component_recipe"] for r in rows
                if cross.get(str(r["component_recipe"]), {}).get("context_mode") == "FULLY_SELF_CONTAINED"
            }),
            "decision": "KEEP",
        })

    candidates = [
        ("P", "EINSETZEN", 4, 4, 4, 4, 4, "selected", "medial/action-chain position, explicit Y arguments and all five registers fit"),
        ("P", "VERWENDEN", 4, 3, 4, 4, 3, "rival", "broadly possible but weaker for source/celestial insertion frames"),
        ("P", "EINBRINGEN", 3, 4, 3, 4, 2, "rival", "too material for source and celestial use"),
        ("P", "BEGINNEN", 4, 1, 2, 3, 4, "rival", "111 of 160 mentions are not first and 126 share a card with another action"),
        ("L", "VERBINDUNG", 4, 4, 4, 3, 4, "selected", "first/standalone/last relation frame works without direction or physical pipe"),
        ("L", "BEZUG", 4, 4, 4, 4, 2, "rival", "safe but too abstract to explain recurring connection/path expansions"),
        ("L", "MIT", 4, 2, 3, 4, 3, "rival", "too grammatical for 18 standalone and 53 final occurrences"),
        ("L", "ANSCHLUSS", 2, 4, 4, 4, 2, "rival", "too physical for source, herbal and celestial owners"),
    ]
    score_rows = []
    for root, meaning, reg, pos, coaction, complement, neutral, status, reason in candidates:
        score_rows.append({
            "root": root, "candidate_de": meaning, "register_fit_0_4": reg,
            "position_fit_0_4": pos, "coaction_fit_0_4": coaction,
            "complement_fit_0_4": complement, "owner_neutrality_0_4": neutral,
            "total_0_20": reg + pos + coaction + complement + neutral,
            "status": status.upper(), "reason_de": reason,
        })

    write_tsv(OUT / "gdt418_430_p_l_occurrence_audit.tsv", occurrence_rows, list(occurrence_rows[0]))
    write_tsv(OUT / "gdt418_231_p_l_recipe_inventory.tsv", recipe_rows, list(recipe_rows[0]))
    write_tsv(OUT / "gdt418_p_l_profiles.tsv", profile_rows, list(profile_rows[0]))
    write_tsv(OUT / "gdt418_p_l_candidate_scorecard.tsv", score_rows, list(score_rows[0]))

    predictions = """# P/L-Kompositionskarten für spätere Seiten

## P = EINSETZEN

- `CH+P+Y`: einen Posten nehmen und in den laufenden Gang einsetzen.
- `O+P+Y`: den Einsetzgang am aktuellen Posten ausführen.
- `P+CHD+DY`: einsetzen, bearbeiten und den Schritt schließen.
- Rot wäre eine neue Seite, auf der P regelmäßig allein als Gegenstand oder
  überwiegend als letzter Kartenbestandteil erscheint.

## L = VERBINDUNG

- `L+CHD+DY`: über den aktiven Bezug/Anschluss bearbeiten und schließen.
- `CH+E+O+L`: nehmen, auf Grad I ausführen und an die aktive Verbindung binden.
- nacktes `L`: dieselbe Verbindung/Relation weitertragen; kein eigenes Verb.
- L erzeugt niemals allein eine Flussrichtung. Rot wäre eine stabile
  Gegenstandsrolle oder eine zweite, unvermeidbare Zeit-/Mengenbedeutung.
"""
    (OUT / "P_L_NEXT_PAGE_COMPOSITION_CARDS.md").write_text(predictions, encoding="utf-8")

    result = {
        "status": "P_AND_L_RETAINED_WITH_EXPLICIT_COMPOSITION_RULES",
        "occurrence_row_count": len(occurrence_rows),
        "p_mention_count": sum(r["root"] == "P" for r in occurrence_rows),
        "l_mention_count": sum(r["root"] == "L" for r in occurrence_rows),
        "recipe_row_count": len(recipe_rows),
        "candidate_count": len(score_rows),
        "p_selected": "EINSETZEN",
        "l_selected": "VERBINDUNG",
        "dictionary_revisions": 0,
        "new_pages": 0,
    }
    (OUT / "gdt418_result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
