# GDT771-Methode — Reicht der vorhandene Vollzeilen-Cache für die vier Lücken?

## Suchraum

Aus GDT769 werden genau 523 reader-exakte Vorkommen der vollständigen Formen
`ol`, `ckhy`, `ols` und `otar` übernommen. Sie liegen an 461 eindeutigen Loci.
Diese Loci bilden die explizite Allow-Liste für zwei Guard-Abfragen:

- GDT734: 461 ausgewählte Zeilen, 0 verbotene Zeilen materialisiert;
- GDT760: 46 ausgewählte Mengenzeilen, 0 verbotene Zeilen materialisiert.

173 der 461 Loci sind im GDT734-Cache vollständig. Vereinigt mit den fünfzehn
GDT770-Zeilen entstehen 176 Loci mit 203 Zielvorkommen. Nach den alten und fünf
neuen zeilenweiten Ausschlüssen bleiben 195 Zielvorkommen für strenge
Entscheidungen. Ausgeschlossene lokale Kontakte werden nicht gelöscht, sondern
mit Grund im Atlas behalten.

## `ol`: vom linken Kontakt zum ganzen Zweig

Ein linker Kontakt ist konservativ lizenziert, wenn mindestens eine dieser
Bedingungen gilt:

- ein GDT760-Mengenspan endet genau am Token vor `ol`;
- die direkte linke Zelle ist eine reader-exakte Form aus
  `src/OL_BARE_VALUE_FORMS.tsv`;
- die konkrete Kante ist in `src/OL_LEFT_ROLE_TRANSFERS.tsv` als bereits
  target-unabhängige `AMOUNT_VALUE`-Kante festgehalten.

Mehrere Belegwege für dasselbe Zielvorkommen werden einmal gezählt. Der Atlas
führt zusätzlich breitere GDT769-Mengenrollen als Sensitivität, ohne sie
automatisch zur konservativen Menge zu machen.

Der zweite Kontrast verlangt einen physisch direkten reader-exakten
Rechtsnachbarn. Der dritte verlangt zusätzlich mindestens eine rechte Rolle,
die der ursprüngliche GDT770-Zweig tatsächlich akzeptiert. Der Crosswalk
übernimmt etwa `CONTENT_PREPARATION → PREPARATION` und
`PROCESS_PASS → PROCESS`. Er übernimmt ausdrücklich nicht
`AMOUNT_VALUE`, `SCALAR_VALUE`, `QUALITY_STAGE`, `CLOSE` oder `KNOWN_OTHER`
als rechte Pflichtrolle. Vier konkrete, bereits an anderen Stellen
eingefrorene Ganzwortrollen stehen in `src/OL_RIGHT_ROLE_TRANSFERS.tsv`.

Dadurch bleiben drei verschiedene Aussagen getrennt: linker Mengen-/Wertfund,
rechter exakter Zellkontakt und vollständig score-fähiger Relatorzweig.

## `ckhy` und `ols`

Für `ckhy` gilt unverändert die Konjunktion der GDT769-Frames
`F05_PROCESS_SLOT_FINAL` und `F07_LINE_FINAL_OR_CLOSE`. Zusätzlich gelangen
vollständige Finalstellen ohne F05 als Negativkontrollen in den nächsten Deck.

Für `ols` gilt `F02_VALUE_DIRECT`. Alle drei exakten Treffer bleiben sichtbar.
Nur eine vollständige Zeile darf die strenge Verfügbarkeitsentscheidung
tragen; `f83r.10` und `f99v.21` werden nicht mithilfe einer gewünschten
`ols`-Bedeutung vervollständigt.

## `otar`

Das Folgenprädikat verwendet wie GDT769 entweder `F14` zusammen mit `F15` oder
`F16`, oder einen gerichteten `F06`-Anschluss. Das Nominalprädikat verwendet
`F01`, `F02` oder `F06`. Ihre Mengen dürfen verschachtelt sein.

Der Endpunktkandidat verwendet entweder den bereits vorhandenen
GDT769-R2-Prozess/Endpunkt-Rahmen oder die unmittelbar eingefrorenen
GDT770-Nachbarrollen. Damit zählt `f75r.43@6` korrekt als lokaler
Feld-zu-Endpunkt-Fall. Ein einzelner Fall erreicht die geforderte zweite Seite
nicht. Die formale Übermenge des Folgenprädikats ist daher ein Anzeigelead,
kein Sieg über `Zwischenzubereitung` oder `bis`.

## Ausgaben

Der Runner schreibt die vollständige Allow-Liste, alle zugelassenen
Zielkontexte, einen eigenen `ol`-Brückenatlas, jeden Diskriminatortreffer, die
Schwellenbilanz, den `otar`-Mengenvergleich, den nächsten Score-Deck, ein
Vierwort-Arbeitswörterbuch und das kompakte Ergebnis.

Der Validator importiert den Runner nicht. Er wiederholt beide Guard-Abfragen,
berechnet die drei `ol`-Mengen unabhängig, prüft den einzelnen `otar`-Endpunkt,
kontrolliert die Null-Kredite und reproduziert alle neun Runner-Ausgaben
bytegenau in einem temporären Verzeichnis.

Die Ausgabe bestätigt keine deutsche oder englische Wortbedeutung, keine
Wortart, keinen Stoff, keine Sprache, keinen Laut- oder Glyphenwert und keinen
produktiven EVA-Wortstamm.
