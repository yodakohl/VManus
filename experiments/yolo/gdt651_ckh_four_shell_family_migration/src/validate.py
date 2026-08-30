#!/usr/bin/env python3
"""Independent release validator for GDT651."""
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
BASE = Path("experiments/yolo/gdt651_ckh_four_shell_family_migration")
ART = ROOT / BASE / "artifacts"
RUN = ROOT / BASE / "src/run.py"
MANIFEST = ROOT / BASE / "experiment.json"
REPORT = ROOT / BASE / "REPORT.md"
VALIDATION = ART / "VALIDATION.json"
G650 = Path("experiments/yolo/gdt650_v26_strict_family_completion")
G650_ALLOW = G650 / "artifacts/PAGE_ALLOWLIST.tsv"
G650_GLOSSARY = G650 / "artifacts/V27_EXACT_TOKEN_GLOSSARY.tsv"
G650_DICTIONARY = G650 / "artifacts/WORKING_DICTIONARY_V27.tsv"
TOKENS = Path("transcription/voynich_zl3b_tokens.tsv")
CROSS = Path("transcription/voynich_cross_transcription_lines.tsv")

STATUS = "PASS_7_CKH_SISTER_WHOLES__V28_FOUR_SHELL_GRID"
TARGETS = {
    "checkhy": (46, 31, 43, 43, "trockenes Arzneikompositum am Gradanfang", "ch+E_ATTR+CKH_LEARNED+y", "STRONG_LEARNED_CKH_FAMILY"),
    "checkhey": (10, 9, 9, 9, "trockenes Arzneikompositum in der Gradmitte", "ch+E_ATTR+CKH_LEARNED+e+y", "STRONG_LEARNED_CKH_FAMILY"),
    "checkhdy": (1, 1, 1, 1, "trockenes Arzneikompositum am Gradanfang, abgeschlossen", "ch+E_ATTR+CKH_LEARNED+d+y", "PROVISIONAL_LOW_N_CKH_FAMILY"),
    "shckhy": (51, 25, 44, 45, "Arzneikompositum: feucht, Gradanfang", "sh+CKH_LEARNED+y", "STRONG_LEARNED_CKH_FAMILY"),
    "shckhey": (10, 9, 8, 8, "Arzneikompositum: feucht, Gradmitte", "sh+CKH_LEARNED+e+y", "STRONG_LEARNED_CKH_FAMILY"),
    "shckhdy": (1, 1, 1, 1, "Arzneikompositum: feucht, Gradanfang, abgeschlossen", "sh+CKH_LEARNED+d+y", "PROVISIONAL_LOW_N_CKH_FAMILY"),
    "shckhedy": (5, 4, 3, 3, "Arzneikompositum: feucht, Gradmitte, abgeschlossen", "sh+CKH_LEARNED+e+d+y", "PROVISIONAL_LOW_N_CKH_FAMILY"),
}
REVISIONS = {
    "chckhy": (126, 69, 115, 115, "Arzneikompositum: trocken, Gradanfang", "ch+CKH_LEARNED+y"),
    "chckhey": (29, 26, 25, 25, "Arzneikompositum: trocken, Gradmitte", "ch+CKH_LEARNED+e+y"),
    "chckheey": (1, 1, 1, 1, "Arzneikompositum: trocken, Gradende", "ch+CKH_LEARNED+ee+y"),
    "chckhdy": (12, 10, 7, 7, "Arzneikompositum: trocken, Gradanfang, abgeschlossen", "ch+CKH_LEARNED+d+y"),
    "chckhedy": (9, 9, 6, 6, "Arzneikompositum: trocken, Gradmitte, abgeschlossen", "ch+CKH_LEARNED+e+d+y"),
    "sheckhy": (33, 17, 24, 24, "feuchtes Arzneikompositum am Gradanfang", "sh+E_ATTR+CKH_LEARNED+y"),
    "sheckhey": (4, 4, 4, 4, "feuchtes Arzneikompositum in der Gradmitte", "sh+E_ATTR+CKH_LEARNED+e+y"),
    "sheckhedy": (4, 4, 3, 3, "feuchtes Arzneikompositum in der Gradmitte, abgeschlossen", "sh+E_ATTR+CKH_LEARNED+e+d+y"),
}
EXPECTED_FINAL = {
    "physical_lines": 4128, "known_token_positions": 14741,
    "unknown_token_positions": 17598, "complete_multi_token_lines": 107,
    "strict_complete_lines": 62, "one_unknown_lines": 159,
    "strict_one_unknown_lines": 40, "exact_glossary_surfaces": 379,
}
NEW_COMPLETE_LOCI = {"f30v.4", "f76v.33", "f80r.43", "f83r.27"}
STRICT_SOURCE_LOCI = {"f30v.4", "f80r.43"}
ABSENT_CELLS = {
    "chckheedy", "checkheey", "checkheedy", "shckheey",
    "shckheedy", "sheckheey", "sheckheedy",
}
FILLER = re.compile(
    r"arbeitsgut|arbeitschritt|arbeitsschritt|arbeitsmittel|arbeitsstoff|"
    r"arbeitsobjekt|werkzeug|produkt weiter|f.hre .* aus|leite .* weiter",
    re.IGNORECASE,
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def canonical_hash(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def load_builder():
    spec = importlib.util.spec_from_file_location("gdt651_builder_validation", RUN)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load GDT651 builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def guarded_query(path: Path, pages: set[str], columns: str) -> list[dict[str, str]]:
    command = [str(ROOT / "vmanus-exp"), "query-tsv", str(path), "--selector", "page"]
    for page in sorted(pages):
        command.extend(("--allow", page))
    command.extend(("--columns", columns, "--forbid-prefix", "f84", "--forbid-prefix", "f84r"))
    done = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    guards = [line for line in done.stderr.splitlines() if line.startswith("GUARD_STATS ")]
    if done.returncode or len(guards) != 1:
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
    occurrence, exact, normalized, ordinal = Counter(), Counter(), Counter(), Counter()
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
        spans = [span_count(cross[row["locus"]][field].split(), surface) for field in ("zl3b_clean", "it2a_clean", "rf1b_clean")]
        exact[surface] += needed <= min(direct)
        normalized[surface] += needed <= min(spans)
    return occurrence, exact, normalized, Counter({surface: len(value) for surface, value in pages.items()})


def main() -> int:
    passed: list[str] = []
    issues: list[str] = []

    def check(ok: object, name: str, detail: str = "") -> None:
        (passed if ok else issues).append(name if ok else f"{name}: {detail or 'condition failed'}")

    try:
        builder = load_builder()
        expected_outputs = (*builder.OUTPUT_NAMES, "RESULT.json")
        with tempfile.TemporaryDirectory(prefix="gdt651_validate_") as tmp:
            replay = Path(tmp)
            builder.build(replay)
            check({path.name for path in replay.iterdir()} == set(expected_outputs), "replay output set")
            for name in expected_outputs:
                check((ART / name).read_bytes() == (replay / name).read_bytes(), f"byte replay:{name}")
    except Exception as exc:
        issues.append(f"builder replay: {type(exc).__name__}: {exc}")

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    result = json.loads((ART / "RESULT.json").read_text(encoding="utf-8"))
    check(manifest.get("experiment_id") == "GDT651", "manifest id")
    check(manifest.get("sealed_data") == {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"}, "manifest seals")
    check(manifest.get("validation") == {"artifact": str(BASE / "artifacts/VALIDATION.json"), "status": "PASS"}, "manifest validation")
    check(result.get("schema") == "GDT651_CKH_FOUR_SHELL_FAMILY_MIGRATION_RESULT_V1", "result schema")
    check(result.get("status") == STATUS, "result status")
    check(result.get("content_sha256") == canonical_hash({key: value for key, value in result.items() if key != "content_sha256"}), "result hash")

    pages = {row["page"] for row in read_tsv(ART / "PAGE_ALLOWLIST.tsv")}
    check(len(pages) == 179 and "f1r" not in pages and not any(page.startswith("f84") for page in pages), "guarded pages")
    check((ART / "PAGE_ALLOWLIST.tsv").read_bytes() == (ROOT / G650_ALLOW).read_bytes(), "allowlist inheritance")
    token_rows = guarded_query(TOKENS, pages, "page,locus,token_index,eva")
    cross_rows = guarded_query(CROSS, pages, "page,locus,zl3b_clean,it2a_clean,rf1b_clean")
    all_surfaces = set(TARGETS) | set(REVISIONS)
    occurrence, exact, normalized, page_count = independent_counts(token_rows, cross_rows, all_surfaces)

    deck = read_tsv(ART / "TARGET_DECISION_DECK.tsv")
    deck_by_surface = {row["surface"]: row for row in deck}
    check(len(deck) == len(deck_by_surface) == 7 and set(deck_by_surface) == set(TARGETS), "seven target rows")
    check([row["candidate_id"] for row in deck] == [f"G651-C{index:02d}" for index in range(1, 8)], "ordered candidate ids")
    check(Counter(row["acceptance_tier"] for row in deck) == Counter({"STRONG_LEARNED_CKH_FAMILY": 4, "PROVISIONAL_LOW_N_CKH_FAMILY": 3}), "tier counts")
    for surface, expected in TARGETS.items():
        row = deck_by_surface[surface]
        observed = (occurrence[surface], page_count[surface], exact[surface], normalized[surface])
        check(observed == expected[:4], f"independent target census:{surface}", repr(observed))
        check((int(row["occurrences"]), int(row["pages"]), int(row["reader_exact_occurrences"]), int(row["split_normalized_occurrences"])) == expected[:4], f"deck census:{surface}")
        check((row["working_meaning_de"], row["composition"], row["acceptance_tier"], row["decision"]) == (expected[4], expected[5], expected[6], "ACCEPT_V28_EXACT_WHOLE"), f"target semantics:{surface}")
    check(sum(occurrence[surface] for surface in TARGETS) == 124 and sum(exact[surface] for surface in TARGETS) == 109 and sum(normalized[surface] for surface in TARGETS) == 110, "target totals")
    check(not any(FILLER.search(row["working_meaning_de"]) for row in deck), "no target filler")

    revisions = read_tsv(ART / "REVISED_EXISTING_WHOLE_DEFAULTS.tsv")
    revision_by_surface = {row["surface"]: row for row in revisions}
    check(len(revisions) == len(revision_by_surface) == 8 and set(revision_by_surface) == set(REVISIONS), "eight revision rows")
    for surface, expected in REVISIONS.items():
        row = revision_by_surface[surface]
        observed = (occurrence[surface], page_count[surface], exact[surface], normalized[surface])
        check(observed == expected[:4], f"independent revision census:{surface}", repr(observed))
        check((int(row["occurrences"]), int(row["pages"]), int(row["reader_exact_occurrences"]), int(row["split_normalized_occurrences"])) == expected[:4], f"revision census:{surface}")
        check((row["new_working_meaning_de"], row["composition"], row["decision"]) == (expected[4], expected[5], "REVISE_V28_FAMILY_DEFAULT"), f"revision semantics:{surface}")
        check("Arzneimischung" in row["old_working_meaning_de"] and "Arzneimischung" not in row["new_working_meaning_de"], f"unsupported noun removed:{surface}")
    check(sum(occurrence[surface] for surface in REVISIONS) == 218, "revision occurrence total")

    family = read_tsv(ART / "FAMILY_EVIDENCE_ATLAS.tsv")
    family_by_surface = {row["surface"]: row for row in family}
    check(len(family) == len(family_by_surface) == 24, "complete 24-cell family grid")
    check(sum(int(row["zl3b_occurrences"]) > 0 for row in family) == 17 and sum(int(row["reader_exact_occurrences"]) > 0 for row in family) == 15, "17 observed and 15 exact cells")
    check(family_by_surface["checkhedy"]["final_status"] == "HELD_ZERO_EXACT" and family_by_surface["sheckhdy"]["final_status"] == "HELD_ZERO_EXACT", "observed zero-exact cells held")
    check(all(family_by_surface[surface]["final_status"] == "ABSENT_HOLD" for surface in ABSENT_CELLS), "seven absent cells held")

    bridges = read_tsv(ART / "BOUNDARY_BRIDGE_ATLAS.tsv")
    check(len(bridges) == 6 and len({row["bridge_id"] for row in bridges}) == 6, "six sister bridges")
    check(all(row["zl3b_line"] and row["it2a_line"] and row["rf1b_line"] for row in bridges), "bridge reader lines populated")
    risks = read_tsv(ART / "RISK_AND_RIVAL_REGISTER.tsv")
    check(len(risks) == 7 and {row["surface"] for row in risks} == set(TARGETS), "complete risk register")
    check(all(row["rival_de"] and row["strongest_counterargument"] and row["replacement_trigger"] for row in risks), "risks retain rivals")

    audits = read_tsv(ART / "ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv")
    check(len(audits) == 124 and len({row["audit_id"] for row in audits}) == 124, "124 unique occurrence audits")
    check(Counter(row["surface"] for row in audits) == Counter({surface: values[0] for surface, values in TARGETS.items()}), "audit surface counts")
    check(sum(int(row["reader_exact"]) for row in audits) == 109 and sum(int(row["split_normalized"]) for row in audits) == 110, "audit reader totals")
    check(sum(int(row["hard_collision"]) for row in audits) == 0, "no recorded hard collision")
    variants = read_tsv(ART / "READER_VARIANT_AUDIT.tsv")
    check(len(variants) == 15 and Counter(row["reader_support"] for row in variants) == Counter({"READER_VARIANT": 14, "ALL_THREE_SPLIT_NORMALIZED": 1}), "14 reader variants plus one split normalization")

    old_gloss_rows = read_tsv(ROOT / G650_GLOSSARY)
    gloss_rows = read_tsv(ART / "V28_EXACT_TOKEN_GLOSSARY.tsv")
    old_gloss, glossary = {row["surface"]: row for row in old_gloss_rows}, {row["surface"]: row for row in gloss_rows}
    check(len(old_gloss) == 372 and len(glossary) == 379 and set(glossary) == set(old_gloss) | set(TARGETS), "glossary 372 to 379")
    check(all(glossary[surface] == row for surface, row in old_gloss.items() if surface not in REVISIONS), "non-CKH base glossary unchanged")
    check(all(glossary[surface]["working_meaning_de"] == REVISIONS[surface][4] for surface in REVISIONS), "revision glossary meanings")
    check(all(glossary[surface]["working_meaning_de"] == TARGETS[surface][4] for surface in TARGETS), "target glossary meanings")

    old_dictionary = read_tsv(ROOT / G650_DICTIONARY)
    dictionary = read_tsv(ART / "WORKING_DICTIONARY_V28.tsv")
    check(len(old_dictionary) == 435 and len(dictionary) == 450 and dictionary[:435] == old_dictionary, "dictionary append-only 435 to 450")
    revision_tail = dictionary[435:443]
    target_tail = dictionary[443:]
    check([row["entry"].split("@", 1)[0] for row in revision_tail] == list(REVISIONS), "eight ordered dictionary revisions")
    check([row["entry"].split("@", 1)[0] for row in target_tail] == list(TARGETS), "seven ordered dictionary additions")
    check(all("E_ATTR" not in row["entry"] and "CKH_LEARNED" not in row["entry"] for row in dictionary[435:]), "no free family component exported")

    coverage = read_tsv(ART / "ALL_LINE_CONCRETE_COVERAGE_V28.tsv")
    complete = read_tsv(ART / "COMPLETE_PASSAGES_V28.tsv")
    one = read_tsv(ART / "ONE_UNKNOWN_PASSAGES_V28.tsv")
    observed_final = {
        "physical_lines": len(coverage), "known_token_positions": sum(int(row["known_tokens"]) for row in coverage),
        "unknown_token_positions": sum(int(row["unknown_tokens"]) for row in coverage),
        "complete_multi_token_lines": len(complete), "strict_complete_lines": sum(int(row["strict_complete"]) for row in complete),
        "one_unknown_lines": len(one), "strict_one_unknown_lines": sum(int(row["strict_eligible"]) for row in one),
        "exact_glossary_surfaces": len(glossary),
    }
    check(observed_final == EXPECTED_FINAL, "V28 coverage metrics", repr(observed_final))
    new_complete = read_tsv(ART / "NEWLY_COMPLETED_LINES.tsv")
    check(len(new_complete) == 4 and {row["locus"] for row in new_complete} == NEW_COMPLETE_LOCI, "four new complete loci")
    check(sum(int(row["strict_complete"]) for row in new_complete) == 3, "three newly strict lines")
    newly_exposed = read_tsv(ART / "NEWLY_EXPOSED_ONE_HOLE_LINES.tsv")
    check(len(newly_exposed) == 9, "nine newly exposed one-hole events")

    reality = read_tsv(ART / "SOURCE_PASSAGE_REALITY_CHECK.tsv")
    check(len(reality) == 2 and {row["locus"] for row in reality} == STRICT_SOURCE_LOCI, "two strict CHECKHY source readings")
    check(all(row["surface"] == "checkhy" and row["strict_complete"] == "1" and "[" not in row["tokenwise_translation_de"] for row in reality), "strict sources fully rendered")
    affected = read_tsv(ART / "AFFECTED_LINE_TRANSLATIONS.tsv")
    unchanged = [row for row in affected if row["v27_tokenwise_de"] == row["v28_tokenwise_de"]]
    check(len(affected) == 308 and not unchanged, "308 affected lines, all changed")

    target_result = result.get("target_run", {})
    coverage_result = result.get("coverage", {})
    revision_result = result.get("family_revision", {})
    check(target_result.get("accepted_surfaces") == [row["surface"] for row in deck], "result target order")
    check((target_result.get("audited_occurrences"), target_result.get("all_reader_exact_occurrences"), target_result.get("split_normalized_occurrences")) == (124, 109, 110), "result audit totals")
    check(target_result.get("strict_v27_holes_closed") == 2 and target_result.get("hard_collisions") == 0, "result closure and collision counts")
    check(revision_result.get("revised_existing_wholes") == 8 and revision_result.get("revised_occurrences") == 218, "result family revision")
    check(coverage_result.get("final") == EXPECTED_FINAL and coverage_result.get("affected_lines") == 308, "result coverage")
    check(result.get("working_dictionary", {}).get("v28_entries") == 450, "result dictionary")

    report_text = REPORT.read_text(encoding="utf-8") if REPORT.exists() else ""
    for needle in ("checkhy", "shckhedy", "Arzneikompositum", "E_ATTR", "14.741", "308", "explor"):
        check(needle.lower() in report_text.lower(), f"report contains:{needle}")

    validation = {
        "schema": "GDT651_VALIDATION_V1", "experiment_id": "GDT651",
        "status": "PASS" if not issues else "FAIL", "checks_passed": len(passed),
        "checks_failed": len(issues), "passed": passed, "issues": issues,
    }
    VALIDATION.write_text(json.dumps(validation, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if issues:
        print(f"GDT651 validation FAIL: {len(issues)} issue(s)")
        for issue in issues:
            print(f"- {issue}")
        return 1
    print(f"GDT651 validation PASS: {len(passed)} checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
