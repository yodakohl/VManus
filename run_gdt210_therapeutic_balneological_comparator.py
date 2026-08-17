#!/usr/bin/env python3
"""Build the GDT210 therapeutic-bath versus apparatus comparison."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

R = Path(__file__).resolve().parent
MANIFEST = R / "gdt210_balneological_image_manifest.tsv"
OBS = R / "gdt210_balneological_observations.tsv"
COMPARISON = R / "gdt210_theory_comparison.tsv"
VISUAL = R / "gdt208_voynich_visual_evidence.tsv"
METHOD = R / "GDT210_THERAPEUTIC_BALNEOLOGICAL_COMPARATOR_METHOD.md"
AUDIT = R / "GDT210_THERAPEUTIC_BALNEOLOGICAL_COMPARATOR_SOURCE_AUDIT.md"
REPORT = R / "GDT210_THERAPEUTIC_BALNEOLOGICAL_COMPARATOR_REPORT.md"
RESULT = R / "gdt210_result.json"
PARENTS = [R / "gdt208_result.json", R / "gdt209_result.json"]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def csha(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, ensure_ascii=True,
                     separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    images = read(MANIFEST)
    observations = read(OBS)
    comparisons = read(COMPARISON)
    visual = read(VISUAL)
    assert len(images) == 4 and len(observations) == 9 and len(comparisons) == 13
    assert not any(row["page"].startswith("f84") for row in visual)
    bath_leads = [r for r in comparisons if r["assessment"] == "BALNEOLOGY_SPECIFIC_LEAD"]
    alch_leads = [r for r in comparisons if r["assessment"] == "ALCHEMICAL_HYDRAULIC_SECONDARY_LEAD"]
    status = "THERAPEUTIC_BALNEOLOGY_LEADING_Q13_CONTENT_THEORY_HYDRAULIC_HYBRID_PROVISIONAL"
    report = f'''# GDT210 — therapeutic balneology now leads the q13 content theory

Status: **{status}**.

## What changed

The inspected alchemical manuscripts established a broad apparatus ecology,
but Morgan MS G.74 supplies a much closer readable visual package. Its ca. 1400
*De balneis Puteolanis* fol. 21r contains vertically tiered figures, two lower
bathing pools, a central descending watercourse, and one architectural frame.
Fols. 9r, 19r, and 25r independently show groups immersed in pools, water
running beside or beneath structures, domes, arches, stairs, and caves.

Across the transparent post-hoc comparison, {len(bath_leads)} axes are specific
leads for the bath theory and {len(alch_leads)} is a secondary lead for the
alchemical/hydraulic theory. No composite score or p-value is claimed.

## Leading theory

The best current q13 content theory is a **therapeutic balneological regimen or
bath-site compendium rendered with a schematic hydraulic/process layer**.
The figures are more likely literal therapeutic subjects or bathers than
personified chemical substances. Pools and local structures likely distinguish
bath installations, water sources, treatment positions, or procedures.

Alchemical circulation remains useful as a secondary analogy for the long
ducts, returns, nested containers, and preparation layer. The most economical
current account is therefore hybrid at the document level: readable-medieval-
bath content plus unusually abstract hydraulic/technical rendering—not a
direct copy of either comparator.

## What this predicts

1. q13 prose blocks should organize primarily by bath/pool installation or
   treatment episode, not one text label per drawn figure.
2. Figure pose and placement should covary with treatment mode—immersion,
   pouring, drinking, sweating, entry, or exit—more than with a fixed sequence
   of alchemical colors.
3. Independently recoverable flow direction should often be supply/drainage
   between bath levels, while only a minority of paths need form closed loops.
4. Repeated visual configurations should preserve a record template even when
   the depicted people vary.
5. A readable homolog that supplies bath-specific captions plus singular
   graphical ownership would be more valuable than another unlabeled vessel.

## Awkward evidence

- q13 has long and bifolio-crossing duct networks not present in the four
  inspected Morgan miniatures; this is why the hydraulic/alchemical layer
  remains live.
- Morgan's miniatures name bath sites in readable surrounding text, but do not
  place a singular label beside every bather. q13 ownership is likewise weak.
- Nothing in the comparison assigns a Voynich group to a bath, disease,
  procedure, body part, water source, or material.
- The exact f77 six-state/five-edge/four-output-one-hold topology remains
  unmatched by both comparator families.

This is a page-genre/content theory, not a translation. No language, sign
value, word, operation, disease, treatment, place, plaintext, or source
manuscript is established. No f84 page is an input or output.
'''
    REPORT.write_text(report, encoding="utf8")
    result = {
        "schema": "GDT210_THERAPEUTIC_BALNEOLOGICAL_COMPARATOR_RESULT_V1",
        "status": status,
        "counts": {
            "external_images": len(images),
            "direct_visual_observations": len(observations),
            "comparison_axes": len(comparisons),
            "balneology_specific_leads": len(bath_leads),
            "alchemical_hydraulic_secondary_leads": len(alch_leads),
            "exact_translation_bridges": 0,
        },
        "leading_content_theory": "Therapeutic balneological regimen or bath-site compendium rendered with a schematic hydraulic/process layer.",
        "figure_role_hypothesis": "Literal therapeutic subjects or bathers are now favored over personified chemical materials.",
        "alchemical_role": "Secondary analogy for long ducts, returns, nested containers, and a possible preparation layer.",
        "analysis_status": "POSTHOC_EXPLORATORY_THEORY_RANKING",
        "gates": {
            "figures_in_water_package": True,
            "multi_level_watercourse_package": True,
            "serial_bath_document_practice": True,
            "cross_page_duct_explained_by_bath_comparator": False,
            "singular_readable_label_bridge": False,
            "translation_authorized": False,
        },
        "f84": {"input_rows": 0, "formal_payload_accessed": False, "image_opened": False},
        "claim_ceiling": "Provisional q13 page genre and figure-role theory only; no Voynich word, bath, disease, procedure, place, language, plaintext, or translation.",
        "inputs": {
            MANIFEST.name: sha(MANIFEST), OBS.name: sha(OBS),
            COMPARISON.name: sha(COMPARISON), VISUAL.name: sha(VISUAL),
            **{p.name: sha(p) for p in PARENTS},
        },
        "implementation": {
            Path(__file__).name: sha(Path(__file__)),
            "validate_gdt210_therapeutic_balneological_comparator.py": sha(R / "validate_gdt210_therapeutic_balneological_comparator.py"),
        },
        "documents": {p.name: sha(p) for p in [METHOD, AUDIT, REPORT]},
    }
    result["result_content_sha256"] = csha(result)
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf8")
    print(json.dumps({"status": status, **result["counts"]}, sort_keys=True))


if __name__ == "__main__":
    main()
