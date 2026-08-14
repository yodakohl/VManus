#!/usr/bin/env python3
"""Reconstruct GDT013 anchors over the full frozen f84r-free GDT016 census."""
from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def csha(value: object) -> str:
    data = json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
    return hashlib.sha256(data.encode()).hexdigest()


def read(name: str) -> list[dict[str, str]]:
    with (ROOT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(name)
    with (ROOT / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def ngrams(text: str, tag: str) -> set[str]:
    padded = "^" + text + "$"
    return {f"{tag}{n}:{padded[i:i+n]}" for n in (1, 2, 3) for i in range(len(padded) - n + 1)}


def formal_features(row: dict[str, str], model: str) -> set[str]:
    if model == "SOURCE_FAMILY":
        return ngrams(row["family_surface"], "F") | {f"FAMILY_EXACT:{row['family_surface']}"}
    if model == "RESIDUAL_HOST":
        return ngrams(row["residual_host"], "H") | {
            f"HOST_EXACT:{row['residual_host']}",
            f"LAYER:{row['stripped_prefix']}",
            f"CLOSURE:{row['dy_closure']}",
        }
    raise ValueError(model)


def hypergeom_pmf(n: int, k: int, m: int) -> np.ndarray:
    lo, hi = max(0, m - (n - k)), min(m, k)
    out = np.zeros(hi + 1, dtype=float)
    denom = math.comb(n, m)
    for x in range(lo, hi + 1):
        out[x] = math.comb(k, x) * math.comb(n - k, m - x) / denom
    return out


def statistic(
    keys: set[tuple[str, int]],
    positive: set[tuple[str, int]],
    context: dict[tuple[str, int], dict[str, object]],
    outcome: str,
    exclude_folio: str | None = None,
    exact_p: bool = True,
) -> dict[str, object]:
    strata: dict[tuple[object, ...], list[tuple[bool, int]]] = defaultdict(list)
    for key in keys:
        x = context[key]
        if exclude_folio and x["physical_folio"] == exclude_folio:
            continue
        strata[(x["page"], x["state"], x["position_bin"])].append((key in positive, int(x[outcome])))
    obs = 0
    expected = 0.0
    numerator = 0.0
    denominator = 0.0
    informative = 0
    distribution = np.array([1.0])
    for values in strata.values():
        n = len(values)
        m = sum(int(a) for a, _ in values)
        k = sum(y for _, y in values)
        if not (0 < m < n and 0 < k < n):
            continue
        informative += 1
        observed = sum(int(a and y) for a, y in values)
        exp = m * k / n
        obs += observed
        expected += exp
        weight = m * (n - m) / n
        numerator += weight * (observed / m - (k - observed) / (n - m))
        denominator += weight
        if exact_p:
            distribution = np.convolve(distribution, hypergeom_pmf(n, k, m))
    effect = numerator / denominator if denominator else 0.0
    p = 1.0
    support = 0
    if exact_p and denominator:
        distance = abs(obs - expected)
        p = float(distribution[np.abs(np.arange(len(distribution)) - expected) >= distance - 1e-12].sum())
        p = min(1.0, p)
        support = int(np.count_nonzero(distribution > 0))
    return {
        "effect": effect,
        "p": p,
        "observed": obs,
        "expected": expected,
        "informative_strata": informative,
        "distribution_support": support,
    }


def main() -> None:
    inventory = read("gdt016_group_state_inventory.tsv")
    anchors = read("gdt013_role_anchors.tsv")
    assert len(inventory) == 15592
    assert len(anchors) == 80
    assert not any(row["locus"].startswith("f84r") for row in inventory)

    row_by_key: dict[tuple[str, int], dict[str, str]] = {}
    line_rows: dict[str, list[dict[str, str]]] = defaultdict(list)
    feature_cache: dict[tuple[tuple[str, int], str], set[str]] = {}
    for row in inventory:
        key = (row["locus"], int(row["group_index"]))
        row_by_key[key] = row
        line_rows[row["locus"]].append(row)
        for model in ("SOURCE_FAMILY", "RESIDUAL_HOST"):
            feature_cache[(key, model)] = formal_features(row, model)

    context: dict[tuple[str, int], dict[str, object]] = {}
    previous_token: dict[tuple[str, int], str] = {}
    for locus, line in line_rows.items():
        line.sort(key=lambda row: int(row["group_index"]))
        future_dy = [0] * len(line)
        has_future_dy = 0
        for i in range(len(line) - 1, -1, -1):
            has_future_dy = max(has_future_dy, int(line[i]["record_state"] == "DY_RESOLUTION"))
            future_dy[i] = has_future_dy
        seen_dy = 0
        immediate = 0
        for i, row in enumerate(line):
            count = int(row["group_count"])
            frac = (int(row["group_index"]) - 1) / (count - 1) if count > 1 else 0.5
            key = (locus, int(row["group_index"]))
            context[key] = {
                "page": row["page"],
                "physical_folio": row["physical_folio"],
                "state": row["record_state"],
                "position_bin": min(3, int(frac * 4)),
                "SEEN_DY": seen_dy,
                "IMMEDIATE_POST_DY": immediate,
                "CLOSED_FIELD": future_dy[i],
                "LINE_FINAL": int(i == len(line) - 1),
            }
            previous_token[key] = line[i - 1]["token"] if i else "LINE_START"
            immediate = int(row["record_state"] == "DY_RESOLUTION")
            seen_dy = max(seen_dy, immediate)

    match: dict[tuple[str, str], set[tuple[str, int]]] = {}
    for anchor in anchors:
        feature = anchor["formal_feature"]
        model = anchor["selected_model"]
        match[(model, feature)] = {
            key for key in row_by_key if feature in feature_cache[(key, model)]
        }
        assert len(match[(model, feature)]) == int(anchor["prose_occurrence_total"])

    roles = sorted({row["role"] for row in anchors})
    role_features: dict[tuple[str, str], list[str]] = defaultdict(list)
    for row in anchors:
        role_features[(row["role"], row["selected_model"])].append(row["formal_feature"])
    scopes = ("UNION", "SOURCE_FAMILY", "RESIDUAL_HOST")
    outcomes = ("SEEN_DY", "IMMEDIATE_POST_DY", "CLOSED_FIELD", "LINE_FINAL")

    membership: list[dict[str, object]] = []
    scope_keys: dict[str, set[tuple[str, int]]] = {}
    role_keys: dict[tuple[str, str], set[tuple[str, int]]] = {}
    for scope in scopes:
        models = ("SOURCE_FAMILY", "RESIDUAL_HOST") if scope == "UNION" else (scope,)
        universe: set[tuple[str, int]] = set()
        for role in roles:
            keys: set[tuple[str, int]] = set()
            for model in models:
                for feature in role_features[(role, model)]:
                    keys |= match[(model, feature)]
            role_keys[(scope, role)] = keys
            universe |= keys
        scope_keys[scope] = universe

    for key in sorted(scope_keys["UNION"]):
        row = row_by_key[key]
        sf_features = sorted(feature for (model, feature), keys in match.items() if model == "SOURCE_FAMILY" and key in keys)
        rh_features = sorted(feature for (model, feature), keys in match.items() if model == "RESIDUAL_HOST" and key in keys)
        membership.append({
            "locus": key[0], "page": row["page"], "physical_folio": row["physical_folio"],
            "group_index": key[1], "token": row["token"], "family_surface": row["family_surface"],
            "record_state": row["record_state"],
            "source_family_roles": "|".join(role for role in roles if key in role_keys[("SOURCE_FAMILY", role)]),
            "residual_host_roles": "|".join(role for role in roles if key in role_keys[("RESIDUAL_HOST", role)]),
            "union_roles": "|".join(role for role in roles if key in role_keys[("UNION", role)]),
            "source_family_features": "|".join(sf_features), "residual_host_features": "|".join(rh_features),
            "claim_state": "FULL_CENSUS_FORMAL_ANCHOR_MATCH_NOT_MEANING",
        })
    write("gdt022_full_anchor_membership.tsv", membership)

    atlas: list[dict[str, object]] = []
    total_tests = len(roles) * len(scopes) * len(outcomes)
    for scope in scopes:
        keys = scope_keys[scope]
        folios = sorted({context[key]["physical_folio"] for key in keys})
        for role in roles:
            positive = role_keys[(scope, role)]
            for outcome in outcomes:
                stat = statistic(keys, positive, context, outcome)
                lofo = [statistic(keys, positive, context, outcome, folio, False)["effect"] for folio in folios]
                adjusted = min(1.0, float(stat["p"]) * total_tests)
                if adjusted < 0.05 and lofo and min(lofo) > 0:
                    label = "INTERESTING_EXPLORATORY"
                elif float(stat["p"]) < 0.1:
                    label = "WEAK"
                elif lofo and min(lofo) < 0 < max(lofo):
                    label = "UNSTABLE"
                else:
                    label = "NO_SIGNAL"
                atlas.append({
                    "scope": scope, "visual_anchor_role": role, "field_context": outcome,
                    "universe_groups": len(keys), "role_groups": len(positive),
                    "conditional_effect": f"{stat['effect']:.12f}",
                    "observed_role_outcomes": stat["observed"], "expected_role_outcomes": f"{stat['expected']:.12f}",
                    "informative_strata": stat["informative_strata"], "exact_distribution_support": stat["distribution_support"],
                    "exact_p": f"{stat['p']:.12f}", "search_adjusted_p_96": f"{adjusted:.12f}",
                    "lofo_folios": len(lofo), "lofo_positive_effects": sum(value > 0 for value in lofo),
                    "lofo_min_effect": f"{min(lofo) if lofo else 0:.12f}", "lofo_max_effect": f"{max(lofo) if lofo else 0:.12f}",
                    "label": label, "claim_state": "FULL_CENSUS_VISUAL_DERIVED_ANCHOR_TO_PROSE_CONTEXT_NOT_MEANING",
                })
    atlas.sort(key=lambda row: (float(row["exact_p"]), -abs(float(row["conditional_effect"])), row["scope"], row["visual_anchor_role"], row["field_context"]))
    write("gdt022_role_phase_tests.tsv", atlas)

    figure_anchors = [row for row in anchors if row["role"] == "FIGURE"]
    all_keys = set(row_by_key)
    feature_tests: list[dict[str, object]] = []
    for anchor in figure_anchors:
        model, feature = anchor["selected_model"], anchor["formal_feature"]
        positive = match[(model, feature)]
        stat = statistic(all_keys, positive, context, "IMMEDIATE_POST_DY")
        folios = sorted({context[key]["physical_folio"] for key in all_keys})
        lofo = [statistic(all_keys, positive, context, "IMMEDIATE_POST_DY", folio, False)["effect"] for folio in folios]
        feature_tests.append({
            "anchor_model": model, "anchor_rank": anchor["rank"], "formal_feature": feature,
            "annotated_support": anchor["support"], "annotated_positive_support": anchor["positive_support"],
            "complete_prose_occurrences": len(positive), "conditional_effect": f"{stat['effect']:.12f}",
            "observed_postdy": stat["observed"], "expected_postdy": f"{stat['expected']:.12f}",
            "informative_strata": stat["informative_strata"], "exact_p": f"{stat['p']:.12f}",
            "search_adjusted_p_10": f"{min(1.0, float(stat['p']) * 10):.12f}",
            "lofo_positive_effects": sum(value > 0 for value in lofo), "lofo_folios": len(lofo),
            "lofo_min_effect": f"{min(lofo):.12f}", "lofo_max_effect": f"{max(lofo):.12f}",
            "claim_state": "POSTSELECTED_INDIVIDUAL_FORMAL_MOTIF_PHASE_AUDIT_NOT_MEANING",
        })
    feature_tests.sort(key=lambda row: (float(row["exact_p"]), row["anchor_model"], row["formal_feature"]))
    write("gdt022_figure_feature_phase_tests.tsv", feature_tests)

    figure_union = role_keys[("UNION", "FIGURE")]
    figure_features_by_key: dict[tuple[str, int], list[str]] = defaultdict(list)
    for anchor in figure_anchors:
        for key in match[(anchor["selected_model"], anchor["formal_feature"])]:
            figure_features_by_key[key].append(anchor["selected_model"] + ":" + anchor["formal_feature"])
    examples: list[dict[str, object]] = []
    for key in sorted(figure_union):
        if not context[key]["IMMEDIATE_POST_DY"]:
            continue
        row = row_by_key[key]
        examples.append({
            "locus": key[0], "page": row["page"], "physical_folio": row["physical_folio"],
            "group_index": key[1], "previous_dy_token": previous_token[key], "target_token": row["token"],
            "target_family": row["family_surface"], "record_state": row["record_state"],
            "matching_figure_features": "|".join(sorted(figure_features_by_key[key])),
            "claim_state": "COMPLETE_PROSE_OCCURRENCE_OF_VISUALLY_NOMINATED_FEATURE_NOT_FIGURE_MEANING",
        })
    write("gdt022_figure_postdy_examples.tsv", examples)

    primary = atlas[0]
    status = "FULL_CENSUS_FIGURE_ANCHOR_POST_CHECKPOINT_LEAD_EXPLORATORY" if (
        primary["visual_anchor_role"] == "FIGURE" and primary["field_context"] == "IMMEDIATE_POST_DY"
    ) else "FULL_CENSUS_VISUAL_PHASE_LEADS_WEAK"
    significant_features = [row for row in feature_tests if float(row["search_adjusted_p_10"]) < 0.05]
    report = f"""# GDT022 full-census visual-anchor / record-phase report

Status: **{status.replace('_', ' ')}**

GDT021's quantitative result is superseded: it scored a display export capped
at 40 occurrences per anchor.  GDT022 reconstructs all 80 frozen anchor
features over the complete {len(inventory):,}-group eligible census.  The
union comprises {len(scope_keys['UNION']):,} distinct prose groups, rather
than GDT021's 1,502 sampled groups.

The strongest of {total_tests} full-census cells is `{primary['scope']} / \
{primary['visual_anchor_role']} / {primary['field_context']}`.  Conditional on
page, anonymous record state, and line-position quartile, the effect is
{float(primary['conditional_effect']):+.4f}: {primary['observed_role_outcomes']}
observed outcomes versus {float(primary['expected_role_outcomes']):.3f}
expected.  The exact conditional p-value is {float(primary['exact_p']):.6g}
and the 96-cell adjusted value is
{float(primary['search_adjusted_p_96']):.6g}.  The effect remains positive in
{primary['lofo_positive_effects']}/{primary['lofo_folios']} leave-one-folio
deletions (minimum {float(primary['lofo_min_effect']):+.4f}).

The individual-feature audit shows that the broad FIGURE-derived set is not a
uniform class.  {len(significant_features)} of ten post-selected motifs survive
the within-audit ten-feature correction.  The strongest rows are recorded in
`gdt022_figure_feature_phase_tests.tsv`; overlapping host motifs are not
independent witnesses.  This decomposition is a guard against turning a
small formal motif family into a general semantic category.

The result is nevertheless useful for theory generation: multiple formal
motifs nominated from annotated figure-associated labels recur unusually
often immediately after a DY checkpoint in prose, even after coarse state and
position matching.  A leading generative hypothesis is that the post-DY phase
licenses a restricted reference/index construction family.  The main rival is
selection and register ecology: the anchors were chosen post hoc from a small
visual atlas, and visually derived role names do not identify what their prose
occurrences denote.  The exported examples are prompts for further formal
analysis, not decoded text.

Only the frozen GDT016 inventory is used as manuscript population.  It contains
no f84r row; f84r was not opened, retained, joined, or scored.
No prose group is assigned FIGURE meaning.  No semantic role, referent, morpheme, word,
syntax, sound, language, plaintext, meaning, or translation is confirmed.
"""
    (ROOT / "GDT022_FULL_CENSUS_VISUAL_PHASE_REPORT.md").write_text(report, encoding="utf-8")

    outputs = (
        "gdt022_full_anchor_membership.tsv", "gdt022_role_phase_tests.tsv",
        "gdt022_figure_feature_phase_tests.tsv", "gdt022_figure_postdy_examples.tsv",
        "GDT022_FULL_CENSUS_VISUAL_PHASE_REPORT.md", "GDT021_SAMPLING_CORRECTION.md",
    )
    inputs = (
        "gdt016_group_state_inventory.tsv", "gdt016_result.json", "gdt013_role_anchors.tsv",
        "gdt013_result.json", "gdt021_result.json", "run_gdt013_latent_role_propagation.py",
        "GDT022_FULL_CENSUS_VISUAL_PHASE_METHOD.md",
    )
    result = {
        "schema": "GDT022_FULL_CENSUS_VISUAL_PHASE_RESULT_V1", "status": status,
        "correction": {
            "superseded_experiment": "GDT021", "reason": "GDT013 propagation export capped each anchor at first 40 matches",
            "gdt021_quantitative_inference_valid": False, "audit_trail_preserved": True,
        },
        "inventory_groups": len(inventory), "physical_folios": len({row["physical_folio"] for row in inventory}),
        "anchors": len(anchors), "roles": roles, "tests": total_tests,
        "scope_group_counts": {scope: len(scope_keys[scope]) for scope in scopes},
        "primary": primary, "figure_feature_tests": len(feature_tests),
        "figure_features_adjusted_positive": len(significant_features), "figure_postdy_examples": len(examples),
        "f84r": {"input_contains_rows": False, "opened": False, "retained": False, "joined": False, "scored": False},
        "claim_ceiling": "Complete-census exploratory association between visually nominated formal motifs and anonymous record phase only; no semantic role, referent, morpheme, word, syntax, sound, language, plaintext, meaning, or translation.",
        "inputs": {name: sha(ROOT / name) for name in inputs},
        "implementation": {"run_gdt022_full_census_visual_phase.py": sha(Path(__file__))},
        "outputs": {name: sha(ROOT / name) for name in outputs},
    }
    result["result_content_sha256"] = csha(result)
    (ROOT / "gdt022_result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "primary": primary, "figure_adjusted_positive": len(significant_features)}, sort_keys=True))


if __name__ == "__main__":
    main()
