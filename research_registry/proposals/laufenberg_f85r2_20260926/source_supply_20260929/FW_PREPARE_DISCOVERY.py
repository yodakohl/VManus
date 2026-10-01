#!/usr/bin/env python3
"""Prepare only FW's fixed discovery loci; preserve frozen formal functions.

No application selector, target meaning, source cleanup, model fitting or cache
rebuilding is performed. Only a guarded projection is decoded into source rows.
"""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import io
import json
import sqlite3
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[4]
BASE = Path(__file__).resolve().parent
SOURCE = "experiments/semantic_assumptions/results/source_separator_transcription.tsv"
CACHE = "experiments/semantic_assumptions/cache/word_profiles.sqlite"
ALLOWLIST = "experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv"
RUNNER = "experiments/yolo/gdt1051_frozen_grammar_local_application/src/run.py"
MERGES = "experiments/yolo/gdt605_multisymbol_unit_alphabet/artifacts/gdt605_bpe_merges.tsv"
LOCUS_UNITS = {
    **{f"f83r.{n}": "FW_F83R_PREVIOUS" for n in range(1, 9)},
    **{f"f83r.{n}": "FW_F83R_CURRENT" for n in range(9, 18)},
    **{f"f83v.{n}": "FW_F83V_PREVIOUS" for n in range(11, 21)},
    **{f"f83v.{n}": "FW_F83V_CURRENT" for n in range(21, 34)},
}
EDITIONS = ("ZL3b", "IT2a", "RF1b")
COLUMNS = (
    "source_group_id", "edition", "locus", "page", "section", "currier",
    "hand", "code", "kind", "grammar_scope", "source_row_index",
    "source_group_index", "source_group_count", "paragraph_start",
    "paragraph_end", "left_separator", "right_separator", "ivtff_group_raw",
)
PINS = {
    SOURCE: "4b649c8290d5afc7a5fbcc8e98db2bc123a1ceb5f3858d3befa781ce96b680f0",
    RUNNER: "8fd6000574b289dd539e9a7b04c45e15a5a767871dae770fd454af91c7146ba2",
    "run_gdt012_core_semantic_atlas.py": "7db6d7eff0937e9fa67a77356a61e00a0e28a6cd73b2c62146844adea8b8fc1c",
    "run_gdt062_right_family_register_renderer.py": "9c9e7a35278d59ace7dd88f3c1e0ca6112ec48cef29fdd86c4e5546c6ec9a665",
    "experiments/yolo/gdt605_multisymbol_unit_alphabet/src/separator_crossing.py": "921c6617615980ed41bf70c8cdf574aa2a15621832e7842dd9dd3621461bf8e8",
    MERGES: "4625c9389ead390907e4ac74e65bc158236f02b439c69cf3b09157f0cd6ca539",
    "tools/word_profiles.py": "1e9cb2017525e8ee3fd07b6a088e73b28b1e4fe4e7c9d17b83b892b94d0943c6",
    ALLOWLIST: "f0def5a04bd91443cf4770c78f1b67e62cac2060627d8de38faba27899188483",
    CACHE: "7a3d21719f43bba7388dc90efd559cedcde5325d7d5a8916ac2bd0e9716e6664",
}


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def prior(conn, form, edition, totals):
    # Only aggregate counts/metadata: no outside occurrence, neighbor or body.
    row = conn.execute("""SELECT COUNT(*) AS count,
        COUNT(DISTINCT page) AS selectors_with_form,
        SUM(CASE WHEN source_group_count>1 AND source_group_index=1 THEN 1 ELSE 0 END) AS start,
        SUM(CASE WHEN source_group_count>1 AND source_group_index>1 AND source_group_index<source_group_count THEN 1 ELSE 0 END) AS middle,
        SUM(CASE WHEN source_group_count>1 AND source_group_index=source_group_count THEN 1 ELSE 0 END) AS end,
        SUM(CASE WHEN source_group_count=1 THEN 1 ELSE 0 END) AS single
        FROM groups WHERE edition=? AND ivtff_group_raw=?""", (edition, form)).fetchone()
    count = row["count"]
    strata = {}
    for field in ("section", "currier", "hand", "kind"):
        strata[field] = [dict(r) for r in conn.execute(
            f'SELECT "{field}" AS value,COUNT(*) AS count FROM groups '
            f'WHERE edition=? AND ivtff_group_raw=? GROUP BY "{field}" ORDER BY "{field}"',
            (edition, form))]
    return {
        "count": count, "selectors_with_form": row["selectors_with_form"],
        "total_groups": totals[edition][0], "selectors_total": totals[edition][1],
        "positions": {k: row[k] or 0 for k in ("start", "middle", "end", "single")},
        "strata_counts": strata,
    }


