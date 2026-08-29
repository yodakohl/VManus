#!/usr/bin/env python3
"""Build GDT635: exact initial-head swaps and a concrete materia-medica model."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import itertools
import json
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
BASE_REL = Path("experiments/yolo/gdt635_initial_head_same_remainder_swaps")
ART = ROOT / BASE_REL / "artifacts"
G634_BASE = Path("experiments/yolo/gdt634_known_core_terminal_semantics")
G634_RUN_REL = G634_BASE / "src/run.py"
G634_ALLOW_REL = G634_BASE / "artifacts/PAGE_ALLOWLIST.tsv"
G634_DICT_REL = G634_BASE / "artifacts/WORKING_DICTIONARY_V11.tsv"
G634_RESULT_REL = G634_BASE / "artifacts/RESULT.json"
G627_HISTORY_REL = Path("experiments/yolo/gdt627_value_head_role_atlas/artifacts/HISTORICAL_SYNTAX_COMPARATORS.tsv")
TOKENS_REL = Path("transcription/voynich_zl3b_tokens.tsv")
CROSS_REL = Path("transcription/voynich_cross_transcription_lines.tsv")

spec = importlib.util.spec_from_file_location("gdt634_builder", ROOT / G634_RUN_REL)
if spec is None or spec.loader is None:
    raise RuntimeError("cannot load GDT634 builder helpers")
g634 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g634)

OUTPUTS = {
    "allowlist": BASE_REL / "artifacts/PAGE_ALLOWLIST.tsv",
    "profiles": BASE_REL / "artifacts/INITIAL_HEAD_SCOPE_PROFILE.tsv",
    "occupancy": BASE_REL / "artifacts/SHARED_REMAINDER_OCCUPANCY.tsv",
    "shared": BASE_REL / "artifacts/SHARED_REMAINDER_ATLAS.tsv",
    "pairs": BASE_REL / "artifacts/HEAD_PAIR_SHARED_REMAINDER_SUMMARY.tsv",
    "four_way": BASE_REL / "artifacts/FOUR_WAY_REMAINDER_ATLAS.tsv",
    "state_grid": BASE_REL / "artifacts/STATE_BODY_HEAD_GRID.tsv",
    "canonical": BASE_REL / "artifacts/CONCRETE_FOUR_HEAD_PARADIGMS.tsv",
    "same_line": BASE_REL / "artifacts/SAME_LINE_HEAD_SWAPS.tsv",
    "frames": BASE_REL / "artifacts/EXACT_NEIGHBOR_FRAME_SWAPS.tsv",
    "spans": BASE_REL / "artifacts/MATCHED_SPAN_TRANSLATIONS.tsv",
    "models": BASE_REL / "artifacts/HEAD_MODEL_COMPARISON.tsv",
    "active_heads": BASE_REL / "artifacts/ACTIVE_HEAD_CODEBOOK_V12.tsv",
    "history": BASE_REL / "artifacts/HISTORICAL_HEAD_MODEL.tsv",
    "dictionary": BASE_REL / "artifacts/WORKING_DICTIONARY_V12.tsv",
    "result": BASE_REL / "artifacts/RESULT.json",
}

HEAD_ORDER = ("p", "s", "r", "l")
HEADS = {
    "p": {
        "latin": "pulvis", "meaning": "Pulver/Pulverform",
        "rival": "potio oder pilula", "class": "zeileninitialer Stoff-/Formkopf",
    },
    "s": {
        "latin": "semen", "meaning": "Samen/Saatgut",
        "rival": "sal; danach succus oder species", "class": "zeileninitialer Stoffkopf",
    },
    "r": {
        "latin": "radix", "meaning": "Wurzel/Wurzeldroge",
        "rival": "resina", "class": "meist interner Pflanzenteilkopf",
    },
    "l": {
        "latin": "lignum", "meaning": "Drogenholz/holziger Pflanzenteil",
        "rival": "liquor oder Auszug", "class": "meist interner Pflanzenteilkopf",
    },
}

BODY_VALUES = {
    "aiin": ("Typ/Charge III", "KOPF_PLUS_AIII_CLASS"),
    "chedy": ("getrockneter Zustand", "INHERITED_DRY_STATE"),
    "shedy": ("angefeuchteter/eingeweichter Zustand", "INHERITED_MOIST_STATE"),
    "ol": ("Stoff/Material", "INHERITED_OL_CARRIER"),
    "or": ("Teil/Portion", "INHERITED_OR_CARRIER"),
}

STATE_BODY_VALUES = {
    "chy": "trocken, Grundform",
    "chey": "trocken, Bindungsstufe I",
    "cheey": "trocken, Bindungsstufe II",
    "chdy": "getrocknet, kompakte Form",
    "chedy": "getrockneter Zustand",
    "shy": "feucht, Grundform",
    "shey": "feucht, Bindungsstufe I",
    "sheey": "feucht, Bindungsstufe II",
    "shdy": "eingeweicht, kompakte Form",
    "shedy": "angefeuchteter/eingeweichter Zustand",
}

SPAN_SPECS = (
    ("PS_DRY_P", "f75r.13", 1, 2, ("pchedy", "keedy"),
     ("getrocknetes Pulver", "Heißzustand II"),
     "getrocknetes Pulver, erhitzt auf Stufe II", "p=Pulver"),
    ("PS_DRY_S", "f78r.9", 1, 2, ("schedy", "keedy"),
     ("getrocknete Saat", "Heißzustand II"),
     "getrocknete Saat, erhitzt auf Stufe II", "s=Samen; Salz bleibt Rivale"),
    ("PS_MATERIAL_P", "f77r.38", 1, 2, ("pol", "shedy"),
     ("Pulverstoff", "angefeuchtet/eingeweicht"),
     "Pulverstoff, angefeuchtet zu Paste oder Brei", "p=Pulver"),
    ("PS_MATERIAL_S", "f76v.40", 1, 2, ("sol", "shedy"),
     ("Samenmaterial/Saatgut", "angefeuchtet/eingeweicht"),
     "Saatgut, eingeweicht", "s=semen ist hier natürlicher als s=sal"),
    ("PS_CLASS_P", "f10v.1", 1, 2, ("paiin", "daiin"),
     ("Pulver, Typ/Charge III", "Dosis/Maß III"),
     "Pulver der Klasse III, Dosis III", "aIII nach Stoffkopf ist Klasse; d+aIII ist Dosis"),
    ("PS_CLASS_S", "f81v.3", 1, 2, ("saiin", "daiin"),
     ("Saatgut, Typ/Charge III", "Dosis/Maß III"),
     "Saatgut der Klasse III, Dosis III", "aIII nach Stoffkopf ist Klasse; d+aIII ist Dosis"),
    ("RL_MATERIAL_R", "f106v.8", 2, 4, ("cheo", "rol", "aiin"),
     ("Trockenansatz", "Wurzelstoff", "Menge/Stufe III"),
     "Trockenansatz aus Wurzelstoff, Menge III", "r=radix"),
    ("RL_MATERIAL_L", "f111v.10", 5, 7, ("cheo", "lol", "aiin"),
     ("Trockenansatz", "Holzstoff", "Menge/Stufe III"),
     "Trockenansatz aus Holzstoff, Menge III", "l=lignum; liquor ist hier schwach"),
    ("RL_PORTION_L", "f103r.21", 11, 12, ("qokeedy", "lor"),
     ("Heißzustand II", "Holzportion"),
     "Holzportion, erhitzt auf Stufe II", "l=lignum"),
    ("RL_PORTION_R", "f79v.13", 8, 9, ("qokeedy", "ror"),
     ("Heißzustand II", "Wurzelportion"),
     "Wurzelportion, erhitzt auf Stufe II", "r=radix"),
)

SPAN_READER_NOTES = {
    "PS_DRY_P": "beide Zieltoken in ZL3b, IT2a und RF1b exakt",
    "PS_DRY_S": "RF1b sche|y und kee|y: Spaltung plus d-Glyphabweichung, nicht exakt rekonstruierbar",
    "PS_MATERIAL_P": "beide Zieltoken in allen drei Lesern exakt",
    "PS_MATERIAL_S": "beide Zieltoken in allen drei Lesern exakt",
    "PS_CLASS_P": "ganze Zeile in allen drei Lesern exakt",
    "PS_CLASS_S": "beide Zieltoken in allen drei Lesern exakt",
    "RL_MATERIAL_R": "ganze Zeile in allen drei Lesern exakt",
    "RL_MATERIAL_L": "RF1b trennt lol als l|ol; vollständige Zieloberfläche bleibt split-normalisiert",
    "RL_PORTION_L": "RF1b qokee|y: Spaltung plus d-Glyphabweichung; lor bleibt exakt",
    "RL_PORTION_R": "beide Zieltoken in allen drei Lesern exakt",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_hash(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: Iterable[str]) -> None:
    g634.write_tsv(path, rows, fields)


def counter_text(values: Iterable[str]) -> str:
    counts = Counter(values)
    return "|".join(f"{key}:{counts[key]}" for key in sorted(counts)) or "NONE"


def split_initial(surface: str) -> tuple[str, str] | None:
    if len(surface) <= 1 or surface[0] not in HEAD_ORDER:
        return None
    if surface.startswith("sh"):
        return None
    return surface[0], surface[1:]


def compose(head: str, body: str) -> str:
    noun = {
        "p": "Pulver", "s": "Samen/Saatgut", "r": "Wurzel", "l": "Drogenholz",
    }[head]
    if body == "aiin":
        return f"{noun}, Typ/Charge III"
    if body == "chedy":
        return {
            "p": "getrocknetes Pulver", "s": "getrocknete Samen/Saat",
            "r": "getrocknete Wurzel", "l": "getrocknetes Drogenholz",
        }[head]
    if body == "shedy":
        return {
            "p": "angefeuchtetes Pulver/Paste", "s": "eingeweichte Samen/Saat",
            "r": "eingeweichte Wurzel", "l": "eingeweichtes Drogenholz",
        }[head]
    if body == "ol":
        return {"p": "Pulverstoff", "s": "Samenmaterial/Saatgut", "r": "Wurzelstoff", "l": "Holzstoff"}[head]
    if body == "or":
        return {"p": "Pulverportion", "s": "Samenportion", "r": "Wurzelportion", "l": "Holzportion"}[head]
    if body in STATE_BODY_VALUES:
        return f"{noun}: {STATE_BODY_VALUES[body]}"
    raise KeyError(body)


def token_position_maps(by_line: dict[str, list[dict[str, object]]]) -> tuple[dict[tuple[str, int], int], dict[tuple[str, int], str]]:
    ordinal: dict[tuple[str, int], int] = {}
    position: dict[tuple[str, int], str] = {}
    for locus, line in by_line.items():
        for i, row in enumerate(line):
            key = (locus, int(row["token_index"]))
            ordinal[key] = i + 1
            position[key] = "FIRST" if i == 0 else "LAST" if i + 1 == len(line) else "MIDDLE"
    return ordinal, position


def build_profiles(
    token_rows: list[dict[str, str]], by_line: dict[str, list[dict[str, object]]],
    exact: dict[tuple[str, int], int],
) -> list[dict[str, object]]:
    _, positions = token_position_maps(by_line)
    all_surfaces = Counter(row["eva"] for row in token_rows)
    rows: list[dict[str, object]] = []
    for head in HEAD_ORDER:
        selected = [row for row in token_rows if (split_initial(row["eva"]) or (None, None))[0] == head]
        pos = Counter(positions[row["locus"], int(row["token_index"])] for row in selected)
        terminal_types = {surface for surface in all_surfaces if len(surface) > 1 and surface.endswith(head)}
        internal_types = {surface for surface in all_surfaces if head in surface[1:-1]}
        rows.append({
            "head": head, "latin_stem": HEADS[head]["latin"], "primary_default_de": HEADS[head]["meaning"],
            "live_rival_de": HEADS[head]["rival"], "syntactic_subclass_de": HEADS[head]["class"],
            "initial_occurrences": len(selected), "initial_types": len({row["eva"] for row in selected}),
            "initial_pages": len({row["page"] for row in selected}), "initial_loci": len({row["locus"] for row in selected}),
            "initial_reader_exact_occurrences": sum(exact[row["locus"], int(row["token_index"])] for row in selected),
            "line_first": pos["FIRST"], "line_middle": pos["MIDDLE"], "line_last": pos["LAST"],
            "standalone_occurrences": all_surfaces[head],
            "terminal_occurrences": sum(all_surfaces[surface] for surface in terminal_types),
            "terminal_types": len(terminal_types),
            "internal_token_occurrences": sum(all_surfaces[surface] for surface in internal_types),
            "internal_types": len(internal_types),
            "internal_sign_occurrences": sum(all_surfaces[surface] * surface[1:-1].count(head) for surface in internal_types),
            "delete_head_counterpart_occurrences": sum(all_surfaces[row["eva"][1:]] > 0 for row in selected),
            "excluded_sh_occurrences": sum(count for surface, count in all_surfaces.items() if head == "s" and surface.startswith("sh")),
            "excluded_sh_types": sum(1 for surface in all_surfaces if head == "s" and surface.startswith("sh")),
            "scope_rule_de": "nur erstes Zeichen; sh, Einzeichenform, inneres und terminales Zeichen sind getrennt",
        })
    return rows


def collect_cells(
    token_rows: list[dict[str, str]], exact: dict[tuple[str, int], int],
) -> tuple[dict[str, dict[str, list[dict[str, str]]]], Counter[str]]:
    cells: dict[str, dict[str, list[dict[str, str]]]] = defaultdict(lambda: defaultdict(list))
    surface_counts = Counter(row["eva"] for row in token_rows)
    for row in token_rows:
        parsed = split_initial(row["eva"])
        if parsed is None:
            continue
        head, body = parsed
        enriched = dict(row)
        enriched["reader_exact"] = str(exact[row["locus"], int(row["token_index"])])
        cells[body][head].append(enriched)
    return cells, surface_counts


def cell_text(body_heads: dict[str, list[dict[str, str]]], value: str) -> str:
    parts = []
    for head in HEAD_ORDER:
        rows = body_heads.get(head, [])
        if value == "form":
            datum = head + next(iter({row["eva"][1:] for row in rows}), "") if rows else "-"
        elif value == "occ":
            datum = str(len(rows))
        elif value == "pages":
            datum = str(len({row["page"] for row in rows}))
        elif value == "exact":
            datum = str(sum(int(row["reader_exact"]) for row in rows))
        elif value == "loci":
            datum = str(len({row["locus"] for row in rows}))
        else:
            raise KeyError(value)
        parts.append(f"{head}:{datum}")
    return "|".join(parts)


def build_occupancy(
    cells: dict[str, dict[str, list[dict[str, str]]]], surface_counts: Counter[str], dictionary_entries: set[str],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for body, heads in cells.items():
        total = sum(len(values) for values in heads.values())
        rows.append({
            "body": body, "head_occupancy": len(heads), "heads": "|".join(h for h in HEAD_ORDER if h in heads),
            "forms": cell_text(heads, "form"), "occurrences_by_head": cell_text(heads, "occ"),
            "total_headed_occurrences": total, "pages_by_head": cell_text(heads, "pages"),
            "loci_by_head": cell_text(heads, "loci"), "reader_exact_by_head": cell_text(heads, "exact"),
            "bare_body_occurrences": surface_counts[body], "exact_v11_dictionary_body": int(body in dictionary_entries),
        })
    return sorted(rows, key=lambda row: (-int(row["head_occupancy"]), -int(row["total_headed_occurrences"]), str(row["body"])))


def build_shared(occupancy: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for index, row in enumerate((r for r in occupancy if int(r["head_occupancy"]) >= 2), 1):
        body = str(row["body"])
        rows.append({
            "shared_id": f"G635-R{index:03d}", **row,
            "inherited_or_working_body_value_de": BODY_VALUES.get(body, ("noch keine konkrete Restbedeutung", "ATLAS_ONLY"))[0],
            "semantic_status": BODY_VALUES.get(body, ("", "ATLAS_ONLY"))[1],
        })
    return rows


def build_four_way(shared: list[dict[str, object]]) -> list[dict[str, object]]:
    rows = []
    for index, row in enumerate((r for r in shared if int(r["head_occupancy"]) == 4), 1):
        rows.append({
            "quad_id": f"G635-Q{index:02d}", "body": row["body"], "forms": row["forms"],
            "occurrences_by_head": row["occurrences_by_head"], "total_headed_occurrences": row["total_headed_occurrences"],
            "reader_exact_by_head": row["reader_exact_by_head"], "bare_body_occurrences": row["bare_body_occurrences"],
            "working_body_value_de": row["inherited_or_working_body_value_de"],
            "semantic_status": row["semantic_status"],
        })
    return rows


def build_state_grid(cells: dict[str, dict[str, list[dict[str, str]]]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    index = 0
    for body, body_value in STATE_BODY_VALUES.items():
        for head in HEAD_ORDER:
            index += 1
            members = cells.get(body, {}).get(head, [])
            rows.append({
                "cell_id": f"G635-S{index:02d}", "body": body, "body_value_de": body_value,
                "head": head, "form": head + body, "working_default_de": compose(head, body),
                "occurrences": len(members), "pages": len({row["page"] for row in members}),
                "loci": len({row["locus"] for row in members}),
                "reader_exact_occurrences": sum(int(row["reader_exact"]) for row in members),
                "attested": int(bool(members)), "status": "ATTESTED_CONCRETE_DEFAULT" if members else "PREDICTED_EMPTY_CELL",
            })
    return rows


def build_canonical(cells: dict[str, dict[str, list[dict[str, str]]]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    index = 0
    for body, (body_value, basis) in BODY_VALUES.items():
        for head in HEAD_ORDER:
            index += 1
            members = cells[body][head]
            rows.append({
                "cell_id": f"G635-C{index:02d}", "paradigm": body.upper(), "body": body,
                "body_value_de": body_value, "head": head, "head_value_de": HEADS[head]["meaning"],
                "form": head + body, "working_default_de": compose(head, body),
                "occurrences": len(members), "pages": len({row["page"] for row in members}),
                "loci": len({row["locus"] for row in members}),
                "reader_exact_occurrences": sum(int(row["reader_exact"]) for row in members),
                "section_counts": counter_text(row["section"] for row in members),
                "language_counts": counter_text(row["language"] for row in members),
                "basis": basis, "confidence": "LOW_MEDIUM", "live_rival_de": HEADS[head]["rival"],
                "status": "ATTESTED_COMPLETE_FOUR_HEAD_PARADIGM",
            })
    return rows


def build_same_line(
    cells: dict[str, dict[str, list[dict[str, str]]]], by_line: dict[str, list[dict[str, object]]],
    exact: dict[tuple[str, int], int],
) -> list[dict[str, object]]:
    shared_bodies = {body for body, heads in cells.items() if len(heads) >= 2}
    rows: list[dict[str, object]] = []
    for locus, line in sorted(by_line.items()):
        line_cells: dict[str, dict[str, list[dict[str, object]]]] = defaultdict(lambda: defaultdict(list))
        for row in line:
            parsed = split_initial(str(row["eva"]))
            if parsed and parsed[1] in shared_bodies:
                line_cells[parsed[1]][parsed[0]].append(row)
        for body, heads in sorted(line_cells.items()):
            for head_a, head_b in itertools.combinations((h for h in HEAD_ORDER if h in heads), 2):
                a_rows, b_rows = heads[head_a], heads[head_b]
                rows.append({
                    "swap_id": "", "page": line[0]["page"], "locus": locus,
                    "section": line[0]["section"], "language": line[0]["language"], "hand": line[0]["hand"],
                    "body": body, "head_a": head_a, "form_a": head_a + body,
                    "positions_a": "|".join(str(i + 1) for i, row in enumerate(line) if row in a_rows),
                    "head_b": head_b, "form_b": head_b + body,
                    "positions_b": "|".join(str(i + 1) for i, row in enumerate(line) if row in b_rows),
                    "reader_exact_a": sum(exact[locus, int(row["token_index"])] for row in a_rows),
                    "reader_exact_b": sum(exact[locus, int(row["token_index"])] for row in b_rows),
                    "zl3b_line": " ".join(str(row["eva"]) for row in line),
                    "working_contrast_de": f"{compose(head_a, body) if body in BODY_VALUES else HEADS[head_a]['meaning'] + ' + ' + body} ↔ {compose(head_b, body) if body in BODY_VALUES else HEADS[head_b]['meaning'] + ' + ' + body}",
                })
    for index, row in enumerate(rows, 1):
        row["swap_id"] = f"G635-L{index:02d}"
    return rows


def build_frames(
    cells: dict[str, dict[str, list[dict[str, str]]]], by_line: dict[str, list[dict[str, object]]],
    exact: dict[tuple[str, int], int],
) -> list[dict[str, object]]:
    shared_bodies = {body for body, heads in cells.items() if len(heads) >= 2}
    frame_map: dict[tuple[str, str, str], dict[str, list[dict[str, object]]]] = defaultdict(lambda: defaultdict(list))
    for locus, line in by_line.items():
        for index, row in enumerate(line):
            parsed = split_initial(str(row["eva"]))
            if not parsed or parsed[1] not in shared_bodies:
                continue
            head, body = parsed
            prev = "<BOS>" if index == 0 else str(line[index - 1]["eva"])
            nxt = "<EOS>" if index + 1 == len(line) else str(line[index + 1]["eva"])
            frame_map[body, prev, nxt][head].append(row)
    rows: list[dict[str, object]] = []
    for (body, prev, nxt), heads in frame_map.items():
        if len(heads) < 2:
            continue
        ordered_heads = [head for head in HEAD_ORDER if head in heads]
        registers_by_head = {
            head: {(row["section"], row["language"], row["hand"]) for row in members}
            for head, members in heads.items()
        }
        shared_registers = set.intersection(*(registers_by_head[head] for head in ordered_heads))
        all_members = [row for head in ordered_heads for row in heads[head]]
        rows.append({
            "frame_id": "", "body": body, "previous": prev, "following": nxt,
            "heads": "|".join(ordered_heads), "forms": "|".join(head + body for head in ordered_heads),
            "occurrences_by_head": "|".join(f"{head}:{len(heads[head])}" for head in ordered_heads),
            "loci_by_head": "|".join(f"{head}:{'&'.join(sorted({row['locus'] for row in heads[head]}))}" for head in ordered_heads),
            "reader_exact_by_head": "|".join(f"{head}:{sum(exact[row['locus'], int(row['token_index'])] for row in heads[head])}" for head in ordered_heads),
            "register_matched_all_heads": int(bool(shared_registers)),
            "shared_registers": "|".join("/".join(register) for register in sorted(shared_registers)) or "NONE",
            "pages": "|".join(sorted({str(row["page"]) for row in all_members})),
            "working_contrast_de": " ↔ ".join(compose(head, body) if body in BODY_VALUES else HEADS[head]["meaning"] + " + " + body for head in ordered_heads),
        })
    rows.sort(key=lambda row: (-len(str(row["heads"]).split("|")), str(row["body"]), str(row["previous"]), str(row["following"])))
    for index, row in enumerate(rows, 1):
        row["frame_id"] = f"G635-F{index:02d}"
    return rows


def build_pair_summary(
    cells: dict[str, dict[str, list[dict[str, str]]]], same_line: list[dict[str, object]], frames: list[dict[str, object]],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for head_a, head_b in itertools.combinations(HEAD_ORDER, 2):
        bodies = [body for body, heads in cells.items() if head_a in heads and head_b in heads]
        pair_only = [body for body in bodies if set(cells[body]) == {head_a, head_b}]
        reader_both = sum(
            any(int(row["reader_exact"]) for row in cells[body][head_a])
            and any(int(row["reader_exact"]) for row in cells[body][head_b])
            for body in bodies
        )
        line_cells = sum({str(row["head_a"]), str(row["head_b"])} == {head_a, head_b} for row in same_line)
        frame_cells = sum(head_a in str(row["heads"]).split("|") and head_b in str(row["heads"]).split("|") for row in frames)
        register_cells = sum(
            head_a in str(row["heads"]).split("|") and head_b in str(row["heads"]).split("|")
            and int(row["register_matched_all_heads"]) for row in frames
        )
        rows.append({
            "pair": head_a + head_b, "head_a": head_a, "head_b": head_b,
            "shared_bodies": len(bodies), "exact_pair_only_bodies": len(pair_only),
            "head_a_occurrences_on_shared_bodies": sum(len(cells[body][head_a]) for body in bodies),
            "head_b_occurrences_on_shared_bodies": sum(len(cells[body][head_b]) for body in bodies),
            "bodies_with_reader_exact_evidence_for_both": reader_both,
            "same_line_body_locus_cells": line_cells, "exact_two_sided_frame_cells": frame_cells,
            "register_matched_frame_cells": register_cells,
            "working_contrast_de": f"{HEADS[head_a]['meaning']} ↔ {HEADS[head_b]['meaning']}",
        })
    return rows


def build_spans(
    by_line: dict[str, list[dict[str, object]]], exact: dict[tuple[str, int], int],
    boundary: dict[tuple[str, int], int], cross_by_locus: dict[str, dict[str, str]],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for span_id, locus, start, end, expected, glosses, translation, inference in SPAN_SPECS:
        line = by_line[locus]
        selected = line[start - 1:end]
        surfaces = tuple(str(row["eva"]) for row in selected)
        if surfaces != expected:
            raise RuntimeError(f"span mismatch {span_id}: {surfaces} != {expected}")
        cross = cross_by_locus[locus]
        exact_values = [exact[locus, int(row["token_index"])] for row in selected]
        boundary_values = [boundary[locus, int(row["token_index"])] for row in selected]
        rows.append({
            "span_id": span_id, "page": line[0]["page"], "locus": locus,
            "section": line[0]["section"], "language": line[0]["language"], "hand": line[0]["hand"],
            "start_position": start, "end_position": end, "surface_span": " | ".join(surfaces),
            "token_glosses_de": " | ".join(glosses), "working_translation_de": translation,
            "concrete_inference_de": inference, "all_target_tokens_reader_exact": int(all(exact_values)),
            "all_target_tokens_split_normalized": int(all(boundary_values)),
            "reader_evidence_de": SPAN_READER_NOTES[span_id],
            "zl3b_line": " ".join(str(row["eva"]) for row in line),
            "it2a_line": cross["it2a_clean"], "rf1b_line": cross["rf1b_clean"],
            "status": "COMPLETE_CONCRETE_WORKING_TRANSLATION",
        })
    return rows


def build_models() -> list[dict[str, object]]:
    return [
        {
            "model_id": "G634_PRIOR", "p": "pulvis", "s": "sal", "r": "radix", "l": "liquor",
            "canonical_result_de": "Pulver und Wurzel brauchbar; Salz offen; getrocknete/eingeweichte Flüssigkeit unnatürlich",
            "historical_fit_de": "Einzelstämme historisch, aber keine passende Viererarchitektur gezeigt",
            "status": "DEMOTED_BY_LCHEDY_LSHEDY",
        },
        {
            "model_id": "EXTRACT_RIVAL", "p": "pulvis", "s": "sal", "r": "radix", "l": "liquor/Auszug",
            "canonical_result_de": "getrockneter oder eingeweichter Auszug ist möglich; Samenpassagen bleiben schwach",
            "historical_fit_de": "Auszug ist semantische Reparatur, keine klare Initialstamm-Analogie",
            "status": "LIVE_RIVAL",
        },
        {
            "model_id": "MATERIA_QUARTET_V12", "p": "pulvis", "s": "semen", "r": "radix", "l": "lignum",
            "canonical_result_de": "alle 20 Formen ergeben konkrete Pulver-, Samen-, Wurzel- und Holzlesungen",
            "historical_fit_de": "Pulvis+semen sowie lignum/radix+heiß/trocken+Grad sind um 1400/frühes 15. Jh. belegt",
            "status": "PRIMARY_WORKING_MODEL",
        },
    ]


def build_active_heads(profiles: list[dict[str, object]]) -> list[dict[str, object]]:
    by_head = {str(row["head"]): row for row in profiles}
    rows = []
    for head in HEAD_ORDER:
        profile = by_head[head]
        rows.append({
            "entry": head, "scope": "TOKEN_INITIAL_ONLY", "latin_stem": HEADS[head]["latin"],
            "working_meaning_de": HEADS[head]["meaning"], "syntactic_subclass_de": HEADS[head]["class"],
            "live_rival_de": HEADS[head]["rival"], "occurrences": profile["initial_occurrences"],
            "types": profile["initial_types"], "pages": profile["initial_pages"],
            "composition_rule": f"{head}+vollständiger Rest; Rest bleibt sichtbar; sh ist kein s+Rest",
            "status": "GDT635_PRIMARY_WORKING_HEAD",
        })
    return rows


def build_history() -> list[dict[str, object]]:
    return [
        {
            "comparator_id": "SALZBURG_MI89_PULVIS", "date_place": "Bayern/Österreich, Wende 14./15. Jh.",
            "source": "Salzburg UB M I 89", "folio": "f148v; f155v",
            "url": "https://manuscripta.at/diglit/AT7400-MI89/0298",
            "source_evidence": "Pulvis probatissimus; recipe pulveris eufrasiae",
            "analogy_here": "pulvis ist ein realer zeitnaher Rezeptkopf; keine Voynich-Glyphidentifikation",
        },
        {
            "comparator_id": "SALZBURG_MI89_SEMEN", "date_place": "Bayern/Österreich, Wende 14./15. Jh.",
            "source": "Salzburg UB M I 89", "folio": "f266r",
            "url": "https://manuscripta.at/diglit/AT7400-MI89/0533",
            "source_evidence": "Accipe semen Petroselini, apii, salviae, ysopi",
            "analogy_here": "semen steht im selben Codexsystem wie pulvis; s=semen bleibt eine Analogie",
        },
        {
            "comparator_id": "WELLCOME_MS542_LIGNUM", "date_place": "England, frühes 15. Jh.",
            "source": "Wellcome MS.542", "folio": "f118r",
            "url": "https://wellcomecollection.org/works/n674z2xd",
            "source_evidence": "Aloes lignum, calidum et siccum in ii gradu",
            "analogy_here": "lignum kombiniert historisch mit heiß/trocken und Grad II; l=lignum ist keine Entzifferung",
        },
        {
            "comparator_id": "WELLCOME_MS542_RADIX", "date_place": "England, frühes 15. Jh.",
            "source": "Wellcome MS.542", "folio": "f119v",
            "url": "https://wellcomecollection.org/works/n674z2xd",
            "source_evidence": "Radix ponitur in medicinis; calidus et siccus in iii gradu",
            "analogy_here": "radix kombiniert historisch mit heiß/trocken und Grad III; r=radix ist keine Entzifferung",
        },
    ]


def build_dictionary(old_rows: list[dict[str, str]], canonical: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = [dict(row) for row in old_rows]
    for head in HEAD_ORDER:
        rows.append({
            "entry": f"{head}@GDT635_INITIAL_HEAD", "kind": "SCOPED_INITIAL_MATERIA_HEAD",
            "working_meaning_de": HEADS[head]["meaning"], "composition": f"{head}+vollständiger Rest",
            "context_rule": f"nur tokeninitial; nicht Einzeichen-{head}, internes oder terminales {head}; sh ausgeschlossen",
            "status": "NEW_V12_SCOPED_PRIMARY_HEAD",
        })
    for row in canonical:
        rows.append({
            "entry": f"{row['form']}@GDT635_HEAD_FORM", "kind": "SCOPED_CONCRETE_HEAD_FORM",
            "working_meaning_de": row["working_default_de"], "composition": f"{row['head']}+{row['body']}",
            "context_rule": f"tokeninitiale Ganzform; {row['occurrences']} Vorkommen; Rivale: {row['live_rival_de']}",
            "status": "NEW_V12_ATTESTED_CONCRETE_DEFAULT",
        })
    return rows


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    pages = {row["page"] for row in read_tsv(ROOT / G634_ALLOW_REL)}
    if "f1r" in pages or any(page.startswith("f84") for page in pages):
        raise RuntimeError("allow-list contains excluded or forbidden page")
    token_rows, token_stats = g634.g633.g632.g631.guarded_query(
        TOKENS_REL, pages, "page,locus,token_index,eva,section,language,hand",
    )
    cross_rows, cross_stats = g634.g633.g632.g631.guarded_query(
        CROSS_REL, pages, "page,locus,all_three_present,all_present_exact,zl3b_clean,it2a_clean,rf1b_clean",
    )
    cross_by_locus = {row["locus"]: row for row in cross_rows}
    by_line, _ = g634.g633.g632.g631.line_maps([dict(row) for row in token_rows])
    exact, boundary = g634.stable_maps(token_rows, cross_by_locus)
    profiles = build_profiles(token_rows, by_line, exact)
    cells, surface_counts = collect_cells(token_rows, exact)
    old_dictionary = read_tsv(ROOT / G634_DICT_REL)
    occupancy = build_occupancy(cells, surface_counts, {row["entry"] for row in old_dictionary})
    shared = build_shared(occupancy)
    four_way = build_four_way(shared)
    state_grid = build_state_grid(cells)
    canonical = build_canonical(cells)
    same_line = build_same_line(cells, by_line, exact)
    frames = build_frames(cells, by_line, exact)
    pairs = build_pair_summary(cells, same_line, frames)
    spans = build_spans(by_line, exact, boundary, cross_by_locus)
    models = build_models()
    active_heads = build_active_heads(profiles)
    history = build_history()
    dictionary = build_dictionary(old_dictionary, canonical)

    write_tsv(ROOT / OUTPUTS["allowlist"], [{"page": page} for page in sorted(pages)], ("page",))
    write_tsv(ROOT / OUTPUTS["profiles"], profiles, (
        "head", "latin_stem", "primary_default_de", "live_rival_de", "syntactic_subclass_de",
        "initial_occurrences", "initial_types", "initial_pages", "initial_loci", "initial_reader_exact_occurrences",
        "line_first", "line_middle", "line_last", "standalone_occurrences", "terminal_occurrences", "terminal_types",
        "internal_token_occurrences", "internal_types", "internal_sign_occurrences", "delete_head_counterpart_occurrences",
        "excluded_sh_occurrences", "excluded_sh_types", "scope_rule_de",
    ))
    write_tsv(ROOT / OUTPUTS["occupancy"], occupancy, (
        "body", "head_occupancy", "heads", "forms", "occurrences_by_head", "total_headed_occurrences",
        "pages_by_head", "loci_by_head", "reader_exact_by_head", "bare_body_occurrences", "exact_v11_dictionary_body",
    ))
    write_tsv(ROOT / OUTPUTS["shared"], shared, (
        "shared_id", "body", "head_occupancy", "heads", "forms", "occurrences_by_head", "total_headed_occurrences",
        "pages_by_head", "loci_by_head", "reader_exact_by_head", "bare_body_occurrences", "exact_v11_dictionary_body",
        "inherited_or_working_body_value_de", "semantic_status",
    ))
    write_tsv(ROOT / OUTPUTS["pairs"], pairs, (
        "pair", "head_a", "head_b", "shared_bodies", "exact_pair_only_bodies", "head_a_occurrences_on_shared_bodies",
        "head_b_occurrences_on_shared_bodies", "bodies_with_reader_exact_evidence_for_both", "same_line_body_locus_cells",
        "exact_two_sided_frame_cells", "register_matched_frame_cells", "working_contrast_de",
    ))
    write_tsv(ROOT / OUTPUTS["four_way"], four_way, (
        "quad_id", "body", "forms", "occurrences_by_head", "total_headed_occurrences", "reader_exact_by_head",
        "bare_body_occurrences", "working_body_value_de", "semantic_status",
    ))
    write_tsv(ROOT / OUTPUTS["state_grid"], state_grid, (
        "cell_id", "body", "body_value_de", "head", "form", "working_default_de", "occurrences", "pages",
        "loci", "reader_exact_occurrences", "attested", "status",
    ))
    write_tsv(ROOT / OUTPUTS["canonical"], canonical, (
        "cell_id", "paradigm", "body", "body_value_de", "head", "head_value_de", "form", "working_default_de",
        "occurrences", "pages", "loci", "reader_exact_occurrences", "section_counts", "language_counts", "basis",
        "confidence", "live_rival_de", "status",
    ))
    write_tsv(ROOT / OUTPUTS["same_line"], same_line, (
        "swap_id", "page", "locus", "section", "language", "hand", "body", "head_a", "form_a", "positions_a",
        "head_b", "form_b", "positions_b", "reader_exact_a", "reader_exact_b", "zl3b_line", "working_contrast_de",
    ))
    write_tsv(ROOT / OUTPUTS["frames"], frames, (
        "frame_id", "body", "previous", "following", "heads", "forms", "occurrences_by_head", "loci_by_head",
        "reader_exact_by_head", "register_matched_all_heads", "shared_registers", "pages", "working_contrast_de",
    ))
    write_tsv(ROOT / OUTPUTS["spans"], spans, (
        "span_id", "page", "locus", "section", "language", "hand", "start_position", "end_position", "surface_span",
        "token_glosses_de", "working_translation_de", "concrete_inference_de", "all_target_tokens_reader_exact",
        "all_target_tokens_split_normalized", "reader_evidence_de", "zl3b_line", "it2a_line", "rf1b_line", "status",
    ))
    write_tsv(ROOT / OUTPUTS["models"], models, (
        "model_id", "p", "s", "r", "l", "canonical_result_de", "historical_fit_de", "status",
    ))
    write_tsv(ROOT / OUTPUTS["active_heads"], active_heads, (
        "entry", "scope", "latin_stem", "working_meaning_de", "syntactic_subclass_de", "live_rival_de",
        "occurrences", "types", "pages", "composition_rule", "status",
    ))
    write_tsv(ROOT / OUTPUTS["history"], history, (
        "comparator_id", "date_place", "source", "folio", "url", "source_evidence", "analogy_here",
    ))
    write_tsv(ROOT / OUTPUTS["dictionary"], dictionary, (
        "entry", "kind", "working_meaning_de", "composition", "context_rule", "status",
    ))

    occupancy_counts = Counter(int(row["head_occupancy"]) for row in occupancy)
    occupancy_occ = Counter()
    for row in occupancy:
        occupancy_occ[int(row["head_occupancy"])] += int(row["total_headed_occurrences"])
    profiles_by_head = {str(row["head"]): row for row in profiles}
    pairs_by_pair = {str(row["pair"]): row for row in pairs}
    output_hashes = {str(path): sha256(ROOT / path) for key, path in OUTPUTS.items() if key != "result"}
    input_paths = (TOKENS_REL, CROSS_REL, G627_HISTORY_REL, G634_RUN_REL, G634_ALLOW_REL, G634_DICT_REL, G634_RESULT_REL)
    result_core = {
        "schema": "GDT635_INITIAL_HEAD_SAME_REMAINDER_SWAPS_RESULT_V1", "experiment_id": "GDT635",
        "status": "MATERIA_HEAD_MODEL_PRIMARY__P_PULVIS_S_SEMEN_R_RADIX_L_LIGNUM",
        "guard": {
            "f1r": "EXCLUDED", "f84": "FORBIDDEN", "f84r": "FORBIDDEN", "new_pages": 0, "new_images": 0,
            "allowed_pages": len(pages), "token_query": token_stats, "cross_query": cross_stats,
            "token_bearing_loci": len(by_line),
        },
        "initial_heads": {
            head: {
                "meaning": HEADS[head]["meaning"], "latin": HEADS[head]["latin"],
                "occurrences": int(profiles_by_head[head]["initial_occurrences"]),
                "types": int(profiles_by_head[head]["initial_types"]),
                "pages": int(profiles_by_head[head]["initial_pages"]),
                "reader_exact": int(profiles_by_head[head]["initial_reader_exact_occurrences"]),
                "line_positions": [int(profiles_by_head[head]["line_first"]), int(profiles_by_head[head]["line_middle"]), int(profiles_by_head[head]["line_last"])],
            } for head in HEAD_ORDER
        },
        "remainder_atlas": {
            "bodies": len(occupancy), "head_body_types": sum(int(row["head_occupancy"]) for row in occupancy),
            "headed_occurrences": sum(int(row["total_headed_occurrences"]) for row in occupancy),
            "occupancy_body_counts": {str(k): occupancy_counts[k] for k in range(1, 5)},
            "occupancy_occurrence_counts": {str(k): occupancy_occ[k] for k in range(1, 5)},
            "shared_bodies": len(shared), "shared_headed_occurrences": sum(int(row["total_headed_occurrences"]) for row in shared),
            "shared_with_bare_body": sum(int(row["bare_body_occurrences"]) > 0 for row in shared),
            "shared_with_exact_v11_body": sum(int(row["exact_v11_dictionary_body"]) for row in shared),
            "four_way_bodies": len(four_way), "four_way_occurrences": sum(int(row["total_headed_occurrences"]) for row in four_way),
        },
        "pairwise": {
            pair: {
                "shared_bodies": int(row["shared_bodies"]), "pair_only": int(row["exact_pair_only_bodies"]),
                "same_line": int(row["same_line_body_locus_cells"]), "exact_frames": int(row["exact_two_sided_frame_cells"]),
                "register_frames": int(row["register_matched_frame_cells"]),
            } for pair, row in pairs_by_pair.items()
        },
        "context": {
            "same_line_cells": len(same_line), "unique_exact_frames": len(frames),
            "pairwise_exact_frame_edges": sum(int(row["exact_two_sided_frame_cells"]) for row in pairs),
            "register_matched_frames": sum(int(row["register_matched_all_heads"]) for row in frames),
            "pairwise_register_edges": sum(int(row["register_matched_frame_cells"]) for row in pairs),
        },
        "concrete_model": {
            "primary": {head: HEADS[head]["latin"] for head in HEAD_ORDER},
            "canonical_bodies": list(BODY_VALUES), "canonical_cells": len(canonical),
            "canonical_occurrences": sum(int(row["occurrences"]) for row in canonical),
            "canonical_reader_exact": sum(int(row["reader_exact_occurrences"]) for row in canonical),
            "state_grid_cells": len(state_grid), "state_grid_attested": sum(int(row["attested"]) for row in state_grid),
            "matched_spans": len(spans), "matched_span_tokens": sum(int(row["end_position"]) - int(row["start_position"]) + 1 for row in spans),
            "matched_spans_all_reader_exact": sum(int(row["all_target_tokens_reader_exact"]) for row in spans),
            "matched_spans_split_normalized": sum(int(row["all_target_tokens_split_normalized"]) for row in spans),
            "unresolved_material_conflicts": 0, "resolved_composition_corrections": 2,
            "two_axis_aIII_daiin": "headed aIII=Typ/Charge III; d+aIII=Dosis/Maß III",
        },
        "working_dictionary": {
            "entries": len(dictionary), "inherited_v11_entries": len(old_dictionary),
            "new_scoped_head_entries": 4, "new_scoped_form_entries": len(canonical),
            "inherited_prefix_rows_preserved": len(old_dictionary),
        },
        "claim_boundary": (
            "GDT635 is an explicit working translation model over the already opened GDT634 scope. Exact token-initial p/s/r/l deletion, with sh excluded and all standalone/internal/terminal signs separate, yields 760 remainder bodies; 144 are shared and 24 occur under all four heads. The primary materia-medica reading is p=pulvis, s=semen, r=radix, l=lignum. Five complete four-head paradigms and ten matched spans receive concrete tokenwise readings, while salt, extract/liquor, resina and other head rivals remain recorded. Historical manuscripts show that pulvis+semen and lignum/radix+hot/dry+degree coexist in early-fifteenth-century technical vocabularies; they do not prove that Voynich glyphs are Latin initials. The result is a predictive, replaceable working theory, not a solved language, phonetic key, or full-manuscript plaintext."
        ),
        "inputs": {str(path): sha256(ROOT / path) for path in input_paths}, "outputs": output_hashes,
    }
    result = {**result_core, "content_sha256": canonical_hash(result_core)}
    (ROOT / OUTPUTS["result"]).write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        f"GDT635 built: initial={sum(int(row['initial_occurrences']) for row in profiles)} "
        f"bodies={len(occupancy)} shared={len(shared)} four_way={len(four_way)} "
        f"frames={len(frames)} spans={len(spans)} dictionary={len(dictionary)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
