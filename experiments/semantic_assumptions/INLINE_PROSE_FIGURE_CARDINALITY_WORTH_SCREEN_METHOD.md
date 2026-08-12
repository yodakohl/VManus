# Inline prose / figure-cardinality worth screen

## Question

Can an existing human annotation that gives the same count for a prose line's
groups and nearby figures establish an author-visible, ordered one-group to
one-figure label array?

This is a bounded worth screen, not a confirmatory semantic test. It is run
before any association between a group surface and an illustrated figure.

## Mechanical candidate selection

Use only
`results/existing_human_exact_locus_annotations.tsv`. Retain an exact-local
row when its human comment:

1. carries `REL_ARRAY_OR_GROUP`;
2. explicitly gives both a word/group count and a nearby figure/nymph count;
3. gives the same single integer for both counts; and
4. does not express the word/group count as a range.

English number words from one through twelve and decimal integers are parsed.
The fixed current table yields f81r.1 (seven/seven) and f84r.27 (10/10).
The 7--9-word versus seven-figure comment on f84v.1 is excluded by rule 4.

## Source-bound native visual gate

Inspect only the exact official Yale canvas containing each selected line and
its adjacent figure band. Native AI inspection is recorded as machine-authored
source-bound evidence, not as human palaeography. No OCR, CLIP, embedding,
glyph classifier, proposed reading, language fit, or filler transcription is
used.

Cardinality equality alone does not assign individual owners. An ordered
label array is admitted only if the page supplies an author-visible singular
assignment for every position through at least one of:

- separate cells or enclosures;
- leaders or connectors;
- explicit dividers; or
- a non-overlapping spatial layout in which every text group is isolated with
  one and only one adjacent figure and the line does not continue as prose.

If either selected line lacks such a complete assignment, its fillers remain
uninterpreted. If both fail, stop the route without testing text features.

## Claim ceiling

A stop permits the descriptive statement that two folios show aggregate
word/figure count correspondences but no source-bound individual ownership.
It does not establish that any group is a figure label, name, ordinal, role,
body-part term, word, sound, language, cipher, plaintext, meaning, or
translation.
