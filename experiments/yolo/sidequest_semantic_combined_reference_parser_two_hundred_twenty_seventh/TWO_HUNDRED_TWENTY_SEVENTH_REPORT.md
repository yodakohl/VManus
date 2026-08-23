# Zweihundertsiebenundzwanzigster Durchgang: kombinierter Werkstattparser

Die Rückkehr- und Doppelungsregeln sind nun in einem gemeinsamen recordweiten Parser verbunden. Er unterscheidet drei Ebenen:

- 381 sichtbare Karten;
- 380 Quelltoken, weil die f82r-Zeilenforttragung zweimal sichtbar, aber einmal gemeint ist;
- 357 Leseeinheiten, davon 343 Einzelkarten und 14 zusammengesetzte Konstruktionen.

Die 14 Konstruktionen tragen 15 Regelanwendungen. Der Unterschied entsteht durch das einzige verschachtelte Fenster `dy chy taiin shy`: `dy chy` setzt zwei Posten, während `chy taiin shy` den zweiten Posten über den Sollwert hinweg aktiv hält.

Der Parser verändert keine Kartenbedeutung. Er erklärt nur, wie ein Schreiber dieselben kleinen Wörter durch Wiederholung und Rahmung zu Mehrzahl, Wiederholung, Rückbezug und Zeilenforttragung zusammensetzen konnte.

Als nächstes wird geprüft, ob diese vier Konstruktionsarten ausreichen, um ein kurzes zusammenhängendes f10r- und f83r-Stück ohne zusätzliche moderne Bindewörter zu übersetzen.
