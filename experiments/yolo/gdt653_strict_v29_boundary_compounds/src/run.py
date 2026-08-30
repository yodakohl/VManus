#!/usr/bin/env python3
"""Build GDT653: close six strict V29 holes through visible compounds."""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import re
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
BASE_REL = Path("experiments/yolo/gdt653_strict_v29_boundary_compounds")
ART = ROOT / BASE_REL / "artifacts"
G652 = Path("experiments/yolo/gdt652_strict_v28_frontier_completion")
G652_RUN = G652 / "src/run.py"
G652_ALLOW = G652 / "artifacts/PAGE_ALLOWLIST.tsv"
G652_COVERAGE = G652 / "artifacts/ALL_LINE_CONCRETE_COVERAGE_V29.tsv"
G652_COMPLETE = G652 / "artifacts/COMPLETE_PASSAGES_V29.tsv"
G652_ONE = G652 / "artifacts/ONE_UNKNOWN_PASSAGES_V29.tsv"
G652_GLOSSARY = G652 / "artifacts/V29_EXACT_TOKEN_GLOSSARY.tsv"
G652_DICTIONARY = G652 / "artifacts/WORKING_DICTIONARY_V29.tsv"
G652_RESULT = G652 / "artifacts/RESULT.json"
G652_REPORT = G652 / "REPORT.md"
G628_REPORT = Path("experiments/yolo/gdt628_chol_measure_frame/REPORT.md")
G633_REPORT = Path("experiments/yolo/gdt633_cth_interfix_semantic_contrasts/REPORT.md")
G636_REPORT = Path("experiments/yolo/gdt636_residual_four_head_semantics/REPORT.md")
G642_REPORT = Path("experiments/yolo/gdt642_exact_e_ol_or_carrier_completion/REPORT.md")
G648_REPORT = Path("experiments/yolo/gdt648_strict_v24_hole_completion/REPORT.md")
G651_REPORT = Path("experiments/yolo/gdt651_ckh_four_shell_family_migration/REPORT.md")

spec = importlib.util.spec_from_file_location("gdt652_builder_for_gdt653", ROOT / G652_RUN)
if spec is None or spec.loader is None:
    raise RuntimeError("cannot load GDT652 builder")
g652 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g652)
g637 = g652.g637
TOKENS_REL = g652.TOKENS_REL
CROSS_REL = g652.CROSS_REL
COVERAGE_FIELDS = g652.COVERAGE_FIELDS
ONE_FIELDS = g652.ONE_FIELDS

STATUS = "PASS_6_STRICT_BOUNDARY_COMPOUNDS__V30"
GENERIC_FILLER = re.compile(
    r"arbeitsgut|arbeitschritt|arbeitsschritt|arbeitsmittel|arbeitsstoff|"
    r"arbeitsobjekt|werkzeug|produkt weiter|f.hre .* aus|leite .* weiter",
    re.IGNORECASE,
)

# The sidequest explicitly permits replaceable meanings before proof. Every
# value remains bound to one complete observed surface. CKH_LEARNED, O_PREP,
# E_ATTR and the tail labels are structural tags, never exported free words.
def card(
    surface: str,
    family: str,
    tier: str,
    meaning: str,
    composition: str,
    rival: str,
    basis: str,
    counterargument: str,
    source_locus: str = "NONE",
) -> dict[str, str]:
    return {
        "surface": surface,
        "source_locus": source_locus,
        "strict_source": "0" if source_locus == "NONE" else "1",
        "family": family,
        "tier": tier,
        "working_meaning_de": meaning,
        "composition": composition,
        "rival_de": rival,
        "decision_basis": basis,
        "counterargument": counterargument,
    }


# GDT653 uses the GDT652 helpers as the reproducible V29 engine and promotes
# only these six complete surfaces in V30.
CANDIDATE_SPECS = (
    card(
        "orol", "OR_OL_FUSION_FAMILY", "STRONG_DIRECT_BOUNDARY_COMPOUND",
        "Drogenstoffportion", "OR_PORTION+OL_MATERIAL", "Wurzelzubereitung",
        "ten tokens with nine all-reader exact anchors and repeated all-reader OR OL separated witnesses",
        "OR and OL remain context-bound carrier nouns and the rival O_PREP+R_ROOT+OL segmentation yields Wurzelzubereitung",
        "f80v.44",
    ),
    card(
        "chckhal", "CKH_AL_FORM_FAMILY", "STRONG_LEARNED_HEAD_COMPOUND",
        "trockenes Arzneikompositum, Rohstoffform I", "ch+CKH_LEARNED+AL_BOUND",
        "trockenes Arzneikompositum, Charge I",
        "four all-reader exact tokens beside exact CKHAL and SHECKHAL sister bodies and the migrated CKH object family",
        "AL may be an item or measure form rather than raw state and the CKH noun remains learned",
        "f83r.39",
    ),
    card(
        "octhdy", "O_PREP_CTH_RESULT_FAMILY", "STRONG_LOW_N_RESULT_COMPOUND",
        "fertig aufbereitete Drogenzubereitung, Grundform", "O_PREP+CTH_LEARNED+d+y",
        "CTH-Ansatz am Gradanfang, abgeschlossen",
        "two all-reader exact tokens extend the known OCTHY/OCTHEY preparation ladder and have a matching populated CTHDY sibling field",
        "both target tokens lie outside the Herbal scope, so Blatt/Kraut remains only a section-local rival",
        "f114r.13",
    ),
    card(
        "chdaly", "DAL_LEARNED_MATERIA_FAMILY", "PROVISIONAL_DAL_HEAD_COMPOUND",
        "trockener Rohdrogenposten, Grundform", "ch+DAL_LEARNED+y",
        "trockener Rohstoff, Form I",
        "three all-reader exact tokens occupy the dry Y cell of the dense DAL/DALY/DALDY and CH/SH by E sister field",
        "DAL is a learned head whose Rohdrogenposten value is inferred from the family rather than independently decoded",
        "f112v.16",
    ),
    card(
        "sodal", "S_ODAL_SEED_PREPARATION_FAMILY", "PROVISIONAL_DIRECT_BOUNDARY_COMPOUND",
        "Ansatz aus einem Saatdrogenposten", "S_SEED+O_PREP+DAL_LEARNED",
        "Saat-Rohstoffmaß",
        "two tokens include one all-reader exact anchor; f93r.11 has IT2a SODAL against RF1b S ODAL while ZL3b reads S ODAM",
        "the S seed value and the deep O plus DAL parse are inherited; ODAL is not an independently translated free word",
        "f42v.8",
    ),
    card(
        "skar", "S_K_AR_SEED_FRACTION_FAMILY", "EXPLORATORY_SINGLETON_COMPOUND",
        "heiße Samenfraktion I", "S_SEED+K_HEISS+AR_FRACTION_I",
        "heiße Salzfraktion I",
        "the singleton is all-reader exact and completes the populated KAR/LKAR/RKAR/SKAR head set with known LKAR",
        "one target token cannot distinguish a productive S plus KAR parse from a learned indivisible name; upstream QOKAR still conflicts between Portion and the AR fraction ladder",
        "f83r.44",
    ),
)

