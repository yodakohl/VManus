#!/usr/bin/env python3
"""Build GDT647: migrate the complete observed quality family to subdegree positions."""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Iterable

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE_REL = Path("experiments/yolo/gdt647_quality_subdegree_family_migration")
ART = ROOT / BASE_REL / "artifacts"
G646 = Path("experiments/yolo/gdt646_tcheey_surface_completion")
G646_RUN = G646 / "src/run.py"
G646_ALLOW = G646 / "artifacts/PAGE_ALLOWLIST.tsv"
G646_COVERAGE = G646 / "artifacts/ALL_LINE_CONCRETE_COVERAGE_V23.tsv"
G646_COMPLETE = G646 / "artifacts/COMPLETE_PASSAGES_V23.tsv"
G646_ONE = G646 / "artifacts/ONE_UNKNOWN_PASSAGES_V23.tsv"
G646_GLOSSARY = G646 / "artifacts/V23_EXACT_TOKEN_GLOSSARY.tsv"
G646_DICTIONARY = G646 / "artifacts/WORKING_DICTIONARY_V23.tsv"
G646_ATLAS = G646 / "artifacts/FORM_FAMILY_ATLAS.tsv"
G646_HISTORICAL = G646 / "artifacts/HISTORICAL_SUBDEGREE_COMPARATOR.tsv"
G646_RESULT = G646 / "artifacts/RESULT.json"
G646_REPORT = G646 / "REPORT.md"

spec = importlib.util.spec_from_file_location("gdt646_builder_for_gdt647", ROOT / G646_RUN)
if spec is None or spec.loader is None:
    raise RuntimeError("cannot load GDT646 builder")
g646 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g646)
g637 = g646.g637
TOKENS_REL = g646.TOKENS_REL
CROSS_REL = g646.CROSS_REL

STATUS = "PASS_107_OBSERVED_QUALITY_WHOLES__NO_SUFFIX_GLOBALIZATION"
COMPOUND_QUALITY = {
    ("k", "ch"): ("k+ch", "heiß und trocken", "heiß-trockener"),
    ("t", "ch"): ("t+ch", "kalt und trocken", "kalt-trockener"),
    ("k", "sh"): ("k+sh", "heiß und feucht", "heiß-feuchter"),
    ("t", "sh"): ("t+sh", "kalt und feucht", "kalt-feuchter"),
}
ENDING = {
    "y": ("y", "am Anfang des Grades"),
    "ey": ("e+y", "in der Mitte des Grades"),
    "eey": ("ee+y", "am Ende des Grades"),
    "dy": ("d+y", "am Anfang des Grades, abgeschlossen"),
    "edy": ("e+d+y", "in der Mitte des Grades, abgeschlossen"),
    "eedy": ("ee+d+y", "am Ende des Grades, abgeschlossen"),
}
ENDING_ORDER = tuple(ENDING)
EXPECTED_NULL = (
    "ksheedy", "tcheedy", "tsheedy",
    "okcheedy", "oksheey", "oksheedy", "otsheey", "otsheedy",
    "qoksheey", "qotsheey", "qotsheedy",
    "kdy", "tdy",
)
OUTPUT_NAMES = (
    "PAGE_ALLOWLIST.tsv", "FAMILY_MIGRATION_DECK.tsv", "NULL_CELL_HOLDS.tsv",
    "AXIS_SCOPE_BOUNDARY.tsv", "MANUAL_PASSAGE_REALITY_CHECK.tsv",
    "ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv", "READER_VARIANT_AUDIT.tsv",
    "AFFECTED_PASSAGES.tsv", "NEWLY_COMPLETED_LINES.tsv",
    "NEWLY_EXPOSED_ONE_HOLE_LINES.tsv", "ROUND_COVERAGE_COUNTS.tsv",
    "V24_EXACT_TOKEN_GLOSSARY.tsv", "ALL_LINE_CONCRETE_COVERAGE_V24.tsv",
    "COMPLETE_PASSAGES_V24.tsv", "ONE_UNKNOWN_PASSAGES_V24.tsv",
    "WORKING_DICTIONARY_V24.tsv",
)

