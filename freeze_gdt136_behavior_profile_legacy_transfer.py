#!/usr/bin/env python3
"""Score-blind capacity audit and freeze for GDT136."""
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
METHOD = ROOT / "GDT136_BEHAVIOR_PROFILE_LEGACY_TRANSFER_METHOD.md"
TARGETS = ROOT / "gdt109_target_inventory.tsv"
SOURCE = ROOT / "gdt062_right_family_inventory.tsv"
PROSE = ROOT / "gdt016_group_state_inventory.tsv"
MANIFEST = ROOT / "gdt095_descriptor_token_manifest.tsv"
CAPACITY = ROOT / "gdt136_capacity.tsv"
PREDICTION = ROOT / "gdt136_prediction.json"

PREFIXES = ("che", "ch", "sh", "t", "s", "d", "q")
RIGHT = ("aiin", "air", "ain", "ar", "al")
EDITIONS = (("ZL3b", "zl3b_forms"), ("IT2a", "it2a_forms"), ("RF1b", "rf1b_forms"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def csha(value: object) -> str:
    data = json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
    return hashlib.sha256(data.encode()).hexdigest()


def rows(path: Path):
    with path.open(encoding="utf-8", newline="") as handle:
        yield from csv.DictReader(handle, delimiter="\t")


def strip_layers(token: str) -> tuple[str, str]:
    wrapper, host = "NONE", token
    for prefix in PREFIXES:
        if host.startswith(prefix) and len(host) > len(prefix):
            wrapper, host = prefix, host[len(prefix):]
            break
    if host.endswith("dy") and len(host) > 2:
        host = host[:-2]
    return wrapper, host


def preparse(wrapper: str, host: str) -> str:
    if host.endswith("m") and len(host) > 1:
        host = host[:-1]
    for suffix in RIGHT:
        if host.endswith(suffix) and len(host) > len(suffix):
            host = host[:-len(suffix)]
            break
    if wrapper in {"ch", "che", "sh"} and host.startswith("d") and len(host) > 1:
        host = host[1:]
    return host


counts = Counter()
for row in rows(PROSE):
    if row["page"].startswith("f84"):
        continue
    counts[preparse(row["stripped_prefix"], row["residual_host"])] += 1
licensed = {host for host in counts if counts[host] and counts["o" + host] and counts["ot" + host]}
licensed |= {"ar", "al", "ol"}


def page_host(token: str) -> str:
    wrapper, host = strip_layers(token)
    host = preparse(wrapper, host)
    if host.startswith("ot") and host[2:] in licensed:
        host = host[2:]
    elif host.startswith("o") and host[1:] in licensed:
        host = host[1:]
    return host or "EMPTY"


host_folios: dict[str, set[str]] = defaultdict(set)
source_rows = 0
for row in rows(SOURCE):
    if row["page"].startswith("f84"):
        continue
    source_rows += 1
    host_folios[row["page_host"]].add(row["physical_folio"])

capacity_rows = []
for row in rows(TARGETS):
    assert not row["page"].startswith("f84")
    flags_1, flags_2 = [], []
    group_counts = []
    for edition, column in EDITIONS:
        hosts = [page_host(token) for token in row[column].split("|")]
        outside = [len(host_folios[host] - {row["physical_folio"]}) for host in hosts]
        flags_1.append(all(value >= 1 for value in outside))
        flags_2.append(all(value >= 2 for value in outside))
        group_counts.append(len(hosts))
    capacity_rows.append({
        "locus": row["locus"],
        "physical_folio": row["physical_folio"],
        "zl_profileable_ge1": int(flags_1[0]),
        "it_profileable_ge1": int(flags_1[1]),
        "rf_profileable_ge1": int(flags_1[2]),
        "profileable_editions_ge1": sum(flags_1),
        "primary_eligible_any_reading": int(any(flags_1)),
        "all_readings_eligible_ge1": int(all(flags_1)),
        "profileable_editions_ge2": sum(flags_2),
        "sensitivity_eligible_any_reading_ge2": int(any(flags_2)),
        "group_counts_zl_it_rf": ";".join(map(str, group_counts)),
        "descriptor_outcome_retained_or_scored": 0,
    })

fields = list(capacity_rows[0])
with CAPACITY.open("w", encoding="utf-8", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
    writer.writeheader(); writer.writerows(capacity_rows)

primary = [row for row in capacity_rows if row["primary_eligible_any_reading"]]
stronger = [row for row in capacity_rows if row["sensitivity_eligible_any_reading_ge2"]]
all_three = [row for row in capacity_rows if row["all_readings_eligible_ge1"]]
assert (len(primary), len({row["physical_folio"] for row in primary})) == (31, 6)
assert (len(stronger), len({row["physical_folio"] for row in stronger})) == (27, 6)
assert (len(all_three), len({row["physical_folio"] for row in all_three})) == (15, 5)

prediction = {
    "schema": "GDT136_BEHAVIOR_PROFILE_LEGACY_TRANSFER_PREDICTION_V1",
    "status": "FROZEN_POSTHOC_CROSS_PANEL_BEFORE_DESCRIPTOR_SCORING",
    "chronology": "Public GDT068 behavior model crossed with public GDT109 target; capacity fixed before new behavior-to-descriptor predictions were computed.",
    "capacity": {
        "source_rows_after_all_f84_exclusion": source_rows,
        "target_loci": len(capacity_rows),
        "target_physical_folios": len({row["physical_folio"] for row in capacity_rows}),
        "primary_loci_any_profileable_reading": len(primary),
        "primary_physical_folios": len({row["physical_folio"] for row in primary}),
        "two_outside_folio_loci": len(stronger),
        "two_outside_folio_physical_folios": len({row["physical_folio"] for row in stronger}),
        "all_readings_profileable_loci": len(all_three),
        "all_readings_profileable_physical_folios": len({row["physical_folio"] for row in all_three}),
    },
    "target": "FIXED_GDT109_44_LOCUS_19_DESCRIPTOR_TOKEN_PANEL",
    "primary_representation": "BEHAVIOR_SELF_NEIGHBOR_NOPOS",
    "comparators": ["PAGE_HOST_CHAR3", "RAW_CHAR3"],
    "eligibility": "AT_LEAST_ONE_COMPLETE_EDITION_RENDERING_WITH_EVERY_HOST_ON_AT_LEAST_ONE_NON_TARGET_FOLIO",
    "alternate_readings": "AVERAGE_PROFILEABLE_EDITIONS;NOT_REPLICATIONS",
    "k": 5,
    "shrink": 4.0,
    "worlds": 10000,
    "selector_models": 3,
    "gates": {
        "behavior_selector_paid_gain_positive": True,
        "behavior_beats_both_string_baselines": True,
        "behavior_positive_at_least_4_of_6_folios": True,
        "two_outside_folio_sensitivity_positive": True,
        "max_three_p_le_005": True,
    },
    "outcome_access": "ARCHIVE_ALREADY_PUBLIC_AND_EXPOSED;CAPACITY_AUDIT_DID_NOT_RETAIN_JOIN_OR_SCORE_DESCRIPTOR_TOKENS",
    "f84": {"all_f84_rows_rejected_before_retention": True, "new_f84r_access": False},
    "claim_ceiling": "Reusable source-formal behavior class only; no semantic class, role, gloss, word, morpheme, POS, sound, language, plaintext, meaning, or translation.",
    "inputs": {path.name: sha(path) for path in (METHOD, TARGETS, SOURCE, PROSE, MANIFEST, ROOT / "gdt068_result.json", ROOT / "gdt109_result.json")},
    "implementation": {Path(__file__).name: sha(Path(__file__))},
    "outputs": {CAPACITY.name: sha(CAPACITY)},
}
prediction["prediction_content_sha256"] = csha(prediction)
PREDICTION.write_text(json.dumps(prediction, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(json.dumps({"status": prediction["status"], **prediction["capacity"]}, sort_keys=True))
