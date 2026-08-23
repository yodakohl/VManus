# Die 28 Programmkarten als kleiner Werkstattbaukasten

Status: schnelle kreative Zehn-Seiten-Arbeitstheorie. Das ist eine konkrete
Schreiberrekonstruktion, keine kanonische Voynich-Behauptung.

## Ergebnis

Die 28 terminalen Programmkarten sind **nicht** 28 völlig unabhängige Wörter.
Sie lassen sich am einfachsten als genau die gesuchte Mischung aus
Fachkürzeln und gelernten Ganzwörtern lehren:

```text
HANDLUNGSKERN
  + optional RICHTUNG / FOLGE / ZIEL
  + optional KURZ- oder LANGGRAD
  + GELERNTE EXAKTKARTEN-SCHLUSSROLLE
```

Von den 28 Karten sind:

- **20 produktiv zusammengesetzt**;
- **4 teilweise zusammengesetzt**, mit einem noch gelernten Innenwert;
- **4 vollständig gelernte Spezialbefehle**.

Über alle zehn Seiten treten diese 28 Karten 78-mal auf. Davon sind 69
Vorkommen produktiv lesbar, fünf teilweise und nur vier echte Ganzwortfälle.
Im engeren Variantenmenü sind es 55 von 64 produktive Aufrufe, fünf teilweise
und vier memorierte Spezialaufrufe.

Das ist viel näher an einem realistischen Werkstattsystem als das frühere
Wörterbuch: Der Lehrling muss nicht 28 freie Sätze auswendig lernen, sondern
15 wiederkehrende Bauteile und vier Spezialkarten.

## Die 15 lehrbaren Bauteile

### Sechs Handlungskerne

| Kern | knapper Wert | typische Programme |
|---|---|---|
| `OK` | Arbeitsgang ansetzen | kurz/länger ansetzen; Umsetz- oder Absetzgang ansetzen |
| `CHD~CHED` | umsetzen, in Arbeitsposition führen | umsetzen, weiterführen, einführen, abführen |
| `SHED` | absetzen | absetzen; weiter absetzen |
| `CKH~CKHE` | durch einen Seihweg führen | seihen; nach außen abseihen |
| `CHK` | wärmen | länger wärmen |
| `OLK` | sammeln/halten | länger sammeln |

`CHK` und `CKHE` bleiben ausdrücklich verschieden. Die ähnliche Zeichenfolge
ist kein Grund, *wärmen* und *seihen* zusammenzuwerfen.

### Sechs Adress-, Richtungs- und Folgebauteile

| Bauteil | Wert |
|---|---|
| `L` | nach außen, ab-/aus- |
| `P` | nach innen, zum Empfänger |
| `AL` | zur bezeichneten Zielstelle |
| `OL` | denselben Gang weiterführen |
| `OT` | danach, folgende Ausführung |
| `AIR` | laufender Flüssigkeits-/Wasserweg |

### Zwei Grade

| Grad | Wert |
|---|---|
| `E` | kurz oder direkt |
| `EE` | länger oder anhaltend |

Diese Grade gelten nur in tatsächlich gebauten Reihen. Ein beliebiges `e` im
Manuskript heißt weiterhin nicht automatisch *kurz*, und `ee` nicht überall
*lang*.

### Eine Schlusskonstruktion

`CLOSE_EXACT` heißt: **Diese ganze exakte Karte schließt die lokale Zelle.**
Es bedeutet ausdrücklich nicht `DY = Ende` als freies sichtbares Suffix. Das
ist nötig, weil sichtbares `dy` auch zur offenen Y-Karte gehören kann und die
nackte `chdy|chedy`-Karte elfmal nichtterminal ist.

## Die saubersten Vorhersagereihen

### Setzgrad

```text
qokedy    OK + E  + SCHLUSS   kurz ansetzen; schließen
qokeedy   OK + EE + SCHLUSS   länger ansetzen; schließen
```

Diese beiden Karten decken zusammen 18 Vorkommen auf den zehn Seiten und 15
Aufrufe im lokalen Variantenmenü.

### Folgegrad

```text
otedy      OT + E  + SCHLUSS  kurze Folge; schließen
qoteedy    OT + EE + SCHLUSS  lange Folge; schließen
```

Das initiale `q` erhält keinen zweiten Sinn; es ist hier eine sichtbare Hülle.

### Transfergitter

```text
schedy / dchedy / tchedy   CHED + SCHLUSS       umsetzen
qolchedy / olchedy         OL + CHED + SCHLUSS  weiter umsetzen
qotchedy / otchedy         OT + CHED + SCHLUSS  danach umsetzen
otchdy                      OT + CHD  + SCHLUSS  danach umsetzen
lchedy                      L  + CHED + SCHLUSS  abführen
pchedy                      P  + CHED + SCHLUSS  einführen
dalchdy                     AL + CHD  + SCHLUSS  zur Zielstelle umsetzen
qokchdy                     OK + CHD  + SCHLUSS  Umsetzgang ansetzen
oldy                        OL + SCHLUSS         fortsetzen
```

