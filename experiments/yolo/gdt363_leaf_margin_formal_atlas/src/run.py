#!/usr/bin/env python3
"""GDT363: exploratory page-level leaf-margin / source-family atlas."""
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
FREEZE = ART / "gdt363_freeze.json"
FORMAL = ROOT / "experiments/semantic_assumptions/results/source_sta_family_consensus_groups.tsv"
ATLAS = ART / "gdt363_candidate_atlas.tsv"
PAGES = ART / "gdt363_page_summary.tsv"
NULL = ART / "gdt363_null_maxT.tsv"
COUNTER = ART / "gdt363_counterexamples.tsv"
RESULT = ART / "gdt363_result.json"
REPORT = EXP / "REPORT.md"
WORLDS = 4096
SEED = 3631901
LAMBDA = 4.0


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]], fields: list[str] | None = None) -> None:
    names = fields or list(rows[0])
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=names, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def family_events(rows: list[dict[str, str]]) -> tuple[dict[str, float], dict[str, str]]:
    """Aggregate source-family events without crossing source-group boundaries."""
    groups = len(rows)
    by_locus: dict[str, list[dict[str, str]]] = defaultdict(list)
    group_events: Counter[str] = Counter()
    locus_events: Counter[str] = Counter()
    kinds: Counter[str] = Counter()
    total_symbols = 0
    for row in rows:
        family = row["family_surface"]
        total_symbols += int(row["symbol_count"])
        kinds[row["kind"]] += 1
        events: set[str] = set()
        events.update(f"COMPONENT:{char}" for char in set(family))
        for n in (2, 3):
            events.update(f"WITHIN_GROUP_{n}GRAM:{family[i:i+n]}" for i in range(len(family) - n + 1))
        events.add("LEFT_BOUNDARY:" + row["left_boundary_profile"])
        events.add("RIGHT_BOUNDARY:" + row["right_boundary_profile"])
        for event in events:
            group_events[event] += 1
        by_locus[row["locus"]].append(row)
    for locus_rows in by_locus.values():
        ordered = sorted(locus_rows, key=lambda r: int(r["consensus_group_index"]))
        first = ordered[0]["family_surface"]
        last = ordered[-1]["family_surface"]
        events: set[str] = set()
        for n in (1, 2, 3):
            if len(first) >= n:
                events.add(f"FIRST_GROUP_PREFIX_{n}:{first[:n]}")
            if len(last) >= n:
                events.add(f"LAST_GROUP_SUFFIX_{n}:{last[-n:]}")
        if len(ordered) >= 2:
            events.add("CONSTRUCTION:MULTIGROUP")
        if len(ordered) >= 3:
            events.add("CONSTRUCTION:THREE_PLUS_GROUPS")
        for event in events:
            locus_events[event] += 1
    loci = len(by_locus)
    values = {name: count / groups for name, count in group_events.items()}
    values.update({name: count / loci for name, count in locus_events.items()})
    meta = {
        "group_count": str(groups), "locus_count": str(loci),
        "mean_symbols_per_group": f"{total_symbols / groups:.12f}",
        "label_group_rate": f"{kinds['L'] / groups:.12f}",
        "alternative_group_rate": f"{sum(r['strict_zero_alternative'] == '0' for r in rows) / groups:.12f}",
    }
    return values, meta


def nuisance_matrix(rows: list[dict[str, object]]) -> tuple[np.ndarray, list[str]]:
    cats = {
        "currier_hand": sorted({f"{r['currier']}:{r['hand']}" for r in rows}),
        "quartile": sorted({str(r["folio_rank_quartile"]) for r in rows}),
        "quire": sorted({str(r["quire"]) for r in rows}),
        "side": sorted({str(r["page_side"]) for r in rows}),
    }
    names = ["log_group_count", "log_locus_count", "mean_symbols_per_group", "label_group_rate", "alternative_group_rate"]
    names += [f"{key}={value}" for key, vals in cats.items() for value in vals]
    data = []
    for row in rows:
        vals = [math.log1p(int(str(row["group_count"]))), math.log1p(int(str(row["locus_count"]))),
                float(str(row["mean_symbols_per_group"])), float(str(row["label_group_rate"])),
                float(str(row["alternative_group_rate"]))]
        actual = {"currier_hand": f"{row['currier']}:{row['hand']}", "quartile": str(row["folio_rank_quartile"]),
                  "quire": str(row["quire"]), "side": str(row["page_side"])}
        vals += [float(actual[key] == value) for key, choices in cats.items() for value in choices]
        data.append(vals)
    return np.asarray(data, dtype=float), names


