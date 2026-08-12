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
METHOD = ROOT / "experiments/semantic_assumptions/LM001X_CURRIER_A_LEAF_MARGIN_EXTENSION_METHOD.md"
ANN = ROOT / "experiments/semantic_assumptions/results/public_voynich_nu_page_annotations_v2.tsv"
ZL = ROOT / "transcription/voynich_zl3b_lines.tsv"
OLD_PANEL = ROOT / "experiments/semantic_assumptions/results/lm001_herbal_leaf_margin_visual_selection.tsv"
OLD_HELD = ROOT / "experiments/semantic_assumptions/results/lm001_leaf_margin_visual_held.json"
OUT_TSV = ROOT / "experiments/semantic_assumptions/results/lm001x_currier_a_leaf_margin_extension_selection.tsv"
OUT_JSON = ROOT / "experiments/semantic_assumptions/results/lm001x_currier_a_leaf_margin_extension_selection.json"
OUT_MD = ROOT / "experiments/semantic_assumptions/results/lm001x_currier_a_leaf_margin_extension_selection_report.md"
MANIFEST_URL = "https://collections.library.yale.edu/manifests/2002046"
MANIFEST_SHA256 = "317d58fd9ea90392a83d9858a91eada3d0b41416a3c835857dc0154bd123a309"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_digest(path: Path) -> str:
    return digest(path.read_bytes())


def keyed(tag: str, page: str) -> str:
    return digest(f"{tag}|{page}".encode("ascii"))


