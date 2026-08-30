#!/usr/bin/env python3
"""Independent source-first release validator for GDT667."""
from __future__ import annotations

import csv
import hashlib
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
BASE = Path("experiments/yolo/gdt667_one_hundred_one_residual_family_completion")
G666 = Path("experiments/yolo/gdt666_one_hundred_fifty_one_residual_family_completion")
ART = ROOT / BASE / "artifacts"
RUN = ROOT / BASE / "src/run.py"
CARD_SPECS = ROOT / BASE / "src/CARD_SPECS.tsv"
OL_SPECS = ROOT / BASE / "src/INHERITED_OL_REVISION_SPECS.tsv"
SOL_SPECS = ROOT / BASE / "src/INHERITED_SOL_REVISION_SPECS.tsv"
STEM_SPECS = ROOT / BASE / "src/STEM_MODEL_SPECS.tsv"
MANUAL_SPECS = ROOT / BASE / "src/MANUAL_PASSAGE_SPECS.tsv"
CANDIDATE_SPECS = tuple(ROOT / BASE / "src" / name for name in (
    "CARD_SPECS_RECIPE_CANDIDATE.tsv",
    "CARD_SPECS_STEM_CANDIDATE.tsv",
    "CARD_SPECS_READER_CANDIDATE.tsv",
    "FINAL_CARD_AUDIT.md",
    "RECIPE_MASTER_MEMO.md",
    "STEM_COMPOSITOR_MEMO.md",
    "MANUAL_PASSAGE_SPECS_READER.tsv",
))
TOKENS = Path("transcription/voynich_zl3b_tokens.tsv")
CROSS = Path("transcription/voynich_cross_transcription_lines.tsv")

OUTPUT_NAMES = (
    "PAGE_ALLOWLIST.tsv", "TARGET_DECISION_DECK.tsv", "ACCEPTED_WHOLE_SURFACE_DEFAULTS.tsv",
    "CONTEXT_RENDERING_CARDS.tsv", "CARD_ARCHITECTURE_SUMMARY.tsv",
    "ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv", "READER_VARIANT_AUDIT.tsv",
    "FAMILY_COMPOSITION_ATLAS.tsv", "STEM_MODEL_V44.tsv",
    "INHERITED_OL_RENDER_REVISIONS.tsv", "INHERITED_SOL_RENDER_REVISIONS.tsv",
    "MANUAL_PASSAGE_AUDIT.tsv",
    "FRONTIER_101_COMPLETIONS.tsv", "TARGET_LINE_TRANSLATIONS.tsv",
    "ROUND_COVERAGE_COUNTS.tsv", "NEWLY_COMPLETED_LINES.tsv",
    "NEWLY_EXPOSED_ONE_HOLE_LINES.tsv", "NEXT_FRONTIER_FULL_PANEL_COUNTS.tsv",
    "V44_WORKING_TOKEN_GLOSSARY.tsv",
    "WORKING_DICTIONARY_V44.tsv", "ALL_LINE_CONCRETE_COVERAGE_V44.tsv",
    "COMPLETE_PASSAGES_V44.tsv", "ONE_UNKNOWN_PASSAGES_V44.tsv",
)

TARGET_ORDER = tuple("""
qoolkeey oiees oain olshy ypchedy oeoar sotchdaiin qokcho qokair qopchcfhy
folaiin chedain qoctholy alam qotedal kechy oeedaiin qokeedain alchedy shsodaiin
sheky qokod kald oteol cholchom ychy yko qoeees ychoees doky ddor ytym qoear
ychol shotchor ykeeb yches oldam chetchaiin tch chd choy chekl qot qotcham
qocheor sheam kary dey ykchey dairl otydal cheos chtedy qotchar sheeod chokeeody
shtaiin chokody ykchol tcheody yokeey ychocthy ykaiir ksho tchain sheoldy qokaly
qocthol octham qokom chkar olshees qolain olchdar chkorol dairol olchdy tshedor
qokedar qolsheey otlol sheeky sshkchdy dedy dairydy cheg lched qolteedy olfar
okeeeykeey chorolk ckheckhy olkaycthy dolas olkees odol agairom ctheol chshoty
cphol
""".split())
TARGETS = frozenset(TARGET_ORDER)


def parse_counts(raw: str) -> dict[str, int]:
    return {item.split("=", 1)[0]: int(item.split("=", 1)[1]) for item in raw.split()}


EXPECTED_COUNTS = parse_counts("""
qoolkeey=1 oiees=1 oain=11 olshy=3 ypchedy=12 oeoar=1 sotchdaiin=1 qokcho=9
qokair=21 qopchcfhy=1 folaiin=1 chedain=17 qoctholy=1 alam=10 qotedal=3 kechy=4
oeedaiin=2 qokeedain=2 alchedy=4 shsodaiin=1 sheky=28 qokod=7 kald=1 oteol=26
cholchom=1 ychy=4 yko=2 qoeees=3 ychoees=1 doky=1 ddor=2 ytym=1 qoear=1
ychol=10 shotchor=1 ykeeb=1 yches=2 oldam=4 chetchaiin=1 tch=2 chd=6 choy=14
chekl=1 qot=14 qotcham=1 qocheor=1 sheam=1 kary=4 dey=2 ykchey=4 dairl=1
otydal=1 cheos=28 chtedy=2 qotchar=3 sheeod=2 chokeeody=1 shtaiin=1 chokody=1
ykchol=6 tcheody=5 yokeey=1 ychocthy=2 ykaiir=1 ksho=8 tchain=1 sheoldy=3
qokaly=17 qocthol=2 octham=1 qokom=2 chkar=9 olshees=1 qolain=3 olchdar=1
chkorol=1 dairol=1 olchdy=8 tshedor=1 qokedar=8 qolsheey=1 otlol=1 sheeky=14
sshkchdy=1 dedy=3 dairydy=1 cheg=3 lched=6 qolteedy=1 olfar=1 okeeeykeey=1
chorolk=1 ckheckhy=1 olkaycthy=1 dolas=1 olkees=3 odol=2 agairom=1 ctheol=8
chshoty=1 cphol=11
""")

