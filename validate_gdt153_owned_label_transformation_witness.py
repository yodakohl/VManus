#!/usr/bin/env python3
"""Independent reconstruction of GDT153 witnesses and assignments."""
import csv
import hashlib
import itertools
import json
from collections import deque
from pathlib import Path

R = Path(__file__).resolve().parent
Q = R / "gdt152_relation_queries.tsv"; T = R / "gdt062_right_family_inventory.tsv"
X = R / "gdt003_transformations.tsv"; A = R / "gdt153_transformation_witness_atlas.tsv"
S = R / "gdt153_assignment_results.tsv"; RESULT = R / "gdt153_result.json"
OUT = R / "gdt153_validation.json"
EDITIONS = ("ZL3b", "IT2a", "RF1b")
EXPECTED = ("PREPEND_Q", "INITIAL_D_TO_S", "INITIAL_O_TO_OT", "APPEND_DY", "APPEND_DAL", "APPEND_DAR", "FINAL_DAL_TO_DAR", "FINAL_DAL_TO_DY", "FINAL_DAR_TO_DY")


def rows(path):
    with path.open(encoding="utf8", newline="") as handle: return list(csv.DictReader(handle, delimiter="\t"))


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def edit(a, b):
    old = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        new = [i]
        for j, y in enumerate(b, 1): new.append(min(new[-1] + 1, old[j] + 1, old[j - 1] + (x != y)))
        old = new
    return old[-1]


def edges(v):
    out = []
    if not v.startswith("q"): out.append(("PREPEND_Q", "q" + v))
    if v.startswith("q") and len(v) > 1: out.append(("INVERSE_PREPEND_Q", v[1:]))
    if v.startswith("d"): out.append(("INITIAL_D_TO_S", "s" + v[1:]))
    if v.startswith("s"): out.append(("INVERSE_INITIAL_D_TO_S", "d" + v[1:]))
    if v.startswith("o") and not v.startswith("ot"): out.append(("INITIAL_O_TO_OT", "ot" + v[1:]))
    if v.startswith("ot"): out.append(("INVERSE_INITIAL_O_TO_OT", "o" + v[2:]))
    for suffix in ("dy", "dal", "dar"):
        out.append(("APPEND_" + suffix.upper(), v + suffix))
        if v.endswith(suffix) and len(v) > len(suffix): out.append(("INVERSE_APPEND_" + suffix.upper(), v[:-len(suffix)]))
    for old, new, name in (("dal", "dar", "FINAL_DAL_TO_DAR"), ("dal", "dy", "FINAL_DAL_TO_DY"), ("dar", "dy", "FINAL_DAR_TO_DY")):
        if v.endswith(old) and len(v) > len(old): out.append((name, v[:-len(old)] + new))
        if v.endswith(new) and len(v) > len(new): out.append(("INVERSE_" + name, v[:-len(new)] + old))
    return out


def variants(v):
    found = {v: (0, ())}; queue = deque([v])
    while queue:
        now = queue.popleft(); depth, path = found[now]
        if depth == 2: continue
        for name, nxt in edges(now):
            candidate = (depth + 1, path + (name,))
            if nxt not in found or candidate < found[nxt]: found[nxt] = candidate; queue.append(nxt)
    return found


def close(a, b): return abs(float(a) - float(b)) <= 5e-12


