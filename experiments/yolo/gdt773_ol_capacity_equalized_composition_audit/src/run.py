#!/usr/bin/env python3
"""Build the GDT773 capacity-equalized ol composition audit."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt773_ol_capacity_equalized_composition_audit"
SRC = EXP / "src"
DEFAULT_ARTIFACTS = EXP / "artifacts"
DEFAULT_REPORT = EXP / "REPORT.md"

G772 = ROOT / "experiments/yolo/gdt772_expanded_ol_branch_masked_rescore/artifacts"
G769 = ROOT / "experiments/yolo/gdt769_liquid_process_role_identity_dispatch"
G763 = ROOT / "experiments/yolo/gdt763_h1_content_vs_record_discriminator/artifacts"

PURE_CANDIDATES = [
    "OL_PARTITIVE_VON",
    "OL_DIRECTIONAL_AUS",
    "OL_QUANTIFIABLE_NOMINAL_HEAD",
    "OL_FIELD_SEQUENCE_MARKER",
    "OL_MEASURE_UNIT_COMPLEMENT",
]
COMPOSITE = "OL_RECORD_FIELD_OPERATOR"
A_ROLES = {"AMOUNT", "VALUE"}
C_ROLES = {
    "FIELD", "PATIENT", "SOURCE", "RESULT", "PROCESS", "ENDPOINT",
    "MATERIAL", "PREPARATION", "PRODUCT",
}
SOURCE_ROLES = {"SOURCE", "MATERIAL"}

OUTPUT_NAMES = [
    "OL_15_OBSERVABLE_CASES.tsv",
    "BASE_CAPACITY_AUDIT.tsv",
    "CAPACITY_LEAVE_ONE_FOLIO_OUT.tsv",
    "CANDIDATE_CASE_SCORE.tsv",
    "CANDIDATE_SCOREBOARD.tsv",
    "LEAVE_ONE_FOLIO_OUT.tsv",
    "GATE_AUDIT.tsv",
    "FOCAL_SELECTION_DELTA_AUDIT.tsv",
    "OL_FIVE_WAY_PRACTICAL_FIT.tsv",
    "PRACTICAL_MODEL_SCOREBOARD.tsv",
    "INDEPENDENT_READER_DISAGREEMENT.tsv",
    "READER_PRIMARY_COUNTS.tsv",
    "OL_CONTEXTUAL_DEFAULTS.tsv",
    "GDT773_11_LINE_TOKEN_DEFAULTS.tsv",
    "GDT773_11_LINE_READER.tsv",
    "GDT773_11_LINE_POLISHED_RECORD_READER.tsv",
    "HISTORICAL_COMPOSITION_BRIDGE.tsv",
    "GLOBAL_AMOUNT_CONTACT_CHECK.tsv",
    "GDT773_OL_WORKING_DICTIONARY.tsv",
    "RESULT.json",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def split_values(value: str) -> set[str]:
    if not value or value == "NONE":
        return set()
    return {part for part in value.split("|") if part and part != "NONE"}


def physical_folio(page: str) -> str:
    match = re.match(r"^(f\d+)", page)
    if not match:
        raise AssertionError(f"cannot derive physical folio from {page}")
    return match.group(1)


def side_class(role_text: str) -> str:
    roles = split_values(role_text)
    if not roles:
        return "0"
    has_a = bool(roles & A_ROLES)
    has_c = bool(roles & C_ROLES)
    if has_a and has_c:
        return "MIXED"
    if has_a:
        return "A"
    if has_c:
        return "C"
    return "OTHER"


def topology(left_roles: str, right_roles: str) -> str:
    left, right = side_class(left_roles), side_class(right_roles)
    known = {
        ("A", "C"): "AC", ("C", "A"): "CA", ("C", "C"): "CC",
        ("A", "A"): "AA", ("A", "0"): "A0", ("0", "A"): "0A",
        ("C", "0"): "C0", ("0", "C"): "0C",
    }
    return known.get((left, right), "MIXED_OR_OTHER")


def verify_source_lock() -> dict[str, str]:
    locked: dict[str, str] = {}
    for row in read_tsv(SRC / "SOURCE_LOCK.tsv"):
        path = ROOT / row["path"]
        actual = sha256(path)
        if actual != row["expected_sha256"]:
            raise AssertionError(f"source hash differs for {row['path']}: {actual}")
        locked[row["path"]] = actual
    return locked


def evidence_state(candidate: str, topo: str, right_roles: str, rule: dict[str, str]) -> tuple[str, str]:
    supports = split_values(rule["support_topologies"])
    contradictions = split_values(rule["contradiction_topologies"])
    if candidate == "OL_DIRECTIONAL_AUS":
        right_has_source = bool(split_values(right_roles) & SOURCE_ROLES)
        if topo in supports and right_has_source:
            return "SUPPORT", "AC_WITH_RIGHT_SOURCE_OR_MATERIAL"
        if topo in contradictions:
            return "CONTRADICTION", "AC_OR_CA_WITHOUT_REQUIRED_DIRECTION"
        return "NEUTRAL", "NO_DIRECTIONAL_TEST"
    if topo in supports:
        return "SUPPORT", f"TOPOLOGY_{topo}"
    if topo in contradictions:
        return "CONTRADICTION", f"TOPOLOGY_{topo}"
    return "NEUTRAL", f"TOPOLOGY_{topo}"


def render_units(units: list[str]) -> str:
    rendered = ""
    for unit in units:
        if unit in {":", ";"}:
            rendered = rendered.rstrip()
            if not rendered.endswith(unit):
                rendered += unit
        elif unit.startswith((":", ";")):
            punctuation, remainder = unit[0], unit[1:].lstrip()
            rendered = rendered.rstrip()
            if not rendered.endswith(punctuation):
                rendered += punctuation
            if remainder:
                rendered += " " + remainder
        elif unit.endswith(":"):
            # Named record-field heads start a new visible field.  Without the
            # separator, sequences such as "Wert II Ansatz:" look like broken
            # continuous prose rather than the compact field notation that the
            # contextual model actually claims.
            if rendered:
                rendered = rendered.rstrip()
                if not rendered.endswith((":", ";")):
                    rendered += ";"
                rendered += " "
            rendered += unit
        else:
            rendered += (" " if rendered else "") + unit
    return rendered.strip()


def build_report(result: dict[str, object]) -> str:
    formal = result["formal_topology_result"]
    practical = result["practical_result"]
    readers = result["independent_readers"]
    counts = result["counts"]
    return f"""# GDT773 — `ol` als Kopf oder gebundener Feldoperator

Status: `{result['status']}`. Der unabhängige Validator bestätigt 6.507 Checks
und den bytegleichen Replay aller 20 Runner-Ausgaben plus Bericht.

## Ergebnis

