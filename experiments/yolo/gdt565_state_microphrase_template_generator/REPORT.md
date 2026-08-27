# GDT565 — 42 kleine Karten erzeugen die gesamte Zustandsübersetzung

Status:
`PASS_1655_EXACT_REPLAYS__ONE_EDITORIAL_DOUBLE_ARGUMENT_NORMALIZATION__716_CELLS__42_RENDERER_CARDS__168_STRUCTURAL_TEMPLATES`

## Ergebnis

Die 716 Rezept-Kontext-Lesungen aus GDT564 sind keine 716 zu lernenden langen
Sätze. Ein Satzbaukasten aus 42 kleinen Karten erzeugt die vollständige
1.656-Karten-Ausgabe:

```text
 9 Zustandsrahmen
 9 Handlungsschablonen
 4 Argumentkarten
14 Modifikatorfragmente für 20 geschriebene Atome
 6 Verknüpfungsregeln
──────────────────────────────────────────────────
42 Renderer-Karten
```

1.655/1.656 GDT563-Mikrophrasen werden bytegleich rekonstruiert. Die einzige
Abweichung ist eine absichtliche deutsche Glättung, die unten vollständig
benannt ist. Es gibt null unerwartete Abweichungen und null gelernte
Langsatzschablonen.

## Wo die scheinbare Vielfalt herkommt

Die Quelle enthält 607 verschiedene deutsche Mikrophrasen. Der Generator baut
sie aus kleinen Beständen:

```text
  9 atomare Handlungsschablonen → 133 beobachtete Handlungsketten
 14 Modifikatorfragmente        →  80 beobachtete Modifikatorphrasen
  4 Argumentkarten              →   9 beobachtete Argumentsignaturen
  9 Zustandsrahmen              → Weiter/Danach/Abschluss außen herum
```

Die 20 Modifikatoratome werden 1.266-mal benutzt. Sie bleiben in geschriebener
Reihenfolge; gleiche deutsche Fragmente löschen ihre unterschiedlichen
Atomkennungen nicht. Sieben lokale Zeichen können etwa alle „hier“ heißen und
trotzdem sieben sichtbare Tags bleiben.

## Der Satzbau selbst ist klein

Nur elf äußere Muster entscheiden, ob ein Satz ein Zustandspräfix, eine
Handlung oder Referenz, einen Modifikatorblock und einen Zustandssuffix besitzt.
Innen gibt es sieben Handlungstopologien und vier Argumenttopologien.

Wenn zusätzlich Zustandsfolge und Modifikatortypen sichtbar bleiben, entstehen
168 abstrakte Strukturmuster. Auch diese sind nicht hauptsächlich Einzelstücke:

```text
 82 wiederkehrende Strukturmuster → 1.570 Karten
 86 einmalige Strukturmuster       →    86 Karten
```

Damit liegen 94,81% der Karten auf einer wiederkehrenden abstrakten Struktur.
Die tragfähige Einheit ist ein kleiner Satzbaukasten, nicht ein riesiges
Ganzwortlexikon.

## Die eine gefundene Unebenheit

Vier sichtbare `Y|Y`-Handlungen waren bereits flüssig als „die beiden Posten“
gesetzt. Genau eine geerbte Handlung aus dem älteren GDT562-Renderer hatte noch:

```text
G407-E1000  Y+D_ADDR+OL+Y
alt:        Weiter: gib den Posten und den Posten; hier.
neu:        Weiter: gib die beiden Posten; hier.
```

Beide Y-Slots, K=GEBEN, D_ADDR=HIER und OL=FORTSETZEN bleiben unverändert. Es
ändert sich weder die gedachte Operation noch ein Wörterbucheintrag—nur die
deutsche Koordination wird jetzt überall gleich ausgesprochen. Der Pass hat
damit nicht nur komprimiert, sondern eine echte redaktionelle Inkonsistenz
gefunden und beseitigt.

## Vollständiger Generationsweg

```text
geschriebenes Rezept
  → GDT564 füllt offene Handlung/Argument
  → Handlungsschablonen erzeugen die geordnete Aktionskette
  → Modifikatorfragmente bleiben in Schriftreihenfolge
  → OT/OL/DY-Rahmen setzt Weiter/Danach/Abschluss
  → Satzkombinator setzt Interpunktion
```

Jeder der 716 Rezept-Kontext-Fälle und jedes der 1.656 Ereignisse bleibt bis
zur Atomspur zurückverfolgbar. Eine Form wie `OL` erhält also keine lange
Sonderdefinition: Sie wählt den Fortsetzungsrahmen, während die beiden
Zustandsslots und die kleinen Aktions-/Argumentkarten den konkreten Satz bauen.

## Nächster Arbeitsweg

Der Generator kann nun in alle 793 bereits zugelassenen Aussagen eingesetzt
werden. Der nächste Pass sollte die 1.656 generierten Zustandszeilen mit den
3.466 übrigen Prosekarten verbinden und eine vollständige 5.122-Ereignis-
Arbeitsausgabe herstellen. Zustandskarten verwenden GDT565, alle übrigen Karten
behalten ihre bisherige ownergebundene Lesung. So sehen wir erstmals jede
Aussage in einer einzigen konsistenten aktuellen Ausgabe, weiterhin ohne eine
neue Seite zu öffnen.

## Grenze

Der kleine Generator zeigt, dass die gesetzte Arbeitsübersetzung intern
kompositionell ist. Er beweist nicht, dass ihre deutschen Grundwerte historisch
richtig sind. Eine generierbare neue Kombination ist noch kein vorhergesagtes
Voynich-Vorkommen. Keine Seite, Oberfläche, Segmentierung, Rezeptfolge oder
Wurzelbedeutung ändert sich. Alle 40 Prüfungen bestehen.