MANUAL_PASSAGE_AUDIT = (
    ("f13v.5", "STRONG", "heiß am Anfang des dritten Grades",
     "Saubere Verbindung aus qoky-Subgradposition und unmittelbar folgendem daiin-Gradwert."),
    ("f35r.14", "STRONG", "kalt und trocken am Anfang des dritten Grades; dazwischen Drogenportion, Ansatz und Menge III",
     "qotchy und qotaiin teilen den sichtbaren qo+t-Kopf; der lokale Scope ist eng."),
    ("f32r.5", "STRONG", "Am Anfang des dritten Grades: kalt und trocken; heiß und trocken.",
     "Direkter k/t-Kontrast im gleichen qo- und y-Rahmen vor daiin."),
    ("f36v.13", "STRONG", "Am Anfang des Grades: heißer Ansatz; kalter Ansatz.",
     "oky und oty zeigen, dass der o-Rahmen die Positionsachse bewahrt."),
    ("f80r.18", "STRONG", "heiß im zweiten Grad; am Gradende heiß und abgeschlossen; erneut heiß im zweiten Grad",
     "Derselbe qo+k-Kopf trägt getrennt Gradnummer und Subgradposition."),
    ("f83r.36", "STRONG", "Feuchte vom Gradanfang bis zur Gradmitte; außerdem heiß am Gradanfang.",
     "Sichtbare shy→shey Anfang-Mitte-Folge, gefolgt von qoky."),
    ("f85r1.21", "STRONG", "In der Gradmitte abgeschlossen: kalter Ansatz und trockener Zustand; kalt im dritten Grad.",
     "otedy und chedy teilen e+d+y; qotaiin liefert getrennt den Gradwert."),
    ("f75v.51", "STRONG", "Heißer Ansatz am Gradende; Holzstoff.",
     "Kurze, widerspruchsfreie o+k+ee+y-Passage."),
    ("f79v.4", "STRONG_WITH_SCOPE", "Am Gradende, abgeschlossen: zweimal heiß. In der Gradmitte, abgeschlossen: trocken. Außerdem heiß am Gradanfang.",
     "Wiederholte Position wird einmal lokal gescopet statt tokenweise verdoppelt."),
    ("f29r.1", "SCOPE_COMPRESSION_REQUIRED", "Am Gradanfang: kalter Ansatz, trocken, kalt-trocken und kalt.",
     "Vier gleiche Positionsmarker sind als lokale Liste lesbar, tokenweise aber schlechte Prosa."),
    ("f49v.12", "MIXED_OLD_NEW_TERMS", "Am Gradanfang: kalt-trocken; danach Trockenansatz und heiß-trockene Zubereitung in noch alter Grundform-Terminologie.",
     "qotchy migriert; chokchy/choky sind umgestellte Ganzwörter außerhalb des Scopes."),
    ("f15v.4", "MIXED_OLD_NEW_TERMS", "heiß am Gradanfang neben heiß-trockener Zubereitung in alter Grundform-Terminologie",
     "Kein Gegenbeleg; choky darf hier aber nicht stillschweigend mitmigrieren."),
    ("f28v.8", "OWNER_SCOPE_OPEN", "trocken am Gradanfang; getrennt davon Grad-/Mengenwerte II und III",
     "Ohne gesicherten Eigentümer darf die Position nicht automatisch an einen Zahlenwert gebunden werden."),
    ("f114v.33", "HARD_WARNING", "Gradende-Werte neben qokeeedy und qokeeo mit noch offener, anderer E-Länge",
     "Schlimmste Mischzeile; EEE und terminales o bleiben ausdrücklich außerhalb der Achse."),
    ("f47v.4", "HARD_WARNING", "Gradend- und Gradanfangswerte; keechy bleibt offen",
     "EE steht in keechy vor CH und darf nicht zu kcheey umgeordnet werden."),
)

