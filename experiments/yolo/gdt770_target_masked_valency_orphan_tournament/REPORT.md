# GDT770 — Vier Wörter unter gleichzeitiger Maske

Status: `PASS`. Der unabhängige Validator besteht 34.744 Prüfungen und baut
alle 17 Runner-Artefakte byteidentisch neu auf.

## Ergebnis in einem Absatz

Das Experiment entfernt in 15 bereits zugelassenen vollständigen Zeilen alle
alten Rollen und deutschen Defaults von `ol`, `ckhy`, `ols` und `otar` und
lässt 18 feste Ganzwortmodelle nur gegen die direkten, target-unabhängigen
Nachbarkanten antreten. Der stärkste Arbeitskandidat ist für `ol` ein
kontextabhängiger Relator, für `ckhy` ein Mischvorgang, für `ols` eine fertige
Zubereitung und für `otar` knapp ein nominaler Zwischenansatz vor dem Rivalen
`dann`. Keines der vier Modelle besteht jedoch alle Stabilitäts- und
Abdeckungshürden. Die formalen Defaults bleiben deshalb `OPAQUE_NULL`; die
konkreten deutschen Wörter sind weiterhin ersetzbare Arbeitsbedeutungen, nicht
entzifferter Klartext.

## Die vier aktuellen Arbeitsbedeutungen

| Form | Konkreter Arbeitsdefault | Rohscore gegen NULL | Was tatsächlich trägt | Was offen bleibt |
| --- | --- | ---: | --- | --- |
| `ol` | unbelegter linker Mengenzweig `[aus?]`; vor einer Mengenangabe `mit`; sonst `und` | 19 gegen 41 | sechs NULL-Waisen auf vier Seiten; jeder Seiten-Holdout bleibt mindestens fünf Punkte vor jedem Rivalen | der eigens erklärte Zweig mit Menge/Wert **links** kommt kein einziges Mal vor; daher keine vollständige Relator-Policy |
| `ckhy` | `mischen` | 13 gegen 32 | fünf Waisen auf drei Seiten; 19 Punkte besser als NULL | ohne `f32r` verliert der Mischvorgang um einen Punkt gegen die beiden Nomenmodelle; an einzelnen Stellen bleiben `Mischung`, `Aufguss` oder `Abkochung` gleich gut |
| `ols` | `fertige Zubereitung` | 0 gegen 23 | alle fünf sichtbaren NULL-Waisen auf drei Seiten werden gebunden | ohne `f104v` steht das Resultat exakt 0:0 mit `abseihen`; die spezifische Identität *Colatura* ist lokal nirgends bewiesen |
| `otar` | `Zwischenzubereitung`; knapper Rivale `dann` | 16 gegen 41 | fünf Waisen auf drei Seiten | nur zwei Punkte vor `dann` (18); verschiedene Seiten drehen die Reihenfolge um, schlechteste Holdout-Marge −7 |

Die Scores sind Strafsummen; kleiner ist besser. `NULL` lässt ein Target opak
und zahlt für jede dadurch offene Mengen-, Wert-, Patienten-, Resultat- oder
Feldkante. Ein Kandidat gewinnt Punkte nur indirekt, indem er genau solche
Kanten bindet, ohne neue Valenzprobleme zu erzeugen. Deutsche Lesbarkeit,
historische Ähnlichkeit und die sichtbare EVA-Schreibung geben null Punkte.

## Warum die frühere Auswertung zu günstig war

Die erste Implementierung behandelte eine gebundene Nachbarseite so, als wären
damit sämtliche Rollen dieses Nachbarn verbraucht. Ein Nachbar kann aber etwa
gleichzeitig `FIELD`, `MATERIAL` und `PATIENT` tragen. Ein Relator, der nur die
`FIELD`-Kante nimmt, darf nicht automatisch auch die `PATIENT`-Waise löschen.

Der korrigierte Binder adressiert deshalb jede Rolle einzeln als
`(Zielstelle, Seite, Nachbarordinal, Rolle)`. Pflichtansprüche laufen zuerst,
danach darf je Seite höchstens eine noch freie optionale Rollenkante gebunden
werden. Doppelansprüche bleiben als eigener Claim sichtbar und werden
bestraft. Diese Korrektur änderte die entscheidenden Scores:

- `ol`-Relator: 11 → 19;
- positionales `ols`: 8 → 16;
- allgemeines `otar=dann`: 14 → 18;
- dadurch wird bei `otar` der nominale Zwischenansatz mit 16 zum knappen
  Rohleader.

Zusätzlich erhielten der target-owned Reader-Span und sein rechter Wertknoten
getrennte Score-IDs. Die 128 Scoreknoten besitzen nun 128 eindeutige
Identitäten. Ein eigenes Claim-Atlas zeigt jeden Bindungsversuch, statt
lediglich pauschal die verfügbare Nachbarseite auszugeben.

## Was jede Form in den 15 Zeilen macht

### `ol`

Vier der fünf Stellen sind zweiseitig. In `f58r.13` und `f3r.19` ist `und` die
konkreteste sparsame Anzeige; in `f55v.10` und `f78r.37` folgt rechts eine
Menge, weshalb `mit` idiomatischer ist. An der finalen Stelle `f55v.10@12`
feuert der Relator nicht; der lokale Arbeitsreader zeigt ehrlich
`[Grundansatz?]`. Zudem binden `f55v.10@2` und `f78r.37@2` ein Relator- und ein
Produktmodell gleich gut, sodass dort
`[abgemessene Zubereitung oder mit?]` stehen bleibt. Global führt die
Relator-Policy klar, aber ihr linkes Mengen-/Wertmuster ist in dieser Kohorte
unbelegt.

