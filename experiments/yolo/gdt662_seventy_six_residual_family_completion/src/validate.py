#!/usr/bin/env python3
"""Independent source-first release validator for GDT662.

The GDT662 builder is deliberately never imported.  Protected transcription
rows are materialized only through the guarded query executable, and the
builder is used solely as a separate process for the final tempdir replay.
"""
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
BASE = Path("experiments/yolo/gdt662_seventy_six_residual_family_completion")
ART = ROOT / BASE / "artifacts"
RUN = ROOT / BASE / "src/run.py"
G661 = Path("experiments/yolo/gdt661_forty_eight_residual_family_completion")
TOKENS = Path("transcription/voynich_zl3b_tokens.tsv")
CROSS = Path("transcription/voynich_cross_transcription_lines.tsv")

OUTPUT_NAMES = (
    "PAGE_ALLOWLIST.tsv", "TARGET_DECISION_DECK.tsv", "ACCEPTED_WHOLE_SURFACE_DEFAULTS.tsv",
    "CONTEXT_RENDERING_CARDS.tsv", "CARD_ARCHITECTURE_SUMMARY.tsv",
    "ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv", "READER_VARIANT_AUDIT.tsv",
    "FAMILY_COMPOSITION_ATLAS.tsv", "FRONTIER_76_COMPLETIONS.tsv",
    "TARGET_LINE_TRANSLATIONS.tsv", "ROUND_COVERAGE_COUNTS.tsv",
    "NEWLY_COMPLETED_LINES.tsv", "NEWLY_EXPOSED_ONE_HOLE_LINES.tsv",
    "V39_WORKING_TOKEN_GLOSSARY.tsv", "WORKING_DICTIONARY_V39.tsv",
    "ALL_LINE_CONCRETE_COVERAGE_V39.tsv", "COMPLETE_PASSAGES_V39.tsv",
    "ONE_UNKNOWN_PASSAGES_V39.tsv",
)

TARGET_ORDER = tuple("""
lkees shar ycheeo otydy lkedar far dsheey choty chkey cheeoldy a oteeo lain dchy oro oekor
ycho schodain choraly totchy qokol sham kochky otoldy qo ctho dchaiin ydaiin dytory kolschees
tchol cthodd sheoty ykchokeo ochockhy qoctheol kcheeytain shckheody qodaiin ytchocthol
qolkeeoly olsheedy shety qokchdyl saiiin qol chee chl lokedy olkchdy tees olkedy oly los
olshdy doly keeol aral dchedy kair ra lchedar ey pcheol lchedam qokeeey oldy sheekchy
ypshedy opchdy taral dytshy choldy tchor sheoees cheyet
""".split())
TARGETS = frozenset(TARGET_ORDER)


def _parse_counts(raw: str) -> dict[str, int]:
    return {item.split("=", 1)[0]: int(item.split("=", 1)[1]) for item in raw.split()}


EXPECTED_COUNTS = _parse_counts("""
lkees=1 shar=29 ycheeo=6 otydy=3 lkedar=1 far=2 dsheey=7 choty=34 chkey=4 cheeoldy=1
a=9 oteeo=6 lain=5 dchy=22 oro=4 oekor=1 ycho=3 schodain=1 choraly=1 totchy=1 qokol=88
sham=6 kochky=1 otoldy=9 qo=50 ctho=18 dchaiin=3 ydaiin=14 dytory=1 kolschees=1 tchol=16
cthodd=1 sheoty=1 ykchokeo=1 ochockhy=1 qoctheol=1 kcheeytain=1 shckheody=1 qodaiin=41
ytchocthol=1 qolkeeoly=1 olsheedy=1 shety=7 qokchdyl=1 saiiin=2 qol=132 chee=1 chl=28
lokedy=1 olkchdy=4 tees=1 olkedy=22 oly=53 los=5 olshdy=3 doly=4 keeol=10 aral=15
dchedy=26 kair=11 ra=1 lchedar=2 ey=14 pcheol=10 lchedam=2 qokeeey=27 oldy=25
sheekchy=2 ypshedy=1 opchdy=18 taral=2 dytshy=1 choldy=8 tchor=21 sheoees=1 cheyet=1
""")


def _parse_tab_map(raw: str) -> dict[str, str]:
    return dict(line.split("\t", 1) for line in raw.strip().splitlines())


EXPECTED_MEANINGS = _parse_tab_map("""
lkees\tstark erhitzte Holzdroge, Endstufe
shar\tangefeuchtete Drogenfraktion I
ycheeo\tEintrag: zweiter Trockenansatz
otydy\tkalter Ansatz in Grundform, fertig
lkedar\terhitzte Holzfraktion I
far\tPflanzendroge
dsheey\tabgemessene, vollständig angefeuchtete Droge
choty\tkalter Trockenansatz
chkey\ttrocken-heiß in der Mittelstufe
cheeoldy\tvollständig getrockneter Drogenstoff, fertig
a\tje, zu gleichen Teilen
oteeo\tzweiter Kaltansatz
lain\tDrogenholz, Charge II
dchy\tDosis Trockendroge, Grundform
oro\tAnsatzportion
oekor\terwärmte Ansatzportion
ycho\tEintrag: Trockenansatz
schodain\ttrockener Samenansatz, Dosis II
choraly\troher Pflanzenteil, Klasse I
totchy\tkalter Ansatz aus kalt-trockener Droge
qokol\terhitzen
sham\tein Maß Flüssigkeit
kochky\theißer Trockenansatz, Grundform
otoldy\tfertiger Kaltansatz
qo\tnehmen
ctho\tKrautansatz
dchaiin\tabgemessene Trockendroge, Grad III
ydaiin\tdavon drei Maße
dytory\tals kalte Portion abteilen
kolschees\theiß getrocknete Arzneispecies
tchol\tkalt-trockenes Drogenmaterial
cthodd\tfertiger Krautabsud
sheoty\tkalt angesetzte Feuchtzubereitung
ykchokeo\tEintrag: heiß-trockener Auszug
ochockhy\tTrockenansatz eines Arzneikompositums
qoctheol\tKrautgrundstoff
kcheeytain\theiß-trocken bis Endstufe, danach kalt Grad II
shckheody\tfertig angesetztes feuchtes Arzneikompositum
qodaiin\tQualitätsgrad III
ytchocthol\tEintrag: kalt-trockener Krautansatz
qolkeeoly\terhitzte Drogenbasis; danach abseihen
olsheedy\tvollständig eingeweichtes Drogenmaterial, fertig
shety\tfeucht-kalt ansetzen
qokchdyl\theiß-trocken aufbereitetes Drogenholz
saiiin\tSaatgutcharge IV
qol\tDrogenstoff zugeben
chee\tvollständig getrocknet
chl\ttrocknen
lokedy\terhitztes Drogenholz, fertig
olkchdy\theiß-trocken aufbereitetes Drogenmaterial
tees\tkalte Arzneispecies, Endstufe
olkedy\terhitzte Drogenbasis, fertig
oly\tabseihen
los\tDrogenholzposten
olshdy\tangefeuchtetes Drogenmaterial, fertig
doly\teine Dosis Abguss
keeol\tstark erhitzter Drogenstoff
aral\tRohdrogenfraktion I
dchedy\tabgemessene Trockendroge, fertig
kair\theiße Drogenfraktion II
ra\tWurzelanteil
lchedar\tgetrocknete Holzfraktion I
ey\tanschließend
pcheol\tgetrockneter Pulverstoff
lchedam\tein Maß getrocknetes Drogenholz
qokeeey\tstark erhitzt, Endstufe III
oldy\tfertiger, abgeseihter Auszug
sheekchy\tvollständig anfeuchten, dann heiß-trocken ansetzen
ypshedy\tEintrag: fertige Pulverpaste
opchdy\tfertiges Trockenpulverpräparat
taral\tkalte Rohdrogenfraktion I
dytshy\tdanach kalt-feucht ansetzen
choldy\tfertig getrocknete Droge
tchor\tkalt-trockene Drogenportion
sheoees\tvollständig eingeweichte Arzneimischung
cheyet\tgetrocknete, abgekühlte Wurzel
""")

