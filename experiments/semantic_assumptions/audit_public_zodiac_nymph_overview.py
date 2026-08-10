#!/usr/bin/env python3
"""Audit Robert Teague's public 2007 zodiac-nymph overview without OCR.

The source is an old Microsoft Word file containing native digital text.  We
use LibreOffice only as a document-format converter; no image or OCR system is
invoked.  Blank cells are retained as UNKNOWN because the source gives no
legend saying that a blank means zero.
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import subprocess
import tempfile
import urllib.request
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
SOURCE_URL = (
    "https://www.as.up.krakow.pl/jvs/library/1-5-2007-06-24/"
    "Zodiac%20Section%20Nymph%20Overview.doc"
)
SOURCE_SHA256 = "7800efaac7cf2b13aa58c77c80f233c2eb63be3adec359765070697e32fb0026"

OUT_TSV = RESULTS / "public_zodiac_nymph_overview.tsv"
OUT_JSON = RESULTS / "public_zodiac_nymph_overview.json"
OUT_REPORT = RESULTS / "public_zodiac_nymph_overview_report.md"

SIGNS = [
    ("Pisces", "f70v2", "f70"),
    ("aries dark", "f70v1", "f70"),
    ("aries light", "f71r", "f71"),
    ("taurus light", "f71v", "f71"),
    ("taurus dark", "f72r1", "f72"),
    ("GEMINI", "f72r2", "f72"),
    ("CANCER", "f72r3", "f72"),
    ("LEO", "f72v3", "f72"),
    ("virgo", "f72v2", "f72"),
    ("libra", "f72v1", "f72"),
    ("scorpio", "f73r", "f73"),
    ("sagitt", "f73v", "f73"),
]

ATTRIBUTES = [
    "Nymphs",
    "Clothed Nymphs",
    "Color Clothes",
    "Crowned Nymphs",
    "Male Nymphs",
    "Stars",
    "Star w/ Tether",
    "Holding Star",
    "Holding Tether",
    "Cans",
    "Color Cans",
]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_bytes(obj: object) -> bytes:
    return (json.dumps(obj, sort_keys=True, indent=2) + "\n").encode("utf-8")


def fetch_source() -> bytes:
    request = urllib.request.Request(SOURCE_URL, headers={"User-Agent": "VManus-public-source-audit/1"})
    with urllib.request.urlopen(request, timeout=30) as response:
        data = response.read()
    if sha256(data) != SOURCE_SHA256:
        raise RuntimeError("public source SHA-256 mismatch")
    return data


def convert_doc_to_rows(data: bytes) -> list[list[str]]:
    # The snap-packaged LibreOffice available on the research host cannot read
    # /tmp, so use a private directory under the account home.  No path is
    # retained in any artifact.
    with tempfile.TemporaryDirectory(prefix="vmanus-public-source-", dir=Path.home()) as name:
        temp = Path(name)
        doc = temp / "nymph_overview.doc"
        doc.write_bytes(data)
        proc = subprocess.run(
            [
                "libreoffice",
                "--headless",
                "--convert-to",
                "txt:Text",
                "--outdir",
                str(temp),
                str(doc),
            ],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=60,
        )
        txt = temp / "nymph_overview.txt"
        if proc.returncode != 0 or not txt.is_file():
            raise RuntimeError("LibreOffice native-text conversion failed")
        lines = list(csv.reader(txt.read_text(encoding="utf-8-sig").splitlines(), delimiter="\t"))
    return lines


def parse_table(rows: list[list[str]]) -> dict[str, list[int | None]]:
    nonempty = [row for row in rows if any(cell.strip() for cell in row)]
    if not nonempty or nonempty[0] != ["Zodiac Section Nymph Overview"]:
        raise RuntimeError("unexpected document title")
    if len(nonempty) != 13:
        raise RuntimeError("unexpected native-text row count")
    header = nonempty[1]
    if len(header) != 13 or header[0] != "" or header[1:] != [item[0] for item in SIGNS]:
        raise RuntimeError("unexpected sign header")

    table: dict[str, list[int | None]] = {}
    for row in nonempty[2:]:
        if len(row) != 13:
            raise RuntimeError("unexpected table width")
        name = "Star w/ Tether" if row[0].replace("  ", " ") == "Star w/ Tether" else row[0]
        if name in table:
            raise RuntimeError("duplicate attribute row")
        values: list[int | None] = []
        for cell in row[1:]:
            values.append(None if cell == "" else int(cell))
        table[name] = values
    if list(table) != ATTRIBUTES:
        raise RuntimeError("unexpected attribute inventory or order")
    return table


def render_tsv(table: dict[str, list[int | None]]) -> bytes:
    columns = ["sign", "page", "physical_folio", *[a.upper().replace(" ", "_").replace("/", "_") for a in ATTRIBUTES]]
    lines = ["\t".join(columns)]
    for i, (sign, page, folio) in enumerate(SIGNS):
        cells = [sign, page, folio]
        cells.extend("UNKNOWN" if table[a][i] is None else str(table[a][i]) for a in ATTRIBUTES)
        lines.append("\t".join(cells))
    return ("\n".join(lines) + "\n").encode("utf-8")


def build_result(table: dict[str, list[int | None]], tsv_bytes: bytes) -> dict[str, object]:
    coverage = {name: sum(value is not None for value in values) for name, values in table.items()}
    complete = [name for name in ATTRIBUTES if coverage[name] == len(SIGNS)]
    nymphs = [int(value) for value in table["Nymphs"] if value is not None]
    stars = [int(value) for value in table["Stars"] if value is not None]
    if len(nymphs) != 12 or len(stars) != 12:
        raise RuntimeError("complete count rows unexpectedly incomplete")
    deficits = [n - s for n, s in zip(nymphs, stars)]
    deficit_pages = [SIGNS[i][1] for i, value in enumerate(deficits) if value > 0]
    deficit_folios = sorted({SIGNS[i][2] for i, value in enumerate(deficits) if value > 0})
    if any(value < 0 for value in deficits):
        raise RuntimeError("star count exceeds nymph count")

    gates = {
        "source_sha256_exact": True,
        "native_digital_text_not_ocr": True,
        "twelve_public_panels_four_physical_folios": len(SIGNS) == 12 and len({x[2] for x in SIGNS}) == 4,
        "nymph_total_is_299": sum(nymphs) == 299,
        "complete_attribute_rows_exactly_nymphs_and_stars": complete == ["Nymphs", "Stars"],
        "blank_cells_retained_as_unknown_not_zero": True,
        "complete_missing_star_contrast_spans_three_folios": len(deficit_folios) >= 3,
        "semantic_target_scored": False,
        "voynich_strings_opened": False,
    }
    decision = "STOP_UNSCORED_NO_INDEPENDENT_ATTRIBUTE_CONTRAST"
    return {
        "experiment": "PUBLIC_ZODIAC_NYMPH_OVERVIEW_CAPACITY",
        "status": decision,
        "decision": decision,
        "source": {
            "author": "Robert Teague",
            "deposit_date": "2007-06-24",
            "title": "Zodiac Section Nymph Overview",
            "url": SOURCE_URL,
            "sha256": SOURCE_SHA256,
            "format": "Microsoft Word 97-2003 native digital text",
            "extraction": "LibreOffice native document conversion; no OCR or image recognition",
        },
        "panel_count": 12,
        "physical_folios": ["f70", "f71", "f72", "f73"],
        "attribute_count": len(ATTRIBUTES),
        "attribute_coverage": coverage,
        "complete_attributes": complete,
        "blank_cell_policy": "UNKNOWN; the source contains no legend licensing blank=0",
        "complete_counts": {
            "nymph_total": sum(nymphs),
            "star_total": sum(stars),
            "nymph_minus_star_by_page": {SIGNS[i][1]: deficits[i] for i in range(12)},
            "positive_deficit_pages": deficit_pages,
            "positive_deficit_folios": deficit_folios,
        },
        "capacity_assessment": {
            "only_complete_rows": ["Nymphs", "Stars"],
            "nymph_count_is_layout_locked": "15 on the four split Aries/Taurus panels; 29 on Pisces; 30 otherwise",
            "missing_star_positive_pages": deficit_pages,
            "missing_star_positive_pages_all_on_one_folio": deficit_folios == ["f72"],
            "incomplete_rows_can_supply_positive_descriptions_but_not_negative_controls": True,
        },
        "gates": gates,
        "claim_ceiling": (
            "A provenance-clean public human overview supplies exact page-level zodiac counts. "
            "Its blank cells are unknown, not negatives; its only complete non-layout contrast "
            "(nymph minus star count) is positive only on f72. It therefore cannot ground a "
            "transferable figure attribute, Voynich stem, word, meaning, plaintext, or translation."
        ),
        "artifacts": {"public_zodiac_nymph_overview.tsv": sha256(tsv_bytes)},
    }


def render_report(result: dict[str, object]) -> bytes:
    coverage = result["attribute_coverage"]
    counts = result["complete_counts"]
    text = f"""# Public zodiac-nymph overview capacity audit

