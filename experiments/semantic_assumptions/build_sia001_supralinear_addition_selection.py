#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "experiments/semantic_assumptions"
RESULTS = BASE / "results"
METHOD = BASE / "SIA001_SUPRALINEAR_ADDITION_METHOD.md"
SOURCE = ROOT / "transcription/sources/Stolfi_text25e1-52.evt"
OUT_JSON = RESULTS / "sia001_supralinear_addition_selection.json"
OUT_MD = RESULTS / "sia001_supralinear_addition_selection_report.md"
MANIFEST_URL = "https://collections.library.yale.edu/manifests/2002046"
MANIFEST_SHA256 = "317d58fd9ea90392a83d9858a91eada3d0b41416a3c835857dc0154bd123a309"
EXPECTED = {
    "f31r.7": {
        "page": "f31r",
        "canvas_id": "1006134",
        "canvas_label": "31r",
        "comment_rule": "UNHEDGED_DARKER_INK_OUT_OF_PLACE_ADDITION",
    },
    "f50v.8": {
        "page": "f50v",
        "canvas_id": "1006173",
        "canvas_label": "50v",
        "comment_rule": "HEDGED_OMITTED_AND_ADDED_ABOVE_GAP",
    },
}


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def select_comments(raw: str) -> list[dict[str, str]]:
    lines = raw.splitlines()
    hits: list[dict[str, str]] = []
    for i, line in enumerate(lines):
        rule = None
        if line.startswith("# ") and "was added in darker ink and rather out of place" in line:
            rule = "UNHEDGED_DARKER_INK_OUT_OF_PLACE_ADDITION"
        elif line.startswith("# ") and "omitted between" in line and "added afterwards above the gap" in line:
            rule = "HEDGED_OMITTED_AND_ADDED_ABOVE_GAP"
        if rule is None:
            continue
        target = next((candidate for candidate in lines[i + 1 :] if candidate.startswith("<f")), None)
        assert target is not None
        match = re.match(r"<([^;>]+);U>", target)
        assert match
        hits.append({"locus": match.group(1), "comment_rule": rule, "comment": line[2:]})
    return hits


def main() -> None:
    hits = select_comments(SOURCE.read_text(encoding="latin-1"))
    assert [(h["locus"], h["comment_rule"]) for h in hits] == [
        ("f31r.7", "UNHEDGED_DARKER_INK_OUT_OF_PLACE_ADDITION"),
        ("f50v.8", "HEDGED_OMITTED_AND_ADDED_ABOVE_GAP"),
    ]

    request = urllib.request.Request(MANIFEST_URL, headers={"User-Agent": "VManus-SIA001/1.0"})
    with urllib.request.urlopen(request, timeout=60) as response:
        manifest_raw = response.read()
    assert sha_bytes(manifest_raw) == MANIFEST_SHA256
    manifest = json.loads(manifest_raw.decode("utf-8"))
    canvases = {}
    for canvas in manifest["items"]:
        label = canvas["label"].get("none", [""])[0]
        body = canvas["items"][0]["items"][0]["body"]
        canvases[label] = {
            "canvas_id": canvas["id"].rsplit("/", 1)[-1],
            "width": body["width"],
            "height": body["height"],
            "service": body["service"][0]["@id"],
        }

    targets = []
    for hit in hits:
        expected = EXPECTED[hit["locus"]]
        canvas = canvases[expected["canvas_label"]]
        assert canvas["canvas_id"] == expected["canvas_id"]
        targets.append(
            {
                **hit,
                "page": expected["page"],
                "canvas_id": canvas["canvas_id"],
                "official_dimensions": [canvas["width"], canvas["height"]],
                "official_full_image_url": canvas["service"] + "/full/full/0/default.jpg",
                "target_image_opened": False,
            }
        )

    result = {
        "experiment": "SIA001_COMPLETE_SUPRALINEAR_ADDITION_SELECTION",
        "schema": "SIA001_SELECTION_V1",
        "status": "FROZEN_COMPLETE_TWO_LOCUS_PANEL_BEFORE_TARGET_IMAGE_ACCESS",
        "decision": "AUTHORIZE_ONE_SOURCE_NATIVE_INSPECTION_PER_TARGET",
        "counts": {"source_comments_selected": 2, "physical_loci": 2, "physical_folios": 2},
        "targets": targets,
        "gates": {
            "exact_complete_literal_comment_rules": len(targets) == 2,
            "exact_expected_loci": [t["locus"] for t in targets] == ["f31r.7", "f50v.8"],
            "exact_two_physical_folios": len({t["page"] for t in targets}) == 2,
            "official_manifest_canvas_bindings": True,
            "target_image_regions_unopened": all(not t["target_image_opened"] for t in targets),
            "outcomes_and_five_physical_gates_frozen": True,
        },
        "panel_pass_rule": "BOTH_TWO_TARGETS_PASS_ALL_FIVE_PHYSICAL_GATES",
        "inputs": {
            str(METHOD.relative_to(ROOT)): sha(METHOD),
            str(SOURCE.relative_to(ROOT)): sha(SOURCE),
            "yale_manifest_2002046_sha256": MANIFEST_SHA256,
        },
        "access": {
            "target_image_bodies_opened": False,
            "ocr_clip_embeddings_or_automated_vision_used": False,
            "formal_family_root_role_or_meaning_fields_used": False,
        },
        "claim_ceiling": (
            "A pass can establish only recurrent visible supralinear insertion practice at two physical loci. "
            "It establishes no correct glyph identity, correction intent, sound, word, language, cipher, "
            "plaintext, meaning, or translation."
        ),
    }
    assert all(result["gates"].values())
    OUT_JSON.write_text(json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "# SIA001 supralinear-addition selection\n\n"
        "Status: **FROZEN_COMPLETE_TWO_LOCUS_PANEL_BEFORE_TARGET_IMAGE_ACCESS**.\n\n"
        "A complete literal scan of the human-authored source selects exactly two explicit above-baseline "
        "addition claims: f31r.7 and f50v.8, on two physical folios. The official Yale manifest fixes canvases "
        "1006134 and 1006173 without opening either target image body. Outcomes, five per-target physical gates, "
        "and the two-of-two recurrent-practice threshold are frozen.\n\n"
        "This authorizes one source-native inspection per target and supplies no glyph value, word, meaning, "
        "plaintext, or translation.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
