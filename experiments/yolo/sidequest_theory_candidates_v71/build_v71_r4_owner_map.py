#!/usr/bin/env python3
"""Build the independent R4 image-to-text ownership map for V71."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


REPO = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
V69 = REPO / "experiments/yolo/sidequest_theory_candidates_v69"

FIELD_SOURCE = V69 / "V69_R4_FINAL_135_FIELD_EDITION.tsv"
ASTRO_SOURCE = V69 / "V69_R4_FINAL_395_ASTRO_GROUPS.tsv"

COLS = [
    "owner_row_id", "layer", "page", "source_id", "record_or_diagram",
    "locus", "owner_mode", "visible_owner", "visible_basis",
    "concrete_silent_argument_default", "strongest_rival", "confidence",
    "v69_revision",
]

PLANTS = {
    "f10r": ("WHOLE_TOOTHED_BLUE_FLOWER_PLANT", "the unidentified pictured toothed blue-flowered simple"),
    "f11r": ("WHOLE_DENSE_BLUE_CROWN_PLANT", "the unidentified pictured dense blue-flowered crown herb"),
    "f55v": ("WHOLE_BROAD_LEAF_PANICLED_PLANT", "the unidentified pictured broad-leaf panicled simple"),
    "f56r": ("WHOLE_MULTIHEAD_SPIRAL_PLANT", "the unidentified pictured multihead spiral herb"),
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, str]], cols: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        out = csv.DictWriter(handle, fieldnames=cols, delimiter="\t", lineterminator="\n")
        out.writeheader()
        out.writerows(rows)


def locus_number(locus: str) -> int:
    return int(locus.rsplit(".", 1)[1])


def prose_owner(row: dict[str, str], first_by_record: set[str]) -> tuple[str, str, str, str, str, str, str]:
    page = row["page"]
    locus = locus_number(row["locus"])
    first = row["field_id"] in first_by_record
    if page in PLANTS:
        owner, argument = PLANTS[page]
        mode = "PAGE_OWNER_ONLY" if first else "INHERITED_VISIBLE"
        basis = "single whole plant occupies and shapes the article text area; no leader ties one field to one part"
        rival = "ordinary plant-article recurrence without an omitted grammatical owner"
        revision = "REMOVE_NARROW_SPECIES_AND_UNPICTURED_OPERATION" if first else "KEEP_OWNER_INHERITANCE_ONLY"
        return mode, owner, basis, argument, rival, "MEDIUM", revision

    if page == "f81v":
        mode = "PAGE_OWNER_ONLY" if first else "INHERITED_VISIBLE"
        return (
            mode, "SHARED_GREEN_FIGURE_POOL", "one common green enclosure contains the two figure rows",
            "the shared pictured bath, pool, or collective station",
            "formal group tableau rather than an actual bath", "MEDIUM",
            "REPLACE_LONG_CIRCULATION_WITH_SHARED_STATION",
        )

    if page == "f82r":
        if locus <= 4:
            owner, arg = "UPPER_PAIRED_FIGURE_CYLINDER_ASSEMBLY", "the upper paired figure-and-cylinder station"
        elif locus <= 7:
            owner, arg = "MIDDLE_LOCAL_DEVICE_STATIONS", "the adjacent local vessel or hand-device station"
        elif locus <= 23:
            owner, arg = "RECLINING_FIGURE_AND_MIDDLE_STATION_ZONE", "the local reclining or middle application station"
        else:
            owner, arg = "LOWER_SHARED_GREEN_FIGURE_FIELD", "the lower shared figure-pool station"
        zone_first = row["field_id"] in {"F045", "F053", "F057", "F062"}
        mode = "PAGE_OWNER_ONLY" if zone_first else "INHERITED_VISIBLE"
        return (
            mode, owner, "locus falls in one of four visibly separated page zones; no contour joins all zones",
            arg, "one symbolic cosmological tableau with figures rather than apparatus", "LOW",
            "SPLIT_SINGLE_PROCESS_INTO_LOCAL_STATION_ZONES",
        )

    if page == "f83r":
        if locus <= 8:
            owner, arg = "UPPER_LOCAL_FIGURE_VESSEL_SET", "the upper local figure-and-vessel station"
        elif locus <= 24:
            owner, arg = "CENTRAL_LOCAL_STATION_SET", "the central local application or transfer station"
        elif locus <= 44:
            owner, arg = "ARCH_LINKED_LOWER_PAIR", "the lower arch-linked pair of figure vessels"
        elif locus <= 49:
            owner, arg = "RIGHT_S_CONDUIT_AND_HUB", "the right-hand S-conduit and multi-ended hub station"
        else:
            owner, arg = "LOWER_PAIRED_APPARATUS_CONTINUATION", "the final local paired-apparatus station"
        zone_first = row["field_id"] in {"F071", "F082", "F109", "F129", "F134"}
        mode = "PAGE_OWNER_ONLY" if zone_first else "INHERITED_VISIBLE"
        return (
            mode, owner, "record/locus zone lies beside a local pictured assembly; exact label-to-object leader is absent",
            arg, "page-level allegorical figure series", "LOW",
            "REMOVE_GLOBAL_FLOW_DIRECTION_AND_KEEP_LOCAL_ASSEMBLY",
        )
    raise AssertionError(page)


def astro_owner(row: dict[str, str]) -> tuple[str, str, str, str, str, str, str]:
    page = row["page"]
    n = locus_number(row["locus"])
    roles = row["roles"]
    if page == "f67r2":
        if n <= 12:
            return ("DIRECT_VISIBLE", "PAIRED_WHEEL_SECTOR_OR_KEY", "local radial key/descriptor occupies a drawn wheel slot", "the local celestial sector or station key", "decorative radial label", "MEDIUM", "REPLACE_LITERAL_7X12_WITH_LOCAL_WHEEL_SLOT")
        if n <= 51:
            return ("PAGE_OWNER_ONLY", "PAIRED_CELESTIAL_WHEEL_LOOKUP", "lookup fragments belong to the paired-wheel plate but lack an object leader", "the currently selected celestial condition or sector", "ordinary surrounding prose", "LOW", "KEEP_LOCAL_LOOKUP_WITHOUT_MATRIX_CLAIM")
        if n <= 71:
            return ("DIRECT_VISIBLE", "LOCAL_AUXILIARY_WHEEL_SLOT", "short key is placed in a bounded local radial or condition slot", "the local auxiliary celestial condition", "decorative caption", "MEDIUM", "KEEP_PAGE_LOCAL_CONDITION_ONLY")
        return ("PAGE_OWNER_ONLY", "PAIRED_CELESTIAL_WHEELS", "long fragments occupy residual prose regions rather than one sector", "the paired celestial lookup plate", "independent prose unrelated to the wheels", "LOW", "REMOVE_AUTHORIAL_START_AND_DIRECTION")

    if page == "f68r1":
        if n <= 7:
            return ("PAGE_OWNER_ONLY", "MULTIPANEL_STAR_ATLAS", "header/prose fragments lie over several star panels", "the current star-field panel or catalogue section", "one prose article over the whole foldout", "LOW", "REPLACE_SINGLE_CENTER_WITH_PANEL_OWNER")
        if n == 8 or n == 37:
            return ("DIRECT_VISIBLE", "RIGHT_SECTORIZED_STAR_SUBMAP_CENTER", "central key/legend is local to the sectorized circular submap", "the central owner or legend of the right star submap", "one of several face medallions rather than owner", "MEDIUM", "KEEP_CENTER_LOCAL_NOT_PAGE_GLOBAL")
        return ("DIRECT_VISIBLE", "RIGHT_SUBMAP_SPATIAL_STAR_SLOT", "one of 28 singleton address labels is placed in a local star/sector slot", "the locally addressed star station in the right submap", "label in an open star field rather than the right wheel", "MEDIUM", "RETAIN_LOCAL_28_ADDRESS_INVENTORY_ONLY")

    if page == "f69v":
        if n == 1:
            return ("PAGE_OWNER_ONLY", "LEFT_APPROX_28_PLACE_WHEEL", "first large circumtext block belongs to the left wheel region", "the left approximately 28-place celestial wheel", "general introduction to all three wheels", "MEDIUM", "LOCALIZE_28_TO_LEFT_WHEEL")
        if n == 2:
            return ("PAGE_OWNER_ONLY", "MIDDLE_LOBED_WHEEL", "second large circumtext block belongs to the middle wheel region", "the middle coarsely lobed celestial wheel", "continuation of the left wheel text", "MEDIUM", "SEPARATE_MIDDLE_WHEEL_NAMESPACE")
        if n == 3:
            return ("PAGE_OWNER_ONLY", "RIGHT_FACE_PETAL_WHEEL_AND_PROSE", "third large block belongs to the right wheel/prose panel", "the right face-centred wheel or its explanatory prose", "general introduction to the sheet", "LOW", "SEPARATE_RIGHT_WHEEL_NAMESPACE")
        return ("DIRECT_VISIBLE", "LEFT_WHEEL_RADIAL_PLACE", "exactly 28 singleton rule loci align with the visible approximately 28-place left inventory", f"left-wheel radial place {n-3:02d}", "abstract ordinal copied without celestial content", "MEDIUM", "RETAIN_28_PLACES_WITHOUT_RULE_START_OR_DIRECTION")
    raise AssertionError(page)


def main() -> None:
    fields = read(FIELD_SOURCE)
    astro_groups = read(ASTRO_SOURCE)
    by_record: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in fields:
        by_record[row["record_unit_id"]].append(row)
    first_by_record = {rows[0]["field_id"] for rows in by_record.values()}

    output: list[dict[str, str]] = []
    for row in fields:
        values = prose_owner(row, first_by_record)
        output.append(dict(zip(COLS, [
            f"R4O{len(output)+1:03d}", "PROSE_FIELD", row["page"], row["field_id"],
            row["record_unit_id"], row["locus"], *values,
        ])))

    by_locus: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in astro_groups:
        by_locus[(row["page"], row["locus"])].append(row)
    for (page, locus), group in by_locus.items():
        reduced = {
            "page": page,
            "locus": locus,
            "roles": "|".join(sorted({row["local_formal_role"] for row in group})),
        }
        values = astro_owner(reduced)
        output.append(dict(zip(COLS, [
            f"R4O{len(output)+1:03d}", "ASTRO_LOCUS", page, locus,
            group[0]["diagram_id"], locus, *values,
        ])))

    write(HERE / "V71_R4_OWNER_LEDGER.tsv", output, COLS)
    revisions = []
    for page in ["f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v"]:
        subset = [row for row in output if row["page"] == page]
        revisions.append({
            "page": page,
            "mapped_units": str(len(subset)),
            "owner_modes": ";".join(f"{k}:{v}" for k, v in sorted(Counter(r["owner_mode"] for r in subset).items())),
            "selected_revision": subset[0]["v69_revision"],
            "remaining_problem": "owner is visible but exact semantic source value remains exemplar-bound",
        })
    write(HERE / "V71_R4_REVISIONS.tsv", revisions, list(revisions[0]))

    counts = Counter(row["owner_mode"] for row in output)
    result = {
        "schema": "V71_R4_OWNER_MAP_VALIDATION_V1",
        "status": "PASS" if len(output) == 277 and len(fields) == 135 and len(by_locus) == 142 else "FAIL",
        "counts": {"rows": len(output), "prose_fields": len(fields), "astro_loci": len(by_locus), **dict(counts)},
        "sealed_pages_opened": [],
    }
    (HERE / "V71_R4_VALIDATION.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
