#!/usr/bin/env python3
"""Build GDT666: close the 151-form V42 frontier as concrete V43 recipe cards."""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import re
import sys
import tempfile
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
BASE_REL = Path("experiments/yolo/gdt666_one_hundred_fifty_one_residual_family_completion")
ART = ROOT / BASE_REL / "artifacts"
G665 = Path("experiments/yolo/gdt665_one_hundred_forty_eight_residual_family_completion")
_spec = importlib.util.spec_from_file_location("gdt665_builder_for_gdt666", ROOT / G665 / "src/run.py")
if _spec is None or _spec.loader is None:
    raise RuntimeError("cannot load GDT665 builder")
g665 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(g665)
TOKENS_REL, CROSS_REL = g665.TOKENS_REL, g665.CROSS_REL
STATUS = "PASS_612_TARGET_POSITIONS__V43_CONCRETE_RECIPE_REGISTER"


# Replaceable exact-surface defaults. Component tags explain the current
# structural hypothesis but never dispatch a substring on their own.  The TSV
# is deliberately the sole card source so card wording can evolve without a
# second embedded dictionary silently drifting out of sync.
def read_card_specs(path: Path) -> tuple[dict[str, str], ...]:
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    expected = {"surface", "working_meaning_de", "composition", "strongest_rival_de", "family"}
    if not rows or set(rows[0]) != expected:
        raise RuntimeError("bad GDT666 CARD_SPECS.tsv columns")
    surfaces = [row["surface"] for row in rows]
    if len(rows) != 151 or len(set(surfaces)) != 151:
        raise RuntimeError("GDT666 CARD_SPECS.tsv must contain 151 unique surfaces")
    return tuple(rows)


EXACT_WHOLE_SPECS = read_card_specs(ROOT / BASE_REL / "src/CARD_SPECS.tsv")

TARGET_ORDER = tuple(row["surface"] for row in EXACT_WHOLE_SPECS)
TARGET_SURFACES = frozenset(TARGET_ORDER)
EXACT_BY_SURFACE = {row["surface"]: row for row in EXACT_WHOLE_SPECS}
CONTEXT_SCOPED_SURFACES = frozenset(surface for surface in TARGET_SURFACES if len(surface) <= 3)
ACTION_SURFACES = frozenset(
    row["surface"] for row in EXACT_WHOLE_SPECS if row["family"] == "ACTION"
)
ENTRY_SURFACES = frozenset(
    row["surface"] for row in EXACT_WHOLE_SPECS if row["family"] == "ENTRY"
)
SOLE_LEARNED_SURFACES = frozenset(
    row["surface"] for row in EXACT_WHOLE_SPECS
    if row["composition"].startswith("LEARNED_")
)
LEARNED_WHOLE_SURFACES = frozenset(
    row["surface"] for row in EXACT_WHOLE_SPECS
    if row["surface"] in SOLE_LEARNED_SURFACES
    and row["surface"] not in ACTION_SURFACES | CONTEXT_SCOPED_SURFACES
)


def parse_counts(raw: str) -> dict[str, int]:
    return {item.split("=", 1)[0]: int(item.split("=", 1)[1]) for item in raw.split()}


EXPECTED_SURFACE_COUNTS = parse_counts("""
ctharal=1 kochor=1 olkeeshy=1 olan=1 oteaiin=2 otealshey=1 otaly=11
otolkeechdy=1 eeeodaiin=1 alol=7 lkshedy=4 raraiin=4 cheodar=4 keam=2 dalchd=1
chcthey=7 dcheoty=1 chdam=10 sokal=1 otcheody=1 cheedain=2 chot=4 ysheed=1
rodam=2 ykeeochody=1 chky=15 chytshy=1 ytol=14 kch=1 qopchaiin=1 choltaiin=1
shdaiin=4 choees=1 okoiin=6 tolshy=1 ysheol=1 keeees=1 ykol=12 kcheor=4
ychor=14 qoaiin=21 oaldary=1 g=11 chcth=2 daid=1 qochol=1 cthody=13 qoos=2
yor=2 dkol=1 chm=1 ctholdy=1 deey=7 dshodar=1 chekar=7 arl=2 yshos=1
dchold=1 ochor=5 kcholqod=1 orchochor=1 chokokor=1 dchdy=8 ycheor=6 chag=1
chololy=1 chekody=1 ay=7 dalain=1 chtchy=3 qokody=8 qody=16 om=20 keesy=1
qocthedy=3 chosory=1 koddy=1 ycheoky=3 chokan=2 qockhey=14 ke=1 keeyfar=1
daiiny=3 chokor=5 chotchey=3 chotor=4 skaiiodar=1 yodaiin=2 choldar=1 qoked=7
polshy=3 koldy=4 ld=4 dlshedy=1 qokalchey=1 qopchey=9 qochy=2 olsheed=1
chcphedy=4 checthey=3 qolal=2 solkeey=3 dsheedal=1 lchor=4 ldchey=1
cheolkaiin=1 dalky=2 ykedy=18 qoke=1 qolkeshdy=1 otaldy=5 oltal=2 eey=8
scthey=1 chckhes=1 okaio=1 cheokain=3 oroiiin=1 yefaiin=1 ycheckhey=1 dshoy=1
cthd=1 dainol=1 okalol=1 cheykain=1 okalchy=3 qolky=4 ldol=2 qopchedy=31
dsholyd=1 qokeoy=2 dytar=1 qolchedy=11 qotee=1 yteeedy=1 yteeo=3 daiinls=1
acthy=1 chokar=6 chcfhy=2 qoeear=3 qoteeos=1 chotain=4 darala=1 shodaiin=21
odor=5 cholky=4 ykoldy=2 qokeol=39 kyty=1 daim=8
""")

LOW_SURFACES = frozenset(surface for surface, count in EXPECTED_SURFACE_COUNTS.items() if count == 1)
STRONG_SURFACES = frozenset(surface for surface, count in EXPECTED_SURFACE_COUNTS.items() if count >= 4)

OUTPUT_NAMES = (
    "PAGE_ALLOWLIST.tsv", "TARGET_DECISION_DECK.tsv", "ACCEPTED_WHOLE_SURFACE_DEFAULTS.tsv",
    "CONTEXT_RENDERING_CARDS.tsv", "CARD_ARCHITECTURE_SUMMARY.tsv",
    "ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv", "READER_VARIANT_AUDIT.tsv",
    "FAMILY_COMPOSITION_ATLAS.tsv", "FRONTIER_151_COMPLETIONS.tsv",
    "TARGET_LINE_TRANSLATIONS.tsv", "ROUND_COVERAGE_COUNTS.tsv",
    "NEWLY_COMPLETED_LINES.tsv", "NEWLY_EXPOSED_ONE_HOLE_LINES.tsv",
    "V43_WORKING_TOKEN_GLOSSARY.tsv", "WORKING_DICTIONARY_V43.tsv",
    "ALL_LINE_CONCRETE_COVERAGE_V43.tsv", "COMPLETE_PASSAGES_V43.tsv",
    "ONE_UNKNOWN_PASSAGES_V43.tsv", "INHERITED_OL_RENDER_REVISIONS.tsv",
    "INHERITED_SOL_RENDER_REVISIONS.tsv", "STEM_MODEL_V43.tsv", "MANUAL_PASSAGE_AUDIT.tsv",
)

