#!/usr/bin/env python3
"""Build the GDT622 historical codebook and Voynich working-reader artifacts."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
sys.path.insert(0, str(ROOT))

from tools.vmanus_experiment import GuardedTSV  # noqa: E402


BASE_REL = Path("experiments/yolo/gdt622_clm667_temperament_codebook")
BASE = ROOT / BASE_REL
SOURCE_REL = BASE_REL / "artifacts/SOURCE_OBSERVATIONS.tsv"
PROVENANCE_REL = BASE_REL / "artifacts/SOURCE_PROVENANCE.tsv"
CANDIDATE_REL = BASE_REL / "artifacts/CANDIDATE_DECK.tsv"
TOKENS_REL = Path("transcription/voynich_zl3b_tokens.tsv")
MANUAL_RELS = {
    "ZL3b": Path("transcription/sources/ZL3b-n.txt"),
    "IT2a": Path("transcription/sources/IT2a-n.txt"),
    "RF1b": Path("transcription/sources/RF1b-e.txt"),
}
SAFE_REL = Path("gdt327_joint_tuple_interlinear.tsv")
GDT621_REL = Path(
    "experiments/yolo/gdt621_manual_source_double_reading/"
    "artifacts/SOURCE_DOUBLE_READING_RESULT.json"
)
GDT621_FINAL_REL = Path(
    "experiments/yolo/gdt621_manual_source_double_reading/FINAL_RESULT.md"
)

SUMMARY_REL = BASE_REL / "artifacts/CANDIDATE_FAMILY_SUMMARY.tsv"
OCCURRENCES_REL = BASE_REL / "artifacts/CANDIDATE_FAMILY_OCCURRENCES.tsv"
EXACT_REL = BASE_REL / "artifacts/EXACT_FORM_OCCURRENCES.tsv"
MINIMAL_REL = BASE_REL / "artifacts/MINIMAL_PAIR_EVIDENCE.tsv"
DEGREE_REL = BASE_REL / "artifacts/DEGREE_PAIR_MATRIX.tsv"
BLOCK_REL = BASE_REL / "artifacts/BLOCK_EVIDENCE.tsv"
ORIENTATION_REL = BASE_REL / "artifacts/ORIENTATION_COMPARISON.tsv"
DECK_ORIENTATION_REL = BASE_REL / "artifacts/DECK_ORIENTATION_COMPARISON.tsv"
MARKER_REL = BASE_REL / "artifacts/MARKER_PREVALENCE.tsv"
ALT_REL = BASE_REL / "artifacts/ALTERNATE_READING_EVIDENCE.tsv"
ALIGNMENT_REL = BASE_REL / "artifacts/CANDIDATE_ALIGNMENT.tsv"
DICTIONARY_REL = BASE_REL / "artifacts/WORKING_DICTIONARY.tsv"
TRANSLATION_REL = BASE_REL / "artifacts/WORKING_TRANSLATION.tsv"
RESULT_REL = BASE_REL / "artifacts/RESULT.json"

FAMILIES = {"KCH": "kch", "KSH": "ksh", "TCH": "tch", "TSH": "tsh"}
FAMILY_PARTS = {
    "KCH": ("k", "ch"),
    "KSH": ("k", "sh"),
    "TCH": ("t", "ch"),
    "TSH": ("t", "sh"),
}
Q_PREFIXES = {
    "KCH": "qokch",
    "KSH": "qoksh",
    "TCH": "qotch",
    "TSH": "qotsh",
}
OPPOSITE_MOISTURE = {
    "KCH": "KSH",
    "KSH": "KCH",
    "TCH": "TSH",
    "TSH": "TCH",
}
EXACT_FORM_FAMILY = {
    "qokchy": "KCH",
    "qokchey": "KCH",
    "qokshy": "KSH",
    "qokshey": "KSH",
    "qotchy": "TCH",
    "qotchey": "TCH",
    "qotshy": "TSH",
    "qotshey": "TSH",
}
EXACT_FORMS = tuple(EXACT_FORM_FAMILY)
QUALITY_WORDS = ("chol", "chor", "shol", "shor")
DEGREE_WORDS = ("dain", "daiin", "daiiin")

# These are exploratory opening/local windows around the candidate evidence.
# The windows were inspected during model development, so they are descriptive,
# not independent tests. Keeping them here exposes that choice and its baselines.
BLOCK_SPECS = (
    ("LIQ_F45_LOCAL", "Liquiritia", "LIQ_HIST_1", "f45r", 1, 5, "KCH", "I"),
    ("LIQ_F90_OPEN", "Liquiritia", "LIQ_DIRECT_1", "f90r1", 1, 5, "KCH", "I"),
    ("DIP_F3_LOCAL", "Diptamus", "DIP_HIST_1", "f3r", 13, 17, "KSH", "III"),
    ("DIP_F23_LOCAL", "Diptamus", "DIP_DIRECT_1", "f23v", 6, 12, "KSH", "III"),
    ("CUC_F24_LOCAL", "Cucurbita", "CUC_HIST_1", "f24r", 1, 12, "TCH", "II"),
    ("CUC_F36_OPEN", "Cucurbita", "CUC_HIST_2", "f36r", 1, 3, "TCH", "II"),
    ("CUC_F49_OPEN", "Cucurbita", "CUC_DIRECT_1", "f49r", 1, 3, "TCH", "II"),
    ("BAL_F38_OPEN", "Balsamus", "BAL_HIST_1", "f38r", 1, 3, "KSH", "II"),
    ("BAL_F32_OPEN", "Balsamus", "BAL_DIRECT_1", "f32r", 1, 5, "KSH", "II"),
)

ALT_SPECS = {
    "f3r.1": ("DIPTAMUS_NAME_CARRIER", "STABLE_ALL_THREE"),
    "f3r.13": ("HOT_DRY_EXACT_CORNER", "ZL_RF_QOKSHEY__IT_QOKCHEY"),
    "f3r.16": ("DEGREE_III_PACKAGE", "ZL_IT_QOKOL_DAIIN__RF_GLYPH_SPLIT"),
    "f19r.1": ("MOISTURE_MINIMAL_PAIR", "QOTSHY_QOTCHY_STABLE_ALL_THREE"),
    "f24r.1": ("CUCURBITA_NAME_CARRIER", "ZL_POR_SPLIT__IT_RF_PORORY_JOINED"),
    "f24r.2": ("DEGREE_II_MARKER", "QOTAIIN_STABLE_ALL_THREE"),
    "f24r.10": ("DEGREE_II_MARKER", "CHOTAIIN_STABLE_ALL_THREE"),
    "f24r.12": ("THERMAL_MINIMAL_PAIR", "QOKCHY_QOTCHY_STABLE_ALL_THREE"),
    "f25r.3": ("MOISTURE_MINIMAL_PAIR", "QOTCHY_QOTSHY_STABLE_ALL_THREE"),
    "f28v.5": ("MOISTURE_MINIMAL_PAIR", "QOTCHEY_QOTSHEY_STABLE_ALL_THREE"),
    "f38r.1": ("BALSAM_NAME_AND_DRY_FAMILY", "TOLOR_OKSHOL_STABLE_ALL_THREE"),
    "f38r.2": ("DRY_FAMILY_AND_DEGREE_II", "KSH_ZL_RF_ONLY__TWO_OTAIIN_STABLE"),
    "f38r.3": ("DEGREE_II_MARKER", "OTAIIN_STABLE__QO_BOUNDARY_VARIES"),
    "f41v.1": ("CERFOLIUM_LABEL_CARRIER", "KEEREDAL_VARIANT_ACROSS_ALL_THREE"),
    "f45r.1": ("LIQUORICE_NAME_CARRIER", "PYKYDAL_STABLE_ALL_THREE"),
    "f45r.3": ("HOT_MOIST_FAMILY", "KCHOL_DAIIN_STABLE_ALL_THREE"),
    "f45r.5": ("HOT_MOIST_EXACT_CORNER", "QOKCHY_STABLE__TOKENIZATION_VARIES"),
    "f23v.6": ("DIRECT_DECK_DRY_AND_DEGREE_CONTEXT", "SENSITIVITY_READING"),
    "f23v.7": ("DIRECT_DECK_DEGREE_III_CONTEXT", "SENSITIVITY_READING"),
    "f23v.10": ("DIRECT_DECK_HOT_DRY_CONTEXT", "SENSITIVITY_READING"),
    "f32r.2": ("DIRECT_DECK_BALSAM_CONTEXT", "SENSITIVITY_READING"),
    "f32r.3": ("DIRECT_DECK_BALSAM_CONTEXT", "SENSITIVITY_READING"),
    "f32r.5": ("DIRECT_DECK_THERMAL_MINIMAL_PAIR", "SENSITIVITY_READING"),
    "f36r.2": ("ALTERNATIVE_GOURD_DEGREE_II_CONTEXT", "SENSITIVITY_READING"),
    "f36r.3": ("ALTERNATIVE_GOURD_COLD_MOIST_CONTEXT", "SENSITIVITY_READING"),
    "f49r.1": ("DIRECT_DECK_CUCURBITA_CONTEXT", "SENSITIVITY_READING"),
    "f49r.2": ("DIRECT_DECK_CUCURBITA_CONTEXT", "SENSITIVITY_READING"),
    "f49r.3": ("DIRECT_DECK_CUCURBITA_CONTEXT", "SENSITIVITY_READING"),
    "f90r1.1": ("DIRECT_DECK_LIQUORICE_CONTEXT", "SENSITIVITY_READING"),
    "f90r1.2": ("DIRECT_DECK_LIQUORICE_CONTEXT", "SENSITIVITY_READING"),
    "f90r1.3": ("DIRECT_DECK_LIQUORICE_CONTEXT", "SENSITIVITY_READING"),
    "f90r1.4": ("DIRECT_DECK_LIQUORICE_CONTEXT", "SENSITIVITY_READING"),
    "f90r1.5": ("DIRECT_DECK_LIQUORICE_CONTEXT", "SENSITIVITY_READING"),
}

GERMAN = {
    "Balsamus": "Balsam",
    "Cerfolium": "Kerbel",
    "Cucurbita": "Kürbis/Kalebasse",
    "Diptamus": "Diptam",
    "Liquiritia": "Süßholz",
}
QUALITY_DE = {
    ("HOT", "DRY"): "heiß und trocken",
    ("HOT", "MOIST"): "heiß und feucht",
    ("COLD", "DRY"): "kalt und trocken",
    ("COLD", "MOIST"): "kalt und feucht",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_bytes(value: object) -> bytes:
    return (
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    ).encode("utf-8")


def canonical_hash(value: object) -> str:
    compact = json.dumps(
        value, sort_keys=True, ensure_ascii=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(compact).hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: Iterable[str]) -> None:
    fieldnames = list(fields)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=fieldnames,
            delimiter="\t",
            lineterminator="\n",
            extrasaction="raise",
        )
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def locus_number(locus: str) -> int:
    match = re.search(r"\.([0-9]+)$", locus)
    return int(match.group(1)) if match else 10**9


def token_sort_key(row: dict[str, str]) -> tuple[str, int, int]:
    return row["page"], locus_number(row["locus"]), int(row["token_index"])


def safe_pages() -> set[str]:
    source = GuardedTSV(
        ROOT / SAFE_REL,
        selector_column="page",
        allowed_values=None,
        forbidden_prefixes=("f84",),
        forbidden_action="error",
    )
    pages = {row["page"] for row in source}
    if not pages or any(page.startswith("f84") for page in pages):
        raise RuntimeError("safe-page inventory is empty or contains sealed material")
    return pages


def guarded_tokens(allowed: set[str]) -> tuple[list[dict[str, str]], dict[str, int]]:
    source = GuardedTSV(
        ROOT / TOKENS_REL,
        selector_column="page",
        allowed_values=allowed,
        forbidden_prefixes=("f84",),
        forbidden_action="skip",
    )
    rows = list(source)
    rows.sort(key=token_sort_key)
    return rows, {
        "selected": source.stats.selected,
        "skipped_forbidden": source.stats.skipped_forbidden,
        "skipped_not_allowed": source.stats.skipped_not_allowed,
    }


def guarded_manual_selected(
    path: Path, allowed_loci: set[str]
) -> tuple[dict[str, str], int]:
    selected: dict[str, str] = {}
    skipped_forbidden = 0
    selector_pattern = re.compile(r"^<([^,>]+),")
    payload_pattern = re.compile(r"^<[^>]+>\s+(.*)$")
    with path.open(encoding="utf-8") as handle:
        for raw_line in handle:
            selector = selector_pattern.match(raw_line)
            if selector is None:
                continue
            locus = selector.group(1)
            page = locus.split(".", 1)[0]
            if page.startswith("f84"):
                skipped_forbidden += 1
                continue
            if locus not in allowed_loci:
                continue
            payload = payload_pattern.match(raw_line.rstrip("\n"))
            if payload is None or locus in selected:
                raise RuntimeError(f"manual reading parse/duplicate error: {path} {locus}")
            selected[locus] = payload.group(1).strip()
    missing = allowed_loci - set(selected)
    if missing:
        raise RuntimeError(f"manual reading missing loci in {path}: {sorted(missing)}")
    return selected, skipped_forbidden


def family_hits(surface: str) -> list[str]:
    return [family for family, literal in FAMILIES.items() if literal in surface]


def q_family_hits(surface: str) -> list[str]:
    return [
        family for family, literal in Q_PREFIXES.items() if surface.startswith(literal)
    ]


def parse_exact_code(surface: str) -> tuple[str, str, str] | None:
    match = re.fullmatch(r"qo([kt])(ch|sh)(y|ey)", surface)
    if match is None:
        return None
    return match.group(1), match.group(2), match.group(3)


def carrier_display(candidate: dict[str, str]) -> str:
    if candidate["candidate_id"] == "CUC_HIST_1":
        return "por [ZL3b] | porory… [IT2a/RF1b]"
    if candidate["candidate_id"] == "CER_SHARED_1":
        return "keer[e:o]dal [ZL3b] | keerodal [IT2a] | keesedal [RF1b]"
    return candidate["name_carrier_default"]


def build_dictionary(candidates: list[dict[str, str]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = [
        {
            "layer": "CLM667_CONFIRMED",
            "surface": "c",
            "composition_slot": "THERMAL_1",
            "default_meaning_de": "heiß",
            "status": "HISTORICAL_CODE_CONFIRMED",
            "evidence": "Repeated Clm 667 rows with readable Latin drug names.",
            "caveat": "This is a Clm 667 value, not a Voynich glyph value.",
        },
        {
            "layer": "CLM667_CONFIRMED",
            "surface": "f",
            "composition_slot": "THERMAL_1",
            "default_meaning_de": "kalt",
            "status": "HISTORICAL_CODE_CONFIRMED",
            "evidence": "Repeated Clm 667 rows with readable Latin drug names.",
            "caveat": "This is a Clm 667 value, not a Voynich glyph value.",
        },
        {
            "layer": "CLM667_CONFIRMED",
            "surface": "s",
            "composition_slot": "MOISTURE_2",
            "default_meaning_de": "trocken",
            "status": "HISTORICAL_CODE_CONFIRMED",
            "evidence": "Repeated Clm 667 rows and separable degrees.",
            "caveat": "This is a Clm 667 value, not a Voynich glyph value.",
        },
        {
            "layer": "CLM667_CONFIRMED",
            "surface": "h",
            "composition_slot": "MOISTURE_2",
            "default_meaning_de": "feucht",
            "status": "HISTORICAL_CODE_CONFIRMED",
            "evidence": "Buglossum, Bdellium and Zinziber rows.",
            "caveat": "This is a Clm 667 value, not a Voynich glyph value.",
        },
        {
            "layer": "CLM667_CONFIRMED",
            "surface": "pbar",
            "composition_slot": "DEGREE",
            "default_meaning_de": "Grad 1 / primo",
            "status": "HISTORICAL_CODE_CONFIRMED",
            "evidence": "Capped p abbreviation beside numeric-degree controls.",
            "caveat": "Scope can be one quality or the quality pair.",
        },
        {
            "layer": "CLM667_CONFIRMED",
            "surface": "1|2|3|4",
            "composition_slot": "DEGREE",
            "default_meaning_de": "Grad 1|2|3|4",
            "status": "HISTORICAL_CODE_CONFIRMED",
            "evidence": "Numeric values occur after either quality.",
            "caveat": "A single final number can have shared scope.",
        },
        {
            "layer": "VOYNICH_WORKING",
            "surface": "k",
            "composition_slot": "THERMAL_1",
            "default_meaning_de": "heiß",
            "status": "EXPLORATORY_DEFAULT",
            "evidence": "KCH enrichment on liquorice blocks and KSH on two hot/dry historical candidates.",
            "caveat": "Diptamus whole-page totals contain more T than K composites.",
        },
        {
            "layer": "VOYNICH_WORKING",
            "surface": "t",
            "composition_slot": "THERMAL_1",
            "default_meaning_de": "kalt",
            "status": "EXPLORATORY_DEFAULT",
            "evidence": "TCH enrichment on cucurbita candidates, especially f36r and f49r.",
            "caveat": "TCH is globally common and also appears on non-cold candidates.",
        },
        {
            "layer": "VOYNICH_WORKING",
            "surface": "ch",
            "composition_slot": "MOISTURE_2",
            "default_meaning_de": "feucht",
            "status": "EXPLORATORY_DEFAULT",
            "evidence": "KCH and TCH are the predicted moist quadrants.",
            "caveat": "The value is not independently fixed outside the plant deck.",
        },
        {
            "layer": "VOYNICH_WORKING",
            "surface": "sh",
            "composition_slot": "MOISTURE_2",
            "default_meaning_de": "trocken",
            "status": "EXPLORATORY_DEFAULT",
            "evidence": "Rare KSH forms occur on f3r and f38r, both hot/dry candidates.",
            "caveat": "SH families are much rarer than CH families.",
        },
        {
            "layer": "VOYNICH_WORKING",
            "surface": "qo-",
            "composition_slot": "QUALITY_FIELD_WRAPPER",
            "default_meaning_de": "Qualitätsangabe / ist von der Eigenschaft",
            "status": "EXPLORATORY_STRUCTURAL_DEFAULT",
            "evidence": "The four exact qokch/qoksh/qotch/qotsh families share this wrapper.",
            "caveat": "q and o are not separately translated here.",
        },
        {
            "layer": "VOYNICH_WORKING_BUNDLE",
            "surface": "qokch-(y|ey)",
            "composition_slot": "QUALITY_CODE",
            "default_meaning_de": "Temperament: heiß und feucht",
            "status": "CONCRETE_EXPLORATORY_DEFAULT",
            "evidence": "Stable exact qokchy plus KCH concentration in both liquorice blocks.",
            "caveat": "The final y/ey is not assigned a degree value.",
        },
        {
            "layer": "VOYNICH_WORKING_BUNDLE",
            "surface": "qoksh-(y|ey)",
            "composition_slot": "QUALITY_CODE",
            "default_meaning_de": "Temperament: heiß und trocken",
            "status": "CONCRETE_EXPLORATORY_DEFAULT",
            "evidence": "Rare KSH forms occur in both Diptamus local blocks and the f38r Balsam opening.",
            "caveat": "f3r qokshey is ZL3b/RF1b; IT2a reads qokchey.",
        },
        {
            "layer": "VOYNICH_WORKING_BUNDLE",
            "surface": "qotch-(y|ey)",
            "composition_slot": "QUALITY_CODE",
            "default_meaning_de": "Temperament: kalt und feucht",
            "status": "CONCRETE_EXPLORATORY_DEFAULT",
            "evidence": "Stable exact qotchy and a clean TCH opening on f36r.",
            "caveat": "TCH is common, so the bundle alone does not identify a plant.",
        },
        {
            "layer": "VOYNICH_WORKING_BUNDLE",
            "surface": "qotsh-(y|ey)",
            "composition_slot": "QUALITY_CODE",
            "default_meaning_de": "Temperament: kalt und trocken",
            "status": "CONCRETE_EXPLORATORY_DEFAULT",
            "evidence": "The fourth combinatorial corner exists and forms sh/ch minimal pairs.",
            "caveat": "It has no named-plant anchor in the current five-item deck.",
        },
        {
            "layer": "VOYNICH_WORKING",
            "surface": "-(y|ey)",
            "composition_slot": "QUALITY_CODE_ENDING",
            "default_meaning_de": "Abschluss oder Verbindung des Eigenschaftscodes",
            "status": "EXPLORATORY_SLOT_ONLY",
            "evidence": "The ending occurs after multiple quality quadrants and across source degrees.",
            "caveat": "It cannot currently mean a particular numeric degree.",
        },
        {
            "layer": "VOYNICH_WORKING",
            "surface": "unmarkiert",
            "composition_slot": "DEGREE",
            "default_meaning_de": "Grad 1",
            "status": "EXPLORATORY_DEGREE_DEFAULT",
            "evidence": "The two liquorice windows lack otaiin and direct same-line (q)okol daiin.",
            "caveat": "This is a page-local absence default, not a decoded glyph; 94/181 safe pages lack both markers.",
        },
        {
            "layer": "VOYNICH_WORKING",
            "surface": "otaiin-family",
            "composition_slot": "DEGREE",
            "default_meaning_de": "Grad 2",
            "status": "EXPLORATORY_DEGREE_DEFAULT",
            "evidence": "It occurs in the f24r and f36r Cucurbita windows and the f38r Balsam opening, but not in either liquorice or Diptamus window.",
            "caveat": "It is common on 81/181 safe pages, and the visual f49r Cucurbita alternative lacks it.",
        },
        {
            "layer": "VOYNICH_WORKING",
            "surface": "dain|daiin|daiiin",
            "composition_slot": "DEGREE_OR_NUMBER_FAMILY",
            "default_meaning_de": "Grad-/Zahlwert, genaue Reihenfolge offen",
            "status": "EXPLORATORY_FAMILY_ONLY",
            "evidence": "These forms follow chol/chor/shol/shor in a recurrent compact bundle.",
            "caveat": "They do not map cleanly to degrees 1/2/3 on the named plant candidates.",
        },
        {
            "layer": "VOYNICH_ALTERNATE_WORKING",
            "surface": "ch|sh + ol|or",
            "composition_slot": "TWO_BY_TWO_QUALITY_BUNDLE",
            "default_meaning_de": "zweiachsige Eigenschaft; Achsenzuordnung noch offen",
            "status": "EXPLORATORY_COMPETING_SEGMENTATION",
            "evidence": "chol/chor/shol/shor immediately precede the degree family on many Herbal lines.",
            "caveat": "The same chol+daiin pair occurs on unlike plant candidates.",
        },
        {
            "layer": "VOYNICH_WORKING",
            "surface": "(q)okol + daiin",
            "composition_slot": "POSSIBLE_DEGREE_3_EXTENSION",
            "default_meaning_de": "Grad 3",
            "status": "EXPLORATORY_DEGREE_DEFAULT",
            "evidence": "The sequence follows dry-family material in both Diptamus candidate blocks.",
            "caveat": "It is rare (9 adjacent events on 8/181 safe pages) but not isolated from other functions of okol and daiin.",
        },
    ]
    for candidate in candidates:
        if candidate["working_selection"] != "PREFERRED":
            continue
        rows.append(
            {
                "layer": "VOYNICH_PAGE_NAME_DEFAULT",
                "surface": carrier_display(candidate),
                "composition_slot": "LEARNED_WHOLE_PLANT_NAME",
                "default_meaning_de": GERMAN[candidate["plant"]],
                "status": "CANDIDATE_NAME_CARRIER_DEFAULT",
                "evidence": f"{candidate['folio']} selected by {candidate['candidate_basis']} plus the current code profile.",
                "caveat": "This assigns a throughput placeholder only; neither page identity nor carrier meaning is a decoded lexeme.",
            }
        )
    return rows


def main() -> int:
    source_rows = read_tsv(ROOT / SOURCE_REL)
    provenance_rows = read_tsv(ROOT / PROVENANCE_REL)
    candidates = read_tsv(ROOT / CANDIDATE_REL)
    allowed_alt_loci = set(ALT_SPECS)
    manual_readings: dict[str, dict[str, str]] = {}
    manual_forbidden_skips: dict[str, int] = {}
    for edition, path in MANUAL_RELS.items():
        readings, skipped = guarded_manual_selected(ROOT / path, allowed_alt_loci)
        manual_readings[edition] = readings
        manual_forbidden_skips[edition] = skipped
    alt_rows = []
    for locus, (evidence_role, agreement_class) in ALT_SPECS.items():
        values = {edition: manual_readings[edition][locus] for edition in MANUAL_RELS}
        alt_rows.append(
            {
                "locus": locus,
                "evidence_role": evidence_role,
                "ZL3b_raw": values["ZL3b"],
                "IT2a_raw": values["IT2a"],
                "RF1b_raw": values["RF1b"],
                "all_raw_identical": int(len(set(values.values())) == 1),
                "agreement_class": agreement_class,
                "reading_rule": "ALTERNATE_READINGS_OF_ONE_MANUSCRIPT",
            }
        )
    write_tsv(
        ROOT / ALT_REL,
        alt_rows,
        (
            "locus",
            "evidence_role",
            "ZL3b_raw",
            "IT2a_raw",
            "RF1b_raw",
            "all_raw_identical",
            "agreement_class",
            "reading_rule",
        ),
    )
    inventory_pages = safe_pages()
    candidate_pages = {row["folio"] for row in candidates}
    if any(page.startswith("f84") for page in candidate_pages):
        raise RuntimeError("candidate deck contains sealed material")
    # GDT327 is a safe 91-page structural panel rather than a complete folio
    # catalog. Explicit candidate pages may extend it; the GuardedTSV still
    # rejects every f84 selector before parsing the rest of that row.
    allowed_pages = inventory_pages | candidate_pages

    all_tokens, guard_stats = guarded_tokens(allowed_pages)
    if guard_stats["skipped_forbidden"] <= 0:
        raise RuntimeError("mixed transcription guard did not reject sealed rows")
    candidate_tokens = [row for row in all_tokens if row["page"] in candidate_pages]
    all_by_page: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in all_tokens:
        all_by_page[row["page"]].append(row)
    by_page: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in candidate_tokens:
        by_page[row["page"]].append(row)

    occurrence_rows: list[dict[str, object]] = []
    summary_rows: list[dict[str, object]] = []
    summary_by_id: dict[str, dict[str, object]] = {}
    for candidate in candidates:
        rows = by_page[candidate["folio"]]
        counts = Counter()
        q_counts = Counter()
        examples: dict[str, list[str]] = defaultdict(list)
        for row in rows:
            for family in family_hits(row["eva"]):
                counts[family] += 1
                examples[family].append(
                    f"{row['locus']}:{row['token_index']}={row['eva']}"
                )
                occurrence_rows.append(
                    {
                        "candidate_id": candidate["candidate_id"],
                        "plant": candidate["plant"],
                        "folio": candidate["folio"],
                        "locus": row["locus"],
                        "token_index": row["token_index"],
                        "surface": row["eva"],
                        "family": family,
                        "q_prefixed": int(family in q_family_hits(row["eva"])),
                        "expected_for_candidate": int(
                            family == candidate["expected_family"]
                        ),
                    }
                )
            for family in q_family_hits(row["eva"]):
                q_counts[family] += 1

        expected = candidate["expected_family"]
        support = counts[expected] if expected in FAMILIES else ""
        contradiction = (
            counts[OPPOSITE_MOISTURE[expected]] if expected in FAMILIES else ""
        )
        first = rows[0]
        if first["eva"] != candidate["name_carrier_default"]:
            raise RuntimeError(
                f"name carrier mismatch for {candidate['candidate_id']}: "
                f"{first['eva']} != {candidate['name_carrier_default']}"
            )
        summary = {
            "candidate_id": candidate["candidate_id"],
            "plant": candidate["plant"],
            "candidate_basis": candidate["candidate_basis"],
            "folio": candidate["folio"],
            "working_selection": candidate["working_selection"],
            "name_carrier_default": candidate["name_carrier_default"],
            "carrier_kind": first["kind"],
            "tokens": len(rows),
            "expected_family": expected,
            "KCH": counts["KCH"],
            "KSH": counts["KSH"],
            "TCH": counts["TCH"],
            "TSH": counts["TSH"],
            "QOKCH": q_counts["KCH"],
            "QOKSH": q_counts["KSH"],
            "QOTCH": q_counts["TCH"],
            "QOTSH": q_counts["TSH"],
            "expected_count": support,
            "same_thermal_opposite_moisture_count": contradiction,
            "expected_minus_opposite": (
                int(support) - int(contradiction) if support != "" else ""
            ),
            "expected_examples": (
                ("|".join(examples[expected][:12]) or "NONE")
                if expected in FAMILIES
                else "NOT_APPLICABLE"
            ),
        }
        summary_rows.append(summary)
        summary_by_id[candidate["candidate_id"]] = summary

    occurrence_rows.sort(
        key=lambda row: (
            str(row["folio"]),
            locus_number(str(row["locus"])),
            int(row["token_index"]),
            str(row["family"]),
        )
    )
    write_tsv(
        ROOT / OCCURRENCES_REL,
        occurrence_rows,
        (
            "candidate_id",
            "plant",
            "folio",
            "locus",
            "token_index",
            "surface",
            "family",
            "q_prefixed",
            "expected_for_candidate",
        ),
    )
    write_tsv(
        ROOT / SUMMARY_REL,
        summary_rows,
        (
            "candidate_id",
            "plant",
            "candidate_basis",
            "folio",
            "working_selection",
            "name_carrier_default",
            "carrier_kind",
            "tokens",
            "expected_family",
            "KCH",
            "KSH",
            "TCH",
            "TSH",
            "QOKCH",
            "QOKSH",
            "QOTCH",
            "QOTSH",
            "expected_count",
            "same_thermal_opposite_moisture_count",
            "expected_minus_opposite",
            "expected_examples",
        ),
    )

    exact_rows: list[dict[str, object]] = []
    exact_counts = Counter()
    exact_pages: dict[str, set[str]] = defaultdict(set)
    exact_group_counts = Counter()
    exact_group_pages: dict[tuple[str, str], set[str]] = defaultdict(set)
    for row in all_tokens:
        if row["eva"] not in EXACT_FORMS:
            continue
        corpus_group = (
            "HERBAL_A"
            if row["section"] == "H" and row["language"] == "A"
            else "OTHER_SAFE"
        )
        exact_counts[row["eva"]] += 1
        exact_pages[row["eva"]].add(row["page"])
        exact_group_counts[(row["eva"], corpus_group)] += 1
        exact_group_pages[(row["eva"], corpus_group)].add(row["page"])
        exact_rows.append(
            {
                "surface": row["eva"],
                "family": EXACT_FORM_FAMILY[row["eva"]],
                "page": row["page"],
                "locus": row["locus"],
                "token_index": row["token_index"],
                "section": row["section"],
                "language": row["language"],
                "corpus_group": corpus_group,
                "candidate_contact": int(row["page"] in candidate_pages),
            }
        )
    write_tsv(
        ROOT / EXACT_REL,
        exact_rows,
        (
            "surface",
            "family",
            "page",
            "locus",
            "token_index",
            "section",
            "language",
            "corpus_group",
            "candidate_contact",
        ),
    )

    exact_by_locus: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in exact_rows:
        exact_by_locus[(str(row["page"]), str(row["locus"]))].append(row)
    minimal_rows: list[dict[str, object]] = []
    for (_page, _locus), rows in exact_by_locus.items():
        rows.sort(key=lambda row: int(row["token_index"]))
        for left_index, left in enumerate(rows):
            left_parts = parse_exact_code(str(left["surface"]))
            if left_parts is None:
                continue
            for right in rows[left_index + 1 :]:
                right_parts = parse_exact_code(str(right["surface"]))
                if right_parts is None or left_parts[2] != right_parts[2]:
                    continue
                differences = [
                    index
                    for index, (left_part, right_part) in enumerate(
                        zip(left_parts[:2], right_parts[:2])
                    )
                    if left_part != right_part
                ]
                if len(differences) != 1:
                    continue
                axis = "THERMAL_K_T" if differences[0] == 0 else "MOISTURE_CH_SH"
                minimal_rows.append(
                    {
                        "page": left["page"],
                        "locus": left["locus"],
                        "left_token_index": left["token_index"],
                        "left_surface": left["surface"],
                        "left_family": left["family"],
                        "right_token_index": right["token_index"],
                        "right_surface": right["surface"],
                        "right_family": right["family"],
                        "changed_axis": axis,
                        "shared_ending": left_parts[2],
                    }
                )
    write_tsv(
        ROOT / MINIMAL_REL,
        minimal_rows,
        (
            "page",
            "locus",
            "left_token_index",
            "left_surface",
            "left_family",
            "right_token_index",
            "right_surface",
            "right_family",
            "changed_axis",
            "shared_ending",
        ),
    )

    block_rows: list[dict[str, object]] = []
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    opposite_thermal = {"KCH": "TCH", "KSH": "TSH", "TCH": "KCH", "TSH": "KSH"}
    diagonal = {"KCH": "TSH", "KSH": "TCH", "TCH": "KSH", "TSH": "KCH"}
    for (
        block_id,
        plant,
        candidate_id,
        folio,
        locus_start,
        locus_end,
        expected_family,
        expected_degree,
    ) in BLOCK_SPECS:
        rows = [
            row
            for row in by_page[folio]
            if locus_start <= locus_number(row["locus"]) <= locus_end
        ]
        if not rows:
            raise RuntimeError(f"empty evidence block: {block_id}")
        counts = Counter()
        for row in rows:
            counts.update(family_hits(row["eva"]))
        block_loci: dict[str, list[dict[str, str]]] = defaultdict(list)
        for row in rows:
            block_loci[row["locus"]].append(row)
        okol_daiin_count = 0
        for locus_rows in block_loci.values():
            locus_rows.sort(key=lambda row: int(row["token_index"]))
            for left, right in zip(locus_rows, locus_rows[1:]):
                if left["eva"] in {"okol", "qokol"} and right["eva"] == "daiin":
                    okol_daiin_count += 1
        otaiin_count = sum("otaiin" in row["eva"] for row in rows)
        if expected_degree == "I":
            marker_match = int(otaiin_count == 0 and okol_daiin_count == 0)
        elif expected_degree == "II":
            marker_match = int(otaiin_count > 0)
        elif expected_degree == "III":
            marker_match = int(okol_daiin_count > 0)
        else:
            raise RuntimeError(f"unknown expected degree: {expected_degree}")
        evidence = []
        for row in rows:
            surface = row["eva"]
            if (
                family_hits(surface)
                or "otaiin" in surface
                or surface in {"shor", "chor", "okol", "qokol", "daiin"}
            ):
                evidence.append(f"{row['locus']}:{row['token_index']}={surface}")
        candidate = candidate_by_id[candidate_id]
        herbal_a_by_page = {
            page: page_rows
            for page, page_rows in all_by_page.items()
            if any(
                row["section"] == "H" and row["language"] == "A"
                for row in page_rows
            )
        }
        baseline_local_counts = []
        baseline_whole_rates = []
        for page_rows in herbal_a_by_page.values():
            local_count = sum(
                expected_family in family_hits(row["eva"])
                for row in page_rows
                if locus_start <= locus_number(row["locus"]) <= locus_end
            )
            baseline_local_counts.append(local_count)
            whole_count = sum(
                expected_family in family_hits(row["eva"]) for row in page_rows
            )
            baseline_whole_rates.append(100.0 * whole_count / len(page_rows))
        candidate_whole_rows = by_page[folio]
        candidate_whole_count = sum(
            expected_family in family_hits(row["eva"])
            for row in candidate_whole_rows
        )
        candidate_whole_rate = 100.0 * candidate_whole_count / len(
            candidate_whole_rows
        )
        block_rows.append(
            {
                "block_id": block_id,
                "plant": plant,
                "candidate_id": candidate_id,
                "working_selection": candidate["working_selection"],
                "folio": folio,
                "locus_range": f"{folio}.{locus_start}-{locus_end}",
                "expected_family": expected_family,
                "expected_degree": expected_degree,
                "KCH": counts["KCH"],
                "KSH": counts["KSH"],
                "TCH": counts["TCH"],
                "TSH": counts["TSH"],
                "expected_count": counts[expected_family],
                "same_thermal_opposite_moisture_count": counts[
                    OPPOSITE_MOISTURE[expected_family]
                ],
                "opposite_thermal_same_moisture_count": counts[
                    opposite_thermal[expected_family]
                ],
                "diagonal_count": counts[diagonal[expected_family]],
                "otaiin_count": otaiin_count,
                "okol_daiin_count": okol_daiin_count,
                "degree_marker_match": marker_match,
                "herbal_a_baseline_pages": len(herbal_a_by_page),
                "local_count_rank_min": 1
                + sum(value > counts[expected_family] for value in baseline_local_counts),
                "local_pages_at_or_above": sum(
                    value >= counts[expected_family] for value in baseline_local_counts
                ),
                "whole_page_expected_rate_per_100": f"{candidate_whole_rate:.6f}",
                "whole_rate_rank_min": 1
                + sum(value > candidate_whole_rate for value in baseline_whole_rates),
                "whole_pages_at_or_above": sum(
                    value >= candidate_whole_rate for value in baseline_whole_rates
                ),
                "evidence_sequence": "|".join(evidence),
            }
        )
    write_tsv(
        ROOT / BLOCK_REL,
        block_rows,
        (
            "block_id",
            "plant",
            "candidate_id",
            "working_selection",
            "folio",
            "locus_range",
            "expected_family",
            "expected_degree",
            "KCH",
            "KSH",
            "TCH",
            "TSH",
            "expected_count",
            "same_thermal_opposite_moisture_count",
            "opposite_thermal_same_moisture_count",
            "diagonal_count",
            "otaiin_count",
            "okol_daiin_count",
            "degree_marker_match",
            "herbal_a_baseline_pages",
            "local_count_rank_min",
            "local_pages_at_or_above",
            "whole_page_expected_rate_per_100",
            "whole_rate_rank_min",
            "whole_pages_at_or_above",
            "evidence_sequence",
        ),
    )
    block_by_candidate = {row["candidate_id"]: row for row in block_rows}
    block_spec_by_candidate = {spec[2]: spec for spec in BLOCK_SPECS}
    alignment_rows: list[dict[str, object]] = []
    for candidate in candidates:
        if candidate["working_selection"] != "PREFERRED":
            continue
        folio = candidate["folio"]
        name_row = by_page[folio][0]
        quality_row: dict[str, str] | None = None
        degree_locus = ""
        degree_surface = ""
        if candidate["candidate_id"] in block_spec_by_candidate:
            spec = block_spec_by_candidate[candidate["candidate_id"]]
            start, end = int(spec[4]), int(spec[5])
            local_rows = [
                row
                for row in by_page[folio]
                if start <= locus_number(row["locus"]) <= end
            ]
            quality_row = next(
                (
                    row
                    for row in local_rows
                    if candidate["expected_family"] in family_hits(row["eva"])
                ),
                None,
            )
            if candidate["shared_degree"] == "2":
                marker = next(
                    (row for row in local_rows if "otaiin" in row["eva"]), None
                )
                if marker is not None:
                    degree_locus = marker["locus"]
                    degree_surface = marker["eva"]
            elif candidate["shared_degree"] == "3":
                local_by_locus: dict[str, list[dict[str, str]]] = defaultdict(list)
                for row in local_rows:
                    local_by_locus[row["locus"]].append(row)
                for locus_rows in local_by_locus.values():
                    locus_rows.sort(key=lambda row: int(row["token_index"]))
                    for left, right in zip(locus_rows, locus_rows[1:]):
                        if left["eva"] in {"okol", "qokol"} and right["eva"] == "daiin":
                            degree_locus = left["locus"]
                            degree_surface = f"{left['eva']} {right['eva']}"
                            break
                    if degree_locus:
                        break
        name_line = locus_number(name_row["locus"])
        quality_line = locus_number(quality_row["locus"]) if quality_row else None
        degree_line = locus_number(degree_locus) if degree_locus else None
        alignment_rows.append(
            {
                "candidate_id": candidate["candidate_id"],
                "plant": candidate["plant"],
                "folio": folio,
                "name_locus": name_row["locus"],
                "name_surface": carrier_display(candidate),
                "name_carrier_basis": candidate["carrier_basis"],
                "quality_locus": quality_row["locus"] if quality_row else "",
                "quality_surface": quality_row["eva"] if quality_row else "",
                "quality_family": candidate["expected_family"],
                "name_to_quality_line_distance": (
                    quality_line - name_line if quality_line is not None else ""
                ),
                "degree_locus": degree_locus,
                "degree_surface": degree_surface,
                "source_expected_degree": candidate["shared_degree"],
                "name_to_degree_line_distance": (
                    degree_line - name_line if degree_line is not None else ""
                ),
                "alignment_scope": (
                    "SAME_LINE"
                    if quality_line == name_line
                    else "PAGE_LOCAL_DISTRIBUTED"
                    if quality_line is not None
                    else "NAME_ONLY_NO_QUALITY_READING"
                ),
            }
        )
    write_tsv(
        ROOT / ALIGNMENT_REL,
        alignment_rows,
        (
            "candidate_id",
            "plant",
            "folio",
            "name_locus",
            "name_surface",
            "name_carrier_basis",
            "quality_locus",
            "quality_surface",
            "quality_family",
            "name_to_quality_line_distance",
            "degree_locus",
            "degree_surface",
            "source_expected_degree",
            "name_to_degree_line_distance",
            "alignment_scope",
        ),
    )
    alignment_by_candidate = {
        row["candidate_id"]: row for row in alignment_rows
    }

    orientations: list[tuple[str, dict[str, str]]] = []
    for hot_atom, cold_atom in (("k", "t"), ("t", "k")):
        for moist_atom, dry_atom in (("ch", "sh"), ("sh", "ch")):
            orientations.append(
                (
                    f"KT_THERMAL__{hot_atom}_HOT__{moist_atom}_MOIST",
                    {
                        hot_atom: "HOT",
                        cold_atom: "COLD",
                        moist_atom: "MOIST",
                        dry_atom: "DRY",
                    },
                )
            )
    for moist_atom, dry_atom in (("k", "t"), ("t", "k")):
        for hot_atom, cold_atom in (("ch", "sh"), ("sh", "ch")):
            orientations.append(
                (
                    f"KT_MOISTURE__{hot_atom}_HOT__{moist_atom}_MOIST",
                    {
                        hot_atom: "HOT",
                        cold_atom: "COLD",
                        moist_atom: "MOIST",
                        dry_atom: "DRY",
                    },
                )
            )
    orientation_rows: list[dict[str, object]] = []
    for assignment_id, assignment in orientations:
        matched = 0
        total = 0
        positive_blocks = 0
        block_scores = []
        for block in block_rows:
            if block["working_selection"] != "PREFERRED":
                continue
            candidate = candidate_by_id[str(block["candidate_id"])]
            target = (candidate["thermal"], candidate["moisture"])
            local_match = 0
            local_total = 0
            for family, (left_atom, right_atom) in FAMILY_PARTS.items():
                count = int(block[family])
                local_total += count
                values = (assignment[left_atom], assignment[right_atom])
                mapped = (
                    next(value for value in values if value in {"HOT", "COLD"}),
                    next(value for value in values if value in {"MOIST", "DRY"}),
                )
                if mapped == target:
                    local_match += count
            matched += local_match
            total += local_total
            positive_blocks += int(local_match > 0)
            block_scores.append(f"{block['block_id']}={local_match}/{local_total}")
        orientation_rows.append(
            {
                "assignment_id": assignment_id,
                "k": assignment["k"],
                "t": assignment["t"],
                "ch": assignment["ch"],
                "sh": assignment["sh"],
                "matched_occurrences": matched,
                "total_family_occurrences": total,
                "positive_blocks": positive_blocks,
                "surface_reading_basis": "ZL3b_PRIMARY_WITH_SELECTED_LOCUS_ALTERNATE_AUDIT",
                "block_scores": "|".join(block_scores),
            }
        )
    orientation_rows.sort(
        key=lambda row: (
            -int(row["matched_occurrences"]),
            -int(row["positive_blocks"]),
            str(row["assignment_id"]),
        )
    )
    for rank, row in enumerate(orientation_rows, start=1):
        row["rank"] = rank
    write_tsv(
        ROOT / ORIENTATION_REL,
        orientation_rows,
        (
            "rank",
            "assignment_id",
            "k",
            "t",
            "ch",
            "sh",
            "matched_occurrences",
            "total_family_occurrences",
            "positive_blocks",
            "surface_reading_basis",
            "block_scores",
        ),
    )

    comparison_decks = {
        "EXTERNAL_PREEXISTING_PROPOSALS": (
            "BAL_HIST_1",
            "CUC_HIST_1",
            "DIP_HIST_1",
            "LIQ_HIST_1",
        ),
        "INTERNAL_DIRECT_IMAGE_MATCHES": (
            "BAL_DIRECT_1",
            "CUC_DIRECT_1",
            "DIP_DIRECT_1",
            "LIQ_DIRECT_1",
        ),
    }
    deck_orientation_rows: list[dict[str, object]] = []
    for deck_id, candidate_ids in comparison_decks.items():
        deck_blocks = [
            block for block in block_rows if block["candidate_id"] in candidate_ids
        ]
        if len(deck_blocks) != 4:
            raise RuntimeError(f"incomplete comparison deck: {deck_id}")
        unranked = []
        for assignment_id, assignment in orientations:
            matched = 0
            total = 0
            positive_blocks = 0
            block_scores = []
            for block in deck_blocks:
                candidate = candidate_by_id[str(block["candidate_id"])]
                target = (candidate["thermal"], candidate["moisture"])
                local_match = 0
                local_total = 0
                for family, (left_atom, right_atom) in FAMILY_PARTS.items():
                    count = int(block[family])
                    local_total += count
                    values = (assignment[left_atom], assignment[right_atom])
                    mapped = (
                        next(
                            value for value in values if value in {"HOT", "COLD"}
                        ),
                        next(
                            value for value in values if value in {"MOIST", "DRY"}
                        ),
                    )
                    if mapped == target:
                        local_match += count
                matched += local_match
                total += local_total
                positive_blocks += int(local_match > 0)
                block_scores.append(
                    f"{block['candidate_id']}={local_match}/{local_total}"
                )
            unranked.append(
                {
                    "deck_id": deck_id,
                    "candidate_ids": "|".join(candidate_ids),
                    "assignment_id": assignment_id,
                    "k": assignment["k"],
                    "t": assignment["t"],
                    "ch": assignment["ch"],
                    "sh": assignment["sh"],
                    "matched_occurrences": matched,
                    "total_family_occurrences": total,
                    "positive_blocks": positive_blocks,
                    "degree_marker_matches": sum(
                        int(block["degree_marker_match"]) for block in deck_blocks
                    ),
                    "surface_reading_basis": "ZL3b_PRIMARY_WITH_SELECTED_LOCUS_ALTERNATE_AUDIT",
                    "block_scores": "|".join(block_scores),
                }
            )
        for row in unranked:
            row["count_rank_min"] = 1 + sum(
                int(other["matched_occurrences"]) > int(row["matched_occurrences"])
                for other in unranked
            )
            row["binary_rank_min"] = 1 + sum(
                int(other["positive_blocks"]) > int(row["positive_blocks"])
                for other in unranked
            )
        deck_orientation_rows.extend(unranked)
    deck_orientation_rows.sort(
        key=lambda row: (
            str(row["deck_id"]),
            int(row["count_rank_min"]),
            -int(row["positive_blocks"]),
            str(row["assignment_id"]),
        )
    )
    write_tsv(
        ROOT / DECK_ORIENTATION_REL,
        deck_orientation_rows,
        (
            "deck_id",
            "candidate_ids",
            "count_rank_min",
            "binary_rank_min",
            "assignment_id",
            "k",
            "t",
            "ch",
            "sh",
            "matched_occurrences",
            "total_family_occurrences",
            "positive_blocks",
            "degree_marker_matches",
            "surface_reading_basis",
            "block_scores",
        ),
    )

    by_locus: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in all_tokens:
        by_locus[(row["page"], row["locus"])].append(row)
    degree_pairs = Counter()
    degree_pair_pages: dict[tuple[str, str], set[str]] = defaultdict(set)
    degree_candidate_contacts = Counter()
    for (page, _locus), rows in by_locus.items():
        rows.sort(key=lambda row: int(row["token_index"]))
        for left, right in zip(rows, rows[1:]):
            if left["eva"] in QUALITY_WORDS and right["eva"] in DEGREE_WORDS:
                pair = (left["eva"], right["eva"])
                degree_pairs[pair] += 1
                degree_pair_pages[pair].add(page)
                degree_candidate_contacts[pair] += int(page in candidate_pages)
    degree_rows = [
        {
            "quality_surface": quality,
            "degree_surface": degree,
            "occurrences": degree_pairs[(quality, degree)],
            "pages": len(degree_pair_pages[(quality, degree)]),
            "candidate_occurrences": degree_candidate_contacts[(quality, degree)],
        }
        for quality in QUALITY_WORDS
        for degree in DEGREE_WORDS
    ]
    write_tsv(
        ROOT / DEGREE_REL,
        degree_rows,
        (
            "quality_surface",
            "degree_surface",
            "occurrences",
            "pages",
            "candidate_occurrences",
        ),
    )

    marker_contacts: dict[str, list[dict[str, str]]] = {
        "OTAIIN_FAMILY": [row for row in all_tokens if "otaiin" in row["eva"]],
        "DAIIN_EXACT": [row for row in all_tokens if row["eva"] == "daiin"],
        "QOKOL_DAIIN_ADJACENT": [],
    }
    for (_page, _locus), rows in by_locus.items():
        rows.sort(key=lambda row: int(row["token_index"]))
        for left, right in zip(rows, rows[1:]):
            if left["eva"] in {"okol", "qokol"} and right["eva"] == "daiin":
                marker_contacts["QOKOL_DAIIN_ADJACENT"].append(left)
    marker_rows: list[dict[str, object]] = []
    for marker, rows in marker_contacts.items():
        pages = {row["page"] for row in rows}
        herbal_a = [
            row
            for row in rows
            if row["section"] == "H" and row["language"] == "A"
        ]
        marker_rows.append(
            {
                "marker": marker,
                "occurrences": len(rows),
                "pages": len(pages),
                "safe_page_rate": f"{len(pages) / len(allowed_pages):.6f}",
                "herbal_a_occurrences": len(herbal_a),
                "herbal_a_pages": len({row["page"] for row in herbal_a}),
            }
        )
    marked_pages = {
        row["page"]
        for marker in ("OTAIIN_FAMILY", "QOKOL_DAIIN_ADJACENT")
        for row in marker_contacts[marker]
    }
    unmarked_pages = allowed_pages - marked_pages
    herbal_a_pages = {
        row["page"]
        for row in all_tokens
        if row["section"] == "H" and row["language"] == "A"
    }
    marker_rows.append(
        {
            "marker": "NO_OTAIIN_OR_QOKOL_DAIIN_PAGE",
            "occurrences": len(unmarked_pages),
            "pages": len(unmarked_pages),
            "safe_page_rate": f"{len(unmarked_pages) / len(allowed_pages):.6f}",
            "herbal_a_occurrences": len(unmarked_pages & herbal_a_pages),
            "herbal_a_pages": len(unmarked_pages & herbal_a_pages),
        }
    )
    write_tsv(
        ROOT / MARKER_REL,
        marker_rows,
        (
            "marker",
            "occurrences",
            "pages",
            "safe_page_rate",
            "herbal_a_occurrences",
            "herbal_a_pages",
        ),
    )

    dictionary_rows = build_dictionary(candidates)
    write_tsv(
        ROOT / DICTIONARY_REL,
        dictionary_rows,
        (
            "layer",
            "surface",
            "composition_slot",
            "default_meaning_de",
            "status",
            "evidence",
            "caveat",
        ),
    )

    translation_rows: list[dict[str, object]] = []
    for candidate in candidates:
        if candidate["working_selection"] != "PREFERRED":
            continue
        plant = candidate["plant"]
        if plant == "Cerfolium":
            source_expected = (
                "Kerbel; eine bekannte Pflanze, häufig in der Küche verwendet."
            )
            property_source = "GDT621_MANFRED_OPENING"
            code_evidence = "NO_TEMPERAMENT_VALUE_IN_THE_READ_SOURCE_OPENING"
            target_span_reading = ""
            degree_reading = ""
            unmapped = (
                "Küchenverwendung und genaue Pflanzenidentität sind keinem "
                "Voynich-Textspan zugeordnet."
            )
            status = "VISUAL_LABEL_IDENTITY_HYPOTHESIS_ONLY"
        else:
            quality = QUALITY_DE[(candidate["thermal"], candidate["moisture"])]
            source_expected = (
                f"{GERMAN[plant]}; {quality}, Grad {candidate['shared_degree']}."
            )
            if plant == "Liquiritia":
                source_expected += " Verwendeter Teil: Wurzel."
            property_source = (
                "CLM667_BALSAMUM"
                if plant == "Balsamus"
                else "GDT621_MANFRED_OPENING"
            )
            block = block_by_candidate[candidate["candidate_id"]]
            alignment = alignment_by_candidate[candidate["candidate_id"]]
            code_evidence = str(block["evidence_sequence"])
            target_span_reading = (
                f"{alignment['quality_locus']} {alignment['quality_surface']} → "
                f"{candidate['expected_family']} → {quality}."
            )
            degree_reading = {
                "1": (
                    "Grad I ist im Zielspan nicht gelesen; unmarkiert ist nur "
                    "der lokale Durchsatz-Default dieser Seitenhypothese."
                ),
                "2": "otaiin-Familie → vorläufiger Grad-II-Kandidat.",
                "3": "(q)okol daiin → vorläufiger Grad-III-Kandidat.",
            }[candidate["shared_degree"]]
            unmapped = "Der Pflanzenname selbst ist nicht lexikalisch bestätigt."
            if plant == "Liquiritia":
                unmapped += " Die Quellenangabe Wurzel hat noch keinen Voynich-Span."
            status = "CONCRETE_TEMPERAMENT_PAGE_READING__NAME_HYPOTHESIS"
            block_support = (
                f"{block['locus_range']}: {candidate['expected_family']}="
                f"{block['expected_count']}, gleiche Temperatur/Gegenfeuchte="
                f"{block['same_thermal_opposite_moisture_count']}, "
                f"andere Temperatur/gleiche Feuchte="
                f"{block['opposite_thermal_same_moisture_count']}."
            )
        if plant == "Cerfolium":
            block_support = "NO_TEMPERAMENT_BLOCK"
        name_hypothesis = (
            f"{carrier_display(candidate)} → {GERMAN[plant]}? "
            "(provisorischer Ganznamen-Träger, nicht lexikalisch bestätigt)"
        )
        translation_rows.append(
            {
                "plant": plant,
                "folio": candidate["folio"],
                "name_carrier_default": candidate["name_carrier_default"],
                "carrier_basis": candidate["carrier_basis"],
                "name_hypothesis_de": name_hypothesis,
                "source_expected_content_de": source_expected,
                "voynich_span_reading_de": target_span_reading,
                "degree_reading_de": degree_reading,
                "block_support_de": block_support,
                "unmapped_source_content_de": unmapped,
                "property_source": property_source,
                "voynich_code_family": candidate["expected_family"],
                "voynich_code_evidence": code_evidence,
                "status": status,
            }
        )
    write_tsv(
        ROOT / TRANSLATION_REL,
        translation_rows,
        (
            "plant",
            "folio",
            "name_carrier_default",
            "carrier_basis",
            "name_hypothesis_de",
            "source_expected_content_de",
            "voynich_span_reading_de",
            "degree_reading_de",
            "block_support_de",
            "unmapped_source_content_de",
            "property_source",
            "voynich_code_family",
            "voynich_code_evidence",
            "status",
        ),
    )

    other_outputs = (
        SUMMARY_REL,
        OCCURRENCES_REL,
        EXACT_REL,
        MINIMAL_REL,
        DEGREE_REL,
        BLOCK_REL,
        ALIGNMENT_REL,
        ORIENTATION_REL,
        DECK_ORIENTATION_REL,
        MARKER_REL,
        ALT_REL,
        DICTIONARY_REL,
        TRANSLATION_REL,
    )
    result = {
        "schema": "GDT622_CLM667_TEMPERAMENT_CODEBOOK_RESULT_V1",
        "experiment_id": "GDT622",
        "status": "CONCRETE_COMPOSITIONAL_WORKING_TRANSLATION_V1",
        "historical_mechanism": {
            "grammar": "WHOLE_LEARNED_DRUG_NAME + (c|f) [degree]? (s|h) [degree]?",
            "confirmed_values": {
                "c": "HOT",
                "f": "COLD",
                "h": "MOIST",
                "s": "DRY",
                "pbar": "DEGREE_1",
            },
            "source_observations": len(source_rows),
            "source_provenance_rows": len(provenance_rows),
            "source_scans": sorted({int(row["scan"]) for row in source_rows}),
        },
        "voynich_working_model": {
            "grammar": "PAGE_RECORD_HYPOTHESIS: LEARNED_WHOLE_NAME_CANDIDATE plus distributed QUALITY and DEGREE fields; adjacency is not established",
            "working_values": {
                "k": "HOT",
                "t": "COLD",
                "ch": "MOIST",
                "sh": "DRY",
                "qo": "QUALITY_FIELD_WRAPPER",
            },
            "degree_family": ["dain", "daiin", "daiiin"],
            "plain_degree_family_order": "UNRESOLVED",
            "local_working_degree_defaults": {
                "I": "UNMARKED_ON_LIQUORICE_WINDOWS_ONLY",
                "II": "otaiin-family candidate",
                "III": "(q)okol + daiin candidate",
            },
            "alternate_quality_bundle": "(ch|sh)+(ol|or), AXIS_VALUES_UNRESOLVED",
        },
        "summary": {
            "safe_pages": len(allowed_pages),
            "gdt327_inventory_pages": len(inventory_pages),
            "explicit_candidate_pages_outside_gdt327": sorted(
                candidate_pages - inventory_pages
            ),
            "safe_tokens": len(all_tokens),
            "candidate_rows": len(candidates),
            "candidate_pages": len(candidate_pages),
            "candidate_family_occurrences": len(occurrence_rows),
            "candidate_page_readings": len(translation_rows),
            "concrete_temperament_page_readings": sum(
                bool(row["voynich_span_reading_de"]) for row in translation_rows
            ),
            "visual_label_hypotheses": sum(
                not bool(row["voynich_span_reading_de"]) for row in translation_rows
            ),
            "exact_form_counts": {
                form: {
                    "occurrences": exact_counts[form],
                    "pages": len(exact_pages[form]),
                    "herbal_a_occurrences": exact_group_counts[(form, "HERBAL_A")],
                    "herbal_a_pages": len(
                        exact_group_pages[(form, "HERBAL_A")]
                    ),
                }
                for form in EXACT_FORMS
            },
            "evidence_blocks": len(block_rows),
            "exact_minimal_pairs": len(minimal_rows),
            "exact_minimal_pairs_by_axis": dict(
                sorted(Counter(row["changed_axis"] for row in minimal_rows).items())
            ),
            "preferred_coded_blocks": sum(
                row["working_selection"] == "PREFERRED" for row in block_rows
            ),
            "preferred_degree_marker_matches": sum(
                int(row["degree_marker_match"])
                for row in block_rows
                if row["working_selection"] == "PREFERRED"
            ),
            "best_orientation": {
                key: orientation_rows[0][key]
                for key in (
                    "assignment_id",
                    "k",
                    "t",
                    "ch",
                    "sh",
                    "matched_occurrences",
                    "total_family_occurrences",
                    "positive_blocks",
                )
            },
            "comparison_decks": {
                deck_id: {
                    "proposed_orientation_count_rank": next(
                        int(row["count_rank_min"])
                        for row in deck_orientation_rows
                        if row["deck_id"] == deck_id
                        and row["assignment_id"]
                        == "KT_THERMAL__k_HOT__ch_MOIST"
                    ),
                    "proposed_orientation_binary_rank": next(
                        int(row["binary_rank_min"])
                        for row in deck_orientation_rows
                        if row["deck_id"] == deck_id
                        and row["assignment_id"]
                        == "KT_THERMAL__k_HOT__ch_MOIST"
                    ),
                    "degree_marker_matches": next(
                        int(row["degree_marker_matches"])
                        for row in deck_orientation_rows
                        if row["deck_id"] == deck_id
                    ),
                }
                for deck_id in comparison_decks
            },
            "marker_prevalence": {
                str(row["marker"]): {
                    "occurrences": int(row["occurrences"]),
                    "pages": int(row["pages"]),
                    "herbal_a_occurrences": int(row["herbal_a_occurrences"]),
                    "herbal_a_pages": int(row["herbal_a_pages"]),
                }
                for row in marker_rows
            },
            "quality_degree_pairs": sum(degree_pairs.values()),
        },
        "preferred_working_pages": {
            row["plant"]: {
                "folio": row["folio"],
                "name_carrier_default": row["name_carrier_default"],
            }
            for row in candidates
            if row["working_selection"] == "PREFERRED"
        },
        "guard": {
            **guard_stats,
            "manual_reading_forbidden_rows_skipped": manual_forbidden_skips,
            "f84": "FORBIDDEN_AND_REJECTED_BEFORE_ROW_PARSE",
            "f84r": "FORBIDDEN_AND_REJECTED_BEFORE_ROW_PARSE",
        },
        "claim_boundary": (
            "Clm 667 proves the historical whole-name plus compositional-code mechanism. "
            "The five Voynich page identities, name carriers, k/t and ch/sh values are "
            "concrete exploratory defaults that yield four page-local temperament readings and "
            "one visual label hypothesis; the headword-to-code attachment is not established. "
            "They are not fixed plaintext or a complete manuscript solution. Unmarked, otaiin, "
            "and (q)okol+daiin are only local degree defaults for I/II/III; the bare "
            "dain/daiin/daiiin family is not numerically ordered."
        ),
        "inputs": {
            str(path): sha256(ROOT / path)
            for path in (
                SOURCE_REL,
                PROVENANCE_REL,
                CANDIDATE_REL,
                TOKENS_REL,
                *MANUAL_RELS.values(),
                SAFE_REL,
                GDT621_REL,
                GDT621_FINAL_REL,
            )
        },
        "outputs": {str(path): sha256(ROOT / path) for path in other_outputs},
    }
    result["content_sha256"] = canonical_hash(result)
    (ROOT / RESULT_REL).write_bytes(canonical_bytes(result))
    print(
        json.dumps(
            {
                "status": result["status"],
                "historical_rows": len(source_rows),
                "candidate_readings": len(translation_rows),
                "quality_degree_pairs": sum(degree_pairs.values()),
                "sealed_rows_rejected": guard_stats["skipped_forbidden"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
