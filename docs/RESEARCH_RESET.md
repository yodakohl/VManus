# Research reset — 2026-09-05

Status: SUPERSEDED AS AN ACTIVE PLAN. The user subsequently required thorough
understanding of the subject and project history before selecting an approach.
The proposed cipher attack below has not been run and is not the current route.

The user asked for an independent decipherment approach, explicitly allowing
departure from the inherited model's schema. Subagents and local GPU use are
authorized; other LLM API keys are prohibited. This note changes the research
route, not the manuscript's evidential status. No new translation is claimed.

## Decision

End guessed-gloss extension and attachment repair as the default next task.
GDT827 can construct two incompatible fluent readings of the same known line;
GDT828 can reject only stipulated immediate-complement constructions. Meaning,
grammar and referents remain jointly adjustable. Those checks avoid some false
claims, but they have not recovered a writing or encryption mechanism.

Preserve the old experiments. Separate observations from modelling commitments:
source groups and separators are observations qualified by transcription;
water, vapour, commands, fixed grammatical roles, the 98-unit BPE inventory,
and prescribed FST role counts are not established components of a decoder.

Historical negatives have limited scope. GDT604 rejects the tested token-based
Naibbe attack. GDT612's score ranks its known truth behind wrong keys and its
implementation differs from the advertised grammar. GDT613 rejects its exact
grammar/coverage contract before target fitting. None of these results proves
that every homophonic, variable-segmentation or context-dependent cipher is
impossible. This is a reassessment of existing reports, not a newly discovered
defect. Later GDT614–616 successors also exist; do not simply restart that family.

## Concrete replacement direction

Recover an explicit encoding mechanism and a consistent key. A bounded first
candidate is a two-phase homophonic letter channel: the active mapping alternates
per encoded atom, multiple cipher atoms may represent one letter, and gaps are
observations rather than plaintext word boundaries. Exactly one plaintext
letter is emitted per atom; there are no guessed whole-word entries or freely
adjustable output lengths. This candidate has no positive Voynich evidence yet.

The duplicate audit found that `run_gdt001_periodic_cipher.py` already tests
unknown homophonic mappings with periods 2, 3 and 4. It calls `search_encoded`
in `run_gdt001_contextual_language.py`, resets at every line or source group,
retains source spaces, and uses a Middle High German order-2 model. The next
candidate differs by continuous phase across physical line breaks, arbitrary
displayed gaps and demonstrated hidden-key recovery under those conditions.
Two-phase homophony alone is not new. The legacy files remain byte-frozen.
Fix the exact new mechanism, parameter limits and failure conditions before fitting.

Evaluate a normalized forward model of the observed ciphertext, including
homophone-choice probabilities and start-phase uncertainty. Recover withheld
plaintext from independently keyed controls with word boundaries removed and
nonsemantic gaps inserted. Evaluate output recovery and identifiable key
equivalence classes; do not demand recovery of unobserved parameters. A capable
decoder must survive these conditions before its target failure is informative.
Roundtrip is necessary but insufficient: wrong reversible keys roundtrip too.

Include a genuinely line-reset control and a no-period control so the solver
must distinguish mechanisms instead of preferring continuous phase everywhere.
Condition on or score the displayed-gap process identically across rivals.

The source representation must preserve raw groups, extended entities and
uncertain boundaries. An opaque glyph sequence is not safely assigned a parity
by counting EVA ASCII characters. If atom counts are uncertain, marginalize
the ambiguity or explicitly delimit the tested stream without selecting a
favourable reading. Do not reuse the old cleaned stream by default.

After calibration, compare one frozen mechanism on separate admitted physical
folios with matched source-only predictive baselines. Known public passages
are not untouched scientific holdouts. Report what was exposed, reserve new
confirmation material prospectively, and retain alternate readings separately.
An external lexical anchor is useful; it is not a general mathematical
prerequisite for cryptanalytic key recovery. The absence of one does not prove
that ciphertext-only decipherment is impossible.

## External method check

Published work gives methods to examine, not Voynich keys. Greshko explicitly
describes Naibbe as a constructed cipher imitating Voynich properties, not its
solution: [author's account](https://www.michaelgreshko.com/naibbe-cipher).

Kambhatla, Born and Sarkar demonstrate recovery of synthetic and historical
homophonic ciphers using recurrence-encoded neural models. Their experiments
retain word boundaries, an important limitation for direct Voynich transfer:
[paper](https://aclanthology.org/2023.findings-eacl.160.pdf). Its linked
[repository](https://github.com/protonish/decipher_symbol_recurrence) currently
contains only a README promising code/data; no ready checkpoint was obtained.
This is inspiration for a local calibrated implementation, not an installed
decoder, a reason to call an external LLM, or evidence that Voynich uses that
encoding. No model training or new target attack has run during this reset.

## Scope and practical execution

Use the existing source-group atlas through guarded selector-first projection.
The 179-selector text allowance and 39-selector visual allowance differ; f84
and f84r remain sealed. Existing source corrections and reproducibility history
are retained. The reset itself is workflow maintenance, with no new GDT number.

Keep reports proportional to results. The next substantive deliverable should
be executable recovery of a hidden plaintext, or a precise failure of that
specified method. It should not be another German paraphrase of guessed words.
