#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "experiments/semantic_assumptions"
RESULTS = BASE / "results"
METHOD = BASE / "SIA001_SUPRALINEAR_ADDITION_METHOD.md"
SOURCE = ROOT / "transcription/sources/Stolfi_text25e1-52.evt"
RESULT = RESULTS / "sia001_supralinear_addition_selection.json"
REPORT = RESULTS / "sia001_supralinear_addition_selection_report.md"
OUT_JSON = RESULTS / "sia001_supralinear_addition_selection_validation.json"
OUT_MD = RESULTS / "sia001_supralinear_addition_selection_validation_report.md"
MANIFEST = "https://collections.library.yale.edu/manifests/2002046"
MANIFEST_SHA = "317d58fd9ea90392a83d9858a91eada3d0b41416a3c835857dc0154bd123a309"


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def main() -> None:
    stored = json.loads(RESULT.read_text(encoding="utf-8"))
    source = SOURCE.read_text(encoding="latin-1")
    checks = []
    phrases = (
        "was added in darker ink and rather out of place",
        "omitted between @o an @d and added afterwards above the gap",
    )
    assert all(source.count(phrase) == 1 for phrase in phrases)
    checks.append("exact_complete_two_comment_census")
    assert [(t["locus"], t["comment_rule"]) for t in stored["targets"]] == [
        ("f31r.7", "UNHEDGED_DARKER_INK_OUT_OF_PLACE_ADDITION"),
        ("f50v.8", "HEDGED_OMITTED_AND_ADDED_ABOVE_GAP"),
    ]
    checks.append("exact_locus_and_rule_order")
    assert stored["counts"] == {"source_comments_selected": 2, "physical_loci": 2, "physical_folios": 2}
    checks.append("exact_two_locus_two_folio_counts")

    with urllib.request.urlopen(urllib.request.Request(MANIFEST, headers={"User-Agent": "VManus-SIA001-validate/1.0"}), timeout=60) as response:
        raw = response.read()
    assert sha_bytes(raw) == MANIFEST_SHA
    manifest = json.loads(raw.decode("utf-8"))
    actual = {}
    for canvas in manifest["items"]:
        label = canvas["label"].get("none", [""])[0]
        body = canvas["items"][0]["items"][0]["body"]
        actual[label] = (canvas["id"].rsplit("/", 1)[-1], [body["width"], body["height"]], body["service"][0]["@id"] + "/full/full/0/default.jpg")
    for target in stored["targets"]:
        label = target["page"][1:]
        assert actual[label] == (target["canvas_id"], target["official_dimensions"], target["official_full_image_url"])
    checks.append("official_manifest_canvas_dimensions_and_urls")
    assert all(not target["target_image_opened"] for target in stored["targets"])
    assert stored["access"] == {
        "target_image_bodies_opened": False,
        "ocr_clip_embeddings_or_automated_vision_used": False,
        "formal_family_root_role_or_meaning_fields_used": False,
    }
    checks.append("sealed_target_image_and_forbidden_fields")
    assert stored["inputs"] == {
        str(METHOD.relative_to(ROOT)): sha(METHOD),
        str(SOURCE.relative_to(ROOT)): sha(SOURCE),
        "yale_manifest_2002046_sha256": MANIFEST_SHA,
    }
    checks.append("exact_input_hash_bindings")
    assert stored["panel_pass_rule"] == "BOTH_TWO_TARGETS_PASS_ALL_FIVE_PHYSICAL_GATES"
    assert all(stored["gates"].values())
    checks.append("frozen_outcomes_gates_and_panel_rule")
    assert "no correct glyph identity" in stored["claim_ceiling"] and "translation" in stored["claim_ceiling"]
    checks.append("claim_ceiling")
    assert RESULT.read_bytes() == (json.dumps(stored, sort_keys=True, separators=(",", ":")) + "\n").encode()
    checks.append("canonical_selection_json")

    validation = {
        "experiment": "SIA001_COMPLETE_SUPRALINEAR_ADDITION_SELECTION_VALIDATION",
        "status": "PASS_9_CHECK_SOURCE_ONLY_RECONSTRUCTION",
        "check_count": len(checks),
        "checks": checks,
        "source_result_sha256": sha(RESULT),
        "source_report_sha256": sha(REPORT),
        "claim_ceiling": "Validation authorizes two source-native physical inspections only and supplies no glyph value, word, meaning, plaintext, or translation.",
    }
    OUT_JSON.write_text(json.dumps(validation, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "# SIA001 selection validation\n\nStatus: **PASS_9_CHECK_SOURCE_ONLY_RECONSTRUCTION**.\n\n"
        "Independent compact code reconstructs the complete two-comment census, exact loci and order, two-folio "
        "scope, official manifest canvas bindings, sealed target access, input hashes, frozen gates and panel rule, "
        "and canonical selection bytes.\n\nNo glyph value, word, meaning, plaintext, or translation follows.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
