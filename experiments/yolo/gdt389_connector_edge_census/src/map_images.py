#!/usr/bin/env python3
"""Guarded Yale IIIF canvas mapping for the frozen GDT389 page allow-list.

Rejected canvas objects are scanned only as raw JSON bytes long enough to read
their top-level page-like label. No other rejected-canvas field is parsed or
retained. Only allow-listed, non-f84 canvas objects are decoded.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
import urllib.request
from pathlib import Path


def root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("repository root not found")


ROOT = root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt389_connector_edge_census"
ART = BASE / "artifacts"
FRAME = ROOT / "experiments/yolo/gdt388_acquisition_ready_relation_edge_protocol/artifacts/gdt388_page_frame.tsv"
MANIFEST_URL = "https://collections.library.yale.edu/manifests/2002046"


def page_side(page: str) -> str:
    match = re.match(r"^f(\d+[rv])(?:\d+)?$", page.lower())
    if not match:
        raise ValueError(page)
    return match.group(1)


def iter_raw_canvas_objects(response):
    marker = b'"items":['
    prefix = b""
    while marker not in prefix:
        chunk = response.read(65536)
        if not chunk:
            raise RuntimeError("manifest root items array not found")
        prefix += chunk
        if len(prefix) > 1_000_000:
            raise RuntimeError("manifest prefix unexpectedly large")
    pending = prefix.split(marker, 1)[1]
    depth = 0
    in_string = False
    escaped = False
    buffer = bytearray()
    started = False
    while True:
        if not pending:
            pending = response.read(65536)
            if not pending:
                break
        for byte in pending:
            char = chr(byte)
            if not started:
                if char == "]":
                    return
                if char != "{":
                    continue
                started = True
                depth = 1
                buffer = bytearray(b"{")
                in_string = False
                escaped = False
                continue
            buffer.append(byte)
            if in_string:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == '"':
                    in_string = False
                continue
            if char == '"':
                in_string = True
            elif char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    yield bytes(buffer)
                    started = False
                    buffer = bytearray()
        pending = b""


def label_values(raw: bytes) -> list[str]:
    values: list[str] = []
    for match in re.finditer(rb'"label"\s*:\s*(\{[^{}]*\})', raw):
        try:
            block = json.loads(match.group(1))
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        if not isinstance(block, dict):
            continue
        for item in block.values():
            if isinstance(item, list):
                values.extend(str(value) for value in item)
    return values


def image_service_id(value):
    if isinstance(value, dict):
        if value.get("type") in {"ImageService2", "ImageService3"} and isinstance(value.get("id"), str):
            return value["id"]
        for child in value.values():
            found = image_service_id(child)
            if found:
                return found
    elif isinstance(value, list):
        for child in value:
            found = image_service_id(child)
            if found:
                return found
    return None


def canvas_oid(value: dict) -> str:
    identifiers = []
    stack = [value]
    while stack:
        item = stack.pop()
        if isinstance(item, dict):
            identifier = item.get("id")
            if isinstance(identifier, str):
                identifiers.append(identifier)
            stack.extend(item.values())
        elif isinstance(item, list):
            stack.extend(item)
    for identifier in identifiers:
        match = re.search(r"/canvas/(\d+)(?:/|$)", identifier)
        if match:
            return match.group(1)
    raise RuntimeError("canvas OID missing")


def main() -> int:
    with FRAME.open(encoding="utf-8", newline="") as handle:
        frame = list(csv.DictReader(handle, delimiter="\t"))
    pages = sorted(row["page"] for row in frame)
    assert len(pages) == 61 and all(not page.lower().startswith("f84") for page in pages)
    side_to_pages: dict[str, list[str]] = {}
    for page in pages:
        side_to_pages.setdefault(page_side(page), []).append(page)

    mappings: list[dict[str, str | int]] = []
    request = urllib.request.Request(MANIFEST_URL, headers={"User-Agent": "VManus-GDT389/1.0"})
    with urllib.request.urlopen(request, timeout=60) as response:
        manifest_etag = response.headers.get("ETag", "")
        manifest_last_modified = response.headers.get("Last-Modified", "")
        for raw in iter_raw_canvas_objects(response):
            labels = label_values(raw)
            page_like = sorted({side for label in labels for side in re.findall(r"(?<!\d)(\d+[rv])(?!\d)", label.lower())})
            if not page_like:
                continue
            # The raw label is the only rejected-canvas field inspected. Mixed
            # f84 canvases are discarded before JSON object decoding.
            if any(side.startswith("84") for side in page_like):
                continue
            matched_pages = sorted({page for side in page_like for page in side_to_pages.get(side, [])})
            if not matched_pages:
                continue
            canvas = json.loads(raw)
            oid = canvas_oid(canvas)
            service = image_service_id(canvas) or f"https://collections.library.yale.edu/iiif/2/{oid}"
            label = next((value for value in labels if re.search(r"\d+[rv]", value.lower())), labels[-1] if labels else "")
            for page in matched_pages:
                mappings.append(
                    {
                        "page": page,
                        "physical_folio": next(row["physical_folio"] for row in frame if row["page"] == page),
                        "canvas_id": oid,
                        "canvas_label": label,
                        "canvas_width": int(canvas.get("width", 0)),
                        "canvas_height": int(canvas.get("height", 0)),
                        "image_service_id": service,
                        "review_image_url": service.rstrip("/") + "/full/1600,/0/default.jpg",
                        "mapping_basis": "OFFICIAL_IIIF_CANVAS_LABEL_ALLOWLIST_MATCH",
                        "formal_access_state": "SEALED",
                    }
                )

    mapped_pages = {row["page"] for row in mappings}
    for page in sorted(set(pages) - mapped_pages):
        mappings.append(
            {
                "page": page,
                "physical_folio": next(row["physical_folio"] for row in frame if row["page"] == page),
                "canvas_id": "",
                "canvas_label": "",
                "canvas_width": 0,
                "canvas_height": 0,
                "image_service_id": "",
                "review_image_url": "",
                "mapping_basis": "UNMAPPED_NOT_GUESSED",
                "formal_access_state": "SEALED",
            }
        )
    mappings.sort(key=lambda row: (str(row["page"]), str(row["canvas_id"])))
    fields = list(mappings[0])
    path = ART / "gdt389_image_manifest.tsv"
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(mappings)
    metadata = {
        "schema": "GDT389_IMAGE_MAPPING_V1",
        "manifest_url": MANIFEST_URL,
        "manifest_etag": manifest_etag,
        "manifest_last_modified": manifest_last_modified,
        "allowed_pages": len(pages),
        "mapped_pages": len(mapped_pages),
        "mapping_rows": len(mappings),
        "mixed_f84_canvas_fields_retained": 0,
        "rejected_canvas_nonlabel_fields_parsed_or_retained": 0,
        "formal_rows_read": 0,
        "image_manifest_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }
    (ART / "gdt389_image_mapping.json").write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")
    print(json.dumps(metadata, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
