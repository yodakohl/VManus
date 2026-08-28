# GDT590 — vier Badgabeln werden Körper-first, aber nicht durch das Bild

## Ergebnis

Die beste einheitliche Arbeitsregel liest alle vier verbliebenen
Y+AIIN-Badgabeln zuerst als `Körper bei der angegebenen Badfüllung`.
`Stationsansatz` bleibt an jeder Stelle als sichtbare Gegenlesung erhalten.
Das ist eine Konsolidierung des bestehenden Gesamtmodells, keine unabhängige
4/4-Entzifferungsbestätigung.

| Host | Stelle / Form | neue erste Klausel | Stärke | Bild allein |
|---|---|---|---|---|
| E2404 | f77r.10 `shey` | Körper im Bad, Füllung, Grad I | mittel–hoch | eher Station |
| E2637 | f77r.39 `cheey` | Körper im Bad, Füllung, Grad II | hoch | leicht Körper |
| E2652 | f77r.41 `sh … qolchey` | Körper im Bad, Füllung | explorativ | knapp Station |
| E3182 | f82r.1 `cheey` | Körper im Bad, Füllung, Grad II | sehr hoch | leicht Station |

## Warum die gemeinsame Regel besser ist

Im vollständigen Bestand gibt es 105 `SH_BIO_BATHE`-Hosts, davon 92 mit Y.
Nach der Entscheidung zerfallen diese 92 ohne Rest in:

- 48 schon vorher blockerfreie Körperhosts;
- vier blockerfreie Körper+Füllung-Hosts aus GDT590;
- 40 Stationshosts, sämtlich mit Relations-, Form- oder Adressblocker.

Damit sind 52/92 Körper und 40/92 Station, ohne eine neue Ausnahme nur wegen
der zusätzlich geschriebenen Füllung zu erfinden. Die elf bekannten
`BIOLOGICAL_BATH_FILL`-Packets passen dazu: fünf enthalten nur Füllung, vier
Körper plus Füllung und zwei geblockte Station plus Füllung.

`shey` besitzt nun 19 alte saubere Körperfälle plus E2404; seine zwei
Stationsfälle sind geblockt. `cheey` besitzt elf alte saubere Körperfälle plus
E2637 und E3182; vier Stationsfälle sind geblockt. E2652 hat als einziges Ziel
ein bloßes SH: Der Aktionsanker steht an Wort 2, der wirkliche Y-Träger
`qolchey` erst an Wort 3. Deshalb bleibt dieser Fall bewusst schwächer.

## Die vollständigen Sätze halten

E3182 ist der stärkste Fall. Direkt vor dem Ziel wird eine Becken- oder
Körpereinheit auf Grad II vorbereitet; direkt danach folgt bereits ein
Körperbad auf Grad I. Körper-first ergibt eine lesbare zweistufige Badfolge.

E2637 hat im selben Satz einen besonders nützlichen Kontrast: blockerfreies
`cheey` kann Körper sein, während das spätere L-geblockte `lsheey` Station
bleibt. Bei E2404 ist die vorausgehende Stationsvorbereitung mit einem Wechsel
zum Badeobjekt vereinbar. E2652 erlaubt denselben Wechsel erst über den
Gouverneur, hat aber kein exaktes bloßes-SH-Körperminimalpaar.

Die vier vollständigen Arbeitspassagen stehen in
`artifacts/GDT590_FOUR_BATH_READER.md`.

## Unabhängige Bildlesung und Dissens

Der Bildpass bestätigt gerade keine einfache 4/4-Körpergeschichte. Alle vier
Ziele sind Prosa, keine exakten Figuren- oder Objektlabels, und keine Linie
weist dem einzelnen Wort einen visuellen Besitzer zu.

- E2404 liegt unter dem dominanten oberen Rohr- und Auslasssystem.
- E2637 steht unmittelbar neben einer Frau und einem dunkelblauen Rundgefäß.
- Bei E2652 liegt der tatsächliche Y-Träger näher am großen Auslass-/Beckenkopf.
- Auf f82r.1 liegt E3182 nach dem Layoutbruch näher am Zentralapparat, das
  folgende `shey` dagegen näher bei Hand, Frau und blauem Becken.

Bildlich neigt daher nur E2637 leicht zu Körper; die anderen drei eher zu
Station oder Apparat. Weil diese Evidenz bloße Nähe und keine Wortbindung ist,
überstimmt die sauberere Host- und Satzkomposition sie im Gesamtmodell. Ein
`Patient` wird nicht eingeführt.

## Umfang der Änderung

Exakt vier von 1.243 Carrier-Slots ändern ihr Arbeitslemma, vier AIIN-Slots
bleiben `Badfüllung`, und exakt vier von 793 Aussagen erhalten eine neue erste
Klausel. Die übrigen 1.239 Slots, 789 Aussagen und sämtliche alten
Wiederholungsspuren bleiben erhalten. Der neue Biological-Y-Bestand lautet
334 Stationsansatz, 65 Körper und sieben Strom.

Validierung: 67/67 Prüfungen grün, einschließlich byte-identischem Neubau der
neun erzeugten Artefakte.

## Was daraus nicht folgt

`Y=Körper` gilt hier nur am vollständig bestimmten Badehost. GDT590 bestätigt
kein Voynich-Wort oder -Stamm, keinen Klartext, keine Sprache, keinen Patienten,
keine Anatomie, Substanz, Krankheit, Heilung, Verfahrensidentität, historische
Quelle oder neue Seite. `Stationsansatz` bleibt bei allen vier als Gegenlesung
gespeichert; E2652 ist der nächste sinnvolle Belastungsfall.
