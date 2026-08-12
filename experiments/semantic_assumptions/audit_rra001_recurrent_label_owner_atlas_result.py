#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "experiments/semantic_assumptions"
RES = BASE / "results"
METHOD = BASE / "RRA001_RECURRENT_LABEL_OWNER_ATLAS_METHOD.md"
SELECTION = RES / "rra001_recurrent_label_owner_atlas_selection.json"
SELECTION_VALIDATION = RES / "rra001_recurrent_label_owner_atlas_selection_validation.json"
OUT = RES / "rra001_recurrent_label_owner_atlas_result.json"
REPORT = RES / "rra001_recurrent_label_owner_atlas_result_report.md"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


FULL_IMAGE_SHA = {
    "1006200": "062ff6a9f14d0c16eb12dc8f6dc480771b7c19746ebdb20302b998e66181ccea",
    "1006201": "c8f24b6be5451aba49eb793784c43cb7fc8341dca8a58ff43fc1eebf4877b60c",
    "1006203": "45f7caf4b58744fdcd4928887661b56a135538a5a40a24fea6ca6c5239898269",
    "1006204": "2552b2eafb7948d182e52ec49e96a5d92a774917924aea594fb1ac3af3bfcdc5",
    "1006205": "c0ac0dbc3e4b4a6eb2b8edf26dc762a7f9bf26ac9c385fa6bdc770725622b1e7",
    "1006209": "654edf15a65d1a2bb0d7bb4995f8f6fba1625d5eed847c9b6969d1c44e385a23",
    "1006218": "81223a0b0aa0a24fe821cf62a9bdf4ac504f222ab3cfcb89fcedd7946bceada0",
    "1006222": "269cb42307824ab82764f80009429e58d98c649371d8efe10d2a1f54132a21ef",
    "1006226": "7e8fa7c29b6c6ab462ad5359bdabfcd60505622700f6e5cb18478d20cbd79fbe",
    "1006233": "3b553c70d0c068cb39a276d391127165c5d9d868ec08e7f5eb2e73b32bb95d1e",
    "1006247": "111f6dfc34b8ecb9230cb5a0d144afef4cbd788048ddda2f440108941c91d5e5",
    "1037112": "a1d21ccad0df430b47f3b3df2829bbefb8c4d1644cb70310e6d1de4b01c20013",
}

PAGE_REGION = {
    "f70v2": ("full", FULL_IMAGE_SHA["1006200"]),
    "f70v1": ("full", FULL_IMAGE_SHA["1006201"]),
    "f72r2": ("full", FULL_IMAGE_SHA["1006203"]),
    "f72r3": ("full", FULL_IMAGE_SHA["1006203"]),
    "f72v3": ("full", FULL_IMAGE_SHA["1006204"]),
    "f72v1": ("full", FULL_IMAGE_SHA["1006205"]),
    "f75v": ("250,950,2400,1100", "2dfe807e3e4b4989c19e6682bf6ffbdeaf7154ef1a94e950a0a156dfc176c9d9"),
    "f80r": ("100,0,2550,650", "c4e1085d47289c800b34cef060dd77774191d568992ba7795f3cc92dba3ae0c5"),
    "f84r": ("50,100,2550,750", "c707ea7451140d191bdc83e3bb517a8c369af40e067046b626993949f336dbf4"),
    "f88r": ("250,50,2300,700", "1e1a166f93c3a3f9e67e45a21a13f096f8a27fe6d7cc5f17878fbea7408d8bbc"),
    "f89r1": ("0,0,4600,1000", "043d888a126be828dfd1b87f09138a9dd2c5abfb3b04d2f6e73c5f357d17af64"),
    "f99v": ("200,0,2400,750", "de99557edd8df3e06684cdc9fdf6063a352998ed30b8e5a4f9858781181d5194"),
}

