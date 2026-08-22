# Technische Zustands- und Endpunktmatrix

Status: kreative Werkstattrekonstruktion für die festen zehn Sidequest-Seiten,
keine behauptete Entzifferung. Ausgangspunkt ist die aktuelle Mengen-/
Zubereitungsedition samt ihrer Y/CHY-Korrektur. Die Kartenidentität bleibt
maßgeblich; sichtbare Ähnlichkeit allein darf keine Zerlegung erzwingen.

## Ausgewählte technische Lesart

Die Zustandsnotation besitzt am ehesten **zwei verschiedene Gradachsen** und
eine davon getrennte Endpunktachse:

```text
MENGEN-/EINSTELLUNGSACHSE
AIN     abgeteilte Portion
AIIN    vorgeschriebenes Maß
IIN     benannte Arbeitsstufe oder Einstellung

DYNAMISCHE PROZESSACHSE
Ø       Grundhandlung ohne ausgesprochene Kontaktstufe
E       kurz, direkt oder gewöhnlich
EE      anhaltend oder verlängert
EEE     vollständig oder durchgehend

REFERENT UND ENDPUNKT
Y/CHY   der aktuell gemeinte Arbeitsposten; dies/es; nicht geschlossen
DY      in einer gelernten exakten Karte: örtlichen Arbeitsschritt schließen
```

Die beste gemeinsame Bauform lautet deshalb:

```text
CORE + GRADE + Y
    = den CORE-Zustand am laufenden Posten halten oder fortsetzen

CORE + GRADE + DY
    = CORE bis zur angegebenen Stufe ausführen und den örtlichen Schritt schließen
```

Diese Regel ist **begrenzt produktiv**, nicht universell. Sie ist im OK-Raster
am klarsten, wird durch OT und die lokale SOLK-Familie gestützt, ist bei SHED
nur auf der Schlussseite erhalten und darf CHK- oder CTH-Ganzkarten nicht
blind überschreiben.

## Das zentrale Kontakt- und Endpunktraster

| Kern und Grad | laufender Posten / offene Fortsetzung | terminaler Schritt |
|---|---|---|
| `OK + Ø` | `OKY/OKCHY`, 13 Ereignisse: Posten in Arbeit nehmen | kein genaues gradloses DY-Gegenstück angesetzt |
| `OK + E` | `OKEY`, 2: kurz anlegen/benetzen | `QOKEDY`, 8: kurz spülen/benetzen; Schluss |
| `OK + EE` | `OKEEY`, 7: anhaltend in Kontakt halten | `QOKEEDY`, 10: eintauchen/einweichen; Schluss |
| `OK + EEE` | nicht belegt; vorhersagbar als vollständiger laufender Kontakt | `QOKEEEDY`, 1: vollständig durchtränken; Schluss |
| `OT + E` | nicht belegt; danach kurz am Posten handeln | `OTEDY`, 2: danach kurz einwirken; Schluss |
| `OT + EE` | `OTEEY`, 2: danach anhaltend einwirken | `QOTEEDY`, 2: danach anhaltend einwirken; Schluss |
| `SH/SHED + E` | keine sichere offene Gegenkarte | `SHEDY`-Familie, 12: kurz/gewöhnlich ruhen; Schluss |
| `SH/SHED + EE` | keine sichere offene Gegenkarte | `SHEEDY`, 1: länger ruhen/nachwirken; Schluss |
| `SOLK + E` | `SOLKEY`, 1: Sammelstelle kurz aktiv | nicht belegt |
| `SOLK + EE` | `SOLKEEY`, 1: Sammelstelle länger offen | `OLKEEDY/SOLKEEDY`, 3: absetzen lassen; Schluss |

Damit erhält E/EE/EEE eine kurze gemeinsame Bedeutung: **Ausdehnung eines
sichtbaren Kontakts, Haltens oder Einwirkens**. Der Kern entscheidet, ob das in
der konkreten Lesung Benetzen, Einweichen, Ruhen, Wärmen oder Stationsbetrieb
heißt. E ist daher nicht global „Wasser“, EE nicht global „Wärme“ und EEE kein
selbständiger Stoff.

Die exakten Identitäten und Ereignisse des stärksten OK-Rasters sind:

| Karte | exakte Tuple-ID | Ereignisse |
|---|---|---|
| `OKY` | `276a7c2d74d1143446f4` | `E008,E081,E085,E140,E188,E195,E247,E251,E298,E323` |
| `OKCHY` | `9ad66e67803a12e745de` | `E011,E091,E095` |
| `OKEY` | `08bd5ca0c2ad137a056d` | `E142,E220` |
| `OKEEY` | `0275fbf14e07935b0a45` | `E153,E175,E194,E205,E293,E317,E322` |
| `OKEDY` | `7db18b2f0fb7ed0fcfd3` | `E101,E137,E138,E259,E294,E297,E318,E335` |
| `OKEEDY` | `7d25241b0e56c836372a` | `E171,E201,E213,E224,E227,E245,E265,E302,E315,E329` |
| `OKEEEDY` | `d25110e0d8488927278f` | `E209` |

