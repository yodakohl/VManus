#!/usr/bin/env python3
"""Independent metadata-only reconstruction for GDT1099 artifacts.

This validator does not import or invoke run.py. It reads the frozen event table
and AN_METADATA.tsv, whose schema is metadata-only, then independently rebuilds
consensus lines, strict physical frames, pair classifications, cells, exclusions,
and summary counts. Locked source files are checked by digest only; the source
transcription TSV is never parsed or emitted.
"""
from __future__ import annotations

import csv
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve()
EXP = HERE.parents[1]
ROOT = HERE.parents[4]
EDITION_ORDER = ("ZL3b", "IT2a", "RF1b")
META_FIELDS = {
    "edition", "page", "locus", "kind", "source_row_index",
    "source_group_index", "source_group_count", "paragraph_start", "paragraph_end",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def check(condition: bool, label: str, errors: list[str]) -> None:
    if not condition:
        errors.append(label)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    errors: list[str] = []
    spec = load_json(EXP / "src/INPUTS.json")

    # Verify locked provenance by digest only. In particular, no source text is
    # parsed; the locked source transcription is only streamed through SHA-256.
    digest_checks = {}
    for item in spec["files"]:
        path = ROOT / item["path"]
        got = sha256(path)
        digest_checks[item["path"]] = got == item["sha256"]
        check(got == item["sha256"], f"input digest mismatch: {item['path']}", errors)

    event_path = ROOT / spec["events"]
    metadata_path = ROOT / spec["metadata"]
    events = read_tsv(event_path)
    metadata = read_tsv(metadata_path)
    meta_schema = set(metadata[0]) if metadata else set()
    check(meta_schema == META_FIELDS, "AN metadata schema changed or contains non-metadata fields", errors)
    check(len(events) == 214, "frozen event roster row count is not 214", errors)
    pages = list(spec["pages"])
    allowed_pages = set(pages)
    check(len(pages) == len(allowed_pages) == 13, "selector list is not 13 unique pages", errors)
    check({r["page"] for r in metadata} == allowed_pages, "metadata page set differs from frozen selectors", errors)
    check(not any(r["page"].startswith("f84") for r in metadata), "forbidden f84 metadata present", errors)
    check({r["edition"] for r in metadata} == set(EDITION_ORDER), "metadata edition set differs", errors)
    check(all({r["edition"] for r in metadata if r["page"] == page} == set(EDITION_ORDER)
              for page in pages), "one or more selectors lack a reader's metadata", errors)

    # Recreate the 30 cells first. The metadata grant covers only side
    # selectors represented by those cells, not all 214 frozen events.
    all_by_cell: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for e in events:
        all_by_cell[(e["edition"], e["base"], e["folio"])].append(e)
    scoped_cell_events = []
    for _, cell_events in sorted(all_by_cell.items()):
        if any(e["lead"] == "p" for e in cell_events) and any(e["lead"] == "y" for e in cell_events):
            scoped_cell_events.extend(cell_events)
    event_pages = {r["locus"].rsplit(".", 1)[0] for r in scoped_cell_events}
    check(event_pages == allowed_pages, "13 selectors do not equal the 30-cell event side selectors", errors)
    check(all(r["lead"] in ("p", "y") for r in events), "unexpected event lead", errors)
    check(all(r["locus"].rsplit(".", 1)[0].startswith(r["folio"]) for r in scoped_cell_events),
          "event locus/physical-folio parsing failed", errors)

    # Check complete group-index inventories and line-constant metadata, then
    # use explicit source_row_index order rather than a locus-number guess.
    raw_lines: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in metadata:
        raw_lines[(row["edition"], row["page"], row["locus"])].append(row)
    line_info: dict[tuple[str, str, str], dict[str, str | int]] = {}
    complete_line_count = 0
    for key, rows in raw_lines.items():
        try:
            counts = [int(r["source_group_count"]) for r in rows]
            indices = sorted(int(r["source_group_index"]) for r in rows)
            row_indexes = [int(r["source_row_index"]) for r in rows]
            n = counts[0]
            inventory_ok = n > 0 and indices == list(range(1, n + 1)) and len(set(counts)) == 1
            constants_ok = all(len({r[name] for r in rows}) == 1 for name in (
                "kind", "source_row_index", "source_group_count", "paragraph_start", "paragraph_end"))
            numeric_ok = len(set(row_indexes)) == 1
            complete = inventory_ok and constants_ok and numeric_ok
            row = dict(rows[0])
            row["complete"] = int(complete)
            row["_order"] = row_indexes[0]
            row["_inventory_ok"] = int(inventory_ok)
            row["_constants_ok"] = int(constants_ok and numeric_ok)
        except (KeyError, ValueError, IndexError):
            row = dict(rows[0])
            row["complete"] = 0
            row["_order"] = 10**18
            row["_inventory_ok"] = 0
            row["_constants_ok"] = 0
        line_info[key] = row
        complete_line_count += int(row["complete"] == 1)

    ordered: dict[tuple[str, str], list[dict[str, str | int]]] = {}
    order_unique = True
    for edition in EDITION_ORDER:
        for page in pages:
            selected = [r for (e, p, _), r in line_info.items() if e == edition and p == page]
            selected.sort(key=lambda r: (int(r["_order"]), str(r["locus"])))
            nums = [int(r["_order"]) for r in selected if int(r["_order"]) < 10**18]
            if len(nums) != len(set(nums)):
                order_unique = False
            ordered[(edition, page)] = selected
    check(order_unique, "source_row_index is not unique within a selector", errors)

    expected_consensus: list[dict[str, str | int]] = []
    expected_frames: list[dict[str, str]] = []
    expected_exclusions: list[dict[str, str]] = []
    membership: dict[str, str] = {}
    rank: dict[str, int] = {}
    same_ordered_lists = True
    order_mismatch_pages = []
    for page in pages:
        z = ordered[("ZL3b", page)]
        it = ordered[("IT2a", page)]
        z_loci = [str(r["locus"]) for r in z]
        it_loci = [str(r["locus"]) for r in it]
        if z_loci != it_loci:
            same_ordered_lists = False
            order_mismatch_pages.append(page)
            expected_exclusions.append({"page": page, "loci": "|".join(z_loci),
                                        "reason": "PAGE_ORDER_OR_LOCUS_DISAGREEMENT"})
            continue

        pending: list[str] = []
        for idx, (zr, ir) in enumerate(zip(z, it)):
            locus = str(zr["locus"])
            rank[locus] = idx
            fields_agree = all(zr[field] == ir[field] for field in
                               ("kind", "paragraph_start", "paragraph_end"))
            complete = int(zr["complete"]) == 1 and int(ir["complete"]) == 1
            flags_well_formed = zr["paragraph_start"] in ("0", "1") and zr["paragraph_end"] in ("0", "1")
            valid = complete and fields_agree and flags_well_formed
            is_p_line = zr["kind"] == "P"
            expected_consensus.append({
                "page": page, "locus": locus, "index": idx,
                "kind": str(zr["kind"]) if valid else "UNKNOWN",
                "start": str(zr["paragraph_start"]) if valid else "NA",
                "end": str(zr["paragraph_end"]) if valid else "NA",
            })

            # Unknown or non-P lines invalidate an open frame and themselves
            # remain unassigned. A well-formed unexpected start closes the old
            # incomplete run and is eligible to seed a new frame.
            if not valid or not is_p_line:
                if pending:
                    expected_exclusions.append({"page": page, "loci": "|".join(pending),
                                                "reason": "INTERRUPTED_OR_UNKNOWN_BOUNDARY"})
                pending = []
                expected_exclusions.append({"page": page, "loci": locus,
                                            "reason": "UNKNOWN_BOUNDARY" if not valid else "NON_P"})
                continue
            if zr["paragraph_start"] == "1":
                if pending:
                    expected_exclusions.append({"page": page, "loci": "|".join(pending),
                                                "reason": "NEW_START_BEFORE_END"})
                pending = [locus]
            elif pending:
                pending.append(locus)
            else:
                expected_exclusions.append({"page": page, "loci": locus, "reason": "NO_KNOWN_START"})
            if zr["paragraph_end"] == "1" and pending:
                fid = pending[0] + "--" + pending[-1]
                expected_frames.append({"frame": fid, "page": page, "start": pending[0],
                                        "end": pending[-1], "loci": "|".join(pending)})
                for member in pending:
                    membership[member] = fid
                pending = []
        if pending:
            expected_exclusions.append({"page": page, "loci": "|".join(pending), "reason": "NO_KNOWN_END"})
    # Check event flags only for the events inside the granted selector set.
    # At each locus, their start flag must equal the shared ZL3b/IT2a projection
    # used by GDT1074. RF's own flags never participate in frame construction.
    event_by_key: dict[tuple[str, str, str], dict[str, str]] = {}
    projected_starts: dict[str, str] = {}
    for locus in {e["locus"] for e in scoped_cell_events}:
        zrow = line_info.get(("ZL3b", locus.rsplit(".", 1)[0], locus))
        irow = line_info.get(("IT2a", locus.rsplit(".", 1)[0], locus))
        if zrow and irow and zrow["paragraph_start"] == irow["paragraph_start"] and zrow["paragraph_start"] in ("0", "1"):
            projected_starts[locus] = str(zrow["paragraph_start"])
        else:
            projected_starts[locus] = "NA"
    for e in scoped_cell_events:
        key = (e["edition"], e["base"], e["locus"])
        check(key not in event_by_key, f"duplicate frozen event identity: {key}", errors)
        event_by_key[key] = e
        check((e["edition"], e["locus"].rsplit(".", 1)[0], e["locus"]) in line_info,
              f"event has no underlying metadata row: {key}", errors)
        check(e["start"] == projected_starts[e["locus"]],
              f"event start flag is not the ZL/IT consensus projection: {key}", errors)

    # Establish all 30 cells from the frozen event roster and retain each full
    # p-by-y Cartesian product, including cross-side and unresolved cases.
    by_cell = all_by_cell
    expected_pairs: list[dict[str, str]] = []
    expected_cells: list[dict[str, str | int]] = []
    for (edition, base, folio), cell_events in sorted(by_cell.items()):
        p_events = [e for e in cell_events if e["lead"] == "p"]
        y_events = [e for e in cell_events if e["lead"] == "y"]
        if not p_events or not y_events:
            continue
        local = []
        for p in p_events:
            for y in y_events:
                p_page, y_page = p["locus"].rsplit(".", 1)[0], y["locus"].rsplit(".", 1)[0]
                p_frame, y_frame = membership.get(p["locus"], ""), membership.get(y["locus"], "")
                order = "UNRESOLVED"
                if p_page != y_page:
                    status = "CROSS_SIDE_SELECTOR"
                else:
                    if p["locus"] in rank and y["locus"] in rank:
                        order = "P_BEFORE_Y" if rank[p["locus"]] < rank[y["locus"]] else "Y_BEFORE_P"
                    status = ("UNRESOLVED_BOUNDARY" if not p_frame or not y_frame else
                              "SAME_PARAGRAPH" if p_frame == y_frame else "DIFFERENT_PARAGRAPHS")
                row = {
                    "edition": edition, "base": base, "folio": folio,
                    "p_locus": p["locus"], "y_locus": y["locus"],
                    "p_form": p["form"], "y_form": y["form"],
                    "p_start": p["start"], "y_start": y["start"],
                    "p_frame": p_frame, "y_frame": y_frame,
                    "order": order, "status": status,
                }
                expected_pairs.append(row)
                local.append(row)
        expected_cells.append({
            "edition": edition, "base": base, "folio": folio,
            "pairs": len(local),
            "statuses": "|".join(sorted({r["status"] for r in local})),
            "same_paragraph_p_before_y": sum(r["status"] == "SAME_PARAGRAPH" and r["order"] == "P_BEFORE_Y" for r in local),
            "paragraph_head_p_before_y": sum(r["status"] == "SAME_PARAGRAPH" and r["order"] == "P_BEFORE_Y" and r["p_start"] == "1" for r in local),
        })

    expected_result = {
        "scope": "All frozen same-base/same-leaf p/y cells; source-marked same-side paragraphs only",
        "cells": len(expected_cells),
        "pairs": len(expected_pairs),
        "complete_physical_frames": len(expected_frames),
        "reader_counts": {
            edition: dict(Counter(row["status"] for row in expected_pairs if row["edition"] == edition))
            for edition in EDITION_ORDER
        },
        "ordered_same_paragraph": [row for row in expected_pairs if row["status"] == "SAME_PARAGRAPH"],
        "claim_ceiling": "Local scope opportunity only; no shared referent, meaning, normalization, significance or independent confirmation",
    }
    check(len(expected_cells) == 30, f"reconstructed cells={len(expected_cells)}, expected 30", errors)
    check(len(expected_pairs) == 32, f"reconstructed Cartesian pairs={len(expected_pairs)}, expected 32", errors)
    check(len(expected_frames) == 82, f"reconstructed complete frames={len(expected_frames)}, expected 82", errors)

    # Compare the independent reconstruction with every supplied exhaustive
    # artifact and with the compact result. TSV fields are normalized as strings.
    def compare_tsv(name: str, expected: list[dict], fields: list[str]) -> bool:
        actual = read_tsv(EXP / "artifacts" / name)
        exp_rows = [{field: str(row[field]) for field in fields} for row in expected]
        act_rows = [{field: row[field] for field in fields} for row in actual]
        ok = act_rows == exp_rows
        check(ok, f"artifact mismatch: {name}", errors)
        return ok

    consensus_fields = ["page", "locus", "index", "kind", "start", "end"]
    frame_fields = ["frame", "page", "start", "end", "loci"]
    exclusion_fields = ["page", "loci", "reason"]
    cell_fields = ["edition", "base", "folio", "pairs", "statuses",
                   "same_paragraph_p_before_y", "paragraph_head_p_before_y"]
    pair_fields = ["edition", "base", "folio", "p_locus", "y_locus", "p_form", "y_form",
                   "p_start", "y_start", "p_frame", "y_frame", "order", "status"]
    consensus_ok = compare_tsv("CONSENSUS_LINES.tsv", expected_consensus, consensus_fields)
    frames_ok = compare_tsv("FRAMES.tsv", expected_frames, frame_fields)
    exclusions_ok = compare_tsv("BOUNDARY_EXCLUSIONS.tsv", expected_exclusions, exclusion_fields)
    cells_ok = compare_tsv("CELLS.tsv", expected_cells, cell_fields)
    pairs_ok = compare_tsv("PAIRS.tsv", expected_pairs, pair_fields)
    actual_result = load_json(EXP / "artifacts/RESULT.json")
    result_ok = actual_result == expected_result
    check(result_ok, "artifact mismatch: RESULT.json", errors)

    # Every RF frame/order is inherited from the one physical ZL/IT consensus;
    # this check records the dependency without treating three editions as n.
    rf_event_count = sum(e["edition"] == "RF1b" for e in events)
    rf_projected_known = sum(e["edition"] == "RF1b" and e["start"] in ("0", "1") for e in events)
    rf_projected_unknown = rf_event_count - rf_projected_known
    same_rows = [r for r in expected_pairs if r["status"] == "SAME_PARAGRAPH"]
    ordered_same_rows = [r for r in same_rows if r["order"] == "P_BEFORE_Y"]
    p_heads = [r for r in ordered_same_rows if r["p_start"] == "1"]
    mismatch_pairs = [r for r in expected_pairs
                      if r["p_locus"].rsplit(".", 1)[0] in order_mismatch_pages
                      and r["p_locus"].rsplit(".", 1)[0] == r["y_locus"].rsplit(".", 1)[0]]
    mismatch_pairs_unresolved = all(r["status"] == "UNRESOLVED_BOUNDARY" for r in mismatch_pairs)
    check(mismatch_pairs_unresolved,
          "same-side pairs on locus/order-mismatched selectors were not all unresolved", errors)
    validation = {
        "status": "PASS" if not errors else "FAIL",
        "independent_reconstruction": True,
        "runner_imported": False,
        "raw_source_tsv_parsed": False,
        "source_tsv_digest_only": True,
        "input_digest_checks": digest_checks,
        "metadata_schema_metadata_only": meta_schema == META_FIELDS,
        "metadata_rows": len(metadata),
        "complete_group_inventory_lines": complete_line_count,
        "ordered_zl_it_first_group_lists_match_all_selectors": same_ordered_lists,
        "ordered_locus_mismatch_selectors": order_mismatch_pages,
        "same_side_pairs_on_mismatch_selectors": len(mismatch_pairs),
        "mismatch_selector_pairs_retained_as_unresolved": mismatch_pairs_unresolved,
        "source_row_index_unique_within_selector": order_unique,
        "selected_side_selectors": len(allowed_pages),
        "frozen_events": len(events),
        "reconstructed_cells": len(expected_cells),
        "reconstructed_cartesian_pairs": len(expected_pairs),
        "reconstructed_complete_frames": len(expected_frames),
        "pair_status_counts": expected_result["reader_counts"],
        "same_paragraph_pairs": len(same_rows),
        "same_paragraph_p_before_y_pairs": len(ordered_same_rows),
        "same_paragraph_p_before_y_where_p_starts_frame": len(p_heads),
        "rf1b_events": rf_event_count,
        "rf1b_projected_start_known": rf_projected_known,
        "rf1b_projected_start_unknown": rf_projected_unknown,
        "rf1b_boundary_source": "ZL3b/IT2a agreed physical metadata; RF1b metadata not used to build frames",
        "artifact_checks": {
            "CONSENSUS_LINES.tsv": consensus_ok,
            "FRAMES.tsv": frames_ok,
            "BOUNDARY_EXCLUSIONS.tsv": exclusions_ok,
            "CELLS.tsv": cells_ok,
            "PAIRS.tsv": pairs_ok,
            "RESULT.json": result_ok,
        },
        "errors": errors,
        "claim_ceiling": "Metadata fidelity only; no meaning or independent confirmation claim",
    }
    write_json(EXP / "artifacts/VALIDATION.json", validation)
    if errors:
        print("GDT1099 metadata validation FAIL: " + "; ".join(errors), file=sys.stderr)
        return 1
    print(f"GDT1099 metadata validation PASS: {len(expected_cells)} cells, {len(expected_pairs)} pairs, {len(expected_frames)} frames")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
