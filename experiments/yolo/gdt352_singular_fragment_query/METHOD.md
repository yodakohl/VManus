# GDT352 — singular pharmaceutical-fragment query

## Question

Can the public human catalogue's independently asserted resemblance between
the full plant on f96v and pharmaceutical fragment 94 be converted into an
exact, singular inscription query, and does that query recover an unusually
similar source-native form on f96v?

This is a bounded exploratory correction to the referent atlas, not a new
decipherment model. GDT351 correctly audited four `ASSERTED_SAME` relations
with no prior local query, but that filter did not include catalogue-numbered
`SIMILARITY_ONLY` rows. The exact human annotation for f99r's bottom row says
there is one plant and one label, so fragment 94 has the singular query locus
`f99r.46`.

The catalogue also links f96v to fragment 116 on f100r. That top row has five
plants and six label words and its source explicitly questions the shift in
ownership. It is retained only as the fixed two-locus uncertainty set
`{f100r.2,f100r.3}`.

## Evidence order and exposure

The visual/referent facts and ownership states come from existing human
annotations. No manuscript image is opened. During the source audit, a broad
crosswalk display exposed the diplomatic surface of `f99r.46` before the
formal score was frozen. Therefore every score here is explicitly
`POST_EXPOSURE_EXPLORATORY`; none is prospective confirmation.

All global source tables are read through a raw-field guard. Every selector
beginning `f84` is discarded before the rest of that row is parsed. The
experiment does not read, retain, display, join, or score f84 data.

## Fixed comparisons

For each ZL3b/IT2a/RF1b reading:

1. compare the complete label surface with every source group on f96v;
2. report exact occurrence, maximum `SequenceMatcher` ratio, and the label's
   rank among all covered f99r plant labels against the same f96v page.

At the all-reading family level, compare the complete label family expression
with individual f96v source groups. Family n-grams are not used. A locus with
multiple source groups would preserve its group delimiter rather than bridge
it.

For fragment 116, score both ownership candidates without selecting between
them. Report how common an exact family match is across the non-f84 consensus
inventory. No p-value or semantic inference is licensed by a two-candidate
ownership set.

## Decision

- `NEW_SINGULAR_QUERY_FORMALLY_SUPPORTED` requires an exact surface match in
  all three readings and an exact consensus-family match.
- Otherwise the singular query is negative.
- Any match in the fragment-116 uncertainty set is descriptive only and is
  labelled `AMBIGUOUS_COMMON_FORM_LEAD` when its family occurs broadly.

## Claim ceiling

At most this experiment establishes whether one newly localized human-nominated
referent has exact or near formal recurrence. It establishes no plant identity,
lexical identity, word meaning, language, plaintext, or translation.
