#!/usr/bin/env python3
"""Independent corrected-selection/accounting validator for GDT134."""

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "gdt016_group_state_inventory.tsv"
FRAMES = ROOT / "gdt046_line_frames.tsv"
INVENTORY = ROOT / "gdt134_general_continuation_inventory.tsv"
SCORES = ROOT / "gdt134_general_continuation_scores.tsv"
FOLDS = ROOT / "gdt134_general_continuation_folds.tsv"
NULL = ROOT / "gdt134_general_continuation_null.tsv"
CHAIN = ROOT / "gdt134_general_continuation_chain_sensitivity.tsv"
COUNTER = ROOT / "gdt134_general_continuation_counterexamples.tsv"
CORRECTION = ROOT / "gdt134_scope_correction.json"
RESULT = ROOT / "gdt134_result.json"
OUT = ROOT / "gdt134_validation.json"
SECTIONS = {"H", "B", "P", "T", "C"}
Q20 = {"f104", "f105", "f106", "f107", "f112", "f113", "f114", "f115"}
PREFIXES = ("che", "ch", "sh", "t", "s", "d", "q")
RIGHT = ("aiin", "air", "ain", "ar", "al")
MODES = ("RAW_CHAR3", "HOST_CHAR3", "COMPILER12")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def csha(value):
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode()).hexdigest()


def read(path):
    with Path(path).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def guarded_rows(path):
    with Path(path).open(encoding="utf-8", newline="") as handle:
        header = handle.readline().rstrip("\r\n").split("\t")
        locus_i = header.index("locus")
        page_i = header.index("page")
        for line in handle:
            cells = line.rstrip("\r\n").split("\t")
            if cells[locus_i].startswith("f84") or cells[page_i].startswith("f84"):
                continue
            yield dict(zip(header, cells))


def numeric(locus):
    match = re.match(r"^(.*)\.(\d+)$", locus)
    return (match.group(1), int(match.group(2))) if match else None


def strip_layers(token):
    prefix = "NONE"
    host = token
    for candidate in PREFIXES:
        if host.startswith(candidate) and len(host) > len(candidate):
            prefix = candidate
            host = host[len(candidate) :]
            break
    closure = int(host.endswith("dy") and len(host) > 2)
    if closure:
        host = host[:-2]
    return prefix, host, closure


def preparse(prefix, residual):
    b3 = int(residual.endswith("m") and len(residual) > 1)
    host = residual[:-1] if b3 else residual
    right = "NONE"
    for suffix in RIGHT:
        if host.endswith(suffix) and len(host) > len(suffix):
            host = host[: -len(suffix)]
            right = suffix
            break
    inner = int(prefix in {"ch", "che", "sh"} and host.startswith("d") and len(host) > 1)
    if inner:
        host = host[1:]
    return host, b3, right, inner


def independent_parser(source):
    prepared = []
    counts = Counter()
    for row in source:
        prefix, residual, closure = strip_layers(row["token"])
        assert closure == int(row["dy_closure"])
        host, b3, right, inner = preparse(prefix, residual)
        prepared.append((row, prefix, host, b3, right, inner, closure))
        counts[host] += 1
    licensed = {host for host in counts if counts[host] and counts["o" + host] and counts["ot" + host]} | {"ar", "al", "ol"}
    parsed = {}
    for row, prefix, host, b3, right, inner, closure in prepared:
        if host.startswith("ot") and host[2:] in licensed:
            host = host[2:]
        elif host.startswith("o") and host[1:] in licensed:
            host = host[1:]
        parsed[(row["locus"], int(row["group_index"]))] = {
            "token": row["token"],
            "page_host": host or "EMPTY",
            "dy": closure,
        }
    return parsed


def fields(groups):
    out = []
    current = []
    for group in groups:
        current.append(group)
        if group["dy"]:
            out.append(current)
            current = []
    if current:
        out.append(current)
    return out


