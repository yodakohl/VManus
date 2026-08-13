#!/usr/bin/env python3
"""Build the exploratory GDT002 contact/gap acquisition result.

The visual calls are sealed human/AI review judgments, not computed from
pixels.  This builder records them, binds the exact public IIIF regions, and
applies only the preregistered capacity gate.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SELECTION = ROOT / "gdt002_contact_gap_selection.tsv"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_tsv(path: Path, records: list[dict[str, object]], fields: list[str]) -> None:
    out = io.StringIO(newline="")
    writer = csv.DictWriter(out, fieldnames=fields, delimiter="\t", lineterminator="\n")
    writer.writeheader()
    writer.writerows(records)
    path.write_text(out.getvalue(), encoding="utf-8")


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


FULL_HASH = {
    "1006233": "3b553c70d0c068cb39a276d391127165c5d9d868ec08e7f5eb2e73b32bb95d1e",
    "1006247": "111f6dfc34b8ecb9230cb5a0d144afef4cbd788048ddda2f440108941c91d5e5",
    "1006248": "6dcf72a0d7eac14da2232987c9cc1521e6d70c9f0f92d3eb39b55fc075520429",
}

# target_id, context xywh, target xywh, context hash, target hash,
# localizer confidence, neutral localizer note, reviewer state/confidence/note.
SEALED = {
    "CG66BD2173E10A": ("6420,2780,1000,700", "6835,3050,245,135", "708c7d1136e422b650b7d6aa8813723859187c7d3bac7d8da2e03073214d2e62", "4f5e9b09ee5e352f04627825b73d7abc11fb31320a41ddc074073a3fdc601be3", "HIGH", "Lower-row inscription beneath a faded dark-leaf drawing; final characters are faint.", "CONTACT", "MEDIUM", "A descending non-writing contour converges with the upper stroke of a tall central writing form; fading limits confidence."),
    "CGE9931A3D31E7": ("6980,2780,1000,700", "7310,3035,355,170", "0bb5617a09e7b41701569deee08c2b64996ebd616b40beb3ac3af99bda327a73", "6058b041bbfea7df1db02413bb7c6ced6a1577655414fa817591df0a7200d572", "MEDIUM", "Very faint lower-row inscription across a pale painted, fold-adjacent region.", "UNCERTAIN", "MEDIUM", "Writing is faint and embedded in mottled wash beside fine contours, preventing a secure boundary call."),
    "CG11CFD3CF48C5": ("7380,2900,1000,650", "7595,3160,505,155", "1e09b019321eb549ea58b49646b13b80d39ab1dd82150cba0225312b86ca33c4", "561774cf942f7d0fec48b15ba8411876fd595a608fed39afe70b9163824d3c2d", "HIGH", "Clear longer lower-row inscription immediately west of a large tan-root drawing.", "CONTACT", "HIGH", "A narrow diagonal non-writing contour traverses the inscription row and overlaps a central writing stroke."),
    "CGF1A0593EF78D": ("430,700,700,750", "646,843,292,137", "72c8330df37375a7292e4a72165eeb51aa89d410a406f0dc36f081a104019e17", "f43e4b0d3ac364ad313cf6c2101042197f7b4e45d7cb12ffc4d80102c67078fe", "HIGH", "Upper label immediately east of the first drawn unit in the registered row.", "CLEAR_GAP", "HIGH", "Visible background surrounds the inscription; no writing stroke reaches a nearby non-writing contour."),
    "CG222DBE381C0D": ("1110,650,650,850", "1295,842,225,125", "4981ef49910392f78f2983c008c74ae83b07b6aa541c98dbf9223cc8bc9591cf", "4a8676dc6698f01a16b78c185348b5005ecbaf347924b5752557a486fedc76a8", "HIGH", "Upper label immediately east of the third drawn unit, above its lower strokes.", "CONTACT", "HIGH", "A long ascending non-writing contour enters the inscription and overlaps the left portion of a writing form."),
    "CGDB3398C41893": ("1430,620,650,850", "1570,830,230,135", "d5e5b0a170d63bb553c9d3644a78d5c56c357c9d32cdba5db0a322e636f41cc7", "e2db4653091620b4c6c2b2f85dde0ccc1cb69ea6b24d0c4e07bbc8b38f74f927", "HIGH", "Upper label in the interval between the fourth and fifth drawn units.", "CLEAR_GAP", "HIGH", "Continuous background separates the target writing from illustrated contours below and to the right."),
    "CG47132E3DBB2B": ("2140,580,600,850", "2305,795,245,155", "e043c4696315dbfed9f4fc48b6391885fef7229173d406b17611e105b4434d93", "923d9ec2e5cad94dbdfedcce9ca84eaeedddfa63a9afa516f7bb0ba12d04300c", "HIGH", "Label east of the sixth drawn unit, beside its upright lower contour.", "CLEAR_GAP", "MEDIUM_HIGH", "Narrow visible background gaps separate the inscription from vertical non-writing contours on both sides."),
    "CG8B5118853586": ("250,700,900,650", "620,1070,330,120", "c47bdc4144f9667a5e3bbceb945c3d1a73478aecd459f74ce7f14794a6a57f06", "d47f0d7ec26933e0bc27a36d6be70bb4ffcfc43cfb0d18cb6a1ba46f4cdef497", "HIGH", "Lower label beside the second drawn unit in the registered row.", "CONTACT", "HIGH", "A narrow descending non-writing contour visibly meets the upper part of a central writing stroke."),
    "CG8D116F0B9695": ("700,650,900,750", "970,1040,310,120", "6ff9c164825cdb61936f31cf16761b6a33bcf6e7d67a0be84c5b7795cb06863e", "4f1438a7e524a3a4596c3947baa1880ef061c298d9ef0ed1d3e4a04e49f9773a", "HIGH", "Lower label beside the third drawn unit in the registered row.", "CLEAR_GAP", "HIGH", "Continuous background separates the inscription from pointed contours above and a broad contour at right."),
    "CGF255D39AC5D6": ("1100,650,800,650", "1400,1000,300,120", "8a0affe34badcb95390ad6ff9b77e68c3f5314f3d3c407eede2ac09d0c177df3", "d98033ddec34e0f34b7ae25b6175d6a510593ce847a611b5425d0667bd9433f2", "HIGH", "Lower label between the fourth and fifth drawn units in the registered row.", "CLEAR_GAP", "HIGH", "The nearest diagonal non-writing contour remains separated from the terminal writing strokes by visible background."),
    "CG5A486DC157BB": ("1450,650,950,650", "1780,1000,360,125", "8eefb68d88e34d485c8d772487d7d9f9004c2097b40b86703cf7acf5f1fce1d1", "3165f837e5cd6a5973d280f2ab51c77eeb2b6f783f2a6e6d7df7d8b10df07161", "HIGH", "Lower label beside the fifth drawn unit in the registered row.", "CLEAR_GAP", "MEDIUM_HIGH", "The final writing form approaches a painted contour closely, but a thin continuous background gap remains visible."),
    "CG1BA8C54B160A": ("1900,300,700,700", "2160,555,300,125", "039d1561374574781ea8065cb6f2593007201be63816ce5e51b0bdb4539475b8", "0bfbca653a13fa69cc97ba5ee6e58fbdec3437fa4a5631b4dd64719aa0762ccb", "HIGH", "Upper label above the sixth drawn unit in the registered row.", "CLEAR_GAP", "MEDIUM", "A long terminal writing stroke descends toward the contour below but remains separated by a narrow visible gap."),
}


def main() -> None:
    with SELECTION.open(encoding="utf-8", newline="") as handle:
        selection = list(csv.DictReader(handle, delimiter="\t"))
    localizations, observations = [], []
    by_folio: dict[str, Counter[str]] = defaultdict(Counter)
    for row in selection:
        (context, target, context_hash, target_hash, loc_conf, loc_note,
         state, review_conf, review_note) = SEALED[row["target_id"]]
        canvas = row["canvas_id"]
        base = f"https://collections.library.yale.edu/iiif/2/{canvas}"
        localizations.append({
            **row, "full_image_sha256": FULL_HASH[canvas], "context_xywh": context,
            "target_xywh": target, "context_region_url": f"{base}/{context}/full/0/default.jpg",
            "target_region_url": f"{base}/{target}/full/0/default.jpg",
            "context_sha256": context_hash, "target_sha256": target_hash,
            "localizer_confidence": loc_conf, "localizer_note": loc_note,
            "localizer_judgment_excluded": "CONTACT_GAP_NOT_JUDGED",
        })
        observations.append({
            "target_id": row["target_id"], "provenance": "AI_DIRECT_VISUAL_OBSERVATION",
            "review_state": state, "review_confidence": review_conf,
            "review_note": review_note, "review_input": "RANDOMIZED_CONTEXT_AND_TARGET_CROPS_ONLY",
            "source_metadata_available_to_reviewer": "0",
        })
        by_folio[row["physical_folio"]][state] += 1

    loc_fields = list(localizations[0])
    obs_fields = list(observations[0])
    write_tsv(ROOT / "gdt002_contact_gap_localizations.tsv", localizations, loc_fields)
    write_tsv(ROOT / "gdt002_contact_gap_observations.tsv", observations, obs_fields)
    folio_counts = {
        folio: {state: counts[state] for state in ("CONTACT", "CLEAR_GAP", "UNCERTAIN")}
        for folio, counts in sorted(by_folio.items())
    }
    folio_pass = {
        folio: counts["CONTACT"] >= 1 and counts["CLEAR_GAP"] >= 2 and counts["UNCERTAIN"] == 0
        for folio, counts in folio_counts.items()
    }
    result = {
        "experiment": "GDT002_CONTACT_GAP_VISUAL_ACQUISITION",
        "status": "STOP_CAPACITY_GATE_FAILED_NO_FORMAL_COMPARISON",
        "provenance": "EXPLORATORY_AI_DIRECT_VISUAL_OBSERVATION",
        "counts_by_physical_folio": folio_counts,
        "capacity_gate_by_physical_folio": folio_pass,
        "capacity_gate_passed": all(folio_pass.values()),
        "decisive_failure": "f89 has zero CLEAR_GAP and one UNCERTAIN; preregistration required every folio to have >=1 CONTACT, >=2 CLEAR_GAP, and zero UNCERTAIN.",
        "access": {
            "official_images_opened_after_registration": True,
            "ocr_or_automated_vision_used": False,
            "source_aware_localizer_saw_transcription_and_formal_tables_after_registration": True,
            "formal_data_supplied_to_crop_reviewer": False,
            "formal_visual_join_or_role_solver_run": False,
            "f100_formal_payload_used_to_tune_visual_calls": False,
        },
        "inputs": {
            "GDT002_CONTACT_GAP_ACQUISITION_METHOD.md": sha(ROOT / "GDT002_CONTACT_GAP_ACQUISITION_METHOD.md"),
            "gdt002_contact_gap_selection.tsv": sha(SELECTION),
            "gdt002_contact_gap_selection_validation.json": sha(ROOT / "gdt002_contact_gap_selection_validation.json"),
            "build_gdt002_contact_gap_result.py": sha(Path(__file__)),
        },
        "outputs": {
            "gdt002_contact_gap_localizations.tsv": sha(ROOT / "gdt002_contact_gap_localizations.tsv"),
            "gdt002_contact_gap_observations.tsv": sha(ROOT / "gdt002_contact_gap_observations.tsv"),
        },
        "claim_ceiling": "The registered three-folio panel contains recorded visible CONTACT and CLEAR_GAP calls, but it fails the frozen per-folio capacity gate. No formal family association, semantic role, word, POS, sound, language, plaintext, meaning, or translation is tested or inferred.",
    }
    write_json(ROOT / "gdt002_contact_gap_result.json", result)


if __name__ == "__main__":
    main()
