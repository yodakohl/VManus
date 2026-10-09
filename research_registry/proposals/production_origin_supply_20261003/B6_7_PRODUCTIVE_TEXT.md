# Vollständige Schreibprobe mit produktiven Stämmen

**Nur erfundene Codes. Keine Glossen für tatsächliche Voynichwörter.**
Leserregeln und Grenzen: [Bauplan](B6_7_PRODUCTIVE_STEMS.md).
Der Quelltext und seine17 gesetzten Lesarten bleiben in [der alten Quellenfassung](B6_7_MANUAL_SOURCE.json) unverändert.

## Das gesamte Rezept

```text
mfeya rkatayn qkakoyd
mfiyeis ia
mchayoi qyr ke nkoyr
mchoyoi io toylr
mcheyoi ia teymr
mckhayoi chi ia sha sho ia
msheyeik ia kaymt
meelqenelqarye ia ckho tiyt rkata
mofiyoi ckhe payp poyf iia
meolaonryoi apiych ia
mfeyoik ckho peyp lqenmcfhqaryt iio
moshoyoi ie qkikaylr
mckhoyoi shiys ia rkatayt
mfeyoi rfolckhnddncphryr iie
mapiyoich ia
mchoyoi rkatayt iii
mafayoishckh in
```

Ein `m` am Anfang kennzeichnet eine Aussage. Der Umbruch ist zur Kontrolle; er wird nicht benötigt.

## Vollständige Rücklesung der sichtbaren Schrift

### 01

Quelle: Willthu machenn guett wlpratt von rindt fleisch

`mfeya rkatayn qkakoyd`

Wenn du gutes Wildbret aus Rindfleisch machen willst: Die folgenden Anweisungen gehören zu diesem Ziel. Das Zielwort führt kein zusätzliches Wildfleisch als Zutat ein.

Rekonstruierte Struktur: `IF_WANT(MAKE(GOOD(KIND(MEAT, WILD)), FROM(ORIGIN(MEAT, CATTLE))))`

### 02

Quelle: So hack es klein

`mfiyeis ia`

So hacke es klein. Der Bezug von es wird mitgeschrieben; Rindfleisch ist hier die naheliegende Lesart, kein im Code ersetzter Nomenwert.

Rekonstruierte Struktur: `SO(DO(SMALL(CHOP(ES))))`

### 03

Quelle: vnd niem einenn sweiß von einem kalb

`mchayoi qyr ke nkoyr`

Und nimm Blut von einem Kalb. Beide unbestimmten Einführungen bleiben erhalten; keine Maßzahl wird ergänzt. Die Kalbsblut-Lesart folgt der vorhandenen XML-Annotation.

Rekonstruierte Struktur: `AND(DO(TAKE(INDEF(ORIGIN(BLOOD, INDEF(YOUNG(CATTLE)))))))`

### 04

Quelle: vnd thu denn in einenn haffenn

`mchoyoi io toylr`

Und gib den/denn in einen Topf. Hier wird denn ausdrücklich als Pronomen den gelesen; sein Antezedent bleibt offen, Blut ist naheliegend. Eine zeitliche Lesart von denn mit unausgesprochenem Objekt wird durch diese manuelle Fassung nicht ebenfalls übertragen.

Rekonstruierte Struktur: `AND(DO(PUT(DEN, IN(INDEF(POT)))))`

### 05

Quelle: vnd sez es vff ein collenn

`mcheyoi ia teymr`

Und setze es auf Kohle/Glut. Das ursprüngliche es und ein bleiben erhalten; Gefäß und Gefäßinhalt werden nicht heimlich gleichgesetzt.

Rekonstruierte Struktur: `AND(DO(SET(ES, ON(INDEF(COLLEN)))))`

### 06

Quelle: vnd ruer es biß es sydenn wurdt

`mckhayoi chi ia sha sho ia`

Und rühre es, bis es siedend wird. Das Eintreten dieses Zustands beendet die Rühranweisung; keine feste Zeit wird eingesetzt. Beide es bleiben ausgeschrieben.

Rekonstruierte Struktur: `AND(DO(UNTIL(STIR(ES), BECOME(BOIL(ES)))))`

### 07

Quelle: so gewß es dan vff daß flech

`msheyeik ia kaymt`

So gieße es dann auf das Fleisch. Das ausdrückliche dann, das offene es und der bestimmte Fleischbezug bleiben erhalten.

Rekonstruierte Struktur: `SO(DO(THEN(POUR(ES, ON(DEF(MEAT))))))`

### 08

Quelle: So vecht es die gestalt alls wilpratt

`meelqenelqarye ia ckho tiyt rkata`

So vecht es die Gestalt wie Wildbret. Gemeint ist plausibel: Es nimmt eine wildbretartige Gestalt an. Das unsichere vecht bleibt als Quellwort stehen; wie ist Vergleich, nicht Identität.

Rekonstruierte Struktur: `SO(QUOTE2:vecht(ES, LIKE(DEF(FORM), KIND(MEAT, WILD))))`

### 09

Quelle: vnd hack dar vnter eir vnd herthes brott

