# Pass 1022 — Der kleine Klammerstapel

> **Integrationshinweis:** Diese Tabelle ist das vollständige beschreibende
> Anschlussinventar ohne Vorgriff über eine Kartengrenze. Der anschließende
> manuelle Bildcheck zeigt, dass diese harte Sperre an f67r2 S032/S041
> scheitert. Die ausgewählte Pass-1022-Regel erlaubt deshalb einen **kurzen
> Vorgriff innerhalb desselben Besitzersegments** und bewahrt die 146
> Besitzer-versus-Nächstkopf-Fälle als sichtbare Alternativen. Die Zählung hier
> bleibt das unveränderte Vergleichsinventar.

## Ergebnis

Die 3.888 laufenden Karten enthalten 4.345 Vorkommen der elf verlangten
Argument-, Grad- und Beziehungskerne. Für jedes Vorkommen steht nun fest,
welche Handlung links und rechts in derselben Karte sichtbar ist, was die
vorige Karte trägt, welcher ältere Handlungskopf noch offen ist und wann nur
der Bildbesitzer bleibt.

Die kleinste brauchbare Lehrlingsregel lautet:

```text
BESITZER ist der Boden des Stapels.

HANDLUNG öffnet den laufenden Rahmen.
Y / AIIN / AIN / OR / E / EE / EEE / AL / AR / AIR
    schließen zuerst an die nächste Handlung links an.
L
    öffnet vorwärts und schließt zuerst an die nächste Handlung rechts an.

Fehlt der bevorzugte Kopf in derselben Karte:
    nimm den Kopf auf der anderen Seite;
    sonst den Kopf der unmittelbar vorigen Karte;
    sonst den letzten älteren Kopf derselben Aussage;
    sonst den sichtbaren Besitzer.

Am Aussagenanfang wird der Stapel geleert.
```

`O=AUSFÜHRUNG`, `OT=DANACH` und `OL=FORTSETZEN` öffnen dabei keinen neuen
Handlungskopf. Sie führen den vorhandenen Gang aus oder weiter. Bei mehreren
Handlungen in derselben Karte bekommt der nächste Kopf den Kern unmittelbar;
die ältere Handlung enthält dann die jüngere Handlungsgruppe. So braucht
`CH+K+Y` keine Sonderregel: `CH[ K[Y] ]`.

## Vollständige Verteilung

| Bindungsort | Vorkommen | Lesung |
|---|---:|---|
| Handlung links in derselben Karte | 2.828 | gewöhnlicher Nachsatz |
| Handlung rechts in derselben Karte | 272 | Vorrahmen oder vorangestellter Kern |
| Handlung der unmittelbar vorigen Karte | 643 | unmittelbare Kartenfortsetzung |
| ältere Handlung derselben Aussage | 353 | geerbter offener Rahmen |
| nur sichtbarer Besitzer | 249 | unterster Stapelrahmen |
| **Summe** | **4.345** | vollständig inventarisiert |

Damit hängen 4.096 Vorkommen an einem ausdrücklichen Handlungskopf. Die 249
Besitzerfälle sind keine verlorenen Karten: Dort ist innerhalb derselben
Aussage rückwärts schlicht kein Kopf offen. `AIIN=WERT` und `AIN=ANTEIL`
stehen innerhalb einer Karte nie vor einem rechten Kopf; ihre Kartenbindung
ist daher besonders schlicht. `L=VERBINDUNG` zeigt erwartungsgemäß die andere
Richtung: 122 seiner 238 Vorkommen greifen in derselben Karte nach rechts.

Die Einzelzahlen je Kern stehen in `SCOPE_STACK_SUMMARY.tsv`; sämtliche 4.345
Kanten mit den ungewählten Kandidaten stehen in
`SCOPE_STACK_ATTACHMENTS.tsv`.

## Die drei echten Restambiguitäten

Die Lehrregel liefert auch an diesen Stellen eine einheitliche Werkstattlektüre.
Die Kartenform allein lässt aber jeweils noch eine zweite Klammerung zu. Alle
329 Alternativzeilen zu 328 betroffenen Fokusvorkommen stehen vollständig in
`SCOPE_STACK_AMBIGUITIES.tsv`; eine Stelle trägt zwei Arten zugleich.

### 1. Zwei gleich nahe Köpfe — 120 Vorkommen

Ein Kern steht genau zwischen zwei Handlungsköpfen. Nachsatzkerne gehen nach
links, `L` als Vorrahmen nach rechts. Beispiel:

```text
f17r  P1003-E0049  CH + E + T + E + LOCAL_CHAR_G
                     ^   ^
Regel:              CH[E]  und anschließend T[E ...]
Alternative:        das erste E könnte bereits T bestimmen
```

