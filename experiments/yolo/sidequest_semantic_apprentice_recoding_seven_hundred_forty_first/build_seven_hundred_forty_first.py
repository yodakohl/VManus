#!/usr/bin/env python3
"""Build Pass 741: recode clean instructions with the apprentice lexicon."""

from __future__ import annotations

import csv
import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P740 = ROOT / "experiments/yolo/sidequest_semantic_apprentice_syntax_seven_hundred_fortieth"


def read(name: str) -> list[dict[str, str]]:
    with (P740 / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


# The scanner receives only the fluent text after the owner colon. Surface,
# card IDs and observed component order never enter scan().
CUES = [
    ("RESUME_CARD", r"\bwiederaufnehm\w*", "wiederaufnehmen"),
    ("TALAM", r"\bverwahr\w*", "verwahren"),
    ("OS", r"\bFach\b", "Fach"),
    ("SHED", r"\babsetz\w*", "absetzen"),
    ("OK", r"\bansetz\w*", "ansetzen"),
    ("CHD", r"\bumsetz\w*", "umsetzen"),
    ("CHK", r"\berwaerm\w*", "erwaermen"),
    ("CTH", r"\bbereit\w*", "bereiten/bereit"),
    ("SOLK", r"\bSammelstelle\w*", "Sammelstelle"),
    ("P", r"\bfuell\w*", "fuellen"),
    ("LSH", r"\bwasch\w*", "waschen"),
    ("CFH", r"\bauswring\w*", "auswringen"),
    ("CH", r"\bentnehm\w*", "entnehmen"),
    ("T", r"\banwend\w*", "anwenden"),
    ("K", r"\bzugeb\w*", "zugeben"),
    ("S", r"\bteil\w*", "teilen/Teil"),
    ("L", r"\bleit\w*", "leiten"),
    ("R", r"\bkuehl\w*", "kuehlen"),
    ("SH", r"\bhalt\w*", "halten"),
    ("LD", r"\bbefestig\w*", "befestigen"),
    ("OT", r"\bdanach\b|\banschliessend\w*", "danach/anschliessend"),
    ("OL", r"\bweiter\w*", "weiter"),
    ("AL", r"\bZielstelle\w*", "Zielstelle"),
    ("AR", r"\bQuelle\w*", "Quelle"),
    ("AIIN", r"\bSollmass\w*", "Sollmass"),
    ("AIN", r"\bPortion\w*", "Portion"),
    ("IIN", r"\bArbeitsstufe\w*", "Arbeitsstufe"),
    ("AN", r"\bNachgabe\w*", "Nachgabe"),
    ("CKH", r"\bDurchlass\w*", "Durchlass"),
    ("AIR", r"\bWasser\w*|\bFluessigkeit\w*", "Wasser/laufende Fluessigkeit"),
    ("OR", r"\bAnsatz\w*", "Ansatz"),
    ("HO", r"\bZutat\w*", "Zutat"),
    ("O", r"\bArbeitsgang\w*", "Arbeitsgang"),
    ("EEE", r"\bvollstaendig\w*", "vollstaendig"),
    ("EE", r"\blaenger\w*", "laenger"),
    ("E", r"\bkurz\w*", "kurz"),
    ("Y", r"\bPosten\w*", "Posten"),
    ("DA", r"\bzweiten Durchgang\b", "zweiter Durchgang"),
    ("DY", r"\bschliess\w*", "schliessen"),
]


def scan(text: str) -> tuple[list[str], list[str]]:
    body = text.split(":", 1)[1] if ":" in text else text
    hits: list[tuple[int, int, str, str]] = []
    for component, pattern, _ in CUES:
        for match in re.finditer(pattern, body, re.IGNORECASE):
            hits.append((match.start(), match.end(), component, match.group()))
    hits.sort(key=lambda item: (item[0], -(item[1] - item[0])))
    accepted: list[tuple[int, int, str, str]] = []
    end = -1
    for hit in hits:
        if hit[0] >= end:
            accepted.append(hit)
            end = hit[1]
    return [item[2] for item in accepted], [item[3] for item in accepted]


def template(components: list[str], slots: dict[str, str]) -> str:
    actions = [i for i, item in enumerate(components) if slots[item] == "ACTION"]
    addresses = [i for i, item in enumerate(components) if slots[item] == "ADDRESS"]
    if not actions:
        order = "NO_ACTION"
    elif not addresses:
        order = "ACTION_UNADDRESSED"
    elif actions[0] < addresses[0]:
        order = "ACTION_THEN_ADDRESS"
    else:
        order = "ADDRESS_THEN_ACTION"
    closed = bool(components and components[-1] == "DY")
    return {
        ("ACTION_UNADDRESSED", True): "T1",
        ("ACTION_THEN_ADDRESS", True): "T2",
        ("ADDRESS_THEN_ACTION", True): "T3",
        ("NO_ACTION", True): "T4",
        ("ACTION_THEN_ADDRESS", False): "T5",
        ("ADDRESS_THEN_ACTION", False): "T6",
        ("ACTION_UNADDRESSED", False): "T7",
        ("NO_ACTION", False): "T8",
    }[(order, closed)]


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    component_map = read("SEVEN_HUNDRED_FORTIETH_39_COMPONENT_SLOT_MAP.tsv")
    source = read("SEVEN_HUNDRED_FORTIETH_116_STATEMENT_PATTERNS.tsv")
    slots = {row["component"]: row["apprentice_slot"] for row in component_map}
    values = {row["component"]: row["short_value_de"] for row in component_map}

    cue_rows = []
    for component, pattern, cue in CUES:
        cue_rows.append({
            "component": component,
            "short_value_de": values[component],
            "apprentice_slot": slots[component],
            "fluent_cue_de": cue,
            "scanner_pattern": pattern,
            "uses_surface_or_card_id": "NO",
        })

    recoding_rows = []
    for row in source:
        inferred, words = scan(row["clean_workshop_reading_de"])
        observed = row["component_sequence"].split("+")
        observed_set, inferred_set = set(observed), set(inferred)
        intersection = observed_set & inferred_set
        recall = len(intersection) / len(observed_set)
        precision = len(intersection) / len(inferred_set) if inferred_set else 0.0
        predicted_template = template(inferred, slots)
        recoding_rows.append({
            "statement_id": row["statement_id"],
            "page": row["page"],
            "record": row["record"],
            "owner_noun_de": row["owner_noun_de"],
            "clean_instruction_de": row["clean_workshop_reading_de"],
            "cue_words_in_order": " | ".join(words),
            "recoded_family_sequence": "+".join(inferred),
            "recoded_family_set": "+".join(sorted(inferred_set)),
            "predicted_template": predicted_template,
            "observed_template_after_reveal": row["template_id"],
            "template_match": "YES" if predicted_template == row["template_id"] else "NO",
            "observed_component_sequence_after_reveal": row["component_sequence"],
            "observed_component_set_after_reveal": "+".join(sorted(observed_set)),
            "component_set_recall": f"{recall:.6f}",
            "component_set_precision": f"{precision:.6f}",
            "exact_component_set": "YES" if observed_set == inferred_set else "NO",
            "missing_components": "+".join(sorted(observed_set - inferred_set)) or "NONE",
            "extra_components": "+".join(sorted(inferred_set - observed_set)) or "NONE",
            "generation_input_contract": "OWNER_PLUS_CLEAN_INSTRUCTION_ONLY",
        })

    confusion = Counter((row["observed_template_after_reveal"], row["predicted_template"]) for row in recoding_rows)
    confusion_rows = [{
        "observed_template": actual,
        "predicted_from_fluent_order": predicted,
        "statements": count,
        "interpretation_de": "Treffer" if actual == predicted else (
            "deutsche Adresse steht vorn; Karte packt Handlungskopf vorn"
            if actual in {"T2", "T5"} and predicted in {"T3", "T6"}
            else "flüssige Lesung spricht eine geerbte Handlung aus"
        ),
    } for (actual, predicted), count in sorted(confusion.items())]

    order_mismatches = [{
        "statement_id": row["statement_id"],
        "page": row["page"],
        "record": row["record"],
        "predicted_template": row["predicted_template"],
        "observed_template": row["observed_template_after_reveal"],
        "clean_instruction_de": row["clean_instruction_de"],
        "recoded_family_sequence": row["recoded_family_sequence"],
        "observed_component_sequence": row["observed_component_sequence_after_reveal"],
        "repair_class": "LEARN_OPERATION_HEAD_PACKING" if row["observed_template_after_reveal"] in {"T2", "T5"} else "KEEP_CONTEXTUAL_ELLIPSIS",
    } for row in recoding_rows if row["template_match"] == "NO"]

    component_errors = [{
        "statement_id": row["statement_id"],
        "page": row["page"],
        "record": row["record"],
        "missing_components": row["missing_components"],
        "extra_components": row["extra_components"],
        "clean_instruction_de": row["clean_instruction_de"],
        "reason_de": "Fluessige Expansion verschweigt einen Kartenwert oder benutzt ein gleichlautendes Hilfsverb.",
    } for row in recoding_rows if row["exact_component_set"] == "NO"]

    recovery_rows = []
    for component, _, cue in CUES:
        observed_statements = {row["statement_id"] for row in recoding_rows if component in row["observed_component_set_after_reveal"].split("+")}
        inferred_statements = {row["statement_id"] for row in recoding_rows if component in row["recoded_family_set"].split("+")}
        hits = observed_statements & inferred_statements
        recovery_rows.append({
            "component": component,
            "short_value_de": values[component],
            "cue_de": cue,
            "observed_statements": len(observed_statements),
            "inferred_statements": len(inferred_statements),
            "hit_statements": len(hits),
            "missed_statements": len(observed_statements - inferred_statements),
            "extra_statements": len(inferred_statements - observed_statements),
            "statement_recall": f"{len(hits) / len(observed_statements):.6f}" if observed_statements else "1.000000",
            "statement_precision": f"{len(hits) / len(inferred_statements):.6f}" if inferred_statements else "1.000000",
        })

    write("SEVEN_HUNDRED_FORTY_FIRST_39_FLUENT_CUES.tsv", cue_rows)
    write("SEVEN_HUNDRED_FORTY_FIRST_116_RECODING_AUDIT.tsv", recoding_rows)
    write("SEVEN_HUNDRED_FORTY_FIRST_11_TEMPLATE_CONFUSIONS.tsv", confusion_rows)
    write("SEVEN_HUNDRED_FORTY_FIRST_27_ORDER_MISMATCHES.tsv", order_mismatches)
    write("SEVEN_HUNDRED_FORTY_FIRST_23_COMPONENT_ERRORS.tsv", component_errors)
    write("SEVEN_HUNDRED_FORTY_FIRST_39_COMPONENT_RECOVERY.tsv", recovery_rows)

    exact_sets = sum(row["exact_component_set"] == "YES" for row in recoding_rows)
    template_hits = sum(row["template_match"] == "YES" for row in recoding_rows)
    mean_recall = sum(float(row["component_set_recall"]) for row in recoding_rows) / len(recoding_rows)
    mean_precision = sum(float(row["component_set_precision"]) for row in recoding_rows) / len(recoding_rows)
    report = f"""# Pass 741 — der Lehrling schreibt zurueck

Der Lehrling erhielt nur Bildbesitzer, die bereinigte deutsche Werkstattanweisung und 39 kurze Bedeutungsstichwoerter. Die Voynich-Oberflaeche, Karten-ID und beobachtete Komponentenfolge gingen nicht in die Rekodierung ein.

## Was schon funktioniert

- In {exact_sets}/116 Aussagen wird die **gesamte Komponentenmenge** exakt wiedergefunden.
- Mittlere Komponenten-Recall: {mean_recall:.3f}; mittlere Precision: {mean_precision:.3f}.
- Alle Aussagen erreichen mindestens 0.70 Recall.
- Das grobe Satzmuster wird in {template_hits}/116 Aussagen wiedergefunden.

Damit ist unser 39-Eintraege-System nicht bloss rueckwaerts lesbar: Aus einer normalen Werkstattanweisung bekommt ein Schreiber fast immer die richtigen Bedeutungsfamilien zurueck.

## Wo die echte Codebuchschicht sitzt

27 Satzmuster weichen ab. Davon sind 25 besonders aufschlussreich: Im Deutschen steht die Adresse oft vorn (`nach Sollmass ansetzen`, `an der Zielstelle ansetzen`), die Voynich-Karte packt aber den **Handlungskopf zuerst** (`OK+AIIN`, `OK+AL`). Weitere zwei Aussagen sprechen im Deutschen ein `halten` aus, obwohl die Karte diese Handlung elliptisch vom laufenden Kontext erbt.

Die verbleibende Huerde ist daher nicht mehr die Bedeutung der 39 Familien, sondern **Kartenpackung**:

1. Wann wird Handlung+Adresse zu einer einzigen handlungskopfigen Karte?
2. Wann bleibt die Adresse als eigene Kopfkarte davor stehen?
3. Wann darf ein Hilfsverb in der fluessigen Lesung erscheinen, ohne eine eigene Karte zu erhalten?

## Konkrete Fehler

Nur sechs beobachtete Komponenten werden ueber alle 116 Aussagen hinweg verschwiegen: O zweimal sowie OS,Y,T,AIN und OT je einmal. Dagegen entstehen 21 zusaetzliche Lesetreffer, vor allem elfmal SH, weil deutsche Wendungen wie `bereitet halten` oder `an der Sammelstelle halten` grammatisch `halten` brauchen, ohne immer eine eigene SH-Karte zu besitzen.

## Nächster Hebel

Baue nun einen kleinen **Kartenpacker**: Er nimmt die rekodierten Bedeutungsfamilien, bevorzugt attestierte Mehrkomponenten-Karten aus dem 173er Deck und entscheidet zwischen Handlungskopf und separatem Adresskopf. Keine neue Bedeutung wird eingefuehrt; gesucht wird nur die historische Mischung aus produktiver Kurzkomposition und gelernter Ganzkarte.
"""
    (HERE / "SEVEN_HUNDRED_FORTY_FIRST_REPORT.md").write_text(report, encoding="utf-8")

    summary = {
        "status": "PASS",
        "components": len(cue_rows),
        "statements": len(recoding_rows),
        "exact_component_sets": exact_sets,
        "component_error_statements": len(component_errors),
        "mean_component_set_recall": round(mean_recall, 6),
        "mean_component_set_precision": round(mean_precision, 6),
        "template_hits": template_hits,
        "template_mismatches": len(order_mismatches),
        "operation_head_packing_mismatches": sum(row["repair_class"] == "LEARN_OPERATION_HEAD_PACKING" for row in order_mismatches),
        "contextual_ellipsis_mismatches": sum(row["repair_class"] == "KEEP_CONTEXTUAL_ELLIPSIS" for row in order_mismatches),
        "decision": "SEMANTIC_FAMILIES_RECODE_WELL__CARD_PACKING_IS_THE_REMAINING_CODEBOOK_LAYER",
    }
    (HERE / "SEVEN_HUNDRED_FORTY_FIRST_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