def fit(X: np.ndarray, y: np.ndarray, train: np.ndarray) -> dict[str, np.ndarray]:
    mean = X[train].mean(axis=0)
    scale = X[train].std(axis=0)
    scale[scale < 1e-9] = 1.0
    Z = np.column_stack([np.ones(len(train)), np.clip((X[train] - mean) / scale, -6, 6)])
    beta = np.zeros(Z.shape[1], dtype=float)
    prevalence = (float(y[train].sum()) + 0.5) / (len(train) + 1.0)
    beta[0] = math.log(prevalence / (1 - prevalence))
    penalty = np.eye(len(beta)); penalty[0, 0] = 0.0
    for _ in range(60):
        p = 1.0 / (1.0 + np.exp(-np.clip(Z @ beta, -30, 30)))
        w = np.maximum(p * (1 - p), 1e-7)
        gradient = Z.T @ (p - y[train]) + LAMBDA * (penalty @ beta)
        hessian = Z.T @ (w[:, None] * Z) + LAMBDA * penalty + np.eye(len(beta)) * 1e-8
        step = np.linalg.solve(hessian, gradient)
        beta -= step
        if float(np.linalg.norm(step)) < 1e-9:
            break
    return {"mean": mean, "scale": scale, "beta": beta}


def predict(model: dict[str, np.ndarray], X: np.ndarray) -> np.ndarray:
    Z = np.column_stack([np.ones(len(X)), np.clip((X - model["mean"]) / model["scale"], -6, 6)])
    return 1.0 / (1.0 + np.exp(-np.clip(Z @ model["beta"], -30, 30)))


def bitloss(y: np.ndarray, p: np.ndarray) -> float:
    p = np.clip(p, 1e-12, 1 - 1e-12)
    return float(np.sum(-y * np.log2(p) - (1 - y) * np.log2(1 - p)))


def auc(y: np.ndarray, p: np.ndarray) -> float:
    pos = np.flatnonzero(y == 1); neg = np.flatnonzero(y == 0)
    if not len(pos) or not len(neg):
        return 0.5
    return sum(float(p[i] > p[j]) + 0.5 * float(p[i] == p[j]) for i in pos for j in neg) / (len(pos) * len(neg))


def lofo(feature: np.ndarray, nuisance: np.ndarray, y: np.ndarray) -> tuple[float, float, int, str]:
    base_predictions = np.zeros(len(y)); full_predictions = np.zeros(len(y)); details = []
    for held in range(len(y)):
        train = np.asarray([i for i in range(len(y)) if i != held], dtype=int)
        test = np.asarray([held], dtype=int)
        base = fit(nuisance, y, train)
        full_x = np.column_stack([nuisance, feature])
        full = fit(full_x, y, train)
        p0 = float(predict(base, nuisance[test])[0]); p1 = float(predict(full, full_x[test])[0])
        base_predictions[held] = p0; full_predictions[held] = p1
        yy = int(y[held])
        gain = math.log2((p1 if yy else 1 - p1) / (p0 if yy else 1 - p0))
        details.append(f"{gain:.8f}")
    gains = np.asarray([float(x) for x in details])
    return bitloss(y, base_predictions) - bitloss(y, full_predictions), auc(y, full_predictions), int((gains > 0).sum()), ";".join(details)


def score_z(F: np.ndarray, y: np.ndarray, strata: list[str]) -> tuple[np.ndarray, np.ndarray]:
    u = np.zeros(F.shape[1]); v = np.zeros(F.shape[1])
    for key in sorted(set(strata)):
        idx = np.asarray([i for i, value in enumerate(strata) if value == key], dtype=int)
        n = len(idx); k = float(y[idx].sum())
        if n < 2 or k <= 0 or k >= n:
            continue
        X = F[idx]; centered = X - X.mean(axis=0)
        u += centered.T @ y[idx]
        v += k * (n - k) / (n * (n - 1)) * np.sum(centered * centered, axis=0)
    z = np.zeros(F.shape[1]); ok = v > 1e-15; z[ok] = u[ok] / np.sqrt(v[ok])
    return z, v


