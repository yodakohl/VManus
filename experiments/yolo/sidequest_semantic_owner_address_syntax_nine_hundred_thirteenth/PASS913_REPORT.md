# Pass 913 — Besitzer- und Adresssyntax der Bildetiketten

## Ergebnis

Die 198 Etikettengruppen in 153 Bildloci sind jetzt an konkrete räumliche Rollen
gebunden: Himmelssektor, Sternstation, Außen-/Innenfigur, Beckenstation, Baugruppe
oder Zutatenplatz. Der sichtbare Name/Klassenwert bleibt zuerst; die wiederkehrenden
Teile bilden darüber eine kleine Adresssyntax.

Der wichtigste Fortschritt ist die Doppelverwendung von `OT–AL`: Auf f70 adressiert
sie nacheinander Sternfiguren, auf f88 Zutatenplätze. Das passt besser zu „nächster
zugewiesener Platz“ als zu einem Pflanzenteil oder einem Badeverb. Ebenso werden
`AR`, `AM`, `Y` und `DY` als Bezug, Innenfeld, aktueller Besitzer und gebundener Eintrag
konkreter, ohne die Bildnamen zu erfinden.

## Acht lesbare Slots

1. **OWNER** — `VISIBLE_IMAGE_OR_LOCAL_NAMESPACE`: konkreter Gegenstand, Figur, Sektor oder Station.
2. **ORDER** — `OT|OL|DA`: nächster Platz | gleiche Reihe | markierter Unterplatz.
3. **CLASS_OR_ACTION** — `O|OK|CH|K|T|S|OR`: Gang/Klasse aufrufen | aktivieren | ablesen | zuordnen | markieren | Klasse | lokaler Eintrag.
4. **ADDRESS** — `AL|AR|AM_ADDR|A_ADDR|D_ADDR|S_ADDR`: Ziel | Bezug/Quelle | Innen/Gegen | lokale | Teil | S-Adresse.
5. **INDEX_OR_AMOUNT** — `AIIN|AIN|IIN`: Sollzahl/Maß | Einheit | Stufe/Index.
6. **GRADE** — `E|EE|EEE`: kurz/erste | länger/zweite | voll/höchste Stufe.
7. **TOPOLOGY** — `L|CKH|AIR|CPH`: Verbindung | Durchlass | Lauf | Gegen-/Empfangsplatz.
8. **REFERENT_OR_BOUNDARY** — `Y|DY`: aktueller Besitzer | gebundener/abgeschlossener Eintrag.

## Rollenbilanz

- `STAR_OR_RAY_STATION`: 37 Gruppen
- `ZODIAC_OUTER_FIGURE`: 37 Gruppen
- `CELESTIAL_SECTOR`: 28 Gruppen
- `ZODIAC_INNER_FIGURE`: 22 Gruppen
- `OUTER_STAR_POSITION`: 17 Gruppen
- `BATH_OR_APPARATUS_STATION_LABEL`: 13 Gruppen
- `LOWER_POOL_STATION_LABEL`: 10 Gruppen
- `PHASE_OR_CONDITION_SLOT`: 10 Gruppen
- `UPPER_INGREDIENT_SLOT`: 6 Gruppen
- `MIDDLE_INGREDIENT_SLOT`: 6 Gruppen
- `CHANNEL_OR_FIGURE_ASSEMBLY_LABEL`: 4 Gruppen
- `LOWER_INGREDIENT_SLOT`: 4 Gruppen
- `SHARED_POOL_LABEL`: 2 Gruppen
- `CENTRE_OR_FACE_SLOT`: 1 Gruppen
- `ZODIAC_CENTRE`: 1 Gruppen

## Konkrete Lesebeispiele

- f70 `OT–AL–Y`: nächster Zielplatz der aktuell bezeichneten Sternfigur.
- f88 `OT–AL–DY`: nächster gebundener Zutatenplatz; sichtbarer Wert Wurzelbündel G.
- f75 `S–AL`: klassenmarkierte Zielstelle am unteren Beckenlabel.
- f67 `OK–AR`: den bezeichneten Bezugsplatz im Rad aktivieren.
- f68 `CPH–O–CTH–Y`: Gegenstelle des lokalen Ringgangs, mit Status des aktuellen Sternplatzes.

## Was bewusst lokal bleibt

Die Etiketten nennen weiterhin keine identifizierte Pflanze, Zutat, Sternfigur oder
historische Himmelsstation. Pass 913 liefert eine brauchbare Klassen-/Adresslesung
über dem sichtbaren Besitzer; der eigentliche Eigenname bleibt Werkstattwissen.

## Nächster Hebel

Pass 914 soll diese acht Slots in das vollständige Handbuch zurückschreiben und die
f70-/f88-Etiketten als fortlaufende Listen lesen. Danach wird geprüft, welche der
vier Registeroperationen O/OK/CH/K im Namensregister wirklich Klassifikatoren sind.
