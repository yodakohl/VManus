# GDT543 — aus 81 Restformen wird ein Stamm-und-Ausbau-Wörterbuch

Status: `PASS_81_FRAGMENT_TARGETS_MAPPED__72_ALIGNED_STEMS__13_RECURRENT_CHANNELS`

## Ergebnis

Jede der 81 Fragment-plus-Atom-Formen besitzt nun eine konkrete Karte der Form

```text
linker Ausbau + [altes vollständiges Rezept] + rechter Ausbau
```

Es gibt 104 gleich lange mögliche Altstämme. Der Reader bewahrt sie alle und
wählt pro Ziel einen Hauptstamm nach derselben endlichen Priorität. 63
verschiedene Stämme werden gewählt; sechzehn Stammfamilien tragen zusammen 34
Ziele.

Der wichtige Zusatz liegt auf der sichtbaren Ebene: Bei 72/81 Zielen ist eine
alte Oberflächenform des gewählten Ganzrezeptes buchstabengetreu und an genau
der erwarteten linken, rechten oder inneren Stelle der neuen Oberfläche
erhalten. Das Modell ist hier also wirklich „gelernte Stammkarte plus sichtbare
Kürzel“, nicht bloß eine nachträgliche Aufteilung der Bedeutungsfolge.

## Dreizehn wiederkehrende Kürzelkanäle

Die 72 sichtbaren Stammkarten liefern 83 linke/rechte Ausbauvorkommen und 53
verschiedene sichtbare Kanäle. Vierzehn wiederholen sich. Dreizehn davon
behalten über alle Vorkommen dieselbe Rezeptabbildung:

- links `ch→CH`, `d→D_ADDR`, `f→LOCAL_CHAR_F`, `k→K`, `l→L`, `p→P`,
  `sh→SH`, `t→T`, `y→Y`;
- rechts `aiin→AIIN`, `chy→CH+Y`, `d→D_ADDR`, `y→Y`.

Sie decken 34 Zieloberflächen ab. Nur ein wiederkehrender Kanal bleibt
mehrdeutig: rechtes `dy` ist fünfmal `DY`, aber bei `kcheody` einmal
`D_ADDR+Y`. Das ist keine Panne, sondern eine nützliche Vorhersagegrenze: Der
sichtbare Rest allein genügt dort nicht; Stammfamilie und vollständiges Rezept
entscheiden weiter.

## Atomgrenzen und alte Überkarten

Die 81 Karten besitzen 93 Ausbauarme. 87 ihrer direkten Andockpaare sind
bereits innerhalb alter vollständiger Karten sichtbar. Bei 28 Armen kommt
mindestens das grenznahe Erweiterungsatom zusammen mit dem ganzen Stamm in
einer alten längeren Karte vor; fünfzehn vollständige Arme tun das.

Acht komplette Zielrezepte erscheinen sogar als zusammenhängende Teilfolge in
19 längeren alten Ganzkarten: `cheod`, `cholpchd`, `dard`, `kody`, `qoteeod`,
`saiis`, `sheod` und `tcheo`. Das sind echte Reduktionsbrücken, obwohl die
kürzere Zielkarte dort nicht als selbständiges Ganzrezept steht.

Sechs Andockpaare bleiben neu: `AIIN>CH` in `aiicthy`, `A_ADDR>DY` in `chady`,
`A_ADDR>P` in `chap`, `P>A_ADDR` in `chepakeo`, `AR>AM_ADDR` in `ofaram` und
`R>OT` in `rotaiin`. `chady` und `chap` behalten trotzdem die bereits separat
belegte `cha`-Stammregel; die anderen vier bleiben benannte Einzeldefaults.

## Satzkontext bleibt sichtbar

Wenn die vollständige Zielkarte probeweise an den alten Stammereignissen
gelesen wird, stimmt die Modusmenge bei 53 Zielen exakt. Bei weiteren sechzehn
ist der Zielmodus enthalten und das alte Material erlaubt zusätzlich einen
zweiten Modus. Zwölf Zielmodi kommen in den Umgebungen des gewählten Stammes
nicht vor.

Diese zwölf Karten werden nicht umgedeutet. Der Befund sagt nur, dass der
Stamm bisher in einem anderen laufenden Satzstand erscheint; der neue Ausbau
oder die neue Satzposition kann den Modus wechseln. Selbst bei den acht
Überkarten sind vier Kontextbrücken passend und vier nur strukturell. Der
Reader zeigt deshalb Struktur und Kontext als zwei getrennte Spalten.

## Arbeitsentscheidung und nächster Griff

Alle 81 Bedeutungen bleiben erhalten und sind jetzt wesentlich genauer
vorhersagbar: alter sichtbarer Stamm, gerichteter Ausbau, Kürzelkanal,
Atomgrenze und Satzmodus stehen explizit nebeneinander. Keine Sequenz fällt auf
eine vage Ganzwortbedeutung zurück.

Als Nächstes sollten die zwölf abweichenden Stammkontexte und sechs neuen
Andockpaare gegen die 23 nicht gewählten gleich langen Altstammoptionen gelesen
werden. Eine alternative Stammwahl darf nur besser werden, wenn sie die
sichtbare Richtung bewahrt und Kontext oder Grenze konkret repariert. Karten,
die dadurch nicht gewinnen, bleiben ausdrücklich als heutige Defaults stehen.

Alle 44 Prüfungen bestehen. Keine Seite, Bedeutung, Zerlegung oder Rezeptkarte
wurde verändert.
