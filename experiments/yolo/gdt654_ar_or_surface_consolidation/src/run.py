#!/usr/bin/env python3
"""Build GDT654: consolidate the recurrent AR/OR whole-surface system."""
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
BASE_REL = Path("experiments/yolo/gdt654_ar_or_surface_consolidation")
ART = ROOT / BASE_REL / "artifacts"
G653 = Path("experiments/yolo/gdt653_strict_v29_boundary_compounds")
G653_RUN = G653 / "src/run.py"
G653_ALLOW = G653 / "artifacts/PAGE_ALLOWLIST.tsv"
G653_COVERAGE = G653 / "artifacts/ALL_LINE_CONCRETE_COVERAGE_V30.tsv"
G653_COMPLETE = G653 / "artifacts/COMPLETE_PASSAGES_V30.tsv"
G653_ONE = G653 / "artifacts/ONE_UNKNOWN_PASSAGES_V30.tsv"
G653_GLOSSARY = G653 / "artifacts/V30_EXACT_TOKEN_GLOSSARY.tsv"
G653_DICTIONARY = G653 / "artifacts/WORKING_DICTIONARY_V30.tsv"
G653_RESULT = G653 / "artifacts/RESULT.json"
G653_REPORT = G653 / "REPORT.md"
G628_REPORT = Path("experiments/yolo/gdt628_chol_measure_frame/REPORT.md")
G636_REPORT = Path("experiments/yolo/gdt636_residual_four_head_semantics/REPORT.md")
G640_REPORT = Path("experiments/yolo/gdt640_downstream_component_prediction/REPORT.md")
G648_REPORT = Path("experiments/yolo/gdt648_strict_v24_hole_completion/REPORT.md")
G649_REPORT = Path("experiments/yolo/gdt649_strict_v25_hole_completion/REPORT.md")

spec = importlib.util.spec_from_file_location("gdt653_builder_for_gdt654", ROOT / G653_RUN)
if spec is None or spec.loader is None:
    raise RuntimeError("cannot load GDT653 builder")
g653 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g653)
TOKENS_REL = g653.TOKENS_REL
CROSS_REL = g653.CROSS_REL
COVERAGE_FIELDS = g653.COVERAGE_FIELDS
ONE_FIELDS = g653.ONE_FIELDS

STATUS = "PASS_19_AR_OR_SURFACES__V31"
GENERIC_FILLER = re.compile(
    r"arbeitsgut|arbeitschritt|arbeitsschritt|arbeitsmittel|arbeitsstoff|"
    r"arbeitsobjekt|werkzeug|produkt weiter|f.hre .* aus|leite .* weiter",
    re.IGNORECASE,
)


def target(
    surface: str,
    mode: str,
    meaning: str,
    composition: str,
    rival: str,
    basis: str,
    counterargument: str,
) -> dict[str, str]:
    return {
        "surface": surface,
        "mode": mode,
        "working_meaning_de": meaning,
        "composition": composition,
        "rival_de": rival,
        "decision_basis": basis,
        "counterargument": counterargument,
    }


TARGET_SPECS = (
    target(
        "ar", "NEW_EXACT_WHOLE", "Drogenfraktion I", "AR_FRACTION_I",
        "Teil-/Sortierklasse I",
        "321 naked occurrences, two direct A R/AR reader splits and P/S/R/L material-head sisters",
        "AR may encode a technical form class rather than an ordinary-language fraction noun",
    ),
    target(
        "or", "REVISE_AMBIGUOUS_TO_EXACT", "Drogenportion", "OR_PORTION",
        "Teil-/Nominalträger",
        "321 naked occurrences, one direct O R/OR reader split, 48 AR/OR co-occurrence lines and POR/SOR/ROR/LOR sisters",
        "OR can remain a nominal carrier whose more specific portion value is supplied by context",
    ),
    target(
        "kar", "NEW_EXACT_WHOLE", "heiße Drogenfraktion I", "K_HEISS+AR_FRACTION_I",
        "heiße Drogenportion",
        "57 occurrences extend AR with K and contrast with observed KOR",
        "KAR may be a learned whole or K may mark a broader preparation state rather than heat",
    ),
    target(
        "kor", "NEW_EXACT_WHOLE", "heiße Drogenportion", "K_HEISS+OR_PORTION",
        "heißer Drogenteil",
        "20 occurrences occupy the OR partner cell beside KAR and the POR/SOR/ROR/LOR portion set",
        "KOR may be a learned head rather than transparent K plus OR",
    ),
    target(
        "tar", "NEW_EXACT_WHOLE", "kalte Drogenfraktion I", "T_KALT+AR_FRACTION_I",
        "kalte Stoffform I",
        "40 occurrences form the cold counterpart of KAR and contrast with observed TOR",
        "TAR may be a learned whole or AR may be a form class rather than a fraction",
    ),
    target(
        "tor", "NEW_EXACT_WHOLE", "kalte Drogenportion", "T_KALT+OR_PORTION",
        "kalter Drogenteil",
        "17 occurrences occupy the OR partner cell beside TAR",
        "TOR may be an indivisible learned head rather than transparent T plus OR",
    ),
    target(
        "oar", "NEW_EXACT_WHOLE", "Drogenfraktion I im Ansatz", "O_PREP+AR_FRACTION_I",
        "Ansatzform I",
        "ten occurrences occupy the naked O+AR cell beside OOR and the populated O+K/T grid",
        "OAR may be a learned preparation form without a separable AR value",
    ),
    target(
        "oor", "NEW_EXACT_WHOLE", "Drogenportion im Ansatz", "O_PREP+OR_PORTION",
        "Zubereitungsteil",
        "two all-reader exact occurrences occupy the O+OR partner of OAR",
        "two tokens are too few to distinguish a productive compound from a learned whole",
    ),
    target(
        "okar", "NEW_EXACT_WHOLE", "heiße Drogenfraktion I im Ansatz", "O_PREP+K_HEISS+AR_FRACTION_I",
        "heiße Drogenportion im Ansatz",
        "119 occurrences, two reader splits exposing O+KAR and the complete OKAR/OKOR/OTAR/OTOR square",
        "the direct splits establish O plus KAR but do not independently split K from AR",
    ),
    target(
        "okor", "NEW_EXACT_WHOLE", "heiße Drogenportion im Ansatz", "O_PREP+K_HEISS+OR_PORTION",
        "heißer Zubereitungsteil",
        "24 occurrences occupy the OR partner of OKAR",
        "OKOR may be an indivisible preparation head",
    ),
    target(
        "otar", "NEW_EXACT_WHOLE", "kalte Drogenfraktion I im Ansatz", "O_PREP+T_KALT+AR_FRACTION_I",
        "kalte Ansatzform I",
        "123 occurrences occupy the cold AR cell opposite OKAR",
        "OTAR may be a learned cold preparation form",
    ),
    target(
        "otor", "NEW_EXACT_WHOLE", "kalte Drogenportion im Ansatz", "O_PREP+T_KALT+OR_PORTION",
        "kalter Zubereitungsteil",
        "33 occurrences occupy the OR partner of OTAR",
        "OTOR may be an indivisible preparation head",
    ),
    target(
        "qoar", "NEW_EXACT_WHOLE", "Drogenfraktion I", "QO_SCOPE+AR_FRACTION_I",
        "Drogenfraktion I im QO-Rahmen",
        "seven all-reader exact occurrences occupy the unqualified QO+AR cell beside QOOR",
        "QO may contribute a lexical value suppressed by the short German default",
    ),
    target(
        "qoor", "NEW_EXACT_WHOLE", "Drogenportion", "QO_SCOPE+OR_PORTION",
        "Drogenportion im QO-Rahmen",
        "six occurrences occupy the QO+OR partner of QOAR",
        "QO may contribute a lexical value and one occurrence is reader-variant",
    ),
    target(
        "qokar", "REVISE_CONFLICTING_EXACT", "heiße Drogenfraktion I", "QO_SCOPE+K_HEISS+AR_FRACTION_I",
        "heiße Drogenportion",
        "153 occurrences occupy the AR cell opposite QOKOR; the full QO K/T by AR/OR square is observed",
        "there is no direct internal K/AR split and QO may alter the carrier class",
    ),
    target(
        "qokor", "NEW_EXACT_WHOLE", "heiße Drogenportion", "QO_SCOPE+K_HEISS+OR_PORTION",
        "heißer Drogenteil",
        "29 occurrences occupy the expected OR partner of QOKAR and the two forms co-occur on two lines",
        "QOKOR may be a learned whole and has no direct internal split",
    ),
    target(
        "qotar", "NEW_EXACT_WHOLE", "kalte Drogenfraktion I", "QO_SCOPE+T_KALT+AR_FRACTION_I",
        "kalte Stoffform I",
        "61 occurrences occupy the AR partner of known QOTOR=kalte Drogenportion",
        "two reader variants exchange QOKAR and QOTAR, so K/T identity is not perfect",
    ),
    target(
        "rkar", "NEW_EXACT_WHOLE", "heiße Wurzelfraktion I", "R_ROOT+K_HEISS+AR_FRACTION_I",
        "heiße Wurzelportion",
        "one all-reader exact occurrence co-occurs with LKAR and occupies the R material cell",
        "the singleton cannot independently distinguish productive R+K+AR from an indivisible learned name",
    ),
    target(
        "lkor", "NEW_EXACT_WHOLE", "heiße Holzportion", "L_WOOD+K_HEISS+OR_PORTION",
        "heißer Holzteil",
        "three all-reader exact occurrences are the OR partner of established LKAR=heiße Holzfraktion I",
        "three tokens remain compatible with a learned indivisible name",
    ),
)

