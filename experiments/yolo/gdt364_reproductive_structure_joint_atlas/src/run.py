#!/usr/bin/env python3
"""GDT364: postexposure three-class Herbal source-family atlas."""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from tools.vmanus_experiment import GuardedTSV, canonical_json_bytes, sha256_file  # noqa: E402

EXP = ROOT / "experiments/yolo/gdt364_reproductive_structure_joint_atlas"
ART = EXP / "artifacts"
PANEL = ART / "gdt364_panel.tsv"
FREEZE = ART / "gdt364_freeze.json"
FORMAL = ROOT / "experiments/semantic_assumptions/results/source_sta_family_consensus_groups.tsv"
GDT363_RUN = ROOT / "experiments/yolo/gdt363_leaf_margin_formal_atlas/src/run.py"
ATLAS = ART / "gdt364_candidate_atlas.tsv"
PAGES = ART / "gdt364_page_summary.tsv"
COUNTER = ART / "gdt364_counterexamples.tsv"
RESULT = ART / "gdt364_result.json"
REPORT = EXP / "REPORT.md"
CLASSES = ["BERRY_NO_CIRCLES", "FLOWER_SIDE", "NO_FRUIT_OR_FLOWER"]
WORLDS = 4096
SEED = 3641901

spec = importlib.util.spec_from_file_location("gdt363_frozen", GDT363_RUN)
if spec is None or spec.loader is None: raise RuntimeError("cannot load frozen GDT363 helpers")
g363 = importlib.util.module_from_spec(spec); spec.loader.exec_module(g363)


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]], fields: list[str] | None = None) -> None:
    names = fields or list(rows[0])
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=names, delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def nuisance(rows: list[dict[str, object]]) -> tuple[np.ndarray, list[str]]:
    cats = {
        "quire": sorted({str(r["quire"]) for r in rows}),
        "side": sorted({str(r["page"])[-1] for r in rows}),
        "pages_on_folio": sorted({str(r["pages_on_physical_folio"]) for r in rows}),
    }
    names = ["log_group_count", "log_locus_count", "mean_symbols", "label_rate", "alternative_rate"]
    names += [f"{key}={value}" for key, vals in cats.items() for value in vals]
    data = []
    for row in rows:
        values = [math.log1p(int(str(row["group_count"]))), math.log1p(int(str(row["locus_count"]))),
                  float(str(row["mean_symbols_per_group"])), float(str(row["label_group_rate"])),
                  float(str(row["alternative_group_rate"]))]
        actual = {"quire": str(row["quire"]), "side": str(row["page"])[-1],
                  "pages_on_folio": str(row["pages_on_physical_folio"])}
        values += [float(actual[key] == value) for key, vals in cats.items() for value in vals]
        data.append(values)
    return np.asarray(data), names


def multiclass_predictions(X: np.ndarray, y: np.ndarray, train: np.ndarray, test: np.ndarray) -> np.ndarray:
    scores = []
    for cls in range(len(CLASSES)):
        binary = (y == cls).astype(float)
        scores.append(g363.predict(g363.fit(X, binary, train), X[test]))
    P = np.column_stack(scores)
    return P / P.sum(axis=1, keepdims=True)


def logloss(y: np.ndarray, P: np.ndarray) -> float:
    return float(np.sum(-np.log2(np.clip(P[np.arange(len(y)), y], 1e-12, 1))))


def lofo(x: np.ndarray, N: np.ndarray, y: np.ndarray, rows: list[dict[str, object]]) -> tuple[float, int, int, int, str]:
    p0 = np.zeros((len(y), len(CLASSES))); p1 = np.zeros_like(p0)
    folds = sorted({str(r["physical_folio"]) for r in rows}, key=lambda f: int(f[1:]))
    details = []; positives = 0
    X = np.column_stack([N, x])
    for held in folds:
        train = np.asarray([i for i, row in enumerate(rows) if row["physical_folio"] != held])
        test = np.asarray([i for i, row in enumerate(rows) if row["physical_folio"] == held])
        p0[test] = multiclass_predictions(N, y, train, test)
        p1[test] = multiclass_predictions(X, y, train, test)
        gain = logloss(y[test], p0[test]) - logloss(y[test], p1[test])
        positives += int(gain > 0); details.append(f"{held}:{gain:.8f}")
    gain = logloss(y, p0) - logloss(y, p1)
    top0 = int(np.sum(np.argmax(p0, axis=1) == y)); top1 = int(np.sum(np.argmax(p1, axis=1) == y))
    return gain, positives, len(folds), top1 - top0, ";".join(details)


