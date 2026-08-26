# GDT453 — Alle erreichbaren Grenzen synchronisieren

## Ergebnis

Die 765 GDT452-Fälle ohne unmittelbare Folgekarte verteilen sich so:

| Grenze | Fälle | Ausgang |
|---|---:|---|
| gleicher Besitzer, nächste Aussage | 695 | 695 grün |
| neuer Besitzer, gleiche Seite | 29 | 29 grün |
| neue Seite | 31 | 31 grün |
| Ende des gesamten Stroms | 10 | keine Karte |

Alle 755 vorhandenen Grenzkarten lesen grün. Es gibt keinen weiteren Stopp und
keine gelbe Herabstufung.

## Warum die Trennung wichtig ist

Bei den 695 gleichen Besitzern wird genau der Zustand verwendet, den der
vorherige Stopp erhalten hat. Das ist der harte Recovery-Test über eine
Aussagegrenze.

Bei 60 Besitzer- oder Seitenwechseln wäre derselbe Zustand dagegen falsch. Der
Leser wählt dort die schon bestehende Bank des neuen Besitzers. In 0/60 Fällen
wird der gestoppte Fremdzustand übernommen. Damit ist Recovery nicht mit einem
pauschalen globalen Reset erkauft.

Die zehn fehlenden Grenzkarten sind zehn Zielvarianten desselben letzten
Ereignisses `G407-E4576`; hinter ihnen existiert im 4.576er Strom nichts mehr.

## Praktische Folge

Der integrierte Leser kann jetzt drei Fehlerlagen sauber behandeln:

1. normaler Stopp, nächste Karte liest sofort;
2. abhängiger Schluss stoppt mit und die nächste Aussage synchronisiert;
3. Stopp am Aussageende, gleiche oder neue Besitzerbank setzt korrekt fort.

Das beseitigt einen operativen Unsicherheitsrest. Es bestätigt weiterhin kein
Voynich-Wort und keine Übersetzung.
