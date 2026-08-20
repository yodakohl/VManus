#!/usr/bin/env python3
"""Prepare the frozen GDT391 page allow-list for direct visual review.

This reuses the already published, f84-free GDT389 official-canvas mapping and
cached image hashes.  Tiling is mechanical; no visual judgment is automated.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import tempfile
import urllib.request
from collections import defaultdict
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("repository root not found")


ROOT = root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt391_local_object_relation_normalization"
ART = BASE / "artifacts"
FREEZE = ART / "gdt391_pre_normalization_freeze.json"
SOURCE_MAPPING = ROOT / "experiments/yolo/gdt389_connector_edge_census/artifacts/gdt389_image_manifest.tsv"
SOURCE_HASHES = ROOT / "experiments/yolo/gdt389_connector_edge_census/artifacts/gdt389_review_image_hashes.tsv"
OUT_MAPPING = ART / "gdt391_image_manifest.tsv"
OUT_HASHES = ART / "gdt391_review_image_hashes.tsv"
TEMP_ROOT = Path(tempfile.gettempdir()) / "gdt391_review_v1"
IMAGES = TEMP_ROOT / "images"
SHEETS = TEMP_ROOT / "contact_sheets"


def tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    pages = freeze["frame"]["pages_allowlist"]
    mapping_rows = tsv(SOURCE_MAPPING)
    hash_rows = tsv(SOURCE_HASHES)
    assert all(not page.lower().startswith("f84") for page in pages)
    selected = [row for row in mapping_rows if row["page"] in pages]
    assert {row["page"] for row in selected} == set(pages)
    assert all(not row["page"].lower().startswith("f84") and "84r" not in row["canvas_label"].lower() and "84v" not in row["canvas_label"].lower() for row in selected)
    write(OUT_MAPPING, selected)

    canvas_to_pages: dict[str, list[str]] = defaultdict(list)
    canvas_to_mapping: dict[str, dict[str, str]] = {}
    for row in selected:
        canvas_to_pages[row["canvas_id"]].append(row["page"])
        canvas_to_mapping[row["canvas_id"]] = row
    expected_hashes = {row["canvas_id"]: row for row in hash_rows}
    assert set(canvas_to_pages) <= set(expected_hashes)

    IMAGES.mkdir(parents=True, exist_ok=True)
    SHEETS.mkdir(parents=True, exist_ok=True)
    reviewed: list[dict[str, object]] = []
    for canvas_id in sorted(canvas_to_pages):
        mapping = canvas_to_mapping[canvas_id]
        path = IMAGES / f"{canvas_id}.jpg"
        old_path = Path(tempfile.gettempdir()) / "gdt389_review_v1" / "images" / f"{canvas_id}.jpg"
        if old_path.is_file():
            data = old_path.read_bytes()
        else:
            request = urllib.request.Request(mapping["review_image_url"], headers={"User-Agent": "VManus-GDT391/1.0"})
            with urllib.request.urlopen(request, timeout=90) as response:
                data = response.read()
        assert hashlib.sha256(data).hexdigest() == expected_hashes[canvas_id]["sha256"]
        if not path.is_file() or path.read_bytes() != data:
            path.write_bytes(data)
        with Image.open(io.BytesIO(data)) as image:
            width, height = image.size
        reviewed.append(
            {
                "canvas_id": canvas_id,
                "canvas_label": mapping["canvas_label"],
                "pages": ",".join(sorted(canvas_to_pages[canvas_id])),
                "review_image_url": mapping["review_image_url"],
                "pixel_width": width,
                "pixel_height": height,
                "sha256": hashlib.sha256(data).hexdigest(),
            }
        )
    write(OUT_HASHES, reviewed)

    font = ImageFont.load_default(size=22)
    cell_w, cell_h = 1000, 1450
    sheet_rows: list[dict[str, object]] = []
    for sheet_index in range((len(reviewed) + 3) // 4):
        batch = reviewed[sheet_index * 4 : (sheet_index + 1) * 4]
        sheet = Image.new("RGB", (cell_w * 2, cell_h * 2), "white")
        draw = ImageDraw.Draw(sheet)
        labels: list[str] = []
        for cell_index, row in enumerate(batch):
            x = (cell_index % 2) * cell_w
            y = (cell_index // 2) * cell_h
            with Image.open(IMAGES / f"{row['canvas_id']}.jpg") as source:
                source = source.convert("RGB")
                source.thumbnail((940, 1360), Image.Resampling.LANCZOS)
                sheet.paste(source, (x + (cell_w - source.width) // 2, y + 55 + (1360 - source.height) // 2))
            label = f"{row['canvas_id']} | {row['pages']}"
            labels.append(label)
            draw.text((x + 15, y + 15), label, fill="black", font=font)
            draw.rectangle((x, y, x + cell_w - 1, y + cell_h - 1), outline="#666666", width=2)
        sheet_path = SHEETS / f"sheet_{sheet_index + 1:02d}.jpg"
        sheet.save(sheet_path, quality=92)
        sheet_rows.append({"sheet": sheet_path.name, "labels": " || ".join(labels), "sha256": hashlib.sha256(sheet_path.read_bytes()).hexdigest()})
    write(TEMP_ROOT / "contact_sheet_manifest.tsv", sheet_rows)
    print(json.dumps({"pages": len(pages), "unique_canvases": len(reviewed), "contact_sheets": len(sheet_rows), "automated_visual_judgments": 0, "formal_rows_read": 0, "f84_rows_retained": 0}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
