#!/usr/bin/env python3
"""Independent reconstruction of the GDT038 context-transfer checkpoint."""
from __future__ import annotations

import csv
import hashlib
import itertools
import json
import math
import statistics
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "gdt016_group_state_inventory.tsv"
OCC = ROOT / "gdt038_occurrence_contexts.tsv"
CLUSTERS = ROOT / "gdt038_context_clusters.tsv"
COMPARE = ROOT / "gdt038_role_comparison.tsv"
RESULT = ROOT / "gdt038_result.json"
VALIDATION = ROOT / "gdt038_validation.json"
LEDGER = ROOT / "GDT002_YOLO_LEDGER.tsv"
CORES = ("daiin", "dam", "okam", "odain")
FEATURES = ("target_state", "wrapper", "field_position", "field_role",
            "previous_state", "next_state", "previous_field_shape",
            "next_field_shape", "micro_context", "masked_field_template",
            "neighbor_field_context")


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha(value):
    raw = json.dumps(value, sort_keys=True, ensure_ascii=True,
                     separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def section(row):
    if row["section"] == "H" and row["currier"] == "B":
        return "HB"
    if row["section"] == "S" and row["currier"] == "B":
        return "SB"
    return "OUT"


def field_shape(field, closed):
    states = [row["record_state"] for _, row in field]
    bucket = str(len(field)) if len(field) <= 3 else "4PLUS"
    return f'{"CLOSED" if closed else "OPEN"}|LEN_{bucket}|{states[0]}>{states[-1]}'


def reconstruct_occurrences(source_rows):
    lines = defaultdict(list)
    for row in source_rows:
        assert not row["locus"].startswith("f84r")
        lines[row["locus"]].append(row)
    output = []
    for locus, line in lines.items():
        line.sort(key=lambda row: int(row["group_index"]))
        sec = section(line[0])
        if sec not in {"HB", "SB"}:
            continue
        fields, current = [], []
        for index, row in enumerate(line):
            current.append((index, row))
            if row["record_state"] == "DY_RESOLUTION":
                fields.append((current, True))
                current = []
        if current:
            fields.append((current, False))
        address = {index: (fi, position)
                   for fi, (field, _) in enumerate(fields)
                   for position, (index, _) in enumerate(field)}
        for index, row in enumerate(line):
            core = row["residual_host"]
            if core not in CORES:
                continue
            fi, position = address[index]
            field, closed = fields[fi]
            states = [item[1]["record_state"] for item in field]
            size = len(field)
            previous = line[index - 1] if index else None
            following = line[index + 1] if index + 1 < len(line) else None
            if size == 1:
                field_position = "SINGLE"
            elif position == 0:
                field_position = "FIELD_START"
            elif position == size - 1:
                field_position = "FIELD_CLOSE" if closed else "OPEN_FIELD_END"
            elif closed and position == size - 2:
                field_position = "PRECLOSE"
            else:
                field_position = "FIELD_INTERNAL"
            previous_field_shape = ("BOL" if fi == 0 else
                                    field_shape(fields[fi - 1][0], fields[fi - 1][1]))
            next_field_shape = ("EOL" if fi + 1 == len(fields) else
                                field_shape(fields[fi + 1][0], fields[fi + 1][1]))
            previous_field_states = ("BOL" if fi == 0 else ">".join(
                item[1]["record_state"] for item in fields[fi - 1][0]))
            next_field_states = ("EOL" if fi + 1 == len(fields) else ">".join(
                item[1]["record_state"] for item in fields[fi + 1][0]))
            masked = list(states)
            masked[position] = f'TARGET[{row["record_state"]}]'
            masked = ">".join(masked) + ("" if closed else ">OPEN")
            previous_state = "BOS" if previous is None else previous["record_state"]
            next_state = "EOS" if following is None else following["record_state"]
            length_bucket = size if size <= 3 else "4PLUS"
            role = (f'{"CLOSED" if closed else "OPEN"}|LEN_{length_bucket}|'
                    f'{field_position}|{row["record_state"]}')
            output.append({
                "locus": locus, "page": row["page"],
                "physical_folio": row["physical_folio"], "section": sec,
                "hand": row["hand"], "group_index": row["group_index"],
                "group_count": row["group_count"], "token": row["token"],
                "wrapper": row["stripped_prefix"], "core": core,
                "wrapper_core": row["stripped_prefix"] + "|" + core,
                "target_state": row["record_state"],
                "line_position": f'{index + 1}/{len(line)}',
                "field_index": str(fi + 1), "field_count": str(len(fields)),
                "field_length": str(size), "field_closed": str(int(closed)),
                "field_position": field_position, "field_role": role,
                "previous_token": "BOS" if previous is None else previous["token"],
                "previous_core": "BOS" if previous is None else previous["residual_host"],
                "previous_state": previous_state,
                "next_token": "EOS" if following is None else following["token"],
                "next_core": "EOS" if following is None else following["residual_host"],
                "next_state": next_state,
                "previous_field_states": previous_field_states,
                "previous_field_shape": previous_field_shape,
                "current_field_states": ">".join(states),
                "masked_field_template": masked,
                "next_field_states": next_field_states,
                "next_field_shape": next_field_shape,
                "micro_context": previous_state + ">TARGET[" + row["record_state"] + "]>" + next_state,
                "neighbor_field_context": previous_field_shape + "||" + next_field_shape,
            })
    output.sort(key=lambda row: (CORES.index(row["core"]), row["locus"],
                                 int(row["group_index"])))
    return output


def jsd(left, right):
    nl, nr = sum(left.values()), sum(right.values())
    answer = 0.0
    for key in sorted(set(left) | set(right)):
        p, q = left[key] / nl, right[key] / nr
        middle = (p + q) / 2
        if p:
            answer += 0.5 * p * math.log2(p / middle)
        if q:
            answer += 0.5 * q * math.log2(q / middle)
    return answer


def overlap(left, right):
    nl, nr = sum(left.values()), sum(right.values())
    shared = sum(min(left[key] / nl, right[key] / nr)
                 for key in sorted(set(left) | set(right)))
    return shared / (2 - shared) if shared < 2 else 1.0


def feature_stats(rows, feature):
    hb = Counter(row[feature] for row in rows if row["section"] == "HB")
    sb = Counter(row[feature] for row in rows if row["section"] == "SB")
    folios = sorted({row["physical_folio"] for row in rows})
    hb_count = len({row["physical_folio"] for row in rows
                    if row["section"] == "HB"})
    null = []
    for chosen_tuple in itertools.combinations(folios, hb_count):
        chosen = set(chosen_tuple)
        left = Counter(row[feature] for row in rows
                       if row["physical_folio"] in chosen)
        right = Counter(row[feature] for row in rows
                        if row["physical_folio"] not in chosen)
        null.append(jsd(left, right))
    observed = jsd(hb, sb)
    deletions = []
    for held in folios:
        remaining = [row for row in rows if row["physical_folio"] != held]
        left = Counter(row[feature] for row in remaining if row["section"] == "HB")
        right = Counter(row[feature] for row in remaining if row["section"] == "SB")
        if left and right:
            deletions.append((overlap(left, right), jsd(left, right)))
    hand3 = [row for row in rows if row["hand"] == "3"]
    hleft = Counter(row[feature] for row in hand3 if row["section"] == "HB")
    hright = Counter(row[feature] for row in hand3 if row["section"] == "SB")
    return {
        "levels": len(set(hb) | set(sb)),
        "weighted_jaccard": overlap(hb, sb), "js_divergence_bits": observed,
        "folio_permutation_local_p": sum(value >= observed - 1e-15 for value in null) / len(null),
        "permutation_worlds": len(null),
        "lofo_min_weighted_jaccard": min(item[0] for item in deletions),
        "lofo_max_js_divergence_bits": max(item[1] for item in deletions),
        "hand3_weighted_jaccard": overlap(hleft, hright) if hleft and hright else math.nan,
        "hand3_hb_count": sum(hleft.values()), "hand3_sb_count": sum(hright.values()),
        "_null": null,
    }


def close(actual, expected, tolerance=5e-9):
    if math.isnan(expected):
        return actual.lower() == "nan"
    return abs(float(actual) - expected) <= tolerance


def main():
    checks = {}
    source = read(SOURCE)
    expected_occ = reconstruct_occurrences(source)
    actual_occ = read(OCC)
    checks["occurrence_rows_exact"] = actual_occ == expected_occ
    checks["occurrence_count_and_core_counts"] = (
        len(actual_occ) == 65 and Counter(row["core"] for row in actual_occ) ==
        Counter({"daiin": 23, "dam": 8, "okam": 16, "odain": 18}) and
        len({row["physical_folio"] for row in actual_occ}) == 21)
    checks["no_f84_source_or_occurrence"] = (not any(
        row["locus"].startswith("f84r") for row in source + actual_occ))

    comparison = {(row["core"], row["feature"]): row for row in read(COMPARE)}
    numeric_exact = True
    state_claims = True
    for core in CORES:
        rows = [row for row in expected_occ if row["core"] == core]
        stats = [feature_stats(rows, feature) for feature in FEATURES]
        means = [statistics.mean(item["_null"]) for item in stats]
        deviations = [statistics.stdev(item["_null"]) if len(item["_null"]) > 1 else 0
                      for item in stats]
        zscores = [((item["js_divergence_bits"] - mean) / deviation if deviation else 0)
                   for item, mean, deviation in zip(stats, means, deviations)]
        maxz = [max(((item["_null"][world] - mean) / deviation if deviation else 0)
                    for item, mean, deviation in zip(stats, means, deviations))
                for world in range(len(stats[0]["_null"]))]
        for feature, item, zscore in zip(FEATURES, stats, zscores):
            stored = comparison[core, feature]
            for key in ("weighted_jaccard", "js_divergence_bits",
                        "folio_permutation_local_p", "lofo_min_weighted_jaccard",
                        "lofo_max_js_divergence_bits", "hand3_weighted_jaccard"):
                numeric_exact &= close(stored[key], item[key])
            numeric_exact &= int(stored["levels"]) == item["levels"]
            numeric_exact &= int(stored["permutation_worlds"]) == item["permutation_worlds"]
            numeric_exact &= int(stored["hand3_hb_count"]) == item["hand3_hb_count"]
            numeric_exact &= int(stored["hand3_sb_count"]) == item["hand3_sb_count"]
            maxt = sum(value >= zscore - 1e-15 for value in maxz) / len(maxz)
            numeric_exact &= close(stored["folio_permutation_maxT_p"], maxt)
        if core in {"daiin", "dam"}:
            state_claims &= Counter(row["target_state"] for row in rows) == {"CARRIER_STATE": len(rows)}
    checks["all_comparison_metrics_independently_reconstructed"] = numeric_exact
    checks["daiin_dam_carrier_state_exact"] = state_claims
    dam = [row for row in expected_occ if row["core"] == "dam"]
    checks["dam_final_open_field_pattern"] = (len(dam) == 8 and
        all(row["next_field_shape"] == "EOL" and row["field_closed"] == "0" for row in dam) and
        Counter(row["field_position"] for row in dam) == {"OPEN_FIELD_END": 5, "FIELD_INTERNAL": 3})

    expected_clusters = []
    for core in CORES:
        rows = [row for row in expected_occ if row["core"] == core]
        for feature in FEATURES:
            groups = defaultdict(list)
            for row in rows:
                groups[row[feature]].append(row)
            for template, items in groups.items():
                hc = sum(row["section"] == "HB" for row in items)
                sc = sum(row["section"] == "SB" for row in items)
                hf = len({row["physical_folio"] for row in items if row["section"] == "HB"})
                sf = len({row["physical_folio"] for row in items if row["section"] == "SB"})
                if hc and sc and hf and sf:
                    classification = "CROSS_SECTION_CROSS_FOLIO"
                elif len(items) >= 2:
                    classification = "SECTION_SPECIFIC_RECURRENT"
                else:
                    classification = "SINGLETON"
                expected_clusters.append({"core": core, "feature": feature,
                    "template": template, "hb_count": str(hc), "sb_count": str(sc),
                    "hb_folios": str(hf), "sb_folios": str(sf),
                    "total_folios": str(len({row["physical_folio"] for row in items})),
                    "classification": classification})
    expected_clusters.sort(key=lambda row: (CORES.index(row["core"]),
        FEATURES.index(row["feature"]), -int(row["hb_count"]) - int(row["sb_count"]),
        row["template"]))
    checks["cluster_atlas_exact"] = read(CLUSTERS) == expected_clusters

    result = json.loads(RESULT.read_text())
    content = dict(result)
    claimed_content_sha = content.pop("result_content_sha256")
    checks["result_content_hash"] = canonical_sha(content) == claimed_content_sha
    checks["result_status"] = result["status"] == (
        "DAM_FIELD_ROLE_PROVISIONAL_LOW_CAPACITY_DAIIN_STATE_ONLY_"
        "OKAM_ODAIN_SECTION_CONDITIONED")
    checks["input_output_document_hashes"] = all(
        sha(ROOT / name) == digest
        for family in ("inputs", "outputs", "documents")
        for name, digest in result[family].items())
    checks["implementation_hash"] = all(
        sha(ROOT / name) == digest for name, digest in result["implementation"].items())
    checks["f84_flags_false"] = not any(result["f84r"].values())
    report = (ROOT / "GDT038_CORE_CONTEXT_TRANSFER_REPORT.md").read_text()
    checks["claim_ceiling_and_dependency_disclosed"] = (
        "No concrete function" in report and "independent role evidence" in report
        and "f84r was not opened" in report)
    ledger = read(LEDGER)
    entries = [row for row in ledger if row["checkpoint_id"] == "GDT038_CKPT001"]
    checks["ledger_entry_exact"] = (len(entries) == 1 and
        entries[0]["result_artifact"] == RESULT.name and
        entries[0]["status"] == result["status"] and
        entries[0]["holdout_page"] == "f84r" and
        entries[0]["discovery_pages"] ==
        "65_OCCURRENCES_4_CORES_21_PHYSICAL_FOLIOS_11_CONTEXT_VIEWS")
    passed = all(checks.values())
    validation = {
        "schema": "GDT038_CORE_CONTEXT_TRANSFER_VALIDATION_V1",
        "status": "PASS_INDEPENDENT_RECONSTRUCTION" if passed else "FAIL",
        "checks": checks, "checks_passed": sum(checks.values()),
        "checks_total": len(checks), "result_sha256": sha(RESULT),
        "validator_sha256": sha(Path(__file__)),
        "scope": "Independent source-to-context reconstruction, metrics, folio permutations, clusters, hashes, claims, and ledger.",
    }
    VALIDATION.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": validation["status"],
                      "checks": f'{validation["checks_passed"]}/{validation["checks_total"]}'},
                     sort_keys=True))
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
