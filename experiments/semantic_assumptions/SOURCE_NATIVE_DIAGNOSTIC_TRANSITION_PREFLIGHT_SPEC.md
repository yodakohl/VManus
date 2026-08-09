# Diagnostic transition-transfer synthetic preflight

Status: **REGISTERED_TARGET_FREE_CALIBRATION**

## Frozen statistic

Use only the 1,382-row masked diagnostic panel. The six favored and 52
disfavored physical family pairs are frozen by the prose atlas; no diagnostic
family sequence is present in the panel.

For each assignment, independently cyclically rotate every exact ordinal
column among recipient groups within each stratum. Assignment zero is identity;
all later shifts use the frozen SplitMix64 mapping. Run both:

- `SECTION_KIND_LENGTH`, preserving section, editorial kind, complete length,
  and every exact-position family marginal;
- `FOLIO_KIND_LENGTH`, additionally confining all movement to the same physical
  folio while preserving kind, length, and exact-position marginals.

Count favored and disfavored adjacent physical pairs. A transfer pass in one
ensemble requires favored upper-tail and disfavored lower-tail empirical p at
or below the registered limit, favored excess and disfavored deficit each at
least .01 per noninitial position, at least 18/26 positive/negative folios,
and maximum absolute folio contribution fractions at most .25. Both ensembles
must pass.

## Synthetic grid

Use 2,048 assignments and p<=.02 for 64 exact-position-only null worlds, eight
global `GRAPH` worlds at strength .65, and eight each `ONE_SECTION`,
`ONE_FOLIO`, and `POSITION_CHAIN` adversaries. Require <=1/64 null passes,
>=7/8 global graph passes, and zero adversarial passes. Recompute world 0 null
and world 100 graph with the target-size 8,192 assignments and require the same
decisions. Require exact capacity, finite summaries, deterministic orbit and
shift digests, malformed sequence/panel rejection, absent target artifacts,
and zero target family access.

Freeze masked panel
`7ed9f8186dcb31bd49a446e6b7751dc0bfc0f9d508feb816314fc71105daea02`,
capacity validation
`0a1257ffd8e1b88a3f94fade1381516c95f2cbdf9eeba3d0dc41a64ca5b23033`,
prose family atlas
`f20a0b1efb256c99c91b0899bb5c946d3a0483bc99a7467373a096d3c1934287`,
atlas validation
`209510d655c4b81c58f8f5eaec27676a4eee71317e3b485b3a1ce88d975dfd5c`,
and core
`4494da0ec8969b44c5636c419fb55b3485d4ddad98c3406c6f0cf09a3595a211`.

A pass authorizes only a separately frozen one-time join of the 1,382
diagnostic family sequences. It does not establish wordhood, ownership, label
meaning, picture identity, sound, language, cipher operation, plaintext, or
translation.
