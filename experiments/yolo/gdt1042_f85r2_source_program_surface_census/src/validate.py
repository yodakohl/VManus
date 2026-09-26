#!/usr/bin/env python3
"""Independent GDT1042 replay from the guarded, frozen projection."""
from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
EXP = ROOT / "experiments/yolo/gdt1042_f85r2_source_program_surface_census"
ART = EXP / "artifacts"
PROJECTION = ART / "guarded_projection.tsv"
LOCK = EXP / "src/PREREG_LOCK.json"
METHOD = EXP / "METHOD.md"
EDITIONS = ("ZL3b", "IT2a", "RF1b")
BLOCKS = ("N", "E", "S", "W")
LINE_BLOCK = {**{i: "N" for i in range(2, 7)}, **{i: "E" for i in range(7, 12)},
              **{i: "S" for i in range(12, 18)}, **{i: "W" for i in range(18, 24)}}
QUERY_COLUMNS = ("source_group_id,edition,locus,page,source_group_index,source_group_count,"
                 "paragraph_start,paragraph_end,left_separator,right_separator,ivtff_group_raw")
QUERY = ["./vmanus-exp", "query-tsv",
         "experiments/semantic_assumptions/results/source_separator_transcription.tsv",
         "--selector", "page", "--allow", "f85r2", "--columns", QUERY_COLUMNS]


def fail(msg: str) -> None:
    raise AssertionError(msg)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_tsv_bytes(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    raw = path.read_bytes()
    rdr = csv.DictReader(io.StringIO(raw.decode("utf-8"), newline=""), delimiter="\t")
    if not rdr.fieldnames:
        fail(f"missing TSV header: {path.relative_to(ROOT)}")
    return list(rdr.fieldnames), list(rdr)


def json_compact(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))


def loc(g: dict, include_block=True, include_position=True) -> dict:
    d = {}
    if include_block:
        d["block"] = g["block"]
    d["locus"] = g["locus"]
    d["source_group_id"] = g["source_group_id"]
    d["index"] = g["source_group_index"]
    if include_position:
        d["position"] = g["within_line_position"]
    return d