def main() -> None:
    ART.mkdir(parents=True, exist_ok=True)
    panel = read(PANEL)
    allowed = {row["page"] for row in panel}
    guarded = GuardedTSV(FORMAL, selector_column="page", allowed_values=allowed,
                         forbidden_prefixes=("f84",), forbidden_action="skip")
    formal_rows = list(guarded)
    if any(row["page"].startswith("f84") for row in formal_rows):
        raise RuntimeError("f84 reached formal parser")
    by_page: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in formal_rows:
        by_page[row["page"]].append(row)
    if set(by_page) != allowed:
        raise AssertionError(sorted(allowed - set(by_page)))

    page_features: dict[str, dict[str, float]] = {}
    strict_features: dict[str, dict[str, float]] = {}
    page_meta: dict[str, dict[str, str]] = {}
    for page in sorted(allowed):
        page_features[page], page_meta[page] = family_events(by_page[page])
        strict_rows = [row for row in by_page[page] if row["strict_zero_alternative"] == "1"]
        strict_features[page], _ = family_events(strict_rows)

    # Feature admission is state-blind and uses the complete 44-page frozen panel.
    all_names = sorted({name for values in page_features.values() for name in values})
    feature_names = [name for name in all_names
                     if sum(page_features[p].get(name, 0.0) > 0 for p in allowed) >= 5
                     and sum(page_features[p].get(name, 0.0) == 0 for p in allowed) >= 5]
    if any(name.startswith("EXACT_") for name in feature_names):
        raise AssertionError("exact family leaked")

    eligible = []
    for row in panel:
        meta = page_meta[row["page"]]
        eligible.append({**row, **meta})
    page_rows = [{**row, **page_meta[row["page"]]} for row in panel]
    write(PAGES, page_rows)
    analysis_rows = [row for row in eligible if row["score_eligible"] == "1"]
    y = np.asarray([1.0 if row["leaf_margin_state"] == "TOOTHED" else 0.0 for row in analysis_rows])
    nuisance, nuisance_names = nuisance_matrix(analysis_rows)
    F = np.asarray([[page_features[row["page"]].get(name, 0.0) for name in feature_names] for row in analysis_rows])
    FS = np.asarray([[strict_features[row["page"]].get(name, 0.0) for name in feature_names] for row in analysis_rows])
    strata = [f"{row['currier']}|{row['folio_rank_quartile']}" for row in analysis_rows]
    observed_z, variances = score_z(F, y, strata)
    strict_z, _ = score_z(FS, y, strata)

    rng = np.random.default_rng(SEED)
    null_z = np.zeros((WORLDS, len(feature_names)))
    null_rows = []
    strata_indices = [[i for i, key2 in enumerate(strata) if key2 == key] for key in sorted(set(strata))]
    mobile = sum(len(idx) for idx in strata_indices if 0 < y[idx].sum() < len(idx))
    for world in range(WORLDS):
        yp = y.copy()
        for idx in strata_indices:
            yp[idx] = yp[np.asarray(idx)[rng.permutation(len(idx))]]
        null_z[world], _ = score_z(F, yp, strata)
        null_rows.append({"world": world + 1, "max_abs_z": f"{np.max(np.abs(null_z[world])):.12f}"})
    write(NULL, null_rows)
    max_abs = np.max(np.abs(null_z), axis=1)

    candidates = []
    for j, name in enumerate(feature_names):
        x = F[:, j]
        xs = FS[:, j]
        overall = float(x[y == 1].mean() - x[y == 0].mean())
        strict_effect = float(xs[y == 1].mean() - xs[y == 0].mean())
        effects = {}
        for currier in ("A", "B"):
            idx = np.asarray([i for i, row in enumerate(analysis_rows) if row["currier"] == currier])
            effects[currier] = float(x[idx][y[idx] == 1].mean() - x[idx][y[idx] == 0].mean())
        quire_effects = []
        for quire in sorted({str(row["quire"]) for row in analysis_rows}):
            idx = np.asarray([i for i, row in enumerate(analysis_rows) if row["quire"] != quire])
            if len(set(y[idx])) == 2:
                quire_effects.append(float(x[idx][y[idx] == 1].mean() - x[idx][y[idx] == 0].mean()))
        direction = 1 if overall > 0 else -1 if overall < 0 else 0
        cross_currier = direction != 0 and all((effects[c] > 0) == (direction > 0) and effects[c] != 0 for c in ("A", "B"))
        quire_stable = direction != 0 and all((v > 0) == (direction > 0) and v != 0 for v in quire_effects)
        gain, held_auc, positive_folds, fold_details = lofo(x, nuisance, y)
        local_p = (1 + int(np.sum(np.abs(null_z[:, j]) >= abs(observed_z[j]) - 1e-12))) / (WORLDS + 1)
        max_p = (1 + int(np.sum(max_abs >= abs(observed_z[j]) - 1e-12))) / (WORLDS + 1)
        support = sum(page_features[p].get(name, 0.0) > 0 for p in allowed)
        selector_paid = gain - math.log2(len(feature_names))
        if gain > 0 and cross_currier and quire_stable and support >= 8 and max_p <= 0.20:
            label = "INTERESTING_EXPLORATORY"
        elif gain > 0 and local_p <= 0.10 and (not cross_currier or not quire_stable):
            label = "LIKELY_REGISTER_OR_LAYOUT_CONFOUND"
        elif gain > 0:
            label = "WEAK"
        else:
            label = "NO_SIGNAL"
        candidates.append({
            "candidate_id": hashlib.sha256(name.encode()).hexdigest()[:16], "formal_feature": name,
            "feature_type": name.split(":", 1)[0], "support_pages_all44": support,
            "absence_pages_all44": 44 - support, "toothed_mean_minus_smooth_mean": f"{overall:.12f}",
            "currier_A_effect": f"{effects['A']:.12f}", "currier_B_effect": f"{effects['B']:.12f}",
            "cross_currier_direction_stable": str(cross_currier).lower(),
            "leave_one_quire_direction_stable": str(quire_stable).lower(),
            "strict_only_effect": f"{strict_effect:.12f}", "observed_stratified_z": f"{observed_z[j]:.12f}",
            "strict_only_stratified_z": f"{strict_z[j]:.12f}", "local_p": f"{local_p:.12f}",
            "library_maxT_p": f"{max_p:.12f}", "lofo_gain_bits": f"{gain:.12f}",
            "selector_paid_gain_bits": f"{selector_paid:.12f}", "lofo_auc": f"{held_auc:.12f}",
            "positive_folds": positive_folds, "total_folds": len(y), "fold_gains": fold_details,
            "label": label,
        })
    candidates.sort(key=lambda row: (float(row["library_maxT_p"]), -abs(float(row["observed_stratified_z"])), -float(row["lofo_gain_bits"]), row["formal_feature"]))
    for rank, row in enumerate(candidates, 1):
        row["rank"] = rank
    fields = ["rank"] + [key for key in candidates[0] if key != "rank"]
    write(ATLAS, candidates, fields)

    counterexamples = []
    for candidate in candidates[:10]:
        name = str(candidate["formal_feature"]); direction = float(candidate["toothed_mean_minus_smooth_mean"])
        scored = sorted(((page_features[row["page"]].get(name, 0.0), row) for row in analysis_rows), key=lambda z: z[0])
        bad = ([item for item in scored if item[1]["leaf_margin_state"] == "TOOTHED"][:2] +
               [item for item in reversed(scored) if item[1]["leaf_margin_state"] == "SMOOTH"][:2]) if direction >= 0 else (
              [item for item in reversed(scored) if item[1]["leaf_margin_state"] == "TOOTHED"][:2] +
              [item for item in scored if item[1]["leaf_margin_state"] == "SMOOTH"][:2])
        for value, row in bad:
            counterexamples.append({"candidate_id": candidate["candidate_id"], "rank": candidate["rank"],
                                    "formal_feature": name, "page": row["page"], "currier": row["currier"],
                                    "leaf_margin_state": row["leaf_margin_state"], "feature_rate": f"{value:.12f}",
                                    "reason": "OPPOSITE_CLASS_EXTREME_FOR_OBSERVED_DIRECTION"})
    write(COUNTER, counterexamples)

    label_counts = Counter(str(row["label"]) for row in candidates)
    top = candidates[0]
    payload = {
        "schema": "GDT363_RESULT_V1", "status": "EXPLORATORY_ATLAS_COMPLETE",
        "panel": {"pages": 44, "eligible": 42, "smooth": 29, "toothed": 13, "uncertain": 2,
                  "formal_groups": len(formal_rows), "formal_pages": len(by_page), "mobile_permutation_pages": mobile},
        "feature_library": {"admitted": len(feature_names), "support_min": 5, "absence_min": 5,
                            "exact_family_expressions": 0, "nuisance_columns": nuisance_names},
        "ranking_labels": dict(sorted(label_counts.items())), "top_candidate": top,
        "null": {"worlds": WORLDS, "seed": SEED, "strata": "CURRIER_X_FOLIO_RANK_QUARTILE",
                 "interpretation": "EXPLORATORY_COARSE_STRATIFIED_MAXT_NOT_EXACT_OPPORTUNITY_MATCH"},
        "historical_procedure": {"LM002_capacity_stop_preserved": True, "LM002_status_rewritten": False},
        "access": {"new_images_opened": False, "f84_rows_parsed_retained_joined_scored": False,
                   "f84_forbidden_rows_skipped_before_parse": guarded.stats.skipped_forbidden,
                   "selected_formal_rows": guarded.stats.selected},
        "inputs": {str(path.relative_to(ROOT)): sha256_file(path) for path in (PANEL, FREEZE, FORMAL, EXP / "METHOD.md")},
        "implementation": {str(Path(__file__).relative_to(ROOT)): sha256_file(Path(__file__))},
        "outputs": {str(path.relative_to(ROOT)): sha256_file(path) for path in (ATLAS, PAGES, NULL, COUNTER)},
        "claim_ceiling": "EXPLORATORY_PAGE_LEVEL_ANONYMOUS_FORMAL_ASSOCIATION_ONLY_NO_LEXICAL_OR_SEMANTIC_CLAIM",
    }
    payload["content_hash"] = hashlib.sha256(canonical_json_bytes(payload)).hexdigest()
    RESULT.write_bytes(canonical_json_bytes(payload))

    top_rows = candidates[:12]
    lines = [
        "# GDT363 leaf-margin / source-family atlas report", "",
        f"Status: **{payload['status']}**.", "",
        "## Outcome", "",
        f"The frozen 44-folio panel yielded **{len(feature_names)}** state-blind anonymous family/construction features. "
        f"No images were reopened. The binary score used 42 pages (29 SMOOTH, 13 TOOTHED); two UNCERTAIN pages remained unscored.", "",
        f"The top-ranked feature is `{top['formal_feature']}`: toothed-minus-smooth rate {float(top['toothed_mean_minus_smooth_mean']):+.4f}, "
        f"LOFO gain {float(top['lofo_gain_bits']):+.3f} bits, local p={float(top['local_p']):.4f}, "
        f"complete-library maxT p={float(top['library_maxT_p']):.4f}, label **{top['label']}**.", "",
        "| rank | anonymous formal feature | effect | LOFO gain bits | local p | maxT p | A/B effects | label |", "|---:|---|---:|---:|---:|---:|---|---|",
    ]
    for row in top_rows:
        lines.append(f"| {row['rank']} | `{row['formal_feature']}` | {float(row['toothed_mean_minus_smooth_mean']):+.4f} | {float(row['lofo_gain_bits']):+.3f} | {float(row['local_p']):.4f} | {float(row['library_maxT_p']):.4f} | {float(row['currier_A_effect']):+.3f} / {float(row['currier_B_effect']):+.3f} | {row['label']} |")
    lines += [
        "", "## Interpretation", "",
        "This is deliberately permissive hypothesis generation. One-sided pages and uncertain pages remain part of the inventory; controls rank suspicion rather than terminate discovery. A page-level association can still be caused by plant illustrator practice, Currier/hand, quire, text volume, or page ecology. The exact family/member identity and all lexical representations were excluded.", "",
        "The historical LM002 synthetic-calibration stop remains a true record of that validation-first workflow; it is not rewritten as a pass. GDT363 instead reports what the already acquired visual observations suggest under a broad anonymous formal atlas.", "",
        "## Provenance and seal", "",
        f"The guarded source reader retained {guarded.stats.selected} whitelisted family-consensus rows and skipped {guarded.stats.skipped_forbidden} f84-prefixed rows before formal-field parsing. No f84 row was retained, joined, displayed, or scored. No new image or catalogue was opened.", "",
        "## Claim ceiling", "",
        "At most, this experiment nominates exploratory page-level covariation between visible leaf-margin class and anonymous source-family distributions. It does not identify a leaf word, plant, lexeme, morpheme, part of speech, sound, language, plaintext, meaning, or translation.", "",
    ]
    REPORT.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
