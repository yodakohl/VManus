#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P463 = ROOT / "experiments/yolo/sidequest_semantic_ten_page_common_roots_four_hundred_sixty_third"
P471 = ROOT / "experiments/yolo/sidequest_semantic_compact_renderer_habits_four_hundred_seventy_first"
P473 = ROOT / "experiments/yolo/sidequest_semantic_silent_owner_dictionary_four_hundred_seventy_third"
P477 = ROOT / "experiments/yolo/sidequest_semantic_sentence_templates_four_hundred_seventy_seventh"
P478 = ROOT / "experiments/yolo/sidequest_semantic_whole_card_slots_four_hundred_seventy_eighth"
P481 = ROOT / "experiments/yolo/sidequest_semantic_direction_triad_four_hundred_eighty_first"
P483 = ROOT / "experiments/yolo/sidequest_semantic_form_classes_four_hundred_eighty_third"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(name)
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def add_inventory(rows: list[dict[str, object]], layer: str, item_id: str, value: str,
                  scope: str, support: str, source: str) -> None:
    rows.append({
        "manual_order": len(rows) + 1,
        "layer": layer,
        "item_id": item_id,
        "teaching_value_or_rule_de": value,
        "scope": scope,
        "support_or_instances": support,
        "source_artifact": source,
    })


