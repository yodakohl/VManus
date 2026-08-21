# V15 R1 — visuell gebundenes Anwendungsdeck der Bio-Werkstatt

Date: 2026-08-21

Status: **explorative Arbeitshypothese, kein GDT-Ergebnis und keine
Uebersetzung**. Perspektive R1: Lehrmeister einer Schreibwerkstatt um 1420.

## Entscheidung vorweg

Die vier 12/10/8/8-Familien sind am einfachsten als ein **kleines Deck
kategorialer Anwendungs- oder Konfigurationswerte** zu lehren. Das Deck bildet
keine vier sichtbaren Bauteile eins zu eins ab. Die Zeichnung und der lokale
Textblock liefern vielmehr die Frage; die Karte liefert eine wiederverwendbare
Antwort, und DY bestaetigt die Zelle.

Die beste konkrete, aber bewusst vorlaeufige Werkstatttaxonomie lautet:

```text
V-Q   := STANDARD / UNVERAENDERT / GRUNDSTELLUNG
V-QE  := DURCHLAUF / ZIRKULIEREND / WEITERGELEITET
V-L   := LOKAL ANSETZEN / AM KOERPER ODER ENDE ANWENDEN
V-S   := HALTEN / RUHEN / ZURUECKHALTEN
```

Das sind Quellklassen, keine Woerterbuchuebersetzungen. Sie sind so gewaehlt,
dass jedes Vorkommen sinnvoll bleiben kann: `STANDARD` kann in Becken, Koerper,
Weg oder Gesamtformular gelten; `DURCHLAUF` kann an Becken, Leitung, Knoten oder
Auslass stehen; `LOKAL` ist nicht auf eine bestimmte Figur beschraenkt; und
`HALTEN` bezeichnet einen Prozesszustand, keinen gezeichneten Gegenstand.

Arbeitskonfidenzen:

| Behauptung | Konfidenz |
|---|---:|
| vier stabile Nutzlastfamilien plus gemeinsamer Commit | .93 |
| latentes Anwendungs-/Konfigurationsdeck | **.68** |
| Werte reagieren teilweise auf sichtbare Funktionszonen | .55 |
| feste Karte = festes gezeichnetes Bauteil | .24 |
| `V-Q = STANDARD` | .56 |
| `V-QE = DURCHLAUF/ZIRKULIEREND` | .49 |
| `V-L = LOKAL/AM ENDE ANWENDEN` | .47 |
| `V-S = HALTEN/RUHEN` | .39 |

Der staerkste Rivale ist ein **seiten- und stencilgebundener Kadenzwert ohne
sichtbare Bedeutung** (`.41`): Die Familienwahl koennte vor allem vom lokalen
Exemplar, von Feldlaenge und Abschlussrhythmus abhaengen. Dieser Rivale bleibt
ernst, weil Seite und Bildrolle stark konfundiert sind. Gewoehnliche
abgekuerzte Prosa ist ein zweiter Rivale (`.34`).

## Scope und saubere Grenze

Verwendet wurden ausschliesslich `f81v`, `f82r` und `f83r`, ihre Seitenbilder
und die bereits veroeffentlichten, bewachten Bio-Sichten. `f84` und `f84r`
blieben versiegelt. Es wurden keine weiteren Voynich-Seiten, keine OCR, keine
Bildklassifikation, keine Laut- oder Sprachsuche und keine V15-Geschwister
verwendet.

Die vier exakten Familien nach dem Reveal sind:

| V15-Label | exakter Tuple-Prefix | n | Seiten |
|---|---|---:|---|
| `V-S` | `bc4f1f5c006c74a4d26d` | 12 | f81v 4; f82r 1; f83r 7 |
| `V-QE` | `7d25241b0e56c836372a` | 10 | f82r 5; f83r 5 |
| `V-Q` | `7db18b2f0fb7ed0fcfd3` | 8 | f81v 3; f83r 5 |
| `V-L` | `de7321bface5628e35d6` | 8 | f82r 1; f83r 7 |

Die Reihenfolge der letzten beiden Prefixe folgt dem publizierten
Seitenprofil: `V-Q` ist die 3/0/5-Familie, `V-L` die 0/1/7-Familie. Die
sichtbaren Formen `shedy/qokeedy/qokedy/lchedy` sind Renderer-Realisierungen,
nicht vier gelesene Woerter.

## Pre-Reveal-Freeze

