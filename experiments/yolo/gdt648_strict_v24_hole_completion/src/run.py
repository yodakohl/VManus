#!/usr/bin/env python3
"""Build GDT648: close seven strict V24 holes with concrete whole-word readings."""
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
BASE_REL = Path("experiments/yolo/gdt648_strict_v24_hole_completion")
ART = ROOT / BASE_REL / "artifacts"
G647 = Path("experiments/yolo/gdt647_quality_subdegree_family_migration")
G647_RUN = G647 / "src/run.py"
G647_ALLOW = G647 / "artifacts/PAGE_ALLOWLIST.tsv"
G647_COVERAGE = G647 / "artifacts/ALL_LINE_CONCRETE_COVERAGE_V24.tsv"
G647_COMPLETE = G647 / "artifacts/COMPLETE_PASSAGES_V24.tsv"
G647_ONE = G647 / "artifacts/ONE_UNKNOWN_PASSAGES_V24.tsv"
G647_NEW_ONE = G647 / "artifacts/NEWLY_EXPOSED_ONE_HOLE_LINES.tsv"
G647_GLOSSARY = G647 / "artifacts/V24_EXACT_TOKEN_GLOSSARY.tsv"
G647_DICTIONARY = G647 / "artifacts/WORKING_DICTIONARY_V24.tsv"
G647_RESULT = G647 / "artifacts/RESULT.json"
G647_REPORT = G647 / "REPORT.md"
G630_REPORT = Path("experiments/yolo/gdt630_outer_carrier_attachment/REPORT.md")
G636_REPORT = Path("experiments/yolo/gdt636_residual_four_head_semantics/REPORT.md")
G642_REPORT = Path("experiments/yolo/gdt642_exact_e_ol_or_carrier_completion/REPORT.md")
G645_REPORT = Path("experiments/yolo/gdt645_ranked_five_surface_completion/REPORT.md")

spec = importlib.util.spec_from_file_location("gdt647_builder_for_gdt648", ROOT / G647_RUN)
if spec is None or spec.loader is None:
    raise RuntimeError("cannot load GDT647 builder")
g647 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g647)
g637 = g647.g637
TOKENS_REL = g647.TOKENS_REL
CROSS_REL = g647.CROSS_REL
COVERAGE_FIELDS = g647.g646.COVERAGE_FIELDS
ONE_FIELDS = g647.g646.ONE_FIELDS

STATUS = "PASS_7_STRICT_WHOLE_SURFACES__213_POSITIONS__V25"
GENERIC_FILLER = re.compile(
    r"arbeitsgut|arbeitschritt|arbeitsschritt|arbeitsmittel|arbeitsstoff|"
    r"arbeitsobjekt|werkzeug|produkt weiter|f.hre .* aus|leite .* weiter",
    re.IGNORECASE,
)

CANDIDATE_SPECS = (
    {
        "surface": "otol", "source_locus": "f77v.2",
        "working_meaning_de": "kaltes Zubereitungsgut", "composition": "o+t+ol",
        "rival_de": "kaltes Material im Ansatzrahmen", "family": "OTOL_32_CARRIER_GRID",
        "decision_basis": "the complete frame by k/t by optional ch by ol/or grid fixes o preparation, t cold and ol material",
    },
    {
        "surface": "sheor", "source_locus": "f49r.5",
        "working_meaning_de": "feuchter Drogenteil", "composition": "sh+e+or",
        "rival_de": "feuchte Drogenportion", "family": "E_OL_OR_QUALITY_GRID",
        "decision_basis": "cheor is dry drug part, sheol is moist material, and the full e+ol/or quality grid predicts sh+e+or without an unattested heor stem",
    },
    {
        "surface": "keol", "source_locus": "f56r.19",
        "working_meaning_de": "heißer Drogenstoff", "composition": "k+e+ol",
        "rival_de": "heiße E-Materialform", "family": "E_OL_OR_QUALITY_GRID",
        "decision_basis": "the observed k/t/ch/sh by e by ol/or grid maps k to hot and ol to material, parallel to accepted cheol and sheol",
    },
    {
        "surface": "odaiin", "source_locus": "f95v1.5",
        "working_meaning_de": "Zubereitungsdosis III", "composition": "o+d+(a+iin)",
        "rival_de": "Zubereitungscharge III", "family": "ODAIIN_DOSAGE_LADDER",
        "decision_basis": "o marks preparation, d the dose/result field, and a+iin the third value; p/s/r/l+odaiin already preserve the same body",
    },
    {
        "surface": "cholkaiin", "source_locus": "f106v.36",
        "working_meaning_de": "Trockengut, heiß im dritten Grad", "composition": "chol+(k+a+iin)",
        "rival_de": "heißes Trockengut, Menge III", "family": "CHOL_KAIIN_FUSION",
        "decision_basis": "both chol and kaiin already have concrete V24 values; independent chol kaiin spans and a reader split bridge the fused exact whole",
    },
    {
        "surface": "lkar", "source_locus": "f106r.35",
        "working_meaning_de": "heiße Holzfraktion I", "composition": "l+(k+ar)",
        "rival_de": "heißes Drogenholz", "family": "L_QUALITY_FRACTION_GRID",
        "decision_basis": "l is the established drug-wood head, the ar/air quality lattice reads kar as hot fraction I, and an l kar boundary bridge exists",
    },
    {
        "surface": "lsheey", "source_locus": "f77r.19",
        "working_meaning_de": "eingeweichtes Drogenholz, Form II", "composition": "l+(sh+ee+y)",
        "rival_de": "feuchtes Drogenholz, Form II", "family": "MATERIAL_QUALITY_FORM_GRID",
        "decision_basis": "the exact l material head combines with the observed sh+eey moist-form-II body; GDT647 degree-end semantics are not exported to material heads",
    },
)

