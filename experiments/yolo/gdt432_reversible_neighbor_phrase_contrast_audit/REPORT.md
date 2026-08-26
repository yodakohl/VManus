# GDT432 — Das Zukunftsdeck bleibt beim Wurzelwechsel hörbar

## Ergebnis

Der GDT431-Fehler, den wir vor Veröffentlichung bereits bei `AIR+Y` gegen
`Y+AIR` repariert hatten, taucht an keiner anderen Stelle wieder auf.

- **145/145** allgemeine Nachbarwege ändern genau einen Bedeutungsplatz;
- **145/145** erzeugen eine andere kurze Werkstattphrase;
- **725/725** Registervergleiche behalten denselben lokalen Unterschied;
- **47/47** Zukunftskarten bestehen alle drei oder vier Nachbarwege;
- **30/30** tatsächlich verwendete gerichtete Wurzelwechsel bleiben hörbar.

Ein Beispiel ist die Hochprioritätskarte `AL+AIN`:

- `AL+AIIN` → `AL+AIN`: **WERT → ANTEIL**;
- `AL+OR` → `AL+AIN`: **EINHEIT → ANTEIL**;
- `AL+Y` → `AL+AIN`: **POSTEN → ANTEIL**;
- `L+AIN` → `AL+AIN`: **VERBINDUNG → ZIELORT**.

Alles andere bleibt positionsgleich. In der Herbal-Fassung wird daraus
„An der Zielstelle: Materialanteil“, im Biological-Register „An der
Zielstation: Stationsanteil“ und im Himmelsregister „An der Zielposition:
Sektoranteil“.

## Was der Test praktisch verbessert

Die deutsche Lesung darf nicht so flüssig werden, dass zwei verschiedene
Rezepte gleich klingen. Deshalb enthält die Audittabelle neben normaler Prosa
eine explizite Slotspur, zum Beispiel:

`1:ACTION_HEAD=NEHMEN | 2:RELATION=ZIELORT`

gegen

`1:ACTION_HEAD=NEHMEN | 2:RELATION=AUSGANG`.

Damit ist jederzeit sichtbar, ob lediglich der gewünschte Kern gewechselt hat.
Wiederholte Formen wie `Y+Y`, `OR+OR` oder `L+SH+L` verlieren ihren äußeren und
inneren Platz nicht in der Grammatik.

## Die 30 Wechsel

Das Deck benutzt beide Richtungen, wo sie wirklich gebraucht werden. Dazu
gehören unter anderem:

- WERT→ANTEIL neunmal und POSTEN→ANTEIL elfmal;
- GEBEN→EINSETZEN neunmal, SETZEN→EINSETZEN siebenmal;
- ZIELORT→BAHN siebenmal und AUSGANG→BAHN achtmal;
- VERBINDUNG→ZIELORT einmal und VERBINDUNG→AUSGANG dreimal;
- BEARBEITEN→HALTEN viermal und WÄHLEN→NEHMEN zweimal.

Jedes Paar besitzt bereits direkte gemeinsame Frames aus GDT428/GDT429; der
kleinste verwendete Paarbeleg umfasst drei solche Frames.

## Ehrlicher Rand

Von den 725 lokalen Vergleichen liegt das Quellrezept in **275** Fällen auch
tatsächlich in genau diesem Register vor. Die übrigen **450** verwenden das
schon festgelegte GDT415-Registerwörterbuch als Gegenprobe. Sie zeigen, dass
unsere Leseregel dort nicht kollabiert; sie sind keine 450 neuen
Manuskriptbelege.

Der Test ist daher eine wichtige interne Qualitätskontrolle und kein neuer
Beweis für NEHMEN, WERT oder BAHN. Sein positiver Nutzen ist konkret: Das
47-Karten-Deck kann später angewendet werden, ohne dass der gewählte
Ein-Kern-Wechsel in der flüssigen Lesung verschwindet.