LEARNED_FUNCTIONS = frozenset({"qo", "a", "ey"})
LEARNED_WHOLES = frozenset({"chl", "far", "los", "cheyet"})
HYBRIDS = frozenset({
    "oro", "dytory", "kolschees", "cthodd", "ochockhy", "shckheody", "qokchdyl", "dytshy",
})
PRODUCTIVE = TARGETS - LEARNED_FUNCTIONS - LEARNED_WHOLES - HYBRIDS
EXPECTED_ARCHITECTURE = {
    "PRODUCTIVE_COMPOUND": (61, 741, PRODUCTIVE),
    "LEARNED_FUNCTION_WORD": (3, 73, LEARNED_FUNCTIONS),
    "LEARNED_WHOLE": (4, 36, LEARNED_WHOLES),
    "HYBRID_EXACT": (8, 11, HYBRIDS),
}

Y_ENTRY_SURFACES = frozenset({"ycheeo", "ycho", "ykchokeo", "ypshedy", "ytchocthol"})
Y_PAYLOADS = {
    "ycheeo": "zweiter Trockenansatz", "ycho": "Trockenansatz",
    "ykchokeo": "heiß-trockener Auszug", "ypshedy": "fertige Pulverpaste",
    "ytchocthol": "kalt-trockener Krautansatz",
}
ACTION_SURFACES = frozenset({"qokol", "qokeeey", "chl", "dytory", "sheekchy", "shety", "dytshy"})
ACTION_RENDER = {
    "qokeeey": "erhitze bis Endstufe III",
    "dytory": "teile als kalte Portion ab",
    "sheekchy": "feuchte vollständig an, dann setze heiß-trocken an",
    "shety": "setze feucht-kalt an",
    "dytshy": "setze danach kalt-feucht an",
}
GRADE_AFTER_QOKOL = {"dain": "II", "daiin": "III", "daiiin": "IV"}
ACTION_BOUNDARIES = frozenset({
    "qol", "qokol", "qokeeey", "chl", "oly", "shety", "sheekchy", "dytory", "dytshy",
})
CHL_PREVIOUS_CONTEXTS = frozenset({("qokar", "aiin"), ("qokar", "ykeedy")})
EY_MIX_CONTEXTS = frozenset({("cheol", "cheor")})


def _parse_context(raw: str) -> dict[tuple[str, str], tuple[int, str]]:
    result: dict[tuple[str, str], tuple[int, str]] = {}
    for line in raw.strip().splitlines():
        klass, surface, count, rendering = line.split("\t", 3)
        result[klass, surface] = int(count), rendering
    return result


EXPECTED_CONTEXT_CARDS = _parse_context("""
A_EQUAL_PARTS\ta\t8\tje zu gleichen Teilen
A_EQUAL_PARTS_CONTINUATION\ta\t1\tzu gleichen Teilen mit Folgendem:
CHEE_DRY_MATERIAL_NEXT\tchee\t1\tvollständig getrocknetes
CHL_DRY_FINISH\tchl\t1\ttrockne.
CHL_DRY_NEXT\tchl\t25\ttrockne Folgendes:
CHL_DRY_PREVIOUS_HOT_FRACTION\tchl\t2\ttrockne die vorstehende heiße Drogenfraktion I
EY_MIX_NEXT\tey\t1\tmische Folgendes:
EY_MIX_PREVIOUS\tey\t1\tmische Vorstehendes.
EY_MIX_BETWEEN_MATERIALS\tey\t1\tmische Vorstehendes mit Folgendem:
EY_SEQUENCE_NEXT\tey\t11\tanschließend:
OLY_STRAIN_FINISH\toly\t36\tseihe Vorstehendes ab.
OLY_STRAIN_PREVIOUS\toly\t17\tseihe Vorstehendes ab
PRACTICAL_ACTION\tdytory\t1\tteile als kalte Portion ab
PRACTICAL_ACTION\tdytshy\t1\tsetze danach kalt-feucht an
PRACTICAL_ACTION\tqokeeey\t27\terhitze bis Endstufe III
PRACTICAL_ACTION\tsheekchy\t2\tfeuchte vollständig an, dann setze heiß-trocken an
PRACTICAL_ACTION\tshety\t7\tsetze feucht-kalt an
QOKOL_DOUBLE_START\tqokol\t2\terhitze
QOKOL_HEAT_NEXT\tqokol\t78\terhitze Folgendes:
QOKOL_TO_GRADE\tqokol\t8\terhitze
QODAIIN_GRADE_NEXT\tqodaiin\t1\tFolgendes: Qualitätsgrad III
QODAIIN_GRADE_PREVIOUS\tqodaiin\t1\tVorstehendes: Qualitätsgrad III
QOL_ADD_NEXT\tqol\t117\tgib Folgendes hinzu:
QOL_ADD_PREVIOUS\tqol\t15\tgib Vorstehendes hinzu
QO_TAKE_NEXT\tqo\t48\tnimm Folgendes:
QO_TAKE_PREVIOUS\tqo\t2\tnimm Vorstehendes.
Y_ENTRY_COMMAND\tycheeo\t6\tEintrag: zweiter Trockenansatz
Y_ENTRY_COMMAND\tycho\t3\tEintrag: Trockenansatz
Y_ENTRY_COMMAND\tykchokeo\t1\tEintrag: heiß-trockener Auszug
Y_ENTRY_COMMAND\typshedy\t1\tEintrag: fertige Pulverpaste
Y_ENTRY_COMMAND\tytchocthol\t1\tEintrag: kalt-trockener Krautansatz
""")
EXPECTED_RENDER_CLASSES = {
    **dict(Counter({klass: sum(count for (name, _), (count, _) in EXPECTED_CONTEXT_CARDS.items() if name == klass)
                    for klass, _ in EXPECTED_CONTEXT_CARDS})),
    "EXACT_WHOLE": 434,
}

BASE_METRICS = {
    "physical_lines": 4128, "known_token_positions": 18451, "unknown_token_positions": 13888,
    "complete_multi_token_lines": 233, "strict_complete_lines": 99,
    "one_unknown_lines": 290, "strict_one_unknown_lines": 73, "working_glossary_surfaces": 556,
}
FINAL_METRICS = {
    "physical_lines": 4128, "known_token_positions": 19312, "unknown_token_positions": 13027,
    "complete_multi_token_lines": 331, "strict_complete_lines": 125,
    "one_unknown_lines": 302, "strict_one_unknown_lines": 67, "working_glossary_surfaces": 632,
}

OPEN = re.compile(r"\[[^\]]+:\?\]")
GENERIC_FILLER = re.compile(
    r"arbeitsgut|arbeitsvorgang|arbeitschritt|arbeitsschritt|arbeitsmittel|arbeitsstoff|"
    r"\b(?:vorgang|prozess|tätigkeit|operation)\b|vorgang\s+ausführen|gut\s+bearbeiten|"
    r"führe\s+.{0,80}\s+aus|leite\s+.{0,80}\s+weiter",
    re.I,
)


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


def split_compact(value: str) -> list[str]:
    return [] if value in {"", "NONE"} else value.split("|")


