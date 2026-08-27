# GDT562 — 687 aktionslose Karten enthalten trotzdem eine vollständige Operation

Status:
`PASS_687_OF_706_FULL_OPERATIONS__693_ACTION_CARRIES__692_ARGUMENTS_AVAILABLE__19_RESIDUALS_CLOSED_BY_FIVE_ROLES`

## Ergebnis

706 der1.656 Zustandskarten besitzen kein geschriebenes Handlungsatom. Das
sah zunächst wie der größte Bedeutungsrest aus. Tatsächlich sind fast alle
diese Karten keine Wortlücken, sondern Zustandsellipsen:

```text
693 / 706  haben eine bereits aktive Handlung
692 / 706  haben ein sichtbares oder bereits aktives Argument
687 / 706  ergeben beides zusammen: vollständige Handlung + Argument
 19 / 706  besitzen fünf andere, vollständig benannte Rollen
```

Damit erhalten97,31% der scheinbar aktionslosen Karten eine konkrete Operation,
ohne dass auf der Karte ein neues Verb erfunden wird.

## Woher die ausgelassene Bedeutung kommt

| Slot | Herkunft | Karten |
|---|---|---:|
| Handlung | frühere sichtbare Handlung derselben Aussage | 544 |
| Handlung | Besitzer-/Abschnittsdefault | 149 |
| Handlung | keine aktive Handlung | 13 |
| Argument | sichtbar in der Karte | 233 |
| Argument | früher sichtbar in derselben Aussage | 355 |
| Argument | Besitzer-/Abschnittsdefault | 104 |
| Argument | kein aktives Argument | 14 |

Die Reichweite ist kurz, aber nicht nur unmittelbare Nachbarschaft. Von544
sichtbaren Handlungsquellen stehen376 direkt davor;168 bleiben zwei bis acht
Karten aktiv. Bei Argumenten sind238/355 unmittelbar und117 zwei bis fünf
Karten entfernt. Das ist ein kleiner Satzspeicher.

Auf den vier aktuellen Seiten besitzen alle54 aktionslosen Karten gespeicherte
GDT539-Quellpointer;54/54 stimmen mit der unabhängigen Rekonstruktion überein.
Für die alten26 Seiten markiert der Leser ehrlich, dass GDT416 keine
Quellereignis-ID speichert, statt eine nachträglich zu behaupten.

## Aus `OL` wird keine zweite Wörterbuchbedeutung

Ein einziges geschriebenes `OL=FORTSETZEN` kann je nach aktivem Zustand eine
vollständige Anweisung weiterführen:

```text
OL   + aktives SH + aktives AIN  → Weiter: halte den Anteil.
OL   + aktives K  + aktives Y    → Weiter: gib den Posten.
OL   + aktives CH + aktives Y    → Weiter: nimm den Posten.
```

Das bedeutet nicht, dass `OL` zugleich „halten“, „geben“ und „nehmen“ heißt.
Sein eigener Wert bleibt nur FORTSETZEN. Die wechselnde Handlung sitzt im
Satzgedächtnis. Genau so kann ein kleines Codebook viel längere Anweisungen
tragen, ohne komplexe Ganzwortdefinitionen zu brauchen.

## Sechs Rollen schließen alle706 Karten

| Rolle | Karten | Bedeutung |
|---|---:|---|
| vollständige geerbte Operation | 687 | Handlung plus sichtbares/geerbtes Argument |
| objektlose geerbte Operation | 6 | aktive Handlung ohne Objektzwang |
| Argumentbezug | 5 | neuer/aktiver Träger ohne ausgesprochene Handlung |
| formaler oder relationaler Vorspann | 4 | Grad/Ausführung/Ausgang vor der folgenden Operation |
| selbständiger abgestufter Abschluss | 3 | Grad setzen und Schritt schließen |
| reine Fortsetzung | 1 | nur den laufenden Gang fortführen |

Die19 Karten außerhalb der Volloperation sind deshalb kein diffuser
„unübersetzter Rest“.

## Der vollständige19er-Rest

Sechs Karten erben eine Handlung, aber kein Argument:

```text
OL                    Weiter: wähle.
OT+O+DY               Danach: halte; zur Ausführung; abschließen.
LOCAL_CHAR_F+OL+OL    Weiter: halte; hier; nochmals weiterführen.
```

Fünf Karten setzen einen Argumentbezug:

```text
OT+EE+Y   Danach: Bezug auf den Posten; auf Grad II.
OL+Y      Weiter: Bezug auf den Posten.
OT+E+Y    Danach: Bezug auf den Posten; auf Grad I.
```

Vier f72r-Karten sind formale/relative Vorspänne, etwa:

```text
OT+E+O+D_ADDR+AR
Danach: auf Grad I; zur Ausführung; hier; vom Ausgang.
```

Drei Einzelkarten schließen einen abgestuften Schritt, und eine einzelne
`OL`-Karte bedeutet schlicht „Weiter.“ Keine dieser19 Karten benötigt einen
zusätzlichen Stamm.

## Sieben Zustandsfolgen reichen

| Folge | Karten | Rahmen |
|---|---:|---|
| `OL` | 317 | aktuelle Operation weiterführen |
| `OT` | 230 | danach zur nächsten Operation |
| `OT+DY` | 76 | danach ausführen und schließen |
| `DY` | 38 | aktuelle Operation schließen |
| `OT+OL` | 21 | danach eröffnen und weiterführen |
| `OL+DY` | 19 | weiterführen und schließen |
| `OL+OL` | 5 | doppelte Fortsetzungsbrücke |

Alle neun Handlungswerte werden tatsächlich geerbt: OK166-mal, SH131, K85,
CH83, S71, CHD71, T52, P18 und R16. Das ist kein Sondertrick für ein einzelnes
Lieblingsverb.

## Neue Arbeitstheorie

Die Schrift scheint hier drei Dinge zu kombinieren:

```text
geschriebene Karte  = neue/ausdrückliche Werte und Zustandsoperatoren
Satzgedächtnis      = zuletzt aktive Handlung und zuletzt aktives Argument
Besitzerkontext     = lokales Nomen und Anfangsdefault
```

So wird aus `OT+E+Y` nicht das absurde Ganzwort „danach Pflanzenmaterial auf
Grad I bearbeiten“. Die Karte sagt nur „danach + Grad I + Posten“; die aktive
Handlung kann etwa HALTEN sein, und der Besitzer macht aus POSTEN einen
Pflanzen-, Stations- oder Drogenposten.

## Nächster Arbeitsweg

Die706 aktionslosen Karten haben nun ownerfreie Mikrophrasen. Die anderen950
Zustandskarten tragen ihre Handlung sichtbar. Der nächste Pass kann beide
Hälften zu einer vollständigen flüssigen1.656-Karten-Ausgabe verbinden: sichtbare
Handlung zuerst, sonst GDT562-Zustandsellipse; in beiden Fällen bleiben
Atomspur, ownerfreier Satz und Besitzer-Kontext als getrennte Kanäle erhalten.
Keine neue Seite ist nötig.

## Grenze

GDT562 ist eine kreative Arbeitsgrammatik für Auslassung und Zustand. Ergänzte
Handlungen und Argumente sind Kontextwerte, keine unsichtbaren Schriftzeichen
und keine neuen Wortübersetzungen. Keine Seite, Oberfläche, Segmentierung,
Rezeptfolge, Wurzelbedeutung oder Aussagegrenze ändert sich. Das Ergebnis
bestätigt weder Klartext noch historische Sprache, Syntax oder Codebuch. Alle39
Validatorprüfungen bestehen.
