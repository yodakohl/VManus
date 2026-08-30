# GDT664 — 140 Restformen als konkrete V41-Werkstattlesung

Status: `PASS_1141_TARGET_POSITIONS__V41_CONCRETE_RECIPE_REGISTER`

## Ergebnis

GDT664 gibt allen 140 neu exponierten Oberflächen eine konkrete, ersetzbare
Bedeutung. Die 1.141 Vorkommen liegen auf 991 Zeilen und 166 Seiten. Alle 146
V40-Ein-Loch-Zeilen, aus denen die Karten gewonnen wurden, sind jetzt
vollständig lesbar. Der unabhängige Replay besteht `10.232/10.232` Prüfungen.

| Größe | V40 | V41 | Änderung |
|---|---:|---:|---:|
| bekannte Tokenstellen | 20.417 | 21.558 | +1.141 |
| unbekannte Tokenstellen | 11.922 | 10.781 | −1.141 |
| vollständige Mehrtokenzeilen | 449 | 613 | +164 |
| davon leserstabil | 147 | 185 | +38 |
| Ein-Loch-Zeilen | 333 | 332 | −1 |
| Arbeitsglossar | 734 | 874 | +140 |
| Wörterbucheinträge | 976 | 1.266 | +290 |

Die zusätzlichen 290 Wörterbucheinträge bestehen aus 140 Oberflächenkarten
und 150 occurrence-spezifischen Renderern. Das ist keine Behauptung von 290
neuen Wörtern: die Renderer lösen nur Lesergrenzen, Labels und Satzpositionen.

## Die entscheidende Stammkorrektur

Die alte Fassung behandelte fast jedes `ol*` als unteilbare „Drogenbasis“.
GDT664 liest die 19 materialgebundenen Formen stattdessen als
`O_PREP + L_WOOD + Rest`: Ansatzrahmen plus Holzdroge. Das ändert 256 bereits
übersetzte Stellen und sagt die neuen dichten Familien direkt voraus:

- `lchedy → olchedy`: getrocknete Holzdroge → Holzdroge im Ansatz fertig
  getrocknet.
- `lkeey → olkeey`: vollständig erhitzte Holzdroge → vollständig erhitzter
  Holzdrogenansatz.
- `lshedy → olshedy`: eingeweichte Holzdroge → Holzdroge im Ansatz vollständig
  eingeweicht.
- `pchedy → opchedy`: fertiges Trockenpulver → fertiges Trockenpulverpräparat
  im Ansatz.
- `rchedy → orchedy`: getrocknete Wurzeldroge → Portion vollständig
  getrocknete Droge.

Drei Ausnahmen bleiben ausdrücklich gelernt: nacktes `ol=Grundansatz`,
`oly=abseihen` und `olyly=nochmals abseihen`. Damit wird kein bequemer
Substring-Wert über sichtbare Ganzwörter gebügelt.

Der manuelle Passagenaudit fand außerdem einen alten Widerspruch: `sol` war 57
Mal Saatgut, aber `solaiin` und `sols` waren als Salz übersetzt. V41 vereinigt
die Familie als Saatgutansatz (`solaiin=drei Teile Saatgutansatz`,
`sols=fertiger Saatgutansatz`, `solor=eine Portion Saatgutansatz`,
`solkeedy=Saatgutansatz vollständig erhitzt`). Salz bleibt nur der sichtbare
Rivale.

## Kurze Formen und Lesergrenzen

`o`, `ch`, `qok`, `m` und `sa` werden nicht blind als isolierte Wörter gelesen.
Eine Zusammenschreibung gilt nur, wenn IT2a oder RF1b sie an derselben lokalen
Position trägt. Ein gleich geschriebenes Wort irgendwo anders in der Zeile
reicht nicht.

| Form | Stellen | lokaler Merge | freier Default |
|---|---:|---:|---|
| `o` | 146 | 88 | 47× Ansatzwasser; 11× Ansatzzeichen |
| `ch` | 13 | 5 | 8× „trockne“ |
| `qok` | 13 | 4 | 9× „erhitze“ |
| `m` | 6 | 3 | 3× „eine Handvoll“ |
| `sa` | 3 | 1 | 2× „gib Saatgut zu“ |

Die drei `o`-Stellen in der 146-Zeilen-Front sind alle Merges:
`f21r.3 o|l→ol`, `f75v.68 o|cthey→octhey`, `f78r.18 o|l→ol`. Sie stützen also
nicht den freien Versuchswert `o=Ansatzwasser`. Dieser darf explorativ stehen,
aber er ist von diesen drei Stellen unabhängig.

## Konkrete neue Karten

Der V41-Stammzettel enthält 36 explizit gescopte Zeilen. Die wichtigsten
Werkstattwerte sind nun:

