# Werkstattlehre: Quelle – Weg – Ziel

Status: kreative Zehn-Seiten-Arbeitstheorie, keine Entzifferung. Diese Runde
verwendet ausschließlich das aktuelle komponentenkomplette Wörterbuch,
Interlinear und Aussagenregister. Sie baut keine wissenschaftliche Prüfung,
sondern eine von mehreren Schreibern leicht zu lernende Werkstattregel.
`f84` und `f84r` blieben versiegelt.

## Die Fünferregel

Ein Lehrmeister um 1420 müsste nur fünf Ortszeichen lehren:

```text
AR    QUELLE     von / aus der Herkunft
AIR   WEG        durch / längs des Laufs
AL    ZIEL       an / zu der Arbeitsstelle
P-    HINEIN     in den Empfänger
L-    HINAUS     aus dem Behälter oder von der Stelle weg
```

`P-` und `L-` sind nur vor `CHED` produktiv. Sie werden nicht als allgemeine
Wörter für hinein und hinaus behauptet. `AR`, `AIR` und `AL` sind drei
gelernte Werkstattkürzel; `AIR` wird nicht in `A+I+R` zerlegt.

Die räumliche Leserichtung lautet:

```text
QUELLE  -- über WEG -->  ZIEL
 AR           AIR         AL

L + CHED = hinausführen       P + CHED = hineinführen
```

Damit kann ein Schreiber die längeren Karten ohne neue Satzglossen bilden:

```text
L+CHED+AR   aus der Quelle hinausführen
L+CHED+AL   zur Auslassstelle hinausführen
P+CHED+AL   in die Ziel-/Empfangsstelle hineinführen
P+CHED+DY   in den Empfänger hineinführen; Schritt schließen
CHED+AIR    den Posten durch den Lauf führen
OK+AR       etwas daraus in den Arbeitsgang nehmen
OK+AIR      den Lauf in Gang setzen
OK+AL       etwas an der Zielstelle einsetzen
```

## Umfang

Das vollständige gerichtete Inventar umfasst **23 exakte Kartentypen und 50
Ereignisse**. Darin sind alle aktuellen `AR`, `AIR`, `AL`, `OK+AR/AIR/AL`,
`L+CHED+AR/AL`, `P+CHED+AL/DY` sowie die für die Richtung entscheidenden
Minimalpaare `L+CHED` und `L+CHED+DY` enthalten.

Komponenten können sich in einem Kartentyp überlagern:

- `AR`: 6 Typen, 10 Ereignisse;
- `AIR`: 4 Typen, 4 Ereignisse;
- `AL`: 10 Typen, 26 Ereignisse;
- `L+CHED`: 4 Typen, 11 Ereignisse;
- `P+CHED`: 2 Typen, 2 Ereignisse.

Die maschinenlesbare Vollzählung mit jedem Ereignis und jeder Aussage steht in
`WORKSHOP_DIRECTION_PARADIGM.tsv`.

## Warum diese Bedeutungen zusammenpassen

### `AR` ist Quelle, nicht Höhe

Die Grundkarte `char|dar|sar` kommt fünfmal als „daraus/von dort“ vor.
`otar` fügt lediglich „danach“ hinzu, `qokar` nimmt das Herkunftsgut in den
Arbeitsgang, und `lchedar` führt es aus der Quelle hinaus. Der alte Einzelwert
„über der Stelle“ für `qokar` passt nicht in diese Reihe.

`skar` liefert die wichtigste Korrektur auf Ereignisebene: Sein Kartenwert
bleibt „erwärmtes Wasser/Medium ausgießen“. Die frühere lokale Ausführung
„einfüllen“ kehrte die sichtbare AR-Richtung um und wird gestrichen.

### `AIR` ist Weg, nicht automatisch Wasser

`chair`, `kair`, `okair` und `schedair` teilen keinen sicheren Stoff, wohl aber
einen Lauf:

```text
chair       Zulauf
kair        Rücklauf
okair       Lauf in Gang setzen
schedair    durch den Lauf führen
```

