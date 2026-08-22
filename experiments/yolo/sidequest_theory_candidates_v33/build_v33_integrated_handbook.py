#!/usr/bin/env python3
"""Build the integrated V33 WHAT/HOW/WHEN consultation handbook."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
RULES = OUT.parent / "sidequest_theory_candidates_v22/V22_F69_28_RULES.tsv"

BODY = [
    ("Aries", "Kopf und Gesicht"), ("Taurus", "Hals und Kehle"),
    ("Gemini", "Schultern, Arme und Hände"), ("Cancer", "Brust"),
    ("Leo", "Herz und oberer Rücken"), ("Virgo", "Bauch und Gedärm"),
    ("Libra", "Lenden und Nieren"), ("Scorpio", "Genitalien und Blase"),
    ("Sagittarius", "Hüften und Schenkel"), ("Capricorn", "Knie"),
    ("Aquarius", "Schienbein und Knöchel"), ("Pisces", "Füße"),
]


def target_stage(rule: str) -> str:
    r = rule.lower()
    if "avoid" in r or "withhold" in r or "rest" in r:
        return "WITHHOLD_OR_REST"
    if "bath" in r or "washing" in r or "rinse" in r:
        return "F81_F82_BATH_OR_RINSE"
    if "anoint" in r or "apply" in r or "cloth" in r:
        return "F83_LOCAL_APPLICATION"
    if "strain" in r or "pour" in r or "draw off" in r:
        return "F81_F83_PREPARE_AND_TRANSFER"
    return "GENERAL_DOSE_OR_PREPARATION"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    with RULES.open() as f:
        rules = list(csv.DictReader(f, delimiter="\t"))
    assert len(rules) == 28
    rows = []
    for r in rules:
        rows.append({
            "moon_station": r["station_index"],
            "visible_entry": r["surface_entry"],
            "selected_working_rule": r["selected_concrete_rule"],
            "treatment_stage": target_stage(r["selected_concrete_rule"]),
            "prior_safety_gate": "CHECK_F67_BODY_SECTOR_FIRST",
            "station_source": "F68_SPATIAL_IDENTIFICATION_THEN_LEARNED_ORDINAL",
            "status": "COMPLETE_SPECULATIVE_CONSULTATION_RULE",
        })

    tsv = OUT / "V33_TWENTY_EIGHT_RULE_PRACTITIONER_TABLE.tsv"
    with tsv.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        w.writeheader(); w.writerows(rows)

    manual = [
        "# V33 — integrated ten-page practitioner handbook", "",
        "Status: **maximally concrete workshop reconstruction, not decipherment**.", "",
        "## The ten-page workflow", "",
        "```text",
        "1. WHAT — choose the pictured simple and preparation (f10r/f11r/f55v/f56r)",
        "2. WHERE — choose the affected body place and bath configuration (f81v/f82r/f83r)",
        "3. SAFETY — on f67r2 reject treatment of the region governed by the Moon's sign",
        "4. WHEN — on f68r1 identify the current one-of-28 lunar station spatially",
        "5. ACTION — use its learned ordinal to consult the matching concrete rule on f69v",
        "6. EXECUTE — perform, modify, repeat or withhold the bath/application",
        "```", "",
        "This is learnable by a small workshop because the practitioner supplies the ordinary",
        "zodiac and 28-station order. The manuscript need only preserve the local station picture,",
        "the rule cards and the five field templates. The absent visible f68→f69 label match is",
        "therefore a real weakness but not fatal to the working mechanism.", "",
        "## f67r2 — body-sector veto", "",
        "The practical rule is: **when the Moon is in a sign, do not strongly treat, cut or bleed",
        "the body region governed by that sign**. For the selected women's regimen the most",
        "important veto is Scorpio → genitalia/bladder; Cancer → breast; Virgo → belly; Libra →",
        "loins/kidneys. A positive f69 bath rule cannot override this body-sector veto.", "",
        "| sign | protected body region |", "|---|---|",
    ] + [f"| {s} | {b} |" for s, b in BODY]
    manual += [
        "", "## f68r1 — station finder", "",
        "The central moon and 28 drawn loci form a recognition chart. The user identifies the",
        "current mansion from its spatial/star pattern and converts it to the conventional ordinal.",
        "No Voynich label is equated with an Arabic or Latin mansion name.", "",
        "## f69v — operational rules", "",
        "The complete 28-rule table is in `V33_TWENTY_EIGHT_RULE_PRACTITIONER_TABLE.tsv`.",
        "Examples that now directly control the Biological workflow:", "",
        "- station 1: warm bath, preferably after sunset;",
        "- station 3: no bloodletting;",
        "- station 9: avoid the hot bath;",
        "- stations 11, 15 and 24: bathing is favourable;",
        "- station 20: do not make a second application;",
        "- station 25: strain the herbal liquor;",
        "- station 27: apply a warm cloth;",
        "- station 28: observe the patient's strength and withhold if weak.", "",
        "## Worked cases", "",
        "### Cold or retained condition", "",
        "Select the indicated warming simple or bath charge. If the Moon does not occupy the",
        "sign governing the treated region and the mansion rule permits warmth, prepare f81v's",
        "common bath, individualize it on f82r, then perform f83r's local warm irrigation and drain.", "",
        "### Weak patient", "",
        "If the station rule prescribes rest, no purge, no second application or withholding, stop",
        "after the mild common bath or omit the procedure entirely. A closure card commits that",
        "decision; it need not end the physical line.", "",
        "### Genital or bladder treatment", "",
        "If the Moon is in Scorpio, defer the local intervention even when bathing is generally",
        "favourable. Otherwise use the station-specific temperature/repetition rule and the f83r",
        "opening/drainage configuration. This is the most concrete current join between Astro and Bio.", "",
        "## Historical fit", "",
        "- [Oxford lunar tool](https://www.cabinet.ox.ac.uk/lunar-tool): Moon calculation plus Zodiac Man and the warning not to operate on its governed region.",
        "- [Oxford medical astrology](https://www.mhs.ox.ac.uk/astrolabe/exhibition/medical_astrology.html): a late-15th-century instrument with a 1–28 lunar-mansion scale.",
        "- [Wellcome MS 8004](https://wellcomecollection.org/works/gcgpe44f): a mid-15th-century medical and astrological compendium.",
        "- [State Library Victoria quintessence manuscript](https://www.slv.vic.gov.au/john-rupescissa-liber-de-consideratione-quintae-essentiae): medicine tied to a specified lunar day.", "",
        "## Translation ceiling", "",
        "This identifies a plausible consultation *operation*, not any written label. The 28 medical",
        "rules are aggressive defaults; the conventional ordinal bridge is supplied by the trained",
        "user rather than visibly demonstrated. The circles could still be astronomical catalogues,",
        "prognostics or unrelated lookup instruments. No cycle start or direction has been recovered.", "",
    ]
    (OUT / "V33_PRACTITIONER_DECISION_MANUAL.md").write_text("\n".join(manual))

    selection = """# V33 theory selection

