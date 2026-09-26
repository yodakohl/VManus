#!/usr/bin/env python3
"""Build exhaustive descriptive tables from the guarded f85r2 projection."""
from __future__ import annotations

import csv
import hashlib
import itertools
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt1042_f85r2_source_program_surface_census"
PROJECTION = EXP / "artifacts/guarded_projection.tsv"
ARTIFACTS = EXP / "artifacts"
EDITIONS = ("ZL3b", "IT2a", "RF1b")
BLOCKS = {
    "N": tuple(range(2, 7)),
    "E": tuple(range(7, 12)),
    "S": tuple(range(12, 18)),
    "W": tuple(range(18, 24)),
}
ALL_SPATIAL = {line: block for block, lines in BLOCKS.items() for line in lines}
LETTERS = re.compile(r"[A-Za-z]+\Z")


def j(value) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def write_tsv(name: str, columns: list[str], rows: list[dict]) -> int:
    path = ARTIFACTS / name
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns, delimiter="\t", lineterminator="\n", extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


def line_num(locus: str) -> int:
    # Parse only the dedicated locus field. source_group_id can carry native
    # suffix tags and is retained verbatim rather than used as a line parser.
    match = re.fullmatch(r"f85r2\.(\d+)(?:[A-Za-z])?", locus)
    if not match:
        raise AssertionError(f"unexpected guarded locus form: {locus!r}")
    return int(match.group(1))


def position(index: int, count: int) -> str:
    if count == 1:
        return "first_last"
    if index == 1:
        return "first"
    if index == count:
        return "last"
    return "interior"


def edit_distance_one(a: str, b: str) -> bool:
    """Levenshtein distance one; adjacent transposition is not a single edit."""
    if abs(len(a) - len(b)) > 1 or a == b:
        return False
    if len(a) == len(b):
        mismatches = sum(x != y for x, y in zip(a, b))
        return mismatches == 1
    short, long = (a, b) if len(a) < len(b) else (b, a)
    i = jx = skips = 0
    while i < len(short) and jx < len(long):
        if short[i] == long[jx]:
            i += 1
            jx += 1
        else:
            skips += 1
            jx += 1
            if skips > 1:
                return False
    return True


def read_projection() -> list[dict]:
    with PROJECTION.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    expected = ["source_group_id", "edition", "locus", "page", "source_group_index", "source_group_count",
                "paragraph_start", "paragraph_end", "left_separator", "right_separator", "ivtff_group_raw"]
    if not rows or list(rows[0]) != expected:
        raise AssertionError("guarded projection is empty or has an unexpected explicit-column schema")
    for row in rows:
        row["line_number"] = line_num(row["locus"])
        row["group_index_int"] = int(row["source_group_index"])
        row["group_count_int"] = int(row["source_group_count"])
        row["block"] = ALL_SPATIAL.get(row["line_number"], "OUTSIDE")
        row["position"] = position(row["group_index_int"], row["group_count_int"])
    return rows