TARGET_BY_SURFACE = {row["surface"]: row for row in TARGET_SPECS}
EXPECTED_COUNTS = {
    "ar": (321, 90, 242, 242),
    "or": (321, 114, 235, 235),
    "kar": (57, 42, 42, 42),
    "kor": (20, 20, 13, 13),
    "tar": (40, 33, 33, 33),
    "tor": (17, 17, 12, 12),
    "oar": (10, 9, 9, 9),
    "oor": (2, 2, 2, 2),
    "okar": (119, 55, 91, 93),
    "okor": (24, 20, 16, 16),
    "otar": (123, 58, 110, 110),
    "otor": (33, 29, 24, 24),
    "qoar": (7, 7, 7, 7),
    "qoor": (6, 6, 5, 5),
    "rkar": (1, 1, 1, 1),
    "qokar": (153, 62, 132, 132),
    "qokor": (29, 25, 21, 21),
    "qotar": (61, 36, 53, 53),
    "lkor": (3, 3, 3, 3),
}

# No unattested cell receives a reading. Rows marked ABSENT are retained only
# as visible holes and use NOT_ASSIGNED rather than a predicted translation.
FAMILY_FORMS = (
    ("AR_LADDER", "ar", "AR", "TARGET"),
    ("AR_LADDER", "air", "A+I+R", "SISTER"),
    ("AR_LADDER", "aiir", "A+II+R", "SISTER"),
    ("AR_LADDER", "aiiir", "A+III+R", "ABSENT"),
    ("MATERIAL_AR", "par", "P+AR", "ANCHOR"),
    ("MATERIAL_AR", "pair", "P+AIR", "ANCHOR"),
    ("MATERIAL_AR", "paiir", "P+AIIR", "ANCHOR"),
    ("MATERIAL_AR", "sar", "S+AR", "ANCHOR"),
    ("MATERIAL_AR", "sair", "S+AIR", "ANCHOR"),
    ("MATERIAL_AR", "saiir", "S+AIIR", "ANCHOR"),
    ("MATERIAL_AR", "rar", "R+AR", "ANCHOR"),
    ("MATERIAL_AR", "rair", "R+AIR", "ANCHOR"),
    ("MATERIAL_AR", "raiir", "R+AIIR", "ANCHOR"),
    ("MATERIAL_AR", "lar", "L+AR", "ANCHOR"),
    ("MATERIAL_AR", "lair", "L+AIR", "ANCHOR"),
    ("MATERIAL_AR", "laiir", "L+AIIR", "SISTER"),
    ("MEASURED_AR", "dar", "D+AR", "ANCHOR"),
    ("MEASURED_AR", "dair", "D+AIR", "ANCHOR"),
    ("MEASURED_AR", "daiir", "D+AIIR", "ANCHOR"),
    ("OR_PORTIONS", "or", "OR", "TARGET"),
    ("OR_PORTIONS", "por", "P+OR", "ANCHOR"),
    ("OR_PORTIONS", "sor", "S+OR", "ANCHOR"),
    ("OR_PORTIONS", "ror", "R+OR", "ANCHOR"),
    ("OR_PORTIONS", "lor", "L+OR", "ANCHOR"),
    ("BARE_KT_AR_OR", "kar", "K+AR", "TARGET"),
    ("BARE_KT_AR_OR", "kor", "K+OR", "TARGET"),
    ("BARE_KT_AR_OR", "tar", "T+AR", "TARGET"),
    ("BARE_KT_AR_OR", "tor", "T+OR", "TARGET"),
    ("O_KT_AR_OR", "oar", "O+AR", "TARGET"),
    ("O_KT_AR_OR", "oor", "O+OR", "TARGET"),
    ("O_KT_AR_OR", "okar", "O+K+AR", "TARGET"),
    ("O_KT_AR_OR", "okor", "O+K+OR", "TARGET"),
    ("O_KT_AR_OR", "otar", "O+T+AR", "TARGET"),
    ("O_KT_AR_OR", "otor", "O+T+OR", "TARGET"),
    ("QO_KT_AR_OR", "qoar", "QO+AR", "TARGET"),
    ("QO_KT_AR_OR", "qoor", "QO+OR", "TARGET"),
    ("QO_KT_AR_OR", "qokar", "QO+K+AR", "TARGET"),
    ("QO_KT_AR_OR", "qokor", "QO+K+OR", "TARGET"),
    ("QO_KT_AR_OR", "qotar", "QO+T+AR", "TARGET"),
    ("QO_KT_AR_OR", "qotor", "QO+T+OR", "ANCHOR"),
    ("MATERIAL_K_AR_OR", "lkar", "L+K+AR", "ANCHOR"),
    ("MATERIAL_K_AR_OR", "lkor", "L+K+OR", "TARGET"),
    ("MATERIAL_K_AR_OR", "skar", "S+K+AR", "ANCHOR"),
    ("MATERIAL_K_AR_OR", "skor", "S+K+OR", "ABSENT"),
    ("MATERIAL_K_AR_OR", "rkar", "R+K+AR", "TARGET"),
    ("MATERIAL_K_AR_OR", "rkor", "R+K+OR", "ABSENT"),
    ("LEARNED_HEAD_COLLISION_HOLD", "char", "CH+AR_OR_LEARNED", "HOLD"),
    ("LEARNED_HEAD_COLLISION_HOLD", "chor", "CHOR_LEARNED_OR_CH+OR", "HOLD"),
    ("LEARNED_HEAD_COLLISION_HOLD", "shar", "SH+AR_OR_LEARNED", "HOLD"),
    ("LEARNED_HEAD_COLLISION_HOLD", "shor", "SHOR_LEARNED_OR_SH+OR", "HOLD"),
)

