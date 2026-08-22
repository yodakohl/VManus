# V69 R2 — Finale historische Doppeledition der zehn Seiten

Status: **vollständige kreative Quellenedition, keine Entzifferung**. Dies ist
der letzte Durchgang; aus R2 folgt kein V70. Verwendet wurden nur die
ausgewählten V60–V68-Schichten und die darin gebundenen Vollledgers der festen
zehn Seiten. `f84` und `f84r` wurden nicht benutzt.

## Endurteil: Inhaltsparität

V68 hat den medizinischen Inhaltsvorsprung aufgehoben. Vier unabhängige
Auswertungen ergaben je einen knappen Sieg für Medizin und Praxis sowie zwei
substanzielle Unentschieden. Deshalb publiziert V69 zwei gleichrangige
Quelltexte:

1. **iatromedizinische Lesefassung:** Simplex → Bad/Anwendung → Wahlzeit;
2. **praktisch-technische Lesefassung:** Material → Badehaus/Wasserprozess →
   Arbeitsplan.

Die medizinische Fassung steht in der Tabelle zuerst, weil der Auftrag sie als
primäre Lesefassung verlangt, **nicht weil sie bewiesen oder global besser
ist**. Beide Texte binden dieselben sichtbaren Gruppen, Karten, Felder,
Registerzustände und Loci. Das stabile Ergebnis liegt eine Stufe höher:

```text
bild- und exemplarabhängiges Werkstattregister
+ kleine domänenneutrale Ganzkarten-/Slotmaschine
+ großer lokaler, ohne Masterexemplar semantisch verlorener Rest
```

## Semantische Obergrenze

| Schicht | Endstand |
|---|---:|
| sichtbare Gruppen, formal gebunden | 776/776 |
| Prosaereignisse | 381 |
| davon V63-erkannt | 119 |
| davon `EXEMPLAR_ONLY` | 262 |
| Astrogruppen, sämtlich lokales Exemplar | 395 |
| Astro-Loci | 142 |
| bestätigte Lexeme | **0** |
| bestätigte Klartextklauseln | **0** |
| festgestellte Sprache, Lautung, Chiffre oder universelle Wortart | **keine** |

Mit Codebuch bleiben sichtbare Identität, Reihenfolge, Feld und Layout
776/776 rücklesbar. Nach der ausgewählten V67-Rekonstruktion ist die konkrete
Quellintention nur **mit** Masterexemplar 776/776 und **ohne** Masterexemplar
0/776 rücklesbar. Das ist die zentrale Schranke dieser Edition: flüssige Prosa
ist eine explizite lokale Rekonstruktion, kein Resultat atomweiser Dekodierung.

## Leseschlüssel

In `V69_R2_DUAL_FOURTEEN_UNIT_EDITION.tsv` steht jedes ungestützte Sachwort
oder jede ungestützte Operation innerhalb eines Tags:

- `[CARD:…]` — einer der elf unveränderten V60-Merkwertbegriffe;
- `[FORMAL:…]` — nichtlexikalischer Prompt;
- `[REGISTER:…]` — anonyme recordlokale Laufzeitreferenz;
- `[IMAGE:…]` / `[IMAGE_RIVAL:…]` — Bildannahme;
- `[GENRE:…]` — Ergänzung aus historischer Textgattung;
- `[EXEMPLAR:…]` / `[LOCAL_EXEMPLAR:…]` — nur im verlorenen lokalen
  Masterexemplar rekonstruierbarer Inhalt;
- `[UNKNOWN:…]` — bewusst unentschiedene Stelle.

Kein Tag außer `[CARD]` verändert das Wörterbuch; auch `[CARD]` bleibt
Fragezeichen-Mnemonic und kein bestätigtes Wort. Das vollständige knappe
Wörterbuch und die drei Quellordnungen stehen in
`V69_R2_FINAL_DICTIONARY_SOURCE_ORDER_MANUAL.tsv`. Die 173-Karten-Tabelle, das
381-Ereignisledger und die elf Entscheidungen sind in
`V69_R2_FIXED_DICTIONARY_BINDING.tsv` bytegenau per SHA-256 eingefroren.

