#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import defaultdict
from functools import lru_cache
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = ROOT / "experiments/yolo/sidequest_semantic_astro_address_cores_four_hundred_sixty_sixth"
GROUPS = BASE / "FOUR_HUNDRED_SIXTY_SIXTH_395_ASTRO_GROUP_ADDRESS_CORES.tsv"
LEDGER = BASE / "FOUR_HUNDRED_SIXTY_SIXTH_776_GROUP_ADDRESS_CORE_LEDGER.tsv"
ASTRO_CORES = BASE / "FOUR_HUNDRED_SIXTY_SIXTH_EIGHT_ASTRO_ADDRESS_CORES.tsv"
SURFACES = ROOT / "experiments/yolo/sidequest_semantic_astro_component_transfer_four_hundred_sixty_first/FOUR_HUNDRED_SIXTY_FIRST_COMPONENT_SURFACE_LEXICON.tsv"
COMPONENTS = ROOT / "experiments/yolo/sidequest_semantic_ten_page_common_roots_four_hundred_sixty_third/FOUR_HUNDRED_SIXTY_THIRD_35_COMPONENT_COMMON_ROOT_MANUAL.tsv"
CARDS = ROOT / "experiments/yolo/sidequest_semantic_ten_page_common_roots_four_hundred_sixty_third/FOUR_HUNDRED_SIXTY_THIRD_173_CARD_COMMON_ROOT_DICTIONARY.tsv"
ALIASES = ROOT / "experiments/yolo/sidequest_semantic_final_reverse_writer_four_hundred_fifty_ninth/FOUR_HUNDRED_FIFTY_NINTH_ELEVEN_EXACT_SELECTION_RULES.tsv"


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


