# GDT1203 — exact regrouping, with a paid end unit

Let the nonempty source word lengths be L1..Ln and prefix sums S1..Sn.
The continuous source followed by END has length Sn+1. Place inner written cuts
at S1+1,...,S(n-1)+1 and the last cut at Sn+1. Nonempty source words make these
cuts strictly increasing. The last source singleton still yields a nonempty
last group containing END. Subtract1from the observed internal cut positions,
remove END, and all original boundaries and source characters are recovered.
This is an inverse proof for arbitrary nonempty source words.

A lost END can hide a trailing empty group: source a|b and source ab would both
collapse to ab if empty outputs were discarded. The explicit end unit therefore
pays for information needed by this construction. Counting ignores no unit.

For a finite unit inventory, an injective prefix-free code over existing signs
preserves equality and inequality of whole unit strings. Thus actual group type
counts and frequencies are invariant under any such fixed carrier. A variable
carrier, ambiguous decoding, dropped end marker or a new grouping is outside
the tested contract. No particular carrier's length, ease or native fit follows.

The source-first rule explains how meaningful input COULD survive regrouping.
It does not explain why the real scribe would choose it, which source language
was used, or whether observed native suffixes are displaced initials. These are
unmet hypotheses, not translated meanings. Original structural constraints and
all previous fixed failures remain in force.
