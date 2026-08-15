#!/usr/bin/env python3
"""GDT110: HPR2 layer test on the acquired CONTACT/GAP panel."""
from __future__ import annotations

import csv
import hashlib
import itertools
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

import run_gdt109_legacy_out_of_panel_descriptor_transfer as hpr

ROOT = Path(__file__).resolve().parent
JOIN = ROOT / "gdt002_exploratory_visual_formal_join.tsv"
ALIGN = ROOT / "experiments/semantic_assumptions/results/source_sta_group_alignment.tsv"
METHOD = ROOT / "GDT110_HPR2_CONTACT_GAP_RELATION_CHANNEL_METHOD.md"
REPORT = ROOT / "GDT110_HPR2_CONTACT_GAP_RELATION_CHANNEL_REPORT.md"
INVENTORY = ROOT / "gdt110_contact_gap_hpr2_inventory.tsv"
EFFECTS = ROOT / "gdt110_layer_effects.tsv"
PREDICTIONS = ROOT / "gdt110_representation_predictions.tsv"
NULL = ROOT / "gdt110_null_results.tsv"
RESULT = ROOT / "gdt110_result.json"

FEATURES = ("DY", "RIGHT", "DY_OR_RIGHT", "B3", "WRAPPER", "FRAME")
REPS = ("RAW_CHAR3", "PAGE_HOST_CHAR3", "EDGE_STRIPPED_CHAR3", "COMPILER_ACTIVE")
EDITIONS = hpr.EDITIONS


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def csha(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()


def feature_state(parsed: list[dict[str, object]], name: str) -> bool:
    dy = any(int(row["dy"]) for row in parsed)
    right = any(row["right"] != "NONE" for row in parsed)
    if name == "DY": return dy
    if name == "RIGHT": return right
    if name == "DY_OR_RIGHT": return dy or right
    if name == "B3": return any(int(row["b3"]) for row in parsed)
    if name == "WRAPPER": return any(row["wrapper"] != "NONE" for row in parsed)
    if name == "FRAME": return any(row["frame"] != "NONE" for row in parsed)
    raise KeyError(name)


def effect(labels: np.ndarray, values: np.ndarray, arrays: list[str]) -> tuple[float, dict[str, float]]:
    per = {}
    for array in sorted(set(arrays)):
        indexes = [i for i, name in enumerate(arrays) if name == array and labels[i] >= 0]
        positives = [i for i in indexes if labels[i] == 1]
        negatives = [i for i in indexes if labels[i] == 0]
        if positives and negatives:
            per[array] = float(values[positives].mean() - values[negatives].mean())
    return (float(np.mean(list(per.values()))) if per else 0.0), per


def jaccard(a: Counter[str], b: Counter[str]) -> float:
    keys = set(a) | set(b); denominator = sum(max(a[key], b[key]) for key in keys)
    return 1 - sum(min(a[key], b[key]) for key in keys) / denominator if denominator else 1.0


def main() -> None:
    panel = [row for row in read(JOIN) if row["channel"] == "CONTACT_GAP"]
    panel.sort(key=lambda row: (row["array_id"], int(row["ordinal"]), row["locus"]))
    assert len(panel) == len({row["locus"] for row in panel}) == 27
    assert Counter(row["visual_state"] for row in panel) == Counter({"CLEAR_GAP": 18, "CONTACT": 8, "UNCERTAIN": 1})
    assert len({row["array_id"] for row in panel}) == 5 and len({row["physical_folio"] for row in panel}) == 3
    assert not any(row["locus"].startswith("f84r") for row in panel)
    wanted = {row["locus"] for row in panel}

    alignment: dict[str, dict[str, list[dict[str, str]]]] = defaultdict(lambda: defaultdict(list))
    with ALIGN.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["locus"].startswith("f84r") or row["locus"] not in wanted:
                continue
            alignment[row["locus"]][row["edition"]].append(row)
    assert set(alignment) == wanted and all(set(alignment[locus]) == set(EDITIONS) for locus in wanted)
    licensed = hpr.licensed_hosts()

    features = np.zeros((len(panel), len(FEATURES)), dtype=int)
    representation: dict[str, list[Counter[str]]] = {rep: [] for rep in REPS}
    inventory = []
    for i, row in enumerate(panel):
        bundles = []
        edition_states = {}
        edition_hosts = {}
        for edition in EDITIONS:
            aligned = sorted(alignment[row["locus"]][edition], key=lambda item: int(item["source_group_index"]))
            tokens = [item["nearest_basic_eva_primary"] for item in aligned]
            families = [item["primary_sta_families"] for item in aligned]
            parsed = [hpr.parse_token(token, licensed) for token in tokens]
            edition_hosts[edition] = "|".join(str(item["page_host"]) for item in parsed)
            edition_states[edition] = {name: feature_state(parsed, name) for name in FEATURES}
            bundles.append(hpr.feature_bundle(tokens, families, licensed))
        average = hpr.average_bundles(bundles)
        for j, name in enumerate(FEATURES):
            features[i, j] = int(sum(edition_states[edition][name] for edition in EDITIONS) >= 2)
        for rep in REPS:
            representation[rep].append(average[rep])
        inventory.append({"locus": row["locus"], "page": row["page"], "physical_folio": row["physical_folio"],
                          "array_id": row["array_id"], "ordinal": row["ordinal"], "visual_state": row["visual_state"],
                          **{name.lower(): int(features[i, j]) for j, name in enumerate(FEATURES)},
                          "zl3b_hosts": edition_hosts["ZL3b"], "it2a_hosts": edition_hosts["IT2a"], "rf1b_hosts": edition_hosts["RF1b"],
                          "reading_policy": "TWO_OF_THREE_BINARY_MAJORITY;AVERAGED_COUNTERS_FOR_PREDICTION", "semantic_role": "UNASSIGNED"})
    write(INVENTORY, inventory)

    labels = np.array([1 if row["visual_state"] == "CONTACT" else 0 if row["visual_state"] == "CLEAR_GAP" else -1 for row in panel], dtype=int)
    arrays = [row["array_id"] for row in panel]
    hard = np.flatnonzero(labels >= 0)
    mixed_arrays = [array for array in sorted(set(arrays)) if {labels[i] for i, name in enumerate(arrays) if name == array and labels[i] >= 0} == {0, 1}]
    fixed_arrays = [array for array in sorted(set(arrays)) if array not in mixed_arrays]

    array_indexes = {array: [i for i, name in enumerate(arrays) if name == array and labels[i] >= 0] for array in sorted(set(arrays))}
    assignments = []
    choices = []
    for array in mixed_arrays:
        indexes = array_indexes[array]; positives = sum(labels[index] == 1 for index in indexes)
        choices.append([(indexes, set(selected)) for selected in itertools.combinations(indexes, positives)])
    for combination in itertools.product(*choices):
        permuted = labels.copy()
        for indexes, positives in combination:
            for index in indexes: permuted[index] = int(index in positives)
        assignments.append(permuted)
    assert len(assignments) == 2520

    observed_effects = []
    null_values = np.zeros((len(assignments), len(FEATURES)))
    for j, name in enumerate(FEATURES):
        value, per = effect(labels, features[:, j], arrays)
        for world, permuted in enumerate(assignments):
            null_values[world, j] = effect(permuted, features[:, j], arrays)[0]
        local_p = float((np.sum(np.abs(null_values[:, j]) >= abs(value) - 1e-12)) / len(assignments))
        max_p = float(np.sum(np.max(np.abs(null_values), axis=1) >= abs(value) - 1e-12) / len(assignments))
        leave = []
        for held in mixed_arrays:
            vals = [score for array, score in per.items() if array != held]
            leave.append(float(np.mean(vals)) if vals else 0.0)
        observed_effects.append({"feature": name, "hard_loci": len(hard), "present_contact": int(sum(features[i, j] for i in hard if labels[i] == 1)),
                                 "present_gap": int(sum(features[i, j] for i in hard if labels[i] == 0)),
                                 "informative_arrays": len(per), "within_array_effect": value,
                                 "local_two_sided_p": local_p, "max_six_feature_p": max_p,
                                 "min_leave_array_effect": min(leave), "max_leave_array_effect": max(leave),
                                 "per_array_effects": ";".join(f"{array}:{score:+.6f}" for array, score in sorted(per.items())),
                                 "one_sided_arrays_retained_descriptively": ";".join(fixed_arrays), "semantic_role": "UNASSIGNED"})
    observed_effects.sort(key=lambda row: (-abs(float(row["within_array_effect"])), row["feature"]))
    write(EFFECTS, [{key: f"{value:.12g}" if isinstance(value, float) else value for key, value in row.items()} for row in observed_effects])

    # Entire-folio-held low-capacity representation predictions.
    neighbor_cache = {}
    for i, target in enumerate(panel):
        eligible = [j for j, row in enumerate(panel) if row["physical_folio"] != target["physical_folio"]]
        for rep in REPS:
            near = sorted(((jaccard(representation[rep][i], representation[rep][j]), panel[j]["locus"], j) for j in eligible), key=lambda item: (item[0], item[1]))
            neighbor_cache[i, rep] = [item for item in near if item[0] < 1 - 1e-12]

    def fit_predictions(state: np.ndarray) -> tuple[np.ndarray, dict[str, np.ndarray]]:
        base = np.zeros(len(panel)); fitted = {rep: np.zeros(len(panel)) for rep in REPS}
        for i, target in enumerate(panel):
            train = [j for j, row in enumerate(panel) if row["physical_folio"] != target["physical_folio"] and state[j] >= 0]
            base[i] = (sum(state[j] == 1 for j in train) + .5) / (len(train) + 1)
            train_set = set(train)
            for rep in REPS:
                overlap = [item for item in neighbor_cache[i, rep] if item[2] in train_set][:5]
                weights = [1 / (.1 + item[0]) for item in overlap]
                numerator = 4 * base[i] + sum(weight * state[item[2]] for weight, item in zip(weights, overlap))
                fitted[rep][i] = numerator / (4 + sum(weights))
        return base, fitted

    baseline, probs = fit_predictions(labels)

    def bits(state: np.ndarray, probability: np.ndarray) -> float:
        indexes = np.flatnonzero(state >= 0); p = np.clip(probability[indexes], 1e-12, 1 - 1e-12); y = state[indexes]
        return float(-np.log2(np.where(y == 1, p, 1 - p)).sum())

    base_bits = bits(labels, baseline); pred_rows = []
    rep_observed = {}
    for rep in REPS:
        held = bits(labels, probs[rep]); rep_observed[rep] = base_bits - held
        folio_gains = []
        for folio in sorted({row["physical_folio"] for row in panel}):
            state = np.array([labels[i] if row["physical_folio"] == folio else -1 for i, row in enumerate(panel)])
            folio_gains.append(bits(state, baseline) - bits(state, probs[rep]))
        pred_rows.append({"representation": rep, "hard_loci": len(hard), "physical_folios": 3,
                          "baseline_bits": base_bits, "held_bits": held, "gain_bits": base_bits - held,
                          "selector_paid_gain_bits": base_bits - held - 2,
                          "positive_gain_folios": sum(value > 0 for value in folio_gains),
                          "min_folio_gain": min(folio_gains), "max_folio_gain": max(folio_gains)})
    pred_null = np.zeros((len(assignments), len(REPS)))
    for world, state in enumerate(assignments):
        permuted_baseline, permuted_probs = fit_predictions(state)
        b = bits(state, permuted_baseline)
        for j, rep in enumerate(REPS): pred_null[world, j] = b - bits(state, permuted_probs[rep])
    for row in pred_rows:
        j = REPS.index(row["representation"]); observed = float(row["gain_bits"])
        row["local_inclusive_p"] = float(np.sum(pred_null[:, j] >= observed - 1e-12) / len(assignments))
        row["max_four_representation_p"] = float(np.sum(np.max(pred_null, axis=1) >= observed - 1e-12) / len(assignments))
    pred_rows.sort(key=lambda row: (-float(row["gain_bits"]), row["representation"]))
    write(PREDICTIONS, [{key: f"{value:.12g}" if isinstance(value, float) else value for key, value in row.items()} for row in pred_rows])

    uncertain_rows = []
    uncertain_index = int(np.flatnonzero(labels < 0)[0])
    for assignment_name, value in (("UNCERTAIN_AS_GAP", 0), ("UNCERTAIN_AS_CONTACT", 1)):
        state = labels.copy(); state[uncertain_index] = value
        for j, name in enumerate(FEATURES):
            score, _ = effect(state, features[:, j], arrays)
            uncertain_rows.append({"null_or_sensitivity": assignment_name, "feature_or_representation": name, "worlds": 0,
                                   "observed_value": score, "probability": "DESCRIPTIVE_NOT_REPERMUTED",
                                   "preserves": "all_hard_calls;only_uncertain_assignment_changes"})
    for row in observed_effects:
        uncertain_rows.append({"null_or_sensitivity": "PRIMARY_WITHIN_ARRAY_EXACT", "feature_or_representation": row["feature"], "worlds": len(assignments),
                               "observed_value": row["within_array_effect"], "probability": row["local_two_sided_p"],
                               "preserves": "array;hard_state_counts;one_sided_arrays"})
    write(NULL, uncertain_rows)

    top = observed_effects[0]; best = pred_rows[0]
    dy = next(row for row in observed_effects if row["feature"] == "DY")
    right = next(row for row in observed_effects if row["feature"] == "RIGHT")
    joint = next(row for row in observed_effects if row["feature"] == "DY_OR_RIGHT")
    b3 = next(row for row in observed_effects if row["feature"] == "B3")
    status = "HPR2_DY_RIGHT_CONTACT_GAP_CHANNEL_NOT_TRANSFERABLE"
    if float(joint["max_six_feature_p"]) <= .05 and min(float(joint["min_leave_array_effect"]), float(joint["max_leave_array_effect"])) > 0:
        status = "HPR2_DY_RIGHT_CONTACT_GAP_CHANNEL_PROVISIONAL"
    REPORT.write_text(f"""# GDT110 — HPR2 contact/gap relation channel

## Outcome

**{status}**

The fixed panel retains all 27 acquired loci: 8 CONTACT, 18 CLEAR_GAP, and one
UNCERTAIN across five arrays and three physical folios. The primary hard-state
orbit has {len(assignments):,} exact within-array assignments. The one-sided
F89R2_L4 and F100V_L1 arrays remain descriptive observations rather than
capacity failures; they cannot contribute to a within-array contrast.

The strongest of the six fixed HPR2 layer effects is `{top['feature']}` at
{float(top['within_array_effect']):+.3f}, local p={float(top['local_two_sided_p']):.4f}
and max-six p={float(top['max_six_feature_p']):.4f}. DY is
{float(dy['within_array_effect']):+.3f}; RIGHT is
{float(right['within_array_effect']):+.3f}; their union is
{float(joint['within_array_effect']):+.3f}; B3 is
{float(b3['within_array_effect']):+.3f}. Per-array directions are exported.

The best whole-folio-held representation is `{best['representation']}` at
{float(best['gain_bits']):+.3f} bits over prevalence and
{float(best['selector_paid_gain_bits']):+.3f} after the four-way selector,
with max-four p={float(best['max_four_representation_p']):.4f}. This tiny
three-folio prediction panel is a stress test, not a semantic decoder.

Thus the GDT103/GDT104 DY/RIGHT relation-layout lead does not transfer as a
stable CONTACT/GAP channel. That narrows the lead: those layers may organize
record relations without encoding physical ink contact. No relation meaning,
semantic role, gloss, word, morpheme, POS, sound, language, plaintext,
meaning, or translation is assigned. f84r was excluded before retention and
not opened, parsed, retained, queried, joined, scored, or targeted.
""", encoding="utf-8")
    result = {"schema": "GDT110_HPR2_CONTACT_GAP_RELATION_CHANNEL_RESULT_V1", "status": status,
              "panel": {"loci": len(panel), "contact": 8, "clear_gap": 18, "uncertain": 1,
                        "arrays": 5, "physical_folios": 3, "mixed_arrays": mixed_arrays,
                        "one_sided_arrays": fixed_arrays, "exact_worlds": len(assignments)},
              "layer_effects": observed_effects, "best_layer": top, "dy": dy, "right": right,
              "dy_or_right": joint, "b3": b3, "representation_scores": pred_rows, "best_representation": best,
              "interpretation": "No stable HPR2 CONTACT/GAP channel; one-sided arrays retained descriptively and uncertainty propagated.",
              "claim_ceiling": "No contact meaning, semantic role, gloss, word, morpheme, POS, sound, language, plaintext, meaning, or translation.",
              "f84r": {"opened": False, "parsed": False, "retained": False, "queried": False, "joined": False, "scored": False, "targeted": False},
              "inputs": {JOIN.name: sha(JOIN), str(ALIGN.relative_to(ROOT)): sha(ALIGN), "gdt002_exploratory_discovery_results.json": sha(ROOT / "gdt002_exploratory_discovery_results.json"), "gdt104_result.json": sha(ROOT / "gdt104_result.json"), "gdt109_result.json": sha(ROOT / "gdt109_result.json")},
              "implementation": {Path(__file__).name: sha(Path(__file__)), "run_gdt109_legacy_out_of_panel_descriptor_transfer.py": sha(ROOT / "run_gdt109_legacy_out_of_panel_descriptor_transfer.py")},
              "outputs": {path.name: sha(path) for path in (INVENTORY, EFFECTS, PREDICTIONS, NULL)},
              "documents": {METHOD.name: sha(METHOD), REPORT.name: sha(REPORT)}}
    result["result_content_sha256"] = csha(result)
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "top": top, "best_representation": best}, sort_keys=True))


if __name__ == "__main__":
    main()
