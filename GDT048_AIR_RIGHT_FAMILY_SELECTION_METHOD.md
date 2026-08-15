# GDT048 — AIR right-family selection inside and outside OK

## Question

GDT047 ranks exact residual host `OKAIR` first after subtracting DY closure,
terminal-M/B3, and carrier+D stacks. This experiment asks whether that lead is
specific to the whole host `OKAIR`, or whether it is inherited from a broader
right-edge choice among `AIR`, `AIN`, `AIIN`, `AR`, and `AL`.

This is a formal distribution test. `AIR` is not assigned a sound, morpheme,
part of speech, meaning, language, or translation.

## Frozen construction

Starting from `gdt016_group_state_inventory.tsv`, retain non-DY, non-terminal-M
groups in Herbal A, Herbal B, Stars/Recipe Currier B, and other Currier B.
Retain outer states `NONE` and `q`; the other wrappers are outside this exact
comparison. Parse the longest matching right edge from the ordered set:

`AIIN, AIR, AIN, AR, AL`.

The remaining left string is the base. Thus `okair`, `okain`, `okaiin`,
`okar`, and `okal` share base `OK`. This decomposition is only an operational
comparison family; it is not presumed linguistic morphology.

Primary target is Herbal B plus Stars/Recipe B. Controls are Herbal A plus
other Currier B. Report:

1. exact Fisher comparison of AIR versus the four matched right edges within
   base OK;
2. the same comparison over all eligible bases and over non-OK bases;
3. exact wrapper-stratified inference within OK;
4. leave-one-target-folio-out log-rate ratios;
5. a predeclared log-odds interaction contrasting the OK effect with the
   non-OK effect; and
6. exact base-wise counts, so recurrence is inspectable rather than inferred
   from a pooled number.

The whole-host interpretation is weakened if AIR is independently enriched on
non-OK bases and the OK-versus-non-OK interaction is not distinguishable from
zero. f84r is skipped before parsing or counting.
