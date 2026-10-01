#!/usr/bin/env python3
"""GDT1125 independent literal source audit; requires explicit hash-bound GO.

This validator neither parses candidate meanings nor opens author/critic models.
It hashes frozen model files, then queries only the fixed application loci.
No occurrence-prior query, decoder, source repair or model fitting is performed.
"""
from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import importlib.util
import io
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = Path(__file__).resolve().parents[1]
READERS = ["ZL3b", "IT2a", "RF1b"]
LOCI = [f"f75v.{n}" for n in range(38, 50)] + [f"f104v.{n}" for n in range(19, 27)]
FIELDS = "source_group_id,edition,locus,page,section,currier,hand,code,kind,grammar_scope,source_row_index,source_group_index,source_group_count,paragraph_start,paragraph_end,left_separator,right_separator,ivtff_group_raw".split(",")
UNITS = {
    "FW_F75V_PREVIOUS": [f"f75v.{n}" for n in range(38, 43)],
    "FW_F75V_CURRENT": [f"f75v.{n}" for n in range(43, 50)],
    "FW_F104V_PREVIOUS": [f"f104v.{n}" for n in range(19, 22)],
    "FW_F104V_CURRENT": [f"f104v.{n}" for n in range(22, 27)],
}
CURRENT_UNITS = ["FW_F75V_CURRENT", "FW_F104V_CURRENT"]
SOURCE = "experiments/semantic_assumptions/results/source_separator_transcription.tsv"
FORMAL = "experiments/yolo/gdt1051_frozen_grammar_local_application/src/run.py"
PINS = {
    SOURCE: "4b649c8290d5afc7a5fbcc8e98db2bc123a1ceb5f3858d3befa781ce96b680f0",
    FORMAL: "8fd6000574b289dd539e9a7b04c45e15a5a767871dae770fd454af91c7146ba2",
    "run_gdt012_core_semantic_atlas.py": "7db6d7eff0937e9fa67a77356a61e00a0e28a6cd73b2c62146844adea8b8fc1c",
    "run_gdt062_right_family_register_renderer.py": "9c9e7a35278d59ace7dd88f3c1e0ca6112ec48cef29fdd86c4e5546c6ec9a665",
    "experiments/yolo/gdt605_multisymbol_unit_alphabet/src/separator_crossing.py": "921c6617615980ed41bf70c8cdf574aa2a15621832e7842dd9dd3621461bf8e8",
    "experiments/yolo/gdt605_multisymbol_unit_alphabet/artifacts/gdt605_bpe_merges.tsv": "4625c9389ead390907e4ac74e65bc158236f02b439c69cf3b09157f0cd6ca539",
    "experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv": "f0def5a04bd91443cf4770c78f1b67e62cac2060627d8de38faba27899188483",
}
PREPARER = str((BASE / "src/prepare_source.py").relative_to(ROOT))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def repository_path(name):
    p = Path(name)
    if p.is_absolute() or ".." in p.parts or not (ROOT / p).resolve().is_relative_to(ROOT):
        raise ValueError("Nonrepository input path")
    return ROOT / p


def unit_for(locus):
    matches = [name for name, loci in UNITS.items() if locus in loci]
    if len(matches) != 1:
        raise ValueError("Locus outside exact four-unit partition")
    return matches[0]