Die 38 neutralen Positionen wurden zuerst nur als `O01`–`O38` mit
Locus/Feld, Textblock, sichtbarer Rolle, Konfidenz und Besitzbegruendung
geschrieben. Keine Rollen wurden nach dem Reveal geaendert.

```text
freeze UTC: 2026-08-21T17:07:54Z
role TSV:   V15_R1_PRE_REVEAL_VISUAL_ROLES.tsv
SHA-256:    b96b07a41c6e0963460f92c140ea245cbfa996d976208fa8bfdbade077b3adc2
rows:       38
```

Rollenbilanz vor Reveal:

| Rolle | n |
|---|---:|
| `VESSEL_POOL_OR_CONTAINER` | 11 |
| `FIGURE_OR_BODY` | 7 |
| `CONDUIT_PATH_OR_FLOW` | 6 |
| `JUNCTION_OR_INTERMEDIATE_STATION` | 4 |
| `VISUALLY_UNOWNED` | 4 |
| `GENERAL_CONFIGURATION_OR_PAGE_OWNER` | 3 |
| `TERMINAL_OUTLET_OR_ENDPOINT` | 3 |

Wichtige Einschraenkung: Bei der Dateisuche erschien vor dem formalen Freeze
versehentlich ein kurzer Ausschnitt aus einem aelteren Terminalaudit mit zehn
Oberflaechenzeilen, jedoch ohne die zugehoerige Familienueberschrift. Die
Rollenkarte wurde nicht nach Familien gruppiert und benutzt keine
Identitaetsspalte; dennoch ist dies **kein vollkommen blinder Freeze**. Der
Hash dokumentiert, was tatsaechlich vor dem vollstaendigen Reveal feststand.

Die Besitzregel war streng blockbezogen. Der Zeichner arbeitete wahrscheinlich
vor dem Textschreiber; deshalb ist Naehe allein schwach. Auf f81v gehoert der
untere Textblock dem grossen Gemeinschaftsbecken, nicht einzelnen Frauen. Auf
f82r wurden oberes Apparatefeld und unterer Beckenblock getrennt. Auf f83r
wurden Koerper-, Bogen/Leitungs- und unklarer unterer Rechtsblock getrennt.
Vier spaete f83r-Positionen blieben absichtlich `VISUALLY_UNOWNED`.

Vollstaendige Freeze- und Reveal-Artefakte:

- `V15_R1_PRE_REVEAL_VISUAL_ROLES.tsv` — alle 38 neutralen Positionen;
- `V15_R1_PRE_REVEAL_FREEZE.json` — Zeit, Hash und Bildhashes;
- `V15_R1_REVEALED_VALUE_ROLE_JOIN.tsv` — unveraenderte Rollen plus Familie.

## Value × role nach Reveal

| Familie | FIGURE | VESSEL | CONDUIT | JUNCTION | TERMINAL | GENERAL | UNOWNED | total |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `V-S` | 2 | 4 | 2 | 2 | 0 | 0 | 2 | 12 |
| `V-QE` | 1 | 4 | 3 | 1 | 1 | 0 | 0 | 10 |
| `V-Q` | 1 | 2 | 1 | 1 | 0 | 3 | 0 | 8 |
| `V-L` | 3 | 1 | 0 | 0 | 2 | 0 | 2 | 8 |
| total | 7 | 11 | 6 | 4 | 3 | 3 | 4 | 38 |

Die Rohassoziation ist sichtbar, aber nicht sauber identifiziert. Der
ungewichtete Kontingenzwert ist `chi2=27.10`, Cramer's `V=.488`; Seite selbst
hat ebenfalls einen starken Zusammenhang mit Familie (`V=.446`). Bei 38
postselektierten Ereignissen und mehreren kleinen Zellen ist das eine
Beschreibung, kein Signifikanzbeweis.

Drei Muster tragen die Arbeitstaxonomie:

1. `V-Q` besitzt **alle 3/3 GENERAL-Zellen** und wird auf f81v.18 sowie
   f83r.20 in direkt benachbarten Zellen wiederholt. Ein neutraler
   Standard-/Grundwert ist dafuer die einfachste Lehre.
2. `V-QE` liegt in **7/10 Faellen an Becken oder Leitung** und besitzt kein
   `VISUALLY_UNOWNED`. Das stuetzt Durchlauf/Zirkulation, wenn auch nur
   explorativ.
