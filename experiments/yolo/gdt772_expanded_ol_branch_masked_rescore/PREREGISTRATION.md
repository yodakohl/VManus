# GDT772-Präregistrierung — sieben Vollbrücken plus eingebaute Gegenfälle

Datum: 2026-09-03

Status vor Ausführung: `REGISTERED_UNSCORED`

## Vor der Wertung festgelegt

1. Basis sind alle fünfzehn Zeilen aus GDT770.
2. Hinzu kommen genau die sieben Loci aus
   `src/NEW_LINE_SPECS.tsv`; kein Treffer wird nach dem Score ausgetauscht.
3. Alle exakten `ol|ckhy|ols|otar` einer aufgenommenen Zeile werden
   gleichzeitig maskiert. Die sieben Zeilen bringen zehn, nicht sieben,
   zusätzliche `ol`-Masken.
4. Die sieben Vollfälle sind `f112r.36@2`, `f30v.2@7`, `f75r.26@2`,
   `f81r.15@2`, `f81r.22@8`, `f82r.33@2` und `f85r1.21@4`.
5. `f75r.26@5`, `f81r.22@4` und `f81r.22@6` bleiben als automatische
   Gegenfälle im Score.
6. Die vollständige GDT770-Kandidatenliste, der Kantenbinder, alle
   Strafgewichte, die acht Gewinnerhürden und die Seite als Holdout-Einheit
   bleiben byteidentisch.
7. Alte Targetdefaults, Targetrollen, deutsche Lesbarkeit und historische
   Plausibilität erhalten null Scorekredit.
8. Rerender-Korrekturen werden erst für die Anzeige eingesetzt und verändern
   keine Strukturrolle.

## Erwartete unterscheidbare Ausgänge

- Der Positionsdispatch gewinnt nur, wenn die sieben Vollfälle seinen
  früheren Vorsprung verstärken, ohne dass die drei Gegenfälle ihn gegen das
  invariante Nomenmodell zurückbinden.
- Das Nomenmodell `Ansatz/Basis` gewinnt nur, wenn es auch nach jedem
  Seiten-Holdout mindestens vier Punkte vor allen Rivalen bleibt.
- Ein exakter oder foldweiser Gleichstand bleibt `OPAQUE_NULL`.
- Die unveränderten `ckhy`, `ols` und `otar`-Decks dürfen nur ihre alten
  Entscheidungen reproduzieren; die neuen Zeilen enthalten keine dieser drei
  exakten Zielformen.

## Aussagegrenze

Die Runde darf eine kohortenlokale `ol`-Policy priorisieren oder den Gegensatz
explizit offenlassen. Sie bestätigt weder ein Wort noch Öl, Wasser, Wein,
Essig, Ansatz, Produkt oder eine Präposition. Sie exportiert keine Teilform und
öffnet keine neue Seite, kein Bild, keine OCR, keine Transkription, kein `f84`
und kein `f84r`.
