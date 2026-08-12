#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import re
import urllib.request
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
METHOD = ROOT / "experiments/semantic_assumptions/LM001_HERBAL_LEAF_MARGIN_VISUAL_CAPACITY_METHOD.md"
ANN = ROOT / "experiments/semantic_assumptions/results/public_voynich_nu_page_annotations_v2.tsv"
ZL = ROOT / "transcription/voynich_zl3b_lines.tsv"
MANIFEST_URL = "https://collections.library.yale.edu/manifests/2002046"
OUT_TSV = ROOT / "experiments/semantic_assumptions/results/lm001_herbal_leaf_margin_visual_selection.tsv"
OUT_JSON = ROOT / "experiments/semantic_assumptions/results/lm001_herbal_leaf_margin_visual_selection.json"
OUT_MD = ROOT / "experiments/semantic_assumptions/results/lm001_herbal_leaf_margin_visual_selection_report.md"
MANIFEST_SHA256 = "317d58fd9ea90392a83d9858a91eada3d0b41416a3c835857dc0154bd123a309"


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def h(tag: str, page: str) -> str:
    return sha_bytes(f"{tag}|{page}".encode("ascii"))


def load_rows() -> list[dict[str, object]]:
    with ZL.open(encoding="utf-8", newline="") as f:
        zr = csv.DictReader(f, delimiter="\t")
        meta: dict[str, dict[str, str]] = {}
        for row in zr:
            meta.setdefault(row["page"], row)
    candidates: list[dict[str, object]] = []
    with ANN.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            page = row["page"]
            match = re.match(r"^f(\d+)", page.lower())
            if "SOURCE_HERBAL_PAGE" not in row["source_tags"] or page not in meta or not match:
                continue
            m = meta[page]
            candidates.append(
                {
                    "page": page,
                    "physical_folio": f"f{match.group(1)}",
                    "folio_number": int(match.group(1)),
                    "currier": m["language"],
                    "section": m["section"],
                    "hand": m["hand"],
                    "quire": row["quire"],
                    "page_selection_sha256": h("LM001_PAGE", page),
                }
            )
    one_per_folio: dict[str, dict[str, object]] = {}
    for row in candidates:
        folio = str(row["physical_folio"])
        if folio not in one_per_folio or str(row["page_selection_sha256"]) < str(one_per_folio[folio]["page_selection_sha256"]):
            one_per_folio[folio] = row
    selected: list[dict[str, object]] = []
    for currier in ("A", "B"):
        pool = sorted(
            (x for x in one_per_folio.values() if x["currier"] == currier),
            key=lambda x: (int(x["folio_number"]), str(x["page"])),
        )
        for i, row in enumerate(pool):
            row["folio_rank_quartile"] = min(4, 4 * i // len(pool) + 1)
        for quartile in range(1, 5):
            cell = [x for x in pool if x["folio_rank_quartile"] == quartile]
            chosen = sorted(cell, key=lambda x: str(x["page_selection_sha256"]))[:4]
            phase_order = sorted(chosen, key=lambda x: h("LM001_PHASE", str(x["page"])))
            for i, row in enumerate(phase_order):
                copy = dict(row)
                copy["phase"] = "CALIBRATION" if i < 2 else "HELD"
                copy["opaque_id"] = "LM" + h("LM001_OPAQUE", str(row["page"]))[:8].upper()
                selected.append(copy)
    return sorted(selected, key=lambda x: str(x["opaque_id"]))


def bind_canvases(rows: list[dict[str, object]]) -> None:
    request = urllib.request.Request(MANIFEST_URL, headers={"User-Agent": "VManus-LM001/1.0"})
    with urllib.request.urlopen(request, timeout=60) as response:
        raw = response.read()
    if sha_bytes(raw) != MANIFEST_SHA256:
        raise SystemExit("official manifest hash mismatch")
    manifest = json.loads(raw.decode("utf-8"))
    by_label: dict[str, list[dict[str, object]]] = {}
    for canvas in manifest["items"]:
        label = canvas["label"].get("none", [""])[0]
        by_label.setdefault(label, []).append(canvas)
    overrides = {"f90v1": "90v (part)", "f94v": "94v and 95r", "f95v2": "95v"}
    for row in rows:
        page = str(row["page"])
        label = overrides.get(page, re.sub(r"[123]$", "", page)[1:])
        hits = by_label.get(label, [])
        if len(hits) != 1:
            raise SystemExit(f"canvas label is not unique for {page}: {label!r}")
        canvas = hits[0]
        body = canvas["items"][0]["items"][0]["body"]
        row["canvas_id"] = canvas["id"].rsplit("/", 1)[-1]
        row["canvas_label"] = label
        row["image_width"] = int(body["width"])
        row["image_height"] = int(body["height"])
        row["review_image_url"] = body["service"][0]["@id"] + "/full/1600,/0/default.jpg"


def main() -> None:
    rows = load_rows()
    bind_canvases(rows)
    fields = [
        "opaque_id", "phase", "currier", "folio_rank_quartile", "page", "physical_folio",
        "folio_number", "section", "hand", "quire", "page_selection_sha256", "canvas_id",
        "canvas_label", "image_width", "image_height", "review_image_url",
    ]
    OUT_TSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_TSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, delimiter="\t", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    counts = Counter((str(x["currier"]), int(x["folio_rank_quartile"]), str(x["phase"])) for x in rows)
    result = {
        "experiment": "LM001_HERBAL_LEAF_MARGIN_VISUAL_SELECTION",
        "schema": "LM001_SELECTION_V1",
        "status": "FROZEN_BEFORE_SELECTED_IMAGE_INSPECTION",
        "decision": "AUTHORIZE_CALIBRATION_THEN_ONE_PASS_HELD_NATIVE_VISUAL_JUDGMENT",
        "counts": {
            "pages": len(rows),
            "physical_folios": len({x["physical_folio"] for x in rows}),
            "currier_A": sum(x["currier"] == "A" for x in rows),
            "currier_B": sum(x["currier"] == "B" for x in rows),
            "calibration": sum(x["phase"] == "CALIBRATION" for x in rows),
            "held": sum(x["phase"] == "HELD" for x in rows),
            "cell_counts": {f"{c}_Q{q}_{p}": counts[(c, q, p)] for c in ("A", "B") for q in range(1, 5) for p in ("CALIBRATION", "HELD")},
        },
        "gates": {
            "exact_32_pages": len(rows) == 32,
            "one_page_per_physical_folio": len({x["physical_folio"] for x in rows}) == 32,
            "balanced_currier": sum(x["currier"] == "A" for x in rows) == 16 and sum(x["currier"] == "B" for x in rows) == 16,
            "balanced_phase": sum(x["phase"] == "CALIBRATION" for x in rows) == 16 and sum(x["phase"] == "HELD" for x in rows) == 16,
            "each_cell_two_calibration_two_held": all(counts[(c, q, p)] == 2 for c in ("A", "B") for q in range(1, 5) for p in ("CALIBRATION", "HELD")),
            "selected_images_not_inspected_by_builder": True,
            "no_voynich_text_features_accessed": True,
        },
        "inputs": {
            str(METHOD.relative_to(ROOT)): sha_file(METHOD),
            str(ANN.relative_to(ROOT)): sha_file(ANN),
            str(ZL.relative_to(ROOT)): sha_file(ZL),
            "yale_manifest_2002046_sha256": MANIFEST_SHA256,
        },
        "panel_sha256": sha_file(OUT_TSV),
        "claim_ceiling": "This freezes a deterministic text-blind 32-page visual panel and rubric only. It establishes no leaf-margin association, plant identity, word, language, plaintext, meaning, or translation.",
    }
    OUT_JSON.write_text(json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "# LM001 herbal leaf-margin visual selection\n\n"
        "Status: **FROZEN_BEFORE_SELECTED_IMAGE_INSPECTION**.\n\n"
        "A deterministic metadata-only selector froze 32 whole herbal pages on 32 physical folios: "
        "16 Currier A, 16 Currier B, 16 calibration, and 16 held. Every Currier-by-folio-rank-"
        "quartile cell contains two calibration and two held pages. The official Yale manifest "
        f"is bound at `{MANIFEST_SHA256}`.\n\n"
        "No selected image was inspected by the builder and no Voynich text feature was accessed. "
        "The visual rubric and capacity gates are frozen in the method before calibration review.\n\n"
        "Claim ceiling: this is only a deterministic visual-selection freeze. It supplies no "
        "plant identity, leaf word, language, plaintext, meaning, or translation.\n",
        encoding="utf-8",
    )
    if not all(result["gates"].values()):
        raise SystemExit("selection gate failure")


if __name__ == "__main__":
    main()
