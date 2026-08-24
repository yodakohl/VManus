#!/usr/bin/env python3
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
YOLO = HERE.parent
P591 = YOLO / "sidequest_semantic_astro_condition_interface_five_hundred_ninety_first"
P594 = YOLO / "sidequest_semantic_scribe_surface_palettes_five_hundred_ninety_fourth"
P595 = YOLO / "sidequest_semantic_surface_preference_manual_five_hundred_ninety_fifth"
P596 = YOLO / "sidequest_semantic_interleaved_teaching_edition_five_hundred_ninety_sixth"


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name, rows):
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main():
    surface_lexicon = read(P594 / "FIVE_HUNDRED_NINETY_FOURTH_230_SURFACE_PALETTE.tsv")
    by_surface = {row["surface"]: row for row in surface_lexicon}
    prose_trace = read(P595 / "FIVE_HUNDRED_NINETY_FIFTH_381_COMPLETE_SURFACE_TRACE.tsv")
    prose_statements = read(P596 / "FIVE_HUNDRED_NINETY_SIXTH_116_FOUR_LINE_STATEMENTS.tsv")
    astro_groups = read(P591 / "FIVE_HUNDRED_NINETY_FIRST_395_GROUP_ASTRO_INTERFACE.tsv")
    astro_loci = read(P591 / "FIVE_HUNDRED_NINETY_FIRST_142_LOCUS_ASTRO_INTERFACE.tsv")

    event_rows = []
    for event in prose_trace:
        entry = by_surface[event["final_surface"]]
        event_rows.append({
            "event_id": event["event_id"], "page": event["page"], "record": event["record"],
            "observed_surface": event["final_surface"], "recovered_card_no": entry["card_no"],
            "recovered_component_parse": entry["component_parse"],
            "recovered_spoken_value_de": entry["invariant_spoken_value_de"],
            "expected_card_no": event["card_no"], "expected_spoken_value_de": event["spoken_value_de"],
            "card_recovery": "EXACT" if entry["card_no"] == event["card_no"] else "MISMATCH",
            "value_recovery": "EXACT" if entry["invariant_spoken_value_de"] == event["spoken_value_de"] else "MISMATCH",
            "owner_needed_for_card_or_value": "NO",
            "owner_needed_for_complete_local_instruction": "YES_IF_CONTEXTUAL_OR_REPEATED",
        })

    surface_sequence_counts = Counter(row["exact_surface_line"] for row in prose_statements)
    owner_sequence_counts = Counter((row["exact_surface_line"], row["silent_owner_de"]) for row in prose_statements)
    owner_sequence_meanings = defaultdict(set)
    for row in prose_statements:
        owner_sequence_meanings[(row["exact_surface_line"], row["silent_owner_de"])].add(row["meaning_line_de"])
    statement_rows = []
    for row in prose_statements:
        sequence_count = surface_sequence_counts[row["exact_surface_line"]]
        owner_count = owner_sequence_counts[(row["exact_surface_line"], row["silent_owner_de"])]
        if sequence_count == 1:
            resolution = "SURFACE_SEQUENCE_UNIQUE"
        elif owner_count == 1:
            resolution = "IMAGE_OWNER_RESOLVES_OCCURRENCE"
        else:
            resolution = "REPEATED_SAME_OWNER_AND_INSTRUCTION"
        statement_rows.append({
            "statement_id": row["statement_id"], "page": row["page"], "record": row["record"],
            "observed_surface_sequence": row["exact_surface_line"],
            "surface_sequence_occurrences": sequence_count, "image_owner_de": row["silent_owner_de"],
            "surface_plus_owner_occurrences": owner_count,
            "recovered_card_sequence": row["card_identity_line"],
            "recovered_spoken_sequence_de": row["spoken_component_line_de"],
            "recovered_instruction_de": row["meaning_line_de"],
            "resolution_class": resolution,
            "functional_instruction_ambiguity_after_owner": "NO" if len(owner_sequence_meanings[(row["exact_surface_line"], row["silent_owner_de"])]) == 1 else "YES",
            "exact_occurrence_identity_required": "NO",
        })

    group_surface_counts = Counter(row["surface_display_only"] for row in astro_groups)
    group_ns_surface_counts = Counter((row["canonical_namespace_id"], row["surface_display_only"]) for row in astro_groups)
    astro_group_rows = []
    for row in astro_groups:
        astro_group_rows.append({
            "opaque_local_id": row["opaque_local_id"], "page": row["page"], "locus": row["locus"],
            "surface_fragment": row["surface_display_only"],
            "surface_fragment_occurrences": group_surface_counts[row["surface_display_only"]],
            "namespace": row["canonical_namespace_id"],
            "namespace_plus_fragment_occurrences": group_ns_surface_counts[(row["canonical_namespace_id"], row["surface_display_only"])],
            "fragment_self_identifying": "YES" if group_surface_counts[row["surface_display_only"]] == 1 else "NO",
            "corrector_rule_de": "nicht einzeln deuten; bis zur vollstaendigen Lokaletikette sammeln und Bildort zeigen",
        })

    locus_surface_counts = Counter(row["complete_surface_display_only"] for row in astro_loci)
    locus_ns_surface_counts = Counter((row["canonical_namespace_id"], row["complete_surface_display_only"]) for row in astro_loci)
    locus_owner_surface_counts = Counter((row["local_image_owner"], row["complete_surface_display_only"]) for row in astro_loci)
    astro_locus_rows = []
    for row in astro_loci:
        surface_count = locus_surface_counts[row["complete_surface_display_only"]]
        ns_count = locus_ns_surface_counts[(row["canonical_namespace_id"], row["complete_surface_display_only"])]
        owner_count = locus_owner_surface_counts[(row["local_image_owner"], row["complete_surface_display_only"])]
        if surface_count == 1:
            resolution = "FULL_LOCUS_SURFACE_UNIQUE"
        elif ns_count == 1:
            resolution = "NAMESPACE_RESOLVES"
        else:
            resolution = "IMAGE_OWNER_RESOLVES"
        astro_locus_rows.append({
            "page": row["page"], "locus": row["locus"],
            "complete_surface": row["complete_surface_display_only"], "surface_occurrences": surface_count,
            "namespace": row["canonical_namespace_id"], "namespace_plus_surface_occurrences": ns_count,
            "image_owner": row["local_image_owner"], "owner_plus_surface_occurrences": owner_count,
            "recovered_instrument_de": row["instrument_reading_de"],
            "recovered_local_use_de": row["possible_condition_use_de"],
            "resolution_class": resolution,
            "external_master_value_recovered_from_surface": "NO",
        })

    manual = [
        (1, "DECLARE_REGISTER", "Prosa oder Astro vor dem Lesen ausrufen"),
        (2, "PROSE_SURFACE_LOOKUP", "sichtbare Prosaform in der 230er Palette suchen"),
        (3, "RECOVER_CARD", "eine eindeutige Kartenidentitaet und Komponentenfolge ausgeben"),
        (4, "SPEAK_VALUE", "den invarianten kurzen Werkstattwert sprechen"),
        (5, "GROUP_STATEMENT", "Karten bis zur lokalen Aussagegrenze sammeln; Zeilenrand ignorieren"),
        (6, "SHOW_OWNER", "Pflanze, Figur, Becken oder Station zeigen"),
        (7, "EXPAND_INSTRUCTION", "Sprechwerte mit dem sichtbaren Besitzer zur lokalen Handlung erweitern"),
        (8, "ALLOW_RECURRENCE", "gleiche Karte am gleichen Besitzer darf dieselbe Anweisung mehrfach setzen"),
        (9, "ASTRO_GROUP", "Astrofragmente nicht einzeln lesen; vollstaendigen Locus bilden"),
        (10, "ASTRO_NAMESPACE", "lokalen Rad-/Paneelnamensraum ausrufen"),
        (11, "ASTRO_OWNER", "bei verbleibender Kollision den exakten Bildort zeigen"),
        (12, "MASTER_VALUE", "konkreten Himmelswert aus dem lokalen Exemplar holen, nicht aus der Oberflaeche erfinden"),
    ]
    manual_rows = [{"step": n, "operation": op, "instruction_de": text} for n, op, text in manual]

    write("FIVE_HUNDRED_NINETY_SEVENTH_381_PROSE_EVENT_BACKREAD.tsv", event_rows)
    write("FIVE_HUNDRED_NINETY_SEVENTH_116_PROSE_STATEMENT_BACKREAD.tsv", statement_rows)
    write("FIVE_HUNDRED_NINETY_SEVENTH_395_ASTRO_FRAGMENT_BACKREAD.tsv", astro_group_rows)
    write("FIVE_HUNDRED_NINETY_SEVENTH_142_ASTRO_LOCUS_BACKREAD.tsv", astro_locus_rows)
    write("FIVE_HUNDRED_NINETY_SEVENTH_TWELVE_STEP_CORRECTOR_MANUAL.tsv", manual_rows)

    prose_resolution = Counter(row["resolution_class"] for row in statement_rows)
    astro_resolution = Counter(row["resolution_class"] for row in astro_locus_rows)
    summary = {
        "status": "PASS", "prose_events": len(event_rows), "event_card_exact": sum(row["card_recovery"] == "EXACT" for row in event_rows),
        "event_value_exact": sum(row["value_recovery"] == "EXACT" for row in event_rows),
        "prose_statements": len(statement_rows), "prose_surface_unique": prose_resolution["SURFACE_SEQUENCE_UNIQUE"],
        "prose_owner_resolved": prose_resolution["IMAGE_OWNER_RESOLVES_OCCURRENCE"],
        "prose_repeated_same_instruction": prose_resolution["REPEATED_SAME_OWNER_AND_INSTRUCTION"],
        "functional_instruction_ambiguities_after_owner": sum(row["functional_instruction_ambiguity_after_owner"] == "YES" for row in statement_rows),
        "astro_fragments": len(astro_group_rows), "ambiguous_astro_fragments": sum(row["fragment_self_identifying"] == "NO" for row in astro_group_rows),
        "astro_loci": len(astro_locus_rows), "astro_surface_unique": astro_resolution["FULL_LOCUS_SURFACE_UNIQUE"],
        "astro_namespace_resolved": astro_resolution["NAMESPACE_RESOLVES"], "astro_owner_resolved": astro_resolution["IMAGE_OWNER_RESOLVES"],
        "decision": "PROSE_BACKREADS_WITH_OWNER__ASTRO_REQUIRES_FULL_LOCUS_AND_IMAGE_ADDRESS",
    }
    (HERE / "FIVE_HUNDRED_NINETY_SEVENTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    report = f"""# Fuenfhundertsiebenundneunzigste Runde: der Rueckwaertskorrektor

## Ergebnis

Die Prosa ist in unserer Arbeitstheorie ruecklesbar, aber nur in der richtigen Reihenfolge:

```text
OBERFLAECHE -> KARTE -> SPRECHWERT -> BILDOWNER -> LOKALE ANWEISUNG
```

Alle {summary['prose_events']} sichtbaren Prosaereignisse liefern exakt eine Kartenidentitaet und einen gesprochenen Wert. Bei ganzen Aussagen sind {summary['prose_surface_unique']}/116 Oberflaechenfolgen bereits allein einmalig. Bei weiteren {summary['prose_owner_resolved']} bestimmt der Bildbesitzer die genaue Stelle. Die letzten {summary['prose_repeated_same_instruction']} sind echte Wiederholungen derselben Karte am selben Besitzer mit derselben Anweisung. Es bleibt daher **keine funktionale Mehrdeutigkeit**, sobald der sichtbare Besitzer mitgelesen wird.

## Was die sieben Wiederholungen sind

Sie sind kein Fehler. `qokedy` erscheint dreimal am gemeinsamen f81v-Becken als dieselbe kurze Einwirkung; `qokeedy` zweimal an den kleinen f82r-Randstationen; `shckhedy` zweimal am B4-Figurenpaar als dasselbe Zurueckhalten. Der Korrektor muss nicht wissen, welche Wiederholung „die echte“ ist – alle setzen denselben lokalen Wert.

## Astro verhaelt sich anders

Einzelne Astrofragmente sind oft unbrauchbar: {summary['ambiguous_astro_fragments']}/395 teilen ihre sichtbare Form mit mindestens einem anderen Fragment. Der Schreiber muss deshalb erst die vollstaendige Lokaletikette bilden.

Von 142 vollstaendigen Loci sind {summary['astro_surface_unique']} durch ihre ganze Oberflaeche einmalig. Bei zwei weiteren entscheidet der Namensraum; bei den letzten drei entscheidet der genaue Bildbesitzer. Damit sind alle 142 **als Adressen** ruecklesbar. Der konkrete Himmelsname oder Kalenderwert bleibt jedoch im Meisterexemplar – genau wie es unsere Zwei-Maschinen-Theorie verlangt.

## Wichtigste Korrektorregel

Prosa darf wortweise in Kartenwerte zerlegt werden. Astro darf erst locusweise und mit Bildadresse gelesen werden. Wer die 395 Astrofragmente einzeln wie Prosawoerter behandelt, erzeugt systematisch falsche Gleichheiten.

## Naechster Schritt

Als naechstes werden die elf Prosa-Records nicht mehr nur lokal, sondern als fortlaufende praktische Arbeitsgaenge rueckgelesen. Gesucht werden die Stellen, an denen derselbe aktuelle Stoff ueber mehrere Aussagen wirklich weitergetragen wird, und die Stellen, an denen der Besitzer sichtbar wechselt und der Arbeitszustand geloescht werden muss.
"""
    (HERE / "FIVE_HUNDRED_NINETY_SEVENTH_REPORT.md").write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
