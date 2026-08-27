# GDT561 — jede Zustandskarte hat jetzt eine vollständige Defaultlesung

Status:
`PASS_1656_TYPED_STATE_CARDS__4684_OF_4684_ATOMS_MAPPED__402_RECIPES_DEFAULTED__939_CARRIER_LINKS_INTEGRATED__18_ORDER_FAMILIES_PRESERVED`

## Ergebnis

Die bisher getrennten Teilmodelle sind jetzt in einem einzigen Kartenleser
zusammengeführt. Er deckt alle1.656 bereits bekannten Karten mit `OT`, `OL`
oder `DY` ab:

```text
1.656 / 1.656 Karten       vollständig gelesen
4.684 / 4.684 Atomstellen mit einem kurzen Default versehen
402   / 402   Rezepte      als geordnete Komposition verfügbar
939   / 939   Grad-, Argument- und Relationsstellen positionsgenau verbunden
0             neu gelernte Ganzkartenbedeutungen
```

Damit kommt in diesem Bestand wirklich keine Sequenz und kein Atom mehr ohne
Default davon. Das ist noch keine Übersetzung des Voynich-Manuskripts, aber es
ist eine vollständige ausführbare Arbeitstheorie für diesen Kartentyp.

## Das Wörterbuch bleibt klein

Die4.684 Stellen brauchen nur36 bereits vorhandene Atome in sieben Rollen:

| Rolle | verschiedene Atome | Stellen | Karten |
|---|---:|---:|---:|
| Handlung | 9 | 1.158 | 950 |
| Grad | 3 | 742 | 729 |
| Argument | 4 | 390 | 382 |
| Relation | 4 | 216 | 212 |
| Zustandssteuerung | 3 | 1.870 | 1.656 |
| Formsteuerung | 4 | 175 | 152 |
| Lokal-/Klassenzeichen | 9 | 133 | 124 |

Die kurzen Kernwerte bleiben dieselben: etwa `CH=NEHMEN`, `SH=HALTEN`,
`Y=POSTEN`, `AIIN=WERT`, `AL=ZIELORT`, `AR=AUSGANG`, `L=VERBINDUNG`,
`E/EE/EEE=GRAD I/II/III`, `OT=DANACH`, `OL=FORTSETZEN` und
`DY=ABSCHLIESSEN`. `HIER`, `VARIANTE` und `KLASSE` sind strukturelle Tags,
nicht behauptete deutsche Wörter im Manuskript.

## Drei Lesekanäle verhindern falsche Sicherheit

Jede Karte zeigt nebeneinander:

1. die vollständige typisierte Spur;
2. den kurzen atomaren Default;
3. die flüssige, besitzergebundene Kontextzeile aus GDT416/GDT539.

Beispiel:

```text
Rezept:  OT+AL+Y
Spur:    OT{ZUSTANDSSTEUERUNG=DANACH}
       > AL{RELATION=ZIELORT}
       > Y{ARGUMENT=POSTEN}
Default: danach; zum Zielort; den Posten
Kontext: Danach im laufenden Gang halte den Positionsposten;
         zur Zielposition.
```

Der Kontext darf also „Positionsposten“ und eine geerbte Handlung liefern,
aber er macht aus `Y` keinen Wörterbucheintrag „Positionsposten halten“. Genau
diese Trennung war in älteren, zu komplexen Bedeutungen verloren gegangen.

## Auch lange Karten werden nicht als Ganzwort erfunden

Die längste Zustandskarte hat neun Atome:

```text
D_ADDR+OL+CH+S+Y+CH+K+E+OL
HIER → FORTSETZEN → NEHMEN → WÄHLEN → POSTEN
     → NEHMEN → GEBEN → GRAD I → FORTSETZEN
```

Ihr knapper Default lautet:

```text
hier; weiter; nehmen; wählen; den Posten;
nehmen; geben; auf Grad I; weiter
```

Die vorhandene Kontextzeile macht daraus lesbar:

> Weiter und weiter nimm den Drogenposten, wähle den Drogenposten,
> nimm den Drogenposten und gib den Drogenposten zu; auf Grad I;
> an der bezeichneten Stelle.

