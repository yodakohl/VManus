#!/usr/bin/env python3
"""GDT1125 shared application source, blocked until the explicit root GO.

No candidate interpretation, prior lookup, fitting or legacy main is called.
The sole body query has twenty hard-coded locus allow-values. FV eligibility is
the current-only subset; earlier paragraphs are available to FW only.
"""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import io
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[4]
BASE = Path(__file__).resolve().parents[1]
ARTIFACTS = BASE / "artifacts"
SPEC = BASE / "src/SPEC.json"
OPEN = ARTIFACTS / "OPEN_RECEIPT.json"
SOURCE = "experiments/semantic_assumptions/results/source_separator_transcription.tsv"
ALLOWLIST = "experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv"
RUNNER = "experiments/yolo/gdt1051_frozen_grammar_local_application/src/run.py"
MERGES = "experiments/yolo/gdt605_multisymbol_unit_alphabet/artifacts/gdt605_bpe_merges.tsv"
UNIT_LOCI = {
    "FW_F75V_PREVIOUS": [f"f75v.{n}" for n in range(38, 43)],
    "FW_F75V_CURRENT": [f"f75v.{n}" for n in range(43, 50)],
    "FW_F104V_PREVIOUS": [f"f104v.{n}" for n in range(19, 22)],
    "FW_F104V_CURRENT": [f"f104v.{n}" for n in range(22, 27)],
}
LOCUS_UNITS = {locus: unit for unit, loci in UNIT_LOCI.items() for locus in loci}
FV_LOCI = [locus for unit, loci in UNIT_LOCI.items() if unit.endswith("CURRENT") for locus in loci]
EDITIONS = ("ZL3b", "IT2a", "RF1b")
COLUMNS = (
    "source_group_id", "edition", "locus", "page", "section", "currier",
    "hand", "code", "kind", "grammar_scope", "source_row_index",
    "source_group_index", "source_group_count", "paragraph_start",
    "paragraph_end", "left_separator", "right_separator", "ivtff_group_raw",
)
FROZEN_PINS = {
    SOURCE: "4b649c8290d5afc7a5fbcc8e98db2bc123a1ceb5f3858d3befa781ce96b680f0",
    ALLOWLIST: "f0def5a04bd91443cf4770c78f1b67e62cac2060627d8de38faba27899188483",
    RUNNER: "8fd6000574b289dd539e9a7b04c45e15a5a767871dae770fd454af91c7146ba2",
    "run_gdt012_core_semantic_atlas.py": "7db6d7eff0937e9fa67a77356a61e00a0e28a6cd73b2c62146844adea8b8fc1c",
    "run_gdt062_right_family_register_renderer.py": "9c9e7a35278d59ace7dd88f3c1e0ca6112ec48cef29fdd86c4e5546c6ec9a665",
    "experiments/yolo/gdt605_multisymbol_unit_alphabet/src/separator_crossing.py": "921c6617615980ed41bf70c8cdf574aa2a15621832e7842dd9dd3621461bf8e8",
    MERGES: "4625c9389ead390907e4ac74e65bc158236f02b439c69cf3b09157f0cd6ca539",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def relative(path):
    return Path(path).relative_to(ROOT).as_posix()


def pinned_path(name):
    require(isinstance(name, str) and name, "Invalid frozen input path")
    p = Path(name)
    require(not p.is_absolute() and ".." not in p.parts, "Frozen paths must be repository-relative")
    result = (ROOT / p).resolve()
    require(result.is_relative_to(ROOT) and result.is_file(), "Frozen input missing or outside repository")
    return result


def verify_open_gate():
    # These metadata checks precede the only guarded body query. Use explicit
    # checks, not assertions that python -O could remove.
    require(SPEC.is_file() and OPEN.is_file(), "Application opening requires frozen SPEC and explicit root GO")
    spec_bytes, open_bytes = SPEC.read_bytes(), OPEN.read_bytes()
    spec, opening = json.loads(spec_bytes), json.loads(open_bytes)
    require(spec.get("status") == "PREOPEN_FROZEN", "SPEC is not PREOPEN_FROZEN")
    require(opening.get("status") == "ROOT_EXPLICIT_APPLICATION_GO", "Root application GO is absent")
    spec_sha = hashlib.sha256(spec_bytes).hexdigest()
    require(opening.get("spec_sha256") == spec_sha, "Root GO does not bind the exact frozen SPEC")
    pins = spec.get("input_hashes")
    require(isinstance(pins, dict) and pins, "SPEC input_hashes map is absent")
    for name, expected in pins.items():
        require(isinstance(expected, str) and re.fullmatch(r"[0-9a-f]{64}", expected), "Invalid SPEC input hash")
        require(sha(pinned_path(name)) == expected, f"Frozen SPEC input changed: {name}")
    models = spec.get("model_files")
    require(isinstance(models, dict) and set(models) == {"FV", "FW"}, "Both frozen candidate model-file lists are required")
    for candidate, names in models.items():
        require(isinstance(names, list) and names and len(set(names)) == len(names), f"Invalid {candidate} model-file list")
        require(all(isinstance(name, str) and name in pins for name in names), f"Every {candidate} model input must be pinned")
    own_name = relative(__file__)
    require(pins.get(own_name) == sha(__file__), "SPEC does not freeze this exact application preparer")
    for name, expected in FROZEN_PINS.items():
        require(pins.get(name) == expected, f"SPEC omits or changes required canonical/formal pin: {name}")
        require(sha(ROOT / name) == expected, f"Canonical/formal input changed: {name}")
    require(len(LOCUS_UNITS) == 20 and len(FV_LOCI) == 12, "Fixed application scope changed")
    with (ROOT / ALLOWLIST).open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        require(reader.fieldnames == ["page"], "Admission allowlist schema changed")
        selectors = [row["page"] for row in reader]
    require(len(selectors) == len(set(selectors)) == 179, "Admission selector count changed")
    require({"f75v", "f104v"}.issubset(selectors), "Application selectors are not admitted")
    return {
        "spec": spec, "spec_sha256": spec_sha,
        "open_receipt_sha256": hashlib.sha256(open_bytes).hexdigest(),
        "input_hashes": pins,
    }


def main():
    gate = verify_open_gate()
    command = ["./vmanus-exp", "query-tsv", SOURCE, "--selector", "locus"]
    for locus in LOCUS_UNITS:
        command += ["--allow", locus]
    command += ["--columns", ",".join(COLUMNS), "--forbid-prefix", "f84", "--forbid-prefix", "f84r"]
    queried = subprocess.run(command, cwd=ROOT, capture_output=True, check=True)
    receipts = [line[12:] for line in queried.stderr.decode().splitlines() if line.startswith("GUARD_STATS ")]
    require(len(receipts) == 1, "One selector guard receipt is required")
    guard = json.loads(receipts[0])
    reader = csv.DictReader(io.StringIO(queried.stdout.decode("utf-8")), delimiter="\t")
    require(reader.fieldnames == list(COLUMNS), "Guarded canonical columns changed")
    rows = list(reader)  # Only the twenty-locus guarded projection is decoded.
    require(len(rows) == guard["selected"], "Source count differs from guard receipt")
    require(len({r["source_group_id"] for r in rows}) == len(rows), "Duplicate source IDs")
    require(all(set(r) == set(COLUMNS) and None not in r.values() for r in rows), "Malformed canonical source fields")
    byline = defaultdict(list)
    for row in rows:
        require(row["locus"] in LOCUS_UNITS and row["edition"] in EDITIONS, "Unexpected application reader or locus")
        require(row["page"] in {"f75v", "f104v"}, "Unexpected application selector")
        byline[row["edition"], row["locus"]].append(row)
    require(set(byline) == {(ed, loc) for ed in EDITIONS for loc in LOCUS_UNITS}, "Missing complete reader/locus source cell")
    for line in byline.values():
        count = len(line)
        require([int(r["source_group_index"]) for r in line] == list(range(1, count + 1)), "Incomplete native group order")
        require(all(int(r["source_group_count"]) == count for r in line), "Native group-count mismatch")
        for field in ("paragraph_start", "paragraph_end"):
            require(len({r[field] for r in line}) == 1, "Inconsistent native line flags")
        if line[0]["edition"] == "RF1b":
            require(all(r["paragraph_start"] == r["paragraph_end"] == "0" for r in line), "RF native flag availability changed; review rather than impute")

    # GDT1051 imports define constants/functions; guarded legacy mains and old
    # source readers are not invoked. No fitting, new licenses or prior lookup.
    module_spec = importlib.util.spec_from_file_location("gdt1125_frozen_gdt1051", ROOT / RUNNER)
    formal = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(formal)
    merges = formal.load_merges()
    parsed = [formal.parse_group(LOCUS_UNITS[r["locus"]], r) for r in rows]
    chunks = formal.make_chunks(parsed, merges)
    memberships = {}
    for ordinal, chunk in enumerate(chunks, 1):
        chunk["chunk_id"] = f"GDT1125_APPLICATION_CHUNK_{ordinal:04d}"
        for index in chunk["group_indices"]:
            key = (chunk["edition"], chunk["locus"], index)
            require(key not in memberships, "Duplicate formal chunk membership")
            memberships[key] = chunk["chunk_id"]
    require(len(memberships) == len(rows), "Formal chunk source omission")
    unit_order = Counter()
    groups = []
    for row, result in zip(rows, parsed):
        unit = LOCUS_UNITS[row["locus"]]
        key = (row["edition"], unit)
        unit_order[key] += 1
        current = unit.endswith("CURRENT")
        groups.append({**row, "unit_id": unit, "unit_reader_order": unit_order[key],
                       "paragraph_role": "CURRENT" if current else "PREVIOUS",
                       "candidate_scoring_scope": ["FV", "FW"] if current else ["FW"],
                       "fv_scoring_eligible": current,
                       "native_paragraph_flags_available": row["edition"] != "RF1b",
                       "formal_gdt012_062": result,
                       "formal_gdt605_chunk_id": memberships[row["edition"], row["locus"], int(row["source_group_index"])]})
    coverage = []
    for unit, loci in UNIT_LOCI.items():
        for edition in EDITIONS:
            count = sum(len(byline[edition, locus]) for locus in loci)
            coverage.append({"unit_id": unit, "edition": edition, "loci": loci,
                             "paragraph_role": "CURRENT" if unit.endswith("CURRENT") else "PREVIOUS",
                             "literal_group_count": count,
                             "native_paragraph_flags_available": edition != "RF1b",
                             "native_start_loci": [loc for loc in loci if byline[edition, loc][0]["paragraph_start"] == "1"],
                             "native_end_loci": [loc for loc in loci if byline[edition, loc][0]["paragraph_end"] == "1"],
                             "candidate_scoring_scope": ["FV", "FW"] if unit.endswith("CURRENT") else ["FW"]})
    gate_after = verify_open_gate()
    require(gate_after == gate, "Root frozen inputs or opening receipt changed during preparation")
    projection_sha = hashlib.sha256(queried.stdout).hexdigest()
    query_receipt = {
        "command": command, "selector": "locus", "allow_values": list(LOCUS_UNITS),
        "output_columns": list(COLUMNS), "guard_stats": guard,
        "projection_sha256": projection_sha,
    }
    packet = {
        "schema": "gdt1125-application-native-v1", "status": "SOURCE_AND_FROZEN_FORMAL_PREPARATION_ONLY",
        "spec_path": relative(SPEC), "spec_sha256": gate["spec_sha256"],
        "open_receipt_path": relative(OPEN), "open_receipt_sha256": gate["open_receipt_sha256"],
        "preparer_path": relative(__file__), "preparer_sha256": sha(__file__),
        "input_hashes": gate["input_hashes"], "query_receipt": query_receipt,
        "raw_projection_path": relative(ARTIFACTS / "APPLICATION_GROUPS.tsv"),
        "raw_projection_sha256": projection_sha,
        "source_receipt_path": relative(ARTIFACTS / "SOURCE_RECEIPT.json"),
        "allowed_loci": list(LOCUS_UNITS), "editions": list(EDITIONS),
        "physical_locus_count": len(LOCUS_UNITS), "raw_group_count": len(rows),
        "candidate_scopes": {"FV": {"loci": FV_LOCI, "earlier_role_donation_permitted": False},
                             "FW": {"loci": list(LOCUS_UNITS), "previous_current_pairs": list(UNIT_LOCI)}},
        "coverage": coverage, "groups": groups, "chunks": chunks,
        "formal_summary": {"eligible_groups": sum(g["parse_status"] == "PURE_FUNCTION_REPLAY" for g in parsed),
                           "unresolved_marked_or_nonlowercase_groups": sum(g["parse_status"] != "PURE_FUNCTION_REPLAY" for g in parsed),
                           "hard_chunks": len(chunks), "eligible_chunks": sum(c["units"] is not None for c in chunks),
                           "merges": len(merges), "new_rules_or_licenses": False},
        "native_RF_paragraph_boundaries_imputed": False, "new_priors_or_outside_bodies": False,
        "confirmed_words": 0, "semantic_validation": False,
        "preservation_claim": "Canonical group/separator fields, not a separately queried diplomatic full-line transcription",
        "sealed_data": {"f84": "FORBIDDEN_AND_ABSENT", "f84r": "FORBIDDEN_AND_ABSENT"},
    }
    packet_bytes = (json.dumps(packet, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    packet_sha = hashlib.sha256(packet_bytes).hexdigest()
    receipt = {
        "schema": "gdt1125-application-source-receipt-v1", "status": "PASS_SOURCE_ACCOUNTING_ONLY",
        "source_path": SOURCE, "source_sha256": FROZEN_PINS[SOURCE],
        "allowlist_path": ALLOWLIST, "allowlist_sha256": FROZEN_PINS[ALLOWLIST],
        "preparer_path": relative(__file__), "preparer_sha256": sha(__file__),
        "input_hashes": gate["input_hashes"], "model_files": gate["spec"]["model_files"],
        "spec_sha256": gate["spec_sha256"], "open_receipt_sha256": gate["open_receipt_sha256"],
        "query_receipt": query_receipt, "coverage": coverage,
        "unique_source_groups": len(rows), "physical_loci": len(LOCUS_UNITS), "reader_locus_cells": len(byline),
        "application_packet_path": relative(ARTIFACTS / "APPLICATION_PACKET.json"),
        "application_packet_sha256": packet_sha,
        "application_groups_path": relative(ARTIFACTS / "APPLICATION_GROUPS.tsv"),
        "application_groups_sha256": projection_sha,
        "candidate_scopes": packet["candidate_scopes"],
        "formal_summary": packet["formal_summary"], "semantic_validation": False,
    }
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    (ARTIFACTS / "APPLICATION_GROUPS.tsv").write_bytes(queried.stdout)
    (ARTIFACTS / "APPLICATION_PACKET.json").write_bytes(packet_bytes)
    receipt_path = ARTIFACTS / "SOURCE_RECEIPT.json"
    receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"application_packet_sha256": packet_sha,
                      "application_groups_sha256": projection_sha,
                      "source_receipt_sha256": sha(receipt_path),
                      "raw_groups": len(rows), "coverage": coverage,
                      "formal_summary": packet["formal_summary"]}, indent=2))


if __name__ == "__main__":
    main()
