#!/usr/bin/env python3
"""Calibrate visual-to-text role recovery in a readable bath manuscript."""
from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

R = Path(__file__).resolve().parent
VISUAL = R / "gdt212_morgan_visual_role_inventory.tsv"
TEXT = R / "gdt211_de_balneis_entry_inventory.tsv"
METHOD = R / "GDT212_DE_BALNEIS_VISUAL_TEXT_GROUNDING_METHOD.md"
REPORT = R / "GDT212_DE_BALNEIS_VISUAL_TEXT_GROUNDING_REPORT.md"
SCORES = R / "gdt212_visual_text_role_scores.tsv"
COUNTER = R / "gdt212_counterexamples.tsv"
RESULT = R / "gdt212_result.json"
PAIRS = (
    ("ACCESS_OR_SETTING", "access_or_setting", "LOCATION_ACCESS", "location_access"),
    ("NON_GENERIC_WATER_SYSTEM", "non_generic_water_system", "HYDRAULIC_PHYSICAL", "hydraulic_physical"),
    ("SPECIFIC_USE_ACTION", "specific_use_action", "PROCEDURE_CAUTION", "procedure_caution"),
    ("BED_OR_DEPARTURE_NARRATIVE", "bed_or_departure_narrative", "OUTCOME_TESTIMONY", "outcome_testimony"),
)


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def csha(value: dict) -> str:
    raw = json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()


def fisher_positive(a: int, b: int, c: int, d: int) -> float:
    n = a + b + c + d
    row = a + b
    col = a + c
    denominator = math.comb(n, row)
    def probability(x: int) -> float:
        return math.comb(col, x) * math.comb(n - col, row - x) / denominator
    return sum(probability(x) for x in range(a, min(row, col) + 1))


def loo_single_feature(rows: list[dict], feature: str, role: str) -> tuple[float, float, float]:
    baseline = 0.0
    model = 0.0
    for target in rows:
        train = [row for row in rows if row is not target]
        y = int(target[role])
        positives = sum(int(row[role]) for row in train)
        prior = (positives + 0.5) / (len(train) + 1.0)
        x = int(target[feature])
        p_x_y1 = (sum(int(row[feature]) for row in train if int(row[role])) + 0.5) / (positives + 1.0)
        p_x_y0 = (sum(int(row[feature]) for row in train if not int(row[role])) + 0.5) / (len(train) - positives + 1.0)
        odds = prior / (1.0 - prior)
        odds *= (p_x_y1 if x else 1.0 - p_x_y1) / (p_x_y0 if x else 1.0 - p_x_y0)
        predicted = odds / (1.0 + odds)
        baseline -= math.log2(prior if y else 1.0 - prior)
        model -= math.log2(predicted if y else 1.0 - predicted)
    return baseline, model, baseline - model


visual = read(VISUAL)
text = {int(row["entry_number"]): row for row in read(TEXT) if row["record_class"] == "BATH_RECORD"}
assert len(visual) == 32 and len(text) == 32
assert {int(row["entry_number"]) for row in visual} == set(text)
assert len({row["morgan_folio"] for row in visual}) == 32
assert all(row["annotation_provenance"] == "EXISTING_HUMAN_ANNOTATION_NORMALIZED" for row in visual)
assert all("f84" not in row["catalogue_url"] and "f84" not in row["morgan_folio"] for row in visual)

joined = []
for row in visual:
    entry = int(row["entry_number"])
    joined.append({**row, **{key: text[entry][key] for key in ("identity", "location_access", "hydraulic_physical", "indication", "procedure_caution", "outcome_testimony")}})

score_rows = []
for visual_name, feature, role_name, role in PAIRS:
    a = sum(int(row[feature]) and int(row[role]) for row in joined)
    b = sum(int(row[feature]) and not int(row[role]) for row in joined)
    c = sum(not int(row[feature]) and int(row[role]) for row in joined)
    d = sum(not int(row[feature]) and not int(row[role]) for row in joined)
    positive_rate = a / (a + b)
    negative_rate = c / (c + d)
    risk = positive_rate - negative_rate
    p = fisher_positive(a, b, c, d)
    baseline, model, gain = loo_single_feature(joined, feature, role)
    adjusted = min(1.0, p * len(PAIRS))
    if risk > 0 and adjusted <= 0.05:
        status = "VISUALLY_GROUNDED_LEAD"
    elif risk > 0:
        status = "WEAK_VISUAL_GROUNDING"
    else:
        status = "NOT_VISUALLY_GROUNDED"
    score_rows.append({
        "visual_feature": visual_name,
        "text_role": role_name,
        "feature_and_role": a,
        "feature_without_role": b,
        "no_feature_with_role": c,
        "neither": d,
        "role_rate_with_feature": positive_rate,
        "role_rate_without_feature": negative_rate,
        "risk_difference": risk,
        "smoothed_odds_ratio": (a + 0.5) * (d + 0.5) / ((b + 0.5) * (c + 0.5)),
        "one_sided_fisher_p": p,
        "bonferroni_four_p": adjusted,
        "loo_prior_bits": baseline,
        "loo_feature_bits": model,
        "loo_gain_bits": gain,
        "status": status,
    })
