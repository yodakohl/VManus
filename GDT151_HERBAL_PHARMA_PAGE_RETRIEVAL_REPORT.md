# GDT151 — complete Herbal-to-pharmaceutical page retrieval

## Outcome

**HERBAL_PHARMA_PAGE_HOST_RETRIEVAL_NOT_SUPPORTED**

The mechanically complete cached human catalogue contributes **32** Herbal to
pharmaceutical drawing references. Thirty-one are scorable as full-page bags
against all **15** pharmaceutical pages; f37r to f101v is preserved but has no
GDT062 pharmaceutical page bag.

Exact PAGE_HOST frequency performs poorly: MRR **0.1770**,
mean rank **8.52/15**, and **6/31**
top-three targets. PAGE_HOST character trigrams are similarly weak. The simple
group-count control reaches MRR **0.2244**, while a
leave-source-out target-degree prior reaches **0.3240** and
**13/31** top-three targets. No formal representation
beats that adversarial nontextual control.

This is a direct generalization failure for the selected GDT148 relation lead.
The six-pair Herbal-to-Herbal result remains an interesting exposed pattern,
but complete cross-section fragment references do not behave like transferable
PAGE_HOST content addresses at page resolution. The negative has an important
limit: each pharmaceutical page contains multiple fragments, and most lack
singular text ownership, so a real fragment code could be diluted beyond
recognition by the complete page bag.

The 100,000 target-label worlds preserve catalogue target popularity and the
two-edge source structure; maximum-over-six tails are reported rather than
used to rescue a representation. No plant or component identity, semantic
role, gloss, word, morpheme, POS, sound, language, plaintext, meaning, or
translation follows. f84r was not retained, joined, scored, or targeted.
