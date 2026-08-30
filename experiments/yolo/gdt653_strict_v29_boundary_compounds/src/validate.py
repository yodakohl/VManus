#!/usr/bin/env python3
"""Independent release validator for GDT653."""
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
BASE = Path("experiments/yolo/gdt653_strict_v29_boundary_compounds")
ART = ROOT / BASE / "artifacts"
RUN = ROOT / BASE / "src/run.py"
MANIFEST = ROOT / BASE / "experiment.json"
REPORT = ROOT / BASE / "REPORT.md"
VALIDATION = ART / "VALIDATION.json"

G652 = Path("experiments/yolo/gdt652_strict_v28_frontier_completion")
G652_ALLOW = G652 / "artifacts/PAGE_ALLOWLIST.tsv"
G652_COVERAGE = G652 / "artifacts/ALL_LINE_CONCRETE_COVERAGE_V29.tsv"
G652_COMPLETE = G652 / "artifacts/COMPLETE_PASSAGES_V29.tsv"
G652_ONE = G652 / "artifacts/ONE_UNKNOWN_PASSAGES_V29.tsv"
G652_GLOSSARY = G652 / "artifacts/V29_EXACT_TOKEN_GLOSSARY.tsv"
G652_DICTIONARY = G652 / "artifacts/WORKING_DICTIONARY_V29.tsv"
TOKENS = Path("transcription/voynich_zl3b_tokens.tsv")
CROSS = Path("transcription/voynich_cross_transcription_lines.tsv")

STATUS = "PASS_6_STRICT_BOUNDARY_COMPOUNDS__V30"
# counts, source, family, tier, meaning, composition, rival
TARGETS = {
    "orol": ((10, 8, 9, 9), "f80v.44", "OR_OL_FUSION_FAMILY",
             "STRONG_DIRECT_BOUNDARY_COMPOUND", "Drogenstoffportion",
             "OR_PORTION+OL_MATERIAL", "Wurzelzubereitung"),
    "chckhal": ((4, 4, 4, 4), "f83r.39", "CKH_AL_FORM_FAMILY",
                "STRONG_LEARNED_HEAD_COMPOUND",
                "trockenes Arzneikompositum, Rohstoffform I",
                "ch+CKH_LEARNED+AL_BOUND", "trockenes Arzneikompositum, Charge I"),
    "octhdy": ((2, 2, 2, 2), "f114r.13", "O_PREP_CTH_RESULT_FAMILY",
               "STRONG_LOW_N_RESULT_COMPOUND",
               "fertig aufbereitete Drogenzubereitung, Grundform",
               "O_PREP+CTH_LEARNED+d+y", "CTH-Ansatz am Gradanfang, abgeschlossen"),
    "chdaly": ((3, 3, 3, 3), "f112v.16", "DAL_LEARNED_MATERIA_FAMILY",
               "PROVISIONAL_DAL_HEAD_COMPOUND",
               "trockener Rohdrogenposten, Grundform",
               "ch+DAL_LEARNED+y", "trockener Rohstoff, Form I"),
    "sodal": ((2, 2, 1, 1), "f42v.8", "S_ODAL_SEED_PREPARATION_FAMILY",
              "PROVISIONAL_DIRECT_BOUNDARY_COMPOUND",
              "Ansatz aus einem Saatdrogenposten",
              "S_SEED+O_PREP+DAL_LEARNED", "Saat-Rohstoffmaß"),
    "skar": ((1, 1, 1, 1), "f83r.44", "S_K_AR_SEED_FRACTION_FAMILY",
             "EXPLORATORY_SINGLETON_COMPOUND", "heiße Samenfraktion I",
             "S_SEED+K_HEISS+AR_FRACTION_I", "heiße Salzfraktion I"),
}
TARGET_ORDER = list(TARGETS)
SOURCE_BY_LOCUS = {spec[1]: surface for surface, spec in TARGETS.items()}