# These are the sixteen judgments that remained sealed by the selection.
NEW = {
    "f72r2.10": ("OTHER_CLASS_OR_SLOT_ASSOCIATED", "The label is localized at its frozen angular position in an open zodiac annulus. The sector contains figure/star material, but no leader, divider, enclosure, or unique one-figure column assigns the inscription to one figure."),
    "f72r2.18": ("OTHER_CLASS_OR_SLOT_ASSOCIATED", "The label is localized at its frozen angular position in the same open zodiac annulus. Neighboring figure/star positions share the ring and no singular ownership device is visible."),
    "f72v3.17": ("OTHER_CLASS_OR_SLOT_ASSOCIATED", "The inscription occupies a frozen annular slot among repeated figure/star positions. The ring supplies a cyclic slot, not a unique assignment to one figure."),
    "f80r.3": ("SINGULAR_COMMON_CLASS_OWNED", "The inscription is centered above the third figure in a repeated top-margin sequence. Adjacent figures have separate horizontally spaced inscriptions, leaving one unambiguous local figure slot and no equal competitor."),
    "f72v1.28": ("OTHER_CLASS_OR_SLOT_ASSOCIATED", "The inscription is localized in an inner zodiac label band. The open annulus and repeated neighboring figures/stars provide no singular assignment device."),
    "f84r.4": ("PROXIMITY_OR_GROUP_ONLY", "The visible inscription area lies above two adjacent figures without a separating owner boundary. The source-visible layout permits the documented one-label-versus-two-label ambiguity and therefore has an equal competitor."),
    "f70v1.9": ("OTHER_CLASS_OR_SLOT_ASSOCIATED", "The label is localized in an open outer figure/star annulus. It occupies a cyclic slot but lacks a leader, cell, divider, or unique one-figure column."),
    "f84r.10": ("SINGULAR_COMMON_CLASS_OWNED", "The short inscription stack above figure 10 is horizontally separated from neighboring stacks under repeated canopy divisions. One figure occupies the local slot and no equal competitor shares it."),
    "f72r3.18": ("OTHER_CLASS_OR_SLOT_ASSOCIATED", "The label is localized in a middle zodiac annulus at its frozen angular position. The open band assigns a slot only; it does not visibly assign the label to one human figure."),
    "f75v.27": ("SINGULAR_COMMON_CLASS_OWNED", "The target is line two of the fifth repeated two-line inscription column. The hanging apparatus boundaries and horizontal spacing reserve that column above one figure with no competing figure."),
    "f88r.5": ("PROXIMITY_OR_GROUP_ONLY", "The label lies east of a plant in a continuous top row, outside the plant drawing and without a leader, enclosure, or exclusive plant cell. Its placement establishes proximity only."),
    "f99v.9": ("PROXIMITY_OR_GROUP_ONLY", "The inscription lies visibly between the seventh and eighth plant drawings. Both are equal competitors and no author-visible device assigns it exclusively to either plant."),
    "f89r1.4": ("PROXIMITY_OR_GROUP_ONLY", "The inscription lies east of one plant within a continuous row but outside its drawing and without a leader or bounded owner cell. Only proximity is visible."),
    "f99v.2": ("PROXIMITY_OR_GROUP_ONLY", "The inscription lies between a container and the first plant, and drawing intrusion breaks the local writing. The visible layout does not assign the whole inscription exclusively to one plant."),
    "f70v2.5": ("OTHER_CLASS_OR_SLOT_ASSOCIATED", "The label is localized in an open outer star/figure annulus. It occupies one angular slot but has no unique connector, divider, enclosure, or one-figure column."),
    "f75v.28": ("SINGULAR_COMMON_CLASS_OWNED", "The target is line one of the sixth repeated two-line inscription column. Apparatus geometry and horizontal separation reserve the column above one figure with no equal competitor."),
}

FIXED_REGION = {
    "f72v3.10": ("2450,1150,1300,1300", "d8b3d64dd9c536c343f8300670f288f1fa1525b20eafd42b89a6b5a0acc352bc"),
    "f75v.37": ("1950,1050,800,1050", "8f792f757ff5ef770befdffe13352e4f3b9bb8215b4464c5974cfa66bc8722ca"),
    "f84r.11": ("1750,250,800,750", "c56ee27c7353bf65a0126dd4f500a7a9f10688c7fccb815efd9b9a69a3bb2058"),
}

FIXED_BASIS = {
    "f75v.21": "Published prior inspection classifies this occurrence as an unattached group/proximity label for the common water-or-apparatus context.",
    "f82r.35": "Published prior inspection classifies this occurrence as an unattached group/proximity label for the common water-or-apparatus context.",
    "f72v3.10": "Published RFO001 inspection localizes the label in an open figure/star annulus without a unique assignment device.",
    "f75v.37": "Published RFO001 inspection finds a reserved two-line column above one figure.",
    "f84r.11": "Published RFO001 inspection finds a distinct stack above figure 11, separate from the stack above figure 12.",
}


