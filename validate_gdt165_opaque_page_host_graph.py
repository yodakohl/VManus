#!/usr/bin/env python3
"""Independent validation for GDT165's opaque exact-host graph test.

This file deliberately does not import the producer.  It independently rebuilds
physical edges, exact-host held models, directed relations, and the complete
held-folio alignment null.  Spectral-community rows are validated for exported
arithmetic/decision integrity rather than by a second eigensolver.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import random
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "gdt062_right_family_inventory.tsv"
DESIGN = ROOT / "gdt165_design.json"
METHOD = ROOT / "GDT165_OPAQUE_PAGE_HOST_RELATION_GRAPH_METHOD.md"
REPORT = ROOT / "GDT165_OPAQUE_PAGE_HOST_RELATION_GRAPH_REPORT.md"
HOSTS = ROOT / "gdt165_host_manifest.tsv"
EDGES = ROOT / "gdt165_edge_inventory.tsv"
FOLDS = ROOT / "gdt165_fold_scores.tsv"
RELATIONS = ROOT / "gdt165_directed_relations.tsv"
COMMUNITIES = ROOT / "gdt165_community_stability.tsv"
NULLS = ROOT / "gdt165_null_results.tsv"
COUNTER = ROOT / "gdt165_counterexamples.tsv"
VARIANTS = ROOT / "gdt165_variant_log.tsv"
RESULT = ROOT / "gdt165_result.json"
VALIDATION = ROOT / "gdt165_validation.json"

ALPHA = 32.0
BETA = 16.0
WORLDS = 1024
MIN_REL = 8
MIN_REL_FOLIOS = 3
FEATURES = ("section", "currier", "hand", "source_frequency_bin", "position_quartile", "line_count_bin")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def csha(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def opaque(value: str) -> str:
    return "H" + hashlib.sha256(value.encode()).hexdigest()[:16]


def seed(label: str) -> int:
    return int(hashlib.sha256(label.encode()).hexdigest()[:16], 16)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def freq_bin(n: int) -> str:
    return "F1" if n == 1 else "F2_4" if n <= 4 else "F5_15" if n <= 15 else "F16_63" if n <= 63 else "F64P"


def line_bin(n: int) -> str:
    return str(n) if n <= 4 else "5_7" if n <= 7 else "8P"


def close(a: float, b: float, tol: float = 2e-8) -> bool:
    return abs(a - b) <= tol * max(1.0, abs(a), abs(b))


class Checks:
    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []

    def add(self, name: str, passed: bool, detail: object = "") -> None:
        self.rows.append({"check": name, "passed": bool(passed), "detail": str(detail)})
        if not passed:
            raise AssertionError(f"{name}: {detail}")


def rebuild_events(checks: Checks):
    rows = []
    total = rejected = 0
    with SOURCE.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            total += 1
            page, locus = row["page"], row["locus"]
            if page.startswith("f84") or locus.startswith("f84"):
                rejected += 1
                continue
            rows.append({"host": row["page_host"], "locus": locus,
                         "folio": row["physical_folio"], "section": row["section"],
                         "currier": row["currier"], "hand": row["hand"],
                         "index": int(row["group_index"]), "group_count": int(row["group_count"])})
    checks.add("source_census", (total, rejected, len(rows)) == (15592, 228, 15364), (total, rejected, len(rows)))
    checks.add("no_retained_f84", all(not r["locus"].startswith("f84") for r in rows))
    by_line = defaultdict(dict)
    for row in rows:
        by_line[row["locus"]][row["index"]] = row
    events = []
    for locus in sorted(by_line, key=lambda x: (x.split(".")[0], int(x.split(".")[-1]))):
        line = by_line[locus]
        lo, hi = min(line), max(line)
        for index in sorted(line):
            if index + 1 not in line:
                continue
            a, b = line[index], line[index + 1]
            quartile = min(3, int(4 * (index - lo) / max(1, hi - lo)))
            events.append({"event_id": len(events), "source": a["host"], "target": b["host"],
                           "locus": locus, "folio": a["folio"], "section": a["section"],
                           "currier": a["currier"], "hand": a["hand"],
                           "source_index": index, "target_index": index + 1,
                           "position_quartile": f"Q{quartile}", "line_count_bin": line_bin(a["group_count"])})
    source_counts = Counter(r["source"] for r in events)
    for row in events:
        row["source_frequency_bin"] = freq_bin(source_counts[row["source"]])
        row["nuisance_key"] = tuple(row[f] for f in FEATURES)
    checks.add("event_census", len(events) == 12467, len(events))
    checks.add("folio_census", len({r["folio"] for r in events}) == 92)
    return rows, events, total, rejected


def train(train: list[dict[str, object]], targets: list[str]):
    global_target = Counter(r["target"] for r in train)
    feature_target = [Counter() for _ in FEATURES]
    feature_total = [Counter() for _ in FEATURES]
    host_target = Counter()
    host_total = Counter()
    for row in train:
        for j, feature in enumerate(FEATURES):
            value = row[feature]
            feature_target[j][value, row["target"]] += 1
            feature_total[j][value] += 1
        host_target[row["source"], row["target"]] += 1
        host_total[row["source"]] += 1
    return {"global": global_target, "n": len(train), "v": len(targets),
            "feature_target": feature_target, "feature_total": feature_total,
            "host_target": host_target, "host_total": host_total}


def probs(model, event, target):
    q = (model["global"][target] + .5) / (model["n"] + .5 * model["v"])
    pieces = []
    for j, feature in enumerate(FEATURES):
        value = event[feature]
        pieces.append((model["feature_target"][j][value, target] + ALPHA * q) /
                      (model["feature_total"][j][value] + ALPHA))
    nuisance = sum(pieces) / len(pieces)
    host = (model["host_target"][event["source"], target] + BETA * nuisance) / (model["host_total"][event["source"]] + BETA)
    return q, nuisance, host


def refit(events, mode, targets, checks: Checks):
    held_key = {"HELD_FOLIO": "folio", "HELD_SECTION": "section", "HELD_HAND": "hand"}[mode]
    artifacts = {}
    calculated = {}
    for held in sorted({r[held_key] for r in events}):
        train_rows = [r for r in events if r[held_key] != held]
        test_rows = [r for r in events if r[held_key] == held]
        model = train(train_rows, targets)
        totals = Counter()
        for event in test_rows:
            q, nuisance, host = probs(model, event, event["target"])
            totals["unigram_bits"] -= math.log2(q)
            totals["nuisance_bits"] -= math.log2(nuisance)
            totals["host_bits"] -= math.log2(host)
            totals["seen"] += int(model["host_total"][event["source"]] > 0)
        totals["events"] = len(test_rows)
        totals["training_events"] = len(train_rows)
        totals["host_gain"] = totals["nuisance_bits"] - totals["host_bits"]
        calculated[str(held)] = totals
        artifacts[held] = model, test_rows
    exported = {r["held"]: r for r in read_tsv(FOLDS) if r["mode"] == mode}
    checks.add(mode + "_fold_keys", set(exported) == set(calculated))
    for held, calc in calculated.items():
        out = exported[held]
        checks.add(f"{mode}_{held}_counts", (int(out["events"]), int(out["training_events"]), int(out["source_seen_events"])) ==
                   (calc["events"], calc["training_events"], calc["seen"]))
        for key in ("unigram_bits", "nuisance_bits", "host_bits"):
            checks.add(f"{mode}_{held}_{key}", close(float(out[key]), calc[key]), (out[key], calc[key]))
        checks.add(f"{mode}_{held}_gain", close(float(out["host_gain_vs_nuisance_bits"]), calc["host_gain"]))
    return calculated, artifacts


def validate_null(events, artifacts, relation_rows, checks: Checks):
    rng = random.Random(seed("GDT165_HELD_ALIGNMENT_NULL"))
    prepared = {}
    swappable = variable = 0
    for held, (model, test) in artifacts.items():
        groups = defaultdict(list)
        for event in test:
            groups[event["nuisance_key"]].append(event)
        packed = {}
        for key, group in groups.items():
            sources = {r["source"] for r in group}
            targets = {r["target"] for r in group}
            exemplar = group[0]
            lookup = {}
            for source in sources:
                probe = dict(exemplar)
                probe["source"] = source
                for target in targets:
                    _, nuisance, host = probs(model, probe, target)
                    lookup[source, target] = math.log2(host / nuisance)
            packed[key] = group, lookup
        prepared[held] = packed
        swappable += sum(len(g) for g in groups.values() if len(g) >= 2)
        variable += sum(len(g) for g in groups.values() if len({r["target"] for r in g}) >= 2)
    exported = read_tsv(NULLS)
    checks.add("null_world_count", len(exported) == WORLDS)
    totals, tops = [], []
    for world in range(WORLDS):
        total = 0.0
        pair_gain = defaultdict(float)
        pair_count = Counter()
        pair_folios = defaultdict(set)
        for held in sorted(prepared):
            for key in sorted(prepared[held], key=str):
                group, lookup = prepared[held][key]
                targets = [r["target"] for r in group]
                rng.shuffle(targets)
                for event, target in zip(group, targets):
                    gain = lookup[event["source"], target]
                    total += gain
                    pair = event["source"], target
                    pair_gain[pair] += gain
                    pair_count[pair] += 1
                    pair_folios[pair].add(held)
        eligible = [pair_gain[p] for p in pair_gain if pair_count[p] >= MIN_REL and len(pair_folios[p]) >= MIN_REL_FOLIOS]
        top = max(eligible, default=0.0)
        out = exported[world]
        checks.add(f"null_{world}_total", close(float(out["total_host_gain_bits"]), total))
        checks.add(f"null_{world}_top", close(float(out["top_eligible_relation_gain_bits"]), top))
        checks.add(f"null_{world}_eligible", int(out["eligible_relations"]) == len(eligible))
        totals.append(total)
        tops.append(top)
    result = json.loads(RESULT.read_text())
    observed_total = sum(float(r["host_gain_vs_nuisance_bits"]) for r in read_tsv(FOLDS) if r["mode"] == "HELD_FOLIO")
    observed_top = max(float(r["held_folio_gain_bits"]) for r in relation_rows)
    summary = result["null"]
    checks.add("null_capacity", (summary["swappable_test_events"], summary["target_variable_test_events"]) == (swappable, variable))
    checks.add("null_observed_total", close(summary["observed_total_host_gain_bits"], observed_total))
    checks.add("null_observed_top", close(summary["observed_top_relation_gain_bits"], observed_top))
    checks.add("null_total_mean", close(summary["null_total_mean"], sum(totals) / WORLDS))
    checks.add("null_top_mean", close(summary["null_top_mean"], sum(tops) / WORLDS))
    p_total = (1 + sum(x >= observed_total - 1e-12 for x in totals)) / (WORLDS + 1)
    p_top = (1 + sum(x >= observed_top - 1e-12 for x in tops)) / (WORLDS + 1)
    checks.add("null_total_p", close(summary["total_gain_p"], p_total))
    checks.add("null_top_p", close(summary["top_relation_maxT_p"], p_top))
    return tops


def main() -> None:
    checks = Checks()
    result = json.loads(RESULT.read_text())
    stored_content = result.pop("result_content_sha256")
    checks.add("result_content_hash", csha(result) == stored_content)
    result["result_content_sha256"] = stored_content
    checks.add("result_schema", result["schema"] == "GDT165_OPAQUE_PAGE_HOST_RELATION_GRAPH_RESULT_V1")
    checks.add("result_status", result["status"] == "OPAQUE_HOST_RELATIONS_NOT_TRANSFERABLE")
    checks.add("design_frozen", json.loads(DESIGN.read_text())["status"] == "FROZEN_BEFORE_SCORING")
    for name, digest in result["inputs"].items():
        checks.add("input_hash_" + name, sha(ROOT / name) == digest)
    for name, digest in result["outputs"].items():
        checks.add("output_hash_" + name, sha(ROOT / name) == digest)
    for name, digest in result["documents"].items():
        checks.add("document_hash_" + name, sha(ROOT / name) == digest)
    for name, digest in result["implementation"].items():
        checks.add("implementation_hash_" + name, sha(ROOT / name) == digest)

    source_rows, events, total, rejected = rebuild_events(checks)
    exported_edges = read_tsv(EDGES)
    checks.add("edge_row_count", len(exported_edges) == len(events))
    edge_fields = ("source_host", "target_host", "locus", "physical_folio", "section", "currier", "hand",
                   "source_index", "target_index", "source_frequency_bin", "position_quartile", "line_count_bin")
    for event, out in zip(events, exported_edges):
        expected = {"source_host": event["source"], "target_host": event["target"], "locus": event["locus"],
                    "physical_folio": event["folio"], "section": event["section"], "currier": event["currier"],
                    "hand": event["hand"], "source_index": str(event["source_index"]),
                    "target_index": str(event["target_index"]), "source_frequency_bin": event["source_frequency_bin"],
                    "position_quartile": event["position_quartile"], "line_count_bin": event["line_count_bin"]}
        checks.add("edge_" + str(event["event_id"]), all(out[f] == expected[f] for f in edge_fields))
        checks.add("edge_hash_" + str(event["event_id"]), out["source_host_id"] == opaque(event["source"]) and out["target_host_id"] == opaque(event["target"]))

    host_rows = read_tsv(HOSTS)
    checks.add("host_manifest_counts", (len(host_rows), sum(int(r["source_events"]) for r in host_rows),
                                        sum(int(r["target_events"]) for r in host_rows),
                                        sum(int(r["community_panel"]) for r in host_rows)) == (1813, 12467, 12467, 128))
    targets = sorted({r["target"] for r in events}, key=opaque)
    calculated = {}
    artifacts = None
    for mode in ("HELD_FOLIO", "HELD_SECTION", "HELD_HAND"):
        calculated[mode], held_artifacts = refit(events, mode, targets, checks)
        if mode == "HELD_FOLIO":
            artifacts = held_artifacts
        aggregate_gain = sum(x["host_gain"] for x in calculated[mode].values())
        checks.add(mode + "_aggregate_gain", close(aggregate_gain, result["summaries"][mode]["host_gain_vs_nuisance_bits"]))
        checks.add(mode + "_all_folds_negative", sum(x["host_gain"] > 0 for x in calculated[mode].values()) == 0)

    contributions = defaultdict(lambda: defaultdict(float))
    pair_folio_gain = defaultdict(lambda: defaultdict(float))
    for mode, rows in calculated.items():
        held_key = {"HELD_FOLIO": "folio", "HELD_SECTION": "section", "HELD_HAND": "hand"}[mode]
        for held in sorted({r[held_key] for r in events}):
            model, test = (artifacts[held] if mode == "HELD_FOLIO" else
                           (train([r for r in events if r[held_key] != held], targets), [r for r in events if r[held_key] == held]))
            for event in test:
                _, nuisance, host = probs(model, event, event["target"])
                gain = math.log2(host / nuisance)
                pair = event["source"], event["target"]
                contributions[pair][mode] += gain
                if mode == "HELD_FOLIO":
                    pair_folio_gain[pair][held] += gain
    pair_counts = Counter((r["source"], r["target"]) for r in events)
    pair_folios = defaultdict(set)
    pair_sections = defaultdict(set)
    pair_hands = defaultdict(set)
    for r in events:
        pair = r["source"], r["target"]
        pair_folios[pair].add(r["folio"]); pair_sections[pair].add(r["section"]); pair_hands[pair].add(r["hand"])
    eligible = {p for p, n in pair_counts.items() if n >= MIN_REL and len(pair_folios[p]) >= MIN_REL_FOLIOS}
    relation_rows = read_tsv(RELATIONS)
    checks.add("eligible_relation_count", len(relation_rows) == len(eligible) == 174)
    relation_by_pair = {(r["source_host"], r["target_host"]): r for r in relation_rows}
    checks.add("eligible_relation_keys", set(relation_by_pair) == eligible)
    for pair in eligible:
        out = relation_by_pair[pair]
        checks.add("relation_counts_" + opaque("|".join(pair)),
                   (int(out["occurrences"]), int(out["folios"]), int(out["sections"]), int(out["hands"])) ==
                   (pair_counts[pair], len(pair_folios[pair]), len(pair_sections[pair]), len(pair_hands[pair])))
        for mode, field in (("HELD_FOLIO", "held_folio_gain_bits"), ("HELD_SECTION", "held_section_gain_bits"), ("HELD_HAND", "held_hand_gain_bits")):
            checks.add("relation_gain_" + mode + "_" + opaque("|".join(pair)), close(float(out[field]), contributions[pair][mode]))
    tops = validate_null(events, artifacts, relation_rows, checks)
    for row in relation_rows:
        expected = (1 + sum(x >= float(row["held_folio_gain_bits"]) - 1e-12 for x in tops)) / (WORLDS + 1)
        checks.add("relation_maxT_" + row["source_host_id"] + row["target_host_id"], close(float(row["maxT_p"]), expected))
    stable = [r for r in relation_rows if r["label"] == "STABLE_DIRECTED_RELATION"]
    checks.add("single_stable_relation", len(stable) == 1 and stable[0]["source_host"] == "ok" and stable[0]["target_host"] == "y")

    community_folds = read_tsv(FOLDS)
    for mode in ("HELD_FOLIO", "HELD_SECTION", "HELD_HAND"):
        rows = [r for r in community_folds if r["mode"] == mode]
        s = result["summaries"][mode]
        checks.add(mode + "_community_gain_integrity", close(sum(float(r["community_gain_vs_nuisance_bits"]) for r in rows), s["community_gain_vs_nuisance_bits"]))
        checks.add(mode + "_community_fold_count", len(rows) == s["folds"])
    comm = read_tsv(COMMUNITIES)
    section = [float(r["coassignment_jaccard"]) for r in comm if r["axis"] == "HELD_SECTION"]
    hand = [float(r["coassignment_jaccard"]) for r in comm if r["axis"] == "HELD_HAND"]
    section_q = [float(r["null_q95"]) for r in comm if r["axis"] == "HELD_SECTION"]
    hand_q = [float(r["null_q95"]) for r in comm if r["axis"] == "HELD_HAND"]
    def median(xs):
        xs = sorted(xs); n = len(xs); return xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2
    checks.add("community_section_median", close(median(section), result["community_summary"]["section_median_jaccard"]))
    checks.add("community_hand_median", close(median(hand), result["community_summary"]["hand_median_jaccard"]))
    checks.add("community_section_q95", close(median(section_q), result["community_summary"]["section_median_null_q95"]))
    checks.add("community_hand_q95", close(median(hand_q), result["community_summary"]["hand_median_null_q95"]))
    checks.add("community_not_predictive", result["community_summary"]["predictive_all_splits"] is False and result["community_summary"]["stable"] is False)
    checks.add("decision_inputs", result["decision_inputs"] == {"community_gate": False, "exact_all_splits_positive": False,
               "held_folio_null_pass": True, "stable_maxT_relation": True})
    checks.add("f84_flags", all(v is False for v in result["f84r"].values()))
    checks.add("claim_ceiling", "translation" in result["claim_ceiling"] and "semantic role" in result["claim_ceiling"])

    payload = {"schema": "GDT165_OPAQUE_PAGE_HOST_RELATION_GRAPH_VALIDATION_V1",
               "status": "PASS_INDEPENDENT_EXACT_HOST_RELATION_NULL_WITH_COMMUNITY_OUTPUT_INTEGRITY",
               "checks_passed": len(checks.rows), "checks_failed": 0,
               "check_manifest_sha256": csha(checks.rows),
               "scope": "Nonimporting source/edge rebuild; independent folio/section/hand exact-host refit; independent directed-relation and full 1024-world held-alignment/maxT null replay; community output arithmetic and decision integrity, not a second spectral eigensolver.",
               "result_sha256": sha(RESULT), "validator_sha256": sha(Path(__file__)),
               "f84r": {"opened": False, "queried": False, "retained": False, "joined": False, "scored": False}}
    payload["validation_content_sha256"] = csha(payload)
    VALIDATION.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "checks": payload["checks_passed"],
                      "result_sha256": payload["result_sha256"]}, sort_keys=True))


if __name__ == "__main__":
    main()