`mofiyoi ckhe payp poyf iia`

Und hacke Eier und hartes Brot darunter. Hart bezieht sich auf Brot; Eier sind im Plural, aber nicht als hartgekocht bezeichnet. Darunter bleibt ein offener Bezug.

Rekonstruierte Struktur: `AND(DO(REL(CHOP(JOIN(PLURAL(EGG), HARD(BREAD))), DARUNTER)))`

### 10

Quelle: vnd wurtz es woll abe

`meolaonryoi apiych ia`

Und würze es gut ab. Das es bleibt offen. Die Quellpartikel abe wird erhalten, ohne daraus einen zusätzlichen Arbeitsschritt abzuleiten.

Rekonstruierte Struktur: `AND(DO(QUOTE1:abe(WELL(APPLY(SPICE, ES)))))`

### 11

Quelle: vnd mach dann ballenn dar auß alls die veist

`mfeyoik ckho peyp lqenmcfhqaryt iio`

Und mache dann Bälle daraus, wie die veist. Veist ist wahrscheinlich Faust; erhalten wird der Vergleich, ohne eine genaue Größe oder Vergleichsdimension einzusetzen. Die Bälle sind im Plural; daraus bleibt offen.

Rekonstruierte Struktur: `AND(DO(THEN(MAKE(LIKE(PLURAL(BALL), DEF(LIT:veist)), DARAUS))))`

### 12

Quelle: vnd seidt die Inne einer fleisch pruee

`moshoyoi ie qkikaylr`

Und siede die in einer Fleischbrühe. Die ist ein pluralischer Rückverweis; Bälle sind naheliegend, werden aber nicht als versteckte Identitätsangabe eingesetzt.

Rekonstruierte Struktur: `AND(DO(REL(BOIL(DIE), IN(INDEF(ORIGIN(BROTH, MEAT))))))`

### 13

Quelle: vnd schneidt es klein alls das wilpratt

`mckhoyoi shiys ia rkatayt`

Und schneide es klein wie das Wildbret. Der Vergleich wird an die Schneideanweisung gebunden; ob primär Größe, Art des Schneidens oder Erscheinung gemeint ist, bleibt offen.

Rekonstruierte Struktur: `AND(DO(LIKE(SMALL(CUT(ES)), DEF(KIND(MEAT, WILD)))))`

### 14

Quelle: vnd mach ein peffer dar zu

`mfeyoi rfolckhnddncphryr iie`

Und mache ein peffer dazu. Die vorhandene Annotation bezeichnet ein Pfeffergericht; weder eine genaue Saucezusammensetzung noch eine bloße Pfeffermenge wird ergänzt.

Rekonstruierte Struktur: `AND(DO(MAKE(INDEF(KIND(DISH, LIT:peffer)), DARZU)))`

### 15

Quelle: vnd wurz es woll

`mapiyoich ia`

Und würze es gut. Ob sich es auf die zuletzt genannte Zubereitung oder das Fleisch bezieht, entscheidet die Schrift nicht zusätzlich.

Rekonstruierte Struktur: `AND(DO(WELL(APPLY(SPICE, ES))))`

### 16

Quelle: vnd lege das wilpratt dar ein

`mchoyoi rkatayt iii`

Und lege das Wildbret darein. Das Quellwort bezeichnet im Zusammenhang plausibel das hergestellte Gericht; es wird kein neues Wildfleisch eingeführt. Darein bleibt ausgeschrieben.

Rekonstruierte Struktur: `AND(DO(PUT(DEF(KIND(MEAT, WILD)), DAREIN)))`

### 17

Quelle: vnd versalcz nicht

`mafayoishckh in`

Und versalze nicht: verboten ist Salzen im Übermaß. Es steht weder ein allgemeines Salzverbot noch ein ausgesprochenes Objekt im Text.

Rekonstruierte Struktur: `AND(DO(NOT(EXCESS(APPLY(SALT_MATERIAL, UNSAID)))))`

## Neue Bildungen ohne neue Stammeinträge

| Inhalt | Geschriebene Form |
|---|---|
| Kalbsfleisch | `mqkanko` |
| Rinderblut | `mqkeko` |
| Brühe aus Kalbsfleisch | `mqkiqkanko` |
| Brühe aus Salbei | `mqkilcfhaponmr` |
| Versehe Fleisch mit Blut | `makeyi ka` |
| Versehe Fleisch nicht mit Blut | `makeyish ka` |

## Vollständige Grundstammtafel

