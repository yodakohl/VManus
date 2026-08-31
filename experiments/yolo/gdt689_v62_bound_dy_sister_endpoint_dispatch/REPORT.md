# GDT689 — V62 bound-`dy` sister dispatch

## Ergebnis

V62 liefert einen einfacheren und praktisch besseren Code für die bisher
verstreuten `dy`-Ganzwortentscheidungen:

| Arbeitsklasse | Formen | aktuelle Positionen | gesprochener Zusatz |
|---|---:|---:|---|
| `RESULT_PARTICIPLE` | 25 | 36 | derselbe Kern als erreichter Zustand |
| `FIELD_END` | 12 | 14 | keiner; Schwesterwert wird übernommen |
| `ACTION_TELICITY` | 0 | 0 | derzeit nicht benötigt |
| `PAIR_INVALID` | 1 | 1 | kein Suffixschluss |
| `UNPAIRED_WHOLE_RETAINED` | 22 | 23 | gelernte Ganzform bleibt |

Das Modell ändert 47 Positionen über bedeutete Schwesterköpfe und drei
`cheody`-Positionen über den parseridentischen Nullfall, zusammen auf 25 der
51 aktuellen Readerzeilen. Es
reduziert die geschriebenen Aktionspositionen von 85 auf 83, weil `olchdy`
und `dshedy` nicht länger ohne Schwesterstütze zu Befehlen gemacht werden. Die
praktische Ausgabe enthält 115 Verben; alle 115 besitzen weiterhin einen
exakten Zeichenspan innerhalb genau eines geschriebenen Aktionsordinals.

## Die entscheidende Trennung

Die Zeichenfolge `dy` und das formale Parseratom `DY` sind nicht dasselbe:

| exakter Parserstatus | Formen | aktuelle Positionen |
|---|---:|---:|
| durchgängig formales `DY` | 24 | 30 |
| gemischte Rezepte mit und ohne `DY` | 2 | 3 |
| sichtbares `dy`, aber kein formales `DY` | 17 | 24 |
| Rezept ungeklärt | 17 | 17 |

Die acht vollständigen GDT624-Qualitätsraster-Paare sind mit der gewählten
Resultatlesung konsistent, obwohl nur vier davon ein formales `DY` besitzen.
Drei haben explizit kein solches Atom, eines ist ungeklärt. Das Raster selbst
belegt jedoch nur `d_bit` und Zustandsbindung; es identifiziert nicht das Wort
„Resultat“ oder ein Partizip.

## Warum 39 Nachbarn nur 36 Schwesterköpfe liefern

Die mechanische Operation `...dy → ...y` findet 39 card-backed Nachbarn.
Zwei dürfen nicht als Bedeutungsminimalpaare zählen:

- `dchedy = D_ADDR+CHD+Y`, aber `dchey = CH+E+Y`; der Parser ändert sich
  vollständig.
- `ypcheddy → ypchedy` lässt die Schwester selbst auf `dy` enden und isoliert
  daher keinen nicht-`dy`-Kern.

Von den übrigen 37 Paaren besitzen 36 beidseitig einen V48-Arbeitswert.
`cheoy` ist zwar real und parseridentisch zu `cheody`, hat aber keinen
unabhängigen V48-Gloss. Es wird deshalb separat als Parser-Nullfall geführt;
seine drei Revisionen verwenden `cheody`'s eigenen Ziel-Ganzwortwert und
behaupten keinen Schwesterkopf.

## Was der Schwestervergleich trägt

Auf den 36 scorebaren Paaren bleibt die grobe Aktions-/Nichtaktionsklasse in
31 Fällen gleich. Die bloße Resultatmehrheit träfe 28. Im auf die aktuellen
Readerseiten vorgefilterten Vergleich nach Sektion, Sprachregister, Hand und
physischer Zeilenposition bleiben 21 Zellen mit 24 Zielpositionen und 215
Schwesterpositionen. Alle 24 sind Resultat/Nichtaktion; dieses Teilpanel trägt
daher die resultative Mehrheit, kann aber `ychedy` nicht separat prüfen.

