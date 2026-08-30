#!/usr/bin/env python3
"""Independent release validator for GDT652."""
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
BASE = Path("experiments/yolo/gdt652_strict_v28_frontier_completion")
ART = ROOT / BASE / "artifacts"
RUN = ROOT / BASE / "src/run.py"
MANIFEST = ROOT / BASE / "experiment.json"
REPORT = ROOT / BASE / "REPORT.md"
VALIDATION = ART / "VALIDATION.json"
G651 = Path("experiments/yolo/gdt651_ckh_four_shell_family_migration")
G651_ALLOW = G651 / "artifacts/PAGE_ALLOWLIST.tsv"
G651_GLOSSARY = G651 / "artifacts/V28_EXACT_TOKEN_GLOSSARY.tsv"
G651_DICTIONARY = G651 / "artifacts/WORKING_DICTIONARY_V28.tsv"
TOKENS = Path("transcription/voynich_zl3b_tokens.tsv")
CROSS = Path("transcription/voynich_cross_transcription_lines.tsv")

STATUS = "PASS_35_EXACT_WHOLES__V29_PREPARATION_AND_MATERIA_GRIDS"
EXPECTED_COUNTS = {
    "ckhy": (34, 32, 25, 25),
    "ckhey": (22, 16, 20, 20),
    "ckheey": (8, 8, 8, 8),
    "ckhdy": (4, 4, 1, 1),
    "ckhedy": (2, 2, 1, 1),
    "ockhy": (6, 6, 6, 6),
    "ockhey": (7, 7, 5, 5),
    "ockhedy": (5, 5, 3, 3),
    "chockhy": (18, 18, 18, 18),
    "chockhey": (4, 4, 3, 3),
    "chockhedy": (1, 1, 1, 1),
    "cheockhy": (8, 7, 7, 7),
    "cheockhey": (1, 1, 1, 1),
    "shockhy": (4, 4, 4, 4),
    "shockhey": (3, 3, 3, 3),
    "sheockhy": (2, 2, 2, 2),
    "sheockhey": (2, 2, 1, 2),
    "chokey": (4, 4, 4, 4),
    "chokeey": (10, 9, 9, 9),
    "chokedy": (4, 3, 2, 2),
    "chokeedy": (2, 2, 2, 2),
    "cheoky": (6, 6, 6, 6),
    "cheokey": (2, 2, 2, 2),
    "cheokeey": (4, 4, 4, 4),
    "cheokedy": (2, 2, 1, 1),
    "shoky": (6, 6, 6, 6),
    "shokey": (3, 3, 2, 2),
    "shokeey": (2, 2, 1, 2),
    "sheoky": (7, 7, 5, 5),
    "sheokey": (2, 2, 2, 2),
    "sheokeedy": (1, 1, 1, 1),
    "opal": (6, 5, 6, 6),
    "osal": (3, 3, 2, 2),
    "oral": (10, 10, 6, 7),
    "olal": (5, 5, 5, 5),
}
FAMILIES = {
    "QUALITY_NEUTRAL_CKH_GRID": {"ckhy", "ckhey", "ckheey", "ckhdy", "ckhedy"},
    "O_PREP_CKH_GRID": {"ockhy", "ockhey", "ockhedy"},
    "QUALIFIED_O_PREP_CKH_GRID": {
        "chockhy", "chockhey", "chockhedy", "cheockhy", "cheockhey",
        "shockhy", "shockhey", "sheockhy", "sheockhey",
    },
    "QUALIFIED_O_PREP_K_GRID": {
        "chokey", "chokeey", "chokedy", "chokeedy", "cheoky", "cheokey",
        "cheokeey", "cheokedy", "shoky", "shokey", "shokeey", "sheoky",
        "sheokey", "sheokeedy",
    },
    "O_PREP_MATERIA_AL_GRID": {"opal", "osal", "oral", "olal"},
}
KEY_MEANINGS = {
    "ckhy": "Arzneikompositum am Gradanfang",
    "ockhy": "Ansatz eines Arzneikompositums am Gradanfang",
    "cheockhy": "trocken angesetztes Arzneikompositum am Gradanfang",
    "chokey": "heiß-trockener Ansatz in der Gradmitte",
    "cheokeey": "trocken angesetzte heiße Zubereitung am Gradende",
    "sheokeedy": "feucht angesetzte heiße Zubereitung am Gradende, abgeschlossen",
    "opal": "Ansatz aus Pulverrohstoff, Form I",
    "osal": "Ansatz aus Saatrohstoff, Form I",
    "oral": "Ansatz aus Wurzelrohstoff, Form I",
    "olal": "Ansatz aus Holzrohstoff, Form I",
}
EXPECTED_FINAL = {
    "physical_lines": 4128, "known_token_positions": 14951,
    "unknown_token_positions": 17388, "complete_multi_token_lines": 113,
    "strict_complete_lines": 67, "one_unknown_lines": 165,
    "strict_one_unknown_lines": 39, "exact_glossary_surfaces": 414,
}
NEW_COMPLETE_LOCI = {"f9v.12", "f107v.7", "f27r.12", "f37v.15", "f42v.15", "f75v.50"}
STRICT_SOURCE_LOCI = {"f9v.12", "f107v.7", "f27r.12", "f42v.15", "f75v.50"}
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
    spec = importlib.util.spec_from_file_location("gdt652_builder_validation", RUN)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load GDT652 builder")
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
        with tempfile.TemporaryDirectory(prefix="gdt652_validate_") as tmp:
            replay = Path(tmp)
            builder.build(replay)
            check({path.name for path in replay.iterdir()} == set(expected_outputs), "replay output set")
            for name in expected_outputs:
                check((ART / name).read_bytes() == (replay / name).read_bytes(), f"byte replay:{name}")
    except Exception as exc:
        issues.append(f"builder replay: {type(exc).__name__}: {exc}")

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    result = json.loads((ART / "RESULT.json").read_text(encoding="utf-8"))
    check(manifest.get("experiment_id") == "GDT652", "manifest id")
    check(manifest.get("sealed_data") == {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"}, "manifest seals")
    check(manifest.get("validation") == {"artifact": str(BASE / "artifacts/VALIDATION.json"), "status": "PASS"}, "manifest validation")
    check(result.get("schema") == "GDT652_PREPARATION_GRID_MIGRATION_RESULT_V2", "result schema")
    check(result.get("status") == STATUS, "result status")
    check(result.get("content_sha256") == canonical_hash({key: value for key, value in result.items() if key != "content_sha256"}), "result hash")

    pages = {row["page"] for row in read_tsv(ART / "PAGE_ALLOWLIST.tsv")}
    check(len(pages) == 179 and "f1r" not in pages and not any(page.startswith("f84") for page in pages), "guarded pages")
    check((ART / "PAGE_ALLOWLIST.tsv").read_bytes() == (ROOT / G651_ALLOW).read_bytes(), "allowlist inheritance")
    token_rows = guarded_query(TOKENS, pages, "page,locus,token_index,eva")
    cross_rows = guarded_query(CROSS, pages, "page,locus,zl3b_clean,it2a_clean,rf1b_clean")
    occurrence, exact, normalized, page_count = independent_counts(token_rows, cross_rows, EXPECTED_COUNTS)

    deck = read_tsv(ART / "TARGET_DECISION_DECK.tsv")
    deck_by_surface = {row["surface"]: row for row in deck}
    check(len(deck) == len(deck_by_surface) == 35 and set(deck_by_surface) == set(EXPECTED_COUNTS), "35 target rows")
    check([row["candidate_id"] for row in deck] == [f"G652-C{index:02d}" for index in range(1, 36)], "ordered candidate ids")
    for surface, expected in EXPECTED_COUNTS.items():
        row = deck_by_surface[surface]
        observed = (occurrence[surface], page_count[surface], exact[surface], normalized[surface])
        check(observed == expected, f"independent target census:{surface}", repr(observed))
        deck_counts = tuple(int(row[field]) for field in ("occurrences", "pages", "reader_exact_occurrences", "split_normalized_occurrences"))
        check(deck_counts == expected, f"deck census:{surface}")
        check(row["decision"] == "ACCEPT_V29_EXACT_WHOLE" and expected[2] >= 1, f"exact-whole admission:{surface}")
    check(sum(value[0] for value in EXPECTED_COUNTS.values()) == 210, "210 target occurrences")
    check(sum(value[2] for value in EXPECTED_COUNTS.values()) == 175, "175 exact occurrences")
    check(sum(value[3] for value in EXPECTED_COUNTS.values()) == 178, "178 normalized occurrences")
    for family, surfaces in FAMILIES.items():
        check({row["surface"] for row in deck if row["family"] == family} == surfaces, f"family membership:{family}")
    for surface, meaning in KEY_MEANINGS.items():
        check(deck_by_surface[surface]["working_meaning_de"] == meaning, f"key meaning:{surface}")
    check(not any(FILLER.search(row["working_meaning_de"]) for row in deck), "no generic filler")
    check(all(row["rival_de"] and row["strongest_counterargument"] for row in deck), "all targets retain rivals")

    family = read_tsv(ART / "FAMILY_EVIDENCE_ATLAS.tsv")
    check(len(family) == 70 and len({row["surface"] for row in family}) == 70, "70-cell family atlas")
    check(Counter(row["final_status"] for row in family) == Counter({"ACCEPTED_V29": 35, "ABSENT_HOLD": 25, "V28_ANCHOR": 7, "ZERO_EXACT_HOLD": 3}), "family status counts")
    check(all(int(row["reader_exact_occurrences"]) >= 1 for row in family if row["final_status"] == "ACCEPTED_V29"), "accepted cells exact anchored")
    check(all(row["final_status"] != "ACCEPTED_V29" for row in family if not int(row["reader_exact_occurrences"])), "no zero-exact family export")

    bridges = read_tsv(ART / "BOUNDARY_BRIDGE_ATLAS.tsv")
    check(len(bridges) == 14 and len({row["bridge_id"] for row in bridges}) == 14, "14 boundary bridges")
    check(all(row["zl3b_line"] and row["it2a_line"] and row["rf1b_line"] for row in bridges), "bridge reader lines populated")
    risks = read_tsv(ART / "RISK_AND_RIVAL_REGISTER.tsv")
    check(len(risks) == 35 and {row["surface"] for row in risks} == set(EXPECTED_COUNTS), "complete risk register")
    check(all(row["replacement_trigger"] for row in risks), "replacement triggers populated")

    audits = read_tsv(ART / "ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv")
    check(len(audits) == len({row["audit_id"] for row in audits}) == 210, "210 unique occurrence audits")
    check(Counter(row["surface"] for row in audits) == Counter({surface: values[0] for surface, values in EXPECTED_COUNTS.items()}), "audit surface counts")
    check(sum(int(row["reader_exact"]) for row in audits) == 175 and sum(int(row["split_normalized"]) for row in audits) == 178, "audit reader totals")
    check(sum(int(row["hard_collision"]) for row in audits) == 0, "no recorded hard collision")
    variants = read_tsv(ART / "READER_VARIANT_AUDIT.tsv")
    check(len(variants) == 35 and Counter(row["reader_support"] for row in variants) == Counter({"READER_VARIANT": 32, "ALL_THREE_SPLIT_NORMALIZED": 3}), "reader warning census")

    old_gloss_rows = read_tsv(ROOT / G651_GLOSSARY)
    gloss_rows = read_tsv(ART / "V29_EXACT_TOKEN_GLOSSARY.tsv")
    old_gloss, glossary = {row["surface"]: row for row in old_gloss_rows}, {row["surface"]: row for row in gloss_rows}
    check(len(old_gloss) == 379 and len(glossary) == 414 and set(glossary) == set(old_gloss) | set(EXPECTED_COUNTS), "glossary 379 to 414")
    check(all(glossary[surface] == row for surface, row in old_gloss.items()), "V28 glossary unchanged")
    check(all(glossary[surface]["working_meaning_de"] == deck_by_surface[surface]["working_meaning_de"] for surface in EXPECTED_COUNTS), "target glossary meanings")

    old_dictionary = read_tsv(ROOT / G651_DICTIONARY)
    dictionary = read_tsv(ART / "WORKING_DICTIONARY_V29.tsv")
    check(len(old_dictionary) == 450 and len(dictionary) == 485 and dictionary[:450] == old_dictionary, "dictionary append-only 450 to 485")
    check([row["entry"].split("@", 1)[0] for row in dictionary[450:]] == list(EXPECTED_COUNTS), "ordered dictionary additions")
    check(not any(row["entry"].split("@", 1)[0] in {"O_PREP", "CKH_LEARNED", "E_ATTR", "K_HEISS"} for row in dictionary), "no structural tag exported")

    coverage = read_tsv(ART / "ALL_LINE_CONCRETE_COVERAGE_V29.tsv")
    complete = read_tsv(ART / "COMPLETE_PASSAGES_V29.tsv")
    one = read_tsv(ART / "ONE_UNKNOWN_PASSAGES_V29.tsv")
    observed_final = {
        "physical_lines": len(coverage), "known_token_positions": sum(int(row["known_tokens"]) for row in coverage),
        "unknown_token_positions": sum(int(row["unknown_tokens"]) for row in coverage),
        "complete_multi_token_lines": len(complete), "strict_complete_lines": sum(int(row["strict_complete"]) for row in complete),
        "one_unknown_lines": len(one), "strict_one_unknown_lines": sum(int(row["strict_eligible"]) for row in one),
        "exact_glossary_surfaces": len(glossary),
    }
    check(observed_final == EXPECTED_FINAL, "V29 coverage metrics", repr(observed_final))
    new_complete = read_tsv(ART / "NEWLY_COMPLETED_LINES.tsv")
    check(len(new_complete) == 6 and {row["locus"] for row in new_complete} == NEW_COMPLETE_LOCI, "six new complete loci")
    check(sum(int(row["strict_complete"]) for row in new_complete) == 5, "five newly strict lines")
    newly_exposed = read_tsv(ART / "NEWLY_EXPOSED_ONE_HOLE_LINES.tsv")
    check(len(newly_exposed) == 12, "12 newly exposed one-hole events")
    reality = read_tsv(ART / "SOURCE_PASSAGE_REALITY_CHECK.tsv")
    check(len(reality) == 5 and {row["locus"] for row in reality} == STRICT_SOURCE_LOCI, "five strict source readings")
    check(all(row["strict_complete"] == "1" and "[" not in row["tokenwise_translation_de"] for row in reality), "strict sources fully rendered")
    affected = read_tsv(ART / "AFFECTED_LINE_TRANSLATIONS.tsv")
    check(len(affected) == 204 and all(row["v28_tokenwise_de"] != row["v29_tokenwise_de"] for row in affected), "204 affected lines changed")

    target_result = result.get("target_run", {})
    coverage_result = result.get("coverage", {})
    check(target_result.get("accepted_surfaces") == [row["surface"] for row in deck], "result target order")
    check((target_result.get("audited_occurrences"), target_result.get("all_reader_exact_occurrences"), target_result.get("split_normalized_occurrences")) == (210, 175, 178), "result audit totals")
    check(target_result.get("strict_v28_holes_closed") == 5 and target_result.get("hard_collisions") == 0, "result closure and collision counts")
    check(coverage_result.get("final") == EXPECTED_FINAL and coverage_result.get("affected_lines") == 204, "result coverage")
    check(result.get("working_dictionary", {}).get("v29_entries") == 485, "result dictionary")

    report_text = REPORT.read_text(encoding="utf-8") if REPORT.exists() else ""
    for needle in ("ckhy", "ockhy", "cheockhy", "chokey", "opal", "Pulver", "Wurzel", "14.951", "explorativ"):
        check(needle.lower() in report_text.lower(), f"report contains:{needle}")

    validation = {
        "schema": "GDT652_VALIDATION_V1", "experiment_id": "GDT652",
        "status": "PASS" if not issues else "FAIL", "checks_passed": len(passed),
        "checks_failed": len(issues), "passed": passed, "issues": issues,
    }
    VALIDATION.write_text(json.dumps(validation, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if issues:
        print(f"GDT652 validation FAIL: {len(issues)} issue(s)")
        for issue in issues:
            print(f"- {issue}")
        return 1
    print(f"GDT652 validation PASS: {len(passed)} checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
