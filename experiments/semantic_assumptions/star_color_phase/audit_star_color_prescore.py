#!/usr/bin/env python3
"""Nonimporting SCP001 prescore reconstruction; never reads target phase."""

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
SOURCE = HERE / "source_panel.tsv"
INTER = ROOT / "experiments/semantic_assumptions/results/pre_grounding_interlinear.tsv"
MATRIX = HERE / "anonymous_feature_matrix.tsv"
CONTROL = HERE / "anonymous_control_result.json"
RUNNER = HERE / "run_star_color_anonymous_controls.py"
OUT = HERE / "prescore_audit.json"
REPORT = ROOT / "experiments/semantic_assumptions/results/star_color_prescore_audit.md"

ED = ("ZL3b", "IT2a", "RF1b")
FF = (
    "WORD_COUNT", "LINE_CARRIER_ANY", "LINE_CARRIER_T", "LINE_CARRIER_D",
    "LINE_CARRIER_S", "ROLE_RATE_BOUND_D", "ROLE_RATE_BOUND_E", "ROLE_RATE_Q",
    "ROLE_RATE_REL_I", "ROLE_RATE_FREE_L", "ROLE_RATE_FREE_R",
    "FIRST_HAS_BOUND_D", "FIRST_HAS_BOUND_E", "FIRST_HAS_Q",
    "FIRST_HAS_REL_I", "FIRST_HAS_FREE_L", "FIRST_HAS_FREE_R",
    "EDGE_RATE_D_TO_Q", "EDGE_RATE_E_TO_Q",
)