REVISION_SPECS: tuple[tuple[str, str, str], ...] = ()

FAMILY_FORMS = tuple(
    (
        str(row["family"]), str(row["surface"]), str(row["composition"]),
        str(row["working_meaning_de"]), "TARGET",
    )
    for row in CANDIDATE_SPECS
) + (
    ("OR_OL_FUSION_FAMILY", "or", "OR_PORTION", "Portions-/Nominalträger", "V29_ANCHOR"),
    ("OR_OL_FUSION_FAMILY", "ol", "OL_MATERIAL", "Drogenstoff-/Materialträger", "V29_ANCHOR"),
    ("CKH_AL_FORM_FAMILY", "ckhal", "CKH_LEARNED+AL_BOUND", "Arzneikompositum, Rohstoffform I", "SISTER_SUPPORT_HOLD"),
    ("CKH_AL_FORM_FAMILY", "sheckhal", "sh+E_ATTR+CKH_LEARNED+AL_BOUND", "feuchtes Arzneikompositum, Rohstoffform I", "SISTER_SUPPORT_HOLD"),
    ("O_PREP_CTH_RESULT_FAMILY", "octhy", "O_PREP+CTH_LEARNED+y", "CTH-Zubereitung, Grundform", "V29_ANCHOR"),
    ("O_PREP_CTH_RESULT_FAMILY", "octhey", "O_PREP+CTH_LEARNED+e+y", "CTH-Zubereitung, Form I", "V29_ANCHOR"),
    ("O_PREP_CTH_RESULT_FAMILY", "octheey", "O_PREP+CTH_LEARNED+ee+y", "CTH-Zubereitung, Form II", "ABSENT_PREDICTION"),
    ("O_PREP_CTH_RESULT_FAMILY", "octhedy", "O_PREP+CTH_LEARNED+e+d+y", "CTH-Zubereitung, Form I, fertig aufbereitet", "SISTER_SUPPORT_HOLD"),
    ("O_PREP_CTH_RESULT_FAMILY", "octheedy", "O_PREP+CTH_LEARNED+ee+d+y", "CTH-Zubereitung, Form II, fertig aufbereitet", "ABSENT_PREDICTION"),
    ("DAL_LEARNED_MATERIA_FAMILY", "dal", "DAL_LEARNED", "Rohdrogenposten", "SISTER_SUPPORT_HOLD"),
    ("DAL_LEARNED_MATERIA_FAMILY", "daly", "DAL_LEARNED+y", "Rohdrogenposten, Grundform", "SISTER_SUPPORT_HOLD"),
    ("DAL_LEARNED_MATERIA_FAMILY", "daldy", "DAL_LEARNED+d+y", "Rohdrogenposten, Grundform, abgeschlossen", "SISTER_SUPPORT_HOLD"),
    ("DAL_LEARNED_MATERIA_FAMILY", "shedal", "sh+E_ATTR+DAL_LEARNED", "feuchter Rohdrogenposten", "SISTER_SUPPORT_HOLD"),
    ("S_ODAL_SEED_PREPARATION_FAMILY", "odal", "O_PREP+DAL_LEARNED", "angesetzter Rohdrogenposten", "SISTER_SUPPORT_HOLD"),
    ("S_K_AR_SEED_FRACTION_FAMILY", "kar", "K_HEISS+AR_FRACTION_I", "heiße Fraktion I", "SISTER_SUPPORT_HOLD"),
    ("S_K_AR_SEED_FRACTION_FAMILY", "sar", "S_SEED+AR_FRACTION_I", "Samenfraktion I", "V29_ANCHOR"),
    ("S_K_AR_SEED_FRACTION_FAMILY", "lkar", "L_WOOD+K_HEISS+AR_FRACTION_I", "heiße Holzfraktion I", "V29_ANCHOR"),
    ("S_K_AR_SEED_FRACTION_FAMILY", "rkar", "R_ROOT+K_HEISS+AR_FRACTION_I", "heiße Wurzelfraktion I", "SISTER_SUPPORT_HOLD"),
    ("S_K_AR_SEED_FRACTION_FAMILY", "qokar", "qo+K_HEISS+AR_FRACTION_I", "V29: heiße Portion; Kompositionsrivale: heiße Fraktion I", "UPSTREAM_SEMANTIC_CONFLICT"),
)

