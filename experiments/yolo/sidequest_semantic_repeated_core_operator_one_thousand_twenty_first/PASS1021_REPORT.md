# Pass 1021 — Was zwei gleiche Kerne bedeuten

## Ergebnis

In allen 3.888 laufenden Karten gibt es nur 40 unmittelbare Doppelkerne. Sie
stehen in 38 Aussagen auf 16 Seiten; keine Karte enthält eine Dreifachform.

Ein einziger universeller Wert wäre verführerisch, aber zu grob. Die 40 Fälle
teilen sich sauber in zwei Werkstattregeln:

```text
PAKETGRENZE:  X + X + Z  -> äußeres X [inneres X [Z]]
FREI:         X + X      -> zwei X bei Dingen / X nochmals bei Handlungen
```

Beide Regeln lesen jeden Kern zweimal und geben ihm keinen neuen Wert.

## Regel 1 — Paketgrenze und Stufenabstieg

28 Fälle gehören hierher:

- 27× `CH+CH`, fast immer vor `T`, `K`, `P` oder `S`;
- 1× `OR+OR` zwischen `OK` und `Y`.

Die `CH`-Doppelungen entstehen regelmäßig, wenn ein äußerer `CH`-Rahmen und
eine geöffnete Form wie `C<T>H`, `C<K>H` oder `C<P>H` zusammentreffen. Das
erste `CH=NEHMEN` gilt dem äußeren Besitzer, das zweite der aktiven
Untereinheit; erst danach folgt Einstellen, Geben, Einsetzen oder Wählen.

Das ist keine geheimnisvolle Verdopplungsbedeutung. Es ist die sichtbare
Folge zweier gleichartiger Ebenen.

## Regel 2 — freie Mehrzahl oder Wiederholung

Die übrigen zwölf Fälle enden frei oder stehen als gleichrangige Köpfe:

- `OL+OL` 5× — fortsetzen und nochmals fortsetzen;
- `AR+AR` 2× — zwei lokale Ausgänge;
- `AL+AL` 2× — zwei lokale Zielorte;
- `Y+Y` 2× — zwei gesetzte oder aufeinander bezogene Posten;
- `OK+OK` 1× — setzen und nochmals setzen.

Bei Dingen klingt die deutsche Expansion pluralisch, bei Handlungen iterativ.
Das Bild oder Register entscheidet, welche zwei Posten, Ziele oder Gänge
gemeint sind. Ein zweites Kernlexem ist nicht nötig.

## Warum nicht alles Verschachtelung ist

Die erste technische Kandidatur wollte alle 40 Fälle als äußeren/inneren
Doppelrahmen lesen. Das trägt `CH+CH` und `OR+OR` gut, aber ein freies
`dalal = AL+AL` oder `ychey = Y+Y` hat rechts keine innere Ergänzung, die einen
Stufenabstieg sichtbar macht. Dort ist „zwei Ziele/Posten“ die einfachere
Lehrregel. Umgekehrt wäre bloße Wiederholung für `CH+CH+T/K/P` zu flach, weil
die Doppelung gerade an einer geöffneten Paketgrenze entsteht.

Die Zweiteilung ist deshalb nicht ein Kompromiss, sondern folgt der graphischen
Stellung.

## f13r, P1009-S009

Die letzte Karte des Pflanzenartikels ist:

```text
okorory = OK + OR + OR + Y
          SETZEN + EINHEIT + EINHEIT + AKTIVER POSTEN
```

Sie gehört zu Regel 1, weil die beiden Einheiten zwischen Handlungskopf und
Referent stehen:

```text
SETZEN [äußere EINHEIT [innere EINHEIT [AKTIVER POSTEN]]]
```

Mit dem sichtbaren Pflanzenbesitzer lautet das Ende nun:

> Danach den nächsten sichtbaren Pflanzenteil wählen und geben; ihn als
> Untereinheit in den laufenden Pflanzenartikel setzen. Offen weiterführen.

`OR` heißt dabei zweimal EINHEIT. *Pflanzenartikel* und *Pflanzenteil* kommen
von äußerem und innerem Bildbesitzer, nicht aus zwei neuen OR-Wörtern.

## Historische Werkstattnähe

Zeitnahe Praktiken erlauben beide Mechanismen: verdoppelte Sigla können einen
Plural markieren, wiederholte Notenzeichen dieselbe Ausführung nochmals, und
frühitalienische Abakusschrift kann dasselbe Kürzel als äußere und innere Größe
schachteln. Das rechtfertigt keine Identifizierung des Voynich-Systems, zeigt
aber, dass ein Lehrling um 1420 beide einfachen Regeln verstehen konnte.

## Arbeitsentscheidung

Das Lehrmeisterblatt erhält eine elfte Öffnungsregel mit zwei Zweigen:

> Öffnet eine lange Form zwei gleiche Kerne vor einer inneren Ergänzung, lies
> äußere und innere Ebene. Stehen die beiden Kerne frei, lies beide als mehrere
> Dinge oder wiederholte Handlung. Lösche den zweiten Kern nie als bloßes
> Ditto und erfinde kein neues Doppelwort.

## Dateien

- `REPEATED_CORE_OCCURRENCES.tsv` — vollständige 40-Kontext-Inventur
- `REPEATED_CORE_PATTERN_SUMMARY.tsv` — sieben betroffene Kerne
- `REPEATED_CORE_REPORT.md` — technische Ein-Regel-Kandidatur
- `HISTORICAL_DOUBLING_WORKSHOP_NOTE.md` — historische Zwei-Regel-Ableitung
- `PASS1021_ADJUDICATED_DOUBLING.tsv` — ausgewählte Lesung jedes Falls
- `PASS1021_CURRENT_APPRENTICE_SHEET.md` — Lehrmeistertafel mit der elften Regel
- `build_pass1021.py`, `validate_pass1021.py`, `PASS1021_VALIDATION.json`
