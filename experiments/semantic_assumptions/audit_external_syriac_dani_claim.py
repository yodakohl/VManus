#!/usr/bin/env python3
"""Audit the public DANI Syriac-pharmaceutical Voynich claim."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import tempfile
import unicodedata
import urllib.request
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
OUT_JSON = RESULTS / "external_syriac_dani_claim_audit.json"
OUT_REPORT = RESULTS / "external_syriac_dani_claim_audit.md"

SOURCES = {
    "zenodo_metadata": {
        "url": "https://zenodo.org/api/records/19583305",
        "sha256": "780301fd3c4b2c3c328c1f69a1eab65d0b0600f2d491ea9578f81699d36ddfa7",
    },
    "superseded_metadata": {
        "url": "https://zenodo.org/api/records/19583306",
        "sha256": "6a350f06393f473dd54afdf1661dac8ce5e194108a462760c0a40e0515d4649c",
    },
    "paper": {
        "url": (
            "https://zenodo.org/api/records/19609475/files/"
            "A_Syriac_Pharmaceutical_Dispensatory_Encoded_in_the_Voynich_Manuscript.pdf/content"
        ),
        "sha256": "79627e490b535df5e57328a7bed22b2ae562a3b2cf56e39ca0650159b00d2208",
    },
    "pipeline": {
        "url": "https://zenodo.org/api/records/19609475/files/pipeline_v31_1.py/content",
        "sha256": "079b6de7b8d2082303a0789fb3904105aecaa491e35600a557090e7981255d6f",
    },
    "lexicon": {
        "url": (
            "https://zenodo.org/api/records/19609475/files/"
            "lexicon_v31_session31_final.json/content"
        ),
        "sha256": "348992fa2bf555f1454a5a5485dd1ca9842acc143059f257f2fcdcf237821589",
    },
}


def download(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "VManus-source-audit/1"})
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read()


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def pdf_text(data: bytes) -> str:
    with tempfile.TemporaryDirectory(prefix="external-source-audit-") as directory:
        source = Path(directory) / "source.pdf"
        output = Path(directory) / "source.txt"
        source.write_bytes(data)
        process = subprocess.run(
            ["pdftotext", "-layout", str(source), str(output)],
            check=False, capture_output=True, text=True, timeout=60,
        )
        if process.returncode != 0:
            raise RuntimeError(f"pdftotext failed: {process.stderr.strip()}")
        return output.read_text(encoding="utf-8")


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=True, allow_nan=False) + "\n").encode("utf-8")


def stable_metadata_projection(metadata: dict[str, object]) -> dict[str, object]:
    """Drop live Zenodo statistics while binding immutable version metadata."""
    meta = metadata["metadata"]
    return {
        "id": metadata["id"],
        "conceptrecid": metadata["conceptrecid"],
        "revision": metadata["revision"],
        "doi": metadata["doi"],
        "created": metadata["created"],
        "updated": metadata["updated"],
        "metadata": {
            "title": meta["title"],
            "publication_date": meta["publication_date"],
            "description": meta["description"],
        },
        "files": [
            {
                "key": item["key"],
                "size": item["size"],
                "checksum": item["checksum"],
                "url": item["links"]["self"],
            }
            for item in metadata["files"]
        ],
    }


def build() -> dict[str, object]:
    bodies = {name: download(item["url"]) for name, item in SOURCES.items()}
    metadata = json.loads(bodies["zenodo_metadata"])
    superseded_metadata = json.loads(bodies["superseded_metadata"])
    metadata_projection = stable_metadata_projection(metadata)
    superseded_projection = stable_metadata_projection(superseded_metadata)
    hashes = {
        "zenodo_metadata": sha(canonical(metadata_projection)),
        "superseded_metadata": sha(canonical(superseded_projection)),
        **{
            name: sha(body) for name, body in bodies.items()
            if name not in {"zenodo_metadata", "superseded_metadata"}
        },
    }
    if any(hashes[name] != item["sha256"] for name, item in SOURCES.items()):
        raise ValueError("public source drift; version the audit rather than silently update")

    paper = pdf_text(bodies["paper"])
    flat = re.sub(r"\s+", " ", unicodedata.normalize("NFKC", paper))
    pipeline = bodies["pipeline"].decode("utf-8")
    lexicon = json.loads(bodies["lexicon"])
    files = metadata.get("files", [])
    if (metadata.get("id") != 19_609_475 or metadata.get("revision") != 4 or
            metadata.get("conceptrecid") != "19583305" or len(files) != 3):
        raise ValueError("Zenodo record or file inventory drift")
    if (superseded_metadata.get("id") != 19_583_306 or
            len(superseded_metadata.get("files", [])) != 1 or
            not superseded_metadata["files"][0]["key"].endswith(".pdf")):
        raise ValueError("superseded Zenodo record drift")
    expected_files = {
        "pipeline_v31_1.py": 11_613,
        "lexicon_v31_session31_final.json": 214_931,
        "A_Syriac_Pharmaceutical_Dispensatory_Encoded_in_the_Voynich_Manuscript.pdf": 88_289,
    }
    if {item.get("key"): item.get("size") for item in files} != expected_files:
        raise ValueError("Zenodo file inventory drift")

    published_claims = {
        "mapping_table_present": (
            "2.2 Character Mapping" in paper and
            all(fragment in flat for fragment in (
                "k k (kaph)", "ch k (kaph)", "q w (waw)",
                "a, o, e, i ∅ vowels stripped",
            ))
        ),
        "corpus_35259_tokens_225_folios": (
            "35,259 tokens across 225 folios" in flat
        ),
        "paper_coverage_86_9_percent": (
            "30,632 of 35,259 tokens (86.9%)" in flat
        ),
        "permutation_claim_500_z_4_86": (
            "Against 500 random permutations: true mapping 86.9%, chance mean 44.7%, z = 4.86" in flat
        ),
        "ai_plant_identification_111_folios": (
            "An independent AI instance" in flat and
            "visually identified plants in 111 herbal folios" in flat
        ),
        "fourteen_visual_correspondences_claimed": (
            "14 folios showed statistically significant concordance" in flat
        ),
        "connected_prose_absent": (
            "No connected Syriac prose" in flat and
            "no paragraph has been read as coherent connected Syriac prose by a specialist" in flat
        ),
        "word_accuracy_claim_10_to_15_percent": (
            "Word-level decode accuracy 10–15%" in flat
        ),
    }
    if not all(published_claims.values()):
        raise ValueError("paper claim text drift")

    all_entries = [entry for values in lexicon.values() for entry in values]
    released_output_alphabet = set("kdrslnwymgšṭpṣ")
    unreachable_keys = [key for key in lexicon if not set(key) <= released_output_alphabet]
    source_missing_entries = [entry for entry in all_entries if not entry.get("source")]
    function_keys = {
        key for key, values in lexicon.items()
        if any(entry.get("domain") == "function" for entry in values)
    }
    nonfunction_keys = {
        key for key, values in lexicon.items()
        if any(entry.get("domain") != "function" for entry in values)
    }
    unknown_gloss_keys = {
        key for key, values in lexicon.items()
        if any("unknown" in (entry.get("meaning") or "").lower() for entry in values)
    }

    method_observations = {
        "latest_concept_version_resolved": (
            metadata["conceptrecid"] == "19583305" and metadata["revision"] == 4
        ),
        "older_one_pdf_record_is_superseded": (
            superseded_metadata["id"] == 19_583_306 and metadata["id"] == 19_609_475
        ),
        "pipeline_and_lexicon_now_published": (
            "pipeline_v31_1.py" in expected_files and
            "lexicon_v31_session31_final.json" in expected_files
        ),
        "exact_input_corpus_not_published": (
            "lsi_all.txt" in pipeline and not any(item.get("key") == "lsi_all.txt" for item in files)
        ),
        "released_pipeline_has_only_coverage_functions": (
            all(f"def {name}" in pipeline for name in (
                "eva_to_skeleton", "strip_affixes", "classify_folio", "parse_ivtff", "run_pipeline",
            )) and "import random" not in pipeline and "def permutation" not in pipeline
        ),
        "permutation_language_visual_phrase_code_absent": all(
            fragment not in pipeline for fragment in (
                "fisher_exact", "hebrew", "arabic", "plant_matches", "recipe_templates",
            )
        ),
        "paper_says_lexicon_is_supplementary": "lexicon_v31_session31" in paper,
        "paper_says_pipeline_is_supplementary": "pipeline_v31.py" in paper,
        "mapping_and_evaluation_use_same_corpus": (
            "The study uses the ZL (Zandbergen-Landini) merged IVTFF transcription" in flat and
            "Each EVA character is mapped to a Syriac consonant" in flat and
            "Coverage is tested against 500 random permutations" in flat
        ),
        "no_train_cal_test_or_held_design_disclosed": not any(
            phrase in paper.lower()
            for phrase in ("training set", "validation set", "test set", "held-out", "holdout")
        ),
        "null_randomizes_only_ten_core_characters": (
            "reassigns the 10 core EVA consonant characters to a random permutation of the 10 Syriac consonants"
            in flat
        ),
        "pipeline_has_additional_unrandomized_choices": all(
            phrase in flat for phrase in (
                "strip annotation markers", "attempt gallows prefix stripping",
                "attempt standard prefix stripping", "attempt suffix stripping (-yn)",
            )
        ),
        "chance_coverage_44_7_percent": "chance mean 44.7%" in flat,
        "metadata_and_pdf_null_numbers_conflict": (
            "z-score 3.83 (14.9 percentage points above baseline)"
            in metadata["metadata"]["description"] and
            "chance mean 44.7%, z = 4.86" in flat
        ),
        "paper_language_coverage_internally_changes": (
            "30,632 of 35,259 tokens (86.9%)" in flat and "Syriac 85.1% 3.8" in flat
        ),
        "exact_empirical_p_formula_not_disclosed": not any(
            phrase in paper.lower() for phrase in ("plus-one", "1/501", "empirical p-value")
        ),
        "lexicon_has_1389_keys_1441_entries": len(lexicon) == 1_389 and len(all_entries) == 1_441,
        "lexicon_entries_without_source_field_1334": len(source_missing_entries) == 1_334,
        "lexicon_keys_unreachable_by_released_mapping_570": len(unreachable_keys) == 570,
        "deposited_function_domains_conflict_with_1375_no_function_count": (
            len(function_keys) == 146 and len(lexicon) - len(function_keys) == 1_243 and
            len(nonfunction_keys) == 1_251 and "Pharma content only (no function words) 1,375" in flat
        ),
        "lexicon_unknown_gloss_keys_16": len(unknown_gloss_keys) == 16,
    }
    if not all(method_observations.values()):
        raise ValueError("method observation drift")

    admission_gates = {
        "released_coverage_pipeline_and_lexicon_available": True,
        "exact_corpus_and_headline_statistics_reconstructable": False,
        "mapping_selection_separated_from_held_evaluation": False,
        "null_covers_mapping_lexicon_filter_and_stripping_choices": False,
        "type_level_or_token_concentration_robustness_reported": False,
        "visual_evidence_complies_with_no_ai_vision_policy": False,
        "connected_specialist_reading_available": False,
        "independent_reproduction_available": False,
    }
    return {
        "experiment": "EXTERNAL_SYRIAC_DANI_CLAIM_AUDIT",
        "status": "HOLD_AS_LANGUAGE_OR_TRANSLATION_EVIDENCE_UNREPRODUCIBLE_NONHELD_AND_VISUAL_COMPONENT_EXCLUDED",
        "decision": "DO_NOT_IMPORT_SYRIAC_MAPPING_WORDS_PHRASES_OR_PLAINTEXT",
        "sources": {
            "zenodo_metadata": {
                "url": SOURCES["zenodo_metadata"]["url"],
                "sha256": hashes["zenodo_metadata"],
                "hash_scope": "stable_projection_excluding_live_statistics",
                "projection_bytes": len(canonical(metadata_projection)),
            },
            "superseded_metadata": {
                "url": SOURCES["superseded_metadata"]["url"],
                "sha256": hashes["superseded_metadata"],
                "hash_scope": "stable_projection_excluding_live_statistics",
                "projection_bytes": len(canonical(superseded_projection)),
            },
            **{
                name: {"url": item["url"], "sha256": hashes[name], "bytes": len(bodies[name])}
                for name, item in SOURCES.items()
                if name not in {"zenodo_metadata", "superseded_metadata"}
            },
        },
        "zenodo": {
            "concept_record_id": int(metadata["conceptrecid"]),
            "record_id": metadata["id"],
            "revision": metadata["revision"],
            "doi": metadata["doi"],
            "title": metadata["metadata"]["title"],
            "publication_date": metadata["metadata"]["publication_date"],
            "published_files": len(files),
            "pipeline_files": 1,
            "lexicon_files": 1,
            "corpus_files": 0,
        },
        "lexicon_audit": {
            "keys": len(lexicon),
            "entries": len(all_entries),
            "entries_without_source_field": len(source_missing_entries),
            "unreachable_keys_under_released_mapping_alphabet": len(unreachable_keys),
            "function_domain_keys": len(function_keys),
            "keys_with_any_nonfunction_sense": len(nonfunction_keys),
            "unknown_gloss_keys": len(unknown_gloss_keys),
        },
        "published_claims": published_claims,
        "method_observations": method_observations,
        "admission_gates": admission_gates,
        "claim_ceiling": (
            "This holds the public DANI deposit outside the active evidence base. It does not "
            "prove that Syriac, Aramaic, Semitic language, or pharmaceutical content is false; "
            "it supplies no admitted Voynich word, phrase, plaintext, or translation."
        ),
    }


def report(result: dict[str, object]) -> str:
    return (
        "# External Syriac DANI claim audit\n\n"
        f"Status: **{result['status']}**.\n\n"
        "This is more testable than a prose-only translation claim: the latest Zenodo "
        "version publishes an EVA-to-consonant table, a 1,389-key JSON lexicon, and a "
        "coverage pipeline. The original one-PDF record was superseded the next day and "
        "is not used for this conclusion.\n\n"
        "The deposit still omits its exact `lsi_all.txt` input. The released Python only "
        "implements parsing, skeleton conversion, affix stripping, and coverage; it does "
        "not implement or preserve the 500 permutations, comparison lexicons, plant "
        "tests, language comparisons, scores, or random seeds. The current metadata still reports "
        "z=3.83 and a 14.9-point gap while its PDF reports z=4.86 and a 42.2-point gap.\n\n"
        "The reported 86.9% result is not held out. The mapping, domain lexicon, token "
        "filter, vowel deletion, gallows handling, prefix/suffix stripping, and downstream "
        "word choices are evaluated on the same manuscript. Its null permutes only ten "
        "core consonant assignments; it does not reproduce the larger search over those "
        "other choices. The headline is frequency-weighted token coverage, while no "
        "type-level or token-concentration robustness and no exact finite-permutation "
        "p-value formula are supplied.\n\n"
        "The deposited lexicon itself has 1,441 entries under 1,389 keys, but 1,334 entries "
        "lack a source field and 570 keys contain consonants the released mapping cannot "
        "emit. Its domain tags also do not reproduce the PDF's 1,375-key no-function "
        "comparison: removing every function-tagged key leaves 1,243, while retaining "
        "mixed-sense keys leaves 1,251.\n\n"
        "The claimed plant support comes from AI visual identification of 111 drawings, "
        "which is excluded by the active no-neural-vision policy. The paper itself says "
        "that no paragraph has "
        "been read as coherent connected Syriac prose by a specialist and estimates only "
        "10--15% word-level accuracy.\n\n"
        "Therefore no Syriac mapping, medical gloss, phrase, or plaintext is imported. "
        "Reopen when the exact corpus, complete statistical code and scores, selection "
        "history, and held evaluation are public and independently reconstructable. This "
        "hold does not establish that a "
        "Syriac or pharmaceutical hypothesis is false.\n"
    )


def main() -> None:
    if OUT_JSON.exists() or OUT_REPORT.exists():
        raise SystemExit("refusing to overwrite external source-audit outputs")
    result = build()
    OUT_JSON.write_bytes(canonical(result))
    OUT_REPORT.write_text(report(result), encoding="utf-8")
    print(json.dumps({"status": result["status"], "decision": result["decision"]},
                     sort_keys=True))


if __name__ == "__main__":
    main()
