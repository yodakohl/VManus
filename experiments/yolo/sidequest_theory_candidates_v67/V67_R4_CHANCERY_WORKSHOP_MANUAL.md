# V67 R4 — Korrektorisches Werkstatthandbuch um 1420

Status: kreative Rekonstruktion eines Schreibverfahrens; keine Sprach- oder
Lautentzifferung.

## Der einfachste lehrbare Mechanismus

Die Werkstatt braucht keine universelle Geheimschrift. Sie braucht vier
materielle Hilfsmittel:

1. die schon gezeichnete Seite als Besitzer- und Layoutplan;
2. ein kleines gemeinsames Heft mit elf häufigen Ganzkarten und vier formalen
   Slotregeln;
3. register- oder seitenlokale Exemplare für die große seltene Kartenschicht;
4. eine Handtafel für Wrapper, Join/Space, Feldschluss und Zeilenanfang.

Der Arbeitsgang lautet:

```text
gewöhnliche medizinische oder technische Quellnotiz
  -> Bildbesitzer und wiederholte Argumente auslassen
  -> OWNER / ACTIVE / TARGET / PREVIOUS recordlokal setzen
  -> häufige Werte als exakte Ganzkarten einsetzen
  -> Parameter-, Ziel-, Link- und Relationsslots formal markieren
  -> übrige Inhalte als ganze Exemplarkarten kopieren
  -> Felder und lokale Abschlüsse setzen
  -> nach freiem Bildraum umbrechen
  -> Hand-/Positionsrenderer anwenden
```

Das erklärt zugleich, warum mehrere Schreiber dasselbe System lernen können
und warum wir heute nur einen kleinen Kontrollkern zurücklesen: Der Code war
mit Exemplar vollständig, aber nicht selbstbeschreibend.

## Quellreihenfolge

Eine einzige Satzstellung für alle Sektionen wäre unnötig kompliziert.

- **Herbal:** Lemma/Bildbesitzer → Pflanzenteil → Vorbereitung → Menge/Zustand
  → Gebrauch → Fortsetzung. Das kann aus lateinischer Formulary-Prosa oder einer
  volkssprachigen Imperativfolge stammen.
- **Biological:** Station → aktive Charge → Parameter/Link/Ziel → Zustand oder
  Kontakt → Transfer → lokaler Schluss. Das ist stärker tabellarisch und
  betriebsartig.
- **Astro:** lokale Schlüssel wählen → gezeichneten Ort lesen → lokale Regel
  anwenden. Die Diagrammoberflächen gehören in ein getrenntes Exemplarbuch.

Die ausgewählte Quelle ist daher ein Hybrid: normale Fachsprache vor der
Kompilation, technische Slots während der Kompilation und Ganzkarten als
Werkstattbrevigraphen. Keine sichtbare Teilform muss eine Silbe oder ein
lateinisches Kürzungszeichen sein.

## Neun Lektionen

1. Bild und Recordgrenzen erkennen.
2. gewöhnliche Quellnotiz schreiben.
3. vier recordlokale Register führen.
4. elf häufige Ganzkarten auswendig lernen.
5. vier formale Slots setzen.
6. seltene Karten aus dem richtigen Exemplar kopieren.
7. Felder und lokale Schlüsse setzen.
8. nach Bildraum umbrechen und Renderer anwenden.
9. getrennt nach Register, Karte und Exemplar korrigieren.

Ein Lehrling darf nie `VORIGES?` über einen Recordreset tragen, Zeile mit Satz
gleichsetzen, einen Wrapper als neues Wort lesen oder f68 und f69 durch moderne
Nummern verbinden.

## Werkstattrollen

- Der **Kompilator** kennt Quelltext, Bildbesitzer und Recordgliederung.
- Der **Exemplarverwalter** pflegt gemeinsame und lokale Ganzkartenlisten.
- Der **Schreiber** setzt Felder, Reflow und Handrenderer.
- Der **Korrektor** liest die opake ID-Folge gegen Exemplar und Registerstand
  zurück. Eine kleine Werkstatt kann Rollen vereinigen; mehrere Hände benötigen
  keine verschiedene Grammatik.

## Rücklesegrenze

Mit Karte, Register und lokalem Exemplar kann die Werkstatt alle 776 Gruppen
reproduzieren. Ohne lokales Exemplar bleiben nur kurze Mnemonics, formale
Slotrollen und Diagrammadressen. Das ist kein Defekt des damaligen Systems: Es
war für Eingeweihte mit materiellen Hilfsmitteln gedacht. Für uns bedeutet es,
dass ein flüssiger deutscher V64–V66-Text eine Quellenrekonstruktion bleibt.

Das ausgewählte Modell ist daher:

```text
EXEMPLAR_DEPENDENT_HYBRID_FORMULARY_AND_CARD_REGISTER
```

Es ist einfacher als eine phonetische Verschlüsselung und flexibler als ein
rein tabellarischer Code. Sein stärkster Widerspruch ist zugleich sein
Erklärungsvermögen: Ohne verlorenes Exemplar sind 239 Prosaevents und sämtliche
395 Astroinhalte nicht semantisch rücklesbar.

## Artefakte

- `V67_R4_NINE_LESSON_MANUAL.tsv`
- `V67_R4_SOURCE_MODEL_COMPARISON.tsv`
- `V67_R4_14_UNIT_SOURCE_EDITION.tsv`
- `V67_R4_776_GROUP_COMPILER_LEDGER.tsv`
- `V67_R4_14_UNIT_ROUNDTRIP_TESTS.tsv`
- `V67_R4_VALIDATION.json`
