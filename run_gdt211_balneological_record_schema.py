#!/usr/bin/env python3
"""Score the frozen De balneis record-schema predictions on q13."""
from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

R = Path(__file__).resolve().parent
FRAMES = R / "gdt046_line_frames.tsv"
HPR2 = R / "gdt062_right_family_inventory.tsv"
FREEZE = R / "gdt211_source_freeze.json"
METHOD = R / "GDT211_BALNEOLOGICAL_RECORD_SCHEMA_METHOD.md"
SOURCE_AUDIT = R / "GDT211_BALNEOLOGICAL_RECORD_SCHEMA_SOURCE_AUDIT.md"
INVENTORY = R / "gdt211_q13_line_inventory.tsv"
TESTS = R / "gdt211_record_schema_tests.tsv"
NULLS = R / "gdt211_null_results.tsv"
COUNTER = R / "gdt211_counterexamples.tsv"
REPORT = R / "GDT211_BALNEOLOGICAL_RECORD_SCHEMA_REPORT.md"
RESULT = R / "gdt211_result.json"
Q13_PREFIXES = {f"f{i}" for i in range(75, 84)}
GUARD_COUNTS: Counter[str] = Counter()


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def csha(value: dict) -> str:
    raw = json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()


def guarded_read(path: Path) -> list[dict[str, str]]:
    """Reject every f84 page before retaining a row's formal fields."""
    kept: list[dict[str, str]] = []
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle, delimiter="\t")
        header = next(reader)
        page_i = header.index("page")
        for values in reader:
            page = values[page_i]
            if page.startswith("f84"):
                GUARD_COUNTS[page] += 1
                continue
            row = dict(zip(header, values))
            assert not row["page"].startswith("f84")
            kept.append(row)
    return kept