def separation(F: np.ndarray, y: np.ndarray, quires: list[str]) -> np.ndarray:
    residual = F.copy()
    for quire in sorted(set(quires)):
        idx = np.asarray([i for i, q in enumerate(quires) if q == quire])
        residual[idx] -= residual[idx].mean(axis=0)
    total = np.sum(residual * residual, axis=0)
    between = np.zeros(F.shape[1])
    for cls in range(len(CLASSES)):
        idx = np.flatnonzero(y == cls)
        if len(idx): between += len(idx) * residual[idx].mean(axis=0) ** 2
    score = np.zeros(F.shape[1]); ok = total > 1e-15; score[ok] = between[ok] / total[ok]
    return score


def permuted_labels(y: np.ndarray, rows: list[dict[str, object]], rng: np.random.Generator) -> np.ndarray:
    by_folio: dict[str, list[int]] = defaultdict(list)
    for i, row in enumerate(rows): by_folio[str(row["physical_folio"])].append(i)
    for idx in by_folio.values(): idx.sort(key=lambda i: str(rows[i]["page"]))
    blocks: dict[tuple[str, int], list[str]] = defaultdict(list)
    for folio, idx in by_folio.items(): blocks[(str(rows[idx[0]]["quire"]), len(idx))].append(folio)
    result = y.copy()
    for folios in blocks.values():
        donors = list(rng.permutation(folios))
        for recipient, donor in zip(folios, donors):
            result[by_folio[recipient]] = y[by_folio[str(donor)]]
    return result


