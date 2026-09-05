# GDT810 — paired qualities do not predict doubled following values

Status: NO_EXTERNAL_PAIRED_QUALITY_MULTIPLE_VALUE_SUPPORT

## Result

The concrete local idea was: if `otchol` means cold-and-dry and `daiin`
means III, could `otchol daiin daiin` mean cold III, dry III?
It remains a possible interpretation of f32v.8, but the proposed general
allocation rule receives no support elsewhere in the inherited cache.

This pass makes one prediction from an existing meaning hypothesis instead
of generating another large ranked vocabulary. It reuses all54 complete
GDT628 matrix forms, including unoccupied cells, and scans2,264 exact head
occurrences in the same179-selector source population. No new page is used.

Among complete, three-reader-supported head/value/next-word brackets outside
f32v, conditional on at least one following written value:

| Inherited whole-word class | One value | Multiple values |
|---|---:|---:|
| Proposed single quality, OL | 29 | 1 |
| Proposed paired quality, OL | 5 | 0 |
| Single-core OR comparison | 8 | 0 |
| Paired-core OR comparison | 4 | 0 |

The five paired-quality examples are `otchol daiin` on f5v.5 and f44v.2,
`otchol dain` on f7r.7, `kchol daiin` on f45r.3 and `tchol dain` on f47r.10.
These forms receive their one/two-quality classification from an inherited
hypothesis; the classification itself has not been independently decoded.

The counterexample to a quality-count explanation is f21v.4:

```text
sho chodaiin choty | chol daiin daiin | chty chtol
```

The central span and next word agree in all three alternative readings.
Here the old `chol` candidate has only one quality, dry, yet two values follow.
Thus repeated values are not unique to supposed two-quality compounds.

## This is not an artefact of the stricter reader filter

The motivating `otchol daiin daiin` itself is present in all three readings.
Its following stop differs: ZL3b/IT2a have `ctho daiin`, RF1b `cthodaiin`.
The declared full head/run/stop comparison therefore gives that larger
bracket two-reader support, not three. That does not make the repeated
`daiin` pair doubtful; it makes the following word boundary variable.

Even retaining every raw ZL3b row, the only arity2 OL head followed by multiple
values is this discovery occurrence. There are zero external examples before
any reader or line-boundary exclusion. Other raw multiple-value occurrences
follow `qotol`, `chol`, `shol` or bare `ol`. The sole mixed run in that raw
OL subset is `shol daiin dain` on f42r.13, with two-reader bracket support.

All zero-value, uncertain-reader and line-end-censored occurrences are kept
in [HEAD_VALUE_RUNS.tsv](artifacts/HEAD_VALUE_RUNS.tsv). The complete18-cell
comparison is [SUMMARY.tsv](artifacts/SUMMARY.tsv).

## Historical reading and consequence

Shared and separate degrees are both historically possible. The official
catalogue transcription of early-fifteenth-century [Wellcome MS.542](https://wellcomecollection.org/works/n674z2xd)
describes hot and dry together in one degree; [MS.712, about1475](https://wellcomecollection.org/works/n8tktt8h)
assigns different degrees to those two qualities of absinthium. Neither
source demonstrates the specific compressed order quality-compound/value/value.

Consequently, a single written degree after an alleged compound could qualify
both qualities. This pass does not reject that older descriptive reading,
the general possibility of degrees, or a special local III/III interpretation.
It does rule out treating this single repeated pair as evidence that the
code systematically writes one following value for each hypothesized quality.

Keep GDT809's 16-entry dictionary and both working readings unchanged.
Do not merge repeated values, invent an unwritten quality, or silently assign
each repeated value to a different subject merely to obtain fluent German.
The next work still needs an independent reason for subject/field binding;
retesting the same quality-arity prediction would add nothing.

## Efficiency and provenance

An initial sho audit found an available older `feuchter Ansatz` card, but its
origin is the earlier sh+o composition hypothesis. Restoring it would increase
coverage without new evidence, so this pass did not enlarge the dictionary.
See [HISTORY.md](HISTORY.md). Existing GDT627/628/686 work is retained and not
counted as a rediscovery; this test concerns only the narrower arity prediction.

One compact builder queries each mixed line source once. An independent
validator passes27 checks, reconstructing all2,264 occurrences,18 summaries,
the result decision, hashes and executable GDT388 intake. The declared
three-reader arity2/multiple-value packet has zero rows, so intake is valid
but not score-ready; that grants no relation or visual-owner evidence.
f84/f84r remain sealed, and no larger renderer or previous experiment changes.

Reproduce with src/run.py and src/validate.py --no-write. The experiment
manifest binds the pre-extraction design, matrix, source files and scripts.
The repository-wide check retains only the known unrelated seven unbound
GDT600 files; they are untouched and excluded from publication.