Die flüssige Zeile ist länger, weil sie Besitzer, Kasus und geerbten Träger
einsetzt. Im Wörterbuch bleibt jedes Atom kurz.

## Die häufigsten Karten sehen tatsächlich wie Arbeitskürzel aus

| Rezept | Karten | vollständiger Default |
|---|---:|---|
| `OL` | 189 | weiter |
| `SH+E+DY` | 119 | halten; auf Grad I; abschließen |
| `OK+EE+DY` | 83 | setzen; auf Grad II; abschließen |
| `OK+E+DY` | 79 | setzen; auf Grad I; abschließen |
| `OT+Y` | 40 | danach; den Posten |
| `OT+E+DY` | 37 | danach; auf Grad I; abschließen |
| `L+CHD+DY` | 35 | über die Verbindung; bearbeiten; abschließen |
| `OL+Y` | 33 | weiter; den Posten |

Das passt besser zu einer Mischung aus Fachkürzeln, Steuerzeichen und wenigen
gelernten lokalen Inhalten als zu einem Wörterbuch, in dem eine kurze Form eine
ganze Geschichte wie „Pflanzenmaterial zeitgebunden beschaffen“ tragen müsste.

## Reihenfolge ist ein eigener Bedeutungsträger

Die402 Rezepte bilden383 ungeordnete Atommengen. In18 dieser Mengen kommen
mehrere Reihenfolgen vor:37 Rezepte mit zusammen102 Karten. Drei klare Paare
sind:

```text
OL+Y     weiter; den Posten
Y+OL     den Posten; weiter

AL+OL    zum Zielort; weiter
OL+AL    weiter; zum Zielort

CH+OT+Y  nehmen; danach; den Posten
OT+CH+Y  danach; nehmen; den Posten
```

Darum ist weder `shey` noch irgendeine andere Oberfläche automatisch ein
unteilbares Wort; aber auch ein ermitteltes Compound darf nicht auf eine
ungeordnete Tüte von Stämmen reduziert werden. Stammwert und Stellung leisten
unterschiedliche Arbeit.

## Was der Zusammenschluss zeigt

Die drei Spezialgrammatiken liefern939 Atomlinks auf787 Karten. Ihre
Überschneidungen sind begrenzt:

```text
Grad ∩ Argument     96 Karten
Grad ∩ Relation     15 Karten
Argument ∩ Relation 22 Karten
alle drei            0 Karten
```

Das erklärt, warum kein einzelnes Schema bisher alle Karten natürlich klingen
ließ. Viele Karten tragen nur eine Spezialisierung; der Rest besteht aus
Handlungen, Zustandssteuerung oder strukturellen Zeichen. Der gemeinsame Leser
braucht daher typisierte Slots, keinen universellen „Wortstamm = Gegenstand“-Trick.

## Der nächste sinnvolle Pass

Die Abdeckungsfrage ist geschlossen; die Sprachqualität noch nicht. 706 Karten
haben keine sichtbare Handlung,1.274 kein sichtbares Argument und274 weder
Handlung, Grad, Argument noch Relation. Davon sind222 reine
`OT/OL/DY`-Steuerkarten. Als Nächstes sollten diese Karten nicht umgedeutet,
sondern nach ihrer praktischen Satzrolle geordnet werden: Initialisierung,
Fortsetzung, Abschluss, Referenz oder Übergang. Anschließend können die213
geordneten Rollenmuster in flüssige Mikrosätze überführt werden, ohne auch nur
einen der36 Stammwerte zu verändern.

## Grenze

GDT561 ist eine kreative, vollständige Arbeitslesung für bereits bekannte
Karten. Es ändert keine Seite, Oberfläche, Segmentierung, Rezeptfolge,
Wurzelbedeutung oder Aussagegrenze und erzeugt keine zukünftige Form. Es
bestätigt weder Klartext noch historische Sprache, Syntax, Lautwerte,
Codebuchidentität oder Gegenstände. Alle51 Validatorprüfungen bestehen.
