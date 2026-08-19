#!/usr/bin/env python3
"""Independent reconstruction validator for GDT363 (does not import producer)."""
from __future__ import annotations

import csv
import hashlib
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from tools.vmanus_experiment import GuardedTSV, canonical_json_bytes, sha256_file  # noqa: E402

EXP = ROOT / "experiments/yolo/gdt363_leaf_margin_formal_atlas"
ART = EXP / "artifacts"
PANEL = ART / "gdt363_panel.tsv"
FORMAL = ROOT / "experiments/semantic_assumptions/results/source_sta_family_consensus_groups.tsv"
ATLAS = ART / "gdt363_candidate_atlas.tsv"
NULL = ART / "gdt363_null_maxT.tsv"
RESULT = ART / "gdt363_result.json"
VALIDATION = ART / "gdt363_validation.json"
SEED = 3631901
WORLDS = 4096
RIDGE = 4.0


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def events(rows: list[dict[str, str]]) -> tuple[dict[str, float], dict[str, float]]:
    by_locus: dict[str, list[dict[str, str]]] = defaultdict(list)
    counts: Counter[str] = Counter()
    total_symbols = 0
    for row in rows:
        family = row["family_surface"]; total_symbols += int(row["symbol_count"])
        names = {f"COMPONENT:{char}" for char in set(family)}
        for n in (2, 3):
            names |= {f"WITHIN_GROUP_{n}GRAM:{family[i:i+n]}" for i in range(len(family) - n + 1)}
        names |= {"LEFT_BOUNDARY:" + row["left_boundary_profile"], "RIGHT_BOUNDARY:" + row["right_boundary_profile"]}
        counts.update(names); by_locus[row["locus"]].append(row)
    values = {key: value / len(rows) for key, value in counts.items()}
    locus_counts: Counter[str] = Counter()
    for locus_rows in by_locus.values():
        ordered = sorted(locus_rows, key=lambda row: int(row["consensus_group_index"]))
        first = ordered[0]["family_surface"]; last = ordered[-1]["family_surface"]
        names = set()
        for n in (1, 2, 3):
            if len(first) >= n: names.add(f"FIRST_GROUP_PREFIX_{n}:{first[:n]}")
            if len(last) >= n: names.add(f"LAST_GROUP_SUFFIX_{n}:{last[-n:]}")
        if len(ordered) >= 2: names.add("CONSTRUCTION:MULTIGROUP")
        if len(ordered) >= 3: names.add("CONSTRUCTION:THREE_PLUS_GROUPS")
        locus_counts.update(names)
    values.update({key: value / len(by_locus) for key, value in locus_counts.items()})
    meta = {"group_count": len(rows), "locus_count": len(by_locus), "mean_symbols_per_group": total_symbols / len(rows),
            "label_group_rate": sum(row["kind"] == "L" for row in rows) / len(rows),
            "alternative_group_rate": sum(row["strict_zero_alternative"] == "0" for row in rows) / len(rows)}
    return values, meta


def nuisance(rows: list[dict[str, object]], meta: dict[str, dict[str, float]]) -> np.ndarray:
    cats = {
        "ch": sorted({f"{r['currier']}:{r['hand']}" for r in rows}),
        "quartile": sorted({str(r["folio_rank_quartile"]) for r in rows}),
        "quire": sorted({str(r["quire"]) for r in rows}),
        "side": sorted({str(r["page_side"]) for r in rows}),
    }
    result = []
    for row in rows:
        m = meta[str(row["page"])]
        values = [math.log1p(m["group_count"]), math.log1p(m["locus_count"]), m["mean_symbols_per_group"],
                  m["label_group_rate"], m["alternative_group_rate"]]
        actual = {"ch": f"{row['currier']}:{row['hand']}", "quartile": str(row["folio_rank_quartile"]),
                  "quire": str(row["quire"]), "side": str(row["page_side"])}
        values += [float(actual[key] == value) for key, choices in cats.items() for value in choices]
        result.append(values)
    return np.asarray(result)


