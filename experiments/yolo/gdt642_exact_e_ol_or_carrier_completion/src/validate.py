#!/usr/bin/env python3
"""Independent release validator for GDT642."""
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
BASE = Path("experiments/yolo/gdt642_exact_e_ol_or_carrier_completion")
ART = ROOT / BASE / "artifacts"
RUN = ROOT / BASE / "src/run.py"
MANIFEST = ROOT / BASE / "experiment.json"
VALIDATION = ART / "VALIDATION.json"
G641_BASE = Path("experiments/yolo/gdt641_strict_tch_bound_form_completion")
G641_ALLOW = G641_BASE / "artifacts/PAGE_ALLOWLIST.tsv"
G641_GLOSSARY = G641_BASE / "artifacts/V18_EXACT_TOKEN_GLOSSARY.tsv"
G641_DICTIONARY = G641_BASE / "artifacts/WORKING_DICTIONARY_V18.tsv"
TOKENS = Path("transcription/voynich_zl3b_tokens.tsv")
CROSS = Path("transcription/voynich_cross_transcription_lines.tsv")

EXPECTED = {
    "cheol": {"meaning": "trockener Drogenstoff", "composition": "ch+e+ol", "occurrences": 142, "pages": 71, "exact": 118},
    "cheor": {"meaning": "trockener Drogenteil", "composition": "ch+e+or", "occurrences": 71, "pages": 45, "exact": 56},
    "tcheol": {"meaning": "kalt-trockener Drogenstoff", "composition": "tch+e+ol", "occurrences": 6, "pages": 5, "exact": 6},
}
EXPECTED_FAMILY = {
    "chol": (343, 303), "cheol": (142, 118), "chor": (190, 176), "cheor": (71, 56),
    "tchol": (16, 11), "tcheol": (6, 6), "tchor": (21, 17), "tcheor": (3, 3),
}
EXPECTED_ROUNDS = (
    ("BASE_V18", 285, 9748, 22591, 44, 33, 60, 17, 238),
    ("cheol", 286, 9890, 22449, 44, 33, 61, 18, 239),
    ("cheor", 287, 9961, 22378, 44, 33, 64, 19, 240),
    ("tcheol", 288, 9967, 22372, 44, 33, 65, 19, 241),
)
EXPECTED_NEW_ONE = {
    "f51v.13": ("cheol", "cheodain", "1"),
    "f15v.11": ("cheor", "oiin", "0"),
    "f88v.26": ("cheor", "choky", "1"),
    "f96v.13": ("cheor", "soysar", "0"),
    "f107r.20": ("tcheol", "kcheedy", "0"),
}
OUTPUTS = (
    "PAGE_ALLOWLIST.tsv", "TARGET_DECISION_DECK.tsv", "E_OL_OR_PRODUCTIVE_GRID.tsv",
    "TARGET_FAMILY_CONTRASTS.tsv", "COMPONENT_BINDING_AUDIT.tsv", "TARGET_NEIGHBOR_SUMMARY.tsv",
    "ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv", "CONCRETE_EXEMPLARS.tsv", "SEQUENTIAL_DECISION_LEDGER.tsv",
    "ROUND_COVERAGE_COUNTS.tsv", "ACCEPTED_WHOLE_SURFACE_DEFAULTS.tsv", "NEWLY_COMPLETED_LINES.tsv",
    "NEWLY_EXPOSED_ONE_HOLE_LINES.tsv", "V19_EXACT_TOKEN_GLOSSARY.tsv",
    "ALL_LINE_CONCRETE_COVERAGE_V19.tsv", "COMPLETE_PASSAGES_V19.tsv",
    "ONE_UNKNOWN_PASSAGES_V19.tsv", "WORKING_DICTIONARY_V19.tsv", "RESULT.json",
)
GENERIC_FILLER = re.compile(
    r"arbeitsgut|arbeitschritt|arbeitsschritt|arbeitsmittel|arbeitsstoff|arbeitsobjekt|"
    r"werkzeug|produkt weiter|f.hre .* aus|leite .* weiter",
    re.IGNORECASE,
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
    spec = importlib.util.spec_from_file_location("gdt642_builder_validation", RUN)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load GDT642 builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def guarded_query(relative_path: Path, pages: set[str], columns: str) -> list[dict[str, str]]:
    command = [str(ROOT / "vmanus-exp"), "query-tsv", str(relative_path), "--selector", "page"]
    for page in sorted(pages):
        command.extend(("--allow", page))
    command.extend(("--columns", columns, "--forbid-prefix", "f84", "--forbid-prefix", "f84r"))
    completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    if completed.returncode:
        raise RuntimeError(completed.stderr or "guarded query failed")
    if len([line for line in completed.stderr.splitlines() if line.startswith("GUARD_STATS ")]) != 1:
        raise RuntimeError("guard statistics missing or duplicated")
    rows = list(csv.DictReader(io.StringIO(completed.stdout), delimiter="\t"))
    if any(row.get("page") == "f1r" or row.get("page", "").startswith("f84") for row in rows):
        raise RuntimeError("forbidden page materialized")
    return rows


def independent_exact_counts(
    token_rows: list[dict[str, str]], cross_rows: list[dict[str, str]],
) -> tuple[Counter[str], Counter[str], Counter[str]]:
    cross = {row["locus"]: row for row in cross_rows}
    occurrence: Counter[str] = Counter()
    exact: Counter[str] = Counter()
    pages: dict[str, set[str]] = {surface: set() for surface in EXPECTED}
    ordinal: Counter[tuple[str, str]] = Counter()
    for row in sorted(token_rows, key=lambda item: (item["page"], item["locus"], int(item["token_index"]))):
        surface = row["eva"]
        if surface not in EXPECTED:
            continue
        occurrence[surface] += 1
        pages[surface].add(row["page"])
        ordinal[row["locus"], surface] += 1
        required = ordinal[row["locus"], surface]
        counts = [cross[row["locus"]][field].split().count(surface) for field in ("zl3b_clean", "it2a_clean", "rf1b_clean")]
        if required <= min(counts):
            exact[surface] += 1
    return occurrence, exact, Counter({surface: len(values) for surface, values in pages.items()})


def main() -> int:
    passed: list[str] = []
    issues: list[str] = []

    def check(ok: object, name: str, detail: str = "") -> None:
        if ok:
            passed.append(name)
        else:
            issues.append(f"{name}: {detail or 'condition failed'}")

    try:
        builder = load_builder()
    except Exception as exc:
        builder = None
        issues.append(f"builder import: {type(exc).__name__}: {exc}")
    if builder is not None:
        check(tuple(getattr(builder, "OUTPUT_NAMES", ())) == OUTPUTS[:-1], "builder output contract")
        with tempfile.TemporaryDirectory(prefix="gdt642_validate_") as tmp:
            replay_dir = Path(tmp)
            try:
                builder.build(replay_dir)
            except Exception as exc:
                issues.append(f"builder replay: {type(exc).__name__}: {exc}")
            else:
                check({path.name for path in replay_dir.iterdir() if path.is_file()} == set(OUTPUTS), "exact replay output set")
                for name in OUTPUTS:
                    expected, actual = ART / name, replay_dir / name
                    check(expected.is_file() and actual.is_file(), f"output present:{name}")
                    if expected.is_file() and actual.is_file():
                        check(expected.read_bytes() == actual.read_bytes(), f"byte replay:{name}")

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    result = json.loads((ART / "RESULT.json").read_text(encoding="utf-8"))
    check(manifest.get("experiment_id") == "GDT642", "manifest experiment id")
    check(manifest.get("sealed_data") == {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"}, "manifest sealed pages")
    check(result.get("schema") == "GDT642_EXACT_E_OL_OR_CARRIER_COMPLETION_RESULT_V1", "result schema")
    check(result.get("content_sha256") == canonical_hash({k: v for k, v in result.items() if k != "content_sha256"}), "result content hash")
    check(result.get("status") == "PASS_3_EXACT_E_CARRIERS__219_POSITIONS__5_NEW_ONE_HOLES", "result status")

    pages = {row["page"] for row in read_tsv(ART / "PAGE_ALLOWLIST.tsv")}
    check("f1r" not in pages and not any(page.startswith("f84") for page in pages), "allowlist excludes f1r/f84")
    token_rows = guarded_query(TOKENS, pages, "page,locus,token_index,eva")
    cross_rows = guarded_query(CROSS, pages, "page,locus,zl3b_clean,it2a_clean,rf1b_clean")
    independent_occ, independent_exact, independent_pages = independent_exact_counts(token_rows, cross_rows)

    deck = read_tsv(ART / "TARGET_DECISION_DECK.tsv")
    check(len(deck) == 3 and {row["surface"] for row in deck} == set(EXPECTED), "three exact target cards")
    for row in deck:
        surface, expected = row["surface"], EXPECTED[row["surface"]]
        check(row["working_meaning_de"] == expected["meaning"], f"meaning:{surface}")
        check(row["composition"] == expected["composition"], f"composition:{surface}")
        check(row["decision"] == "ACCEPT" and row["scope"] == "exact complete ZL3b surface only", f"scope:{surface}")
        check(int(row["occurrences"]) == expected["occurrences"] == independent_occ[surface], f"occurrences:{surface}")
        check(int(row["pages"]) == expected["pages"] == independent_pages[surface], f"pages:{surface}")
        check(int(row["reader_exact_occurrences"]) == expected["exact"] == independent_exact[surface], f"reader exact:{surface}")
        check(not GENERIC_FILLER.search(row["working_meaning_de"]), f"no generic filler:{surface}")

    grid = read_tsv(ART / "E_OL_OR_PRODUCTIVE_GRID.tsv")
    check(len(grid) == 11 and all(row["occupied_cells"] == "4" and row["complete_four_cell_grid"] == "1" for row in grid), "eleven complete four-cell grids")
    check({row["prefix"] for row in grid if row["target_family"] == "1"} == {"ch", "tch"}, "two focal grid rows")
    family = {row["surface"]: row for row in read_tsv(ART / "TARGET_FAMILY_CONTRASTS.tsv")}
    check(set(family) == set(EXPECTED_FAMILY), "eight focal sister cells")
    for surface, (occurrences, exact_count) in EXPECTED_FAMILY.items():
        check(int(family[surface]["occurrences"]) == occurrences, f"family occurrences:{surface}")
        check(int(family[surface]["reader_exact_occurrences"]) == exact_count, f"family exact:{surface}")

    components = read_tsv(ART / "COMPONENT_BINDING_AUDIT.tsv")
    check(len(components) == 9, "nine bound component rows")
    check(all("exact" in row["licensed_use"] or row["licensed_use"].startswith("no bare") for row in components), "component scope barriers")

    audits = read_tsv(ART / "ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv")
    check(len(audits) == 219 and len({row["audit_id"] for row in audits}) == 219, "219 unique occurrence audits")
    audit_surface = Counter(row["surface"] for row in audits)
    check(audit_surface == Counter({surface: value["occurrences"] for surface, value in EXPECTED.items()}), "audit target census")
    check(sum(int(row["reader_exact"]) for row in audits) == 180, "180 reader-exact target occurrences")
    check(sum(int(row["split_normalized"]) for row in audits) == 182, "182 split-normalized target occurrences")
    check(Counter(row["verdict"] for row in audits) == Counter({"CONSISTENT_CONCRETE": 117, "OPAQUE_CONTEXT": 63, "READER_BOUNDARY_WARNING": 39}), "audit verdict census")
    check(all(row["hard_collision"] == "0" for row in audits), "zero hard collisions")
    check(all(int(row["reader_exact"]) <= int(row["split_normalized"]) for row in audits), "exact implies boundary normalized")
    for row in audits:
        check(row["before_gloss"] == f"[{row['surface']}:?]", f"target unknown before:{row['audit_id']}")
        check(row["after_gloss"] == EXPECTED[row["surface"]]["meaning"], f"target concrete after:{row['audit_id']}")

    exemplars = read_tsv(ART / "CONCRETE_EXEMPLARS.tsv")
    check(len(exemplars) == 10 and {row["surface"] for row in exemplars} == set(EXPECTED), "ten concrete exemplars")
    check(all(EXPECTED[row["surface"]]["meaning"] in row["literal_v19_de"] for row in exemplars), "exemplars contain target readings")
    check(all(not GENERIC_FILLER.search(row["smoothed_partial_reading_de"]) for row in exemplars), "exemplars contain no generic filler")

    ledger = read_tsv(ART / "SEQUENTIAL_DECISION_LEDGER.tsv")
    check(len(ledger) == 3 and [row["surface"] for row in ledger] == list(EXPECTED), "three sequential decisions")
    check(sum(int(row["hard_collisions"]) for row in ledger) == 0, "ledger zero collision")
    check(sum(int(row["consistent_concrete"]) for row in ledger) == 117, "ledger concrete total")
    check(sum(int(row["opaque_context"]) for row in ledger) == 63, "ledger opaque total")
    check(sum(int(row["reader_boundary_warning"]) for row in ledger) == 39, "ledger reader-warning total")

    rounds = read_tsv(ART / "ROUND_COVERAGE_COUNTS.tsv")
    check(len(rounds) == 4, "four coverage rounds")
    for row, expected in zip(rounds, EXPECTED_ROUNDS):
        observed = (
            row["surface"], int(row["dictionary_entries"]), int(row["known_token_positions"]),
            int(row["unknown_token_positions"]), int(row["complete_multi_token_lines"]),
            int(row["strict_complete_lines"]), int(row["one_unknown_lines"]),
            int(row["strict_one_unknown_lines"]), int(row["exact_glossary_surfaces"]),
        )
        check(observed == expected, f"coverage round:{row['surface']}", repr(observed))

    new_complete = read_tsv(ART / "NEWLY_COMPLETED_LINES.tsv")
    check(not new_complete, "no fabricated new complete line")
    new_one = read_tsv(ART / "NEWLY_EXPOSED_ONE_HOLE_LINES.tsv")
    check(len(new_one) == 5 and {row["locus"] for row in new_one} == set(EXPECTED_NEW_ONE), "five newly exposed one-hole lines")
    for row in new_one:
        enabled, unknown, strict = EXPECTED_NEW_ONE[row["locus"]]
        check((row["enabled_by_surface"], row["unknown_surface"], row["strict_eligible"]) == (enabled, unknown, strict), f"new one-hole:{row['locus']}")

    v18_gloss = {row["surface"]: row for row in read_tsv(ROOT / G641_GLOSSARY)}
    v19_gloss = {row["surface"]: row for row in read_tsv(ART / "V19_EXACT_TOKEN_GLOSSARY.tsv")}
    check(len(v18_gloss) == 238 and len(v19_gloss) == 241, "glossary 238 to 241")
    check(all(v19_gloss[surface] == row for surface, row in v18_gloss.items()), "V18 glossary rows preserved")
    for surface, expected in EXPECTED.items():
        check(v19_gloss[surface]["working_meaning_de"] == expected["meaning"], f"V19 glossary target:{surface}")
        check(v19_gloss[surface]["scope_state"] == "KNOWN_EXACT_WHOLE", f"V19 exact scope:{surface}")

    v18_dictionary = read_tsv(ROOT / G641_DICTIONARY)
    v19_dictionary = read_tsv(ART / "WORKING_DICTIONARY_V19.tsv")
    check(len(v18_dictionary) == 285 and len(v19_dictionary) == 288, "dictionary 285 to 288")
    check(v19_dictionary[:285] == v18_dictionary, "V18 dictionary byte-order prefix preserved")
    check([row["entry"].split("@", 1)[0] for row in v19_dictionary[285:]] == list(EXPECTED), "three exact dictionary tail entries")

    coverage = read_tsv(ART / "ALL_LINE_CONCRETE_COVERAGE_V19.tsv")
    complete = read_tsv(ART / "COMPLETE_PASSAGES_V19.tsv")
    one = read_tsv(ART / "ONE_UNKNOWN_PASSAGES_V19.tsv")
    check(len(coverage) == 4128 and sum(int(row["known_tokens"]) for row in coverage) == 9967, "V19 coverage totals")
    check(sum(int(row["unknown_tokens"]) for row in coverage) == 22372, "V19 unknown positions")
    check(len(complete) == 44 and sum(int(row["strict_complete"]) for row in complete) == 33, "V19 complete lines unchanged")
    check(len(one) == 65 and sum(int(row["strict_eligible"]) for row in one) == 19, "V19 one-hole frontier")
    check(all(row["page"] != "f1r" and not row["page"].startswith("f84") for row in coverage), "coverage contains no forbidden page")

    for relative, digest in result.get("inputs", {}).items():
        check((ROOT / relative).is_file() and sha256(ROOT / relative) == digest, f"input hash:{relative}")
    for relative, digest in result.get("outputs", {}).items():
        check((ROOT / relative).is_file() and sha256(ROOT / relative) == digest, f"output hash:{relative}")
    check(result.get("target_run", {}).get("audited_occurrences") == 219, "result audit count")
    check(result.get("coverage", {}).get("newly_exposed_one_hole_lines") == 5, "result new one-hole count")
    check(result.get("working_dictionary", {}).get("v19_entries") == 288, "result V19 dictionary count")

    validation_core = {
        "schema": "GDT642_VALIDATION_V1", "experiment_id": "GDT642",
        "status": "PASS" if not issues else "FAIL", "passed_checks": len(passed),
        "issue_count": len(issues), "issues": issues,
        "summary": {
            "target_occurrences": len(audits), "reader_exact": sum(int(row["reader_exact"]) for row in audits),
            "concrete_compatible": sum(row["verdict"] == "CONSISTENT_CONCRETE" for row in audits),
            "new_one_hole_lines": len(new_one), "v19_dictionary_entries": len(v19_dictionary),
        },
    }
    validation = {**validation_core, "content_sha256": canonical_hash(validation_core)}
    VALIDATION.write_text(json.dumps(validation, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"GDT642 validation: {validation['status']} checks={len(passed)} issues={len(issues)}")
    for issue in issues:
        print(f"ISSUE {issue}")
    return 0 if not issues else 1


if __name__ == "__main__":
    raise SystemExit(main())
