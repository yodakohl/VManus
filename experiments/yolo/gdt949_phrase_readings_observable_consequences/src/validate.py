#!/usr/bin/env python3
"""Independent, source-bounded audit for GDT949 (no semantic scoring)."""
from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

EXP = Path(__file__).resolve().parents[1]
ROOT = EXP.parents[2]
SPEC_PATH = EXP / "src/SPEC.json"
LOCK_PATH = EXP / "PREREG_LOCK.json"
CLOCK_PATH = EXP / "CANDIDATE_LOCK.json"
EDITIONS = ("ZL3b", "IT2a", "RF1b")
FAMILIES = (("cheo", "cho"), ("oka", "ota"))
CELLS = ("rr", "rl", "lr", "ll")


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fail(errors, check, **details):
    errors.append(dict(check=check, **details))


def leaf(page: str):
    match = re.match(r"f(\d+)", str(page))
    return int(match.group(1)) if match else None


def check_locks(errors):
    checked = []
    for lock_path in (LOCK_PATH, CLOCK_PATH):
        lock = read(lock_path)
        for rel, wanted in lock.get("files", {}).items():
            # PREREG_LOCK uses repository-relative paths; the candidate lock
            # intentionally uses paths relative to this experiment directory.
            path = (ROOT / rel) if (ROOT / rel).is_file() else (EXP / rel)
            if not path.is_file():
                fail(errors, "LOCK_FILE_MISSING", file=rel)
                continue
            checked.append(rel)
            if digest(path) != wanted:
                fail(errors, "LOCK_HASH_MISMATCH", file=rel)
    return checked


def guarded_source(spec, errors):
    """Rebuild lines and occurrences from raw guarded JSON, without extract.py."""
    if tuple(spec.get("editions", ())) != EDITIONS:
        fail(errors, "EDITION_SCOPE", actual=spec.get("editions"))
    if {tuple(x) for x in spec.get("families", ())} != set(FAMILIES):
        fail(errors, "FAMILY_SCOPE", actual=spec.get("families"))
    lines, occurrences = {}, []
    for source in spec.get("sources", ()):
        path = ROOT / source
        if not path.is_file():
            fail(errors, "SOURCE_MISSING", source=source)
            continue
        packet = read(path)
        columns = packet.get("group_columns", ())
        for raw_line in packet.get("lines", ()):
            meta = raw_line.get("metadata", {})
            edition, locus = meta.get("edition"), meta.get("locus")
            if meta.get("kind") != "P":
                continue
            if str(meta.get("page", "")).startswith("f84") or meta.get("page") == "f116v":
                fail(errors, "SEALED_PAGE_IN_SOURCE", edition=edition, locus=locus)
            key = (edition, locus)
            if key in lines:
                fail(errors, "DUPLICATE_FULL_LINE", key=key)
            groups = [dict(zip(columns, row)) for row in raw_line.get("groups", ())]
            lines[key] = {"metadata": meta, "groups": groups, "source": source}
            for a, b in zip(groups, groups[1:]):
                wa, wb = a.get("ivtff_group_raw", ""), b.get("ivtff_group_raw", "")
                if not (re.fullmatch(r"[a-z]+", wa) and re.fullmatch(r"[a-z]+", wb)):
                    continue
                if wa[-1] not in "rl" or wb[-1] not in "rl":
                    continue
                family = (wa[:-1], wb[:-1])
                if family not in FAMILIES:
                    continue
                if (a.get("right_separator") != b.get("left_separator") or
                        a.get("right_separator") != "DEFINITE_SPACE"):
                    continue
                try:
                    contiguous = int(b["source_group_index"]) == int(a["source_group_index"]) + 1
                except (KeyError, TypeError, ValueError):
                    contiguous = False
                if not contiguous:
                    continue
                occurrences.append({
                    "edition": edition, "locus": locus, "page": meta.get("page"),
                    "family": f"{family[0]}/{family[1]}",
                    "cell": wa[-1] + wb[-1], "words": [wa, wb],
                    "ids": [a.get("source_group_id"), b.get("source_group_id")],
                    "group_count": len(groups),
                })
    return lines, occurrences


def occurrence_key(row):
    return (row.get("edition"), row.get("locus"), row.get("family"),
            row.get("cell"), tuple(row.get("ids", ())))


def choose_selection(occurrences):
    selected = []
    for family in FAMILIES:
        fname = "/".join(family)
        rows = [o for o in occurrences if o["edition"] == "ZL3b" and o["family"] == fname]
        pairs = [(a, b) for a in rows if a["cell"] == "rr"
                 for b in rows if b["cell"] == "ll" and leaf(a["page"]) != leaf(b["page"])]
        if not pairs:
            continue
        a, b = min(pairs, key=lambda pair: (
            sum(x["group_count"] for x in pair),
            tuple((x["page"], x["locus"], tuple(x["ids"])) for x in pair)))
        selected.extend({"family": fname, "cell": x["cell"],
                         "locus": x["locus"], "page": x["page"]} for x in (a, b))
    return selected


