#!/usr/bin/env python3
"""Independent GDT812 conservation checks; never imports or runs the builder."""
import argparse
from collections import Counter
import csv
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import urlparse


PAGES = ("f21r", "f32v", "f100v", "f101r")
FORBIDDEN = ("f84", "f84r")
BASE_COLUMNS = (
    "page_order", "page", "locus", "line_number", "code", "relation", "kind",
    "subtype", "section", "language", "hand", "quire", "folio_type",
    "paragraph_start", "paragraph_end", "token_count", "eva_clean", "ivtff_raw",
)
CROSS_COLUMNS = (
    "page", "locus", "all_three_present", "all_present_exact",
    "zl3b_it2a_similarity", "zl3b_rf1b_similarity", "zl3b_clean", "it2a_clean",
    "rf1b_clean",
)
READERS = {"ZL3b": "eva_clean", "IT2a": "it2a_clean", "RF1b": "rf1b_clean"}


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = Path(__file__).resolve().parents[1]
ARTIFACT = EXP / "artifacts/gdt812_validation.json"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def table(text):
    parser = csv.DictReader(io.StringIO(text), delimiter="\t")
    rows = list(parser)
    require(all(None not in row and None not in row.values() for row in rows),
            "Malformed TSV row")
    return parser.fieldnames, rows


def project(source, columns):
    command = ["./vmanus-exp", "query-tsv", source, "--selector", "page"]
    for page in PAGES:
        command.extend(["--allow", page])
    command.extend(["--columns", ",".join(columns)])
    for prefix in FORBIDDEN:
        command.extend(["--forbid-prefix", prefix])
    process = subprocess.run(command, cwd=ROOT, capture_output=True, check=True)
    headings, rows = table(process.stdout.decode("utf-8"))
    require(headings == list(columns), "Guard returned unexpected columns")
    stats_lines = [line[12:] for line in process.stderr.decode("utf-8").splitlines()
                   if line.startswith("GUARD_STATS ")]
    require(len(stats_lines) == 1, "Missing or duplicate guard statistics")
    stats = json.loads(stats_lines[0])
    require(stats["selected"] == len(rows), "Guard selected count mismatch")
    require(all(row["page"] in PAGES for row in rows), "Guard scope violation")
    return rows, {
        "allowed": list(PAGES), "columns": list(columns), "command": command,
        "forbidden_prefixes": list(FORBIDDEN), "selector": "page",
        "source": source, "projected_tsv_sha256": digest(process.stdout),
        "stats": stats,
    }


def keyed(rows):
    result = {(row["page"], row["locus"]): row for row in rows}
    require(len(result) == len(rows), "Duplicate source locus")
    return result