## Vierzehn Einheiten

| Einheit | iatromedizinische Lesefassung | gleich sichtbarer praktischer Rivale | lokaler Stand |
|---|---|---|---|
| H1 | Wurzelwasser, kleine Anwendung, warmer Nachgebrauch | Seifenkraut-Waschsud | Medizin lokal stärker, Inhalt paritätisch |
| H2 | zwei Blütenfraktionen als Salbe | zwei Fraktionen als Pflanzenreiniger | Gleichstand |
| H3 | Veilchenwein und Veilchenöl | Duftwasser und Duftöl | Medizin lokal stärker, Inhalt paritätisch |
| H4 | Blattauszug, Wundwäsche, Umschlag | Waidmaische und zweiter Färbegang | Medizin lokal stärker, Inhalt paritätisch |
| H5 | Sonnentau-Hautgebrauch und Brusttrank | Turnsole-Farbtüchlein | Praxis lokal stärker, Inhalt paritätisch |
| B1 | Badeflotte und Beckenbeschickung | Badehausversorgung und Pflanzenreiniger | Gleichstand |
| B2 | Teilbad, Waschung, warmer Nachgang | gewöhnlicher Kundenbadgang | Gleichstand |
| B3 | warmer Lavagezyklus | Zisternen-, Misch- und Rücklaufplan | Praxis im Prozess stärker, Inhalt paritätisch |
| B4 | warme Haut-/Wundwäsche mit Tuch | Leinen-, Filter- und Wannenwäsche | Medizin lokal stärker, Inhalt paritätisch |
| B5 | warmer medizinischer Übergabenachtrag | Boiler-/Heißwasserübergabe | Praxis lokal stärker |
| B6 | kalter pharmazeutischer Filtergang | Kaltwasser-Bypass | Praxis lokal stärker |
| A1 | planetarisch-zodiakale medizinische Wahlzeit | allgemeiner Werkstatt-Wahlrahmen | Medizin spezifischer, Praxis billiger |
| A2 | 28 Mondhausadressen mit medizinisch-magischen Operationen | 28 allgemeine Arbeitsadressen | Gleichstand |
| A3 | 28 medizinische Wahlregeln | 28 allgemeine Arbeitsregeln | Gleichstand |

### Herbal

