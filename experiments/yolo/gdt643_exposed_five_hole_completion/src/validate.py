#!/usr/bin/env python3
"""Independent release validator for GDT643."""
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
BASE = Path("experiments/yolo/gdt643_exposed_five_hole_completion")
ART = ROOT / BASE / "artifacts"
RUN = ROOT / BASE / "src/run.py"
MANIFEST = ROOT / BASE / "experiment.json"
VALIDATION = ART / "VALIDATION.json"
G642_BASE = Path("experiments/yolo/gdt642_exact_e_ol_or_carrier_completion")
G642_ALLOW = G642_BASE / "artifacts/PAGE_ALLOWLIST.tsv"
G642_GLOSSARY = G642_BASE / "artifacts/V19_EXACT_TOKEN_GLOSSARY.tsv"
G642_DICTIONARY = G642_BASE / "artifacts/WORKING_DICTIONARY_V19.tsv"
TOKENS = Path("transcription/voynich_zl3b_tokens.tsv")
CROSS = Path("transcription/voynich_cross_transcription_lines.tsv")

EXPECTED = {
    "cheodain": {
        "meaning": "Trockenansatz, Dosis II", "composition": "ch+e+o+d+ain",
        "occurrences": 8, "pages": 8, "exact": 5, "split": 5,
        "gate": "AT_LEAST_ONE_ALL_READER_EXACT", "scope": "exact complete ZL3b surface only",
    },
    "oiin": {
        "meaning": "Zubereitungsform III", "composition": "o+iin",
        "occurrences": 26, "pages": 20, "exact": 15, "split": 15,
        "gate": "AT_LEAST_ONE_ALL_READER_EXACT", "scope": "exact complete ZL3b surface only",
    },
    "choky": {
        "meaning": "heiß-trockene Zubereitung, Grundform", "composition": "ch+o+k+y",
        "occurrences": 32, "pages": 28, "exact": 30, "split": 30,
        "gate": "AT_LEAST_ONE_ALL_READER_EXACT", "scope": "exact complete ZL3b surface only",
    },
    "soysar": {
        "meaning": "Samenzubereitung, Grundform; Samenfraktion I",
        "composition": "soy|sar = s+o+y | s+ar", "occurrences": 1, "pages": 1,
        "exact": 0, "split": 1, "gate": "ALL_READER_SPLIT_NORMALIZED",
        "scope": "exact ZL3b boundary package soy|sar only",
    },
    "kcheedy": {
        "meaning": "heiß-trockene gebundene Abschlussform, Bindungsstufe II",
        "composition": "k+ch+ee+d+y", "occurrences": 1, "pages": 1,
        "exact": 0, "split": 0, "gate": "TWO_READER_EXACT_WITH_THERMAL_RIVAL",
        "scope": "exact ZL3b/IT2a kcheedy surface with explicit RF1b tcheedy rival",
    },
}
EXPECTED_ROUNDS = (
    ("BASE_V19", 288, 9967, 22372, 44, 33, 65, 19, 241),
    ("cheodain", 289, 9975, 22364, 45, 34, 64, 18, 242),
    ("oiin", 290, 10001, 22338, 46, 34, 64, 18, 243),
    ("choky", 291, 10033, 22306, 47, 35, 67, 20, 244),
    ("soysar", 292, 10034, 22305, 48, 35, 66, 20, 245),
    ("kcheedy", 293, 10035, 22304, 49, 35, 65, 20, 246),
)
EXPECTED_COMPLETE = {
    "f51v.13": ("cheodain", "1"), "f15v.11": ("oiin", "0"),
    "f88v.26": ("choky", "1"), "f96v.13": ("soysar", "0"),
    "f107r.20": ("kcheedy", "0"),
}
EXPECTED_NEW_ONE = {
    "f15v.8": ("oiin", "ytchor", "0"), "f44v.11": ("choky", "otal", "0"),
    "f15v.4": ("choky", "qotchod", "1"), "f49v.22": ("choky", "cthol", "1"),
    "f49v.12": ("choky", "chokchy", "1"),
}
EXPECTED_FAMILY_PAIRS = {
    ("CHEO_D_VALUE", surface) for surface in ("cheody", "cheodain", "cheodaiin", "cheodaiiin")
} | {
    ("CHO_D_VALUE", surface) for surface in ("chodain", "chodaiin")
} | {
    ("OIIN_HEADS", surface) for surface in ("oiin", "poiin", "soiin", "roiin", "loiin", "cthoiin", "choiin", "doiin")
} | {
    ("CHOK_CHOT", surface) for surface in ("choky", "choty", "chokain", "chotain", "chokaiin", "chotaiin")
} | {
    ("SOY_SAR", surface) for surface in ("soy", "sar", "soysar")
} | {
    ("KCH_E_LENGTH", surface) for surface in ("kchedy", "kcheedy", "qokchedy", "qokcheedy")
} | {
    ("TCH_E_LENGTH", surface) for surface in ("tchedy", "tcheedy", "qotchedy", "qotcheedy")
}
OUTPUTS = (
    "PAGE_ALLOWLIST.tsv", "TARGET_DECISION_DECK.tsv", "FORM_FAMILY_ATLAS.tsv",
    "COMPONENT_BINDING_AUDIT.tsv", "READER_VARIANT_AUDIT.tsv",
    "ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv", "SEQUENTIAL_DECISION_LEDGER.tsv",
    "ROUND_COVERAGE_COUNTS.tsv", "ACCEPTED_WHOLE_SURFACE_DEFAULTS.tsv",
    "NEWLY_COMPLETED_LINES.tsv", "NEWLY_EXPOSED_ONE_HOLE_LINES.tsv",
    "V20_EXACT_TOKEN_GLOSSARY.tsv", "ALL_LINE_CONCRETE_COVERAGE_V20.tsv",
    "COMPLETE_PASSAGES_V20.tsv", "ONE_UNKNOWN_PASSAGES_V20.tsv",
    "WORKING_DICTIONARY_V20.tsv", "RESULT.json",
)
EXPECTED_INPUTS = {
    *(f"experiments/yolo/gdt{number}_{slug}/src/run.py" for number, slug in (
        (631, "prefixed_cth_quality_parts"), (632, "cth_interfix_lattice"),
        (633, "cth_interfix_semantic_contrasts"), (634, "known_core_terminal_semantics"),
        (635, "initial_head_same_remainder_swaps"), (636, "residual_four_head_semantics"),
        (637, "ladder_completion_one_unknown_passages"), (638, "sequential_compound_promotion"),
        (639, "strict_hole_component_repair"), (640, "downstream_component_prediction"),
        (641, "strict_tch_bound_form_completion"),
    )),
    "experiments/yolo/gdt642_exact_e_ol_or_carrier_completion/src/run.py",
    "experiments/yolo/gdt642_exact_e_ol_or_carrier_completion/artifacts/PAGE_ALLOWLIST.tsv",
    "experiments/yolo/gdt642_exact_e_ol_or_carrier_completion/artifacts/ALL_LINE_CONCRETE_COVERAGE_V19.tsv",
    "experiments/yolo/gdt642_exact_e_ol_or_carrier_completion/artifacts/COMPLETE_PASSAGES_V19.tsv",
    "experiments/yolo/gdt642_exact_e_ol_or_carrier_completion/artifacts/ONE_UNKNOWN_PASSAGES_V19.tsv",
    "experiments/yolo/gdt642_exact_e_ol_or_carrier_completion/artifacts/NEWLY_EXPOSED_ONE_HOLE_LINES.tsv",
    "experiments/yolo/gdt642_exact_e_ol_or_carrier_completion/artifacts/V19_EXACT_TOKEN_GLOSSARY.tsv",
    "experiments/yolo/gdt642_exact_e_ol_or_carrier_completion/artifacts/WORKING_DICTIONARY_V19.tsv",
    "experiments/yolo/gdt642_exact_e_ol_or_carrier_completion/artifacts/RESULT.json",
    "experiments/yolo/gdt642_exact_e_ol_or_carrier_completion/REPORT.md",
    "experiments/yolo/gdt624_productive_quality_shell_grid/REPORT.md",
    "experiments/yolo/gdt624_productive_quality_shell_grid/artifacts/GRID_CELLS.tsv",
    "experiments/yolo/gdt627_value_head_role_atlas/REPORT.md",
    "experiments/yolo/gdt628_chol_measure_frame/REPORT.md",
    "experiments/yolo/gdt633_cth_interfix_semantic_contrasts/REPORT.md",
    "experiments/yolo/gdt636_residual_four_head_semantics/REPORT.md",
    "experiments/yolo/gdt636_residual_four_head_semantics/artifacts/WORKING_DICTIONARY_V13.tsv",
    "experiments/yolo/gdt639_strict_hole_component_repair/REPORT.md",
    "transcription/voynich_zl3b_tokens.tsv", "transcription/voynich_cross_transcription_lines.tsv",
}
GENERIC_FILLER = re.compile(
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
    spec = importlib.util.spec_from_file_location("gdt643_builder_validation", RUN)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load GDT643 builder")
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
        raise RuntimeError("excluded or forbidden page materialized")
    return rows


def concatenated_span_count(tokens: list[str], target: str) -> int:
    count = 0
    for start in range(len(tokens)):
        joined = ""
        for token in tokens[start:]:
            joined += token
            if joined == target:
                count += 1
                break
            if len(joined) >= len(target) or not target.startswith(joined):
                break
    return count


def independent_counts(
    token_rows: list[dict[str, str]], cross_rows: list[dict[str, str]], surfaces: set[str],
) -> tuple[Counter[str], Counter[str], Counter[str], Counter[str]]:
    cross = {row["locus"]: row for row in cross_rows}
    occurrence: Counter[str] = Counter()
    exact: Counter[str] = Counter()
    split: Counter[str] = Counter()
    pages: dict[str, set[str]] = {surface: set() for surface in surfaces}
    ordinal: Counter[tuple[str, str]] = Counter()
    for row in sorted(token_rows, key=lambda item: (item["page"], item["locus"], int(item["token_index"]))):
        surface = row["eva"]
        if surface not in surfaces:
            continue
        occurrence[surface] += 1
        pages[surface].add(row["page"])
        ordinal[row["locus"], surface] += 1
        required = ordinal[row["locus"], surface]
        direct = [cross[row["locus"]][field].split().count(surface) for field in ("zl3b_clean", "it2a_clean", "rf1b_clean")]
        normalized = [
            concatenated_span_count(cross[row["locus"]][field].split(), surface)
            for field in ("zl3b_clean", "it2a_clean", "rf1b_clean")
        ]
        if required <= min(direct):
            exact[surface] += 1
        if required <= min(normalized):
            split[surface] += 1
    return occurrence, exact, split, Counter({surface: len(values) for surface, values in pages.items()})


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
        with tempfile.TemporaryDirectory(prefix="gdt643_validate_") as tmp:
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
    check(manifest.get("experiment_id") == "GDT643", "manifest experiment id")
    check(manifest.get("sealed_data") == {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"}, "manifest sealed pages")
    check(manifest.get("validation", {}).get("status") == "PASS", "manifest validation status")
    check(result.get("schema") == "GDT643_EXPOSED_FIVE_HOLE_COMPLETION_RESULT_V1", "result schema")
    check(result.get("content_sha256") == canonical_hash({k: v for k, v in result.items() if k != "content_sha256"}), "result content hash")
    check(result.get("status") == "PASS_5_EXPOSED_HOLES__5_NEW_COMPLETE_LINES__68_POSITIONS", "result status")

    pages = {row["page"] for row in read_tsv(ART / "PAGE_ALLOWLIST.tsv")}
    check(len(pages) == 179 and "f1r" not in pages and not any(page.startswith("f84") for page in pages), "179-page guarded allowlist")
    check((ART / "PAGE_ALLOWLIST.tsv").read_bytes() == (ROOT / G642_ALLOW).read_bytes(), "allowlist byte-equal GDT642")
    token_rows = guarded_query(TOKENS, pages, "page,locus,token_index,eva")
    cross_rows = guarded_query(CROSS, pages, "page,locus,zl3b_clean,it2a_clean,rf1b_clean")
    family_rows = read_tsv(ART / "FORM_FAMILY_ATLAS.tsv")
    surfaces = {row["surface"] for row in family_rows} | set(EXPECTED)
    independent_occ, independent_exact, independent_split, independent_pages = independent_counts(token_rows, cross_rows, surfaces)

    deck = read_tsv(ART / "TARGET_DECISION_DECK.tsv")
    check(len(deck) == 5 and [row["surface"] for row in deck] == list(EXPECTED), "five ordered target cards")
    for row in deck:
        surface, expected = row["surface"], EXPECTED[row["surface"]]
        check(row["working_meaning_de"] == expected["meaning"], f"meaning:{surface}")
        check(row["composition"] == expected["composition"], f"composition:{surface}")
        check(row["reader_gate"] == expected["gate"], f"reader gate:{surface}")
        check(row["decision"] == "ACCEPT" and row["scope"] == expected["scope"], f"scope:{surface}")
        check(int(row["occurrences"]) == expected["occurrences"] == independent_occ[surface], f"occurrences:{surface}")
        check(int(row["pages"]) == expected["pages"] == independent_pages[surface], f"pages:{surface}")
        check(int(row["reader_exact_occurrences"]) == expected["exact"] == independent_exact[surface], f"reader exact:{surface}")
        check(int(row["split_normalized_occurrences"]) == expected["split"] == independent_split[surface], f"split normalized:{surface}")
        check(not GENERIC_FILLER.search(row["working_meaning_de"]), f"no generic filler:{surface}")

    check({(row["family"], row["surface"]) for row in family_rows} == EXPECTED_FAMILY_PAIRS, "exact 31 family cells")
    for row in family_rows:
        surface = row["surface"]
        check(int(row["zl3b_occurrences"]) == independent_occ[surface], f"family occurrences:{surface}")
        check(int(row["pages"]) == independent_pages[surface], f"family pages:{surface}")
        check(int(row["reader_exact_occurrences"]) == independent_exact[surface], f"family exact:{surface}")
    tcheedy = next(row for row in family_rows if row["surface"] == "tcheedy")
    check(tcheedy["zl3b_occurrences"] == "0" and tcheedy["cross_reader_only"] == "1", "RF1b-only tcheedy cell")

    components = read_tsv(ART / "COMPONENT_BINDING_AUDIT.tsv")
    check(len(components) == 13 and all(row["licensed_use"].startswith("inside exact ") for row in components), "13 exact-bound component rows")
    variants = read_tsv(ART / "READER_VARIANT_AUDIT.tsv")
    check([row["surface"] for row in variants] == ["soysar", "kcheedy"], "two explicit reader rival cards")
    check(
        (variants[0]["locus"], variants[0]["zl3b_line"], variants[0]["it2a_line"], variants[0]["rf1b_line"])
        == ("f96v.13", "soysar cheor", "soy sar cheor", "soysar cheor"),
        "IT2a exposes exact soy|sar boundary",
    )
    check(
        (variants[1]["locus"], variants[1]["zl3b_line"], variants[1]["it2a_line"], variants[1]["rf1b_line"])
        == ("f107r.20", "tcheol kcheedy", "tcheol kcheedy", "tcheol tcheedy"),
        "RF1b exposes exact k/t thermal rival",
    )

    audits = read_tsv(ART / "ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv")
    check(len(audits) == 68 and len({row["audit_id"] for row in audits}) == 68, "68 unique occurrence audits")
    check(Counter(row["surface"] for row in audits) == Counter({surface: value["occurrences"] for surface, value in EXPECTED.items()}), "audit target census")
    check(sum(int(row["reader_exact"]) for row in audits) == 50, "50 reader-exact occurrences")
    check(sum(int(row["split_normalized"]) for row in audits) == 51, "51 split-normalized occurrences")
    check(sum(int(row["thermal_reader_rival"]) for row in audits) == 1, "one thermal reader rival")
    check(Counter(row["verdict"] for row in audits) == Counter({
        "CLEAN_CONTEXT_COMPATIBLE": 23, "OPAQUE_OR_UNSTABLE_CONTEXT": 27,
        "READER_VARIANT_WARNING": 17, "READER_SPLIT_NORMALIZED": 1,
    }), "audit verdict census")
    check(all(row["hard_collision"] == "0" for row in audits), "zero manually recorded hard collisions")
    for surface, expected in EXPECTED.items():
        surface_rows = [row for row in audits if row["surface"] == surface]
        check(sum(int(row["reader_exact"]) for row in surface_rows) == expected["exact"], f"audit reader exact:{surface}")
        check(sum(int(row["split_normalized"]) for row in surface_rows) == expected["split"], f"audit split normalized:{surface}")
    check(all(int(row["reader_exact"]) <= int(row["split_normalized"]) for row in audits), "reader exact implies split normalized")
    for row in audits:
        reader_exact, split_normalized = int(row["reader_exact"]), int(row["split_normalized"])
        clean_known, known = int(row["clean_known_other_tokens"]), int(row["known_other_tokens"])
        if reader_exact:
            expected_support = "ALL_THREE_EXACT"
        elif split_normalized:
            expected_support = "ALL_THREE_SPLIT_NORMALIZED"
        elif row["surface"] == "kcheedy" and row["locus"] == "f107r.20":
            expected_support = "TWO_READER_EXACT_THERMAL_RIVAL"
        else:
            expected_support = "READER_VARIANT"
        if expected_support == "ALL_THREE_EXACT" and clean_known >= 2:
            expected_verdict = "CLEAN_CONTEXT_COMPATIBLE"
        elif expected_support == "ALL_THREE_EXACT":
            expected_verdict = "OPAQUE_OR_UNSTABLE_CONTEXT"
        elif expected_support == "ALL_THREE_SPLIT_NORMALIZED":
            expected_verdict = "READER_SPLIT_NORMALIZED"
        else:
            expected_verdict = "READER_VARIANT_WARNING"
        check(0 <= clean_known <= known, f"clean companion bounds:{row['audit_id']}")
        check(row["reader_support"] == expected_support, f"rowwise reader support:{row['audit_id']}")
        check(row["verdict"] == expected_verdict, f"rowwise verdict:{row['audit_id']}")
        check(row["before_gloss"] == f"[{row['surface']}:?]", f"target unknown before:{row['audit_id']}")
        check(row["after_gloss"] == EXPECTED[row["surface"]]["meaning"], f"target concrete after:{row['audit_id']}")

    ledger = read_tsv(ART / "SEQUENTIAL_DECISION_LEDGER.tsv")
    check(len(ledger) == 5 and [row["surface"] for row in ledger] == list(EXPECTED), "five sequential decisions")
    check(all(row["decision"] == "ACCEPT" and row["hard_collisions"] == "0" for row in ledger), "five accepts without collision")
    check(sum(int(row["clean_context_compatible"]) for row in ledger) == 23, "ledger clean-context total")
    check(sum(int(row["opaque_or_unstable_context"]) for row in ledger) == 27, "ledger opaque/unstable total")

    rounds = read_tsv(ART / "ROUND_COVERAGE_COUNTS.tsv")
    check(len(rounds) == 6, "six cumulative coverage states")
    for row, expected in zip(rounds, EXPECTED_ROUNDS):
        observed = (
            row["surface"], int(row["dictionary_entries"]), int(row["known_token_positions"]),
            int(row["unknown_token_positions"]), int(row["complete_multi_token_lines"]),
            int(row["strict_complete_lines"]), int(row["one_unknown_lines"]),
            int(row["strict_one_unknown_lines"]), int(row["exact_glossary_surfaces"]),
        )
        check(observed == expected, f"coverage round:{row['surface']}", repr(observed))

    new_complete = read_tsv(ART / "NEWLY_COMPLETED_LINES.tsv")
    complete_by_locus = {row["locus"]: row for row in read_tsv(ART / "COMPLETE_PASSAGES_V20.tsv")}
    check(len(new_complete) == 5 and {row["locus"] for row in new_complete} == set(EXPECTED_COMPLETE), "five newly complete lines")
    for row in new_complete:
        surface, strict = EXPECTED_COMPLETE[row["locus"]]
        check((row["surface"], row["strict_complete"]) == (surface, strict), f"new completion:{row['locus']}")
        check(row["locus"] in complete_by_locus and complete_by_locus[row["locus"]]["strict_complete"] == strict, f"completion in V20:{row['locus']}")
        check(EXPECTED[surface]["meaning"] in row["literal_v20_de"], f"completion contains target:{row['locus']}")
        check(not GENERIC_FILLER.search(row["smoothed_working_reading_de"]), f"completion no filler:{row['locus']}")
    new_one = read_tsv(ART / "NEWLY_EXPOSED_ONE_HOLE_LINES.tsv")
    final_one_by_locus = {row["locus"]: row for row in read_tsv(ART / "ONE_UNKNOWN_PASSAGES_V20.tsv")}
    check(len(new_one) == 5 and {row["locus"] for row in new_one} == set(EXPECTED_NEW_ONE), "five newly exposed one-hole lines")
    for row in new_one:
        enabled, unknown, strict = EXPECTED_NEW_ONE[row["locus"]]
        check((row["enabled_by_surface"], row["unknown_surface"], row["strict_eligible"]) == (enabled, unknown, strict), f"new one-hole:{row['locus']}")
        check(
            row["locus"] in final_one_by_locus
            and final_one_by_locus[row["locus"]]["unknown_surface"] == unknown
            and final_one_by_locus[row["locus"]]["strict_eligible"] == strict,
            f"new one-hole in V20:{row['locus']}",
        )

    v19_gloss = {row["surface"]: row for row in read_tsv(ROOT / G642_GLOSSARY)}
    v20_gloss = {row["surface"]: row for row in read_tsv(ART / "V20_EXACT_TOKEN_GLOSSARY.tsv")}
    check(len(v19_gloss) == 241 and len(v20_gloss) == 246, "glossary 241 to 246")
    check(all(v20_gloss[surface] == row for surface, row in v19_gloss.items()), "V19 glossary preserved")
    for surface, expected in EXPECTED.items():
        check(v20_gloss[surface]["working_meaning_de"] == expected["meaning"], f"V20 glossary target:{surface}")
        check(v20_gloss[surface]["scope_state"] == "KNOWN_EXACT_WHOLE", f"V20 exact-whole scope:{surface}")

    v19_dictionary = read_tsv(ROOT / G642_DICTIONARY)
    v20_dictionary = read_tsv(ART / "WORKING_DICTIONARY_V20.tsv")
    check(len(v19_dictionary) == 288 and len(v20_dictionary) == 293, "dictionary 288 to 293")
    check(v20_dictionary[:288] == v19_dictionary, "V19 dictionary prefix preserved")
    check([row["entry"].split("@", 1)[0] for row in v20_dictionary[288:]] == list(EXPECTED), "five exact dictionary tail rows")

    coverage = read_tsv(ART / "ALL_LINE_CONCRETE_COVERAGE_V20.tsv")
    complete = read_tsv(ART / "COMPLETE_PASSAGES_V20.tsv")
    one = read_tsv(ART / "ONE_UNKNOWN_PASSAGES_V20.tsv")
    check(len(coverage) == 4128 and sum(int(row["known_tokens"]) for row in coverage) == 10035, "V20 known coverage")
    check(sum(int(row["unknown_tokens"]) for row in coverage) == 22304, "V20 unknown coverage")
    check(len(complete) == 49 and sum(int(row["strict_complete"]) for row in complete) == 35, "V20 complete lines")
    check(len(one) == 65 and sum(int(row["strict_eligible"]) for row in one) == 20, "V20 one-hole frontier")
    check(all(row["page"] != "f1r" and not row["page"].startswith("f84") for row in coverage), "coverage excludes f1r/f84")

    for path in ART.glob("*.tsv"):
        raw = path.read_bytes()
        lines = raw.splitlines(keepends=True)
        rows = read_tsv(path)
        check(
            b"\t\t" not in raw and not any(line.startswith(b"\t") or line.endswith(b"\t\n") or line.endswith(b"\t\r\n") for line in lines)
            and all(None not in row and all(value not in (None, "") for value in row.values()) for row in rows),
            f"no empty TSV cell:{path.name}",
        )
    check(set(result.get("inputs", {})) == EXPECTED_INPUTS, "exact result input set")
    check(set(result.get("outputs", {})) == {str(BASE / "artifacts" / name) for name in OUTPUTS[:-1]}, "exact result output set")
    for relative, digest in result.get("inputs", {}).items():
        check((ROOT / relative).is_file() and sha256(ROOT / relative) == digest, f"input hash:{relative}")
    for relative, digest in result.get("outputs", {}).items():
        check((ROOT / relative).is_file() and sha256(ROOT / relative) == digest, f"output hash:{relative}")
    check(result.get("target_run") == {
        "candidates": 5, "accepted": 5, "held": 0, "audited_occurrences": 68,
        "all_reader_exact_occurrences": 50, "split_normalized_occurrences": 51,
        "thermal_reader_rivals": 1, "hard_collisions": 0,
        "verdicts": {
            "CLEAN_CONTEXT_COMPATIBLE": 23, "OPAQUE_OR_UNSTABLE_CONTEXT": 27,
            "READER_SPLIT_NORMALIZED": 1, "READER_VARIANT_WARNING": 17,
        },
        "accepted_surfaces": list(EXPECTED),
    }, "exact result target run")
    check(result.get("coverage") == {
        "base_complete_multi_token_lines": 44, "base_strict_complete_lines": 33,
        "newly_completed_lines": 5, "newly_exposed_one_hole_lines": 5,
        "physical_lines": 4128, "known_token_positions": 10035,
        "unknown_token_positions": 22304, "complete_multi_token_lines": 49,
        "strict_complete_lines": 35, "one_unknown_lines": 65,
        "strict_one_unknown_lines": 20, "exact_glossary_surfaces": 246,
    }, "exact result coverage")
    check(result.get("working_dictionary", {}).get("v20_entries") == 293, "result V20 dictionary count")

    validation_core = {
        "schema": "GDT643_VALIDATION_V1", "experiment_id": "GDT643",
        "status": "PASS" if not issues else "FAIL", "passed_checks": len(passed),
        "issue_count": len(issues), "issues": issues,
        "summary": {
            "target_occurrences": len(audits), "reader_exact": sum(int(row["reader_exact"]) for row in audits),
            "clean_context_compatible": sum(row["verdict"] == "CLEAN_CONTEXT_COMPATIBLE" for row in audits),
            "new_complete_lines": len(new_complete), "new_one_hole_lines": len(new_one),
            "v20_dictionary_entries": len(v20_dictionary),
        },
    }
    validation = {**validation_core, "content_sha256": canonical_hash(validation_core)}
    VALIDATION.write_text(json.dumps(validation, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"GDT643 validation: {validation['status']} checks={len(passed)} issues={len(issues)}")
    for issue in issues:
        print(f"ISSUE {issue}")
    return 0 if not issues else 1


if __name__ == "__main__":
    raise SystemExit(main())