Die Formen `s/d/t` am Anfang der Basiskarte und wechselndes `q` werden nicht
als zusätzliche Verben behandelt. Sie sind Renderer-/Rahmenelemente innerhalb
derselben exakten Karten.

### Absetz- und Seihgitter

```text
shedy / tedy     SHED + SCHLUSS       absetzen
qokshedy         OK + SHED + SCHLUSS  Absetzgang ansetzen
solshedy         OL + SHED + SCHLUSS  weiter absetzen

shckhedy         CKHE + SCHLUSS       seihen
lcheckhedy       L + CKHE + SCHLUSS   nach außen abseihen
```

### Zwei lange Fachprogramme

```text
chkeedy    CHK + EE + SCHLUSS   länger wärmen
olkeedy    OLK + EE + SCHLUSS   länger sammeln
```

Damit sagt `EE` nicht selbst *wärmen* oder *sammeln*. Es verlängert den jeweils
anderen Kern.

## Vier ehrliche Teilkompositionen

Diese Karten zeigen bekannte Teile, aber noch keinen vollständig
vorhersagbaren Innenbau:

| Karte | lesbarer Teil | gelernter Rest |
|---|---|---|
| `ldy` | `L` = nach außen | Abziehhandlung |
| `daldy` | `AL` = an der Zielstelle | Nebenöffnung setzen |
| `dairydy` | `AIR` = Wasserlauf | Lauf schließen |
| `lochedy` | `L+CHED` = abführen | `O` als lokaler Restselektor |

Wichtig ist besonders `lochedy`: Das lokale `O` darf *Rest* auswählen, ohne
dass daraus sofort ein globaler Stamm `O = Rest` gemacht wird.

## Vier gelernte Ganzwörter

```text
sshkchdy    schwenken; schließen
rshedy      Waschung; schließen
lkedy       nachwaschen; schließen
qokylddy    befestigen; schließen
```

Diese vier Karten sind kein Scheitern des Modells, sondern genau die
Nomenklatorhälfte des gesuchten Mischsystems. Besonders `rshedy` schützt vor
einer falschen mechanischen Analyse: Obwohl `shedy` produktiv *absetzen*
bedeutet, ist `rshedy` als gelernte Karte *Waschung* und nicht „R + absetzen“.

## Was der Lehrling tatsächlich lernt

1. Er erkennt zuerst die ganze exakte Karte, nicht bloß die sichtbare EVA-
   Zeichenfolge.
2. Bei einer lizenzierten Familie liest er Kern, Richtung/Folge und Grad.
3. Das lokale Bild oder der vorangehende Posten liefert Gegenstand und Ziel.
4. Die ganze terminale Karte bestätigt den Zellschluss.
5. Vier Spezialkarten werden als unteilbare Werkstattbefehle gelernt.
6. `q`, wechselndes `s/d/t` und einzelne Hüllen werden nicht mit Bedeutungen
   überladen.

Damit kann ein Schreiber ein neues **vorhersehbares Mitglied einer belegten
Reihe** bilden oder lesen, etwa `OK + E/EE` oder `OT + E/EE`. Er darf aber
nicht beliebige sichtbare Teilfolgen frei kombinieren.

## Was sich an der laufenden Übersetzung ändert

Die 173 Kartenwerte, 381 Ereignislesungen und 116 deutschen Arbeitsanweisungen
werden in dieser Runde nicht umgeschrieben. Ihre knappen Programmbedeutungen
bleiben gleich. Neu ist, dass 20 der 28 Programmkarten nicht länger als 20
separate Wörter gelernt werden müssen, sondern aus demselben kleinen
Komponentenapparat rücklesbar sind.

Die vollständige Zuordnung steht in `PROGRAM_COMPOSITION_REGISTER.tsv`; das
15-teilige Lehrwörterbuch in `PROGRAM_COMPONENT_LEXICON.tsv`; die acht
Programmfamilien in `PROGRAM_FAMILY_GRID.tsv`. Die vollständige Ausgabe bleibt
in den 173-/381-/116-/11-Dateien erhalten.

## Nächster sinnvoller Angriffspunkt

Außerhalb dieses Variantenmenüs existieren elf weitere terminale exakte
Karten. Der nächste kreative Pass sollte prüfen, welche davon in denselben
Baukasten fallen und welche die Nomenklatorliste ehrlich erweitern. Erst danach
lohnt sich eine neue flüssige Gesamtübersetzung der Biological-Seiten.

`f84` und `f84r` blieben versiegelt.
