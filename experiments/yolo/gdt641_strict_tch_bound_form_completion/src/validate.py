#!/usr/bin/env python3
"""Independent release validator for GDT641."""
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
from collections import Counter, defaultdict
from pathlib import Path

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = Path("experiments/yolo/gdt641_strict_tch_bound_form_completion")
ART = ROOT / BASE / "artifacts"
RUN = ROOT / BASE / "src/run.py"
MANIFEST = ROOT / BASE / "experiment.json"
VALIDATION = ART / "VALIDATION.json"

G640_BASE = Path("experiments/yolo/gdt640_downstream_component_prediction")
G640_ALLOW = G640_BASE / "artifacts/PAGE_ALLOWLIST.tsv"
G640_ONE = G640_BASE / "artifacts/ONE_UNKNOWN_PASSAGES_V17.tsv"
G640_COMPLETE = G640_BASE / "artifacts/COMPLETE_PASSAGES_V17.tsv"
G640_GLOSSARY = G640_BASE / "artifacts/V17_EXACT_TOKEN_GLOSSARY.tsv"
G640_DICTIONARY = G640_BASE / "artifacts/WORKING_DICTIONARY_V17.tsv"
TOKENS = Path("transcription/voynich_zl3b_tokens.tsv")
CROSS = Path("transcription/voynich_cross_transcription_lines.tsv")

TARGETS = ("tcheor", "chetchy")
EXPECTED_OCCURRENCES = {"tcheor": 3, "chetchy": 4}
EXPECTED_LOCI = {
    "tcheor": {"f113r.42", "f15r.12", "f58v.31"},
    "chetchy": {"f29v.1", "f37v.8", "f87r.12", "f88r.30"},
}
EXPECTED_CARDS = {
    "tcheor": {
        "meaning": "kalt-trockener Drogenteil",
        "composition": "tch+e+or",
        "source_locus": "f15r.12",
    },
    "chetchy": {
        "meaning": "getrocknete Droge; kalt-trocken, Grundform",
        "composition": "ch+e+tch+y",
        "source_locus": "f37v.8",
    },
}
EXPECTED_NEW_LINES = {
    "f15r.12": {
        "surface": "tcheor",
        "zl3b": "qotor shor tcheor chy cthaiin shan",
        "smooth": (
            "Kalte Drogenportion; Blüten-/Fruchtstand; kalt-trockener Drogenteil; "
            "trockene Grundform; Blatt-/Krautgut, Klasse III; feucht, Grad I."
        ),
    },
    "f37v.8": {
        "surface": "chetchy",
        "zl3b": "qotor choiin chetchy daiin",
        "smooth": (
            "Kalte Drogenportion; Trockenpräparat, Form III; getrocknete Droge, "
            "kalt-trocken, Grundform; Grad III."
        ),
    },
}

# Every file emitted by run.py. README.md is hand-authored and intentionally
# outside the deterministic builder replay.
OUTPUTS = (
    "PAGE_ALLOWLIST.tsv",
    "TARGET_DECISION_DECK.tsv",
    "FORM_FAMILY_ATLAS.tsv",
    "COMPONENT_BINDING_AUDIT.tsv",
    "ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv",
    "SEQUENTIAL_DECISION_LEDGER.tsv",
    "ROUND_COVERAGE_COUNTS.tsv",
    "ACCEPTED_WHOLE_SURFACE_DEFAULTS.tsv",
    "NEWLY_COMPLETED_LINES.tsv",
    "V18_EXACT_TOKEN_GLOSSARY.tsv",
    "ALL_LINE_CONCRETE_COVERAGE_V18.tsv",
    "COMPLETE_PASSAGES_V18.tsv",
    "ONE_UNKNOWN_PASSAGES_V18.tsv",
    "WORKING_DICTIONARY_V18.tsv",
    "RESULT.json",
)
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
    raw = json.dumps(
        value, sort_keys=True, ensure_ascii=True, separators=(",", ":")
    ).encode()
    return hashlib.sha256(raw).hexdigest()


