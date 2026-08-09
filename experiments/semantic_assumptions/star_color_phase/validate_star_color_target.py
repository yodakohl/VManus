#!/usr/bin/env python3
"""Independent scalar validation of the completed SCP001 target."""

from __future__ import annotations

import csv
import hashlib
import itertools
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
BIND = HERE / "source_phase_binding.tsv"
MATRIX = HERE / "anonymous_feature_matrix.tsv"
CONTROL = HERE / "anonymous_control_result.json"
AUDIT = HERE / "prescore_audit.json"
TARGET = HERE / "TARGET_RESULT.json"
ROWS = HERE / "target_feature_results.tsv"
RUNNER = HERE / "run_star_color_target.py"
OUT = HERE / "target_validation.json"
REPORT = ROOT / "experiments/semantic_assumptions/results/star_color_target_validation.md"

ED = ("ZL3b", "IT2a", "RF1b")
ELIGIBLE = (
    "WORD_COUNT", "LINE_CARRIER_ANY", "LINE_CARRIER_T", "ROLE_RATE_BOUND_D",
    "ROLE_RATE_BOUND_E", "ROLE_RATE_Q", "ROLE_RATE_REL_I", "ROLE_RATE_FREE_L",
    "ROLE_RATE_FREE_R", "FIRST_HAS_BOUND_D", "FIRST_HAS_BOUND_E",
    "FIRST_HAS_REL_I", "FIRST_HAS_FREE_R", "EDGE_RATE_D_TO_Q", "EDGE_RATE_E_TO_Q",
)
RUNNER_SHA = "0f495ac904f7ff2cbabdbc63645376ad4c13fb403f194b8f983aa5437d76d59c"


def rows(path):
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def close(a, b, tol=5e-12):
    return abs(float(a) - float(b)) <= tol


def matrix_and_contrasts():
    raw = rows(MATRIX)
    matrix = []
    feature_names = tuple(k for k in raw[0] if k not in {
        "page", "physical_folio", "star_ordinal", "ordinal_parity", "locus", "edition"
    })
    for r in raw:
        matrix.append({
            **{k: r[k] for k in ("page", "physical_folio", "star_ordinal", "ordinal_parity", "locus", "edition")},
            **{f: float(r[f]) for f in feature_names},
        })
    vals = defaultdict(list)
    pf = {}
    for r in matrix:
        pf[r["page"]] = r["physical_folio"]
        for f in feature_names:
            vals[(r["page"], r["edition"], f, r["ordinal_parity"])].append(r[f])
    pages = sorted(pf)
    cc = {}
    for p in pages:
        for e in ED:
            for f in feature_names:
                cc[(p, e, f)] = statistics.fmean(vals[(p, e, f, "ODD")]) - statistics.fmean(vals[(p, e, f, "EVEN")])
    return raw, feature_names, pages, pf, cc


def effect(cc, pages, pf, phase, e, f, omit=None):
    grouped = defaultdict(list)
    for p in pages:
        if pf[p] != omit:
            grouped[pf[p]].append(phase[p] * cc[(p, e, f)])
    return statistics.fmean(statistics.fmean(v) for v in grouped.values())


def eligibility(features, pages, pf, cc, phases):
    out = []
    for f in features:
        good = True
        for e in ED:
            orbit = [effect(cc, pages, pf, ph, e, f) for ph in phases]
            supported = [p for p in pages if abs(cc[(p, e, f)]) > 1e-15]
            good &= statistics.pstdev(orbit) > 0 and len(supported) >= 5 and len({pf[p] for p in supported}) >= 4
        if good:
            out.append(f)
    return out


