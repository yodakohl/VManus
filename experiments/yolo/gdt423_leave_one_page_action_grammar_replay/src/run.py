#!/usr/bin/env python3
"""Leave one page key out and replay action grammar from all remaining pages."""

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
BASE = ROOT / "experiments/yolo/gdt423_leave_one_page_action_grammar_replay"
OUT = BASE / "artifacts"
CLAUSES = ROOT / "experiments/yolo/gdt416_owner_local_imperative_sentence_compiler/artifacts/gdt416_4576_imperative_clauses.tsv"
LONG_CHAINS = ROOT / "experiments/yolo/gdt422_multi_action_chain_pair_reduction/artifacts/gdt422_110_long_action_chain_inventory.tsv"

ACTIONS = {"OK", "CH", "SH", "K", "S", "CHD", "T", "R", "P"}
GRADES = {"E", "EE", "EEE"}
ARGUMENTS = {"Y", "AIIN", "AIN", "OR"}


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
    long_chain_status = {row["component_recipe"]: row["reduction_status"] for row in read_tsv(LONG_CHAINS)}
    pages = sorted({row["physical_page"] for row in clauses})

    cell_pages: dict[tuple[str, str, str, str], set[str]] = defaultdict(set)
    head_pages: dict[str, set[str]] = defaultdict(set)
    margin_pages: dict[str, dict[tuple[str, str], set[str]]] = defaultdict(lambda: defaultdict(set))
    recipe_pages: dict[str, set[str]] = defaultdict(set)
    event_meta: dict[str, tuple[str, tuple[str, str, str, str] | None]] = {}

    for row in clauses:
        atoms = row["component_recipe"].split("+")
        actions = tuple(atom for atom in atoms if atom in ACTIONS)
        grades = [atom for atom in atoms if atom in GRADES]
        arguments = [atom for atom in atoms if atom in ARGUMENTS]
        dy_count = atoms.count("DY")
        page = row["physical_page"]
        recipe_pages[row["component_recipe"]].add(page)

        if not actions:
            category = "NO_ACTION_HEAD"
            cell = None
        elif len(actions) == 1:
            clean = len(grades) <= 1 and len(arguments) <= 1 and dy_count <= 1
            category = "CLEAN_SINGLE_HEAD" if clean else "NONCLEAN_SINGLE_HEAD"
            cell = None
            if clean:
                head = actions[0]
                cell = (head, grades[0] if grades else "NONE", arguments[0] if arguments else "NONE", "CLOSE" if dy_count else "OPEN")
        elif len(actions) == 2:
            clean = len(grades) <= 1 and len(arguments) <= 1 and dy_count <= 1
            category = "CLEAN_ORDERED_PAIR" if clean else "NONCLEAN_ORDERED_PAIR"
            cell = None
            if clean:
                head = "+".join(actions)
                cell = (head, grades[0] if grades else "NONE", arguments[0] if arguments else "NONE", "CLOSE" if dy_count else "OPEN")
        else:
            category = "LONG_ACTION_CHAIN"
            cell = None

        if cell:
            head, grade, argument, endpoint = cell
            cell_pages[cell].add(page)
            head_pages[head].add(page)
            if grade != "NONE":
                margin_pages[head][("GRADE", grade)].add(page)
            if argument != "NONE":
                margin_pages[head][("ARGUMENT", argument)].add(page)
            if endpoint == "CLOSE":
                margin_pages[head][("ENDPOINT", "CLOSE")].add(page)
        event_meta[row["global_running_event_id"]] = (category, cell)

    event_rows: list[dict[str, object]] = []
    page_cells: dict[tuple[str, tuple[str, str, str, str]], dict[str, object]] = {}
    for row in clauses:
        category, cell = event_meta[row["global_running_event_id"]]
        page = row["physical_page"]
        cause: list[str] = []
        if cell:
            head, grade, argument, endpoint = cell
            if cell_pages[cell] - {page}:
                replay = "GREEN_EXACT_SLOT_SKELETON_FROM_OTHER_PAGE"
            else:
                if not head_pages[head] - {page}:
                    cause.append("HEAD_OR_ORDERED_PAIR_PAGE_PRIVATE")
                if grade != "NONE" and not margin_pages[head][("GRADE", grade)] - {page}:
                    cause.append("GRADE_SLOT_PAGE_PRIVATE")
                if argument != "NONE" and not margin_pages[head][("ARGUMENT", argument)] - {page}:
                    cause.append("ARGUMENT_SLOT_PAGE_PRIVATE")
                if endpoint == "CLOSE" and not margin_pages[head][("ENDPOINT", "CLOSE")] - {page}:
                    cause.append("CLOSE_SLOT_PAGE_PRIVATE")
                replay = "RED_PAGE_PRIVATE_HEAD_OR_SLOT" if cause else "AMBER_MARGINS_OLD_COMBINATION_NEW"
            skeleton = "|".join(cell)
        elif category in {"NONCLEAN_SINGLE_HEAD", "NONCLEAN_ORDERED_PAIR"}:
            replay = (
                "GREEN_COMPLEX_EXACT_RECIPE_FROM_OTHER_PAGE"
                if recipe_pages[row["component_recipe"]] - {page}
                else "AMBER_COMPLEX_ROOT_READING_OUTSIDE_SIMPLE_ATLAS"
            )
            skeleton = "NONCLEAN"
        elif category == "LONG_ACTION_CHAIN":
            replay = "GREEN_LONG_CHAIN_REDUCED_BY_GDT422"
            skeleton = long_chain_status[row["component_recipe"]]
        else:
            replay = "OUTSIDE_ACTION_GRAMMAR__ROOT_READING_UNCHANGED"
            skeleton = "NO_ACTION"

        event_rows.append({
            "global_running_event_id": row["global_running_event_id"],
            "global_statement_id": row["global_statement_id"],
            "held_out_page": page,
            "register": row["register"],
            "owner_de": row["owner_de"],
            "surface": row["surface"],
            "component_recipe": row["component_recipe"],
            "grammar_category": category,
            "slot_skeleton": skeleton,
            "leave_page_replay_status": replay,
            "red_causes": "|".join(cause) if cause else "NONE",
            "imperative_clause_de": row["imperative_clause_de"],
        })

        if cell:
            key = (page, cell)
            entry = page_cells.setdefault(key, {
                "held_out_page": page,
                "slot_skeleton": "|".join(cell),
                "head_or_pair": cell[0],
                "grade_slot": cell[1],
                "argument_slot": cell[2],
                "endpoint_slot": cell[3],
                "leave_page_replay_status": replay,
                "red_causes": "|".join(cause) if cause else "NONE",
                "event_count": 0,
                "surfaces": set(),
                "component_recipes": set(),
            })
            entry["event_count"] = int(entry["event_count"]) + 1
            entry["surfaces"].add(row["surface"])
            entry["component_recipes"].add(row["component_recipe"])

    page_cell_rows: list[dict[str, object]] = []
    for entry in page_cells.values():
        entry["surfaces"] = "|".join(sorted(entry["surfaces"]))
        entry["component_recipes"] = "|".join(sorted(entry["component_recipes"]))
        page_cell_rows.append(entry)
    page_cell_rows.sort(key=lambda row: (str(row["held_out_page"]), str(row["slot_skeleton"])))

    page_rows: list[dict[str, object]] = []
    for page in pages:
        rows = [row for row in event_rows if row["held_out_page"] == page]
        clean = [row for row in rows if row["grammar_category"] in {"CLEAN_SINGLE_HEAD", "CLEAN_ORDERED_PAIR"}]
        page_rows.append({
            "held_out_page": page,
            "registers": "|".join(sorted({str(row["register"]) for row in rows})),
            "event_count": len(rows),
            "clean_slot_event_count": len(clean),
            "green_clean_event_count": sum(str(row["leave_page_replay_status"]).startswith("GREEN") for row in clean),
            "amber_clean_event_count": sum(str(row["leave_page_replay_status"]).startswith("AMBER") for row in clean),
            "red_clean_event_count": sum(str(row["leave_page_replay_status"]).startswith("RED") for row in clean),
            "green_or_amber_clean_share": f"{sum(not str(row['leave_page_replay_status']).startswith('RED') for row in clean) / len(clean):.6f}" if clean else "1.000000",
            "complex_event_count": sum(row["grammar_category"] in {"NONCLEAN_SINGLE_HEAD", "NONCLEAN_ORDERED_PAIR"} for row in rows),
            "long_chain_event_count": sum(row["grammar_category"] == "LONG_ACTION_CHAIN" for row in rows),
            "no_action_event_count": sum(row["grammar_category"] == "NO_ACTION_HEAD" for row in rows),
        })

    red_rows = [row for row in page_cell_rows if str(row["leave_page_replay_status"]).startswith("RED")]
    write_tsv(OUT / "gdt423_4576_event_leave_page_replay.tsv", event_rows, list(event_rows[0]))
    write_tsv(OUT / "gdt423_1129_page_slot_cell_replay.tsv", page_cell_rows, list(page_cell_rows[0]))
    write_tsv(OUT / "gdt423_24_page_key_summary.tsv", page_rows, list(page_rows[0]))
    write_tsv(OUT / "gdt423_57_red_page_slot_cells.tsv", red_rows, list(red_rows[0]))

    card = [
        "# Nächste-Seite-Karte für die Handlungsschubladen", "",
        "1. **GRÜN:** dieselbe Kopf-/Paar-Schublade ist auf einer anderen Seite vorhanden.",
        "2. **GELB:** Kopf/Paar und jeder einzelne Slot sind alt, aber ihre Kombination ist neu.",
        "3. **ROT:** Kopf/Paar oder mindestens ein Slot ist im übrigen Lehrdeck unbekannt.",
        "4. Eine rote Form darf nicht still als regulär akzeptiert werden.",
        "5. Komplexe Mehrslotkarten bleiben root-lesbar, liegen aber außerhalb des einfachen Vierfachrasters.",
        "6. Lange Ketten werden nur mit GDT422-Paketregeln gelesen.", "",
        "Auf den bisherigen Seiten: 2.553/2.662 saubere Ereignisse grün, 50 gelb, 59 rot.",
    ]
    (OUT / "NEXT_PAGE_ACTION_GRAMMAR_CARD.md").write_text("\n".join(card) + "\n", encoding="utf-8")

    clean_rows = [row for row in event_rows if row["grammar_category"] in {"CLEAN_SINGLE_HEAD", "CLEAN_ORDERED_PAIR"}]
    category_counts = Counter(row["grammar_category"] for row in event_rows)
    cause_counts = Counter(cause for row in red_rows for cause in str(row["red_causes"]).split("|") if cause != "NONE")
    result = {
        "status": "LEAVE_ONE_PAGE_ACTION_GRAMMAR_REPLAY_COMPLETE",
        "page_key_count": len(pages),
        "admitted_physical_page_or_panel_count": 26,
        "event_count": len(event_rows),
        "category_event_counts": dict(sorted(category_counts.items())),
        "clean_slot_event_count": len(clean_rows),
        "green_clean_event_count": sum(str(row["leave_page_replay_status"]).startswith("GREEN") for row in clean_rows),
        "amber_clean_event_count": sum(str(row["leave_page_replay_status"]).startswith("AMBER") for row in clean_rows),
        "red_clean_event_count": sum(str(row["leave_page_replay_status"]).startswith("RED") for row in clean_rows),
        "page_slot_cell_count": len(page_cell_rows),
        "red_page_slot_cell_count": len(red_rows),
        "red_cause_counts": dict(sorted(cause_counts.items())),
        "pages_with_zero_red_clean_events": sum(int(row["red_clean_event_count"]) == 0 for row in page_rows),
        "new_pages": 0,
        "dictionary_revisions": 0,
    }
    (OUT / "gdt423_result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
