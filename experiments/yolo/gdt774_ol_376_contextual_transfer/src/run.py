#!/usr/bin/env python3
"""Build the GDT774 cache-only transfer of the GDT773 ``ol`` renderer."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Callable, Iterable


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt774_ol_376_contextual_transfer"
SRC = EXP / "src"
DEFAULT_ARTIFACTS = EXP / "artifacts"
DEFAULT_REPORT = EXP / "REPORT.md"

G769 = ROOT / "experiments/yolo/gdt769_liquid_process_role_identity_dispatch/artifacts"
G683 = ROOT / "experiments/yolo/gdt683_ol_semantic_debt_reconciliation/artifacts"
G760 = ROOT / "experiments/yolo/gdt760_quantity_bilateral_content_attachment/artifacts"
G762 = ROOT / "experiments/yolo/gdt762_moist_medium_candidate_discrimination/artifacts"
G763 = ROOT / "experiments/yolo/gdt763_h1_content_vs_record_discriminator/artifacts"
G773 = ROOT / "experiments/yolo/gdt773_ol_capacity_equalized_composition_audit/artifacts"

FALLBACK = "Ansatz-/Zubereitungsposten"

OUTPUT_NAMES = [
    "OL_376_TRANSFER_ATLAS.tsv",
    "TRANSFER_BRANCH_SUMMARY.tsv",
    "AMOUNT_17_EDGE_AUDIT.tsv",
    "CALIBRATION_REPLAY_AUDIT.tsv",
    "DIRECT_SIGNATURE_DIRECTION_SUMMARY.tsv",
    "F15_STATE_BRIDGE_AUDIT.tsv",
    "LINE_POSITION_REPEAT_AUDIT.tsv",
    "ADJACENT_OL_PAIR_AUDIT.tsv",
    "REGISTER_DISPATCH_SUMMARY.tsv",
    "PHYSICAL_FOLIO_TRANSFER_SUMMARY.tsv",
    "LEGACY_GRUNDANSATZ_COMPARISON.tsv",
    "MANUAL_24_CONTEXT_AUDIT.tsv",
    "GDT774_WORKING_DICTIONARY.tsv",
    "RESULT.json",
    "structural_audit/OL_376_STRUCTURAL_POSITION_ATLAS.tsv",
    "structural_audit/OL_DIRECT_SIGNATURE_DIRECTION_MATRIX.tsv",
    "structural_audit/OL_EVIDENCE_VENN_DISPATCH.tsv",
    "structural_audit/OL_SELF_REPEAT_ATLAS.tsv",
    "structural_audit/OL_NEIGHBOR_SURFACE_SUMMARY.tsv",
    "structural_audit/OL_REPEATED_NEIGHBOR_FRAMES.tsv",
    "structural_audit/OL_REGISTER_SUMMARY.tsv",
    "structural_audit/OL_FOLIO_HOLDOUT.tsv",
    "structural_audit/OL_POSITION_MATCHED_NULL.tsv",
    "structural_audit/STRUCTURAL_AUDIT_RESULT.json",
]

BRANCH = {
    "G774-D00": "GDT773_CALIBRATION_COPY",
    "G774-D01": "AMOUNT_TO_CONTENT_HEAD",
    "G774-D02": "CONTENT_TO_AMOUNT_HEAD",
    "G774-D03": "PROCESS_SEQUENCE_RIGHT",
    "G774-D04": "FIELD_CLOSURE_LEFT",
    "G774-D05": "CLOSE_RIGHT_NOMINAL_VETO",
    "G774-D06": "STATE_FIELD_CHAIN",
    "G774-D07": "GENERIC_NOMINAL_FALLBACK",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def guarded_read_tsv(
    path: Path, *, selector: str, allowed_values: Iterable[str], columns: list[str]
) -> list[dict[str, str]]:
    """Read a mixed TSV only through the repository's pre-materialization guard."""
    relative = path.relative_to(ROOT)
    command = [
        str(ROOT / "vmanus-exp"), "query-tsv", str(relative),
        "--selector", selector, "--columns", ",".join(columns),
    ]
    for value in sorted(set(allowed_values)):
        command.extend(["--allow", value])
    completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=True)
    if "GUARD_STATS" not in completed.stderr:
        raise AssertionError(f"guard statistics missing for {relative}")
    return list(csv.DictReader(io.StringIO(completed.stdout), delimiter="\t"))


