#!/usr/bin/env python3
"""Independent release validator for GDT647."""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import io
import json
import re
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = Path("experiments/yolo/gdt647_quality_subdegree_family_migration")
ART = ROOT / BASE / "artifacts"
RUN = ROOT / BASE / "src/run.py"
MANIFEST = ROOT / BASE / "experiment.json"
VALIDATION = ART / "VALIDATION.json"
G646 = Path("experiments/yolo/gdt646_tcheey_surface_completion")
G646_ALLOW = G646 / "artifacts/PAGE_ALLOWLIST.tsv"
G646_GLOSSARY = G646 / "artifacts/V23_EXACT_TOKEN_GLOSSARY.tsv"
G646_DICTIONARY = G646 / "artifacts/WORKING_DICTIONARY_V23.tsv"
TOKENS = Path("transcription/voynich_zl3b_tokens.tsv")
CROSS = Path("transcription/voynich_cross_transcription_lines.tsv")

STATUS = "PASS_107_OBSERVED_QUALITY_WHOLES__NO_SUFFIX_GLOBALIZATION"
EXPECTED_DECISIONS = Counter({
    "ADD_V24_EXACT_WHOLE": 86,
    "ADD_V24_READER_WARNING_WHOLE": 4,
    "REVISE_V23_EXACT_WHOLE": 15,
    "REVISE_V23_READER_WARNING_WHOLE": 1,
    "RETAIN_IDENTICAL_V23": 1,
})
EXPECTED_FAMILIES = Counter({
    "QUALITY_COMPOUND_DIRECT": 21,
    "QUALITY_COMPOUND_O_CARRIER": 19,
    "QUALITY_COMPOUND_QO_CARRIER": 21,
    "MOISTURE_QUALITY_DIRECT": 12,
    "TEMPERATURE_QUALITY_DIRECT": 10,
    "TEMPERATURE_QUALITY_O_CARRIER": 12,
    "TEMPERATURE_QUALITY_QO_CARRIER": 12,
})
EXPECTED_NULL = {
    "ksheedy", "tcheedy", "tsheedy", "okcheedy", "oksheey", "oksheedy",
    "otsheey", "otsheedy", "qoksheey", "qotsheey", "qotsheedy", "kdy", "tdy",
}
READER_UNSTABLE = {"kcheedy", "otcheedy", "qoksheedy", "qotcheey", "qotdy"}
EXPECTED_BASE = {
    "physical_lines": 4128, "known_token_positions": 10351,
    "unknown_token_positions": 21988, "complete_multi_token_lines": 61,
    "strict_complete_lines": 42, "one_unknown_lines": 70,
    "strict_one_unknown_lines": 22, "exact_glossary_surfaces": 257,
}
EXPECTED_FINAL = {
    "physical_lines": 4128, "known_token_positions": 13782,
    "unknown_token_positions": 18557, "complete_multi_token_lines": 77,
    "strict_complete_lines": 42, "one_unknown_lines": 152,
    "strict_one_unknown_lines": 48, "exact_glossary_surfaces": 347,
}
FILLER = re.compile(
    r"arbeitsgut|arbeitschritt|arbeitsschritt|arbeitsmittel|arbeitsstoff|arbeitsobjekt|"
    r"werkzeug|produkt weiter|f.hre .* aus|leite .* weiter", re.IGNORECASE,
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_hash(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def load_builder():
    spec = importlib.util.spec_from_file_location("gdt647_builder_validation", RUN)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load GDT647 builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def guarded_query(path: Path, pages: set[str], columns: str) -> list[dict[str, str]]:
    command = [str(ROOT / "vmanus-exp"), "query-tsv", str(path), "--selector", "page"]
    for page in sorted(pages):
        command.extend(("--allow", page))
    command.extend(("--columns", columns, "--forbid-prefix", "f84", "--forbid-prefix", "f84r"))
    done = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    guard_lines = [line for line in done.stderr.splitlines() if line.startswith("GUARD_STATS ")]
    if done.returncode or len(guard_lines) != 1:
        raise RuntimeError(done.stderr or "guarded query failed")
    rows = list(csv.DictReader(io.StringIO(done.stdout), delimiter="\t"))
    if any(row.get("page") == "f1r" or row.get("page", "").startswith("f84") for row in rows):
        raise RuntimeError("forbidden page materialized")
    return rows


def span_count(tokens: list[str], target: str) -> int:
    total = 0
    for start in range(len(tokens)):
        joined = ""
        for token in tokens[start:]:
            joined += token
            if joined == target:
                total += 1
                break
            if len(joined) >= len(target) or not target.startswith(joined):
                break
    return total


def independent_counts(token_rows, cross_rows, surfaces):
    cross = {row["locus"]: row for row in cross_rows}
    occurrence, exact, split, ordinal = Counter(), Counter(), Counter(), Counter()
    pages = {surface: set() for surface in surfaces}
    for row in sorted(token_rows, key=lambda item: (item["page"], item["locus"], int(item["token_index"]))):
        surface = row["eva"]
        if surface not in surfaces:
            continue
        occurrence[surface] += 1
        pages[surface].add(row["page"])
        ordinal[row["locus"], surface] += 1
        needed = ordinal[row["locus"], surface]
        direct = [cross[row["locus"]][field].split().count(surface) for field in ("zl3b_clean", "it2a_clean", "rf1b_clean")]
        normalized = [span_count(cross[row["locus"]][field].split(), surface) for field in ("zl3b_clean", "it2a_clean", "rf1b_clean")]
        exact[surface] += needed <= min(direct)
        split[surface] += needed <= min(normalized)
    return occurrence, exact, split, Counter({surface: len(value) for surface, value in pages.items()})


def main() -> int:
    passed: list[str] = []
    issues: list[str] = []

    def check(ok: object, name: str, detail: str = "") -> None:
        (passed if ok else issues).append(name if ok else f"{name}: {detail or 'condition failed'}")

    try:
        builder = load_builder()
        expected_outputs = (*builder.OUTPUT_NAMES, "RESULT.json")
        with tempfile.TemporaryDirectory(prefix="gdt647_validate_") as tmp:
            replay = Path(tmp)
            builder.build(replay)
            check({path.name for path in replay.iterdir()} == set(expected_outputs), "replay output set")
            for name in expected_outputs:
                check((ART / name).read_bytes() == (replay / name).read_bytes(), f"byte replay:{name}")
    except Exception as exc:
        issues.append(f"builder replay: {type(exc).__name__}: {exc}")
        builder = None
        expected_outputs = ()

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    result = json.loads((ART / "RESULT.json").read_text(encoding="utf-8"))
    check(manifest.get("experiment_id") == "GDT647", "manifest id")
    check(manifest.get("sealed_data") == {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"}, "manifest seals")
    check(manifest.get("validation") == {"artifact": str(BASE / "artifacts/VALIDATION.json"), "status": "PASS"}, "manifest validation")
    check(result.get("schema") == "GDT647_QUALITY_SUBDEGREE_FAMILY_MIGRATION_RESULT_V2", "result schema")
    check(result.get("status") == STATUS, "result status")
    check(result.get("content_sha256") == canonical_hash({k: value for k, value in result.items() if k != "content_sha256"}), "result hash")

    pages = {row["page"] for row in read_tsv(ART / "PAGE_ALLOWLIST.tsv")}
    check(len(pages) == 179 and "f1r" not in pages and not any(page.startswith("f84") for page in pages), "guarded pages")
    check((ART / "PAGE_ALLOWLIST.tsv").read_bytes() == (ROOT / G646_ALLOW).read_bytes(), "allowlist inheritance")
    token_rows = guarded_query(TOKENS, pages, "page,locus,token_index,eva")
    cross_rows = guarded_query(CROSS, pages, "page,locus,zl3b_clean,it2a_clean,rf1b_clean")

    deck = read_tsv(ART / "FAMILY_MIGRATION_DECK.tsv")
    surfaces = {row["surface"] for row in deck}
    check(len(deck) == len(surfaces) == 107, "107 unique observed surfaces")
    check(Counter(row["decision"] for row in deck) == EXPECTED_DECISIONS, "decision tiers")
    check(Counter(row["family"] for row in deck) == EXPECTED_FAMILIES, "family tiers")
    check([row["cell_id"] for row in deck] == [f"G647-C{index:02d}" for index in range(1, 108)], "ordered cell ids")
    check(not any(FILLER.search(row["new_meaning_de"]) for row in deck), "no generic filler meanings")
    occurrence, exact, split, page_count = independent_counts(token_rows, cross_rows, surfaces)
    for row in deck:
        surface = row["surface"]
        observed = (
            int(row["zl3b_occurrences"]), int(row["pages"]),
            int(row["reader_exact_occurrences"]), int(row["split_normalized_occurrences"]),
        )
        expected = (occurrence[surface], page_count[surface], exact[surface], split[surface])
        check(observed == expected, f"surface census:{surface}", repr(observed))
        check(row["reader_anchor"] == ("ALL_READER_EXACT" if exact[surface] else "ZL3B_READER_VARIANT_ONLY"), f"reader tier:{surface}")
    check(sum(occurrence.values()) == 5664 and sum(exact.values()) == 4141 and sum(split.values()) == 4156, "independent family totals")
    check({surface for surface in surfaces if exact[surface] == 0} == READER_UNSTABLE, "five reader-unstable surfaces")

    nulls = read_tsv(ART / "NULL_CELL_HOLDS.tsv")
    check(len(nulls) == 13 and {row["surface"] for row in nulls} == EXPECTED_NULL, "13 absent holds")
    check(not (surfaces & EXPECTED_NULL) and all(occurrence[surface] == 0 for surface in EXPECTED_NULL), "holds truly absent")
    boundary = read_tsv(ART / "AXIS_SCOPE_BOUNDARY.tsv")
    check(len(boundary) == 8 and Counter(row["decision"] for row in boundary) == Counter({"INCLUDE": 3, "EXCLUDE": 5}), "scope boundary")
    check({row["scope_id"] for row in boundary if row["decision"] == "EXCLUDE"} == {"CTH", "MATERIAL_HEADS", "REVERSED_COMPOUNDS", "OTHER_LADDERS", "OVERLONG_OR_REORDERED"}, "explicit exclusions")

    old_gloss_rows = read_tsv(ROOT / G646_GLOSSARY)
    gloss_rows = read_tsv(ART / "V24_EXACT_TOKEN_GLOSSARY.tsv")
    old_gloss = {row["surface"]: row for row in old_gloss_rows}
    glossary = {row["surface"]: row for row in gloss_rows}
    check(len(old_gloss_rows) == len(old_gloss) == 257 and len(gloss_rows) == len(glossary) == 347, "glossary 257 to 347")
    check(set(glossary) == set(old_gloss) | surfaces, "glossary exact target union")
    check(all(glossary[surface] == row for surface, row in old_gloss.items() if surface not in surfaces), "all out-of-scope glosses unchanged")
    if builder is not None:
        generated = {row["surface"]: row for row in builder.all_family_specs()}
        check(surfaces | EXPECTED_NULL == set(generated), "complete 120-cell generator")
        for row in deck:
            surface = row["surface"]
            check((row["composition"], row["new_meaning_de"]) == (generated[surface]["composition"], generated[surface]["working_meaning_de"]), f"generated semantics:{surface}")
            check(glossary[surface]["working_meaning_de"] == generated[surface]["working_meaning_de"], f"glossary semantics:{surface}")
    check(glossary["tcheey"]["working_meaning_de"] == "kalt und trocken am Ende des Grades", "tcheey retained identically")
    check(all(glossary[surface] == old_gloss[surface] for surface in ("cthy", "ly", "soysar", "qokeeedy", "choky", "cheaiin")), "named non-globalization controls")

    old_dictionary = read_tsv(ROOT / G646_DICTIONARY)
    dictionary = read_tsv(ART / "WORKING_DICTIONARY_V24.tsv")
    check(len(old_dictionary) == 304 and len(dictionary) == 410 and dictionary[:304] == old_dictionary, "dictionary append-only 304 to 410")
    overlay_surfaces = [row["entry"].split("@", 1)[0] for row in dictionary[304:]]
    check(len(overlay_surfaces) == len(set(overlay_surfaces)) == 106 and set(overlay_surfaces) == surfaces - {"tcheey"}, "106 exact-whole overlays")

    rounds = read_tsv(ART / "ROUND_COVERAGE_COUNTS.tsv")
    check(len(rounds) == 2, "two coverage states")
    observed_rounds = [{key: int(row[key]) for key in EXPECTED_BASE} for row in rounds]
    check(observed_rounds == [EXPECTED_BASE, EXPECTED_FINAL], "coverage round metrics", repr(observed_rounds))
    coverage = read_tsv(ART / "ALL_LINE_CONCRETE_COVERAGE_V24.tsv")
    complete = read_tsv(ART / "COMPLETE_PASSAGES_V24.tsv")
    one = read_tsv(ART / "ONE_UNKNOWN_PASSAGES_V24.tsv")
    check(len(coverage) == 4128 and sum(int(row["known_tokens"]) for row in coverage) == 13782 and sum(int(row["unknown_tokens"]) for row in coverage) == 18557, "V24 coverage")
    check(len(complete) == 77 and sum(int(row["strict_complete"]) for row in complete) == 42, "V24 complete deck")
    check(len(one) == 152 and sum(int(row["strict_eligible"]) for row in one) == 48, "V24 one-hole deck")
    new_complete = read_tsv(ART / "NEWLY_COMPLETED_LINES.tsv")
    new_one = read_tsv(ART / "NEWLY_EXPOSED_ONE_HOLE_LINES.tsv")
    check(len(new_complete) == 16 and sum(int(row["strict_complete"]) for row in new_complete) == 0, "16 nonstrict new complete lines")
    check(len(new_one) == 90 and sum(int(row["strict_eligible"]) for row in new_one) == 26, "90 new one-hole lines")
    affected = read_tsv(ART / "AFFECTED_PASSAGES.tsv")
    check(len(affected) == 2555 and sum(int(row["newly_known_positions"]) for row in affected) == 3431 and sum(int(row["meaning_revisions"]) for row in affected) == 2227, "passage impact")
    manual = read_tsv(ART / "MANUAL_PASSAGE_REALITY_CHECK.tsv")
    check(len(manual) == 15 and Counter(row["assessment"] for row in manual)["STRONG"] == 8, "manual reality check")
    check({"f114v.33", "f47v.4"} <= {row["locus"] for row in manual if row["assessment"] == "HARD_WARNING"}, "manual hard warnings retained")
    check(not any(FILLER.search(row["scoped_reading_de"]) for row in manual), "no filler in scoped readings")

    expected_result_migration = {
        "observed_cells": 107, "new_observed_wholes": 90,
        "new_all_reader_anchored_wholes": 86, "new_reader_warning_wholes": 4,
        "revised_exact_wholes": 16, "revised_all_reader_anchored_wholes": 15,
        "revised_reader_warning_wholes": 1, "retained_exact_wholes": 1,
        "target_occurrences": 5664, "reader_exact_occurrences": 4141,
        "split_normalized_occurrences": 4156, "surfaces_with_all_reader_anchor": 102,
        "reader_unstable_observed_surfaces": 5, "absent_cells_held": 13,
    }
    check(all(result.get("migration", {}).get(key) == value for key, value in expected_result_migration.items()), "result migration totals")
    check(result.get("coverage") == {"base": EXPECTED_BASE, "final": EXPECTED_FINAL}, "result coverage totals")
    check(result.get("passage_impact") == {
        "affected_lines": 2555, "base_complete_lines_touched": 28,
        "base_one_hole_lines_touched": 32, "manual_reality_check_lines": 15,
        "meaning_revision_positions": 2227, "newly_known_positions": 3431,
        "newly_completed_lines": 16, "newly_exposed_one_hole_lines": 90,
    }, "result passage totals")
    check(result.get("working_dictionary") == {
        "v23_entries": 304, "v24_entries": 410, "overlay_entries": 106,
        "v23_prefix_sha256": canonical_hash(old_dictionary),
        "v24_sha256": canonical_hash(dictionary), "base_glossary_surfaces": 257,
        "v24_glossary_surfaces": 347,
    }, "result dictionary totals")

    check(set(result.get("outputs", {})) == {str(BASE / "artifacts" / name) for name in expected_outputs if name != "RESULT.json"}, "result output set")
    for relative, digest in result.get("inputs", {}).items():
        check((ROOT / relative).is_file() and sha256(ROOT / relative) == digest, f"input hash:{relative}")
    for relative, digest in result.get("outputs", {}).items():
        check((ROOT / relative).is_file() and sha256(ROOT / relative) == digest, f"output hash:{relative}")
    for path in ART.glob("*.tsv"):
        rows = read_tsv(path)
        check(all(None not in row and all(value not in (None, "") for value in row.values()) for row in rows), f"complete TSV:{path.name}")
    check(all(row["page"] != "f1r" and not row["page"].startswith("f84") for row in coverage), "coverage privacy guard")

    status = "PASS" if not issues else "FAIL"
    validation_core = {
        "schema": "GDT647_VALIDATION_V1", "experiment_id": "GDT647",
        "status": status, "checks_passed": len(passed), "issues": issues,
        "result_sha256": sha256(ART / "RESULT.json"),
        "run_sha256": sha256(RUN),
        "validated_counts": {
            "observed_surfaces": len(deck), "target_occurrences": sum(occurrence.values()),
            "reader_exact_occurrences": sum(exact.values()), "held_absent_cells": len(nulls),
            "known_token_positions": sum(int(row["known_tokens"]) for row in coverage),
            "complete_lines": len(complete), "one_unknown_lines": len(one),
        },
    }
    validation = {**validation_core, "content_sha256": canonical_hash(validation_core)}
    VALIDATION.write_text(json.dumps(validation, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if issues:
        for issue in issues:
            print(f"FAIL {issue}", file=sys.stderr)
        return 1
    print(f"GDT647 validation PASS ({len(passed)} checks)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
