# LRG003 edge-profile block decomposition

Status: `REGISTERED_POST_CONFIRMATION_AGGREGATE_DECOMPOSITION`

LRG002 confirms that the opposite-parity LRG001 profile is elevated at both
corrected segment edges. LRG003 localizes that confirmed effect without opening
or ranking individual feature weights or forms.

Use the four feature blocks fixed before LRG001 calibration:

1. `FAMILY_INVENTORY`: 24 normalized family counts;
2. `INITIAL_FAMILY`: 24 initial-family one-hots;
3. `FINAL_FAMILY`: 24 final-family one-hots;
4. `ADJACENT_PAIR`: 576 normalized adjacent-family counts.

For each of the 5,824 B/P prose groups, compute each block's contribution under
the already fixed opposite-parity profile. Center every block independently
within exact page x symbol-count. Compute equal-folio FIRST-minus-CORE and
LAST-minus-CORE vectors for each block, section, parity, and folio. Project each
aggregate block vector onto the confirmed total raw-score direction and report
its signed fraction of the total projection.

Also compute and page-length-center the ordinary full 648-column raw score.
The sum of four centered block arrays and every aggregate vector must reconcile
with the full score to maximum absolute error <= 1e-12. Emit aggregate block
results and array digests only: no individual family weight, family ranking,
form, row, EVA spelling, semantic label, or English gloss.

This is an additive mechanism description, not a new confirmation test. Block
names describe feature locations, not morphemes, words, POS, names, identifiers,
meanings, plaintext, or translation.
