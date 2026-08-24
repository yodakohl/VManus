#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P481 = ROOT / "experiments/yolo/sidequest_semantic_direction_triad_four_hundred_eighty_first"


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


def parts(parse: str) -> set[str]:
    return set(parse.replace("WHOLE[", "").replace("]", "").split("+"))


def visible_path(owner_code: str) -> bool:
    if "GAP_UNRESOLVED" in owner_code:
        return False
    return any(token in owner_code for token in ("PAIR", "CYLINDER", "DEVICE", "POOL", "EDGE", "ARCH", "S_RUN", "MULTIPORT"))


def slot(required: bool, explicit: list[str], whole: str | None, owner: str | None, inherited: str | None, local: str) -> tuple[str, str]:
    if not required:
        return "NOT_REQUIRED", "—"
    if explicit:
        return "EXPLICIT", " | ".join(explicit)
    if whole:
        return "WHOLE_CARD", whole
    if owner:
        return "OWNER_VISIBLE", owner
    if inherited:
        return "RECORD_INHERITED", inherited
    return "LOCAL_EXEMPLAR", local


def main() -> None:
    events = read(P481 / "FOUR_HUNDRED_EIGHTY_FIRST_381_DIRECTION_REVISED_PROSE_EVENTS.tsv")
    astro = read(P481 / "FOUR_HUNDRED_EIGHTY_FIRST_395_DIRECTION_REVISED_ASTRO_GROUPS.tsv")
    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        by_statement[row["statement_id"]].append(row)

    state: dict[str, dict[str, str | None]] = {}
    matrix = []
    for sid in dict.fromkeys(row["statement_id"] for row in events):
        rows = by_statement[sid]
        record = rows[0]["record_unit_id"]
        if record not in state:
            state[record] = {"source": None, "quantity": None, "path": None, "target": None, "owner": None}
        st = state[record]
        owner_codes = list(dict.fromkeys(row["owner_code"] for row in rows))
        owner_names = list(dict.fromkeys(row["concrete_owner_de"] for row in rows))
        reset = rows[0]["owner_reset"] == "YES" or st["owner"] not in {None, owner_codes[0]}
        phases = {row["action_phase"] for row in rows}
        source_required = bool(phases & {"SELECT", "PREPARE", "MOVE", "APPLY", "COLLECT"})
        quantity_required = "MEASURE" in phases
        path_required = "MOVE" in phases
        target_required = bool(phases & {"MOVE", "APPLY"})

        source_explicit = [row["pass481_event_de"] for row in rows if "AR" in parts(row["component_parse"])]
        quantity_explicit = [row["pass481_event_de"] for row in rows if row["quantity_root"] != "NONE"]
        path_explicit = [row["pass481_event_de"] for row in rows if "AIR" in parts(row["component_parse"])]
        target_explicit = [row["pass481_event_de"] for row in rows if "AL" in parts(row["component_parse"])]
        receiver = "Arbeitsfach/Empfänger" if any(row["joint_tuple_id"] == "df1098831679a8ad1b39" for row in rows) else None
        owner_source = rows[0]["short_active_before_de"] if reset else None
        owner_target = " → ".join(owner_names) if rows[0]["register"] == "BIOLOGICAL" else None
        owner_path = "sichtbarer lokaler Lauf bei " + " → ".join(owner_names) if any(visible_path(code) for code in owner_codes) else None

        source_status, source_value = slot(source_required, source_explicit, None, owner_source, None if reset else st["source"], "lokal gelernter Ausgangsbestand")
        quantity_status, quantity_value = slot(quantity_required, quantity_explicit, None, None, None if reset else st["quantity"], "lokal gelerntes Maß oder Stufe")
        path_status, path_value = slot(path_required, path_explicit, None, owner_path, None if reset else st["path"], "lokal gelernter Transferweg")
        target_status, target_value = slot(target_required, target_explicit, receiver, owner_target, None if reset else st["target"], "örtlich gelernte, nicht sichtbare Zielstelle")

        if source_status in {"EXPLICIT", "OWNER_VISIBLE"}:
            st["source"] = source_value
        if quantity_status == "EXPLICIT":
            st["quantity"] = quantity_value
        if path_status in {"EXPLICIT", "OWNER_VISIBLE"}:
            st["path"] = path_value
        if target_status in {"EXPLICIT", "WHOLE_CARD", "OWNER_VISIBLE"}:
            st["target"] = target_value
        st["owner"] = owner_codes[-1]
        st["source"] = rows[-1]["short_active_after_de"]

        statuses = [status for required, status in ((source_required, source_status), (quantity_required, quantity_status), (path_required, path_status), (target_required, target_status)) if required]
        if not statuses:
            completion = "NO_DIRECTIONAL_OR_QUANTITY_SLOT_REQUIRED"
        elif all(status == "EXPLICIT" for status in statuses):
            completion = "FULLY_EXPLICIT"
        elif "LOCAL_EXEMPLAR" in statuses:
            completion = "LOCAL_EXEMPLAR_REQUIRED"
        elif "RECORD_INHERITED" in statuses:
            completion = "RECORD_COMPLETED"
        else:
            completion = "IMAGE_OR_WHOLE_CARD_COMPLETED"
        action = "; ".join(row["pass481_event_de"] for row in rows) + "."
        expansion = f"Quelle [{source_status}]: {source_value}; Menge/Stufe [{quantity_status}]: {quantity_value}; Lauf [{path_status}]: {path_value}; Ziel [{target_status}]: {target_value}. Handlung: {action}"
        matrix.append({
            "statement_id": sid,
            "register": rows[0]["register"],
            "record_unit_id": record,
            "page": rows[0]["page"],
            "events": len(rows),
            "event_ids": "|".join(row["event_id"] for row in rows),
            "owner_codes": "|".join(owner_codes),
            "owner_reset": "YES" if reset else "NO",
            "source_required": "YES" if source_required else "NO",
            "source_status": source_status,
            "source_value_de": source_value,
            "quantity_required": "YES" if quantity_required else "NO",
            "quantity_status": quantity_status,
            "quantity_value_de": quantity_value,
            "path_required": "YES" if path_required else "NO",
            "path_status": path_status,
            "path_value_de": path_value,
            "target_required": "YES" if target_required else "NO",
            "target_status": target_status,
            "target_value_de": target_value,
            "completion_class": completion,
            "complete_expansion_de": expansion,
        })
    write("FOUR_HUNDRED_EIGHTY_SECOND_116_ELLIPSIS_MATRIX.tsv", matrix)

    counts = []
    for slot_name in ("source", "quantity", "path", "target"):
        for status in ("EXPLICIT", "OWNER_VISIBLE", "WHOLE_CARD", "RECORD_INHERITED", "LOCAL_EXEMPLAR", "NOT_REQUIRED"):
            n = sum(row[f"{slot_name}_status"] == status for row in matrix)
            counts.append({"slot": slot_name.upper(), "supply_status": status, "statements": n, "herbal": sum(row[f"{slot_name}_status"] == status and row["register"] == "HERBAL" for row in matrix), "biological": sum(row[f"{slot_name}_status"] == status and row["register"] == "BIOLOGICAL" for row in matrix)})
    write("FOUR_HUNDRED_EIGHTY_SECOND_SLOT_SUPPLY_COUNTS.tsv", counts)

    class_counts = Counter(row["completion_class"] for row in matrix)
    class_rows = [{"completion_class": key, "statements": value, "herbal": sum(row["completion_class"] == key and row["register"] == "HERBAL" for row in matrix), "biological": sum(row["completion_class"] == key and row["register"] == "BIOLOGICAL" for row in matrix)} for key, value in sorted(class_counts.items())]
    write("FOUR_HUNDRED_EIGHTY_SECOND_COMPLETION_CLASSES.tsv", class_rows)

    astro_loci: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in astro:
        astro_loci[(row["diagram_id"], row["page"], row["locus"])].append(row)
    units = []
    for unit in [f"H{n}" for n in range(1, 6)] + [f"B{n}" for n in range(1, 7)]:
        rows = [row for row in matrix if row["record_unit_id"] == unit]
        units.append({"unit_order": len(units)+1, "unit_id": unit, "page": rows[0]["page"], "domain": rows[0]["register"], "statements_or_loci": len(rows), "groups": sum(int(row["events"]) for row in rows), "continuous_complete_expansion_de": " ".join(row["complete_expansion_de"] for row in rows)})
    for unit in ("A1", "A2", "A3"):
        loci = [(key, rows) for key, rows in astro_loci.items() if key[0] == unit]
        units.append({"unit_order": len(units)+1, "unit_id": unit, "page": loci[0][0][1], "domain": "ASTRO", "statements_or_loci": len(loci), "groups": sum(len(rows) for _, rows in loci), "continuous_complete_expansion_de": " ".join("Locus " + key[2] + ": " + "; ".join(row["pass481_celestial_reading_de"] for row in rows) + "." for key, rows in loci)})
    write("FOUR_HUNDRED_EIGHTY_SECOND_14_ELLIPSIS_EXPANDED_UNITS.tsv", units)

    md = ["# Ellipsis-expanded ten-page edition", ""]
    for unit in units:
        md.extend([f"## {unit['unit_id']} — {unit['page']}", "", unit["continuous_complete_expansion_de"], ""])
    (HERE / "FOUR_HUNDRED_EIGHTY_SECOND_ELLIPSIS_EXPANDED_TEN_PAGE_EDITION.md").write_text("\n".join(md), encoding="utf-8")

    summary = {"status": "PASS", "statements": len(matrix), "prose_events": sum(int(row["events"]) for row in matrix), "completion_classes": dict(sorted(class_counts.items())), "local_exemplar_required": class_counts["LOCAL_EXEMPLAR_REQUIRED"], "record_completed": class_counts["RECORD_COMPLETED"], "image_or_whole_completed": class_counts["IMAGE_OR_WHOLE_CARD_COMPLETED"], "fully_explicit": class_counts["FULLY_EXPLICIT"], "units": len(units), "groups": sum(int(row["groups"]) for row in units)}
    (HERE / "FOUR_HUNDRED_EIGHTY_SECOND_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