| Begriff | Code | Ergänzungen | Bedeutung |
|---|---|---:|---|
| MEAT | `ka` | 0 | Fleisch |
| CATTLE | `ko` | 0 | Rind |
| BLOOD | `ke` | 0 | Blut |
| BROTH | `ki` | 0 | Brühe |
| WILD | `ta` | 0 | Wild- als Artbestimmung |
| POT | `to` | 0 | Topf |
| COLLEN | `te` | 0 | Kohle/Glut; Quellwort collenn |
| FORM | `ti` | 0 | Gestalt |
| EGG | `pa` | 0 | Ei |
| BREAD | `po` | 0 | Brot |
| BALL | `pe` | 0 | Ball/Ballen |
| SPICE | `pi` | 0 | Gewürz |
| SALT_MATERIAL | `fa` | 0 | Salz |
| DISH | `fo` | 0 | Gericht |
| MAKE | `fe` | 2 | machen: Erzeugnis, Herkunft/Zusatzbezug |
| CHOP | `fi` | 1 | hacken: Objekt |
| TAKE | `cha` | 1 | nehmen: Objekt |
| PUT | `cho` | 2 | geben/legen: Objekt, Zielbezug |
| SET | `che` | 2 | setzen: Objekt, Ortsbezug |
| STIR | `chi` | 1 | rühren: Objekt |
| BECOME | `sha` | 1 | Eintreten/Werden: Zustand |
| BOIL | `sho` | 1 | sieden: Träger |
| POUR | `she` | 2 | gießen: Objekt, Zielbezug |
| CUT | `shi` | 1 | schneiden: Objekt |
| UNTIL | `ckha` | 2 | Tätigkeit bis zum Eintritt einer Bedingung |
| LIKE | `ckho` | 2 | Vergleich: Verglichenes, Vergleichsgegenstand |
| JOIN | `ckhe` | 2 | Koordination von zwei Bestandteilen |
| AFTER | `ckhi` | 2 | Tätigkeit nach Eintritt einer Bedingung |
| IDENTITY | `ctha` | 2 | Identität zweier Angaben |

## Grammatische Zusätze nach y

| Aufgabe | Zeichen |
|---|---|
| IF_WANT | `a` |
| AND | `o` |
| SO | `e` |
| DO | `i` |
| GOOD | `n` |
| FROM | `d` |
| SMALL | `s` |
| INDEF | `r` |
| IN | `l` |
| ON | `m` |
| THEN | `k` |
| DEF | `t` |
| PLURAL | `p` |
| HARD | `f` |
| WELL | `ch` |
| NOT | `sh` |
| EXCESS | `ckh` |

Die Folge bewahrt den Geltungsbereich außen→innen. DO ist Aufforderung; AND ist und, keine erfundene Zeitrelation. IF_WANT gilt für den folgenden Rezeptabsatz. Die übrigen Bedeutungen stehen in der unveränderten [vorherigen vollständigen Tafel](B6_7_MANUAL_TEXTS.md).

## Offene Rückverweise

| Form | Schreibweise |
|---|---|
| ES | `ia` |
| DEN | `io` |
| DIE | `ie` |
| UNSAID | `in` |
| DARUNTER | `iia` |
| DARAUS | `iio` |
| DARZU | `iie` |
| DAREIN | `iii` |

## Buchstabiertafel für unbekannte Namen

| Buchstabe | Zeichenfolge |
|---|---|
| a | `a` |
| b | `o` |
| c | `e` |
| d | `i` |
| e | `n` |
| f | `d` |
| g | `s` |
| h | `l` |
| i | `m` |
| j | `k` |
| k | `t` |
| l | `p` |
| m | `f` |
| n | `ch` |
| o | `sh` |
| p | `ckh` |
| q | `cth` |
| r | `cph` |
| s | `cfh` |
| t | `qa` |
| u | `qo` |
| v | `qe` |
| w | `qi` |
| x | `qn` |
| y | `qd` |
| z | `qs` |

Unbekanntes = `l` + Buchstabierung + `r`. Ein unbekanntes Prädikat beginnt mit `e` und `a/o/e/i` für0/1/2/3 Ergänzungen, dann folgt sein ausgeschriebener Name. Kein verstecktes Wörterbuch ergänzt seine Bedeutung.

## Bedeutungsgegensätze und eine formale Reihenfolgeprobe

- `mckha chi ia sha sho ia` → `UNTIL(STIR(ES), BECOME(BOIL(ES)))`; `mckhi chi ia sha sho ia` → `AFTER(STIR(ES), BECOME(BOIL(ES)))`.
- `mckho ti rkata` → `LIKE(FORM, KIND(MEAT, WILD))`; `mctha ti rkata` → `IDENTITY(FORM, KIND(MEAT, WILD))`.
- `mafayshckh in` → `NOT(EXCESS(APPLY(SALT_MATERIAL, UNSAID)))`; `mafaysh in` → `NOT(APPLY(SALT_MATERIAL, UNSAID))`.
- `mckhe payp poyf` → `JOIN(PLURAL(EGG), HARD(BREAD))`; `mckhe payfp po` → `JOIN(HARD(PLURAL(EGG)), BREAD)`.
- `mapi ia` → `APPLY(SPICE, ES)`; `mapi qkako` → `APPLY(SPICE, ORIGIN(MEAT, CATTLE))`.

Die letzte Paarung prüft nur die unterschiedliche Operatorreihenfolge; der Ausdruck Übermaß(Nicht(...)) ist damit nicht als natürliche Rezeptanweisung bestätigt.

- `mafayshckh ia` → `NOT(EXCESS(APPLY(SALT_MATERIAL, ES)))`; `mafayckhsh ia` → `EXCESS(NOT(APPLY(SALT_MATERIAL, ES)))`.