def load_exact(path, expected_sha):
    if not re.fullmatch(r"[0-9a-f]{64}", expected_sha):
        raise ValueError("Expected exact lowercase SHA256")
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != expected_sha:
        raise ValueError("Frozen metadata hash mismatch: " + str(path.relative_to(ROOT)))
    return json.loads(data)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec-sha256", required=True)
    parser.add_argument("--open-receipt-sha256", required=True)
    args = parser.parse_args()
    # No source/packet body is materialized before all preopening gates pass.
    spec = load_exact(BASE / "src/SPEC.json", args.spec_sha256)
    opening = load_exact(BASE / "artifacts/OPEN_RECEIPT.json", args.open_receipt_sha256)
    if spec.get("status") != "PREOPEN_FROZEN":
        raise ValueError("SPEC is not PREOPEN_FROZEN")
    if opening.get("status") != "ROOT_EXPLICIT_APPLICATION_GO" or opening.get("spec_sha256") != args.spec_sha256:
        raise ValueError("No exact root application GO bound to this SPEC")
    inputs = spec.get("input_hashes")
    models = spec.get("model_files")
    if not isinstance(inputs, dict) or not isinstance(models, dict) or set(models) != {"FV", "FW"}:
        raise ValueError("Missing frozen input/model pin inventory")
    model_paths = []
    for owner in ["FV", "FW"]:
        paths = models[owner]
        if not isinstance(paths, list) or not paths or not all(isinstance(p, str) and p in inputs for p in paths):
            raise ValueError("Every candidate model path must have a SPEC input hash")
        model_paths.extend(paths)
    if PREPARER not in inputs:
        raise ValueError("SPEC lacks exact source-preparer pin")
    for path, expected in PINS.items():
        if inputs.get(path) != expected:
            raise ValueError("SPEC lacks exact unchanged source/formal pin: " + path)
    input_checks = []
    for name, expected in inputs.items():
        if not isinstance(expected, str) or not re.fullmatch(r"[0-9a-f]{64}", expected):
            raise ValueError("Malformed frozen input hash")
        actual = sha(repository_path(name))
        input_checks.append(dict(path=name, expected_sha256=expected, actual_sha256=actual, match=actual == expected))
        if actual != expected:
            raise ValueError("Frozen input hash mismatch: " + name)
    for name, expected in PINS.items():
        if sha(repository_path(name)) != expected:
            raise ValueError("Unchanged source/formal pin mismatch: " + name)
    if any(l.startswith("f84") or l.startswith("f116v") for l in LOCI) or len(LOCI) != 20 or len(FIELDS) != 18:
        raise ValueError("Invalid fixed source scope")
    argv = ["./vmanus-exp", "query-tsv", SOURCE, "--selector", "locus"]
    for locus in LOCI:
        argv += ["--allow", locus]
    argv += ["--columns", ",".join(FIELDS), "--forbid-prefix", "f84", "--forbid-prefix", "f84r", "--forbid-prefix", "f116v"]
    query = subprocess.run(argv, cwd=ROOT, capture_output=True, check=True)
    reader = csv.DictReader(io.StringIO(query.stdout.decode("utf-8")), delimiter="\t")
    if reader.fieldnames != FIELDS:
        raise ValueError("Canonical projection header mismatch")
    rows = list(reader)
    # These totals are computed before parsing a prepared packet or its counts.
    direct_counts = dict(groups=len(rows), physical_loci=len({r["locus"] for r in rows}), reader_locus_cells=len({(r["edition"], r["locus"]) for r in rows}))
    guard = json.loads(query.stderr.decode("utf-8").strip().split("GUARD_STATS ", 1)[1])
    packet_path = BASE / "artifacts/APPLICATION_PACKET.json"
    groups_path = BASE / "artifacts/APPLICATION_GROUPS.tsv"
    packet_sha = sha(packet_path)
    if opening.get("source_packet_sha256") is not None and opening["source_packet_sha256"] != packet_sha:
        raise ValueError("Opening receipt source-packet pin mismatch")
    packet = json.loads(packet_path.read_bytes())
    errors = []

    def check(condition, kind, detail):
        if not condition:
            errors.append(dict(kind=kind, detail=detail))

    check(guard["selected"] == len(rows), "GUARD_SELECTED_COUNT", "Guard versus direct rows")
    check(packet.get("allowed_loci") == LOCI, "PACKET_LOCUS_SCOPE", "Exact20 locus allows required")
    check(packet.get("editions") == READERS, "PACKET_READERS", "All three alternate readers required")
    check(packet.get("spec_sha256") == args.spec_sha256, "PACKET_SPEC_PIN", "Prepared source must belong to exact frozen SPEC")
    check(packet.get("preparer_path") == PREPARER and packet.get("preparer_sha256") == inputs[PREPARER], "PACKET_PREPARER_PIN", "Exact frozen source-preparer provenance")
    for name, expected in packet.get("input_hashes", {}).items():
        check(sha(repository_path(name)) == expected, "PACKET_INPUT_PIN", name)
    for name, expected in PINS.items():
        check(packet.get("input_hashes", {}).get(name) == expected, "PACKET_FORMAL_PIN", name)
    check(packet.get("raw_group_count") == direct_counts["groups"], "PACKET_GROUP_COUNT", "Prepared count versus independently determined source")
    check(packet.get("physical_locus_count") == direct_counts["physical_loci"], "PACKET_LOCUS_COUNT", "Prepared versus direct loci")
    groups = packet.get("groups", [])
    projection_receipt = packet.get("query_receipt", {})
    check(projection_receipt.get("selector") == "locus" and projection_receipt.get("allow_values") == LOCI and projection_receipt.get("output_columns") == FIELDS, "PACKET_QUERY_SCOPE", "Exact20 selector allows/18 canonical fields")
    check(projection_receipt.get("projection_sha256") == hashlib.sha256(query.stdout).hexdigest(), "PACKET_QUERY_HASH", "Independent canonical projection hash")
    check(projection_receipt.get("guard_stats", {}).get("selected") == len(rows), "PACKET_GUARD_SELECTED", "Prepared guard count versus direct canonical rows")
    check([{k: g.get(k) for k in FIELDS} for g in groups] == rows, "ALL_NATIVE_FIELD_ORDER", "Every18 canonical fields/native order must match JSON")
    native_bytes = groups_path.read_bytes()
    check(native_bytes == query.stdout, "CANONICAL_PROJECTION_BYTES", "Native TSV must equal independent guarded output bytes")
    native_reader = csv.DictReader(io.StringIO(native_bytes.decode("utf-8")), delimiter="\t")
    check(native_reader.fieldnames == FIELDS and list(native_reader) == rows, "ALL_NATIVE_TSV_FIELDS", "Exact18 fields/order must match TSV")
    check(len({r["source_group_id"] for r in rows}) == len(rows), "NATIVE_ID_UNIQUENESS", "Duplicate source IDs")
    bycell = collections.defaultdict(list)
    for row in rows:
        check(row["locus"] in LOCI and row["edition"] in READERS and not row["page"].startswith(("f84", "f116v")), "CANONICAL_SCOPE", row["source_group_id"])
        bycell[row["edition"], row["locus"]].append(row)
    cells = []
    for edition in READERS:
        for locus in LOCI:
            rs = bycell[edition, locus]
            cells.append(dict(edition=edition, locus=locus, groups=len(rs), source_row_indexes=sorted({r["source_row_index"] for r in rs}), native_flags=sorted({(r["paragraph_start"], r["paragraph_end"]) for r in rs})))
            check(bool(rs), "NATIVE_CELL_ABSENT", edition + "|" + locus)
            check([int(r["source_group_index"]) for r in rs] == list(range(1, len(rs) + 1)), "NATIVE_INDEX_ORDER", edition + "|" + locus)
            check(all(int(r["source_group_count"]) == len(rs) for r in rs), "NATIVE_GROUP_COUNT", edition + "|" + locus)
            check(len({r["source_row_index"] for r in rs}) == 1, "NATIVE_ROW_IDENTITY", edition + "|" + locus)
            if rs:
                check(rs[0]["left_separator"] == "LINE_START" and rs[-1]["right_separator"] == "LINE_END", "LINE_EDGES", edition + "|" + locus)
                check(all(a["right_separator"] == b["left_separator"] for a, b in zip(rs, rs[1:])), "RAW_SEAMS", edition + "|" + locus)
    legacy_spec = importlib.util.spec_from_file_location("gdt1125_source_formal1051", ROOT / FORMAL)
    legacy = importlib.util.module_from_spec(legacy_spec)
    legacy_spec.loader.exec_module(legacy)
    merges = legacy.load_merges()
    replay = []
    unit_ord = collections.Counter()
    for row, saved in zip(rows, groups):
        unit = unit_for(row["locus"])
        unit_ord[unit, row["edition"]] += 1
        formal = legacy.parse_group(unit, row)
        replay.append(formal)
        check(saved.get("unit_id") == unit and saved.get("unit_reader_order") == unit_ord[unit, row["edition"]], "UNIT_READER_ORDER", row["source_group_id"])
        check(saved.get("formal_gdt012_062") == formal, "PURE_FORMAL_GROUP_REPLAY", row["source_group_id"])
        check(saved.get("native_paragraph_flags_available") == (row["edition"] != "RF1b"), "RF_NATIVE_AVAILABILITY", row["source_group_id"])
        current = unit in CURRENT_UNITS
        check(saved.get("paragraph_role") == ("CURRENT" if current else "PREVIOUS"), "GROUP_PARAGRAPH_ROLE", row["source_group_id"])
        check(saved.get("candidate_scoring_scope") == (["FV", "FW"] if current else ["FW"]) and saved.get("fv_scoring_eligible") is current, "GROUP_CANDIDATE_SCOPE", row["source_group_id"])
    check(len(replay) == len(rows), "REPLAY_SOURCE_COVERAGE", "Each canonical group requires a formal record")
    chunks = legacy.make_chunks(replay, merges)
    saved_chunks = packet.get("chunks", [])
    check(len(chunks) == len(saved_chunks), "HARD_CHUNK_COUNT", "Direct replay versus packet")
    memberships = {}
    for actual, saved in zip(chunks, saved_chunks):
        cid = saved.get("chunk_id")
        check(isinstance(cid, str) and bool(cid), "CHUNK_ID_PRESENT", "Every chunk needs a reference ID")
        check({k: v for k, v in saved.items() if k != "chunk_id"} == actual, "PURE_CHUNK_REPLAY", cid)
        for index in actual["group_indices"]:
            key = (actual["edition"], actual["locus"], index)
            check(key not in memberships, "DUPLICATE_CHUNK_GROUP", str(key))
            memberships[key] = cid
    check(len({c.get("chunk_id") for c in saved_chunks}) == len(saved_chunks), "CHUNK_ID_UNIQUENESS", "Duplicate chunk IDs")
    check(len(memberships) == len(rows), "CHUNK_GROUP_CONSERVATION", "Each original group retained exactly once")
    for row, saved in zip(rows, groups):
        key = (row["edition"], row["locus"], int(row["source_group_index"]))
        check(saved.get("formal_gdt605_chunk_id") == memberships.get(key), "NATIVE_CHUNK_REFERENCE", row["source_group_id"])
    coverage = packet.get("coverage", [])
    check([(c.get("unit_id"), c.get("edition")) for c in coverage] == [(u, e) for u in UNITS for e in READERS], "FOUR_UNIT_COVERAGE_SET", "Exactly four FW units/all three readers")
    for cov in coverage:
        unit, edition = cov.get("unit_id"), cov.get("edition")
        if unit not in UNITS or edition not in READERS:
            continue
        rs = [r for r in rows if r["edition"] == edition and r["locus"] in UNITS[unit]]
        starts = [l for l in UNITS[unit] if any(r["locus"] == l and r["paragraph_start"] == "1" for r in rs)]
        ends = [l for l in UNITS[unit] if any(r["locus"] == l and r["paragraph_end"] == "1" for r in rs)]
        expected_starts = [UNITS[unit][0]] if edition != "RF1b" else []
        expected_ends = [UNITS[unit][-1]] if edition != "RF1b" else []
        check(starts == expected_starts and ends == expected_ends, "NATIVE_FOUR_BOUNDARIES", unit + "|" + edition)
        check(cov.get("loci") == UNITS[unit] and cov.get("literal_group_count") == len(rs) and cov.get("native_start_loci") == starts and cov.get("native_end_loci") == ends and cov.get("native_paragraph_flags_available") == (edition != "RF1b"), "COVERAGE_NATIVE_FIELDS", unit + "|" + edition)
        check(cov.get("paragraph_role") == ("PREVIOUS" if unit.endswith("PREVIOUS") else "CURRENT"), "PREVIOUS_CURRENT_ROLE", unit + "|" + edition)
        check(cov.get("candidate_scoring_scope") == (["FV", "FW"] if unit in CURRENT_UNITS else ["FW"]), "COVERAGE_CANDIDATE_SCOPE", unit + "|" + edition)
    check(all((r["paragraph_start"], r["paragraph_end"]) == ("0", "0") for r in rows if r["edition"] == "RF1b"), "RF_ZERO_FLAGS", "Absence encoded literal0/0; no native RF boundaries")
    check(packet.get("native_RF_paragraph_boundaries_imputed") is False, "RF_NO_IMPUTATION", "Native RF boundaries must remain unavailable")
    counts = dict(direct_counts, groups_by_reader=dict(collections.Counter(r["edition"] for r in rows)), groups_by_unit_reader={"|".join(k): v for k, v in unit_ord.items()}, eligible_groups=sum(g["parse_status"] == "PURE_FUNCTION_REPLAY" for g in replay), unresolved_groups=sum(g["parse_status"] != "PURE_FUNCTION_REPLAY" for g in replay), hard_chunks=len(chunks), eligible_chunks=sum(c["status"] == "REPLAY" for c in chunks), uncertain_small_space_seams=sum(r["right_separator"] == "UNCERTAIN_SMALL_SPACE" for r in rows), merges=len(merges))
    summary = packet.get("formal_summary", {})
    expected_summary = dict(eligible_groups=counts["eligible_groups"], marked_or_nonlowercase_unresolved_groups=counts["unresolved_groups"], hard_chunks=counts["hard_chunks"], eligible_chunks=counts["eligible_chunks"], eligible_exact_whole_types=len({r["ivtff_group_raw"] for r in rows if re.fullmatch(r"[a-z]+", r["ivtff_group_raw"])}), merges=64, new_rules_or_local_frames=False)
    check(summary == expected_summary, "FORMAL_SUMMARY", "Independent pure replay aggregate summary")
    fv_ids = [r["source_group_id"] for r in rows if unit_for(r["locus"]) in CURRENT_UNITS]
    result = dict(schema="gdt1125-independent-source-validation-v1", status="PASS" if not errors else "FAIL_SOURCE_REPRESENTATION", validation_kind="LITERAL_SOURCE_CONSERVATION_AND_UNCHANGED_FORMAL_REPLAY", spec_sha256=args.spec_sha256, open_receipt_sha256=args.open_receipt_sha256, source_packet_sha256=packet_sha, source_packet_pin_present="source_packet_sha256" in opening, source_tsv_sha256=sha(groups_path), validator_sha256=sha(Path(__file__)), frozen_input_checks=input_checks, model_pin_policy="Hash-only; candidate/critic model contents are not parsed", query=dict(command=argv, output_sha256=hashlib.sha256(query.stdout).hexdigest(), guard_stats=guard, source_counts_computed_before_packet_parsing=True), source_cells=cells, counts=counts, errors=errors, error_count=len(errors), FV_scope=dict(unit_ids=CURRENT_UNITS, loci=[l for u in CURRENT_UNITS for l in UNITS[u]], source_group_ids=fv_ids, groups=len(fv_ids), previous_paragraphs_not_donated=True), FW_scope=dict(unit_ids=list(UNITS), loci=LOCI, source_group_ids=[r["source_group_id"] for r in rows], paragraph_roles={u: "PREVIOUS" if u.endswith("PREVIOUS") else "CURRENT" for u in UNITS}), RF_policy="Literal0/0 preserved; native boundaries unavailable; external matching-locus windows only", exposure="Previously project-exposed selected complete paragraph windows on leaves75/104; not whole-leaf readings or independent confirmation", independent_confirmation=0, confirmed_words=0, semantic_validation=False, additional_prior_queries=0, new_pixels=False, sealed_data={"f84": "FORBIDDEN_AND_ABSENT", "f84r": "FORBIDDEN_AND_ABSENT", "f116v": "NOT_ADMITTED_AND_ABSENT"}, decision="Faithful source PASS permits frozen-model exposed-data application; it selects no meaning. Representation mismatch blocks affected input, not a lexical hypothesis.")
    (BASE / "artifacts/SOURCE_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(dict(status=result["status"], counts=counts, error_count=len(errors)), indent=2))
    return not errors


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
