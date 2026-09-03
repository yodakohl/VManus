#!/usr/bin/env python3
"""Build GDT775's complete-right-word renderer and predecessor-slot audit."""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import io
import json
import math
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from types import ModuleType
from typing import Iterable, Mapping, Sequence

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt775_ol_right_complement_slot_test"
SRC, ART = EXP / "src", EXP / "artifacts"
REPORT = EXP / "REPORT.md"
G774 = ROOT / "experiments/yolo/gdt774_ol_376_contextual_transfer/artifacts/OL_376_TRANSFER_ATLAS.tsv"
G734 = ROOT / "experiments/yolo/gdt734_v99r7_recurrent_unknown_family_dispatch/artifacts/V99R7_1606_COMPLETE_WORD_CONFIDENCE.tsv"
G762_STATES = ROOT / "experiments/yolo/gdt762_moist_medium_candidate_discrimination/src/STATE_PAIR_PRIORS.tsv"
G737_CANDIDATES = ROOT / "experiments/yolo/gdt737_held_body_record_role_transfer/artifacts/HELD_BODY_WORKING_CANDIDATES.tsv"
G769_CORE = ROOT / "experiments/yolo/gdt769_liquid_process_role_identity_dispatch/src/core_atlas.py"
G735_HISTORY = ROOT / "experiments/yolo/gdt735_historical_semantic_bridge_atlas/src/HISTORICAL_SOURCE_REGISTRY.tsv"
CROSS = ROOT / "transcription/voynich_cross_transcription_lines.tsv"
FALLBACK = "Ansatz-/Zubereitungsposten"
HISTORICAL_IDS = ("HSR008", "HSR010", "HSR012", "HSR013", "HSR017")
BOUNDARY_SURFACES = frozenset({"cheey", "kaiin", "oiin"})

OUTPUT_NAMES = [
    "OL_327_RIGHT_COMPLEMENT_ATLAS.tsv",
    "RIGHT_COMPLEMENT_SURFACE_CENSUS.tsv",
    "RIGHT_COMPLEMENT_13_ROLE_REGISTRY.tsv",
    "SLOT_ONLY_EXTENSION_AUDIT.tsv",
    "EXACT_FRAME_REPETITION.tsv",
    "PREDECESSOR_ANCHOR_DECK.tsv",
    "ANCHOR_PREDECESSOR_EDGE_ATLAS.tsv",
    "PREDECESSOR_VECTOR_COMPARISON.tsv",
    "PREDECESSOR_SURFACE_SIMILARITY.tsv",
    "PREDECESSOR_FOLIO_HOLDOUT.tsv",
    "PREDECESSOR_TARGET_DROP_AUDIT.tsv",
    "CROSS_READER_BOUNDARY_AUDIT.tsv",
    "HISTORICAL_CONSTRUCTION_COMPARATORS.tsv",
    "RIGHT_COMPLEMENT_MODEL_SCORE.tsv",
    "GDT775_376_RENDERER.tsv",
    "GDT775_WORKING_DICTIONARY.tsv",
    "GDT775_GDT388_RELATION_PACKET.tsv",
    "GDT775_RELATION_EDGE_CROSSWALK.tsv",
    "RELATION_PACKET_INTAKE.json",
    "RESULT.json",
]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def serialise(value: object) -> object:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, float):
        return f"{value:.9f}"
    return value


def write_tsv(path: Path, rows: Iterable[Mapping[str, object]], fields: Sequence[str]) -> None:
    material = list(rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fields), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in material:
            writer.writerow({field: serialise(row.get(field, "")) for field in fields})


