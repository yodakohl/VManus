#!/usr/bin/env python3
"""Create expansion-free diplomatic control tables plus a truth commitment."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import unicodedata
import xml.etree.ElementTree as ET
import zipfile
from collections import Counter
from pathlib import Path

STE_SHA = "3db06c80345e584e5b6af7e062af839964312b92bcf1edb8b88aa05110024df6"
NB_SHA = "59e5264acb4546477567e78c8b3d444c472f1a0a5256ee0ee7d0407a70904652"
NB_MD5 = "ce2c6150d9fc45ac4b4ea2a439b7aa8e"
PAGE_NS = "http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15"
TEI_NS = "http://www.tei-c.org/ns/1.0"
LINE_FIELDS = (
    "corpus", "record_id", "source_record_key", "book_or_ms", "page_id",
    "line_id", "line_index", "writer_id", "diplomatic_bare",
    "diplomatic_marked", "surface_group_count", "abbreviation_site_count",
    "record_line_count", "record_position_quartile",
)
SITE_FIELDS = (
    "site_id", "corpus", "record_id", "line_id", "site_index_in_record",
    "surface_span_bare", "surface_span_marked", "source_element",
)


def file_digest(path: Path, algorithm: str = "sha256") -> str:
    h = hashlib.new(algorithm)
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def canonical_hash(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()


def local(element: ET.Element) -> str:
    return element.tag.rsplit("}", 1)[-1]


def render(element: ET.Element, *, expanded: bool, marked: bool, linebreaks: bool = False) -> str:
    out: list[str] = []

    def walk(node: ET.Element) -> None:
        tag = local(node)
        if tag == "ex" and not expanded:
            return
        if tag == "am":
            return
        if tag == "lb" and linebreaks:
            out.append("\n")
        if node.text:
            out.append(node.text)
        for child in node:
            walk(child)
            if child.tail:
                out.append(child.tail)
        if marked and tag in {"expan", "abbr"}:
            out.append("¤")

    walk(element)
    return unicodedata.normalize("NFC", "".join(out))


def clean_line(text: str) -> str:
    return " ".join(text.replace("\n", " ").split())


def site_id(corpus: str, record: str, ordinal: int) -> str:
    return "AS" + hashlib.sha256(f"{corpus}|{record}|{ordinal}".encode()).hexdigest()[:14].upper()


def zip_xml_members(path: Path) -> list[str]:
    with zipfile.ZipFile(path) as archive:
        members = [name for name in archive.namelist()
                   if re.fullmatch(r"nuremberg_letterbooks/diplomatic-regularised/Band[2-5]/\d+\.xml", name)]
    return sorted(members, key=lambda name: (int(name.split("/")[-2][4:]), int(Path(name).stem)))


def nuremberg(path: Path) -> tuple[list[dict[str, object]], list[dict[str, object]], list[tuple], list[tuple]]:
    lines: list[dict[str, object]] = []
    sites: list[dict[str, object]] = []
    truth_lines: list[tuple] = []
    truth_regularized: list[tuple] = []
    with zipfile.ZipFile(path) as archive:
        for member in zip_xml_members(path):
            parts = member.split("/")
            book = parts[-2]
            numeric_id = int(Path(member).stem)
            record = f"NB_B{book[4:]}_R{numeric_id:06d}"
            root = ET.fromstring(archive.read(member))
            record_lines: list[dict[str, object]] = []
            record_sites: list[dict[str, object]] = []
            site_ordinal = 0
            line_ordinal = 0
            for page_index, page in enumerate(root.findall(f".//{{{PAGE_NS}}}Page"), 1):
                page_id = page.attrib.get("imageFilename", f"PAGE_{page_index:03d}")
                for text_line in page.findall(f".//{{{PAGE_NS}}}TextLine"):
                    unicode = text_line.find(f"{{{PAGE_NS}}}TextEquiv/{{{PAGE_NS}}}Unicode")
                    if unicode is None:
                        continue
                    line_ordinal += 1
                    line_id = f"{record}_L{line_ordinal:04d}"
                    bare = clean_line(render(unicode, expanded=False, marked=False))
                    marked = clean_line(render(unicode, expanded=False, marked=True))
                    expanded = clean_line(render(unicode, expanded=True, marked=False))
                    line_sites = []
                    for node in unicode.iter():
                        if local(node) != "expan":
                            continue
                        site_ordinal += 1
                        sid = site_id("NUREMBERG", record, site_ordinal)
                        span = clean_line(render(node, expanded=False, marked=False))
                        span_expanded = clean_line(render(node, expanded=True, marked=False))
                        line_sites.append(sid)
                        record_sites.append({
                            "site_id": sid, "corpus": "NUREMBERG", "record_id": record,
                            "line_id": line_id, "site_index_in_record": site_ordinal,
                            "surface_span_bare": span, "surface_span_marked": span + "¤",
                            "source_element": "expan",
                        })
                        truth_lines.append(("SITE", sid, span_expanded))
                    record_lines.append({
                        "corpus": "NUREMBERG", "record_id": record,
                        "source_record_key": f"{book}/{numeric_id}.xml", "book_or_ms": book,
                        "page_id": page_id, "line_id": line_id, "line_index": line_ordinal,
                        "writer_id": text_line.attrib.get("writerID", "UNKNOWN"),
                        "diplomatic_bare": bare, "diplomatic_marked": marked,
                        "surface_group_count": len(bare.split()),
                        "abbreviation_site_count": len(line_sites),
                    })
                    truth_lines.append(("LINE", line_id, expanded))
            total = len(record_lines)
            for row in record_lines:
                row["record_line_count"] = total
                row["record_position_quartile"] = min(3, 4 * (int(row["line_index"]) - 1) // max(1, total))
            lines.extend(record_lines)
            sites.extend(record_sites)
            for div in root.iter():
                if local(div) != "div" or div.attrib.get("type") == "regularised":
                    continue
                text = clean_line(render(div, expanded=True, marked=False, linebreaks=True))
                truth_regularized.append((record, div.attrib.get("type", "UNKNOWN"), text))
    return lines, sites, truth_lines, truth_regularized


def ste1(path: Path) -> tuple[list[dict[str, object]], list[dict[str, object]], list[tuple], list[tuple]]:
    root = ET.parse(path).getroot()
    lines: list[dict[str, object]] = []
    sites: list[dict[str, object]] = []
    truth_lines: list[tuple] = []
    truth_regularized: list[tuple] = []
    segments = root.findall(f".//{{{TEI_NS}}}text//{{{TEI_NS}}}seg")
    for seg_index, seg in enumerate(segments, 1):
        record = f"STE1_SEG{seg_index:02d}"
        bare_parts = render(seg, expanded=False, marked=False, linebreaks=True).split("\n")
        marked_parts = render(seg, expanded=False, marked=True, linebreaks=True).split("\n")
        expanded_parts = render(seg, expanded=True, marked=False, linebreaks=True).split("\n")
        triples = [(clean_line(a), clean_line(b), clean_line(c)) for a, b, c in zip(bare_parts, marked_parts, expanded_parts)]
        triples = [triple for triple in triples if any(triple)]
        seg_sites = [node for node in seg.iter() if local(node) == "abbr"]
        site_cursor = 0
        total = len(triples)
        for line_index, (bare, marked, expanded) in enumerate(triples, 1):
            line_id = f"{record}_L{line_index:04d}"
            count = marked.count("¤")
            for _ in range(count):
                node = seg_sites[site_cursor]
                site_cursor += 1
                sid = site_id("STE1", record, site_cursor)
                span = clean_line(render(node, expanded=False, marked=False))
                span_expanded = clean_line(render(node, expanded=True, marked=False))
                sites.append({
                    "site_id": sid, "corpus": "STE1", "record_id": record,
                    "line_id": line_id, "site_index_in_record": site_cursor,
                    "surface_span_bare": span, "surface_span_marked": span + "¤",
                    "source_element": "abbr",
                })
                truth_lines.append(("SITE", sid, span_expanded))
            lines.append({
                "corpus": "STE1", "record_id": record, "source_record_key": f"seg/{seg_index}",
                "book_or_ms": "Ste1", "page_id": "046v", "line_id": line_id,
                "line_index": line_index, "writer_id": "UNKNOWN",
                "diplomatic_bare": bare, "diplomatic_marked": marked,
                "surface_group_count": len(bare.split()), "abbreviation_site_count": count,
                "record_line_count": total,
                "record_position_quartile": min(3, 4 * (line_index - 1) // max(1, total)),
            })
            truth_lines.append(("LINE", line_id, expanded))
        assert site_cursor == len(seg_sites), (record, site_cursor, len(seg_sites))
        truth_regularized.append((record, "technical_recipe_record", clean_line(" ".join(c for _, _, c in triples))))
    return lines, sites, truth_lines, truth_regularized


def write_tsv(path: Path, fields: tuple[str, ...], rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ste1", type=Path, required=True)
    parser.add_argument("--nuremberg", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("."))
    args = parser.parse_args()
    assert file_digest(args.ste1) == STE_SHA
    assert file_digest(args.nuremberg) == NB_SHA
    assert file_digest(args.nuremberg, "md5") == NB_MD5
    nb_lines, nb_sites, nb_truth, nb_regularized = nuremberg(args.nuremberg)
    st_lines, st_sites, st_truth, st_regularized = ste1(args.ste1)
    lines = st_lines + nb_lines
    sites = st_sites + nb_sites
    assert len({row["line_id"] for row in lines}) == len(lines)
    assert len({row["site_id"] for row in sites}) == len(sites)
    assert sum(int(row["abbreviation_site_count"]) for row in lines) == len(sites)
    assert not any("<ex" in row["diplomatic_bare"] or "<ex" in row["diplomatic_marked"] for row in lines)
    # These are external controls and expose no Voynich page/locus field at all.
    assert {row["corpus"] for row in lines} == {"STE1", "NUREMBERG"}
    args.output_dir.mkdir(parents=True, exist_ok=True)
    line_path = args.output_dir / "gdt155_blinded_diplomatic.tsv"
    site_path = args.output_dir / "gdt155_blinded_abbreviation_sites.tsv"
    write_tsv(line_path, LINE_FIELDS, lines)
    write_tsv(site_path, SITE_FIELDS, sites)
    truth_material = {
        "expanded_line_and_site_truth": sorted(st_truth + nb_truth),
        "regularized_or_record_truth": sorted(st_regularized + nb_regularized),
    }
    counts = Counter(row["corpus"] for row in lines)
    site_counts = Counter(row["corpus"] for row in sites)
    record_counts = Counter((row["corpus"], row["record_id"]) for row in lines)
    result = {
        "schema": "GDT155_BLIND_SOURCE_FREEZE_V1",
        "status": "BLINDED_DIPLOMATIC_SURFACE_FROZEN_BEFORE_FULL_UNBLIND",
        "sources": {
            "ste1_sha256": STE_SHA,
            "nuremberg_labels_sha256": NB_SHA,
            "nuremberg_labels_md5": NB_MD5,
        },
        "counts": {
            "lines": len(lines), "abbreviation_sites": len(sites),
            "records": len(record_counts), "ste1_lines": counts["STE1"],
            "nuremberg_lines": counts["NUREMBERG"], "ste1_sites": site_counts["STE1"],
            "nuremberg_sites": site_counts["NUREMBERG"],
        },
        "truth_content_sha256": canonical_hash(truth_material),
        "truth_exported": False,
        "protocol": {
            "method_sha256": file_digest(Path(__file__).resolve().parent / "GDT155_MEDIEVAL_ABBREVIATION_POSITIVE_CONTROL_METHOD.md"),
            "source_audit_sha256": file_digest(Path(__file__).resolve().parent / "GDT155_MEDIEVAL_ABBREVIATION_SOURCE_AUDIT.md"),
            "source_manifest_sha256": file_digest(Path(__file__).resolve().parent / "gdt155_source_manifest.tsv"),
            "source_provenance_sha256": file_digest(Path(__file__).resolve().parent / "gdt155_source_provenance.json"),
        },
        "implementation": {
            "prepare_gdt155_blind_positive_controls.py": file_digest(Path(__file__).resolve()),
            "fetch_gdt155_positive_control_sources.py": file_digest(Path(__file__).resolve().parent / "fetch_gdt155_positive_control_sources.py"),
        },
        "blinded_outputs": {
            line_path.name: file_digest(line_path),
            site_path.name: file_digest(site_path),
        },
        "f84": {"voynich_inputs": 0, "voynich_page_or_locus_columns": 0, "accessed": False},
    }
    result["freeze_content_sha256"] = canonical_hash(result)
    (args.output_dir / "gdt155_source_freeze.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(result["counts"], sort_keys=True))


if __name__ == "__main__":
    main()
