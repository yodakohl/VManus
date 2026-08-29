# GDT625 method

## Question

Can ordered local uses of the GDT624 quality family support concrete operations
such as moistening or drying, and which intervening or attached surfaces name
the processed plant part?

## Route and scope

The route was duplicate-screened before registration. GDT623 and GDT624 are the
current semantic inputs. GDT437 and GDT557 were read only as older order/scope
comparators; their English state-machine wording is not imported as plaintext.

The canonical 179-page GDT624 allow-list is reused. It excludes f1r and every
f84 selector. The mixed token and cross-reading tables are materialized only
through `./vmanus-exp query-tsv`, with every allowed page named explicitly and
with both `--forbid-prefix f84` and `--forbid-prefix f84r`. No new image page is
opened. Manual judgments are restricted to the eleven previously opened
Herbal images listed in `MANUAL_VISUAL_JUDGMENTS.tsv`.

## Terminal quality family

The exact productive 48-cell grid remains the registered core. For local
sequence work, a larger terminal family is admitted:

```text
PREFIX + {k,t} + {ch,sh} + [e?] + [d?] + y
```

`PREFIX` may be empty and is preserved verbatim. Parsing is terminal: no
internal substring is silently discarded. The inherited working atoms are:

```text
k = hot       t = cold
ch = dry      sh = moist
```

Every exact occurrence is counted once. A conservative cross-reading witness
is the minimum identical surface count on the corresponding ZL3b, IT2a and
RF1b line; this is a stability audit, not three independent observations.

## Ordered pairs and paths

Within each page, terminal-family occurrences are sorted by physical line and
token index. A pair is retained only when the second occurrence is the next
quality-family occurrence and lies on the same line or the immediately next
physical line. Each pair records state direction, line distance, shell
compatibility, intervening tokens, local anchors and reading stability.

Three consecutive local occurrences form a cycle only when thermal value is
constant and moisture follows A-B-A. A state path receives an operation gloss
only conditionally:

```text
dry -> moist        = moisten/soak, if the same carrier is retained
moist -> dry        = dry, if the same carrier is retained
dry -> moist -> dry = soak and then dry, if one carrier spans all states
```

Adjacent antonymic quality forms without a common carrier remain a contrast or
two-part description.

## `cth-` role extraction

All safe-panel surfaces beginning `cth` are enumerated. For `cthy` and
comparison terms, the builder measures section, page and locus distribution;
three-reading stability; line position; same-line contacts with `shor`, `chor`
and `dair`; and strict immediate contacts with terminal quality forms.

The manual image pass ranks `cthy` as leaf drug, aerial herb, generic plant
part, or grammar. "Blattgut/Blattdroge" is selected because it explains the
Herbal restriction, repeated `chor/shor` proximity, bidirectional
quality-to-carrier syntax, and the opened leaf-rich folios. It is deliberately
broader than a single anatomical leaf.

## Historical comparator

Wellcome MS 542 and MS 541 show the mixed architecture sought here: learned
drug and plant names, compact hot/cold and dry/moist quality fields,
substitution/glossary material, and recipes in the same codex. Their recipe
operations remain separate verbs or verb phrases. This predicts that a
Voynich operation should occupy an intervening/frame position and should not
be assigned to `ch`, `sh`, `e` or `d` merely because two states differ.

## Claim ceiling

GDT625 promotes a concrete `cth-/cthy` plant-part default and supplies a
conditional relation reader for state changes. It corrects f29v.4 from a
preferred temporal drying sequence to two preferred part-state bindings. It
does not identify the underlying language, prove the four quality atom
orientations, prove that `otar` is a verb or connective, or establish any
complete Voynich recipe.
