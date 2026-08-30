#!/usr/bin/env python3
"""Independent release validator for GDT645."""
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
BASE = Path("experiments/yolo/gdt645_ranked_five_surface_completion")
ART = ROOT / BASE / "artifacts"
RUN = ROOT / BASE / "src/run.py"
MANIFEST = ROOT / BASE / "experiment.json"
VALIDATION = ART / "VALIDATION.json"
G644 = Path("experiments/yolo/gdt644_downstream_five_surface_completion")
G644_ALLOW = G644 / "artifacts/PAGE_ALLOWLIST.tsv"
G644_GLOSSARY = G644 / "artifacts/V21_EXACT_TOKEN_GLOSSARY.tsv"
G644_DICTIONARY = G644 / "artifacts/WORKING_DICTIONARY_V21.tsv"
TOKENS = Path("transcription/voynich_zl3b_tokens.tsv")
CROSS = Path("transcription/voynich_cross_transcription_lines.tsv")

EXPECTED = {
    "oky": ("heißer Ansatz, Grundform", "o+k+y", "f36v.13", 89, 66, 80, 80,
            "exact complete ZL3b surface only"),
    "otchor": ("kalt-trockene Drogenportion im Ansatz", "o+t+ch+or", "f35r.14", 16, 14, 16, 16,
               "exact complete ZL3b surface only"),
    "ychair": ("zweiter trockener Anteil dieser Droge", "y+(ch+air)", "f18r.12", 1, 1, 1, 1,
               "exact complete ZL3b surface only; initial y and air remain whole-bound"),
    "cheaiin": ("trocken im dritten Grad", "ch+e+(a+iin)", "f19v.14", 4, 4, 3, 3,
                "exact complete ZL3b surface only; e and a+iin remain whole-bound"),
    "cthom": ("eine Handvoll Blatt- oder Krautansatz", "cth+o+[m]_whole", "f4r.7", 5, 5, 5, 5,
              "exact complete ZL3b surface only; terminal m remains whole-bound"),
}
EXPECTED_ROUNDS = (
    ("BASE_V21", 298, 10230, 22109, 54, 38, 75, 26, 251),
    ("oky", 299, 10319, 22020, 55, 39, 74, 25, 252),
    ("otchor", 300, 10335, 22004, 56, 40, 75, 24, 253),
    ("ychair", 301, 10336, 22003, 57, 41, 74, 23, 254),
    ("cheaiin", 302, 10340, 21999, 58, 41, 73, 23, 255),
    ("cthom", 303, 10345, 21994, 60, 42, 71, 22, 256),
)
EXPECTED_COMPLETE = {
    "f36v.13": ("oky", "1"), "f35r.14": ("otchor", "1"),
    "f18r.12": ("ychair", "1"), "f19v.14": ("cheaiin", "0"),
    "f4r.7": ("cthom", "1"), "f6r.12": ("cthom", "0"),
}
EXPECTED_NEW_ONE = {
    "f15v.5": ("otchor", "s", "0"),
    "f35r.5": ("otchor", "tcheey", "0"),
}
FAMILY_PAIRS = {
    *(("OKY_GRID", f"{f}{q}y") for f in ("", "o", "qo") for q in ("k", "t")),
    *(("OTCHOR_GRID", f"{f}{q}{d}{c}") for f in ("", "o", "qo", "y")
      for q in ("k", "t") for d in ("", "ch") for c in ("ol", "or")),
    *(("YCHAIR_GRID", f"{f}{q}{c}") for f in ("", "y")
      for q in ("k", "t", "ch", "sh") for c in ("ar", "air")),
    *(("CHEAIIN_LADDER", s) for s in (
        "chean", "cheain", "cheaiin", "cheaiiin", "shean", "sheain", "sheaiin", "sheaiiin",
    )),
    *(("CTHOM_FAMILY", s) for s in ("ctho", "cthom", "cthal", "cthar", "cthol", "cthor")),
}
ABSENT = {"yshair", "cheaiiin", "shean", "sheaiiin"}
OUTPUTS = (
    "PAGE_ALLOWLIST.tsv", "TARGET_DECISION_DECK.tsv", "FORM_FAMILY_ATLAS.tsv",
    "COMPONENT_BINDING_AUDIT.tsv", "READER_VARIANT_AUDIT.tsv",
    "ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv", "SEQUENTIAL_DECISION_LEDGER.tsv",
    "ROUND_COVERAGE_COUNTS.tsv", "ACCEPTED_WHOLE_SURFACE_DEFAULTS.tsv",
    "NEWLY_COMPLETED_LINES.tsv", "NEWLY_EXPOSED_ONE_HOLE_LINES.tsv",
    "V22_EXACT_TOKEN_GLOSSARY.tsv", "ALL_LINE_CONCRETE_COVERAGE_V22.tsv",
    "COMPLETE_PASSAGES_V22.tsv", "ONE_UNKNOWN_PASSAGES_V22.tsv",
    "WORKING_DICTIONARY_V22.tsv", "RESULT.json",
)
HELPERS = tuple(
    f"experiments/yolo/gdt{n}_{slug}/src/run.py"
    for n, slug in (
        (631, "prefixed_cth_quality_parts"), (632, "cth_interfix_lattice"),
        (633, "cth_interfix_semantic_contrasts"), (634, "known_core_terminal_semantics"),
        (635, "initial_head_same_remainder_swaps"), (636, "residual_four_head_semantics"),
        (637, "ladder_completion_one_unknown_passages"), (638, "sequential_compound_promotion"),
        (639, "strict_hole_component_repair"), (640, "downstream_component_prediction"),
        (641, "strict_tch_bound_form_completion"), (642, "exact_e_ol_or_carrier_completion"),
        (643, "exposed_five_hole_completion"),
    )
)
EXPECTED_INPUTS = set(HELPERS) | {
    "experiments/yolo/gdt529_nearest_terminal_m_square/REPORT.md",
    "experiments/yolo/gdt624_productive_quality_shell_grid/REPORT.md",
    "experiments/yolo/gdt624_productive_quality_shell_grid/artifacts/GRID_CELLS.tsv",
    "experiments/yolo/gdt626_mobile_operation_lexicon/REPORT.md",
    "experiments/yolo/gdt628_chol_measure_frame/REPORT.md",
    "experiments/yolo/gdt631_prefixed_cth_quality_parts/REPORT.md",
    "experiments/yolo/gdt633_cth_interfix_semantic_contrasts/REPORT.md",
    "experiments/yolo/gdt636_residual_four_head_semantics/REPORT.md",
    "experiments/yolo/gdt639_strict_hole_component_repair/REPORT.md",
    "experiments/yolo/gdt640_downstream_component_prediction/REPORT.md",
    str(G644 / "src/run.py"), str(G644 / "artifacts/PAGE_ALLOWLIST.tsv"),
    str(G644 / "artifacts/ALL_LINE_CONCRETE_COVERAGE_V21.tsv"),
    str(G644 / "artifacts/COMPLETE_PASSAGES_V21.tsv"),
    str(G644 / "artifacts/ONE_UNKNOWN_PASSAGES_V21.tsv"),
    str(G644 / "artifacts/NEWLY_EXPOSED_ONE_HOLE_LINES.tsv"),
    str(G644 / "artifacts/V21_EXACT_TOKEN_GLOSSARY.tsv"),
    str(G644 / "artifacts/WORKING_DICTIONARY_V21.tsv"),
    str(G644 / "artifacts/RESULT.json"), str(G644 / "REPORT.md"), str(TOKENS), str(CROSS),
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
    payload = json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


def load_builder():
    spec = importlib.util.spec_from_file_location("gdt645_builder_validation", RUN)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load GDT645 builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def guarded_query(path: Path, pages: set[str], columns: str) -> list[dict[str, str]]:
    command = [str(ROOT / "vmanus-exp"), "query-tsv", str(path), "--selector", "page"]
    for page in sorted(pages):
        command.extend(("--allow", page))
    command.extend(("--columns", columns, "--forbid-prefix", "f84", "--forbid-prefix", "f84r"))
    done = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    if done.returncode or len([line for line in done.stderr.splitlines() if line.startswith("GUARD_STATS ")]) != 1:
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
        direct = [cross[row["locus"]][f].split().count(surface) for f in ("zl3b_clean", "it2a_clean", "rf1b_clean")]
        normalized = [span_count(cross[row["locus"]][f].split(), surface) for f in ("zl3b_clean", "it2a_clean", "rf1b_clean")]
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
        check(tuple(builder.OUTPUT_NAMES) == OUTPUTS[:-1], "builder output contract")
        with tempfile.TemporaryDirectory(prefix="gdt645_validate_") as tmp:
            replay = Path(tmp)
            builder.build(replay)
            check({path.name for path in replay.iterdir()} == set(OUTPUTS), "replay output set")
            for name in OUTPUTS:
                check((ART / name).read_bytes() == (replay / name).read_bytes(), f"byte replay:{name}")
    except Exception as exc:
        issues.append(f"builder replay: {type(exc).__name__}: {exc}")

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    result = json.loads((ART / "RESULT.json").read_text(encoding="utf-8"))
    check(manifest.get("experiment_id") == "GDT645", "manifest id")
    check(manifest.get("sealed_data") == {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"}, "manifest seals")
    check(manifest.get("validation") == {"artifact": str(BASE / "artifacts/VALIDATION.json"), "status": "PASS"}, "manifest validation")
    check(result.get("schema") == "GDT645_RANKED_FIVE_SURFACE_COMPLETION_RESULT_V1", "result schema")
    check(result.get("status") == "PASS_5_RANKED_SURFACES__115_POSITIONS__6_NEW_COMPLETE_LINES", "result status")
    check(result.get("content_sha256") == canonical_hash({k: v for k, v in result.items() if k != "content_sha256"}), "result hash")

    pages = {row["page"] for row in read_tsv(ART / "PAGE_ALLOWLIST.tsv")}
    check(len(pages) == 179 and "f1r" not in pages and not any(page.startswith("f84") for page in pages), "guarded pages")
    check((ART / "PAGE_ALLOWLIST.tsv").read_bytes() == (ROOT / G644_ALLOW).read_bytes(), "allowlist replay")
    token_rows = guarded_query(TOKENS, pages, "page,locus,token_index,eva")
    cross_rows = guarded_query(CROSS, pages, "page,locus,zl3b_clean,it2a_clean,rf1b_clean")
    family = read_tsv(ART / "FORM_FAMILY_ATLAS.tsv")
    surfaces = {row["surface"] for row in family} | set(EXPECTED)
    occ, exact, split, page_counts = independent_counts(token_rows, cross_rows, surfaces)

    deck = read_tsv(ART / "TARGET_DECISION_DECK.tsv")
    check(len(deck) == 5 and [row["surface"] for row in deck] == list(EXPECTED), "ordered targets")
    for order, row in enumerate(deck, 1):
        meaning, composition, locus, n, p, e, s, scope = EXPECTED[row["surface"]]
        check((row["candidate_id"], int(row["candidate_order"]), row["source_locus"]) == (f"G645-C{order:02d}", order, locus), f"card id:{row['surface']}")
        check((row["working_meaning_de"], row["composition"], row["scope"]) == (meaning, composition, scope), f"card semantics:{row['surface']}")
        check(row["reader_gate"] == "AT_LEAST_ONE_ALL_READER_EXACT" and row["decision"] == "ACCEPT" and not FILLER.search(meaning), f"card gate:{row['surface']}")
        check((int(row["occurrences"]), int(row["pages"]), int(row["reader_exact_occurrences"]), int(row["split_normalized_occurrences"])) == (n, p, e, s) == (occ[row["surface"]], page_counts[row["surface"]], exact[row["surface"]], split[row["surface"]]), f"card census:{row['surface']}")

    pairs = {(row["family"], row["surface"]) for row in family}
    check(len(family) == len(pairs) == 68 and pairs == FAMILY_PAIRS, "68-cell atlas")
    check({row["surface"] for row in family if row["surface_status"] == "ABSENT_PREDICTION_HOLD"} == ABSENT, "four held null cells")
    for row in family:
        surface = row["surface"]
        check(row["surface_status"] == ("ABSENT_PREDICTION_HOLD" if surface in ABSENT else "OBSERVED"), f"family status:{surface}")
        check((int(row["zl3b_occurrences"]), int(row["pages"]), int(row["reader_exact_occurrences"]), row["cross_reader_only"]) == (occ[surface], page_counts[surface], exact[surface], "0"), f"family census:{surface}")

    components = read_tsv(ART / "COMPONENT_BINDING_AUDIT.tsv")
    check(len(components) == 14 and [row["component_id"] for row in components] == [f"G645-B{i:02d}" for i in range(1, 15)], "14 components")
    check(len({(row["surface"], row["segment"]) for row in components}) == 14, "unique components")
    for row in components:
        check(row["surface"] in EXPECTED and row["licensed_use"] == f"inside exact {row['surface']} only", f"component scope:{row['component_id']}")
        check(row["evidence_path"] in EXPECTED_INPUTS and (ROOT / row["evidence_path"]).is_file(), f"component source:{row['component_id']}")

    audits = read_tsv(ART / "ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv")
    variants = read_tsv(ART / "READER_VARIANT_AUDIT.tsv")
    check(len(audits) == len({row["audit_id"] for row in audits}) == 115, "115 audits")
    check(Counter(row["surface"] for row in audits) == Counter({surface: values[3] for surface, values in EXPECTED.items()}), "audit census")
    check(sum(int(row["reader_exact"]) for row in audits) == sum(int(row["split_normalized"]) for row in audits) == 105, "105 exact targets")
    check(Counter(row["verdict"] for row in audits) == Counter({"CLEAN_CONTEXT_COMPATIBLE": 60, "OPAQUE_OR_UNSTABLE_CONTEXT": 45, "READER_VARIANT_WARNING": 10}), "audit verdicts")
    check(len(variants) == 10 and {(row["surface"], row["locus"]) for row in variants} == {(row["surface"], row["locus"]) for row in audits if row["reader_exact"] == "0"}, "warning deck")
    for row in audits:
        reader_exact, normalized = int(row["reader_exact"]), int(row["split_normalized"])
        clean, known = int(row["clean_known_other_tokens"]), int(row["known_other_tokens"])
        support = "ALL_THREE_EXACT" if reader_exact else "ALL_THREE_SPLIT_NORMALIZED" if normalized else "READER_VARIANT"
        verdict = "CLEAN_CONTEXT_COMPATIBLE" if support == "ALL_THREE_EXACT" and clean >= 2 else "OPAQUE_OR_UNSTABLE_CONTEXT" if support == "ALL_THREE_EXACT" else "READER_SPLIT_NORMALIZED" if support == "ALL_THREE_SPLIT_NORMALIZED" else "READER_VARIANT_WARNING"
        check(0 <= clean <= known and row["reader_support"] == support and row["verdict"] == verdict, f"audit logic:{row['audit_id']}")
        check(row["before_gloss"] == f"[{row['surface']}:?]" and row["after_gloss"] == EXPECTED[row["surface"]][0], f"audit replacement:{row['audit_id']}")
        check(row["hard_collision"] == row["thermal_reader_rival"] == "0", f"audit collision:{row['audit_id']}")

    rounds = read_tsv(ART / "ROUND_COVERAGE_COUNTS.tsv")
    ledger = read_tsv(ART / "SEQUENTIAL_DECISION_LEDGER.tsv")
    check(len(rounds) == 6 and len(ledger) == 5 and [row["surface"] for row in ledger] == list(EXPECTED), "sequential states")
    for row, expected_row in zip(rounds, EXPECTED_ROUNDS):
        observed = (row["surface"], int(row["dictionary_entries"]), int(row["known_token_positions"]), int(row["unknown_token_positions"]), int(row["complete_multi_token_lines"]), int(row["strict_complete_lines"]), int(row["one_unknown_lines"]), int(row["strict_one_unknown_lines"]), int(row["exact_glossary_surfaces"]))
        check(observed == expected_row, f"round:{row['surface']}", repr(observed))

    new_complete = read_tsv(ART / "NEWLY_COMPLETED_LINES.tsv")
    complete_by_locus = {row["locus"]: row for row in read_tsv(ART / "COMPLETE_PASSAGES_V22.tsv")}
    check(len(new_complete) == 6 and {row["locus"] for row in new_complete} == set(EXPECTED_COMPLETE), "six completed lines")
    for row in new_complete:
        surface, strict = EXPECTED_COMPLETE[row["locus"]]
        check((row["surface"], row["strict_complete"]) == (surface, strict) and complete_by_locus[row["locus"]]["strict_complete"] == strict, f"completion:{row['locus']}")
        check(EXPECTED[surface][0] in row["literal_v22_de"] and not FILLER.search(row["smoothed_working_reading_de"]), f"completion text:{row['locus']}")
    new_one = read_tsv(ART / "NEWLY_EXPOSED_ONE_HOLE_LINES.tsv")
    one_by_locus = {row["locus"]: row for row in read_tsv(ART / "ONE_UNKNOWN_PASSAGES_V22.tsv")}
    check(len(new_one) == 2 and {row["locus"] for row in new_one} == set(EXPECTED_NEW_ONE), "two new one-hole lines")
    for row in new_one:
        expected_row = EXPECTED_NEW_ONE[row["locus"]]
        check((row["enabled_by_surface"], row["unknown_surface"], row["strict_eligible"]) == expected_row and one_by_locus[row["locus"]]["unknown_surface"] == expected_row[1], f"one-hole:{row['locus']}")

    old_gloss_rows, gloss_rows = read_tsv(ROOT / G644_GLOSSARY), read_tsv(ART / "V22_EXACT_TOKEN_GLOSSARY.tsv")
    old_gloss = {row["surface"]: row for row in old_gloss_rows}
    glossary = {row["surface"]: row for row in gloss_rows}
    check(len(old_gloss_rows) == len(old_gloss) == 251 and len(gloss_rows) == len(glossary) == 256, "glossary 251 to 256")
    check(all(glossary[surface] == row for surface, row in old_gloss.items()), "glossary prefix")
    for surface, values in EXPECTED.items():
        check(glossary[surface]["working_meaning_de"] == values[0] and glossary[surface]["scope_state"] == "KNOWN_EXACT_WHOLE", f"gloss:{surface}")

    old_dictionary, dictionary = read_tsv(ROOT / G644_DICTIONARY), read_tsv(ART / "WORKING_DICTIONARY_V22.tsv")
    check(len(old_dictionary) == 298 and len(dictionary) == 303 and dictionary[:298] == old_dictionary, "dictionary prefix")
    check([row["entry"].split("@", 1)[0] for row in dictionary[298:]] == list(EXPECTED), "dictionary tail")
    for order, row in enumerate(ledger, 1):
        check((row["pre_dictionary_sha256"], row["post_dictionary_sha256"]) == (canonical_hash(dictionary[:297 + order]), canonical_hash(dictionary[:298 + order])), f"ledger hashes:{row['surface']}")
    for order, row in enumerate(rounds):
        check(row["dictionary_sha256"] == canonical_hash(dictionary[:298 + order]), f"round hash:{row['surface']}")

    coverage = read_tsv(ART / "ALL_LINE_CONCRETE_COVERAGE_V22.tsv")
    complete = read_tsv(ART / "COMPLETE_PASSAGES_V22.tsv")
    one = read_tsv(ART / "ONE_UNKNOWN_PASSAGES_V22.tsv")
    check(len(coverage) == 4128 and sum(int(row["known_tokens"]) for row in coverage) == 10345 and sum(int(row["unknown_tokens"]) for row in coverage) == 21994, "V22 coverage")
    check(len(complete) == 60 and sum(int(row["strict_complete"]) for row in complete) == 42, "V22 completions")
    check(len(one) == 71 and sum(int(row["strict_eligible"]) for row in one) == 22, "V22 frontier")
    check(all(row["page"] != "f1r" and not row["page"].startswith("f84") for row in coverage), "coverage guard")

    for path in ART.glob("*.tsv"):
        rows, raw = read_tsv(path), path.read_bytes()
        check(b"\t\t" not in raw and all(None not in row and all(value not in (None, "") for value in row.values()) for row in rows), f"complete TSV:{path.name}")
    check(set(result.get("inputs", {})) == EXPECTED_INPUTS, "result input set")
    check(set(result.get("outputs", {})) == {str(BASE / "artifacts" / name) for name in OUTPUTS[:-1]}, "result output set")
    for relative, digest in result.get("inputs", {}).items():
        check((ROOT / relative).is_file() and sha256(ROOT / relative) == digest, f"input hash:{relative}")
    for relative, digest in result.get("outputs", {}).items():
        check((ROOT / relative).is_file() and sha256(ROOT / relative) == digest, f"output hash:{relative}")
    check(result.get("target_run") == {"candidates": 5, "accepted": 5, "held": 0, "audited_occurrences": 115, "all_reader_exact_occurrences": 105, "split_normalized_occurrences": 105, "thermal_reader_rivals": 0, "hard_collisions": 0, "verdicts": {"CLEAN_CONTEXT_COMPATIBLE": 60, "OPAQUE_OR_UNSTABLE_CONTEXT": 45, "READER_VARIANT_WARNING": 10}, "accepted_surfaces": list(EXPECTED)}, "result target state")
    check(result.get("coverage") == {"base_complete_multi_token_lines": 54, "base_strict_complete_lines": 38, "newly_completed_lines": 6, "newly_exposed_one_hole_lines": 2, "physical_lines": 4128, "known_token_positions": 10345, "unknown_token_positions": 21994, "complete_multi_token_lines": 60, "strict_complete_lines": 42, "one_unknown_lines": 71, "strict_one_unknown_lines": 22, "exact_glossary_surfaces": 256}, "result coverage")
    check(result.get("guard") == {"f1r": "EXCLUDED", "f84": "FORBIDDEN", "f84r": "FORBIDDEN", "new_pages": 0, "new_images": 0, "allowed_pages": 179, "token_query": {"selected": 32339, "skipped_forbidden": 709, "skipped_not_allowed": 5940}, "cross_query": {"selected": 4137, "skipped_forbidden": 98, "skipped_not_allowed": 1151}}, "result guard")
    check(result.get("working_dictionary") == {"v21_entries": 298, "v22_entries": 303, "accepted_tail_entries": 5, "v21_prefix_sha256": canonical_hash(old_dictionary), "v22_sha256": canonical_hash(dictionary), "base_glossary_surfaces": 251, "v22_glossary_surfaces": 256}, "result dictionary")

    core = {
        "schema": "GDT645_VALIDATION_V1", "experiment_id": "GDT645",
        "status": "PASS" if not issues else "FAIL", "passed_checks": len(passed),
        "issue_count": len(issues), "issues": issues,
        "summary": {"target_occurrences": len(audits), "reader_exact": sum(int(row["reader_exact"]) for row in audits), "clean_context_compatible": sum(row["verdict"] == "CLEAN_CONTEXT_COMPATIBLE" for row in audits), "new_complete_lines": len(new_complete), "new_one_hole_lines": len(new_one), "v22_dictionary_entries": len(dictionary), "result_content_sha256": result.get("content_sha256")},
    }
    validation = {**core, "content_sha256": canonical_hash(core)}
    VALIDATION.write_text(json.dumps(validation, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"GDT645 validation: {validation['status']} checks={len(passed)} issues={len(issues)}")
    for issue in issues:
        print(f"ISSUE {issue}")
    return 0 if not issues else 1


if __name__ == "__main__":
    raise SystemExit(main())
