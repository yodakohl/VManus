# Vollständige künstliche Schreibproben zu b6.7

5. Oktober 2026. Manuelle Konstruktion, keine Voynich-Übersetzung und keine Statistikbestätigung.
Schlüssel frei erfunden. Gleiche Zeichenfolgen im Manuskript erhalten dadurch keine Bedeutung.
Quelle und Lesart: `B6_7_MANUAL_SOURCE.json`; Regeln und Grenzen: `B6_7_MANUAL_DESIGN.md`.
Die Zeilen unten erleichtern die Kontrolle. Das angehängte `y` markiert den Satzanfang (bei9 das Ende); Umbruch ist frei.

## Gemeinsame manuelle Rücklesung

### 01

Quelle: Willthu machenn guett wlpratt von rindt fleisch

Lesart: Wenn du gutes Wildbret aus Rindfleisch machen willst: Die folgenden Anweisungen gehören zu diesem Ziel. Das Zielwort führt kein zusätzliches Wildfleisch als Zutat ein.

`IF_WANT(MAKE(GOOD(WILPRATT), FROM(BEEF)))`

### 02

Quelle: So hack es klein

Lesart: So hacke es klein. Der Bezug von es wird mitgeschrieben; Rindfleisch ist hier die naheliegende Lesart, kein im Code ersetzter Nomenwert.

`SO(DO(SMALL(CHOP(ES))))`

### 03

Quelle: vnd niem einenn sweiß von einem kalb

Lesart: Und nimm Blut von einem Kalb. Beide unbestimmten Einführungen bleiben erhalten; keine Maßzahl wird ergänzt. Die Kalbsblut-Lesart folgt der vorhandenen XML-Annotation.

`AND(DO(TAKE(INDEF(ORIGIN(BLOOD, INDEF(CALF))))))`

### 04

Quelle: vnd thu denn in einenn haffenn

Lesart: Und gib den/denn in einen Topf. Hier wird denn ausdrücklich als Pronomen den gelesen; sein Antezedent bleibt offen, Blut ist naheliegend. Eine zeitliche Lesart von denn mit unausgesprochenem Objekt wird durch diese manuelle Fassung nicht ebenfalls übertragen.

`AND(DO(PUT(DEN, IN(INDEF(POT)))))`

### 05

Quelle: vnd sez es vff ein collenn

Lesart: Und setze es auf Kohle/Glut. Das ursprüngliche es und ein bleiben erhalten; Gefäß und Gefäßinhalt werden nicht heimlich gleichgesetzt.

`AND(DO(SET(ES, ON(INDEF(COLLEN)))))`

### 06

Quelle: vnd ruer es biß es sydenn wurdt

Lesart: Und rühre es, bis es siedend wird. Das Eintreten dieses Zustands beendet die Rühranweisung; keine feste Zeit wird eingesetzt. Beide es bleiben ausgeschrieben.

`AND(DO(UNTIL(STIR(ES), BECOME(BOIL(ES)))))`

### 07

Quelle: so gewß es dan vff daß flech

Lesart: So gieße es dann auf das Fleisch. Das ausdrückliche dann, das offene es und der bestimmte Fleischbezug bleiben erhalten.

`SO(DO(THEN(POUR(ES, ON(DEF(MEAT))))))`

### 08

Quelle: So vecht es die gestalt alls wilpratt

Lesart: So vecht es die Gestalt wie Wildbret. Gemeint ist plausibel: Es nimmt eine wildbretartige Gestalt an. Das unsichere vecht bleibt als Quellwort stehen; wie ist Vergleich, nicht Identität.

`SO(VECHT(ES, LIKE(DEF(FORM), WILPRATT)))`

### 09

Quelle: vnd hack dar vnter eir vnd herthes brott

Lesart: Und hacke Eier und hartes Brot darunter. Hart bezieht sich auf Brot; Eier sind im Plural, aber nicht als hartgekocht bezeichnet. Darunter bleibt ein offener Bezug.

`AND(DO(CHOP_TO(JOIN(PLURAL(EGG), HARD(BREAD)), DARUNTER)))`

