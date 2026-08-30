#!/usr/bin/env python3
"""Independent release validator for GDT654."""
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
BASE = Path("experiments/yolo/gdt654_ar_or_surface_consolidation")
ART = ROOT / BASE / "artifacts"
RUN = ROOT / BASE / "src/run.py"
MANIFEST = ROOT / BASE / "experiment.json"
REPORT = ROOT / BASE / "REPORT.md"
VALIDATION = ART / "VALIDATION.json"
G653 = Path("experiments/yolo/gdt653_strict_v29_boundary_compounds")
G653_ALLOW = G653 / "artifacts/PAGE_ALLOWLIST.tsv"
G653_COVERAGE = G653 / "artifacts/ALL_LINE_CONCRETE_COVERAGE_V30.tsv"
G653_COMPLETE = G653 / "artifacts/COMPLETE_PASSAGES_V30.tsv"
G653_ONE = G653 / "artifacts/ONE_UNKNOWN_PASSAGES_V30.tsv"
G653_GLOSSARY = G653 / "artifacts/V30_EXACT_TOKEN_GLOSSARY.tsv"
G653_DICTIONARY = G653 / "artifacts/WORKING_DICTIONARY_V30.tsv"
TOKENS = Path("transcription/voynich_zl3b_tokens.tsv")
CROSS = Path("transcription/voynich_cross_transcription_lines.tsv")
STATUS = "PASS_19_AR_OR_SURFACES__V31"

