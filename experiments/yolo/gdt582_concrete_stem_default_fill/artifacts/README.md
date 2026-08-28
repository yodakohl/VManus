# Artifacts

- `gdt582_42_core_stem_defaults.tsv`: das vollständige produktive
  Arbeitswörterbuch der GDT581-`slot_value`-Analyseklassen mit kurzem
  invariantem Kern und Occurrencezahlen; keine Bestätigung von 42 sprachlichen
  Wortstämmen.
- `gdt582_181_register_realization_cells.tsv`: jede tatsächlich belegte
  Analyseklasse×Register-Ausformulierung; nicht belegte Zellen werden nicht
  erfunden.
- `gdt582_80_learned_name_defaults.tsv`: alle ownerbestimmten
  `content_class × raw_name_core`-Karten, darunter die austauschbare
  Stoff-/Pflanzenpalette.
- `gdt582_13702_content_slot_defaults.tsv`: jeder offene GDT581-Inhaltsslot mit
  produktivem oder gelerntem Default.
- `gdt582_2187_control_slot_defaults.tsv`: die getrennten reinen
  Steuerungsslots; diese erhalten niemals eine Stoffbedeutung.
- `gdt582_15889_complete_default_ledger.tsv`: vollständige Vereinigung beider
  Partitionen, jeweils mit unveränderter Slot- und Hostidentität.
- `gdt582_4026_alias_default_resolutions.tsv`: geerbte Werte auf dieselbe
  Analyseklasse×Register-Karte aufgelöst; keine neuen geschriebenen Slots.
- `gdt582_5122_concrete_event_edition.tsv`: vollständige Ereignisausgabe mit
  exakter Slottrace, konkreter Klausel und unverändertem GDT581-Rückkanal.
- `gdt582_793_concrete_statement_edition.tsv`: alle festen Aussagen, nur aus
  ihren unveränderten Event-ID-Folgen zusammengesetzt.
- `gdt582_744_concrete_local_card_edition.tsv`: die komplette getrennte lokale
  Kartenebene samt Owner, Locus, Komponenten- und Namensdefaults.
- `gdt582_30_page_concrete_profiles.tsv`: Seitenweise Vollständigkeitsbilanz.
- `gdt582_25_event_sense_checks.tsv`: fünf vollständige Ereignisse je Register.
- `gdt582_20_complete_passage_sense_checks.tsv`: vier vollständige Aussagen je
  Register, alte Strukturstimme und neue Arbeitslesung nebeneinander.
- `gdt582_4_candidate_pack_scorecard.tsv`: Registerhybrid, universelles
  Apothekerpack, universelles Tabellenpack und Oberflächenlern-Rivale. Nur der
  Hybrid ist vollständig gerendert; die drei Rivalen tragen heuristische
  Domänenkosten beziehungsweise Wörterbuchgrößen.
- `GDT582_CONCRETE_DEFAULT_THIRTY_PAGE_EDITION.md`: lesbare Gesamtausgabe aller
  5.122 Ereignisse und 744 lokalen Karten.
- `GDT582_MANUAL_SENSE_AUDIT.md`: unabhängiger manueller Audit der 20
  Aussagen-, 25 Ereignis- und aller lokalen Namenskarten; keine materielle
  Korrektur, aber explizite verbleibende Wahrheitsgrenze.
- `gdt582_result.json`: kompakte Ergebnis-, Count- und Inputhash-Bilanz.
- `gdt582_validation.json`: unabhängiges Validierungsergebnis für Projektion,
  Counts, Schlüssel, Traces, Komposition und Nichtleerheit; es bestätigt nicht
  die historische oder semantische Richtigkeit der 42/181/80 Hauswerte.

Die drei größeren Slot-/Ereignistabellen werden trotz der normalen
5-MB-Grenze behalten, weil sie den reproduzierbaren Beleg für „ein nichtleerer
Default pro exakter GDT581-Occurrence“ bilden. Die kleineren Partitionen,
Wörterbücher und Prüfdecks erlauben gezielte Nutzung ohne Laden der
Gesamttabelle.
