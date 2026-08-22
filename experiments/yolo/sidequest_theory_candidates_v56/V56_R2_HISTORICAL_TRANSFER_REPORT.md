# V56 R2 — historischer Quellenphrasen-Transfer Herbal ↔ Biological

## Ergebnis

Die tragfähige Brücke ist klein: **zehn Quellenphrasenklassen auf elf exakten
gemeinsamen Karten**. Sie bilden kein Wörterbuch, sondern eine plausible
Kurzsprache für zwei medizinische Schreiblagen:

```text
nach Maß | mit dem Vorigen | verwenden | an | setzen
Bereitung | wenn bereit | klar | wie zuvor | Teil
```

Ein zwölfter ausgewählter Kartentyp, das CLOSE-gebundene `oldy`, behält nur
den formalen LINK-Wert und wird für eine gesprochene gemeinsame Phrase auf
`LOCAL_ONLY` gesetzt. Fünf weitere gemeinsame exakte Karten bleiben
`UNKNOWN/WITHDRAW`.

## Exakter Scope und Counts

Die sieben erlaubten GDT327-Seiten enthalten 381 Ereignisse. Der bewachte
Exact-ID-Schnitt ergibt:

- 17 gemeinsame exakte Kartentypen;
- 44 Herbal- und 92 Biological-Ereignisse, zusammen 136;
- davon 12 Typen mit überhaupt einem ausgewählten V50/V51-Anker;
- diese zwölf tragen 30 Herbal- und 68 Biological-Ereignisse, zusammen 98;
- Entscheidungen: 11 `KEEP`, 1 `LOCAL_ONLY`, 5 `WITHDRAW`.

Die Matrix zählt eine Karte nur dann als transferierbar, wenn dieselbe
`joint_tuple_id` in beiden Registern vorkommt. Sichtbare Ähnlichkeit,
PAGE_HOST-Nachbarschaft und Substrings zählen nicht.

## Historischer Mechanismus

Materia-medica-Artikel, Rezeptbücher, Bäder- und Frauenheiltexte um 1420
teilen eine kleine Menge gewöhnlicher Kurzformeln. Die einschlägigen
Quellmechanismen sind nicht ungewöhnlich:

- Maß- und Dosierformeln wie *secundum/ad mensuram*;
- Rückverweise wie *ut supra*, *prius*, *praedictus* oder *cum praedicto*;
- knappe Setz- und Gebrauchsverben wie *pone*, *mitte*, *utere*, *appone*;
- Zielergänzungen mit *ad locum/ad partem*;
- Zustandsklauseln wie *quando paratum* und *donec clarum*;
- breite Sachwörter wie *praeparatio/confectio* und *pars*.

Die Rezepttradition des *Antidotarium Nicolai* erklärt Maß, Bereitung,
Mischen und Gebrauch; die *Trotula*-Tradition erklärt denselben elliptischen
Stil bei Bad, Waschung, warmer Anwendung und Auflage. *De balneis
Puteolanis* stützt die gemeinsame Bad-/Heildomäne, ist aber eher eine
Gattungs- als eine Wortlautparallele. Diese lateinischen Beispiele zeigen nur,
wie eine Quellphrase abgekürzt werden konnte. Sie identifizieren weder die
Manuskriptsprache noch Lautung oder Etymologie einer Karte.

## Was wirklich überträgt

Am stärksten sind `MASS?` (9/11), der offene LINK-Typ (3/16), `VERWENDEN?`
(3/7), `BEREIT?` (3/4) und `BEREITUNG?` (5/2). Ihre lokalen Gegenstände
wechseln—Pflanzenteil und Auszug im Herbal, Portion, Medium oder Station im
Biological—doch die kurze Quellenhandlung bleibt gewöhnlich.

`KLAR?`, `AN?`, `ZUVOR?` und `TEIL?` bleiben wegen 1–3 Herbal-Belegen
schwächer. Sie werden behalten, weil ihre minimale Phrase den Gegenstand nicht
heimlich mitliefert: `an` nennt kein Ziel, `Teil` kein Organ, `wie zuvor`
keinen Antezedenten und `klar` kein bestimmtes Medium.

`SETZEN` überträgt auf zwei verschiedene exakte Karten. Beide bleiben getrennt;
das gemeinsame Wort ist nur der V50-Operator. Insbesondere erbt
`SET(<ARG_AIIN>)` **nicht** `AIIN=MASS?`, und `SET(<ARG_AL>)` erbt **nicht**
`AL=AN?`. Die lokalen Fassungen „einen Bestandteil ansetzen“ und „eine Charge
einstellen“ liegen auf der Recordebene.

## Lokale Ausnahmen und Rückzüge

Mehrere medizinisch attraktive Merkwörter scheitern schon am Exact-ID-Gate:

| Kandidat | Herbal | Bio | Entscheidung |
|---|---:|---:|---|
| `LCHE=ABLASSEN?` | 0 | 8 | `LOCAL_ONLY` |
| `OKE=SPÜLEN?` | 0 | 8 | `LOCAL_ONLY` |
| `OKEEY=WARM?` | 0 | 7 | `LOCAL_ONLY` |
| `CKHY=UNKNOWN` | 0 | 4 | `WITHDRAW` |
| `OT=MARKIEREN` als PAGE_HOST | 0 | 7 | `LOCAL_ONLY` |
| `E=UNKNOWN` als PAGE_HOST | 0 | 14 | `WITHDRAW` |

Besonders wichtig ist der Wärmetest: Die gemeinsame exakte Karte `cheeky`
kommt je einmal in Herbal und Bio vor, ist aber **nicht** die exakte OKEEY-Karte.
Darum darf `WARM?` trotz passender lokaler Artikel nicht über die ähnliche
Oberfläche importiert werden.

## Stärkster Gesamtwiderspruch

Die 17 gemeinsamen Kartentypen beweisen eine gemeinsame Werkstatt- oder
Registerökologie; sie beweisen keine gemeinsame Wortbedeutung. V53 benennt nur
32/100 Herbal-Ereignisse mit ausgewählten Ankern, V54 nur 113/281 Bio-
Ereignisse. Pflanze, Wasser, Wein, Bad, Rohr, Körper und Krankheit stammen aus
Bild und Gattung. Ein kurzer Transfer bleibt nur dort zulässig, wo er genau
diese stillen Gegenstände **nicht** in den Kartenwert einbaut.

**Validierung: PASS — 17 gemeinsame exakte Karten, 44 Herbal- plus 92
Biological-Ereignisse; 17 Matrixzeilen; keine Substrings, keine Lautung, keine
zusätzliche Seite.**