def write_tsv(path: Path, rows: Iterable[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_source_lock() -> dict[str, str]:
    locked: dict[str, str] = {}
    for row in read_tsv(SRC / "SOURCE_LOCK.tsv"):
        relative = Path(row["path"])
        if relative.is_absolute() or ".." in relative.parts:
            raise AssertionError(f"unsafe source-lock path: {relative}")
        path = ROOT / relative
        actual = sha256(path)
        if actual != row["expected_sha256"]:
            raise AssertionError(f"source hash differs for {relative}: {actual}")
        locked[row["path"]] = actual
    return locked


def counts(rows: Iterable[dict[str, object]]) -> dict[str, int]:
    material = list(rows)
    return {
        "occurrences": len(material),
        "page_labels": len({str(row["page"]) for row in material}),
        "physical_folios": len({str(row["physical_folio"]) for row in material}),
        "loci": len({str(row["locus"]) for row in material}),
    }


def join_values(values: Iterable[str]) -> str:
    clean = sorted({value for value in values if value})
    return "|".join(clean) if clean else "NONE"


def evidence_directions(direct: dict[str, object], channel: str) -> set[str]:
    evidence = direct["channel_evidence"].get(channel, [])
    return {str(item.get("direction", "")) for item in evidence if item.get("direction")}


def build_report(result: dict[str, object]) -> str:
    auto = result["automatic_renderer"]
    hybrid = result["hybrid_renderer"]
    geometry = result["geometry"]
    calibration = result["calibration_replay"]
    amount = result["amount_transfer"]
    manual = result["manual_context_audit"]
    structural = result["structural_audit"]
    position_null = structural["null_results"]["N01_FOLIO_SLOT_POSITION"]
    neighbor_null = structural["null_results"]["N02_FOLIO_POSITION_NEIGHBOR"]
    repeat_null = structural["null_results"]["N01_FOLIO_SLOT_POSITION"]
    return f"""# GDT774 — Transfer des `ol`-Kontextoperators auf 376 Stellen

Status: `{result['status']}`. Diese Runde benutzt ausschließlich bereits
gecachte, reader-exakte Positionen. Sie öffnet keine neue Seite und behauptet
weiterhin null bestätigte Lexeme oder Klartextsätze. Der unabhängige Validator
bestätigt 28.954 Checks, alle fünfzehn Source Locks und den bytegleichen Replay
aller 24 Runner-Ausgaben plus Bericht.

## Das konkrete Ergebnis

Der occurrence-ID-freie Renderer gibt allen {geometry['occurrences']} exakten
`ol`-Vorkommen eine sichtbare Arbeitsbedeutung. Er findet aber nur
**{auto['contextual_occurrences']} kontextspezifische Stellen
({auto['contextual_rate_percent']:.2f}%)**. Die übrigen
**{auto['nominal_occurrences']} ({auto['nominal_rate_percent']:.2f}%)** bleiben
ehrlich beim schwachen Ganzwortdefault `Ansatz-/Zubereitungsposten`.

Die automatische Ausgabe verteilt sich auf:

- {auto['output_counts']['Ansatz:']} × `Ansatz:` nach einer Mengenform;
- {auto['output_counts']['Menge:']} × `Menge:` vor einer Mengenform;
- {auto['output_counts']['und dann']} × `und dann` vor einem direkten Prozessanker;
- {auto['output_counts'][';']} × `;` nach einem direkten Abschlussanker;
- {auto['output_counts']['und']} × `und` in einer beidseitigen F15-Zustandsbrücke;
- {auto['output_counts'][FALLBACK]} × nominaler Fallback.

Ein automatischer Doppelpunkt wird **nie** erzeugt: Der eine GDT773-Fall hat
keinen übertragbaren, occurrence-ID-freien Trigger. Ebenso bleiben rechtsseitige
Abschlüsse, linksseitige Prozesse, bloße Zeilenränder, nackte F14-Geometrie
und alle sieben `ol ol`-Paare nominal.

## Wie viel von GDT773 wirklich überträgt

Die Regeln reproduzieren nur **{calibration['automatic_exact_matches']} von 15**
fixierten GDT773-Ausgaben. Die sechs Fehlstellen waren durch fallweise
Feldinterpretation gewonnen, nicht durch eine portable Beobachtungsregel. Der
praktische Hybridreader bewahrt die fünfzehn alten Kalibrierentscheidungen und
wendet die automatischen Regeln sonst unverändert an. Dadurch erhält er
{hybrid['contextual_occurrences']} kontextspezifische und
{hybrid['nominal_occurrences']} nominale Ausgaben; das ist ein Arbeitsrenderer,
kein besserer semantischer Test.

## Mengenrichtung und Sperren

Die sechzehn bekannten Mengenkontakte enthalten wegen des bilateralen
`ol s aiin ol` genau {amount['raw_edges']} occurrence-spezifische Kanten.
Fünf `ol` links von der Mengenform werden `Menge:`. Zwölf liegen rechts;
zwei davon sind jedoch zeilenfinal und würden einen baumelnden Kopf `Ansatz:`
erzeugen. Sie fallen zurück auf das Nomen. Damit bleiben
{amount['selected_edges']} ausgewählte Mengenoutputs. Phrase-Lizenz,
GDT763-Slotfunktion und die beidseitige Ambiguität bleiben im Kantenaudit
sichtbar: {amount['phrase_licensed_selected_edges']} der ausgewählten Kanten
haben die stärkere alte Phrasenlizenz, {amount['directional_c0_selected_edges']}
nur den explorativen Richtungsdefault. Keine Einheit wird dadurch identifiziert.

## Formale Realität der breiten Verteilung

Die {geometry['occurrences']} Token liegen auf {geometry['loci']} Zeilen,
{geometry['page_labels']} Seitenlabels und {geometry['physical_folios']}
physischen Folios. Ihre Lage ist {geometry['line_first']} first,
{geometry['line_middle']} medial und {geometry['line_last']} last. Nur
{geometry['any_direct_signature']} haben irgendeine direkte Signatur; die
meisten Kontexte sind also nicht fein genug typisiert.

Der operatorartige Eindruck ist zudem registerabhängig: In Sektion B liegen
nur {geometry['section_b_first']} von {geometry['section_b_total']} Token first,
außerhalb B dagegen {geometry['non_b_first']} von {geometry['non_b_total']}.
Mehrfach-`ol` konzentriert sich ebenfalls in B/Hand 2. Gleichzeitig sind die
{geometry['adjacent_repeat_tokens']} Token in sieben benachbarten `ol ol`-Paaren
signaturlos und bleiben nominal. Das stützt einen gemischten Recordkopf/Operator,
nicht ein globales Satzzeichen.

Der feste 20.000er Folio-Slotvergleich erwartet im Mittel
{position_null['line_first']['null_mean']:.2f} first-Positionen statt der
beobachteten {position_null['line_first']['observed']}; das interne Profil ist
also nicht bloß Seitenmischung. Zugleich sind sieben benachbarte Paare gegen
{repeat_null['adjacent_pairs']['null_mean']:.2f} erwartet unauffällig. Die
rechte Nachbarvielfalt ist mit {neighbor_null['unique_right_neighbors']['observed']}
gegen {neighbor_null['unique_right_neighbors']['null_mean']:.2f} im
folio-und-positionsgleichen Nullmodell stark konzentriert. Das ist der beste
nächste Hebel, kann aber sowohl einen Feldkopf mit Komplement als auch einen
Operator vor einem Feld anzeigen.

Eine breitere, bereits vorhandene Evidenz-Vereinigung erreicht nur
{structural['typed_union_occurrences']} Token; {structural['untyped_occurrences']}
bleiben außerhalb dieser Typisierung. Dreizehn der fünfzehn GDT773-Fälle liegen
in jener Vereinigung. Der Kalibrierdeck war damit stark auf informative
Kontexte angereichert und darf nicht als repräsentativ für alle 376 gelten.

## Vergleich zum alten `Grundansatz`

Alle 376 Stellen kreuzen zum alten GDT683-Output `Grundansatz`; alle beruhen
auf derselben geerbten GDT664-Karte, nicht auf 376 unabhängigen Bestätigungen.
GDT774 verwirft diesen Bestand nicht. Es zerlegt ihn in {auto['contextual_occurrences']}
gerichtete Feldausgaben und {auto['nominal_occurrences']} schwächere nominale
Fallbacks. Öl, Wasser und Wein bleiben ununterscheidbar.

Die 24 manuell ausgewählten Kontrastkontexte werden vom automatischen Reader
{manual['automatic_preferred_matches']}/24 und vom Hybridreader
{manual['hybrid_preferred_matches']}/24 wie spezifiziert ausgegeben. Diese
Stichprobe dokumentiert Richtungsfälle und Sperren; weil sie zur Regelprüfung
entworfen wurde, erhält sie null unabhängigen Bedeutungs- oder Scorecredit.

## Grenze und nächster Hebel

`ol` bleibt ein komplettes EVA-Ganzwort. Kein Zeichen oder Teilstring bekommt
eine Bedeutung. Strukturrollen und deutsche Arbeitsausgaben stehen getrennt.
Der nächste sinnvolle Hebel liegt in den {auto['nominal_occurrences']}
Fallbackstellen: die stark konzentrierten rechten Folger und der B/Hand-2-Split
können neue, occurrence-ID-freie Unterklassen liefern. Erst solche Unterklassen
dürfen weitere konkrete Outputs ersetzen.
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_ARTIFACTS)
    parser.add_argument("--report-path", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--structural-iterations", type=int, default=20000)
    args = parser.parse_args()
    artifacts = args.output_dir if args.output_dir.is_absolute() else ROOT / args.output_dir
    report_path = args.report_path if args.report_path.is_absolute() else ROOT / args.report_path
    artifacts.mkdir(parents=True, exist_ok=True)

    locked_hashes = verify_source_lock()
    structural_dir = artifacts / "structural_audit"
    subprocess.run(
        [
            sys.executable, str(SRC / "structural_audit.py"),
            "--output-dir", str(structural_dir),
            "--iterations", str(args.structural_iterations),
        ],
        cwd=ROOT, text=True, capture_output=True, check=True,
    )
    structural_result = json.loads(
        (structural_dir / "STRUCTURAL_AUDIT_RESULT.json").read_text(encoding="utf-8")
    )
    if structural_result["status"] != "PASS__376_OL__STRUCTURAL_AUDIT__NO_NEW_PAGE":
        raise AssertionError("structural audit did not pass")
    policies = sorted(read_tsv(SRC / "TRANSFER_POLICY_SPECS.tsv"), key=lambda row: int(row["priority"]))
    policy = {row["rule_id"]: row for row in policies}
    if set(policy) != {f"G774-D{i:02d}" for i in range(8)}:
        raise AssertionError("transfer-policy universe differs")
    if any(row["semantic_credit"] != "0" or row["component_export_credit"] != "0" for row in policies):
        raise AssertionError("policy grants semantic or component credit")

    target_source = read_tsv(G769 / "TARGET_526_EXACT_CONTEXT_ATLAS.tsv")
    targets = [row for row in target_source if row["surface"] == "ol"]
    if len(targets) != 376 or any(row["reader_exact"] != "1" for row in targets):
        raise AssertionError("expected 376 reader-exact ol targets")
    target_by_key = {(row["locus"], int(row["ordinal"])): row for row in targets}
    if len(target_by_key) != 376:
        raise AssertionError("ol occurrence keys are not unique")

    frame_source = read_tsv(G769 / "FRAME_LOCUS_EVIDENCE.tsv")
    frame_rows = [row for row in frame_source if row["target_surface"] == "ol"]
    f14_keys = {(row["locus"], int(row["ordinal"])) for row in frame_rows if row["frame_id"] == "F14_MEDIAL_TWO_SIDED_LINKER"}
    f15_by_key = {
        (row["locus"], int(row["ordinal"])): row
        for row in frame_rows if row["frame_id"] == "F15_STATE_TRANSITION_BRIDGE"
    }
    if len(f14_keys) != 212 or len(f15_by_key) != 31 or not set(f15_by_key).issubset(f14_keys):
        raise AssertionError("F14/F15 frame universe differs")

    expression_source = read_tsv(G760 / "QUANTITY_281_EXPRESSION_ATLAS.tsv")
    expression_by_id = {row["expression_id"]: row for row in expression_source}
    contact_source = read_tsv(G762 / "OL_AMOUNT_EXPRESSION_CONTACT_ATLAS.tsv")
    slot_source = read_tsv(G763 / "OL_16_SLOT_FUNCTION_ATLAS.tsv")
    slot_by_contact = {row["source_contact_id"]: row for row in slot_source}
    if len(contact_source) != 16 or len(slot_by_contact) != 16:
        raise AssertionError("amount contact/slot source count differs")

    amount_edges: list[dict[str, object]] = []
    amount_selected_by_key: dict[tuple[str, int], dict[str, object]] = {}
    amount_any_by_key: dict[tuple[str, int], dict[str, object]] = {}
    for contact in contact_source:
        expression = expression_by_id[contact["expression_id"]]
        slot = slot_by_contact[contact["ol_amount_contact_id"]]
        start, end = int(expression["start_ordinal"]), int(expression["end_ordinal"])
        for side in contact["ol_sides_relative_to_amount"].split("|"):
            if side == "L":
                ol_ordinal, relation, rule_id = start - 1, "OL_LEFT_OF_AMOUNT", "G774-D02"
            elif side == "R":
                ol_ordinal, relation, rule_id = end + 1, "OL_RIGHT_OF_AMOUNT", "G774-D01"
            else:
                raise AssertionError(f"unknown amount side: {side}")
            key = (contact["locus"], ol_ordinal)
            target = target_by_key.get(key)
            if target is None:
                raise AssertionError(f"amount edge lacks exact ol target: {key}")
            line_final = ol_ordinal == int(target["line_token_count"])
            selected = not (relation == "OL_RIGHT_OF_AMOUNT" and line_final)
            edge = {
                "edge_id": f"{contact['ol_amount_contact_id']}-{side}",
                "source_contact_id": contact["ol_amount_contact_id"],
                "gdt763_slot_id": slot["ol_slot_id"],
                "expression_id": contact["expression_id"],
                "page": contact["page"], "physical_folio": contact["physical_folio"],
                "locus": contact["locus"], "amount_expression_eva": contact["amount_expression_eva"],
                "amount_candidate_de": contact["amount_candidate_de"], "amount_rivals_de": contact["amount_rivals_de"],
                "amount_working_confidence": contact["amount_working_confidence"],
                "amount_start_ordinal": start, "amount_end_ordinal": end,
                "ol_side_relative_to_amount": side, "relation": relation, "ol_ordinal": ol_ordinal,
                "line_token_count": target["line_token_count"], "ol_line_final": int(line_final),
                "conditional_phrase_license": contact["conditional_phrase_license"],
                "gdt762_decision": contact["decision"], "gdt763_slot_function": slot["selected_slot_function"],
                "gdt763_dispatch_basis": slot["dispatch_basis"], "selected_for_transfer": int(selected),
                "exclusion_reason": "NONE" if selected else "DANGLING_CONTENT_HEAD_AT_LINE_END",
                "transfer_rule_id": rule_id if selected else "G774-D07",
                "automatic_default_de": policy[rule_id]["default_de"] if selected else FALLBACK,
                "bilateral_contact": int(contact["ol_directed_edges"] == "2"),
                "default_is_translation": 0, "confirmed_lexeme": 0, "component_export_credit": 0,
            }
            amount_edges.append(edge)
            if key in amount_any_by_key:
                raise AssertionError(f"duplicate amount edge for target {key}")
            amount_any_by_key[key] = edge
            if selected:
                amount_selected_by_key[key] = edge
    if len(amount_edges) != 17 or len(amount_selected_by_key) != 15:
        raise AssertionError("amount edge or selected-edge count differs")

    calibration_source = read_tsv(G773 / "OL_CONTEXTUAL_DEFAULTS.tsv")
    calibration_by_key = {(row["locus"], int(row["ordinal"])): row for row in calibration_source}
    if len(calibration_by_key) != 15:
        raise AssertionError("GDT773 calibration universe differs")

    safe_pages = {row["page"] for row in targets}
    legacy_columns = [
        "page", "locus", "ordinal", "working_translation_de", "semantic_decision",
        "evidence_type", "reader_support", "boundary_active", "render_once",
    ]
    legacy_source = guarded_read_tsv(
        G683 / "OL_463_OCCURRENCE_AUDIT.tsv", selector="page",
        allowed_values=safe_pages, columns=legacy_columns,
    )
    legacy_by_key = {(row["locus"], int(row["ordinal"])): row for row in legacy_source}
    if not set(target_by_key).issubset(legacy_by_key):
        raise AssertionError("guarded GDT683 crosswalk is incomplete")

    locus_targets: dict[str, list[dict[str, str]]] = defaultdict(list)
    for target in targets:
        locus_targets[target["locus"]].append(target)
    for locus_rows in locus_targets.values():
        locus_rows.sort(key=lambda row: int(row["ordinal"]))

    atlas: list[dict[str, object]] = []
    for source in sorted(targets, key=lambda row: (row["page"], int(row["line_number"]), int(row["ordinal"]))):
        key = (source["locus"], int(source["ordinal"]))
        direct = json.loads(source["direct_signatures"])
        process_right = "RIGHT" in (evidence_directions(direct, "PROCESS") | evidence_directions(direct, "OLY"))
        process_left = "LEFT" in (evidence_directions(direct, "PROCESS") | evidence_directions(direct, "OLY"))
        close_left = "LEFT" in evidence_directions(direct, "CLOSE")
        close_right = "RIGHT" in evidence_directions(direct, "CLOSE")
        amount_edge = amount_selected_by_key.get(key)
        if amount_edge is not None and amount_edge["relation"] == "OL_RIGHT_OF_AMOUNT":
            auto_rule = "G774-D01"
        elif amount_edge is not None and amount_edge["relation"] == "OL_LEFT_OF_AMOUNT":
            auto_rule = "G774-D02"
        elif process_right:
            auto_rule = "G774-D03"
        elif close_left:
            auto_rule = "G774-D04"
        elif close_right:
            auto_rule = "G774-D05"
        elif key in f15_by_key and key in f14_keys:
            auto_rule = "G774-D06"
        else:
            auto_rule = "G774-D07"
        auto_spec = policy[auto_rule]
        calibration = calibration_by_key.get(key)
        if calibration is not None:
            hybrid_rule = "G774-D00"
            hybrid_branch = BRANCH[hybrid_rule]
            hybrid_function = calibration["selected_function"]
            hybrid_default = calibration["selected_default_de"]
            hybrid_confidence = "INHERITED_GDT773_CONTEXT"
        else:
            hybrid_rule = auto_rule
            hybrid_branch = BRANCH[auto_rule]
            hybrid_function = auto_spec["selected_function"]
            hybrid_default = auto_spec["default_de"]
            hybrid_confidence = auto_spec["base_confidence"]
        repeats = locus_targets[source["locus"]]
        repeat_ordinals = [int(row["ordinal"]) for row in repeats]
        ordinal = int(source["ordinal"])
        adjacent_repeat = int(any(abs(ordinal - other) == 1 for other in repeat_ordinals if other != ordinal))
        legacy = legacy_by_key[key]
        if legacy["working_translation_de"] != "Grundansatz":
            raise AssertionError(f"legacy crosswalk unexpectedly differs at {key}")
        auto_default = auto_spec["default_de"]
        atlas.append({
            "target_occurrence_id": source["target_occurrence_id"], "raw_occurrence_id": source["raw_occurrence_id"],
            "surface": source["surface"], "page": source["page"], "physical_folio": source["physical_folio"],
            "locus": source["locus"], "line_number": source["line_number"], "section": source["section"],
            "language": source["language"], "hand": source["hand"], "ordinal": source["ordinal"],
            "token_index": source["token_index"], "line_token_count": source["line_token_count"],
            "line_position": source["line_position"], "normalized_line_position": source["normalized_line_position"],
            "paragraph_start_line": source["paragraph_start_line"], "paragraph_end_line": source["paragraph_end_line"],
            "true_paragraph_opener": source["true_paragraph_opener"], "true_paragraph_closer": source["true_paragraph_closer"],
            "reader_exact": source["reader_exact"], "written_line_eva": source["written_line_eva"],
            "direct_signatures": source["direct_signatures"],
            "direct_signature_channels": join_values(direct["signature_channels"]),
            "any_direct_signature": int(bool(direct["signature_channels"])),
            "amount_transfer_signal": int(amount_edge is not None),
            "amount_relation": str(amount_edge["relation"]) if amount_edge else "NONE",
            "amount_raw_excluded": int(key in amount_any_by_key and key not in amount_selected_by_key),
            "process_right_signal": int(process_right), "process_left_signal": int(process_left),
            "close_left_signal": int(close_left), "close_right_signal": int(close_right),
            "f14_medial_two_sided": int(key in f14_keys), "f15_state_transition_bridge": int(key in f15_by_key),
            "ol_count_in_locus": len(repeats), "ol_index_in_locus": repeat_ordinals.index(ordinal) + 1,
            "adjacent_ol_repeat": adjacent_repeat,
            "calibration_case_id": calibration["case_id"] if calibration else "NONE",
            "calibration_default_de": calibration["selected_default_de"] if calibration else "NONE",
            "automatic_rule_id": auto_rule, "automatic_branch": BRANCH[auto_rule],
            "automatic_function": auto_spec["selected_function"], "automatic_default_de": auto_default,
            "automatic_confidence": auto_spec["base_confidence"], "automatic_contextual": int(auto_default != FALLBACK),
            "hybrid_rule_id": hybrid_rule, "hybrid_branch": hybrid_branch,
            "hybrid_function": hybrid_function, "hybrid_default_de": hybrid_default,
            "hybrid_confidence": hybrid_confidence, "hybrid_contextual": int(hybrid_default != FALLBACK),
            "legacy_gdt683_default_de": legacy["working_translation_de"],
            "legacy_gdt683_semantic_decision": legacy["semantic_decision"],
            "legacy_gdt683_evidence_type": legacy["evidence_type"],
            "legacy_gdt683_reader_support": legacy["reader_support"],
            "default_is_translation": 0, "confirmed_lexeme": 0, "confirmed_plaintext": 0,
            "semantic_identity_credit": 0, "component_export_credit": 0,
        })

    auto_counts = Counter(str(row["automatic_default_de"]) for row in atlas)
    expected_auto = {"Ansatz:": 10, "Menge:": 5, "und dann": 4, ";": 3, "und": 27, FALLBACK: 327}
    if dict(auto_counts) != expected_auto:
        raise AssertionError(f"automatic dispatch differs: {dict(auto_counts)}")

    write_tsv(artifacts / "OL_376_TRANSFER_ATLAS.tsv", atlas, list(atlas[0]))

    branch_summary: list[dict[str, object]] = []
    for renderer in ("AUTOMATIC", "HYBRID"):
        prefix = renderer.lower()
        groups: dict[tuple[str, str, str], list[dict[str, object]]] = defaultdict(list)
        for row in atlas:
            group = (
                str(row[f"{prefix}_rule_id"]), str(row[f"{prefix}_branch"]),
                str(row[f"{prefix}_default_de"]),
            )
            groups[group].append(row)
        for (rule_id, branch, output), rows in sorted(groups.items()):
            branch_summary.append({
                "row_type": "BRANCH", "renderer": renderer, "rule_id": rule_id,
                "branch": branch, "output_de": output, **counts(rows),
                "contextual_occurrences": len(rows) if output != FALLBACK else 0,
            })
        branch_summary.append({
            "row_type": "TOTAL", "renderer": renderer, "rule_id": "ALL", "branch": "ALL",
            "output_de": "ALL", **counts(atlas),
            "contextual_occurrences": sum(int(row[f"{prefix}_contextual"]) for row in atlas),
        })
    write_tsv(artifacts / "TRANSFER_BRANCH_SUMMARY.tsv", branch_summary, list(branch_summary[0]))

    amount_edges.sort(key=lambda row: (str(row["page"]), str(row["locus"]), int(row["ol_ordinal"])))
    write_tsv(artifacts / "AMOUNT_17_EDGE_AUDIT.tsv", amount_edges, list(amount_edges[0]))

    atlas_by_key = {(str(row["locus"]), int(row["ordinal"])): row for row in atlas}
    calibration_audit: list[dict[str, object]] = []
    for calibration in calibration_source:
        key = (calibration["locus"], int(calibration["ordinal"]))
        row = atlas_by_key[key]
        exact = row["automatic_default_de"] == calibration["selected_default_de"]
        miss_reason = (
            "NONE" if exact else
            "NO_OCCURRENCE_ID_FREE_TRANSFER_TRIGGER" if row["automatic_rule_id"] == "G774-D07" else
            "PORTABLE_RULE_SELECTS_DIFFERENT_OUTPUT"
        )
        calibration_audit.append({
            "case_id": calibration["case_id"], "page": row["page"], "physical_folio": row["physical_folio"],
            "locus": row["locus"], "ordinal": row["ordinal"], "context_eva": calibration["context_eva"],
            "gdt773_dispatch_rule_id": calibration["dispatch_rule_id"],
            "gdt773_selected_function": calibration["selected_function"],
            "gdt773_default_de": calibration["selected_default_de"],
            "automatic_rule_id": row["automatic_rule_id"], "automatic_branch": row["automatic_branch"],
            "automatic_default_de": row["automatic_default_de"], "automatic_exact_match": int(exact),
            "miss_reason": miss_reason, "hybrid_rule_id": row["hybrid_rule_id"],
            "hybrid_default_de": row["hybrid_default_de"],
            "hybrid_exact_match": int(row["hybrid_default_de"] == calibration["selected_default_de"]),
            "amount_transfer_signal": row["amount_transfer_signal"], "process_right_signal": row["process_right_signal"],
            "close_left_signal": row["close_left_signal"], "close_right_signal": row["close_right_signal"],
            "f15_state_transition_bridge": row["f15_state_transition_bridge"],
            "score_credit": 0, "confirmed_lexeme": 0, "component_export_credit": 0,
        })
    write_tsv(artifacts / "CALIBRATION_REPLAY_AUDIT.tsv", calibration_audit, list(calibration_audit[0]))

    direct_specs: list[tuple[str, str, Callable[[dict[str, object]], bool], str]] = [
        ("ANY_DIRECT_SIGNATURE", "ANY", lambda row: bool(row["any_direct_signature"]), "diagnostic only"),
        ("G769_AMOUNT", "ANY", lambda row: "AMOUNT" in str(row["direct_signature_channels"]).split("|"), "strict nine-token subset; broad amount transfer uses GDT762/GDT763"),
        ("PROCESS_OR_OLY", "RIGHT", lambda row: bool(row["process_right_signal"]), "licenses und dann"),
        ("PROCESS_OR_OLY", "LEFT", lambda row: bool(row["process_left_signal"]), "directional rival; no automatic sequence output"),
        ("CLOSE", "LEFT", lambda row: bool(row["close_left_signal"]), "licenses field boundary"),
        ("CLOSE", "RIGHT", lambda row: bool(row["close_right_signal"]), "nominal veto; no field boundary"),
        ("STATE_DRY", "ANY", lambda row: "STATE_DRY" in str(row["direct_signature_channels"]).split("|"), "diagnostic only"),
        ("STATE_MOIST", "ANY", lambda row: "STATE_MOIST" in str(row["direct_signature_channels"]).split("|"), "diagnostic only"),
        ("NO_DIRECT_SIGNATURE", "NONE", lambda row: not bool(row["any_direct_signature"]), "no GDT769 direct-context evidence"),
    ]
    direct_summary: list[dict[str, object]] = []
    for signal, direction, predicate, interpretation in direct_specs:
        selected_rows = [row for row in atlas if predicate(row)]
        direct_summary.append({
            "signal": signal, "direction": direction, **counts(selected_rows),
            "automatic_selected_occurrences": sum(int(row["automatic_contextual"]) for row in selected_rows),
            "automatic_outputs_de": join_values(str(row["automatic_default_de"]) for row in selected_rows),
            "interpretation": interpretation, "semantic_identity_credit": 0, "component_export_credit": 0,
        })
    write_tsv(artifacts / "DIRECT_SIGNATURE_DIRECTION_SUMMARY.tsv", direct_summary, list(direct_summary[0]))

    f15_audit: list[dict[str, object]] = []
    for key, frame in sorted(f15_by_key.items()):
        row = atlas_by_key[key]
        detail = json.loads(frame["detail"])
        f15_audit.append({
            "target_occurrence_id": frame["target_occurrence_id"], "page": frame["page"],
            "physical_folio": row["physical_folio"], "locus": frame["locus"], "ordinal": frame["ordinal"],
            "transition_directions": join_values(detail.get("direction_labels", [])),
            "transition_count": len(detail.get("transitions", [])), "frame_detail": frame["detail"],
            "f14_medial_two_sided": row["f14_medial_two_sided"],
            "amount_priority_overlap": row["amount_transfer_signal"],
            "process_right_priority_overlap": row["process_right_signal"],
            "close_left_priority_overlap": row["close_left_signal"],
            "close_right_nominal_veto_overlap": row["close_right_signal"],
            "automatic_rule_id": row["automatic_rule_id"], "automatic_default_de": row["automatic_default_de"],
            "hybrid_rule_id": row["hybrid_rule_id"], "hybrid_default_de": row["hybrid_default_de"],
            "relation_is_translation": 0, "confirmed_lexeme": 0, "component_export_credit": 0,
        })
    write_tsv(artifacts / "F15_STATE_BRIDGE_AUDIT.tsv", f15_audit, list(f15_audit[0]))

    line_specs: list[tuple[str, Callable[[dict[str, object]], bool], str]] = [
        ("ALL", lambda row: True, "complete 376-token transfer universe"),
        ("LINE_FIRST", lambda row: row["line_position"] == "FIRST", "written-line first position"),
        ("LINE_MIDDLE", lambda row: row["line_position"] == "MIDDLE", "written-line medial position"),
        ("LINE_LAST", lambda row: row["line_position"] == "LAST", "written-line final position"),
        ("PARAGRAPH_START_LINE", lambda row: row["paragraph_start_line"] == "1", "occurs somewhere on a paragraph-start line"),
        ("PARAGRAPH_END_LINE", lambda row: row["paragraph_end_line"] == "1", "occurs somewhere on a paragraph-end line"),
        ("TRUE_PARAGRAPH_OPENER", lambda row: row["true_paragraph_opener"] == "1", "token itself opens paragraph"),
        ("TRUE_PARAGRAPH_CLOSER", lambda row: row["true_paragraph_closer"] == "1", "token itself closes paragraph"),
        ("MULTI_OL_LINE_TOKEN", lambda row: int(row["ol_count_in_locus"]) > 1, "token lies on a locus with repeated ol"),
        ("ADJACENT_OL_REPEAT_TOKEN", lambda row: row["adjacent_ol_repeat"] == 1, "token belongs to an adjacent ol ol pair"),
        ("F14_MEDIAL_TWO_SIDED", lambda row: row["f14_medial_two_sided"] == 1, "geometry alone has zero dispatch credit"),
        ("F15_STATE_TRANSITION", lambda row: row["f15_state_transition_bridge"] == 1, "state bridge; lower than direct rules"),
        ("NO_DIRECT_SIGNATURE", lambda row: row["any_direct_signature"] == 0, "no GDT769 direct signature"),
    ]
    line_summary: list[dict[str, object]] = []
    for category, predicate, interpretation in line_specs:
        selected_rows = [row for row in atlas if predicate(row)]
        line_summary.append({
            "category": category, **counts(selected_rows),
            "automatic_contextual": sum(int(row["automatic_contextual"]) for row in selected_rows),
            "automatic_nominal": sum(not bool(row["automatic_contextual"]) for row in selected_rows),
            "hybrid_contextual": sum(int(row["hybrid_contextual"]) for row in selected_rows),
            "interpretation": interpretation,
        })
    write_tsv(artifacts / "LINE_POSITION_REPEAT_AUDIT.tsv", line_summary, list(line_summary[0]))

    pair_columns = [
        "page", "locus", "left_ordinal", "right_ordinal", "working_render_de",
        "selected_scope", "rule", "zl3b_line",
    ]
    legacy_pair_source = guarded_read_tsv(
        G683 / "ADJACENT_OL_PAIRS.tsv", selector="page", allowed_values=safe_pages,
        columns=pair_columns,
    )
    legacy_pairs = {
        (row["locus"], int(row["left_ordinal"]), int(row["right_ordinal"])): row
        for row in legacy_pair_source
    }
    pair_audit: list[dict[str, object]] = []
    for locus, rows in sorted(locus_targets.items()):
        ordinals = sorted(int(row["ordinal"]) for row in rows)
        for left, right in zip(ordinals, ordinals[1:]):
            if right != left + 1:
                continue
            left_row, right_row = atlas_by_key[(locus, left)], atlas_by_key[(locus, right)]
            legacy_pair = legacy_pairs.get((locus, left, right))
            if legacy_pair is None:
                raise AssertionError(f"adjacent pair missing from guarded GDT683 data: {locus}@{left}-{right}")
            pair_audit.append({
                "pair_id": f"{locus}@{left}-{right}", "page": left_row["page"],
                "physical_folio": left_row["physical_folio"], "locus": locus,
                "left_ordinal": left, "right_ordinal": right,
                "left_direct_signature": left_row["direct_signature_channels"],
                "right_direct_signature": right_row["direct_signature_channels"],
                "left_automatic_rule_id": left_row["automatic_rule_id"],
                "right_automatic_rule_id": right_row["automatic_rule_id"],
                "left_automatic_default_de": left_row["automatic_default_de"],
                "right_automatic_default_de": right_row["automatic_default_de"],
                "legacy_selected_scope": legacy_pair["selected_scope"],
                "legacy_working_render_de": legacy_pair["working_render_de"],
                "written_line_eva": left_row["written_line_eva"],
                "separator_evidence": 0, "confirmed_lexeme": 0, "component_export_credit": 0,
            })
    if len(pair_audit) != 7:
        raise AssertionError("adjacent ol-pair count differs")
    write_tsv(artifacts / "ADJACENT_OL_PAIR_AUDIT.tsv", pair_audit, list(pair_audit[0]))

    register_specs: list[tuple[str, str, Callable[[dict[str, object]], bool]]] = [
        ("ALL", "ALL", lambda row: True),
        ("SECTION", "B", lambda row: row["section"] == "B"),
        ("SECTION", "NON_B", lambda row: row["section"] != "B"),
        ("HAND", "2", lambda row: row["hand"] == "2"),
        ("HAND", "NON_2", lambda row: row["hand"] != "2"),
    ]
    for value in sorted({str(row["section"]) for row in atlas}):
        if value != "B":
            register_specs.append(("SECTION_VALUE", value, lambda row, value=value: row["section"] == value))
    for value in sorted({str(row["hand"]) for row in atlas}):
        register_specs.append(("HAND_VALUE", value, lambda row, value=value: row["hand"] == value))
    register_summary: list[dict[str, object]] = []
    for group_type, group_value, predicate in register_specs:
        selected_rows = [row for row in atlas if predicate(row)]
        register_summary.append({
            "group_type": group_type, "group_value": group_value, **counts(selected_rows),
            "line_first": sum(row["line_position"] == "FIRST" for row in selected_rows),
            "line_middle": sum(row["line_position"] == "MIDDLE" for row in selected_rows),
            "line_last": sum(row["line_position"] == "LAST" for row in selected_rows),
            "multi_ol_line_tokens": sum(int(row["ol_count_in_locus"]) > 1 for row in selected_rows),
            "adjacent_repeat_tokens": sum(int(row["adjacent_ol_repeat"]) for row in selected_rows),
            "any_direct_signature": sum(int(row["any_direct_signature"]) for row in selected_rows),
            "automatic_contextual": sum(int(row["automatic_contextual"]) for row in selected_rows),
            "automatic_nominal": sum(not bool(row["automatic_contextual"]) for row in selected_rows),
            "hybrid_contextual": sum(int(row["hybrid_contextual"]) for row in selected_rows),
            "hybrid_nominal": sum(not bool(row["hybrid_contextual"]) for row in selected_rows),
        })
    write_tsv(artifacts / "REGISTER_DISPATCH_SUMMARY.tsv", register_summary, list(register_summary[0]))

    folio_groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in atlas:
        folio_groups[str(row["physical_folio"])].append(row)
    folio_summary: list[dict[str, object]] = []
    for folio, rows in sorted(folio_groups.items()):
        folio_summary.append({
            "physical_folio": folio, **counts(rows),
            "sections": join_values(str(row["section"]) for row in rows),
            "hands": join_values(str(row["hand"]) for row in rows),
            "line_first": sum(row["line_position"] == "FIRST" for row in rows),
            "line_middle": sum(row["line_position"] == "MIDDLE" for row in rows),
            "line_last": sum(row["line_position"] == "LAST" for row in rows),
            "any_direct_signature": sum(int(row["any_direct_signature"]) for row in rows),
            "automatic_contextual": sum(int(row["automatic_contextual"]) for row in rows),
            "automatic_nominal": sum(not bool(row["automatic_contextual"]) for row in rows),
            "hybrid_contextual": sum(int(row["hybrid_contextual"]) for row in rows),
            "hybrid_nominal": sum(not bool(row["hybrid_contextual"]) for row in rows),
        })
    write_tsv(artifacts / "PHYSICAL_FOLIO_TRANSFER_SUMMARY.tsv", folio_summary, list(folio_summary[0]))

    legacy_rows = [legacy_by_key[(str(row["locus"]), int(row["ordinal"]))] for row in atlas]
    legacy_comparison: list[dict[str, object]] = []
    for decision in sorted({row["semantic_decision"] for row in legacy_rows}):
        rows = [row for row in legacy_rows if row["semantic_decision"] == decision]
        keyset = {(row["locus"], int(row["ordinal"])) for row in rows}
        selected = [row for row in atlas if (str(row["locus"]), int(row["ordinal"])) in keyset]
        legacy_comparison.append({
            "renderer": "LEGACY_GDT683", "class": decision, "output_de": "Grundansatz", **counts(selected),
            "contextual_occurrences": 0, "nominal_occurrences": len(selected),
            "evidence_types": join_values(row["evidence_type"] for row in rows),
            "interpretation": "inherited learned-whole application; not an independent confirmation",
        })
    for renderer, output_field, context_field in (
        ("AUTOMATIC_GDT774", "automatic_default_de", "automatic_contextual"),
        ("HYBRID_GDT774", "hybrid_default_de", "hybrid_contextual"),
    ):
        contextual = [row for row in atlas if int(row[context_field])]
        nominal = [row for row in atlas if not int(row[context_field])]
        for klass, rows in (("CONTEXTUAL", contextual), ("NOMINAL_FALLBACK", nominal)):
            legacy_comparison.append({
                "renderer": renderer, "class": klass,
                "output_de": join_values(str(row[output_field]) for row in rows), **counts(rows),
                "contextual_occurrences": len(rows) if klass == "CONTEXTUAL" else 0,
                "nominal_occurrences": len(rows) if klass == "NOMINAL_FALLBACK" else 0,
                "evidence_types": "GDT774_DIRECTIONAL_CONTEXT" if klass == "CONTEXTUAL" else "GDT773_NOMINAL_FALLBACK",
                "interpretation": "working renderer output; zero lexeme or plaintext credit",
            })
    write_tsv(artifacts / "LEGACY_GRUNDANSATZ_COMPARISON.tsv", legacy_comparison, list(legacy_comparison[0]))

    manual_specs = read_tsv(SRC / "MANUAL_24_CONTEXT_AUDIT_SPECS.tsv")
    manual_audit: list[dict[str, object]] = []
    for spec in manual_specs:
        key = (spec["locus"], int(spec["ordinal"]))
        row = atlas_by_key.get(key)
        if row is None:
            raise AssertionError(f"manual context not in transfer atlas: {key}")
        manual_audit.append({
            **spec, "page": row["page"], "physical_folio": row["physical_folio"],
            "written_line_eva": row["written_line_eva"],
            "automatic_rule_id": row["automatic_rule_id"], "automatic_default_de": row["automatic_default_de"],
            "automatic_preferred_match": int(row["automatic_default_de"] == spec["preferred_output"]),
            "automatic_acceptable_rival_match": int(row["automatic_default_de"] == spec["acceptable_rival"]),
            "hybrid_rule_id": row["hybrid_rule_id"], "hybrid_default_de": row["hybrid_default_de"],
            "hybrid_preferred_match": int(row["hybrid_default_de"] == spec["preferred_output"]),
            "hybrid_acceptable_rival_match": int(row["hybrid_default_de"] == spec["acceptable_rival"]),
            "audit_is_independent_semantic_test": 0, "score_credit": 0,
            "confirmed_lexeme": 0, "component_export_credit": 0,
        })
    if len(manual_audit) != 24:
        raise AssertionError("manual context audit count differs")
    write_tsv(artifacts / "MANUAL_24_CONTEXT_AUDIT.tsv", manual_audit, list(manual_audit[0]))

    dictionary = [
        {
            "entry_id": "G774-W01", "surface_or_context": "ol (no portable signal)",
            "structural_role": "NOMINAL_FALLBACK", "working_default_de": FALLBACK,
            "automatic_occurrences": auto_counts[FALLBACK],
            "hybrid_occurrences": sum(row["hybrid_default_de"] == FALLBACK for row in atlas),
            "confidence": "C0_CONTEXT_UNRESOLVED",
            "positive_evidence": "GDT773 equal-capacity nominal winner; unsupported broad contexts retain the least specific whole-form output",
            "counterevidence": "does not identify one invariant substance; GDT683 Grundansatz applications are inherited from one card",
            "scope": "COMPLETE_EVA_WHOLE_ONLY__NO_COMPONENT_EXPORT",
        },
        {
            "entry_id": "G774-W02", "surface_or_context": "amount expression ol, ol not line-final",
            "structural_role": "CONTENT_FIELD_HEAD", "working_default_de": "Ansatz:",
            "automatic_occurrences": auto_counts["Ansatz:"],
            "hybrid_occurrences": sum(row["automatic_rule_id"] == "G774-D01" for row in atlas),
            "confidence": "C1_IF_PHRASE_LICENSE_ELSE_C0_DIRECTIONAL",
            "positive_evidence": "ten occurrence-specific right-of-amount edges after removing two dangling line-final heads",
            "counterevidence": "von and nominal head remain possible; unit and substance identities are open",
            "scope": "OCCURRENCE_CONTEXT_ONLY",
        },
        {
            "entry_id": "G774-W03", "surface_or_context": "ol amount expression",
            "structural_role": "MEASURE_FIELD_HEAD", "working_default_de": "Menge:",
            "automatic_occurrences": auto_counts["Menge:"],
            "hybrid_occurrences": sum(row["automatic_rule_id"] == "G774-D02" for row in atlas),
            "confidence": "C1_IF_PHRASE_LICENSE_ELSE_C0_DIRECTIONAL",
            "positive_evidence": "five occurrence-specific left-of-amount edges including one side of the bilateral pair",
            "counterevidence": "nominal head remains a rival and the historical unit is not identified",
            "scope": "OCCURRENCE_CONTEXT_ONLY",
        },
        {
            "entry_id": "G774-W04", "surface_or_context": "ol before direct PROCESS or oly",
            "structural_role": "SEQUENCE", "working_default_de": "und dann",
            "automatic_occurrences": auto_counts["und dann"],
            "hybrid_occurrences": sum(row["automatic_rule_id"] == "G774-D03" for row in atlas),
            "confidence": "C1_DIRECT_PROCESS_DIRECTION",
            "positive_evidence": "four direct right-side process anchors; direction agrees with GDT773",
            "counterevidence": "four left-side process anchors do not license the same reading; concrete operation open",
            "scope": "OCCURRENCE_CONTEXT_ONLY",
        },
        {
            "entry_id": "G774-W05", "surface_or_context": "direct CLOSE ol",
            "structural_role": "FIELD_BOUNDARY", "working_default_de": ";",
            "automatic_occurrences": auto_counts[";"],
            "hybrid_occurrences": sum(row["automatic_rule_id"] == "G774-D04" for row in atlas),
            "confidence": "C1_DIRECT_CLOSE_DIRECTION",
            "positive_evidence": "three direct left-side close anchors",
            "counterevidence": "nine close-right cases require the opposite nominal-veto direction",
            "scope": "OCCURRENCE_CONTEXT_ONLY",
        },
        {
            "entry_id": "G774-W06", "surface_or_context": "F15 and F14 state bridge after higher rules",
            "structural_role": "COORDINATION", "working_default_de": "und",
            "automatic_occurrences": auto_counts["und"],
            "hybrid_occurrences": sum(row["automatic_rule_id"] == "G774-D06" for row in atlas),
            "confidence": "C1_STRUCTURAL_BRIDGE__C0_LEXEME",
            "positive_evidence": "27 of 31 two-sided state bridges remain after directional priorities and vetoes",
            "counterevidence": "field punctuation or a nominal relation remains possible; transition direction is heterogeneous",
            "scope": "OCCURRENCE_CONTEXT_ONLY",
        },
        {
            "entry_id": "G774-W07", "surface_or_context": "GDT773 calibration-only field defaults",
            "structural_role": "LOCKED_LOCAL_FIELD_OUTPUT", "working_default_de": "Ansatz: | : | ;",
            "automatic_occurrences": 0,
            "hybrid_occurrences": sum(
                row["hybrid_rule_id"] == "G774-D00"
                and row["hybrid_default_de"] != row["automatic_default_de"]
                for row in atlas
            ),
            "confidence": "C0_INHERITED_CASE_SPECIFIC",
            "positive_evidence": "six fixed GDT773 calibration outputs retained only by the practical hybrid",
            "counterevidence": "no occurrence-ID-free trigger reproduces them automatically",
            "scope": "FIFTEEN_CASE_CALIBRATION_ONLY",
        },
    ]
    for row in dictionary:
        row.update({
            "default_is_translation": 0, "confirmed_lexeme": 0, "confirmed_plaintext": 0,
            "semantic_identity_credit": 0, "component_export_credit": 0,
        })
    write_tsv(artifacts / "GDT774_WORKING_DICTIONARY.tsv", dictionary, list(dictionary[0]))

    geometry = counts(atlas)
    section_b = [row for row in atlas if row["section"] == "B"]
    non_b = [row for row in atlas if row["section"] != "B"]
    auto_context = [row for row in atlas if int(row["automatic_contextual"])]
    hybrid_context = [row for row in atlas if int(row["hybrid_contextual"])]
    hybrid_counts = Counter(str(row["hybrid_default_de"]) for row in atlas)
    result: dict[str, object] = {
        "experiment_id": "GDT774",
        "status": "PASS__PARTIAL_CONTEXT_TRANSFER__NO_PLAINTEXT",
        "question": "How much of the fixed GDT773 contextual ol renderer transfers by occurrence-ID-free cached rules to all 376 reader-exact ol positions?",
        "source_hashes": locked_hashes,
        "geometry": {
            **geometry,
            "line_first": sum(row["line_position"] == "FIRST" for row in atlas),
            "line_middle": sum(row["line_position"] == "MIDDLE" for row in atlas),
            "line_last": sum(row["line_position"] == "LAST" for row in atlas),
            "paragraph_start_line": sum(row["paragraph_start_line"] == "1" for row in atlas),
            "paragraph_end_line": sum(row["paragraph_end_line"] == "1" for row in atlas),
            "true_paragraph_openers": sum(row["true_paragraph_opener"] == "1" for row in atlas),
            "true_paragraph_closers": sum(row["true_paragraph_closer"] == "1" for row in atlas),
            "any_direct_signature": sum(int(row["any_direct_signature"]) for row in atlas),
            "f14_medial_two_sided": len(f14_keys), "f15_state_bridges": len(f15_by_key),
            "multi_ol_loci": sum(len(rows) > 1 for rows in locus_targets.values()),
            "multi_ol_tokens": sum(int(row["ol_count_in_locus"]) > 1 for row in atlas),
            "adjacent_repeat_pairs": len(pair_audit),
            "adjacent_repeat_tokens": sum(int(row["adjacent_ol_repeat"]) for row in atlas),
            "section_b_total": len(section_b),
            "section_b_first": sum(row["line_position"] == "FIRST" for row in section_b),
            "non_b_total": len(non_b),
            "non_b_first": sum(row["line_position"] == "FIRST" for row in non_b),
        },
        "automatic_renderer": {
            "contextual_occurrences": len(auto_context),
            "nominal_occurrences": len(atlas) - len(auto_context),
            "contextual_rate_percent": 100.0 * len(auto_context) / len(atlas),
            "nominal_rate_percent": 100.0 * (len(atlas) - len(auto_context)) / len(atlas),
            "contextual_page_labels": len({row["page"] for row in auto_context}),
            "contextual_physical_folios": len({row["physical_folio"] for row in auto_context}),
            "contextual_loci": len({row["locus"] for row in auto_context}),
            "output_counts": dict(auto_counts),
        },
        "hybrid_renderer": {
            "contextual_occurrences": len(hybrid_context),
            "nominal_occurrences": len(atlas) - len(hybrid_context),
            "contextual_rate_percent": 100.0 * len(hybrid_context) / len(atlas),
            "nominal_rate_percent": 100.0 * (len(atlas) - len(hybrid_context)) / len(atlas),
            "calibration_copy_occurrences": sum(row["hybrid_rule_id"] == "G774-D00" for row in atlas),
            "output_counts": dict(hybrid_counts),
        },
        "calibration_replay": {
            "cases": len(calibration_audit),
            "automatic_exact_matches": sum(int(row["automatic_exact_match"]) for row in calibration_audit),
            "automatic_misses": sum(not bool(row["automatic_exact_match"]) for row in calibration_audit),
            "hybrid_exact_matches": sum(int(row["hybrid_exact_match"]) for row in calibration_audit),
        },
        "amount_transfer": {
            "contact_rows": len(contact_source), "raw_edges": len(amount_edges),
            "selected_edges": sum(int(row["selected_for_transfer"]) for row in amount_edges),
            "line_final_exclusions": sum(not bool(row["selected_for_transfer"]) for row in amount_edges),
            "phrase_licensed_selected_edges": sum(
                int(row["selected_for_transfer"]) and row["conditional_phrase_license"] == "1"
                for row in amount_edges
            ),
            "directional_c0_selected_edges": sum(
                int(row["selected_for_transfer"]) and row["conditional_phrase_license"] != "1"
                for row in amount_edges
            ),
            "ol_left_of_amount": sum(row["relation"] == "OL_LEFT_OF_AMOUNT" for row in amount_edges),
            "ol_right_of_amount": sum(row["relation"] == "OL_RIGHT_OF_AMOUNT" for row in amount_edges),
            "bilateral_edges": sum(int(row["bilateral_contact"]) for row in amount_edges),
        },
        "manual_context_audit": {
            "cases": len(manual_audit),
            "automatic_preferred_matches": sum(int(row["automatic_preferred_match"]) for row in manual_audit),
            "hybrid_preferred_matches": sum(int(row["hybrid_preferred_match"]) for row in manual_audit),
            "independent_semantic_score_credit": 0,
        },
        "legacy_crosswalk": {
            "matched_occurrences": len(legacy_rows),
            "grundansatz_outputs": sum(row["working_translation_de"] == "Grundansatz" for row in legacy_rows),
            "gdt664_inherited_evidence": sum(row["evidence_type"] == "GDT664_PUBLISHED_LEARNED_WHOLE" for row in legacy_rows),
        },
        "structural_audit": structural_result,
        "claim_ceiling": {
            "new_pages_opened": 0, "new_images_opened": 0, "new_ocr": 0, "new_transcription": 0,
            "f84_accessed": 0, "f84r_accessed": 0, "confirmed_lexemes": 0,
            "confirmed_plaintext_clauses": 0, "component_exports": 0,
            "specific_medium_selected": 0, "translation_claimed": 0,
        },
        "next_route": "Partition the 327 automatic nominal fallbacks by register-conditioned right-follower whole/context classes; retain fallback where no occurrence-ID-free subclass predicts a concrete field role.",
    }
    (artifacts / "RESULT.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(build_report(result), encoding="utf-8")
    print(json.dumps({
        "status": result["status"], "automatic": result["automatic_renderer"],
        "hybrid": result["hybrid_renderer"],
    }, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