Die maschinenbaubare Regel „gleiches Rezept oder bereits endpunktgebundene
Schwester → FIELD_END, sonst RESULT_PARTICIPLE“ reproduziert 36/37
Entscheidungen. `ychedy` bleibt die einzige Ausnahme: Sein nominaler Zielwert
und die Aktionsschwester werden zu „bis zur Mittelstufe getrocknet und
abgeschlossen“ vereinigt. Das ist ein ausdrücklich in-sample gewählter
Ganzwortentscheid, keine gehaltene Prognose.

Das ist kein Universalbeweis, aber eine bessere Kompositionsregel als die
alten unabhängig gelernten Ganzwortglossen: zuerst Schwesterkern bewahren,
danach höchstens Resultat hinzufügen.

## Konkrete Verbesserungen

### `olchdy / olchy`

Die Schwester `olchy` trägt Holzdroge, Ansatz und Trocknung. V61 machte daraus
bei `olchdy` den generischen Befehl „Trockenstoff vollständig trocknen“ und
verlor Materialkopf und Ansatz. V62 liest:

> Holzdroge im Ansatz fertig getrocknet.

### `olshedy / olshey`

Die alte Zielkarte wechselte von einer Drogenbasis zu Holzdroge. V62 erhält
den Schwesterkopf:

> bis zur Mittelstufe eingeweichte Drogenbasis, abgeschlossen.

### `solchedy / solchey`

Aus dem Saatgutansatz wurde zuvor ein neuer „Saatgutstoff“. V62 liest:

> bis zur Mittelstufe fertig getrockneter Saatgutansatz.

### `qoeedy / qoeey`

Der alte Zielwert ersetzte die Endportion durch einen vollständig fertigen
Ansatz. Da `qoeedy` formal gar kein `DY` trägt, übernimmt V62 die
Schwesterhandlung ohne Zusatz:

> nimm die Endportion hinzu.

### `ychedy / ychey`

Die Schwester schreibt Trocknung bis zur Mittelstufe und Abschluss. Das Ziel
bleibt die nominale Resultatform, verliert aber das frei erfundene Genre-Wort
„Eintrag“:

> bis zur Mittelstufe getrocknet und abgeschlossen.

## Drei Null- und Schutzfälle

- `cheody/cheoy` besitzt beidseitig exakt `CH+E+O+Y`. Das sichtbare `d` trägt
  hier weder formales `DY` noch einen gesprochenen Zusatz. Weil `cheoy` keinen
  eigenen Gloss hat, bleibt `getrockneter Ansatz` ausdrücklich `cheody`'s
  eigener Ganzwortwert.
- `dchedy/dchey` bleibt parser-invalid und wird nicht passend gemacht.
- 22 unpaarige oder unbewertete Formen behalten ihre Ganzwortlesung. Ein
  nützlicher Paarcode darf diese Lücken nicht mit einer erfundenen
  Universalbedeutung füllen.

## Readerstand

Der vollständige V62-Reader umfasst weiterhin 51 Zeilen und 479 geschriebene
Positionen. Die 47 Schwester- und drei Parser-Null-Änderungen stehen einzeln
mit Seite, Locus, Ordinal,
Surface, Schwester, Vorher/Nachher und Parserstatus in
`artifacts/V62_50_POSITION_REVISIONS.tsv`. Die Schuldenstände bleiben bewusst
106 strikt, 152 in der mechanischen Union und 330 in der Vier-Schichten-Union:
V62 korrigiert Komposition, bestätigt aber noch keine historische
Wortidentität.

## Grenze und nächster Hebel

V62 ist eine konkrete Arbeitsübersetzung, keine Entzifferung. Es zeigt aber,
wie die nächste Runde arbeiten muss: nicht weitere Ganzwörter frei erfinden,
sondern überkonkrete Stoff- und Objektköpfe gegen ihre sichtbaren Familien
zurückbinden. Besonders `Gummiharz`, `Blüten-/Fruchtstand`, `Wurzel`,
`CTH-Drogenmaterial`, `qo-Rahmen` und `Holzbindung offen` müssen in Hauptwert
und Unsicherheitsapparat getrennt werden, ohne neue Seiten zu öffnen.