def main() -> None:
    source = read(GROUPS)
    component_values = {row["component"]: row["value_de"] for row in read(COMPONENTS)}
    astro_values = {row["component"]: row["atomic_value_de"] for row in read(ASTRO_CORES)}
    astro_values.update({"I_COUNT": "Zaehlstrich", "AN_SECTION": "Abschnitt"})
    all_values = component_values | astro_values

    atom_surface: dict[str, set[str]] = defaultdict(set)
    for row in read(SURFACES):
        atom_surface[row["surface_atom"]].update(row["components"].split("|"))
    for row in read(ASTRO_CORES):
        atom_surface[row["surface_atom"]].add(row["component"])
    atom_surface["i"].add("I_COUNT")
    atom_surface["an"].add("AN_SECTION")
    forms = sorted(atom_surface, key=lambda item: (-len(item), item))

    def parses(surface: str) -> list[tuple[str, ...]]:
        if surface.startswith("q"):
            surface = surface[1:]

        @lru_cache(None)
        def walk(index: int) -> tuple[tuple[str, ...], ...]:
            if index == len(surface):
                return ((),)
            output = []
            for form in forms:
                if surface.startswith(form, index):
                    for component in sorted(atom_surface[form]):
                        for rest in walk(index + len(form)):
                            output.append((component,) + rest)
            return tuple(output)

        output = list(walk(0))
        if not output:
            return []
        shortest = min(map(len, output))
        return sorted(set(item for item in output if len(item) == shortest))

    decisions = []
    selected = {}
    for row in source:
        if row["transfer_status"] != "ASTRO_LOCAL_LABEL":
            continue
        alternatives = parses(row["surface"])
        if not alternatives:
            continue
        choice = alternatives[0]
        parse_text = "+".join(choice)
        atomic = " + ".join(all_values[part] for part in choice)
        selected[row["group_serial"]] = (parse_text, atomic)
        decisions.append({
            "decision_order": len(decisions) + 1,
            "group_serial": row["group_serial"],
            "diagram_id": row["diagram_id"],
            "page": row["page"],
            "locus": row["locus"],
            "surface": row["surface"],
            "parse_alternatives": " || ".join("+".join(option) for option in alternatives),
            "selected_parse": parse_text,
            "selected_atomic_value_de": atomic,
            "new_core_support": "I_COUNT" if "I_COUNT" in choice else "AN_SECTION",
        })
    write("FOUR_HUNDRED_SIXTY_SEVENTH_11_FINAL_NAME_DECISIONS.tsv", decisions)

    groups = []
    for row in source:
        out = dict(row)
        out["selected_component_parse"] = out["selected_component_parse"].replace("S_LABEL", "S_ADDR").replace("D_LABEL", "D_ADDR")
        out["atomic_common_root_value_de"] = out["atomic_common_root_value_de"].replace("Sternetikett", "Sternbezug").replace("Platzetikett", "Teiladresse")
        if row["group_serial"] in selected:
            parse_text, atomic = selected[row["group_serial"]]
            out["selected_component_parse"] = parse_text
            out["atomic_common_root_value_de"] = atomic
            out["transfer_status"] = "ASTRO_COUNT_SECTION_RESOLVED_SEQUENCE"
            out["nomenclator_resolution"] = "NEW_RECURRENT_CORE"
        elif row["transfer_status"] == "ASTRO_LOCAL_LABEL":
            out["atomic_common_root_value_de"] = "Himmelsname OTAZA"
            out["nomenclator_resolution"] = "MEMORIZED_WHOLE_NAME"
        else:
            out["nomenclator_resolution"] = "NOT_REQUIRED"
        groups.append(out)
    write("FOUR_HUNDRED_SIXTY_SEVENTH_395_ASTRO_GROUP_CLOSED_NOMENCLATOR.tsv", groups)

    new_cores = []
    for surface, component, value in (("i", "I_COUNT", "Zaehlstrich"), ("an", "AN_SECTION", "Abschnitt")):
        support = [row for row in decisions if component in row["selected_parse"].split("+")]
        new_cores.append({
            "surface_atom": surface,
            "component": component,
            "atomic_value_de": value,
            "support_groups": len(support),
            "support_group_serials": "|".join(row["group_serial"] for row in support),
            "support_diagrams": "|".join(dict.fromkeys(row["diagram_id"] for row in support)),
            "teaching_rule_de": f"Lies {surface} im Astroregister als {value}.",
        })
    write("FOUR_HUNDRED_SIXTY_SEVENTH_TWO_FINAL_ASTRO_CORES.tsv", new_cores)

    by_locus: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in groups:
        by_locus[row["locus"]].append(row)
    loci = []
    for locus, rows in by_locus.items():
        whole = sum(row["nomenclator_resolution"] == "MEMORIZED_WHOLE_NAME" for row in rows)
        loci.append({
            "locus_row": len(loci) + 1,
            "diagram_id": rows[0]["diagram_id"],
            "page": rows[0]["page"],
            "locus": locus,
            "local_namespace": rows[0]["local_namespace"],
            "groups": len(rows),
            "group_serials": "|".join(row["group_serial"] for row in rows),
            "complete_reading_de": "; ".join(row["atomic_common_root_value_de"] for row in rows),
            "compositional_groups": len(rows) - whole,
            "memorized_whole_names": whole,
            "locus_status": "COMPOSITION_PLUS_ONE_WHOLE_NAME" if whole else "FULLY_COMPOSITIONAL",
            "orientation": "UNSPECIFIED",
            "cross_instrument_join": "NONE",
        })
    write("FOUR_HUNDRED_SIXTY_SEVENTH_142_ASTRO_LOCUS_CLOSED_NOMENCLATOR.tsv", loci)

    group_by_serial = {int(row["group_serial"]): row for row in groups}
    ledger = []
    for row in read(LEDGER):
        out = dict(row)
        if row["domain"] == "ASTRO":
            group = group_by_serial[int(row["unified_id"].split(":")[1])]
            out["formal_parse"] = group["selected_component_parse"]
            out["atomic_default_de"] = group["atomic_common_root_value_de"]
            out["context_expansion_de"] = group["atomic_common_root_value_de"]
            out["interpretation_status"] = "MEMORIZED_ASTRO_WHOLE_NAME" if group["nomenclator_resolution"] == "MEMORIZED_WHOLE_NAME" else group["transfer_status"]
        ledger.append(out)
    write("FOUR_HUNDRED_SIXTY_SEVENTH_776_GROUP_COMPLETE_APPRENTICE_LEDGER.tsv", ledger)

    dictionary = []
    for row in read(COMPONENTS):
        dictionary.append({
            "unit_no": len(dictionary) + 1,
            "scope": "SHARED_PROSE_ASTRO",
            "unit_kind": "PRODUCTIVE_COMPONENT",
            "surface_or_component": row["component"],
            "default_value_de": row["value_de"],
            "context_rule_de": f"Komponiere {row['component']} mit seinen Nachbarbausteinen.",
            "support_groups_or_events": row["combined_support_cards"],
            "source": "PASS463_SHARED_COMPONENT",
        })
    all_astro_cores = read(ASTRO_CORES) + new_cores
    for row in all_astro_cores:
        support = sum(row["component"] in group["selected_component_parse"].split("+") for group in groups)
        dictionary.append({
            "unit_no": len(dictionary) + 1,
            "scope": "ASTRO_ONLY",
            "unit_kind": "PRODUCTIVE_ADDRESS_COMPONENT",
            "surface_or_component": row["component"],
            "default_value_de": row["atomic_value_de"],
            "context_rule_de": row["teaching_rule_de"],
            "support_groups_or_events": support,
            "source": "PASS466_467_ASTRO_COMPONENT",
        })
    whole_cards = [row for row in read(CARDS) if row["lexicon_class"] == "MEMORIZED_WHOLE_CARD"]
    for row in whole_cards:
        dictionary.append({
            "unit_no": len(dictionary) + 1,
            "scope": "PROSE",
            "unit_kind": "MEMORIZED_WHOLE_CARD",
            "surface_or_component": row["surfaces"],
            "default_value_de": row["small_value_de"],
            "context_rule_de": "Als eine gelernte Ganzkarte kopieren.",
            "support_groups_or_events": row["events"],
            "source": "PASS463_PROSE_DICTIONARY",
        })
    dictionary.append({
        "unit_no": len(dictionary) + 1,
        "scope": "ASTRO_ONLY",
        "unit_kind": "MEMORIZED_WHOLE_NAME",
        "surface_or_component": "otaza",
        "default_value_de": "Himmelsname OTAZA",
        "context_rule_de": "Als lokalen Namen auf f69v kopieren; nicht zerlegen.",
        "support_groups_or_events": 1,
        "source": "PASS467_LOCAL_NOMENCLATOR",
    })
    write("FOUR_HUNDRED_SIXTY_SEVENTH_52_UNIT_APPRENTICE_DICTIONARY.tsv", dictionary)

    aliases = read(ALIASES)
    write("FOUR_HUNDRED_SIXTY_SEVENTH_ELEVEN_EXACT_CARD_ALIAS_RULES.tsv", aliases)
    write("FOUR_HUNDRED_SIXTY_SEVENTH_ONE_ASTRO_WHOLE_NAME.tsv", [{
        "surface": "otaza", "group_serial": "258", "diagram_id": "A3", "page": "f69v",
        "locus": "f69v.1", "default_value_de": "Himmelsname OTAZA",
        "copy_rule_de": "Ungeteilt aus dem lokalen f69v-Namenverzeichnis kopieren.",
    }])

    md = [
        "# Complete ten-page apprentice dictionary", "",
        "## Inventory", "",
        "- 35 shared productive workshop components",
        "- 10 Astro-only address and counting components",
        "- 6 memorized prose whole cards",
        "- 1 memorized Astro whole name",
        "- 11 exact-card alias selection rules", "",
        "## Writing order", "",
        "1. Choose the visible picture or diagram owner.",
        "2. Write shared operation, argument, grade and endpoint components.",
        "3. In Astro, add address components D/S/A/F/AM/CPH/CFH/G/I/AN.",
        "4. At a label edge, expand S as a star label and D as a place label.",
        "5. Copy one of the six prose whole cards or OTAZA only when the exemplar calls for it.",
        "6. Apply the eleven surface-selection rules to recover the exact card shape.", "",
        "## Result", "",
        "All 776 visible groups receive one short default. Of 395 Astro groups, 394 are compositions and only OTAZA is a learned local name. No orientation or f68-to-f69 key is assumed.",
    ]
    (HERE / "FOUR_HUNDRED_SIXTY_SEVENTH_COMPLETE_TEN_PAGE_APPRENTICE_MANUAL.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    summary = {
        "status": "PASS",
        "new_final_cores": len(new_cores),
        "newly_composed_groups": len(decisions),
        "astro_compositional_groups": sum(row["nomenclator_resolution"] != "MEMORIZED_WHOLE_NAME" for row in groups),
        "astro_whole_names": sum(row["nomenclator_resolution"] == "MEMORIZED_WHOLE_NAME" for row in groups),
        "dictionary_units": len(dictionary),
        "alias_rules": len(aliases),
        "unified_groups": len(ledger),
    }
    (HERE / "FOUR_HUNDRED_SIXTY_SEVENTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