Die Richtungsregel ist leicht zu lernen, doch die Gleichnähe bleibt als echte
örtliche Klammeralternative sichtbar.

### 2. Besitzer oder Kopf der nächsten Karte — 146 Vorkommen

Hier fehlt jeder örtliche oder geerbte Kopf, aber die nächste Karte eröffnet
eine Handlung. Die Kurzregel greift nicht vorwärts über eine Kartengrenze und
bindet an den Besitzer. Beispiel:

```text
f17r  P1003-E0016  D_ADDR + OR  |  nächste Karte: CH + ...
Regel:              BESITZER[EINHEIT]
Alternative:        CH könnte die vorangestellte EINHEIT aufnehmen
```

Das ist die wichtigste noch offene Kartenfrage. Sie betrifft 119 Karten, weil
manche Karten zwei der verlangten Kerne tragen.

### 3. `R` als Kopf oder Schwanz — 63 Vorkommen

`R` ist bereits als `MARK_HEAD_OR_TAIL` geführt. Wenn ein verlangter Kern an
ein solches `R` anschließt und ein älterer Kopf vorhanden ist, bleiben zwei
Lesungen möglich. Beispiel:

```text
f18r  P1008-E0001  P + D_ADDR + R + AIR + DY
Regel:              P[ R[AIR] ]
Alternative:        P[ ... R ] und AIR weiterhin unter P
```

Die 63 Fokusvorkommen gehen auf 42 verschiedene `R`-Karten zurück. Bis der
örtliche Text entscheidet, wird `R` vor einem rechten Fokus als Kopf gelesen;
die Schwanzlesung bleibt ausdrücklich erhalten.

## Grad und Beziehungen benutzen denselben Stapel

Es ist keine zweite Grammatik nötig:

- `E / EE / EEE` schließen wie Nachsätze an die nächste Handlung links an;
  ohne linken Kopf benutzen sie denselben Rechts-, Vorige-Karte-, Erb- und
  Besitzerweg.
- `AL / AR / AIR` schließen ebenfalls nach links; sie behalten nur ihre Werte
  ZIELORT, AUSGANG und LAUF.
- `L` ist der einzige der verlangten Kerne mit bevorzugtem Rechtsgriff, weil
  VERBINDUNG den eingeschlossenen oder folgenden Gang eröffnet.

Damit erhalten WERT, ANTEIL, EINHEIT, AKTIVER POSTEN, Grade und Beziehungen
dieselbe mechanische Reichweite, ohne eine neue Bedeutung einzuführen.

## Verdoppelte Kerne

Die sieben Karten mit unmittelbar verdoppeltem Fokus übernehmen unverändert
die vorige Zweigregel:

- `OK+OR+OR+Y` auf f13r ist ein Paketabstieg;
- zweimal `P+AR+AR`, zweimal `AL+AL` und zweimal `Y+Y` sind freie Paare.

Für f13r ergibt der Stapel deshalb ausdrücklich:

```text
OK [ OR_außen [ OR_innen [ Y ] ] ]
SETZEN [ äußere EINHEIT [ innere EINHEIT [ AKTIVER POSTEN ] ] ]
```

Beide `OR` hängen am selben gesetzten Kartenrahmen, tragen aber die Rollen
`PACKAGE_OUTER` und `PACKAGE_INNER`. Die zwölf Atome der freien Doppelungen
stehen dagegen als `FREE_PEER_1` und `FREE_PEER_2` gleichrangig. Dadurch wird
weder ein zweites Lexem erfunden noch eines der geschriebenen Zeichen
verschluckt.

## Was der Stapel jetzt leistet

Ein Lehrling braucht nur einen Besitzerrahmen, einen laufenden Handlungskopf,
eine bevorzugte Richtung für Nachsatz gegen `L` und den Rückgriff über frühere
Karten. Das deckt jedes verlangte Vorkommen ab. Die 328 offenen Stellen sind
nicht versteckt: Sie sind mit beiden Klammerungen, Karte, Aussage, Besitzer
und Regelentscheidung einzeln nachschlagbar.

Dateien:

- `SCOPE_STACK_ATTACHMENTS.tsv` — 4.345 vollständige Vorkommenszeilen
- `SCOPE_STACK_AMBIGUITIES.tsv` — alle 329 echten Alternativzeilen
- `SCOPE_STACK_SUMMARY.tsv` — Kern-für-Kern-Verteilung
- `SCOPE_STACK_SUMMARY.json` — kompakte Zählung und Anschlussprüfungen
- `SCOPE_STACK_BUILD.py` — der kleine Stapelbauer
