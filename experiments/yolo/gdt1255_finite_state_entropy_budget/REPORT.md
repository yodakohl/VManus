# GDT1255 — two-state letter writers fail the fixed Deot comparison

**ALL_AT_MOST_TWO_STATE_FIXED_SOURCE_WRITERS_EXCLUDED.** Every deterministic
writer with at most two complete states, fixed injective output rows and one
source letter per output sign exceeds the unchanged1228conditional-entropy
ceiling for this complete source projection. This includes alternating two
alphabets and arbitrary two-state transition rules, not just a fitted key.
It excludes neither Hebrew nor meaningful Voynich writing in general.

The new step is a conditional model-class bound using old validated source
statistics. No new manuscript measurements, words or cipher keys were obtained.

## Why a small state has limited effect

Choose a within-word adjacent pair uniformly. Let P,X be the preceding/current
source letters, S the complete state before P, and Z,Y their written signs.
With Z=f_S(P), current state T=g(S,P), and Y=f_T(X), both Z and T are fixed
once(S,P)is known. Every output row is injective. Hence

```
H(Y|Z) >= H(Y|Z,S,P) = H(Y|S,P) = H(X|S,P)
       = H(X|P) - I(X;S|P) >= H(X|P) - log2(K).
```

This holds for the actual finite empirical pairs, without stationarity or
independent-character assumptions. Two states can reduce this quantity by
at most one bit. A fixed unknown key does not supply additional varying state.

| Entire fixed source orientation | Source H2 | Two-state output lower bound | Greatest allowed native H2 | Smallest exclusion margin |
|---|---:|---:|---:|---:|
| Logical |3.683285179|2.683285179|2.621689042|0.061596137|
| Reverse each source word |3.695099300|2.695099300|2.621689042|0.073410258|

All values are bits per within-word pair. The greatest allowed ceiling is
IT2a's largest old scoreable value plus the unchanged0.30allowance. RF1b and
ZL3b have lower ceilings; both orientations exceed every reader's ceiling.
This uses all eight scoreable cells/1024dependent samples per reading, not a
favorable pooled reference. Smaller no-capacity cells remain explicitly open.
The source remains the same6288word bare Deot edition projection. Point removal,
final-letter folding, source genre and editorial limitations are inherited1228
conditions, not claims about an identified Voynich original.

## Scope that matters

The entire varying control must fit within the two states. Output rows and
within-word state update rules stay fixed. State may reset or change by a
public convention between words; these boundary transitions are not counted
pairs. A source-dependent entry state does not invalidate the bound because
state/source correlation is allowed, although a usable reader would need that
entry information. Extra uncounted position, lookahead or random controls,
internal external resets, omitted/expanded letters, additional control signs,
whole-word abbreviations or altered word boundaries are outside the contract.

This is an exclusion under a fixed operational comparison, not an independently
calibrated significance claim.1223/1225's sampling warnings remain. It does not
prove that the Voynich writer had three states, that a three-state system fits,
or that another source has the same entropy. No automatic state expansion,
source replacement, tolerance change or key optimization follows.

1230's previous-source-letter bound used source triples and a different state
restriction. Its result remains separate.1202alreadyexcluded the four fixed
recipe sources with at most two whole-word aliases; this is not their rerun.
The old001periodic searches and all their historical scope limits remain.

## Concrete check and validation

The one-bit bound can be attained: write source words AA,AB with fixed state
within each word, toggling state at the word boundary. Row0maps A/Bto0/1,
row1maps A/Bto1/0. The output is00,10. Source pair entropy is1bit and output
pair entropy0. This invented example is not a Voynich assignment.

Root derived the inequality; the bounded producer independently checked the
algebra, resets and sharp example without computing source/native results.
The runner checks9216tiny ternary two-state machines on one frozen invented
message. A separate validator reconstructs every finite encoding and inverse,
uses joint-minus-marginal entropy, and separately checks cached margins with
50-digit Decimal arithmetic. It also verifies the sharp example and a
noninjective constant-output countercontrol, which violates the claimed bound
when the injectivity premise is removed. PASS validates software/cached
arithmetic; the proof, not the fixture count, covers the entire model class.

Input result hashes match1228/1230original manifests. Registration lock at
2026-10-07T11:32:53.405797+00:00preceded mechanical evaluation; cached numbers
and the resulting expected sign were already known. No blind discovery claim.
No new source or target query, image, reserve, f84/f84r or f116v access.
Local checkpoint under4Octoberinstruction, no commit/push. The user-requested
five-hour work block continues; this bounded result is not the final session.