ATLAS_STATUS = {
    **{surface: "ACCEPTED_V30" for surface in TARGETS},
    **{surface: "V29_ANCHOR" for surface in ("or", "ol", "octhy", "octhey", "sar", "lkar")},
    **{surface: "SISTER_SUPPORT_HOLD" for surface in (
        "ckhal", "sheckhal", "octhedy", "dal", "daly", "daldy",
        "shedal", "odal", "kar", "rkar",
    )},
    "octheey": "ABSENT_HOLD", "octheedy": "ABSENT_HOLD",
    "qokar": "UPSTREAM_SEMANTIC_CONFLICT",
}
BRIDGES = {
    "G653-B01": ("OR_OL_FUSION_FAMILY", "f34v.3", "or ol / orol"),
    "G653-B02": ("OR_OL_FUSION_FAMILY", "f78v.25", "or ol / orol"),
    "G653-B03": ("OR_OL_FUSION_FAMILY", "f104v.33", "or ol / orol"),
    "G653-B04": ("O_PREP_CTH_RESULT_FAMILY", "f112r.23", "octhdy"),
    "G653-B05": ("DAL_LEARNED_MATERIA_FAMILY", "f75v.22", "daldy / dal dy"),
    "G653-B06": ("S_ODAL_SEED_PREPARATION_FAMILY", "f93r.11", "s odal / sodal"),
    "G653-B07": ("CKH_AL_FORM_FAMILY", "f83r.39", "chckhal / ckhal / sheckhal"),
    "G653-B08": ("S_K_AR_SEED_FRACTION_FAMILY", "f83r.44", "skar / kar / lkar / rkar"),
    "G653-B09": ("OR_OL_FUSION_FAMILY", "f82r.10", "oroldair / orol dain / orol dair"),
    "G653-B10": ("S_ODAL_SEED_PREPARATION_FAMILY", "f116r.50", "sodal / s dal"),
    "G653-B11": ("OR_OL_FUSION_FAMILY", "f102v2.19", "o r o l / or ol"),
}
BASE_METRICS = {
    "physical_lines": 4128, "known_token_positions": 14951,
    "unknown_token_positions": 17388, "complete_multi_token_lines": 113,
    "strict_complete_lines": 67, "one_unknown_lines": 165,
    "strict_one_unknown_lines": 39, "exact_glossary_surfaces": 414,
}
FINAL_METRICS = {
    "physical_lines": 4128, "known_token_positions": 14973,
    "unknown_token_positions": 17366, "complete_multi_token_lines": 119,
    "strict_complete_lines": 73, "one_unknown_lines": 160,
    "strict_one_unknown_lines": 34, "exact_glossary_surfaces": 420,
}
ROUNDS = (
    ("BASE_V29", 485, 14951, 17388, 113, 67, 165, 39, 414),
    ("orol", 486, 14961, 17378, 114, 68, 165, 39, 415),
    ("chckhal", 487, 14965, 17374, 115, 69, 164, 38, 416),
    ("octhdy", 488, 14967, 17372, 116, 70, 163, 37, 417),
    ("chdaly", 489, 14970, 17369, 117, 71, 162, 36, 418),
    ("sodal", 490, 14972, 17367, 118, 72, 161, 35, 419),
    ("skar", 491, 14973, 17366, 119, 73, 160, 34, 420),
)
TAGS = {
    "OR_PORTION", "OL_MATERIAL", "CKH_LEARNED", "AL_BOUND", "O_PREP",
    "CTH_LEARNED", "DAL_LEARNED", "S_SEED", "K_HEISS", "AR_FRACTION_I",
}
FILLER = re.compile(
    r"arbeitsgut|arbeitschritt|arbeitsschritt|arbeitsmittel|arbeitsstoff|"
    r"arbeitsobjekt|werkzeug|produkt weiter|f.hre .* aus|leite .* weiter|"
    r"geh(?:e)? zur arbeit|nimm .* arbeite", re.IGNORECASE,
)
OUTPUTS = (
    "PAGE_ALLOWLIST.tsv", "TARGET_DECISION_DECK.tsv", "FAMILY_EVIDENCE_ATLAS.tsv",
    "BOUNDARY_BRIDGE_ATLAS.tsv", "RISK_AND_RIVAL_REGISTER.tsv",
    "ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv", "READER_VARIANT_AUDIT.tsv",
    "SEQUENTIAL_DECISION_LEDGER.tsv", "ROUND_COVERAGE_COUNTS.tsv",
    "ACCEPTED_WHOLE_SURFACE_DEFAULTS.tsv", "SOURCE_PASSAGE_REALITY_CHECK.tsv",
    "AFFECTED_LINE_TRANSLATIONS.tsv", "NEWLY_COMPLETED_LINES.tsv",
    "NEWLY_EXPOSED_ONE_HOLE_LINES.tsv", "V30_EXACT_TOKEN_GLOSSARY.tsv",
    "ALL_LINE_CONCRETE_COVERAGE_V30.tsv", "COMPLETE_PASSAGES_V30.tsv",
    "ONE_UNKNOWN_PASSAGES_V30.tsv", "WORKING_DICTIONARY_V30.tsv", "RESULT.json",
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
            "reader_exact": int(needed <= min(direct)),
            "split_normalized": int(needed <= min(spans)),
        })
    return records


def counts(records, surfaces: set[str]):
    answer = {}
    for surface in surfaces:
        members = [row for row in records if row["surface"] == surface]
        answer[surface] = (
            len(members), len({row["page"] for row in members}),
            sum(row["reader_exact"] for row in members),
            sum(row["split_normalized"] for row in members),
        )
    return answer


def metrics(coverage, complete, one_unknown, glossary_size: int):
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


def adjacent(line: str, *wanted: str) -> bool:
    tokens = line.split()
    return any(tuple(tokens[index:index + len(wanted)]) == wanted for index in range(len(tokens) - len(wanted) + 1))