### 10

Quelle: vnd wurtz es woll abe

Lesart: Und würze es gut ab. Das es bleibt offen. Die Quellpartikel abe wird erhalten, ohne daraus einen zusätzlichen Arbeitsschritt abzuleiten.

`AND(DO(ABE(WELL(SEASON(ES)))))`

### 11

Quelle: vnd mach dann ballenn dar auß alls die veist

Lesart: Und mache dann Bälle daraus, wie die veist. Veist ist wahrscheinlich Faust; erhalten wird der Vergleich, ohne eine genaue Größe oder Vergleichsdimension einzusetzen. Die Bälle sind im Plural; daraus bleibt offen.

`AND(DO(THEN(MAKE(LIKE(PLURAL(BALL), DEF(VEIST)), DARAUS))))`

### 12

Quelle: vnd seidt die Inne einer fleisch pruee

Lesart: Und siede die in einer Fleischbrühe. Die ist ein pluralischer Rückverweis; Bälle sind naheliegend, werden aber nicht als versteckte Identitätsangabe eingesetzt.

`AND(DO(BOIL_IN(DIE, IN(INDEF(MEAT_BROTH)))))`

### 13

Quelle: vnd schneidt es klein alls das wilpratt

Lesart: Und schneide es klein wie das Wildbret. Der Vergleich wird an die Schneideanweisung gebunden; ob primär Größe, Art des Schneidens oder Erscheinung gemeint ist, bleibt offen.

`AND(DO(LIKE(SMALL(CUT(ES)), DEF(WILPRATT))))`

### 14

Quelle: vnd mach ein peffer dar zu

Lesart: Und mache ein peffer dazu. Die vorhandene Annotation bezeichnet ein Pfeffergericht; weder eine genaue Saucezusammensetzung noch eine bloße Pfeffermenge wird ergänzt.

`AND(DO(MAKE(INDEF(PEFFER), DARZU)))`

### 15

Quelle: vnd wurz es woll

Lesart: Und würze es gut. Ob sich es auf die zuletzt genannte Zubereitung oder das Fleisch bezieht, entscheidet die Schrift nicht zusätzlich.

`AND(DO(WELL(SEASON(ES))))`

### 16

Quelle: vnd lege das wilpratt dar ein

Lesart: Und lege das Wildbret darein. Das Quellwort bezeichnet im Zusammenhang plausibel das hergestellte Gericht; es wird kein neues Wildfleisch eingeführt. Darein bleibt ausgeschrieben.

`AND(DO(PUT(DEF(WILPRATT), DAREIN)))`

### 17

Quelle: vnd versalcz nicht

Lesart: Und versalze nicht: verboten ist Salzen im Übermaß. Es steht weder ein allgemeines Salzverbot noch ein ausgesprochenes Objekt im Text.

`AND(DO(NOT(EXCESS(SALT(UNSAID)))))`

## System 01

```text
kary kor kol kom kon ker
kany kam kel ken kem
kaly kam kir kil kin kim kil tar
kaly kam tal tan tam kil tor
kaly kam tol kem ton kil tom
kaly kam ter tel kem ten tem kem
kany kam tir til kem ton tin tim
kany par kem pal tin pan kom
kaly kam pam por pol pon pom per pel
kaly kam pen pem pir kem
kaly kam tir kor pal pol pil tin pin pim
kaly kam far fal tam kil fan
kaly kam pal kel fam kem tin kom
kaly kam kor kil for fol
kaly kam pem pir kem
kaly kam tal tin kom fon
kaly kam fom fer fel fen
```

119 geschriebene Wörter, 374 Arbeitszeichen, 59 Formen. Alle Definitionen mitgezählt.

## System 02

```text
korqaay komqoa kerqoo
kenqaeaioey kem
kirqaoaiy kinqoi kim tarqoi
talqaoaiy tan torqeaoi
tolqaoaiy kem tomqeooi
terqaoaiy tel kem ten tem kem
tilqaeaieey kem timqeoei
parqaey kem pal panqei kom
pamqaoaiy por ponqia perqio pel
pirqaoaiieiiy kem
korqaoaieey pal pilqia pinqei pim
farqaoaiy fal fanqeaoi
palqaoaiy famqoe kem komqei
korqaoaiy forqoi fol
pirqaoaiiiy kem
talqaoaiy komqei fon
felqaoaidadoy fen
```

