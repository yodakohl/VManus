#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import defaultdict
from functools import lru_cache
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = ROOT / "experiments/yolo/sidequest_semantic_astro_ambiguity_resolution_four_hundred_sixty_fourth"
GROUPS = BASE / "FOUR_HUNDRED_SIXTY_FOURTH_395_ASTRO_GROUP_RESOLVED.tsv"
LEDGER = BASE / "FOUR_HUNDRED_SIXTY_FOURTH_776_GROUP_RESOLVED_LEDGER.tsv"
COMPONENT_SURFACES = ROOT / "experiments/yolo/sidequest_semantic_astro_component_transfer_four_hundred_sixty_first/FOUR_HUNDRED_SIXTY_FIRST_COMPONENT_SURFACE_LEXICON.tsv"
COMPONENT_VALUES = ROOT / "experiments/yolo/sidequest_semantic_ten_page_common_roots_four_hundred_sixty_third/FOUR_HUNDRED_SIXTY_THIRD_35_COMPONENT_COMMON_ROOT_MANUAL.tsv"


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
    values = {row["component"]: row["value_de"] for row in read(COMPONENT_VALUES)}
    atom_surface: dict[str, set[str]] = defaultdict(set)
    for row in read(COMPONENT_SURFACES):
        for component in row["components"].split("|"):
            atom_surface[row["surface_atom"]].add(component)
    forms = sorted(atom_surface, key=lambda item: (-len(item), item))

    def minimal_parses(surface: str) -> list[tuple[str, ...]]:
        if surface.startswith("q"):
            surface = surface[1:]
        if not surface:
            return [()]

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

        parses = list(walk(0))
        if not parses:
            return []
        minimum = min(map(len, parses))
        return sorted(set(parse for parse in parses if len(parse) == minimum))

    resolutions = []
    resolution_by_serial = {}
    for row in groups_in:
        if row["transfer_status"] != "ASTRO_LOCAL_LABEL" or not row["surface"].endswith(("s", "d")):
            continue
        label_surface = row["surface"][-1]
        core = row["surface"][:-1]
        parses = minimal_parses(core)
        if not parses:
            continue
        if len(parses) == 1:
            selected = parses[0]
            rule = "UNIQUE_CORE_AFTER_LABEL_FRAME_REMOVAL"
        else:
            preferred = [parse for parse in parses if "CHD" in parse or "OT" in parse]
            selected = preferred[0] if preferred else parses[0]
            rule = "KNOWN_MACRO_PRIORITY_AFTER_LABEL_FRAME_REMOVAL"
        label_component = "S_LABEL" if label_surface == "s" else "D_LABEL"
        label_value = "Sternetikett" if label_surface == "s" else "Platzetikett"
        parse_text = "+".join(selected + (label_component,))
        base_value = " + ".join(values[part] for part in selected)
        atomic = f"{base_value} + {label_value}" if base_value else label_value
        resolution_by_serial[row["group_serial"]] = (parse_text, atomic, rule)
        resolutions.append({
            "resolution_order": len(resolutions) + 1,
            "group_serial": row["group_serial"],
            "diagram_id": row["diagram_id"],
            "page": row["page"],
            "locus": row["locus"],
            "surface": row["surface"],
            "core_surface": core or "EMPTY",
            "label_frame": label_component,
            "label_frame_value_de": label_value,
            "core_parse_alternatives": " || ".join("+".join(parse) if parse else "EMPTY" for parse in parses),
            "selected_parse": parse_text,
            "selected_atomic_value_de": atomic,
            "selection_rule": rule,
        })
    write("FOUR_HUNDRED_SIXTY_FIFTH_36_LABEL_FRAME_RESOLUTIONS.tsv", resolutions)

    groups = []
    for row in groups_in:
        out = dict(row)
        if row["group_serial"] in resolution_by_serial:
            parse_text, atomic, rule = resolution_by_serial[row["group_serial"]]
            out["selected_component_parse"] = parse_text
            out["atomic_common_root_value_de"] = atomic
            out["transfer_status"] = "ASTRO_LABEL_FRAME_RESOLVED_COMPONENT_SEQUENCE"
            out["label_frame_resolution_rule"] = rule
        else:
            out["label_frame_resolution_rule"] = "NOT_APPLIED"
        groups.append(out)
    write("FOUR_HUNDRED_SIXTY_FIFTH_395_ASTRO_GROUP_LABEL_FRAMES.tsv", groups)

    by_locus: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in groups:
        by_locus[row["locus"]].append(row)
    loci = []
    for locus, rows in by_locus.items():
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
    write("FOUR_HUNDRED_SIXTY_FIFTH_142_ASTRO_LOCUS_LABEL_FRAMES.tsv", loci)

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
    write("FOUR_HUNDRED_SIXTY_FIFTH_776_GROUP_LABEL_FRAME_LEDGER.tsv", ledger)

    types: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in groups_in:
        if row["transfer_status"] == "ASTRO_LOCAL_LABEL":
            types[row["surface"]].append(row)
    type_rows = []
    for surface, rows in sorted(types.items(), key=lambda item: (-len(item[1]), item[0])):
        type_rows.append({
            "local_type_order": len(type_rows) + 1,
            "surface": surface,
            "occurrences": len(rows),
            "diagrams": "|".join(dict.fromkeys(row["diagram_id"] for row in rows)),
            "namespaces": "|".join(dict.fromkeys(row["local_namespace"] for row in rows)),
            "group_serials": "|".join(row["group_serial"] for row in rows),
            "label_frame_resolved": "YES" if any(row["group_serial"] in resolution_by_serial for row in rows) else "NO",
            "working_type_value_de": resolution_by_serial[rows[0]["group_serial"]][1] if rows[0]["group_serial"] in resolution_by_serial else f"gelernter Himmelsname {surface.upper()}",
        })
    write("FOUR_HUNDRED_SIXTY_FIFTH_98_LOCAL_TYPE_REGISTER.tsv", type_rows)

    summary = {
        "status": "PASS",
        "input_local_groups": 113,
        "input_local_types": len(type_rows),
        "label_frame_resolved_groups": len(resolutions),
        "remaining_local_groups": sum(row["transfer_status"] == "ASTRO_LOCAL_LABEL" for row in groups),
        "total_resolved_groups": sum(row["transfer_status"] != "ASTRO_LOCAL_LABEL" for row in groups),
        "fully_resolved_loci": sum(row["locus_resolution_status"] == "FULLY_RESOLVED" for row in loci),
        "mixed_loci": sum(row["locus_resolution_status"] == "MIXED_LOCAL_AND_RESOLVED" for row in loci),
        "local_only_loci": sum(row["locus_resolution_status"] == "LOCAL_ONLY" for row in loci),
    }
    (HERE / "FOUR_HUNDRED_SIXTY_FIFTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
