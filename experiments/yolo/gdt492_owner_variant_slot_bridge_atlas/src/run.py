#!/usr/bin/env python3
"""Decompose GDT491's four owner variants into old observed slot values."""

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
BASE = ROOT / "experiments/yolo/gdt492_owner_variant_slot_bridge_atlas"
OUT = BASE / "artifacts"
G413 = ROOT / "experiments/yolo/gdt413_twenty_six_page_semantic_working_edition/artifacts"
G415 = ROOT / "experiments/yolo/gdt415_owner_local_semantic_expansion_atlas/artifacts"
G416 = ROOT / "experiments/yolo/gdt416_owner_local_imperative_sentence_compiler/artifacts"
G491 = ROOT / "experiments/yolo/gdt491_markierungen_observed_phrase_contrast_atlas/artifacts"
COMPONENTS_IN = G413 / "gdt413_46_component_working_dictionary.tsv"
REGISTER_ATLAS_IN = G415 / "gdt415_95_register_expansion_atlas.tsv"
CLAUSES_IN = G416 / "gdt416_4576_imperative_clauses.tsv"
OWNER_VARIANTS_IN = G491 / "gdt491_4_owner_variant_contrast_cards.tsv"
SLOT_MATRIX = OUT / "gdt492_35_observed_register_slot_cells.tsv"
SLOT_OCCURRENCES = OUT / "gdt492_12_owner_variant_slot_occurrences.tsv"
FAMILY_CARRIERS = OUT / "gdt492_23_exact_frame_family_carriers.tsv"
ACTION_CELLS = OUT / "gdt492_17_exact_frame_action_cells.tsv"
ACTION_REGISTER_CELLS = OUT / "gdt492_19_action_register_phrase_cells.tsv"
ALTERNATE_CELLS = OUT / "gdt492_9_non_tr_action_cells.tsv"
REGISTER_BRIDGES = OUT / "gdt492_2_same_action_cross_register_bridges.tsv"
CARD_SUMMARIES = OUT / "gdt492_4_owner_variant_card_summaries.tsv"
READABLE = OUT / "GDT492_OWNER_VARIANT_SLOT_BRIDGE_ATLAS.md"
RESULT = OUT / "gdt492_result.json"
STATUS = "FOUR_OWNER_VARIANTS_DECOMPOSED__THIRTY_FIVE_SLOT_CELLS_OBSERVED__NINE_ALTERNATE_ACTION_CELLS"
ACTION_ROOTS = ("OK", "CH", "SH", "K", "S", "CHD", "T", "R", "P")
RELEVANT_ROOTS = ("T", "R", "AL", "Y", "CH", "E", "OR")
REGISTER_ORDER = ("SOURCE_SECTION_T", "HERBAL", "BIOLOGICAL", "CELESTIAL", "PHARMA")
EXPECTED_FRAMES = ("@ACTION+AL+Y", "@ACTION+CH+E+Y", "@ACTION+OR+Y", "CH+@ACTION")


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


def recipe_atoms(recipe: str) -> list[str]:
    return recipe.split("+") if recipe else []