def check_packets(lines, occurrences, errors):
    paths = {name: EXP / "artifacts" / name for name in
             ("ALL_OCCURRENCES.json", "ALL_MATCHING_LINES.json", "SOURCE_PACKET.json")}
    if any(not path.is_file() for path in paths.values()):
        fail(errors, "GENERATED_PACKET_MISSING")
        return {}, set()
    all_rows = read(paths["ALL_OCCURRENCES.json"])
    matching = read(paths["ALL_MATCHING_LINES.json"])
    packet = read(paths["SOURCE_PACKET.json"])
    if sorted(occurrence_key(x) for x in all_rows) != sorted(occurrence_key(x) for x in occurrences):
        fail(errors, "PAIR_ENUMERATION_CONTENT")
    if len(all_rows) != 54:
        fail(errors, "PAIR_ENUMERATION_TOTAL", expected=54, actual=len(all_rows))
    expected_counts = Counter((x["family"], x["cell"]) for x in occurrences)
    actual_counts = Counter((x.get("family"), x.get("cell")) for x in all_rows)
    if actual_counts != expected_counts:
        fail(errors, "PAIR_ENUMERATION_COUNTS", expected=dict(expected_counts), actual=dict(actual_counts))
    if set(x.get("cell") for x in all_rows) != set(CELLS):
        fail(errors, "PAIR_CELL_SET", actual=sorted({x.get("cell") for x in all_rows}))
    expected_selection = choose_selection(occurrences)
    if packet.get("selection") != expected_selection:
        fail(errors, "SELECTION_RULE_MISMATCH", expected=expected_selection,
             actual=packet.get("selection"))
    loci = {x["locus"] for x in expected_selection}
    expected_packet = [line for (edition, locus), line in sorted(lines.items()) if locus in loci]
    if packet.get("lines") != expected_packet:
        fail(errors, "PACKET_LINE_CONTENT")
    if len(packet.get("lines", ())) != 12:
        fail(errors, "PACKET_LINE_COUNT", expected=12, actual=len(packet.get("lines", ())))
    expected_matching_keys = {(x["edition"], x["locus"]) for x in occurrences}
    actual_matching_keys = {(x.get("metadata", {}).get("edition"), x.get("metadata", {}).get("locus"))
                            for x in matching}
    if len(matching) != len(expected_matching_keys) or actual_matching_keys != expected_matching_keys:
        fail(errors, "MATCHING_LINE_SET", expected=len(expected_matching_keys), actual=len(matching))
    if matching != [lines[key] for key in sorted(expected_matching_keys)]:
        fail(errors, "MATCHING_LINE_CONTENT")
    return packet, loci


