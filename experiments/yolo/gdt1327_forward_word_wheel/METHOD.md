# GDT1327 — forward whole-word wheel: preregistered necessary test

Selected 2026-10-11 before native reciprocal-pair counts. Total wall-time budget:
25 minutes from 05:03 UTC, including preparation, validation and publication.
If unfinished, stop expansion and record the exact remaining work.

## Complete invented writer
Source domain is any finite string over lowercase a-z and SPACE, including empty,
leading/trailing and repeated spaces. Reject all other characters. A paid shared
bank W contains M>=28 distinct nonempty strings over 22 abstract drawings; exact
whole strings each name one unique index0..M-1. Source characters map bijectively
to positive steps1..27. Bank, order, alphabet permutation, and initial index are
shared apparatus; no historical attestation or native key is asserted.
For every source character advance by its step modulo M and output the reached
whole bank entry. At the initial index and after each payload output, emit K extra
copies of the current bank entry, where independently P(K=k)=.99*.01**k for k>=0.
Zero copies are allowed; this is a normalized finite-almost-sure padding rule.
Physical spaces delimit output packets; no gaps inside a packet. A one-line
message suffices; multiple explicitly demarcated lines have paid shared anchors
and encode consecutive source substrings. Empty source can yield initial nulls.
Reader looks up successive indices starting at the shared anchor: delta0 is null,
delta1..27 is its unique source character, all other deltas are invalid. This
recovers the exact source including source spaces. Word-shape structure is paid
in the bank, not explained by this construction.

## Question, predecessors and assumptions
Unknown: can any such ordering accommodate already admitted whole-word adjacency?
GDT1301 emits differences of source-WORD ranks, not the reached ciphertext-word
state; its four fixed sourcebook failures remain unchanged. GDT1217 differences
source-unit states on a22ring with escape glyphs and fixed source books; its
length-dispersion failure remains. GDT1319 concerns only first/last-unit marker
interfaces, not arbitrary whole-word states. GDT857 disjoint per-letter pools is
not this state machine; explicit null repeats permit AAA here. No old failure is
superseded. Positive motivation: a small reversible human-operable rule can carry
state across whole packets and permit repeats; neither property proves a fit.

Assume retained strict whole groups are exact packets, with no skipped payload
between original consecutive groups. Each form has exactly one bank position.
Generously allow a different bank/order per page and an arbitrary shared anchor
per physical line. The two relevant edges must share a page bank, not a line.
No reset inside an observed adjacency. Alternate readers stay separate.

## Necessary obstruction and fixed selection
For distinct A,B, A->B requires forward distance d in1..27; B->A requires M-d
in1..27. Thus M<=54. If the same page has V>54 distinct whole forms, M>=V>54,
a contradiction for every bank ordering, unused entries, and source alphabet
permutation. Null repeats do not change the argument. This is an elementary
necessary condition, not a sufficiency test or newly discovered theorem.

Use all strict GDT1233 groups and GDT1319 original-consecutive same-line pairs,
hash-bound and admitted by GDT631 allowlist. For each reader and page retain V,
number of distinct unordered reciprocal nonself pairs and qualifying status.
Select lexicographically first qualifying page, then lexicographically first
unordered pair, then lowest (locus,source_group_index) witness per direction.
Save complete page table and exact witnesses. No counts have been inspected.
A qualifying page excludes the stated whole family for that reader. Absence
means NOT_EXCLUDED_BY_THIS_TEST, never a recovered key or success. If all three
qualify, close family; otherwise retain reader-specific outcome. No p-values,
sourcebook fit, phase fitting, signed/large-step repair or alias-bank expansion.

Validator rebuilds page sets and pairs from guarded GDT915 original line windows,
checking every strict row, and independently verifies all results and witnesses.
Source-free fixtures: exhaustive small rings S=1..6, M=S+1..4S+2 demonstrate
reciprocal existence iff M<=2S; M=2S antipodal pair shows sharpness. Complete
writer/reader roundtrips check all two-character sources and representative
null counts. Claims concern this writing rule only, not all stateful ciphers,
medieval authors, natural language, meanings or semantic word boundaries.
No semantic relation packet is created; GDT388 relation scoring is not invoked.
No new image, reserve, f84/f84r or f116v access. This panel is historically exposed.
