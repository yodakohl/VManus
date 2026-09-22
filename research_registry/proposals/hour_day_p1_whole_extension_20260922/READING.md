# Bedingter Gesamtentwurf für f82r.1–9

Dies ist eine vollständige, aber unbestätigte Arbeitslektüre der beiden exakt
gebundenen 72er-Einheiten. Alle 60 Werte aus GDT1015 bleiben unverändert. Die
ZL3b-Fassung verwendet 42 neue ganze Werte. Die fünf IT2a-Varianten `qocseedy`,
`sor`, `lchor`, `sshol` und `shecthy` bleiben offen; sie werden weder als ZL-
Formen gelesen noch durch eine bequeme Aliasregel ersetzt. Die zwei `daiin`
in C01 bleiben zwei geschriebene Rollen: Rahmenzahl der ganzen Zeitspanne und
Rückkehrmaß innerhalb derselben Zählung. Die vier `qokaiin`-Vorkommen bleiben
eigene RULER-Ereignisse: Ende C03, Anfang C04, sowie die beiden Projektionen in
C09.

`GROUP_SOURCE_DETAILS.json` erhält alle gespeicherten Separatoren. Die fünf
Bildunterbrechungen in ZL3b .1–.5 und die entsprechenden IT2a-Grenzen sind
Quellgrenzen, keine Glyphenunsicherheit; in ZL3b .8 bleibt `lcho|r` ein
unsicherer kleiner Abstand. Keine dieser Unterbrechungen beweist syntaktische
Kontinuität oder eine Satzgrenze. Die neun Abschnitte unten sind daher eine
offengelegte Arbeitsaufteilung und keine aus der Zeichnung abgeleitete
Interpunktion.

Der Entwurf lautet: Ein vorheriger Zeitabschnitt eröffnet einen Tagesrahmen.
Dieser Rahmen zählt vierundzwanzig Einheiten und führt über denselben
Folgeschritt zurück. Eine vollständige Tagesperiode enthält Nacht und helle
Zeit. Von einem gemeinsam gesetzten Anfangspunkt wird eine Stunde als
abgeleitete Stufe in einem Herrscherkreis bestimmt. Die Folge hält die
Herrscherzuordnung über den Nachtübergang und die gemessene Dauer zusammen.
Eine spätere Zählung setzt wieder an der gemeinsamen Phase an, wählt das erste
passende Glied und erreicht den Endpunkt der hellen Zeit. Die abschließende
Herrscherprojektion bleibt an diesen Anfang und dieselbe Folge gebunden; sie
ist keine neue freie Quelle. Diese Klammer verbindet die Aussagen in P1C02 und
P1C09 durch B01_PHASE_ALPHA. Sie ist eine zusätzliche Arbeitsbindung, kein
zweites 24-mod-7-Ergebnis.

## Jede geschriebene Zeile

Die folgenden Rohformen sind die vollständige sichtbare ZL3b-/IT2a-Abdeckung.
Ihre Werte und die neun Satzabschnitte stehen maschinenlesbar in
`SOURCE.json`, `LEXICON.json` und `CLAUSES.json`; Unsicherheitszeichen und
Lesergrenzen werden unverändert aus `SOURCE.json` übernommen.

| Abschnitt | ZL3b exakt | IT2a exakt | Bedingte deutsche Aussage |
|---|---|---|---|
| C01 / .1 | `qosheedy qokeol daiin shckhy okeeor cheey daiin shey` | `qocseedy qokeol daiin shckhy okeeor cheey daiin shey` | Ein vorheriger Zeitabschnitt eröffnet die Spanne; 24 zählt den Rahmen und das Rückkehrmaß, der Folgeschritt hält die Reihe zusammen. `qocseedy` bleibt offen. |
| C02 / .2 | `dchedy qolchedy qokain dy qokeedy qokal lcheckhy lched` | gleich | Der Tagesabschnitt umfasst die Nachtspanne; der gemeinsame Anfangspunkt führt zu einer abgeleiteten Stunde und endet an der Nachtgrenze. |
| C03 / .3 | `qokeey lcheckhedy qokaly solkaiin chckhy qokaiin` | gleich | Der erste Nachtfortgang wird als abgeleitete Folge im Herrscherkreis markiert; der Phasenwechsel führt zur Herrscherzuordnung. |
| C04 / .4 | `qokaiin octheol chkeey ldy oteey qokal sheckhy qoky` | gleich | Die Herrscherfolge ordnet einen früheren Punkt und führt ihn als abgeleitete Stufe zum Zielpunkt. |
| C05 / .5 | `sol lkchedy qokeedy qokal cthol chedy qoteedy qokal` | gleich | Im Kreis folgt auf den Nachtbezug eine Stunde; die Schwelle, die helle Zeit und die gemessene Dauer führen zur nächsten abgeleiteten Phase. |
| C06 / .6 | `sar shedy qol shedaiin sheckhy okal sheky qotaiin chedol` | `sor shedy qol shedaiin sheckhy okal sheky qotaiin chedol` | Ein Abschnitt verbindet eingesetzte Einheiten; aus der Herrscherstufe folgt ein Nachfolger, dessen Anzahl den Abschluss bestimmt. `sor` bleibt offen. |
| C07 / .7 | `dshedy sotaiin qokar shedy solshedy qokeey qoky ls cheey` | gleich | Die Startzählung setzt am Ursprung ein, wählt das erste Zielglied und folgt innerhalb des Kreises dem gebundenen nächsten Glied. |
| C08 / .8 | `qekeey sheedy qokedy lcho r cheey qokey qotal chedy qoteor` | `qokeey sheedy qokedy lchor cheey qokey qotal chedy qoteor` | Ein zweiter Anfang setzt ein angewandtes Glied in den ganzen Tagesrahmen; Nacht, Nachfolger, helle Zeit und Endpunkt bleiben verbunden. `lcho` und `lchor` sind getrennte Formen. |
| C09 / .9 | `ssholshecthy qokaiin chkedy rchey dairchey qokaiin` | `sshol shecthy qokaiin chkedy rchey dairchey qokaiin` | Nach der Ordnungsgrenze wird dieselbe abgeleitete Phase aus der Folge bestimmt und zweimal als Herrscherprojektion sichtbar. `ssholshecthy` und `sshol`/`shecthy` bleiben getrennte Zweige. |

## Bindungen, Kosten und Rivale

`B01_PHASE_ALPHA` binds the initial point in C02 to both C09 ruler projections.
`B02_DAY_FRAME` gives the two `daiin` occurrences their separate units while
keeping the DAY boundary stable. `B03_RULER_SUCCESSION` explicitly separates
the H ruler cycle from any DAY succession. `B04_DERIVED_PHASE` carries the
derived phase across C03/C04/C05/C09. `B05_NIGHT_BOUNDARY` keeps night inside
one complete day. `B06_READER_BRANCH` preserves the ZL and IT accounts as
separate exact branches. The inventory is six bindings, four reusable
productions, 42 new ZL whole values, and no aliases, packing, per-occurrence
senses, or new numeral assignment.

The principal rival gives each `DERIVED` occurrence a fresh phase, so the
repeated ruler statements do not share alpha. A second rival identifies the
DAY successor with H without declaring that type change. A third treats P1 as
retrospective explanation rather than the next temporal event. These rivals
remain compatible with the exposed strings. The present draft does not select
among them and claims no complete coherence or historical meaning.
