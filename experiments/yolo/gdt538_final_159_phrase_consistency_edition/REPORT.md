# GDT538 — alle 159 Endkarten haben jetzt eine wirkliche Kurzlesung

Status: `PASS_ALL_159_HAVE_CANONICAL_PHRASES__Y_RESTORED_AS_ARGUMENT`

## Ergebnis

Die Lücke war größer als die sichtbaren sieben Sonderkarten vermuten ließen:
152/159 Einträge des finalen GDT537-Lesers enthielten im Kurzphrasenfeld nur
`INHERITED`. GDT538 ersetzt alle 152 Platzhalter. Jetzt besitzen 159/159
Oberflächen eine konkrete deutsche Werkstattfassung und zusätzlich eine exakt
geordnete Lesekette.

Die 159 Rezepte sind sämtlich verschieden. „Gleiches Rezept, andere Phrase“
war daher auf dieser Oberfläche kein testbarer Konflikt. Die richtige
Konsistenzebene sind die Bausteine: 640 Slots aus 34 Typen werden überall mit
derselben Realisierung ausgesprochen. Neunzehn Wortwerte bleiben ungeklammert;
fünfzehn Grad-, Steuer-, Adress-, Zeichen- und lokale Kerntypen bleiben in
eckigen Klammern und werden nicht heimlich zu Wörtern.

Beispiele:

```text
chekchy   CH+K+Y           nehmen → geben → Posten
           Den Posten nehmen und geben.

alkey     AL+K+E+Y         Zielort → geben → [Grad I] → Posten
           Am Zielort; den Posten geben; auf Grad I.

chxar     CH+LOCAL_X+AR    nehmen → [lokaler X-Zeichen-/Namenskern] → Ausgang
           Nehmen; mit lokalem X-Zeichen-/Namenskern; vom Ausgang.
```

## Eine kleine, aber wichtige Korrektur

Vier handgeschriebene Sonderphrasen hatten `Y=POSTEN` als deutsches Verb
„posten“ verwendet: `aiicthy`, `chekchy`, `dairykodas` und `dalcheeeky`.
Unser gemeinsames Modell führt Y jedoch durchgehend als Argumentslot. Die neue
Ausgabe stellt deshalb „Posten“ wieder als Nomen dar. Zum Beispiel wird
`chekchy` nicht mehr „Nehmen, geben und posten“, sondern **„Den Posten nehmen
und geben.“**

Das ist keine Umdeutung von Y und keine Rezeptänderung. Es beseitigt eine
redaktionelle Rollenvermischung, die nur in diesen vier freien Formulierungen
entstanden war. Die exakt geordnete Kette bleibt bei `aiicthy` bewusst:

```text
Wert → nehmen → einstellen → Posten
```

Die glatte Fassung lautet: **„Den Wert und den Posten nehmen und einstellen.“**

## Konsistenz und Leser

Acht kleine Satzmuster decken alle 159 Karten. Unter den aktuellen Rezepten
liegen 62 Ein-Atom-Nachbarpaare; bei allen 62 bleibt jeder unveränderte Slot
gleich und genau der eingefügte, gelöschte oder ersetzte Slot bekommt einen
anderen Ausdruck. Wiederholungen bleiben als „zweimal“ oder „erneut“ sichtbar.

Der neue Leser gibt zuerst GDT538s Phrase aus, behält GDT537s Endrezept und
delegiert lokale, alte und unbekannte Oberflächen weiterhin an die vorhandenen
rollenbewussten Leser. Der unabhängige Validator besteht 51/51 Prüfungen.

## Nächster Schritt

Die Wortebene ist jetzt vollständig aussprechbar. Die genaue Rückbindung teilt
die 168 Vorkommen in **149 Prosakarten über 49 der 78 Aussagen** und **19 lokale
Rand-/Kennkarten**. Als Nächstes werden nur die 149 Prosavorkommen in ihre
Aussagen eingesetzt; die 19 lokalen bleiben im lokalen Deck. Dort lässt sich
prüfen, wo ein Kartenfragment sein Verb oder Argument aus dem laufenden Satz
erbt. Seiten, Rezepte und Stammwerte bleiben unverändert.