`QOKEEDAL` (`93f69c38fdedee1598e9`, E117) zeigt zusätzlich, dass derselbe
anhaltende Grad statt eines Endpunkts eine Zielstelle erhalten kann:
„an der Zielstelle anhaltend in Kontakt halten“. `OKEEOL`
(`daf32e6db9e04413ce7f`, E190) bindet ihn an die Fortsetzung mit dem vorigen
Posten. GRADE, Referent, Ziel und Abschluss sind also getrennte technische
Aufgaben.

## IIN ist eine Stufe, nicht eine Portion

Die drei IIN-Karten bilden keine Kontaktleiter, sondern benennen die jeweils
eingestellte Stufe:

| Karte | Tuple-ID | Ereignisse | konkrete Lesung |
|---|---|---|---|
| `OIIIN/SOIIIN` | `2c82523794dcb7d2b343` | `E161,E309` | vorgeschriebener Grad |
| `KAIIIN` | `409de02322e7b2ca0c62` | `E036` | weiche Konsistenz |
| `DAIIIN` | `fcc1deda9e24ec268eb0` | `E371` | zweite Öffnungsstufe |

Die Hülle liefert die Art der Stufe, IIN den gemeinsamen Beitrag
„Grad/Einstellung“. Das erklärt die knappen Gegenpaare:

```text
KAIN      Portion                 KAIIIN    weiche Zustandsstufe
DAIIN     vorgeschriebenes Maß    DAIIIN    zweite Öffnungsstufe
AIN       abgeteiltes Teil        IIN       erreichte/geforderte Einstellung
```

IIN darf darum nicht nachträglich in AIIN hineingelesen werden. Die sechs
Mengen-Gegenkarten stehen vollständig in der Tabelle und behalten ihre
konkreten Werte Portion beziehungsweise Maß.

## CTH, SHED, CHK und SOLK

### CTH — bereit

`CTHY` (`e0b630cb1b5df5e7105b`, sieben Ereignisse) heißt kurz „bereit“.
`QCTHEY/SHCTHEY` (`6b89d6dd70635bc60fe0`, E204/E258) erweitert das zu
„den laufenden Posten bereit halten“. Das ist ein brauchbares offenes
Zustandspaar:

```text
CTHY          bereit
CTH + E + Y   den aktuellen Posten in Bereitschaft halten
```

Aber `CTHAIIN` bleibt die gelernte Karte „Kraut zerstoßen“ und `SHECTHY` die
gelernte Karte „warmes Wasser“. Sie verhindern eine globale Regel
`jedes sichtbare CTH = bereit`.

### SHED — ruhen oder absetzen

Die stärkste exakte Paarung ist:

```text
CHEEDY/SHEDY/TEDY    kurz oder gewöhnlich ruhen lassen; Schluss   12
SHEEDY               länger ruhen oder nachwirken lassen; Schluss  1
SHEDAL                Ruhe- oder Absetzstelle                       2
QOKSHEDY              Ansatz zur Ruhe/Absetzung bringen; Schluss     1
```

Hier ist der Kern der Ruhe-/Absetzvorgang, E/EE ist der Grad und DY der
Abschluss. Eine offene `SH+E+Y`-Karte ist auf den festen Seiten nicht sicher
belegt; sie bleibt nur eine mögliche künftige Komposition.

### CHK — Wärme, aber KY bleibt ganz

`CHEKY` (`d904bf7b044dd3922781`, drei Ereignisse) und `CHEEKY`
(`2c1a5fd92b9e3c762242`, zwei) ergeben „kurz/mild erwärmen“ gegenüber „länger
warm halten“. Alle fünf stehen intern oder offen. Das Gradpaar ist gut, aber
`KY` wird nicht als selbständiges Y zerlegt.

Diese Vorsicht ist produktiv: Die exakte Karte `CHKEEY`
(`f0db6d30cd34f4cb2a4d`) bedeutet weiterhin „breites Gefäß“, und `CHKEEDY`
(`a84fbe3ad380df345b97`) bleibt „vollständig benetzen; Ende“. Ein erfundenes
universelles `CHK+EE+Y` würde gerade diese beiden gelernten Karten zerstören.

### SOLK — lokale Sammelstation

Die örtliche f81v–f83r-Familie ist fast ein ideales Zustandsdiagramm:

```text
SOLKEY              Sammelstelle kurz öffnen/aktiv halten
SOLKEEY             Sammelstelle länger offen halten
OLKEEDY/SOLKEEDY    an der Sammelstelle stehen/absetzen; Schluss
```

Hier gehört der sichtbare Zustand dem lokalen Becken-/Stationsbesitzer. Das
ist nicht dasselbe wie eine im Text genannte Substanz. `SOLKAIIN` bleibt die
gelernte Ganzkarte „durch Tuch“ und begrenzt die Übertragung.