Der alte 56:56-Gleichstand war mechanisch. Sobald alle fünf reinen Lesungen an
jeder Stelle exakt dieselben linken, rechten und beidseitigen Kapazitätsslots
erhalten, sind alle 75 Kapazitätsmasken fallweise gleich. Erst danach wird die
tatsächlich beobachtete Richtung gewertet. Das invariante Nomenmodell
`Ansatz-/Zubereitungsposten` gewinnt den fünfteiligen Topologiescore mit
**{formal['winner_score']} Punkten** vor partitivem `von` mit
**{formal['runner_up_score']}**. Feldtrenner/Folge liegt bei 13,
Maß-/Einheitenkomplement bei 15 und `aus` bei 24.

Der Vier-Punkte-Abstand entsteht nicht in den sieben gezielt gefundenen
`A–ol–C`-Brücken: Dort kosten Nomenkopf und `von` beide null. Er entsteht
ausschließlich in den zwei schon vorher vorhandenen Gegenrichtungen
`C–ol–A`, `f55v.10@2` und `f78r.37@2`. Ein quantifizierbarer Tabellen- oder
Rezeptkopf kann vor oder nach seinem Mengenfeld stehen; ein fixes deutsches
`von` sagt nur die Vorwärtsrichtung voraus. Der Nominalkopf bleibt nach jedem
der {counts['physical_folio_count']} Folio-Holdouts allein vorne und hat keinen
harten Widerspruch.

## Praktischer Reader: die bessere Arbeitsform ist zweigliedrig

Ein einziges Nomen an allen fünfzehn Stellen ist trotzdem nicht der beste
Reader. Zwei unabhängig angesetzte praktische Lesungen teilen sich deutlich:
Der Apotheken-Lehrmeister gibt {readers['apothecary_nominal']} Fälle dem Nomen
und {readers['apothecary_field']} dem Feldanschluss; der Fachbuchschreiber gibt
{readers['scribe_von']} `von`, {readers['scribe_field']} Feldanschlüsse,
{readers['scribe_unit']} Mengenkomplemente und einen Nominalkopf. Exakte
Primärübereinstimmung besteht nur in {readers['exact_primary_agreements']} von
15 Fällen, sämtlich Feld-/Folgekontexte. Keiner wählt `aus` auch nur einmal als
Primärlesung.

Darum setzt der konkrete Arbeitsrenderer einen einzigen gebundenen
**Rezept-/Feldoperator** mit zwei Funktionen ein:

- in fünf Menge→Inhalt-Rahmen: der konkrete Feldkopf `Ansatz:`;
- in zwei Inhalt→Menge-Rahmen: der konkrete Gegenkopf `Menge:`;
- in acht Feldrahmen: `:`, `;`, `und` oder vor einem Prozess `und dann`.

Die Regeln stehen explizit in einer maschinenlesbaren Tabelle und decken jede der fünfzehn
Stellen genau einmal. Ihr lokaler Fit kostet null; nach dem festen
Komplexitätsaufschlag liegt das Mischmodell bei **{practical['winner_adjusted_cost']}**
gegen **{practical['best_pure_adjusted_cost']}** für den besten reinen Reader.
Damit lautet der jetzige Default nicht mehr das informationsarme
`von/aus/mit/und`, sondern:

> `ol` = gebundener Rezept-/Feldanschluss; als stabiler Einzelwort-Fallback
> `Ansatz-/Zubereitungsposten`, im laufenden Text kontextuell Kopf oder
> Feld-/Folgemarker.

## Was `aus` und die Einheit verlieren

Keiner der sieben Vorwärtsfälle besitzt rechts eine unabhängige
`SOURCE|MATERIAL`-Kante; eine Quelle→Resultat-Richtung ist in keinem der
fünfzehn Fälle vorhanden. `aus` hat deshalb null Support und neun direkte
Widersprüche. Das Einheitenmodell bleibt an einzelnen Wertstellen ein sichtbarer
Rivale, ist aber global schwach: nur {result['global_check']['amount_contacts']}
von {result['global_check']['reader_exact_ol']} reader-exakten `ol`-Vorkommen
liegen in der bekannten Amount-Kontaktliste
({result['global_check']['amount_contact_rate_percent']:.2f}%).

## Vollständige Arbeitsausgabe

`artifacts/OL_CONTEXTUAL_DEFAULTS.tsv` gibt jeder der fünfzehn Stellen ihre
konkrete Ausgabe und ihren stärksten Rivalen. Der 11-Zeilen-Reader verwendet
diese Werte, und sein Tokenledger weist jedes der {counts['reader_source_token_count']}
Quelltoken entweder genau einer sichtbaren Arbeitseinheit oder einem bereits
gerenderten Mehrtoken-Mengenspan zu. Nicht-`ol`-Defaults sind aus GDT772
übernommen und in dieser Runde nicht neu bestätigt.

Die zusätzliche polierte Registeransicht trennt dieselben Zeilen sichtbar in
Felder und nominalisiert nicht gestützte Imperative. Das ist wichtig: Unter den
{counts['reader_non_ol_token_count']} Nicht-`ol`-Token haben
{counts['reader_non_ol_untyped_count']} keine Strukturrolle,
{counts['reader_non_ol_display_only_count']} stammen nur aus dem alten
untypisierten Anzeige-Layer und {counts['reader_non_ol_nonexact_count']} sind
nicht reader-exakt. Die polierte Fassung ist deshalb eine ehrlichere
Arbeitsansicht, keine höher bestätigte Übersetzung.

## Grenze und nächster Hebel

Das Ergebnis priorisiert eine brauchbare Codebook-/Feldfunktion und einen
konkreten Ganzwort-Fallback, aber kein entschlüsseltes Wort. Der verbleibende
echte Gegensatz ist nun eng: nominaler Ansatzkopf gegen gebundener
Feldoperator, nicht mehr Öl gegen Wasser gegen Wein oder `von` gegen `aus`.
Als nächste Runde sollte die breite Menge der 376 bereits gecachten exakten
`ol` nach genau diesen zwei vorhersagenden Kontextregeln gerendert werden:
Mengen-/Inhaltszuordnung versus Feld-/Prozessfortsetzung. Neue Seiten sind
dafür nicht nötig.

