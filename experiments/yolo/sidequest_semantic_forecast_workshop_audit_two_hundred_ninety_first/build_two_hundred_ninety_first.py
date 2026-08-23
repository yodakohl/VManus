#!/usr/bin/env python3
"""Build the creative workshop audit of the twelve Pass-286 forecasts."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P286 = ROOT / "experiments/yolo/sidequest_semantic_apprentice_reverse_codebook_two_hundred_eighty_sixth/TWO_HUNDRED_EIGHTY_SIXTH_12_NEW_COMPOSITION_FORECASTS.tsv"
CARDS = ROOT / "experiments/yolo/sidequest_semantic_two_layer_prose_two_hundred_seventy_ninth/TWO_HUNDRED_SEVENTY_NINTH_173_TWO_LAYER_DICTIONARY.tsv"
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_two_layer_prose_two_hundred_seventy_ninth/TWO_HUNDRED_SEVENTY_NINTH_381_TWO_LAYER_EVENTS.tsv"
ASTRO = ROOT / "experiments/yolo/sidequest_semantic_astro_reverse_encoder_two_hundred_eighty_ninth/TWO_HUNDRED_EIGHTY_NINTH_265_REVERSE_ENCODINGS.tsv"
LEDGER = ROOT / "experiments/yolo/sidequest_semantic_complete_forward_writer_two_hundred_ninetieth/TWO_HUNDRED_NINETIETH_776_FORWARD_WRITING_LEDGER.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def tokens(recipe: str) -> list[str]:
    base = recipe.replace("WHOLE_SIGN[", "").replace("]", "")
    return [part.split("[")[0] for part in base.split("+") if part]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


DECISIONS = {
    1: {
        "decision": "REWRITE_AS_TWO_CARD_WORKSTEP",
        "revised": "qokaiin · qokedy",
        "reading": "Sollmaß einsetzen; anschließend den kurzen Arbeitsgang festsetzen",
        "confidence": "MEDIUM",
        "reason": "OK+AIIN exists nine times, but DY closes an operation rather than a bare value. B3-S007 already places qokaiin before a terminal work card.",
        "anchors": "E243,E245",
    },
    2: {
        "decision": "ALREADY_REALIZED_AS_TWO_CARDS",
        "revised": "okain · qokeedy",
        "reading": "eine Portion einsetzen und den längeren Arbeitsgang festsetzen",
        "confidence": "HIGH",
        "reason": "B2-S011 already contains the exact two-card workshop solution; fusion would remove a useful operation boundary.",
        "anchors": "E200,E201",
    },
    3: {
        "decision": "KEEP_AS_NEW_COMPOUND",
        "revised": "otain",
        "reading": "zum nächsten Portionsposten wechseln",
        "confidence": "MEDIUM",
        "reason": "OT+AIIN and OL+AIN are visible neighbors in the paradigm, but OT+AIN is still the missing square.",
        "anchors": "E312,E358",
    },
    4: {
        "decision": "ALREADY_REALIZED_AS_TWO_CARDS",
        "revised": "ol · daiin",
        "reading": "mit dem vorgeschriebenen Maß weiter",
        "confidence": "HIGH",
        "reason": "The exact meaning is written as adjacent continuation and measure cards in B6-S001; H2-S002 gives the same construction with a renderer variant.",
        "anchors": "E376,E377,E029,E030",
    },
    5: {
        "decision": "ALREADY_REALIZED_AS_TWO_CARDS",
        "revised": "daiin · dar",
        "reading": "das Sollmaß aus der Quelle nehmen",
        "confidence": "HIGH",
        "reason": "H2-S002 writes measure then source as two adjacent cards. The source marker behaves as an address, not as a mandatory fused suffix.",
        "anchors": "E030,E031",
    },
    6: {
        "decision": "ALREADY_REALIZED_AS_TWO_CARDS",
        "revised": "cheedar · chldaiin",
        "reading": "aus der Quelle überführen und am vorgeschriebenen Wert weiterführen",
        "confidence": "HIGH",
        "reason": "B3-S026 already juxtaposes AR+TRANSFER and AIIN in one statement. The observed order is transfer-source then value continuation.",
        "anchors": "E285,E286",
    },
    7: {
        "decision": "KEEP_AS_NEW_COMPOUND",
        "revised": "pchedain",
        "reading": "eine Portion in den Empfänger überführen",
        "confidence": "HIGH",
        "reason": "pchedy supplies P+TRANSFER and chedain supplies AIN+TRANSFER. Their shared CHED body predicts the missing overlay pchedain.",
        "anchors": "E221,E303",
    },
    8: {
        "decision": "REWRITE_AS_TWO_CARD_WORKSTEP",
        "revised": "solkaiin · qokedy",
        "reading": "Sollmenge an der Sammelstelle halten; Arbeitsgang festsetzen",
        "confidence": "MEDIUM",
        "reason": "solkaiin already names the prescribed collection, while closure remains an operation card. A fused solkaiindy is therefore less workshop-like.",
        "anchors": "E178,E335",
    },
    9: {
        "decision": "KEEP_AS_NEW_GRADE_MEMBER",
        "revised": "lsheedy",
        "reading": "einen Waschgang länger halten und festsetzen",
        "confidence": "MEDIUM",
        "reason": "lshedy gives ungraded wash-close and the E/EE series supplies duration. The extra E is the economical long member.",
        "anchors": "E143,E261",
    },
    10: {
        "decision": "KEEP_AS_NEW_GRADE_MEMBER",
        "revised": "sheeedy",
        "reading": "vollständig absetzen und festsetzen",
        "confidence": "HIGH",
        "reason": "shedy/cheedy and sheedy already occupy short and long grades. A third E predicts the full-grade member directly.",
        "anchors": "E255,E261",
    },
    11: {
        "decision": "KEEP_AS_NEW_GRADE_MEMBER",
        "revised": "sheeckhal",
        "reading": "lange zur Zielpassage führen",
        "confidence": "HIGH",
        "reason": "sheckhal is the attested short target-passage. The normal EE extension predicts sheeckhal for the long grade.",
        "anchors": "E115,E187",
    },
    12: {
        "decision": "REWRITE_AS_TWO_CARD_WORKSTEP",
        "revised": "otar · qokchdy",
        "reading": "zum folgenden Quellposten wechseln; überführen und festsetzen",
        "confidence": "MEDIUM",
        "reason": "otar and OT+TRANSFER+CLOSE are each established, but the four-way fusion has no model for ordering AR against terminal DY. Two cards preserve both scopes.",
        "anchors": "E149,E363",
    },
}


def main() -> None:
    forecasts = read_tsv(P286)
    cards = read_tsv(CARDS)
    events = read_tsv(EVENTS)
    astro = read_tsv(ASTRO)
    ledger = read_tsv(LEDGER)
    event_by_id = {row["event_id"]: row for row in events}
    events_by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        events_by_statement[row["statement_id"]].append(row)

    audit: list[dict[str, object]] = []
    near: list[dict[str, object]] = []
    for forecast in forecasts:
        number = int(forecast["forecast"])
        target = set(tokens(forecast["predicted_family_recipe"]))
        exact_cards = [row for row in cards if set(tokens(row["family_parse"])) == target]
        exact_visible = sorted({row["master_form"] for row in exact_cards})

        candidates = []
        for row in cards:
            observed = set(tokens(row["family_parse"]))
            overlap = len(target & observed)
            if not overlap:
                continue
            candidates.append((overlap / len(target), -len(observed - target), row))
        candidates.sort(key=lambda item: (item[0], item[1], int(item[2]["prose_event_count"])), reverse=True)
        for rank, (_, _, row) in enumerate(candidates[:3], start=1):
            overlap = sorted(target & set(tokens(row["family_parse"])))
            near.append({
                "forecast": number,
                "match_rank": rank,
                "match_scope": "PROSE_SINGLE_CARD",
                "locus_or_statement": row["master_card_id"],
                "visible_sequence": row["master_form"],
                "observed_recipe_sequence": row["family_parse"],
                "covered_forecast_components": "+".join(overlap),
                "coverage_fraction": f"{len(overlap)}/{len(target)}",
                "interpretation": "paradigm neighbor; not automatically the forecast",
            })

        windows = []
        for statement_id, statement_events in events_by_statement.items():
            for start in range(len(statement_events)):
                for length in range(2, min(4, len(statement_events) - start) + 1):
                    window = statement_events[start:start + length]
                    union = set()
                    for row in window:
                        union.update(tokens(row["family_parse"]))
                    if target <= union:
                        windows.append((length, statement_id, window))
        for rank, (length, statement_id, window) in enumerate(sorted(windows, key=lambda item: (item[0], item[1]))[:3], start=1):
            near.append({
                "forecast": number,
                "match_rank": rank,
                "match_scope": "PROSE_ADJACENT_WINDOW",
                "locus_or_statement": statement_id,
                "visible_sequence": " · ".join(row["visible_surface"] for row in window),
                "observed_recipe_sequence": " | ".join(row["family_parse"] for row in window),
                "covered_forecast_components": "+".join(sorted(target)),
                "coverage_fraction": f"{len(target)}/{len(target)}",
                "interpretation": "all components occur locally; scope and order still require workshop reading",
            })

        decision = DECISIONS[number]
        anchor_rows = [event_by_id[event_id] for event_id in decision["anchors"].split(",")]
        astro_hits = sorted({row["resulting_visible_surface"] for row in astro if row["resulting_visible_surface"] in {a["visible_surface"] for a in anchor_rows}})
        audit.append({
            "forecast": number,
            "original_instruction_de": forecast["new_instruction_de"],
            "original_recipe": forecast["predicted_family_recipe"],
            "old_surface_skeleton": forecast["predicted_surface_skeleton"],
            "component_family_card_count": len(exact_cards),
            "component_family_visible_forms": "|".join(exact_visible) or "NONE",
            "old_predicted_surface_exact_hits": sum(1 for row in ledger if row["resulting_visible_surface"] == forecast["predicted_surface_skeleton"].replace("-", "")),
            "anchor_events": decision["anchors"],
            "anchor_surfaces": " · ".join(row["visible_surface"] for row in anchor_rows),
            "anchor_recipes": " | ".join(row["family_parse"] for row in anchor_rows),
            "astro_reuse_of_anchor_surface": "|".join(astro_hits) or "NONE",
            "workshop_decision": decision["decision"],
            "revised_writer_output": decision["revised"],
            "revised_reading_de": decision["reading"],
            "confidence": decision["confidence"],
            "workshop_reason": decision["reason"],
        })

    audit_path = HERE / "TWO_HUNDRED_NINETY_FIRST_12_FORECAST_AUDIT.tsv"
    near_path = HERE / "TWO_HUNDRED_NINETY_FIRST_OBSERVED_NEAR_MATCHES.tsv"
    write_tsv(audit_path, audit, list(audit[0]))
    write_tsv(near_path, near, list(near[0]))

    counts = Counter(row["workshop_decision"] for row in audit)
    report = f"""# Sidequest-Pass 291: die zwölf Lehrlingsprognosen im vorhandenen Deck

