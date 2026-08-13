#!/usr/bin/env python3
"""Independent integrity and reconstruction validator for the GDT001 lattice."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "experiments/semantic_assumptions/results/source_separator_transcription.tsv"
STA = ROOT / "experiments/semantic_assumptions/results/source_sta_family_consensus_loci.tsv"
LATTICE = ROOT / "gdt001_corpus_lattice.json"
FLAT = ROOT / "gdt001_corpus_lattice.tsv"
EDITIONS = ("ZL3b", "IT2a", "RF1b")
SEPARATORS = {
    "LINE_START", "LINE_END", "DEFINITE_SPACE", "UNCERTAIN_SMALL_SPACE",
    "DRAWING_INTERRUPTION", "DRAWING_INTERRUPTION_UNALIGNED",
}


def need(condition: bool, label: str, checks: list[str]) -> None:
    if not condition:
        raise AssertionError(label)
    checks.append(label)


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def strict_json(path: Path) -> tuple[Any, bytes]:
    raw = path.read_bytes()

    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in items:
            if key in result:
                raise ValueError(f"duplicate JSON key: {key}")
            result[key] = value
        return result

    value = json.loads(
        raw.decode("utf-8"), object_pairs_hook=pairs,
        parse_constant=lambda token: (_ for _ in ()).throw(ValueError(token)),
    )
    canonical = (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
    if canonical != raw:
        raise AssertionError("lattice JSON is not canonical")
    return value, raw


def canonical(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()


def unsigned(value: str) -> int:
    if not value.isdigit():
        raise AssertionError(f"not an unsigned integer: {value!r}")
    return int(value)


def source_projection(row: dict[str, str]) -> dict[str, Any]:
    fragments = row["clean_ascii_fragments"].split() if row["clean_ascii_fragments"] else []
    positions = [unsigned(item) for item in row["legacy_surface_positions_1based"].split(",")] if row["legacy_surface_positions_1based"] else []
    return {
        "source_group_index": unsigned(row["source_group_index"]),
        "source_group_count": unsigned(row["source_group_count"]),
        "paragraph_start": bool(unsigned(row["paragraph_start"])),
        "paragraph_end": bool(unsigned(row["paragraph_end"])),
        "left_separator": row["left_separator"],
        "right_separator": row["right_separator"],
        "ivtff_group_raw": row["ivtff_group_raw"],
        "clean_ascii_fragments": fragments,
        "legacy_surface_positions_1based": positions,
        "legacy_interlinear_row_present": bool(unsigned(row["legacy_interlinear_row_present"])),
        "legacy_mapping_status": row["legacy_mapping_status"],
    }


def flatten_json(lattice: dict[str, Any]) -> list[dict[str, str]]:
    output: list[dict[str, str]] = []
    for line in lattice["lines"]:
        for path in line["alternatives"]:
            groups = path["groups"]
            output.append({
                "path_id": path["path_id"], "locus": line["locus"],
                "page": line["page"], "section": line["section"], "currier": line["currier"],
                "hand": line["hand"], "code": line["code"], "kind": line["kind"],
                "grammar_scope": line["grammar_scope"],
                "available_editions": ",".join(line["available_editions"]),
                "edition_support": ",".join(path["edition_support"]),
                "unique_path_count": str(line["unique_path_count"]),
                "observation_choice_bits": path["observation_choice_bits"],
                "path_sha256": path["path_sha256"], "group_count": str(len(groups)),
                "ivtff_groups_json": json.dumps([g["ivtff_group_raw"] for g in groups], ensure_ascii=False, separators=(",", ":")),
                "clean_fragments_json": json.dumps([g["clean_ascii_fragments"] for g in groups], ensure_ascii=False, separators=(",", ":")),
                "separator_path_json": json.dumps([[g["left_separator"], g["right_separator"]] for g in groups], separators=(",", ":")),
                "sta_alignment_present": str(int(line["sta_alignment"] is not None)),
            })
    return output


def main() -> None:
    checks: list[str] = []
    lattice, raw = strict_json(LATTICE)
    need(lattice["schema"] == "GDT001_CORPUS_LATTICE_V1", "schema", checks)
    need(lattice["status"] == "EXPLORATORY_BRANCH_INPUT", "exploratory_status", checks)
    need(lattice["branch"] == "yolo/gdt001-global-decipherment", "branch_binding", checks)
    need(lattice["base_commit"] == "f68381e519ee4f739f8003f1354d49691fab2db2", "base_commit_binding", checks)
    expected_inputs = {
        str(SOURCE.relative_to(ROOT)): {"sha256": digest(SOURCE), "bytes": SOURCE.stat().st_size},
        str(STA.relative_to(ROOT)): {"sha256": digest(STA), "bytes": STA.stat().st_size},
    }
    need(lattice["inputs"] == expected_inputs, "input_hashes_and_sizes", checks)
    need(lattice["edition_order"] == list(EDITIONS), "edition_order", checks)
    need(set(lattice["separator_states"]) == SEPARATORS and len(lattice["separator_states"]) == 6, "separator_vocabulary", checks)
    need(lattice["observation_code"]["choice_cost"] == "log2(unique_path_count) bits for a selected line path", "choice_cost_rule", checks)
    need(lattice["observation_code"]["editions_are_replications"] is False, "alternate_not_replication", checks)

    source: dict[str, dict[str, list[dict[str, Any]]]] = defaultdict(lambda: defaultdict(list))
    source_meta: dict[str, dict[str, str]] = {}
    edition_counts: Counter[str] = Counter()
    seen: set[str] = set()
    fragment_count = 0
    with SOURCE.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            identifier = row["source_group_id"]
            if identifier in seen:
                raise AssertionError("duplicate source group")
            seen.add(identifier)
            edition_counts[row["edition"]] += 1
            group = source_projection(row)
            fragment_count += len(group["clean_ascii_fragments"])
            if {group["left_separator"], group["right_separator"]} - SEPARATORS:
                raise AssertionError("unknown source separator")
            source[row["locus"]][row["edition"]].append(group)
            meta = {field: row[field] for field in ("page", "section", "currier", "hand", "code", "kind", "grammar_scope")}
            if row["locus"] in source_meta and source_meta[row["locus"]] != meta:
                raise AssertionError("source metadata mismatch")
            source_meta[row["locus"]] = meta
    need(edition_counts == Counter({"ZL3b": 39026, "IT2a": 37919, "RF1b": 38525}), "edition_source_counts", checks)
    need(len(seen) == 115470 and len(source) == 5386, "source_group_and_line_counts", checks)
    need(fragment_count == 118011, "modeled_fragment_count", checks)

    sta_loci: set[str] = set()
    with STA.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["locus"] in sta_loci:
                raise AssertionError("duplicate STA locus")
            sta_loci.add(row["locus"])
    need(len(sta_loci) == 3934 and not (sta_loci - set(source)), "sta_alignment_coverage", checks)

    lines = lattice["lines"]
    need([line["locus"] for line in lines] == sorted(source), "canonical_line_order", checks)
    unique_paths = 0
    collapsed = 0
    for line in lines:
        locus = line["locus"]
        need_line = source[locus]
        if any(line[field] != source_meta[locus][field] for field in source_meta[locus]):
            raise AssertionError(f"line metadata mismatch: {locus}")
        available = [edition for edition in EDITIONS if edition in need_line]
        if line["available_editions"] != available:
            raise AssertionError(f"edition availability mismatch: {locus}")
        groups_by_digest: dict[bytes, list[str]] = {}
        for edition in available:
            groups = sorted(need_line[edition], key=lambda group: group["source_group_index"])
            if [g["source_group_index"] for g in groups] != list(range(1, len(groups) + 1)):
                raise AssertionError("noncontiguous source groups")
            if groups[0]["left_separator"] != "LINE_START" or groups[-1]["right_separator"] != "LINE_END":
                raise AssertionError("source line edges")
            key = canonical(groups)
            groups_by_digest.setdefault(key, []).append(edition)
        expected_paths = sorted(groups_by_digest.items(), key=lambda item: tuple(EDITIONS.index(e) for e in item[1]))
        if line["unique_path_count"] != len(expected_paths):
            raise AssertionError(f"path count mismatch: {locus}")
        choice = format(math.log2(len(expected_paths)), ".12f")
        if line["observation_choice_bits"] != choice:
            raise AssertionError(f"choice bits mismatch: {locus}")
        if (line["sta_alignment"] is not None) != (locus in sta_loci):
            raise AssertionError(f"STA presence mismatch: {locus}")
        if len(line["alternatives"]) != len(expected_paths):
            raise AssertionError("alternative cardinality")
        for index, (payload, support) in enumerate(expected_paths, 1):
            actual = line["alternatives"][index - 1]
            if actual["path_id"] != f"{locus}|P{index:02d}" or actual["edition_support"] != support:
                raise AssertionError(f"path identity mismatch: {locus}")
            if actual["observation_choice_bits"] != choice:
                raise AssertionError("alternative choice bits")
            if actual["path_sha256"] != hashlib.sha256(payload).hexdigest():
                raise AssertionError(f"path hash mismatch: {locus}")
            if canonical(actual["groups"]) != payload:
                raise AssertionError(f"path groups mismatch: {locus}")
        unique_paths += len(expected_paths)
        collapsed += len(available) - len(expected_paths)
    need(unique_paths == 12713 and collapsed == 3272, "reconstructed_path_counts", checks)
    expected_counts = {
        "physical_lines": 5386, "pages": 227, "physical_folios": 103,
        "source_group_rows": 115470, "unique_line_paths": 12713,
        "collapsed_duplicate_edition_paths": 3272, "modeled_ascii_fragments": 118011,
        "sta_aligned_lines": 3934,
    }
    need(lattice["counts"] == expected_counts, "published_counts", checks)

    expected_flat = flatten_json(lattice)
    with FLAT.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        actual_flat = list(reader)
    need(actual_flat == expected_flat, "tsv_exact_flattening", checks)
    need(raw == LATTICE.read_bytes(), "canonical_duplicate_free_json", checks)
    print(json.dumps({
        "status": "PASS", "checks": checks, "check_count": len(checks),
        "lattice_sha256": digest(LATTICE), "tsv_sha256": digest(FLAT),
        "physical_lines": 5386, "unique_line_paths": 12713,
        "claim_ceiling": lattice["claim_ceiling"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
