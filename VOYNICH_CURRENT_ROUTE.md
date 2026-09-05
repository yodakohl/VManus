# Voynich current route
Updated: 2026-09-05. Read first; current route, not history.
`./vmanus-work lookup GDT811 GDT809` returns compact pointers from
`experiments/EXPERIMENT_INDEX.tsv`. Open only needed reports.

## Goal and actual position

Obtain a concrete translation whose meanings and constructions carry across
passages without continual reinterpretation. The manuscript is not translated.

- Confirmed English lexemes: **0**. Confirmed German lexemes: **0**.
- Confirmed plaintext clauses: **0**; language, sounds, cipher and POS/SVO unknown.
- Concrete exploratory meanings are welcome, but remain hypotheses. Tests of
  source conservation or renderer consistency do not establish their truth.
- EVA letters are modern transcription labels: p/s/r/l are not Latin initials.
  ZL3b/IT2a/RF1b are alternate readings of one manuscript, not independent witnesses.

## Scope: the lists govern admission

- Thirty visually released physical pages map to 35 source selectors:
  `experiments/yolo/gdt791_thirty_page_visual_owner_spine/src/PAGE_SELECTOR_SPECS.tsv`.
- The inherited text corpus has 179 selectors:
  `experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv`.
- GDT811 joined those lists: 190 selectors, not 190 visually
  inspected or newly admitted pages. This union is not automatic experiment scope.
- Preserve explicit panel keys such as f67r2/f68r1. Physical pages, source
  selectors and normalized folio/group keys are different counting units.
- GDT327's older 91-folio edition does not enlarge this scope.
- f84 is sealed; f84r is sealed. Open no new page/image/transcription without
  separate user release. Earlier metadata exposure supplied no semantic licence.
- Query mixed TSVs only through `./vmanus-exp query-tsv` with explicit selector
  allow-values, requested columns and forbidden prefixes f84/f84r. Reject the
  selector before materializing the payload, never parse everything then filter.
- Image labels, embeddings and OCR counts do not identify words.
  Visual observation and inferred meaning stay separate.

## Current working model

A page-conditioned construction hierarchy with strong line-position effects:
productive technical shells, learned wholes and possible opaque names.
Physical line reset is not a universal sentence break.
Keep descriptive substance/part/quality/degree records distinct from
prescriptive ingredient/amount/process records; both are historical analogies.
Distinguish depicted thing, property and reference/category. Common property
vocabulary and a compendium of different genres remain rivals.

Structural tags (PAGE_HOST, DY, B3, H1–H4, tuple IDs) are analyst variables.
H1/H2 tend toward entry positions, H3/H4 toward internal/final positions;
the full old semantic pairing did not transfer (GDT736–737). No POS is decoded.
GDT333 rejects universal register-independent roles. GDT336 supplies only a
weak placement prior, not a decoder. GDT398 licenses no free equivalence merges.

Renderer precedence: exact context/bound span > licensed exact whole > unknown.
Consume a span once. Preserve repetitions, unresolved tokens and alternative
boundaries. Do not export a component merely because similar words recur.

## Latest material results: GDT809–811

- GDT809: four paragraphs, 145 tokens; 16 low-confidence whole
  defaults cover 46 positions, 99 remain open. Descriptive quality/degree and
  recipe state/amount readings remain rivals; prior local D preference survives
  only as a prior. cthy leaf/herb/opaque botanical identities remain tied;
  external record compatibility overlaps training and is not new meaning evidence.
- GDT810: one following value per alleged compound quality does not extend
  beyond the motivating f32v case. Shared degrees/local separate grades remain
  possible. Reusing sho adds no evidence: its old gloss came from sh+o composition.
- GDT811: full f17r/f77r/f88r/f72r text, 178 loci/946 tokens, with local labels
  separate. Eleven label/prose string edges do not identify pictured objects.
  f88r repeats only okol as an exact complete label in its prose; f77r repeats
  only otedy, at the next paragraph rather than the upper arch paragraph.
