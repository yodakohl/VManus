# GDT489 — der letzte Singleton bekommt einen typisierten Weg

Status: `EINSTELLEN_HAS_TWO_TYPED_COMPOSITION_EDGES__ALL_SIXTEEN_SINGLETONS_CONNECTED`

## Ergebnis

Die elf exakten GDT428-T/R-Rahmen tragen zusammen 30 T- und 46 R-Ereignisse.
Zehn Rahmen besitzen einen nichtleeren Nachbarkontext. Neun davon erscheinen
bereits in den 183 lokalen Events: 168 Rahmen×Event-Zeugen, 175 konkrete
Positionen und 121 verschiedene Events. Nur `CHD+Y = BEARBEITEN · POSTEN`
fehlt lokal als zusammenhängender Kontext.

Diese breite Kontextkapazität wird nicht pauschal auf EINSTELLEN übertragen.
Tatsächlich berühren die zwei lokalen T-Events genau drei nichtleere
T-Teilrahmen:

- `G485-E118 CH+T` trifft `CH+@ACTION` als ganzen Event;
- `G485-E133 CH+T+Y` trifft `CH+@ACTION` als Präfix;
- derselbe Event trifft `@ACTION+Y` als Suffix.

Daraus entstehen genau zwei typisierte Kompositionskanten:

- `NEHMEN → EINSTELLEN`, zweimal lokal und in zwei Registern;
- `EINSTELLEN → POSTEN`, einmal lokal im pharmazeutischen Träger.

Die beiden festen deutschen Lesungen zeigen genau diese Rollen: „nimm … und
stelle … ein“ sowie „… den Posten … stelle beide ein“. Es wird kein zusätzlicher
Satz analog gebildet.

## Vollständige Verbindung

`POSTEN ↔ HIER` ist in GDT486 eine zweimal wiederkehrende Ersatzkante. Deshalb
besitzt der letzte Singleton nun den alternativen Weg:

`EINSTELLEN —Komposition→ POSTEN —wiederkehrender Ersatz→ HIER`.

Der Weg ist vollständig, aber nicht homogen. `EINSTELLEN ↔ HIER` bleibt ein
kapazitätsbegrenzter Ersatzendpunkt und wird nicht nachträglich zu einem reinen
Ersatzzyklus erklärt. Im typisierten Gesamtgraphen sind jetzt dennoch alle
sechzehn ehemaligen Einzelregeln verbunden: fünfzehn durch reine
Ersatzzyklen, eine durch diesen gemischten Weg.

Der deterministische Validator besteht 98 von 98 Prüfungen. Keine Bedeutung,
Formulierung, Modellfolge, Grenze, Oberfläche, Rezeptfolge, Event- oder
Seitenzuordnung ändert sich.

## Nächster sinnvoller Schritt

Aus den zwei beobachteten T-Kompositionsformen kann ein kleines Satzmuster
gebaut werden. Weitere T-Rahmen mit `WERT`, `ANTEIL`, `ZIELORT`, `FORTSETZEN`
oder `POSTEN` erhalten erst dann eine konkrete Formulierung, wenn ihre
GDT428-T-Träger selbst mit einer lesbaren Quelle verbunden sind. Der lokal
fehlende Kontext `CHD+Y` bleibt offen.
