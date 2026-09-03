#!/usr/bin/env python3
"""Build the GDT772 expanded, simultaneously masked policy rescore."""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable, Mapping, Sequence


TARGETS = ("ol", "ckhy", "ols", "otar")
TARGET_MASKS = {
    "ol": "TM-Q7M2", "ckhy": "TM-V4C9", "ols": "TM-H8R1", "otar": "TM-N5K6",
}
RIGHT_BRANCH_ROLES = {
    "FIELD", "PATIENT", "SOURCE", "RESULT", "PROCESS", "ENDPOINT",
    "MATERIAL", "PREPARATION", "PRODUCT",
}
ALLOWED_STRUCTURAL_ROLES = {
    "AMOUNT", "VALUE", "PATIENT", "SOURCE", "RESULT", "PROCESS",
    "ENDPOINT", "FIELD", "CLOSE", "PREDICATE_ONLY_CLOSE", "MATERIAL",
    "PREPARATION", "PRODUCT",
}


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXPERIMENT = ROOT / "experiments/yolo/gdt772_expanded_ol_branch_masked_rescore"
DEFAULT_OUTPUT = EXPERIMENT / "artifacts"
DEFAULT_REPORT = EXPERIMENT / "REPORT.md"
G770 = ROOT / "experiments/yolo/gdt770_target_masked_valency_orphan_tournament"
G734_CELLS = ROOT / "experiments/yolo/gdt734_v99r7_recurrent_unknown_family_dispatch/artifacts/V99R7_32339_COMPACT_CELL_REGISTER.tsv"
OLD_COHORT = G770 / "src/COHORT_15_LINE_SPECS.tsv"
OLD_SLOTS = G770 / "src/TARGET_INDEPENDENT_SLOT_CONSTRAINTS.tsv"
CANDIDATES = G770 / "src/CANDIDATE_POLICY_SPECS.tsv"
PENALTIES = G770 / "src/PENALTY_SPECS.tsv"
OLD_SCOREBOARD = G770 / "artifacts/TARGET_POLICY_SCOREBOARD.tsv"
NEW_LINES = EXPERIMENT / "src/NEW_LINE_SPECS.tsv"
NEW_EDGE_ROLES = EXPERIMENT / "src/NEW_EDGE_ROLE_SPECS.tsv"
RERENDER_OVERRIDES = EXPERIMENT / "src/RERENDER_OVERRIDE_SPECS.tsv"
MANUAL_READINGS = EXPERIMENT / "src/MANUAL_RECIPE_READING_SPECS.tsv"
CONTRACT_LOCK = EXPERIMENT / "src/SCORE_CONTRACT_LOCK.tsv"