BRIDGE_SPECS = (
    ("G653-B01", "OR_OL_FUSION_FAMILY", "f34v.3", "or ol / orol", "all-reader separated OR OL witness for the fused target"),
    ("G653-B02", "OR_OL_FUSION_FAMILY", "f78v.25", "or ol / orol", "all-reader separated OR OL witness for the fused target"),
    ("G653-B03", "OR_OL_FUSION_FAMILY", "f104v.33", "or ol / orol", "all-reader separated OR OL witness for the fused target"),
    ("G653-B04", "O_PREP_CTH_RESULT_FAMILY", "f112r.23", "octhdy", "second all-reader exact OCTHDY occurrence in a longer preparation/quality list"),
    ("G653-B05", "DAL_LEARNED_MATERIA_FAMILY", "f75v.22", "daldy / dal dy", "IT2a split exposes DAL before the completion tail while ZL3b/RF1b retain fusion"),
    ("G653-B06", "S_ODAL_SEED_PREPARATION_FAMILY", "f93r.11", "s odal / sodal", "reader split directly exposes the S plus ODAL fusion"),
    ("G653-B07", "CKH_AL_FORM_FAMILY", "f83r.39", "chckhal / ckhal / sheckhal", "strict target belongs to the observed CKH plus AL sister field"),
    ("G653-B08", "S_K_AR_SEED_FRACTION_FAMILY", "f83r.44", "skar / kar / lkar / rkar", "strict singleton belongs to the populated material-head KAR set"),
    ("G653-B09", "OR_OL_FUSION_FAMILY", "f82r.10", "oroldair / orol dain / orol dair", "superform reader split exposes OROL as one complete unit before a value tail"),
    ("G653-B10", "S_ODAL_SEED_PREPARATION_FAMILY", "f116r.50", "sodal / s dal", "reader warning: RF1b omits O, so this is family support but not split normalization"),
    ("G653-B11", "OR_OL_FUSION_FAMILY", "f102v2.19", "o r o l / or ol", "reader granularity independently exposes OR and OL without a fused target token"),
)

SMOOTHED_SOURCE_LINES = {
    "f80v.44": "Eine Portion heißen Drogenstoffs.",
    "f83r.39": "Trockenes Arzneikompositum, Rohstoffform I: Wärmegrad II; bis zur Gradmitte feucht; nochmals Wärmegrad II.",
    "f114r.13": "Fertig aufbereitete Drogenzubereitung, Grundform: heiß-trocken, Grad III, in der Gradmitte abgeschlossen.",
    "f112v.16": "Trockener Rohdrogenposten, Grundform, Samencharge III; Qualitätsfolge: heiß/feucht bis Gradende; kalt bis Gradende abgeschlossen; heiß bis Gradmitte; dort trocken abgeschlossen; zweimal heiß bis Gradende.",
    "f42v.8": "Ansatz aus einem Saatdrogenposten, Samencharge III.",
    "f83r.44": "Heiße Samenfraktion I, bis zur Gradmitte feucht und abgeschlossen.",
}

