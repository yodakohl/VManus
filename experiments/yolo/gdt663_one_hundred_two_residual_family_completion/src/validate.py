#!/usr/bin/env python3
"""Independent source-first release validator for GDT663."""
from __future__ import annotations

import csv
import hashlib
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
BASE = Path("experiments/yolo/gdt663_one_hundred_two_residual_family_completion")
ART = ROOT / BASE / "artifacts"
RUN = ROOT / BASE / "src/run.py"
G662 = Path("experiments/yolo/gdt662_seventy_six_residual_family_completion")
TOKENS = Path("transcription/voynich_zl3b_tokens.tsv")
CROSS = Path("transcription/voynich_cross_transcription_lines.tsv")

OUTPUT_NAMES = (
    "PAGE_ALLOWLIST.tsv", "TARGET_DECISION_DECK.tsv", "ACCEPTED_WHOLE_SURFACE_DEFAULTS.tsv",
    "CONTEXT_RENDERING_CARDS.tsv", "CARD_ARCHITECTURE_SUMMARY.tsv",
    "ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv", "READER_VARIANT_AUDIT.tsv",
    "FAMILY_COMPOSITION_ATLAS.tsv", "FRONTIER_102_COMPLETIONS.tsv",
    "TARGET_LINE_TRANSLATIONS.tsv", "ROUND_COVERAGE_COUNTS.tsv",
    "NEWLY_COMPLETED_LINES.tsv", "NEWLY_EXPOSED_ONE_HOLE_LINES.tsv",
    "V40_WORKING_TOKEN_GLOSSARY.tsv", "WORKING_DICTIONARY_V40.tsv",
    "ALL_LINE_CONCRETE_COVERAGE_V40.tsv", "COMPLETE_PASSAGES_V40.tsv",
    "ONE_UNKNOWN_PASSAGES_V40.tsv",
)

TARGET_ORDER = tuple("""
okeeshy chokaiin lkain kalol okarol qokeeody alkal olkeeo arolkeey chdar sholkeedy chedar
teedar qotoiin qokchd ykoly choross sokchy qokchol odchaiin fshor ylg cthoj choly lo dchor
dosg cthory shosaiin ytchy tcho ckhor sols solaiin shody ksheo akaiin ched schesy chyky
shoqoky shocho ckhal sholoiin yckhodaiin keeody lchdal talody char chedyqokam oltedy sheety
keed olkol olyly ldy okeshey okeolor rory chedaiin qoraiin dary shee ykal dchokol okeshy
ytaiin saral cholchey yshealdy chkain rolchey qor qokechey deeeese olkaiin ary tolkain qotl
l ychedy olshey qoly taldain chetyry okair oraiiin olaiin salchtedytar qoteytyqoky sholdy
lkedy qotaldy oychey olain opchey odain ochedy oldal chody ckheody cthosg
""".split())
TARGETS = frozenset(TARGET_ORDER)


def parse_counts(raw: str) -> dict[str, int]:
    return {item.split("=", 1)[0]: int(item.split("=", 1)[1]) for item in raw.split()}


EXPECTED_COUNTS = parse_counts("""
okeeshy=2 chokaiin=15 lkain=33 kalol=2 okarol=2 qokeeody=13 alkal=1 olkeeo=4 arolkeey=1
chdar=17 sholkeedy=2 chedar=31 teedar=3 qotoiin=2 qokchd=6 ykoly=1 choross=1 sokchy=1
qokchol=15 odchaiin=1 fshor=1 ylg=1 cthoj=1 choly=12 lo=20 dchor=23 dosg=1 cthory=2
shosaiin=4 ytchy=14 tcho=8 ckhor=8 sols=3 solaiin=1 shody=46 ksheo=5 akaiin=2 ched=17
schesy=1 chyky=4 shoqoky=1 shocho=1 ckhal=3 sholoiin=1 yckhodaiin=1 keeody=8 lchdal=2
talody=1 char=75 chedyqokam=1 oltedy=6 sheety=7 keed=2 olkol=3 olyly=1 ldy=24
okeshey=1 okeolor=1 rory=1 chedaiin=32 qoraiin=1 dary=19 shee=11 ykal=9 dchokol=1
okeshy=2 ytaiin=39 saral=3 cholchey=2 yshealdy=1 chkain=12 rolchey=1 qor=21
qokechey=1 deeeese=1 olkaiin=28 ary=15 tolkain=2 qotl=2 l=163 ychedy=11 olshey=13
qoly=7 taldain=1 chetyry=1 okair=18 oraiiin=1 olaiin=39 salchtedytar=1 qoteytyqoky=1
sholdy=6 lkedy=26 qotaldy=1 oychey=1 olain=11 opchey=26 odain=14 ochedy=8 oldal=2
chody=78 ckheody=5 cthosg=1
""")

