# GDT592 — Jede Badhandlung hat jetzt ein Arbeitsobjekt

## Ergebnis

Alle 254 `SH_BIO_BATHE`-Handlungen lassen sich nun ohne leere Objektstelle
lesen. Das stärkste Ergebnis ist nicht bloß die Vollständigkeit, sondern die
Korrektur des ersten Modells: Von 24 zunächst angenommenen Episode-Carries
sind 13 in Wahrheit näher liegende, schriftlich sichtbare Objektübergaben.
Übrig bleiben elf kurze Carries, davon neun mit einem typisierten Donor und
zwei Wiederaufnahmen des neutralen Badeguts.

| Objektklasse | Handlungen |
|---|---:|
| Körper | 53 |
| Stationsansatz | 81 |
| Badegut | 107 |
| Bade-/Stationseinheit | 9 |
| Anwendungsportion | 4 |
| gesamt | 254 |

Die Auswahlwege sind 92 geschriebenes Y, sechs geschriebenes OR, zwei
geschriebene AIN, 25 blockerbedingte Stationen, 13 lokale Handoffs, elf
Episode-Carries und 105 kalte Badegut-Defaults. AIIN wählt nie das Objekt; es
bleibt in allen fünf AIIN-only-Fällen der Füllparameter.

## Die 13 besseren lokalen Donoren

Neun Handoffs ändern die alte Carry-Lesung tatsächlich:

- E1673, E3221 und E3665 werden durch ein späteres lokales Y zu
  `Stationsansatz` statt neutralem Badegut;
- E1746 und E3625 übernehmen AIN als `Anwendungsportion`;
- E3067 und E3550 übernehmen OR wortgleich als `Stationseinheit`, nicht als
  den älteren Körper- beziehungsweise Stationsreferenten;
- E3234 und E3304 übernehmen einen unmittelbar sichtbaren Stationsansatz statt
  Körper.

Vier weitere Fälle bestätigen die alte Klasse mit einem näheren Donor:
E2641, E2736, E3034 und E3621 bleiben Station. E3621 liest deshalb besonders
transparent `denselben Stationsansatz ... bei der angegebenen Füllung`:
Stationsansatz und AIIN-Füllung besetzen zwei verschiedene Rollen.

Die zwei entfernt gebundenen Donoren bleiben korrekt zweistufig. Bei E3067
steht der T-Gouverneur an E3065, der entscheidende OR-Slot aber an E3066; bei
E3304 steht der S-Gouverneur an E3299 und sein Y-Slot an E3301. Der Leser gibt
beides getrennt aus, statt Gouverneur und geschriebenes Objekt auf ein Event
zusammenzuziehen.

## Die elf verbleibenden Carries

Die echten Carry-Ziele sind E1579, E1713, E2471, E2481, E2638, E2881, E2914,
E3219, E3379, E3489 und E3590. Sie liegen höchstens zwei laufende Ereignisse
vom letzten Badeobjekt entfernt: sieben sind unmittelbar, vier kurz. Die
früher problematischen langen Fälle E3067, E3304 und E3550 sind durch ihre
näheren schriftlichen Donoren verschwunden.

E2881 ist der klarste Restfall: eine unmittelbar zuvor geschriebene
Badeinheit wird als `dieselbe Badeinheit` wiederaufgenommen. E3219 und E3489
sind bewusst schwächer und heißen `dasselbe zu badende Gut`; bei beiden bleibt
sichtbar, dass nur der neutrale Default wiederholt wird. E2481 bleibt der
inhaltliche Reststreit: die Badeepisode trägt Station, GDT569 dagegen OR/
Stationseinheit.

## Der vollständige Leser

149 Handlungen hatten keinen geschriebenen Carrier und fünf nur AIIN. Damit
werden 154 Klauseln in 132 Aussagen ergänzt; 100 bereits ausgeschriebene
Objektklauseln und 661 nicht betroffene Aussagen bleiben bytegleich. Die neue
Fassung vermeidet das tautologische `Badeobjekt im Bad` und sagt stattdessen
`das zu badende Gut im Bad`. Bei echter Wiederaufnahme steht anaphorisch
`denselben Stationsansatz`, `dieselbe Badeinheit` oder
`dasselbe zu badende Gut`.

Das Endprofil umfasst 177 Badeaussagen in 190 Reader-/Absatzsegmenten auf den
sechs bekannten Seiten. Der vollständige deutsche Arbeitsleser steht in
`artifacts/GDT592_COMPLETE_BATH_OBJECT_READER.md`.

## Was GDT569 zusätzlich öffnet

117 der 254 Aktionsslots besitzen eine ältere GDT569-State-Zeile: 109 tragen
ein altes Argument fort, acht besitzen ein lokales explizites Argument. Diese
Spur wird nicht als identisch mit dem neuen Badeobjekt ausgegeben.

Am produktivsten sind 61 neutrale Badegut-Fälle mit einem spezifischeren alten
Kandidaten:

| alte Wurzel | Fälle | nächste Arbeitsbedeutung |
|---|---:|---|
| Y | 49 | Körper oder Stationsansatz noch entscheiden |
| AIN | 8 | Anwendungsportion versuchen |
| OR | 4 | Bade-/Stationseinheit versuchen |

Die zwölf AIN/OR-Fälle sind damit der direkte nächste Bedeutungsgewinn. Die 49
Y-Fälle brauchen die bereits entwickelte Körper/Station-Umgebung, dürfen aber
nicht wieder pauschal `Stationsposten` heißen. Nur E1719 und E2481 bleiben als
echte Klassengegensätze in einer eigenen Tabelle erhalten.

## E2652 und Grenze

E2652 bleibt unverändert `Halte den Körper im Bad bei der angegebenen
Füllung`; GDT592 patcht dort nichts, und `Stationsansatz` bleibt sichtbar.

Der Pass ist eine möglichst vollständige Werkstattlektüre, keine bestätigte
Entzifferung. Er fügt keine Seite, Wurzel, Segmentierung oder historische
Quelle hinzu. Validierung: 112/112 Prüfungen grün, einschließlich vollständiger
Input-Joins, Slot-Grain bei E3243 und byte-identischem Neubau aller 13
generierten Artefakte.