QUALITY_GRID_CORES = (
    ("UNQUALIFIED", ""), ("K", "k"), ("T", "t"), ("CH", "ch"), ("SH", "sh"),
    ("K_CH", "kch"), ("K_SH", "ksh"), ("T_CH", "tch"), ("T_SH", "tsh"),
)
GRID_SPECS = tuple(
    (shell_name, qualifier_name, f"{shell}{core}ar", f"{shell}{core}or")
    for shell_name, shell in (("BARE", ""), ("O", "o"), ("QO", "qo"))
    for qualifier_name, core in QUALITY_GRID_CORES
)

PAIR_SPECS = (
    ("ar", "or", "Drogenfraktion I / Drogenportion"),
    ("kar", "kor", "heiße Drogenfraktion I / heiße Drogenportion"),
    ("tar", "tor", "kalte Drogenfraktion I / kalte Drogenportion"),
    ("okar", "okor", "heiße Fraktion / Portion im Ansatz"),
    ("otar", "otor", "kalte Fraktion / Portion im Ansatz"),
    ("qokar", "qokor", "heiße Drogenfraktion / Drogenportion"),
    ("qotar", "qotor", "kalte Drogenfraktion / Drogenportion"),
    ("lkar", "lkor", "heiße Holzfraktion / Holzportion"),
    ("ar", "qokar", "Drogenfraktion I / heiße Drogenfraktion I"),
    ("or", "qokar", "Drogenportion / heiße Drogenfraktion I"),
)

BOUNDARY_SPECS = (
    ("G654-B01", "DIRECT_TARGET_SPLIT", "f113v.29", "a r / ar", "reader split directly exposes AR"),
    ("G654-B02", "DIRECT_TARGET_SPLIT", "f113v.41", "a r / ar", "second reader split directly exposes AR"),
    ("G654-B03", "DIRECT_TARGET_SPLIT", "f102v2.19", "o r / or", "reader split directly exposes OR"),
    ("G654-B04", "DIRECT_SUPERFORM_SPLIT", "f105r.4", "okar / ok ar", "reader split exposes O plus KAR"),
    ("G654-B05", "DIRECT_SUPERFORM_SPLIT", "f108v.10", "okar / o kar", "second reader split exposes O plus KAR"),
    ("G654-B06", "DIRECT_MATERIAL_SPLIT", "f76r.49", "l kar / lkar", "reader split exposes L plus KAR"),
    ("G654-W01", "WARNING_NO_FUSED_OR", "f36r.5", "o r / s r", "warning only: no fused OR token in any reader"),
    ("G654-W02", "WARNING_SUPERFORM_ONLY", "f111r.21", "o r / oxor", "warning only: other readers use a superform, not exact OR"),
)

REALITY_LOCI = {
    "ar": ("f55r.10", "f103v.23", "f33v.9"),
    "or": ("f20v.4", "f6r.12", "f103r.17"),
    "kar": ("f46r.12", "f58v.31", "f6r.2"),
    "qokar": ("f55r.10", "f83v.26", "f89v1.12"),
    "rkar": ("f103r.5",),
}

CURATED_COMPLETE_READINGS = {
    "f37r.7": "Samenportion; in der Gradmitte trocken; heiße Drogenportion; anschließend dieselbe Portionsklasse im QO-Rahmen; Menge/Portion III.",
    "f81v.5": "Im Ansatz heiß, Grad III; Grad-/Maßwert III; kalt im Zubereitungsrahmen, Grad II; trockenes Arzneikompositum am Gradanfang; abgeschlossener heißer Ansatz am Gradende; heiß am Gradanfang; heiße Drogenfraktion I; erneut Grad-/Maßwert III; heiße Drogenfraktion I im Ansatz.",
    "f86v6.35": "Samenfraktion I, Menge III; kalte Drogenfraktion I im Ansatz; getrockneter Ansatz; kalt Grad III; heiß Grad III; Gut/Ansatz; kalt in der Gradmitte; erneut heiß Grad III; heiße Drogenfraktion I im Ansatz; erneut Gut/Ansatz.",
    "f99v.3": "Kalte Drogenportion im Ansatz; am Gradanfang trocken.",
    "f89v1.12": "Heiße Drogenfraktion I, Zubereitungsdosis III.",
    "f20v.4": "Feuchtansatz: eine Drogenportion, Menge III; feuchtes Gut, Qualitätsgrad III.",
    "f6r.12": "Eine Drogenportion feuchten Guts; eine Handvoll Blatt-/Krautansatz; Pflanzen-/Reproduktionsteil; CTH-Drogenmaterial.",
    "f103r.17": "Samenfraktion I: feucht und heiß in der Gradmitte; am Gradende heiß abgeschlossen, danach weiter heiß; trockenes Arzneikompositum am Gradanfang; heiße Substanz; kalter Ansatz am Gradanfang; eine Drogenportion, Menge III.",
    "f80r.43": "Samenportion; feuchtes Arzneikompositum am Gradanfang; heiße Drogenfraktion I; trockenes Arzneikompositum am Gradanfang; im Ansatz heiß, Grad II; erneut feuchtes Arzneikompositum am Gradanfang; heiß bis Gradende; rohes Drogenholz.",
    "f82v.36": "Samencharge III: feucht in der Gradmitte; am Gradende heiß abgeschlossen; heiße Drogenfraktion I; feuchtes CTH-Drogenmaterial, Form I, Bindungsstufe II; heiß, Grad III; abgekühltes Material; getrockneter Wurzelstoff.",
    "f77r.19": "Am Gradende heiß abgeschlossen; Drogenholz, trocken gebunden, Form I; eingeweichtes Drogenholz, Form II; zweimal am Gradende heiß abgeschlossen; heiße Drogenfraktion I; am Gradende heiß; Drogenholz, Charge III; trocken in der Gradmitte.",
    "f80r.18": "Pulvercharge III; feuchtes Material; heiß, Grad II; trocken-kalt gebundene Form; am Gradende heiß abgeschlossen; heiße Drogenfraktion I; feuchte CTH-Materialform; kaltes Material; feuchtes CTH-Drogenmaterial; heiß, Grad II; heißes Material.",
    "f35r.5": "Kalt-trockene Drogenportion im Ansatz; Feuchtansatz; kalt und trocken am Gradende; Saatgut, trocken gebunden, Form II; Gradwerte III und II; eine Drogenportion.",
    "f76r.56": "Heiß, Grad III; Drogengut; in der Gradmitte feucht abgeschlossen; am Gradende heiß; eine Drogenportion; am Gradanfang feucht abgeschlossen.",
}