def tsv_rows(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def check_census(errors, occurrences):
    path = EXP / "artifacts/CENSUS.tsv"
    if not path.is_file():
        fail(errors, "CENSUS_MISSING")
        return []
    expected = []
    for edition in EDITIONS:
        for family in ("cheo/cho", "oka/ota"):
            rows = [o for o in occurrences if o["edition"] == edition and o["family"] == family]
            counts = Counter(o["cell"] for o in rows)
            expected.append({"edition": edition, "family": family,
                             **{cell: str(counts[cell]) for cell in CELLS}, "total": str(len(rows))})
    actual = [{key: row.get(key, "") for key in ("edition", "family", *CELLS, "total")}
              for row in tsv_rows(path)]
    if actual != expected:
        fail(errors, "CENSUS_CONTENT", expected=expected, actual=actual)
    return expected


def check_alignment(packet, model, errors):
    candidates = model.get("candidates", {})
    if set(candidates) != {"N", "S"}:
        fail(errors, "CANDIDATE_SET", actual=sorted(candidates))
    loci = {line["metadata"]["locus"] for line in packet.get("lines", ())}
    for cid, candidate in candidates.items():
        if len(candidate.get("lexicon", {})) != 33:
            fail(errors, "LEXICON_SIZE", candidate=cid, actual=len(candidate.get("lexicon", {})))
        if set(candidate.get("readings", {})) != loci:
            fail(errors, "READING_LOCUS_SET", candidate=cid)
    path = EXP / "artifacts/ALIGNMENT.tsv"
    if not path.is_file():
        fail(errors, "ALIGNMENT_MISSING")
        return {}
    rows = tsv_rows(path)
    coverage = {}
    expected_raw = [(line["metadata"]["edition"], group["source_group_id"],
                     group["ivtff_group_raw"])
                    for line in packet.get("lines", ()) for group in line["groups"]]
    for cid in candidates:
        mine = [row for row in rows if row.get("candidate") == cid]
        actual_raw = [(row.get("edition"), row.get("source_id"), row.get("raw")) for row in mine]
        if sorted(actual_raw) != sorted(expected_raw):
            fail(errors, "ALIGNMENT_POSITIONS", candidate=cid,
                 expected=len(expected_raw), actual=len(mine))
        unknown = [row for row in mine if row.get("status") != "STIPULATED"]
        rf_unknown = [row for row in unknown if row.get("edition") == "RF1b"]
        if len(mine) != 100:
            fail(errors, "ALIGNMENT_TOTAL", candidate=cid, expected=100, actual=len(mine))
        if len(rf_unknown) != 3 or any(row.get("edition") != "RF1b" for row in unknown):
            fail(errors, "OPEN_RF_CAPACITY", candidate=cid, actual=len(rf_unknown))
        coverage[cid] = {"positions": len(mine), "open_positions": len(unknown),
                          "open_rf_positions": len(rf_unknown),
                          "lexicon_forms": len(candidates[cid].get("lexicon", {}))}
    if len(rows) != 200:
        fail(errors, "ALIGNMENT_ALL_CANDIDATES", expected=200, actual=len(rows))
    return coverage


def check_consequences(model, census, errors):
    path = EXP / "artifacts/CONSEQUENCES.json"
    if not path.is_file():
        fail(errors, "CONSEQUENCES_MISSING")
        return
    rows = read(path)
    by_id = {row.get("id"): row for row in rows}
    for cid in ("D1", "D3", "D4"):
        if by_id.get(cid, {}).get("available") is not False:
            fail(errors, "UNAVAILABLE_BINDING_MARKED_AVAILABLE", id=cid)
    d2 = by_id.get("D2", {})
    if d2.get("available") is not True:
        fail(errors, "D2_UNAVAILABLE")
    else:
        expected = [{"edition": row["edition"], "family": row["family"],
                     "mixed": int(row["rl"]) + int(row["lr"]), "total": int(row["total"])}
                    for row in census]
        if d2.get("observed") != expected:
            fail(errors, "D2_OBSERVATION", expected=expected, actual=d2.get("observed"))
        if all(row["mixed"] == 0 for row in expected):
            fail(errors, "D2_NO_MIXED_CELL")
    if by_id.get("D5", {}).get("available") is not True:
        fail(errors, "D5_UNAVAILABLE")


def check_result(packet, coverage, errors):
    path = EXP / "artifacts/RESULT.json"
    if not path.is_file():
        fail(errors, "RESULT_MISSING")
        return
    result = read(path)
    for key, expected in (("total_pair_occurrences", 54), ("physical_selected_leaves", 4),
                          ("source_reader_lines", 12)):
        if result.get(key) != expected:
            fail(errors, "RESULT_COUNT", field=key, expected=expected, actual=result.get(key))
    candidates = {row.get("id"): row for row in result.get("candidates", ())}
    for cid in coverage:
        row = candidates.get(cid, {})
        if row.get("glossary_forms") != 33 or row.get("aligned_positions") != 100:
            fail(errors, "RESULT_CANDIDATE_COUNTS", candidate=cid, actual=row)
        if row.get("open_positions") != 3:
            fail(errors, "RESULT_OPEN_RF_COUNT", candidate=cid, actual=row)
    if result.get("semantic_confirmation_capacity") != 0 or result.get("reserves_opened") is not False:
        fail(errors, "RESULT_CLAIM_CEILING")


def main():
    errors = []
    checked = check_locks(errors)
    spec = read(SPEC_PATH)
    lines, occurrences = guarded_source(spec, errors)
    packet, loci = check_packets(lines, occurrences, errors)
    model = read(EXP / "src/CANDIDATES.json")
    census = check_census(errors, occurrences)
    coverage = check_alignment(packet, model, errors)
    check_consequences(model, census, errors)
    check_result(packet, coverage, errors)
    result = {
        "experiment": "GDT949", "independent": True,
        "status": "PASS" if not errors else "FAIL", "locked_files": checked,
        "source_files": len(spec.get("sources", ())), "pair_occurrences": len(occurrences),
        "pair_cells": {f"{family}:{cell}": count for (family, cell), count in
                       Counter((x["family"], x["cell"]) for x in occurrences).items()},
        "selected_loci": sorted(loci), "packet_lines": len(packet.get("lines", ())),
        "candidate_coverage": coverage, "errors": errors,
        "meaning_validated": False, "confirmed_words": 0,
        "claim_ceiling": "observable packet and reading audit only; D2 tests an added attachment bridge"
    }
    (EXP / "artifacts/VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    review = {
        "experiment": "GDT949", "reviewer": "independent_bounded_validator",
        "status": result["status"], "critical_issues": errors,
        "scope": {"sources": "six guarded GDT915 JSONs from SPEC", "reserves_opened": False,
                   "new_text_or_images": False},
        "checks": {"selection": "four shortest RR/LL complete lines on four leaves",
                   "pair_cells": 54, "source_reader_lines": 12,
                   "positions_per_candidate": 100, "lexicon_values_per_candidate": 33,
                   "open_rf_positions_per_candidate": 3},
        "semantic_decision": "D2 rejects the added universal adjacent-constituent bridge via mixed cells; it neither refutes nor confirms either isolated meaning.",
        "meaning_validated": False, "confirmed_words": 0,
        "frozen_comment_typo": "The model's 34-value comment is treated as a declared typo; the frozen lexicon has 33 values per candidate."
    }
    (EXP / "REVIEW.json").write_text(json.dumps(review, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
