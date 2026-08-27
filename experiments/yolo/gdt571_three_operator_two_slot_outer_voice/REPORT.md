# GDT571 — drei Operatoren und zwei Slots tragen alle neun Außenrahmen

Status:
`PASS_3_OPERATOR_CARDS__5_POSITION_REALIZATIONS__2_SLOT_RULES__9_SEQUENCES__1870_MARKERS__54_FINITE_FOLLOWERS__ZERO_ROOT_CHANGE`

## Der eigentliche Gewinn

Die bisherige Ausgabe besaß neun eigene OT/OL/DY-Rahmen. Das sah klein aus,
war aber immer noch ein Ganzfolgenwörterbuch: `OT+OL`, `OL+OL`, `OL+OT` und
`DY+OL` brauchten jeweils eigens formulierte Endstücke.

GDT571 benötigt nur noch drei Operator-Karten:

| Operator | kurzer Arbeitswert | Eingang | Nachläufer | Vorkommen |
|---|---|---|---|---:|
| OT | DANACH | Danach | eröffne danach den nächsten Gang | 404 |
| OL | FORTSETZEN | Weiter | führe den Gang weiter | 761 |
| DY | ABSCHLIESSEN | – | schließe den Schritt | 705 |

Nur fünf der sechs theoretischen Operator×Position-Zellen kommen vor. DY hat
keine Eingangsform. Das ist kein fehlender Default: Alle705 DY-Vorkommen stehen
im Nachläufer-Slot und schließen dort den Schritt.

## Die zwei Slots

Die Regel ist einfacher als die neun alten Rahmen:

1. Ist der erste Zustandsoperator OT oder OL, steht er als Eingangspräfix vor
   der konkreten Handlung: `Danach` oder `Weiter`.
2. Jedes DY und jeder weitere Operator steht nach Handlung und Modifikatoren.
   Mehrere Nachläufer bleiben in ihrer geschriebenen Reihenfolge.

Damit landen1.111 Operatoren im Eingangs- und759 im Nachläufer-Slot. Zusammen
sind das alle1.870 geschriebenen OT/OL/DY-Vorkommen. Keine Folge wird sortiert,
gekürzt oder als eigenes Wort gelernt.

| Folge | Karten | Zwei-Slot-Ausgabe |
|---|---:|---|
| OL | 619 | Weiter: … |
| DY | 544 | …; schließe den Schritt |
| OT | 279 | Danach: … |
| OT+DY | 86 | Danach: …; schließe den Schritt |
| OL+DY | 74 | Weiter: …; schließe den Schritt |
| OT+OL | 38 | Danach: …; führe den Gang weiter |
| OL+OL | 14 | Weiter: …; führe den Gang weiter |
| DY+OL | 1 | …; schließe den Schritt; führe den Gang weiter |
| OL+OT | 1 | Weiter: …; eröffne danach den nächsten Gang |

Gerade `OL+OL` zeigt den Vorteil: Die Wiederholung bleibt vollständig sichtbar,
weil das erste OL `Weiter` und das zweite `führe den Gang weiter` liefert. Das
zusätzliche gelernte Endstück „nochmals weiterführen“ ist nicht mehr nötig.

## Konkrete neue Lesungen

```text
OT+OL
alt: Danach: entnimm denselben laufenden Eintrag; weiterführen.
neu: Danach: entnimm denselben laufenden Eintrag; führe den Gang weiter.

OL+OL
alt: Weiter im laufenden Gang: wähle denselben Positionswert;
     nochmals weiterführen.
neu: Weiter im laufenden Gang: wähle denselben Positionswert;
     führe den Gang weiter.

OL+OT
alt: Weiter: kennzeichne den laufenden Eintrag;
     danach nächsten Gang eröffnen.
neu: Weiter: kennzeichne den laufenden Eintrag;
     eröffne danach den nächsten Gang.

DY+OL
alt: Setze denselben Stationswert im Stationsgang an; auf Grad II;
     schließe den Schritt; danach weiterführen.
neu: Setze denselben Stationswert im Stationsgang an; auf Grad II;
     schließe den Schritt; führe den Gang weiter.
```

Die beiden seltenen Umkehrungen werden also nicht wegerklärt. Sie sind gerade
die klarsten Demonstrationen dafür, dass der Nachläufer-Slot die Schriftfolge
wirklich ausspricht.

## Reichweite

53 nachlaufende OL und das eine nachlaufende OT erhalten eine finite Form.
Dadurch ändern sich54 Zustandszeilen,44 Aussagen und24 Seiten. Die übrigen1.602
Zustandszeilen sowie alle3.466 Nichtzustandszeilen bleiben bytegleich. Die
vollständige Ausgabe behält5.122 Ereignisse,793 Aussagen und30 Seiten; alle50
Prüfungen bestehen.

Der aktuelle Arbeitsbaukasten ist damit nochmals kleiner:19 kurze Wurzeln,
ownergebundene Fachstimme, zwei Kontextslots, typisierte Modifikatoren und für
die äußere Ablaufsteuerung drei Operatoren in zwei Slots. Eine lange Lesung wie
„Weiter …; führe den Gang weiter“ ist eine Komposition, keine Bedeutung von OL.

## Nächster Arbeitsweg

In den3.466 bisher unangetasteten Nichtzustandszeilen stehen noch zahlreiche
technische Auditformen wie `[wie zuvor]`, `[außen]` und `[innen]`. Der nächste
Pass soll zuerst ihren vollständigen Bestand zählen und prüfen, welche davon
mit denselben Kontext- und Koordinationskarten natürlich ausgesprochen werden
können. Dafür wird keine neue Seite und keine neue Wurzel benötigt.
