# GDT482 method

## Question

Are GDT481's 45 remaining single-event record tails really opaque, or are their
fixed meanings composed from smaller semantic pieces already used elsewhere in
the six-page edition?

## Inputs

- GDT479's 183 definitive local events and 146 fixed bundles;
- GDT481's 135 record-fragment coverage rows, used only to select the 45
  one-event `SINGLETON_FRAGMENT_TAIL` records;
- no new page, reading, boundary, model, or meaning.

## Construction

Each GDT479 literal working reading is split at its ordered `·` and `/`
boundaries. Learned names are replaced within each event by encounter-ordered
slots (`{N1}`, `{N2}`, ...), so repeated identity inside an event remains
visible without pretending that two different names are the same word.
`cheo:DROGENFAMILIE` becomes a typed learned-family slot rather than a
functional morpheme.

For all 183 events, the builder inventories every contiguous span of one, two,
or three semantic components. A span supports a residual event only when it
also occurs in at least one *other* event. Two atlases are retained:

1. model-conditioned: donor and target share `COORDINATE`, `INSTRUCTION`, or
   `CATALOGUE`;
2. model-free backoff: the ordered meaning fragment may recur under another
   model, but the target's active model is not changed.

A deterministic left-to-right tiler maximizes, in order: recurrently covered
components, components covered by multi-component fragments, longer recurrent
fragments, and fewer segments. A nonrecurrent fallback is allowed only for one
component, which makes the precise local residue explicit.

## Interpretation classes

- `MODEL_CONDITIONED_RECURRENT`: fully tileable inside the active model;
- `MODEL_FREE_RECURRENT_BACKOFF`: fully tileable only across models;
- `LEARNED_LEXICAL_SLOT_ONLY`: the remaining local item is a learned name or
  family label, not a missing functional meaning;
- `UNIQUE_FUNCTIONAL_COMPONENT_REMAINS`: a genuine functional component in
  the current working edition has no second event-level occurrence.

Recurrence does not create a translation and nonrecurrence does not erase one.
Every event retains its concrete GDT479 default; GDT482 only shows how much of
that default is assembled from already familiar components.

## Claim ceiling

The result is an internal component atlas for the fixed 45 residual events. It
does not establish plaintext, historical language, name identity, or a new
meaning, and it does not authorize a model change.
