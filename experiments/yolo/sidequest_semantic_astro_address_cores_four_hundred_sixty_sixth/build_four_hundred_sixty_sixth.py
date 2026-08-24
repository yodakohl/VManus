#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import defaultdict
from functools import lru_cache
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = ROOT / "experiments/yolo/sidequest_semantic_astro_label_frames_four_hundred_sixty_fifth"
GROUPS = BASE / "FOUR_HUNDRED_SIXTY_FIFTH_395_ASTRO_GROUP_LABEL_FRAMES.tsv"
LEDGER = BASE / "FOUR_HUNDRED_SIXTY_FIFTH_776_GROUP_LABEL_FRAME_LEDGER.tsv"
SURFACES = ROOT / "experiments/yolo/sidequest_semantic_astro_component_transfer_four_hundred_sixty_first/FOUR_HUNDRED_SIXTY_FIRST_COMPONENT_SURFACE_LEXICON.tsv"
VALUES = ROOT / "experiments/yolo/sidequest_semantic_ten_page_common_roots_four_hundred_sixty_third/FOUR_HUNDRED_SIXTY_THIRD_35_COMPONENT_COMMON_ROOT_MANUAL.tsv"

ASTRO_ATOMS = {
    "d": ("D_ADDR", "Teiladresse"),
    "s": ("S_ADDR", "Sternbezug"),
    "a": ("A_ADDR", "Nebenadresse"),
    "f": ("F_ADDR", "Aussenbezug"),
    "am": ("AM_ADDR", "Gegenfeld"),
    "cph": ("CPH_CLASS", "Sternfigur"),
    "cfh": ("CFH_CLASS", "Sternhaufen"),
    "g": ("G_ADDR", "Strahlmarke"),
}


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
    groups_in = read(GROUPS)
    values = {row["component"]: row["value_de"] for row in read(VALUES)}
    for _, (component, value) in ASTRO_ATOMS.items():
        values[component] = value
    atom_surface: dict[str, set[str]] = defaultdict(set)
    for row in read(SURFACES):
        atom_surface[row["surface_atom"]].update(row["components"].split("|"))
    for surface, (component, _) in ASTRO_ATOMS.items():
        atom_surface[surface].add(component)
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

    by_locus: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in groups_in:
        by_locus[row["locus"]].append(row)
    decisions = []
    selected_by_serial = {}
    for row in groups_in:
        if row["transfer_status"] != "ASTRO_LOCAL_LABEL":
            continue
        alternatives = parses(row["surface"])
        if not alternatives:
            continue
        locus_rows = by_locus[row["locus"]]
        position = locus_rows.index(row) + 1
        total = len(locus_rows)
        if any("CHD" in option for option in alternatives):
            selected = next(option for option in alternatives if "CHD" in option)
            rule = "KNOWN_CHD_MACRO_PRIORITY"
        elif any(option and option[0] == "OT" for option in alternatives):
            selected = next(option for option in alternatives if option and option[0] == "OT")
            rule = "KNOWN_OT_SEQUENCE_PRIORITY"
        elif len(alternatives) > 1 and any(option and option[-1] == "DY" for option in alternatives):
            endpoint = position == total
            selected = next(option for option in alternatives if option[-1] == ("DY" if endpoint else "Y"))
            rule = "LOCUS_ENDPOINT" if endpoint else "LOCUS_INTERNAL_CURRENT_ITEM"
        else:
            selected = alternatives[0]
            rule = "UNIQUE_SHORTEST_ASTRO_ADDRESS_PARSE"
        parse_text = "+".join(selected)
        atomic = " + ".join(values[part] for part in selected)
        selected_by_serial[row["group_serial"]] = (parse_text, atomic, rule)
        decisions.append({
            "decision_order": len(decisions) + 1,
            "group_serial": row["group_serial"],
            "diagram_id": row["diagram_id"],
            "page": row["page"],
            "locus": row["locus"],
            "position_in_locus": position,
            "groups_in_locus": total,
            "surface": row["surface"],
            "parse_alternatives": " || ".join("+".join(option) for option in alternatives),
            "selected_parse": parse_text,
            "selected_atomic_value_de": atomic,
            "selection_rule": rule,
        })
    write("FOUR_HUNDRED_SIXTY_SIXTH_65_ADDRESS_CORE_DECISIONS.tsv", decisions)

    atoms = []
    for surface, (component, value) in ASTRO_ATOMS.items():
        support = [row for row in decisions if component in row["selected_parse"].split("+")]
        atoms.append({
            "surface_atom": surface,
            "component": component,
            "atomic_value_de": value,
            "support_groups": len(support),
            "support_group_serials": "|".join(row["group_serial"] for row in support),
            "support_diagrams": "|".join(dict.fromkeys(row["diagram_id"] for row in support)),
            "teaching_rule_de": f"Lies {surface} im Astroregister als {value}.",
        })
    write("FOUR_HUNDRED_SIXTY_SIXTH_EIGHT_ASTRO_ADDRESS_CORES.tsv", atoms)

    groups = []
    for row in groups_in:
        out = dict(row)
        if row["group_serial"] in selected_by_serial:
            parse_text, atomic, rule = selected_by_serial[row["group_serial"]]
            out["selected_component_parse"] = parse_text
            out["atomic_common_root_value_de"] = atomic
            out["transfer_status"] = "ASTRO_ADDRESS_CORE_RESOLVED_SEQUENCE"
            out["address_core_resolution_rule"] = rule
        else:
            out["address_core_resolution_rule"] = "NOT_APPLIED"
        groups.append(out)
    write("FOUR_HUNDRED_SIXTY_SIXTH_395_ASTRO_GROUP_ADDRESS_CORES.tsv", groups)

    resolved_loci: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in groups:
        resolved_loci[row["locus"]].append(row)
    loci = []
    for locus, rows in resolved_loci.items():
        local = sum(row["transfer_status"] == "ASTRO_LOCAL_LABEL" for row in rows)
        status = "LOCAL_ONLY" if local == len(rows) else "MIXED_LOCAL_AND_RESOLVED" if local else "FULLY_RESOLVED"
        loci.append({
            "locus_row": len(loci) + 1,
            "diagram_id": rows[0]["diagram_id"],
            "page": rows[0]["page"],
            "locus": locus,
            "local_namespace": rows[0]["local_namespace"],
            "groups": len(rows),
            "group_serials": "|".join(row["group_serial"] for row in rows),
            "resolved_atomic_reading_de": "; ".join(row["atomic_common_root_value_de"] for row in rows),
            "resolved_groups": len(rows) - local,
            "local_groups": local,
            "locus_resolution_status": status,
            "orientation": "UNSPECIFIED",
            "cross_instrument_join": "NONE",
        })
    write("FOUR_HUNDRED_SIXTY_SIXTH_142_ASTRO_LOCUS_ADDRESS_CORES.tsv", loci)

    group_by_serial = {int(row["group_serial"]): row for row in groups}
    ledger = []
    for row in read(LEDGER):
        out = dict(row)
        if row["domain"] == "ASTRO":
            group = group_by_serial[int(row["unified_id"].split(":")[1])]
            out["formal_parse"] = group["selected_component_parse"]
            out["atomic_default_de"] = group["atomic_common_root_value_de"]
            out["context_expansion_de"] = group["atomic_common_root_value_de"]
            out["interpretation_status"] = group["transfer_status"]
        ledger.append(out)
    write("FOUR_HUNDRED_SIXTY_SIXTH_776_GROUP_ADDRESS_CORE_LEDGER.tsv", ledger)

    remaining = []
    for row in groups:
        if row["transfer_status"] == "ASTRO_LOCAL_LABEL":
            remaining.append({
                "remaining_order": len(remaining) + 1,
                "group_serial": row["group_serial"],
                "diagram_id": row["diagram_id"],
                "page": row["page"],
                "locus": row["locus"],
                "surface": row["surface"],
                "local_namespace": row["local_namespace"],
                "default_whole_name_de": f"gelernter Himmelsname {row['surface'].upper()}",
            })
    write("FOUR_HUNDRED_SIXTY_SIXTH_12_REMAINING_WHOLE_NAMES.tsv", remaining)

    summary = {
        "status": "PASS",
        "new_address_cores": len(atoms),
        "newly_resolved_groups": len(decisions),
        "total_resolved_groups": sum(row["transfer_status"] != "ASTRO_LOCAL_LABEL" for row in groups),
        "remaining_local_groups": len(remaining),
        "fully_resolved_loci": sum(row["locus_resolution_status"] == "FULLY_RESOLVED" for row in loci),
        "mixed_loci": sum(row["locus_resolution_status"] == "MIXED_LOCAL_AND_RESOLVED" for row in loci),
        "local_only_loci": sum(row["locus_resolution_status"] == "LOCAL_ONLY" for row in loci),
    }
    (HERE / "FOUR_HUNDRED_SIXTY_SIXTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