def main() -> None:
    panel = read(PANEL); allowed = {row["page"] for row in panel}
    reader = GuardedTSV(FORMAL, selector_column="page", allowed_values=allowed,
                        forbidden_prefixes=("f84",), forbidden_action="skip")
    source = list(reader)
    if any(row["page"].startswith("f84") for row in source): raise RuntimeError("f84 parsed")
    by_page: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in source: by_page[row["page"]].append(row)
    if set(by_page) != allowed: raise AssertionError(sorted(allowed - set(by_page)))
    values = {}; strict = {}; meta = {}
    for page in allowed:
        values[page], meta[page] = g363.family_events(by_page[page])
        strict[page], _ = g363.family_events([r for r in by_page[page] if r["strict_zero_alternative"] == "1"])
    names = sorted(name for name in {n for v in values.values() for n in v}
                   if sum(values[p].get(name, 0) > 0 for p in allowed) >= 5
                   and sum(values[p].get(name, 0) == 0 for p in allowed) >= 5)
    folio_counts = Counter(row["physical_folio"] for row in panel)
    rows = [{**row, **meta[row["page"]], "pages_on_physical_folio": str(folio_counts[row["physical_folio"]]),
             "currier": by_page[row["page"]][0]["currier"], "hand": by_page[row["page"]][0]["hand"]} for row in panel]
    if {row["currier"] for row in rows} != {"A"}: raise AssertionError("unexpected Currier")
    write(PAGES, rows)
    y = np.asarray([CLASSES.index(row["visual_state"]) for row in rows], dtype=int)
    F = np.asarray([[values[row["page"]].get(name, 0) for name in names] for row in rows])
    FS = np.asarray([[strict[row["page"]].get(name, 0) for name in names] for row in rows])
    N, nuisance_names = nuisance(rows); quires = [str(row["quire"]) for row in rows]
    observed = separation(F, y, quires); strict_score = separation(FS, y, quires)
    capacity_folios: dict[str, list[int]] = defaultdict(list)
    for i, row in enumerate(rows): capacity_folios[str(row["physical_folio"])].append(i)
    capacity_blocks: dict[tuple[str, int], list[str]] = defaultdict(list)
    for folio, idx in capacity_folios.items():
        capacity_blocks[(str(rows[idx[0]]["quire"]), len(idx))].append(folio)
    mobile_folios = mobile_pages = 0
    for folios in capacity_blocks.values():
        vectors = {tuple(y[capacity_folios[folio]]) for folio in folios}
        if len(folios) > 1 and len(vectors) > 1:
            mobile_folios += len(folios); mobile_pages += sum(len(capacity_folios[folio]) for folio in folios)
    rng = np.random.default_rng(SEED); null = np.zeros((WORLDS, len(names)))
    for world in range(WORLDS): null[world] = separation(F, permuted_labels(y, rows, rng), quires)
    null_max = null.max(axis=1)
    candidates = []
    for j, name in enumerate(names):
        x = F[:, j]
        class_means = {cls: float(x[y == k].mean()) for k, cls in enumerate(CLASSES)}
        contrasts = {}
        for k, cls in enumerate(CLASSES): contrasts[cls] = class_means[cls] - float(x[y != k].mean())
        dominant = max(CLASSES, key=lambda cls: abs(contrasts[cls])); direction = 1 if contrasts[dominant] > 0 else -1
        leave = []
        for quire in sorted(set(quires)):
            idx = np.asarray([i for i, q in enumerate(quires) if q != quire]); k = CLASSES.index(dominant)
            if np.any(y[idx] == k) and np.any(y[idx] != k):
                leave.append(float(x[idx][y[idx] == k].mean() - x[idx][y[idx] != k].mean()))
        leave_stable = bool(leave) and all((effect > 0) == (direction > 0) and effect != 0 for effect in leave)
        gain, positive, folds, top_delta, details = lofo(x, N, y, rows)
        local_p = (1 + int(np.sum(null[:, j] >= observed[j] - 1e-15))) / (WORLDS + 1)
        max_p = (1 + int(np.sum(null_max >= observed[j] - 1e-15))) / (WORLDS + 1)
        support = sum(values[p].get(name, 0) > 0 for p in allowed)
        paid = gain - math.log2(len(names))
        if gain > 0 and max_p <= .20 and leave_stable and support >= 8:
            label = "INTERESTING_EXPLORATORY"
        elif gain > 0 and local_p <= .10 and (max_p > .20 or not leave_stable):
            label = "LIKELY_QUIRE_OR_PAGE_CONFOUND"
        elif gain > 0: label = "WEAK"
        else: label = "NO_SIGNAL"
        candidates.append({
            "candidate_id": hashlib.sha256(name.encode()).hexdigest()[:16], "formal_feature": name,
            "feature_type": name.split(":", 1)[0], "support_pages": support, "absence_pages": 34 - support,
            "berry_mean": f"{class_means['BERRY_NO_CIRCLES']:.12f}", "flower_mean": f"{class_means['FLOWER_SIDE']:.12f}",
            "no_fruit_flower_mean": f"{class_means['NO_FRUIT_OR_FLOWER']:.12f}", "dominant_state": dominant,
            "dominant_one_vs_rest_effect": f"{contrasts[dominant]:.12f}",
            "leave_one_quire_direction_stable": str(leave_stable).lower(), "joint_separation": f"{observed[j]:.12f}",
            "strict_only_separation": f"{strict_score[j]:.12f}", "local_p": f"{local_p:.12f}",
            "library_maxT_p": f"{max_p:.12f}", "lofo_gain_bits": f"{gain:.12f}",
            "selector_paid_gain_bits": f"{paid:.12f}", "positive_folio_folds": positive, "folio_folds": folds,
            "top1_correct_delta": top_delta, "fold_gains": details, "label": label,
        })
    candidates.sort(key=lambda r: (float(r["library_maxT_p"]), -float(r["joint_separation"]), -float(r["lofo_gain_bits"]), r["formal_feature"]))
    for rank, row in enumerate(candidates, 1): row["rank"] = rank
    write(ATLAS, candidates, ["rank"] + [key for key in candidates[0] if key != "rank"])
    counters = []
    for candidate in candidates[:10]:
        name = str(candidate["formal_feature"]); target = str(candidate["dominant_state"])
        direction = 1 if float(candidate["dominant_one_vs_rest_effect"]) > 0 else -1
        ordered = sorted(((values[row["page"]].get(name, 0), row) for row in rows), key=lambda z: z[0])
        bad_target = [z for z in (ordered if direction > 0 else reversed(ordered)) if z[1]["visual_state"] == target][:2]
        bad_other = [z for z in (reversed(ordered) if direction > 0 else ordered) if z[1]["visual_state"] != target][:2]
        for value, row in list(bad_target) + list(bad_other):
            counters.append({"candidate_id": candidate["candidate_id"], "rank": candidate["rank"], "formal_feature": name,
                             "page": row["page"], "physical_folio": row["physical_folio"], "visual_state": row["visual_state"],
                             "feature_rate": f"{value:.12f}", "reason": "OPPOSITE_CLASS_EXTREME"})
    write(COUNTER, counters)
    label_counts = Counter(str(row["label"]) for row in candidates); top = candidates[0]
    payload = {
        "schema": "GDT364_RESULT_V1", "status": "POSTEXPOSURE_JOINT_ATLAS_COMPLETE",
        "panel": {"pages": 34, "physical_folios": 29, "formal_groups": len(source),
                  "classes": dict(Counter(row["visual_state"] for row in rows))},
        "feature_library": {"admitted": len(names), "support_min": 5, "absence_min": 5,
                            "nuisance_columns": nuisance_names, "exact_family_expressions": 0},
        "ranking_labels": dict(sorted(label_counts.items())), "top_candidate": top,
        "null": {"worlds": WORLDS, "seed": SEED, "unit": "WHOLE_FOLIO_STATE_VECTOR",
                 "strata": "QUIRE_X_PAGES_ON_FOLIO", "maxT": True,
                 "mobile_physical_folios": mobile_folios, "mobile_pages": mobile_pages},
        "historical_results": {"BERRY001_and_FLOWER001_preserved": True, "postexposure": True},
        "access": {"new_images_opened": False, "f84_rows_parsed_retained_joined_scored": False,
                   "f84_rows_skipped_before_parse": reader.stats.skipped_forbidden},
        "inputs": {str(path.relative_to(ROOT)): sha256_file(path) for path in (PANEL, FREEZE, FORMAL, EXP / "METHOD.md", GDT363_RUN)},
        "implementation": {str(Path(__file__).relative_to(ROOT)): sha256_file(Path(__file__))},
        "outputs": {str(path.relative_to(ROOT)): sha256_file(path) for path in (ATLAS, PAGES, COUNTER)},
        "claim_ceiling": "POSTEXPOSURE_EXPLORATORY_THREE_CLASS_PAGE_ASSOCIATION_ONLY_NO_LEXICAL_OR_SEMANTIC_CLAIM",
    }
    payload["content_hash"] = hashlib.sha256(canonical_json_bytes(payload)).hexdigest(); RESULT.write_bytes(canonical_json_bytes(payload))
    lines = ["# GDT364 reproductive-structure joint atlas report", "", f"Status: **{payload['status']}**.", "",
             "## Outcome", "", f"The exact existing-human panel contains 34 pages on 29 physical folios: 19 side-view-flower, 8 berry-without-added-circles, and 7 explicit no-fruit-or-flower pages. The state-blind source-family library retained **{len(names)}** features.", "",
             f"Top: `{top['formal_feature']}`, dominant class `{top['dominant_state']}`, one-versus-rest rate effect {float(top['dominant_one_vs_rest_effect']):+.4f}, LOFO gain {float(top['lofo_gain_bits']):+.3f} bits, local p={float(top['local_p']):.4f}, maxT p={float(top['library_maxT_p']):.4f}, **{top['label']}**.", "",
             "| rank | anonymous feature | berry / flower / none rates | dominant contrast | LOFO bits | local p | maxT p | label |", "|---:|---|---|---:|---:|---:|---:|---|"]
    for row in candidates[:12]:
        lines.append(f"| {row['rank']} | `{row['formal_feature']}` | {float(row['berry_mean']):.3f} / {float(row['flower_mean']):.3f} / {float(row['no_fruit_flower_mean']):.3f} | {float(row['dominant_one_vs_rest_effect']):+.3f} | {float(row['lofo_gain_bits']):+.3f} | {float(row['local_p']):.4f} | {float(row['library_maxT_p']):.4f} | {row['label']} |")
    lines += ["", "## Interpretation", "",
              f"This combines weak observations instead of requiring either old binary experiment to pass alone. It is still fully postexposure: the binary BERRY001 and FLOWER001 results already exist, and their nonconfirmations are unchanged. Whole-folio holdout and folio-vector permutations prevent the five two-page folios from being counted as independent pages. Only {mobile_folios}/29 folios ({mobile_pages}/34 pages) lie in null strata with more than one state vector, so adjusted power is limited.", "",
              "A surviving feature would remain a page-level renderer/content association with quire and illustration-style alternatives. It would not be a word or a semantic role.", "",
              "## Seal and claim ceiling", "",
              f"The guarded reader retained {reader.stats.selected} whitelisted formal rows and skipped {reader.stats.skipped_forbidden} f84-prefixed rows before formal-field parsing. No f84 row was retained, joined, displayed, or scored; no image or catalogue was opened.", "",
              "This result assigns no plant, flower, berry, lexeme, morpheme, part of speech, sound, language, plaintext, meaning, or translation.", ""]
    REPORT.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__": main()
