#!/usr/bin/env python3
"""Independent release validator for GDT648."""
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
BASE = Path("experiments/yolo/gdt648_strict_v24_hole_completion")
ART = ROOT / BASE / "artifacts"
RUN = ROOT / BASE / "src/run.py"
MANIFEST = ROOT / BASE / "experiment.json"
VALIDATION = ART / "VALIDATION.json"
G647 = Path("experiments/yolo/gdt647_quality_subdegree_family_migration")
G647_ALLOW = G647 / "artifacts/PAGE_ALLOWLIST.tsv"
G647_GLOSSARY = G647 / "artifacts/V24_EXACT_TOKEN_GLOSSARY.tsv"
G647_DICTIONARY = G647 / "artifacts/WORKING_DICTIONARY_V24.tsv"
G647_NEW_ONE = G647 / "artifacts/NEWLY_EXPOSED_ONE_HOLE_LINES.tsv"
TOKENS = Path("transcription/voynich_zl3b_tokens.tsv")
CROSS = Path("transcription/voynich_cross_transcription_lines.tsv")

STATUS = "PASS_7_STRICT_WHOLE_SURFACES__213_POSITIONS__V25"
TARGETS = {
    "otol": (58, 48, 56, 56, "kaltes Zubereitungsgut", "o+t+ol", "f77v.2"),
    "sheor": (40, 32, 31, 31, "feuchter Drogenteil", "sh+e+or", "f49r.5"),
    "keol": (18, 16, 16, 16, "heißer Drogenstoff", "k+e+ol", "f56r.19"),
    "odaiin": (55, 42, 42, 42, "Zubereitungsdosis III", "o+d+(a+iin)", "f95v1.5"),
    "cholkaiin": (5, 5, 4, 4, "Trockengut, heiß im dritten Grad", "chol+(k+a+iin)", "f106v.36"),
    "lkar": (31, 21, 29, 29, "heiße Holzfraktion I", "l+(k+ar)", "f106r.35"),
    "lsheey": (6, 5, 6, 6, "eingeweichtes Drogenholz, Form II", "l+(sh+ee+y)", "f77r.19"),
}
EXPECTED_FINAL = {
    "physical_lines": 4128, "known_token_positions": 13995,
    "unknown_token_positions": 18344, "complete_multi_token_lines": 87,
    "strict_complete_lines": 49, "one_unknown_lines": 151,
    "strict_one_unknown_lines": 44, "exact_glossary_surfaces": 354,
}
FAMILY_ROWS = Counter({
    "OTOL_32_CARRIER_GRID": 32, "L_QUALITY_FRACTION_GRID": 24,
    "MATERIAL_QUALITY_FORM_GRID": 24, "E_OL_OR_QUALITY_GRID": 16,
    "ODAIIN_DOSAGE_LADDER": 8, "CHOL_KAIIN_FUSION": 6,
})
OBSERVED_FAMILY_ROWS = Counter({
    "OTOL_32_CARRIER_GRID": 32, "MATERIAL_QUALITY_FORM_GRID": 21,
    "E_OL_OR_QUALITY_GRID": 16, "L_QUALITY_FRACTION_GRID": 16,
    "ODAIIN_DOSAGE_LADDER": 8, "CHOL_KAIIN_FUSION": 4,
})
NEW_COMPLETE_LOCI = {
    "f106r.35", "f106v.36", "f10r.12", "f49r.5", "f56r.19",
    "f75r.46", "f77r.19", "f77v.2", "f89v1.12", "f95v1.5",
}
FILLER = re.compile(
    r"arbeitsgut|arbeitschritt|arbeitsschritt|arbeitsmittel|arbeitsstoff|"
    r"arbeitsobjekt|werkzeug|produkt weiter|f.hre .* aus|leite .* weiter",
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
    spec = importlib.util.spec_from_file_location("gdt648_builder_validation", RUN)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load GDT648 builder")
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
        with tempfile.TemporaryDirectory(prefix="gdt648_validate_") as tmp:
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
    check(manifest.get("experiment_id") == "GDT648", "manifest id")
    check(manifest.get("sealed_data") == {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"}, "manifest seals")
    check(manifest.get("validation") == {"artifact": str(BASE / "artifacts/VALIDATION.json"), "status": "PASS"}, "manifest validation")
    check(result.get("schema") == "GDT648_STRICT_V24_HOLE_COMPLETION_RESULT_V1", "result schema")
    check(result.get("status") == STATUS, "result status")
    check(result.get("content_sha256") == canonical_hash({key: value for key, value in result.items() if key != "content_sha256"}), "result hash")

    pages = {row["page"] for row in read_tsv(ART / "PAGE_ALLOWLIST.tsv")}
    check(len(pages) == 179 and "f1r" not in pages and not any(page.startswith("f84") for page in pages), "guarded pages")
    check((ART / "PAGE_ALLOWLIST.tsv").read_bytes() == (ROOT / G647_ALLOW).read_bytes(), "allowlist inheritance")
    token_rows = guarded_query(TOKENS, pages, "page,locus,token_index,eva")
    cross_rows = guarded_query(CROSS, pages, "page,locus,zl3b_clean,it2a_clean,rf1b_clean")
    occurrence, exact, normalized, page_count = independent_counts(token_rows, cross_rows, set(TARGETS))

    deck = read_tsv(ART / "TARGET_DECISION_DECK.tsv")
    deck_by_surface = {row["surface"]: row for row in deck}
    check(len(deck) == len(deck_by_surface) == 7 and set(deck_by_surface) == set(TARGETS), "seven target rows")
    check([row["candidate_id"] for row in deck] == [f"G648-C{index:02d}" for index in range(1, 8)], "ordered candidate ids")
    for surface, expected in TARGETS.items():
        occ, pages_expected, exact_expected, norm_expected, meaning, parse, source = expected
        row = deck_by_surface[surface]
        observed = (occurrence[surface], page_count[surface], exact[surface], normalized[surface])
        check(observed == expected[:4], f"independent target census:{surface}", repr(observed))
        check((int(row["occurrences"]), int(row["pages"]), int(row["reader_exact_occurrences"]), int(row["split_normalized_occurrences"])) == expected[:4], f"deck census:{surface}")
        check((row["working_meaning_de"], row["composition"], row["source_locus"], row["decision"]) == (meaning, parse, source, "ACCEPT"), f"target semantics:{surface}")
    check(sum(occurrence.values()) == 213 and sum(exact.values()) == 184 and sum(normalized.values()) == 184, "target totals")
    check(not any(FILLER.search(row["working_meaning_de"]) for row in deck), "no target filler")

    frontier = read_tsv(ART / "STRICT_FRONTIER_ADJUDICATION.tsv")
    check(len(frontier) == len({row["surface"] for row in frontier}) == 26, "complete 26-surface frontier")
    check(Counter(row["decision"] for row in frontier) == Counter({"HOLD_SEPARATE_AUDIT": 13, "ACCEPT_V25": 7, "REJECT_CURRENT_ROUTE": 6}), "frontier decision counts")
    check({row["surface"] for row in frontier if row["decision"] == "ACCEPT_V25"} == set(TARGETS), "frontier accepted set")
    check({row["surface"] for row in frontier if row["decision"] == "REJECT_CURRENT_ROUTE"} == {"dy", "ykeody", "ykeey", "checkhy", "sheckhy", "olsaly"}, "frontier reject set")
    frontier_by_surface = {row["surface"]: row for row in frontier}
    check(frontier_by_surface["sheor"]["parse"] == "sh+e+or" and frontier_by_surface["sheckhy"]["parse"] == "sh+e+ckh+y" and frontier_by_surface["shedal"]["parse"] == "sh+e+d+al", "longest-first SH parses")
    base_frontier = [row for row in read_tsv(ROOT / G647_NEW_ONE) if row["strict_eligible"] == "1"]
    check(len(base_frontier) == 26 and {row["unknown_surface"] for row in base_frontier} == set(frontier_by_surface), "frontier source identity")
    for surface, expected in TARGETS.items():
        check(any(row["unknown_surface"] == surface and row["locus"] == expected[6] for row in base_frontier), f"strict source:{surface}")

    family = read_tsv(ART / "FAMILY_EVIDENCE_ATLAS.tsv")
    check(len(family) == 110 and Counter(row["family"] for row in family) == FAMILY_ROWS, "family atlas rows")
    check(Counter(row["family"] for row in family if int(row["zl3b_occurrences"])) == OBSERVED_FAMILY_ROWS, "observed family cells")
    check({row["surface"] for row in family if row["surface_status"] == "TARGET"} == set(TARGETS), "family target cells")
    check(all(int(row["reader_exact_occurrences"]) > 0 for row in family if row["surface_status"] == "TARGET"), "family target anchors")

    components = read_tsv(ART / "COMPONENT_BINDING_AUDIT.tsv")
    check(len(components) == 18 and [row["component_id"] for row in components] == [f"G648-B{index:02d}" for index in range(1, 19)], "component bindings")
    check(all(row["licensed_use"] == f"inside exact {row['surface']} only" for row in components), "components whole-bound")
    bridges = {row["surface"]: row for row in read_tsv(ART / "FUSION_BRIDGE_AUDIT.tsv")}
    check((bridges["cholkaiin"]["zl3b_separated_pairs"], bridges["cholkaiin"]["it2a_separated_pairs"], bridges["cholkaiin"]["rf1b_separated_pairs"]) == ("2", "2", "2"), "cholkaiin split bridge")
    check((bridges["lkar"]["zl3b_separated_pairs"], bridges["lkar"]["it2a_separated_pairs"], bridges["lkar"]["rf1b_separated_pairs"]) == ("1", "0", "1"), "lkar boundary warning")

    audits = read_tsv(ART / "ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv")
    check(len(audits) == 213 and len({row["audit_id"] for row in audits}) == 213, "213 unique occurrence audits")
    check(Counter(row["surface"] for row in audits) == Counter({surface: values[0] for surface, values in TARGETS.items()}), "audit surface counts")
    check(Counter(row["verdict"] for row in audits) == Counter({"CLEAN_CONTEXT_COMPATIBLE": 136, "OPAQUE_OR_SHORT_CONTEXT": 48, "READER_VARIANT_WARNING": 29}), "audit verdicts")
    check(sum(int(row["hard_collision"]) for row in audits) == 0, "no recorded hard collision")
    variants = read_tsv(ART / "READER_VARIANT_AUDIT.tsv")
    check(len(variants) == 29 and all(row["reader_support"] == "READER_VARIANT" for row in variants), "29 reader variants")

    old_gloss_rows = read_tsv(ROOT / G647_GLOSSARY)
    gloss_rows = read_tsv(ART / "V25_EXACT_TOKEN_GLOSSARY.tsv")
    old_gloss, glossary = {row["surface"]: row for row in old_gloss_rows}, {row["surface"]: row for row in gloss_rows}
    check(len(old_gloss) == 347 and len(glossary) == 354 and set(glossary) == set(old_gloss) | set(TARGETS), "glossary 347 to 354")
    check(all(glossary[surface] == row for surface, row in old_gloss.items()), "base glossary unchanged")
    check(all(glossary[surface]["working_meaning_de"] == TARGETS[surface][4] for surface in TARGETS), "target glossary meanings")
    check(glossary["lsheey"]["working_meaning_de"] == "eingeweichtes Drogenholz, Form II", "no lsheey degree-end transfer")

    old_dictionary = read_tsv(ROOT / G647_DICTIONARY)
    dictionary = read_tsv(ART / "WORKING_DICTIONARY_V25.tsv")
    check(len(old_dictionary) == 410 and len(dictionary) == 417 and dictionary[:410] == old_dictionary, "dictionary append-only 410 to 417")
    tail_surfaces = [row["entry"].split("@", 1)[0] for row in dictionary[410:]]
    check(set(tail_surfaces) == set(TARGETS) and len(tail_surfaces) == len(set(tail_surfaces)), "seven dictionary overlays")
    check(any(row["entry"] == "odaiin@GDT636_REMAINDER" for row in dictionary[:410]) and any(row["entry"] == "odaiin@GDT648_EXACT_WHOLE" for row in dictionary[410:]), "odaiin firewall plus exact whole")

    coverage = read_tsv(ART / "ALL_LINE_CONCRETE_COVERAGE_V25.tsv")
    complete = read_tsv(ART / "COMPLETE_PASSAGES_V25.tsv")
    one = read_tsv(ART / "ONE_UNKNOWN_PASSAGES_V25.tsv")
    observed_final = {
        "physical_lines": len(coverage), "known_token_positions": sum(int(row["known_tokens"]) for row in coverage),
        "unknown_token_positions": sum(int(row["unknown_tokens"]) for row in coverage),
        "complete_multi_token_lines": len(complete), "strict_complete_lines": sum(int(row["strict_complete"]) for row in complete),
        "one_unknown_lines": len(one), "strict_one_unknown_lines": sum(int(row["strict_eligible"]) for row in one),
        "exact_glossary_surfaces": len(glossary),
    }
    check(observed_final == EXPECTED_FINAL, "V25 coverage metrics", repr(observed_final))
    new_complete = read_tsv(ART / "NEWLY_COMPLETED_LINES.tsv")
    check(len(new_complete) == 10 and {row["locus"] for row in new_complete} == NEW_COMPLETE_LOCI, "ten new complete loci")
    check(sum(int(row["strict_complete"]) for row in new_complete) == 7, "seven new strict complete")
    reality = read_tsv(ART / "SOURCE_PASSAGE_REALITY_CHECK.tsv")
    check(len(reality) == 7 and {row["surface"] for row in reality} == set(TARGETS), "seven source reality checks")
    check(all(row["strict_complete"] == "1" and row["assessment"] == "CONCRETE_AND_COMPOSITIONAL" for row in reality), "strict source checks complete")
    check(not any(FILLER.search(row["smoothed_working_reading_de"]) for row in reality), "no source-reading filler")
    exposed = read_tsv(ART / "NEWLY_EXPOSED_ONE_HOLE_LINES.tsv")
    check(len(exposed) == 9 and sum(int(row["strict_eligible"]) for row in exposed) == 3, "nine new one-hole lines")

    rounds = read_tsv(ART / "ROUND_COVERAGE_COUNTS.tsv")
    check(len(rounds) == 8 and [int(row["known_token_positions"]) for row in rounds] == [13782, 13840, 13880, 13898, 13953, 13958, 13989, 13995], "sequential known counts")
    check([int(row["complete_multi_token_lines"]) for row in rounds] == [77, 79, 80, 81, 84, 85, 86, 87], "sequential complete counts")
    check([int(row["strict_complete_lines"]) for row in rounds] == [42, 43, 44, 45, 46, 47, 48, 49], "sequential strict counts")
    ledger = read_tsv(ART / "SEQUENTIAL_DECISION_LEDGER.tsv")
    check(len(ledger) == 7 and all(row["decision"] == "ACCEPT" and row["hard_collisions"] == "0" for row in ledger), "seven sequential acceptances")

    target_result = result.get("target_run", {})
    check(target_result.get("accepted_surfaces") == [row["surface"] for row in deck], "result accepted order")
    check(target_result.get("audited_occurrences") == 213 and target_result.get("all_reader_exact_occurrences") == 184, "result target totals")
    check(target_result.get("strict_frontier_decisions") == {"ACCEPT_V25": 7, "HOLD_SEPARATE_AUDIT": 13, "REJECT_CURRENT_ROUTE": 6}, "result frontier decisions")
    check(result.get("coverage", {}).get("final") == EXPECTED_FINAL, "result final metrics")
    check(result.get("coverage", {}).get("newly_completed_lines") == 10, "result completion gain")
    check(result.get("working_dictionary", {}).get("v24_entries") == 410 and result.get("working_dictionary", {}).get("v25_entries") == 417, "result dictionary counts")

    if expected_outputs:
        check(set(result.get("outputs", {})) == {str(BASE / "artifacts" / name) for name in builder.OUTPUT_NAMES}, "result output inventory")
        check(all(result["outputs"][str(BASE / "artifacts" / name)] == sha256(ART / name) for name in builder.OUTPUT_NAMES), "result output hashes")
    check(all((ROOT / path).is_file() and sha256(ROOT / path) == digest for path, digest in result.get("inputs", {}).items()), "result input hashes")

    payload = {
        "schema": "GDT648_VALIDATION_V1", "experiment_id": "GDT648",
        "status": "PASS" if not issues else "FAIL", "passed_checks": len(passed),
        "issues": issues, "artifact_hashes": {
            path.name: sha256(path) for path in sorted(ART.iterdir()) if path.is_file() and path.name != "VALIDATION.json"
        },
    }
    VALIDATION.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if issues:
        for issue in issues:
            print(f"FAIL: {issue}", file=sys.stderr)
        return 1
    print(f"GDT648 validation PASS ({len(passed)} checks)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