def guarded_query(path: Path, pages: set[str], columns: str) -> tuple[list[dict[str, str]], dict[str, int]]:
    command = [str(ROOT / "vmanus-exp"), "query-tsv", str(path), "--selector", "page"]
    for page in sorted(pages):
        command.extend(("--allow", page))
    command.extend(("--columns", columns))
    for prefix in ("f1r", "f84", "f84r"):
        command.extend(("--forbid-prefix", prefix))
    done = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    stats_lines = [line for line in done.stderr.splitlines() if line.startswith("GUARD_STATS ")]
    if done.returncode or len(stats_lines) != 1:
        raise RuntimeError(done.stderr or "guarded query failed")
    rows = list(csv.DictReader(io.StringIO(done.stdout), delimiter="\t"))
    stats = {key: int(value) for key, value in json.loads(stats_lines[0][12:]).items()}
    if stats.get("selected") != len(rows):
        raise RuntimeError("guard stats disagree with materialized rows")
    if any(row.get("page") == "f1r" or row.get("page", "").startswith("f84") for row in rows):
        raise RuntimeError("forbidden page escaped guarded query")
    return rows, stats


def span_count(words: list[str], target: str) -> int:
    count = 0
    for start in range(len(words)):
        joined = ""
        for word in words[start:]:
            joined += word
            if joined == target:
                count += 1
                break
            if len(joined) >= len(target) or not target.startswith(joined):
                break
    return count


def position(ordinal: int, length: int) -> str:
    if length == 1:
        return "ONLY"
    if ordinal == 1:
        return "BOS"
    if ordinal == length:
        return "EOS"
    return "MEDIAL"


def card_type(surface: str) -> str:
    if surface in LEARNED_FUNCTIONS:
        return "LEARNED_FUNCTION_WORD"
    if surface in LEARNED_WHOLES:
        return "LEARNED_WHOLE"
    if surface in HYBRIDS:
        return "HYBRID_EXACT"
    return "PRODUCTIVE_COMPOUND"


def rendering_class(surface: str, pos: str, left: str, right: str) -> str:
    if surface in Y_ENTRY_SURFACES:
        return "Y_ENTRY_COMMAND"
    if surface == "qo":
        return "QO_TAKE_PREVIOUS" if pos in {"EOS", "ONLY"} else "QO_TAKE_NEXT"
    if surface == "qol":
        if right == "qol":
            return "QOL_ADD_PREVIOUS"
        if left == "qol":
            return "QOL_ADD_NEXT"
        if pos in {"EOS", "ONLY"} or right in ACTION_BOUNDARIES:
            return "QOL_ADD_PREVIOUS"
        return "QOL_ADD_NEXT"
    if surface == "qokol":
        if right in GRADE_AFTER_QOKOL:
            return "QOKOL_TO_GRADE"
        if right == "qokol":
            return "QOKOL_DOUBLE_START"
        return "QOKOL_HEAT_NEXT"
    if surface == "oly":
        return "OLY_STRAIN_FINISH" if pos in {"EOS", "ONLY"} else "OLY_STRAIN_PREVIOUS"
    if surface == "a":
        return "A_EQUAL_PARTS_CONTINUATION" if pos in {"EOS", "ONLY"} else "A_EQUAL_PARTS"
    if surface == "ey":
        if pos in {"EOS", "ONLY"}:
            return "EY_MIX_PREVIOUS"
        if pos == "BOS":
            return "EY_MIX_NEXT"
        if (left, right) in EY_MIX_CONTEXTS:
            return "EY_MIX_BETWEEN_MATERIALS"
        return "EY_SEQUENCE_NEXT"
    if surface == "qodaiin" and right == "qodaiin":
        return "QODAIIN_GRADE_PREVIOUS"
    if surface == "qodaiin" and left == "qodaiin":
        return "QODAIIN_GRADE_NEXT"
    if surface == "chee" and right == "ol":
        return "CHEE_DRY_MATERIAL_NEXT"
    if surface == "chl":
        if pos in {"EOS", "ONLY"}:
            return "CHL_DRY_FINISH"
        if (left, right) in CHL_PREVIOUS_CONTEXTS:
            return "CHL_DRY_PREVIOUS_HOT_FRACTION"
        return "CHL_DRY_NEXT"
    if surface in ACTION_SURFACES:
        return "PRACTICAL_ACTION"
    return "EXACT_WHOLE"


def render_text(surface: str, klass: str) -> str:
    if klass == "EXACT_WHOLE":
        return EXPECTED_MEANINGS[surface]
    return EXPECTED_CONTEXT_CARDS[klass, surface][1]


def source_records(
    tokens: list[dict[str, str]], cross_rows: list[dict[str, str]],
) -> tuple[list[dict[str, object]], dict[str, list[dict[str, str]]]]:
    cross = {row["locus"]: row for row in cross_rows}
    by_line: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in tokens:
        by_line[row["locus"]].append(row)
    for line in by_line.values():
        line.sort(key=lambda item: int(item["token_index"]))

    records: list[dict[str, object]] = []
    for locus in sorted(by_line):
        line = by_line[locus]
        words = [row["eva"] for row in line]
        seen: Counter[str] = Counter()
        readers = [cross[locus][field].split() for field in ("zl3b_clean", "it2a_clean", "rf1b_clean")]
        for index, token in enumerate(line):
            surface = token["eva"]
            seen[surface] += 1
            if surface not in TARGETS:
                continue
            ordinal = index + 1
            pos = position(ordinal, len(line))
            left = words[index - 1] if index else "<BOS>"
            right = words[index + 1] if index + 1 < len(line) else "<EOS>"
            klass = rendering_class(surface, pos, left, right)
            direct_caps = [reader.count(surface) for reader in readers]
            span_caps = [span_count(reader, surface) for reader in readers]
            records.append({
                "occurrence_id": f"G662-T{len(records) + 1:04d}",
                "page": token["page"], "locus": locus, "token_index": int(token["token_index"]),
                "ordinal": ordinal, "line_length": len(line), "surface": surface,
                "kind": token["kind"], "position": pos, "section": token["section"],
                "language": token["language"], "hand": token["hand"], "left": left, "right": right,
                "card_type": card_type(surface), "rendering_class": klass,
                "working_gloss": EXPECTED_MEANINGS[surface], "working_render": render_text(surface, klass),
                "reader_exact": int(seen[surface] <= min(direct_caps)),
                "split_normalized": int(seen[surface] <= min(span_caps)),
                "all_three_present": cross[locus]["all_three_present"],
                "all_present_exact": cross[locus]["all_present_exact"],
                "zl3b_line": cross[locus]["zl3b_clean"], "it2a_line": cross[locus]["it2a_clean"],
                "rf1b_line": cross[locus]["rf1b_clean"],
            })
    return records, by_line


def metric_rows(coverage, complete, one, glossary) -> dict[str, int]:
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


def without(row: dict[str, str], *keys: str) -> dict[str, str]:
    return {key: value for key, value in row.items() if key not in keys}


