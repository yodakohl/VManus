# Independent GDT1040 closure check

The public-gated validator completed PASS at18:00:40UTC. It independently
checked all81 recurrent-category assignments per whole unit (243 rows), all
full-path counts, and the exact longest-prefix and tie-break results. All three
units are FULL_UNSAT; the shared-category joint model is UNSAT. Each best
complete-clause prefix has25 groups. These are syntax results under the stated
relaxation, not readings or semantic confirmations.

The full-run tracked cores are rechecked UNSAT but are not claimed minimal.
They can include late or terminal constraints and therefore do not, by
themselves, locate the first obstruction. A separately labelled post-result
explanation checks the already registered prefix diagnostic with length≥26.
Its inclusion-minimal constraint subsets isolate the same five literal groups
in every source:

`22 chey — 23 daiin — 24 chey — 25 lchedy — 26 qokaiin`

The last two are fixed nouns. To consume group26, its head must be group25
with one argument or group24 with two. Group25 is a fixed noun, so chey24 must
be P2. The global form rule then makes chey22 P2 as well. That head would need
both groups23 and24 to be nouns, contradicting chey24=P2. The argument does
not assign a meaning to chey or daiin and does not depend on a line boundary.
It closes these prefix/arity rules with the inherited noun assignments, not
every grammar or loan interpretation.

VALIDATION_EARLY_CORE.json retains all three source-labelled subsets and
self-contained SMT-LIB UNSAT certificates. They explain a post-result prefix
boundary; they are not a new predeclared falsifier. Minimum cardinality is not
claimed. The registered validator code and all inputs remain unchanged.

The guarded ALL_GROUPS display audit checks all215 rows against frozen SOURCE,
validated prefix lengths, assigned categories and exact seven old denotations:
75 prefix rows and140 unparsed rows (47/47/46), with no dropped suffix and every
`is_full_interpretation` flag false. Its results are in
VALIDATION_GROUP_AUDIT.json. An initial guard invocation supplied comma-joined
allow-values and selected zero rows; the corrected invocation uses eight
explicit repeated --allow flags. No filtering or guard bypass was used.

The early obstruction is additional to the openly predicted qoky and final
chedy/chary obstructions. They are related consequences of one restrictive
model, not independent meaning confirmations. No new meaning, production,
alias, reference repair or semantic execution follows from this audit.
