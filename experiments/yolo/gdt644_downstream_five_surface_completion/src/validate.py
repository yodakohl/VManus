#!/usr/bin/env python3
"""Independent release validator for GDT644."""
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
BASE = Path("experiments/yolo/gdt644_downstream_five_surface_completion")
ART = ROOT / BASE / "artifacts"
RUN = ROOT / BASE / "src/run.py"
MANIFEST = ROOT / BASE / "experiment.json"
VALIDATION = ART / "VALIDATION.json"
G643_BASE = Path("experiments/yolo/gdt643_exposed_five_hole_completion")
G643_ALLOW = G643_BASE / "artifacts/PAGE_ALLOWLIST.tsv"
G643_GLOSSARY = G643_BASE / "artifacts/V20_EXACT_TOKEN_GLOSSARY.tsv"
G643_DICTIONARY = G643_BASE / "artifacts/WORKING_DICTIONARY_V20.tsv"
TOKENS = Path("transcription/voynich_zl3b_tokens.tsv")
CROSS = Path("transcription/voynich_cross_transcription_lines.tsv")

EXPECTED = {
    "otal": {
        "meaning": "Ansatz aus kaltem Rohstoff, Form I", "composition": "o+t+al",
        "source_locus": "f44v.11",
        "occurrences": 119, "pages": 57, "exact": 109, "split": 109,
        "gate": "AT_LEAST_ONE_ALL_READER_EXACT", "scope": "exact complete ZL3b surface only",
    },
    "cthol": {
        "meaning": "CTH-Drogenstoff; im Kräuterbuch Blatt- oder Krautdroge", "composition": "cth+ol",
        "source_locus": "f49v.22",
        "occurrences": 51, "pages": 34, "exact": 50, "split": 50,
        "gate": "AT_LEAST_ONE_ALL_READER_EXACT", "scope": "exact complete ZL3b surface only",
    },
    "chokchy": {
        "meaning": "Trockenansatz: heiß-trockene Grundform", "composition": "cho+(k+ch+y)",
        "source_locus": "f49v.12",
        "occurrences": 15, "pages": 13, "exact": 13, "split": 13,
        "gate": "AT_LEAST_ONE_ALL_READER_EXACT", "scope": "exact complete ZL3b surface only",
    },
    "qotchod": {
        "meaning": "kalt-trockene Zubereitung, fertig gebunden", "composition": "qo+tch+o+d",
        "source_locus": "f15v.4",
        "occurrences": 2, "pages": 2, "exact": 2, "split": 2,
        "gate": "AT_LEAST_ONE_ALL_READER_EXACT", "scope": "exact complete ZL3b surface only",
    },
    "ytchor": {
        "meaning": "kalt-trockene Portion dieser Droge", "composition": "y+(tch+or)",
        "source_locus": "f15v.8",
        "occurrences": 8, "pages": 7, "exact": 8, "split": 8,
        "gate": "AT_LEAST_ONE_ALL_READER_EXACT",
        "scope": "exact complete ZL3b surface only; initial y remains bound",
    },
}
EXPECTED_ROUNDS = (
    ("BASE_V20", 293, 10035, 22304, 49, 35, 65, 20, 246),
    ("otal", 294, 10154, 22185, 50, 35, 66, 21, 247),
    ("cthol", 295, 10205, 22134, 51, 36, 73, 26, 248),
    ("chokchy", 296, 10220, 22119, 52, 37, 75, 25, 249),
    ("qotchod", 297, 10222, 22117, 53, 38, 74, 24, 250),
    ("ytchor", 298, 10230, 22109, 54, 38, 75, 26, 251),
)
EXPECTED_COMPLETE = {
    "f44v.11": ("otal", "0"), "f49v.22": ("cthol", "1"),
    "f49v.12": ("chokchy", "1"), "f15v.4": ("qotchod", "1"),
    "f15v.8": ("ytchor", "0"),
}
EXPECTED_NEW_ONE = {
    "f75v.50": ("otal", "opal", "1"), "f83v.30": ("otal", "qotals", "0"),
    "f18r.12": ("cthol", "ychair", "1"), "f19v.14": ("cthol", "cheaiin", "0"),
    "f28v.8": ("cthol", "yk", "1"), "f35r.14": ("cthol", "otchor", "1"),
    "f36v.13": ("cthol", "oky", "1"), "f4r.7": ("cthol", "cthom", "1"),
    "f54v.12": ("cthol", "s", "1"), "f93r.31": ("cthol", "olchod", "0"),
    "f42r.17": ("chokchy", "shotol", "0"), "f49v.40": ("chokchy", "kshardy", "0"),
    "f8v.9": ("chokchy", "orchl", "0"), "f36r.8": ("ytchor", "yd", "1"),
    "f37v.6": ("ytchor", "yokor", "1"),
}
EXPECTED_FAMILY_PAIRS = {
    ("OTAL_GRID", surface) for surface in ("okal", "otal", "okar", "otar", "qokal", "qotal", "qokar", "qotar")
} | {
    ("CTH_CARRIER", surface) for surface in ("cthal", "cthar", "cthol", "cthor", "ctheol", "ctheor")
} | {
    ("NESTED_CHO_SHO", surface) for surface in ("chokchy", "chotchy", "shokchy", "shotchy")
} | {
    ("CHOD_CLOSURE", surface) for surface in (
        "kcho", "kchod", "kchody", "tcho", "tchod", "tchody",
        "okcho", "okchod", "okchody", "otcho", "otchod", "otchody",
        "qokcho", "qokchod", "qokchody", "qotcho", "qotchod", "qotchody",
    )
} | {
    ("Y_QUALITY_CARRIER", surface) for surface in ("ykol", "ykor", "ytol", "ytor", "ykchol", "ykchor", "ytchol", "ytchor")
}
OUTPUTS = (
    "PAGE_ALLOWLIST.tsv", "TARGET_DECISION_DECK.tsv", "FORM_FAMILY_ATLAS.tsv",
    "COMPONENT_BINDING_AUDIT.tsv", "READER_VARIANT_AUDIT.tsv",
    "ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv", "SEQUENTIAL_DECISION_LEDGER.tsv",
    "ROUND_COVERAGE_COUNTS.tsv", "ACCEPTED_WHOLE_SURFACE_DEFAULTS.tsv",
    "NEWLY_COMPLETED_LINES.tsv", "NEWLY_EXPOSED_ONE_HOLE_LINES.tsv",
    "V21_EXACT_TOKEN_GLOSSARY.tsv", "ALL_LINE_CONCRETE_COVERAGE_V21.tsv",
    "COMPLETE_PASSAGES_V21.tsv", "ONE_UNKNOWN_PASSAGES_V21.tsv",
    "WORKING_DICTIONARY_V21.tsv", "RESULT.json",
)
EXPECTED_INPUTS = {
    *(f"experiments/yolo/gdt{number}_{slug}/src/run.py" for number, slug in (
        (631, "prefixed_cth_quality_parts"), (632, "cth_interfix_lattice"),
        (633, "cth_interfix_semantic_contrasts"), (634, "known_core_terminal_semantics"),
        (635, "initial_head_same_remainder_swaps"), (636, "residual_four_head_semantics"),
        (637, "ladder_completion_one_unknown_passages"), (638, "sequential_compound_promotion"),
        (639, "strict_hole_component_repair"), (640, "downstream_component_prediction"),
        (641, "strict_tch_bound_form_completion"),
        (642, "exact_e_ol_or_carrier_completion"),
    )),
    "experiments/yolo/gdt643_exposed_five_hole_completion/src/run.py",
    "experiments/yolo/gdt643_exposed_five_hole_completion/artifacts/PAGE_ALLOWLIST.tsv",
    "experiments/yolo/gdt643_exposed_five_hole_completion/artifacts/ALL_LINE_CONCRETE_COVERAGE_V20.tsv",
    "experiments/yolo/gdt643_exposed_five_hole_completion/artifacts/COMPLETE_PASSAGES_V20.tsv",
    "experiments/yolo/gdt643_exposed_five_hole_completion/artifacts/ONE_UNKNOWN_PASSAGES_V20.tsv",
    "experiments/yolo/gdt643_exposed_five_hole_completion/artifacts/NEWLY_EXPOSED_ONE_HOLE_LINES.tsv",
    "experiments/yolo/gdt643_exposed_five_hole_completion/artifacts/V20_EXACT_TOKEN_GLOSSARY.tsv",
    "experiments/yolo/gdt643_exposed_five_hole_completion/artifacts/WORKING_DICTIONARY_V20.tsv",
    "experiments/yolo/gdt643_exposed_five_hole_completion/artifacts/RESULT.json",
    "experiments/yolo/gdt643_exposed_five_hole_completion/REPORT.md",
    "experiments/yolo/gdt624_productive_quality_shell_grid/REPORT.md",
    "experiments/yolo/gdt624_productive_quality_shell_grid/artifacts/GRID_CELLS.tsv",
    "experiments/yolo/gdt628_chol_measure_frame/REPORT.md",
    "experiments/yolo/gdt631_prefixed_cth_quality_parts/REPORT.md",
    "experiments/yolo/gdt633_cth_interfix_semantic_contrasts/REPORT.md",
    "experiments/yolo/gdt639_strict_hole_component_repair/REPORT.md",
    "experiments/yolo/gdt640_downstream_component_prediction/REPORT.md",
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
    spec = importlib.util.spec_from_file_location("gdt644_builder_validation", RUN)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load GDT644 builder")
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
        with tempfile.TemporaryDirectory(prefix="gdt644_validate_") as tmp:
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
    check(manifest.get("experiment_id") == "GDT644", "manifest experiment id")
    check(manifest.get("sealed_data") == {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"}, "manifest sealed pages")
    check(manifest.get("validation", {}).get("status") == "PASS", "manifest validation status")
    check(
        manifest.get("validation", {}).get("artifact") == str(BASE / "artifacts/VALIDATION.json"),
        "manifest validation artifact",
    )
    check(result.get("schema") == "GDT644_DOWNSTREAM_FIVE_SURFACE_COMPLETION_RESULT_V1", "result schema")
    check(result.get("content_sha256") == canonical_hash({k: v for k, v in result.items() if k != "content_sha256"}), "result content hash")
    check(result.get("status") == "PASS_5_DOWNSTREAM_SURFACES__195_POSITIONS__5_NEW_COMPLETE_LINES", "result status")

    pages = {row["page"] for row in read_tsv(ART / "PAGE_ALLOWLIST.tsv")}
    check(len(pages) == 179 and "f1r" not in pages and not any(page.startswith("f84") for page in pages), "179-page guarded allowlist")
    check((ART / "PAGE_ALLOWLIST.tsv").read_bytes() == (ROOT / G643_ALLOW).read_bytes(), "allowlist byte-equal GDT643")
    token_rows = guarded_query(TOKENS, pages, "page,locus,token_index,eva")
    cross_rows = guarded_query(CROSS, pages, "page,locus,zl3b_clean,it2a_clean,rf1b_clean")
    family_rows = read_tsv(ART / "FORM_FAMILY_ATLAS.tsv")
    surfaces = {row["surface"] for row in family_rows} | set(EXPECTED)
    independent_occ, independent_exact, independent_split, independent_pages = independent_counts(token_rows, cross_rows, surfaces)

    deck = read_tsv(ART / "TARGET_DECISION_DECK.tsv")
    check(len(deck) == 5 and [row["surface"] for row in deck] == list(EXPECTED), "five ordered target cards")
    for order, row in enumerate(deck, 1):
        surface, expected = row["surface"], EXPECTED[row["surface"]]
        check(
            (row["candidate_id"], int(row["candidate_order"]), row["source_locus"])
            == (f"G644-C{order:02d}", order, expected["source_locus"]),
            f"candidate identity:{surface}",
        )
        check(row["working_meaning_de"] == expected["meaning"], f"meaning:{surface}")
        check(row["composition"] == expected["composition"], f"composition:{surface}")
        check(row["reader_gate"] == expected["gate"], f"reader gate:{surface}")
        check(row["decision"] == "ACCEPT" and row["scope"] == expected["scope"], f"scope:{surface}")
        check(int(row["occurrences"]) == expected["occurrences"] == independent_occ[surface], f"occurrences:{surface}")
        check(int(row["pages"]) == expected["pages"] == independent_pages[surface], f"pages:{surface}")
        check(int(row["reader_exact_occurrences"]) == expected["exact"] == independent_exact[surface], f"reader exact:{surface}")
        check(int(row["split_normalized_occurrences"]) == expected["split"] == independent_split[surface], f"split normalized:{surface}")
        check(not GENERIC_FILLER.search(row["working_meaning_de"]), f"no generic filler:{surface}")

    check(
        len(family_rows) == 44
        and len({(row["family"], row["surface"]) for row in family_rows}) == 44
        and {(row["family"], row["surface"]) for row in family_rows} == EXPECTED_FAMILY_PAIRS,
        "exact 44 unique family cells",
    )
    for row in family_rows:
        surface = row["surface"]
        check(int(row["zl3b_occurrences"]) == independent_occ[surface], f"family occurrences:{surface}")
        check(int(row["pages"]) == independent_pages[surface], f"family pages:{surface}")
        check(int(row["reader_exact_occurrences"]) == independent_exact[surface], f"family exact:{surface}")
    check(all(row["cross_reader_only"] == "0" for row in family_rows), "no reader-only family cells")

    components = read_tsv(ART / "COMPONENT_BINDING_AUDIT.tsv")
    check(
        len(components) == 15
        and [row["component_id"] for row in components] == [f"G644-B{index:02d}" for index in range(1, 16)]
        and len({(row["surface"], row["segment"]) for row in components}) == 15
        and all(row["licensed_use"] == f"inside exact {row['surface']} only" for row in components),
        "15 uniquely identified exact-bound component rows",
    )
    for row in components:
        check(row["surface"] in EXPECTED, f"component target:{row['component_id']}")
        check(row["evidence_path"] in EXPECTED_INPUTS, f"component evidence registered:{row['component_id']}")
        check((ROOT / row["evidence_path"]).is_file(), f"component evidence exists:{row['component_id']}")
    variants = read_tsv(ART / "READER_VARIANT_AUDIT.tsv")
    cross_by_locus = {row["locus"]: row for row in cross_rows}
    check(len(variants) == 13 and len({(row["surface"], row["locus"]) for row in variants}) == 13, "13 unique reader-warning cards")
    for row in variants:
        cross = cross_by_locus[row["locus"]]
        check(
            (row["zl3b_line"], row["it2a_line"], row["rf1b_line"])
            == (cross["zl3b_clean"], cross["it2a_clean"], cross["rf1b_clean"]),
            f"reader warning source:{row['surface']}:{row['locus']}",
        )

    audits = read_tsv(ART / "ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv")
    check(len(audits) == 195 and len({row["audit_id"] for row in audits}) == 195, "195 unique occurrence audits")
    independent_target_keys: set[tuple[str, str, int]] = set()
    token_rows_by_locus: dict[str, list[dict[str, str]]] = {}
    for row in token_rows:
        token_rows_by_locus.setdefault(row["locus"], []).append(row)
    for locus, rows in token_rows_by_locus.items():
        for ordinal, row in enumerate(sorted(rows, key=lambda item: int(item["token_index"])), 1):
            if row["eva"] in EXPECTED:
                independent_target_keys.add((row["eva"], locus, ordinal))
    check(
        {(row["surface"], row["locus"], int(row["token_ordinal"])) for row in audits}
        == independent_target_keys
        and len(independent_target_keys) == 195,
        "audit keys equal independent target-token census",
    )
    check(Counter(row["surface"] for row in audits) == Counter({surface: value["occurrences"] for surface, value in EXPECTED.items()}), "audit target census")
    check(sum(int(row["reader_exact"]) for row in audits) == 182, "182 reader-exact occurrences")
    check(sum(int(row["split_normalized"]) for row in audits) == 182, "182 split-normalized occurrences")
    check(sum(int(row["thermal_reader_rival"]) for row in audits) == 0, "zero thermal reader rivals")
    check(
        {(row["surface"], row["locus"]) for row in variants}
        == {(row["surface"], row["locus"]) for row in audits if row["reader_exact"] == "0"},
        "reader-warning deck equals every non-exact target occurrence",
    )
    check(Counter(row["verdict"] for row in audits) == Counter({
        "CLEAN_CONTEXT_COMPATIBLE": 117, "OPAQUE_OR_UNSTABLE_CONTEXT": 65,
        "READER_VARIANT_WARNING": 13,
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
    check([int(row["round"]) for row in ledger] == list(range(1, 6)), "ledger round order")
    check(all(row["decision"] == "ACCEPT" and row["hard_collisions"] == "0" for row in ledger), "five accepts without collision")
    check(sum(int(row["clean_context_compatible"]) for row in ledger) == 117, "ledger clean-context total")
    check(sum(int(row["opaque_or_unstable_context"]) for row in ledger) == 65, "ledger opaque/unstable total")

    rounds = read_tsv(ART / "ROUND_COVERAGE_COUNTS.tsv")
    check(len(rounds) == 6, "six cumulative coverage states")
    check([int(row["round"]) for row in rounds] == list(range(6)), "coverage round order")
    check([row["decision"] for row in rounds] == ["BASE", "ACCEPT", "ACCEPT", "ACCEPT", "ACCEPT", "ACCEPT"], "coverage round decisions")
    for row, expected in zip(rounds, EXPECTED_ROUNDS):
        observed = (
            row["surface"], int(row["dictionary_entries"]), int(row["known_token_positions"]),
            int(row["unknown_token_positions"]), int(row["complete_multi_token_lines"]),
            int(row["strict_complete_lines"]), int(row["one_unknown_lines"]),
            int(row["strict_one_unknown_lines"]), int(row["exact_glossary_surfaces"]),
        )
        check(observed == expected, f"coverage round:{row['surface']}", repr(observed))

    new_complete = read_tsv(ART / "NEWLY_COMPLETED_LINES.tsv")
    complete_by_locus = {row["locus"]: row for row in read_tsv(ART / "COMPLETE_PASSAGES_V21.tsv")}
    check(len(new_complete) == 5 and {row["locus"] for row in new_complete} == set(EXPECTED_COMPLETE), "five newly complete lines")
    for row in new_complete:
        surface, strict = EXPECTED_COMPLETE[row["locus"]]
        check((row["surface"], row["strict_complete"]) == (surface, strict), f"new completion:{row['locus']}")
        check(row["locus"] in complete_by_locus and complete_by_locus[row["locus"]]["strict_complete"] == strict, f"completion in V21:{row['locus']}")
        check(EXPECTED[surface]["meaning"] in row["literal_v21_de"], f"completion contains target:{row['locus']}")
        check(not GENERIC_FILLER.search(row["smoothed_working_reading_de"]), f"completion no filler:{row['locus']}")
    new_one = read_tsv(ART / "NEWLY_EXPOSED_ONE_HOLE_LINES.tsv")
    final_one_by_locus = {row["locus"]: row for row in read_tsv(ART / "ONE_UNKNOWN_PASSAGES_V21.tsv")}
    check(len(new_one) == 15 and {row["locus"] for row in new_one} == set(EXPECTED_NEW_ONE), "15 newly exposed one-hole lines")
    for row in new_one:
        enabled, unknown, strict = EXPECTED_NEW_ONE[row["locus"]]
        check((row["enabled_by_surface"], row["unknown_surface"], row["strict_eligible"]) == (enabled, unknown, strict), f"new one-hole:{row['locus']}")
        check(
            row["locus"] in final_one_by_locus
            and final_one_by_locus[row["locus"]]["unknown_surface"] == unknown
            and final_one_by_locus[row["locus"]]["strict_eligible"] == strict,
            f"new one-hole in V21:{row['locus']}",
        )

    v20_gloss_rows = read_tsv(ROOT / G643_GLOSSARY)
    v21_gloss_rows = read_tsv(ART / "V21_EXACT_TOKEN_GLOSSARY.tsv")
    check(
        len(v20_gloss_rows) == len({row["surface"] for row in v20_gloss_rows}) == 246
        and len(v21_gloss_rows) == len({row["surface"] for row in v21_gloss_rows}) == 251,
        "unique glossary surfaces 246 to 251",
    )
    v20_gloss = {row["surface"]: row for row in v20_gloss_rows}
    v21_gloss = {row["surface"]: row for row in v21_gloss_rows}
    check(all(v21_gloss[surface] == row for surface, row in v20_gloss.items()), "V20 glossary preserved")
    for surface, expected in EXPECTED.items():
        check(v21_gloss[surface]["working_meaning_de"] == expected["meaning"], f"V21 glossary target:{surface}")
        check(v21_gloss[surface]["scope_state"] == "KNOWN_EXACT_WHOLE", f"V21 exact-whole scope:{surface}")

    v20_dictionary = read_tsv(ROOT / G643_DICTIONARY)
    v21_dictionary = read_tsv(ART / "WORKING_DICTIONARY_V21.tsv")
    check(len(v20_dictionary) == 293 and len(v21_dictionary) == 298, "dictionary 293 to 298")
    check(v21_dictionary[:293] == v20_dictionary, "V20 dictionary prefix preserved")
    check([row["entry"].split("@", 1)[0] for row in v21_dictionary[293:]] == list(EXPECTED), "five exact dictionary tail rows")

    accepted = read_tsv(ART / "ACCEPTED_WHOLE_SURFACE_DEFAULTS.tsv")
    check(len(accepted) == 5 and [row["surface"] for row in accepted] == list(EXPECTED), "five accepted defaults")
    for order, (row, dictionary_row) in enumerate(zip(accepted, v21_dictionary[293:]), 1):
        expected = EXPECTED[row["surface"]]
        check(
            (row["entry"], row["kind"], row["working_meaning_de"], row["composition"], row["status"])
            == (
                dictionary_row["entry"], dictionary_row["kind"], dictionary_row["working_meaning_de"],
                dictionary_row["composition"], dictionary_row["status"],
            ),
            f"accepted dictionary binding:{row['surface']}",
        )
        check(
            (int(row["accepted_round"]), row["source_locus"], int(row["occurrences"]))
            == (order, expected["source_locus"], expected["occurrences"]),
            f"accepted provenance:{row['surface']}",
        )

    for order, row in enumerate(ledger, 1):
        pre_rows, post_rows = v21_dictionary[: 293 + order - 1], v21_dictionary[: 293 + order]
        check(
            (int(row["pre_dictionary_entries"]), int(row["post_dictionary_entries"]))
            == (len(pre_rows), len(post_rows)),
            f"ledger dictionary sizes:{row['surface']}",
        )
        check(
            (row["pre_dictionary_sha256"], row["post_dictionary_sha256"])
            == (canonical_hash(pre_rows), canonical_hash(post_rows)),
            f"ledger dictionary hash chain:{row['surface']}",
        )
    for order, row in enumerate(rounds):
        prefix = v21_dictionary[: 293 + order]
        check(row["dictionary_sha256"] == canonical_hash(prefix), f"coverage dictionary hash:{row['surface']}")

    coverage = read_tsv(ART / "ALL_LINE_CONCRETE_COVERAGE_V21.tsv")
    complete = read_tsv(ART / "COMPLETE_PASSAGES_V21.tsv")
    one = read_tsv(ART / "ONE_UNKNOWN_PASSAGES_V21.tsv")
    check(len(coverage) == 4128 and sum(int(row["known_tokens"]) for row in coverage) == 10230, "V21 known coverage")
    check(sum(int(row["unknown_tokens"]) for row in coverage) == 22109, "V21 unknown coverage")
    check(len(complete) == 54 and sum(int(row["strict_complete"]) for row in complete) == 38, "V21 complete lines")
    check(len(one) == 75 and sum(int(row["strict_eligible"]) for row in one) == 26, "V21 one-hole frontier")
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
        "candidates": 5, "accepted": 5, "held": 0, "audited_occurrences": 195,
        "all_reader_exact_occurrences": 182, "split_normalized_occurrences": 182,
        "thermal_reader_rivals": 0, "hard_collisions": 0,
        "verdicts": {
            "CLEAN_CONTEXT_COMPATIBLE": 117, "OPAQUE_OR_UNSTABLE_CONTEXT": 65,
            "READER_VARIANT_WARNING": 13,
        },
        "accepted_surfaces": list(EXPECTED),
    }, "exact result target run")
    check(result.get("coverage") == {
        "base_complete_multi_token_lines": 49, "base_strict_complete_lines": 35,
        "newly_completed_lines": 5, "newly_exposed_one_hole_lines": 15,
        "physical_lines": 4128, "known_token_positions": 10230,
        "unknown_token_positions": 22109, "complete_multi_token_lines": 54,
        "strict_complete_lines": 38, "one_unknown_lines": 75,
        "strict_one_unknown_lines": 26, "exact_glossary_surfaces": 251,
    }, "exact result coverage")
    check(result.get("guard") == {
        "f1r": "EXCLUDED", "f84": "FORBIDDEN", "f84r": "FORBIDDEN",
        "new_pages": 0, "new_images": 0, "allowed_pages": 179,
        "token_query": {"selected": 32339, "skipped_forbidden": 709, "skipped_not_allowed": 5940},
        "cross_query": {"selected": 4137, "skipped_forbidden": 98, "skipped_not_allowed": 1151},
    }, "exact guarded query accounting")
    check(result.get("working_dictionary") == {
        "v20_entries": 293, "v21_entries": 298, "accepted_tail_entries": 5,
        "v20_prefix_sha256": canonical_hash(v20_dictionary),
        "v21_sha256": canonical_hash(v21_dictionary),
        "base_glossary_surfaces": 246, "v21_glossary_surfaces": 251,
    }, "exact result dictionary state")

    validation_core = {
        "schema": "GDT644_VALIDATION_V1", "experiment_id": "GDT644",
        "status": "PASS" if not issues else "FAIL", "passed_checks": len(passed),
        "issue_count": len(issues), "issues": issues,
        "summary": {
            "target_occurrences": len(audits), "reader_exact": sum(int(row["reader_exact"]) for row in audits),
            "clean_context_compatible": sum(row["verdict"] == "CLEAN_CONTEXT_COMPATIBLE" for row in audits),
            "new_complete_lines": len(new_complete), "new_one_hole_lines": len(new_one),
            "v21_dictionary_entries": len(v21_dictionary),
            "result_content_sha256": result.get("content_sha256"),
        },
    }
    validation = {**validation_core, "content_sha256": canonical_hash(validation_core)}
    VALIDATION.write_text(json.dumps(validation, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"GDT644 validation: {validation['status']} checks={len(passed)} issues={len(issues)}")
    for issue in issues:
        print(f"ISSUE {issue}")
    return 0 if not issues else 1


if __name__ == "__main__":
    raise SystemExit(main())