# surface: mode, meaning, composition, occurrences, pages, exact, normalized
TARGETS = {
    "ar": ("NEW_EXACT_WHOLE", "Drogenfraktion I", "AR_FRACTION_I", 321, 90, 242, 242),
    "or": ("REVISE_AMBIGUOUS_TO_EXACT", "Drogenportion", "OR_PORTION", 321, 114, 235, 235),
    "kar": ("NEW_EXACT_WHOLE", "heiße Drogenfraktion I", "K_HEISS+AR_FRACTION_I", 57, 42, 42, 42),
    "kor": ("NEW_EXACT_WHOLE", "heiße Drogenportion", "K_HEISS+OR_PORTION", 20, 20, 13, 13),
    "tar": ("NEW_EXACT_WHOLE", "kalte Drogenfraktion I", "T_KALT+AR_FRACTION_I", 40, 33, 33, 33),
    "tor": ("NEW_EXACT_WHOLE", "kalte Drogenportion", "T_KALT+OR_PORTION", 17, 17, 12, 12),
    "oar": ("NEW_EXACT_WHOLE", "Drogenfraktion I im Ansatz", "O_PREP+AR_FRACTION_I", 10, 9, 9, 9),
    "oor": ("NEW_EXACT_WHOLE", "Drogenportion im Ansatz", "O_PREP+OR_PORTION", 2, 2, 2, 2),
    "okar": ("NEW_EXACT_WHOLE", "heiße Drogenfraktion I im Ansatz", "O_PREP+K_HEISS+AR_FRACTION_I", 119, 55, 91, 93),
    "okor": ("NEW_EXACT_WHOLE", "heiße Drogenportion im Ansatz", "O_PREP+K_HEISS+OR_PORTION", 24, 20, 16, 16),
    "otar": ("NEW_EXACT_WHOLE", "kalte Drogenfraktion I im Ansatz", "O_PREP+T_KALT+AR_FRACTION_I", 123, 58, 110, 110),
    "otor": ("NEW_EXACT_WHOLE", "kalte Drogenportion im Ansatz", "O_PREP+T_KALT+OR_PORTION", 33, 29, 24, 24),
    "qoar": ("NEW_EXACT_WHOLE", "Drogenfraktion I", "QO_SCOPE+AR_FRACTION_I", 7, 7, 7, 7),
    "qoor": ("NEW_EXACT_WHOLE", "Drogenportion", "QO_SCOPE+OR_PORTION", 6, 6, 5, 5),
    "qokar": ("REVISE_CONFLICTING_EXACT", "heiße Drogenfraktion I", "QO_SCOPE+K_HEISS+AR_FRACTION_I", 153, 62, 132, 132),
    "qokor": ("NEW_EXACT_WHOLE", "heiße Drogenportion", "QO_SCOPE+K_HEISS+OR_PORTION", 29, 25, 21, 21),
    "qotar": ("NEW_EXACT_WHOLE", "kalte Drogenfraktion I", "QO_SCOPE+T_KALT+AR_FRACTION_I", 61, 36, 53, 53),
    "rkar": ("NEW_EXACT_WHOLE", "heiße Wurzelfraktion I", "R_ROOT+K_HEISS+AR_FRACTION_I", 1, 1, 1, 1),
    "lkor": ("NEW_EXACT_WHOLE", "heiße Holzportion", "L_WOOD+K_HEISS+OR_PORTION", 3, 3, 3, 3),
}
TARGET_ORDER = list(TARGETS)
NEW_SURFACES = {surface for surface, spec in TARGETS.items() if spec[0].startswith("NEW")}
REVISED_SURFACES = set(TARGETS) - NEW_SURFACES
GRID_SPECS = tuple(
    (shell_name, qualifier, f"{shell}{core}ar", f"{shell}{core}or")
    for shell_name, shell in (("BARE", ""), ("O", "o"), ("QO", "qo"))
    for qualifier, core in (
        ("UNQUALIFIED", ""), ("K", "k"), ("T", "t"), ("CH", "ch"), ("SH", "sh"),
        ("K_CH", "kch"), ("K_SH", "ksh"), ("T_CH", "tch"), ("T_SH", "tsh"),
    )
)
BOUNDARIES = {
    "G654-B01": ("DIRECT_TARGET_SPLIT", "f113v.29", "a r / ar"),
    "G654-B02": ("DIRECT_TARGET_SPLIT", "f113v.41", "a r / ar"),
    "G654-B03": ("DIRECT_TARGET_SPLIT", "f102v2.19", "o r / or"),
    "G654-B04": ("DIRECT_SUPERFORM_SPLIT", "f105r.4", "okar / ok ar"),
    "G654-B05": ("DIRECT_SUPERFORM_SPLIT", "f108v.10", "okar / o kar"),
    "G654-B06": ("DIRECT_MATERIAL_SPLIT", "f76r.49", "l kar / lkar"),
    "G654-W01": ("WARNING_NO_FUSED_OR", "f36r.5", "o r / s r"),
    "G654-W02": ("WARNING_SUPERFORM_ONLY", "f111r.21", "o r / oxor"),
}
BASE_METRICS = {
    "physical_lines": 4128, "known_token_positions": 14973, "unknown_token_positions": 17366,
    "complete_multi_token_lines": 119, "strict_complete_lines": 73, "one_unknown_lines": 160,
    "strict_one_unknown_lines": 34, "exact_glossary_surfaces": 420,
}
FINAL_METRICS = {
    "physical_lines": 4128, "known_token_positions": 15846, "unknown_token_positions": 16493,
    "complete_multi_token_lines": 123, "strict_complete_lines": 75, "one_unknown_lines": 197,
    "strict_one_unknown_lines": 44, "exact_glossary_surfaces": 437,
}
ROUNDS = (
    ("BASE_V30", 491, 14973, 17366, 119, 73, 160, 34, 420),
    ("ar", 492, 15294, 17045, 119, 73, 169, 34, 421),
    ("or", 493, 15294, 17045, 119, 74, 169, 35, 421),
    ("kar", 494, 15351, 16988, 119, 74, 176, 36, 422),
    ("kor", 495, 15371, 16968, 119, 74, 180, 37, 423),
    ("tar", 496, 15411, 16928, 119, 74, 182, 39, 424),
    ("tor", 497, 15428, 16911, 119, 74, 183, 40, 425),
    ("oar", 498, 15438, 16901, 119, 74, 183, 40, 426),
    ("oor", 499, 15440, 16899, 119, 74, 183, 40, 427),
    ("okar", 500, 15559, 16780, 120, 74, 186, 41, 428),
    ("okor", 501, 15583, 16756, 120, 74, 187, 42, 429),
    ("otar", 502, 15706, 16633, 121, 74, 190, 42, 430),
    ("otor", 503, 15739, 16600, 122, 74, 192, 42, 431),
    ("qoar", 504, 15746, 16593, 122, 74, 192, 42, 432),
    ("qoor", 505, 15752, 16587, 122, 74, 193, 43, 433),
    ("qokar", 506, 15752, 16587, 122, 74, 193, 43, 433),
    ("qokor", 507, 15781, 16558, 123, 75, 195, 44, 434),
    ("qotar", 508, 15842, 16497, 123, 75, 197, 44, 435),
    ("rkar", 509, 15843, 16496, 123, 75, 197, 44, 436),
    ("lkor", 510, 15846, 16493, 123, 75, 197, 44, 437),
)
OUTPUTS = (
    "PAGE_ALLOWLIST.tsv", "TARGET_DECISION_DECK.tsv", "FAMILY_CONTRAST_ATLAS.tsv",
    "FULL_AR_OR_PAIR_GRID.tsv", "PAIR_CONTRAST_COUNTS.tsv", "BOUNDARY_EVIDENCE_ATLAS.tsv",
    "REVISION_LEDGER.tsv", "ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv", "READER_VARIANT_AUDIT.tsv",
    "ROUND_COVERAGE_COUNTS.tsv", "ACCEPTED_WHOLE_SURFACE_DEFAULTS.tsv",
    "SOURCE_PASSAGE_REALITY_CHECK.tsv", "CURATED_COMPLETE_PASSAGE_READINGS.tsv",
    "AFFECTED_LINE_TRANSLATIONS.tsv", "NEWLY_COMPLETED_LINES.tsv",
    "NEWLY_EXPOSED_ONE_HOLE_LINES.tsv", "V31_EXACT_TOKEN_GLOSSARY.tsv",
    "ALL_LINE_CONCRETE_COVERAGE_V31.tsv", "COMPLETE_PASSAGES_V31.tsv",
    "ONE_UNKNOWN_PASSAGES_V31.tsv", "WORKING_DICTIONARY_V31.tsv", "RESULT.json",
)
FILLER = re.compile(
    r"arbeitsgut|arbeitschritt|arbeitsschritt|arbeitsmittel|arbeitsstoff|arbeitsobjekt|"
    r"werkzeug|produkt weiter|f.hre .* aus|leite .* weiter|geh(?:e)? zur arbeit|nimm .* arbeite",
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


def guarded_query(path: Path, pages: set[str], columns: str) -> tuple[list[dict[str, str]], dict[str, int]]:
    command = [str(ROOT / "vmanus-exp"), "query-tsv", str(path), "--selector", "page"]
    for page in sorted(pages):
        command.extend(("--allow", page))
    command.extend(("--columns", columns, "--forbid-prefix", "f84", "--forbid-prefix", "f84r"))
    done = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    stats_lines = [line for line in done.stderr.splitlines() if line.startswith("GUARD_STATS ")]
    if done.returncode or len(stats_lines) != 1:
        raise RuntimeError(done.stderr or "guarded query failed")
    rows = list(csv.DictReader(io.StringIO(done.stdout), delimiter="\t"))
    if any(row.get("page") == "f1r" or row.get("page", "").startswith("f84") for row in rows):
        raise RuntimeError("excluded or forbidden page materialized")
    return rows, json.loads(stats_lines[0].removeprefix("GUARD_STATS "))


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


def independent_occurrences(token_rows, cross_rows, surfaces: set[str]):
    cross = {row["locus"]: row for row in cross_rows}
    ordinal: Counter[tuple[str, str]] = Counter()
    records = []
    for row in sorted(token_rows, key=lambda item: (item["page"], item["locus"], int(item["token_index"]))):
        surface = row["eva"]
        if surface not in surfaces:
            continue
        ordinal[row["locus"], surface] += 1
        needed = ordinal[row["locus"], surface]
        lines = [cross[row["locus"]][field].split() for field in ("zl3b_clean", "it2a_clean", "rf1b_clean")]
        direct = [tokens.count(surface) for tokens in lines]
        spans = [span_count(tokens, surface) for tokens in lines]
        records.append({
            "surface": surface, "page": row["page"], "locus": row["locus"],
            "reader_exact": int(needed <= min(direct)), "split_normalized": int(needed <= min(spans)),
        })
    return records


def census(records, surface: str) -> tuple[int, int, int, int]:
    members = [row for row in records if row["surface"] == surface]
    return (len(members), len({row["page"] for row in members}),
            sum(row["reader_exact"] for row in members), sum(row["split_normalized"] for row in members))


def metrics(coverage, complete, one_unknown, glossary_size: int) -> dict[str, int]:
    return {
        "physical_lines": len(coverage),
        "known_token_positions": sum(int(row["known_tokens"]) for row in coverage),
        "unknown_token_positions": sum(int(row["unknown_tokens"]) for row in coverage),
        "complete_multi_token_lines": len(complete),
        "strict_complete_lines": sum(int(row["strict_complete"]) for row in complete),
        "one_unknown_lines": len(one_unknown),
        "strict_one_unknown_lines": sum(int(row["strict_eligible"]) for row in one_unknown),
        "exact_glossary_surfaces": glossary_size,
    }


def load_builder():
    spec = importlib.util.spec_from_file_location("gdt654_builder_validation", RUN)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load GDT654 builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    passed: list[str] = []
    issues: list[str] = []

    def check(ok: object, name: str, detail: str = "") -> None:
        (passed if ok else issues).append(name if ok else f"{name}: {detail or 'condition failed'}")

    result = json.loads((ART / "RESULT.json").read_text(encoding="utf-8"))
    check(result.get("schema") == "GDT654_AR_OR_SURFACE_CONSOLIDATION_RESULT_V1", "result schema")
    check(result.get("experiment_id") == "GDT654" and result.get("status") == STATUS, "result identity/status")
    check(result.get("content_sha256") == canonical_hash({k: v for k, v in result.items() if k != "content_sha256"}), "result content hash")

    allow_rows = read_tsv(ART / "PAGE_ALLOWLIST.tsv")
    pages = {row["page"] for row in allow_rows}
    check(len(allow_rows) == len(pages) == 179, "179 unique guarded pages")
    check("f1r" not in pages and not any(page.startswith("f84") for page in pages), "f1r excluded and f84 forbidden")
    check((ART / "PAGE_ALLOWLIST.tsv").read_bytes() == (ROOT / G653_ALLOW).read_bytes(), "V30 allowlist inherited byte-identically")
    token_rows, token_stats = guarded_query(TOKENS, pages, "page,locus,token_index,eva")
    cross_rows, cross_stats = guarded_query(CROSS, pages, "page,locus,zl3b_clean,it2a_clean,rf1b_clean")
    check(len(token_rows) == 32339 and token_stats == {"selected": 32339, "skipped_forbidden": 709, "skipped_not_allowed": 5940}, "guarded token census", repr(token_stats))
    check(len(cross_rows) == 4137 and cross_stats == {"selected": 4137, "skipped_forbidden": 98, "skipped_not_allowed": 1151}, "guarded cross census", repr(cross_stats))
    guard = result.get("guard", {})
    check(guard.get("token_query") == token_stats and guard.get("cross_query") == cross_stats, "result guarded counts")
    check(guard.get("allowed_pages") == 179 and guard.get("f1r") == "EXCLUDED" and guard.get("f84") == guard.get("f84r") == "FORBIDDEN" and guard.get("new_pages") == guard.get("new_images") == 0, "result guard ceiling")

    all_surfaces = set(TARGETS) | {surface for row in GRID_SPECS for surface in row[2:]}
    records = independent_occurrences(token_rows, cross_rows, all_surfaces)
    deck = read_tsv(ART / "TARGET_DECISION_DECK.tsv")
    deck_by = {row["surface"]: row for row in deck}
    check(len(deck) == len(deck_by) == 19 and list(deck_by) == TARGET_ORDER, "19 ordered target cards")
    check([row["candidate_id"] for row in deck] == [f"G654-C{i:02d}" for i in range(1, 20)], "ordered candidate ids")
    for index, (surface, spec) in enumerate(TARGETS.items(), 1):
        row = deck_by[surface]
        expected_counts = spec[3:]
        artifact_counts = tuple(int(row[field]) for field in ("occurrences", "pages", "reader_exact_occurrences", "split_normalized_occurrences"))
        check(census(records, surface) == expected_counts, f"independent target census:{surface}", repr(census(records, surface)))
        check(artifact_counts == expected_counts, f"deck target census:{surface}", repr(artifact_counts))
        check((row["mode"], row["v31_meaning_de"], row["composition"]) == spec[:3], f"target value:{surface}")
        check(row["candidate_order"] == str(index) and row["decision"] == "ACCEPT_V31_EXACT_WHOLE", f"target admission:{surface}")
        check(bool(row["rival_de"] and row["decision_basis"] and row["strongest_counterargument"]), f"target support/rival:{surface}")
    check(sum(TARGETS[s][3] for s in TARGETS) == 1347, "1347 target occurrences")
    check(sum(TARGETS[s][5] for s in TARGETS) == 1051, "1051 reader-exact target occurrences")
    check(sum(TARGETS[s][6] for s in TARGETS) == 1053, "1053 split-normalized target occurrences")
    check(NEW_SURFACES == set(result["target_run"]["new_surfaces"]) and REVISED_SURFACES == set(result["target_run"]["revised_surfaces"]), "17 new and two revised targets")

    grid = read_tsv(ART / "FULL_AR_OR_PAIR_GRID.tsv")
    check(len(grid) == 27 and [(row["shell"], row["qualifier"], row["ar_surface"], row["or_surface"]) for row in grid] == list(GRID_SPECS), "complete ordered 27-pair grid")
    observed = occurrences = exact_total = normalized_total = 0
    for row in grid:
        for side in ("ar", "or"):
            surface = row[f"{side}_surface"]
            independent = census(records, surface)
            artifact = tuple(int(row[f"{side}_{field}"]) for field in ("occurrences", "pages", "reader_exact", "split_normalized"))
            check(artifact == independent, f"independent grid census:{surface}", repr(artifact))
            observed += int(independent[0] > 0)
            occurrences += independent[0]
            exact_total += independent[2]
            normalized_total += independent[3]
            check(row[f"{side}_status"] != "ACCEPTED_V31" or surface in TARGETS, f"no unregistered grid export:{surface}")
    check((observed, occurrences, exact_total, normalized_total) == (45, 1882, 1516, 1521), "54-cell grid totals", repr((observed, occurrences, exact_total, normalized_total)))
    check(result.get("full_ar_or_grid") == {
        "pair_rows": 27, "total_cells": 54, "observed_cells": 45, "occurrences": 1882,
        "all_reader_exact_occurrences": 1516, "split_normalized_occurrences": 1521,
        "accepted_v31_cells": 19, "learned_head_collision_holds": ["char", "chor", "shar", "shor"],
    }, "result full-grid packet")

    cross_by = {row["locus"]: row for row in cross_rows}
    boundary_rows = read_tsv(ART / "BOUNDARY_EVIDENCE_ATLAS.tsv")
    boundary_by = {row["bridge_id"]: row for row in boundary_rows}
    check(len(boundary_rows) == len(boundary_by) == 8 and list(boundary_by) == list(BOUNDARIES), "eight ordered boundary rows")
    for bridge_id, expected in BOUNDARIES.items():
        row, source = boundary_by[bridge_id], cross_by[expected[1]]
        check((row["evidence_type"], row["locus"], row["diagnostic_surface"]) == expected, f"boundary identity:{bridge_id}")
        check(row["page"] == source["page"] and tuple(row[field] for field in ("zl3b_line", "it2a_line", "rf1b_line")) == tuple(source[field] for field in ("zl3b_clean", "it2a_clean", "rf1b_clean")), f"boundary source fidelity:{bridge_id}")
        check(bool(row["supports"]), f"boundary interpretation:{bridge_id}")

    audits = read_tsv(ART / "ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv")
    check(len(audits) == len({row["audit_id"] for row in audits}) == 1347, "1347 unique occurrence audits")
    check(Counter(row["surface"] for row in audits) == Counter({surface: spec[3] for surface, spec in TARGETS.items()}), "audit surface census")
    check(sum(int(row["reader_exact"]) for row in audits) == 1051 and sum(int(row["split_normalized"]) for row in audits) == 1053, "audit exact/normalized totals")
    check(sum(int(row["hard_collision"]) for row in audits) == 0, "no target hard collisions")
    independent_counter = Counter((row["surface"], row["page"], row["locus"], row["reader_exact"], row["split_normalized"]) for row in records if row["surface"] in TARGETS)
    artifact_counter = Counter((row["surface"], row["page"], row["locus"], int(row["reader_exact"]), int(row["split_normalized"])) for row in audits)
    check(artifact_counter == independent_counter, "all audit reader flags independently reproduced")
    variants = read_tsv(ART / "READER_VARIANT_AUDIT.tsv")
    check(len(variants) == 296, "296 non-exact reader rows")
    check(Counter(row["reader_support"] for row in variants) == Counter({"ALL_THREE_SPLIT_NORMALIZED": 2, "READER_VARIANT": 294}), "variant support split")
    check(sum(row["verdict"] == "READER_VARIANT_WARNING" for row in audits) == 294, "294 hard reader warnings")

    revisions = read_tsv(ART / "REVISION_LEDGER.tsv")
    revision_by = {row["surface"]: row for row in revisions}
    check(len(revisions) == 2 and set(revision_by) == {"or", "qokar"}, "two visible revisions")
    check((revision_by["or"]["v30_meaning_de"], revision_by["or"]["v31_meaning_de"]) == ("Teil-/Nominalträger; genaue Basisbedeutung offen", "Drogenportion"), "OR revision")
    check((revision_by["qokar"]["v30_meaning_de"], revision_by["qokar"]["v31_meaning_de"]) == ("heiße Portion", "heiße Drogenfraktion I"), "QOKAR correction")

    base_gloss_rows = read_tsv(ROOT / G653_GLOSSARY)
    gloss_rows = read_tsv(ART / "V31_EXACT_TOKEN_GLOSSARY.tsv")
    base_gloss = {row["surface"]: row for row in base_gloss_rows}
    glossary = {row["surface"]: row for row in gloss_rows}
    check(len(base_gloss_rows) == len(base_gloss) == 420 and len(gloss_rows) == len(glossary) == 437, "glossary 420 to 437")
    check(set(glossary) == set(base_gloss) | NEW_SURFACES, "exact 17-surface glossary extension")
    check(all(glossary[surface] == row for surface, row in base_gloss.items() if surface not in REVISED_SURFACES), "non-revised V30 glossary retained")
    for surface, spec in TARGETS.items():
        row = glossary[surface]
        check((row["working_meaning_de"], row["source"], row["strength"], row["scope_state"], row["priority"]) == (spec[1], f"GDT654:{spec[0]}", "EXACT_WHOLE_AR_OR_CONSOLIDATION", "KNOWN_EXACT_WHOLE", "150"), f"V31 glossary card:{surface}")

    base_dictionary = read_tsv(ROOT / G653_DICTIONARY)
    dictionary = read_tsv(ART / "WORKING_DICTIONARY_V31.tsv")
    additions = dictionary[len(base_dictionary):]
    check(len(base_dictionary) == 491 and len(dictionary) == 510, "dictionary 491 to 510")
    check(dictionary[:491] == base_dictionary, "V30 dictionary prefix unchanged")
    check([row["entry"].split("@", 1)[0] for row in additions] == TARGET_ORDER, "19 ordered dictionary additions")
    for index, (surface, row) in enumerate(zip(TARGET_ORDER, additions), 1):
        spec = TARGETS[surface]
        check((row["entry"], row["working_meaning_de"], row["composition"], row["status"]) == (f"{surface}@GDT654_EXACT_WHOLE", spec[1], spec[2], f"NEW_V31_ACCEPTED_ROUND_{index:02d}"), f"dictionary addition:{surface}")

    base_cov = read_tsv(ROOT / G653_COVERAGE)
    base_complete = read_tsv(ROOT / G653_COMPLETE)
    base_one = read_tsv(ROOT / G653_ONE)
    coverage = read_tsv(ART / "ALL_LINE_CONCRETE_COVERAGE_V31.tsv")
    complete = read_tsv(ART / "COMPLETE_PASSAGES_V31.tsv")
    one = read_tsv(ART / "ONE_UNKNOWN_PASSAGES_V31.tsv")
    check(metrics(base_cov, base_complete, base_one, len(base_gloss)) == BASE_METRICS, "V30 metrics")
    check(metrics(coverage, complete, one, len(glossary)) == FINAL_METRICS, "V31 metrics")
    check(sum(int(row["token_count"]) for row in coverage) == 32339, "V31 token census")
    check(FINAL_METRICS["known_token_positions"] - BASE_METRICS["known_token_positions"] == 873, "873 newly known positions")
    base_cov_by = {row["locus"]: row for row in base_cov}
    cov_by = {row["locus"]: row for row in coverage}
    new_positions = Counter(row["locus"] for row in token_rows if row["eva"] in NEW_SURFACES)
    check(all(int(cov_by[locus]["known_tokens"]) - int(base_cov_by[locus]["known_tokens"]) == new_positions[locus] for locus in cov_by), "linewise new-surface deltas")
    target_loci = {row["locus"] for row in token_rows if row["eva"] in TARGETS}
    affected = read_tsv(ART / "AFFECTED_LINE_TRANSLATIONS.tsv")
    check(len(affected) == len({row["locus"] for row in affected}) == 990 and {row["locus"] for row in affected} == target_loci, "990 exact affected lines")
    base_complete_by = {row["locus"]: row for row in base_complete}
    complete_by = {row["locus"]: row for row in complete}
    new_loci = {"f37r.7", "f81v.5", "f86v6.35", "f99v.3"}
    check(set(complete_by) - set(base_complete_by) == new_loci, "exact four new complete loci")
    new_rows = read_tsv(ART / "NEWLY_COMPLETED_LINES.tsv")
    check(len(new_rows) == 4 and {row["locus"] for row in new_rows} == new_loci, "four new-complete rows")
    check({row["locus"] for row in new_rows if row["strict_complete"] == "1"} == {"f37r.7"}, "one newly closed strict line")
    check(base_complete_by["f6r.12"]["strict_complete"] == "0" and complete_by["f6r.12"]["strict_complete"] == "1", "OR revision makes f6r.12 strict")
    exposed = read_tsv(ART / "NEWLY_EXPOSED_ONE_HOLE_LINES.tsv")
    check(len(exposed) == 41 and len({(row["introduced_round"], row["locus"], row["unknown_surface"]) for row in exposed}) == 41, "41 sequentially exposed one-hole rows")
    curated = read_tsv(ART / "CURATED_COMPLETE_PASSAGE_READINGS.tsv")
    check(len(curated) == 14 and new_loci <= {row["locus"] for row in curated}, "14 curated complete readings including four new")
    check(all(row["curated_workshop_reading_de"] and "[" not in row["curated_workshop_reading_de"] and "?" not in row["curated_workshop_reading_de"] for row in curated), "curated readings concrete")
    curated_by = {row["locus"]: row for row in curated}
    check("IT2a reads final OTAR" in curated_by["f86v6.35"]["reader_note"] and "RF1b reads OTAR" in curated_by["f99v.3"]["reader_note"], "manual reader warnings retained")

    round_rows = read_tsv(ART / "ROUND_COVERAGE_COUNTS.tsv")
    check(len(round_rows) == 20 and [row["round"] for row in round_rows] == [str(i) for i in range(20)], "20 ordered coverage rounds")
    for index, expected in enumerate(ROUNDS):
        row = round_rows[index]
        observed_round = (row["surface"], int(row["dictionary_entries"]), int(row["known_token_positions"]), int(row["unknown_token_positions"]), int(row["complete_multi_token_lines"]), int(row["strict_complete_lines"]), int(row["one_unknown_lines"]), int(row["strict_one_unknown_lines"]), int(row["exact_glossary_surfaces"]))
        check(observed_round == expected, f"round metrics:{index}", repr(observed_round))
        check(row["dictionary_sha256"] == canonical_hash(dictionary[:int(row["dictionary_entries"])]), f"round dictionary hash:{index}")

    target_run = result.get("target_run", {})
    check((target_run.get("candidates"), target_run.get("accepted_exact_wholes"), target_run.get("audited_occurrences"), target_run.get("all_reader_exact_occurrences"), target_run.get("split_normalized_occurrences"), target_run.get("reader_variant_warnings"), target_run.get("hard_collisions")) == (19, 19, 1347, 1051, 1053, 294, 0), "result target metrics")
    check(result.get("coverage") == {"base": BASE_METRICS, "final": FINAL_METRICS, "newly_completed_lines": 4, "newly_exposed_one_hole_lines": 41, "affected_lines": 990}, "result coverage packet")
    working = result.get("working_dictionary", {})
    check((working.get("v30_entries"), working.get("v31_entries"), working.get("accepted_tail_entries"), working.get("v30_glossary_surfaces"), working.get("v31_glossary_surfaces")) == (491, 510, 19, 420, 437), "result dictionary metrics")
    check(working.get("v30_prefix_sha256") == canonical_hash(base_dictionary) and working.get("v31_sha256") == canonical_hash(dictionary), "result dictionary hashes")
    claim = str(result.get("claim_boundary", "")).lower()
    check(all(term in claim for term in ("exploratory", "17 new", "revises or and qokar", "no free component", "plaintext", "f1r", "new page", "new image")), "result claim core")

    scan_paths = [ROOT / BASE / name for name in ("REPORT.md", "METHOD.md", "README.md", "artifacts/README.md", "artifacts/RESULT.json")] + sorted(ART.glob("*.tsv"))
    filler_hits = [str(path.relative_to(ROOT)) for path in scan_paths if FILLER.search(path.read_text(encoding="utf-8"))]
    check(not filler_hits, "no generic filler", repr(filler_hits))
    inputs = result.get("inputs", {})
    check(bool(inputs) and all(not Path(path).is_absolute() and (ROOT / path).is_file() for path in inputs), "result input path core")
    for path, digest in inputs.items():
        check(sha256(ROOT / path) == digest, f"result input hash:{path}")
    outputs = result.get("outputs", {})
    expected_outputs = {str(BASE / "artifacts" / name) for name in OUTPUTS if name != "RESULT.json"}
    check(set(outputs) == expected_outputs, "result output path set")
    for path, digest in outputs.items():
        check(sha256(ROOT / path) == digest, f"result output hash:{path}")

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    check(manifest.get("experiment_id") == "GDT654" and manifest.get("slug") == "ar_or_surface_consolidation", "manifest identity")
    check(manifest.get("status") == STATUS, "manifest status")
    check(manifest.get("sealed_data") == {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"}, "manifest seals")
    check(manifest.get("commands") == {"run": f"python3 {BASE}/src/run.py", "validate": f"python3 {BASE}/src/validate.py"}, "manifest commands")
    check(manifest.get("validation") == {"artifact": str(BASE / "artifacts/VALIDATION.json"), "status": "PASS"}, "manifest validation")
    check(set(manifest.get("dependencies", [])) == {"GDT628", "GDT636", "GDT640", "GDT648", "GDT649", "GDT653"}, "manifest dependencies")
    question, ceiling = str(manifest.get("question", "")).lower(), str(manifest.get("claim_ceiling", "")).lower()
    check(len(question) >= 80 and all(term in question for term in ("nineteen", "ar", "or", "qokar", "concrete")), "manifest question core")
    check(len(ceiling) >= 120 and all(term in ceiling for term in ("explor", "exact whole", "free component", "plaintext", "exact ingredient")), "manifest claim ceiling core")
    manifest_inputs = {row.get("path"): row for row in manifest.get("inputs", [])}
    check(set(manifest_inputs) == set(inputs), "manifest/result inputs")
    for path, row in manifest_inputs.items():
        check(row.get("sha256") == inputs[path] == sha256(ROOT / path) and bool(row.get("role")), f"manifest input seal:{path}")
    manifest_outputs = {row.get("path"): row for row in manifest.get("outputs", [])}
    required = {str(BASE / path) for path in (
        "METHOD.md", "README.md", "REPORT.md", "artifacts/README.md", "artifacts/TARGET_DECISION_DECK.tsv",
        "artifacts/FULL_AR_OR_PAIR_GRID.tsv", "artifacts/BOUNDARY_EVIDENCE_ATLAS.tsv", "artifacts/REVISION_LEDGER.tsv",
        "artifacts/ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv", "artifacts/CURATED_COMPLETE_PASSAGE_READINGS.tsv",
        "artifacts/NEWLY_COMPLETED_LINES.tsv", "artifacts/RESULT.json", "artifacts/V31_EXACT_TOKEN_GLOSSARY.tsv",
        "artifacts/ALL_LINE_CONCRETE_COVERAGE_V31.tsv", "artifacts/COMPLETE_PASSAGES_V31.tsv",
        "artifacts/ONE_UNKNOWN_PASSAGES_V31.tsv", "artifacts/WORKING_DICTIONARY_V31.tsv",
        "artifacts/VALIDATION.json", "src/run.py", "src/validate.py",
    )}
    check(required <= set(manifest_outputs), "manifest core outputs")
    for path, row in manifest_outputs.items():
        target_path = ROOT / str(path)
        check(not Path(str(path)).is_absolute() and target_path.is_file() and bool(row.get("role")), f"manifest output path:{path}")
        if str(path) != str(BASE / "artifacts/VALIDATION.json") and target_path.is_file():
            check(row.get("sha256") == sha256(target_path), f"manifest output seal:{path}")

    report_text = REPORT.read_text(encoding="utf-8").lower()
    for needle in ("drogenfraktion i", "drogenportion", "qokar", "qokor", "1.347", "1.882", "1.516", "14.973", "15.846", "f37r.7", "f99v.3", "explorativ"):
        check(needle in report_text, f"report contains:{needle}")

    # Builder replay deliberately runs last; all semantic and census checks above
    # are performed without importing the implementation being validated.
    try:
        builder = load_builder()
        with tempfile.TemporaryDirectory(prefix="gdt654_validate_") as temporary:
            replay = Path(temporary)
            builder.build(replay)
            check({path.name for path in replay.iterdir()} == set(OUTPUTS), "replay output set")
            for name in OUTPUTS:
                check((ART / name).read_bytes() == (replay / name).read_bytes(), f"byte replay:{name}")
    except Exception as exc:
        issues.append(f"builder replay: {type(exc).__name__}: {exc}")

    validation = {
        "schema": "GDT654_VALIDATION_V1", "experiment_id": "GDT654",
        "status": "PASS" if not issues else "FAIL", "checks_passed": len(passed),
        "checks_failed": len(issues), "passed": passed, "issues": issues,
    }
    VALIDATION.write_text(json.dumps(validation, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if issues:
        print(f"GDT654 validation FAIL: {len(issues)} issue(s), {len(passed)} checks passed")
        for issue in issues:
            print(f"- {issue}")
        return 1
    print(f"GDT654 validation PASS: {len(passed)} checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