- Stoffe: Saatgut, Saatrohstoff, Kraut-/Blattdroge, Wurzel, Holzdroge,
  Blütenfraktion, Pulver, Rohdroge und Ansatz.
- Handlungen: trocknen, einweichen, erhitzen, abkühlen, abmessen, zugeben,
  abgießen, ausziehen, abseihen, abfüllen und abschließen.
- Mengen: erster/zweiter Bruch, Portion, zwei/drei Teile, Maß, Handvoll, Gran
  und Bündel.
- Produkte: Trockenansatz, Feuchtansatz, Holzabsud, Wurzelauszug,
  Saatgutansatz, Pulverpräparat und eingedickter Holzdrogenauszug.

`m=eine Handvoll` ist eine freie, nicht exportierte Siglenkarte. `am=ein Maß`
bleibt separat. `-g=ein Gran` gilt nur in den drei gelernten Ganzformen
`chkag`, `kcharg`, `chokolg`; es wird nicht auf andere g-Endungen übertragen.
`b` erhält weiterhin keinen Stammwert: `oleeeb=stark eingedickter
Holzdrogenauszug` bleibt ein LOW-Ganzwort, während „Bad“ als Rivale erhalten
ist.

## Was die Übersetzung jetzt tatsächlich sagt

Der automatische Kanal bleibt absichtlich eine prüfbare Tokenfolge. Die 30
manuell geglätteten Passagen sind die lesbare Werkstattfassung. Beispiele:

`f103v.17`

> Erhitze vollständig, trockne bis zur Mittelstufe und kühle ganz ab. Schließe
> den Kaltansatz; erhitze die Holzdroge mäßig, weiche bis zur Mittelstufe ein
> und gib eine leicht erhitzte Portion Rohdroge in den Grundansatz. Füge die
> erste Trockenfraktion und eine leicht gekühlte Portion Rohdroge hinzu; rühre
> zuletzt das fertige Trockenpulver ein.

`f107r.44`

> Nimm zwei Dosen Trockenansatz, erhitze bis zur Endstufe, koche vollständig
> aus und halte anschließend auf Heizstufe III.

`f47r.5`

> Nimm zwei Maße Holzdrogenansatz, weiche ihn bis zur Mittelstufe ein und gib
> ein Gran heißen Trockenabsud hinzu.

`f6v.11`

> Nimm eine Holzportion und die erste Trockenfraktion, vermische sie mit einem
> Maß kalten Ansatzes und einer Handvoll Krautansatz und schließe ab.

`f78r.18`

> Trockne den Grundansatz bis zur Mittelstufe und erhitze auf Stufe II. Miss die
> erste Fraktion ab, gib die erste Drogenfraktion hinzu und erwärme den Ansatz
> nochmals mäßig.

Das ist erstmals durchgehend konkrete Rezeptprosa. Sie benennt jedoch noch
keine bestimmte Pflanze, Krankheit oder Trägerflüssigkeit. Diese Inhaltsnamen
müssen auf späteren Seiten aus den noch offenen Slots kommen; sie dürfen nicht
aus „Rohdroge“ oder „Ansatz“ herbeigeschrieben werden.

## Historische Vergleichbarkeit

Wellcome MS 683 zeigt für die Mitte des 15. Jahrhunderts genau den passenden
Registertyp: Zutaten, Öle, Salben, Pulver, Pillen, Einweichen und kompakte
Kornmengen stehen nebeneinander. Eine historische Maßtabelle führt
*manipulus* „Handvoll“ mit `man/manp/manip`, selten auch `m`. Das macht
Handvoll- und Gran-Karten zeittypisch; es identifiziert keine Voynich-Glyphe.
Details und Links stehen in `HISTORICAL_ANALOGUES.md`.

## Arbeitsstand

Die stärkste neue Basis ist damit:

1. gemischtes Rezeptregister aus produktiven Stämmen und gelernten
   Ganzwörtern;
2. `O_PREP + L_WOOD` als produktive Holzdrogenansatz-Familie;
3. `S/SAL/SOL` als Saatfamilie;
4. kurze Siglen nur occurrence-sensitiv;
5. konkrete Werkstattlesung getrennt vom unveränderten strukturellen Tag.

Die LOW-Karten bleiben sichtbar: freies `o=Ansatzwasser`, `m=Handvoll`, die
drei Gran-Ganzwörter, `cfhar`, `oeeesoy`, `okaial`, `oleeeb`, `qoeeeety`,
`qykaiin`, `ychklkaiin` und `ykanam`. Sie bleiben stehen, bis eine spätere Seite
eine bessere Bedeutung liefert oder sie unmöglich macht.
