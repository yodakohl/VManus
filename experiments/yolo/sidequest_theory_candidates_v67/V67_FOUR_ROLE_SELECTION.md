# V67 — Vierrollen-Auswahl: Werkstattrealisierung um 1420

Status: kreative Rekonstruktion eines Lehr- und Schreibverfahrens; keine
Sprach-, Laut- oder Klartextidentifikation.

## Auswahl

Alle vier Rollen wählen dasselbe zweistufige Hybridmodell:

```text
gewöhnliche lateinische oder volkssprachliche Fachquelle
  -> bild- und registergestützte Ellipse
  -> recordlokale OWNER / ACTIVE / TARGET / PREVIOUS-Zustände
  -> 11 gelernte exakte Ganzkarten + 4 Formalprompts
  -> großer lokal exemplarabhängiger Ganzkartenrest
  -> Herbal-Artikel | Bio-Arbeitszellen | Astro-Lookup
  -> Feldschluss, Bildraum-Reflow und Handrenderer
```

Die vier Formalprompts und elf Mnemonics belegen wegen einer Überschneidung
14, nicht 15, verschiedene Control-Karten. Sie erkennen 119/381
Prosaereignisse; 262 bleiben lokale Exemplarkarten. Alle 395 Astrogruppen sind
seitenlokale Diagrammadressen oder -fragmente und übernehmen keine Prosaform.

## Was ein Lehrling wirklich lernen muss

1. Bildbesitzer und Recordgrenzen erkennen.
2. Die normale lokale Fachnotiz formulieren.
3. Wiederholte Besitzer-, Aktiv-, Ziel- und Vorpostenargumente auslassen und
   vier recordlokale Register führen.
4. Die 14 gemeinsamen Control-Karten als **ganze Formen** lernen.
5. Alle übrigen Karten aus dem richtigen Register-/Seitenexemplar kopieren.
6. 135 Felder, 90 lokale Schlüsse und 45 offene Schnitte setzen.
7. Erst danach nach dem verfügbaren Bildraum umbrechen und die Handrenderer
   anwenden.
8. Gegen Übergangslog, Codeblatt und Masterexemplar rücklesen.

Das ist für eine kleine Werkstatt mit Kompilator, Exemplarverwalter, Schreiber
und Korrektor plausibel handhabbar. Rollen können von drei bis fünf Personen
geteilt oder vereinigt werden.

## Drei unterschiedliche Quellordnungen

- **Herbal:** Besitzer/Lemma → Teil → Bearbeitung/Medium → Menge/Zustand →
  Gebrauch → Fortsetzung. Lateinische Formulary-Prosa und volkssprachlicher
  Imperativ sind beide mögliche Vorstufen.
- **Biological:** Station → aktive Charge → Parameter/Link/Ziel → Zustand oder
  Kontakt → Transfer → lokaler Schluss. Die Reinschrift ist tabellarischer als
  die mögliche mündliche Anweisung.
- **Astro:** lokale Schlüssel wählen → gezeichneten Locus lesen → lokale Regel
  anwenden. Dafür gilt ein getrenntes Diagrammcodebuch.

Ein abstrakter Latin-like- und ein Vernacular-like-Slotproxy verletzen beide
42/94 vergleichbare Paarordnungen. Die sichtbare Folge identifiziert daher
weder Latein noch eine Volkssprache und wird vom Compiler nicht umsortiert.

## Reversibilität

```text
sichtbare ID, Reihenfolge, Feld und Layout mit Codebuch: 776/776
konkrete ausgewählte Quellintention mit Masterexemplar: 776/776
konkrete ausgewählte Quellintention ohne Masterexemplar:   0/776
```

Die 119 Control-Ereignisse liefern ohne Exemplar nur einen kurzen Mnemonic- oder
Formalwert, nicht die vollständige Quellphrase mit Gegenstand, Medium, Ziel und
Kontext. 202 Prosaereignisse in 34 IDs benötigen zusätzlich einen
Vorkommensselektor für die richtige Oberfläche; 140 wiederholte Astroformen
benötigen ihre Diagrammadresse.

Vier Register sind für die gewählte Edition minimal: ohne Zustand werden 9/116
Aussagen getragen, mit OWNER 27, mit OWNER+ACTIVE 88, mit zusätzlichem PREVIOUS
107 und erst mit TARGET 116. Der nackte Postzustand rekonstruiert nur 47/116;
das Übergangslog bleibt notwendig.

## Historische Einordnung

Zeitnahe Rezeptbücher, Herbalien, medizinische Faltalmanache, Tabellen,
gewöhnliche Brevigraphen und mehrhändige Sammelhandschriften machen jede
einzelne Werkstatttechnik plausibel. Sie belegen nicht dieses konkrete
Codebuch. Der stärkste Rival bleibt deshalb ein gewöhnliches mehrsprachiges
Fachmiszellaneum mit unbekannter Sprache und starkem Layout.

## Urteil

`EXEMPLAR_DEPENDENT_HYBRID_FORMULARY_AND_CARD_REGISTER`

Das System ist **lehrbar und kopierbar**, aber nicht selbstbeschreibend. Es
erklärt mehrere Hände, große lokale Kartenschwänze, Reflow, Felder und drei
Diagrammnamespaces besser als eine universelle Lautchiffre. Sein Preis ist
offen: Geht das Masterexemplar verloren, bleibt uns die formale Hülle, nicht
der konkrete Quelltext.
