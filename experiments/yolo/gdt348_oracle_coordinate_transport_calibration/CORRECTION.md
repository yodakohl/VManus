# GDT348 result-status correction

The first scorer invocation stopped before result output because the local
variable `p` was reused for a coordinate pair and then formatted as a number.
Only that variable name was corrected before the first successful score.

The first successful score then assigned `ORACLE_CALIBRATION_INCONCLUSIVE`
because its decision branch compared the in-memory integer `comparable` flag
to the string `"1"`. The published TSV rows showed all three panels as powered
and comparable, and all three frozen graph gains were negative. The mechanical
predeclared branch is therefore `ORACLE_MANUSCRIPT_SPECIFIC_RETAINED`.

The correction changes only the type-safe status comparison. It changes no
source split, crosswalk, state, transition, marginal, graph weight, codelength,
exact recovery, edge decomposition, null world, p-value, or claim ceiling.
No pre-correction result was committed or pushed, and no f84 input was used.

While binding this correction into the result inputs, one invocation stopped
at Python parse time because the edited result assignment had one extra space
of indentation. Removing that space was implementation-only and occurred
before any further score or artifact rewrite.

The independent final validator then found that nine-decimal TSV formatting
rounded one lexical-A null world onto the reported observed score, making the
inclusive tail unreconstructible from retained rows. Numeric score and null
fields were therefore regenerated at 17 significant digits. The underlying
doubles, world ordering, exceedance count, p-value, and decision are unchanged.
