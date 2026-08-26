# GDT461 — internal stem residual bridge

## Result

Functional stems are not confined to the edges of local labels. Nine
strict-internal channels survive running-text calibration and assign 53
nonoverlapping occurrences in 44/107 labels:

| stem | working value | matching running extension types |
|---|---|---:|
| `air` | BAHN | 8/8 |
| `cth` | NEHMEN · EINSTELLEN | 39/39 |
| `dar` | HIER · AUSGANG | 6/6 |
| `al` | ZIELORT | 74/81 |
| `ar` | AUSGANG | 35/38 |
| `ok` | SETZEN | 107/114 |
| `ol` | FORTSETZEN | 103/107 |
| `ot` | DANACH | 55/56 |
| `sh` | HALTEN | 125/131 |

These internal assignments account for another 114 characters. Together with
GDT460's edge channels, 391/713 characters (54.84%) of the learned-label deck
now have a calibrated functional reading.

## Revised label architecture

| status | GDT460 | GDT461 |
|---|---:|---:|
| full function formula | 5 | 12 |
| function shell + learned core | 78 | 81 |
| owner-family marker only | 5 | 1 |
| whole learned label | 19 | 13 |

Ninety-three labels now contain at least one calibrated function channel.
Including the sole family-only label, 94/107 have internal structure.

## Twelve complete formulae

The internal channels close seven additional gaps. The complete set is now:

- `okolar` → `SETZEN · FORTSETZEN · AUSGANG`;
- `alcphy` → `ZIELORT · NEHMEN · EINSETZEN · POSTEN`;
- `okaraiin` → `SETZEN · AUSGANG · WERT`;
- `otalaiin` → `DANACH · ZIELORT · WERT`;
- `okalam` → `SETZEN · ZIELORT · HIER`;
- `sharam` → `HALTEN · AUSGANG · HIER`;
- `okaram` → `SETZEN · AUSGANG · HIER`;
- `otolam` → `DANACH · FORTSETZEN · HIER`;
- `alaly` → `ZIELORT · ZIELORT · POSTEN`;
- `otolaiin` → `DANACH · FORTSETZEN · WERT`;
- `otokol` → `DANACH · SETZEN · FORTSETZEN`;
- `otolarol` → `DANACH · FORTSETZEN · AUSGANG · FORTSETZEN`.

This is the clearest current evidence for word-like composition inside the
local nomenclator stream: the same short surface pieces retain the same working
value at the beginning, middle, or end under separately calibrated channels.

## What happened to the old nineteen-word tail

Five residuals gain an internal function:

- `osarsheeeo` contains `ar=AUSGANG` and `sh=HALTEN`;
- `yfary` and `ytarem` contain `ar=AUSGANG`;
- `octho` contains `cth=NEHMEN · EINSTELLEN`;
- `dotedy` contains `ot=DANACH`.

One more, `cheosdy`, joins the exact `cheo` pharmaceutical family. The family
has four unique address surfaces on both pharmaceutical pages:
`cheocthy`, `cheody`, `cheosdy`, and `opcheor`. Its safe value is only
`DROGENFAMILIE`.

Thirteen labels remain genuinely whole under the present rules:
`oiil`, `arom`, `ofaom`, `chdaiirdainy`, `ofchdamy`, `opoiiinoin`, `opoeey`,
`of`, `arody`, `ykyd`, `ykocfhy`, `yddy`, and `korainy`.

## Working codebook rule

The current name-card grammar is now:

> calibrated prefix + zero or more calibrated internal functions + learned
> name fragment(s) + calibrated suffix.

Only the thirteen final exceptions still require whole-form memorization. The
middle fragments remain visible in brackets in the released dictionary, so a
long fluent phrase is never mistaken for one word meaning.

## Validation and ceiling

Validation passes 39/39 checks. It recomputes the nine internal calibrations,
all 53 intervals, nonoverlap and center containment, the exact `cheo` family,
all revised counts, source/image bindings, and a byte-identical rebuild.

No new page, surface prediction, core meaning, individual name, confirmed
lexeme, plaintext, or language claim is added.