SMOOTHED_SOURCE_LINES = {
    "f77v.2": "Kaltes Zubereitungsgut; feucht in der Gradmitte, abgeschlossen.",
    "f49r.5": "Pflanzenteil; feuchter Drogenteil; trocken in der Gradmitte; kalt am Gradende; kalt im ersten Grad.",
    "f56r.19": "Kalt-trockener Ansatz in der Gradmitte; heißer Drogenstoff, Grad III.",
    "f95v1.5": "Ansatz aus kaltem Rohstoff, Form I; feucht in der Gradmitte, abgeschlossen; Zubereitungsdosis III; trocken in der Gradmitte.",
    "f106v.36": "Saatgut; feucht und abgeschlossen am Gradende; heiß im dritten Grad; Trockengut, heiß im dritten Grad.",
    "f106r.35": "Heißer Ansatz, Grad III; heiß-trockene Zubereitung; heiße Holzfraktion I; trocken am Gradanfang, abgeschlossen; getrocknetes Drogenholz.",
    "f77r.19": "Heiß und abgeschlossen am Gradende; trockenes Drogenholz; eingeweichtes Drogenholz, Form II; heiße Portion und Holzcharge III.",
}

COMPONENT_ROWS = (
    ("otol", "o", "Ansatz/Zubereitung", G630_REPORT, "PREPARATION_FRAME"),
    ("otol", "t", "kalt", G630_REPORT, "COLD_QUALITY"),
    ("otol", "ol", "Gut/Material", G630_REPORT, "MATERIAL_CARRIER"),
    ("sheor", "sh", "feucht", G642_REPORT, "MOIST_QUALITY"),
    ("sheor", "e", "attributive Verbindung; nur gebunden", G642_REPORT, "BOUND_ATTRIBUTIVE_LINK"),
    ("sheor", "or", "Teil", G642_REPORT, "PART_CARRIER"),
    ("keol", "k", "heiß", G642_REPORT, "HOT_QUALITY"),
    ("keol", "e", "attributive Verbindung; nur gebunden", G642_REPORT, "BOUND_ATTRIBUTIVE_LINK"),
    ("keol", "ol", "Stoff/Material", G642_REPORT, "MATERIAL_CARRIER"),
    ("odaiin", "o", "Zubereitung", G636_REPORT, "PREPARATION_HEAD"),
    ("odaiin", "d", "Dosis-/Ergebnisfeld; nur hier gebunden", G636_REPORT, "BOUND_DOSE_FIELD"),
    ("odaiin", "a+iin", "Wert III", G636_REPORT, "BOUND_VALUE_III"),
    ("cholkaiin", "chol", "Trockengut", G630_REPORT, "DRY_MATERIAL_WHOLE"),
    ("cholkaiin", "k+a+iin", "heiß im dritten Grad", G647_REPORT, "HOT_DEGREE_III_WHOLE"),
    ("lkar", "l", "Drogenholz", G636_REPORT, "WOOD_MATERIAL_HEAD"),
    ("lkar", "k+ar", "heiße Fraktion I; nur gebunden", G645_REPORT, "BOUND_HOT_FRACTION_I"),
    ("lsheey", "l", "Drogenholz", G636_REPORT, "WOOD_MATERIAL_HEAD"),
    ("lsheey", "sh+ee+y", "Feucht-/Einweichform II; nur gebunden", G636_REPORT, "BOUND_MOIST_FORM_II"),
)

BRIDGES = (
    ("cholkaiin", "chol", "kaiin"),
    ("lkar", "l", "kar"),
)