OUTPUT_NAMES = (
    "PAGE_ALLOWLIST.tsv", "TARGET_DECISION_DECK.tsv", "FAMILY_EVIDENCE_ATLAS.tsv",
    "BOUNDARY_BRIDGE_ATLAS.tsv", "RISK_AND_RIVAL_REGISTER.tsv", "ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv",
    "READER_VARIANT_AUDIT.tsv", "SEQUENTIAL_DECISION_LEDGER.tsv",
    "ROUND_COVERAGE_COUNTS.tsv", "ACCEPTED_WHOLE_SURFACE_DEFAULTS.tsv",
    "SOURCE_PASSAGE_REALITY_CHECK.tsv", "AFFECTED_LINE_TRANSLATIONS.tsv",
    "NEWLY_COMPLETED_LINES.tsv", "NEWLY_EXPOSED_ONE_HOLE_LINES.tsv",
    "V30_EXACT_TOKEN_GLOSSARY.tsv", "ALL_LINE_CONCRETE_COVERAGE_V30.tsv",
    "COMPLETE_PASSAGES_V30.tsv", "ONE_UNKNOWN_PASSAGES_V30.tsv",
    "WORKING_DICTIONARY_V30.tsv",
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


def line_position(line: list[dict[str, object]], token_index: int) -> int:
    for ordinal, token in enumerate(line, 1):
        if int(token["token_index"]) == token_index:
            return ordinal
    raise RuntimeError("token position not found")


def dictionary_row(spec_row: dict[str, str], round_number: int, occurrences: int, exact_count: int) -> dict[str, object]:
    return {
        "entry": f"{spec_row['surface']}@GDT653_EXACT_WHOLE",
        "kind": f"EXACT_ZL3B_WHOLE_{spec_row['tier']}",
        "working_meaning_de": spec_row["working_meaning_de"],
        "composition": spec_row["composition"],
        "context_rule": (
            f"exact complete surface only; tier={spec_row['tier']}; {occurrences} audited occurrences; "
            f"{exact_count} all-reader exact; learned components remain family-bound"
        ),
        "status": f"NEW_V30_ACCEPTED_ROUND_{round_number:02d}",
    }


def build(output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    pages = {row["page"] for row in read_tsv(ROOT / G652_ALLOW)}
    if "f1r" in pages or any(page.startswith("f84") for page in pages):
        raise RuntimeError("allow-list contains excluded or forbidden page")
    guarded_query = g637.g636.g635.g634.g633.g632.g631.guarded_query
    token_rows, token_stats = guarded_query(
        TOKENS_REL, pages, "page,locus,token_index,eva,section,language,hand",
    )
    cross_rows, cross_stats = guarded_query(
        CROSS_REL, pages, "page,locus,all_three_present,all_present_exact,zl3b_clean,it2a_clean,rf1b_clean",
    )
    cross_by_locus = {row["locus"]: row for row in cross_rows}
    by_line, _ = g637.g636.g635.g634.g633.g632.g631.line_maps([dict(row) for row in token_rows])
    exact, boundary = g637.g636.g635.g634.stable_maps(token_rows, cross_by_locus)

    base_dictionary = [dict(row) for row in read_tsv(ROOT / G652_DICTIONARY)]
    base_gloss_rows = read_tsv(ROOT / G652_GLOSSARY)
    base_glossary = {row["surface"]: dict(row) for row in base_gloss_rows}
    base_coverage = read_tsv(ROOT / G652_COVERAGE)
    base_complete = read_tsv(ROOT / G652_COMPLETE)
    base_one = read_tsv(ROOT / G652_ONE)
    if (len(base_dictionary), len(base_glossary), len(base_coverage), len(base_complete), len(base_one)) != (485, 414, 4128, 113, 165):
        raise RuntimeError("GDT652 V29 base counts changed")
    replay_coverage, replay_one, _, replay_complete = g637.build_line_coverage(
        by_line, base_glossary, exact, boundary, cross_by_locus,
    )
    if (string_rows(replay_coverage) != string_rows(base_coverage)
            or string_rows(replay_complete) != string_rows(base_complete)
            or string_rows(replay_one) != string_rows(base_one)):
        raise RuntimeError("GDT652 V29 editions do not replay")
    base_metrics = metrics(replay_coverage, replay_one, replay_complete, base_glossary)
    expected_base = {
        "physical_lines": 4128, "known_token_positions": 14951,
        "unknown_token_positions": 17388, "complete_multi_token_lines": 113,
        "strict_complete_lines": 67, "one_unknown_lines": 165,
        "strict_one_unknown_lines": 39, "exact_glossary_surfaces": 414,
    }
    if base_metrics != expected_base:
        raise RuntimeError(f"GDT652 V29 metrics changed: {base_metrics!r}")

    targets = {str(row["surface"]) for row in CANDIDATE_SPECS}
    revision_surfaces = {surface for surface, _, _ in REVISION_SPECS}
    if targets & set(base_glossary):
        raise RuntimeError("a GDT653 target is already in the V29 glossary")
    if revision_surfaces - set(base_glossary) or targets & revision_surfaces:
        raise RuntimeError("GDT653 revision deck no longer matches the V29 glossary")
    strict_source = {str(row["surface"]): str(row["source_locus"]) for row in CANDIDATE_SPECS if row["strict_source"] == "1"}
    source_pairs = {(row["unknown_surface"], row["locus"]): row for row in base_one}
    for surface, locus in strict_source.items():
        source = source_pairs.get((surface, locus))
        if source is None or int(source["strict_eligible"]) != 1:
            raise RuntimeError(f"strict GDT652 source frontier changed: {(surface, locus)}")
    if strict_source != {
            "orol": "f80v.44", "chckhal": "f83r.39",
            "octhdy": "f114r.13", "chdaly": "f112v.16",
            "sodal": "f42v.8", "skar": "f83r.44"}:
        raise RuntimeError("strict source deck changed")
    strict_hole_rows = sorted(
        (row for row in base_one if row["unknown_surface"] in targets and int(row["strict_eligible"]) == 1),
        key=lambda row: row["locus"],
    )
    if [(row["unknown_surface"], row["locus"]) for row in strict_hole_rows] != [
            ("chdaly", "f112v.16"), ("octhdy", "f114r.13"),
            ("sodal", "f42v.8"), ("orol", "f80v.44"),
            ("chckhal", "f83r.39"), ("skar", "f83r.44")]:
        raise RuntimeError("GDT653 strict-hole frontier changed")

    token_counts = Counter(str(row["eva"]) for row in token_rows)
    family_rows: list[dict[str, object]] = []
    for family, surface, composition, reading, planned_status in FAMILY_FORMS:
        members = [row for row in token_rows if row["eva"] == surface]
        exact_count = sum(exact[row["locus"], int(row["token_index"])] for row in members)
        normalized_count = sum(boundary[row["locus"], int(row["token_index"])] for row in members)
        family_rows.append({
            "family": family, "surface": surface, "composition": composition,
            "predicted_reading_de": reading, "zl3b_occurrences": len(members),
            "pages": len({row["page"] for row in members}),
            "reader_exact_occurrences": exact_count,
            "split_normalized_occurrences": normalized_count,
            "planned_status": planned_status,
            "final_status": (
                "ACCEPTED_V30" if surface in targets else
                "UPSTREAM_SEMANTIC_CONFLICT" if planned_status == "UPSTREAM_SEMANTIC_CONFLICT" else
                "V29_ANCHOR" if surface in base_glossary else
                "ABSENT_HOLD" if not members else planned_status
            ),
        })

    bridge_rows: list[dict[str, object]] = []
    for bridge_id, family, locus, diagnostic, support in BRIDGE_SPECS:
        row = cross_by_locus.get(locus)
        if row is None:
            raise RuntimeError(f"missing bridge locus: {locus}")
        bridge_rows.append({
            "bridge_id": bridge_id, "family": family, "page": row["page"], "locus": locus,
            "diagnostic_surface": diagnostic, "zl3b_line": row["zl3b_clean"],
            "it2a_line": row["it2a_clean"], "rf1b_line": row["rf1b_clean"],
            "supports": support,
        })

    glossary = {key: dict(value) for key, value in base_glossary.items()}
    coverage, one_unknown, _, complete = g637.build_line_coverage(
        by_line, glossary, exact, boundary, cross_by_locus,
    )
    if metrics(coverage, one_unknown, complete, glossary) != base_metrics:
        raise RuntimeError("V29 replay changed before the first GDT653 target")
    base_complete_loci = {row["locus"] for row in base_complete}
    seen_one_loci = {row["locus"] for row in base_one}
    accepted_dictionary_rows: list[dict[str, object]] = []
    target_deck: list[dict[str, object]] = []
    audit_rows: list[dict[str, object]] = []
    variant_rows: list[dict[str, object]] = []
    ledger_rows: list[dict[str, object]] = []
    newly_exposed_rows: list[dict[str, object]] = []
    round_rows: list[dict[str, object]] = [{
        "round": 0, "surface": "BASE_V29", "tier": "BASE", "dictionary_entries": len(base_dictionary),
        "dictionary_sha256": canonical_hash(base_dictionary), **base_metrics,
    }]

    for round_number, raw_spec in enumerate(CANDIDATE_SPECS, 1):
        spec_row = {key: str(value) for key, value in raw_spec.items()}
        surface = spec_row["surface"]
        if GENERIC_FILLER.search(spec_row["working_meaning_de"]):
            raise RuntimeError(f"generic filler in target: {surface}")
        members = [row for row in token_rows if row["eva"] == surface]
        if not members or len(members) != token_counts[surface]:
            raise RuntimeError(f"target occurrence drift: {surface}")
        exact_count = sum(exact[row["locus"], int(row["token_index"])] for row in members)
        split_count = sum(boundary[row["locus"], int(row["token_index"])] for row in members)
        if exact_count == 0:
            raise RuntimeError(f"accepted target lacks an all-reader exact anchor: {surface}")

        pre_coverage, pre_one, pre_complete = coverage, one_unknown, complete
        pre_by_locus = {row["locus"]: row for row in pre_coverage}
        pre_complete_loci = {row["locus"] for row in pre_complete}
        if spec_row["strict_source"] == "1":
            source = {row["locus"]: row for row in pre_one}.get(spec_row["source_locus"])
            if source is None or source["unknown_surface"] != surface or int(source["strict_eligible"]) != 1:
                raise RuntimeError(f"source line no longer strict one-hole: {surface}")

        g637.set_gloss(
            glossary, surface, spec_row["working_meaning_de"], f"GDT653:{spec_row['tier']}",
            "EXACT_WHOLE_FAMILY_EXTENSION", "KNOWN_EXACT_WHOLE", 148,
        )
        coverage, one_unknown, _, complete = g637.build_line_coverage(
            by_line, glossary, exact, boundary, cross_by_locus,
        )
        post_by_locus = {row["locus"]: row for row in coverage}
        new_complete_loci = sorted({row["locus"] for row in complete} - pre_complete_loci)
        if spec_row["strict_source"] == "1" and spec_row["source_locus"] not in new_complete_loci:
            raise RuntimeError(f"target failed to close strict source: {surface}")

        verdicts: Counter[str] = Counter()
        members.sort(key=lambda row: (row["page"], row["locus"], int(row["token_index"])))
        for occurrence, member in enumerate(members, 1):
            locus, token_index = member["locus"], int(member["token_index"])
            line = by_line[locus]
            ordinal = line_position(line, token_index)
            before, after = pre_by_locus[locus], post_by_locus[locus]
            before_glosses, after_glosses = split_pipe(before["token_glosses_de"]), split_pipe(after["token_glosses_de"])
            reader_exact = exact[locus, token_index]
            normalized = boundary[locus, token_index]
            support = "ALL_THREE_EXACT" if reader_exact else "ALL_THREE_SPLIT_NORMALIZED" if normalized else "READER_VARIANT"
            known_other = int(before["known_tokens"])
            clean_other = known_other - int(before["ambiguous_tokens"]) - int(before["reader_unstable_tokens"])
            if support == "READER_VARIANT":
                verdict = "READER_VARIANT_WARNING"
            elif spec_row["tier"].startswith("EXPLORATORY"):
                verdict = "EXPLORATORY_CONTEXT_NO_RECORDED_COLLISION" if clean_other >= 2 else "EXPLORATORY_SHORT_OR_OPAQUE"
            elif clean_other >= 2:
                verdict = "FAMILY_CONTEXT_COMPATIBLE"
            else:
                verdict = "SHORT_OR_OPAQUE_CONTEXT"
            verdicts[verdict] += 1
            audit_rows.append({
                "audit_id": f"G653-A{round_number:02d}-{occurrence:03d}", "round": round_number,
                "surface": surface, "tier": spec_row["tier"], "page": member["page"], "locus": locus,
                "section": member["section"], "language": member["language"], "hand": member["hand"],
                "token_ordinal": ordinal,
                "line_position": "ONLY" if len(line) == 1 else "INITIAL" if ordinal == 1 else "FINAL" if ordinal == len(line) else "MEDIAL",
                "previous": "<BOS>" if ordinal == 1 else line[ordinal - 2]["eva"],
                "following": "<EOS>" if ordinal == len(line) else line[ordinal]["eva"],
                "zl3b_line": before["zl3b_line"], "it2a_line": cross_by_locus[locus]["it2a_clean"],
                "rf1b_line": cross_by_locus[locus]["rf1b_clean"], "reader_support": support,
                "reader_exact": reader_exact, "split_normalized": normalized,
                "before_gloss_de": before_glosses[ordinal - 1], "after_gloss_de": after_glosses[ordinal - 1],
                "known_other_tokens": known_other, "clean_known_other_tokens": clean_other,
                "local_before_de": before["token_glosses_de"], "local_after_de": after["token_glosses_de"],
                "hard_collision": 0, "verdict": verdict,
            })
            if support != "ALL_THREE_EXACT":
                variant_rows.append({
                    "surface": surface, "page": member["page"], "locus": locus,
                    "zl3b_line": before["zl3b_line"], "it2a_line": cross_by_locus[locus]["it2a_clean"],
                    "rf1b_line": cross_by_locus[locus]["rf1b_clean"], "reader_support": support,
                    "working_meaning_de": spec_row["working_meaning_de"],
                    "decision": "RETAIN_EXACT_ZL3B_WITH_READER_WARNING",
                })

        accepted_dictionary_rows.append(dictionary_row(spec_row, round_number, len(members), exact_count))
        current_one_by_locus = {row["locus"]: row for row in one_unknown}
        for locus in sorted(set(current_one_by_locus) - seen_one_loci):
            newly_exposed_rows.append({
                "introduced_round": round_number, "enabled_by_surface": surface,
                **{field: current_one_by_locus[locus][field] for field in ONE_FIELDS},
            })
        seen_one_loci.update(current_one_by_locus)
        post_dictionary = [*base_dictionary, *accepted_dictionary_rows]
        ledger_rows.append({
            "round": round_number, "surface": surface, "tier": spec_row["tier"], "decision": "ACCEPT_V30_EXACT_WHOLE",
            "decision_reason": spec_row["decision_basis"], "pre_dictionary_entries": len(post_dictionary) - 1,
            "post_dictionary_entries": len(post_dictionary), "occurrences": len(members),
            "all_reader_exact": exact_count, "split_normalized": split_count,
            "reader_variant": len(members) - split_count, "hard_collisions": 0,
            "complete_before": len(pre_complete), "complete_after": len(complete),
            "strict_complete_after": sum(int(row["strict_complete"]) for row in complete),
            "one_unknown_before": len(pre_one), "one_unknown_after": len(one_unknown),
            "new_complete_loci": "|".join(new_complete_loci) or "NONE",
        })
        target_deck.append({
            "candidate_id": f"G653-C{round_number:02d}", "candidate_order": round_number,
            "surface": surface, "source_locus": spec_row["source_locus"], "strict_source": spec_row["strict_source"],
            "family": spec_row["family"], "acceptance_tier": spec_row["tier"],
            "working_meaning_de": spec_row["working_meaning_de"], "composition": spec_row["composition"],
            "rival_de": spec_row["rival_de"], "occurrences": len(members),
            "pages": len({row["page"] for row in members}), "reader_exact_occurrences": exact_count,
            "split_normalized_occurrences": split_count, "decision": "ACCEPT_V30_EXACT_WHOLE",
            "decision_basis": spec_row["decision_basis"], "strongest_counterargument": spec_row["counterargument"],
        })
        round_rows.append({
            "round": round_number, "surface": surface, "tier": spec_row["tier"],
            "dictionary_entries": len(post_dictionary), "dictionary_sha256": canonical_hash(post_dictionary),
            **metrics(coverage, one_unknown, complete, glossary),
        })

    final_dictionary = [*base_dictionary, *accepted_dictionary_rows]
    final_coverage, final_one, _, final_complete = g637.build_line_coverage(
        by_line, glossary, exact, boundary, cross_by_locus,
    )
    final_by_locus = {row["locus"]: row for row in final_coverage}
    base_by_locus = {row["locus"]: row for row in base_coverage}
    final_complete_by_locus = {row["locus"]: row for row in final_complete}
    final_metrics = metrics(final_coverage, final_one, final_complete, glossary)
    final_gloss_rows = [
        {key: row[key] for key in ("surface", "working_meaning_de", "source", "strength", "scope_state", "priority")}
        for row in sorted(glossary.values(), key=lambda item: str(item["surface"]))
    ]
    accepted_defaults = [{
        "surface": row["entry"].split("@", 1)[0], **row,
        "source_locus": next(item["source_locus"] for item in target_deck if item["surface"] == row["entry"].split("@", 1)[0]),
        "occurrences": next(item["occurrences"] for item in target_deck if item["surface"] == row["entry"].split("@", 1)[0]),
        "acceptance_tier": next(item["acceptance_tier"] for item in target_deck if item["surface"] == row["entry"].split("@", 1)[0]),
    } for row in accepted_dictionary_rows]

    risk_rows = [{
        "surface": row["surface"], "acceptance_tier": row["acceptance_tier"],
        "working_meaning_de": row["working_meaning_de"], "rival_de": row["rival_de"],
        "strongest_support": row["decision_basis"], "strongest_counterargument": row["strongest_counterargument"],
        "replacement_trigger": (
            "replace the whole default if a better shared-head value explains every sister or if direct reader boundaries require a competing segmentation"
        ),
    } for row in target_deck]

    reality_rows: list[dict[str, object]] = []
    for strict_hole in strict_hole_rows:
        surface, locus = strict_hole["unknown_surface"], strict_hole["locus"]
        row = final_by_locus[locus]
        reality_rows.append({
            "surface": surface, "page": row["page"], "locus": locus,
            "strict_complete": final_complete_by_locus[locus]["strict_complete"],
            "zl3b_line": row["zl3b_line"], "tokenwise_translation_de": row["token_glosses_de"],
            "smoothed_working_reading_de": SMOOTHED_SOURCE_LINES[locus],
            "acceptance_tier": next(item["acceptance_tier"] for item in target_deck if item["surface"] == surface),
        })
    reality_rows.sort(key=lambda row: row["locus"])

    affected_rows: list[dict[str, object]] = []
    for locus in sorted(by_line):
        present = list(dict.fromkeys(
            token["eva"] for token in by_line[locus] if token["eva"] in targets | revision_surfaces
        ))
        if not present:
            continue
        row = final_by_locus[locus]
        affected_rows.append({
            "page": row["page"], "locus": locus, "target_surfaces": "|".join(present),
            "zl3b_line": row["zl3b_line"], "v29_tokenwise_de": base_by_locus[locus]["token_glosses_de"],
            "v30_tokenwise_de": row["token_glosses_de"],
            "v30_working_reading_de": "; ".join(split_pipe(row["token_glosses_de"])),
            "complete_v30": int(row["unknown_tokens"]) == 0,
        })

    new_complete_rows: list[dict[str, object]] = []
    for locus in sorted(set(final_complete_by_locus) - base_complete_loci):
        row = final_by_locus[locus]
        present = list(dict.fromkeys(token["eva"] for token in by_line[locus] if token["eva"] in targets))
        new_complete_rows.append({
            "page": row["page"], "locus": locus, "strict_complete": final_complete_by_locus[locus]["strict_complete"],
            "enabled_by_surfaces": "|".join(present), "zl3b_line": row["zl3b_line"],
            "literal_v30_de": "; ".join(split_pipe(row["token_glosses_de"])),
            "curated_source_reading_de": SMOOTHED_SOURCE_LINES.get(locus, "NOT_CURATED_SOURCE_LINE"),
        })

    write_tsv(output_dir / "PAGE_ALLOWLIST.tsv", [{"page": page} for page in sorted(pages)], ("page",))
    write_tsv(output_dir / "TARGET_DECISION_DECK.tsv", target_deck, (
        "candidate_id", "candidate_order", "surface", "source_locus", "strict_source", "family",
        "acceptance_tier", "working_meaning_de", "composition", "rival_de", "occurrences", "pages",
        "reader_exact_occurrences", "split_normalized_occurrences", "decision", "decision_basis",
        "strongest_counterargument",
    ))
    write_tsv(output_dir / "FAMILY_EVIDENCE_ATLAS.tsv", family_rows, (
        "family", "surface", "composition", "predicted_reading_de", "zl3b_occurrences", "pages",
        "reader_exact_occurrences", "split_normalized_occurrences", "planned_status", "final_status",
    ))
    write_tsv(output_dir / "BOUNDARY_BRIDGE_ATLAS.tsv", bridge_rows, (
        "bridge_id", "family", "page", "locus", "diagnostic_surface", "zl3b_line",
        "it2a_line", "rf1b_line", "supports",
    ))
    write_tsv(output_dir / "RISK_AND_RIVAL_REGISTER.tsv", risk_rows, (
        "surface", "acceptance_tier", "working_meaning_de", "rival_de", "strongest_support",
        "strongest_counterargument", "replacement_trigger",
    ))
    write_tsv(output_dir / "ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv", audit_rows, (
        "audit_id", "round", "surface", "tier", "page", "locus", "section", "language", "hand",
        "token_ordinal", "line_position", "previous", "following", "zl3b_line", "it2a_line", "rf1b_line",
        "reader_support", "reader_exact", "split_normalized", "before_gloss_de", "after_gloss_de",
        "known_other_tokens", "clean_known_other_tokens", "local_before_de", "local_after_de",
        "hard_collision", "verdict",
    ))
    write_tsv(output_dir / "READER_VARIANT_AUDIT.tsv", variant_rows, (
        "surface", "page", "locus", "zl3b_line", "it2a_line", "rf1b_line", "reader_support",
        "working_meaning_de", "decision",
    ))
    write_tsv(output_dir / "SEQUENTIAL_DECISION_LEDGER.tsv", ledger_rows, (
        "round", "surface", "tier", "decision", "decision_reason", "pre_dictionary_entries",
        "post_dictionary_entries", "occurrences", "all_reader_exact", "split_normalized", "reader_variant",
        "hard_collisions", "complete_before", "complete_after", "strict_complete_after", "one_unknown_before",
        "one_unknown_after", "new_complete_loci",
    ))
    write_tsv(output_dir / "ROUND_COVERAGE_COUNTS.tsv", round_rows, (
        "round", "surface", "tier", "dictionary_entries", "dictionary_sha256", "physical_lines",
        "known_token_positions", "unknown_token_positions", "complete_multi_token_lines", "strict_complete_lines",
        "one_unknown_lines", "strict_one_unknown_lines", "exact_glossary_surfaces",
    ))
    write_tsv(output_dir / "ACCEPTED_WHOLE_SURFACE_DEFAULTS.tsv", accepted_defaults, (
        "surface", "entry", "kind", "working_meaning_de", "composition", "context_rule", "status",
        "source_locus", "occurrences", "acceptance_tier",
    ))
    write_tsv(output_dir / "SOURCE_PASSAGE_REALITY_CHECK.tsv", reality_rows, (
        "surface", "page", "locus", "strict_complete", "zl3b_line", "tokenwise_translation_de",
        "smoothed_working_reading_de", "acceptance_tier",
    ))
    write_tsv(output_dir / "AFFECTED_LINE_TRANSLATIONS.tsv", affected_rows, (
        "page", "locus", "target_surfaces", "zl3b_line", "v29_tokenwise_de", "v30_tokenwise_de",
        "v30_working_reading_de", "complete_v30",
    ))
    write_tsv(output_dir / "NEWLY_COMPLETED_LINES.tsv", new_complete_rows, (
        "page", "locus", "strict_complete", "enabled_by_surfaces", "zl3b_line", "literal_v30_de",
        "curated_source_reading_de",
    ))
    write_tsv(output_dir / "NEWLY_EXPOSED_ONE_HOLE_LINES.tsv", newly_exposed_rows, (
        "introduced_round", "enabled_by_surface", *ONE_FIELDS,
    ))
    write_tsv(output_dir / "V30_EXACT_TOKEN_GLOSSARY.tsv", final_gloss_rows, (
        "surface", "working_meaning_de", "source", "strength", "scope_state", "priority",
    ))
    write_tsv(output_dir / "ALL_LINE_CONCRETE_COVERAGE_V30.tsv", final_coverage, COVERAGE_FIELDS)
    write_tsv(output_dir / "COMPLETE_PASSAGES_V30.tsv", final_complete, (
        "rank", "strict_complete", *COVERAGE_FIELDS, "working_translation_de",
    ))
    write_tsv(output_dir / "ONE_UNKNOWN_PASSAGES_V30.tsv", final_one, ONE_FIELDS)
    write_tsv(output_dir / "WORKING_DICTIONARY_V30.tsv", final_dictionary, (
        "entry", "kind", "working_meaning_de", "composition", "context_rule", "status",
    ))

    output_paths = [output_dir / name for name in OUTPUT_NAMES]
    input_paths = (
        G652_RUN, G652_ALLOW, G652_COVERAGE, G652_COMPLETE, G652_ONE,
        G652_GLOSSARY, G652_DICTIONARY, G652_RESULT, G652_REPORT,
        G628_REPORT, G633_REPORT, G636_REPORT, G642_REPORT, G648_REPORT, G651_REPORT,
        TOKENS_REL, CROSS_REL,
    )
    verdicts = Counter(row["verdict"] for row in audit_rows)
    tiers = Counter(row["acceptance_tier"] for row in target_deck)
    result_core = {
        "schema": "GDT653_STRICT_BOUNDARY_COMPOUNDS_RESULT_V1",
        "experiment_id": "GDT653", "status": STATUS,
        "guard": {"f1r": "EXCLUDED", "f84": "FORBIDDEN", "f84r": "FORBIDDEN", "new_pages": 0,
                  "new_images": 0, "allowed_pages": len(pages), "token_query": token_stats, "cross_query": cross_stats},
        "target_run": {
            "candidates": len(target_deck), "accepted_exact_wholes": len(target_deck),
            "accepted_surfaces": [row["surface"] for row in target_deck],
            "strict_v29_holes_closed": len(strict_hole_rows), "acceptance_tiers": dict(sorted(tiers.items())),
            "audited_occurrences": len(audit_rows),
            "all_reader_exact_occurrences": sum(int(row["reader_exact"]) for row in audit_rows),
            "split_normalized_occurrences": sum(int(row["split_normalized"]) for row in audit_rows),
            "reader_variant_warnings": sum(row["verdict"] == "READER_VARIANT_WARNING" for row in audit_rows),
            "hard_collisions": sum(int(row["hard_collision"]) for row in audit_rows),
            "verdicts": dict(sorted(verdicts.items())),
            "held_support_or_absent_cells": sorted(
                row["surface"] for row in family_rows
                if row["final_status"] not in {"ACCEPTED_V30", "V29_ANCHOR"}
            ),
        },
        "compound_packet": {
            "separated_counterpart_targets": ["orol"],
            "reader_split_targets": ["sodal"],
            "learned_head_targets": ["chckhal", "octhdy", "chdaly"],
            "singleton_composition_target": ["skar"],
            "upstream_consistency_conflicts": [
                "qokar is V29 heiße Portion but its visible K+AR tail predicts heiße Fraktion I; GDT653 records but does not silently rewrite its recurrent old card"
            ],
            "structural_tags_not_free_words": [
                "OR_PORTION", "OL_MATERIAL", "CKH_LEARNED", "AL_BOUND", "O_PREP",
                "CTH_LEARNED", "DAL_LEARNED", "S_SEED", "K_HEISS", "AR_FRACTION_I",
            ],
        },
        "coverage": {"base": base_metrics, "final": final_metrics,
                     "newly_completed_lines": len(new_complete_rows),
                     "newly_exposed_one_hole_lines": len(newly_exposed_rows),
                     "affected_lines": len(affected_rows)},
        "working_dictionary": {"v29_entries": len(base_dictionary), "v30_entries": len(final_dictionary),
                               "accepted_tail_entries": len(accepted_dictionary_rows),
                               "v29_prefix_sha256": canonical_hash(base_dictionary),
                               "v30_sha256": canonical_hash(final_dictionary),
                               "v29_glossary_surfaces": len(base_glossary), "v30_glossary_surfaces": len(glossary)},
        "claim_boundary": (
            "GDT653 is an exploratory working translation, not a solved plaintext. It adds six observed exact-whole compounds and closes six strict V29 holes. "
            "OROL has repeated separated OR OL counterparts and SODAL has one reader split; CHCKHAL, OCTHDY and CHDALY inherit explicitly learned family heads; SKAR is a visibly marked "
            "singleton composition. All inner tags remain family-bound and every rival stays replaceable. Supporting sister surfaces are audited but not exported. "
            "The recurrent upstream QOKAR Portion/AR-Fraktion conflict remains explicit and is not silently revised in this six-card pass. "
            "No free component, global suffix, absent-cell meaning, plaintext, phonetics, language, exact ingredient identity, f1r, new page or new image is asserted."
        ),
        "inputs": {str(path): sha256(ROOT / path) for path in input_paths},
        "outputs": {str(BASE_REL / "artifacts" / path.name): sha256(path) for path in output_paths},
    }
    result = {**result_core, "content_sha256": canonical_hash(result_core)}
    (output_dir / "RESULT.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8",
    )
    return result


def main() -> int:
    result = build(ART)
    target, coverage = result["target_run"], result["coverage"]
    print(
        f"GDT653 built: accepted={target['accepted_exact_wholes']} audits={target['audited_occurrences']} "
        f"known={coverage['final']['known_token_positions']} complete={coverage['final']['complete_multi_token_lines']} "
        f"strict={coverage['final']['strict_complete_lines']} one_unknown={coverage['final']['one_unknown_lines']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