58 geschriebene Wörter, 347 Arbeitszeichen, 47 Formen. Alle Definitionen mitgezählt.

## System 03

```text
kqaaqory kqoaqom kqooqer
kqaeaioeqeny kem
kqaoaiqiry kqoiqin kim tqoiqar
tqaoaiqaly tan tqeaoiqor
tqaoaiqoly kem tqeooiqom
tqaoaiqery tel kem ten tem kem
tqaeaieeqily kem tqeoeiqim
pqaeqary kem pal pqeiqan kom
pqaoaiqamy por pqiaqon pqioqer pel
pqaoaiieiiqiry kem
kqaoaieeqory pal pqiaqil pqeiqin pim
fqaoaiqary fal fqeaoiqan
pqaoaiqaly fqoeqam kem kqeiqom
kqaoaiqory fqoiqor fol
pqaoaiiiqiry kem
tqaoaiqaly kqeiqom fon
fqaoaidadoqely fen
```

58 geschriebene Wörter, 381 Arbeitszeichen, 47 Formen. Alle Definitionen mitgezählt.

## System 04

```text
kary kor kol fil tim fin kon kin tim fem
kany kam kel ken kem
kaly kam kir kil kin kim kil tar
kaly kam tal tan tam kil tor
kaly kam tol kem ton kil tom
kaly kam ter tel kem ten tem kem
kany kam tir til kem ton tin tim
kany par kem pal tin pan fil tim fin
kaly kam pam por pol pon pom per pel
kaly kam pen pem pir kem
kaly kam tir kor pal pol pil tin pin pim
kaly kam far fal tam kil kin fir tim
kaly kam pal kel fam kem tin fil tim fin
kaly kam kor kil for fol
kaly kam pem pir kem
kaly kam tal tin fil tim fin fon
kaly kam fom fer fel fen
```

131 geschriebene Wörter, 410 Arbeitszeichen, 60 Formen. Alle Definitionen mitgezählt.

## System 05

```text
kary kor kol r kon ker
my o kel ken e
ay o kir i kin kim i tar
ay o tal tan tam i tor
ay o tol e ton i tom
ay o ter tel e ten tem e
my o tir til e ton l tim
my par e pal l pan r
ay o pam por pol pon pom per pel
ay o pen n pir e
ay o tir kor pal pol pil l pin pim
ay o far fal tam i fan
ay o pal kel fam e l r
ay o kor i for fol
ay o n pir e
ay o tal l r fon
ay o fom fer fel fen
```

119 geschriebene Wörter, 260 Arbeitszeichen, 59 Formen. Alle Definitionen mitgezählt.

## System 06

```text
korqay kol kom kon ker
kelqey ken kem
kirqoy kil kin kim kil tar
talqoy tan tam kil tor
tolqoy kem ton kil tom
terqoy tel kem ten tem kem
tirqey til kem ton tin tim
parqiy kem pal tin pan kom
pamqoy por pol pon pom per pel
penqoy pem pir kem
tirqoy kor pal pol pil tin pin pim
farqoy fal tam kil fan
palqoy kel fam kem tin kom
korqoy kil for fol
pemqoy pir kem
talqoy tin kom fon
fomqoy fer fel fen
```

87 geschriebene Wörter, 312 Arbeitszeichen, 61 Formen. Alle Definitionen mitgezählt.

## System 07

```text
kary kor kol kom kon ker
kany kam kel ken kem
kaly kam kir kil kin kim kil tar
kaly kam tal tan tam kil tor
kaly kam tol kem ton kil tom
kaly kam ter tel yo ten tem yo
kany kam tir til yo ton tin tim
kany par yo pal tin pan kom
kaly kam pam por pol pon pom per pel
kaly kam pen pem pir kem
kaly kam tir kor pal pol pil tin pin pim
kaly kam far fal tam kil fan
kaly kam pal kel fam kem tin kom
kaly kam kor kil for fol
kaly kam pem pir kem
kaly kam tal tin kom fon
kaly kam fom fer fel fen
```

