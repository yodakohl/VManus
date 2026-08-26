# Mechanischer Parser für die nächsten Seiten

## 1. Sichtbares Rezept

Die Oberfläche wird zuerst mit ihrem vorhandenen Rezept gelesen. Eine neue
Oberfläche darf nur sichtbare Atome enthalten; Ein-Edit-Nachbarn liefern keine
unsichtbaren Zeichen.

## 2. Scope-Selector wählen

Für jeden Fokus genau einen Selector benutzen:

- `NEAREST_HEAD_LEFT_TIE`: nächster Kopf, bei Gleichstand links;
- `AL_AR_ORDERED_FALLBACK`: links → aktiver Kopf → gleicher Kartenkopf rechts → Besitzer;
- `L_AIR_RIGHT_FALLBACK`: rechts, sonst links, sonst aktiver Kopf/Besitzer;
- `PREVIOUS_CARD_STACK`: unmittelbar voriger offener Kopf;
- `INHERITED_ACTION_STACK`: im Besitzerblock geerbter Kopf;
- `ONE_CARD_FORWARD`: erster sichtbarer Kopf genau der nächsten Karte;
- `Q_OT_PACKAGE_FORWARD`: Q-/OT-Paket zum ersten Kopf genau der nächsten Karte;
- `OWNER_CONTEXT`: sichtbarer Besitzer, wenn kein Handlungskopf lizenziert ist.

## 3. Zielkopf lizenzieren

Der gewählte Zielatom muss einer der zehn belegten Köpfe sein:
`CH`, `CHD`, `K`, `OK`, `P`, `R`, `S`, `SH`, `T` oder `OWNER`.

Bei `R` wird danach nur seine sichtbare Lage entschieden:

- erster eigener Kopf mit rechtem Glied: `R_HEAD`;
- voriger Kopf aktiv, R ohne eigenes rechtes Glied: `R_TAIL`;
- voriger Kopf aktiv und R besitzt ein eigenes rechtes Glied: `R_NESTED`.

Die R-Lage ändert weder Blickweite noch Kernwert.

## 4. Zielkarte von innen lesen

Ein vorwärtsgereichtes Paket bindet zuerst an den ersten Kopf. Danach werden
die internen Argumente der Zielkarte mit denselben Selectorregeln gebunden.
Darum lautet `Y | R+SH+...+Y`:

`R[Y_previous] ; SH[Y_internal]`.

## 5. Doppelungen

Freie Doppelung bleibt Peer/Mehrzahl/Wiederholung. Sichtbar geschachtelte
Doppelung bleibt äußerer und innerer Paket-Scope. Die zweite Kopie wird nie
stillschweigend gelöscht.

## Stopp

Stoppen, wenn ein Fall mehr als eine Karte springt, eine Besitzer- oder
Aussagegrenze überquert, einen elften Kopf oder neunten Selector verlangt,
einen bekannten Kern umdeutet oder ein unsichtbares Atom importiert.