def selected():
    source = list(guarded_rows(SOURCE))
    parsed = independent_parser(source)
    by = defaultdict(list)
    for row in source:
        if row["section"] in SECTIONS and row["physical_folio"] not in Q20:
            by[row["locus"]].append(row)
    complete = {}
    for locus, rows in by.items():
        rows.sort(key=lambda row: int(row["group_index"]))
        count = int(rows[0]["group_count"])
        if len(rows) == count and [int(row["group_index"]) for row in rows] == list(range(1, count + 1)):
            complete[locus] = rows
    frames = {row["locus"]: row for row in guarded_rows(FRAMES)}
    out = {}
    for locus, rows in complete.items():
        if locus not in frames:
            continue
        position = numeric(locus)
        if not position:
            continue
        next_locus = f"{position[0]}.{position[1] + 1}"
        if next_locus not in complete or next_locus not in frames:
            continue
        if frames[next_locus]["paragraph_start"] != "0":
            continue
        source_groups = [parsed[(locus, int(row["group_index"]))] for row in rows]
        target_groups = [parsed[(next_locus, int(row["group_index"]))] for row in complete[next_locus]]
        last = fields(source_groups)[-1]
        target = fields(target_groups)[0]
        out[(locus, next_locus)] = {
            "page": rows[0]["page"],
            "physical_folio": rows[0]["physical_folio"],
            "section": rows[0]["section"],
            "currier": rows[0]["currier"],
            "hand": rows[0]["hand"],
            "first_paragraph_start": frames[locus]["paragraph_start"],
            "primary_continuation_pair": str(int(frames[locus]["paragraph_start"] == "0")),
            "source_line_number": str(position[1]),
            "source_group_count": str(len(rows)),
            "source_member_count": str(sum(len(row["family_surface"]) for row in rows)),
            "last_field_group_count": str(len(last)),
            "last_field_host_length": str(sum(len(group["page_host"]) for group in last)),
            "last_field_raw_length": str(sum(len(group["token"]) for group in last)),
            "target_first_field_group_count": str(len(target)),
        }
    return out


def strata(inventory, exact):
    groups = defaultdict(list)
    for index, row in enumerate(inventory):
        if row["primary_continuation_pair"] != "1":
            continue
        key = [row["section"], row["currier"], row["hand"], row["source_group_count"]]
        if exact:
            key.extend(
                [row["last_field_group_count"], row["last_field_host_length"], row["last_field_raw_length"]]
            )
        groups[tuple(key)].append(index)
    return groups


def capacity(groups, inventory):
    swappable = sum(len(ids) for ids in groups.values() if len(ids) > 1)
    mobile = sum(
        len(ids)
        for ids in groups.values()
        if len(ids) > 1
        and len({min(4, int(inventory[index]["target_first_field_group_count"])) for index in ids}) > 1
    )
    return swappable, mobile


def close(left, right):
    return abs(float(left) - float(right)) < 2e-10


