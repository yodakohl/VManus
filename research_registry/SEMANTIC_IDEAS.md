# Concrete historical semantic hypotheses

The default list contains source-attested propositions. Source pointers, empty
headings, experiment methods, result rows without a proposition and pending
extraction work are excluded. Their original records remain in the source archive.
This is curation of historical hypotheses, not decipherment progress.

The public snapshot contains **3,604 concrete semantic hypothesis variants** and
**251 separate formal-role cards**. Active cards and the correction archive retain all **4,377 reviewed source cases**;
**475 repetitions of identical normalized assertions** are grouped for display.
All **5,370 proposal fragments**, **3,788 component excerpts** and **82 IP entries**
have explicit dispositions. This is not a count of independently distinct theories.
The local V81 supplement adds **96 concrete cards** (76 lexical, 19 content models, one formal role).

```bash
./vmanus-work priorities "qokaldy"
./vmanus-work priorities --offset 8
./vmanus-work priorities --show SEM:0018dcd7222eec8bfc97 --field evidence
./vmanus-work priorities --show SEM:0018dcd7222eec8bfc97 --field cases
./vmanus-work priorities --include-formal "closure"
./vmanus-work priorities --sources "qokaldy"
./vmanus-work priorities --groups
```

The detail example opens the AROL hypothesis; use other IDs returned by search.
Search returns eight
cards by default and at most twenty. The SQLite full-text index ranks direct claim
matches ahead of incidental evidence matches; ranking is navigation, not scientific
priority. Evidence and source-specific cases have bounded pages. No full registry
or history needs to enter model context, including at ten thousand ideas.

Each card states a hypothesis and binds it to exact original source lines and file
hashes. Different meanings for the same form remain separate. Identical normalized
assertion wording has one display card with separate source cases; whitespace and
backtick typography alone are normalized. Domain differences, alternatives and
failures are retained. This does not establish semantic equivalence between
paraphrases or merge whole experiments. Older assessed comparisons remain under
`--groups`; registry `ideas duplicates` and `ideas reconsider` retain their gates.

Formal-role assignments have a separate type and are excluded by default. They are
not English or German translations. Rejected historical claims remain retrievable
with their source rejection when recorded; unconfirmed is not the same as rejected.
Original limitations and competing interpretations are visible in evidence and cases.
For source-experiment verdicts and reopening conditions, use `--field assessments`.
These remain experiment-level context, not automatic verdicts on each component.
Alternatively follow the linked registry/experiment ID with `ideas show`, `ideas reconsider` and `lookup`.
No card becomes executable from this curation (`ready` is always false).

`SEMANTIC_IDEAS_MANIFEST.json` gives exact public card counts, source-fragment review
coverage and input hashes. An unreviewed source is counted as remaining review work,
never inserted as a placeholder idea. Coverage of the retained extraction universe
is distinct from recovery of unavailable or unextracted historical prose.

The local, ignored V81 review is added at query time with `local_only: true` and
separate IDs. Its exact source quotes and current file hashes must validate. Those
original untracked files and their local review are not published or silently folded
into public counts. A fresh clone therefore has the complete public view only.

Rebuild with `python -m tools.semantic_ideas --build` after a material source-review
update; check with `python -m tools.semantic_ideas --check`. Rebuilding binds the
reviewed statements, not new scientific conclusions. Preserve previous decisions
and source cases when recording corrections; never erase a failure to reopen a route.

## Source correction pass

An append-only correction log, `semantic_claim_corrections.jsonl`, currently
archives 47 source-extraction errors and restates177 source assertions
with explicit scope and appropriate lexical, functional, model or formal types. Numeric table ratios, denied constituent inferences
and dispatch metadata had incorrectly entered the hypothesis list. Every original
card, source case and exact quote remains in `semantic_ideas_excluded.jsonl` or
in the restated card. `--show ID` retrieves archived cards as well. These are
curation withdrawals, not scientific refutations. Actual proposed-and-rejected
hypotheses remain active historical records.

Correction revisions must name their predecessor and bind the original claim,
cases and evidence. Changed source scope requires explicit review; a rebuild
cannot silently renew an old decision. Independent semantic-equivalence reviews now support 39 display groups,
reducing 48 paraphrase variants while keeping every original card accessible. The source-polarity
audit is bounded and does not establish error-free global extraction.

## Reviewed identity and scoped failure memory

The default public view currently has **3,556 semantic display entries** from
3,604 active semantic variants. `semantic_identity_decisions.jsonl` records39
approved equivalence groups, four related-but-distinct links,28 explicit rival
links and two specializations. Whole-card V51/V60 continuity is backed by shared
source-deck IDs, not merely matching names or occurrence counts. These are
source-scoped propositions; shared subject words alone never establish identity.
Independent peer reviews cover each accepted group, including the I and N expansions.
Conflicting nonidentity links block transitive merging; changed source scope or
assertion wording invalidates an old judgment. Local cards remain separate.

```bash
./vmanus-work priorities --show SEM:31fd25d0bdce9a8d12ed --field equivalents
./vmanus-work priorities --show SEM:31fd25d0bdce9a8d12ed --field relations
./vmanus-work priorities --show SEM:08a05de29068958d3f58 --field assessments
```

The display shows one original representative and the number of equivalent
variants. Its status and ordinary source/case counts belong to that representative;
`group_scope_cases` counts all member cases. Open each equivalent ID for its own
case history. No rejection, success or reopening permission crosses an identity
link. Search covers every member wording. Cached pages do not deserialize the
complete card snapshot, including the10k-card regression.

