#!/usr/bin/env python3
"""Build V62 from exact visible-dy sister contrasts and head preservation."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import subprocess
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt689_v62_bound_dy_sister_endpoint_dispatch"
ART = BASE / "artifacts"
DECISIONS = BASE / "src/V62_DY_SISTER_DECISIONS.tsv"
GDT515_LEDGER = ROOT / "experiments/yolo/gdt515_second_random_four_page_full_admission/artifacts/gdt515_5866_unified_group_ledger.tsv"
GDT515_PAGE_SUMMARY = ROOT / "experiments/yolo/gdt515_second_random_four_page_full_admission/artifacts/gdt515_30_page_summary.tsv"
GDT516_PAIRS = ROOT / "experiments/yolo/gdt516_thirty_page_new_surface_family_consolidation/artifacts/gdt516_110_dy_y_pair_atlas.tsv"
V48_GLOSSARY = ROOT / "experiments/yolo/gdt671_fifteen_residual_family_completion/artifacts/V48_WORKING_TOKEN_GLOSSARY.tsv"
V48_LINES = ROOT / "experiments/yolo/gdt671_fifteen_residual_family_completion/artifacts/ALL_LINE_CONCRETE_COVERAGE_V48.tsv"
GRID = ROOT / "experiments/yolo/gdt624_productive_quality_shell_grid/artifacts/GRID_CELLS.tsv"
BOUND = ROOT / "experiments/yolo/gdt687_v60_dchey_y_dy_action_result_boundary_dispatch/artifacts/BOUND_DY_60_SURFACE_DISPATCH.tsv"
POSITIONS = ROOT / "experiments/yolo/gdt687_v60_dchey_y_dy_action_result_boundary_dispatch/artifacts/V60_95_POSITION_SCOPE_DISPATCH.tsv"
DY_PRIOR = ROOT / "experiments/yolo/gdt687_v60_dchey_y_dy_action_result_boundary_dispatch/artifacts/DY_705_CLOSURE_PRIOR.tsv"
V61_READER = ROOT / "experiments/yolo/gdt688_v61_exact_verb_ordinal_provenance_renderer/artifacts/V61_51_LINE_READER.tsv"
VERB_RULES = ROOT / "experiments/yolo/gdt688_v61_exact_verb_ordinal_provenance_renderer/src/V61_VERB_RULES.tsv"

GRID_D_BIT_PAIRS = [
    ("kchdy", "kchy"), ("tchdy", "tchy"), ("tchedy", "tchey"),
    ("okchedy", "okchey"), ("otchdy", "otchy"),
    ("qokchdy", "qokchy"), ("qokchedy", "qokchey"),
    ("qotchedy", "qotchey"),
]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def guarded_query_tsv(
    path: Path,
    *,
    selector: str,
    allowed_values: set[str],
    columns: tuple[str, ...],
) -> list[dict[str, str]]:
    """Materialize selected columns only after the repository page guard."""
    command = [
        str(ROOT / "vmanus-exp"), "query-tsv", str(path),
        "--selector", selector,
        "--columns", ",".join(columns),
        "--forbid-prefix", "f84",
    ]
    for value in sorted(allowed_values):
        command.extend(["--allow", value])
    completed = subprocess.run(
        command,
        cwd=ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    rows = list(csv.DictReader(io.StringIO(completed.stdout), delimiter="\t"))
    assert rows and tuple(rows[0]) == columns
    return rows


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def int_set(value: str) -> set[int]:
    return {int(item) for item in value.split("|") if item and item != "NONE"}


def compile_rules(rows: list[dict[str, str]]) -> list[tuple[str, re.Pattern[str]]]:
    rules = [(row["canonical_lemma"], re.compile(row["regex"], re.IGNORECASE)) for row in rows]
    assert len(rules) == len({lemma for lemma, _ in rules}) == 32
    return rules


def occurrences(text: str, rules: list[tuple[str, re.Pattern[str]]]) -> list[dict[str, object]]:
    found = [
        {"start": match.start(), "end": match.end(), "lemma": lemma, "matched_text": match.group(0)}
        for lemma, pattern in rules for match in pattern.finditer(text)
    ]
    found.sort(key=lambda row: (int(row["start"]), int(row["end"]), str(row["lemma"])))
    for left, right in zip(found, found[1:]):
        assert int(left["end"]) <= int(right["start"]), (text, left, right)
    return found


def verb_lemmas_present(text: str, rules: list[tuple[str, re.Pattern[str]]]) -> list[str]:
    """Classify legacy card prose without treating regex span overlap as syntax.

    A historical card such as ``kühle ... ab und schließe ab`` can make the
    deliberately broad separable-verb regex reach across the second ``ab``.
    For the sister-card ACTION/NONACTION diagnostic we need only the presence
    of canonical lemmas; exact non-overlapping spans remain mandatory for the
    newly rendered V62 reader below.
    """
    return [lemma for lemma, pattern in rules if pattern.search(text)]


def render_with_segments(glosses: list[str]) -> tuple[str, list[dict[str, object]]]:
    text = ""
    segments: list[dict[str, object]] = []
    for ordinal, gloss in enumerate(glosses, 1):
        if gloss in {";", "."}:
            stripped = text.rstrip(" ,;.")
            for segment in segments:
                if int(segment["end"]) > len(stripped):
                    segment["end"] = len(stripped)
            text = stripped
            start = len(text)
            text += gloss
            segments.append({"ordinal": ordinal, "start": start, "end": len(text), "gloss": gloss})
            continue
        separator = "" if not text else (" " if text.endswith((";", ".", ":")) else "; ")
        text += separator
        start = len(text)
        text += gloss
        segments.append({"ordinal": ordinal, "start": start, "end": len(text), "gloss": gloss})
    if text and not text.endswith("."):
        text += "."
    if text:
        text = text[:1].upper() + text[1:]
    return text, segments


def line_position(ordinal: int, length: int) -> str:
    if ordinal == 1:
        return "INITIAL"
    if ordinal == length:
        return "FINAL"
    return "MEDIAL"


def page_guard(rows: list[dict[str, str]], fields: tuple[str, ...]) -> None:
    for row in rows:
        for field in fields:
            value = row.get(field, "")
            if value:
                assert not value.lower().startswith("f84"), (field, value)


def build(output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    bound_rows = read_tsv(BOUND)
    decision_rows = read_tsv(DECISIONS)
    position_rows = [row for row in read_tsv(POSITIONS) if row["target_family"] == "BOUND_DY"]
    v61_rows = read_tsv(V61_READER)
    glossary_rows = read_tsv(V48_GLOSSARY)
    pair_atlas_rows = read_tsv(GDT516_PAIRS)
    grid_rows = read_tsv(GRID)
    dy_prior_rows = read_tsv(DY_PRIOR)
    gdt515_page_rows = read_tsv(GDT515_PAGE_SUMMARY)
    rules = compile_rules(read_tsv(VERB_RULES))

    reader_pages = {row["page"] for row in v61_rows}
    gdt515_pages = {row["physical_page"] for row in gdt515_page_rows}
    assert len(gdt515_page_rows) == len(gdt515_pages) == 30
    page_guard(gdt515_page_rows, ("physical_page",))
    v48_line_rows = guarded_query_tsv(
        V48_LINES,
        selector="page",
        allowed_values=reader_pages,
        columns=("page", "locus", "section", "language", "hand", "token_count", "zl3b_line"),
    )
    gdt515_rows = guarded_query_tsv(
        GDT515_LEDGER,
        selector="physical_page",
        allowed_values=gdt515_pages,
        columns=(
            "global_group_ordinal", "global_group_id", "physical_page", "locus",
            "source_statement_id", "surface", "component_recipe",
        ),
    )

    page_guard(position_rows, ("page",))
    page_guard(v61_rows, ("page",))
    page_guard(v48_line_rows, ("page",))
    page_guard(gdt515_rows, ("physical_page",))

    assert len(bound_rows) == len(decision_rows) == 60
    assert len({row["surface"] for row in bound_rows}) == 60
    assert {row["surface"] for row in bound_rows} == {row["surface"] for row in decision_rows}
    assert len(position_rows) == sum(int(row["positions"]) for row in bound_rows) == 74
    assert sum(int(row["action_positions"]) for row in bound_rows) == 15
    assert sum(int(row["result_positions"]) for row in bound_rows) == 59
    assert len({row["locus"] for row in position_rows}) == 33
    assert len({row["page"] for row in position_rows}) == 23
    assert len(v61_rows) == 51 and sum(int(row["token_count"]) for row in v61_rows) == 479

    bound = {row["surface"]: row for row in bound_rows}
    decisions = {row["surface"]: row for row in decision_rows}
    glossary = {row["surface"]: row for row in glossary_rows}
    v61_by_locus = {row["locus"]: row for row in v61_rows}

    v48_occurrences: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in v48_line_rows:
        tokens = row["zl3b_line"].split()
        assert len(tokens) == int(row["token_count"])
        register_key = f'{row["section"]}|{row["language"]}|{row["hand"]}'
        for ordinal, surface in enumerate(tokens, 1):
            v48_occurrences[surface].append({
                "page": row["page"], "locus": row["locus"], "ordinal": ordinal,
                "position": line_position(ordinal, len(tokens)), "register_key": register_key,
            })

    recipes: dict[str, set[str]] = defaultdict(set)
    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    by_locus: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in gdt515_rows:
        if row["surface"] in bound:
            recipes[row["surface"]].add(row["component_recipe"])
        by_statement[row["source_statement_id"]].append(row)
        by_locus[row["locus"]].append(row)

    statement_position_by_group: dict[str, str] = {}
    for rows in by_statement.values():
        rows.sort(key=lambda row: int(row["global_group_ordinal"]))
        for index, row in enumerate(rows):
            statement_position_by_group[row["global_group_id"]] = (
                "INITIAL" if index == 0 else ("FINAL" if index == len(rows) - 1 else "MEDIAL")
            )

    statement_index: dict[tuple[str, int, str], tuple[str, str]] = {}
    for locus, rows in by_locus.items():
        rows.sort(key=lambda row: int(row["global_group_ordinal"]))
        for ordinal, row in enumerate(rows, 1):
            statement_index[(locus, ordinal, row["surface"])] = (
                statement_position_by_group[row["global_group_id"]], row["source_statement_id"]
            )

    pair_atlas = {(row["dy_surface"], row["y_surface"]): row for row in pair_atlas_rows}
    grid = {row["surface"]: row for row in grid_rows}

    inventory_rows: list[dict[str, object]] = []
    formal_status_by_surface: dict[str, str] = {}
    for source in bound_rows:
        surface = source["surface"]
        decision = decisions[surface]
        assert surface.endswith("dy")
        derived_sister = surface[:-2] + "y"
        sister = decision["sister_surface"]
        if sister != "NONE":
            assert sister == derived_sister
        surface_recipes = sorted(recipes.get(surface, set()))
        if not surface_recipes:
            formal_status = "UNRESOLVED"
        elif all("DY" in recipe.split("+") for recipe in surface_recipes):
            formal_status = "FORMAL_DY"
        elif any("DY" in recipe.split("+") for recipe in surface_recipes):
            formal_status = "MIXED_FORMAL_DY"
        else:
            formal_status = "NO_FORMAL_DY"
        formal_status_by_surface[surface] = formal_status
        sister_occ = v48_occurrences.get(derived_sister, [])
        sister_source = (
            "V48_WORKING_CARD" if derived_sister in glossary else
            "GDT516_PARSER_CONTROL" if derived_sister in {"cheoy", "dchey"} else
            "VISIBLE_WITHOUT_WORKING_CARD" if sister_occ else "ABSENT"
        )
        atlas = pair_atlas.get((surface, derived_sister), {})
        inventory_rows.append({
            "surface": surface,
            "positions": int(source["positions"]),
            "lines": int(source["lines"]),
            "v60_action_positions": int(source["action_positions"]),
            "v60_result_positions": int(source["result_positions"]),
            "v60_dispatch_class": source["dispatch_class"],
            "v60_literal_gloss_de": source["v60_literal_gloss_de"],
            "derived_one_edit_sister": derived_sister,
            "sister_occurrences_v48": len(sister_occ),
            "sister_pages_v48": len({str(item["page"]) for item in sister_occ}),
            "sister_source": sister_source,
            "sister_working_meaning_de": glossary.get(derived_sister, {}).get("working_meaning_de", "NONE"),
            "pair_status": decision["pair_status"],
            "v62_class": decision["v62_class"],
            "evidence_basis": decision["evidence_basis"],
            "transfer_policy": decision["transfer_policy"],
            "v62_literal_gloss_de": (
                source["v60_literal_gloss_de"] if decision["v62_gloss_override_de"] == "KEEP_V60"
                else decision["v62_gloss_override_de"]
            ),
            "formal_dy_status": formal_status,
            "gdt515_recipes": "|".join(surface_recipes) if surface_recipes else "NONE",
            "gdt516_pair_recipe_relation": atlas.get("recipe_relation", "NOT_IN_GDT516_PAIR_ATLAS"),
            "gdt516_bound_recipe": atlas.get("dy_recipes", "NONE"),
            "gdt516_sister_recipe": atlas.get("y_recipes", "NONE"),
            "rationale_de": decision["rationale_de"],
        })

    formal_surface_counts = Counter(formal_status_by_surface.values())
    formal_position_counts = Counter()
    for row in bound_rows:
        formal_position_counts[formal_status_by_surface[row["surface"]]] += int(row["positions"])
    assert formal_surface_counts == Counter({
        "FORMAL_DY": 24, "MIXED_FORMAL_DY": 2,
        "NO_FORMAL_DY": 17, "UNRESOLVED": 17,
    }), formal_surface_counts
    assert formal_position_counts == Counter({
        "FORMAL_DY": 30, "MIXED_FORMAL_DY": 3,
        "NO_FORMAL_DY": 24, "UNRESOLVED": 17,
    }), formal_position_counts

    card_backed = [
        row for row in inventory_rows
        if row["sister_source"] in {"V48_WORKING_CARD", "GDT516_PARSER_CONTROL"}
    ]
    assert len(card_backed) == 39
    assert sum(row["sister_occurrences_v48"] for row in card_backed if row["sister_source"] == "V48_WORKING_CARD") == 639
    assert sum(row["pair_status"] == "REAL_NON_DY_SISTER" for row in inventory_rows) == 36
    assert sum(row["pair_status"] == "PARSER_EQUIVALENT_NULL" for row in inventory_rows) == 1
    assert sum(row["pair_status"] == "VISIBLE_SISTER_WITHOUT_CARD" for row in inventory_rows) == 10
    assert sum(row["pair_status"] == "NO_REAL_SISTER" for row in inventory_rows) == 11
    assert decisions["cheody"]["v62_class"] == "FIELD_END"
    assert pair_atlas[("cheody", "cheoy")]["recipe_relation"] == "SAME_RECIPE"
    assert pair_atlas[("cheody", "cheoy")]["dy_recipes"] == pair_atlas[("cheody", "cheoy")]["y_recipes"] == "CH+E+O+Y"
    assert decisions["dchedy"]["pair_status"] == "PARSER_INVALID_PAIR"
    assert pair_atlas[("dchedy", "dchey")]["dy_recipes"] == "D_ADDR+CHD+Y"
    assert pair_atlas[("dchedy", "dchey")]["y_recipes"] == "CH+E+Y"
    assert decisions["ypcheddy"]["pair_status"] == "NESTED_DY_SISTER_EXCLUDED"
    assert decisions["ypcheddy"]["sister_surface"].endswith("dy")

    semantic_rows = [row for row in inventory_rows if row["pair_status"] == "REAL_NON_DY_SISTER"]
    parser_null_rows = [row for row in inventory_rows if row["pair_status"] == "PARSER_EQUIVALENT_NULL"]
    assert len(semantic_rows) == 36 and len(parser_null_rows) == 1

    prediction_rows: list[dict[str, object]] = []
    for row in [*semantic_rows, *parser_null_rows]:
        if row["gdt516_pair_recipe_relation"] == "SAME_RECIPE":
            predicted = "FIELD_END"
            rule = "SAME_RECIPE_TO_FIELD_END"
        elif decisions[str(row["surface"])]["sister_endpoint_before_dy"] == "1":
            predicted = "FIELD_END"
            rule = "SISTER_ENDPOINT_TO_FIELD_END"
        else:
            predicted = "RESULT_PARTICIPLE"
            rule = "OPEN_SISTER_TO_RESULT_PARTICIPLE"
        selected = str(row["v62_class"])
        prediction_rows.append({
            "surface": row["surface"], "sister_surface": row["derived_one_edit_sister"],
            "pair_status": row["pair_status"], "same_recipe": int(row["gdt516_pair_recipe_relation"] == "SAME_RECIPE"),
            "sister_endpoint_before_dy": decisions[str(row["surface"])]["sister_endpoint_before_dy"],
            "mechanical_rule": rule, "predicted_class": predicted,
            "selected_class": selected, "match": int(predicted == selected),
            "override_basis": "INHERITED_TARGET_RESULT_PLUS_ACTION_SISTER__IN_SAMPLE" if predicted != selected else "NONE",
            "evaluation_scope": "COMPRESSION_AUDIT_NOT_HELD_PREDICTION",
        })
    assert len(prediction_rows) == 37
    assert sum(int(row["match"]) for row in prediction_rows) == 36
    assert [row["surface"] for row in prediction_rows if not int(row["match"])] == ["ychedy"]

    score_rows: list[dict[str, object]] = []
    confusion = Counter()
    score_pair_surfaces: set[str] = set()
    for source in bound_rows:
        surface = source["surface"]
        sister = surface[:-2] + "y"
        if decisions[surface]["pair_status"] != "REAL_NON_DY_SISTER" or sister not in glossary:
            continue
        sister_text = glossary[sister]["working_meaning_de"]
        sister_verbs = verb_lemmas_present(sister_text, rules)
        target_class = "ACTION" if int(source["action_positions"]) else "RESULT"
        sister_class = "ACTION" if sister_verbs else "NONACTION"
        confusion[(target_class, sister_class)] += 1
        score_pair_surfaces.add(surface)
        score_rows.append({
            "surface": surface,
            "sister_surface": sister,
            "v60_target_class": target_class,
            "sister_text_class": sister_class,
            "sister_verbs": "|".join(sister_verbs) if sister_verbs else "NONE",
            "sister_working_meaning_de": sister_text,
            "class_relation": "SAME" if (target_class == "ACTION") == (sister_class == "ACTION") else "CHANGED",
            "v62_selected_class": decisions[surface]["v62_class"],
            "v62_pair_status": decisions[surface]["pair_status"],
        })
    assert len(score_rows) == 36
    assert confusion == Counter({
        ("RESULT", "NONACTION"): 25, ("ACTION", "ACTION"): 6,
        ("RESULT", "ACTION"): 3, ("ACTION", "NONACTION"): 2,
    })

    bound_cells: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in position_rows:
        surface = row["surface"]
        if surface not in score_pair_surfaces:
            continue
        line = v61_by_locus[row["locus"]]
        register_key = f'{line["section"]}|{line["language"]}|{line["hand"]}'
        bound_cells[(surface, register_key, row["line_position"])].append(row)

    sister_cells: Counter[tuple[str, str, str]] = Counter()
    for surface in score_pair_surfaces:
        sister = surface[:-2] + "y"
        for occurrence in v48_occurrences[sister]:
            sister_cells[(surface, str(occurrence["register_key"]), str(occurrence["position"]))] += 1

    controlled_rows: list[dict[str, object]] = []
    controlled_confusion = Counter()
    for key in sorted(bound_cells):
        if not sister_cells[key]:
            continue
        surface, register_key, position = key
        source = bound[surface]
        sister = surface[:-2] + "y"
        sister_action = bool(verb_lemmas_present(glossary[sister]["working_meaning_de"], rules))
        target_action = bool(int(source["action_positions"]))
        count = len(bound_cells[key])
        controlled_confusion[("ACTION" if target_action else "RESULT", "ACTION" if sister_action else "NONACTION")] += count
        controlled_rows.append({
            "surface": surface, "sister_surface": sister, "register_key": register_key,
            "position_basis": "PHYSICAL_LINE_POSITION", "position": position,
            "bound_v61_positions": count,
            "bound_v60_class": "ACTION" if target_action else "RESULT",
            "sister_v48_positions": sister_cells[key],
            "sister_text_class": "ACTION" if sister_action else "NONACTION",
            "class_relation": "SAME" if target_action == sister_action else "CHANGED",
        })
    assert len(controlled_rows) == 21
    assert len({row["surface"] for row in controlled_rows}) == 17
    assert sum(int(row["bound_v61_positions"]) for row in controlled_rows) == 24
    assert sum(int(row["sister_v48_positions"]) for row in controlled_rows) == 215
    assert controlled_confusion == Counter({("RESULT", "NONACTION"): 24})

    position_output: list[dict[str, object]] = []
    for row in position_rows:
        key = (row["locus"], int(row["ordinal"]), row["surface"])
        statement = statement_index.get(key)
        line = v61_by_locus[row["locus"]]
        decision = decisions[row["surface"]]
        position_output.append({
            "page": row["page"], "locus": row["locus"], "ordinal": int(row["ordinal"]),
            "surface": row["surface"],
            "register_key": f'{line["section"]}|{line["language"]}|{line["hand"]}',
            "physical_line_position": row["line_position"],
            "true_statement_position": statement[0] if statement else "UNAVAILABLE",
            "statement_id": statement[1] if statement else "UNAVAILABLE",
            "statement_position_source": "GDT515_EXACT_EVENT_JOIN" if statement else "NOT_PUBLICLY_JOINABLE",
            "formal_dy_status": formal_status_by_surface[row["surface"]],
            "v60_dispatch_class": row["dispatch_class"],
            "v62_class": decision["v62_class"], "pair_status": decision["pair_status"],
        })
    statement_known = [row for row in position_output if row["true_statement_position"] != "UNAVAILABLE"]
    assert len(statement_known) == 7
    assert Counter(row["true_statement_position"] for row in statement_known) == Counter({"MEDIAL": 3, "FINAL": 3, "INITIAL": 1})
    assert sum(row["physical_line_position"] == row["true_statement_position"] for row in statement_known) == 3

    grid_audit: list[dict[str, object]] = []
    for surface, sister in GRID_D_BIT_PAIRS:
        assert surface in grid and sister in grid
        assert grid[surface]["d_bit"] == "1" and grid[sister]["d_bit"] == "0"
        assert decisions[surface]["v62_class"] == "RESULT_PARTICIPLE"
        grid_audit.append({
            "surface": surface, "sister_surface": sister,
            "surface_working_default_de": grid[surface]["working_default_de"],
            "sister_working_default_de": grid[sister]["working_default_de"],
            "surface_d_bit": 1, "sister_d_bit": 0,
            "v62_class": "RESULT_PARTICIPLE",
            "evidence": "COMPLETE_GDT624_D_BIT_STATE_BINDING__DOES_NOT_IDENTIFY_RESULT_SEMANTICS",
        })

    targets_by_locus: dict[str, dict[int, dict[str, str]]] = defaultdict(dict)
    for row in position_rows:
        targets_by_locus[row["locus"]][int(row["ordinal"])] = row

    v62_rows: list[dict[str, object]] = []
    provenance_rows: list[dict[str, object]] = []
    revision_rows: list[dict[str, object]] = []
    position_revision_rows: list[dict[str, object]] = []
    for line in v61_rows:
        tokens = line["zl3b_line"].split()
        old_glosses = line["literal_token_glosses_de"].split(" | ")
        assert len(tokens) == len(old_glosses) == int(line["token_count"])
        new_glosses = list(old_glosses)
        old_actions = int_set(line["action_ordinals"])
        new_actions = set(old_actions)
        changed_ordinals: list[int] = []

        for ordinal, target in sorted(targets_by_locus.get(line["locus"], {}).items()):
            surface = target["surface"]
            decision = decisions[surface]
            assert tokens[ordinal - 1] == surface
            if decision["pair_status"] in {"REAL_NON_DY_SISTER", "PARSER_EQUIVALENT_NULL"}:
                new_gloss = decision["v62_gloss_override_de"]
                assert new_gloss != "KEEP_V60"
                new_glosses[ordinal - 1] = new_gloss
                changed_ordinals.append(ordinal)
                if decision["v62_class"] == "RESULT_PARTICIPLE":
                    new_actions.discard(ordinal)
                elif decision["v62_class"] == "ACTION_TELICITY":
                    new_actions.add(ordinal)
                else:
                    assert decision["v62_class"] == "FIELD_END"
                    # FIELD_END carries no new spoken value. Its grammatical
                    # orientation therefore follows the copied sister card,
                    # rather than blindly preserving the older whole-card
                    # action/result guess.
                    if verb_lemmas_present(new_gloss, rules):
                        new_actions.add(ordinal)
                    else:
                        new_actions.discard(ordinal)
                position_revision_rows.append({
                    "page": line["page"], "locus": line["locus"], "ordinal": ordinal,
                    "surface": surface, "sister_surface": decision["sister_surface"],
                    "v61_literal_gloss_de": old_glosses[ordinal - 1],
                    "v62_literal_gloss_de": new_gloss,
                    "v62_class": decision["v62_class"],
                    "formal_dy_status": formal_status_by_surface[surface],
                    "action_before": int(ordinal in old_actions), "action_after": int(ordinal in new_actions),
                    "preservation_rule": (
                        "KEEP_SISTER_HEAD_DEGREE_AND_BASE_ACTION__ADD_ONLY_SELECTED_DY_EFFECT"
                        if decision["pair_status"] == "REAL_NON_DY_SISTER"
                        else "SAME_RECIPE_TARGET_WHOLE_CARD__NO_VISIBLE_D_SEMANTIC_LOAD"
                    ),
                })

        strict_text, segments = render_with_segments(new_glosses)
        action_lemmas: dict[int, set[str]] = {}
        for ordinal in sorted(new_actions):
            local = occurrences(new_glosses[ordinal - 1], rules)
            assert local, (line["locus"], ordinal, new_glosses[ordinal - 1])
            action_lemmas[ordinal] = {str(item["lemma"]) for item in local}

        line_verbs = occurrences(strict_text, rules)
        for occurrence_index, occurrence in enumerate(line_verbs, 1):
            containers = [
                segment for segment in segments
                if int(segment["start"]) <= int(occurrence["start"])
                and int(occurrence["end"]) <= int(segment["end"])
            ]
            assert len(containers) == 1, (line["locus"], occurrence, containers)
            ordinal = int(containers[0]["ordinal"])
            assert ordinal in new_actions, (line["locus"], occurrence, ordinal, new_actions)
            assert str(occurrence["lemma"]) in action_lemmas[ordinal]
            provenance_rows.append({
                "page": line["page"], "locus": line["locus"], "v61_reader_mode": line["v61_reader_mode"],
                "occurrence_index": occurrence_index,
                "char_start": occurrence["start"], "char_end": occurrence["end"],
                "matched_text": occurrence["matched_text"], "canonical_lemma": occurrence["lemma"],
                "source_ordinal": ordinal, "source_surface": tokens[ordinal - 1],
                "source_literal_gloss_de": new_glosses[ordinal - 1], "action_licensed": 1,
                "provenance_status": "EXACT_V62_RENDERER_SPAN_TO_ACTION_ORDINAL",
            })

        output: dict[str, object] = dict(line)
        output["v62_action_positions"] = len(new_actions)
        output["v62_action_ordinals"] = "|".join(str(value) for value in sorted(new_actions)) if new_actions else "NONE"
        output["v62_action_surfaces"] = "|".join(tokens[value - 1] for value in sorted(new_actions)) if new_actions else "NONE"
        output["v62_literal_token_glosses_de"] = " | ".join(new_glosses)
        output["v62_practical_translation_de"] = strict_text
        output["v62_dy_sister_revisions"] = len(changed_ordinals)
        output["v62_dy_sister_ordinals"] = "|".join(str(value) for value in changed_ordinals) if changed_ordinals else "NONE"
        output["v62_verb_occurrences"] = len(line_verbs)
        output["v62_provenance_status"] = "ALL_PRACTICAL_VERBS_EXACT_ACTION_ORDINAL"
        v62_rows.append(output)

        if changed_ordinals or new_actions != old_actions:
            revision_rows.append({
                "page": line["page"], "locus": line["locus"],
                "changed_ordinals": "|".join(str(value) for value in changed_ordinals) if changed_ordinals else "NONE",
                "changed_surfaces": "|".join(tokens[value - 1] for value in changed_ordinals) if changed_ordinals else "NONE",
                "v61_action_ordinals": line["action_ordinals"], "v62_action_ordinals": output["v62_action_ordinals"],
                "v61_practical_translation_de": line["practical_translation_de"],
                "v62_practical_translation_de": strict_text,
                "revision_rule": "SISTER_HEAD_STAGE_ACTION_PRESERVATION",
            })

    assert len(v62_rows) == 51
    assert len(position_revision_rows) == 50
    assert sum(row["preservation_rule"] == "KEEP_SISTER_HEAD_DEGREE_AND_BASE_ACTION__ADD_ONLY_SELECTED_DY_EFFECT" for row in position_revision_rows) == 47
    assert sum(row["preservation_rule"] == "SAME_RECIPE_TARGET_WHOLE_CARD__NO_VISIBLE_D_SEMANTIC_LOAD" for row in position_revision_rows) == 3
    assert sum(int(row["v62_action_positions"]) for row in v62_rows) == 83
    assert sum(int(row["v62_verb_occurrences"]) for row in v62_rows) == len(provenance_rows)
    assert any(row["surface"] == "olchdy" and row["action_before"] == 1 and row["action_after"] == 0 for row in position_revision_rows)
    assert any(row["surface"] == "dshedy" and row["action_before"] == 1 and row["action_after"] == 0 for row in position_revision_rows)
    assert any(row["surface"] == "ychedy" and row["action_before"] == 0 and row["action_after"] == 0 for row in position_revision_rows)

    class_summary: list[dict[str, object]] = []
    for class_name in ["RESULT_PARTICIPLE", "FIELD_END", "ACTION_TELICITY", "PAIR_INVALID", "UNPAIRED_WHOLE_RETAINED"]:
        members = [row for row in inventory_rows if row["v62_class"] == class_name]
        class_summary.append({
            "v62_class": class_name, "surfaces": len(members),
            "current_positions": sum(int(row["positions"]) for row in members),
            "v60_action_positions": sum(int(row["v60_action_positions"]) for row in members),
            "v60_result_positions": sum(int(row["v60_result_positions"]) for row in members),
            "v62_action_positions": sum(
                int(row["positions"]) if row["v62_class"] == "ACTION_TELICITY" else
                int(row["positions"]) if row["v62_class"] == "FIELD_END" and verb_lemmas_present(str(row["v62_literal_gloss_de"]), rules) else
                int(row["v60_action_positions"]) if row["v62_class"] in {"PAIR_INVALID", "UNPAIRED_WHOLE_RETAINED"} else 0
                for row in members
            ),
            "meaning": {
                "RESULT_PARTICIPLE": "Schwesterkern als erreichtes oder fertiges nominales Resultat",
                "FIELD_END": "Schwester bereits endpunktgebunden; keine zusätzliche dy-Bedeutung aussprechen",
                "ACTION_TELICITY": "dieselbe Grundhandlung mit explizitem Zielpunkt",
                "PAIR_INVALID": "sichtbarer Nachbar, aber kein zulässiger Parserkontrast",
                "UNPAIRED_WHOLE_RETAINED": "Ganzform behalten; keine Endungsbedeutung exportieren",
            }[class_name],
        })

    hypothesis_rows = [
        {"hypothesis": "V60_WHOLE_CARD_DISPATCH", "result": "45 result surfaces / 15 action surfaces", "kept": "complete default coverage", "rejected": "dy may silently change a sister head or duplicate an endpoint"},
        {"hypothesis": "SURFACE_ONLY_RESULT_MODEL", "result": "30 result / 6 field / 3 telic over 39 proposed pairs", "kept": "resultative tendency and three-way vocabulary", "rejected": "follows inherited target glosses when those already drift from the sister"},
        {"hypothesis": "FORMAL_DY_ONLY", "result": "26 formal-DY / 17 non-DY / 17 unresolved surfaces", "kept": "parser guard and statement-end null", "rejected": "cannot by itself supply a practical meaning to all visible forms"},
        {"hypothesis": "V62_HEAD_PRESERVING_MIXED_CODE", "result": "25 result / 12 field / 0 telic; 1 parser-invalid; 22 whole-only", "kept": "selected working basis", "rejected": "productive action-telicity: all three candidates reduce to result or sister-copy"},
    ]

    reader_lines = [
        "# GDT689 V62 — kompletter 51-Zeilen-Arbeitsreader", "",
        "Die praktische Spalte ist quellgeordnet. Bei 50 Positionen bewahrt V62 den Schwesterkopf, Grad und Grundvorgang; nur Resultat, Telizität oder Feldschluss darf hinzukommen.", "",
    ]
    for row in v62_rows:
        marker = "REVIDIERT" if int(row["v62_dy_sister_revisions"]) else "GEHALTEN"
        reader_lines.extend([
            f'## {row["locus"]} — {marker}', "", f'`{row["zl3b_line"]}`', "",
            str(row["v62_practical_translation_de"]), "",
        ])
    reader_path = output_dir / "GDT689_V62_DY_SISTER_READER.md"
    reader_path.write_text("\n".join(reader_lines).rstrip() + "\n", encoding="utf-8")

    write_tsv(output_dir / "SURFACE_DY_60_FORM_INVENTORY.tsv", inventory_rows, list(inventory_rows[0]))
    write_tsv(output_dir / "SURFACE_DY_74_POSITION_INVENTORY.tsv", position_output, list(position_output[0]))
    write_tsv(output_dir / "SISTER_36_HEAD_PRESERVING_COMPARISON.tsv", semantic_rows, list(semantic_rows[0]))
    write_tsv(output_dir / "PARSER_EQUIVALENT_NULL_CONTROL.tsv", parser_null_rows, list(parser_null_rows[0]))
    write_tsv(output_dir / "V62_37_RULE_PREDICTION_AUDIT.tsv", prediction_rows, list(prediction_rows[0]))
    write_tsv(output_dir / "V48_36_USABLE_SISTER_CLASS_AUDIT.tsv", score_rows, list(score_rows[0]))
    write_tsv(output_dir / "CORE_REGISTER_PHYSICAL_POSITION_CELLS.tsv", controlled_rows, list(controlled_rows[0]))
    write_tsv(output_dir / "GRID_8_D_BIT_STATE_CONTROLS.tsv", grid_audit, list(grid_audit[0]))
    write_tsv(output_dir / "V62_CLASS_SUMMARY.tsv", class_summary, list(class_summary[0]))
    write_tsv(output_dir / "V62_50_POSITION_REVISIONS.tsv", position_revision_rows, list(position_revision_rows[0]))
    write_tsv(output_dir / "V62_LINE_REVISIONS.tsv", revision_rows, list(revision_rows[0]))
    v62_fields = list(v61_rows[0]) + [
        "v62_action_positions", "v62_action_ordinals", "v62_action_surfaces",
        "v62_literal_token_glosses_de", "v62_practical_translation_de",
        "v62_dy_sister_revisions", "v62_dy_sister_ordinals",
        "v62_verb_occurrences", "v62_provenance_status",
    ]
    write_tsv(output_dir / "V62_51_LINE_READER.tsv", v62_rows, v62_fields)
    write_tsv(output_dir / "V62_VERB_OCCURRENCE_PROVENANCE.tsv", provenance_rows, list(provenance_rows[0]))
    write_tsv(output_dir / "HYPOTHESIS_COMPARISON.tsv", hypothesis_rows, list(hypothesis_rows[0]))

    prior = dy_prior_rows[0]
    assert prior["marker"] == "DY" and int(prior["occurrence_count"]) == 705
    assert int(prior["statement_final_event_count"]) == 702

    generated = [
        "SURFACE_DY_60_FORM_INVENTORY.tsv", "SURFACE_DY_74_POSITION_INVENTORY.tsv",
        "SISTER_36_HEAD_PRESERVING_COMPARISON.tsv", "PARSER_EQUIVALENT_NULL_CONTROL.tsv",
        "V62_37_RULE_PREDICTION_AUDIT.tsv", "V48_36_USABLE_SISTER_CLASS_AUDIT.tsv",
        "CORE_REGISTER_PHYSICAL_POSITION_CELLS.tsv", "GRID_8_D_BIT_STATE_CONTROLS.tsv",
        "V62_CLASS_SUMMARY.tsv", "V62_50_POSITION_REVISIONS.tsv", "V62_LINE_REVISIONS.tsv",
        "V62_51_LINE_READER.tsv", "V62_VERB_OCCURRENCE_PROVENANCE.tsv",
        "HYPOTHESIS_COMPARISON.tsv", "GDT689_V62_DY_SISTER_READER.md",
    ]
    result = {
        "status": "PASS_V62_36_HEAD_SISTERS_PLUS_1_RECIPE_NULL__25_RESULT_12_FIELD_0_TELIC__47_HEAD_PLUS_3_NULL_REVISIONS",
        "population": {
            "surfaces": 60, "positions": 74, "lines": 33, "pages": 23,
            "one_edit_card_backed_pairs": 39, "head_preserving_sister_pairs": 36,
            "same_recipe_parser_null_pairs": 1,
            "parser_invalid_pairs": 1, "nested_dy_pairs_excluded": 1,
            "visible_sisters_without_card": 10, "absent_sisters": 11,
        },
        "v62_dispatch": {
            "result_participle_surfaces": 25, "field_end_surfaces": 12,
            "action_telicity_surfaces": 0, "pair_invalid_surfaces": 1,
            "whole_only_surfaces": 22, "revised_positions": len(position_revision_rows),
            "head_preserving_revised_positions": 47, "parser_null_revised_positions": 3,
            "revised_lines": len(revision_rows),
            "action_positions": sum(int(row["v62_action_positions"]) for row in v62_rows),
            "practical_verb_occurrences": len(provenance_rows),
            "exact_verb_provenance": len(provenance_rows),
        },
        "formal_dy": {
            "definite_formal_dy_surfaces": formal_surface_counts["FORMAL_DY"],
            "mixed_formal_dy_surfaces": formal_surface_counts["MIXED_FORMAL_DY"],
            "non_formal_visible_dy_surfaces": formal_surface_counts["NO_FORMAL_DY"],
            "unresolved_surfaces": formal_surface_counts["UNRESOLVED"],
            "definite_formal_dy_positions": formal_position_counts["FORMAL_DY"],
            "mixed_formal_dy_positions": formal_position_counts["MIXED_FORMAL_DY"],
            "non_formal_visible_dy_positions": formal_position_counts["NO_FORMAL_DY"],
            "unresolved_positions": formal_position_counts["UNRESOLVED"],
            "formal_statement_final_prior": 702, "formal_statement_total_prior": 705,
        },
        "class_diagnostic": {
            "v48_scored_usable_pairs": 36, "same_class_pairs": 31, "result_majority_correct": 28,
            "mechanical_rule_matches": 36, "mechanical_rule_total": 37,
            "mechanical_rule_exception": "ychedy__IN_SAMPLE_WHOLE_CARD_OVERRIDE",
            "controlled_cells": len(controlled_rows),
            "controlled_bound_positions": sum(int(row["bound_v61_positions"]) for row in controlled_rows),
            "controlled_sister_positions": sum(int(row["sister_v48_positions"]) for row in controlled_rows),
            "true_statement_position_joins": len(statement_known),
            "physical_position_matches_true_statement": sum(
                row["physical_line_position"] == row["true_statement_position"] for row in statement_known
            ),
        },
        "semantic_debt": {"strict": 106, "mechanical_union": 152, "four_layer_union": 330},
        "sealed_pages_absent": True,
        "claim_ceiling": "Exploratory replaceable head-preserving working code; not historical plaintext or a universal visible-dy morpheme.",
        "files": {name: sha256(output_dir / name) for name in generated},
    }
    write_json(output_dir / "RESULT.json", result)
    return result


def main() -> int:
    result = build(ART)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
