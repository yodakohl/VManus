# GDT686 — `dain/daiin` sind Wertstufen; der Kopf entscheidet Grad oder Menge

Status: `PASS_955_VALUE_HEAD_CENSUS__REJECT_UNIVERSAL_AXIS__V59_FOUR_GRADES_SEVEN_AMOUNTS`

## Ergebnis

Die alte Karte `Grad-/Maßwert` war keine Übersetzung, sondern zwei
unentschiedene Möglichkeiten in einem Feld. V59 trennt jetzt Form und Achse:

```text
dain     = d + Wertstufe II
daiin    = d + Wertstufe III
qodaiin  = qod + Wertstufe III
```

Danach entscheidet der sichtbare Satzkopf:

```text
Qualitätskopf + d-Wert   -> Qualität im Grad II/III
Stoff-/Teilkopf + d-Wert -> zwei/drei lokale Portionen oder Maße
kein typisierter Kopf    -> Wertstufe bleibt stabil, Sachachse lokal offen
```

Für den globalen Renderer gibt es deshalb kein universelles `Grad III` und
kein universelles `drei Portionen`. Für die elf Stellen unseres aktuellen
Readers wählt V59 dagegen bewusst je einen konkreten lokalen Default: vier
Grade und sieben Mengen.

## Vollständiger Bestand

| Form | Parse | Positionen | Seiten | Loci | dreifach reader-exakt |
|---|---|---:|---:|---:|---:|
| `dain` | `d+a+II` | 193 | 90 | 182 | 149 |
| `daiin` | `d+a+III` | 721 | 169 | 638 | 602 |
| `qodaiin` | `qod+a+III` | 41 | 25 | 40 | 34 |
| gesamt | — | 955 | 174 | 810 | 785 |

Die ganze nackte d-Reihe lautet:

```text
dan 17 | dain 193 | daiin 721 | daiiin 17
 I         II          III          IV
```

Sie besitzt 27 identische Nachbarrahmen mit mehreren Stufen und 49 Zeilen, in
denen mehrere d-Werte zusammen vorkommen. Besonders klar ist f38v.6:

```text
daiin daiiin dain dain
 III    IV    II   II
```

Das widerlegt alte Lesungen wie „und“, „nimm“ oder „führe aus“. Es beweist
aber allein noch nicht, ob die jeweilige Reihe Grade, Mengen oder Klassen
nummeriert.

## Wo die Achse tatsächlich sichtbar ist

Nach exakter Überlappungsbereinigung zerfallen die 914 nackten d-Ziele so:

| Kontext | Positionen | Arbeitsachse |
|---|---:|---|
| kernhaltiger OL-Qualitätskopf | 75 | Grad |
| sichtbarer OR-/Teil-/Materialkopf | 53 | lokale Menge/Portion |
| nackter OL-Träger | 11 | Achse offen |
| äußerer Kopf nicht unmittelbar typisiert | 775 | Achse lokal bestimmen |

Die kleinsten Discriminatoren sind bereits konkrete Klauseln:

```text
chol daiin cthy
Blattgut: trocken, Grad III.

chor daiin cthy
Pflanzenteil: drei lokale Portionen/Maße; danach Blattgut.

chor qotol daiin
Pflanzenteil: kalt, Grad III.
```

Der Qualitätskopf unmittelbar vor `daiin` schlägt also den weiter außen
stehenden Teilkopf. Umgekehrt darf ein sichtbarer Teil- oder Fraktionskopf
eine Mengenlesung tragen, wenn kein konkurrierender Qualitätskopf dazwischen
steht.

## `qodaiin` ist nicht einfach ein längeres `daiin`

Die qod-Reihe ist kleiner und unvollständig:

```text
qodain 10 | qodaiin 41 | qodaiiin 1 | qodan 0
```

Sie besitzt keinen kontrollierten Mehrwert-Nachbarrahmen. Zwei
Alternativleser zeigen sogar verschiedene innere Grenzen desselben Spans:

```text
f86v3.25  qodaiin  <->  qod | aiin
f95r2.1   qodaiin  <->  qo  | daiin
```

Darum bleibt die globale Karte `qod-Wertzelle III; Kopf offen`. Das freie
`qo`-Aktionsgloss wird nicht in das gebundene Wort hineinkopiert. Am einzelnen
Locus darf ein sichtbarer Kopf dennoch einen praktischen Default auswählen.

## Die elf konkreten V59-Entscheidungen

