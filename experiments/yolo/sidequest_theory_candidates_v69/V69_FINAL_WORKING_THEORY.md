# V69 — finale Auswahl der zweiten Zehnrundenserie

Status: **vollständige kreative Arbeitstheorie, keine Entzifferung**.

## Vierrollenentscheidung

Alle vier Perspektiven enden unabhängig bei derselben Architektur und
derselben Deutungsgrenze:

| Rolle | stärkster Beitrag | Ergebnis |
|---|---|---|
| R1 Werkstattlehrmeister | vollständige kanonische Ausgabe, Handbuch und 40 Validierungsgates | exemplarabhängiges Ganzkarten-/Registersystem |
| R2 historischer Fachschreiber | historische Quellenbindung und komplette lesbare Doppelausgabe | iatromedizinisch redaktionell zuerst, nicht evidentiell bevorzugt |
| R3 technischer Notator | 27 Quellhashes, 10 Releasehashes, 22 Compilerübergänge und deterministischer Neubau | formale Maschine stabil, Domänensieger `NONE` |
| R4 Kanzleikorrektor | unabhängige Zusammenführung beider Inhaltseditionen und Kontextkompaktierung | beide Inhaltswelten ausdrücklich gleichrangig |

Die Auswahl lautet:

`DOMAIN_NEUTRAL_EXEMPLAR_CARD_REGISTER_WITH_COEQUAL_CONTENT_EDITIONS`

## Kanonische Arbeitsannahme

Eine kleine Werkstatt um 1420 arbeitet mit einem Masterexemplar und einem
gelernten Ganzkartendeck. Eine gewöhnliche, heute unbekannte Fachquelle wird
durch Bild und Register elliptisch verkürzt. Vier recordlokale Speicherplätze
(`OWNER`, `ACTIVE`, `TARGET`, `PREVIOUS`) tragen ausgelassene Argumente. Danach
setzt der Schreiber entweder eine der 14 wiederverwendbaren Control-Karten oder
eine der 159 lokalen Exemplarkarten, schließt gegebenenfalls das Feld und passt
die Darstellung an Hand, Register und verfügbaren Bildraum an.

Das ist einfach genug, um es durch Vormachen, Abschreiben und Korrektur zu
lernen. Es ist ohne Masterexemplar absichtlich nicht selbstentschlüsselnd.

## Gefrorener Bestand

- 10 Seiten und 14 vollständige Einheiten;
- 173 exakte opake Prosa-Kartentypen und 381 Vorkommen;
- 11 kurze kreative Mnemonics und 4 Formalcontrols auf 14 verschiedenen IDs;
- 119/381 durch den begrenzten Parser erreichte Ereignisse;
- 262/381 `EXEMPLAR_ONLY`;
- 135 Felder und 116 rekonstruierte Quellaussagen;
- 395 seitenlokale Astrogruppen;
- 776/776 Gruppen in beiden Volltextspalten;
- 0/776 vollständige Quellintention ohne Masterexemplar.

## Kleinstes Wörterbuch

Die elf mnemonischen Ganzkarten heißen mit bewusstem Fragezeichen:

`MASS?`, `ANWENDEN?`, `BEREIT?`, `ANSATZ?`, `ZIEL?`, `KLAR?`, `VORIGES?`,
`ANTEIL?`, `TEMPERIEREN?`, `SPÜLEN?`, `ABLASSEN?`.

Das sind keine sichtbaren Stämme und keine deutschen Wortübersetzungen. Vor
allem bedeutet `KLAR?` nur einen möglichen Endzustand; die frühere lange Glosse
„bis die Flüssigkeit klar abläuft“ ist eine lokale Satzerweiterung, keine
Wortbedeutung. `ey`, `ch`, `chy`, `cho`, PAGE_HOST, Wrapper und Teilstrings
bleiben ohne Inhaltswert.

