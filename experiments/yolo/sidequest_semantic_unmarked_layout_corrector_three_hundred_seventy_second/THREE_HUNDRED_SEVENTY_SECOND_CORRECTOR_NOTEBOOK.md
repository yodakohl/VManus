# Pass 372 — unmarkiertes Korrektorenheft

- LAYOUT_A_WIDTH20 Zeile 1: `or kain chckhy cheky`
- LAYOUT_A_WIDTH20 Zeile 2: `cheky oky`
- LAYOUT_A_WIDTH20 Zeile 3: `aiin okeey qokedy`
- LAYOUT_B_WIDTH30 Zeile 1: `chor chkain shckhy cheky choky`
- LAYOUT_B_WIDTH30 Zeile 2: `chaiin qokeey`
- LAYOUT_B_WIDTH30 Zeile 3: `qokeey qokedy`

## Randentscheidungen

- LAYOUT_A_WIDTH20 1→2: **READ_ONCE_REMOVE_LEFT_MARGIN_COPY** — gleiche Karte direkt beidseits desselben Besitzerrandes.
- LAYOUT_A_WIDTH20 2→3: **RESET_NEW_MICROCYCLE** — Satzplatzfolge fällt von Zielgang auf Maßgang.
- LAYOUT_B_WIDTH30 1→2: **RESET_NEW_MICROCYCLE** — Satzplatzfolge fällt von Zielgang auf Maßgang.
- LAYOUT_B_WIDTH30 2→3: **READ_ONCE_REMOVE_LEFT_MARGIN_COPY** — gleiche Karte direkt beidseits desselben Besitzerrandes.

## Ergebnis

- LAYOUT_A_WIDTH20: `or kain chckhy cheky oky aiin okeey qokedy` (YES)
- LAYOUT_B_WIDTH30: `chor chkain shckhy cheky choky chaiin qokeey qokedy` (YES)