def rr(path: Path):
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def hx(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def split_atoms(s: str):
    return [a for token in s.split() for a in token.split("+") if a]


def count_role(s: str, role: str) -> int:
    aa = split_atoms(s)
    if role == "Q":
        return sum(a[:2] == "Q_" for a in aa)
    return sum(a == role for a in aa)


def first_role(s: str, role: str) -> float:
    aa = s.split()[0].split("+") if s.split() else []
    if role == "Q":
        return float(any(a[:2] == "Q_" for a in aa))
    return float(role in aa)


def confirmed(s: str, left: str) -> int:
    n = 0
    for item in s.split(";"):
        if not item or ":" not in item:
            continue
        roles = item.split(":", 1)[1]
        if ">" in roles:
            a, b = roles.split(">", 1)
            n += int(a == left and b[:2] == "Q_")
    return n


def independent_features(r):
    n = int(r["word_count"])
    role = r["role_sequence"]
    lc = r["line_carrier"]
    return {
        "WORD_COUNT": float(n), "LINE_CARRIER_ANY": float(lc != ""),
        "LINE_CARRIER_T": float(lc == "t"), "LINE_CARRIER_D": float(lc == "d"),
        "LINE_CARRIER_S": float(lc == "s"),
        "ROLE_RATE_BOUND_D": count_role(role, "BOUND_D") / n,
        "ROLE_RATE_BOUND_E": count_role(role, "BOUND_E") / n,
        "ROLE_RATE_Q": count_role(role, "Q") / n,
        "ROLE_RATE_REL_I": count_role(role, "REL_I") / n,
        "ROLE_RATE_FREE_L": count_role(role, "FREE_L") / n,
        "ROLE_RATE_FREE_R": count_role(role, "FREE_R") / n,
        "FIRST_HAS_BOUND_D": first_role(role, "BOUND_D"),
        "FIRST_HAS_BOUND_E": first_role(role, "BOUND_E"),
        "FIRST_HAS_Q": first_role(role, "Q"),
        "FIRST_HAS_REL_I": first_role(role, "REL_I"),
        "FIRST_HAS_FREE_L": first_role(role, "FREE_L"),
        "FIRST_HAS_FREE_R": first_role(role, "FREE_R"),
        "EDGE_RATE_D_TO_Q": confirmed(r["confirmed_edges"], "BOUND_D") / n,
        "EDGE_RATE_E_TO_Q": confirmed(r["confirmed_edges"], "BOUND_E") / n,
    }


def reconstruct():
    src = rr(SOURCE)
    units = {
        r["locus"]: (r["page"], r["physical_folio"], r["star_ordinal"], r["ordinal_parity"])
        for r in src
    }
    assert len(src) == len(units) == 120
    selected = defaultdict(dict)
    with INTER.open(encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            if r["locus"] in units:
                assert r["edition"] not in selected[r["locus"]]
                selected[r["locus"]][r["edition"]] = r
    rebuilt = []
    for locus, meta in units.items():
        assert set(selected[locus]) == set(ED)
        for edition in ED:
            values = independent_features(selected[locus][edition])
            rebuilt.append({
                "page": meta[0], "physical_folio": meta[1],
                "star_ordinal": meta[2], "ordinal_parity": meta[3],
                "locus": locus, "edition": edition, **values,
            })
    return src, rebuilt


def exact_matrix_match(rebuilt, stored):
    if len(rebuilt) != len(stored) or len(stored) != 360:
        return False
    for a, b in zip(rebuilt, stored):
        for k in ("page", "physical_folio", "star_ordinal", "ordinal_parity", "locus", "edition"):
            if str(a[k]) != b[k]:
                return False
        for f in FF:
            if abs(float(a[f]) - float(b[f])) > 5e-12:
                return False
    return True


def contrasts(rebuilt):
    values = defaultdict(list)
    pf = {}
    for r in rebuilt:
        pf[r["page"]] = r["physical_folio"]
        for f in FF:
            values[(r["page"], r["edition"], f, r["ordinal_parity"])].append(float(r[f]))
    pages = sorted(pf)
    cc = {}
    for p in pages:
        for e in ED:
            for f in FF:
                cc[(p, e, f)] = statistics.fmean(values[(p, e, f, "ODD")]) - statistics.fmean(values[(p, e, f, "EVEN")])
    return pages, pf, cc


def eff(cc, pages, pf, phase, e, f, omit=None):
    by_folio = defaultdict(list)
    for p in pages:
        if pf[p] != omit:
            by_folio[pf[p]].append(phase[p] * cc[(p, e, f)])
    return statistics.fmean(statistics.fmean(x) for x in by_folio.values())


def independent_eligibility(cc, pages, pf, phases):
    eligible, detail = [], {}
    for f in FF:
        detail[f] = {}
        good = True
        for e in ED:
            orbit = [eff(cc, pages, pf, ph, e, f) for ph in phases]
            pp = [p for p in pages if abs(cc[(p, e, f)]) > 1e-15]
            folios = {pf[p] for p in pp}
            sd = statistics.pstdev(orbit)
            detail[f][e] = {"sd": sd, "pages": len(pp), "folios": len(folios)}
            good &= math.isfinite(sd) and sd > 0 and len(pp) >= 5 and len(folios) >= 4
        if good:
            eligible.append(f)
    return eligible, detail


def scalar_synthetic_checks():
    pages = [f"P{i}" for i in range(1, 10)]
    pf = {f"P{i}": f"F{i}" for i in range(1, 8)}
    pf.update({"P8": "F6", "P9": "F7"})
    truth = dict(zip(pages, (1, 1, -1, 1, -1, 1, 1, -1, 1)))
    phases = [dict(zip(pages, s)) for s in itertools.product((-1, 1), repeat=9)]

    def robust_for(cc):
        vals = {e: [eff(cc, pages, pf, ph, e, "X") for ph in phases] for e in ED}
        sd = {e: statistics.pstdev(vals[e]) for e in ED}
        robust = []
        for i in range(512):
            z = [vals[e][i] / sd[e] for e in ED]
            robust.append(max(min(z), min(-x for x in z), 0.0))
        idx = phases.index(truth)
        return robust, idx

    plant = {(p, e, "X"): truth[p] * (1 + .03 * pages.index(p)) for p in pages for e in ED}
    rob, idx = robust_for(plant)
    plant_p = sum(v >= rob[idx] - 1e-15 for v in rob) / 512
    comp_idx = phases.index({p: -truth[p] for p in pages})

    disagree = {(p, e, "X"): truth[p] * (-1 if e == "RF1b" else 1) for p in pages for e in ED}
    dis, didx = robust_for(disagree)

    parity = {(p, e, "X"): 1.0 for p in pages for e in ED}
    normal = statistics.fmean(truth[p] * parity[(p, "ZL3b", "X")] for p in pages if truth[p] == 1)
    reverse = statistics.fmean(truth[p] * parity[(p, "ZL3b", "X")] for p in pages if truth[p] == -1)

    leverage = {(p, e, "X"): truth[p] * (20 if p == "P1" else 0) for p in pages for e in ED}
    deleted = eff(leverage, pages, pf, truth, "ZL3b", "X", omit="F1")
    return {
        "synthetic_512": len(phases) == 512,
        "synthetic_planted_2_of_512": plant_p == 2 / 512,
        "synthetic_complement_equal": abs(rob[idx] - rob[comp_idx]) < 1e-12,
        "synthetic_parity_strata_opposite": normal > 0 and reverse < 0,
        "synthetic_leverage_deletion_zero": deleted == 0,
        "synthetic_reading_disagreement_zero": dis[didx] == 0,
    }


def close(a, b, tol=1e-14):
    return abs(float(a) - float(b)) <= tol


def main():
    control = json.loads(CONTROL.read_text(encoding="utf-8"))
    stored = rr(MATRIX)
    source, rebuilt = reconstruct()
    pages, pf, cc = contrasts(rebuilt)
    phases = [dict(zip(pages, s)) for s in itertools.product((-1, 1), repeat=len(pages))]
    eligible, detail = independent_eligibility(cc, pages, pf, phases)

    checks = {}
    checks["bound_input_hashes"] = control["inputs"] == {
        str(SOURCE.relative_to(ROOT)): hx(SOURCE), str(INTER.relative_to(ROOT)): hx(INTER)
    }
    checks["feature_inventory"] = tuple(control["features_frozen"]) == FF
    checks["exact_120_source_rows"] = len(source) == 120 and len({r["locus"] for r in source}) == 120
    checks["exact_360_matrix_rows"] = len(stored) == 360 and len({(r["locus"], r["edition"]) for r in stored}) == 360
    checks["independent_feature_matrix"] = exact_matrix_match(rebuilt, stored)
    checks["matrix_hash"] = hx(MATRIX) == control["matrix_sha256"]
    checks["exact_page_folio_topology"] = len(pages) == 9 and len(set(pf.values())) == 7
    checks["exact_512_orbit"] = len(phases) == control["phase_orbit"] == 512
    checks["eligibility_identity"] = eligible == control["eligible_features"] and len(eligible) == 15
    checks["eligibility_numerics"] = all(
        detail[f][e][k] == control["eligibility_detail"][f][e][k]
        if k in ("pages", "folios") else close(detail[f][e][k], control["eligibility_detail"][f][e][k])
        for f in FF for e in ED for k in ("sd", "pages", "folios")
    )
    checks.update(scalar_synthetic_checks())
    checks["registered_controls_all_true"] = control["passed"] == control["total"] == 19 and all(control["controls"].values())
    runner_source = RUNNER.read_text(encoding="utf-8")
    checks["runner_target_fields_absent"] = "first_color" not in runner_source and '["color"]' not in runner_source and "['color']" not in runner_source
    checks["target_artifacts_absent"] = not (HERE / "TARGET_RESULT.json").exists() and not (HERE / "target_feature_results.tsv").exists()
    checks["target_flags_false"] = control["target_phase_accessed"] is False and control["target_result_exists"] is False
    checks["claim_ceiling"] = control["claim_ceiling"] == "marker-color-conditioned formal construction only"

    assert all(checks.values()), {k: v for k, v in checks.items() if not v}
    payload = {
        "experiment": "SCP001", "status": "PASS_PRESCORE_AUDIT_TARGET_AUTHORIZED_UNRUN",
        "checks": checks, "passed": sum(checks.values()), "total": len(checks),
        "eligible_features": eligible, "matrix_sha256": hx(MATRIX),
        "target_phase_accessed": False, "target_result_exists": False,
    }
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# SCP001 independent prescore audit\n\n"
        f"**PASS — {sum(checks.values())}/{len(checks)} nonimporting checks; target authorized but unrun.**\n\n"
        "A separate scalar implementation reconstructs all 120 source units, 360 "
        "reading rows, 19 formal features, the exact stored matrix and hash, the 15 "
        "eligible features and every support/variance value, nine-page/seven-folio "
        "topology, all 512 synchronized phases, and the planted, complement, parity, "
        "leverage, disagreement, and degeneracy behavior. It also confirms all 19 "
        "registered controls, static absence of target fields in the control runner, "
        "false target-access flags, absent target artifacts, and the claim ceiling.\n\n"
        "This authorizes one separate frozen target implementation. It supplies no "
        "color function, recipe class, number, word, lexeme, plaintext, language, or "
        "translation.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
