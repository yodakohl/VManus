# GDT405 – Vorhersagepaket für den zweiten Zufallsbatch

## Ergebnis

`SECOND_RANDOM_BATCH_LOCK_READY`.

Vor der nächsten Seitenfreigabe sind nun exakt gesperrt:

| Bestand | Zahl |
|---|---:|
| Oberflächenrezepte | 426 |
| Zeichenwerte | 46 |
| Parserfaktoren | 31 |
| Amber-Mikrogrenzen | 49 |
| leere Seitenplätze | 4 |
| Aufnahme-/Stoppregeln | 12 |

Eine bekannte Oberfläche muss auf der nächsten Seite ihr GDT405-Rezept
behalten. Eine unbekannte Oberfläche darf sichtbar aus alten Zeichen bestehen.
Ein Ein-Edit-Nachbar darf kein unsichtbares Zeichen liefern. Kernwertänderung,
neuer Faktor, Besitzer-/Aussagegrenzsprung oder Vorgriff über mehr als eine
Karte stoppt den Batch.

Die 49 Amber-Formen sind nicht heimlich grün geworden. Bei exakter Wiederkehr
wird zuerst das gesperrte Primärrezept gelesen und dann nur die sichtbare
Paketgrenze geprüft. Bestätigung kann Amber zu Green machen; eine neue Bedeutung
kann es nicht.

Damit ist der nächste Lauf erstmals ein harter Durchsatztest gegen **426 echte
Oberflächenvorhersagen**, nicht wieder nur eine nachträgliche Zerlegung.
