#!/usr/bin/env python3
"""SCP001 target-blind feature extraction and anonymous controls."""

from __future__ import annotations

import csv
import hashlib
import itertools
import json
import math
import statistics
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
SOURCE = HERE / "source_panel.tsv"
INTER = ROOT / "experiments/semantic_assumptions/results/pre_grounding_interlinear.tsv"
MATRIX = HERE / "anonymous_feature_matrix.tsv"
RESULT = HERE / "anonymous_control_result.json"
REPORT = ROOT / "experiments/semantic_assumptions/results/star_color_anonymous_control_report.md"

EDITIONS = ("ZL3b", "IT2a", "RF1b")
FEATURES = (
    "WORD_COUNT", "LINE_CARRIER_ANY", "LINE_CARRIER_T", "LINE_CARRIER_D",
    "LINE_CARRIER_S", "ROLE_RATE_BOUND_D", "ROLE_RATE_BOUND_E", "ROLE_RATE_Q",
    "ROLE_RATE_REL_I", "ROLE_RATE_FREE_L", "ROLE_RATE_FREE_R",
    "FIRST_HAS_BOUND_D", "FIRST_HAS_BOUND_E", "FIRST_HAS_Q",
    "FIRST_HAS_REL_I", "FIRST_HAS_FREE_L", "FIRST_HAS_FREE_R",
    "EDGE_RATE_D_TO_Q", "EDGE_RATE_E_TO_Q",
)
ALLOWED_SOURCE_FIELDS = {
    "page", "physical_folio", "star_ordinal", "ordinal_parity", "locus",
    "zl_marker", "reading_coverage",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atoms(path: str) -> list[str]:
    return [part for word in path.split() for part in word.split("+") if part]


def atom_count(path: str, name: str) -> int:
    aa = atoms(path)
    return sum(a.startswith("Q_") for a in aa) if name == "Q" else aa.count(name)


def first_has(path: str, name: str) -> float:
    first = path.split()[0] if path.split() else ""
    aa = [x for x in first.split("+") if x]
    return float(any(a.startswith("Q_") for a in aa)) if name == "Q" else float(name in aa)


def edge_count(value: str, left: str) -> int:
    total = 0
    for edge in filter(None, value.split(";")):
        roles = edge.split(":", 1)[-1]
        if ">" not in roles:
            continue
        a, b = roles.split(">", 1)
        total += a == left and b.startswith("Q_")
    return total


def extract(row: dict[str, str]) -> dict[str, float]:
    n = int(row["word_count"])
    assert n > 0
    roles = row["role_sequence"]
    carrier = row["line_carrier"]
    values = {
        "WORD_COUNT": float(n),
        "LINE_CARRIER_ANY": float(bool(carrier)),
        "LINE_CARRIER_T": float(carrier == "t"),
        "LINE_CARRIER_D": float(carrier == "d"),
        "LINE_CARRIER_S": float(carrier == "s"),
        "ROLE_RATE_BOUND_D": atom_count(roles, "BOUND_D") / n,
        "ROLE_RATE_BOUND_E": atom_count(roles, "BOUND_E") / n,
        "ROLE_RATE_Q": atom_count(roles, "Q") / n,
        "ROLE_RATE_REL_I": atom_count(roles, "REL_I") / n,
        "ROLE_RATE_FREE_L": atom_count(roles, "FREE_L") / n,
        "ROLE_RATE_FREE_R": atom_count(roles, "FREE_R") / n,
        "FIRST_HAS_BOUND_D": first_has(roles, "BOUND_D"),
        "FIRST_HAS_BOUND_E": first_has(roles, "BOUND_E"),
        "FIRST_HAS_Q": first_has(roles, "Q"),
        "FIRST_HAS_REL_I": first_has(roles, "REL_I"),
        "FIRST_HAS_FREE_L": first_has(roles, "FREE_L"),
        "FIRST_HAS_FREE_R": first_has(roles, "FREE_R"),
        "EDGE_RATE_D_TO_Q": edge_count(row["confirmed_edges"], "BOUND_D") / n,
        "EDGE_RATE_E_TO_Q": edge_count(row["confirmed_edges"], "BOUND_E") / n,
    }
    assert tuple(values) == FEATURES
    assert all(math.isfinite(v) for v in values.values())
    return values


def load_units() -> list[dict[str, str]]:
    with SOURCE.open(encoding="utf-8", newline="") as fh:
        source_rows = list(csv.DictReader(fh, delimiter="\t"))
    units = [{k: r[k] for k in ALLOWED_SOURCE_FIELDS} for r in source_rows]
    assert len(units) == 120
    assert len({r["locus"] for r in units}) == 120
    assert all(r["ordinal_parity"] == ("ODD" if int(r["star_ordinal"]) % 2 else "EVEN") for r in units)
    return units


def build_matrix(units: list[dict[str, str]]) -> list[dict[str, str | float]]:
    by_locus: dict[str, dict[str, dict[str, str]]] = defaultdict(dict)
    with INTER.open(encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            if r["locus"] in {u["locus"] for u in units}:
                assert r["edition"] not in by_locus[r["locus"]]
                by_locus[r["locus"]][r["edition"]] = r
    out = []
    for u in units:
        assert set(by_locus[u["locus"]]) == set(EDITIONS)
        for edition in EDITIONS:
            vals = extract(by_locus[u["locus"]][edition])
            out.append({**{k: u[k] for k in ("page", "physical_folio", "star_ordinal", "ordinal_parity", "locus")},
                        "edition": edition, **vals})
    assert len(out) == 360
    assert len({(r["locus"], r["edition"]) for r in out}) == 360
    return out


def write_matrix(matrix: list[dict[str, str | float]]) -> None:
    fields = ("page", "physical_folio", "star_ordinal", "ordinal_parity", "locus", "edition") + FEATURES
    with MATRIX.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fields, delimiter="\t", lineterminator="\n")
        w.writeheader()
        for row in matrix:
            w.writerow({k: (f"{row[k]:.12g}" if k in FEATURES else row[k]) for k in fields})


def matrix_contract(matrix, units) -> bool:
    expected = {
        (u["locus"], e): (u["page"], u["physical_folio"], u["star_ordinal"], u["ordinal_parity"])
        for u in units for e in EDITIONS
    }
    if len(matrix) != 360 or len({(r["locus"], r["edition"]) for r in matrix}) != 360:
        return False
    for r in matrix:
        key = (str(r["locus"]), str(r["edition"]))
        if key not in expected:
            return False
        if tuple(str(r[k]) for k in ("page", "physical_folio", "star_ordinal", "ordinal_parity")) != expected[key]:
            return False
        if not all(math.isfinite(float(r[f])) for f in FEATURES):
            return False
    return True


def page_contrasts(matrix: list[dict[str, str | float]], features=FEATURES):
    vals: dict[tuple[str, str, str, str], list[float]] = defaultdict(list)
    page_folio = {}
    for r in matrix:
        page_folio[str(r["page"])] = str(r["physical_folio"])
        for f in features:
            vals[(str(r["page"]), str(r["edition"]), f, str(r["ordinal_parity"]))].append(float(r[f]))
    out = {}
    pages = sorted(page_folio)
    for p in pages:
        for e in EDITIONS:
            for f in features:
                odd = vals[(p, e, f, "ODD")]
                even = vals[(p, e, f, "EVEN")]
                assert odd and even
                out[(p, e, f)] = statistics.fmean(odd) - statistics.fmean(even)
    return pages, page_folio, out


def all_phases(pages: list[str]):
    return [dict(zip(pages, signs)) for signs in itertools.product((-1, 1), repeat=len(pages))]


def reading_effect(contrast, pages, page_folio, phase, edition, feature, omit_folio=None):
    folio_values: dict[str, list[float]] = defaultdict(list)
    for p in pages:
        folio = page_folio[p]
        if folio != omit_folio:
            folio_values[folio].append(phase[p] * contrast[(p, edition, feature)])
    return statistics.fmean(statistics.fmean(v) for v in folio_values.values())


def eligibility(contrast, pages, page_folio, phases, features=FEATURES):
    eligible, detail = [], {}
    for f in features:
        per_reading = {}
        ok = True
        for e in EDITIONS:
            orbit = [reading_effect(contrast, pages, page_folio, ph, e, f) for ph in phases]
            supported_pages = [p for p in pages if abs(contrast[(p, e, f)]) > 1e-15]
            supported_folios = {page_folio[p] for p in supported_pages}
            sd = statistics.pstdev(orbit)
            per_reading[e] = {"sd": sd, "pages": len(supported_pages), "folios": len(supported_folios)}
            ok &= math.isfinite(sd) and sd > 0 and len(supported_pages) >= 5 and len(supported_folios) >= 4
        detail[f] = per_reading
        if ok:
            eligible.append(f)
    return eligible, detail


def robust_stats(contrast, pages, page_folio, phases, eligible):
    effects, scales, robust = {}, {}, {}
    for e in EDITIONS:
        for f in eligible:
            orbit = [reading_effect(contrast, pages, page_folio, ph, e, f) for ph in phases]
            scales[(e, f)] = statistics.pstdev(orbit)
            for i, value in enumerate(orbit):
                effects[(i, e, f)] = value
    for i in range(len(phases)):
        for f in eligible:
            zz = [effects[(i, e, f)] / scales[(e, f)] for e in EDITIONS]
            robust[(i, f)] = max(min(zz), min(-z for z in zz), 0.0)
    return effects, scales, robust


def evaluate_phase(contrast, pages, page_folio, phases, phase, eligible):
    index = next(i for i, ph in enumerate(phases) if ph == phase)
    effects, scales, robust = robust_stats(contrast, pages, page_folio, phases, eligible)
    family = [max((robust[(i, f)] for f in eligible), default=0.0) for i in range(len(phases))]
    rows = []
    for f in eligible:
        observed = robust[(index, f)]
        es = {e: effects[(index, e, f)] for e in EDITIONS}
        signs = {1 if v > 0 else -1 if v < 0 else 0 for v in es.values()}
        direction = next(iter(signs)) if len(signs) == 1 else 0
        raw_p = sum(robust[(i, f)] >= observed - 1e-15 for i in range(len(phases))) / len(phases)
        family_p = sum(v >= observed - 1e-15 for v in family) / len(phases)
        strata_ok = direction != 0
        for wanted in (-1, 1):
            subset = [p for p in pages if phase[p] == wanted]
            if not subset:
                strata_ok = False
                continue
            sf = {p: page_folio[p] for p in subset}
            for e in EDITIONS:
                subeff = reading_effect(contrast, subset, sf, phase, e, f)
                strata_ok &= (subeff > 0) == (direction > 0) and subeff != 0
        deletion_ok = direction != 0
        for folio in sorted(set(page_folio.values())):
            for e in EDITIONS:
                value = reading_effect(contrast, pages, page_folio, phase, e, f, omit_folio=folio)
                deletion_ok &= (value > 0) == (direction > 0) and value != 0
        gates = {
            "same_direction": direction != 0,
            "robust_z": observed >= 2.0 - 1e-15,
            "raw_p": raw_p <= 0.025 + 1e-15,
            "family_p": family_p <= 0.05 + 1e-15,
            "phase_strata": bool(strata_ok),
            "folio_deletions": bool(deletion_ok),
        }
        rows.append({"feature": f, "robust_z": observed, "raw_p": raw_p,
                     "family_p": family_p, "effects": es, "gates": gates,
                     "pass": all(gates.values())})
    return rows, family, index


def synthetic_controls():
    pages = [f"P{i}" for i in range(1, 10)]
    page_folio = {p: f"F{min(i, 7)}" for i, p in enumerate(pages, 1)}
    # Two paired-page folios reproduce the 9-page / 7-folio topology.
    page_folio.update({"P8": "F6", "P9": "F7"})
    phase = dict(zip(pages, (1, 1, -1, 1, -1, 1, 1, -1, 1)))
    phases = all_phases(pages)

    planted = {}
    parity = {}
    leverage = {}
    disagree = {}
    constant = {}
    for p in pages:
        for e in EDITIONS:
            planted[(p, e, "X")] = phase[p] * (1.0 + 0.03 * pages.index(p))
            parity[(p, e, "X")] = 1.0
            leverage[(p, e, "X")] = phase[p] * (20.0 if p == "P1" else 0.0)
            disagree[(p, e, "X")] = phase[p] * (-1.0 if e == "RF1b" else 1.0)
            constant[(p, e, "X")] = 0.0

    planted_rows, _, idx = evaluate_phase(planted, pages, page_folio, phases, phase, ["X"])
    parity_rows, _, _ = evaluate_phase(parity, pages, page_folio, phases, phase, ["X"])
    leverage_rows, _, _ = evaluate_phase(leverage, pages, page_folio, phases, phase, ["X"])
    disagree_rows, _, _ = evaluate_phase(disagree, pages, page_folio, phases, phase, ["X"])
    const_eligible, _ = eligibility(constant, pages, page_folio, phases, ["X"])
    complement = {p: -phase[p] for p in pages}
    complement_rows, _, cidx = evaluate_phase(planted, pages, page_folio, phases, complement, ["X"])
    return {
        "orbit_512": len(phases) == 512,
        "planted_two_sided_minimum": planted_rows[0]["pass"] and planted_rows[0]["family_p"] == 2 / 512,
        "global_complement_invariance": (
            abs(planted_rows[0]["robust_z"] - complement_rows[0]["robust_z"]) < 1e-12
            and planted_rows[0]["family_p"] == complement_rows[0]["family_p"]
            and idx != cidx
        ),
        "parity_only_vetoed": not parity_rows[0]["pass"] and not parity_rows[0]["gates"]["phase_strata"],
        "one_folio_leverage_vetoed": not leverage_rows[0]["pass"] and not leverage_rows[0]["gates"]["folio_deletions"],
        "reading_disagreement_vetoed": not disagree_rows[0]["pass"] and not disagree_rows[0]["gates"]["same_direction"],
        "constant_ineligible": const_eligible == [],
    }


def extraction_fixture() -> bool:
    row = {
        "word_count": "4", "line_carrier": "d",
        "role_sequence": "BOUND_D+Q_BOUND_E FREE_R BOUND_E+REL_I Q_BARE",
        "confirmed_edges": "W1>W2:BOUND_D>Q_BOUND_E;W3>W4:BOUND_E>Q_BARE",
    }
    got = extract(row)
    expected = {
        "WORD_COUNT": 4.0, "LINE_CARRIER_ANY": 1.0, "LINE_CARRIER_T": 0.0,
        "LINE_CARRIER_D": 1.0, "LINE_CARRIER_S": 0.0,
        "ROLE_RATE_BOUND_D": .25, "ROLE_RATE_BOUND_E": .25,
        "ROLE_RATE_Q": .5, "ROLE_RATE_REL_I": .25, "ROLE_RATE_FREE_L": 0.0,
        "ROLE_RATE_FREE_R": .25, "FIRST_HAS_BOUND_D": 1.0,
        "FIRST_HAS_BOUND_E": 0.0, "FIRST_HAS_Q": 1.0,
        "FIRST_HAS_REL_I": 0.0, "FIRST_HAS_FREE_L": 0.0,
        "FIRST_HAS_FREE_R": 0.0, "EDGE_RATE_D_TO_Q": .25,
        "EDGE_RATE_E_TO_Q": .25,
    }
    return got == expected


def main() -> None:
    assert not (HERE / "TARGET_RESULT.json").exists()
    units = load_units()
    matrix = build_matrix(units)
    assert matrix_contract(matrix, units)
    second_matrix = build_matrix(units)
    write_matrix(matrix)
    pages, page_folio, contrast = page_contrasts(matrix)
    phases = all_phases(pages)
    eligible, eligibility_detail = eligibility(contrast, pages, page_folio, phases)

    controls = synthetic_controls()
    controls["extraction_fixture"] = extraction_fixture()
    controls["matrix_cardinality"] = len(matrix) == 360
    controls["matrix_unique_rows"] = len({(r["locus"], r["edition"]) for r in matrix}) == 360
    controls["matrix_deterministic_rebuild"] = matrix == second_matrix
    controls["duplicate_row_guard"] = not matrix_contract(matrix + [dict(matrix[0])], units)
    controls["missing_row_guard"] = not matrix_contract(matrix[:-1], units)
    page_drift = [dict(r) for r in matrix]
    page_drift[0]["page"] = "f999r"
    controls["page_drift_guard"] = not matrix_contract(page_drift, units)
    locus_drift = [dict(r) for r in matrix]
    locus_drift[0]["locus"] = "f999r.1"
    controls["locus_drift_guard"] = not matrix_contract(locus_drift, units)
    controls["page_topology"] = len(pages) == 9 and len(set(page_folio.values())) == 7
    controls["target_phase_unopened"] = not (HERE / "TARGET_RESULT.json").exists()
    own_source = Path(__file__).read_text(encoding="utf-8")
    forbidden_source_tokens = ("first_" + "color", "[" + '"color"' + "]", "[" + "'color'" + "]")
    controls["target_fields_not_referenced"] = not any(token in own_source for token in forbidden_source_tokens)
    controls["eligible_nonempty"] = bool(eligible)
    assert all(controls.values()), {k: v for k, v in controls.items() if not v}

    payload = {
        "experiment": "SCP001",
        "status": "PASS_ANONYMOUS_CONTROLS_TARGET_UNOPENED",
        "inputs": {str(p.relative_to(ROOT)): sha(p) for p in (SOURCE, INTER)},
        "matrix_sha256": sha(MATRIX),
        "matrix_rows": len(matrix),
        "features_frozen": list(FEATURES),
        "eligible_features": eligible,
        "eligibility_detail": eligibility_detail,
        "phase_orbit": len(phases),
        "controls": controls,
        "passed": sum(controls.values()),
        "total": len(controls),
        "target_phase_accessed": False,
        "target_result_exists": False,
        "claim_ceiling": "marker-color-conditioned formal construction only",
    }
    RESULT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# SCP001 anonymous controls\n\n"
        f"**PASS — {sum(controls.values())}/{len(controls)} controls; target unopened.**\n\n"
        f"The target-blind matrix contains {len(matrix)} rows and {len(FEATURES)} frozen "
        f"formal features; {len(eligible)} pass the prespecified support rule. The exact "
        "512-phase engine recovers a distributed planted construction at the expected "
        "two-sided 2/512 floor, preserves global complement symmetry, and rejects "
        "parity-only, one-folio, reading-disagreement, and degenerate controls. Feature "
        "extraction, row identity, page/folio topology, determinism, and target absence "
        "also pass.\n\n"
        "No red/yellow phase field was read and `TARGET_RESULT.json` is absent. These "
        "controls supply no color function, word, lexeme, plaintext, language, or "
        "translation.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
