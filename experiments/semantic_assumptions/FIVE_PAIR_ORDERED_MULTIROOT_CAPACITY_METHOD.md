# Five-pair ordered-multiroot capacity audit

Status before execution: **SCORE-BLIND CAPACITY ONLY**.

## Question

Does the newly fixed fifth Herbal↔pharmaceutical relation remove the two
design blockers that stopped S100: an exact assignment orbit too small to
reach `p <= .01`, and too little genuinely multi-root label support?

This is not S100 and does not run its scorer.  It inspects only relation
identity, label-row metadata, and the number of formal roots in each complete
one-word pharmaceutical label.  It must not use any of the five Herbal target
pages, compute a label-to-page score, inspect a best match, or serialize any
label surface or root identity.

## Fixed relation panel

The four public SNPL001 relations are retained without alteration and the
published `JSP2025_05` f37v↔f102r1 relation is appended.  The five Herbal pages
and five pharmaceutical label loci must be distinct.

The fifth relation and its locus were published while its characters were
sealed.  During the subsequent capacity check, an interactive diagnostic
mistakenly displayed the fifth label surface and formal root sequence to the
analyst.  No f37v prose, label-to-page association, target score, candidate
ranking, or best match was opened.  This exposure is recorded rather than
silently treating the subsequent design as fully analyst-blind.

## Capacity gates

All of the following are required:

1. exactly five fixed relations, five target pages, and five label loci;
2. every label is a strict one-word diagnostic-label row in ZL3b, IT2a, and
   RF1b;
3. the formal-root count of each label is identical across the three alternate
   readings;
4. at least four of the five labels contain at least two formal roots in every
   reading;
5. the newly added fifth label contains at least two formal roots;
6. the exhaustive fixed assignment orbit is `5! = 120`, with minimum inclusive
   one-sided rank `1/120 <= .01`;
7. no Herbal target row or label-to-page score is used.

## Consequence of a pass

A pass authorizes only a new target-blind scorer calibration and a new public
preregistration.  The future primary must use all five relations, require the
true assignment to be unique rank 1/120 jointly and in every alternate
reading, and include a fixed deletion of the singleton label.  That four-way
view can only reach 1/24, so it is a robustness check requiring unique rank 1
and a positive margin, not a second `p <= .01` result.  Synthetic null,
wrong-pairing, one-relation, one-reading, concentration, parser mutation, and
independent reconstruction controls are mandatory before target access.

The old S100 scorer remains prohibited.  No result here can name a plant,
component, word, sound, language, cipher, plaintext, meaning, or translation.