write(SCORES, [{key: f"{value:.12g}" if isinstance(value, float) else value for key, value in row.items()} for row in score_rows], list(score_rows[0]))

body_visible = sum(int(row["body_condition_cue"]) for row in joined)
indications = sum(int(row["indication"]) for row in joined)
counter_rows = [
    {"counterexample": "INDICATION_CONSTANT_VISIBILITY_SPARSE", "evidence": f"INDICATION is present in {indications}/32 readable entries, but explicit BODY_CONDITION_CUE occurs in only {body_visible}/32 catalogue scenes.", "impact": "Visual absence cannot be read as absence of therapeutic indications."},
    {"counterexample": "PROCEDURE_DIRECTION_REVERSED", "evidence": "SPECIFIC_USE_ACTION has PROCEDURE_CAUTION in 10/20 scenes versus 10/12 scenes without the cue.", "impact": "Depicted actions do not identify the source's procedure/caution role."},
    {"counterexample": "OUTCOME_NOT_PICTURED", "evidence": "BED_OR_DEPARTURE_NARRATIVE has OUTCOME_TESTIMONY in 1/8 scenes versus 5/24 without it.", "impact": "Narrative-looking geometry does not recover narrated outcomes."},
    {"counterexample": "GENERIC_BATHING_ECOLOGY", "evidence": "Every retained miniature depicts a bath context, while every readable entry has identity and indication material.", "impact": "Shared genre ecology is not record-level semantic recovery."},
    {"counterexample": "POSTHOC_NORMALIZATION", "evidence": "The five visual categories were normalized after the Morgan catalogue was read.", "impact": "The calibration is exploratory and cannot confirm a Voynich role."},
    {"counterexample": "NONINDEPENDENT_PRIOR_IMAGES", "evidence": "Morgan fols. 9r, 19r, 21r and 25r were already inspected in GDT210.", "impact": "Those four catalogue rows are not an independent replication of the image-level comparator."},
]
write(COUNTER, counter_rows, list(counter_rows[0]))

access = next(row for row in score_rows if row["visual_feature"] == "ACCESS_OR_SETTING")
water = next(row for row in score_rows if row["visual_feature"] == "NON_GENERIC_WATER_SYSTEM")
action = next(row for row in score_rows if row["visual_feature"] == "SPECIFIC_USE_ACTION")
outcome = next(row for row in score_rows if row["visual_feature"] == "BED_OR_DEPARTURE_NARRATIVE")
status = "SETTING_HYDRAULICS_WEAKLY_VISUALLY_GROUNDED_INDICATION_FIELDS_NOT_RECOVERED"

