# V45 R4 — Stamm-first Korrektur der vollständigen Übersetzung

## Korrekturprinzip

Die V43-Übersetzung bleibt vollständig, wird aber nicht länger so behandelt,
als wären 173 ganze deutsche Sätze 173 elementare „Wörter“. Jede Karte erhält
nun drei explizite Ebenen:

```text
stabiler PAGE_HOST-Kern oder formale Achse
+ lizenzierte Koordinate (FRAME / INNER_D / RIGHT / DY / B3)
+ konkrete lokale Expansion aus Bild, Record und Nachbarkarten
```

Der Builder erzeugt ein vollständiges 173-Kartenlexikon und eine vollständige
381-Ereignis-Interlinearversion. Kein Ereignis verliert seine konkrete
deutsche Lesung.

## Harte Konsistenzregeln

1. `AIIN` trägt immer STANDARDISIERTES MASS, nie Tuch, Flüssigkeit oder Ziel.
2. `OR` trägt immer BEREITETES MEDIUM/PRODUKT; „Flüssigkeit“ ist lokale
   Spezialisierung.
3. `OK` trägt immer AKTIVIERUNG/ZUWEISUNG; RIGHT bestimmt den Operanden.
4. `OT` trägt immer MARKIERTEN BEZUG/ROUTE/PARAMETER.
5. `EY` trägt höchstens SOLLZUSTAND; „klar ablaufen“ ist lokale Expansion.
6. `DY` trägt Vollzug/Zellschluss, nicht die konkrete vorausgehende Handlung.
7. `CHEY` und `CHEEY` werden nicht oberflächlich zusammengezogen.
8. Eine nicht produktiv belegte Karte bleibt eine konkrete Ganzkarte, statt
   durch erfundene Buchstabenwerte zwangszergliedert zu werden.

## Ergebnis

Die Übersetzung wird dadurch nicht kürzer, aber ihr Lernmechanismus wird
einfacher. Dieselbe lange deutsche Lesung kann nun als Expansion einer kleinen
Kernkarte verstanden werden. Beispiel:

```text
qokaiin
  OK    = spezifizierten Arbeitsposten aktivieren
  AIIN  = standardisiertes Maß
  lokal = beginne den nächsten abgemessenen Posten

shey / cheey
  EY    = geforderten beobachtbaren Sollzustand erreichen
  lokal = bis die Flüssigkeit klar abläuft
```

Bei den meisten der 136 Hosts ist das Panel weiterhin zu klein für ein echtes
Paradigma. Dort wird der konkrete Ganzkartenwert beibehalten und ausdrücklich
als gelernter Kartenwert markiert. Das ist ehrlicher und zugleich für eine
Werkstatt um 1420 plausibler als eine voll reguläre moderne Kunstsprache.

## Grenze

Dies ist die kreative Zehnseiten-Arbeitstheorie. Die Zerlegung weist keine
Sprache, Laute, Morpheme, Medizin oder historische Bedeutung nach. Astro bleibt
im bereits getrennten lokalen Diagrammnamensraum. `f84` und `f84r` blieben
versiegelt.
