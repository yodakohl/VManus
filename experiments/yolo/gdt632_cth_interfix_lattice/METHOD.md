# GDT632 method

## Frage

Bilden die bereits sichtbaren Reihen

```text
ch/sh + (nichts | e | o | eo) + cth + Rest
```

ein gemeinsames Kompositionsgitter? Falls ja: Gruppieren sich `e` und `o`
gleich, oder verlangt das Vorkommen nackter Köpfe eine Hierarchie wie
`ch/sh + e? + [o? + cth+Rest]`? Die Bedeutungen von `e` und `o` werden nur
eingetragen, wenn das Panel selbst eine konkrete Zuordnung trägt.

## Eingaben und Seitengrenze

- dieselbe explizite 179-Seiten-Allowlist wie in GDT631; `f1r` ist
  ausgeschlossen, `f84` und `f84r` bleiben vor dem Einlesen verboten;
- ZL3b-Token und die Zeilenlesungen ZL3b/IT2a/RF1b, jeweils über den guarded
  TSV-Reader mit expliziten Auswahlwerten und Ausgabespalten;
- GDT625s publizierte CTH-Grundfamilie;
- GDT631s Ergebnis, Wörterbuch V8 und bereits publizierte Bildurteile;
- keine neue Seite und kein neues Bild.

ZL3b, IT2a und RF1b sind verschiedene Lesungen desselben Manuskriptspans.
Leserübereinstimmung misst Transkriptionsstabilität, nicht drei unabhängige
Vorkommen.

## Formenraster

1. Als fusionierte Zielform gilt exakt
   `^(ch|sh)(eo|e|o)?cth(.*)$`. Der linke Qualitätskern ist `CH` oder `SH`,
   die Zwischenklasse `NONE`, `E`, `O` oder `EO`; alles nach `cth` bleibt der
   sichtbare Rest `R`.
2. Für jede der acht Zellen werden Token, Typen, Seiten, Reste,
   Dreifachstabilität und Zugehörigkeit zur publizierten nackten CTH-Familie
   gezählt. Gleicher Rest unter `ch` und `sh` bildet ein direktes Paar.
3. Die fusionierten ZL3b-Token bleiben die feste Grundpopulation. Getrennte
   Ausdrücke werden nicht hineingemischt, sondern in vier nachvollziehbaren
   Populationen ausgewiesen:

   - `FUSED_ZL`;
   - plus sieben in allen Lesern getrennte `linke Shell | cth+R`-Spans;
   - plus drei ZL3b-getrennte, in einem anderen Leser fusionierte eindeutige
     Spans;
   - plus f21r.7, dessen linke Grenze sichtbar, dessen rechter Zielrand aber
     überlappend ist.

## Innere Hierarchie und Reihenfolge

4. Unabhängig vom Qualitätskern werden sämtliche nackten Köpfe
   `cth+R`, `ecth+R`, `octh+R` und `eocth+R` gezählt. Für jede Zieloberfläche
   wird dann die erwartete innere Basis gebildet:

   ```text
   ch/sh + ∅/e + cthR    -> cthR
   ch/sh + o/eo + cthR   -> octhR
   ```

   Abdeckung wird sowohl im globalen Typendeck als auch auf derselben Seite
   berichtet. Globale Typabdeckung zeigt Komposition; sie wird nicht als
   lokale Kopie ausgegeben.
5. `ch/sh+eo+cth` wird gegen die umgekehrte Reihenfolge
   `ch/sh+oe+cth` geprüft. Zusätzlich werden nackte und getrennte E-, O-, EO-
   und OE-Köpfe in jeder der drei Lesungen gezählt.
6. Die Leserzeilen werden nach derselben Zielspanne in fusionierter und
   getrennter Form durchsucht. Die konservative interne Grenze verlangt genau
   einen Zielspan pro Leser. Mehrfachziele und äußere Restgrenzen bleiben als
   Warnungen sichtbar. Zwei Gegenrichtungen werden vollständig als Nullsuche
   ausgegeben: `ch/sh | e/o/eo+cthR` und `ch/sh | e/o/eo | cthR`.

Damit können Orthographie und innere Analyse auseinanderfallen. Ein sichtbares
`cheo | cthy` kann morphologisch dennoch als `ch+e+[octhy]` gelesen werden.

## Kontext und Arbeitsbedeutung

7. Gleiche Reste, gleiche linke/rechte Nachbarn, wiederholte Mikroklammern,
   Abschnitt, Currier-Sprache und Hand werden zellenweise verglichen.
   Seitenkoexistenz prüft, ob `e/o` bloß ein deterministischer Seiten- oder
   Handersatz sein könnten.
8. Die aus GDT631 übernommene Arbeitsachse bleibt konkret:

   - `ch` = provisorisch trocken;
   - `sh` = provisorisch feucht;
   - `cth+R` = CTH-Pflanzen-/Drogenmaterial, im Herbal Blatt-/Krautmaterial.

   Kontakte zu heißen, kalten, trockenen und feuchten Gradformen werden bis
   Distanz drei gezählt; unmittelbare Kontakte und gleiche Achse werden separat
   ausgewiesen. `e` und `o` werden im deutschen Lesetext nicht mit „Wasser“,
   „Öl“, „Wurzel“ oder einem anderen geratenen Wort gefüllt. Ihre Formklasse
   bleibt im Parse als `[E]`, `[O]` oder `[EO]` sichtbar.
9. Konkrete Ausgaben enthalten nur die kleinste tatsächlich gelesene
   Qualitäts-/Materialklammer. Nicht gelesene Nachbartoken werden nicht durch
   Tätigkeitsfloskeln ersetzt.

## Vollständigkeitskontrolle

10. Eine breitere Zählung erfasst jedes fusionierte ZL3b-Token, das mit
    `ch` oder `sh` beginnt und später `cth` enthält. Formen außerhalb des
    exakten `∅/e/o/eo`-Rasters werden vollständig aufgelistet. Dadurch kann ein
    sauberes Raster nicht versehentlich als universelle CTH-Grammatik erscheinen.
11. Die geerbten Bildurteile werden nur auf tatsächlich dort vorkommende
    Zielklassen übertragen. Zwei zeitnahe Arzneibuchvergleiche prüfen lediglich,
    ob gelernte Namen, Pflanzenteile, Qualitätskürzel und Grade historisch in
    einem Mischsystem zusammenstehen konnten.

## Auswertungsregel und Reichweite

Das geordnete Modell wird Arbeitsbasis, wenn alle acht Oberflächenzellen
belegt sind, gleiche Reste die `ch/sh`-Gegenreihen verbinden, O-/EO-Formen ihre
vorhergesagten nackten `o+cth+R`-Köpfe treffen, die EO/OE-Reihenfolge gerichtet
ist und echte Lesergrenzen die linke Shell vom CTH-Teil trennen.

Das Experiment darf konkrete trockene beziehungsweise feuchte CTH-Materialformen
ausgeben. Es darf `e` oder `o` noch kein Lexem geben. Insbesondere folgen aus
dem Raster weder Wasser/Öl noch Blatt/Wurzel, Medium/Gefäß oder eine Operation.
Es identifiziert keine Phonetik, Sprache, Pflanzenart oder Gesamtübersetzung.
