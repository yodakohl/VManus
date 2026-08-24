# Bewegliche Fallkarten

Der Fallselektor und die Handlungsreihenfolge sind getrennt: jede Fallkarte wird durch Position 1 bis 5 geschoben; danach wird einmal der Fall erkannt und einmal die Arbeitsreihenfolge gelesen.

## C1: os = ARBEITSFACH

Erlaubte Positionen: **1|2**. Klasse: **LIMITED_EARLY**.

Regel: ARBEITSFACH MUSS VOR WASCHGANG STEHEN.

## C2: cthy = BEREIT

Erlaubte Positionen: **1|2|3|4|5**. Klasse: **FREE_EARLY**.

Regel: BEREIT-CHECK DARF VOR DEM VOLLSCHLUSS WANDERN.

## C3: cfhy = AUSWRINGEN

Erlaubte Positionen: **1**. Klasse: **POSITION_BOUND**.

Regel: AUSWRINGEN MUSS VOR EINFUELLEN STEHEN.

## C4: ykan = NACHPORTION

Erlaubte Positionen: **3**. Klasse: **POSITION_BOUND**.

Regel: NACHPORTION MUSS AUF PORTION UND VOR ZIEL FOLGEN.

## C5: cho = ZUTAT

Erlaubte Positionen: **1|2**. Klasse: **LIMITED_EARLY**.

Regel: ERSTE ZUTAT MUSS VOR WEITERER ZUTAT STEHEN.

## Lehrmeisterschluss

Alle 25 Varianten bleiben als Fall erkennbar, aber nur elf bleiben als Arbeitsfolge sinnvoll. BEREIT ist eine frei wandernde Pruefkarte. ARBEITSFACH und ZUTAT koennen begrenzt als fruehe Ueberschrift wandern. AUSWRINGEN und NACHPORTION sind reihenfolgegebundene Handlungen. Der Fallhinweis ist also semantisch beweglich, die Prozesssyntax jedoch nicht beliebig.
