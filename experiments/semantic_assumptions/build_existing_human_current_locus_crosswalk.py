#!/usr/bin/env python3
"""Crosswalk legacy human label/title records to current IVTFF loci.

The unit of assignment is a physical legacy location, not a transcription
record.  This matters because the 1998 source contains U- and V-coded
transcriptions for
the same twenty f75v locations.  Three provenance-declared mapping layers are
used, in descending priority:

1. a unique human Grove-number plus ring-scope key shared by both sources;
2. a strongly separated whole-group sequence alignment through Stolfi's
   explicit EVMT-to-integer locator table;
3. conservative page-local string assignment across physical locations.

Object identities, grammar, English meaning, image pixels, OCR, and automated
vision never enter the mapping.  Repeated texts at distinct physical
locations are retained as real repetitions; unresolved repetitions stay
ambiguous rather than being discarded.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import re
import sys
import time
from collections import Counter, defaultdict
from itertools import chain
from pathlib import Path
from typing import Any, Iterable

import numpy as np
from rapidfuzz.fuzz import ratio
from scipy.optimize import linear_sum_assignment


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
TRANSCRIPTION = ROOT / "transcription"
sys.path.insert(0, str(TRANSCRIPTION))
from export_transcription import parse_edition  # noqa: E402

LABEL_INDEX = HERE / "cache" / "existing_human_annotations" / "labtit-best.idx"
LABEL_FORMAT_URL = "https://www.ic.unicamp.br/en/~stolfi/EXPORT/voynich/98-02-01-lotsa-labels/"
LABEL_ANNOTATIONS = RESULTS / "existing_human_label_annotations.tsv"
EXACT_ANNOTATIONS = RESULTS / "existing_human_exact_locus_annotations.tsv"
LOCUS_ROLES = RESULTS / "existing_human_locus_roles.tsv"
PAGE_ANNOTATIONS = RESULTS / "existing_human_page_annotations.tsv"
PAGE_CENSUS = RESULTS / "document_role_page_census.tsv"
STOLFI_LINES = TRANSCRIPTION / "voynich_stolfi25e1_lines.tsv"
EDITION_PATHS = {
    "ZL3b": TRANSCRIPTION / "sources" / "ZL3b-n.txt",
    "IT2a": TRANSCRIPTION / "sources" / "IT2a-n.txt",
    "RF1b": TRANSCRIPTION / "sources" / "RF1b-e.txt",
}

CROSSWALK_OUT = RESULTS / "existing_human_current_locus_crosswalk.tsv"
LABEL_MATRIX_OUT = RESULTS / "existing_human_source_role_matrix.tsv"
PAGE_MATRIX_OUT = RESULTS / "existing_human_page_role_matrix.tsv"
MANIFEST_OUT = RESULTS / "existing_human_current_locus_crosswalk.json"
REPORT_OUT = RESULTS / "existing_human_current_locus_crosswalk_report.md"

PAGE_ALIASES = {"f101v1": "f101v", "f101v2": "f101v", "f86r4": "fros"}
MIN_RATIO = 0.84
HIGH_RATIO = 0.94
MIN_MARGIN = 0.08
SEQUENCE_MIN_MEAN = 0.82
CLEAR_STATUSES = {
    "EXPLICIT_HUMAN_POSITION_KEY",
    "SEQUENCE_GROUP_POSITION",
    "EXACT_UNIQUE",
    "HIGH_RATIO_UNIQUE",
    "MARGINED_RATIO",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalized(value: str) -> str:
    return "".join(re.findall(r"[a-z]+", value.lower()))


def natural_key(value: str) -> tuple[tuple[int, Any], ...]:
    return tuple(
        (0, int(part)) if part.isdigit() else (1, part.lower())
        for part in re.split(r"(\d+)", value)
        if part
    )


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, fields: list[str], rows: Iterable[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def parse_label_source() -> list[dict[str, Any]]:
    annotations = {row["source_record_id"]: row for row in read_tsv(LABEL_ANNOTATIONS)}
    output = []
    for raw_line in LABEL_INDEX.read_text(encoding="utf-8").splitlines():
        fields = raw_line.split("|")
        if len(fields) != 11:
            raise ValueError("legacy label index does not have eleven fields")
        (
            source_id, source_section, source_page, source_unit, source_item,
            source_transcriber_code, source_text, alternate_text, object_class,
            object_guess, comments,
        ) = fields
        record_id = f"STOLFI_BEST_{source_id}"
        annotation = annotations[record_id]
        page_lower = source_page.lower()
        location = f"{source_page}.{source_unit}.{source_item}".lower()
        output.append({
            "source_record_id": record_id,
            "source_section": source_section,
            "source_page": page_lower,
            "current_page_key": PAGE_ALIASES.get(page_lower, page_lower),
            "legacy_alias_applied": int(page_lower in PAGE_ALIASES),
            "source_unit": source_unit.lower(),
            "source_item": source_item.lower(),
            "source_location": location,
            "source_physical_location_id": location,
            "source_transcriber_code": source_transcriber_code,
            "source_text": source_text,
            "source_alternate_text": alternate_text,
            "source_normalized": normalized(source_text),
            "source_object_class": object_class,
            "source_object_guess": object_guess,
            "source_comments": comments,
            "source_attribute_tags": annotation["attribute_tags"],
            "source_certainty": annotation["certainty"],
        })
    return output


def cluster_sources(sources: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    for source in sources:
        grouped[source["source_physical_location_id"]].append(source)
    output = []
    for location, records in grouped.items():
        first = records[0]
        if len({(r["source_page"], r["source_unit"], r["source_item"]) for r in records}) != 1:
            raise ValueError(f"mixed physical source location {location}")
        output.append({
            "cluster_id": location,
            "source_page": first["source_page"],
            "current_page_key": first["current_page_key"],
            "source_unit": first["source_unit"],
            "source_item": first["source_item"],
            "source_norms": {r["source_normalized"] for r in records if r["source_normalized"]},
            "records": sorted(records, key=lambda r: r["source_transcriber_code"]),
        })
    return sorted(output, key=lambda c: min(int(r["source_record_id"].rsplit("_", 1)[1]) for r in c["records"]))


def load_current_loci() -> tuple[dict[str, list[dict[str, Any]]], dict[str, dict[str, Any]]]:
    by_edition: dict[str, dict[str, dict[str, Any]]] = {}
    for edition, path in EDITION_PATHS.items():
        _pages, lines = parse_edition(path, edition)
        by_edition[edition] = {
            line.locus.lower(): {
                "page": line.page,
                "locus": line.locus,
                "code": line.code,
                "text": " ".join(line.clean_words),
            }
            for line in lines
        }
    by_page: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    by_locus: dict[str, dict[str, Any]] = {}
    for locus, zl in by_edition["ZL3b"].items():
        readings = {edition: by_edition[edition].get(locus, {}).get("text", "") for edition in EDITION_PATHS}
        item = {
            "current_page": zl["page"],
            "current_locus": zl["locus"],
            "current_code": zl["code"],
            "current_kind": zl["code"][1:2],
            "current_subtype": zl["code"][2:3],
            "readings": readings,
            "normalized_readings": {normalized(text) for text in readings.values() if normalized(text)},
        }
        by_locus[locus] = item
        by_page[zl["page"].lower()].append(item)
    # Five editorial loci contain no clean Voynich token and are consequently
    # absent from parse_edition.  They still are real current physical loci and
    # can be the target of an explicit human position key (for example the
    # deliberately missing f72r2 zodiac label).
    for role in read_tsv(LOCUS_ROLES):
        locus = role["locus"].lower()
        if locus in by_locus:
            continue
        item = {
            "current_page": role["page"],
            "current_locus": role["locus"],
            "current_code": role["code"],
            "current_kind": role["kind"],
            "current_subtype": role["subtype"],
            "readings": {edition: "" for edition in EDITION_PATHS},
            "normalized_readings": set(),
        }
        by_locus[locus] = item
        by_page[role["page"].lower()].append(item)
    for rows in by_page.values():
        rows.sort(key=lambda row: int(row["current_locus"].rsplit(".", 1)[1]))
    return dict(by_page), by_locus


def pair_score(source_norms: set[str], target_norms: set[str]) -> float:
    return max((ratio(a, b) / 100.0 for a in source_norms for b in target_norms), default=0.0)


def human_scope(value: str) -> str:
    lowered = value.lower()
    if "not in circle" in lowered or "outside diagram" in lowered:
        return "OUTSIDE"
    if "outer" in lowered:
        return "OUTER"
    if "inner" in lowered:
        return "INNER"
    if "middle" in lowered:
        return "MIDDLE"
    return ""


def grove_number(value: str, require_grove: bool = False) -> int | None:
    pattern = r"grove's\s*#\s*(\d+)" if require_grove else r"#\s*(\d+)"
    match = re.search(pattern, value, re.I)
    return int(match.group(1)) if match else None


def explicit_position_mappings(clusters: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    index: defaultdict[tuple[str, str, int], set[str]] = defaultdict(set)
    for row in read_tsv(EXACT_ANNOTATIONS):
        scope = human_scope(row["unit_description"] + " " + row["local_comment"])
        number = grove_number(row["local_comment"], require_grove=True)
        if scope and number is not None:
            index[(row["page"].lower(), scope, number)].add(row["locus"].lower())
    output = {}
    for cluster in clusters:
        keys = set()
        for record in cluster["records"]:
            scope = human_scope(record["source_comments"])
            number = grove_number(record["source_comments"])
            if scope and number is not None:
                keys.add((cluster["current_page_key"], scope, number))
        targets = set(chain.from_iterable(index[key] for key in keys if len(index[key]) == 1))
        if len(keys) == 1 and len(targets) == 1:
            key = next(iter(keys))
            output[cluster["cluster_id"]] = {
                "current_locus": next(iter(targets)),
                "position_key": f"{key[1]}:GROVE_{key[2]}",
            }
    return output


def load_locator_groups(by_locus: dict[str, dict[str, Any]]) -> dict[tuple[str, str], list[dict[str, Any]]]:
    groups: defaultdict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in read_tsv(STOLFI_LINES):
        target = by_locus.get(row["locus"].lower())
        match = re.match(r"[^.]+\.([^.]+)\.(.+)$", row["old_locus"].lower())
        if target is None or match is None:
            continue
        old_unit, old_item = match.groups()
        sequence_norms = set(target["normalized_readings"])
        if normalized(row["clean_text"]):
            sequence_norms.add(normalized(row["clean_text"]))
        groups[(target["current_page"].lower(), old_unit)].append({
            **target,
            "old_unit": old_unit,
            "old_item": old_item,
            "sequence_norms": sequence_norms,
        })
    for rows in groups.values():
        rows.sort(key=lambda row: natural_key(row["old_item"]))
    return dict(groups)


def sequence_mappings(
    clusters: list[dict[str, Any]],
    target_groups: dict[tuple[str, str], list[dict[str, Any]]],
) -> tuple[dict[str, dict[str, Any]], list[dict[str, Any]]]:
    source_groups: defaultdict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for cluster in clusters:
        source_groups[(cluster["current_page_key"], cluster["source_page"], cluster["source_unit"])].append(cluster)
    for rows in source_groups.values():
        rows.sort(key=lambda row: natural_key(row["source_item"]))
    mappings: dict[str, dict[str, Any]] = {}
    summaries = []
    for source_key, source_rows in sorted(source_groups.items()):
        size = len(source_rows)
        if size < 3:
            continue
        candidates = []
        for (page, target_unit), target_rows in target_groups.items():
            if page != source_key[0] or len(target_rows) != size:
                continue
            for reversed_order in (False, True):
                oriented = list(reversed(target_rows)) if reversed_order else target_rows
                for rotation in range(size):
                    aligned = oriented[rotation:] + oriented[:rotation]
                    scores = [pair_score(source["source_norms"], target["sequence_norms"]) for source, target in zip(source_rows, aligned)]
                    exact_count = sum(bool(source["source_norms"] & target["sequence_norms"]) for source, target in zip(source_rows, aligned))
                    candidates.append({
                        "mean_ratio": sum(scores) / size,
                        "exact_count": exact_count,
                        "target_unit": target_unit,
                        "reversed": reversed_order,
                        "rotation": rotation,
                        "aligned": aligned,
                    })
        if len(candidates) < 2:
            continue
        candidates.sort(key=lambda row: (row["mean_ratio"], row["exact_count"]), reverse=True)
        best, runner = candidates[:2]
        margin = best["mean_ratio"] - runner["mean_ratio"]
        exact_gate = max(3, math.ceil(0.75 * size))
        strong = (
            best["exact_count"] >= 2
            and best["mean_ratio"] >= SEQUENCE_MIN_MEAN
            and (
                margin >= MIN_MARGIN
                or (best["exact_count"] >= exact_gate and best["exact_count"] - runner["exact_count"] >= 2)
            )
        )
        if not strong:
            continue
        summary = {
            "source_page": source_key[1],
            "source_unit": source_key[2],
            "current_page_key": source_key[0],
            "source_group_size": size,
            "target_old_unit": best["target_unit"],
            "sequence_reversed": int(best["reversed"]),
            "sequence_rotation": best["rotation"],
            "sequence_mean_ratio": best["mean_ratio"],
            "sequence_exact_count": best["exact_count"],
            "sequence_runner_mean_ratio": runner["mean_ratio"],
            "sequence_group_margin": margin,
        }
        summaries.append(summary)
        for source, target in zip(source_rows, best["aligned"]):
            mappings[source["cluster_id"]] = {
                **summary,
                "current_locus": target["current_locus"].lower(),
            }
    return mappings, summaries


def string_mappings(
    clusters: list[dict[str, Any]],
    current_by_page: dict[str, list[dict[str, Any]]],
    blocked_clusters: set[str],
    blocked_targets: set[str],
) -> dict[str, dict[str, Any]]:
    all_clusters_by_page: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    for cluster in clusters:
        all_clusters_by_page[cluster["current_page_key"]].append(cluster)
    output: dict[str, dict[str, Any]] = {}
    for page, all_clusters in all_clusters_by_page.items():
        all_targets = current_by_page.get(page, [])
        candidates = [c for c in all_clusters if c["cluster_id"] not in blocked_clusters and c["source_norms"]]
        targets = [t for t in all_targets if t["current_locus"].lower() not in blocked_targets]
        assigned: dict[str, tuple[int, int, np.ndarray]] = {}
        if candidates and targets:
            matrix = np.asarray([[pair_score(c["source_norms"], t["normalized_readings"]) for t in targets] for c in candidates], dtype=np.float64)
            rr, cc = linear_sum_assignment(-matrix)
            for i, j in zip(rr, cc):
                assigned[candidates[int(i)]["cluster_id"]] = (int(i), int(j), matrix)
        for cluster in all_clusters:
            if cluster["cluster_id"] in blocked_clusters:
                continue
            if not cluster["source_norms"]:
                output[cluster["cluster_id"]] = {"match_status": "NO_SOURCE_STRING", "primary_eligible": 0}
                continue
            assignment = assigned.get(cluster["cluster_id"])
            if assignment is None:
                output[cluster["cluster_id"]] = {"match_status": "NO_CURRENT_PAGE_OR_ASSIGNMENT", "primary_eligible": 0}
                continue
            i, j, matrix = assignment
            target = targets[j]
            value = float(matrix[i, j])
            row_other = np.delete(matrix[i], j)
            column_other = np.delete(matrix[:, j], i)
            row_second = float(row_other.max()) if len(row_other) else 0.0
            column_second = float(column_other.max()) if len(column_other) else 0.0
            margin = value - max(row_second, column_second)
            exact = bool(cluster["source_norms"] & target["normalized_readings"])
            source_exact_target_count = sum(bool(cluster["source_norms"] & t["normalized_readings"]) for t in all_targets)
            target_exact_cluster_count = sum(bool(c["source_norms"] & target["normalized_readings"]) for c in all_clusters)
            if exact:
                status = "EXACT_UNIQUE" if source_exact_target_count == target_exact_cluster_count == 1 else "EXACT_REPEAT_AMBIGUOUS"
            elif value >= HIGH_RATIO and margin >= MIN_MARGIN:
                status = "HIGH_RATIO_UNIQUE"
            elif value >= MIN_RATIO and margin >= MIN_MARGIN:
                status = "MARGINED_RATIO"
            else:
                status = "AMBIGUOUS_OR_LOW"
            output[cluster["cluster_id"]] = {
                "current_locus": target["current_locus"].lower(),
                "match_status": status,
                "primary_eligible": int(status in CLEAR_STATUSES),
                "string_ratio": value,
                "row_second_ratio": row_second,
                "column_second_ratio": column_second,
                "minimum_margin": margin,
                "cluster_exact_target_count_on_current_page": source_exact_target_count,
                "target_exact_cluster_count_on_current_page": target_exact_cluster_count,
            }
    return output


def build_crosswalk(
    sources: list[dict[str, Any]], clusters: list[dict[str, Any]],
    current_by_page: dict[str, list[dict[str, Any]]], by_locus: dict[str, dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, int]]:
    position = explicit_position_mappings(clusters)
    sequence, sequence_summaries = sequence_mappings(clusters, load_locator_groups(by_locus))
    strong: dict[str, dict[str, Any]] = {}
    conflicts: set[str] = set()
    noncurrent_positions = {
        cid for cid, mapping in position.items()
        if mapping["current_locus"] not in by_locus
    }
    for cluster in clusters:
        cid = cluster["cluster_id"]
        pos = position.get(cid)
        seq = sequence.get(cid)
        if cid in noncurrent_positions:
            continue
        if pos and seq and pos["current_locus"] != seq["current_locus"]:
            conflicts.add(cid)
        elif pos:
            strong[cid] = {**pos, "match_status": "EXPLICIT_HUMAN_POSITION_KEY", "mapping_method": "HUMAN_GROVE_SCOPE_NUMBER", "manual_position_description_used_for_mapping": 1}
        elif seq:
            strong[cid] = {**seq, "match_status": "SEQUENCE_GROUP_POSITION", "mapping_method": "MANUAL_TRANSCRIPTION_GROUP_SEQUENCE", "manual_position_description_used_for_mapping": 0}
    target_to_clusters: defaultdict[str, list[str]] = defaultdict(list)
    for cid, mapping in strong.items():
        target_to_clusters[mapping["current_locus"]].append(cid)
    for target, ids in target_to_clusters.items():
        if len(ids) > 1:
            conflicts.update(ids)
    for cid in conflicts:
        strong.pop(cid, None)
    blocked_targets = {mapping["current_locus"] for mapping in strong.values()}
    string = string_mappings(
        clusters, current_by_page,
        set(strong) | conflicts | noncurrent_positions, blocked_targets,
    )

    records_by_id = {row["source_record_id"]: row for row in sources}
    source_norm_page_count = Counter(
        (cluster["current_page_key"], value)
        for cluster in clusters for value in cluster["source_norms"]
    )
    rows = []
    for cluster in clusters:
        cid = cluster["cluster_id"]
        if cid in noncurrent_positions:
            mapping = {
                "match_status": "EXPLICIT_MISSING_POSITION_NO_CURRENT_LOCUS",
                "primary_eligible": 0,
                "mapping_method": "HUMAN_GROVE_SCOPE_NUMBER_MISSING_POSITION",
                "manual_position_description_used_for_mapping": 1,
            }
        elif cid in conflicts:
            mapping = {
                "match_status": "STRONG_MAPPING_EVIDENCE_CONFLICT",
                "primary_eligible": 0,
                "mapping_method": "CONFLICT_POSITION_SEQUENCE_OR_TARGET",
                "manual_position_description_used_for_mapping": int(cid in position),
            }
        elif cid in strong:
            mapping = {**strong[cid], "primary_eligible": 1}
        else:
            mapping = {**string[cid], "mapping_method": "PAGE_LOCAL_PHYSICAL_CLUSTER_STRING", "manual_position_description_used_for_mapping": 0}
        target = by_locus.get(mapping.get("current_locus", ""))
        if target:
            current_ratio = pair_score(cluster["source_norms"], target["normalized_readings"])
            mapping.setdefault("string_ratio", current_ratio)
        record_ids = [record["source_record_id"] for record in cluster["records"]]
        transcriber_codes = sorted({record["source_transcriber_code"] for record in cluster["records"]})
        for source_id in record_ids:
            source = records_by_id[source_id]
            row = dict(source)
            row.update({
                "physical_location_record_count": len(record_ids),
                "same_physical_location_record_ids": ";".join(record_ids),
                "physical_location_transcriber_codes": ";".join(transcriber_codes),
                "physical_location_normalized_source_texts": ";".join(sorted(cluster["source_norms"])),
                "matching_method": mapping["mapping_method"],
                "manual_position_description_used_for_mapping": mapping["manual_position_description_used_for_mapping"],
                "descriptions_used_for_matching": mapping["manual_position_description_used_for_mapping"],
                "position_candidate_locus": position.get(cid, {}).get("current_locus", ""),
                "sequence_candidate_locus": sequence.get(cid, {}).get("current_locus", ""),
                "position_key": position.get(cid, {}).get("position_key", ""),
                "match_status": mapping["match_status"],
                "primary_eligible": mapping["primary_eligible"],
                "source_text_physical_location_multiplicity_on_current_page": source_norm_page_count[(cluster["current_page_key"], source["source_normalized"])] if source["source_normalized"] else 0,
            })
            for field in (
                "string_ratio", "row_second_ratio", "column_second_ratio", "minimum_margin",
                "cluster_exact_target_count_on_current_page", "target_exact_cluster_count_on_current_page",
                "target_old_unit", "source_group_size", "sequence_reversed", "sequence_rotation",
                "sequence_mean_ratio", "sequence_exact_count", "sequence_runner_mean_ratio", "sequence_group_margin",
            ):
                if field in mapping:
                    value = mapping[field]
                    row[field] = f"{value:.6f}" if isinstance(value, float) else value
            if target:
                readings = target["readings"]
                row.update({
                    "current_page": target["current_page"],
                    "current_locus": target["current_locus"],
                    "current_code": target["current_code"],
                    "current_kind": target["current_kind"],
                    "current_subtype": target["current_subtype"],
                    "ZL3b_text": readings["ZL3b"], "IT2a_text": readings["IT2a"], "RF1b_text": readings["RF1b"],
                    "all_three_present": int(all(readings.values())),
                })
            rows.append(row)
    rows.sort(key=lambda row: int(row["source_record_id"].rsplit("_", 1)[1]))
    diagnostics = {
        "explicit_position_clusters": len(position),
        "strong_sequence_groups": len(sequence_summaries),
        "strong_sequence_clusters": len(sequence),
        "strong_mapping_conflict_clusters": len(conflicts),
        "explicit_missing_noncurrent_positions": len(noncurrent_positions),
    }
    return rows, sequence_summaries, diagnostics


def build_label_matrix(crosswalk: list[dict[str, Any]]) -> list[dict[str, Any]]:
    eligible = [row for row in crosswalk if row.get("primary_eligible") == 1]
    grouped: defaultdict[tuple[str, ...], list[dict[str, Any]]] = defaultdict(list)
    for row in eligible:
        key = (row["source_section"], row["source_object_class"], row["source_object_guess"], row["current_kind"], row["current_subtype"])
        grouped[key].append(row)
    output = []
    for key, rows in sorted(grouped.items()):
        physical_ids = list(dict.fromkeys(row["source_physical_location_id"] for row in rows))
        output.append({
            "source_section": key[0], "source_object_class": key[1], "source_object_guess": key[2],
            "current_kind": key[3], "current_subtype": key[4],
            "clear_physical_location_count": len(physical_ids),
            "clear_source_record_count": len(rows),
            "current_page_count": len({row["current_page"] for row in rows}),
            "source_certainty_counts": ";".join(f"{name}:{count}" for name, count in sorted(Counter(row["source_certainty"] for row in rows).items())),
            "source_physical_location_ids": ";".join(physical_ids),
            "source_record_ids": ";".join(row["source_record_id"] for row in rows),
        })
    return output


def build_page_matrix() -> list[dict[str, Any]]:
    annotations = {row["page"]: row for row in read_tsv(PAGE_ANNOTATIONS)}
    output = []
    for row in read_tsv(PAGE_CENSUS):
        annotation = annotations.get(row["page"])
        output.append({
            "page_order": row["page_order"], "page": row["page"], "section": row["section"],
            "currier": row["currier"], "hand": row["hand"], "quire": row["quire"],
            "P_count": row["P_count"], "L_count": row["L_count"], "C_count": row["C_count"], "R_count": row["R_count"],
            "paragraph_start_count": row["paragraph_start_count"], "layout_template_id": row["layout_template_id"],
            "catalogue_match_status": "EXACT" if annotation else "COMPOUND_ALIAS_REQUIRED" if row["page"] == "fRos" else "MISSING",
            "source_tags": annotation["source_tags"] if annotation else "",
            "has_general_description": int(bool(annotation and annotation["general_description"])),
            "has_illustration_description": int(bool(annotation and annotation["illustrations"])),
            "has_text_description": int(bool(annotation and annotation["text_description"])),
            "source_url": annotation["source_url"] if annotation else "",
        })
    return output


def main() -> None:
    started = time.perf_counter()
    sources = parse_label_source()
    clusters = cluster_sources(sources)
    current_by_page, by_locus = load_current_loci()
    crosswalk, sequence_summaries, diagnostics = build_crosswalk(sources, clusters, current_by_page, by_locus)
    label_matrix = build_label_matrix(crosswalk)
    page_matrix = build_page_matrix()

    crosswalk_fields = [
        "source_record_id", "source_section", "source_page", "current_page_key", "legacy_alias_applied",
        "source_unit", "source_item", "source_location", "source_physical_location_id", "source_transcriber_code",
        "source_text", "source_alternate_text", "source_normalized", "source_object_class", "source_object_guess",
        "source_comments", "source_attribute_tags", "source_certainty", "physical_location_record_count",
        "same_physical_location_record_ids", "physical_location_transcriber_codes", "physical_location_normalized_source_texts",
        "matching_method", "manual_position_description_used_for_mapping", "descriptions_used_for_matching",
        "position_candidate_locus", "sequence_candidate_locus", "position_key", "current_page", "current_locus",
        "current_code", "current_kind", "current_subtype", "ZL3b_text", "IT2a_text", "RF1b_text", "all_three_present",
        "string_ratio", "row_second_ratio", "column_second_ratio", "minimum_margin",
        "source_text_physical_location_multiplicity_on_current_page", "cluster_exact_target_count_on_current_page",
        "target_exact_cluster_count_on_current_page", "target_old_unit", "source_group_size", "sequence_reversed",
        "sequence_rotation", "sequence_mean_ratio", "sequence_exact_count", "sequence_runner_mean_ratio",
        "sequence_group_margin", "match_status", "primary_eligible",
    ]
    label_matrix_fields = [
        "source_section", "source_object_class", "source_object_guess", "current_kind", "current_subtype",
        "clear_physical_location_count", "clear_source_record_count", "current_page_count", "source_certainty_counts",
        "source_physical_location_ids", "source_record_ids",
    ]
    page_matrix_fields = [
        "page_order", "page", "section", "currier", "hand", "quire", "P_count", "L_count", "C_count", "R_count",
        "paragraph_start_count", "layout_template_id", "catalogue_match_status", "source_tags", "has_general_description",
        "has_illustration_description", "has_text_description", "source_url",
    ]
    write_tsv(CROSSWALK_OUT, crosswalk_fields, crosswalk)
    write_tsv(LABEL_MATRIX_OUT, label_matrix_fields, label_matrix)
    write_tsv(PAGE_MATRIX_OUT, page_matrix_fields, page_matrix)

    status_record_counts = Counter(row["match_status"] for row in crosswalk)
    physical_status = {}
    for row in crosswalk:
        physical_status[row["source_physical_location_id"]] = row["match_status"]
    status_location_counts = Counter(physical_status.values())
    eligible = [row for row in crosswalk if row.get("primary_eligible") == 1]
    eligible_locations = {row["source_physical_location_id"] for row in eligible}
    kind_by_location = {
        row["source_physical_location_id"]: row["current_kind"] for row in eligible
    }
    normalized_source_locations: defaultdict[str, set[str]] = defaultdict(set)
    for cluster in clusters:
        for value in cluster["source_norms"]:
            normalized_source_locations[value].add(cluster["cluster_id"])
    repeated_source_locations = {
        value: locations
        for value, locations in normalized_source_locations.items()
        if len(locations) > 1
    }
    payload = {
        "status": "PASS_CLUSTERED_MULTI_EVIDENCE_CURRENT_LOCUS_CROSSWALK",
        "thresholds": {
            "minimum_ratio": MIN_RATIO, "high_ratio": HIGH_RATIO, "minimum_margin": MIN_MARGIN,
            "sequence_minimum_mean_ratio": SEQUENCE_MIN_MEAN,
        },
        "page_aliases": PAGE_ALIASES,
        "label_index_format_url": LABEL_FORMAT_URL,
        "counts": {
            "source_records": len(sources),
            "source_records_with_string": sum(bool(row["source_normalized"]) for row in sources),
            "physical_source_locations": len(clusters),
            "multi_witness_physical_locations": sum(len(c["records"]) > 1 for c in clusters),
            "repeated_normalized_source_text_types": len(repeated_source_locations),
            "physical_locations_in_repeated_text_types": len(set().union(*repeated_source_locations.values())),
            "crosswalk_rows": len(crosswalk),
            "match_status_source_records": dict(sorted(status_record_counts.items())),
            "match_status_physical_locations": dict(sorted(status_location_counts.items())),
            "primary_eligible_source_records": len(eligible),
            "primary_eligible_physical_locations": len(eligible_locations),
            "primary_eligible_pages": len({row["current_page"] for row in eligible}),
            "primary_eligible_all_three_physical_locations": len({row["source_physical_location_id"] for row in eligible if row["all_three_present"]}),
            "primary_eligible_by_current_kind_physical_locations": dict(sorted(Counter(kind_by_location.values()).items())),
            "label_role_matrix_rows": len(label_matrix),
            "page_role_matrix_rows": len(page_matrix),
            "page_role_exact_catalogue_matches": sum(row["catalogue_match_status"] == "EXACT" for row in page_matrix),
            **diagnostics,
        },
        "inputs": {str(path.relative_to(ROOT)): sha256(path) for path in (
            LABEL_INDEX, LABEL_ANNOTATIONS, EXACT_ANNOTATIONS, LOCUS_ROLES, PAGE_ANNOTATIONS, PAGE_CENSUS,
            STOLFI_LINES, *EDITION_PATHS.values(),
        )},
        "guardrails": [
            "assignment unit is a physical legacy location, not a transcription record",
            "U- and V-coded transcriptions of the same f75v location may map to the same current locus",
            "identical text at distinct locations is retained as a genuine repetition",
            "only explicit Grove scope-number layout keys, ordered manual transcription groups, and manual strings select mappings",
            "object identities attributes grammar English meaning and image pixels do not select mappings",
            "ambiguous low and conflicting locations remain in the output with primary_eligible=0",
            "ZL3b IT2a RF1b and Stolfi are alternate readings or annotation layers, never replications",
        ],
        "sequence_group_summaries": sequence_summaries,
        "image_pixels_or_automated_vision_used": False,
        "manual_visual_quality_control_used": False,
        "ocr_used": False,
        "semantic_or_grammar_score_computed": False,
        "runtime_seconds": time.perf_counter() - started,
    }
    payload["artifact_hashes"] = {str(path.relative_to(ROOT)): sha256(path) for path in (CROSSWALK_OUT, LABEL_MATRIX_OUT, PAGE_MATRIX_OUT)}
    MANIFEST_OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    counts = payload["counts"]
    report = "\n".join([
        "# Existing-human current-locus crosswalk", "",
        "Decision: **PASS_CLUSTERED_MULTI_EVIDENCE_CURRENT_LOCUS_CROSSWALK**.", "",
        "Important correction: the 1,018 source rows are not 1,018 physical labels. "
        "They represent **998 physical locations**; f75v has 20 locations with both U- and V-coded transcriptions. "
        "The prior record-level Hungarian assignment incorrectly forced those paired transcription records onto different loci and is superseded.", "",
        "The source format defines field 6 as the one-letter transcriber code, field 7 as the EVA label/title, and field 8 as an alternate spelling. "
        "The active schema now uses `source_transcriber_code`; string matching always uses the field-7 text.", "",
        f"The corrected crosswalk retains all **{counts['source_records']}** source records and maps "
        f"**{counts['primary_eligible_physical_locations']} / {counts['physical_source_locations']}** physical locations "
        f"conservatively on {counts['primary_eligible_pages']} pages.", "",
        "| match status | physical locations | source records |", "|---|---:|---:|",
        *[
            f"| {name} | {status_location_counts.get(name, 0)} | {status_record_counts.get(name, 0)} |"
            for name in sorted(set(status_location_counts) | set(status_record_counts))
        ], "",
        f"Explicit human ring/Grove-number keys map {counts['explicit_position_clusters']} physical locations. "
        f"Strongly separated sequence alignments map {counts['strong_sequence_clusters']} locations in "
        f"{counts['strong_sequence_groups']} whole groups. Conflicting strong evidence remains withheld "
        f"for {counts['strong_mapping_conflict_clusters']} locations.", "",
        f"Repeated words are not removed. {counts['repeated_normalized_source_text_types']} exact-normalized source text types "
        f"occur at {counts['physical_locations_in_repeated_text_types']} physical locations. A repeated word at two physical "
        "locations remains two rows; sequence or explicit "
        "position evidence may disambiguate which occurrence is which. Alternate transcriptions of one physical location remain "
        "linked and never count as two labels or independent confirmation.", "",
        f"Clear current kinds by physical location: `{counts['primary_eligible_by_current_kind_physical_locations']}`. "
        "This is a document-role crosswalk, not evidence that a label is a name, noun, or translated word.", "",
        f"The page-role matrix covers {counts['page_role_matrix_rows']} active pages with "
        f"{counts['page_role_exact_catalogue_matches']} literal catalogue matches; `fRos` remains `COMPOUND_ALIAS_REQUIRED`.", "",
        "No image, OCR, automated vision, grammar feature, object identity, or English semantic score selected a mapping. "
        "The explicit position layer uses only human ring scope and Grove numbering. Ambiguous records were not dropped.", "",
    ])
    REPORT_OUT.write_text(report, encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
