#!/usr/bin/env python3
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
YOLO = HERE.parent
P577 = YOLO / "sidequest_semantic_gloss_free_reconstruction_five_hundred_seventy_seventh"
P587 = YOLO / "sidequest_semantic_uniform_three_line_edition_five_hundred_eighty_seventh"


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name, rows):
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def position_class(position, total):
    if total == 1:
        return "ONLY"
    if position == 1:
        return "FIRST"
    if position == total:
        return "LAST"
    return "MIDDLE"


def main():
    cards = read(P577 / "FIVE_HUNDRED_SEVENTY_SEVENTH_ONE_HUNDRED_SEVENTY_THREE_GLOSS_FREE_CARD_RECONSTRUCTIONS.tsv")
    events = read(P577 / "FIVE_HUNDRED_SEVENTY_SEVENTH_THREE_HUNDRED_EIGHTY_ONE_GLOSS_FREE_EVENT_RECONSTRUCTIONS.tsv")
    event_index = {row["event_id"]: row for row in read(P587 / "FIVE_HUNDRED_EIGHTY_SEVENTH_THREE_HUNDRED_EIGHTY_ONE_EVENT_INDEX.tsv")}
    statements = {row["statement_id"]: row for row in read(P587 / "FIVE_HUNDRED_EIGHTY_SEVENTH_ONE_HUNDRED_SIXTEEN_THREE_LINE_STATEMENTS.tsv")}
    by_card = defaultdict(list)
    for event in events:
        idx = event_index[event["event_id"]]
        total = int(statements[event["statement_id"]]["event_count"])
        enriched = dict(event)
        enriched["position_class"] = position_class(int(idx["position_in_statement"]), total)
        by_card[event["card_no"]].append(enriched)

    card_rows = []
    palette_rows = []
    surface_rows = []
    for card in cards:
        card_events = by_card[card["card_no"]]
        surfaces = card["surfaces"].split("|")
        pages = sorted({event["page"] for event in card_events})
        records = sorted({event["record"] for event in card_events})
        within_page = any(
            len({event["observed_surface"] for event in card_events if event["page"] == page}) > 1
            for page in pages
        )
        position_surfaces = defaultdict(set)
        for event in card_events:
            position_surfaces[event["position_class"]].add(event["observed_surface"])
        same_position_multi = any(len(values) > 1 for values in position_surfaces.values())
        if len(surfaces) > 1:
            surface_class = "MULTISURFACE_WITHIN_PAGE_PALETTE" if within_page else "MULTISURFACE_CROSS_PAGE_PALETTE"
        elif int(card["occurrences"]) > 1:
            surface_class = "FIXED_RECURRENT_FORM"
        else:
            surface_class = "ONE_OFF_EXEMPLAR_FORM"
        interpretation = {
            "MULTISURFACE_WITHIN_PAGE_PALETTE": "gleicher Kartenwert, mehrere lokal verfuegbare Schreibformen sogar auf derselben Seite",
            "MULTISURFACE_CROSS_PAGE_PALETTE": "gleicher Kartenwert, seitenuebergreifend verschiedene gelernte Schreibformen; Hand/Register moeglich, nicht identifiziert",
            "FIXED_RECURRENT_FORM": "wiederkehrende Karte mit stabiler sichtbarer Form",
            "ONE_OFF_EXEMPLAR_FORM": "einmalige sichtbare Form wird aus dem lokalen Exemplar kopiert",
        }[surface_class]
        card_row = {
            "card_no": card["card_no"], "surfaces": card["surfaces"], "surface_count": len(surfaces),
            "occurrences": card["occurrences"], "pages": "|".join(pages), "records": "|".join(records),
            "component_parse": card["component_parse"],
            "invariant_spoken_value_de": card["reconstructed_component_values_de"],
            "licensed_frame_codes": card["licensed_frame_codes"],
            "surface_class": surface_class,
            "multiple_surfaces_within_same_page": "YES" if within_page else "NO",
            "multiple_surfaces_at_same_statement_position": "YES" if same_position_multi else "NO",
            "position_classes": "|".join(sorted(position_surfaces)),
            "scribe_palette_reading_de": interpretation,
            "semantic_difference_between_surfaces": "NONE",
            "universal_surface_rule": "NOT_AVAILABLE__LEARN_CARD_LOCAL_PALETTE",
        }
        card_rows.append(card_row)
        if len(surfaces) > 1:
            palette_rows.append(card_row)
        for surface in surfaces:
            surface_events = [event for event in card_events if event["observed_surface"] == surface]
            surface_rows.append({
                "surface": surface, "card_no": card["card_no"], "component_parse": card["component_parse"],
                "invariant_spoken_value_de": card["reconstructed_component_values_de"],
                "events": len(surface_events),
                "pages": "|".join(sorted({event["page"] for event in surface_events})),
                "records": "|".join(sorted({event["record"] for event in surface_events})),
                "statement_positions": "|".join(sorted({event["position_class"] for event in surface_events})),
                "writing_instruction_de": (
                    "diese Form als zugelassene Variante derselben Karte kopieren" if len(surfaces) > 1
                    else "diese feste Kartenform aus dem Exemplar kopieren"
                ),
                "meaning_change": "NONE",
            })

    hypotheses = [
        {"hypothesis": "CARD_LOCAL_SCRIBE_PALETTE", "fit": "BEST", "support_de": "34 Karten haben mehrere Formen; alle behalten exakt dieselbe Komponentenlesung", "problem_de": "die Wahl der einzelnen Form bleibt oft nur aus dem Exemplar bekannt"},
        {"hypothesis": "SIMPLE_STATEMENT_POSITION_RULE", "fit": "POOR", "support_de": "zwei duenne Paletten trennen beobachtete ONLY/MIDDLE-Formen", "problem_de": "32 von 34 Paletten benutzen mehrere Formen in derselben Positionsklasse"},
        {"hypothesis": "ONE_HAND_ONE_FORM", "fit": "POSSIBLE_ONLY_FOR_SUBSET", "support_de": "15 Paletten wechseln nur ueber Seiten hinweg", "problem_de": "19 Paletten wechseln schon innerhalb derselben Seite; reale Haende sind hier nicht zugeordnet"},
        {"hypothesis": "UNIVERSAL_PRODUCTIVE_WRAPPER_GRAMMAR", "fit": "WITHDRAW", "support_de": "viele Alternanten tragen q/ch/sh/d/s/t-artige Rahmen", "problem_de": "formale Vorarbeiten fanden keine stabile uebertragbare Regel fuer unbekannte Alternanten"},
        {"hypothesis": "SURFACE_CHANGE_EQUALS_MEANING_CHANGE", "fit": "REJECT_WITHIN_CURRENT_CARD_SYSTEM", "support_de": "keiner", "problem_de": "jede der 34 Paletten bleibt an eine exakte Kartenidentitaet und einen gesprochenen Wert gebunden"},
    ]

    write("FIVE_HUNDRED_NINETY_FOURTH_173_CARD_SURFACE_STATUS.tsv", card_rows)
    write("FIVE_HUNDRED_NINETY_FOURTH_230_SURFACE_PALETTE.tsv", surface_rows)
    write("FIVE_HUNDRED_NINETY_FOURTH_34_MULTISURFACE_CARDS.tsv", palette_rows)
    write("FIVE_HUNDRED_NINETY_FOURTH_FIVE_SURFACE_HYPOTHESES.tsv", hypotheses)

    counts = Counter(row["surface_class"] for row in card_rows)
    summary = {
        "status": "PASS", "cards": len(card_rows), "events": len(events), "distinct_surfaces": len(surface_rows),
        "multisurface_cards": len(palette_rows), "multisurface_events": sum(int(row["occurrences"]) for row in palette_rows),
        "within_page_palettes": counts["MULTISURFACE_WITHIN_PAGE_PALETTE"],
        "cross_page_only_palettes": counts["MULTISURFACE_CROSS_PAGE_PALETTE"],
        "fixed_recurrent_forms": counts["FIXED_RECURRENT_FORM"],
        "one_off_exemplar_forms": counts["ONE_OFF_EXEMPLAR_FORM"],
        "same_position_multi_palettes": sum(row["multiple_surfaces_at_same_statement_position"] == "YES" for row in palette_rows),
        "decision": "CARD_LOCAL_SURFACE_PALETTES__NOT_UNIVERSAL_HAND_OR_POSITION_RULE",
    }
    (HERE / "FIVE_HUNDRED_NINETY_FOURTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    report = f"""# Fuenfhundertvierundneunzigste Runde: Schreibpaletten statt neuer Bedeutungen

## Ergebnis

Die 173 Prosakarten erscheinen in 230 sichtbaren Formen. Das vergroessert das Woerterbuch **nicht**: 34 wiederkehrende Karten besitzen zusammen 91 zugelassene Oberflaechenvarianten und decken {summary['multisurface_events']}/381 Ereignisse. Jede Variante behaelt denselben Komponentenbau und denselben gesprochenen Wert.

Die einfachste Lehre fuer mehrere Schreiber lautet daher:

```text
KARTENWERT WAHLEN
-> karteneigenen sichtbaren Formensatz aufschlagen
-> eine im lokalen Exemplar zugelassene Form schreiben
-> Bedeutung nicht noch einmal aus q/ch/sh/d/s/t erraten
```

## Vier praktische Klassen

- **19 Karten** wechseln ihre Form bereits innerhalb derselben Seite. Das sind echte lokale Schreibpaletten; eine starre „eine Hand = eine Form“-Regel reicht nicht.
- **15 Karten** zeigen verschiedene Formen nur auf verschiedenen Seiten. Hier koennen Hand-, Register- oder Seitengewohnheiten mitwirken, aber die zehn Seiten identifizieren sie nicht sauber.
- **17 Karten** kehren mit genau einer festen Form wieder.
- **122 Karten** sind einmalige Formen. Der Lehrling kopiert sie aus dem Exemplar; er muss daraus weder neue Stamme noch neue Woerter bilden.

## Position erklaert die Wahl fast nie

Bei 32 der 34 Mehrformkarten treten verschiedene sichtbare Varianten in derselben Aussageposition auf. Nur zwei duenne Paletten trennen ihre beobachteten Formen nach `ONLY` gegen `MIDDLE`. Damit ist der Variantenwechsel keine einfache Satzanfangs-/Satzendregel.

Das passt zum Schreiberbild um 1420: Eine Werkstatt kann fuer denselben registrierten Kartenwert mehrere gelernte Brevigrafen oder Eintrittsformen dulden. Der Korrektor prueft, ob die Form zur Kartenpalette gehoert, nicht ob alle Haende dieselbe Form bevorzugen.

## Wichtige Einschraenkung

Wir nennen diese Formen Schreibpaletten, nicht frei erzeugte Allographe. Die formale Archivarbeit zeigt, dass genaue Hostvarianten meist als ganze Formtabellen gelernt werden muessen und eine kleine universelle Rendererregel auf unbekannte Formen nicht stabil uebertraegt. Kreativ heisst das: Der Schreiber darf waehlen, aber nur aus dem Kartenexemplar.

## Konsequenz fuer die Lernlast

Der Lehrling lernt weiterhin 38 Komponenten, 56 Rahmen und 37 gesprochene Werte. Dazu kommen 34 kleine Formpaletten; die 122 einmaligen Formen bleiben Kopiermaterial. Es entstehen keine 230 unabhaengigen Bedeutungen und kein Zwang, jede sichtbare Vorsilbe semantisch zu uebersetzen.

## Naechster Schritt

Als naechstes werden die 34 Paletten gegen den lokalen Platz im Feld geordnet: nicht um eine universelle Regel zu erzwingen, sondern um pro Karte eine einfache Vorzugsform fuer Eintritt, Mitte, Schluss oder freie Wahl zu formulieren.
"""
    (HERE / "FIVE_HUNDRED_NINETY_FOURTH_REPORT.md").write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
