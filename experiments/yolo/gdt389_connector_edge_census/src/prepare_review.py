#!/usr/bin/env python3
"""Prepare the direct-visual GDT389 review packet from the safe image manifest.

This utility performs no OCR, image classification, captioning, or geometric
judgment.  It downloads the already allow-listed Yale review images, records
their hashes, and places deterministic thumbnails into contact sheets.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import tempfile
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("repository root not found")


ROOT = root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt389_connector_edge_census"
ART = BASE / "artifacts"
IMAGE_MANIFEST = ART / "gdt389_image_manifest.tsv"
PUBLIC_HASH_MANIFEST = ART / "gdt389_review_image_hashes.tsv"
FREEZE = ART / "gdt389_pre_image_freeze.json"
REVIEW_ROOT = Path(tempfile.gettempdir()) / "gdt389_review_v1"
DOWNLOADS = REVIEW_ROOT / "images"
SHEETS = REVIEW_ROOT / "contact_sheets"


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    review_order = freeze["page_universe"]["review_order"]
    assert len(review_order) == 61
    assert all(not page.lower().startswith("f84") for page in review_order)

    with IMAGE_MANIFEST.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    assert rows and all(not row["page"].lower().startswith("f84") for row in rows)
    assert all("84r" not in row["canvas_label"].lower() and "84v" not in row["canvas_label"].lower() for row in rows)
    assert {row["page"] for row in rows} == set(review_order)

    order_index = {page: index for index, page in enumerate(review_order)}
    by_canvas: dict[str, dict[str, object]] = {}
    for row in rows:
        canvas_id = row["canvas_id"]
        assert canvas_id and row["review_image_url"]
        entry = by_canvas.setdefault(
            canvas_id,
            {
                "canvas_id": canvas_id,
                "canvas_label": row["canvas_label"],
                "review_image_url": row["review_image_url"],
                "pages": [],
            },
        )
        entry["pages"].append(row["page"])
    canvases = sorted(
        by_canvas.values(),
        key=lambda entry: min(order_index[page] for page in entry["pages"]),
    )
    assert len(canvases) == 50

    DOWNLOADS.mkdir(parents=True, exist_ok=True)
    SHEETS.mkdir(parents=True, exist_ok=True)
    downloaded: list[dict[str, object]] = []
    for entry in canvases:
        canvas_id = str(entry["canvas_id"])
        path = DOWNLOADS / f"{canvas_id}.jpg"
        if path.is_file():
            data = path.read_bytes()
        else:
            request = urllib.request.Request(str(entry["review_image_url"]), headers={"User-Agent": "VManus-GDT389/1.0"})
            with urllib.request.urlopen(request, timeout=90) as response:
                data = response.read()
            path.write_bytes(data)
        with Image.open(io.BytesIO(data)) as image:
            width, height = image.size
        downloaded.append(
            {
                **entry,
                "pages": ",".join(sorted(entry["pages"], key=order_index.get)),
                "local_name": path.name,
                "pixel_width": width,
                "pixel_height": height,
                "sha256": sha_bytes(data),
            }
        )

    manifest_path = REVIEW_ROOT / "download_manifest.tsv"
    fields = list(downloaded[0])
    with manifest_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(downloaded)
    public_fields = [
        "canvas_id",
        "canvas_label",
        "pages",
        "review_image_url",
        "pixel_width",
        "pixel_height",
        "sha256",
    ]
    with PUBLIC_HASH_MANIFEST.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=public_fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows({field: row[field] for field in public_fields} for row in downloaded)

    font = ImageFont.load_default(size=20)
    cell_w, cell_h = 780, 900
    thumb_w, thumb_h = 740, 830
    per_sheet = 6
    sheet_rows: list[dict[str, object]] = []
    for sheet_index in range((len(downloaded) + per_sheet - 1) // per_sheet):
        batch = downloaded[sheet_index * per_sheet : (sheet_index + 1) * per_sheet]
        sheet = Image.new("RGB", (cell_w * 3, cell_h * 2), "white")
        draw = ImageDraw.Draw(sheet)
        labels: list[str] = []
        for cell_index, entry in enumerate(batch):
            x = (cell_index % 3) * cell_w
            y = (cell_index // 3) * cell_h
            path = DOWNLOADS / str(entry["local_name"])
            with Image.open(path) as source:
                source = source.convert("RGB")
                source.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
                px = x + (cell_w - source.width) // 2
                py = y + 50 + (thumb_h - source.height) // 2
                sheet.paste(source, (px, py))
            label = f"{entry['pages']} | Yale {entry['canvas_id']} | {entry['canvas_label']}"
            labels.append(label)
            draw.text((x + 12, y + 12), label, fill="black", font=font)
            draw.rectangle((x, y, x + cell_w - 1, y + cell_h - 1), outline="#777777", width=2)
        sheet_path = SHEETS / f"sheet_{sheet_index + 1:02d}.jpg"
        sheet.save(sheet_path, quality=92)
        sheet_rows.append(
            {
                "sheet": sheet_path.name,
                "canvas_count": len(batch),
                "labels": " || ".join(labels),
                "sha256": hashlib.sha256(sheet_path.read_bytes()).hexdigest(),
            }
        )
    sheet_manifest = REVIEW_ROOT / "contact_sheet_manifest.tsv"
    with sheet_manifest.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(sheet_rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(sheet_rows)
    print(
        json.dumps(
            {
                "allowed_pages": len(review_order),
                "unique_canvases": len(downloaded),
                "contact_sheets": len(sheet_rows),
                "download_manifest_sha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
                "contact_sheet_manifest_sha256": hashlib.sha256(sheet_manifest.read_bytes()).hexdigest(),
                "public_hash_manifest_sha256": hashlib.sha256(PUBLIC_HASH_MANIFEST.read_bytes()).hexdigest(),
                "automated_visual_judgments": 0,
                "formal_rows_read": 0,
                "f84_rows_retained": 0,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