def validate():
    spec_path = EXP / "src/SPEC.json"
    admission_path = EXP / "src/PAGE_ADMISSIONS.tsv"
    result_path = EXP / "artifacts/gdt812_result.json"
    reader_path = EXP / "artifacts/COMPLETE_ADMITTED_PAGES.md"
    lines_path = EXP / "artifacts/ADMITTED_PAGE_LINES.tsv"
    spec = json.loads(spec_path.read_text())
    result = json.loads(result_path.read_text())
    manifest = json.loads((EXP / "experiment.json").read_text())
    _, admissions = table(admission_path.read_text())
    checks = []

    def group(name, function):
        try:
            detail = function()
            checks.append({"group": name, "status": "PASS", "detail": detail})
        except (ValueError, KeyError, TypeError, IndexError) as error:
            checks.append({"group": name, "status": "FAIL", "detail": str(error)})

    def admission():
        require(spec["physical_pages"] == list(PAGES), "Unexpected physical admission")
        require(spec["source_selectors"] == list(PAGES), "Unexpected selector admission")
        require([(r["physical_page"], r["source_selector"]) for r in admissions]
                == [(p, p) for p in PAGES], "Admission rows disagree with exact scope")
        require(all(r["decision"] == "ADMITTED" and r["purpose"].strip()
                    and r["grant_id"] == spec["grant_id"] for r in admissions),
                "Incomplete admission authority")
        require(spec["additional_page_limit"] == 20, "Wrong user quota")
        require(spec["additional_pages_admitted"] == len(admissions), "Wrong admitted count")
        require(spec["additional_pages_remaining"] == 20 - len(admissions), "Wrong reserve")
        require(spec["forbidden_prefixes"] == list(FORBIDDEN), "Missing explicit exclusions")
        for document in (spec, manifest, result):
            require(document["experiment_id"] == "GDT812", "Wrong experiment ID")
            require(document["sealed_data"] == {p: "FORBIDDEN" for p in FORBIDDEN},
                    "Missing sealed-data declaration")
        return {"admitted": len(admissions), "limit": 20, "remaining": 20 - len(admissions)}

    group("admission_and_seals", admission)
    # These commands are defined here, not accepted from result metadata or the builder.
    base, base_query = project("transcription/voynich_zl3b_lines.tsv", BASE_COLUMNS)
    cross, cross_query = project("transcription/voynich_cross_transcription_lines.tsv", CROSS_COLUMNS)
    base_by_key, cross_by_key = keyed(base), keyed(cross)
    output_columns, output = table(lines_path.read_text())
    output_by_key = keyed(output)

    def provenance():
        require(result["guarded_queries"] == [base_query, cross_query],
                "Recorded guarded-query provenance differs from fresh projections")
        for name, path in (("spec", spec_path), ("admissions", admission_path)):
            require(result["authorization"][name] == path.relative_to(ROOT).as_posix(),
                    "Authorization path mismatch")
            require(result["authorization"][name + "_sha256"] == digest(path.read_bytes()),
                    "Authorization hash mismatch")
        return {"independent_guarded_projections": 2, "authorization_hashes": 2}

    group("guarded_provenance", provenance)

    def conservation():
        require(base_by_key.keys() == cross_by_key.keys() == output_by_key.keys(),
                "Source/cross-reader/output locus sets differ")
        expected_columns = list(BASE_COLUMNS) + ["physical_page", "source_selector"]
        expected_columns += list(CROSS_COLUMNS[2:])
        require(output_columns == expected_columns, "Output schema differs from preservation schema")
        require(list(output_by_key) == list(base_by_key), "Source order not conserved")
        for key, source in base_by_key.items():
            projected = output_by_key[key]
            require(all(projected[c] == source[c] for c in BASE_COLUMNS),
                    "Base-field mismatch at " + key[1])
            alternate = cross_by_key[key]
            require(all(projected[c] == alternate[c] for c in CROSS_COLUMNS[2:]),
                    "Alternate-reading mismatch at " + key[1])
            require(alternate["zl3b_clean"] == source["eva_clean"],
                    "Independent ZL3b sources disagree at " + key[1])
            require(projected["physical_page"] == projected["source_selector"] == key[0],
                    "Owner/selector mismatch at " + key[1])
        return {"source_rows": len(base), "complete_three_reader_rows": len(cross)}

    group("exact_field_conservation", conservation)

    def summaries():
        expected = []
        for page in PAGES:
            rows = [r for r in base if r["page"] == page]
            require(rows, "Admitted page has no source rows")
            for row in rows:
                require(int(row["token_count"]) == len(row["eva_clean"].split()),
                        "Source token-count inconsistency at " + row["locus"])
            tokens = {label: sum(len((r[column] if label == "ZL3b" else
                       cross_by_key[(page, r["locus"])][column]).split()) for r in rows)
                      for label, column in READERS.items()}
            missing = {label: sum(not cross_by_key[(page, r["locus"])][column]
                                 for r in rows)
                       for label, column in READERS.items() if label != "ZL3b"}
            expected.append({"physical_page": page, "source_selector": page,
                             "source_lines": len(rows), "tokens": tokens,
                             "paragraph_starts": sum(int(r["paragraph_start"]) for r in rows),
                             "paragraph_ends": sum(int(r["paragraph_end"]) for r in rows),
                             "source_kind_counts": dict(Counter(r["kind"] for r in rows)),
                             "missing_cached_readings": missing})
        require(result["summaries"] == expected, "Per-page summaries differ from raw projections")
        total = sum(len(r["eva_clean"].split()) for r in base)
        require(result["source_lines"] == len(base), "Result line total mismatch")
        require(result["total_tokens"] == total, "Result token total mismatch")
        require(result["physical_pages"] == result["source_selectors"] == list(PAGES),
                "Result scope mismatch")
        require(result["admitted_physical_pages"] == len(PAGES), "Result admission total mismatch")
        return {"source_rows": len(base), "ZL3b_tokens": total, "per_page": expected}

    group("raw_derived_counts", summaries)

    def markdown():
        text = reader_path.read_text()
        require(re.findall(r"^## (.+)$", text, re.M) == list(PAGES), "Markdown page headings differ")
        sections = list(re.finditer(r"^### ([^\n]+)\n(.*?)(?=^### |\Z)", text, re.M | re.S))
        require(len(sections) == len(base), "Markdown locus count differs")
        for section, source in zip(sections, base):
            heading = source["locus"] + " — source kind " + source["kind"]
            for field, flag in (("paragraph_start", "PARAGRAPH_START"),
                                ("paragraph_end", "PARAGRAPH_END")):
                if source[field] == "1":
                    heading += " " + flag
            require(section[1] == heading, "Markdown locus/kind/paragraph flags differ")
            blocks = re.findall(r"^(ZL3b|IT2a|RF1b):\n\n```text\n(.*?)\n```", section[2], re.M | re.S)
            expected = [("ZL3b", source["eva_clean"])]
            alt = cross_by_key[(source["page"], source["locus"])]
            expected += [(label, alt[column]) for label, column in READERS.items() if label != "ZL3b"]
            require(blocks == expected, "Markdown reading differs at " + source["locus"])
        require(text.count("```text\n") == len(base) * len(READERS), "Unexpected text blocks")
        return {"loci": len(base), "exact_reading_blocks": len(base) * len(READERS)}

    group("complete_markdown_readings", markdown)

    def semantic_ceiling():
        for field in ("confirmed_lexemes", "confirmed_plaintext_clauses", "new_relations_counted"):
            require(type(result[field]) is int and result[field] == 0, "Nonzero semantic claim: " + field)
        for field in ("dictionary_changed", "semantic_ranking_performed", "visual_ownership_inferred"):
            require(result[field] is False, "Unexpected semantic flag: " + field)
        require(spec["confirmed_lexemes"] == 0, "Spec promotes a lexeme")
        require("SEMANTICS_UNRESOLVED" in result["status"], "Result omits unresolved status")
        require("EVA is transcription, not plaintext" in reader_path.read_text(), "Reader lacks caveat")
        return "Declared zero promotion verified; no meaning, species, or ownership is validated."

    group("declared_semantic_ceiling", semantic_ceiling)

    def image_provenance():
        path = EXP / "src/IMAGE_SOURCES.tsv"
        if not path.exists():
            return {"present": False, "scope": "Optional image inventory absent; images not validated"}
        columns, rows = table(path.read_text())
        require(rows, "Empty image inventory")
        require(columns == ["physical_page", "yale_image_id", "image_url", "sha256",
                            "manifest_url", "canvas_label", "viewed"], "Image schema differs")
        require([r["physical_page"] for r in rows] == list(PAGES), "Image page coverage differs")
        shared = {}
        for row in rows:
            urls = [v for k, v in row.items() if "url" in k.lower() and v]
            require(urls and all(urlparse(v).scheme == "https" and urlparse(v).netloc for v in urls),
                    "Missing/non-HTTPS image provenance")
            require(row["yale_image_id"].isdigit() and
                    "/iiif/2/" + row["yale_image_id"] + "/" in row["image_url"],
                    "Image ID and URL disagree")
            require(all(urlparse(v).netloc == "collections.library.yale.edu" for v in urls),
                    "Unexpected image provenance host")
            require(re.fullmatch(r"[0-9a-f]{64}", row["sha256"]), "Malformed image hash")
            require(row["physical_page"][1:] in row["canvas_label"].split(" and "),
                    "Canvas label does not include admitted page")
            require(row["viewed"] in {"ROOT_PERSONALLY_VIEWED",
                    "ROOT_AND_VISUAL_REVIEWER_PERSONALLY_VIEWED"}, "Missing direct-view declaration")
            binding = (row["image_url"], row["sha256"], row["manifest_url"], row["canvas_label"])
            require(shared.setdefault(row["yale_image_id"], binding) == binding,
                    "Shared image ID has inconsistent provenance")
        return {"present": True, "rows": len(rows), "unique_images": len(shared),
                "scope": "Metadata declarations only; image bytes and object semantics not validated"}

    group("optional_image_provenance", image_provenance)
    bindings = [spec_path, admission_path, result_path, lines_path, reader_path, Path(__file__).resolve()]
    image_path = EXP / "src/IMAGE_SOURCES.tsv"
    if image_path.exists():
        bindings.append(image_path)
    return {
        "experiment_id": "GDT812", "status": "PASS" if all(c["status"] == "PASS" for c in checks) else "FAIL",
        "claim_ceiling": "PASS validates construction and source conservation, not meanings.",
        "semantic_validation": False, "runner_imported_or_executed": False,
        "checks": checks, "guarded_queries": [base_query, cross_query],
        "validated_files": [{"path": p.relative_to(ROOT).as_posix(), "sha256": digest(p.read_bytes())}
                            for p in bindings],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--no-write", action="store_true", help="Print checks without changing any files")
    args = parser.parse_args()
    try:
        report = validate()
    except (OSError, ValueError, KeyError, TypeError, subprocess.CalledProcessError) as error:
        # Avoid publishing machine-local paths or raw subprocess payloads on failure.
        report = {"experiment_id": "GDT812", "status": "FAIL", "semantic_validation": False,
                  "error": "Validation could not complete: " + type(error).__name__}
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if not args.no_write:
        ARTIFACT.write_text(rendered)
    print(rendered, end="")
    return 0 if report["status"] == "PASS" else 1


if __name__ == '__main__':
    raise SystemExit(main())
