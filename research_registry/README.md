# Research memory

This is the working entry point for the whole recorded investigation. It keeps
ideas, research families, attempts and historical events separate. Record counts
are **not** counts of independent meaning hypotheses. Importing an old PASS or
FAIL does not endorse its scientific interpretation.

## Assessed hypothesis components and priorities

The substantive first pass is in [SEMANTIC_PRIORITY.md](SEMANTIC_PRIORITY.md).
Use `./vmanus-work priorities` for eight groups, `priorities --show GROUP_ID`
for one decision, and `ideas relations ID` for source-bound component links.
Two repeated word assignments are deduplicated at claim level; whole experiments
and distinct variants are preserved. Conditional ranks are not execution approval.
All 82 IP proposals have provisional queue dispositions; full historical identity
adjudication remains incomplete and has an explicit coverage report.

## Normal work: load a shortlist, then one dossier

```bash
./vmanus-work ideas search "Pflanzenteile Zuordnung"
./vmanus-work ideas duplicates "deterministic checksum final character"
./vmanus-work ideas show GDT854
./vmanus-work ideas search --blocker insufficient_independent_data
./vmanus-work ideas search --change new_data --scope semantic
./vmanus-work ideas search --signal capacity
```

Search returns at most eight cards by default, twenty explicitly. Use the
returned `next_offset` with `--offset` for another page. `show` displays one
dossier with three recent events. Longer history, evidence and requirements
have their own bounded pages:

```bash
./vmanus-work ideas events GDT854 --limit 8 --offset 0
./vmanus-work ideas requirements GDT854
./vmanus-work ideas relations GDT854
./vmanus-work ideas sources IP014
./vmanus-work ideas reviews IP014
```

Do not open the entire JSONL corpus or old prose logs in model context. The
SQLite full-text index reads metadata locally and returns only the selected
cards. Canonical files retain full imported events and evidence locators;
display truncation is labelled. Search is lexical, with a small documented
German/English navigation vocabulary. A low score or no hit proves no novelty.

`--blocker` selects assessed classifications. `--signal` selects explicit
historical wording, **not** an adjudicated failure. `--scope semantic` excludes
unclassified records; use unrestricted search as well during duplicate checks.

## What changed, and could it justify another test?

```bash
./vmanus-work ideas reconsider GDT854 --change new_data \
  --evidence docs/STRUCTURAL_KNOWLEDGE.md
```

The command above demonstrates the interface, **not new data**. It returns the
fixed prerequisites and marks their content UNVERIFIED. For GDT854 these include
CTH support on three physical folios, other-kernel training in every held fold,
and total folio capacity. A filename and a claim of more data satisfy none of
those facts. The strongest result is `RECONSIDERATION_REVIEW_REQUIRED`, never
permission, scientific eligibility, or evidence that the numerical gates pass.

Change categories are `new_data`, `new_binding`, `new_design`,
`source_correction`, and `new_authorization`. All requirements apply; preserve
source-written alternatives rather than silently converting OR to AND. Inherited
registry summaries always require primary-source review first. A refuted fixed
model is not rescued by more observations. A user-stopped route stays stopped.
Changed source bytes or new events invalidate affected reviews. The existing
experimental admission, sealed-data and GDT388 gates still apply separately.

## Add an idea; retain decisions

Save a small repository-relative JSON proposal with `title`, `summary`, `scope`
and, if known, `design` fields `mechanism`, `unit`, `contrast`, `prediction`,
`scope`. Then:

```bash
./vmanus-work ideas duplicates --proposal research_registry/examples/proposal.json
./vmanus-work ideas add research_registry/examples/proposal.json
```

The example is synthetic and should not be added to the real registry. New ideas
receive stable `IDEA000001`-style IDs; old IP/GDT/family IDs remain usable.
Matching normalized design fields produces a duplicate **candidate**, not an
automatic merge. A confirmed `duplicate_of` decision needs source evidence and
a written reason. The original record and its events remain accessible.

`review FILE.json` appends an attributed decision to `curation.jsonl`, chaining
it to the previous review. Include `record_id`, `reviewer`, `reason`, `scope`,
`verdict`, `assessment_basis`, `blockers`, `reopen` and `relations`. Evidence paths
are repository-relative; the command binds their bytes and the imported record
content. Corrections, supersessions and failed variants therefore remain visible.
Use a new idea ID for a genuinely changed mechanism and link its predecessor.
Do not edit an old failure into a success or change an old experiment's contract.

## Storage and refresh

- `imported.jsonl`: deterministic metadata snapshot of the five historical
  registries. Never edit it by hand.
- `SOURCE_MANIFEST.json`: source hashes, preservation counts and gaps.
- `ideas.jsonl`: new authored proposals, independent of the importer.
- `curation.jsonl`: attributed classifications and review revisions. Imported
  claims and assessed conclusions remain separate.
- `runtime/index.sqlite3`: disposable local search index, never published.

```bash
./vmanus-work ideas refresh
./vmanus-work ideas check
./vmanus-work ideas stats
```

Refresh imports only the allowlisted metadata files, never raw transcription,
images or arbitrary linked reports. It preserves new ideas and reviews, but
does not renew stale evidence bindings. It reports index gaps rather than filling
them with invented experiments. Do not append routine refresh/search operations
to the scientific ledger. After a material historical or scientific update,
append its existing ledger record, refresh once, and publish the exact artifacts
after privacy checks. The legacy hash-bound tools and reports remain unchanged.

The initial migration preserves all recorded ledger events, including duplicates
and superseded claims. An exact historical GDT reference creates a navigation
link to the indexed attempt; it does not merge different ideas or experiments.
Missing old bulk reports remain missing. This makes their summaries searchable,
not newly verified. See `VALIDATION.json` for preservation and scale checks.

Coverage boundary: the pre-reset investigation's 105 ledger entries were
compacted before this migration; the remaining reset summary does not reconstruct
105 individual decisions. The GDT index also has a recorded GDT256 gap. These
limits are explicit in `SOURCE_GAPS.json`. All rows of the five surviving import
sources are preserved; unrecorded ideas or removed bulk files are not invented.
