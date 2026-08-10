#!/usr/bin/env python3
"""Independent nonimporting validation for the TPQ001 public-source audit."""

from __future__ import annotations

import csv
import hashlib
import html
import json
import re
import subprocess
import tempfile
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RESULT = ROOT / "experiments/semantic_assumptions/results/f67_f70_theorica_source_audit.json"
REPORT = ROOT / "experiments/semantic_assumptions/results/f67_f70_theorica_source_audit.md"
VALIDATION = ROOT / "experiments/semantic_assumptions/results/f67_f70_theorica_source_validation.json"
LOCAL = ROOT / "experiments/semantic_assumptions/results/public_voynich_nu_page_annotations_v2.tsv"

SOURCES = [
    ("gotha_catalog", "https://bilder.manuscripta-mediaevalia.de/hs//projekt-Gotha-pdfs/Chart_A_472.pdf"),
    ("pantin_article", "https://link.springer.com/content/pdf/10.1007/978-3-031-11317-8_2.pdf"),
    ("pelling_claim", "https://ciphermysteries.com/wp-json/wp/v2/posts/12439?_fields=id,date,modified,link,content"),
    ("voynich_q09", "https://www.voynich.nu/q09/index.html"),
    ("voynich_q10", "https://www.voynich.nu/q10/index.html"),
]


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def retrieve(entry: tuple[str, str]) -> tuple[str, str, bytes]:
    name, url = entry
    request = urllib.request.Request(url, headers={"User-Agent": "VManus-TPQ001-validator/1.0"})
    with urllib.request.urlopen(request, timeout=60) as response:
        if response.status != 200:
            raise AssertionError((name, response.status))
        return name, url, response.read()


def visible_html(data: bytes) -> str:
    text = data.decode("utf-8", "replace")
    text = re.sub(r"<(script|style)\b.*?</\1>", " ", text, flags=re.I | re.S)
    return " ".join(html.unescape(re.sub(r"<[^>]*>", " ", text)).split())


def catalog_text(data: bytes) -> str:
    with tempfile.TemporaryDirectory(prefix="tpq001_validator_") as folder:
        pdf = Path(folder, "input.pdf")
        txt = Path(folder, "output.txt")
        pdf.write_bytes(data)
        subprocess.check_call(
            ["pdftotext", "-layout", str(pdf), str(txt)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return " ".join(txt.read_text("utf-8").split())


def main() -> None:
    result = json.loads(RESULT.read_text("utf-8"))
    checks = 0
    with ThreadPoolExecutor(max_workers=5) as executor:
        fetched = {name: (url, data) for name, url, data in executor.map(retrieve, SOURCES)}

    for name, (url, data) in fetched.items():
        record = result["sources"][name]
        assert record == {"url": url, "bytes": len(data), "sha256": digest(data)}
        checks += 3

    pelling_json = json.loads(fetched["pelling_claim"][1].decode("utf-8"))
    pelling = visible_html(pelling_json["content"]["rendered"].encode("utf-8"))
    assert "seven full-page circular diagrams, starting with the Sun and Moon" in pelling
    assert "set of full-size circular diagrams for those seven astrological planets" in pelling
    checks += 2

    gotha = catalog_text(fetched["gotha_catalog"][1])
    titles = result["gotha"]["consecutive_f3r_f8r_titles"]
    assert len(titles) == 7 and all(title in gotha for title in titles)
    assert result["gotha"]["total_disk_diagrams"] == 17
    assert "17 scheibenförmige Diagramme" in gotha
    assert result["gotha"]["catalogue_date"] == "circa 1460"
    assert "nordbairisches Sprachgebiet • um 1460" in gotha
    checks += 6

    classical = {"SUN", "MOON", "MERCURY", "VENUS", "MARS", "JUPITER", "SATURN"}
    present = set(result["gotha"]["individual_classical_planets_in_sequence"])
    absent = set(result["gotha"]["missing_individual_classical_planets"])
    assert present == {"SATURN", "JUPITER", "MARS", "VENUS"}
    assert absent == classical - present
    assert len(result["gotha"]["non_individual_planet_titles"]) == 3
    checks += 3

    pantin = catalog_text(fetched["pantin_article"][1])
    assert "one diagram for the Sun, two for the Moon" in pantin
    assert "one for the superior planets, and one for Venus and Mercury" in pantin
    assert result["canonical_theorica"]["one_to_one_seven_planet_layout"] is False
    checks += 3

    q09 = visible_html(fetched["voynich_q09"][1])
    q10 = visible_html(fetched["voynich_q10"][1])
    assert "sun face in the centre" in q09.lower()
    assert "sun with a face in the centre" in q10.lower()
    checks += 2

    local_data = LOCAL.read_bytes()
    local_record = result["sources"]["local_public_annotation_v2"]
    assert local_record["bytes"] == len(local_data)
    assert local_record["sha256"] == digest(local_data)
    rows = list(csv.DictReader(local_data.decode("utf-8").splitlines(), delimiter="\t"))
    rows = [r for r in rows if re.fullmatch(r"f(?:6[7-9]|7[0-3]).*", r["page"])]
    by_page = {r["page"]: r for r in rows}
    assert len(rows) == result["voynich_public_catalogue"]["f67_f73_page_panels"] == 26
    assert "sun face in the centre" in by_page["f68v1"]["illustrations"].lower()
    assert "sun with a face in the centre" in by_page["f70r2"]["illustrations"].lower()
    assert result["voynich_public_catalogue"]["apparent_sun_pages"] == ["f68v1", "f70r2"]
    checks += 6

    expected_gates = {
        "published_hypothesis_identified": True,
        "gotha_sequence_is_seven_individual_classical_planets": False,
        "canonical_theorica_is_one_diagram_per_classical_planet": False,
        "voynich_apparent_sun_graphic_is_unique_in_f68v1_f70r2": False,
        "gotha_witness_is_not_later_than_1404_1438_parchment_interval": False,
        "exact_one_to_one_label_donor_available": False,
    }
    assert result["gates"] == expected_gates
    assert result["decision"] == "STOP_NO_ONE_TO_ONE_THEORICA_LABEL_DONOR"
    assert "no Voynich word is translated" in result["claim_ceiling"]
    assert "one-to-one names" in result["reopen_only_with"]
    checks += 4

    report = REPORT.read_text("utf-8")
    for required in [
        "STOP_NO_ONE_TO_ONE_THEORICA_LABEL_DONOR",
        "Circulus orbis signorum",
        "Circulus augum planetarum",
        "f68v1",
        "f70r2",
        "does not show that the Voynich diagrams are non-planetary",
    ]:
        assert required in report
        checks += 1

    validation = json.loads(VALIDATION.read_text("utf-8"))
    assert validation == {
        "audit_id": "TPQ001",
        "checks": checks,
        "decision": result["decision"],
        "discrepancies": 0,
        "method": "INDEPENDENT_NONIMPORTING_PUBLIC_TEXT_RECONSTRUCTION_NO_OCR_NO_IMAGE_MODEL",
        "status": "PASS",
    }
    print(f"TPQ001 independent validation PASS ({checks} checks)")


if __name__ == "__main__":
    main()
