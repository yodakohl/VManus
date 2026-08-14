#!/usr/bin/env python3
"""Freeze the target-blind ASJP v21 core-40 phonotactic panel for Q20P001."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUT_CORPUS = ROOT / "q20p001_asjp_v21_core40.tsv"
OUT_MANIFEST = ROOT / "q20p001_language_manifest.tsv"
OUT_PROVENANCE = ROOT / "q20p001_source_provenance.json"
ASJP_COMMIT = "012795349540ba0dabfdcf2be16f2e77622f62d6"
LANGUAGES = {
    "GEORGIAN": "KARTVELIAN_TARGET",
    "MINGRELIAN": "KARTVELIAN_TARGET",
    "LAZ": "KARTVELIAN_TARGET",
    "SVAN": "KARTVELIAN_TARGET",
    "ARMENIAN": "UNRELATED_CONTROL",
    "CHECHEN": "UNRELATED_CONTROL",
    "AVAR": "UNRELATED_CONTROL",
    "BASQUE": "UNRELATED_CONTROL",
    "TURKISH": "UNRELATED_CONTROL",
    "GREEK": "UNRELATED_CONTROL",
    "ARABIC_QURANIC": "UNRELATED_CONTROL",
    "FINNISH": "UNRELATED_CONTROL",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("asjp_root", type=Path, help="Checkout of lexibank/asjp at tag v21")
    args = parser.parse_args()
    root = args.asjp_root.resolve()
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    if commit != ASJP_COMMIT:
        raise RuntimeError(f"expected ASJP v21 commit {ASJP_COMMIT}, got {commit}")
    cldf = root / "cldf"

    with (cldf / "parameters.csv").open(encoding="utf-8", newline="") as handle:
        parameters = {row["ID"]: row for row in csv.DictReader(handle) if row["Name"].startswith("*")}
    if len(parameters) != 40:
        raise RuntimeError(f"expected 40 ASJP core concepts, got {len(parameters)}")
    with (cldf / "languages.csv").open(encoding="utf-8", newline="") as handle:
        language_rows = {row["ID"]: row for row in csv.DictReader(handle)}
    if not set(LANGUAGES) <= set(language_rows):
        raise RuntimeError("one or more frozen language IDs are missing")

    candidates: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    with (cldf / "forms.csv").open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            key = (row["Language_ID"], row["Parameter_ID"])
            if row["Language_ID"] in LANGUAGES and row["Parameter_ID"] in parameters and row["Segments"].strip():
                candidates[key].append(row)

    corpus_rows: list[dict[str, object]] = []
    manifest_rows: list[dict[str, object]] = []
    for language_id, panel in LANGUAGES.items():
        selected = []
        for parameter_id in sorted(parameters, key=lambda value: int(value)):
            available = sorted(candidates[language_id, parameter_id], key=lambda row: row["ID"])
            if not available:
                continue
            row = available[0]
            segments = [segment for segment in row["Segments"].split() if segment != "+"]
            if not segments:
                continue
            selected.append((parameter_id, row, segments))
            corpus_rows.append(
                {
                    "panel": panel,
                    "language_id": language_id,
                    "glottocode": language_rows[language_id]["Glottocode"],
                    "family": language_rows[language_id]["Family"],
                    "parameter_id": parameter_id,
                    "concepticon_gloss": parameters[parameter_id]["Concepticon_Gloss"],
                    "asjp_form_id": row["ID"],
                    "phoneme_segments": " ".join(segments),
                    "source_record_count_for_concept": len(available),
                    "loan_flag_retained_not_selected_on": row["Loan"],
                }
            )
        inventory = sorted({segment for _, _, segments in selected for segment in segments})
        manifest_rows.append(
            {
                "panel": panel,
                "language_id": language_id,
                "name": language_rows[language_id]["Glottolog_Name"],
                "glottocode": language_rows[language_id]["Glottocode"],
                "iso639p3": language_rows[language_id]["ISO639P3code"],
                "family": language_rows[language_id]["Family"],
                "core_concepts_present": len(selected),
                "phoneme_inventory_size": len(inventory),
                "phoneme_inventory": " ".join(inventory),
                "selection_rule": "LOWEST_ASJP_FORM_ID_PER_AVAILABLE_STARRED_CORE_CONCEPT;PLUS_BOUNDARY_REMOVED",
            }
        )

    write_tsv(
        OUT_CORPUS,
        corpus_rows,
        [
            "panel", "language_id", "glottocode", "family", "parameter_id", "concepticon_gloss",
            "asjp_form_id", "phoneme_segments", "source_record_count_for_concept", "loan_flag_retained_not_selected_on",
        ],
    )
    write_tsv(
        OUT_MANIFEST,
        manifest_rows,
        [
            "panel", "language_id", "name", "glottocode", "iso639p3", "family", "core_concepts_present",
            "phoneme_inventory_size", "phoneme_inventory", "selection_rule",
        ],
    )
    provenance = {
        "schema": "Q20P001_ASJP_V21_SOURCE_PROVENANCE_V1",
        "status": "FROZEN_BEFORE_Q20_TARGET_SCORING",
        "upstream": {
            "title": "ASJP Database v21",
            "editors": "Wichmann, Soren; Holman, Eric W.; Brown, Cecil H.; Dryer, Matthew S.; Ran, Qibin (eds.)",
            "year": 2025,
            "repository": "https://github.com/lexibank/asjp",
            "tag": "v21",
            "commit": ASJP_COMMIT,
            "license": "CC BY 4.0",
            "citation": "Wichmann et al. (eds.). 2025. The ASJP Database (version 21).",
            "cldf_forms_sha256": sha256(cldf / "forms.csv"),
            "cldf_languages_sha256": sha256(cldf / "languages.csv"),
            "cldf_parameters_sha256": sha256(cldf / "parameters.csv"),
        },
        "selection": {
            "language_ids": list(LANGUAGES),
            "target_panel": [key for key, value in LANGUAGES.items() if value == "KARTVELIAN_TARGET"],
            "control_panel": [key for key, value in LANGUAGES.items() if value == "UNRELATED_CONTROL"],
            "concepts": "ASJP 40 starred core concepts",
            "one_form_per_concept": "lowest stable ASJP FormTable ID",
            "plus_sign_handling": "ASJP internal boundary marker removed; not treated as a phoneme",
            "loan_handling": "retained; loan status did not select records",
        },
        "outputs": {
            OUT_CORPUS.name: sha256(OUT_CORPUS),
            OUT_MANIFEST.name: sha256(OUT_MANIFEST),
        },
        "claim_ceiling": "Uniform modern/basic-vocabulary phonotactic comparator only; no historical identity, word matching, plaintext, meaning, or translation.",
    }
    OUT_PROVENANCE.write_text(json.dumps(provenance, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({row["language_id"]: row["core_concepts_present"] for row in manifest_rows}, sort_keys=True))


if __name__ == "__main__":
    main()