LABEL_RENDER = {
    "o": "[Ansatzzeichen]", "ch": "[Trockenzeichen]", "qok": "[Heizzeichen]",
    "m": "[Handvollzeichen]", "sa": "[Saatzeichen]", "air": "[Fraktion-II-Zeichen]",
    "cheky": "[Trocken-Heiz-Zeichen]", "ykar": "[Heißfraktionszeichen]",
}
GENERIC_FILLER = re.compile(
    r"arbeitsgut|arbeitsvorgang|arbeitschritt|arbeitsschritt|arbeitsmittel|arbeitsstoff|"
    r"vorgang ausführen|gut bearbeiten|arbeitsprodukt|nimm werkzeug",
    re.I,
)
PRACTICAL_REPLACEMENTS = (
    ("Eigenschafts-/Zustands-/Materialträger; als nacktes Wort Gut/Ansatz", "Grundansatz"),
    ("Eigenschafts-/Zustands-/Materialträger", "Grundansatz"),
    ("trocken in der Mitte des Grades, abgeschlossen", "bis zur mittleren Trockenstufe gebracht"),
    ("trocken in der Mitte des Grades", "bis zur mittleren Trockenstufe"),
    ("trocken am Ende des Grades, abgeschlossen", "vollständig getrocknet"),
    ("trocken am Ende des Grades", "vollständig getrocknet"),
    ("trocken am Anfang des Grades, abgeschlossen", "angetrocknet"),
    ("trocken am Anfang des Grades", "angetrocknet"),
    ("feucht in der Mitte des Grades, abgeschlossen", "bis zur mittleren Einweichstufe gebracht"),
    ("feucht in der Mitte des Grades", "bis zur mittleren Einweichstufe"),
    ("feucht am Ende des Grades, abgeschlossen", "vollständig eingeweicht"),
    ("feucht am Ende des Grades", "vollständig eingeweicht"),
    ("feucht am Anfang des Grades", "leicht angefeuchtet"),
    ("heiß in der Mitte des Grades, abgeschlossen", "bis zur mittleren Heizstufe gebracht"),
    ("heiß in der Mitte des Grades", "bis zur mittleren Heizstufe"),
    ("heiß am Ende des Grades, abgeschlossen", "bis zur Heizendstufe gebracht"),
    ("heiß am Ende des Grades", "bis zur Heizendstufe"),
    ("heiß am Anfang des Grades, abgeschlossen", "leicht erhitzt"),
    ("heiß am Anfang des Grades", "leicht erhitzt"),
    ("kalt in der Mitte des Grades, abgeschlossen", "bis zur mittleren Kühlstufe gebracht"),
    ("kalt in der Mitte des Grades", "bis zur mittleren Kühlstufe"),
    ("kalt am Ende des Grades, abgeschlossen", "bis zur Kühlendstufe gebracht"),
    ("kalt am Ende des Grades", "bis zur Kühlendstufe"),
    ("kalt am Anfang des Grades", "leicht gekühlt"),
    ("Pflanzen-/Reproduktionsteil", "Pflanzenteil"),
    ("reproduktiver Teil", "Blüten- oder Fruchtdroge"),
    ("trocken; nominal trockenes Gut/Material", "Trockengut"),
    ("feucht; nominal feuchtes Gut/Material", "Feuchtgut"),
    ("trocken; nominal trockenes Gut", "Trockengut"),
    ("feucht; nominal feuchtes Gut", "Feuchtgut"),
    ("feuchte CTH-Materialform; im Herbal feuchtes Blatt-/Krautgut", "feuchte Krautdroge"),
    ("trockene CTH-Materialform; im Herbal trockenes Blatt-/Krautgut", "getrocknete Krautdroge"),
    ("CTH-Drogenmaterial; im Herbal Blatt-/Krautdroge", "Krautdroge"),
    ("CTH-Drogenmaterial", "Krautdroge"),
    ("CTH-Zubereitung/Ansatz, Form I", "Krautzubereitung, Form I"),
    ("Grad-/Maßwert IV", "vier Maße"),
    ("Grad-/Maßwert III", "drei Maße"),
    ("Grad-/Maßwert II", "zwei Maße"),
    ("Menge-/Klassenwert IV", "vier Teile"),
    ("Menge-/Klassenwert III", "drei Teile"),
    ("Menge-/Klassenwert II", "zwei Teile"),
    ("Menge IV", "vier Teile"),
    ("Menge III", "drei Teile"),
    ("Menge II", "zwei Teile"),
    ("Qualitätsgrad IV", "Stufe IV"),
    ("Qualitätsgrad III", "Stufe III"),
    ("Qualitätsgrad II", "Stufe II"),
    ("Rohstoffklasse I im Ansatz, heiß am Gradanfang", "Rohstoff I, leicht erhitzt im Ansatz"),
    ("Rohstoffklasse I im Ansatz, kalt am Gradanfang", "Rohstoff I, leicht gekühlt im Ansatz"),
    ("Rohstoffklasse I, feucht in der Gradmitte", "Rohstoff I bis zur mittleren Einweichstufe"),
    ("Rohstoffklasse I, heiß in der Gradmitte", "Rohstoff I bis zur mittleren Heizstufe"),
    ("Rohstoffklasse I", "Rohstoff I"),
    ("heißer Ansatz in der Mitte des Grades", "Ansatz bis zur mittleren Heizstufe"),
    ("kalter Ansatz in der Mitte des Grades, abgeschlossen", "Ansatz auf mittlerer Kühlstufe abgeschlossen"),
    ("kalter Ansatz in der Mitte des Grades", "Ansatz bis zur mittleren Kühlstufe"),
    ("kalter Ansatz am Ende des Grades, abgeschlossen", "Ansatz auf Kühlendstufe abgeschlossen"),
    ("kalter Ansatz am Ende des Grades", "Ansatz auf Kühlendstufe"),
    ("heißer Ansatz am Ende des Grades, abgeschlossen", "Ansatz auf Heizendstufe abgeschlossen"),
    ("heißer Ansatz am Ende des Grades", "Ansatz auf Heizendstufe"),
    ("heißer Ansatz am Anfang des Grades", "leicht erhitzter Ansatz"),
    ("heiß, Grad III, im Ansatzrahmen", "Ansatz auf Heizstufe III"),
    ("heißes Material [terminal-M]", "eine Maßeinheit heißer Drogenbasis"),
    ("im Herbal ", ""),
)

# These are practical render revisions only.  V42's structural tags remain
# byte-visible in its inherited glossary/dictionary; V43 translates the 19
# material descendants as O_PREP + bound L_WOOD.  Naked ``ol`` remains a
# learned exact whole, while ``oly``/``olyly`` remain actions and are excluded.
def read_ol_revision_specs(path: Path) -> tuple[dict[str, str], ...]:
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    expected = {"surface", "positions", "practical_meaning_de", "composition", "retained_rival_de"}
    if not rows or set(rows[0]) != expected:
        raise RuntimeError("bad GDT666 INHERITED_OL_REVISION_SPECS.tsv columns")
    surfaces = [row["surface"] for row in rows]
    if len(rows) != 19 or len(set(surfaces)) != 19 or sum(int(row["positions"]) for row in rows) != 256:
        raise RuntimeError("GDT666 OL revision source must contain 19 unique forms at 256 positions")
    if "ol" in surfaces or "oly" in surfaces or "olyly" in surfaces:
        raise RuntimeError("naked ol and action forms must remain outside the inherited material revisions")
    return tuple(rows)


OL_REVISION_SPECS = read_ol_revision_specs(ROOT / BASE_REL / "src/INHERITED_OL_REVISION_SPECS.tsv")
INHERITED_OL_RENDER_REVISIONS = {
    row["surface"]: (row["practical_meaning_de"], row["composition"])
    for row in OL_REVISION_SPECS
}


def read_sol_revision_specs(path: Path) -> tuple[dict[str, str], ...]:
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    expected = {"surface", "positions", "practical_meaning_de", "composition", "retained_rival_de"}
    if not rows or set(rows[0]) != expected:
        raise RuntimeError("bad GDT666 INHERITED_SOL_REVISION_SPECS.tsv columns")
    surfaces = [row["surface"] for row in rows]
    if len(rows) != 2 or len(set(surfaces)) != 2 or sum(int(row["positions"]) for row in rows) != 4:
        raise RuntimeError("GDT666 SOL revision source must contain 2 unique forms at 4 positions")
    return tuple(rows)


SOL_REVISION_SPECS = read_sol_revision_specs(ROOT / BASE_REL / "src/INHERITED_SOL_REVISION_SPECS.tsv")
INHERITED_SOL_RENDER_REVISIONS = {
    row["surface"]: (row["practical_meaning_de"], row["composition"])
    for row in SOL_REVISION_SPECS
}
INHERITED_RENDER_REVISIONS = {
    **INHERITED_OL_RENDER_REVISIONS,
    **INHERITED_SOL_RENDER_REVISIONS,
}

# GDT660 deliberately freezes one hand-written full-line rendering and ignores
# all token gloss markers at this locus.  V43 preserves that sentence but must
# revise its one inherited OL token after the legacy renderer returns.
LEGACY_FIXED_TRANSLATION_LOCI = frozenset({"f80v.21"})


def read_stem_model_specs(path: Path) -> tuple[dict[str, str], ...]:
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    expected = {"stem", "structural_role", "practical_default_de", "scope", "examples", "exclusions", "strength"}
    if not rows or set(rows[0]) != expected or len(rows) != 48:
        raise RuntimeError("GDT666 STEM_MODEL_SPECS.tsv must contain the 48-row V43 schema")
    return tuple(rows)


STEM_MODEL_SPECS = read_stem_model_specs(ROOT / BASE_REL / "src/STEM_MODEL_SPECS.tsv")


def read_manual_passage_specs(path: Path) -> tuple[dict[str, str], ...]:
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    expected = {"rank", "locus", "zl3b_line", "manual_workshop_translation_de", "notes"}
    if not rows or set(rows[0]) != expected or len(rows) != 30:
        raise RuntimeError("GDT666 MANUAL_PASSAGE_SPECS.tsv must contain the fixed 30-row schema")
    if [int(row["rank"]) for row in rows] != list(range(1, 31)):
        raise RuntimeError("GDT666 manual passage ranks must be 1..30")
    if len({row["locus"] for row in rows}) != 30:
        raise RuntimeError("GDT666 manual passage loci must be unique")
    return tuple(rows)


MANUAL_PASSAGE_SPECS = read_manual_passage_specs(ROOT / BASE_REL / "src/MANUAL_PASSAGE_SPECS.tsv")


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


def split_pipe(value: object) -> list[str]:
    return str(value).split(" | ") if str(value) else []


def parse_compact(value: object) -> list[str]:
    return [] if str(value) in {"", "NONE"} else str(value).split("|")


def position_label(ordinal: int, length: int) -> str:
    if length == 1:
        return "ONLY"
    if ordinal == 1:
        return "BOS"
    if ordinal == length:
        return "EOS"
    return "MEDIAL"


def card_type(surface: str) -> str:
    if surface in CONTEXT_SCOPED_SURFACES:
        return "CONTEXT_SCOPED_SHORT_FORM"
    if surface in SOLE_LEARNED_SURFACES:
        return "LEARNED_ACTION_WHOLE" if surface in ACTION_SURFACES else "LEARNED_WHOLE"
    if surface in ENTRY_SURFACES:
        return "ENTRY_COMPOSITE"
    return "PRODUCTIVE_COMPOUND"