def exact_results(pages, pf, cc, phases, phase):
    scales = {}
    all_effects = {}
    robust = {}
    for e in ED:
        for f in ELIGIBLE:
            orbit = [effect(cc, pages, pf, ph, e, f) for ph in phases]
            scales[(e, f)] = statistics.pstdev(orbit)
            for i, value in enumerate(orbit):
                all_effects[(i, e, f)] = value
    for i in range(512):
        for f in ELIGIBLE:
            zz = [all_effects[(i, e, f)] / scales[(e, f)] for e in ED]
            robust[(i, f)] = max(min(zz), min(-z for z in zz), 0.0)
    family = [max(robust[(i, f)] for f in ELIGIBLE) for i in range(512)]
    idx = phases.index(phase)
    result = []
    for f in ELIGIBLE:
        es = {e: all_effects[(idx, e, f)] for e in ED}
        signset = {1 if v > 0 else -1 if v < 0 else 0 for v in es.values()}
        direction = next(iter(signset)) if len(signset) == 1 else 0
        rz = robust[(idx, f)]
        raw_p = sum(robust[(i, f)] >= rz - 1e-15 for i in range(512)) / 512
        fam_p = sum(v >= rz - 1e-15 for v in family) / 512
        subgroup = {}
        strata_ok = direction != 0
        for label, wanted in (("red_first_effects", 1), ("yellow_first_effects", -1)):
            subpages = [p for p in pages if phase[p] == wanted]
            subpf = {p: pf[p] for p in subpages}
            subgroup[label] = {e: effect(cc, subpages, subpf, phase, e, f) for e in ED}
            for v in subgroup[label].values():
                strata_ok &= v != 0 and (v > 0) == (direction > 0)
        deletions = {
            folio: {e: effect(cc, pages, pf, phase, e, f, omit=folio) for e in ED}
            for folio in sorted(set(pf.values()))
        }
        deletion_ok = direction != 0 and all(
            v != 0 and (v > 0) == (direction > 0)
            for dd in deletions.values() for v in dd.values()
        )
        gates = {
            "same_direction": direction != 0,
            "robust_z": rz >= 2 - 1e-15,
            "raw_p": raw_p <= .025 + 1e-15,
            "family_p": fam_p <= .05 + 1e-15,
            "phase_strata": bool(strata_ok),
            "folio_deletions": bool(deletion_ok),
        }
        result.append({
            "feature": f, "robust_z": rz, "raw_p": raw_p, "family_p": fam_p,
            "effects": es, "gates": gates, "pass": all(gates.values()),
            **subgroup, "folio_deletion_effects": deletions,
        })
    return idx, family, result


def nested_match(a, b):
    if isinstance(a, dict):
        return isinstance(b, dict) and set(a) == set(b) and all(nested_match(a[k], b[k]) for k in a)
    if isinstance(a, list):
        return isinstance(b, list) and len(a) == len(b) and all(nested_match(x, y) for x, y in zip(a, b))
    if isinstance(a, (float, int)) and not isinstance(a, bool):
        return isinstance(b, (float, int)) and close(a, b)
    return a == b


