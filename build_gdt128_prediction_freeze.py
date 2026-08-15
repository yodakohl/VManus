#!/usr/bin/env python3
"""Build the frozen GDT128 prediction without opening the target image."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "gdt128_prediction.json"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def csha(value):
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(raw).hexdigest()


def main():
    result = {
        "schema": "GDT128_Q20_QOKAL_SHEEDY_TRANSFER_PREDICTION_V1",
        "status": "FROZEN_BEFORE_F103R_STAR15_VISUAL_REVIEW",
        "target": {
            "target_id": "GDT128_F103R_STAR15", "page": "f103r", "physical_folio": "f103",
            "star_ordinal": 15, "open_locus": "f103r.43", "formal_field_locus": "f103r.43",
            "formal_group_indices": [7, 8], "formal_tokens": ["qokal", "sheedy"],
            "prediction": {"rays": 8, "tail": 1, "color": "UNPREDICTED"},
            "canvas_id": "1006254", "image_url": "https://collections.library.yale.edu/iiif/2/1006254/full/full/0/default.jpg",
        },
        "analogy": {
            "reference_page": "f104v", "reference_star_ordinal": 6,
            "reference_field": "qotol|sheedy", "reference_visible_state": "8_RAYS_1_TAIL",
            "exact_hpr2_skeleton_match": False,
            "frozen_mismatch": "qotol uses OT frame; qokal is PAGE_HOST ok plus RIGHT_FAMILY al",
        },
        "postselection": {"gdt127_formal_atlas_used": True, "prior_star_panel_exposed": True, "pristine_blind": False},
        "target_access": {
            "f103r_image_prior_repository_exposure_unrelated": True,
            "exact_star15_rays_or_tail_joined_at_freeze": False,
            "exact_star15_rays_or_tail_inspected_by_gdt128_at_freeze": False,
        },
        "claim_ceiling": "One provenance-qualified postselected visual transfer only; no star meaning, number, role, word, morpheme, POS, sound, language, plaintext, meaning, or translation.",
        "f84r": {key: False for key in ("opened", "retained", "queried", "joined", "scored", "targeted", "predicted")},
        "inputs": {
            "gdt127_result.json": sha(ROOT / "gdt127_result.json"),
            "gdt127_q20_field_visual_leads.tsv": sha(ROOT / "gdt127_q20_field_visual_leads.tsv"),
            "gdt016_group_state_inventory.tsv": sha(ROOT / "gdt016_group_state_inventory.tsv"),
            "experiments/semantic_assumptions/results/source_separator_transcription.tsv": sha(ROOT / "experiments/semantic_assumptions/results/source_separator_transcription.tsv"),
        },
        "implementation": {Path(__file__).name: sha(Path(__file__))},
        "outputs": {"gdt128_frozen_prediction.tsv": sha(ROOT / "gdt128_frozen_prediction.tsv")},
        "documents": {"GDT128_Q20_QOKAL_SHEEDY_TRANSFER_METHOD.md": sha(ROOT / "GDT128_Q20_QOKAL_SHEEDY_TRANSFER_METHOD.md")},
    }
    result["prediction_content_sha256"] = csha(result)
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "target": result["target"]}, sort_keys=True))


if __name__ == "__main__":
    main()
