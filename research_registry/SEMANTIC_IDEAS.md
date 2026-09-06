# Concrete historical semantic hypotheses

This is the working view of source-attested historical propositions, not a report
of decipherment. Source pointers, empty headings, methods without a proposition,
result-only rows and unfinished extraction work are excluded from the idea list.
They remain in the source archive. No hypothesis becomes executable by inclusion.

## Current public snapshot

| Unit | Count |
|---|---:|
| Active semantic hypothesis variants | 3,719 |
| Separately typed formal-role cards | 265 |
| Reviewed source cases, including the correction archive | 4,507 |
| Archived source-extraction errors | 47 |
| Exact normalized assertion repetitions grouped | 476 |
| Reviewed equivalence groups / display reduction | 43 / 52 |
| Public semantic display entries | 3,667 |

These are different units, not a deduplicated total of independent theories.
A local ignored supplement contributes95 semantic cards and one formal card;
the ordinary local default therefore displays3,762 semantic entries. A fresh
public clone has the public view only. Local source files and quotes are not
published or silently folded into public counts.

## Bounded retrieval

```bash
./vmanus-work priorities "qokaldy"
./vmanus-work priorities --offset 8
./vmanus-work priorities --show SEM:0018dcd7222eec8bfc97 --field evidence
./vmanus-work priorities --show SEM:0018dcd7222eec8bfc97 --field cases
./vmanus-work priorities --show SEM:08a05de29068958d3f58 --field assessments
./vmanus-work priorities --include-formal "closure"
./vmanus-work priorities --sources "qokaldy"
./vmanus-work priorities --groups
./vmanus-work priorities --shortlist
```

The first detail ID is the AROL hypothesis. Use IDs returned by search for other
cards. Search returns eight cards by default, at most twenty; details and source
cases are paged. Direct claim matches rank ahead of incidental evidence matches.
Lexical ranking is navigation, not semantic support or scientific priority.
Use the guarded query interface or `semantic_ideas.connect(root)` so snapshot
freshness is checked before reading SQLite; a directly opened old cache can lag.
The cached query path and10k-card regression avoid loading a complete history
into model context. Do not dump the JSONL registries to read them.

## Identity and original source cases

Each proposition binds exact source lines and file hashes. Its complete scope
includes the whole form or construction, model version, domain and local owner
where relevant. Different meanings and rivals remain separate. A quoted broad
paragraph does not automatically make every subclaim independently addressable;
an atomic gloss does not cover a complete multi-card model.

Whitespace and backtick typography alone are normalized for exact assertions.
Explicit equivalence decisions add43 groups without deleting any original ID.
The identity log also retains five related-but-distinct links,28 rival links and
two specializations. Conflicting nonidentity blocks transitive merging; changed
claim or case bindings require a new review. Shared spelling, shortened wording
or a matching source title alone proves neither identity nor nonidentity.

One representative appears per reviewed equivalent group. Its status and normal
source/case counts belong to that representative; `group_scope_cases` counts all
member cases. Open `--field equivalents` or `--field relations` for the others.
No failure, success or execution permission propagates across an identity link.

The append-only correction log archives47 erroneous exports and restates177
source assertions. Every original claim, case and quote remains retrievable,
including via `--show ID` for archived cards. Numeric columns, alias-column
misparses, unlicensed constituent exports and metadata are extraction errors;
actual proposed-and-rejected meanings remain historical hypotheses. Formal tags
are separately typed and excluded from the semantic default. Unconfirmed does
not mean rejected, and an old source PASS does not confirm a meaning.

## Failure memory and conditional priorities

Thirty-two scoped question dossiers distinguish empirical failure, invalid test,
insufficient capacity, missing meaning binding, proposal-only status and historical
model revision. They appear before inherited experiment context under assessments.
They state the actual compared subclaim, primary evidence, scope and changed-input
requirements. An editorial wording preference is not an empirical falsifier.
Original conditional predictions remain distinct from observed counterexamples;
reviewer-supplied reopening conditions are prospective, not old preregistrations.
Only the latest linked revision acts; all older decisions remain in the log.

The separate shortlist contains nine conditional questions in an explicitly
reviewed subset, not a global ranking of every variant. All nine remain unready.
Each gives the missing observation, outcome consequences and a bounded budget
only after qualifying evidence exists. More pages, smoother prose or another
successful rendering do not themselves satisfy those conditions.

The two added source questions concern the exact R2 AIR role and the substantive
axis of naked ODAIIN. Dryness of another patient cannot refute a fluid AIR carrier.
Pass268 already broadened portable AIR to path while retaining local wet readings;
that authored revision is not an independent role counterexample. ODAIIN's later
open value level need not exclude an amount specialization. GDT728's inherited
wording dispatch leaves evidence and active readings unchanged. No binary rerun,
free substring meaning or automatic bridge between model versions is licensed.

## Recovery coverage and maintenance

All5,370 retained proposal fragments,3,788 component excerpts and82 IP entries
have explicit initial dispositions. These are source-intake units, not independent
ideas. The archive's9,917 unresolved extraction blocks and5,561 pointer rows keep
immutable intake labels; they are not a current count of missing propositions.
Later full-scope reviews and audit-only source comparisons live in the bounded
`decisions/clean_gap_review_*.json` artifacts. An audit pointer does not add a
source-case payload. Quote overlap alone never certifies complete review.

Latest integrated packet: CW/CX/DA/DC/DF retains34 source cases, including two
formal contracts. Ten Pass304 MC/form/clause assignments use a reproducible,
selective four-column lexicon projection; no event data was reopened. Nine bath
readings stay in two local bundles and four organ-label compositions preserve
their rival readings. CV adds one exact lexical equivalence. CY/DB/DF add eight
scoped reason dossiers. GDT685 executed context joins and renderer repairs, but
inherited roles and fixed verdict/rank fields are not independent meaning tests.
The original source bytes remain intact; the current route and DF dossier qualify
the old strong wording. DD separates actual source transitions from renamed or
still-unexecuted tests. No new mechanism is inferred from a local clause count.
The source-polarity and identity audits are bounded, not global error-free claims.

`SEMANTIC_IDEAS_MANIFEST.json` records exact counts and bound inputs. Rebuild after
material source review with `python -m tools.semantic_ideas --build`; check with
`python -m tools.semantic_ideas --check`. A material legacy-ledger update first
requires one registry metadata refresh and broad inventory rebuild. Source bytes
remain unchanged. `VALIDATION.json` and the independent decision audits record
source preservation, current bindings and repository checks, not semantic truth.
