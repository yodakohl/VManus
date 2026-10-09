# Necessary subcodes without instantaneous segmentation

Let S be exactly the working signs whose one-unit strings belong to C. Every
one-unit whole word forces its sign into S. A complete two-unit word ab has
only two nonempty unit factorizations: [ab] or [a,b]. If either singleton is
absent, ab itself must be a codeword. Thus B(S) is contained in every candidate
C with that exact singleton set. A subset of a UD code is UD: any collision in
B would remain a collision in C. Enumerating all S containing W1 is exhaustive,
regardless of the unbounded lengths of other codewords. If S contains allA,
any longer code collides with its singleton spelling, so only identity remains.

For any h not in S, a word starting h must begin with a code at least two units
long. Different second units require different h-headed codes. Let d_h count
these actual whole-word branches, and b_h the already counted B entries with
that head. Add max(0,d_h-b_h) for each such h to |B|. Heads are disjoint, so no
entry pays twice. Because allAunits occur and properS omits one, at least one
longer used code exists; |C|>=|S|+1. Heads IN S may also have longer codes: do
not copy the prefix-free prohibition into this proof. Full-table extra costs
and additional full-word contradictions are optimistically ignored.

The minimum necessary bound across every UD B(S), S proper, cannot exceed the
true minimum if a full nontrivial code exists. It need not be attainable. A
collision-free short subcode is not a parse of all original words. Counts of
source entries, not glyph-frequency or language values, are being bounded.

Runner explores residuals with explicit pairs of different codeword sequences.
When equal concatenations are reached it saves a collision. Exhaustion saves
the closed residual set. All nonempty residuals are proper suffixes of a code;
B lengths are at most2, so those residuals have length1. Validator separately
uses general unoriented residual-set closure and direct collision equality.
Controls compare the bound with all binary UD tables length1..3 before target.
Independent same-researcher code is not independent palaeography or semantics.