def gates(outcome: str) -> dict[str, bool]:
    positive = outcome == "SINGULAR_COMMON_CLASS_OWNED"
    return {
        "target_inscription_securely_localized": True,
        "exactly_one_common_class_object_in_local_slot": positive,
        "author_visible_singular_assignment_device": positive,
        "no_equal_competing_common_class_object": positive,
        "assignment_independent_of_editorial_wording_or_transcription_order": True,
    }


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    selection = json.loads(SELECTION.read_text())
    observations = []
    for row in selection["rows"]:
        locus = row["locus"]
        canvas = row["canvas_id"]
        if row["exposure"] == "FIXED_PRIOR":
            outcome = row["fixed_outcome"]
            basis = FIXED_BASIS[locus]
            if locus in FIXED_REGION:
                region, region_sha = FIXED_REGION[locus]
            else:
                region, region_sha = "fixed-prior-full-canvas", FULL_IMAGE_SHA[canvas]
        else:
            outcome, basis = NEW[locus]
            region, region_sha = PAGE_REGION[row["page"]]
        observations.append({
            "surface": row["surface"],
            "locus": locus,
            "page": row["page"],
            "physical_folio": row["physical_folio"],
            "shared_classes": row["shared_classes"],
            "exposure": row["exposure"],
            "outcome": outcome,
            "gates": gates(outcome),
            "canvas_id": canvas,
            "official_full_image_sha256": FULL_IMAGE_SHA[canvas],
            "review_region": region,
            "review_region_sha256": region_sha,
            "visible_basis": basis,
        })

    by_type: dict[str, list[dict]] = defaultdict(list)
    for observation in observations:
        by_type[observation["surface"]].append(observation)
    type_results = []
    for surface in sorted(by_type):
        rows = by_type[surface]
        passed = all(row["outcome"] == "SINGULAR_COMMON_CLASS_OWNED" for row in rows)
        type_results.append({
            "surface": surface,
            "loci": [row["locus"] for row in rows],
            "singular_owned_count": sum(row["outcome"] == "SINGULAR_COMMON_CLASS_OWNED" for row in rows),
            "occurrence_count": len(rows),
            "passes_all_occurrences": passed,
        })

    outcome_counts = Counter(row["outcome"] for row in observations)
    passing = [row["surface"] for row in type_results if row["passes_all_occurrences"]]
    result = {
        "experiment": "RRA001_RECURRENT_LABEL_OWNER_ATLAS",
        "schema": "RRA001_RESULT_V1",
        "status": "STOP_ZERO_OF_NINE_TYPES_RETAIN_SINGULAR_COMMON_CLASS_OWNERSHIP",
        "decision": "CLOSE_EXACT_RECURRENT_SINGULAR_OBJECT_NAME_BRIDGE_AT_CURRENT_ANNOTATION_COVERAGE",
        "observations": observations,
        "type_results": type_results,
        "counts": {
            "types": len(type_results),
            "loci": len(observations),
            "physical_folios": len({row["physical_folio"] for row in observations}),
            "fixed_prior_outcomes": sum(row["exposure"] == "FIXED_PRIOR" for row in observations),
            "new_target_judgments": sum(row["exposure"] == "SEALED_TARGET_JUDGMENT" for row in observations),
            "singular_common_class_owned": outcome_counts["SINGULAR_COMMON_CLASS_OWNED"],
            "other_class_or_slot_associated": outcome_counts["OTHER_CLASS_OR_SLOT_ASSOCIATED"],
            "proximity_or_group_only": outcome_counts["PROXIMITY_OR_GROUP_ONLY"],
            "localization_unresolved": outcome_counts["LOCALIZATION_UNRESOLVED"],
            "passing_types": len(passing),
        },
        "panel_gate": {"every_occurrence_singular_owned_by_type": passing},
        "inputs": {str(path.relative_to(ROOT)): sha256(path) for path in (METHOD, SELECTION, SELECTION_VALIDATION)},
        "access": {
            "sixteen_target_specific_ownership_judgments_opened_after_selection_publication": True,
            "official_source_native_pixels_used": True,
            "ocr_clip_embedding_or_automated_vision_used": False,
            "parser_roots_or_roles_used": False,
            "structural_tags_kept_distinct_from_translation": True,
        },
        "claim_ceiling": "None of the nine complete exact recurrent label types is singularly owned by its shared human-annotated coarse class at every occurrence. This closes only the exact whole-surface recurrent singular-object-name bridge at current annotation coverage. It does not show that labels are meaningless or never names, and it establishes no class word POS sound language cipher plaintext meaning or translation.",
    }
    OUT.write_text(json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n")
    REPORT.write_text(
        "# RRA001 recurrent-label owner atlas result\n\n"
        "Status: **STOP_ZERO_OF_NINE_TYPES_RETAIN_SINGULAR_COMMON_CLASS_OWNERSHIP**.\n\n"
        "The complete frozen atlas contains nine exact recurrent label surfaces at 21 loci on nine physical folios. "
        "Six occurrences have singular visible ownership, eight occupy a formal slot without singular ownership by the shared class, and seven show proximity or group association only. "
        "Crucially, every one of the nine surface types has at least one nonsingular occurrence. The frozen all-occurrences rule therefore yields **0/9 passing types**.\n\n"
        "This is a focused negative result, not a claim that Voynich labels are meaningless. Some biological labels do occupy clear one-to-one figure columns. "
        "What fails is stability: the same exact strings recur elsewhere in open zodiac annuli, between plants, or in group/proximity positions. "
        "Close the exact whole-surface recurrent singular-object-name bridge at current human-annotation coverage. "
        "No class name, word, POS, sound, language, cipher, plaintext, meaning, or translation follows.\n"
    )


if __name__ == "__main__":
    main()