Die gemeinsame Quellordnung lautet Besitzer/Lemma → Pflanzenteil →
Bearbeitung/Medium → Menge/Zustand → Gebrauch → Fortsetzung. Ein illustriertes
Herbal wie Egerton MS 747 stützt Bildbesitzer plus Artikel
([British Library](https://searcharchives.bl.uk/catalog/032-001983805));
fünfzehntjahrhundertliche Farbenbücher stützen dieselbe kurze
Rohstoff-Rezeptform
([Bologna-Handbuch](https://www.hrz.hr/en/activities/publications/books-and-proceedings/secrets-of-colours-a-15th-century-handbook-on-the-preparation-of-paints/)).
Keine Quelle identifiziert jedoch eine der fünf Pflanzenbilder. H1/H3/H4
bleiben die besten medizinischen Lesungen, H5 die beste praktische, H2 ist
vollständig offen.

### Biological

Die gemeinsame Quellordnung lautet Station → aktive Charge → Parameter,
Verknüpfung oder Ziel → Zustand/Kontakt → Transfer → lokaler Schluss. Eine
mittelalterliche Badstube verband tatsächlich Hitze, Wasser, kalte Endspülung
und Personal; medizinische Nebenleistungen waren möglich
([Kuml](https://tidsskrift.dk/kuml/article/view/24661)). Mittelalterliche
Wasseranlagen kannten Quellen, Gefälle, Zisternen, Verzweigungen, Rohre,
Abflüsse und Wartung
([Magnusson](https://books.google.com/books/about/Water_Technology_in_the_Middle_Ages.html?id=3JhG-zqV9eMC)).
Darum ist „medizinisch **plus** Apparatebetrieb“ eine gute Lesefassung, aber
kein Sieger über Badehaus/Wasserwerk. B2 ist der stärkste echte Badowner;
B5/B6 sind am besten technisch.

### Astro

Die gemeinsame Quellordnung lautet externer Schlüssel → gezeichneter Locus →
ganzer lokaler Regeleintrag → Anwendung auf eine schon bekannte Aufgabe. Ein
medizinisches Faltalmanach von 1415–1420 stützt die Konsultation von
Planetenstunden und Mondort vor einem Eingriff
([Wellcome](https://wellcomecollection.org/stories/the-enigma-of-the-medieval-folding-almanac));
Michael von Rhodos verbindet 1434 Astronomie, Astrologie, Navigation,
Schiffbau und Arbeitsgedächtnis
([Projekt](https://brunelleschi.imss.fi.it/michaelofrhodes/manuscript.html)).
Beide Gattungen sind zeitnah. Alle Planet-, Zeichen-, Körper-, Mondhaus- und
Arbeitsnamen bleiben äußere Exemplarbezeichnungen. A2 und A3 haben keinen
sichtbaren Schlüssel, keinen bewiesenen Start und keine bewiesene Richtung.

## Widerspruch und Konfidenz

`V69_R2_CONTRADICTION_CONFIDENCE.tsv` gibt für jede Einheit den stärksten
positiven Befund und den stärksten Gegenbeleg beider Fassungen an. Die formale
Bindung hat Konfidenz 1,00, weil sie nur bereits veröffentlichte Serien und
Hashes prüft. Die Inhaltskonfidenzen liegen bewusst nur zwischen 0,18 und
0,40. Die wichtigsten globalen Widersprüche sind:

- kein sichtbarer Querindex verbindet Herbal, Bio und Astro;
- kein Pflanzen-, Leiden-, Körper-, Stoff-, Gefäß-, Rohr- oder Arbeitsname ist
  kartengestützt;
- 262/381 Prosaereignisse und 395/395 Astrogruppen brauchen das lokale
  Exemplar;
- `SPÜLEN?` und `ABLASSEN?` bleiben an ihren Vorkommen terminalfamilien-
  konfundiert;
- f68r1 und f69v teilen keinen exakten ganzen Eintrag und haben je 56
  gleichwertige Orientierungen;
- Bildgattung kann den plausiblen Inhalt rahmen, aber nicht die Schrift lesen.

## Historische Mechanismen

Die Werkstattform selbst ist historisch plausibel. Wellcome MS.683 zeigt eine
mehrhändige lateinische Rezeptsammlung mit formelhaften Kürzungen
([Katalog](https://wellcomecollection.org/works/w6ne7k4t)). Das valencianische
Färberhandbuch Joanot Valeros verband Färberei, Fleckenentfernung, Medizin,
Abkürzungen und Konten
([The Medieval Review](https://scholarworks.iu.edu/journals/index.php/tmr/article/view/17771)).
Eine ungefähr zeitgleiche medizinische Sammelhandschrift vereint Chirurgie,
Pflanzen, Rezepte und Zodiac Man
([BL Add MS 29301](https://searcharchives.bl.uk/catalog/032-002020783)).
Diese Vergleiche machen Abbreviation, Mischgattung und Exemplarlernen möglich;
sie belegen weder Voynich-Lautung noch das konkrete Codebuch.

## Vollständigkeit und Schluss

`V69_R2_776_BINDING.tsv` bindet lückenlos:

- H1–H5: 100 Ereignisse, 20 Felder, 19 Aussagen;
- B1–B6: 281 Ereignisse, 115 Felder, 97 Aussagen;
- A1–A3: 395 Gruppen, 142 Loci;
- zusammen: **14 Einheiten und 776/776 sichtbare Gruppen**.

Die finale R2-Edition ist deshalb keine Wahl zwischen zwei attraktiven
Übersetzungen. Sie ist eine kontrollierte Doppeledition derselben formalen
Hülle. Medizin bleibt die primär dargestellte historische Lesefassung;
praktische Material-/Badehaus-/Kalenderprosa bleibt inhaltlich gleichrangig.
Die wissenschaftliche Aussage endet darunter: **Form und Bindung sind
reproduzierbar; Inhalt, Sprache und Lautung sind nicht identifiziert.**