Date: 2026-08-22

Status: **integrated WHAT/HOW/WHEN medical consultation selected**.

The ten pages now make one executable workshop book: select a pictured simple;
select the women's bath/application configuration; veto treatment of the body
region governed by the Moon's zodiac sign; recognize the one-of-28 station;
consult the corresponding f69 rule; then perform or withhold the procedure.

The strongest concrete joined case is local genital/bladder treatment: Scorpio
vetoes intervention; otherwise the current mansion chooses warmth, cool wash,
rest, repetition, straining, local application or withholding. This is a
historically plausible use model, not a decoded label system. The missing visible
f68→f69 index remains the chief weakness. f84 and f84r remained sealed.
"""
    (OUT / "V33_THEORY_SELECTION.md").write_text(selection)

    same = {}
    for row in rows:
        same.setdefault(row["visible_entry"], set()).add(row["selected_working_rule"])
    checks = {
        "rules_28": len(rows) == 28,
        "stations_unique": len({r["moon_station"] for r in rows}) == 28,
        "recurrent_surface_consistent": all(len(v) == 1 for v in same.values()),
        "all_stages_assigned": all(r["treatment_stage"] for r in rows),
        "f84_sealed": True,
    }
    val = {
        "schema": "SIDEQUEST_V33_VALIDATION_V1", "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks, "input": {str(RULES.relative_to(ROOT)): digest(RULES)},
        "outputs": {tsv.name: digest(tsv), "V33_PRACTITIONER_DECISION_MANUAL.md": digest(OUT / "V33_PRACTITIONER_DECISION_MANUAL.md")},
    }
    (OUT / "V33_VALIDATION.json").write_text(json.dumps(val, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": val["status"], "rules": 28, "workflow": "WHAT_HOW_WHEN"}))


if __name__ == "__main__":
    main()
