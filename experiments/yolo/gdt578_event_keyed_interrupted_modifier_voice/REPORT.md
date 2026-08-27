# GDT578 — die unterbrochenen Modifier haben jetzt lokale Köpfe

## Ergebnis

`PASS_5_ATTACHMENT_CLASSES__3_PROSE_FRAMES__20_HEAD_VOICES__58_EVENT_CARDS__60_GROUPS__121_REPEAT_SLOTS__173_ORDERED_MODIFIER_FRAGMENTS__61_PARTICLES__5122_EXACT_ROUNDTRIPS__ONE_CONFLICT_UNCHANGED`.

GDT578 setzt den Atlas aus GDT577 tatsächlich in die vollständige Arbeitsausgabe
ein. 60 konfliktfreie Wiederholungsgruppen mit 121 geschriebenen Slots liegen
in 58 Ereignissen. Sie werden nicht mehr als abgetrennter Modifierblock gelesen,
sondern an ihren lokalen Handlungskopf zurückgebunden.

```text
CH+E+T+E+LOCAL_CHAR_G
Nimm ...; beim Nehmen: auf Grad I;
beim Einstellen: ebenfalls auf Grad I; mit der g-Variante.

O+P+O+AM_ADDR
Setze ... ein; beim Einsetzen: als Ausführung;
beim Einsetzen: erneut als Ausführung; an der AM-Stelle.
```

Damit sagen die beiden gleichen Grade oder Ausführungsmarker nicht mehr nur
„dasselbe zweimal“. Man sieht, ob sie zwei verschiedene Handlungen begleiten,
einen Kopf umklammern oder unter einem fortgeführten Kopf stehen.

## Fünf Anschlussklassen, nur drei Proserahmen

Die 121 Slots verwenden genau die fünf GDT577-Topologien, aber deren deutsche
Oberfläche reduziert sich auf drei Rahmen: `beim {Handlungskopf}: ...`,
`beim fortgeführten {Handlungskopf}: ...` und `bei der Fortsetzung: ...`.

| Anschlussform | Slots | Stimme |
|---|---:|---|
| verschiedene Handlungsvorkommen | 71 | `beim Nehmen ...; beim Einstellen ebenfalls ...` |
| Klammer um denselben Kopf | 30 | zweimal beim selben Kopf, in geschriebener Slotfolge |
| gleicher Kopf, gleiche Seite | 6 | zwei geordnete Angaben vor oder nach demselben Kopf |
| aktiver Kontextkopf | 12 | `beim fortgeführten Nehmen: ...` |
| Handlung plus Fortsetzungsträger | 2 | erste Stelle bei der Handlung, zweite bei OL |

Die Köpfe stammen aus zwanzig bereits vorhandenen GDT568-Handlungsstimmen.
PRE_HEAD und POST_HEAD bleiben in der Anschlusstabelle getrennt, werden aber
nicht als zeitliches „vor/nach der Handlung“ übersetzt: Schriftlage allein
belegt noch keine Prozesschronologie.

Wenn dieselbe Wurzel mehrfach im Ereignis steht, wird auch die konkrete
Occurrence genannt:

```text
G407-E0628
... beim ersten Wählen: auf Grad I;
beim ersten Wählen: erneut auf Grad I;
... beim zweiten Wählen: nochmals auf Grad I.
```

Das ist wichtig: `S ... S` besitzt zwei sichtbare Wähl-Handlungen; ein bloßes
„beim Wählen“ hätte die neue Bindungsinformation wieder versteckt.

## Alle geschriebenen Teile bleiben erhalten

Die 58 Ereignisse enthalten 173 Modifierfragmente. 121 sind die gebundenen
Wiederholungsslots; 52 andere Fragmente bleiben unverändert in roher
Atomreihenfolge. Die zweite oder dritte Nennung erhält 61 kurze Partikeln:
32-mal `ebenfalls`, zwanzigmal `erneut`, achtmal `wieder` und einmal
`nochmals`. Der Partikelspan liegt ausdrücklich außerhalb des jeweiligen
Wurzelausdrucks.

35 der 773 gelernten Sigla stehen in den neu formulierten Ereignissen. Ihre
Positionen werden neu berechnet; die übrigen 738 bleiben unangetastet. Zwei
Ereignisse, `G407-E0966` und `G407-E3605`, enthalten je zwei überlappende
Gruppen und werden trotzdem nur einmal als Ganzes gerendert.

## Ereignisschlüssel statt gefährlicher Textersetzung

Jede Änderung besitzt eine explizite Karte `event_id → Quellsatz → Zielsatz`.
Das ist nicht bloß technische Vorsicht: `G407-E1955` und `G407-E2638` haben
denselben Quellsatz, sind aber zwei verschiedene Manuskript-Ereignisse. Eine
globale Textsuche könnte beide unkontrolliert gemeinsam ersetzen. Die
ereignisgebundene Ausgabe rekonstruiert alle 5.122 GDT576-Sätze und alle 793
Aussagen exakt.

Geändert werden 58 Ereignisse—44 Nichtzustands- und vierzehn Zustandskarten—,
48 Aussagen und 24 der dreißig Seiten. Gegenüber GDT574 enthält die kumulierte
Lesestimme jetzt 750 veränderte Ereignisse, 305 Aussagen und 28 Seiten.

## Bewusste Grenzen

`G407-E1755`, seine Aussage `G407-S149` und die Seite f75r bleiben wegen des in
GDT577 gefundenen früheren Scope-Stimmenkonflikts bytegleich. Auch die siebzehn
getrennten Außen/Innen-Paare und die drei rohen Nachbarwiederholungen bleiben
unverändert; sie gehören in eigene kleine Folgepässe.

Die Ausgabe ist eine deutlich bessere konkrete Arbeitsübersetzung der schon
angenommenen Struktur. Sie ändert aber keinen Wurzelwert und erklärt die
explorativen O-/D_ADDR-Köpfe nicht nachträglich zu bewiesenem Klartext.

## Nächster Schritt

Als Nächstes werden die siebzehn Außen/Innen-Paare koordiniert, ohne einen der
beiden geschriebenen Scope-Slots zu verlieren. Danach bleiben nur die drei
wirklich roh benachbarten Relationswiederholungen als enger Zählpass offen.
