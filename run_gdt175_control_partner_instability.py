#!/usr/bin/env python3
"""Calibrate the frozen GDT175 diagnostic on A, B2, and factorial B only."""
from __future__ import annotations

import csv
import gzip
import hashlib
import itertools
import json
import math
import random
import os
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

R = Path(__file__).resolve().parent
DESIGN = R / "gdt175_design.json"
METHOD = R / "GDT175_RECURRENCE_PARTNER_INSTABILITY_METHOD.md"
P172 = R / "gdt172_blind_parses.json.gz"
P173 = R / "gdt173_blind_parses.json.gz"
HOSTS = R / "gdt175_control_host_metrics.tsv"
BINS = R / "gdt175_control_bin_summary.tsv"
SCOPES = R / "gdt175_control_scope_summary.tsv"
REPORT = R / "GDT175_CONTROL_CALIBRATION_REPORT.md"
RESULT = R / "gdt175_control_result.json"

ALPHA = 16.0
BETA = 8.0
WORLDS = 256
SYSTEMS = {
    "CONTROL_P": "LEXICAL_A",
    "CONTROL_R": "HUMAN_GROWN_B2",
    "CONTROL_Q": "FACTORIAL_B",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def csha(value) -> str:
    raw = json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def write_tsv(path: Path, rows: list[dict]) -> None:
    fields: list[str] = []
    for row in rows:
        for field in row:
            if field not in fields:
                fields.append(field)
    with path.open("w", encoding="utf8", newline="") as handle:
        writer = csv.DictWriter(handle, fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows([{field: row.get(field, "NA") for field in fields} for row in rows])


def load_control_rows() -> dict[str, list[dict]]:
    out = {name: [] for name in SYSTEMS.values()}
    for path in (P172, P173):
        with gzip.open(path, "rt", encoding="utf8") as handle:
            payload = json.load(handle)
        for row in payload["rows"]:
            if row["parser_level"] != "SURFACE_ONLY" or row["world_view"] not in SYSTEMS:
                continue
            out[SYSTEMS[row["world_view"]]].append(row)
    assert all(len(rows) == 15214 for rows in out.values())
    # These are anonymous synthetic folios (`CONTROL_*`), not manuscript loci.
    assert all(all(str(row["folio_id"]).startswith("CONTROL_") for row in rows) for rows in out.values())
    return out


def make_events(rows: list[dict]) -> list[dict]:
    lines: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        lines[str(row["physical_line_id"])].append(row)
    events = []
    for line_id, line in lines.items():
        line.sort(key=lambda item: int(item["group_index"]))
        for source, target in zip(line, line[1:]):
            assert int(target["group_index"]) == int(source["group_index"]) + 1
            events.append({
                "line_id": line_id,
                "folio": str(source["folio_id"]),
                "register": str(source["register"]),
                "host": str(source["inferred_host"]),
                "target": str(target["inferred_host"]),
                "nuisance": (
                    int(source["group_index"]),
                    int(source["line_ordinal_on_folio"]) % 3,
                    int(source["group_count"]),
                ),
            })
    return events


def entropy(counts: Counter) -> float:
    total = sum(counts.values())
    return -sum((n / total) * math.log2(n / total) for n in counts.values() if n) if total else 0.0


def jaccard(a: Counter, b: Counter) -> float:
    left, right = set(a), set(b)
    return len(left & right) / len(left | right) if left or right else 0.0


def jsd(a: Counter, b: Counter, support: tuple[str, ...]) -> float:
    ka = sum(a.values()) + 0.5 * len(support)
    kb = sum(b.values()) + 0.5 * len(support)
    ans = 0.0
    for target in support:
        pa = (a.get(target, 0) + 0.5) / ka
        pb = (b.get(target, 0) + 0.5) / kb
        middle = (pa + pb) / 2.0
        ans += 0.5 * pa * math.log2(pa / middle) + 0.5 * pb * math.log2(pb / middle)
    return ans


def pair_metrics(by_folio: dict[str, Counter]) -> tuple[float, float]:
    support = tuple(sorted(set().union(*(set(values) for values in by_folio.values()))))
    matrix = np.zeros((len(by_folio), len(support)), dtype=np.int64)
    index = {target: i for i, target in enumerate(support)}
    for row_index, folio in enumerate(sorted(by_folio)):
        for target, count in by_folio[folio].items():
            matrix[row_index, index[target]] = count
    return pair_metrics_matrix(matrix)


def pair_metrics_matrix(matrix: np.ndarray) -> tuple[float, float]:
    rows = matrix.shape[0]
    left, right = np.triu_indices(rows, 1)
    binary = matrix > 0
    intersections = (binary.astype(np.int64) @ binary.astype(np.int64).T)[left, right]
    sizes = binary.sum(axis=1)
    unions = sizes[left] + sizes[right] - intersections
    overlap = float(np.mean(intersections / unions))
    probs = (matrix.astype(np.float64) + 0.5) / (matrix.sum(axis=1, keepdims=True) + 0.5 * matrix.shape[1])
    host_entropy = -np.sum(probs * np.log2(probs), axis=1)
    middle = (probs[left] + probs[right]) / 2.0
    middle_entropy = -np.sum(middle * np.log2(middle), axis=1)
    divergence = float(np.mean(middle_entropy - (host_entropy[left] + host_entropy[right]) / 2.0))
    return overlap, divergence


def seed(*parts: str) -> int:
    return int(hashlib.sha256("|".join(parts).encode()).hexdigest()[:16], 16)


def sampling_null(system: str, scope: str, host: str, by_folio: dict[str, Counter], observed_overlap: float, observed_jsd: float) -> dict:
    folios = sorted(by_folio)
    sizes = [sum(by_folio[folio].values()) for folio in folios]
    support = sorted(set().union(*(set(values) for values in by_folio.values())))
    index = {target: i for i, target in enumerate(support)}
    partners: list[int] = []
    for folio in folios:
        partners.extend(index[target] for target in by_folio[folio].elements())
    rng = random.Random(seed("GDT175", system, scope, host))
    overlaps, divergences = [], []
    for _ in range(WORLDS):
        shuffled = list(partners)
        rng.shuffle(shuffled)
        matrix = np.zeros((len(folios), len(support)), dtype=np.int64)
        cursor = 0
        for row_index, size in enumerate(sizes):
            matrix[row_index] = np.bincount(shuffled[cursor:cursor + size], minlength=len(support))
            cursor += size
        overlap, divergence = pair_metrics_matrix(matrix)
        overlaps.append(overlap)
        divergences.append(divergence)
    overlap_mean = sum(overlaps) / WORLDS
    jsd_mean = sum(divergences) / WORLDS
    return {
        "null_overlap_mean": overlap_mean,
        "overlap_excess": observed_overlap - overlap_mean,
        "overlap_lower_p": (1 + sum(value <= observed_overlap + 1e-15 for value in overlaps)) / (WORLDS + 1),
        "null_jsd_mean": jsd_mean,
        "jsd_excess": observed_jsd - jsd_mean,
        "jsd_upper_p": (1 + sum(value >= observed_jsd - 1e-15 for value in divergences)) / (WORLDS + 1),
    }


def sampling_null_job(args) -> tuple[str, dict]:
    system, scope, host, by_folio, overlap, divergence = args
    return host, sampling_null(system, scope, host, by_folio, overlap, divergence)


def occurrence_bin(count: int) -> str:
    if count <= 4:
        return "N2_4"
    if count <= 15:
        return "N5_15"
    if count <= 63:
        return "N16_63"
    return "N64_PLUS"


def held_host_gains(events: list[dict]) -> Counter:
    vocab = sorted({event["target"] for event in events})
    global_target, global_n = Counter(), 0
    nuisance_target, nuisance_n = Counter(), Counter()
    host_target, host_n = Counter(), Counter()
    fold_target, fold_n = defaultdict(Counter), Counter()
    fold_nuisance_target, fold_nuisance_n = defaultdict(Counter), defaultdict(Counter)
    fold_host_target, fold_host_n = defaultdict(Counter), defaultdict(Counter)
    for event in events:
        target, nk, host, fold = event["target"], event["nuisance"], event["host"], event["folio"]
        global_target[target] += 1; global_n += 1
        nuisance_target[nk, target] += 1; nuisance_n[nk] += 1
        host_target[host, target] += 1; host_n[host] += 1
        fold_target[fold][target] += 1; fold_n[fold] += 1
        fold_nuisance_target[fold][nk, target] += 1; fold_nuisance_n[fold][nk] += 1
        fold_host_target[fold][host, target] += 1; fold_host_n[fold][host] += 1
    gains = Counter()
    for event in events:
        target, nk, host, fold = event["target"], event["nuisance"], event["host"], event["folio"]
        q = (global_target[target] - fold_target[fold][target] + 0.5) / (global_n - fold_n[fold] + 0.5 * len(vocab))
        base = (nuisance_target[nk, target] - fold_nuisance_target[fold][nk, target] + ALPHA * q) / (nuisance_n[nk] - fold_nuisance_n[fold][nk] + ALPHA)
        hp = (host_target[host, target] - fold_host_target[fold][host, target] + BETA * base) / (host_n[host] - fold_host_n[fold][host] + BETA)
        gains[host] += math.log2(hp / base)
    return gains


def scope_metrics(system: str, scope_type: str, scope_value: str, rows: list[dict], events: list[dict], executor: ProcessPoolExecutor) -> tuple[list[dict], dict, list[dict]]:
    host_events: dict[str, list[dict]] = defaultdict(list)
    for event in events:
        host_events[event["host"]].append(event)
    eligible = {
        host for host, values in host_events.items()
        if len(values) >= 2 and len({value["folio"] for value in values}) >= 2
    }
    gains = held_host_gains(events)
    prepared = []
    for host in sorted(eligible):
        values = host_events[host]
        by_folio: dict[str, Counter] = defaultdict(Counter)
        pooled = Counter()
        for event in values:
            by_folio[event["folio"]][event["target"]] += 1
            pooled[event["target"]] += 1
        overlap, divergence = pair_metrics(by_folio)
        prepared.append((host, values, by_folio, pooled, overlap, divergence))
    jobs = [(system, f"{scope_type}:{scope_value}", host, by_folio, overlap, divergence) for host, values, by_folio, pooled, overlap, divergence in prepared]
    nulls = dict(executor.map(sampling_null_job, jobs, chunksize=8))
    host_rows = []
    for host, values, by_folio, pooled, overlap, divergence in prepared:
        row = {
            "system": system,
            "scope_type": scope_type,
            "scope_value": scope_value,
            "host": host,
            "occurrence_bin": occurrence_bin(len(values)),
            "next_events": len(values),
            "physical_folios": len(by_folio),
            "partner_types": len(pooled),
            "held_gain_bits": gains[host],
            "held_bits_per_event": gains[host] / len(values),
            "partner_set_overlap": overlap,
            "pairwise_jsd_bits": divergence,
            "pooled_target_entropy_bits": entropy(pooled),
            "mean_within_folio_entropy_bits": sum(entropy(counts) for counts in by_folio.values()) / len(by_folio),
            **nulls[host],
            "null_worlds": WORLDS,
        }
        host_rows.append(row)
    eligible_events = sum(row["next_events"] for row in host_rows)
    powered = len({event["folio"] for event in events}) >= 3 and len(events) >= 20 and len(host_rows) >= 3
    scope_row = summarize(system, scope_type, scope_value, "ALL_ELIGIBLE", host_rows, len(rows), len(events), powered)
    bin_rows = []
    for name in ("N2_4", "N5_15", "N16_63", "N64_PLUS"):
        selected = [row for row in host_rows if row["occurrence_bin"] == name]
        bin_rows.append(summarize(system, scope_type, scope_value, name, selected, len(rows), len(events), len(selected) >= 5))
    assert int(scope_row["eligible_next_events"]) == eligible_events
    return host_rows, scope_row, bin_rows


def mean(rows: list[dict], key: str) -> float | str:
    return sum(float(row[key]) for row in rows) / len(rows) if rows else "NA"


def summarize(system: str, scope_type: str, scope_value: str, label: str, rows: list[dict], total_groups: int, total_events: int, powered: bool) -> dict:
    eligible_events = sum(int(row["next_events"]) for row in rows)
    gain = sum(float(row["held_gain_bits"]) for row in rows)
    return {
        "system": system,
        "scope_type": scope_type,
        "scope_value": scope_value,
        "occurrence_bin": label,
        "total_groups": total_groups,
        "total_next_events": total_events,
        "eligible_hosts": len(rows),
        "eligible_next_events": eligible_events,
        "event_coverage": eligible_events / total_events if total_events else 0.0,
        "physical_folios": len(set().union(*(set() for _ in []))) if False else "DERIVED_SEPARATELY",
        "held_gain_bits": gain,
        "held_bits_per_event": gain / eligible_events if eligible_events else "NA",
        "mean_partner_set_overlap": mean(rows, "partner_set_overlap"),
        "mean_null_overlap": mean(rows, "null_overlap_mean"),
        "mean_overlap_excess": mean(rows, "overlap_excess"),
        "mean_pairwise_jsd_bits": mean(rows, "pairwise_jsd_bits"),
        "mean_null_jsd_bits": mean(rows, "null_jsd_mean"),
        "mean_jsd_excess": mean(rows, "jsd_excess"),
        "mean_pooled_target_entropy_bits": mean(rows, "pooled_target_entropy_bits"),
        "mean_within_folio_entropy_bits": mean(rows, "mean_within_folio_entropy_bits"),
        "powered": int(powered),
    }


def fmt(value) -> str:
    return "NA" if value == "NA" else f"{float(value):.6f}"


def main() -> None:
    design = json.loads(DESIGN.read_text())
    assert design["status"] == "DIAGNOSTIC_FROZEN_BEFORE_CONTROL_CALIBRATION"
    assert design["controls"] == ["LEXICAL_A", "HUMAN_GROWN_B2", "FACTORIAL_B"]
    assert design["build_b3"] is False and design["f84r_access"] is False
    controls = load_control_rows()
    all_host_rows, scope_rows, bin_rows = [], [], []
    counts = {}
    with ProcessPoolExecutor(max_workers=min(16, os.cpu_count() or 1)) as executor:
        for system in ("LEXICAL_A", "HUMAN_GROWN_B2", "FACTORIAL_B"):
            rows = controls[system]
            events = make_events(rows)
            counts[system] = {"groups": len(rows), "next_events": len(events), "folios": len({row["folio_id"] for row in rows}), "registers": len({row["register"] for row in rows})}
            host, scope, bins = scope_metrics(system, "GLOBAL", "ALL", rows, events, executor)
            scope["physical_folios"] = counts[system]["folios"]
            for item in bins: item["physical_folios"] = counts[system]["folios"]
            all_host_rows.extend(host); scope_rows.append(scope); bin_rows.extend(bins)
            for register in sorted({str(row["register"]) for row in rows}):
                subrows = [row for row in rows if str(row["register"]) == register]
                subevents = [event for event in events if event["register"] == register]
                host, scope, bins = scope_metrics(system, "REGISTER", register, subrows, subevents, executor)
                folios = len({row["folio_id"] for row in subrows})
                scope["physical_folios"] = folios
                for item in bins: item["physical_folios"] = folios
                all_host_rows.extend(host); scope_rows.append(scope); bin_rows.extend(bins)
            scope_rows.append({"system": system, "scope_type": "SECTION", "scope_value": "UNAVAILABLE", "occurrence_bin": "ALL_ELIGIBLE", "total_groups": len(rows), "total_next_events": len(events), "eligible_hosts": 0, "eligible_next_events": 0, "event_coverage": 0.0, "physical_folios": counts[system]["folios"], "held_gain_bits": "NA", "held_bits_per_event": "NA", "mean_partner_set_overlap": "NA", "mean_null_overlap": "NA", "mean_overlap_excess": "NA", "mean_pairwise_jsd_bits": "NA", "mean_null_jsd_bits": "NA", "mean_jsd_excess": "NA", "mean_pooled_target_entropy_bits": "NA", "mean_within_folio_entropy_bits": "NA", "powered": 0})
    all_host_rows.sort(key=lambda row: (row["system"], row["scope_type"], row["scope_value"], row["occurrence_bin"], row["host"]))
    scope_rows.sort(key=lambda row: (row["system"], row["scope_type"], row["scope_value"]))
    bin_rows.sort(key=lambda row: (row["system"], row["scope_type"], row["scope_value"], row["occurrence_bin"]))
    write_tsv(HOSTS, all_host_rows); write_tsv(BINS, bin_rows); write_tsv(SCOPES, scope_rows)
    envelopes = {}
    for bin_name in ("N2_4", "N5_15", "N16_63", "N64_PLUS"):
        selected = [row for row in bin_rows if row["scope_type"] == "GLOBAL" and row["occurrence_bin"] == bin_name and int(row["powered"])]
        assert len(selected) == 3
        envelopes[bin_name] = {
            key: [min(float(row[key]) for row in selected), max(float(row[key]) for row in selected)]
            for key in ("held_bits_per_event", "mean_overlap_excess", "mean_jsd_excess")
        }
    global_rows = [row for row in scope_rows if row["scope_type"] == "GLOBAL"]
    report_lines = [
        "# GDT175 control calibration — recurrence with partner instability",
        "",
        "Status: **CONTROL_CALIBRATION_FROZEN_BEFORE_VOYNICH_SCORING**.",
        "",
        "The unchanged GDT175 diagnostic was run only on frozen lexical A, human-grown B2, and factorial B. No Voynich source, B3, oracle field, or f84r material was read.",
        "",
        "## Global control calibration",
        "",
        "| control | eligible hosts | event coverage | held bits/event | overlap excess | JSD excess |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in global_rows:
        report_lines.append(f"| {row['system']} | {row['eligible_hosts']} | {fmt(row['event_coverage'])} | {fmt(row['held_bits_per_event'])} | {fmt(row['mean_overlap_excess'])} | {fmt(row['mean_jsd_excess'])} |")
    report_lines += [
        "",
        "All four frozen occurrence bins are powered in all three controls. The closed control envelopes in `gdt175_control_result.json` are now fixed; later Voynich placement may not alter them.",
        "",
        "Register rows use the same definitions and expose whether a global result is caused by register mixing. Synthetic SECTION scope is explicitly unavailable rather than inferred.",
        "",
        "## Claim ceiling",
        "",
        "This is instrument calibration only. It establishes no Voynich architecture, word, code, language, morphology, role, meaning, plaintext, or translation.",
    ]
    REPORT.write_text("\n".join(report_lines) + "\n")
    result = {
        "schema": "GDT175_CONTROL_PARTNER_INSTABILITY_RESULT_V1",
        "status": "CONTROL_CALIBRATION_FROZEN_BEFORE_VOYNICH_SCORING",
        "counts": {**counts, "host_metric_rows": len(all_host_rows), "bin_summary_rows": len(bin_rows), "scope_summary_rows": len(scope_rows)},
        "global_control_rows": global_rows,
        "control_envelopes": envelopes,
        "diagnostic": {"alpha": ALPHA, "beta": BETA, "null_worlds": WORLDS, "occurrence_bins": design["occurrence_bins"], "no_rescaling": True, "no_tuning": True},
        "inputs": {path.name: sha(path) for path in (DESIGN, METHOD, P172, P173)},
        "outputs": {path.name: sha(path) for path in (HOSTS, BINS, SCOPES, REPORT)},
        "commitments": {"host_rows_content_sha256": csha(all_host_rows), "bin_rows_content_sha256": csha(bin_rows), "scope_rows_content_sha256": csha(scope_rows)},
        "implementation": {Path(__file__).name: sha(Path(__file__))},
        "firewall": {"systems_read": ["LEXICAL_A", "HUMAN_GROWN_B2", "FACTORIAL_B"], "voynich_inputs": 0, "oracle_fields": 0, "build_b3": False, "f84r_access": False},
        "claim_ceiling": "Synthetic control calibration only; no Voynich architecture word code language morphology role meaning plaintext or translation.",
    }
    result["result_content_sha256"] = csha(result)
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": result["status"], "counts": result["counts"], "globals": global_rows}, sort_keys=True))


if __name__ == "__main__":
    main()
