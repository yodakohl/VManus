#!/usr/bin/env python3
"""Freeze graphematic medieval comparator corpora for GDT159.

The program does not score a Voynich target.  It extracts only visible surface
groups from public diplomatic/graphematic transcriptions and applies the exact
GDT003 token normalization and whole-unit fold balancing policy.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import io
import json
import re
import subprocess
import xml.etree.ElementTree as ET
import zipfile
from collections import defaultdict
from pathlib import Path

from prepare_gdt003_structural_fingerprint_corpora import balance_units, letter_tokens, retain_low_capacity


ROOT = Path(__file__).resolve().parent
OUT_CORPORA = ROOT / "gdt159_diplomatic_corpora.json.gz"
OUT_MANIFEST = ROOT / "gdt159_diplomatic_corpus_manifest.tsv"
OUT_PROVENANCE = ROOT / "gdt159_diplomatic_source_provenance.json"

CREMMA_COMMIT = "292525969ad98380b398e6606a9c2a36d51913ae"
HTROMANCE_COMMIT = "fe25eb9ffaa37a32333fe0e3f4093ff4dd8186db"
IFORAL_COMMIT = "9bdc5b006f634bc2e12abe043ca6e5578dfcdd83"
TRANSCRIBO_ZIP_SHA256 = "fd3b6cc4661027ec3e1311b21f3eba8fe083f26f79f20b1347888ce21f3ab71b"

CREMMA_URL = "https://github.com/HTR-United/CREMMA-Medieval-LAT"
HTROMANCE_URL = "https://github.com/HTRomance-Project/medieval-latin"
IFORAL_URL = "https://github.com/arhelio/iForal-Dataset"
TRANSCRIBO_URL = "https://doi.org/10.5281/zenodo.13757440"

MEDICAL_DIRS = ("Egerton821", "H318", "CLM13027", "Latin16195", "Phi_10a135")
SCHOLASTIC_DIRS = ("WettF0015", "BIS-193", "Mazarine915")
CREMMA_15C_DIRS = (
    "LaurentianusPluteus39.34", "PalLat373", "LaurentianusPluteus53.08",
    "LaurentianusPluteus53.09", "SBB_PK_Hdschr25", "BGO-511", "Latin8236",
)
HTROMANCE_15C_DIRS = (
    "bnf-lat-14650", "bnf-smith-lesouëf-11", "bnf-smith-lesouëf-12",
    "bnf-arsenal-ms-1046", "bnf-nal-632",
)


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git_head(path: Path) -> str:
    return subprocess.check_output(["git", "-C", str(path), "rev-parse", "HEAD"], text=True).strip()


def alto_tokens(data: bytes) -> list[str]:
    values: list[str] = []
    for _, node in ET.iterparse(io.BytesIO(data), events=("end",)):
        if node.tag.endswith("String"):
            values.extend(letter_tokens(node.get("CONTENT", ""), "LATIN"))
        node.clear()
    return values


def page_tokens(data: bytes) -> list[str]:
    values: list[str] = []
    for _, node in ET.iterparse(io.BytesIO(data), events=("end",)):
        if node.tag.endswith("Unicode"):
            values.extend(letter_tokens(node.text or "", "LATIN"))
        node.clear()
    return values


def alto_units(repo: Path, repository: str, commit: str, folders: tuple[str, ...]) -> tuple[dict[str, list[str]], list[dict[str, object]]]:
    units: dict[str, list[str]] = {}
    files: list[dict[str, object]] = []
    for folder in folders:
        base = repo / "data" / folder
        assert base.is_dir(), base
        for path in sorted(base.glob("*.xml")):
            if path.name.endswith(".chocomufin.xml") or path.name == "METS.xml":
                continue
            data = path.read_bytes()
            rel = path.relative_to(repo).as_posix()
            unit = f"{repository}:{rel}"
            tokens = alto_tokens(data)
            if tokens:
                units[unit] = tokens
            files.append({
                "repository": repository, "commit": commit, "path": rel,
                "sha256": sha_bytes(data), "bytes": len(data), "eligible_tokens": len(tokens),
            })
    return units, files


def iforal_units(repo: Path) -> tuple[dict[str, list[str]], list[dict[str, object]]]:
    units: dict[str, list[str]] = {}
    files: list[dict[str, object]] = []
    for folder in sorted((repo / "data").iterdir()):
        match = re.search(r"_(\d{4})$", folder.name)
        if not match or not 1390 <= int(match.group(1)) <= 1450:
            continue
        for path in sorted(folder.glob("*.xml")):
            if path.name == "METS.xml":
                continue
            data = path.read_bytes()
            rel = path.relative_to(repo).as_posix()
            unit = f"IFORAL:{rel}"
            tokens = page_tokens(data)
            if tokens:
                units[unit] = tokens
            files.append({
                "repository": "IFORAL", "commit": IFORAL_COMMIT, "path": rel,
                "sha256": sha_bytes(data), "bytes": len(data), "eligible_tokens": len(tokens),
            })
    return units, files


def transcribo_units(path: Path) -> tuple[dict[str, list[str]], list[dict[str, object]]]:
    assert sha(path) == TRANSCRIBO_ZIP_SHA256
    units: dict[str, list[str]] = {}
    files: list[dict[str, object]] = []
    with zipfile.ZipFile(path) as archive:
        for name in sorted(archive.namelist()):
            if "/data/Biblioteka_Baworowskich_Rps_12533_II/" not in name:
                continue
            if not name.endswith(".xml") or name.endswith("METS.xml"):
                continue
            data = archive.read(name)
            tokens = alto_tokens(data)
            if tokens:
                units[f"TRANSCRIBOQUEST:{name}"] = tokens
            files.append({
                "repository": "TRANSCRIBOQUEST2024", "record": "13757440", "path": name,
                "sha256": sha_bytes(data), "bytes": len(data), "eligible_tokens": len(tokens),
            })
    return units, files


def freeze_corpus(corpus_id: str, units: dict[str, list[str]]) -> tuple[list[dict[str, object]], dict[str, object]]:
    rows, capacity = balance_units(units, corpus_id)
    if not rows:
        rows, capacity = retain_low_capacity(units, corpus_id)
    assert rows
    return rows, capacity


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cremma-lat", type=Path, required=True)
    parser.add_argument("--htromance-lat", type=Path, required=True)
    parser.add_argument("--iforal", type=Path, required=True)
    parser.add_argument("--transcribo-zip", type=Path, required=True)
    args = parser.parse_args()
    assert git_head(args.cremma_lat) == CREMMA_COMMIT
    assert git_head(args.htromance_lat) == HTROMANCE_COMMIT
    assert git_head(args.iforal) == IFORAL_COMMIT

    med, med_files = alto_units(args.cremma_lat, "CREMMA_MEDII_AEVI", CREMMA_COMMIT, MEDICAL_DIRS)
    schol, schol_files = alto_units(args.cremma_lat, "CREMMA_MEDII_AEVI", CREMMA_COMMIT, SCHOLASTIC_DIRS)
    lat15a, lat15a_files = alto_units(args.cremma_lat, "CREMMA_MEDII_AEVI", CREMMA_COMMIT, CREMMA_15C_DIRS)
    lat15b, lat15b_files = alto_units(args.htromance_lat, "HTROMANCE_LATIN", HTROMANCE_COMMIT, HTROMANCE_15C_DIRS)
    iforal, iforal_files = iforal_units(args.iforal)
    apoth, apoth_files = transcribo_units(args.transcribo_zip)

    specs = (
        {
            "corpus_id": "LATIN_MEDICAL_GRAPHEMATIC", "language": "Medieval Latin", "family": "Italic",
            "tier": "DIPLOMATIC_MEDICAL_PERIOD_SENSITIVITY", "requested_scope": "Latin_technical_medical",
            "historical_status": "12TH_14TH_C_MEDICAL_ABBREVIATIONS_PRESERVED", "date_span": "1100-1399",
            "genre": "medical_treatises_recipes", "transcription_policy": "GRAPHEMATIC_ABBREVIATIONS_PRESERVED",
            "units": med, "files": med_files,
        },
        {
            "corpus_id": "LATIN_15C_GRAPHEMATIC", "language": "Medieval Latin", "family": "Italic",
            "tier": "DIPLOMATIC_EXACT_CENTURY", "requested_scope": "early_15c_diplomatic_priority",
            "historical_status": "15TH_C_LATIN_GRAPHEMATIC_MIXED_GENRE", "date_span": "1400-1499",
            "genre": "mixed_scholastic_literary_ecclesiastical", "transcription_policy": "GRAPHEMATIC_ABBREVIATIONS_PRESERVED",
            "units": lat15a | lat15b, "files": lat15a_files + lat15b_files,
        },
        {
            "corpus_id": "LATIN_SCHOLASTIC_GRAPHEMATIC", "language": "Medieval Latin", "family": "Italic",
            "tier": "DIPLOMATIC_SCHOLASTIC_PERIOD_SENSITIVITY", "requested_scope": "Latin_scholastic_abbreviation_practice",
            "historical_status": "13TH_14TH_C_SCHOLASTIC_ABBREVIATIONS_PRESERVED", "date_span": "1270-1399",
            "genre": "scholastic_commentary", "transcription_policy": "GRAPHEMATIC_ABBREVIATIONS_PRESERVED",
            "units": schol, "files": schol_files,
        },
        {
            "corpus_id": "IFORAL_1395_1411_GRAPHEMATIC", "language": "Medieval Latin and Portuguese", "family": "Romance_mixed",
            "tier": "DIPLOMATIC_EXACT_PERIOD_LOW_CAPACITY", "requested_scope": "different_morphology_abbreviation_practice",
            "historical_status": "1395_1411_CHARTERS_GRAPHEMATIC", "date_span": "1395-1411",
            "genre": "charters_forais", "transcription_policy": "VISIBLE_ABBREVIATION_SIGNS_PRESERVED",
            "units": iforal, "files": iforal_files,
        },
        {
            "corpus_id": "LATIN_GERMAN_APOTHECARY_LATE15", "language": "Latin and German", "family": "Italic_Germanic_mixed",
            "tier": "DIPLOMATIC_TECHNICAL_LOW_CAPACITY", "requested_scope": "Latin_technical_medical",
            "historical_status": "LATE_15TH_C_APOTHECARY_ABBREVIATIONS_PRESERVED", "date_span": "1450-1499",
            "genre": "apothecary_recipes", "transcription_policy": "GRAPHEMATIC_ABBREVIATIONS_AND_MEASURE_SIGNS_PRESERVED",
            "units": apoth, "files": apoth_files,
        },
    )

    records: list[dict[str, object]] = []
    manifest: list[dict[str, object]] = []
    provenance_corpora: dict[str, object] = {}
    for spec in specs:
        rows, capacity = freeze_corpus(str(spec["corpus_id"]), spec["units"])  # type: ignore[arg-type]
        records.extend(rows)
        manifest.append({
            **{key: spec[key] for key in (
                "corpus_id", "language", "family", "tier", "requested_scope", "historical_status",
                "date_span", "genre", "transcription_policy",
            )},
            "capacity_state": capacity["capacity_state"], "sampled_tokens": len(rows),
            "source_units": capacity["units"], "eligible_source_tokens": capacity["eligible_tokens"],
            "folds": len({str(row["fold_id"]) for row in rows}), "surface_only": 1,
            "phoneme_mapping": 0, "translation_or_lemma_used": 0,
        })
        provenance_corpora[str(spec["corpus_id"])] = {
            **capacity, "date_span": spec["date_span"], "genre": spec["genre"],
            "transcription_policy": spec["transcription_policy"], "files": spec["files"],
            "sampled_stream_sha256": hashlib.sha256(json.dumps(rows, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest(),
        }

    payload = {"schema": "GDT159_DIPLOMATIC_CORPORA_V1", "records": records}
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()
    with OUT_CORPORA.open("wb") as target:
        with gzip.GzipFile(fileobj=target, mode="wb", mtime=0) as handle:
            handle.write(raw)
    fields = [
        "corpus_id", "language", "family", "tier", "requested_scope", "historical_status",
        "date_span", "genre", "transcription_policy", "capacity_state", "sampled_tokens",
        "source_units", "eligible_source_tokens", "folds", "surface_only", "phoneme_mapping",
        "translation_or_lemma_used",
    ]
    write_tsv(OUT_MANIFEST, manifest, fields)
    provenance = {
        "schema": "GDT159_DIPLOMATIC_SOURCE_PROVENANCE_V1", "access_date": "2026-08-15",
        "repositories": {
            "CREMMA_MEDII_AEVI": {"url": CREMMA_URL, "commit": CREMMA_COMMIT, "license": "CC-BY-4.0"},
            "HTROMANCE_LATIN": {"url": HTROMANCE_URL, "commit": HTROMANCE_COMMIT, "license": "CC-BY-4.0"},
            "IFORAL": {"url": IFORAL_URL, "commit": IFORAL_COMMIT, "license": "CC-BY-4.0"},
            "TRANSCRIBOQUEST2024": {"url": TRANSCRIBO_URL, "record": "13757440", "zip_sha256": TRANSCRIBO_ZIP_SHA256, "license": "CC-BY-4.0"},
        },
        "corpora": provenance_corpora,
        "normalization": "EXACT_GDT003_LETTER_TOKENS_NFC_CASEFOLD_LATIN_SCRIPT_LENGTH_2_30",
        "voynich_target_opened": False, "f84r_opened": False,
    }
    provenance["normalized_corpora_sha256"] = sha(OUT_CORPORA)
    OUT_PROVENANCE.write_text(json.dumps(provenance, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"corpora": len(specs), "records": len(records), "manifest": manifest}, sort_keys=True))


if __name__ == "__main__":
    main()
