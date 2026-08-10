#!/usr/bin/env python3
"""Production-free validation of the public zodiac-nymph capacity stop."""

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

INPUT_TSV = RESULTS / "public_zodiac_nymph_overview.tsv"
INPUT_JSON = RESULTS / "public_zodiac_nymph_overview.json"
INPUT_REPORT = RESULTS / "public_zodiac_nymph_overview_report.md"
OUT_JSON = RESULTS / "public_zodiac_nymph_overview_validation.json"
OUT_REPORT = RESULTS / "public_zodiac_nymph_overview_validation.md"

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

ATTRS = [
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

# Independent diplomatic transcription of the source's 11 rows.  None means
# an empty cell in the native document, never a semantic zero.
EXPECTED = {
    "Nymphs": [29, 15, 15, 15, 15, 30, 30, 30, 30, 30, 30, 30],
    "Clothed Nymphs": [None, 10, 14, 12, None, 4, None, None, None, None, None, None],
    "Color Clothes": [None, None, 14, 12, None, None, None, None, None, None, None, None],
    "Crowned Nymphs": [None, None, None, None, None, None, 1, 1, None, 1, None, None],
    "Male Nymphs": [None, 1, 2, None, None, 4, None, 1, None, None, None, None],
    "Stars": [29, 15, 15, 15, 15, 29, 28, 29, 30, 30, 30, 30],
    "Star w/ Tether": [29, 12, None, None, None, None, 19, 7, 6, 1, 2, None],
    "Holding Star": [None, 3, 15, 15, 15, 29, 28, 27, 30, 30, 30, 28],
    "Holding Tether": [29, 12, None, None, None, None, None, 2, None, None, None, 2],
    "Cans": [29, 15, 15, 15, 5, 3, None, None, 1, None, None, None],
    "Color Cans": [8, 1, 13, None, None, None, None, None, None, None, None, None],
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(obj: object) -> bytes:
    return (json.dumps(obj, sort_keys=True, indent=2) + "\n").encode()


def source_rows() -> list[list[str]]:
    request = urllib.request.Request(SOURCE_URL, headers={"User-Agent": "VManus-clean-validation/1"})
    with urllib.request.urlopen(request, timeout=30) as response:
        raw = response.read()
    if digest(raw) != SOURCE_SHA256:
        raise RuntimeError("source digest mismatch")
    with tempfile.TemporaryDirectory(prefix="vmanus-validation-", dir=Path.home()) as name:
        folder = Path(name)
        doc = folder / "source.doc"
        doc.write_bytes(raw)
        conversion = subprocess.run(
            ["libreoffice", "--headless", "--convert-to", "txt:Text", "--outdir", str(folder), str(doc)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=60,
            check=False,
        )
        txt = folder / "source.txt"
        if conversion.returncode or not txt.exists():
            raise RuntimeError("native document conversion failed")
        return list(csv.reader(txt.read_text(encoding="utf-8-sig").splitlines(), delimiter="\t"))


def reconstruct() -> tuple[dict[str, list[int | None]], int]:
    checks = 0
    rows = [row for row in source_rows() if any(cell for cell in row)]
    assert rows[0] == ["Zodiac Section Nymph Overview"]
    checks += 1
    assert rows[1] == ["", *[x[0] for x in SIGNS]]
    checks += 1
    assert len(rows) == 13
    checks += 1
    found: dict[str, list[int | None]] = {}
    for row in rows[2:]:
        key = "Star w/ Tether" if row[0].replace("  ", " ") == "Star w/ Tether" else row[0]
        assert key not in found and len(row) == 13
        checks += 2
        values = [None if cell == "" else int(cell) for cell in row[1:]]
        found[key] = values
        assert values == EXPECTED[key]
        checks += 1 + len(values)
    assert list(found) == ATTRS
    checks += 1
    return found, checks


def expected_tsv(table: dict[str, list[int | None]]) -> bytes:
    cols = ["sign", "page", "physical_folio", *[x.upper().replace(" ", "_").replace("/", "_") for x in ATTRS]]
    rows = ["\t".join(cols)]
    for i, (sign, page, folio) in enumerate(SIGNS):
        rows.append("\t".join([sign, page, folio, *[("UNKNOWN" if table[a][i] is None else str(table[a][i])) for a in ATTRS]]))
    return ("\n".join(rows) + "\n").encode()


def install(path: Path, data: bytes) -> None:
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    with os.fdopen(fd, "wb") as handle:
        handle.write(data)


def main() -> None:
    if OUT_JSON.exists() or OUT_REPORT.exists():
        raise SystemExit("refusing to overwrite validation artifacts")
    table, checks = reconstruct()
    tsv = expected_tsv(table)
    stored_tsv = INPUT_TSV.read_bytes()
    stored_json_bytes = INPUT_JSON.read_bytes()
    stored_report = INPUT_REPORT.read_bytes()
    assert stored_tsv == tsv
    checks += 1
    result = json.loads(stored_json_bytes)
    assert stored_json_bytes == canonical(result)
    checks += 1
    coverage = {name: sum(value is not None for value in table[name]) for name in ATTRS}
    assert result["attribute_coverage"] == coverage
    checks += len(coverage)
    assert result["complete_attributes"] == ["Nymphs", "Stars"]
    checks += 1
    nymphs = EXPECTED["Nymphs"]
    stars = EXPECTED["Stars"]
    assert all(value is not None for value in nymphs + stars)
    nn = [int(x) for x in nymphs]
    ss = [int(x) for x in stars]
    deficits = [a - b for a, b in zip(nn, ss)]
    deficit_pages = [SIGNS[i][1] for i, value in enumerate(deficits) if value]
    assert sum(nn) == 299 and sum(ss) == 295
    assert deficit_pages == ["f72r2", "f72r3", "f72v3"]
    assert {SIGNS[i][2] for i, value in enumerate(deficits) if value} == {"f72"}
    checks += 4
    assert result["complete_counts"]["nymph_minus_star_by_page"] == {SIGNS[i][1]: deficits[i] for i in range(12)}
    checks += 12
    assert result["source"]["sha256"] == SOURCE_SHA256
    assert result["source"]["url"] == SOURCE_URL
    assert result["source"]["author"] == "Robert Teague"
    checks += 3
    assert result["decision"] == "STOP_UNSCORED_NO_INDEPENDENT_ATTRIBUTE_CONTRAST"
    assert result["status"] == result["decision"]
    checks += 2
    gates = result["gates"]
    assert gates["complete_missing_star_contrast_spans_three_folios"] is False
    assert gates["semantic_target_scored"] is False
    assert gates["voynich_strings_opened"] is False
    assert all(value is True for key, value in gates.items() if key not in {"complete_missing_star_contrast_spans_three_folios", "semantic_target_scored", "voynich_strings_opened"})
    checks += len(gates)
    assert result["artifacts"] == {"public_zodiac_nymph_overview.tsv": digest(tsv)}
    checks += 1
    report_text = stored_report.decode()
    for witness in (
        "Status: **STOP_UNSCORED_NO_INDEPENDENT_ATTRIBUTE_CONTRAST**",
        "**UNKNOWN**",
        "No\nVoynich string was opened or scored",
        SOURCE_URL,
    ):
        assert witness in report_text
        checks += 1

    validation = {
        "experiment": "PUBLIC_ZODIAC_NYMPH_OVERVIEW_CAPACITY_VALIDATION",
        "status": "PASS_INDEPENDENT_LIVE_SOURCE_RECONSTRUCTION",
        "checks": checks,
        "source_sha256": SOURCE_SHA256,
        "input_hashes": {
            INPUT_TSV.name: digest(stored_tsv),
            INPUT_JSON.name: digest(stored_json_bytes),
            INPUT_REPORT.name: digest(stored_report),
        },
        "reconstructed": {
            "panels": 12,
            "folios": 4,
            "attributes": 11,
            "complete_attributes": ["Nymphs", "Stars"],
            "nymph_total": 299,
            "star_total": 295,
            "positive_deficit_pages": deficit_pages,
            "positive_deficit_folios": ["f72"],
        },
        "decision": result["decision"],
        "target_isolation": {
            "voynich_transcriptions_opened": False,
            "voynich_strings_scored": False,
            "ocr_used": False,
            "automated_image_recognition_used": False,
        },
        "claim_ceiling": result["claim_ceiling"],
    }
    validation_bytes = canonical(validation)
    report = f"""# Public zodiac-nymph overview validation

Status: **PASS_INDEPENDENT_LIVE_SOURCE_RECONSTRUCTION**

The independent validator downloaded the public Word source, verified SHA-256
`{SOURCE_SHA256}`, converted its native digital text without OCR, and passed
**{checks}** checks. It exactly reconstructed 12 panels, four folios, 11
attributes, the 299 nymph and 295 star totals, every UNKNOWN cell, the TSV, and
the source-capacity stop.

Only `Nymphs` and `Stars` are complete. All three pages with a positive
nymph-minus-star difference are on f72, and incomplete rows do not supply
negative controls. Decision: **{result['decision']}**. No Voynich
transcription, string score, OCR, or automated image recognition was used.
""".encode()
    install(OUT_JSON, validation_bytes)
    try:
        install(OUT_REPORT, report)
    except Exception:
        OUT_JSON.unlink(missing_ok=True)
        raise
    print(json.dumps({"status": validation["status"], "checks": checks}, sort_keys=True))


if __name__ == "__main__":
    main()
