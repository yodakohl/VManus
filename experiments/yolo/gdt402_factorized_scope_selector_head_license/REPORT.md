# GDT402 — Der Scope-Parser ist vollständig faktorisiert

## Ergebnis

Alle **4.374/4.374** Fokusanschlüsse lassen sich als Produkt unabhängiger
Entscheidungen lesen. Es braucht weder eine neue Grundregel noch eine
registerprivate Ausnahme.

Die Maschine besitzt:

- 8 Scope-Selectoren;
- 6 sichtbare Anschlusslagen;
- 10 mögliche Handlungsköpfe einschließlich sichtbarem Besitzer;
- 4 R-Lagen (`NONE`, Kopf, Schwanz, geschachtelt);
- 3 Wiederholungsmodi.

Beim Registertransfer genügen für 4.295 Anschlüsse Fokuswert+Lage+Selector, für
78 Fokusfamilie+Lage+Selector. Genau ein bereits bekannter f77r-Fall
`dalchedy` fällt auf die Grundregel `AL_AR_ORDERED_FALLBACK` zurück. Beim
Seitentransfer sind es 4.365/8/1. Kein Fall braucht einen unbekannten Selector.

## Warum die GDT400-Warnungen verschwinden

GDT400 schrieb etwa
`ONE_CARD_FORWARD|R_POSITIONAL_MARKING` als eine kombinierte Regel. Das mischt
zwei Fragen:

1. **Wohin läuft der Fokus?** — genau eine Karte vorwärts.
2. **Welches sichtbare Atom ist dort der Kopf?** — `R` in Kopfposition.

Getrennt besitzen alle vier früheren Warnzeilen schon auf der exakten
Fokus-Selector-Ebene Unterstützung außerhalb ihres Registers; `R` ist als Kopf
ebenfalls außerhalb des Registers vorhanden. Sie werden daher nicht durch
grobe Ähnlichkeit gerettet, sondern durch zwei alte, geordnet ausgeführte
Operationen.

## Zwei lokale Topologien

Nur zwei Formen bleiben als sichtbare Spezialbilder im Lehrbuch:

- ein einzelnes geschachteltes R auf f18r;
- zwei Fokuszeilen eines Paketabstiegs bei der Doppel-EINHEIT auf f13r.

Beide sind aus sichtbarer Kartenposition ableitbar. Sie sind keine neue
Distanzregel und keine neue Bedeutung. Eine anders geformte neue R- oder
Doppelstruktur bleibt auf künftigen Seiten gelb, bis sie sich mit denselben
Topologieregeln lesen lässt.

## Praktische Folge

Die nächste Seite wird nicht mehr gegen hunderte zusammengesetzte Signaturen
verglichen. Der Leser segmentiert die Karte, wählt einen der acht Selector,
findet den Zielkopf und löst erst danach R- oder Doppelpaket-Topologie. Das
senkt die Zahl scheinbarer Ausnahmen, ohne die 19 Kernwerte beweglich zu machen.