3. `V-L` liegt in **5/8 Faellen an Koerper oder Auslass**, gegenueber 10/38
   solcher Rollen insgesamt. Es fehlt ganz an Leitung, Knoten und GENERAL.
   Das macht lokale Anwendung bzw. Endstellenwert plausibel.

`V-S` ist absichtlich die breiteste Karte. Sie verteilt sich auf Becken,
Leitung, Knoten, Koerper und ungebundene Zellen. Ein Gegenstandsname waere
damit unbrauchbar; ein ortsunabhaengiges `halten/ruhen/zurueckhalten` bleibt
moeglich. Seine 3/12 Singleton-Rate ist geringer als bei `V-QE` und `V-L`, was
zu einem Wert passt, der haeufig nach Qualifikatoren gesetzt wird.

Die vier `VISUALLY_UNOWNED`-Zeilen wurden nicht attraktiv umverteilt. Sie sind
zweimal `V-L`, zweimal `V-S`. Das schwaecht jede harte Gegenstandskarte, laesst
aber die Prozess-/Anwendungstaxonomie stehen.

## f82r.27: sieben Zellen ohne erfundene Eigentuemerschaft

Die Zeile lautet formal:

```text
A | (B,b) | V-QE | D | E | V-QE | F
```

Die beiden nicht benachbarten `V-QE`-Zellen F3 und F6 wurden vor Reveal beide
als `VESSEL_POOL_OR_CONTAINER`, `HIGH`, eingefroren. Das ist eine positive
Antwort auf die enge Frage des Protokolls: Sie besetzen **vergleichbare
Blockrollen**. Es ist aber keine Lizenz, F3 und F6 zwei gezeichneten Rohren
oder Frauen zuzuweisen. Die sichere Lesung ist:

> Fuer die untere Beckenanordnung: bestaetige A; setze B mit Zusatz b;
> waehle fuer den dritten Slot den Durchlauf-/Zirkulationswert C; bestaetige D
> und E; setze fuer den korrespondierenden sechsten Slot nochmals genau C;
> bestaetige zuletzt F.

Eine konkretere Werkstattlehre darf sagen: „zwei verschiedene Fragen erhalten
denselben Betriebszustand“. Sie darf **nicht** sagen: „dieses linke Rohr und
jenes rechte Rohr gehoeren nachweislich derselben Frau“. Die Seite besitzt
keine unabhaengige Zellen-zu-Bauteil-Karte.

## Drei kontinuierliche Ruecklesungen

Die folgenden Lesungen decken alle 38 Zielereignisse in Seitenreihenfolge ab.
`[OPAQUE]` bezeichnet die uebrigen bestaetigten Werte; kein Text wird als
beweisbarer Satz ausgegeben.

### f81v — Gemeinschaftsbecken mit Grund- und Haltezustand

Zielsequenz:

```text
line 2:  V-Q
line 17: V-S
line 18: V-S | V-Q | V-Q
line 24: V-S
line 27: V-S
```

> Lege fuer die obere allgemeine Konfiguration die Grundstellung fest. Fuer
> das grosse gemeinschaftliche Becken halte den qualifizierten Ansatz; halte
> in der naechsten Zelle wiederum den angegebenen Ansatz und setze dann zwei
> benachbarte Slots beide auf Grundstellung. Nach den dazwischenliegenden
> opaken Angaben waehle erneut Halten/Ruhen und bestaetige denselben
> Betriebsmodus am Ende des Beckenblocks.

Das ist besser als `V-Q = Becken`, denn `V-Q` steht einmal im oberen
allgemeinen Block und zweimal im Beckenblock. Das Bild liefert den Gegenstand;
die Karte liefert den Zustand.

### f82r — vom oberen Apparat zum unteren Becken

Zielsequenz:

```text
upper apparatus: V-QE ; V-S
lower pool block: V-QE ; V-L ; V-QE ;
line 27: [A] | [B,b] | V-QE | [D] | [E] | V-QE | [F]
```

> Stelle am oberen Zwischenapparat zuerst Durchlauf her und setze den spaeteren
> Knoten auf Halten. Im unteren Beckenblock waehle Durchlauf, dann eine lokale
> Anwendung, danach wieder Durchlauf. In der letzten Siebenzellenzeile
> bestaetige A und B mit Zusatz; gib dem dritten und dem sechsten Slot denselben
> Durchlaufwert; lasse D, E und F als ihre eigenen exakten Antworten stehen.