## Y, DY, Bildbesitzer, Zeile und Schluss sind vier verschiedene Dinge

1. **Bildbesitzer:** Die Pflanze, das Becken oder die lokale Gefäßstation kommt
   aus Seite und Zeichnung. Sie ist nicht der Zustand und wird nicht von Y
   automatisch benannt.
2. **Laufender Posten:** Y/CHY bedeutet „dies/es, der aktuell gemeinte
   Arbeitsposten“. Die Tabelle enthält 18 solche exakten Kartenidentitäten mit
   66 Ereignissen, einschließlich der neuen Mengenkompositionen.
3. **Physische Zeile:** Fünf Zielereignisse (`E202,E220,E273,E342,E364`) stehen
   unmittelbar vor einem Zeilenwechsel, doch ihre Aussage läuft danach weiter.
   Der Zeilenwechsel ist kein Endpunktzeichen.
4. **Zellschluss:** 37 exakte Zielkarten liefern 89 Schlussereignisse. Alle 89
   stehen am Ende ihrer ausgewählten Aussage. Umgekehrt stehen acht
   nichtterminale Zielereignisse am Aussageende; auch ein Aussageende erzwingt
   also ohne Schlusskarte keinen geschlossenen Arbeitsgang.

Der wichtigste Gegenbeleg gegen blindes Buchstabenschneiden ist die exakte
Y-Karte `b921a237be883a820352`: Sie erscheint unter anderem als sichtbares
`dy`, ist aber „der laufende Posten“, nicht Schluss. Ebenso ist
`CHDY/CHEDY` (`6f7ff8287eddf4da9fdb`, elf Ereignisse) die nichtterminale Karte
„den laufenden Posten umsetzen“. Dagegen ist die getrennte Tuple-ID
`259b2b3b0bf859882e2c` mit `DCHEDY/SCHEDY/TCHEDY` viermal wirklich terminal:
„Arbeitsbewegung abschließen“.

Damit lautet die Schreiberregel nicht „jedes dy beendet“, sondern:

> **Erkenne zuerst die gelernte Karte. Innerhalb einer lizenzierten
> Zustandsfamilie hält Y den Posten laufend; die gelernte DY-Gegenkarte schließt
> die Zelle.**

## Begrenzte Vorhersagen

Wenn auf denselben zehn Seiten eine noch nicht zugeordnete exakte Karte in
einer bereits lizenzierten Hülle auftauchte, wären folgende Defaultlesungen
lehrbar:

| Komposition | kurze Defaultbedeutung |
|---|---|
| `OK+EEE+Y` | laufenden Posten vollständig in Kontakt halten; noch nicht schließen |
| `OT+E+Y` | den laufenden Posten danach kurz anlegen/einwirken lassen; offen |
| `CTH+EE+Y` | den laufenden Posten länger in Bereitschaft halten |
| `SH+EE+Y` | den laufenden Posten länger ruhen lassen; noch nicht schließen |
| `SOLK+E+DY` | kurz an der Sammelstelle halten/absetzen und schließen |
| `SH+EEE+DY` | vollständig absetzen/nachwirken lassen und schließen |

Das sind **Kompositionsvorhersagen**, keine neu gefundenen Karten. Drei
sichtbar verlockende Vorhersagen sind ausdrücklich gesperrt:

- `CHKEEY` darf nicht als freies `CHK+EE+Y` gelesen werden: exakte Ganzkarte
  „breites Gefäß“;
- `CTHAIIN` darf nicht als CTH plus Maß/Grad gelesen werden: „Kraut zerstoßen“;
- `SOLKAIIN` darf nicht als SOLK plus Maß/Grad gelesen werden: „durch Tuch“.

## Vollständiges Inventar

`TECHNICAL_STATE_LATTICE.tsv` enthält:

- 64 attestierte Zielkarten mit 175 eindeutigen Ereignissen;
- darunter alle 37 terminalen Karten mit sämtlichen 89 Schlüssen;
- sechs exakte AIN/AIIN-Gegenkarten mit 44 Ereignissen;
- vier widersprechende Ganzkarten mit je einem konkreten Default;
- insgesamt 74 Zeilen mit vollständigen Tuple-IDs, Oberflächen, Event-IDs,
  Seiten, Records, Aussagen, Kartenpositionen, Zeilenfortsetzungen, Besitzern,
  Zuständen, Referentenstatus, Zellschluss und begrenzter Vorhersage.

Keine Zielkarte bleibt bedeutungsleer. Die drei festen Astro-Seiten enthalten
in der aktuellen 381er Prosaedition keine Zielereignisse und wurden nicht
künstlich aufgefüllt. Keine andere Seite wurde geöffnet; f84 und f84r blieben
vollständig versiegelt. Kein Commit oder Push wurde ausgeführt.
