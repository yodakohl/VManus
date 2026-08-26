#!/usr/bin/env python3
"""Build a cross-register phrasebook from exact shared component recipes."""

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
BASE = ROOT / "experiments/yolo/gdt417_cross_register_semantic_parallel_phrasebook"
OUT = BASE / "artifacts"
CLAUSES = ROOT / "experiments/yolo/gdt416_owner_local_imperative_sentence_compiler/artifacts/gdt416_4576_imperative_clauses.tsv"
STATEMENTS = ROOT / "experiments/yolo/gdt416_owner_local_imperative_sentence_compiler/artifacts/gdt416_715_imperative_statements.tsv"
CORES = ROOT / "experiments/yolo/gdt412_chd_process_core_completion/artifacts/gdt412_final_19_core_dictionary.tsv"
REGISTERS = ("SOURCE_SECTION_T", "HERBAL", "BIOLOGICAL", "CELESTIAL", "PHARMA")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sample(rows: list[dict[str, str]], register: str, field: str) -> str:
    return next((r[field] for r in rows if r["register"] == register), "NONE")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    clauses = read_tsv(CLAUSES)
    statements = read_tsv(STATEMENTS)
    cores = read_tsv(CORES)
    roots = [r["root"] for r in cores]

    by_recipe: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in clauses:
        by_recipe[row["component_recipe"]].append(row)

    recipe_rows: list[dict[str, object]] = []
    event_rows: list[dict[str, object]] = []
    cross_recipes: set[str] = set()
    for recipe, rows in sorted(by_recipe.items()):
        registers = sorted({r["register"] for r in rows}, key=REGISTERS.index)
        if len(registers) < 2:
            continue
        cross_recipes.add(recipe)
        readings = {r["portable_back_projection_de"] for r in rows}
        if len(readings) != 1:
            raise RuntimeError(f"portable reading drift inside recipe {recipe}")
        tier = {2: "TWO_REGISTERS", 3: "THREE_REGISTERS", 4: "FOUR_REGISTERS", 5: "ALL_FIVE_REGISTERS"}[len(registers)]
        inherited_action_count = sum(r["inherited_action_root"] != "NONE" for r in rows)
        inherited_argument_count = sum(r["inherited_argument_root"] != "NONE" for r in rows)
        contextual_count = sum(
            r["inherited_action_root"] != "NONE" or r["inherited_argument_root"] != "NONE"
            for r in rows
        )
        context_mode = (
            "FULLY_SELF_CONTAINED" if contextual_count == 0
            else "FULLY_CONTEXT_BOUND" if contextual_count == len(rows)
            else "MIXED_SELF_CONTAINED_AND_CONTEXT_BOUND"
        )
        row = {
            "component_recipe": recipe,
            "portable_core_reading_de": next(iter(readings)),
            "register_count": len(registers),
            "registers": "|".join(registers),
            "portability_tier": tier,
            "event_count": len(rows),
            "page_count": len({r["physical_page"] for r in rows}),
            "surface_count": len({r["surface"] for r in rows}),
            "surfaces": "|".join(sorted({r["surface"] for r in rows})),
            "inherited_action_event_count": inherited_action_count,
            "inherited_argument_event_count": inherited_argument_count,
            "context_bound_event_count": contextual_count,
            "context_mode": context_mode,
        }
        for register in REGISTERS:
            row[f"{register.lower()}_example"] = sample(rows, register, "imperative_clause_de")
        recipe_rows.append(row)
        for event in rows:
            event_rows.append({
                "component_recipe": recipe,
                "portable_core_reading_de": next(iter(readings)),
                "portability_tier": tier,
                "global_running_event_id": event["global_running_event_id"],
                "global_statement_id": event["global_statement_id"],
                "physical_page": event["physical_page"],
                "register": event["register"],
                "owner_de": event["owner_de"],
                "surface": event["surface"],
                "imperative_clause_de": event["imperative_clause_de"],
            })

    exact_groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    template_groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in statements:
        exact_groups[row["portable_core_reading_de"]].append(row)
        template_groups[row["template_sequence"]].append(row)

    exact_rows: list[dict[str, object]] = []
    exact_pattern_count = 0
    for reading, rows in sorted(exact_groups.items()):
        registers = sorted({r["register"] for r in rows}, key=REGISTERS.index)
        if len(registers) < 2:
            continue
        exact_pattern_count += 1
        parallel_id = f"EXACT-{exact_pattern_count:03d}"
        for row in rows:
            exact_rows.append({
                "parallel_id": parallel_id,
                "portable_core_reading_de": reading,
                "register_count": len(registers),
                "registers": "|".join(registers),
                "global_statement_id": row["global_statement_id"],
                "physical_page": row["physical_page"],
                "register": row["register"],
                "owner_de": row["owner_de"],
                "surface_sequence": row["surface_sequence"],
                "imperative_reading_de": row["imperative_reading_de"],
            })

    template_rows: list[dict[str, object]] = []
    template_pattern_count = 0
    for pattern, rows in sorted(template_groups.items()):
        registers = sorted({r["register"] for r in rows}, key=REGISTERS.index)
        if len(registers) < 2:
            continue
        template_pattern_count += 1
        parallel_id = f"TEMPLATE-{template_pattern_count:03d}"
        for row in rows:
            template_rows.append({
                "parallel_id": parallel_id,
                "template_sequence": pattern,
                "register_count": len(registers),
                "registers": "|".join(registers),
                "global_statement_id": row["global_statement_id"],
                "physical_page": row["physical_page"],
                "register": row["register"],
                "owner_de": row["owner_de"],
                "portable_core_reading_de": row["portable_core_reading_de"],
                "imperative_reading_de": row["imperative_reading_de"],
            })

    root_rows: list[dict[str, object]] = []
    for root in roots:
        total_mentions = 0
        cross_mentions = 0
        cross_types: set[str] = set()
        all_five_types: set[str] = set()
        registers: set[str] = set()
        for recipe, rows in by_recipe.items():
            multiplicity = recipe.split("+").count(root)
            if not multiplicity:
                continue
            mentions = multiplicity * len(rows)
            total_mentions += mentions
            recipe_registers = {r["register"] for r in rows}
            if recipe in cross_recipes:
                cross_mentions += mentions
                cross_types.add(recipe)
                registers.update(recipe_registers)
                if len(recipe_registers) == 5:
                    all_five_types.add(recipe)
        root_rows.append({
            "root": root,
            "total_mention_count": total_mentions,
            "cross_register_mention_count": cross_mentions,
            "cross_register_share": f"{cross_mentions / total_mentions:.6f}",
            "cross_register_recipe_type_count": len(cross_types),
            "all_five_recipe_type_count": len(all_five_types),
            "supported_register_count": len(registers),
            "supported_registers": "|".join(sorted(registers, key=REGISTERS.index)),
            "status": "PORTABLE_CORE_HAS_CROSS_REGISTER_RECIPE_SUPPORT" if len(registers) == 5 else "LIMITED_CROSS_REGISTER_SUPPORT",
        })

    recipe_fields = [
        "component_recipe", "portable_core_reading_de", "register_count", "registers",
        "portability_tier", "event_count", "page_count", "surface_count", "surfaces",
        "inherited_action_event_count", "inherited_argument_event_count",
        "context_bound_event_count", "context_mode",
    ] + [f"{r.lower()}_example" for r in REGISTERS]
    write_tsv(OUT / "gdt417_298_cross_register_recipes.tsv", recipe_rows, recipe_fields)
    write_tsv(OUT / "gdt417_3317_cross_register_events.tsv", event_rows, list(event_rows[0]))
    write_tsv(OUT / "gdt417_45_exact_statement_parallels.tsv", exact_rows, list(exact_rows[0]))
    write_tsv(OUT / "gdt417_168_template_statement_parallels.tsv", template_rows, list(template_rows[0]))
    write_tsv(OUT / "gdt417_19_root_portability.tsv", root_rows, list(root_rows[0]))

    phrasebook = [
        "# Zwanzig Kartenrezepte, die in allen fünf Registern vorkommen", "",
        "Jede Zeile behält dieselbe Kernspur. Nur Besitzerwörter und deutsche",
        "Imperativform ändern sich.", "",
    ]
    all_five = [r for r in recipe_rows if r["portability_tier"] == "ALL_FIVE_REGISTERS"]
    for index, row in enumerate(sorted(all_five, key=lambda r: (r["context_mode"] != "FULLY_SELF_CONTAINED", -int(r["event_count"]), str(r["component_recipe"]))), 1):
        phrasebook += [
            f"## {index}. `{row['component_recipe']}` — {row['portable_core_reading_de']}", "",
            f"Belegt in {row['event_count']} Ereignissen auf {row['page_count']} Seiten. Kontextmodus: **{row['context_mode']}**.", "",
        ]
        for register in REGISTERS:
            phrasebook.append(f"- **{register}:** {row[f'{register.lower()}_example']}")
        phrasebook.append("")
    (OUT / "ALL_FIVE_REGISTER_PARALLEL_PHRASEBOOK.md").write_text("\n".join(phrasebook), encoding="utf-8")

    tiers = Counter(r["portability_tier"] for r in recipe_rows)
    context_modes = Counter(r["context_mode"] for r in recipe_rows)
    result = {
        "status": "CROSS_REGISTER_SEMANTIC_PARALLEL_PHRASEBOOK_COMPLETE",
        "all_recipe_type_count": len(by_recipe),
        "cross_register_recipe_type_count": len(recipe_rows),
        "cross_register_event_count": len(event_rows),
        "two_register_recipe_count": tiers["TWO_REGISTERS"],
        "three_register_recipe_count": tiers["THREE_REGISTERS"],
        "four_register_recipe_count": tiers["FOUR_REGISTERS"],
        "all_five_register_recipe_count": tiers["ALL_FIVE_REGISTERS"],
        "fully_self_contained_recipe_count": context_modes["FULLY_SELF_CONTAINED"],
        "fully_context_bound_recipe_count": context_modes["FULLY_CONTEXT_BOUND"],
        "mixed_context_recipe_count": context_modes["MIXED_SELF_CONTAINED_AND_CONTEXT_BOUND"],
        "all_five_fully_self_contained_recipe_count": sum(r["portability_tier"] == "ALL_FIVE_REGISTERS" and r["context_mode"] == "FULLY_SELF_CONTAINED" for r in recipe_rows),
        "exact_cross_register_statement_pattern_count": exact_pattern_count,
        "exact_cross_register_statement_count": len(exact_rows),
        "template_cross_register_statement_pattern_count": template_pattern_count,
        "template_cross_register_statement_count": len(template_rows),
        "root_count": len(root_rows),
        "roots_supported_in_all_five_registers": sum(r["supported_register_count"] == 5 for r in root_rows),
        "new_pages": 0,
        "new_roots": 0,
        "new_meanings": 0,
    }
    (OUT / "gdt417_result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