def write_json(path: Path, value: Mapping[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_locks() -> int:
    rows = read_tsv(SRC / "SOURCE_LOCK.tsv")
    for row in rows:
        relative = Path(row["path"])
        assert not relative.is_absolute() and ".." not in relative.parts
        actual = sha256(ROOT / relative)
        assert actual == row["expected_sha256"], f"source changed: {relative}: {actual}"
    return len(rows)


def load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def physical_folio(page: str) -> str:
    if page.startswith("fRos"):
        return "fRos"
    match = re.match(r"^(f\d+)", page)
    assert match is not None, page
    return match.group(1)


def guarded_cross(pages: Iterable[str]) -> list[dict[str, str]]:
    columns = "page,locus,all_three_present,zl3b_clean,it2a_clean,rf1b_clean"
    command = [str(ROOT / "vmanus-exp"), "query-tsv", str(CROSS.relative_to(ROOT)),
               "--selector", "page", "--columns", columns]
    for page in sorted(set(pages)):
        command.extend(["--allow", page])
    done = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=True)
    assert "GUARD_STATS" in done.stderr
    return list(csv.DictReader(io.StringIO(done.stdout), delimiter="\t"))


def neighbor(row: Mapping[str, str], context: object, offset: int) -> tuple[str, int, bool]:
    line = context.by_line[row["locus"]]
    index = int(row["ordinal"]) - 1 + offset
    if not 0 <= index < len(line):
        return "NONE", 0, False
    token = line[index]
    exact = bool(context.exact[(row["locus"], int(token["token_index"]))])
    return str(token["eva"]), index + 1, exact


def cosine(first: Counter[str], second: Counter[str]) -> float:
    keys = set(first) | set(second)
    numerator = sum(float(first[key]) * float(second[key]) for key in keys)
    left = math.sqrt(sum(float(value) ** 2 for value in first.values()))
    right = math.sqrt(sum(float(value) ** 2 for value in second.values()))
    return numerator / (left * right) if left and right else 0.0


def exact_bigrams(environment: Mapping[str, object]) -> list[dict[str, object]]:
    context = environment["context"]
    rows: list[dict[str, object]] = []
    for locus in sorted(context.by_line):
        line = context.by_line[locus]
        for index in range(len(line) - 1):
            left, right = line[index], line[index + 1]
            if not context.exact[(locus, int(left["token_index"]))]:
                continue
            if not context.exact[(locus, int(right["token_index"]))]:
                continue
            page = str(left["page"])
            rows.append({
                "page": page, "physical_folio": physical_folio(page), "locus": locus,
                "section": left["section"], "language": left["language"], "hand": left["hand"],
                "predecessor_ordinal": index + 1, "right_ordinal": index + 2,
                "predecessor_surface": left["eva"], "right_surface": right["eva"],
                "predecessor_line_position": "FIRST" if index == 0 else "MIDDLE",
            })
    return rows


def mean_surface_vector(edges: Sequence[Mapping[str, object]], surfaces: Sequence[str]) -> Counter[str]:
    totals = Counter(str(row["predecessor_surface"]) for row in edges)
    output: Counter[str] = Counter()
    for surface in surfaces:
        assert totals[surface]
        for row in edges:
            if row["predecessor_surface"] == surface:
                output[str(row["right_surface"])] += 1 / totals[surface] / len(surfaces)
    return output


def boundary_mode(text: str, right: str) -> str:
    tokens = text.split()
    separated = sum(tokens[i] == "ol" and tokens[i + 1] == right for i in range(len(tokens) - 1))
    fused = sum(token == "ol" + right for token in tokens)
    if separated == 1 and fused == 0:
        return "SEPARATED_EXACT"
    if separated == 0 and fused == 1:
        return "FUSED_EXACT"
    if separated == 0 and fused == 0:
        return "NO_EXACT_PAIR_FORM"
    return "AMBIGUOUS_MULTIPLE_FORMS"


def make_packet(
    target_edges: Sequence[Mapping[str, object]], anchor_edges: Sequence[Mapping[str, object]]
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    material = [("TARGET_SLOT", row) for row in target_edges]
    material += [("ANCHOR_SLOT", row) for row in anchor_edges]
    material.sort(key=lambda item: (str(item[1]["page"]), str(item[1]["locus"]), int(item[1]["predecessor_ordinal"]), item[0]))
    rows: list[dict[str, object]] = []
    crosswalk: list[dict[str, object]] = []
    for number, (batch, edge) in enumerate(material, 1):
        locus = str(edge["locus"])
        left, right = int(edge["predecessor_ordinal"]), int(edge["right_ordinal"])
        rows.append({
            "edge_id": f"G775-E{number:04d}", "batch_id": f"GDT775_{batch}",
            "page": edge["page"], "physical_folio": edge["physical_folio"],
            "diagram_unit_id": f"LINE:{locus}", "pivot_visual_id": f"TOKEN:{locus}:{left}",
            "pivot_locus": f"{locus}@{left}", "target_visual_id": f"TOKEN:{locus}:{right}",
            "target_locus": f"{locus}@{right}", "relation_type": "NEXT_TOKEN",
            "direction_basis": "TRANSCRIPTION_ORDER_ONLY", "ownership_basis": "NONVISUAL_TEXT_ADJACENCY",
            "geometry_only_selection": "FALSE", "source_manifest_id": "GDT769",
            "page_crop_sha256": "NONE", "pivot_crop_sha256": "NONE", "target_crop_sha256": "NONE",
            "source_aware_localizer": "GDT775_RUNNER", "relation_reviewer": "GDT775_VALIDATOR",
            "relation_confidence": "EXPLORATORY", "ambiguity_state": "UNREVIEWED_TEXT_RELATION",
            "formal_access_state": "SEALED_NOT_ACCESSED", "fold_assignment": "NONE",
            "eligibility_status": "INELIGIBLE_EXPLORATORY_TEXT_RELATION",
        })
        crosswalk.append({
            "edge_id": f"G775-E{number:04d}", "batch_id": f"GDT775_{batch}",
            "source_row_id": edge.get("target_occurrence_id", f"ANCHOR:{locus}@{left}"),
            "page": edge["page"], "physical_folio": edge["physical_folio"], "locus": locus,
            "predecessor_ordinal": left, "right_ordinal": right,
            "predecessor_surface": edge["predecessor_surface"], "right_surface": edge["right_surface"],
            "score_eligible": 0, "component_export_credit": 0,
        })
    return rows, crosswalk


def build_report(result: Mapping[str, object]) -> str:
    family = result["right_family"]
    renderer = result["renderer"]
    pred = result["predecessor"]
    boundary = result["boundary"]
    return f"""# GDT775 — `ol` plus vollständiges rechtes Ganzwort

Status: `{result['status']}`.

## Konkreter Fortschritt

GDT775 ersetzt an **{family['selected_occurrences']}** bisher generischen
`ol`-Stellen den Platzhalter durch eine konkrete Gesamtphrase. Davon bilden
{family['primary_occurrences']} den wiederkehrenden Kern und
{family['extension_occurrences']} eine markierte Familienerweiterung. Die
Durchsatzfassung ergänzt {family['slot_only_occurrences']} zweifolige
Ganzwort-Leads. Damit steigen die automatischen konkreten Ausgaben von 49 auf
**{renderer['throughput_contextual']}**, während die generischen Fallbacks von
327 auf **{renderer['throughput_fallback']}** fallen.

Beispiele: `ol chedy` → **„Ansatz; mittlere Trockenstufe erreicht“**,
`ol shedy` → **„Ansatz; mittlere Feuchtstufe erreicht“**, `ol aiin` →
**„Ansatz, Menge III“**, `ol kaiin` → **„Ansatz: heiß, Grad III“** und
`ol oiin` → **„Ansatz in Zubereitungsform III“**. Der Renderer konsumiert
jeweils den ganzen Span `ol X`; er erfindet keine Bedeutung für EVA-Teilstrings.

## Was die Lesung trägt — und was nicht

Unter {pred['novel_exact_right']} sauberen exakt-rechten Fallbacks ähnelt die
Rechtsfolgerverteilung der autorisierten Mischgruppe aus Inhalts-/Recordköpfen,
Messfeld und Überschriften stärker als vollständigen Feld-/Formeloperatoren.
`NOMINAL_HEAD` ist dabei nur ein interner Kurzname, keine upstream bestätigte
Goldklasse. Im nur nach Oberflächenzahl balancierten 6+6-Deck
lauten die Cosinuswerte
{pred['core_nominal_cosine']:.6f} gegen {pred['core_operator_cosine']:.6f}; im
8+8-Deck {pred['expanded_nominal_cosine']:.6f} gegen
{pred['expanded_operator_cosine']:.6f}. Das 8+8-Deck erweitert das 6+6-Deck
und ist keine unabhängige Replikation. Eine zweite Rechnung gewichtet jede
Ankeroberfläche gleich, damit das häufige `chor` nicht allein entscheidet.

Dieser Vorsprung ist ein **positionskonfundierter Lean**, keine Rollenlösung:
{pred['target_middle_edges']}/{pred['novel_exact_right']} Zielkanten und
{pred['core_nominal_middle_edges']}/{pred['core_nominal_edges']} nominale
Kernkanten sind medial, aber nur {pred['core_operator_middle_edges']}/
{pred['core_operator_edges']} Operatorkanten. Die 110 Leave-one-folio-Zeilen
sind 55 physische Folios mal zwei verschachtelte Decks und daher
Stabilitätssensitivitäten, keine 110 unabhängigen oder prädiktiven Holdouts.

Die 13 Ganzwörter erscheinen reader-exakt {family['right_exact']} Mal rechts
von `ol`, aber nur {family['left_exact']} Mal links davon. Weil die Familie als
rechte Komplementfamilie zusammengestellt wurde, ist dieses Verhältnis nur
selektionsbewusste Beschreibung, keine unabhängige Evidenz. Bei `cheey`, `kaiin`
und `oiin` zeigen {boundary['fusion_variants']} von {boundary['audited_pairs']}
Stellen eine einseitige fusionierte Alternativlesung (`olX`). Alle drei liegen
jedoch außerhalb der reader-exakten ausgewählten Spannen; die
{boundary['selected_audited_pairs']} ausgewählten Auditfälle bleiben in allen
drei Lesungen getrennt. Die Fusionen zeigen daher nur lokale
Segmentierungsunsicherheit und **keine** positive Bindungsevidenz. ZL3b, IT2a
und RF1b sind drei Lesungen desselben Manuskripts, keine unabhängigen Zeugen.

Auch der gepoolte nominale Vorsprung lizenziert nicht alle 66 Fälle: nur
{family['individual_nominal_tokens']} Tokens aus
{family['individual_nominal_surfaces']} Ganzwörtern haben individuell einen
stabilen nominalen Slot-Lead; {family['individual_uninformative_tokens']} Tokens
sind uninformativ und die {family['individual_operator_tokens']} `kaiin`-Tokens
lehnen operatorartig. Noch deutlicher ist der Drop-Test: ohne `daiin` kippt
das equalized 6+6-Deck zum Operator und das 8+8-Deck schrumpft auf fast Gleichstand;
ohne die ganze 13er-Familie kippen beide Decks. Der globale Lean ist damit eine
Diagnostik, keine Lizenzquelle für den Renderer.

Drei ausgewählte Spannen stehen unmittelbar nach einem weiteren `ol`. Sie
bleiben für den explorativen Durchsatz sichtbar, tragen aber occurrence-lokal
`C0_ADJACENT_OL_COLLISION`; insbesondere `ol ol olaiin` ist Gegenbeleg und
nicht Bestätigung. `daiin` (fünf Familienspannen) und `dain` (zwei
Durchsatzspannen) sind ausdrücklich neue Scope-Extrapolationen, nicht der
Export bereits global erlaubter Karten.

## Grenze und nächste Route

Die konkrete Substanz des Ansatzes bleibt offen; Wasser, Wein und Öl werden
nicht ausgewählt. HSR008/010/012/013/017 zeigen nur eine zeitnahe Architektur
aus Materia-/Präparatekopf plus Qualität, Grad, Form oder Dosis. Sie liefern
keine Voynich-Wortidentität. `Ansatz` bleibt ein austauschbarer Arbeitsrenderer.

Von den 327 alten Fallbacks sind in der Durchsatzfassung noch
{renderer['throughput_fallback']} offen. Als Nächstes prüft ein separates
Folgeexperiment die bereits lokalisierten medialen H4/H3-Feldformen positions- und
registergematcht; parallel dürfen die 33 wiederkehrenden rechten
Ganzwortklassen als ausdrücklich heuristischer Durchsatz sortiert werden.
Danach bekommen die häufigsten bislang bedeutungslosen rechten Ganzwörter
selbst konkrete Kandidaten.
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifacts-dir", type=Path, default=ART)
    parser.add_argument("--report-path", type=Path, default=REPORT)
    args = parser.parse_args()
    artifacts = args.artifacts_dir if args.artifacts_dir.is_absolute() else ROOT / args.artifacts_dir
    report_path = args.report_path if args.report_path.is_absolute() else ROOT / args.report_path
    artifacts.mkdir(parents=True, exist_ok=True)
    lock_count = verify_locks()

    ol_rows = read_tsv(G774)
    assert len(ol_rows) == 376 and all(row["surface"] == "ol" for row in ol_rows)
    assert not any(row["page"].startswith("f84") for row in ol_rows)
    core = load_module("gdt769_for_gdt775", G769_CORE)
    _g764, environment = core.load_guarded_environment(ROOT)
    assert dict(environment["guard"]) == {"selected": 4137, "skipped_forbidden": 98, "skipped_not_allowed": 1150}
    context = environment["context"]

    family_specs = read_tsv(SRC / "RIGHT_COMPLEMENT_SPECS.tsv")
    extension_specs = read_tsv(SRC / "SLOT_ONLY_EXTENSION_SPECS.tsv")
    anchor_specs = read_tsv(SRC / "PREDECESSOR_CONTROL_SPECS.tsv")
    assert len(family_specs) == 13 and len({row["surface"] for row in family_specs}) == 13
    assert len(extension_specs) == 4 and len(anchor_specs) == 16
    assert all(row["component_export_credit"] == "0" for row in family_specs + extension_specs + anchor_specs)
    family_by = {row["surface"]: row for row in family_specs}
    extension_by = {row["surface"]: row for row in extension_specs}

    cards: dict[str, dict[str, str]] = {}
    g734_rows = read_tsv(G734)
    for authored in family_specs + extension_specs:
        matches = [row for row in g734_rows if row["surface"] == authored["surface"]
                   and row["v99r7_spoken_default_de"] == authored["expected_whole_default_de"]
                   and row["working_model_level"] == authored["expected_whole_level"]]
        assert len(matches) == 1, (authored["surface"], len(matches))
        cards[authored["surface"]] = matches[0]

    state_by_surface: dict[str, dict[str, str]] = {}
    for prior in read_tsv(G762_STATES):
        for side in ("dry", "moist"):
            surface = prior[f"{side}_surface"]
            state_by_surface[surface] = {
                "state_pair_id": prior["pair_id"],
                "state_pair_role": prior["pair_role"],
                "state_prior_candidate_de": prior[f"{side}_working_candidate_de"],
                "state_prior_confidence": prior["working_confidence"],
                "state_prior_counterevidence": prior["counterevidence"],
            }
    assert {surface: state_by_surface[surface]["state_pair_id"] for surface in
            ("chy", "chey", "cheey", "chdy", "chedy", "sheey", "shedy")} == {
        "chy": "SP02", "chey": "SP03", "cheey": "SP04", "chdy": "SP05",
        "chedy": "SP06", "sheey": "SP04", "shedy": "SP06",
    }
    later_olaiin_rows = [row for row in read_tsv(G737_CANDIDATES) if row["body"] == "olaiin"]
    assert len(later_olaiin_rows) == 1
    later_olaiin = later_olaiin_rows[0]
    assert later_olaiin["concrete_body_role_de"] == "Materialträger: Wert III"
    assert "OLD_ABSOLUTE_NUMBER_UNSUPPORTED" in later_olaiin["counterevidence"]

    fallback = [row for row in ol_rows if row["automatic_contextual"] == "0"]
    clean = [row for row in fallback if row["any_direct_signature"] == "0"
             and row["hybrid_contextual"] == "0"]
    assert len(fallback) == 327 and len(clean) == 305
    clean_ids = {row["target_occurrence_id"] for row in clean}

    atlas_rows: list[dict[str, object]] = []
    target_all: list[dict[str, object]] = []
    target_clean: list[dict[str, object]] = []
    for row in fallback:
        left, _left_ord, left_exact = neighbor(row, context, -1)
        right, right_ord, right_exact = neighbor(row, context, 1)
        novel = row["target_occurrence_id"] in clean_ids
        family = family_by.get(right) if novel and right_exact else None
        extension = extension_by.get(right) if novel and right_exact else None
        selected = family or extension
        branch = "RIGHT_COMPLETE_13_FAMILY" if family else "SLOT_ONLY_WHOLE_EXTENSION" if extension else "GENERIC_NOMINAL_FALLBACK"
        atlas_rows.append({
            "target_occurrence_id": row["target_occurrence_id"], "page": row["page"],
            "physical_folio": row["physical_folio"], "locus": row["locus"],
            "section": row["section"], "language": row["language"], "hand": row["hand"],
            "ordinal": row["ordinal"], "left_surface": left, "left_reader_exact": int(left_exact),
            "right_surface": right, "right_ordinal": right_ord, "right_reader_exact": int(right_exact),
            "automatic_contextual": row["automatic_contextual"],
            "any_direct_signature": row["any_direct_signature"],
            "calibration_case_id": row["calibration_case_id"],
            "hybrid_contextual": row["hybrid_contextual"],
            "no_direct_signature": int(row["any_direct_signature"] == "0"),
            "not_calibration_case": int(row["calibration_case_id"] == "NONE"),
            "novel_305_member": int(novel), "dispatch_branch": branch,
            "register_id": f"{row['section']}|{row['language']}|{row['hand']}",
            "family_tier": family["family_tier"] if family else "NONE",
            "semantic_class": selected["semantic_class"] if selected else "NONE",
            "portable_span_de": selected["portable_span_de"] if selected else FALLBACK,
            "fluent_span_de": selected["fluent_span_de"] if selected else FALLBACK,
            "construction_confidence": selected["construction_confidence"] if selected else "C0_CONTEXT_UNRESOLVED",
            "scope_status": selected["scope_status"] if selected else "NONE",
            "specific_counterevidence_de": selected["specific_counterevidence_de"] if selected else "NONE",
            "adjacent_left_ol_collision": int(left == "ol"),
            "written_line_eva": row["written_line_eva"], "default_is_translation": 0,
            "confirmed_lexeme": 0, "confirmed_plaintext": 0, "component_export_credit": 0,
        })
        if right_exact:
            edge = {"target_occurrence_id": row["target_occurrence_id"],
                    "page": row["page"], "physical_folio": row["physical_folio"],
                    "locus": row["locus"], "section": row["section"], "language": row["language"],
                    "hand": row["hand"], "predecessor_ordinal": int(row["ordinal"]),
                    "right_ordinal": right_ord, "predecessor_surface": "ol", "right_surface": right,
                    "predecessor_line_position": row["line_position"]}
            target_all.append(edge)
            if novel:
                target_clean.append(edge)
    assert len(target_all) == 221 and len(target_clean) == 203
    family_rows = [row for row in atlas_rows if row["dispatch_branch"] == "RIGHT_COMPLETE_13_FAMILY"]
    primary_rows = [row for row in family_rows if row["family_tier"] == "PRIMARY"]
    family_extension = [row for row in family_rows if row["family_tier"] == "EXTENSION"]
    slot_rows = [row for row in atlas_rows if row["dispatch_branch"] == "SLOT_ONLY_WHOLE_EXTENSION"]
    assert (len(family_rows), len(primary_rows), len(family_extension), len(slot_rows)) == (66, 57, 9, 8)
    family_selected_ids = {str(row["target_occurrence_id"]) for row in family_rows}

    bigrams = exact_bigrams(environment)
    universe = {
        "edges": len(bigrams),
        "pair_types": len({(row["predecessor_surface"], row["right_surface"]) for row in bigrams}),
        "predecessor_surfaces": len({row["predecessor_surface"] for row in bigrams}),
        "right_surfaces": len({row["right_surface"] for row in bigrams}),
        "loci": len({row["locus"] for row in bigrams}),
        "physical_folios": len({row["physical_folio"] for row in bigrams}),
    }
    assert universe == {"edges": 16657, "pair_types": 14395, "predecessor_surfaces": 3488,
                        "right_surfaces": 3393, "loci": 3584, "physical_folios": 90}

    decks: dict[str, dict[str, list[str]]] = {}
    for deck in ("CORE_6_PLUS_6", "EXPANDED_8_PLUS_8"):
        decks[deck] = {}
        for anchor_class in ("NOMINAL_HEAD", "FIELD_OPERATOR"):
            decks[deck][anchor_class] = [
                row["surface"] for row in anchor_specs if row["anchor_class"] == anchor_class
                and (deck == "EXPANDED_8_PLUS_8" or row["deck_membership"] == "CORE_AND_EXPANDED")
            ]
    assert all(len(surfaces) == 6 for surfaces in decks["CORE_6_PLUS_6"].values())
    assert all(len(surfaces) == 8 for surfaces in decks["EXPANDED_8_PLUS_8"].values())
    expanded_surfaces = set(decks["EXPANDED_8_PLUS_8"]["NOMINAL_HEAD"] + decks["EXPANDED_8_PLUS_8"]["FIELD_OPERATOR"])
    anchor_edges = [row for row in bigrams if row["predecessor_surface"] in expanded_surfaces]
    anchor_counts = Counter(str(row["predecessor_surface"]) for row in anchor_edges)
    assert dict(anchor_counts) == {
        "chor": 141, "shor": 63, "cthy": 49, "dair": 39, "ofchy": 3, "schor": 2,
        "pol": 9, "polaiin": 7, "ychor": 13, "ycheol": 7, "ychol": 8, "dcheol": 4,
        "qokchor": 5, "ycheor": 5, "pchor": 9, "tshol": 5,
    }

    target_vectors = {
        "ALL_FALLBACK_221": Counter(str(row["right_surface"]) for row in target_all),
        "NOVEL_203": Counter(str(row["right_surface"]) for row in target_clean),
    }
    target_edge_sets = {"ALL_FALLBACK_221": target_all, "NOVEL_203": target_clean}
    vector_rows: list[dict[str, object]] = []
    similarity_rows: list[dict[str, object]] = []
    vector_index: dict[tuple[str, str], dict[str, object]] = {}
    for target_name, target_vector in target_vectors.items():
        for deck, classes in decks.items():
            pooled: dict[str, Counter[str]] = {}
            equalized: dict[str, Counter[str]] = {}
            capacities: dict[str, int] = {}
            positions: dict[str, Counter[str]] = {}
            for anchor_class, surfaces in classes.items():
                selected = [row for row in anchor_edges if row["predecessor_surface"] in surfaces]
                capacities[anchor_class] = len(selected)
                positions[anchor_class] = Counter(str(row["predecessor_line_position"]) for row in selected)
                pooled[anchor_class] = Counter(str(row["right_surface"]) for row in selected)
                equalized[anchor_class] = mean_surface_vector(selected, surfaces)
                for surface in surfaces:
                    own = Counter(str(row["right_surface"]) for row in selected if row["predecessor_surface"] == surface)
                    similarity_rows.append({
                        "target_cohort": target_name, "deck": deck, "anchor_class": anchor_class,
                        "anchor_surface": surface, "outgoing_edges": sum(own.values()),
                        "right_types": len(own), "cosine_to_target": cosine(target_vector, own),
                    })
            nraw, oraw = cosine(target_vector, pooled["NOMINAL_HEAD"]), cosine(target_vector, pooled["FIELD_OPERATOR"])
            neq, oeq = cosine(target_vector, equalized["NOMINAL_HEAD"]), cosine(target_vector, equalized["FIELD_OPERATOR"])
            target_positions = Counter(str(row["predecessor_line_position"]) for row in target_edge_sets[target_name])
            current = {
                "target_cohort": target_name, "deck": deck, "target_edges": sum(target_vector.values()),
                "target_right_types": len(target_vector), "nominal_edges": capacities["NOMINAL_HEAD"],
                "operator_edges": capacities["FIELD_OPERATOR"], "nominal_raw_cosine": nraw,
                "operator_raw_cosine": oraw, "raw_cosine_delta_nominal_minus_operator": nraw - oraw,
                "nominal_surface_equalized_cosine": neq, "operator_surface_equalized_cosine": oeq,
                "surface_equalized_delta_nominal_minus_operator": neq - oeq,
                "target_first_edges": target_positions["FIRST"], "target_middle_edges": target_positions["MIDDLE"],
                "nominal_first_edges": positions["NOMINAL_HEAD"]["FIRST"], "nominal_middle_edges": positions["NOMINAL_HEAD"]["MIDDLE"],
                "operator_first_edges": positions["FIELD_OPERATOR"]["FIRST"], "operator_middle_edges": positions["FIELD_OPERATOR"]["MIDDLE"],
                "position_confound_status": "SEVERE_FIRST_MIDDLE_CLASS_IMBALANCE",
                "raw_winner": "NOMINAL_HEAD" if nraw > oraw else "FIELD_OPERATOR",
                "surface_equalized_winner": "NOMINAL_HEAD" if neq > oeq else "FIELD_OPERATOR",
            }
            vector_rows.append(current)
            vector_index[(target_name, deck)] = current
    for target_name in target_vectors:
        assert vector_index[(target_name, "CORE_6_PLUS_6")]["nominal_edges"] == 297
        assert vector_index[(target_name, "CORE_6_PLUS_6")]["operator_edges"] == 42
        assert vector_index[(target_name, "EXPANDED_8_PLUS_8")]["nominal_edges"] == 313
        assert vector_index[(target_name, "EXPANDED_8_PLUS_8")]["operator_edges"] == 56
        assert all(vector_index[(target_name, deck)][kind] == "NOMINAL_HEAD"
                   for deck in decks for kind in ("raw_winner", "surface_equalized_winner"))

    holdouts: list[dict[str, object]] = []
    for folio in sorted({str(row["physical_folio"]) for row in target_clean}):
        target = Counter(str(row["right_surface"]) for row in target_clean if row["physical_folio"] != folio)
        for deck, classes in decks.items():
            scores: dict[str, float] = {}
            for anchor_class, surfaces in classes.items():
                control = Counter(str(row["right_surface"]) for row in anchor_edges
                                  if row["physical_folio"] != folio and row["predecessor_surface"] in surfaces)
                scores[anchor_class] = cosine(target, control)
            holdouts.append({
                "held_physical_folio": folio, "deck": deck, "remaining_target_edges": sum(target.values()),
                "nominal_raw_cosine": scores["NOMINAL_HEAD"], "operator_raw_cosine": scores["FIELD_OPERATOR"],
                "delta_nominal_minus_operator": scores["NOMINAL_HEAD"] - scores["FIELD_OPERATOR"],
                "winner": "NOMINAL_HEAD" if scores["NOMINAL_HEAD"] > scores["FIELD_OPERATOR"] else "FIELD_OPERATOR",
            })

    # Influence audit: remove selected RHS types only from the target vector
    # while leaving both comparison decks fixed. This asks whether the pooled
    # direction survives without the very words later selected for rendering.
    drop_scenarios = {
        "BASELINE": frozenset(),
        "DROP_DAIIN": frozenset({"daiin"}),
        "DROP_DAIIN_AND_AIIN": frozenset({"daiin", "aiin"}),
        "DROP_FIXED_13_FAMILY": frozenset(family_by),
    }
    target_drop_rows: list[dict[str, object]] = []
    for scenario, dropped in drop_scenarios.items():
        retained = [row for row in target_clean if str(row["right_surface"]) not in dropped]
        target_vector = Counter(str(row["right_surface"]) for row in retained)
        for deck, classes in decks.items():
            scores: dict[str, float] = {}
            for anchor_class, surfaces in classes.items():
                scores[anchor_class] = cosine(target_vector, mean_surface_vector(anchor_edges, surfaces))
            target_drop_rows.append({
                "scenario": scenario, "deck": deck,
                "dropped_right_surfaces": "|".join(sorted(dropped)) if dropped else "NONE",
                "dropped_target_tokens": len(target_clean) - len(retained),
                "remaining_target_edges": len(retained), "remaining_right_types": len(target_vector),
                "nominal_surface_equalized_cosine": scores["NOMINAL_HEAD"],
                "operator_surface_equalized_cosine": scores["FIELD_OPERATOR"],
                "delta_nominal_minus_operator": scores["NOMINAL_HEAD"] - scores["FIELD_OPERATOR"],
                "winner": "NOMINAL_HEAD" if scores["NOMINAL_HEAD"] > scores["FIELD_OPERATOR"] else "FIELD_OPERATOR",
                "interpretation": "TARGET_INFLUENCE_DIAGNOSTIC__CONTROL_DECKS_FIXED",
            })
    drop_index = {(row["scenario"], row["deck"]): row for row in target_drop_rows}
    assert drop_index[("BASELINE", "CORE_6_PLUS_6")]["winner"] == "NOMINAL_HEAD"
    assert drop_index[("DROP_DAIIN", "CORE_6_PLUS_6")]["winner"] == "FIELD_OPERATOR"
    assert drop_index[("DROP_FIXED_13_FAMILY", "CORE_6_PLUS_6")]["winner"] == "FIELD_OPERATOR"
    assert drop_index[("DROP_FIXED_13_FAMILY", "EXPANDED_8_PLUS_8")]["winner"] == "FIELD_OPERATOR"

    fallback_right = Counter(str(row["right_surface"]) for row in target_all)
    clean_right = Counter(str(row["right_surface"]) for row in target_clean)
    clean_meta: dict[str, list[Mapping[str, object]]] = defaultdict(list)
    for row in target_clean:
        clean_meta[str(row["right_surface"])].append(row)
    census_rows: list[dict[str, object]] = []
    for right in sorted(set(fallback_right) | set(clean_right)):
        meta = clean_meta[right]
        measures: dict[str, float | int] = {}
        for deck, classes in decks.items():
            for anchor_class, surfaces in classes.items():
                selected = [row for row in anchor_edges if row["predecessor_surface"] in surfaces and row["right_surface"] == right]
                prefix = ("core" if deck.startswith("CORE") else "expanded") + "_" + ("nominal" if anchor_class == "NOMINAL_HEAD" else "operator")
                measures[prefix + "_raw_edges"] = len(selected)
                measures[prefix + "_support_surfaces"] = len({row["predecessor_surface"] for row in selected})
                measures[prefix + "_support_folios"] = len({row["physical_folio"] for row in selected})
                measures[prefix + "_surface_mass"] = sum(
                    sum(1 for row in selected if row["predecessor_surface"] == surface) / anchor_counts[surface] / len(surfaces)
                    for surface in surfaces
                )
        core_delta = float(measures["core_nominal_surface_mass"]) - float(measures["core_operator_surface_mass"])
        expanded_delta = float(measures["expanded_nominal_surface_mass"]) - float(measures["expanded_operator_surface_mass"])
        direction = "NOMINAL_HEAD" if core_delta > 0 and expanded_delta > 0 else "FIELD_OPERATOR" if core_delta < 0 and expanded_delta < 0 else "DECK_FLIP" if core_delta * expanded_delta < 0 else "UNINFORMATIVE"
        strong = direction in {"NOMINAL_HEAD", "FIELD_OPERATOR"} and fallback_right[right] >= 2
        if strong:
            short = "nominal" if direction == "NOMINAL_HEAD" else "operator"
            other = "operator" if short == "nominal" else "nominal"
            for deck_prefix in ("core", "expanded"):
                win = float(measures[f"{deck_prefix}_{short}_surface_mass"])
                lose = float(measures[f"{deck_prefix}_{other}_surface_mass"])
                ratio = math.inf if win > 0 and lose == 0 else win / lose if lose else 0.0
                strong = strong and ratio >= 2.0
                strong = strong and int(measures[f"{deck_prefix}_{short}_support_surfaces"]) >= 2
                strong = strong and int(measures[f"{deck_prefix}_{short}_support_folios"]) >= 2
        slot_tier = "TIER_A_STABLE" if strong else "LEAD_ONLY" if direction in {"NOMINAL_HEAD", "FIELD_OPERATOR"} else direction
        census_rows.append({
            "right_surface": right, "fallback_target_tokens": fallback_right[right], "novel_target_tokens": clean_right[right],
            "novel_pages": len({row["page"] for row in meta}), "novel_physical_folios": len({row["physical_folio"] for row in meta}),
            "novel_loci": len({row["locus"] for row in meta}),
            "novel_registers": len({(row["section"], row["language"], row["hand"]) for row in meta}),
            "family_member": int(right in family_by), "slot_extension_member": int(right in extension_by),
            "whole_default_de": cards[right]["v99r7_spoken_default_de"] if right in cards else "NONE",
            "whole_level": cards[right]["working_model_level"] if right in cards else "NONE",
            **measures, "stable_direction": direction, "slot_evidence_tier": slot_tier,
        })
    census_by = {str(row["right_surface"]): row for row in census_rows}

    family_surfaces = set(family_by)
    left_written = right_written = left_exact = right_exact = 0
    for row in ol_rows:
        left, _lo, le = neighbor(row, context, -1)
        right, _ro, re = neighbor(row, context, 1)
        left_written += int(left in family_surfaces)
        right_written += int(right in family_surfaces)
        left_exact += int(left in family_surfaces and le)
        right_exact += int(right in family_surfaces and re)
    assert (left_written, right_written, left_exact, right_exact) == (36, 94, 27, 77)

    frame_counts = {"FALLBACK_327": Counter(), "NOVEL_305": Counter()}
    for row in fallback:
        left, _lo, le = neighbor(row, context, -1)
        right, _ro, re = neighbor(row, context, 1)
        if le and re:
            frame = f"{left}|ol|{right}"
            frame_counts["FALLBACK_327"][frame] += 1
            if row["target_occurrence_id"] in clean_ids:
                frame_counts["NOVEL_305"][frame] += 1
    assert (sum(frame_counts["FALLBACK_327"].values()), len(frame_counts["FALLBACK_327"]),
            sum(frame_counts["NOVEL_305"].values()), len(frame_counts["NOVEL_305"])) == (167, 166, 151, 150)
    assert {key: value for key, value in frame_counts["NOVEL_305"].items() if value > 1} == {"chey|ol|aiin": 2}
    frame_rows = [{"cohort": cohort, "frame": frame, "occurrences": amount}
                  for cohort in ("FALLBACK_327", "NOVEL_305")
                  for frame, amount in sorted(frame_counts[cohort].items())]

    cross_by_locus = {row["locus"]: row for row in guarded_cross(row["page"] for row in ol_rows)}
    boundary_targets: list[tuple[dict[str, str], str, int, bool]] = []
    for row in ol_rows:
        right, right_ordinal, exact = neighbor(row, context, 1)
        if right in BOUNDARY_SURFACES:
            boundary_targets.append((row, right, right_ordinal, exact))
    boundary_rows: list[dict[str, object]] = []
    for row, right, right_ordinal, exact in boundary_targets:
        source = cross_by_locus[row["locus"]]
        modes = {name: boundary_mode(source[name + "_clean"], right) for name in ("zl3b", "it2a", "rf1b")}
        variant = int(modes["zl3b"] == "SEPARATED_EXACT" and sorted((modes["it2a"], modes["rf1b"])) == ["FUSED_EXACT", "SEPARATED_EXACT"])
        all_separated = int(set(modes.values()) == {"SEPARATED_EXACT"})
        clean_member = row["target_occurrence_id"] in clean_ids
        selected_member = row["target_occurrence_id"] in family_selected_ids
        boundary_rows.append({
            "target_occurrence_id": row["target_occurrence_id"],
            "page": row["page"], "physical_folio": row["physical_folio"], "locus": row["locus"],
            "ol_ordinal": row["ordinal"], "right_ordinal": right_ordinal, "right_surface": right,
            "right_reader_exact": int(exact),
            "automatic_fallback": int(row["automatic_contextual"] == "0"),
            "clean_305_member": int(clean_member), "family_66_member": int(selected_member),
            "all_three_present": source["all_three_present"],
            "zl3b_clean": source["zl3b_clean"], "it2a_clean": source["it2a_clean"], "rf1b_clean": source["rf1b_clean"],
            "zl3b_mode": modes["zl3b"], "it2a_mode": modes["it2a"], "rf1b_mode": modes["rf1b"],
            "one_sided_fusion_variant": variant, "all_three_separated": all_separated,
            "interpretation": "LOCAL_BOUNDARY_UNCERTAINTY" if variant else "STABLE_SEPARATION",
            "pair_search_scope": "LINE_GLOBAL_SINGLE_FORM", "independent_witness_count": 1,
            "component_export_credit": 0,
        })
    assert len(boundary_rows) == 19
    assert sum(int(row["one_sided_fusion_variant"]) for row in boundary_rows) == 3
    assert sum(int(row["all_three_separated"]) for row in boundary_rows) == 16
    assert sum(int(row["right_reader_exact"]) for row in boundary_rows) == 16
    assert sum(int(row["family_66_member"]) for row in boundary_rows) == 14
    assert not any(int(row["one_sided_fusion_variant"]) for row in boundary_rows if int(row["right_reader_exact"]))
    assert all(int(row["all_three_separated"]) for row in boundary_rows if int(row["family_66_member"]))

    history_source = {row["source_id"]: row for row in read_tsv(G735_HISTORY)}
    history_rows = [{
        "source_id": source_id, "work": history_source[source_id]["work"],
        "date_band": history_source[source_id]["date_band"], "region": history_source[source_id]["region"],
        "language": history_source[source_id]["language"], "slot_signature": history_source[source_id]["slot_signature"],
        "whole_plus_code_layout": history_source[source_id]["whole_plus_code_layout"],
        "evidence_summary": history_source[source_id]["evidence_summary"], "caveat": history_source[source_id]["caveat"],
        "gdt775_use": "ARCHITECTURE_ONLY", "voynich_identity_credit": 0, "lexeme_credit": 0,
        "component_export_credit": 0,
    } for source_id in HISTORICAL_IDS]

    role_rows: list[dict[str, object]] = []
    for spec in family_specs:
        census = census_by[spec["surface"]]
        card = cards[spec["surface"]]
        tier_threshold_pass = (
            card["working_model_level"].startswith(("W2_", "W3_"))
            and int(census["novel_target_tokens"]) >= 3
            and int(census["novel_physical_folios"]) >= 3
            and int(census["novel_registers"]) >= 2
        )
        assert (spec["family_tier"] == "PRIMARY") == tier_threshold_pass
        state_prior = state_by_surface.get(spec["surface"], {})
        role_rows.append({
            "surface": spec["surface"], "semantic_class": spec["semantic_class"],
            "portable_span_de": spec["portable_span_de"], "fluent_span_de": spec["fluent_span_de"],
            "strongest_rival_de": spec["strongest_rival_de"], "family_tier": spec["family_tier"],
            "historical_source_ids": spec["historical_source_ids"], "construction_confidence": spec["construction_confidence"],
            "scope_status": spec["scope_status"], "specific_counterevidence_de": spec["specific_counterevidence_de"],
            "whole_default_de": card["v99r7_spoken_default_de"],
            "whole_level": card["working_model_level"],
            "whole_score_0_100_not_probability": card["working_model_score_0_100_not_probability"],
            "source_gdts": card["source_gdts"],
            "tier_threshold_pass": int(tier_threshold_pass),
            "tier_basis": "WHOLE_W2_OR_W3__TOKENS_GE3__FOLIOS_GE3__REGISTERS_GE2",
            "state_pair_id": state_prior.get("state_pair_id", "NONE"),
            "state_pair_role": state_prior.get("state_pair_role", "NONE"),
            "state_prior_candidate_de": state_prior.get("state_prior_candidate_de", "NONE"),
            "state_prior_confidence": state_prior.get("state_prior_confidence", "NONE"),
            "state_prior_counterevidence": state_prior.get("state_prior_counterevidence", "NONE"),
            "later_rival_source": "GDT737" if spec["surface"] == "olaiin" else "NONE",
            "later_rival_candidate_de": later_olaiin["concrete_body_role_de"] if spec["surface"] == "olaiin" else "NONE",
            "later_rival_counterevidence": later_olaiin["counterevidence"] if spec["surface"] == "olaiin" else "NONE",
            "selected_occurrences": census["novel_target_tokens"], "pages": census["novel_pages"],
            "physical_folios": census["novel_physical_folios"], "loci": census["novel_loci"],
            "registers": census["novel_registers"], "predecessor_slot_direction": census["stable_direction"],
            "predecessor_slot_tier": census["slot_evidence_tier"],
            "default_is_translation": 0, "confirmed_lexeme": 0, "confirmed_plaintext": 0,
            "component_export_credit": 0,
        })
    slot_audit: list[dict[str, object]] = []
    for spec in extension_specs:
        census = census_by[spec["surface"]]
        slot_audit.append({
            "surface": spec["surface"], "semantic_class": spec["semantic_class"],
            "portable_span_de": spec["portable_span_de"], "fluent_span_de": spec["fluent_span_de"],
            "strongest_rival_de": spec["strongest_rival_de"],
            "whole_default_de": cards[spec["surface"]]["v99r7_spoken_default_de"],
            "whole_level": cards[spec["surface"]]["working_model_level"],
            "selected_occurrences": census["novel_target_tokens"], "pages": census["novel_pages"],
            "physical_folios": census["novel_physical_folios"], "predecessor_slot_direction": census["stable_direction"],
            "predecessor_slot_tier": census["slot_evidence_tier"],
            "construction_confidence": spec["construction_confidence"], "selected_in_family_renderer": 0,
            "scope_status": spec["scope_status"], "specific_counterevidence_de": spec["specific_counterevidence_de"],
            "selected_in_throughput_renderer": 1, "default_is_translation": 0, "confirmed_lexeme": 0,
            "confirmed_plaintext": 0, "component_export_credit": 0,
        })
    assert {(row["surface"], row["predecessor_slot_direction"], row["predecessor_slot_tier"]) for row in slot_audit} == {
        ("al", "NOMINAL_HEAD", "TIER_A_STABLE"),
        ("dain", "NOMINAL_HEAD", "TIER_A_STABLE"),
        ("or", "NOMINAL_HEAD", "TIER_A_STABLE"),
        ("chol", "FIELD_OPERATOR", "TIER_A_STABLE"),
    }

    individually_nominal = [row for row in role_rows if row["predecessor_slot_direction"] == "NOMINAL_HEAD"
                            and row["predecessor_slot_tier"] == "TIER_A_STABLE"]
    individually_operator = [row for row in role_rows if row["predecessor_slot_direction"] == "FIELD_OPERATOR"]
    individually_uninformative = [row for row in role_rows if row["predecessor_slot_direction"] == "UNINFORMATIVE"]
    assert (len(individually_nominal), sum(int(row["selected_occurrences"]) for row in individually_nominal)) == (6, 33)
    assert (len(individually_operator), sum(int(row["selected_occurrences"]) for row in individually_operator)) == (1, 5)
    assert (len(individually_uninformative), sum(int(row["selected_occurrences"]) for row in individually_uninformative)) == (6, 28)

    novel_core = vector_index[("NOVEL_203", "CORE_6_PLUS_6")]
    novel_expanded = vector_index[("NOVEL_203", "EXPANDED_8_PLUS_8")]
    model_rows = [
        {"model_id": "M01_NOMINAL_HEAD_PLUS_COMPLETE_WHOLE", "selected": 1,
         "realization": "Ansatz plus vollständiger rechter Qualitäts-/Wert-/Formdefault",
         "selection_basis": "EXPLORATORY_THROUGHPUT_RENDERER_CONVENTION",
         "robustness_status": "NOT_ROBUST_TO_DAIIN_OR_FIXED_FAMILY_TARGET_DROP",
         "right_exact_family": right_exact, "left_exact_family": left_exact, "right_left_ratio": right_exact / left_exact,
         "core_predecessor_cosine": novel_core["nominal_raw_cosine"], "expanded_predecessor_cosine": novel_expanded["nominal_raw_cosine"],
         "boundary_fusion_variants": 3, "selected_exact_fusion_variants": 0,
         "positive_evidence": "usable complete-whole complements; baseline head-mix predecessor lead only",
         "counterevidence": "position-confounded; drop-daiin flips core equalized result; dropping fixed family flips both decks; only 33/66 tokens have individual nominal Tier-A support; 77:27 orientation is selection-aware description",
         "confirmed_lexeme": 0, "component_export_credit": 0},
        {"model_id": "M02_STATUS_FORM_CONNECTOR", "selected": 0,
         "realization": "in/als/auf/mit plus vollständiger rechter Default",
         "selection_basis": "UNSELECTED_RIVAL", "robustness_status": "NOT_NUMERICALLY_SCORED",
         "right_exact_family": right_exact, "left_exact_family": left_exact, "right_left_ratio": right_exact / left_exact,
         "core_predecessor_cosine": "NOT_SCORED", "expanded_predecessor_cosine": "NOT_SCORED",
         "boundary_fusion_variants": 3, "selected_exact_fusion_variants": 0,
         "positive_evidence": "rightward quality/value/form family permits a connector reading",
         "counterevidence": "preposition changes by complement; all selected exact boundary cases remain separated; no score assigned",
         "confirmed_lexeme": 0, "component_export_credit": 0},
        {"model_id": "M03_FIELD_FORMULA_OPERATOR", "selected": 0,
         "realization": "Feldgrenze oder Doppelpunkt vor rechtem Ganzwort",
         "selection_basis": "UNSELECTED_RIVAL", "robustness_status": "BASELINE_LOSER_BUT_TARGET_DROP_WINNER",
         "right_exact_family": right_exact, "left_exact_family": left_exact, "right_left_ratio": right_exact / left_exact,
         "core_predecessor_cosine": novel_core["operator_raw_cosine"], "expanded_predecessor_cosine": novel_expanded["operator_raw_cosine"],
         "boundary_fusion_variants": 3, "selected_exact_fusion_variants": 0,
         "positive_evidence": "some complements can be complete record fields; wins both equalized decks after fixed-family target drop",
         "counterevidence": "loses both unadjusted pooled decks; available operator controls are mostly line-initial",
         "confirmed_lexeme": 0, "component_export_credit": 0},
    ]

    atlas_by_id = {row["target_occurrence_id"]: row for row in atlas_rows}
    renderer_rows: list[dict[str, object]] = []
    for row in ol_rows:
        audit = atlas_by_id.get(row["target_occurrence_id"])
        family = bool(audit and audit["dispatch_branch"] == "RIGHT_COMPLETE_13_FAMILY")
        slot = bool(audit and audit["dispatch_branch"] == "SLOT_ONLY_WHOLE_EXTENSION")
        right, right_ordinal, right_is_exact = neighbor(row, context, 1)
        consumes_right = family or slot
        family_default = audit["fluent_span_de"] if family else row["automatic_default_de"]
        throughput_default = audit["fluent_span_de"] if family or slot else row["automatic_default_de"]
        hybrid_default = audit["fluent_span_de"] if family or slot else row["hybrid_default_de"]
        renderer_rows.append({
            "target_occurrence_id": row["target_occurrence_id"], "page": row["page"],
            "physical_folio": row["physical_folio"], "locus": row["locus"], "section": row["section"],
            "language": row["language"], "hand": row["hand"], "ordinal": row["ordinal"],
            "right_surface": right, "right_ordinal": right_ordinal,
            "right_reader_exact": int(right_is_exact),
            "gdt774_automatic_branch": row["automatic_branch"], "gdt774_automatic_default_de": row["automatic_default_de"],
            "family_branch": "RIGHT_COMPLETE_13_FAMILY" if family else "INHERITED_GDT774",
            "family_renderer_default_de": family_default,
            "family_renderer_contextual": int(row["automatic_contextual"] == "1" or family),
            "throughput_branch": "SLOT_ONLY_WHOLE_EXTENSION" if slot else "RIGHT_COMPLETE_13_FAMILY" if family else "INHERITED_GDT774",
            "throughput_renderer_default_de": throughput_default,
            "throughput_renderer_contextual": int(row["automatic_contextual"] == "1" or family or slot),
            "hybrid_throughput_default_de": hybrid_default,
            "hybrid_throughput_contextual": int(row["hybrid_contextual"] == "1" or family or slot),
            "family_span_consumes_right_token": int(family),
            "throughput_span_consumes_right_token": int(consumes_right),
            "hybrid_throughput_span_consumes_right_token": int(consumes_right),
            "family_span_id": f"G775-FAMILY-SPAN:{row['target_occurrence_id']}" if family else "NONE",
            "throughput_span_id": f"G775-THROUGHPUT-SPAN:{row['target_occurrence_id']}" if consumes_right else "NONE",
            "throughput_right_token_id": f"{row['locus']}@{right_ordinal}" if consumes_right else "NONE",
            "construction_confidence": "C0_ADJACENT_OL_COLLISION__FAMILY_RETAINED" if family and audit["adjacent_left_ol_collision"] else audit["construction_confidence"] if family or slot else row["automatic_confidence"],
            "written_line_eva": row["written_line_eva"], "default_is_translation": 0,
            "confirmed_lexeme": 0, "confirmed_plaintext": 0, "component_export_credit": 0,
        })
    family_context = sum(int(row["family_renderer_contextual"]) for row in renderer_rows)
    throughput_context = sum(int(row["throughput_renderer_contextual"]) for row in renderer_rows)
    hybrid_context = sum(int(row["hybrid_throughput_contextual"]) for row in renderer_rows)
    assert (family_context, throughput_context, hybrid_context) == (115, 123, 129)
    consumed = [row for row in renderer_rows if int(row["throughput_span_consumes_right_token"])]
    assert len(consumed) == 74 and len({row["throughput_span_id"] for row in consumed}) == 74
    assert len({row["throughput_right_token_id"] for row in consumed}) == 74

    dictionary: list[dict[str, object]] = [{
        "entry": "ol", "entry_scope": "EXACT_WHOLE_CONTEXTUAL_HEAD",
        "selected_default_de": "Ansatz-/Zubereitungsposten; vor lizenziertem Ganzwort: Ansatz plus Komplement",
        "confidence": "C2_STRUCTURAL_C0_SEMANTIC_RENDERER", "occurrences": 376, "pages": 98, "physical_folios": 61,
        "positive_evidence": f"{len(family_rows)} vollständige rechte Ganzwortkarten einsetzbar; Orientierung {right_exact}:{left_exact} nur deskriptiv und selektionsbewusst",
        "counterevidence": "Nominalvergleich ist positionskonfundiert und kippt in Zieltyp-Drop-Tests; Paket nicht score-ready; genaue Substanz und Lexem offen",
        "strongest_rival_de": "Status-/Formverbinder in/als/auf/mit; alternativ Feldtrenner",
        "historical_analogue_ids": "HSR008|HSR010|HSR012|HSR013|HSR017",
        "default_is_translation": 0, "confirmed_lexeme": 0, "confirmed_plaintext": 0, "component_export_credit": 0,
    }]
    for row in role_rows:
        dictionary.append({
            "entry": f"ol {row['surface']}", "entry_scope": "EXACT_TWO_WHOLE_SPAN",
            "selected_default_de": row["fluent_span_de"], "confidence": row["construction_confidence"],
            "occurrences": row["selected_occurrences"], "pages": row["pages"], "physical_folios": row["physical_folios"],
            "positive_evidence": f"rechter Ganzwortdefault={row['whole_default_de']}; Familientier={row['family_tier']}; Slot={row['predecessor_slot_direction']}/{row['predecessor_slot_tier']}; Register={row['registers']}",
            "counterevidence": row["specific_counterevidence_de"],
            "strongest_rival_de": row["strongest_rival_de"], "historical_analogue_ids": row["historical_source_ids"],
            "default_is_translation": 0, "confirmed_lexeme": 0, "confirmed_plaintext": 0, "component_export_credit": 0,
        })
    for row in slot_audit:
        dictionary.append({
            "entry": f"ol {row['surface']}", "entry_scope": "EXACT_TWO_WHOLE_SLOT_EXTENSION",
            "selected_default_de": row["fluent_span_de"], "confidence": row["construction_confidence"],
            "occurrences": row["selected_occurrences"], "pages": row["pages"], "physical_folios": row["physical_folios"],
            "positive_evidence": f"Zweifolio-Wiederholung; rechter Ganzwortdefault={row['whole_default_de']}; Slot={row['predecessor_slot_direction']}/{row['predecessor_slot_tier']}",
            "counterevidence": row["specific_counterevidence_de"],
            "strongest_rival_de": row["strongest_rival_de"], "historical_analogue_ids": "HSR008|HSR010|HSR012|HSR013",
            "default_is_translation": 0, "confirmed_lexeme": 0, "confirmed_plaintext": 0, "component_export_credit": 0,
        })

    packet, relation_crosswalk = make_packet(target_clean, anchor_edges)
    packet_fields = ["edge_id", "batch_id", "page", "physical_folio", "diagram_unit_id", "pivot_visual_id",
                     "pivot_locus", "target_visual_id", "target_locus", "relation_type", "direction_basis",
                     "ownership_basis", "geometry_only_selection", "source_manifest_id", "page_crop_sha256",
                     "pivot_crop_sha256", "target_crop_sha256", "source_aware_localizer", "relation_reviewer",
                     "relation_confidence", "ambiguity_state", "formal_access_state", "fold_assignment", "eligibility_status"]

    outputs: list[tuple[str, list[dict[str, object]] | list[dict[str, str]], list[str]]] = [
        ("OL_327_RIGHT_COMPLEMENT_ATLAS.tsv", atlas_rows, list(atlas_rows[0])),
        ("RIGHT_COMPLEMENT_SURFACE_CENSUS.tsv", census_rows, list(census_rows[0])),
        ("RIGHT_COMPLEMENT_13_ROLE_REGISTRY.tsv", role_rows, list(role_rows[0])),
        ("SLOT_ONLY_EXTENSION_AUDIT.tsv", slot_audit, list(slot_audit[0])),
        ("EXACT_FRAME_REPETITION.tsv", frame_rows, list(frame_rows[0])),
        ("PREDECESSOR_ANCHOR_DECK.tsv", anchor_specs, list(anchor_specs[0])),
        ("ANCHOR_PREDECESSOR_EDGE_ATLAS.tsv", anchor_edges, list(anchor_edges[0])),
        ("PREDECESSOR_VECTOR_COMPARISON.tsv", vector_rows, list(vector_rows[0])),
        ("PREDECESSOR_SURFACE_SIMILARITY.tsv", similarity_rows, list(similarity_rows[0])),
        ("PREDECESSOR_FOLIO_HOLDOUT.tsv", holdouts, list(holdouts[0])),
        ("PREDECESSOR_TARGET_DROP_AUDIT.tsv", target_drop_rows, list(target_drop_rows[0])),
        ("CROSS_READER_BOUNDARY_AUDIT.tsv", boundary_rows, list(boundary_rows[0])),
        ("HISTORICAL_CONSTRUCTION_COMPARATORS.tsv", history_rows, list(history_rows[0])),
        ("RIGHT_COMPLEMENT_MODEL_SCORE.tsv", model_rows, list(model_rows[0])),
        ("GDT775_376_RENDERER.tsv", renderer_rows, list(renderer_rows[0])),
        ("GDT775_WORKING_DICTIONARY.tsv", dictionary, list(dictionary[0])),
        ("GDT775_GDT388_RELATION_PACKET.tsv", packet, packet_fields),
        ("GDT775_RELATION_EDGE_CROSSWALK.tsv", relation_crosswalk, list(relation_crosswalk[0])),
    ]
    for name, rows, fields in outputs:
        write_tsv(artifacts / name, rows, fields)

    intake_done = subprocess.run([str(ROOT / "vmanus-exp"), "check-edge-packet",
                                  str(artifacts / "GDT775_GDT388_RELATION_PACKET.tsv")],
                                 cwd=ROOT, text=True, capture_output=True, check=True)
    intake = json.loads(intake_done.stdout)
    assert intake == {"status": "VALID_ACQUISITION_NOT_SCORE_READY", "packet_rows": 572,
                      "eligible_edges": 0, "eligible_folios": 0, "discovery_edges": 0,
                      "holdout_edges": 0, "mobile_edges": 0, "capacity_gate_50_edges_5_folios": False,
                      "holdout_gate": False, "mobile_null_gate": False, "score_ready": False, "errors": []}
    write_json(artifacts / "RELATION_PACKET_INTAKE.json", intake)

    def cohort_counts(rows: Sequence[Mapping[str, object]]) -> dict[str, int]:
        return {"occurrences": len(rows), "pages": len({str(row["page"]) for row in rows}),
                "physical_folios": len({str(row["physical_folio"]) for row in rows}),
                "loci": len({str(row["locus"]) for row in rows})}

    result = {
        "experiment_id": "GDT775", "status": "PASS__RENDERER_THROUGHPUT_66_PLUS_8__PREDECESSOR_DIAGNOSTIC_NOT_SCORE_READY__NO_PLAINTEXT",
        "source_locks": lock_count, "guard": dict(environment["guard"]),
        "cohorts": {"all_ol": cohort_counts(ol_rows), "automatic_fallback": cohort_counts(fallback),
                    "novel_no_direct_no_calibration": cohort_counts(clean),
                    "fallback_exact_right": len(target_all), "novel_exact_right": len(target_clean)},
        "exact_bigram_universe": universe,
        "right_family": {"surface_count": 13, "selected_occurrences": len(family_rows),
                         "primary_occurrences": len(primary_rows), "extension_occurrences": len(family_extension),
                         "slot_only_occurrences": len(slot_rows), "right_written": right_written,
                         "left_written": left_written, "right_exact": right_exact, "left_exact": left_exact,
                         "orientation_status": "DESCRIPTIVE_SELECTION_AWARE__FAMILY_AUTHORED_AS_RIGHT_COMPLEMENTS",
                         "individual_nominal_surfaces": len(individually_nominal),
                         "individual_nominal_tokens": sum(int(row["selected_occurrences"]) for row in individually_nominal),
                         "individual_operator_surfaces": len(individually_operator),
                         "individual_operator_tokens": sum(int(row["selected_occurrences"]) for row in individually_operator),
                         "individual_uninformative_surfaces": len(individually_uninformative),
                         "individual_uninformative_tokens": sum(int(row["selected_occurrences"]) for row in individually_uninformative),
                         "adjacent_left_ol_collisions": sum(int(row["adjacent_left_ol_collision"]) for row in family_rows)},
        "predecessor": {"all_fallback_exact_right": 221, "novel_exact_right": 203,
                        "comparison_status": "DESCRIPTIVE_NOT_SCORE_READY__POSITION_AND_TARGET_TYPE_SENSITIVE",
                        "balanced_by": "SURFACE_COUNT_ONLY__NOT_EDGE_COUNT",
                        "nominal_label_scope": "AUTHORED_CONTENT_OR_RECORD_HEAD_MIX__INCLUDES_DAIR_MEASURE_FIELD_AND_POL_HEADINGS",
                        "decks_independent": False,
                        "core_nominal_edges": novel_core["nominal_edges"], "core_operator_edges": novel_core["operator_edges"],
                        "core_nominal_cosine": novel_core["nominal_raw_cosine"], "core_operator_cosine": novel_core["operator_raw_cosine"],
                        "core_nominal_surface_equalized_cosine": novel_core["nominal_surface_equalized_cosine"],
                        "core_operator_surface_equalized_cosine": novel_core["operator_surface_equalized_cosine"],
                        "expanded_nominal_edges": novel_expanded["nominal_edges"], "expanded_operator_edges": novel_expanded["operator_edges"],
                        "expanded_nominal_cosine": novel_expanded["nominal_raw_cosine"], "expanded_operator_cosine": novel_expanded["operator_raw_cosine"],
                        "expanded_nominal_surface_equalized_cosine": novel_expanded["nominal_surface_equalized_cosine"],
                        "expanded_operator_surface_equalized_cosine": novel_expanded["operator_surface_equalized_cosine"],
                        "target_first_edges": novel_core["target_first_edges"], "target_middle_edges": novel_core["target_middle_edges"],
                        "core_nominal_first_edges": novel_core["nominal_first_edges"], "core_nominal_middle_edges": novel_core["nominal_middle_edges"],
                        "core_operator_first_edges": novel_core["operator_first_edges"], "core_operator_middle_edges": novel_core["operator_middle_edges"],
                        "position_confound_status": "SEVERE_FIRST_MIDDLE_CLASS_IMBALANCE",
                        "target_drop_robust": False,
                        "target_drop_audit": {
                            f"{row['scenario']}__{row['deck']}": {
                                "remaining_target_edges": row["remaining_target_edges"],
                                "nominal_surface_equalized_cosine": row["nominal_surface_equalized_cosine"],
                                "operator_surface_equalized_cosine": row["operator_surface_equalized_cosine"],
                                "winner": row["winner"],
                            } for row in target_drop_rows
                        },
                        "leave_one_folio_sensitivity_rows": len(holdouts),
                        "nominal_sensitivity_wins": sum(row["winner"] == "NOMINAL_HEAD" for row in holdouts)},
        "boundary": {"audited_pairs": len(boundary_rows), "fusion_variants": sum(int(row["one_sided_fusion_variant"]) for row in boundary_rows),
                     "all_three_separated": sum(int(row["all_three_separated"]) for row in boundary_rows),
                     "reader_exact_audited_pairs": sum(int(row["right_reader_exact"]) for row in boundary_rows),
                     "selected_audited_pairs": sum(int(row["family_66_member"]) for row in boundary_rows),
                     "selected_fusion_variants": sum(int(row["one_sided_fusion_variant"]) for row in boundary_rows if int(row["family_66_member"])),
                     "independent_witnesses": 1},
        "renderer": {"gdt774_automatic_contextual": 49, "family_contextual": family_context,
                     "family_fallback": 376 - family_context, "throughput_contextual": throughput_context,
                     "throughput_fallback": 376 - throughput_context, "hybrid_throughput_contextual": hybrid_context,
                     "hybrid_throughput_fallback": 376 - hybrid_context},
        "relation_packet": intake, "historical_source_ids": list(HISTORICAL_IDS),
        "confirmed_lexemes": 0, "confirmed_plaintext_clauses": 0, "component_exports": 0,
        "new_pages": 0, "new_images": 0, "new_ocr": 0, "new_transcriptions": 0,
        "claim_ceiling": "Replaceable complete-whole ol+X working spans on the cached cohort; no specific substance, language, lexeme, plaintext, EVA component or historical identity.",
    }
    write_json(artifacts / "RESULT.json", result)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(build_report(result), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