SCOPE_BOUNDARY = (
    ("INCLUDE", "A", "(empty|o|qo)+(k|t)+(ch|sh)+(y|ey|eey|dy|edy|eedy)",
     "Exakte qualitatskopfige Ganzoberflachen; o/qo bleiben gebunden."),
    ("INCLUDE", "B", "(ch|sh)+(y|ey|eey|dy|edy|eedy)",
     "Exakte Trocken-/Feucht-Ganzoberflachen."),
    ("INCLUDE", "C", "(k|t|ok|ot|qok|qot)+(y|ey|eey|dy|edy|eedy)",
     "Exakte Heiss-/Kalt-Ganzoberflachen; C hat keinen Feuchte-/Trocken-Slot."),
    ("EXCLUDE", "CTH", "cth/octh/qocth families",
     "Ohne sichtbaren Qualitatskopf ist unklar, wessen Gradposition bezeichnet wird."),
    ("EXCLUDE", "MATERIAL_HEADS", "p/s/r/l + y-family remainder",
     "Nacktes y wird nicht zu Gradanfang globalisiert; ly/soysar bleiben unverandert."),
    ("EXCLUDE", "REVERSED_COMPOUNDS", "choky/chokchy/shok* and analogues",
     "Andere Reihenfolge; braucht einen eigenen exact-whole-Audit."),
    ("EXCLUDE", "OTHER_LADDERS", "aN/oiin/air/al/ol/or",
     "Gradnummer, Zubereitungsform, Fraktion und Materialtrager bleiben getrennte Achsen."),
    ("EXCLUDE", "OVERLONG_OR_REORDERED", "qokeeedy/keechy/initial-y forms",
     "EEE, EE-vor-CH und initiales y sind nicht von der Dreierachse lizenziert."),
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: Iterable[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fields), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_hash(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def string_rows(rows: list[dict[str, object]]) -> list[dict[str, str]]:
    return [{str(key): str(value) for key, value in row.items()} for row in rows]


def split_pipe(value: object) -> list[str]:
    return str(value).split(" | ") if str(value) else []


def metrics(coverage, one_unknown, complete, glossary) -> dict[str, int]:
    return {
        "physical_lines": len(coverage),
        "known_token_positions": sum(int(row["known_tokens"]) for row in coverage),
        "unknown_token_positions": sum(int(row["unknown_tokens"]) for row in coverage),
        "complete_multi_token_lines": len(complete),
        "strict_complete_lines": sum(int(row["strict_complete"]) for row in complete),
        "one_unknown_lines": len(one_unknown),
        "strict_one_unknown_lines": sum(int(row["strict_eligible"]) for row in one_unknown),
        "exact_glossary_surfaces": len(glossary),
    }


def all_family_specs() -> list[dict[str, str]]:
    """Return the predeclared quality-headed whole-word lattice.

    The ending is interpreted only inside these exact heads.  In particular,
    this is not a rule for arbitrary words ending in y/ey/eey/dy/edy/eedy.
    """
    specs: list[dict[str, str]] = []
    for carrier, carrier_parse, family in (
        ("", "", "QUALITY_COMPOUND_DIRECT"),
        ("o", "o+", "QUALITY_COMPOUND_O_CARRIER"),
        ("qo", "qo+", "QUALITY_COMPOUND_QO_CARRIER"),
    ):
        for temperature in ("k", "t"):
            for moisture in ("ch", "sh"):
                head_parse, quality, adjective = COMPOUND_QUALITY[(temperature, moisture)]
                for ending in ENDING_ORDER:
                    tail_parse, position = ENDING[ending]
                    surface = f"{carrier}{temperature}{moisture}{ending}"
                    if carrier == "o":
                        meaning = f"{adjective} Ansatz {position}"
                    else:
                        meaning = f"{quality} {position}"
                    specs.append({
                        "surface": surface,
                        "composition": f"{carrier_parse}{head_parse}+{tail_parse}",
                        "working_meaning_de": meaning,
                        "family": family,
                    })
    for quality_head, quality, family in (
        ("ch", "trocken", "MOISTURE_QUALITY_DIRECT"),
        ("sh", "feucht", "MOISTURE_QUALITY_DIRECT"),
    ):
        for ending in ENDING_ORDER:
            tail_parse, position = ENDING[ending]
            specs.append({
                "surface": f"{quality_head}{ending}",
                "composition": f"{quality_head}+{tail_parse}",
                "working_meaning_de": f"{quality} {position}",
                "family": family,
            })
    for quality_head, head_parse, quality, family in (
        ("k", "k", "heiß", "TEMPERATURE_QUALITY_DIRECT"),
        ("t", "t", "kalt", "TEMPERATURE_QUALITY_DIRECT"),
        ("ok", "o+k", "heißer Ansatz", "TEMPERATURE_QUALITY_O_CARRIER"),
        ("ot", "o+t", "kalter Ansatz", "TEMPERATURE_QUALITY_O_CARRIER"),
        ("qok", "qo+k", "heiß", "TEMPERATURE_QUALITY_QO_CARRIER"),
        ("qot", "qo+t", "kalt", "TEMPERATURE_QUALITY_QO_CARRIER"),
    ):
        for ending in ENDING_ORDER:
            tail_parse, position = ENDING[ending]
            specs.append({
                "surface": f"{quality_head}{ending}",
                "composition": f"{head_parse}+{tail_parse}",
                "working_meaning_de": f"{quality} {position}",
                "family": family,
            })
    if len(specs) != 120 or len({row["surface"] for row in specs}) != 120:
        raise RuntimeError("quality-headed lattice construction drift")
    return specs


def family_specs(token_counts: Counter[str]) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    all_specs = all_family_specs()
    observed = [row for row in all_specs if token_counts[row["surface"]] > 0]
    absent = [row for row in all_specs if token_counts[row["surface"]] == 0]
    if len(observed) != 107:
        raise RuntimeError(f"observed quality-headed surface count changed: {len(observed)}")
    if tuple(row["surface"] for row in absent) != EXPECTED_NULL:
        raise RuntimeError(f"quality-headed null cells changed: {[row['surface'] for row in absent]!r}")
    return observed, absent


def dictionary_overlay(
    spec_row: dict[str, str], decision: str, occurrences: int, reader_exact: int,
) -> dict[str, object]:
    return {
        "entry": f"{spec_row['surface']}@GDT647_SUBDEGREE_WHOLE",
        "kind": "EXACT_QUALITY_SUBDEGREE_FAMILY_MIGRATION",
        "working_meaning_de": spec_row["working_meaning_de"],
        "composition": spec_row["composition"],
        "context_rule": (
            f"exact complete ZL3b surface only; {occurrences} audited occurrences, "
            f"{reader_exact} all-reader exact; migration decision {decision}; "
            "every component remains whole-bound; "
            "no substring, absent-cell or non-family transfer"
        ),
        "status": "NEW_V24_FAMILY_MIGRATION",
    }


def build(output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    pages = {row["page"] for row in read_tsv(ROOT / G646_ALLOW)}
    if "f1r" in pages or any(page.startswith("f84") for page in pages):
        raise RuntimeError("allow-list contains excluded or forbidden page")
    guarded_query = g637.g636.g635.g634.g633.g632.g631.guarded_query
    token_rows, token_stats = guarded_query(
        TOKENS_REL, pages, "page,locus,token_index,eva,section,language,hand",
    )
    cross_rows, cross_stats = guarded_query(
        CROSS_REL, pages,
        "page,locus,all_three_present,all_present_exact,zl3b_clean,it2a_clean,rf1b_clean",
    )
    cross_by_locus = {row["locus"]: row for row in cross_rows}
    by_line, _ = g637.g636.g635.g634.g633.g632.g631.line_maps([dict(row) for row in token_rows])
    exact, boundary = g637.g636.g635.g634.stable_maps(token_rows, cross_by_locus)

    base_dictionary = [dict(row) for row in read_tsv(ROOT / G646_DICTIONARY)]
    base_gloss_rows = read_tsv(ROOT / G646_GLOSSARY)
    base_glossary = {row["surface"]: dict(row) for row in base_gloss_rows}
    base_coverage = read_tsv(ROOT / G646_COVERAGE)
    base_complete = read_tsv(ROOT / G646_COMPLETE)
    base_one = read_tsv(ROOT / G646_ONE)
    atlas = read_tsv(ROOT / G646_ATLAS)
    if (len(base_dictionary), len(base_glossary), len(base_coverage), len(base_complete), len(base_one)) != (304, 257, 4128, 61, 70):
        raise RuntimeError("GDT646 V23 base counts changed")
    replay_coverage, replay_one, _, replay_complete = g637.build_line_coverage(
        by_line, base_glossary, exact, boundary, cross_by_locus,
    )
    if (
        string_rows(replay_coverage) != string_rows(base_coverage)
        or string_rows(replay_complete) != string_rows(base_complete)
        or string_rows(replay_one) != string_rows(base_one)
    ):
        raise RuntimeError("GDT646 V23 line editions do not replay")
    base_metrics = metrics(replay_coverage, replay_one, replay_complete, base_glossary)
    expected_base = {
        "physical_lines": 4128, "known_token_positions": 10351,
        "unknown_token_positions": 21988, "complete_multi_token_lines": 61,
        "strict_complete_lines": 42, "one_unknown_lines": 70,
        "strict_one_unknown_lines": 22, "exact_glossary_surfaces": 257,
    }
    if base_metrics != expected_base:
        raise RuntimeError(f"GDT646 V23 metrics changed: {base_metrics!r}")

    token_counts = Counter(row["eva"] for row in token_rows)
    specs, absent_specs = family_specs(token_counts)
    old_atlas_surfaces = {row["surface"] for row in atlas}
    if not old_atlas_surfaces <= {row["surface"] for row in (*specs, *absent_specs)}:
        raise RuntimeError("GDT646 family atlas is no longer a subset of the GDT647 lattice")
    target_surfaces = {row["surface"] for row in specs}
    target_order = {row["surface"]: order for order, row in enumerate(specs, 1)}
    base_by_locus = {row["locus"]: row for row in base_coverage}
    migration_rows: list[dict[str, object]] = []
    overlays: list[dict[str, object]] = []
    glossary = {key: dict(value) for key, value in base_glossary.items()}
    for order, spec_row in enumerate(specs, 1):
        surface = spec_row["surface"]
        members = [row for row in token_rows if row["eva"] == surface]
        if len(members) != token_counts[surface] or not members:
            raise RuntimeError(f"target occurrence drift: {surface}")
        old = base_glossary.get(surface)
        exact_count = sum(exact[row["locus"], int(row["token_index"])] for row in members)
        split_count = sum(boundary[row["locus"], int(row["token_index"])] for row in members)
        if surface == "tcheey":
            decision = "RETAIN_IDENTICAL_V23"
            if old is None or old["working_meaning_de"] != spec_row["working_meaning_de"]:
                raise RuntimeError("tcheey base meaning changed")
        elif old is None:
            decision = "ADD_V24_EXACT_WHOLE" if exact_count else "ADD_V24_READER_WARNING_WHOLE"
        else:
            decision = "REVISE_V23_EXACT_WHOLE" if exact_count else "REVISE_V23_READER_WARNING_WHOLE"
        if surface == "kcheedy" and old is None:
            raise RuntimeError("kcheedy GDT643 anchor missing")
        reader_anchor = "ALL_READER_EXACT" if exact_count else "ZL3B_READER_VARIANT_ONLY"
        if decision != "RETAIN_IDENTICAL_V23":
            g637.set_gloss(
                glossary, surface, spec_row["working_meaning_de"],
                "GDT647:FAMILY_MIGRATION" if exact_count else "GDT647:FAMILY_MIGRATION_READER_WARNING",
                "EXACT_QUALITY_SUBDEGREE_FAMILY" if exact_count else "ZL3B_QUALITY_SUBDEGREE_READER_WARNING",
                "KNOWN_EXACT_WHOLE" if exact_count else "KNOWN_READER_VARIANT_WHOLE", 130,
            )
            overlays.append(dictionary_overlay(spec_row, decision, len(members), exact_count))
        migration_rows.append({
            "cell_id": f"G647-C{order:02d}", "family": spec_row["family"],
            "surface": surface, "composition": spec_row["composition"],
            "old_meaning_de": old["working_meaning_de"] if old else "UNKNOWN_SURFACE",
            "new_meaning_de": spec_row["working_meaning_de"], "decision": decision,
            "zl3b_occurrences": len(members), "pages": len({row["page"] for row in members}),
            "reader_exact_occurrences": exact_count,
            "split_normalized_occurrences": split_count,
            "reader_variant_occurrences": len(members) - split_count,
            "reader_anchor": reader_anchor,
        })

    final_coverage, final_one, _, final_complete = g637.build_line_coverage(
        by_line, glossary, exact, boundary, cross_by_locus,
    )
    final_by_locus = {row["locus"]: row for row in final_coverage}
    base_complete_by_locus = {row["locus"]: row for row in base_complete}
    final_complete_by_locus = {row["locus"]: row for row in final_complete}
    base_one_loci = {row["locus"] for row in base_one}
    final_one_by_locus = {row["locus"]: row for row in final_one}

    audit_rows: list[dict[str, object]] = []
    variant_rows: list[dict[str, object]] = []
    for migration in migration_rows:
        surface = str(migration["surface"])
        members = [row for row in token_rows if row["eva"] == surface]
        members.sort(key=lambda row: (row["page"], row["locus"], int(row["token_index"])))
        for occurrence, member in enumerate(members, 1):
            locus, token_index = member["locus"], int(member["token_index"])
            line = by_line[locus]
            ordinal = g646.line_position(line, token_index)
            before, after = base_by_locus[locus], final_by_locus[locus]
            before_glosses, after_glosses = split_pipe(before["token_glosses_de"]), split_pipe(after["token_glosses_de"])
            reader_exact = exact[locus, token_index]
            normalized = boundary[locus, token_index]
            support = "ALL_THREE_EXACT" if reader_exact else "ALL_THREE_SPLIT_NORMALIZED" if normalized else "READER_VARIANT"
            clean_other = (
                int(before["known_tokens"]) - int(before["ambiguous_tokens"])
                - int(before["reader_unstable_tokens"])
                - int(before_glosses[ordinal - 1] != f"[{surface}:?]")
            )
            if support == "ALL_THREE_EXACT" and clean_other >= 2:
                verdict = "CLEAN_CONTEXT_COMPATIBLE"
            elif support == "ALL_THREE_EXACT":
                verdict = "OPAQUE_OR_UNSTABLE_CONTEXT"
            elif support == "ALL_THREE_SPLIT_NORMALIZED":
                verdict = "READER_SPLIT_NORMALIZED"
            else:
                verdict = "READER_VARIANT_WARNING"
            audit_id = f"G647-A{target_order[surface]:03d}-{occurrence:03d}"
            audit_rows.append({
                "audit_id": audit_id, "surface": surface, "page": member["page"],
                "locus": locus, "section": member["section"], "language": member["language"],
                "hand": member["hand"], "token_ordinal": ordinal,
                "line_position": "ONLY" if len(line) == 1 else "INITIAL" if ordinal == 1 else "FINAL" if ordinal == len(line) else "MEDIAL",
                "previous": "<BOS>" if ordinal == 1 else line[ordinal - 2]["eva"],
                "following": "<EOS>" if ordinal == len(line) else line[ordinal]["eva"],
                "reader_support": support, "reader_exact": reader_exact,
                "split_normalized": normalized,
                "old_gloss_de": before_glosses[ordinal - 1],
                "new_gloss_de": after_glosses[ordinal - 1],
                "changed_gloss": int(before_glosses[ordinal - 1] != after_glosses[ordinal - 1]),
                "clean_known_other_tokens": clean_other,
                "local_before_de": before["token_glosses_de"],
                "local_after_de": after["token_glosses_de"],
                "thermal_reader_rival": int(surface == "kcheedy" and not reader_exact),
                "hard_collision": 0, "verdict": verdict,
            })
            if support != "ALL_THREE_EXACT":
                cross = cross_by_locus[locus]
                variant_rows.append({
                    "surface": surface, "page": member["page"], "locus": locus,
                    "zl3b_line": before["zl3b_line"], "it2a_line": cross["it2a_clean"],
                    "rf1b_line": cross["rf1b_clean"], "reader_support": support,
                    "new_meaning_de": migration["new_meaning_de"],
                    "decision": "RETAIN_EXACT_ZL3B_WITH_READER_WARNING",
                })

    affected_rows: list[dict[str, object]] = []
    for locus, before in base_by_locus.items():
        after = final_by_locus[locus]
        if before["token_glosses_de"] == after["token_glosses_de"]:
            continue
        line = by_line[locus]
        old_glosses, new_glosses = split_pipe(before["token_glosses_de"]), split_pipe(after["token_glosses_de"])
        changed = [
            str(token["eva"]) for token, old, new in zip(line, old_glosses, new_glosses) if old != new
        ]
        revisions = sum(not old.startswith("[") and old != new for old, new in zip(old_glosses, new_glosses))
        affected_rows.append({
            "page": before["page"], "locus": locus, "section": before["section"],
            "changed_surfaces": "|".join(changed),
            "newly_known_positions": int(after["known_tokens"]) - int(before["known_tokens"]),
            "meaning_revisions": revisions,
            "complete_before": int(locus in base_complete_by_locus),
            "complete_after": int(locus in final_complete_by_locus),
            "strict_complete_after": final_complete_by_locus.get(locus, {}).get("strict_complete", "0"),
            "zl3b_line": before["zl3b_line"], "old_translation_de": before["token_glosses_de"],
            "new_translation_de": after["token_glosses_de"],
        })
    affected_rows.sort(key=lambda row: (row["page"], row["locus"]))

    new_complete_loci = sorted(set(final_complete_by_locus) - set(base_complete_by_locus))
    new_complete_rows = [{
        "page": final_by_locus[locus]["page"], "locus": locus,
        "strict_complete": final_complete_by_locus[locus]["strict_complete"],
        "enabled_by_surfaces": "|".join(
            dict.fromkeys(
                token["eva"] for token in by_line[locus]
                if token["eva"] in target_surfaces
                and f"[{token['eva']}:?]" in split_pipe(base_by_locus[locus]["token_glosses_de"])
            )
        ),
        "zl3b_line": final_by_locus[locus]["zl3b_line"],
        "working_translation_de": final_by_locus[locus]["token_glosses_de"],
    } for locus in new_complete_loci]
    new_one_loci = sorted(set(final_one_by_locus) - base_one_loci)
    new_one_rows = [{
        "enabled_by_surfaces": "|".join(
            dict.fromkeys(
                token["eva"] for token in by_line[locus]
                if token["eva"] in target_surfaces
            )
        ),
        **{field: final_one_by_locus[locus][field] for field in g646.ONE_FIELDS},
    } for locus in new_one_loci]

    null_rows = [{
        "surface": row["surface"], "family": row["family"],
        "predicted_reading_de": row["working_meaning_de"],
        "status": "ABSENT_PREDICTION_HOLD",
    } for row in absent_specs]

    scope_rows = [
        {"decision": decision, "scope_id": scope_id, "surface_pattern": pattern, "reason": reason}
        for decision, scope_id, pattern, reason in SCOPE_BOUNDARY
    ]
    manual_rows: list[dict[str, object]] = []
    for locus, assessment, scoped_reading, note in MANUAL_PASSAGE_AUDIT:
        if locus not in final_by_locus:
            raise RuntimeError(f"manual passage locus missing: {locus}")
        line = by_line[locus]
        touched = list(dict.fromkeys(str(token["eva"]) for token in line if str(token["eva"]) in target_surfaces))
        if not touched:
            raise RuntimeError(f"manual passage has no migrated quality surface: {locus}")
        line_state = (
            "COMPLETE_V24" if locus in final_complete_by_locus
            else "ONE_HOLE_V24" if locus in final_one_by_locus
            else "PARTIAL_V24"
        )
        final_row = final_by_locus[locus]
        manual_rows.append({
            "page": final_row["page"], "locus": locus, "line_state": line_state,
            "assessment": assessment, "migrated_surfaces": "|".join(touched),
            "zl3b_line": final_row["zl3b_line"],
            "tokenwise_translation_de": final_row["token_glosses_de"],
            "scoped_reading_de": scoped_reading, "audit_note": note,
        })

    final_dictionary = [*base_dictionary, *overlays]
    final_gloss_rows = [
        {key: row[key] for key in ("surface", "working_meaning_de", "source", "strength", "scope_state", "priority")}
        for row in sorted(glossary.values(), key=lambda item: str(item["surface"]))
    ]
    final_metrics = metrics(final_coverage, final_one, final_complete, glossary)
    round_rows = [
        {"round": 0, "surface": "BASE_V23", "decision": "BASE",
         "dictionary_entries": len(base_dictionary), "dictionary_sha256": canonical_hash(base_dictionary), **base_metrics},
        {"round": 1, "surface": "QUALITY_SUBDEGREE_FAMILY", "decision": "MIGRATE",
         "dictionary_entries": len(final_dictionary), "dictionary_sha256": canonical_hash(final_dictionary), **final_metrics},
    ]

    write_tsv(output_dir / "PAGE_ALLOWLIST.tsv", [{"page": page} for page in sorted(pages)], ("page",))
    write_tsv(output_dir / "FAMILY_MIGRATION_DECK.tsv", migration_rows, (
        "cell_id", "family", "surface", "composition", "old_meaning_de",
        "new_meaning_de", "decision", "zl3b_occurrences", "pages",
        "reader_exact_occurrences", "split_normalized_occurrences",
        "reader_variant_occurrences", "reader_anchor",
    ))
    write_tsv(output_dir / "NULL_CELL_HOLDS.tsv", null_rows, (
        "surface", "family", "predicted_reading_de", "status",
    ))
    write_tsv(output_dir / "AXIS_SCOPE_BOUNDARY.tsv", scope_rows, (
        "decision", "scope_id", "surface_pattern", "reason",
    ))
    write_tsv(output_dir / "MANUAL_PASSAGE_REALITY_CHECK.tsv", manual_rows, (
        "page", "locus", "line_state", "assessment", "migrated_surfaces",
        "zl3b_line", "tokenwise_translation_de", "scoped_reading_de", "audit_note",
    ))
    write_tsv(output_dir / "ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv", audit_rows, (
        "audit_id", "surface", "page", "locus", "section", "language", "hand",
        "token_ordinal", "line_position", "previous", "following", "reader_support",
        "reader_exact", "split_normalized", "old_gloss_de", "new_gloss_de",
        "changed_gloss", "clean_known_other_tokens", "local_before_de",
        "local_after_de", "thermal_reader_rival", "hard_collision", "verdict",
    ))
    write_tsv(output_dir / "READER_VARIANT_AUDIT.tsv", variant_rows, (
        "surface", "page", "locus", "zl3b_line", "it2a_line", "rf1b_line",
        "reader_support", "new_meaning_de", "decision",
    ))
    write_tsv(output_dir / "AFFECTED_PASSAGES.tsv", affected_rows, (
        "page", "locus", "section", "changed_surfaces", "newly_known_positions",
        "meaning_revisions", "complete_before", "complete_after",
        "strict_complete_after", "zl3b_line", "old_translation_de",
        "new_translation_de",
    ))
    write_tsv(output_dir / "NEWLY_COMPLETED_LINES.tsv", new_complete_rows, (
        "page", "locus", "strict_complete", "enabled_by_surfaces", "zl3b_line",
        "working_translation_de",
    ))
    write_tsv(output_dir / "NEWLY_EXPOSED_ONE_HOLE_LINES.tsv", new_one_rows, (
        "enabled_by_surfaces", *g646.ONE_FIELDS,
    ))
    write_tsv(output_dir / "ROUND_COVERAGE_COUNTS.tsv", round_rows, (
        "round", "surface", "decision", "dictionary_entries", "dictionary_sha256",
        "physical_lines", "known_token_positions", "unknown_token_positions",
        "complete_multi_token_lines", "strict_complete_lines", "one_unknown_lines",
        "strict_one_unknown_lines", "exact_glossary_surfaces",
    ))
    write_tsv(output_dir / "V24_EXACT_TOKEN_GLOSSARY.tsv", final_gloss_rows, (
        "surface", "working_meaning_de", "source", "strength", "scope_state", "priority",
    ))
    write_tsv(output_dir / "ALL_LINE_CONCRETE_COVERAGE_V24.tsv", final_coverage, g646.COVERAGE_FIELDS)
    write_tsv(output_dir / "COMPLETE_PASSAGES_V24.tsv", final_complete, (
        "rank", "strict_complete", *g646.COVERAGE_FIELDS, "working_translation_de",
    ))
    write_tsv(output_dir / "ONE_UNKNOWN_PASSAGES_V24.tsv", final_one, g646.ONE_FIELDS)
    write_tsv(output_dir / "WORKING_DICTIONARY_V24.tsv", final_dictionary, (
        "entry", "kind", "working_meaning_de", "composition", "context_rule", "status",
    ))

    output_paths = [output_dir / name for name in OUTPUT_NAMES]
    base_result = json.loads((ROOT / G646_RESULT).read_text(encoding="utf-8"))
    inherited_inputs = tuple(Path(path) for path in base_result["inputs"])
    input_paths = tuple(dict.fromkeys((
        *inherited_inputs, G646_RUN, G646_ALLOW, G646_COVERAGE, G646_COMPLETE,
        G646_ONE, G646_GLOSSARY, G646_DICTIONARY, G646_ATLAS, G646_HISTORICAL,
        G646_RESULT, G646_REPORT, TOKENS_REL, CROSS_REL,
    )))
    verdicts = Counter(row["verdict"] for row in audit_rows)
    result_core = {
        "schema": "GDT647_QUALITY_SUBDEGREE_FAMILY_MIGRATION_RESULT_V2",
        "experiment_id": "GDT647", "status": STATUS,
        "guard": {
            "f1r": "EXCLUDED", "f84": "FORBIDDEN", "f84r": "FORBIDDEN",
            "new_pages": 0, "new_images": 0, "allowed_pages": len(pages),
            "token_query": token_stats, "cross_query": cross_stats,
        },
        "migration": {
            "observed_cells": len(migration_rows),
            "new_observed_wholes": sum(str(row["decision"]).startswith("ADD_V24_") for row in migration_rows),
            "new_all_reader_anchored_wholes": sum(row["decision"] == "ADD_V24_EXACT_WHOLE" for row in migration_rows),
            "new_reader_warning_wholes": sum(row["decision"] == "ADD_V24_READER_WARNING_WHOLE" for row in migration_rows),
            "revised_exact_wholes": sum(str(row["decision"]).startswith("REVISE_V23_") for row in migration_rows),
            "revised_all_reader_anchored_wholes": sum(row["decision"] == "REVISE_V23_EXACT_WHOLE" for row in migration_rows),
            "revised_reader_warning_wholes": sum(row["decision"] == "REVISE_V23_READER_WARNING_WHOLE" for row in migration_rows),
            "retained_exact_wholes": sum(row["decision"] == "RETAIN_IDENTICAL_V23" for row in migration_rows),
            "target_occurrences": len(audit_rows),
            "reader_exact_occurrences": sum(int(row["reader_exact"]) for row in audit_rows),
            "split_normalized_occurrences": sum(int(row["split_normalized"]) for row in audit_rows),
            "reader_variant_warnings": sum(row["verdict"] == "READER_VARIANT_WARNING" for row in audit_rows),
            "surfaces_with_all_reader_anchor": sum(int(row["reader_exact_occurrences"]) > 0 for row in migration_rows),
            "reader_unstable_observed_surfaces": sum(int(row["reader_exact_occurrences"]) == 0 for row in migration_rows),
            "verdicts": dict(sorted(verdicts.items())),
            "absent_cells_held": len(null_rows),
        },
        "passage_impact": {
            "affected_lines": len(affected_rows),
            "base_complete_lines_touched": sum(row["locus"] in base_complete_by_locus for row in affected_rows),
            "base_one_hole_lines_touched": sum(row["locus"] in base_one_loci for row in affected_rows),
            "meaning_revision_positions": sum(int(row["meaning_revisions"]) for row in affected_rows),
            "newly_known_positions": final_metrics["known_token_positions"] - base_metrics["known_token_positions"],
            "newly_completed_lines": len(new_complete_rows),
            "newly_exposed_one_hole_lines": len(new_one_rows),
            "manual_reality_check_lines": len(manual_rows),
        },
        "coverage": {"base": base_metrics, "final": final_metrics},
        "working_dictionary": {
            "v23_entries": len(base_dictionary), "v24_entries": len(final_dictionary),
            "overlay_entries": len(overlays), "v23_prefix_sha256": canonical_hash(base_dictionary),
            "v24_sha256": canonical_hash(final_dictionary),
            "base_glossary_surfaces": len(base_glossary), "v24_glossary_surfaces": len(glossary),
        },
        "claim_boundary": (
            "GDT647 migrates only the 107 observed exact ZL3b whole surfaces in three predeclared quality-headed families to beginning/middle/end within the separately numbered degree. "
            "Ninety previously unknown surfaces are added, sixteen prior exact wholes are revised and tcheey is retained identically. "
            "Thirteen absent cells remain holds; five observed surfaces without an all-reader exact occurrence remain visibly reader-unstable. "
            "The ending is not globalized: naked CTH, p/s/r/l material words, oiin, al, air and aN stay unchanged. "
            "No plaintext, phonetics, language, ingredient identity, free component or absent-cell value is promoted."
        ),
        "inputs": {str(path): sha256(ROOT / path) for path in input_paths},
        "outputs": {str(BASE_REL / "artifacts" / path.name): sha256(path) for path in output_paths},
    }
    result = {**result_core, "content_sha256": canonical_hash(result_core)}
    (output_dir / "RESULT.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return result


def main() -> int:
    result = build(ART)
    migration, impact, final = result["migration"], result["passage_impact"], result["coverage"]["final"]
    print(
        f"GDT647 built: cells={migration['observed_cells']} positions={migration['target_occurrences']} "
        f"new_known={impact['newly_known_positions']} affected={impact['affected_lines']} "
        f"complete={final['complete_multi_token_lines']} one_unknown={final['one_unknown_lines']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
