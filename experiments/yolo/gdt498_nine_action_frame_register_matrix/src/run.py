#!/usr/bin/env python3
"""Build the complete nine-action by eleven-frame by five-register matrix."""

from __future__ import annotations

import csv
import importlib.util
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from types import ModuleType


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt498_nine_action_frame_register_matrix"
ART = BASE / "artifacts"
G416 = ROOT / "experiments/yolo/gdt416_owner_local_imperative_sentence_compiler"
G415 = ROOT / "experiments/yolo/gdt415_owner_local_semantic_expansion_atlas/artifacts"
G493 = ROOT / "experiments/yolo/gdt493_owner_dependent_tr_realization_deck/artifacts"
G497 = ROOT / "experiments/yolo/gdt497_complete_context_safe_tr_default_deck/artifacts"

CLAUSES_IN = G416 / "artifacts/gdt416_4576_imperative_clauses.tsv"
COMPILER_IN = G416 / "src/run.py"
VALUES_IN = G415 / "gdt415_95_register_expansion_atlas.tsv"
FRAMES_IN = G493 / "gdt493_11_frame_coverage.tsv"
FRAME_VALUES_IN = G493 / "gdt493_55_observed_register_value_cells.tsv"
TR_DEFAULTS_IN = G497 / "gdt497_110_current_default_cells.tsv"

MATRIX_OUT = ART / "gdt498_495_action_frame_register_cells.tsv"
OBSERVED_OUT = ART / "gdt498_observed_cells.tsv"
COMPOSED_OUT = ART / "gdt498_composed_cells.tsv"
ACTION_OUT = ART / "gdt498_9_action_coverage.tsv"
FRAME_OUT = ART / "gdt498_11_frame_coverage.tsv"
REGISTER_OUT = ART / "gdt498_5_register_coverage.tsv"
ACTION_FRAME_OUT = ART / "gdt498_99_action_frame_coverage.tsv"
FRAME_REGISTER_OUT = ART / "gdt498_55_frame_register_head_coverage.tsv"
READABLE_OUT = ART / "GDT498_NINE_ACTION_FRAME_REGISTER_MATRIX.md"
RESULT_OUT = ART / "gdt498_result.json"

ACTION_ORDER = ("OK", "CH", "SH", "K", "S", "CHD", "T", "R", "P")
REGISTER_ORDER = ("SOURCE_SECTION_T", "HERBAL", "BIOLOGICAL", "CELESTIAL", "PHARMA")
STATUS = "ALL_FOUR_HUNDRED_NINETY_FIVE_CELLS_READABLE__ZERO_UNAVAILABLE__OBSERVED_AND_COMPOSED_VISIBLE"
GUARD = "WORKING_MEANING_MATRIX__NO_SURFACE_OR_OCCURRENCE_PREDICTION"


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


def load_compiler() -> ModuleType:
    spec = importlib.util.spec_from_file_location("gdt416_compiler", COMPILER_IN)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load GDT416 compiler")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def select_observed_phrase(rows: list[dict[str, str]]) -> tuple[str, int]:
    counts = Counter(row["imperative_clause_de"] for row in rows)
    phrase, count = sorted(counts.items(), key=lambda item: (-item[1], len(item[0].split()), len(item[0]), item[0]))[0]
    return phrase, count


def context_generalize(phrase: str, frame: str) -> tuple[str, int, str]:
    pattern = r"\b(?:den|die|das) [^.;]+? \[wie zuvor\]"
    matches = list(re.finditer(pattern, phrase))
    expected = 2 if frame == "CH+@ACTION" else 1
    if len(matches) != expected:
        raise ValueError(f"state phrase has {len(matches)} inherited nouns, expected {expected}: {phrase}")
    index = 0

    def replace(_match: re.Match[str]) -> str:
        nonlocal index
        index += 1
        return "das zuvor Genannte" if index == 1 else "es"

    output = re.sub(pattern, replace, phrase)
    fluency = "CONTEXT_NOUN_GENERALIZED"
    if frame == "@ACTION+OL":
        body = output.removeprefix("Weiter ")
        if body == output:
            raise ValueError(f"OL renderer lost Weiter: {output}")
        output = "Fahre fort: " + body[0].upper() + body[1:]
        fluency = "CONTEXT_NOUN_GENERALIZED__FORTSETZEN_COLON"
    return output, expected, fluency