def main() -> int:
    checks: list[str] = []
    check_results: list[dict[str, object]] = []
    failures: list[str] = []

    def check(name: str, condition: bool) -> None:
        passed = bool(condition)
        checks.append(name)
        check_results.append({"name": name, "passed": passed})
        if not passed:
            failures.append(name)

    inherited_allow = ROOT / G661 / "artifacts/PAGE_ALLOWLIST.tsv"
    page_rows = read_tsv(inherited_allow)
    pages = {row["page"] for row in page_rows}
    check("allowlist_179", len(page_rows) == len(pages) == 179)
    check("allowlist_forbidden_absent", "f1r" not in pages and not any(page.startswith("f84") for page in pages))
    check("allowlist_inherited_bytes", (ART / "PAGE_ALLOWLIST.tsv").read_bytes() == inherited_allow.read_bytes())

    tokens, token_stats = guarded_query(
        TOKENS, pages, "page,locus,token_index,eva,kind,section,language,hand"
    )
    cross, cross_stats = guarded_query(
        CROSS, pages, "page,locus,all_three_present,all_present_exact,zl3b_clean,it2a_clean,rf1b_clean"
    )
    check("guarded_token_census", len(tokens) == 32339 and token_stats.get("selected") == 32339)
    check("guarded_cross_census", len(cross) == 4137 and cross_stats.get("selected") == 4137)
    records, by_line = source_records(tokens, cross)
    cross_by_locus = {row["locus"]: row for row in cross}
    check("cross_unique_loci", len(cross_by_locus) == 4137)
    check("source_physical_lines", len(by_line) == 4128)
    check("source_zl_matches_cross", all(
        locus in cross_by_locus and " ".join(row["eva"] for row in line) == cross_by_locus[locus]["zl3b_clean"]
        for locus, line in by_line.items()
    ))
    check("source_target_order_constants", len(TARGET_ORDER) == len(TARGETS) == 76 and set(EXPECTED_COUNTS) == TARGETS)
    check("source_target_positions_861", len(records) == 861)
    check("source_target_counts", dict(Counter(str(row["surface"]) for row in records)) == EXPECTED_COUNTS)
    check("source_target_lines_776", len({str(row["locus"]) for row in records}) == 776)
    check("source_target_pages_160", len({str(row["page"]) for row in records}) == 160)
    check("source_reader_exact_667", sum(int(row["reader_exact"]) for row in records) == 667)
    check("source_split_normalized_682", sum(int(row["split_normalized"]) for row in records) == 682)
    source_render_counts = dict(Counter(str(row["rendering_class"]) for row in records))
    check("source_rendering_classes", source_render_counts == EXPECTED_RENDER_CLASSES)
    source_context_map = {
        (klass, surface): (
            len(members), {str(row["working_render"]) for row in members},
        )
        for klass, surface in {(str(row["rendering_class"]), str(row["surface"])) for row in records}
        if klass != "EXACT_WHOLE"
        for members in [[row for row in records if row["rendering_class"] == klass and row["surface"] == surface]]
    }
    check("source_context_card_map", source_context_map == {
        key: (count, {rendering}) for key, (count, rendering) in EXPECTED_CONTEXT_CARDS.items()
    })

    decision = read_tsv(ART / "TARGET_DECISION_DECK.tsv")
    accepted = read_tsv(ART / "ACCEPTED_WHOLE_SURFACE_DEFAULTS.tsv")
    context_cards = read_tsv(ART / "CONTEXT_RENDERING_CARDS.tsv")
    architecture = read_tsv(ART / "CARD_ARCHITECTURE_SUMMARY.tsv")
    audit = read_tsv(ART / "ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv")
    reader = read_tsv(ART / "READER_VARIANT_AUDIT.tsv")
    family = read_tsv(ART / "FAMILY_COMPOSITION_ATLAS.tsv")
    frontier = read_tsv(ART / "FRONTIER_76_COMPLETIONS.tsv")
    target_lines = read_tsv(ART / "TARGET_LINE_TRANSLATIONS.tsv")
    rounds = read_tsv(ART / "ROUND_COVERAGE_COUNTS.tsv")
    new_complete = read_tsv(ART / "NEWLY_COMPLETED_LINES.tsv")
    new_one = read_tsv(ART / "NEWLY_EXPOSED_ONE_HOLE_LINES.tsv")
    glossary = read_tsv(ART / "V39_WORKING_TOKEN_GLOSSARY.tsv")
    dictionary = read_tsv(ART / "WORKING_DICTIONARY_V39.tsv")
    coverage = read_tsv(ART / "ALL_LINE_CONCRETE_COVERAGE_V39.tsv")
    complete = read_tsv(ART / "COMPLETE_PASSAGES_V39.tsv")
    one = read_tsv(ART / "ONE_UNKNOWN_PASSAGES_V39.tsv")

    base_glossary = read_tsv(ROOT / G661 / "artifacts/V38_WORKING_TOKEN_GLOSSARY.tsv")
    base_dictionary = read_tsv(ROOT / G661 / "artifacts/WORKING_DICTIONARY_V38.tsv")
    base_coverage = read_tsv(ROOT / G661 / "artifacts/ALL_LINE_CONCRETE_COVERAGE_V38.tsv")
    base_complete = read_tsv(ROOT / G661 / "artifacts/COMPLETE_PASSAGES_V38.tsv")
    base_one = read_tsv(ROOT / G661 / "artifacts/ONE_UNKNOWN_PASSAGES_V38.tsv")
    source_frontier = read_tsv(ROOT / G661 / "artifacts/NEWLY_EXPOSED_ONE_HOLE_LINES.tsv")

    records_by_surface: dict[str, list[dict[str, object]]] = defaultdict(list)
    for record in records:
        records_by_surface[str(record["surface"])].append(record)
    decision_by_surface = {row["surface"]: row for row in decision}
    check("decision_76_order", len(decision) == 76 and tuple(row["surface"] for row in decision) == TARGET_ORDER)
    check("decision_ids", [row["decision_id"] for row in decision] == [f"G662-D{i:02d}" for i in range(1, 77)])
    check("decision_meanings", {row["surface"]: row["working_default_de"] for row in decision} == EXPECTED_MEANINGS)
    check("decision_card_types", all(row["card_type"] == card_type(row["surface"]) for row in decision))
    check("decision_source_statistics", all(
        int(row["occurrences"]) == len(records_by_surface[row["surface"]])
        and int(row["lines"]) == len({str(item["locus"]) for item in records_by_surface[row["surface"]]})
        and int(row["pages"]) == len({str(item["page"]) for item in records_by_surface[row["surface"]]})
        and int(row["reader_exact_occurrences"]) == sum(int(item["reader_exact"]) for item in records_by_surface[row["surface"]])
        and int(row["split_normalized_occurrences"]) == sum(int(item["split_normalized"]) for item in records_by_surface[row["surface"]])
        and row["rendering_classes"] == "|".join(sorted({str(item["rendering_class"]) for item in records_by_surface[row["surface"]]}))
        for row in decision
    ))
    check("decision_concrete_nonempty", all(
        row["composition"] and row["strongest_rival_de"] and not OPEN.search(row["working_default_de"])
        and not GENERIC_FILLER.search(row["working_default_de"]) for row in decision
    ))
    check("decision_status_exact", all(row["status"] == "ACCEPT_V39_REPLACEABLE_NO_SUBSTRING_EXPORT" for row in decision))
    check("accepted_76_order", len(accepted) == 76 and tuple(row["surface"] for row in accepted) == TARGET_ORDER)
    check("accepted_matches_decisions", all(
        row["working_meaning_de"] == decision_by_surface[row["surface"]]["working_default_de"]
        and row["composition"] == decision_by_surface[row["surface"]]["composition"]
        and row["strongest_rival_de"] == decision_by_surface[row["surface"]]["strongest_rival_de"]
        and row["card_type"] == decision_by_surface[row["surface"]]["card_type"]
        and row["strength"] == decision_by_surface[row["surface"]]["strength"]
        and row["occurrences"] == decision_by_surface[row["surface"]]["occurrences"]
        for row in accepted
    ))
    check("accepted_exact_scope", all(
        row["scope"] == "EXACT_WHITESPACE_DELIMITED_WHOLE"
        and row["status"] == "ACCEPT_V39_REPLACEABLE_NO_SUBSTRING_EXPORT" for row in accepted
    ))

    check("architecture_four_rows", [row["card_type"] for row in architecture] == list(EXPECTED_ARCHITECTURE))
    architecture_ok = True
    for row in architecture:
        types, positions, surfaces = EXPECTED_ARCHITECTURE[row["card_type"]]
        ordered = [surface for surface in TARGET_ORDER if surface in surfaces]
        architecture_ok &= (
            int(row["surface_types"]) == types and int(row["positions"]) == positions
            and row["surfaces"].split("|") == ordered
            and sum(EXPECTED_COUNTS[surface] for surface in ordered) == positions
            and row["dispatch_rule"] == "exact whole only; component analysis is explanatory, never automatic substring export"
        )
    check("architecture_61_3_4_8_and_741_73_36_11", architecture_ok)

    actual_context = {
        (row["rendering_class"], row["surface"]): (int(row["occurrences"]), row["working_render_de"])
        for row in context_cards
    }
    check("context_cards_31", len(context_cards) == 31 and len(actual_context) == 31)
    check("context_card_ids", [row["card_id"] for row in context_cards] == [f"G662-C{i:02d}" for i in range(1, 32)])
    check("context_cards_exact", actual_context == EXPECTED_CONTEXT_CARDS)
    check("context_cards_source_total", sum(int(row["occurrences"]) for row in context_cards) == 427)
    check("context_cards_exact_dispatch", all(
        row["selection_rule"] == "exact token equality; position only where named in the rendering class"
        and row["semantic_effect"] == "practical German rendering; exact whole default and source surface remain visible"
        for row in context_cards
    ))

    source_by_key = {(str(row["locus"]), int(row["token_index"])): row for row in records}
    check("audit_861_unique", len(audit) == 861 and len({(row["locus"], row["token_index"]) for row in audit}) == 861)
    check("audit_occurrence_ids", [row["occurrence_id"] for row in audit] == [f"G662-T{i:04d}" for i in range(1, 862)])
    audit_match = True
    for row in audit:
        source = source_by_key.get((row["locus"], int(row["token_index"])))
        if source is None:
            audit_match = False
            continue
        expected_state = "KNOWN_EXACT_WHOLE" if int(source["reader_exact"]) else "READER_BOUNDARY_UNSTABLE"
        audit_match &= all((
            row["occurrence_id"] == source["occurrence_id"], row["page"] == source["page"],
            int(row["ordinal"]) == source["ordinal"], int(row["line_length"]) == source["line_length"],
            row["surface"] == source["surface"], row["token_kind"] == source["kind"],
            row["position"] == source["position"], row["section"] == source["section"],
            row["language"] == source["language"], row["hand"] == source["hand"],
            row["card_type"] == source["card_type"],
            row["scope_mode"] == "EXACT_WHITESPACE_WHOLE_WITH_OPTIONAL_PRACTICAL_RENDER",
            row["rendering_class"] == source["rendering_class"], row["left_surface"] == source["left"],
            row["right_surface"] == source["right"], row["working_gloss_de"] == source["working_gloss"],
            row["working_render_de"] == source["working_render"],
            int(row["reader_exact"]) == source["reader_exact"],
            int(row["split_normalized"]) == source["split_normalized"],
            row["all_three_present"] == source["all_three_present"],
            row["all_present_exact"] == source["all_present_exact"],
            row["zl3b_line"] == source["zl3b_line"], row["it2a_line"] == source["it2a_line"],
            row["rf1b_line"] == source["rf1b_line"], row["v38_gloss_de"] == f"[{row['surface']}:?]",
            row["v39_gloss_de"] == EXPECTED_MEANINGS[row["surface"]],
            row["v38_scope_state"] == "UNKNOWN_SURFACE", row["v39_scope_state"] == expected_state,
            int(row["exact_surface_dispatch"]) == 1, int(row["substring_dispatch"]) == 0,
        ))
    check("audit_full_source_match", audit_match and len(source_by_key) == len(audit))
    check("audit_all_concrete", all(
        not OPEN.search(row["v39_gloss_de"]) and not GENERIC_FILLER.search(row["v39_gloss_de"])
        and not GENERIC_FILLER.search(row["v39_working_translation_de"]) for row in audit
    ))
    check("audit_exact_whole_not_substring", all(
        int(row["exact_surface_dispatch"]) == 1 and int(row["substring_dispatch"]) == 0 for row in audit
    ))

    reader_by_id = {row["occurrence_id"]: row for row in reader}
    check("reader_861_unique", len(reader) == len(reader_by_id) == 861)
    check("reader_totals", sum(int(row["reader_exact"]) for row in reader) == 667 and sum(int(row["split_normalized"]) for row in reader) == 682)
    check("reader_matches_source", all(
        row["occurrence_id"] in reader_by_id
        and reader_by_id[str(row["occurrence_id"])]["page"] == str(row["page"])
        and reader_by_id[str(row["occurrence_id"])]["locus"] == str(row["locus"])
        and int(reader_by_id[str(row["occurrence_id"])]["ordinal"]) == int(row["ordinal"])
        and reader_by_id[str(row["occurrence_id"])]["surface"] == str(row["surface"])
        and reader_by_id[str(row["occurrence_id"])]["position"] == str(row["position"])
        and int(reader_by_id[str(row["occurrence_id"])]["reader_exact"]) == int(row["reader_exact"])
        and int(reader_by_id[str(row["occurrence_id"])]["split_normalized"]) == int(row["split_normalized"])
        and reader_by_id[str(row["occurrence_id"])]["zl3b_line"] == str(row["zl3b_line"])
        and reader_by_id[str(row["occurrence_id"])]["it2a_line"] == str(row["it2a_line"])
        and reader_by_id[str(row["occurrence_id"])]["rf1b_line"] == str(row["rf1b_line"])
        for row in records
    ))
    check("reader_claim_boundary", all("does not identify plaintext" in row["claim_boundary"] for row in reader))

    check("family_76_unique", len(family) == 76 and {row["surface"] for row in family} == TARGETS)
    check("family_source_counts", all(
        int(row["occurrences"]) == len(records_by_surface[row["surface"]])
        and int(row["lines"]) == len({str(item["locus"]) for item in records_by_surface[row["surface"]]})
        and int(row["pages"]) == len({str(item["page"]) for item in records_by_surface[row["surface"]]})
        and row["card_type"] == card_type(row["surface"])
        and row["working_default_de"] == EXPECTED_MEANINGS[row["surface"]]
        for row in family
    ))
    check("family_claim_scope", all(
        row["claim_scope"] == "exact whole; composition predicts relatives only as an explicit future proposal"
        for row in family
    ))

    base_by_locus = {row["locus"]: row for row in base_coverage}
    final_by_locus = {row["locus"]: row for row in coverage}
    target_keys = {(str(row["locus"]), int(row["ordinal"])) for row in records}
    record_by_ordinal = {(str(row["locus"]), int(row["ordinal"])): row for row in records}
    check("coverage_loci_preserved", len(base_by_locus) == len(final_by_locus) == 4128 and set(base_by_locus) == set(final_by_locus))
    projection_before: list[tuple[object, ...]] = []
    projection_after: list[tuple[object, ...]] = []
    coverage_exact = True
    target_changes = 0
    invariant_fields = (
        "page", "locus", "section", "language", "hand", "token_count", "reader_exact_tokens",
        "split_normalized_tokens", "all_three_present", "all_present_exact", "zl3b_line",
    )
    for locus, before in base_by_locus.items():
        after = final_by_locus[locus]
        coverage_exact &= all(before[field] == after[field] for field in invariant_fields)
        before_glosses, after_glosses = split_pipe(before["token_glosses_de"]), split_pipe(after["token_glosses_de"])
        before_sources, after_sources = split_pipe(before["gloss_sources"]), split_pipe(after["gloss_sources"])
        before_states, after_states = split_pipe(before["scope_states"]), split_pipe(after["scope_states"])
        coverage_exact &= len(before_glosses) == len(after_glosses) == int(before["token_count"])
        local = 0
        for ordinal in range(1, len(before_glosses) + 1):
            key = locus, ordinal
            if key in target_keys:
                target_changes += 1
                local += 1
                record = record_by_ordinal[key]
                expected_state = "KNOWN_EXACT_WHOLE" if int(record["reader_exact"]) else "READER_BOUNDARY_UNSTABLE"
                coverage_exact &= (
                    before_glosses[ordinal - 1] == f"[{record['surface']}:?]"
                    and before_sources[ordinal - 1] == "OPEN" and before_states[ordinal - 1] == "UNKNOWN_SURFACE"
                    and after_glosses[ordinal - 1] == EXPECTED_MEANINGS[str(record["surface"])]
                    and after_sources[ordinal - 1] == f"GDT662:EXACT_WHOLE:{record['surface']}"
                    and after_states[ordinal - 1] == expected_state
                )
            else:
                token_surface = by_line[locus][ordinal - 1]["eva"]
                projection_before.append((locus, ordinal, token_surface, before_glosses[ordinal - 1], before_sources[ordinal - 1], before_states[ordinal - 1]))
                projection_after.append((locus, ordinal, token_surface, after_glosses[ordinal - 1], after_sources[ordinal - 1], after_states[ordinal - 1]))
        before_pairs = list(zip(split_compact(before["unknown_ordinals"]), split_compact(before["unknown_surfaces"])))
        expected_pairs = [pair for pair in before_pairs if (locus, int(pair[0])) not in target_keys]
        after_pairs = list(zip(split_compact(after["unknown_ordinals"]), split_compact(after["unknown_surfaces"])))
        coverage_exact &= all((
            int(after["known_tokens"]) == int(before["known_tokens"]) + local,
            int(after["unknown_tokens"]) == int(before["unknown_tokens"]) - local,
            after_pairs == expected_pairs,
            int(after["context_licensed_tokens"]) == after_states.count("KNOWN_CONTEXT_LICENSED"),
            int(after["ambiguous_tokens"]) == after_states.count("AMBIGUOUS_ACTIVE_RIVAL"),
            int(after["reader_unstable_tokens"]) == after_states.count("READER_BOUNDARY_UNSTABLE"),
            after["coverage_fraction"] == f"{int(after['known_tokens']) / int(after['token_count']):.6f}",
        ))
    check("coverage_target_changes_861", target_changes == 861)
    check("coverage_v38_to_v39_exact_arithmetic", coverage_exact)
    check("coverage_non_target_projection_byte_fields", projection_before == projection_after and len(projection_before) == 31478)
    non_target_sha = canonical_hash(projection_before)
    check("coverage_non_target_hash_constant", non_target_sha == "f846bb6f5a3d4b7b5716b9efa7871594e0e4406baf23ed073e9df647e3526eea")
    check("base_metrics", metric_rows(base_coverage, base_complete, base_one, base_glossary) == BASE_METRICS)
    check("final_metrics", metric_rows(coverage, complete, one, glossary) == FINAL_METRICS)

    derived_complete = {
        row["locus"]: int(int(row["ambiguous_tokens"]) == 0 and int(row["reader_unstable_tokens"]) == 0 and int(row["all_present_exact"]) == 1)
        for row in coverage if int(row["unknown_tokens"]) == 0 and int(row["token_count"]) >= 2
    }
    derived_one = {
        row["locus"]: int(int(row["ambiguous_tokens"]) == 0 and int(row["reader_unstable_tokens"]) == 0 and int(row["all_present_exact"]) == 1)
        for row in coverage if int(row["unknown_tokens"]) == 1 and int(row["known_tokens"]) >= 1
    }
    check("complete_derived", {row["locus"]: int(row["strict_complete"]) for row in complete} == derived_complete)
    check("one_unknown_derived", {row["locus"]: int(row["strict_eligible"]) for row in one} == derived_one)
    base_complete_loci = {row["locus"] for row in base_complete}
    base_one_loci = {row["locus"] for row in base_one}
    expected_new_complete = set(derived_complete) - base_complete_loci
    expected_new_one = set(derived_one) - base_one_loci
    check("new_complete_98", len(new_complete) == 98 and {row["locus"] for row in new_complete} == expected_new_complete)
    check("new_one_105", len(new_one) == 105 and {row["locus"] for row in new_one} == expected_new_one)
    complete_by_locus = {row["locus"]: row for row in complete}
    one_by_locus = {row["locus"]: row for row in one}
    check("new_complete_rows_exact", all(
        without(row, "rank") == without(complete_by_locus[row["locus"]], "rank") for row in new_complete
    ))
    check("new_one_rows_exact", all(
        row["base_unknown_tokens"] == base_by_locus[row["locus"]]["unknown_tokens"]
        and without(row, "rank", "base_unknown_tokens") == without(one_by_locus[row["locus"]], "rank")
        for row in new_one
    ))
    check("complete_no_open_or_filler", all(
        not OPEN.search(row["working_translation_de"]) and not GENERIC_FILLER.search(row["working_translation_de"])
        for row in complete
    ))

    base_glossary_map = {row["surface"]: row for row in base_glossary}
    glossary_map = {row["surface"]: row for row in glossary}
    check("glossary_632_unique", len(glossary) == len(glossary_map) == 632)
    check("glossary_base_unchanged", all(glossary_map.get(surface) == row for surface, row in base_glossary_map.items()))
    check("glossary_exact_76_new", set(glossary_map) - set(base_glossary_map) == TARGETS)
    check("glossary_new_exact_values", all(
        glossary_map[surface]["working_meaning_de"] == EXPECTED_MEANINGS[surface]
        and glossary_map[surface]["source"] == "GDT662:EXACT_WHOLE"
        and glossary_map[surface]["scope_state"] == "KNOWN_EXACT_WHOLE"
        and glossary_map[surface]["priority"] == "225" for surface in TARGETS
    ))
    check("function_word_defaults", all((
        glossary_map["a"]["working_meaning_de"] == "je, zu gleichen Teilen",
        glossary_map["ey"]["working_meaning_de"] == "anschließend",
        glossary_map["qo"]["working_meaning_de"] == "nehmen",
    )))

    check("dictionary_785", len(base_dictionary) == 678 and len(dictionary) == 785)
    check("dictionary_base_prefix", dictionary[:678] == base_dictionary)
    added_dictionary = dictionary[678:]
    exact_dictionary = [row for row in added_dictionary if row["status"] == "NEW_V39_PROVISIONAL_CONCRETE_RECIPE_DEFAULT"]
    render_dictionary = [row for row in added_dictionary if row["kind"] == "PRACTICAL_RENDERING_CARD"]
    check("dictionary_76_exact_plus_31_render", len(exact_dictionary) == 76 and len(render_dictionary) == 31 and len(added_dictionary) == 107)
    check("dictionary_exact_entries", {
        row["entry"] for row in exact_dictionary
    } == {f"{surface}@GDT662_EXACT_WHOLE" for surface in TARGETS})
    check("dictionary_exact_values", all(
        row["kind"] == card_type(row["entry"].split("@", 1)[0])
        and row["working_meaning_de"] == EXPECTED_MEANINGS[row["entry"].split("@", 1)[0]]
        and row["context_rule"] == "only the exact whitespace-delimited surface; no substring inheritance"
        for row in exact_dictionary
    ))
    check("dictionary_render_entries", {
        (row["composition"], row["entry"].split("@", 1)[0]): row["working_meaning_de"]
        for row in render_dictionary
    } == {key: value[1] for key, value in EXPECTED_CONTEXT_CARDS.items()})
    check("dictionary_render_scope", all(
        row["context_rule"] == "exact token equality; position only where named in the rendering class"
        and row["status"] == "NEW_V39_RENDER_OF_EXACT_WHOLE" for row in render_dictionary
    ))

    check("round_two_rows", len(rounds) == 2 and [row["version"] for row in rounds] == ["V38", "V39"])
    round_metrics = [{key: int(row[key]) for key in FINAL_METRICS} for row in rounds]
    check("round_base_metrics", round_metrics[0] == BASE_METRICS and rounds[0]["dictionary_entries"] == "678")
    check("round_final_metrics", round_metrics[1] == FINAL_METRICS and rounds[1]["dictionary_entries"] == "785")
    check("round_added_cards", rounds[1]["added_cards"] == "76_EXACT_WHOLES+31_RENDERINGS")

    affected_loci = sorted({str(row["locus"]) for row in records})
    target_line_map = {row["locus"]: row for row in target_lines}
    check("target_lines_776_unique", len(target_lines) == len(target_line_map) == 776 and list(target_line_map) == affected_loci)
    target_line_exact = True
    for locus in affected_loci:
        row = target_line_map[locus]
        members = [record for record in records if record["locus"] == locus]
        before, after = base_by_locus[locus], final_by_locus[locus]
        target_line_exact &= all((
            row["page"] == after["page"], row["section"] == after["section"],
            int(row["target_occurrences"]) == len(members),
            row["target_ordinals"] == "|".join(str(member["ordinal"]) for member in members),
            row["target_surfaces"] == "|".join(str(member["surface"]) for member in members),
            row["rendering_classes"] == "|".join(str(member["rendering_class"]) for member in members),
            row["zl3b_line"] == after["zl3b_line"], row["v38_token_glosses_de"] == before["token_glosses_de"],
            row["v39_token_glosses_de"] == after["token_glosses_de"],
            int(row["v38_unknown_tokens"]) == int(before["unknown_tokens"]),
            int(row["v39_unknown_tokens"]) == int(after["unknown_tokens"]),
            int(row["v39_complete"]) == int(int(after["unknown_tokens"]) == 0),
        ))
    check("target_lines_source_projection", target_line_exact)
    check("target_lines_audit_translation", all(
        row["v39_working_translation_de"] == target_line_map[row["locus"]]["v39_working_translation_de"]
        for row in audit
    ))
    check("target_lines_no_generic_filler", all(
        not GENERIC_FILLER.search(row["v39_working_translation_de"]) for row in target_lines
    ))

    # Concrete renderer regressions, including all folds added after the first
    # GDT662 draft.  These are checked against independently reconstructed token
    # contexts, not merely against the renderer-card table.
    translations = {locus: row["v39_working_translation_de"] for locus, row in target_line_map.items()}
    check("render_qokol_grade_ii", "erhitze bis Grad II" in translations["f102r1.5"])
    check("render_qokol_double_grade_iii", "erhitze zweimal bis Grad III" in translations["f104v.11"])
    check("render_qokol_grade_iv", "erhitze bis Grad IV" in translations["f53v.4"])
    check("render_qokol_non_grade_double", "erhitze zweimal Folgendes:" in translations["f88r.27"])
    check("render_qol_pair_direction", all(
        phrase in translations["f75v.40"] for phrase in ("gib Vorstehendes hinzu", "gib Folgendes hinzu:")
    ) and "gib zweimal" not in translations["f75v.40"])
    check("render_qol_direction_collision", all(
        phrase in translations["f77r.38"] for phrase in ("gib Folgendes hinzu:", "gib Vorstehendes hinzu")
    ))
    check("render_qo_terminal_take", translations["f13v.4"].endswith("nimm Vorstehendes."))
    check("render_qo_y_fold", "nimm hierzu Folgendes:" in translations["f79r.3"])
    check("render_oly_finish", translations["f103v.45"].endswith("seihe Vorstehendes ab."))
    check("render_chl_finish", translations["f78r.19"].endswith("trockne."))
    check("render_chl_previous", "trockne die vorstehende heiße Drogenfraktion I" in translations["f8r.17"])
    check("render_a_equal_parts", "je zu gleichen Teilen" in translations["f113v.41"])
    check("render_ey_sequence", "anschließend:" in translations["f102v1.12"] and "mische" not in translations["f102v1.12"])
    check("render_ey_bos_mix", translations["f80r.34"].startswith("mische Folgendes:"))
    check("render_ey_eos_mix", translations["f47r.7"].endswith("mische Vorstehendes."))
    check("render_ey_between_materials", "mische Vorstehendes mit Folgendem:" in translations["f82r.33"])
    check("render_qodaiin_pair_scope", all(
        phrase in translations["f104r.4"]
        for phrase in ("Vorstehendes: Qualitätsgrad III", "Folgendes: Qualitätsgrad III")
    ))
    check("render_chee_ol_bound", "vollständig getrocknetes Drogenmaterial" in translations["f77r.43"])
    check("render_action_texts_present", all(
        str(record["working_render"]).rstrip(".") in translations[str(record["locus"])]
        for record in records
        if record["rendering_class"] in {"PRACTICAL_ACTION", "Y_ENTRY_COMMAND"}
    ))
    source_grade_folds_ok = True
    source_qol_pairs_ok = True
    source_qo_y_folds_ok = True
    for locus, line in by_line.items():
        if locus not in target_line_map:
            continue
        words = [token["eva"] for token in line]
        text = translations[locus]
        for index in range(len(words) - 1):
            if words[index] == "qokol" and words[index + 1] in GRADE_AFTER_QOKOL:
                grade = GRADE_AFTER_QOKOL[words[index + 1]]
                phrase = ("erhitze zweimal" if index and words[index - 1] == "qokol" else "erhitze") + f" bis Grad {grade}"
                source_grade_folds_ok &= phrase in text
            if words[index] == words[index + 1] == "qol":
                source_qol_pairs_ok &= (
                    "gib Vorstehendes hinzu" in text and "gib Folgendes hinzu:" in text
                    and "gib zweimal" not in text
                )
            if words[index] == "qo" and words[index + 1] == "y":
                source_qo_y_folds_ok &= "nimm hierzu Folgendes:" in text
    check("all_source_qokol_grade_folds", source_grade_folds_ok)
    check("all_source_qol_pair_directions", source_qol_pairs_ok)
    check("all_source_qo_y_folds", source_qo_y_folds_ok)

    check("source_frontier_78", len(source_frontier) == 78 and len({row["unknown_surface"] for row in source_frontier}) == 76)
    check("frontier_78", len(frontier) == 78)
    frontier_exact = True
    for source, row in zip(source_frontier, frontier):
        surface = source["unknown_surface"]
        pos = position(int(source["unknown_ordinal"]), int(source["token_count"]))
        expected_render = render_text(surface, rendering_class(surface, pos, source["previous"], source["following"]))
        frontier_exact &= all((
            row["rank"] == source["rank"], row["page"] == source["page"], row["locus"] == source["locus"],
            row["surface"] == surface, row["working_default_de"] == EXPECTED_MEANINGS[surface],
            row["practical_render_de"] == expected_render, row["card_type"] == card_type(surface),
            row["composition"] == decision_by_surface[surface]["composition"],
            row["strongest_rival_de"] == decision_by_surface[surface]["strongest_rival_de"],
            row["strength"] == decision_by_surface[surface]["strength"], row["zl3b_line"] == source["zl3b_line"],
            row["v38_translation_de"] == source["proposed_complete_translation_de"],
            row["v39_translation_de"] == translations[row["locus"]],
            row["status"] == "COMPLETE_WITH_PROVISIONAL_CONCRETE_DEFAULT",
        ))
    check("frontier_full_source_match", frontier_exact)
    check("frontier_all_concrete", all(
        not OPEN.search(row["v39_translation_de"]) and not GENERIC_FILLER.search(row["v39_translation_de"])
        for row in frontier
    ))

    result = json.loads((ART / "RESULT.json").read_text(encoding="utf-8"))
    check("result_status", result.get("status") == "PASS_861_TARGET_POSITIONS__V39_MIXED_RECIPE_REGISTER")
    check("result_schema", result.get("schema") == "GDT662_SEVENTY_SIX_RESIDUAL_FAMILY_COMPLETION_RESULT_V1")
    check("result_content_hash", result.get("content_sha256") == canonical_hash({key: value for key, value in result.items() if key != "content_sha256"}))
    check("result_target_dimensions", all((
        result["targets"]["surface_types"] == 76, result["targets"]["exact_whole_surfaces"] == 76,
        result["targets"]["positions"] == 861, result["targets"]["lines"] == 776,
        result["targets"]["pages"] == 160, result["targets"]["reader_exact_positions"] == 667,
        result["targets"]["split_normalized_positions"] == 682,
        result["targets"]["all_positions_concrete"] is True,
        result["targets"]["substring_dispatch_positions"] == 0,
    )))
    check("result_target_counts", result["targets"]["surface_counts"] == EXPECTED_COUNTS)
    check("result_render_classes", result["targets"]["rendering_classes"] == EXPECTED_RENDER_CLASSES)
    check("result_architecture", result["architecture"] == {
        kind: {"surface_types": values[0], "positions": values[1]} for kind, values in EXPECTED_ARCHITECTURE.items()
    })
    check("result_coverage_metrics", result["coverage"]["base"] == BASE_METRICS and result["coverage"]["final"] == FINAL_METRICS)
    check("result_coverage_deltas", all((
        result["coverage"]["affected_lines"] == 776,
        result["coverage"]["newly_completed_lines"] == 98,
        result["coverage"]["newly_exposed_one_hole_lines"] == 105,
        result["coverage"]["non_target_token_positions_unchanged"] == 31478,
        result["coverage"]["non_target_exactly_unchanged"] is True,
        result["coverage"]["non_target_before_sha256"] == non_target_sha,
        result["coverage"]["non_target_after_sha256"] == non_target_sha,
    )))
    check("result_delta_loci", all((
        result["coverage"]["newly_completed_loci"] == sorted(expected_new_complete),
        result["coverage"]["newly_exposed_one_hole_loci"] == sorted(expected_new_one),
    )))
    check("result_dictionary", result["working_dictionary"] == {
        "v38_entries": 678, "v39_entries": 785, "added_exact_whole_entries": 76,
        "added_rendering_entries": 31, "v38_glossary_surfaces": 556, "v39_glossary_surfaces": 632,
    })
    check("result_frontier", result["frontier"] == {"source_rows": 78, "completed_rows": 78, "unfilled_target_slots": 0})
    check("result_guard", all((
        result["guard"]["allowed_pages"] == 179, result["guard"]["f1r"] == "EXCLUDED_BY_EXACT_ALLOWLIST",
        result["guard"]["f84"] == "FORBIDDEN", result["guard"]["f84r"] == "FORBIDDEN",
        result["guard"]["new_pages"] == 0, result["guard"]["new_images"] == 0,
        result["guard"]["token_query"] == {
            "selected": 32339, "skipped_forbidden": 709, "skipped_not_allowed": 5940,
        },
        result["guard"]["cross_query"] == {
            "selected": 4137, "skipped_forbidden": 98, "skipped_not_allowed": 1151,
        },
    )))
    expected_replay = [str(BASE / "artifacts" / name) for name in (*OUTPUT_NAMES, "RESULT.json")]
    check("result_replay_contract", result["determinism_contract"] == {
        "builder_supports_artifact_dir_cli": True,
        "exact_whole_dispatch_requires_token_equality": True,
        "replay_files": expected_replay,
    })
    output_hashes = result.get("outputs", {})
    check("result_output_hash_keys", set(output_hashes) == {str(BASE / "artifacts" / name) for name in OUTPUT_NAMES})
    check("result_output_hashes", all(
        output_hashes.get(str(BASE / "artifacts" / name)) == sha256(ART / name) for name in OUTPUT_NAMES
    ))
    input_hashes = result.get("inputs", {})
    check("result_input_hashes", bool(input_hashes) and all(
        (ROOT / path).is_file() and sha256(ROOT / path) == digest for path, digest in input_hashes.items()
    ))
    check("result_claim_boundary", all(fragment in result["claim_boundary"] for fragment in (
        "Exploratory replaceable", "No substring dispatch", "not confirmed plaintext", "f1r", "f84r",
    )))

    replay_ok = True
    replay_error = ""
    with tempfile.TemporaryDirectory(prefix="gdt662_validator_replay_") as directory:
        replay_dir = Path(directory)
        done = subprocess.run(
            [sys.executable, str(RUN), "--artifact-dir", str(replay_dir)],
            cwd=ROOT, text=True, capture_output=True, check=False,
        )
        if done.returncode:
            replay_ok = False
            replay_error = done.stderr or done.stdout
        else:
            for name in (*OUTPUT_NAMES, "RESULT.json"):
                if not (replay_dir / name).is_file() or (ART / name).read_bytes() != (replay_dir / name).read_bytes():
                    replay_ok = False
                    replay_error = f"byte replay mismatch: {name}"
                    break
    check("tempdir_byte_replay_all_19", replay_ok)

    status = f"PASS_{len(checks)}_INDEPENDENT_CHECKS" if not failures else f"FAIL_{len(failures)}_OF_{len(checks)}_CHECKS"
    checked_artifacts = [str(BASE / "artifacts" / name) for name in (*OUTPUT_NAMES, "RESULT.json")]
    validation_core = {
        "schema": "GDT662_INDEPENDENT_VALIDATION_V1",
        "experiment_id": "GDT662",
        "status": status,
        "checks_run": len(checks),
        "checks_passed": len(checks) - len(failures),
        "checks": check_results,
        "failures": failures,
        "source_summary": {
            "allowed_pages": len(pages),
            "guarded_tokens": len(tokens),
            "guarded_cross_rows": len(cross),
            "physical_lines": len(by_line),
            "target_surface_types": len(TARGETS),
            "target_positions": len(records),
            "target_lines": len({str(row["locus"]) for row in records}),
            "target_pages": len({str(row["page"]) for row in records}),
            "reader_exact_positions": sum(int(row["reader_exact"]) for row in records),
            "split_normalized_positions": sum(int(row["split_normalized"]) for row in records),
        },
        "architecture_summary": {
            kind: {"surface_types": values[0], "positions": values[1]}
            for kind, values in EXPECTED_ARCHITECTURE.items()
        },
        "coverage_summary": {
            "base": BASE_METRICS,
            "final": FINAL_METRICS,
            "non_target_positions": len(projection_before),
            "non_target_projection_sha256": non_target_sha,
            "newly_completed_lines": len(new_complete),
            "newly_exposed_one_hole_lines": len(new_one),
        },
        "frontier_summary": {
            "source_rows": len(source_frontier),
            "completed_rows": len(frontier),
            "concrete_rows": sum(not OPEN.search(row["v39_translation_de"]) for row in frontier),
            "unfilled_target_slots": sum(bool(OPEN.search(row["v39_translation_de"])) for row in frontier),
        },
        "replay_summary": {
            "builder_exit_zero": done.returncode == 0,
            "files_checked": len(checked_artifacts),
            "checked_artifacts": checked_artifacts,
            "byte_identical": replay_ok,
            "error_code": "NONE" if replay_ok else (
                replay_error if replay_error.startswith("byte replay mismatch:") else "BUILDER_SUBPROCESS_FAILED"
            ),
        },
        "validated_artifacts_sha256": {
            relative: sha256(ROOT / relative) for relative in checked_artifacts
        },
        "claim_boundary": (
            "Independent source-first validation of census, exact-whole dispatch, rendering, V38-to-V39 "
            "arithmetic, non-target preservation, frontier completion, hashes, and deterministic replay. "
            "A passing result validates the release mechanics and internal working-model contract; it does "
            "not establish Voynich plaintext, language, phonetics, ingredients, disease, or historical truth."
        ),
    }
    validation = {**validation_core, "content_sha256": canonical_hash(validation_core)}
    (ART / "VALIDATION.json").write_text(
        json.dumps(validation, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    if failures:
        print(status, file=sys.stderr)
        for name in failures:
            print(f"FAIL {name}", file=sys.stderr)
        if replay_error:
            print(replay_error, file=sys.stderr)
        return 1
    print(f"GDT662 validated: {status}; source=861/76; frontier=78/78; byte_replay=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
