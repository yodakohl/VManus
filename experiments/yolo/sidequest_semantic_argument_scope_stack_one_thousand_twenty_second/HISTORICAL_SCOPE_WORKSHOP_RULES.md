# Historische Scope-Tafel: acht Bindungsregeln

## Die nächste Werkstattanalogie um 1420

Unser System passt am ehesten zu einer **Mischung aus Bildzettel,
Rezeptkurzschrift und Tabelle**. Der Schreiber setzt nicht in jede Kurzform
nochmals Besitzer und Verb. Er hält beides im Kopf, bis eine sichtbare Grenze
es ersetzt.

- Im norditalienischen Kräuterbuch [LJS 419](https://openn.library.upenn.edu/Data/0001/html/ljs419.html)
  stehen kurze Zubereitungsnotizen um und sogar über dem Pflanzenbild. Das
  Bild kann damit den stummen Besitzer mehrerer Textstücke liefern.
- Im nordostitalienischen [Wellcome MS.683](https://wellcomecollection.org/works/w6ne7k4t)
  eröffnet eine Überschrift wie *Unguentum pro stomaco* einen Block, einmaliges
  *Recipe* trägt den Handlungsauftrag über eine Zutatenreihe, *ana grani ij*
  gibt mehreren Gliedern denselben Wert, und ein abschließendes *fiat
  pessarium* fasst die vorhergehenden Glieder zum Ziel zusammen.
- [Wellcome MS.418](https://wellcomecollection.org/works/f6nzyzh4) beginnt eine
  ganze Wasserfolge mit Rubrik und *modus quomodo debent fieri*, danach folgen
  einzelne Wasserüberschriften und jeweils ein knappes *Recype*. Rubrik,
  Einzelbesitzer und Handlung liegen also auf verschiedenen Ebenen.
- Die Kalender-, Rechen- und Medizintafeln des um 1425 angelegten
  [Wellcome MS.8515](https://wellcomecollection.org/works/w9nkm98w) liefern das
  Layoutmodell: Eine Überschrift oder Spalte gilt für die Kurzwerte darunter,
  statt in jedem Feld wiederholt zu werden. In zeitnahen Rechnungen tragen
  *idem*, *eodem* und *ut supra* denselben Gedanken ausdrücklich weiter, etwa
  in den [Durhamer Rechnungsrollen](https://quod.lib.umich.edu/c/cme/CME00048/1%3A2?rgn=div1&view=fulltext).

Das ergibt keine Zeile-für-Zeile-Prosa, sondern einen kleinen Scope-Stapel:

```text
BESITZER [ GANG [ PAKET [ HANDLUNG [ POSTEN / WERT / ANTEIL / EINHEIT ]
                                  [ AUSGANG / VERBINDUNG / LAUF / ZIELORT ]
                                  [ GRAD / STUFE ] ] ] ] ]
```

## Acht Regeln für den Lehrling

1. **Der sichtbare Besitzer trägt vorwärts.** Bild, Gefäß, Station oder Rad
   gilt für alle folgenden Kurzformen, bis ein neuer sichtbarer Besitzer
   beginnt. Ein Zeilenende allein beendet weder Besitzer noch Aussage.

2. **Beginn und Schluss betreffen den Gang, nicht sofort den Besitzer.**
   `CARRIER_Q` eröffnet unter dem laufenden Besitzer einen Gang. Nur ein
   lizenziertes `DY` schließt diesen Gang; der Bildbesitzer bleibt bis zur
   nächsten sichtbaren Besitzergrenze verfügbar.

3. **Zuerst das ganze Paket, dann die Nachbarschaft.** Greife die längste
   gelernte Form und öffne erst danach ihre Kerne. Darum ist `CHK = CH|K`
   linear, `CKH = C<K>H` dagegen eingeschoben. Auch zwei gleiche Kerne werden
   zuerst nach Paketgrenze oder freier Wiederholung gelesen. Die Paketgrenze
   entscheidet, welchem Handlungskopf ein Zusatz gehört.

4. **Ein Handlungskopf eröffnet das laufende Verb.** `OK`, `CH`, `SH`, `K`,
   `S`, `T`, `CHD`, `R` oder `P` trägt seine Handlung über die anschließenden
   kurzen Zusätze. Ein neuer Handlungskopf ersetzt ihn; Besitzergrenze oder
   lizenziertes `DY` beendet seine Reichweite.

5. **Fehlt der Handlungskopf, wird er örtlich ergänzt.** Eine Kurzform ohne
   eigene Handlung übernimmt die zuletzt laufende Handlung desselben Gangs und
   Besitzers. `OL` setzt genau diesen Gang fort. `OT` eröffnet den nächsten
   Schritt: folgt dort ein neuer Handlungskopf, gilt der neue; folgt nur ein
   Zusatz, gilt die geerbte Handlung weiter.

6. **Posten und Maße suchen zuerst ihr eigenes Paket.** `Y`, `AIIN`, `AIN` und
   `OR` binden an einen Handlungskopf im selben Paket, gleich ob sie davor oder
   danach stehen. Fehlt dort einer, binden sie rückwärts an die laufende
   Handlung. Sie springen nie über einen neuen Handlungskopf, ein lizenziertes
   `DY` oder eine Besitzergrenze. So bleiben `CH+AIN`, `P+AIN` und `P+AIIN`
   ohne Sonderregel lesbar.

7. **Beziehungen haben eine feste Seite.** `AR` und `AL` hängen als AUSGANG
   und ZIELORT an der Handlung links von ihnen. `L` und `AIR` bilden dagegen
   einen VERBINDUNGS- oder LAUFRAHMEN für die eingeschlossene beziehungsweise
   unmittelbar folgende Handlung. Kein Beziehungszeichen erfindet ein
   ausgelassenes Ding oder eine Richtung.

8. **Grad und Stufe verändern nur eine Handlung.** `E`, `EE`, `EEE`, `IIN`,
   `DA` und das ausführende `O` binden zuerst an den Handlungskopf ihres
   Pakets. Gibt es dort keinen, gelten sie für die laufende Handlung desselben
   Gangs; nach `OT` also gewöhnlich rückwärts für den fortgeführten Auftrag.
   Sie werden nie selbst zum Verb und reichen nicht über `DY` oder eine neue
   Besitzergrenze.

## Lehrmeisterprobe

Der Lehrling fragt bei jeder Kurzform nur:

```text
Welcher Besitzer? — Welcher Gang? — Welches Paket? — Welche Handlung?
```

Erst dann hängt er POSTEN, WERT, ANTEIL, EINHEIT, Beziehung, Grad und Stufe
an. Damit darf eine Aussage über mehrere Zeilen laufen, eine Bildkennung darf
mehrere Aussagen besitzen, und eine knappe Folge muss Besitzer oder Verb nicht
jedes Mal ausschreiben. Das ist genau die Art von Sparsamkeit, die Bildherbar,
Rezeptblock, Rechnungseintrag und Tabelle einem Werkstattleser um 1420 bereits
vertraut machen konnten.