Die Lesung macht aus `V-QE` keinen Stoffnamen: Dasselbe Medium waere moeglich,
aber die Wiederholung in verschiedenen geerbten Slots passt mindestens ebenso
gut zu einem Betriebszustand.

### f83r — Koerper-, Leitungs- und Endstellenkarte

Zielsequenz nach Bildzone:

```text
upper outlet:      V-L ; V-QE | V-L
body block:        V-S | V-Q | V-L ; V-QE | V-S | V-L ; V-L
block transition:  V-Q | V-Q
arch/path block:   V-QE ; V-S ; V-QE | V-Q ; V-S ; V-QE ; V-Q | V-S
unowned tail:      V-L | V-S ; V-L ; V-S
```

> Am oberen Auslass setze die lokale Anwendung; fuehre den naechsten Zustand
> durch und bestaetige wieder die lokale Endstellenart. Im Koerperblock halte
> einen Ansatz, setze den folgenden Slot auf Standard und den spaeteren lokal;
> danach folgen Durchlauf, Halten und lokale Anwendung, nochmals lokal. Am
> Uebergang erhalten zwei benachbarte Slots dieselbe Grundstellung. Im
> Bogen-/Leitungsblock wechseln Durchlauf, Halten, Durchlauf, Standard, Halten,
> Durchlauf und zuletzt Standard plus Halten. Der visuell ungebundene Schwanz
> schliesst mit lokal, halten, lokal, halten.

Gerade der ungebundene Schwanz ist nuetzlich: Er zwingt `V-L` und `V-S`, als
abstrakte Anwendungen/Zustaende zu funktionieren, statt als huebsche Namen der
naechsten Zeichnung.

## Die kleinste lehrbare Produktionsregel

Ein Lehrling braucht keine moderne Tabelle und keine vier uebersetzten
Vokabeln. Er erhaelt ein Bio-Exemplar mit vier Ganzkarten und Beispielzellen:

```text
1. BESTIMME DEN AKTIVEN BILDBLOCK:
   Koerper | Becken | Weg | Knoten | Ende | allgemeine Konfiguration.

2. LIES DIE FRAGE AUS STENCIL UND ROUTINE:
   Die Frage muss nicht im Feld wiederholt werden.

3. KOPIERE OPTIONAL QUALIFIKATOREN.

4. WAEHLE GENAU EINE WERTKARTE:
   V-Q  Grundstellung
   V-QE durchlaufend
   V-L  lokal/endstaendig
   V-S  haltend/ruhend

5. SETZE DEN GEMEINSAMEN COMMIT.
   Der Commit ist nicht die Bedeutung der Wertkarte.

6. PRUEFE EXAKTE KARTENIDENTITAET, NICHT BUCHSTABENKLANG.
```

Die Karten bilden keine Skala und keine feste Stationsfolge. Derselbe Wert darf
in benachbarten oder nicht benachbarten Slots wiederholt werden. Ein anderer
Slot darf dieselbe Karte anders fluessig expandieren, solange die gemeinsame
Zustandsklasse erhalten bleibt.

Typische Lehrlingsfehler waeren:

- `V-Q` und `V-QE` wegen aehnlicher sichtbarer Realisierung zu verwechseln;
- den Wert korrekt, aber den angehaengten Commit falsch oder doppelt zu setzen;
- den Becken-, Koerper- oder Leitungsbesitzer in jeder Zelle auszuschreiben,
  obwohl ihn das Bild erbt;
- f82r.27 F6 aus Gewohnheit als neuen Wert statt als exakte Wiederholung von
  F3 zu kopieren;
- aus den vier Karten eine falsche Reihenfolge oder Heiss/Kalt-Skala zu bauen;
- eine f83r-haeufige Karte blind in das f81v- oder f82r-Exemplar zu tragen.

Ein Korrektor prueft deshalb in dieser Reihenfolge: Bildblock, Feldgrenzen,
optionale Qualifikatoren, exakte Wertkarte, Commit, Wiederholungen. Er prueft
nicht die vermutete Aussprache.

## Rivalen und Widersprueche

### 1. Generischer Stencil-/Kadenzwert — staerkster Rivale

Der Rivale erklaert die starke Seitenkonfundierung, mobile Feldordnungen und
das Fehlen einer unabhaengigen Bauteilkarte. `V-Q` fehlt f82r ganz; `V-L` liegt
7/8-mal auf f83r. Ein lokales Abschreibexemplar kann solche Profile ohne
Semantik erzeugen.

