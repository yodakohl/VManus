#!/usr/bin/env python3
"""Audit the public Honeycutt/thevoynich.org operator-system claim."""

from __future__ import annotations

import hashlib
import html
import json
import re
import subprocess
import tempfile
import urllib.request
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
OUT_JSON = RESULTS / "external_honeycutt_system_claim_audit.json"
OUT_REPORT = RESULTS / "external_honeycutt_system_claim_audit.md"

SOURCES = {
    "site_home": {
        "url": "https://www.thevoynich.org/",
        "sha256": "131c873221260a19e201cf79d2b30a1e06688bd5373dcf3e9f7a1c31f32ac883",
    },
    "site_findings": {
        "url": "https://www.thevoynich.org/findings",
        "sha256": "7d99378c8c24011dee265a753825571b918d4ddddd4278d2d040f8114a22edb7",
    },
    "zenodo_metadata": {
        "url": "https://zenodo.org/api/records/18687530",
        "sha256": "dc932161147cbdb4f4d7202a96392ee117db05d6cecf5ad85a8b3876bab25348",
    },
    "zenodo_pdf": {
        "url": (
            "https://zenodo.org/api/records/18687530/files/"
            "Voynich%20Manuscript%20Systems%20Analysis_%20A%20Non-Semantic%20"
            "Structural%20Survey.pdf/content"
        ),
        "sha256": "954a52921ab182b9eac16989d4cf222a03057e2f80e909c6652c62ab758cc96d",
    },
}


def download(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "VManus-source-audit/1"})
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read()


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def plain_html(data: bytes) -> str:
    text = data.decode("utf-8")
    text = re.sub(r"<script\b.*?</script>", " ", text, flags=re.I | re.S)
    text = re.sub(r"<style\b.*?</style>", " ", text, flags=re.I | re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


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
    metadata_projection = stable_metadata_projection(metadata)
    observed_hashes = {
        "zenodo_metadata": sha(canonical(metadata_projection)),
        **{name: sha(body) for name, body in bodies.items() if name != "zenodo_metadata"},
    }
    if any(observed_hashes[name] != item["sha256"] for name, item in SOURCES.items()):
        raise ValueError("public source drift; version the audit rather than silently update")

    home = plain_html(bodies["site_home"])
    findings = plain_html(bodies["site_findings"])
    paper = pdf_text(bodies["zenodo_pdf"])
    paper_flat = re.sub(
        r"\s+", " ",
        paper.translate({ord("\u200b"): None, ord("\ufeff"): None, ord("\xad"): None}),
    )

    files = metadata.get("files", [])
    if len(files) != 1 or files[0].get("size") != 286_106:
        raise ValueError("Zenodo file inventory drift")
    if (metadata.get("id") != 18_687_530 or metadata.get("revision") != 3 or
            metadata.get("conceptrecid") != "18687529"):
        raise ValueError("Zenodo record drift")

    site_claims = {
        "operator_classes_31": "31 operator classes" in findings,
        "folios_226": "226 folios" in findings,
        "transitions_114507": "114,507 transitions" in findings,
        "currier_accuracy_92_9": "92.9% Currier A/B accuracy" in findings,
        "adversarial_0_of_6": "adversarial testing 0/6" in findings,
        "database_internal_only": "internal-only research surface" in home,
        "not_decipherment": "does not decipher word content" in home,
    }
    if not all(site_claims.values()):
        raise ValueError("public site claim text drift")

    paper_observations = {
        "operator_system_s0_s12_13_classes": (
            "OPERATOR SYSTEM (S0–S12)" in paper_flat and
            all(f"S{index}" in paper_flat for index in range(13))
        ),
        "site_31_class_phrase_absent": "31 operator classes" not in paper_flat,
        "site_114507_transition_phrase_absent": "114,507 transitions" not in paper_flat,
        "site_92_9_accuracy_phrase_absent": "92.9%" not in paper_flat,
        "site_0_of_6_phrase_absent": "0/6" not in paper_flat,
        "ai_pattern_detection_declared": (
            "AI Role:" in paper and
            "Pattern detection, adjacency calculation, geometric extraction" in paper_flat
        ),
        "hair_and_color_visual_states_used": (
            "Hair Density (H0–H3)" in paper_flat and
            "Color Bands (C0–C3)" in paper_flat
        ),
        "future_complete_adjacency_atlas_not_current_output": (
            "14.1 Stage 1 — Complete Adjacency Atlas" in paper_flat and
            'Output → "Voynich Graph Atlas v1"' in paper_flat
        ),
        "no_github_url": "github.com" not in paper.lower(),
        "no_zenodo_data_file_reference": not any(
            suffix in paper.lower() for suffix in (".csv", ".tsv", ".json", ".sqlite")
        ),
    }
    if not all(paper_observations.values()):
        raise ValueError("paper observation drift")

    gates = {
        "public_numeric_claims_reproduced_by_deposit": False,
        "observed_voynich_units_mapped_to_operator_classes": False,
        "adjacency_matrix_or_transition_table_published": False,
        "natural_language_or_cipher_comparator_results_published": False,
        "code_or_machine_readable_data_published": False,
        "method_complies_with_no_ai_vision_policy": False,
        "private_database_is_independently_auditable": False,
    }
    return {
        "experiment": "EXTERNAL_HONEYCUTT_SYSTEM_CLAIM_AUDIT",
        "status": "REJECT_AS_ACTIVE_EVIDENCE_SOURCE_INCOMPLETE_AND_METHOD_EXCLUDED",
        "decision": "DO_NOT_IMPORT_OPERATOR_CLASSES_MODULE_MEANINGS_OR_SYSTEM_IDENTITY",
        "sources": {
            "zenodo_metadata": {
                "url": SOURCES["zenodo_metadata"]["url"],
                "sha256": observed_hashes["zenodo_metadata"],
                "hash_scope": "stable_projection_excluding_live_statistics",
                "projection_bytes": len(canonical(metadata_projection)),
            },
            **{
                name: {"url": item["url"], "sha256": observed_hashes[name],
                       "bytes": len(bodies[name])}
                for name, item in SOURCES.items() if name != "zenodo_metadata"
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


def report(result: dict[str, object]) -> str:
    return (
        "# External Honeycutt operator-system claim audit\n\n"
        f"Status: **{result['status']}**.\n\n"
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
        raise SystemExit("refusing to overwrite external source-audit outputs")
    result = build()
    OUT_JSON.write_bytes(canonical(result))
    OUT_REPORT.write_text(report(result), encoding="utf-8")
    print(json.dumps({"status": result["status"], "decision": result["decision"]},
                     sort_keys=True))


if __name__ == "__main__":
    main()