def card_strength(surface: str) -> str:
    if surface in LOW_SURFACES:
        return "LOW_EXPLORATORY"
    if surface in CONTEXT_SCOPED_SURFACES:
        return "CONTEXT_READER_MERGE__FREE_DEFAULT_EXPLORATORY"
    if surface in STRONG_SURFACES:
        return "STRONG_PRACTICAL_OR_COMPOSITIONAL"
    return "MEDIUM_EXACT_WHOLE"


def align_reader_tokens(source: list[str], alternate: list[str]) -> list[tuple[str, tuple[int, ...], str]]:
    """Align one reader, preferring exact tokens and exact boundary changes."""
    n, m = len(source), len(alternate)
    cells: list[list[tuple[int, int, list[tuple[str, tuple[int, ...], str]]] | None]] = [
        [None] * (m + 1) for _ in range(n + 1)
    ]
    cells[0][0] = (0, 0, [])

    def offer(
        i: int, j: int, cost: int, steps: int,
        path: list[tuple[str, tuple[int, ...], str]],
        operation: tuple[str, tuple[int, ...], str],
    ) -> None:
        candidate = (cost, steps, [*path, operation])
        previous = cells[i][j]
        if previous is None or candidate[:2] < previous[:2]:
            cells[i][j] = candidate

    for i in range(n + 1):
        for j in range(m + 1):
            cell = cells[i][j]
            if cell is None:
                continue
            cost, steps, path = cell
            if i < n and j < m:
                offer(
                    i + 1, j + 1, cost + (0 if source[i] == alternate[j] else 10), steps + 1,
                    path, ("ONE", (i,), alternate[j]),
                )
            if i + 1 < n and j < m and source[i] + source[i + 1] == alternate[j]:
                offer(i + 2, j + 1, cost + 1, steps + 1, path, ("MERGE_2", (i, i + 1), alternate[j]))
            if i + 2 < n and j < m and source[i] + source[i + 1] + source[i + 2] == alternate[j]:
                offer(i + 3, j + 1, cost + 1, steps + 1, path, ("MERGE_3", (i, i + 1, i + 2), alternate[j]))
            if i < n and j + 1 < m and source[i] == alternate[j] + alternate[j + 1]:
                offer(i + 1, j + 2, cost + 1, steps + 1, path, ("SPLIT_2", (i,), source[i]))
            if i < n:
                offer(i + 1, j, cost + 10, steps + 1, path, ("DELETE", (i,), ""))
            if j < m:
                offer(i, j + 1, cost + 10, steps + 1, path, ("INSERT", (), alternate[j]))
    final = cells[n][m]
    if final is None:
        raise RuntimeError("reader token alignment unexpectedly has no path")
    return final[2]


def aligned_merge_evidence(
    line: list[dict[str, str]], cross_row: dict[str, str]
) -> dict[int, list[tuple[str, str, str]]]:
    """Map source-token indices to locally aligned, exact reader joins."""
    source = [row["eva"] for row in line]
    evidence: dict[int, list[tuple[str, str, str]]] = defaultdict(list)
    for reader_field, reader_name in (("it2a_clean", "IT2a"), ("rf1b_clean", "RF1b")):
        alternate = cross_row[reader_field].split()
        for operation, source_indices, merged in align_reader_tokens(source, alternate):
            if operation == "MERGE_2":
                left_index, right_index = source_indices
                if source[left_index] in CONTEXT_SCOPED_SURFACES:
                    evidence[left_index].append(("RIGHT", merged, reader_name))
                if source[right_index] in CONTEXT_SCOPED_SURFACES:
                    evidence[right_index].append(("LEFT", merged, reader_name))
            elif operation == "MERGE_3":
                left_index, middle_index, right_index = source_indices
                if source[middle_index] in CONTEXT_SCOPED_SURFACES:
                    evidence[middle_index].append(("BOTH", merged, reader_name))
    return evidence


def contextual_merge_candidate(
    surface: str, line: list[dict[str, str]], index: int,
    candidates: list[tuple[str, str, str]], known_meanings: dict[str, str],
) -> tuple[str, str, str, str, int]:
    """Select a locally aligned alternate-reader join and concrete rendering."""
    left = line[index - 1]["eva"] if index else ""
    right = line[index + 1]["eva"] if index + 1 < len(line) else ""
    direction_order = ("LEFT", "BOTH", "RIGHT") if surface == "m" else ("RIGHT", "LEFT", "BOTH")
    grouped: dict[tuple[str, str], set[str]] = defaultdict(set)
    for direction, merged, reader in candidates:
        grouped[direction, merged].add(reader)
    ordered = sorted(
        grouped,
        key=lambda item: (item[1] not in known_meanings, direction_order.index(item[0]), item[1]),
    )
    for direction, merged in ordered:
        if merged in known_meanings:
            readers = "+".join(sorted(grouped[direction, merged]))
            return direction, merged, practicalize(known_meanings[merged]), readers, 1
    if ordered:
        direction, merged = ordered[0]
        left_meaning = practicalize(known_meanings.get(left, left or "Vorstehendes"))
        right_meaning = practicalize(known_meanings.get(right, right or "Folgendes"))
        if surface == "o":
            render = (
                f"{left_meaning} im Ansatz mit {right_meaning}" if direction == "BOTH"
                else f"{left_meaning} im Ansatz" if direction == "LEFT"
                else f"Ansatz mit {right_meaning}"
            )
        elif surface == "ch":
            render = f"trockne {right_meaning}" if direction == "RIGHT" else f"trockne {left_meaning}"
        elif surface == "qok":
            render = f"erhitze {right_meaning}" if direction == "RIGHT" else f"erhitze {left_meaning}"
        elif surface == "m":
            render = f"eine Handvoll {left_meaning}" if direction != "RIGHT" else f"eine Handvoll {right_meaning}"
        elif surface == "keechy" and direction == "LEFT":
            render = f"erhitze {left_meaning} vollständig und trockne es leicht nach"
        elif surface == "dom" and direction == "LEFT":
            render = f"miss eine Handvoll {left_meaning} für den Ansatz ab"
        elif surface == "shok" and direction == "RIGHT":
            render = f"erhitze {right_meaning} als Feuchtansatz"
        elif surface == "otolaiin" and direction == "RIGHT":
            render = f"drei Teile Kaltansatz mit {right_meaning}"
        elif surface == "kesey" and direction == "LEFT":
            render = f"erhitze in {left_meaning} das Saatgut bis zur mittleren Stufe"
        else:
            render = EXACT_BY_SURFACE[surface]["working_meaning_de"]
        readers = "+".join(sorted(grouped[direction, merged]))
        return direction, merged, render, readers, 0
    return "NONE", "NONE", EXACT_BY_SURFACE[surface]["working_meaning_de"], "NONE", 0


def raw_line_set_merge_candidates(
    surface: str, line: list[dict[str, str]], index: int, cross_row: dict[str, str]
) -> list[str]:
    """Return the deliberately insufficient anywhere-on-line candidates for audit."""
    left = line[index - 1]["eva"] if index else ""
    right = line[index + 1]["eva"] if index + 1 < len(line) else ""
    alternate_tokens = set(cross_row["it2a_clean"].split()) | set(cross_row["rf1b_clean"].split())
    possible = (
        ("LEFT", left + surface if left else ""),
        ("RIGHT", surface + right if right else ""),
        ("BOTH", left + surface + right if left and right else ""),
    )
    return [f"{direction}:{merged}" for direction, merged in possible if merged and merged in alternate_tokens]


def rendering_class(
    surface: str, position: str, kind: str, merge_direction: str = "NONE",
    merge_surface: str = "NONE", merge_known: int = 0,
) -> str:
    if kind == "L" or position == "ONLY":
        return "LABEL_SIGLUM"
    if surface in CONTEXT_SCOPED_SURFACES and merge_direction != "NONE":
        known = "KNOWN" if merge_known else "NOVEL"
        return f"{surface.upper()}_READER_MERGE_{merge_direction}_{known}"
    free_classes = {
        "o": "O_FREE_ANSATZWASSER", "ch": "CH_DRY_ACTION", "qok": "QOK_HEAT_ACTION",
        "m": "M_HANDFUL", "sa": "SA_SEED_ADDITION",
    }
    if surface in free_classes:
        return free_classes[surface]
    if surface in ACTION_SURFACES:
        return f"{surface.upper()}_ACTION"
    if surface in ENTRY_SURFACES:
        return "ENTRY_WHOLE" if position == "BOS" else "REFERENCE_WHOLE"
    return "EXACT_WHOLE"


def occurrence_values(
    surface: str, position: str, kind: str, merge_direction: str, merge_surface: str,
    merge_meaning: str, merge_known: int,
) -> tuple[str, str, str]:
    klass = rendering_class(surface, position, kind, merge_direction, merge_surface, merge_known)
    default = EXACT_BY_SURFACE[surface]["working_meaning_de"]
    if klass == "LABEL_SIGLUM":
        label = LABEL_RENDER.get(surface, f"[{default}-Zeichen]")
        return label, label, klass
    if surface in CONTEXT_SCOPED_SURFACES and merge_direction != "NONE":
        return merge_meaning, merge_meaning, klass
    render = {
        "O_FREE_ANSATZWASSER": "Ansatzwasser",
        "CH_DRY_ACTION": "trockne Folgendes:",
        "QOK_HEAT_ACTION": "erhitze Folgendes:",
        "M_HANDFUL": "eine Handvoll",
        "SA_SEED_ADDITION": "gib einen Teil Saatgut hinzu",
    }.get(klass, default)
    if klass == "REFERENCE_WHOLE" and default.startswith("Eintrag: "):
        render = "hierzu: " + default.removeprefix("Eintrag: ")
    return default, render, klass


