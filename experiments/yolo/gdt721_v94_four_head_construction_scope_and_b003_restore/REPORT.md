# GDT721 — V94 four-head construction scope and legacy-span restoration

Status: `PASS_V94_4_HEAD_READINGS_REPAIRED__POL_POWDER_MATERIAL__LOR_WOOD_PORTION__L_R_ACTIVE_OCCURRENCES_BOUND__3_LEGACY_SPANS_RESTORED__52_WEAK_READINGS_REMAIN__NO_SCORE_CREDIT__ALL_H0_NONE`

## Ergebnis

Das Vier-Kopf-Modell liefert zwei konkrete, kompositionell vorhersagbare
Ganzwörter. Die beiden nackten Einzeichenbelege werden davon getrennt.

| Form | Arbeitsbedeutung | Zerlegung | aktive Fundstelle |
|---|---|---|---|
| `pol` | Pulverstoff | `P_INITIAL_POWDER + OL_MATERIAL_BODY` | selbständig: Pulverstoff |
| `lor` | Holzportion | `L_INITIAL_WOOD + OR_PORTION_BODY` | selbständig: Holzportion |
| `l` | Holz / holziger Pflanzenteil (nur als Kompositionskopf) | initialer L-Kopf | keine Einzelausgabe; in B003 konsumiert |
| `r` | Wurzel / Wurzeldroge (nur als Kompositionskopf) | initialer R-Kopf | keine Einzelausgabe; in `keo r` konsumiert |

`pol` steht auf f77r.38 am Zeilenanfang vor `shedy`. GDT635 belegt die Form
16-mal auf zwölf Seiten und dreizehnmal lesergenau. Entscheidend ist nicht nur
dieser Wiederholung: Im vollständigen `pol/sol/rol/lol`-Gitter reproduziert die
Zerlegung den Körper `ol=Stoff/Material`, den Anfangskopf
`p=Pulver/Pulverform` und damit `pol=Pulverstoff`. Der exakte Rahmen `pol shedy` wechselt an
vergleichbaren Stellen mit `sol shedy`.

`lor` steht auf f107r.2 zeilenfinal als Nomen. Die Form kommt 38-mal auf 28
Seiten vor und ist dreißigmal lesergenau. Das vollständige
`por/sor/ror/lor`-Gitter reproduziert `l + or = Holzportion`; GDT693 bewahrt
die geerbte Lesung der aktiven Position als `OR_PORTION`-Kontrollfall. OR bleibt dabei ein
zugelassener Körper und wird nicht künstlich als O+R zerlegt.

## Konstruktionswörterbuch

V94 behält fünf eng begrenzte Arbeitswerte:

- `p-` → Pulver / Pulverform
- `l-` → Holz / holziger Pflanzenteil
- `r-` → Wurzel / Wurzeldroge
- `-ol` → Stoff / Material
- `-or` → Teil / Portion

Diese Werte gelten in den belegten initialen Vier-Kopf-Kompositionen. Sie sind
kein freies Einzeichen- oder Substring-Wörterbuch. Genau diese Begrenzung macht
das Modell nützlich: Es erklärt nicht bloß `pol` und `lor`, sondern komponiert
im selben Raster auch `rol=Wurzelstoff`, `lol=Holzstoff`,
`ror=Wurzelportion` und die jeweiligen Samenformen. `pulvis`, `lignum` und
`radix` sind dabei nur die bereits
in GDT635 verwendeten internen Merkhilfen, keine historische Evidenz und keine
behaupteten Voynich-Klartexte.

## Nacktes `l` und `r`

Der produktive L-Kopf ist mit 1.224 Anfangsvorkommen in 344 Typen stark, aber
GDT635 trennt 163 nackte `l` ausdrücklich davon. Deshalb bedeutet P435 nicht
frei und überall Holz. An dieser Stelle verschmelzen die Alternativleser
`l|karchees`; der Gesamtspan wird einmal als „vollständig getrocknete Charge
aus Anteil I der erhitzten Holzdroge“ ausgegeben.

Für R gilt dasselbe: 332 Anfangsvorkommen in 116 Typen stützen den
Wurzel-/Radix-Kopf, während 129 nackte `r` getrennt bleiben. P289 ist die rechte
Hälfte von `keo|r`; der ausführbare Gesamtwert lautet einmal „heiße Portion“.
Ein zusätzliches „Wurzel“ wäre Doppelrendering. Ebenso wird `r` nicht zu
„Portion“ umdefiniert: Der Portionswert gehört dem gebundenen Ganzen, und im
produktiven Restmodell trägt OR die Portionsfunktion.

## Renderer-Reparatur

Der V93-Kontextbestand referenzierte B001, B002 und B003 weiterhin an jeweils
zwei exakten Positionen. Der kanonische V93-Span-Renderer enthielt jedoch nur
die späteren Spans `G683_CHEOP_OL` und `G678_KEO_R_F7R2`. V94 stellt die drei
verlorenen, bereits in GDT695 byte-identisch eingefrorenen Spans wieder her:

| Span | Ganzwert |
|---|---|
| B001 | drei Portionen des Anteils I des heißen Holzansatzes |
| B002 | Anteil I des heißen Holzansatzes; drei Portionen davon |
| B003 | vollständig getrocknete Charge aus Anteil I der erhitzten Holzdroge |

Damit besitzt der kanonische Renderer fünf vollständige gebundene Spans. Alle
zehn beteiligten Positionen werden genau einmal konsumiert; kein Span und kein
Bestandteil ist global exportierbar. Die beiden One-shot-Direktiven und alle
acht f7r.2-Ausgabeeinheiten bleiben byte-identisch. Ein eigener Ausführungsbeleg
weist für jeden der fünf Spans zwei konsumierte Positionen, unterdrückte
Einzelausgaben und genau eine ausgegebene Ganzheit aus.

## Bestand

- 4 revidierte Lesungen an 4 Positionen auf 4 Seiten
- 30 exakt wiederholbare Primärevidenzbindungen
- 12 Rivalenmodellzeilen und 5 konstruktionsgebundene Atome
- 320 Nichtziel-Wortzeilen und 475 Nichtziel-Kontexte unverändert
- 324 aktive Lesungen an 479 Positionen: 7 W0, 135 W1, 163 W2 und 19 W3
- 1.582 Oberflächen / 1.586 vollständige Lesungen, jede mit Default,
  Confidence, Evidenz und Gegenbeleg
- 52 weak readings remain

## Grenze

V94 ist die derzeit beste konkrete Arbeitstheorie für diese Formen. Sie setzt
keine Pflanzenart, Sprache oder historische Codebuchidentität fest. Die vier
Scores bleiben bei 31 beziehungsweise 32, weil GDT721 vorhandene Evidenz
korrekt zusammensetzt und Renderer-Scope repariert, aber keine unabhängige neue
Wortbezeugung erzeugt. f84 und f84r bleiben unbenutzt.
