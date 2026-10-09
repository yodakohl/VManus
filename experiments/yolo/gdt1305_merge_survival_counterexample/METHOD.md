# GDT1305: minimal token-survival counterexample

## Decision note and budget
2026-10-09, source-free scope clarification, not another native decoder or corpus.
GDT608 retains directed component backoff and stronger exact-unit profiles on
its frozen final BPE tokenization. Its own report explicitly allows an explanation
through graphemic environments and the BPE algorithm; the8October scope review
already rejects inferring universal noncomposition from an ATOMIC win. None of
those positives or qualifications is being rerun or overturned.

Precise small question: can two fixed merge rules on a source with independent
characters and a memoryless word stop create a persistent final-boundary advantage
for the merged-unit profile over its right component? If yes, preserve an explicit
counterexample against requiring lexical exception memory from that observation
alone. If no, do not infer such memory anyway; stop this attempted witness. This
is not a measurement of how much of608's native gap is a tokenization effect.
Smallest adequate work is an analytic construction and exact independent checks;
no simulator fit, decoder, new source corpus, native recount or enlarged control
suite. Inclusive budget12:30–12:50UTC,20minutes for proof, implementation,
validation, documentation and publication. No automatic native followup.

## Fixed source and processing
Nonempty words over abstract A,B,C. First character probabilities1/4,1/4,1/2.
After each character, END with probability1/4; otherwise select the next independent
character with the same probabilities. Mean raw length4. These are abstract toy
letters, not Voynich glyphs or meanings. The source has no lexical memory or
pair-specific continuation parameter; END is independent of character/context.

First replace every adjacent A,B by M. Then replace adjacent M,C by N. Rules
are fixed for the counterexample, NOT claimed to be the first two frequency-
trained BPE rules of this IID source. M and N are new token labels, not meanings.
No overlap ambiguity occurs in either pass. Profiles are counted on final surviving
tokens, analogously to the aspect of608 being illustrated.

Predicted exact expectations per word:
- raw B count1; raw AB count3/16; raw ABC count9/128.
- surviving M count15/128; final M count3/64; final-rate2/5.
- surviving B count13/16; final B count13/64; final-rate1/4.
- before second merge, AB final-rate1/4, matching raw B.

The mechanism is removal of M occurrences followed by C, not a new dependence
in the generating source. At population probabilities, predicting surviving M's
final flag with its own2/5 beats the right-component1/4 by their Bernoulli KL
in bits. This is an expected single-feature scoring difference, not the full
608primary score or a new p-value/held-native test. Independent generated words
share the same population phenomenon, but no experimental holdout is claimed.

## Checks and scope
Primary program computes formulas and exhaustively tokenizes all nonempty words
through length8 with exact weights; finite truncation is explicitly separate
from the infinite source. Independent validator uses a streaming merge transducer
and an exact rational absorbing-state system for infinite expected counts/final
rates. Compare every finite word and weighted sum. Include a no-second-merge
baseline and a fixture showing that absorbed M occurrences were interior.
Input binding is this protocol and the source-free proof note; previous native
reports may be cited but no manuscript token/pixel is newly loaded for the test.
f84/f84r/f116v/reserves remain unopened. Native word meanings remain0.
