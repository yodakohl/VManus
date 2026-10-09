# Explicit implementation correction after first filter output

The first1192filter represented length bins only through the source pool maximum9, omitting constant native target bins10–12 from its TV sum. It returned zero survivors even under this optimistic lower TV bound. Thus its negative necessary-capacity implication was sound, but calling the computed TV exact was incorrect. No full candidate was evaluated or selected.

The corrected histogram width covers both source and target maxima; original source/criteria/order/cap are unchanged. V1runner,lock,filter andresult remain retained. A new binding lock records corrected code; independent full-histogram matrix reconstruction checks every pair instead of reusing the two-bin shortcut. This is an explicit engineering correction, not a new source test or a criterion change.
