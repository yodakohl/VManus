#!/usr/bin/env python3
"""Single registered SCP001 target invocation. Do not rerun or retune."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

import run_star_color_anonymous_controls as core

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
BIND = HERE / "source_phase_binding.tsv"
MATRIX = HERE / "anonymous_feature_matrix.tsv"
CONTROL = HERE / "anonymous_control_result.json"
AUDIT = HERE / "prescore_audit.json"
TARGET = HERE / "TARGET_RESULT.json"
ROWS = HERE / "target_feature_results.tsv"
REPORT = ROOT / "experiments/semantic_assumptions/results/star_color_target_report.md"
EXPECTED_HASHES = {
    "binding": "535e34dcbef6ce3f34b61d8f8d990ce02152c844a8ef4acbfd3dd5063b13697e",
    "matrix": "e6f7a83cc6816d2c811e27753cca92b2257c35b919e38e55e377501ea4bd5204",
    "control": "614bde4a4a145b345337b105daa62a069a9392e7386127048eedfe733b56495c",
    "audit": "9dc70b8fc4df1b867e9ec255612767ceef2576f0d08c2499375d7d7ce377620e",
    "engine": "670530f4b2a144ea35cb1b9eeafd37677ef3a458e712ed330be82a10cd88d615",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_tsv(path: Path):
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def load_matrix():
    out = []
    for r in read_tsv(MATRIX):
        out.append({
            **{k: r[k] for k in ("page", "physical_folio", "star_ordinal", "ordinal_parity", "locus", "edition")},
            **{f: float(r[f]) for f in core.FEATURES},
        })
    return out


def subgroup_effects(contrast, pages, page_folio, phase, feature, wanted):
    subset = [p for p in pages if phase[p] == wanted]
    sf = {p: page_folio[p] for p in subset}
    return {e: core.reading_effect(contrast, subset, sf, phase, e, feature) for e in core.EDITIONS}


def deletion_effects(contrast, pages, page_folio, phase, feature):
    return {
        folio: {e: core.reading_effect(contrast, pages, page_folio, phase, e, feature, omit_folio=folio)
                for e in core.EDITIONS}
        for folio in sorted(set(page_folio.values()))
    }


def main() -> None:
    assert not TARGET.exists(), "registered target already exists; rerun forbidden"
    assert not ROWS.exists(), "target row artifact already exists; rerun forbidden"
    assert sha(BIND) == EXPECTED_HASHES["binding"]
    assert sha(MATRIX) == EXPECTED_HASHES["matrix"]
    assert sha(CONTROL) == EXPECTED_HASHES["control"]
    assert sha(AUDIT) == EXPECTED_HASHES["audit"]
    assert sha(HERE / "run_star_color_anonymous_controls.py") == EXPECTED_HASHES["engine"]
    control = json.loads(CONTROL.read_text(encoding="utf-8"))
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    assert control["status"] == "PASS_ANONYMOUS_CONTROLS_TARGET_UNOPENED"
    assert control["passed"] == control["total"] == 19
    assert audit["status"] == "PASS_PRESCORE_AUDIT_TARGET_AUTHORIZED_UNRUN"
    assert audit["passed"] == audit["total"] == 21
    assert control["matrix_sha256"] == audit["matrix_sha256"] == sha(MATRIX)

    phase_rows = read_tsv(BIND)
    phase = {r["page"]: 1 if r["first_color"] == "RED" else -1 for r in phase_rows}
    assert len(phase) == 9 and set(phase.values()) == {-1, 1}
    assert [p for p, value in phase.items() if value == -1] == ["f113r", "f114v"]

    matrix = load_matrix()
    pages, page_folio, contrast = core.page_contrasts(matrix)
    assert set(pages) == set(phase)
    phases = core.all_phases(pages)
    eligible, detail = core.eligibility(contrast, pages, page_folio, phases)
    assert eligible == control["eligible_features"] == audit["eligible_features"]
    rows, family_orbit, target_index = core.evaluate_phase(
        contrast, pages, page_folio, phases, phase, eligible
    )

    complete = []
    for row in rows:
        f = row["feature"]
        normal = subgroup_effects(contrast, pages, page_folio, phase, f, 1)
        reversed_phase = subgroup_effects(contrast, pages, page_folio, phase, f, -1)
        deletions = deletion_effects(contrast, pages, page_folio, phase, f)
        assert row["gates"]["phase_strata"] == all(
            value != 0 and (value > 0) == (next(iter({1 if x > 0 else -1 if x < 0 else 0 for x in row["effects"].values()})) > 0)
            for value in list(normal.values()) + list(reversed_phase.values())
        ) if row["gates"]["same_direction"] else not row["gates"]["phase_strata"]
        assert all(math.isfinite(float(x)) for x in row["effects"].values())
        complete.append({**row, "red_first_effects": normal,
                         "yellow_first_effects": reversed_phase,
                         "folio_deletion_effects": deletions})

    candidates = [r["feature"] for r in complete if r["pass"]]
    family_bytes = "\n".join(f"{x:.17g}" for x in family_orbit).encode()
    payload = {
        "experiment": "SCP001",
        "status": "FINAL_CONFIRMATION_FORMAL_COLOR_CONSTRUCTION" if candidates else "FINAL_NONCONFIRMATION",
        "decision": "CONFIRM" if candidates else "NONCONFIRMATION",
        "inputs": {
            str(BIND.relative_to(ROOT)): sha(BIND),
            str(MATRIX.relative_to(ROOT)): sha(MATRIX),
            str(CONTROL.relative_to(ROOT)): sha(CONTROL),
            str(AUDIT.relative_to(ROOT)): sha(AUDIT),
        },
        "target_phase": phase,
        "target_assignment_index": target_index,
        "phase_orbit": len(phases),
        "family_orbit_sha256": hashlib.sha256(family_bytes).hexdigest(),
        "features_frozen": list(core.FEATURES),
        "eligible_features": eligible,
        "eligibility_detail": detail,
        "feature_results": complete,
        "passing_features": candidates,
        "claim_ceiling": "marker-color-conditioned formal construction only",
        "forbidden": ["color meaning", "recipe class", "number", "lexeme", "plaintext", "language", "translation"],
    }

    fields = ("feature", "robust_z", "raw_p", "family_p", "same_direction",
              "phase_strata", "folio_deletions", "pass")
    with ROWS.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fields, delimiter="\t", lineterminator="\n")
        w.writeheader()
        for r in complete:
            w.writerow({
                "feature": r["feature"], "robust_z": f'{r["robust_z"]:.12g}',
                "raw_p": f'{r["raw_p"]:.12g}', "family_p": f'{r["family_p"]:.12g}',
                "same_direction": int(r["gates"]["same_direction"]),
                "phase_strata": int(r["gates"]["phase_strata"]),
                "folio_deletions": int(r["gates"]["folio_deletions"]),
                "pass": int(r["pass"]),
            })
    payload["target_rows_sha256"] = sha(ROWS)
    TARGET.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    ranked = sorted(complete, key=lambda r: (r["family_p"], -r["robust_z"], r["feature"]))
    best = ranked[0]
    if candidates:
        decision = (
            f"**CONFIRM — {len(candidates)} feature(s) pass: {', '.join(candidates)}.**"
        )
    else:
        decision = "**NONCONFIRMATION — zero of 15 eligible formal features passes.**"
    REPORT.write_text(
        "# SCP001 alternating star-color target\n\n"
        f"{decision}\n\n"
        f"The single registered 512-phase target was invoked once. The strongest "
        f"feature is `{best['feature']}` with robust z {best['robust_z']:.6f}, raw "
        f"p {best['raw_p']:.6f}, and familywise p {best['family_p']:.6f}. "
        f"Its phase-stratum gate is {best['gates']['phase_strata']} and its every-folio "
        f"deletion gate is {best['gates']['folio_deletions']}.\n\n"
        "This result concerns only whether red versus faded-yellow marginal-star "
        "markers condition already established formal line structure. It supplies no "
        "meaning for either color, recipe class, number, word, lexeme, plaintext, "
        "language, or translation. Independent target reconstruction is mandatory.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
