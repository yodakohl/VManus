# GDT896: complete source entries under a decoded-control ring

Preregistered 2026-09-09 23:03 UTC, before896 target processing. Decision and
60-minute total budget: [proposal](../../../docs/joint_reading/PROPOSAL.md).
Preparation checkpoint23:18, latest target start23:38, publication by23:58UTC.

The historical mechanism is Alberti's fixed-outer-index mode in Meister1906,
printed pp133,136–139, [Getty digitization](https://archive.org/details/diegeheimschrift00meis).
The actual fixed-index passage is
[p138](https://archive.org/download/diegeheimschrift00meis/page/n153/mode/1up).
This later mechanism has no established connection to Voynich. Its optional
sentence codebook, uppercase nulls, spelling deletions and mobile-index mode
are excluded. The first transmitted sign initializes a message and emits no
payload, an explicit protocol reading. Source images were inspected before
selection; IDEA000130 retains edition/dating qualifications.

Outer sequence O is `abcdefgilmnopqrstuxz1234`, 24 distinct positions. One
unknown index j in0..19 and one injective position map pi for all observed
literal ASCII cipher characters are shared by an entire reading panel.
The global rotation gauge is pi(the panel's lexically least glyph)=0; other
disconnected message components retain all relative offsets. Unobserved inner
signs occupy unused positions existentially and are never claimed identified.

At the first cipher character c0 set anchor=c0 without output. Every subsequent
c yields k=(pi(c)-pi(anchor)+j) mod24. If k<20, emit O[k] and retain anchor;
otherwise emit nothing and set anchor=c. Arbitrary consecutive and trailing
controls are allowed as an explicitly broader mechanical closure of the source
procedure. A negative result therefore also excludes its stricter subcases;
a compatible witness does not establish that this broader usage was historical.

Inputs are byte-frozen in SPEC.json. Source is exactly895's1016 complete accepted
entries of the explicitly partial eclectic Simon edition. Concatenate every
original word after ONLY j->i and v->u. If any other letter falls outside O's
20 ordinary letters, exclude the whole entry and retain its ID/reason. No title,
apparatus, H deletion, replacement spelling, omitted word or new acquisition.
Distinct entries producing identical projected strings remain distinct aliases.

Target is exactly893's previously exposed odd-only complete-paragraph packet:
ZL14, IT259, RF11, consensus1. These are alternative readings of one manuscript,
not independent samples. Concatenate every complete literal raw word group;
spaces have no channel role. EVERY paragraph is one separately initialized
complete message, assigned a DISTINCT complete source entry. This paragraph-as-
message and Simon-copy conjunction is hypothetical, not a source fact. No
partial coverage, source windows, reading mixing, held or new-page access.

For n cipher characters in R maximal equal-character runs, output length is
n-R..n-1. The initial run of r signs emits O[j]^(r-1). Each later run of r emits
either some ordinary letter repeated r times, or O[j]^(r-1). Exact acceptance
of this independent-run relaxation is a necessary domain filter; it is not
sufficient for any ring. Global symbol capacity is24 and entry assignment is
AllDifferent. Remaining cases use exhaustive finite ring/entry search, keeping
every observed model until completion or the budget/cap. A fixed message first
glyph is a local gauge only; the global search must retain component offsets.

Primary direct position DFS and independently built relative-position/offset
join each receive300seconds PER PANEL including domains. Panels may run in
parallel, at most32 CPU workers. Retain at most100 observed models per panel;
reaching the cap, timeout or recursion/resource failure means UNKNOWN, retaining
any found witness. All20 index values must be excluded for COMPLETE_UNSAT.
COMPLETE_SAT requires exhaustive enumeration below the cap. Finite solution
families are compared independently; a witness is replayed character by
character even if enumeration remains incomplete. Source plaintext and modern
edition bodies remain local; public output stores IDs, hashes, finite keys,
domain certificates and numerical summaries.

UNSAT closes only this source-pool/message/channel conjunction. SAT is exact
compatibility; all-solution agreement could motivate a separately registered
held prediction, not immediate translation. UNKNOWN parks this test. No source,
word boundary, control rule, coverage or optimizer repair follows automatically.
GDT895 and604 remain closed; their flat-code failures were not evidence against
this state-dependent channel. Scientific meaning/held/null gates remain intact.
