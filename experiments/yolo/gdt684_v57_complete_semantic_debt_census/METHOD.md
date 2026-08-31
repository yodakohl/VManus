# GDT684 method

## Question

Does V57's 479/479 formal assignment actually deliver practical semantic
information at every position, and which exact cards, layer transitions and
working assumptions must be repaired first?

## Inputs

- GDT683 `V57_51_LINE_READER.tsv`: the complete 51-line, 479-position reader;
- GDT683 `RESULT.json`: frozen V57 totals and scope;
- GDT683 `OL_417_LINE_RERENDER.tsv`: the separate outside-V57 free-`l` context;
- GDT664 `STEM_MODEL_V41.tsv`: provenance and MEDIUM strength of the learned
  `ol = Grundansatz` whole-word card;
- `src/ANCHOR_DRIFT_SPECS.tsv`: seven manually located cross-layer drifts.

No page, image or transcription outside those admitted inputs is opened.
`f84` and `f84r` remain forbidden.

## Method

1. Split each V57 line into the 479 exact whitespace positions and require
   one literal gloss and one aligned chunk per position.
2. Detect explicit identity, material-role, state, value, structure and action
   signals with the published regular expressions in
   `SEMANTIC_SIGNAL_RULES.tsv`. Partition every position into one disjoint
   information class. This produces the broad 335-position specificity view.
3. Apply a separate curated card queue to nine repair families: generic
   carriers, open values, unresolved bindings, structural cards, open
   taxonomies, generic drug heads, raw classes, opaque form codes and
   headless quantities. This is the narrower 139-position practical queue;
   one `oidal` position belongs to two families, hence 140 memberships.
4. Independently apply five literal, non-fluency-dependent alarms:
   `OPEN_COMPOSITION`, `NON_SINGLE_GLOSS`, `STRUCTURAL_META_AS_VALUE`,
   `HARD_GENERIC_CARRIER` and `STATE_ONLY_NO_OBJECT`. Their 194 overlapping
   memberships cover 172 positions. The two exact surface sets are embedded
   in the deterministic builder and printed in the summary artifact.
5. Compare the 86 declared action positions with operation words in the
   literal and practical layers. Count operation-label-by-line pairs, not
   inferred syntactic verbs. Preserve the exact regex deck with the output.
6. Attach the seven manual anchor drifts to their exact ordinal spans. These
   include the `dchey` action/result conflict, `dy` becoming an invented
   command, the `qodaiin` quality-to-quantity swap, two lost open bindings and
   two untracked material/span rewrites.
7. Keep two scope distinctions explicit: five free V57 `ol` working cards are
   a MEDIUM semantic-confidence watch inside the 479 denominator; the free
   `l` on f111v.18 is an outside-V57 companion and is not added to it.
8. Join the current `(surface, literal gloss)` exactly against the published
   LOW/EXPLORATORY cards in GDT671, GDT674 and GDT677–681. This retains 30
   positions / 28 cards; the rewritten f115r.1 `cheop` compound part correctly
   does not join its older longer gloss.
9. Compare practical prose with a separate frozen 31-lemma operation deck.
   This exact definition yields 74 extra operation×line pairs on 29 lines.
10. Rebuild every generated artifact byte-for-byte in a temporary directory
   and validate counts, subsets, hashes, spans, sealed-page absence and the
   three-layer crosswalk.

## Decision rule and claim ceiling

Pass means that all 479 positions have an explicit information class, repair
route and three-layer debt state; the debt subsets and manual anchors replay
exactly; no excluded page was accessed; and a byte-identical rebuild succeeds.

The census does not accept a new meaning. `chol = Trockenansatz`,
`shol = Feuchtansatz` and `tol = Kaltansatz` are forward working predictions
for the next exact-occurrence circuit. Structural tags remain distinct from
word translations. No language, phonetic value, named plant, disease, patient,
cure, carrier liquid or historical codebook is identified.