119 geschriebene Wörter, 370 Arbeitszeichen, 60 Formen. Alle Definitionen mitgezählt.

## System 08

```text
ray kar kor kol kom kon ker
ray kan kam kel ken kem
ray kal kam kir kil kin kim kil tar
rey tal tan tam kil tor
rey tol kem ton kil tom
rey ter tel kem ten tem kem
ray kan kam tir til kem ton tin tim
roy par kem pal tin pan kom
ray kal kam pam por pol pon pom per pel
rey pen pem pir kem
rey tir kor pal pol pil tin pin pim
rey far fal tam kil fan
rey pal kel fam kem tin kom
rey kor kil for fol
rey pem pir kem
rey tal tin kom fon
rey fom fer fel fen
```

113 geschriebene Wörter, 339 Arbeitszeichen, 62 Formen. Alle Definitionen mitgezählt.

## System 09

```text
kom kol ker kon kor kary
kem ken kel kam kany
kim tar kil kin kil kir kam kaly
tan tor kil tam tal kam kaly
kem tom kil ton tol kam kaly
kem tel kem tem ten ter kam kaly
kem tim tin ton til tir kam kany
kem pan tin kom pal par kany
pon pol per pom por pel pam kam kaly
kem pir pem pen kam kaly
pil pol pin tin pal pim kor tir kam kaly
fal fan kil tam far kam kaly
kem fam kel kom tin pal kam kaly
for kil fol kor kam kaly
kem pir pem kam kaly
kom tin fon tal kam kaly
fen fel fer fom kam kaly
```

119 geschriebene Wörter, 374 Arbeitszeichen, 59 Formen. Alle Definitionen mitgezählt.

## System 10

```text
may pem pir kem
kary kor kol kom kon ker
kany kam kel ken kem
kaly kam kir kil kin kim kil tar
kaly kam tal tan tam kil tor
kaly kam tol kem ton kil tom
kaly kam ter tel kem ten tem kem
kany kam tir til kem ton tin tim
kany par kem pal tin pan kom
kaly kam pam por pol pon pom per pel
kaly kam pen ra
kaly kam tir kor pal pol pil tin pin pim
kaly kam far fal tam kil fan
kaly kam pal kel fam kem tin kom
kaly kam kor kil for fol
kaly kam ra
kaly kam tal tin kom fon
kaly kam fom fer fel fen
```

119 geschriebene Wörter, 372 Arbeitszeichen, 61 Formen. Alle Definitionen mitgezählt.

## Vollständige gemeinsame Wurzeltafel

Keine Wurzel bedeutet einen ganzen Quellsatz. Stelligkeit und Argumentreihenfolge sind Teil des gelernten Schlüssels.
Der Leser braucht diese65 Einträge, die Zusatzregeln seines Systems und für neue Namen die Buchstabentafel. Das ist Lernaufwand, kein kostenloses Wissen.