EXPECTED_KEY_MEANINGS = {
    "alkal": "Laugensalz / Alkali",
    "solaiin": "Salz, Menge III",
    "l": "Pfund / Gewichtseinheit",
    "ylg": "in ein Holzgefäß geben",
    "dosg": "eine Dosis Rückstand",
    "cthosg": "Krautrückstand",
    "deeeese": "lange bis zur letzten Stufe ruhen lassen",
    "qor": "nimm eine Drogenportion",
    "shee": "vollständig anfeuchten",
    "qoly": "gib Vorstehendes hinzu und schließe die Zugabe ab",
    "olyly": "seihe ein zweites Mal ab",
}
GENERIC = re.compile(
    r"arbeitsgut|arbeitsvorgang|arbeitschritt|arbeitsschritt|arbeitsmittel|arbeitsstoff|"
    r"vorgang ausführen|gut bearbeiten|eigenschafts-/zustands-/materialträger",
    re.I,
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def guarded_query(path: Path, pages: set[str], columns: str) -> tuple[list[dict[str, str]], dict[str, int]]:
    command = [str(ROOT / "vmanus-exp"), "query-tsv", str(path), "--selector", "page"]
    for page in sorted(pages):
        command.extend(("--allow", page))
    command.extend(("--columns", columns, "--forbid-prefix", "f84", "--forbid-prefix", "f84r"))
    completed = subprocess.run(command, cwd=ROOT, check=True, text=True, capture_output=True)
    rows = list(csv.DictReader(io.StringIO(completed.stdout), delimiter="\t"))
    stats_lines = [line for line in completed.stderr.splitlines() if line.startswith("GUARD_STATS ")]
    if len(stats_lines) != 1:
        raise RuntimeError("guarded query did not emit exactly one statistics line")
    stats = json.loads(stats_lines[0].removeprefix("GUARD_STATS "))
    return rows, {key: int(value) for key, value in stats.items()}


def main() -> int:
    checks: list[dict[str, object]] = []

    def check(name: str, condition: bool, detail: object = "") -> None:
        checks.append({"name": name, "pass": bool(condition), "detail": detail})

    result = json.loads((ART / "RESULT.json").read_text(encoding="utf-8"))
    base_pages = {row["page"] for row in read_tsv(ROOT / G662 / "artifacts/PAGE_ALLOWLIST.tsv")}
    pages = {row["page"] for row in read_tsv(ART / "PAGE_ALLOWLIST.tsv")}
    check("exact inherited page allowlist", pages == base_pages and len(pages) == 179)
    check("f1r excluded", "f1r" not in pages)
    check("sealed f84 family absent", not any(page.startswith("f84") for page in pages))

    tokens, token_stats = guarded_query(
        TOKENS, pages, "page,locus,token_index,eva,kind,section,language,hand"
    )
    cross, cross_stats = guarded_query(
        CROSS, pages, "page,locus,all_three_present,all_present_exact,zl3b_clean,it2a_clean,rf1b_clean"
    )
    check("guarded token census", len(tokens) == 32339 and token_stats["selected"] == 32339, token_stats)
    check("guarded cross census", len(cross) == 4137 and cross_stats["selected"] == 4137, cross_stats)
    check("token guard rejected sealed rows", token_stats["skipped_forbidden"] > 0, token_stats)
    check("cross guard rejected sealed rows", cross_stats["skipped_forbidden"] > 0, cross_stats)
    raw_counts = Counter(row["eva"] for row in tokens)
    for surface in TARGET_ORDER:
        check(f"raw count {surface}", raw_counts[surface] == EXPECTED_COUNTS[surface], raw_counts[surface])
    check("target count sum", sum(EXPECTED_COUNTS.values()) == 1105)

    deck = read_tsv(ART / "TARGET_DECISION_DECK.tsv")
    accepted = read_tsv(ART / "ACCEPTED_WHOLE_SURFACE_DEFAULTS.tsv")
    context = read_tsv(ART / "CONTEXT_RENDERING_CARDS.tsv")
    architecture = read_tsv(ART / "CARD_ARCHITECTURE_SUMMARY.tsv")
    audit = read_tsv(ART / "ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv")
    reader = read_tsv(ART / "READER_VARIANT_AUDIT.tsv")
    frontier = read_tsv(ART / "FRONTIER_102_COMPLETIONS.tsv")
    target_lines = read_tsv(ART / "TARGET_LINE_TRANSLATIONS.tsv")
    rounds = read_tsv(ART / "ROUND_COVERAGE_COUNTS.tsv")
    glossary = read_tsv(ART / "V40_WORKING_TOKEN_GLOSSARY.tsv")
    dictionary = read_tsv(ART / "WORKING_DICTIONARY_V40.tsv")
    coverage = read_tsv(ART / "ALL_LINE_CONCRETE_COVERAGE_V40.tsv")
    complete = read_tsv(ART / "COMPLETE_PASSAGES_V40.tsv")
    one = read_tsv(ART / "ONE_UNKNOWN_PASSAGES_V40.tsv")
    new_complete = read_tsv(ART / "NEWLY_COMPLETED_LINES.tsv")
    new_one = read_tsv(ART / "NEWLY_EXPOSED_ONE_HOLE_LINES.tsv")
    base_frontier = read_tsv(ROOT / G662 / "artifacts/NEWLY_EXPOSED_ONE_HOLE_LINES.tsv")
    base_coverage = read_tsv(ROOT / G662 / "artifacts/ALL_LINE_CONCRETE_COVERAGE_V39.tsv")
    base_glossary = read_tsv(ROOT / G662 / "artifacts/V39_WORKING_TOKEN_GLOSSARY.tsv")

    check("decision deck order", tuple(row["surface"] for row in deck) == TARGET_ORDER)
    check("accepted deck order", tuple(row["surface"] for row in accepted) == TARGET_ORDER)
    check("decision dimensions", len(deck) == len(accepted) == 102)
    check("audit dimensions", len(audit) == len(reader) == 1105)
    check("frontier dimensions", len(frontier) == len(base_frontier) == 105)
    check("target-line affected census", len(target_lines) == 949)
    check("context-card census", len(context) == 89)
    check("architecture position total", sum(int(row["positions"]) for row in architecture) == 1105)
    check("glossary dimension", len(glossary) == 734)
    check("dictionary dimension", len(dictionary) == 976)
    check("coverage physical lines", len(coverage) == 4128)
    check("complete line census", len(complete) == 449)
    check("new complete census", len(new_complete) == 118)
    check("one-hole census", len(one) == 333)
    check("new one-hole census", len(new_one) == 146)
    check("round versions", [row["version"] for row in rounds] == ["V39", "V40"])

    deck_by_surface = {row["surface"]: row for row in deck}
    for surface, meaning in EXPECTED_KEY_MEANINGS.items():
        check(f"key meaning {surface}", deck_by_surface[surface]["working_default_de"] == meaning)
    check("all deck entries concrete", all(row["working_default_de"] and "?" not in row["working_default_de"] for row in deck))
    check("all deck entries retain rival", all(row["strongest_rival_de"] for row in deck))
    check("all deck entries retain composition", all(row["composition"] for row in deck))
    check("no generic filler in deck", not any(GENERIC.search(row["working_default_de"]) for row in deck))

    audit_counts = Counter(row["surface"] for row in audit)
    check("audit surface counts", dict(audit_counts) == EXPECTED_COUNTS)
    check("all audit slots were open", all(row["v39_gloss_de"] == f"[{row['surface']}:?]" for row in audit))
    check("all audit slots now filled", all(row["v40_gloss_de"] and "?" not in row["v40_gloss_de"] for row in audit))
    check("no substring dispatch", all(row["substring_dispatch"] == "0" for row in audit))
    check("practical audit has no generic filler", not any(GENERIC.search(row["v40_working_translation_de"]) for row in audit))
    check("all target translations have no generic filler", not any(GENERIC.search(row["v40_working_translation_de"]) for row in target_lines))

    l_rows = [row for row in audit if row["surface"] == "l"]
    l_reader = [row for row in reader if row["surface"] == "l"]
    check("l occurrence census", len(l_rows) == len(l_reader) == 163)
    check("l exact-reader census", sum(int(row["reader_exact"]) for row in l_rows) == 38)
    check("l label census", sum(row["token_kind"] == "L" for row in l_rows) == 4)
    merge_rows = [row for row in l_rows if row["reader_merge_surface"] != "NONE"]
    check("l attested adjacent-merge census", len(merge_rows) == 105)
    for row in merge_rows:
        alternate = set(row["it2a_line"].split()) | set(row["rf1b_line"].split())
        check(
            f"l merge attested {row['occurrence_id']}",
            row["reader_merge_surface"] in alternate,
            row["reader_merge_surface"],
        )
    check("o|l to ol merge count", sum(row["reader_merge_surface"] == "ol" for row in l_rows) == 15)
    check("qo|l to qol merge count", sum(row["reader_merge_surface"] == "qol" for row in l_rows) == 3)
    check("free l fallback is explicit weight", all(
        row["working_render_de"] == "ein Pfund"
        for row in l_rows if row["rendering_class"] == "L_FREE_WEIGHT_SIGLUM"
    ))

    cross_by_locus = {row["locus"]: row for row in cross}
    for row in reader:
        source = cross_by_locus[row["locus"]]
        check(f"reader ZL3b {row['occurrence_id']}", row["zl3b_line"] == source["zl3b_clean"])
        check(f"reader IT2a {row['occurrence_id']}", row["it2a_line"] == source["it2a_clean"])
        check(f"reader RF1b {row['occurrence_id']}", row["rf1b_line"] == source["rf1b_clean"])

    check("frontier loci preserved", [row["locus"] for row in frontier] == [row["locus"] for row in base_frontier])
    check("frontier surfaces preserved", [row["surface"] for row in frontier] == [row["unknown_surface"] for row in base_frontier])
    check("frontier fully closed", all(row["status"] == "COMPLETE_WITH_PROVISIONAL_CONCRETE_DEFAULT" for row in frontier))
    check("frontier translations no holes", not any("[" + row["surface"] + ":?]" in row["v40_translation_de"] for row in frontier))
    check("frontier translations no generic filler", not any(GENERIC.search(row["v40_translation_de"]) for row in frontier))
    check("container rendering visible", any("Holzgefäß" in row["v40_translation_de"] for row in frontier))
    check("pound rendering visible", any("ein Pfund" in row["v40_translation_de"] for row in frontier))
    check("salt rendering visible", any("Salz" in row["v40_translation_de"] for row in frontier))
    check("residue rendering visible", any("Rückstand" in row["v40_translation_de"] for row in frontier))
    check("rest rendering visible", any("ruhen" in row["v40_translation_de"] for row in frontier))

    base_by_locus = {row["locus"]: row for row in base_coverage}
    coverage_by_locus = {row["locus"]: row for row in coverage}
    check("coverage loci stable", set(base_by_locus) == set(coverage_by_locus))
    non_target_before: list[tuple[str, int, str, str, str, str]] = []
    non_target_after: list[tuple[str, int, str, str, str, str]] = []
    for locus, base_row in base_by_locus.items():
        final_row = coverage_by_locus[locus]
        words = base_row["zl3b_line"].split()
        before_gloss = base_row["token_glosses_de"].split(" | ")
        after_gloss = final_row["token_glosses_de"].split(" | ")
        before_source = base_row["gloss_sources"].split(" | ")
        after_source = final_row["gloss_sources"].split(" | ")
        before_state = base_row["scope_states"].split(" | ")
        after_state = final_row["scope_states"].split(" | ")
        check(f"coverage alignment {locus}", len(words) == len(before_gloss) == len(after_gloss))
        for index, surface in enumerate(words):
            if surface in TARGETS:
                continue
            non_target_before.append((locus, index + 1, surface, before_gloss[index], before_source[index], before_state[index]))
            non_target_after.append((locus, index + 1, surface, after_gloss[index], after_source[index], after_state[index]))
    check("non-target projection frozen", non_target_before == non_target_after and len(non_target_before) == 31234)
    check("known arithmetic", sum(int(row["known_tokens"]) for row in coverage) == 20417)
    check("unknown arithmetic", sum(int(row["unknown_tokens"]) for row in coverage) == 11922)
    check("known delta exactly 1105", 20417 - 19312 == 1105)
    check("unknown delta exactly 1105", 13027 - 11922 == 1105)
    check("strict complete census", sum(int(row["strict_complete"]) for row in complete) == 147)
    check("strict one-hole census", sum(int(row["strict_eligible"]) for row in one) == 80)

    base_gloss_by_surface = {row["surface"]: row for row in base_glossary}
    gloss_by_surface = {row["surface"]: row for row in glossary}
    check("base glossary meanings frozen", all(
        gloss_by_surface[surface]["working_meaning_de"] == row["working_meaning_de"]
        for surface, row in base_gloss_by_surface.items()
    ))
    check("structural ol glossary preserved", gloss_by_surface["ol"]["working_meaning_de"] == base_gloss_by_surface["ol"]["working_meaning_de"])
    check("practical translations remove ol meta-text", not any(
        "Eigenschafts-/Zustands-/Materialträger" in row["working_translation_de"] for row in complete
    ))

    check("result status", result["status"] == "PASS_1105_TARGET_POSITIONS__V40_CONCRETE_RECIPE_REGISTER")
    check("result target dimensions", result["targets"]["surface_types"] == 102 and result["targets"]["positions"] == 1105)
    check("result free-l dimensions", result["free_l"]["positions"] == 163 and result["free_l"]["reader_exact_positions"] == 38)
    check("result frontier dimensions", result["frontier"]["source_rows"] == result["frontier"]["completed_rows"] == 105)
    check("result guard", result["guard"]["f84"] == result["guard"]["f84r"] == "FORBIDDEN")
    check("result no new pages/images", result["guard"]["new_pages"] == result["guard"]["new_images"] == 0)
    check("result output hash set", set(result["outputs"]) == {str(BASE / "artifacts" / name) for name in OUTPUT_NAMES})
    for relative, expected in result["inputs"].items():
        check(f"input hash {relative}", sha256(ROOT / relative) == expected)
    for relative, expected in result["outputs"].items():
        check(f"output hash {relative}", sha256(ROOT / relative) == expected)

    with tempfile.TemporaryDirectory(prefix="gdt663_validator_replay_") as directory:
        replay = Path(directory)
        completed_process = subprocess.run(
            [sys.executable, str(RUN), "--artifact-dir", str(replay)],
            cwd=ROOT, text=True, capture_output=True,
        )
        check("builder tempdir replay exits zero", completed_process.returncode == 0, completed_process.stderr[-1000:])
        for name in (*OUTPUT_NAMES, "RESULT.json"):
            check(f"byte replay {name}", (ART / name).read_bytes() == (replay / name).read_bytes())

    local_unix = "/" + "home/"
    local_macos = "/" + "Users/"
    forbidden_text = re.compile(
        re.escape(local_unix) + "|" + re.escape(local_macos)
        + r"|BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY|AKIA[0-9A-Z]{16}"
    )
    privacy_files = [ROOT / BASE / "src/run.py", ROOT / BASE / "src/validate.py"] + [ART / name for name in (*OUTPUT_NAMES, "RESULT.json")]
    check("artifact/source privacy scan", not any(
        forbidden_text.search(path.read_text(encoding="utf-8", errors="replace")) for path in privacy_files
    ))

    failures = [row for row in checks if not row["pass"]]
    validation = {
        "schema": "GDT663_VALIDATION_V1", "experiment_id": "GDT663",
        "status": "PASS" if not failures else "FAIL", "checks_total": len(checks),
        "checks_passed": len(checks) - len(failures), "failures": failures,
        "guarded_token_stats": token_stats, "guarded_cross_stats": cross_stats,
        "checks": checks,
    }
    (ART / "VALIDATION.json").write_text(
        json.dumps(validation, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"GDT663 validation: {validation['status']} {validation['checks_passed']}/{validation['checks_total']}")
    if failures:
        for row in failures[:20]:
            print(f"FAIL {row['name']}: {row['detail']}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
