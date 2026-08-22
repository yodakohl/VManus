# V69 R4 — kanonische zweite Zehnseitenedition

Status: vollständige kreative Arbeitstheorie; **keine Entzifferung**.

## Endmodell

```text
DOMAIN_NEUTRAL_EXEMPLAR_CARD_REGISTER

gewöhnliche Fachquelle
  -> Bild-/Registerellipse
  -> 4 recordlokale Register
  -> 14 exakte Control-Karten
  -> 159 lokale opake Prosa-Ganzkartentypen
  -> Felder, Reflow, Renderer

Astro: drei getrennte seitenlokale Diagrammnamespaces
```

Dieses Modell ist für eine kleine Werkstatt um 1420 lehrbar, sofern
Masterexemplar, Codeblatt und Rendererbeispiele vorhanden sind. Es ist nicht
selbstbeschreibend: Die formale Seite kann mit den Hilfsmitteln 776/776
reproduziert werden; die vollständige konkrete Quellintention ist ohne
Masterexemplar 0/776 rücklesbar.

## Kanonisches Wörterbuch

Von 173 exakten Prosa-Kartentypen besitzen 14 eine wiederverwendbare
Control-Rolle. Elf tragen die kreativen kurzen Mnemonics:

```text
MASS?  ANWENDEN?  BEREIT?  ANSATZ?  ZIEL?  KLAR?
VORIGES?  ANTEIL?  TEMPERIEREN?  SPÜLEN?  ABLASSEN?
```

Vier exakte Karten tragen formale Prompts, wobei eine mit `MASS?` überlappt:

```text
VORGABEPARAMETER?
STANDARDSLOT_SETZEN
LOKALEN_RELATIONSSLOT_SETZEN
AKTIVEN_ARBEITSSTAND_VERKNÜPFEN
```

Die übrigen 159 Kartentypen sind `UNKNOWN_EXEMPLAR_WHOLE_CARD`. Die 14
Control-Karten erkennen 119/381 Prosaereignisse; 262 Ereignisse bleiben lokale
Exemplarkarten. Kein Kartenstück, PAGE_HOST, sichtbarer Stamm oder Wrapper
erhält einen Inhaltswert.

## Syntax und Speicher

116 Quellenstatements laufen über 135 Felder und 57 physische Loci. Die Felder
sind 14 `UNIQUE`, 56 `AMBIGUOUS`, 65 `UNPARSED`; die Aussagen 12/49/55.
Physische Zeilen sind Reflow. Vier Register — OWNER, ACTIVE, TARGET, PREVIOUS —
resetten an jedem Record und sind für die gewählte Edition minimal. `CLOSE`
beendet ein Feld, nicht notwendig einen Satz.

## Zwei gleichrangige Inhaltseditionen

V68 hat den früheren medizinischen Vorsprung aufgehoben. V69 publiziert deshalb
beide Volltexte:

### Iatromedizinische Lesefassung

- Herbal: fünf bebilderte Simple-Artikel mit Wurzel-, Blüten-, Blatt- und
  Feuchtkrautbereitungen;
- Biological: therapeutische Bad-/Wascharbeit mit realer Becken-, Filter-,
  Leitungs- und Auslassbedienung;
- Astro: 7×12 medizinischer Wahlrahmen, 28 Mondstationsadressen und unabhängige
  28er Wahlregeln.

### Praktisch-technische Lesefassung

- Herbal: Pflanzenrohstoffe, Auszüge, Materialproben und Vorräte;
- Biological: Badehaus-/Waschhausbecken, Filter, Leitungen, Rücklauf und
  Wartung;
- Astro: generischer Arbeits-, Termin- und Stationsplan.

Das sind `SIMPLE/BATH/ELECTION` und `MATERIAL/PROCESS/SCHEDULE`. Keine Fassung
ist robust Sieger; beide benutzen dieselbe formale Maschine.

## Astro-Grenze

f67r2 bleibt ein 7×12-Selektor, f68r1 ein Zentrum-plus-28-Raumkatalog und f69v
eine unabhängige 28er-Regelfolge. Es gibt keinen sichtbaren f68↔f69-Schlüssel,
keine lizenzierte Orientierung und keinen Prosa-Kartenimport. Alle 395 Gruppen
sind lokale Diagrammfragmente, keine gelesenen Wörter.

## Was die zehn Runden verbessert haben

- phrase-lange „Wortbedeutungen“ wurden auf elf kurze Mnemonics reduziert;
- Zeile, Feld, Statement und Record wurden getrennt;
- Ellipse wurde als vier recordlokale Speicherregister ausführbar;
- ein begrenzter Slotparser ersetzte freie Satzfantasie;
- Herbal, Bio und Astro erhielten vollständige, getrennt geschichtete Texte;
- ein konkreter Werkstattcompiler erklärte Mehrhändigkeit ohne Lautchiffre;
- der vollständige technische Rivale entfernte den medizinischen
  Bestätigungsbias.

## Harte Deutungsgrenze

Die Ausgabe enthält **null bestätigte Lexeme, null bestätigte Klartextklauseln,
null Lautwerte und null Sprachidentifikation**. Sie ist die derzeit
kohärenteste vollständige Schreibersimulation für diese zehn Seiten. Ihr Wert
liegt in konkreten, gegeneinander testbaren Volltexten und einem einfachen
Werkstattmechanismus — nicht in behaupteter Übersetzung.

## Release

- `V69_R4_FINAL_173_CARD_DICTIONARY.tsv`
- `V69_R4_FINAL_381_PROSE_EVENT_INTERLINEAR.tsv`
- `V69_R4_FINAL_135_FIELD_EDITION.tsv`
- `V69_R4_FINAL_116_STATEMENT_EDITION.tsv`
- `V69_R4_FINAL_395_ASTRO_GROUPS.tsv`
- `V69_R4_FINAL_776_GROUP_LEDGER.tsv`
- `V69_R4_FINAL_14_UNIT_DUAL_TRANSLATION.tsv`
- `V69_R4_READABLE_DUAL_TEN_PAGE_EDITION.md`
- `V69_R4_FINAL_9_LESSON_WORKSHOP_MANUAL.tsv`
- `V69_R4_VALIDATION.json`
- `V69_R4_INDEPENDENT_VALIDATION.json`
- `validate_v69_r4_final_second_edition.py`

V69 ist der vereinbarte Endpunkt. Es wird kein V70 automatisch begonnen.