def practicalize(text: str) -> str:
    rendered = text
    for source, target in PRACTICAL_REPLACEMENTS:
        rendered = rendered.replace(source, target)
    rendered = re.sub(r"\s+", " ", rendered)
    return re.sub(r"\.{2,}", ".", rendered).replace(".;", ";").replace(":;", ":").strip()


def metrics(coverage, one_unknown, complete, glossary) -> dict[str, int]:
    return {
        "physical_lines": len(coverage),
        "known_token_positions": sum(int(row["known_tokens"]) for row in coverage),
        "unknown_token_positions": sum(int(row["unknown_tokens"]) for row in coverage),
        "complete_multi_token_lines": len(complete),
        "strict_complete_lines": sum(int(row["strict_complete"]) for row in complete),
        "one_unknown_lines": len(one_unknown),
        "strict_one_unknown_lines": sum(int(row["strict_eligible"]) for row in one_unknown),
        "working_glossary_surfaces": len(glossary),
    }


def line_translation(
    locus: str,
    line: list[dict[str, str]],
    glosses: list[str],
    y_occurrence_by_token: dict[tuple[str, int], dict[str, object]],
    inherited_target_by_token: dict[tuple[str, int], dict[str, object]],
    target_by_token: dict[tuple[str, int], dict[str, object]],
) -> str:
    """Render V43 with reader joins over the complete V42 renderer."""
    working_glosses = list(glosses)
    # GDT665's renderer only applies its positional action cards to the map it
    # receives as the current layer.  Re-promote the archived G665 rows here;
    # older G660-G664 rows remain the inherited structural layer exactly as in
    # the V42 build.
    inherited = {
        key: row for key, row in inherited_target_by_token.items()
        if not str(row.get("occurrence_id", "")).startswith("G665-")
    }
    current = {
        key: row for key, row in inherited_target_by_token.items()
        if str(row.get("occurrence_id", "")).startswith("G665-")
    }
    current.update(target_by_token)
    suppress: set[tuple[str, int]] = set()
    for key, occurrence in target_by_token.items():
        if key[0] != locus or occurrence["surface"] not in CONTEXT_SCOPED_SURFACES:
            continue
        direction = str(occurrence["reader_merge_direction"])
        index = int(occurrence["ordinal"]) - 1
        neighbor_indices = (
            (index - 1,) if direction == "LEFT" else (index + 1,) if direction == "RIGHT"
            else (index - 1, index + 1) if direction == "BOTH" else ()
        )
        for neighbor_index in neighbor_indices:
            if not 0 <= neighbor_index < len(line):
                continue
            neighbor_key = (locus, int(line[neighbor_index]["token_index"]))
            suppress.add(neighbor_key)
            working_glosses[neighbor_index] = ""
    for key in suppress:
        inherited.pop(key, None)
        current.pop(key, None)
    rendered = g665.line_translation(
        locus, line, working_glosses, y_occurrence_by_token, inherited, current
    )
    return practicalize(rendered)


