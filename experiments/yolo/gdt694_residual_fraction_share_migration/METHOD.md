# GDT694 method

## Question and fixed scope

GDT693 selected German *Anteil* for its scoped R-selector family but left 22
inherited exact token positions under older whole-form glosses containing
*Fraktion*. GDT694 asks whether every one of those residual positions can be
migrated without erasing its already assigned material head, quality, index,
quantity, action, reader boundary or local product rival.

The scope is fixed at GDT693's 479 token positions, 51 lines and 36 admitted
pages. The 22 residual keys are the complete target list. No search over other
pages or over similar-looking substrings is performed; f84 and f84r are
forbidden.

## Exact-card source deck

`src/V67_22_RESIDUAL_SHARE_RULES.tsv` supplies one row per residual key. Every
row binds:

- locus, token ordinal, exact surface and expected V66 gloss;
- one V67 main gloss, explicit share index and preserved material/action heads;
- a composition class and visible parse or reader boundary;
- one strongest local rival and primary experiment history.

A build stops if any expected surface or V66 gloss has changed. Therefore the
migration cannot silently land on a later homograph or an inherited edit.

The architecture remains deliberately hybrid. Three forms—`arl`, `lldar` and
`chear`—are `LEARNED_WHOLE_WITH_SHARE_RENDERER`: their German whole-card heads
are normalized, but their apparent internal substrings are not exported.
Nineteen further cards retain exact-card compositions around productive or
learned bodies. Even those rules license only the named occurrence/surface;
there is no global substring replacement.

## Ambiguity repairs

Five decisions are checked separately:

1. `okeeodar` contains one written `d`. The main uses the longer GDT691
   `KEEOD+AR` workflow block and reads *Anteil I des vollständig erhitzten
   Auszugs*. The older `KEEO+D+AR` measured-Ansatz parse remains the rival;
   the main may not use the same `d` for both *Auszug/abgezogen* and
   *abgemessen*.
2. RF1b exposes `ar|aram`. The main therefore reads appositionally
   *Drogenanteil I; davon ein Maß*. GDT693's recursive two-R reading remains a
   named rival, not an unmarked doubling.
3. `chdar` uses I as the AR share index and no longer counts that same I again
   as an independent preparation stage.
4. In learned `chear`, GDT639 binds `CH+E` only as one attributive dry shell.
   V67 therefore adds no independent E-stage and licenses no free `E` parse.
5. At f86v6.4, both alternate readers join `lkarchees`. The new exact span
   `l|karchees` consumes the wood head once and renders a fully dried charge
   from share I of the heated wood drug.

The two inherited GDT693 quantity/head spans remain unchanged, giving three
non-overlapping bound spans in V67.

## Renderer and preservation checks

The builder first reconstructs all 51 V66 lines from their token glosses and
two inherited spans. It then changes exactly the 22 registered keys, adds the
third span and reconstructs V67. It records the complete 479-token edition,
the complete 51-line edition, a 17-line change audit, all 22 rule applications,
three spans, 113 verb profiles, six inherited product rivals, and terminology
and composition-class censuses.

The independent validator does not import the builder. It recomputes rule
keysets, changes, both line editions, span consumption, verb-profile parity,
term counts, critical ambiguity repairs and all hashes. Finally it executes
the builder in a fresh temporary directory and compares twelve generated files
byte-for-byte.

## Decision rule and claim ceiling

Pass requires exactly 22 changed token positions on 17 lines, zero
*Fraktion*-bearing words in both V67 channels, three non-overlapping exact
spans, parity for all 113 inherited verb profiles, unchanged six product
rivals, and zero new/f84/f84r pages. All conditions pass.

V67 is an exploratory exact-card German working renderer. It assigns a
practical default to every token in this fixed deck and makes its selected
share terminology uniform. It is not recovered plaintext and identifies no
language, sound value or manuscript-wide free morpheme dictionary.
