# V57 — Auswahl des lehrbaren Werkstattsystems

Status: kreative Zehn-Seiten-Arbeitstheorie, keine Entzifferung.

## Gemeinsames Urteil der vier Rollen

`SMALL_PRODUCTIVE_CONTROL_GRAMMAR_PLUS_LARGE_EXEMPLAR_LAYER`

Das System wäre für mehrere Schreiber um 1420 praktisch erlernbar, aber nur
als beaufsichtigtes Formular-/Exemplarsystem. Es ist nicht als autonomer
deutscher oder lateinischer Bedeutungs-Codec rekonstruiert.

Die einfachste Werkstattarchitektur lautet:

```text
Bild oder Diagrammlage liefert den stillen Besitzer
+ vier produktive Kontrollprompts
+ FIELD := NONCLOSE* TERMINAL?
+ elf memorierte gemeinsame Ganzkarten
+ register- und seitenlokale Exemplardecks
+ Positions-/Rendererregeln
= reproduzierbare sichtbare Seite
```

## Was ein Lehrling wirklich lernt

1. **Seitentyp und stillen Besitzer binden.** Herbal bindet die Bildpflanze,
   Biological einen sichtbaren Becken-/Figur-/Laufkontext, Astro eine
   Diagrammposition. Der Besitzer wird nicht als Kartenwort geschrieben.
2. **Felder statt Sätze bauen.** Ein Feld enthält beliebig viele offene
   Karten und höchstens eine feldfinale Schlusskarte. Die physische Zeile ist
   Reflow und darf eine Aussage fortsetzen.
3. **Vier harte Prompts benutzen.** Vorgabeparameter aufrufen, Standardslot
   setzen, lokalen Relationsslot setzen, aktiven Arbeitsstand verknüpfen.
4. **Elf gemeinsame Ganzkarten erkennen.** Ihre zehn deutschen Mnemonics sind
   Rezitationshilfen, keine bewiesenen Wörter und keine zerlegbaren Stämme.
5. **Den langen Schwanz kopieren.** 162 der 173 Prosa-Kartentypen liegen
   außerhalb des elfteiligen Brückendecks. Sie werden aus dem lokalen
   Musterbogen übernommen und dürfen bei der Rücklesung `UNKNOWN` bleiben.
6. **Astro separat lernen.** f67r2, f68r1 und f69v sind drei eigene
   Positions-/Lookup-Schablonen. Weder Prosa-Werte noch ein stiller
   f68↔f69-Index dürfen importiert werden.

Das ausgewählte achtstufige Curriculum steht in
`V57_SELECTED_TEACHING_MANUAL.tsv`.

## Ausführbare Maschine

R3s acht Zustände und fünfzehn Übergänge sind die strengste Fassung. Ein
Schreiber wählt Prosa oder Astro, bindet Register und Bildargument, öffnet
Record und Feld, kopiert eine lizenzierte Kern- oder lokale Karte, setzt
optional den formalen Schluss, behandelt den Zeilenwechsel nur als Renderer-
Reset und schließt Record beziehungsweise Seite. Jede nicht eindeutig
lizenzierte Karte geht in `REJECT`, statt aus einer flüssigen Übersetzung
erfunden zu werden.

Mit dem vollständigen Exemplar ist der formale Rundlauf verlustfrei:
Kartenidentität, Feldgrenze, Schluss, Wiederholung, Lage und Zeilenumbruch
können kopiert und zurückgelesen werden. Aus der freien Quellenprosa allein
geht das nicht:

- Tier A adressiert nur 45/381 Ereignisse (11,8 %) in 35/135 Feldern;
- 236/381 Ereignisse (61,9 %) bleiben unter der ausgewählten Schicht opak;
- die konkrete Herbal-/Bio-Prosa wählt weder die seltene Ganzkarte noch ihre
  JOIN/SPACE-, Positions- oder Oberflächenform;
- f69v hat formal 140/140 Gruppen, aber 0/140 extern verankerte Regelinhalte.

## Drei entscheidende Rücklesungen

### f10r_R1

Mit Bild und Exemplar kommen 14/14 Karten und beide Felder zurück. Ohne
Exemplar bleibt nur ungefähr:

```text
markierten Bildstoff im Standardslot verwenden
+ laufenden Ansatz verknüpfen
```

Wurzel, Wasser, Reinigen, Zerkleinern, Verwahren und Wärme sind lokale
Artikelannahmen.

### f82r_R1

Mit Exemplar kommen 62/62 Karten und 26/26 Felder zurück. Der gemeinsame Kern
liefert nur:

```text
Vorgabeposten am lokalen Bezug setzen
+ mit Arbeitsstand verknüpfen
+ verwenden
+ lokale Bio-Zellen kopieren und schließen
```

Bad, Wasser, Tuch, Temperatur, Körper und genaue Bewegungsfolge bleiben im
Bild-/Registerwissen.

### f68r1

Die Kombination `SPATIAL_LOCUS + LOCAL_EXEMPLAR_LABEL` bewahrt die formale
Station genau. Mond, Mondhaus, Wirkung, Start und Richtung werden nicht
zurückgewonnen. Das ist die reinste lehrbare Teilmaschine der zehn Seiten.

## Typische Lehrlingsfehler

- Zeile als Satz oder Schluss lesen;
- CLOSE als gesprochenes „fertig“ oder „ablassen“ behandeln;
- Wrapper, JOIN/SPACE oder RIGHT-Familie übersetzen;
- sichtbare Ähnlichkeit statt exakter Ganzkartenidentität kopieren;
- Bildobjekte in Kartenwerte einschreiben;
- Bio-lokale WARM-/SPÜLEN-/ABLASSEN-Mnemonics ins Herbal übertragen;
- eine opake Karte durch eine plausible bekannte Karte ersetzen;
- die beiden qokaiin-Vorkommen am f82r-Zeilenwechsel zusammenziehen;
- die zwei 28er-Diagramme allein wegen ihrer Größe indexgleich lesen.

Der Korrektor repariert stets gegen das lokale Exemplar, nicht gegen den
erwarteten Satzsinn.

## Historische Plausibilität

Die Rekonstruktion braucht keinen modernen Compiler. Sie kombiniert
zeitgenössisch gewöhnliche Mechanismen: Fachabbreviatur, memorierte
Brevigrafen, Musterkopie, bildgestützte Ellipse, lokale Registeraddenda,
Formularzellen und getrennte Almanachschablonen. R2s konkreter Lehrplan setzt
für einen vorgebildeten Schreiber acht beaufsichtigte Lektionen beziehungsweise
144 Arbeitsstunden an. Diese Zahl ist eine Plausibilitätsprobe, keine
historische Messung.

## Verbesserung gegenüber V56

V56 lieferte ein Phrasebook. V57 erklärt, wie dasselbe System trotz vieler
opaker Karten und mehrerer Hände benutzt werden kann: Die kleine Schicht wird
produktiv gelernt, der große Schwanz nicht entschlüsselt, sondern als
Exemplarbestand bewahrt. Dadurch muss keine kurze Karte eine ganze moderne
Anweisung tragen.

Der Preis ist ebenso klar: Unsere flüssigen Zehn-Seiten-Texte sind
meisterseitige Expansionen. Sie können nicht allein aus dem sichtbaren
Kartentext rekonstruiert werden.

`f84` und `f84r` blieben versiegelt.