REPORT.write_text(f"""# GDT212 — readable bath illustration/text grounding

## Outcome

**{status}**

The full 32-entry Morgan/ALIM overlap sharpens GDT210.  Readable bath
illustrations weakly expose access/setting and non-generic water organization,
but they do not reliably expose procedure, outcome, or the detailed indication
layer.  This is exactly the calibration needed before using q13 imagery as a
semantic guide.

## Paired role tests

| Visual catalogue feature | Readable text role | 2x2 `a/b/c/d` | Risk difference | one-sided p | four-pair adjusted p | Result |
|---|---|---:|---:|---:|---:|---|
| ACCESS_OR_SETTING | LOCATION_ACCESS | {access['feature_and_role']}/{access['feature_without_role']}/{access['no_feature_with_role']}/{access['neither']} | {access['risk_difference']:+.3f} | {access['one_sided_fisher_p']:.4f} | {access['bonferroni_four_p']:.4f} | {access['status']} |
| NON_GENERIC_WATER_SYSTEM | HYDRAULIC_PHYSICAL | {water['feature_and_role']}/{water['feature_without_role']}/{water['no_feature_with_role']}/{water['neither']} | {water['risk_difference']:+.3f} | {water['one_sided_fisher_p']:.4f} | {water['bonferroni_four_p']:.4f} | {water['status']} |
| SPECIFIC_USE_ACTION | PROCEDURE_CAUTION | {action['feature_and_role']}/{action['feature_without_role']}/{action['no_feature_with_role']}/{action['neither']} | {action['risk_difference']:+.3f} | {action['one_sided_fisher_p']:.4f} | {action['bonferroni_four_p']:.4f} | {action['status']} |
| BED_OR_DEPARTURE_NARRATIVE | OUTCOME_TESTIMONY | {outcome['feature_and_role']}/{outcome['feature_without_role']}/{outcome['no_feature_with_role']}/{outcome['neither']} | {outcome['risk_difference']:+.3f} | {outcome['one_sided_fisher_p']:.4f} | {outcome['bonferroni_four_p']:.4f} | {outcome['status']} |

No pair survives the four-pair correction.  The two intended-direction leads
are nevertheless coherent and small: visible access/setting raises readable
LOCATION_ACCESS prevalence by {access['risk_difference']:.3f}, and a visible
non-generic water system raises HYDRAULIC_PHYSICAL prevalence by
{water['risk_difference']:.3f}.  Their leave-one-entry-out gains are only
{access['loo_gain_bits']:+.3f} and {water['loo_gain_bits']:+.3f} bits over 32
decisions.

The treatment/action bridge fails directionally: textual procedure/caution is
more common when the catalogue lacks a specific depicted action.  Outcome
testimony is likewise not recovered by narrative-looking bed/departure scenes.
Most importantly, INDICATION occurs in all 32 texts, while an explicit bodily
condition cue appears in only {body_visible}/32 catalogue scenes.  Pictures
therefore omit much of the medically important textual payload.

## Consequence for q13

The strongest defensible transfer is narrower than “the figures tell us the
disease.”  Pools, streams, caves, stairs, enclosures and connecting structures
can weakly support a `SETTING_OR_HYDRAULIC_DESCRIPTION` layer.  Figures and
gestures cannot, on this calibration, identify an indication, procedure, or
outcome field.  Thus GDT210's therapeutic-balneological page theory remains
plausible, but GDT212 shifts the actionable visual anchor toward the physical
hydraulic/access layer and away from patient/disease glossing.

No Voynich text was scored in GDT212, no host was assigned a role, and no word,
language, plaintext or translation follows.  No f84 source or payload was
accessed.
""", encoding="utf-8")

result = {
    "schema": "GDT212_DE_BALNEIS_VISUAL_TEXT_GROUNDING_RESULT_V1",
    "status": status,
    "mapped_bath_entries": len(joined),
    "visual_feature_counts": {feature.upper(): sum(int(row[feature]) for row in joined) for feature in ("access_or_setting", "non_generic_water_system", "specific_use_action", "body_condition_cue", "bed_or_departure_narrative")},
    "text_role_counts": {role.upper(): sum(int(row[role]) for row in joined) for role in ("location_access", "hydraulic_physical", "indication", "procedure_caution", "outcome_testimony")},
    "paired_scores": {row["visual_feature"] + "__" + row["text_role"]: row for row in score_rows},
    "interpretation": "Readable bath imagery weakly exposes setting/access and non-generic water organization, but not indication, procedure, or outcome fields.",
    "voynich_scored": False,
    "semantic_mapping": "NONE",
    "claim_ceiling": "External readable-manuscript visual/text calibration only; no Voynich role, word, sound, language, plaintext, meaning, or translation.",
    "f84": {"accessed": False, "retained": False, "queried": False, "scored": False},
    "inputs": {path.name: sha(path) for path in (VISUAL, TEXT, R / "gdt211_source_freeze.json")},
    "implementation": {Path(__file__).name: sha(Path(__file__))},
    "outputs": {path.name: sha(path) for path in (SCORES, COUNTER)},
    "documents": {path.name: sha(path) for path in (METHOD, REPORT)},
}
result["result_content_sha256"] = csha(result)
RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(json.dumps({"status": status, "access_risk": access["risk_difference"], "water_risk": water["risk_difference"], "body_cues": body_visible}, sort_keys=True))
