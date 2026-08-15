#!/usr/bin/env python3
"""Test whether fixed GDT003 operations explain GDT152 raw-string witnesses."""
import csv
import hashlib
import itertools
import json
from collections import Counter, deque
from pathlib import Path

R = Path(__file__).resolve().parent
QUERIES = R / "gdt152_relation_queries.tsv"
TOKENS = R / "gdt062_right_family_inventory.tsv"
TRANSFORMS = R / "gdt003_transformations.tsv"
PARENT = R / "gdt152_result.json"
METHOD = R / "GDT153_OWNED_LABEL_TRANSFORMATION_WITNESS_METHOD.md"
REPORT = R / "GDT153_OWNED_LABEL_TRANSFORMATION_WITNESS_REPORT.md"
ATLAS = R / "gdt153_transformation_witness_atlas.tsv"
ASSIGN = R / "gdt153_assignment_results.tsv"
COUNTER = R / "gdt153_counterexamples.tsv"
RESULT = R / "gdt153_result.json"
EDITIONS = ("ZL3b", "IT2a", "RF1b")
MEASURES = ("RAW_EDIT", "GDT003_MACRO_EDIT", "GDT003_EXACT_DEPTH2")
EXPECTED = (
    "PREPEND_Q", "INITIAL_D_TO_S", "INITIAL_O_TO_OT", "APPEND_DY",
    "APPEND_DAL", "APPEND_DAR", "FINAL_DAL_TO_DAR",
    "FINAL_DAL_TO_DY", "FINAL_DAR_TO_DY",
)