def load_builder():
    spec = importlib.util.spec_from_file_location("gdt641_builder_validation", RUN)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load GDT641 builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def guarded_query(
    relative_path: Path, pages: set[str], columns: str
) -> tuple[list[dict[str, str]], dict[str, int]]:
    """Materialize an explicitly allowed projection through the guarded CLI."""
    command = [
        str(ROOT / "vmanus-exp"),
        "query-tsv",
        str(relative_path),
        "--selector",
        "page",
    ]
    for page in sorted(pages):
        command.extend(("--allow", page))
    command.extend(
        (
            "--columns",
            columns,
            "--forbid-prefix",
            "f84",
            "--forbid-prefix",
            "f84r",
        )
    )
    completed = subprocess.run(
        command, cwd=ROOT, text=True, capture_output=True, check=False
    )
    if completed.returncode:
        raise RuntimeError(completed.stderr or "guarded query failed")
    stat_lines = [
        line for line in completed.stderr.splitlines() if line.startswith("GUARD_STATS ")
    ]
    if len(stat_lines) != 1:
        raise RuntimeError("guard statistics missing or duplicated")
    materialized = list(csv.DictReader(io.StringIO(completed.stdout), delimiter="\t"))
    if any(
        row.get("page") == "f1r" or row.get("page", "").startswith("f84")
        for row in materialized
    ):
        raise RuntimeError("excluded or forbidden page materialized")
    stats = {
        key: int(value)
        for key, value in json.loads(stat_lines[0][12:]).items()
    }
    return materialized, stats


def independently_exact_target_occurrences(
    token_rows: list[dict[str, str]], cross_rows: list[dict[str, str]]
) -> tuple[dict[str, list[tuple[str, int]]], list[str]]:
    """Reconstruct reader-exact ordinals without using GDT641's stable map."""
    cross_by_locus = {row["locus"]: row for row in cross_rows}
    ordinal: Counter[tuple[str, str]] = Counter()
    exact: dict[str, list[tuple[str, int]]] = defaultdict(list)
    failures: list[str] = []
    ordered = sorted(
        token_rows,
        key=lambda row: (row["page"], row["locus"], int(row["token_index"])),
    )
    for row in ordered:
        surface = row["eva"]
        if surface not in EXPECTED_OCCURRENCES:
            continue
        locus = row["locus"]
        ordinal[locus, surface] += 1
        cross = cross_by_locus.get(locus)
        if cross is None:
            failures.append(f"missing cross-transcription row for {locus}")
            continue
        required_ordinal = ordinal[locus, surface]
        counts = {
            reader: cross[field].split().count(surface)
            for reader, field in (
                ("ZL3b", "zl3b_clean"),
                ("IT2a", "it2a_clean"),
                ("RF1b", "rf1b_clean"),
            )
        }
        if min(counts.values()) < required_ordinal:
            failures.append(
                f"{surface} {locus} ordinal {required_ordinal} reader counts {counts}"
            )
        else:
            exact[surface].append((locus, int(row["token_index"])))
    return dict(exact), failures


