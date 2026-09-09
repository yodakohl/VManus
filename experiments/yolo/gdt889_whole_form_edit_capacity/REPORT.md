# GDT889 — One-edit correction leaves at most20 messages

Among the749 fixed valid whole forms,730 must encode one identical message
under guaranteed context-free correction of any single insertion, deletion or
substitution. The remaining19 forms are singleton components. Thus the exact
maximum is20 distinct messages. An injective code is impossible on this scope.
The730-form component covers1,598 of the1,617 original group occurrences;
each isolated form occurs once. These are mathematical consequences of the
hypothesis, not claims that those Voynich words actually mean the same thing.

Two centres whose radius-one edit balls intersect must have the same decoded
message. Transitive closure propagates that equality across the large component.
For example, both `cheol` and `chol` can produce `ceol` in one deletion or
substitution. A context-free decoder cannot recover different messages from
that identical received string. Longer chains force equality even between
forms separated by more than two edits.

The producer constructs edit balls explicitly and publishes729 witnessed forest
edges. A separate implementation checks all280,126 distinct pairs with exact
Levenshtein dynamic programming, finds9,469 distance-at-most-two edges, and
recovers exactly the same20 components with BFS. Every forest witness passes.
Both implementations were written and run by root; this is algorithmically
independent verification, not a second human/source observer. Source-free
fixtures and an additional961-pair short binary-string check passed before fit.
Preregistration was public in d12ac9ca before the target computation.

The unchanged source is GDT883's all-three-concordant odd-leaf cache. No new
transcription, even leaf, image or sealed material was accessed. Different
readings are not independent manuscripts. Boundaries are supplied externally.
All observed spellings are assumed valid codewords, not existing scribal errors.

The20 bound is tight for this finite codeword set: assign one distinct message
to each component and decode the union of its error balls accordingly. These
unions do not overlap across components. Additional valid forms can only merge
classes and lower the bound. Without an independently required message count,
the noninjective hypothesis remains possible. Contextual correction, restricted
error types, actual scribal corruption and different written units are outside
this test. No translation or general rejection of redundancy follows.

Reproduce with the run and validate commands in experiment.json. The exact words,
components, collision witnesses, source hashes and validation are published.
