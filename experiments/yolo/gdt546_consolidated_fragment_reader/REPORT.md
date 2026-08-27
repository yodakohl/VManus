# GDT546 — die 81 Fragmentkarten sind jetzt ein Reader

Status: `PASS_81_CARD_FRAGMENT_READER__4_DUAL_BRIDGES__12_EXPLICIT_DEFAULTS`

## Ergebnis

Die 81 bisher über mehrere Experimente verteilten Fragment-plus-Atom-Lesungen
lassen sich ohne Bedeutungsänderung in einen einzigen exakten Reader
kompilieren. Jede Karte gibt nun gemeinsam aus:

- Oberfläche und vollständige Komponentenfolge;
- neutrale deutsche Komponentenlesung und bekannte Kontextlesung;
- Hauptstamm mit sichtbarer Stammspur;
- linken und rechten Ausbau samt Kürzelkanal und alter Andockkante;
- Stammkontext und alte Überkarten;
- eine optionale zweite Herleitung oder den genauen Restvorbehalt.

Damit kommt bei diesen 81 Formen keine Sequenz mehr als bloßes, vage
glossiertes Ganzwort davon. Der Reader zeigt immer die derzeitige
Komponentenbedeutung und die konkrete Herleitung, die sie trägt.

## Was die gemeinsame Ausgabe zeigt

Die früheren Teilbefunde bleiben unverändert sichtbar: 72/81 Hauptstämme sind
buchstabengetreu und richtungsgleich in der Zieloberfläche erhalten; einer ist
nur richtungsabweichend, acht besitzen keine exakte alte sichtbare Stammform.
69/81 Hauptstämme erlauben den Ziel-Satzmodus, 12 bleiben Kontextdefaults. Von
93 direkten Ausbaukanten sind 87 alt. Je 34 Karten liegen in einer
wiederkehrenden Hauptstammfamilie beziehungsweise benutzen mindestens einen
wiederkehrenden invarianten sichtbaren Kürzelkanal. Acht vollständige
Zielrezepte stecken zusätzlich in alten längeren Karten.

Vier Karten zeigen jetzt zwei Herleitungen:

- `chckhedy`: `CH+CH+[K+E+DY]` plus `CH+[CH+K]+E+DY`;
- `chepakeo`: `[CH+E+P]+A_ADDR+K+E+O` plus
  `CH+E+P+A_ADDR+K+[E+O]`;
- `chepos`: `[CH+E+P]+O+S` plus `[CH+E]+P+O+S`;
- `tosheo`: `T+[O+SH+E+O]` plus `T+O+[SH+E]+O`.

Bei `chckhedy` bleibt die sichtbare Richtung der zweiten Brücke ausdrücklich
abweichend. Die anderen drei Zweitstämme liegen exakt an der erwarteten
Oberflächenposition. Alle vier Hauptstämme bleiben unangetastet.

Die zwölf übrigen Warnkarten werden nicht verworfen: `aiicthy`, `chady`,
`chap`, `folchol`, `kody`, `ofaram`, `qoekedy`, `qokshd`, `qoteeod`,
`rotaiin`, `saiis` und `shokaiir` erhalten weiterhin eine vollständige
Defaultlesung, jetzt aber mit ihrem konkreten Kontext- oder Kantenrest direkt
in derselben Ausgabe.

## Praktischer Gebrauch

```bash
python3 experiments/yolo/gdt546_consolidated_fragment_reader/src/read_fragment.py \
  --surface chepakeo
```

Ein unbekannter Schlüssel stoppt mit `STOP_UNKNOWN_FRAGMENT_SURFACE`; der
Reader zieht keine ähnlich geschriebene Karte heran. Alle 33 Prüfungen
bestehen, einschließlich vollständiger Quellfeld-Replays, sichtbarer
Rekonstruktionen, CLI-Stop und byteidentischem Generator-Neulauf.

## Nächster Griff

Die Fragmentgruppe ist damit praktisch benutzbar. Als Nächstes sollen die
letzten 24 Atom/Faktor-Formen aus GDT542 denselben Vertrag bekommen:
vollständige Defaultbedeutung, konkrete sichtbare Atom- oder Faktorherleitung,
Kontextspur und exakt benannte Restlücke. Dafür wird keine neue Seite geöffnet.

GDT546 ändert keine Seite, Oberfläche, Rezeptkarte, Hauptstamm oder
Wurzelbedeutung. Die deutschen Sätze bleiben Arbeitslesungen, kein behaupteter
Klartext.
