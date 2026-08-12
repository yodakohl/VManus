#!/usr/bin/env python3
"""Build the text-blind RTA001 author-visible relation graph inventory.

This builder never reads a transcription surface.  It consumes only already
published topology/annotation artifacts and emits directed relation edges.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"

ANNOTATIONS = RESULTS / "existing_human_exact_locus_annotations.tsv"
CIRCLES = RESULTS / "special_circle_text_blind_array_inventory.tsv"
ROSETTES_SELECTION = RESULTS / "rd5x3001_rosettes_doorway_selection.json"
ROSETTES_RESULT = RESULTS / "rd5x3001_rosettes_doorway_topology_result.json"

OUT_TSV = RESULTS / "rta001_relation_graph_inventory.tsv"
OUT_JSON = RESULTS / "rta001_relation_graph_inventory.json"

FIELDS = [
    "panel_id",
    "physical_folio",
    "page",
    "source_node",
    "target_node",
    "relation_type",
    "relation_instance",
    "source_locus",
    "target_locus",
    "ownership_or_topology_basis",
    "allowed_panel_symmetries",
    "previous_exposure",
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def strict_json(path: Path) -> object:
    def pairs(items: list[tuple[str, object]]) -> dict[str, object]:
        out: dict[str, object] = {}
        for key, value in items:
            if key in out:
                raise ValueError(f"duplicate JSON key in {path}: {key}")
            out[key] = value
        return out

    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=pairs)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def edge(
    panel_id: str,
    physical_folio: str,
    page: str,
    source_node: str,
    target_node: str,
    relation_type: str,
    relation_instance: str,
    source_locus: str,
    target_locus: str,
    basis: str,
    symmetries: str,
    exposure: str,
) -> dict[str, str]:
    row = {
        "panel_id": panel_id,
        "physical_folio": physical_folio,
        "page": page,
        "source_node": source_node,
        "target_node": target_node,
        "relation_type": relation_type,
        "relation_instance": relation_instance,
        "source_locus": source_locus,
        "target_locus": target_locus,
        "ownership_or_topology_basis": basis,
        "allowed_panel_symmetries": symmetries,
        "previous_exposure": exposure,
    }
    assert list(row) == FIELDS
    return row


def circle_edges(rows: list[dict[str, str]]) -> tuple[list[dict[str, str]], list[dict[str, object]]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[row["array_id"]].append(row)
    out: list[dict[str, str]] = []
    excluded: list[dict[str, object]] = []
    for array_id in sorted(grouped, key=lambda x: int(x.split("|", 1)[0].replace("SCARR", ""))):
        group = sorted(grouped[array_id], key=lambda x: int(x["slot_index"]))
        states = Counter(x["occupancy_state"] for x in group)
        n = int(group[0]["slot_count"])
        if n != len(group) or states != {"TRANSCRIBED": n}:
            excluded.append(
                {
                    "panel_id": array_id,
                    "reason": "INCOMPLETE_CYCLE",
                    "slot_count": n,
                    "inventory_rows": len(group),
                    "occupancy_states": dict(sorted(states.items())),
                }
            )
            continue
        if n < 4:
            excluded.append({"panel_id": array_id, "reason": "FEWER_THAN_FOUR_SLOTS", "slot_count": n})
            continue
        folio = group[0]["physical_folio"]
        page = group[0]["page"]
        unit = group[0]["unit"]
        basis = (
            f"Published text-blind special-circle array {array_id}; {group[0]['unit_description']} "
            "Slot order is the complete human-transcribed author-visible circular sequence."
        )
        for i, src in enumerate(group):
            dst = group[(i + 1) % n]
            out.append(
                edge(
                    array_id,
                    folio,
                    page,
                    f"{array_id}:S{int(src['slot_index']):03d}",
                    f"{array_id}:S{int(dst['slot_index']):03d}",
                    "CYCLIC_SUCCESSOR",
                    f"{array_id}:E{int(src['slot_index']):03d}",
                    src["locus"],
                    dst["locus"],
                    basis,
                    f"DIHEDRAL_D{n}:ROTATIONS_{n}:REFLECTIONS_{n}",
                    "SPECIAL_CIRCLE_TEXT_BLIND_ARRAY_INVENTORY;TEXT_ASSOCIATION_UNOPENED_AT_SELECTION",
                )
            )
    return out, excluded


def f75_edges(annotations: list[dict[str, str]]) -> list[dict[str, str]]:
    selected = []
    for row in annotations:
        if row["page"] != "f75v" or row["unit"] != "N1":
            continue
        match = re.search(r"Label L(\d+), line ([12])\.$", row["local_comment"])
        if match:
            selected.append((int(match.group(1)), int(match.group(2)), row))
    by_column = defaultdict(dict)
    for column, line, row in selected:
        by_column[column][line] = row
    if sorted(by_column) != list(range(1, 11)) or any(set(x) != {1, 2} for x in by_column.values()):
        raise ValueError("f75v N1 is not the registered ten complete two-line stacks")
    out = []
    for column in range(1, 11):
        src, dst = by_column[column][1], by_column[column][2]
        out.append(
            edge(
                "RTA001|f75v|N1_TWO_LINE_STACKS",
                "f75",
                "f75v",
                f"f75v:N1:L{column:02d}:R1",
                f"f75v:N1:L{column:02d}:R2",
                "ROW_SUCCESSOR",
                f"f75v:N1:L{column:02d}:R1_TO_R2",
                src["locus"],
                dst["locus"],
                "Existing human annotation explicitly groups each pair as line 1 and line 2 of one two-line label L1-L10.",
                "COLUMN_ORDER_C2_REVERSAL;ROW_DIRECTION_FIXED",
                "F67_TAIL_ECHO_F75V_TRANSFER_SCREEN;PAIRING_PREEXISTED_AND_WAS_NOT_STRING_SELECTED",
            )
        )
    return out


def f67_sector_edges(annotations: list[dict[str, str]]) -> list[dict[str, str]]:
    sector_rows: dict[str, dict[int, dict[str, str]]] = defaultdict(dict)
    pattern = re.compile(r"Sector at ([0-9]{2}:[0-9]{2}), line ([1-4])\.")
    for row in annotations:
        if row["page"] != "f67r2" or row["unit"] != "Q1":
            continue
        match = pattern.search(row["local_comment"])
        if match:
            sector_rows[match.group(1)][int(match.group(2))] = row
    if len(sector_rows) != 12 or any(sorted(lines) != list(range(1, max(lines) + 1)) for lines in sector_rows.values()):
        raise ValueError("f67r2 Q1 is not the registered twelve complete sector line stacks")
    out = []
    panel = "RTA001|f67r2|Q1_SECTOR_ROWS"
    for sector in sorted(sector_rows):
        lines = sector_rows[sector]
        maximum = max(lines)
        safe_sector = sector.replace(":", "")
        for source_line in range(1, maximum):
            target_line = source_line + 1
            src, dst = lines[source_line], lines[target_line]
            out.append(
                edge(
                    panel,
                    "f67",
                    "f67r2",
                    f"f67r2:Q1:{safe_sector}:R{source_line}",
                    f"f67r2:Q1:{safe_sector}:R{target_line}",
                    "ROW_SUCCESSOR",
                    f"f67r2:Q1:{safe_sector}:R{source_line}_TO_R{target_line}",
                    src["locus"],
                    dst["locus"],
                    "Existing human annotation assigns numbered text lines to the same author-drawn moon sector.",
                    "SECTOR_ORDER_D12;ROW_DIRECTION_FIXED",
                    "EXISTING_HUMAN_SECTOR_LINE_ANNOTATION;NO_STRING_SELECTION",
                )
            )
        for source_line in range(1, maximum - 1):
            target_line = source_line + 2
            src, dst = lines[source_line], lines[target_line]
            out.append(
                edge(
                    panel,
                    "f67",
                    "f67r2",
                    f"f67r2:Q1:{safe_sector}:R{source_line}",
                    f"f67r2:Q1:{safe_sector}:R{target_line}",
                    "ROW_SKIP_ONE",
                    f"f67r2:Q1:{safe_sector}:R{source_line}_TO_R{target_line}",
                    src["locus"],
                    dst["locus"],
                    "Derived two-step edge inside the same numbered author-drawn sector, retained only for composition testing.",
                    "SECTOR_ORDER_D12;ROW_DIRECTION_FIXED",
                    "EXISTING_HUMAN_SECTOR_LINE_ANNOTATION;DERIVED_BEFORE_TEXT_ACCESS",
                )
            )
    return out


def rosettes_edges(selection: dict[str, object], result: dict[str, object]) -> list[dict[str, str]]:
    if result.get("status") != "PASS_LOCAL_FIVE_BY_THREE_AUTHOR_VISIBLE_SCHEMA":
        raise ValueError("Rosettes 5x3 topology is not registered PASS")
    rows = selection["rows"]
    if not isinstance(rows, list) or len(rows) != 15:
        raise ValueError("Rosettes selection must contain exactly 15 rows")
    out = []
    panel = "RTA001|fRos|FIVE_BY_THREE"
    for record in range(5):
        triplet = rows[record * 3 : record * 3 + 3]
        for source_position, target_position, relation_type in [
            (1, 2, "ROW_SUCCESSOR"),
            (2, 3, "ROW_SUCCESSOR"),
            (1, 3, "ROW_SKIP_ONE"),
        ]:
            src = triplet[source_position - 1]
            dst = triplet[target_position - 1]
            out.append(
                edge(
                    panel,
                    "fRos",
                    str(src["page"]),
                    f"fRos:RECORD{record + 1}:R{source_position}",
                    f"fRos:RECORD{record + 1}:R{target_position}",
                    relation_type,
                    f"fRos:RECORD{record + 1}:R{source_position}_TO_R{target_position}",
                    str(src["locus"]),
                    str(dst["locus"]),
                    "Published native-visual PASS: five author-separated openings, each containing one local three-row stack.",
                    "RECORD_ORDER_C2_REVERSAL;ROW_DIRECTION_FIXED",
                    "RD5X3001_TOPOLOGY_EXPOSED;FORMAL_ASSOCIATION_UNOPENED_BY_TOPOLOGY_SELECTION",
                )
            )
    return out


def build() -> tuple[list[dict[str, str]], dict[str, object]]:
    annotations = read_tsv(ANNOTATIONS)
    circle_rows = read_tsv(CIRCLES)
    circle, exclusions = circle_edges(circle_rows)
    rows = circle + f67_sector_edges(annotations) + f75_edges(annotations) + rosettes_edges(
        strict_json(ROSETTES_SELECTION), strict_json(ROSETTES_RESULT)
    )
    rows.sort(
        key=lambda r: (
            r["physical_folio"],
            r["panel_id"],
            r["relation_type"],
            r["relation_instance"],
        )
    )
    keys = [(r["panel_id"], r["relation_instance"]) for r in rows]
    if len(keys) != len(set(keys)):
        raise ValueError("duplicate panel/relation instance")
    metadata: dict[str, object] = {
        "experiment": "RTA001_GRAPH_TO_TEXT_OPERATOR_INDUCTION",
        "schema_version": "RTA001_RELATION_GRAPH_INVENTORY_V1",
        "status": "BUILT_TEXT_BLIND",
        "decision": "AUTHORIZE_EXACT_EDGE_PROGRAM_EXTRACTION",
        "inputs": {
            "existing_human_exact_locus_annotations_sha256": sha256(ANNOTATIONS),
            "special_circle_text_blind_array_inventory_sha256": sha256(CIRCLES),
            "rd5x3001_rosettes_doorway_selection_sha256": sha256(ROSETTES_SELECTION),
            "rd5x3001_rosettes_doorway_topology_result_sha256": sha256(ROSETTES_RESULT),
        },
        "counts": {
            "directed_edges": len(rows),
            "panels": len({r["panel_id"] for r in rows}),
            "physical_folios": len({r["physical_folio"] for r in rows}),
            "relation_types": dict(sorted(Counter(r["relation_type"] for r in rows).items())),
            "edges_by_folio": dict(sorted(Counter(r["physical_folio"] for r in rows).items())),
            "complete_circle_panels": len({r["panel_id"] for r in circle}),
        },
        "excluded_candidates": {
            "incomplete_circle_arrays": exclusions,
            "f57v": "Excluded: existing inner/outer correspondence is proximity-based and geometry-confounded.",
            "f84r": "Excluded: annotations do not establish repeated multi-row stacks; proposed ownership is ambiguous/proximity-based.",
            "cross_band_circle_pairings": "Excluded: no author-visible slot correspondence is registered.",
        },
        "holdout_unit": "physical_folio",
        "symmetry_policy": "Every allowed group is explicit per edge. Symmetries are marginalized or encoded; none may be selected after text inspection for free.",
        "previous_exposure_policy": "Rows record prior topology/formal exposure; no relation was selected by string similarity.",
        "claim_ceiling": "This inventory establishes directed author-visible formal relations only; it contains no meaning, language, cipher, plaintext, or translation claim.",
        "rows": rows,
    }
    return rows, metadata


def write(rows: list[dict[str, str]], metadata: dict[str, object]) -> None:
    OUT_TSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_TSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    metadata = dict(metadata)
    metadata["artifacts"] = {
        "inventory_tsv": str(OUT_TSV.relative_to(ROOT)),
        "inventory_tsv_sha256": sha256(OUT_TSV),
    }
    OUT_JSON.write_text(json.dumps(metadata, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="reconstruct and compare without writing")
    args = parser.parse_args()
    rows, metadata = build()
    if args.check:
        if not OUT_TSV.exists() or not OUT_JSON.exists():
            raise SystemExit("registered inventory outputs are absent")
        old_tsv = OUT_TSV.read_bytes()
        old_json = strict_json(OUT_JSON)
        import io

        buffer = io.StringIO(newline="")
        writer = csv.DictWriter(buffer, fieldnames=FIELDS, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        if old_tsv != buffer.getvalue().encode("utf-8"):
            raise SystemExit("inventory TSV differs from reconstruction")
        if not isinstance(old_json, dict) or old_json.get("counts") != metadata["counts"]:
            raise SystemExit("inventory JSON counts differ from reconstruction")
        print(json.dumps(metadata["counts"], sort_keys=True))
        return
    write(rows, metadata)
    print(json.dumps(metadata["counts"], sort_keys=True))


if __name__ == "__main__":
    main()
