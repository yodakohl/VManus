# Concrete historical semantic hypotheses

This is the working view of source-attested historical propositions, not a report
of decipherment. Source pointers, empty headings, methods without a proposition,
result-only rows and unfinished extraction work are excluded from the idea list.
They remain in the source archive. No hypothesis becomes executable by inclusion.
New IDEA proposals live in the general registry and retain their review status;
they do not automatically add historical SEM cards or confirmed meanings.

## Current public snapshot

Current continuation remains in progress: [session record](decisions/semantic_10h_session.md).

Earlier completed ten-hour comparison and remaining coverage limits: [completion report](decisions/semantic_10h_completion.md).
Earlier four-hour curation delta: [scoped results](decisions/semantic_4h_completion.md).

| Unit | Count |
|---|---:|
| Active semantic hypothesis variants | 3,868 |
| Separately typed formal-role cards | 266 |
| Reviewed source cases, including the correction archive | 4,656 |
| Archived source-extraction errors | 45 |
| Exact normalized assertion repetitions grouped | 477 |
| Reviewed equivalence groups / display reduction | 85 / 103 |
| Public semantic display entries | 3,766 |

These are different units, not a deduplicated total of independent theories.
A local ignored supplement contributes95 semantic cards and one formal card;
the ordinary local default therefore displays3,861 semantic entries. A fresh
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
Explicit equivalence decisions add85 groups without deleting any original ID.
The identity log also retains 16 related-but-distinct links,33 rival links and
four specializations. Conflicting nonidentity blocks transitive merging; changed
claim or case bindings require a new review. Shared spelling, shortened wording
or a matching source title alone proves neither identity nor nonidentity.

Before selecting another identity comparison, consult `IDENTITY_REVIEW_INPUTS.json`
and the current operative identity log. The manifest records the required hashed review
inputs, including earlier proposal and peer formats missed by the narrower DO
selection list. It is a bounded coverage receipt, not an automatic pair verdict.
Update it when new identity reviews are added; distinguish an old recommendation
from a committed relation. The three DO selections did not repeat a reviewed pair.

Use `./vmanus-work identity-inputs --declared REVIEW.json --field FIELD` on the
explicit path/hash list actually used. The read-only check compares required
membership and both recorded hashes with current bytes; extra files cannot
replace omitted mandatory reviews. Diagnostics show at most20 entries per field,
with exact totals. A PASS proves input coverage, not reading or proposition
novelty. A later enlarged manifest is a new preparation requirement, not proof
that an earlier reviewer omitted files which did not yet exist.

One representative appears per reviewed equivalent group. Its status and normal
source/case counts belong to that representative; `group_scope_cases` counts all
member cases. Open `--field equivalents` or `--field relations` for the others.
No failure, success or execution permission propagates across an identity link.

The append-only correction log currently retains45 archived source-error cards and220 scope-restatement
decisions. Every original claim, case and quote remains retrievable,
including via `--show ID` for archived cards. Numeric columns, alias-column
misparses, unlicensed constituent exports and metadata are extraction errors;
actual proposed-and-rejected meanings remain historical hypotheses. Formal tags
are separately typed and excluded from the semantic default. Unconfirmed does
not mean rejected, and an old source PASS does not confirm a meaning.

## Failure memory and conditional priorities

124 scoped question dossiers distinguish empirical failure, invalid test,
insufficient capacity, missing meaning binding, proposal-only status and historical
model revision. They appear before inherited experiment context under assessments.
They state the actual compared subclaim, primary evidence, scope and changed-input
requirements. The current124 dossiers directly target148 semantic cards. The nine
priorities directly target27, with23 shared targets;3,716 semantic cards have no
direct target binding in these two lists. This is a coverage limit, not an
automatic scientific verdict on those cards (see decisions/kq_assessment_coverage.json; earlier snapshots remain preserved). An editorial wording preference is not an empirical falsifier.
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

GW recovers V26's full local-operation/major-step/open-state hierarchy as one
historical construction hypothesis. GY resolves the V69 counting hold: its concrete
exemplar implementation adds no separate semantic mechanism beyond the existing
complete models. Its source receipt retains the implementation details without
asserting full equivalence or adding a duplicate card. GW's two initial reviews
concern actual unresolved source blocks, despite their LEGACY_COMPONENT prefix;
they are distinct from the3,788 extracted component assertions. GX's apparent
endpoint errors were a newline-counting convention; three exact selected spans
include a final blank line. No mass correction or semantic regrading follows.
A073/A004 mappings remain available but uninspected, not missing data.

Before adding a fuller model card, check whether an existing short card already
names that uniquely defined historical source model. Compare its complete case
and defining sources across intake paths; enrich the existing ID when appropriate.
A short description is not automatically a different proposition. Conversely,
a broad card quoting an unrelated claim does not automatically cover that claim.
FD records a real selection error, not two newly discovered semantic mechanisms.
An expected pattern used to argue for an existing named model does not by itself
constitute another functional hypothesis. FT preserves its recurrence explanation
under the model ID because the source specifies no additional temporal contract.

Four append-only type alignments preserve the original claims and IDs. Pure
ordering/reset over predefined roles is formal, including the corrected DE335
case. Supplying or interrupting interpreted content through context is functional
(GDT416 ellipsis and the local Pass347 material thread). GDT413's division of
core readings and local designations is a semantic model. Same-source DY types
were aligned before identity; the same-type grouping check remains in force.
Classification changes scientific support neither upward nor downward.
Before a new type audit, follow the current case’s source review and its bound
peer as well as dedicated type-audit files. EG’s Pass338 selection repeated an
explicit DE peer judgment; that is a repeated check, not first-time coverage.

Use `./vmanus-work source-reviews --review REVIEW.json --source-id ID` with an
explicit public decisions file, optionally adding `--path PATH --line N
--line-end M`. It returns up to eight prior-review receipts (maximum twenty),
separating exact IDs, contained spans and partial overlaps. Reading, pending
comparison and unknown statuses remain distinct. It opens no source text and
never establishes proposition coverage, identity, permission to skip work or
semantic support. Supplied-hash agreement is metadata comparison, not fresh
primary-source validation. The thirteen real DE receipts and nine regression
cases are recorded in `decisions/semantic_source_review_validation_dh.json`.
The source-polarity and identity audits are bounded, not global error-free claims.

`SEMANTIC_IDEAS_MANIFEST.json` records exact counts and bound inputs. Rebuild after
material source review with `python -m tools.semantic_ideas --build`; check with
`python -m tools.semantic_ideas --check`. A material legacy-ledger update first
requires one registry metadata refresh and broad inventory rebuild. Source bytes
remain unchanged. `VALIDATION.json` and the independent decision audits record
source preservation, current bindings and repository checks, not semantic truth.
