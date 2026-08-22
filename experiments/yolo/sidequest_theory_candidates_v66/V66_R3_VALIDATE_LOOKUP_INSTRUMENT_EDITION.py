#!/usr/bin/env python3
"""Validate the bounded V66 R3 Astro lookup-instrument release."""

from __future__ import annotations

import csv
import hashlib
import io
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
YOLO = ROOT / "experiments" / "yolo"
QUERY = ROOT / "vmanus-exp"
SOURCE_LEDGER = YOLO / "sidequest_theory_candidates_v22" / "V22_SELECTED_COMPLETE_TRANSLATION_LEDGER.tsv"
SOURCE_RULES = YOLO / "sidequest_theory_candidates_v22" / "V22_F69_28_RULES.tsv"
BUILDER = HERE / "V66_R3_BUILD_LOOKUP_INSTRUMENT_EDITION.py"

FILES = {
    "groups": (HERE / "V66_R3_395_GROUP_LOOKUP_EDITION.tsv", 395),
    "loci": (HERE / "V66_R3_142_LOCUS_FUNCTIONS.tsv", 142),
    "matrix": (HERE / "V66_R3_F67_84_VIRTUAL_LOOKUP_CELLS.tsv", 84),
    "addresses": (HERE / "V66_R3_F68_29_ADDRESS_CATALOGUE.tsv", 29),
    "rules": (HERE / "V66_R3_F69_28_TECHNICAL_RULES.tsv", 28),
    "rotations": (HERE / "V66_R3_196_ROTATION_EQUIVALENCE_VARIANTS.tsv", 196),
    "algorithms": (HERE / "V66_R3_3_LOOKUP_ALGORITHMS.tsv", 3),
    "diagrams": (HERE / "V66_R3_3_DIAGRAM_TECHNICAL_EDITION.tsv", 3),
    "costs": (HERE / "V66_R3_6_MODEL_ASSUMPTION_COSTS.tsv", 6),
}