def select() -> list[dict[str, object]]:
    metadata: dict[str, dict[str, str]] = {}
    with ZL.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            metadata.setdefault(row["page"], row)
    with OLD_PANEL.open(encoding="utf-8", newline="") as handle:
        excluded = {row["physical_folio"] for row in csv.DictReader(handle, delimiter="\t")}
    candidates: list[dict[str, object]] = []
    with ANN.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            page = row["page"]
            match = re.match(r"^f(\d+)", page.lower())
            if (
                "SOURCE_HERBAL_PAGE" not in row["source_tags"]
                or page not in metadata
                or metadata[page]["language"] != "A"
                or not match
            ):
                continue
            folio = f"f{match.group(1)}"
            if folio in excluded:
                continue
            candidates.append(
                {
                    "page": page,
                    "physical_folio": folio,
                    "folio_number": int(match.group(1)),
                    "currier": "A",
                    "section": metadata[page]["section"],
                    "hand": metadata[page]["hand"],
                    "quire": row["quire"] or metadata[page]["quire"],
                    "folio_rank_quartile": None,
                    "folio_page_sha256": keyed("LM001X_PAGE", page),
                    "selection_sha256": keyed("LM001X_SELECT", page),
                }
            )
    one_per_folio: dict[str, dict[str, object]] = {}
    for row in candidates:
        folio = str(row["physical_folio"])
        if folio not in one_per_folio or str(row["folio_page_sha256"]) < str(
            one_per_folio[folio]["folio_page_sha256"]
        ):
            one_per_folio[folio] = row

    full_pool = sorted(
        (row for row in one_per_folio.values()),
        key=lambda row: (int(row["folio_number"]), str(row["page"])),
    )
    # Quartiles inherit the original eligible Currier-A rank system. Rebuild it
    # from all Currier-A herbal folios, including those excluded above.
    all_a: dict[str, tuple[int, str]] = {}
    with ANN.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            page = row["page"]
            match = re.match(r"^f(\d+)", page.lower())
            if "SOURCE_HERBAL_PAGE" in row["source_tags"] and page in metadata and metadata[page]["language"] == "A" and match:
                folio = f"f{match.group(1)}"
                candidate = (int(match.group(1)), page)
                if folio not in all_a or keyed("LM001_PAGE", page) < keyed("LM001_PAGE", all_a[folio][1]):
                    all_a[folio] = candidate
    ranked = sorted(all_a.items(), key=lambda item: (item[1][0], item[1][1]))
    quartile = {folio: min(4, 4 * index // len(ranked) + 1) for index, (folio, _) in enumerate(ranked)}
    for row in full_pool:
        row["folio_rank_quartile"] = quartile[str(row["physical_folio"])]

    selected = []
    quires = sorted({str(row["quire"]) for row in full_pool if row["quire"] != "q05"})
    for quire in quires:
        cell = [row for row in full_pool if row["quire"] == quire]
        selected.extend(sorted(cell, key=lambda row: str(row["selection_sha256"]))[:3])
    for row in selected:
        row["opaque_id"] = "LX" + keyed("LM001X_OPAQUE", str(row["page"]))[:8].upper()
    return sorted(selected, key=lambda row: str(row["opaque_id"]))


def bind_canvases(rows: list[dict[str, object]]) -> None:
    request = urllib.request.Request(MANIFEST_URL, headers={"User-Agent": "VManus-LM001X/1.0"})
    with urllib.request.urlopen(request, timeout=60) as response:
        raw = response.read()
    if digest(raw) != MANIFEST_SHA256:
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
        row["review_image_url"] = body["service"][0]["@id"] + "/full/1600,/0/default.jpg"


def main() -> None:
    old = json.loads(OLD_HELD.read_text(encoding="utf-8"))
    assert old["counts"] == {"SMOOTH": 10, "TOOTHED": 5, "UNCERTAIN": 1, "pages": 16}
    rows = select()
    bind_canvases(rows)
    fields = [
        "opaque_id", "page", "physical_folio", "folio_number", "currier", "section", "hand",
        "quire", "folio_rank_quartile", "folio_page_sha256", "selection_sha256", "canvas_id",
        "canvas_label", "review_image_url",
    ]
    with OUT_TSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    quire_counts = Counter(str(row["quire"]) for row in rows)
    quartile_counts = Counter(str(row["folio_rank_quartile"]) for row in rows)
    gates = {
        "exact_19_pages": len(rows) == 19,
        "exact_19_new_physical_folios": len({row["physical_folio"] for row in rows}) == 19,
        "all_currier_A": all(row["currier"] == "A" for row in rows),
        "q05_excluded": all(row["quire"] != "q05" for row in rows),
        "quire_cap_three": max(quire_counts.values()) <= 3,
        "at_least_six_quires": len(quire_counts) >= 6,
        "selected_images_not_opened_by_builder": True,
        "no_voynich_text_features_accessed": True,
    }
    result = {
        "experiment": "LM001X_CURRIER_A_LEAF_MARGIN_EXTENSION_SELECTION",
        "schema": "LM001X_SELECTION_V1",
        "status": "FROZEN_BEFORE_EXTENSION_IMAGE_INSPECTION",
        "decision": "AUTHORIZE_ONE_PASS_EXTENSION_NATIVE_VISUAL_JUDGMENT",
        "counts": {
            "pages": len(rows),
            "physical_folios": len({row["physical_folio"] for row in rows}),
            "quire_counts": dict(sorted(quire_counts.items())),
            "quartile_counts": dict(sorted(quartile_counts.items())),
        },
        "gates": gates,
        "inputs": {
            str(METHOD.relative_to(ROOT)): file_digest(METHOD),
            str(ANN.relative_to(ROOT)): file_digest(ANN),
            str(ZL.relative_to(ROOT)): file_digest(ZL),
            str(OLD_PANEL.relative_to(ROOT)): file_digest(OLD_PANEL),
            str(OLD_HELD.relative_to(ROOT)): file_digest(OLD_HELD),
            "yale_manifest_2002046_sha256": MANIFEST_SHA256,
        },
        "panel_sha256": file_digest(OUT_TSV),
        "claim_ceiling": "This freezes 19 new Currier-A herbal folios for one source-only leaf-margin capacity extension. It supplies no text association, plant identity, word, language, plaintext, meaning, or translation.",
    }
    if not all(gates.values()):
        raise SystemExit("selection gate failure")
    OUT_JSON.write_text(json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "# LM001X Currier-A leaf-margin extension selection\n\n"
        "Status: **FROZEN_BEFORE_EXTENSION_IMAGE_INSPECTION**.\n\n"
        "A deterministic metadata-only selector froze 19 previously unused Currier-A herbal folios "
        "across eight quires. q05 is excluded and every included quire contributes at most three pages. "
        "Official Yale canvases are bound without opening image bodies.\n\n"
        "The unchanged LM001 rubric will be applied once in opaque-ID order. Only a combined old-plus-new "
        "pass of every original LM001 gate could license a separate text design. No Voynich text feature "
        "was accessed, and no plant identity, word, plaintext, meaning, or translation follows.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
