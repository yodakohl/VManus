#!/usr/bin/env python3
"""Independent source/feature/null validator for GDT364."""
from __future__ import annotations

import csv
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from tools.vmanus_experiment import GuardedTSV, canonical_json_bytes, sha256_file  # noqa: E402

EXP = ROOT / "experiments/yolo/gdt364_reproductive_structure_joint_atlas"; ART = EXP / "artifacts"
PANEL = ART / "gdt364_panel.tsv"; ATLAS = ART / "gdt364_candidate_atlas.tsv"
FORMAL = ROOT / "experiments/semantic_assumptions/results/source_sta_family_consensus_groups.tsv"
RESULT = ART / "gdt364_result.json"; VALIDATION = ART / "gdt364_validation.json"
CLASSES = ["BERRY_NO_CIRCLES", "FLOWER_SIDE", "NO_FRUIT_OR_FLOWER"]
WORLDS = 4096; SEED = 3641901


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as h: return list(csv.DictReader(h, delimiter="\t"))


def page_values(rows: list[dict[str, str]]) -> dict[str, float]:
    groups = len(rows); by_locus: dict[str, list[dict[str, str]]] = defaultdict(list); gc: Counter[str] = Counter()
    for row in rows:
        family = row["family_surface"]
        names = {f"COMPONENT:{c}" for c in set(family)}
        for n in (2, 3): names |= {f"WITHIN_GROUP_{n}GRAM:{family[i:i+n]}" for i in range(len(family) - n + 1)}
        names |= {"LEFT_BOUNDARY:" + row["left_boundary_profile"], "RIGHT_BOUNDARY:" + row["right_boundary_profile"]}
        gc.update(names); by_locus[row["locus"]].append(row)
    values = {name: count / groups for name, count in gc.items()}; lc: Counter[str] = Counter()
    for lr in by_locus.values():
        ordered = sorted(lr, key=lambda r: int(r["consensus_group_index"])); first = ordered[0]["family_surface"]; last = ordered[-1]["family_surface"]
        names = set()
        for n in (1, 2, 3):
            if len(first) >= n: names.add(f"FIRST_GROUP_PREFIX_{n}:{first[:n]}")
            if len(last) >= n: names.add(f"LAST_GROUP_SUFFIX_{n}:{last[-n:]}")
        if len(ordered) >= 2: names.add("CONSTRUCTION:MULTIGROUP")
        if len(ordered) >= 3: names.add("CONSTRUCTION:THREE_PLUS_GROUPS")
        lc.update(names)
    values.update({name: count / len(by_locus) for name, count in lc.items()}); return values


def separation(F: np.ndarray, y: np.ndarray, quires: list[str]) -> np.ndarray:
    R = F.copy()
    for quire in sorted(set(quires)):
        idx = np.asarray([i for i, q in enumerate(quires) if q == quire]); R[idx] -= R[idx].mean(0)
    total = np.sum(R * R, axis=0); between = np.zeros(F.shape[1])
    for cls in range(3):
        idx = np.flatnonzero(y == cls)
        if len(idx): between += len(idx) * R[idx].mean(0) ** 2
    out = np.zeros(F.shape[1]); ok = total > 1e-15; out[ok] = between[ok] / total[ok]; return out


def permute(y: np.ndarray, rows: list[dict[str, str]], rng: np.random.Generator) -> np.ndarray:
    by: dict[str, list[int]] = defaultdict(list)
    for i, row in enumerate(rows): by[row["physical_folio"]].append(i)
    for idx in by.values(): idx.sort(key=lambda i: rows[i]["page"])
    blocks: dict[tuple[str, int], list[str]] = defaultdict(list)
    for folio, idx in by.items(): blocks[(rows[idx[0]]["quire"], len(idx))].append(folio)
    out = y.copy()
    for folios in blocks.values():
        for recipient, donor in zip(folios, list(rng.permutation(folios))): out[by[recipient]] = y[by[str(donor)]]
    return out


