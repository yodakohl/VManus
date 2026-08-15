# GDT058 — Q2 source-context record-coordinate bifurcation

## Question

Does source-native Q2 occupy different record coordinates when it is the first
member of a group versus when it follows A1 inside a group? This is an
exploratory formal-context test. Source-native Q2 corresponds to a display
`t` entry when group-initial and participates in the A1Q2 source pattern behind
display `ot` internally; it is distinct from the display-q/Q1 relation. The
test does not assume one prefix, morpheme, sound, or meaning.

## Inventory

Use complete physical lines from `gdt016_group_state_inventory.tsv`. Join the
source-native consensus group sequences and retain only groups whose complete
STA-code sequence agrees in ZL3b, IT2a, and RF1b. Alternate readings are one
manuscript, not replications. f84r is skipped before formal fields are parsed.

Two contexts are fixed:

1. `GROUP_INITIAL_Q2`: the first source member is Q2.
2. `INTERNAL_A1Q2`: an internal Q2 immediately follows A1.

For the first context, controls contain no Q2. For the second, controls contain
A1 but no Q2. Target and control groups must share page, source-code length,
and terminal source member. This deliberately controls major page/register,
length, and right-edge composition differences without requiring exact whole
group identity.

## Tests

For each context compare target minus control for normalized physical-line
position, normalized DY-field index, normalized within-field position, and
immediate-after-DY status. Use weighted matched-stratum effects, 20,000 fixed
random label permutations within strata, an eight-test Bonferroni correction,
and leave-one-physical-folio effects.

A robust negative early effect for group-initial Q2 plus a robust positive
later effect for internal A1Q2 supports context-conditioned record placement.
It does not give either context a linguistic or semantic interpretation.
