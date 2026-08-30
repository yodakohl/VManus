#!/usr/bin/env python3
"""Independent release validator for GDT650."""
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
BASE = Path("experiments/yolo/gdt650_v26_strict_family_completion")
ART = ROOT / BASE / "artifacts"
RUN = ROOT / BASE / "src/run.py"
MANIFEST = ROOT / BASE / "experiment.json"
REPORT = ROOT / BASE / "REPORT.md"
VALIDATION = ART / "VALIDATION.json"
G649 = Path("experiments/yolo/gdt649_strict_v25_hole_completion")
G649_ALLOW = G649 / "artifacts/PAGE_ALLOWLIST.tsv"
G649_GLOSSARY = G649 / "artifacts/V26_EXACT_TOKEN_GLOSSARY.tsv"
G649_DICTIONARY = G649 / "artifacts/WORKING_DICTIONARY_V26.tsv"
TOKENS = Path("transcription/voynich_zl3b_tokens.tsv")
CROSS = Path("transcription/voynich_cross_transcription_lines.tsv")

STATUS = "PASS_7_EXACT_WHOLES__V27_FIVE_STRICT_FAMILIES_CLOSED"
TARGETS = {
    "otcho": (7, 7, 6, 6, "kalt-trockene Zubereitung", "o+(t+ch)+o", "STRONG_ATTESTED_FAMILY"),
    "cholor": (5, 5, 4, 4, "trockene Zutat", "chol+or", "PROVISIONAL_BOUNDARY_FAMILY"),
    "sheo": (37, 29, 28, 28, "Feuchtzubereitung", "sh+e+o", "STRONG_COMPOSITIONAL_SHELL"),
    "ycheol": (11, 10, 8, 9, "trockener Drogenstoff dieser Droge", "y|(ch+e+ol)", "STRONG_LOCAL_ENTRY_FAMILY"),
    "sheckhy": (33, 17, 24, 24, "feuchte Arzneimischung, Anfangsgrad, gebunden", "sh+e+CKH_LEARNED+y", "EXPLORATORY_LEARNED_CKH_HEAD"),
    "sheckhey": (4, 4, 4, 4, "feuchte Arzneimischung, Mittelgrad, gebunden", "sh+e+CKH_LEARNED+e+y", "EXPLORATORY_LEARNED_CKH_HEAD"),
    "sheckhedy": (4, 4, 3, 3, "feuchte Arzneimischung, Mittelgrad, gebunden und abgeschlossen", "sh+e+CKH_LEARNED+e+d+y", "EXPLORATORY_LEARNED_CKH_HEAD"),
}
EXPECTED_FINAL = {
    "physical_lines": 4128, "known_token_positions": 14617,
    "unknown_token_positions": 17722, "complete_multi_token_lines": 103,
    "strict_complete_lines": 59, "one_unknown_lines": 153,
    "strict_one_unknown_lines": 41, "exact_glossary_surfaces": 372,
}
NEW_COMPLETE_LOCI = {
    "f10r.8", "f14r.7", "f32r.13", "f81r.23",
    "f85r2.4", "f103r.23", "f108r.34",
}
STRICT_SOURCES = {
    "otcho": "f14r.7", "cholor": "f10r.8", "sheo": "f85r2.4",
    "ycheol": "f108r.34", "sheckhy": "f103r.23",
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
    spec = importlib.util.spec_from_file_location("gdt650_builder_validation", RUN)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load GDT650 builder")
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
        with tempfile.TemporaryDirectory(prefix="gdt650_validate_") as tmp:
            replay = Path(tmp)
            builder.build(replay)
            check({path.name for path in replay.iterdir()} == set(expected_outputs), "replay output set")
            for name in expected_outputs:
                check((ART / name).read_bytes() == (replay / name).read_bytes(), f"byte replay:{name}")
    except Exception as exc:
        issues.append(f"builder replay: {type(exc).__name__}: {exc}")
        builder = None

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    result = json.loads((ART / "RESULT.json").read_text(encoding="utf-8"))
    check(manifest.get("experiment_id") == "GDT650", "manifest id")
    check(manifest.get("sealed_data") == {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"}, "manifest seals")
    check(manifest.get("validation") == {"artifact": str(BASE / "artifacts/VALIDATION.json"), "status": "PASS"}, "manifest validation")
    check(result.get("schema") == "GDT650_V26_STRICT_FAMILY_COMPLETION_RESULT_V1", "result schema")
    check(result.get("status") == STATUS, "result status")
    check(result.get("content_sha256") == canonical_hash({key: value for key, value in result.items() if key != "content_sha256"}), "result hash")

    pages = {row["page"] for row in read_tsv(ART / "PAGE_ALLOWLIST.tsv")}
    check(len(pages) == 179 and "f1r" not in pages and not any(page.startswith("f84") for page in pages), "guarded pages")
    check((ART / "PAGE_ALLOWLIST.tsv").read_bytes() == (ROOT / G649_ALLOW).read_bytes(), "allowlist inheritance")
    token_rows = guarded_query(TOKENS, pages, "page,locus,token_index,eva")
    cross_rows = guarded_query(CROSS, pages, "page,locus,zl3b_clean,it2a_clean,rf1b_clean")
    occurrence, exact, normalized, page_count = independent_counts(token_rows, cross_rows, set(TARGETS))

    deck = read_tsv(ART / "TARGET_DECISION_DECK.tsv")
    deck_by_surface = {row["surface"]: row for row in deck}
    check(len(deck) == len(deck_by_surface) == 7 and set(deck_by_surface) == set(TARGETS), "seven target rows")
    check([row["candidate_id"] for row in deck] == [f"G650-C{index:02d}" for index in range(1, 8)], "ordered candidate ids")
    check(Counter(row["acceptance_tier"] for row in deck) == Counter({
        "STRONG_ATTESTED_FAMILY": 1, "PROVISIONAL_BOUNDARY_FAMILY": 1,
        "STRONG_COMPOSITIONAL_SHELL": 1, "STRONG_LOCAL_ENTRY_FAMILY": 1,
        "EXPLORATORY_LEARNED_CKH_HEAD": 3,
    }), "tier counts")
    for surface, expected in TARGETS.items():
        occ, pages_expected, exact_expected, norm_expected, meaning, parse, tier = expected
        row = deck_by_surface[surface]
        observed = (occurrence[surface], page_count[surface], exact[surface], normalized[surface])
        check(observed == expected[:4], f"independent target census:{surface}", repr(observed))
        check((int(row["occurrences"]), int(row["pages"]), int(row["reader_exact_occurrences"]), int(row["split_normalized_occurrences"])) == expected[:4], f"deck census:{surface}")
        check((row["working_meaning_de"], row["composition"], row["acceptance_tier"], row["decision"]) == (meaning, parse, tier, "ACCEPT_V27_EXACT_WHOLE"), f"target semantics:{surface}")
    check(sum(occurrence.values()) == 101 and sum(exact.values()) == 77 and sum(normalized.values()) == 78, "target totals")
    check(not any(FILLER.search(row["working_meaning_de"]) for row in deck), "no target filler")
    check("sheckhdy" not in deck_by_surface and "sheckheey" not in deck_by_surface and "sheckheedy" not in deck_by_surface, "held cells outside targets")
    check(all("sh+e+CKH_LEARNED" in row["composition"] for row in deck if row["surface"].startswith("sheckh")), "literal SH E CKH order")

    family = read_tsv(ART / "FAMILY_EVIDENCE_ATLAS.tsv")
    check(len(family) == 34 and Counter(row["family"] for row in family) == Counter({
        "OTCHO_COLD_DRY_PREPARATION": 9, "CHOL_OR_FUSED_INGREDIENT": 7,
        "SH_E_O_PREPARATION_SHELL": 4, "LOCAL_Y_CH_E_OL_ENTRY": 4,
        "SH_E_CKH_SUBDEGREE": 10,
    }), "family atlas rows")
    family_by_surface = {row["surface"]: row for row in family}
    check(family_by_surface["sheckhdy"]["final_status"] == "HELD_ZERO_EXACT", "reader-unstable SHECKHDY held")
    check(family_by_surface["sheckheey"]["final_status"] == "ABSENT_HOLD" and family_by_surface["sheckheedy"]["final_status"] == "ABSENT_HOLD", "absent SHECKH cells held")

    bridges = read_tsv(ART / "BOUNDARY_BRIDGE_ATLAS.tsv")
    check(len(bridges) == 16 and len({row["bridge_id"] for row in bridges}) == 16, "sixteen boundary bridges")
    check(Counter(row["family"] for row in bridges) == Counter({
        "OTCHO_COLD_DRY_PREPARATION": 2, "CHOL_OR_FUSED_INGREDIENT": 6,
        "LOCAL_Y_CH_E_OL_ENTRY": 6, "SH_E_CKH_SUBDEGREE": 2,
    }), "bridge family counts")
    check(all(row["zl3b_line"] and row["it2a_line"] and row["rf1b_line"] for row in bridges), "bridge reader lines populated")

    risks = read_tsv(ART / "RISK_AND_RIVAL_REGISTER.tsv")
    check(len(risks) == 7 and {row["surface"] for row in risks} == set(TARGETS), "complete risk register")
    check(all(row["rival_de"] and row["strongest_counterargument"] and row["replacement_trigger"] for row in risks), "risks retain rivals")

    audits = read_tsv(ART / "ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv")
    check(len(audits) == 101 and len({row["audit_id"] for row in audits}) == 101, "101 unique occurrence audits")
    check(Counter(row["surface"] for row in audits) == Counter({surface: values[0] for surface, values in TARGETS.items()}), "audit surface counts")
    check(sum(int(row["reader_exact"]) for row in audits) == 77 and sum(int(row["split_normalized"]) for row in audits) == 78, "audit reader totals")
    check(sum(int(row["hard_collision"]) for row in audits) == 0, "no recorded hard collision")
    variants = read_tsv(ART / "READER_VARIANT_AUDIT.tsv")
    check(len(variants) == 24 and Counter(row["reader_support"] for row in variants) == Counter({
        "READER_VARIANT": 23, "ALL_THREE_SPLIT_NORMALIZED": 1,
    }), "23 reader variants plus one split normalization")

    old_gloss_rows = read_tsv(ROOT / G649_GLOSSARY)
    gloss_rows = read_tsv(ART / "V27_EXACT_TOKEN_GLOSSARY.tsv")
    old_gloss, glossary = {row["surface"]: row for row in old_gloss_rows}, {row["surface"]: row for row in gloss_rows}
    check(len(old_gloss) == 365 and len(glossary) == 372 and set(glossary) == set(old_gloss) | set(TARGETS), "glossary 365 to 372")
    check(all(glossary[surface] == row for surface, row in old_gloss.items()), "base glossary unchanged")
    check(all(glossary[surface]["working_meaning_de"] == TARGETS[surface][4] for surface in TARGETS), "target glossary meanings")

    old_dictionary = read_tsv(ROOT / G649_DICTIONARY)
    dictionary = read_tsv(ART / "WORKING_DICTIONARY_V27.tsv")
    check(len(old_dictionary) == 428 and len(dictionary) == 435 and dictionary[:428] == old_dictionary, "dictionary append-only 428 to 435")
    tail_surfaces = [row["entry"].split("@", 1)[0] for row in dictionary[428:]]
    check(set(tail_surfaces) == set(TARGETS) and len(tail_surfaces) == len(set(tail_surfaces)), "seven dictionary overlays")

    coverage = read_tsv(ART / "ALL_LINE_CONCRETE_COVERAGE_V27.tsv")
    complete = read_tsv(ART / "COMPLETE_PASSAGES_V27.tsv")
    one = read_tsv(ART / "ONE_UNKNOWN_PASSAGES_V27.tsv")
    observed_final = {
        "physical_lines": len(coverage), "known_token_positions": sum(int(row["known_tokens"]) for row in coverage),
        "unknown_token_positions": sum(int(row["unknown_tokens"]) for row in coverage),
        "complete_multi_token_lines": len(complete), "strict_complete_lines": sum(int(row["strict_complete"]) for row in complete),
        "one_unknown_lines": len(one), "strict_one_unknown_lines": sum(int(row["strict_eligible"]) for row in one),
        "exact_glossary_surfaces": len(glossary),
    }
    check(observed_final == EXPECTED_FINAL, "V27 coverage metrics", repr(observed_final))
    new_complete = read_tsv(ART / "NEWLY_COMPLETED_LINES.tsv")
    check(len(new_complete) == 7 and {row["locus"] for row in new_complete} == NEW_COMPLETE_LOCI, "seven new complete loci")
    check(sum(int(row["strict_complete"]) for row in new_complete) == 6, "six newly strict lines")
    newly_exposed = read_tsv(ART / "NEWLY_EXPOSED_ONE_HOLE_LINES.tsv")
    check(len(newly_exposed) == 2, "two newly exposed one-hole events")

    reality = {row["surface"]: row for row in read_tsv(ART / "SOURCE_PASSAGE_REALITY_CHECK.tsv")}
    check(len(reality) == 5 and {surface: row["locus"] for surface, row in reality.items()} == STRICT_SOURCES, "five strict source readings")
    check(all(row["strict_complete"] == "1" and "[" not in row["tokenwise_translation_de"] for row in reality.values()), "strict sources fully rendered")
    affected = read_tsv(ART / "AFFECTED_LINE_TRANSLATIONS.tsv")
    unchanged = [row for row in affected if row["v26_tokenwise_de"] == row["v27_tokenwise_de"]]
    check(len(affected) == 97 and not unchanged, "97 affected lines, all changed")

    target_result = result.get("target_run", {})
    coverage_result = result.get("coverage", {})
    check(target_result.get("accepted_surfaces") == [row["surface"] for row in deck], "result target order")
    check((target_result.get("audited_occurrences"), target_result.get("all_reader_exact_occurrences"), target_result.get("split_normalized_occurrences")) == (101, 77, 78), "result audit totals")
    check(target_result.get("strict_v26_holes_closed") == 5 and target_result.get("hard_collisions") == 0, "result closure and collision counts")
    check(coverage_result.get("final") == EXPECTED_FINAL and coverage_result.get("affected_lines") == 97, "result coverage")
    check(result.get("working_dictionary", {}).get("v27_entries") == 435, "result dictionary")

    report_text = REPORT.read_text(encoding="utf-8") if REPORT.exists() else ""
    for needle in ("otcho", "cholor", "sheo", "ycheol", "sheckhy", "101", "14.617", "explor"):
        check(needle.lower() in report_text.lower(), f"report contains:{needle}")

    validation = {
        "schema": "GDT650_VALIDATION_V1", "experiment_id": "GDT650",
        "status": "PASS" if not issues else "FAIL", "checks_passed": len(passed),
        "checks_failed": len(issues), "passed": passed, "issues": issues,
    }
    VALIDATION.write_text(json.dumps(validation, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if issues:
        print(f"GDT650 validation FAIL: {len(issues)} issue(s)")
        for issue in issues:
            print(f"- {issue}")
        return 1
    print(f"GDT650 validation PASS: {len(passed)} checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
