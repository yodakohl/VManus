# Conditional role-prior feasibility, 2026-10-03

Bounded source metadata/tokenization review only. No model fitted, candidate
selected, target scored, source acquired, or legacy byte changed. All twelve
cached CoNLL-U hashes match the original GDT001 public manifests before parsing.
Source spellings and POS were processed for aggregate tokenization/coverage
accounting only; no word examples or high-frequency class results were selected.

## Exact cached inputs

Each brace expands to the three literal filenames train, dev and test:

- `.gdt001/repos/latin_llct/la_llct-ud-{train,dev,test}.conllu`
- `.gdt001/repos/latin_ittb/la_ittb-ud-{train,dev,test}.conllu`
- `.gdt001/repos/middle_french/frm_profiterole-ud-{train,dev,test}.conllu`
- `.gdt001/repos/old_italian/it_old-ud-{train,dev,test}.conllu`

Hash inventories: `gdt001_language_pack_manifest.json` and
`gdt001_latin_scholastic_pack.json`. Use original CoNLL-U, not the normalized
GDT001 ASCII language packs. The latter discard observation details and tags.

| Corpus | Integer syntactic words incl. punctuation | Sentences | Multiword ranges | Empty nodes | CCONJ | PRON | VERB |
|---|---:|---:|---:|---:|---:|---:|---:|
| LLCT | 242411 | 9023 | 20 | 0 | 13993 | 18279 | 28723 |
| ITTB | 450517 | 26977 | 37 | 0 | 19149 | 23610 | 59768 |
| Middle French | 119001 | 5971 | 1582 | 0 | 6692 | 11545 | 14665 |
| Old Italian | 122024 | 3419 | 2936 | 306 | 5133 | 14183 | 16940 |

No malformed ten-column rows, missing FORM values or internal FORM whitespace
were found among integer words. These counts do NOT establish power for any
future frequency-selected panel. Italian's README count differs from the pinned
files; pinned file counts above govern. Annotation provenance is converted from
manual or converted with corrections, not uniformly native manual UD tagging.

## Visible unit integrity

Use multiword-range FORM instead of covered integer FORMs, omit empty nodes,
retain remaining integer FORMs, and honor `SpaceAfter=No`. This reconstructs
the complete `# text` value EXACTLY for every sentence in all four corpora.
Surface-unit counts before no-space joining are 242391 / 450480 / 117419 /
119060; no-space joins number 30826 / 62358 / 15451 / 19200, respectively.

Thus original edited space-group observations can be recovered mechanically,
without POS-directed grouping. They are not identical to syntactic words.
Mixed POS constituents must remain represented in evaluation rather than be
discarded, assigned one convenient tag, or split using held gold. Preserve
punctuation in the source receipt; a punctuation-masked predictor requires a
fixed observable-character rule, not PUNCT labels. Empty nodes are editorial
analysis with no corresponding written form and cannot become observations.

Gold sentence boundaries need not become features or context resets. However,
continuous work order still needs a frozen metadata policy: LLCT references
contain document identifiers and spans; ITTB references are unique sentence
identifiers; Italian has canto/verse metadata; French has `doc_id` on only
4584 of5971 sentences. Its cached README's three-extract description is stale
(four doc_id values occur). This audit did not reconstruct complete works.
Original train/dev/test shards cannot be treated as independent languages or
silently concatenated into asserted manuscript order.

## Predecessor limits retained

- GDT376 `experiments/yolo/gdt376_corema_hidden_function_oracle/REPORT.md`:
  local head signature positive; broad function, REF and other roles fail.
- GDT378 `experiments/yolo/gdt378_cross_corpus_construction_transfer/REPORT.md`
  and `SOURCE_AUDIT.md`: heterogeneous gold and lexical oracles; primary target
  null degenerate; subsequent identity lead nonpromoting.
- GDT381 `experiments/yolo/gdt381_relational_topology_transfer/REPORT.md`:
  target definition/predictor overlap, no role transfer.
- GDT382 `experiments/yolo/gdt382_voynichification_methodology_audit/REPORT.md`:
  composite fragmentation, strict universal failure, overcontrol; no universal
  impossibility of roles, no authorization to repeat target search.
- GDT385 `experiments/yolo/gdt385_corema_parent_link_consequence/REPORT.md`:
  one TIME-derived route passes, full registered instrument fails.
- GDT394 `experiments/yolo/gdt394_latent_role_bottleneck_transfer_audit/REPORT.md`:
  role loses matched generic bottlenecks; semantic-role architecture closed.
- `experiments/semantic_assumptions/CLOSED_ROUTE_FAMILIES.tsv`, exact family
  KNOWN_LANGUAGE_POS_AND_WORD_ORDER: target route remains closed. Its cited
  `semantic_assumptions/results/currier_role_transducer_audit_report.md` was not
  found by bounded filename lookup; do not pretend its primary was inspected.
  The existing family row and registry semantic_catalog entry preserve the
  closure, not a new verified universal theorem.

## Decision boundary

A direct held-language gold-role endpoint is different from reconstructing a
topology-defined class. Conditional proposal ranking is different from target
POS assignment. Both Latin collections must be held together; three related
languages are not a universal-language sample. High source performance could
support ordering C0 proposals under an explicit word-like-unit assumption;
it cannot translate a target group, exclude an alternative meaning, or waive
the word-profile rule. Failure stops the fixed source ranking instrument, not
grammatical interpretation in general. GDT1160 does not remove this gap.

Before implementation, root must decide whether conditional proposal ordering
alone is worth the work and freeze surface grouping, mixed gold accounting,
boundary-free context and calibration criteria. No target POS reopening or
new experiment is selected by this receipt.

## Root decision after independent challenge

Not selected for implementation. An independent review retained the original
376/378/382/394 failures and required a prewritten pair of complete, equally
admissible C0 accounts whose priority this role contrast would actually change.
No such pair is supplied: the current LIGHT versus DURATION alternatives can
both be nominal, and inscription TOKEN versus PATTERN likewise does not turn
on the proposed POS classes. The source grouping capacity is retained. Proposed
thresholds remain unregistered suggestions, not measured gains or authorization
to infer target roles. No new experiment, model fit or target access occurred.
