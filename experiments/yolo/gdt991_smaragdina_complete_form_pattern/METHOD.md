# Complete role-form pattern, unchanged underlying source

This is a necessary-consequence test of GDT990, not a new source, decoder, frame
rule or longer cvc5 run. Every GDT990 source tree, order and uncertainty remains.
The 32,376 old rows are all retained; the 1,980 unretained whole equations are the
only new pattern jobs. Source-unknown and necessary-contradiction rows are never
silently discarded or reclassified as new results.

For every source event, its symbol is the ordered pair (root, argument slot).
The same pair must always emit the same nonempty surface string. A different
slot may emit a different string for the same root; distinct pairs may share a
value. All singleton positions remain present and nonempty. The full emitted
stream equals the whole paragraph. Each original word seam must coincide with
a form end. A form never crosses a seam. No source position, target character,
background group or paragraph remainder is omitted.

Every original code induces such a pattern by value(root,0)=root and
value(root,r)=P[r]+root+S[r]. Therefore pattern exhaustion contradicts the original
code. The converse is false: a pattern can fit while distinct roots collide or
no common frame factorization exists. Such a fit is not an original code.

## Direct finite matching

Encode the fixed words with a separating vertical bar, a character absent from
all eligible words. At the first occurrence of each pair, capture one or more
nonseparator characters. Later occurrences use that exact capture. Allow a bar
only between forms. Full matching consumes the entire target. This expression
represents exactly all possible nonempty role-form assignments within words.

Before each form, two sound lookaheads constrain the remaining text. There can
be no more remaining word separators than remaining forms minus one; there must
be at least one remaining nonseparator character per remaining form. These are
only search pruning, not additional writing assumptions. They are especially
useful when every remaining word must contain exactly one form.

The primary implementation uses installed regex2026.4.4, shortest-first capture
choices and a five-second matching limit per case. The independent checker
constructs the reversed event order and reversed target words, uses ordinary
Python re with longest-first choices, and is bounded externally at ten seconds
per primary negative. Exhaustion, timeout, external interruption and errors are
distinct. No timeout is called exhaustion. Maximum24workers; a shared absolute
15-minute limit begins with the first target run and also caps subsequent
reverse validation. Unstarted work stays unknown. Jobs are saved to an append-only
result journal immediately as they complete. Assembly from a journal does not
rerun any matcher.

## Can the saved pattern witness be a complete original code?

For each nonzero argument slot, enumerate every common prefix and common suffix
of its saved surface values whose combined length leaves a nonempty core. The
slot-zero strings directly fix bare roots. All appearances of a root must have
the same remaining core, and cores of distinct roots must be distinct globally.
There is no prefix-free requirement. Each successful assignment is replayed on
every source event and every target character and seam.

This finite factorization only concerns the **first saved pattern witness**.
At most100000search nodes/two seconds are used. Its outcomes are a full original
code witness, no factorization of this particular witness, or a factorization
limit. A failed factorization does not reject any other possible pattern
witness; no post-result enumeration of further matches is added. A witnessed
code is not unique, either as factorization, across patterns, source branches
or writer orders. No lexical value is claimed fixed. Full values and alignment
are saved, with these unresolved alternatives explicit.

## All-case decision and validation

The independent checker replays all positive pattern strings, checks original
code conditions for every factored witness, verifies all inherited statuses and
case identities, and reconstructs source streams independently from the trees.
Primary negative cases receive the reverse check. If that check finds a witness,
validation fails; if it reaches its limit, the primary exhaustion is reported
as not independently corroborated. The final table separates corroborated
contradictions from all remaining computational and source uncertainties.

All 5,100 small two-symbol/two-character streams and word partitions are compared
to a separate exhaustive cut oracle before target use. Whole-source controls
cover all six branches and four orders, with nonempty frames and a changed
repeated value. A colliding-root pattern must remain a relaxed positive while
failing original factorization. A seam through a form must fail.

The source/writer signatures are grouped before fitting by the complete anonymous
(root,role)-equality pattern. Equal signatures have the same formal predictions;
root names or English gloss differences cannot be selected by this matcher.
The original THELESM secret/treasure semantic ambiguity remains regardless.

If at least90%of the1,980open cases remain unresolved at original-code level,
stop this computational branch. No third algorithm, small added projection,
longer runtime or repaired source is automatically selected for any outcome.
A new contradiction closes its fixed case; a full code is a conditional whole
reading, not a confirmed word. No search-wide null or independent meaning test
exists. All targets were exposed; editions are alternate readings of one
manuscript. Independent confirmation capacity0; reserves, f84/f84r/f116v closed.