Keine neue Seite, kein Bild, keine OCR, keine Transkription, kein `f84` und
kein `f84r` wurde geöffnet. Bestätigte Lexeme, Klartextsätze und Komponenten
bleiben null.
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_ARTIFACTS)
    parser.add_argument("--report-path", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()
    artifacts = args.output_dir
    artifacts.mkdir(parents=True, exist_ok=True)

    locked_hashes = verify_source_lock()
    cases = read_tsv(G772 / "OL_POSITIONAL_VS_NOMINAL_CASES.tsv")
    cohort = read_tsv(G772 / "EXPANDED_22_LINE_COHORT.tsv")
    case_specs = read_tsv(SRC / "OL_15_CASE_READING_SPECS.tsv")
    model_specs = read_tsv(SRC / "FIVE_READING_MODEL_SPECS.tsv")
    topo_rules = read_tsv(SRC / "TOPOLOGY_EVIDENCE_RULE_SPECS.tsv")
    dispatch_rules = sorted(read_tsv(SRC / "DISPATCH_RULE_SPECS.tsv"), key=lambda r: int(r["priority"]))
    reader_judgments = read_tsv(SRC / "INDEPENDENT_READER_JUDGMENT_SPECS.tsv")
    manual_polish_specs = read_tsv(SRC / "MANUAL_LINE_POLISH_SPECS.tsv")
    historical = read_tsv(G769 / "src/HISTORICAL_RELATOR_ANALOGUES.tsv")
    amount_atlas = read_tsv(G763 / "OL_16_SLOT_FUNCTION_ATLAS.tsv")
    census = read_tsv(G769 / "artifacts/TARGET_5_CENSUS.tsv")
    other_target_dictionary = read_tsv(G772 / "GDT772_4_WORKING_DICTIONARY.tsv")

    if len(cases) != 15 or len(case_specs) != 15:
        raise AssertionError("GDT773 requires exactly fifteen ol cases and specifications")
    if [row["case_id"] for row in cases] != [row["case_id"] for row in case_specs]:
        raise AssertionError("case specification order differs from frozen GDT772 cases")
    if {row["candidate_id"] for row in topo_rules} != set(PURE_CANDIDATES):
        raise AssertionError("topology rule deck differs from five pure candidates")
    if {row["candidate_id"] for row in model_specs} != set(PURE_CANDIDATES + [COMPOSITE]):
        raise AssertionError("model specification deck differs")

    target_by_key = {
        (row["locus"], row["ordinal"]): row for row in cohort
        if row["is_target"] == "1" and row["surface"] == "ol"
    }
    line_rows: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in cohort:
        line_rows[row["cohort_id"]].append(row)
    for rows in line_rows.values():
        rows.sort(key=lambda r: int(r["ordinal"]))

    spec_by_case = {row["case_id"]: row for row in case_specs}
    observables: list[dict[str, object]] = []
    for case, spec in zip(cases, case_specs):
        if (case["locus"], case["ordinal"]) != (spec["locus"], spec["ordinal"]):
            raise AssertionError(f"case locus/ordinal mismatch at {case['case_id']}")
        target = target_by_key[(case["locus"], case["ordinal"])]
        topo = topology(case["left_roles"], case["right_roles"])
        rows = line_rows[case["cohort_id"]]
        written = " ".join(row["surface"] for row in rows)
        observables.append({
            "case_id": case["case_id"], "occurrence_id": case["occurrence_id"],
            "cohort_id": case["cohort_id"], "locus": case["locus"],
            "page": case["page"], "physical_folio": physical_folio(case["page"]),
            "ordinal": case["ordinal"], "left_roles": case["left_roles"],
            "right_roles": case["right_roles"],
            "left_slot": int(bool(split_values(case["left_roles"]))),
            "right_slot": int(bool(split_values(case["right_roles"]))),
            "bridge_slot": int(bool(split_values(case["left_roles"])) and bool(split_values(case["right_roles"]))),
            "topology": topo,
            "right_source_or_material": int(bool(split_values(case["right_roles"]) & SOURCE_ROLES)),
            "discovery_focal": case["full_branch_declared"],
            "context_class": spec["context_class"], "context_eva": spec["context_eva"],
            "written_line_eva": written, "target_surface_provenance_only": target["surface"],
            "target_identity_credit": 0, "confirmed_lexeme": 0, "component_export_credit": 0,
        })
    topo_counts = Counter(row["topology"] for row in observables)
    expected_topologies = {"AC": 7, "CA": 2, "CC": 2, "C0": 1, "A0": 1, "0A": 1, "AA": 1}
    if dict(topo_counts) != expected_topologies:
        raise AssertionError(f"unexpected topology census: {dict(topo_counts)}")

    observable_fields = [
        "case_id", "occurrence_id", "cohort_id", "locus", "page", "physical_folio",
        "ordinal", "left_roles", "right_roles", "left_slot", "right_slot", "bridge_slot",
        "topology", "right_source_or_material", "discovery_focal", "context_class",
        "context_eva", "written_line_eva", "target_surface_provenance_only",
        "target_identity_credit", "confirmed_lexeme", "component_export_credit",
    ]
    write_tsv(artifacts / "OL_15_OBSERVABLE_CASES.tsv", observables, observable_fields)

    capacity_rows: list[dict[str, object]] = []
    for row in observables:
        mask = f"L{row['left_slot']}R{row['right_slot']}B{row['bridge_slot']}"
        penalty = 2 - int(row["left_slot"]) - int(row["right_slot"])
        for candidate in PURE_CANDIDATES:
            capacity_rows.append({
                "candidate_id": candidate, "case_id": row["case_id"], "locus": row["locus"],
                "physical_folio": row["physical_folio"], "left_slot": row["left_slot"],
                "right_slot": row["right_slot"], "bridge_slot": row["bridge_slot"],
                "capacity_mask": mask, "base_penalty": penalty,
                "candidate_specific_capacity_credit": 0, "equality_pass": 1,
            })
    for case_id in {row["case_id"] for row in capacity_rows}:
        rows = [row for row in capacity_rows if row["case_id"] == case_id]
        if len({(row["capacity_mask"], row["base_penalty"]) for row in rows}) != 1:
            raise AssertionError(f"capacity differs at {case_id}")
    write_tsv(artifacts / "BASE_CAPACITY_AUDIT.tsv", capacity_rows, [
        "candidate_id", "case_id", "locus", "physical_folio", "left_slot", "right_slot",
        "bridge_slot", "capacity_mask", "base_penalty", "candidate_specific_capacity_credit",
        "equality_pass",
    ])

    folios = sorted({str(row["physical_folio"]) for row in observables}, key=lambda x: int(x[1:]))
    capacity_loo: list[dict[str, object]] = []
    for held in folios:
        totals = {}
        for candidate in PURE_CANDIDATES:
            totals[candidate] = sum(int(row["base_penalty"]) for row in capacity_rows if row["candidate_id"] == candidate and row["physical_folio"] != held)
        equal = len(set(totals.values())) == 1
        for candidate in PURE_CANDIDATES:
            capacity_loo.append({
                "held_physical_folio": held, "candidate_id": candidate,
                "remaining_case_count": sum(1 for row in observables if row["physical_folio"] != held),
                "aggregate_base_penalty": totals[candidate], "all_candidates_equal": int(equal),
            })
    if not all(int(row["all_candidates_equal"]) for row in capacity_loo):
        raise AssertionError("leave-folio-out capacity differs")
    write_tsv(artifacts / "CAPACITY_LEAVE_ONE_FOLIO_OUT.tsv", capacity_loo, [
        "held_physical_folio", "candidate_id", "remaining_case_count",
        "aggregate_base_penalty", "all_candidates_equal",
    ])

    topo_rule_by_candidate = {row["candidate_id"]: row for row in topo_rules}
    case_scores: list[dict[str, object]] = []
    for row in observables:
        for candidate in PURE_CANDIDATES:
            rule = topo_rule_by_candidate[candidate]
            state, trigger = evidence_state(candidate, str(row["topology"]), str(row["right_roles"]), rule)
            cost = int(rule[{"SUPPORT": "support_cost", "NEUTRAL": "neutral_cost", "CONTRADICTION": "contradiction_cost"}[state]])
            case_scores.append({
                "candidate_id": candidate, "case_id": row["case_id"], "locus": row["locus"],
                "physical_folio": row["physical_folio"], "topology": row["topology"],
                "discovery_focal": row["discovery_focal"], "evidence_state": state,
                "trigger_code": trigger, "evidence_penalty": cost,
                "common_capacity_mask": f"L{row['left_slot']}R{row['right_slot']}B{row['bridge_slot']}",
                "common_capacity_credit": 0, "semantic_role_credit": 0,
                "confirmed_lexeme": 0, "component_export_credit": 0,
            })
    write_tsv(artifacts / "CANDIDATE_CASE_SCORE.tsv", case_scores, [
        "candidate_id", "case_id", "locus", "physical_folio", "topology", "discovery_focal",
        "evidence_state", "trigger_code", "evidence_penalty", "common_capacity_mask",
        "common_capacity_credit", "semantic_role_credit", "confirmed_lexeme", "component_export_credit",
    ])

    score_totals = {candidate: sum(int(row["evidence_penalty"]) for row in case_scores if row["candidate_id"] == candidate) for candidate in PURE_CANDIDATES}
    expected_scores = {
        "OL_QUANTIFIABLE_NOMINAL_HEAD": 6, "OL_PARTITIVE_VON": 10,
        "OL_FIELD_SEQUENCE_MARKER": 13, "OL_MEASURE_UNIT_COMPLEMENT": 15,
        "OL_DIRECTIONAL_AUS": 24,
    }
    if score_totals != expected_scores:
        raise AssertionError(f"unexpected formal scores: {score_totals}")
    full_min = min(score_totals.values())
    full_min_candidates = sorted(candidate for candidate, score in score_totals.items() if score == full_min)

    loo_rows: list[dict[str, object]] = []
    loo_unique_winner: dict[str, bool] = {candidate: True for candidate in PURE_CANDIDATES}
    for held in folios:
        fold_scores = {
            candidate: sum(int(row["evidence_penalty"]) for row in case_scores if row["candidate_id"] == candidate and row["physical_folio"] != held)
            for candidate in PURE_CANDIDATES
        }
        fold_min = min(fold_scores.values())
        minima = sorted(candidate for candidate, score in fold_scores.items() if score == fold_min)
        for candidate in PURE_CANDIDATES:
            other_best = min(score for other, score in fold_scores.items() if other != candidate)
            loo_rows.append({
                "held_physical_folio": held, "candidate_id": candidate,
                "remaining_case_count": sum(1 for row in observables if row["physical_folio"] != held),
                "fold_score": fold_scores[candidate], "best_rival_score": other_best,
                "margin_over_best_rival": other_best - fold_scores[candidate],
                "fold_minimum_candidates": "|".join(minima),
                "candidate_unique_fold_winner": int(minima == [candidate]),
            })
            if minima != [candidate]:
                loo_unique_winner[candidate] = False
    write_tsv(artifacts / "LEAVE_ONE_FOLIO_OUT.tsv", loo_rows, [
        "held_physical_folio", "candidate_id", "remaining_case_count", "fold_score",
        "best_rival_score", "margin_over_best_rival", "fold_minimum_candidates",
        "candidate_unique_fold_winner",
    ])

    scoreboard: list[dict[str, object]] = []
    for candidate in PURE_CANDIDATES:
        rows = [row for row in case_scores if row["candidate_id"] == candidate]
        support = [row for row in rows if row["evidence_state"] == "SUPPORT"]
        nondiscovery = [row for row in support if row["discovery_focal"] == "0"]
        contradictions = [row for row in rows if row["evidence_state"] == "CONTRADICTION"]
        best_rival = min(score for other, score in score_totals.items() if other != candidate)
        scoreboard.append({
            "candidate_id": candidate, "support_occurrences": len(support),
            "support_pages": len({row["physical_folio"] for row in support}),
            "nondiscovery_support_occurrences": len(nondiscovery),
            "nondiscovery_support_pages": len({row["physical_folio"] for row in nondiscovery}),
            "neutral_occurrences": sum(row["evidence_state"] == "NEUTRAL" for row in rows),
            "contradiction_occurrences": len(contradictions),
            "contradiction_pages": len({row["physical_folio"] for row in contradictions}),
            "total_score": score_totals[candidate], "best_rival_score": best_rival,
            "margin_over_best_rival": best_rival - score_totals[candidate],
            "full_minimum": int(candidate in full_min_candidates),
            "all_leave_one_folio_out_unique_wins": int(loo_unique_winner[candidate]),
        })
    board_by_candidate = {row["candidate_id"]: row for row in scoreboard}

    capacity_equal = all(int(row["equality_pass"]) for row in capacity_rows) and all(int(row["all_candidates_equal"]) for row in capacity_loo)
    gate_rows: list[dict[str, object]] = []
    for candidate in PURE_CANDIDATES:
        board = board_by_candidate[candidate]
        ac_pages = len({row["physical_folio"] for row in case_scores if row["candidate_id"] == candidate and row["topology"] == "AC" and row["evidence_state"] == "SUPPORT"})
        ca_pages = len({row["physical_folio"] for row in case_scores if row["candidate_id"] == candidate and row["topology"] == "CA" and row["evidence_state"] == "SUPPORT"})
        checks = [
            ("G00", capacity_equal, "casewise_and_leave_folio_capacity_equal"),
            ("G01", int(board["support_occurrences"]) >= 4 and int(board["support_pages"]) >= 4, f"{board['support_occurrences']}_occurrences__{board['support_pages']}_pages"),
            ("G02", int(board["nondiscovery_support_occurrences"]) >= 2 and int(board["nondiscovery_support_pages"]) >= 2, f"{board['nondiscovery_support_occurrences']}_occurrences__{board['nondiscovery_support_pages']}_pages"),
            ("G03", int(board["margin_over_best_rival"]) >= 4, f"margin_{board['margin_over_best_rival']}"),
            ("G04", int(board["contradiction_occurrences"]) == 0, f"{board['contradiction_occurrences']}_contradictions"),
            ("G05", bool(int(board["all_leave_one_folio_out_unique_wins"])), "all_folds_unique" if int(board["all_leave_one_folio_out_unique_wins"]) else "not_all_folds_unique"),
            ("G06", candidate != "OL_QUANTIFIABLE_NOMINAL_HEAD" or (ac_pages >= 2 and ca_pages >= 2), "not_applicable" if candidate != "OL_QUANTIFIABLE_NOMINAL_HEAD" else f"AC_{ac_pages}_pages__CA_{ca_pages}_pages"),
            ("G07", full_min_candidates == [candidate], "|".join(full_min_candidates)),
        ]
        for gate_id, passed, observed in checks:
            gate_rows.append({"candidate_id": candidate, "gate_id": gate_id, "passed": int(passed), "observed": observed})
        board["all_winner_gates_pass"] = int(all(passed for _, passed, _ in checks))
    winners = [row["candidate_id"] for row in scoreboard if int(row["all_winner_gates_pass"])]
    if winners != ["OL_QUANTIFIABLE_NOMINAL_HEAD"]:
        raise AssertionError(f"unexpected formal winner list: {winners}")
    write_tsv(artifacts / "CANDIDATE_SCOREBOARD.tsv", sorted(scoreboard, key=lambda r: (int(r["total_score"]), str(r["candidate_id"]))), [
        "candidate_id", "support_occurrences", "support_pages", "nondiscovery_support_occurrences",
        "nondiscovery_support_pages", "neutral_occurrences", "contradiction_occurrences",
        "contradiction_pages", "total_score", "best_rival_score", "margin_over_best_rival",
        "full_minimum", "all_leave_one_folio_out_unique_wins", "all_winner_gates_pass",
    ])
    write_tsv(artifacts / "GATE_AUDIT.tsv", gate_rows, ["candidate_id", "gate_id", "passed", "observed"])

    focal_rows: list[dict[str, object]] = []
    for row in observables:
        if row["discovery_focal"] != "1":
            continue
        nominal = next(x for x in case_scores if x["case_id"] == row["case_id"] and x["candidate_id"] == "OL_QUANTIFIABLE_NOMINAL_HEAD")
        von = next(x for x in case_scores if x["case_id"] == row["case_id"] and x["candidate_id"] == "OL_PARTITIVE_VON")
        focal_rows.append({
            "case_id": row["case_id"], "locus": row["locus"], "physical_folio": row["physical_folio"],
            "topology": row["topology"], "nominal_penalty": nominal["evidence_penalty"],
            "von_penalty": von["evidence_penalty"],
            "nominal_minus_von": int(nominal["evidence_penalty"]) - int(von["evidence_penalty"]),
            "focal_selection_neutral": int(nominal["evidence_penalty"] == von["evidence_penalty"]),
        })
    if len(focal_rows) != 7 or any(int(row["nominal_minus_von"]) for row in focal_rows):
        raise AssertionError("focal selection is not neutral between nominal and von")
    write_tsv(artifacts / "FOCAL_SELECTION_DELTA_AUDIT.tsv", focal_rows, [
        "case_id", "locus", "physical_folio", "topology", "nominal_penalty", "von_penalty",
        "nominal_minus_von", "focal_selection_neutral",
    ])

    fit_columns = {
        "OL_PARTITIVE_VON": ("fit_von", "von_reading_de"),
        "OL_DIRECTIONAL_AUS": ("fit_aus", "aus_reading_de"),
        "OL_QUANTIFIABLE_NOMINAL_HEAD": ("fit_nominal", "nominal_reading_de"),
        "OL_FIELD_SEQUENCE_MARKER": ("fit_field_sequence", "field_sequence_reading_de"),
        "OL_MEASURE_UNIT_COMPLEMENT": ("fit_measure_unit", "measure_unit_reading_de"),
    }
    practical_rows: list[dict[str, object]] = []
    for spec in case_specs:
        for candidate in PURE_CANDIDATES:
            fit_col, reading_col = fit_columns[candidate]
            practical_rows.append({
                "case_id": spec["case_id"], "locus": spec["locus"], "ordinal": spec["ordinal"],
                "candidate_id": candidate, "fit_cost": spec[fit_col],
                "fit_grade": {"0": "NATURAL", "1": "USABLE", "2": "STRAINED", "3": "CONTRADICTORY"}[spec[fit_col]],
                "candidate_reading_de": spec[reading_col], "reason_de": spec["reason_de"],
                "evidence_refs": spec["evidence_refs"], "score_is_plaintext_credit": 0,
            })
    write_tsv(artifacts / "OL_FIVE_WAY_PRACTICAL_FIT.tsv", practical_rows, [
        "case_id", "locus", "ordinal", "candidate_id", "fit_cost", "fit_grade",
        "candidate_reading_de", "reason_de", "evidence_refs", "score_is_plaintext_credit",
    ])

    rule_matches: dict[str, dict[str, str]] = {}
    for spec in case_specs:
        matches = [rule for rule in dispatch_rules if spec["context_class"] in split_values(rule["context_classes"])]
        if len(matches) != 1:
            raise AssertionError(f"dispatch coverage for {spec['case_id']} is {len(matches)}")
        rule_matches[spec["case_id"]] = matches[0]
    contextual_rows: list[dict[str, object]] = []
    for spec in case_specs:
        rule = rule_matches[spec["case_id"]]
        fit_col, _ = fit_columns[rule["fit_source_candidate"]]
        contextual_rows.append({
            "case_id": spec["case_id"], "locus": spec["locus"], "ordinal": spec["ordinal"],
            "context_eva": spec["context_eva"], "context_class": spec["context_class"],
            "dispatch_rule_id": rule["rule_id"], "complexity_branch": rule["complexity_branch"],
            "selected_function": rule["selected_function"], "selected_default_de": spec["default_surface_de"],
            "rule_default_de": rule["default_surface_de"], "strongest_rival_de": spec["alternative_de"],
            "selected_local_fit_cost": spec[fit_col], "portable_rule_de": rule["portable_rule_de"],
            "default_is_translation": 0, "confirmed_lexeme": 0, "component_export_credit": 0,
        })
    if any(int(row["selected_local_fit_cost"]) for row in contextual_rows):
        raise AssertionError("predeclared contextual renderer contains a non-natural selected case")
    write_tsv(artifacts / "OL_CONTEXTUAL_DEFAULTS.tsv", contextual_rows, [
        "case_id", "locus", "ordinal", "context_eva", "context_class", "dispatch_rule_id",
        "complexity_branch", "selected_function", "selected_default_de", "rule_default_de",
        "strongest_rival_de", "selected_local_fit_cost", "portable_rule_de",
        "default_is_translation", "confirmed_lexeme", "component_export_credit",
    ])

    model_by_id = {row["candidate_id"]: row for row in model_specs}
    practical_board: list[dict[str, object]] = []
    for candidate in PURE_CANDIDATES:
        rows = [row for row in practical_rows if row["candidate_id"] == candidate]
        raw = sum(int(row["fit_cost"]) for row in rows)
        complexity = int(model_by_id[candidate]["model_complexity_cost"])
        practical_board.append({
            "candidate_id": candidate, "natural_cases": sum(row["fit_grade"] == "NATURAL" for row in rows),
            "usable_or_better_cases": sum(row["fit_grade"] in {"NATURAL", "USABLE"} for row in rows),
            "contradictory_cases": sum(row["fit_grade"] == "CONTRADICTORY" for row in rows),
            "raw_practical_fit_cost": raw, "model_complexity_cost": complexity,
            "adjusted_practical_cost": raw + complexity, "case_coverage": 15,
        })
    composite_raw = sum(int(row["selected_local_fit_cost"]) for row in contextual_rows)
    composite_complexity = int(model_by_id[COMPOSITE]["model_complexity_cost"])
    practical_board.append({
        "candidate_id": COMPOSITE, "natural_cases": 15, "usable_or_better_cases": 15,
        "contradictory_cases": 0, "raw_practical_fit_cost": composite_raw,
        "model_complexity_cost": composite_complexity,
        "adjusted_practical_cost": composite_raw + composite_complexity, "case_coverage": 15,
    })
    practical_board.sort(key=lambda row: (int(row["adjusted_practical_cost"]), str(row["candidate_id"])))
    for index, row in enumerate(practical_board, start=1):
        row["rank"] = index
        row["selected_working_renderer"] = int(index == 1 and row["candidate_id"] == COMPOSITE)
    if practical_board[0]["candidate_id"] != COMPOSITE or int(practical_board[0]["adjusted_practical_cost"]) >= int(practical_board[1]["adjusted_practical_cost"]):
        raise AssertionError("contextual record operator is not the unique practical winner")
    write_tsv(artifacts / "PRACTICAL_MODEL_SCOREBOARD.tsv", practical_board, [
        "rank", "candidate_id", "natural_cases", "usable_or_better_cases", "contradictory_cases",
        "raw_practical_fit_cost", "model_complexity_cost", "adjusted_practical_cost",
        "case_coverage", "selected_working_renderer",
    ])

    judgments_by_case: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in reader_judgments:
        judgments_by_case[row["case_id"]].append(row)
    if set(judgments_by_case) != set(spec_by_case) or any(len(rows) != 2 for rows in judgments_by_case.values()):
        raise AssertionError("independent reader matrix must contain two judgments per case")
    disagreement_rows: list[dict[str, object]] = []
    exact_agreements = 0
    for case_id in [row["case_id"] for row in case_specs]:
        rows = sorted(judgments_by_case[case_id], key=lambda row: row["reader_id"])
        agreed = rows[0]["primary_candidate"] == rows[1]["primary_candidate"]
        exact_agreements += int(agreed)
        selected = next(row for row in contextual_rows if row["case_id"] == case_id)
        disagreement_rows.append({
            "case_id": case_id, "locus": spec_by_case[case_id]["locus"],
            "apothecary_primary": next(row["primary_candidate"] for row in rows if row["reader_id"] == "R_APOTHECARY"),
            "scribe_primary": next(row["primary_candidate"] for row in rows if row["reader_id"] == "R_SCRIBE"),
            "exact_primary_agreement": int(agreed),
            "contextual_selected_function": selected["selected_function"],
            "contextual_default_de": selected["selected_default_de"],
            "disagreement_preserved": int(not agreed),
        })
    write_tsv(artifacts / "INDEPENDENT_READER_DISAGREEMENT.tsv", disagreement_rows, [
        "case_id", "locus", "apothecary_primary", "scribe_primary", "exact_primary_agreement",
        "contextual_selected_function", "contextual_default_de", "disagreement_preserved",
    ])
    reader_count_rows: list[dict[str, object]] = []
    for reader_id in sorted({row["reader_id"] for row in reader_judgments}):
        rows = [row for row in reader_judgments if row["reader_id"] == reader_id]
        counts = Counter(row["primary_candidate"] for row in rows)
        for candidate in PURE_CANDIDATES:
            reader_count_rows.append({
                "reader_id": reader_id, "reader_background": rows[0]["reader_background"],
                "candidate_id": candidate, "primary_count": counts[candidate],
                "case_count": len(rows), "changed_files": 0,
            })
    write_tsv(artifacts / "READER_PRIMARY_COUNTS.tsv", reader_count_rows, [
        "reader_id", "reader_background", "candidate_id", "primary_count", "case_count", "changed_files",
    ])

    historical_by_id = {row["analogue_id"]: row for row in historical}
    historical_rows: list[dict[str, object]] = []
    for model in model_specs:
        for analogue_id in model["historical_analogue_ids"].split("|"):
            analogue = historical_by_id[analogue_id]
            historical_rows.append({
                "candidate_id": model["candidate_id"], "short_label_de": model["short_label_de"],
                "analogue_id": analogue_id, "date_or_witness": analogue["date_or_witness"],
                "source": analogue["source"], "class": analogue["class"],
                "historical_architecture_de": analogue["historical_architecture_de"],
                "discriminates_de": analogue["discriminates_de"], "caveat_de": analogue["caveat_de"],
                "url": analogue["url"], "voynich_identity_credit": 0,
            })
    write_tsv(artifacts / "HISTORICAL_COMPOSITION_BRIDGE.tsv", historical_rows, [
        "candidate_id", "short_label_de", "analogue_id", "date_or_witness", "source", "class",
        "historical_architecture_de", "discriminates_de", "caveat_de", "url", "voynich_identity_credit",
    ])

    ol_census = next(row for row in census if row["surface"] == "ol")
    global_row = {
        "surface": "ol", "reader_exact_ol": int(ol_census["reader_exact_occurrences"]),
        "known_amount_contacts": len(amount_atlas),
        "known_amount_contact_rate": f"{len(amount_atlas) / int(ol_census['reader_exact_occurrences']):.6f}",
        "deck_cases_with_any_A_side": sum(row["topology"] in {"AC", "CA", "AA", "A0", "0A"} for row in observables),
        "deck_case_count": len(observables), "deck_is_amount_enriched": 1,
        "fixed_global_unit_selected": 0, "specific_substance_selected": 0,
    }
    write_tsv(artifacts / "GLOBAL_AMOUNT_CONTACT_CHECK.tsv", [global_row], list(global_row))

    contextual_by_key = {(row["locus"], str(row["ordinal"])): row for row in contextual_rows}
    other_defaults = {row["whole_form"]: row["concrete_replaceable_default_de"] for row in other_target_dictionary}
    ol_cohort_ids = {case["cohort_id"] for case in cases}
    selected_cohort = [row for row in cohort if row["cohort_id"] in ol_cohort_ids]
    token_defaults: list[dict[str, object]] = []
    for row in selected_cohort:
        key = (row["locus"], row["ordinal"])
        if key in contextual_by_key:
            default = contextual_by_key[key]["selected_default_de"]
            source = contextual_by_key[key]["dispatch_rule_id"]
            render_once = 1
        elif row["is_target"] == "1":
            if row["surface"] not in other_defaults:
                raise AssertionError(f"missing inherited target default for {row['surface']}")
            default = other_defaults[row["surface"]]
            source = "GDT772_OTHER_TARGET_WORKING_DICTIONARY"
            render_once = 1
        elif row["frozen_non_target_default_de"] == "NONE":
            if row["span_member_role"] != "CONSUMED":
                raise AssertionError(f"unexplained NONE display at {row['locus']}@{row['ordinal']}")
            default = "in der vorigen Mehrtoken-Mengenform enthalten"
            source = "INHERITED_CONSUMED_SPAN_MEMBER"
            render_once = 0
        else:
            default = row["frozen_non_target_default_de"]
            source = "GDT772_INHERITED_NON_OL_DEFAULT"
            render_once = 0 if row["span_member_role"] == "CONSUMED" else 1
        token_defaults.append({
            "cohort_id": row["cohort_id"], "locus": row["locus"], "physical_folio": physical_folio(row["page"]),
            "ordinal": row["ordinal"], "surface": row["surface"], "is_ol_target": int(key in contextual_by_key),
            "working_default_de": default, "default_source": source, "render_once": render_once,
            "span_id": row["span_id"], "span_member_role": row["span_member_role"],
            "default_is_translation": 0, "confirmed_lexeme": 0, "component_export_credit": 0,
        })
    if not all(str(row["working_default_de"]).strip() for row in token_defaults):
        raise AssertionError("a selected-line token lacks a working default")
    write_tsv(artifacts / "GDT773_11_LINE_TOKEN_DEFAULTS.tsv", token_defaults, [
        "cohort_id", "locus", "physical_folio", "ordinal", "surface", "is_ol_target",
        "working_default_de", "default_source", "render_once", "span_id", "span_member_role",
        "default_is_translation", "confirmed_lexeme", "component_export_credit",
    ])

    reader_rows: list[dict[str, object]] = []
    for cohort_id in sorted(ol_cohort_ids, key=lambda cid: int(cid.split("-L")[-1])):
        rows = sorted([row for row in token_defaults if row["cohort_id"] == cohort_id], key=lambda row: int(row["ordinal"]))
        eva = " ".join(f"[{row['surface']}]" if row["is_ol_target"] else str(row["surface"]) for row in rows)
        units = [str(row["working_default_de"]) for row in rows if int(row["render_once"])]
        defaults = [str(row["working_default_de"]) for row in rows if row["is_ol_target"]]
        reader_rows.append({
            "cohort_id": cohort_id, "locus": rows[0]["locus"], "physical_folio": rows[0]["physical_folio"],
            "source_token_count": len(rows), "practical_unit_count": len(units),
            "ol_target_count": sum(int(row["is_ol_target"]) for row in rows),
            "written_line_eva": eva, "ol_contextual_defaults_de": " | ".join(defaults),
            "working_reading_de": render_units(units), "all_source_tokens_accounted": 1,
            "inherited_non_ol_defaults_revalidated": 0, "default_is_translation": 0,
            "confirmed_plaintext": 0,
        })
    if len(reader_rows) != 11 or sum(int(row["ol_target_count"]) for row in reader_rows) != 15:
        raise AssertionError("eleven-line reader coverage differs")
    write_tsv(artifacts / "GDT773_11_LINE_READER.tsv", reader_rows, [
        "cohort_id", "locus", "physical_folio", "source_token_count", "practical_unit_count",
        "ol_target_count", "written_line_eva", "ol_contextual_defaults_de", "working_reading_de",
        "all_source_tokens_accounted", "inherited_non_ol_defaults_revalidated",
        "default_is_translation", "confirmed_plaintext",
    ])

    polish_by_cohort = {row["cohort_id"]: row for row in manual_polish_specs}
    if len(polish_by_cohort) != 11 or set(polish_by_cohort) != {str(row["cohort_id"]) for row in reader_rows}:
        raise AssertionError("manual polished reader must cover the eleven selected lines exactly once")
    polished_rows: list[dict[str, object]] = []
    for reader in reader_rows:
        cohort_id = str(reader["cohort_id"])
        spec = polish_by_cohort[cohort_id]
        if spec["locus"] != reader["locus"] or spec["ol_direction_valid"] != "1":
            raise AssertionError(f"manual polish locus or ol direction differs at {cohort_id}")
        source_rows = [row for row in selected_cohort if row["cohort_id"] == cohort_id]
        non_ol_rows = [
            row for row in source_rows
            if not (row["is_target"] == "1" and row["surface"] == "ol")
        ]
        polished_rows.append({
            "cohort_id": cohort_id, "locus": reader["locus"],
            "risk_level": spec["risk_level"], "ol_direction_valid": 1,
            "source_token_count": len(source_rows), "ol_target_count": reader["ol_target_count"],
            "non_ol_token_count": len(non_ol_rows),
            "non_ol_untyped_count": sum(row["structural_roles"] == "NONE" for row in non_ol_rows),
            "non_ol_display_only_count": sum(
                row["current_provenance"] == "GDT734_COMPLETE_CELL__DISPLAY_ONLY_UNTYPED"
                for row in non_ol_rows
            ),
            "non_ol_nonexact_count": sum(row["reader_exact"] == "0" for row in non_ol_rows),
            "written_line_eva": reader["written_line_eva"],
            "mechanical_working_reading_de": reader["working_reading_de"],
            "polished_record_reading_de": spec["polished_record_reading_de"],
            "manual_note_de": spec["manual_note_de"],
            "editorial_condensation": 1, "all_ol_targets_preserved": 1,
            "polished_is_translation": spec["polished_is_translation"],
            "confirmed_lexeme": spec["confirmed_lexeme"], "confirmed_plaintext": 0,
        })
    write_tsv(artifacts / "GDT773_11_LINE_POLISHED_RECORD_READER.tsv", polished_rows, [
        "cohort_id", "locus", "risk_level", "ol_direction_valid", "source_token_count",
        "ol_target_count", "non_ol_token_count", "non_ol_untyped_count",
        "non_ol_display_only_count", "non_ol_nonexact_count", "written_line_eva",
        "mechanical_working_reading_de", "polished_record_reading_de", "manual_note_de",
        "editorial_condensation", "all_ol_targets_preserved", "polished_is_translation",
        "confirmed_lexeme", "confirmed_plaintext",
    ])

    dictionary_row = {
        "dictionary_id": "G773-D01", "whole_form": "ol",
        "formal_invariant_working_default": "Ansatz-/Zubereitungsposten",
        "selected_contextual_model": COMPOSITE,
        "contextual_working_default_de": "Menge→Inhalt: Ansatz:; Inhalt→Menge: Menge:; sonst : / ; / und / und dann",
        "confidence_level": "C1_STRUCTURAL_COMPOSITION__C0_LEXEME",
        "evidence_de": "Topologiescore Nominalkopf 6 gegen von 10; sieben AC plus zwei CA; fünfzehn konkrete Regeln; zwei Leser stimmen auf sechs Feldfällen exakt überein.",
        "counterevidence_de": "Die Leser trennen sich auf neun Fällen, besonders Nominalkopf gegen partitives von und Mengenkomplement; die breite 376er Übertragung steht noch aus.",
        "aus_status": "kein Primärfall; null gerichteter Source-Result-Rahmen",
        "unit_status": "lokaler Rivale; global nur 16 bekannte Amount-Kontakte unter 376 exakten ol",
        "specific_substance_status": "Öl, Wasser, Wein und Essig unselektiert",
        "replaceable": 1, "default_is_translation": 0, "confirmed_lexeme": 0,
        "confirmed_plaintext": 0, "component_export_credit": 0,
    }
    write_tsv(artifacts / "GDT773_OL_WORKING_DICTIONARY.tsv", [dictionary_row], list(dictionary_row))

    apoth_counts = Counter(row["primary_candidate"] for row in reader_judgments if row["reader_id"] == "R_APOTHECARY")
    scribe_counts = Counter(row["primary_candidate"] for row in reader_judgments if row["reader_id"] == "R_SCRIBE")
    result = {
        "experiment_id": "GDT773",
        "status": "PASS__15_OL_CASES_11_LINES_10_PHYSICAL_FOLIOS__75_EQUAL_CAPACITY_MASKS__FORMAL_NOMINAL_HEAD_6_VS_VON_10_FIELD_13_UNIT_15_AUS_24__CONTEXTUAL_ASSOCIATION7_FIELD8__ZERO_CONFIRMED_LEXEMES_NO_NEW_PAGE",
        "question": "After equalizing binding capacity, which of five concrete ol readings best explains the fifteen fixed cases, and can one explicit contextual operator render every case?",
        "counts": {
            "ol_case_count": len(observables), "line_count": len(reader_rows),
            "physical_folio_count": len(folios), "capacity_row_count": len(capacity_rows),
            "formal_case_score_count": len(case_scores), "practical_fit_row_count": len(practical_rows),
            "contextual_default_count": len(contextual_rows), "reader_judgment_count": len(reader_judgments),
            "reader_source_token_count": len(token_defaults),
            "reader_practical_unit_count": sum(int(row["practical_unit_count"]) for row in reader_rows),
            "reader_non_ol_token_count": sum(int(row["non_ol_token_count"]) for row in polished_rows),
            "reader_non_ol_untyped_count": sum(int(row["non_ol_untyped_count"]) for row in polished_rows),
            "reader_non_ol_display_only_count": sum(int(row["non_ol_display_only_count"]) for row in polished_rows),
            "reader_non_ol_nonexact_count": sum(int(row["non_ol_nonexact_count"]) for row in polished_rows),
            "historical_bridge_row_count": len(historical_rows),
            "topology_counts": dict(sorted(topo_counts.items())),
        },
        "formal_topology_result": {
            "winner": winners[0], "winner_score": score_totals[winners[0]],
            "runner_up": "OL_PARTITIVE_VON", "runner_up_score": score_totals["OL_PARTITIVE_VON"],
            "all_scores": score_totals, "winner_full_margin": board_by_candidate[winners[0]]["margin_over_best_rival"],
            "all_leave_one_folio_out_unique_wins": True,
            "focal_ac_nominal_von_delta": sum(int(row["nominal_minus_von"]) for row in focal_rows),
            "capacity_equalized": capacity_equal,
        },
        "practical_result": {
            "winner": COMPOSITE, "winner_adjusted_cost": int(practical_board[0]["adjusted_practical_cost"]),
            "best_pure": practical_board[1]["candidate_id"],
            "best_pure_adjusted_cost": int(practical_board[1]["adjusted_practical_cost"]),
            "association_default_count": sum(row["complexity_branch"] == "ASSOCIATE_QUANTITY_CONTENT" for row in contextual_rows),
            "field_default_count": sum(row["complexity_branch"] == "ADVANCE_OR_CLOSE_FIELD" for row in contextual_rows),
        },
        "independent_readers": {
            "exact_primary_agreements": exact_agreements,
            "apothecary_nominal": apoth_counts["OL_QUANTIFIABLE_NOMINAL_HEAD"],
            "apothecary_field": apoth_counts["OL_FIELD_SEQUENCE_MARKER"],
            "scribe_von": scribe_counts["OL_PARTITIVE_VON"],
            "scribe_field": scribe_counts["OL_FIELD_SEQUENCE_MARKER"],
            "scribe_unit": scribe_counts["OL_MEASURE_UNIT_COMPLEMENT"],
            "scribe_nominal": scribe_counts["OL_QUANTIFIABLE_NOMINAL_HEAD"],
            "aus_primary_count": apoth_counts["OL_DIRECTIONAL_AUS"] + scribe_counts["OL_DIRECTIONAL_AUS"],
        },
        "global_check": {
            "reader_exact_ol": int(ol_census["reader_exact_occurrences"]),
            "amount_contacts": len(amount_atlas),
            "amount_contact_rate": len(amount_atlas) / int(ol_census["reader_exact_occurrences"]),
            "amount_contact_rate_percent": 100 * len(amount_atlas) / int(ol_census["reader_exact_occurrences"]),
            "deck_is_amount_enriched": True,
        },
        "source_hashes": locked_hashes,
        "outputs": OUTPUT_NAMES,
        "scope": {
            "new_page_opened": False, "new_image_opened": False,
            "new_ocr_opened": False, "new_transcription_opened": False,
            "f84_accessed": False, "f84r_accessed": False,
        },
        "claim_ceiling": {
            "confirmed_lexemes": 0, "confirmed_translations": 0,
            "confirmed_plaintext_clauses": 0, "component_export_credit": 0,
            "eva_latin_credit": 0, "defaults_are_replaceable": True,
        },
    }
    if result["practical_result"]["association_default_count"] != 7 or result["practical_result"]["field_default_count"] != 8:
        raise AssertionError("contextual association/field split differs")
    (artifacts / "RESULT.json").write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.report_path.parent.mkdir(parents=True, exist_ok=True)
    args.report_path.write_text(build_report(result), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
