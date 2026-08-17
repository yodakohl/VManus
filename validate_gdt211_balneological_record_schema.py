#!/usr/bin/env python3
"""Independent retained-artifact validation for GDT211."""
from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

R = Path(__file__).resolve().parent
RESULT = R / "gdt211_result.json"
VALIDATION = R / "gdt211_validation.json"
FRAMES = R / "gdt046_line_frames.tsv"
HPR2 = R / "gdt062_right_family_inventory.tsv"
SOURCE_INVENTORY = R / "gdt211_de_balneis_entry_inventory.tsv"
SOURCE_FREEZE = R / "gdt211_source_freeze.json"
LINE_INVENTORY = R / "gdt211_q13_line_inventory.tsv"
TESTS = R / "gdt211_record_schema_tests.tsv"
NULLS = R / "gdt211_null_results.tsv"
COUNTEREXAMPLES = R / "gdt211_counterexamples.tsv"
Q13 = {f"f{i}" for i in range(75, 84)}
checks: list[str] = []


def ok(name: str, condition: bool) -> None:
    assert condition, name
    checks.append(name)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def csha(value: dict) -> str:
    raw = json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


result = json.loads(RESULT.read_text(encoding="utf-8"))
stored_content = result.pop("result_content_sha256")
ok("result_content_hash", csha(result) == stored_content)
result["result_content_sha256"] = stored_content
ok("status_literal", result["status"] == "BALNEOLOGICAL_RECORD_SCHEMA_COMPATIBLE_BUT_GENERIC_LINE_OPENING_CONFOUND")
ok("no_semantic_mapping", result["semantic_mapping"] == "NONE")
ok("f84_guard", result["f84"] == {"all_f84_rows_rejected_before_formal_retention": True, "f84v_page_metadata_seen_only_by_guard": True, "f84v_source_rows_rejected": 249, "f84v_formal_fields_retained": False, "f84r_present_in_source": False, "f84r_accessed": False, "joined": False, "scored": False})

for name, digest in result["inputs"].items():
    ok(f"input_hash:{name}", sha(R / name) == digest)
for name, digest in result["outputs"].items():
    ok(f"output_hash:{name}", sha(R / name) == digest)
for name, digest in result["documents"].items():
    ok(f"document_hash:{name}", sha(R / name) == digest)
for name, digest in result["implementation"].items():
    ok(f"implementation_hash:{name}", sha(R / name) == digest)

source_rows = read(SOURCE_INVENTORY)
baths = [row for row in source_rows if row["record_class"] == "BATH_RECORD"]
ok("source_33_numbered", len(source_rows) == 33 and [int(row["entry_number"]) for row in source_rows] == list(range(1, 34)))
ok("source_32_baths", len(baths) == 32)
ok("dedication_excluded", [row["entry_number"] for row in source_rows if row["record_class"] == "META_DEDICATION"] == ["31"])
role_counts = {role: sum(int(row[role]) for row in baths) for role in ("identity", "location_access", "hydraulic_physical", "indication", "procedure_caution", "outcome_testimony")}
ok("source_role_counts", role_counts == {"identity": 32, "location_access": 17, "hydraulic_physical": 23, "indication": 32, "procedure_caution": 20, "outcome_testimony": 6})
freeze = json.loads(SOURCE_FREEZE.read_text(encoding="utf-8"))
ok("source_freeze_status", freeze["status"] == "EXTERNAL_BALNEOLOGICAL_RECORD_SCHEMA_FROZEN_BEFORE_Q13_SCORE")
ok("source_freeze_commit_bound", result["chronology"]["external_source_freeze_commit"] == "4d62597" and result["chronology"]["target_scored_after_freeze"] is True)

# Independent source rebuild.  Reject f84 before retaining formal fields.
frame_rows = []
with FRAMES.open(encoding="utf-8", newline="") as handle:
    reader = csv.reader(handle, delimiter="\t")
    header = next(reader)
    pi = header.index("page")
    for values in reader:
        if values[pi].startswith("f84"):
            continue
        frame_rows.append(dict(zip(header, values)))
frames = {row["locus"]: row for row in frame_rows}
first_group: dict[str, dict[str, str]] = {}
with HPR2.open(encoding="utf-8", newline="") as handle:
    reader = csv.reader(handle, delimiter="\t")
    header = next(reader)
    pi = header.index("page")
    li = header.index("locus")
    gi = header.index("group_index")
    for values in reader:
        if values[pi].startswith("f84"):
            continue
        locus = values[li]
        if locus in frames and int(values[gi]) == 1:
            first_group[locus] = dict(zip(header, values))