| Begriff | Künstliche Wurzel | Ergänzungen | Bedeutung |
|---|---|---:|---|
| IF_WANT | `kar` | 1 | Wenn du [1] willst; Bedingung für den folgenden Rezeptabsatz |
| AND | `kal` | 1 | und [1]; Quellreihenfolge erhalten, keine zusätzlich behauptete zeitliche Relation |
| SO | `kan` | 1 | so [1]; quellensprachliche Folge-/Anschlussverknüpfung |
| DO | `kam` | 1 | Aufforderung an den Leser: [1] |
| MAKE | `kor` | 2 | machen/herstellen: Erzeugnis [1], Herkunft/Zusatzbezug [2] |
| GOOD | `kol` | 1 | gut: Eigenschaft von [1] |
| FROM | `kon` | 1 | aus/von [1] |
| WILPRATT | `kom` | 0 | Quellwort Wildbret; Ziel, Vergleich oder spätere Benennung ergeben sich aus dem Satz, kein neuer Referent |
| BEEF | `ker` | 0 | Rindfleisch |
| SMALL | `kel` | 1 | [1] klein ausführen; keine Zahl oder feste Stückgröße |
| CHOP | `ken` | 1 | [1] hacken |
| ES | `kem` | 0 | es; ursprünglicher, nicht aufgelöster Rückverweis |
| TAKE | `kir` | 1 | [1] nehmen |
| INDEF | `kil` | 1 | ein/eine/einem [1]; unbestimmte Einführung, keine zugesetzte Maßzahl |
| ORIGIN | `kin` | 2 | [1] von/aus [2] |
| BLOOD | `kim` | 0 | Blut; sweiß ist im vorhandenen XML als Kalbsblut annotiert |
| CALF | `tar` | 0 | Kalb |
| PUT | `tal` | 2 | [1] geben/legen, Zielbezug [2] |
| DEN | `tan` | 0 | denn als den gelesen; Pronominal-Lesart gesetzt, Antezedent offen; zeitliches denn ist damit nicht mitcodiert |
| IN | `tam` | 1 | in [1] |
| POT | `tor` | 0 | Topf/Hafen |
| SET | `tol` | 2 | [1] setzen, Ortsbezug [2] |
| ON | `ton` | 1 | auf [1] |
| COLLEN | `tom` | 0 | Quellwort collenn; Kohle/Glut, keine ergänzte Menge |
| UNTIL | `ter` | 2 | Tätigkeit [1] bis zum Eintreten der Bedingung [2] |
| STIR | `tel` | 1 | [1] rühren |
| BECOME | `ten` | 1 | Eintreten/Werden von [1] |
| BOIL | `tem` | 1 | [1] siedet |
| THEN | `tir` | 1 | dann [1] |
| POUR | `til` | 2 | [1] gießen, Zielbezug [2] |
| DEF | `tin` | 1 | das/die bestimmte [1] |
| MEAT | `tim` | 0 | Fleisch; der ausgeschriebene Nomenbezug wird nicht als neue Portion eingeführt |
| VECHT | `par` | 2 | Quellprädikat vecht: [1], Ergänzung [2]; Lesart nimmt an ist plausibel, nicht still eingesetzt |
| LIKE | `pal` | 2 | [1] wie [2]; Vergleich, keine Identitätsbehauptung; Vergleichsdimension bleibt offen |
| FORM | `pan` | 0 | Gestalt |
| CHOP_TO | `pam` | 2 | [1] hacken, mit dem geschriebenen Richtungs-/Mischbezug [2] |
| JOIN | `por` | 2 | [1] und [2] als koordinierte Bestandteile |
| PLURAL | `pol` | 1 | mehrere [1], ohne bestimmte Anzahl |
| EGG | `pon` | 0 | Ei |
| HARD | `pom` | 1 | hartes [1] |
| BREAD | `per` | 0 | Brot |
| DARUNTER | `pel` | 0 | darunter; nicht aufgelöster Rückverweis |
| ABE | `pen` | 1 | [1] ab; Quellpartikel abe bleibt erhalten, keine zusätzliche Handlung erfunden |
| WELL | `pem` | 1 | [1] gut ausführen |
| SEASON | `pir` | 1 | [1] würzen |
| BALL | `pil` | 0 | Ball/Ballen |
| VEIST | `pin` | 0 | Quellwort veist; wahrscheinlich Faust, keine genaue Maßzahl angenommen |
| DARAUS | `pim` | 0 | daraus; nicht aufgelöster Rückverweis |
| BOIL_IN | `far` | 2 | [1] sieden, Medium-/Ortsbezug [2]; ausdrücklich kein beliebiges Garen |
| DIE | `fal` | 0 | die; ursprünglicher pluralischer Rückverweis, keine still zugewiesene Identität |
| MEAT_BROTH | `fan` | 0 | Fleischbrühe |
| CUT | `fam` | 1 | [1] schneiden |
| PEFFER | `for` | 0 | Quellwort peffer; im vorhandenen XML Gericht pfeffer, keine Gewürzmenge oder Zutatenliste |
| DARZU | `fol` | 0 | dazu; nicht aufgelöster Rückverweis |
| DAREIN | `fon` | 0 | darein; nicht aufgelöster Rückverweis |
| NOT | `fom` | 1 | nicht [1]; Verneinung genau dieser Ergänzung |
| EXCESS | `fer` | 1 | [1] im Übermaß; zusammen mit Salzen: versalzen |
| SALT | `fel` | 1 | [1] salzen |
| UNSAID | `fen` | 0 | Objekt in der Quelle nicht ausgesprochen; kein ergänzter Gegenstand |
| CATTLE | `fem` | 0 | Rind |
| BROTH | `fir` | 0 | Brühe |
| KIND | `fil` | 2 | Grundbegriff [1] mit Artbestimmung [2] |
| WILD | `fin` | 0 | wild/Wild- als Artbestimmung |
| AFTER | `fim` | 2 | Tätigkeit [1] nach Eintreten der Bedingung [2] |
| IDENTITY | `char` | 2 | [1] ist identisch mit [2] |