def main() -> int:
    passed: list[str] = []
    issues: list[str] = []

    def check(ok: object, name: str, detail: str = "") -> None:
        if ok:
            passed.append(name)
        else:
            issues.append(f"{name}: {detail or 'condition failed'}")

    # Cold replay: every builder-emitted byte is compared with the repository.
    try:
        builder = load_builder()
    except Exception as exc:  # pragma: no cover - release failure path
        builder = None
        issues.append(f"builder import: {type(exc).__name__}: {exc}")
    if builder is not None:
        check(
            tuple(getattr(builder, "OUTPUT_NAMES", ())) == OUTPUTS[:-1],
            "builder output contract",
            str(tuple(getattr(builder, "OUTPUT_NAMES", ()))),
        )
        with tempfile.TemporaryDirectory(prefix="gdt641_validate_") as tmp:
            replay_dir = Path(tmp)
            try:
                replay_result = builder.build(replay_dir)
            except Exception as exc:  # pragma: no cover - release failure path
                replay_result = None
                issues.append(f"builder replay: {type(exc).__name__}: {exc}")
            if replay_result is not None:
                check(
                    {path.name for path in replay_dir.iterdir() if path.is_file()}
                    == set(OUTPUTS),
                    "replay emitted exactly the frozen output set",
                )
                for name in OUTPUTS:
                    expected = ART / name
                    actual = replay_dir / name
                    check(
                        expected.is_file() and actual.is_file(),
                        f"output present:{name}",
                    )
                    if expected.is_file() and actual.is_file():
                        check(
                            expected.read_bytes() == actual.read_bytes(),
                            f"byte replay:{name}",
                            f"repo={sha256(expected)} replay={sha256(actual)}",
                        )
                stored_result = json.loads((ART / "RESULT.json").read_text())
                check(replay_result == stored_result, "builder return equals RESULT")

    result = json.loads((ART / "RESULT.json").read_text(encoding="utf-8"))
    result_core = {
        key: value for key, value in result.items() if key != "content_sha256"
    }
    check(
        result.get("content_sha256") == canonical_hash(result_core),
        "RESULT canonical content hash",
    )
    check(result.get("experiment_id") == "GDT641", "RESULT experiment id")
    check(
        result.get("status")
        == "PASS_2_STRICT_TCH_EXACT_DEFAULTS__2_NEW_COMPLETE_LINES",
        "RESULT status",
    )
    expected_result_outputs = {
        str(BASE / "artifacts" / name)
        for name in OUTPUTS
        if name != "RESULT.json"
    }
    check(
        set(result.get("outputs", {})) == expected_result_outputs,
        "RESULT output inventory",
    )
    for relative, digest in result.get("inputs", {}).items():
        path = ROOT / relative
        check(
            path.is_file() and sha256(path) == digest,
            f"RESULT input hash:{relative}",
        )
    for relative, digest in result.get("outputs", {}).items():
        path = ROOT / relative
        check(
            path.is_file() and sha256(path) == digest,
            f"RESULT output hash:{relative}",
        )
    check(
        str(TOKENS) in result.get("inputs", {})
        and str(CROSS) in result.get("inputs", {}),
        "raw sources are hash-bound inputs",
    )

    # Inherited allow-list and an independent guarded source census.
    allow_rows = read_tsv(ART / "PAGE_ALLOWLIST.tsv")
    pages = {row["page"] for row in allow_rows}
    check(
        (ART / "PAGE_ALLOWLIST.tsv").read_bytes()
        == (ROOT / G640_ALLOW).read_bytes(),
        "GDT640 allow-list inherited byte-for-byte",
    )
    check(len(allow_rows) == len(pages) == 179, "179 unique allowed pages")
    check("f1r" not in pages, "f1r excluded from allow-list")
    check(not any(page.startswith("f84") for page in pages), "f84 family forbidden")
    guard = result.get("guard", {})
    check(
        guard.get("allowed_pages") == 179
        and guard.get("f1r") == "EXCLUDED"
        and guard.get("f84") == "FORBIDDEN"
        and guard.get("f84r") == "FORBIDDEN"
        and guard.get("new_pages") == 0
        and guard.get("new_images") == 0,
        "RESULT material guard",
    )
    try:
        token_rows, token_stats = guarded_query(
            TOKENS,
            pages,
            "page,locus,token_index,eva,section,language,hand",
        )
        cross_rows, cross_stats = guarded_query(
            CROSS,
            pages,
            "page,locus,all_three_present,all_present_exact,zl3b_clean,it2a_clean,rf1b_clean",
        )
    except Exception as exc:  # pragma: no cover - release failure path
        token_rows, cross_rows, token_stats, cross_stats = [], [], {}, {}
        issues.append(f"independent guarded census: {type(exc).__name__}: {exc}")
    check(token_stats == guard.get("token_query"), "independent token guard statistics")
    check(cross_stats == guard.get("cross_query"), "independent cross guard statistics")
    check(
        all(
            row["page"] in pages
            and row["page"] != "f1r"
            and not row["page"].startswith("f84")
            for row in token_rows + cross_rows
        ),
        "independently materialized scope is clean",
    )
    token_counts = Counter(row["eva"] for row in token_rows)
    actual_counts = {target: token_counts[target] for target in TARGETS}
    check(
        actual_counts == EXPECTED_OCCURRENCES,
        "independent guarded target census 3+4",
        str(actual_counts),
    )
    check(sum(actual_counts.values()) == 7, "seven guarded target occurrences")
    actual_loci = {
        target: {row["locus"] for row in token_rows if row["eva"] == target}
        for target in TARGETS
    }
    check(actual_loci == EXPECTED_LOCI, "exact target locus census", str(actual_loci))
    exact_by_target, exact_failures = independently_exact_target_occurrences(
        token_rows, cross_rows
    )
    exact_counts = {
        target: len(exact_by_target.get(target, [])) for target in TARGETS
    }
    check(
        not exact_failures,
        "all target ordinals reader-exact",
        "; ".join(exact_failures),
    )
    check(
        exact_counts == EXPECTED_OCCURRENCES,
        "independent reader-exact census 3+4",
        str(exact_counts),
    )

    # Frozen target cards, exact meanings, and complete-surface-only scope.
    deck = read_tsv(ART / "TARGET_DECISION_DECK.tsv")
    check(tuple(row["surface"] for row in deck) == TARGETS, "target order")
    check(len(deck) == 2, "two target decisions")
    deck_by_surface = {row["surface"]: row for row in deck}
    for target in TARGETS:
        row = deck_by_surface.get(target, {})
        expected = EXPECTED_CARDS[target]
        check(
            row.get("working_meaning_de") == expected["meaning"],
            f"{target} exact meaning",
        )
        check(
            row.get("composition") == expected["composition"],
            f"{target} exact composition",
        )
        check(
            row.get("gdt640_source_locus") == expected["source_locus"],
            f"{target} source locus",
        )
        check(
            int(row.get("occurrences", -1)) == EXPECTED_OCCURRENCES[target],
            f"{target} deck occurrence count",
        )
        check(
            int(row.get("reader_exact_occurrences", -1))
            == EXPECTED_OCCURRENCES[target],
            f"{target} deck reader exact",
        )
        check(
            row.get("decision") == "ACCEPT" and row.get("barrier") == "NONE",
            f"{target} accepted",
        )
        check(
            row.get("scope") == "exact whole surface only",
            f"{target} exact-only scope",
        )
    check(
        "gebunden"
        not in deck_by_surface.get("tcheor", {}).get("working_meaning_de", "").lower(),
        "tcheor e realized by adjective rather than extra literal word",
    )
    check(
        re.search(
            r"blatt|kraut|\bcth\b",
            deck_by_surface.get("chetchy", {}).get("working_meaning_de", ""),
            re.IGNORECASE,
        )
        is None,
        "chetchy imports no CTH/leaf meaning",
    )

    accepted = read_tsv(ART / "ACCEPTED_WHOLE_SURFACE_DEFAULTS.tsv")
    check(
        tuple(row["surface"] for row in accepted) == TARGETS,
        "two accepted exact surfaces",
    )
    accepted_by_surface = {row["surface"]: row for row in accepted}
    for target in TARGETS:
        row = accepted_by_surface.get(target, {})
        expected = EXPECTED_CARDS[target]
        check(
            row.get("working_meaning_de") == expected["meaning"],
            f"{target} accepted meaning",
        )
        check(
            row.get("composition") == expected["composition"],
            f"{target} accepted composition",
        )
        check(
            row.get("source_locus") == expected["source_locus"],
            f"{target} accepted source",
        )
        check(
            row.get("kind") == "EXACT_WHOLE_SURFACE_TCH_COMPLETION"
            and "exact complete surface only" in row.get("context_rule", "")
            and "no substring, naked-body, wrapper or absent-cell transfer"
            in row.get("context_rule", ""),
            f"{target} accepted whole-surface restriction",
        )

    family = read_tsv(ART / "FORM_FAMILY_ATLAS.tsv")
    check(len(family) == 15, "fifteen bounded family witnesses")
    family_by_surface = {row["surface"]: row for row in family}
    for target in TARGETS:
        row = family_by_surface.get(target, {})
        check(
            int(row.get("occurrences", -1)) == EXPECTED_OCCURRENCES[target],
            f"{target} family census",
        )
        check(
            int(row.get("reader_exact_occurrences", -1))
            == EXPECTED_OCCURRENCES[target],
            f"{target} family exact census",
        )
        check(
            row.get("working_reading_de") == EXPECTED_CARDS[target]["meaning"],
            f"{target} family meaning",
        )

    components = read_tsv(ART / "COMPONENT_BINDING_AUDIT.tsv")
    expected_components = {
        ("tcheor", "tch"): (
            "kalt-trocken",
            "BOUND_TCH_QUALITY_BLOCK",
            "inside exact tcheor only",
        ),
        ("tcheor", "e"): (
            "attributive Bindungsstufe",
            "BOUND_E_STAGE",
            "inside exact tcheor only",
        ),
        ("tcheor", "or"): (
            "Drogenteil; Portionslesung bleibt Rivale",
            "BOUND_OR_PART_CARRIER",
            "no bare-or promotion",
        ),
        ("chetchy", "ch+e"): (
            "getrocknet und attributiv gefasst",
            "DRY_ATTRIBUTIVE_SHELL",
            "inside exact chetchy only",
        ),
        ("chetchy", "tch"): (
            "kalt-trockene Qualitätsklasse",
            "BOUND_TCH_QUALITY_BLOCK",
            "inside exact chetchy only",
        ),
        ("chetchy", "y"): (
            "Grundformabschluss",
            "BOUND_BASE_FORM",
            "inside exact chetchy only",
        ),
    }
    component_by_key = {
        (row["surface"], row["segment"]): row for row in components
    }
    check(
        len(components) == len(component_by_key) == 6,
        "six unique component bindings",
    )
    check(set(component_by_key) == set(expected_components), "exact component inventory")
    for key, (value, kind, licensed) in expected_components.items():
        row = component_by_key.get(key, {})
        check(
            row.get("working_value_de") == value
            and row.get("evidence_kind") == kind
            and row.get("licensed_use") == licensed,
            f"component binding:{key[0]}:{key[1]}",
        )
        evidence = row.get("evidence_path", "")
        check(
            bool(evidence)
            and (ROOT / evidence).is_file()
            and result.get("inputs", {}).get(evidence) == sha256(ROOT / evidence),
            f"component evidence hash:{key[0]}:{key[1]}",
        )

    # V17 remains an exact prefix; only the two complete target surfaces enter.
    v17_dictionary = read_tsv(ROOT / G640_DICTIONARY)
    v18_dictionary = read_tsv(ART / "WORKING_DICTIONARY_V18.tsv")
    check(
        len(v17_dictionary) == 283 and len(v18_dictionary) == 285,
        "dictionary 283 to 285",
    )
    check(v18_dictionary[:283] == v17_dictionary, "V17 dictionary prefix preserved")
    check(
        tuple(
            row["entry"].split("@", 1)[0] for row in v18_dictionary[283:]
        )
        == TARGETS,
        "V18 dictionary tail contains only exact targets",
    )
    check(
        all(
            row["kind"] == "EXACT_WHOLE_SURFACE_TCH_COMPLETION"
            and "no substring, naked-body, wrapper or absent-cell transfer"
            in row["context_rule"]
            for row in v18_dictionary[283:]
        ),
        "no bare component dictionary promotion",
    )
    forbidden_bare = {"ch", "che", "e", "or", "tch", "y", "cth"}
    check(
        not any(
            row["entry"].split("@", 1)[0].lower() in forbidden_bare
            for row in v18_dictionary[283:]
        ),
        "no new CH/CHE/E/OR/TCH/Y/CTH row",
    )
    v17_glossary = read_tsv(ROOT / G640_GLOSSARY)
    v18_glossary = read_tsv(ART / "V18_EXACT_TOKEN_GLOSSARY.tsv")
    v17_glossary_by_surface = {
        row["surface"]: row for row in v17_glossary
    }
    v18_glossary_by_surface = {
        row["surface"]: row for row in v18_glossary
    }
    check(
        len(v17_glossary) == 236 and len(v18_glossary) == 238,
        "glossary 236 to 238",
    )
    check(
        all(
            v18_glossary_by_surface.get(surface) == row
            for surface, row in v17_glossary_by_surface.items()
        ),
        "all V17 glossary cards preserved",
    )
    check(
        set(v18_glossary_by_surface) - set(v17_glossary_by_surface)
        == set(TARGETS),
        "only target surfaces added to glossary",
    )
    for target in TARGETS:
        row = v18_glossary_by_surface.get(target, {})
        check(
            row.get("working_meaning_de") == EXPECTED_CARDS[target]["meaning"],
            f"{target} glossary meaning",
        )
        check(
            row.get("scope_state") == "KNOWN_EXACT_WHOLE"
            and row.get("strength") == "EXACT_WHOLE_SURFACE_TCH_COMPLETION",
            f"{target} glossary exact-whole status",
        )

    # Full coverage totals, sequential deltas, and exactly two new strict lines.
    coverage = read_tsv(ART / "ALL_LINE_CONCRETE_COVERAGE_V18.tsv")
    complete = read_tsv(ART / "COMPLETE_PASSAGES_V18.tsv")
    one_unknown = read_tsv(ART / "ONE_UNKNOWN_PASSAGES_V18.tsv")
    check(len(coverage) == 4128, "4,128 physical coverage lines")
    check(
        sum(int(row["known_tokens"]) for row in coverage) == 9748
        and sum(int(row["unknown_tokens"]) for row in coverage) == 22591,
        "coverage positions 9748/22591",
    )
    check(
        len(complete) == 44
        and sum(int(row["strict_complete"]) for row in complete) == 33,
        "complete lines 44/33 strict",
    )
    check(
        len(one_unknown) == 60
        and sum(int(row["strict_eligible"]) for row in one_unknown) == 17,
        "one-hole lines 60/17 strict",
    )
    base_complete = read_tsv(ROOT / G640_COMPLETE)
    base_complete_loci = {row["locus"] for row in base_complete}
    final_complete_loci = {row["locus"] for row in complete}
    check(len(base_complete) == 42, "V17 has forty-two complete lines")
    check(
        final_complete_loci - base_complete_loci == set(EXPECTED_NEW_LINES),
        "exactly two new complete loci",
        str(sorted(final_complete_loci - base_complete_loci)),
    )
    check(base_complete_loci <= final_complete_loci, "no V17 complete line lost")
    frontier = read_tsv(ROOT / G640_ONE)
    strict_frontier = {
        row["unknown_surface"]: row["locus"]
        for row in frontier
        if int(row["strict_eligible"]) and row["unknown_surface"] in TARGETS
    }
    check(
        strict_frontier
        == {
            target: EXPECTED_CARDS[target]["source_locus"]
            for target in TARGETS
        },
        "both targets were frozen strict V17 holes",
        str(strict_frontier),
    )
    new_lines = read_tsv(ART / "NEWLY_COMPLETED_LINES.tsv")
    check(len(new_lines) == 2, "two newly completed line cards")
    new_by_locus = {row["locus"]: row for row in new_lines}
    check(set(new_by_locus) == set(EXPECTED_NEW_LINES), "new-line card locus set")
    for locus, expected in EXPECTED_NEW_LINES.items():
        row = new_by_locus.get(locus, {})
        check(
            row.get("surface") == expected["surface"]
            and row.get("zl3b_line") == expected["zl3b"]
            and row.get("smoothed_working_reading_de") == expected["smooth"],
            f"exact new line:{locus}",
        )
        check(
            row.get("strict_complete") == "1"
            and row.get("all_present_exact") == "1"
            and row.get("scope_clean") == "1",
            f"strict clean new line:{locus}",
        )
    check(
        new_by_locus.get("f37v.8", {})
        .get("smoothed_working_reading_de", "")
        .endswith("Grad III."),
        "f37v.8 smooths terminal daiin to Grad III",
    )

    rounds = read_tsv(ART / "ROUND_COVERAGE_COUNTS.tsv")
    expected_rounds = [
        ("0", "BASE_V17", "283", "9741", "22598", "42", "31", "62", "19", "236"),
        ("1", "tcheor", "284", "9744", "22595", "43", "32", "61", "18", "237"),
        ("2", "chetchy", "285", "9748", "22591", "44", "33", "60", "17", "238"),
    ]
    actual_rounds = [
        (
            row["round"],
            row["surface"],
            row["dictionary_entries"],
            row["known_token_positions"],
            row["unknown_token_positions"],
            row["complete_multi_token_lines"],
            row["strict_complete_lines"],
            row["one_unknown_lines"],
            row["strict_one_unknown_lines"],
            row["exact_glossary_surfaces"],
        )
        for row in rounds
    ]
    check(
        actual_rounds == expected_rounds,
        "exact sequential coverage deltas",
        str(actual_rounds),
    )

    # All seven occurrences must yield the frozen 4 concrete / 3 opaque split.
    audits = read_tsv(ART / "ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv")
    check(len(audits) == 7, "seven occurrence audit rows")
    audit_counts = Counter(row["surface"] for row in audits)
    check(
        {target: audit_counts[target] for target in TARGETS}
        == EXPECTED_OCCURRENCES,
        "audit target census 3+4",
    )
    audit_loci = {
        target: {
            row["locus"] for row in audits if row["surface"] == target
        }
        for target in TARGETS
    }
    check(audit_loci == EXPECTED_LOCI, "audit locus census")
    check(
        all(row["reader_exact"] == "1" for row in audits),
        "all audit rows reader exact",
    )
    check(
        Counter(row["verdict"] for row in audits)
        == Counter({"CONSISTENT_CONCRETE": 4, "OPAQUE_CONTEXT": 3}),
        "audit verdict split 4/3",
    )
    recalculated_verdicts = []
    for row in audits:
        known = int(row["known_other_tokens"])
        positions = int(row["other_token_positions"])
        recalculated_verdicts.append(
            "OPAQUE_CONTEXT"
            if known < 2 and not (positions == 1 and known == 1)
            else "CONSISTENT_CONCRETE"
        )
        check(
            row["after_gloss"] == EXPECTED_CARDS[row["surface"]]["meaning"],
            f"audit after-gloss:{row['audit_id']}",
        )
        check(
            row["before_state"] == "UNKNOWN_SURFACE"
            and row["before_gloss"] == f"[{row['surface']}:?]",
            f"audit was an actual prior hole:{row['audit_id']}",
        )
    check(
        recalculated_verdicts == [row["verdict"] for row in audits],
        "audit verdicts independently replay their context rule",
    )
    audit_witnesses = {
        target: sorted(
            (row["locus"], int(row["token_ordinal"]))
            for row in audits
            if row["surface"] == target
        )
        for target in TARGETS
    }
    independent_witnesses = {
        target: sorted(
            (locus, token_index)
            for locus, token_index in exact_by_target.get(target, [])
        )
        for target in TARGETS
    }
    check(
        audit_witnesses == independent_witnesses,
        "audit rows match independent exact witnesses",
    )

    ledger = read_tsv(ART / "SEQUENTIAL_DECISION_LEDGER.tsv")
    check(tuple(row["surface"] for row in ledger) == TARGETS, "ledger target order")
    check(
        [
            (
                row["consistent_concrete"],
                row["opaque_context"],
                row["reader_boundary_warning"],
            )
            for row in ledger
        ]
        == [("2", "1", "0"), ("2", "2", "0")],
        "ledger verdict partitions",
    )
    check(
        [
            (
                row["trial_complete_gain"],
                row["trial_strict_complete_gain"],
                row["trial_new_complete_loci"],
            )
            for row in ledger
        ]
        == [("1", "1", "f15r.12"), ("1", "1", "f37v.8")],
        "ledger exact line gains",
    )

    target_run = result.get("target_run", {})
    check(
        (
            target_run.get("candidates"),
            target_run.get("accepted"),
            target_run.get("held"),
            target_run.get("audited_occurrences"),
        )
        == (2, 2, 0, 7),
        "RESULT target counts",
    )
    check(
        target_run.get("accepted_surfaces") == list(TARGETS)
        and target_run.get("verdicts")
        == {"CONSISTENT_CONCRETE": 4, "OPAQUE_CONTEXT": 3},
        "RESULT target identities and verdicts",
    )
    expected_coverage = {
        "base_complete_multi_token_lines": 42,
        "base_strict_complete_lines": 31,
        "newly_completed_lines": 2,
        "physical_lines": 4128,
        "known_token_positions": 9748,
        "unknown_token_positions": 22591,
        "complete_multi_token_lines": 44,
        "strict_complete_lines": 33,
        "one_unknown_lines": 60,
        "strict_one_unknown_lines": 17,
        "exact_glossary_surfaces": 238,
    }
    check(result.get("coverage") == expected_coverage, "RESULT exact V18 coverage")
    expected_dictionary = {
        "v17_entries": 283,
        "v18_entries": 285,
        "accepted_tail_entries": 2,
        "base_glossary_surfaces": 236,
        "v18_glossary_surfaces": 238,
    }
    check(
        all(
            result.get("working_dictionary", {}).get(key) == value
            for key, value in expected_dictionary.items()
        ),
        "RESULT dictionary counts",
    )

    # Generic placeholder language is forbidden from generated text artifacts.
    for name in OUTPUTS:
        check(
            GENERIC_FILLER.search((ART / name).read_text(encoding="utf-8"))
            is None,
            f"no generic filler:{name}",
        )

    # Manifest gates are checked when populated; an unscored scaffold may have
    # empty arrays, but no populated item may lack or mismatch a hash.
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    check(manifest.get("experiment_id") == "GDT641", "manifest experiment id")
    check(
        manifest.get("slug") == "strict_tch_bound_form_completion",
        "manifest slug",
    )
    check(
        manifest.get("sealed_data", {}).get("f84") == "FORBIDDEN"
        and manifest.get("sealed_data", {}).get("f84r") == "FORBIDDEN",
        "manifest f84/f84r seals",
    )
    check(
        manifest.get("commands", {}).get("run")
        == f"python3 {BASE}/src/run.py"
        and manifest.get("commands", {}).get("validate")
        == f"python3 {BASE}/src/validate.py",
        "manifest commands",
    )
    for field in ("inputs", "outputs"):
        items = manifest.get(field, [])
        check(isinstance(items, list), f"manifest {field} is a list")
        if not isinstance(items, list):
            continue
        for index, item in enumerate(items):
            ok_shape = (
                isinstance(item, dict)
                and isinstance(item.get("path"), str)
                and isinstance(item.get("sha256"), str)
                and bool(item.get("path"))
                and bool(item.get("sha256"))
            )
            check(ok_shape, f"manifest {field}[{index}] hash shape")
            if not ok_shape:
                continue
            relative = Path(item["path"])
            check(
                not relative.is_absolute() and ".." not in relative.parts,
                f"manifest {field}[{index}] relative path",
            )
            path = ROOT / relative
            check(
                path.is_file() and sha256(path) == item["sha256"],
                f"manifest {field} hash:{item['path']}",
            )
    validation = manifest.get("validation", {})
    if validation.get("artifact"):
        validation_path = ROOT / validation["artifact"]
        check(validation_path.is_file(), "manifest validation artifact exists")

    payload = {
        "schema": "GDT641_INDEPENDENT_VALIDATION_V1",
        "experiment_id": "GDT641",
        "status": "PASS" if not issues else "FAIL",
        "checks_passed": len(passed),
        "issues": issues,
        "validated_result_sha256": sha256(ART / "RESULT.json"),
        "validator_sha256": sha256(Path(__file__)),
    }
    VALIDATION.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        f"GDT641 validation: {payload['status']} "
        f"checks={len(passed)} issues={len(issues)}"
    )
    for issue in issues:
        print("FAIL:", issue)
    return 0 if not issues else 1


if __name__ == "__main__":
    raise SystemExit(main())