Er erklaert aber schlechter, warum die vier exakten Hosts unterschiedliche
Singleton-Raten besitzen, warum `V-Q` und `V-QE` absichtlich wiederholt werden
und warum die Werte trotz gemeinsamem Commit stabil getrennt bleiben. Darum
bleibt er knapp hinter dem latenten Konfigurationsdeck.

### 2. Gewoehnliche abgekuerzte Prosa

Vier haeufige Karten koennten Verben, Produkte oder Ergebnisformeln wie
„halte“, „wende an“, „fertig“ oder „erprobt“ abkuerzen. Historisch ist das
unproblematisch. Sechzehn von 38 Zielzellen bestehen jedoch nur aus der
Wertkarte; mehrere Werte stehen in einer einzigen Recordzeile, und alle tragen
dieselbe formale Commit-Schicht. Das sieht eher wie Antworten auf geerbte
Fragen als wie vollstaendige wiederholte Prosaklauseln aus.

### 3. Vier sichtbare Stationsnamen

Die Value×role-Tabelle widerspricht einer harten Stationslesung. `V-S` spannt
fuenf Rollen, `V-QE` ebenfalls fuenf, und selbst die besten Konzentrationen
sind nicht exklusiv. Dieser Rivale wird verworfen. Eine **weiche**
Stationsabhaengigkeit bleibt als Kontext fuer abstrakte Werte erhalten.

### 4. Medium-/Badklassen

`V-QE` koennte statt Durchlauf ein wiederkehrendes Arbeitsmedium oder eine
Badklasse sein; sieben seiner zehn Faelle liegen an Becken/Leitung. Das bleibt
der beste konkrete Bedeutungsrivale innerhalb des medizinischen Forks
(`.43`). Er verliert vorlaeufig, weil auch Figur, Knoten und Auslass vorkommen
und keine sichtbare Fluessigkeitsart die Familie unabhaengig besitzt.

## Vorhersagen auf den drei festen Seiten

1. Eine erneute, weiterhin identitaetsblinde Blockannotation sollte `V-Q` im
   allgemeinen/neutralen Bereich und `V-L` im Koerper-/Endstellenbereich
   ueberzufaellig erhalten. Fallen diese Konzentrationen bei kleinen
   Blockgrenzenaenderungen sofort zusammen, gewinnt der Kadenzrivale.
2. Das Entfernen aller vier `VISUALLY_UNOWNED`-Zeilen darf die
   `V-QE`-Becken/Leitungs- und `V-Q`-GENERAL-Muster nicht erzeugen; beide stehen
   schon ohne diese Zeilen. `V-L` muss trotzdem an Koerper/Ende konzentriert
   bleiben.
3. f82r.27 F3 und F6 muessen bei jeder ehrlichen Blockkarte dieselbe
   grobe Becken-/Konfigurationsrolle behalten. Eine Theorie, die ihnen erst
   nach dem Reveal zwei verschiedene sichtbare Stationen gibt, ist
   nachtraegliche Eigentuemerschaft.
4. Innerhalb f83r sollte ein nur nach Zeile/Feldordinal arbeitendes
   Kadenzmodell mindestens so gut wie die sieben visuellen Rollen vorhersagen,
   falls die Bedeutungslesung falsch ist. Die Arbeitstheorie erwartet dagegen
   verbleibenden Rollenwert nach einem innerhalb-Seite-Vergleich.
5. Rendererwechsel duerfen `shedy/cheedy/tedy` sichtbar variieren, ohne die
   exakte `V-S`-Kartenklasse oder ihre Halt-/Ruhefunktion zu aendern.
6. Eine spaetere Werkstattkopie derselben drei Seiten sollte eher
   Verwechslungen zwischen `V-Q`/`V-QE` und Commit-Fehler zeigen als eine
   systematische Umordnung der vier Werte zu vier festen Spalten.

## Schluss

V15 liefert keine Bildlegende. Es liefert eine nuetzlichere Werkstattlehre:
Das Bild besitzt den Gegenstand, der Stencil besitzt die Frage, die exakte
Karte waehlt einen abstrakten Betriebs- oder Anwendungswert, und der Commit
bestaetigt ihn. Die beste konkrete Viererlesung ist vorlaeufig
`STANDARD / DURCHLAUF / LOKAL / HALTEN`. Sie bleibt stehen, bis eine
innerhalb-Seite-Kontrolle sie zerlegt oder ein einfacheres Deck alle 38
Vorkommen besser erklaert.
