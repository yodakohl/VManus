# GDT114 — Q20 OPEN-to-BODY record-template linkage

Status: `EXPLORATORY_YOLO_FIXED_MODEL_FAMILY`

## Question

Q20OB001 already found that an OPEN's literal member/family/group inventory did
not improve its own BODY string code: every fitted cache weight was zero.  This
experiment asks a different question implied by GDT113.  Does the OPEN predict
the BODY's **HPR2 record-template profile** on a completely unseen physical
folio, after record shape and the other BODY records on that held folio are
already available to the baseline?

OPEN and BODY mean first physical line and subsequent physical lines of an
already human-delimited star record.  They are not headings, recipes, or
semantic fields.

## Panel and sealed material

Reuse the 170 Q20OB001 records on eight physical folios (`f104`, `f105`,
`f106`, `f107`, `f112`, `f113`, `f114`, `f115`).  ZL3b is primary; IT2a and
RF1b are alternate-reading sensitivities of the same manuscript.  The parser
is the already published GDT062 HPR2 projection.  The source alignment is
stream-filtered to the registered Q20 loci before formal values are retained.
Any `f84r` row is rejected before parsing.  f84r is not opened, retained,
queried, joined, scored, targeted, or assigned a prediction.

## Fixed representations

For each OPEN and BODY, calculate normalized counts of:

- wrapper classes `q,d,s,ch,che,sh,t`;
- `O` and `OT` local frames;
- any RIGHT_FAMILY, DY and B3;
- the final source-display character of PAGE_HOST over a fixed 26-bin ASCII
  alphabet plus an OTHER bin;
- mean PAGE_HOST length and exact-host diversity.

The BODY vector is the fixed prediction target.  Five OPEN representations are
compared:

1. `COMPILER_ONLY`: wrapper/frame/RIGHT/DY/B3 rates;
2. `EDGE_ONLY`: PAGE_HOST final-character rates, mean length and diversity;
3. `FULL_HPR2`: compiler plus edge features;
4. `RAW_CHAR3_HASH32`: state-blind source-display character trigrams;
5. `HOST_CHAR3_HASH32`: PAGE_HOST character trigrams.

The hash features use SHA-256 modulo 32 and are fixed before scoring.  They are
string controls, not decoded text.

## Nested held-folio prediction

Hold out one physical folio at a time.  A nuisance model sees record line count,
OPEN/BODY group and member counts, page-side, normalized record ordinal, and a
leave-one-record-out mean BODY profile computed from all *other* records on the
same folio.  That last term is an adversarial page/following-text control.

Each candidate adds one frozen OPEN representation.  Multi-output ridge
regression predicts the standardized BODY template vector.  Ridge strength is
chosen only inside the seven training folios by inner leave-one-folio-out
cross-validation from `{0.1,1,10,100,1000}`.  Held gain is the reduction in
unit-variance Gaussian squared-error code,
`(SSE_nuisance-SSE_model)/(2 ln 2)`.  Because dimensions overlap, this is a
comparative pseudo-code score, not a literal lossless manuscript code.

## Pairing null

In each held folio and edition, permute complete OPEN representations only
within exact OPEN-member-count strata.  BODY, folio, page ecology, record
length, other-BODY profile, and the multiset of OPENs remain fixed.  Use 4,096
SHA-seeded worlds, the same assignment world for all five models, and report
inclusive local and max-five p-values.  One-sided arrays/strata remain valid
observations but provide no pairing permutation capacity.

## Interpretation

This is exploratory hypothesis generation.  Positive gains rank a candidate
record linkage; they do not establish semantics.  A useful result requires a
positive selector-paid FULL_HPR2 gain, positive gain on at least six of eight
ZL3b folios, positive direction in all three readings, a max-five p at most
0.05, and performance above both hashed-string controls.  Missing any gate is
reported as weak/local or absent, not used to stop future YOLO exploration.

No word, morpheme, POS, sound, language, plaintext, meaning, translation,
recipe, heading, or semantic role is assigned.
