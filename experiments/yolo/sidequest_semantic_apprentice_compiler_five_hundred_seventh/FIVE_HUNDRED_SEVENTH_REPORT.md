# Pass 507 — der konkrete Lehrlings-Compiler

Die bisher getrennten Ebenen bilden nun einen einzigen zwölfstufigen
Werkstattablauf:

1. sichtbaren Bildbesitzer wählen;
2. aktiven Posten übernehmen oder beim Besitzerwechsel zurücksetzen;
3. Herbal- oder Bio-Schreibmodus wählen;
4. einen häufigen Weg oder eine freie Primitivfolge wählen;
5. die Folge im Fünf-Zustands-Automaten beginnen;
6. Quellen- und Maßsperren beachten;
7. passende Komponenten- oder Ganzkarten wählen;
8. bei einer Endkarte erst die Handlung, dann `CLOSE` ausführen;
9. Körper und Wrapper als sichtbare Oberfläche schreiben;
10. am Zeilenende nur umbrechen, nicht automatisch beenden;
11. offen weiterführen oder ausdrücklich schließen;
12. Oberfläche, Karte, Handlung und Besitzer rückwärts kontrollieren.

Alle 381 Prosakarten sind damit vorwärts und rückwärts durchgeschrieben. Sie
erzeugen 470 Prozessprimitive in 116 Aussagen und elf Records. 21
Besitzerwechsel setzen den Gegenstand zurück, ohne automatisch die
Ablaufmaschine zu schließen.

314 Oberflächen folgen direkt aus Körper und den kompakten Schreibgewohnheiten.
67 seltene Allographen müssen weiterhin aus dem lokalen Exemplar kopiert
werden. Das ist für eine kleine Werkstatt plausibel: Die Grammatik ist
lehrbar, die komplette graphische Palette bleibt teilweise exemplarabhängig.

Der entscheidende Gewinn ist die Rücklesbarkeit der Ebenen. Eine sichtbare
Karte ist nicht gleichzeitig Wort, Bildbesitzer und Satz. Der Leser bestimmt
erst die Karte, dann ihre Prozesshandlung, hält den aktuellen Besitzer fest und
liest erst daraus die lokale Werkstattaussage.

Als Nächstes wird derselbe Compiler auf die drei Astro-Seiten erweitert, jedoch
ohne die Prosa-Primitiven in Himmelsnamen umzudeuten. Astro erhält eine eigene
kleine `LOCATE → READ → RECORD`-Schleife unter demselben Exemplarprinzip.
