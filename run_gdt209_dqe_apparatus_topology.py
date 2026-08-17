#!/usr/bin/env python3
"""Build the GDT209 direct-image topology audit."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

R = Path(__file__).resolve().parent
MANIFEST = R / "gdt209_external_image_manifest.tsv"
OBS = R / "gdt209_external_visual_observations.tsv"
COMPARISON = R / "gdt209_topology_comparison.tsv"
VISUAL = R / "gdt208_voynich_visual_evidence.tsv"
METHOD = R / "GDT209_DQE_APPARATUS_TOPOLOGY_METHOD.md"
AUDIT = R / "GDT209_DQE_APPARATUS_TOPOLOGY_SOURCE_AUDIT.md"
REPORT = R / "GDT209_DQE_APPARATUS_TOPOLOGY_REPORT.md"
RESULT = R / "gdt209_result.json"
PARENTS = [R / "gdt208_result.json"]


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
    assert len(images) == 3 and len(observations) == 9 and len(comparisons) == 11
    assert not any(row["page"].startswith("f84") for row in visual)
    q13_differences = [row for row in comparisons if row["verdict"] == "Q13_SPECIFIC_DIFFERENCE"]
    status = "BROAD_ALCHEMICAL_APPARATUS_ECOLOGY_SUPPORTED_SPECIFIC_HOMOLOG_ABSENT"
    report = f'''# GDT209 — direct apparatus images support the class, not a copied q13 design

Status: **{status}**.

## Result

Direct source-bound inspection found genuine quintessence-tradition machinery:

- Wolfenbüttel fol. 40r shows two connected pear-shaped vessels with crossing
  ducts;
- Othmer fol. 10r shows a return-loop vessel and a second vessel with paired
  internal descending ducts;
- Othmer fol. 36r shows paired domed furnaces, nested chambers, fire, and side
  outlets.

This is materially better evidence than a generic claim that medieval
alchemy used vessels. It supports circulation, paired-container, nested-
apparatus, and side-duct geometry as authentic technical imagery near the
Voynich period.

## Specificity failure

The same direct images lack all {len(q13_differences)} q13-specific comparison
features in the frozen table: human figures embedded in the system, repeated
figure/process stages, and colored pools. They also lack a matching color
program. The exact homolog is absent, and the translation bridge is absent.

The Denison study's body-vessel and repeated-ascent/descent description remains
useful scholarly evidence, but its cited manuscript figures were not present
as downloadable assets on the public thesis page and were not treated as
directly inspected here.

## Updated theory

The best current q13 theory remains a medicinal-alchemical circulation,
separation, and staged-transformation system, possibly using figures as
material/process personifications. Its historical plausibility is stronger;
its **iconographic specificity is low**. The evidence supports membership in a
broad apparatus ecology, not descent from Rupescissa's diagram and not the
f77 four-elements-plus-fifth-essence mapping.

## Next discriminating evidence

A useful readable homolog must add what these comparators lack: figures inside
connected liquid channels, repeated process-stage units, and labels with
singular visible ownership. Without that bridge, visual apparatus similarity
cannot decode a Voynich group.

No language, source manuscript, sign value, word, operation, substance,
plaintext, or translation is established. No f84 page is an input or output.
'''
    REPORT.write_text(report, encoding="utf8")
    result = {
        "schema": "GDT209_DQE_APPARATUS_TOPOLOGY_RESULT_V1",
        "status": status,
        "counts": {
            "external_images": len(images),
            "direct_visual_observations": len(observations),
            "topology_axes": len(comparisons),
            "q13_specific_differences": len(q13_differences),
            "exact_q13_homologs": 0,
            "readable_label_bridges": 0,
        },
        "theory_update": {
            "medical_alchemical_apparatus_class_plausibility": "STRENGTHENED",
            "direct_rupescissa_diagram_derivation": "NOT_SUPPORTED",
            "q13_iconographic_specificity": "LOW",
            "f77_four_plus_fifth_refinement": "POSTHOC_UNCONFIRMED",
        },
        "gates": {
            "source_bound_primary_images": True,
            "paired_container_and_duct_analogy": True,
            "figures_inside_connected_system_homolog": False,
            "serial_stage_homolog": False,
            "exact_f77_topology_homolog": False,
            "singular_readable_label_bridge": False,
            "translation_authorized": False,
        },
        "f84": {
            "input_rows": 0,
            "formal_payload_accessed": False,
            "image_opened": False,
        },
        "claim_ceiling": "Broad historical apparatus ecology and low iconographic specificity only; no source, language, sign, word, operation, material, plaintext, or translation.",
        "inputs": {
            MANIFEST.name: sha(MANIFEST),
            OBS.name: sha(OBS),
            COMPARISON.name: sha(COMPARISON),
            VISUAL.name: sha(VISUAL),
            **{path.name: sha(path) for path in PARENTS},
        },
        "implementation": {
            Path(__file__).name: sha(Path(__file__)),
            "validate_gdt209_dqe_apparatus_topology.py": sha(R / "validate_gdt209_dqe_apparatus_topology.py"),
        },
        "documents": {path.name: sha(path) for path in [METHOD, AUDIT, REPORT]},
    }
    result["result_content_sha256"] = csha(result)
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf8")
    print(json.dumps({"status": status, **result["counts"]}, sort_keys=True))


if __name__ == "__main__":
    main()