def write(path: Path, rows: list[dict], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def length_bucket(n: int) -> str:
    if n <= 4:
        return "1-4"
    if n <= 7:
        return "5-7"
    if n <= 10:
        return "8-10"
    return "11+"


def scope_rows(lines: list[dict], scope: str) -> list[dict]:
    if scope == "Q13_B_PRIMARY":
        return [x for x in lines if x["is_q13"] and x["section"] == "B"]
    if scope == "Q13_ALL_SENSITIVITY":
        return [x for x in lines if x["is_q13"]]
    if scope == "HERBAL_B_HAND2_CONTROL":
        return [x for x in lines if x["section"] == "H" and x["currier"] == "B" and x["hand"] == "2"]
    if scope == "TC_B_HAND2_CONTROL":
        return [x for x in lines if x["section"] in {"T", "C"} and x["currier"] == "B" and x["hand"] == "2"]
    raise AssertionError(scope)


def stats(rows: list[dict], field: str) -> dict:
    folios: dict[str, set[str]] = defaultdict(set)
    counts = Counter(row[field] for row in rows)
    for row in rows:
        folios[row[field]].add(row["physical_folio"])
    start = [row for row in rows if row["paragraph_start"] == 1]
    body = [row for row in rows if row["paragraph_start"] == 0]
    assert start and body
    recurring = lambda row: int(len(folios[row[field]]) >= 2)
    srate = sum(recurring(row) for row in start) / len(start)
    brate = sum(recurring(row) for row in body) / len(body)
    sfreq = sum(math.log2(counts[row[field]]) for row in start) / len(start)
    bfreq = sum(math.log2(counts[row[field]]) for row in body) / len(body)
    return {
        "lines": len(rows),
        "paragraph_starts": len(start),
        "physical_folios": len({row["physical_folio"] for row in rows}),
        "start_recurrent": sum(recurring(row) for row in start),
        "start_recurrent_fraction": srate,
        "continuation_recurrent": sum(recurring(row) for row in body),
        "continuation_recurrent_fraction": brate,
        "continuation_minus_start_recurrence": brate - srate,
        "start_mean_log2_frequency": sfreq,
        "continuation_mean_log2_frequency": bfreq,
        "continuation_minus_start_log2_frequency": bfreq - sfreq,
        "recurrence_values": [recurring(row) for row in rows],
    }


def exact_null(rows: list[dict], values: list[int], mode: str) -> dict:
    strata: dict[tuple, list[int]] = defaultdict(list)
    for i, row in enumerate(rows):
        key = [row["page"]]
        if mode == "PAGE_LENGTH_BUCKET":
            key.append(length_bucket(row["group_count"]))
        elif mode == "PAGE_EXACT_GROUP_COUNT":
            key.append(row["group_count"])
        elif mode != "PAGE_ONLY":
            raise AssertionError(mode)
        strata[tuple(key)].append(i)
    observed = sum(values[i] for i, row in enumerate(rows) if row["paragraph_start"])
    distribution = {0: 1}
    total_worlds = 1
    swappable = 0
    mobile_strata = 0
    for indices in strata.values():
        n = len(indices)
        k = sum(rows[i]["paragraph_start"] for i in indices)
        successes = sum(values[i] for i in indices)
        total_worlds *= math.comb(n, k)
        if 0 < k < n:
            swappable += n
            mobile_strata += 1
        local = {
            selected: math.comb(successes, selected) * math.comb(n - successes, k - selected)
            for selected in range(max(0, k - (n - successes)), min(k, successes) + 1)
        }
        updated: Counter[int] = Counter()
        for left, left_ways in distribution.items():
            for right, right_ways in local.items():
                updated[left + right] += left_ways * right_ways
        distribution = dict(updated)
    favorable = sum(ways for selected, ways in distribution.items() if selected <= observed)
    return {
        "null": mode,
        "total_worlds": total_worlds,
        "swappable_lines": swappable,
        "mobile_strata": mobile_strata,
        "observed_start_recurrent": observed,
        "inclusive_one_sided_p": favorable / total_worlds,
    }


freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
assert freeze["status"] == "EXTERNAL_BALNEOLOGICAL_RECORD_SCHEMA_FROZEN_BEFORE_Q13_SCORE"
assert freeze["semantic_mapping"] == "NONE"

frames = {row["locus"]: row for row in guarded_read(FRAMES)}
groups: dict[str, list[dict]] = defaultdict(list)
for row in guarded_read(HPR2):
    if row["locus"] in frames:
        groups[row["locus"]].append(row)
assert not any(page.startswith("f84r") for page in GUARD_COUNTS)

lines: list[dict] = []
for locus, frame in frames.items():
    if locus not in groups:
        continue
    gs = sorted(groups[locus], key=lambda row: int(row["group_index"]))
    assert [int(row["group_index"]) for row in gs] == list(range(1, len(gs) + 1))
    first = gs[0]
    assert first["page"] == frame["page"] and first["physical_folio"] == frame["physical_folio"]
    lines.append({
        "locus": locus,
        "page": frame["page"],
        "physical_folio": frame["physical_folio"],
        "section": first["section"],
        "currier": first["currier"],
        "hand": first["hand"],
        "paragraph_start": int(frame["paragraph_start"]),
        "group_count": int(frame["group_count"]),
        "first_token": first["token"],
        "first_page_host": first["page_host"],
        "is_q13": first["page"][:3] in Q13_PREFIXES,
        "semantic_role": "UNASSIGNED",
    })
assert all(not row["page"].startswith("f84") for row in lines)

primary = scope_rows(lines, "Q13_B_PRIMARY")
assert len(primary) == 233 and sum(row["paragraph_start"] for row in primary) == 17
host_primary = stats(primary, "first_page_host")
token_primary = stats(primary, "first_token")

host_folios: dict[str, set[str]] = defaultdict(set)
token_folios: dict[str, set[str]] = defaultdict(set)
for row in primary:
    host_folios[row["first_page_host"]].add(row["physical_folio"])
    token_folios[row["first_token"]].add(row["physical_folio"])
inventory_rows = []
for row in sorted(primary, key=lambda x: (int(x["page"][1:-1]), x["page"][-1], int(x["locus"].split(".")[1]))):
    inventory_rows.append({
        **{key: row[key] for key in ("locus", "page", "physical_folio", "section", "currier", "hand", "paragraph_start", "group_count", "first_token", "first_page_host")},
        "first_token_cross_folio_recurrent": int(len(token_folios[row["first_token"]]) >= 2),
        "first_page_host_cross_folio_recurrent": int(len(host_folios[row["first_page_host"]]) >= 2),
        "semantic_role": "UNASSIGNED",
    })
write(INVENTORY, inventory_rows, list(inventory_rows[0]))

test_rows = []
scope_stats: dict[str, dict[str, dict]] = {}
for scope in ("Q13_B_PRIMARY", "Q13_ALL_SENSITIVITY", "HERBAL_B_HAND2_CONTROL", "TC_B_HAND2_CONTROL"):
    z = scope_rows(lines, scope)
    scope_stats[scope] = {}
    for representation, field in (("PAGE_HOST", "first_page_host"), ("RAW_TOKEN", "first_token")):
        score = stats(z, field)
        scope_stats[scope][representation] = {k: v for k, v in score.items() if k != "recurrence_values"}
        test_rows.append({
            "scope": scope,
            "representation": representation,
            **{key: score[key] for key in score if key != "recurrence_values"},
            "semantic_role": "UNASSIGNED",
        })
write(TESTS, [{k: f"{v:.12g}" if isinstance(v, float) else v for k, v in row.items()} for row in test_rows], list(test_rows[0]))

null_rows = []
for representation, score in (("PAGE_HOST", host_primary), ("RAW_TOKEN", token_primary)):
    for mode in ("PAGE_ONLY", "PAGE_LENGTH_BUCKET", "PAGE_EXACT_GROUP_COUNT"):
        null_rows.append({
            "scope": "Q13_B_PRIMARY",
            "representation": representation,
            **exact_null(primary, score["recurrence_values"], mode),
        })
write(NULLS, [{k: f"{v:.12g}" if isinstance(v, float) else v for k, v in row.items()} for row in null_rows], list(null_rows[0]))

strict = next(row for row in null_rows if row["representation"] == "PAGE_HOST" and row["null"] == "PAGE_EXACT_GROUP_COUNT")
herbal = scope_stats["HERBAL_B_HAND2_CONTROL"]["PAGE_HOST"]
specificity_margin = host_primary["continuation_minus_start_recurrence"] - herbal["continuation_minus_start_recurrence"]
if host_primary["continuation_minus_start_recurrence"] > 0 and strict["inclusive_one_sided_p"] <= 0.05 and specificity_margin >= 0.10:
    status = "BALNEOLOGICAL_RECORD_SCHEMA_SPECIFIC_LEAD"
elif host_primary["continuation_minus_start_recurrence"] > 0:
    status = "BALNEOLOGICAL_RECORD_SCHEMA_COMPATIBLE_BUT_GENERIC_LINE_OPENING_CONFOUND"
else:
    status = "BALNEOLOGICAL_RECORD_SCHEMA_NOT_SUPPORTED"

counter_rows = [
    {"counterexample": "GENERIC_PAGE_HOST_OPENING_EFFECT", "evidence": f"q13 effect {host_primary['continuation_minus_start_recurrence']:+.6f}; Herbal-B/hand-2 effect {herbal['continuation_minus_start_recurrence']:+.6f}; specificity margin {specificity_margin:+.6f}", "impact": "The PAGE_HOST result is nearly identical in the same-hand Herbal control and is not bath-specific."},
    {"counterexample": "EXACT_LENGTH_MATCHED_NULL", "evidence": f"p={strict['inclusive_one_sided_p']:.6f}; {strict['swappable_lines']} swappable lines in {strict['mobile_strata']} strata", "impact": "The nominal page-only lead does not survive exact line group-count control."},
    {"counterexample": "RECURRENT_OPENERS", "evidence": f"{host_primary['start_recurrent']}/{host_primary['paragraph_starts']} opening PAGE_HOSTs recur on another q13 folio", "impact": "Paragraph starts are not a unique identifier dictionary."},
    {"counterexample": "EDITORIAL_BOUNDARY", "evidence": "paragraph_start comes from the frozen source layout layer", "impact": "It is not an authorially translated heading marker."},
    {"counterexample": "NO_FIXED_SOURCE_ORDER", "evidence": "The readable bath entries vary role order and omit optional roles.", "impact": "No one-to-one HPR2 field-slot map is licensed."},
    {"counterexample": "ILLUSTRATION_LABEL_MISMATCH", "evidence": "q13 contains many local figure/apparatus labels, while the readable comparator schema is entry-level.", "impact": "The comparator does not explain q13 local-label ownership or vocabulary."},
]
write(COUNTER, counter_rows, list(counter_rows[0]))

REPORT.write_text(f"""# GDT211 — balneological record-schema bridge

## Outcome

**{status}**

The externally frozen *De balneis* schema makes one useful anonymous
prediction: a record-opening identity/site field should recur across folios less
often than shared body material.  q13 points in that direction, but the effect
is not specifically balneological and does not survive the strict length
control.

## External schema

The source audit retained 32 bath records and excluded the numbered dedication.
All 32 bath records contain identity and indication material; 17 contain
location/access, 23 hydraulic/physical description, 20 procedure/caution and 6
outcome/testimony.  This supports a variable information package, not a rigid
slot sequence.

## q13 result

The primary section-B inventory contains {host_primary['lines']} physical lines
on {host_primary['physical_folios']} folios, including
{host_primary['paragraph_starts']} editorial paragraph starts.

- PAGE_HOST recurrence: {host_primary['start_recurrent']}/{host_primary['paragraph_starts']}
  ({host_primary['start_recurrent_fraction']:.3f}) at starts versus
  {host_primary['continuation_recurrent']}/{host_primary['lines']-host_primary['paragraph_starts']}
  ({host_primary['continuation_recurrent_fraction']:.3f}) elsewhere; effect
  {host_primary['continuation_minus_start_recurrence']:+.3f}.
- Complete first-token recurrence: {token_primary['start_recurrent']}/{token_primary['paragraph_starts']}
  ({token_primary['start_recurrent_fraction']:.3f}) versus
  {token_primary['continuation_recurrent']}/{token_primary['lines']-token_primary['paragraph_starts']}
  ({token_primary['continuation_recurrent_fraction']:.3f}); effect
  {token_primary['continuation_minus_start_recurrence']:+.3f}.
- The mean PAGE_HOST frequency contrast is
  {host_primary['continuation_minus_start_log2_frequency']:+.3f} log2 units.

The exact page-only PAGE_HOST recurrence null is
{next(x for x in null_rows if x['representation']=='PAGE_HOST' and x['null']=='PAGE_ONLY')['inclusive_one_sided_p']:.4f},
but page plus length bucket is
{next(x for x in null_rows if x['representation']=='PAGE_HOST' and x['null']=='PAGE_LENGTH_BUCKET')['inclusive_one_sided_p']:.4f}
and page plus exact group count is {strict['inclusive_one_sided_p']:.4f}.
Only {strict['swappable_lines']} lines remain swappable in the exact-count null.

## Specificity failure

The Herbal-B/hand-2 PAGE_HOST effect is {herbal['continuation_minus_start_recurrence']:+.3f},
almost identical to q13; the q13-minus-Herbal margin is only
{specificity_margin:+.3f}.  The most economical explanation is therefore a
generic line/paragraph-opening architecture combined with line-length and
frequency effects—not a recovered bath-identity slot.

## What this changes

The readable bath tradition remains a strong page-genre comparator from
GDT210, and GDT211 supplies a plausible *kind* of record package.  It does not
localize identity or therapeutic content inside Voynichese.  The next useful
step is an independently owned repeated referent or a readable homolog, not a
post-hoc gloss on the rare opening hosts.

## Claim ceiling

No PAGE_HOST is assigned a bath, place, disease, body part, procedure, word,
morpheme, sound, language, plaintext, or translation.  The result tests only
anonymous record-schema compatibility.  No f84 page was retained or scored;
f84r was not accessed.
""", encoding="utf-8")

result = {
    "schema": "GDT211_BALNEOLOGICAL_RECORD_SCHEMA_RESULT_V1",
    "status": status,
    "chronology": {"external_source_freeze_commit": "4d62597", "target_scored_after_freeze": True, "target_corpus_historically_exposed": True},
    "external_schema": {"bath_records": freeze["eligible_bath_records"], "role_counts": freeze["role_counts"]},
    "primary_scope": "Q13_B_PRIMARY",
    "primary_page_host": scope_stats["Q13_B_PRIMARY"]["PAGE_HOST"],
    "primary_raw_token": scope_stats["Q13_B_PRIMARY"]["RAW_TOKEN"],
    "exact_group_count_null": {k: v for k, v in strict.items() if k not in {"scope", "representation"}},
    "herbal_b_hand2_page_host_control": herbal,
    "specificity_margin": specificity_margin,
    "semantic_mapping": "NONE",
    "interpretation": "The bath-entry schema is compatible with q13 opening rarity, but the lead is generic to same-hand paragraph architecture and length-sensitive.",
    "claim_ceiling": "Anonymous record-schema compatibility only; no bath, site, condition, body part, procedure, word, morpheme, sound, language, plaintext, or translation.",
    "f84": {"all_f84_rows_rejected_before_formal_retention": True, "f84v_page_metadata_seen_only_by_guard": True, "f84v_source_rows_rejected": sum(GUARD_COUNTS.values()), "f84v_formal_fields_retained": False, "f84r_present_in_source": False, "f84r_accessed": False, "joined": False, "scored": False},
    "inputs": {path.name: sha(path) for path in (FRAMES, HPR2, FREEZE)},
    "implementation": {Path(__file__).name: sha(Path(__file__))},
    "outputs": {path.name: sha(path) for path in (INVENTORY, TESTS, NULLS, COUNTER)},
    "documents": {path.name: sha(path) for path in (METHOD, SOURCE_AUDIT, REPORT)},
}
result["result_content_sha256"] = csha(result)
RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(json.dumps({"status": status, "page_host_effect": host_primary["continuation_minus_start_recurrence"], "strict_p": strict["inclusive_one_sided_p"], "specificity_margin": specificity_margin}, sort_keys=True))
