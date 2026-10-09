# Left prefix quotients and a necessary size bound

If u and u r are concatenations of a prefix-free table C, decoding u r starts
with the entire decoding of u, hence r is a concatenation too. Repeatedly add
nonempty r. Every addition is a suffix of an original word; closure is finite.
This theorem does not hold for all uniquely decodable codes (C={a,ab}), and
right cancellation is invalid (C={a,ba}). It is not a word-meaning inference.

In closed R, let H be first signs and F singleton strings. Every h in H needs
at least one h-headed code; every f in F is a singleton code and cannot head
a longer code. If ab is in R, singleton a implies singleton b. Thus a supposed
long-code head g forces every predecessor N_g in this two-sign graph to be
non-singleton. For each such h, distinct second signs d_h require at least
max(1,d_h) different h-headed codes. Put K=H union {g}, including g outside H.
The total necessary bound is |K|+sum over N_g of(max(1,d_h)-1). Intersecting F
is impossible. Minimize over all occurring g, never only word-initial heads.
This is a lower bound, not minimum-size optimization or a positive table.

The members P of R without a proper prefix in R form a prefix-free basis.
Any r in R factors over P by repeated prefix quotient. W subset C* iff P
subset C*. If F contains every used working sign, no longer code can be used
at any table size. Otherwise P supplies some nontrivial formal table, possibly
large and fitted to native input; no source language or practical writer follows.

Root implementations differ: runner derives parent-linked closure in rounds;
validator replays exact equalities, then checks every cut against a fixed point
and independently computes all obligations. This is independent code by one
researcher, not independent transcription or historical confirmation.
