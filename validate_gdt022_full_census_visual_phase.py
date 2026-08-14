#!/usr/bin/env python3
"""Independent, nonimporting reconstruction of GDT022."""
from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
RESULT = ROOT / "gdt022_result.json"
VALIDATION = ROOT / "gdt022_validation.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()


def rows(name: str) -> list[dict[str, str]]:
    with (ROOT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def has_feature(row: dict[str, str], model: str, feature: str) -> bool:
    if feature.startswith("FAMILY_EXACT:"):
        return model == "SOURCE_FAMILY" and row["family_surface"] == feature.split(":", 1)[1]
    if feature.startswith("HOST_EXACT:"):
        return model == "RESIDUAL_HOST" and row["residual_host"] == feature.split(":", 1)[1]
    if feature.startswith("LAYER:"):
        return model == "RESIDUAL_HOST" and row["stripped_prefix"] == feature.split(":", 1)[1]
    if feature.startswith("CLOSURE:"):
        return model == "RESIDUAL_HOST" and row["dy_closure"] == feature.split(":", 1)[1]
    tag = "F" if model == "SOURCE_FAMILY" else "H"
    text = row["family_surface"] if model == "SOURCE_FAMILY" else row["residual_host"]
    if not feature.startswith(tag) or ":" not in feature:
        return False
    n = int(feature[1:feature.index(":")])
    wanted = feature.split(":", 1)[1]
    padded = "^" + text + "$"
    return any(padded[i:i+n] == wanted for i in range(len(padded) - n + 1))


def pmf(n: int, successes: int, draws: int) -> np.ndarray:
    lower = max(0, draws - (n - successes))
    upper = min(draws, successes)
    values = np.zeros(upper + 1)
    total = math.comb(n, draws)
    for value in range(lower, upper + 1):
        values[value] = math.comb(successes, value) * math.comb(n - successes, draws - value) / total
    return values


def score(keys, positives, contexts, outcome, omitted=None, probability=True):
    buckets = defaultdict(list)
    for key in keys:
        item = contexts[key]
        if omitted and item["folio"] == omitted:
            continue
        buckets[(item["page"], item["state"], item["quartile"])].append((key in positives, item[outcome]))
    observed = 0
    expectation = 0.0
    top = 0.0
    bottom = 0.0
    informative = 0
    law = np.array([1.0])
    for bucket in buckets.values():
        n = len(bucket)
        selected = sum(int(flag) for flag, _ in bucket)
        outcomes = sum(value for _, value in bucket)
        if selected in (0, n) or outcomes in (0, n):
            continue
        informative += 1
        overlap = sum(int(flag and value) for flag, value in bucket)
        expected = selected * outcomes / n
        observed += overlap
        expectation += expected
        weight = selected * (n - selected) / n
        top += weight * (overlap / selected - (outcomes - overlap) / (n - selected))
        bottom += weight
        if probability:
            law = np.convolve(law, pmf(n, outcomes, selected))
    effect = top / bottom if bottom else 0.0
    p_value = 1.0
    support = 0
    if probability and bottom:
        radius = abs(observed - expectation)
        p_value = min(1.0, float(law[np.abs(np.arange(len(law)) - expectation) >= radius - 1e-12].sum()))
        support = int(np.count_nonzero(law > 0))
    return effect, p_value, observed, expectation, informative, support


def close(left, right, tolerance=7e-12):
    return abs(float(left) - float(right)) <= tolerance


def main() -> None:
    checks: list[tuple[str, bool]] = []
    result = json.loads(RESULT.read_text())
    body = dict(result)
    digest = body.pop("result_content_sha256")
    checks += [("schema", result["schema"] == "GDT022_FULL_CENSUS_VISUAL_PHASE_RESULT_V1"), ("content_hash", digest == canonical(body))]
    for part in ("inputs", "implementation", "outputs"):
        for name, expected in result[part].items():
            checks.append((part + ":" + name, sha(ROOT / name) == expected))

    inventory = rows("gdt016_group_state_inventory.tsv")
    anchors = rows("gdt013_role_anchors.tsv")
    checks += [
        ("inventory_count", len(inventory) == result["inventory_groups"] == 15592),
        ("anchor_count", len(anchors) == result["anchors"] == 80),
        ("f84_absent", not any(row["locus"].startswith("f84r") for row in inventory)),
        ("producer_cap_confirmed", "matches[:40]" in (ROOT / "run_gdt013_latent_role_propagation.py").read_text()),
        ("correction", result["correction"]["superseded_experiment"] == "GDT021" and not result["correction"]["gdt021_quantitative_inference_valid"]),
    ]

    lookup = {}
    lines = defaultdict(list)
    for row in inventory:
        key = (row["locus"], int(row["group_index"]))
        lookup[key] = row
        lines[row["locus"]].append(row)
    context = {}
    previous = {}
    for locus, line in lines.items():
        line.sort(key=lambda row: int(row["group_index"]))
        future = [0] * len(line)
        flag = 0
        for index in range(len(line) - 1, -1, -1):
            flag = max(flag, int(line[index]["record_state"] == "DY_RESOLUTION"))
            future[index] = flag
        seen = 0
        after = 0
        for index, row in enumerate(line):
            count = int(row["group_count"])
            position = (int(row["group_index"]) - 1) / (count - 1) if count > 1 else 0.5
            key = (locus, int(row["group_index"]))
            context[key] = {
                "page": row["page"], "folio": row["physical_folio"], "state": row["record_state"],
                "quartile": min(3, int(position * 4)), "SEEN_DY": seen, "IMMEDIATE_POST_DY": after,
                "CLOSED_FIELD": future[index], "LINE_FINAL": int(index == len(line) - 1),
            }
            previous[key] = line[index - 1]["token"] if index else "LINE_START"
            after = int(row["record_state"] == "DY_RESOLUTION")
            seen = max(seen, after)

    matched = {}
    for anchor in anchors:
        pair = (anchor["selected_model"], anchor["formal_feature"])
        matched[pair] = {key for key, row in lookup.items() if has_feature(row, *pair)}
        checks.append(("anchor_total:" + ":".join(pair), len(matched[pair]) == int(anchor["prose_occurrence_total"])))

    roles = sorted({row["role"] for row in anchors})
    role_features = defaultdict(list)
    for anchor in anchors:
        role_features[(anchor["role"], anchor["selected_model"])].append(anchor["formal_feature"])
    scopes = ("UNION", "SOURCE_FAMILY", "RESIDUAL_HOST")
    outcomes = ("SEEN_DY", "IMMEDIATE_POST_DY", "CLOSED_FIELD", "LINE_FINAL")
    universes = {}
    positives = {}
    for scope in scopes:
        models = ("SOURCE_FAMILY", "RESIDUAL_HOST") if scope == "UNION" else (scope,)
        universe = set()
        for role in roles:
            selected = set()
            for model in models:
                for feature in role_features[(role, model)]:
                    selected |= matched[(model, feature)]
            positives[(scope, role)] = selected
            universe |= selected
        universes[scope] = universe
        checks.append(("scope_count:" + scope, len(universe) == result["scope_group_counts"][scope]))

    stored = {(row["scope"], row["visual_anchor_role"], row["field_context"]): row for row in rows("gdt022_role_phase_tests.tsv")}
    for scope in scopes:
        keys = universes[scope]
        folios = sorted({context[key]["folio"] for key in keys})
        for role in roles:
            selected = positives[(scope, role)]
            for outcome in outcomes:
                effect, p_value, observed, expected, n_strata, support = score(keys, selected, context, outcome)
                lofo = [score(keys, selected, context, outcome, folio, False)[0] for folio in folios]
                row = stored[(scope, role, outcome)]
                checks.append(("atlas:" + scope + ":" + role + ":" + outcome,
                    int(row["universe_groups"]) == len(keys) and int(row["role_groups"]) == len(selected)
                    and close(row["conditional_effect"], effect) and close(row["exact_p"], p_value)
                    and int(row["observed_role_outcomes"]) == observed and close(row["expected_role_outcomes"], expected)
                    and int(row["informative_strata"]) == n_strata and int(row["exact_distribution_support"]) == support
                    and int(row["lofo_positive_effects"]) == sum(value > 0 for value in lofo)
                    and close(row["lofo_min_effect"], min(lofo)) and close(row["lofo_max_effect"], max(lofo))))
    primary = min(stored.values(), key=lambda row: (float(row["exact_p"]), -abs(float(row["conditional_effect"])), row["scope"], row["visual_anchor_role"], row["field_context"]))
    checks += [
        ("atlas_size", len(stored) == result["tests"] == 96),
        ("primary", all(str(primary[key]) == str(result["primary"][key]) for key in ("scope", "visual_anchor_role", "field_context", "observed_role_outcomes")) and close(primary["exact_p"], result["primary"]["exact_p"])),
    ]

    feature_rows = {(row["anchor_model"], row["formal_feature"]): row for row in rows("gdt022_figure_feature_phase_tests.tsv")}
    for anchor in [row for row in anchors if row["role"] == "FIGURE"]:
        pair = (anchor["selected_model"], anchor["formal_feature"])
        effect, p_value, observed, expected, n_strata, _ = score(set(lookup), matched[pair], context, "IMMEDIATE_POST_DY")
        folios = sorted({item["folio"] for item in context.values()})
        lofo = [score(set(lookup), matched[pair], context, "IMMEDIATE_POST_DY", folio, False)[0] for folio in folios]
        row = feature_rows[pair]
        checks.append(("feature:" + ":".join(pair), int(row["complete_prose_occurrences"]) == len(matched[pair])
            and close(row["conditional_effect"], effect) and close(row["exact_p"], p_value)
            and int(row["observed_postdy"]) == observed and close(row["expected_postdy"], expected)
            and int(row["informative_strata"]) == n_strata and int(row["lofo_positive_effects"]) == sum(value > 0 for value in lofo)
            and close(row["lofo_min_effect"], min(lofo)) and close(row["lofo_max_effect"], max(lofo))))
    checks.append(("feature_counts", len(feature_rows) == result["figure_feature_tests"] == 10 and sum(float(row["search_adjusted_p_10"]) < 0.05 for row in feature_rows.values()) == result["figure_features_adjusted_positive"] == 3))

    membership = rows("gdt022_full_anchor_membership.tsv")
    checks += [
        ("membership_count", len(membership) == len(universes["UNION"]) == 7543),
        ("membership_keys", {(row["locus"], int(row["group_index"])) for row in membership} == universes["UNION"]),
    ]
    figure_union = positives[("UNION", "FIGURE")]
    expected_examples = {(key[0], key[1], previous[key], lookup[key]["token"]) for key in figure_union if context[key]["IMMEDIATE_POST_DY"]}
    actual_examples = {(row["locus"], int(row["group_index"]), row["previous_dy_token"], row["target_token"]) for row in rows("gdt022_figure_postdy_examples.tsv")}
    checks.append(("examples", actual_examples == expected_examples and len(actual_examples) == result["figure_postdy_examples"]))

    ledger = (ROOT / "GDT002_YOLO_LEDGER.tsv").read_text()
    report = (ROOT / "GDT022_FULL_CENSUS_VISUAL_PHASE_REPORT.md").read_text().lower()
    correction = (ROOT / "GDT021_SAMPLING_CORRECTION.md").read_text().lower()
    checks += [
        ("ledger", ledger.count("GDT021_CKPT002") == 1 and ledger.count("GDT022_CKPT001") == 1),
        ("f84_flags", result["f84r"] == {"input_contains_rows": False, "opened": False, "retained": False, "joined": False, "scored": False}),
        ("claims", all(text in report for text in ("no prose group is assigned figure meaning", "selection and register ecology", "f84r was not opened", "no semantic role"))),
        ("correction_text", "superseded" in correction and "matches[:40]" in correction),
    ]

    failures = [name for name, ok in checks if not ok]
    validation = {
        "schema": "GDT022_FULL_CENSUS_VISUAL_PHASE_VALIDATION_V1",
        "status": "PASS" if not failures else "FAIL", "checks": len(checks), "failures": failures,
        "result_sha256": sha(RESULT), "validator_sha256": sha(Path(__file__)),
        "scope": "Independent nonimporting reconstruction of all complete-census anchor matches, 96 conditional randomization tests, 10 FIGURE-feature audits, LOFO effects, examples, correction, hashes, f84r exclusion, ledger, and claim ceiling.",
    }
    VALIDATION.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n")
    print(json.dumps(validation, sort_keys=True))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
