# Pass 1019 — visueller Kerncheck auf f13r und f88r

## Kurzes Ergebnis

Die Bilder tragen die breiten Pass-1018-Kerne insgesamt besser als die alten
engen Lesungen, aber nicht alle drei gleich stark:

- `OR = EINHEIT` ist die deutlichste Verbesserung auf beiden Seiten;
- `AIN = ANTEIL` passt auf f88r sichtbar besser als `PORTION`;
- `AIIN = WERT` ist die vorsichtigere Oberform, wird aber durch kein
  Messgerät, keine Zahl und keine Skala im Bild selbst identifiziert.

Die alten Wörter verschwinden nicht. Auf einer Apothekenseite darf `EINHEIT`
lokal **Ansatz/Charge**, `ANTEIL` lokal **Portion/Zutatenstück** und `WERT`
lokal **Maß/Dosis** werden. Der Vorteil ist, dass das Bild diese engere Wahl
nicht mehr vorwegnehmen muss.

## Was man auf den beiden Seiten sieht

Das vollständige Original von f13r (Yale-Objekt `1006098`, SHA-256
`454eb5f05db936ed0cf729c3881af0ded0993bc116246c6c8fd0c2789f4e9833`)
zeigt eine einzige große Pflanze. Besonders deutlich getrennt sind die
rotbraune Wurzel, mehrere helle runde Kronenstücke, breite Blätter und der
Blütenstand. Der Text steht oberhalb der Pflanze. Es gibt kein sichtbares
Gefäß, Gemisch, Maßgerät oder Dosierzeichen.

Das vollständige Original von f88r (Yale-Objekt `1037112`, SHA-256
`a1d21ccad0df430b47f3b3df2829bbefb8c4d1644cb70310e6d1de4b01c20013`)
zeigt drei hohe Gefäße, drei Reihen abgetrennter Wurzel-/Blattposten und drei
dazugehörige Prosablöcke. Gerade diese reiche Gliederung macht die breite
Lesung nützlich: Ein Textkern kann sich auf einzelnes Stück, Reihe,
Gefäßgruppe oder Charge beziehen, ohne dass jede Ebene vorab **Ansatz** heißen
muss.

Beide Originale wurden manuell in voller Auflösung betrachtet. Ausgewertet
wurden vier konkrete Pass-1018-Kontexte je Seite.

## OR: Einheit schlägt Ansatz

Auf f13r ist `ANSATZ` fast immer eine zusätzliche Geschichte. Das Bild besitzt
zwar einen ganzen Pflanzenartikel und klar erkennbare Unterteile, aber keine
Zubereitung. In `torshor ... opchor` und `tchor dor daiin ... okchor` lässt
sich `OR=EINHEIT` unmittelbar als Pflanzen-, Teil- oder Arbeitseinheit lesen.
Ein lokaler Ansatz bleibt möglich, stammt dann aber aus dem Werkstattkontext
und nicht aus der Zeichnung.

Besonders aufschlussreich ist `okorory` am Seitenende. Mit der alten Lesung
entsteht ungefähr **Ansatz in Ansatz setzen**. Mit der breiteren Lesung wird
daraus eine verschachtelte Zuordnung: einen gewählten Pflanzenteil in die
laufende Artikel- oder Arbeitseinheit setzen. Das ist einfacher und näher am
sichtbaren Besitzer.

Auf f88r ist **Ansatz** durchaus plausibler, denn Gefäße stehen sichtbar neben
den Stoffreihen. Trotzdem zeigt die Seite mehrere Ebenen zugleich. `OR` kann
eine Stoffgruppe, ein Gefäß oder die damit gebildete Charge aufnehmen.
`EINHEIT` hält diese Ebenen zusammen; **Ansatz** ist eine gute lokale
Expansion, nicht mehr der erzwungene Stammwert.

## AIN: Anteil schlägt Portion

Ein exakter `AIN`-Kontext kommt auf f13r in der aktuellen Ausgabe nicht vor;
dort darf deshalb keine künstliche Bildbestätigung erfunden werden. Auf f88r
ist der Kontext `oain or` dagegen sehr anschaulich. Direkt darüber liegen
getrennte Wurzeln und Blätter. Sie sind sichtbare **Anteile** einer
Stoffgruppe, aber nicht erkennbar abgewogen und nicht einmal zwingend mehrere
Stücke derselben Droge. `PORTION` setzt bereits eine Mengeninterpretation;
`ANTEIL` passt sowohl zu einem Zutatenstück als auch zu einer später bemessenen
Portion.

Die kurze lokale Lesung lautet deshalb:

> Einen Zutatenanteil bearbeiten und der laufenden Einheit zuordnen.

## AIIN: Wert ist besser, aber nicht im Bild bewiesen

Weder f13r noch f88r zeigt Zahlen, Waagen, Maßstriche oder eine klar
abgebildete Dosis. Darum trägt das Bild `AIIN=MASS` nicht direkt. Es trägt aber
auch `AIIN=WERT` nicht als sichtbares Ding. **Wert** ist hier besser, weil es
die Art der Eintragung offenhält: Arbeitswert auf f13r, Mengen- oder
Dosierwert auf f88r. In einer flüssigen lokalen Kräuter- oder Apothekenlesung
darf daraus weiterhin **nach Maß** werden.

Die passende Hierarchie ist:

> `AIIN = WERT` → lokal `Mengenwert / Dosierwert` → flüssig `nach Maß`.

Der Fehler der alten Fassung war also nicht das Wort **Maß** im fertigen
Apothekensatz. Der Fehler war, **MASS** bereits als unveränderlichen Kern über
jeden Bildbesitzer zu legen.

## Beste kurze Lesungen

Für f13r ergibt sich aus den geprüften Stellen:

> Die bezeichnete Pflanzeneinheit nach dem eingetragenen Wert einstellen,
> einen Teil nehmen und den Folgegang setzen. Den nächsten sichtbaren Teil der
> laufenden Einheit geben; offen weiterführen.

Für f88r:

> Einen Zutatenanteil bearbeiten und der laufenden Einheit zuordnen. Den
> angegebenen Wert übernehmen, aus der Einheit einen Teil nehmen und die
> nächste Einheit im bezeichneten Grad weiterführen.

## Schluss

Pass 1018 geht optisch in die richtige Richtung. Die beste Ordnung lautet:

> portabler Kern: `EINHEIT / ANTEIL / WERT`
>
> lokale Apothekenfassung: `Charge oder Ansatz / Zutatenportion / Maß oder Dosis`

So bleibt f13r ein Pflanzenartikel, ohne zum unsichtbaren Labor zu werden, und
f88r darf weiterhin konkret pharmazeutisch klingen, ohne jede sichtbare
Gruppierung auf dieselbe Zubereitungsart zu reduzieren.