def main():
    target = json.loads(TARGET.read_text(encoding="utf-8"))
    control = json.loads(CONTROL.read_text(encoding="utf-8"))
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    raw_matrix, features, pages, pf, cc = matrix_and_contrasts()
    phases = [dict(zip(pages, signs)) for signs in itertools.product((-1, 1), repeat=9)]
    phase_rows = rows(BIND)
    phase = {r["page"]: 1 if r["first_color"] == "RED" else -1 for r in phase_rows}
    idx, family, rebuilt = exact_results(pages, pf, cc, phases, phase)
    family_digest = hashlib.sha256("\n".join(f"{x:.17g}" for x in family).encode()).hexdigest()
    stored_rows = rows(ROWS)

    checks = {}
    checks["runner_hash"] = sha(RUNNER) == RUNNER_SHA
    checks["target_input_hashes"] = target["inputs"] == {
        str(BIND.relative_to(ROOT)): sha(BIND), str(MATRIX.relative_to(ROOT)): sha(MATRIX),
        str(CONTROL.relative_to(ROOT)): sha(CONTROL), str(AUDIT.relative_to(ROOT)): sha(AUDIT),
    }
    checks["prescore_statuses"] = control["passed"] == 19 and audit["passed"] == 21
    checks["matrix_contract"] = len(raw_matrix) == 360 and len({(r["locus"], r["edition"]) for r in raw_matrix}) == 360
    checks["feature_inventory"] = list(features) == target["features_frozen"]
    checks["eligibility"] = eligibility(features, pages, pf, cc, phases) == list(ELIGIBLE) == target["eligible_features"]
    checks["phase_binding"] = phase == target["target_phase"] and [p for p in pages if phase[p] == -1] == ["f113r", "f114v"]
    checks["orbit_and_index"] = len(phases) == target["phase_orbit"] == 512 and idx == target["target_assignment_index"] == 493
    checks["family_orbit_digest"] = family_digest == target["family_orbit_sha256"]
    checks["all_feature_results"] = nested_match(rebuilt, target["feature_results"])
    checks["all_feature_rows"] = len(stored_rows) == 15 and all(
        r["feature"] == s["feature"]
        and close(r["robust_z"], s["robust_z"])
        and close(r["raw_p"], s["raw_p"])
        and close(r["family_p"], s["family_p"])
        and int(r["same_direction"]) == int(s["gates"]["same_direction"])
        and int(r["phase_strata"]) == int(s["gates"]["phase_strata"])
        and int(r["folio_deletions"]) == int(s["gates"]["folio_deletions"])
        and int(r["pass"]) == int(s["pass"])
        for r, s in zip(stored_rows, rebuilt)
    )
    checks["target_rows_hash"] = sha(ROWS) == target["target_rows_sha256"]
    checks["zero_passes"] = not any(r["pass"] for r in rebuilt) and target["passing_features"] == []
    checks["decision"] = target["decision"] == "NONCONFIRMATION" and target["status"] == "FINAL_NONCONFIRMATION"
    ranked = sorted(rebuilt, key=lambda r: (r["family_p"], -r["robust_z"], r["feature"]))
    checks["best_feature"] = (
        ranked[0]["feature"] == "LINE_CARRIER_ANY"
        and close(ranked[0]["robust_z"], 1.12527462618)
        and close(ranked[0]["raw_p"], .171875)
        and close(ranked[0]["family_p"], .93359375)
    )
    checks["claim_ceiling"] = target["claim_ceiling"] == "marker-color-conditioned formal construction only"
    checks["forbidden_inferences"] = set(target["forbidden"]) == {
        "color meaning", "recipe class", "number", "lexeme", "plaintext", "language", "translation"
    }
    checks["all_finite"] = all(
        math.isfinite(float(r[k])) for r in rebuilt for k in ("robust_z", "raw_p", "family_p")
    )

    assert all(checks.values()), {k: v for k, v in checks.items() if not v}
    payload = {
        "experiment": "SCP001", "status": "PASS_INDEPENDENT_TARGET_RECONSTRUCTION",
        "checks": checks, "passed": sum(checks.values()), "total": len(checks),
        "decision": "NONCONFIRMATION", "passing_features": [],
        "best_feature": "LINE_CARRIER_ANY", "target_sha256": sha(TARGET),
    }
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# SCP001 independent target validation\n\n"
        f"**PASS — {sum(checks.values())}/{len(checks)} checks reconstruct the final nonconfirmation.**\n\n"
        "A separate scalar implementation verifies the frozen runner and input hashes, "
        "360-row matrix, 19-feature inventory, 15-feature eligibility, physical phase "
        "binding, target index 493, all 512 assignments, family-orbit digest, every "
        "reading effect, robust z, raw and family tail, normal/reversed phase effect, "
        "seven folio deletions, all stored rows and hashes, zero passes, decision, and "
        "claim ceiling. The strongest feature is LINE_CARRIER_ANY (robust z 1.125275, "
        "raw p .171875, familywise p .933594), which is nonconfirming.\n\n"
        "Validation confirms arithmetic and binding only. It supplies no color meaning, "
        "recipe class, number, lexeme, plaintext, language, or translation.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
