# GDT772 — Sieben neue `ol`-Brücken im unveränderten Turnier

Status: `PARTIAL__22_LINES_186_TOKENS_183_SCORE_NODES_182_READER_UNITS__27_TARGET_MASKS_OL15_CKHY4_OLS3_OTAR5__OL_LEFT_BRANCH_7_ON_6_PAGES_OTHER_BRANCH_4_ON_4__OL_POSITIONAL_NOMINAL_EXACT_TIE_56__0_POLICY_WINS__ZERO_CONFIRMED_LEXEMES_NO_NEW_PAGE`. Der getrennte Validator bestätigt 304 Prüfungen,
eine unabhängige Scoreberechnung und den byteidentischen Replay aller vierzehn
Runner-Artefakte.

## Ergebnis

Die fehlende GDT770-Verzweigung ist jetzt real belegt: sieben vollständige
Fälle auf sechs Seiten verbinden eine linke Mengen-/Wertkante über `ol` mit
einer rechten Zubereitungs-, Feld- oder Prozesskante. Trotzdem gewinnt
`von/aus` nicht. Sobald alle exakten `ol` derselben sieben Zeilen ebenfalls
verdeckt werden, kommen drei unvermeidliche Gegenfälle hinzu. Im unveränderten
Score landen der Positionsdispatch und das invariante Nomen `Ansatz/Basis`
dadurch **exakt gleichauf bei 56 Strafpunkten**.
`OPAQUE_NULL` liegt bei 127, das messbare Produktmodell bei
76.

Das ist kein Rückfall auf fehlende Abdeckung. Beide Positionszweige bestehen
ihre Seitenhürde: der neue linke Wertzweig auf sechs Seiten, der alte andere
zweiseitige Zweig auf vier. Die Entscheidung bleibt offen, weil das
Positionsmodell seinen alten Neun-Punkte-Vorsprung gegenüber `Ansatz/Basis`
in den neuen Zeilen genau wieder verliert und zusätzlich die Gleichstands- und
Holdout-Hürden verfehlt.

## Wo die exakte Bindung entsteht

- Die sieben Vollfälle geben dem Positionsmodell lokal je vier Punkte Vorteil
  gegenüber dem Nomenmodell: zusammen +28.
- `f75r.26@5` besitzt links einen Wert, aber rechts keine zugelassene Kante.
- `f81r.22@4` besitzt rechts einen Wert, aber links keine typisierte Kante.
- `f81r.22@6` besitzt links einen Wert und rechts nur einen weiteren
  Mengen-/Wertposten, nicht die geforderte Feld-/Stoff-/Prozessseite.
- Diese drei Fälle kosten den Positionsdispatch zusammen 37 Punkte, während
  das breite Nomenmodell dort null zahlt. Die neue Tranche kippt den alten
  relativen Vorsprung daher um neun Punkte; über alt und neu entsteht 56:56.

Die vollständige Fallrechnung steht in
`artifacts/OL_POSITIONAL_VS_NOMINAL_CASES.tsv`. Der neue Reader zeigt jede der
sieben Zeilen parallel mit `[ol]`, `von/aus`, `Ansatz/Basis` und
`Produkt/Resultat`, ohne diese Anzeigen in den Score einzuspeisen.

## Praktischer Rezeptlese-Gegencheck

Der getrennte manuelle Gegencheck macht den Gleichstand inhaltlich noch
wichtiger. Die sieben linken Felder sind nicht siebenmal derselbe Typ: vier
sind echte Mengenformen (`sain` dreimal, `oraiin` einmal), `dain` ist nur ein
dimensionsoffener Wert, und `keor` sowie `chedar` tragen bereits zusätzliche
Inhalts- oder Qualitätsstruktur. In sechs Fällen ist ein quantifizierter
Ansatz-/Inhaltskopf mindestens ebenso natürlich wie ein partitives `von`.
Beim siebten Fall, `chedar ol oly`, ist die mechanische Ausgabe „von/aus
abseihen“ praktisch schlechter als ein Feldtrenner oder `dann/und`.

Darum wird `aus` deutlich herabgestuft: Keine der sieben Zeilen zeigt eine
unabhängige Quelle→Resultat-Richtung. Auch Öl, Wasser und Wein bleiben
untereinander vollständig ununterscheidbar. Die Einzelfallurteile samt
konkreten Rivalen stehen in `artifacts/OL_MANUAL_RECIPE_READING.tsv` und haben
null Scorekredit.

Der Gegencheck legt zugleich eine Grenze des alten Kandidatendecks offen. Der
Positionsrelator darf eine linke Menge **und** ein rechtes
Zubereitungs-/Prozessfeld binden. Das alte Nomen `Ansatz/Basis` darf dagegen
keinen quantifizierten Inhaltskopf mit rechtem Modifikator oder Prozessfeld
abbilden. Der Stand 56:56 ist deshalb keine feine lexikalische Entscheidung,
sondern der Punkt, an dem das alte Deck ausgereizt ist.

## Die anderen drei Wörter

`ckhy`, `ols` und `otar` reproduzieren ihre GDT770-Ergebnisse bytefunktional,
weil keine der sieben neuen Zeilen eine dieser drei exakten Ganzformen enthält.
Ihre Defaults bleiben formal NULL. Das ist ein Kontrollsignal dafür, dass nur
neue `ol`-Evidenz in den alten Scorer gelangt ist.

## Konsequenz für die Arbeitsübersetzung

Für `ol` ist die beste ehrliche Anzeige jetzt nicht ein einziges Wort, sondern
die konkrete Opposition:

> quantifizierter `Ansatz/Inhaltskopf` **oder**, wenn ein echter partitiver
> Anschluss passt, `von`; andernfalls Feldtrenner beziehungsweise `und/dann`.

`aus` bleibt nur ein schwacher, richtungsabhängiger Rivale. Öl, Wasser, Wein,
Essig und ein fertiges Produkt erklären diese Kohorte nicht besser. Die Daten
entscheiden aber auch noch nicht zwischen der relationalen und der nominalen
Seite.

Die nächste sinnvolle Runde verwendet dieselben fünfzehn `ol`-Fälle und keine
neuen Seiten. Sie trennt `von` von `aus`, ergänzt ein Nomenmodell, das linke
Menge plus rechten Modifikator/Prozess legal binden kann, und führt
Feldtrenner/Folge sowie Maß-/Einheitenkomplement als eigene Kandidaten. Erst
dieses reparierte Deck kann die jetzt sichtbare Opposition fair entscheiden.

## Grenze und Scope

Die Runde verwendet 22 bereits zugelassene Zeilen, 186 Token, 183 Scorenodes
und 27 gleichzeitige Zielmasken auf 20 Seiten. Keine neue Seite, kein Bild,
keine OCR, keine neue Transkription, kein `f84` und kein `f84r` wurde geöffnet.
Bestätigte Lexeme, Übersetzungen und Komponenten bleiben null.
