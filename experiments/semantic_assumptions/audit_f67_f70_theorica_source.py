#!/usr/bin/env python3
"""Reconstruct the TPQ001 public-source audit without OCR or image analysis."""

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
LOCAL = ROOT / "experiments/semantic_assumptions/results/public_voynich_nu_page_annotations_v2.tsv"

URLS = {
    "pelling_claim": "https://ciphermysteries.com/wp-json/wp/v2/posts/12439?_fields=id,date,modified,link,content",
    "gotha_catalog": "https://bilder.manuscripta-mediaevalia.de/hs//projekt-Gotha-pdfs/Chart_A_472.pdf",
    "pantin_article": "https://link.springer.com/content/pdf/10.1007/978-3-031-11317-8_2.pdf",
    "voynich_q09": "https://www.voynich.nu/q09/index.html",
    "voynich_q10": "https://www.voynich.nu/q10/index.html",
}

GOTHA_SEQUENCE = [
    "Circulus orbis signorum",
    "Circulus anni",
    "Circulus Saturni",
    "Circulus Jouis",
    "Circulus Martis",
    "Circulus Veneris",
    "Circulus augum planetarum",
]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fetch(item: tuple[str, str]) -> tuple[str, bytes]:
    key, url = item
    req = urllib.request.Request(url, headers={"User-Agent": "VManus-TPQ001/1.0"})
    with urllib.request.urlopen(req, timeout=60) as response:
        assert response.status == 200
        return key, response.read()


def html_text(data: bytes) -> str:
    raw = data.decode("utf-8", errors="replace")
    raw = re.sub(r"<script\b.*?</script>", " ", raw, flags=re.I | re.S)
    raw = re.sub(r"<style\b.*?</style>", " ", raw, flags=re.I | re.S)
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", raw)).split())


def pdf_text(data: bytes) -> str:
    with tempfile.TemporaryDirectory(prefix="tpq001_") as directory:
        source = Path(directory) / "catalog.pdf"
        output = Path(directory) / "catalog.txt"
        source.write_bytes(data)
        subprocess.run(
            ["pdftotext", "-layout", str(source), str(output)],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return " ".join(output.read_text(encoding="utf-8").split())


def local_facts() -> tuple[bytes, dict[str, str], int]:
    data = LOCAL.read_bytes()
    rows = list(csv.DictReader(data.decode("utf-8").splitlines(), delimiter="\t"))
    scope = [row for row in rows if re.fullmatch(r"f(?:6[7-9]|7[0-3]).*", row["page"])]
    descriptions = {row["page"]: row["illustrations"] for row in scope}
    assert len(scope) == 26
    assert "sun face in the centre" in descriptions["f68v1"].lower()
    assert "sun with a face in the centre" in descriptions["f70r2"].lower()
    return data, descriptions, len(scope)


def reconstruct() -> dict:
    with ThreadPoolExecutor(max_workers=5) as pool:
        sources = dict(pool.map(fetch, URLS.items()))

    pelling_payload = json.loads(sources["pelling_claim"].decode("utf-8"))
    pelling = html_text(pelling_payload["content"]["rendered"].encode("utf-8"))
    gotha = pdf_text(sources["gotha_catalog"])
    pantin = pdf_text(sources["pantin_article"])
    q09 = html_text(sources["voynich_q09"])
    q10 = html_text(sources["voynich_q10"])
    local_bytes, descriptions, scope_count = local_facts()

    assert "seven full-page circular diagrams, starting with the Sun and Moon" in pelling
    assert "set of full-size circular diagrams for those seven astrological planets" in pelling
    assert all(title in gotha for title in GOTHA_SEQUENCE)
    assert "nordbairisches Sprachgebiet • um 1460" in gotha
    assert "17 scheibenförmige Diagramme" in gotha
    assert "one diagram for the Sun, two for the Moon" in pantin
    assert "one for the superior planets, and one for Venus and Mercury" in pantin
    assert "sun face in the centre" in q09.lower()
    assert "sun with a face in the centre" in q10.lower()

    named = ["SATURN", "JUPITER", "MARS", "VENUS"]
    missing = ["SUN", "MOON", "MERCURY"]
    gates = {
        "published_hypothesis_identified": True,
        "gotha_sequence_is_seven_individual_classical_planets": False,
        "canonical_theorica_is_one_diagram_per_classical_planet": False,
        "voynich_apparent_sun_graphic_is_unique_in_f68v1_f70r2": False,
        "gotha_witness_is_not_later_than_1404_1438_parchment_interval": False,
        "exact_one_to_one_label_donor_available": False,
    }
    result = {
        "audit_id": "TPQ001",
        "date": "2026-08-10",
        "method": "PUBLIC_HUMAN_TEXT_ONLY_NO_OCR_NO_IMAGE_MODEL_NO_VOYNICH_STRING_SCORE",
        "sources": {
            key: {"url": URLS[key], "bytes": len(value), "sha256": sha(value)}
            for key, value in sorted(sources.items())
        }
        | {
            "local_public_annotation_v2": {
                "path": "experiments/semantic_assumptions/results/public_voynich_nu_page_annotations_v2.tsv",
                "bytes": len(local_bytes),
                "sha256": sha(local_bytes),
            }
        },
        "gotha": {
            "catalogue_date": "circa 1460",
            "total_disk_diagrams": 17,
            "consecutive_f3r_f8r_titles": GOTHA_SEQUENCE,
            "individual_classical_planets_in_sequence": named,
            "missing_individual_classical_planets": missing,
            "non_individual_planet_titles": [
                "Circulus orbis signorum",
                "Circulus anni",
                "Circulus augum planetarum",
            ],
        },
        "canonical_theorica": {
            "diagram_functions": [
                "Sun",
                "Moon",
                "Moon nodes",
                "three superior planets grouped",
                "Venus and Mercury grouped",
            ],
            "one_to_one_seven_planet_layout": False,
        },
        "voynich_public_catalogue": {
            "f67_f73_page_panels": scope_count,
            "apparent_sun_pages": ["f68v1", "f70r2"],
            "f68v1_description": descriptions["f68v1"],
            "f70r2_description": descriptions["f70r2"],
            "warning": "human apparent-object descriptions are not authorial identities",
        },
        "gates": gates,
        "decision": "STOP_NO_ONE_TO_ONE_THEORICA_LABEL_DONOR",
        "claim_ceiling": (
            "Gotha Chart. A 472 and the canonical Theorica tradition do not provide "
            "an exact seven-slot external label key for the Voynich circle block; "
            "planetary or astronomical roles remain possible and no Voynich word is translated."
        ),
        "reopen_only_with": (
            "a human-catalogued contemporary-or-earlier seven-unit witness with explicit "
            "one-to-one names and a non-post-hoc complete-block order or topology correspondence"
        ),
    }
    return result


def main() -> None:
    stored = json.loads(RESULT.read_text(encoding="utf-8"))
    rebuilt = reconstruct()
    assert rebuilt == stored
    print("TPQ001 producer reconstruction PASS")


if __name__ == "__main__":
    main()