def read(path):
    with path.open(encoding="utf8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path, rows):
    with path.open("w", encoding="utf8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def csha(value):
    data = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
    return hashlib.sha256(data).hexdigest()


def edit(a, b):
    previous = list(range(len(b) + 1))
    for i, left in enumerate(a, 1):
        current = [i]
        for j, right in enumerate(b, 1):
            current.append(min(current[-1] + 1, previous[j] + 1, previous[j - 1] + (left != right)))
        previous = current
    return previous[-1]


def trigrams(value):
    value = "^" + value + "$"
    return Counter(value[i:i + 3] for i in range(max(1, len(value) - 2)))


def jac(a, b):
    left, right = trigrams(a), trigrams(b); keys = set(left) | set(right)
    denom = sum(max(left[key], right[key]) for key in keys)
    return sum(min(left[key], right[key]) for key in keys) / denom if denom else 0.0


def neighbors(value):
    """Undirected applications of exactly the nine retained GDT003 contrasts."""
    out = []
    if not value.startswith("q"): out.append(("PREPEND_Q", "q" + value))
    if value.startswith("q") and len(value) > 1: out.append(("INVERSE_PREPEND_Q", value[1:]))
    if value.startswith("d"): out.append(("INITIAL_D_TO_S", "s" + value[1:]))
    if value.startswith("s"): out.append(("INVERSE_INITIAL_D_TO_S", "d" + value[1:]))
    if value.startswith("o") and not value.startswith("ot"): out.append(("INITIAL_O_TO_OT", "ot" + value[1:]))
    if value.startswith("ot"): out.append(("INVERSE_INITIAL_O_TO_OT", "o" + value[2:]))
    for suffix in ("dy", "dal", "dar"):
        out.append(("APPEND_" + suffix.upper(), value + suffix))
        if value.endswith(suffix) and len(value) > len(suffix):
            out.append(("INVERSE_APPEND_" + suffix.upper(), value[:-len(suffix)]))
    for old, new, name in (("dal", "dar", "FINAL_DAL_TO_DAR"),
                           ("dal", "dy", "FINAL_DAL_TO_DY"),
                           ("dar", "dy", "FINAL_DAR_TO_DY")):
        if value.endswith(old) and len(value) > len(old): out.append((name, value[:-len(old)] + new))
        if value.endswith(new) and len(value) > len(new): out.append(("INVERSE_" + name, value[:-len(new)] + old))
    return out


def variants(value, max_depth=2):
    found = {value: (0, ())}; queue = deque([value])
    while queue:
        current = queue.popleft(); depth, path = found[current]
        if depth == max_depth: continue
        for name, nxt in neighbors(current):
            candidate = (depth + 1, path + (name,))
            if nxt not in found or candidate < found[nxt]:
                found[nxt] = candidate; queue.append(nxt)
    return found


def main():
    transform_rows = read(TRANSFORMS)
    retained = tuple(row["transformation"] for row in transform_rows if row["retained_for_prediction"] == "1")
    assert retained == EXPECTED
    queries = read(QUERIES)
    relation_ids = sorted({row["relation_id"] for row in queries})
    targets = [next(row["target_page"] for row in queries if row["relation_id"] == rid) for rid in relation_ids]
    assert len(queries) == 15 and len(relation_ids) == len(set(targets)) == 5
    assert {row["edition"] for row in queries} == set(EDITIONS)
    assert not any(row["label_locus"].startswith("f84") or row["target_page"].startswith("f84") for row in queries)
    target_set = set(targets); page_rows = {page: [] for page in targets}
    with TOKENS.open(encoding="utf8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["page"] in target_set:
                assert not row["page"].startswith("f84")
                page_rows[row["page"]].append(row)
    assert all(page_rows.values())

    atlas_rows = []; assign_rows = []; summaries = {}
    permutations = list(itertools.permutations(range(5)))
    for edition in EDITIONS:
        by_relation = {row["relation_id"]: row for row in queries if row["edition"] == edition}
        matrices = {measure: [[0.0] * 5 for _ in range(5)] for measure in MEASURES}
        for i, rid in enumerate(relation_ids):
            query = by_relation[rid]; token = query["token"]; transformed = variants(token)
            for j, page in enumerate(targets):
                raw_candidates = sorted((edit(token, row["token"]), row["token"], row["locus"], jac(token, row["token"])) for row in page_rows[page])
                raw_distance, raw_token, raw_locus, raw_jac = raw_candidates[0]
                macro_candidates = []
                exact_candidates = []
                for variant, (depth, path) in transformed.items():
                    for row in page_rows[page]:
                        residual = edit(variant, row["token"])
                        macro_candidates.append((depth + residual, depth, residual, row["token"], row["locus"], path, variant))
                        if residual == 0: exact_candidates.append((depth, row["token"], row["locus"], path, variant))
                macro_cost, macro_depth, residual, macro_token, macro_locus, macro_path, macro_variant = sorted(macro_candidates)[0]
                exact = sorted(exact_candidates)[0] if exact_candidates else None
                matrices["RAW_EDIT"][i][j] = -float(raw_distance)
                matrices["GDT003_MACRO_EDIT"][i][j] = -float(macro_cost)
                matrices["GDT003_EXACT_DEPTH2"][i][j] = 1.0 if exact else 0.0
                atlas_rows.append({
                    "edition": edition, "relation_id": rid, "label_locus": query["label_locus"],
                    "label_token": token, "candidate_target_page": page, "is_true_target": int(i == j),
                    "raw_best_token": raw_token, "raw_best_locus": raw_locus,
                    "raw_edit_distance": raw_distance, "raw_char3_jaccard": f"{raw_jac:.12g}",
                    "macro_best_token": macro_token, "macro_best_locus": macro_locus,
                    "macro_cost": macro_cost, "macro_operation_depth": macro_depth,
                    "macro_residual_edit": residual, "macro_transformed_query": macro_variant,
                    "macro_operation_path": ";".join(macro_path) if macro_path else "NONE",
                    "macro_improvement_over_raw_edit": raw_distance - macro_cost,
                    "exact_depth2_reachable": int(exact is not None),
                    "exact_operation_depth": exact[0] if exact else "NA",
                    "exact_operation_path": ";".join(exact[3]) if exact else "NA",
                    "evidence_status": "POSTHOC_DISPLAY_STRING_WITNESS",
                })
        for measure in MEASURES:
            matrix = matrices[measure]
            scores = [sum(matrix[i][perm[i]] for i in range(5)) for perm in permutations]
            true = scores[0]
            row_ranks = [1 + sum(value > matrix[i][i] + 1e-12 for value in matrix[i]) for i in range(5)]
            summary = {
                "edition": edition, "measure": measure, "relations": 5, "assignments": 120,
                "true_assignment_score": f"{true:.12g}",
                "true_assignment_rank": 1 + sum(value > true + 1e-12 for value in scores),
                "inclusive_assignment_tail": f"{sum(value >= true - 1e-12 for value in scores) / 120:.12g}",
                "true_row_ranks": ",".join(map(str, row_ranks)),
                "true_target_exact_paths": sum(matrix[i][i] > 0 for i in range(5)) if measure == "GDT003_EXACT_DEPTH2" else "NA",
            }
            assign_rows.append(summary); summaries[(edition, measure)] = summary
    write(ATLAS, atlas_rows); write(ASSIGN, assign_rows)
    total_exact = sum(int(row["exact_depth2_reachable"]) for row in atlas_rows)
    true_exact = sum(int(row["exact_depth2_reachable"]) for row in atlas_rows if int(row["is_true_target"]))
    improvements = sum(int(row["macro_improvement_over_raw_edit"]) > 0 for row in atlas_rows)
    true_improvements = sum(int(row["macro_improvement_over_raw_edit"]) > 0 for row in atlas_rows if int(row["is_true_target"]))
    zl_raw = summaries[("ZL3b", "RAW_EDIT")]; zl_macro = summaries[("ZL3b", "GDT003_MACRO_EDIT")]
    counter = [
        {"type": "ZERO_TRANSFORM_REACHABILITY", "value": f"{total_exact}_OF_{len(atlas_rows)}_QUERY_PAGE_CELLS", "detail": "No label has an exact depth-two GDT003-operation witness on any candidate page in any alternate reading."},
        {"type": "ZERO_TRUE_TRANSFORM_WITNESS", "value": f"{true_exact}_OF_15_TRUE_READING_RELATIONS", "detail": "No true label/page relation is connected by the fixed operation inventory within depth two."},
        {"type": "NO_TRUE_MACRO_IMPROVEMENT", "value": f"{true_improvements}_OF_15_TRUE_RELATION_READINGS|{improvements}_OF_{len(atlas_rows)}_ALL_CELLS", "detail": "The only improvements are the same RP04 to wrong-page f37v suffix-removal witness in three alternate readings."},
        {"type": "ORDINARY_EDIT_ONLY", "value": f"ZL_RAW_RANK_{zl_raw['true_assignment_rank']}_OF_120|MACRO_RANK_{zl_macro['true_assignment_rank']}_OF_120", "detail": "The best macro paths use zero operations, so the modest edit assignment contains no GDT003-specific contribution."},
        {"type": "PANEL_EXPOSED", "value": "POSTHOC_MECHANISM_AUDIT", "detail": "All five relations, strings, and target pages were already exposed; this is not replication or semantic confirmation."},
        {"type": "DISPLAY_REPRESENTATION", "value": "LOSSY_NEAREST_BASIC", "detail": "The tested strings are the published nearest-basic display view, not source-native phonemes, words, or morphemes."},
    ]
    write(COUNTER, counter)
    status = "GDT003_TRANSFORMATIONS_DO_NOT_EXPLAIN_GDT152_RAW_NEAR_MISS"
    REPORT.write_text(f"""# GDT153 — owned-label transformation witness audit

## Outcome

**{status}**

The fixed nine-operation GDT003 algebra provides **zero exact depth-two
witnesses in {total_exact}/{len(atlas_rows)} label×candidate-page×reading
cells**, including **{true_exact}/15** true relation/readings. Allowing the
operations as one-unit edit macros improves **{improvements}/{len(atlas_rows)}**
cells, but **{true_improvements}/15** true relation/readings. All three
improvements are the same wrong-page RP04 → f37v `-dy`-removal witness.

In ZL3b, the five-way assignment under minimum ordinary edit distance ranks
**{zl_raw['true_assignment_rank']}/120** (inclusive tail
{float(zl_raw['inclusive_assignment_tail']):.3f}); the macro score is the same
numeric assignment score and ranks **{zl_macro['true_assignment_rank']}/120**
(tail {float(zl_macro['inclusive_assignment_tail']):.3f}, with a different tie
multiplicity). The alternate readings do not create a transformation path.

The concrete true-page witnesses are therefore ordinary partial string
overlaps—for example `koldarod` versus `daror`, and `loralody` versus
`qolody`—not instances of the frozen `q`/`d↔s`/`o↔ot`/right-edge operation
inventory. This explains why GDT152's raw-character near miss did not localize
to HPR2 PAGE_HOST or source-family structure.

## Consequence

Do not promote the GDT152 raw rank as evidence that a pharmaceutical label is
a transformed Herbal page address. The result also does not refute global
formal composition: GDT003 already showed many exact rectangles, but its
held-folio predictive advantage did not beat string baselines. Here those
fixed operations simply do not account for the five exposed local relations.

No plant/component identity, address, semantic role, gloss, word, morpheme,
POS, sound, language, plaintext, meaning, or translation follows. f84r was not
retained, joined, scored, targeted, or inspected.
""", encoding="utf8")
    result = {
        "schema": "GDT153_OWNED_LABEL_TRANSFORMATION_WITNESS_RESULT_V1",
        "status": status, "relations": 5, "editions": list(EDITIONS),
        "candidate_pages": 5, "atlas_cells": len(atlas_rows),
        "fixed_operations": list(EXPECTED), "maximum_operation_depth": 2,
        "exact_depth2_cells": total_exact, "true_exact_depth2_cells": true_exact,
        "macro_improvement_cells": improvements, "true_macro_improvement_cells": true_improvements,
        "assignments": assign_rows,
        "interpretation": "The GDT152 raw-string near miss is ordinary edit similarity; none of the frozen GDT003 operations supplies an exact or cost-improving witness.",
        "claim_ceiling": "Post-hoc formal mechanism audit only; no plant/component identity, address, semantic role, gloss, word, morpheme, POS, sound, language, plaintext, meaning, or translation.",
        "f84r": {key: False for key in ("retained", "joined", "scored", "targeted", "inspected")},
        "inputs": {path.name: sha(path) for path in (QUERIES, TOKENS, TRANSFORMS, PARENT)},
        "implementation": {Path(__file__).name: sha(Path(__file__))},
        "outputs": {path.name: sha(path) for path in (ATLAS, ASSIGN, COUNTER)},
        "documents": {METHOD.name: sha(METHOD), REPORT.name: sha(REPORT)},
    }
    result["result_content_sha256"] = csha(result)
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf8")
    print(json.dumps({"status": status, "exact": total_exact, "macro_improvements": improvements,
                      "zl_raw_rank": zl_raw["true_assignment_rank"], "zl_macro_rank": zl_macro["true_assignment_rank"]}, sort_keys=True))


if __name__ == "__main__":
    main()
