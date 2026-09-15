# GDT962 — fixed BPE units in the complete Behenian roster

Exploratory follow-up after full GDT960/961 exposure. No old experiment changes.
Use all22 fixed GDT960 windows, both source directions, both MATERIAL and
PLANT_IDENTITY source tables, and every32/34 plant name. The only new
hypothesis is that a plant is marked by a unit of the already frozen GDT605
parser rather than by an unchanged whole word or context-free raw substring.

Two fixed representations: FINAL_UNITS and ALL_TREE_NODES. Apply the exact
nine ordered GDT605 character collapses, then all64 frozen BPE merges in their
old rank order, left to right per merge. FINAL_UNITS retains every final token;
ALL_TREE_NODES retains every actually instantiated leaf/internal node of those
tokens. No new merges, frequency filter, chosen prefix, spelling correction,
language model, parser learning or old word glosses. Candidates are restricted
to the fixed98-unit GDT605 inventory in both representations.

Read only GDT960 ALL_WINDOWS.json.gz, already admitted and exposed. Reconstruct
hard chunks within each physical line: join successive groups exactly when the
intervening separator is UNCERTAIN_SMALL_SPACE. Every other separator, including
a drawing interruption, breaks the chunk. Preserve raw groups, IDs and boundary
classes. A chunk is known only if all raw groups are [a-z]+ and its outer
boundaries are LINE_START/LINE_END/DEFINITE_SPACE/DRAWING_INTERRUPTION. An
unaligned drawing boundary or nonliteral group makes the whole chunk UNKNOWN.
Do not select bracket alternatives or delete unknown signs. This raw adapter
is explicitly more conservative than GDT605's old cleaned-text intake; the
ordered collapse/merges themselves are unchanged. It differs from GDT960's
wholeword boundary test because uncertain spaces are joined by the preexisting
GDT605 rule. List every changed-knownness group in a separate audit.

For each of176 cases, all5808 source-plant predictions are frozen before parsing.
For each unit, retain its observed fifteen-paragraph incidence mask including
zero and group identical masks without losing unit names. Every source plant
requires a distinct unit whose presence is biconditional with source incidence.
A known-mask candidate has exactly that observed mask; this is not confirmation
of absence in UNKNOWN chunks. An upper candidate has no known extra row and
an UNKNOWN chunk in each missing required row. No unbounded fresh unit is added.
List every plant's complete known/upper domains, missing rows and contradictions.

Compute maximum bipartite matching for the complete plant roster, separately
for known and upper domains. A deficient matching rejects the corresponding
necessary condition even if each individual domain is nonempty. A full matching
only passes a necessary condition: UNKNOWN chunks have unlimited abstract unit
capacity in this upper bound, and no jointly realizable full unknown string is
claimed. Retain one deterministic witness and every marginal domain, not a
preferred dictionary. All marginal domains are local necessary domains, not
claimed jointly extendable values. No significance or GDT388 evidence score.

No new data, image, selector or reserved page. Five previously exposed physical
leaves, overlapping windows; alternate editions are not independent. Independent
confirmation capacity is zero per candidate. f84/f84r remain sealed; f116v and
reserves closed. Confirmed meanings remain zero regardless of formal matches.
A complete candidate licenses only a later separately registered content test;
no complete candidate closes this fixed98-unit plant-marker model on this scope.
No automatic parser extension, new plant aliases or part-rule rescue follows.
