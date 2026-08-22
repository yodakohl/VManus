# V69 R3 — kanonische technische Doppelausgabe

## Ergebnis

Die V60–V68-Auswahl ist als deterministische, gezählte und gehashte Endausgabe konsolidiert. Die formale Karten-/Registermaschine bleibt vom lokalen Inhalt getrennt. Iatromedizinische und praktische Werkstattlektüre stehen vollständig nebeneinander; `domain_selection=NONE` und kein semantischer Sieger wird gewählt.

Der wissenschaftliche Grenzwert bleibt streng: **0/776 Gruppen erlauben vollständige Quellrekonstruktion ohne externes Exemplar**. Die Ausgabe bestätigt kein Voynich-Lexem, keine PAGE_HOST-Bedeutung und keine Komponentenvererbung.

## Schichtenvertrag

1. `exact_joint_card_id` beziehungsweise Astro-Seitenadresse ist die opake Identität.
2. Formel, formaler Wert, CLOSE/OPEN, Feldoperation, Registerübergang und Reflow sind die reversible formale Schicht.
3. Nur die elf in V60 ausgewählten exakten Ganzkarten erhalten ein globales Arbeitsmerkwort; alle übrigen Enden heißen ausdrücklich `UNKNOWN_EXEMPLAR`.
4. Vier ausgewählte strikte Konstruktionen bleiben formale Prompts und werden nicht zu Wortbedeutungen. Der Sonderfall `DAIIN` bleibt ausdrücklich `SURFACE_DAIIN_ONLY:VORGABEPARAMETER?`; er wird nicht auf AIIN/CHAIIN/SAIIN/TAIIN derselben opaken Karten-ID vererbt.
5. Parser, vier recordlokale Register und Zeilenreflow liefern die ausführbare Struktur.
6. Iatromedizinischer und praktischer Text sind zwei gleichrangige, lokale Exemplarausfüllungen. Sie sind keine Kartenwerte.
7. Astrogruppen sind ausschließlich seitenlokal; sie übernehmen keine Prosa-Tuples oder -Prompts.

## Vollständigkeitsaudit

| Ebene | Ergebnis |
|---|---:|
| exakte Prosa-Kartentypen | 173 |
| Prosa-Ereignisse | 381 |
| Felder | 135 |
| Statements | 116 |
| Astrogruppen / Astro-Loci | 395 / 142 |
| vereinheitlichte Ledgerzeilen | 776 = 381 + 395 |
| vollständige Einheiten | 14 = 5 Herbal + 6 Bio + 3 Astro |
| Compilerübergänge | 22 |
| geprüfte Invarianten | 37/37 PASS |

Die Merkwortschicht umfasst 11/173 Kartentypen und 85/381 Prosa-Ereignisse. Die formale Promptschicht umfasst 4/173 Typen und 45/381 Ereignisse; wegen einer Überschneidung beträgt die Vereinigungsmenge 14 Typen beziehungsweise 119 Ereignisse. Damit bleiben 162 Typen/296 Ereignisse ohne Merkwort und 159 Typen/262 Ereignisse vollständig im `EXEMPLAR_ONLY`-Kanal.

Von 135 Feldern sind 90 terminal und 45 offen; der feste Parser liefert 14 eindeutige, 56 mehrdeutige und 65 ungeklärte Felder. Von 116 Statements sind 12 eindeutig, 49 mehrdeutig und 55 ungeklärt. Alle elf Prosa-Records setzen `OWNER`, `ACTIVE_ITEM/PREPARATION`, `TARGET/STATION` und `PREVIOUS_ITEM` am Anfang auf `UNSET`. Alle 116 Übergänge sind aus dem vollständigen Übergangslog rückwärts rekonstruierbar, aber nur 47 aus dem Endzustand allein.

Die 46 physischen Zeilengrenzen bleiben von Satzgrenzen getrennt (`CONTINUE=19`, `RESET=8`, `PARALLEL=10`, `SECTION=8`, `UNRESOLVED=1`); 18 Statements überspannen mehrere physische Zeilen. Damit ist Zeile ausdrücklich nicht Satz.

Astro enthält 190 Gruppen/74 Loci auf f67r2, 65/37 auf f68r1 und 140/31 auf f69v. f68 und f69 besitzen weder gleichindexige noch beliebige Vollformtreffer (`0/0`) und werden nicht direkt verbunden. Startpunkt, Drehrichtung und Orientierung bleiben undeutete Editionsparameter.

## Compiler und Rückweg

Der 22-stufige Werkstattcompiler führt typisierte Quellklauseln über recordlokale Register zu exakter Karte oder formalem Prompt, Feldabschluss, Zeilenreflow und Renderer. Der Decoder rekonstruiert die formale Spur für 776/776 Gruppen. Lokale Besitzer, Stoffe, Körperteile, Geräte, Zwecke und Handlungen kommen jedoch aus dem gefrorenen Exemplar: ohne dieses Exemplar ist die vollständige Quellintention 0/776 rekonstruierbar. Mit bereitgestelltem Exemplar enthält das Ledger für jede Gruppe beide vollständigen lokalen Ausgaben; das ist Lookup, kein entzifferter Klartext.

Herbal wird daher parallel als iatromedizinisches Simple und als Pflanzen-/Materialcharge ausgegeben, Bio als Badeanwendung und als Becken-/Leitungsbetrieb, Astro als medizinische Wahltafel und als generischer Arbeitsplan. Abschnittsinterne Kosten bleiben dokumentiert, werden wegen verschiedener Rubriken aber nicht zu einem globalen Sieger addiert.

## Reproduzierbarkeit und Artefakte

- `V69_R3_BUILD_CANONICAL_DUAL_RELEASE.py` baut alle Tabellen byte-deterministisch aus 27 eingefrorenen, SHA-256-geprüften V60–V68-Quellen.
- `V69_R3_VALIDATE_CANONICAL_DUAL_RELEASE.py` prüft Counts, disjunkte Schichten, Eventpartitionen, Resets, Reflow, Rückwärtslauf, Astro-Namensräume, f68/f69-Trennung, Quellenhashes, zehn Releasehashes und einen identischen Neubau.
- `V69_R3_SOURCE_MANIFEST.tsv` enthält die 27 Quellhashes; `V69_R3_RELEASE_MANIFEST.tsv` enthält zehn kanonische Tabellenhashes.
- `V69_R3_173_CARD_DICTIONARY.tsv`, `V69_R3_381_PROSE_EVENT_LEDGER.tsv`, `V69_R3_135_FIELD_LEDGER.tsv`, `V69_R3_116_STATEMENT_LEDGER.tsv`, `V69_R3_395_ASTRO_GROUP_LEDGER.tsv`, `V69_R3_776_UNIFIED_DUAL_LEDGER.tsv`, `V69_R3_14_UNIT_DUAL_EDITION.tsv` und `V69_R3_22_COMPILER_TRANSITIONS.tsv` sind die eigentliche Ausgabe.

Validatorstatus: `PASS`; deterministischer Neubau: `PASS`; Quellhashes: 27/27; Releasehashes: 10/10; bestätigte Lexeme: 0; gewählter Domänensieger: `NONE`. Dies ist die terminale R3-Ausgabe; sie eröffnet keine V70-Route.
