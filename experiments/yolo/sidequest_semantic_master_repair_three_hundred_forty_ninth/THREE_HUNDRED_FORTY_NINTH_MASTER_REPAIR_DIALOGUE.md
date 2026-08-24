# Drei Fehlkopien und ihre Reparatur

Der Meister lässt drei Fehler absichtlich stehen. Er benutzt keine neue
Bedeutung, sondern nur Kartenregister, Stofffaden und Slotreihenfolge.

## Fehler 1: CARD_IDENTITY

**Lehrling:** `qokedy`

**Folge:** Die Oberfläche dekodiert als Kurzkontakt (7db18b2f0fb7ed0fcfd3), nicht als Klarauszug.

**Meister:** Richtiger Slot, aber falsche Kartenidentität; die Form gehört zu einem Kontaktgang.

Er zeigt drei Hinweise:

1. Das geforderte Ergebnis im Arbeitsgang ist Klarauszug.
2. Nachseihen → Klarauszug → Rücknahmeschluss bildet die lokale Stofffolge.
3. qokedy ist bereits eine andere registrierte Karte für Kurzkontakt.

**Reparatur:** qokedy durch shey ersetzen; cheey wäre dieselbe registrierte Klarauszug-Karte in einer anderen Hand.

## Fehler 2: MATERIAL_THREAD

**Lehrling:** `Rohteil → Anwendungsposten`

**Folge:** Der Lehrling verwirft beim Mikrogangwechsel die unmittelbar gesetzte bemessene Portion.

**Meister:** Karten und Slots stimmen, aber der Stofffaden wurde ohne Marker zurückgesetzt.

Er zeigt drei Hinweise:

1. E207 setzt sichtbar Sollmaß und damit Bemessene Portion.
2. E208 Diesposten verweist auf genau den laufenden, nicht auf einen neuen Posten.
3. Zwischen E207 und E209 steht kein Rohteil-Marker.

**Reparatur:** E208 mit Bemessene Portion beginnen und erst durch E209 Volleinsatz zu Anwendungsposten wechseln.

## Fehler 3: SIX_SLOT_ORDER

**Lehrling:** `Mikrogang 3: E180 E181 E182; Mikrogang 4: E183`

**Folge:** Folgevorbereitung wird hinter zwei Sollstellungen in denselben Gang gezogen.

**Meister:** Kein Wortfehler, sondern eine ausgelassene Mikroganggrenze vor E182.

Er zeigt drei Hinweise:

1. Die Slotfolge würde S2 → S2 → S1 rückwärts laufen.
2. Ein neuer S1-Bezug eröffnet nach der Sollstellung den nächsten Arbeitsgang.
3. Der folgende Langwärmen-Schritt S4 gehört zu diesem neu eröffneten Gang.

**Reparatur:** Grenze zwischen E181 und E182 einsetzen; E182 S1 und E183 S4 bilden Mikrogang 4.

## Werkstattergebnis

Alle drei Fehler werden eindeutig lokalisiert. Einer betrifft die Karte,
einer den fortlaufenden Stoff und einer nur die Gliederung. Die Schreiber
müssen deshalb nicht jeden Satz auswendig kennen: mehrere schwache Kanäle
überlappen und stellen die richtige Lesung wieder her.
