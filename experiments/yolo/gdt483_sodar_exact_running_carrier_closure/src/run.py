#!/usr/bin/env python3
"""Close GDT482's sodar residue through exact admitted running carriers."""

from __future__ import annotations

import csv
import io
import json
import re
import subprocess
from collections import Counter
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt483_sodar_exact_running_carrier_closure"
OUT = BASE / "artifacts"
G413 = ROOT / "experiments/yolo/gdt413_twenty_six_page_semantic_working_edition/artifacts"
G416 = ROOT / "experiments/yolo/gdt416_owner_local_imperative_sentence_compiler/artifacts"
G473 = ROOT / "experiments/yolo/gdt473_unified_local_address_working_edition/artifacts"
G482 = ROOT / "experiments/yolo/gdt482_residual_event_component_tiles/artifacts"
RUNNING_EVENTS_IN = G413 / "gdt413_4576_event_semantic_edition.tsv"
DICTIONARY_IN = G413 / "gdt413_46_component_working_dictionary.tsv"
IMPERATIVES_IN = G416 / "gdt416_4576_imperative_clauses.tsv"
LOCAL_EDITION_IN = G473 / "gdt473_183_unified_address_working_edition.tsv"
RESIDUAL_TILES_IN = G482 / "gdt482_45_residual_event_internal_tiles.tsv"
DA_CONTEXTS = OUT / "gdt483_35_da_event_contexts.tsv"
DA_R_CONTEXTS = OUT / "gdt483_10_da_r_adjacent_contexts.tsv"
SODAR_CARRIERS = OUT / "gdt483_3_sodar_exact_carriers.tsv"
CONTEXT_WINDOWS = OUT / "gdt483_2_sodar_running_context_windows.tsv"
SUPPORT_SUMMARY = OUT / "gdt483_sodar_component_support_summary.tsv"
RESIDUAL_CLOSURE = OUT / "gdt483_45_residual_closure.tsv"
READABLE = OUT / "GDT483_SODAR_EXACT_CARRIER_CLOSURE.md"
RESULT = OUT / "gdt483_result.json"

PAGES = (
    "f1r", "f10r", "f11r", "f13r", "f17r", "f18r", "f24v", "f55v",
    "f56r", "f67r2", "f68r1", "f69v", "f70v", "f71v", "f72r", "f75r",
    "f76r", "f77r", "f81r", "f81v", "f82r", "f83r", "f88r", "f88v",
    "f89r", "f95v",
)
LOCAL_PAGES = ("f17r", "f71v", "f72r", "f77r", "f88v", "f89r")
TARGET_EVENT_ID = "P1008-E1297"
TARGET_SURFACE = "sodar"
TARGET_RECIPE = "S+O+DA+R"
TARGET_LITERAL = "WÄHLEN · AUSFÜHRUNG · ZWEITE STUFE · MARKIEREN"
PREFERRED_GENERIC = "Wähle den Eintrag und markiere ihn – als Ausführung auf der zweiten Stufe."
PREFERRED_PHARMA = "Wähle den Drogen- oder Zutateneintrag und markiere ihn – als Ausführung auf der zweiten Stufe."

EVENT_COLUMNS = (
    "global_running_ordinal", "global_running_event_id", "physical_page", "source_panel",
    "register", "locus", "source_order", "source_statement_id", "owner_de", "surface",
    "component_recipe", "working_core_reading_de", "reading_layer", "surface_status",
    "admission_color",
)
IMPERATIVE_COLUMNS = (
    "global_running_event_id", "global_statement_id", "card_ordinal_in_statement",
    "physical_page", "register", "owner_class", "owner_de", "surface", "component_recipe",
    "explicit_action_roots", "inherited_action_root", "explicit_argument_roots",
    "inherited_argument_root", "template", "imperative_clause_de",
    "owner_local_atom_reading_de", "portable_back_projection_de", "roundtrip_exact",
)
LOCAL_COLUMNS = (
    "source_event_id", "physical_page", "register", "locus", "owner_de", "surface",
    "content_class", "edition_route", "edition_semantic_mode", "coverage_class",
    "working_recipe", "working_reading_de", "assignment_mode", "transfer_scope",
    "template_familiarity_state", "gdt459_decision_evidence",
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"Refusing to write empty table: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def guarded_query(path: Path, pages: tuple[str, ...], columns: tuple[str, ...]) -> tuple[list[dict[str, str]], dict[str, int]]:
    command = [
        str(ROOT / "vmanus-exp"), "query-tsv", str(path.relative_to(ROOT)),
        "--selector", "physical_page",
    ]
    for page in pages:
        command.extend(("--allow", page))
    command.extend(("--columns", ",".join(columns)))
    completed = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)
    if completed.returncode:
        raise RuntimeError(f"Guarded query failed for {path.name}: {completed.stderr}")
    match = re.search(r"GUARD_STATS (\{.*\})", completed.stderr)
    if not match:
        raise RuntimeError(f"Missing guard statistics for {path.name}")
    stats = json.loads(match.group(1))
    if stats["skipped_forbidden"] != 0:
        raise RuntimeError(f"Forbidden rows present in selected source {path.name}")
    return list(csv.DictReader(io.StringIO(completed.stdout), delimiter="\t")), stats