def load_builder():
    spec = importlib.util.spec_from_file_location("gdt653_builder_validation", RUN)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load GDT653 builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    passed: list[str] = []
    issues: list[str] = []

    def check(ok: object, name: str, detail: str = "") -> None:
        (passed if ok else issues).append(name if ok else f"{name}: {detail or 'condition failed'}")

    result = json.loads((ART / "RESULT.json").read_text(encoding="utf-8"))
    check(result.get("schema") == "GDT653_STRICT_BOUNDARY_COMPOUNDS_RESULT_V1", "result schema")
    check(result.get("experiment_id") == "GDT653" and result.get("status") == STATUS, "result identity/status")
    check(result.get("content_sha256") == canonical_hash({k: v for k, v in result.items() if k != "content_sha256"}), "result content hash")

    allow_rows = read_tsv(ART / "PAGE_ALLOWLIST.tsv")
    pages = {row["page"] for row in allow_rows}
    check(len(allow_rows) == len(pages) == 179, "179 unique guarded pages")
    check("f1r" not in pages and not any(page.startswith("f84") for page in pages), "f1r excluded and f84 forbidden")
    check((ART / "PAGE_ALLOWLIST.tsv").read_bytes() == (ROOT / G652_ALLOW).read_bytes(), "V29 allowlist inherited byte-identically")
    token_rows, token_stats = guarded_query(TOKENS, pages, "page,locus,token_index,eva")
    cross_rows, cross_stats = guarded_query(CROSS, pages, "page,locus,zl3b_clean,it2a_clean,rf1b_clean")
    expected_token_stats = {"selected": 32339, "skipped_forbidden": 709, "skipped_not_allowed": 5940}
    expected_cross_stats = {"selected": 4137, "skipped_forbidden": 98, "skipped_not_allowed": 1151}
    check(len(token_rows) == 32339 and token_stats == expected_token_stats, "guarded token census", repr(token_stats))
    check(len(cross_rows) == 4137 and cross_stats == expected_cross_stats, "guarded cross census", repr(cross_stats))
    guard = result.get("guard", {})
    check(guard.get("token_query") == token_stats and guard.get("cross_query") == cross_stats, "result guarded counts")
    check(guard.get("allowed_pages") == 179 and guard.get("f1r") == "EXCLUDED" and guard.get("f84") == guard.get("f84r") == "FORBIDDEN" and guard.get("new_pages") == guard.get("new_images") == 0, "result guard ceiling")

    atlas = read_tsv(ART / "FAMILY_EVIDENCE_ATLAS.tsv")
    atlas_by = {row["surface"]: row for row in atlas}
    records = independent_occurrences(token_rows, cross_rows, set(ATLAS_STATUS))
    census = counts(records, set(ATLAS_STATUS))
    target_records = [row for row in records if row["surface"] in TARGETS]
    deck = read_tsv(ART / "TARGET_DECISION_DECK.tsv")
    deck_by = {row["surface"]: row for row in deck}
    check(len(deck) == len(deck_by) == 6 and list(deck_by) == TARGET_ORDER, "six ordered target cards")
    check([row["candidate_id"] for row in deck] == [f"G653-C{i:02d}" for i in range(1, 7)], "ordered candidate ids")
    for index, (surface, spec) in enumerate(TARGETS.items(), 1):
        row = deck_by[surface]
        artifact_counts = tuple(int(row[field]) for field in ("occurrences", "pages", "reader_exact_occurrences", "split_normalized_occurrences"))
        check(census[surface] == spec[0], f"independent target census:{surface}", repr(census[surface]))
        check(artifact_counts == spec[0], f"deck target census:{surface}", repr(artifact_counts))
        check((row["source_locus"], row["family"], row["acceptance_tier"], row["working_meaning_de"], row["composition"], row["rival_de"]) == spec[1:], f"exact target value:{surface}")
        check(row["candidate_order"] == str(index) and row["strict_source"] == "1" and row["decision"] == "ACCEPT_V30_EXACT_WHOLE", f"target admission:{surface}")
        check(bool(row["decision_basis"] and row["strongest_counterargument"]), f"target support/rival:{surface}")
    check(sum(census[s][0] for s in TARGETS) == 22, "22 independent target occurrences")
    check(sum(census[s][2] for s in TARGETS) == 20, "20 independent exact occurrences")
    check(sum(census[s][3] for s in TARGETS) == 20, "20 independent normalized occurrences")

    check(len(atlas) == len(atlas_by) == 25 and set(atlas_by) == set(ATLAS_STATUS), "25 unique atlas cells")
    check(Counter(row["final_status"] for row in atlas) == Counter(ATLAS_STATUS.values()), "atlas status census")
    for surface, status in ATLAS_STATUS.items():
        row = atlas_by[surface]
        artifact_counts = tuple(int(row[field]) for field in ("zl3b_occurrences", "pages", "reader_exact_occurrences", "split_normalized_occurrences"))
        check(artifact_counts == census[surface], f"independent atlas census:{surface}", repr(artifact_counts))
        check(row["final_status"] == status, f"atlas status:{surface}")
    check(atlas_by["sar"]["composition"] == "S_SEED+AR_FRACTION_I" and atlas_by["sar"]["final_status"] == "V29_ANCHOR", "SAR sister anchor")
    check(atlas_by["qokar"]["composition"] == "qo+K_HEISS+AR_FRACTION_I" and atlas_by["qokar"]["final_status"] == "UPSTREAM_SEMANTIC_CONFLICT" and census["qokar"] == (153, 62, 132, 132), "QOKAR upstream conflict held")
    check(all(atlas_by[s]["final_status"] != "ACCEPTED_V30" for s in set(ATLAS_STATUS) - set(TARGETS)), "no sister/absent export")

    cross_by = {row["locus"]: row for row in cross_rows}
    bridge_rows = read_tsv(ART / "BOUNDARY_BRIDGE_ATLAS.tsv")
    bridge = {row["bridge_id"]: row for row in bridge_rows}
    check(len(bridge_rows) == len(bridge) == 11 and list(bridge) == list(BRIDGES), "11 ordered boundary bridges")
    for bridge_id, expected in BRIDGES.items():
        row, source = bridge[bridge_id], cross_by[expected[1]]
        check((row["family"], row["locus"], row["diagnostic_surface"]) == expected, f"bridge identity:{bridge_id}")
        check(row["page"] == source["page"] and tuple(row[f] for f in ("zl3b_line", "it2a_line", "rf1b_line")) == tuple(source[f] for f in ("zl3b_clean", "it2a_clean", "rf1b_clean")), f"bridge source fidelity:{bridge_id}")
        check(bool(row["supports"]), f"bridge interpretation:{bridge_id}")
    check(all(adjacent(bridge[key][field], "or", "ol") for key in ("G653-B01", "G653-B02", "G653-B03") for field in ("zl3b_line", "it2a_line", "rf1b_line")), "three all-reader OR OL bridges")
    check(adjacent(bridge["G653-B05"]["it2a_line"], "dal", "dy") and all("daldy" in bridge["G653-B05"][f].split() for f in ("zl3b_line", "rf1b_line")), "DAL/DY split bridge")
    check("sodal" in bridge["G653-B06"]["it2a_line"].split() and adjacent(bridge["G653-B06"]["rf1b_line"], "s", "odal") and adjacent(bridge["G653-B06"]["zl3b_line"], "s", "odam"), "S/ODAL split bridge")
    check("oroldair" in bridge["G653-B09"]["zl3b_line"].split() and all("orol" in bridge["G653-B09"][f].split() for f in ("it2a_line", "rf1b_line")), "OROL superform bridge")
    check("sodal" in bridge["G653-B10"]["zl3b_line"].split() and "sodal" in bridge["G653-B10"]["it2a_line"].split() and adjacent(bridge["G653-B10"]["rf1b_line"], "s", "dal"), "SODAL O-omission bridge")
    check(adjacent(bridge["G653-B11"]["zl3b_line"], "o", "r", "o", "l") and all(adjacent(bridge["G653-B11"][f], "or", "ol") for f in ("it2a_line", "rf1b_line")), "OR/OL granularity bridge")
    for bridge_id, surface in (("G653-B04", "octhdy"), ("G653-B07", "chckhal"), ("G653-B08", "skar")):
        check(all(surface in bridge[bridge_id][f].split() for f in ("zl3b_line", "it2a_line", "rf1b_line")), f"exact sister bridge:{surface}")

    audits = read_tsv(ART / "ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv")
    check(len(audits) == len({row["audit_id"] for row in audits}) == 22, "22 unique occurrence audits")
    check(Counter(row["surface"] for row in audits) == Counter({s: spec[0][0] for s, spec in TARGETS.items()}), "audit surface census")
    check(sum(int(row["reader_exact"]) for row in audits) == 20 and sum(int(row["split_normalized"]) for row in audits) == 20, "audit 20/20 reader totals")
    check(Counter(row["reader_support"] for row in audits) == Counter({"ALL_THREE_EXACT": 20, "READER_VARIANT": 2}), "audit support census")
    check(sum(int(row["hard_collision"]) for row in audits) == 0, "no hard collision")
    record_by_pair = {(row["surface"], row["locus"]): row for row in target_records}
    for row in audits:
        source, independent = cross_by[row["locus"]], record_by_pair[row["surface"], row["locus"]]
        check((int(row["reader_exact"]), int(row["split_normalized"])) == (independent["reader_exact"], independent["split_normalized"]), f"audit reader flags:{row['surface']}:{row['locus']}")
        check(tuple(row[f] for f in ("zl3b_line", "it2a_line", "rf1b_line")) == tuple(source[f] for f in ("zl3b_clean", "it2a_clean", "rf1b_clean")), f"audit source fidelity:{row['surface']}:{row['locus']}")
        check(row["after_gloss_de"] == TARGETS[row["surface"]][4], f"audit target gloss:{row['surface']}:{row['locus']}")

    variants = read_tsv(ART / "READER_VARIANT_AUDIT.tsv")
    expected_variants = {("orol", "f103r.3"), ("sodal", "f116r.50")}
    unstable = {(row["surface"], row["locus"]) for row in target_records if not row["split_normalized"]}
    check(len(variants) == 2 and {(r["surface"], r["locus"]) for r in variants} == expected_variants, "two variant rows")
    check(unstable == expected_variants, "independent variant census")
    check({(r["surface"], r["locus"]) for r in audits if r["verdict"] == "READER_VARIANT_WARNING"} == expected_variants, "variant/audit linkage")
    for row in variants:
        source = cross_by[row["locus"]]
        check(row["reader_support"] == "READER_VARIANT" and row["decision"] == "RETAIN_EXACT_ZL3B_WITH_READER_WARNING", f"variant retention:{row['surface']}")
        check(tuple(row[f] for f in ("zl3b_line", "it2a_line", "rf1b_line")) == tuple(source[f] for f in ("zl3b_clean", "it2a_clean", "rf1b_clean")), f"variant source fidelity:{row['surface']}")

    old_gloss_rows = read_tsv(ROOT / G652_GLOSSARY)
    gloss_rows = read_tsv(ART / "V30_EXACT_TOKEN_GLOSSARY.tsv")
    old_gloss = {row["surface"]: row for row in old_gloss_rows}
    glossary = {row["surface"]: row for row in gloss_rows}
    check(len(old_gloss_rows) == len(old_gloss) == 414, "414 unique V29 glosses")
    check(len(gloss_rows) == len(glossary) == 420 and set(glossary) == set(old_gloss) | set(TARGETS), "glossary 414 to 420")
    check(all(glossary[surface] == row for surface, row in old_gloss.items()), "V29 glossary unchanged")
    for surface, spec in TARGETS.items():
        row = glossary[surface]
        check((row["working_meaning_de"], row["source"], row["strength"], row["scope_state"], row["priority"]) == (spec[4], f"GDT653:{spec[3]}", "EXACT_WHOLE_FAMILY_EXTENSION", "KNOWN_EXACT_WHOLE", "148"), f"V30 glossary card:{surface}")

    old_dictionary = read_tsv(ROOT / G652_DICTIONARY)
    dictionary = read_tsv(ART / "WORKING_DICTIONARY_V30.tsv")
    additions = dictionary[len(old_dictionary):]
    check(len(old_dictionary) == 485 and len(dictionary) == 491, "dictionary 485 to 491")
    check(dictionary[:485] == old_dictionary, "V29 dictionary unchanged")
    check([row["entry"].split("@", 1)[0] for row in additions] == TARGET_ORDER, "six ordered dictionary additions")
    for index, (surface, row) in enumerate(zip(TARGET_ORDER, additions), 1):
        spec = TARGETS[surface]
        check((row["entry"], row["kind"], row["working_meaning_de"], row["composition"], row["status"]) == (f"{surface}@GDT653_EXACT_WHOLE", f"EXACT_ZL3B_WHOLE_{spec[3]}", spec[4], spec[5], f"NEW_V30_ACCEPTED_ROUND_{index:02d}"), f"dictionary addition:{surface}")
    exported = {row["entry"].split("@", 1)[0] for row in dictionary} | set(glossary)
    check(not (exported & TAGS), "no structural tag exported")

    old_cov, old_complete, old_one = (read_tsv(ROOT / path) for path in (G652_COVERAGE, G652_COMPLETE, G652_ONE))
    coverage = read_tsv(ART / "ALL_LINE_CONCRETE_COVERAGE_V30.tsv")
    complete = read_tsv(ART / "COMPLETE_PASSAGES_V30.tsv")
    one = read_tsv(ART / "ONE_UNKNOWN_PASSAGES_V30.tsv")
    old_metrics = metrics(old_cov, old_complete, old_one, len(old_gloss))
    new_metrics = metrics(coverage, complete, one, len(glossary))
    check(old_metrics == BASE_METRICS, "V29 metrics", repr(old_metrics))
    check(new_metrics == FINAL_METRICS, "V30 metrics", repr(new_metrics))
    check(sum(int(row["token_count"]) for row in coverage) == 32339, "V30 token census")
    check(new_metrics["known_token_positions"] - old_metrics["known_token_positions"] == 22 and old_metrics["unknown_token_positions"] - new_metrics["unknown_token_positions"] == 22, "V29/V30 position delta")
    check(new_metrics["complete_multi_token_lines"] - old_metrics["complete_multi_token_lines"] == 6 and new_metrics["strict_complete_lines"] - old_metrics["strict_complete_lines"] == 6, "V29/V30 complete deltas")
    check(old_metrics["one_unknown_lines"] - new_metrics["one_unknown_lines"] == 5 and old_metrics["strict_one_unknown_lines"] - new_metrics["strict_one_unknown_lines"] == 5, "V29/V30 one-hole deltas")
    old_cov_by = {row["locus"]: row for row in old_cov}
    cov_by = {row["locus"]: row for row in coverage}
    target_positions = Counter(row["locus"] for row in target_records)
    check(set(old_cov_by) == set(cov_by) and len(cov_by) == 4128, "coverage locus set")
    check(all(int(cov_by[l]["known_tokens"]) - int(old_cov_by[l]["known_tokens"]) == target_positions[l] and int(old_cov_by[l]["unknown_tokens"]) - int(cov_by[l]["unknown_tokens"]) == target_positions[l] for l in cov_by), "linewise target-position deltas")
    affected = read_tsv(ART / "AFFECTED_LINE_TRANSLATIONS.tsv")
    check(len(affected) == len({r["locus"] for r in affected}) == 22 and {r["locus"] for r in affected} == set(target_positions), "22 exact affected lines")
    check(all(r["v29_tokenwise_de"] != r["v30_tokenwise_de"] for r in affected), "all affected translations changed")
    check(all((r["complete_v30"] == "True") == (int(cov_by[r["locus"]]["unknown_tokens"]) == 0) for r in affected), "affected completion flags")

    old_complete_by = {row["locus"]: row for row in old_complete}
    complete_by = {row["locus"]: row for row in complete}
    expected_loci = set(SOURCE_BY_LOCUS)
    check(set(old_complete_by) <= set(complete_by), "no V29 complete line lost")
    check(set(complete_by) - set(old_complete_by) == expected_loci, "exact six new complete loci")
    new_rows = read_tsv(ART / "NEWLY_COMPLETED_LINES.tsv")
    new_by = {row["locus"]: row for row in new_rows}
    check(len(new_rows) == len(new_by) == 6 and set(new_by) == expected_loci, "six new complete rows")
    check(all(row["strict_complete"] == "1" for row in new_rows), "all six new lines strict")
    old_one_by_pair = {(row["unknown_surface"], row["locus"]): row for row in old_one}
    for locus, surface in SOURCE_BY_LOCUS.items():
        source, row = old_one_by_pair.get((surface, locus), {}), new_by[locus]
        check(source.get("strict_eligible") == "1" and source.get("unknown_tokens") == "1", f"strict V29 source:{surface}")
        check(row["enabled_by_surfaces"] == surface and row["zl3b_line"] == cov_by[locus]["zl3b_line"] and TARGETS[surface][4] in row["literal_v30_de"], f"new complete payload:{surface}")
        check("[" not in row["literal_v30_de"] and "?" not in row["literal_v30_de"] and row["curated_source_reading_de"] != "NOT_CURATED_SOURCE_LINE", f"complete concrete rendering:{surface}")

    reality = read_tsv(ART / "SOURCE_PASSAGE_REALITY_CHECK.tsv")
    reality_by = {row["locus"]: row for row in reality}
    check(len(reality) == len(reality_by) == 6 and set(reality_by) == expected_loci, "six strict reality rows")
    for locus, surface in SOURCE_BY_LOCUS.items():
        row = reality_by[locus]
        check(row["surface"] == surface and row["strict_complete"] == "1" and row["acceptance_tier"] == TARGETS[surface][3], f"reality identity:{surface}")
        check(TARGETS[surface][4] in row["tokenwise_translation_de"] and "[" not in row["tokenwise_translation_de"] and "?" not in row["tokenwise_translation_de"], f"reality concrete rendering:{surface}")
    exposed = read_tsv(ART / "NEWLY_EXPOSED_ONE_HOLE_LINES.tsv")
    check(len(exposed) == 1 and (exposed[0]["enabled_by_surface"], exposed[0]["locus"], exposed[0]["unknown_surface"], exposed[0]["strict_eligible"]) == ("orol", "f75v.70", "olchedy", "1"), "one newly exposed strict hole")

    round_rows = read_tsv(ART / "ROUND_COVERAGE_COUNTS.tsv")
    check(len(round_rows) == 7 and [row["round"] for row in round_rows] == [str(i) for i in range(7)], "seven ordered rounds")
    for index, expected in enumerate(ROUNDS):
        row = round_rows[index]
        observed = (row["surface"], int(row["dictionary_entries"]), int(row["known_token_positions"]), int(row["unknown_token_positions"]), int(row["complete_multi_token_lines"]), int(row["strict_complete_lines"]), int(row["one_unknown_lines"]), int(row["strict_one_unknown_lines"]), int(row["exact_glossary_surfaces"]))
        check(observed == expected, f"round metrics:{index}", repr(observed))
        check(row["dictionary_sha256"] == canonical_hash(dictionary[:int(row["dictionary_entries"])]), f"round dictionary hash:{index}")
    ledger = read_tsv(ART / "SEQUENTIAL_DECISION_LEDGER.tsv")
    check(len(ledger) == 6 and [row["surface"] for row in ledger] == TARGET_ORDER, "six sequential decisions")
    for index, row in enumerate(ledger, 1):
        surface, spec = TARGET_ORDER[index - 1], TARGETS[TARGET_ORDER[index - 1]]
        check(row["round"] == str(index) and row["decision"] == "ACCEPT_V30_EXACT_WHOLE" and (int(row["pre_dictionary_entries"]), int(row["post_dictionary_entries"])) == (484 + index, 485 + index) and (int(row["occurrences"]), int(row["all_reader_exact"]), int(row["split_normalized"])) == (spec[0][0], spec[0][2], spec[0][3]) and row["new_complete_loci"] == spec[1], f"sequential payload:{surface}")

    defaults = read_tsv(ART / "ACCEPTED_WHOLE_SURFACE_DEFAULTS.tsv")
    default_by = {row["surface"]: row for row in defaults}
    risks = read_tsv(ART / "RISK_AND_RIVAL_REGISTER.tsv")
    risk_by = {row["surface"]: row for row in risks}
    check(len(defaults) == len(default_by) == 6 and list(default_by) == TARGET_ORDER, "six accepted defaults")
    check(len(risks) == len(risk_by) == 6 and set(risk_by) == set(TARGETS), "six rival rows")
    for surface, spec in TARGETS.items():
        check((default_by[surface]["working_meaning_de"], default_by[surface]["composition"]) == (spec[4], spec[5]), f"default payload:{surface}")
        check((risk_by[surface]["working_meaning_de"], risk_by[surface]["rival_de"]) == (spec[4], spec[6]) and bool(risk_by[surface]["strongest_counterargument"] and risk_by[surface]["replacement_trigger"]), f"rival payload:{surface}")

    target = result.get("target_run", {})
    check(target.get("accepted_surfaces") == TARGET_ORDER, "result target order")
    check((target.get("candidates"), target.get("accepted_exact_wholes"), target.get("strict_v29_holes_closed")) == (6, 6, 6), "result closure census")
    check((target.get("audited_occurrences"), target.get("all_reader_exact_occurrences"), target.get("split_normalized_occurrences")) == (22, 20, 20), "result 22/20/20")
    check(target.get("reader_variant_warnings") == 2 and target.get("hard_collisions") == 0, "result variants/collisions")
    check(result.get("coverage") == {"base": BASE_METRICS, "final": FINAL_METRICS, "newly_completed_lines": 6, "newly_exposed_one_hole_lines": 1, "affected_lines": 22}, "result coverage")
    working = result.get("working_dictionary", {})
    check((working.get("v29_entries"), working.get("v30_entries"), working.get("accepted_tail_entries"), working.get("v29_glossary_surfaces"), working.get("v30_glossary_surfaces")) == (485, 491, 6, 414, 420), "result dictionary metrics")
    check(working.get("v29_prefix_sha256") == canonical_hash(old_dictionary) and working.get("v30_sha256") == canonical_hash(dictionary), "result dictionary hashes")
    packet = result.get("compound_packet", {})
    check(packet.get("separated_counterpart_targets") == ["orol"] and packet.get("reader_split_targets") == ["sodal"], "result direct-boundary classes")
    check(packet.get("learned_head_targets") == ["chckhal", "octhdy", "chdaly"] and packet.get("singleton_composition_target") == ["skar"], "result learned/singleton classes")
    check(set(packet.get("structural_tags_not_free_words", [])) == TAGS, "result structural-tag ceiling")
    check(len(packet.get("upstream_consistency_conflicts", [])) == 1 and "qokar" in packet["upstream_consistency_conflicts"][0].lower() and "not silently rewrite" in packet["upstream_consistency_conflicts"][0].lower(), "result QOKAR conflict ceiling")
    claim = str(result.get("claim_boundary", "")).lower()
    check(all(word in claim for word in ("exploratory", "not a solved plaintext", "six", "replaceable", "no free component", "f1r", "new page", "new image")), "result claim core")

    scan_paths = [ROOT / BASE / name for name in ("REPORT.md", "METHOD.md", "README.md", "artifacts/README.md", "artifacts/RESULT.json")] + sorted(ART.glob("*.tsv"))
    filler_hits = [str(path.relative_to(ROOT)) for path in scan_paths if FILLER.search(path.read_text(encoding="utf-8"))]
    check(not filler_hits, "no generic filler", repr(filler_hits))
    semantic_text = "\n".join(row["working_meaning_de"] for row in deck) + "\n" + "\n".join(row["smoothed_working_reading_de"] for row in reality)
    check(not any(tag in semantic_text for tag in TAGS), "no tags in rendered German")

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
    check(manifest.get("experiment_id") == "GDT653" and manifest.get("slug") == "strict_v29_boundary_compounds", "manifest identity")
    check(manifest.get("status") == STATUS, "manifest status")
    check(manifest.get("sealed_data") == {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"}, "manifest seals")
    check(manifest.get("commands") == {"run": f"python3 {BASE}/src/run.py", "validate": f"python3 {BASE}/src/validate.py"}, "manifest commands")
    check(manifest.get("validation") == {"artifact": str(BASE / "artifacts/VALIDATION.json"), "status": "PASS"}, "manifest validation")
    check(set(manifest.get("dependencies", [])) == {"GDT628", "GDT633", "GDT636", "GDT642", "GDT648", "GDT651", "GDT652"}, "manifest dependencies")
    question, ceiling = str(manifest.get("question", "")).lower(), str(manifest.get("claim_ceiling", "")).lower()
    check(len(question) >= 80 and all(word in question for word in ("six", "strict", "concrete", "whole-bound", "close")), "manifest question core")
    check(len(ceiling) >= 120 and all(word in ceiling for word in ("explor", "exact-whole", "free component", "plaintext", "exact ingredient")), "manifest claim ceiling core")
    manifest_inputs = {row.get("path"): row for row in manifest.get("inputs", [])}
    check(set(manifest_inputs) == set(inputs), "manifest/result inputs")
    for path, row in manifest_inputs.items():
        check(row.get("sha256") == inputs[path] == sha256(ROOT / path) and bool(row.get("role")), f"manifest input seal:{path}")
    manifest_outputs = {row.get("path"): row for row in manifest.get("outputs", [])}
    required = {
        str(BASE / path) for path in (
            "METHOD.md", "README.md", "REPORT.md", "artifacts/README.md",
            "artifacts/TARGET_DECISION_DECK.tsv", "artifacts/FAMILY_EVIDENCE_ATLAS.tsv",
            "artifacts/BOUNDARY_BRIDGE_ATLAS.tsv", "artifacts/SOURCE_PASSAGE_REALITY_CHECK.tsv",
            "artifacts/NEWLY_COMPLETED_LINES.tsv", "artifacts/RESULT.json",
            "artifacts/V30_EXACT_TOKEN_GLOSSARY.tsv", "artifacts/ALL_LINE_CONCRETE_COVERAGE_V30.tsv",
            "artifacts/COMPLETE_PASSAGES_V30.tsv", "artifacts/WORKING_DICTIONARY_V30.tsv",
            "artifacts/VALIDATION.json", "src/run.py", "src/validate.py",
        )
    }
    check(required <= set(manifest_outputs), "manifest core outputs")
    for path, row in manifest_outputs.items():
        target_path = ROOT / str(path)
        check(not Path(str(path)).is_absolute() and target_path.is_file() and bool(row.get("role")), f"manifest output path:{path}")
        if str(path) != str(BASE / "artifacts/VALIDATION.json") and target_path.is_file():
            check(row.get("sha256") == sha256(target_path), f"manifest output seal:{path}")

    report_text = REPORT.read_text(encoding="utf-8").lower()
    for needle in (
        "drogenstoffportion", "trockenes arzneikompositum, rohstoffform i",
        "fertig aufbereitete drogenzubereitung, grundform",
        "trockener rohdrogenposten, grundform",
        "ansatz aus einem saatdrogenposten", "heiße samenfraktion i",
        "14.951", "14.973", "113", "119", "67", "73", "explorativ",
    ):
        check(needle in report_text, f"report contains:{needle}")
    check(all(surface in report_text for surface in TARGETS), "report six surfaces")
    check(all(locus.lower() in report_text for locus in SOURCE_BY_LOCUS), "report six source loci")

    # Replay deliberately runs last; every scientific check above is builder-independent.
    try:
        builder = load_builder()
        with tempfile.TemporaryDirectory(prefix="gdt653_validate_") as tmp:
            replay = Path(tmp)
            builder.build(replay)
            check({path.name for path in replay.iterdir()} == set(OUTPUTS), "replay output set")
            for name in OUTPUTS:
                check((ART / name).read_bytes() == (replay / name).read_bytes(), f"byte replay:{name}")
    except Exception as exc:
        issues.append(f"builder replay: {type(exc).__name__}: {exc}")

    validation = {
        "schema": "GDT653_VALIDATION_V1", "experiment_id": "GDT653",
        "status": "PASS" if not issues else "FAIL", "checks_passed": len(passed),
        "checks_failed": len(issues), "passed": passed, "issues": issues,
    }
    VALIDATION.write_text(json.dumps(validation, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if issues:
        print(f"GDT653 validation FAIL: {len(issues)} issue(s), {len(passed)} checks passed")
        for issue in issues:
            print(f"- {issue}")
        return 1
    print(f"GDT653 validation PASS: {len(passed)} checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
