#!/usr/bin/env python3
"""Clean public-source validation of the DANI Syriac claim audit.

The validator never imports or executes the audit producer or the deposited
pipeline.  It re-fetches the Zenodo records and all current deposited files,
extracts only the PDF's embedded text, parses the pipeline as inert Python AST,
reconstructs the lexicon counts, and rebuilds the canonical audit artifacts.
"""

from __future__ import annotations

import ast
import copy
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
PRODUCER = HERE / "audit_external_syriac_dani_claim.py"
RESULT = RESULTS / "external_syriac_dani_claim_audit.json"
REPORT = RESULTS / "external_syriac_dani_claim_audit.md"
OUT_JSON = RESULTS / "external_syriac_dani_claim_audit_validation.json"
OUT_REPORT = RESULTS / "external_syriac_dani_claim_audit_validation.md"

EXPECTED_PRODUCER_SHA256 = (
    "003d6adc336faf6cc4af273912b59620e5d199f309d8cc908d6eaeac1f295ce0"
)
EXPECTED_RESULT_SHA256 = (
    "f1917e6417817cd157d858c7d79d1c2cd948818e606c214b45268fc9585fa34b"
)
EXPECTED_REPORT_SHA256 = (
    "2955ae13fd86a0a7d3b53270f35b3272a8e6b0726785e5f0f2a266fb31efdb00"
)

CURRENT_METADATA_URL = "https://zenodo.org/api/records/19583305"
SUPERSEDED_METADATA_URL = "https://zenodo.org/api/records/19583306"
FILE_SOURCES = {
    "paper": {
        "url": (
            "https://zenodo.org/api/records/19609475/files/"
            "A_Syriac_Pharmaceutical_Dispensatory_Encoded_in_the_"
            "Voynich_Manuscript.pdf/content"
        ),
        "sha256": "79627e490b535df5e57328a7bed22b2ae562a3b2cf56e39ca0650159b00d2208",
        "bytes": 88_289,
    },
    "pipeline": {
        "url": (
            "https://zenodo.org/api/records/19609475/files/"
            "pipeline_v31_1.py/content"
        ),
        "sha256": "079b6de7b8d2082303a0789fb3904105aecaa491e35600a557090e7981255d6f",
        "bytes": 11_613,
    },
    "lexicon": {
        "url": (
            "https://zenodo.org/api/records/19609475/files/"
            "lexicon_v31_session31_final.json/content"
        ),
        "sha256": "348992fa2bf555f1454a5a5485dd1ca9842acc143059f257f2fcdcf237821589",
        "bytes": 214_931,
    },
}
EXPECTED_CURRENT_PROJECTION_SHA256 = (
    "780301fd3c4b2c3c328c1f69a1eab65d0b0600f2d491ea9578f81699d36ddfa7"
)
EXPECTED_SUPERSEDED_PROJECTION_SHA256 = (
    "6a350f06393f473dd54afdf1661dac8ce5e194108a462760c0a40e0515d4649c"
)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(value: object) -> bytes:
    return (
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def download(url: str) -> bytes:
    request = urllib.request.Request(
        url, headers={"User-Agent": "VManus-independent-source-validator/1"}
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read()


def metadata_projection(record: dict[str, object]) -> dict[str, object]:
    """Bind immutable record content but deliberately omit live usage counts."""
    meta = record["metadata"]
    return {
        "id": record["id"],
        "conceptrecid": record["conceptrecid"],
        "revision": record["revision"],
        "doi": record["doi"],
        "created": record["created"],
        "updated": record["updated"],
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
            for item in record["files"]
        ],
    }


def extract_embedded_pdf_text(data: bytes) -> tuple[str, dict[str, str], int]:
    """Extract the digital text layer and count, but never inspect, raster images."""
    with tempfile.TemporaryDirectory(prefix="dani-source-validation-") as directory:
        pdf_path = Path(directory) / "source.pdf"
        text_path = Path(directory) / "source.txt"
        pdf_path.write_bytes(data)

        info_process = subprocess.run(
            ["pdfinfo", str(pdf_path)],
            check=True,
            capture_output=True,
            text=True,
            timeout=60,
        )
        info: dict[str, str] = {}
        for line in info_process.stdout.splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                info[key.strip()] = value.strip()

        text_process = subprocess.run(
            ["pdftotext", "-layout", "-enc", "UTF-8", str(pdf_path), str(text_path)],
            check=True,
            capture_output=True,
            text=True,
            timeout=60,
        )
        if text_process.stderr.strip():
            raise AssertionError(f"pdftotext warning: {text_process.stderr.strip()}")

        image_process = subprocess.run(
            ["pdfimages", "-list", str(pdf_path)],
            check=True,
            capture_output=True,
            text=True,
            timeout=60,
        )
        image_rows = [
            line
            for line in image_process.stdout.splitlines()
            if re.match(r"^\s*\d+\s+\d+\s+", line)
        ]
        return text_path.read_text(encoding="utf-8"), info, len(image_rows)


def assigned_literal(tree: ast.Module, name: str) -> object:
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if any(isinstance(target, ast.Name) and target.id == name for target in node.targets):
            return ast.literal_eval(node.value)
    raise AssertionError(f"missing literal assignment: {name}")


def pipeline_fingerprint(source: str) -> dict[str, object]:
    """Derive released operations from inert syntax, without importing the code."""
    tree = ast.parse(source)
    mapping = assigned_literal(tree, "EVA_CONSONANT_MAP")
    gallows = assigned_literal(tree, "GALLOWS_PREFIXES")
    standard = assigned_literal(tree, "STANDARD_PREFIXES")
    suffix = assigned_literal(tree, "SUFFIX_STRIP")
    if not isinstance(mapping, dict):
        raise AssertionError("EVA_CONSONANT_MAP is not a literal dictionary")
    function_names = sorted(
        node.name for node in tree.body if isinstance(node, ast.FunctionDef)
    )
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".", 1)[0])
    return {
        "mapping": mapping,
        "output_alphabet": sorted(set("".join(str(value) for value in mapping.values()))),
        "gallows_prefixes": gallows,
        "standard_prefixes": standard,
        "suffixes": suffix,
        "function_names": function_names,
        "imports": sorted(imports),
        "only_h_transcriber": ";H>" in source and ";Z>" not in source and ";F>" not in source,
        "local_corpus_default": "lsi_all.txt" in source,
        "frequency_weighted_token_counter": (
            "total_tokens += 1" in source and "matched_tokens += 1" in source
        ),
    }


