# Concrete historical semantic hypotheses

The default list contains source-attested propositions. Source pointers, empty
headings, experiment methods, result rows without a proposition and pending
extraction work are excluded. Their original records remain in the source archive.
This is curation of historical hypotheses, not decipherment progress.

The public snapshot contains **2,983 concrete semantic hypothesis variants** and
**404 separate formal-role cards**. Active cards and the correction archive retain all **3,865 reviewed source cases**;
**453 repetitions of identical normalized assertions** are grouped for display.
All **5,370 proposal fragments**, **3,788 component excerpts** and **82 IP entries**
have explicit dispositions. This is not a count of independently distinct theories.
The local V81 supplement adds **96 concrete cards** (77 lexical, 19 content models).

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
archives 25 source-extraction errors and restates five local occurrence-role
summaries as formal roles. Numeric table ratios, denied constituent inferences
and dispatch metadata had incorrectly entered the hypothesis list. Every original
card, source case and exact quote remains in `semantic_ideas_excluded.jsonl` or
in the restated card. `--show ID` retrieves archived cards as well. These are
curation withdrawals, not scientific refutations. Actual proposed-and-rejected
hypotheses remain active historical records.

Correction revisions must name their predecessor and bind the original claim,
cases and evidence. Changed source scope requires explicit review; a rebuild
cannot silently renew an old decision. Independent semantic-equivalence reviews
are in progress and are not yet applied to the default view. The source-polarity
audit is bounded and does not establish error-free global extraction.
