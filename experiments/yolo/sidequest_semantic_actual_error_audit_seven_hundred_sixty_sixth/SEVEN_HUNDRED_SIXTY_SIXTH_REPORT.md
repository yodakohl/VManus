# Pass 766 — Welche wirklichen Stolperstellen sind Schreibfehler?

Die kurze Antwort: fast keine.

Es gibt drei unmittelbar doppelte exakte Karten. Nur `E180/E181` sitzt genau an der bekannten physischen Zeilengrenze und erfuellt die lokale Read-once-Regel. Beide Formen bleiben sichtbar, aber der Schreiber spricht bzw. plant nur eine Quellkarte. `E020/E021` und `E033/E034` stehen mitten in ihren Formeln, haben jeweils zwei Oberflaechen und keinen Randhinweis; sie bleiben absichtliche Wiederholung oder gelernte lokale Formel.

Auch die anderen vermeintlichen Fehler verschwinden beim Blick auf das ganze kleine System:

- 27 von116 Aussagen sind regelhaft offen, 15 Herbal und12 Bio. Wir setzen keinen erfundenen Schluss ein.
- Acht Kartenfamilien benutzen mindestens zwei der Grade E/EE/EEE. Ein seltener Vollgrad ist deshalb kein Schreibfehler.
- Vier Aussagen wechseln mitten im rekonstruierten Satz sichtbar den Bildbesitzer. Der Besitzerwechsel ist staerker als unser Satzfluss; wir verbinden die Stationen nicht kuenstlich.

Damit haben wir381 sichtbare Karten, aber380 logische Quellkarten. Der einzige produktionsnahe Sonderfall ist eine lokale Randwiederholung; er wird nicht ausradiert, sondern beim Lesen einmal verbraucht.

Als naechstes wird der Vorwaertskompiler genau so umgebaut: erst380 logische Quellkarten erzeugen, dann als reine Schreib-/Layoutoperation die Randkopie E180 einfuegen und wieder381 sichtbare Karten liefern.
