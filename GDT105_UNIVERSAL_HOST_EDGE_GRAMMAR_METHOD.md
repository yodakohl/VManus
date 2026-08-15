# GDT105 — universal PAGE_HOST edge grammar

## Question

Is GDT102's `PCH` tail-to-renderer relation specific to `PCH`, or is it an
instance of a manuscript-wide PAGE_HOST edge grammar?

## Panel

Use all 15,592 groups in the frozen non-f84r HPR2 inventory. Define the formal
renderer outcome as one of:

- `BARE`;
- `DY`;
- `RIGHT`;
- `DY_RIGHT`;
- `B3`.

These are parser states, not semantic or linguistic categories.

## Models

With the complete physical folio removed, compare Jeffreys-smoothed models
conditioned on target register plus:

- register only;
- first PAGE_HOST character;
- final PAGE_HOST character;
- final two PAGE_HOST characters;
- PAGE_HOST length;
- exact PAGE_HOST.

Then train the same models after removing every `pch`-containing group and
score only `pch` groups. Finally, train on all other registers and score each
target register, without using target-register identity.

## Interpretation

If final-character prediction transfers from non-PCH to PCH and across
registers, the PCH tail grid is not a core-specific renderer system. The HPR2
generator should factor PAGE_HOST into a putative content address plus a
universal edge state. This does not establish that the residual address is
semantic; it only identifies a better formal boundary.

## Seal and claim ceiling

f84r is absent and is not opened, retained, queried, joined, scored, or
targeted. Formal edge grammar only: no word, morpheme, POS, sound, language,
plaintext, semantic role, gloss, meaning, or translation.
