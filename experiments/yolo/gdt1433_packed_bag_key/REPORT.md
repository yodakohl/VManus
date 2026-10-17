# GDT1433 — preparation improved, actual controls still stop the test

**CONTROL_STOP_NO_NATIVE_SEARCH.** Both actual32-group positive controls reach
the solver but return UNKNOWN/timeout. The registered gate therefore forbids
the native59-group search. Native cases:0. No key or word candidate, manuscript
finding, transposition-family exclusion or translated word was obtained.

| Measured stage | Packed bitvector | Packed integer |
|---|---:|---:|
| Preparation |0.834990s|0.799122s|
| Solver call |22.106560s|20.069810s|
| Complete control call |22.946193s|20.872051s|
| Result |UNKNOWN|UNKNOWN|

The solver timeout parameter was20seconds in both programs. It is a Z3 soft
limit, not an external hard kill; the primary actual call overshot it by about
2.1seconds. No runtime is presented as a strict20second total. These UNKNOWN
results do not contradict the directly verified planted positive certificate.

## Exactly what changed

GDT1431stopped both builders at20second preparation caps before either solver.
This separately selected implementation represents the SAME count constraints
as one carry-free packed equation per candidate word. Sourceletter variables
remain single nonzero unit powers; mergers allowed, no deletion or splitting.
Base must exceed wholeword length including merged counts. The observed maximum
source/control length14uses base16/88bits in the primary and base15/unbounded
integers in the secondary. Equal sums have equal22digit counts without carry
or overflow under this contract. Both new builders finish in under1second.

That is an engineering improvement; solving remains beyond the declared budget.
It does NOT supersede the old1431stop or turn a stopped native test into a pass.
The original1431files and1427/1430FWD/REV failures remain unchanged.

Scientific inputs are byte-identical1426:2133Syriacforms/23sourcecodepoints,
all59IT2af75v.38–42groups,22workingunits, one global SOURCE→unit function and
arbitrary occurrence-specific within-word permutations. The chosen edited
medical reference is not an identified Voynich language. The broad transposition
question remains OPEN for precisely this finite vocabulary/key/group contract.

## Registration, development and checks

Public preregistration `ed29116d960ca98c2124ab57fd4c9ccfcc16f818` was independently verified at
2026-10-17T14:57:17.181330+00:00, before either actual control. LOCK binds the complete
protocol, both implementations, unchanged inputs, predecessor sources and
source-free development receipts. No actual control/native search preceded it.

Primary50tiny cases matched exhaustive function enumeration, including two
22unit high-bin cases with66/132bit widths. The separately written integer
engine passed40complete function cases plus9named checks; its initial empty-domain
handling was corrected before lock and disclosed. Neither toy suite nor the
known planted certificate substitutes for the actual control-search requirement.
Both implementations use Z3: this is representation cross-checking, not an
independent solver backend. The primary builder is not imported by the secondary.

Static validation reuses ONLY the pinned1431input reconstruction/direct certificate/
inverse helpers. It recomputes W from346cached source records (5768tokens/2133forms/23letters),
reconstructs the original32control words/key and59raw native groups/units,
and does not independently retranscribe the original SyriacXML.
It checks the positive planted certificate, both saved control timeouts, zero
native searches and publication-before-execution. It does not rerun a solver.
PASS means accounting/provenance, not native capacity or a historical reading.

## Stop boundary

End this implementation here, with no third encoding, cap increase, sourcewordbook,
unit/boundary change, target subset or post-result repair. No native search is
permitted after this gateSTOP. No word profile or inherited gloss was used to
assign a meaning, and no new source corpus, raw mixed TSV, image or reserve was
acquired. Existing179text selectors and sealedf84/f84r/f116v boundaries stand.

This answers a technical feasibility question only. It provides no translation
progress and does not narrow the manuscript's linguistic search space. A new
scientific selection must have a genuinely different motivated content/writing
consequence; it cannot be a third attempt to repair this stopped solver.
0confirmedtranslatedwords. Inclusive14:46:14–15:31:14UTC covers preparation
through final publication; actual elapsed is recorded in the active state.
