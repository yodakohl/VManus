# GDT612 method

## Question

Can a simplified hard-bucket decoder inspired by GDT609's FST34 inventory
identify one compositional Latin, Old Italian, or Middle High German key on the
public GDT605/GDT606 unit stream, and is its calibration itself identifiable?

## Architecture

The implemented pilot gives the 34 primitives exactly 18 literal, four
syllabic, three prefix, three suffix, two connector, two context-abbreviation,
one whole-form and one active-null role. All 64 learned merges compose
recursively in their directed GDT608 order by default. A fit may buy at most
eight exact merge overrides, at most four of them whole forms; null mass is at
most 3%, and exact `qok` may never be a whole-form override.

This is materially narrower and different from the exact GDT609 model. The
binary does not parse `model_v1.json`; it hard-fixes the role counts and one
active null, uses weak violation penalties rather than the published FST,
treats connector and wholeform through the same transition, guards only exact
`qok`, and permits lexicon-injected overrides in the primary fit. These are
properties of the executed pilot, not of FST34 itself.

Each fit uses only the 68-folio train stream and a hash-pinned language
reference. Its objective combines real-versus-within-word-order-destroyed
fourth-order character likelihood, a small lexicon term, grammar/length costs,
and codebook cost. Six deterministic 60,000-proposal real starts are run per
language, plus three destroyed-reference fits. Held data is opened only by the
separate evaluator.

## Calibration and evaluation

The same binary and capacity first attack a planted Latin code with the
same 34 roles, merge tree, eight overrides, four whole forms, null cap and qok
guard. Post-run audit shows that this control is not an identifiable inverse
problem: four primitive assignments and one override never occur in train, and
the planted truth loses to all six wrong fitted keys under the exact executed
objective. All six synthetic fits and all target fits are preserved. Target
evidence is exact carrier evidence only: the same primitive role+output, full
unit output, or source-position word span must recur in all six starts.

Positive language-model or dictionary score is explicitly diagnostic because
candidate outputs come from the scored reference. It cannot itself identify a
carrier value.

## Decision and claim ceiling

The executed objective/control implementation is invalid because the known
truth ranks last and the control omits truth carriers. The target keys remain a
reproducible descriptive stress test with zero unanimous outputs. The experiment
may reject only this heuristic objective/control pair, retain a stable role
without a value, and expose output concentration. It may not reject the
historical FST34 capacity itself, assign a word/sound/language/plaintext/meaning,
or turn a dominant reference token into a translation.