## Gebundene Grammatikzeichen für2 und3

Die Folge läuft vom äußersten zum innersten Zusatz; gelesen wird durch Wiederanlegen in umgekehrter Reihenfolge.

| Zusatz | Zeichen |
|---|---|
| IF_WANT | `aa` |
| AND | `ao` |
| SO | `ae` |
| DO | `ai` |
| GOOD | `oa` |
| FROM | `oo` |
| SMALL | `oe` |
| INDEF | `oi` |
| IN | `ea` |
| ON | `eo` |
| THEN | `ee` |
| DEF | `ei` |
| PLURAL | `ia` |
| HARD | `io` |
| ABE | `ie` |
| WELL | `ii` |
| NOT | `da` |
| EXCESS | `do` |

## Kurzformen für5

| Begriff | Kurzform |
|---|---|
| AND | `a` |
| DO | `o` |
| ES | `e` |
| INDEF | `i` |
| DEF | `l` |
| WILPRATT | `r` |
| WELL | `n` |
| SO | `m` |

## Registerklassen für7

- `a`: BALL, BEEF, BLOOD, BREAD, BROTH, CALF, CATTLE, COLLEN, EGG, FORM, MEAT, MEAT_BROTH, PEFFER, POT, VEIST, WILD, WILPRATT.
- `o`: DARAUS, DAREIN, DARUNTER, DARZU, DEN, DIE, ES, UNSAID.
- `e`: BECOME, BOIL, BOIL_IN, CHOP, CHOP_TO, CUT, MAKE, POUR, PUT, SALT, SEASON, SET, STIR, TAKE, VECHT.
- `i`: ABE, AFTER, AND, DEF, DO, EXCESS, FROM, GOOD, HARD, IDENTITY, IF_WANT, IN, INDEF, JOIN, KIND, LIKE, NOT, ON, ORIGIN, PLURAL, SMALL, SO, THEN, UNTIL, WELL.

## Buchstabentafel für neue wörtliche Namen

Nur a–z in dieser Probe. Neues Wort = `s` + Dreiergruppen + `d`; null Ergänzungen.
Das ist ein ausgeschriebener Name in der Beispielsprache, keine Erklärung seiner Eigenschaften.

| Buchstabe | Gruppe |
|---|---|
| a | `aaa` |
| b | `aao` |
| c | `aae` |
| d | `aai` |
| e | `aoa` |
| f | `aoo` |
| g | `aoe` |
| h | `aoi` |
| i | `aea` |
| j | `aeo` |
| k | `aee` |
| l | `aei` |
| m | `aia` |
| n | `aio` |
| o | `aie` |
| p | `aii` |
| q | `oaa` |
| r | `oao` |
| s | `oae` |
| t | `oai` |
| u | `ooa` |
| v | `ooo` |
| w | `ooe` |
| x | `ooi` |
| y | `oea` |
| z | `oeo` |