- Seven-whole inventory: 164 occurrences; okol 58/45 page-group keys,
  qokol 90/52, chokol 3, okoldy 8, qoekol 2, ofaldo 1, ofal 2. okol is cross-register,
  so a specific plant name is not selected. ofaldo/ofal is a scarce name-form
  candidate, not a species or a licensed do suffix.
- Both otchol-X-Y-chol spans on f17r are reader-exact, one across a line break.
  No other width-two case occurs on the 30 released pages; exact otchol chol
  on f4r contradicts obligatory two-slot grammar. Retain only local scope rivals.
- No dictionary change or translated clause. GDT811's 19 checks validate
  reconstruction, not meanings; all 17 new text-only relations are ineligible.

## Which source to open

| Need | Index lookup / source |
|---|---|
| Current content synthesis + complete four-page text | GDT811: WORKING_THEORY.md and full reader |
| Shared concrete paragraph hypotheses | GDT809: joint reader and common dictionary |
| Thirty-page image/text ownership and boundaries | GDT790–791; PANEL > RECORD > old statement |
| Latest integrated legacy renderer/dictionary | GDT734; read later corrections before using a gloss |
| Historical specialist/learned-word bridge | GDT735; no comparable four-initial material code identified |
| Label/prose and circle-label corrections | GDT792–798; learned whole/status rivals, no unique-day code |
| Physical line endings, context and independent axes | GDT800–808; no universal l/m or e/o meaning |

The GDT734 V99R7 cache is an inherited display, not current semantic truth.
GDT809's 16-card dictionary supplements it; it is not a global replacement.
GDT737 quarantines 80 p/s/r/l-derived held cards; GDT738 holds salt/species
readings of solaiin/sols. GDT754 removes inherited component-composed prose.
GDT769–786 bound ol and related wholes by occurrence; oil/water/wine stay open.
GDT794 gives complete radial labels priority over global pharmaceutical glosses.
The noncanonical workshop summary may suggest candidates, not promote them.

## Avoid repeating work

Before a genuinely new research route, run `./vmanus-exp route-check QUERY`.
Its lexical ranking is navigation, not a verdict. Inspect relevant returned
primary reports and `experiments/semantic_assumptions/CLOSED_ROUTE_FAMILIES.tsv`.
Do not rerun failures without new data or a genuinely different prediction.
Do not revive:

- EVA-to-Latin initials; generic language/cipher expansion or anonymous role induction;
- generic universal action prose, substring glosses, neighbour/backoff meanings;
- universal q/base direction, tuple roles or free equivalence clusters;
- the withdrawn f57/f77 element decoder, literal Naibbe/whitespace route or FST34/V2;
- botanical species naming by resemblance plus recycled medicinal-use statistics;
- GDT629 clause rediscovery or GDT686/GDT764 degree-versus-amount dispatch;
- the same GDT809 rankings, GDT810 arity count or GDT811 reference/scope inventories.

## Next useful work and efficient operation

Seek concrete meanings for written contrasts with shared subject/scope across
complete passages. Rare names and broad property/reference forms need different
explanations. Keep alternatives; absence alone is no disproof.
No new broad method selected.

Reuse readers; batch related probes. Reformatting/recounting is not a new
experiment. Workflow: `docs/WORKFLOW.md`. Add helpers outside hash-bound tools.

## Detailed memory and recording

- `VOYNICH_ACTIVE_STATE.md`: full claim registry; read targeted sections only.
- `experiments/semantic_assumptions/ACTIVE_EXPERIMENT_LEDGER.tsv`: append-only
  material history. Add one short row per material pass/failure/correction/lead.
- Older handoff/worklogs are recovery archives and may be superseded.
- Keep GDT001–336 untouched; new GDT337+ experiments use the scaffold and
  manifest, explicitly sealing f84 and f84r. New relation evidence still runs
  through `./vmanus-exp check-edge-packet`; text identity is not visual ownership.
- Preserve unrelated/untracked work. Scan the exact staged tree before any
  publication. Full global checking remains separate from task-scoped checking.
- Replace current summaries, not append chronology. Details remain in reports,
  registry and Git.