NON_TARGET_DECISIONS = {
    "okool": ("HOLD_SEPARATE_AUDIT", "o+k+o+ol", "kaltes/heißes Gut mit zusätzlichem O-Feld", "Das zweite O hat noch keinen kalibrierten Kontrast."),
    "losaiin": ("HOLD_SEPARATE_AUDIT", "l+osaiin | lo+saiin", "Holzzubereitung oder Holz-Saat-Menge", "Singleton mit zwei gleich sichtbaren Zerlegungen."),
    "chdaly": ("HOLD_SEPARATE_AUDIT", "ch+d+al+y", "trockene Rohstoffform", "D, AL und Y sind in dieser Reihenfolge noch nicht gemeinsam kalibriert."),
    "octhdy": ("HOLD_SEPARATE_AUDIT", "o+cth+d+y", "fertig aufbereiteter CTH-Ansatz", "Nur zwei Belege; außerhalb Herbal darf CTH nicht vorschnell Blatt/Kraut heißen."),
    "dy": ("REJECT_CURRENT_ROUTE", "d+y", "resultatives Feld ohne sichtbaren Besitzer", "Ein nacktes Hochfrequenzfeld liefert keinen Stoff und würde gebundene DY-Werte globalisieren."),
    "ykeody": ("REJECT_CURRENT_ROUTE", "y+k+e+o+d+y", "offen", "Initiales Y ist nicht lizenziert; eine kurze Glosse würde K/E/O/D löschen."),
    "cheokeey": ("HOLD_SEPARATE_AUDIT", "ch+e+o+k+ee+y", "Trockenansatz, heiß, E-Länge II", "Reihenfolge gehört nicht zur migrierten Qualitätsfamilie und darf nicht umgestellt werden."),
    "ykeey": ("REJECT_CURRENT_ROUTE", "y+k+ee+y", "initiale-Y-Leiter offen", "Rekurrent, aber initiales Y besitzt noch keinen stabilen Sachwert."),
    "checkhy": ("REJECT_CURRENT_ROUTE", "ch+e+ckh+y", "offen", "CKH bleibt opak und darf nicht als CTH oder CH umgedeutet werden."),
    "soty": ("HOLD_SEPARATE_AUDIT", "s+o+t+y", "kalte Saatzubereitungs-Grundform", "Konkrete Singleton-Idee ohne wiederholte p/s/r/l-Restfamilie."),
    "keeey": ("HOLD_SEPARATE_AUDIT", "k+eee+y", "heiße EEE-Stufe", "EEE ist eine eigene Leiter und nicht die migrierte Y/EY/EEY-Achse."),
    "chokey": ("HOLD_SEPARATE_AUDIT", "ch+o+k+e+y", "heiß-trockene Zubereitungsform", "Umgestellte CH-O-K-Reihe braucht einen eigenen Formaudit."),
    "olkeeey": ("HOLD_SEPARATE_AUDIT", "ol+k+eee+y", "heißes Gut mit EEE-Stufe", "Sowohl OL-Besitz als auch EEE-Bedeutung sind offen."),
    "dchodaiin": ("HOLD_SEPARATE_AUDIT", "d+ch+o+d+a+iin", "dosierter Trockenansatz, Dosis III", "Das führende D-Feld und das innere chodaiin sind nicht separat registriert."),
    "sheckhy": ("REJECT_CURRENT_ROUTE", "sh+e+ckh+y", "offen", "SH darf nicht als S-Samenkopf zerlegt werden; CKH bleibt opak."),
    "olsaly": ("REJECT_CURRENT_ROUTE", "ol+s+al+y | o+l+saly", "offen", "Internes S erbt keine tokeninitiale Samenfunktion; beide Parses sind unkalibriert."),
    "qolchey": ("HOLD_SEPARATE_AUDIT", "qo+l+ch+e+y | q+ol+chey", "Drogenholz im QO-Rahmen, Trockenform I", "Nichtinitiales L und Q/OL-Scope müssen zuerst getrennt werden."),
    "skar": ("HOLD_SEPARATE_AUDIT", "s+k+ar", "heiße Samenfraktion I", "Vorhersage aus lkar, aber nur ein Beleg."),
    "shedal": ("HOLD_SEPARATE_AUDIT", "sh+e+d+al", "angefeuchteter Rohstoff", "SH ist kein S-Samenkopf; D+AL braucht einen eigenen Audit."),
}