## Was gesucht wurde

Die zwölf in Pass 286 erfundenen Zusammensetzungen wurden gegen sämtliche bereits sichtbaren Karten und gegen benachbarte Kartenfolgen der zehn Seiten gehalten. Das ist ein Werkstatttest: Würde ein Schreiber den Inhalt wirklich zu einer neuen Karte verschmelzen, oder verwendet sein System lieber zwei gelernte Karten nacheinander?

## Ergebnis

- **Vier Prognosen sind schon als Zwei-Karten-Konstruktion vorhanden:** 2, 4, 5 und 6.
- **Fünf bleiben echte neue Kartenprognosen:** 3, 7, 9, 10 und 11.
- **Drei werden zu Zwei-Karten-Arbeitsgängen umgebaut:** 1, 8 und 12.
- Keine der zwölf alten Gerüstschreibungen kommt als exakte fertige Karte vor. Das ist kein Scheitern der Stämme; es zeigt eine bisher fehlende Regel: **Wert-/Adresskarten und abgeschlossene Tätigkeiten werden oft nicht zusammengeschweißt.**

Die stärkste neue Einzelvorhersage ist `pchedain`: `pchedy` liefert EMPFÄNGER+ÜBERFÜHREN, `chedain` PORTION+ÜBERFÜHREN. Die fehlende Überlagerung ist daher viel weniger frei erfunden als das alte abstrakte Gerüst `p-ain-ched`.