def main() -> int:
    if not PROJECTION.is_file():
        raise SystemExit("missing guarded projection; run the preregistered query-tsv command first")
    rows = read_projection()

    # Verify every selected native group is present exactly once and in bounds.
    by_line: dict[tuple[str, str], list[dict]] = defaultdict(list)
    ids = Counter()
    for r in rows:
        if r["page"] != "f85r2":
            raise AssertionError(f"projection contains non-target page: {r['page']!r}")
        if r["edition"] not in EDITIONS:
            raise AssertionError(f"unexpected edition in target projection: {r['edition']!r}")
        by_line[(r["edition"], r["locus"])].append(r)
        ids[(r["edition"], r["source_group_id"])] += 1
    if set(r["edition"] for r in rows) != set(EDITIONS):
        raise AssertionError("one or more registered alternate readings are absent")
    if any(n != 1 for n in ids.values()):
        raise AssertionError("duplicate source_group_id within edition")
    line_checks = []
    for edition in EDITIONS:
        loci = {locus for ed, locus in by_line if ed == edition}
        expected_loci = {f"f85r2.{n}" for n in range(1, 25)}
        if loci != expected_loci:
            raise AssertionError(f"{edition}: locus set mismatch; got {sorted(loci)}")
        for locus in sorted(loci, key=line_num):
            group_rows = by_line[(edition, locus)]
            counts = {r["group_count_int"] for r in group_rows}
            indices = [r["group_index_int"] for r in group_rows]
            if len(counts) != 1 or len(group_rows) != next(iter(counts)) or sorted(indices) != list(range(1, len(group_rows) + 1)):
                raise AssertionError(f"{edition}/{locus}: incomplete or inconsistent source groups")
            if len({r["source_group_id"] for r in group_rows}) != len(group_rows):
                raise AssertionError(f"{edition}/{locus}: duplicate group identity")
            line_checks.append({"edition": edition, "locus": locus, "groups": len(group_rows), "complete": True})

    # Preserve all selected rows, including non-spatial lines .1 and .24.
    native_rows = []
    for r in rows:
        native_rows.append({
            "edition": r["edition"], "block": r["block"], "locus": r["locus"],
            "source_group_id": r["source_group_id"], "source_group_index": r["source_group_index"],
            "source_group_count": r["source_group_count"], "within_line_position": r["position"],
            "paragraph_start": r["paragraph_start"], "paragraph_end": r["paragraph_end"],
            "left_separator": r["left_separator"], "right_separator": r["right_separator"],
            "ivtff_group_raw": r["ivtff_group_raw"],
        })
    native_rows.sort(key=lambda r: (EDITIONS.index(r["edition"]), line_num(r["locus"]), int(r["source_group_index"])))
    n_native = write_tsv("native_groups.tsv", list(native_rows[0]), native_rows)

    # Counts and distinct complete surface forms for every spatial block.
    block_counts = []
    for edition in EDITIONS:
        for block, lines in BLOCKS.items():
            subset = [r for r in rows if r["edition"] == edition and r["line_number"] in lines]
            block_counts.append({"edition": edition, "block": block, "line_count": len(lines),
                                 "group_count": len(subset), "distinct_complete_forms": len({r["ivtff_group_raw"] for r in subset})})
        outside = [r for r in rows if r["edition"] == edition and r["block"] == "OUTSIDE"]
        block_counts.append({"edition": edition, "block": "OUTSIDE", "line_count": len({r["locus"] for r in outside}),
                             "group_count": len(outside), "distinct_complete_forms": len({r["ivtff_group_raw"] for r in outside})})
    n_counts = write_tsv("block_counts.tsv", ["edition", "block", "line_count", "group_count", "distinct_complete_forms"], block_counts)

    repeated_rows = []
    intersections = []
    ngram_rows = []
    edit_rows = []
    edit_meta = {}
    edge_rows = []
    for edition in EDITIONS:
        spatial = [r for r in rows if r["edition"] == edition and r["block"] != "OUTSIDE"]
        by_form: dict[str, list[dict]] = defaultdict(list)
        by_block_form: dict[str, dict[str, list[dict]]] = {b: defaultdict(list) for b in BLOCKS}
        for r in spatial:
            by_form[r["ivtff_group_raw"]].append(r)
            by_block_form[r["block"]][r["ivtff_group_raw"]].append(r)
        for form in sorted((f for f, occ in by_form.items() if len(occ) >= 2)):
            occ = sorted(by_form[form], key=lambda r: (line_num(r["locus"]), r["group_index_int"]))
            block_names = [b for b in BLOCKS if by_block_form[b].get(form)]
            repeated_rows.append({"edition": edition, "form_raw": form, "occurrence_count": len(occ),
                                  "within_block_recurrence": any(len(by_block_form[b][form]) >= 2 for b in block_names),
                                  "cross_block_recurrence": len(block_names) >= 2,
                                  "blocks": ",".join(block_names),
                                  "locations_json": j([{"block": r["block"], "locus": r["locus"], "source_group_id": r["source_group_id"],
                                                        "index": r["group_index_int"], "position": r["position"]} for r in occ])})
        for a, b in itertools.combinations(BLOCKS, 2):
            for form in sorted(set(by_block_form[a]) & set(by_block_form[b])):
                intersections.append({"edition": edition, "block_a": a, "block_b": b, "form_raw": form,
                                      "locations_a_json": j([{"locus": r["locus"], "source_group_id": r["source_group_id"], "index": r["group_index_int"]} for r in by_block_form[a][form]]),
                                      "locations_b_json": j([{"locus": r["locus"], "source_group_id": r["source_group_id"], "index": r["group_index_int"]} for r in by_block_form[b][form]])})

        # Contiguous native group sequences, grouped by full recorded boundary
        # signature. Retain every signature for a repeated surface sequence.
        line_groups = {locus: sorted(v, key=lambda r: r["group_index_int"])
                       for (ed, locus), v in by_line.items() if ed == edition and v[0]["block"] != "OUTSIDE"}
        for n in (2, 3):
            occurrences: dict[tuple[tuple[str, ...], tuple[tuple[str, str], ...]], list[dict]] = defaultdict(list)
            for locus, groups in line_groups.items():
                for start in range(len(groups) - n + 1):
                    win = groups[start:start+n]
                    sequence = tuple(r["ivtff_group_raw"] for r in win)
                    boundaries = tuple((win[k]["right_separator"], win[k+1]["left_separator"]) for k in range(n-1))
                    occurrences[(sequence, boundaries)].append({"block": win[0]["block"], "locus": locus,
                        "start_index": win[0]["group_index_int"], "source_group_ids": [r["source_group_id"] for r in win]})
            surface_totals: Counter = Counter()
            sig_count: Counter = Counter()
            for (seq, sig), occ in occurrences.items():
                surface_totals[seq] += len(occ)
                sig_count[seq] += 1
            for (seq, sig), occ in sorted(occurrences.items()):
                total = surface_totals[seq]
                if total < 2:
                    continue
                ngram_rows.append({"edition": edition, "n": n, "sequence_json": j(seq),
                    "boundary_signature_json": j(sig), "signature_occurrence_count": len(occ),
                    "surface_sequence_total_occurrences": total,
                    "separator_signature_ambiguous": sig_count[seq] > 1,
                    "occurrences_json": j(sorted(occ, key=lambda o: (line_num(o["locus"]), o["start_index"])))})

        # Exhaustive unique-form pairs at literal Levenshtein distance 1.
        clean_forms = sorted(f for f in by_form if LETTERS.fullmatch(f))
        excluded_forms = sorted(f for f in by_form if not LETTERS.fullmatch(f))
        candidate_pairs = len(clean_forms) * (len(clean_forms) - 1) // 2
        edge_count = 0
        for form_a, form_b in itertools.combinations(clean_forms, 2):
            if not edit_distance_one(form_a, form_b):
                continue
            edge_count += 1
            occ_a = sorted(by_form[form_a], key=lambda r: (line_num(r["locus"]), r["group_index_int"]))
            occ_b = sorted(by_form[form_b], key=lambda r: (line_num(r["locus"]), r["group_index_int"]))
            edit_rows.append({"edition": edition, "form_a": form_a, "form_b": form_b,
                "distance": 1, "operation_note": "Levenshtein insertion/deletion/substitution; transposition is not one edit",
                "occurrence_count_a": len(occ_a), "occurrences_a_json": j([{"block": r["block"], "locus": r["locus"], "source_group_id": r["source_group_id"], "index": r["group_index_int"], "position": r["position"]} for r in occ_a]),
                "occurrence_count_b": len(occ_b), "occurrences_b_json": j([{"block": r["block"], "locus": r["locus"], "source_group_id": r["source_group_id"], "index": r["group_index_int"], "position": r["position"]} for r in occ_b])})
        edit_meta[edition] = {"spatial_group_occurrences": len(spatial), "distinct_surface_forms": len(by_form),
            "clean_ascii_letter_forms": len(clean_forms), "excluded_nonclean_distinct_forms": len(excluded_forms),
            "excluded_nonclean_occurrences": sum(len(by_form[f]) for f in excluded_forms),
            "candidate_unordered_clean_form_pairs": candidate_pairs, "distance_one_pairs": edge_count}

        # First and last native group plus both recorded separators, every line.
        for (ed, locus), groups in by_line.items():
            if ed != edition:
                continue
            ordered = sorted(groups, key=lambda r: r["group_index_int"])
            first, last = ordered[0], ordered[-1]
            edge_rows.append({"edition": edition, "block": first["block"], "locus": locus,
                "group_count": len(ordered), "first_group_raw": first["ivtff_group_raw"],
                "first_source_group_id": first["source_group_id"], "first_left_separator": first["left_separator"],
                "first_right_separator": first["right_separator"], "last_group_raw": last["ivtff_group_raw"],
                "last_source_group_id": last["source_group_id"], "last_left_separator": last["left_separator"],
                "last_right_separator": last["right_separator"]})

    n_repeated = write_tsv("repeated_forms.tsv", ["edition", "form_raw", "occurrence_count", "within_block_recurrence", "cross_block_recurrence", "blocks", "locations_json"], repeated_rows)
    n_intersections = write_tsv("block_intersections.tsv", ["edition", "block_a", "block_b", "form_raw", "locations_a_json", "locations_b_json"], intersections)
    n_ngrams = write_tsv("repeated_ngrams.tsv", ["edition", "n", "sequence_json", "boundary_signature_json", "signature_occurrence_count", "surface_sequence_total_occurrences", "separator_signature_ambiguous", "occurrences_json"], ngram_rows)
    n_edits = write_tsv("literal_edit1_pairs.tsv", ["edition", "form_a", "form_b", "distance", "operation_note", "occurrence_count_a", "occurrences_a_json", "occurrence_count_b", "occurrences_b_json"], edit_rows)
    n_edges = write_tsv("line_first_last.tsv", ["edition", "block", "locus", "group_count", "first_group_raw", "first_source_group_id", "first_left_separator", "first_right_separator", "last_group_raw", "last_source_group_id", "last_left_separator", "last_right_separator"], sorted(edge_rows, key=lambda r: (EDITIONS.index(r["edition"]), line_num(r["locus"]))))

    projection_sha = hashlib.sha256(PROJECTION.read_bytes()).hexdigest()
    stderr_path = ARTIFACTS / "query_guard_stderr.txt"
    stderr_sha = hashlib.sha256(stderr_path.read_bytes()).hexdigest() if stderr_path.exists() else None
    summary = {
        "experiment": "GDT1042",
        "result_status": "complete_descriptive_census",
        "scope": {"page": "f85r2", "editions_separately": list(EDITIONS), "blocks": {b: list(v) for b, v in BLOCKS.items()},
                  "outside_spatial_blocks_retained": [1, 24], "sealed_pages_accessed": [], "semantic_readings_used": False},
        "input": {"guarded_query": "./vmanus-exp query-tsv experiments/semantic_assumptions/results/source_separator_transcription.tsv --selector page --allow f85r2 --columns source_group_id,edition,locus,page,source_group_index,source_group_count,paragraph_start,paragraph_end,left_separator,right_separator,ivtff_group_raw",
                  "projection_file": "artifacts/guarded_projection.tsv", "projection_sha256": projection_sha,
                  "source_hash_scope": "sha256 of the exact selector-guarded query stdout projection; the mixed source file was not opened or hashed directly",
                  "query_guard_stderr_sha256": stderr_sha,
                  "guard_stats": "GUARD_STATS selected 473, skipped_forbidden 2122, skipped_not_allowed 112875; see query_guard_stderr.txt"},
        "completeness": {"projection_group_rows": len(rows), "unique_group_ids": len(ids), "line_instances_checked": len(line_checks),
                         "line_instances_complete": all(x["complete"] for x in line_checks), "line_checks": line_checks,
                         "group_table_rows": n_native, "group_table_covers_projection": n_native == len(rows),
                         "all_editions_present": set(r["edition"] for r in rows) == set(EDITIONS),
                         "all_lines_1_to_24_per_edition": len(line_checks) == 72},
        "table_rows": {"block_counts": n_counts, "repeated_forms": n_repeated, "block_intersections": n_intersections,
                       "repeated_ngrams": n_ngrams, "literal_edit1_pairs": n_edits, "line_first_last": n_edges},
        "edit1_exclusion_and_pair_counts": edit_meta,
        "interpretive_limit": "Descriptive whole-form and adjacency inventory only; no meanings, scoring, significance, or null model.",
    }
    result_path = ARTIFACTS / "RESULT.json"
    result_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"projection_rows": len(rows), "tables": summary["table_rows"], "edit1": edit_meta}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, OSError, ValueError, KeyError) as exc:
        print(f"GDT1042 census failed: {exc}", file=sys.stderr)
        raise SystemExit(2)
