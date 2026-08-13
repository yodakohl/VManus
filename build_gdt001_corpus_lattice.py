#!/usr/bin/env python3
"""Build the branch-local GDT001 whole-manuscript observation lattice."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
from collections import defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "experiments/semantic_assumptions/results/source_separator_transcription.tsv"
STA = ROOT / "experiments/semantic_assumptions/results/source_sta_family_consensus_loci.tsv"
OUT_JSON = ROOT / "gdt001_corpus_lattice.json"
OUT_TSV = ROOT / "gdt001_corpus_lattice.tsv"
EDITION_ORDER = ("ZL3b", "IT2a", "RF1b")
SEPARATORS = (
    "LINE_START",
    "LINE_END",
    "DEFINITE_SPACE",
    "UNCERTAIN_SMALL_SPACE",
    "DRAWING_INTERRUPTION",
    "DRAWING_INTERRUPTION_UNALIGNED",
)
META = ("page", "section", "currier", "hand", "code", "kind", "grammar_scope")
GROUP_FIELDS = (
    "source_group_index",
    "source_group_count",
    "paragraph_start",
    "paragraph_end",
    "left_separator",
    "right_separator",
    "ivtff_group_raw",
    "clean_ascii_fragments",
    "clean_ascii_fragment_count",
    "legacy_surface_positions_1based",
    "legacy_interlinear_row_present",
    "legacy_mapping_status",
)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def canonical(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def parse_int(value: str) -> int:
    if not value or not value.isdigit():
        raise ValueError(f"expected unsigned integer, received {value!r}")
    return int(value)


def csv_list(value: str) -> list[int]:
    if not value:
        return []
    return [parse_int(item) for item in value.split(",")]


def physical_folio(page: str) -> str:
    match = re.match(r"^(f\d+)", page)
    return match.group(1) if match else page


def group_projection(row: dict[str, str]) -> dict[str, Any]:
    fragments = [] if not row["clean_ascii_fragments"] else row["clean_ascii_fragments"].split()
    group = {
        "source_group_index": parse_int(row["source_group_index"]),
        "source_group_count": parse_int(row["source_group_count"]),
        "paragraph_start": bool(parse_int(row["paragraph_start"])),
        "paragraph_end": bool(parse_int(row["paragraph_end"])),
        "left_separator": row["left_separator"],
        "right_separator": row["right_separator"],
        "ivtff_group_raw": row["ivtff_group_raw"],
        "clean_ascii_fragments": fragments,
        "legacy_surface_positions_1based": csv_list(row["legacy_surface_positions_1based"]),
        "legacy_interlinear_row_present": bool(parse_int(row["legacy_interlinear_row_present"])),
        "legacy_mapping_status": row["legacy_mapping_status"],
    }
    if row["left_separator"] not in SEPARATORS or row["right_separator"] not in SEPARATORS:
        raise ValueError("unknown separator")
    if len(fragments) != parse_int(row["clean_ascii_fragment_count"]):
        raise ValueError("fragment count mismatch")
    if group["source_group_index"] < 1 or group["source_group_index"] > group["source_group_count"]:
        raise ValueError("group index out of bounds")
    return group


def read_source() -> tuple[dict[str, dict[str, list[dict[str, Any]]]], dict[str, dict[str, str]]]:
    by_locus: dict[str, dict[str, list[dict[str, Any]]]] = defaultdict(lambda: defaultdict(list))
    metadata: dict[str, dict[str, str]] = {}
    seen_ids: set[str] = set()
    with SOURCE.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        expected = {
            "source_group_id", "edition", "locus", *META, "source_row_index", *GROUP_FIELDS,
        }
        if set(reader.fieldnames or ()) != expected:
            raise ValueError("source atlas schema mismatch")
        for row in reader:
            identifier = row["source_group_id"]
            if identifier in seen_ids:
                raise ValueError(f"duplicate source group: {identifier}")
            seen_ids.add(identifier)
            if row["edition"] not in EDITION_ORDER:
                raise ValueError("unknown edition")
            locus = row["locus"]
            meta = {field: row[field] for field in META}
            if locus in metadata and metadata[locus] != meta:
                raise ValueError(f"metadata disagreement across editions at {locus}")
            metadata[locus] = meta
            by_locus[locus][row["edition"]].append(group_projection(row))
    for locus, editions in by_locus.items():
        for edition, groups in editions.items():
            groups.sort(key=lambda group: group["source_group_index"])
            if [g["source_group_index"] for g in groups] != list(range(1, len(groups) + 1)):
                raise ValueError(f"noncontiguous groups at {edition}:{locus}")
            if any(g["source_group_count"] != len(groups) for g in groups):
                raise ValueError(f"group-count drift at {edition}:{locus}")
            if groups[0]["left_separator"] != "LINE_START" or groups[-1]["right_separator"] != "LINE_END":
                raise ValueError(f"line boundary drift at {edition}:{locus}")
            for left, right in zip(groups, groups[1:]):
                if left["right_separator"] != right["left_separator"]:
                    raise ValueError(f"separator adjacency drift at {edition}:{locus}")
    return by_locus, metadata


def read_sta() -> dict[str, dict[str, Any]]:
    integer_fields = {"symbol_count", "alternative_sites", "strict_zero_alternative"}
    list_fields = {
        "zl_sta_codes", "it_sta_codes", "rf_sta_codes",
        "union_boundary_positions", "synchronized_boundary_positions",
        "three_reading_boundary_positions", "two_reading_boundary_positions",
        "one_reading_boundary_positions",
    }
    retained = (
        "symbol_count", "family_sequence", "zl_sta_codes", "it_sta_codes", "rf_sta_codes",
        "alternative_sites", "strict_zero_alternative", "union_boundary_positions",
        "synchronized_boundary_positions", "three_reading_boundary_positions",
        "two_reading_boundary_positions", "one_reading_boundary_positions",
        "exact_boundary_position_sets", "exact_typed_boundary_maps",
    )
    output: dict[str, dict[str, Any]] = {}
    with STA.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        for row in reader:
            locus = row["locus"]
            if locus in output:
                raise ValueError(f"duplicate STA locus {locus}")
            item: dict[str, Any] = {}
            for field in retained:
                value: Any = row[field]
                if field in integer_fields:
                    value = parse_int(value)
                elif field in list_fields:
                    value = [] if not value else value.split() if "positions" not in field else csv_list(value)
                elif field.startswith("exact_"):
                    value = bool(parse_int(value))
                item[field] = value
            output[locus] = item
    return output


def make_lattice() -> dict[str, Any]:
    by_locus, metadata = read_source()
    sta = read_sta()
    lines = []
    unique_paths = 0
    collapsed_edition_paths = 0
    raw_groups = 0
    modeled_fragments = 0
    for locus in sorted(by_locus):
        paths: dict[bytes, dict[str, Any]] = {}
        for edition in EDITION_ORDER:
            if edition not in by_locus[locus]:
                continue
            groups = by_locus[locus][edition]
            raw_groups += len(groups)
            modeled_fragments += sum(len(group["clean_ascii_fragments"]) for group in groups)
            key = canonical(groups)
            if key not in paths:
                paths[key] = {"edition_support": [], "groups": groups}
            paths[key]["edition_support"].append(edition)
        ordered = sorted(paths.values(), key=lambda p: tuple(EDITION_ORDER.index(e) for e in p["edition_support"]))
        path_count = len(ordered)
        choice_bits = format(math.log2(path_count), ".12f")
        alternatives = []
        for index, path in enumerate(ordered, 1):
            payload = canonical(path["groups"])
            alternatives.append({
                "path_id": f"{locus}|P{index:02d}",
                "path_sha256": hashlib.sha256(payload).hexdigest(),
                "edition_support": path["edition_support"],
                "observation_choice_bits": choice_bits,
                "groups": path["groups"],
            })
        unique_paths += path_count
        collapsed_edition_paths += sum(len(path["edition_support"]) - 1 for path in alternatives)
        meta = metadata[locus]
        lines.append({
            "line_id": locus,
            "locus": locus,
            **meta,
            "available_editions": [edition for edition in EDITION_ORDER if edition in by_locus[locus]],
            "unique_path_count": path_count,
            "observation_choice_bits": choice_bits,
            "alternatives": alternatives,
            "sta_alignment": sta.get(locus),
        })
    if set(sta) - set(by_locus):
        raise ValueError("STA loci absent from source atlas")
    return {
        "schema": "GDT001_CORPUS_LATTICE_V1",
        "status": "EXPLORATORY_BRANCH_INPUT",
        "branch": "yolo/gdt001-global-decipherment",
        "base_commit": "f68381e519ee4f739f8003f1354d49691fab2db2",
        "inputs": {
            str(SOURCE.relative_to(ROOT)): {"sha256": sha256(SOURCE), "bytes": SOURCE.stat().st_size},
            str(STA.relative_to(ROOT)): {"sha256": sha256(STA), "bytes": STA.stat().st_size},
        },
        "edition_order": list(EDITION_ORDER),
        "separator_states": list(SEPARATORS),
        "observation_code": {
            "unit": "whole physical line",
            "path_equivalence": "byte-identical canonical projected group sequences collapse across editions",
            "choice_cost": "log2(unique_path_count) bits for a selected line path",
            "raw_channel": "ivtff_group_raw and legacy cleaner provenance retained exactly; model scores must price raw residuals",
            "editions_are_replications": False,
        },
        "counts": {
            "physical_lines": len(lines),
            "pages": len({line["page"] for line in lines}),
            "physical_folios": len({physical_folio(line["page"]) for line in lines}),
            "source_group_rows": raw_groups,
            "unique_line_paths": unique_paths,
            "collapsed_duplicate_edition_paths": collapsed_edition_paths,
            "modeled_ascii_fragments": modeled_fragments,
            "sta_aligned_lines": sum(line["sta_alignment"] is not None for line in lines),
        },
        "lines": lines,
        "claim_ceiling": "Exploratory full-manuscript manual-observation lattice; no selected reading, language, cipher, plaintext, meaning, or confirmed translation.",
    }


def tsv_bytes(lattice: dict[str, Any]) -> bytes:
    fields = [
        "path_id", "locus", *META, "available_editions", "edition_support",
        "unique_path_count", "observation_choice_bits", "path_sha256", "group_count",
        "ivtff_groups_json", "clean_fragments_json", "separator_path_json", "sta_alignment_present",
    ]
    import io
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields, delimiter="\t", lineterminator="\n")
    writer.writeheader()
    for line in lattice["lines"]:
        for path in line["alternatives"]:
            groups = path["groups"]
            writer.writerow({
                "path_id": path["path_id"],
                "locus": line["locus"],
                **{field: line[field] for field in META},
                "available_editions": ",".join(line["available_editions"]),
                "edition_support": ",".join(path["edition_support"]),
                "unique_path_count": line["unique_path_count"],
                "observation_choice_bits": path["observation_choice_bits"],
                "path_sha256": path["path_sha256"],
                "group_count": len(groups),
                "ivtff_groups_json": json.dumps([g["ivtff_group_raw"] for g in groups], ensure_ascii=False, separators=(",", ":")),
                "clean_fragments_json": json.dumps([g["clean_ascii_fragments"] for g in groups], ensure_ascii=False, separators=(",", ":")),
                "separator_path_json": json.dumps([[g["left_separator"], g["right_separator"]] for g in groups], separators=(",", ":")),
                "sta_alignment_present": int(line["sta_alignment"] is not None),
            })
    return output.getvalue().encode("utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    lattice = make_lattice()
    json_data = canonical(lattice)
    tsv_data = tsv_bytes(lattice)
    if args.check_only:
        print(json.dumps({"json_sha256": hashlib.sha256(json_data).hexdigest(), "tsv_sha256": hashlib.sha256(tsv_data).hexdigest(), **lattice["counts"]}, sort_keys=True))
        return
    for path in (OUT_JSON, OUT_TSV):
        if path.exists() and not args.force:
            raise FileExistsError(path)
    OUT_JSON.write_bytes(json_data)
    OUT_TSV.write_bytes(tsv_data)
    print(json.dumps({"json_sha256": sha256(OUT_JSON), "tsv_sha256": sha256(OUT_TSV), **lattice["counts"]}, sort_keys=True))


if __name__ == "__main__":
    main()