def fit(X: np.ndarray, y: np.ndarray, train: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    mean = X[train].mean(0); scale = X[train].std(0); scale[scale < 1e-9] = 1
    Z = np.column_stack([np.ones(len(train)), np.clip((X[train] - mean) / scale, -6, 6)])
    beta = np.zeros(Z.shape[1]); prior = (y[train].sum() + .5) / (len(train) + 1); beta[0] = math.log(prior / (1 - prior))
    pen = np.eye(len(beta)); pen[0, 0] = 0
    for _ in range(60):
        p = 1 / (1 + np.exp(-np.clip(Z @ beta, -30, 30))); w = np.maximum(p * (1 - p), 1e-7)
        gradient = Z.T @ (p - y[train]) + RIDGE * pen @ beta
        hessian = Z.T @ (w[:, None] * Z) + RIDGE * pen + np.eye(len(beta)) * 1e-8
        delta = np.linalg.solve(hessian, gradient); beta -= delta
        if np.linalg.norm(delta) < 1e-9: break
    return mean, scale, beta


def pred(model: tuple[np.ndarray, np.ndarray, np.ndarray], X: np.ndarray) -> np.ndarray:
    mean, scale, beta = model
    Z = np.column_stack([np.ones(len(X)), np.clip((X - mean) / scale, -6, 6)])
    return 1 / (1 + np.exp(-np.clip(Z @ beta, -30, 30)))


def loss(y: np.ndarray, p: np.ndarray) -> float:
    p = np.clip(p, 1e-12, 1 - 1e-12)
    return float(np.sum(-y * np.log2(p) - (1 - y) * np.log2(1 - p)))


def lofo(x: np.ndarray, N: np.ndarray, y: np.ndarray) -> float:
    p0 = np.zeros(len(y)); p1 = np.zeros(len(y)); X = np.column_stack([N, x])
    for held in range(len(y)):
        train = np.asarray([i for i in range(len(y)) if i != held]); test = np.asarray([held])
        p0[held] = pred(fit(N, y, train), N[test])[0]
        p1[held] = pred(fit(X, y, train), X[test])[0]
    return loss(y, p0) - loss(y, p1)


def zscore(F: np.ndarray, y: np.ndarray, strata: list[str]) -> np.ndarray:
    u = np.zeros(F.shape[1]); v = np.zeros(F.shape[1])
    for key in sorted(set(strata)):
        idx = np.asarray([i for i, value in enumerate(strata) if value == key]); n = len(idx); k = y[idx].sum()
        if n < 2 or k <= 0 or k >= n: continue
        X = F[idx]; C = X - X.mean(0); u += C.T @ y[idx]
        v += k * (n - k) / (n * (n - 1)) * np.sum(C * C, axis=0)
    z = np.zeros(F.shape[1]); ok = v > 1e-15; z[ok] = u[ok] / np.sqrt(v[ok]); return z


def main() -> None:
    checks: list[dict[str, object]] = []
    def check(name: str, condition: bool, detail: object = "") -> None:
        checks.append({"name": name, "pass": bool(condition), "detail": detail})
        if not condition: raise AssertionError(f"{name}: {detail}")

    panel = read(PANEL); atlas = read(ATLAS); result = json.loads(RESULT.read_text())
    check("panel_44", len(panel) == 44)
    check("physical_folios_44", len({r['physical_folio'] for r in panel}) == 44)
    check("visual_counts", Counter(r["leaf_margin_state"] for r in panel) == Counter(SMOOTH=29, TOOTHED=13, UNCERTAIN=2))
    allowed = {r["page"] for r in panel}
    reader = GuardedTSV(FORMAL, selector_column="page", allowed_values=allowed,
                        forbidden_prefixes=("f84",), forbidden_action="skip")
    source = list(reader)
    check("source_selected_3075", len(source) == 3075, len(source))
    check("source_covers_44", {r["page"] for r in source} == allowed)
    check("source_no_f84", not any(r["page"].startswith("f84") for r in source))
    by_page: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in source: by_page[row["page"]].append(row)
    values = {}; strict = {}; meta = {}
    for page in allowed:
        values[page], meta[page] = events(by_page[page])
        strict[page], _ = events([r for r in by_page[page] if r["strict_zero_alternative"] == "1"])
    names = sorted(name for name in {n for v in values.values() for n in v}
                   if sum(values[p].get(name, 0) > 0 for p in allowed) >= 5
                   and sum(values[p].get(name, 0) == 0 for p in allowed) >= 5)
    check("feature_count_247", len(names) == 247, len(names))
    check("feature_set_exact", set(names) == {r["formal_feature"] for r in atlas})
    check("exact_family_absent", not any(name.startswith("EXACT_") for name in names))
    rows = [r for r in panel if r["score_eligible"] == "1"]
    y = np.asarray([1.0 if r["leaf_margin_state"] == "TOOTHED" else 0.0 for r in rows])
    F = np.asarray([[values[r["page"]].get(name, 0) for name in names] for r in rows])
    FS = np.asarray([[strict[r["page"]].get(name, 0) for name in names] for r in rows])
    strata = [f"{r['currier']}|{r['folio_rank_quartile']}" for r in rows]
    z = zscore(F, y, strata); zs = zscore(FS, y, strata)
    by_name = {r["formal_feature"]: r for r in atlas}
    check("all_observed_z", all(abs(float(by_name[n]["observed_stratified_z"]) - z[j]) < 5e-10 for j, n in enumerate(names)))
    check("all_strict_z", all(abs(float(by_name[n]["strict_only_stratified_z"]) - zs[j]) < 5e-10 for j, n in enumerate(names)))
    check("all_support", all(int(by_name[n]["support_pages_all44"]) == sum(values[p].get(n, 0) > 0 for p in allowed) for n in names))
    effects = [F[y == 1, j].mean() - F[y == 0, j].mean() for j in range(len(names))]
    check("all_effects", all(abs(float(by_name[n]["toothed_mean_minus_smooth_mean"]) - effects[j]) < 5e-10 for j, n in enumerate(names)))

    rng = np.random.default_rng(SEED); max_values = []; null_matrix = np.zeros((WORLDS, len(names)))
    blocks = [[i for i, value in enumerate(strata) if value == key] for key in sorted(set(strata))]
    for world in range(WORLDS):
        yp = y.copy()
        for idx in blocks: yp[idx] = yp[np.asarray(idx)[rng.permutation(len(idx))]]
        null_matrix[world] = zscore(F, yp, strata); max_values.append(float(np.max(np.abs(null_matrix[world]))))
    stored_null = read(NULL)
    check("null_4096", len(stored_null) == WORLDS)
    check("null_values", all(abs(float(stored_null[i]["max_abs_z"]) - max_values[i]) < 5e-10 for i in range(WORLDS)))
    local = [(1 + int(np.sum(np.abs(null_matrix[:, j]) >= abs(z[j]) - 1e-12))) / (WORLDS + 1) for j in range(len(names))]
    maxp = [(1 + sum(v >= abs(z[j]) - 1e-12 for v in max_values)) / (WORLDS + 1) for j in range(len(names))]
    check("all_local_p", all(abs(float(by_name[n]["local_p"]) - local[j]) < 5e-10 for j, n in enumerate(names)))
    check("all_maxT_p", all(abs(float(by_name[n]["library_maxT_p"]) - maxp[j]) < 5e-10 for j, n in enumerate(names)))
    N = nuisance(rows, meta)
    gains = [lofo(F[:, j], N, y) for j in range(len(names))]
    check("all_lofo_gains", all(abs(float(by_name[n]["lofo_gain_bits"]) - gains[j]) < 5e-8 for j, n in enumerate(names)))
    expected_order = sorted(atlas, key=lambda r: (float(r["library_maxT_p"]), -abs(float(r["observed_stratified_z"])), -float(r["lofo_gain_bits"]), r["formal_feature"]))
    check("rank_order", [int(r["rank"]) for r in expected_order] == list(range(1, len(atlas) + 1)))
    check("no_interesting", not any(r["label"] == "INTERESTING_EXPLORATORY" for r in atlas))
    check("top_abb", atlas[0]["formal_feature"] == "WITHIN_GROUP_3GRAM:ABB", atlas[0]["formal_feature"])
    copy = dict(result); content_hash = copy.pop("content_hash")
    check("result_content_hash", hashlib.sha256(canonical_json_bytes(copy)).hexdigest() == content_hash)
    check("result_top", result["top_candidate"]["candidate_id"] == atlas[0]["candidate_id"])
    check("input_hashes", all(sha256_file(ROOT / rel) == digest for rel, digest in result["inputs"].items()))
    check("implementation_hashes", all(sha256_file(ROOT / rel) == digest for rel, digest in result["implementation"].items()))
    check("output_hashes", all(sha256_file(ROOT / rel) == digest for rel, digest in result["outputs"].items()))
    check("report_claim_ceiling", "does not identify a leaf word" in (EXP / "REPORT.md").read_text())
    check("report_f84_guard", "No f84 row was retained, joined, displayed, or scored" in (EXP / "REPORT.md").read_text())
    check("all_output_pages_no_f84", not any(r["page"].startswith("f84") for r in read(ART / "gdt363_page_summary.tsv")))
    payload = {
        "schema": "GDT363_VALIDATION_V1", "status": "PASS", "checks": checks,
        "check_count": len(checks), "pass_count": sum(bool(c["pass"]) for c in checks),
        "scope": "INDEPENDENT_SOURCE_JOIN_FEATURE_NULL_AND_LOFO_RECONSTRUCTION",
        "result_sha256": sha256_file(RESULT), "result_content_hash": content_hash,
        "validator_sha256": sha256_file(Path(__file__)),
        "documents": {str(path.relative_to(ROOT)): sha256_file(path) for path in (EXP / "METHOD.md", EXP / "REPORT.md")},
        "f84_accessed": False,
    }
    payload["content_hash"] = hashlib.sha256(canonical_json_bytes(payload)).hexdigest()
    VALIDATION.write_bytes(canonical_json_bytes(payload))
    print(f"PASS {payload['pass_count']}/{payload['check_count']}")


if __name__ == "__main__":
    main()
