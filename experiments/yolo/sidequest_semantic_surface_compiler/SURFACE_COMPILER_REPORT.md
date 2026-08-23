# Oberflächen-Compiler der Werkstatt

## Was korrigiert wurde

Der vorige Durchgang war bei `DCH` zu schnell. `dchol/schol` kann weiterhin als gelernte Karte **VORIGER POSTEN** gelesen werden, aber `DCH` ist kein tragfähiger Stamm: dieselben sichtbaren Buchstaben liegen auch in Umsetzungsformen wie `dchdy`, `dchedy`, `chedchy` und `shecthedchy`. Der Compiler verwendet deshalb längsten Treffer: `CHD~CHED = UMSETZEN` schlägt jede freie `DCH`-Analyse. Die sieben anderen alten Brücken sind vorerst nur gelernte lexikalische Körper oder Schwänze, keine produktiven Stämme.

## Neue Arbeitsregel

Eine sichtbare Karte wird von außen nach innen gelesen:

1. registrierte Renderer-/Schreiberform erkennen;
2. längsten bekannten Körper nehmen (`AIR`, `CHD~CHED`, `CKHE` vor kürzeren Treffern);
3. portable Operatoren und Adressen lesen (`OK/OL/OT`, `AIIN/AIN/IIN`, `AL/AR/AIR`);
4. nur in einer belegten Familie `E/EE/EEE` als kurz/länger/voll lesen;
5. `Y` nur als lizenziertes Postenargument und `DY` nur exact-card-gebunden als Schluss lesen.

Damit besitzen 163/173 Kartentypen und 365/381 Prosaereignisse mindestens einen sichtbar wiederverwendbaren Beitrag. Das ist noch keine Buchstabenentzifferung: der Compiler trennt echte Oberflächenhinweise von gelernten Fachkörpern.

## Verteilung der 173 Karten

- `LEXICAL_BODY_PLUS_PRODUCTIVE_SUFFIX`: 90 Karten / 167 Ereignisse
- `LEXICAL_ROOT_ONLY`: 2 Karten / 5 Ereignisse
- `LITERAL_PRODUCTIVE_PARSE`: 63 Karten / 157 Ereignisse
- `MEMORIZED_WHOLE`: 9 Karten / 15 Ereignisse
- `PRODUCTIVE_FRAME_PLUS_MEMORIZED_BODY`: 7 Karten / 7 Ereignisse
- `RENDERER_ALIAS_PLUS_PRODUCTIVE_PARSE`: 2 Karten / 30 Ereignisse


## Produktive Vorhersage statt Rückerzählung

`FORWARD_PREDICTIONS.tsv` enthält 18 vorwärts gebildete Zellen. Die Regel darf eine bisher nicht belegte Karte lesen, falls sie später auftaucht; sie darf aber keine vorhandene Karte still umbenennen. Treffer in den 230 Formen werden deshalb nur als Review-Kandidaten markiert. Die stärksten Reihen sind derzeit `OK`, `OL`, `OT`, `CHD`, `CTH`, `CKH`, `CHK`, `SHED`, `SOLK`, `HO`, `L`, `Y` und `OR`.

## Kollisionsaudit

Sichtbare Formen mit `dch`: chedchy, dchdy, dchedy, dchey, dchol, shecthedchy. Nur `dchol/schol` bleibt als gelernter Ganzwert; die Umsetzungsfamilie behält `CHD~CHED`. Ebenso bleiben `CFH`, `CPH`, `DCHE`, `LDDY`, `SK`, `DAN` und `AM` kurze Werkstatt-Mnemonics, bis eine zweite unabhängige Karte denselben Körper produktiv benutzt.

## Nächster Hebel

Der Compiler wird im nächsten Pass nicht auf weitere Bedeutungen trainiert, sondern auf die 381 laufenden Kontexte angewandt. Besonders wichtig sind die leeren Vorhersagezellen und die Karten, deren sichtbare Form zwar passt, deren bisheriger Ganzwert aber widerspricht. Danach wird derselbe Parser ohne neue Wortbedeutung gegen die 395 Astrogruppen gehalten.
