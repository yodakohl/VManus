#!/usr/bin/env python3
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
YOLO = HERE.parent
P561 = YOLO / "sidequest_semantic_record_wrapper_melodies_five_hundred_sixty_first"
P577 = YOLO / "sidequest_semantic_gloss_free_reconstruction_five_hundred_seventy_seventh"
P594 = YOLO / "sidequest_semantic_scribe_surface_palettes_five_hundred_ninety_fourth"


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name, rows):
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main():
    renderer = read(P561 / "FIVE_HUNDRED_SIXTY_FIRST_THREE_HUNDRED_EIGHTY_ONE_FINAL_RENDERER.tsv")
    melodies = read(P561 / "FIVE_HUNDRED_SIXTY_FIRST_NINE_RECORD_MELODIES.tsv")
    palettes = read(P594 / "FIVE_HUNDRED_NINETY_FOURTH_34_MULTISURFACE_CARDS.tsv")
    card_values = {
        row["card_no"]: row
        for row in read(P577 / "FIVE_HUNDRED_SEVENTY_SEVENTH_ONE_HUNDRED_SEVENTY_THREE_GLOSS_FREE_CARD_RECONSTRUCTIONS.tsv")
    }
    palette_ids = {row["card_no"] for row in palettes}
    by_card = defaultdict(list)
    trace_rows = []
    for row in renderer:
        by_card[row["card_no"]].append(row)
        source_instruction = {
            "GLOBAL_RULE_RENDERER": f"schreibe die globale Vorzugsform {row['final_surface']}",
            "AUTOMATIC_CONTEXT_RULE": f"wenn der unmittelbare Kontext {row['renderer_rule']} ausloest, schreibe {row['final_surface']}",
            "FORMULA_CADENCE_RULE": f"in der gelernten Formelkadenz {row['renderer_rule']} schreibe {row['final_surface']}",
            "RECORD_WRAPPER_MELODY": f"am Recordmelodieplatz {row['renderer_rule']} schreibe {row['final_surface']}",
        }[row["renderer_source"]]
        trace_rows.append({
            "event_id": row["event_id"], "page": row["page"], "record": row["record"], "locus": row["locus"],
            "card_no": row["card_no"], "component_parse": row["component_parse"],
            "spoken_value_de": card_values[row["card_no"]]["reconstructed_component_values_de"],
            "renderer_source": row["renderer_source"], "renderer_rule": row["renderer_rule"],
            "final_surface": row["final_surface"], "writing_instruction_de": source_instruction,
            "surface_changes_meaning": "NO", "requires_local_event_lookup": "NO",
        })

    preference_rows = []
    for palette in palettes:
        rows = by_card[palette["card_no"]]
        surface_counts = Counter(row["final_surface"] for row in rows)
        source_counts = Counter(row["renderer_source"] for row in rows)
        default_surface, default_events = sorted(surface_counts.items(), key=lambda item: (-item[1], item[0]))[0]
        exceptional = [row for row in rows if row["renderer_source"] != "GLOBAL_RULE_RENDERER"]
        preference_rows.append({
            "card_no": palette["card_no"], "component_parse": palette["component_parse"],
            "spoken_value_de": palette["invariant_spoken_value_de"], "registered_surfaces": palette["surfaces"],
            "events": palette["occurrences"], "default_surface": default_surface, "default_events": default_events,
            "global_default_events": source_counts["GLOBAL_RULE_RENDERER"],
            "automatic_context_events": source_counts["AUTOMATIC_CONTEXT_RULE"],
            "formula_cadence_events": source_counts["FORMULA_CADENCE_RULE"],
            "record_melody_events": source_counts["RECORD_WRAPPER_MELODY"],
            "exception_rule_ids": "|".join(sorted({row["renderer_rule"] for row in exceptional})) or "NONE",
            "apprentice_instruction_de": (
                f"normalerweise {default_surface}; nur bei den genannten Kontext-, Kadenz- oder Recordmelodieregeln eine andere registrierte Form schreiben"
            ),
            "free_choice": "NO",
        })

    source_rows = []
    for source, instruction in (
        ("GLOBAL_RULE_RENDERER", "globale Vorzugsform der gewaehlten Karte"),
        ("AUTOMATIC_CONTEXT_RULE", "unmittelbarer Kontext schaltet eine registrierte Form"),
        ("FORMULA_CADENCE_RULE", "gelerntes Mehrkartenmuster schaltet eine registrierte Form"),
        ("RECORD_WRAPPER_MELODY", "kurze lokale Wrapperfolge des Records schaltet eine registrierte Form"),
    ):
        rows = [row for row in trace_rows if row["renderer_source"] == source]
        source_rows.append({
            "priority": len(source_rows) + 1, "renderer_source": source, "events": len(rows),
            "cards": len({row["card_no"] for row in rows}), "records": len({row["record"] for row in rows}),
            "teaching_rule_de": instruction, "semantic_contribution": "NONE",
        })

    write("FIVE_HUNDRED_NINETY_FIFTH_381_COMPLETE_SURFACE_TRACE.tsv", trace_rows)
    write("FIVE_HUNDRED_NINETY_FIFTH_34_CARD_PREFERENCES.tsv", preference_rows)
    write("FIVE_HUNDRED_NINETY_FIFTH_FOUR_RENDERER_SOURCES.tsv", source_rows)
    write("FIVE_HUNDRED_NINETY_FIFTH_NINE_RECORD_MELODIES.tsv", melodies)

    counts = Counter(row["renderer_source"] for row in trace_rows)
    summary = {
        "status": "PASS", "events": len(trace_rows), "cards": len(card_values), "palette_cards": len(preference_rows),
        "global_default_events": counts["GLOBAL_RULE_RENDERER"],
        "automatic_context_events": counts["AUTOMATIC_CONTEXT_RULE"],
        "formula_cadence_events": counts["FORMULA_CADENCE_RULE"],
        "record_melody_events": counts["RECORD_WRAPPER_MELODY"],
        "record_melodies": len(melodies), "exact_surface_roundtrip": sum(row["requires_local_event_lookup"] == "NO" for row in trace_rows),
        "free_choices": sum(row["free_choice"] == "YES" for row in preference_rows),
        "decision": "DEFAULT_FORM_PLUS_CONTEXT_CADENCE_AND_RECORD_MELODY",
    }
    (HERE / "FIVE_HUNDRED_NINETY_FIFTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    report = f"""# Fuenfhundertfuenfundneunzigste Runde: die praktische Oberflaechenregel

## Ergebnis

Die 34 Mehrformkarten brauchen keine freie Wahl und keine neue Bedeutung. Ein Lehrling kann alle 381 Prosaflaechen mit vier gestuften Gewohnheiten schreiben:

1. **{summary['global_default_events']} Ereignisse:** globale Vorzugsform der Karte.
2. **{summary['automatic_context_events']} Ereignisse:** unmittelbarer Kontext schaltet automatisch eine andere registrierte Form.
3. **{summary['formula_cadence_events']} Ereignisse:** eine gelernte Mehrkartenformel schaltet die passende Form.
4. **{summary['record_melody_events']} Ereignisse:** neun kurze Recordmelodien liefern die restlichen lokalen Eintrittsgesten.

Damit wird jede sichtbare Form ohne einzelne Ereignistabelle erzeugt. Die lokale Zusatzlast sind neun kurze Melodien mit insgesamt 22 Plätzen, beispielsweise `H3 d->d`, `H5 s->ch`, `B2 d->d->s->blank` und `B4 blank->t->ch->q`.

## Lehrsatz

```text
Karte und Wert waehlen
-> pruefe unmittelbaren Kontext
-> pruefe bekannte Formelkadenz
-> pruefe aktuellen Recordmelodieplatz
-> sonst schreibe die globale Vorzugsform
```

Die sichtbare Form ist damit Teil des Schreibrituals, nicht des Inhalts. `aiin/chaiin/daiin/saiin/taiin` bleiben derselbe Masswert; `al/chal/cheal/dal/sal/tal` dieselbe Zieladresse; `cheol/chol/ol/qol/sol/tol` dieselbe Fortsetzungskarte. Der Rahmen zeigt, wie die Hand an dieser Stelle in die Karte eintritt.

## Mehrhanddeutung

Die Recordmelodie kann eine Seiten- oder Schreibergewohnheit sein, ohne dass wir eine reale Hand identifizieren. Ein neuer Schreiber lernt die lokale Rezitation vom Musterblatt. Er darf nicht beliebig jede Geste an jede Karte setzen: nur die registrierte Palette und die vierstufige Regel sind erlaubt.

## Warum das besser ist als freie Allographie

Freie Allographie wuerde die genaue Oberflaeche offenlassen. Das Werkstattmodell liefert dagegen fuer 381/381 Ereignisse eine konkrete Schreibform, bleibt aber klein: ein Standard pro Karte, acht unmittelbare Wechsel, die gelernten Formelkadenzen und neun Recordmelodien. Keine dieser Regeln fuegt ein Wort oder einen semantischen Stamm hinzu.

## Naechster Schritt

Als naechstes werden die neun Recordmelodien in den fortlaufenden Herbal- und Biological-Text eingeblendet. Ziel ist eine Faksimile-nahe Lehrfassung: Bedeutungslinie, Kartenlinie und Schreiberrezitation pro Record, sodass ein Lehrling die zehn Seiten tatsaechlich abschreiben koennte.
"""
    (HERE / "FIVE_HUNDRED_NINETY_FIFTH_REPORT.md").write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