def lexicon_fingerprint(
    lexicon: dict[str, list[dict[str, object]]], output_alphabet: set[str]
) -> dict[str, int]:
    entries = [entry for values in lexicon.values() for entry in values]
    function_keys = {
        key
        for key, values in lexicon.items()
        if any(entry.get("domain") == "function" for entry in values)
    }
    nonfunction_keys = {
        key
        for key, values in lexicon.items()
        if any(entry.get("domain") != "function" for entry in values)
    }
    return {
        "keys": len(lexicon),
        "entries": len(entries),
        "entries_without_source_field": sum(not entry.get("source") for entry in entries),
        "unreachable_keys_under_released_mapping_alphabet": sum(
            not set(key) <= output_alphabet for key in lexicon
        ),
        "function_domain_keys": len(function_keys),
        "keys_with_any_nonfunction_sense": len(nonfunction_keys),
        "unknown_gloss_keys": sum(
            any("unknown" in str(entry.get("meaning") or "").lower() for entry in values)
            for values in lexicon.values()
        ),
    }


def expected_report() -> str:
    return (
        "# External Syriac DANI claim audit\n\n"
        "Status: **HOLD_AS_LANGUAGE_OR_TRANSLATION_EVIDENCE_UNREPRODUCIBLE_NONHELD_"
        "AND_VISUAL_COMPONENT_EXCLUDED**.\n\n"
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


def admissibility_guard(result: dict[str, object], report: str) -> bool:
    gates = result.get("admission_gates", {})
    return bool(
        result.get("decision") == "DO_NOT_IMPORT_SYRIAC_MAPPING_WORDS_PHRASES_OR_PLAINTEXT"
        and isinstance(gates, dict)
        and gates.get("released_coverage_pipeline_and_lexicon_available") is True
        and all(
            value is False
            for key, value in gates.items()
            if key != "released_coverage_pipeline_and_lexicon_available"
        )
        and "does not prove" in str(result.get("claim_ceiling", ""))
        and "supplies no admitted Voynich word" in str(result.get("claim_ceiling", ""))
        and "Therefore no Syriac mapping, medical gloss, phrase, or plaintext is imported."
        in report
        and "This hold does not establish that a Syriac or pharmaceutical hypothesis is false."
        in report
    )


def version_guard(current: dict[str, object], old: dict[str, object]) -> bool:
    current_files = {item.get("key"): item.get("size") for item in current.get("files", [])}
    old_files = old.get("files", [])
    return bool(
        current.get("id") == 19_609_475
        and current.get("conceptrecid") == "19583305"
        and current.get("revision") == 4
        and current.get("doi") == "10.5281/zenodo.19609475"
        and current_files
        == {
            "pipeline_v31_1.py": 11_613,
            "lexicon_v31_session31_final.json": 214_931,
            "A_Syriac_Pharmaceutical_Dispensatory_Encoded_in_the_Voynich_Manuscript.pdf": 88_289,
        }
        and old.get("id") == 19_583_306
        and old.get("conceptrecid") == "19583305"
        and old.get("revision") == 3
        and len(old_files) == 1
        and str(old_files[0].get("key", "")).endswith(".pdf")
        and str(old.get("created", "")) < str(current.get("created", ""))
    )


def main() -> None:
    if OUT_JSON.exists() or OUT_REPORT.exists():
        raise SystemExit("refusing to overwrite DANI validation outputs")

    checks: list[dict[str, object]] = []

    def check(name: str, condition: bool) -> None:
        checks.append({"name": name, "pass": bool(condition)})

    check("producer_source_sha256", digest(PRODUCER.read_bytes()) == EXPECTED_PRODUCER_SHA256)
    check("producer_result_sha256", digest(RESULT.read_bytes()) == EXPECTED_RESULT_SHA256)
    check("producer_report_sha256", digest(REPORT.read_bytes()) == EXPECTED_REPORT_SHA256)

    current_body = download(CURRENT_METADATA_URL)
    superseded_body = download(SUPERSEDED_METADATA_URL)
    current = json.loads(current_body)
    superseded = json.loads(superseded_body)
    current_projection = metadata_projection(current)
    superseded_projection = metadata_projection(superseded)
    current_projection_bytes = canonical(current_projection)
    superseded_projection_bytes = canonical(superseded_projection)

    check("current_concept_resolves_latest_version", version_guard(current, superseded))
    check(
        "current_stable_metadata_projection_sha256",
        digest(current_projection_bytes) == EXPECTED_CURRENT_PROJECTION_SHA256,
    )
    check("current_stable_metadata_projection_bytes", len(current_projection_bytes) == 3_259)
    check(
        "superseded_stable_metadata_projection_sha256",
        digest(superseded_projection_bytes) == EXPECTED_SUPERSEDED_PROJECTION_SHA256,
    )
    check("superseded_stable_metadata_projection_bytes", len(superseded_projection_bytes) == 2_245)
    check(
        "live_usage_statistics_excluded_from_projection",
        "stats" in current and "stats" not in current_projection,
    )

    bodies = {name: download(item["url"]) for name, item in FILE_SOURCES.items()}
    for name, item in FILE_SOURCES.items():
        check(f"source_hash:{name}", digest(bodies[name]) == item["sha256"])
        check(f"source_bytes:{name}", len(bodies[name]) == item["bytes"])

    paper, pdf_info, raster_images = extract_embedded_pdf_text(bodies["paper"])
    paper_flat = re.sub(r"\s+", " ", unicodedata.normalize("NFKC", paper))
    paper_lower = paper.lower()
    check("pdf_has_11_pages", pdf_info.get("Pages") == "11")
    check("pdf_embedded_text_nonempty", len(paper_flat.split()) > 3_000)
    check("pdf_contains_no_raster_images", raster_images == 0)

    pipeline = bodies["pipeline"].decode("utf-8")
    pipeline_fp = pipeline_fingerprint(pipeline)
    expected_mapping = {
        "k": "k", "d": "d", "r": "r", "s": "s", "l": "l", "n": "n",
        "q": "w", "y": "y", "m": "m", "g": "g", "sh": "š", "ch": "k",
        "cth": "ṭk", "ckh": "kk", "cph": "pk", "cfh": "pk", "t": "ṭ",
        "p": "p", "f": "ṣ", "a": "", "o": "", "e": "", "i": "",
        "x": "", "h": "",
    }
    check("pipeline_ast_exact_mapping", pipeline_fp["mapping"] == expected_mapping)
    check(
        "pipeline_ast_output_alphabet",
        set(pipeline_fp["output_alphabet"]) == set("kdrslnwymgšṭpṣ"),
    )
    check("pipeline_ast_gallows_prefixes", pipeline_fp["gallows_prefixes"] == ["ṭ", "p", "ṣ"])
    check("pipeline_ast_standard_prefixes", pipeline_fp["standard_prefixes"] == ["d", "l", "w"])
    check("pipeline_ast_suffixes", pipeline_fp["suffixes"] == ["yn"])
    check(
        "pipeline_ast_exact_top_level_functions",
        pipeline_fp["function_names"]
        == ["classify_folio", "eva_to_skeleton", "parse_ivtff", "run_pipeline", "strip_affixes"],
    )
    check("pipeline_ast_no_statistical_import", not ({"random", "scipy", "sklearn"} & set(pipeline_fp["imports"])))
    check("pipeline_only_h_transcriber", bool(pipeline_fp["only_h_transcriber"]))
    check("pipeline_local_corpus_default", bool(pipeline_fp["local_corpus_default"]))
    check("pipeline_frequency_weighted_token_counter", bool(pipeline_fp["frequency_weighted_token_counter"]))
    check(
        "pipeline_lacks_headline_statistical_components",
        all(
            fragment not in pipeline.lower()
            for fragment in (
                "fisher_exact", "import random", "def permutation", "hebrew",
                "arabic", "plant_matches", "recipe_templates",
            )
        ),
    )

    lexicon = json.loads(bodies["lexicon"])
    check(
        "lexicon_schema",
        isinstance(lexicon, dict)
        and all(
            isinstance(key, str)
            and isinstance(values, list)
            and values
            and all(isinstance(entry, dict) for entry in values)
            for key, values in lexicon.items()
        ),
    )
    lexicon_fp = lexicon_fingerprint(lexicon, set(pipeline_fp["output_alphabet"]))
    expected_lexicon_fp = {
        "keys": 1_389,
        "entries": 1_441,
        "entries_without_source_field": 1_334,
        "unreachable_keys_under_released_mapping_alphabet": 570,
        "function_domain_keys": 146,
        "keys_with_any_nonfunction_sense": 1_251,
        "unknown_gloss_keys": 16,
    }
    check("lexicon_exact_audit_counts", lexicon_fp == expected_lexicon_fp)
    entries = [entry for values in lexicon.values() for entry in values]
    check("lexicon_nonempty_source_count", sum(bool(entry.get("source")) for entry in entries) == 107)
    check("lexicon_reachable_key_count", len(lexicon) - lexicon_fp["unreachable_keys_under_released_mapping_alphabet"] == 819)
    check(
        "lexicon_generated_prefix_gloss_counts",
        sum(
            any("and-" in str(entry.get("meaning", "")) for entry in values)
            for values in lexicon.values()
        ) == 233
        and sum(
            any(str(entry.get("meaning", "")).startswith("of/which-") for entry in values)
            for values in lexicon.values()
        ) == 216
        and sum(
            any(str(entry.get("meaning", "")).startswith("to/for-") for entry in values)
            for values in lexicon.values()
        ) == 216,
    )

    published_claims = {
        "mapping_table_present": (
            "2.2 Character Mapping" in paper
            and all(
                fragment in paper_flat
                for fragment in (
                    "k k (kaph)", "ch k (kaph)", "q w (waw)",
                    "a, o, e, i ∅ vowels stripped",
                )
            )
        ),
        "corpus_35259_tokens_225_folios": "35,259 tokens across 225 folios" in paper_flat,
        "paper_coverage_86_9_percent": "30,632 of 35,259 tokens (86.9%)" in paper_flat,
        "permutation_claim_500_z_4_86": (
            "Against 500 random permutations: true mapping 86.9%, chance mean 44.7%, z = 4.86"
            in paper_flat
        ),
        "ai_plant_identification_111_folios": (
            "An independent AI instance" in paper_flat
            and "visually identified plants in 111 herbal folios" in paper_flat
        ),
        "fourteen_visual_correspondences_claimed": (
            "14 folios showed statistically significant concordance" in paper_flat
        ),
        "connected_prose_absent": (
            "No connected Syriac prose" in paper_flat
            and "no paragraph has been read as coherent connected Syriac prose by a specialist"
            in paper_flat
        ),
        "word_accuracy_claim_10_to_15_percent": "Word-level decode accuracy 10–15%" in paper_flat,
    }
    check("all_bound_published_claims_present", all(published_claims.values()))

    current_files = current["files"]
    current_keys = {item["key"] for item in current_files}
    function_keys = {
        key
        for key, values in lexicon.items()
        if any(entry.get("domain") == "function" for entry in values)
    }
    method_observations = {
        "latest_concept_version_resolved": (
            current["conceptrecid"] == "19583305" and current["revision"] == 4
        ),
        "older_one_pdf_record_is_superseded": (
            superseded["id"] == 19_583_306 and current["id"] == 19_609_475
        ),
        "pipeline_and_lexicon_now_published": (
            "pipeline_v31_1.py" in current_keys
            and "lexicon_v31_session31_final.json" in current_keys
        ),
        "exact_input_corpus_not_published": (
            pipeline_fp["local_corpus_default"] and "lsi_all.txt" not in current_keys
        ),
        "released_pipeline_has_only_coverage_functions": (
            pipeline_fp["function_names"]
            == ["classify_folio", "eva_to_skeleton", "parse_ivtff", "run_pipeline", "strip_affixes"]
            and "random" not in pipeline_fp["imports"]
        ),
        "permutation_language_visual_phrase_code_absent": all(
            fragment not in pipeline.lower()
            for fragment in ("fisher_exact", "hebrew", "arabic", "plant_matches", "recipe_templates")
        ),
        "paper_says_lexicon_is_supplementary": "lexicon_v31_session31" in paper,
        "paper_says_pipeline_is_supplementary": "pipeline_v31.py" in paper,
        "mapping_and_evaluation_use_same_corpus": (
            "The study uses the ZL (Zandbergen-Landini) merged IVTFF transcription" in paper_flat
            and "Each EVA character is mapped to a Syriac consonant" in paper_flat
            and "Coverage is tested against 500 random permutations" in paper_flat
        ),
        "no_train_cal_test_or_held_design_disclosed": not any(
            phrase in paper_lower
            for phrase in ("training set", "validation set", "test set", "held-out", "holdout")
        ),
        "null_randomizes_only_ten_core_characters": (
            "reassigns the 10 core EVA consonant characters to a random permutation of the 10 Syriac consonants"
            in paper_flat
        ),
        "pipeline_has_additional_unrandomized_choices": all(
            phrase in paper_flat
            for phrase in (
                "strip annotation markers", "attempt gallows prefix stripping",
                "attempt standard prefix stripping", "attempt suffix stripping (-yn)",
            )
        ),
        "chance_coverage_44_7_percent": "chance mean 44.7%" in paper_flat,
        "metadata_and_pdf_null_numbers_conflict": (
            "z-score 3.83 (14.9 percentage points above baseline)"
            in current["metadata"]["description"]
            and "chance mean 44.7%, z = 4.86" in paper_flat
        ),
        "paper_language_coverage_internally_changes": (
            "30,632 of 35,259 tokens (86.9%)" in paper_flat and "Syriac 85.1% 3.8" in paper_flat
        ),
        "exact_empirical_p_formula_not_disclosed": not any(
            phrase in paper_lower for phrase in ("plus-one", "1/501", "empirical p-value")
        ),
        "lexicon_has_1389_keys_1441_entries": (
            lexicon_fp["keys"] == 1_389 and lexicon_fp["entries"] == 1_441
        ),
        "lexicon_entries_without_source_field_1334": (
            lexicon_fp["entries_without_source_field"] == 1_334
        ),
        "lexicon_keys_unreachable_by_released_mapping_570": (
            lexicon_fp["unreachable_keys_under_released_mapping_alphabet"] == 570
        ),
        "deposited_function_domains_conflict_with_1375_no_function_count": (
            len(function_keys) == 146
            and len(lexicon) - len(function_keys) == 1_243
            and lexicon_fp["keys_with_any_nonfunction_sense"] == 1_251
            and "Pharma content only (no function words) 1,375" in paper_flat
        ),
        "lexicon_unknown_gloss_keys_16": lexicon_fp["unknown_gloss_keys"] == 16,
    }
    check("all_method_observations_reconstructed", all(method_observations.values()))

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

    source_descriptors = {
        "zenodo_metadata": {
            "url": CURRENT_METADATA_URL,
            "sha256": digest(current_projection_bytes),
            "hash_scope": "stable_projection_excluding_live_statistics",
            "projection_bytes": len(current_projection_bytes),
        },
        "superseded_metadata": {
            "url": SUPERSEDED_METADATA_URL,
            "sha256": digest(superseded_projection_bytes),
            "hash_scope": "stable_projection_excluding_live_statistics",
            "projection_bytes": len(superseded_projection_bytes),
        },
        **{
            name: {
                "url": item["url"],
                "sha256": digest(bodies[name]),
                "bytes": len(bodies[name]),
            }
            for name, item in FILE_SOURCES.items()
        },
    }
    reconstructed = {
        "experiment": "EXTERNAL_SYRIAC_DANI_CLAIM_AUDIT",
        "status": (
            "HOLD_AS_LANGUAGE_OR_TRANSLATION_EVIDENCE_UNREPRODUCIBLE_NONHELD_"
            "AND_VISUAL_COMPONENT_EXCLUDED"
        ),
        "decision": "DO_NOT_IMPORT_SYRIAC_MAPPING_WORDS_PHRASES_OR_PLAINTEXT",
        "sources": source_descriptors,
        "zenodo": {
            "concept_record_id": int(current["conceptrecid"]),
            "record_id": current["id"],
            "revision": current["revision"],
            "doi": current["doi"],
            "title": current["metadata"]["title"],
            "publication_date": current["metadata"]["publication_date"],
            "published_files": len(current_files),
            "pipeline_files": 1,
            "lexicon_files": 1,
            "corpus_files": 0,
        },
        "lexicon_audit": lexicon_fp,
        "published_claims": published_claims,
        "method_observations": method_observations,
        "admission_gates": admission_gates,
        "claim_ceiling": (
            "This holds the public DANI deposit outside the active evidence base. It does not "
            "prove that Syriac, Aramaic, Semitic language, or pharmaceutical content is false; "
            "it supplies no admitted Voynich word, phrase, plaintext, or translation."
        ),
    }

    result_bytes = RESULT.read_bytes()
    report_text = REPORT.read_text(encoding="utf-8")
    expected_report_text = expected_report()
    check("producer_json_is_canonical", result_bytes == canonical(json.loads(result_bytes)))
    check("independent_canonical_json_reconstruction", result_bytes == canonical(reconstructed))
    check("independent_report_reconstruction", report_text == expected_report_text)
    check("scientific_claim_ceiling_guard", admissibility_guard(reconstructed, report_text))

    # Explicit mutations must be rejected by source, version, or overstatement guards.
    overstatement = copy.deepcopy(reconstructed)
    overstatement["decision"] = "IMPORT_SYRIAC_TRANSLATION"
    check("mutation_rejected:import_decision", not admissibility_guard(overstatement, report_text))
    overstatement = copy.deepcopy(reconstructed)
    overstatement["claim_ceiling"] = "The manuscript is proven to be Syriac."
    check("mutation_rejected:claim_ceiling", not admissibility_guard(overstatement, report_text))
    overstatement = copy.deepcopy(reconstructed)
    overstatement["admission_gates"]["visual_evidence_complies_with_no_ai_vision_policy"] = True
    check("mutation_rejected:visual_gate", not admissibility_guard(overstatement, report_text))
    overstatement = copy.deepcopy(reconstructed)
    overstatement["admission_gates"]["exact_corpus_and_headline_statistics_reconstructable"] = True
    check("mutation_rejected:reproducibility_gate", not admissibility_guard(overstatement, report_text))
    bad_report = report_text.replace(
        "Therefore no Syriac mapping, medical gloss, phrase, or plaintext is imported.",
        "Therefore the Syriac mapping and plaintext are admitted.",
    )
    check("mutation_rejected:report_overstatement", not admissibility_guard(reconstructed, bad_report))

    bad_current = copy.deepcopy(current)
    bad_current["revision"] = 5
    check("mutation_rejected:version", not version_guard(bad_current, superseded))
    bad_old = copy.deepcopy(superseded)
    bad_old["files"].append(copy.deepcopy(bad_old["files"][0]))
    check("mutation_rejected:superseded_inventory", not version_guard(current, bad_old))

    mutated_pipeline = pipeline.replace("'q': 'w'", "'q': 'q'", 1)
    check(
        "mutation_rejected:pipeline_mapping",
        pipeline_fingerprint(mutated_pipeline)["output_alphabet"] != pipeline_fp["output_alphabet"],
    )
    mutated_lexicon = copy.deepcopy(lexicon)
    mutated_lexicon.pop(next(iter(mutated_lexicon)))
    check(
        "mutation_rejected:lexicon_inventory",
        lexicon_fingerprint(mutated_lexicon, set(pipeline_fp["output_alphabet"])) != lexicon_fp,
    )
    check(
        "mutation_rejected:pdf_admission",
        "No connected Syriac prose"
        not in paper_flat.replace("No connected Syriac prose", "Connected Syriac prose", 1),
    )

    failures = [str(item["name"]) for item in checks if not item["pass"]]
    if failures:
        raise AssertionError("validation failures: " + ", ".join(failures))

    validation = {
        "experiment": "EXTERNAL_SYRIAC_DANI_CLAIM_AUDIT_VALIDATION",
        "status": "PASS_CLEAN_PUBLIC_SOURCE_RECONSTRUCTION",
        "checks": len(checks),
        "failures": [],
        "producer_imported_or_executed": False,
        "deposited_pipeline_imported_or_executed": False,
        "ocr_or_image_recognition_used": False,
        "producer_sha256": digest(PRODUCER.read_bytes()),
        "producer_result_sha256": digest(result_bytes),
        "producer_report_sha256": digest(REPORT.read_bytes()),
        "public_source_sha256": {
            "current_stable_metadata_projection": digest(current_projection_bytes),
            "superseded_stable_metadata_projection": digest(superseded_projection_bytes),
            **{name: digest(body) for name, body in bodies.items()},
        },
        "embedded_pdf_text_sha256": digest(paper.encode("utf-8")),
        "lexicon_audit": lexicon_fp,
        "mutation_guards": 10,
        "conclusion": (
            "The current public deposit is not admissible as Syriac, pharmaceutical, "
            "lexical, plaintext, or translation evidence; the underlying hypothesis is "
            "not thereby shown false."
        ),
    }
    validation_report = (
        "# External Syriac DANI audit validation\n\n"
        f"Status: **{validation['status']}**.\n\n"
        f"{len(checks)} independent checks re-fetched the current concept record, its "
        "superseded one-PDF version, and all three current files. They reconstructed the "
        "stable metadata projections, embedded PDF claims, inert pipeline AST, mapping "
        "alphabet, lexicon inventory, admission decision, canonical JSON, and report "
        "exactly. Ten source/version/overstatement mutations were rejected.\n\n"
        "Neither the producer nor the deposited pipeline was imported or executed. Only "
        "the PDF's embedded digital text was extracted; no OCR or image recognition was "
        "used. The hold concerns the currently deposited evidence and does not show that "
        "the Syriac or pharmaceutical hypothesis itself is false.\n"
    )
    OUT_JSON.write_bytes(canonical(validation))
    OUT_REPORT.write_text(validation_report, encoding="utf-8")
    print(json.dumps({"status": validation["status"], "checks": len(checks)}, sort_keys=True))


if __name__ == "__main__":
    main()
