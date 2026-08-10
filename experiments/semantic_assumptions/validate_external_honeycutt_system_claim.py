#!/usr/bin/env python3
"""Independent public-source validator for the Honeycutt system audit.

This module does not import or execute the producer.  It downloads the four
public objects again, extracts the PDF's tagged text layer (never OCR), and
reconstructs the producer's canonical result and report from those sources.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import tempfile
import urllib.request
from html.parser import HTMLParser
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
PRODUCER = HERE / "audit_external_honeycutt_system_claim.py"
RESULT = RESULTS / "external_honeycutt_system_claim_audit.json"
REPORT = RESULTS / "external_honeycutt_system_claim_audit.md"
OUT_JSON = RESULTS / "external_honeycutt_system_claim_audit_validation.json"
OUT_REPORT = RESULTS / "external_honeycutt_system_claim_audit_validation.md"

EXPECTED_PRODUCER_SHA256 = (
    "54a9cdcc98694176f1b2e26286b7f1329a74b22fa85c665fb93541e76f90d495"
)
EXPECTED_RESULT_SHA256 = (
    "450d6db3cd864cab442f8c6f5e66b1c1d2c3fe986758397eeddfbed8fd38d392"
)
EXPECTED_REPORT_SHA256 = (
    "b6e27c81c69f449c91da9510eccfd049ccd42d40d11953ca7251360f024532c6"
)

SOURCES = {
    "site_home": {
        "url": "https://www.thevoynich.org/",
        "sha256": "131c873221260a19e201cf79d2b30a1e06688bd5373dcf3e9f7a1c31f32ac883",
        "bytes": 16_723,
    },
    "site_findings": {
        "url": "https://www.thevoynich.org/findings",
        "sha256": "7d99378c8c24011dee265a753825571b918d4ddddd4278d2d040f8114a22edb7",
        "bytes": 17_313,
    },
    "zenodo_metadata": {
        "url": "https://zenodo.org/api/records/18687530",
        "sha256": "dc932161147cbdb4f4d7202a96392ee117db05d6cecf5ad85a8b3876bab25348",
        "projection_bytes": 1_347,
    },
    "zenodo_pdf": {
        "url": (
            "https://zenodo.org/api/records/18687530/files/"
            "Voynich%20Manuscript%20Systems%20Analysis_%20A%20Non-Semantic%20"
            "Structural%20Survey.pdf/content"
        ),
        "sha256": "954a52921ab182b9eac16989d4cf222a03057e2f80e909c6652c62ab758cc96d",
        "bytes": 286_106,
    },
}


class VisibleHTML(HTMLParser):
    """Extract visible text without using the producer's regex parser."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.hidden_depth = 0
        self.parts: list[str] = []

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        del attrs
        if tag.lower() in {"script", "style"}:
            self.hidden_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in {"script", "style"} and self.hidden_depth:
            self.hidden_depth -= 1

    def handle_data(self, data: str) -> None:
        if not self.hidden_depth:
            self.parts.append(data)

    def text(self) -> str:
        return re.sub(r"\s+", " ", " ".join(self.parts)).strip()


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


def visible_html(data: bytes) -> str:
    parser = VisibleHTML()
    parser.feed(data.decode("utf-8"))
    parser.close()
    return parser.text()


def stable_zenodo_projection(payload: dict[str, object]) -> dict[str, object]:
    """Independently select immutable record/version fields, excluding statistics."""
    record_metadata = payload["metadata"]
    file_inventory = payload["files"]
    return {
        "id": payload["id"],
        "conceptrecid": payload["conceptrecid"],
        "revision": payload["revision"],
        "doi": payload["doi"],
        "created": payload["created"],
        "updated": payload["updated"],
        "metadata": {
            "title": record_metadata["title"],
            "publication_date": record_metadata["publication_date"],
            "description": record_metadata["description"],
        },
        "files": [
            {
                "key": file_item["key"],
                "size": file_item["size"],
                "checksum": file_item["checksum"],
                "url": file_item["links"]["self"],
            }
            for file_item in file_inventory
        ],
    }