OUTPUT_NAMES = (
    "PAGE_ALLOWLIST.tsv", "TARGET_DECISION_DECK.tsv", "STRICT_FRONTIER_ADJUDICATION.tsv", "FAMILY_EVIDENCE_ATLAS.tsv",
    "COMPONENT_BINDING_AUDIT.tsv", "FUSION_BRIDGE_AUDIT.tsv",
    "ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv", "READER_VARIANT_AUDIT.tsv",
    "SEQUENTIAL_DECISION_LEDGER.tsv", "ROUND_COVERAGE_COUNTS.tsv",
    "ACCEPTED_WHOLE_SURFACE_DEFAULTS.tsv", "SOURCE_PASSAGE_REALITY_CHECK.tsv",
    "NEWLY_COMPLETED_LINES.tsv", "NEWLY_EXPOSED_ONE_HOLE_LINES.tsv",
    "V25_EXACT_TOKEN_GLOSSARY.tsv", "ALL_LINE_CONCRETE_COVERAGE_V25.tsv",
    "COMPLETE_PASSAGES_V25.tsv", "ONE_UNKNOWN_PASSAGES_V25.tsv",
    "WORKING_DICTIONARY_V25.tsv",
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


def pair_count(line: str, left: str, right: str) -> int:
    tokens = line.split()
    return sum(tokens[index:index + 2] == [left, right] for index in range(len(tokens) - 1))


def dictionary_row(spec_row: dict[str, str], round_number: int, occurrences: int, exact_count: int) -> dict[str, object]:
    return {
        "entry": f"{spec_row['surface']}@GDT648_EXACT_WHOLE",
        "kind": "EXACT_ZL3B_WHOLE_STRICT_V24_COMPLETION",
        "working_meaning_de": spec_row["working_meaning_de"],
        "composition": spec_row["composition"],
        "context_rule": (
            f"exact complete surface only; {occurrences} audited occurrences; {exact_count} all-reader exact; "
            "components remain whole-bound; no substring, absent-cell or unrelated-family transfer"
        ),
        "status": f"NEW_V25_ACCEPTED_ROUND_{round_number:02d}",
    }


def family_forms() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for stage, ending in enumerate(("an", "ain", "aiin", "aiiin"), 1):
        roman = ("I", "II", "III", "IV")[stage - 1]
        rows.append({"family": "ODAIIN_DOSAGE_LADDER", "surface": f"od{ending}",
                     "composition": f"o+d+({ending})", "predicted_reading_de": f"Zubereitungsdosis {roman}"})
    for head, noun in (("p", "Pulver"), ("s", "Saatgut"), ("r", "Wurzel"), ("l", "Drogenholz")):
        rows.append({"family": "ODAIIN_DOSAGE_LADDER", "surface": f"{head}odaiin",
                     "composition": f"{head}+(o+d+(a+iin))", "predicted_reading_de": f"{noun}: Zubereitungsdosis III"})

    for frame in ("", "o", "qo", "y"):
        for thermal in ("k", "t"):
            for dry in ("", "ch"):
                for carrier in ("ol", "or"):
                    quality = ("heiß" if thermal == "k" else "kalt") + ("-trocken" if dry else "")
                    noun = "Drogenstoff" if carrier == "ol" else "Drogenteil"
                    frame_text = {"": "", "o": " im Ansatz", "qo": " in der Zubereitung", "y": " dieser Droge"}[frame]
                    rows.append({"family": "OTOL_32_CARRIER_GRID", "surface": f"{frame}{thermal}{dry}{carrier}",
                                 "composition": f"{frame + '+' if frame else ''}{thermal}{'+' + dry if dry else ''}+{carrier}",
                                 "predicted_reading_de": f"{quality}er {noun}{frame_text}"})

    quality_names = {"k": "heiß", "t": "kalt", "ch": "trocken", "sh": "feucht"}
    for quality, quality_de in quality_names.items():
        for carrier, noun in (("ol", "Drogenstoff"), ("or", "Drogenteil")):
            for linker in ("", "e"):
                rows.append({"family": "E_OL_OR_QUALITY_GRID", "surface": f"{quality}{linker}{carrier}",
                             "composition": f"{quality}{'+' + linker if linker else ''}+{carrier}",
                             "predicted_reading_de": f"{quality_de}er {noun}"})

    for stage, ending in enumerate(("an", "ain", "aiin", "aiiin"), 1):
        roman = ("I", "II", "III", "IV")[stage - 1]
        rows.append({"family": "CHOL_KAIIN_FUSION", "surface": f"cholk{ending}",
                     "composition": f"chol+(k+{ending})", "predicted_reading_de": f"Trockengut, heiß im Grad {roman}"})
    for surface, parse, reading in (
        ("chol", "ch+ol", "Trockengut"), ("kaiin", "k+(a+iin)", "heiß im Grad III"),
    ):
        rows.append({"family": "CHOL_KAIIN_FUSION", "surface": surface,
                     "composition": parse, "predicted_reading_de": reading})

    for quality, quality_de in quality_names.items():
        for carrier, roman in (("ar", "I"), ("air", "II"), ("aiir", "III")):
            rows.append({"family": "L_QUALITY_FRACTION_GRID", "surface": f"{quality}{carrier}",
                         "composition": f"{quality}+{carrier}", "predicted_reading_de": f"{quality_de}e Fraktion {roman}"})
            rows.append({"family": "L_QUALITY_FRACTION_GRID", "surface": f"l{quality}{carrier}",
                         "composition": f"l+({quality}+{carrier})", "predicted_reading_de": f"{quality_de}e Holzfraktion {roman}"})

    form_endings = {"y": "Grundform", "ey": "Form I", "eey": "Form II"}
    material_names = {"p": "Pulver", "s": "Saatgut", "r": "Wurzel", "l": "Drogenholz"}
    for material, material_de in material_names.items():
        for quality, quality_de in (("ch", "trocken"), ("sh", "feucht/eingeweicht")):
            for ending, ending_de in form_endings.items():
                rows.append({"family": "MATERIAL_QUALITY_FORM_GRID", "surface": f"{material}{quality}{ending}",
                             "composition": f"{material}+({quality}+{ending})",
                             "predicted_reading_de": f"{material_de}, {quality_de}, {ending_de}"})
    unique: dict[tuple[str, str], dict[str, str]] = {}
    for row in rows:
        unique[row["family"], row["surface"]] = row
    return list(unique.values())


def build(output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    pages = {row["page"] for row in read_tsv(ROOT / G647_ALLOW)}
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

    base_dictionary = [dict(row) for row in read_tsv(ROOT / G647_DICTIONARY)]
    base_gloss_rows = read_tsv(ROOT / G647_GLOSSARY)
    base_glossary = {row["surface"]: dict(row) for row in base_gloss_rows}
    base_coverage = read_tsv(ROOT / G647_COVERAGE)
    base_complete = read_tsv(ROOT / G647_COMPLETE)
    base_one = read_tsv(ROOT / G647_ONE)
    source_frontier = read_tsv(ROOT / G647_NEW_ONE)
    if (len(base_dictionary), len(base_glossary), len(base_coverage), len(base_complete), len(base_one)) != (410, 347, 4128, 77, 152):
        raise RuntimeError("GDT647 V24 base counts changed")
    replay_coverage, replay_one, _, replay_complete = g637.build_line_coverage(
        by_line, base_glossary, exact, boundary, cross_by_locus,
    )
    if (string_rows(replay_coverage) != string_rows(base_coverage)
            or string_rows(replay_complete) != string_rows(base_complete)
            or string_rows(replay_one) != string_rows(base_one)):
        raise RuntimeError("GDT647 V24 editions do not replay")
    base_metrics = metrics(replay_coverage, replay_one, replay_complete, base_glossary)
    expected_base = {
        "physical_lines": 4128, "known_token_positions": 13782,
        "unknown_token_positions": 18557, "complete_multi_token_lines": 77,
        "strict_complete_lines": 42, "one_unknown_lines": 152,
        "strict_one_unknown_lines": 48, "exact_glossary_surfaces": 347,
    }
    if base_metrics != expected_base:
        raise RuntimeError(f"GDT647 V24 metrics changed: {base_metrics!r}")
    targets = {str(row["surface"]) for row in CANDIDATE_SPECS}
    source_pairs = {(row["unknown_surface"], row["locus"]): row for row in source_frontier}
    for raw_spec in CANDIDATE_SPECS:
        pair = (str(raw_spec["surface"]), str(raw_spec["source_locus"]))
        if pair not in source_pairs or int(source_pairs[pair]["strict_eligible"]) != 1:
            raise RuntimeError(f"strict GDT647 source frontier changed: {pair}")

    strict_frontier = [row for row in source_frontier if int(row["strict_eligible"]) == 1]
    strict_surfaces = {row["unknown_surface"] for row in strict_frontier}
    if len(strict_frontier) != 26 or strict_surfaces != targets | set(NON_TARGET_DECISIONS):
        raise RuntimeError("26-surface strict GDT647 frontier changed")

    token_counts = Counter(str(row["eva"]) for row in token_rows)
    family_rows: list[dict[str, object]] = []
    for family_row in family_forms():
        surface = family_row["surface"]
        members = [row for row in token_rows if row["eva"] == surface]
        family_rows.append({
            **family_row, "zl3b_occurrences": len(members), "pages": len({row["page"] for row in members}),
            "reader_exact_occurrences": sum(exact[row["locus"], int(row["token_index"])] for row in members),
            "split_normalized_occurrences": sum(boundary[row["locus"], int(row["token_index"])] for row in members),
            "surface_status": "TARGET" if surface in targets else "OBSERVED" if members else "ABSENT_HOLD",
        })
    family_rows.sort(key=lambda row: (str(row["family"]), str(row["surface"])))

    frontier_rows: list[dict[str, object]] = []
    target_by_surface = {str(row["surface"]): row for row in CANDIDATE_SPECS}
    frontier_by_surface: dict[str, list[dict[str, str]]] = {}
    for row in strict_frontier:
        frontier_by_surface.setdefault(row["unknown_surface"], []).append(row)
    for surface in sorted(strict_surfaces):
        members = [row for row in token_rows if row["eva"] == surface]
        if surface in target_by_surface:
            target = target_by_surface[surface]
            decision, parse = "ACCEPT_V25", str(target["composition"])
            direction, reason = str(target["working_meaning_de"]), str(target["decision_basis"])
        else:
            decision, parse, direction, reason = NON_TARGET_DECISIONS[surface]
        frontier_rows.append({
            "surface": surface, "strict_source_loci": "|".join(sorted(row["locus"] for row in frontier_by_surface[surface])),
            "zl3b_occurrences": len(members), "pages": len({row["page"] for row in members}),
            "reader_exact_occurrences": sum(exact[row["locus"], int(row["token_index"])] for row in members),
            "split_normalized_occurrences": sum(boundary[row["locus"], int(row["token_index"])] for row in members),
            "parse": parse, "working_direction_de": direction, "decision": decision, "reason": reason,
        })

    component_rows = [
        {"component_id": f"G648-B{index:02d}", "surface": surface, "segment": segment,
         "working_value_de": value, "evidence_path": str(path), "evidence_kind": kind,
         "licensed_use": f"inside exact {surface} only"}
        for index, (surface, segment, value, path, kind) in enumerate(COMPONENT_ROWS, 1)
    ]
    bridge_rows: list[dict[str, object]] = []
    for surface, left, right in BRIDGES:
        counts = {reader: sum(pair_count(row[field], left, right) for row in cross_rows)
                  for reader, field in (("zl3b", "zl3b_clean"), ("it2a", "it2a_clean"), ("rf1b", "rf1b_clean"))}
        loci = sorted({row["locus"] for row in cross_rows if pair_count(row["zl3b_clean"], left, right)})
        fused_members = [row for row in token_rows if row["eva"] == surface]
        bridge_rows.append({
            "surface": surface, "left": left, "right": right, "zl3b_separated_pairs": counts["zl3b"],
            "it2a_separated_pairs": counts["it2a"], "rf1b_separated_pairs": counts["rf1b"],
            "zl3b_pair_loci": "|".join(loci) or "NONE", "fused_occurrences": len(fused_members),
            "decision": "SUPPORTS_BOUNDARY_ALTERNATION" if min(counts.values()) else "ONE_READER_OR_ZL3B_BRIDGE_ONLY",
        })

    glossary = {key: dict(value) for key, value in base_glossary.items()}
    coverage, one_unknown, complete = replay_coverage, replay_one, replay_complete
    base_complete_loci = {row["locus"] for row in base_complete}
    base_one_loci = {row["locus"] for row in base_one}
    accepted_dictionary_rows: list[dict[str, object]] = []
    target_deck: list[dict[str, object]] = []
    audit_rows: list[dict[str, object]] = []
    variant_rows: list[dict[str, object]] = []
    ledger_rows: list[dict[str, object]] = []
    round_rows: list[dict[str, object]] = [{
        "round": 0, "surface": "BASE_V24", "decision": "BASE", "dictionary_entries": len(base_dictionary),
        "dictionary_sha256": canonical_hash(base_dictionary), **base_metrics,
    }]
    seen_one_loci = set(base_one_loci)
    newly_exposed_rows: list[dict[str, object]] = []

    for round_number, raw_spec in enumerate(CANDIDATE_SPECS, 1):
        spec_row = {key: str(value) for key, value in raw_spec.items()}
        surface = spec_row["surface"]
        if surface in glossary or GENERIC_FILLER.search(spec_row["working_meaning_de"]):
            raise RuntimeError(f"invalid target: {surface}")
        members = [row for row in token_rows if row["eva"] == surface]
        if not members or len(members) != token_counts[surface]:
            raise RuntimeError(f"target occurrence drift: {surface}")
        exact_count = sum(exact[row["locus"], int(row["token_index"])] for row in members)
        split_count = sum(boundary[row["locus"], int(row["token_index"])] for row in members)
        if exact_count == 0:
            raise RuntimeError(f"target lacks all-reader exact anchor: {surface}")

        pre_coverage, pre_one, pre_complete = coverage, one_unknown, complete
        pre_by_locus = {row["locus"]: row for row in pre_coverage}
        pre_complete_loci = {row["locus"] for row in pre_complete}
        pre_one_by_locus = {row["locus"]: row for row in pre_one}
        source = pre_one_by_locus.get(spec_row["source_locus"])
        if source is None or source["unknown_surface"] != surface or int(source["strict_eligible"]) != 1:
            raise RuntimeError(f"source line no longer strict one-hole: {surface}")

        g637.set_gloss(
            glossary, surface, spec_row["working_meaning_de"], "GDT648:STRICT_WHOLE_COMPLETION",
            "EXACT_WHOLE_COMPOSITIONAL_COMPLETION", "KNOWN_EXACT_WHOLE", 140,
        )
        coverage, one_unknown, _, complete = g637.build_line_coverage(
            by_line, glossary, exact, boundary, cross_by_locus,
        )
        post_by_locus = {row["locus"]: row for row in coverage}
        new_complete_loci = sorted({row["locus"] for row in complete} - pre_complete_loci)
        if spec_row["source_locus"] not in new_complete_loci:
            raise RuntimeError(f"target failed to close strict source: {surface}")

        verdicts: Counter[str] = Counter()
        round_audits: list[dict[str, object]] = []
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
            if support == "ALL_THREE_EXACT" and clean_other >= 2:
                verdict = "CLEAN_CONTEXT_COMPATIBLE"
            elif support == "ALL_THREE_EXACT":
                verdict = "OPAQUE_OR_SHORT_CONTEXT"
            elif support == "ALL_THREE_SPLIT_NORMALIZED":
                verdict = "READER_SPLIT_NORMALIZED"
            else:
                verdict = "READER_VARIANT_WARNING"
            verdicts[verdict] += 1
            audit_row = {
                "audit_id": f"G648-A{round_number:02d}-{occurrence:03d}", "round": round_number,
                "surface": surface, "page": member["page"], "locus": locus, "section": member["section"],
                "language": member["language"], "hand": member["hand"], "token_ordinal": ordinal,
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
            }
            round_audits.append(audit_row)
            if support != "ALL_THREE_EXACT":
                variant_rows.append({
                    "surface": surface, "page": member["page"], "locus": locus,
                    "zl3b_line": before["zl3b_line"], "it2a_line": cross_by_locus[locus]["it2a_clean"],
                    "rf1b_line": cross_by_locus[locus]["rf1b_clean"], "reader_support": support,
                    "working_meaning_de": spec_row["working_meaning_de"],
                    "decision": "RETAIN_EXACT_ZL3B_WITH_READER_WARNING",
                })
        audit_rows.extend(round_audits)

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
            "round": round_number, "surface": surface, "decision": "ACCEPT",
            "decision_reason": spec_row["decision_basis"], "pre_dictionary_entries": len(post_dictionary) - 1,
            "post_dictionary_entries": len(post_dictionary), "occurrences": len(members),
            "all_reader_exact": exact_count, "split_normalized": split_count,
            "reader_variant": len(members) - split_count,
            "clean_context_compatible": verdicts["CLEAN_CONTEXT_COMPATIBLE"],
            "opaque_or_short_context": verdicts["OPAQUE_OR_SHORT_CONTEXT"],
            "hard_collisions": 0, "complete_before": len(pre_complete), "complete_after": len(complete),
            "strict_complete_after": sum(int(row["strict_complete"]) for row in complete),
            "one_unknown_before": len(pre_one), "one_unknown_after": len(one_unknown),
            "new_complete_loci": "|".join(new_complete_loci),
        })
        target_deck.append({
            "candidate_id": f"G648-C{round_number:02d}", "candidate_order": round_number,
            "surface": surface, "source_locus": spec_row["source_locus"], "family": spec_row["family"],
            "working_meaning_de": spec_row["working_meaning_de"], "composition": spec_row["composition"],
            "rival_de": spec_row["rival_de"], "occurrences": len(members),
            "pages": len({row["page"] for row in members}), "reader_exact_occurrences": exact_count,
            "split_normalized_occurrences": split_count, "decision": "ACCEPT",
            "decision_basis": spec_row["decision_basis"],
        })
        round_rows.append({
            "round": round_number, "surface": surface, "decision": "ACCEPT",
            "dictionary_entries": len(post_dictionary), "dictionary_sha256": canonical_hash(post_dictionary),
            **metrics(coverage, one_unknown, complete, glossary),
        })

    final_dictionary = [*base_dictionary, *accepted_dictionary_rows]
    final_coverage, final_one, _, final_complete = g637.build_line_coverage(
        by_line, glossary, exact, boundary, cross_by_locus,
    )
    final_by_locus = {row["locus"]: row for row in final_coverage}
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
    } for row in accepted_dictionary_rows]

    reality_rows: list[dict[str, object]] = []
    for order, spec_row in enumerate(CANDIDATE_SPECS, 1):
        locus = str(spec_row["source_locus"])
        row = final_by_locus[locus]
        reality_rows.append({
            "candidate_id": f"G648-C{order:02d}", "surface": spec_row["surface"], "page": row["page"],
            "locus": locus, "strict_complete": final_complete_by_locus[locus]["strict_complete"],
            "zl3b_line": row["zl3b_line"], "tokenwise_translation_de": row["token_glosses_de"],
            "smoothed_working_reading_de": SMOOTHED_SOURCE_LINES[locus],
            "assessment": "CONCRETE_AND_COMPOSITIONAL", "rival_de": spec_row["rival_de"],
        })

    new_complete_rows = []
    for locus in sorted(set(final_complete_by_locus) - base_complete_loci):
        row = final_by_locus[locus]
        enabled = list(dict.fromkeys(token["eva"] for token in by_line[locus] if token["eva"] in targets))
        new_complete_rows.append({
            "page": row["page"], "locus": locus, "strict_complete": final_complete_by_locus[locus]["strict_complete"],
            "enabled_by_surfaces": "|".join(enabled), "zl3b_line": row["zl3b_line"],
            "literal_v25_de": "; ".join(split_pipe(row["token_glosses_de"])),
            "smoothed_source_reading_de": SMOOTHED_SOURCE_LINES.get(locus, "NOT_CURATED_SOURCE_LINE"),
        })

    write_tsv(output_dir / "PAGE_ALLOWLIST.tsv", [{"page": page} for page in sorted(pages)], ("page",))
    write_tsv(output_dir / "TARGET_DECISION_DECK.tsv", target_deck, (
        "candidate_id", "candidate_order", "surface", "source_locus", "family", "working_meaning_de",
        "composition", "rival_de", "occurrences", "pages", "reader_exact_occurrences",
        "split_normalized_occurrences", "decision", "decision_basis",
    ))
    write_tsv(output_dir / "STRICT_FRONTIER_ADJUDICATION.tsv", frontier_rows, (
        "surface", "strict_source_loci", "zl3b_occurrences", "pages", "reader_exact_occurrences",
        "split_normalized_occurrences", "parse", "working_direction_de", "decision", "reason",
    ))
    write_tsv(output_dir / "FAMILY_EVIDENCE_ATLAS.tsv", family_rows, (
        "family", "surface", "composition", "predicted_reading_de", "zl3b_occurrences", "pages",
        "reader_exact_occurrences", "split_normalized_occurrences", "surface_status",
    ))
    write_tsv(output_dir / "COMPONENT_BINDING_AUDIT.tsv", component_rows, (
        "component_id", "surface", "segment", "working_value_de", "evidence_path", "evidence_kind", "licensed_use",
    ))
    write_tsv(output_dir / "FUSION_BRIDGE_AUDIT.tsv", bridge_rows, (
        "surface", "left", "right", "zl3b_separated_pairs", "it2a_separated_pairs", "rf1b_separated_pairs",
        "zl3b_pair_loci", "fused_occurrences", "decision",
    ))
    write_tsv(output_dir / "ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv", audit_rows, (
        "audit_id", "round", "surface", "page", "locus", "section", "language", "hand", "token_ordinal",
        "line_position", "previous", "following", "zl3b_line", "it2a_line", "rf1b_line", "reader_support",
        "reader_exact", "split_normalized", "before_gloss_de", "after_gloss_de", "known_other_tokens",
        "clean_known_other_tokens", "local_before_de", "local_after_de", "hard_collision", "verdict",
    ))
    write_tsv(output_dir / "READER_VARIANT_AUDIT.tsv", variant_rows, (
        "surface", "page", "locus", "zl3b_line", "it2a_line", "rf1b_line", "reader_support",
        "working_meaning_de", "decision",
    ))
    write_tsv(output_dir / "SEQUENTIAL_DECISION_LEDGER.tsv", ledger_rows, (
        "round", "surface", "decision", "decision_reason", "pre_dictionary_entries", "post_dictionary_entries",
        "occurrences", "all_reader_exact", "split_normalized", "reader_variant", "clean_context_compatible",
        "opaque_or_short_context", "hard_collisions", "complete_before", "complete_after", "strict_complete_after",
        "one_unknown_before", "one_unknown_after", "new_complete_loci",
    ))
    write_tsv(output_dir / "ROUND_COVERAGE_COUNTS.tsv", round_rows, (
        "round", "surface", "decision", "dictionary_entries", "dictionary_sha256", "physical_lines",
        "known_token_positions", "unknown_token_positions", "complete_multi_token_lines", "strict_complete_lines",
        "one_unknown_lines", "strict_one_unknown_lines", "exact_glossary_surfaces",
    ))
    write_tsv(output_dir / "ACCEPTED_WHOLE_SURFACE_DEFAULTS.tsv", accepted_defaults, (
        "surface", "entry", "kind", "working_meaning_de", "composition", "context_rule", "status",
        "source_locus", "occurrences",
    ))
    write_tsv(output_dir / "SOURCE_PASSAGE_REALITY_CHECK.tsv", reality_rows, (
        "candidate_id", "surface", "page", "locus", "strict_complete", "zl3b_line", "tokenwise_translation_de",
        "smoothed_working_reading_de", "assessment", "rival_de",
    ))
    write_tsv(output_dir / "NEWLY_COMPLETED_LINES.tsv", new_complete_rows, (
        "page", "locus", "strict_complete", "enabled_by_surfaces", "zl3b_line", "literal_v25_de",
        "smoothed_source_reading_de",
    ))
    write_tsv(output_dir / "NEWLY_EXPOSED_ONE_HOLE_LINES.tsv", newly_exposed_rows, (
        "introduced_round", "enabled_by_surface", *ONE_FIELDS,
    ))
    write_tsv(output_dir / "V25_EXACT_TOKEN_GLOSSARY.tsv", final_gloss_rows, (
        "surface", "working_meaning_de", "source", "strength", "scope_state", "priority",
    ))
    write_tsv(output_dir / "ALL_LINE_CONCRETE_COVERAGE_V25.tsv", final_coverage, COVERAGE_FIELDS)
    write_tsv(output_dir / "COMPLETE_PASSAGES_V25.tsv", final_complete, (
        "rank", "strict_complete", *COVERAGE_FIELDS, "working_translation_de",
    ))
    write_tsv(output_dir / "ONE_UNKNOWN_PASSAGES_V25.tsv", final_one, ONE_FIELDS)
    write_tsv(output_dir / "WORKING_DICTIONARY_V25.tsv", final_dictionary, (
        "entry", "kind", "working_meaning_de", "composition", "context_rule", "status",
    ))

    output_paths = [output_dir / name for name in OUTPUT_NAMES]
    input_paths = (
        G647_RUN, G647_ALLOW, G647_COVERAGE, G647_COMPLETE, G647_ONE, G647_NEW_ONE,
        G647_GLOSSARY, G647_DICTIONARY, G647_RESULT, G647_REPORT,
        G630_REPORT, G636_REPORT, G642_REPORT, G645_REPORT, TOKENS_REL, CROSS_REL,
    )
    verdicts = Counter(row["verdict"] for row in audit_rows)
    family_counts = Counter(row["family"] for row in family_rows if int(row["zl3b_occurrences"]) > 0)
    result_core = {
        "schema": "GDT648_STRICT_V24_HOLE_COMPLETION_RESULT_V1",
        "experiment_id": "GDT648", "status": STATUS,
        "guard": {"f1r": "EXCLUDED", "f84": "FORBIDDEN", "f84r": "FORBIDDEN", "new_pages": 0,
                  "new_images": 0, "allowed_pages": len(pages), "token_query": token_stats, "cross_query": cross_stats},
        "target_run": {
            "candidates": len(target_deck), "accepted": len(target_deck), "held": 0,
            "accepted_surfaces": [row["surface"] for row in target_deck],
            "audited_occurrences": len(audit_rows), "all_reader_exact_occurrences": sum(int(row["reader_exact"]) for row in audit_rows),
            "split_normalized_occurrences": sum(int(row["split_normalized"]) for row in audit_rows),
            "reader_variant_warnings": sum(row["verdict"] == "READER_VARIANT_WARNING" for row in audit_rows),
            "hard_collisions": sum(int(row["hard_collision"]) for row in audit_rows),
            "verdicts": dict(sorted(verdicts.items())), "observed_family_cells": dict(sorted(family_counts.items())),
            "strict_frontier_decisions": dict(sorted(Counter(row["decision"] for row in frontier_rows).items())),
        },
        "coverage": {"base": base_metrics, "final": final_metrics,
                     "newly_completed_lines": len(new_complete_rows),
                     "newly_exposed_one_hole_lines": len(newly_exposed_rows)},
        "working_dictionary": {"v24_entries": len(base_dictionary), "v25_entries": len(final_dictionary),
                               "accepted_tail_entries": len(accepted_dictionary_rows),
                               "v24_prefix_sha256": canonical_hash(base_dictionary), "v25_sha256": canonical_hash(final_dictionary),
                               "v24_glossary_surfaces": len(base_glossary), "v25_glossary_surfaces": len(glossary)},
        "claim_boundary": (
            "GDT648 gives seven previously unknown exact ZL3b whole surfaces concrete, replaceable readings: "
            "otol=cold preparation material, sheor=moist drug part, keol=hot drug material, odaiin=preparation dose III, "
            "cholkaiin=dry material hot in degree III, lkar=hot wood fraction I, and lsheey=soaked drug wood form II. "
            "Each closes a pre-existing strict V24 one-hole line, has at least one all-reader exact anchor, and is audited at every allowed "
            "occurrence. Components remain bound to these complete surfaces and displayed comparison cells; no plaintext, phonetics, language, "
            "ingredient identity, absent cell, bare component or manuscript-wide suffix rule is asserted."
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
        f"GDT648 built: accepted={target['accepted']} audits={target['audited_occurrences']} "
        f"known={coverage['final']['known_token_positions']} complete={coverage['final']['complete_multi_token_lines']} "
        f"strict={coverage['final']['strict_complete_lines']} one_unknown={coverage['final']['one_unknown_lines']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