def main():
    result = json.loads(RESULT.read_text(encoding="utf8")); queries = rows(Q); atlas = rows(A); stored = rows(S)
    retained = tuple(r["transformation"] for r in rows(X) if r["retained_for_prediction"] == "1")
    rids = sorted({r["relation_id"] for r in queries}); targets = [next(r["target_page"] for r in queries if r["relation_id"] == rid) for rid in rids]
    page = {p: [] for p in targets}
    with T.open(encoding="utf8", newline="") as handle:
        for r in csv.DictReader(handle, delimiter="\t"):
            if r["page"] in page: page[r["page"]].append(r)
    rebuilt = {}; summaries = {}
    perms = list(itertools.permutations(range(5)))
    for edition in EDITIONS:
        qmap = {r["relation_id"]: r for r in queries if r["edition"] == edition}
        matrices = {name: [[0.0] * 5 for _ in range(5)] for name in ("RAW_EDIT", "GDT003_MACRO_EDIT", "GDT003_EXACT_DEPTH2")}
        for i, rid in enumerate(rids):
            token = qmap[rid]["token"]; vv = variants(token)
            for j, p in enumerate(targets):
                raw = min((edit(token, r["token"]), r["token"], r["locus"]) for r in page[p])
                macro = min((depth + edit(v, r["token"]), depth, edit(v, r["token"]), r["token"], r["locus"], path, v) for v, (depth, path) in vv.items() for r in page[p])
                exact = [item for item in ((depth, r["token"], r["locus"], path, v) for v, (depth, path) in vv.items() for r in page[p]) if item[1] == item[4]]
                exact = min(exact) if exact else None
                rebuilt[(edition, rid, p)] = (raw, macro, exact)
                matrices["RAW_EDIT"][i][j] = -raw[0]; matrices["GDT003_MACRO_EDIT"][i][j] = -macro[0]; matrices["GDT003_EXACT_DEPTH2"][i][j] = int(exact is not None)
        for name, matrix in matrices.items():
            scores = [sum(matrix[i][perm[i]] for i in range(5)) for perm in perms]; true = scores[0]
            summaries[(edition, name)] = (true, 1 + sum(x > true + 1e-12 for x in scores), sum(x >= true - 1e-12 for x in scores) / 120, [1 + sum(x > matrix[i][i] + 1e-12 for x in matrix[i]) for i in range(5)])
    checks = {}
    checks["schema"] = result["schema"] == "GDT153_OWNED_LABEL_TRANSFORMATION_WITNESS_RESULT_V1"
    checks["status"] = result["status"] == "GDT003_TRANSFORMATIONS_DO_NOT_EXPLAIN_GDT152_RAW_NEAR_MISS"
    checks["operations"] = retained == EXPECTED and result["fixed_operations"] == list(EXPECTED)
    checks["panel"] = len(queries) == 15 and len(atlas) == 75 and len(rids) == len(set(targets)) == 5
    checks["atlas_keys"] = {(r["edition"], r["relation_id"], r["candidate_target_page"]) for r in atlas} == set(rebuilt)
    exact_total = 0; macro_improvements = 0; true_macro_improvements = 0; atlas_ok = True
    for r in atlas:
        raw, macro, exact = rebuilt[(r["edition"], r["relation_id"], r["candidate_target_page"])]
        atlas_ok &= int(r["raw_edit_distance"]) == raw[0] and r["raw_best_token"] == raw[1] and r["raw_best_locus"] == raw[2]
        atlas_ok &= int(r["macro_cost"]) == macro[0] and int(r["macro_operation_depth"]) == macro[1] and int(r["macro_residual_edit"]) == macro[2]
        atlas_ok &= int(r["exact_depth2_reachable"]) == int(exact is not None)
        exact_total += int(exact is not None); macro_improvements += raw[0] > macro[0]
        true_macro_improvements += int(r["is_true_target"]) and raw[0] > macro[0]
    checks["atlas_reconstruction"] = atlas_ok
    smap = {(r["edition"], r["measure"]): r for r in stored}
    checks["assignment_rows"] = len(stored) == 9 and set(smap) == set(summaries)
    for key, (score, rank, tail, rr) in summaries.items():
        r = smap[key]
        checks["assignment_" + "_".join(key)] = close(r["true_assignment_score"], score) and int(r["true_assignment_rank"]) == rank and close(r["inclusive_assignment_tail"], tail) and r["true_row_ranks"] == ",".join(map(str, rr))
    checks["zero_exact"] = exact_total == result["exact_depth2_cells"] == 0 and result["true_exact_depth2_cells"] == 0
    checks["macro_improvement_localization"] = macro_improvements == result["macro_improvement_cells"] == 3 and true_macro_improvements == result["true_macro_improvement_cells"] == 0
    checks["f84_absent"] = not any(r["label_locus"].startswith("f84") or r["target_page"].startswith("f84") for r in queries) and all(v is False for v in result["f84r"].values())
    checks["input_hashes"] = all((R / n).exists() and sha(R / n) == h for n, h in result["inputs"].items())
    checks["implementation_hash"] = all((R / n).exists() and sha(R / n) == h for n, h in result["implementation"].items())
    checks["output_hashes"] = all((R / n).exists() and sha(R / n) == h for n, h in result["outputs"].items())
    checks["document_hashes"] = all((R / n).exists() and sha(R / n) == h for n, h in result["documents"].items())
    content = dict(result); recorded = content.pop("result_content_sha256")
    checks["content_hash"] = hashlib.sha256(json.dumps(content, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()).hexdigest() == recorded
    checks["claim_ceiling"] = all(term in result["claim_ceiling"] for term in ("semantic role", "plaintext", "translation"))
    status = "PASS_INDEPENDENT_OPERATION_GRAPH_WITNESS_AND_120_ASSIGNMENT_RECONSTRUCTION" if all(checks.values()) else "FAIL"
    out = {"schema": "GDT153_OWNED_LABEL_TRANSFORMATION_WITNESS_VALIDATION_V1", "status": status,
           "checks_total": len(checks), "checks_passed": sum(checks.values()), "checks": checks,
           "result_sha256": sha(RESULT), "validator_sha256": sha(Path(__file__))}
    OUT.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf8")
    print(json.dumps({"status": status, "passed": sum(checks.values()), "total": len(checks)}, sort_keys=True))


if __name__ == "__main__": main()