def main():
    result = json.loads(RESULT.read_text())
    checks = []

    def check(name, value):
        checks.append({"check": name, "pass": bool(value)})
        assert value, name

    check("schema", result["schema"] == "GDT134_GENERAL_ADJACENT_CONTINUATION_TRANSFER_RESULT_V2")
    check("status", result["status"] == "INSUFFICIENT_EXACT_NULL_CAPACITY")
    check("directional", result["directional_outcome"] == "RAW_RESIDUAL_REVERSES_ON_NEW_ORDINARY_CONTINUATIONS")
    prediction = json.loads((ROOT / "gdt134_prediction.json").read_text())
    correction = json.loads(CORRECTION.read_text())
    check("freeze", prediction["status"] == "FROZEN_BEFORE_GENERAL_ADJACENT_PAIR_ENUMERATION")
    check("correction_status", correction["status"] == "POST_ENUMERATION_SCOPE_AND_NULL_CORRECTION_BEFORE_FINAL_RESCORING")
    frozen_correction_hash = correction.pop("correction_content_sha256")
    check("correction_content", csha(correction) == frozen_correction_hash)
    check("superseded_binding", correction["superseded_prepublication_run"]["result_sha256"] == "3022e3ee0cec954a5ef717894b1a7f0dac017477243eea78d38d384051d66416")

    inventory = read(INVENTORY)
    source = selected()
    indexed = {(row["locus"], row["next_locus"]): row for row in inventory}
    check("pair_keys", set(indexed) == set(source))
    check("pair_counts", len(inventory) == result["pairs"] == 252)
    check("folio_counts", len({row["physical_folio"] for row in inventory}) == result["physical_folios"] == 67)
    primary = [row for row in inventory if row["primary_continuation_pair"] == "1"]
    exposed = [row for row in inventory if row["primary_continuation_pair"] == "0"]
    even = [row for row in primary if int(row["source_line_number"]) % 2 == 0]
    odd = [row for row in primary if int(row["source_line_number"]) % 2 == 1]
    check("subset_counts", result["subsets"] == {
        "ALL_DESCRIPTIVE": 252,
        "PRIMARY_CONTINUATION_TO_CONTINUATION": 221,
        "EXPOSED_START_TO_NEXT": 31,
        "PRIMARY_NONOVERLAP_EVEN_SOURCE_LINE": 111,
        "PRIMARY_NONOVERLAP_ODD_SOURCE_LINE": 110,
    })
    check("primary_folios", len({row["physical_folio"] for row in primary}) == 65)
    for key, row in indexed.items():
        expected = source[key]
        check("source_" + row["locus"], all(expected[field] == row[field] for field in expected))
    check("selection", all(row["selection"] == "POST_ENUMERATION_CORRECTED_ALL_F84_EXCLUDED" for row in inventory))
    check("no_f84_inventory", all(not row["page"].startswith("f84") and not row["locus"].startswith("f84") for row in inventory))

    exact = capacity(strata(inventory, True), inventory)
    coarse = capacity(strata(inventory, False), inventory)
    check("capacity", exact == (14, 6) and coarse == (204, 195))
    check("result_capacity", result["null_capacity"] == {
        "exact_swappable": 14,
        "exact_target_mobile": 6,
        "coarse_swappable": 204,
        "coarse_target_mobile": 195,
    })

    scores = read(SCORES)
    folds = read(FOLDS)
    null = read(NULL)
    chain = read(CHAIN)
    score_map = {(row["model"], row["scope"]): row for row in scores}
    result_scores = {(row["model"], row["scope"]): row for row in result["scores"]}
    check("score_rows", len(scores) == len(result_scores) == 30)
    check("fold_rows", len(folds) == 195)
    check("null_rows", len(null) == 6)
    check("chain_rows", len(chain) == 6)
    check("chain_exact", {(row["model"], row["scope"], row["gain_bits"]) for row in chain} == {
        (row["model"], row["scope"], row["gain_bits"])
        for row in scores
        if row["scope"].startswith("PRIMARY_NONOVERLAP")
    })
    for mode in MODES:
        all_score = score_map[mode, "ALL_DESCRIPTIVE"]
        primary_score = score_map[mode, "PRIMARY_CONTINUATION_TO_CONTINUATION"]
        exposed_score = score_map[mode, "EXPOSED_START_TO_NEXT"]
        even_score = score_map[mode, "PRIMARY_NONOVERLAP_EVEN_SOURCE_LINE"]
        odd_score = score_map[mode, "PRIMARY_NONOVERLAP_ODD_SOURCE_LINE"]
        section_scores = [row for row in scores if row["model"] == mode and row["scope"].startswith("PRIMARY_SECTION_")]
        mode_folds = [row for row in folds if row["model"] == mode]
        check("all_add_" + mode, close(all_score["gain_bits"], float(primary_score["gain_bits"]) + float(exposed_score["gain_bits"])))
        check("parity_add_" + mode, close(primary_score["gain_bits"], float(even_score["gain_bits"]) + float(odd_score["gain_bits"])))
        check("section_add_" + mode, close(primary_score["gain_bits"], sum(float(row["gain_bits"]) for row in section_scores)))
        check("fold_count_" + mode, len(mode_folds) == 65)
        check("fold_add_" + mode, close(primary_score["gain_bits"], sum(float(row["gain_bits"]) for row in mode_folds)))
        check("result_score_" + mode, all(close(row["gain_bits"], result_scores[(row["model"], row["scope"])]["gain_bits"]) for row in scores if row["model"] == mode))

    null_map = {(row["null_id"], row["model"]): row for row in null}
    check("null_capacity_rows", all(
        int(null_map[null_id, mode]["swappable_pairs"]) == (14 if null_id == "EXACT_OPPORTUNITY_PRIMARY" else 204)
        and int(null_map[null_id, mode]["target_mobile_pairs"]) == (6 if null_id == "EXACT_OPPORTUNITY_PRIMARY" else 195)
        for null_id in ("EXACT_OPPORTUNITY_PRIMARY", "COARSE_EXACT_SOURCE_COUNT_PRIMARY")
        for mode in MODES
    ))
    raw_all = result_scores["RAW_CHAR3", "ALL_DESCRIPTIVE"]
    raw_primary = result_scores["RAW_CHAR3", "PRIMARY_CONTINUATION_TO_CONTINUATION"]
    gates = {
        "raw_gain_positive_all": raw_all["gain_bits"] > 0,
        "raw_gain_positive_primary_subset": raw_primary["gain_bits"] > 0,
        "raw_beats_host_primary": raw_primary["gain_bits"] > result_scores["HOST_CHAR3", "PRIMARY_CONTINUATION_TO_CONTINUATION"]["gain_bits"],
        "raw_beats_compiler_primary": raw_primary["gain_bits"] > result_scores["COMPILER12", "PRIMARY_CONTINUATION_TO_CONTINUATION"]["gain_bits"],
        "majority_primary_folios_positive": sum(int(row["positive"]) for row in folds if row["model"] == "RAW_CHAR3") > 65 / 2,
        "exact_capacity_at_least_50": False,
        "exact_max_three_p_le_005": False,
    }
    check("gates", gates == result["gates"])
    check("raw_sign_reversal", float(score_map["RAW_CHAR3", "PRIMARY_CONTINUATION_TO_CONTINUATION"]["gain_bits"]) < 0 < float(score_map["RAW_CHAR3", "EXPOSED_START_TO_NEXT"]["gain_bits"]))

    check("input_hashes", all(sha(ROOT / path) == digest for path, digest in result["inputs"].items()))
    check("implementation_hashes", all(sha(ROOT / path) == digest for path, digest in result["implementation"].items()))
    check("output_hashes", all(sha(ROOT / path) == digest for path, digest in result["outputs"].items()))
    check("document_hashes", all(sha(ROOT / path) == digest for path, digest in result["documents"].items()))
    check(
        "scientific_rows_no_f84",
        all(
            not row.get("page", "").startswith("f84")
            and not row.get("locus", "").startswith("f84")
            and not row.get("next_locus", "").startswith("f84")
            for row in inventory
        ),
    )
    check("f84_state", result["f84"] == {
        "f84r_rows_in_actual_sources": 0,
        "all_f84_rows_stream_rejected_before_formal_retention_or_hpr2_parse": True,
        "new_f84r_access": False,
        "prior_limited_f84r_audit_exposure_inherited": True,
    })
    content = dict(result)
    digest = content.pop("result_content_sha256")
    check("result_content", csha(content) == digest)

    validation = {
        "schema": "GDT134_GENERAL_ADJACENT_CONTINUATION_TRANSFER_VALIDATION_V2",
        "status": "PASS_INDEPENDENT_CORRECTED_SELECTION_AND_ACCOUNTING",
        "checks": len(checks),
        "passed": sum(row["pass"] for row in checks),
        "scope": (
            "Independent guarded source selection, HPR2 host reconstruction, exact-source-count "
            "capacity, retained score/fold/null accounting, correction, gates, hashes, and f84 "
            "exclusion; trained coefficients and permutation worlds are not independently refit."
        ),
        "result_sha256": sha(RESULT),
        "validator_sha256": sha(Path(__file__)),
        "check_rows": checks,
    }
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": validation["status"], "checks": validation["checks"]}, sort_keys=True))


if __name__ == "__main__":
    main()
