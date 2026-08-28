# GDT593 — AIN und OR werden erstmals konkrete getragene Badeobjekte

## Ergebnis

Zwölf neutrale Badegut-Stellen sind jetzt konkret lesbar. Acht getragene
AIN-Werte ergeben `Anwendungsportion`; vier getragene OR-Werte ergeben die
Klasse `Einheit`—lokal Stationseinheit, nach Reset Badeinheit. Fünf lokale Quellen heißen anaphorisch `dieselbe`; in sieben
Reset-/Besitzerfällen steht nur der bestimmte Typ. Damit ändert sich das Gesamtprofil der 254
Badhandlungen wie folgt:

| Objektklasse | GDT592 | GDT593 |
|---|---:|---:|
| Körper | 53 | 53 |
| Stationsansatz | 81 | 81 |
| Badegut | 107 | 95 |
| Bade-/Stationseinheit | 9 | 13 |
| Anwendungsportion | 4 | 12 |
| gesamt | 254 | 254 |

Die kalten Badegut-Defaults sinken von 105 auf 93. Darin stecken noch 49
spezifische Y-Kandidaten und 44 Stellen ohne nutzbare spezifische Wurzel.

## Die zwölf Lesungen

| Ziel | Wurzel | neue Klausel |
|---|---|---|
| E1560 | OR | Halte dieselbe Stationseinheit im Bad auf Grad I |
| E1717 | AIN | Halte die Anwendungsportion im Bad auf Grad I |
| E1778 | AIN | Halte dieselbe Anwendungsportion im Bad auf Grad I |
| E1781 | AIN | Halte die Anwendungsportion im Bad auf Grad I |
| E2608 | AIN | Halte dieselbe Anwendungsportion im Bad auf Grad II |
| E2828 | OR | Halte die Badeinheit im Bad auf Grad II |
| E2997 | OR | Halte dieselbe Stationseinheit im Bad auf Grad I |
| E2998 | OR | Halte die Badeinheit im Bad auf Grad II |
| E3134 | AIN | Halte dieselbe Anwendungsportion im Bad auf Grad I |
| E3314 | AIN | Halte die Anwendungsportion im Bad auf Grad I |
| E3315 | AIN | Halte die Anwendungsportion im Bad auf Grad I |
| E3628 | AIN | Halte die Anwendungsportion im Bad auf Grad I |

Das ist spürbar konkreter als `Halte das zu badende Gut ...`, ohne eine
zusätzliche Stoffbedeutung zu erfinden. Lokales OR heißt absichtlich
`Stationseinheit`: Das entspricht der GDT569-Spur und dem bereits vorhandenen
OR-Handoff in GDT592. Nach einem Reset wird derselbe Einheitstyp am SH-Bad-Ziel
als `Badeinheit` neu realisiert. Die jeweils andere Form bleibt als
gleichklassige Alternative sichtbar.

## Schriftquelle und Besitzer-Default sind nicht dasselbe

Sechs Ziele haben eine kanonische gleichsatzinterne AIN/OR-Quelle:
E1560, E1778, E2608, E2997, E3134 und E3314. Bei fünf liegt kein Readerreset
dazwischen. E3314 bleibt der offene Sonderfall: AIN steht unmittelbar davor,
aber ein OT-Host eröffnet sichtbar den nächsten Arbeitsgang.

Die anderen sechs—E1717, E1781, E2828, E2998, E3315 und E3628—sind echte
GDT581-Besitzer-Defaults. Ihre nächstliegenden geschriebenen AIN/OR-Zeugen
liegen ein bis fünf Ereignisse zurück und im selben physischen Absatz, aber
über einer Satzgrenze. GDT593 nennt sie deshalb `context_witness` und nie
`object_source_event_id`. Der konkrete Typ kommt hier aus dem übernommenen
Kontextstamm, nicht aus einer fingierten lokalen Übergabe. Genau deshalb steht
dort `die`, nicht identitätsbehauptend `dieselbe`.

## Rivalen bleiben vollständig erhalten

Jede Karte bewahrt die bisherige Klausel, zum Beispiel:

```text
primär:  Halte die Anwendungsportion im Bad auf Grad I
Rivale:  Halte das zu badende Gut im Bad auf Grad I
```

Damit ist die Arbeitsedition mutiger, ohne die Rückkehr zum neutralen Default
zu verbauen. Die ältere GDT569-Form `Stationsanteil` bleibt ebenfalls im
Tabellenkanal; sie wird nicht stillschweigend gelöscht.

## Nächster Schritt

Y darf nicht durch dieselbe Regel laufen. Unter den 49 verbleibenden Fällen
gibt es lokale Donoren mit `Stationsansatz`, zwei mit `Strom` und zahlreiche
Besitzer-Defaults, bei denen die saubere SH-Bad-Umgebung körpernah gelesen
werden kann. Der nächste Pass muss daher occurrence-level zwischen lokaler
Donorbedeutung und `BODY_FIRST_PROVISIONAL` unterscheiden und Station sowie
Badegut als Rivalen behalten.

GDT593 öffnet keine neue Seite. Validierung: 64/64 Prüfungen grün, darunter die
exakte 8/4-Population, 6/6-Quellart, E3314 als einzige direkte Readerreset-
Ausnahme, vollständige Rivalen und byte-identischer Neubau aller Artefakte.