Vier zusätzliche formale Prompts sind
`VORGABEPARAMETER?`, `STANDARDSLOT_SETZEN`,
`LOKALEN_RELATIONSSLOT_SETZEN` und
`AKTIVEN_ARBEITSSTAND_VERKNÜPFEN`; einer überlappt mit `MASS?`.

## Gleichrangige Volltexte

Die iatromedizinische Fassung liest die zehn Seiten als
`SIMPLE / BATH / ELECTION`: bebilderte Simples, therapeutische Bade- und
Waschprozesse sowie drei medizinisch-astrologische Lookup-Instrumente.

Die praktisch-technische Fassung liest sie als
`MATERIAL / PROCESS / SCHEDULE`: Pflanzenrohstoffartikel,
Badehaus-/Waschhaus-/Wasserwerksbetrieb und einen getrennten Arbeitsplan.

V68s vier Vergleiche ergeben einen knappen praktischen Sieg, einen knappen
medizinischen Sieg und zwei substantielle Unentschieden. Deshalb wird weder
Medizin noch Technik ausgewählt. Die Architektur erklärt beide; genau das ist
zugleich ihre Stärke und ihre wichtigste ungelöste Schwäche.

## Astrogrenze

`f67r2` bleibt ein 7×12-Selektor, `f68r1` ein Zentrum-plus-28-Katalog und
`f69v` eine unabhängige 28er-Regelfolge. Start und Rotation sind ungeklärt.
Es gibt keinen f68↔f69-Schlüssel, keinen Import von Prosa-Kartenwerten und kein
gelesenes Astro-Wort.

## Was nach zehn Runden besser ist

V60–V69 haben lange Fantasieglossen auf kurze, exakte Ganzkarten-Mnemonics
zurückgeführt; Zeile, Feld und Aussage getrennt; Ellipse als recordlokalen
Speicher ausführbar gemacht; einen begrenzten statt universellen Parser gebaut;
alle Herbal-, Bio- und Astrogruppen vollständig zweispaltig gebunden; einen
historisch lehrbaren Werkstattcompiler formuliert; und durch den vollständigen
praktischen Rivalen den medizinischen Bestätigungsbias sichtbar entfernt.

## Endgrenze

Bestätigte Lexeme: **0**. Bestätigte Klartextklauseln: **0**. Identifizierte
Sprache, Lautwerte, Alphabet, Chiffre, Semantik oder direkte Übersetzung:
**keine**. Vollständigkeit bedeutet hier nur, dass beide kreativen Welten jedes
sichtbare Ereignis ohne leere Defaultstelle aufnehmen; sie beweist keine der
Welten historisch.

## Primäre Artefakte

- `V69_R1_CANONICAL_SECOND_EDITION_REPORT.md` — umfangreichste kanonische
  Maschinenedition;
- `V69_R2_FINAL_HISTORICAL_DUAL_EDITION_REPORT.md` — historische und lesbare
  Doppelbindung;
- `V69_R3_CANONICAL_DUAL_RELEASE_REPORT.md` — strengste technische
  Reproduzierbarkeitsfassung;
- `V69_R4_FINAL_SECOND_EDITION_REPORT.md` — kompakte Synthese;
- `V69_R4_READABLE_DUAL_TEN_PAGE_EDITION.md` — beide vollständigen Lesetexte;
- `V69_R4_FINAL_173_CARD_DICTIONARY.tsv` — finales kleines Kartenwörterbuch;
- `V69_R4_FINAL_776_GROUP_LEDGER.tsv` — vollständige Gruppenzuordnung;
- `V69_R1_VALIDATION.json`, `V69_R2_VALIDATION.json` und
  `V69_R4_INDEPENDENT_VALIDATION.json` — unabhängige PASS-Prüfungen.

## Stopp

Dies ist Runde V69 und damit die zehnte verlangte Verbesserung seit V60.
**Kein V70 wird automatisch begonnen.**
