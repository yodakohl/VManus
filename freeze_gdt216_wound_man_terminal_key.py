#!/usr/bin/env python3
"""Freeze the external GDT216 positive control and target prediction."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


SOURCES = [
    {
        "source_id": "WELLCOME_MS49",
        "source_class": "PRIMARY_INSTITUTIONAL_CATALOGUE_AND_DIGITAL_MANUSCRIPT",
        "repository": "Wellcome Collection",
        "identifier": "MS.49",
        "folio_scope": "34r-35v",
        "date": "circa 1420-1430",
        "url": "https://wellcomecollection.org/works/af6d7sm2",
        "bibliographic_reference": "Wellcome Collection catalogue, MS.49",
        "supporting_statement": "The catalogue identifies Wound Man text and diagram on folios 34r-35v and supplies the public digital manuscript.",
    },
    {
        "source_id": "HARTNELL_2017",
        "source_class": "PEER_REVIEWED_SCHOLARLY_ARTICLE",
        "repository": "British Art Studies",
        "identifier": "issue 6, DOI 10.17658/issn.2058-5462/issue-06/jhartnell",
        "folio_scope": "Wellcome MS 49 fol.35r and comparators",
        "date": "2017",
        "url": "https://britishartstudies.ac.uk/issues/06/wound-man",
        "bibliographic_reference": "Jack Hartnell, Wording the Wound Man, British Art Studies 6 (2017)",
        "supporting_statement": "Short diagram catchphrases carry small red numbers linking to a preceding forty-four-paragraph Wundarznei; examples 14, 19 and 41 and alternative line/alphabetic/unkeyed formats are documented.",
    },
]


PAIRS = [
    {"pair_id": "WM14", "diagram_condition": "large-intestine/stomach/entrails injury", "terminal_key": "14", "prose_entry_key": "14", "prose_function": "wound closure and red-powder preparation", "exact_key_match": 1, "full_phrase_match_expected": 0, "source_id": "HARTNELL_2017"},
    {"pair_id": "WM19", "diagram_condition": "itchy or scabby condition", "terminal_key": "19", "prose_entry_key": "19", "prose_function": "three antipruritic salves", "exact_key_match": 1, "full_phrase_match_expected": 0, "source_id": "HARTNELL_2017"},
    {"pair_id": "WM41", "diagram_condition": "snakebite or poisoning", "terminal_key": "41", "prose_entry_key": "41", "prose_function": "two bite remedies", "exact_key_match": 1, "full_phrase_match_expected": 0, "source_id": "HARTNELL_2017"},
]


def main() -> None:
    manifest = ROOT / "gdt216_wound_man_source_manifest.tsv"
    pairs = ROOT / "gdt216_positive_control_pairs.tsv"
    write_tsv(manifest, SOURCES)
    write_tsv(pairs, PAIRS)
    result = {
        "experiment": "GDT216_WOUND_MAN_TERMINAL_KEY_SOURCE_FREEZE",
        "status": "EXTERNAL_TERMINAL_KEY_MECHANISM_FROZEN_BEFORE_VOYNICH_SCORE",
        "mechanism": "DIAGRAM_DESCRIPTIVE_PHRASE_PLUS_TERMINAL_KEY_TO_PROSE_INITIAL_KEY",
        "positive_control": {
            "pairs": 3,
            "exact_terminal_to_initial_matches": 3,
            "full_phrase_exact_matches_expected": 0,
        },
        "target_prediction": {
            "pages": 23,
            "physical_folios": 11,
            "representations": [
                "FINAL_GROUP_EXACT_TO_INITIAL_GROUP_EXACT",
                "FINAL_FAMILY_1_TO_INITIAL_FAMILY_1",
                "FINAL_FAMILY_2_TO_INITIAL_FAMILY_2",
            ],
            "null_worlds": 432,
            "max_family": 3,
            "score_run": False,
        },
        "f84": {"accessed": False, "input": False, "output": False},
        "claim_ceiling": "External mechanism and frozen formal prediction only; no Voynich key, number, word, language, plaintext, meaning, or translation.",
    }
    outputs = [manifest.name, pairs.name]
    documents = ["GDT216_WOUND_MAN_TERMINAL_KEY_SOURCE_AUDIT.md", "GDT216_TERMINAL_KEY_PREDICTION_METHOD.md"]
    result["outputs_sha256"] = {name: sha(ROOT / name) for name in outputs}
    result["documents_sha256"] = {name: sha(ROOT / name) for name in documents}
    result["implementation_sha256"] = sha(Path(__file__))
    result["validator_sha256"] = sha(ROOT / "validate_gdt216_wound_man_terminal_key_freeze.py")
    canonical = json.dumps(result, sort_keys=True, separators=(",", ":"))
    result["content_sha256"] = hashlib.sha256(canonical.encode()).hexdigest()
    (ROOT / "gdt216_prediction_freeze.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