CONTEXT_SURFACES = frozenset(surface for surface in TARGETS if len(surface) <= 3)
OL_REVISIONS = parse_counts("""
olaiin=39 olain=11 olal=5 oldal=2 oldy=25 olkaiin=28 olkain=33 olkam=11 olkchdy=4
olkedy=22 olkeeo=4 olkol=3 olor=26 ols=17 olshdy=3 olsheedy=1 olshey=13 oltedy=6
olteedy=3
""")
OL_EXCEPTIONS = frozenset({"ol", "oly", "olyly"})
GRAIN_SURFACES = frozenset({"chkag", "kcharg", "chokolg", "cheg"})
ATOM_SPELLINGS = {
    "O_PREP": ("o",), "L_WOOD": ("l",), "FREE_LIBRA_SIGLUM": ("l",),
    "LEARNED_OL_BASE": ("ol",), "OL_MATERIAL": ("ol",), "S_SEED": ("s",),
    "OLY_STRAIN_ACTION": ("oly",),
    "S_TERM_SPECIES": ("s",), "SOL_SEED_PREP": ("sol",), "SAL_SEED_RAW": ("sal",),
    "CH_DRY": ("ch",), "SH_MOIST": ("sh",), "K_HOT": ("k",), "T_COLD": ("t",),
    "R_ROOT": ("r",), "CTH_HERB": ("cth",), "CHOR_PLANT_PART": ("chor",),
    "CKH_COMPOSITE": ("ckh",), "F_FLOWER": ("f", "cfh"), "P_POWDER": ("p",),
    "QO_COMMAND": ("q", "qo"), "QOL_ADD": ("qol",), "QOKOL_HEAT": ("qokol",),
    "Y_REFERENCE": ("y",), "Y_START_OR_CLOSE": ("y",), "D_MEASURE": ("d",),
    "D_TERM_CLOSE": ("d",), "DY_FINISHED": ("dy",), "E_MIDDLE": ("e",),
    "EE_END": ("ee",), "EEE_LONG_OR_FINAL": ("eee",), "A_PART_OR_LINK": ("a",),
    "AL_RAW_I": ("al",), "AN_I": ("an",), "AR_FRACTION_I": ("ar",),
    "AIR_FRACTION_II": ("air",), "AIIR_FRACTION_III": ("aiir",),
    "OR_PORTION": ("or",), "AM_UNIT_I": ("am",), "MANIPULUS_SIGLUM": ("m",),
    "G_GRAIN_SIGLUM": ("g",), "AIN_II": ("ain",), "AIIN_III": ("aiin",),
    "IN_FORM_II": ("in",), "IIN_FORM_III": ("iin",), "IIIN_FORM_IV": ("iiin",),
    "J_BUNDLE": ("j",), "B_UNKNOWN": ("b",), "I_FORM_I": ("i",),
    "SO_SEED_PREP": ("so",), "OM_HANDFUL_PREP": ("om",),
    "CPH_COMPOSITE": ("cph",),
}
GENERIC = re.compile(
    r"arbeitsgut|arbeitsvorgang|arbeitschritt|arbeitsschritt|arbeitsmittel|arbeitsstoff|"
    r"arbeitsprodukt|vorgang ausführen|gut bearbeiten|nimm werkzeug|führe .{0,30} aus|"
    r"leite (?:es |das |sie )?weiter",
    re.I,
)
OPEN_MARKER = re.compile(r"\[[^\]\n]+:\?\]")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_hash(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def split_pipe(value: str) -> list[str]:
    return value.split(" | ") if value else []


def guarded_query(path: Path, pages: set[str], columns: str) -> tuple[list[dict[str, str]], dict[str, int]]:
    command = [str(ROOT / "vmanus-exp"), "query-tsv", str(path), "--selector", "page"]
    for page in sorted(pages):
        command.extend(("--allow", page))
    command.extend((
        "--columns", columns,
        "--forbid-prefix", "f1r", "--forbid-prefix", "f84", "--forbid-prefix", "f84r",
    ))
    completed = subprocess.run(command, cwd=ROOT, check=True, text=True, capture_output=True)
    rows = list(csv.DictReader(io.StringIO(completed.stdout), delimiter="\t"))
    stats_lines = [line for line in completed.stderr.splitlines() if line.startswith("GUARD_STATS ")]
    if len(stats_lines) != 1:
        raise RuntimeError("guarded query did not emit exactly one statistics line")
    stats = json.loads(stats_lines[0].removeprefix("GUARD_STATS "))
    return rows, {key: int(value) for key, value in stats.items()}


def coverage_metrics(
    coverage: list[dict[str, str]], one: list[dict[str, str]],
    complete: list[dict[str, str]], glossary: list[dict[str, str]],
) -> dict[str, int]:
    return {
        "physical_lines": len(coverage),
        "known_token_positions": sum(int(row["known_tokens"]) for row in coverage),
        "unknown_token_positions": sum(int(row["unknown_tokens"]) for row in coverage),
        "complete_multi_token_lines": len(complete),
        "strict_complete_lines": sum(int(row["strict_complete"]) for row in complete),
        "one_unknown_lines": len(one),
        "strict_one_unknown_lines": sum(int(row["strict_eligible"]) for row in one),
        "working_glossary_surfaces": len(glossary),
    }


def merged_surface_for(row: dict[str, str]) -> str:
    direction = row["reader_merge_direction"]
    if direction == "LEFT":
        return row["left_surface"] + row["surface"]
    if direction == "RIGHT":
        return row["surface"] + row["right_surface"]
    if direction == "BOTH":
        return row["left_surface"] + row["surface"] + row["right_surface"]
    return "NONE"


def aligned_merge_evidence(
    source: tuple[str, ...], reader: tuple[str, ...], target_index: int,
    expected_surface: str,
) -> set[str]:
    """Independently replay the fixed left-to-right minimum-cost alignment."""
    n, m = len(source), len(reader)
    cells: list[list[tuple[int, int, list[tuple[str, tuple[int, ...], str]]] | None]] = [
        [None] * (m + 1) for _ in range(n + 1)
    ]
    cells[0][0] = (0, 0, [])

    def offer(
        i: int, j: int, cost: int, steps: int,
        path: list[tuple[str, tuple[int, ...], str]],
        operation: tuple[str, tuple[int, ...], str],
    ) -> None:
        candidate = (cost, steps, [*path, operation])
        previous = cells[i][j]
        if previous is None or candidate[:2] < previous[:2]:
            cells[i][j] = candidate

    for i in range(n + 1):
        for j in range(m + 1):
            cell = cells[i][j]
            if cell is None:
                continue
            cost, steps, path = cell
            if i < n and j < m:
                offer(i + 1, j + 1, cost + (0 if source[i] == reader[j] else 10), steps + 1,
                      path, ("ONE", (i,), reader[j]))
            if i + 1 < n and j < m and source[i] + source[i + 1] == reader[j]:
                offer(i + 2, j + 1, cost + 1, steps + 1, path,
                      ("MERGE_2", (i, i + 1), reader[j]))
            if i + 2 < n and j < m and source[i] + source[i + 1] + source[i + 2] == reader[j]:
                offer(i + 3, j + 1, cost + 1, steps + 1, path,
                      ("MERGE_3", (i, i + 1, i + 2), reader[j]))
            if i < n and j + 1 < m and source[i] == reader[j] + reader[j + 1]:
                offer(i + 1, j + 2, cost + 1, steps + 1, path,
                      ("SPLIT_2", (i,), source[i]))
            if i < n:
                offer(i + 1, j, cost + 10, steps + 1, path, ("DELETE", (i,), ""))
            if j < m:
                offer(i, j + 1, cost + 10, steps + 1, path, ("INSERT", (), reader[j]))
    final = cells[n][m]
    if final is None:
        raise RuntimeError("reader alignment unexpectedly has no path")
    directions: set[str] = set()
    for op, source_indices, merged in final[2]:
        if op == "MERGE_2" and merged == expected_surface:
            if target_index == source_indices[0]:
                directions.add("RIGHT")
            elif target_index == source_indices[1]:
                directions.add("LEFT")
        elif op == "MERGE_3" and merged == expected_surface and target_index == source_indices[1]:
            directions.add("BOTH")
    return directions


def main() -> int:
    checks: list[dict[str, object]] = []

    def check(name: str, condition: bool, detail: object = "") -> None:
        checks.append({"name": name, "pass": bool(condition), "detail": detail})

    # Establish the safe panel and query the two mixed sources through their
    # guarded selector before trusting any GDT667 result or generated artifact.
    base_pages = {row["page"] for row in read_tsv(ROOT / G666 / "artifacts/PAGE_ALLOWLIST.tsv")}
    check("inherited safe page allowlist", len(base_pages) == 179)
    check("f1r excluded before source query", "f1r" not in base_pages)
    check("sealed f84 family excluded before source query", not any(page.startswith("f84") for page in base_pages))
    tokens, token_stats = guarded_query(
        TOKENS, base_pages, "page,locus,token_index,eva,kind,section,language,hand"
    )
    cross, cross_stats = guarded_query(
        CROSS, base_pages,
        "page,locus,all_three_present,all_present_exact,zl3b_clean,it2a_clean,rf1b_clean",
    )
    check("guarded token census", len(tokens) == 32339 and token_stats["selected"] == 32339, token_stats)
    check("guarded cross census", len(cross) == 4137 and cross_stats["selected"] == 4137, cross_stats)
    check("token guard rejected forbidden selectors", token_stats["skipped_forbidden"] > 0, token_stats)
    check("cross guard rejected forbidden selectors", cross_stats["skipped_forbidden"] > 0, cross_stats)
    check("materialized token pages safe", all(row["page"] in base_pages for row in tokens))
    check("materialized cross pages safe", all(row["page"] in base_pages for row in cross))

    by_line: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in tokens:
        by_line[row["locus"]].append(row)
    for line in by_line.values():
        line.sort(key=lambda row: int(row["token_index"]))
    cross_by_locus = {row["locus"]: row for row in cross}
    check("source physical-line census", len(by_line) == 4128 and len(cross_by_locus) == 4137)
    check("source token/cross identity", all(
        locus in cross_by_locus
        and " ".join(row["eva"] for row in line) == cross_by_locus[locus]["zl3b_clean"]
        for locus, line in by_line.items()
    ))
    raw_counts = Counter(row["eva"] for row in tokens)
    for surface in TARGET_ORDER:
        check(f"raw count {surface}", raw_counts[surface] == EXPECTED_COUNTS[surface], raw_counts[surface])
    check("target count sum", sum(EXPECTED_COUNTS.values()) == 438)

    specs = read_tsv(CARD_SPECS)
    spec_fields = {"surface", "working_meaning_de", "composition", "strongest_rival_de", "family"}
    check("CARD_SPECS columns", bool(specs) and set(specs[0]) == spec_fields, list(specs[0]) if specs else [])
    spec_order = tuple(row["surface"] for row in specs)
    check("CARD_SPECS fixed order", spec_order == TARGET_ORDER)
    check("CARD_SPECS 101 unique forms", len(specs) == len(set(spec_order)) == 101)
    check("CARD_SPECS all fields populated", all(all(row[field] for field in spec_fields) for row in specs))
    check("CARD_SPECS raw positions", sum(raw_counts[row["surface"]] for row in specs) == 438)
    check("CARD_SPECS no generic filler", not any(GENERIC.search(row["working_meaning_de"]) for row in specs))
    check("CARD_SPECS no open marker", not any(OPEN_MARKER.search("\t".join(row.values())) for row in specs))
    specs_by_surface = {row["surface"]: row for row in specs}

    ol_specs = read_tsv(OL_SPECS)
    ol_fields = {"surface", "positions", "practical_meaning_de", "composition", "retained_rival_de"}
    check("O+L source columns", bool(ol_specs) and set(ol_specs[0]) == ol_fields)
    check("O+L source exact set", {row["surface"] for row in ol_specs} == set(OL_REVISIONS))
    check("O+L source 19 unique forms", len(ol_specs) == len({row["surface"] for row in ol_specs}) == 19)
    check("O+L source position sum 256", sum(int(row["positions"]) for row in ol_specs) == 256)

    sol_specs = read_tsv(SOL_SPECS)
    check("SOL source columns", bool(sol_specs) and set(sol_specs[0]) == ol_fields)
    check("SOL source exact set", {row["surface"] for row in sol_specs} == {"solaiin", "sols"})
    check("SOL source 2 unique forms and 4 positions", len(sol_specs) == 2
          and len({row["surface"] for row in sol_specs}) == 2
          and sum(int(row["positions"]) for row in sol_specs) == 4)

    stem_specs = read_tsv(STEM_SPECS)
    stem_fields = {
        "stem", "structural_role", "practical_default_de", "scope", "examples",
        "exclusions", "strength",
    }
    check("stem-model source columns", bool(stem_specs) and set(stem_specs[0]) == stem_fields)
    check("stem-model source 52 rows", len(stem_specs) == 52)
    check("stem structural roles distinct from German defaults", all(
        row["structural_role"] and row["practical_default_de"]
        and row["structural_role"] != row["practical_default_de"]
        for row in stem_specs
    ))

    manual_specs = read_tsv(MANUAL_SPECS)
    manual_fields = {"rank", "locus", "zl3b_line", "manual_workshop_translation_de", "notes"}
    check("manual-passage source columns", bool(manual_specs) and set(manual_specs[0]) == manual_fields)
    check("manual-passage source dimensions", len(manual_specs) == 25
          and [int(row["rank"]) for row in manual_specs] == list(range(1, 26))
          and len({row["locus"] for row in manual_specs}) == 25)

    pages = {row["page"] for row in read_tsv(ART / "PAGE_ALLOWLIST.tsv")}
    check("released page allowlist inherited exactly", pages == base_pages)
    result = json.loads((ART / "RESULT.json").read_text(encoding="utf-8"))
    deck = read_tsv(ART / "TARGET_DECISION_DECK.tsv")
    accepted = read_tsv(ART / "ACCEPTED_WHOLE_SURFACE_DEFAULTS.tsv")
    context = read_tsv(ART / "CONTEXT_RENDERING_CARDS.tsv")
    architecture = read_tsv(ART / "CARD_ARCHITECTURE_SUMMARY.tsv")
    audit = read_tsv(ART / "ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv")
    reader = read_tsv(ART / "READER_VARIANT_AUDIT.tsv")
    family = read_tsv(ART / "FAMILY_COMPOSITION_ATLAS.tsv")
    stem_model = read_tsv(ART / "STEM_MODEL_V44.tsv")
    ol_revisions = read_tsv(ART / "INHERITED_OL_RENDER_REVISIONS.tsv")
    sol_revisions = read_tsv(ART / "INHERITED_SOL_RENDER_REVISIONS.tsv")
    manual = read_tsv(ART / "MANUAL_PASSAGE_AUDIT.tsv")
    frontier = read_tsv(ART / "FRONTIER_101_COMPLETIONS.tsv")
    target_lines = read_tsv(ART / "TARGET_LINE_TRANSLATIONS.tsv")
    rounds = read_tsv(ART / "ROUND_COVERAGE_COUNTS.tsv")
    glossary = read_tsv(ART / "V44_WORKING_TOKEN_GLOSSARY.tsv")
    dictionary = read_tsv(ART / "WORKING_DICTIONARY_V44.tsv")
    coverage = read_tsv(ART / "ALL_LINE_CONCRETE_COVERAGE_V44.tsv")
    complete = read_tsv(ART / "COMPLETE_PASSAGES_V44.tsv")
    one = read_tsv(ART / "ONE_UNKNOWN_PASSAGES_V44.tsv")
    new_complete = read_tsv(ART / "NEWLY_COMPLETED_LINES.tsv")
    new_one = read_tsv(ART / "NEWLY_EXPOSED_ONE_HOLE_LINES.tsv")
    next_frontier = read_tsv(ART / "NEXT_FRONTIER_FULL_PANEL_COUNTS.tsv")

    base_art = ROOT / G666 / "artifacts"
    base_frontier = read_tsv(base_art / "NEWLY_EXPOSED_ONE_HOLE_LINES.tsv")
    base_coverage = read_tsv(base_art / "ALL_LINE_CONCRETE_COVERAGE_V43.tsv")
    base_complete = read_tsv(base_art / "COMPLETE_PASSAGES_V43.tsv")
    base_one = read_tsv(base_art / "ONE_UNKNOWN_PASSAGES_V43.tsv")
    base_glossary = read_tsv(base_art / "V43_WORKING_TOKEN_GLOSSARY.tsv")
    base_dictionary = read_tsv(base_art / "WORKING_DICTIONARY_V43.tsv")

    check("decision deck fixed order", tuple(row["surface"] for row in deck) == TARGET_ORDER)
    check("accepted deck fixed order", tuple(row["surface"] for row in accepted) == TARGET_ORDER)
    check("decision dimensions", len(deck) == len(accepted) == len(family) == 101)
    deck_by_surface = {row["surface"]: row for row in deck}
    accepted_by_surface = {row["surface"]: row for row in accepted}
    for surface in TARGET_ORDER:
        spec = specs_by_surface[surface]
        check(f"deck mirrors CARD_SPECS {surface}", all(
            deck_by_surface[surface][target] == spec[source]
            for target, source in (
                ("working_default_de", "working_meaning_de"), ("composition", "composition"),
                ("strongest_rival_de", "strongest_rival_de"), ("family", "family"),
            )
        ))
        check(f"accepted mirrors CARD_SPECS {surface}", all(
            accepted_by_surface[surface][field] == spec[field]
            for field in ("working_meaning_de", "composition", "strongest_rival_de")
        ))
        check(f"deck count {surface}", int(deck_by_surface[surface]["occurrences"]) == EXPECTED_COUNTS[surface])
    check("architecture position total", sum(int(row["positions"]) for row in architecture) == 438)

    audit_counts = Counter(row["surface"] for row in audit)
    check("occurrence audit dimensions", len(audit) == len(reader) == 438)
    check("occurrence audit exact counts", dict(audit_counts) == EXPECTED_COUNTS, dict(audit_counts))
    check("occurrence IDs are G667", all(row["occurrence_id"].startswith("G667-") for row in audit))
    check("all target slots were V43-open", all(row["v43_gloss_de"] == f"[{row['surface']}:?]" for row in audit))
    check("all target slots are V44-filled", all(
        row["v44_gloss_de"] and not OPEN_MARKER.search(row["v44_gloss_de"]) for row in audit
    ))
    check("no substring dispatch", all(row["substring_dispatch"] == "0" for row in audit))
    check("audit practical prose has no generic work filler", not any(
        GENERIC.search(row["v44_working_translation_de"]) for row in audit
    ))
    check("target-line practical prose has no generic work filler", not any(
        GENERIC.search(row["v44_working_translation_de"]) for row in target_lines
    ))

    audit_by_id = {row["occurrence_id"]: row for row in audit}
    reader_by_id = {row["occurrence_id"]: row for row in reader}
    check("reader/audit occurrence IDs", set(reader_by_id) == set(audit_by_id))
    for occurrence_id, row in reader_by_id.items():
        source = cross_by_locus[row["locus"]]
        check(f"reader ZL3b {occurrence_id}", row["zl3b_line"] == source["zl3b_clean"])
        check(f"reader IT2a {occurrence_id}", row["it2a_line"] == source["it2a_clean"])
        check(f"reader RF1b {occurrence_id}", row["rf1b_line"] == source["rf1b_clean"])

    merge_rows = [row for row in audit if row["reader_merge_surface"] != "NONE"]
    check("only named context surfaces merge", all(row["surface"] in CONTEXT_SURFACES for row in merge_rows))
    check("label and one-token rows never merge", all(
        row["reader_merge_surface"] == "NONE"
        for row in audit if row["token_kind"] == "L" or row["position"] == "ONLY"
    ))
    check("non-context cards never reader-dispatch", all(
        row["reader_merge_direction"] == row["reader_merge_surface"] == "NONE"
        and row["context_or_reader_dispatch"] == "0"
        for row in audit if row["surface"] not in CONTEXT_SURFACES
    ))
    for row in audit:
        direction, merged = row["reader_merge_direction"], row["reader_merge_surface"]
        if merged == "NONE":
            check(f"no phantom merge direction {row['occurrence_id']}", direction == "NONE", direction)
            continue
        source_tokens = tuple(row["zl3b_line"].split())
        local_directions: set[str] = set()
        supporting_readers: set[str] = set()
        for reader_name, reader_line in (("IT2a", row["it2a_line"]), ("RF1b", row["rf1b_line"])):
            reader_directions = aligned_merge_evidence(
                source_tokens, tuple(reader_line.split()), int(row["ordinal"]) - 1, merged,
            )
            local_directions.update(reader_directions)
            if direction in reader_directions:
                supporting_readers.add(reader_name)
        check(f"merge direction {row['occurrence_id']}", direction in {"LEFT", "RIGHT", "BOTH"}, direction)
        check(f"merge spelling {row['occurrence_id']}", merged == merged_surface_for(row), merged)
        check(f"merge locally aligned {row['occurrence_id']}", direction in local_directions, sorted(local_directions))
        check(
            f"merge reader witnesses {row['occurrence_id']}",
            set(row["reader_merge_readers"].split("+")) == supporting_readers,
            row["reader_merge_readers"],
        )
        check(f"merge decision {row['occurrence_id']}", row["reader_merge_decision"] == "ACCEPT_LOCAL_MINIMUM_ALIGNMENT")
        prefix = row["surface"].upper()
        check(
            f"merge class explicit {row['occurrence_id']}",
            row["rendering_class"].startswith(f"{prefix}_READER_MERGE_{direction}_")
            and row["rendering_class"].endswith(("_KNOWN", "_NOVEL")),
            row["rendering_class"],
        )
    check("context-card merges cite reader boundary", all(
        row["surface"] not in CONTEXT_SURFACES or row["reader_merge_surface"] == "NONE"
        or "reader" in row["selection_rule"].lower()
        for row in context
    ))
    check("non-context decision label", all(
        row["reader_merge_decision"] == "NOT_A_CONTEXT_SHORT_FORM"
        for row in audit if row["surface"] not in CONTEXT_SURFACES
    ))
    check("label/only decision label", all(
        row["reader_merge_decision"] == "NO_MERGE_LABEL_OR_ONLY"
        for row in audit if row["surface"] in CONTEXT_SURFACES
        and (row["token_kind"] == "L" or row["position"] == "ONLY")
    ))
    check("eligible unmerged decision label", all(
        row["reader_merge_decision"] in {"REJECT_NONLOCAL_LINE_SET_ONLY", "NO_EXACT_LOCAL_READER_JOIN"}
        for row in audit if row["surface"] in CONTEXT_SURFACES
        and row["token_kind"] != "L" and row["position"] != "ONLY"
        and row["reader_merge_surface"] == "NONE"
    ))

    check("only named GDT667 boundary forms reader-dispatch", all(
        row["surface"] in CONTEXT_SURFACES for row in merge_rows
    ))

    check("stem-model artifact byte-equivalent to source", (ART / "STEM_MODEL_V44.tsv").read_bytes() == STEM_SPECS.read_bytes())
    stems_by_key = {(row["stem"], row["structural_role"]): row for row in stem_model}
    check("stem-model artifact 52 rows", len(stem_model) == len(stems_by_key) == 52)
    stem_roles = {row["structural_role"] for row in stem_model}
    card_atoms = {row["surface"]: row["composition"].split("+") for row in specs}
    check("composition syntax has only plus-delimited atoms", all(
        row["composition"] and ";" not in row["composition"] and " " not in row["composition"]
        and all(card_atoms[row["surface"]]) for row in specs
    ))
    check("every composition atom has a stem role or exact-whole namespace", all(
        atom in stem_roles or atom == f"LEARNED_{row['surface'].upper()}_WHOLE"
        for row in specs for atom in card_atoms[row["surface"]]
    ))
    learned_wholes = {
        row["surface"] for row in specs
        if card_atoms[row["surface"]] == [f"LEARNED_{row['surface'].upper()}_WHOLE"]
    }
    check("final synthesis is 94 role-composed plus 7 learned", len(learned_wholes) == 7
          and len(specs) - len(learned_wholes) == 94)
    check("learned wholes use a sole exact-surface namespace", all(
        atoms == [f"LEARNED_{surface.upper()}_WHOLE"]
        for surface, atoms in card_atoms.items() if any(atom.startswith("LEARNED_") for atom in atoms)
    ))

    def declared_spelling_count(row: dict[str, str]) -> int:
        atoms = card_atoms[row["surface"]]
        if row["surface"] in learned_wholes:
            return 1
        candidates = {""}
        for atom in atoms:
            if atom not in ATOM_SPELLINGS:
                return 0
            candidates = {prefix + spelling for prefix in candidates for spelling in ATOM_SPELLINGS[atom]}
        return int(row["surface"] in candidates)

    check("each declared composition reconstructs its exact surface once", all(
        declared_spelling_count(row) == 1 for row in specs
    ))

    terminal_s_actual = {surface for surface, atoms in card_atoms.items() if "S_TERM_SPECIES" in atoms}
    check("terminal-s role stays terminal", all(
        card_atoms[surface][-1] == "S_TERM_SPECIES" and surface.endswith("s")
        for surface in terminal_s_actual
    ))
    seed_actual = {surface for surface, atoms in card_atoms.items() if "S_SEED" in atoms}
    check("seed role never occupies the absolute terminal slot", all(
        card_atoms[surface][-1] != "S_SEED" for surface in seed_actual
    ))
    seed_internal_followers = {
        "E_MIDDLE", "EE_END", "EEE_LONG_OR_FINAL", "Y_START_OR_CLOSE", "DY_FINISHED",
        "AN_I", "AIN_II", "AIIN_III", "IN_FORM_II", "IIN_FORM_III", "IIIN_FORM_IV",
        "S_TERM_SPECIES",
    }
    check("internal seed has its own grade, charge, form or close marker", all(
        atoms.index("S_SEED") == 0
        or atoms[atoms.index("S_SEED") + 1] in seed_internal_followers
        for atoms in card_atoms.values() if "S_SEED" in atoms
    ))

    terminal_d_actual = {surface for surface, atoms in card_atoms.items() if "D_TERM_CLOSE" in atoms}
    check("terminal-d role stays terminal", all(
        card_atoms[surface][-1] == "D_TERM_CLOSE" and surface.endswith("d")
        for surface in terminal_d_actual
    ))
    check("dose-d stays nonterminal; any close-d stays terminal", all(
        atoms.index("D_MEASURE") < len(atoms) - 1
        and ("D_TERM_CLOSE" not in atoms or atoms[-1] == "D_TERM_CLOSE")
        for atoms in card_atoms.values() if "D_MEASURE" in atoms
    ))
    internal_d_followers = {
        "AN_I", "AIN_II", "AIIN_III", "AIR_FRACTION_II", "AIIR_FRACTION_III",
        "AR_FRACTION_I", "OR_PORTION", "AM_UNIT_I", "MANIPULUS_SIGLUM",
        "IN_FORM_II", "IIN_FORM_III", "IIIN_FORM_IV", "AL_RAW_I", "OL_MATERIAL",
        "L_WOOD", "R_ROOT", "CTH_HERB", "CHOR_PLANT_PART", "F_FLOWER", "P_POWDER",
    }
    check("noninitial dose-d precedes a quantity, material or form head", all(
        atoms.index("D_MEASURE") == 0
        or atoms[atoms.index("D_MEASURE") + 1] in internal_d_followers
        for atoms in card_atoms.values() if "D_MEASURE" in atoms
    ))

    qol_actual = {surface for surface, atoms in card_atoms.items() if "QOL_ADD" in atoms}
    check("qol stays a left-head without O/L double count", all(
        card_atoms[surface][0] == "QOL_ADD"
        and surface.startswith("qol")
        and not ({"O_PREP", "L_WOOD", "QOKOL_HEAT"} & set(card_atoms[surface]))
        for surface in qol_actual
    ))
    qokol_actual = {surface for surface, atoms in card_atoms.items() if "QOKOL_HEAT" in atoms}
    check("qokol remains a separate learned heat block", all(
        card_atoms[surface][0] == "QOKOL_HEAT" and surface.startswith("qokol")
        and "QOL_ADD" not in card_atoms[surface]
        for surface in qokol_actual
    ))
    oly_actual = {surface for surface, atoms in card_atoms.items() if "OLY_STRAIN_ACTION" in atoms}
    check("OLY predicts the terminal qoctholy straining block", oly_actual == {"qoctholy"}
          and card_atoms["qoctholy"] == ["QO_COMMAND", "CTH_HERB", "OLY_STRAIN_ACTION"]
          and specs_by_surface["qoctholy"]["working_meaning_de"] == "seihe den Krautdrogenstoff ab")

    y_reference_actual = {surface for surface, atoms in card_atoms.items() if "Y_REFERENCE" in atoms}
    check("Y-reference marks a visible y subboundary", all(
        surface.startswith("y") or "y" in surface[1:]
        for surface in y_reference_actual
    ))
    y_close_actual = {surface for surface, atoms in card_atoms.items() if "Y_START_OR_CLOSE" in atoms}
    check("close-Y stays terminal", all(
        card_atoms[surface][-1] == "Y_START_OR_CLOSE" and surface.endswith("y")
        for surface in y_close_actual
    ))
    iin_actual = {surface for surface, atoms in card_atoms.items() if "IIN_FORM_III" in atoms}
    check("form-III stays final", all(
        card_atoms[surface][-1] == "IIN_FORM_III" and surface.endswith("iin")
        for surface in iin_actual
    ))
    chor_actual = {surface for surface, atoms in card_atoms.items() if "CHOR_PLANT_PART" in atoms}
    check("chor plant-part atom reconstructs a visible chor block", all(
        "chor" in surface for surface in chor_actual
    ))

    check("portion wording requires OR or learned whole", all(
        "portion" not in row["working_meaning_de"].lower()
        or "OR_PORTION" in card_atoms[row["surface"]] or row["surface"] in learned_wholes
        for row in specs
    ))
    check("initial/internal s is seed", stems_by_key[("s-", "S_SEED")]["practical_default_de"] == "Saatgut"
          and "initial oder intern" in stems_by_key[("s-", "S_SEED")]["scope"])
    check("absolute terminal s is charge/species", stems_by_key[("-s", "S_TERM_SPECIES")]["practical_default_de"] == "Charge; Arzneispecies"
          and "absolut terminal" in stems_by_key[("-s", "S_TERM_SPECIES")]["scope"])
    check("initial d and terminal d stay distinct", stems_by_key[("d-", "D_MEASURE")]["practical_default_de"] == "abmessen; eine Dosis"
          and stems_by_key[("-d", "D_TERM_CLOSE")]["practical_default_de"] == "abschließen; abziehen")
    check("qol is learned add-command", stems_by_key[("qol", "QOL_ADD")]["practical_default_de"] == "Drogenstoff zugeben"
          and "nicht zugleich als q plus" in stems_by_key[("qol", "QOL_ADD")]["exclusions"])
    check("qokol is separate learned heat block", stems_by_key[("qokol", "QOKOL_HEAT")]["practical_default_de"] == "erhitzen"
          and "nicht als QOL_ADD" in stems_by_key[("qokol", "QOKOL_HEAT")]["exclusions"])
    check("terminal ol is material carrier", stems_by_key[("-ol", "OL_MATERIAL")]["practical_default_de"].startswith("Drogenstoff")
          and "nacktem ol" in stems_by_key[("-ol", "OL_MATERIAL")]["exclusions"])
    l_stems = [row for row in stem_model if row["stem"] == "l"]
    check("l keeps dual bound/free scope", len(l_stems) == 2
          and {row["structural_role"] for row in l_stems} == {"L_WOOD", "FREE_LIBRA_SIGLUM"}
          and any("gebunden" in row["scope"] for row in l_stems)
          and any("frei" in row["scope"] for row in l_stems))
    ol_stem = stems_by_key[("ol", "LEARNED_OL_BASE")]
    check("naked ol exception explicit", "Ganzwort" in ol_stem["scope"]
          and "O_PREP+L_WOOD" in ol_stem["exclusions"]
          and "oly/olyly" in ol_stem["exclusions"])
    sol_stem = stems_by_key[("sol", "SOL_SEED_PREP")]
    check("sol stem is seed preparation", "Saatgutansatz" in sol_stem["practical_default_de"]
          and "Salz" in sol_stem["exclusions"])
    oly_stem = stems_by_key[("oly", "OLY_STRAIN_ACTION")]
    check("oly stem is narrow learned straining block", oly_stem["practical_default_de"] == "abseihen"
          and set(oly_stem["examples"].split("|")) == {"oly", "loly", "chololy"}
          and all(surface in oly_stem["exclusions"] for surface in ("choly", "doly", "qoly", "ykoly")))
    m_stem = stems_by_key[("m", "MANIPULUS_SIGLUM")]
    check("m stem is free-only Handvoll", m_stem["practical_default_de"] == "eine Handvoll"
          and "freies Ganzwort" in m_stem["scope"] and "Substring" in m_stem["exclusions"])
    g_stem = stems_by_key[("g", "G_GRAIN_SIGLUM")]
    check("g stem restricted to exact four named cards", g_stem["practical_default_de"] == "ein Gran"
          and set(g_stem["examples"].split("|")) == GRAIN_SURFACES
          and "vier namentlich lizenzierten Karten" in g_stem["scope"]
          and "freies g" in g_stem["exclusions"]
          and card_atoms["cheg"] == ["CH_DRY", "E_MIDDLE", "G_GRAIN_SIGLUM"]
          and any(row["surface"] == "g" and row["working_meaning_de"] == "vorstehenden Rezeptposten abschließen"
                  for row in base_glossary))
    b_stem = stems_by_key[("b", "B_UNKNOWN")]
    check("b has no productive value", b_stem["practical_default_de"] == "kein produktiver Wert"
          and b_stem["examples"] == "oleeeb" and "nicht Stammwert" in b_stem["exclusions"])

    i_stem = stems_by_key[("i", "I_FORM_I")]
    check("i fills only the preparation Form-I ladder cell", i_stem["practical_default_de"] == "Zubereitungsform I"
          and card_atoms["oiees"] == ["O_PREP", "I_FORM_I", "EE_END", "S_TERM_SPECIES"]
          and raw_counts["oin"] == 7 and raw_counts["oiin"] == 26 and raw_counts["oiiin"] == 11)
    so_stem = stems_by_key[("so", "SO_SEED_PREP")]
    check("so is the recurrent seed-preparation head", so_stem["practical_default_de"] == "Saatgutzubereitung"
          and card_atoms["sotchdaiin"][0] == "SO_SEED_PREP"
          and card_atoms["shsodaiin"][1] == "SO_SEED_PREP"
          and all(raw_counts[surface] > 0 for surface in ("soaiin", "sodaiin", "sody", "soin", "soiin", "soiiin")))
    om_stem = stems_by_key[("om", "OM_HANDFUL_PREP")]
    check("om is a terminal handful-preparation block", om_stem["practical_default_de"] == "eine Handvoll Ansatz"
          and raw_counts["om"] == 20 and raw_counts["cthom"] == 5 and raw_counts["dom"] == 5
          and card_atoms["cholchom"][-1] == card_atoms["qokom"][-1] == "OM_HANDFUL_PREP"
          and "agairom" in om_stem["exclusions"])
    cph_stem = stems_by_key[("cph", "CPH_COMPOSITE")]
    check("cph is a composite-preparation material head", cph_stem["practical_default_de"].startswith("Arzneikompositum")
          and raw_counts["cphol"] == 11 and raw_counts["cphedy"] == 8 and raw_counts["chcphedy"] == 4
          and card_atoms["cphol"] == ["CPH_COMPOSITE", "OL_MATERIAL"]
          and "cfh=Blütenfraktion" in cph_stem["exclusions"])
    check("named flower cards stay inside the inherited flower role", all(
        "F_FLOWER" in card_atoms[surface] for surface in ("qopchcfhy", "folaiin", "olfar")
    ))
    check("seven difficult cards remain concrete learned wholes", learned_wholes == {
        "agairom", "dairydy", "okeeeykeey", "olkaycthy", "otydal", "ykeeb", "ytym",
    })

    check("O+L artifact byte-equivalent to source", (ART / "INHERITED_OL_RENDER_REVISIONS.tsv").read_bytes() == OL_SPECS.read_bytes())
    ol_spec_by_surface = {row["surface"]: row for row in ol_specs}
    revision_by_surface = {row["surface"]: row for row in ol_revisions}
    check("nineteen inherited O+L material forms", len(ol_revisions) == len(revision_by_surface) == 19)
    check("exact O+L revision set", set(revision_by_surface) == set(OL_REVISIONS), sorted(revision_by_surface))
    check("O+L revision count 256", sum(int(row["positions"]) for row in ol_revisions) == 256)
    for surface, expected_count in OL_REVISIONS.items():
        row = revision_by_surface[surface]
        check(f"O+L raw count {surface}", raw_counts[surface] == expected_count == int(row["positions"]), raw_counts[surface])
        check(f"O+L source row {surface}", row == ol_spec_by_surface[surface])
        check(f"O+L wood rendering {surface}", "Holz" in row["practical_meaning_de"], row["practical_meaning_de"])
        check(f"O+L composition {surface}", "O_PREP+L_WOOD" in row["composition"], row["composition"])
    check("ol/oly/olyly excluded from O+L revision", not (set(revision_by_surface) & OL_EXCEPTIONS))

    check("SOL artifact byte-equivalent to source", (ART / "INHERITED_SOL_RENDER_REVISIONS.tsv").read_bytes() == SOL_SPECS.read_bytes())
    sol_spec_by_surface = {row["surface"]: row for row in sol_specs}
    sol_revision_by_surface = {row["surface"]: row for row in sol_revisions}
    check("two inherited SOL forms", len(sol_revisions) == len(sol_revision_by_surface) == 2)
    check("exact SOL revision set", set(sol_revision_by_surface) == {"solaiin", "sols"})
    check("SOL revision count 4", sum(int(row["positions"]) for row in sol_revisions) == 4)
    for surface, expected_count in {"solaiin": 1, "sols": 3}.items():
        row = sol_revision_by_surface[surface]
        check(f"SOL raw count {surface}", raw_counts[surface] == expected_count == int(row["positions"]), raw_counts[surface])
        check(f"SOL source row {surface}", row == sol_spec_by_surface[surface])
        check(f"SOL seed rendering {surface}", "Saatgutansatz" in row["practical_meaning_de"]
              and "Salz" not in row["practical_meaning_de"])
        check(f"SOL seed composition {surface}", row["composition"].startswith("SOL_SEED_PREP"))
    base_gloss_by_surface = {row["surface"]: row for row in base_glossary}
    gloss_by_surface = {row["surface"]: row for row in glossary}
    check("V44 glossary adds exactly 101 targets", len(glossary) == len(base_glossary) + 101)
    check("all inherited structural glosses frozen", all(
        surface in gloss_by_surface
        and gloss_by_surface[surface]["working_meaning_de"] == row["working_meaning_de"]
        and gloss_by_surface[surface]["scope_state"] == row["scope_state"]
        for surface, row in base_gloss_by_surface.items()
    ))
    check("O+L practical meanings not exported as structural tags", all(
        gloss_by_surface[surface]["working_meaning_de"] != revision_by_surface[surface]["practical_meaning_de"]
        for surface in OL_REVISIONS
    ))
    check("ol/oly/olyly structural exceptions preserved", all(
        gloss_by_surface[surface]["working_meaning_de"] == base_gloss_by_surface[surface]["working_meaning_de"]
        for surface in OL_EXCEPTIONS
    ))

    check("frontier dimensions", len(frontier) == len(base_frontier) == 102)
    check("frontier loci preserved", [row["locus"] for row in frontier] == [row["locus"] for row in base_frontier])
    check("frontier surfaces preserved", [row["surface"] for row in frontier] == [row["unknown_surface"] for row in base_frontier])
    check("frontier completely closed", all(
        row["status"] == "COMPLETE_WITH_PROVISIONAL_CONCRETE_DEFAULT"
        and not OPEN_MARKER.search(row["v44_translation_de"])
        and not GENERIC.search(row["v44_translation_de"])
        for row in frontier
    ))
    expected_next_surfaces = {row["unknown_surface"] for row in new_one}
    check("next-frontier dimensions", len(new_one) == len(next_frontier) == 76
          and len(expected_next_surfaces) == 76)
    check("next-frontier exact surface set", {row["surface"] for row in next_frontier} == expected_next_surfaces)
    check("next-frontier full-panel counts", all(
        int(row["full_panel_positions"]) == raw_counts[row["surface"]]
        and int(row["newly_exposed_lines"])
        == sum(candidate["unknown_surface"] == row["surface"] for candidate in new_one)
        for row in next_frontier
    ))
    check("next-frontier ranked by full-panel count", [
        (int(row["full_panel_positions"]), row["surface"]) for row in next_frontier
    ] == sorted(
        ((int(row["full_panel_positions"]), row["surface"]) for row in next_frontier),
        key=lambda item: (-item[0], item[1]),
    ))

    base_by_locus = {row["locus"]: row for row in base_coverage}
    coverage_by_locus = {row["locus"]: row for row in coverage}
    check("coverage loci stable", set(base_by_locus) == set(coverage_by_locus) == set(by_line))
    manual_by_rank = {row["rank"]: row for row in manual}
    manual_spec_by_rank = {row["rank"]: row for row in manual_specs}
    complete_by_locus = {row["locus"]: row for row in complete}
    check("manual-passage artifact dimensions", len(manual) == len(manual_by_rank) == 25
          and sorted(int(rank) for rank in manual_by_rank) == list(range(1, 26)))
    for rank in map(str, range(1, 26)):
        row, spec = manual_by_rank[rank], manual_spec_by_rank[rank]
        check(f"manual source fields {rank}", all(row[field] == spec[field] for field in manual_fields))
        check(f"manual guarded line identity {rank}", row["locus"] in cross_by_locus
              and row["zl3b_line"] == cross_by_locus[row["locus"]]["zl3b_clean"])
        check(f"manual V44 complete {rank}", row["v44_unknown_tokens"] == "0"
              and row["locus"] in complete_by_locus)
        check(f"manual automatic renderer identity {rank}", row["automatic_v44_translation_de"]
              == complete_by_locus[row["locus"]]["working_translation_de"])
        check(f"manual and automatic channels distinct {rank}", "manual workshop prose versus deterministic V44 renderer" in row["comparison_scope"])
        check(f"manual prose concrete {rank}", not GENERIC.search(row["manual_workshop_translation_de"])
              and not OPEN_MARKER.search(row["manual_workshop_translation_de"])
              and not GENERIC.search(row["automatic_v44_translation_de"])
              and not OPEN_MARKER.search(row["automatic_v44_translation_de"]))
    non_target_before: list[tuple[str, int, str, str, str, str]] = []
    non_target_after: list[tuple[str, int, str, str, str, str]] = []
    for locus, base_row in base_by_locus.items():
        final_row = coverage_by_locus[locus]
        words = [row["eva"] for row in by_line[locus]]
        before_gloss, after_gloss = split_pipe(base_row["token_glosses_de"]), split_pipe(final_row["token_glosses_de"])
        before_source, after_source = split_pipe(base_row["gloss_sources"]), split_pipe(final_row["gloss_sources"])
        before_state, after_state = split_pipe(base_row["scope_states"]), split_pipe(final_row["scope_states"])
        check(f"coverage alignment {locus}", len(words) == len(before_gloss) == len(after_gloss))
        for index, surface in enumerate(words):
            if surface in TARGETS:
                continue
            non_target_before.append((locus, index + 1, surface, before_gloss[index], before_source[index], before_state[index]))
            non_target_after.append((locus, index + 1, surface, after_gloss[index], after_source[index], after_state[index]))
    check("non-target structural projection frozen", non_target_before == non_target_after)
    check("non-target position census", len(non_target_before) == 32339 - 438, len(non_target_before))

    base_metrics = coverage_metrics(base_coverage, base_one, base_complete, base_glossary)
    final_metrics = coverage_metrics(coverage, one, complete, glossary)
    check("coverage physical lines", final_metrics["physical_lines"] == base_metrics["physical_lines"] == 4128)
    check("known delta exactly 438", final_metrics["known_token_positions"] - base_metrics["known_token_positions"] == 438)
    check("unknown delta exactly 438", base_metrics["unknown_token_positions"] - final_metrics["unknown_token_positions"] == 438)
    check("new-complete artifact is actual set difference", {
        row["locus"] for row in new_complete
    } == {row["locus"] for row in complete} - {row["locus"] for row in base_complete})
    check("new-one-hole artifact is actual set difference", {
        row["locus"] for row in new_one
    } == {row["locus"] for row in one} - {row["locus"] for row in base_one})
    check("round versions", [row["version"] for row in rounds] == ["V43", "V44"])
    check("round base metrics", all(int(rounds[0][key]) == value for key, value in base_metrics.items()))
    check("round final metrics", all(int(rounds[1][key]) == value for key, value in final_metrics.items()))
    check("round dictionary dimensions", int(rounds[0]["dictionary_entries"]) == len(base_dictionary) and int(rounds[1]["dictionary_entries"]) == len(dictionary))
    check("complete practical prose has no generic filler", not any(
        GENERIC.search(row["working_translation_de"]) for row in complete
    ))
    check("complete practical prose has no open marker", not any(
        OPEN_MARKER.search(row["working_translation_de"]) for row in complete
    ))
    check("structural OL metatext absent from practical prose", not any(
        "Eigenschafts-/Zustands-/Materialträger" in row["working_translation_de"] for row in complete
    ))
    revised_complete = [row for row in complete if set(row["zl3b_line"].split()) & set(OL_REVISIONS)]
    check("completed O+L passages render wood", all("Holz" in row["working_translation_de"] for row in revised_complete))
    sol_complete = [
        row for row in complete
        if set(row["zl3b_line"].split()) & {"solaiin", "sols", "solor", "solkeedy"}
    ]
    check("completed SOL passages render seed not salt", all(
        "Saat" in row["working_translation_de"] and "Salz" not in row["working_translation_de"]
        for row in sol_complete
    ))
    for exception in ("oly", "olyly"):
        exception_rows = [row for row in complete if exception in row["zl3b_line"].split()]
        check(f"{exception} keeps straining action", all(
            "seih" in row["working_translation_de"].lower()
            or (exception == "oly" and "L_READER_MERGE_RIGHT:loly" in row["gloss_sources"])
            for row in exception_rows
        ))
    qoctholy_rows = [row for row in complete if "qoctholy" in row["zl3b_line"].split()]
    check("qoctholy renders the predicted straining action", bool(qoctholy_rows)
          and all("seih" in row["working_translation_de"].lower() for row in qoctholy_rows))

    check("result schema", result["schema"] == "GDT667_ONE_HUNDRED_ONE_RESIDUAL_FAMILY_COMPLETION_RESULT_V1")
    check("result status", result["status"] == "PASS_438_TARGET_POSITIONS__V44_CONCRETE_RECIPE_REGISTER")
    check("result target dimensions", result["targets"]["surface_types"] == 101 and result["targets"]["positions"] == 438)
    check("result target counts", result["targets"]["surface_counts"] == EXPECTED_COUNTS)
    check("result frontier dimensions", result["frontier"]["source_rows"] == result["frontier"]["completed_rows"] == 102
          and result["frontier"]["next_rows"] == result["frontier"]["next_unique_surfaces"] == 76
          and result["frontier"]["unfilled_target_slots"] == 0)
    check("result next-frontier leaders", result["frontier"]["next_leaders"] == [
        {"surface": row["surface"], "full_panel_positions": int(row["full_panel_positions"])}
        for row in next_frontier[:10]
    ])
    check("result guard", result["guard"]["f84"] == result["guard"]["f84r"] == "FORBIDDEN")
    check("result excludes f1r", result["guard"]["f1r"] == "EXCLUDED_BY_EXACT_ALLOWLIST")
    check("result no new pages/images", result["guard"]["new_pages"] == result["guard"]["new_images"] == 0)
    check("result base coverage metrics", result["coverage"]["base"] == base_metrics)
    check("result final coverage metrics", result["coverage"]["final"] == final_metrics)
    check("result non-target census", result["coverage"]["non_target_token_positions_unchanged"] == len(non_target_before))
    check("result dictionary dimensions", result["working_dictionary"]["v43_entries"] == len(base_dictionary) and result["working_dictionary"]["v44_entries"] == len(dictionary))
    check("result glossary dimensions", result["working_dictionary"]["v43_glossary_surfaces"] == len(base_glossary) and result["working_dictionary"]["v44_glossary_surfaces"] == len(glossary))
    contextual_rows = [row for row in audit if row["surface"] in CONTEXT_SURFACES]
    contextual_counts = Counter(row["surface"] for row in contextual_rows)
    contextual_merge_counts = Counter(
        f"{row['surface']}:{row['reader_merge_direction']}:{row['reader_merge_surface']}"
        if row["reader_merge_surface"] != "NONE" else f"{row['surface']}:FREE_NO_ADJACENT_MERGE"
        for row in contextual_rows if row["token_kind"] != "L" and row["position"] != "ONLY"
    )
    result_context = result["context_short_forms"]
    check("result context position census", result_context["positions"] == len(contextual_rows))
    check("result context surface counts", result_context["surface_counts"] == dict(sorted(contextual_counts.items())))
    check("result context merge count", result_context["merge_positions"] == len(merge_rows))
    check("result raw line-set count", result_context["raw_line_set_candidate_positions"] == sum(
        row["raw_line_set_candidates"] != "NONE" for row in contextual_rows
    ))
    check("result rejected nonlocal count", result_context["rejected_nonlocal_line_set_positions"] == sum(
        row["reader_merge_decision"] == "REJECT_NONLOCAL_LINE_SET_ONLY" for row in contextual_rows
    ))
    check("result context merge classes", result_context["merge_classes"] == dict(sorted(contextual_merge_counts.items())))
    check("result inherited O+L dimensions", result["inherited_ol_revision"]["surface_types"] == 19
          and result["inherited_ol_revision"]["positions"] == 256
          and result["inherited_ol_revision"]["composition"] == "O_PREP+L_WOOD"
          and result["inherited_ol_revision"]["naked_ol_remains_exact_whole"] is True
          and result["inherited_ol_revision"]["oly_and_olyly_remain_actions"] is True)
    check("result inherited SOL role", result["inherited_sol_revision"]["composition"] == "SOL_SEED_PREP"
          and result["inherited_sol_revision"]["surface_types"] == 2
          and result["inherited_sol_revision"]["positions"] == 4)
    check("result stem-model dimensions", result["stem_model"]["rows"] == 52
          and result["stem_model"]["structural_roles_distinct_from_german_defaults"] is True)
    check("result card-synthesis dimensions", result["card_synthesis"]["productive_compositions"] == 94
          and result["card_synthesis"]["learned_exact_wholes"] == 7
          and result["card_synthesis"]["learned_exact_surfaces"] == sorted(learned_wholes)
          and result["card_synthesis"]["inherited_stem_roles_reused"] == 48
          and result["card_synthesis"]["total_stem_roles"] == 52
          and result["card_synthesis"]["new_stem_roles"] == 4
          and result["card_synthesis"]["new_stem_role"] == "I_FORM_I|SO_SEED_PREP|OM_HANDFUL_PREP|CPH_COMPOSITE"
          and result["card_synthesis"]["candidate_lenses"]
          == ["stem_compositor", "recipe_master", "passage_reader"])
    check("result manual-passage dimensions", result["manual_passages"]["rows"] == 25
          and result["manual_passages"]["source_lines_exact"] is True
          and result["manual_passages"]["v44_complete_rows"] == 25
          and result["manual_passages"]["manual_and_automatic_kept_distinct"] is True)
    check("result output hash set", set(result["outputs"]) == {str(BASE / "artifacts" / name) for name in OUTPUT_NAMES})
    result_core = {key: value for key, value in result.items() if key != "content_sha256"}
    check("result canonical content hash", result["content_sha256"] == canonical_hash(result_core))
    for relative, expected in result["inputs"].items():
        check(f"input hash {relative}", sha256(ROOT / relative) == expected)
    check("CARD_SPECS sealed as input", str(BASE / "src/CARD_SPECS.tsv") in result["inputs"])
    check("O+L specs sealed as input", str(BASE / "src/INHERITED_OL_REVISION_SPECS.tsv") in result["inputs"])
    check("SOL specs sealed as input", str(BASE / "src/INHERITED_SOL_REVISION_SPECS.tsv") in result["inputs"])
    check("stem-model specs sealed as input", str(BASE / "src/STEM_MODEL_SPECS.tsv") in result["inputs"])
    check("manual-passage specs sealed as input", str(BASE / "src/MANUAL_PASSAGE_SPECS.tsv") in result["inputs"])
    check("all independent candidate sources sealed as inputs", all(
        str(path.relative_to(ROOT)) in result["inputs"] for path in CANDIDATE_SPECS
    ))
    for relative, expected in result["outputs"].items():
        check(f"output hash {relative}", sha256(ROOT / relative) == expected)

    with tempfile.TemporaryDirectory(prefix="gdt667_validator_replay_") as directory:
        replay = Path(directory)
        completed_process = subprocess.run(
            [sys.executable, str(RUN), "--artifact-dir", str(replay)],
            cwd=ROOT, text=True, capture_output=True,
        )
        check("builder tempdir replay exits zero", completed_process.returncode == 0, completed_process.stderr[-1200:])
        if completed_process.returncode == 0:
            for name in (*OUTPUT_NAMES, "RESULT.json"):
                check(f"byte replay {name}", (ART / name).read_bytes() == (replay / name).read_bytes())

    local_unix = "/" + "home/"
    local_macos = "/" + "Users/"
    forbidden_text = re.compile(
        re.escape(local_unix) + "|" + re.escape(local_macos)
        + r"|BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY|AKIA[0-9A-Z]{16}"
    )
    privacy_files = [RUN, Path(__file__), CARD_SPECS, OL_SPECS, SOL_SPECS, STEM_SPECS, MANUAL_SPECS, *CANDIDATE_SPECS] + [
        ART / name for name in (*OUTPUT_NAMES, "RESULT.json")
    ]
    check("artifact/source privacy scan", not any(
        forbidden_text.search(path.read_text(encoding="utf-8", errors="replace")) for path in privacy_files
    ))

    failures = [row for row in checks if not row["pass"]]
    validation = {
        "schema": "GDT667_VALIDATION_V1", "experiment_id": "GDT667",
        "status": "PASS" if not failures else "FAIL", "checks_total": len(checks),
        "checks_passed": len(checks) - len(failures), "failures": failures,
        "guarded_token_stats": token_stats, "guarded_cross_stats": cross_stats,
        "dynamic_base_metrics": base_metrics, "dynamic_final_metrics": final_metrics,
        "checks": checks,
    }
    (ART / "VALIDATION.json").write_text(
        json.dumps(validation, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"GDT667 validation: {validation['status']} {validation['checks_passed']}/{validation['checks_total']}")
    if failures:
        for row in failures[:30]:
            print(f"FAIL {row['name']}: {row['detail']}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
