#!/usr/bin/env python3
"""Build the GDT208 source comparison and bounded content theory."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

R = Path(__file__).resolve().parent
MANIFEST = R / "gdt208_external_source_manifest.tsv"
COMPARISON = R / "gdt208_structural_comparison.tsv"
METHOD = R / "GDT208_MEDICAL_ALCHEMICAL_CIRCULATION_METHOD.md"
AUDIT = R / "GDT208_MEDICAL_ALCHEMICAL_CIRCULATION_SOURCE_AUDIT.md"
REPORT = R / "GDT208_MEDICAL_ALCHEMICAL_CIRCULATION_REPORT.md"
RESULT = R / "gdt208_result.json"
PARENTS = [R / "gdt195_result.json", R / "gdt202_result.json", R / "gdt206_result.json"]
VISUAL = R / "gdt208_voynich_visual_evidence.tsv"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def csha(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True,
                                      separators=(",", ":")).encode()).hexdigest()


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    sources = read(MANIFEST)
    comparisons = read(COMPARISON)
    assert [row["source_id"] for row in sources] == [
        "RUP_WELLCOME_708", "RUP_DENISON_1451", "DONUM_BL_2560",
        "DONUM_BL_2560_F7_IMAGE",
    ]
    assert len(comparisons) == 11
    visual = read(VISUAL)
    pages = {row["page"] for row in visual}
    required = {"f77r", "f78v", "f81r", "f82v", "f83r"}
    assert required <= pages and not any(page.startswith("f84") for page in pages)
    exact_absent = next(row for row in comparisons if row["comparison_id"] == "C08")
    bridge_absent = next(row for row in comparisons if row["comparison_id"] == "C09")
    status = "MEDICAL_ALCHEMICAL_CIRCULATION_THEORY_STRENGTHENED_EXACT_TRANSLATION_KEY_ABSENT"
    report = f'''# GDT208 — the strongest content theory is medicinal-alchemical circulation

Status: **{status}**.

## Leading theory

The q13 apparatus pages most plausibly describe a **medicinal-alchemical
circulation, separation, and staged-transformation system**.  Their human
figures are provisionally better modeled as personified materials or process
states inside an apparatus than as a literal catalogue of bathers.

This theory now explains several observations jointly:

- a near-contemporary medical-alchemical work combines distillation of wine,
  plants, and minerals with medical remedies;
- its illustrated apparatus circulates material repeatedly from bottom to top
  and back through side tubes;
- its prose uses body anatomy as the apparatus metaphor;
- a separate late-fifteenth-century alchemical series places kings, queens,
  a man, worms, flowers, and roses inside colored flasks as process imagery;
- q13 independently contains figures, colored pools, tubes, connected
  top/bottom structures, prose, and local labels.

## The f77 refinement

The strongest new speculative reading is:

> four emitting boundaries expel or register the four corruptible elemental
> fractions, while the one non-emitting boundary retains the fifth essence.

Rupescissa's readable process supplies the external four-versus-fifth
distinction and repeated pipe circulation.  It does **not** supply six ordered
states, five boundaries, or the exact output mask.  Consequently this is a
post-hoc process hypothesis, not confirmation and not a restoration of the
withdrawn COLD/DRY/HOT/MOIST word glosses.

## Hard negatives

- {exact_absent['voynich_observation']}.
- {bridge_absent['voynich_observation']}.
- The external *Donum Dei* black/white/red sequence does not match a frozen
  q13 color progression.
- Static alphabetic, word-codebook, expansion, consonantal, and homophonic
  language channels remain failed.

## Novel predictions

1. A true homolog should depict recirculation through a body-like apparatus
   and explicitly distinguish four removable fractions from one retained
   product.
2. Independent q13 flow evidence should identify repeated ascent/descent or
   return circulation, not a single one-way source-to-destination pipe.
3. Figure identity should track material/process state more consistently than
   human biography, patient identity, or literal bathing activity.
4. A readable parallel should align labels to apparatus stages or material
   states; an isolated visual resemblance without singular label ownership
   must fail the translation bridge.
5. If the f77 refinement is right, the central non-emission should be a
   retention/repetition phase rather than a fifth discarded output.

The theory narrows the content search, but no Voynich source group receives a
meaning.  No language, sound, word, operation, material, plaintext, or
translation is established.  The final inputs are f84-free.  An initial
uncommitted builder pass list-loaded the global public human page-annotation
table before filtering and thereby materialized its f84r description row in
memory; it was not displayed, retained, joined, or used, and no f84r
transcription/formal payload or image was opened.
'''
    REPORT.write_text(report, encoding="utf8")
    result = {
        "schema": "GDT208_MEDICAL_ALCHEMICAL_CIRCULATION_RESULT_V1",
        "status": status,
        "counts": {
            "external_source_records": len(sources),
            "structural_comparisons": len(comparisons),
            "non_f84_visual_evidence_pages": len(pages),
            "exact_homologs": 0,
            "singular_readable_voynich_bridges": 0,
        },
        "leading_content_theory": "Medicinal-alchemical circulation, separation, and staged transformation with personified material/process states.",
        "f77_exploratory_refinement": "Four emissions may register expelled elemental fractions while the non-emission retains a fifth essence.",
        "semantic_status": "HYPOTHESIS_GENERATION_ONLY",
        "gates": {
            "near_contemporary_medical_distillation_context": True,
            "top_bottom_pipe_circulation_analogy": True,
            "personified_figure_in_vessel_analogy": True,
            "exact_f77_six_state_homolog": False,
            "singular_readable_voynich_label_bridge": False,
            "translation_authorized": False,
        },
        "claim_ceiling": "A leading content-domain theory for non-f84 q13 imagery; no source-group meaning, language, sound, word, operation, material, plaintext, or translation.",
        "f84": {
            "final_input_rows": 0,
            "superseded_builder_global_human_atlas_loaded_before_filter": True,
            "superseded_f84r_public_page_description_displayed": False,
            "superseded_f84r_public_page_description_retained_or_used": False,
            "f84r_transcription_or_formal_payload_accessed": False,
            "f84r_image_opened": False,
        },
        "inputs": {
            MANIFEST.name: sha(MANIFEST),
            COMPARISON.name: sha(COMPARISON),
            VISUAL.name: sha(VISUAL),
            **{path.name: sha(path) for path in PARENTS},
        },
        "implementation": {
            Path(__file__).name: sha(Path(__file__)),
            "validate_gdt208_medical_alchemical_circulation.py": sha(R / "validate_gdt208_medical_alchemical_circulation.py"),
        },
        "documents": {path.name: sha(path) for path in [METHOD, AUDIT, REPORT]},
    }
    result["result_content_sha256"] = csha(result)
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf8")
    print(json.dumps({"status": status, **result["counts"]}, sort_keys=True))


if __name__ == "__main__":
    main()