primary = []
for locus, frame in frames.items():
    group = first_group.get(locus)
    if not group or group["page"][:3] not in Q13 or group["section"] != "B":
        continue
    primary.append({
        "locus": locus,
        "page": group["page"],
        "folio": group["physical_folio"],
        "start": int(frame["paragraph_start"]),
        "n": int(frame["group_count"]),
        "host": group["page_host"],
        "token": group["token"],
    })
ok("primary_line_count", len(primary) == 233)
ok("primary_start_count", sum(row["start"] for row in primary) == 17)
ok("primary_folio_count", len({row["folio"] for row in primary}) == 9)
ok("no_f84_primary", not any(row["page"].startswith("f84") for row in primary))


def metric(field: str) -> tuple[float, int, int, list[int]]:
    folios: dict[str, set[str]] = defaultdict(set)
    for row in primary:
        folios[row[field]].add(row["folio"])
    values = [int(len(folios[row[field]]) >= 2) for row in primary]
    starts = [v for v, row in zip(values, primary) if row["start"]]
    body = [v for v, row in zip(values, primary) if not row["start"]]
    return sum(body) / len(body) - sum(starts) / len(starts), sum(starts), sum(body), values


host_effect, host_start, host_body, host_values = metric("host")
token_effect, token_start, token_body, token_values = metric("token")
ok("host_counts", host_start == 8 and host_body == 164)
ok("token_counts", token_start == 4 and token_body == 113)
ok("host_effect", abs(host_effect - result["primary_page_host"]["continuation_minus_start_recurrence"]) < 1e-14)
ok("token_effect", abs(token_effect - result["primary_raw_token"]["continuation_minus_start_recurrence"]) < 1e-14)


def exact_count_p(values: list[int]) -> tuple[int, int, int, float]:
    strata: dict[tuple[str, int], list[int]] = defaultdict(list)
    for i, row in enumerate(primary):
        strata[row["page"], row["n"]].append(i)
    observed = sum(values[i] for i, row in enumerate(primary) if row["start"])
    distribution = {0: 1}
    total = 1
    swappable = 0
    mobile = 0
    for indices in strata.values():
        n = len(indices)
        k = sum(primary[i]["start"] for i in indices)
        success = sum(values[i] for i in indices)
        total *= math.comb(n, k)
        if 0 < k < n:
            swappable += n
            mobile += 1
        local = {j: math.comb(success, j) * math.comb(n - success, k - j) for j in range(max(0, k - (n - success)), min(k, success) + 1)}
        updated: Counter[int] = Counter()
        for a, wa in distribution.items():
            for b, wb in local.items():
                updated[a + b] += wa * wb
        distribution = dict(updated)
    favorable = sum(ways for selected, ways in distribution.items() if selected <= observed)
    return total, swappable, mobile, favorable / total


worlds, swappable, mobile, strict_p = exact_count_p(host_values)
ok("strict_worlds", worlds == 3732480)
ok("strict_capacity", swappable == 42 and mobile == 14)
ok("strict_p", abs(strict_p - result["exact_group_count_null"]["inclusive_one_sided_p"]) < 1e-14 and abs(strict_p - 0.29583333333333334) < 1e-14)

published_inventory = read(LINE_INVENTORY)
ok("published_inventory_count", len(published_inventory) == 233)
ok("published_inventory_unique", len({row["locus"] for row in published_inventory}) == 233)
ok("published_inventory_no_f84", not any(row["page"].startswith("f84") for row in published_inventory))
published_tests = read(TESTS)
ok("test_rows", len(published_tests) == 8)
published_nulls = read(NULLS)
ok("null_rows", len(published_nulls) == 6)
strict_row = next(row for row in published_nulls if row["representation"] == "PAGE_HOST" and row["null"] == "PAGE_EXACT_GROUP_COUNT")
ok("published_strict_p", abs(float(strict_row["inclusive_one_sided_p"]) - strict_p) < 1e-12)
ok("counterexamples", len(read(COUNTEREXAMPLES)) == 6)

validation = {
    "schema": "GDT211_BALNEOLOGICAL_RECORD_SCHEMA_VALIDATION_V1",
    "status": "PASS",
    "checks_passed": len(checks),
    "checks": checks,
    "result_sha256": sha(RESULT),
    "result_content_sha256": stored_content,
    "validator_sha256": sha(Path(__file__)),
    "independent_reconstruction": {
        "primary_lines": len(primary),
        "paragraph_starts": sum(row["start"] for row in primary),
        "host_effect": host_effect,
        "raw_token_effect": token_effect,
        "strict_worlds": worlds,
        "strict_p": strict_p,
    },
    "f84r_accessed": False,
}
VALIDATION.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(json.dumps({"status": "PASS", "checks": len(checks), "host_effect": host_effect, "strict_p": strict_p}, sort_keys=True))
