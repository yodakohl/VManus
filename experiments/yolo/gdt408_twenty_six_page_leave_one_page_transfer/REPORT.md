# GDT408 – Jede Seite gegen die übrigen 25

## Ergebnis

`TWENTY_SIX_OF_TWENTY_SIX_PAGE_FACTOR_REPLAY_COMPLETE`.

Alle 24 laufenden Seiten bestehen den Auslass als faktorisierte
Werkstattkonstruktion; `f69v` und `f70v` bestehen separat als reine lokale
Register. Es gibt keinen seitenprivaten portablen Kern und keinen
seitenprivaten Scope-Faktor.

## Laufende 4.576 Ereignisse

| Übertragungsstufe | Ereignisse |
|---|---:|
| identische Oberfläche auf anderer Seite | 3.402 |
| identisches Rezept unter anderer Oberfläche | 284 |
| alle benachbarten Pakete auf anderen Seiten | 755 |
| bekannte Atome in neuer Paketfolge | 129 |
| einzelne bekannte Atome ohne innere Grenze | 4 |
| alter lokaler Kanal, nur auf dieser Seite | 2 |
| seitenprivater portabler Kern | **0** |

Damit übertragen 3.686/4.576 Ereignisse direkt als Oberfläche oder komplettes
Rezept. Weitere 755 werden aus anderswo belegten Nachbarpaketen gebaut. Nur
135 Ereignisse brauchen die schwächste erlaubte Kompositionsstufe; zwei davon
sind die schon vorher als lokal klassifizierten Zeichen `RESUME_CARD` auf
`f56r` und `LOCAL_CHAR_J` auf `f88r`.

Diese beiden sind kein nachträglicher Rettungstrick: GDT405 hatte beide vor
diesem Lauf als `LOCAL_OR_CLASS_SIGN` gesperrt. Sie dürfen nicht als portable
Wörter gezählt werden und dürfen zugleich keinen portablen Kern zum Scheitern
bringen.

## Alle 5.051 Scope-Bindungen

| Replay | Bindungen |
|---|---:|
| komplette gleiche Faktorsignatur auf anderer Seite | 5.003 |
| neue Kombination ausschließlich alter Faktorwerte | 48 |
| seitenprivater Faktorwert | **0** |

Damit bleibt auch der Parser nicht nur „global bekannt“: 99,05 % der Bindungen
haben ihre komplette Selector–Geometrie–Kopf–R–Doppelungs-Signatur bereits auf
einer anderen Seite.

## Die lokalen 693 Gruppen

- 238 haben dieselbe lokale Oberfläche auf einer anderen Seite;
- 158 haben wenigstens dieselbe lokale Rezeptform;
- 297 bleiben echte seitenprivate Bild-/Stationsnamen.

Das ist erwarteter Nomenklatorrest, keine Prosa-Niederlage. Besonders `f69v`
und `f70v` bleiben lokale Himmelsregister und bekommen keine erfundenen Sätze.

## Schwierige, aber bestandene Seiten

Die niedrigsten direkten Oberflächenanteile liegen auf `f17r`, `f24v` und
`f67r2`; gerade dort übernimmt die sichtbare Paketkomposition. Auch die vier
zufällig aufgenommenen Seiten bestehen: keine braucht einen neuen portablen
Kern oder Parserfaktor.

## Ehrliche Grenze

Dieser Test ist ein deutlicher Gewinn für **Komposition und Durchsatz**. Er ist
noch kein Beweis, dass `CH=NEHMEN`, `AIIN=WERT` oder ein anderer deutscher
Arbeitswert stimmt. Er zeigt enger: Wenn diese 19 portablen Werte als
Werkstattpseudonyme benutzt werden, muss keine Seite einen eigenen zusätzlichen
portablen Wert erfinden. Der nächste sinnvolle Angriff gilt deshalb nicht mehr
der Parserform, sondern der Bedeutungsdrift jedes einzelnen Kernwerts über alle
26 Seiten.