CURATED_READER_NOTES = {
    "f37r.7": "ZL3b/IT2a/RF1b exact",
    "f81v.5": "ZL3b/IT2a line exact; RF1b segments edge forms differently but KAR and OKAR remain stable",
    "f86v6.35": "IT2a reads final OTAR rather than ZL3b/RF1b OKAR; final hot/cold value is reader-unstable",
    "f99v.3": "RF1b reads OTAR rather than ZL3b/IT2a OTOR; fraction versus portion is reader-unstable",
}

OUTPUT_NAMES = (
    "PAGE_ALLOWLIST.tsv", "TARGET_DECISION_DECK.tsv", "FAMILY_CONTRAST_ATLAS.tsv",
    "FULL_AR_OR_PAIR_GRID.tsv",
    "PAIR_CONTRAST_COUNTS.tsv", "BOUNDARY_EVIDENCE_ATLAS.tsv", "REVISION_LEDGER.tsv",
    "ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv",
    "READER_VARIANT_AUDIT.tsv", "ROUND_COVERAGE_COUNTS.tsv",
    "ACCEPTED_WHOLE_SURFACE_DEFAULTS.tsv", "SOURCE_PASSAGE_REALITY_CHECK.tsv",
    "CURATED_COMPLETE_PASSAGE_READINGS.tsv",
    "AFFECTED_LINE_TRANSLATIONS.tsv", "NEWLY_COMPLETED_LINES.tsv",
    "NEWLY_EXPOSED_ONE_HOLE_LINES.tsv", "V31_EXACT_TOKEN_GLOSSARY.tsv",
    "ALL_LINE_CONCRETE_COVERAGE_V31.tsv", "COMPLETE_PASSAGES_V31.tsv",
    "ONE_UNKNOWN_PASSAGES_V31.tsv", "WORKING_DICTIONARY_V31.tsv",
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


def dictionary_row(spec_row: dict[str, str], round_number: int, occurrences: int, exact_count: int) -> dict[str, object]:
    return {
        "entry": f"{spec_row['surface']}@GDT654_EXACT_WHOLE",
        "kind": f"EXACT_ZL3B_WHOLE_{spec_row['mode']}",
        "working_meaning_de": spec_row["working_meaning_de"],
        "composition": spec_row["composition"],
        "context_rule": (
            f"exact complete surface only; mode={spec_row['mode']}; {occurrences} audited occurrences; "
            f"{exact_count} all-reader exact; supersedes current glossary card without deleting material history"
        ),
        "status": f"NEW_V31_ACCEPTED_ROUND_{round_number:02d}",
    }


def line_position(line: list[dict[str, object]], token_index: int) -> int:
    for ordinal, token in enumerate(line, 1):
        if int(token["token_index"]) == token_index:
            return ordinal
    raise RuntimeError("token position not found")


def build(output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    pages = {row["page"] for row in read_tsv(ROOT / G653_ALLOW)}
    if "f1r" in pages or any(page.startswith("f84") for page in pages):
        raise RuntimeError("allow-list contains excluded or forbidden page")
    guarded_query = g653.g637.g636.g635.g634.g633.g632.g631.guarded_query
    token_rows, token_stats = guarded_query(
        TOKENS_REL, pages, "page,locus,token_index,eva,section,language,hand",
    )
    cross_rows, cross_stats = guarded_query(
        CROSS_REL, pages, "page,locus,all_three_present,all_present_exact,zl3b_clean,it2a_clean,rf1b_clean",
    )
    cross_by_locus = {row["locus"]: row for row in cross_rows}
    by_line, _ = g653.g637.g636.g635.g634.g633.g632.g631.line_maps([dict(row) for row in token_rows])
    exact, boundary = g653.g637.g636.g635.g634.stable_maps(token_rows, cross_by_locus)

    base_dictionary = [dict(row) for row in read_tsv(ROOT / G653_DICTIONARY)]
    base_gloss_rows = read_tsv(ROOT / G653_GLOSSARY)
    base_glossary = {row["surface"]: dict(row) for row in base_gloss_rows}
    base_coverage = read_tsv(ROOT / G653_COVERAGE)
    base_complete = read_tsv(ROOT / G653_COMPLETE)
    base_one = read_tsv(ROOT / G653_ONE)
    if (len(base_dictionary), len(base_glossary), len(base_coverage), len(base_complete), len(base_one)) != (491, 420, 4128, 119, 160):
        raise RuntimeError("GDT653 V30 base counts changed")
    replay_coverage, replay_one, _, replay_complete = g653.g637.build_line_coverage(
        by_line, base_glossary, exact, boundary, cross_by_locus,
    )
    if (string_rows(replay_coverage) != string_rows(base_coverage)
            or string_rows(replay_complete) != string_rows(base_complete)
            or string_rows(replay_one) != string_rows(base_one)):
        raise RuntimeError("GDT653 V30 editions do not replay")
    base_metrics = metrics(replay_coverage, replay_one, replay_complete, base_glossary)
    expected_base = {
        "physical_lines": 4128, "known_token_positions": 14973,
        "unknown_token_positions": 17366, "complete_multi_token_lines": 119,
        "strict_complete_lines": 73, "one_unknown_lines": 160,
        "strict_one_unknown_lines": 34, "exact_glossary_surfaces": 420,
    }
    if base_metrics != expected_base:
        raise RuntimeError(f"GDT653 V30 metrics changed: {base_metrics!r}")

    if any(GENERIC_FILLER.search(row["working_meaning_de"]) for row in TARGET_SPECS):
        raise RuntimeError("generic filler in GDT654 target deck")
    new_surfaces = tuple(row["surface"] for row in TARGET_SPECS if row["mode"].startswith("NEW"))
    if any(surface in base_glossary for surface in new_surfaces):
        raise RuntimeError("new GDT654 target unexpectedly exists in V30 glossary")
    if base_glossary.get("or", {}).get("scope_state") != "AMBIGUOUS_ACTIVE_RIVAL":
        raise RuntimeError("V30 OR ambiguity changed")
    if base_glossary.get("qokar", {}).get("working_meaning_de") != "heiße Portion":
        raise RuntimeError("V30 QOKAR conflict changed")

    token_counts = Counter(str(row["eva"]) for row in token_rows)
    for surface, expected in EXPECTED_COUNTS.items():
        members = [row for row in token_rows if row["eva"] == surface]
        observed = (
            len(members), len({row["page"] for row in members}),
            sum(exact[row["locus"], int(row["token_index"])] for row in members),
            sum(boundary[row["locus"], int(row["token_index"])] for row in members),
        )
        if observed != expected:
            raise RuntimeError(f"target count drift: {surface}: {observed!r}")

    family_rows: list[dict[str, object]] = []
    for family, surface, decomposition, role in FAMILY_FORMS:
        members = [row for row in token_rows if row["eva"] == surface]
        base_row = base_glossary.get(surface)
        target_row = TARGET_BY_SURFACE.get(surface)
        final_meaning = (
            target_row["working_meaning_de"] if target_row else
            base_row["working_meaning_de"] if base_row else "NOT_ASSIGNED"
        )
        family_rows.append({
            "family": family, "surface": surface, "decomposition": decomposition, "role": role,
            "v30_meaning_de": base_row["working_meaning_de"] if base_row else "OPEN",
            "v31_meaning_de": final_meaning,
            "zl3b_occurrences": len(members), "pages": len({row["page"] for row in members}),
            "reader_exact_occurrences": sum(exact[row["locus"], int(row["token_index"])] for row in members),
            "split_normalized_occurrences": sum(boundary[row["locus"], int(row["token_index"])] for row in members),
            "final_status": (
                "ACCEPTED_V31" if target_row else
                "V30_ANCHOR" if base_row and base_row.get("scope_state") != "AMBIGUOUS_ACTIVE_RIVAL" else
                "OBSERVED_HOLD" if members else "ABSENT_HOLD"
            ),
        })

    def grid_surface_stats(surface: str) -> dict[str, object]:
        members = [row for row in token_rows if row["eva"] == surface]
        base_row = base_glossary.get(surface)
        return {
            "surface": surface, "occurrences": len(members),
            "pages": len({row["page"] for row in members}),
            "exact": sum(exact[row["locus"], int(row["token_index"])] for row in members),
            "normalized": sum(boundary[row["locus"], int(row["token_index"])] for row in members),
            "status": (
                "ACCEPTED_V31" if surface in TARGET_BY_SURFACE else
                "V30_ANCHOR" if base_row and base_row.get("scope_state") != "AMBIGUOUS_ACTIVE_RIVAL" else
                "OBSERVED_HOLD" if members else "ABSENT_HOLD"
            ),
        }

    full_grid_rows: list[dict[str, object]] = []
    for shell, qualifier, ar_surface, or_surface in GRID_SPECS:
        ar_stats, or_stats = grid_surface_stats(ar_surface), grid_surface_stats(or_surface)
        full_grid_rows.append({
            "shell": shell, "qualifier": qualifier,
            "ar_surface": ar_surface, "ar_occurrences": ar_stats["occurrences"],
            "ar_pages": ar_stats["pages"], "ar_reader_exact": ar_stats["exact"],
            "ar_split_normalized": ar_stats["normalized"], "ar_status": ar_stats["status"],
            "or_surface": or_surface, "or_occurrences": or_stats["occurrences"],
            "or_pages": or_stats["pages"], "or_reader_exact": or_stats["exact"],
            "or_split_normalized": or_stats["normalized"], "or_status": or_stats["status"],
        })
    observed_grid_cells = sum(
        int(row["ar_occurrences"] > 0) + int(row["or_occurrences"] > 0) for row in full_grid_rows
    )
    grid_occurrences = sum(int(row["ar_occurrences"]) + int(row["or_occurrences"]) for row in full_grid_rows)
    grid_exact = sum(int(row["ar_reader_exact"]) + int(row["or_reader_exact"]) for row in full_grid_rows)
    grid_normalized = sum(
        int(row["ar_split_normalized"]) + int(row["or_split_normalized"]) for row in full_grid_rows
    )
    if (len(full_grid_rows), observed_grid_cells, grid_occurrences, grid_exact) != (27, 45, 1882, 1516):
        raise RuntimeError("full 54-cell AR/OR grid drift")

    line_surfaces = {locus: {str(token["eva"]) for token in line} for locus, line in by_line.items()}
    pair_rows: list[dict[str, object]] = []
    for first, second, distinction in PAIR_SPECS:
        loci = sorted(locus for locus, surfaces in line_surfaces.items() if first in surfaces and second in surfaces)
        exact_loci = [
            locus for locus in loci
            if int(cross_by_locus[locus]["all_three_present"]) == 1
            and int(cross_by_locus[locus]["all_present_exact"]) == 1
        ]
        pair_rows.append({
            "first_surface": first, "second_surface": second, "required_distinction_de": distinction,
            "cooccurrence_lines": len(loci), "all_reader_exact_lines": len(exact_loci),
            "example_loci": "|".join(loci[:12]) or "NONE",
        })

    boundary_rows: list[dict[str, object]] = []
    for bridge_id, evidence_type, locus, diagnostic, support in BOUNDARY_SPECS:
        row = cross_by_locus.get(locus)
        if row is None:
            raise RuntimeError(f"missing GDT654 boundary locus: {locus}")
        boundary_rows.append({
            "bridge_id": bridge_id, "evidence_type": evidence_type,
            "page": row["page"], "locus": locus, "diagnostic_surface": diagnostic,
            "zl3b_line": row["zl3b_clean"], "it2a_line": row["it2a_clean"],
            "rf1b_line": row["rf1b_clean"], "supports": support,
        })

    glossary = {key: dict(value) for key, value in base_glossary.items()}
    coverage, one_unknown, _, complete = g653.g637.build_line_coverage(
        by_line, glossary, exact, boundary, cross_by_locus,
    )
    base_complete_loci = {row["locus"] for row in base_complete}
    seen_one_loci = {row["locus"] for row in base_one}
    accepted_dictionary_rows: list[dict[str, object]] = []
    target_deck: list[dict[str, object]] = []
    audit_rows: list[dict[str, object]] = []
    variant_rows: list[dict[str, object]] = []
    revision_rows: list[dict[str, object]] = []
    round_rows: list[dict[str, object]] = [{
        "round": 0, "surface": "BASE_V30", "mode": "BASE", "dictionary_entries": len(base_dictionary),
        "dictionary_sha256": canonical_hash(base_dictionary), **base_metrics,
    }]
    newly_exposed_rows: list[dict[str, object]] = []

    for round_number, raw_spec in enumerate(TARGET_SPECS, 1):
        spec_row = {key: str(value) for key, value in raw_spec.items()}
        surface = spec_row["surface"]
        members = [row for row in token_rows if row["eva"] == surface]
        members.sort(key=lambda row: (row["page"], row["locus"], int(row["token_index"])))
        exact_count = sum(exact[row["locus"], int(row["token_index"])] for row in members)
        normalized_count = sum(boundary[row["locus"], int(row["token_index"])] for row in members)
        if len(members) != token_counts[surface] or exact_count == 0:
            raise RuntimeError(f"target occurrence or anchor drift: {surface}")

        pre_coverage, pre_one, pre_complete = coverage, one_unknown, complete
        pre_by_locus = {row["locus"]: row for row in pre_coverage}
        old_gloss = base_glossary.get(surface, {}).get("working_meaning_de", "OPEN")
        g653.g637.set_gloss(
            glossary, surface, spec_row["working_meaning_de"], f"GDT654:{spec_row['mode']}",
            "EXACT_WHOLE_AR_OR_CONSOLIDATION", "KNOWN_EXACT_WHOLE", 150,
        )
        coverage, one_unknown, _, complete = g653.g637.build_line_coverage(
            by_line, glossary, exact, boundary, cross_by_locus,
        )
        post_by_locus = {row["locus"]: row for row in coverage}
        new_complete_loci = sorted({row["locus"] for row in complete} - {row["locus"] for row in pre_complete})
        accepted_dictionary_rows.append(dictionary_row(spec_row, round_number, len(members), exact_count))
        if spec_row["mode"].startswith("REVISE"):
            revision_rows.append({
                "surface": surface, "mode": spec_row["mode"], "v30_meaning_de": old_gloss,
                "v31_meaning_de": spec_row["working_meaning_de"], "occurrences": len(members),
                "reader_exact_occurrences": exact_count, "reason": spec_row["decision_basis"],
            })

        verdicts: Counter[str] = Counter()
        for occurrence, member in enumerate(members, 1):
            locus, token_index = member["locus"], int(member["token_index"])
            line = by_line[locus]
            ordinal = line_position(line, token_index)
            before, after = pre_by_locus[locus], post_by_locus[locus]
            before_glosses, after_glosses = split_pipe(before["token_glosses_de"]), split_pipe(after["token_glosses_de"])
            reader_exact = exact[locus, token_index]
            normalized = boundary[locus, token_index]
            support = "ALL_THREE_EXACT" if reader_exact else "ALL_THREE_SPLIT_NORMALIZED" if normalized else "READER_VARIANT"
            known_other = int(before["known_tokens"]) - int(before["ambiguous_tokens"]) - int(before["reader_unstable_tokens"])
            if support == "READER_VARIANT":
                verdict = "READER_VARIANT_WARNING"
            elif known_other >= 2:
                verdict = "CONCRETE_CONTEXT_COMPATIBLE"
            else:
                verdict = "SHORT_OR_OPAQUE_CONTEXT"
            verdicts[verdict] += 1
            audit_rows.append({
                "audit_id": f"G654-A{round_number:02d}-{occurrence:04d}", "round": round_number,
                "surface": surface, "mode": spec_row["mode"], "page": member["page"], "locus": locus,
                "section": member["section"], "language": member["language"], "hand": member["hand"],
                "token_ordinal": ordinal,
                "line_position": "ONLY" if len(line) == 1 else "INITIAL" if ordinal == 1 else "FINAL" if ordinal == len(line) else "MEDIAL",
                "previous": "<BOS>" if ordinal == 1 else line[ordinal - 2]["eva"],
                "following": "<EOS>" if ordinal == len(line) else line[ordinal]["eva"],
                "zl3b_line": before["zl3b_line"], "it2a_line": cross_by_locus[locus]["it2a_clean"],
                "rf1b_line": cross_by_locus[locus]["rf1b_clean"], "reader_support": support,
                "reader_exact": reader_exact, "split_normalized": normalized,
                "before_gloss_de": before_glosses[ordinal - 1], "after_gloss_de": after_glosses[ordinal - 1],
                "known_other_tokens": known_other, "v30_line_de": before["token_glosses_de"],
                "v31_line_de": after["token_glosses_de"], "hard_collision": 0, "verdict": verdict,
            })
            if support != "ALL_THREE_EXACT":
                variant_rows.append({
                    "surface": surface, "page": member["page"], "locus": locus,
                    "zl3b_line": before["zl3b_line"], "it2a_line": cross_by_locus[locus]["it2a_clean"],
                    "rf1b_line": cross_by_locus[locus]["rf1b_clean"], "reader_support": support,
                    "working_meaning_de": spec_row["working_meaning_de"],
                    "decision": "RETAIN_EXACT_ZL3B_WITH_READER_WARNING",
                })

        current_one_by_locus = {row["locus"]: row for row in one_unknown}
        for locus in sorted(set(current_one_by_locus) - seen_one_loci):
            newly_exposed_rows.append({
                "introduced_round": round_number, "enabled_by_surface": surface,
                **{field: current_one_by_locus[locus][field] for field in ONE_FIELDS},
            })
        seen_one_loci.update(current_one_by_locus)
        post_dictionary = [*base_dictionary, *accepted_dictionary_rows]
        target_deck.append({
            "candidate_id": f"G654-C{round_number:02d}", "candidate_order": round_number,
            "surface": surface, "mode": spec_row["mode"], "v30_meaning_de": old_gloss,
            "v31_meaning_de": spec_row["working_meaning_de"], "composition": spec_row["composition"],
            "rival_de": spec_row["rival_de"], "occurrences": len(members),
            "pages": len({row["page"] for row in members}), "reader_exact_occurrences": exact_count,
            "split_normalized_occurrences": normalized_count, "reader_variant_occurrences": len(members) - normalized_count,
            "decision": "ACCEPT_V31_EXACT_WHOLE", "decision_basis": spec_row["decision_basis"],
            "strongest_counterargument": spec_row["counterargument"],
        })
        round_rows.append({
            "round": round_number, "surface": surface, "mode": spec_row["mode"],
            "dictionary_entries": len(post_dictionary), "dictionary_sha256": canonical_hash(post_dictionary),
            **metrics(coverage, one_unknown, complete, glossary),
        })

    final_dictionary = [*base_dictionary, *accepted_dictionary_rows]
    final_coverage, final_one, _, final_complete = g653.g637.build_line_coverage(
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

    affected_rows: list[dict[str, object]] = []
    targets = set(TARGET_BY_SURFACE)
    for locus in sorted(by_line):
        present = list(dict.fromkeys(token["eva"] for token in by_line[locus] if token["eva"] in targets))
        if not present:
            continue
        row = final_by_locus[locus]
        affected_rows.append({
            "page": row["page"], "locus": locus, "target_surfaces": "|".join(present),
            "zl3b_line": row["zl3b_line"], "v30_tokenwise_de": base_by_locus[locus]["token_glosses_de"],
            "v31_tokenwise_de": row["token_glosses_de"], "complete_v31": int(row["unknown_tokens"]) == 0,
        })

    new_complete_rows: list[dict[str, object]] = []
    for locus in sorted(set(final_complete_by_locus) - base_complete_loci):
        row = final_by_locus[locus]
        present = list(dict.fromkeys(token["eva"] for token in by_line[locus] if token["eva"] in targets))
        new_complete_rows.append({
            "page": row["page"], "locus": locus, "strict_complete": final_complete_by_locus[locus]["strict_complete"],
            "enabled_by_surfaces": "|".join(present), "zl3b_line": row["zl3b_line"],
            "literal_v31_de": "; ".join(split_pipe(row["token_glosses_de"])),
        })

    accepted_defaults = [{
        "surface": row["entry"].split("@", 1)[0], **row,
        "occurrences": next(item["occurrences"] for item in target_deck if item["surface"] == row["entry"].split("@", 1)[0]),
        "acceptance_mode": next(item["mode"] for item in target_deck if item["surface"] == row["entry"].split("@", 1)[0]),
    } for row in accepted_dictionary_rows]

    audit_by_surface_locus: dict[tuple[str, str], dict[str, object]] = {}
    for row in audit_rows:
        audit_by_surface_locus.setdefault((str(row["surface"]), str(row["locus"])), row)
    reality_rows: list[dict[str, object]] = []
    for surface, loci in REALITY_LOCI.items():
        for rank, locus in enumerate(loci, 1):
            row = audit_by_surface_locus.get((surface, locus))
            if row is None:
                raise RuntimeError(f"curated reality locus lacks target {surface}: {locus}")
            final = final_by_locus[locus]
            reality_rows.append({
                "surface": surface, "selection_rank": rank, "page": row["page"], "locus": locus,
                "reader_support": row["reader_support"], "zl3b_line": row["zl3b_line"],
                "tokenwise_v31_de": final["token_glosses_de"],
                "working_reading_de": CURATED_COMPLETE_READINGS.get(
                    locus, "; ".join(split_pipe(final["token_glosses_de"]))
                ),
                "syntax_note": (
                    "MANUAL_SEQUENCE_READING__TOKENWISE_BASELINE_RETAINED"
                    if locus in CURATED_COMPLETE_READINGS else "TOKEN_ORDER_BASELINE__MANUAL_SCOPE_NOT_ASSERTED"
                ),
            })
    for surface in TARGET_BY_SURFACE:
        if surface in REALITY_LOCI:
            continue
        candidates = [row for (candidate_surface, _), row in audit_by_surface_locus.items() if candidate_surface == surface]
        candidates.sort(key=lambda row: (-int(row["reader_exact"]), -int(row["known_other_tokens"]), row["locus"]))
        limit = 2 if len(candidates) >= 10 else 1
        for rank, row in enumerate(candidates[:limit], 1):
            final = final_by_locus[str(row["locus"])]
            reality_rows.append({
                "surface": surface, "selection_rank": rank, "page": row["page"], "locus": row["locus"],
                "reader_support": row["reader_support"], "zl3b_line": row["zl3b_line"],
                "tokenwise_v31_de": final["token_glosses_de"],
                "working_reading_de": "; ".join(split_pipe(final["token_glosses_de"])),
                "syntax_note": "TOKEN_ORDER_BASELINE__MANUAL_SCOPE_NOT_ASSERTED",
            })

    curated_complete_rows: list[dict[str, object]] = []
    for locus, reading in CURATED_COMPLETE_READINGS.items():
        final = final_by_locus.get(locus)
        if final is None or locus not in final_complete_by_locus:
            raise RuntimeError(f"curated GDT654 line is not V31 complete: {locus}")
        present = list(dict.fromkeys(token["eva"] for token in by_line[locus] if token["eva"] in targets))
        curated_complete_rows.append({
            "page": final["page"], "locus": locus,
            "strict_complete": final_complete_by_locus[locus]["strict_complete"],
            "target_surfaces": "|".join(present), "zl3b_line": final["zl3b_line"],
            "tokenwise_v31_de": final["token_glosses_de"], "curated_workshop_reading_de": reading,
            "syntax_note": "QUALITIES_READ_AS_ORDERED_REGISTER_SEQUENCE__NOT_SIMULTANEOUS",
            "reader_note": CURATED_READER_NOTES.get(locus, "see line-level cross-reader fields in source audit"),
        })

    write_tsv(output_dir / "PAGE_ALLOWLIST.tsv", [{"page": page} for page in sorted(pages)], ("page",))
    write_tsv(output_dir / "TARGET_DECISION_DECK.tsv", target_deck, (
        "candidate_id", "candidate_order", "surface", "mode", "v30_meaning_de", "v31_meaning_de",
        "composition", "rival_de", "occurrences", "pages", "reader_exact_occurrences",
        "split_normalized_occurrences", "reader_variant_occurrences", "decision", "decision_basis",
        "strongest_counterargument",
    ))
    write_tsv(output_dir / "FAMILY_CONTRAST_ATLAS.tsv", family_rows, (
        "family", "surface", "decomposition", "role", "v30_meaning_de", "v31_meaning_de",
        "zl3b_occurrences", "pages", "reader_exact_occurrences", "split_normalized_occurrences", "final_status",
    ))
    write_tsv(output_dir / "FULL_AR_OR_PAIR_GRID.tsv", full_grid_rows, (
        "shell", "qualifier", "ar_surface", "ar_occurrences", "ar_pages", "ar_reader_exact",
        "ar_split_normalized", "ar_status", "or_surface", "or_occurrences", "or_pages",
        "or_reader_exact", "or_split_normalized", "or_status",
    ))
    write_tsv(output_dir / "PAIR_CONTRAST_COUNTS.tsv", pair_rows, (
        "first_surface", "second_surface", "required_distinction_de", "cooccurrence_lines",
        "all_reader_exact_lines", "example_loci",
    ))
    write_tsv(output_dir / "BOUNDARY_EVIDENCE_ATLAS.tsv", boundary_rows, (
        "bridge_id", "evidence_type", "page", "locus", "diagnostic_surface",
        "zl3b_line", "it2a_line", "rf1b_line", "supports",
    ))
    write_tsv(output_dir / "REVISION_LEDGER.tsv", revision_rows, (
        "surface", "mode", "v30_meaning_de", "v31_meaning_de", "occurrences",
        "reader_exact_occurrences", "reason",
    ))
    write_tsv(output_dir / "ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv", audit_rows, (
        "audit_id", "round", "surface", "mode", "page", "locus", "section", "language", "hand",
        "token_ordinal", "line_position", "previous", "following", "zl3b_line", "it2a_line", "rf1b_line",
        "reader_support", "reader_exact", "split_normalized", "before_gloss_de", "after_gloss_de",
        "known_other_tokens", "v30_line_de", "v31_line_de", "hard_collision", "verdict",
    ))
    write_tsv(output_dir / "READER_VARIANT_AUDIT.tsv", variant_rows, (
        "surface", "page", "locus", "zl3b_line", "it2a_line", "rf1b_line", "reader_support",
        "working_meaning_de", "decision",
    ))
    write_tsv(output_dir / "ROUND_COVERAGE_COUNTS.tsv", round_rows, (
        "round", "surface", "mode", "dictionary_entries", "dictionary_sha256", "physical_lines",
        "known_token_positions", "unknown_token_positions", "complete_multi_token_lines", "strict_complete_lines",
        "one_unknown_lines", "strict_one_unknown_lines", "exact_glossary_surfaces",
    ))
    write_tsv(output_dir / "ACCEPTED_WHOLE_SURFACE_DEFAULTS.tsv", accepted_defaults, (
        "surface", "entry", "kind", "working_meaning_de", "composition", "context_rule", "status",
        "occurrences", "acceptance_mode",
    ))
    write_tsv(output_dir / "SOURCE_PASSAGE_REALITY_CHECK.tsv", reality_rows, (
        "surface", "selection_rank", "page", "locus", "reader_support", "zl3b_line",
        "tokenwise_v31_de", "working_reading_de", "syntax_note",
    ))
    write_tsv(output_dir / "CURATED_COMPLETE_PASSAGE_READINGS.tsv", curated_complete_rows, (
        "page", "locus", "strict_complete", "target_surfaces", "zl3b_line",
        "tokenwise_v31_de", "curated_workshop_reading_de", "syntax_note", "reader_note",
    ))
    write_tsv(output_dir / "AFFECTED_LINE_TRANSLATIONS.tsv", affected_rows, (
        "page", "locus", "target_surfaces", "zl3b_line", "v30_tokenwise_de", "v31_tokenwise_de", "complete_v31",
    ))
    write_tsv(output_dir / "NEWLY_COMPLETED_LINES.tsv", new_complete_rows, (
        "page", "locus", "strict_complete", "enabled_by_surfaces", "zl3b_line", "literal_v31_de",
    ))
    write_tsv(output_dir / "NEWLY_EXPOSED_ONE_HOLE_LINES.tsv", newly_exposed_rows, (
        "introduced_round", "enabled_by_surface", *ONE_FIELDS,
    ))
    write_tsv(output_dir / "V31_EXACT_TOKEN_GLOSSARY.tsv", final_gloss_rows, (
        "surface", "working_meaning_de", "source", "strength", "scope_state", "priority",
    ))
    write_tsv(output_dir / "ALL_LINE_CONCRETE_COVERAGE_V31.tsv", final_coverage, COVERAGE_FIELDS)
    write_tsv(output_dir / "COMPLETE_PASSAGES_V31.tsv", final_complete, (
        "rank", "strict_complete", *COVERAGE_FIELDS, "working_translation_de",
    ))
    write_tsv(output_dir / "ONE_UNKNOWN_PASSAGES_V31.tsv", final_one, ONE_FIELDS)
    write_tsv(output_dir / "WORKING_DICTIONARY_V31.tsv", final_dictionary, (
        "entry", "kind", "working_meaning_de", "composition", "context_rule", "status",
    ))

    output_paths = [output_dir / name for name in OUTPUT_NAMES]
    input_paths = (
        G653_RUN, G653_ALLOW, G653_COVERAGE, G653_COMPLETE, G653_ONE,
        G653_GLOSSARY, G653_DICTIONARY, G653_RESULT, G653_REPORT,
        G628_REPORT, G636_REPORT, G640_REPORT, G648_REPORT, G649_REPORT, TOKENS_REL, CROSS_REL,
    )
    verdicts = Counter(row["verdict"] for row in audit_rows)
    result_core = {
        "schema": "GDT654_AR_OR_SURFACE_CONSOLIDATION_RESULT_V1",
        "experiment_id": "GDT654", "status": STATUS,
        "guard": {"f1r": "EXCLUDED", "f84": "FORBIDDEN", "f84r": "FORBIDDEN", "new_pages": 0,
                  "new_images": 0, "allowed_pages": len(pages), "token_query": token_stats, "cross_query": cross_stats},
        "target_run": {
            "candidates": len(target_deck), "accepted_exact_wholes": len(target_deck),
            "accepted_surfaces": [row["surface"] for row in target_deck],
            "new_surfaces": [row["surface"] for row in target_deck if row["mode"].startswith("NEW")],
            "revised_surfaces": [row["surface"] for row in target_deck if row["mode"].startswith("REVISE")],
            "audited_occurrences": len(audit_rows),
            "all_reader_exact_occurrences": sum(int(row["reader_exact"]) for row in audit_rows),
            "split_normalized_occurrences": sum(int(row["split_normalized"]) for row in audit_rows),
            "reader_variant_warnings": sum(row["verdict"] == "READER_VARIANT_WARNING" for row in audit_rows),
            "hard_collisions": sum(int(row["hard_collision"]) for row in audit_rows),
            "verdicts": dict(sorted(verdicts.items())),
        },
        "semantic_axis": {
            "AR": "Drogenfraktion I", "OR": "Drogenportion", "K_AR": "heiße Drogenfraktion I",
            "K_OR": "heiße Drogenportion", "T_AR": "kalte Drogenfraktion I",
            "T_OR": "kalte Drogenportion", "QOKAR_v30": "heiße Portion",
            "QOKAR_v31": "heiße Drogenfraktion I", "QOKOR_v31": "heiße Drogenportion",
            "target_subgrid": "19 observed exact wholes; CHOR/SHOR learned-head collisions remain outside",
            "rival_retained": "QO may change the carrier class, leaving heiße Drogenportion as the QOKAR whole-word rival",
            "structural_tags_not_free_words": ["AR_FRACTION_I", "OR_PORTION", "O_PREP", "QO_SCOPE", "K_HEISS", "T_KALT", "R_ROOT", "L_WOOD"],
        },
        "full_ar_or_grid": {
            "pair_rows": len(full_grid_rows), "total_cells": len(full_grid_rows) * 2,
            "observed_cells": observed_grid_cells, "occurrences": grid_occurrences,
            "all_reader_exact_occurrences": grid_exact,
            "split_normalized_occurrences": grid_normalized,
            "accepted_v31_cells": len(target_deck),
            "learned_head_collision_holds": ["char", "chor", "shar", "shor"],
        },
        "coverage": {"base": base_metrics, "final": final_metrics,
                     "newly_completed_lines": len(new_complete_rows),
                     "newly_exposed_one_hole_lines": len(newly_exposed_rows),
                     "affected_lines": len(affected_rows)},
        "working_dictionary": {"v30_entries": len(base_dictionary), "v31_entries": len(final_dictionary),
                               "accepted_tail_entries": len(accepted_dictionary_rows),
                               "v30_prefix_sha256": canonical_hash(base_dictionary),
                               "v31_sha256": canonical_hash(final_dictionary),
                               "v30_glossary_surfaces": len(base_glossary), "v31_glossary_surfaces": len(glossary)},
        "claim_boundary": (
            "GDT654 is an exploratory working-translation consolidation, not solved plaintext. It promotes 17 new exact wholes across the transparent AR/OR, K/T, O and QO grid and visibly revises OR and QOKAR across all allowed occurrences. "
            "AR=Drogenfraktion I and OR=Drogenportion are current technical defaults; QOKAR retains heiße Drogenportion as a whole-word rival. CHOR/SHOR learned-head collisions stay outside and internal tags remain family-bound. "
            "No free component, global suffix, absent-cell meaning, phonetics, language, exact ingredient identity, f1r, new page or new image is asserted."
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
    target_run, coverage = result["target_run"], result["coverage"]
    print(
        f"GDT654 built: accepted={target_run['accepted_exact_wholes']} audits={target_run['audited_occurrences']} "
        f"known={coverage['final']['known_token_positions']} complete={coverage['final']['complete_multi_token_lines']} "
        f"strict={coverage['final']['strict_complete_lines']} one_unknown={coverage['final']['one_unknown_lines']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