def main() -> None:
    components = read(P463 / "FOUR_HUNDRED_SIXTY_THIRD_35_COMPONENT_COMMON_ROOT_MANUAL.tsv")
    owners = read(P473 / "FOUR_HUNDRED_SEVENTY_THIRD_OWNER_CLASS_DICTIONARY.tsv")
    motifs = read(P477 / "FOUR_HUNDRED_SEVENTY_SEVENTH_NINE_SENTENCE_TEMPLATES.tsv")
    motif_statements = {row["statement_id"]: row for row in read(P477 / "FOUR_HUNDRED_SEVENTY_SEVENTH_116_TEMPLATE_SENTENCES.tsv")}
    forms = read(P483 / "FOUR_HUNDRED_EIGHTY_THIRD_SEVEN_RECURRENT_FORM_CLASSES.tsv")
    assignments = read(P483 / "FOUR_HUNDRED_EIGHTY_THIRD_116_FORM_CLASS_ASSIGNMENTS.tsv")
    local_forms = read(P483 / "FOUR_HUNDRED_EIGHTY_THIRD_65_LOCAL_FORMS.tsv")
    whole_decisions = read(P478 / "FOUR_HUNDRED_SEVENTY_EIGHTH_SIX_WHOLE_CARD_SLOT_DECISIONS.tsv")
    dictionary = read(P481 / "FOUR_HUNDRED_EIGHTY_FIRST_173_DIRECTION_REVISED_DICTIONARY.tsv")
    events = read(P481 / "FOUR_HUNDRED_EIGHTY_FIRST_381_DIRECTION_REVISED_PROSE_EVENTS.tsv")
    astro = read(P481 / "FOUR_HUNDRED_EIGHTY_FIRST_395_DIRECTION_REVISED_ASTRO_GROUPS.tsv")
    renderer = read(P471 / "FOUR_HUNDRED_SEVENTY_FIRST_776_COMPACT_RENDERER_PREDICTIONS.tsv")
    habits = read(P471 / "FOUR_HUNDRED_SEVENTY_FIRST_NINE_RENDERER_HABITS.tsv")
    exceptions = read(P471 / "FOUR_HUNDRED_SEVENTY_FIRST_113_EXEMPLAR_RENDERER_EXCEPTIONS.tsv")

    current_dictionary = {row["joint_tuple_id"]: row for row in dictionary}
    whole_ids = {row["joint_tuple_id"] for row in whole_decisions}
    statement_map = {row["statement_id"]: row for row in assignments}
    renderer_map = {(row["domain"], row["item_id"]): row for row in renderer}

    inventory: list[dict[str, object]] = []
    for row in components:
        add_inventory(inventory, "L1_SHARED_COMPONENT", row["component"],
                      f"{row['role']}: {row['value_de']}", row["register_scope"],
                      row["combined_support_cards"], "PASS463_COMPONENT_MANUAL")
    for row in owners:
        add_inventory(inventory, "L2_OWNER_CLASS", row["owner_class"],
                      row["teaching_rule_de"], row["scope"], row["instances"],
                      "PASS473_OWNER_DICTIONARY")
    for row in motifs:
        add_inventory(inventory, "L3_SHARED_SENTENCE_MOTIF", row["template_id"],
                      row["teaching_sentence_de"], "HERBAL_AND_BIOLOGICAL",
                      row["total_occurrences"], "PASS477_SENTENCE_TEMPLATES")
    for row in forms:
        add_inventory(inventory, "L4_BIO_FORM_CARD", row["form_class_id"],
                      row["apprentice_rule_de"], "BIOLOGICAL",
                      row["statements"], "PASS483_RECURRENT_FORMS")
    for row in whole_decisions:
        current = current_dictionary[row["joint_tuple_id"]]
        add_inventory(inventory, "L5_LEARNED_WHOLE_CARD", row["card_no"],
                      current["pass481_value_de"], current["registers"],
                      current["events"], "PASS478_WHOLE_CARD_DECK_CURRENT_VALUE")
    for row in local_forms:
        add_inventory(inventory, "L6_LOCAL_STATEMENT_FORM", row["statement_id"],
                      row["complete_expansion_de"], row["register"], "1",
                      "PASS483_LOCAL_FORMS")
    add_inventory(inventory, "L7_ASTRO_READING_RULE", "ASTRO_LOCATE_READ_RECORD",
                  "Sichtbaren Ort wählen; dortige Kartenfolge lesen; lokalen Wert eintragen; am nächsten Locus neu beginnen.",
                  "ASTRO", "142 loci / 395 groups", "PASS473_OWNERED_ASTRO_LOCI")
    for row in habits:
        add_inventory(inventory, "L8_RENDERER_HABIT", f"RH{row['habit_no']}",
                      row["teaching_habit_de"], row["domain"], row["support_items"],
                      "PASS471_RENDERER_HABITS")
    for row in exceptions:
        add_inventory(inventory, "L9_SURFACE_EXEMPLAR", f"SX{row['exception_no']}",
                      f"{row['compact_predicted_surface']} → {row['exemplar_surface']}",
                      row["domain"], "1", "PASS471_RENDERER_EXCEPTIONS")
    write("FOUR_HUNDRED_EIGHTY_FOURTH_283_ITEM_HIERARCHICAL_MANUAL.tsv", inventory)

    ledger = []
    route_counts = Counter()
    for row in events:
        statement = statement_map[row["statement_id"]]
        motif = motif_statements[row["statement_id"]]
        if statement["form_status"] == "RECURRENT_APPRENTICE_FORM":
            semantic_layer = "BIO_FORM_CARD"
            syntax_item = statement["form_class_id"]
        elif motif["templates_used"] != "NONE":
            semantic_layer = "SHARED_MOTIF_PLUS_LOCAL_FILL"
            syntax_item = motif["templates_used"]
        else:
            semantic_layer = "LOCAL_STATEMENT_FORM"
            syntax_item = row["statement_id"]
        if row["joint_tuple_id"] in whole_ids:
            semantic_layer += "+LEARNED_WHOLE_CARD"
        render = renderer_map[("PROSE", row["event_id"])]
        surface_layer = "DEFAULT_OR_HABIT" if render["exact_without_exemplar"] == "YES" else "LOCAL_SURFACE_EXEMPLAR"
        route_counts[(semantic_layer, surface_layer)] += 1
        ledger.append({
            "writer_order": len(ledger) + 1,
            "domain": "PROSE",
            "item_id": row["event_id"],
            "unit_id": row["record_unit_id"],
            "page": row["page"],
            "locus": row["locus"],
            "statement_or_locus": row["statement_id"],
            "owner_or_namespace": row["owner_code"],
            "semantic_layer": semantic_layer,
            "syntax_item": syntax_item,
            "component_parse": row["component_parse"],
            "concrete_reading_de": row["pass481_event_de"],
            "surface_layer": surface_layer,
            "renderer_habit": render["habit_applied"],
            "predicted_surface": render["predicted_surface"],
            "observed_surface": render["observed_surface"],
            "surface_exact_without_exemplar": render["exact_without_exemplar"],
        })
    for row in astro:
        item_id = f"A:{int(row['group_serial']):03d}"
        render = renderer_map[("ASTRO", item_id)]
        surface_layer = "DEFAULT_OR_HABIT" if render["exact_without_exemplar"] == "YES" else "LOCAL_SURFACE_EXEMPLAR"
        route_counts[("ASTRO_LOCATE_READ_RECORD", surface_layer)] += 1
        ledger.append({
            "writer_order": len(ledger) + 1,
            "domain": "ASTRO",
            "item_id": item_id,
            "unit_id": row["diagram_id"],
            "page": row["page"],
            "locus": row["locus"],
            "statement_or_locus": row["locus"],
            "owner_or_namespace": row["visible_owner"],
            "semantic_layer": "ASTRO_LOCATE_READ_RECORD",
            "syntax_item": row["local_namespace"],
            "component_parse": row["selected_component_parse"],
            "concrete_reading_de": row["pass481_celestial_reading_de"],
            "surface_layer": surface_layer,
            "renderer_habit": render["habit_applied"],
            "predicted_surface": render["predicted_surface"],
            "observed_surface": render["observed_surface"],
            "surface_exact_without_exemplar": render["exact_without_exemplar"],
        })
    write("FOUR_HUNDRED_EIGHTY_FOURTH_776_FORWARD_RECONSTRUCTION.tsv", ledger)

    route_rows = []
    for (semantic, surface), count in sorted(route_counts.items()):
        route_rows.append({"semantic_route": semantic, "surface_route": surface, "groups": count,
                           "share_of_776": f"{count / 776:.4f}"})
    write("FOUR_HUNDRED_EIGHTY_FOURTH_RECONSTRUCTION_ROUTES.tsv", route_rows)

    layer_counts = Counter(row["layer"] for row in inventory)
    layer_rows = []
    for layer in ("L1_SHARED_COMPONENT", "L2_OWNER_CLASS", "L3_SHARED_SENTENCE_MOTIF",
                  "L4_BIO_FORM_CARD", "L5_LEARNED_WHOLE_CARD", "L6_LOCAL_STATEMENT_FORM",
                  "L7_ASTRO_READING_RULE", "L8_RENDERER_HABIT", "L9_SURFACE_EXEMPLAR"):
        layer_rows.append({"layer": layer, "items": layer_counts[layer],
                           "kind": "SEMANTIC_OR_SYNTAX" if layer < "L8" else "GRAPHIC_RENDERER",
                           "cumulative_items": sum(layer_counts[x] for x in layer_counts if x <= layer)})
    write("FOUR_HUNDRED_EIGHTY_FOURTH_MANUAL_LAYER_COUNTS.tsv", layer_rows)

    statement_events = Counter()
    statement_routes = {}
    for row in ledger[:381]:
        statement_events[row["statement_or_locus"]] += 1
        statement_routes[row["statement_or_locus"]] = row["semantic_layer"].split("+")[0]
    units = []
    for unit in [f"H{n}" for n in range(1, 6)] + [f"B{n}" for n in range(1, 7)]:
        rows = [row for row in assignments if row["record_unit_id"] == unit]
        counts = Counter(statement_routes[row["statement_id"]] for row in rows)
        units.append({
            "unit_order": len(units) + 1,
            "unit_id": unit,
            "page": rows[0]["page"],
            "domain": rows[0]["register"],
            "statements_or_loci": len(rows),
            "groups": sum(int(row["events"]) for row in rows),
            "manual_route_counts": ";".join(f"{key}={value}" for key, value in sorted(counts.items())),
            "continuous_edition_de": " ".join(row["complete_expansion_de"] for row in rows),
        })
    locus_groups: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in astro:
        locus_groups[(row["diagram_id"], row["page"], row["locus"])].append(row)
    for unit in ("A1", "A2", "A3"):
        loci = [(key, rows) for key, rows in locus_groups.items() if key[0] == unit]
        units.append({
            "unit_order": len(units) + 1,
            "unit_id": unit,
            "page": loci[0][0][1],
            "domain": "ASTRO",
            "statements_or_loci": len(loci),
            "groups": sum(len(rows) for _, rows in loci),
            "manual_route_counts": f"ASTRO_LOCATE_READ_RECORD={len(loci)}",
            "continuous_edition_de": " ".join("Bei " + key[2] + ": " + "; ".join(row["pass481_celestial_reading_de"] for row in rows) + "." for key, rows in loci),
        })
    write("FOUR_HUNDRED_EIGHTY_FOURTH_14_HIERARCHICAL_UNIT_EDITIONS.tsv", units)

    report_lines = ["# Hierarchical workshop manual — ten-page edition", "",
                    "The manual is read from top to bottom: component, visible owner, sentence motif or Bio form, local fill where needed, then renderer.", ""]
    for row in units:
        report_lines.extend([f"## {row['unit_id']} — {row['page']}", "", row["continuous_edition_de"], ""])
    (HERE / "FOUR_HUNDRED_EIGHTY_FOURTH_HIERARCHICAL_TEN_PAGE_EDITION.md").write_text("\n".join(report_lines), encoding="utf-8")

    summary = {
        "status": "PASS",
        "manual_items": len(inventory),
        "semantic_or_syntax_items": sum(row["kind"] == "SEMANTIC_OR_SYNTAX" for row in layer_rows for _ in range(int(row["items"]))),
        "renderer_items": len(habits) + len(exceptions),
        "components": len(components),
        "owners": len(owners),
        "motifs": len(motifs),
        "bio_forms": len(forms),
        "whole_cards": len(whole_decisions),
        "local_forms": len(local_forms),
        "astro_rules": 1,
        "renderer_habits": len(habits),
        "renderer_exceptions": len(exceptions),
        "groups": len(ledger),
        "surface_exact_without_exemplar": sum(row["surface_exact_without_exemplar"] == "YES" for row in ledger),
        "surface_exemplar_groups": sum(row["surface_exact_without_exemplar"] == "NO" for row in ledger),
        "units": len(units),
    }
    (HERE / "FOUR_HUNDRED_EIGHTY_FOURTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