Darum ist der kleinste gemeinsame Beitrag `AIR = Laufweg`. Wasser kann in der
lokalen Ausführung von `chair` oder `kair` stehen, ist aber nicht das
Werkstattkürzel selbst. Ebenso wird aus `schedair` nicht mehr gleichzeitig
„führen oder abziehen“: Die Richtung kommt nur von `P/L/AR/AL`; AIR nennt den
Weg.

### `AL` ist Ziel, nicht automatisch unten oder Ablauf

Die exakte AL-Grundkarte erscheint zehnmal als `al|chal|cheal|dal|sal|tal`.
Ihre kleinste Anweisung ist „an der Zielstelle“. Die längeren Karten werden
dadurch regelmäßig:

```text
OK+AL        an der Zielstelle einsetzen
OK+AL+Y      den laufenden Posten an der Zielstelle einsetzen
OK+EE+AL     an der Zielstelle länger in Kontakt halten
CHD+AL       an der Zielstelle umsetzen
OT+AL        danach zur Zielstelle
```

`otal|qotal` verliert deshalb den eingebauten „Ablauf“. Ein Ablauf kann lokal
die Zielstelle sein, aber `AL` bedeutet weder unten noch Auslass. In
`olsaly = untere Zielstelle` und `ldalor = bezeichnete Zielstelle` kommt die
zusätzliche Bestimmung aus der gelernten Gesamtkarte.

### `P` und `L` bilden das einfache Richtungspaar

Das stärkste Lehrpaar ist:

```text
lchedal   Auslassstelle       pchedal   Einfüllstelle
lchedy    hinaus; Schluss     pchedy    hinein; Schluss
```

Die acht `lchedy`-Ereignisse machen `L = hinaus/weg` zum robustesten
Richtungszeichen der Runde. `lched` ist dieselbe Bewegung ohne sichtbaren
Abschluss. Die zwei P-Belege sind dünner, aber exakt entgegengesetzt lesbar.

## Nahe Minimalpaare

| Paar | ausgewählter Unterschied | verworfene Gegenidee |
|---|---|---|
| `char` / `chair` | `AR = aus Quelle`; `AIR = über Laufweg` | `AIR` bloß als längeres Wasserwort |
| `qokar` / `qokal` | aus der Quelle nehmen / am Ziel einsetzen | AR als „über“, AL als „unter“ |
| `lchedar` / `lchedal` | aus Quelle hinaus / zur Auslassstelle hinaus | AR und AL als austauschbare Ortsendung |
| `otar` / `otal` | danach aus / danach zum Ziel | beide als festes „Ablassen“ |
| `lchedal` / `pchedal` | Auslassstelle / Einfüllstelle | P und L als bedeutungslose Hüllen |
| `lchedy` / `pchedy` | hinaus und schließen / hinein und schließen | beide allgemein „transferieren“ |
| `qokal` / `okair` | Ziel aktivieren / Weg aktivieren | beide allgemein „Wasser öffnen“ |

## Konkrete Kartenwerte

Die neue Lehre ändert keine Kartenidentität. Sie kürzt oder präzisiert nur die
Defaults:

| exakte Karte | ausgewählter Default |
|---|---|
| `char|dar|sar` | daraus; von der Quelle |
| `cheoar` | klaren Auszug daraus entnehmen |
| `skar` | erwärmtes Wasser oder Medium ausgießen |
| `otar` | danach auslassen oder entnehmen |
| `qokar` | daraus in den Arbeitsgang nehmen |
| `lchedar` | aus der Quelle hinausführen |
| `chair` | Zulauf |
| `kair` | Rücklauf |
| `okair` | den Lauf in Gang setzen |
| `schedair` | den Posten durch den Lauf führen |
| `al|chal|cheal|dal|sal|tal` | an der Zielstelle |
| `ldalor` | bezeichnete Zielstelle |
| `olsaly` | untere Zielstelle |
| `otal|qotal` | danach zur Zielstelle |
| `okal|qokal` | an der Zielstelle einsetzen |
| `qokaly` | den laufenden Posten an der Zielstelle einsetzen |
| `qokeedal` | an der Zielstelle anhaltend in Kontakt halten |
| `chdal` | an der Zielstelle umsetzen |
| `lchedal` | Auslassstelle |
| `pchedal` | Einfüllstelle |
| `lched` | hinausführen |
| `lchedy` | hinausführen; Schluss |
| `pchedy` | hineinführen; Schluss |

