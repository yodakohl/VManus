#!/usr/bin/env python3
"""Record the source-bound f102r1 row3/item1 label-ownership observation."""

from __future__ import annotations

import ast
import csv
import hashlib
import json
import re
from pathlib import Path


BASE = Path(__file__).resolve().parent
ROOT = BASE.parent.parent
PAIR_SOURCE = BASE / "cache/existing_human_annotations/stolfi_2025_internal_plant_pairs.tsv"
PAGES = BASE / "results/existing_human_page_annotations.tsv"
Q19 = BASE / "cache/public_voynich_nu_catalogue/q19.html"
LINES = ROOT / "transcription/voynich_stolfi25e1_lines.tsv"
PRIOR = BASE / "results/public_repeated_plant_source_native_capacity.json"
METHOD = BASE / "F102R1_FIFTH_REPEATED_PLANT_LABEL_NATIVE_VISUAL_OWNERSHIP_METHOD.md"
PRODUCER = Path(__file__).resolve()
OUT = BASE / "results/f102r1_fifth_repeated_plant_label_native_visual_ownership.json"
REPORT = BASE / "results/f102r1_fifth_repeated_plant_label_native_visual_ownership_report.md"

FROZEN = {
    PAIR_SOURCE: "53248c1ab2a50ec43a56ecee0bb22478a890a00f38671c75882620d8c5d28230",
    PAGES: "b358f244cbe853448dd5c32dbc04004cb8ce63d9a8c5ed5afe2a679a115d87fa",
    Q19: "119fe32a005723833ec07a313fd87e1cd044a1f685ddd4fdd199e573c1dff1fb",
    LINES: "b4c83c18f8f814e547ab4a849dab8cf24188680fc512d9497885bdaa0d944988",
    PRIOR: "a16700eafc88653c3b95f8fcd840a4c86a185ca240a0e19123e880a46373cb2e",
}
IMAGE_URL = "https://collections.library.yale.edu/iiif/2/1006251/full/full/0/default.jpg"
IMAGE_SHA256 = "30fd529fc6bf8999d5be48024ee6a1676af55e8d66dc0a4f77993fe2565e9d94"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=False) + "\n").encode()


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing to overwrite f102r1 ownership artifacts")
    for path, expected in FROZEN.items():
        if sha(path) != expected:
            raise SystemExit(f"frozen input mismatch: {path.name}")

    with PAIR_SOURCE.open(encoding="utf-8", newline="") as handle:
        pairs = {row["relation_id"]: row for row in csv.DictReader(handle, delimiter="\t")}
    relation = pairs["JSP2025_05"]
    expected_relation = {
        "first_page": "f37v", "second_page_current": "f102r1", "second_row": "3",
        "second_item": "1", "match_kind": "GOOD_HERBAL_PHARMA",
        "root_copied": "1", "leaves_copied": "1", "flower_copied": "0",
        "component_note": "pharma omits flower",
    }
    if any(relation[key] != value for key, value in expected_relation.items()):
        raise ValueError("JSP2025_05 relation drift")

    with PAGES.open(encoding="utf-8", newline="") as handle:
        page = next(row for row in csv.DictReader(handle, delimiter="\t")
                    if row["page"] == "f102r1")
    if "1 label of a plant fragment" not in page["text_description"]:
        raise ValueError("f102r1 plant-label count drift")
    if "There are 4 labels in total" not in page["text_description"]:
        raise ValueError("f102r1 total-label count drift")

    current = None
    for line in Q19.read_text(encoding="utf-8", errors="replace").splitlines():
        match = re.search(r'<TH CLASS="Ph" ID="([^"]+)">', line, re.I)
        if match:
            current = match.group(1)
        match = re.search(r"child_oid=([0-9]+)", line)
        if current == "f102r1" and match:
            if match.group(1) != "1006251":
                raise ValueError("f102r1 canvas drift")
            break
    else:
        raise ValueError("f102r1 canvas not found")

    with LINES.open(encoding="utf-8", newline="") as handle:
        metadata = [{key: row[key] for key in ("page", "locus", "old_locus", "code")}
                    for row in csv.DictReader(handle, delimiter="\t") if row["page"] == "f102r1"]
    plant_labels = [row for row in metadata if row["code"] == "@Lf"]
    if plant_labels != [{"page": "f102r1", "locus": "f102r1.2",
                         "old_locus": "f102r1.L1.1", "code": "@Lf"}]:
        raise ValueError("unique f102r1 plant-label locus drift")
    prior = json.loads(PRIOR.read_text(encoding="utf-8"))
    if prior["capacity"]["relations"] != 4:
        raise ValueError("prior relation count drift")

    result = {
        "experiment": "F102R1_FIFTH_REPEATED_PLANT_LABEL_NATIVE_VISUAL_OWNERSHIP",
        "status": "PASS_PROVISIONAL_NATIVE_VISUAL_SINGULAR_DIRECT_INTERIOR_OWNERSHIP",
        "decision": "REOPEN_FIVE_PAIR_SCORE_BLIND_CAPACITY_AND_DESIGN_ONLY",
        "human_relation": {
            "relation_id": "JSP2025_05", "herbal_page": "f37v",
            "pharmaceutical_page": "f102r1", "row": 3, "item": 1,
            "match_kind": "GOOD_HERBAL_PHARMA", "root_copied": True,
            "leaves_copied": True, "flower_copied": False,
        },
        "label_binding": {
            "current_locus": "f102r1.2", "old_locus": "f102r1.L1.1",
            "metadata_role": "@Lf", "page_plant_fragment_labels": 1,
            "page_total_labels": 4, "label_surface_accessed": False,
        },
        "official_image": {
            "manifest": "https://collections.library.yale.edu/manifests/2002046",
            "canvas_id": "1006251", "image_url": IMAGE_URL,
            "sha256": IMAGE_SHA256, "width": 8176, "height": 3864,
            "review_rectangle": {"x": 2600, "y": 1900, "width": 3000, "height": 1900},
        },
        "native_visual_observation": {
            "ownership_grade": "SINGULAR_DIRECT_INTERIOR",
            "description": (
                "The sole plant-fragment inscription on f102r1 is drawn inside the pale neck "
                "at the top of the bottom-left red-rooted plant. The writing overlaps that "
                "plant body and no competing fragment occupies the local writing region."
            ),
            "machine_authored_source_bound_observation": True,
            "ocr_or_transcription_used": False,
            "automated_vision_embedding_or_similarity_used": False,
        },
        "capacity_change": {"previous_strongly_owned_relations": 4,
                            "new_relations_added": 1,
                            "current_strongly_owned_relations": 5},
        "gates": {
            "human_good_drawing_relation_exact": True,
            "official_canvas_exact": True,
            "unique_page_plant_label": True,
            "unique_current_Lf_locus": True,
            "writing_inside_target_fragment_body": True,
            "no_competing_fragment_in_local_writing_region": True,
            "label_surface_remained_sealed": True,
        },
        "inputs": {str(path.relative_to(ROOT)): sha(path) for path in FROZEN} | {
            METHOD.name: sha(METHOD), PRODUCER.name: sha(PRODUCER),
            "yale_iiif_full_image_sha256": IMAGE_SHA256,
        },
        "claim_ceiling": (
            "The image supports provisional singular ownership for a fifth human repeated-plant "
            "relation and authorizes only a new score-blind capacity/design audit. It supplies "
            "no plant name, component name, word, sound, language, cipher, plaintext, meaning, "
            "or translation."
        ),
    }
    OUT.write_bytes(canonical(result))
    REPORT.write_text(
        "# f102r1 fifth repeated-plant label ownership\n\n"
        f"Status: **{result['status']}**\n\n"
        "The cached human relation `JSP2025_05` identifies f102r1 row 3/item 1 as "
        "the root-and-leaf copy of f37v. On the exact official Yale canvas, the page's "
        "sole plant-fragment inscription is written inside the pale neck at the top of "
        "that bottom-left red-rooted plant, with no competing fragment in the local "
        "writing region. Current metadata maps the unique `@Lf` record to `f102r1.2`.\n\n"
        "This is a source-bound machine-authored visual observation, not OCR or inherited "
        "human ownership annotation. The label characters remain sealed. It raises the "
        "strongly owned repeated-plant panel from four to five relations and reopens only "
        "a new score-blind capacity/design audit.\n\n"
        f"Claim ceiling: {result['claim_ceiling']}\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
