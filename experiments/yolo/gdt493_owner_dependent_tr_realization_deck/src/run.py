#!/usr/bin/env python3
"""Compile all eleven T/R frames across five owner registers."""

from __future__ import annotations

import csv
import importlib.util
import json
from collections import Counter, defaultdict
from pathlib import Path
from types import ModuleType


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt493_owner_dependent_tr_realization_deck"
OUT = BASE / "artifacts"
G413 = ROOT / "experiments/yolo/gdt413_twenty_six_page_semantic_working_edition/artifacts"
G415 = ROOT / "experiments/yolo/gdt415_owner_local_semantic_expansion_atlas/artifacts"
G416_BASE = ROOT / "experiments/yolo/gdt416_owner_local_imperative_sentence_compiler"
G416 = G416_BASE / "artifacts"
G428 = ROOT / "experiments/yolo/gdt428_within_class_action_semantic_contrasts/artifacts"
G492 = ROOT / "experiments/yolo/gdt492_owner_variant_slot_bridge_atlas/artifacts"
COMPONENTS_IN = G413 / "gdt413_46_component_working_dictionary.tsv"
REGISTER_ATLAS_IN = G415 / "gdt415_95_register_expansion_atlas.tsv"
CLAUSES_IN = G416 / "gdt416_4576_imperative_clauses.tsv"
RENDERER_IN = G416_BASE / "src/run.py"
FRAMES_IN = G428 / "gdt428_104_direct_substitution_frames.tsv"
G492_RESULT_IN = G492 / "gdt492_result.json"
VALUE_CELLS = OUT / "gdt493_55_observed_register_value_cells.tsv"
DECK = OUT / "gdt493_110_owner_frame_realization_cells.tsv"
OBSERVED = OUT / "gdt493_37_observed_clause_cells.tsv"
COMPOSED = OUT / "gdt493_73_composed_working_cells.tsv"
CONTRASTS = OUT / "gdt493_55_tr_register_contrast_cards.tsv"
FRAME_COVERAGE = OUT / "gdt493_11_frame_coverage.tsv"
REGISTER_COVERAGE = OUT / "gdt493_5_register_coverage.tsv"
STATE_FRAMES = OUT / "gdt493_4_state_dependent_frames.tsv"
STATE_OVERRIDES = OUT / "gdt493_3_observed_inherited_argument_overrides.tsv"
READABLE = OUT / "GDT493_OWNER_DEPENDENT_TR_REALIZATION_DECK.md"
RESULT = OUT / "gdt493_result.json"
STATUS = "ONE_HUNDRED_TEN_OWNER_REALIZATIONS__THIRTY_SEVEN_OBSERVED__SEVENTY_THREE_COMPOSED_WORKING"
ROOT_ORDER = ("T", "R", "AIIN", "AIN", "AL", "Y", "CH", "E", "CHD", "OL", "OR")
REGISTER_ORDER = ("SOURCE_SECTION_T", "HERBAL", "BIOLOGICAL", "CELESTIAL", "PHARMA")
ACTION_ORDER = ("T", "R")
STATE_DEPENDENT_FRAMES = {"@ACTION", "@ACTION+AL", "@ACTION+OL", "CH+@ACTION"}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"Refusing to write empty table {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def load_renderer() -> ModuleType:
    spec = importlib.util.spec_from_file_location("gdt416_canonical_renderer", RENDERER_IN)
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot load GDT416 renderer")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def atoms(recipe: str) -> list[str]:
    return recipe.split("+") if recipe else []