## Alle 36 berührten Aussagen

Die folgende Liste gibt für jede Aussage sämtliche gerichteten Ereignisse und
die einzusetzende neue Kurzlesung an. Nicht genannte Karten der Aussage bleiben
unverändert.

| Aussage | Ereignisse | gerichtete Kurzlesung |
|---|---|---|
| `H1-S001` | E003 `char`; E006 `chair` | daraus; Zulauf |
| `H2-S002` | E031 `dar` | daraus |
| `H4-S003` | E065 `cheoar` | klaren Auszug daraus entnehmen |
| `H4-S004` | E069 `okal` | an der Zielstelle einsetzen |
| `H5-S001` | E082 `dal` | an der Zielstelle |
| `B1-S002` | E103 `kair`; E104 `okal`; E105 `sar`; E109 `al`; E117 `qokeedal` | Rücklauf; am Ziel einsetzen; daraus; Zielstelle; am Ziel anhaltend in Kontakt halten |
| `B1-S014` | E147 `lchedal`; E149 `otar` | Auslassstelle; danach auslassen |
| `B1-S016` | E152 `qokal` | an der Zielstelle einsetzen |
| `B1-S017` | E156 `sal` | an der Zielstelle |
| `B1-S021` | E166 `chal` | an der Zielstelle |
| `B2-S004` | E172 `qokal`; E174 `lched` | am Ziel einsetzen; hinausführen |
| `B2-S005` | E177 `qokaly` | laufenden Posten am Ziel einsetzen |
| `B2-S006` | E186 `qokal` | an der Zielstelle einsetzen |
| `B2-S008` | E191 `qokar` | daraus in den Arbeitsgang nehmen |
| `B2-S011` | E199 `char` | daraus |
| `B2-S013` | E210 `lchedy` | hinausführen; Schluss |
| `B2-S016` | E214 `cheal`; E215 `lchedar`; E221 `pchedy` | an der Zielstelle; aus der Quelle hinausführen; in den Empfänger hineinführen und schließen |
| `B3-S002` | E230 `qotal` | danach zur Zielstelle |
| `B3-S003` | E235 `lchedy` | hinausführen; Schluss |
| `B3-S004` | E237 `qotal`; E238 `dar` | danach zur Zielstelle; daraus |
| `B3-S006` | E241 `qokal` | an der Zielstelle einsetzen |
| `B3-S008` | E246 `lchedy` | hinausführen; Schluss |
| `B3-S010` | E248 `pchedal` | Einfüllstelle |
| `B3-S014` | E260 `okair` | den Lauf in Gang setzen |
| `B3-S015` | E262 `lchedy` | hinausführen; Schluss |
| `B3-S020` | E268 `dal`; E269 `lchedy` | an der Zielstelle; hinausführen und schließen |
| `B3-S021` | E272 `dal`; E278 `tal` | jeweils an der Zielstelle |
| `B3-S023` | E282 `lchedy` | hinausführen; Schluss |
| `B3-S030` | E300 `schedair` | den Posten durch den Lauf führen |
| `B3-S034` | E313 `olsaly` | untere Zielstelle |
| `B4-S003` | E320 `otal` | danach zur Zielstelle |
| `B4-S012` | E345 `lchedy` | hinausführen; Schluss |
| `B4-S015` | E357 `lchedy` | hinausführen; Schluss |
| `B4-S016` | E359 `dal`; E360 `skar` | an der Zielstelle; erwärmtes Medium ausgießen |
| `B5-S003` | E365 `dal`; E368 `chdal` | an der Zielstelle; dort umsetzen |
| `B6-S001` | E381 `ldalor` | bezeichnete Zielstelle |

## Lehrmeisterurteil

```text
SELECT__AR_SOURCE__AIR_PATH__AL_TARGET__P_IN__L_OUT
```

Das ist einfacher als das vorige Gemisch aus Quelle, Wasser, Rückstrom,
Ablauf, oberer Stelle und beliebigem Transfer: Jeder räumliche Baustein hat
jetzt genau eine Aufgabe. Konkrete Stoffe, Gefäße und Anwendungen dürfen die
lokale Übersetzung ergänzen, aber nicht den Stammwert umdrehen.