def main():
    assert len(LOCUS_UNITS) == 40 and {x.split(".")[0] for x in LOCUS_UNITS} == {"f83r", "f83v"}
    for name, expected in PINS.items():
        assert sha(ROOT / name) == expected, f"Frozen input changed: {name}"
    command = ["./vmanus-exp", "query-tsv", SOURCE, "--selector", "locus"]
    for locus in LOCUS_UNITS:
        command += ["--allow", locus]
    command += ["--columns", ",".join(COLUMNS), "--forbid-prefix", "f84", "--forbid-prefix", "f84r"]
    got = subprocess.run(command, cwd=ROOT, capture_output=True, check=True)
    guard_reports = [line[12:] for line in got.stderr.decode().splitlines() if line.startswith("GUARD_STATS ")]
    assert len(guard_reports) == 1
    guard = json.loads(guard_reports[0])
    reader = csv.DictReader(io.StringIO(got.stdout.decode("utf-8")), delimiter="\t")
    assert reader.fieldnames == list(COLUMNS)
    rows = list(reader)  # Guarded discovery projection only.
    assert len(rows) == guard["selected"]
    assert len({r["source_group_id"] for r in rows}) == len(rows)
    assert all(set(r) == set(COLUMNS) and None not in r.values() for r in rows)
    assert all(r["locus"] in LOCUS_UNITS and r["edition"] in EDITIONS for r in rows)
    byline = defaultdict(list)
    for row in rows:
        assert row["page"] in {"f83r", "f83v"}
        byline[row["edition"], row["locus"]].append(row)
    assert set(byline) == {(ed, locus) for ed in EDITIONS for locus in LOCUS_UNITS}
    for line in byline.values():
        n = len(line)
        assert [int(r["source_group_index"]) for r in line] == list(range(1, n + 1))
        assert all(int(r["source_group_count"]) == n for r in line)
        for field in ("paragraph_start", "paragraph_end"):
            assert len({r[field] for r in line}) == 1

    # Imported main is guarded. Do not call group_rows()/main() or any legacy
    # source inventory loader. Only unchanged parse_group/make_chunks functions.
    spec = importlib.util.spec_from_file_location("fw_frozen_gdt1051", ROOT / RUNNER)
    formal = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(formal)
    merges = formal.load_merges()
    assert len(merges) == 64
    parsed = [formal.parse_group(LOCUS_UNITS[r["locus"]], r) for r in rows]
    chunks = formal.make_chunks(parsed, merges)
    memberships = {}
    for ordinal, chunk in enumerate(chunks, 1):
        chunk["chunk_id"] = f"FW_DISCOVERY_CHUNK_{ordinal:04d}"
        for index in chunk["group_indices"]:
            key = (chunk["edition"], chunk["locus"], index)
            assert key not in memberships
            memberships[key] = chunk["chunk_id"]
    assert len(memberships) == len(rows)
    unit_indices = Counter()
    groups = []
    for row, result in zip(rows, parsed):
        key = (row["edition"], LOCUS_UNITS[row["locus"]])
        unit_indices[key] += 1
        groups.append({**row, "unit_id": key[1],
                       "unit_reader_order": unit_indices[key],
                       "formal_gdt012_062": result,
                       "formal_gdt605_chunk_id": memberships[row["edition"], row["locus"], int(row["source_group_index"])],
                       "native_paragraph_flags_available": row["edition"] != "RF1b"})

    conn = sqlite3.connect((ROOT / CACHE).resolve().as_uri() + "?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    receipt = json.loads(conn.execute("SELECT value FROM metadata WHERE key='receipt'").fetchone()[0])
    assert receipt["inputs"]["source_sha256"] == PINS[SOURCE]
    assert receipt["inputs"]["allowlist_sha256"] == PINS[ALLOWLIST]
    assert receipt["inputs"]["code_sha256"] == PINS["tools/word_profiles.py"]
    assert receipt["inputs"]["selector_count"] == 179
    assert receipt["inputs"]["matching"] == "exact_raw_group"
    totals = {ed: tuple(conn.execute("SELECT COUNT(*),COUNT(DISTINCT page) FROM groups WHERE edition=?", (ed,)).fetchone()) for ed in EDITIONS}
    assert sum(n[0] for n in totals.values()) == receipt["guard_stats"]["selected"]
    forms = sorted({g["raw"] for g in parsed if g["parse_status"] == "PURE_FUNCTION_REPLAY"})
    priors = {form: {ed: prior(conn, form, ed, totals) for ed in EDITIONS} for form in forms}
    conn.close()
    for per_reader in priors.values():
        for value in per_reader.values():
            assert sum(value["positions"].values()) == value["count"]
    coverage = []
    for unit in dict.fromkeys(LOCUS_UNITS.values()):
        loci = [loc for loc, owner in LOCUS_UNITS.items() if owner == unit]
        for edition in EDITIONS:
            line_rows = [byline[edition, loc] for loc in loci]
            coverage.append({"unit_id": unit, "edition": edition, "loci": loci,
                             "literal_group_count": sum(map(len, line_rows)),
                             "native_paragraph_flags_available": edition != "RF1b",
                             "native_start_loci": [loc for loc in loci if byline[edition, loc][0]["paragraph_start"] == "1"],
                             "native_end_loci": [loc for loc in loci if byline[edition, loc][0]["paragraph_end"] == "1"],
                             "paragraph_role": "PREVIOUS" if unit.endswith("PREVIOUS") else "CURRENT",
                             "scope_role": "JOINT_DISCOVERY_SAME_PHYSICAL_LEAF"})
    decision = BASE / "FW_DECISION.md"
    packet = {
        "schema": "FW-discovery-native-v1", "status": "SOURCE_AND_FROZEN_FORMAL_PREPARATION_ONLY",
        "decision_path": str(decision.relative_to(ROOT)), "decision_sha256": sha(decision),
        "partition": "discovery only; f83r and f83v are the same physical leaf; no independent confirmation",
        "allowed_loci": list(LOCUS_UNITS), "editions": list(EDITIONS),
        "input_hashes": PINS,
        "preparer_path": str(Path(__file__).relative_to(ROOT)), "preparer_sha256": sha(__file__),
        "query_receipt": {"command": command, "selector": "locus", "allow_values": list(LOCUS_UNITS),
                          "output_columns": list(COLUMNS), "guard_stats": guard,
                          "projection_sha256": hashlib.sha256(got.stdout).hexdigest()},
        "coverage": coverage, "raw_group_count": len(rows), "physical_locus_count": len(LOCUS_UNITS),
        "formal_summary": {"eligible_groups": sum(g["parse_status"] == "PURE_FUNCTION_REPLAY" for g in parsed),
                           "marked_or_nonlowercase_unresolved_groups": sum(g["parse_status"] != "PURE_FUNCTION_REPLAY" for g in parsed),
                           "hard_chunks": len(chunks), "eligible_chunks": sum(c["units"] is not None for c in chunks),
                           "eligible_exact_whole_types": len(forms), "merges": 64,
                           "new_rules_or_local_frames": False},
        "groups": groups, "chunks": chunks, "exact_whole_priors": priors,
        "word_prior_receipt": receipt,
        "word_prior_scope": "Existing verified179-selector cache, exact aggregate frequency/selector dispersion/source-locus position/metadata counts per reader; no outside bodies or neighbors",
        "raw_projection_path": str((BASE / "FW_DISCOVERY_GROUPS.tsv").relative_to(ROOT)),
        "raw_projection_sha256": hashlib.sha256(got.stdout).hexdigest(),
        "application_bodies_opened": False, "application_pixels_opened": False,
        "confirmed_words": 0, "semantic_validation": False,
        "native_RF_paragraph_boundaries_imputed": False,
        "sealed_data": {"f84": "FORBIDDEN_AND_ABSENT", "f84r": "FORBIDDEN_AND_ABSENT"},
    }
    # Recheck input pins before publishing owned outputs.
    for name, expected in PINS.items():
        assert sha(ROOT / name) == expected
    (BASE / "FW_DISCOVERY_GROUPS.tsv").write_bytes(got.stdout)
    out = BASE / "FW_DISCOVERY_PACKET.json"
    out.write_text(json.dumps(packet, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"packet_sha256": sha(out), "raw_projection_sha256": packet["raw_projection_sha256"],
                      "raw_groups": len(rows), "coverage": coverage, "formal_summary": packet["formal_summary"]}, indent=2))


if __name__ == "__main__":
    main()