Status: **{result['decision']}**

Robert Teague's public 2007 `Zodiac Section Nymph Overview` is a genuine new
human-authored source for the f70--f73 zodiac panels. Its native digital table
contains 12 panels on four physical folios and 11 attributes. It was converted
as document text; no OCR, image recognition, or new visual annotation was used.

Only `Nymphs` and `Stars` are filled on all 12 panels. They total
**{counts['nymph_total']}** and **{counts['star_total']}**. Their positive differences occur on
{', '.join(counts['positive_deficit_pages'])}, all on physical folio
**{counts['positive_deficit_folios'][0]}**. The nymph-count contrast is itself
locked to the split 15-record Aries/Taurus layout versus the full pages.

The other nine rows have coverage {json.dumps(coverage, sort_keys=True)}. The
source provides no legend saying that a blank cell means zero, so every blank
is retained as **UNKNOWN**. These rows can document positive observations but
cannot provide honest absent/negative controls.

Therefore this source improves the public factual inventory but does not open a
fair semantic score. A future route needs explicit zero/absent values or
slot-level positive/negative attributes spanning independent folios. No
Voynich string was opened or scored, and no figure attribute, stem, word,
meaning, plaintext, or translation follows.

Public source: {SOURCE_URL}
"""
    return text.encode("utf-8")


def install_no_clobber(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    fd = os.open(path, flags, 0o644)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
    except Exception:
        path.unlink(missing_ok=True)
        raise


def main() -> None:
    for path in (OUT_TSV, OUT_JSON, OUT_REPORT):
        if path.exists():
            raise SystemExit(f"refusing to overwrite {path}")
    source = fetch_source()
    table = parse_table(convert_doc_to_rows(source))
    tsv_bytes = render_tsv(table)
    result = build_result(table, tsv_bytes)
    json_bytes = canonical_bytes(result)
    report_bytes = render_report(result)
    install_no_clobber(OUT_TSV, tsv_bytes)
    try:
        install_no_clobber(OUT_JSON, json_bytes)
        install_no_clobber(OUT_REPORT, report_bytes)
    except Exception:
        OUT_TSV.unlink(missing_ok=True)
        OUT_JSON.unlink(missing_ok=True)
        OUT_REPORT.unlink(missing_ok=True)
        raise
    print(json.dumps({"decision": result["decision"], "outputs": [str(OUT_TSV), str(OUT_JSON), str(OUT_REPORT)]}, sort_keys=True))


if __name__ == "__main__":
    main()
