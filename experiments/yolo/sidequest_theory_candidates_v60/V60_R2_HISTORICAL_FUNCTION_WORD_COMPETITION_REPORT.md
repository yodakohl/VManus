# V60 R2 — Historischer Funktions- und Wortartenwettbewerb

## Ergebnis

Der Ganzkarten-Drucktest über alle **85 exakten Vorkommen** trägt neun der elf
kanonischen V59-R1-Merkwörter weiter. Zwei Lesungen werden enger und
werkstattsprachlich sparsamer gefasst:

- `OLOR`: **ZUVOR? → VORIGES?**
- `OTCHEY`: **TEIL? → NIMM?**

Dies ist keine Entzifferung und keine Laut- oder Sprachzuweisung. Die deutschen
Wörter sind kurze Funktionsmerker für eine um 1420 denkbare Rezept-, Bad- oder
Arbeitsvorlage. Die vorhandenen flüssigen V59-Sätze dienen ausschließlich als
Kontextdruck; sie werden nicht rückwärts in einzelne Karten hineingelesen.

## Prüfregel und Abdeckung

Gebunden wurde ausschließlich die ungeteilte sichtbare Karte über ihre exakte
`joint_tuple_id`. Weder PAGE_HOST-Werte noch Teilstrings, Nachbarschaftsstücke
oder Zeichenklänge wurden semantisch übertragen. Für jedes Vorkommen wurden das
vollständige Feld, linke und rechte Nachbarschaft, Feldposition, Record/Register
und der formale Schlussstatus geprüft.

Die 85 Belege verteilen sich wie folgt: `AIIN` 20, `OKY` 10, `CTHY` 7, `OR` 7,
`AL` 10, `EY` 4, `OLOR` 2, `OTCHEY` 2, `OKEEY` 7, `OKE` 8 und `LCHE` 8. Der
zeilenweise Nachweis steht in `V60_R2_85_OCCURRENCE_AUDIT.tsv`.

## Entscheidungen

| Karte | V60-Merker | Wortart/Funktion | Zwei atomare Rivalen | Entscheidung | Konfidenz | stärkster Allvorkommens-Gegenbeleg |
|---|---|---|---|---|---:|---|
| AIIN | MASS? | Substantiv/Maßsigle | VORGABE?, MENGE? | KEEP | .58 | Keine Einheit oder Skala ist sichtbar; die breite Positionsmobilität passt ebenso zu einem bloßen Wertslot. |
| OKY | VERWENDEN? | Verb | NEHMEN?, ANWENDEN? | KEEP | .60 | Das Objekt bleibt überall bild- oder exemplarabhängig; besonders im Bio-Register könnte nur „ausführen/fortsetzen“ gemeint sein. |
| CTHY | BEREIT? | Zustandsadjektiv/Temporalprädikat | DANN?, FERTIG? | KEEP | .48 | Mehrere Belege liegen mitten im Ablauf, einmal sogar vor `OR`; ein rein formaler Statusslot bleibt fast gleich stark. |
| OR | BEREITUNG? | Sachnomen | FLÜSSIGKEIT?, POSTEN? | KEEP | .42 | Die unmittelbare Doppelung auf f10r macht „Bereitung Bereitung“ sprachlich schwer und trennt Präparat nicht von Arbeitskategorie. |
| AL | AN? | Präposition/Relationspartikel | DORT?, DAZU? | KEEP | .43 | Vier FIRST-, zwei LAST- und ein ONLY-Beleg verlangen ein unsichtbares Komplement; DORT wäre selbstständiger. |
| EY | KLAR? | Zustandsadjektiv | FERTIG?, SAUBER? | KEEP | .39 | Einer von nur vier Belegen steht ohne sichtbaren Klärvorgang zwischen Zusatz und Anteil. |
| OLOR | VORIGES? | anaphorisches Pronomen/substantiviertes Adjektiv | DAVON?, ZUVOR? | **REVISE** | .36 | Nur zwei Belege und kein ausgeschriebener Antezedent; zeitlicher und anaphorischer Rückverweis bleiben kaum trennbar. |
| OTCHEY | NIMM? | Rezeptimperativ | TEIL?, DIES? | **REVISE** | .44 | Nur zwei Belege; ein markierter Gegenstand oder eine formale Auswahl kann die gleiche feldinitiale Stellung tragen. |
| OKEEY | WARM? | Temperaturadjektiv | LAUWARM?, ERWÄRMEN? | KEEP | .52 | Nur Bio-Belege und kein unabhängiges Temperaturzeichen; technische Prozesslesungen bleiben möglich. |
| OKE | SPÜLEN? | terminales Handlungsverb | WASCHEN?, SCHLIESSEN? | KEEP | .31 | Alle 8/8 Belege sind formal `CLOSE`; Tätigkeit und bloßer Schlusswert sind vollständig konfundiert. |
| LCHE | ABLASSEN? | terminales Handlungsverb | LEEREN?, SCHLIESSEN? | KEEP | .34 | Ebenfalls 8/8 `CLOSE`; nicht an jedem Ort ist ein sichtbarer Ablauf vorhanden. |