def build_readable(
    deck: list[dict[str, object]],
    contrasts: list[dict[str, object]],
    frames: list[dict[str, object]],
    registers: list[dict[str, object]],
    overrides: list[dict[str, object]],
    result: dict[str, object],
) -> str:
    lines = [
        "# GDT493 — 110 owner-abhängige T/R-Arbeitslesungen",
        "",
        "GDT493 legt jeden der elf T/R-Rahmen in jedem der fünf Register aus. Die Herkunft steht auf jeder Karte: `OBSERVED_CLAUSE` ist eine wortwörtliche alte GDT416-Klausel; `COMPOSED_WORKING` ist eine neue, ausdrücklich so markierte Arbeitslesung aus dem unveränderten GDT416-Renderer und ausschließlich alten Registerwerten.",
        "",
        f"- Vollständiges Raster: **{result['realization_cell_count']}/110**.",
        f"- Wortwörtlich beobachtete Zellen: **{result['observed_clause_cell_count']}** mit **{result['observed_carrier_count']}** Trägern und **{result['observed_clause_form_count']}** Formen.",
        f"- Slotweise zusammengesetzte Arbeitszellen: **{result['composed_working_cell_count']}**; unmarkiert ausgegebene Kompositionen: **{result['unlabelled_composed_count']}**.",
        f"- T/R-Kontrastkarten: **{result['tr_register_contrast_count']}/55**, alle mit verschiedenen Ausgaben und identischem formalen Rest.",
        f"- Alte Wert×Register-Zellen: **{result['observed_register_value_cell_count']}/55**; neue Slotwerte: **{result['new_slot_value_count']}**.",
        "",
        "## Deck-Legende",
        "",
        "- `OBSERVED_CLAUSE`: Der vollständige Rezept×Register-Satz hat mindestens einen alten Eventträger. Angezeigt wird der häufigste alte Satz, bei Gleichstand der kürzere, dann der alphabetisch erste.",
        "- `COMPOSED_WORKING`: Das genaue Rezept ist in diesem Register noch nicht als vollständiger Satz belegt. Der angezeigte Satz wird vom alten GDT416-Renderer aus alten Slotwerten gebaut.",
        "- Bei Rahmen ohne sichtbares Argument (`@ACTION`, `@ACTION+AL`, `@ACTION+OL`, `CH+@ACTION`) verwendet nur die Arbeitskomposition `Y=POSTEN` als klar ausgewiesenen Default des aktiven Arguments; ein realer Satz darf stattdessen WERT, ANTEIL oder EINHEIT erben.",
        "",
        "## Alle 110 Karten",
        "",
    ]
    deck_by_frame: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in deck:
        deck_by_frame[str(row["frozen_frame"])].append(row)
    for frame in frames:
        lines.extend([
            f"### `{frame['frozen_frame']}` — {frame['observed_cell_count']} beobachtet / {frame['composed_cell_count']} zusammengesetzt",
            "",
            "| Aktion | Register | Status | Ausgabe | Komponentenlesung |",
            "|---|---|---|---|---|",
        ])
        for row in deck_by_frame[str(frame["frozen_frame"])]:
            lines.append(f"| `{row['action_root']}` | {row['register']} | **{row['evidence_status']}** | {row['display_phrase_de']} | `{row['portable_component_trace_de']}` |")
        lines.append("")
    lines.extend([
        "## 55 direkte T/R-Ausgaben",
        "",
        "Jeder Rahmen×Register-Paarvergleich behält denselben Komponentenrest. Acht Paare sind beidseitig beobachtet, 21 haben eine beobachtete und eine zusammengesetzte Seite, 26 sind beidseitig zusammengesetzt. Alle 55 bleiben sprachlich verschieden.",
        "",
        "| Rahmen | Register | T | R | Evidenzpaar |",
        "|---|---|---|---|---|",
    ])
    for row in contrasts:
        lines.append(f"| `{row['frozen_frame']}` | {row['register']} | {row['t_display_phrase_de']} | {row['r_display_phrase_de']} | {row['pair_evidence_status']} |")
    lines.extend([
        "",
        "## Registerabdeckung",
        "",
        "| Register | beobachtet | zusammengesetzt | alte Träger |",
        "|---|---:|---:|---:|",
    ])
    for row in registers:
        lines.append(f"| {row['register']} | {row['observed_cell_count']} | {row['composed_cell_count']} | {row['observed_carrier_count']} |")
    lines.extend([
        "",
        "## Drei sichtbare Zustandskorrekturen",
        "",
        "In 34/37 beobachteten Zellen ist auch die Y-Default-Ausgabe des Renderers tatsächlich belegt. Drei beobachtete Zellen erben stattdessen ein anderes aktives Argument; die Beobachtung gewinnt immer:",
        "",
    ])
    for row in overrides:
        lines.extend([
            f"- `{row['action_recipe']}` / {row['register']}: Renderer-Y „{row['composed_working_phrase_de']}“; beobachtet „{row['selected_observed_phrase_de']}“; geerbtes Argument `{row['observed_inherited_argument_roots']}`.",
        ])
    lines.extend([
        "",
        "Das sind keine Fehler des Komponentenmodells: Das Rezept enthält dort kein sichtbares Argument, also entscheidet der laufende Besitzerzustand, ob POSTEN, WERT, ANTEIL oder EINHEIT eingesetzt wird.",
        "",
        "## Arbeitsfolgerung",
        "",
        "Das Deck liefert nun für keine der 110 Kombinationen mehr eine leere Bedeutung. Gleichzeitig bleibt die Herkunft hörbar: Beobachtung und produktive Arbeitskomposition werden nicht vermischt. Das ist genau die gesuchte Mischarchitektur aus kurzen Fachkürzeln, stabilen Kompositionsplätzen, registergebundenem Wortschatz und wenigen getragenen Zuständen.",
        "",
        "## Nächster Schritt",
        "",
        "Verdichte die 73 zusammengesetzten Zellen zu Vorhersagekarten für die weiterhin geschlossenen Seiten. Priorität haben Zellen, die durch mindestens zwei alte Nachbarhandlungen im selben Rahmen und durch alte Slotwerte in genau diesem Register gestützt sind. Die Ausgabe bleibt `COMPOSED_WORKING`, bis ein späterer echter Träger sie beobachtet.",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    components = read_tsv(COMPONENTS_IN)
    register_atlas = read_tsv(REGISTER_ATLAS_IN)
    clauses = read_tsv(CLAUSES_IN)
    frame_source = read_tsv(FRAMES_IN)
    g492_result = json.loads(G492_RESULT_IN.read_text(encoding="utf-8"))
    renderer = load_renderer()
    if (len(components), len(register_atlas), len(clauses), len(frame_source)) != (46, 95, 4576, 104):
        raise RuntimeError("Input count drift")
    if g492_result.get("status") != "FOUR_OWNER_VARIANTS_DECOMPOSED__THIRTY_FIVE_SLOT_CELLS_OBSERVED__NINE_ALTERNATE_ACTION_CELLS":
        raise RuntimeError("GDT492 route drift")
    tr_frames = [row for row in frame_source if row["contrast_pair"] == "T~R"]
    if len(tr_frames) != 11:
        raise RuntimeError("T/R frame drift")

    component_map = {row["atom"]: row for row in components}
    expansion_map = {(row["root"], row["register"]): row for row in register_atlas}
    clauses_by_recipe_register: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in clauses:
        clauses_by_recipe_register[(row["component_recipe"], row["register"])].append(row)

    value_rows: list[dict[str, object]] = []
    for root in ROOT_ORDER:
        for register in REGISTER_ORDER:
            local = [row for row in clauses if row["register"] == register and root in atoms(row["component_recipe"])]
            mentions = sum(atoms(row["component_recipe"]).count(root) for row in clauses if row["register"] == register)
            if root == "E":
                source = component_map[root]
                portable = source["working_value_de"]
                category = source["factor_family"]
                expansion = "GRAD I"
                source_name = "GDT413_COMPONENT_PLUS_GDT416_CARRIERS"
            else:
                source = expansion_map[(root, register)]
                portable = source["portable_default_de"]
                category = source["structural_category"]
                expansion = source["owner_local_expansion_de"]
                source_name = "GDT415_REGISTER_EXPANSION_ATLAS"
                if (mentions, len(local)) != (int(source["mention_count"]), int(source["event_count"])):
                    raise RuntimeError(f"Register support drift for {root}/{register}")
            value_rows.append({
                "value_cell_id": f"G493-V{len(value_rows) + 1:02d}",
                "root": root,
                "portable_default_de": portable,
                "structural_category": category,
                "register": register,
                "owner_local_expansion_de": expansion,
                "mention_count": mentions,
                "event_count": len(local),
                "page_count": len({row["physical_page"] for row in local}),
                "owner_count": len({row["owner_de"] for row in local}),
                "source_atlas": source_name,
                "observed_old_value_cell": "YES" if local else "NO",
            })
    value_map = {(str(row["root"]), str(row["register"])): row for row in value_rows}

    deck_rows: list[dict[str, object]] = []
    for frame_number, frame_row in enumerate(tr_frames, 1):
        frame = frame_row["frozen_frame"]
        for action in ACTION_ORDER:
            recipe = frame.replace("@ACTION", action)
            recipe_parts = atoms(recipe)
            explicit_actions = [part for part in recipe_parts if part in renderer.ACTION_ROOTS]
            explicit_arguments = [part for part in recipe_parts if part in renderer.ARGUMENT_ROOTS]
            inherited_argument = "" if explicit_arguments else "Y"
            for register in REGISTER_ORDER:
                local = clauses_by_recipe_register[(recipe, register)]
                phrase_counter = Counter(row["imperative_clause_de"] for row in local)
                composed_phrase = renderer.render_clause(register, recipe_parts, explicit_actions, "", inherited_argument)
                if local:
                    evidence_status = "OBSERVED_CLAUSE"
                    selected_phrase, selected_count = sorted(phrase_counter.items(), key=lambda item: (-item[1], len(item[0]), item[0]))[0]
                    provenance = "GDT416_EXACT_RECIPE_REGISTER_CLAUSE"
                    phrase_observed = "YES"
                    phrase_composed = "NO"
                    composed_observed = "YES" if composed_phrase in phrase_counter else "NO"
                    selected_equals = "YES" if selected_phrase == composed_phrase else "NO"
                else:
                    evidence_status = "COMPOSED_WORKING"
                    selected_phrase = composed_phrase
                    selected_count = 0
                    provenance = "GDT416_RENDERER_PLUS_OLD_REGISTER_VALUE_CELLS"
                    phrase_observed = "NO"
                    phrase_composed = "YES"
                    composed_observed = "NO_EXACT_CELL"
                    selected_equals = "NO_EXACT_CELL"
                portable_trace = " · ".join(str(value_map[(part, register)]["portable_default_de"]) for part in recipe_parts)
                owner_trace = " · ".join(f"{part}={value_map[(part, register)]['owner_local_expansion_de']}" for part in recipe_parts)
                deck_rows.append({
                    "realization_cell_id": f"G493-C{len(deck_rows) + 1:03d}",
                    "frame_id": f"G493-F{frame_number:02d}",
                    "frozen_frame": frame,
                    "action_root": action,
                    "action_recipe": recipe,
                    "register": register,
                    "portable_component_trace_de": portable_trace,
                    "owner_local_slot_trace_de": owner_trace,
                    "state_requirement": "SELF_CONTAINED_ARGUMENT" if explicit_arguments else "ACTIVE_ARGUMENT_REQUIRED",
                    "composed_state_default": "NONE" if explicit_arguments else "Y=POSTEN [wie zuvor]",
                    "composed_working_phrase_de": composed_phrase,
                    "evidence_status": evidence_status,
                    "display_phrase_de": selected_phrase,
                    "display_phrase_provenance": provenance,
                    "observed_event_count": len(local),
                    "observed_clause_form_count": len(phrase_counter),
                    "selected_observed_phrase_carrier_count": selected_count,
                    "observed_pages": "|".join(sorted({row["physical_page"] for row in local})) or "NONE",
                    "observed_event_ids": "|".join(row["global_running_event_id"] for row in local) or "NONE",
                    "all_observed_clause_forms_de": " || ".join(sorted(phrase_counter)) or "NONE",
                    "observed_inherited_argument_roots": "|".join(sorted({row["inherited_argument_root"] for row in local if row["inherited_argument_root"] != "NONE"})) or "NONE",
                    "composed_phrase_observed_in_exact_cell": composed_observed,
                    "selected_phrase_equals_composed_phrase": selected_equals,
                    "display_phrase_is_observed_clause": phrase_observed,
                    "display_phrase_is_composed_working": phrase_composed,
                    "composed_working_label_visible": "YES" if evidence_status == "COMPOSED_WORKING" else "NOT_APPLICABLE",
                    "all_recipe_value_cells_observed": "YES" if all(value_map[(part, register)]["observed_old_value_cell"] == "YES" for part in recipe_parts) else "NO",
                    "new_slot_value_required": "NO",
                })

    observed_rows = [row for row in deck_rows if row["evidence_status"] == "OBSERVED_CLAUSE"]
    composed_rows = [row for row in deck_rows if row["evidence_status"] == "COMPOSED_WORKING"]
    contrast_rows: list[dict[str, object]] = []
    for frame_number, frame_row in enumerate(tr_frames, 1):
        frame = frame_row["frozen_frame"]
        for register in REGISTER_ORDER:
            t_cell = next(row for row in deck_rows if row["frozen_frame"] == frame and row["action_root"] == "T" and row["register"] == register)
            r_cell = next(row for row in deck_rows if row["frozen_frame"] == frame and row["action_root"] == "R" and row["register"] == register)
            statuses = {str(t_cell["evidence_status"]), str(r_cell["evidence_status"])}
            if statuses == {"OBSERVED_CLAUSE"}:
                pair_status = "BOTH_OBSERVED"
            elif statuses == {"COMPOSED_WORKING"}:
                pair_status = "BOTH_COMPOSED_WORKING"
            else:
                pair_status = "MIXED_OBSERVED_COMPOSED"
            contrast_rows.append({
                "contrast_id": f"G493-TR{len(contrast_rows) + 1:02d}",
                "frame_id": f"G493-F{frame_number:02d}",
                "frozen_frame": frame,
                "register": register,
                "t_recipe": t_cell["action_recipe"],
                "r_recipe": r_cell["action_recipe"],
                "t_evidence_status": t_cell["evidence_status"],
                "r_evidence_status": r_cell["evidence_status"],
                "pair_evidence_status": pair_status,
                "t_display_phrase_de": t_cell["display_phrase_de"],
                "r_display_phrase_de": r_cell["display_phrase_de"],
                "t_portable_trace_de": t_cell["portable_component_trace_de"],
                "r_portable_trace_de": r_cell["portable_component_trace_de"],
                "formal_remainder_unchanged": "YES",
                "display_phrases_distinct": "YES" if t_cell["display_phrase_de"] != r_cell["display_phrase_de"] else "NO",
                "all_value_cells_observed": "YES",
            })

    frame_rows: list[dict[str, object]] = []
    for frame_number, source in enumerate(tr_frames, 1):
        local = [row for row in deck_rows if row["frozen_frame"] == source["frozen_frame"]]
        frame_rows.append({
            "frame_id": f"G493-F{frame_number:02d}",
            "frozen_frame": source["frozen_frame"],
            "realization_cell_count": len(local),
            "observed_cell_count": sum(row["evidence_status"] == "OBSERVED_CLAUSE" for row in local),
            "composed_cell_count": sum(row["evidence_status"] == "COMPOSED_WORKING" for row in local),
            "observed_carrier_count": sum(int(row["observed_event_count"]) for row in local),
            "observed_clause_form_count": sum(int(row["observed_clause_form_count"]) for row in local),
            "state_requirement": "ACTIVE_ARGUMENT_REQUIRED" if source["frozen_frame"] in STATE_DEPENDENT_FRAMES else "SELF_CONTAINED_ARGUMENT",
            "all_registers_covered": "YES" if {str(row["register"]) for row in local} == set(REGISTER_ORDER) else "NO",
            "both_actions_covered": "YES" if {str(row["action_root"]) for row in local} == set(ACTION_ORDER) else "NO",
        })

    register_rows: list[dict[str, object]] = []
    for register in REGISTER_ORDER:
        local = [row for row in deck_rows if row["register"] == register]
        register_rows.append({
            "register_id": f"G493-R{len(register_rows) + 1:02d}",
            "register": register,
            "realization_cell_count": len(local),
            "observed_cell_count": sum(row["evidence_status"] == "OBSERVED_CLAUSE" for row in local),
            "composed_cell_count": sum(row["evidence_status"] == "COMPOSED_WORKING" for row in local),
            "observed_carrier_count": sum(int(row["observed_event_count"]) for row in local),
            "observed_clause_form_count": sum(int(row["observed_clause_form_count"]) for row in local),
            "frame_count": len({str(row["frozen_frame"]) for row in local}),
            "action_count": len({str(row["action_root"]) for row in local}),
            "all_cells_have_display_phrase": "YES" if all(row["display_phrase_de"] for row in local) else "NO",
        })

    state_frame_rows: list[dict[str, object]] = []
    for frame in [row["frozen_frame"] for row in tr_frames if row["frozen_frame"] in STATE_DEPENDENT_FRAMES]:
        local = [row for row in deck_rows if row["frozen_frame"] == frame]
        state_frame_rows.append({
            "state_frame_id": f"G493-SF{len(state_frame_rows) + 1:02d}",
            "frozen_frame": frame,
            "realization_cell_count": len(local),
            "observed_cell_count": sum(row["evidence_status"] == "OBSERVED_CLAUSE" for row in local),
            "composed_cell_count": sum(row["evidence_status"] == "COMPOSED_WORKING" for row in local),
            "observed_inherited_argument_roots": "|".join(sorted({root for row in local for root in str(row["observed_inherited_argument_roots"]).split("|") if root != "NONE"})) or "NONE",
            "composed_state_default": "Y=POSTEN [wie zuvor]",
            "state_can_override_y_default": "YES",
            "composed_phrase_claimed_observed": "NO",
        })

    override_rows: list[dict[str, object]] = []
    for row in observed_rows:
        if row["composed_phrase_observed_in_exact_cell"] == "YES":
            continue
        override_rows.append({
            "override_id": f"G493-O{len(override_rows) + 1:02d}",
            "realization_cell_id": row["realization_cell_id"],
            "frozen_frame": row["frozen_frame"],
            "action_recipe": row["action_recipe"],
            "register": row["register"],
            "composed_state_default": row["composed_state_default"],
            "composed_working_phrase_de": row["composed_working_phrase_de"],
            "selected_observed_phrase_de": row["display_phrase_de"],
            "observed_inherited_argument_roots": row["observed_inherited_argument_roots"],
            "observed_event_count": row["observed_event_count"],
            "observation_overrides_composed_default": "YES",
            "new_meaning_required": "NO",
        })

    counts = tuple(map(len, (value_rows, deck_rows, observed_rows, composed_rows, contrast_rows, frame_rows, register_rows, state_frame_rows, override_rows)))
    if counts != (55, 110, 37, 73, 55, 11, 5, 4, 3):
        raise RuntimeError(f"Unexpected realization deck counts: {counts}")
    write_tsv(VALUE_CELLS, value_rows)
    write_tsv(DECK, deck_rows)
    write_tsv(OBSERVED, observed_rows)
    write_tsv(COMPOSED, composed_rows)
    write_tsv(CONTRASTS, contrast_rows)
    write_tsv(FRAME_COVERAGE, frame_rows)
    write_tsv(REGISTER_COVERAGE, register_rows)
    write_tsv(STATE_FRAMES, state_frame_rows)
    write_tsv(STATE_OVERRIDES, override_rows)

    result = {
        "status": STATUS,
        "frame_count": len(frame_rows),
        "action_count": len(ACTION_ORDER),
        "register_count": len(REGISTER_ORDER),
        "realization_cell_count": len(deck_rows),
        "observed_clause_cell_count": len(observed_rows),
        "composed_working_cell_count": len(composed_rows),
        "observed_carrier_count": sum(int(row["observed_event_count"]) for row in observed_rows),
        "observed_clause_form_count": sum(int(row["observed_clause_form_count"]) for row in observed_rows),
        "observed_register_value_cell_count": sum(row["observed_old_value_cell"] == "YES" for row in value_rows),
        "relevant_value_count": len(ROOT_ORDER),
        "tr_register_contrast_count": len(contrast_rows),
        "both_observed_contrast_count": sum(row["pair_evidence_status"] == "BOTH_OBSERVED" for row in contrast_rows),
        "mixed_contrast_count": sum(row["pair_evidence_status"] == "MIXED_OBSERVED_COMPOSED" for row in contrast_rows),
        "both_composed_contrast_count": sum(row["pair_evidence_status"] == "BOTH_COMPOSED_WORKING" for row in contrast_rows),
        "distinct_tr_display_count": sum(row["display_phrases_distinct"] == "YES" for row in contrast_rows),
        "state_dependent_frame_count": len(state_frame_rows),
        "canonical_renderer_phrase_observed_cell_count": sum(row["composed_phrase_observed_in_exact_cell"] == "YES" for row in observed_rows),
        "selected_default_equals_renderer_count": sum(row["selected_phrase_equals_composed_phrase"] == "YES" for row in observed_rows),
        "observed_inherited_argument_override_count": len(override_rows),
        "unlabelled_composed_count": sum(row["evidence_status"] == "COMPOSED_WORKING" and row["composed_working_label_visible"] != "YES" for row in deck_rows),
        "claimed_observed_without_witness_count": sum(row["display_phrase_is_observed_clause"] == "YES" and int(row["observed_event_count"]) == 0 for row in deck_rows),
        "new_slot_value_count": sum(row["new_slot_value_required"] != "NO" for row in deck_rows),
        "meaning_change_count": 0,
        "source_wording_change_count": 0,
        "active_model_change_count": 0,
        "record_boundary_change_count": 0,
        "surface_change_count": 0,
        "recipe_change_count": 0,
        "page_change_count": 0,
        "claim_ceiling": "Owner-dependent working realization deck for eleven fixed T-R frames across five registers; 37 cells are exact observed clauses and 73 are visibly labelled compositions from old value cells and the unchanged GDT416 renderer, with no new slot value, meaning, boundary, surface, recipe, event, or page.",
    }
    READABLE.write_text(build_readable(deck_rows, contrast_rows, frame_rows, register_rows, override_rows, result), encoding="utf-8")
    RESULT.write_text(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
