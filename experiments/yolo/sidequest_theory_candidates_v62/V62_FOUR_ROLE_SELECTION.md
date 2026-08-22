# V62 — Vierrollen-Auswahl: anonymes Ellipsengedächtnis

Status: kreative Registerrekonstruktion, keine Referenzauflösung.

## Ausgewähltes Modell

Die ausführbare R3-Maschine wird übernommen:

```text
OWNER       = stiller Record-/Bildbesitzer
ACTIVE      = aktiver Posten oder Ansatz
TARGET      = gegenwärtiger Ziel-/Stationsslot
PREVIOUS    = depth-one Verweis auf einen vorigen Posten
```

Alle Werte sind recordlokale anonyme IDs. Keine ID heißt Pflanze, Wasser,
Körper, Bad, Gefäß, Leitung oder irgendein anderes Sachwort.

## Warum vier Register statt einer flüssigen Nacherzählung

Unter der vollständigen V61-Quellenedition decken persistente Registermodelle:

| Gedächtnis | vollständig rücklesbare Aussagen |
|---|---:|
| keines | 9/116 |
| nur OWNER | 27/116 |
| OWNER + ACTIVE | 88/116 |
| + PREVIOUS | 107/116 |
| + TARGET | 116/116 |

Das vierte Register wird nur durch neun zielsensitive Aussagen verlangt. Die
Zahl ist deshalb kein universelles Sprachgesetz, sondern der kleinste
ausführbare Zustand **für unsere aktuelle kreative Edition**.

## Was die Rollen wirklich leisten

- Das Bild setzt OWNER einmal; danach bleibt er still.
- Klausel- und Zellwechsel tragen oder ersetzen ACTIVE nach der V61-Karte.
- `VORIGES?` fordert den PREVIOUS-Slot an, liefert aber keinen Antezedenten.
- `ZIEL?` fordert TARGET an, liefert aber kein Ziel.
- Die übrigen V60-Mnemonics lösen Parameter-, Handlungs- oder Zustandsbedarf
  aus, ohne ihre stillen Argumente zu identifizieren.

Mit vollständigem Transition-Log sind 116/116 Schritte rückwärts lesbar; aus
dem nackten Endzustand nur 47/116. Die Maschine ist daher eine
Werkstattprozedur mit Verlaufsbuch, keine selbstgenügsame Chiffre.

## Kosten und Gegenmodell

49 irreduzible Ambiguitäten betreffen 33 Statements: mehrere mögliche
Vorbezüge, mehrere Ziele, offene Recordenden, Zwei-Anteil-Reihenfolgen und die
ungelöste V61-Grenze. Außerdem stammen konkrete Registerfüllungen weiterhin
aus dem lokalen Exemplar. Ein reines Formular-Kopiermodell kann alle sichtbaren
Formen ohne semantisches Gedächtnis erzeugen; es ist der stärkste Rivale.

## Entscheidung für V63

V63 darf OWNER/ACTIVE/TARGET/PREVIOUS als anonyme Laufzeitwerte benutzen und
fragen, ob `MASS?`, `BEREIT?`, `KLAR?`, `ANSATZ?`, `ZIEL?` und die formalen
SET/MARK/LINK-Prompts eine einheitliche Slotgrammatik bilden. Es darf daraus
keine Pronomen, Kasus, Nomen, Verbklassen oder Weltreferenten ableiten.