def unique_join(values: list[str]) -> str:
    return "|".join(sorted(set(values))) if values else "NONE"


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    compiler = load_compiler()
    _clause_fields, clauses = read_tsv(CLAUSES_IN)
    _value_fields, values = read_tsv(VALUES_IN)
    _frame_fields, frames = read_tsv(FRAMES_IN)
    _frame_value_fields, frame_values = read_tsv(FRAME_VALUES_IN)
    _tr_fields, tr_defaults = read_tsv(TR_DEFAULTS_IN)
    if (len(clauses), len(values), len(frames), len(frame_values), len(tr_defaults)) != (4576, 95, 11, 55, 110):
        raise ValueError("input count drift")

    value_by_root_register = {(row["root"], row["register"]): row for row in values}
    for row in frame_values:
        key = (row["root"], row["register"])
        if key in value_by_root_register:
            old = value_by_root_register[key]
            if old["portable_default_de"] != row["portable_default_de"] or old["owner_local_expansion_de"] != row["owner_local_expansion_de"]:
                raise ValueError(f"register-value disagreement: {key}")
        else:
            value_by_root_register[key] = row
    clauses_by_recipe_register: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in clauses:
        clauses_by_recipe_register[(row["component_recipe"], row["register"])].append(row)
    tr_by_key = {(row["frozen_frame"], row["action_root"], row["register"]): row for row in tr_defaults}

    draft: list[dict[str, object]] = []
    for frame in frames:
        frozen_frame = frame["frozen_frame"]
        state_requirement = frame["state_requirement"]
        for action_root in ACTION_ORDER:
            action_recipe = frozen_frame.replace("@ACTION", action_root)
            atoms = action_recipe.split("+")
            for register in REGISTER_ORDER:
                old_cells = [value_by_root_register.get((atom, register)) for atom in atoms]
                missing_atoms = [atom for atom, cell in zip(atoms, old_cells) if cell is None]
                observed = clauses_by_recipe_register[(action_recipe, register)]
                selected_observed_phrase = "NONE"
                selected_observed_carriers = 0
                if observed:
                    selected_observed_phrase, selected_observed_carriers = select_observed_phrase(observed)

                if missing_atoms:
                    evidence_status = "UNAVAILABLE_MISSING_OWNER_VALUE"
                    default_policy = "UNAVAILABLE"
                    current_phrase = "NICHT VERFÜGBAR: " + "|".join(missing_atoms)
                    editorial_change = "NONE"
                    generalized_nouns = 0
                elif action_root in {"T", "R"}:
                    inherited = tr_by_key[(frozen_frame, action_root, register)]
                    current_phrase = str(inherited["current_default_phrase_de"])
                    evidence_status = str(inherited["evidence_status_retained"])
                    default_policy = "GDT497_CURRENT_DEFAULT_INHERITED"
                    editorial_change = str(inherited["editorial_change_type"])
                    generalized_nouns = int(inherited["generalized_inherited_noun_count"])
                    if bool(observed) != (evidence_status == "OBSERVED_CLAUSE"):
                        raise ValueError(f"T/R observation-status drift: {frozen_frame} {action_root} {register}")
                elif observed:
                    current_phrase = selected_observed_phrase
                    evidence_status = "OBSERVED_CLAUSE"
                    default_policy = "SELECTED_OBSERVED_CLAUSE"
                    editorial_change = "UNCHANGED_OBSERVED"
                    generalized_nouns = 0
                else:
                    explicit_actions = [atom for atom in atoms if atom in compiler.ACTION_ROOTS]
                    explicit_arguments = [atom for atom in atoms if atom in compiler.ARGUMENT_ROOTS]
                    rendered = compiler.render_clause(
                        register,
                        atoms,
                        explicit_actions,
                        "",
                        "Y" if state_requirement == "ACTIVE_ARGUMENT_REQUIRED" else "",
                    )
                    if state_requirement == "ACTIVE_ARGUMENT_REQUIRED":
                        current_phrase, generalized_nouns, editorial_change = context_generalize(rendered, frozen_frame)
                    else:
                        current_phrase = rendered
                        generalized_nouns = 0
                        editorial_change = "UNCHANGED_SELF_CONTAINED_RENDERER"
                    evidence_status = "COMPOSED_WORKING"
                    default_policy = "GDT416_RENDERER_PLUS_OLD_REGISTER_VALUES"

                draft.append(
                    {
                        "matrix_cell_id": f"G498-M{len(draft) + 1:03d}",
                        "frame_id": frame["frame_id"],
                        "frozen_frame": frozen_frame,
                        "action_root": action_root,
                        "action_recipe": action_recipe,
                        "register": register,
                        "portable_component_trace_de": " · ".join(str(cell["portable_default_de"]) for cell in old_cells if cell),
                        "owner_local_component_trace_de": " · ".join(str(cell["owner_local_expansion_de"]) for cell in old_cells if cell),
                        "state_requirement": state_requirement,
                        "availability_status": "READABLE" if not missing_atoms else "UNAVAILABLE",
                        "missing_owner_value_atoms": "|".join(missing_atoms) or "NONE",
                        "evidence_status": evidence_status,
                        "current_default_policy": default_policy,
                        "current_default_phrase_de": current_phrase,
                        "editorial_change_type": editorial_change,
                        "generalized_inherited_noun_count": generalized_nouns,
                        "observed_event_count": len(observed),
                        "observed_clause_form_count": len({row["imperative_clause_de"] for row in observed}),
                        "selected_observed_phrase_carrier_count": selected_observed_carriers,
                        "selected_observed_phrase_de": selected_observed_phrase,
                        "observed_pages": unique_join([row["physical_page"] for row in observed]),
                        "observed_event_ids": "|".join(row["global_running_event_id"] for row in observed) or "NONE",
                        "all_observed_clause_forms_de": " || ".join(sorted({row["imperative_clause_de"] for row in observed})) or "NONE",
                        "observed_inherited_argument_roots": unique_join([
                            row["inherited_argument_root"] for row in observed if row["inherited_argument_root"] != "NONE"
                        ]),
                        "all_component_value_cells_old": "YES" if not missing_atoms else "NO",
                        "same_frame_register_observed_other_action_count": 0,
                        "same_frame_register_observed_other_actions": "NONE",
                        "same_action_frame_observed_other_register_count": 0,
                        "same_action_frame_observed_other_registers": "NONE",
                        "composition_support_class": "PENDING",
                        "working_root_meaning_changed": "NO",
                        "surface_prediction_made": "NO",
                        "occurrence_prediction_made": "NO",
                        "guard": GUARD,
                    }
                )

    cells_by_frame_register: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    cells_by_frame_action: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in draft:
        cells_by_frame_register[(str(row["frozen_frame"]), str(row["register"]))].append(row)
        cells_by_frame_action[(str(row["frozen_frame"]), str(row["action_root"]))].append(row)
    for row in draft:
        local_observed = [
            cell for cell in cells_by_frame_register[(str(row["frozen_frame"]), str(row["register"]))]
            if cell["action_root"] != row["action_root"] and cell["evidence_status"] == "OBSERVED_CLAUSE"
        ]
        cross_observed = [
            cell for cell in cells_by_frame_action[(str(row["frozen_frame"]), str(row["action_root"]))]
            if cell["register"] != row["register"] and cell["evidence_status"] == "OBSERVED_CLAUSE"
        ]
        row["same_frame_register_observed_other_action_count"] = len(local_observed)
        row["same_frame_register_observed_other_actions"] = "|".join(str(cell["action_root"]) for cell in local_observed) or "NONE"
        row["same_action_frame_observed_other_register_count"] = len(cross_observed)
        row["same_action_frame_observed_other_registers"] = "|".join(str(cell["register"]) for cell in cross_observed) or "NONE"
        if row["evidence_status"] == "OBSERVED_CLAUSE":
            support_class = "OBSERVED_EXACT_CELL"
        elif row["availability_status"] == "UNAVAILABLE":
            support_class = "UNAVAILABLE"
        elif len(local_observed) >= 2:
            support_class = "COMPOSED_MULTIHEAD_SAME_REGISTER"
        elif len(local_observed) == 1:
            support_class = "COMPOSED_SINGLE_HEAD_SAME_REGISTER"
        elif cross_observed:
            support_class = "COMPOSED_CROSS_REGISTER_SAME_ACTION"
        else:
            support_class = "COMPOSED_OLD_VALUES_ONLY"
        row["composition_support_class"] = support_class

    matrix_rows = draft
    observed_rows = [row for row in matrix_rows if row["evidence_status"] == "OBSERVED_CLAUSE"]
    composed_rows = [row for row in matrix_rows if row["evidence_status"] == "COMPOSED_WORKING"]
    unavailable_rows = [row for row in matrix_rows if row["availability_status"] == "UNAVAILABLE"]
    if unavailable_rows:
        raise ValueError(f"unexpected unavailable cells: {len(unavailable_rows)}")

    def summarize(axis: str, values_order: tuple[str, ...] | None = None) -> list[dict[str, object]]:
        values_axis = list(values_order) if values_order else sorted({str(row[axis]) for row in matrix_rows})
        output: list[dict[str, object]] = []
        for value in values_axis:
            group = [row for row in matrix_rows if row[axis] == value]
            classes = Counter(str(row["composition_support_class"]) for row in group)
            output.append(
                {
                    axis: value,
                    "matrix_cell_count": len(group),
                    "observed_cell_count": sum(row["evidence_status"] == "OBSERVED_CLAUSE" for row in group),
                    "composed_cell_count": sum(row["evidence_status"] == "COMPOSED_WORKING" for row in group),
                    "unavailable_cell_count": sum(row["availability_status"] == "UNAVAILABLE" for row in group),
                    "observed_event_count": sum(int(row["observed_event_count"]) for row in group),
                    "multihead_composed_count": classes["COMPOSED_MULTIHEAD_SAME_REGISTER"],
                    "single_head_composed_count": classes["COMPOSED_SINGLE_HEAD_SAME_REGISTER"],
                    "cross_register_composed_count": classes["COMPOSED_CROSS_REGISTER_SAME_ACTION"],
                    "old_values_only_composed_count": classes["COMPOSED_OLD_VALUES_ONLY"],
                    "context_generalized_count": sum(int(row["generalized_inherited_noun_count"]) > 0 for row in group),
                    "all_value_cells_old": "YES" if all(row["all_component_value_cells_old"] == "YES" for row in group) else "NO",
                    "all_defaults_readable": "YES" if all(row["availability_status"] == "READABLE" for row in group) else "NO",
                }
            )
        return output

    action_rows = summarize("action_root", ACTION_ORDER)
    frame_rows = summarize("frozen_frame")
    register_rows = summarize("register", REGISTER_ORDER)

    action_frame_rows: list[dict[str, object]] = []
    for frame in frames:
        for action in ACTION_ORDER:
            group = cells_by_frame_action[(frame["frozen_frame"], action)]
            action_frame_rows.append(
                {
                    "action_frame_id": f"G498-AF{len(action_frame_rows) + 1:03d}",
                    "frame_id": frame["frame_id"],
                    "frozen_frame": frame["frozen_frame"],
                    "action_root": action,
                    "action_recipe": frame["frozen_frame"].replace("@ACTION", action),
                    "register_cell_count": len(group),
                    "observed_register_cell_count": sum(row["evidence_status"] == "OBSERVED_CLAUSE" for row in group),
                    "observed_registers": "|".join(str(row["register"]) for row in group if row["evidence_status"] == "OBSERVED_CLAUSE") or "NONE",
                    "composed_register_cell_count": sum(row["evidence_status"] == "COMPOSED_WORKING" for row in group),
                    "observed_event_count": sum(int(row["observed_event_count"]) for row in group),
                    "all_five_registers_readable": "YES" if len(group) == 5 and all(row["availability_status"] == "READABLE" for row in group) else "NO",
                    "all_owner_value_cells_old": "YES" if all(row["all_component_value_cells_old"] == "YES" for row in group) else "NO",
                }
            )

    frame_register_rows: list[dict[str, object]] = []
    for frame in frames:
        for register in REGISTER_ORDER:
            group = cells_by_frame_register[(frame["frozen_frame"], register)]
            observed_heads = [str(row["action_root"]) for row in group if row["evidence_status"] == "OBSERVED_CLAUSE"]
            frame_register_rows.append(
                {
                    "frame_register_id": f"G498-FR{len(frame_register_rows) + 1:02d}",
                    "frame_id": frame["frame_id"],
                    "frozen_frame": frame["frozen_frame"],
                    "register": register,
                    "action_cell_count": len(group),
                    "observed_action_head_count": len(observed_heads),
                    "observed_action_heads": "|".join(observed_heads) or "NONE",
                    "composed_action_cell_count": sum(row["evidence_status"] == "COMPOSED_WORKING" for row in group),
                    "observed_event_count": sum(int(row["observed_event_count"]) for row in group),
                    "all_nine_actions_readable": "YES" if len(group) == 9 and all(row["availability_status"] == "READABLE" for row in group) else "NO",
                    "all_owner_value_cells_old": "YES" if all(row["all_component_value_cells_old"] == "YES" for row in group) else "NO",
                }
            )

    write_tsv(MATRIX_OUT, matrix_rows)
    write_tsv(OBSERVED_OUT, observed_rows)
    write_tsv(COMPOSED_OUT, composed_rows)
    write_tsv(ACTION_OUT, action_rows)
    write_tsv(FRAME_OUT, frame_rows)
    write_tsv(REGISTER_OUT, register_rows)
    write_tsv(ACTION_FRAME_OUT, action_frame_rows)
    write_tsv(FRAME_REGISTER_OUT, frame_register_rows)

    support_counts = Counter(str(row["composition_support_class"]) for row in matrix_rows)
    lines = [
        "# GDT498 — Neun Handlungen × elf Rahmen × fünf Register",
        "",
        f"Status: `{STATUS}`",
        "",
        "Das Raster enthält jede Kombination der neun kurzen Handlungsköpfe mit",
        "den elf T/R-Rahmen und fünf owner-lokalen Registern. Jede Zelle zeigt",
        "Beobachtung oder sichtbar komponierten Arbeitsdefault; keine bleibt leer.",
        "",
        f"- Gesamtzellen: **{len(matrix_rows)}**; beobachtet: **{len(observed_rows)}**; komponiert: **{len(composed_rows)}**; nicht verfügbar: **{len(unavailable_rows)}**.",
        f"- Beobachtete Events in den exakten Zellen: **{sum(int(row['observed_event_count']) for row in observed_rows)}**.",
        f"- Kompositionen mit 2+ lokalen alten Köpfen: **{support_counts['COMPOSED_MULTIHEAD_SAME_REGISTER']}**; mit einem: **{support_counts['COMPOSED_SINGLE_HEAD_SAME_REGISTER']}**; nur registerübergreifend: **{support_counts['COMPOSED_CROSS_REGISTER_SAME_ACTION']}**; nur alte Einzelwerte: **{support_counts['COMPOSED_OLD_VALUES_ONLY']}**.",
        "",
        "## Handlung×Rahmen-Abdeckung",
        "",
        "| Rahmen | Aktion | Rezept | beobachtete Register | komponierte Register | Events |",
        "|---|---|---|---:|---:|---:|",
    ]
    for row in action_frame_rows:
        lines.append(
            f'| `{row["frozen_frame"]}` | {row["action_root"]} | `{row["action_recipe"]}` | '
            f'{row["observed_register_cell_count"]} | {row["composed_register_cell_count"]} | {row["observed_event_count"]} |'
        )
    lines.extend(["", "## Alle 495 aktuellen Arbeitsdefaults", "", "| ID | Rahmen | Aktion | Register | Default | Evidenz | Stütze |", "|---|---|---|---|---|---|---|"])
    for row in matrix_rows:
        lines.append(
            f'| {row["matrix_cell_id"]} | `{row["frozen_frame"]}` | `{row["action_recipe"]}` | '
            f'{row["register"]} | {row["current_default_phrase_de"]} | `{row["evidence_status"]}` | '
            f'`{row["composition_support_class"]}` |'
        )
    lines.extend(["", f'`{GUARD}`', ""])
    READABLE_OUT.write_text("\n".join(lines), encoding="utf-8")

    tr_matrix = [row for row in matrix_rows if row["action_root"] in {"T", "R"}]
    tr_exact_matches = sum(
        row["current_default_phrase_de"] == tr_by_key[(str(row["frozen_frame"]), str(row["action_root"]), str(row["register"]))]["current_default_phrase_de"]
        for row in tr_matrix
    )
    result = {
        "status": STATUS,
        "matrix_cells": len(matrix_rows),
        "action_count": len(action_rows),
        "frame_count": len(frame_rows),
        "register_count": len(register_rows),
        "action_frame_cells": len(action_frame_rows),
        "frame_register_cells": len(frame_register_rows),
        "observed_cells": len(observed_rows),
        "composed_cells": len(composed_rows),
        "unavailable_cells": len(unavailable_rows),
        "observed_events": sum(int(row["observed_event_count"]) for row in observed_rows),
        "multihead_same_register_compositions": support_counts["COMPOSED_MULTIHEAD_SAME_REGISTER"],
        "single_head_same_register_compositions": support_counts["COMPOSED_SINGLE_HEAD_SAME_REGISTER"],
        "cross_register_same_action_compositions": support_counts["COMPOSED_CROSS_REGISTER_SAME_ACTION"],
        "old_values_only_compositions": support_counts["COMPOSED_OLD_VALUES_ONLY"],
        "context_generalized_cells": sum(int(row["generalized_inherited_noun_count"]) > 0 for row in matrix_rows),
        "inherited_noun_occurrences_generalized": sum(int(row["generalized_inherited_noun_count"]) for row in matrix_rows),
        "tr_cells": len(tr_matrix),
        "tr_current_default_exact_matches": tr_exact_matches,
        "all_value_cells_old": sum(row["all_component_value_cells_old"] == "YES" for row in matrix_rows),
        "working_root_meaning_changes": sum(row["working_root_meaning_changed"] == "YES" for row in matrix_rows),
        "surface_predictions": sum(row["surface_prediction_made"] == "YES" for row in matrix_rows),
        "occurrence_predictions": sum(row["occurrence_prediction_made"] == "YES" for row in matrix_rows),
        "guard": GUARD,
    }
    RESULT_OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
