#!/usr/bin/env python3
"""Cross the 29 productive families with seven Biological operating modes."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
FAMILIES = ROOT / "experiments/yolo/sidequest_semantic_root_pruning_two_hundred_ninety_seventh/TWO_HUNDRED_NINETY_SEVENTH_29_PRODUCTIVE_FAMILIES.tsv"
RAW = ROOT / "experiments/yolo/sidequest_semantic_two_layer_prose_two_hundred_seventy_ninth/TWO_HUNDRED_SEVENTY_NINTH_381_TWO_LAYER_EVENTS.tsv"
BIO = ROOT / "experiments/yolo/sidequest_semantic_bio_operating_modes_three_hundred_eighth/THREE_HUNDRED_EIGHTH_281_EVENT_OPERATING_MODES.tsv"
MODES = ["CHARGE", "TREAT", "SETTLE", "PASS_FILTER", "DISCHARGE", "MEASURE", "LOCAL_CONTROL"]


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def family_tokens(parse: str) -> set[str]:
    return {token for token in re.split(r"[^A-Z0-9_]+", parse.upper()) if token}


def interpretation(family: str, events: int, share: float) -> tuple[str, str]:
    if events == 0:
        return "NO_BIO_COVERAGE", "Auf diesen drei Bio-Seiten nicht sichtbar; Wert bleibt aus Herbal/gesamtprosa erhalten."
    if family == "CHED_TRANSFER":
        return "DIRECTIONALLY_CONDITIONED_TRANSFER_CORE", "Der Kern trägt Übergabe; L/P/AR/AL und Ganzkarte entscheiden Beschicken gegen Abführen."
    if family == "OK":
        return "MULTIMODE_OPERATION_ACTIVATOR", "OK setzt einen Arbeitsgang in Kraft, bestimmt aber nicht allein Behandlung oder Beschickung."
    if family in {"E_GRADE", "Y", "DY"}:
        return "GRADE_REFERENT_ENDPOINT_FRAME", "Grad, laufender Posten oder lizenzierter Schluss rahmen mehrere Betriebsarten."
    if family in {"OL", "OT", "AR", "AL", "AIR", "CTH", "SOLK"}:
        return "LOCAL_CONTROL_ADDRESS_OR_STATE_FAMILY", "Trägt Folge, Adresse, Lauf, Bereitschaft oder Sammelstelle statt einer einzigen Handlung."
    if events < 3:
        return "NARROW_LOW_COUNT_SPECIALIST", "Operativ konkret, aber auf den Bio-Seiten nur ein- oder zweimal belegt."
    if share >= 0.75:
        return "MODE_PREDICTIVE_CONTENT_FAMILY", "Sagt überwiegend dieselbe Betriebsart voraus und darf als Inhalts-/Operationsstamm gelehrt werden."
    return "MULTIMODE_CONTENT_OR_FRAME", "Verteilt sich zu breit; nur mit Partnern oder als Ganzkarte konkret lesen."


def main() -> None:
    families = read(FAMILIES)
    family_ids = {r["family_id"] for r in families}
    raw = {r["event_id"]: r for r in read(RAW)}
    bio = read(BIO)
    membership_rows = []
    counts: dict[str, Counter[str]] = {family: Counter() for family in family_ids}
    cards: dict[str, set[str]] = {family: set() for family in family_ids}
    layer_counts: Counter[tuple[str, str]] = Counter()
    layer_cards: dict[str, set[str]] = defaultdict(set)
    for event in bio:
        tokens = family_tokens(raw[event["event_id"]]["family_parse"])
        memberships = sorted(tokens & family_ids)
        layer = "PRODUCTIVE_COMPOSITION" if memberships else "LEARNED_WHOLE_OR_MICROSIGN"
        layer_counts[(layer, event["operating_mode"])] += 1
        layer_cards[layer].add(event["master_card_id"])
        for family in memberships:
            counts[family][event["operating_mode"]] += 1
            cards[family].add(event["master_card_id"])
        membership_rows.append({
            "event_id": event["event_id"], "record_unit_id": event["record_unit_id"], "statement_id": event["statement_id"],
            "visible_surface": event["visible_surface"], "master_card_id": event["master_card_id"],
            "family_parse": raw[event["event_id"]]["family_parse"],
            "productive_family_memberships": "|".join(memberships) if memberships else "NONE",
            "teaching_layer": layer, "operating_mode": event["operating_mode"],
            "imperative_clause_de": event["imperative_clause_de"],
        })
    membership_path = HERE / "THREE_HUNDRED_NINTH_281_EVENT_STEM_MODE_MEMBERSHIPS.tsv"
    write(membership_path, membership_rows)

    matrix_rows = []
    for family in families:
        family_id = family["family_id"]
        counter = counts[family_id]
        total = sum(counter.values())
        dominant, dominant_count = counter.most_common(1)[0] if total else ("NONE", 0)
        share = dominant_count / total if total else 0.0
        category, rule = interpretation(family_id, total, share)
        matrix_rows.append({
            "family_order": family["new_family_order"], "family_id": family_id,
            "visible_core_or_variants": family["visible_core_or_variants"], "short_value_de": family["short_value_de"],
            "family_tier": family["new_tier"], "bio_card_types": len(cards[family_id]), "bio_event_memberships": total,
            **{f"mode_{mode.lower()}": counter[mode] for mode in MODES},
            "dominant_mode": dominant, "dominant_mode_share": f"{share:.3f}",
            "operational_interpretation": category, "teaching_rule_de": rule,
        })
    matrix_path = HERE / "THREE_HUNDRED_NINTH_29_FAMILY_MODE_MATRIX.tsv"
    write(matrix_path, matrix_rows)

    layer_rows = []
    for layer in ["PRODUCTIVE_COMPOSITION", "LEARNED_WHOLE_OR_MICROSIGN"]:
        layer_rows.append({
            "teaching_layer": layer, "distinct_card_types": len(layer_cards[layer]),
            "event_count": sum(layer_counts[(layer, mode)] for mode in MODES),
            **{f"mode_{mode.lower()}": layer_counts[(layer, mode)] for mode in MODES},
            "reading_rule_de": "Komponenten nach Stamm- und Slotregel zusammensetzen" if layer == "PRODUCTIVE_COMPOSITION" else "Ganzkarte als kurze gelernte Ausnahme lesen",
        })
    layer_path = HERE / "THREE_HUNDRED_NINTH_LAYER_MODE_CROSSWALK.tsv"
    write(layer_path, layer_rows)

    predictive = [r for r in matrix_rows if r["operational_interpretation"] == "MODE_PREDICTIVE_CONTENT_FAMILY"]
    lines = ["# Betriebsarten-Lernblatt der 29 Stammfamilien", "", "Ein Stamm wird nur dann als Betriebsinhalt gesprochen, wenn er auf den Bio-Seiten überwiegend denselben Modus trägt. Rahmen- und Adressstämme bleiben funktionsoffen und erhalten ihren konkreten Satzwert erst mit Partnerkarten.", ""]
    for row in matrix_rows:
        lines += [
            f"## {row['family_id']} — {row['short_value_de']}", "",
            f"**Bio:** {row['bio_event_memberships']} Ereignisse; Hauptmodus {row['dominant_mode']} ({float(row['dominant_mode_share']):.0%}).", "",
            f"**Lehrstatus:** {row['operational_interpretation']}.", "",
            f"**Regel:** {row['teaching_rule_de']}", "",
        ]
    manual_path = HERE / "THREE_HUNDRED_NINTH_STEM_OPERATING_MANUAL.md"
    manual_path.write_text("\n".join(lines), encoding="utf-8")

    report_path = HERE / "THREE_HUNDRED_NINTH_REPORT.md"
    report_path.write_text(
        "# Sidequest-Pass 309: welche Stämme sagen eine Betriebsart voraus?\n\n"
        f"Von den 29 produktiven Familien sind {len(predictive)} auf den Bio-Seiten echte Modusträger: " + ", ".join(f"{r['family_id']}→{r['dominant_mode']}" for r in predictive) + ". P und O_WITHDRAW sind zusätzlich perfekte, aber nur zweimal belegte Spezialisten. CHED_TRANSFER ist richtungsbedingt: 31 Beschickungs-, zwölf Abführ- und drei Steuerereignisse. OK ist dagegen der erwartete Aktivator und verteilt sich vor allem auf Behandlung (27) und Beschickung (25). E_GRADE, Y und DY rahmen mehrere Modi und sind keine Inhaltsverben.\n\n"
        "Die Kompositionshypothese trägt erstaunlich viel Last: 264 der 281 Bio-Ereignisse und 111 von 124 sichtbaren Kartentypen enthalten mindestens eine der 29 Familien; nur 17 Ereignisse auf 13 Kartentypen bleiben gelernte Ganz-/Mikrozeichen.\n\n"
        "Als nächstes kann aus den zehn Modusträgern plus den richtungs- und rahmengebundenen Familien ein minimales Bio-Wörterbuch gebaut werden, das jede Karte kompositionell oder als explizite Ganzwortausnahme erklärt.\n",
        encoding="utf-8",
    )
    category_counts = Counter(r["operational_interpretation"] for r in matrix_rows)
    summary = {
        "status": "PASS", "families": len(matrix_rows), "bio_events": len(membership_rows),
        "predictive_content_families": len(predictive), "category_counts": dict(category_counts),
        "composed_event_count": sum(layer_counts[("PRODUCTIVE_COMPOSITION", mode)] for mode in MODES),
        "whole_event_count": sum(layer_counts[("LEARNED_WHOLE_OR_MICROSIGN", mode)] for mode in MODES),
        "composed_card_types": len(layer_cards["PRODUCTIVE_COMPOSITION"]), "whole_card_types": len(layer_cards["LEARNED_WHOLE_OR_MICROSIGN"]),
        "source_hashes": {str(p.relative_to(ROOT)): sha(p) for p in [FAMILIES, RAW, BIO]},
        "output_hashes": {p.name: sha(p) for p in [membership_path, matrix_path, layer_path, manual_path, report_path]},
    }
    (HERE / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