Die stärksten Gradvorhersagen sind:

- `lsheedy` — Waschgang länger halten und schließen;
- `sheeedy` — vollständig absetzen und schließen;
- `sheeckhal` — lange Zielpassage.

Hier wird jeweils nur ein bereits sichtbares E/EE/EEE-Raster um genau ein freies Fach erweitert.

## Die wichtigste Reparatur

`DY` ist keine beliebig anklebende Satzendungs-Silbe. Es gehört zu lizenzierten Tätigkeitskarten. Daher wird etwa „Sollmaß einsetzen und festsetzen“ nicht mehr als spekulatives `qokaiindy` geschrieben, sondern als `qokaiin · qokedy`: erst den Sollwert setzen, dann den Arbeitsgang ausführen und festsetzen. Dasselbe Prinzip repariert `solkaiin-dy` und die überladene Vierfachbildung OT+AR+TRANSFER+DY.

## Neue kurze Schreibtafel

1. Zielwert + Tätigkeit: meistens zwei Karten.
2. Adresse + Wert: darf als zwei Karten stehen; die Reihenfolge folgt dem Arbeitsgang.
3. Ein Modifikator innerhalb einer bekannten Tätigkeit: darf zu einer Karte verschmelzen.
4. E/EE/EEE wird nur in einer bereits sichtbaren Gradfamilie weitergeführt.
5. Ein fehlendes Paradigmenfeld bekommt genau eine Prognose; keine Kette freier Synonyme.

## Nächster Angriff

Die fünf verbliebenen Neubildungen sollen jetzt in ein kleines **Produktionsquadrat** gestellt werden: ihre Elternkarten, genaue Buchstabenüberlagerung, Lehrlingsabschrift und eine konkrete Beispielsituation. Danach wird geprüft, ob unsere 36 Stämme wirklich dieselbe innere Reihenfolge benutzen oder ob mehrere Kompositionstypen existieren.
"""
    (HERE / "TWO_HUNDRED_NINETY_FIRST_WORKSHOP_FORECAST_REPORT.md").write_text(report, encoding="utf-8")

    summary = {
        "status": "PASS",
        "forecasts": len(audit),
        "decision_counts": dict(sorted(counts.items())),
        "near_match_rows": len(near),
        "ledger_rows_checked": len(ledger),
        "astro_rows_checked": len(astro),
        "source_hashes": {str(path.relative_to(ROOT)): sha(path) for path in [P286, CARDS, EVENTS, ASTRO, LEDGER]},
        "outputs": {path.name: sha(path) for path in [audit_path, near_path, HERE / "TWO_HUNDRED_NINETY_FIRST_WORKSHOP_FORECAST_REPORT.md"]},
    }
    (HERE / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
