# GDT215 — best current q13 generative theory

## Result

**HYBRID_BALNEOLOGICAL_RECORD_COMPILER_LEADING_SEMANTIC_KEY_ZERO**

The best current theory is a **hybrid medical record compiler with a distinct
diagram-reference register**.  The q13 pages most plausibly combine a
therapeutic balneological document domain, schematic setting/hydraulic/process
drawings, short graphical reference strings, and longer practical records.
The theory assigns exactly zero Voynich strings a meaning.

This is more useful than saying only “underdetermined”: it specifies a
generator, ranks its rivals, identifies its unresolved costs, and makes new
predictions.  It is still hypothesis generation rather than confirmation.

## Explicit generative model

```text
PAGE := PAGE_PROFILE VISUAL_SYSTEM GRAPHICAL_LABEL_REGISTER? RECORD+
RECORD := RECORD_OPEN? RECORD_BODY+
RECORD_BODY := ENTRY_STATE? FIELD (DY_CLASS FIELD)* B3_CLASS?
FIELD := WRAPPER? INNER_D? POSITION_FRAME? PAGE_HOST RIGHT_FAMILY?
```

The provisional document roles are:

- `PAGE_PROFILE`: site/system context;
- `VISUAL_SYSTEM`: physical setting or hydraulic/process model;
- `GRAPHICAL_LABEL_REGISTER`: component, state, case, or reference values;
- `RECORD_OPEN`: identity or setting header;
- `RECORD_BODY`: practical description, indication, procedure, caution, or
  testimony, with those alternatives not localized;
- `PAGE_HOST`: the best formal candidate for an opaque content address/value;
- wrappers, right families, `DY`, and `B3`: record rendering and closure.

These are latent document roles, not English translations or parts of speech.

## Representative parses

The safest parse is structural rather than lexical:

```text
q13 page
  PAGE_PROFILE
  VISUAL_SYSTEM(pools, enclosures, ducts, figures, repeated units)
  GRAPHICAL_LABEL_REGISTER(short label-associated constructions)
  RECORD+

record line
  ENTRY_STATE?
  FIELD [DY_CLASS FIELD]*
  B3_CLASS?

field
  WRAPPER? INNER_D? POSITION_FRAME? PAGE_HOST RIGHT_FAMILY?
```

The one f80r/f82r text-linked locus with connected-component evidence,
`f82r.10`, is compatible with a component/state reference, but it receives no
value.  `f82r.35` and `f82r.38` remain proximity-only despite their hydraulic
visual context.  Their strings are therefore not parsed as object names.

## Why the hybrid leads

It explains several otherwise awkward observations together:

- the anonymous HPR2/page-conditioned compiler survives while every active
  semantic gloss has been withdrawn;
- physical lines, entry state, `DY` fields, and `B3` closure behave like a
  record renderer rather than ordinary running prose alone;
- short labels form a transferable construction register, yet simple dropped-
  prefix or exact key mechanisms fail;
- exact PAGE_HOST identity is locally recurrent but does not behave as a
  stable global dictionary or one-referent/one-host codebook;
- authentic medieval abbreviation explains only part of the surface algebra;
- readable medieval medical, bath, and hydraulic sources establish that
  diagrams, reference marks, and practical prose can coexist in the proposed
  period without implying direct descent.

The rival ranking is:

1. **hybrid language + abbreviation + notation — leading**;
2. **semantic/technical notation — live secondary**;
3. **compressed abbreviated natural language — insufficient alone**.

## What remains awkward

The theory has no identifying semantic key.  Exact label-to-prose reuse is not
globally unusual; current external-referent pairs do not preserve exact hosts
or full tuples; 22 of 23 f80r/f82r linked rows have only proximity ownership;
q13's long ducts exceed the closest readable bath illustrations; and all
tested historical-language mappings lose matched anonymous controls.  These
are costs, not facts to be explained away.

## Novel predictions

The highest-value predictions, frozen in
`gdt215_prediction_registry.tsv`, are:

1. a new singular repeated hydraulic component should preserve the full
   record/label construction more often than PAGE_HOST alone across held
   folios;
2. a readable q13-like homolog should align local captions with an
   explanatory reference mechanism even if therapeutic payload remains
   visually hidden;
3. a repeated bath/site/installation should preserve opening plus
   setting/hydraulic tuple structure despite exact-host variation;
4. visual grounding should recover setting/hydraulics better than indication,
   procedure, or outcome content;
5. a true bilingual/keyed legend should collapse page-conditioned ambiguity
   and create stable full-tuple correspondences.

The first, second, third, and fifth predictions were not used to build the
theory.  Failure narrows or rejects the implicated layer; it does not license
post-hoc gloss repair.

## Conclusion

The current data support a concrete theory of **document architecture**, not a
translation: q13 is best modeled as a page-conditioned hybrid medical record
system with a possible diagram reference register, provisionally situated in
a therapeutic balneological domain with technical hydraulic rendering.

The next useful step is external identification, not another internal word
guess: acquire a provenance-clean repeated setting/hydraulic referent with
singular text ownership and held-folio replication, or a readable q13-like
diagram with diplomatic labels and prose.

No f84 artifact was accessed.  No word, language, plaintext, or translation is
claimed.