`KEEP` bedeutet nur, dass innerhalb dieses Wettbewerbs kein Rivale klar besser
passt. Das Fragezeichen bleibt Bestandteil jeder explorativen Lesung.

## Warum die zwei Revisionen sparsamer sind

### OLOR → VORIGES?

Auf f10r steht `OLOR` innerhalb einer Folge aus Verbindung/Arbeitsansatz und
erneuter Verbindung; auf f81v eröffnet es ein Feld, das anschließend den
laufenden Ansatz weiterführt. Beide V59-Expansionen mussten bereits „aus dem
vorigen Ansatz“ ergänzen. **VORIGES?** bezeichnet daher knapper den anaphorisch
übernommenen Bestand als das lediglich zeitliche **ZUVOR?**. Eine Werkstatt kann
ein solches Ganzzeichen wie *praedictum* oder *idem* aus einem Exemplar lernen.
Diese lateinischen Wörter sind nur historische Funktionsvergleiche, keine
behaupteten Äquivalente oder Lautwerte. Wegen `n=2` bleibt die Konfidenz gering.

### OTCHEY → NIMM?

Beide Vorkommen sind feldinitial. Auf f56r folgt eine Objekt-/Blütenkarte und
`AIIN`; auf f83r folgen ein Wärmezustand und ein Gebrauchsverb. Die bisherigen
flüssigen Lesungen setzten in beiden Fällen bereits den nicht kartengebundenen
Imperativ „Nimm …“ ein. **NIMM?** macht diese Quellenfunktion sichtbar und
vermeidet zugleich, **TEIL?** als schweigendes Objekt plus ein zusätzliches
schweigendes Verb auszubauen. Als unteilbarer Brevigraf wäre eine
*recipe*-ähnliche Anfangsformel in einer Rezeptwerkstatt lehrbar. Dennoch kann
die Karte bei nur zwei Belegen ebenso „Teil“ oder „dies“ markieren.

## Historischer Werkstattdruck

Die Gewinner besitzen die passende Größenordnung für kurze Rubrik- und
Rezeptfunktionen: Maß-/Mengenhinweis, Gebrauchsverb, Zustandsprädikat,
Präparatnomen, Zielrelation, Qualitätszustand, Rückverweis, Anfangsimperativ,
Temperaturstatus und zwei Schlussoperationen. Vergleichbare Funktionsbereiche
lassen sich mit den lateinischen Schreiberbegriffen *mensura/quantitas*,
*utere/applica*, *paratus*, *praeparatio/confectio*, *ad*, *clarus*,
*praedictum/idem*, *recipe*, *calidus/tepidus*, *lavare/abluere* und
*effundere/evacuare* beschreiben. Das begründet allein historische
Werkstattplausibilität; es weist dem Voynich-Zeichenbestand weder Latein noch
eine Aussprache zu.

Am belastbarsten ist die registerübergreifende, positionsflexible Funktion von
`AIIN` und `OKY`, nicht deren konkreter Wortlaut. `OKEEY` ist als
Bio-Temperaturstatus brauchbar, bleibt aber registerlokal. `AL` überlebt nur als
elliptische Bild-/Rubrikrelation. `EY`, `OR`, `OKE` und `LCHE` werden nicht
hochgestuft: Bei `OKE`/`LCHE` verhindert insbesondere die perfekte
Terminalkonfundierung jede sichere medizinische Differenzierung.

## Revision und Validierung

Das revidierte 173-Karten-Wörterbuch bewahrt Oberflächen, exakte IDs und alle
formalen Werte. Das revidierte 381-Ereignis-Ledger bewahrt Reihenfolge,
Kontexttexte und nichtmedizinische Rivalen; nur die vier exakten Ereignisse der
beiden revidierten Karten ändern ihren Merker. Damit bleiben 81 weitere
Zielereignisse und alle 296 Nichtzielereignisse unverändert.

`V60_R2_VALIDATION.json` meldet **PASS**: 11 Entscheidungen, 85 geprüfte
Zielvorkommen, 173 Wörterbuchkarten und 381 Prosaereignisse; genau ein Gewinner
und zwei Einwort-Rivalen je Karte; 9 KEEP, 2 REVISE; keine formalen oder lokalen
Textänderungen außerhalb der vier exakten Marker. Die Guards melden null
f84/f84r-Zugriffe, null neue Seiten und null gelesene V60-Geschwisterdateien.