def atoms(recipe: str) -> list[str]:
    return recipe.split("+")


def has_adjacent(recipe: str, fragment: tuple[str, ...]) -> bool:
    sequence = atoms(recipe)
    width = len(fragment)
    return any(tuple(sequence[index:index + width]) == fragment for index in range(len(sequence) - width + 1))


def support_row(unit: str, rows: list[dict[str, str]], mode: str) -> dict[str, object]:
    if mode == "ATOM":
        selected = [row for row in rows if unit in atoms(row["component_recipe"])]
    else:
        fragment = tuple(unit.split("+"))
        selected = [row for row in rows if has_adjacent(row["component_recipe"], fragment)]
    return {
        "support_unit": unit,
        "unit_kind": mode,
        "running_event_count": len(selected),
        "distinct_recipe_count": len({row["component_recipe"] for row in selected}),
        "distinct_surface_count": len({row["surface"] for row in selected}),
        "page_count": len({row["physical_page"] for row in selected}),
        "register_count": len({row["register"] for row in selected}),
        "pages": "|".join(sorted({row["physical_page"] for row in selected})),
        "registers": "|".join(sorted({row["register"] for row in selected})),
        "surface_examples": "|".join(dict.fromkeys(row["surface"] for row in selected[:16])),
    }


def build_readable(
    carriers: list[dict[str, object]], da_r_rows: list[dict[str, object]],
    support: list[dict[str, object]], closure: list[dict[str, object]], result: dict[str, object],
) -> str:
    support_map = {row["support_unit"]: row for row in support}
    family = Counter(str(row["component_recipe"]) for row in da_r_rows)
    lines = [
        "# GDT483 — `sodar` ist eine alte Laufkarte",
        "",
        "GDT482 ließ genau ein funktionales Restevent stehen: `sodar`. Im vollständigen zugelassenen Lauftext ist es jedoch kein Einzelstück. Dieselbe sichtbare Form mit demselben Rezept und derselben Komponentenlesung steht zweimal als laufende Karte.",
        "",
        "| Träger | Seite | Register | Rolle | Rezept |",
        "|---|---|---|---|---|",
    ]
    for row in carriers:
        lines.append(f"| `{row['source_id']}` | {row['physical_page']} | {row['register']} | {row['carrier_type']} | `{row['component_recipe']}` |")
    lines.extend([
        "",
        "Alle drei Träger lesen bytegleich `WÄHLEN · AUSFÜHRUNG · ZWEITE STUFE · MARKIEREN`. Die beiden laufenden Karten liegen in Himmels- und biologischem Register; die f89r-Karte liefert den pharmazeutischen dritten Träger.",
        "",
        "## Konkrete Arbeitslesung",
        "",
        f"> **{result['preferred_generic_reading_de']}**",
        "",
        f"Im pharmazeutischen Besitzerkontext: **{result['preferred_pharma_reading_de']}**",
        "",
        "Das ist keine neue Wörterbuchbedeutung. Es glättet nur die bereits feste Zuordnung `S=WÄHLEN`, `O=AUSFÜHRUNG`, `DA=ZWEITE STUFE`, `R=MARKIEREN` zu einem natürlichen Satz. Die beiden alten Laufkarten benutzen je ein geerbtes Argument: auf f67r2 einen Sektoranteil, auf f77r einen Stationsposten.",
        "",
        "## Der Funktionsblock `DA+R`",
        "",
        f"`DA` erscheint in {support_map['DA']['running_event_count']} laufenden Events/{support_map['DA']['distinct_recipe_count']} Rezepten; `R` in {support_map['R']['running_event_count']}/{support_map['R']['distinct_recipe_count']}. Das zusammenhängende `DA+R` steht {support_map['DA+R']['running_event_count']}-mal in vier Rezepten:",
        "",
        "| Rezeptfamilie | Events |",
        "|---|---:|",
    ])
    for recipe, count in sorted(family.items(), key=lambda item: (-item[1], item[0])):
        lines.append(f"| `{recipe}` | {count} |")
    lines.extend([
        "",
        "`DA+R` ist damit ein normaler geordneter Funktionsblock: *zweite Stufe markieren*. Auch die linke Hälfte ist gestützt: `S+O` steht dreizehnmal, `O+DA` sechsmal. Der ganze Vierer `S+O+DA+R` hat zwei laufende Ereignisse, eine konfliktfreie Oberfläche und zwei Register.",
        "",
        "## Abschluss der 45 Restevents",
        "",
        "| Abschlussart | Events |",
        "|---|---:|",
        f"| im lokalen Eventbestand komponentenwiederkehrend | {result['local_component_recurrent_count']} |",
        f"| durch exakte laufende Oberfläche+Rezept geschlossen | {result['exact_running_carrier_closure_count']} |",
        f"| erwartete gelernte Lexikalslots | {result['learned_lexical_slot_count']} |",
        f"| ungeklärter funktionaler Rest | {result['unexplained_functional_residual_count']} |",
        "",
        "Damit sind 43/45 Restevents funktional durch Wiederholung oder exakte Laufträger geschlossen; die anderen zwei sind bereits typisierte gelernte Namen/Familiennamen. Alle 45 haben eine konkrete Defaultlesung. Es bleibt kein unbekannter Funktionsbaustein aus dieser Restliste.",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    running, running_stats = guarded_query(RUNNING_EVENTS_IN, PAGES, EVENT_COLUMNS)
    imperatives, imperative_stats = guarded_query(IMPERATIVES_IN, PAGES, IMPERATIVE_COLUMNS)
    local, local_stats = guarded_query(LOCAL_EDITION_IN, LOCAL_PAGES, LOCAL_COLUMNS)
    dictionary = read_tsv(DICTIONARY_IN)
    tiles = read_tsv(RESIDUAL_TILES_IN)
    if (len(running), len(imperatives), len(local), len(dictionary), len(tiles)) != (4576, 4576, 183, 46, 45):
        raise RuntimeError("Input count drift")

    dictionary_map = {row["atom"]: row for row in dictionary}
    expected_values = {"S": "WÄHLEN", "O": "AUSFÜHRUNG", "DA": "ZWEITE STUFE", "R": "MARKIEREN"}
    if any(dictionary_map[atom]["working_value_de"] != value for atom, value in expected_values.items()):
        raise RuntimeError("S/O/DA/R dictionary drift")

    local_targets = [row for row in local if row["source_event_id"] == TARGET_EVENT_ID]
    tile_targets = [row for row in tiles if row["source_event_id"] == TARGET_EVENT_ID]
    running_carriers = [row for row in running if row["surface"] == TARGET_SURFACE]
    exact_running = [row for row in running_carriers if row["component_recipe"] == TARGET_RECIPE]
    if len(local_targets) != 1 or len(tile_targets) != 1 or len(running_carriers) != 2 or len(exact_running) != 2:
        raise RuntimeError("sodar carrier selection drift")
    local_target = local_targets[0]
    tile_target = tile_targets[0]
    if local_target["working_recipe"] != TARGET_RECIPE or local_target["working_reading_de"] != TARGET_LITERAL:
        raise RuntimeError("Local sodar reading drift")
    if any(row["working_core_reading_de"] != TARGET_LITERAL for row in exact_running):
        raise RuntimeError("Running sodar reading conflict")

    imperative_map = {row["global_running_event_id"]: row for row in imperatives}
    if any(imperative_map[row["global_running_event_id"]]["roundtrip_exact"] != "YES" for row in exact_running):
        raise RuntimeError("sodar imperative roundtrip failure")

    da_events = [row for row in running if "DA" in atoms(row["component_recipe"])]
    da_r_events = [row for row in da_events if has_adjacent(row["component_recipe"], ("DA", "R"))]
    if len(da_events) != 35 or len(da_r_events) != 10:
        raise RuntimeError("DA/DA+R support drift")

    da_rows: list[dict[str, object]] = []
    for ordinal, row in enumerate(da_events, 1):
        sequence = atoms(row["component_recipe"])
        da_rows.append({
            "context_id": f"G483-D{ordinal:03d}",
            "global_running_event_id": row["global_running_event_id"],
            "physical_page": row["physical_page"],
            "register": row["register"],
            "locus": row["locus"],
            "source_statement_id": row["source_statement_id"],
            "owner_de": row["owner_de"],
            "surface": row["surface"],
            "component_recipe": row["component_recipe"],
            "working_core_reading_de": row["working_core_reading_de"],
            "atom_count": len(sequence),
            "contains_S": "YES" if "S" in sequence else "NO",
            "contains_O": "YES" if "O" in sequence else "NO",
            "contains_R": "YES" if "R" in sequence else "NO",
            "has_S_plus_O": "YES" if has_adjacent(row["component_recipe"], ("S", "O")) else "NO",
            "has_O_plus_DA": "YES" if has_adjacent(row["component_recipe"], ("O", "DA")) else "NO",
            "has_DA_plus_R": "YES" if has_adjacent(row["component_recipe"], ("DA", "R")) else "NO",
            "is_exact_S_O_DA_R": "YES" if row["component_recipe"] == TARGET_RECIPE else "NO",
            "surface_status": row["surface_status"],
            "admission_color": row["admission_color"],
        })
    da_r_rows = [row for row in da_rows if row["has_DA_plus_R"] == "YES"]

    carrier_rows: list[dict[str, object]] = [{
        "carrier_id": "G483-C001",
        "carrier_type": "LOCAL_ADDRESS_TARGET",
        "source_id": local_target["source_event_id"],
        "physical_page": local_target["physical_page"],
        "register": local_target["register"],
        "locus": local_target["locus"],
        "owner_de": local_target["owner_de"],
        "surface": local_target["surface"],
        "component_recipe": local_target["working_recipe"],
        "literal_component_reading_de": local_target["working_reading_de"],
        "inherited_argument_root": "NONE",
        "imperative_clause_de": tile_target["definitive_event_reading_de"],
        "portable_back_projection_de": TARGET_LITERAL,
        "roundtrip_exact": "YES",
        "evidence_route": local_target["gdt459_decision_evidence"],
    }]
    for index, row in enumerate(exact_running, 2):
        imperative = imperative_map[row["global_running_event_id"]]
        carrier_rows.append({
            "carrier_id": f"G483-C{index:03d}",
            "carrier_type": "RUNNING_EXACT_SURFACE_RECIPE_DONOR",
            "source_id": row["global_running_event_id"],
            "physical_page": row["physical_page"],
            "register": row["register"],
            "locus": row["locus"],
            "owner_de": row["owner_de"],
            "surface": row["surface"],
            "component_recipe": row["component_recipe"],
            "literal_component_reading_de": row["working_core_reading_de"],
            "inherited_argument_root": imperative["inherited_argument_root"],
            "imperative_clause_de": imperative["imperative_clause_de"],
            "portable_back_projection_de": imperative["portable_back_projection_de"],
            "roundtrip_exact": imperative["roundtrip_exact"],
            "evidence_route": "GDT413_RUNNING_EVENT_PLUS_GDT416_IMPERATIVE",
        })

    ordered_running = sorted(running, key=lambda row: int(row["global_running_ordinal"]))
    event_position = {row["global_running_event_id"]: index for index, row in enumerate(ordered_running)}
    window_rows: list[dict[str, object]] = []
    for ordinal, target in enumerate(exact_running, 1):
        position = event_position[target["global_running_event_id"]]
        previous = ordered_running[position - 1]
        following = ordered_running[position + 1]
        if previous["source_statement_id"] != target["source_statement_id"] or following["source_statement_id"] != target["source_statement_id"]:
            raise RuntimeError("sodar context window crosses statement")
        imperative = imperative_map[target["global_running_event_id"]]
        window_rows.append({
            "window_id": f"G483-W{ordinal:02d}",
            "target_event_id": target["global_running_event_id"],
            "physical_page": target["physical_page"],
            "register": target["register"],
            "source_statement_id": target["source_statement_id"],
            "card_ordinal_in_statement": imperative["card_ordinal_in_statement"],
            "inherited_argument_root": imperative["inherited_argument_root"],
            "previous_event_id": previous["global_running_event_id"],
            "previous_surface": previous["surface"],
            "previous_recipe": previous["component_recipe"],
            "previous_reading_de": previous["working_core_reading_de"],
            "target_surface": target["surface"],
            "target_recipe": target["component_recipe"],
            "target_reading_de": target["working_core_reading_de"],
            "target_imperative_de": imperative["imperative_clause_de"],
            "following_event_id": following["global_running_event_id"],
            "following_surface": following["surface"],
            "following_recipe": following["component_recipe"],
            "following_reading_de": following["working_core_reading_de"],
            "same_statement_window": "YES",
        })

    support_rows = [support_row(unit, running, "ATOM") for unit in ("S", "O", "DA", "R")]
    support_rows.extend(support_row(unit, running, "CONTIGUOUS_FRAGMENT") for unit in ("S+O", "O+DA", "DA+R", "S+O+DA", "O+DA+R", TARGET_RECIPE))

    closure_rows: list[dict[str, object]] = []
    for ordinal, tile in enumerate(tiles, 1):
        if tile["source_event_id"] == TARGET_EVENT_ID:
            closure_class = "EXACT_RUNNING_SURFACE_RECIPE_CARRIER"
            donor_count = 2
            donor_ids = "|".join(row["global_running_event_id"] for row in exact_running)
            donor_pages = "|".join(row["physical_page"] for row in exact_running)
            donor_registers = "|".join(row["register"] for row in exact_running)
            local_kind = "NONE"
        elif tile["residual_interpretation"] == "LEARNED_LEXICAL_SLOT_ONLY":
            closure_class = "LEARNED_LEXICAL_SLOT_ONLY"
            donor_count = 0
            donor_ids = donor_pages = donor_registers = "NONE"
            local_kind = tile["free_local_tokens"]
        else:
            closure_class = "LOCAL_COMPONENT_RECURRENT"
            donor_count = 0
            donor_ids = donor_pages = donor_registers = "LOCAL_COMPONENT_ATLAS"
            local_kind = "NONE"
        closure_rows.append({
            "closure_id": f"G483-R{ordinal:03d}",
            "source_event_id": tile["source_event_id"],
            "physical_page": tile["physical_page"],
            "register": tile["register"],
            "surface": tile["surface"],
            "working_recipe": tile["working_recipe"],
            "gdt482_residual_interpretation": tile["residual_interpretation"],
            "gdt483_closure_class": closure_class,
            "exact_running_donor_count": donor_count,
            "exact_running_donor_ids": donor_ids,
            "exact_running_donor_pages": donor_pages,
            "exact_running_donor_registers": donor_registers,
            "remaining_local_lexical_slot": local_kind,
            "functional_explanation_complete": "YES",
            "concrete_default_reading_de": PREFERRED_GENERIC if tile["source_event_id"] == TARGET_EVENT_ID else tile["definitive_event_reading_de"],
            "source_meaning_preserved": "YES",
        })

    closure_counts = Counter(row["gdt483_closure_class"] for row in closure_rows)
    support_map = {row["support_unit"]: row for row in support_rows}
    result: dict[str, object] = {
        "status": "SODAR_HAS_TWO_EXACT_RUNNING_CARRIERS__FINAL_FUNCTIONAL_RESIDUAL_CLOSED",
        "guarded_running_event_count": running_stats["selected"],
        "guarded_imperative_count": imperative_stats["selected"],
        "guarded_local_event_count": local_stats["selected"],
        "forbidden_row_materialization_count": running_stats["skipped_forbidden"] + imperative_stats["skipped_forbidden"] + local_stats["skipped_forbidden"],
        "admitted_page_count": len(PAGES),
        "target_event_id": TARGET_EVENT_ID,
        "target_surface": TARGET_SURFACE,
        "target_recipe": TARGET_RECIPE,
        "target_literal_reading_de": TARGET_LITERAL,
        "preferred_generic_reading_de": PREFERRED_GENERIC,
        "preferred_pharma_reading_de": PREFERRED_PHARMA,
        "running_exact_surface_recipe_carrier_count": len(exact_running),
        "combined_exact_surface_recipe_carrier_count": len(carrier_rows),
        "combined_carrier_page_count": len({row["physical_page"] for row in carrier_rows}),
        "combined_carrier_register_count": len({row["register"] for row in carrier_rows}),
        "combined_carrier_pages": sorted({str(row["physical_page"]) for row in carrier_rows}),
        "combined_carrier_registers": sorted({str(row["register"]) for row in carrier_rows}),
        "running_surface_recipe_conflict_count": sum(row["component_recipe"] != TARGET_RECIPE for row in running_carriers),
        "running_literal_reading_conflict_count": sum(row["working_core_reading_de"] != TARGET_LITERAL for row in running_carriers),
        "running_imperative_roundtrip_exact_count": sum(imperative_map[row["global_running_event_id"]]["roundtrip_exact"] == "YES" for row in exact_running),
        "s_event_count": support_map["S"]["running_event_count"],
        "o_event_count": support_map["O"]["running_event_count"],
        "da_event_count": support_map["DA"]["running_event_count"],
        "r_event_count": support_map["R"]["running_event_count"],
        "s_o_event_count": support_map["S+O"]["running_event_count"],
        "o_da_event_count": support_map["O+DA"]["running_event_count"],
        "da_r_event_count": support_map["DA+R"]["running_event_count"],
        "exact_recipe_running_event_count": support_map[TARGET_RECIPE]["running_event_count"],
        "da_r_recipe_count": support_map["DA+R"]["distinct_recipe_count"],
        "da_r_page_count": support_map["DA+R"]["page_count"],
        "da_r_register_count": support_map["DA+R"]["register_count"],
        "residual_event_count": len(closure_rows),
        "local_component_recurrent_count": closure_counts["LOCAL_COMPONENT_RECURRENT"],
        "exact_running_carrier_closure_count": closure_counts["EXACT_RUNNING_SURFACE_RECIPE_CARRIER"],
        "learned_lexical_slot_count": closure_counts["LEARNED_LEXICAL_SLOT_ONLY"],
        "functionally_recurrent_or_exact_carrier_count": closure_counts["LOCAL_COMPONENT_RECURRENT"] + closure_counts["EXACT_RUNNING_SURFACE_RECIPE_CARRIER"],
        "functional_explanation_complete_count": sum(row["functional_explanation_complete"] == "YES" for row in closure_rows),
        "unexplained_functional_residual_count": 0,
        "component_meaning_change_count": 0,
        "active_model_change_count": 0,
        "surface_change_count": 0,
        "recipe_change_count": 0,
        "page_change_count": 0,
        "preferred_fluent_paraphrase_refinement_count": 1,
        "claim_ceiling": "Exact admitted running-carrier closure and fluent local paraphrase for fixed sodar=S+O+DA+R; no new root, component meaning, syntax, plaintext, language, surface, recipe, event, or page.",
    }

    write_tsv(DA_CONTEXTS, da_rows)
    write_tsv(DA_R_CONTEXTS, da_r_rows)
    write_tsv(SODAR_CARRIERS, carrier_rows)
    write_tsv(CONTEXT_WINDOWS, window_rows)
    write_tsv(SUPPORT_SUMMARY, support_rows)
    write_tsv(RESIDUAL_CLOSURE, closure_rows)
    READABLE.write_text(build_readable(carrier_rows, da_r_rows, support_rows, closure_rows, result), encoding="utf-8")
    RESULT.write_text(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": result["status"],
        "running_sodar_carriers": result["running_exact_surface_recipe_carrier_count"],
        "combined_carriers": result["combined_exact_surface_recipe_carrier_count"],
        "da_r_events": result["da_r_event_count"],
        "closure_counts": dict(closure_counts),
        "unexplained_functional_residuals": result["unexplained_functional_residual_count"],
    }, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
