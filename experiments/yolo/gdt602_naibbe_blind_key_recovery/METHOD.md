# GDT602 method

## Question

Once Naibbe's hidden unigram/prefix/suffix code units are correctly segmented,
can an unknown surface-to-letter key be recovered from ciphertext and an
independent Latin model without using the published key or aligned plaintext?

## Separation of information

The harness uses the pinned published table and aligned Pliny control only to
construct the oracle segmentation and post-hoc truth map. The solver receives
only state-tagged surface IDs, line boundaries, the public 23-letter alphabet,
the public fact that Naibbe has six anonymous tables, and a char-4 model fitted
to independent Caesar. `solve()` has no plaintext, table, or true-key argument.

## Objective

The score is Caesar char-4 log likelihood inside the public Naibbe model class.
Each of U/P/S may assign at most six distinct surface types to one plaintext
letter, because every one of the six tables contains one code for every
state-letter pair. Keys outside that capacity have infinite description
length. Annealing uses swaps and capacity-respecting reassignments, followed by
coordinate/swap polishing.

The comparison removes the capacity. It exhibits the known maximum-likelihood
mode collapse. A separate Markov-type score adds the empirical type-class
multiplicity term and checks whether the recovered output is typical of Caesar
rather than merely a high-probability repetitive mode.

## Decision and ceiling

Recovery requires every seed to exceed 99.9% event-weighted character accuracy
and 98% type accuracy. The result licenses only unknown-key recovery
conditional on the oracle segmentation and the known six-table architecture.
It does not solve hidden segmentation, decode Voynich, or establish a language
or meaning.
