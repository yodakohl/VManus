# Finite proof for arbitrary fixed tails

Index each of22source letters by its distinct first output drawing g. Its
unknown code is C_g=g+s_g, with arbitrary finite s_g. Different initials imply
prefix freedom automatically, hence a deterministic left-to-right parse once
a table is fixed. Group beginnings and endings are code boundaries by contract.

For a partial table, parse from every group beginning until mismatch, end, or
its first unassigned head. A mismatch rules out every completion of that partial
table. Otherwise every reached remainder beginning with the same g must start
with C_g. Its only possible values are the nonempty prefixes of their longest
common prefix. Enumerating those lengths loses no completion. Assignment
strictly decreases the number of unassigned heads, so at most22decision levels
are possible. No internal boundary is inferred without the preceding assigned
codes. Whole-word end constraints are retained, including rare singleton groups.

At a full successful parse, arbitrary codes for never-used heads cannot create
observed redundancy. The positive criterion needs a code longer than one that
was actually used. A branch tree with every possible prefix child and only
contradiction or identity-only leaves proves that all used codes are singletons.
A positive table is checked against every selected form; it remains an opaque
formal spelling and supplies no correspondence with an actual language.

Runner uses recursive working-unit parsing and a prefix-domain backtracker.
Validator independently reconstructs eligibility with a regex tokenizer and
replays the certificate with explicit remainder lists. Binary tiny universes
are exhaustively compared to all distinct-first finite tables before target
output. Independent implementation by the same root is not independent human
or semantic confirmation. Producer reviews the theorem without target counts.
