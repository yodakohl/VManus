# GDT599-Artefakte

## Vollständige Editionen

- `GDT599_COMPLETE_OBJECT_READER.md`: alle 313 Aussagen als deutscher
  Arbeitsleser, danach der getrennte lokale Kartenanhang.
- `gdt599_313_complete_statements.tsv`: Aussagen, Absatzgrenzen und
  Vollständigkeitsstatus.
- `gdt599_1443_complete_action_edition.tsv`: jeder Aktionsslot mit Quelle,
  Objekt und Endklausel.
- `gdt599_2272_complete_host_edition.tsv`: vollständiger Hoststrom; die
  GDT598-Quellklausel bleibt als unveränderte Provenienzspalte erhalten.
- `gdt599_793_remaining_action_object_replay.tsv`: die exakt neu ergänzte
  Population mit Auswahlweg, Referenzmodus und Zustandsfortschreibung.

Die großen Volltabellen sind nötig, weil Summen weder die 1.443 exakten
Aktionsslot-Joins noch die Reihenfolge von 2.272 Hosts, die Absatzgrenzen und
die 313 zusammengesetzten Aussagen reproduzieren können.

## Regeln und Entscheidungen

- `gdt599_8_selection_route_cards.tsv`: vollständige Auswahlhierarchie.
- `gdt599_3_reference_scope_cards.tsv`: links-anaphorische, rechts-bestimmte
  und lokale/defaultierte Referenzformen.
- `gdt599_6_root_default_cards.tsv`: kurze ersetzbare Rootdefaults.
- `gdt599_6_compatibility_cards.tsv`: zulässige Objektklassen je Zielroot.
- `gdt599_46_aiin_quantity_bindings.tsv`: AIIN-Mengenhüllen und ihre
  Substratquellen.
- `gdt599_24_action_q_result_transitions.tsv`: Eingang und resultierender
  Stationsansatz jedes aktionsgebundenen Q.
- `gdt599_11_manual_workshop_decisions.tsv`: elf lokale Objektkorrekturen.
- `gdt599_3_override_propagation_effects.tsv`: die drei echten
  Folgewirkungen dieser Korrekturen.
- `gdt599_3_manual_clause_polish.tsv`: reine deutsche Klauselglättungen ohne
  Bedeutungswechsel.

## Kontrolle und Passthrough

- `gdt599_projection_review_queue.tsv`: 125 gezielt weiter zu prüfende
  Projektionen.
- `gdt599_6_page_profiles.tsv`: Populationen und Profile je Seite.
- `gdt599_40_local_card_passthrough.tsv`: strikt getrennter lokaler Anhang.
- `gdt599_40_inherited_manual_reviews.tsv`: unveränderte, namespacete
  GDT596/GDT597-Reviews.
- `gdt599_result.json`: kompaktes Gesamtergebnis und Input-Hashes.
- `gdt599_validation.json`: 103 bestandene deterministische Prüfungen.
