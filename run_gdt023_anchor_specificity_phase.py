#!/usr/bin/env python3
"""Audit role specificity and state branches behind the GDT022 lead."""
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

from run_gdt022_full_census_visual_phase import csha, formal_features, sha, statistic, write

ROOT = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (ROOT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    inventory = read("gdt016_group_state_inventory.tsv")
    anchors = read("gdt013_role_anchors.tsv")
    assert len(inventory) == 15592 and len(anchors) == 80
    assert not any(row["locus"].startswith("f84r") for row in inventory)
    lookup = {(row["locus"], int(row["group_index"])): row for row in inventory}
    lines: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in inventory:
        lines[row["locus"]].append(row)
    context = {}
    previous = {}
    for locus, line in lines.items():
        line.sort(key=lambda row: int(row["group_index"]))
        after = 0
        for index, row in enumerate(line):
            count = int(row["group_count"])
            frac = (int(row["group_index"]) - 1) / (count - 1) if count > 1 else 0.5
            key = (locus, int(row["group_index"]))
            context[key] = {
                "page": row["page"], "physical_folio": row["physical_folio"],
                "state": row["record_state"], "position_bin": min(3, int(frac * 4)),
                "IMMEDIATE_POST_DY": after,
            }
            previous[key] = line[index - 1] if index else None
            after = int(row["record_state"] == "DY_RESOLUTION")

    feature_roles: dict[tuple[str, str], set[str]] = defaultdict(set)
    matches: dict[tuple[str, str], set[tuple[str, int]]] = {}
    for anchor in anchors:
        pair = (anchor["selected_model"], anchor["formal_feature"])
        feature_roles[pair].add(anchor["role"])
        matches[pair] = {key for key, row in lookup.items() if pair[1] in formal_features(row, pair[0])}
        assert len(matches[pair]) == int(anchor["prose_occurrence_total"])
    figure = sorted(pair for pair, roles in feature_roles.items() if "FIGURE" in roles)
    qjb = ("SOURCE_FAMILY", "F3:QJB")
    kal = ("RESIDUAL_HOST", "H3:kal")
    okal = ("RESIDUAL_HOST", "HOST_EXACT:okal")
    specs = [
        ("FIGURE_ALL_10", figure),
        ("FIGURE_ROLE_UNIQUE", [pair for pair in figure if len(feature_roles[pair]) == 1]),
        ("FIGURE_ROLE_SHARED", [pair for pair in figure if len(feature_roles[pair]) > 1]),
        ("FIGURE_WITHOUT_QJB", [pair for pair in figure if pair != qjb]),
        ("FIGURE_WITHOUT_KAL_OR_OKAL", [pair for pair in figure if pair not in (kal, okal)]),
        ("FIGURE_WITHOUT_QJB_KAL_OKAL", [pair for pair in figure if pair not in (qjb, kal, okal)]),
        ("QJB_ONLY", [qjb]), ("KAL_ONLY", [kal]), ("OKAL_ONLY", [okal]),
    ]
    all_keys = set(lookup)
    folios = sorted({row["physical_folio"] for row in inventory})
    ablations = []
    for name, features in specs:
        positive = set().union(*(matches[pair] for pair in features)) if features else set()
        stat = statistic(all_keys, positive, context, "IMMEDIATE_POST_DY")
        lofo = [statistic(all_keys, positive, context, "IMMEDIATE_POST_DY", folio, False)["effect"] for folio in folios]
        ablations.append({
            "test_id": name, "feature_count": len(features),
            "features": "|".join(model + ":" + feature for model, feature in features),
            "full_occurrences": len(positive), "conditional_effect": f"{stat['effect']:.12f}",
            "observed_postdy": stat["observed"], "expected_postdy": f"{stat['expected']:.12f}",
            "informative_strata": stat["informative_strata"], "exact_p": f"{stat['p']:.12f}",
            "search_adjusted_p_9": f"{min(1.0, float(stat['p']) * len(specs)):.12f}",
            "lofo_positive_effects": sum(value > 0 for value in lofo), "lofo_folios": len(lofo),
            "lofo_min_effect": f"{min(lofo):.12f}", "lofo_max_effect": f"{max(lofo):.12f}",
            "interpretive_scope": "ANNOTATION_CHANNEL_SPECIFICITY_AUDIT_NOT_SEMANTICS",
        })
    write("gdt023_anchor_ablation_tests.tsv", ablations)

    role_rows = []
    for pair in figure:
        anchor_rows = [row for row in anchors if (row["selected_model"], row["formal_feature"]) == pair]
        role_rows.append({
            "anchor_model": pair[0], "formal_feature": pair[1],
            "selected_for_roles": "|".join(sorted(feature_roles[pair])), "selected_role_count": len(feature_roles[pair]),
            "figure_channel_unique": int(feature_roles[pair] == {"FIGURE"}),
            "complete_prose_occurrences": len(matches[pair]),
            "annotated_support_by_role": "|".join(row["role"] + ":" + row["positive_support"] + "/" + row["support"] for row in sorted(anchor_rows, key=lambda row: row["role"])),
            "claim_state": "ANCHOR_SELECTION_PROVENANCE_NOT_ROLE_MEANING",
        })
    write("gdt023_figure_anchor_role_overlap.tsv", role_rows)

    branches = [("QJB", qjb, matches[qjb]), ("KAL", kal, matches[kal]), ("OKAL", okal, matches[okal]), ("KAL_NON_OKAL", kal, matches[kal] - matches[okal])]
    summaries = []
    examples = []
    for name, pair, keys in branches:
        post = {key for key in keys if context[key]["IMMEDIATE_POST_DY"]}
        state_counts = Counter(lookup[key]["record_state"] for key in keys)
        prefix_counts = Counter(lookup[key]["stripped_prefix"] for key in keys)
        summaries.append({
            "branch": name, "formal_feature": pair[0] + ":" + pair[1], "occurrences": len(keys),
            "postdy_occurrences": len(post), "physical_folios": len({lookup[key]["physical_folio"] for key in keys}),
            "dy_resolution_occurrences": state_counts["DY_RESOLUTION"], "al_state_occurrences": state_counts["AL_STATE"],
            "ar_state_occurrences": state_counts["AR_REFERENCE"], "ed_state_occurrences": state_counts["ED_MEDIUM"],
            "q_prefix_occurrences": prefix_counts["q"], "no_prefix_occurrences": prefix_counts["NONE"],
            "claim_state": "ANONYMOUS_POST_CHECKPOINT_STATE_BRANCH_NOT_MEANING",
        })
        for key in sorted(post):
            row = lookup[key]
            prior = previous[key]
            examples.append({
                "branch": name, "locus": key[0], "page": row["page"], "physical_folio": row["physical_folio"],
                "group_index": key[1], "target_token": row["token"], "target_family": row["family_surface"],
                "target_state": row["record_state"], "target_prefix": row["stripped_prefix"],
                "previous_dy_token": prior["token"], "previous_dy_family": prior["family_surface"],
                "claim_state": "CONCRETE_POST_DY_FORMAL_SEQUENCE_NOT_MEANING",
            })
    write("gdt023_postdy_branch_summary.tsv", summaries)
    write("gdt023_postdy_branch_examples.tsv", examples)

    by_test = {row["test_id"]: row for row in ablations}
    status = "SHARED_DIAGRAM_ANCHOR_POST_DY_BRANCHES_PROVISIONAL_FIGURE_SPECIFICITY_FAILED"
    report = f"""# GDT023 anchor-specificity / post-DY branch report

Status: **{status.replace('_', ' ')}**

The corrected GDT022 association is real as a formal concentration but is not
FIGURE-specific.  Nine of the ten FIGURE-nominated features were also selected
from at least one other annotation channel; the sole channel-unique feature is
`H3:olk`, which has effect {float(by_test['FIGURE_ROLE_UNIQUE']['conditional_effect']):+.4f}
and exact p={float(by_test['FIGURE_ROLE_UNIQUE']['exact_p']):.3g}.  The complete
ten-feature set has effect {float(by_test['FIGURE_ALL_10']['conditional_effect']):+.4f}
(p={float(by_test['FIGURE_ALL_10']['exact_p']):.6g}), while removing QJB, KAL,
and OKAL together leaves effect
{float(by_test['FIGURE_WITHOUT_QJB_KAL_OKAL']['conditional_effect']):+.4f}
(p={float(by_test['FIGURE_WITHOUT_QJB_KAL_OKAL']['exact_p']):.3g}).

The three carrying motifs were never annotation-channel-exclusive. QJB was
nominated by FIGURE and WATER/APPARATUS examples; KAL by FIGURE and ARRAY/GROUP;
OKAL by FIGURE, WATER/APPARATUS, and ARRAY/GROUP.  Their prose occurrence sets
also separate cleanly: QJB and KAL overlap at zero groups.  QJB occurs 522 times
on 40 folios, with 449 occurrences in anonymous DY_RESOLUTION and 219 directly
after another DY.  KAL occurs 250 times on 48 folios, with 236 in AL_STATE and
67 directly after DY.  Thus the useful generative refinement is a two-branch
post-checkpoint construction: a QJB-heavy repeated-resolution branch and a
KAL/OKAL-heavy AL-state branch.

The leading abductive interpretation is now narrower and more coherent:
formal patterns learned from several kinds of diagram-associated labels recur
in prose after a checkpoint, plausibly as a generic diagram-item/reference or
indexing construction.  This is better than a FIGURE gloss because it explains
the anchor-channel overlap.  It is still speculative: QJB is heavily entangled
with the already known DY template, KAL and OKAL are nested, and no prose
referent is independently visible.

Only the frozen GDT016 inventory is used; it contains no f84r row.  f84r was
not opened, retained, joined, or scored.  No FIGURE, WATER, ARRAY, object,
referent, morpheme, word, syntax, sound, language, plaintext, meaning, or
translation is assigned.
"""
    (ROOT / "GDT023_ANCHOR_SPECIFICITY_PHASE_REPORT.md").write_text(report, encoding="utf-8")

    outputs = ("gdt023_anchor_ablation_tests.tsv", "gdt023_figure_anchor_role_overlap.tsv", "gdt023_postdy_branch_summary.tsv", "gdt023_postdy_branch_examples.tsv", "GDT023_ANCHOR_SPECIFICITY_PHASE_REPORT.md")
    inputs = ("gdt016_group_state_inventory.tsv", "gdt016_result.json", "gdt013_role_anchors.tsv", "gdt013_result.json", "gdt022_result.json", "GDT023_ANCHOR_SPECIFICITY_PHASE_METHOD.md")
    result = {
        "schema": "GDT023_ANCHOR_SPECIFICITY_PHASE_RESULT_V1", "status": status,
        "inventory_groups": len(inventory), "figure_anchor_features": len(figure),
        "figure_unique_features": sum(feature_roles[pair] == {"FIGURE"} for pair in figure),
        "ablation_tests": len(ablations), "primary_ablation": by_test["FIGURE_ALL_10"],
        "all_three_removed": by_test["FIGURE_WITHOUT_QJB_KAL_OKAL"],
        "qjb_kal_overlap": len(matches[qjb] & matches[kal]), "branches": summaries,
        "leading_hypothesis": "Shared diagram-associated formal motifs occupy two post-DY branches: QJB-heavy repeated resolution and KAL/OKAL-heavy AL state; generic reference/index function is speculative.",
        "f84r": {"input_contains_rows": False, "opened": False, "retained": False, "joined": False, "scored": False},
        "claim_ceiling": "Annotation-channel-shared formal motifs and anonymous post-checkpoint branches only; no semantic role, referent, morpheme, word, syntax, sound, language, plaintext, meaning, or translation.",
        "inputs": {name: sha(ROOT / name) for name in inputs},
        "implementation": {"run_gdt023_anchor_specificity_phase.py": sha(Path(__file__)), "run_gdt022_full_census_visual_phase.py": sha(ROOT / "run_gdt022_full_census_visual_phase.py")},
        "outputs": {name: sha(ROOT / name) for name in outputs},
    }
    result["result_content_sha256"] = csha(result)
    (ROOT / "gdt023_result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "all": by_test["FIGURE_ALL_10"], "removed": by_test["FIGURE_WITHOUT_QJB_KAL_OKAL"], "overlap": result["qjb_kal_overlap"]}, sort_keys=True))


if __name__ == "__main__":
    main()
