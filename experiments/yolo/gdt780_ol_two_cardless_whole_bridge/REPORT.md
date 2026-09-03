# GDT780 — zwei belegte kartenlose Ganzwörter nach `ol`

Status: `PASS__2_EXACT_CARDLESS_WHOLES__2_FORMS__2_LOCI__247_CONTEXTUAL__129_FALLBACKS__207_CONSUMED__NO_COMPONENT_EXPORT`.

## Ergebnis

Der eingefrorene, occurrence-ID-freie Selektor trifft genau zwei der 25
reader-exakten kartenlosen GDT779-Restzeilen: `ol eees` und `ol sheeol`, je
einmal auf zwei loci, zwei Seitenlabels und zwei physischen Folios. Es existiert
kein weiteres exaktes, nicht-exaktes oder bereits kontextuelles Elternmatch
dieser beiden vollständigen Oberflächen.

Beide Treffer ersetzen den generischen Ansatz-/Zubereitungsfallback. Die
kontextuelle Abdeckung steigt **245→247**, die Restmenge fällt **131→129** und
der kollisionsfreie Verbrauch rechter Tokens steigt **205→207**. Alle anderen
374 Rendererzeilen bleiben in Bedeutung, Precedence und Verbrauch unverändert.

## Unabhängige Brücken

- **`eees` → Mengenfeld:** Der gelockte GDT758-Komparator zählt sieben
  reader-exakte Vorkommen, vier exakte Rechtskontexte und drei `aiin`-Folger
  (Rate .75 gegenüber .021613, Lift 34.702083). GDT769s gelockte Detailzeile
  rekonstruiert die Zielstelle als reader-exaktes `ol`, gefolgt von den beiden
  sauberen, zulässigen Tokens `eees aiin`; ihre Entfernung ergibt ausführbar
  **drei Kontexte und zwei `aiin`-Treffer**. Das trägt ein Mengen-/Wertfeld,
  aber weder Zahl noch Einheit.
- **`sheeol` → Endzustand:** GDT745–GDT747 liefern zehn Cache-/neun exakte
  Vorkommen, einen gemeinsamen Form-Verteilungskern `END_STAGE` und vier lokale
  Endkontakte auf drei Seiten. Die gelockte Detailzeile G747-O060 weist die
  Zielstelle selbst als reader-exakt, `L0` und mit null lokalen Supports aus;
  alle vier Endkontakte liegen damit außerhalb des Ziels. Der sichtbare
  GDT748-Kälterahmen hat ausdrücklich keine Ganzwortbrücke; Feuchte und Kälte
  bleiben Rivalen, nicht Identitäten.

## Zwei vollständige Passagen

- `f43v.16`: `ol eees aiin oloaiin oteos qoky chey` → ⟦Mengenfeld⟧ aiin oloaiin oteos qoky chey
- `f88r.21`: `teol chor olsheody qokeol shoy ol sheeol sheoldg` → teol chor olsheody qokeol shoy ⟦Endzustand⟧ sheoldg

Die Doppelklammern markieren ersetzbare exakte Spannenwerte. Ungeklammerte
EVA-Formen bleiben ungelöst.

## Restschuld und Grenze

Die 129 Fallbacks zerfallen in 23 reader-exakte kartenlose Rechte, 49
nicht-exakte Rechte mit V99R7-Karte, 20 nicht-exakte Rechte ohne Karte und 37
Zeilenenden ohne rechtes Token. Keine andere Form wird über Nachbarn,
Editdistanz oder Teilstrings mitgezogen.

`Mengenfeld` und `Endzustand` sind praktische Rollenlabels ganzer Spannen, keine
Übersetzungen. GDT780 bestätigt kein EVA-Zeichen, keinen Wortteil, kein Lexem,
keine Zahl, Einheit, Flüssigkeit, Substanz oder Klartextklausel. Es wurden keine
neuen Seiten, Bilder, OCR oder Transkriptionen geöffnet; `f84` und `f84r`
blieben gesperrt. Das GDT388-Paket bleibt `VALID_ACQUISITION_NOT_SCORE_READY`.