Twenty-two reviewed question dossiers in `semantic_failure_decisions.jsonl` distinguish
empirical failure, invalid test, insufficient capacity, missing meaning binding
proposal-only status and historical model revisions. They appear before inherited experiment context under
`--field assessments`. They name the actual tested subclaim, primary evidence,
limits and prospective changed-input conditions. These reviewer conditions are
not original preregistered gates or approval to rerun. A narrower failed
antecedent binding never automatically rejects a broader possessive hypothesis.
Only the latest linked revision acts; all original decisions remain in the log.

## Recovery and conditional priorities

The J/M/R/V/AB/AF/AG/AL/AM/AN/BB/BD/BE source-block reviews inspect809 distinct blocks. Q/U/AA/AC
revisit the earlier scope questions; AO resolves40 AL scope questions. These revisits
are not extra source blocks. Recovery
now includes complete historical book models, concrete rendering hypotheses and
local competing readings. A local f37v dryness-degree interpretation is marked
as an instance of the terminal-degree default, not an independent new mechanism.
Presence of a narrower proposition inside a broad card's quote is source-text
preservation; it need not make that proposition independently addressable for
failure or identity decisions. AE makes this distinction explicit for GDT214.
The source archive contains9,917 unresolved extraction blocks plus5,561 pointer
rows; those intake labels are immutable source metadata, not a current count of
missing ideas. Current recovery dispositions reside in the bounded review batches.

The type audit has now primary-checked all396 originally navigated formal cards:
AQ/AR/AS/AT/AU cover the remaining336 cases. Root and AV/AW resolve overlapping
scope and counterexample judgments before integration. The AQ–AW integration restored
98 historical semantic variants, removed seven erroneous exports, and preserved
one actual failed binding rule with its four counterexample instances. A previous
AQABAC/BACA correction remains separate. Types do not imply scientific support.

The four counterbindings reject a blanket side-selection rule relative to the
existing interpreted model trace. They are not four word translations and do not
supply independently annotated manuscript syntax. AW records that comparison
limit and changed-input conditions in its own scoped dossier. Pure component
parses remain formal even when an adjacent sentence suggests a meaning; these
nearby propositions receive separate coverage checks before any recovery.

AX/AY/AZ/BA check70 nearby-meaning hints from the type reviews. They retain
59 additional source cases:54 semantic variants, one formal universal-rule rival
and four exact existing assertions. Predicted unattested cells, local compound
instances and whole general rules remain explicitly distinguished; these counts
are not independently new theories. BC records three historical model revisions:
wide-vessel OKEEOL, all-doubles nesting and the coarse CHEEKY preparation gloss.
Their different source reasons and prospective changed-input requirements remain
separate from an independently demonstrated meaning failure.

BB/BD/BE inspect260 further source blocks. BH/BI/BJ/BK resolve the scope
questions and peer corrections from those cohorts; revisits are not counted as
new blocks. Together with the targeted BG source review, they preserve98 more
source cases, including two exact existing assertions. The newly addressable
full models and local variants are not98 new independent mechanisms. Six short
Pass147 defaults and QOCKHEY keep undecided identity to longer wordings; omitted
verbs alone do not prove a different meaning.

BG corrects an unsupported global Y=Station export while preserving the E2863
local station instance and AIIN fill/medium separately from its patient. BL checks
18 more polarity cases: two unlicensed assignment exports are archived, five
real historical rejections remain with explicit source status, and eleven
qualified proposals are retained. A no-proof statement alone is not a failure.
Status strings can contain substantive hypotheses; peer-discovered cases receive
full source comparisons rather than being dismissed by their formatting.

Recovered GDT180 retains its later GDT202 semantic withdrawal. AD separately
records the failed GDT235 exact-residual coarse-object lookup and the still
unbound local BACA class candidate. BACA missed the strict prefix-selection rule;
its exposed sensitivity is not a direct semantic test by the strict residual
instrument. Re-listing any historical claim never reinstates a decoder.

```bash
./vmanus-work priorities --shortlist
./vmanus-work priorities --shortlist "okal"
```

The separate shortlist contains seven conditional question priorities within the
thirteen reviewed dossiers. It is not a global ranking of all ideas. No scientific
test in that subset is currently ready: each entry states the missing observation,
what each outcome would change and a bounded budget after qualifying evidence
exists. Changed dossier contents, source evidence or target propositions invalidate
the affected priority. Ranking never establishes semantic support. The immediate
work remains recovery and source-scope curation; completed I peer review and
scoped failure integration are no longer new tasks merely because K listed them.

Local source corrections use an ignored append-only overlay. One local B3
completion rendering is now formal, leaving95 local semantic cards. Original
local hypotheses and correction histories remain retrievable; no local source
file or local source quote is included in the public correction packet.

BM/BN review160 further short spans and BO four selected longer spans; BP/BS
revisit long paragraphs already partially quoted. BQ/BR resolve the parent scope
questions. Their109 new source cases include29 exact whole values and marked
local relations, not109 independent mechanisms. Complete recipe wording keeps
all token contributions; the AIR dry-workpiece falsifier remains limited to the
same paradigm. BV restores two exact alias-table readings. BT distinguishes an
entire process ladder from one default and a cloth-specific reading from an
explicitly broadened one; five short/long comparisons remain unresolved.

BW/CA recover the complete literal-alias families from18 selected table rows;
five follow-up rows are existing-proposition audits without fabricated new cases.
The erroneous aiin→daiin column export is archived while the actual prescribed-
measure family remains. BX retains18 held/rival values; BZ separates six technical
admission stops from the actual historical sheor=Samendroge withdrawal.
BU adds two revision dossiers, with all12 source-word edits recovered in BY.
Filtern→Seihgang names two processes; it is not a tested cloth-versus-operation
contrast. None of these editorial choices independently establishes a meaning.
