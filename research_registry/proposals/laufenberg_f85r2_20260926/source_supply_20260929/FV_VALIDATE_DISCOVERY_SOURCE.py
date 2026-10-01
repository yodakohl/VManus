#!/usr/bin/env python3
"""Independent, discovery-only literal FV audit. No author/application access."""
import collections
import csv
import hashlib
import importlib.util
import io
import json
import re
import sqlite3
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = Path(__file__).resolve().parent
RELBASE = BASE.relative_to(ROOT)
READERS = ["ZL3b", "IT2a", "RF1b"]
LOCI = [f"f83r.{n}" for n in range(9, 18)] + [f"f83v.{n}" for n in range(21, 34)]
COLS = "source_group_id,edition,locus,page,section,currier,hand,code,kind,grammar_scope,source_row_index,source_group_index,source_group_count,paragraph_start,paragraph_end,left_separator,right_separator,ivtff_group_raw".split(",")
SOURCE = "experiments/semantic_assumptions/results/source_separator_transcription.tsv"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(name):
    return json.loads((BASE / name).read_text())


def main():
    errors = []

    def check(ok, kind, detail):
        if not ok:
            errors.append({"kind": kind, "detail": detail})

    contract = read("FV_SOURCE_CONTRACT.json")
    receipt = read("FV_AUTHOR_INPUT_RECEIPT.json")
    pin_results = []
    for item in receipt["inputs"]:
        path = ROOT / item["path"]
        actual = sha(path)
        ok = actual == item["sha256"] and path.stat().st_size == item["bytes"]
        pin_results.append({"path": item["path"], "expected_sha256": item["sha256"], "actual_sha256": actual, "match": ok})
        check(ok, "AUTHOR_RECEIPT_PIN", item["path"])
    for path, expected in contract["formal_and_input_pins"].items():
        check(sha(ROOT / path) == expected, "CONTRACT_INPUT_PIN", path)
    check(contract["canonical_source"]["columns"] == COLS, "CONTRACT_COLUMN_LIST", "Expected exact18 selected fields")
    check(contract["canonical_source"]["explicit_allows"] == LOCI, "CONTRACT_SELECTOR_LIST", "Expected exact22 discovery loci")
    packet = read("FV_DISCOVERY_PACKET.json")
    for path, expected in packet["input_hashes"].items():
        check(sha(ROOT / path) == expected, "PACKET_INPUT_PIN", path)
    check(packet["allowed_loci"] == LOCI, "PACKET_SELECTOR_LIST", "Wrong allowed_loci")
    check(packet["editions"] == READERS, "PACKET_READER_LIST", "Wrong reader list/order")
    argv = ["./vmanus-exp", "query-tsv", SOURCE, "--selector", "locus"]
    for locus in LOCI:
        argv += ["--allow", locus]
    argv += ["--columns", ",".join(COLS), "--forbid-prefix", "f84", "--forbid-prefix", "f84r"]
    query = subprocess.run(argv, cwd=ROOT, capture_output=True, check=True)
    text = query.stdout.decode("utf-8")
    source_reader = csv.DictReader(io.StringIO(text), delimiter="\t")
    check(source_reader.fieldnames == COLS, "SOURCE_HEADER", str(source_reader.fieldnames))
    rows = list(source_reader)
    guard = json.loads(query.stderr.decode().strip().split("GUARD_STATS ", 1)[1])
    check(guard["selected"] == len(rows), "GUARD_SELECTED_COUNT", "Selected count differs from independent rows")
    check(sha(BASE / "FV_DISCOVERY_GROUPS.tsv") == hashlib.sha256(query.stdout).hexdigest(), "TSV_PROJECTION_BYTES", "Guarded output versus native projection bytes")
    native_reader = csv.DictReader(io.StringIO((BASE / "FV_DISCOVERY_GROUPS.tsv").read_text()), delimiter="\t")
    check(native_reader.fieldnames == COLS, "TSV_HEADER", str(native_reader.fieldnames))
    native_rows = list(native_reader)
    check(native_rows == rows, "TSV_ROW_FIELD_ORDER", "Full exact canonical field/order comparison")
    packet_projection = [{k: group.get(k) for k in COLS} for group in packet["groups"]]
    check(packet_projection == rows, "JSON_ROW_FIELD_ORDER", "Full exact canonical field/order comparison")
    check(packet["raw_group_count"] == len(rows), "PACKET_GROUP_COUNT", "Count differs from independently queried rows")
    check(packet["query_receipt"]["projection_sha256"] == hashlib.sha256(query.stdout).hexdigest(), "QUERY_HASH_RECEIPT", "Projection hash mismatch")
    check(packet["query_receipt"]["command"] == argv, "QUERY_ARGV_RECEIPT", "Exact selectors/columns/forbidden prefixes differ")
    check(packet["query_receipt"]["guard_stats"] == guard, "QUERY_GUARD_RECEIPT", "Guard stats differ")
    ids = [r["source_group_id"] for r in rows]
    check(len(set(ids)) == len(ids), "DUPLICATE_NATIVE_ID", "Native IDs not unique")
    bycell = collections.defaultdict(list)
    for row in rows:
        check(row["locus"] in LOCI and row["edition"] in READERS, "SOURCE_SCOPE", row["source_group_id"])
        bycell[row["edition"], row["locus"]].append(row)
    cells = []
    for edition in READERS:
        for locus in LOCI:
            rs = bycell[edition, locus]
            cells.append({"edition": edition, "locus": locus, "groups": len(rs), "source_row_indexes": sorted({r["source_row_index"] for r in rs}), "native_paragraph_flags": sorted({(r["paragraph_start"], r["paragraph_end"]) for r in rs})})
            check(bool(rs), "MISSING_SOURCE_CELL", edition + "|" + locus)
            check([int(r["source_group_index"]) for r in rs] == list(range(1, len(rs) + 1)), "GROUP_INDEX_ORDER", edition + "|" + locus)
            check(all(int(r["source_group_count"]) == len(rs) for r in rs), "SOURCE_GROUP_COUNT", edition + "|" + locus)
            check(len({r["source_row_index"] for r in rs}) == 1, "SOURCE_ROW_IDENTITY", edition + "|" + locus)
            if rs:
                check(rs[0]["left_separator"] == "LINE_START" and rs[-1]["right_separator"] == "LINE_END", "LINE_EDGE", edition + "|" + locus)
                check(all(a["right_separator"] == b["left_separator"] for a, b in zip(rs, rs[1:])), "RAW_SEAM_AGREEMENT", edition + "|" + locus)
    # Import legacy pure functions without calling their old-packet/main routines.
    formal_path = ROOT / "experiments/yolo/gdt1051_frozen_grammar_local_application/src/run.py"
    spec = importlib.util.spec_from_file_location("fv_independent_legacy1051", formal_path)
    formal = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(formal)
    merges = formal.load_merges()
    replay_groups = []
    unit_ord = collections.Counter()
    for row, saved in zip(rows, packet["groups"]):
        unit = "FV_F83R_DISCOVERY" if row["page"] == "f83r" else "FV_F83V_DISCOVERY"
        unit_ord[unit, row["edition"]] += 1
        replay = formal.parse_group(unit, row)
        replay_groups.append(replay)
        check(saved["formal_gdt012_062"] == replay, "GROUP_FORMAL_REPLAY", row["source_group_id"])
        check(saved["unit_id"] == unit and saved["unit_reader_order"] == unit_ord[unit, row["edition"]], "UNIT_ORDER", row["source_group_id"])
        check(saved["native_paragraph_flags_available"] == (row["edition"] != "RF1b"), "NATIVE_FLAGS_AVAILABLE", row["source_group_id"])
    chunks = formal.make_chunks(replay_groups, merges)
    check(len(chunks) == len(packet["chunks"]), "CHUNK_COUNT", "Independent chunks differ")
    chunk_owner = {}
    for i, (actual, saved) in enumerate(zip(chunks, packet["chunks"]), 1):
        cid = f"FV_DISCOVERY_CHUNK_{i:04d}"
        check(saved == dict(actual, chunk_id=cid), "CHUNK_FORMAL_REPLAY", cid)
        for index in actual["group_indices"]:
            key = (actual["edition"], actual["locus"], index)
            check(key not in chunk_owner, "DUPLICATE_CHUNK_MEMBERSHIP", str(key))
            chunk_owner[key] = cid
    for row, saved in zip(rows, packet["groups"]):
        key = (row["edition"], row["locus"], int(row["source_group_index"]))
        check(saved["formal_gdt605_chunk_id"] == chunk_owner.get(key), "GROUP_CHUNK_REFERENCE", row["source_group_id"])
    check(len(chunk_owner) == len(rows), "CHUNK_SOURCE_CONSERVATION", "Each original group must occur exactly once")
    whole_types = sorted({r["ivtff_group_raw"] for r in rows if re.fullmatch("[a-z]+", r["ivtff_group_raw"])})
    check(sorted(packet["exact_whole_priors"]) == whole_types, "PRIOR_TYPE_SET", "Extra/missing discovery raw whole")
    con = sqlite3.connect("file:" + str(ROOT / "experiments/semantic_assumptions/cache/word_profiles.sqlite") + "?mode=ro", uri=True)
    cache_receipt = json.loads(con.execute("SELECT value FROM metadata WHERE key='receipt'").fetchone()[0])
    check(cache_receipt == packet["word_prior_receipt"], "CACHE_RECEIPT", "Metadata receipt differs")
    prior_cells = 0
    for word in whole_types:
        for edition in READERS:
            where = "FROM groups WHERE ivtff_group_raw=? AND edition=?"
            args = (word, edition)
            count, pages = con.execute("SELECT COUNT(*),COUNT(DISTINCT page) " + where, args).fetchone()
            total, selectors = con.execute("SELECT COUNT(*),COUNT(DISTINCT page) FROM groups WHERE edition=?", (edition,)).fetchone()
            pcounts = dict(con.execute("SELECT CASE WHEN source_group_count=1 THEN 'single' WHEN source_group_index=1 THEN 'start' WHEN source_group_index=source_group_count THEN 'end' ELSE 'middle' END,COUNT(*) " + where + " GROUP BY 1", args).fetchall())
            positions = {k: pcounts.get(k, 0) for k in ["start", "middle", "end", "single"]}
            strata = {}
            for field in ["section", "currier", "hand", "kind"]:
                strata[field] = [{"value": v, "count": n} for v, n in con.execute("SELECT " + field + ",COUNT(*) " + where + " GROUP BY " + field + " ORDER BY " + field, args)]
            actual = dict(count=count, selectors_with_form=pages, total_groups=total, selectors_total=selectors, positions=positions, strata_counts=strata)
            check(packet["exact_whole_priors"][word].get(edition) == actual, "EXACT_WHOLE_PRIOR", word + "|" + edition)
            prior_cells += 1
    con.close()
    counts = dict(groups=len(rows), loci=len({r["locus"] for r in rows}), reader_locus_cells=len(bycell), groups_by_reader=dict(collections.Counter(r["edition"] for r in rows)), groups_by_reader_unit={"|".join(k): v for k, v in unit_ord.items()}, eligible_groups=sum(r["parse_status"] == "PURE_FUNCTION_REPLAY" for r in replay_groups), unresolved_groups=sum(r["parse_status"] != "PURE_FUNCTION_REPLAY" for r in replay_groups), chunks=len(chunks), eligible_chunks=sum(c["status"] == "REPLAY" for c in chunks), uncertain_small_space_seams=sum(r["right_separator"] == "UNCERTAIN_SMALL_SPACE" for r in rows), eligible_whole_types=len(whole_types), prior_reader_type_cells=prior_cells, merges=len(merges))
    expected_summary = dict(eligible_groups=counts["eligible_groups"], marked_or_nonlowercase_unresolved_groups=counts["unresolved_groups"], hard_chunks=counts["chunks"], eligible_chunks=counts["eligible_chunks"], eligible_exact_whole_types=counts["eligible_whole_types"], merges=counts["merges"], new_rules_or_local_frames=False)
    check(packet["formal_summary"] == expected_summary, "FORMAL_SUMMARY", "Summary differs from independent replay")
    check(receipt["source_group_count"] == len(rows) and receipt["physical_locus_count"] == counts["loci"] and receipt["reader_locus_cells"] == counts["reader_locus_cells"], "ROOT_RECEIPT_COUNTS", "Receipt count differs from independent source")
    check([(x["unit_id"], x["edition"]) for x in packet["coverage"]] == [(unit, edition) for unit in ["FV_F83R_DISCOVERY", "FV_F83V_DISCOVERY"] for edition in READERS], "COVERAGE_CELL_SET", "Exactly six ordered unit/reader coverage cells required")
    check(packet["physical_locus_count"] == counts["loci"], "PACKET_LOCUS_COUNT", "Locus count mismatch")
    check(packet["native_RF_paragraph_boundaries_imputed"] is False, "RF_IMPUTATION_CLAIM", "Unexpected imputation")
    check(all((r["paragraph_start"], r["paragraph_end"]) == ("0", "0") for r in rows if r["edition"] == "RF1b"), "RF_NATIVE_ABSENCE_ENCODING", "Expected observed canonical0/0 absence encoding")
    prior_inputs = cache_receipt["inputs"]
    check(prior_inputs["selector_count"] == 179 and len(prior_inputs["selectors"]) == 179 and len(set(prior_inputs["selectors"])) == 179, "PRIOR_SELECTOR_RECEIPT", "Fixed179 selector receipt inconsistent")
    check(prior_inputs["source"] == SOURCE and prior_inputs["source_sha256"] == sha(ROOT / SOURCE), "PRIOR_SOURCE_RECEIPT", "Cached source provenance mismatch")
    check(prior_inputs["allowlist_sha256"] == contract["frequency_prior"]["fixed179_allowlist_sha256_supplied"], "PRIOR_ALLOWLIST_CONTRACT", "Allowlist pin differs")
    check(not any(x.startswith("f84") or x == "f116v" for x in prior_inputs["selectors"]), "PRIOR_EXCLUDED_SELECTORS", "Forbidden selector in cached receipt")
    for cov in packet["coverage"]:
        rs = [r for r in rows if r["edition"] == cov["edition"] and ("FV_F83R_DISCOVERY" if r["page"] == "f83r" else "FV_F83V_DISCOVERY") == cov["unit_id"]]
        loci = [l for l in LOCI if any(r["locus"] == l for r in rs)]
        starts = [l for l in loci if any(r["locus"] == l and r["paragraph_start"] == "1" for r in rs)]
        ends = [l for l in loci if any(r["locus"] == l and r["paragraph_end"] == "1" for r in rs)]
        check(cov["loci"] == loci and cov["literal_group_count"] == len(rs) and cov["native_start_loci"] == starts and cov["native_end_loci"] == ends and cov["native_paragraph_flags_available"] == (cov["edition"] != "RF1b"), "COVERAGE_NATIVE_FIELDS", cov["unit_id"] + "|" + cov["edition"])
    out = dict(schema="FV-independent-discovery-source-audit-v1", status="PASS_LITERAL_CONSERVATION_WITH_CONTRACT_PREMISE_CORRECTION" if not errors else "FAIL_SOURCE_AUDIT", receipt_pins=pin_results, contract_sha256=sha(BASE / "FV_SOURCE_CONTRACT.json"), validator_sha256=sha(Path(__file__)), guarded_query=dict(command=argv, output_sha256=hashlib.sha256(query.stdout).hexdigest(), guard_stats=guard), counts=counts, source_cells=cells, representation_errors=errors, representation_error_count=len(errors), contract_premise_discrepancies=[dict(kind="RF_ABSENCE_ENCODING", frozen_statement="RF source-empty paragraph flags must remain empty", observed="Canonical RF paragraph_start/paragraph_end are literal strings0/0; packet preserves them and explicitly reports native flags unavailable.", consequence="Contract literal-empty premise is false. No source or packet edit; absence of native paragraph boundary evidence remains true. A strict empty-field subcriterion cannot PASS; literal source conservation does PASS.")], column_accounting=dict(literal_field_count=len(COLS), fields=COLS, frozen_prose_field_count=18, mismatch=False), scope=dict(discovery_loci=LOCI, readers=READERS, additional_bodies_opened=False, author_drafts_opened=False, new_pixels_opened=False, physical_leaf_training=83, extra_leaves=[75,104], extra_coverage="Selected exposed paragraphs, not whole leaves", independent_confirmation=0), conclusion="All source comparisons concern input representation, not meaning. Source/model priors faithfully conserved if representation_error_count=0; no lexical validation, new decoder, reserved evidence or independent manuscript confirmation.")
    (BASE / "FV_DISCOVERY_SOURCE_AUDIT.json").write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({k: out[k] for k in ["status", "counts", "representation_errors"]}, indent=2))
    return not errors


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
