#!/usr/bin/env python3
"""Independent source reconstruction of the GDT175 control calibration."""
from __future__ import annotations

import csv
import gzip
import hashlib
import itertools
import json
import math
import random
from collections import Counter, defaultdict
from pathlib import Path

R = Path(__file__).resolve().parent
DESIGN = R / "gdt175_design.json"
P172 = R / "gdt172_blind_parses.json.gz"
P173 = R / "gdt173_blind_parses.json.gz"
HOSTS = R / "gdt175_control_host_metrics.tsv"
BINS = R / "gdt175_control_bin_summary.tsv"
SCOPES = R / "gdt175_control_scope_summary.tsv"
RESULT = R / "gdt175_control_result.json"
RUNNER = R / "run_gdt175_control_partner_instability.py"
OUT = R / "gdt175_control_validation.json"
SYSTEMS = {"CONTROL_P": "LEXICAL_A", "CONTROL_R": "HUMAN_GROWN_B2", "CONTROL_Q": "FACTORIAL_B"}
ALPHA, BETA, WORLDS = 16.0, 8.0, 256


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def csha(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()


def read(path: Path) -> list[dict]:
    with path.open(encoding="utf8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def check(value, label: str, checks: list[str]) -> None:
    if not value:
        raise AssertionError(label)
    checks.append(label)


def close(a, b, tolerance=1e-9) -> bool:
    return abs(float(a) - float(b)) <= tolerance * max(1.0, abs(float(a)), abs(float(b)))


def load() -> dict[str, list[dict]]:
    out = {value: [] for value in SYSTEMS.values()}
    for path in (P172, P173):
        with gzip.open(path, "rt", encoding="utf8") as handle:
            rows = json.load(handle)["rows"]
        for row in rows:
            if row["parser_level"] == "SURFACE_ONLY" and row["world_view"] in SYSTEMS:
                out[SYSTEMS[row["world_view"]]].append(row)
    return out


def events(rows: list[dict]) -> list[dict]:
    lines = defaultdict(list)
    for row in rows:
        lines[str(row["physical_line_id"])].append(row)
    out = []
    for line in lines.values():
        line.sort(key=lambda row: int(row["group_index"]))
        for left, right in zip(line, line[1:]):
            assert int(right["group_index"]) == int(left["group_index"]) + 1
            out.append({"folio": str(left["folio_id"]), "register": str(left["register"]), "host": str(left["inferred_host"]), "target": str(right["inferred_host"]), "nk": (int(left["group_index"]), int(left["line_ordinal_on_folio"]) % 3, int(left["group_count"]))})
    return out


def entropy(counts: Counter) -> float:
    total = sum(counts.values())
    return -sum(n / total * math.log2(n / total) for n in counts.values() if n) if total else 0.0


def pair_values(by_folio: dict[str, Counter]) -> tuple[float, float]:
    support = sorted(set().union(*(set(counter) for counter in by_folio.values())))
    values = []
    for left, right in itertools.combinations(sorted(by_folio), 2):
        a, b = by_folio[left], by_folio[right]
        overlap = len(set(a) & set(b)) / len(set(a) | set(b))
        da, db = sum(a.values()) + 0.5 * len(support), sum(b.values()) + 0.5 * len(support)
        divergence = 0.0
        for target in support:
            pa, pb = (a.get(target, 0) + 0.5) / da, (b.get(target, 0) + 0.5) / db
            middle = (pa + pb) / 2
            divergence += 0.5 * pa * math.log2(pa / middle) + 0.5 * pb * math.log2(pb / middle)
        values.append((overlap, divergence))
    return sum(x for x, _ in values) / len(values), sum(x for _, x in values) / len(values)


def held(values: list[dict]) -> Counter:
    vocab = {x["target"] for x in values}
    gt, gn, nt, nn, ht, hn = Counter(), 0, Counter(), Counter(), Counter(), Counter()
    ft, fn = defaultdict(Counter), Counter()
    fnt, fnn, fht, fhn = defaultdict(Counter), defaultdict(Counter), defaultdict(Counter), defaultdict(Counter)
    for x in values:
        t, nk, h, f = x["target"], x["nk"], x["host"], x["folio"]
        gt[t] += 1; gn += 1; nt[nk, t] += 1; nn[nk] += 1; ht[h, t] += 1; hn[h] += 1
        ft[f][t] += 1; fn[f] += 1; fnt[f][nk, t] += 1; fnn[f][nk] += 1; fht[f][h, t] += 1; fhn[f][h] += 1
    gains = Counter()
    for x in values:
        t, nk, h, f = x["target"], x["nk"], x["host"], x["folio"]
        q = (gt[t] - ft[f][t] + 0.5) / (gn - fn[f] + 0.5 * len(vocab))
        base = (nt[nk, t] - fnt[f][nk, t] + ALPHA * q) / (nn[nk] - fnn[f][nk] + ALPHA)
        hp = (ht[h, t] - fht[f][h, t] + BETA * base) / (hn[h] - fhn[f][h] + BETA)
        gains[h] += math.log2(hp / base)
    return gains


def null_values(system: str, scope: str, host: str, by_folio: dict[str, Counter], observed_overlap: float, observed_jsd: float) -> tuple[float, float, float, float]:
    folios = sorted(by_folio); sizes = [sum(by_folio[x].values()) for x in folios]
    partners = []
    for folio in folios:
        partners.extend(by_folio[folio].elements())
    value = int(hashlib.sha256("|".join(("GDT175", system, scope, host)).encode()).hexdigest()[:16], 16)
    rng, overlaps, divergences = random.Random(value), [], []
    for _ in range(WORLDS):
        sample = list(partners); rng.shuffle(sample); cursor = 0; rebuilt = {}
        for folio, size in zip(folios, sizes):
            rebuilt[folio] = Counter(sample[cursor:cursor + size]); cursor += size
        overlap, divergence = pair_values(rebuilt); overlaps.append(overlap); divergences.append(divergence)
    return sum(overlaps) / WORLDS, sum(divergences) / WORLDS, (1 + sum(x <= observed_overlap + 1e-15 for x in overlaps)) / 257, (1 + sum(x >= observed_jsd - 1e-15 for x in divergences)) / 257


def main() -> None:
    checks: list[str] = []
    design, result = json.loads(DESIGN.read_text()), json.loads(RESULT.read_text())
    host_rows, bin_rows, scope_rows = read(HOSTS), read(BINS), read(SCOPES)
    check(design["status"] == "DIAGNOSTIC_FROZEN_BEFORE_CONTROL_CALIBRATION", "design_status", checks)
    check(result["status"] == "CONTROL_CALIBRATION_FROZEN_BEFORE_VOYNICH_SCORING", "result_status", checks)
    check(result["firewall"] == {"build_b3": False, "f84r_access": False, "oracle_fields": 0, "systems_read": ["LEXICAL_A", "HUMAN_GROWN_B2", "FACTORIAL_B"], "voynich_inputs": 0}, "firewall", checks)
    controls = load()
    check(all(len(rows) == 15214 for rows in controls.values()), "source_group_counts", checks)
    check(all(all(str(row["folio_id"]).startswith("CONTROL_") for row in rows) for rows in controls.values()), "synthetic_folios_only", checks)
    exported = {(row["system"], row["scope_type"], row["scope_value"], row["host"]): row for row in host_rows}
    reconstructed_scope = {}
    audit_null = []
    for system, rows in controls.items():
        all_events = events(rows)
        check(len(all_events) == 12805 and len({row["folio_id"] for row in rows}) == 176, "event_and_folio_counts", checks)
        scopes = [("GLOBAL", "ALL", rows, all_events)]
        for register in sorted({row["register"] for row in rows}):
            scopes.append(("REGISTER", str(register), [row for row in rows if row["register"] == register], [event for event in all_events if event["register"] == register]))
        for scope_type, scope_value, subrows, subevents in scopes:
            grouped = defaultdict(list)
            for event in subevents: grouped[event["host"]].append(event)
            eligible = {host for host, values in grouped.items() if len(values) >= 2 and len({x["folio"] for x in values}) >= 2}
            gain = held(subevents)
            reconstructed_scope[system, scope_type, scope_value] = (len(subrows), len(subevents), len(eligible), sum(len(grouped[h]) for h in eligible))
            for host in eligible:
                key = (system, scope_type, scope_value, host); check(key in exported, "host_key_coverage", checks); row = exported[key]
                values = grouped[host]; by_folio = defaultdict(Counter); pooled = Counter()
                for x in values: by_folio[x["folio"]][x["target"]] += 1; pooled[x["target"]] += 1
                overlap, divergence = pair_values(by_folio)
                check(int(row["next_events"]) == len(values) and int(row["physical_folios"]) == len(by_folio) and int(row["partner_types"]) == len(pooled), "host_counts", checks)
                check(close(row["held_gain_bits"], gain[host]) and close(row["partner_set_overlap"], overlap) and close(row["pairwise_jsd_bits"], divergence), "host_primary_metrics", checks)
                check(close(row["pooled_target_entropy_bits"], entropy(pooled)) and close(row["mean_within_folio_entropy_bits"], sum(entropy(x) for x in by_folio.values()) / len(by_folio)), "host_entropy", checks)
            # Independently replay one host per nonempty occurrence bin in every global control.
            if scope_type == "GLOBAL":
                for bin_name in ("N2_4", "N5_15", "N16_63", "N64_PLUS"):
                    candidates = [h for h in eligible if exported[system, scope_type, scope_value, h]["occurrence_bin"] == bin_name]
                    # Replay the least frequent eligible host in each bin. This
                    # still checks every frozen bin/seed path without making an
                    # independent validator quadratic in a maximum-degree host.
                    if candidates:
                        chosen = min(candidates, key=lambda h: (len(grouped[h]), h))
                        audit_null.append((system, scope_type, scope_value, chosen, grouped[chosen]))
    check(len(exported) == len(host_rows), "host_keys_unique", checks)
    for row in scope_rows:
        if row["scope_type"] == "SECTION":
            check(row["scope_value"] == "UNAVAILABLE" and row["powered"] == "0", "section_unavailable", checks); continue
        key = (row["system"], row["scope_type"], row["scope_value"]); expected = reconstructed_scope[key]
        check(tuple(map(int, (row["total_groups"], row["total_next_events"], row["eligible_hosts"], row["eligible_next_events"]))) == expected, "scope_counts", checks)
    for system, scope_type, scope_value, host, values in audit_null:
        row = exported[system, scope_type, scope_value, host]; by_folio = defaultdict(Counter)
        for x in values: by_folio[x["folio"]][x["target"]] += 1
        no, nj, po, pj = null_values(system, f"{scope_type}:{scope_value}", host, by_folio, float(row["partner_set_overlap"]), float(row["pairwise_jsd_bits"]))
        check(close(row["null_overlap_mean"], no) and close(row["null_jsd_mean"], nj) and close(row["overlap_lower_p"], po) and close(row["jsd_upper_p"], pj), "sampled_null_replay", checks)
    # Summary arithmetic is checked from exported per-host rows, independently of the producer.
    for summary in bin_rows + [row for row in scope_rows if row["scope_type"] != "SECTION"]:
        selected = [row for row in host_rows if row["system"] == summary["system"] and row["scope_type"] == summary["scope_type"] and row["scope_value"] == summary["scope_value"] and (summary["occurrence_bin"] == "ALL_ELIGIBLE" or row["occurrence_bin"] == summary["occurrence_bin"])]
        count = sum(int(row["next_events"]) for row in selected); gain = sum(float(row["held_gain_bits"]) for row in selected)
        check(int(summary["eligible_hosts"]) == len(selected) and int(summary["eligible_next_events"]) == count and close(summary["held_gain_bits"], gain), "summary_arithmetic", checks)
        if selected:
            check(close(summary["mean_overlap_excess"], sum(float(row["overlap_excess"]) for row in selected) / len(selected)) and close(summary["mean_jsd_excess"], sum(float(row["jsd_excess"]) for row in selected) / len(selected)), "summary_equal_host_weighting", checks)
    checks = list(dict.fromkeys(checks))
    check(all(sha(R / name) == value for name, value in result["inputs"].items()), "input_hashes", checks)
    check(all(sha(R / name) == value for name, value in result["outputs"].items()), "output_hashes", checks)
    check(sha(RUNNER) == result["implementation"][RUNNER.name], "implementation_hash", checks)
    stored = result.pop("result_content_sha256"); check(csha(result) == stored, "result_content_hash", checks)
    out = {"schema": "GDT175_CONTROL_PARTNER_INSTABILITY_VALIDATION_V1", "status": "PASS_INDEPENDENT_CONTROL_SOURCE_RECONSTRUCTION", "checks_passed": len(checks), "checks_failed": 0, "checks": checks, "host_metric_rows": len(host_rows), "bin_summary_rows": len(bin_rows), "scope_summary_rows": len(scope_rows), "sampled_null_hosts_replayed": len(audit_null), "result_sha256": sha(RESULT), "validator_sha256": sha(Path(__file__)), "voynich_inputs": 0, "build_b3": False, "f84r_access": False}
    out["validation_content_sha256"] = csha(out)
    OUT.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(f"PASS {len(checks)}/{len(checks)}")


if __name__ == "__main__":
    main()