QUERY_COLUMNS = (
    "page", "locus", "event_index", "surface", "ledger_scope",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def guarded_source() -> list[dict[str, str]]:
    command = [
        str(QUERY), "query-tsv", str(SOURCE_LEDGER),
        "--selector", "page",
        "--allow", "f67r2", "--allow", "f68r1", "--allow", "f69v",
        "--columns", ",".join(QUERY_COLUMNS),
        "--forbid-prefix", "f84",
    ]
    selected = subprocess.check_output(command, text=True)
    return list(csv.DictReader(io.StringIO(selected), delimiter="\t"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate() -> None:
    data = {name: read_tsv(path) for name, (path, _) in FILES.items()}
    for name, (_, count) in FILES.items():
        require(len(data[name]) == count, f"{name}: expected {count}, got {len(data[name])}")

    source = guarded_source()
    require(len(source) == 395, "guarded source must contain 395 Astro groups")
    require({row["ledger_scope"] for row in source} == {"ZL3B_ASTRO_VISIBLE_TOKEN"}, "source scope drift")
    require(Counter(row["page"] for row in source) == Counter({"f67r2": 190, "f68r1": 65, "f69v": 140}), "source page counts")
    require(len({(row["page"], row["locus"]) for row in source}) == 142, "source locus count")

    groups = data["groups"]
    loci = data["loci"]
    require(Counter(row["page"] for row in groups) == Counter({"f67r2": 190, "f68r1": 65, "f69v": 140}), "group page counts")
    require(Counter(row["page"] for row in loci) == Counter({"f67r2": 74, "f68r1": 37, "f69v": 31}), "locus page counts")
    require(len({row["local_group_id"] for row in groups}) == 395, "local group IDs not unique")
    require(len({row["local_locus_id"] for row in loci}) == 142, "local locus IDs not unique")
    require(all(re.fullmatch(r"A[123]:G\d{3}", row["local_group_id"]) for row in groups), "non-local group ID")
    require(all(row["diagram_id"] == {"f67r2": "A1", "f68r1": "A2", "f69v": "A3"}[row["page"]] for row in groups + loci), "page/diagram mismatch")
    forbidden_columns = {"exact_tuple_id", "source_event_serial"}
    require(not forbidden_columns.intersection(groups[0]), "prose/global ID leaked into group edition")
    require(all("GDT327_PROSE" not in "\t".join(row.values()) for row in groups), "prose scope leaked")
    require(all(row["crosspage_contract"] == "PAGE_LOCAL_ID_ONLY;NO_F68_F69_JOIN;NO_PROSE_TUPLE" for row in groups), "group crosspage contract")
    require(all(row["technical_group_role"] and row["local_lookup_address"] and row["concrete_technical_function_German"] for row in groups), "group without executable local function")

    source_projection = {(r["page"], r["locus"], r["event_index"]): r["surface"] for r in source}
    group_projection = {(r["page"], r["source_locus"], r["group_index_within_locus"]): r["surface_display_only"] for r in groups}
    require(source_projection == group_projection, "395-group source projection mismatch")

    groups_by_locus: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in groups:
        groups_by_locus[(row["page"], row["source_locus"])].append(row)
    require(set(groups_by_locus) == {(r["page"], r["source_locus"]) for r in loci}, "locus key mismatch")
    for locus in loci:
        members = groups_by_locus[(locus["page"], locus["source_locus"])]
        require(int(locus["group_count"]) == len(members), f"group count mismatch at {locus['source_locus']}")
        require(locus["local_group_ids"].split("|") == [r["local_group_id"] for r in members], f"group order mismatch at {locus['source_locus']}")
        require(locus["crosspage_contract"] == "NONE", "locus crosspage join")

    f67_loci = [r for r in loci if r["diagram_id"] == "A1"]
    require(Counter(r["instrument_component"] for r in f67_loci) == Counter({
        "COLUMN_12": 12, "ROW_7": 7, "AUX_COLUMN_12": 12,
        "CONDITION_8": 8, "INSTRUCTION_BLOCK": 35,
    }), "f67 visible selector inventory")
    matrix = data["matrix"]
    expected_cells = {f"A1:R{r:02d}:C{c:02d}" for r in range(1, 8) for c in range(1, 13)}
    require({r["virtual_cell_address"] for r in matrix} == expected_cells, "f67 7x12 cartesian matrix")
    require(all(r["visible_cell_value"] == "NONE;VIRTUAL_COMBINATION_ONLY" for r in matrix), "virtual cells presented as visible")
    require(all("NO_AUTHORIAL" in r["orientation_status"] for r in matrix), "f67 implicit origin")

    addresses = data["addresses"]
    require(Counter(r["catalogue_entry_type"] for r in addresses) == Counter({"CENTER": 1, "SPATIAL_STATION": 28}), "f68 center+28")
    require({r["source_locus"] for r in addresses if r["catalogue_entry_type"] == "SPATIAL_STATION"} == {f"f68r1.{i}" for i in range(9, 37)}, "f68 station loci")
    require(all(r["crosspage_mapping"] == "NONE" and "NO" in r["orientation_status"] for r in addresses), "f68 join/orientation")

    rules = data["rules"]
    source_rules = read_tsv(SOURCE_RULES)
    require([r["source_locus"] for r in rules] == [r["locus"] for r in source_rules], "f69 rule locus projection")
    require([r["surface_entry_display_only"] for r in rules] == [r["surface_entry"] for r in source_rules], "f69 full-entry projection")
    require(all(r["polarity_from_layout"] == "NO" and r["crosspage_alignment"] == "NONE" for r in rules), "f69 polarity/join")
    by_entry: dict[str, set[str]] = defaultdict(set)
    for row in rules:
        by_entry[row["surface_entry_display_only"]].add(row["technical_rule_German"])
    require(all(len(values) == 1 for values in by_entry.values()), "identical f69 full entry has unequal rule")
    okeod = [r for r in rules if r["surface_entry_display_only"] == "okeod"]
    require([r["editorial_rule_index"] for r in okeod] == ["11", "15", "24"] and len({r["technical_rule_German"] for r in okeod}) == 1, "okeod equality contract")

    rotations = data["rotations"]
    require(Counter(r["diagram_id"] for r in rotations) == Counter({"A1": 84, "A2": 56, "A3": 56}), "rotation orbit counts")
    require(all(r["authorial_orientation_licensed"] == "NO" and "NONE" in r["crosspage_effect"] for r in rotations), "rotation overclaim")
    require({(r["primary_offset"], r["secondary_offset"]) for r in rotations if r["diagram_id"] == "A1"} == {(str(a), str(b)) for a in range(7) for b in range(12)}, "A1 rotation variants")
    for diagram in ("A2", "A3"):
        require({(r["primary_offset"], r["traversal_sense"]) for r in rotations if r["diagram_id"] == diagram} == {(str(a), s) for a in range(28) for s in ("FORWARD", "REVERSE")}, f"{diagram} rotation variants")

    algorithms = data["algorithms"]
    require({r["diagram_id"] for r in algorithms} == {"A1", "A2", "A3"}, "algorithm coverage")
    require(all(r["deterministic_algorithm"] and r["process_graph"] for r in algorithms), "missing executable algorithm/graph")
    require(all(r["crosspage_join"] == "REJECT_UNLICENSED_F68_TO_F69_JOIN" for r in algorithms if r["diagram_id"] in {"A2", "A3"}), "algorithm accepts direct join")

    f68_forms = [r["surface_display_only"] for r in addresses if r["catalogue_entry_type"] == "SPATIAL_STATION"]
    f69_forms = [r["surface_entry_display_only"] for r in rules]
    require(sum(a == b for a, b in zip(f68_forms, f69_forms, strict=True)) == 0, "same-index f68/f69 match")
    require(set(f68_forms).isdisjoint(f69_forms), "all-pair f68/f69 match")

    costs = data["costs"]
    require(sum(int(r["weighted_cost"]) for r in costs if r["model"] == "GENERIC_WORKPLAN") == 50, "technical cost total")
    require(sum(int(r["weighted_cost"]) for r in costs if r["model"] == "MEDICAL_ELECTION_TABLE") == 137, "medical cost total")
    require(all(r["orientation_assumption"] == "0" and r["crosspage_join_assumption"] == "0" for r in costs), "hidden orientation/join cost")
    diagrams = data["diagrams"]
    require([(r["diagram_id"], int(r["locus_count"]), int(r["group_count"])) for r in diagrams] == [("A1", 74, 190), ("A2", 37, 65), ("A3", 31, 140)], "diagram summary counts")
    require(all(r["complete_technical_default_German"] and r["strongest_contradiction"] for r in diagrams), "incomplete diagram reading")
    require(all(r["direct_crosspage_mapping"] == "NONE" for r in diagrams), "summary crosspage join")

    before = {name: digest(path) for name, (path, _) in FILES.items()}
    subprocess.run([sys.executable, str(BUILDER)], cwd=HERE, check=True, stdout=subprocess.DEVNULL)
    after = {name: digest(path) for name, (path, _) in FILES.items()}
    require(before == after, "builder is not byte-deterministic")

    print("PASS V66 R3 validator")
    print("source=guarded_Astro_only; pages=3; groups=395; loci=142")
    print("f67=190/74+84_virtual; f68=65/37+29_addresses; f69=140/31+28_rules")
    print("rotations=A1:84+A2:56+A3:56=196; direct_f68_f69_join=NONE")
    print("assumption_costs=generic_workplan:50;medical_election:137; deterministic_rebuild=PASS")


if __name__ == "__main__":
    validate()
