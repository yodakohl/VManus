#!/usr/bin/env python3
"""Build GDT637: extend four minim ladders and rank near-readable lines."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
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
BASE_REL = Path("experiments/yolo/gdt637_ladder_completion_one_unknown_passages")
ART = ROOT / BASE_REL / "artifacts"
G636_BASE = Path("experiments/yolo/gdt636_residual_four_head_semantics")
G636_RUN_REL = G636_BASE / "src/run.py"
G636_ALLOW_REL = G636_BASE / "artifacts/PAGE_ALLOWLIST.tsv"
G636_DICT_REL = G636_BASE / "artifacts/WORKING_DICTIONARY_V13.tsv"
G636_DEFAULTS_REL = G636_BASE / "artifacts/RESIDUAL_BODY_DEFAULTS.tsv"
G636_RESULT_REL = G636_BASE / "artifacts/RESULT.json"

spec = importlib.util.spec_from_file_location("gdt636_builder", ROOT / G636_RUN_REL)
if spec is None or spec.loader is None:
    raise RuntimeError("cannot load GDT636 builder helpers")
g636 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g636)

TOKENS_REL = g636.TOKENS_REL
CROSS_REL = g636.CROSS_REL
HEAD_ORDER = ("p", "s", "r", "l")
HEAD_CLASS = {"p": "ENTRY", "s": "ENTRY", "r": "INGREDIENT", "l": "INGREDIENT"}
HEAD_NOUN = {
    "p": "Pulver", "s": "Samendroge", "r": "Wurzeldroge", "l": "Drogenholz",
}
TARGET_ORDER = ("aiir", "oiiin", "aim", "aiim")
TARGET_SPECS = {
    "aiir": {
        "components": "a+ii+R", "family": "PART_CLASS", "stage": "III",
        "body_value": "Teil-/Sortierklasse III", "rival": "Fraktions-/Qualitätsklasse III",
        "basis": "setzt ar/air mit genau einem zusätzlichen i-Minim fort",
    },
    "oiiin": {
        "components": "o+iiin", "family": "PREPARATION_FORM", "stage": "IV",
        "body_value": "Formklasse IV", "rival": "Zubereitungs-/Chargenklasse IV oder gelerntes Ganzwort",
        "basis": "setzt on/oin/oiin mit der vierten sichtbaren Minimstufe fort",
    },
    "aim": {
        "components": "a+i+m", "family": "QUANTITY_CLASS", "stage": "II",
        "body_value": "Mengenklasse II", "rival": "Charge-/Mischklasse II",
        "basis": "setzt am/aim/aiim fort; Abschlussfunktion bleibt strikt zeilenfinal",
    },
    "aiim": {
        "components": "a+ii+m", "family": "QUANTITY_CLASS", "stage": "III",
        "body_value": "Mengenklasse III", "rival": "Abschluss-/Charge-/Mischklasse III",
        "basis": "dritte sichtbare A-M-Stufe; Abschlussfunktion bleibt strikt zeilenfinal",
    },
}

# Concrete manual readings supplied by an independent passage pass.  They are
# proposals for the one-open-slot worksheet, not V14 dictionary promotions.
CURATED_UNKNOWN_DEFAULTS = {
    "qoky": ("heiß, Grundform", "qok quality head + terminal base y", "MEDIUM"),
    "otchol": ("kalt-trockenes Zubereitungsmaterial", "o frame + t cold + ch dry + ol material", "HIGH"),
    "keechy": ("heiß gebundene Trockenform II", "k hot + ee form II + ch-y dry base", "MEDIUM"),
    "chokshy": ("trocken angesetzte heiß-feuchte Grundform", "ch dry + o frame + k/sh quality pair + y base", "MEDIUM"),
    "cthoiin": ("Blatt-/Krautzubereitung, Form III", "cth plant-drug head + oiin form III", "HIGH"),
    "cthom": ("Blatt-/Krautansatz, Einheit/Maß I", "cth plant-drug head + o preparation + m unit I", "MEDIUM"),
    "qotchol": ("kalt-trockenes Material", "qo frame + t cold + ch dry + ol material", "HIGH"),
    "cthor": ("Blatt-/Krautportion", "cth plant-drug head + or portion", "HIGH"),
    "choiin": ("Trockenansatz, Form III", "ch dry + oiin preparation form III", "HIGH"),
    "dol": ("abgemessenes Material", "d value head + ol material", "MEDIUM"),
    "doiin": ("Dosis der Zubereitungsform III", "d dose/value head + oiin preparation form III", "MEDIUM"),
    "oaiir": ("Zubereitungs-Teilklasse III", "o preparation head + aiir part/sort class III", "HIGH"),
    "chotaiin": ("Trockenansatz: kalt, Grad III", "ch dry + o preparation + t-aIII cold grade", "HIGH"),
    "okeor": ("erhitzte Zubereitungsportion, Form I", "o preparation + k hot + e form I + or portion", "HIGH"),
    "qocheor": ("trockene Portion, Form I", "qo frame + ch dry + e form I + or portion", "HIGH"),
    "dair": ("abgemessene Fraktion II", "d measure head + air fraction stage II", "HIGH"),
    "kcho": ("heiß-trockener Ansatz", "GDT636 concrete f49r.12 span: k + ch + o", "HIGH"),
}

OPAQUE_UNKNOWN_SURFACES = {"cpholdy", "cheockhy", "chckhal", "okcholksh"}

OUTPUT_NAMES = (
    "PAGE_ALLOWLIST.tsv", "LADDER_16_HEAD_CELL_GRID.tsv", "LADDER_OCCURRENCE_CONTEXTS.tsv",
    "LADDER_CONTEXT_TRANSFER.tsv", "LADDER_BODY_CONTRASTS.tsv", "V14_EXACT_TOKEN_GLOSSARY.tsv",
    "ALL_LINE_CONCRETE_COVERAGE.tsv", "ONE_UNKNOWN_PASSAGE_RANKING.tsv",
    "STRICT_ONE_UNKNOWN_PASSAGES.tsv", "PROPOSED_UNKNOWN_DEFAULTS.tsv",
    "COMPLETE_PASSAGE_CANDIDATES.tsv",
    "WORKING_DICTIONARY_V14.tsv",
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


def target_gloss(head: str, body: str) -> str:
    if body == "aiir":
        return {
            "p": "Pulver: Teil-/Sortierklasse III", "s": "Samendroge: Teil-/Sortierklasse III",
            "r": "Wurzeldroge: Teil-/Sortierklasse III", "l": "Drogenholz: Teil-/Sortierklasse III",
        }[head]
    if body == "oiiin":
        return {
            "p": "Pulver: Formklasse IV", "s": "Samendroge: Formklasse IV",
            "r": "Wurzeldroge: Formklasse IV", "l": "Drogenholz: Formklasse IV",
        }[head]
    if body == "aim":
        return {
            "p": "Pulver: Mengenklasse II", "s": "Samendroge: Mengenklasse II",
            "r": "Wurzeldroge: Mengenklasse II", "l": "Drogenholz: Mengenklasse II",
        }[head]
    if body == "aiim":
        return {
            "p": "Pulver: Mengenklasse III", "s": "Samendroge: Mengenklasse III",
            "r": "Wurzeldroge: Mengenklasse III", "l": "Drogenholz: Mengenklasse III",
        }[head]
    raise KeyError(body)


def literal_entry_surface(row: dict[str, str]) -> str | None:
    entry, kind, status = row["entry"], row["kind"], row["status"]
    if "PREDICTED" in status:
        return None
    if kind in {"SCOPED_CONCRETE_HEAD_FORM", "SCOPED_RESIDUAL_HEAD_FORM"}:
        surface = entry.split("@", 1)[0]
        return surface if re.fullmatch(r"[a-z]+", surface) else None
    if kind == "TARGET_SURFACE_DEFAULT" and re.fullmatch(r"[a-z]+", entry):
        return entry
    direct_kinds = {
        "QUALITY_STATE_MATERIAL_CARRIER", "NOMINAL_PART_CARRIER", "DRY_OL_FORM",
        "MOIST_OL_FORM", "HOT_OL_FORM", "COLD_OL_FORM", "DIRECT_QUALITY_VALUE",
        "FUSED_FREE_VALUE", "PART_OR_FORM", "DRY_CTH_MATERIAL", "MOIST_CTH_MATERIAL",
        "NESTED_COLD_DRY_CTH_PART", "WRAPPED_MOIST_CTH_PART", "CTH_BASE_FORM",
        "CTH_FORM_I", "CTH_FORM_II", "CTH_PREPARATION_BASE", "CTH_PREPARATION_FORM_I",
        "DRY_EXTENDED_BOUND_CTH", "MOIST_EXTENDED_BOUND_CTH_FORM_I",
        "DRY_BOUND_CTH_MATERIAL", "MOIST_BOUND_CTH_MATERIAL", "DRY_CTH_PREPARATION",
        "MOIST_CTH_PREPARATION", "DRY_BOUND_CTH_PREPARATION", "MOIST_BOUND_CTH_PREPARATION",
    }
    if kind in direct_kinds and re.fullmatch(r"[a-z]+", entry):
        return entry
    return None


def set_gloss(
    glossary: dict[str, dict[str, object]], surface: str, meaning: str, source: str,
    strength: str, state: str, priority: int,
) -> None:
    previous = glossary.get(surface)
    if previous is None or priority >= int(previous["priority"]):
        glossary[surface] = {
            "surface": surface, "working_meaning_de": meaning, "source": source,
            "strength": strength, "scope_state": state, "priority": priority,
        }


def build_exact_glossary(
    v13: list[dict[str, str]], target_grid: list[dict[str, object]],
) -> dict[str, dict[str, object]]:
    glossary: dict[str, dict[str, object]] = {}
    for row in v13:
        surface = literal_entry_surface(row)
        if not surface:
            continue
        if row["kind"].startswith("SCOPED_"):
            priority, state = 90, "KNOWN_EXACT_WHOLE"
        elif row["kind"] == "TARGET_SURFACE_DEFAULT":
            priority, state = 80, "KNOWN_EXACT_WHOLE"
        else:
            priority = 60
            state = "AMBIGUOUS_ACTIVE_RIVAL" if surface in {"ol", "or"} else "KNOWN_CONTEXT_LICENSED"
        set_gloss(glossary, surface, row["working_meaning_de"], f"V13:{row['kind']}",
                  row["status"], state, priority)

    stages = ((1, "an"), (2, "ain"), (3, "aiin"), (4, "aiiin"))
    qualities = {
        "k": "heiß", "t": "kalt", "ch": "trocken", "sh": "feucht",
        "ok": "heiß im Zubereitungsrahmen", "ot": "kalt im Zubereitungsrahmen",
        "qok": "heiß im qo-Rahmen", "qot": "kalt im qo-Rahmen",
    }
    for prefix, quality in qualities.items():
        for stage, suffix in stages:
            roman = ("I", "II", "III", "IV")[stage - 1]
            set_gloss(glossary, prefix + suffix, f"{quality}, Grad {roman}",
                      "V13:QUALITY_DEGREE_SERIES", "PRODUCTIVE_EXACT_SERIES",
                      "KNOWN_CONTEXT_LICENSED", 70)
    for stage, suffix in stages:
        roman = ("I", "II", "III", "IV")[stage - 1]
        set_gloss(glossary, "d" + suffix, f"Grad-/Maßwert {roman}",
                  "V13:CONTEXTUAL_VALUE_SERIES", "CONTEXTUAL_EXACT_SERIES",
                  "KNOWN_CONTEXT_LICENSED", 70)
        set_gloss(glossary, suffix, f"Menge-/Klassenwert {roman}",
                  "V13:VALUE_MINIM_SERIES", "CONTEXTUAL_EXACT_SERIES",
                  "KNOWN_CONTEXT_LICENSED", 55)
        if stage <= 3:
            set_gloss(glossary, "cth" + suffix, f"Blatt-/Krautgut, Menge/Klasse {roman}",
                      "V13:PART_VALUE_SERIES", "PRODUCTIVE_EXACT_SERIES",
                      "KNOWN_CONTEXT_LICENSED", 70)
        if stage in (2, 3):
            set_gloss(glossary, "chor" + suffix, f"Blüten-/Pflanzenteil, Menge/Klasse {roman}",
                      "V13:PART_VALUE_SERIES", "PRODUCTIVE_EXACT_SERIES",
                      "KNOWN_CONTEXT_LICENSED", 70)

    for row in target_grid:
        if int(row["occurrences"]) > 0:
            set_gloss(glossary, str(row["form"]), str(row["working_default_de"]),
                      "GDT637:ATTESTED_LADDER_CELL", "SCOPED_LADDER_EXTENSION",
                      "KNOWN_EXACT_WHOLE", 100)
    return glossary


def contextual_gloss(
    surface: str, locus: str, ordinal: int, line: list[dict[str, object]],
    glossary: dict[str, dict[str, object]],
) -> tuple[str | None, str, str]:
    if surface == "daiir" and locus == "f85r1.21":
        return "Maß III", "V13:TARGET_LOCUS_DEFAULT", "KNOWN_CONTEXT_LICENSED"
    row = glossary.get(surface)
    if row is None:
        return None, "OPEN", "UNKNOWN_SURFACE"
    meaning = str(row["working_meaning_de"])
    source = str(row["source"])
    state = str(row["scope_state"])
    if source == "V13:CONTEXTUAL_VALUE_SERIES":
        previous = str(line[ordinal - 2]["eva"]) if ordinal > 1 else ""
        if previous.endswith("ol"):
            meaning = meaning.replace("Grad-/Maßwert", "Qualitätsgrad")
        elif previous.endswith(("or", "cthy", "chor", "shor")):
            meaning = meaning.replace("Grad-/Maßwert", "Menge/Portion")
    return meaning, source, state


def build_target_grid(
    token_rows: list[dict[str, str]], positions: dict[tuple[str, int], tuple[int, str]],
    exact: dict[tuple[str, int], int],
) -> list[dict[str, object]]:
    surface_rows: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in token_rows:
        surface_rows[row["eva"]].append(row)
    rows: list[dict[str, object]] = []
    index = 0
    for body in TARGET_ORDER:
        spec = TARGET_SPECS[body]
        for head in HEAD_ORDER:
            index += 1
            form = head + body
            members = surface_rows.get(form, [])
            pos = Counter(positions[row["locus"], int(row["token_index"])][1] for row in members)
            rows.append({
                "cell_id": f"G637-C{index:02d}", "body": body, "components": spec["components"],
                "body_working_value_de": spec["body_value"], "family": spec["family"],
                "stage": spec["stage"], "head": head, "head_class": HEAD_CLASS[head],
                "form": form, "working_default_de": target_gloss(head, body),
                "occurrences": len(members), "pages": len({row["page"] for row in members}),
                "loci": len({row["locus"] for row in members}),
                "reader_exact_occurrences": sum(exact[row["locus"], int(row["token_index"])] for row in members),
                "line_first": pos["FIRST"], "line_middle": pos["MIDDLE"], "line_last": pos["LAST"],
                "rival_de": spec["rival"], "composition_basis": spec["basis"],
                "status": "ATTESTED_SCOPED_LADDER_DEFAULT" if members else "PREDICTED_UNATTESTED_CELL",
            })
    return rows


def build_target_contexts(
    grid: list[dict[str, object]], token_rows: list[dict[str, str]],
    by_line: dict[str, list[dict[str, object]]], positions: dict[tuple[str, int], tuple[int, str]],
    exact: dict[tuple[str, int], int], boundary: dict[tuple[str, int], int],
) -> list[dict[str, object]]:
    forms = {str(row["form"]): row for row in grid if int(row["occurrences"]) > 0}
    rows: list[dict[str, object]] = []
    for member in token_rows:
        if member["eva"] not in forms:
            continue
        cell = forms[member["eva"]]
        locus = member["locus"]
        line = by_line[locus]
        ordinal, position = positions[locus, int(member["token_index"])]
        meaning = str(cell["working_default_de"])
        if cell["body"] in ("aim", "aiim") and position == "LAST":
            meaning += "; Eintrag abgeschlossen"
        rows.append({
            "context_id": "", "page": member["page"], "locus": locus,
            "section": member["section"], "language": member["language"], "hand": member["hand"],
            "cell_id": cell["cell_id"], "body": cell["body"], "head": cell["head"],
            "form": member["eva"], "working_default_de": meaning, "token_ordinal": ordinal,
            "line_position": position, "previous": "<BOS>" if ordinal == 1 else line[ordinal - 2]["eva"],
            "following": "<EOS>" if ordinal == len(line) else line[ordinal]["eva"],
            "reader_exact": exact[locus, int(member["token_index"])],
            "split_normalized": boundary[locus, int(member["token_index"])],
            "zl3b_line": " ".join(str(row["eva"]) for row in line),
        })
    rows.sort(key=lambda row: (str(row["body"]), HEAD_ORDER.index(str(row["head"])), str(row["locus"])))
    for index, row in enumerate(rows, 1):
        row["context_id"] = f"G637-X{index:02d}"
    return rows


def build_context_transfer(
    grid: list[dict[str, object]], by_line: dict[str, list[dict[str, object]]],
) -> list[dict[str, object]]:
    lower = {"aiir": "air", "oiiin": "oiin", "aim": "am", "aiim": "aim"}
    frames: dict[str, set[tuple[str, str]]] = defaultdict(set)
    counts: Counter[str] = Counter()
    for line in by_line.values():
        for index, item in enumerate(line):
            surface = str(item["eva"])
            counts[surface] += 1
            frames[surface].add(("<BOS>" if index == 0 else str(line[index - 1]["eva"]),
                                 "<EOS>" if index + 1 == len(line) else str(line[index + 1]["eva"])))
    rows: list[dict[str, object]] = []
    for cell in grid:
        body, head, form = str(cell["body"]), str(cell["head"]), str(cell["form"])
        lower_form = head + lower[body]
        shared = sorted(frames[form] & frames[lower_form])
        rows.append({
            "cell_id": cell["cell_id"], "body": body, "head": head, "form": form,
            "occurrences": cell["occurrences"], "lower_stage_form": lower_form,
            "lower_stage_occurrences": counts[lower_form], "current_neighbor_frames": len(frames[form]),
            "lower_neighbor_frames": len(frames[lower_form]), "exact_shared_neighbor_frames": len(shared),
            "shared_frame_examples": "|".join(f"{a}>{b}" for a, b in shared[:8]),
            "transfer_reading_de": f"{form} erhöht gegenüber {lower_form} nur die sichtbare Stufe; Kopf und Feld bleiben gleich",
            "status": "ATTESTED_TRANSFER" if int(cell["occurrences"]) else "VISIBLE_PREDICTION",
        })
    return rows


def build_body_contrasts(
    by_line: dict[str, list[dict[str, object]]], exact: dict[tuple[str, int], int],
) -> list[dict[str, object]]:
    specs = (
        ("ar", "aiir", "V13 Fraktionsklasse I gegen neue Teil-/Sortierklasse III"),
        ("air", "aiir", "V13 Fraktionsklasse II gegen neue Teil-/Sortierklasse III"),
        ("aiir", "aim", "Teil-/Sortierklasse III gegen Mengenklasse II"),
        ("aiim", "am", "neue Mengenklasse III gegen V13 Maß-/Einheitsform I"),
    )
    rows: list[dict[str, object]] = []
    def carries_body(surface: str, body: str) -> bool:
        if surface == body:
            return True
        parsed = g636.g635.split_initial(surface)
        return bool(parsed and parsed[1] == body)

    for index, (left, right, meaning) in enumerate(specs, 1):
        loci: list[str] = []
        exact_loci: list[str] = []
        for locus, line in by_line.items():
            left_tokens = [token for token in line if carries_body(str(token["eva"]), left)]
            right_tokens = [token for token in line if carries_body(str(token["eva"]), right)]
            if not left_tokens or not right_tokens:
                continue
            loci.append(locus)
            selected = left_tokens + right_tokens
            if all(exact[locus, int(token["token_index"])] for token in selected):
                exact_loci.append(locus)
        rows.append({
            "contrast_id": f"G637-K{index:02d}", "left_surface": left, "right_surface": right,
            "working_contrast_de": meaning, "shared_lines": len(loci),
            "reader_exact_shared_lines": len(exact_loci), "loci": "|".join(loci),
            "reader_exact_loci": "|".join(exact_loci) or "NONE",
            "consequence_de": "sichtbare Koexistenz verbietet Synonymgleichsetzung der beiden Stufen/Felder",
        })
    return rows


def suggest_unknown(surface: str, section: str) -> tuple[str, str, str]:
    if surface in CURATED_UNKNOWN_DEFAULTS:
        meaning, basis, strength = CURATED_UNKNOWN_DEFAULTS[surface]
        return meaning, f"MANUAL_COMPOSITION:{basis}", strength
    if surface in OPAQUE_UNKNOWN_SURFACES:
        return f"{surface}: ungeklärt", "OPAQUE_REMAINDER_NO_FORCED_COMPOSITION", "OPEN"
    if len(surface) > 1 and surface[0] in HEAD_ORDER and surface[1:] in TARGET_SPECS:
        return target_gloss(surface[0], surface[1:]), "TARGET_LADDER_COMPOSITION", "HIGH"
    material, core = "", surface
    if len(core) > 1 and core[0] in HEAD_ORDER:
        material, core = HEAD_NOUN[core[0]], core[1:]
    cues: list[str] = []
    if "cth" in core:
        cues.append("Blatt-/Krautgut")
    elif "ol" in core:
        cues.append("Material/Zubereitungsstoff")
    elif "al" in core:
        cues.append("Rohstoff")
    elif "or" in core:
        cues.append("Portion/Zutat")
    elif "ar" in core:
        cues.append("Fraktion")
    if core.startswith(("qok", "ok", "k")):
        cues.insert(0, "heiß")
    elif core.startswith(("qot", "ot", "t")):
        cues.insert(0, "kalt")
    if core.startswith("ch"):
        cues.insert(0, "trocken")
    elif core.startswith("sh"):
        cues.insert(0, "feucht/eingeweicht")
    if core.startswith("o"):
        cues.append("Zubereitung/Ansatz")
    if core.endswith("dy"):
        cues.append("fertig aufbereitete Form")
    elif core.endswith("y") and not any("gut" in cue.lower() for cue in cues):
        cues.append("Grundform")
    if core.endswith("m"):
        cues.append("Mengenklasse; nur zeilenfinal zusätzlich Abschluss")
    cues = list(dict.fromkeys(cues))
    if material and cues:
        return f"{material}: " + ", ".join(cues), "VISIBLE_HEAD_PLUS_FIELD_COMPOSITION", "MEDIUM"
    if len(cues) >= 2:
        return ", ".join(cues), "VISIBLE_MULTI_FIELD_COMPOSITION", "MEDIUM"
    if cues:
        return cues[0], "VISIBLE_SINGLE_FIELD_COMPOSITION", "LOW"
    return f"{surface}: ungeklärt", "NO_VISIBLE_COMPOSITION_NO_FILLER", "OPEN"


def build_line_coverage(
    by_line: dict[str, list[dict[str, object]]], glossary: dict[str, dict[str, object]],
    exact: dict[tuple[str, int], int], boundary: dict[tuple[str, int], int],
    cross_by_locus: dict[str, dict[str, str]],
) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    coverage: list[dict[str, object]] = []
    for locus, line in sorted(by_line.items()):
        glosses: list[str] = []
        sources: list[str] = []
        states: list[str] = []
        unknown: list[tuple[int, str]] = []
        for ordinal, token in enumerate(line, 1):
            surface = str(token["eva"])
            meaning, source, state = contextual_gloss(surface, locus, ordinal, line, glossary)
            if meaning is None:
                unknown.append((ordinal, surface))
                glosses.append(f"[{surface}:?]")
            else:
                glosses.append(meaning)
                if not exact[locus, int(token["token_index"])]:
                    state = "READER_BOUNDARY_UNSTABLE"
            sources.append(source)
            states.append(state)
        count = len(line)
        known = count - len(unknown)
        cross = cross_by_locus.get(locus, {})
        coverage.append({
            "page": line[0]["page"], "locus": locus, "section": line[0]["section"],
            "language": line[0]["language"], "hand": line[0]["hand"],
            "token_count": count, "known_tokens": known,
            "context_licensed_tokens": states.count("KNOWN_CONTEXT_LICENSED"),
            "ambiguous_tokens": states.count("AMBIGUOUS_ACTIVE_RIVAL"),
            "reader_unstable_tokens": states.count("READER_BOUNDARY_UNSTABLE"),
            "unknown_tokens": len(unknown), "coverage_fraction": f"{known / count:.6f}",
            "reader_exact_tokens": sum(exact[locus, int(token["token_index"])] for token in line),
            "split_normalized_tokens": sum(boundary[locus, int(token["token_index"])] for token in line),
            "all_three_present": cross.get("all_three_present", "0"),
            "all_present_exact": cross.get("all_present_exact", "0"),
            "zl3b_line": " ".join(str(token["eva"]) for token in line),
            "token_glosses_de": " | ".join(glosses), "gloss_sources": " | ".join(sources),
            "scope_states": " | ".join(states),
            "unknown_ordinals": "|".join(str(item[0]) for item in unknown) or "NONE",
            "unknown_surfaces": "|".join(item[1] for item in unknown) or "NONE",
        })

    one_unknown: list[dict[str, object]] = []
    for row in coverage:
        if int(row["unknown_tokens"]) != 1 or int(row["known_tokens"]) < 1:
            continue
        ordinal = int(str(row["unknown_ordinals"]))
        surface = str(row["unknown_surfaces"])
        line = by_line[str(row["locus"])]
        proposal, basis, strength = suggest_unknown(surface, str(row["section"]))
        strict = int(
            int(row["ambiguous_tokens"]) == 0
            and int(row["reader_unstable_tokens"]) == 0
            and int(row["all_present_exact"]) == 1
        )
        strength_rank = {"HIGH": 4, "MEDIUM": 3, "LOW": 2, "OPEN": 1}[strength]
        score = int(row["known_tokens"]) * 1_000_000 + strength_rank * 100_000 + strict * 10_000 - int(row["token_count"]) * 100
        proposed = str(row["token_glosses_de"]).split(" | ")
        proposed[ordinal - 1] = proposal
        one_unknown.append({
            "rank": 0, "score": score, "strict_eligible": strict, **row,
            "unknown_ordinal": ordinal, "unknown_surface": surface,
            "previous": "<BOS>" if ordinal == 1 else line[ordinal - 2]["eva"],
            "following": "<EOS>" if ordinal == len(line) else line[ordinal]["eva"],
            "proposed_default_de": proposal, "proposal_basis": basis,
            "proposal_strength": strength,
            "proposed_complete_translation_de": "; ".join(proposed),
        })
    one_unknown.sort(key=lambda row: (-int(row["score"]), str(row["locus"])))
    for index, row in enumerate(one_unknown, 1):
        row["rank"] = index
    strict_rows = [dict(row) for row in one_unknown if int(row["strict_eligible"])]
    strict_rows.sort(key=lambda row: (-int(row["known_tokens"]), -int(row["score"]), str(row["locus"])))
    for index, row in enumerate(strict_rows, 1):
        row["rank"] = index

    complete = [dict(row) for row in coverage if int(row["unknown_tokens"]) == 0 and int(row["token_count"]) >= 2]
    for row in complete:
        row["strict_complete"] = int(
            int(row["ambiguous_tokens"]) == 0
            and int(row["reader_unstable_tokens"]) == 0
            and int(row["all_present_exact"]) == 1
        )
    complete.sort(key=lambda row: (-int(row["strict_complete"]), -int(row["token_count"]), str(row["locus"])))
    for index, row in enumerate(complete, 1):
        row["rank"] = index
        row["working_translation_de"] = "; ".join(str(row["token_glosses_de"]).split(" | "))
    return coverage, one_unknown, strict_rows, complete


def build_proposed_defaults(one_unknown: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in one_unknown:
        grouped[str(row["unknown_surface"])].append(row)
    rows: list[dict[str, object]] = []
    strength_rank = {"HIGH": 4, "MEDIUM": 3, "LOW": 2, "OPEN": 1}
    for surface, members in grouped.items():
        best = max(members, key=lambda row: (strength_rank[str(row["proposal_strength"])], int(row["known_tokens"])))
        rows.append({
            "proposal_id": "", "surface": surface, "candidate_lines": len(members),
            "pages": len({str(row["page"]) for row in members}),
            "strict_candidate_lines": sum(int(row["strict_eligible"]) for row in members),
            "proposed_default_de": best["proposed_default_de"],
            "proposal_basis": best["proposal_basis"], "proposal_strength": best["proposal_strength"],
            "example_loci": "|".join(str(row["locus"]) for row in members[:8]),
            "status": "WORKSHEET_PROPOSAL_NOT_IN_V14",
        })
    rows.sort(key=lambda row: (-int(row["strict_candidate_lines"]), -int(row["candidate_lines"]),
                               -strength_rank[str(row["proposal_strength"])], str(row["surface"])))
    for index, row in enumerate(rows, 1):
        row["proposal_id"] = f"G637-P{index:03d}"
    return rows


def build_dictionary(v13: list[dict[str, str]], grid: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = [dict(row) for row in v13]
    for cell in grid:
        if int(cell["occurrences"]) == 0:
            continue
        rule = f"complete token-initial form; {cell['occurrences']} occurrences; lower-stage field retained"
        if cell["body"] in ("aim", "aiim"):
            rule += "; only line-final use additionally closes the entry"
        rows.append({
            "entry": f"{cell['form']}@GDT637_LADDER_FORM", "kind": "SCOPED_LADDER_HEAD_FORM",
            "working_meaning_de": cell["working_default_de"],
            "composition": f"{cell['head']}+{cell['components']}", "context_rule": rule,
            "status": "NEW_V14_ATTESTED_LADDER_DEFAULT",
        })
    return rows


def build(output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    pages = {row["page"] for row in read_tsv(ROOT / G636_ALLOW_REL)}
    if "f1r" in pages or any(page.startswith("f84") for page in pages):
        raise RuntimeError("allow-list contains excluded or forbidden page")
    token_rows, token_stats = g636.g635.g634.g633.g632.g631.guarded_query(
        TOKENS_REL, pages, "page,locus,token_index,eva,section,language,hand",
    )
    cross_rows, cross_stats = g636.g635.g634.g633.g632.g631.guarded_query(
        CROSS_REL, pages, "page,locus,all_three_present,all_present_exact,zl3b_clean,it2a_clean,rf1b_clean",
    )
    cross_by_locus = {row["locus"]: row for row in cross_rows}
    by_line, _ = g636.g635.g634.g633.g632.g631.line_maps([dict(row) for row in token_rows])
    exact, boundary = g636.g635.g634.stable_maps(token_rows, cross_by_locus)
    positions = g636.position_maps(by_line)
    v13 = read_tsv(ROOT / G636_DICT_REL)

    grid = build_target_grid(token_rows, positions, exact)
    contexts = build_target_contexts(grid, token_rows, by_line, positions, exact, boundary)
    transfer = build_context_transfer(grid, by_line)
    contrasts = build_body_contrasts(by_line, exact)
    glossary = build_exact_glossary(v13, grid)
    coverage, one_unknown, strict_rows, complete = build_line_coverage(
        by_line, glossary, exact, boundary, cross_by_locus,
    )
    proposals = build_proposed_defaults(one_unknown)
    dictionary = build_dictionary(v13, grid)

    write_tsv(output_dir / "PAGE_ALLOWLIST.tsv", [{"page": page} for page in sorted(pages)], ("page",))
    write_tsv(output_dir / "LADDER_16_HEAD_CELL_GRID.tsv", grid, (
        "cell_id", "body", "components", "body_working_value_de", "family", "stage", "head",
        "head_class", "form", "working_default_de", "occurrences", "pages", "loci",
        "reader_exact_occurrences", "line_first", "line_middle", "line_last", "rival_de",
        "composition_basis", "status",
    ))
    write_tsv(output_dir / "LADDER_OCCURRENCE_CONTEXTS.tsv", contexts, (
        "context_id", "page", "locus", "section", "language", "hand", "cell_id", "body",
        "head", "form", "working_default_de", "token_ordinal", "line_position", "previous",
        "following", "reader_exact", "split_normalized", "zl3b_line",
    ))
    write_tsv(output_dir / "LADDER_CONTEXT_TRANSFER.tsv", transfer, (
        "cell_id", "body", "head", "form", "occurrences", "lower_stage_form",
        "lower_stage_occurrences", "current_neighbor_frames", "lower_neighbor_frames",
        "exact_shared_neighbor_frames", "shared_frame_examples", "transfer_reading_de", "status",
    ))
    write_tsv(output_dir / "LADDER_BODY_CONTRASTS.tsv", contrasts, (
        "contrast_id", "left_surface", "right_surface", "working_contrast_de", "shared_lines",
        "reader_exact_shared_lines", "loci", "reader_exact_loci", "consequence_de",
    ))
    glossary_rows = [
        {key: row[key] for key in ("surface", "working_meaning_de", "source", "strength", "scope_state", "priority")}
        for row in sorted(glossary.values(), key=lambda item: str(item["surface"]))
    ]
    write_tsv(output_dir / "V14_EXACT_TOKEN_GLOSSARY.tsv", glossary_rows,
              ("surface", "working_meaning_de", "source", "strength", "scope_state", "priority"))
    coverage_fields = (
        "page", "locus", "section", "language", "hand", "token_count", "known_tokens",
        "context_licensed_tokens", "ambiguous_tokens", "reader_unstable_tokens", "unknown_tokens",
        "coverage_fraction", "reader_exact_tokens", "split_normalized_tokens", "all_three_present",
        "all_present_exact", "zl3b_line", "token_glosses_de", "gloss_sources", "scope_states",
        "unknown_ordinals", "unknown_surfaces",
    )
    write_tsv(output_dir / "ALL_LINE_CONCRETE_COVERAGE.tsv", coverage, coverage_fields)
    one_fields = (
        "rank", "score", "strict_eligible", *coverage_fields, "unknown_ordinal", "unknown_surface",
        "previous", "following", "proposed_default_de", "proposal_basis", "proposal_strength",
        "proposed_complete_translation_de",
    )
    write_tsv(output_dir / "ONE_UNKNOWN_PASSAGE_RANKING.tsv", one_unknown, one_fields)
    write_tsv(output_dir / "STRICT_ONE_UNKNOWN_PASSAGES.tsv", strict_rows, one_fields)
    write_tsv(output_dir / "PROPOSED_UNKNOWN_DEFAULTS.tsv", proposals, (
        "proposal_id", "surface", "candidate_lines", "pages", "strict_candidate_lines",
        "proposed_default_de", "proposal_basis", "proposal_strength", "example_loci", "status",
    ))
    write_tsv(output_dir / "COMPLETE_PASSAGE_CANDIDATES.tsv", complete,
              ("rank", "strict_complete", *coverage_fields, "working_translation_de"))
    write_tsv(output_dir / "WORKING_DICTIONARY_V14.tsv", dictionary,
              ("entry", "kind", "working_meaning_de", "composition", "context_rule", "status"))

    attested = [row for row in grid if int(row["occurrences"]) > 0]
    output_paths = [output_dir / name for name in OUTPUT_NAMES]
    output_hashes = {str(BASE_REL / "artifacts" / path.name): sha256(path) for path in output_paths}
    input_paths = (G636_RUN_REL, G636_ALLOW_REL, G636_DICT_REL, G636_DEFAULTS_REL, G636_RESULT_REL, TOKENS_REL, CROSS_REL)
    proposal_counts = Counter(str(row["proposal_strength"]) for row in one_unknown)
    result_core = {
        "schema": "GDT637_LADDER_COMPLETION_ONE_UNKNOWN_PASSAGES_RESULT_V1",
        "experiment_id": "GDT637",
        "status": "EIGHT_ATTESTED_LADDER_CELLS_ADDED__ONE_UNKNOWN_PASSAGES_RANKED",
        "guard": {
            "f1r": "EXCLUDED", "f84": "FORBIDDEN", "f84r": "FORBIDDEN",
            "new_pages": 0, "new_images": 0, "allowed_pages": len(pages),
            "token_query": token_stats, "cross_query": cross_stats, "token_bearing_loci": len(by_line),
        },
        "ladder_completion": {
            "target_bodies": len(TARGET_ORDER), "candidate_cells": len(grid),
            "attested_cells": len(attested), "predicted_unattested_cells": len(grid) - len(attested),
            "attested_occurrences": sum(int(row["occurrences"]) for row in attested),
            "reader_exact_occurrences": sum(int(row["reader_exact_occurrences"]) for row in attested),
            "forms_added_to_v14": len(dictionary) - len(v13),
        },
        "passage_coverage": {
            "physical_lines": len(coverage), "exact_glossary_surfaces": len(glossary),
            "complete_multi_token_lines": len(complete), "one_unknown_lines": len(one_unknown),
            "strict_one_unknown_lines": len(strict_rows),
            "unique_unknown_proposals": len(proposals),
            "bare_contrast_rows": len(contrasts),
            "one_unknown_proposal_strength": dict(sorted(proposal_counts.items())),
            "top_strict_loci": [str(row["locus"]) for row in strict_rows[:20]],
        },
        "working_dictionary": {
            "entries": len(dictionary), "inherited_v13_entries": len(v13),
            "new_attested_entries": len(dictionary) - len(v13),
            "predicted_cells_excluded": len(grid) - len(attested),
        },
        "claim_boundary": (
            "GDT637 extends only four already visible minim ladders under the frozen p/s/r/l material heads. "
            "Eight observed head cells receive the mechanically predicted next-stage meaning and eight empty cells remain visible predictions rather than dictionary entries. "
            "V13 concrete token readings are then applied with explicit scope and reader states to every line on the unchanged 179-page corpus. "
            "Exactly-one-unknown candidates and strict reader-stable candidates are published; unknown-slot proposals remain replaceable suggestions, not confirmed plaintext."
        ),
        "inputs": {str(path): sha256(ROOT / path) for path in input_paths}, "outputs": output_hashes,
    }
    result = {**result_core, "content_sha256": canonical_hash(result_core)}
    (output_dir / "RESULT.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8",
    )
    return result


def main() -> int:
    result = build(ART)
    ladder, passages = result["ladder_completion"], result["passage_coverage"]
    print(
        f"GDT637 built: cells={ladder['candidate_cells']} attested={ladder['attested_cells']} "
        f"occurrences={ladder['attested_occurrences']} glossary={passages['exact_glossary_surfaces']} "
        f"complete={passages['complete_multi_token_lines']} one_unknown={passages['one_unknown_lines']} "
        f"strict={passages['strict_one_unknown_lines']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