### `ckhy`

In `f32r.2` bindet `mischen` Patientenrollen auf beiden Seiten und ist der
sauberste Einzelfall. `f17v.5` trägt den Vorgang nur von links. In `f10v.2`
sind Vorgang, Positionsdispatch und zwei Nomenmodelle lokal strafgleich; der
Reader lässt alle vier Bedeutungsrichtungen sichtbar. `f24r.3` besitzt keine
positive Bindung und bleibt als
`[Aufguss oder Abkochung oder Mischung?]` markiert. Der globale Mischvorgang
ist nützlich, aber von `f32r` abhängig.

### `ols`

Das Resultatmodell bindet alle drei Stellen ohne Strafe. Das reicht für die
breite Anzeige `fertige Zubereitung`, aber nicht für eine Colatura: In den
beiden finalen Zeilen `f83v.22` und `f15v.7` ist `abseihen` lokal ebenso gut,
und keine unmittelbare Sieboperation identifiziert die Substanz. Nur
`f104v.19` verbindet Material links und den Wert `aiin` rechts klar mit einem
Resultatposten. Der alte spezifische Slash-Renderer wird daher im praktischen
Reader nicht als vermeintlich gewonnenes Wort ausgegeben.

### `otar`

Der Gesamtscore bevorzugt das Nomenmodell 16:18, doch die Seiten widersprechen
einander. `f115v.5` bevorzugt `dann`; `f55v.10` und `f46v.2` helfen dem
Nomenmodell; in `f86v5.13` stehen beide lokal gleich; und `f75r.43` bindet
sogar `bis` und `dann` gleich gut. `f46v.2` liefert für den nominalen Targetwert
keine positive Nachbarbindung und erscheint deshalb als
`[Zwischenzubereitung?]`. Die richtige Arbeitsdarstellung ist nicht ein neues
festes `otar`-Wort, sondern die offene Opposition
`Zwischenzubereitung ↔ dann`, mit kleinem Rohvorteil für die erste Seite.

## Konkreter Reader ohne versteckte Sicherheit

[GDT770_CONCRETE_READER.md](artifacts/GDT770_CONCRETE_READER.md) verbraucht
jedes der 131 Quelltoken genau einmal in 127 praktischen Einheiten. Die
Differenz entsteht aus vier bereits lizenzierten Zweierspans; einer davon ist
nur im Reader zusammengezogen und bleibt für den Score getrennt.

Der Reader ist bewusst kein glatter Rezepttext. Er behält alle lokal
strafgleichen Kandidaten, statt den ersten Tabellenwert als scheinbare
Übersetzung zu wählen:

- Support A: zwei Seiten positiv gebunden;
- Support B: nur eine Seite positiv gebunden;
- Support C: keine positive Bindung;
- C-Fälle und lokale Gleichstände erscheinen in `[Frageklammern?]`.

Das verhindert konkret, dass `f24r.3 ckhy=Mischung`, `f55v.10 ol=Grundansatz`
oder `f46v.2 otar=Zwischenzubereitung` sicherer aussehen, als ihre Kanten es
erlauben. [READER_UNIT_CONSUMPTION.tsv](artifacts/READER_UNIT_CONSUMPTION.tsv)
weist für jede Ausgabeeinheit die disjunkten Quellordinale nach.

## Umfang und Behauptungsgrenze

- 15 vollständige Zeilen, 131 Token, 128 eindeutige Scoreknoten;
- 127 Reader-Einheiten, davon 17 gleichzeitig maskierte Zielstellen;
- 30 unter NULL offene Strukturkanten;
- 18 Kandidaten in 22 festen Zweigen und 75
  Kandidat-mal-Vorkommen-Auswertungen;
- 71 Leave-one-page-out-Zeilen und 144 Gateentscheidungen;
- null Policy-Gewinner, null bestätigte Lexeme, null bestätigte
  Klartextklauseln und null Komponentenexport.

Es wurde keine neue Manuskriptseite, kein Bild, keine OCR und keine neue
Transkription geöffnet. `f84` und `f84r` blieben gesperrt. Die
`ATTACHMENT_EDGE_ATLAS.tsv` ist eine interne Spur über geerbte unmittelbare
Textnachbarschaft und keine neue visuelle Relationsevidenz.

## Nächster sinnvoller Schritt

Die nächste Runde sollte keine weiteren Bedeutungen frei erfinden, sondern
die vier exakt sichtbaren Entscheidungslücken mit schon zugelassenem Material
füllen:

1. mindestens zwei unabhängige Vorkommen mit Menge/Wert direkt **links** von
   `ol`, damit `aus` wirklich gegen die Nominalmodelle antreten kann;
2. eine zweite patientengestützte finale `ckhy`-Stelle;
3. eine zweite `ols`-Stelle mit rechtem Wert und einen unabhängigen Kontrast
   Resultat gegen Siebvorgang;
4. zusätzliche `otar`-Brücken, die Nominalfeld, allgemeine Folge und echten
   rechten Endpunkt auseinanderziehen.

Wenn der bereits zugelassene Cache solche Kontexte nicht enthält, ist genau
das die Information: Dann tragen diese 15 Zeilen die gewünschte
Ganzwortkonkretheit nicht, und die nächste freigegebene Viererseite muss diese
Kontraste liefern, statt nur mehr gleichartige Beispiele anzuhäufen.
