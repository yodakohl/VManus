# GDT407 – Eine echte gemeinsame 26-Seiten-Ausgabe

## Ergebnis

`UNIFIED_TWENTY_SIX_PAGE_EDITION_COMPLETE`.

Die aktuelle Arbeitsbasis war bisher über mehrere Passes verteilt und nur in
Summen zusammengezählt. Sie liegt jetzt erstmals als eine einzige, durchgehend
verlinkte Ausgabe vor:

| Ebene | Zahl |
|---|---:|
| physische Seiten | 26 |
| sichtbare Gruppen | 5.269 |
| laufende Ereignisse | 4.576 |
| lokale Adressen/Marker | 693 |
| Aussagen | 715 |
| Fokusbindungen | 5.051 |

Alle alten und neuen IDs bleiben neben den globalen GDT407-IDs erhalten. Jede
Fokusbindung zeigt auf ein vorhandenes Ereignis oder ausdrücklich auf den
sichtbaren Besitzer. Kein Besitzer- oder Aussagegrenzsprung und kein Vorgriff
über mehr als eine Karte wurde beim Zusammenbau eingeführt.

## Wichtige Bereinigung

„26 Seiten“ und „24 laufende Prosaseiten“ sind keine widersprüchlichen Zahlen.
`f69v` und `f70v` bleiben reine lokale Himmelsregister. Außerdem tragen mehrere
andere Seiten einzelne Bild- oder Abschnittsmarker neben laufendem Text. Daher:

- 4.576 Ereignisse bilden die 715 laufenden Aussagen;
- 693 Gruppen werden nur als lokale Adressen oder Marker kopiert;
- zusammen ergeben sie 5.269 sichtbare Gruppen.

Die lokalen 693 Gruppen werden nie nachträglich als Prosa behandelt.

## Was sich nicht geändert hat

- kein Kernwert;
- kein Oberflächenrezept;
- keine Aussagegrenze;
- kein Besitzer;
- kein Scope-Selector oder Handlungskopf;
- keine neue Seite und kein neues Bild.

Die vollständige lesbare Fassung steht in
`TWENTY_SIX_PAGE_READABLE_CORE_EDITION.md`; die maschinenlesbaren Ebenen liegen
separat unter `artifacts/`. Der Doppelbuild ist byte-identisch und alle
Integritätsprüfungen bestehen.

## Nächster Nutzen

Diese Ausgabe macht den entscheidenden Test möglich: Jede der 26 Seiten kann
nun vollständig ausgeblendet und ausschließlich gegen die übrigen 25 geprüft
werden. Damit wird sichtbar, welche Rezepte wirklich portabel sind und welche
nur auf ihrer eigenen Seite plausibel gemacht wurden.
