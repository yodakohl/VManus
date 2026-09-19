# Exact existential extension of every old code/page row

SPEC derives each gap and tail from all occurrences of the four selected atoms
in unchanged GDT963 SOURCE. All omitted occurrences have minimum length one.
Known separators have already been removed by the old contract. No new target
construction, source alias, key or transcription is introduced.

For fixed codes, earliest nonoverlapping matching after every required minimum
gap is complete: an earlier match leaves at least as much room for later events
and the tail. The initial zero gap anchors the first name at position zero.
Every subsequent selected gap and every tail is positive in these projections.
Saved positions are witnesses, not constraints on other possible alignments.

## Finite search and completeness

IRIS/XIPHION are fixed by the old row. Search a pair (l,b) of nonempty prefixes
of possible LEAF/BROAD strings. Both values occur in I.1 and IV.20, so roots
are every ordered pair of their common single characters. Use breadth-first
traversal, sorted roots and children; no semantic ranking. A child appends one
character to one variable, drawn from exactly the common successors of that
prefix among all substring occurrences in both fixed pages. Each path is finite
because it remains a substring of finite pages.

Reject a node if either value begins with a complete fixed name code. No longer
extension restores prefix-incomparability. Otherwise test both local whole-page
projections and all I.2/I.3 pages, requiring four distinct physical leaves. If
no completion exists for these prefixes, no longer pair can work: shortening
any eventual true values back to these prefixes preserves the matched starts;
freed suffix characters increase subsequent positive gaps or the positive tail.
Omitted occurrences can absorb that extra length. This proof uses the necessary
relaxation only, not the full omitted-code equality/prefix constraints, exact
occurrence counts, zero internal gaps or fixed event lengths.

If a feasible state has four pairwise prefix-incomparable values, it is a valid
partial witness. Otherwise extend LEAF when it prefixes a fixed name; else
BROAD when it prefixes a fixed name; else the shorter of LEAF/BROAD when one
prefixes the other, with LEAF first on equality. Every valid descendant must
extend that offending value. The branching therefore loses no feasible solution.
Finite exhaustion excludes only this old row; CPU/wall limits produce UNKNOWN.

## Output and verification

Store all 8,990 statuses. For SAT save one deterministic four-value witness and
every matching Acorus/Meum page participating in a distinct-leaf completion for
that dictionary, both local alignments and the exact factored count. One saved
witness is not exhaustive LEAF/BROAD identification. For UNSAT save every visited
prefix node, its reason and full child alphabet; the separate validator checks
all roots, branches and closed nodes. Unknowns have no exclusion credit. An
independent regex implementation verifies certificates without importing run.py.

Thirteen occurrences now share literal values. Six hundred other occurrences
and all untested equalities remain unsolved. Source-unknown and edition-capacity
cases remain unchanged. Proof checking is not semantic confirmation; no p-value.