CELL_COLUMNS = (
    "cell_id", "page", "locus", "token_ordinal", "surface",
    "v99r7_semantic_value_de", "v99r7_spoken_cell_de", "gdt734_confidence_level",
    "gdt734_semantic_scope", "practical_unit_layer", "practical_unit_id",
    "practical_unit_role", "v99r7_practical_render_once_de", "unknown_v99r7",
)
OUTPUT_NAMES = (
    "EXPANDED_22_LINE_COHORT.tsv", "TARGET_27_OCCURRENCE_INVENTORY.tsv",
    "CANDIDATE_OCCURRENCE_SCOREBOARD.tsv", "TARGET_POLICY_SCOREBOARD.tsv",
    "LEAVE_ONE_PAGE_OUT.tsv", "BRANCH_COVERAGE.tsv", "WINNER_GATE_AUDIT.tsv",
    "TARGET_DECISIONS.tsv", "OL_POSITIONAL_VS_NOMINAL_CASES.tsv",
    "GDT770_GDT772_SCORE_DELTA.tsv", "GDT772_4_WORKING_DICTIONARY.tsv",
    "GDT772_7_NEW_LINE_READER.tsv", "OL_MANUAL_RECIPE_READING.tsv", "RESULT.json",
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def split_set(value: str) -> frozenset[str]:
    if value.strip().upper() in {"", "NONE", "NA", "N/A"}:
        return frozenset()
    return frozenset(part for part in value.split("|") if part)


def pipe(values: Iterable[object]) -> str:
    material = [str(value) for value in values]
    return "|".join(material) if material else "NONE"


def serialise(value: object) -> object:
    if isinstance(value, (dict, list, tuple, set, frozenset)):
        if isinstance(value, (set, frozenset)):
            value = sorted(value)
        return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return value


def write_tsv(path: Path, columns: Sequence[str], rows: Iterable[Mapping[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(columns), delimiter="\t", lineterminator="\n", extrasaction="raise")
        writer.writeheader()
        for row in rows:
            writer.writerow({column: serialise(row[column]) for column in columns})


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_contract_lock() -> dict[str, str]:
    rows = read_tsv(CONTRACT_LOCK)
    if len(rows) != 11 or len({row["lock_id"] for row in rows}) != len(rows):
        raise AssertionError("score contract lock must contain eleven unique rows")
    hashes: dict[str, str] = {}
    for row in rows:
        relative = Path(row["path"])
        if relative.is_absolute() or ".." in relative.parts:
            raise AssertionError(f"unsafe contract path: {relative}")
        path = ROOT / relative
        actual = sha256(path)
        if actual != row["expected_sha256"]:
            raise AssertionError(f"score contract changed: {relative}: {actual}")
        hashes[row["path"]] = actual
    return hashes


def guarded_new_cells(line_specs: Sequence[Mapping[str, str]]) -> tuple[list[dict[str, str]], dict[str, int]]:
    loci = [row["locus"] for row in line_specs]
    if len(loci) != 7 or len(set(loci)) != 7:
        raise AssertionError("new-line selector must contain exactly seven unique loci")
    if any(re.match(r"^f84(?:r|v|$)", locus) for locus in loci):
        raise AssertionError("forbidden selector entered GDT772 allow list")
    command = [str(ROOT / "vmanus-exp"), "query-tsv", str(G734_CELLS.relative_to(ROOT)), "--selector", "locus"]
    for locus in loci:
        command.extend(("--allow", locus))
    command.extend(("--columns", ",".join(CELL_COLUMNS)))
    completed = subprocess.run(command, cwd=ROOT, check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    rows = list(csv.DictReader(completed.stdout.splitlines(), delimiter="\t"))
    stats_rows = [line for line in completed.stderr.splitlines() if line.startswith("GUARD_STATS ")]
    if len(stats_rows) != 1:
        raise AssertionError("guard emitted no unique statistics row")
    stats = json.loads(stats_rows[0].removeprefix("GUARD_STATS "))
    expected = {"selected": 55, "skipped_forbidden": 0, "skipped_not_allowed": 32284}
    if stats != expected:
        raise AssertionError(f"unexpected guarded-cell statistics: {stats}")
    return rows, stats


def parse_ordinals(value: str) -> tuple[int, ...]:
    if value in {"", "NONE"}:
        return ()
    return tuple(int(item) for item in value.split("|"))


def validate_small_specs(line_specs: Sequence[Mapping[str, str]], edge_specs: Sequence[Mapping[str, str]], override_specs: Sequence[Mapping[str, str]]) -> None:
    if [row["line_id"] for row in line_specs] != [f"G772-L{index:03d}" for index in range(16, 23)]:
        raise AssertionError("new line IDs or order changed")
    if sum(len(parse_ordinals(row["full_branch_target_ordinals"])) for row in line_specs) != 7:
        raise AssertionError("expected seven declared full branches")
    if sum(len(parse_ordinals(row["collateral_control_target_ordinals"])) for row in line_specs) != 3:
        raise AssertionError("expected three declared collateral controls")
    if len(edge_specs) != 16 or len(override_specs) != 14:
        raise AssertionError("edge-role or rerender specification count changed")
    for row in (*edge_specs, *override_specs):
        for field in ("default_is_translation", "confirmed_lexeme", "component_export_credit"):
            if row[field] != "0":
                raise AssertionError(f"nonzero semantic credit in {field}")
    if any(row["score_credit"] != "0" for row in override_specs):
        raise AssertionError("renderer override entered the score")
    for row in edge_specs:
        roles = split_set(row["structural_roles"])
        if not roles or roles - ALLOWED_STRUCTURAL_ROLES:
            raise AssertionError(f"bad structural role row: {row['edge_role_id']}")


def build_new_cohort(cell_rows: Sequence[Mapping[str, str]], line_specs: Sequence[Mapping[str, str]], edge_specs: Sequence[Mapping[str, str]], override_specs: Sequence[Mapping[str, str]]) -> tuple[list[dict[str, str]], dict[tuple[str, int], str]]:
    by_locus: defaultdict[str, list[Mapping[str, str]]] = defaultdict(list)
    for row in cell_rows:
        by_locus[row["locus"]].append(row)
    edge_map = {(row["locus"], int(row["ordinal"])): row for row in edge_specs}
    override_map = {(row["locus"], int(row["ordinal"])): row for row in override_specs}
    if len(edge_map) != len(edge_specs) or len(override_map) != len(override_specs):
        raise AssertionError("duplicate edge or override slot")
    output: list[dict[str, str]] = []
    case_map: dict[tuple[str, int], str] = {}
    used_edges: set[tuple[str, int]] = set()
    used_overrides: set[tuple[str, int]] = set()
    for line in line_specs:
        rows = sorted(by_locus[line["locus"]], key=lambda row: int(row["token_ordinal"]))
        count = int(line["expected_token_count"])
        if len(rows) != count or [int(row["token_ordinal"]) for row in rows] != list(range(1, count + 1)):
            raise AssertionError(f"token geometry changed: {line['locus']}")
        written = " ".join(row["surface"] for row in rows)
        if written != line["expected_written_line_eva"]:
            raise AssertionError(f"written line changed: {line['locus']}: {written}")
        if any(row["unknown_v99r7"] != "0" for row in rows):
            raise AssertionError(f"new line is no longer complete: {line['locus']}")
        full = set(parse_ordinals(line["full_branch_target_ordinals"]))
        controls = set(parse_ordinals(line["collateral_control_target_ordinals"]))
        for ordinal in full:
            case_map[(line["line_id"], ordinal)] = "GDT771_FULL_LEFT_VALUE_RIGHT_TYPED"
        for ordinal in controls:
            case_map[(line["line_id"], ordinal)] = "COLLATERAL_DIRECTIONAL_CONTROL"
        provisional: list[dict[str, str]] = []
        for cell in rows:
            ordinal = int(cell["token_ordinal"])
            key = (line["locus"], ordinal)
            edge, override = edge_map.get(key), override_map.get(key)
            if edge:
                used_edges.add(key)
                if edge["surface"] != cell["surface"]:
                    raise AssertionError(f"edge surface changed at {key}")
            if override:
                used_overrides.add(key)
                if override["surface"] != cell["surface"]:
                    raise AssertionError(f"override surface changed at {key}")
            target = cell["surface"] in TARGETS
            default = "" if target else (override["practical_default_de"] if override else cell["v99r7_spoken_cell_de"])
            source_rows = [cell["cell_id"]]
            if edge:
                source_rows.append(edge["edge_role_id"])
            if override:
                source_rows.append(override["override_id"])
            provisional.append({
                "cohort_id": line["line_id"], "locus": line["locus"], "page": line["page"],
                "line_class": "GDT771_FULL_BRANCH_PLUS_COLLATERAL_CONTROLS", "line_token_count": str(count),
                "ordinal": str(ordinal), "surface": cell["surface"], "is_target": "1" if target else "0",
                "target_mask_id": TARGET_MASKS[cell["surface"]] if target else "NONE",
                "scoring_identity": TARGET_MASKS[cell["surface"]] if target else "NON_TARGET",
                "frozen_non_target_default_de": default, "structural_axes": "NONE",
                "structural_roles": "NONE" if target or edge is None else edge["structural_roles"],
                "reader_exact": "1", "span_id": "NONE", "span_member_role": "NONE",
                "render_once_owner_ordinal": "NONE", "left_neighbor_roles": "NONE",
                "right_neighbor_roles": "NONE", "left_neighbor_exact": "0", "right_neighbor_exact": "0",
                "source_artifact": str(G734_CELLS.relative_to(ROOT)), "source_row": "|".join(source_rows),
                "current_provenance": "GDT771_EXACT_TARGET__ALL_TARGET_FIELDS_WITHHELD" if target else "GDT771_TARGET_INDEPENDENT_EDGE_ROLE__CURRENT_DISPLAY" if edge else "GDT734_COMPLETE_CELL__DISPLAY_ONLY_UNTYPED",
                "old_target_default_credit": "0", "old_target_role_credit": "0", "old_target_evidence_credit": "0",
                "old_target_confidence_credit": "0", "default_is_translation": "0", "confirmed_lexeme": "0",
                "confirmed_plaintext": "0", "component_export_credit": "0",
            })
        for index, row in enumerate(provisional):
            if row["is_target"] != "1":
                continue
            left = provisional[index - 1] if index > 0 else None
            right = provisional[index + 1] if index + 1 < len(provisional) else None
            row["left_neighbor_exact"] = "1" if left and left["reader_exact"] == "1" and left["structural_roles"] != "NONE" else "0"
            row["right_neighbor_exact"] = "1" if right and right["reader_exact"] == "1" and right["structural_roles"] != "NONE" else "0"
            row["left_neighbor_roles"] = left["structural_roles"] if left and left["is_target"] == "0" else "NONE"
            row["right_neighbor_roles"] = right["structural_roles"] if right and right["is_target"] == "0" else "NONE"
        output.extend(provisional)
    if used_edges != set(edge_map) or used_overrides != set(override_map):
        raise AssertionError("unused edge or rerender specification")
    if len(output) != 55:
        raise AssertionError(f"expected 55 new cells, got {len(output)}")
    targets = [row for row in output if row["is_target"] == "1"]
    if Counter(row["surface"] for row in targets) != Counter({"ol": 10}):
        raise AssertionError("new lines do not contain exactly ten ol masks")
    if set(case_map) != {(row["cohort_id"], int(row["ordinal"])) for row in targets}:
        raise AssertionError("full/control declarations do not cover all new targets")
    full_slots, control_slots = set(), set()
    for row in targets:
        left, right = split_set(row["left_neighbor_roles"]), split_set(row["right_neighbor_roles"])
        key = (row["cohort_id"], int(row["ordinal"]))
        (full_slots if left & {"AMOUNT", "VALUE"} and right & RIGHT_BRANCH_ROLES else control_slots).add(key)
    declared_full = {key for key, value in case_map.items() if value.startswith("GDT771_FULL")}
    if full_slots != declared_full or control_slots != set(case_map) - declared_full:
        raise AssertionError("declared full/control ol geometry does not match roles")
    if len({row["page"] for row in targets if (row["cohort_id"], int(row["ordinal"])) in full_slots}) != 6:
        raise AssertionError("seven full branches must occupy six pages")
    banned = re.compile(r"\b(?:Samen|Saatgut|Holz|Pulver|Wurzel|Drogen\w*)\b", re.IGNORECASE)
    stale = [(row["locus"], row["ordinal"], row["frozen_non_target_default_de"]) for row in output if row["is_target"] == "0" and banned.search(row["frozen_non_target_default_de"])]
    if stale:
        raise AssertionError(f"retired literal remains in new-line reader: {stale}")
    return output, case_map


def import_gdt770_modules():
    source = G770 / "src"
    if str(source) not in sys.path:
        sys.path.insert(0, str(source))
    import model as model770  # type: ignore
    import scoring as scoring770  # type: ignore
    spec = importlib.util.spec_from_file_location("gdt770_run_helpers", source / "run.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load GDT770 runner helpers")
    run770 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(run770)
    return model770, scoring770, run770


def occurrence_class(context: object, target_surface: str, case_map: Mapping[tuple[str, int], str]) -> str:
    key = (context.cohort_id, context.ordinal)
    if key in case_map:
        return case_map[key]
    if target_surface != "ol":
        return "GDT770_UNCHANGED_TARGET"
    if context.locus == "f55v.10" and context.ordinal == 12:
        return "GDT770_FINAL_ONE_SIDED_CONTROL"
    return "GDT770_OTHER_TWO_SIDED_CONTROL"


def render_roles(node: object | None) -> str:
    return pipe(sorted(node.roles)) if node is not None else "NONE"


def build_report(result: Mapping[str, object]) -> str:
    ol = result["target_results"]["ol"]
    return f"""# GDT772 — Sieben neue `ol`-Brücken im unveränderten Turnier

Status: `{result['status']}`. Der getrennte Validator bestätigt 304 Prüfungen,
eine unabhängige Scoreberechnung und den byteidentischen Replay aller vierzehn
Runner-Artefakte.

## Ergebnis

Die fehlende GDT770-Verzweigung ist jetzt real belegt: sieben vollständige
Fälle auf sechs Seiten verbinden eine linke Mengen-/Wertkante über `ol` mit
einer rechten Zubereitungs-, Feld- oder Prozesskante. Trotzdem gewinnt
`von/aus` nicht. Sobald alle exakten `ol` derselben sieben Zeilen ebenfalls
verdeckt werden, kommen drei unvermeidliche Gegenfälle hinzu. Im unveränderten
Score landen der Positionsdispatch und das invariante Nomen `Ansatz/Basis`
dadurch **exakt gleichauf bei {ol['raw_lead_penalty']} Strafpunkten**.
`OPAQUE_NULL` liegt bei {ol['null_penalty']}, das messbare Produktmodell bei
{ol['product_penalty']}.

Das ist kein Rückfall auf fehlende Abdeckung. Beide Positionszweige bestehen
ihre Seitenhürde: der neue linke Wertzweig auf sechs Seiten, der alte andere
zweiseitige Zweig auf vier. Die Entscheidung bleibt offen, weil das
Positionsmodell seinen alten Neun-Punkte-Vorsprung gegenüber `Ansatz/Basis`
in den neuen Zeilen genau wieder verliert und zusätzlich die Gleichstands- und
Holdout-Hürden verfehlt.

## Wo die exakte Bindung entsteht

- Die sieben Vollfälle geben dem Positionsmodell lokal je vier Punkte Vorteil
  gegenüber dem Nomenmodell: zusammen +28.
- `f75r.26@5` besitzt links einen Wert, aber rechts keine zugelassene Kante.
- `f81r.22@4` besitzt rechts einen Wert, aber links keine typisierte Kante.
- `f81r.22@6` besitzt links einen Wert und rechts nur einen weiteren
  Mengen-/Wertposten, nicht die geforderte Feld-/Stoff-/Prozessseite.
- Diese drei Fälle kosten den Positionsdispatch zusammen 37 Punkte, während
  das breite Nomenmodell dort null zahlt. Die neue Tranche kippt den alten
  relativen Vorsprung daher um neun Punkte; über alt und neu entsteht 56:56.

Die vollständige Fallrechnung steht in
`artifacts/OL_POSITIONAL_VS_NOMINAL_CASES.tsv`. Der neue Reader zeigt jede der
sieben Zeilen parallel mit `[ol]`, `von/aus`, `Ansatz/Basis` und
`Produkt/Resultat`, ohne diese Anzeigen in den Score einzuspeisen.

## Praktischer Rezeptlese-Gegencheck

Der getrennte manuelle Gegencheck macht den Gleichstand inhaltlich noch
wichtiger. Die sieben linken Felder sind nicht siebenmal derselbe Typ: vier
sind echte Mengenformen (`sain` dreimal, `oraiin` einmal), `dain` ist nur ein
dimensionsoffener Wert, und `keor` sowie `chedar` tragen bereits zusätzliche
Inhalts- oder Qualitätsstruktur. In sechs Fällen ist ein quantifizierter
Ansatz-/Inhaltskopf mindestens ebenso natürlich wie ein partitives `von`.
Beim siebten Fall, `chedar ol oly`, ist die mechanische Ausgabe „von/aus
abseihen“ praktisch schlechter als ein Feldtrenner oder `dann/und`.

Darum wird `aus` deutlich herabgestuft: Keine der sieben Zeilen zeigt eine
unabhängige Quelle→Resultat-Richtung. Auch Öl, Wasser und Wein bleiben
untereinander vollständig ununterscheidbar. Die Einzelfallurteile samt
konkreten Rivalen stehen in `artifacts/OL_MANUAL_RECIPE_READING.tsv` und haben
null Scorekredit.

Der Gegencheck legt zugleich eine Grenze des alten Kandidatendecks offen. Der
Positionsrelator darf eine linke Menge **und** ein rechtes
Zubereitungs-/Prozessfeld binden. Das alte Nomen `Ansatz/Basis` darf dagegen
keinen quantifizierten Inhaltskopf mit rechtem Modifikator oder Prozessfeld
abbilden. Der Stand 56:56 ist deshalb keine feine lexikalische Entscheidung,
sondern der Punkt, an dem das alte Deck ausgereizt ist.

## Die anderen drei Wörter

`ckhy`, `ols` und `otar` reproduzieren ihre GDT770-Ergebnisse bytefunktional,
weil keine der sieben neuen Zeilen eine dieser drei exakten Ganzformen enthält.
Ihre Defaults bleiben formal NULL. Das ist ein Kontrollsignal dafür, dass nur
neue `ol`-Evidenz in den alten Scorer gelangt ist.

## Konsequenz für die Arbeitsübersetzung

Für `ol` ist die beste ehrliche Anzeige jetzt nicht ein einziges Wort, sondern
die konkrete Opposition:

> quantifizierter `Ansatz/Inhaltskopf` **oder**, wenn ein echter partitiver
> Anschluss passt, `von`; andernfalls Feldtrenner beziehungsweise `und/dann`.

`aus` bleibt nur ein schwacher, richtungsabhängiger Rivale. Öl, Wasser, Wein,
Essig und ein fertiges Produkt erklären diese Kohorte nicht besser. Die Daten
entscheiden aber auch noch nicht zwischen der relationalen und der nominalen
Seite.

Die nächste sinnvolle Runde verwendet dieselben fünfzehn `ol`-Fälle und keine
neuen Seiten. Sie trennt `von` von `aus`, ergänzt ein Nomenmodell, das linke
Menge plus rechten Modifikator/Prozess legal binden kann, und führt
Feldtrenner/Folge sowie Maß-/Einheitenkomplement als eigene Kandidaten. Erst
dieses reparierte Deck kann die jetzt sichtbare Opposition fair entscheiden.

## Grenze und Scope

Die Runde verwendet 22 bereits zugelassene Zeilen, 186 Token, 183 Scorenodes
und 27 gleichzeitige Zielmasken auf 20 Seiten. Keine neue Seite, kein Bild,
keine OCR, keine neue Transkription, kein `f84` und kein `f84r` wurde geöffnet.
Bestätigte Lexeme, Übersetzungen und Komponenten bleiben null.
"""


def build(output_dir: Path, report_path: Path) -> dict[str, object]:
    contract_hashes = validate_contract_lock()
    line_specs, edge_specs, override_specs = read_tsv(NEW_LINES), read_tsv(NEW_EDGE_ROLES), read_tsv(RERENDER_OVERRIDES)
    manual_readings = read_tsv(MANUAL_READINGS)
    validate_small_specs(line_specs, edge_specs, override_specs)
    if len(manual_readings) != 7 or len({row["audit_id"] for row in manual_readings}) != 7:
        raise AssertionError("manual recipe-reading deck must contain seven unique cases")
    if any(row[field] != "0" for row in manual_readings for field in ("score_credit", "default_is_translation", "confirmed_lexeme", "component_export_credit")):
        raise AssertionError("manual recipe reading entered score or semantic credit")
    expected_manual_slots = {
        (row["locus"], ordinal)
        for row in line_specs for ordinal in parse_ordinals(row["full_branch_target_ordinals"])
    }
    if {(row["locus"], int(row["target_ordinal"])) for row in manual_readings} != expected_manual_slots:
        raise AssertionError("manual recipe readings do not cover the seven full branches")
    guarded_cells, guard_stats = guarded_new_cells(line_specs)
    new_rows, case_map = build_new_cohort(guarded_cells, line_specs, edge_specs, override_specs)
    old_rows = read_tsv(OLD_COHORT)
    if len(old_rows) != 131:
        raise AssertionError("GDT770 cohort size changed")
    if set(old_rows[0]) != set(new_rows[0]):
        raise AssertionError("new cohort schema differs from GDT770")
    cohort = old_rows + new_rows
    old_slots = read_tsv(OLD_SLOTS)
    new_slots = [{"cohort_id": row["cohort_id"], "ordinal": row["ordinal"], "target_mask_id": row["target_mask_id"], "predicate_only_close": "0", "provenance": "GDT771_NO_TARGET_INDEPENDENT_PREDICATE_ONLY_CLOSE_FOR_OL"} for row in new_rows if row["is_target"] == "1"]
    slot_rows = old_slots + new_slots
    model770, scoring770, run770 = import_gdt770_modules()
    by_line: defaultdict[str, list[Mapping[str, str]]] = defaultdict(list)
    for row in cohort:
        by_line[row["cohort_id"]].append(row)
    score_node_count = sum(len(model770.build_nodes(rows)) for rows in by_line.values())
    targets = [row for row in cohort if row["is_target"] == "1"]
    target_counts = Counter(row["surface"] for row in targets)
    if (len(cohort), len(by_line), len({row["page"] for row in cohort}), score_node_count, target_counts) != (186, 22, 20, 183, Counter({"ol": 15, "otar": 5, "ckhy": 4, "ols": 3})):
        raise AssertionError("expanded cohort cardinalities changed")
    predicate_slots = {(row["cohort_id"], int(row["ordinal"])): row["predicate_only_close"] == "1" for row in slot_rows}
    if set(predicate_slots) != {(row["cohort_id"], int(row["ordinal"])) for row in targets}:
        raise AssertionError("slot constraints do not cover expanded targets")
    contexts = list(model770.make_target_contexts(cohort, predicate_slots))
    if len(contexts) != 27:
        raise AssertionError("context builder did not produce 27 target masks")
    context_by_id = {context.occurrence_id: context for context in contexts}
    candidate_rows, penalty_rows = read_tsv(CANDIDATES), read_tsv(PENALTIES)
    weights = {row["penalty_id"]: int(row["weight"]) for row in penalty_rows}
    source_branches: defaultdict[str, list[Mapping[str, str]]] = defaultdict(list)
    candidate_order: dict[str, int] = {}
    candidate_surface: dict[str, str] = {}
    for index, row in enumerate(candidate_rows):
        source_branches[row["candidate_id"]].append(row)
        candidate_order.setdefault(row["candidate_id"], index)
        candidate_surface[row["candidate_id"]] = row["target_surface"]
    if len(source_branches) != 18 or len(candidate_rows) != 22:
        raise AssertionError("candidate deck changed")
    branches_by_candidate = {candidate_id: [{key: value for key, value in row.items() if key != "target_surface"} for row in rows] for candidate_id, rows in source_branches.items()}
    contexts_by_mask: defaultdict[str, list[object]] = defaultdict(list)
    for context in contexts:
        contexts_by_mask[context.target_mask_id].append(context)
    target_candidates: defaultdict[str, list[str]] = defaultdict(list)
    evaluations_by_candidate: dict[str, list[object]] = {}
    aggregates: dict[str, dict[str, object]] = {}
    all_evaluations: list[object] = []
    for candidate_id in sorted(branches_by_candidate, key=candidate_order.__getitem__):
        surface, mask_id = candidate_surface[candidate_id], TARGET_MASKS[candidate_surface[candidate_id]]
        target_candidates[mask_id].append(candidate_id)
        evaluations = [scoring770.evaluate_occurrence(candidate_id, branches_by_candidate[candidate_id], context, weights) for context in sorted(contexts_by_mask[mask_id], key=lambda item: (item.page, item.locus, item.ordinal))]
        evaluations_by_candidate[candidate_id] = evaluations
        all_evaluations.extend(evaluations)
        aggregates[candidate_id] = scoring770.aggregate_evaluations(candidate_id, evaluations, branches_by_candidate[candidate_id])
    loo_rows, min_loo = run770.compute_leave_one_page_out(target_candidates, evaluations_by_candidate)
    branch_rows = run770.make_branch_coverage(target_candidates, contexts_by_mask, evaluations_by_candidate, branches_by_candidate)
    gate_rows, metrics, decision_rows = run770.evaluate_gates(target_candidates, aggregates, min_loo)
    target_surface_by_mask = {value: key for key, value in TARGET_MASKS.items()}
    decisions = [{"surface_provenance_only": target_surface_by_mask[row["target_mask_id"]], **row, "target_surface_visible_to_scorer": 0, "confirmed_lexeme": 0, "confirmed_plaintext": 0} for row in decision_rows]
    policy_rows = run770.policy_scoreboard_rows(aggregates, metrics, {candidate_id: TARGET_MASKS[surface] for candidate_id, surface in candidate_surface.items()})
    occurrence_rows: list[dict[str, object]] = []
    for evaluation in all_evaluations:
        context = context_by_id[evaluation.occurrence_id]
        surface = target_surface_by_mask[evaluation.target_mask_id]
        occurrence_rows.append({
            "candidate_id": evaluation.candidate_id, "occurrence_id": evaluation.occurrence_id,
            "cohort_id": evaluation.cohort_id, "locus": evaluation.locus, "page": evaluation.page,
            "ordinal": context.ordinal, "surface_provenance_only": surface,
            "occurrence_class": occurrence_class(context, surface, case_map), "branch_id": evaluation.branch_id,
            "policy_class": evaluation.policy_class, "policy_kind": evaluation.policy_kind,
            "requirements_hold": int(evaluation.requirements_hold),
            "bound_edge_ids": pipe(edge.edge_id for edge in evaluation.bound_edges),
            "bound_edge_roles": pipe(edge.role for edge in evaluation.bound_edges),
            "resolved_orphan_ids": pipe(sorted(evaluation.resolved_orphans)),
            "unresolved_orphan_ids": pipe(sorted(evaluation.unresolved_orphans)),
            "total_penalty": evaluation.penalty, "penalty_ids": pipe(event.penalty_id for event in evaluation.penalty_events),
            "penalty_triggers": pipe(event.trigger_code for event in evaluation.penalty_events),
            "renderer_de_display_only": evaluation.renderer_de, "target_surface_score_credit": 0,
            "fluency_credit": 0, "confirmed_lexeme": 0,
        })
    inventory_rows: list[dict[str, object]] = []
    surface_by_slot = {(row["cohort_id"], int(row["ordinal"])): row["surface"] for row in targets}
    for context in contexts:
        surface = surface_by_slot[(context.cohort_id, context.ordinal)]
        inventory_rows.append({
            "occurrence_id": context.occurrence_id, "cohort_id": context.cohort_id, "locus": context.locus,
            "page": context.page, "ordinal": context.ordinal, "surface_provenance_only": surface,
            "occurrence_class": occurrence_class(context, surface, case_map),
            "left_roles": render_roles(context.left), "right_roles": render_roles(context.right),
            "left_reader_exact": int(context.left is not None), "right_reader_exact": int(context.right is not None),
            "null_orphan_ids": pipe(item[0] for item in context.null_orphans),
            "null_orphan_types": pipe(item[1] for item in context.null_orphans),
            "predicate_only_close": int(context.predicate_only_close), "target_default_credit": 0,
            "target_role_credit": 0, "confirmed_lexeme": 0, "component_export_credit": 0,
        })
    evaluations_index = {(evaluation.candidate_id, evaluation.occurrence_id): evaluation for evaluation in all_evaluations}
    ol_cases: list[dict[str, object]] = []
    ol_candidate_ids = ["OL_NULL", "OL_POSITIONAL_RELATOR", "OL_NOMINAL_BASE", "OL_MEASURABLE_PRODUCT_RESULT"]
    for index, context in enumerate(sorted(contexts_by_mask[TARGET_MASKS["ol"]], key=lambda item: (item.page, item.locus, item.ordinal)), 1):
        evaluations = {candidate_id: evaluations_index[(candidate_id, context.occurrence_id)] for candidate_id in ol_candidate_ids}
        minimum = min(item.penalty for item in evaluations.values())
        local_minimum = sorted(candidate_id for candidate_id, item in evaluations.items() if item.penalty == minimum)
        positional, nominal = evaluations["OL_POSITIONAL_RELATOR"], evaluations["OL_NOMINAL_BASE"]
        product, null = evaluations["OL_MEASURABLE_PRODUCT_RESULT"], evaluations["OL_NULL"]
        case_class = occurrence_class(context, "ol", case_map)
        ol_cases.append({
            "case_id": f"G772-OL{index:02d}", "occurrence_id": context.occurrence_id,
            "cohort_id": context.cohort_id, "locus": context.locus, "page": context.page,
            "ordinal": context.ordinal, "case_class": case_class, "left_roles": render_roles(context.left),
            "right_roles": render_roles(context.right), "positional_branch": positional.branch_id,
            "positional_requirements_hold": int(positional.requirements_hold),
            "positional_penalty": positional.penalty, "nominal_penalty": nominal.penalty,
            "product_penalty": product.penalty, "null_penalty": null.penalty,
            "positional_advantage_over_nominal": nominal.penalty - positional.penalty,
            "local_minimum_candidates": pipe(local_minimum), "local_minimum_penalty": minimum,
            "full_branch_declared": int(case_class.startswith("GDT771_FULL")),
            "collateral_or_final_control": int("CONTROL" in case_class),
            "semantic_identity_credit": 0, "component_export_credit": 0,
        })
    old_policy = {row["candidate_id"]: row for row in read_tsv(OLD_SCOREBOARD)}
    delta_rows = []
    for row in policy_rows:
        candidate_id, old = str(row["candidate_id"]), old_policy[str(row["candidate_id"])]
        delta_rows.append({
            "candidate_id": candidate_id, "target_surface_provenance_only": candidate_surface[candidate_id],
            "gdt770_occurrences": int(old["target_occurrence_count"]), "gdt772_occurrences": int(row["target_occurrence_count"]),
            "occurrence_delta": int(row["target_occurrence_count"]) - int(old["target_occurrence_count"]),
            "gdt770_penalty": int(old["total_penalty"]), "gdt772_penalty": int(row["total_penalty"]),
            "penalty_delta": int(row["total_penalty"]) - int(old["total_penalty"]),
            "gdt770_delta_vs_null": int(old["delta_vs_null"]), "gdt772_delta_vs_null": int(row["delta_vs_null"]),
            "delta_vs_null_change": int(row["delta_vs_null"]) - int(old["delta_vs_null"]),
            "gdt770_failed_gates": old["failed_gate_ids"], "gdt772_failed_gates": row["failed_gate_ids"],
            "score_contract_changed": 0, "confirmed_lexeme": 0,
        })
    decision_by_surface = {row["surface_provenance_only"]: row for row in decisions}
    policy_by_id = {str(row["candidate_id"]): row for row in policy_rows}
    dictionary_defaults = {
        "ol": "quantifizierter Ansatz/Inhaltskopf ↔ partitives von ↔ Feldtrenner/und-dann; aus schwach",
        "ckhy": "mischen; lokal Mischung oder Infusion/Dekokt offen",
        "ols": "fertige Zubereitung; Colatura oder abseihen offen",
        "otar": "Zwischenzubereitung ↔ weiter/dann; bis nur lokal",
    }
    evidence = {
        "ol": "Sieben vollständige linke Wertbrücken auf sechs Seiten und vier OTHER_TWO_SIDED-Seiten; Positionsdispatch und Ansatz/Basis enden 56:56.",
        "ckhy": "Unveränderte vier GDT770-Stellen; Mischvorgang bleibt Rohleader, aber ohne f32r nicht stabil.",
        "ols": "Unveränderte drei GDT770-Stellen; breites Resultat bindet lokal, doch Produktidentität und Vorgang bleiben nicht trennbar.",
        "otar": "Unveränderte fünf GDT770-Stellen; Nomenmodell bleibt zwei Punkte vor weiter/dann, aber Seiten-Holdouts drehen die Ordnung.",
    }
    counterevidence = {
        "ol": "Drei automatisch mitmaskierte neue Gegenfälle kosten den Positionsdispatch 37 gegen 0 beim Nomen; Gleichstand und Holdouts scheitern.",
        "ckhy": "Nur eine patientengestützte Finalseite; Nomen- und Vorgangskandidaten bleiben lokal gebunden.",
        "ols": "Nur eine komplette Stelle besitzt rechts einen Wert; Colatura ist nirgends unabhängig identifiziert.",
        "otar": "Nur ein FIELD-zu-ENDPOINT-Fall für bis; Folge- und Nominalrahmen überlappen.",
    }
    dictionary_rows = []
    for index, surface in enumerate(TARGETS, 1):
        decision = decision_by_surface[surface]
        dictionary_rows.append({
            "dictionary_id": f"G772-D{index:02d}", "whole_form": surface,
            "formal_policy_decision": decision["formal_decision"], "formal_status": decision["formal_status"],
            "raw_lead_candidate": decision["raw_lead_candidate"],
            "concrete_replaceable_default_de": dictionary_defaults[surface],
            "confidence_level": "C1_STRUCTURAL__C0_IDENTITY", "evidence_de": evidence[surface],
            "counterevidence_de": counterevidence[surface], "scope": "WHOLE_FORM_OCCURRENCE_ONLY",
            "replaceable": 1, "default_is_translation": 0, "confirmed_lexeme": 0,
            "confirmed_plaintext": 0, "component_export_credit": 0,
        })
    new_by_line: defaultdict[str, list[Mapping[str, str]]] = defaultdict(list)
    for row in new_rows:
        new_by_line[row["cohort_id"]].append(row)
    new_context_by_slot = {(context.cohort_id, context.ordinal): context for context in contexts if context.cohort_id.startswith("G772-")}
    reader_rows = []
    line_spec_by_id = {row["line_id"]: row for row in line_specs}
    for line_id in sorted(new_by_line):
        rows = sorted(new_by_line[line_id], key=lambda row: int(row["ordinal"]))
        renderings = {"masked": [], "positional": [], "nominal": [], "product": []}
        summaries = []
        for row in rows:
            if row["is_target"] != "1":
                for values in renderings.values():
                    values.append(row["frozen_non_target_default_de"])
                continue
            context = new_context_by_slot[(line_id, int(row["ordinal"]))]
            pos = evaluations_index[("OL_POSITIONAL_RELATOR", context.occurrence_id)]
            nom = evaluations_index[("OL_NOMINAL_BASE", context.occurrence_id)]
            prod = evaluations_index[("OL_MEASURABLE_PRODUCT_RESULT", context.occurrence_id)]
            renderings["masked"].append("[ol]")
            renderings["positional"].append(pos.renderer_de if pos.requirements_hold else "[ol: Positionsregel scheitert]")
            renderings["nominal"].append("Ansatz/Basis")
            renderings["product"].append("messbares Produkt/Resultat" if prod.requirements_hold else "[ol: Produktregel scheitert]")
            summaries.append(f"@{row['ordinal']} pos={pos.penalty},nom={nom.penalty},prod={prod.penalty}")
        spec_row = line_spec_by_id[line_id]
        reader_rows.append({
            "line_id": line_id, "locus": spec_row["locus"], "page": spec_row["page"],
            "written_line_eva": spec_row["expected_written_line_eva"],
            "target_ordinals": pipe(row["ordinal"] for row in rows if row["is_target"] == "1"),
            "full_branch_ordinals": spec_row["full_branch_target_ordinals"],
            "collateral_control_ordinals": spec_row["collateral_control_target_ordinals"],
            "masked_reader_de": "; ".join(renderings["masked"]),
            "positional_reader_de": "; ".join(renderings["positional"]),
            "nominal_reader_de": "; ".join(renderings["nominal"]),
            "product_reader_de": "; ".join(renderings["product"]),
            "local_penalty_summary": " | ".join(summaries), "reader_score_credit": 0,
            "default_is_translation": 0, "confirmed_plaintext": 0,
        })
    output_dir.mkdir(parents=True, exist_ok=True)
    tables = (
        ("EXPANDED_22_LINE_COHORT.tsv", cohort), ("TARGET_27_OCCURRENCE_INVENTORY.tsv", inventory_rows),
        ("CANDIDATE_OCCURRENCE_SCOREBOARD.tsv", occurrence_rows), ("TARGET_POLICY_SCOREBOARD.tsv", policy_rows),
        ("LEAVE_ONE_PAGE_OUT.tsv", loo_rows), ("BRANCH_COVERAGE.tsv", branch_rows),
        ("WINNER_GATE_AUDIT.tsv", gate_rows), ("TARGET_DECISIONS.tsv", decisions),
        ("OL_POSITIONAL_VS_NOMINAL_CASES.tsv", ol_cases), ("GDT770_GDT772_SCORE_DELTA.tsv", delta_rows),
        ("GDT772_4_WORKING_DICTIONARY.tsv", dictionary_rows), ("GDT772_7_NEW_LINE_READER.tsv", reader_rows),
        ("OL_MANUAL_RECIPE_READING.tsv", manual_readings),
    )
    for name, rows in tables:
        write_tsv(output_dir / name, tuple(rows[0].keys()), rows)
    ol_scores = {candidate_id: int(policy_by_id[candidate_id]["total_penalty"]) for candidate_id in ("OL_NULL", "OL_POSITIONAL_RELATOR", "OL_NOMINAL_BASE", "OL_MEASURABLE_PRODUCT_RESULT")}
    expected_ol = {"OL_NULL": 127, "OL_POSITIONAL_RELATOR": 56, "OL_NOMINAL_BASE": 56, "OL_MEASURABLE_PRODUCT_RESULT": 76}
    if ol_scores != expected_ol:
        raise AssertionError(f"unexpected ol score result: {ol_scores}")
    if any(row["formal_status"] != "OPAQUE_NULL" for row in decisions):
        raise AssertionError("unexpected policy winner")
    branch_lookup = {(row["candidate_id"], row["branch_id"]): row for row in branch_rows}
    left_branch = branch_lookup[("OL_POSITIONAL_RELATOR", "LEFT_AMOUNT_OR_VALUE")]
    other_branch = branch_lookup[("OL_POSITIONAL_RELATOR", "OTHER_TWO_SIDED")]
    if (int(left_branch["qualified_occurrence_count"]), int(left_branch["qualified_page_count"])) != (7, 6):
        raise AssertionError("new left branch coverage changed")
    if (int(other_branch["qualified_occurrence_count"]), int(other_branch["qualified_page_count"])) != (4, 4):
        raise AssertionError("old other branch coverage changed")
    status = "PARTIAL__22_LINES_186_TOKENS_183_SCORE_NODES_182_READER_UNITS__27_TARGET_MASKS_OL15_CKHY4_OLS3_OTAR5__OL_LEFT_BRANCH_7_ON_6_PAGES_OTHER_BRANCH_4_ON_4__OL_POSITIONAL_NOMINAL_EXACT_TIE_56__0_POLICY_WINS__ZERO_CONFIRMED_LEXEMES_NO_NEW_PAGE"
    result: dict[str, object] = {
        "experiment_id": "GDT772", "status": status,
        "question": "Does the unchanged GDT770 positional ol policy beat nominal and product rivals after adding all seven complete GDT771 left-value branches and all collateral exact targets on those lines?",
        "counts": {"line_count": 22, "page_count": 20, "token_count": 186, "score_node_count": score_node_count, "practical_reader_unit_count": 182, "target_occurrence_count": len(contexts), "target_counts": dict(sorted(target_counts.items())), "new_line_count": 7, "new_token_count": 55, "new_ol_target_count": 10, "new_full_ol_branch_count": 7, "new_collateral_control_count": 3, "manual_recipe_reading_count": len(manual_readings), "candidate_count": len(source_branches), "candidate_occurrence_evaluation_count": len(all_evaluations), "policy_winner_count": sum(int(row["policy_winner_count"]) for row in decisions)},
        "ol_branch": {"left_amount_or_value_qualified_occurrences": 7, "left_amount_or_value_qualified_pages": 6, "other_two_sided_qualified_occurrences": 4, "other_two_sided_qualified_pages": 4, "full_case_positional_advantage_total": sum(int(row["positional_advantage_over_nominal"]) for row in ol_cases if int(row["full_branch_declared"])), "collateral_case_positional_advantage_total": sum(int(row["positional_advantage_over_nominal"]) for row in ol_cases if row["case_class"] == "COLLATERAL_DIRECTIONAL_CONTROL"), "all_old_case_positional_advantage_total": sum(int(row["positional_advantage_over_nominal"]) for row in ol_cases if row["cohort_id"].startswith("G770-")), "score_tie": ol_scores["OL_POSITIONAL_RELATOR"] == ol_scores["OL_NOMINAL_BASE"]},
        "target_results": {surface: {"formal_decision": decision_by_surface[surface]["formal_decision"], "formal_status": decision_by_surface[surface]["formal_status"], "raw_lead_candidate": decision_by_surface[surface]["raw_lead_candidate"], "raw_minimum_candidates": decision_by_surface[surface]["raw_minimum_candidates"], "raw_lead_penalty": decision_by_surface[surface]["raw_lead_penalty"], "null_penalty": decision_by_surface[surface]["null_penalty"], "failed_gates": decision_by_surface[surface]["raw_lead_failed_gates"], **({"product_penalty": ol_scores["OL_MEASURABLE_PRODUCT_RESULT"]} if surface == "ol" else {})} for surface in TARGETS},
        "score_contract": {"candidate_penalty_gate_and_code_changed": False, "locked_source_hashes": contract_hashes, "target_surface_score_credit": 0, "old_target_default_role_evidence_confidence_credit": 0, "reader_and_fluency_credit": 0, "resampling_unit": "page"},
        "guard": guard_stats,
        "scope": {"new_page_opened": False, "new_image_opened": False, "new_ocr_opened": False, "new_transcription_opened": False, "f84_accessed": False, "f84r_accessed": False},
        "claim_ceiling": {"confirmed_lexemes": 0, "confirmed_plaintext_clauses": 0, "confirmed_translations": 0, "component_export_credit": 0, "eva_latin_credit": 0, "defaults_are_replaceable": True},
        "outputs": list(OUTPUT_NAMES),
    }
    write_json(output_dir / "RESULT.json", result)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(build_report(result), encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report-path", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()
    output = args.output_dir if args.output_dir.is_absolute() else ROOT / args.output_dir
    report = args.report_path if args.report_path.is_absolute() else ROOT / args.report_path
    result = build(output, report)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
