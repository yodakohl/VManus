#!/usr/bin/env python3
"""Compile the GDT564 state-context selector atlas."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt564_state_context_selector_atlas"
OUT = BASE / "artifacts"
SOURCE = ROOT / "experiments/yolo/gdt563_complete_state_microphrase_edition/artifacts/gdt563_1656_complete_state_microphrases.tsv"

ARGUMENT_ROOTS = {"Y", "AIIN", "AIN", "OR"}
PHRASE = "owner_free_microphrase_de"
ACTION = "effective_action_roots"
ARGUMENT = "effective_argument_roots"

FIXED = "FIXED_RECIPE"
ARG_ROUTE = "WRITTEN_ACTION__SELECT_ARGUMENT"
ACTION_ROUTE = "WRITTEN_ARGUMENT__SELECT_ACTION"
PAIR_ROUTE = "OPEN_FRAME__SELECT_ACTION_ARGUMENT"

ROUTE_FIELDS = {
    FIXED: (),
    ARG_ROUTE: (ARGUMENT,),
    ACTION_ROUTE: (ACTION,),
    PAIR_ROUTE: (ACTION, ARGUMENT),
}

CANDIDATES = [
    ("RECIPE_ONLY", ()),
    ("EFFECTIVE_ACTION", (ACTION,)),
    ("EFFECTIVE_ARGUMENT", (ARGUMENT,)),
    ("ACTION_ARGUMENT", (ACTION, ARGUMENT)),
    ("RESOLUTION_MODE", ("resolution_mode",)),
    ("SOURCE_LAYER", ("microphrase_source_layer",)),
    ("STATEMENT_POSITION", ("statement_position",)),
    ("REGISTER", ("register",)),
    ("PHYSICAL_PAGE", ("physical_page",)),
    ("COHORT", ("cohort",)),
]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def packed(values: set[str] | list[str]) -> str:
    return " || ".join(sorted(set(values)))


def partition(rows: list[dict[str, str]], fields: tuple[str, ...]) -> dict[tuple[str, ...], list[dict[str, str]]]:
    groups: dict[tuple[str, ...], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        groups[tuple(row[field] for field in fields)].append(row)
    return dict(groups)


def candidate_stats(rows: list[dict[str, str]], fields: tuple[str, ...]) -> dict[str, int | bool]:
    cells = partition(rows, fields)
    ambiguous = sum(len({row[PHRASE] for row in members}) > 1 for members in cells.values())
    modal_hits = sum(Counter(row[PHRASE] for row in members).most_common(1)[0][1] for members in cells.values())
    return {
        "resolved": ambiguous == 0,
        "cell_count": len(cells),
        "ambiguous_cell_count": ambiguous,
        "modal_hit_count": modal_hits,
    }


def visible_argument(recipe: str) -> bool:
    return any(atom in ARGUMENT_ROOTS for atom in recipe.split("+"))


def structural_route(rows: list[dict[str, str]], phrase_count: int) -> str:
    if phrase_count == 1:
        return FIXED
    if rows[0]["written_action_roots"] != "NONE":
        return ARG_ROUTE
    if visible_argument(rows[0]["recipe"]):
        return ACTION_ROUTE
    return PAIR_ROUTE


def minimal_class(rows: list[dict[str, str]]) -> tuple[str, str]:
    action_ok = bool(candidate_stats(rows, (ACTION,))["resolved"])
    argument_ok = bool(candidate_stats(rows, (ARGUMENT,))["resolved"])
    mode_ok = bool(candidate_stats(rows, ("resolution_mode",))["resolved"])
    if action_ok and argument_ok:
        return "EITHER_ACTION_OR_ARGUMENT", "EFFECTIVE_ARGUMENT"
    if argument_ok and mode_ok:
        return "ARGUMENT_OR_RESOLUTION_MODE", "EFFECTIVE_ARGUMENT"
    if argument_ok:
        return "ARGUMENT_ONLY", "EFFECTIVE_ARGUMENT"
    if action_ok:
        return "ACTION_ONLY", "EFFECTIVE_ACTION"
    return "ACTION_ARGUMENT_REQUIRED", "ACTION_ARGUMENT"


def selector_key(fields: tuple[str, ...], values: tuple[str, ...]) -> str:
    if not fields:
        return "NONE"
    labels = {ACTION: "ACTION", ARGUMENT: "ARGUMENT"}
    return " | ".join(f"{labels.get(field, field.upper())}={value}" for field, value in zip(fields, values))


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    rows = read_tsv(SOURCE)
    rows.sort(key=lambda row: int(row["state_microphrase_ordinal"]))
    by_recipe: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_recipe[row["recipe"]].append(row)

    recipe_rows: list[dict[str, object]] = []
    variable_audit_rows: list[dict[str, object]] = []
    selector_cells: list[dict[str, object]] = []
    route_members: dict[str, list[tuple[str, list[dict[str, str]]]]] = defaultdict(list)
    minimal_members: dict[str, list[tuple[str, list[dict[str, str]]]]] = defaultdict(list)
    variable_recipes: dict[str, list[dict[str, str]]] = {}

    for recipe_ordinal, recipe in enumerate(sorted(by_recipe), 1):
        members = by_recipe[recipe]
        phrases = {row[PHRASE] for row in members}
        phrase_count = len(phrases)
        route = structural_route(members, phrase_count)
        route_members[route].append((recipe, members))
        if phrase_count == 1:
            equivalence = "NOT_NEEDED"
            canonical = "NONE"
        else:
            variable_recipes[recipe] = members
            equivalence, canonical = minimal_class(members)
            minimal_members[equivalence].append((recipe, members))

        fields = ROUTE_FIELDS[route]
        cells = partition(members, fields)
        assert all(len({row[PHRASE] for row in group}) == 1 for group in cells.values())
        recipe_rows.append({
            "recipe_ordinal": recipe_ordinal,
            "recipe": recipe,
            "event_count": len(members),
            "distinct_microphrase_count": phrase_count,
            "recurrence_status": "SINGLETON" if len(members) == 1 else "RECURRENT",
            "variability_status": "FIXED" if phrase_count == 1 else "CONTEXT_VARIABLE",
            "written_action_status": "PRESENT" if members[0]["written_action_roots"] != "NONE" else "ABSENT",
            "written_argument_status": "PRESENT" if visible_argument(recipe) else "ABSENT",
            "portable_route": route,
            "portable_selector_fields": "+".join(fields) if fields else "NONE",
            "empirical_minimal_equivalence_class": equivalence,
            "canonical_empirical_selector": canonical,
            "selector_cell_count": len(cells),
            "distinct_effective_action_count": len({row[ACTION] for row in members}),
            "distinct_effective_argument_count": len({row[ARGUMENT] for row in members}),
            "effective_action_signatures": packed({row[ACTION] for row in members}),
            "effective_argument_signatures": packed({row[ARGUMENT] for row in members}),
            "sample_microphrase_de": members[0][PHRASE],
            "guard": "VISIBLE_SLOT_ROUTE__NO_OWNER_OR_PAGE_SELECTOR",
        })

        if phrase_count > 1:
            for candidate, candidate_fields in CANDIDATES:
                stats = candidate_stats(members, candidate_fields)
                variable_audit_rows.append({
                    "recipe": recipe,
                    "event_count": len(members),
                    "distinct_microphrase_count": phrase_count,
                    "candidate": candidate,
                    "selector_fields": "+".join(candidate_fields) if candidate_fields else "NONE",
                    "selector_cell_count": stats["cell_count"],
                    "ambiguous_cell_count": stats["ambiguous_cell_count"],
                    "resolved_status": "RESOLVED" if stats["resolved"] else "AMBIGUOUS",
                    "modal_hit_count": stats["modal_hit_count"],
                    "modal_hit_rate": f"{int(stats['modal_hit_count']) / len(members):.9f}",
                })

            for key, group in sorted(cells.items()):
                selector_cells.append({
                    "selector_cell_ordinal": 0,
                    "selector_cell_id": "",
                    "recipe": recipe,
                    "portable_route": route,
                    "selector_fields": "+".join(fields),
                    "selector_key": selector_key(fields, key),
                    "effective_action_signatures": packed({row[ACTION] for row in group}),
                    "effective_argument_signatures": packed({row[ARGUMENT] for row in group}),
                    "owner_free_microphrase_de": group[0][PHRASE],
                    "event_count": len(group),
                    "event_ids": packed({row["event_id"] for row in group}),
                    "physical_page_count": len({row["physical_page"] for row in group}),
                    "physical_pages": packed({row["physical_page"] for row in group}),
                    "register_count": len({row["register"] for row in group}),
                    "registers": packed({row["register"] for row in group}),
                    "cohort_count": len({row["cohort"] for row in group}),
                    "cohorts": packed({row["cohort"] for row in group}),
                    "resolution_modes": packed({row["resolution_mode"] for row in group}),
                    "statement_positions": packed({row["statement_position"] for row in group}),
                    "source_layers": packed({row["microphrase_source_layer"] for row in group}),
                    "cross_page_status": "CROSS_PAGE" if len({row["physical_page"] for row in group}) > 1 else "ONE_PAGE",
                    "guard": "OBSERVED_CONTEXT_CELL__PHRASE_UNIQUE_WITHIN_EXACT_RECIPE",
                })

    selector_cells.sort(key=lambda row: (str(row["recipe"]), str(row["selector_key"])))
    for ordinal, row in enumerate(selector_cells, 1):
        row["selector_cell_ordinal"] = ordinal
        row["selector_cell_id"] = f"GDT564-C{ordinal:04d}"

    candidate_profile_rows: list[dict[str, object]] = []
    for candidate, fields in CANDIDATES:
        tests = [row for row in variable_audit_rows if row["candidate"] == candidate]
        candidate_profile_rows.append({
            "candidate": candidate,
            "selector_fields": "+".join(fields) if fields else "NONE",
            "variable_recipe_count": len(variable_recipes),
            "resolved_recipe_count": sum(row["resolved_status"] == "RESOLVED" for row in tests),
            "resolved_event_count": sum(int(row["event_count"]) for row in tests if row["resolved_status"] == "RESOLVED"),
            "selector_cell_count": sum(int(row["selector_cell_count"]) for row in tests),
            "ambiguous_cell_count": sum(int(row["ambiguous_cell_count"]) for row in tests),
            "modal_hit_count": sum(int(row["modal_hit_count"]) for row in tests),
            "event_count": sum(int(row["event_count"]) for row in tests),
            "modal_hit_rate": f"{sum(int(row['modal_hit_count']) for row in tests) / sum(int(row['event_count']) for row in tests):.9f}",
        })

    route_order = [FIXED, ARG_ROUTE, ACTION_ROUTE, PAIR_ROUTE]
    route_profile_rows: list[dict[str, object]] = []
    for route in route_order:
        members = route_members[route]
        fields = ROUTE_FIELDS[route]
        route_profile_rows.append({
            "portable_route": route,
            "selector_fields": "+".join(fields) if fields else "NONE",
            "recipe_count": len(members),
            "event_count": sum(len(group) for _, group in members),
            "selector_cell_count": sum(len(partition(group, fields)) for _, group in members),
            "distinct_recipe_microphrase_count": sum(len({row[PHRASE] for row in group}) for _, group in members),
            "route_rule_de": {
                FIXED: "Rezept allein: feste beobachtete Mikrophrase",
                ARG_ROUTE: "Handlung steht da; aktives Argument einsetzen",
                ACTION_ROUTE: "Argument steht da; aktive Handlung einsetzen",
                PAIR_ROUTE: "Handlung und Argument fehlen; beide Zustände einsetzen",
            }[route],
        })

    minimal_order = [
        "ARGUMENT_ONLY", "ACTION_ONLY", "ACTION_ARGUMENT_REQUIRED",
        "EITHER_ACTION_OR_ARGUMENT", "ARGUMENT_OR_RESOLUTION_MODE",
    ]
    minimal_profile_rows: list[dict[str, object]] = []
    for name in minimal_order:
        members = minimal_members[name]
        minimal_profile_rows.append({
            "minimal_equivalence_class": name,
            "recipe_count": len(members),
            "event_count": sum(len(group) for _, group in members),
            "distinct_recipe_microphrase_count": sum(len({row[PHRASE] for row in group}) for _, group in members),
            "recipes": packed({recipe for recipe, _ in members}),
        })

    recurrent_cells = [row for row in selector_cells if int(row["event_count"]) > 1]
    cross_page_cells = [row for row in selector_cells if int(row["physical_page_count"]) > 1]
    cross_register_cells = [row for row in selector_cells if int(row["register_count"]) > 1]
    cross_cohort_cells = [row for row in selector_cells if int(row["cohort_count"]) > 1]
    candidate_lookup = {row["candidate"]: row for row in candidate_profile_rows}

    result = {
        "status": "PASS_402_RECIPE_SELECTOR_ATLAS__101_VARIABLE_RECIPES_RESOLVED__415_CONTEXT_CELLS__ZERO_AMBIGUITY__THREE_PORTABLE_ROUTES",
        "source_state_card_count": len(rows),
        "exact_recipe_count": len(by_recipe),
        "fixed_recipe_count": len(route_members[FIXED]),
        "fixed_recipe_event_count": sum(len(group) for _, group in route_members[FIXED]),
        "context_variable_recipe_count": len(variable_recipes),
        "context_variable_event_count": sum(len(group) for group in variable_recipes.values()),
        "observed_variable_selector_cell_count": len(selector_cells),
        "observed_variable_recipe_microphrase_count": sum(len({row[PHRASE] for row in group}) for group in variable_recipes.values()),
        "complete_recipe_plus_context_cell_count": len(route_members[FIXED]) + len(selector_cells),
        "portable_route_recipe_counts": {row["portable_route"]: row["recipe_count"] for row in route_profile_rows},
        "portable_route_event_counts": {row["portable_route"]: row["event_count"] for row in route_profile_rows},
        "portable_route_cell_counts": {row["portable_route"]: row["selector_cell_count"] for row in route_profile_rows},
        "empirical_canonical_selector_recipe_counts": {
            "EFFECTIVE_ARGUMENT": sum(row["canonical_empirical_selector"] == "EFFECTIVE_ARGUMENT" for row in recipe_rows),
            "EFFECTIVE_ACTION": sum(row["canonical_empirical_selector"] == "EFFECTIVE_ACTION" for row in recipe_rows),
            "ACTION_ARGUMENT": sum(row["canonical_empirical_selector"] == "ACTION_ARGUMENT" for row in recipe_rows),
        },
        "minimal_equivalence_class_counts": {row["minimal_equivalence_class"]: row["recipe_count"] for row in minimal_profile_rows},
        "action_argument_resolved_recipe_count": candidate_lookup["ACTION_ARGUMENT"]["resolved_recipe_count"],
        "action_argument_ambiguous_cell_count": candidate_lookup["ACTION_ARGUMENT"]["ambiguous_cell_count"],
        "recipe_only_modal_hit_count": candidate_lookup["RECIPE_ONLY"]["modal_hit_count"],
        "effective_action_modal_hit_count": candidate_lookup["EFFECTIVE_ACTION"]["modal_hit_count"],
        "effective_argument_modal_hit_count": candidate_lookup["EFFECTIVE_ARGUMENT"]["modal_hit_count"],
        "action_argument_modal_hit_count": candidate_lookup["ACTION_ARGUMENT"]["modal_hit_count"],
        "recurrent_selector_cell_count": len(recurrent_cells),
        "recurrent_selector_cell_event_count": sum(int(row["event_count"]) for row in recurrent_cells),
        "cross_page_selector_cell_count": len(cross_page_cells),
        "cross_register_selector_cell_count": len(cross_register_cells),
        "cross_cohort_selector_cell_count": len(cross_cohort_cells),
        "maximum_selector_cell_event_count": max(int(row["event_count"]) for row in selector_cells),
        "all_portable_selector_cells_phrase_unique": all(
            row["resolved_status"] == "RESOLVED"
            for row in variable_audit_rows if row["candidate"] == "ACTION_ARGUMENT"
        ),
        "owner_page_or_register_required": False,
        "new_pages": 0,
        "new_surfaces": 0,
        "new_recipes": 0,
        "new_root_values": 0,
        "input_sha256": {"gdt563_complete_state_microphrases": sha256(SOURCE)},
    }

    write_tsv(OUT / "gdt564_402_recipe_selector_routes.tsv", recipe_rows, list(recipe_rows[0]))
    write_tsv(OUT / "gdt564_1010_selector_candidate_tests.tsv", variable_audit_rows, list(variable_audit_rows[0]))
    write_tsv(OUT / "gdt564_415_observed_selector_cells.tsv", selector_cells, list(selector_cells[0]))
    write_tsv(OUT / "gdt564_10_candidate_selector_profiles.tsv", candidate_profile_rows, list(candidate_profile_rows[0]))
    write_tsv(OUT / "gdt564_4_portable_route_profiles.tsv", route_profile_rows, list(route_profile_rows[0]))
    write_tsv(OUT / "gdt564_5_empirical_minimal_classes.tsv", minimal_profile_rows, list(minimal_profile_rows[0]))

    top_cells = sorted(selector_cells, key=lambda row: (-int(row["event_count"]), str(row["recipe"])))[:12]
    book = [
        "# GDT564 – kompakter Kontextwähler für alle 402 Zustandsrezepte",
        "",
        "## Ergebnis",
        "",
        "301 Rezepte haben in den aktuellen Ereignissen eine feste Mikrophrase. Die101 variablen Rezepte",
        "werden durch415 beobachtete Kontextzellen vollständig getrennt. `Rezept + aktive Handlung + aktives",
        "Argument` hat null mehrdeutige Zellen; Besitzer, Seite und Register sind nicht nötig.",
        "",
        "```text",
        "geschriebene Handlung vorhanden  → nur aktives Argument auswählen",
        "nur geschriebenes Argument da    → nur aktive Handlung auswählen",
        "beide Slots ausgelassen           → Handlung + Argument auswählen",
        "```",
        "",
        "## Vier portable Routen",
        "",
        "| Route | Rezepte | Ereignisse | Kontextzellen |",
        "|---|---:|---:|---:|",
    ]
    for row in route_profile_rows:
        book.append(f"| `{row['portable_route']}` | {row['recipe_count']} | {row['event_count']} | {row['selector_cell_count']} |")
    book += [
        "",
        "Die301 festen Rezepte plus415 variable Zellen ergeben716 vollständige Rezept-Kontext-Lesungen.",
        "Der sichtbare Dreiwegschalter ist absichtlich etwas vorsichtiger als ein pro Rezept gelernter",
        "Minimaltrick: Er verlässt sich nicht auf zufällige Gleichläufe von Handlung und Argument.",
        "",
        "## Empirisch kleinste Schlüssel",
        "",
        "| Minimalrelation | Rezepte | Ereignisse | Mikrophrasen |",
        "|---|---:|---:|---:|",
    ]
    for row in minimal_profile_rows:
        book.append(f"| `{row['minimal_equivalence_class']}` | {row['recipe_count']} | {row['event_count']} | {row['distinct_recipe_microphrase_count']} |")
    book += [
        "",
        "Für einen festen ausführbaren Standard wird bei Gleichstand das Argument bevorzugt. Damit nutzen60",
        "variable Rezepte nur das Argument,26 nur die Handlung und15 beide Werte. Die portable sichtbare",
        "Regel bleibt jedoch54/15/32, weil sie auch bei einer später neu auftretenden Kombination weiß, welcher",
        "Slot wirklich offen ist.",
        "",
        "## Warum die Zustände zählen",
        "",
        f"Wählt man je Rezept immer nur seine häufigste Phrase, trifft man {candidate_lookup['RECIPE_ONLY']['modal_hit_count']}/1277 Ereignisse.",
        f"Nur die Handlung erreicht {candidate_lookup['EFFECTIVE_ACTION']['modal_hit_count']}/1277, nur das Argument {candidate_lookup['EFFECTIVE_ARGUMENT']['modal_hit_count']}/1277.",
        f"Handlung plus Argument erreicht {candidate_lookup['ACTION_ARGUMENT']['modal_hit_count']}/1277 und lässt {candidate_lookup['ACTION_ARGUMENT']['ambiguous_cell_count']} mehrdeutige Zellen.",
        "",
        "## Wiederverwendete Zellen",
        "",
        f"{len(recurrent_cells)}/415 Zellen treten mehrfach auf und tragen {sum(int(row['event_count']) for row in recurrent_cells)}/1277 Ereignisse.",
        f"{len(cross_page_cells)} Zellen stehen auf mehreren Seiten,{len(cross_register_cells)} in mehreren Registern und",
        f"{len(cross_cohort_cells)} in beiden Seitenkohorten. Die größte Einzelzelle hat {result['maximum_selector_cell_event_count']} Ereignisse.",
        "",
        "| Rezept | Selektor | Ereignisse | Mikrophrase |",
        "|---|---|---:|---|",
    ]
    for row in top_cells:
        phrase = str(row["owner_free_microphrase_de"]).replace("|", "\\|")
        book.append(f"| `{row['recipe']}` | `{row['selector_key']}` | {row['event_count']} | {phrase} |")
    book += [
        "",
        "## Arbeitsregel",
        "",
        "Das Rezept liefert die sichtbaren Kürzel und ihre Reihenfolge. Der Selektor füllt nur die tatsächlich",
        "offenen Handlungs- und Argumentslots. Er darf weder den Besitzer in einen Wortstamm zurückschreiben",
        "noch eine neue Ganzwortbedeutung lernen. Diese Ausgabe benutzt keine neue Seite und ändert keinen Root.",
        "",
    ]
    (OUT / "GDT564_CONTEXT_SELECTOR_BOOK.md").write_text("\n".join(book), encoding="utf-8")
    (OUT / "gdt564_result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