def build(output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    base_art = ROOT / G665 / "artifacts"
    pages = {row["page"] for row in read_tsv(base_art / "PAGE_ALLOWLIST.tsv")}
    if len(pages) != 179 or "f1r" in pages or any(page.startswith("f84") for page in pages):
        raise RuntimeError("inherited page allow-list is not the exact safe 179-page panel")
    tokens, token_stats = g665.g664.g663.g662.g661.g659.guarded_query(
        TOKENS_REL, pages, "page,locus,token_index,eva,kind,section,language,hand"
    )
    cross, cross_stats = g665.g664.g663.g662.g661.g659.guarded_query(
        CROSS_REL, pages,
        "page,locus,all_three_present,all_present_exact,zl3b_clean,it2a_clean,rf1b_clean",
    )
    if (len(tokens), len(cross)) != (32339, 4137):
        raise RuntimeError("guarded source census drift")
    by_line: dict[str, list[dict[str, str]]] = defaultdict(list)
    tokens_by_surface: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in tokens:
        by_line[row["locus"]].append(row)
        tokens_by_surface[row["eva"]].append(row)
    for line in by_line.values():
        line.sort(key=lambda row: int(row["token_index"]))
    cross_by_locus = {row["locus"]: row for row in cross}
    if len(by_line) != 4128:
        raise RuntimeError("physical-line census drift")
    for locus, line in by_line.items():
        if locus not in cross_by_locus or " ".join(row["eva"] for row in line) != cross_by_locus[locus]["zl3b_clean"]:
            raise RuntimeError(f"guarded token/cross mismatch: {locus}")

    base_dictionary = read_tsv(base_art / "WORKING_DICTIONARY_V42.tsv")
    base_glossary_rows = read_tsv(base_art / "V42_WORKING_TOKEN_GLOSSARY.tsv")
    base_coverage = read_tsv(base_art / "ALL_LINE_CONCRETE_COVERAGE_V42.tsv")
    base_complete = read_tsv(base_art / "COMPLETE_PASSAGES_V42.tsv")
    base_one = read_tsv(base_art / "ONE_UNKNOWN_PASSAGES_V42.tsv")
    frontier = read_tsv(base_art / "NEWLY_EXPOSED_ONE_HOLE_LINES.tsv")
    dimensions = (
        len(base_dictionary), len(base_glossary_rows), len(base_coverage), len(base_complete),
        len(base_one), len(frontier),
    )
    if dimensions != (1509, 1022, 4128, 802, 313, 156):
        raise RuntimeError(f"V42 base dimensions drift: {dimensions!r}")
    frontier_order = tuple(dict.fromkeys(row["unknown_surface"] for row in frontier))
    if frontier_order != TARGET_ORDER or len(TARGET_SURFACES) != 151:
        raise RuntimeError("the 151-form frontier or fixed order drifted")
    base_glossary = {row["surface"]: row for row in base_glossary_rows}
    if any(surface in base_glossary for surface in TARGET_SURFACES):
        raise RuntimeError("a GDT666 target unexpectedly already has a V42 glossary row")
    known_meanings = {surface: row["working_meaning_de"] for surface, row in base_glossary.items()}
    known_meanings.update({row["surface"]: row["working_meaning_de"] for row in EXACT_WHOLE_SPECS})

    y_occurrences = read_tsv(
        ROOT / g665.g664.g663.g662.g661.g660.G659 / "artifacts/Y_OCCURRENCE_CENSUS.tsv"
    )
    y_occurrence_by_token = {
        (row["locus"], int(row["token_index"])): row for row in y_occurrences
    }
    inherited_target_by_token: dict[tuple[str, int], dict[str, object]] = {}
    inherited_audits = (
        ROOT / g665.g664.g663.g662.g661.G660 / "artifacts/ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv",
        ROOT / g665.g664.g663.g662.G661 / "artifacts/ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv",
        ROOT / g665.g664.g663.G662 / "artifacts/ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv",
        ROOT / g665.g664.G663 / "artifacts/ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv",
        ROOT / g665.G664 / "artifacts/ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv",
        base_art / "ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv",
    )
    for path in inherited_audits:
        for row in read_tsv(path):
            inherited_target_by_token[row["locus"], int(row["token_index"])] = row

    surface_counts = Counter(row["eva"] for row in tokens)
    observed_counts = {surface: surface_counts[surface] for surface in TARGET_ORDER}
    if observed_counts != EXPECTED_SURFACE_COUNTS or sum(observed_counts.values()) != 612:
        raise RuntimeError(f"target surface count drift: {observed_counts!r}")
    exact, normalized = g665.g664.g663.g662.g661.g660.stable_maps(tokens, cross_by_locus)

    occurrence_rows: list[dict[str, object]] = []
    target_by_token: dict[tuple[str, int], dict[str, object]] = {}
    context_counts: Counter[str] = Counter()
    contextual_merge_counts: Counter[str] = Counter()
    for locus in sorted(by_line):
        line = by_line[locus]
        words = [row["eva"] for row in line]
        local_merge_evidence = aligned_merge_evidence(line, cross_by_locus[locus])
        for index, token in enumerate(line):
            surface = token["eva"]
            if surface not in TARGET_SURFACES:
                continue
            ordinal = index + 1
            position = position_label(ordinal, len(line))
            key = (locus, int(token["token_index"]))
            merge_direction = merge_surface = "NONE"
            merge_meaning = EXACT_BY_SURFACE[surface]["working_meaning_de"]
            merge_readers, merge_known = "NONE", 0
            raw_candidates = (
                raw_line_set_merge_candidates(surface, line, index, cross_by_locus[locus])
                if surface in CONTEXT_SCOPED_SURFACES else []
            )
            merge_decision = "NOT_A_CONTEXT_SHORT_FORM"
            if surface in CONTEXT_SCOPED_SURFACES and token["kind"] != "L" and position != "ONLY":
                merge_direction, merge_surface, merge_meaning, merge_readers, merge_known = contextual_merge_candidate(
                    surface, line, index, local_merge_evidence.get(index, []), known_meanings
                )
                merge_decision = (
                    "ACCEPT_LOCAL_MINIMUM_ALIGNMENT" if merge_direction != "NONE"
                    else "REJECT_NONLOCAL_LINE_SET_ONLY" if raw_candidates
                    else "NO_EXACT_LOCAL_READER_JOIN"
                )
                contextual_merge_counts[
                    f"{surface}:{merge_direction}:{merge_surface}"
                    if merge_direction != "NONE" else f"{surface}:FREE_NO_ADJACENT_MERGE"
                ] += 1
            elif surface in CONTEXT_SCOPED_SURFACES:
                merge_decision = "NO_MERGE_LABEL_OR_ONLY"
            working_gloss, working_render, klass = occurrence_values(
                surface, position, token["kind"], merge_direction, merge_surface, merge_meaning, merge_known
            )
            item: dict[str, object] = {
                "occurrence_id": f"G666-T{len(occurrence_rows) + 1:04d}",
                "page": token["page"], "locus": locus, "token_index": token["token_index"],
                "ordinal": ordinal, "line_length": len(line), "surface": surface,
                "token_kind": token["kind"], "position": position, "section": token["section"],
                "language": token["language"], "hand": token["hand"],
                "family": EXACT_BY_SURFACE[surface]["family"], "card_type": card_type(surface),
                "scope_mode": (
                    "OCCURRENCE_SCOPED_READER_MERGE_OR_FREE_DEFAULT"
                    if surface in CONTEXT_SCOPED_SURFACES
                    else "EXACT_WHITESPACE_WHOLE_WITH_OPTIONAL_PRACTICAL_RENDER"
                ),
                "rendering_class": klass,
                "left_surface": words[index - 1] if index else "<BOS>",
                "right_surface": words[index + 1] if index + 1 < len(line) else "<EOS>",
                "reader_merge_direction": merge_direction, "reader_merge_surface": merge_surface,
                "reader_merge_readers": merge_readers, "reader_merge_known_surface": merge_known,
                "raw_line_set_candidates": "|".join(raw_candidates) if raw_candidates else "NONE",
                "reader_merge_decision": merge_decision,
                "working_gloss_de": working_gloss, "working_render_de": working_render,
                "composition": EXACT_BY_SURFACE[surface]["composition"],
                "strongest_rival_de": EXACT_BY_SURFACE[surface]["strongest_rival_de"],
                "reader_exact": exact[key], "split_normalized": normalized[key],
                "all_three_present": cross_by_locus[locus]["all_three_present"],
                "all_present_exact": cross_by_locus[locus]["all_present_exact"],
                "zl3b_line": cross_by_locus[locus]["zl3b_clean"],
                "it2a_line": cross_by_locus[locus]["it2a_clean"],
                "rf1b_line": cross_by_locus[locus]["rf1b_clean"],
            }
            occurrence_rows.append(item)
            target_by_token[key] = item
            context_counts[klass] += 1
    if len(occurrence_rows) != 612 or len(target_by_token) != 612:
        raise RuntimeError("target occurrence census drift")
    contextual_rows = [row for row in occurrence_rows if row["surface"] in CONTEXT_SCOPED_SURFACES]
    contextual_surface_counts = Counter(str(row["surface"]) for row in contextual_rows)
    expected_contextual_counts = Counter({
        surface: EXPECTED_SURFACE_COUNTS[surface] for surface in CONTEXT_SCOPED_SURFACES
    })
    if contextual_surface_counts != expected_contextual_counts:
        raise RuntimeError(f"context short-form census drift: {contextual_surface_counts!r}")

    base_by_locus = {row["locus"]: row for row in base_coverage}
    coverage_rows: list[dict[str, object]] = []
    non_target_before: list[tuple[object, ...]] = []
    non_target_after: list[tuple[object, ...]] = []
    affected_loci: set[str] = set()
    for base_row in base_coverage:
        locus = base_row["locus"]
        line = by_line[locus]
        glosses = split_pipe(base_row["token_glosses_de"])
        sources = split_pipe(base_row["gloss_sources"])
        states = split_pipe(base_row["scope_states"])
        if not (len(line) == len(glosses) == len(sources) == len(states)):
            raise RuntimeError(f"V42 token columns misalign: {locus}")
        unknown_pairs = list(zip(parse_compact(base_row["unknown_ordinals"]), parse_compact(base_row["unknown_surfaces"])))
        target_ordinals: set[str] = set()
        for index, token in enumerate(line):
            key = (locus, int(token["token_index"]))
            if key not in target_by_token:
                non_target_before.append((locus, index + 1, token["eva"], glosses[index], sources[index], states[index]))
                continue
            occurrence = target_by_token[key]
            surface = token["eva"]
            if glosses[index] != f"[{surface}:?]" or sources[index] != "OPEN" or states[index] != "UNKNOWN_SURFACE":
                raise RuntimeError(f"V42 target not open at {locus}.{index + 1}: {surface}")
            glosses[index] = str(occurrence["working_gloss_de"])
            if surface in CONTEXT_SCOPED_SURFACES:
                sources[index] = f"GDT666:{occurrence['rendering_class']}:{occurrence['reader_merge_surface']}"
                states[index] = "KNOWN_CONTEXT_LICENSED" if int(occurrence["reader_exact"]) else "READER_BOUNDARY_UNSTABLE"
            else:
                sources[index] = f"GDT666:EXACT_WHOLE:{surface}"
                states[index] = "KNOWN_EXACT_WHOLE" if int(occurrence["reader_exact"]) else "READER_BOUNDARY_UNSTABLE"
            target_ordinals.add(str(index + 1))
            affected_loci.add(locus)
        for index, token in enumerate(line):
            if (locus, int(token["token_index"])) not in target_by_token:
                non_target_after.append((locus, index + 1, token["eva"], glosses[index], sources[index], states[index]))
        unknown_pairs = [pair for pair in unknown_pairs if pair[0] not in target_ordinals]
        result = dict(base_row)
        result["known_tokens"] = int(base_row["known_tokens"]) + len(target_ordinals)
        result["context_licensed_tokens"] = states.count("KNOWN_CONTEXT_LICENSED")
        result["ambiguous_tokens"] = states.count("AMBIGUOUS_ACTIVE_RIVAL")
        result["reader_unstable_tokens"] = states.count("READER_BOUNDARY_UNSTABLE")
        result["unknown_tokens"] = len(unknown_pairs)
        result["coverage_fraction"] = f"{int(result['known_tokens']) / int(result['token_count']):.6f}"
        result["token_glosses_de"] = " | ".join(glosses)
        result["gloss_sources"] = " | ".join(sources)
        result["scope_states"] = " | ".join(states)
        result["unknown_ordinals"] = "|".join(pair[0] for pair in unknown_pairs) or "NONE"
        result["unknown_surfaces"] = "|".join(pair[1] for pair in unknown_pairs) or "NONE"
        if int(base_row["unknown_tokens"]) - len(target_ordinals) != len(unknown_pairs):
            raise RuntimeError(f"V42->V43 arithmetic drift: {locus}")
        coverage_rows.append(result)
    if non_target_before != non_target_after:
        raise RuntimeError("a non-target token projection changed")
    non_target_sha = canonical_hash(non_target_before)
    coverage_by_locus = {str(row["locus"]): row for row in coverage_rows}

    complete_rows: list[dict[str, object]] = []
    for row in coverage_rows:
        if int(row["unknown_tokens"]) or int(row["token_count"]) < 2:
            continue
        item = dict(row)
        item["strict_complete"] = int(
            int(row["ambiguous_tokens"]) == 0 and int(row["reader_unstable_tokens"]) == 0
            and int(row["all_present_exact"]) == 1
        )
        item["working_translation_de"] = line_translation(
            str(row["locus"]), by_line[str(row["locus"])], split_pipe(row["token_glosses_de"]),
            y_occurrence_by_token, inherited_target_by_token, target_by_token,
        )
        complete_rows.append(item)
    complete_rows.sort(key=lambda row: (-int(row["strict_complete"]), -int(row["token_count"]), str(row["locus"])))
    for rank, row in enumerate(complete_rows, 1):
        row["rank"] = rank

    base_one_by_locus = {row["locus"]: row for row in base_one}
    one_rows: list[dict[str, object]] = []
    for row in coverage_rows:
        if int(row["unknown_tokens"]) != 1 or int(row["known_tokens"]) < 1:
            continue
        ordinal = int(str(row["unknown_ordinals"]))
        surface = str(row["unknown_surfaces"])
        old = base_one_by_locus.get(str(row["locus"]))
        if old and old["unknown_surface"] == surface and int(old["unknown_ordinal"]) == ordinal:
            proposal, basis, strength = old["proposed_default_de"], old["proposal_basis"], old["proposal_strength"]
        else:
            proposal, basis, strength = f"[{surface}:?]", "NEWLY_EXPOSED_BY_GDT666_NO_NEW_CARD", "OPEN"
        strict = int(
            int(row["ambiguous_tokens"]) == 0 and int(row["reader_unstable_tokens"]) == 0
            and int(row["all_present_exact"]) == 1
        )
        score = int(row["known_tokens"]) * 1_000_000 + strict * 10_000 - int(row["token_count"]) * 100
        line = by_line[str(row["locus"])]
        proposed_glosses = split_pipe(row["token_glosses_de"])
        proposed_glosses[ordinal - 1] = proposal
        one_rows.append({
            "rank": 0, "score": score, "strict_eligible": strict, **row,
            "unknown_ordinal": ordinal, "unknown_surface": surface,
            "previous": "<BOS>" if ordinal == 1 else line[ordinal - 2]["eva"],
            "following": "<EOS>" if ordinal == len(line) else line[ordinal]["eva"],
            "proposed_default_de": proposal, "proposal_basis": basis, "proposal_strength": strength,
            "proposed_complete_translation_de": line_translation(
                str(row["locus"]), line, proposed_glosses, y_occurrence_by_token,
                inherited_target_by_token, target_by_token,
            ),
        })
    one_rows.sort(key=lambda row: (-int(row["score"]), str(row["locus"])))
    for rank, row in enumerate(one_rows, 1):
        row["rank"] = rank

    glossary_rows: list[dict[str, object]] = [dict(row) for row in base_glossary_rows]
    dictionary_rows: list[dict[str, object]] = [dict(row) for row in base_dictionary]
    for spec_row in EXACT_WHOLE_SPECS:
        surface = spec_row["surface"]
        glossary_rows.append({
            "surface": surface, "working_meaning_de": spec_row["working_meaning_de"],
            "source": "GDT666:CONTEXT_SHORT_DEFAULT" if surface in CONTEXT_SCOPED_SURFACES else "GDT666:EXACT_WHOLE",
            "strength": card_strength(surface),
            "scope_state": "KNOWN_CONTEXT_LICENSED" if surface in CONTEXT_SCOPED_SURFACES else "KNOWN_EXACT_WHOLE",
            "priority": 230,
        })
        dictionary_rows.append({
            "entry": f"{surface}@GDT666_DEFAULT", "kind": card_type(surface),
            "working_meaning_de": spec_row["working_meaning_de"], "composition": spec_row["composition"],
            "context_rule": (
                "visible alternate-reader join first; otherwise exact free default"
                if surface in CONTEXT_SCOPED_SURFACES
                else "only the exact whitespace-delimited surface; no substring inheritance"
            ),
            "status": "NEW_V43_PROVISIONAL_CONCRETE_RECIPE_DEFAULT",
        })
    glossary_rows.sort(key=lambda row: str(row["surface"]))
    if len(glossary_rows) != 1173:
        raise RuntimeError("V43 glossary dimension drift")

    context_cards: list[dict[str, object]] = []
    context_keys = sorted({
        (str(row["rendering_class"]), str(row["surface"]), str(row["reader_merge_surface"]), str(row["working_render_de"]))
        for row in occurrence_rows if row["rendering_class"] != "EXACT_WHOLE"
    })
    for klass, surface, merge_surface, render in context_keys:
        members = [
            row for row in occurrence_rows
            if row["rendering_class"] == klass and row["surface"] == surface
            and row["reader_merge_surface"] == merge_surface and row["working_render_de"] == render
        ]
        context_cards.append({
            "card_id": f"G666-C{len(context_cards) + 1:03d}", "rendering_class": klass,
            "surface": surface, "reader_merge_surface": merge_surface, "occurrences": len(members),
            "working_render_de": render,
            "selection_rule": "exact token and listed context; named merge requires an attested alternate-reader join",
            "semantic_effect": "practical rendering only; the structural composition remains separately visible",
        })
        dictionary_rows.append({
            "entry": f"{surface}@GDT666_{klass}_{merge_surface}", "kind": "PRACTICAL_RENDERING_CARD",
            "working_meaning_de": render, "composition": f"{klass}:{merge_surface}",
            "context_rule": "exact occurrence context; reader join where named",
            "status": "NEW_V43_CONTEXT_RENDER",
        })

    architecture_rows: list[dict[str, object]] = []
    for kind in (
        "PRODUCTIVE_COMPOUND", "ENTRY_COMPOSITE", "LEARNED_ACTION_WHOLE", "LEARNED_WHOLE",
        "CONTEXT_SCOPED_SHORT_FORM",
    ):
        surfaces = [surface for surface in TARGET_ORDER if card_type(surface) == kind]
        architecture_rows.append({
            "card_type": kind, "surface_types": len(surfaces),
            "positions": sum(EXPECTED_SURFACE_COUNTS[surface] for surface in surfaces),
            "surfaces": "|".join(surfaces),
            "dispatch_rule": (
                f"exact whole; {len(CONTEXT_SCOPED_SURFACES)} short forms additionally use "
                "attested alternate-reader joins"
            ),
        })

    base_complete_loci = {row["locus"] for row in base_complete}
    newly_completed = [dict(row) for row in complete_rows if row["locus"] not in base_complete_loci]
    newly_completed.sort(key=lambda row: str(row["locus"]))
    for rank, row in enumerate(newly_completed, 1):
        row["rank"] = rank
    base_one_loci = {row["locus"] for row in base_one}
    newly_one = [dict(row) for row in one_rows if row["locus"] not in base_one_loci]
    newly_one.sort(key=lambda row: str(row["locus"]))
    for rank, row in enumerate(newly_one, 1):
        row["rank"] = rank
        row["base_unknown_tokens"] = base_by_locus[str(row["locus"])]["unknown_tokens"]

    audit_rows: list[dict[str, object]] = []
    reader_rows: list[dict[str, object]] = []
    for occurrence in occurrence_rows:
        locus, ordinal = str(occurrence["locus"]), int(occurrence["ordinal"])
        base_row, final_row = base_by_locus[locus], coverage_by_locus[locus]
        audit_rows.append({
            **occurrence,
            "v42_gloss_de": split_pipe(base_row["token_glosses_de"])[ordinal - 1],
            "v43_gloss_de": split_pipe(final_row["token_glosses_de"])[ordinal - 1],
            "v42_scope_state": split_pipe(base_row["scope_states"])[ordinal - 1],
            "v43_scope_state": split_pipe(final_row["scope_states"])[ordinal - 1],
            "v43_working_translation_de": line_translation(
                locus, by_line[locus], split_pipe(final_row["token_glosses_de"]),
                y_occurrence_by_token, inherited_target_by_token, target_by_token,
            ),
            "exact_surface_dispatch": int(occurrence["surface"] not in CONTEXT_SCOPED_SURFACES),
            "context_or_reader_dispatch": int(occurrence["surface"] in CONTEXT_SCOPED_SURFACES),
            "substring_dispatch": 0,
        })
        reader_rows.append({
            "occurrence_id": occurrence["occurrence_id"], "page": occurrence["page"], "locus": locus,
            "ordinal": ordinal, "surface": occurrence["surface"], "position": occurrence["position"],
            "reader_exact": occurrence["reader_exact"], "split_normalized": occurrence["split_normalized"],
            "reader_merge_direction": occurrence["reader_merge_direction"],
            "reader_merge_surface": occurrence["reader_merge_surface"],
            "reader_merge_readers": occurrence["reader_merge_readers"],
            "reader_merge_known_surface": occurrence["reader_merge_known_surface"],
            "raw_line_set_candidates": occurrence["raw_line_set_candidates"],
            "reader_merge_decision": occurrence["reader_merge_decision"],
            "all_present_exact": occurrence["all_present_exact"], "zl3b_line": occurrence["zl3b_line"],
            "it2a_line": occurrence["it2a_line"], "rf1b_line": occurrence["rf1b_line"],
            "claim_boundary": "reader agreement selects boundary confidence or a short-form merge card; it does not identify plaintext",
        })
    if any(str(row["v42_gloss_de"]) != f"[{row['surface']}:?]" for row in audit_rows):
        raise RuntimeError("not every target occurrence was open in V42")
    if any(GENERIC_FILLER.search(str(row["v43_working_translation_de"])) for row in audit_rows):
        raise RuntimeError("generic work filler leaked into GDT666")
    if any("Eigenschafts-/Zustands-/Materialträger" in str(row["v43_working_translation_de"]) for row in audit_rows):
        raise RuntimeError("structural OL meta-gloss leaked into practical V43 prose")

    decision_rows: list[dict[str, object]] = []
    accepted_rows: list[dict[str, object]] = []
    for index, spec_row in enumerate(EXACT_WHOLE_SPECS, 1):
        surface = spec_row["surface"]
        members = [row for row in occurrence_rows if row["surface"] == surface]
        decision_rows.append({
            "decision_id": f"G666-D{index:03d}", "surface": surface, "family": spec_row["family"],
            "card_type": card_type(surface), "working_default_de": spec_row["working_meaning_de"],
            "composition": spec_row["composition"], "strongest_rival_de": spec_row["strongest_rival_de"],
            "occurrences": len(members), "lines": len({row["locus"] for row in members}),
            "pages": len({row["page"] for row in members}),
            "reader_exact_occurrences": sum(int(row["reader_exact"]) for row in members),
            "split_normalized_occurrences": sum(int(row["split_normalized"]) for row in members),
            "rendering_classes": "|".join(sorted({str(row["rendering_class"]) for row in members})),
            "strength": card_strength(surface), "status": "ACCEPT_V43_REPLACEABLE",
        })
        accepted_rows.append({
            "surface": surface, "working_meaning_de": spec_row["working_meaning_de"],
            "composition": spec_row["composition"], "strongest_rival_de": spec_row["strongest_rival_de"],
            "card_type": card_type(surface), "strength": card_strength(surface), "occurrences": len(members),
            "scope": "CONTEXT_SCOPED_READER_BOUNDARY" if surface in CONTEXT_SCOPED_SURFACES else "EXACT_WHITESPACE_DELIMITED_WHOLE",
            "status": "ACCEPT_V43_REPLACEABLE",
        })

    family_rows: list[dict[str, object]] = []
    for family in sorted({row["family"] for row in EXACT_WHOLE_SPECS}):
        for surface in [row["surface"] for row in EXACT_WHOLE_SPECS if row["family"] == family]:
            members = tokens_by_surface[surface]
            family_rows.append({
                "family": family, "surface": surface, "card_type": card_type(surface),
                "occurrences": len(members), "lines": len({row["locus"] for row in members}),
                "pages": len({row["page"] for row in members}),
                "working_default_de": EXACT_BY_SURFACE[surface]["working_meaning_de"],
                "composition": EXACT_BY_SURFACE[surface]["composition"],
                "claim_scope": "exact whole; composition predicts relatives only as a future explicit card",
            })

    target_line_rows: list[dict[str, object]] = []
    for locus in sorted(affected_loci):
        members = [row for row in occurrence_rows if row["locus"] == locus]
        base_row, final_row = base_by_locus[locus], coverage_by_locus[locus]
        target_line_rows.append({
            "page": final_row["page"], "locus": locus, "section": final_row["section"],
            "target_occurrences": len(members), "target_ordinals": "|".join(str(row["ordinal"]) for row in members),
            "target_surfaces": "|".join(str(row["surface"]) for row in members),
            "rendering_classes": "|".join(str(row["rendering_class"]) for row in members),
            "zl3b_line": final_row["zl3b_line"], "v42_token_glosses_de": base_row["token_glosses_de"],
            "v43_token_glosses_de": final_row["token_glosses_de"],
            "v43_working_translation_de": line_translation(
                locus, by_line[locus], split_pipe(final_row["token_glosses_de"]),
                y_occurrence_by_token, inherited_target_by_token, target_by_token,
            ),
            "v42_unknown_tokens": base_row["unknown_tokens"], "v43_unknown_tokens": final_row["unknown_tokens"],
            "v43_complete": int(int(final_row["unknown_tokens"]) == 0),
        })

    frontier_rows: list[dict[str, object]] = []
    occurrence_by_locus_ordinal = {
        (str(row["locus"]), int(row["ordinal"])): row for row in occurrence_rows
    }
    for row in frontier:
        surface, locus, ordinal = row["unknown_surface"], row["locus"], int(row["unknown_ordinal"])
        final_row = coverage_by_locus[locus]
        occurrence = occurrence_by_locus_ordinal[locus, ordinal]
        frontier_rows.append({
            "rank": row["rank"], "page": row["page"], "locus": locus, "surface": surface,
            "working_default_de": EXACT_BY_SURFACE[surface]["working_meaning_de"],
            "practical_render_de": occurrence["working_render_de"],
            "card_type": card_type(surface), "composition": EXACT_BY_SURFACE[surface]["composition"],
            "strongest_rival_de": EXACT_BY_SURFACE[surface]["strongest_rival_de"],
            "strength": card_strength(surface), "reader_merge_surface": occurrence["reader_merge_surface"],
            "zl3b_line": row["zl3b_line"], "v42_translation_de": row["proposed_complete_translation_de"],
            "v43_translation_de": line_translation(
                locus, by_line[locus], split_pipe(final_row["token_glosses_de"]),
                y_occurrence_by_token, inherited_target_by_token, target_by_token,
            ),
            "status": "COMPLETE_WITH_PROVISIONAL_CONCRETE_DEFAULT",
        })
    if len(frontier_rows) != 156 or any(f"[{row['surface']}:?]" in str(row["v43_translation_de"]) for row in frontier_rows):
        raise RuntimeError("a GDT666 frontier slot remained open in V43")

    manual_passage_rows: list[dict[str, object]] = []
    for spec_row in MANUAL_PASSAGE_SPECS:
        locus = spec_row["locus"]
        if locus not in by_line or spec_row["zl3b_line"] != cross_by_locus[locus]["zl3b_clean"]:
            raise RuntimeError(f"manual passage source drift: {locus}")
        final_row = coverage_by_locus[locus]
        if int(final_row["unknown_tokens"]) != 0:
            raise RuntimeError(f"manual passage is not V43-complete: {locus}")
        automatic = line_translation(
            locus, by_line[locus], split_pipe(final_row["token_glosses_de"]),
            y_occurrence_by_token, inherited_target_by_token, target_by_token,
        )
        if GENERIC_FILLER.search(automatic):
            raise RuntimeError(f"generic work filler leaked into manual passage: {locus}")
        manual_passage_rows.append({
            **spec_row,
            "automatic_v43_translation_de": automatic,
            "v43_unknown_tokens": final_row["unknown_tokens"],
            "comparison_scope": "manual workshop prose versus deterministic V43 renderer; neither is confirmed plaintext",
        })

    base_metrics = metrics(base_coverage, base_one, base_complete, base_glossary_rows)
    final_metrics = metrics(coverage_rows, one_rows, complete_rows, glossary_rows)
    expected_base = {
        "physical_lines": 4128, "known_token_positions": 22552, "unknown_token_positions": 9787,
        "complete_multi_token_lines": 802, "strict_complete_lines": 225,
        "one_unknown_lines": 313, "strict_one_unknown_lines": 67, "working_glossary_surfaces": 1022,
    }
    if base_metrics != expected_base:
        raise RuntimeError(f"V42 base metrics drift: {base_metrics!r}")
    round_rows = [
        {"version": "V42", "added_cards": "BASE", "dictionary_entries": len(base_dictionary), **base_metrics},
        {"version": "V43", "added_cards": f"151_DEFAULTS+{len(context_cards)}_RENDERINGS+19_OL_REVISIONS+2_SOL_REVISIONS",
         "dictionary_entries": len(dictionary_rows), **final_metrics},
    ]

    coverage_fields, complete_fields, one_fields = list(base_coverage[0]), list(base_complete[0]), list(base_one[0])
    write_tsv(output_dir / "PAGE_ALLOWLIST.tsv", [{"page": page} for page in sorted(pages)], ("page",))
    write_tsv(output_dir / "TARGET_DECISION_DECK.tsv", decision_rows, list(decision_rows[0]))
    write_tsv(output_dir / "ACCEPTED_WHOLE_SURFACE_DEFAULTS.tsv", accepted_rows, list(accepted_rows[0]))
    write_tsv(output_dir / "CONTEXT_RENDERING_CARDS.tsv", context_cards, list(context_cards[0]))
    write_tsv(output_dir / "CARD_ARCHITECTURE_SUMMARY.tsv", architecture_rows, list(architecture_rows[0]))
    write_tsv(output_dir / "ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv", audit_rows, list(audit_rows[0]))
    write_tsv(output_dir / "READER_VARIANT_AUDIT.tsv", reader_rows, list(reader_rows[0]))
    write_tsv(output_dir / "FAMILY_COMPOSITION_ATLAS.tsv", family_rows, list(family_rows[0]))
    write_tsv(output_dir / "FRONTIER_151_COMPLETIONS.tsv", frontier_rows, list(frontier_rows[0]))
    write_tsv(output_dir / "TARGET_LINE_TRANSLATIONS.tsv", target_line_rows, list(target_line_rows[0]))
    write_tsv(output_dir / "ROUND_COVERAGE_COUNTS.tsv", round_rows, list(round_rows[0]))
    write_tsv(output_dir / "NEWLY_COMPLETED_LINES.tsv", newly_completed, complete_fields)
    write_tsv(output_dir / "NEWLY_EXPOSED_ONE_HOLE_LINES.tsv", newly_one, ["base_unknown_tokens", *one_fields])
    write_tsv(output_dir / "V43_WORKING_TOKEN_GLOSSARY.tsv", glossary_rows, list(base_glossary_rows[0]))
    write_tsv(output_dir / "WORKING_DICTIONARY_V43.tsv", dictionary_rows, list(base_dictionary[0]))
    write_tsv(output_dir / "ALL_LINE_CONCRETE_COVERAGE_V43.tsv", coverage_rows, coverage_fields)
    write_tsv(output_dir / "COMPLETE_PASSAGES_V43.tsv", complete_rows, complete_fields)
    write_tsv(output_dir / "ONE_UNKNOWN_PASSAGES_V43.tsv", one_rows, one_fields)
    write_tsv(
        output_dir / "INHERITED_OL_RENDER_REVISIONS.tsv",
        [dict(row) for row in OL_REVISION_SPECS],
        ("surface", "positions", "practical_meaning_de", "composition", "retained_rival_de"),
    )
    write_tsv(
        output_dir / "INHERITED_SOL_RENDER_REVISIONS.tsv",
        [dict(row) for row in SOL_REVISION_SPECS],
        ("surface", "positions", "practical_meaning_de", "composition", "retained_rival_de"),
    )
    write_tsv(
        output_dir / "STEM_MODEL_V43.tsv",
        [dict(row) for row in STEM_MODEL_SPECS],
        ("stem", "structural_role", "practical_default_de", "scope", "examples", "exclusions", "strength"),
    )
    write_tsv(
        output_dir / "MANUAL_PASSAGE_AUDIT.tsv",
        manual_passage_rows,
        (
            "rank", "locus", "zl3b_line", "manual_workshop_translation_de", "notes",
            "automatic_v43_translation_de", "v43_unknown_tokens", "comparison_scope",
        ),
    )

    input_paths = (
        G665 / "REPORT.md", G665 / "artifacts/RESULT.json", G665 / "artifacts/PAGE_ALLOWLIST.tsv",
        G665 / "artifacts/V42_WORKING_TOKEN_GLOSSARY.tsv", G665 / "artifacts/WORKING_DICTIONARY_V42.tsv",
        G665 / "artifacts/ALL_LINE_CONCRETE_COVERAGE_V42.tsv", G665 / "artifacts/COMPLETE_PASSAGES_V42.tsv",
        G665 / "artifacts/ONE_UNKNOWN_PASSAGES_V42.tsv", G665 / "artifacts/NEWLY_EXPOSED_ONE_HOLE_LINES.tsv",
        G665 / "artifacts/ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv",
        g665.G664 / "artifacts/ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv",
        g665.g664.G663 / "artifacts/ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv",
        g665.g664.g663.G662 / "artifacts/ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv",
        g665.g664.g663.g662.G661 / "artifacts/ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv",
        g665.g664.g663.g662.g661.G660 / "artifacts/ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv",
        g665.g664.g663.g662.g661.g660.G659 / "artifacts/Y_OCCURRENCE_CENSUS.tsv",
        BASE_REL / "src/CARD_SPECS.tsv", BASE_REL / "src/INHERITED_OL_REVISION_SPECS.tsv",
        BASE_REL / "src/INHERITED_SOL_REVISION_SPECS.tsv",
        BASE_REL / "src/STEM_MODEL_SPECS.tsv",
        BASE_REL / "src/MANUAL_PASSAGE_SPECS.tsv",
        BASE_REL / "src/CARD_SPECS_RECIPE_CANDIDATE.tsv",
        BASE_REL / "src/CARD_SPECS_STEM_CANDIDATE.tsv",
        BASE_REL / "src/CARD_SPECS_READER_CANDIDATE.tsv",
        BASE_REL / "src/CARD_SPECS_HISTORICAL_CANDIDATE.tsv",
        BASE_REL / "src/HISTORICAL_CODEBOOK_ANALOG_MEMO.md",
        BASE_REL / "src/FINAL_CARD_AUDIT.md",
        BASE_REL / "src/OLY_FAMILY_AUDIT.md",
        BASE_REL / "src/G_FREE_CONTEXT_AUDIT.md",
        BASE_REL / "src/MANUAL_PASSAGE_SPECS_READER.tsv",
        TOKENS_REL, CROSS_REL,
    )
    output_paths = [output_dir / name for name in OUTPUT_NAMES]
    result_core: dict[str, object] = {
        "schema": "GDT666_ONE_HUNDRED_FIFTY_ONE_RESIDUAL_FAMILY_COMPLETION_RESULT_V1",
        "experiment_id": "GDT666", "status": STATUS,
        "guard": {
            "allowed_pages": len(pages), "f1r": "EXCLUDED_BY_EXACT_ALLOWLIST", "f84": "FORBIDDEN",
            "f84r": "FORBIDDEN", "new_pages": 0, "new_images": 0,
            "token_query": token_stats, "cross_query": cross_stats,
        },
        "targets": {
            "surface_types": len(TARGET_SURFACES), "positions": len(occurrence_rows),
            "lines": len(affected_loci), "pages": len({row["page"] for row in occurrence_rows}),
            "surface_counts": observed_counts,
            "reader_exact_positions": sum(int(row["reader_exact"]) for row in occurrence_rows),
            "split_normalized_positions": sum(int(row["split_normalized"]) for row in occurrence_rows),
            "rendering_classes": dict(sorted(context_counts.items())), "all_positions_concrete": True,
            "substring_dispatch_positions": 0,
        },
        "context_short_forms": {
            "positions": len(contextual_rows), "surface_counts": dict(sorted(contextual_surface_counts.items())),
            "reader_exact_positions": sum(int(row["reader_exact"]) for row in contextual_rows),
            "merge_positions": sum(row["reader_merge_direction"] != "NONE" for row in contextual_rows),
            "raw_line_set_candidate_positions": sum(row["raw_line_set_candidates"] != "NONE" for row in contextual_rows),
            "rejected_nonlocal_line_set_positions": sum(
                row["reader_merge_decision"] == "REJECT_NONLOCAL_LINE_SET_ONLY" for row in contextual_rows
            ),
            "merge_classes": dict(sorted(contextual_merge_counts.items())),
            "free_defaults": {
                surface: EXACT_BY_SURFACE[surface]["working_meaning_de"]
                for surface in sorted(CONTEXT_SCOPED_SURFACES)
            },
            "label_defaults": {key: value for key, value in LABEL_RENDER.items() if key in CONTEXT_SCOPED_SURFACES},
        },
        "inherited_ol_revision": {
            "surface_types": len(OL_REVISION_SPECS),
            "positions": sum(int(row["positions"]) for row in OL_REVISION_SPECS),
            "composition": "O_PREP+L_WOOD",
            "naked_ol_remains_exact_whole": True,
            "oly_and_olyly_remain_actions": True,
        },
        "inherited_sol_revision": {
            "surface_types": len(SOL_REVISION_SPECS),
            "positions": sum(int(row["positions"]) for row in SOL_REVISION_SPECS),
            "composition": "SOL_SEED_PREP",
            "salt_rival_retained": True,
        },
        "stem_model": {
            "rows": len(STEM_MODEL_SPECS),
            "structural_roles_distinct_from_german_defaults": True,
            "source": str(BASE_REL / "src/STEM_MODEL_SPECS.tsv"),
        },
        "card_synthesis": {
            "candidate_lenses": ["stem", "recipe", "passage", "historical_workshop"],
            "productive_compositions": len(TARGET_SURFACES - SOLE_LEARNED_SURFACES),
            "learned_exact_wholes": len(SOLE_LEARNED_SURFACES),
            "learned_exact_surfaces": sorted(SOLE_LEARNED_SURFACES),
            "inherited_stem_roles_reused": 47,
            "total_stem_roles": len(STEM_MODEL_SPECS),
            "new_stem_roles": 1,
            "new_stem_role": "OLY_STRAIN_ACTION",
            "historical_analogue": (
                "hybrid workshop breviary: command head plus material/process, grade/measure, "
                "and a limited learned whole vocabulary"
            ),
        },
        "manual_passages": {
            "rows": len(manual_passage_rows),
            "source_lines_exact": True,
            "v43_complete_rows": sum(int(row["v43_unknown_tokens"]) == 0 for row in manual_passage_rows),
            "manual_and_automatic_kept_distinct": True,
        },
        "architecture": {
            row["card_type"]: {"surface_types": row["surface_types"], "positions": row["positions"]}
            for row in architecture_rows
        },
        "coverage": {
            "base": base_metrics, "final": final_metrics, "affected_lines": len(affected_loci),
            "newly_completed_lines": len(newly_completed),
            "newly_completed_loci": sorted(row["locus"] for row in newly_completed),
            "newly_exposed_one_hole_lines": len(newly_one),
            "newly_exposed_one_hole_loci": sorted(row["locus"] for row in newly_one),
            "non_target_token_positions_unchanged": len(non_target_before),
            "non_target_before_sha256": non_target_sha,
            "non_target_after_sha256": canonical_hash(non_target_after),
            "non_target_exactly_unchanged": True,
        },
        "working_dictionary": {
            "v42_entries": len(base_dictionary), "v43_entries": len(dictionary_rows),
            "added_default_entries": len(EXACT_WHOLE_SPECS), "added_rendering_entries": len(context_cards),
            "v42_glossary_surfaces": len(base_glossary_rows), "v43_glossary_surfaces": len(glossary_rows),
        },
        "frontier": {"source_rows": len(frontier), "completed_rows": len(frontier_rows), "unfilled_target_slots": 0},
        "determinism_contract": {
            "builder_supports_artifact_dir_cli": True, "exact_whole_dispatch_requires_token_equality": True,
            "reader_merge_dispatch_requires_attested_alternate_token": True,
            "replay_files": [str(BASE_REL / "artifacts" / name) for name in (*OUTPUT_NAMES, "RESULT.json")],
        },
        "claim_boundary": (
            "Exploratory replaceable concrete defaults for 151 V42 residual surfaces at 612 inherited positions. "
            f"The final synthesis uses {len(TARGET_SURFACES - SOLE_LEARNED_SURFACES)} productive compounds "
            f"and {len(SOLE_LEARNED_SURFACES)} learned exact wholes. {len(CONTEXT_SCOPED_SURFACES)} "
            "boundary-sensitive short forms use a local "
            "alternate-reader join when visibly attested and their exact free default otherwise; all other new cards dispatch "
            "only on exact whitespace-delimited surfaces. Nineteen inherited material forms retain their O_PREP+L_WOOD practical renderer at 256 positions, "
            "while naked ol stays a learned exact whole and oly/olyly stay actions. Two inherited sol forms are revised "
            "from salt to the manuscript-internal sol=seed model at four positions. Practical German renderers do not "
            "alter the structural glossary. No confirmed plaintext, language, phonetics, exact plant "
            "identity, disease, new page, image, f1r, f84 or f84r is asserted."
        ),
        "inputs": {str(path): sha256(ROOT / path) for path in input_paths},
        "outputs": {str(BASE_REL / "artifacts" / path.name): sha256(path) for path in output_paths},
    }
    result = {**result_core, "content_sha256": canonical_hash(result_core)}
    (output_dir / "RESULT.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-dir", type=Path, default=ART)
    args = parser.parse_args(argv)
    result = build(args.artifact_dir)
    if args.artifact_dir.resolve() == ART.resolve():
        with tempfile.TemporaryDirectory(prefix="gdt666_replay_") as directory:
            replay_dir = Path(directory)
            replay_result = build(replay_dir)
            if replay_result != result:
                raise RuntimeError("tempdir RESULT replay differs")
            for name in (*OUTPUT_NAMES, "RESULT.json"):
                if (ART / name).read_bytes() != (replay_dir / name).read_bytes():
                    raise RuntimeError(f"tempdir replay differs: {name}")
    print(
        f"GDT666 built: targets={result['targets']['positions']} surfaces=151 "
        f"known={result['coverage']['final']['known_token_positions']} "
        f"complete={result['coverage']['final']['complete_multi_token_lines']} "
        f"one_hole={result['coverage']['final']['one_unknown_lines']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
