# V65 R4 — Korrektorische Biological-Zweitausgabe

Status: vollständige kreative Defaultlesung für die sechs erlaubten
Biological-Records; keine Entzifferung.

## Urteil

Die 115 Felder lesen sich am konsistentesten als **kurze Betriebszellen eines
therapeutischen Bad-/Irrigationsregisters, dessen Apparateschicht real und nicht
nur Bildmetapher ist**. Figuren lizenzieren Bad, Waschung oder lokale Anwendung
als bevorzugte Exemplarfüllung. Becken, Leitungen, Filter, Einläufe und
menschenfreie Ausläufe lizenzieren zugleich einen vollständigen technischen
Rivalen.

Die sechs Recordprozesse sind:

1. gemeinsamer Grundkreislauf: beschicken, portionieren, verbinden,
   temperieren, mischen, ruhen, prüfen, nachfüllen, weiterleiten;
2. einzelne Badestation: dosieren, erwärmen, zwischen Zugängen führen,
   filtrieren, auffangen, anwenden oder prüfen, Varianten spülen/ablassen;
3. langer Irrigations-/Rücklaufzyklus: setzen, abziehen, warm nachspeisen,
   verteilen, unten fangen, klären, rückführen, Teilstrecken reinigen;
4. warmer Nachgang: spülen, Anteil wählen, filtrieren, warm gebrauchen,
   Gefäß und Lauf reinigen, ablassen, neu beschicken;
5. kurzer Übergabenachtrag: Teilcharge ziehen, einmal temperieren, halten, mit
   recordlokalem Vorposten verknüpfen und weitergeben;
6. offener Kaltgang: Bestand ohne Erhitzen fortführen, dosieren, einfach
   filtrieren und zum Zielslot bringen.

## Was V65 gegenüber V54 verbessert

- Alle 281 Ereignisse erhalten eine konkrete Lesung, aber jede Zeile nennt
  zugleich ihre Schicht: exakte Kartenhilfe, formale Slotexpansion oder lokales
  Exemplar.
- Die 97 V61-Aussagen ersetzen Zeilen als Prozesseinheiten. Besonders lange
  f83r-Sequenzen sind Phasen und Varianten, keine Liste von 38 Beschwerden.
- `VORIGES?` ist stets recordlokal. Ein sichtbarer Nachbarrecord darf keine
  unsichtbare Charge liefern.
- `SPÜLEN?` und `ABLASSEN?` bleiben an ihren 16 terminalen Vorkommen
  schlusskonfundiert; der Prozessgraph benutzt sie, ohne daraus freie Wörter zu
  machen.
- Der technische Apparateablauf wird nicht mehr als bloße Nullhypothese
  behandelt. Er ist bei B3, B5 und B6 mindestens so glatt wie die medizinische
  Expansion.

## Harte Begrenzung

Im Bio-Slice sind 191/281 Ereignisse `UNPARSED_EXEMPLAR`. Die Felder sind
14 `UNIQUE`, 41 `AMBIGUOUS`, 60 `UNPARSED`; die Aussagen 12/35/50. Wasser,
Patient, Körperöffnung, Tuch, Temperatur, Gefäß und Krankheit stammen daher
nicht aus den Karten. Ein vollständiger deutscher Text ist hier ein
Werkstattexemplar, kein wiedergewonnener Ausgangstext.

Der technische und der medizinische Text teilen nur eine anonyme Algebra:

```text
OWNER/STATION -> ACTIVE CHARGE -> PARAMETER/LINK/TARGET
              -> STATE/CONTACT -> TRANSFER -> LOCAL CLOSE
```

Diese Algebra kann ein Bad, eine Irrigation, eine Materialprobe oder einen
Wasserwerksgang instanziieren. Kein einzelnes Voynich-Gebilde wird als WASSER,
FRAU, ROHR oder KRANKHEIT glossiert.

## Artefakte

- `V65_R4_281_EVENT_BIO_INTERLINEAR.tsv`
- `V65_R4_115_FIELD_BIO_EDITION.tsv`
- `V65_R4_97_STATEMENT_BIO_EDITION.tsv`
- `V65_R4_6_RECORD_BIO_EDITION.tsv`
- `V65_R4_PROCESS_GRAPHS.tsv`
- `V65_R4_VALIDATION.json`

Der Builder prüft 281/115/97/6, die ausgewählten V63-Statussummen, die
Recordgrößen, vollständige Defaulttexte und den Ausschluss versiegelter Seiten.