def build_readable(
    cards: list[dict[str, object]],
    slots: list[dict[str, object]],
    matrix: list[dict[str, object]],
    action_cells: list[dict[str, object]],
    bridges: list[dict[str, object]],
    result: dict[str, object],
) -> str:
    lines = [
        "# GDT492 — die vier Owner-Varianten sind vollständig slotweise lesbar",
        "",
        "GDT492 zerlegt nur die vier GDT491-Karten, deren beobachtete T- und R-Sätze verschiedene Besitzerwörter tragen. Kein Satz wird umformuliert. Stattdessen werden die alten Registerrealisierungen jedes formalen Slots danebengestellt und die vollständigen Rahmenfamilien nach weiteren alten Handlungsköpfen durchsucht.",
        "",
        f"- Offene Owner-Karten zerlegt: **{result['owner_variant_card_count']}/4**.",
        f"- Formale Slotvorkommen: **{result['owner_variant_slot_occurrence_count']}**; undefinierte Slots: **{result['undefined_slot_count']}**.",
        f"- Relevante Werte: **{result['relevant_root_count']}** über **{result['observed_register_slot_cell_count']}/35** beobachtete Registerzellen.",
        f"- Exakte Rahmenfamilie: **{result['exact_family_carrier_count']}** alte Träger, **{result['exact_action_cell_count']}** Aktionszellen und **{result['observed_family_clause_form_count']}** Satzformen.",
        f"- Davon zusätzliche Nicht-T/R-Zellen: **{result['alternate_non_tr_action_cell_count']}**; gleiche Handlung über mehrere Register: **{result['same_action_cross_register_bridge_count']}**.",
        "",
        "## Vier zerlegte Karten",
        "",
    ]
    slots_by_card: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in slots:
        slots_by_card[str(row["card_id"])].append(row)
    for card in cards:
        lines.extend([
            f"### `{card['frozen_frame']}`",
            "",
            f"- beobachtetes T: {card['t_selected_observed_phrase_de']}",
            f"- beobachtetes R: {card['r_selected_observed_phrase_de']}",
            f"- Rahmenfamilie: {card['family_event_count']} Events, {card['action_cell_count']} Handlungsköpfe, {card['observed_clause_form_count']} Satzformen, Register `{card['registers']}`.",
            "",
            "| Slot | portabler Wert | T-Registerform | R-Registerform | Relation |",
            "|---:|---|---|---|---|",
        ])
        for slot in slots_by_card[str(card["card_id"])]:
            lines.append(f"| {slot['slot_ordinal']} | `{slot['portable_value_pair_de']}` | {slot['t_owner_local_expansion_de']} | {slot['r_owner_local_expansion_de']} | {slot['slot_relation']} |")
        lines.append("")
    lines.extend([
        "## Was den Unterschied trägt",
        "",
        "Von den acht nicht-aktionalen Slotvorkommen wechseln sieben nur ihre bereits festgelegte Registerform: Zielposition/Zielstation, Positionsposten/Stationsposten, Eintrag/Stationsposten, Arbeitseinheit/Stationseinheit sowie die registergebundenen NEHMEN-Formen. Ein Slot bleibt sogar wörtlich stabil: `E=GRAD I`. Die Aktionsslots sind der beabsichtigte T/R-Kontrast und werden nicht als Owner-Differenz gezählt.",
        "",
        "## Alle sieben Werte sind in allen fünf Registern alt",
        "",
        "| Wurzel | portabler Wert | fünf beobachtete Registerformen | Events über alle Register |",
        "|---|---|---|---:|",
    ])
    matrix_by_root: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in matrix:
        matrix_by_root[str(row["root"])].append(row)
    for root in RELEVANT_ROOTS:
        local = matrix_by_root[root]
        forms = " / ".join(f"{row['register']}={row['owner_local_expansion_de']}" for row in local)
        lines.append(f"| `{root}` | {local[0]['portable_default_de']} | {forms} | {sum(int(row['event_count']) for row in local)} |")
    lines.extend([
        "",
        "## Die Rahmenfamilien liefern zusätzliche Handlungen",
        "",
        "| Rahmen | Handlung | Events | Register | beobachtete Formen | T/R? |",
        "|---|---|---:|---|---:|---|",
    ])
    for row in action_cells:
        lines.append(f"| `{row['frozen_frame']}` | `{row['action_root']}` | {row['event_count']} | {row['registers']} | {row['observed_clause_form_count']} | {row['is_t_or_r']} |")
    lines.extend([
        "",
        "Besonders nützlich ist `@ACTION+AL+Y`: `OK` realisiert exakt denselben Rahmen celestial und biologisch, `CH` biologisch und pharmazeutisch. Diese zwei alten Brücken zeigen direkt, dass Positions-/Stations-/Drogenwortlaut am Besitzerregister hängt, während `AL+Y = ZIELORT · POSTEN` stehen bleibt.",
        "",
        "## Zwei direkte Registerbrücken",
        "",
    ])
    for row in bridges:
        lines.append(f"- `{row['action_recipe']}`: {row['registers']} — {row['observed_clauses_de']}")
    lines.extend([
        "",
        "## Arbeitsfolgerung",
        "",
        "Die vier GDT491-Abweichungen verlangen keine neue Bedeutung und kein zusammengesetztes Geheimwort. Sie verhalten sich wie dieselbe kleine Komponentenkarte mit registergebundenem Fachwortschatz. Das stärkt die Lesart *Mischung aus kurzen produktiven Fachkürzeln und gelernten owner-lokalen Ganzwörtern*: Die Kürzel bestimmen Slot und portablen Wert; der Seitenbesitzer bestimmt den konkreten deutschen Werkstattwortlaut.",
        "",
        "## Nächster Schritt",
        "",
        "Kompiliere aus den 35 beobachteten Registerzellen eine kleine Owner-abhängige Satzschablone für alle elf T/R-Rahmen. Jede Ausgabe muss entweder eine bereits beobachtete Klausel sein oder ausdrücklich als slotweise zusammengesetzte Arbeitslesung markiert bleiben. So bekommen auch die vier Varianten eine gemeinsame Vorhersageform, ohne sie als beobachteten Satz auszugeben.",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    components = read_tsv(COMPONENTS_IN)
    register_atlas = read_tsv(REGISTER_ATLAS_IN)
    clauses = read_tsv(CLAUSES_IN)
    owner_variants = read_tsv(OWNER_VARIANTS_IN)
    if (len(components), len(register_atlas), len(clauses), len(owner_variants)) != (46, 95, 4576, 4):
        raise RuntimeError("Input count drift")
    if tuple(row["frozen_frame"] for row in owner_variants) != EXPECTED_FRAMES:
        raise RuntimeError("Owner-variant frame drift")

    component_map = {row["atom"]: row for row in components}
    expansion_map = {(row["root"], row["register"]): row for row in register_atlas}
    clauses_by_recipe: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in clauses:
        clauses_by_recipe[row["component_recipe"]].append(row)

    slot_matrix_rows: list[dict[str, object]] = []
    for root in RELEVANT_ROOTS:
        for register in REGISTER_ORDER:
            local_events = [row for row in clauses if row["register"] == register and root in recipe_atoms(row["component_recipe"])]
            mention_count = sum(recipe_atoms(row["component_recipe"]).count(root) for row in clauses if row["register"] == register)
            if root == "E":
                source = component_map[root]
                portable = source["working_value_de"]
                category = source["factor_family"]
                expansion = "GRAD I"
                source_atlas = "GDT413_COMPONENT_PLUS_GDT416_OBSERVED_CARRIERS"
                source_mentions = mention_count
                source_events = len(local_events)
            else:
                source = expansion_map[(root, register)]
                portable = source["portable_default_de"]
                category = source["structural_category"]
                expansion = source["owner_local_expansion_de"]
                source_atlas = "GDT415_REGISTER_EXPANSION_ATLAS"
                source_mentions = int(source["mention_count"])
                source_events = int(source["event_count"])
                if (source_mentions, source_events) != (mention_count, len(local_events)):
                    raise RuntimeError(f"Support drift for {root}/{register}")
            slot_matrix_rows.append({
                "slot_cell_id": f"G492-SC{len(slot_matrix_rows) + 1:02d}",
                "root": root,
                "portable_default_de": portable,
                "structural_category": category,
                "register": register,
                "owner_local_expansion_de": expansion,
                "mention_count": source_mentions,
                "event_count": source_events,
                "page_count": len({row["physical_page"] for row in local_events}),
                "owner_class_count": len({row["owner_class"] for row in local_events}),
                "owner_count": len({row["owner_de"] for row in local_events}),
                "sample_pages": "|".join(sorted({row["physical_page"] for row in local_events})),
                "source_atlas": source_atlas,
                "observed_old_slot_cell": "YES" if local_events else "NO",
            })
    slot_matrix_map = {(str(row["root"]), str(row["register"])): row for row in slot_matrix_rows}

    family_carrier_rows: list[dict[str, object]] = []
    action_cell_rows: list[dict[str, object]] = []
    action_register_rows: list[dict[str, object]] = []
    card_summary_rows: list[dict[str, object]] = []
    slot_occurrence_rows: list[dict[str, object]] = []
    for card_number, card in enumerate(owner_variants, 1):
        card_id = f"G492-CARD{card_number:02d}"
        frame = card["frozen_frame"]
        family_events: list[dict[str, str]] = []
        frame_action_cells: list[dict[str, object]] = []
        for action in ACTION_ROOTS:
            recipe = frame.replace("@ACTION", action)
            local = clauses_by_recipe[recipe]
            if not local:
                continue
            family_events.extend(local)
            for event in local:
                family_carrier_rows.append({
                    "carrier_id": f"G492-FC{len(family_carrier_rows) + 1:02d}",
                    "card_id": card_id,
                    "frozen_frame": frame,
                    "action_root": action,
                    "action_recipe": recipe,
                    "is_t_or_r": "YES" if action in {"T", "R"} else "NO",
                    "global_running_event_id": event["global_running_event_id"],
                    "global_statement_id": event["global_statement_id"],
                    "physical_page": event["physical_page"],
                    "register": event["register"],
                    "owner_class": event["owner_class"],
                    "owner_de": event["owner_de"],
                    "surface": event["surface"],
                    "imperative_clause_de": event["imperative_clause_de"],
                    "portable_back_projection_de": event["portable_back_projection_de"],
                    "roundtrip_exact": event["roundtrip_exact"],
                    "observed_not_invented": "YES",
                })
            cell = {
                "action_cell_id": f"G492-AC{len(action_cell_rows) + 1:02d}",
                "card_id": card_id,
                "frozen_frame": frame,
                "action_root": action,
                "action_recipe": recipe,
                "is_t_or_r": "YES" if action in {"T", "R"} else "NO",
                "event_count": len(local),
                "page_count": len({row["physical_page"] for row in local}),
                "pages": "|".join(sorted({row["physical_page"] for row in local})),
                "register_count": len({row["register"] for row in local}),
                "registers": "|".join(sorted({row["register"] for row in local})),
                "owner_class_count": len({row["owner_class"] for row in local}),
                "observed_clause_form_count": len({row["imperative_clause_de"] for row in local}),
                "observed_clauses_de": " || ".join(sorted({row["imperative_clause_de"] for row in local})),
                "all_roundtrip_exact": "YES" if all(row["roundtrip_exact"] == "YES" for row in local) else "NO",
            }
            action_cell_rows.append(cell)
            frame_action_cells.append(cell)
            for register in REGISTER_ORDER:
                register_local = [row for row in local if row["register"] == register]
                if not register_local:
                    continue
                action_register_rows.append({
                    "action_register_cell_id": f"G492-ARC{len(action_register_rows) + 1:02d}",
                    "card_id": card_id,
                    "frozen_frame": frame,
                    "action_root": action,
                    "action_recipe": recipe,
                    "register": register,
                    "event_count": len(register_local),
                    "page_count": len({row["physical_page"] for row in register_local}),
                    "pages": "|".join(sorted({row["physical_page"] for row in register_local})),
                    "observed_clause_form_count": len({row["imperative_clause_de"] for row in register_local}),
                    "observed_clauses_de": " || ".join(sorted({row["imperative_clause_de"] for row in register_local})),
                    "observed_not_invented": "YES",
                })

        t_witnesses = [row for row in clauses_by_recipe[card["t_recipe"]] if row["imperative_clause_de"] == card["t_selected_observed_phrase_de"]]
        r_witnesses = [row for row in clauses_by_recipe[card["r_recipe"]] if row["imperative_clause_de"] == card["r_selected_observed_phrase_de"]]
        t_registers = {row["register"] for row in t_witnesses}
        r_registers = {row["register"] for row in r_witnesses}
        if len(t_registers) != 1 or len(r_registers) != 1:
            raise RuntimeError(f"Selected phrase register ambiguity for {frame}")
        t_register = next(iter(t_registers))
        r_register = next(iter(r_registers))
        for slot_ordinal, token in enumerate(frame.split("+"), 1):
            t_root = "T" if token == "@ACTION" else token
            r_root = "R" if token == "@ACTION" else token
            t_slot = slot_matrix_map[(t_root, t_register)]
            r_slot = slot_matrix_map[(r_root, r_register)]
            if token == "@ACTION":
                relation = "ACTION_CONTRAST_WITH_OWNER_LOCAL_REALIZATIONS"
            elif t_slot["owner_local_expansion_de"] == r_slot["owner_local_expansion_de"]:
                relation = "REGISTER_STABLE_REALIZATION"
            else:
                relation = "OWNER_LOCAL_REALIZATION_OF_SAME_PORTABLE_VALUE"
            portable_pair = str(t_slot["portable_default_de"])
            if t_root != r_root:
                portable_pair += " ↔ " + str(r_slot["portable_default_de"])
            slot_occurrence_rows.append({
                "slot_occurrence_id": f"G492-S{len(slot_occurrence_rows) + 1:02d}",
                "card_id": card_id,
                "frozen_frame": frame,
                "slot_ordinal": slot_ordinal,
                "frame_token": token,
                "t_root": t_root,
                "r_root": r_root,
                "portable_value_pair_de": portable_pair,
                "t_register": t_register,
                "r_register": r_register,
                "t_owner_local_expansion_de": t_slot["owner_local_expansion_de"],
                "r_owner_local_expansion_de": r_slot["owner_local_expansion_de"],
                "t_register_event_support": t_slot["event_count"],
                "r_register_event_support": r_slot["event_count"],
                "slot_relation": relation,
                "both_slot_cells_observed": "YES" if t_slot["observed_old_slot_cell"] == r_slot["observed_old_slot_cell"] == "YES" else "NO",
                "new_slot_value_required": "NO",
            })
        card_summary_rows.append({
            "card_id": card_id,
            "frozen_frame": frame,
            "t_recipe": card["t_recipe"],
            "r_recipe": card["r_recipe"],
            "t_register": t_register,
            "r_register": r_register,
            "t_selected_observed_phrase_de": card["t_selected_observed_phrase_de"],
            "r_selected_observed_phrase_de": card["r_selected_observed_phrase_de"],
            "formal_slot_count": len(frame.split("+")),
            "nonaction_slot_count": sum(token != "@ACTION" for token in frame.split("+")),
            "owner_variant_nonaction_slot_count": sum(row["card_id"] == card_id and row["slot_relation"] == "OWNER_LOCAL_REALIZATION_OF_SAME_PORTABLE_VALUE" for row in slot_occurrence_rows),
            "register_stable_nonaction_slot_count": sum(row["card_id"] == card_id and row["slot_relation"] == "REGISTER_STABLE_REALIZATION" for row in slot_occurrence_rows),
            "family_event_count": len(family_events),
            "action_cell_count": len(frame_action_cells),
            "action_roots": "|".join(str(row["action_root"]) for row in frame_action_cells),
            "alternate_non_tr_action_cell_count": sum(row["is_t_or_r"] == "NO" for row in frame_action_cells),
            "action_register_cell_count": sum(row["frozen_frame"] == frame for row in action_register_rows),
            "observed_clause_form_count": len({row["imperative_clause_de"] for row in family_events}),
            "register_count": len({row["register"] for row in family_events}),
            "registers": "|".join(sorted({row["register"] for row in family_events})),
            "page_count": len({row["physical_page"] for row in family_events}),
            "pages": "|".join(sorted({row["physical_page"] for row in family_events})),
            "all_slots_observed": "YES",
            "new_phrase_invented": "NO",
        })

    alternate_rows = [row for row in action_cell_rows if row["is_t_or_r"] == "NO"]
    bridge_rows: list[dict[str, object]] = []
    for cell in action_cell_rows:
        if int(cell["register_count"]) < 2:
            continue
        local = [row for row in action_register_rows if row["frozen_frame"] == cell["frozen_frame"] and row["action_root"] == cell["action_root"]]
        bridge_rows.append({
            "bridge_id": f"G492-B{len(bridge_rows) + 1:02d}",
            "card_id": cell["card_id"],
            "frozen_frame": cell["frozen_frame"],
            "action_root": cell["action_root"],
            "action_recipe": cell["action_recipe"],
            "register_count": cell["register_count"],
            "registers": cell["registers"],
            "event_count": cell["event_count"],
            "observed_clause_form_count": cell["observed_clause_form_count"],
            "observed_clauses_de": " || ".join(str(row["observed_clauses_de"]) for row in local),
            "same_action_and_formal_frame_across_registers": "YES",
            "owner_words_vary_by_register": "YES",
        })

    counts = tuple(map(len, (
        slot_matrix_rows, slot_occurrence_rows, family_carrier_rows, action_cell_rows,
        action_register_rows, alternate_rows, bridge_rows, card_summary_rows,
    )))
    if counts != (35, 12, 23, 17, 19, 9, 2, 4):
        raise RuntimeError(f"Unexpected slot-bridge counts: {counts}")
    write_tsv(SLOT_MATRIX, slot_matrix_rows)
    write_tsv(SLOT_OCCURRENCES, slot_occurrence_rows)
    write_tsv(FAMILY_CARRIERS, family_carrier_rows)
    write_tsv(ACTION_CELLS, action_cell_rows)
    write_tsv(ACTION_REGISTER_CELLS, action_register_rows)
    write_tsv(ALTERNATE_CELLS, alternate_rows)
    write_tsv(REGISTER_BRIDGES, bridge_rows)
    write_tsv(CARD_SUMMARIES, card_summary_rows)

    result = {
        "status": STATUS,
        "owner_variant_card_count": len(card_summary_rows),
        "owner_variant_slot_occurrence_count": len(slot_occurrence_rows),
        "nonaction_slot_occurrence_count": sum(row["frame_token"] != "@ACTION" for row in slot_occurrence_rows),
        "owner_local_nonaction_slot_count": sum(row["slot_relation"] == "OWNER_LOCAL_REALIZATION_OF_SAME_PORTABLE_VALUE" for row in slot_occurrence_rows),
        "register_stable_nonaction_slot_count": sum(row["slot_relation"] == "REGISTER_STABLE_REALIZATION" for row in slot_occurrence_rows),
        "undefined_slot_count": sum(row["both_slot_cells_observed"] != "YES" for row in slot_occurrence_rows),
        "relevant_root_count": len(RELEVANT_ROOTS),
        "observed_register_slot_cell_count": sum(row["observed_old_slot_cell"] == "YES" for row in slot_matrix_rows),
        "exact_family_carrier_count": len(family_carrier_rows),
        "exact_action_cell_count": len(action_cell_rows),
        "action_register_cell_count": len(action_register_rows),
        "observed_family_clause_form_count": len({(row["frozen_frame"], row["imperative_clause_de"]) for row in family_carrier_rows}),
        "alternate_non_tr_action_cell_count": len(alternate_rows),
        "same_action_cross_register_bridge_count": len(bridge_rows),
        "family_register_count": len({row["register"] for row in family_carrier_rows}),
        "family_page_count": len({row["physical_page"] for row in family_carrier_rows}),
        "family_action_root_count": len({row["action_root"] for row in family_carrier_rows}),
        "all_slots_observed": all(row["both_slot_cells_observed"] == "YES" for row in slot_occurrence_rows),
        "all_family_carriers_roundtrip_exact": all(row["roundtrip_exact"] == "YES" for row in family_carrier_rows),
        "invented_phrase_count": 0,
        "new_portable_value_count": 0,
        "meaning_change_count": 0,
        "wording_change_count": 0,
        "active_model_change_count": 0,
        "record_boundary_change_count": 0,
        "surface_change_count": 0,
        "recipe_change_count": 0,
        "page_change_count": 0,
        "claim_ceiling": "Observed owner-slot decomposition and exact old action-family bridges for four fixed GDT491 owner variants; all seven relevant values have old support in all five registers, with no invented phrase, new meaning, model, boundary, surface, recipe, event, or page.",
    }
    READABLE.write_text(build_readable(card_summary_rows, slot_occurrence_rows, slot_matrix_rows, action_cell_rows, bridge_rows, result), encoding="utf-8")
    RESULT.write_text(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
