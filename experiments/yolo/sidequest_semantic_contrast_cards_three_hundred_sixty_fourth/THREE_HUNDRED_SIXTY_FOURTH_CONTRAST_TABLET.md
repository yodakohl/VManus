# Pass 364 — 22 Kontrasttafeln

## P01 — Abführung + ABFÜHREN

- **ABZIEHEN** → `T03::TRANSFER[abziehen]` (NOMENCLATOR_MNEMONIC)
- **ERGEBNIS** → `T03::TRANSFER[Abzug]` (GRAMMATICAL_ASPECT)
- **GUT** → `T03::TRANSFER[Abführgut]` (GRAMMATICAL_ASPECT)
- **VORGANG** → `T03::TRANSFER[Abführung]` (GRAMMATICAL_ASPECT)
- **WEGFÜHREN** → `T03::TRANSFER[abführen]` (GRAMMATICAL_ASPECT)

## P02 — Abführung + QUELLE+ABFÜHREN

- **ERGEBNIS** → `T03::TRANSFER[Quellabzug]` (GRAMMATICAL_ASPECT)
- **VORGANG** → `T03::TRANSFER[Quellabführung]` (GRAMMATICAL_ASPECT)

## P03 — Absetzen + ABSETZEN

- **NACH_EINSATZ** → `T05::TRANSFER[Einsatzabsetzen]` (REPEATED_SEMANTIC_CUE)
- **SCHLIESSEN** → `T05::TRANSFER[Absetzschluss]` (REPEATED_SEMANTIC_CUE)
- **ZEIT** → `T05::TRANSFER[Standzeit]` (REPEATED_SEMANTIC_CUE)

## P04 — Ansatz + ANSATZ

- **AUSZUG** → `B03::BEZUG[Auszugsansatz]` (REPEATED_SEMANTIC_CUE)
- **GRUNDANSATZ** → `B03::BEZUG[Ansatz]` (REPEATED_SEMANTIC_CUE)

## P05 — Ansatz + FOLGE+ANSATZ

- **GLEICHER_WEITER** → `B03::BEZUG[Fortsetzungsansatz]` (REPEATED_SEMANTIC_CUE)
- **NÄCHSTER** → `B03::BEZUG[Folgeansatz]` (REPEATED_SEMANTIC_CUE)

## P06 — Durchgang + DURCHGANG

- **BECKEN** → `T04::TRANSFER[Beckenlauf]` (OWNER_VISIBLE)
- **LEITEN** → `T04::TRANSFER[durchleiten]` (GRAMMATICAL_ASPECT)
- **PASSIEREN_LASSEN** → `T04::TRANSFER[durchlassen]` (GRAMMATICAL_ASPECT)

## P07 — Durchgang + KURZ+DURCHGANG

- **ABSCHNITT** → `T04::TRANSFER[Kurzpassage]` (GRAMMATICAL_ASPECT)
- **VORGANG** → `T04::TRANSFER[Kurzdurchgang]` (GRAMMATICAL_ASPECT)

## P08 — Einsetzen + OHNE_ZUSATZ

- **GRUNDHANDLUNG** → `Z02::ZIEL[Einsetzen]` (NOMENCLATOR_MNEMONIC)
- **LAUF** → `Z02::ZIEL[Laufeinsatz]` (REPEATED_SEMANTIC_CUE)
- **NEU** → `Z02::ZIEL[Neueinsatz]` (REPEATED_SEMANTIC_CUE)
- **WIEDER** → `Z02::ZIEL[Wiedereinsatz]` (REPEATED_SEMANTIC_CUE)

## P09 — Festmachen + BINDEN

- **HANDLUNG** → `A02::SCHLUSS[befestigen]` (GRAMMATICAL_ASPECT)
- **STUFE** → `A02::SCHLUSS[Bindestufe]` (REPEATED_SEMANTIC_CUE)

## P10 — Fortsetzung + FOLGE

- **AKTIV_FÜHREN** → `B04::BEZUG[weiterführen]` (GRAMMATICAL_ASPECT)
- **ANKNÜPFEN** → `B04::BEZUG[Anschluss]` (NOMENCLATOR_MNEMONIC)
- **GLEICHES_WEITER** → `B04::BEZUG[Fortsetzung]` (REPEATED_SEMANTIC_CUE)
- **LAUF** → `B04::BEZUG[Weiterlauf]` (REPEATED_SEMANTIC_CUE)
- **NÄCHSTES_WEITER** → `B04::BEZUG[Folgefortsetzung]` (REPEATED_SEMANTIC_CUE)
- **WEG** → `B04::BEZUG[Weiterweg]` (REPEATED_SEMANTIC_CUE)

## P11 — Fortsetzung + FOLGE+LANG

- **GLEICHER_WEITER** → `B04::BEZUG[Langfortsetzung]` (REPEATED_SEMANTIC_CUE)
- **NÄCHSTER** → `B04::BEZUG[Langfolge]` (REPEATED_SEMANTIC_CUE)
- **STUFE** → `B04::BEZUG[Langfolgestufe]` (REPEATED_SEMANTIC_CUE)