def extract_tagged_pdf(data: bytes) -> tuple[str, dict[str, str], int]:
    """Return tagged text, pdfinfo fields, and raster-image count."""
    with tempfile.TemporaryDirectory(prefix="honeycutt-validation-") as directory:
        source = Path(directory) / "source.pdf"
        text_path = Path(directory) / "source.txt"
        source.write_bytes(data)
        info_process = subprocess.run(
            ["pdfinfo", str(source)],
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
            ["pdftotext", "-layout", "-enc", "UTF-8", str(source), str(text_path)],
            check=True,
            capture_output=True,
            text=True,
            timeout=60,
        )
        if text_process.stderr.strip():
            raise AssertionError(f"pdftotext warning: {text_process.stderr.strip()}")
        image_process = subprocess.run(
            ["pdfimages", "-list", str(source)],
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


def normalized_pdf_text(text: str) -> str:
    return re.sub(
        r"\s+",
        " ",
        text.translate(
            {
                ord("\u200b"): None,
                ord("\ufeff"): None,
                ord("\u00ad"): None,
            }
        ),
    ).strip()


def expected_report() -> str:
    return (
        "# External Honeycutt operator-system claim audit\n\n"
        "Status: **REJECT_AS_ACTIVE_EVIDENCE_SOURCE_INCOMPLETE_AND_METHOD_EXCLUDED**.\n\n"
        "The public findings page states 31 operator classes, 226 folios, "
        "114,507 transitions, 92.9% Currier A/B accuracy, and 0/6 adversarial "
        "tests. The sole Zenodo file is a 34-page PDF with no code or data. It "
        "instead defines 13 named S0--S12 classes, supplies no observed-form-to-"
        "class mapping or transition table, and does not contain the website's "
        "numeric claims. Its complete adjacency atlas is listed as future work.\n\n"
        "The PDF explicitly credits AI with pattern detection, adjacency "
        "calculation, and geometric extraction, and its model uses visual hair-"
        "density and colour states. Those inputs are excluded by the active method "
        "policy. The 424-finding substrate database is private and invite-gated.\n\n"
        "Therefore the operator classes, module functions, Padua system identity, "
        "and claim that the manuscript is not language or cipher are not admitted. "
        "This source audit does not establish the opposite and supplies no word, "
        "meaning, plaintext, or translation.\n"
    )


def main() -> None:
    if OUT_JSON.exists() or OUT_REPORT.exists():
        raise SystemExit("refusing to overwrite Honeycutt validation outputs")

    checks: list[dict[str, object]] = []

    def check(name: str, condition: bool) -> None:
        checks.append({"name": name, "pass": bool(condition)})

    check("producer_source_sha256", digest(PRODUCER.read_bytes()) == EXPECTED_PRODUCER_SHA256)
    check("producer_result_sha256", digest(RESULT.read_bytes()) == EXPECTED_RESULT_SHA256)
    check("producer_report_sha256", digest(REPORT.read_bytes()) == EXPECTED_REPORT_SHA256)

    bodies = {name: download(item["url"]) for name, item in SOURCES.items()}
    metadata = json.loads(bodies["zenodo_metadata"])
    metadata_projection = stable_zenodo_projection(metadata)
    metadata_projection_bytes = canonical(metadata_projection)
    for name, item in SOURCES.items():
        if name == "zenodo_metadata":
            check(
                "source_hash:zenodo_metadata_stable_projection",
                digest(metadata_projection_bytes) == item["sha256"],
            )
            check(
                "source_bytes:zenodo_metadata_stable_projection",
                len(metadata_projection_bytes) == item["projection_bytes"],
            )
        else:
            check(f"source_hash:{name}", digest(bodies[name]) == item["sha256"])
            check(f"source_bytes:{name}", len(bodies[name]) == item["bytes"])

    home = visible_html(bodies["site_home"])
    findings = visible_html(bodies["site_findings"])
    paper, pdf_info, raster_images = extract_tagged_pdf(bodies["zenodo_pdf"])
    paper_flat = normalized_pdf_text(paper)
    paper_lower = paper_flat.lower()

    check("pdf_is_tagged", pdf_info.get("Tagged", "").lower() == "yes")
    check("pdf_has_34_pages", pdf_info.get("Pages") == "34")
    check("pdf_contains_no_raster_images", raster_images == 0)
    check("pdf_tagged_text_nonempty", len(paper_flat.split()) > 3_000)

    files = metadata.get("files", [])
    expected_file_name = (
        "Voynich Manuscript Systems Analysis_ A Non-Semantic Structural Survey.pdf"
    )
    check("zenodo_record_id", metadata.get("id") == 18_687_530)
    check(
        "zenodo_version_identity",
        metadata.get("conceptrecid") == "18687529"
        and metadata.get("revision") == 3
        and metadata.get("doi") == "10.5281/zenodo.18687530",
    )
    check(
        "zenodo_metadata",
        metadata.get("metadata", {}).get("title")
        == "Voynich Manuscript Paduan Medical Reference"
        and metadata.get("metadata", {}).get("publication_date") == "2026-02-19",
    )
    check("zenodo_single_file", len(files) == 1)
    check(
        "zenodo_pdf_inventory",
        len(files) == 1
        and files[0].get("key") == expected_file_name
        and files[0].get("size") == 286_106
        and files[0].get("checksum") == "md5:af5279daf02c1d18170d93a2272ba30e",
    )
    check(
        "zenodo_no_code_or_data_files",
        len(files) == 1 and str(files[0].get("key", "")).lower().endswith(".pdf"),
    )

    fcore_claim = (
        "F-CORE-1 An operator grammar exists in the VMS textual channel. "
        "31 operator classes, 226 folios, 114,507 transitions, 92.9% Currier A/B "
        "accuracy, adversarial testing 0/6 at p<0.05 for transferable cipher mapping."
    )
    check("website_fcore_claim_bound_as_one_entry", fcore_claim in findings)
    check("website_31_operator_classes", "31 operator classes" in findings)
    check("website_226_folios", "226 folios" in findings)
    check("website_114507_transitions", "114,507 transitions" in findings)
    check("website_92_9_currier_accuracy", "92.9% Currier A/B accuracy" in findings)
    check("website_adversarial_0_of_6", "adversarial testing 0/6" in findings)
    check("website_not_decipherment", "does not decipher word content" in home)
    check(
        "website_private_invite_only_database",
        "424 findings" in home
        and "internal-only research surface" in home
        and "Walkthrough access is invite-only" in home
        and "private, invite-gated research workspace" in findings,
    )

    operator_heading = "4. OPERATOR SYSTEM (S0–S12)"
    next_heading = "5. GEOMETRIC STATE MODEL (H/C/G)"
    check(
        "operator_section_bounds",
        operator_heading in paper_flat and next_heading in paper_flat,
    )
    operator_section = paper_flat.split(operator_heading, 1)[1].split(next_heading, 1)[0]
    definitions = {
        0: "Reset / null",
        1: "Boundary",
        2: "Flow initiation",
        3: "Sustained flow (kernel operator)",
        4: "Load / peak",
        5: "Cluster core",
        6: "Cluster periphery",
        7: "Gate / handoff",
        8: "Cyclic / volvelle-compatible step",
        9: "Convergent maximum",
        10: "Rare exit / return",
        11: "Annotation function",
        12: "Extraneous / index tagging",
    }
    check(
        "pdf_exact_s0_s12_definitions",
        all(f"S{index} — {label}" in operator_section for index, label in definitions.items()),
    )
    operator_labels = {
        int(value) for value in re.findall(r"\bS(1[0-2]|[0-9])\b", operator_section)
    }
    check("pdf_exact_13_class_inventory", operator_labels == set(range(13)))

    numeric_patterns = {
        "31_operator_classes": r"\b31\s+operator\s+classes\b",
        "226_folios": r"\b226\s+folios\b",
        "114507_transitions": r"\b114\s*,?\s*507\s+transitions\b",
        "92_9_accuracy": r"\b92\s*\.\s*9\s*%",
        "zero_of_six": r"\b0\s*/\s*6\b",
    }
    for name, pattern in numeric_patterns.items():
        check(f"pdf_absent_website_numeric:{name}", re.search(pattern, paper_flat, re.I) is None)

    check(
        "pdf_ai_extraction_credit",
        "AI Role:" in paper_flat
        and "Pattern detection, adjacency calculation, geometric extraction" in paper_flat,
    )
    check(
        "pdf_hair_and_colour_visual_states",
        "Hair Density (H0–H3)" in paper_flat
        and "Color Bands (C0–C3)" in paper_flat
        and "Used primarily in Balneo figures" in paper_flat
        and "Extracted through periodicity analysis" in paper_flat,
    )
    check(
        "pdf_complete_adjacency_atlas_is_future",
        "14. ROADMAP FOR NEXT-STAGE RESEARCH" in paper_flat
        and "14.1 Stage 1 — Complete Adjacency Atlas" in paper_flat
        and "full operator adjacency tables across all folios" in paper_flat
        and "weighted transition matrices" in paper_flat
        and 'Output → "Voynich Graph Atlas v1".' in paper_flat,
    )
    check(
        "pdf_no_repository_or_machine_data_reference",
        "github.com" not in paper_lower
        and not any(
            suffix in paper_lower for suffix in (".csv", ".tsv", ".json", ".sqlite")
        ),
    )

    # The bound tagged document has no raster figures and no observed Voynich
    # surface examples assigned to S-classes.  Its only use of EVA is a prose
    # assertion about independent transcriptions, not a mapping or data table.
    check("pdf_eva_mention_count", len(re.findall(r"\bEVA\b", paper_flat)) == 1)
    check(
        "pdf_no_observed_form_class_mapping",
        not any(
            phrase in paper_lower
            for phrase in (
                "glyph-to-operator",
                "glyph to operator",
                "observed-form-to-class",
                "operator assignment table",
                "class mapping table",
            )
        )
        and not any(
            token in paper_lower
            for token in ("qok", "daiin", "chedy", "shedy", "okeedy")
        ),
    )

    table_mentions = [
        re.sub(r"\s+", " ", line).strip()
        for line in paper.translate(
            {ord("\u200b"): None, ord("\ufeff"): None, ord("\u00ad"): None}
        ).splitlines()
        if re.search(r"\b(?:adjacency tables?|transition matrices?|adjacency matrix)\b", line, re.I)
    ]
    check(
        "pdf_no_published_transition_matrix_or_table",
        len(table_mentions) == 4
        and any("must resolve into valid" in line for line in table_mentions)
        and any("runnable adjacency matrix" in line for line in table_mentions)
        and any("full" in line and "operator adjacency tables" in line for line in table_mentions)
        and any("weighted" in line and "transition matrices" in line for line in table_mentions),
    )
    check(
        "pdf_no_published_language_cipher_comparator_result",
        not any(
            phrase in paper_lower
            for phrase in (
                "control corpus",
                "benchmark corpus",
                "comparator corpus",
                "sample size",
                "confidence interval",
                "precision and recall",
            )
        ),
    )

    site_claims = {
        "operator_classes_31": "31 operator classes" in findings,
        "folios_226": "226 folios" in findings,
        "transitions_114507": "114,507 transitions" in findings,
        "currier_accuracy_92_9": "92.9% Currier A/B accuracy" in findings,
        "adversarial_0_of_6": "adversarial testing 0/6" in findings,
        "database_internal_only": "internal-only research surface" in home,
        "not_decipherment": "does not decipher word content" in home,
    }
    paper_observations = {
        "operator_system_s0_s12_13_classes": (
            operator_heading in paper_flat
            and all(f"S{index}" in paper_flat for index in range(13))
        ),
        "site_31_class_phrase_absent": "31 operator classes" not in paper_flat,
        "site_114507_transition_phrase_absent": "114,507 transitions" not in paper_flat,
        "site_92_9_accuracy_phrase_absent": "92.9%" not in paper_flat,
        "site_0_of_6_phrase_absent": "0/6" not in paper_flat,
        "ai_pattern_detection_declared": (
            "AI Role:" in paper
            and "Pattern detection, adjacency calculation, geometric extraction" in paper_flat
        ),
        "hair_and_color_visual_states_used": (
            "Hair Density (H0–H3)" in paper_flat
            and "Color Bands (C0–C3)" in paper_flat
        ),
        "future_complete_adjacency_atlas_not_current_output": (
            "14.1 Stage 1 — Complete Adjacency Atlas" in paper_flat
            and 'Output → "Voynich Graph Atlas v1"' in paper_flat
        ),
        "no_github_url": "github.com" not in paper_lower,
        "no_zenodo_data_file_reference": not any(
            suffix in paper_lower for suffix in (".csv", ".tsv", ".json", ".sqlite")
        ),
    }
    gates = {
        "public_numeric_claims_reproduced_by_deposit": False,
        "observed_voynich_units_mapped_to_operator_classes": False,
        "adjacency_matrix_or_transition_table_published": False,
        "natural_language_or_cipher_comparator_results_published": False,
        "code_or_machine_readable_data_published": False,
        "method_complies_with_no_ai_vision_policy": False,
        "private_database_is_independently_auditable": False,
    }
    reconstructed = {
        "experiment": "EXTERNAL_HONEYCUTT_SYSTEM_CLAIM_AUDIT",
        "status": "REJECT_AS_ACTIVE_EVIDENCE_SOURCE_INCOMPLETE_AND_METHOD_EXCLUDED",
        "decision": "DO_NOT_IMPORT_OPERATOR_CLASSES_MODULE_MEANINGS_OR_SYSTEM_IDENTITY",
        "sources": {
            "zenodo_metadata": {
                "url": SOURCES["zenodo_metadata"]["url"],
                "sha256": digest(metadata_projection_bytes),
                "hash_scope": "stable_projection_excluding_live_statistics",
                "projection_bytes": len(metadata_projection_bytes),
            },
            **{
                name: {
                    "url": item["url"],
                    "sha256": digest(bodies[name]),
                    "bytes": len(bodies[name]),
                }
                for name, item in SOURCES.items()
                if name != "zenodo_metadata"
            },
        },
        "zenodo": {
            "record_id": metadata["id"],
            "title": metadata["metadata"]["title"],
            "publication_date": metadata["metadata"]["publication_date"],
            "published_files": len(files),
            "pdf_bytes": files[0]["size"],
            "code_or_data_files": 0,
        },
        "site_claims": site_claims,
        "paper_observations": paper_observations,
        "admission_gates": gates,
        "claim_ceiling": (
            "This rejects the cited public deposit as reproducible admissible evidence; "
            "it does not prove that the manuscript is language, nonlanguage, cipher, or "
            "machine and supplies no word, meaning, plaintext, or translation."
        ),
    }

    result_bytes = RESULT.read_bytes()
    report_text = REPORT.read_text(encoding="utf-8")
    check("producer_json_is_canonical", result_bytes == canonical(json.loads(result_bytes)))
    check("independent_canonical_json_reconstruction", result_bytes == canonical(reconstructed))
    check("independent_report_reconstruction", report_text == expected_report())
    check("all_admission_gates_false", set(gates.values()) == {False})
    check(
        "claim_ceiling_rejects_source_not_hypothesis",
        reconstructed["status"].startswith("REJECT_AS_ACTIVE_EVIDENCE_SOURCE")
        and "does not prove" in reconstructed["claim_ceiling"]
        and "does not establish the opposite" in report_text,
    )

    failures = [str(item["name"]) for item in checks if not item["pass"]]
    if failures:
        raise AssertionError("validation failures: " + ", ".join(failures))

    validation = {
        "experiment": "EXTERNAL_HONEYCUTT_SYSTEM_CLAIM_AUDIT_VALIDATION",
        "status": "PASS_CLEAN_PUBLIC_SOURCE_RECONSTRUCTION",
        "checks": len(checks),
        "failures": [],
        "producer_imported_or_executed": False,
        "ocr_or_image_recognition_used": False,
        "producer_sha256": digest(PRODUCER.read_bytes()),
        "producer_result_sha256": digest(result_bytes),
        "producer_report_sha256": digest(REPORT.read_bytes()),
        "public_source_sha256": {
            "site_home": digest(bodies["site_home"]),
            "site_findings": digest(bodies["site_findings"]),
            "zenodo_metadata_stable_projection": digest(metadata_projection_bytes),
            "zenodo_pdf": digest(bodies["zenodo_pdf"]),
        },
        "zenodo_metadata_hash_scope": "stable_projection_excluding_live_statistics",
        "zenodo_metadata_projection_bytes": len(metadata_projection_bytes),
        "tagged_pdf_text_sha256": digest(paper.encode("utf-8")),
        "conclusion": (
            "The cited public source is inadmissible as active evidence at this time; "
            "the underlying system hypothesis is not thereby shown false."
        ),
    }
    validation_report = (
        "# External Honeycutt system-audit validation\n\n"
        f"Status: **{validation['status']}**.\n\n"
        f"{len(checks)} independent checks re-fetched and bound both public site pages, "
        "the Zenodo 1,347-byte stable metadata projection (excluding live statistics), "
        "and the tagged 34-page PDF; reconstructed the F-CORE "
        "claims, S0--S12 inventory, missing public mappings/data/matrices, future-atlas "
        "wording, declared AI/visual inputs, private database gate, admission decision, "
        "canonical JSON, and report exactly. No producer module, OCR, or image "
        "recognition was used.\n\n"
        "The audit rejects only the cited public source as currently admissible evidence; "
        "it does not show that the underlying system hypothesis is false.\n"
    )
    OUT_JSON.write_bytes(canonical(validation))
    OUT_REPORT.write_text(validation_report, encoding="utf-8")
    print(json.dumps({"status": validation["status"], "checks": len(checks)}, sort_keys=True))


if __name__ == "__main__":
    main()
