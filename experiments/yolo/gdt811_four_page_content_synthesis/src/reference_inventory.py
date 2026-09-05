#!/usr/bin/env python3
"""Exact seven-whole inventory on inherited, explicitly guarded selectors."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
from typing import Any, Iterable


def find_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("repository root not found")


ROOT = find_root(Path(__file__).resolve())
SRC = Path(__file__).resolve().parent
EXPERIMENT = SRC.parent
DESIGN = SRC / "REFERENCE_DESIGN.md"
G631 = ROOT / "experiments/yolo/gdt631_prefixed_cth_quality_parts"
G791 = ROOT / "experiments/yolo/gdt791_thirty_page_visual_owner_spine"
ALLOWLIST = G631 / "artifacts/PAGE_ALLOWLIST.tsv"
SELECTOR_SPECS = G791 / "src/PAGE_SELECTOR_SPECS.tsv"
LINE_ATLAS = G791 / "artifacts/GDT791_1007_LINE_OWNER_ATLAS.tsv"
ZL = ROOT / "transcription/voynich_zl3b_lines.tsv"
CROSS = ROOT / "transcription/voynich_cross_transcription_lines.tsv"
SURFACES = ("okol", "chokol", "qokol", "okoldy", "qoekol", "ofaldo", "ofal")
INVENTORY_FIELDS = (
    "page", "locus", "section", "source_line", "surface", "ordinal",
    "within_line_occurrence_rank", "line_number", "physical_page", "physical_page_basis",
    "released_physical_page", "released_gdt791_status", "raw_kind",
    "raw_role", "zl3b_occurrences_in_line", "it2a_occurrences_in_line",
    "rf1b_occurrences_in_line", "it2a_rank_ordinal", "rf1b_rank_ordinal",
    "it2a_rank_supported", "rf1b_rank_supported", "reader_support_count",
    "reader_support_definition", "semantic_credit", "component_export_credit",
)
SUMMARY_FIELDS = (
    "surface", "occurrences", "distinct_loci", "source_selectors",
    "physical_pages", "three_reading_rank_supported", "f88r_occurrences",
    "outside_f88r_occurrences", "outside_f88r_physical_pages",
    "raw_prose_occurrences", "raw_label_occurrences", "raw_other_occurrences",
    "released_running_occurrences", "released_local_occurrences",
    "outside_gdt791_occurrences", "counts_by_section_json",
    "counts_by_physical_page_json", "counts_by_raw_role_json",
    "counts_by_released_status_json", "semantic_credit", "component_export_credit",
)
DISTRIBUTION_FIELDS = (
    "surface", "dimension", "category", "occurrences", "distinct_loci",
    "source_selectors", "physical_pages", "three_reading_rank_supported",
    "outside_f88r_occurrences", "semantic_credit", "component_export_credit",
)


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def digest(path: Path) -> str:
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def read_specs(path: Path) -> list[dict[str, str]]:
    # These are selector-only scope specifications, not mixed manuscript rows.
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def side(selector: str) -> str:
    match = re.fullmatch(r"(f\d+[rv])\d*", selector)
    if not match:
        raise RuntimeError(f"unsupported source selector: {selector}")
    return match.group(1)


def selector_key(selector: str) -> tuple[int, str, int]:
    match = re.fullmatch(r"f(\d+)([rv])(\d*)", selector)
    if not match:
        raise RuntimeError("invalid source selector")
    return int(match.group(1)), match.group(2), int(match.group(3) or 0)


def guarded_query(path: Path, selector: str, allows: Iterable[str],
                  columns: tuple[str, ...], query_id: str
                  ) -> tuple[list[dict[str, str]], dict[str, Any]]:
    values = sorted(set(allows), key=selector_key)
    if not values or any(value.startswith("f84") for value in values):
        raise RuntimeError("empty or sealed query scope")
    command = [str(ROOT / "vmanus-exp"), "query-tsv", rel(path),
               "--selector", selector]
    for value in values:
        command.extend(("--allow", value))
    command.extend(("--columns", ",".join(columns), "--forbid-prefix", "f84",
                    "--forbid-prefix", "f84r"))
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError(f"guarded query failed: {query_id}")
    stat_lines = [line for line in result.stderr.splitlines()
                  if line.startswith("GUARD_STATS ")]
    if len(stat_lines) != 1:
        raise RuntimeError(f"missing guard statistics: {query_id}")
    rows = list(csv.DictReader(io.StringIO(result.stdout), delimiter="\t"))
    if any(tuple(row) != columns for row in rows):
        raise RuntimeError(f"unexpected retained columns: {query_id}")
    if any(row[selector] not in values or row[selector].startswith("f84")
           for row in rows):
        raise RuntimeError(f"guarded selector contract failed: {query_id}")
    stats = json.loads(stat_lines[0].removeprefix("GUARD_STATS "))
    if stats["selected"] != len(rows):
        raise RuntimeError(f"guard row count failed: {query_id}")
    return rows, {"query_id": query_id, "source": rel(path),
                  "selector": selector, "allow_values": values,
                  "columns": list(columns), "forbid_prefixes": ["f84", "f84r"],
                  "guard_stats": stats}


def write_tsv(path: Path, rows: Iterable[dict[str, Any]], fields: tuple[str, ...]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t",
                                lineterminator="\n", extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)


def compact(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def count_values(rows: list[dict[str, Any]], field: str) -> dict[str, int]:
    return dict(sorted(Counter(row[field] for row in rows).items()))


def basic_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "occurrences": len(rows),
        "distinct_loci": len({row["locus"] for row in rows}),
        "source_selectors": len({row["page"] for row in rows}),
        "physical_pages": len({row["physical_page"] for row in rows}),
        "three_reading_rank_supported": sum(row["reader_support_count"] == 3 for row in rows),
        "outside_f88r_occurrences": sum(row["physical_page"] != "f88r" for row in rows),
    }


def build(output_dir: Path) -> dict[str, Any]:
    if not DESIGN.is_file():
        raise RuntimeError("REFERENCE_DESIGN.md must exist before execution")
    inherited_rows = read_specs(ALLOWLIST)
    inherited = {row["page"] for row in inherited_rows}
    if len(inherited_rows) != 179 or len(inherited) != 179:
        raise RuntimeError("inherited 179-selector scope changed")
    released_specs = read_specs(SELECTOR_SPECS)
    released = {row["source_selector"]: row["physical_page"] for row in released_specs}
    if len(released) != len(released_specs) or len(set(released.values())) != 30:
        raise RuntimeError("released thirty-page selector mapping changed")
    allowed = inherited | set(released)
    if any(value.startswith("f84") for value in allowed):
        raise RuntimeError("sealed selector present in admitted scope")

    # Exactly one raw query and one alternate query. Only their selected columns
    # are materialized; the inherited corpus stays in memory, not a new dump.
    raw, raw_stats = guarded_query(ZL, "page", allowed,
        ("page", "locus", "line_number", "section", "kind", "eva_clean"), "raw_zl3b")
    cross, cross_stats = guarded_query(CROSS, "page", allowed,
        ("page", "locus", "zl3b_clean", "it2a_clean", "rf1b_clean"), "alternate_lines")
    atlas, atlas_stats = guarded_query(LINE_ATLAS, "source_selector", released,
        ("source_selector", "physical_page", "locus", "line_kind", "eva_clean"),
        "released_gdt791_line_status")
    cross_by_key = {(row["page"], row["locus"]): row for row in cross}
    atlas_by_key = {(row["source_selector"], row["locus"]): row for row in atlas}
    if len(cross_by_key) != len(cross) or len(atlas_by_key) != len(atlas):
        raise RuntimeError("duplicate source line identity")

    inventory: list[dict[str, Any]] = []
    for row in raw:
        key = row["page"], row["locus"]
        words = row["eva_clean"].split()
        targets = set(words) & set(SURFACES)
        if not targets:
            continue
        alternate = cross_by_key.get(key)
        if alternate is None or alternate["zl3b_clean"] != row["eva_clean"]:
            raise RuntimeError(f"target source/alternate replay differs at {row['locus']}")
        known = atlas_by_key.get(key)
        if row["page"] in released:
            if known is None or known["eva_clean"] != row["eva_clean"]:
                raise RuntimeError(f"released target line missing or changed at {row['locus']}")
            if known["physical_page"] != released[row["page"]]:
                raise RuntimeError("released target physical page differs")
        elif known is not None:
            raise RuntimeError("unreleased line entered GDT791 join")
        positions = {
            reader: {surface: [index for index, token in enumerate(text.split(), 1)
                                if token == surface] for surface in targets}
            for reader, text in (("zl3b", row["eva_clean"]),
                                 ("it2a", alternate["it2a_clean"]),
                                 ("rf1b", alternate["rf1b_clean"]))
        }
        ranks: Counter[str] = Counter()
        for ordinal, surface in enumerate(words, 1):
            if surface not in targets:
                continue
            ranks[surface] += 1
            rank = ranks[surface]
            it_pos, rf_pos = positions["it2a"][surface], positions["rf1b"][surface]
            it_support, rf_support = int(len(it_pos) >= rank), int(len(rf_pos) >= rank)
            inventory.append({
                "page": row["page"], "locus": row["locus"], "section": row["section"],
                "source_line": row["eva_clean"], "surface": surface, "ordinal": ordinal,
                "within_line_occurrence_rank": rank, "line_number": row["line_number"],
                "physical_page": known["physical_page"] if known else side(row["page"]),
                "physical_page_basis": "GDT791_EXPLICIT_MAPPING" if known else "NORMALIZED_SIDE_HEURISTIC",
                "released_physical_page": known["physical_page"] if known else "NOT_IN_GDT791",
                "released_gdt791_status": known["line_kind"] if known else "NOT_IN_GDT791",
                "raw_kind": row["kind"],
                "raw_role": {"P": "PROSE", "L": "LOCAL_LABEL"}.get(row["kind"], "OTHER"),
                "zl3b_occurrences_in_line": len(positions["zl3b"][surface]),
                "it2a_occurrences_in_line": len(it_pos), "rf1b_occurrences_in_line": len(rf_pos),
                "it2a_rank_ordinal": it_pos[rank - 1] if it_support else "ABSENT",
                "rf1b_rank_ordinal": rf_pos[rank - 1] if rf_support else "ABSENT",
                "it2a_rank_supported": it_support, "rf1b_rank_supported": rf_support,
                "reader_support_count": 1 + it_support + rf_support,
                "reader_support_definition": "NTH_EXACT_WHOLE_IN_SAME_LINE__NOT_ALIGNMENT_PROOF",
                "semantic_credit": 0, "component_export_credit": 0,
            })
    inventory.sort(key=lambda row: (selector_key(row["page"]),
                                    int(row["line_number"]), row["ordinal"]))

    summaries, distributions = [], []
    for surface in SURFACES:
        rows = [row for row in inventory if row["surface"] == surface]
        summaries.append({
            "surface": surface, **basic_counts(rows),
            "f88r_occurrences": sum(row["physical_page"] == "f88r" for row in rows),
            "outside_f88r_physical_pages": len({row["physical_page"] for row in rows
                                                if row["physical_page"] != "f88r"}),
            "raw_prose_occurrences": sum(row["raw_role"] == "PROSE" for row in rows),
            "raw_label_occurrences": sum(row["raw_role"] == "LOCAL_LABEL" for row in rows),
            "raw_other_occurrences": sum(row["raw_role"] == "OTHER" for row in rows),
            "released_running_occurrences": sum(row["released_gdt791_status"] == "RUNNING_PROSE" for row in rows),
            "released_local_occurrences": sum(row["released_gdt791_status"] == "LOCAL_LABEL_OR_MARKER" for row in rows),
            "outside_gdt791_occurrences": sum(row["released_gdt791_status"] == "NOT_IN_GDT791" for row in rows),
            "counts_by_section_json": compact(count_values(rows, "section")),
            "counts_by_physical_page_json": compact(count_values(rows, "physical_page")),
            "counts_by_raw_role_json": compact(count_values(rows, "raw_role")),
            "counts_by_released_status_json": compact(count_values(rows, "released_gdt791_status")),
            "semantic_credit": 0, "component_export_credit": 0,
        })
        for dimension in ("section", "physical_page", "raw_role", "released_gdt791_status"):
            groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
            for row in rows:
                groups[row[dimension]].append(row)
            for category, members in sorted(groups.items()):
                distributions.append({"surface": surface, "dimension": dimension,
                    "category": category, **basic_counts(members),
                    "semantic_credit": 0, "component_export_credit": 0})

    output_dir = output_dir.resolve()
    rel(output_dir)  # Artifacts must remain within the repository; no private paths.
    output_dir.mkdir(parents=True, exist_ok=True)
    outputs = {
        "REFERENCE_INVENTORY.tsv": (inventory, INVENTORY_FIELDS),
        "REFERENCE_WHOLE_SUMMARY.tsv": (summaries, SUMMARY_FIELDS),
        "REFERENCE_DISTRIBUTION_COUNTS.tsv": (distributions, DISTRIBUTION_FIELDS),
    }
    for name, (rows, fields) in outputs.items():
        write_tsv(output_dir / name, rows, fields)
    inputs = (Path(__file__).resolve(), DESIGN, ALLOWLIST, SELECTOR_SPECS, LINE_ATLAS, ZL, CROSS)
    result = {
        "status": "DESCRIPTIVE_WHOLE_INVENTORY__NO_MEANING_SELECTION",
        "surfaces": list(SURFACES), "inherited_selector_count": len(inherited),
        "released_source_selector_count": len(released), "released_physical_page_count": 30,
        "union_selector_count": len(allowed), "raw_lines_selected": len(raw),
        "alternate_lines_selected": len(cross), "released_line_status_rows_selected": len(atlas),
        "inventory_occurrences": len(inventory), "summary_rows": len(summaries),
        "distribution_rows": len(distributions),
        "f88r_seed_occurrences": sum(row["physical_page"] == "f88r" for row in inventory),
        "three_reading_rank_supported": sum(row["reader_support_count"] == 3 for row in inventory),
        "queries": [raw_stats, cross_stats, atlas_stats],
        "source_hashes": {rel(path): digest(path) for path in inputs},
        "artifact_hashes": {name: digest(output_dir / name) for name in outputs},
        "new_pages_opened": 0, "new_images_opened": 0,
        "semantic_credit": 0, "component_export_credit": 0,
        "physical_page_count_caveat": "GDT791 explicit keys are authoritative for released occurrences, including panel-numbered keys; outside GDT791, physical_page is only a normalized-side grouping heuristic, not an independently established physical-page identity.",
        "reader_support_caveat": "Ordinal occurrence-rank existence within one alternate line, not token alignment or independent witnesses.",
    }
    (output_dir / "REFERENCE_RESULT.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=EXPERIMENT / "artifacts")
    args = parser.parse_args()
    result = build(args.output_dir)
    print(json.dumps({key: result[key] for key in (
        "status", "union_selector_count", "inventory_occurrences",
        "summary_rows", "f88r_seed_occurrences", "three_reading_rank_supported")},
        ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