def main() -> None:
    checks = []
    def ck(name: str, okay: bool, detail: object = "") -> None:
        checks.append({"name": name, "pass": bool(okay), "detail": detail})
        if not okay: raise AssertionError((name, detail))
    panel = read(PANEL); atlas = read(ATLAS); result = json.loads(RESULT.read_text())
    ck("panel_34", len(panel) == 34); ck("folios_29", len({r['physical_folio'] for r in panel}) == 29)
    ck("states", Counter(r["visual_state"] for r in panel) == Counter(FLOWER_SIDE=19, BERRY_NO_CIRCLES=8, NO_FRUIT_OR_FLOWER=7))
    allowed = {r["page"] for r in panel}; reader = GuardedTSV(FORMAL, selector_column="page", allowed_values=allowed, forbidden_prefixes=("f84",), forbidden_action="skip")
    source = list(reader); ck("source_2181", len(source) == 2181, len(source)); ck("source_pages", {r["page"] for r in source} == allowed)
    ck("source_no_f84", not any(r["page"].startswith("f84") for r in source))
    by_page: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in source: by_page[row["page"]].append(row)
    values = {page: page_values(rows) for page, rows in by_page.items()}
    names = sorted(name for name in {n for v in values.values() for n in v}
                   if sum(values[p].get(name, 0) > 0 for p in allowed) >= 5 and sum(values[p].get(name, 0) == 0 for p in allowed) >= 5)
    ck("feature_200", len(names) == 200, len(names)); ck("feature_set", set(names) == {r["formal_feature"] for r in atlas})
    ck("no_exact", not any(name.startswith("EXACT_") for name in names))
    y = np.asarray([CLASSES.index(r["visual_state"]) for r in panel]); F = np.asarray([[values[r["page"]].get(name, 0) for name in names] for r in panel])
    quires = [r["quire"] for r in panel]; observed = separation(F, y, quires); by_name = {r["formal_feature"]: r for r in atlas}
    ck("observed_scores", all(abs(float(by_name[n]["joint_separation"]) - observed[j]) < 5e-10 for j, n in enumerate(names)))
    means_ok = True
    field = {0: "berry_mean", 1: "flower_mean", 2: "no_fruit_flower_mean"}
    for j, name in enumerate(names):
        for cls in range(3): means_ok &= abs(float(by_name[name][field[cls]]) - F[y == cls, j].mean()) < 5e-10
    ck("all_class_means", means_ok)
    rng = np.random.default_rng(SEED); null = np.zeros((WORLDS, len(names)))
    for world in range(WORLDS): null[world] = separation(F, permute(y, panel, rng), quires)
    maxv = null.max(1)
    local = [(1 + int(np.sum(null[:, j] >= observed[j] - 1e-15))) / (WORLDS + 1) for j in range(len(names))]
    maxp = [(1 + int(np.sum(maxv >= observed[j] - 1e-15))) / (WORLDS + 1) for j in range(len(names))]
    ck("local_p", all(abs(float(by_name[n]["local_p"]) - local[j]) < 5e-10 for j, n in enumerate(names)))
    ck("maxT_p", all(abs(float(by_name[n]["library_maxT_p"]) - maxp[j]) < 5e-10 for j, n in enumerate(names)))
    gains_ok = folds_ok = True
    for row in atlas:
        parts = [float(item.split(":", 1)[1]) for item in row["fold_gains"].split(";")]
        gains_ok &= abs(sum(parts) - float(row["lofo_gain_bits"])) < 5e-7
        folds_ok &= len(parts) == 29 and sum(value > 0 for value in parts) == int(row["positive_folio_folds"])
    ck("fold_gain_arithmetic", gains_ok); ck("fold_counts", folds_ok)
    ck("no_interesting", not any(r["label"] == "INTERESTING_EXPLORATORY" for r in atlas))
    ck("top_KU", atlas[0]["formal_feature"] == "WITHIN_GROUP_2GRAM:KU", atlas[0]["formal_feature"])
    ck("top_maxT", abs(float(atlas[0]["library_maxT_p"]) - 0.793263363437) < 1e-10)
    ck("mobile_capacity", result["null"]["mobile_physical_folios"] == 19 and result["null"]["mobile_pages"] == 22)
    copy = dict(result); digest = copy.pop("content_hash"); ck("content_hash", hashlib.sha256(canonical_json_bytes(copy)).hexdigest() == digest)
    ck("input_hashes", all(sha256_file(ROOT / rel) == value for rel, value in result["inputs"].items()))
    ck("implementation_hashes", all(sha256_file(ROOT / rel) == value for rel, value in result["implementation"].items()))
    ck("output_hashes", all(sha256_file(ROOT / rel) == value for rel, value in result["outputs"].items()))
    report = (EXP / "REPORT.md").read_text(); ck("report_postexposure", "fully postexposure" in report)
    ck("report_claim_ceiling", "assigns no plant, flower, berry" in report)
    ck("report_f84", "No f84 row was retained, joined, displayed, or scored" in report)
    payload = {"schema": "GDT364_VALIDATION_V1", "status": "PASS", "checks": checks,
               "pass_count": sum(bool(x["pass"]) for x in checks), "check_count": len(checks),
               "scope": "INDEPENDENT_SOURCE_FEATURE_AND_COMPLETE_NULL_RECONSTRUCTION_PLUS_MODEL_ARITHMETIC",
               "result_sha256": sha256_file(RESULT), "validator_sha256": sha256_file(Path(__file__)),
               "documents": {str(path.relative_to(ROOT)): sha256_file(path) for path in (EXP / "METHOD.md", EXP / "REPORT.md")},
               "f84_accessed": False}
    payload["content_hash"] = hashlib.sha256(canonical_json_bytes(payload)).hexdigest()
    VALIDATION.write_bytes(canonical_json_bytes(payload)); print(f"PASS {payload['pass_count']}/{payload['check_count']}")


if __name__ == "__main__": main()
