# Sidequest: das kleine Lehrlings-Codebuch

## Ergebnis

Die verbliebene Auswendigschicht ist klein genug, um sie einem Schreiber auf
einem einzigen Blatt beizubringen:

- 22 exakte Ganzkarten;
- zusammen nur 28 der 381 sichtbaren Prosaereignisse;
- zusammengezogen zu 16 kurzen Werkstatt-Kopfwoertern;
- 8 Ganzkarten sind unteilbare Schlussbefehle, die jeweils nur einmal vorkommen;
- 14 offene Ganzkartentypen tragen die uebrigen 20 Vorkommen.

Das ergibt ein handhabbares Mischsystem: Der Schreiber bildet den groessten
Teil aus produktiven Kernen und schaut nur selten in eine kleine
Nomenklatorliste. Von 381 Kartenereignissen sind 332 produktiv, 21 besitzen
einen bekannten Kern mit einem lokal gelernten Traeger und 28 sind Ganzkarten.

## Die sechzehn gelernten Begriffe

| Kopfwort | exakte Karten | kurze Werkstattlesung |
|---|---|---|
| ZUSATZ | `dl` | Zusatz zum laufenden Ansatz |
| GEFAESS | `os`; `ly`; `oykchor` | allgemeines, Empfangs- oder Zubereitungsgefaess |
| KUEHLEN | `tchody`; `ody` | bezeichneten Posten kuehlen; Schluss |
| ROH | `qekey` | unbehandelter Ausgangsposten |
| TUCH | `dain` | Arbeitstuch |
| SCHWENKEN | `sshkchdy` | einmal bewegen; Schluss |
| PFLANZENTEIL | `dchey`; `sh` | Wurzel oder Staengel nach Zeichnung |
| WASCHEN | `rshedy`; `lkedy` | Waschgang oder Nachwaschen; Schluss |
| AUFTRAGEN | `cheeckhody` | bereiteten Posten auftragen; Schluss |
| FUELLEN | `ytey` | bezeichneten Empfaenger fuellen |
| KLARLAUF | `cheey|shey` | klarer Ablauf oder Klarauszug |
| TRENNEN | `cfhy`; `cphy` | auswringen oder nachseihen |
| FRISCHWASSER | `dshedy` | Frischwasser zugeben; Schluss |
| VORIGES | `dchol|schol` | vorigen aktiven Posten wiederaufnehmen |
| TEILEN | `ches` | aktuellen Posten teilen |
| BEFESTIGEN | `qokylddy` | aktuellen Posten befestigen; Schluss |

Das sind Kopfwoerter, keine behaupteten Lautwerte. Mehrere sichtbare Karten
koennen dasselbe Kopfwort mit einer gelernten Unterart realisieren. Genau das
macht das System fuer eine kleine Werkstatt plausibel: produktive Bauteile fuer
haeufige Beziehungen und ein sehr kleines Deck aus fachlichen Ganzzeichen fuer
Gegenstaende oder komplette Handgriffe.

## So lernt der Lehrling das System

Die Karten werden in drei Klassen markiert:

- `P`: voll aus bekannten Bauteilen bilden und lesen;
- `p`: bekannten Kern bilden, den lokalen Traeger aus dem Muster uebernehmen;
- `W`: exakte Ganzkarte aus der 22-Karten-Liste erkennen.

Die 116 vorhandenen Aussagen teilen sich dadurch in drei Lektionen:

- 79 Saetze bestehen nur aus produktiven Karten;
- 15 Saetze brauchen mindestens einen gebundenen Traeger, aber keine Ganzkarte;
- 22 Saetze brauchen wenigstens einen Codebuchgriff.

Ein Lehrgang kann daher mit den 79 leichten Saetzen beginnen, dann die 15
Traeger-Saetze einfuehren und zum Schluss die 16 Kopfwoerter an 16 ausgewaehlten
Diktaten ueben. Die vollstaendige Abschreibtafel behaelt die exakte sichtbare
Reihenfolge aller 381 Ereignisse bei.

## Beispiel einer Ruecklesung

Die Folge auf `f10r`, Aussage `H1-S001`, wird als

```text
dchey cthoor char chty os chair otytchol oky daiin etyd
W     P      P    P    W  P     p         P   P     P
```

unterrichtet. Der Lehrling schlaegt nur `dchey=PFLANZENTEIL/WURZEL` und
`os=GEFAESS` nach. Den Rest baut er aus dem produktiven Kasten. Die laufende
Werkstattanweisung lautet:

> Nimm die Wurzel, bereite den Ansatz, trenne daraus einen Teil ab, gib ihn in
> das Gefaess, gib den Wasserzulauf zu, fuehre den naechsten Teilposten weiter,
> setze ihn nach Sollmass an und behalte einen kleinen Restteil.

Das ist erheblich lernbarer als ein Woerterbuch mit 173 unabhaengigen Woertern:
Nur 16 Bedeutungskoepfe muessen wirklich auswendig gelernt werden.

## Arbeitsentscheidung

Die beste aktuelle Schreiberhypothese ist deshalb:

```text
produktive Fachkuerzel
+ gebundene lokale Traeger
+ 16 gelernte Nomenklator-Kopfwoerter auf 22 exakten Karten
+ Bildbesitzer fuer den konkreten Gegenstand
```

Die Ganzkarten sind nicht der Haupttext, sondern die kleine Fachwortschicht des
Systems. Das Bild sagt, *welcher* Gegenstand gemeint ist; die produktive
Grammatik sagt, was mit ihm geschieht; das Codebuch liefert seltene Dinge wie
Tuch, Gefaess, Klarlauf oder einen kompletten Wasch-/Befestigungsbefehl.

## Artefakte

- `APPRENTICE_ONE_PAGE_MANUAL.md`: einseitige Lehrregel;
- `WHOLE_HEADWORD_16.tsv`: die sechzehn Kopfwoerter;
- `WHOLE_CARD_22_CODEBOOK.tsv`: alle exakten Ganzkarten und Vorkommen;
- `COPYBOOK_116_STATEMENTS.tsv`: vollstaendige P/p/W-Abschreibtafel;
- `APPRENTICE_16_EXERCISES.tsv`: je eine Uebung pro Kopfwort;
- `build_apprentice_codebook.py`: reproduzierbarer Bau;
- `validate_apprentice_codebook.py` und `VALIDATION.json`: Konsistenzpruefung.

Die Runde verwendet nur die festen sieben Prosaseiten. Die Astro-Tafeln bleiben
unveraendert und getrennt; die versiegelten Seiten wurden nicht benutzt.
