#!/usr/bin/env python3
"""Build GDT634: a concrete, complete working edition of eight micro-lines."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import itertools
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE_REL = Path("experiments/yolo/gdt634_known_core_terminal_semantics")
ART = ROOT / BASE_REL / "artifacts"
G633_BASE = Path("experiments/yolo/gdt633_cth_interfix_semantic_contrasts")
G633_RUN_REL = G633_BASE / "src/run.py"
G633_ALLOW_REL = G633_BASE / "artifacts/PAGE_ALLOWLIST.tsv"
G633_DICT_REL = G633_BASE / "artifacts/WORKING_DICTIONARY_V10.tsv"
G633_RESULT_REL = G633_BASE / "artifacts/RESULT.json"
G044_RESULT_REL = Path("gdt044_result.json")
G044_REPORT_REL = Path("GDT044_OKAM_TERMINAL_M_REPORT.md")
TOKENS_REL = Path("transcription/voynich_zl3b_tokens.tsv")
CROSS_REL = Path("transcription/voynich_cross_transcription_lines.tsv")

spec = importlib.util.spec_from_file_location("gdt633_builder", ROOT / G633_RUN_REL)
if spec is None or spec.loader is None:
    raise RuntimeError("cannot load GDT633 builder helpers")
g633 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g633)

OUTPUTS = {
    "allowlist": BASE_REL / "artifacts/PAGE_ALLOWLIST.tsv",
    "lines": BASE_REL / "artifacts/TARGET_LINES.tsv",
    "types": BASE_REL / "artifacts/TARGET_WORD_CENSUS.tsv",
    "tokens": BASE_REL / "artifacts/COMPLETE_TOKEN_WORKING_EDITION.tsv",
    "microeditions": BASE_REL / "artifacts/COMPLETE_MICROLINE_TRANSLATIONS.tsv",
    "quality_global": BASE_REL / "artifacts/QUALITY_E_LENGTH_GLOBAL_SUMMARY.tsv",
    "quality_targets": BASE_REL / "artifacts/QUALITY_TERMINAL_TARGETS.tsv",
    "o_transfer": BASE_REL / "artifacts/O_PREPARATION_TRANSFER_PARADIGMS.tsv",
    "carrier_lattice": BASE_REL / "artifacts/AL_AR_OL_OR_CARRIER_LATTICE.tsv",
    "heads": BASE_REL / "artifacts/LEXICAL_HEAD_COMPOSITION_GRID.tsv",
    "composition_checks": BASE_REL / "artifacts/AGGRESSIVE_DEFAULT_COMPOSITION_CHECKS.tsv",
    "head_profiles": BASE_REL / "artifacts/INITIAL_HEAD_POSITION_AND_BACKOFF.tsv",
    "vowel_bridges": BASE_REL / "artifacts/CARRIER_VOWEL_BODY_BRIDGES.tsv",
    "history": BASE_REL / "artifacts/HISTORICAL_STEM_ANALOGIES.tsv",
    "terminal_m": BASE_REL / "artifacts/TERMINAL_M_PROFILE.tsv",
    "reader_bridges": BASE_REL / "artifacts/CROSS_READER_READING_EVIDENCE.tsv",
    "dictionary": BASE_REL / "artifacts/WORKING_DICTIONARY_V11.tsv",
    "result": BASE_REL / "artifacts/RESULT.json",
}

TARGET_LOCI = (
    "f29r.1", "f82v.36", "f80r.18", "f80v.10",
    "f20v.10", "f22v.15", "f114v.33", "f85r1.21",
)


def D(parse: str, meaning: str, basis: str, confidence: str, rival: str) -> dict[str, str]:
    return {
        "parse": parse, "meaning": meaning, "basis": basis,
        "confidence": confidence, "rival": rival,
    }


# Every visible target type receives one content/state/quantity default.  The
# aggressive defaults stay separately labelled so each can be replaced without
# destabilising the inherited quality and quantity layers.
DEFAULTS = {
    "aiin": D("a+III", "Menge III", "INHERITED_VALUE", "MEDIUM", "Grad oder Klasse III"),
    "chedy": D("ch+e+d+y", "getrockneter Zustand", "PRODUCTIVE_QUALITY", "MEDIUM", "trocken gebundene Form"),
    "cheecthy": D("ch+ee+cth+y", "trockenes CTH-Drogenmaterial, Bindungsstufe II", "INHERITED_CTH", "MEDIUM", "im Herbal trockenes Blatt-/Krautgut"),
    "cheo": D("ch+e+o", "trocken angesetzte Zubereitung", "BOUNDARY_CTH_SHELL", "MEDIUM", "trockene o-Rahmenform"),
    "cheocthey": D("ch+e+o+cth+ey", "trockene Drogenzubereitung, Form I", "INHERITED_CTH", "MEDIUM", "trockenes CTH-Gut im o-Rahmen"),
    "cheody": D("ch+e+o+d+y", "getrockneter Ansatz", "O_STATE_TRANSFER", "LOW_MEDIUM", "trockene innere-o-Zustandsform"),
    "chep": D("ch+e+p_terminal", "trockenes Pulver", "TERMINAL_P_PULVERFORM_HYPOTHESIS", "LOW", "trockenes p-Drogengut; nicht vom initialen p abgeleitet"),
    "chety": D("ch+e+t+y", "trocken-kalte gebundene Form", "REVERSED_QUALITY_CORE", "LOW_MEDIUM", "gelerntes Ganzwort"),
    "chocthy": D("ch+o+cth+y", "trockene CTH-Drogenzubereitung", "INHERITED_CTH", "MEDIUM", "im Herbal trockene Blatt-/Krautzubereitung"),
    "chol": D("ch+ol", "trockenes Material", "INHERITED_OL", "MEDIUM", "Trockenheitsangabe ohne Nomen"),
    "chor": D("ch+or", "Pflanzenteil", "INHERITED_OR", "LOW_MEDIUM", "Reproduktionsteil; trockene r-Trägerform"),
    "chy": D("ch+y", "trocken, Grundform", "PRODUCTIVE_QUALITY", "MEDIUM", "trockene Grundstufe"),
    "ctheey": D("cth+eey", "CTH-Drogenmaterial, Form II", "INHERITED_CTH", "MEDIUM", "im Herbal Blatt-/Krautdroge, Form II"),
    "cthy": D("cth+y", "CTH-Drogenmaterial", "INHERITED_CTH", "MEDIUM", "im Herbal Blatt-/Krautgut"),
    "daiin": D("d+a+III", "Grad III", "INHERITED_VALUE", "MEDIUM", "Maß oder Klasse III"),
    "daiir": D("AIR-Oberflächenform; Zielort separat normalisiert", "am Zielort f85r1.21: Maß III", "TARGET_LOCUS_ONLY_NORMALIZATION", "MEDIUM", "die übrigen 13 daiir-Vorkommen bleiben AIR-offen"),
    "daltedy": D("d+al+t+e+d+y", "abgekühltes Material", "L_CARRIER_STATE_TRANSFER", "LOW", "kalte gebundene dal-Form"),
    "dolshedy": D("d+ol+sh+e+d+y", "eingeweichtes Material", "L_CARRIER_STATE_TRANSFER", "LOW", "befeuchtetes Material"),
    "dory": D("d+or+y", "abgemessene Portion", "R_CARRIER_STATE_TRANSFER", "LOW", "unmarkierter Teilwert"),
    "ety": D("e+t+y", "gekühlt", "LEADING_E_COLD_HYPOTHESIS", "LOW", "kalt gebundene Form; gelerntes Ganzwort"),
    "kaiin": D("k+a+III", "heiß, Grad III", "INHERITED_VALUE", "MEDIUM", "Hitze-Klasse III"),
    "lkealy": D("l+k+e+al+y", "erwärmte Flüssigkeit", "LIQUOR_HEAD_HYPOTHESIS", "LOW", "heiße l-Rahmenform"),
    "oaiin": D("o+a+III", "Ansatzmenge III", "O_VALUE_TRANSFER", "LOW_MEDIUM", "Zubereitung, Menge III"),
    "okaiin": D("o+k+a+III", "heiß, Grad III, im Ansatzrahmen", "INHERITED_VALUE", "MEDIUM", "o-Rahmen, Hitze III"),
    "ol": D("o+l", "Material", "INHERITED_OL", "LOW_MEDIUM", "Mischung; nicht ausgesprochener Eigenschaftsträger"),
    "olkam": D("ol+k+a+m", "heißes Material [terminal-M]", "OL_K_PLUS_TERMINAL_M", "LOW_MEDIUM", "OL-Kopf mit positionalem M unbekannter Funktion"),
    "olor": D("o+l+o+r", "Zutat", "DIRECT_OL_OR_COMPOUND", "LOW_MEDIUM", "Materialportion; gelerntes Ganzwort"),
    "oraiin": D("o+r+a+III", "Portion III", "DIRECT_OR_VALUE", "LOW_MEDIUM", "Nominalträger, Stufe III"),
    "otedy": D("o+t+e+d+y", "gekühlter Ansatz", "O_STATE_TRANSFER", "LOW_MEDIUM", "kalte o-Rahmen-Zustandsform"),
    "oty": D("o+t+y", "kalter Ansatz, Grundform", "O_QUALITY_TRANSFER", "LOW_MEDIUM", "kalte o-Rahmenform"),
    "paiin": D("p+a+III", "Pulver, Menge III", "PULVIS_HEAD_HYPOTHESIS", "LOW", "p-Drogengut, Stufe III"),
    "posaiin": D("posa+III; IT2a p+or+a+III", "Salzpulver-Zubereitung III", "CROSS_READER_LEARNED_POSA_FORK", "LOW", "IT2a Pulverportion III; Samenpulver III"),
    "qokaiin": D("qo+k+a+III", "heiß, Grad III", "INHERITED_VALUE", "MEDIUM", "qo-Rahmen, Hitze III"),
    "qokain": D("qo+k+a+II", "heiß, Grad II", "INHERITED_VALUE", "MEDIUM", "qo-Rahmen, Hitze II"),
    "qokal": D("qo+k+a+l", "heiße Substanz", "A_L_MATERIAL_POLARITY", "LOW_MEDIUM", "heiße L-Form"),
    "qokar": D("qo+k+a+r", "heiße Portion", "A_R_PART_POLARITY", "LOW_MEDIUM", "heißer Teil; heiße R-Form"),
    "qokchy": D("qo+k+ch+y", "heiß-trocken", "PRODUCTIVE_QUALITY", "MEDIUM", "qo-Rahmen, heiß-trocken"),
    "qokeedy": D("qo+k+ee+d+y", "heißer Zustand, Bindungsstufe II", "PRODUCTIVE_QUALITY", "MEDIUM", "heiße Grad-II-Form"),
    "qokeeedy": D("qo+k+eee+d+y", "heißer Zustand, Bindungsstufe III", "PRODUCTIVE_QUALITY", "LOW_MEDIUM", "heiße Grad-III-Form"),
    "qokeeo": D("qo+k+ee+o", "heißer Ansatz, Bindungsstufe II", "TERMINAL_O_E_LADDER", "LOW_MEDIUM", "heiße terminale o-Form"),
    "qotaiin": D("qo+t+a+III", "kalt, Grad III", "INHERITED_VALUE", "MEDIUM", "Kälte-Klasse III"),
    "qotainol": D("qotain+ol; IT2a/RF1b qotain | ol", "kaltes Material, Grad II", "TWO_READER_BOUNDARY_NORMALIZATION", "MEDIUM", "fusioniertes Ganzwort"),
    "qotchy": D("qo+t+ch+y", "kalt-trocken", "PRODUCTIVE_QUALITY", "MEDIUM", "qo-Rahmen, kalt-trocken"),
    "qoteey": D("qo+t+ee+y", "kalt, Bindungsstufe II", "PRODUCTIVE_QUALITY", "MEDIUM", "kalte Grad-II-Form"),
    "qotol": D("qo+t+ol", "kaltes Material", "INHERITED_OL", "MEDIUM", "kalte Zustandsform"),
    "qoty": D("qo+t+y", "kalt, Grundform", "PRODUCTIVE_QUALITY", "MEDIUM", "qo-Rahmen, kalt"),
    "rcheald": D("r+ch+e+al+d; IT2a/RF1b rcheold", "getrockneter Wurzelstoff", "RADIX_HEAD_PLUS_L_CARRIER", "LOW", "getrockneter Pflanzenteil"),
    "saiin": D("s+a+III", "Salz, Menge III", "SAL_HEAD_HYPOTHESIS", "LOW", "Samen, Menge III"),
    "shcthy": D("sh+cth+y", "feuchtes CTH-Drogenmaterial", "INHERITED_CTH", "MEDIUM", "im Herbal feuchtes Blatt-/Krautgut"),
    "she": D("sh+e", "feucht, attributiv gebunden", "INHERITED_E_SHELL", "MEDIUM", "Feuchtestufe I"),
    "shecthy": D("sh+e+cth+y", "feuchtes CTH-Drogenmaterial", "INHERITED_CTH", "MEDIUM", "im Herbal feuchtes Blatt-/Krautgut"),
    "sheecthey": D("sh+ee+cth+ey", "feuchtes Drogengut, Form I, Bindungsstufe II", "INHERITED_CTH", "MEDIUM", "feuchte CTH-Form mit zweifachem e"),
    "sheey": D("sh+ee+y", "feucht, Bindungsstufe II", "PRODUCTIVE_QUALITY", "MEDIUM", "Feuchtegrad II"),
    "sheol": D("sh+e+ol", "feuchtes Material", "OL_QUALITY_TRANSFER", "MEDIUM", "feucht gebundene OL-Form"),
    "shey": D("sh+e+y", "feucht, attributiv gebunden", "PRODUCTIVE_QUALITY", "MEDIUM", "Feuchteform I"),
    "sho": D("sh+o", "feuchter Ansatz", "INHERITED_PREPARATION_SHELL", "MEDIUM", "feuchte o-Rahmenform"),
    "shokaiin": D("sh+o+k+a+III", "feucht-heißer Ansatz, Grad III", "COMPOSED_PREPARATION_VALUE", "LOW_MEDIUM", "shoka-Gut, Stufe III"),
    "sol": D("s+ol", "Salzsubstanz", "SAL_HEAD_HYPOTHESIS", "LOW", "Samenmaterial"),
}

# Section- and locus-bound readings must never leak into the global surface
# dictionary.  These overrides affect only the named target occurrence.
TARGET_OVERRIDES = {
    ("f29r.1", "cheecthy"): D("ch+ee+cth+y", "trockenes Blatt-/Krautgut, Bindungsstufe II", "HERBAL_SECTION_SPECIALIZATION", "MEDIUM", "global trockenes CTH-Drogenmaterial"),
    ("f20v.10", "chocthy"): D("ch+o+cth+y", "trockene Blatt-/Krautzubereitung", "HERBAL_SECTION_SPECIALIZATION", "MEDIUM", "global trockene CTH-Drogenzubereitung"),
    ("f22v.15", "cthy"): D("cth+y", "Blatt-/Krautgut", "HERBAL_SECTION_SPECIALIZATION", "MEDIUM", "global CTH-Drogenmaterial"),
    ("f22v.15", "chocthy"): D("ch+o+cth+y", "trockene Blatt-/Krautzubereitung", "HERBAL_SECTION_SPECIALIZATION", "MEDIUM", "global trockene CTH-Drogenzubereitung"),
    ("f85r1.21", "daiir"): D("d+a+III; IT2a/RF1b daiin", "Maß III", "TWO_READER_TARGET_LOCUS_NORMALIZATION", "MEDIUM", "ZL3b AIR-Form; keine globale daiir-Normalisierung"),
}

MICROLINE_TRANSLATIONS = {
    "f29r.1": (
        "Salzpulver-Zubereitung III [IT2a: Pulverportion III] | feucht gebunden | Menge III | trockenes Pulver | kalter Ansatz | trocken | kalt-trocken | kalt | trockenes Blatt-/Krautgut, Bindungsstufe II.",
        "ZL3b/RF1b posaiin gegen IT2a poraiin: Die s/r-Lesegabel bleibt sichtbar; Samenpulver III ist der Stoffrivale.",
    ),
    "f82v.36": (
        "Salz, Menge III | feuchte Form | heißer Zustand II | heiße Portion | feuchtes Drogengut, Form I und Bindungsstufe II | heiß, Grad III | abgekühltes Material | getrockneter Wurzelstoff.",
        "s=Salz und r=Wurzel sind historische Initialhypothesen; Samen bzw. Pflanzenteil bleiben Rivalen.",
    ),
    "f80r.18": (
        "Pulver, Menge III | feuchtes Material | heiß, Grad II | trocken-kalte Form | heißer Zustand II | heiße Portion | feuchtes Drogengut | kaltes Material | feuchtes Drogengut | heiß, Grad II | heißes Material [terminal-M].",
        "Das finale m von olkam ist ein positionsgebundener Marker unbekannter Funktion und wird nicht stillschweigend gelöscht.",
    ),
    "f80v.10": (
        "Salzsubstanz | Feuchteform II | heiß, Grad III | feuchtes Drogengut | eingeweichtes Material | heiße Substanz | feuchtes Drogengut | kaltes Material, Grad II.",
        "qotainol wird nach zwei Lesern als qotain | ol gelesen.",
    ),
    "f20v.10": (
        "Feucht-heißer Ansatz, Grad III | trockene Blatt-/Krautzubereitung | trockenes Material | Grad III | trocken | Pflanzenteil | gekühlt.",
        "ety=gekühlt ist die schwächste Einzelzuweisung dieser Zeile.",
    ),
    "f22v.15": (
        "feuchter Ansatz | Blatt-/Krautgut | trockene Blatt-/Krautzubereitung | heiß-trocken | abgemessene Portion.",
        "Geschlossenste der acht Lesungen; dory bleibt ein schwacher OR-Transfer.",
    ),
    "f114v.33": (
        "heiß, Grad III | Feuchteform II | Ansatzmenge III | feuchtes Material | Kaltform II | heißer Zustand III | trocken angesetzte Zubereitung | Drogengut, Form II | heißer Ansatz, Form II | erwärmte Flüssigkeit.",
        "l=liquor/Flüssigkeit ist eine aggressive historische Initialhypothese.",
    ),
    "f85r1.21": (
        "Maß III | getrockneter Ansatz | Portion III | Material | heißer Ansatz, Grad III | trockene Drogenzubereitung, Form I | Zutat | gekühlter Ansatz | kalt, Grad III | Pflanzenteil | getrockneter Zustand.",
        "daiir wird an dieser Stelle nach IT2a und RF1b als daiin normalisiert.",
    ),
}

READER_BRIDGE_NOTES = {
    "f29r.1": "ZL3b/RF1b posaiin gegen IT2a poraiin; RF1b fusioniert chep|oty. Das erzwingt eine offene s/r-Lesegabel und stützt die trockene-Pulver|Kaltansatz-Grenze.",
    "f82v.36": "RF1b trennt s|aiin; IT2a/RF1b lesen rcheold statt rcheald. Das stützt s+Wert und einen L-Träger nach r+che.",
    "f80r.18": "ZL3b/IT2a bewahren die ganze Zeile; RF1b trennt mehrere kurze Körper. Semantik folgt den wiederkehrenden Vollformen, nicht RF1b allein.",
    "f80v.10": "IT2a und RF1b trennen qotain|ol, ZL3b fusioniert qotainol. Daher kalt Grad II + Material.",
    "f20v.10": "Alle drei Leser bewahren die sieben Tokens exakt.",
    "f22v.15": "Alle drei Leser bewahren die fünf Tokens exakt.",
    "f114v.33": "IT2a fusioniert cheo|ctheey zu cheoctheey; RF1b trennt qo|eeo. Die CTH-Zubereitung ist boundary-stabil.",
    "f85r1.21": "IT2a/RF1b lesen daiin statt ZL3b daiir; RF1b trennt cheo|y und che|y. Die konkrete Linie nutzt die Zwei-Leser-Normalisierung.",
}

MAIN_QUALITY_RE = re.compile(r"^(qo|o)?(ch|sh|k|t)(e{0,3})(d?)y$")
INNER_O_RE = re.compile(r"^(qo|o)?(ch|sh|k|t)(e{0,3})ody$")
REVERSE_QUALITY_RE = re.compile(r"^(qo|o)?(ch|sh)(e{0,3})(k|t)y$")
QUALITY_TARGETS = (
    "chy", "shey", "sheey", "qoty", "oty", "qoteey", "chedy",
    "cheody", "otedy", "qokeedy", "qokeeedy", "chety", "ety",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_hash(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: Iterable[str]) -> None:
    g633.g632.write_tsv(path, rows, fields)


def counter_text(values: Iterable[str]) -> str:
    counts = Counter(values)
    return "|".join(f"{key}:{counts[key]}" for key in sorted(counts)) or "NONE"


def stable_maps(
    token_rows: list[dict[str, str]], cross_by_locus: dict[str, dict[str, str]],
) -> tuple[dict[tuple[str, int], int], dict[tuple[str, int], int]]:
    ordinals: Counter[tuple[str, str]] = Counter()
    exact: dict[tuple[str, int], int] = {}
    boundary: dict[tuple[str, int], int] = {}
    for row in sorted(token_rows, key=g633.g632.g631.token_sort_key):
        locus, surface = row["locus"], row["eva"]
        ordinals[locus, surface] += 1
        cross = cross_by_locus[locus]
        exact_caps = [cross[field].split().count(surface) for field in ("zl3b_clean", "it2a_clean", "rf1b_clean")]
        norm_caps = [g633.g632.g631.concatenated_span_count(cross[field].split(), surface) for field in ("zl3b_clean", "it2a_clean", "rf1b_clean")]
        key = (locus, int(row["token_index"]))
        exact[key] = int(ordinals[locus, surface] <= min(exact_caps))
        boundary[key] = int(ordinals[locus, surface] <= min(norm_caps))
    return exact, boundary


def make_target_lines(
    by_line: dict[str, list[dict[str, object]]], line_text: dict[str, str],
    cross_by_locus: dict[str, dict[str, str]],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for index, locus in enumerate(TARGET_LOCI, 1):
        meta = by_line[locus][0]
        cross = cross_by_locus[locus]
        rows.append({
            "line_id": f"G634-L{index:02d}", "page": meta["page"], "locus": locus,
            "section": meta["section"], "language": meta["language"], "hand": meta["hand"],
            "zl3b_line": line_text[locus], "it2a_line": cross["it2a_clean"], "rf1b_line": cross["rf1b_clean"],
            "all_present_exact": cross["all_present_exact"], "token_count": len(by_line[locus]),
            "reader_evidence_de": READER_BRIDGE_NOTES[locus],
        })
    return rows


def make_target_editions(
    by_line: dict[str, list[dict[str, object]]], exact: dict[tuple[str, int], int],
    boundary: dict[tuple[str, int], int], counts: Counter[str], pages_by: dict[str, set[str]],
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    token_rows: list[dict[str, object]] = []
    micro_rows: list[dict[str, object]] = []
    token_id = 0
    for line_index, locus in enumerate(TARGET_LOCI, 1):
        line = by_line[locus]
        for position, source in enumerate(line, 1):
            token_id += 1
            surface = str(source["eva"])
            if surface not in DEFAULTS:
                raise RuntimeError(f"target surface lacks default: {surface}")
            default = TARGET_OVERRIDES.get((locus, surface), DEFAULTS[surface])
            key = (locus, int(source["token_index"]))
            token_rows.append({
                "edition_id": f"G634-T{token_id:03d}", "line_id": f"G634-L{line_index:02d}",
                "page": source["page"], "locus": locus, "position": position,
                "token_index": source["token_index"], "surface": surface,
                "structural_parse": default["parse"], "working_default_de": default["meaning"],
                "basis": default["basis"], "confidence": default["confidence"], "live_rival_de": default["rival"],
                "allowed_occurrences": counts[surface], "allowed_pages": len(pages_by[surface]),
                "ordinal_surface_all_readers_exact": exact[key],
                "zl_surface_split_normalized_all_readers": boundary[key],
            })
        translation, caution = MICROLINE_TRANSLATIONS[locus]
        micro_rows.append({
            "line_id": f"G634-L{line_index:02d}", "page": line[0]["page"], "locus": locus,
            "surface_line": " ".join(str(row["eva"]) for row in line), "token_count": len(line),
            "tokens_with_primary_default": len(line), "unassigned_or_banned_filler_tokens": 0,
            "working_translation_de": translation, "principal_caution_de": caution,
        })
    return token_rows, micro_rows


def make_target_census(
    token_rows: list[dict[str, str]], target_types: set[str], exact: dict[tuple[str, int], int],
    boundary: dict[tuple[str, int], int], target_edition: list[dict[str, object]],
) -> list[dict[str, object]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    target_counts = Counter(str(row["surface"]) for row in target_edition)
    target_defaults: dict[str, dict[str, object]] = {}
    for row in target_edition:
        surface = str(row["surface"])
        compact = {
            "structural_parse": row["structural_parse"], "working_default_de": row["working_default_de"],
            "basis": row["basis"], "confidence": row["confidence"],
        }
        if surface in target_defaults and target_defaults[surface] != compact:
            raise RuntimeError(f"target surface has inconsistent target defaults: {surface}")
        target_defaults[surface] = compact
    for row in token_rows:
        if row["eva"] in target_types:
            grouped[row["eva"]].append(row)
    result: list[dict[str, object]] = []
    for surface in sorted(target_types):
        rows = grouped[surface]
        default = target_defaults[surface]
        result.append({
            "surface": surface, "target_occurrences": target_counts[surface], "allowed_occurrences": len(rows),
            "pages": len({row["page"] for row in rows}), "loci": len({row["locus"] for row in rows}),
            "ordinal_surface_all_readers_exact_occurrences": sum(exact[row["locus"], int(row["token_index"])] for row in rows),
            "zl_surface_split_normalized_all_readers_occurrences": sum(boundary[row["locus"], int(row["token_index"])] for row in rows),
            "section_counts": counter_text(row["section"] for row in rows),
            "language_counts": counter_text(row["language"] for row in rows),
            "structural_parse": default["structural_parse"], "working_default_de": default["working_default_de"],
            "basis": default["basis"], "confidence": default["confidence"],
        })
    return result


def quality_parse(surface: str) -> tuple[str, str, int, str, str] | None:
    match = MAIN_QUALITY_RE.fullmatch(surface)
    if match:
        return match.group(1) or "BARE", match.group(2), len(match.group(3)), match.group(4) or "NO_D", "MAIN_DY" if match.group(4) else "MAIN_Y"
    match = INNER_O_RE.fullmatch(surface)
    if match:
        return match.group(1) or "BARE", match.group(2), len(match.group(3)), "INNER_O_D", "INNER_ODY"
    match = REVERSE_QUALITY_RE.fullmatch(surface)
    if match:
        return match.group(1) or "BARE", f"{match.group(2)}>{match.group(4)}", len(match.group(3)), "NO_D", "REVERSED_DOUBLE_CORE"
    if surface == "ety":
        return "BARE", "t", 1, "NO_D", "LEADING_E"
    return None


def line_surface_stable(locus: str, surface: str, cross_by_locus: dict[str, dict[str, str]], count_in_zl: int) -> bool:
    cross = cross_by_locus[locus]
    return all(cross[field].split().count(surface) >= count_in_zl for field in ("zl3b_clean", "it2a_clean", "rf1b_clean"))


def make_quality_tables(
    token_rows: list[dict[str, str]], by_line: dict[str, list[dict[str, object]]],
    cross_by_locus: dict[str, dict[str, str]], exact: dict[tuple[str, int], int],
) -> tuple[list[dict[str, object]], list[dict[str, object]], dict[str, object]]:
    main = [row for row in token_rows if MAIN_QUALITY_RE.fullmatch(row["eva"])]
    global_rows: list[dict[str, object]] = []
    for e_level in range(4):
        selected = [row for row in main if len(MAIN_QUALITY_RE.fullmatch(row["eva"]).group(3)) == e_level]  # type: ignore[union-attr]
        global_rows.append({
            "e_level": e_level, "occurrences": len(selected), "types": len({row["eva"] for row in selected}),
            "pages": len({row["page"] for row in selected}),
            "ordinal_surface_all_readers_exact_occurrences": sum(exact[row["locus"], int(row["token_index"])] for row in selected),
            "types_with_any_ordinal_surface_all_readers_exact": sum(
                any(exact[row["locus"], int(row["token_index"])] for row in selected if row["eva"] == surface)
                for surface in {row["eva"] for row in selected}
            ),
            "working_slot_de": "Grundform" if e_level == 0 else f"Bindungsstufe {e_level}",
        })

    by_surface = Counter(row["eva"] for row in token_rows)
    pages_by: dict[str, set[str]] = defaultdict(set)
    loci_by: dict[str, set[str]] = defaultdict(set)
    stable_by = Counter()
    for row in token_rows:
        pages_by[row["eva"]].add(row["page"])
        loci_by[row["eva"]].add(row["locus"])
        stable_by[row["eva"]] += exact[row["locus"], int(row["token_index"])]

    target_rows: list[dict[str, object]] = []
    total_ladder_loci: set[tuple[str, str, str, str]] = set()
    total_stable_ladder_loci: set[tuple[str, str, str, str]] = set()
    for surface in QUALITY_TARGETS:
        parsed = quality_parse(surface)
        assert parsed is not None
        wrapper, core, e_level, d_slot, family = parsed
        ladder_loci: set[str] = set()
        stable_loci: set[str] = set()
        if family in {"MAIN_Y", "MAIN_DY", "INNER_ODY", "REVERSED_DOUBLE_CORE"}:
            for locus, line in by_line.items():
                surfaces = [str(row["eva"]) for row in line]
                if surface not in surfaces:
                    continue
                family_members = []
                for candidate in set(surfaces):
                    cp = quality_parse(candidate)
                    if cp and (cp[0], cp[1], cp[3], cp[4]) == (wrapper, core, d_slot, family):
                        family_members.append(candidate)
                if len({quality_parse(candidate)[2] for candidate in family_members}) < 2:  # type: ignore[index]
                    continue
                ladder_loci.add(locus)
                if all(line_surface_stable(locus, candidate, cross_by_locus, surfaces.count(candidate)) for candidate in family_members):
                    stable_loci.add(locus)
                total_ladder_loci.add((locus, wrapper, core, f"{d_slot}:{family}"))
                if locus in stable_loci:
                    total_stable_ladder_loci.add((locus, wrapper, core, f"{d_slot}:{family}"))
        target_rows.append({
            "surface": surface, "family": family, "wrapper": wrapper, "quality_core": core,
            "e_level": e_level, "d_or_inner_o_slot": d_slot, "structural_parse": DEFAULTS[surface]["parse"],
            "occurrences": by_surface[surface], "pages": len(pages_by[surface]), "loci": len(loci_by[surface]),
            "ordinal_surface_all_readers_exact_occurrences": stable_by[surface], "zl_same_line_e_ladder_loci": len(ladder_loci),
            "all_member_ordinal_surface_all_readers_exact_ladder_loci": len(stable_loci),
            "working_default_de": DEFAULTS[surface]["meaning"], "confidence": DEFAULTS[surface]["confidence"],
        })
    diagnostics = {
        "main_occurrences": len(main), "main_types": len({row["eva"] for row in main}),
        "main_pages": len({row["page"] for row in main}),
        "main_ordinal_surface_all_readers_exact": sum(exact[row["locus"], int(row["token_index"])] for row in main),
        "target_zl_ladder_loci_union": len(total_ladder_loci),
        "target_all_member_ordinal_surface_all_readers_exact_ladder_loci_union": len(total_stable_ladder_loci),
    }
    return global_rows, target_rows, diagnostics


def form_summary(
    form: str, token_rows: list[dict[str, str]], exact: dict[tuple[str, int], int],
) -> tuple[int, int, int]:
    selected = [row for row in token_rows if row["eva"] == form]
    return len(selected), len({row["page"] for row in selected}), sum(exact[row["locus"], int(row["token_index"])] for row in selected)


def make_o_transfer(
    token_rows: list[dict[str, str]], by_line: dict[str, list[dict[str, object]]],
    exact: dict[tuple[str, int], int],
) -> list[dict[str, object]]:
    paradigms = (
        ("OA_VALUE", ("oain", "oaiin"), "o + Wert II/III", "Ansatz/Zubereitung mit Wert"),
        ("SHOKA_VALUE", ("shokain", "shokaiin"), "sh+o+k+a+Wert", "feucht-heißer Ansatz mit Grad"),
        ("QOK_TERMINAL_O_E", ("qokeo", "qokeeo"), "qo+k+e/ee+o", "heißer Ansatz, Bindungsstufe I/II"),
        ("CH_INNER_ODY_E", ("chody", "cheody", "cheeody"), "ch+e0/e1/e2+ody", "trockene innere-o-Zustandsform"),
        ("OT_DY_E", ("otdy", "otedy", "oteedy", "oteeedy"), "o+t+e0/e1/e2/e3+dy", "kalte o-Zustandsform"),
        ("COLD_Y_WRAPPERS", ("ty", "oty", "qoty"), "BARE/o/qo+t+y", "kalte Grundform unter drei Rahmen"),
        ("COLD_EE_Y_WRAPPERS", ("teey", "oteey", "qoteey"), "BARE/o/qo+t+ee+y", "kalte Bindungsstufe II unter drei Rahmen"),
        ("COLD_E_DY_WRAPPERS", ("tedy", "otedy", "qotedy"), "BARE/o/qo+t+e+dy", "kalter Zustand unter drei Rahmen"),
        ("HOT_EE_DY_WRAPPERS", ("keedy", "okeedy", "qokeedy"), "BARE/o/qo+k+ee+dy", "heißer Zustand II unter drei Rahmen"),
    )
    line_sets = {locus: {str(row["eva"]) for row in line} for locus, line in by_line.items()}
    rows: list[dict[str, object]] = []
    for paradigm_id, forms, parse, meaning in paradigms:
        summaries = {form: form_summary(form, token_rows, exact) for form in forms}
        edges = []
        for left, right in itertools.combinations(forms, 2):
            n = sum(left in surfaces and right in surfaces for surfaces in line_sets.values())
            if n:
                edges.append(f"{left}~{right}:{n}")
        rows.append({
            "paradigm_id": paradigm_id, "forms": "|".join(forms),
            "occurrences_by_form": "|".join(f"{form}:{summaries[form][0]}" for form in forms),
            "pages_by_form": "|".join(f"{form}:{summaries[form][1]}" for form in forms),
            "ordinal_surface_all_readers_exact_by_form": "|".join(f"{form}:{summaries[form][2]}" for form in forms),
            "zl_same_line_cooccurrences": "|".join(edges) or "NONE", "structural_parse": parse,
            "working_transfer_de": meaning,
            "boundary_de": "o=Zubereitung bleibt ein konstruktionsgebundener Arbeitswert; nicht Wasser, Wein oder Öl",
        })
    return rows


def make_carrier_lattice(
    token_rows: list[dict[str, str]], by_line: dict[str, list[dict[str, object]]],
    exact: dict[tuple[str, int], int],
) -> list[dict[str, object]]:
    prefixes = ("", "k", "t", "ch", "sh", "ok", "ot", "qok", "qot", "p", "s", "r", "l", "d")
    endings = ("al", "ar", "ol", "or")
    line_sets = {locus: {str(row["eva"]) for row in line} for locus, line in by_line.items()}
    rows: list[dict[str, object]] = []
    for prefix in prefixes:
        forms = {ending: prefix + ending for ending in endings}
        summaries = {ending: form_summary(form, token_rows, exact) for ending, form in forms.items()}
        pairs = []
        for left, right in itertools.combinations(endings, 2):
            n = sum(forms[left] in surfaces and forms[right] in surfaces for surfaces in line_sets.values())
            if n:
                pairs.append(f"{left}~{right}:{n}")
        rows.append({
            "prefix": prefix or "BARE", "occupied_cells": sum(summaries[e][0] > 0 for e in endings),
            **{f"{ending}_surface": forms[ending] for ending in endings},
            **{f"{ending}_occurrences": summaries[ending][0] for ending in endings},
            **{f"{ending}_pages": summaries[ending][1] for ending in endings},
            **{f"{ending}_ordinal_surface_all_readers_exact": summaries[ending][2] for ending in endings},
            "zl_same_line_pairs": "|".join(pairs) or "NONE",
            "working_polarity_de": "L=Substanz/Material; R=Teil/Portion; a/o bleiben verschiedene Trägervokale",
        })
    return rows


def make_head_grid(token_rows: list[dict[str, str]], exact: dict[tuple[str, int], int]) -> list[dict[str, object]]:
    hypotheses = {
        "p": ("pulvis", "Pulver", "p-Drogengut"),
        "s": ("sal", "Salz", "semen/Samen"),
        "r": ("radix", "Wurzelstoff", "Pflanzenteil"),
        "l": ("liquor", "Flüssigkeit", "l-Rahmen"),
    }
    tails = ("an", "ain", "aiin", "aiiin", "al", "ar", "ol", "or", "olain", "olaiin", "orain", "oraiin")
    rows: list[dict[str, object]] = []
    for head, (latin, meaning, rival) in hypotheses.items():
        forms = [head + tail for tail in tails]
        summaries = {form: form_summary(form, token_rows, exact) for form in forms}
        rows.append({
            "head": head, "historical_stem": latin, "primary_default_de": meaning, "live_rival_de": rival,
            "value_forms": "|".join(f"{form}:{summaries[form][0]}" for form in forms[:4]),
            "carrier_forms": "|".join(f"{form}:{summaries[form][0]}" for form in forms[4:8]),
            "carrier_value_forms": "|".join(f"{form}:{summaries[form][0]}" for form in forms[8:]),
            "total_selected_occurrences": sum(summary[0] for summary in summaries.values()),
            "ordinal_surface_all_readers_exact_selected_occurrences": sum(summary[2] for summary in summaries.values()),
            "status": "EXPLORATORY_PRIMARY_STEM__REPLACE_IF_COMPOSITION_FAILS",
        })
    return rows


def make_composition_checks(
    token_rows: list[dict[str, str]], by_line: dict[str, list[dict[str, object]]],
    exact: dict[tuple[str, int], int],
) -> list[dict[str, object]]:
    checks = (
        ("P_DRY_MOIST", ("chep", "shep", "chepy", "shepy"), "terminales p trägt ch/sh-Qualität", "separate terminal-p-Pulverform besitzt trockene und feuchte Formen; kein Beleg für initiales p"),
        ("DAL_THERMAL", ("dalkedy", "daltedy"), "dal trägt k/t", "daltedy ist eine kalte, nicht isolierte dal-Form"),
        ("DAL_MOISTURE", ("dalchedy", "dalshedy"), "dal trägt ch/sh", "dal besitzt trockene und feuchte Zustände"),
        ("DOL_MOISTURE", ("dolchedy", "dolshedy"), "dol trägt ch/sh", "dolshedy=befeuchtet hat einen trockenen Gegenkörper"),
        ("TERMINAL_O_THERMAL", ("qokeeo", "qoteeo"), "terminales o unter k/t", "qokeeo=heißer Ansatz hat eine kalte Gegenform"),
        ("OLK_M_THERMAL", ("olkam", "oltam"), "OL-M-Schluss unter k/t", "olkam=heißes Material [terminal-M] hat eine seltene kalte Gegenform"),
        ("R_ROOT_DRY_MOIST", ("rcheald", "rsheald"), "initiales r unter ch/sh", "nur die trockene Wurzelhypothese ist belegt"),
        ("L_LIQUID_HOT_COLD", ("lkealy", "ltealy"), "initiales l unter k/t", "nur die heiße Flüssigkeitshypothese ist belegt"),
        ("P_CARRIER_VALUE", ("pol", "por", "paiin", "polaiin", "poraiin"), "p mit L/R und Wert", "Pulver besitzt Material-, Portions- und Wertformen"),
        ("S_CARRIER_VALUE", ("sol", "sor", "saiin", "solaiin", "soraiin"), "s mit L/R und Wert", "Salz besitzt Material-, Portions- und Wertformen"),
    )
    line_sets = {locus: {str(row["eva"]) for row in line} for locus, line in by_line.items()}
    rows: list[dict[str, object]] = []
    for check_id, forms, rule, diagnosis in checks:
        summaries = {form: form_summary(form, token_rows, exact) for form in forms}
        edges = []
        for left, right in itertools.combinations(forms, 2):
            n = sum(left in surfaces and right in surfaces for surfaces in line_sets.values())
            if n:
                edges.append(f"{left}~{right}:{n}")
        rows.append({
            "check_id": check_id, "forms": "|".join(forms),
            "occurrences_by_form": "|".join(f"{form}:{summaries[form][0]}" for form in forms),
            "pages_by_form": "|".join(f"{form}:{summaries[form][1]}" for form in forms),
            "ordinal_surface_all_readers_exact_by_form": "|".join(f"{form}:{summaries[form][2]}" for form in forms),
            "zl_same_line_cooccurrences": "|".join(edges) or "NONE", "composition_rule_de": rule,
            "working_diagnosis_de": diagnosis,
            "status": "MULTIPLE_LISTED_FORMS_ATTESTED" if sum(summaries[form][0] > 0 for form in forms) >= 2 else "ONE_SIDED_ONLY",
        })
    return rows


def make_initial_head_profiles(
    token_rows: list[dict[str, str]], by_line: dict[str, list[dict[str, object]]],
) -> list[dict[str, object]]:
    counts = Counter(row["eva"] for row in token_rows)
    positions: dict[tuple[str, int], str] = {}
    for locus, line in by_line.items():
        for index, row in enumerate(line):
            positions[locus, int(row["token_index"])] = "FIRST" if index == 0 else "LAST" if index + 1 == len(line) else "MIDDLE"
    meanings = {"p": "pulvis/Pulver", "s": "sal/Salz", "r": "radix/Wurzel", "l": "liquor/flüssige Form"}
    rows: list[dict[str, object]] = []
    for head in ("p", "s", "r", "l"):
        selected = [
            row for row in token_rows
            if row["eva"].startswith(head)
            and len(row["eva"]) > 1
            and not (head == "s" and row["eva"].startswith("sh"))
        ]
        position_counts = Counter(positions[row["locus"], int(row["token_index"])] for row in selected)
        backed = [row for row in selected if counts[row["eva"][1:]] > 0]
        types = {row["eva"] for row in selected}
        rows.append({
            "head": head, "working_default_de": meanings[head], "prefixed_occurrences": len(selected),
            "prefixed_types": len(types), "delete_head_counterpart_occurrences": len(backed),
            "delete_head_counterpart_types": sum(counts[surface[1:]] > 0 for surface in types),
            "first_occurrences": position_counts["FIRST"], "middle_occurrences": position_counts["MIDDLE"],
            "last_occurrences": position_counts["LAST"], "standalone_occurrences": counts[head],
            "working_diagnosis_de": "produktive Produkthülle" if head == "p" else "innerer Stoff-/Teilmodifikator" if head in {"r", "l"} else "häufiger Stoffkopf mit eigenem Trägergitter",
        })
    return rows


def make_vowel_bridges(token_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    counts = Counter(row["eva"] for row in token_rows)
    rows: list[dict[str, object]] = []
    for terminal, meaning in (("l", "Substanz/Material"), ("r", "Teil/Portion")):
        a_types = {surface for surface in counts if surface.endswith("a" + terminal)}
        o_types = {surface for surface in counts if surface.endswith("o" + terminal)}
        a_bodies = {surface[:-2] for surface in a_types}
        o_bodies = {surface[:-2] for surface in o_types}
        shared = sorted(a_bodies & o_bodies)
        rows.append({
            "terminal": terminal.upper(), "working_polarity_de": meaning,
            "a_carrier_types": len(a_types), "o_carrier_types": len(o_types), "shared_bodies": len(shared),
            "shared_a_occurrences": sum(counts[body + "a" + terminal] for body in shared),
            "shared_o_occurrences": sum(counts[body + "o" + terminal] for body in shared),
            "example_pairs": "|".join(
                f"{body + 'a' + terminal}~{body + 'o' + terminal}" for body in shared
                if body in {"", "ch", "sh", "s", "qok", "qot", "che", "she"}
            ),
            "working_diagnosis_de": "a und o realisieren parallele Trägerformen; sie werden nicht als derselbe Buchstabe behandelt",
        })
    return rows


def make_historical_rows() -> list[dict[str, object]]:
    return [
        {
            "comparator_id": "PAL_LAT_1234", "date_place": "Deutschland, um 1400",
            "source": "BAV Pal.lat.1234", "url": "https://doi.org/10.11588/diglit.11353",
            "relevant_architecture": "Gradus medicinarum simplicium; Tabellen einfacher/zusammengesetzter Arzneien; Dosis; Öle; Materia medica",
            "use_here": "stützt Qualitätsgrad+Dosis+Stoffteil-Architektur, keine Voynich-Buchstabenwerte",
        },
        {
            "comparator_id": "WELLCOME_MS_105", "date_place": "Deutschland, vor 1435",
            "source": "Wellcome MS.105", "url": "https://wellcomecollection.org/works/abzgsvax",
            "relevant_architecture": "pharmakologische Traktate über einfache/zusammengesetzte Pflanzen- und Tierdrogen",
            "use_here": "zeitnaher Mischbuch-Komparator, keine Oberflächenentsprechung",
        },
        {
            "comparator_id": "WELLCOME_MS_624", "date_place": "Deutschland, 1440er–1450er",
            "source": "Wellcome MS.624, Circa instans", "url": "https://wellcomecollection.org/works/y78kt23d",
            "relevant_architecture": "alphabetisch geordnete einfache Arzneistoffe und ihre Eigenschaften",
            "use_here": "leicht späterer Fachwort-/Eigenschaftskomparator",
        },
        {
            "comparator_id": "LATIN_STEM_SET", "date_place": "mittelalterliches pharmazeutisches Latein",
            "source": "pulvis; sal/semen; radix; liquor", "url": "NONE",
            "relevant_architecture": "Pulver; Salz/Samen; Wurzel; Flüssigkeit als Arzneikategorien",
            "use_here": "liefert aggressive Initialdefaults p/s/r/l; keine Behauptung identischer historischer Siglen",
        },
        {
            "comparator_id": "CAMBRIDGE_CASEBOOK_CONTINUITY", "date_place": "frühneuzeitliche Rezeptpraxis; nicht um 1420",
            "source": "Cambridge Casebooks treatment glossary", "url": "https://casebooks.lib.cam.ac.uk/using-the-casebooks/glossary-of-treatments",
            "relevant_architecture": "p wird tatsächlich als pulvis/Pulver erläutert",
            "use_here": "nur Kontinuitätsanalogie für p=pulvis, kein zeitgleicher Schlüssel",
        },
    ]


def make_terminal_m(
    token_rows: list[dict[str, str]], by_line: dict[str, list[dict[str, object]]],
    exact: dict[tuple[str, int], int],
) -> list[dict[str, object]]:
    positions: dict[tuple[str, int], bool] = {}
    for locus, line in by_line.items():
        for index, row in enumerate(line):
            positions[locus, int(row["token_index"])] = index + 1 == len(line)
    selected = ("kam", "okam", "qokam", "olkam")
    rows: list[dict[str, object]] = []
    populations = [("ALL_TERMINAL_M", lambda surface: surface.endswith("m")), ("ALL_AM", lambda surface: surface.endswith("am"))]
    populations.extend((form, lambda surface, form=form: surface == form) for form in selected)
    for label, predicate in populations:
        hits = [row for row in token_rows if predicate(row["eva"])]
        final = sum(positions[row["locus"], int(row["token_index"])] for row in hits)
        rows.append({
            "population": label, "occurrences": len(hits), "pages": len({row["page"] for row in hits}),
            "line_final_occurrences": final, "line_final_share": f"{final / len(hits):.6f}" if hits else "0.000000",
            "ordinal_surface_all_readers_exact_occurrences": sum(exact[row["locus"], int(row["token_index"])] for row in hits),
            "working_default_de": "positionsgebundener terminal-M-Marker; Funktion und Lautwert unbekannt",
        })
    return rows


def make_reader_bridges(lines: list[dict[str, object]]) -> list[dict[str, object]]:
    return [{
        "bridge_id": f"G634-B{index:02d}", "page": row["page"], "locus": row["locus"],
        "zl3b_line": row["zl3b_line"], "it2a_line": row["it2a_line"], "rf1b_line": row["rf1b_line"],
        "semantic_consequence_de": row["reader_evidence_de"],
    } for index, row in enumerate(lines, 1)]


def make_dictionary(old: list[dict[str, str]]) -> tuple[list[dict[str, object]], int, int]:
    # V10 is preserved row-for-row.  GDT634 adds new target surfaces and atoms
    # instead of destroying inherited context restrictions or provenance.
    rows: list[dict[str, object]] = [dict(source) for source in old]
    revised = 0
    old_entries = {row["entry"] for row in old}
    atom_additions = (
        ("p- (initial)", "PULVIS_HEAD_HYPOTHESIS", "Pulver", "p+Träger/Wert", "historische Initialhypothese; p-Drogengut bleibt Rivale"),
        ("-p (terminal)", "TERMINAL_P_PULVERFORM_HYPOTHESIS", "Pulverform", "Qualität+p", "separate LOW-Hypothese; nicht aus initialem p abgeleitet"),
        ("s- (initial)", "SAL_HEAD_HYPOTHESIS", "Salz", "s+Träger/Wert", "Samen/Saatgut bleibt direkter Rivale"),
        ("r- (initial)", "RADIX_HEAD_HYPOTHESIS", "Wurzelstoff", "r+Qualität/Träger", "nur als aggressiver Anfangskopf"),
        ("l- (initial)", "LIQUOR_HEAD_HYPOTHESIS", "Flüssigkeit", "l+Qualität/Träger", "l-Rahmen bleibt Rivale"),
        ("a+l / o+l", "L_MATERIAL_POLARITY", "Substanz-/Materialträger", "Trägervokal+L", "a und o nicht gleichgesetzt"),
        ("a+r / o+r", "R_PART_POLARITY", "Teil-/Portionsträger", "Trägervokal+R", "a und o nicht gleichgesetzt"),
    )
    for entry, kind, meaning, composition, rule in atom_additions:
        rows.append({
            "entry": entry, "kind": kind, "working_meaning_de": meaning,
            "composition": composition, "context_rule": rule, "status": "NEW_V11_EXPLORATORY_ATOM",
        })
    additions = len(atom_additions)
    for surface in sorted(DEFAULTS):
        if surface in old_entries:
            continue
        default = DEFAULTS[surface]
        entry = "daiir@f85r1.21" if surface == "daiir" else surface
        rows.append({
            "entry": entry, "kind": "TARGET_LOCUS_DEFAULT" if surface == "daiir" else "TARGET_SURFACE_DEFAULT",
            "working_meaning_de": "Maß III" if surface == "daiir" else default["meaning"],
            "composition": "d+a+III; IT2a/RF1b daiin" if surface == "daiir" else default["parse"],
            "context_rule": (
                "nur f85r1.21; andere daiir-Vorkommen bleiben offen"
                if surface == "daiir" else f"{default['basis']}; Rivale: {default['rival']}"
            ),
            "status": "NEW_V11_TARGET_LOCUS_DEFAULT" if surface == "daiir" else "NEW_V11_TARGET_DEFAULT",
        })
        additions += 1
    return rows, revised, additions


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    pages = {row["page"] for row in read_tsv(ROOT / G633_ALLOW_REL)}
    if "f1r" in pages or any(page.startswith("f84") for page in pages):
        raise RuntimeError("allow-list contains excluded or forbidden page")
    token_rows, token_stats = g633.g632.g631.guarded_query(
        TOKENS_REL, pages, "page,locus,token_index,eva,section,language,hand",
    )
    cross_rows, cross_stats = g633.g632.g631.guarded_query(
        CROSS_REL, pages, "page,locus,all_three_present,all_present_exact,zl3b_clean,it2a_clean,rf1b_clean",
    )
    cross_by_locus = {row["locus"]: row for row in cross_rows}
    by_line, line_text = g633.g632.g631.line_maps([dict(row) for row in token_rows])
    if any(locus not in by_line or locus not in cross_by_locus for locus in TARGET_LOCI):
        raise RuntimeError("target locus missing from guarded source")
    exact, boundary = stable_maps(token_rows, cross_by_locus)
    counts = Counter(row["eva"] for row in token_rows)
    pages_by: dict[str, set[str]] = defaultdict(set)
    for row in token_rows:
        pages_by[row["eva"]].add(row["page"])

    lines = make_target_lines(by_line, line_text, cross_by_locus)
    target_tokens, microeditions = make_target_editions(by_line, exact, boundary, counts, pages_by)
    target_types = {str(row["surface"]) for row in target_tokens}
    census = make_target_census(token_rows, target_types, exact, boundary, target_tokens)
    quality_global, quality_targets, quality_diag = make_quality_tables(token_rows, by_line, cross_by_locus, exact)
    o_transfer = make_o_transfer(token_rows, by_line, exact)
    carrier_lattice = make_carrier_lattice(token_rows, by_line, exact)
    heads = make_head_grid(token_rows, exact)
    composition_checks = make_composition_checks(token_rows, by_line, exact)
    head_profiles = make_initial_head_profiles(token_rows, by_line)
    vowel_bridges = make_vowel_bridges(token_rows)
    history = make_historical_rows()
    terminal_m = make_terminal_m(token_rows, by_line, exact)
    reader_bridges = make_reader_bridges(lines)
    dictionary, revised_dictionary, added_dictionary = make_dictionary(read_tsv(ROOT / G633_DICT_REL))

    write_tsv(ROOT / OUTPUTS["allowlist"], [{"page": page} for page in sorted(pages)], ("page",))
    write_tsv(ROOT / OUTPUTS["lines"], lines, (
        "line_id", "page", "locus", "section", "language", "hand", "zl3b_line", "it2a_line", "rf1b_line",
        "all_present_exact", "token_count", "reader_evidence_de",
    ))
    write_tsv(ROOT / OUTPUTS["types"], census, (
        "surface", "target_occurrences", "allowed_occurrences", "pages", "loci", "ordinal_surface_all_readers_exact_occurrences",
        "zl_surface_split_normalized_all_readers_occurrences", "section_counts", "language_counts", "structural_parse", "working_default_de", "basis", "confidence",
    ))
    write_tsv(ROOT / OUTPUTS["tokens"], target_tokens, (
        "edition_id", "line_id", "page", "locus", "position", "token_index", "surface", "structural_parse",
        "working_default_de", "basis", "confidence", "live_rival_de", "allowed_occurrences", "allowed_pages",
        "ordinal_surface_all_readers_exact", "zl_surface_split_normalized_all_readers",
    ))
    write_tsv(ROOT / OUTPUTS["microeditions"], microeditions, (
        "line_id", "page", "locus", "surface_line", "token_count", "tokens_with_primary_default",
        "unassigned_or_banned_filler_tokens", "working_translation_de", "principal_caution_de",
    ))
    write_tsv(ROOT / OUTPUTS["quality_global"], quality_global, (
        "e_level", "occurrences", "types", "pages", "ordinal_surface_all_readers_exact_occurrences",
        "types_with_any_ordinal_surface_all_readers_exact", "working_slot_de",
    ))
    write_tsv(ROOT / OUTPUTS["quality_targets"], quality_targets, (
        "surface", "family", "wrapper", "quality_core", "e_level", "d_or_inner_o_slot", "structural_parse",
        "occurrences", "pages", "loci", "ordinal_surface_all_readers_exact_occurrences", "zl_same_line_e_ladder_loci",
        "all_member_ordinal_surface_all_readers_exact_ladder_loci", "working_default_de", "confidence",
    ))
    write_tsv(ROOT / OUTPUTS["o_transfer"], o_transfer, (
        "paradigm_id", "forms", "occurrences_by_form", "pages_by_form", "ordinal_surface_all_readers_exact_by_form",
        "zl_same_line_cooccurrences",
        "structural_parse", "working_transfer_de", "boundary_de",
    ))
    write_tsv(ROOT / OUTPUTS["carrier_lattice"], carrier_lattice, (
        "prefix", "occupied_cells", "al_surface", "ar_surface", "ol_surface", "or_surface",
        "al_occurrences", "ar_occurrences", "ol_occurrences", "or_occurrences",
        "al_pages", "ar_pages", "ol_pages", "or_pages",
        "al_ordinal_surface_all_readers_exact", "ar_ordinal_surface_all_readers_exact",
        "ol_ordinal_surface_all_readers_exact", "or_ordinal_surface_all_readers_exact",
        "zl_same_line_pairs", "working_polarity_de",
    ))
    write_tsv(ROOT / OUTPUTS["heads"], heads, (
        "head", "historical_stem", "primary_default_de", "live_rival_de", "value_forms", "carrier_forms",
        "carrier_value_forms", "total_selected_occurrences", "ordinal_surface_all_readers_exact_selected_occurrences", "status",
    ))
    write_tsv(ROOT / OUTPUTS["composition_checks"], composition_checks, (
        "check_id", "forms", "occurrences_by_form", "pages_by_form", "ordinal_surface_all_readers_exact_by_form",
        "zl_same_line_cooccurrences",
        "composition_rule_de", "working_diagnosis_de", "status",
    ))
    write_tsv(ROOT / OUTPUTS["head_profiles"], head_profiles, (
        "head", "working_default_de", "prefixed_occurrences", "prefixed_types", "delete_head_counterpart_occurrences",
        "delete_head_counterpart_types", "first_occurrences", "middle_occurrences", "last_occurrences",
        "standalone_occurrences", "working_diagnosis_de",
    ))
    write_tsv(ROOT / OUTPUTS["vowel_bridges"], vowel_bridges, (
        "terminal", "working_polarity_de", "a_carrier_types", "o_carrier_types", "shared_bodies",
        "shared_a_occurrences", "shared_o_occurrences", "example_pairs", "working_diagnosis_de",
    ))
    write_tsv(ROOT / OUTPUTS["history"], history, (
        "comparator_id", "date_place", "source", "url", "relevant_architecture", "use_here",
    ))
    write_tsv(ROOT / OUTPUTS["terminal_m"], terminal_m, (
        "population", "occurrences", "pages", "line_final_occurrences", "line_final_share",
        "ordinal_surface_all_readers_exact_occurrences", "working_default_de",
    ))
    write_tsv(ROOT / OUTPUTS["reader_bridges"], reader_bridges, (
        "bridge_id", "page", "locus", "zl3b_line", "it2a_line", "rf1b_line", "semantic_consequence_de",
    ))
    write_tsv(ROOT / OUTPUTS["dictionary"], dictionary, (
        "entry", "kind", "working_meaning_de", "composition", "context_rule", "status",
    ))

    basis_counts = Counter(str(row["basis"]) for row in target_tokens)
    carrier_by_prefix = {str(row["prefix"]): row for row in carrier_lattice}
    m_by_population = {str(row["population"]): row for row in terminal_m}
    output_hashes = {str(path): sha256(ROOT / path) for key, path in OUTPUTS.items() if key != "result"}
    input_paths = (TOKENS_REL, CROSS_REL, G633_ALLOW_REL, G633_DICT_REL, G633_RESULT_REL, G633_RUN_REL, G044_RESULT_REL, G044_REPORT_REL)
    result_core = {
        "schema": "GDT634_KNOWN_CORE_TERMINAL_SEMANTICS_RESULT_V1", "experiment_id": "GDT634",
        "status": "COMPLETE_8_LINE_CONCRETE_WORKING_EDITION__69_OF_69_TOKENS_DEFAULTED",
        "guard": {
            "f1r": "EXCLUDED", "f84": "FORBIDDEN", "f84r": "FORBIDDEN", "new_image_pages": 0,
            "allowed_pages": len(pages), "token_query": token_stats, "cross_query": cross_stats,
        },
        "edition": {
            "lines": len(lines), "tokens": len(target_tokens), "types": len(target_types),
            "tokens_with_primary_default": sum(bool(row["working_default_de"]) for row in target_tokens),
            "unassigned_or_banned_filler_tokens": 0,
            "ordinal_surface_all_readers_exact_target_tokens": sum(int(row["ordinal_surface_all_readers_exact"]) for row in target_tokens),
            "zl_surface_split_normalized_all_readers_target_tokens": sum(int(row["zl_surface_split_normalized_all_readers"]) for row in target_tokens),
            "basis_counts": dict(sorted(basis_counts.items())),
        },
        "quality_terminal": quality_diag | {
            "e_level_counts": {str(row["e_level"]): int(row["occurrences"]) for row in quality_global},
            "target_types": len(quality_targets),
        },
        "concrete_transfers": {
            "p_initial": "pulvis/Pulver", "p_terminal": "separate Pulverform-Hypothese",
            "s_initial": "sal/Salz; Samen rival", "posaiin": "gelerntes posa-Ganzwort; IT2a pora-Gabel",
            "r_initial": "radix/Wurzel", "l_initial": "liquor/Flüssigkeit",
            "l_terminal": "Substanz/Material", "r_terminal": "Teil/Portion", "o": "konstruktionsgebundener Ansatz/Zubereitung",
            "m": "positionsgebundener terminal-M-Marker; Wert unbekannt", "daiir_target": "two-reader daiin normalization: Maß III",
        },
        "aggressive_composition_checks": {
            "rows": len(composition_checks),
            "multiple_listed_forms_attested_rows": sum(row["status"] == "MULTIPLE_LISTED_FORMS_ATTESTED" for row in composition_checks),
            "one_sided_rows": sum(row["status"] == "ONE_SIDED_ONLY" for row in composition_checks),
        },
        "head_backoff": {
            str(row["head"]): {
                "prefixed_occurrences": int(row["prefixed_occurrences"]),
                "delete_head_counterpart_occurrences": int(row["delete_head_counterpart_occurrences"]),
                "first_occurrences": int(row["first_occurrences"]),
            } for row in head_profiles
        },
        "carrier_vowel_bridges": {
            str(row["terminal"]): {
                "shared_bodies": int(row["shared_bodies"]),
                "shared_a_occurrences": int(row["shared_a_occurrences"]),
                "shared_o_occurrences": int(row["shared_o_occurrences"]),
            } for row in vowel_bridges
        },
        "carrier_checks": {
            "qok": {ending: int(carrier_by_prefix["qok"][f"{ending}_occurrences"]) for ending in ("al", "ar", "ol", "or")},
            "qok_zl_same_line_pairs": carrier_by_prefix["qok"]["zl_same_line_pairs"],
            "bare": {ending: int(carrier_by_prefix["BARE"][f"{ending}_occurrences"]) for ending in ("al", "ar", "ol", "or")},
        },
        "terminal_m": {
            "all_occurrences": int(m_by_population["ALL_TERMINAL_M"]["occurrences"]),
            "all_line_final": int(m_by_population["ALL_TERMINAL_M"]["line_final_occurrences"]),
            "olkam_occurrences": int(m_by_population["olkam"]["occurrences"]),
            "olkam_line_final": int(m_by_population["olkam"]["line_final_occurrences"]),
        },
        "working_dictionary": {
            "entries": len(dictionary), "inherited_v10_entries": len(dictionary) - added_dictionary,
            "revised_v10_entries": revised_dictionary, "new_v11_entries": added_dictionary,
        },
        "claim_boundary": (
            "GDT634 is a complete concrete working edition of eight already selected lines: all 69 token positions and all 58 surface types receive a nonempty material, part, state, quality or quantity gloss and no banned generic work/process filler. The productive e-length, quality, CTH, minim and OL/OR layers are inherited; explicit reader evidence keeps the posaiin/poraiin fork, qotain|ol and cheo|ctheey boundaries, and the target-locus-only daiir/daiin normalization distinct. p-initial=pulvis, s-initial=sal, initial r=radix and initial l=liquor are deliberately aggressive historical-stem defaults; terminal p is a separate LOW pulver-form hypothesis. Herbal CTH alone specializes to leaf/herb, and terminal m remains a positional marker of unknown value. a/o before L/R remain distinct carriers, and o=preparation is construction-bound rather than a universal water/wine/oil value. The edition is a replaceable translation hypothesis, not a solved language, phonetic key or manuscript-wide plaintext."
        ),
        "inputs": {str(path): sha256(ROOT / path) for path in input_paths}, "outputs": output_hashes,
    }
    result = {**result_core, "content_sha256": canonical_hash(result_core)}
    (ROOT / OUTPUTS["result"]).write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        f"GDT634 built: lines={len(lines)} tokens={len(target_tokens)} types={len(target_types)} "
        f"quality={quality_diag['main_occurrences']}/{quality_diag['main_types']} "
        f"dictionary={len(dictionary)} unassigned=0"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
