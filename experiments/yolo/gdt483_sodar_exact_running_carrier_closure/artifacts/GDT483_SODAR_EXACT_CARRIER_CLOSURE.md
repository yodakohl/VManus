# GDT483 — `sodar` ist eine alte Laufkarte

GDT482 ließ genau ein funktionales Restevent stehen: `sodar`. Im vollständigen zugelassenen Lauftext ist es jedoch kein Einzelstück. Dieselbe sichtbare Form mit demselben Rezept und derselben Komponentenlesung steht zweimal als laufende Karte.

| Träger | Seite | Register | Rolle | Rezept |
|---|---|---|---|---|
| `P1008-E1297` | f89r | PHARMA | LOCAL_ADDRESS_TARGET | `S+O+DA+R` |
| `G407-E0930` | f67r2 | CELESTIAL | RUNNING_EXACT_SURFACE_RECIPE_DONOR | `S+O+DA+R` |
| `G407-E2712` | f77r | BIOLOGICAL | RUNNING_EXACT_SURFACE_RECIPE_DONOR | `S+O+DA+R` |

Alle drei Träger lesen bytegleich `WÄHLEN · AUSFÜHRUNG · ZWEITE STUFE · MARKIEREN`. Die beiden laufenden Karten liegen in Himmels- und biologischem Register; die f89r-Karte liefert den pharmazeutischen dritten Träger.

## Konkrete Arbeitslesung

> **Wähle den Eintrag und markiere ihn – als Ausführung auf der zweiten Stufe.**

Im pharmazeutischen Besitzerkontext: **Wähle den Drogen- oder Zutateneintrag und markiere ihn – als Ausführung auf der zweiten Stufe.**

Das ist keine neue Wörterbuchbedeutung. Es glättet nur die bereits feste Zuordnung `S=WÄHLEN`, `O=AUSFÜHRUNG`, `DA=ZWEITE STUFE`, `R=MARKIEREN` zu einem natürlichen Satz. Die beiden alten Laufkarten benutzen je ein geerbtes Argument: auf f67r2 einen Sektoranteil, auf f77r einen Stationsposten.

## Der Funktionsblock `DA+R`

`DA` erscheint in 35 laufenden Events/20 Rezepten; `R` in 114/52. Das zusammenhängende `DA+R` steht 10-mal in vier Rezepten:

| Rezeptfamilie | Events |
|---|---:|
| `DA+R+Y` | 5 |
| `DA+R+A_ADDR+AM_ADDR` | 2 |
| `S+O+DA+R` | 2 |
| `L+DA+R` | 1 |

`DA+R` ist damit ein normaler geordneter Funktionsblock: *zweite Stufe markieren*. Auch die linke Hälfte ist gestützt: `S+O` steht dreizehnmal, `O+DA` sechsmal. Der ganze Vierer `S+O+DA+R` hat zwei laufende Ereignisse, eine konfliktfreie Oberfläche und zwei Register.

## Abschluss der 45 Restevents

| Abschlussart | Events |
|---|---:|
| im lokalen Eventbestand komponentenwiederkehrend | 42 |
| durch exakte laufende Oberfläche+Rezept geschlossen | 1 |
| erwartete gelernte Lexikalslots | 2 |
| ungeklärter funktionaler Rest | 0 |

Damit sind 43/45 Restevents funktional durch Wiederholung oder exakte Laufträger geschlossen; die anderen zwei sind bereits typisierte gelernte Namen/Familiennamen. Alle 45 haben eine konkrete Defaultlesung. Es bleibt kein unbekannter Funktionsbaustein aus dieser Restliste.