## P12 — Fortsetzung + FOLGE+POSTEN

- **GLEICHER_POSTEN** → `B04::BEZUG[Weiterposten]` (REPEATED_SEMANTIC_CUE)
- **NÄCHSTER_POSTEN** → `B04::BEZUG[Folgeposten]` (REPEATED_SEMANTIC_CUE)
- **NÄCHSTES_WEITER** → `B04::BEZUG[Folgefortsetzungsposten]` (REPEATED_SEMANTIC_CUE)

## P13 — Klären + KLÄREN+ABFÜHREN

- **KLAR** → `T07::TRANSFER[Klarabzug]` (REPEATED_SEMANTIC_CUE)
- **TRENNEN** → `T07::TRANSFER[Trennabzug]` (REPEATED_SEMANTIC_CUE)

## P14 — Material + PORTION+PFLANZENTEIL

- **ALLGEMEINER_TEIL** → `B01::BEZUG[Pflanzenteil]` (OWNER_VISIBLE)
- **WURZEL** → `B01::BEZUG[Wurzelteil]` (OWNER_VISIBLE)

## P15 — Portion + POSTEN+PORTION

- **NORMALE_PORTION** → `M02::MASS[Postenportion]` (NOMENCLATOR_MNEMONIC)
- **ZWEITE_PORTION** → `M02::MASS[Postenzweitportion]` (REPEATED_SEMANTIC_CUE)

## P16 — Sollmaß + MASS

- **EINSTELLUNG** → `M01::MASS[Sollstellung]` (REPEATED_SEMANTIC_CUE)
- **MENGE** → `M01::MASS[Sollmaß]` (REPEATED_SEMANTIC_CUE)

## P17 — Transfer + OHNE_ZUSATZ

- **AUSZUG_NEHMEN** → `T01::TRANSFER[Auszugnahme]` (REPEATED_SEMANTIC_CUE)
- **LAUF_BEENDEN** → `T01::TRANSFER[Laufschluss]` (REPEATED_SEMANTIC_CUE)

## P18 — Transfer + TRANSFER

- **NEUTRAL** → `T01::TRANSFER[Transfer]` (NOMENCLATOR_MNEMONIC)
- **UMSETZEN** → `T01::TRANSFER[Umsetzen]` (REPEATED_SEMANTIC_CUE)
- **UMSETZEN_SCHLIESSEN** → `T01::TRANSFER[Umsetzschluss]` (REPEATED_SEMANTIC_CUE)
- **ÜBERFÜHREN** → `T01::TRANSFER[überführen]` (NOMENCLATOR_MNEMONIC)

## P19 — Waschgang + WASCHEN

- **WASCHEN** → `T09::TRANSFER[Waschgang]` (REPEATED_SEMANTIC_CUE)
- **WASSER_ZU** → `T09::TRANSFER[Wasserzulauf]` (OWNER_VISIBLE)

## P20 — Wärmen + LANG

- **HANDLUNG** → `D04::ZUSTAND[Langwärmen]` (GRAMMATICAL_ASPECT)
- **ZUSTAND** → `D04::ZUSTAND[Langwärme]` (GRAMMATICAL_ASPECT)

## P21 — Zielstelle + ZIEL

- **ALLGEMEIN** → `Z01::ZIEL[Stelle]` (NOMENCLATOR_MNEMONIC)
- **EINGABE** → `Z01::ZIEL[Zieleingabe]` (GRAMMATICAL_ASPECT)
- **EINSATZ** → `Z01::ZIEL[Zieleinsatz]` (GRAMMATICAL_ASPECT)
- **MARKE** → `Z01::ZIEL[Zielmarke]` (REPEATED_SEMANTIC_CUE)
- **SCHLIESSEN** → `Z01::ZIEL[Zielschluss]` (REPEATED_SEMANTIC_CUE)
- **ZWISCHEN** → `Z01::ZIEL[Zwischenziel]` (REPEATED_SEMANTIC_CUE)

## P22 — Zugabe + ZUGABE

- **AUSZUG** → `M03::MASS[Auszugzugabe]` (REPEATED_SEMANTIC_CUE)
- **EINLEGEN** → `M03::MASS[Einlage]` (GRAMMATICAL_ASPECT)
- **ZUGEBEN** → `M03::MASS[Zugabe]` (GRAMMATICAL_ASPECT)
- **ZUSATZSTOFF** → `M03::MASS[Zusatz]` (GRAMMATICAL_ASPECT)

## Regel

Ein wiederkehrender Bedeutungsunterschied darf als Zusatzkürzel gelehrt werden. Ein einmaliger Unterschied bleibt ein Merkspruch an der ganzen Karte. Beides wählt die Karte, aber nur Ersteres erweitert die produktive Grammatik.