| Stelle | V59-Default | Bindung |
|---|---|---|
| f10r.2#9 `daiin` | Qualitätsgrad III des erhitzten Ansatzes | links `oky` |
| f112v.10#1 `dain` | Feuchtgrad II | rechts `sheey` |
| f116r.12#5 `dain` | zwei Portionen des erhitzten, nachgetrockneten Drogenmaterials | links |
| f116r.12#11 `dain` | zwei Portionen der Rohdroge I im kalten Anfangsansatz | links |
| f56r.6#5 `daiin` | Qualitätsgrad III des heißen Endzustands | links `keey` |
| f76v.10#9 `daiin` | drei Portionen des eingeweichten Arzneikompositums | links |
| f83v.12#1 `daiin` | drei Portionen feuchten Arzneikompositums | rechts |
| f86v3.13#5 `qodaiin` | drei Portionen der ersten erhitzten Ansatzfraktion | rechts `olkar` |
| f86v6.5#5 `daiin` | drei Portionen der ersten erhitzten Ansatzfraktion | links `olkar` |
| f88r.19#3 `daiin` | Qualitätsgrad III des heißen Trockenabsuds | links `chokol` |
| f8r.15#7 `daiin` | drei Materialmaße | rechts `dol` |

Diese Defaults sind absichtlich mutiger als die globale Karte. Zehn tragen
AMBER, einer GREEN. Jeder behält seinen stärksten lokalen Rivalen im
Positionsartefakt; im praktischen Text erscheint dennoch nur eine Lesung.

## Was die Übersetzung jetzt tatsächlich sagt

f10r.2 verliert eine erfundene Entnahmehandlung:

> Eine Portion Blatt- oder Krautansatz bis zur Mittelstufe trocknen und
> abschließen. Erste und zweite Trockenfraktion kalt-trocken ansetzen und mit
> einer Ansatzcharge sowie nachgekühltem Trockenstoff verbinden. Den Ansatz
> leicht erhitzen: Qualitätsgrad III; anschließend bis zur Mittelstufe kühlen
> und abschließen.

f86v3.13 wird zu einer sichtbaren Rezeptliste statt eines versteckten
Layerwechsels:

> Vollständig eingeweichter Ansatz; eine Portion vollständig eingeweichte
> Droge. Abkühlen, bis zur Mittelstufe trocknen, ansetzen und fertigstellen.
> Heizstufe II; drei Portionen der ersten erhitzten Ansatzfraktion; drei Dosen
> Trockendroge. Hierzu bis zur Mittelstufe trocknen und abschließen; einen
> gleichen Teil erhitzen und abschließen; Trockengut auf Heizstufe II.

f8r.15 sagt nun schlicht:

> Arzneikompositumstoff: trocken, bis zur Mittelstufe; eine Charge unter Wärme
> getrockneter Droge leicht nachtrocknen; trocken auf Anfangsstufe. Drei
> Materialmaße; die vierte abgemessene, leicht getrocknete Fraktion mit
> Arzneikompositum auf Anfangsstufe ansetzen.

`daiin` erzeugt dabei weder „abnehmen“ noch „verbinden“. Ein Verb bleibt nur
erhalten, wenn eine andere bereits lizenzierte Karte es trägt.

## Informationsgewinn

| Schuldmaß | V58 | V59 | Änderung |
|---|---:|---:|---:|
| kuratierte Kartenpositionen | 131 | 120 | -11 |
| mechanische Schuldunion | 172 | 163 | -9 |
| mechanische Mitgliedschaften | 186 | 177 | -9 |
| Slash-/Mehrfachglossen | 36 | 27 | -9 |
| breite Spezifität offen | 335 | 324 | -11 |
| Vier-Schichten-Union | 381 | 370 | -11 |
| ohne aktuelles Schuld-/Konfidenzsignal | 98 | 109 | +11 |

Alle 86 Aktionslizenzen bleiben unverändert.

## Nächster Zug

Als Nächstes folgt die Aktions-/Strukturachse `dchey/y/dy`. Dort liegen noch
größere praktische Fehler: nominale Ergebnisse werden zu Befehlen, und
Strukturabschlüsse erzeugen Verben wie „schließen“, obwohl kein Aktionskopf
sie lizenziert. Der nächste Reader soll jede aktuelle Stelle als echte Aktion,
Ergebniszustand oder bloßen Feldabschluss dispatchen und danach die praktische
Prosa neu setzen.

## Claim ceiling

GDT686 fixiert die geordneten Wertstufen und liefert elf konkrete,
ersetzbare lokale Arbeitslesungen. Es identifiziert keine historische
Maßeinheit, keinen historischen Qualitätsnamen, keine Zutat, Flüssigkeit,
Pflanze, Krankheit, Person, Heilung, Sprache, Lautung oder Codebuchidentität.
Es öffnet keine neue Seite; f84 und f84r bleiben ausgeschlossen.