def lev_distance(a: str, b: str) -> int:
    """Unit-cost insertion/deletion/substitution Levenshtein DP; no swap edge."""
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(cur[-1] + 1, prev[j] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def row_key(row: dict[str, str], headers: list[str]) -> tuple[str, ...]:
    return tuple(row.get(h, "") for h in headers)


def compare_table(name: str, expected: list[dict[str, str]]) -> dict:
    path = ART / name
    headers, actual = read_tsv_bytes(path)
    if len(actual) != len(expected):
        fail(f"{name}: row count actual={len(actual)} expected={len(expected)}")
    if any(set(row) != set(headers) for row in expected):
        fail(f"{name}: independent table schema mismatch")
    a = Counter(row_key(row, headers) for row in actual)
    e = Counter(row_key(row, headers) for row in expected)
    if a != e:
        missing = list((e - a).items())[:2]
        extra = list((a - e).items())[:2]
        fail(f"{name}: full-row mismatch; missing={missing!r}; extra={extra!r}")
    return {"rows": len(actual), "sha256": digest(path.read_bytes()), "exact_rows": True}


def main() -> None:
    # Verify the preregistration lock before consulting its claimed projection hash.
    lock = json.loads(LOCK.read_text(encoding="utf-8"))
    method_hash = digest(METHOD.read_bytes())
    if method_hash != lock["sha256"]:
        fail(f"METHOD hash mismatch: computed {method_hash}, locked {lock['sha256']}")

    # The sole access to the mixed source is the selector-first guarded command.
    query = subprocess.run(QUERY, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           check=False)
    if query.returncode:
        fail(f"guarded query failed ({query.returncode}): {query.stderr.decode('utf-8', 'replace')}")
    projection_bytes = PROJECTION.read_bytes()
    if query.stdout != projection_bytes:
        fail("guarded query stdout differs byte-for-byte from frozen projection")
    result = json.loads((ART / "RESULT.json").read_text(encoding="utf-8"))
    projection_hash = digest(projection_bytes)
    if projection_hash != result["input"]["projection_sha256"]:
        fail("guarded projection checksum does not match registered result")
    if result["input"]["guarded_query"] != " ".join(QUERY):
        fail("registered guarded query differs from independently executed query")
    if digest(query.stderr) != result["input"]["query_guard_stderr_sha256"]:
        fail("guard stderr checksum differs from registered result")
    stderr_text = query.stderr.decode("utf-8")
    m = re.search(r"GUARD_STATS\s+(\{.*\})", stderr_text)
    if not m:
        fail("guard emitted no GUARD_STATS")
    stats = json.loads(m.group(1))
    if stats != {"selected": 473, "skipped_forbidden": 2122, "skipped_not_allowed": 112875}:
        fail(f"unexpected guard statistics: {stats}")

    hdr, src_rows = read_tsv_bytes(PROJECTION)
    expected_headers = QUERY_COLUMNS.split(",")
    if hdr != expected_headers:
        fail(f"projection columns mismatch: {hdr!r}")
    if len(src_rows) != 473:
        fail(f"projection row count={len(src_rows)}, expected 473")
    ids = [r["source_group_id"] for r in src_rows]
    if len(ids) != len(set(ids)):
        fail("duplicate source_group_id in projection")
    if any(r["page"] != "f85r2" or r["edition"] not in EDITIONS for r in src_rows):
        fail("unexpected page or edition in projection")

    # Independently establish line completeness and position labels from index/count.
    line_groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for source in src_rows:
        r = dict(source)
        try:
            idx, count = int(r["source_group_index"]), int(r["source_group_count"])
            n = int(r["locus"].rsplit(".", 1)[1])
        except Exception as exc:
            fail(f"malformed index/locus row {r}: {exc}")
        if r["locus"] != f"f85r2.{n}" or not 1 <= n <= 24 or not 1 <= idx <= count:
            fail(f"invalid locus/index/count: {r}")
        key = (r["edition"], r["locus"])
        line_groups[key].append(r)
    if set(line_groups) != {(e, f"f85r2.{n}") for e in EDITIONS for n in range(1, 25)}:
        fail("edition/line coverage is not exactly 3 x lines 1..24")
    checks = []
    groups: list[dict] = []
    for edition in EDITIONS:
        for n in range(1, 25):
            locus = f"f85r2.{n}"
            rows = line_groups[(edition, locus)]
            rows.sort(key=lambda r: int(r["source_group_index"]))
            counts = {int(r["source_group_count"]) for r in rows}
            count = len(rows)
            if counts != {count} or [int(r["source_group_index"]) for r in rows] != list(range(1, count + 1)):
                fail(f"incomplete index sequence for {edition} {locus}: {count} rows, declared={counts}")
            block = LINE_BLOCK.get(n, "OUTSIDE")
            checks.append({"edition": edition, "locus": locus, "groups": count, "complete": True})
            for j, r in enumerate(rows):
                r["source_group_index"] = int(r["source_group_index"])
                r["source_group_count"] = count
                r["paragraph_start"] = int(r["paragraph_start"])
                r["paragraph_end"] = int(r["paragraph_end"])
                r["block"] = block
                r["within_line_position"] = ("first_last" if count == 1 else
                                              "first" if j == 0 else
                                              "last" if j == count - 1 else "interior")
                groups.append(r)
    if len(checks) != 72 or sum(1 for c in checks if c["locus"].endswith(tuple(f".{n}" for n in range(2,24)))) != 66:
        fail("not all 22 spatial and 2 outside lines per edition were checked")

    # Complete native-group table.
    native_expected = []
    native_headers = ["edition","block","locus","source_group_id","source_group_index","source_group_count","within_line_position","paragraph_start","paragraph_end","left_separator","right_separator","ivtff_group_raw"]
    for g in groups:
        native_expected.append({h: str(g[h]) for h in native_headers})
    table_checks = {"native_groups.tsv": compare_table("native_groups.tsv", native_expected)}

    # Fixed block line/group/form counts.
    bc = []
    for e in EDITIONS:
        for b in (*BLOCKS, "OUTSIDE"):
            gs = [g for g in groups if g["edition"] == e and g["block"] == b]
            bc.append({"edition":e,"block":b,"line_count":str(len({g['locus'] for g in gs})),"group_count":str(len(gs)),"distinct_complete_forms":str(len({g['ivtff_group_raw'] for g in gs}))})
    table_checks["block_counts.tsv"] = compare_table("block_counts.tsv", bc)

    # Exact form sets, exhaustive occurrence lists, and all six block-pair intersections.
    repeated = []
    intersections = []
    intersection_pair_sets = []
    for e in EDITIONS:
        per_block = {b: [g for g in groups if g["edition"] == e and g["block"] == b] for b in BLOCKS}
        form_locs = defaultdict(list)
        for b in BLOCKS:
            for g in per_block[b]:
                form_locs[g["ivtff_group_raw"]].append(loc(g))
        for form, occurrences in sorted(form_locs.items()):
            if len(occurrences) >= 2:
                block_names = [b for b in BLOCKS if any(x["block"] == b for x in occurrences)]
                repeated.append({"edition":e,"form_raw":form,"occurrence_count":str(len(occurrences)),
                    "within_block_recurrence":str(any(sum(x["block"] == b for x in occurrences) >= 2 for b in BLOCKS)),
                    "cross_block_recurrence":str(len(block_names) >= 2),"blocks":",".join(block_names),"locations_json":json_compact(occurrences)})
        sets = {b: {g["ivtff_group_raw"] for g in per_block[b]} for b in BLOCKS}
        for ba, bb in combinations(BLOCKS, 2):
            shared_forms = sorted(sets[ba] & sets[bb])
            intersection_pair_sets.append({"edition":e,"block_a":ba,"block_b":bb,"shared_forms":shared_forms})
            for form in shared_forms:
                la = [loc(g, include_block=False, include_position=False) for g in per_block[ba] if g["ivtff_group_raw"] == form]
                lb = [loc(g, include_block=False, include_position=False) for g in per_block[bb] if g["ivtff_group_raw"] == form]
                intersections.append({"edition":e,"block_a":ba,"block_b":bb,"form_raw":form,"locations_a_json":json_compact(la),"locations_b_json":json_compact(lb)})
    table_checks["repeated_forms.tsv"] = compare_table("repeated_forms.tsv", repeated)
    table_checks["block_intersections.tsv"] = compare_table("block_intersections.tsv", intersections)

    # All contiguous 2/3-group sequences wholly within a line; separator pairs retained.
    occurrences_by_seq_sig = defaultdict(list)
    totals = Counter()
    for e in EDITIONS:
        lines = [(key, sorted(v, key=lambda g: g["source_group_index"])) for key,v in line_groups.items() if key[0] == e]
        for (edition,locus), rows in lines:
            nline = int(locus.rsplit(".", 1)[1])
            block = LINE_BLOCK.get(nline, "OUTSIDE")
            for n in (2,3):
                for start in range(0, len(rows)-n+1):
                    chunk = rows[start:start+n]
                    seq = tuple(g["ivtff_group_raw"] for g in chunk)
                    totals[(e,n,seq)] += 1
                    sig = tuple((chunk[i]["right_separator"], chunk[i+1]["left_separator"]) for i in range(n-1))
                    occurrences_by_seq_sig[(e,n,seq,sig)].append({"block":block,"locus":locus,"start_index":chunk[0]["source_group_index"],"source_group_ids":[g["source_group_id"] for g in chunk]})
    repeated_ng = []
    seq_signatures = defaultdict(set)
    for e,n,seq,sig in occurrences_by_seq_sig:
        seq_signatures[(e,n,seq)].add(sig)
    for (e,n,seq,sig), occs in sorted(occurrences_by_seq_sig.items()):
        total = totals[(e,n,seq)]
        if total < 2:
            continue
        repeated_ng.append({"edition":e,"n":str(n),"sequence_json":json_compact(list(seq)),"boundary_signature_json":json_compact([list(p) for p in sig]),
            "signature_occurrence_count":str(len(occs)),"surface_sequence_total_occurrences":str(total),"separator_signature_ambiguous":str(len(seq_signatures[(e,n,seq)]) > 1),"occurrences_json":json_compact(occs)})
    table_checks["repeated_ngrams.tsv"] = compare_table("repeated_ngrams.tsv", repeated_ng)

    # Exhaustively compare all distinct clean whole forms by independent DP distance.
    edit_pairs = []
    edit_summary = {}
    for e in EDITIONS:
        spatial = [g for g in groups if g["edition"] == e and g["block"] in BLOCKS]
        by_form = defaultdict(list)
        for g in spatial:
            by_form[g["ivtff_group_raw"]].append(loc(g))
        clean = sorted(form for form in by_form if re.fullmatch(r"[A-Za-z]+", form))
        n_candidates = len(clean)*(len(clean)-1)//2
        eligible = []
        for a,b in combinations(clean,2):
            d = lev_distance(a,b)
            if d == 1:
                eligible.append((a,b))
                edit_pairs.append({"edition":e,"form_a":a,"form_b":b,"distance":"1","operation_note":"Levenshtein insertion/deletion/substitution; transposition is not one edit",
                    "occurrence_count_a":str(len(by_form[a])),"occurrences_a_json":json_compact(by_form[a]),"occurrence_count_b":str(len(by_form[b])),"occurrences_b_json":json_compact(by_form[b])})
        allforms = {g["ivtff_group_raw"] for g in spatial}
        edit_summary[e] = {"spatial_group_occurrences":len(spatial),
                           "distinct_surface_forms":len(allforms),"clean_ascii_letter_forms":len(clean),
                           "excluded_nonclean_distinct_forms":len(allforms)-len(clean),
                           "excluded_nonclean_occurrences":sum(len(v) for f,v in by_form.items() if f not in set(clean)),
                           "candidate_unordered_clean_form_pairs":n_candidates,"distance_one_pairs":len(eligible)}
    table_checks["literal_edit1_pairs.tsv"] = compare_table("literal_edit1_pairs.tsv", edit_pairs)

    # Every line including outside lines: retain first/last raw groups and both separators.
    first_last = []
    for e in EDITIONS:
        for n in range(1,25):
            locus = f"f85r2.{n}"
            rows = sorted(line_groups[(e,locus)], key=lambda g: int(g["source_group_index"]))
            first, last = rows[0], rows[-1]
            first_last.append({"edition":e,"block":LINE_BLOCK.get(n,"OUTSIDE"),"locus":locus,"group_count":str(len(rows)),
                "first_group_raw":first["ivtff_group_raw"],"first_source_group_id":first["source_group_id"],"first_left_separator":first["left_separator"],"first_right_separator":first["right_separator"],
                "last_group_raw":last["ivtff_group_raw"],"last_source_group_id":last["source_group_id"],"last_left_separator":last["left_separator"],"last_right_separator":last["right_separator"]})
    table_checks["line_first_last.tsv"] = compare_table("line_first_last.tsv", first_last)

    # Verify every declared published table is included and row totals match RESULT.
    if result["completeness"]["projection_group_rows"] != len(groups) or result["completeness"]["unique_group_ids"] != len(set(ids)):
        fail("registered row/ID completeness metadata mismatch")
    if result["completeness"]["line_instances_checked"] != 72 or result["completeness"]["line_instances_complete"] is not True:
        fail("registered line completeness metadata mismatch")
    if result["completeness"]["line_checks"] != checks:
        fail("registered line checks differ from independent index reconstruction")
    summarized_tables = {k.removesuffix(".tsv"): v["rows"] for k,v in table_checks.items() if k != "native_groups.tsv"}
    if result["table_rows"] != summarized_tables:
        fail("RESULT table row counts mismatch independent table replay")
    if result["edit1_exclusion_and_pair_counts"] != edit_summary:
        fail("RESULT edit-pair diagnostics mismatch independent DP replay")

    validation = {
        "experiment":"GDT1042",
        "status":"PASS_INDEPENDENT_REPLAY",
        "method_sha256":method_hash,
        "guarded_projection_sha256":projection_hash,
        "guarded_query":" ".join(QUERY),
        "guard_stats":stats,
        "projection_rows":len(src_rows),
        "unique_source_group_ids":len(set(ids)),
        "complete_line_instances":len(checks),
        "spatial_line_instances":66,
        "outside_line_instances":6,
        "line_index_completeness":"Every edition/locus group index is exactly 1..declared source_group_count.",
        "independent_distance_algorithm":"Unit-cost Levenshtein dynamic program with insertion, deletion, and substitution only; every unordered pair of distinct clean ASCII-letter whole forms was enumerated.",
        "tables":table_checks,
        "all_six_block_pair_intersections_per_reader":intersection_pair_sets,
        "edit1_diagnostics":edit_summary,
        "limitations":"Descriptive surface replay only; no semantic interpretation or independence claim. ZL3b, IT2a, and RF1b are alternate readings of one manuscript."
    }
    target = ART / "VALIDATION.json"
    target.write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status":validation["status"],"tables":{k:v["rows"] for k,v in table_checks.items()},"output":str(target.relative_to(ROOT))}, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"VALIDATION FAILED: {exc}", file=sys.stderr)
        raise
