# GDT1394: independent source-code gaps, fixed old certificate cohort

Prospective decision note, 2026-10-16, before native code-length counts.
Inclusive preparation/implementation/validation/publication budget: 10:16–11:01 UTC.

IDEA001067 supplies an invertible list-of-unary-instructions code but puts fair,
independent visible gaps between complete codes. Unlike GDT1328 (within-word e/i
runs), this asks whether inter-code word formation can have independent cuts.
The unknown is spacing feasibility, not meanings or source-language identity.
If every head fails, retire this independent-gap serialization. If one survives,
retain only spacing capacity; no lexical roles or content algebra are selected.
At the time limit, stop expansion. Do not repair the decoder or change the model.

## Fixed carrier and scope
For each of the 22 old working units choose a global escape head P. Grant all
21 other singletons and all 21 codes Px (x != P), a superset of IDEA001067's
19 single/19 double atoms plus two unary operators. A P at a group's end or PP
contradicts the carrier. Parse each visible group without moving its boundaries.
Its token count is units minus P count. Source instructions may be arbitrary,
but must be fixed independently of the later cuts; source length cannot depend
on those cuts. We also relax the original syntax and test no action meanings.

Use ONLY the original 23 rank-certificate paragraphs per reader in GDT1259's
published cached CERTIFICATES, crosschecked with its CENSUS and SPEC. No new
selection, full-census raw reconstruction, RF1b, reserved or sealed data. These
are exposed historical paragraphs; ZL3b and IT2a read the same manuscript.
Original source paragraph flags and the unproved 22-unit alphabet are premises.

## Null and exact calculation
Within each paragraph, every complete-token boundary is cut independently
with one constant probability p in (0,1); p may differ by paragraph. All cuts
across paragraphs are also independent. Conditioning on token total N and
visible group total M removes p. Ordered positive compositions of N into M are
uniform. X is the number of one-TOKEN visible groups, not one-glyph groups.
For N>M, count(X=k)=choose(M,k)*choose(N-M-1,M-k-1), with impossible choices
zero; denominator choose(N-1,M-1). For N=M, X=M deterministically. Expectation
is M(M-1)/(N-1), except N=M=1 has expectation 1. Exact integer counts must sum.

Aggregate X over the 23 paragraphs for each reader/head. A fixed lambda grid
0,.05,...,10 gives the valid LOWER-tail probability UPPER bound:
min_lambda exp(lambda*Xobs + sum log E[exp(-lambda*X)]).
Evaluate with log-sum-exp, add 1e-8 numerical safety to log bound, clamp at 0.
Numerical safety is a floating-point precaution, not a formal interval proof; independent recomputation and exact small CDF checks remain required.
No fitted p or native-driven statistic, lambda grid, cohort or threshold changes.

A shape-valid head is SHORTFALL_REJECTED only with >=12 variable paragraph
PMFs on >=10 physical leaves (r/v/foldouts share fNN), Xobs/E[X] <= .75,
and log bound <= log(.01/44). Otherwise NOT_REJECTED or CAPACITY_STOP.
Invalid heads retain a first actual source witness. Reader exclusion requires
every head invalid or rejected; the composite uses the worst (maximum) bound,
not the best head. Joint rejection requires both readers excluded. The 44-case
correction is conservative bookkeeping; readers are not independent replications.

## Dependencies and limits
The cohort was selected earlier for rank and eligibility, not this statistic.
Nevertheless preservation of the conditional gap law under that earlier
selection is an ASSUMPTION, not proved by conditioning on N/M. This is a
conditional fixed-cohort model comparison, not project-wide calibrated evidence
or a logical impossibility for stochastic generation. Layout/width-dependent
cuts, context/serial dependence, different or context-dependent code-length rules, different real units,
paragraph misflags, and other source channels are outside the tested model.
Nonblank line wraps occur only at existing groups; no extra within-group cuts.
A failed spacing channel does not falsify the abstract instruction language.
No words, operations, English glosses or native glyph roles are assigned.

## Freeze and validation
Source-free controls precede LOCK.json. Lock protocol, SPEC, primary, independent
validator and source pins before the native run. The validator does not import
the primary; it computes PMFs by surplus allocation, enumerates all compositions
N<=14 and checks small exact convolution CDFs against Chernoff bounds. It rebuilds
the projection, parses units independently and checks all 44 cases and decisions.
